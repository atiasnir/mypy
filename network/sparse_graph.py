import numpy as np
import pandas as pd

import numpy.linalg as la
from scipy.sparse import csr_matrix, issparse, dia_matrix

from ..metrics import jaccard_distance
from .random import shuffle

from .mcl import mcl
from .propagate import normalize, propagate
from .topological_sort import topological_sort

class SparseGraph(object):
    """ 
    A helper class that holds an adjacency matrix in sparse matrix format.
    Node labels are also tracked (to some extent). 
    """

    def __init__(self, spmat, names=None):
        """ Initialize the matrix 

        Parameters:
        -----------
        spmat: csr_matrix containing the adjacency matrix
        names: an optional numpy.array or pandas.Series containing the labels
               for the nodes. If omitted nodes are labeled with integers.
        """
        if not isinstance(spmat, csr_matrix) or spmat.shape[0] != spmat.shape[1]:
            raise ValueError("Invalid sparse matrix for initialization")

        if names is None:
            names = np.arange(spmat.shape[0])

        if isinstance(names, pd.Series):
            self.names = names
        else:
            self.names = pd.Series(np.arange(names.shape[0],dtype=np.int), names)

        self.data = spmat

    def normalize(self):
        """ Normalization for propagation """
        data = 1.0 / np.sqrt(self.data.sum(1))
        d = dia_matrix((data.T,[0]), (len(data),len(data)))
        return SparseGraph(d * self.data * d, self.names)

    def propagate(self, y, alpha=0.6, eps=1e-5, max_iter=1000):
        # TODO: Create nicer interface for y of type pd.Series 
        #       (align to network and return value as Series with index)
        f = np.copy(y)
        y = (1-alpha)*y
        g = alpha * self.data
        for i in range(max_iter):
            fold, f = f, g*f + y
            if la.norm(f-fold) < eps:
                break
        return f 
    smooth = propagate # alias
    
    def mcl(self, **kwargs):
        """ A straightforward implementation for Markov Cluster.

        Parameters: 
        -----------
        see mcl module

        Examples:
        ---------
        >>> g = SparseGraph.from_indices(['a', 'a', 'b', 'b', 'b', 'c', 'c', 'd', 'd', 'f', 'f', 'g'], ['b', 'd', 'd', 'c', 'e', 'd', 'e', 'e', 'f', 'g', 'h', 'h'])
        >>> [np.sort(c) for c in g.mcl()]
        [array(['a', 'b', 'c', 'd', 'e'], dtype=object), array(['f', 'g', 'h'], dtype=object)]
        >>> [np.sort(c) for c in g.mcl(inflation=1.2)]
        [array(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'], dtype=object)]
        """
       
        clusters = mcl(self.data, **kwargs)
        return [self.names.index[c].values for c in clusters]

    def edges(self, symmetric=True):
        if symmetric:
            return (np.count_nonzero(self.data.diagonal()) + self.data.nnz) / 2
        return self.data.nnz

    def abs(self):
        return abs(self.data)

    def degrees(self):
        return (self != 0).sum(1)

    def degree_distribution(self):
        b = np.bincount(self.degrees())
        indices = np.where(b)[0]
        return pd.Series(data=b[indices], index=indices)

    def merge(self, other):
        """ Combine two networks (based on their node labels). Weight for
        duplicate edges are taken from other.

        Parameters:
        -----------
        other: the network to merge

        Returns the merged network

        Examples:
        ---------
        >>> row = ['a', 'b', 'c']
        >>> col = ['b', 'c', 'd']
        >>> g = SparseGraph.from_indices(row, col)
        >>> g.to_frame()
           a  b  c  d
        a  0  1  0  0
        b  1  0  1  0
        c  0  1  0  1
        d  0  0  1  0
        >>> h = SparseGraph.from_indices(['a', 'a', 'e'], ['b', 'e', 'd']) * 2
        >>> h.to_frame()
           a  b  d  e
        a  0  2  0  2
        b  2  0  0  0
        d  0  0  0  2
        e  2  0  2  0
        >>> g.merge(h).to_frame()
           a  b  c  d  e
        a  0  2  0  0  2
        b  2  0  1  0  0
        c  0  1  0  1  0
        d  0  0  1  0  2
        e  2  0  0  2  0
        """
        df = self.to_frame(asmatrix=False, symmetric=False)
        df = df.append(other.to_frame(asmatrix=False, symmetric=False), ignore_index=True)
        df.drop_duplicates(subset=('i', 'j'), take_last=True, inplace=True)
        return self.from_indices(df.i, df.j, df.data, symmetric=False)
        

    def copy(self):
        return SparseGraph(self.data.copy(), self.names.copy())

    def shuffle(self, directed=False, max_iterations=None, seed=0):
        return shuffle(self.data, directed=directed,
                       max_iterations=max_iterations, seed=seed)

    def topological_sort(self):
        """ Returns an ordered list of the nodes of a DAG so that 
            all edges are from nodes with lower indices to nodes with
            higher indices

        Example:
        --------

        >>> g = SparseGraph.from_indices([7, 7, 5, 3, 3, 11, 11, 11, 8], [11, 8, 11, 8, 10, 2, 9, 10, 9], symmetric=False)
        >>> g.topological_sort()
        array([ 7,  5, 11,  3, 10,  8,  9,  2])
        """
        return self.names.index.values[topological_sort(self.data)]

    def pdist(self, metric='correlation', *args, **kwargs):
