mypy
====

A collection of python tools. These mainly involve:

1. Data processing
2. Networks (graphs) and related algorithms

### mypy.pd
helpers for pandas

 * split_and_stack, which creates multiple rows from string delimited columns
 * merge, which is an in-place replacement for pandas merge (can also be assigned to pandas.DataFrame.merge) which is slightly better (in my opinion, see the docs :-))
 * data_uri() helps to generate links to data in ipython notebook (avoid using large data frames). The basics:
 	>>> from IPython.display import HTML
	>>> df = pandas.DataFrame(...)
	>>> data_uri(df, HTML)

### mypy.network
A very useful SparseGraph class that behaves as a mixture of a sparse-matrix and a DataFrame.
Additionally, there are a few algorithms in this package, some are better implemented than their `scipy` counterparts.

### mypy.network.random
random graph generation (geometric and preferential attachment) and degree-preserving shuffling (requires a compilation of the accompanying c library)

### mypy.os
Convenient cross-platform directory creation with won't blow up in you face

### mypy.stats
Statistical utilities. Currently contains only partial correlation

### mypy.metrics
Currently contains Jaccard pairwise distance for sparse matrices (much faster than the dense version that is shipped with `scipy`)

Setup
-----
Note that I currently don't package it. I just clone the repository directly into:
'<my_virtual_env>/lib/python2.7/site-packages'

If you don't know where it is run

    >>> import site
    >>> site.getsitepackages()[0]
