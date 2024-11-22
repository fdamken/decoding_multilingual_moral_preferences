import re
import shutil
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path
from typing import Optional

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from countryinfo import CountryInfo
from scipy.cluster import hierarchy as hch

from model import get_available_models

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['hatch.linewidth'] = .5
# use TrueType fonts instead of Type 3 fonts
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

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
LEAF_ORDERING = {
    "gemini-1.0-pro-001": {
        "de": 0,
        "en": 0,
        "fr": 0,
        "pt": 0,
        "ru": 0,
        "ar": 2,
        "ja": 2,
        "ko": 2,
        "zh": 2,
        "es": 1,
    },
    "gpt-3.5-turbo-0125": {
        "de": 1,
        "en": 1,
        "fr": 1,
        "pt": 3,
        "ru": 3,
        "ar": 2,
        "ja": 2,
        "ko": 2,
        "zh": 2,
        "es": 0,
    },
    "Meta-Llama-3-8B-Instruct": {
        "de": 0,
        "en": 0,
        "fr": 0,
        "pt": 3,
        "ru": 3,
        "ar": 1,
        "ja": 1,
        "ko": 1,
        "zh": 1,
        "es": 2,
    },
}
RELEVANT_LANGUAGES = list(LANGUAGE_CLUSTERS.keys())
CLUSTER_COLORS = ["#1b9e77", "#d95f02", "#7570b3"]


def determine_precision(uncertainty: float) -> Optional[int]:
    if uncertainty == 0.0:
        return None
    uncertainty_integral, uncertainty_fraction = str(uncertainty).split(".")
    if uncertainty_integral == "0":
        precision_search_str = uncertainty_fraction
        integral_precision = False
    else:
        precision_search_str = "".join(reversed(uncertainty_integral))
        integral_precision = True
    precision_index = re.search("[1-9]", precision_search_str).start() + 1
    if integral_precision:
        return -precision_index + 1
    return precision_index


def round_to_precision(value: float, precision: Optional[int]) -> float:
    if precision is None:
        return value
    return round(value, precision)


def format_measurement_to_tuple(value: float, uncertainty: float) -> tuple[str, str]:
    precision = determine_precision(uncertainty)
    value = round_to_precision(value, precision)
    uncertainty = round_to_precision(uncertainty, precision)
    if precision is not None and precision > 0:
        return f"{value:.{precision}f}", f"{uncertainty:.{precision}f}"
    return str(value), str(uncertainty)


def format_measurement(value: float, uncertainty: float) -> str:
    return " \xb1 ".join(format_measurement_to_tuple(value, uncertainty))


def vectorize(df, df_se):
    X = df.values[:, 1:].astype(float)
    X_se = df_se.values[:, 1:].astype(float)
    sigma = np.std(X, axis=0)
    return X, X_se, (X - np.mean(X, axis=0)) / sigma, X_se / sigma


def _cluster(df, df_se, model_name):
    leaf_ordering = LEAF_ORDERING.get(model_name, LANGUAGE_CLUSTERS)
    # sort_key = lambda x: [leaf_ordering[language] for language in x]
    # df.sort_values("Country", inplace=True, key=sort_key)
    # df_se.sort_values("Country", inplace=True, key=sort_key)
    X_unnormalized, X_se_unnormalized, X, X_se = vectorize(df, df_se)
    Z = hch.linkage(X, method='ward')
    if model_name != "mme":
        labels = df["Country"].values
        fig, ax = plt.subplots(figsize=(1.68036, .5 * 1.68036))
        Z_optimal = hch.optimal_leaf_ordering(
            Z,
            np.arange(len(labels)).reshape((-1, 1)),
            metric=lambda a, b: abs(leaf_ordering[labels[int(a.item())]] - leaf_ordering[labels[int(b.item())]]),
        )
        result = hch.dendrogram(
            Z_optimal,
            link_color_func=lambda _: "black",
            leaf_label_func=lambda k: labels[k],
            ax=ax,
        )
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        boundaries = [xlim[0]] + ((ax.get_xticks()[1:] + ax.get_xticks()[:-1]) / 2).tolist() + [xlim[1]]
        for left, right, label in zip(boundaries[:-1], boundaries[1:], result["ivl"], strict=True):
            cluster = LANGUAGE_CLUSTERS[label]
            color = CLUSTER_COLORS[cluster]
            hatch = [r"\\" * 4, "-" * 7, "//" * 4][cluster]
            ax.add_patch(
                mpatches.Rectangle(
                    (left, ylim[0]),
                    right - left,
                    ylim[1] - ylim[0],
                    fill=False,
                    hatch=hatch,
                    color=color,
                    linestyle="",
                )
            )
        ax.set_yticks([])
        ax.tick_params(axis="both", labelsize=9)
        fig.tight_layout(pad=.1)
        fig.savefig(f"{model_name}/dendrogram.pdf")
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
    return X_unnormalized, X_se_unnormalized, X, X_se, grouping[::-1]  # grouping is reversed


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
        # Gaussian error propagation
        ses = np.sqrt((grouped_X_se[i] ** 2).sum(axis=0)) / grouped_X_se[i].shape[0]
        cluster_means.append(np.append(means, means[:1]))
        # to connect to the first point again
        cluster_ses.append(np.append(ses, ses[:1]))
    return np.array(cluster_means), np.array(cluster_ses)


