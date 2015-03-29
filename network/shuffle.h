#ifndef SHUFFLE_H_4PX3V27U
#define SHUFFLE_H_4PX3V27U

#include <algorithm>
#include <random>
#include <iostream>
#include <iomanip>

void change_edge(int t, int* edge, double* data, int* begin, int* end) {
	using namespace std;
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
	using namespace std;
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
	using namespace std;
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
	using namespace std;
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


#endif /* end of include guard: SHUFFLE_H_4PX3V27U */
