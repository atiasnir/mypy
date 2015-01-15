import os.path

PATHWAY_FILENAME = 'pathways'
ENTRY_FILENAME = 'entries'
RELATION_FILENAME = 'relations'
REACTION_FILENAME = 'reactions'

def construct_path(path, species, filename):
    extension = '' if filename.endswith('.tsv') else '.tsv'
    return os.path.join(path, species, filename + extension)
