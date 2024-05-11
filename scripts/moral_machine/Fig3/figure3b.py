import shutil
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tikzplotlib
from countryinfo import CountryInfo
from scipy.cluster import hierarchy as hch

from model import get_available_models

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 10

WESTERN = 0
EASTERN = 1
SOUTHERN = 2
# when weighing by population, english becomes eastern, everything else stays the same
LANGUAGE_CLUSTERS = {
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
RELEVANT_LANGUAGES = list(LANGUAGE_CLUSTERS.keys())
CLUSTER_COLORS = ["#CC6677", "#4477AA", "#DDCC77"]


def vectorize(df, df_se):
    X = df.values[:, 1:].astype(float)
    X_se = df_se.values[:, 1:].astype(float)
    sigma = np.std(X, axis=0)
    return (X - np.mean(X, axis=0)) / sigma, X_se / sigma


def _cluster(df, df_se, model_name):
    X, X_se = vectorize(df, df_se)
    Z = hch.linkage(X, method='ward')
    if model_name != "mme":
        labels = df["Country"].values
        fig, ax = plt.subplots()
        result = hch.dendrogram(Z, labels=labels, link_color_func=lambda _: "black", ax=ax)
        xlim = ax.get_xlim()
        boundaries = [xlim[0]] + ((ax.get_xticks()[1:] + ax.get_xticks()[:-1]) / 2).tolist() + [xlim[1]]
        for left, right, label in zip(boundaries[:-1], boundaries[1:], result["ivl"], strict=True):
            # make sure alpha is in sync with radar plot
            ax.axvspan(left, right, color=CLUSTER_COLORS[LANGUAGE_CLUSTERS[label]], alpha=0.4)
        ax.set_yticks([])
        fig.tight_layout()
        tikzplotlib.clean_figure(fig)
        code = tikzplotlib.get_tikz_code(fig).replace(
            "xmajorticks=false,",
            "ymajorticks=false,\n"
            "xtick pos=bottom,\n"
            "typeset ticklabels with strut,"
        )
        with open(f"{model_name}/dendrogram.tikz", "w") as f:
            f.write(code)
        # fig.show()
        plt.close(fig)
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
                for language, cluster in LANGUAGE_CLUSTERS.items():
                    if hierarchy.endswith(language):
                        grouping.append(cluster)
                        break
                else:
                    assert False, f"no language found for {hierarchy=}"
    if model_name == "mme":
        language_to_countries = {language: [] for language in RELEVANT_LANGUAGES}
        country_names = CountryInfo().all()
        for country_name in country_names:
            country_info = CountryInfo(country_name)
            if country_info.iso(3) in country_to_cluster:
                try:
                    languages = country_info.languages()
                except KeyError:
                    languages = []
                for language in RELEVANT_LANGUAGES:
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
    return X, X_se, grouping[::-1]  # grouping is reversed


def _prepare_for_plotting(X, X_se, grouping):
    grouping = np.array(grouping)
    grouped_X = list()
    grouped_X_se = list()
    for g in range(3):
        grouped_X.append(X[grouping == g])
        grouped_X_se.append(X_se[grouping == g])
    cluster_means = []
    cluster_ses = []
    for i in range(3):
        means = grouped_X[i].mean(axis=0)
        ses = np.sqrt((grouped_X_se[i] ** 2).sum(axis=0)) / grouped_X_se[i].shape[0]
        cluster_means.append(np.append(means, means[:1]))
        # to connect to the first point again
        cluster_ses.append(np.append(ses, ses[:1]))
    return np.array(cluster_means), np.array(cluster_ses)


def _make_radar_plot(X, X_se, grouping, X_mme, X_mme_se, grouping_mme, model_name):
    clusters, clusters_se = _prepare_for_plotting(X, X_se, grouping)
    clusters_mme, clusters_mme_se = _prepare_for_plotting(X_mme, X_mme_se, grouping_mme)
    print(clusters_mme[1])

    N = 9
    x_as = [n / float(N) * 2 * np.pi for n in range(N)]
    x_as += x_as[:1]

    labels = ["Western",
              "Eastern",
              "Southern"]
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
        # make sure alpha is in sync with dendrogram
        ax.fill_between(
            x_as,
            clusters[i] - clusters_se[i],
            clusters[i] + clusters_se[i],
            color=CLUSTER_COLORS[i],
            zorder=5,
            alpha=0.4,
        )
        ax.plot(x_as, clusters[i], linewidth=2, zorder=6, color=CLUSTER_COLORS[i])
        if model_name != "mme":
            ax.plot(x_as, clusters_mme[i], linewidth=2, zorder=4, color="black", alpha=.6)
        ax.plot(np.linspace(0, 2 * np.pi, 1000), np.zeros(1000), color="black", linewidth=1, zorder=3)
        ymin, ymax = ax.get_ylim()
        ax.set_yticks(np.arange(np.floor(ymin), np.ceil(ymax) + 1., 1.))
        ax.set_yticklabels([])
        ax.set_xticks(x_as[:-1])
        ax.set_xticklabels(subtext, fontsize=20)
        ax.set_title(labels[i])
        ax.tick_params(axis="both", labelsize=9)
    fig.tight_layout()
    fig.savefig(f"{model_name}/radar_plot.pdf")
    fig.show()
    plt.close(fig)


def radar_plot(model_name, df, df_se, df_mme, df_mme_se):
    X, X_se, grouping = _cluster(df, df_se, model_name)
    X_mme, X_mme_se, grouping_mme = _cluster(df_mme, df_mme_se, "mme")
    _make_radar_plot(X, X_se, grouping, X_mme, X_mme_se, grouping_mme, model_name)


def _load_df(model_name):
    df_path = Path(__file__).parent.parent.parent.parent / "results" / "prepared_for_fig3" / f"{model_name}.csv"
    if not df_path.exists():
        return False
    df_loaded = pd.read_csv(df_path)
    df_estimates = pd.DataFrame()
    df_estimates["Country"] = df_loaded["Unnamed: 0"]
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
        df_estimates[column] = df_loaded[column]
    df_se = pd.DataFrame()
    df_se["Country"] = df_loaded["Unnamed: 0"]
    columns = [
        "[Omission -> Commission]: se",
        "[Passengers -> Pedestrians]: se",
        "Gender [Male -> Female]: se",
        "Fitness [Large -> Fit]: se",
        "Law [Illegal -> Legal]: se",
        "Social Status [Low -> High]: se",
        "Age [Elderly -> Young]: se",
        "No. Characters [Less -> More]: se",
        "Species [Pets -> Humans]: se",
    ]
    for column in columns:
        df_se[column] = df_loaded[column]
    return df_estimates, df_se


def _run(model_name, df_mme_estimates, df_mme_se):
    print(f"processing {model_name}")
    df = _load_df(model_name)
    if df is False:
        return
    df_estimates, df_se = df
    path = Path(model_name)
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(exist_ok=True, parents=True)
    radar_plot(model_name, df_estimates, df_se, df_mme_estimates, df_mme_se)


def main():
    df_mme_estimates, df_mme_se = _load_df("mme")
    with ProcessPoolExecutor() as pool:
        pool.map(partial(_run, df_mme_estimates=df_mme_estimates, df_mme_se=df_mme_se), get_available_models() + ["mme"])


if __name__ == '__main__':
    main()
