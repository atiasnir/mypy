
import numpy as np 
from scipy.sparse import csr_matrix

#import pyximport
#pyximport.install()

from _topological_sort import topological_sort

names = np.array(['7', '5', '3', '11', '8', '2', '9', '10'])
#                        7 5 3 11 8 2 9 10
#                    7:  0 0 0  1 1 0 0  0
#                    5:  0 0 0  1 0 0 0  0
#                    3:  0 0 0  0 1 0 0  1
#                   11:  0 0 0  0 0 1 1  1
#                    8:  0 0 0  0 0 0 1  0
#                    2:  0 0 0  0 0 0 0  0
#                    9:  0 0 0  0 0 0 0  0
#                   10:  0 0 0  0 0 0 0  0
m = csr_matrix(np.array([[0, 0, 0, 1, 1, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 0, 1, 0, 0, 1],
                         [0, 0, 0, 0, 0, 1, 1, 1],
                         [0, 0, 0, 0, 0, 0, 1, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0]]))

print names[topological_sort(m)]
