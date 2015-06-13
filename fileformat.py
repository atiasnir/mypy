""" READ all kinds of files

>>> import mypy.fileformat as ff
>>> ff.parse_your_favorite_file(filename)
"""
import os
import pandas as pd

GENE_INFO_COLUMNS = ('tax_id', 'gene_id', 'symbol', 'locustag', 'synonyms',
                     'xrefs', 'chromosome', 'map_location', 'description',
                     'gene_type', 'gene_symbol', 'full_name',
                     'nomenclature_status', 'other_designations',
                     'modification_date')
def gene_info(filename, remove_newentry=True, **kwd):
    defaults = {'names': GENE_INFO_COLUMNS, 'comment': '#', 'na_values': ('-',)}
    defaults.update(**kwd)
    result = pd.read_table(filename, **defaults)
    if remove_newentry:
        result.drop(result.index[result.symbol=='NEWENTRY'], inplace=True)
    return result


HIPPIE_COLUMNS = ('uniprot_id_a', 'entrez_id_a', 'uniprot_id_b', 'entrez_id_b', 'confidence', 'info')
def hippie(filename, **kwd):
    defaults = {'names': HIPPIE_COLUMNS }
    defaults.update(**kwd)
    return pd.read_table(filename, **defaults)


UNIPROT_IDMAPPING = ('protein', 'db', 'dbid')
def uniprot_mapping(filename, db=('UniProtKB-ID', 'GeneID'),
        raw=False, separator='|', **kwd):
    defaults = {'names': UNIPROT_IDMAPPING,
            'compression': 'gzip'}
    defaults.update(kwd)
    raw_data = pd.read_table(filename, **defaults)
    if raw:
        return raw_data
    
    return pd.pivot_table(raw_data, 'dbid', index='protein', columns='db',
            aggfunc=lambda x: separator.join(x)).dropna(subset=db)

def inconsistent(df, db, df_cols, db_cols):
    """given one putative (df) and on true (db) mapping
    return the inconsistent part of df"""
    merged = pd.merge(df, db, left_on=df_cols, right_on=db_cols, how='left')
    return merged[merged[db_cols[0]].isnull()][df.columns]

def uniprot_humsavar(filename):
    """
    read amino-acid polymorphisms from
    http://uniprot.org/docs/humsavar
    """
    import re
    import io
    out = io.StringIO()
    out.write('\t'.join(['GENE_NAME', 'ACC', 'FTId', 'ORIGINAL',
        'POSITION', 'MUTATED', 'VARIANT', 'dbSNP', 'DISEASE']) + '\n')
    with open(filename) as f:
        s = re.compile('(\S+)\s+(\S+)\s+(\S+)\s+p\.([a-zA-Z]+)(\d+)([a-zA-Z]+)\s+(\S+)\s+(\S+)\s+(.*)') # one regex to rule them all
        for i,line in enumerate(f):
            if i < 30: # header
                continue
            if line == '\n': # reached end
                break
            out.write('\t'.join(s.match(line.strip()).groups()) + '\n')
    out.seek(0)
    return pd.read_table(out, na_values='-')

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

GENE_ASSOCIATION_COLUMNS = ('db', 'db_object_id', 'db_object_symbol',
                            'qualifier', 'go_id', 'db_reference',
                            'evidence_code', 'with_from', 'aspect',
                            'db_object_name', 'db_object_synonym',
                            'db_object_type', 'taxon', 'date', 'assigned_by',
                            'annotation_extension', 'gene_product_form_id')
GENE_ASSOCIATION_EXPERIMENTAL_EVIDENCE = ('EXP', 'IDA', 'IPI', 'IMP', 'IGI', 'IEP')

