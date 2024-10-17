import math
import itertools
import numpy as np

import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity

import arabic_reshaper
from bidi.algorithm import get_display

from . import parameters
from .utils import *

def silhouette(X, clusters):
    """returns the silhouette score of a cluster"""
    score = silhouette_score(X, clusters)
    print(f"Silhouette Score: {score}")
    return score


def plotScores(uniques=False):
    """plot the number of isolated segments for each decimal score between 0 and 1"""

    ids = []
    scores = []
    seen = set()

    for path in sorted(glob.glob(f"output/{parameters.NAMEPATH}/sorted/*.json")):
        data = openJson(path)
        for entry in data:

            max_score = max(entry["similarities"]["meanLayer"])
            maxScoreIndex = entry["similarities"]["meanLayer"].index(max_score)
            segment = " ".join(entry["commonSegments"]["TOK"][maxScoreIndex])
            
            if segment not in seen:
                ids.append(entry["metadata"]["id"])
                scores.append(max_score)

            if uniques: #if uniques, we don't take into account frequencies
                seen.add(segment)          

    bins = np.arange(0, 1.1, 0.1)
    fig, ax1 = plt.subplots()

    counts, edges, _ = ax1.hist(scores, bins=bins, edgecolor='black')
    ax1.set_xlabel('Scores')
    ax1.set_ylabel('Number of sequences')

    ax2 = ax1.twinx()
    cumulative_counts = np.cumsum(counts)
    ax2.plot(edges[:-1] + 0.05, cumulative_counts, color='red', marker='o', linestyle='-', linewidth=2) #cumulative Number of sequences found

    filename = f"logs/{parameters.NAMEPATH}/images/plotscores.png"
    if uniques:
        filename = filename.replace(".png","_uniques.png")

    plt.savefig(filename)
    plt.close()


def intraCluster(cluster):
    """calculate the intra-cluster score of a list"""
    try:
        vectorizer = parameters.vectorizer
        X = vectorizer.fit_transform(cluster)
        cosine_sim = cosine_similarity(X)
        total = list(itertools.chain(*cosine_sim))
        return (sum(total))/(len(total))
    except:
        return "NA" #if vectorization wasn't possible for some reason


def plotCoherenceProgression(studied_seeds):
    """for each seed, calculates the progression of its intra-cluster score the deeper in the ranking we go"""
    
    # GET DATA #
    results = {}
    for path in glob.glob(f"output/{parameters.NAMEPATH}/sorted/*.json"):
        data = openJson(path)
        seed = data[0]["paired_with"]["seed"]
        if seed not in results:
            results[seed] = {}
        for entry in data:
            maxScore = max(entry["similarities"]["meanLayer"])
            maxScoreIndex = entry["similarities"]["meanLayer"].index(maxScore)
            results[seed][" ".join(entry["commonSegments"]["TOK"][maxScoreIndex])] = maxScore

    # GET INTRA CLUSTER SCORES #
    thresholds = [1] + np.arange(0.99,-0.01,-0.01).tolist() #[1,0.99,0.98,...0.02,0.01,0]
    coherences_all = []
    seeds = []

    for seed,segments in results.items():
        coherences = []
        sequences_old = []
        coherence_old = "NA"

        for current in thresholds:

            sequences = []
            for seq, score in segments.items():
                if score >= current:
                    sequences.append(seq)

            if sequences != sequences_old:
                coherence = intraCluster(sequences)

            else:
                coherence = coherence_old

            coherences.append(coherence)
            sequences_old = sequences
            coherence_old = coherence

        coherences_all.append(coherences)
        seeds.append(seed)

    # FIGURE #
    plt.figure(figsize=(12, 4))
    
    colors = plt.colormaps['Dark2'].colors
    colors_count = 0

    #plot coherence progression for each sequence
    for i, scores in enumerate(coherences_all):
        thresh = [thresholds[i] for i in range(len(scores)) if scores[i] != "NA"]
        scores = [i for i in scores if i != "NA"]
        if seeds[i] in studied_seeds:
            plt.plot(thresh, scores, linestyle='--', color=colors[colors_count], alpha=0.8, label=get_display(arabic_reshaper.reshape(seeds[i])))
            colors_count += 1
        else:
            plt.plot(thresh, scores, linestyle='-', color="lightgray", alpha=0.4, label='_nolegend_')

    #plot mean coherence progression
    scores_merge = []
    for i in range(len(thresholds)):
        i_scores = []
        for cs in coherences_all:
            if cs[i] != "NA":
                i_scores.append(cs[i])
        if len(i_scores) == 0:
            scores_merge.append("NA")
        else:
            scores_merge.append(sum(i_scores)/len(i_scores))
    thresh_merge = [thresholds[i] for i in range(len(scores_merge)) if scores_merge[i] != "NA"]
    scores_merge = [i for i in scores_merge if i != "NA"]
    plt.plot(thresh_merge, scores_merge, linestyle='-', color="red", alpha=1)

    plt.xlabel('Threshold')
    plt.ylabel('Intra Cluster Score')

    plt.legend()
    plt.xlim(thresholds[0],thresholds[-1])
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    plt.tight_layout()
    plt.savefig(f"logs/{parameters.NAMEPATH}/images/plotCoherenceProgression.png")
    plt.close()


