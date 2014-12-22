"""
download latest (human) release using
wget ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/HUMAN_9606_idmapping.dat.gz
"""
import pandas as pd

GENE_INFO_COLUMNS = ('tax_id', 'gene_id', 'symbol', 'locustag', 'synonyms',
                     'xrefs', 'chromosome', 'map_location', 'description',
                     'gene_type', 'gene_symbol', 'full_name',
                     'nomenclature_status', 'other_designations',
                     'modification_date')
def gene_info(filename, **kwd):
    defaults = {'names': GENE_INFO_COLUMNS, 'comment': '#', 'na_values': ('-',)}
    defaults.update(**kwd)
    return pd.read_table(filename, **defaults)


HIPPIE_COLUMNS = ('uniprot_id_a', 'entrez_id_a', 'uniprot_id_b', 'entrez_id_b', 'confidence', 'info')
def hippie(filename, **kwd):
    defaults = {'names': HIPPIE_COLUMNS }
    defaults.update(**kwd)
    return pd.read_table(filename, **defaults)


UNIPROT_IDMAPPING = ('protein', 'db', 'dbid')
def uniprot_mapping(filename, db=('UniProtKB-ID', 'GeneID'), raw=False, **kwd):
    defaults = {'names': UNIPROT_IDMAPPING }
    defaults.update(kwd)

    raw_data = pd.read_table(filename, **defaults)
    if raw:
        return raw_data
    
    return pd.pivot_table(raw_data, 'dbid', index='protein', columns='db',
            aggfunc=lambda x: "|".join(x)).dropna(subset=db)

ANAT_COLUMNS = ('interactor_a', 'interactor_b', 'confidence', 'directed')
def anat_network(filename, **kwds):
    defaults = {'names': ANAT_COLUMNS}
    defaults.update(kwds)
    return pd.read_table(filename, **defaults)

BIOGRID_COLUMNS = ('biogrid_interaction_id', 'entrez_a', 'entrez_b',
                   'biogrid_a', 'biogrid_b', 'systematic_name_a',
                   'systematic_name_b', 'official_symbol_a',
                   'official_symbol_b', 'synonyms_a', 'synonyms_b',
                   'experimental_system', 'experimental_system_type', 'author',
                   'pubmed_id', 'organism_a', 'organism_b', 'throughput',
                   'score', 'modification', 'phenotypes', 'qualifications',
                   'tags', 'source_database')
def biogrid(filename, use_common_columns=True, **kwds):
    """ Reads BioGRID's tab2 format """
    defaults = {'names': BIOGRID_COLUMNS,
                'comment': '#', 
                'na_values': ('-',)}
    if use_common_columns:
        if 'usecols' in kwds:
            kwds['usecols'] += ('entrez_a', 'entrez_b', 'experimental_system_type')
        else:
            kwds['usecols'] = ('entrez_a', 'entrez_b', 'experimental_system_type')
    defaults.update(kwds)
    return pd.read_table(filename, **defaults)

def biogrid_physical(filename, **kwds):
    if 'usecols' in kwds:
        kwds['usecols'] += ('experimental_system_type',)
    result = biogrid(filename, **kwds)
    result.drop(result.index[result.experimental_system_type != 'physical'], inplace=True)
    result.drop('experimental_system_type', axis=1, inplace=True)
    return result

def biogrid_genetic(filename, **kwds):
    if 'usecols' in kwds:
        kwds['usecols'] += ('experimental_system_type',)
    result = biogrid(filename, **kwds)
    result.drop(result.index[result.experimental_system_type != 'genetic'], inplace=True)
    result.drop('experimental_system_type', axis=1, inplace=True)
    return result
