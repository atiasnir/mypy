import pandas as pd
import subprocess
import tempfile
import os
import os.path

def terminals_table(anchor, terminals):
    """turn anchor and list of terminal into the correct format
    pd.DataFrame <anchor> <terminal>"""
    df = pd.DataFrame(terminals, columns=['terminal'])
    df['anchor'] = anchor
    return df[['anchor', 'terminal']]

_RESULT_COLUMNS = ['interactor_a', 'interactor_b', 'confidence', 'transformed', 'directed']
def run(network, terminals, alpha=0.25, verbose=False):
    """ Run ANAT returning the network as pd.DataFrame
    Parameters:
        alpha - default 0.25
    Returns:
        pd.DataFrame <interactor_a> <interactor_b> <confidence> <transformed> <directed>
    
    >>> n = mypy.fileformat.read.anat_network()
    >>> t = terminals_table('1017', ['2843', '1232', '1958']) # these are truly random
    >>> run(n[n.confidence > 0.5], t, verbose=True)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        _out = os.path.join(tmpdir, 'out')
        network.to_csv(os.path.join(tmpdir, 'network'), index=False, sep='\t', header=None)
        terminals.to_csv(os.path.join(tmpdir, 'terminals'), index=False, sep='\t', header=None)
        output = subprocess.check_output(['steinprt',
            '-n', 'network',
            '-s', 'terminals',
            '-b', '{:0.2f}'.format(alpha),
            '-f', tmpdir,
            '-r', _out]) # -f flag ignored by steinprt
        if verbose:
            print(output)
        return pd.read_table(_out, sep = ' ', names = _RESULT_COLUMNS)

def filter(network, confidence):
    return network[network.confidence > confidence]

def _run_example():
    import mypy.fileformat.read as reader
    n = reader.anat_network()
    t = terminals_table('1017', ['2843', '1232', '1958']) # these are truly random
    result = run(filter(n, 0.5), t, verbose=True)
    return result
