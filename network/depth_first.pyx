cimport cython 
cimport numpy as np

import numpy as np

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef int _depth_first_visit(int i,
                            int order_end,
                            int[::1] indptr, 
                            int[::1] indices, 
                            long[::1] status, 
                            long[::1] order, 
                            long[::1] predecessors) nogil:
    cdef int j
    cdef int idx

    status[i] = 1

    order[order_end] = i
    order_end += 1

    for idx in range(indptr[i], indptr[i+1]):
        j = indices[idx]
    
        if status[j] == 0:
            predecessors[j] = i
            order_end = _depth_first_visit(j, order_end, indptr, indices, status, order, predecessors)

    status[i] = 2

    return order_end

def depth_first_order(csgraph, i_start, directed=True, return_predecessors=True):
    cdef int n = csgraph.shape[0]

    order = np.empty(n, dtype=np.int)
    status = np.zeros(n, dtype=np.int)
    predecessors = np.empty(n, dtype=np.int)

    predecessors[i_start] = -9999 # compliance with scipy
    _depth_first_visit(i_start, 0, csgraph.indptr, csgraph.indices, status, order, predecessors)

    if return_predecessors:
        return order, predecessors

    return order
