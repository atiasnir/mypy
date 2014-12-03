#!/usr/bin/env python
import argparse
import sys
import concurrent.futures
from mypy.os import mkdir

from bs4 import BeautifulSoup
import requests

import pandas as pd


def pathway_list():
    """ download list of all KEGG pathways """
    response = requests.get("http://rest.kegg.jp/list/pathway/hsa/")
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

def pathway(path):
    """ retrieve all entries of the specified pathway """
    response = requests.get("http://rest.kegg.jp/get/{path}/kgml".format(path=path))
    page = BeautifulSoup(response.text)

    entries = get_entries(path, page)
    reactions = get_reactions(path, page)
    relations = get_relations(path, page)
    return entries, reactions, relations

def load_async(path_list):
    """ retrieve pathways in parallel """
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_url = {executor.submit(pathway, path): path for path in
                path_list}
        for future in concurrent.futures.as_completed(future_to_url):
            yield future.result()

def concat_rows(dfs):
    """ concatenate a list of data frames by row """
    return pd.concat(dfs, axis=0)

def weave(x):
    """ transform list of tuples into tuple of lists (transpose)"""
    return zip(*list(x))

def construct():
    """ load data and aggregate into 'pathway, 'entries', 'reactions'
    and 'relations' tables """
    pathways = pathway_list()
    annotations = load_async(pathways.pathway)
    entries, reactions, relations = map(concat_rows, weave(annotations))
    return {'pathways':pathways, 'entries':entries, 'reactions':reactions,
            'relations':relations}

def download_kegg(path):
    """ download kegg and save it to 'path/.kegg/' """
    kegg = construct()
    mkdir(path)
    for name, df in kegg.items():
        df.to_csv(path + name + '.csv', index=False)
    return kegg
