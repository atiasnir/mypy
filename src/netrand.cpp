#include <algorithm>
#include <random>
#include <iostream>
#include <iomanip>

using namespace std;

void change_edge(int t, int* edge, double* data, int* begin, int* end) {
	*edge = t;
	while(edge < end-1 && *edge > edge[1]) {
		swap(edge[0], edge[1]);
		swap(data[0], data[1]);
		++edge;
	}
	while(edge > begin && *edge < edge[-1]) {
		swap(edge[0], edge[-1]);
		swap(data[0], data[-1]);
		--edge;
	}
}

void show_mat(const char* prefix, int nnz, int* indices, int n, int* indptr, double* data) {
	cout << prefix << endl;
	for(int r=0; r<n; ++r) {
		int col = indptr[r];
		cout << r << "]    ";
		for(int c=0; c<n; ++c)
			if(col < indptr[r+1] && c == indices[col]) {
				cout << setprecision(3) << setw(6) << left << data[col] << " ";
				++col;
			} else {
				cout << "0.     ";
			}
		cout << endl;
	}
	cout << "----------------" << endl;
}
	

int shuffle_edges_directed(int nnz, int* indices, int n, int* indptr, double* data, int iterations, int seed) {
	mt19937_64 						rng(seed);
	uniform_int_distribution<int> 	randnnz(0, nnz-1);
	int 							switches = 0;

	for(int counter=0; counter<iterations; ++counter) {
		int iv = randnnz(rng);
		int u = upper_bound(indptr, indptr+n, iv) - indptr - 1;
		int v = indices[iv];

		int it = randnnz(rng);
		int s = upper_bound(indptr, indptr+n, it) - indptr - 1;
		int t =  indices[it];

		if(s==t || s==u || s==v || t==u || t==v)
			continue;

		int* ubegin = indices + indptr[u];
		int* uend = indices + indptr[u+1];
		int* pos = lower_bound(ubegin, uend, t);
		if(pos < uend && *pos==t)
			// (u,t) in g
			continue;

		int* sbegin = indices+indptr[s];
		int* send = indices+indptr[s+1];
		pos = lower_bound(sbegin, send, v);
		if(pos < indices + indptr[s+1] && *pos==v)
			// (s,v) in g
			continue;

		//cout << "u=" << u << " v=" <<v << " s="<< s << " t=" <<t <<endl;
		//cout << "g[u,v]=" << data[iv] << " g[s,t]=" << data[it] << endl;
		change_edge(t, indices+iv, data+iv, ubegin, uend);
		//show_mat("1:", nnz, indices, n, indptr, data);
		change_edge(v, indices+it, data+it, sbegin, send);
		//show_mat("2:", nnz, indices, n, indptr, data);

		//indices[iv] = t;
		//indices[it] = v;
		//swap(data[iv], data[it]);

		//sort(ubegin, uend);
		//sort(sbegin, send);
		++switches;
	}

	return switches;
}

int shuffle_edges_undirected(int nnz, int* indices, int n, int* indptr, double* data, int iterations, int seed) {
	mt19937_64 						rng(seed);
	uniform_int_distribution<int> 	randnnz(0, nnz-1);
	int switches = 0;

	//show_mat("start", nnz, indices, n, indptr, data);

	for(int counter=0; counter<iterations; ++counter) {
		int iv = randnnz(rng);
		int u = upper_bound(indptr, indptr+n, iv) - indptr - 1;
		int v = indices[iv];

		int it = randnnz(rng);
		int s = upper_bound(indptr, indptr+n, it) - indptr - 1;
		int t =  indices[it];

		if(s==t || s==u || s==v || t==u || t==v)
			continue;

		int* ubegin = indices + indptr[u];
		int* uend = indices + indptr[u+1];
		int* pos = lower_bound(ubegin, uend, t);
		if(pos < uend && *pos==t)
			// (u,t) in g
			continue;

		int* sbegin = indices+indptr[s];
		int* send = indices+indptr[s+1];
		pos = lower_bound(sbegin, send, v);
		if(pos < indices + indptr[s+1] && *pos==v)
			// (s,v) in g
			continue;

		double duv = data[iv];
		double dst = data[it];

		//cout << "u=" << u << " v=" <<v << " s="<< s << " t=" <<t <<endl;
		//cout << "g[u,v]=" << duv << " g[s,t]=" << dst << endl;

		change_edge(t, indices+iv, data+iv, ubegin, uend);
		//show_mat("1:", nnz, indices, n, indptr, data);
		change_edge(v, indices+it, data+it, sbegin, send);
		//show_mat("2:", nnz, indices, n, indptr, data);
		//indices[iv] = t;
		//indices[it] = v;

		//sort(ubegin, uend);
		//sort(sbegin, send);

		int* vbegin = indices+indptr[v];
		int* vend = indices+indptr[v+1];
		//*lower_bound(vbegin, vend, u) = s;
		//sort(vbegin, vend);
		pos = lower_bound(vbegin, vend, u);
		data[pos-indices] = dst;
		change_edge(s, pos, data + (pos-indices), vbegin, vend);
		//show_mat("3:", nnz, indices, n, indptr, data);

		int* tbegin = indices+indptr[t];
		int* tend = indices+indptr[t+1];
		//*lower_bound(tbegin, tend, s) = u;
		//sort(tbegin, tend);
		pos = lower_bound(tbegin, tend, s);
		data[pos-indices] = duv;
		change_edge(u, pos, data + (pos-indices), tbegin, tend);
		//show_mat("4:", nnz, indices, n, indptr, data);

		++switches;
	}

	return switches;
}