def go_annotation(filename, experimental=True, **kwds):
    defaults = {'comment' : '!',
            'compression' : 'gzip',
            'names': GENE_ASSOCIATION_COLUMNS}

    if experimental and 'usecols' in kwds:
        kwds['usecols'] += ('evidence_code', )

    defaults.update(kwds)
    result = pd.read_table(filename, **defaults)

    if experimental:
        retain_mask = result.evidence_code.isin(GENE_ASSOCIATION_EXPERIMENTAL_EVIDENCE)
        result.drop(result.index[~retain_mask], inplace=True)

    return result

PHOSPHOSITE_COLUMNS = ('kinase', 'kinase_id', 'kinase_gene', 'location', 'kinase_organism',
                       'substrate', 'substrate_entrez', 'substrate_id', 'substrate_gene', 'substrate_organism', 
                       'substrate_residue', 'site_grp_id', 'site_amino_acids', 'in_vivo_rxn', 'in_vitro_rxn', 'cst_cat')

def phosphosite(filename, organism=None, **kwds):
    defaults = {'names': PHOSPHOSITE_COLUMNS, 
            'compression' : 'gzip', 'skiprows': 4}
    defaults.update(**kwds)

    tbl = pd.read_table(filename, **defaults)
    if 'in_vivo_rxn' in tbl:
        tbl.in_vivo_rxn = tbl.in_vivo_rxn.str.startswith('X')

    if 'in_vitro_rxn' in tbl:
        tbl.in_vitro_rxn = tbl.in_vitro_rxn.str.startswith('X')

    if organism is not None:
        if type(organism) is str:
            mask = (tbl.kinase_organism == organism) & (tbl.substrate_organism == organism)
        else:
            mask = tbl.kinase_organism.isin(organism) & tbl.substrate_organism.isin(organism)
        tbl.drop(tbl.index[~mask], inplace=True)

    return tbl

def _phosphosite_extra(filename, organism):
    df = pd.read_csv(filename)
    if organism is not None:
        if hasattr(organism, '__iter__'):
            mask = df.ORGANISM.isin(organism)
        else:
            mask = df.ORGANISM == organism
        df.drop(df.index[~mask], inplace=True)
    return df

def regulatory_phosphosites(filename, organism=None, **kwds):
    return _phosphosite_extra(filename, organism)

def disease_associated_phosphosites(filename, organism=None, **kwds):
    return _phosphosite_extra(filename, organism)

SGD_FEATURES_FILE_COLUMNS = ('sgdid', 'feature_type', 'feature_qualifier',
                             'feature_name', 'gene_name', 'alias',
                             'parent_feature_name', 'secondary_sgdid',
                             'chromosome', 'start_coordinate',
                             'stop_coordinate', 'strand', 'position',
                             'coordinate_version', 'sequence_version',
                             'description')

def sgd_features(filename, **kwds):
    defaults = {'names': SGD_FEATURES_FILE_COLUMNS }
    defaults.update(**kwds)
    return pd.read_table(filename, **defaults)


SGD_PHENOTYPE_FILE_COLUMNS = ('feature_name', 'feature_type', 'gene_name',
                              'sgdid', 'reference', 'experiment_type',
                              'mutant_type', 'allele', 'strain_background',
                              'phenotype', 'chemical', 'condition', 'details',
                              'reporter')
def sgd_phenotype(filename, **kwds):
    defaults = {'names': SGD_PHENOTYPE_FILE_COLUMNS }
    defaults.update(**kwds)
    return pd.read_table(filename, **defaults)

