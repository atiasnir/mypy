import numpy as np
import scipy.linalg as la
import scipy.linalg.lapack as lapack
import scipy.stats as stats

def _cov2cor(v):
    '''
    Converts a symmetric positive definite matrix to a correlation matrix by 
    normalizing by the diagonal.
    '''
    r,c = v.shape
    assert r == c
    s = 1.0/np.sqrt(np.diag(v))
    v *= s.reshape(r,1)
    v *= s.reshape(1,c)

    return v

def partial_correlation(x, return_pvalue=False):
    """ x: samples X features """
    n, gp = x.shape 
    df = np.max(n - np.linalg.matrix_rank(x), 0)

    cvx = np.cov(x.T)
    r = la.cholesky(cvx, overwrite_a=True)
    icvx, info = lapack.dpotri(r, overwrite_c=True)

    pcor = -_cov2cor(icvx)
    pcor += pcor.T
    np.fill_diagonal(pcor, 1.0)

    if return_pvalue:
        statistic = pcor*np.sqrt(df/(1-pcor**2))
        pvalue = 2*stats.t.cdf(-abs(statistic), df)
        np.fill_diagonal(pvalue, 0.0)
        return pcor, pvalue

    return pcor