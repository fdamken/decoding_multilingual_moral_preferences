import matplotlib
matplotlib.use('Agg')
import numpy as np
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import permutations
from scipy.cluster import hierarchy as hch

from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.patches as mpatches
from matplotlib.colors import rgb2hex
import matplotlib.font_manager as fm




font_prop = fm.FontProperties(fname='fonts/RobotoCondensed-Regular.ttf',
                              size=32)
label_font_prop = fm.FontProperties(fname='fonts/RobotoCondensed-Regular.ttf',
                              size=42)

prefs = ["Intervention", "Relation to AV", "Law", "Gender",
         "Fitness", "Social Status", "Age", "No. Characters", "Species"]


df = pd.read_csv("data/CountriesChangePr.csv")

df = df[df.columns[:10]]
df.columns = ["Country"] + prefs

countries = df["Country"].values
X = df.values[:,1:].astype(np.float)
X = (X - np.mean(X, axis=0))/np.std(X, axis=0)


countries_df = pd.read_csv("data/countryInfo.csv")
continents_df = countries_df[["Country",  "Continent"]]
continents_df["Continent"] = continents_df['Continent'].astype("category")
continents_df["Continent"] = continents_df["Continent"].cat.codes + 1
continents_df.index = countries_df["ISO3"]

cultural_df = pd.read_csv("data/cultures.csv")
cultural_df["categories"] = cultural_df["categories"].astype("category")
cultural_df["code"] = cultural_df["categories"].cat.codes + 1
cultural_df.index = cultural_df["countries"]
cultural_df = pd.merge(continents_df, cultural_df, left_index=True, right_index=True, how='right')
cultural_df = cultural_df[["Country", "categories", "code"]]
cultural_df.columns = ["Country", "Categories", "Code"]

cultural_group_dict = {
    4: 0,
    2: 0,
    8: 0,
    1: 0,
    7: 0,
    3: 1,
    9: 1,
    5: 1,
    6: 2,
    0: 2
}

cultural_df['Cluster'] = cultural_df['Code']#.apply(lambda x: cultural_group_dict[x])

cultural_dict = {
    5: "Islamic",
    7: "Orthodox",
    6: "Latin America",
    2: "Catholic",
    4: "English",
    8: "Protestant",
    3: "Confucian",
    1: "Baltic",
    9: "South Asia",
    0: "Other"
}

Z = hch.linkage(X, 'ward')
rootnode, node_list = hch.to_tree(Z, rd=True)

N = len(node_list) - 1
geneology = dict()
node_values = list()
for node in node_list[::-1]:
    id = N - node.id

    if id == 0:
        geneology[id] = str(id)

    if id not in geneology:
        # find ancestors
        for node2 in node_list:
            if (node2.count != 1):
                if (node.id == node2.left.id) or (node.id == node2.right.id):
                    id2 = N - node2.id
                    if node.dist == 0:
                        iso3 = countries[node.id]
                        geneology[id] = geneology[id2] + "." + iso3
                    else:
                        geneology[id] = geneology[id2] + '.' + str(id)
                    break

    if node.dist == 0:
        g = geneology[id][2:-4]
        iso3 = countries[node.id]
        try:
            cluster = cultural_df.ix[iso3]["Cluster"]
        except:
            cluster = None
        node_values.append((iso3, g, cluster))

iso3 = [node[0] for node in node_values]
values = [node[1] for node in node_values]
cluster_truth = [node[2] for node in node_values]

