import numpy as np 

def _partition(a, x, first, last):
    while first != last:
        while a[first] < x:
            first += 1
            if first == last:
                return first
        last -= 1
        if first == last:
            return first
        while a[last] >= x:
            last -= 1
            if first == last:
                return first
        a[first], a[last] = a[last], a[first]
        first += 1

    return first

def partition(a, pivot, first, last):
    """ partition the array 'a' so that 'item' is in 
        its sorted place

        Parameters:
        -----------
        a: the array 
        pivot: index to the pivot
        first: first index to consider
        last: last index to consider

        Note that: first <= pivot < last

        Examples:
        ---------

        >>> a = [51, 81, 74, 12, 58, 92, 86, 25, 67, 33, 18, 41, 49, 63, 29, 37]
        >>> p = partition(a, 0, 0, len(a))
        >>> sorted(a).index(51) == p
        True
    """
    a[first], a[pivot] = a[pivot], a[first]

    pivot = _partition(a, a[first], first+1, last) - 1

    a[first], a[pivot] = a[pivot], a[first]
    return pivot

def _find_min(a, idx, stack):
    """ recursive implementation for incremental quick sort
        which returns the minimum element in a while maintaining 
        an index and stack for subsequent calls. 

        The goal is to efficiently find only the first k sorted 
        elements
        
        Parameters:
        -----------
        a: the array (will be changed by the call
        idx: the start index 
        stack: a stack for bookeeping

        returns the minimum value. It will also be placed in idx

        Examples:
        ---------
        >>> a = [51, 81, 74, 12, 58, 92, 86, 25, 67, 33, 18, 41, 49, 63, 29, 37]
        >>> s = [len(a)]
        >>> _find_min(a, 0, s)
        12
        >>> _find_min(a, 1, s)
        18
    """
    if idx == stack[-1]:
        return a[stack.pop()]

    pidx = np.random.randint(idx, stack[-1])
    pidx = partition(a, pidx, idx, stack[-1])
    stack.append(pidx)

    return _find_min(a, idx, stack)

def _find_min_iter(a, idx, stack):
    """ iterative implementation for incremental quick sort
        which returns the minimum element in a while maintaining 
        an index and stack for subsequent calls. 

        The goal is to efficiently find only the first k sorted 
        elements
        
        Parameters:
        -----------
        a: the array (will be changed by the call
        idx: the start index 
        stack: a stack for bookeeping

        returns the minimum value. It will also be placed in idx

        Examples:
        ---------
        >>> a = [51, 81, 74, 12, 58, 92, 86, 25, 67, 33, 18, 41, 49, 63, 29, 37]
        >>> s = [len(a)]
        >>> _find_min_iter(a, 0, s)
        12
        >>> _find_min_iter(a, 1, s)
        18
    """
    while idx != stack[-1]:
        pidx = np.random.randint(idx, stack[-1])
        pidx = partition(a, pidx, idx, stack[-1])
        stack.append(pidx)

    return a[stack.pop()]


def first_k(a, k):
    """ sort the first k elements in a and return them.
        there's no guarantee on the order of the rest of the 
        array.

    Parameters:
    -----------
    a: the array to partially sort
    k: the number of elements to retrieve

    Examples:
    ---------
    >>> first_k([51, 81, 74, 12, 58, 92, 86, 25, 67, 33, 18, 41, 49, 63, 29, 37], 3)
    [12, 18, 25]
    """

    s = [len(a)]
    for i in range(k):
        _find_min_iter(a, i, s)

    return a[0:k]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
