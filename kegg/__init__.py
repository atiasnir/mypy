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

import paths

class Kegg(object):
    pass

def load(species='hsa', cache_folder=None, force_download=False):
    home = os.path.expanduser('~')
    if cache_folder is None:
        if os.path.exists(home + '/bnet'):
            cache_folder = home + '/bnet/.kegg'
        else:
            cache_folder = home + '/.kegg'

    if force_download or not os.path.isfile(paths.construct_path(cache_folder, species, paths.PATHWAY_FILENAME)):
        from .download import download_kegg
        download_kegg(cache_folder, species) # removed return value due to suspected pandas bug

    pathways = pd.read_table(paths.construct_path(cache_folder, species, paths.PATHWAY_FILENAME))
    entries = pd.read_table(paths.construct_path(cache_folder, species, paths.ENTRY_FILENAME))
    reactions = pd.read_table(paths.construct_path(cache_folder, species, paths.REACTION_FILENAME))
    relations = pd.read_table(paths.construct_path(cache_folder, species, paths.RELATION_FILENAME))

    # Basic building blocks
    if species == 'hsa':
        pathways.loc[:,'description'] = pathways.loc[:,'description'].str.replace(' - Homo sapiens \(human\)','')

    # Nodes
    nodes = split_and_stack(entries[entries['type'] == 'gene'], 'name')
    nodes['GeneID'] = nodes.name.str.replace(species + ':', '')
    nodes = nodes.merge(pathways)

    # Edges
    entry1 = pd.merge(relations, nodes[['pathway', 'id',
        'GeneID']].rename(columns={'id': 'entry1', 'GeneID':0}))
    entry2 = pd.merge(relations, nodes[['pathway', 'id',
        'GeneID']].rename(columns={'id': 'entry2', 'GeneID':1}))
    edges = pd.merge(entry1, entry2).merge(pathways)

    retval = Kegg()
    retval.pathways = pathways
    retval.entries = entries
    retval.reactions = reactions
    retval.relations = relations
    retval.nodes = nodes
    retval.edges = edges

    return retval
