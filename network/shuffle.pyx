cimport cython
from cython.parallel import prange, parallel
cimport numpy as np
import numpy as np

cdef extern from "shuffle.h":
    int shuffle_edges_undirected(int nnz, int* indices, int n, int* indptr, double* data, int iterations, int seed) nogil
    int shuffle_edges_directed(int nnz, int* indices, int n, int* indptr, double* data, int iterations, int seed) nogil

cdef extern from "tasks.h":
    cdef cppclass tasker:
        void add(int nnz, int* indices, int n, int* indptr, double* data, int iterations, int seed) nogil
        int exectue(int i, int(*func)(int, int*, int, int*, double*, int, int)) nogil
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

def shuffle_multiple(network, int n, bint directed, int max_iterations, seed):
    networks = [network.copy() for _ in range(n)]

    cdef int[::1] indices
    cdef int[::1] indptr
    cdef double[::1] data
    cdef tasker container
    cdef int i

    for i in range(n):
        indices = networks[i].indices
        indptr = networks[i].indptr
        data = networks[i].data
        container.add(indices.shape[0], &indices[0], indptr.shape[0], &indptr[0], &data[0], max_iterations, seed[i])
                      
    with nogil, parallel():
        for i in prange(n):
            if directed:
                container.exectue(i, shuffle_edges_directed)
            else:
                container.exectue(i, shuffle_edges_undirected)

    return networks