def obo(filename):
    relations = []
    terms = []

    with open(filename, 'r') as f:
        rec = None
        for line in f:
            if (rec is None) and line.startswith('[Term]'):
                rec = {}
                continue

            if rec is not None:
                if line.isspace():
                    if (rec is not None) and ('go_id' in rec):
                        terms.append(rec)
                    rec = None
                elif line.startswith('id: '):
                    rec['go_id'] = line[4:-1]
                elif line.startswith('is_a: '):
                    relations .append((rec['go_id'], line[6:line.index('!', 6)-1], 'is_a'))
                elif line.startswith('relationship: part_of '):
                    relations .append((rec['go_id'], line[22:line.index('!', 22)-1], 'part_of'))
                elif line.startswith('name: ' ):
                    rec['name'] = line[6:-1]
                elif line.startswith('description: '):
                    rec['description'] = line[13:-1]
                elif line.startswith('namespace: '):
                    rec['namespace'] = line[11:-1]
                elif line.startswith('is_obsolete: true'):
                    rec['obsolete'] = True
                elif line.startswith('replaced_by: '):
                    rec['replaced_by'] = line[13:-1]

    terms = pd.DataFrame(terms)
    relations = pd.DataFrame(relations, columns=('go_id_category', 'go_id_parent', 'relation'))

    return terms, relations

COSMIC_COLUMNS = ['ID_SAMPLE', 'SAMPLE_NAME', 'GENE_NAME', 'REGULATION', 'Z_SCORE', 'ID_STUDY']
def cosmic(base_path, disease, filter_incomplete_studies=True, **kwargs):
    """ read cosmic study
    studies should report 18068 genes pre patient
    >>> import mypy.fileformat.read as reader
    >>> aml = reader.cosmic('db/Cosmic', 'AcuteMyeloidLeukemia') """
    full_path = os.path.join(base_path, disease + '.tsv')
    df = pd.read_table(full_path, header=None, **kwargs)
    df.columns = COSMIC_COLUMNS
    if filter_incomplete_studies:
        df = df.groupby('ID_SAMPLE').filter(lambda df : len(df) == 18068)
    return df

def cosmic_list(base_path):
    """ get list of available cosmic files
    >>> reader.cosmic_list('db/Cosmic')
    """
    import glob
    files = glob.glob(os.path.join(base_path, '*.tsv'))
    names = [os.path.basename(x)[:-4] for x in files]
    return [x for x in names if x != 'CosmicGeneExpression'] # skip big dataset

def cosmic_mutation(base_path, cancer, kind, **kwargs):
    """ read cosmic study
    >>> import mypy.fileformat.read as reader
    >>> mutation_kind = reader.cosmic_mutation_kinds('db/CosmicMutations')[0]
    >>> cancer = reader.cosmic_mutation_cancers('db/CosmicMutations', mutation_kind)[0]
    >>> df = reader.cosmic_mutation('db/CosmicMutations', cancer, mutation_kind)
    """
    full_path = os.path.join(base_path, '{}_{}.tsv'.format(cancer, kind))
    df = pd.read_table(full_path, **kwargs)
    return df

def cosmic_mutation_kinds(base_path):
    """ retrieve all mutations types
    >>> reader.cosmic_mutation_types('db/Cosmic')
    """
    import glob
    files = glob.glob(os.path.join(base_path, '*.tsv'))
    kinds = set([])
    for x in files:
        file = os.path.basename(x)[:-4]
        try:
            kinds.add(file.split('_', 1)[1])
        except:
            print(file)
    return kinds

def cosmic_mutation_cancers(base_path, mutation):
    """ get list of available cosmic files filtered by mutation type"""
    import glob
    files = glob.glob(os.path.join(base_path, '*{}.tsv'.format(mutation)))
    return [os.path.basename(x)[:-4].split('_', 1)[0] for x in files]

CORUM_COLUMNS = ('complex_id', 'complex_name', 'sysnonyms', 'organism', 
                          'uniprot_gene_id', 'gene_id', 'method', 'pubmed', 
                          'catgeories', 'func_comment', 'disesae_comment', 'subunit_comment')
def corum(filename, use_common_columns=True, **kwds):
    defaults = {'sep': ';',
                'names': CORUM_COLUMNS,
                'skiprows': 1,
                
                }
    if use_common_columns:
        defaults['usecols'] = ('complex_id', 'organism', 'uniprot_gene_id')

    defaults.update(kwds)
    return pd.read_csv(filename, **defaults)
