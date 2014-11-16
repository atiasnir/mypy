import pylab as plt
import numpy as np

def corr_plot(df, method='spearman', **kwargs):
    """ pandas.DataFrame correlation matrix plot"""
    corr = df.corr(method=method)
    heat_plot(corr.fillna(0), vmin=-1, vmax=1, **kwargs)

def heat_plot(df, **kwargs):
    """ pandas.DataFrame heatmap """
    plt.pcolormesh(df.values, **kwargs)
    plt.xticks(0.5 + np.arange(df.shape[1]), df.columns, rotation='vertical')
    plt.yticks(0.5 + np.arange(df.shape[0]), df.columns)
    plt.colorbar()

def na_plot(df):
    """ pandas.DataFrame plot missing (NaN) values """
    mat = ~np.isnan(df.values)
    plt.pcolormesh(mat, cmap='Greys')
    plt.ylim((0,mat.shape[0]))
    plt.xticks(0.5 + np.arange(mat.shape[1]), df.columns, rotation='vertical')
