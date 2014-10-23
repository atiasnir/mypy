"""
A module with utilities related to distance computation.
Specifically, attempt to take advantage of sparse data
"""

import numpy as np
import scipy.sparse as sparse
import scipy.spatial.distance as distance
from sklearn.metrics.pairwise import pairwise_distances

def jaccard_distance(X, Y=None, n_jobs=-1, **kwds):
    """ Computes the Jaccard distance between all the pairs of vectors in X.
    If X is not sparse the function defaults to sklearn.metrics.pairwise.pairwise_distances
    If Y is given distances between X and Y are computed

    The Jaccard index is defined as the intersection / union of items in the vector (that is 
    non-sparse indices, regardless of their magnitude)

    Parameters:
    -----------
    X: an array (dims: samples X features)
    Y: an optional array (dims: samples_2 X features)
    n_jobs: optionally run on multiple cores
    **kwds: additional parameters to sklearn.metrics.pairwise.pairwise_distances

    Returns a square distance matrix. All elements are in [0, 1]. 
    One may use 1-R for similarity (where R is the return value)

    Examples:
        >>> from scipy.sparse import csr_matrix
        >>> from numpy import matrix
        >>> d = matrix([[1, 1, 1, 0, 0], [0, 1, 1, 0, 1]])
        >>> s = csr_matrix(d)
        >>> jaccard_distance(s)
        matrix([[ 0. ,  0.5],
                [ 0.5,  0. ]])
        >>> jaccard_distance(s, [1, 1, 1, 0, 1])
        matrix([[ 0.25],
                [ 0.25]])
    """
    if Y is None:
        Y = X
    if sparse.issparse(X):
        if not sparse.issparse(Y):
            Y = sparse.csr_matrix(Y)
        mmx = (X!=0)
        mmy = (Y!=0)
        mx = sparse.csr_matrix((np.ones_like(mmx.data, dtype=np.double), mmx.indices, mmx.indptr), shape=mmx.shape)
        if X is Y:
            my = mx
        else:
            my = sparse.csr_matrix((np.ones_like(mmy.data, dtype=np.double), mmy.indices, mmy.indptr), shape=mmy.shape)
        m_int = mx * my.T
        m_uni = pairwise_distances(mx, my, metric='manhattan', n_jobs=n_jobs, **kwds)
        m_uni += m_int
        return 1.0 - (m_int / m_uni)
    else:
        return pairwise_distances(X, metric='jaccard', n_jobs=n_jobs, **kwds)


if __name__ == '__main__':
    import doctest

    doctest.testmod()
