from urllib.request import urlretrieve
import datetime
import os
import pandas as pd

def download(url):
    #TODO: check that download was successful
    filename = os.path.basename(url)
    urlretrieve(url, filename)
    return filename

_ROOT_PATH = '/home/bnet/jandanielr/mydata'
_DB = 'db.tab'
_CURRENT = 'current'
PATH = os.path.join(_ROOT_PATH, _CURRENT)
DB_PATH = os.path.join(PATH, _DB)
if __name__ == '__main__':
    # setup new directory
    db = pd.read_table(_DB)
    oldPath = os.getcwd()
    newPath = _ROOT_PATH
    os.chdir(newPath)
    try:
        os.unlink(_CURRENT)
    except FileNotFoundError: # occurs on first run
        pass
    today = datetime.datetime.now().strftime('%Y_%m_%d')
    print('downloading into', today)
    os.mkdir(today)
    os.chdir(today)
    # download all db and save filename mapping to current
    db['DATE'] = today
    db['FILE'] = db['URL'].apply(download)
    db.to_csv(_DB, sep='\t', index=False)
    # reset symlink
    os.chdir(newPath)
    os.symlink(today, _CURRENT)
    os.chdir(oldPath)
    print('done')
