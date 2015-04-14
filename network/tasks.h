#ifndef TASKS_H_UBEJFEAR
#define TASKS_H_UBEJFEAR

#include <vector>

struct shuffle_task {
	int nnz_;
	int* indices_;
	int n_; 
	int* indptr_;
	double* data_; 
	int iterations_;
	int seed_;

	shuffle_task(int nnz, int* indices, int n, int* indptr, double* data, int iterations, int seed)
		: nnz_(nnz), indices_(indices), n_(n), indptr_(indptr), data_(data), iterations_(iterations), seed_(seed)
	{}
};

struct tasker {
	tasker() {
		tasks_.reserve(100);
	}

	void add(int nnz, int* indices, int n, int* indptr, double* data, int iterations, int seed) {
		tasks_.emplace_back(nnz, indices, n, indptr, data, iterations, seed);
	}

	int exectue(int i, int(*func)(int, int*, int, int*, double*, int, int)) {
		shuffle_task& params = tasks_[i];
		return func(params.nnz_, params.indices_, params.n_, params.indptr_, params.data_, params.iterations_, params.seed_);
	}
private:
	std::vector<shuffle_task> tasks_;
};

#endif /* end of include guard: TASKS_H_UBEJFEAR */

