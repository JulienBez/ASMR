from sklearn.metrics import pairwise_kernels
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-xlm-r-multilingual-v1')

from . import parameters
from .utils import *

def vectorizer(V,seed,sents,metric="cosine"):
    """vectorize in unigrams and bigrams the seed and the sent"""
    X = V.fit_transform([" ".join(sent) for sent in sents]) #to ensure there odds items don't ruin the process
    Y = V.transform([" ".join(seed)])
    return pairwise_kernels(Y,X,metric=metric)[0]


def embeddings(seed,sents,metric="cosine"):
    """vectorize in unigrams and bigrams the seed and the sent"""
    X = model.encode([" ".join(sent) for sent in sents], batch_size=32, show_progress_bar=False)
    Y = model.encode([" ".join(seed)])
    return pairwise_kernels(Y,X,metric=metric)[0]


def meanLayers(data,ponderWithLength=True,LANG=parameters.NAMEPATH):
    """return mean of a single similarity score on each layer"""
    seed = openJson(f"data/{LANG}.json")[data[0]["paired_with"]["seed"]]
    for entry in data:
        meanLayer = []
        for i in range(len(entry["alignments"])):
            total_layers = 0
            nb_layers = 0
            for layer in parameters.layers.keys():
               if ponderWithLength and layer != "SEM":
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
            try:
                sents.append(data[i]["commonSegments"][layer][j])
            except:
                sents.append(data[i]["commonSegments"][parameters.TOK_layer][j])
            data[i]["similarities"][layer].append(0)
    return ids,sents


def measure(path,LANG=parameters.NAMEPATH):
    """get similarity of all entries with the seed for a file for each layer"""
    data = openJson(path)
    seed = openJson(f"data/{LANG}.json")[data[0]["paired_with"]["seed"]]
    for layer in parameters.layers.keys():
        sents_ids,sents = handleMultiplesAlignments(data,layer)
        try:
            if layer == parameters.POS_layer:
                V = parameters.POS_vectorizer #vectorizer with words, aka pos tags
                pairwise_sim = vectorizer(V,seed[layer],sents)
            if layer == parameters.SEM_layer:
                pairwise_sim = embeddings(seed[parameters.LEM_layer],sents)
            else:
                V = parameters.vectorizer
                pairwise_sim = vectorizer(V,seed[layer],sents)
            for i,ids in enumerate(sents_ids):
                data[ids["entry"]]["similarities"][layer][ids["alignment"]] = float(pairwise_sim[i])
        except:
            for ids in sents_ids:
                data[ids["entry"]]["similarities"][layer][ids["alignment"]] = -1 #if error with vectorizer
    writeJson(path,meanLayers(data,LANG=LANG))


def measureAll(LANG=parameters.NAMEPATH):
    """process similarities function on every file in 'sorted/' folder"""
    for path in tqdm(glob.glob(f"output/{LANG}/sorted/*.json")):
        measure(path,LANG=LANG)
    print("")
