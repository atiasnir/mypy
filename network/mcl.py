import numpy as np
import scipy.sparse as sparse
import scipy.sparse.sparsetools as spt

def _csr_scale_columns(m, scale):
    spt.csr_scale_columns(m.shape[0], m.shape[1], m.indptr, m.indices, m.data, scale)

def _csr_normalize_columns(m):
    factor = m.sum(0)
    nnzeros = np.where(factor > 0)
    factor[nnzeros] = 1.0 / factor[nnzeros]
    factor = np.array(factor)[0]
    spt.csr_scale_columns(m.shape[0], m.shape[1], m.indptr, m.indices, m.data, factor)

    return m

def prepare(m, add_self_loops=True):
    if add_self_loops:
        entries = m.max(1).todense()
        entries[entries == 0] = 1.0
        d = sparse.dia_matrix((np.asarray(entries.T.astype(np.double)), [0]), m.shape) # self edges
    else:
        d = sparse.csr_matrix(m.shape)

    return _csr_normalize_columns(m + d)

def interpret(M):
    clusters = np.asarray(np.where(M.sum(1) > 0)[0]).squeeze(0)
    return [M.indices[M.indptr[c]:M.indptr[c+1]] for c in clusters]

def mcl(m, expansion=2.0, inflation=2.0, threshold=1e-6, add_self_loops=True, cap=0.001, max_iterations=-1, should_interpret=True):
    M = prepare(m, add_self_loops=add_self_loops)

    # ugly, but will loop (almost) indefinitely when 
    # max_iterations is negative
    while max_iterations != 0:
        Mp = (M**expansion)
        #if np.all(abs(Mp - M).data < threshold).all():
        #    break
        Mp.data **= inflation
        if cap is not None:
            Mp.data[Mp.data < cap] = 0
            Mp.eliminate_zeros()
        _csr_normalize_columns(Mp)
        if np.all(abs(Mp - M).data < threshold).all():
            break
        M = Mp
        max_iterations -= 1

    if should_interpret:
        return interpret(M)

    return M

def main():
    mcl_demo = np.array([
        [0.200, 0.250, 0,     0,     0,     0.333, 0.250, 0,     0,     0.250, 0,     0],
        [0.200, 0.250, 0.250, 0,     0.200, 0,     0,     0,     0,     0,     0,     0],
        [0,     0.250, 0.250, 0.200, 0.200, 0,     0,     0,     0,     0,     0,     0],
        [0,     0,     0.250, 0.200, 0,     0,     0,     0.200, 0.200, 0,     0.200, 0],
        [0,     0.250, 0.250, 0,     0.200, 0,     0.250, 0.200, 0,     0,     0,     0],
        [0.200, 0,     0,     0,     0,     0.333, 0,     0,     0,     0.250, 0,     0],
        [0.200, 0,     0,     0,     0.200, 0,     0.250, 0,     0,     0.250, 0,     0],
        [0,     0,     0,     0.200, 0.200, 0,     0,     0.200, 0.200, 0,     0.200, 0],
        [0,     0,     0,     0.200, 0,     0,     0,     0.200, 0.200, 0,     0.200, 0.333],
        [0.200, 0,     0,     0,     0,     0.333, 0.250, 0,     0,     0.250, 0,     0],
        [0,     0,     0,     0.200, 0,     0,     0,     0.200, 0.200, 0,     0.200, 0.333],
        [0,     0,     0,     0,     0,     0,     0,     0,     0.200, 0,     0.200, 0.333]])

    print mcl(sparse.csr_matrix(mcl_demo))

if __name__ == '__main__':
    main()
