import os

def mkdir(path):
    """ create directory and itermediates if not already present """
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
