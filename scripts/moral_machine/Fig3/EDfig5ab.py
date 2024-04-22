import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import matplotlib.font_manager as fm
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import silhouette_score, silhouette_samples, calinski_harabaz_score




def vectorize(df):
    """
        Returns N x F Numpy Array representing F dimensions of ACME values
        of N Countries.

        Input: Pandas DataFrame

        Output: Numpy Array
    """

    X = df.values[:, 4:].astype(float)

    #Normalize Values
    X = (X - np.mean(X, axis=0)) / np.std(X, axis=0)

    return X




def clustering_test(df, savefig=True):
    prefs = df.columns[4:]
    X = vectorize(df)

    N = X.shape[0]

    calin_hara_indices = list()
    silhouette_indices = list()
    Ks = list(range(2,N))
    for k in Ks:

        # # #
        # Hierarchical / Agglomerative with Ward Linkage
        #
        agg_ward = AgglomerativeClustering(n_clusters=k, linkage='ward')
        C = agg_ward.fit_predict(X)

        calin_idx = calinski_harabaz_score(X, C)
        calin_hara_indices.append(calin_idx)

        sil_idx = silhouette_score(X, C)
        silhouette_indices.append(sil_idx)


        # # #
        # Hierarchical / Agglomerative with Complete Linkage
        #
        agg_comp = AgglomerativeClustering(n_clusters=k, linkage='complete')
        C = agg_comp.fit_predict(X)

        calin_idx = calinski_harabaz_score(X, C)
        calin_hara_indices.append(calin_idx)
        sil_idx = silhouette_score(X, C)
        silhouette_indices.append(sil_idx)


        # # #
        # Hierarchical / Agglomerative with Average Linkage
        #
        agg_avg = AgglomerativeClustering(n_clusters=k, linkage='average')
        C = agg_avg.fit_predict(X)

        calin_idx = calinski_harabaz_score(X, C)
        calin_hara_indices.append(calin_idx)

        sil_idx = silhouette_score(X, C)
        silhouette_indices.append(sil_idx)


        # # #
        # KMeans
        #
        kmeans = KMeans(n_clusters=k)
        C = kmeans.fit_predict(X)

        calin_idx = calinski_harabaz_score(X, C)
        calin_hara_indices.append(calin_idx)
        sil_idx = silhouette_score(X, C)
        silhouette_indices.append(sil_idx)

    df = pd.DataFrame({
        "K": [k for k in Ks for _ in ['Ward', 'Complete', 'Average', 'Kmeans']],
        "Method": ['Ward', 'Complete', 'Average', 'Kmeans'] * len(Ks),
        "Calinski-Harabasz": calin_hara_indices,
        "Silhouette": silhouette_indices})
    df = df[["K", "Method", "Calinski-Harabasz", "Silhouette"]]

    ticks_font_prop = fm.FontProperties(fname='fonts/RobotoCondensed-Regular.ttf', size=28)
    label_font_prop = fm.FontProperties(fname='fonts/RobotoCondensed-Regular.ttf', size=36)

    plt.figure(figsize=(16,10))
    for method in ['Ward', 'Complete', 'Average', 'Kmeans']:
        method_df = df[df['Method'] == method]['Calinski-Harabasz']
        plt.plot(method_df.values, label=method, linewidth=8)
        plt.xticks(range(0,130,10), fontproperties=ticks_font_prop)
        plt.yticks(fontproperties=ticks_font_prop)
        plt.xlabel("Number of Clusters (K)", fontproperties=label_font_prop)
        plt.xlim(-1,len(Ks))
    plt.legend(prop=ticks_font_prop)
    plt.tight_layout()
    if savefig:
        plt.savefig('image/calinski-harabasz.pdf', format='pdf')
    plt.show()

    plt.figure(figsize=(16,10))
    for method in ['Ward', 'Complete', 'Average', 'Kmeans']:
        method_df = df[df['Method'] == method]['Silhouette']
        plt.plot(method_df.values, label=method, linewidth=8)
        plt.xticks(range(0,N,10), fontproperties=ticks_font_prop)
        plt.yticks(fontproperties=ticks_font_prop)
        plt.xlabel("Number of Clusters (K)", fontproperties=label_font_prop)
        plt.xlim(-1,len(Ks))
    plt.legend(prop=ticks_font_prop)
    plt.tight_layout()
    if savefig:
        plt.savefig('image/silhouette.pdf', format='pdf')
    plt.show()

    return df


if __name__ == '__main__':
    df = pd.read_csv('data/CountryLevelAMCEVals.csv')
    clustering_test(df)
