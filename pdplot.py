import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn.metrics
        
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, dendrogram

def corr_plot(df, method='spearman', **kwargs):
    """ pandas.DataFrame correlation matrix plot"""
    corr = df.corr(method=method)
    heat_plot(corr.fillna(0), vmin=-1, vmax=1, **kwargs)

def heat_plot(df, cluster=False, colorbar=True, **kwargs):
    """ pandas.DataFrame heatmap """
    view = df
    if cluster:
        rows, cols = _cluster_idx(df)
        view = df.iloc[rows, cols]
    plt.pcolormesh(view.values, **kwargs)
    plt.xticks(0.5 + np.arange(df.shape[1]), view.columns, rotation='vertical')
    plt.xlim(0,df.shape[1])
    plt.yticks(0.5 + np.arange(df.shape[0]), view.index)
    plt.ylim(0,df.shape[0])
    if colorbar:
        plt.colorbar()

def _cluster_idx(df):
    """ sort indices by clusters """
    dcol = pdist(df.T)
    drow = pdist(df)
    lcol = linkage(dcol)
    lrow = linkage(drow)
    cols = dendrogram(lcol, no_plot=True)['leaves']
    rows = dendrogram(lrow, no_plot=True)['leaves']
    return rows,cols

def na_plot(df, cluster=False):
    """ pandas.DataFrame plot missing (NaN) values """
    mat = pd.DataFrame(~np.isnan(df.values))
    if cluster:
        rows, cols = _cluster_idx(mat)
        mat = mat.iloc[rows,cols]
    plt.pcolormesh(mat.values, cmap='Greys')
    plt.ylim((0,mat.shape[0]))
    plt.xticks(0.5 + np.arange(mat.shape[1]), df.columns, rotation='vertical')
    plt.xlim(0,mat.shape[1])

def auc_plot(scores, gold_standard, label_template=None, **kwargs):
    fpr, tpr, _ = sklearn.metrics.roc_curve(gold_standard, scores)
    auc_score = sklearn.metrics.auc(fpr, tpr)

    should_add_line = len(plt.gcf().axes) == 0

    if label_template is not None:
        kwargs['label'] = label_template.format(auc=auc_score)

    plt.plot(fpr, tpr, **kwargs)
    
    if should_add_line:
        plt.plot([0, 1], [0, 1], 'k--')

    return auc_score
