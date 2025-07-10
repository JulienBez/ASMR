from sklearn.metrics import pairwise_kernels
from Levenshtein import ratio

from . import parameters
from .utils import *

def vectorizer(V,seed,sents,metric="cosine"):
    """vectorize in unigrams and bigrams the seed and the sent"""
    X = V.fit_transform([" ".join(sent) for sent in sents]) # to ensure there odds items don't ruin the process
    Y = V.transform([" ".join(seed)])
    return pairwise_kernels(Y,X,metric=metric)[0]


def meanLayers(data,ponderWithLength=True):
    """return mean of a single similarity score on each layer"""
    seed = openJson(f"data/{parameters.NAMEPATH}.json")[data[0]["paired_with"]["seed"]]
    for entry in data:
        meanLayer = []
        for i in range(len(entry["alignments"])):
            total_layers = 0
            nb_layers = 0
            for layer in parameters.layers.keys():
               if ponderWithLength:
                    size_difference = len(seed[layer])-len(entry["commonSegments"][layer][i])
                    if size_difference > 0:
                        entry["similarities"][layer][i] = (entry["similarities"][layer][i]*(len(seed[layer])-size_difference))/len(seed[layer])
               total_layers += entry["similarities"][layer][i]
               nb_layers += 1
            meanLayer.append(total_layers/nb_layers)
        entry["similarities"]["meanLayer"] = meanLayer
    return data


def handleMultiplesAlignments(data,layer):
    """handle entries with multiple alignments"""
    ids = []
    sents = []
    for i in range(len(data)):
        if "similarities" not in data[i]:
            data[i]["similarities"] = {}
        data[i]["similarities"][layer] = []
        for j in range(len(data[i]["alignments"])):
            ids.append({"entry":i,"alignment":j})
            sents.append(data[i]["commonSegments"][layer][j])
            data[i]["similarities"][layer].append(0)
    return ids,sents


def measure(path):
    """get similarity of all entries with the seed for a file for each layer"""
    data = openJson(path)
    seed = openJson(f"data/{parameters.NAMEPATH}.json")[data[0]["paired_with"]["seed"]]
    for layer in parameters.layers.keys():
        sents_ids,sents = handleMultiplesAlignments(data,layer)
        try:
            V = parameters.vectorizer
            if layer == parameters.POS_layer:
                V = parameters.POS_vectorizer # vectorizer with words, aka pos tags
            pairwise_sim = vectorizer(V,seed[layer],sents)
            for i,ids in enumerate(sents_ids):
                data[ids["entry"]]["similarities"][layer][ids["alignment"]] = pairwise_sim[i]
        except:
            for ids in sents_ids:
                data[ids["entry"]]["similarities"][layer][ids["alignment"]] = -1 # if empty vocabulary
    writeJson(path,meanLayers(data))


def measureLEVEN(path):
    """small test we made replacing cosine similarity with levenshtein distance"""
    data = openJson(path)
    seed = openJson(f"data/{parameters.NAMEPATH}.json")[data[0]["paired_with"]["seed"]]
    for layer in parameters.layers.keys():
        sents_ids,sents = handleMultiplesAlignments(data,layer)
        pairwise_sim = []
        for s in sents:
            p = ratio(" ".join(seed[layer])," ".join(s))
            pairwise_sim.append(p)
        for i,ids in enumerate(sents_ids):
            data[ids["entry"]]["similarities"][layer][ids["alignment"]] = pairwise_sim[i]
    writeJson(path,meanLayers(data))


def measureAll():
    """process similarities function on every file in 'sorted/' folder"""
    for path in tqdm(glob.glob(f"output/{parameters.NAMEPATH}/sorted/*.json")):
        measure(path)
    print("")
