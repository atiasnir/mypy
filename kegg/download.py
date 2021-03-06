#!/usr/bin/env python
import joblib
import mypy.os_utils
import os.path

from bs4 import BeautifulSoup
import requests

import pandas as pd

import paths

KEGG_BASE_URL = 'http://rest.kegg.jp' 

def pathway_list(species='hsa'):
    """ download list of all KEGG pathways """
    response = requests.get("{domain}/list/pathway/{species}".format(domain=KEGG_BASE_URL, species=species))
    page = BeautifulSoup(response.text)
    return pd.DataFrame([line.split('\t') for line in page.body.text.split('\n')[:-1]],
            columns=['pathway', 'description'])

def get_entries(path, page):
    """ aggregate <entry> tag """
    entries = []
    for entry in page.find_all('entry'):
        entry.attrs.update({'pathway' : path})
        entries.append(entry.attrs)
    return pd.DataFrame(entries)

def get_reactions(path, page):
    """ aggreagate <reaction> tag """
    reactions = []
    reactants = []
    for reaction in page.find_all('reaction'):
        reaction.attrs.update({'pathway': path})
        reactions.append(reaction.attrs)
        
        for sub in reaction.find_all('substrate'):
            sub.attrs.update({'reaction' : reaction['name'], 'role':
                'substrate', 'pathway': path})
            reactants.append(sub.attrs)
        for prod in reaction.find_all('product'):
            prod.attrs.update({'reaction' : reaction['name'], 'role' :
                'product', 'pathway' : path})
            reactants.append(prod.attrs)
    
    reactions = pd.DataFrame(reactions).rename(columns = {'id' : 'reaction_id', 'name' : 'reaction'})
    reactants = pd.DataFrame(reactants).rename(columns = {'id' : 'reactant_id', 'name' : 'reactant'})
    try:
        return pd.merge(reactions, reactants)
    except:
        return pd.DataFrame({'reaction' : []})
        
def get_relations(path, page):
    """ aggregate <relation> tag """
    relations = []
    for relation in page.find_all('relation'):
        relation.attrs.update({'pathway' : path})
        subtype = relation.find('subtype') # are there ever more than one?
        if subtype is not None:
            relation.attrs.update(subtype.attrs)
        relations.append(relation.attrs)
    return pd.DataFrame(relations)

def download_pathway(path):
    """ retrieve all entries of the specified pathway """
    response = requests.get("{domain}/get/{path}/kgml".format(domain=KEGG_BASE_URL, path=path))
    page = BeautifulSoup(response.text)

    entries = get_entries(path, page)
    reactions = get_reactions(path, page)
    relations = get_relations(path, page)
    return entries, reactions, relations

def download_all_pathways(path_list, **kwd):
    """ retrieve pathways in parallel """
    defaults = {'n_jobs': 100, 'backend': 'threading'}
    defaults.update(kwd)
    return joblib.Parallel(**defaults)(joblib.delayed(download_pathway)(path) for path in path_list)
    
def concat_rows(dfs):
    """ concatenate a list of data frames by row """
    return pd.concat(dfs, axis=0)

def weave(x):
    """ transform list of tuples into tuple of lists (transpose)"""
    return zip(*list(x))

def construct(species='hsa'):
    """ load data and aggregate into 'pathway, 'entries', 'reactions'
    and 'relations' tables """
    pathways = pathway_list(species)
    annotations = download_all_pathways(pathways.pathway)
    entries, reactions, relations = map(concat_rows, weave(annotations))
    return {paths.PATHWAY_FILENAME: pathways, 
            paths.ENTRY_FILENAME: entries,
            paths.REACTION_FILENAME: reactions,
            paths.RELATION_FILENAME: relations}

def download_kegg(path, species='hsa'):
    """ download kegg and save it to 'path/.kegg/' """
    kegg = construct(species)
    mypy.os_utils.mkdir(os.path.join(path, species))
    for name, df in kegg.items():
        df.to_csv(paths.construct_path(path, species, name), index=False, sep='\t')
