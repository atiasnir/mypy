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
