#import pyximport
#pyximport.install()

import numpy as np 
import scipy.sparse as sparse
import scipy.sparse.csgraph as csg
import depth_first

i, j = zip((0, 1),
           (0, 2),
           (1, 2),
           (2, 3),
           (2, 5),
           (3, 4),
           (3, 6),
           (4, 6),
           (5, 7))

g = sparse.csr_matrix((np.ones(len(i)),(i,j)), shape=(8,8))
g = g + g.T

import timeit

o, p = depth_first.depth_first_order(g, 0)
print "order:", o
print "pred :", p

o, p = csg.depth_first_order(g, 0)
print "order:", o
print "pred :", p

# timing
print "my:", timeit.timeit('o, p = depth_first.depth_first_order(g, 0)', setup='from __main__ import *', number=100000)
print "scipy:", timeit.timeit('o, p = csg.depth_first_order(g, 0)', setup='from __main__ import *', number=100000)