def _compute_rmse(X, X_ref, X_se, X_ref_se):
    rmse = np.sqrt(np.mean((X - X_ref) ** 2))
    # Gaussian error propagation
    se = np.sqrt(((X - X_ref) ** 2 * (X_se ** 2 + X_ref_se ** 2)).sum()) / (rmse * X.size)
    return rmse, se


def _compute_mae(X, X_ref, X_se, X_ref_se):
    mae = np.mean(np.abs(X - X_ref))
    # Gaussian error propagation
    se = np.sqrt((X_se ** 2 + X_ref_se ** 2).sum()) / (mae * X.size)
    return mae, se


def _make_radar_plot(X, X_se, grouping, X_mme, X_mme_se, grouping_mme, model_name, normalized):
    clusters, clusters_se = _prepare_for_plotting(X, X_se, grouping)
    clusters_mme, clusters_mme_se = _prepare_for_plotting(X_mme, X_mme_se, grouping_mme)

    if not normalized and model_name != "mme":
        measurements = []
        for i in [0, 1, 2, ...]:
            measurements.append(
                format_measurement(*_compute_rmse(clusters[i], clusters_mme[i], clusters_se[i], clusters_mme_se[i]))
            )
        print("mme: " + " & ".join([model_name] + measurements))
    if not normalized:
        measurements = []
        for i in [0, 1, 2, ...]:
            measurements.append(
                format_measurement(
                    *_compute_mae(clusters[i], np.zeros_like(clusters[i]), clusters_se[i], np.zeros_like(clusters[i]))
                )
            )
        print("zero: " + " & ".join([model_name] + measurements))

    N = 9
    x_as = [n / float(N) * 2 * np.pi for n in range(N)]
    x_as += x_as[:1]

    labels = ["Western", "Eastern", "Southern"]
    subtext = ["inaction", "peds.", "     females", "fit", "lawful", "higher\nstatus", "young ", "more ", "humans  "]

    width = 3.4307
    # fig, axes = plt.subplots(
    #     1,
    #     3,
    #     figsize=(width / 2, width / 3.3 / 2),
    #     subplot_kw={'projection': 'polar'}
    # )
    # fig = plt.figure(figsize=(width, width))
    # gs = GridSpec(2, 2)
    # axes = [
    #     plt.subplot(gs[0, :], projection="polar"),
    #     plt.subplot(gs[1, 1], projection="polar"),
    #     plt.subplot(gs[1, 1], projection="polar"),
    # ]
    for i in range(3):
        fig, ax = plt.subplots(
            figsize=(.99 * width / 2, .97 * width / 2),
            subplot_kw={'projection': 'polar'}
        )
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.fill_between(
            x_as,
            clusters[i] - clusters_se[i],
            clusters[i] + clusters_se[i],
            color=CLUSTER_COLORS[i],
            zorder=5,
            alpha=.4,
            label="Confidence Interval",
        )
        ax.plot(x_as, clusters[i], linewidth=2, zorder=6, color=CLUSTER_COLORS[i], label="Cluster")
        if model_name != "mme":
            line, = ax.plot(x_as, clusters_mme[i], linewidth=2, zorder=4, color="black", alpha=.6, ls="dashed", label="MME")
            line.set_dashes([1, 2])
            line.set_dash_capstyle("round")
        ax.plot(np.linspace(0, 2 * np.pi, 1000), np.zeros(1000), color="black", linewidth=1, zorder=3, label="Zero")
        ymin, ymax = ax.get_ylim()
        # a bit counterintuitive, but the unnormalized values are in [-1, 1] while the normalized values can be larger
        ymin = np.floor(ymin) if normalized else -1
        ymax = np.ceil(ymax) if normalized else 1
        ax.set_ylim(ymin, ymax)
        ax.set_yticks(np.arange(ymin, ymax + 1., 1.))
        ax.set_yticklabels([])
        ax.set_xticks(x_as[:-1])
        ax.set_xticklabels(subtext)
        ax.set_title(labels[i])
        ax.tick_params(axis="both", labelsize=9)
        # ax.legend()
        fig.tight_layout(pad=.1)
        # fig.subplots_adjust(wspace=0.7)
        fig.savefig(f"{model_name}/radar_plot_{'zscore' if normalized else 'amce'}_{i}.pdf")
        # fig.show()
        plt.close(fig)


def radar_plot(model_name, df, df_se, df_mme, df_mme_se, normalize):
    X_unnormalized, X_se_unnormalized, X, X_se, grouping = _cluster(df, df_se, model_name)
    X_mme_unnormalized, X_mme_se_unnormalized, X_mme, X_mme_se, grouping_mme = _cluster(df_mme, df_mme_se, "mme")
    _make_radar_plot(
        X if normalize else X_unnormalized,
        X_se if normalize else X_se_unnormalized,
        grouping,
        X_mme if normalize else X_mme_unnormalized,
        X_mme_se if normalize else X_mme_se_unnormalized,
        grouping_mme,
        model_name,
        normalize,
    )


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
    radar_plot(model_name, df_estimates, df_se, df_mme_estimates, df_mme_se, True)
    radar_plot(model_name, df_estimates, df_se, df_mme_estimates, df_mme_se, False)


def main():
    df_mme_estimates, df_mme_se = _load_df("mme")
    # _run("falcon-7b-instruct", df_mme_estimates=df_mme_estimates, df_mme_se=df_mme_se)
    # quit()
    with ProcessPoolExecutor() as pool:
        pool.map(partial(_run, df_mme_estimates=df_mme_estimates, df_mme_se=df_mme_se), get_available_models() + ["mme"])


if __name__ == '__main__':
    main()