def clusterByThreshold(studied_seeds):
    """"""

    # FIGURE SIZE ESTIMATION #
    total = len(studied_seeds) 
    nlines = 3
    ncols = math.ceil(total/nlines) #round up to next integer
    if total < nlines:
        nlines = total + 1
        ncols = 1

    fig, axs = plt.subplots(ncols, nlines, figsize=(15, 5*ncols), sharex=True, sharey=True) #to have number of col and lines
    fig.tight_layout()

    for seed, ax in zip(studied_seeds,axs.ravel()):

        # GET DATA #
        filename = "".join(x for x in seed.replace(" ","_") if x.isalnum() or x == "_")
        data = openJson(f"output/{parameters.NAMEPATH}/sorted/{filename}.json")

        entries = []
        scores = []

        for entry in data:
            maxScore = max(entry["similarities"]["meanLayer"])
            maxScoreIndex = entry["similarities"]["meanLayer"].index(maxScore)
            entries.append(" ".join(entry["commonSegments"]["TOK"][maxScoreIndex]))
            scores.append(maxScore)

        # VECTORS #
        vectorizer = parameters.vectorizer
        X = vectorizer.fit_transform(entries + [seed])

        reducer = PCA(n_components=2)
        X_reduced = reducer.fit_transform(X.toarray())

        #jitter to allow to see overlapping points
        jitter_strength = 0.07
        X_jittered = X_reduced + np.random.normal(0, jitter_strength, X_reduced.shape)

        cmap = plt.get_cmap('coolwarm')
        colors = list(cmap(scores)) + ["black"]
        
        ax.scatter(X_jittered[:, 0], X_jittered[:, 1], c=colors, alpha=1, s=100)
        ax.set_title(f'{get_display(arabic_reshaper.reshape(seed))}')
        ax.grid(True)

    plt.savefig(f"logs/{parameters.NAMEPATH}/images/clusterByThreshold.png")
    plt.close()


def results():
    """"""
    createFolders(f"logs/{parameters.NAMEPATH}/images")
    #plotCoherenceProgression(["Travailler plus pour gagner plus","Que la force soit avec toi","c'est le deuxième effet Kisscool"])
    plotCoherenceProgression(["غضب غضبا شديد ","قلب الضيا بعينه ظلام ","فلما سمع فلان من فلان ذلك الكلام "])
    plotScores()
    plotScores(uniques=True)
    clusterByThreshold(["فز واثب على الاقدام ","بات ذلك الليله ","وعند فراغه من ذلك الكلام "])
    
    """
    unwanted = 'فلما سمع فلان من فلان ذلك الكلام '
    l = list(openJson(f"data/{parameters.NAMEPATH}.json").keys())
    print(l)
    print(len(l))
    l = [i for i in l if i == unwanted]
    print(len(l))
    clusterByThreshold(l)
    """

    #clusterByThreshold(list(openJson(f"data/{parameters.NAMEPATH}.json").keys()))
    #clusterByThreshold(["Travailler plus pour gagner plus","Que la force soit avec toi","c'est le deuxième effet Kisscool"])