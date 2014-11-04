mypy
====

A collection of python tools. These mainly involve:

1. Data processing
2. Networks (graphs) and related algorithms

### mypy.pd
two helpers for pandas

 * split_and_stack, which creates multiple rows from string delimited columns
 * merge, which is an in-place replacement for pandas merge (can also be assigned to pandas.DataFrame.merge) which is slightly better (in my opinion, see the docs :-))

### mypy.network
A very useful SparseGraph class that behaves as a mixture of a sparse-matrix and a DataFrame

### mypy.network.random
random graph generation (geometric and preferential attachment) and degree-preserving shuffling (requires a compilation of the accompanying c library)

### mypy.os
Convenient cross-platform directory creation with won't blow up in you face

Setup
-----
Note that I currently don't package it. I just clone the repository directly into:
'<my_virtual_env>/lib/python2.7/site-packages'

If you don't know where it is run

    >>> import site
    >>> site.getsitepackages()[0]
