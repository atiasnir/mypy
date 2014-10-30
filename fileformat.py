import pandas as pd

GENE_INFO_COLUMNS = ('tax_id', 'gene_id', 'symbol', 'locustag', 'synonyms',
                     'xrefs', 'chromosome', 'map_location', 'description',
                     'gene_type', 'gene_symbol', 'full_name',
                     'nomenclature_status', 'other_designations',
                     'modification_date')

def gene_info(filename):
    return pd.read_table(filename, names=GENE_INFO_COLUMNS, comment='#', na_values=('-',))
