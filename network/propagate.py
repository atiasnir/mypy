import numpy as np
import scipy.sparse as sparse

def normalize(m):
    """ Normalization for propagation """
    data = 1.0 / np.sqrt(m.sum(1))
    d = sparse.dia_matrix((data.T,[0]), (len(data),len(data)))
    return d * m * d

def propagate(m, y, alpha=0.6, eps=1e-5, max_iterations=1000):
    # TODO: Create nicer interface for y of type pd.Series 
    #       (align to network and return value as Series with index)
    f = (1-alpha)*y
    g = alpha * m
    for i in range(max_iterations):
        fold, f = f, g*f + y
        if la.norm(f-fold) < eps:
            break
    return f 

