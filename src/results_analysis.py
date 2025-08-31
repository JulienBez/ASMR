import matplotlib.pyplot as plt
import numpy

from . import parameters
from .utils import *

def sortResults(language,segment,category,measure,n):
    """"""
    res_dev = openJson(f"output/{language}/dev_{segment}_results.json")
    res = [i for i in sorted(res_dev,key=lambda x:res_dev[x][category][measure],reverse=True) if i != "ruleBased"][:n]
    writeJson(f"output/{language}/dev_{segment}_best_runs.json",res)
    return res


def prettyNum(num):
    """"""
    num = str(num)
    if len(num) < 4:
        num = f"{num}0"
    if len(num) >= 5:
        num = num[:4]
    return num


def getResults(language,category):
    """"""

    all_recall = {}
    all_precision = {}
    all_F1 = {}

    max_recall = [0,""]
    max_precision = [0,""]
    max_F1 = [0,""]

    mean = []

    for segment in ["exact","fuzzy","combined"]:
        res_test = [[k,v] for k,v in openJson(f"output/{language}/test_{segment}_results.json").items() if k != 'ruleBased']

        recall = numpy.mean([i[1][category]["R"] for i in res_test])
        precision = numpy.mean([i[1][category]["P"] for i in res_test])
        F1_score = numpy.mean([i[1][category]["F"] for i in res_test])
        mean = mean + [recall,precision,F1_score]

        sdt_dev_recall = numpy.std([i[1][category]["R"] for i in res_test])
        sdt_dev_precision = numpy.std([i[1][category]["P"] for i in res_test])
        sdt_dev_F1_score = numpy.std([i[1][category]["F"] for i in res_test])

        if recall > max_recall[0]:
            max_recall = [recall,segment]
        
        if precision > max_precision[0]:
            max_precision = [precision,segment]

        if F1_score > max_F1[0]:
            max_F1 = [F1_score,segment]

        #table = table + [f"{round(recall,2)} $\pm$ {round(sdt_dev_recall,2)}", f"{round(precision,2)} $\pm$ {round(sdt_dev_precision,2)}", f"{round(F1_score,2)} $\pm$ {round(sdt_dev_F1_score,2)}"]   
        all_recall[segment] = f"{prettyNum(round(recall,3)*100)}$\pm${prettyNum(round(sdt_dev_recall,2)).replace('0.','.')}"
        all_precision[segment] = f"{prettyNum(round(precision,3)*100)}$\pm${prettyNum(round(sdt_dev_precision,2)).replace('0.','.')}"
        all_F1[segment] = f"{prettyNum(round(F1_score,3)*100)}$\pm${prettyNum(round(sdt_dev_F1_score,2)).replace('0.','.')}"

    table = [language]
    for segment in ["exact","fuzzy","combined"]:
        if segment == max_recall[1]:
            all_recall[segment] = f"\\textbf{{{all_recall[segment]}}}"
        if segment == max_precision[1]:
            all_precision[segment] = f"\\textbf{{{all_precision[segment]}}}"
        if segment == max_F1[1]:
            all_F1[segment] = f"\\textbf{{{all_F1[segment]}}}"
        table = table + [all_recall[segment],all_precision[segment],all_F1[segment]]

    return table,mean


def getTable(category="Variant-of-train",measure="F",n=10):
    """"""

    all_mean = []
    table = ["Language & R & P & F & R & P & F & R & P & F \\\\","\\hline"]

    languages = set()
    for path in glob.glob("data/*.json"):
        lang = path.split("/")[-1].replace(".json","")
        languages.add(lang)

    for language in sorted(list(languages)):
        t,mean = getResults(language,category)
        line = " & ".join(t) + " \\\\"
        table.append(line)
        all_mean.append(mean)

    final_mean = ["Mean"]
    for i,item in enumerate(all_mean[0]):
        m = numpy.mean([all_mean[j][i] for j in range(len(all_mean))])
        final_mean.append(str(round(m,3)*100))

    final_mean = " & ".join(final_mean).replace("0.",".") + " \\\\"
    table.append("\\hline")
    table.append(final_mean)
    writeFile("logs/table_res.tex","\n".join(table))


def allMeans(segment):
    """"""

    studied_cat = ["Tok-based",
                   "Continuous",
                   "Discontinuous",
                   "Seen-in-train",
                   "Unseen-in-train",
                   "Variant-of-train",
                   "Identical-to-train"
                ]

    languages = set()
    for path in glob.glob("data/*.json"):
        lang = path.split("/")[-1].replace(".json","")
        languages.add(lang)

    dict_m = {}
    for language in sorted(list(languages)):
        dict_m[language] = {}
        res_test = [[k,v] for k,v in openJson(f"output/{language}/test_{segment}_results.json").items() if k != 'ruleBased']
        for cat in studied_cat:
            dict_m[language][cat] = numpy.mean([i[1][cat]["F"] for i in res_test])

    dict_m["Mean"] = {cat:numpy.mean([i[cat] for j,i in dict_m.items()]) for cat in studied_cat}

    table = [[""] + studied_cat]
    for lang,res in dict_m.items():
        table.append([lang] + [prettyNum(round(res[cat],3)*100) for cat in studied_cat])

    lines = []
    for line in table:
        lines.append(" & ".join(line) + " \\\\ ")

    writeFile("logs/categories_res.tex","\n".join(lines))

