from . import parameters
from .utils import *


def statsTable():
    """"""
    total_cand = 0
    table = []
    for path in glob.glob(f"output/{parameters.NAMEPATH}/sorted/*.json"):
        data = openJson(path)
        tokens = 0
        sup_5 = 0
        sup_9 = 0
        for entry in data:
            tokens += len(entry["parsing"]["TOK"])
            maxi = max(entry["similarities"]["meanLayer"])
            if maxi > 0.5 and maxi <= 0.9:
                sup_5 += 1
                total_cand += 1
            elif maxi > 0.9:
                sup_9 += 1
                total_cand += 1
        tab = [data[0]["paired_with"]["seed"],len(data),tokens,sup_5,sup_9]
        table.append(tab)
    table = sorted(table,reverse=True,key=lambda x: x[1])
    for i in range(len(table)):
        table[i] = [str(j) for j in table[i]]
    table = [" & ".join(["MWE","\\# tweets","\\# tokens","> 0.5","> 0.9 \\\\"])] + [" & ".join(t) + " \\\\" for t in table]
    createFolders(f"logs/{parameters.NAMEPATH}")
    writeFile(f"logs/{parameters.NAMEPATH}/table_stats.tex","\n".join(table))
    #print(total_cand)


def statsInput():
    """retrieve various stats for the corpus before ASMR run"""
    num_sentences = 0
    num_token = 0
    vocabulary = set()
    for path in glob.glob(f"data/{parameters.NAMEPATH}/*.json"):
        data = openJson(path)
        for entry in data:
            list_tok = entry["parsing"][parameters.main_layer]
            num_token += len(list_tok)
            num_sentences += 1
            vocabulary.update(list_tok)
    total_vocabulary = len(vocabulary)
    stats = {
        "total_tokens":num_token,
        "total_sentences":num_sentences,
        "total_vocabulary":total_vocabulary,
        "mean_token_per_sentence":num_token/num_sentences,
        "TTR":total_vocabulary/num_token
    }
    createFolders(f"logs/{parameters.NAMEPATH}")
    writeJson(f"logs/{parameters.NAMEPATH}/stats_input.json",sorted([[j,i] for i,j in stats.items()],reverse=True))


def statsOutput():
    """retrieve the number of candidates found with score > 0.5 for each seed after ASMR run"""
    stats = {"total":0,"total_uniques":0}
    for path in glob.glob(f"output/{parameters.NAMEPATH}/sorted/*.json"):
        data = openJson(path)
        seen = []
        nb = 0
        nb_uniques = 0
        for i in data:
            maxi = max([[j,i] for i,j in enumerate(i["similarities"]["meanLayer"])])
            if maxi[0] > 0.5:
                nb += 1
                if " ".join(i["commonSegments"][parameters.TOK_layer][maxi[1]]) not in seen:
                    nb_uniques += 1
                    seen.append(" ".join(i["commonSegments"][parameters.TOK_layer][maxi[1]]))
        stats[path] = [nb,nb_uniques]
        stats["total"] += nb
        stats["total_uniques"] += nb_uniques
    createFolders(f"logs/{parameters.NAMEPATH}")
    writeJson(f"logs/{parameters.NAMEPATH}/stats_output.json",sorted([[j,i] for i,j in stats.items()],reverse=True))


def metadata():
    """"""
    createFolders(f"logs/{parameters.NAMEPATH}/images")
    try:
        statsInput()
    except:
        debug("metadata.py : no file in data/NAMEPATH")
    try:
        statsOutput()
        statsTable()
    except:
        debug("metadata.py : no file in output/NAMEPATH/sorted")