//----------------------------------- PYTHON ---------------------------

#include <boost/python.hpp>

class py_gil_release {
public:
    inline py_gil_release() {
        _thread_state = PyEval_SaveThread();
    }

    inline ~py_gil_release() {
        PyEval_RestoreThread(_thread_state);
        _thread_state = NULL;
    }

private:
    PyThreadState* _thread_state;
};

using namespace boost;

struct pybuffer_holder {
	Py_buffer _buffer;

	pybuffer_holder() {
	}

	~pybuffer_holder() {
		PyBuffer_Release(&_buffer);
	}

	operator Py_buffer*() {
		return &_buffer;
	}

	Py_buffer* operator->() {
		return &_buffer;
	}
};

template<int N>
bool starts_with(const string& str, const char (&constant)[N]) {
	return strncmp(str.c_str(), constant, N-1) == 0;
}


int py_shuffle_edges(python::object g, bool directed, int iterations, int seed) {
	pybuffer_holder indices_buffer;
	pybuffer_holder indptr_buffer;
	pybuffer_holder data_buffer;

	python::object indices =  g.attr("indices");
	python::object indptr =  g.attr("indptr");
	python::object data =  g.attr("data");

	if(PyObject_GetBuffer(indices.ptr(), indices_buffer, PyBUF_CONTIG|PyBUF_FORMAT) != 0)
		throw runtime_error("not a buffer");

	if(PyObject_GetBuffer(indptr.ptr(), indptr_buffer, PyBUF_CONTIG|PyBUF_FORMAT) != 0)
		throw runtime_error("not a buffer");

	if(PyObject_GetBuffer(data.ptr(), data_buffer, PyBUF_CONTIG|PyBUF_FORMAT) != 0)
		throw runtime_error("not a buffer");

	if(directed) {
		return shuffle_edges_directed(indices_buffer->shape[0], (int*)indices_buffer->buf,
				indptr_buffer->shape[0], (int*)indptr_buffer->buf,
				(double*)data_buffer->buf, iterations, seed);
	} else {
		return shuffle_edges_undirected(indices_buffer->shape[0], (int*)indices_buffer->buf,
				indptr_buffer->shape[0], (int*)indptr_buffer->buf,
				(double*)data_buffer->buf, iterations, seed);
	}
}

template<class T>
std::vector<T> list_to_vector(python::object l) {
	std::vector<T> result;
	size_t n = python::len(l);
	result.reserve(n);
	
	for(size_t idx=0; idx<n; ++idx) {
		T value(python::extract<T>(l[idx]));
		result.push_back(value);
	}

	//return std::move(result);
	return result;
}

void py_sparse_to_file(python::object g, python::object file, python::object pnames, bool directed) {
	FILE* f = PyFile_AsFile(file.ptr());
	pybuffer_holder indices_buffer;
	pybuffer_holder indptr_buffer;
	pybuffer_holder data_buffer;

	python::object indices =  g.attr("indices");
	python::object indptr =  g.attr("indptr");
	python::object data =  g.attr("data");

	if(PyObject_GetBuffer(indices.ptr(), indices_buffer, PyBUF_CONTIG|PyBUF_FORMAT) != 0)
		throw runtime_error("not a buffer");

	if(PyObject_GetBuffer(indptr.ptr(), indptr_buffer, PyBUF_CONTIG|PyBUF_FORMAT) != 0)
		throw runtime_error("not a buffer");

	if(PyObject_GetBuffer(data.ptr(), data_buffer, PyBUF_CONTIG|PyBUF_FORMAT) != 0)
		throw runtime_error("not a buffer");

	vector<string> names(list_to_vector<string>(pnames));

	if(directed) {
		double* dp = (double*)data_buffer->buf;
		int* ip = (int*)indices_buffer->buf;
		int* colbegin = (int*)indptr_buffer->buf;
		int* col = colbegin;

		for(int nnz=0; nnz<data_buffer->shape[0]; ++nnz) {
			while(nnz>=col[1])
				++col;
			int u = col - colbegin;
			int v = *ip++;
			double d = *dp++;

			fprintf(f, "%s\t%s\t%f\t1\n", names[u].c_str(), names[v].c_str(), d);
		}

	} else {
		double* dp = (double*)data_buffer->buf;
		int* ip = (int*)indices_buffer->buf;
		int* colbegin = (int*)indptr_buffer->buf;
		int* col = colbegin;

		for(int nnz=0; nnz<data_buffer->shape[0]; ++nnz) {
			while(nnz>col[1])
				++col;
			int u = col - colbegin;
			int v = *ip++;
			double d = *dp++;

			if(u<v)
				fprintf(f, "%s\t%s\t%f\t0\n", names[u].c_str(), names[v].c_str(), d);
		}

	}

}

BOOST_PYTHON_MODULE(netrand) {
	def("shuffle_edges", &py_shuffle_edges);
	def("sparse_to_file", &py_sparse_to_file);
}
