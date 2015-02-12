from urllib.request import urlretrieve
import datetime
import os
import pandas as pd

class _cd:
    """ changes directory, it will be created if non existant """
    def __init__(self, newPath):
        self.newPath = newPath
        if not os.path.isdir(newPath):
            os.mkdir(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def download(url):
    """ saves url to current folder. returns filename """
    #TODO: check that download was successful
    filename = os.path.basename(url)
    urlretrieve(url, filename)
    return filename

def link_static(path):
    """ symlink _CURRENT_PATH/file -> _STATIC_PATH/file """
    static_path = os.path.join(_ROOT_PATH, _STATIC_PATH, path)
    current_path = os.path.join(_CURRENT_PATH, path)
    os.symlink(static_path, current_path)

_ROOT_PATH = '/home/bnet/DB'
_STATIC_PATH = 'static'
_CURRENT_PATH = 'current'

_DOWNLOAD = 'download.tab'
_STATIC = 'static.tab'
_DB = 'db.tab'
_db_cols = ['DB', 'SPECIES', 'DATE', 'FILE', 'URL']

PATH = os.path.join(_ROOT_PATH, _CURRENT_PATH)
DB_PATH = os.path.join(PATH, _DB)

if __name__ == '__main__':
    to_download = pd.read_table(_DOWNLOAD)
    with _cd(_ROOT_PATH):
        try:
            os.unlink(_CURRENT_PATH)
        except FileNotFoundError: # occurs on first run
            pass
        new_dir = datetime.datetime.now().strftime('%Y_%m_%d')
        
        with _cd(new_dir): # download and save filename mapping to current
            to_download['DATE'] = new_dir
            to_download['FILE'] = to_download['URL'].apply(download)

        # reset symlink
        os.symlink(new_dir, _CURRENT_PATH)

        # include static files and save db table
        if os.path.isfile(_STATIC):
            static = pd.read_table(_STATIC)
            static['FILE'].apply(link_static)
            (pd.concat([to_download, static])
                    [_db_cols]
                    .to_csv(DB_PATH, sep='\t', index=False))
        else:
            to_download[_db_cols].to_csv(DB_PATH, sep='\t', index=False)
        
