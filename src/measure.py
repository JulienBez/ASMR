from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

import parameters
from .utils import *

def vectorizer(seed,sent):
    """vectorize in unigrams and bigrams the seed and the sent"""
    vectorizer = CountVectorizer(ngram_range=parameters.ngram_range,
                                 stop_words=parameters.stop_words,
                                 lowercase=parameters.lowercase,
                                 analyzer=parameters.analyzer
                                )
    return vectorizer.fit_transform([" ".join(seed)," ".join(sent)])


def distCosinus(X):
    """calculate cosine similarity score"""
    return cosine_similarity(X[1],X[0])[0].tolist()[0]


def meanLayers(data):
    """return mean of a single similarity score on each layer"""
    for entry in data:
        meanLayer = []
        for i in range(len(entry["alignments"])):
            total_layers = 0
            for layer in entry["similarities"].keys():
               total_layers = total_layers + entry["similarities"][layer][i]
            meanLayer.append(total_layers/len(entry["similarities"].keys()))
        entry["similarities"]["meanLayer"] = meanLayer
    return data


def fasterMeasure(data):
    """help run this script faster by not recalculating similarities measures of already seen common segments"""
    dicSimilarities = {} 
    for entry in data:
        for layer in entry["parsing"].keys():
            if layer not in dicSimilarities:
                dicSimilarities[layer] = {}
            for i,segment in enumerate(entry["commonSegments"][layer]):
                if " ".join(str(segment)) not in dicSimilarities[layer]:
                    seed = openJson("logs/seeds.json")[data[0]["paired_with"]["seed"]][layer]
                    sent = entry["commonSegments"][layer][i]
                    try:
                        X = vectorizer(seed,sent)
                        dicSimilarities[layer][" ".join(segment)] = distCosinus(X)
                    except:
                        dicSimilarities[layer][" ".join(segment)] = -1 #vectorization was not possible
    return dicSimilarities


def measure(path):
    """for each sent in a json file (path), get its similarity for each layer"""
    data = openJson(path)
    dicSimilarities = fasterMeasure(data)
    for entry in data:
        entry["similarities"] = {}
        for layer in entry["parsing"].keys():
            entry["similarities"][layer] = []
            for segment in entry["commonSegments"][layer]:
                entry["similarities"][layer].append(dicSimilarities[layer][" ".join(segment)])
    writeJson(path,meanLayers(data))


def measureAll():
    """process similarities function on every file in 'sorted/' folder"""
    for path in tqdm(glob.glob("output/sorted/*.json")):
        measure(path)
    print("")

