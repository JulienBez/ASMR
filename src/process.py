from sklearn.metrics.pairwise import cosine_similarity

from . import parameters
from .utils import *

def sortByDistances(similarity_threshold = 0.9):
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
    
    for seq in sequences:
        vectorizer.fit([seq] + sentences)

        sequence_vectors = vectorizer.transform([seq])
        sentence_vectors = vectorizer.transform(sentences)

        cosine_sim = cosine_similarity(sentence_vectors, sequence_vectors)
        dict_seq[seq] = {}

        for i,_ in enumerate(sentences):
            similarity_score = cosine_sim[i][0]
            if similarity_score > similarity_threshold:
                dict_seq[seq][ids[i]] = {"seed":seq,"distance":1-similarity_score}

    return dict_seq


def sortByCommons(common_elements = 3):
    """sometime, the sortByDistances feature is not good enough, filtering out too much stuff. This is an alternative"""

    ids = []
    sentences = []

    for path in glob.glob(f"data/{parameters.NAMEPATH}/*.json"):
        data = openJson(path)

        for i in data:
            sentences.append(i["parsing"]["lemma"])
            ids.append(i["metadata"]["id"])

    sequences = list(openJson(f"data/{parameters.NAMEPATH}.json").keys())
    dict_seq = {}

    for seq in sequences:

        dict_seq[seq] = {}
        seq_set = set(seq.split(" "))

        commonElems = min([common_elements,len(seq_set)])

        for i,_ in enumerate(sentences):
            if len(seq_set & set(sentences[i])) >= commonElems:
                dict_seq[seq][ids[i]] = {"seed":seq,"distance":-1} #-1 indicates that we use sortByCommonElements
    
    return dict_seq


def sortBySeeds():
    """for each sentence, sort it in each seed that it is close to"""

    if parameters.processType == "sortByDistances":
        dict_seq = sortByDistances()
    elif parameters.processType == "sortByCommons":
        dict_seq = sortByCommons()
    else:
        print("process.py : processType does not match any know process type, aborting...")

    for seq,sent in tqdm(dict_seq.items()):
        new_data = [] 

        for path in glob.glob(f"data/{parameters.NAMEPATH}/*.json"):
            data = openJson(path)

            for i in range(len(data)):

                identifier = data[i]["metadata"]["id"]
                try:
                    data[i]["paired_with"] = {"seed":sent[identifier]["seed"],"distance":sent[identifier]["distance"]}
                    new_data.append(data[i])
                except:
                    continue

                for key,values in data[i]["parsing"].items():
                    data[i]["parsing"][key] = [v if v != "-" else "ASMR_SEP" for v in values] #MIGHT CAUSE ISSUES

        if len(new_data) > 0:
            writeJson(f"output/{parameters.NAMEPATH}/sorted/{''.join(x for x in seq.replace(' ','_') if x.isalnum() or x == '_')}.json",new_data)


def process():
    """process process on every file in 'data/' folder"""
    createFolders(f"output/{parameters.NAMEPATH}/sorted")
    if len(glob.glob(f"output/{parameters.NAMEPATH}/sorted")) == 0:
        sortBySeeds()
    print("")
