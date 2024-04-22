import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.cluster import hierarchy as hch
from scipy.stats import pearsonr
from sklearn.decomposition import PCA


def vectorize(df):
    """
        Returns N x F Numpy Array representing F dimensions of ACME values
        of N Countries.

        Input: Pandas DataFrame

        Output: Numpy Array
    """

    X = df.values[:, 4:].astype(float)

    # Normalize Values
    X = (X - np.mean(X, axis=0)) / np.std(X, axis=0)

    return X


def pca_2D(df, savefig=True):
    prefs = df.columns[4:]
    country_labels = df["ISO3"].values

    X = vectorize(df)
    Z = hch.linkage(X, method='ward')

    rootnode, node_list = hch.to_tree(Z, rd=True)
    N = len(node_list) - 1

    geneology = dict()
    grouping = list()
    for node in node_list[::-1]:
        id_ = N - node.id
        if id_ == 0:
            geneology[id_] = str(id_)

        if id_ not in geneology:
            for node2 in node_list:
                if (node2.count != 1):
                    if (node.id == node2.left.id) or (node.id == node2.right.id):
                        id2 = N - node2.id
                        if node.dist == 0:
                            row = df.iloc[node.id]
                            country_name = row["Country"]
                            geneology[id_] = geneology[id2] + "." + country_name
                        else:
                            geneology[id_] = geneology[id2] + "." + str(id_)
                        break

        hierarchy = geneology[id_]
        if node.dist == 0:
            val = float(hierarchy[2:5])
            if val == 1.3:
                grouping.append(0)
            elif val == 1.5:
                grouping.append(1)
            elif val > 2.0:
                grouping.append(2)
            else:
                print(val)

    colors = ["#CC6677", "#4477AA", "#DDCC77"]

    patch1 = mpatches.Patch(color="#CC6677", alpha=0.8)
    patch2 = mpatches.Patch(color="#4477AA", alpha=0.8)
    patch3 = mpatches.Patch(color="#DDCC77", alpha=0.8)
    font_prop = fm.FontProperties(fname='fonts/RobotoCondensed-Regular.ttf', size=20)

    labels = ["Western",
              "Eastern",
              "Southern"]

    pca = PCA(n_components=2)
    X2 = pca.fit_transform(X)

    grouping = np.array(grouping)
    grouped_X = list()
    for g in np.unique(grouping):
        grouped_X.append(X2[::-1][grouping == g])

    x_min, x_max = np.min(X2), np.max(X2)

    text_font_prop = fm.FontProperties(
        fname='fonts/RobotoCondensed-Regular.ttf', size=8,
        weight='extra bold'
    )
    label_font_prop = fm.FontProperties(fname='fonts/RobotoCondensed-Regular.ttf', size=20)

    plt.figure(figsize=(12, 12))
    for j, X_c in enumerate(grouped_X):
        plt.scatter(X_c[:, 0], X_c[:, 1], marker='o', s=200, c=colors[j], label=labels[j])

    for i, label in enumerate(country_labels):
        plt.text(
            X2[i, 0] - 0.07, X2[i, 1] - 0.025, label,
            fontproperties=text_font_prop, color='white'
        )
    plt.xticks(fontproperties=label_font_prop)
    plt.yticks(fontproperties=label_font_prop)
    plt.xlim(x_min - 0.5, x_max + 0.5)
    plt.ylim(x_min - 0.5, x_max + 0.5)
    plt.xlabel("Component 1", fontproperties=label_font_prop)
    plt.ylabel("Component 2", fontproperties=label_font_prop)
    plt.legend(prop=label_font_prop, loc=4)
    if savefig:
        plt.savefig("image/pca.pdf", format="pdf", bbox_inches='tight')
    plt.show()


def distance_matrix(df, savefig=True):
    prefs = df.columns[4:]
    country_labels = df["ISO3"].values

    X = vectorize(df)
    Z = hch.linkage(X, method='ward')

    N = X.shape[0]
    distance_matrix = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            distance_matrix[i, j] = pearsonr(X[i, :], X[j, :])[0]

    distance_matrix -= np.eye(N)

    label_font_prop = fm.FontProperties(fname='fonts/RobotoCondensed-Regular.ttf', size=7)

    fig, ax = plt.subplots(1, 1, figsize=(16, 24))
    ax.grid(False)

    divider = make_axes_locatable(ax)
    dax1 = divider.append_axes("right", size="2%", pad=0.1)
    dax2 = divider.append_axes("left", size="15%", pad=0.0)
    dax3 = divider.append_axes("top", size="15%", pad=0.0)

    hch.set_link_color_palette(["#DDCC77", "#4477AA", "#CC6677"])
    dnd = hch.dendrogram(
        Z, ax=dax2, orientation="left",
        color_threshold=0.8 * np.max(Z[:, 2]),
        above_threshold_color='#CCCCCC'
    )
    hch.dendrogram(
        Z, ax=dax3, orientation="top",
        color_threshold=0.80 * np.max(Z[:, 2]),
        above_threshold_color='#808080'
    )

    idx = np.array(dnd["leaves"])[::-1]
    cax = ax.imshow(distance_matrix[idx][:, idx], cmap='PuOr')
    cbar = plt.colorbar(cax, cax=dax1)
    cbar.ax.tick_params(labelsize=12)
    ax.set_xticks([])
    ax.set_yticks([])
    dax1.set_xticks([])
    dax1.set_yticks([])
    dax1.set_frame_on(False)
    dax2.set_xticks([])
    dax2.set_yticks([])
    dax3.set_xticks([])
    dax3.set_yticks([])
    dax3.set_xlim(1250, 0)
    if savefig:
        plt.savefig("image/distance_matrix.pdf", format="pdf", bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    df = pd.read_csv('data/CountryLevelAMCEVals.csv')
    pca_2D(df)
    distance_matrix(df)
