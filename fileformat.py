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
    
    return pd.pivot_table(raw_data, 'dbid', index='protein', columns='db', aggfunc=lambda x: "|".join(x)).dropna()

ANAT_COLUMNS = ('interactor_a', 'interactor_b', 'confidence', 'directed')
def anat_network(filename, **kwds):
    defaults = {'names': ANAT_COLUMNS}
    defaults.update(kwds)
    return pd.read_table(filename, **defaults)

