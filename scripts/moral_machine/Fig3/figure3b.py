from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tikzplotlib
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

    X = df.values[:, 1:].astype(float)

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


def radar_plot(title, df, savefig=True):
    X = vectorize(df)
    Z = hch.linkage(X, method='ward')

    language_map = {
        "ar": "Arabic",
        "de": "German",
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "ja": "Japanese",
        "kr": "Korean",
        "pt": "Portuguese",
        "ru": "Russian",
        "zh": "Chinese",
    }
    WESTERN = 0
    EASTERN = 1
    _language_clusters = {
        "ar": EASTERN,
        "de": WESTERN,
        "en": WESTERN,
        "es": WESTERN,
        "fr": WESTERN,
        "ja": EASTERN,
        "kr": EASTERN,
        "pt": WESTERN,
        "ru": EASTERN,
        "zh": EASTERN,
    }

    # noinspection PyTypeChecker
    hch.dendrogram(Z, labels=[language_map[l] for l in df["Country"].values])
    plt.xticks(rotation=90)
    plt.yticks([])
    plt.title(title)
    plt.tight_layout()
    tikzplotlib.clean_figure()
    code = tikzplotlib.get_tikz_code() \
        .replace("xmajorticks=false,", "ymajorticks=false,\nxtick pos=bottom,")
    with open("dendrogram.tikz", "w") as f:
        f.write(code)
    plt.show()

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
            for language, cluster in _language_clusters.items():
                if hierarchy.endswith(language):
                    grouping.append(cluster)
                    break
            else:
                assert False, f"no language found for {hierarchy=}"

    labels = ["Western",
              "Eastern"]

    grouping = np.array(grouping)
    grouped_X = list()
    for g in range(2):
        grouped_X.append(X[::-1][grouping == g])

    cluster1_means = grouped_X[0].mean(axis=0)
    cluster2_means = grouped_X[1].mean(axis=0)

    N = len(cluster1_means)
    x_as = [n / float(N) * 2 * np.pi for n in range(N)]

    cluster1_means = np.append(cluster1_means, cluster1_means[:1])
    cluster2_means = np.append(cluster2_means, cluster2_means[:1])

    x_as += x_as[:1]

    clusters = np.array([cluster1_means, cluster2_means])
    min_val = clusters.min()
    clusters_adj = np.sqrt(np.square(clusters - min_val))

    colors = ["#CC6677", "#4477AA", "#DDCC77"]

    subtext = ["preference \nfor inaction", "sparing \npedestrians", "sparing \nfemales", "sparing \nthe fit",
               "sparing \nthe lawful", "sparing \nhigher status", "sparing \nthe young", "sparing \nmore",
               "sparing \nhumans"]

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(7.00137, 7.00137 / 2),
        subplot_kw={'projection': 'polar'}
    )

    for i, ax in enumerate(axes.ravel()):
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.plot(x_as, clusters_adj[i], linewidth=3, linestyle='solid', zorder=3, color=colors[i])
        ax.fill(x_as, clusters_adj[i], color=colors[i], alpha=0.4)
        ax.plot(np.linspace(0, 2 * np.pi, 1000), np.ones(1000) * -1 * min_val, color='black', linewidth=0.7)
        ax.set_xticks(x_as[:-1])
        ax.set_xticklabels(subtext)
        ax.tick_params(axis='y', width=10, which='major')
        y_ticks = np.sqrt(np.square(np.arange(0, 3, 1) - min_val))
        ax.set_ylim(0, y_ticks.max())
        ax.set_yticks(y_ticks)
        ax.set_yticklabels([r"$z = 0$", r"$z = 1$", ""])
        ax.set_title(labels[i])

    fig.suptitle(title)
    fig.tight_layout()
    if savefig:
        fig.savefig("radar_plot.pgf")
    fig.show()


if __name__ == '__main__':
    _model_map = {
        "falcon-7b-instruct": "Falcon 7B-Instruct",
        "falcon-40b-instruct": "Falcon 40B-Instruct",
        "falcon-180B-chat": "Falcon 180B-Chat",
        "Llama-2-7b-chat-hf": "Llama 2 7B-Chat",
        "Llama-2-13b-chat-hf": "Llama 2 13B-Chat",
        "Llama-2-70b-chat-hf": "Llama 2 70B-Chat",
        "Meta-Llama-3-8B-Instruct": "Llama 3 8B-Instruct",
        "Meta-Llama-3-70B-Instruct": "Llama 3 70B-Instruct",
        "mpt-7b-chat": "MPT 7B-Chat",
        "mpt-30b-chat": "MPT 30B-Chat",
    }
    model_name = "Meta-Llama-3-70B-Instruct"
    file_path = Path(__file__).parent.parent.parent.parent / "results" / "prepared_for_fig3" / f"{model_name}.csv"
    df_loaded = pd.read_csv(file_path)
    df = pd.DataFrame()
    df["Country"] = df_loaded["Unnamed: 0"]
    columns = [
        "[Omission -> Commission]: Estimates",
        "[Passengers -> Pedestrians]: Estimates",
        "Gender [Male -> Female]: Estimates",
        "Fitness [Large -> Fit]: Estimates",
        "Law [Illegal -> Legal]: Estimates",
        "Social Status [Low -> High]: Estimates",
        "Age [Elderly -> Young]: Estimates",
        "No. Characters [Less -> More]: Estimates",
        "Species [Pets -> Humans]: Estimates",
    ]
    for column in columns:
        df[column] = df_loaded[column]
    # create_d3_dendogram(df, leaf_color="Culture")
    radar_plot(_model_map[model_name], df)
