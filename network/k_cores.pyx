cimport cython 
cimport numpy as np 
import numpy as np 

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef void _bin_sort(long[::1] bin, 
                    int[::1] deg, 
                    int[::1] pos, 
                    int[::1] vert) nogil:
    cdef int v

    for v in range(deg.shape[0]):
        pos[v] = bin[deg[v]]
        vert[pos[v]] = v
        bin[deg[v]] += 1

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cdef void _cores(int[::1] indptr, 
                 int[::1] indices,
                 long[::1] bin,
                 int[::1] deg,
                 int[::1] pos,
                 int[::1] vert) nogil:
    cdef int d, v, j, u, du, pu, w, dw, pw

    # restore bin
    for d in range(bin.shape[0]-1, 0, -1):
        bin[d] = bin[d-1]
    bin[0] = 0

    # cores
    for i in range(deg.shape[0]):
        v = vert[i]
        for j in range(indptr[v], indptr[v+1]):
            u = indices[j]
            if deg[u] > deg[v]:
                du = deg[u]
                pu = pos[u]
                pw = bin[du]
                w = vert[pw]
                if w != u:
                    pos[u] = pw
                    vert[pu] = w
                    pos[w] = pu
                    vert[pw] = u
                bin[du] += 1
                deg[u] -= 1

def k_cores(g):
    """ Find the k-core number of all vertices 

    Based on the paper:
    Vladimir Batagelj, Matjaz Zaversnik: An O(m) Algorithm for Cores Decomposition of Networks. 

    """
    n = g.shape[0]

    deg = np.diff(g.indptr)
    md = np.max(deg)
    bin = np.cumsum(np.bincount(deg))
    
    pos = np.empty(n, dtype=np.int32)
    vert = np.empty(n, dtype=np.int32)

    _bin_sort(bin, deg, pos, vert)
    _cores(g.indptr, g.indices, bin, deg, pos, vert)

    return deg
