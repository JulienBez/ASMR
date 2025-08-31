from sklearn.metrics import pairwise_kernels
from sklearn.feature_extraction.text import TfidfVectorizer
from Levenshtein import ratio

from .utils import *

def vectorizer(V,seed,sents,metric="cosine"):
    """vectorize in unigrams and bigrams the seed and the sent"""
    X = V.fit_transform([" ".join(sent) for sent in sents]) #to ensure there odds items don't ruin the process
    Y = V.transform([" ".join(seed)])
    return pairwise_kernels(Y,X,metric=metric)[0]


def meanLayers(data,studied_layers,data_type,ponderWithLength=True):
    """return mean of a single similarity score on each layer"""
    seed = openJson(f"output/{data_type}/seeds.json")[data[0]["paired_with"]["seed"]]
    for entry in data:
        meanLayer = []
        for i in range(len(entry["alignments"])):
            total_layers = 0
            nb_layers = 0
            for layer in studied_layers:
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


def measure(path,ngram,analyzer,studied_layers,data_type):
    """get similarity of all entries with the seed for a file for each layer"""
    data = openJson(path)
    seed = openJson(f"output/{data_type}/seeds.json")[data[0]["paired_with"]["seed"]]
    for layer in studied_layers:
        sents_ids,sents = handleMultiplesAlignments(data,layer)
        V = TfidfVectorizer(ngram_range=(ngram),encoding="utf-8",lowercase=True,stop_words=None,analyzer=analyzer)
        if layer == ["POS"]:
            V = TfidfVectorizer(ngram_range=(1,1),encoding="utf-8",lowercase=True,stop_words=None,analyzer="word")
        pairwise_sim = vectorizer(V,seed[layer],sents)
        for i,ids in enumerate(sents_ids):
            data[ids["entry"]]["similarities"][layer][ids["alignment"]] = pairwise_sim[i]
    writeJson(path,meanLayers(data,studied_layers,data_type))


def measureLEVEN(path,ngram,analyzer,studied_layers,data_type):
    """small test we made replacing cosine similarity with levenshtein distance"""
    data = openJson(path)
    seed = openJson(f"output/{data_type}/seeds.json")[data[0]["paired_with"]["seed"]]
    for layer in studied_layers:
        sents_ids,sents = handleMultiplesAlignments(data,layer)
        pairwise_sim = []
        for s in sents:
            p = ratio(" ".join(seed[layer])," ".join(s))
            pairwise_sim.append(p)
        for i,ids in enumerate(sents_ids):
            data[ids["entry"]]["similarities"][layer][ids["alignment"]] = pairwise_sim[i]
    writeJson(path,meanLayers(data,studied_layers,data_type))


def measureAll(ngram,analyzer,studied_layers,data_type):
    """process similarities function on every file in 'sorted/' folder"""
    for path in glob.glob(f"output/{data_type}/sorted/*.json"):
        measureLEVEN(path,ngram,analyzer,studied_layers,data_type)
