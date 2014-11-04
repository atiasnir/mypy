import numpy as np
cimport numpy as np
cimport cython

def topological_sort(csgraph):
    cdef int N = csgraph.shape[0]
    
    node_list = np.empty(N, dtype=np.int)
    marked = np.zeros(N, dtype=np.int)
    stacked = np.zeros(N, dtype=np.int)

    _topological_sort(csgraph.indices, csgraph.indptr, node_list, marked, stacked)

    return node_list

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef void _topological_sort(int[::1] indices,
                            int[::1] indptr,
                            long[::1] node_list,
                            long[::1] marked,
                            long[::1] stacked) nogil:
    cdef int N = indices.shape[0] - 1
    cdef int i_nl_end = N-1
    cdef int i
    
    for i from 0 <= i < N:
        if marked[i]:
            continue

        i_nl_end = _topological_sort_visit_rec(i, i_nl_end, indices, indptr, node_list, marked, stacked)

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef unsigned int _topological_sort_visit_rec(
                           unsigned int head_node,
                           unsigned int i_nl_end,
                           int[::1] indices,
                           int[::1] indptr,
                           long[::1] node_list,
                           long[::1] marked,
                           long[::1] stacked) nogil:
    cdef int i

    if stacked[head_node] == 1:
        with gil:
            raise ValueError("Not a DAG")
    
    if marked[head_node] == 0:
        stacked[head_node] = 1

        for i from indptr[head_node] <= i < indptr[head_node + 1]:
            i_nl_end = _topological_sort_visit_rec(indices[i], i_nl_end, indices, indptr, node_list, marked, stacked)

        marked[head_node] = 1
        stacked[head_node] = 0
        node_list[i_nl_end] = head_node

        i_nl_end -= 1

    return i_nl_end
