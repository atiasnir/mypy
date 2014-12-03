"""
KEGG : expose the KEGG database as a set of 'pandas.DataFrame's

Allows for fast and convenient annotation of other 'pandas.DataFrame's
using the 'merge' and 'groupby' operations.

The database is initially downloaded into the path defined in 'settings.py'.
For subsequent import the already downloaded tables are read from cache.
"""
import os.path
import pandas as pd
from mypy.pd import split_and_stack

from .settings import PATH

if not os.path.isfile(PATH + 'pathways.csv'):
    from .download import download_kegg
    msg = """ initializing module:
    downloading kegg to {p}
    change the path by modifying "settings.py"
    """
    print(msg.format(p = PATH))
    kegg = download_kegg(PATH)

else:
    from glob import glob
    kegg = {}
    for file_path in glob(PATH + '*.csv'):
        kegg[file_path.split('/')[-1][:-4]] = pd.read_csv(file_path)

"""
Basic building blocks
"""
pathways = kegg['pathways']
pathways.loc[:,'description'] = pathways.loc[:,'description'].str.replace(' - Homo sapiens \(human\)','')

entries = kegg['entries']
entries_name = split_and_stack(entries, 'name')

reactions = kegg['reactions']
relations = kegg['relations']

"""
Nodes
"""
nodes = split_and_stack(entries[entries.type == 'gene'], 'name')
nodes['GeneID'] = nodes.name.str.replace('hsa:','')
nodes = nodes.merge(pathways)

"""
Edges
"""
entry1 = pd.merge(relations, nodes[['pathway', 'id',
    'GeneID']].rename(columns={'id': 'entry1', 'GeneID':0}))
entry2 = pd.merge(relations, nodes[['pathway', 'id',
    'GeneID']].rename(columns={'id': 'entry2', 'GeneID':1}))
edges = pd.merge(entry1, entry2).merge(pathways)
del entry1
del entry2
