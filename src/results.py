###########################################################
#                                                         #
# results.py :                                            #
#                                                         #
#   - some results                                        #
#                                                         #
###########################################################

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer

from .utils import *

def getResults():
    """"""
    results = {}
    for path in glob.glob("output/sorted/*.json"):
        data = openJson(path)
        seed = data[0]["paired_with"]["seed"]
        if seed not in results:
            results[seed] = []
        for entry in data:
            maxScore = max(entry["similarities"]["meanLayer"])
            maxScoreIndex = entry["similarities"]["meanLayer"].index(maxScore)
            if maxScore >= 0.7:
                results[seed].append(" ".join(entry["commonSegments"]["TOK"][maxScoreIndex]))
    return {k:v for k,v in results.items() if len(v) > 0}


def clusterSegments():
    """"""

    results = getResults()
    segments = []
    clusters = []

    for k,v in results.items():
        for seg in v:
            segments.append(seg)
            clusters.append(k)

    vectorizer = TfidfVectorizer(ngram_range=(2,3),encoding='utf-8',lowercase=True,analyzer="char_wb")
    X = vectorizer.fit_transform(segments)

    reducer = PCA(n_components=2)  # For PCA
    X_reduced = reducer.fit_transform(X.toarray())

    df = pd.DataFrame(X_reduced, columns=['x', 'y'])
    df['cluster'] = clusters
    palette = sns.color_palette('colorblind', len(set(clusters)))

    jitter_strength = 0.01
    df['x_jittered'] = df['x'] + np.random.normal(0, jitter_strength, size=df.shape[0])
    df['y_jittered'] = df['y'] + np.random.normal(0, jitter_strength, size=df.shape[0])

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='x_jittered', y='y_jittered', hue='cluster', palette=palette, s=100, alpha=0.7, legend=False)

    plt.xlabel(' ')
    plt.ylabel(' ')
    plt.savefig("logs/images/clusterSegments.png")
    plt.close()


def plotScores():
    """"""

    ids = []
    scores = []

    for path in sorted(glob.glob("output/sorted/*.json")):
        data = openJson(path)
        for entry in data:
            ids.append(entry["metadata"]["id"])
            max_score = max(entry["similarities"]["meanLayer"])
            scores.append(max_score)

    bins = np.arange(0, 1.1, 0.1)
    plt.hist(scores, bins=bins, edgecolor='black')

    plt.xlabel('Scores')
    plt.ylabel('Number of segments')
    plt.savefig("logs/images/plotscores.png")
    plt.close()