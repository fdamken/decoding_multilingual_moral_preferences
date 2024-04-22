import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
from scipy.cluster import hierarchy as hch
import matplotlib.patches as mpatches


subtext = ["Preference for Inaction", "Sparing Pedestrians", "Sparing Females", "Sparing the Fit",
           "Sparing the Lawful", "Sparing Higher Status", "Sparing the Younger", "Sparing More",
           "Sparing Humans"]

prefs = ["Intervention", "Relation to AV", "Gender","Fitness", "Law",
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

    #Normalize Values
    X = (X - np.mean(X, axis=0)) / np.std(X, axis=0)

    return X


def joy_plot(df, savefig=True):
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
        grouped_X.append(X[::-1][grouping==g])

    fig, axes = plt.subplots(9,1, figsize=(8,14))
    for i, ax in enumerate(axes.ravel()):
        for j, x_c in enumerate(grouped_X):
            sns.kdeplot(x_c[:,i], shade=False, ax=ax, linewidth=2, alpha=1., color=colors[j])
            sns.kdeplot(x_c[:,i], shade=True, ax=ax, linewidth=2, alpha=0.15, color=colors[j])
        ax.set_ylabel(xlabels[i], rotation="horizontal",
                      horizontalalignment="right",
                      verticalalignment="center",
                      fontsize=20, fontproperties=font_prop)
        ax.set_yticks([])
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_xlim(-5,5)

        if i == 0:
            ax.legend([patch1, patch2, patch3], labels, prop=font_prop,
                      loc="upper center", bbox_to_anchor=(0.5, 1.6), ncol=3)
        if i == 8:
            ax.set_xlabel("Z-Score of Effect Sizes", fontsize=22, fontproperties=font_prop)
            ax.set_xticks(range(-4,6,2))
            ax.set_xticklabels(labels=range(-4,6,2),
                               fontproperties=font_prop)
            ax.tick_params(axis='x', which='major', pad=15)
        else:
            ax.set_xticks([])
    plt.tight_layout()

    if savefig:
        plt.savefig("image/joyplot.pdf", format="pdf", bbox_inches = 'tight')
    else:
        plt.show()


if __name__ == '__main__':

    df = pd.read_csv('data/CountryLevelAMCEVals.csv')
    joy_plot(df)
