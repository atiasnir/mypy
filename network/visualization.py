import subprocess
import sparse_graph
from cStringIO import StringIO

def _as_dot_file(m, node_attributes=None, directed=False):
    s = StringIO()
    s.write('digraph G {' if directed else 'graph G {')
    s.write(' graph[bgcolor="transparent"]; ')

    if node_attributes is not None:
        for k, v in enumerate(node_attributes):
            s.write('%d[%s];' % (k, ','.join(['%s=%s' % (x,y) for x,y in v.iteritems()])))

    i, j = m.nonzero()
    if not directed:
        mask = i < j
        i, j = i[mask], j[mask]
        edge = '--'
    else:
        edge = '->'

    for u,v in zip(i, j):
        s.write('%d %s %d[penwidth=%.2f,color="#0000FF88"];' % (u, edge, v, m[u, v]))

    s.write('}')

    return s.getvalue()

def render(csr, node_attributes=None, directed=False, prog='dot', **kwargs):
    commandline = sum([['-' + x,y] for x,y in kwargs.iteritems()], [])

    pipe = subprocess.Popen([prog] + commandline, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    if isinstance(csr, sparse_graph.SparseGraph) and node_attributes is None:
        node_attributes = [{'label': x} for x in csr.names.index] 

    return pipe.communicate(_as_dot_file(csr, node_attributes, directed))[0]
