import scipy.sparse as sparse
import gurobipy as gurobi

#i, j =[list(x) for x in  zip(('a','b'),
#                             ('a','d'),
#                             ('b','c'),
#                             ('b','d'),
#                             ('b','e'),
#                             ('c','d'),
#                             ('c','e'),
#                             ('d','e'),
#                             ('d','f'),
#                             ('d','g'),
#                             ('e','g'),
#                             ('f','g'))]
#
#g = net.SparseGraph.from_indices(i, j)

def _build_model(g, return_x=False):
    s = (2*g).data.todense()-1 # g==0 => s == -1; g ==1 => s == 1

    m = gurobi.Model("cluster_edit")
    n = g.data.shape[0]

    # define variables
    x = {(i, j): m.addVar(vtype=GRB.BINARY, name="x_%s_%s" % (i, j)) for i in range(n) for j in range(i+1, n)}
    m.update()

    # add objective
    edges = g.nnz / 2 # assume symmetric matrix with no self-edges
    m.setObjective(edges - quicksum(x[i, j]*s[i, j] for i in range(n) for j in range(i+1, n)), GRB.MINIMIZE)

    # add constraints
    for i in range(n):
        for j in range(i+1, n):
            for k in range(j+1, n):
                m.addConstr(x[i, j] + x[j, k] - x[i, k] <= 1)
                m.addConstr(x[i, j] - x[j, k] + x[i, k] <= 1)
                m.addConstr(-x[i, j] + x[j, k] + x[i, k] <= 1)
    m.update()

    return m if not return_x else (m, x)

def cluster_edit(g, return_graph=True):
    """ A naive ILP for cluster editing.
        The method returns the number of edits and, optionally, the resulting cluster graph.

        * requires gurobi optimizer to be installed *
    """
    m, x = _build_model(g, return_x=True)
    m.optimize()

    if not return_graph:
        return m.objVal

    cg = sparse.csr_matrix(g.shape, np.int)
    for k, v in x.iteritems():
        if v.getAttr(gurobi.GRB.x) > 0:
            cg[k] = 1

    cg += cg.T # make symmetric
    return m.objVal, cg
