import numpy as np 

def edge_id(a, b, sep=':'):
    """ Returns an id identifying the edge regardless of the order of interactors 

    Parameters
    ----------
    a: the first interactor (a pandas series)
    b: the second interactor

    Returns an id where the interactors are lexicographically sorted and separted 
    by 'sep'

    >>> import pandas as pd
    >>> a = pd.Series(['a', 'c', 'c'])
    >>> b = pd.Series(['b', 'b', 'd'])
    >>> edge_id(a, b)
    array(['a:b', 'b:c', 'c:d'], dtype=object)

    """
    return np.where(a<b, a + sep + b, b + sep + a)
