import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster import hierarchy as hch

subtext = ["Preference for Inaction", "Sparing Pedestrians", "Sparing Females", "Sparing the Fit",
           "Sparing the Lawful", "Sparing Higher Status", "Sparing the Younger", "Sparing More",
           "Sparing Humans"]

prefs = ["Intervention", "Relation to AV", "Gender", "Fitness", "Law",
         "Social Status", "Age", "No. Characters", "Species"]

xlabels = list()
for i in range(len(subtext)):
    pref = prefs[i]
    xlabel = '' + pref + '\n'
    xlabel += "(" + subtext[i] + ")"
    xlabels.append(xlabel)


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


def create_d3_dendogram(df, leaf_color=None, save_csv=True):
    """
        Returns schema for D3 Radial Dendrogram Plot
    """
    prefs = df.columns[4:]
    X = vectorize(df)
    Z = hch.linkage(X, method='ward')

    rootnode, node_list = hch.to_tree(Z, rd=True)
    N = len(node_list) - 1

    geneology = dict()
    node_hierarchy = list()
    node_culture = list()
    node_continent = list()
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
            row = df.iloc[node.id]
            culture = row["Culture"]
            continent = row["Continent"]
            node_hierarchy.append([hierarchy, culture, continent])
        else:
            node_hierarchy.append([hierarchy, None, None])

    d3_dendo_tree_df = pd.DataFrame(node_hierarchy)
    d3_dendo_tree_df.columns = ["id", "culture", "continent"]

    if save_csv:
        if leaf_color:
            d3_dendo_tree_df.to_csv('data/dendrogram_{}.csv'.format(leaf_color))
        else:
            d3_dendo_tree_df.to_csv('dendrogram.csv')

    return d3_dendo_tree_df


def radar_plot(df, savefig=True):
    prefs = df.columns[4:]
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

    grouping = np.array(grouping)
    grouped_X = list()
    for g in range(3):
        grouped_X.append(X[::-1][grouping == g])

    cluster1_means = grouped_X[0].mean(axis=0)  # Cluster 1
    cluster2_means = grouped_X[1].mean(axis=0)  # Cluster 2
    cluster3_means = grouped_X[2].mean(axis=0)  # Cluster 3

    N = len(cluster1_means)
    x_as = [n / float(N) * 2 * np.pi for n in range(N)]

    cluster1_means = np.append(cluster1_means, cluster1_means[:1])
    cluster2_means = np.append(cluster2_means, cluster2_means[:1])
    cluster3_means = np.append(cluster3_means, cluster3_means[:1])

    x_as += x_as[:1]

    clusters = np.array([cluster1_means, cluster2_means, cluster3_means])
    min_val = clusters.min()
    clusters_adj = np.sqrt(np.square(clusters - min_val))
    ytick_labels = [np.sqrt(np.square(i - 1 - min_val)) - .3 for i in range(4)]

    colors = ["#CC6677", "#4477AA", "#DDCC77"]

    subtext = ["Preference \nfor Inaction", "Sparing \nPedestrians", "Sparing \nFemales", "Sparing \nthe Fit",
               "Sparing \nthe Lawful", "Sparing \nHigher Status", "Sparing \nthe Younger", "Sparing \nMore",
               "Sparing \nHumans"]

    font_prop = fm.FontProperties(fname='fonts/RobotoCondensed-Regular.ttf', size=20)
    font_axis_prop = fm.FontProperties(fname='fonts/RobotoCondensed-Regular.ttf', size=22)
    font_title_prop = fm.FontProperties(fname='fonts/RobotoCondensed-Regular.ttf', size=36)

    fig, axes = plt.subplots(1, 3, figsize=(22, 8), subplot_kw={'projection': 'polar'})
    fig.subplots_adjust(wspace=.3)

    for i, ax in enumerate(axes.ravel()):
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.plot(x_as, clusters_adj[i], linewidth=3, linestyle='solid', zorder=3, color=colors[i])
        ax.fill(x_as, clusters_adj[i], color=colors[i], alpha=0.4)
        ax.plot(np.linspace(0, 2 * np.pi, 1000), np.ones(1000) * -1 * min_val, color='black', linewidth=0.7)
        ax.set_xticks(x_as[:-1])
        ax.set_xticklabels([])
        ax.set_ylim(0, 3)
        ax.tick_params(axis='y', width=10, which='major')
        y_ticks = np.sqrt(np.square(np.arange(-1, 3, 1) - min_val))
        ax.set_yticks(y_ticks)
        ax.set_yticklabels([])
        for i in range(4):
            y = ytick_labels[i]
            if i > 0:
                ax.text(0.0, y, "z={}".format(i - 1), fontproperties=font_axis_prop)
                ax.text(x_as[0], 3.3, subtext[0], fontproperties=font_prop, rotation=0, horizontalalignment='center')
                ax.text(x_as[1], 3.65, subtext[1], fontproperties=font_prop, rotation=-40, horizontalalignment='center')
                ax.text(x_as[2], 3.5, subtext[2], fontproperties=font_prop, rotation=-80, horizontalalignment='center')
                ax.text(x_as[3], 3.5, subtext[3], fontproperties=font_prop, rotation=-120, horizontalalignment='center')
                ax.text(x_as[4], 3.55, subtext[4], fontproperties=font_prop, rotation=-160, horizontalalignment='center')
                ax.text(x_as[5], 3.5, subtext[5], fontproperties=font_prop, rotation=-200, horizontalalignment='center')
                ax.text(x_as[6] + 0.1, 3.5, subtext[6], fontproperties=font_prop, rotation=-240, horizontalalignment='center')
                ax.text(x_as[7], 3.55, subtext[7], fontproperties=font_prop, rotation=-280, horizontalalignment='center')
                ax.text(x_as[8], 3.55, subtext[8], fontproperties=font_prop, rotation=-320, horizontalalignment='center')
    if savefig:
        plt.savefig("image/radar_plot.pdf", format="pdf")


if __name__ == '__main__':
    df = pd.read_csv('data/CountryLevelAMCEVals.csv')
    create_d3_dendogram(df, leaf_color="Culture")
    radar_plot(df)
