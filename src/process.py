from sklearn.metrics.pairwise import cosine_similarity

from . import parameters
from .utils import *

def getDistances():
    """for each seed, find the closest sentences to this seed (a.k.a remove the furthest ones)"""

    ids = []
    sentences = []

    for path in glob.glob(f"data/{parameters.NAMEPATH}/*.json"):
        data = openJson(path)

        for i in data:
            sentences.append(i["sent"])
            ids.append(i["metadata"]["id"])

    dict_seq = {}
    vectorizer = parameters.vectorizer
    
    sequences = list(openJson(f"data/{parameters.NAMEPATH}.json").keys())
    
    for seq in tqdm(sequences):
        vectorizer.fit([seq] + sentences)

        sequence_vectors = vectorizer.transform([seq])
        sentence_vectors = vectorizer.transform(sentences)

        cosine_sim = cosine_similarity(sentence_vectors, sequence_vectors)
        dict_seq[seq] = {}

        for i,_ in enumerate(sentences):
            similarity_score = cosine_sim[i][0]
            dict_seq[seq][ids[i]] = {"seed":seq,"distance":1-similarity_score}

    return dict_seq


def sortByDistances():
    """for each sentence, sort it in each seed that it is close to"""

    dict_seq = getDistances()

    for seq,sent in dict_seq.items():
        new_data = [] 

        for path in glob.glob(f"data/{parameters.NAMEPATH}/*.json"):
            data = openJson(path)

            for i in range(len(data)):
                identifier = data[i]["metadata"]["id"]

                if sent[identifier]["distance"] < 0.9:
                    data[i]["paired_with"]["seed"] = sent[identifier]["seed"]
                    data[i]["paired_with"]["distance"] = sent[identifier]["distance"]

                    new_data.append(data[i])

        if len(new_data) > 0:
            writeJson(f"output/{parameters.NAMEPATH}/sorted/{''.join(x for x in seq.replace(' ','_') if x.isalnum() or x == '_')}.json",new_data)


def process():
    """process process on every file in 'data/' folder"""
    createFolders(f"output/{parameters.NAMEPATH}/sorted")
    sortByDistances()
    print("")
