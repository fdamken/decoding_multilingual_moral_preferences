from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tikzplotlib
from countryinfo import CountryInfo
from scipy.cluster import hierarchy as hch

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 10

WESTERN = 0
EASTERN = 1
SOUTHERN = 2
# when weighing by population, english becomes eastern, everything else stays the same
_language_clusters = {
    "de": WESTERN,
    "en": WESTERN,
    "fr": WESTERN,
    "pt": WESTERN,
    "ru": WESTERN,
    "ar": EASTERN,
    "ja": EASTERN,
    "ko": EASTERN,
    "zh": EASTERN,
    "es": SOUTHERN,
}
relevant_languages = list(_language_clusters.keys())


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


def radar_plot(model_name, title, df, savefig=True):
    X = vectorize(df)
    Z = hch.linkage(X, method='ward')

    if model_name != "mme":
        labels = df["Country"].values
        hch.dendrogram(Z, labels=labels, link_color_func=lambda _: "black")
        plt.xticks(rotation=90)
        plt.yticks([])
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
    country_to_cluster = {}
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
            if model_name == "mme":
                val = float(hierarchy[2:5])
                if val == 1.3:
                    grouping.append(0)
                    country_to_cluster[hierarchy[-3:]] = 0
                elif val == 1.5:
                    grouping.append(1)
                    country_to_cluster[hierarchy[-3:]] = 1
                elif val > 2.0:
                    grouping.append(2)
                    country_to_cluster[hierarchy[-3:]] = 2
                else:
                    print(val)
            else:
                for language, cluster in _language_clusters.items():
                    if hierarchy.endswith(language):
                        grouping.append(cluster)
                        break
                else:
                    assert False, f"no language found for {hierarchy=}"

    if model_name == "mme":
        language_to_countries = {language: [] for language in relevant_languages}
        country_names = CountryInfo().all()
        for country_name in country_names:
            country_info = CountryInfo(country_name)
            if country_info.iso(3) in country_to_cluster:
                try:
                    languages = country_info.languages()
                except KeyError:
                    languages = []
                for language in relevant_languages:
                    if language in languages:
                        language_to_countries[language].append(
                            (country_info.name().capitalize(), country_info.iso(3), country_info.population())
                        )
        for language, countries in language_to_countries.items():
            country_counts = {
                "western": [],
                "eastern": [],
                "southern": [],
            }
            for country, iso3, population in countries:
                if iso3 in country_to_cluster:
                    match country_to_cluster[iso3]:
                        case 0:
                            country_counts["western"].append(country)
                        case 1:
                            country_counts["eastern"].append(country)
                        case 2:
                            country_counts["southern"].append(country)
                        case _:
                            assert False
            print(
                f"{language} & "
                f"{', '.join(sorted(country_counts['western']))} & "
                f"{', '.join(sorted(country_counts['eastern']))} & "
                f"{', '.join(sorted(country_counts['southern']))} & "
                f"{max(country_counts, key=lambda x: len(country_counts[x]))} \\\\"
            )

    labels = ["Western",
              "Eastern",
              "Southern"]

    grouping = np.array(grouping)
    grouped_X = list()
    for g in range(3):
        grouped_X.append(X[::-1][grouping == g])

    cluster1_means = grouped_X[0].mean(axis=0)
    cluster2_means = grouped_X[1].mean(axis=0)
    cluster3_means = grouped_X[2].mean(axis=0)

    N = len(cluster1_means)
    x_as = [n / float(N) * 2 * np.pi for n in range(N)]

    cluster1_means = np.append(cluster1_means, cluster1_means[:1])
    cluster2_means = np.append(cluster2_means, cluster2_means[:1])
    cluster3_means = np.append(cluster3_means, cluster3_means[:1])

    x_as += x_as[:1]

    clusters = np.array([cluster1_means, cluster2_means, cluster3_means])
    min_val = clusters.min()
    clusters_adj = np.sqrt(np.square(clusters - min_val))

    colors = ["black"] * 3

    subtext = ["inaction", "peds.", "     females", "fit", "lawful", "higher\nstatus", "young ", "more ", "humans  "]

    width = 7.00137
    fig, axes = plt.subplots(
        1,
        3,
        figsize=(width, width / 3),
        subplot_kw={'projection': 'polar'}
    )

    for i, ax in enumerate(axes.ravel()):
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.plot(x_as, clusters_adj[i], linewidth=3, linestyle='solid', zorder=3, color=colors[i])
        ax.fill(x_as, clusters_adj[i], color=colors[i], alpha=0.4)
        ax.plot(np.linspace(0, 2 * np.pi, 1000), np.ones(1000) * -1 * min_val, color='black', linewidth=0.7)
        ax.set_xticks(x_as[:-1])
        ax.set_xticklabels(subtext, fontsize=20)
        y_ticks = np.sqrt(np.square(np.arange(0, 3, 1) - min_val))
        ax.set_ylim(0, y_ticks.max())
        ax.set_yticks(y_ticks)
        ax.set_yticklabels([r"$z = 0$", r"$z = 1$", ""], fontsize=3)
        ax.set_title(labels[i])
        ax.tick_params(axis="both", labelsize=9)

    # fig.suptitle(title)
    fig.tight_layout()
    if savefig:
        fig.savefig("radar_plot.pdf")
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
        "mme": "Moral Machine Experiment",
        "mpt-7b-chat": "MPT 7B-Chat",
        "mpt-30b-chat": "MPT 30B-Chat",
    }
    model_name = "mpt-30b-chat"
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
    radar_plot(model_name, _model_map[model_name], df)