#        pd.DataFrame(1.0-pairwise_distances(holstege, metric='correlation', n_jobs=-1), 
#                                      index=holstege.index, columns=holstege.index)
        if metric=='jaccard':
            distances = jaccard_distance(self.data, *args, **kwargs)
        else:
            distances = distance.squareform(distance.pdist(self.data.todense(), metric, *args, **kwargs))
        return pd.DataFrame(distances, self.names.index, self.names.index)

    def to_frame(self, asmatrix=True, symmetric=True):
        """ Convert the current network to pandas.DataFrame 

        Parameters:
        -----------
        asmatrix: determines whether the dataframe represents the adjacency 
                  matrix (default) or the list of edges.

        symmetric: when asmatrix==False, eliminate duplicate entries 
                   for the same edge (from, to) and (to, from) by reporting 
                   only edges where `from` is less than `to`

        Examples:
        ---------
        >>> row = ['a', 'b', 'c']
        >>> col = ['b', 'c', 'd']
        >>> g = SparseGraph.from_indices(row, col)
        >>> g.data.todense()
        matrix([[0, 1, 0, 0],
                [1, 0, 1, 0],
                [0, 1, 0, 1],
                [0, 0, 1, 0]])
        
        >>> g.to_frame(asmatrix=False)
           i  j  data
        0  a  b     1
        1  b  c     1
        2  c  d     1

        >>> g.to_frame()
           a  b  c  d
        a  0  1  0  0
        b  1  0  1  0
        c  0  1  0  1
        d  0  0  1  0
        """

        if not asmatrix:
            inv = self.names.index.to_series()

            if symmetric:
                i, j = self.data.nonzero()
                mask = i <= j
                i = inv.iloc[i[mask]].values
                j = inv.iloc[j[mask]].values
                data = self.data.data[mask]
            else:
                i, j = [inv.iloc[x].values for x in self.data.nonzero()]
                data = self.data.data

            return pd.DataFrame({'i': i, 'j': j, 'data': data}, columns=('i','j','data'))

        return pd.DataFrame(data=np.asarray(self.data.todense()), index=self.names.index, columns=self.names.index)

    @staticmethod 
    def from_indices(i, j, data=None, symmetric=True):
        """ Create a sparse network from a list of edges. 

        i: (array of) names of source nodes
        j: (array of) names of destination nodes
        data: edge weights (optional, default:1)
        symmetric: specify whether edges are directional or not (which is the default)

        >>> row = ['a', 'b', 'c']
        >>> col = ['b', 'c', 'd']
        >>> g = SparseGraph.from_indices(row, col)
        >>> g.data.todense()
        matrix([[0, 1, 0, 0],
                [1, 0, 1, 0],
                [0, 1, 0, 1],
                [0, 0, 1, 0]])
        >>> g = SparseGraph.from_indices(row, col, 1+np.arange(len(row)))
        >>> g.data.todense()
        matrix([[0, 1, 0, 0],
                [1, 0, 2, 0],
                [0, 2, 0, 3],
                [0, 0, 3, 0]])
        >>> import pandas as pd
        >>> g = SparseGraph.from_indices(pd.Series([10, 11, 12]).astype(str), pd.Series([11, 12, 13]).astype(str))
        >>> g.data.todense()
        matrix([[0, 1, 0, 0],
                [1, 0, 1, 0],
                [0, 1, 0, 1],
                [0, 0, 1, 0]])
        """
        allnames = np.union1d(i, j)
        names = pd.Series(np.arange(allnames.shape[0],dtype=np.int), allnames)

        if data is None:
            data = np.ones(len(i), dtype=np.int)

        smatrix = csr_matrix((data, (names.loc[i], names.loc[j])), shape=(allnames.shape[0], allnames.shape[0]))
        data = smatrix if not symmetric else smatrix + smatrix.T

        return SparseGraph(data, names)

    @classmethod
    def _add_comparison_method(cls):

        def create_comp_method(op, eliminate_zeros=False):
            def comp_method(self, other):
                if isinstance(other, SparseGraph):
                    result = op(self.data, other.data)
                else:
                    result = op(self.data, other)

                if issparse(result):
                    if eliminate_zeros:
                        result.eliminate_zeros()

                    if result.shape == self.data.shape:
                        return SparseGraph(result, self.names)

                return result

            comp_method.__name__ =  op.__name__
            if op.__doc__ is not None:
                comp_method.__doc__ = op.__doc__.replace('>>>', '>>') # HACK: avoid doc-testing wrapped methods
            return comp_method

        cls.__lt__ = create_comp_method(csr_matrix.__lt__)
        cls.__ge__ = create_comp_method(csr_matrix.__ge__)
        cls.__gt__ = create_comp_method(csr_matrix.__gt__)
        cls.__ne__ = create_comp_method(csr_matrix.__ne__)
        cls.__eq__ = create_comp_method(csr_matrix.__eq__)
        cls.__le__ = create_comp_method(csr_matrix.__le__)

        cls.__add__ = create_comp_method(csr_matrix.__add__, True)
        cls.__radd__ = create_comp_method(csr_matrix.__radd__, True)
        cls.__sub__ = create_comp_method(csr_matrix.__sub__, True)
        cls.__rsub__ = create_comp_method(csr_matrix.__rsub__, True)
        cls.__mul__ = create_comp_method(csr_matrix.__mul__, True)
        cls.__rmul__ = create_comp_method(csr_matrix.__rmul__, True)
        cls.multiply = create_comp_method(csr_matrix.multiply, True)
        cls.maximum = create_comp_method(csr_matrix.maximum, True)
        cls.minimum = create_comp_method(csr_matrix.minimum, True)

    @classmethod
    def _add_sparse_ops(cls):

        def create_noarg_method(method):
            def wrapper(self):
                result = method(self.data)
                
                if (result is not None) and \
                   hasattr(result, 'shape') and \
                   (result.shape == self.data.shape):
                    return SparseGraph(result, self.names.copy())

                return result

            wrapper.__name__ = method.__name__
            if method.__doc__ is not None:
                wrapper.__doc__ = method.__doc__.replace('>>>', '>>') # HACK: avoid doc-testing wrapped methods
            return wrapper

        def create_axis_method(method):
            def wrapper(self, axis=None):
                result = method(self.data, axis)

                if not np.isscalar(result) and np.any(result.shape) == 1:
                    if issparse(result):
                        return pd.Series(np.squeeze(np.asarray(result.todense())), self.names.index)

                    return pd.Series(np.squeeze(np.asarray(result)), self.names.index)

                return result

            wrapper.__name__ = method.__name__
            if method.__doc__ is not None:
                wrapper.__doc__ = method.__doc__.replace('>>>', '>>') # HACK: avoid doc-testing wrapped methods
            return wrapper

        cls.__abs__ = create_noarg_method(csr_matrix.__abs__)
        cls.arcsin = create_noarg_method(csr_matrix.arcsin)
        cls.arcsinh = create_noarg_method(csr_matrix.arcsinh)
        cls.arctan = create_noarg_method(csr_matrix.arctan)
        cls.arctanh = create_noarg_method(csr_matrix.arctanh)
        cls.ceil = create_noarg_method(csr_matrix.ceil)
        cls.conj = create_noarg_method(csr_matrix.conj)
        cls.conjugate = create_noarg_method(csr_matrix.conjugate)
        cls.copy = create_noarg_method(csr_matrix.copy)

        cls.diagonal = create_noarg_method(csr_matrix.diagonal)
        cls.eliminate_zeros = create_noarg_method(csr_matrix.eliminate_zeros)
        cls.expm1 = create_noarg_method(csr_matrix.expm1)
        cls.floor = create_noarg_method(csr_matrix.floor)
        cls.getH = create_noarg_method(csr_matrix.getH)
        cls.getformat = create_noarg_method(csr_matrix.getformat)
        cls.getmaxprint = create_noarg_method(csr_matrix.getmaxprint)
        cls.log1p = create_noarg_method(csr_matrix.log1p)
        cls.nonzero = create_noarg_method(csr_matrix.nonzero)
        cls.prune = create_noarg_method(csr_matrix.prune)
        cls.rad2deg = create_noarg_method(csr_matrix.rad2deg)
        cls.rint = create_noarg_method(csr_matrix.rint)
        cls.sign = create_noarg_method(csr_matrix.sign)
        cls.sin = create_noarg_method(csr_matrix.sin)
        cls.sinh = create_noarg_method(csr_matrix.sinh)
        cls.sort_indices = create_noarg_method(csr_matrix.sort_indices)
        cls.sorted_indices = create_noarg_method(csr_matrix.sorted_indices)
        cls.sqrt = create_noarg_method(csr_matrix.sqrt)
        cls.sum_duplicates = create_noarg_method(csr_matrix.sum_duplicates)
        cls.tan = create_noarg_method(csr_matrix.tan)
        cls.tanh = create_noarg_method(csr_matrix.tanh)
        cls.trunc = create_noarg_method(csr_matrix.trunc)

        cls.sum = create_axis_method(csr_matrix.sum)
        cls.getnnz = create_axis_method(csr_matrix.getnnz)
        cls.max = create_axis_method(csr_matrix.max)
        cls.mean = create_axis_method(csr_matrix.mean)
        cls.min = create_axis_method(csr_matrix.min)

SparseGraph._add_comparison_method()
SparseGraph._add_sparse_ops()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