countries_sublist = list()
cluster_pred = list()
for i in range(len(values)):
    countries_sublist.append(iso3[i])

    # Cluster 0
    if values[i][:4] == '2.14':
        cluster_pred.append(9)

    # Cluster 1
    elif values[i][:3] == '2.9':
        cluster_pred.append(1)

    # Cluster 2
    elif values[i][:6] == '1.5.13':
        cluster_pred.append(2)

    # Cluster 3
    elif values[i][:6] == '1.5.11':
        cluster_pred.append(3)

    # Cluster 4
    elif values[i][:5] == '1.3.6':
        cluster_pred.append(4)

    # Cluster 5
    elif values[i][:8] == '1.3.4.10':
        cluster_pred.append(5)

    # Cluster 6
    elif values[i][:10] == '1.3.4.7.15':
        cluster_pred.append(6)

    # Cluster 7
    elif values[i][:13] == '1.3.4.7.12.28':
        cluster_pred.append(7)

    # Cluster 8
    elif values[i][:13] == '1.3.4.7.12.43':
        cluster_pred.append(8)

    else:
        print(values[i], iso3[i])
country_cluster_df = pd.DataFrame(dict(Country=countries_sublist,
                                        ClusterPred=cluster_pred,
                                        ClusterTruth=cluster_truth))
country_cluster_df = country_cluster_df[["Country", "ClusterPred", "ClusterTruth"]]
country_cluster_df = pd.merge(country_cluster_df, cultural_df.reset_index(), left_on="Country", right_on="countries")
country_cluster_df = country_cluster_df[["countries", "ClusterPred", "ClusterTruth"]]
country_cluster_df.dropna(inplace=True)
country_cluster_df['ClusterTruth'] = country_cluster_df['ClusterTruth'].astype(int)


def purity(df):
    denominator = len(df)
    numerators = list()
    for i in range(9):
        cluster_i_df = df[df['ClusterPred'] == i+1]
        vals = cluster_i_df.groupby('ClusterTruth').count()['countries'].values
        max_val = np.max(vals)
        numerators.append(max_val)
    return 1.0*np.sum(numerators)/denominator

def max_matching(df):
    denominator = len(df)
    numerators = np.zeros((9,9), dtype=int)

    for i in range(9):
        cluster_i_df = df[df['ClusterPred'] == i+1]
        for j in range(9):
            cluster_ij_df = cluster_i_df[cluster_i_df['ClusterTruth'] == j+1]
            numerators[i,j] = len(cluster_ij_df)

    max_val = 0
    for i_array in permutations(range(9)):
        i_array = np.array(i_array)
        val = np.diag(numerators[:, i_array]).sum()
        if max_val < val:
            max_val = val

    return 1.0*max_val / denominator

purity_measures = list()
max_matching_measures = list()
for i in range(1000):
    np.random.seed(i)
    n = len(country_cluster_df)
    vals = np.random.choice(9, size=n)
    vals = [z+1 for z in vals]
    fake_df = pd.DataFrame(dict(countries=country_cluster_df['countries'],
                                ClusterTruth=country_cluster_df['ClusterTruth'],
                                ClusterPred=vals))

    purity_measures.append(purity(fake_df))
    max_matching_measures.append(max_matching(fake_df))


plt.figure(figsize=(16,10))
plt.hist(purity_measures, bins=15, normed=True)
plt.axvline(purity(country_cluster_df), linestyle='--',
            color='r', label='purity={:.4f}'.format(purity(country_cluster_df)))
plt.legend(prop=label_font_prop, loc=1)
plt.xticks(fontproperties=font_prop)
plt.yticks(fontproperties=font_prop)
plt.tight_layout()
plt.savefig('image/purity.pdf', format='pdf',transparent=True)
#plt.show()

plt.figure(figsize=(16,10))
plt.hist(max_matching_measures, bins=15, normed=True)
plt.axvline(max_matching(country_cluster_df), linestyle='--',
            color='r', label='Max Matching={:.4f}'.format(max_matching(country_cluster_df)))
plt.legend(prop=label_font_prop, loc=1)
plt.xticks(fontproperties=font_prop)
plt.yticks(fontproperties=font_prop)
plt.tight_layout()
plt.savefig('image/max-matching.pdf', format='pdf',transparent=True)
#plt.show()
