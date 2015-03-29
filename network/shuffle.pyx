cimport cython
cimport numpy as np
import numpy as np

cdef extern from "shuffle.h":
    int shuffle_edges_undirected(int nnz, int* indices, int n, int* indptr, double* data, int iterations, int seed) nogil
    int shuffle_edges_directed(int nnz, int* indices, int n, int* indptr, double* data, int iterations, int seed) nogil

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef int shuffle_edges_internal(int[::1] indices, int[::1] indptr, double[::1] data,
                       bint directed, int iterations, int seed) nogil:
    with nogil:
        if directed:
            return shuffle_edges_directed(indices.shape[0], &indices[0], indptr.shape[0], &indptr[0], &data[0], iterations, seed)
        else:
            return shuffle_edges_undirected(indices.shape[0], &indices[0], indptr.shape[0], &indptr[0], &data[0], iterations, seed)

def shuffle_edges(network, directed, max_iterations, seed):
    return shuffle_edges_internal(network.indices, network.indptr, network.data, directed, max_iterations, seed)
