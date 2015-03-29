import numpy as np

from scipy.spatial.distance import pdist, squareform
from scipy.sparse import csr_matrix

try:
    import pyximport
    pyximport.install()

    from shuffle import shuffle_edges as _shuffle_edges
except:
    import warnings
    warnings.warn('Compilation with cython failed. Randomization will not work')

def geometric(n, threshold=0.5, dim=5):
    """ Generate a random graph based on geometric model. 
    
    `n` points are sampled from a `dim`-dimensional 1-unit cube and all 
    euclidean pairwise distances between them are computed. The output graph 
    has a node corresponding to each of the points. Nodes whose
    corresponding points are closer than `threshold` are connected 
    via an edge in the output graph.

    Parameters:
    -----------
    n:         the number of node in the output graph 
    threshold: the maximum distance between connected nodes 
    dim:       the dimensionality of the cube

    Examples:
    ---------
    >>> import numpy as np 
    >>> np.random.seed(2)
    >>> geometric(5, dim=3).todense()
    matrix([[ 0.,  1.,  0.,  0.,  0.],
            [ 1.,  0.,  1.,  1.,  1.],
            [ 0.,  1.,  0.,  1.,  1.],
            [ 0.,  1.,  1.,  0.,  1.],
            [ 0.,  1.,  1.,  1.,  0.]])
    """

    data = np.random.rand(n, dim)
    distances = pdist(data)
    return csr_matrix(squareform(np.where(distances < threshold, 1, 0)))

def preferential(n, k=1):
    """ Generate a random graph based on preferential attachment model. 
    Starting from an edge (n-2) nodes are added sequentially such that 
    each added node is attached to k existing nodes. The probability
    of which node to choose is proportional their degree.

    Parameters:
    -----------
    n: the number of nodes

    Examples:
    ---------
    >>> import numpy as np 
    >>> np.random.seed(3)
    >>> preferential(7).todense()
    matrix([[ 0.,  1.,  0.,  0.,  0.,  0.,  0.],
            [ 1.,  0.,  1.,  1.,  1.,  1.,  0.],
            [ 0.,  1.,  0.,  0.,  0.,  0.,  0.],
            [ 0.,  1.,  0.,  0.,  0.,  0.,  0.],
            [ 0.,  1.,  0.,  0.,  0.,  0.,  1.],
            [ 0.,  1.,  0.,  0.,  0.,  0.,  0.],
            [ 0.,  0.,  0.,  0.,  1.,  0.,  0.]])
    """

    data = np.zeros(shape=(n,n))
    data[0,1] = 1
    data[1,0] = 1

    for i in range(2, n):
        p = data.sum(axis=0) / data.sum()
        to = np.unique(np.random.choice(i, size=k, p=p[p>0]))

        data[i, to] = 1
        data[to, i] = 1

    return csr_matrix(data)

def shuffle(network, directed=False, max_iterations=None, seed=0):
    """ A degree-preserving shuffling of the edges of the input network.
    Note that the shuffling changes the original matrix.

    Parameters
    ----------
    network:        A square matrix representing a network. Will try to convert
                    to csr_matrix if not already so.
    directed:       Specify whether to treat the network as undirected (the
                    default) or as directed. 
    max_iterations: The maximum number of iterations to perform. Defaults to 10
                    times the number of edges
    seed:           A seed for the interna random number generator

    Returns the actual number of edge shuffles that took place. 

    Examples:
        >>> from numpy import array
        >>> from scipy.sparse import csr_matrix
        >>> row = array([0,1,2])
        >>> col = array([1,2,3])
        >>> data = array([1,1,1])
        >>> g = csr_matrix((data, (row, col)), shape=(4,4))
        >>> g = g + g.T # undirected
        >>> g.todense() # 0 - 1 - 2 - 3
        matrix([[0, 1, 0, 0],
                [1, 0, 1, 0],
                [0, 1, 0, 1],
                [0, 0, 1, 0]])
        
        >>> shuffle(g, max_iterations=1)
        1
        >>> g.todense() # 0 - 2 - 1 - 3
        matrix([[0, 0, 1, 0],
                [0, 0, 1, 1],
                [1, 1, 0, 0],
                [0, 1, 0, 0]])
        
    """
    if not isinstance(network, csr_matrix):
        network = csr_matrix(network)

    if max_iterations is None:
        max_iterations = 100 * network.nnz

    return _shuffle_edges(network, directed, max_iterations, seed)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
