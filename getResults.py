from src.utils import *
from src.align import *
from src.segment import *
from src.measure import *
from src.evaluation import *

import numpy

print(f"model & recall & precision & F1 & accuracy \\\\")

def topN(data_type,version,n=10):
    "return top N results for datatype (train,dev,test)"
    res = openJson(f"output/results/{data_type}_sorted.json")[version]
    return [i for i in res[:n]]


def findTopN(data_type1,data_type2,version,n=10):
    "return top N results parameters from datatype1 for datatype2"
    res1 = topN(data_type1,version,n=n)
    res2 = openJson(f"output/results/{data_type2}.json")[version]
    return [[i[0],res2[i[0]]] for i in res1]


for version in ["exact","fuzzy","combined"]:

    n= len(openJson("output/results/train.json")[version])

    topNtrain = topN("train",version,n=n) #top 50 for train
    findtopNdev = sorted(findTopN("train","val",version,n=n), key=lambda x:x[1]["F1score"],reverse=True) #we check the results of the 50 best parameters sets for train on dev
    #a = ["_".join(i[0].split("_")[:4]) for i in topNtrain]

    #les auteurs de catchphrase ont fait 20 et 5 splits pour leurs expériences, on peut s'aligner avec eux et faire 20 splits à la fin :
    # - on prend les 10 meilleures runs de topNtrain et les 10 meilleures runs de findtopNdev
    param_set_test = [i[0] for i in topNtrain[:10] + findtopNdev[:10]]

    test = openJson("output/results/test_sorted.json")[version]
    res_test = sorted([i for i in test if i[0] in param_set_test], key=lambda x:x[1]["F1score"],reverse=True)

    for i in res_test:
        print(i)

    #en gros: 
    # - on récupère les 50 meilleures runs du train (topNtrain)
    # - on récupère les 50 runs avec les mêmes paramètres dans le dev (findtopNdev)
    # - on récupère les 10 meilleures runs du topNtrain et les 10 meilleures runs du findtopNdev
    # - on utilise ces 10 runs sur test et on regarde

    # on remarque que la couche POS ne revient pas souvent 
    # MAIS la couche top est utilisée lors de la segmentation donc elle est pas totalement mise de côté

    recall = numpy.mean([i[1]["recall"] for i in res_test])
    precision = numpy.mean([i[1]["precision"] for i in res_test])
    F1_score = numpy.mean([i[1]["F1score"] for i in res_test])
    accuracy = numpy.mean([i[1]["accuracy"] for i in res_test])

    sdt_dev_recall = numpy.std([i[1]["recall"] for i in res_test])
    sdt_dev_precision = numpy.std([i[1]["precision"] for i in res_test])
    sdt_dev_F1_score = numpy.std([i[1]["F1score"] for i in res_test])
    sdt_dev_accuracy = numpy.std([i[1]["accuracy"] for i in res_test])

    print(f"ASMR$_{version}$ & {round(recall,2)} $\pm$ {round(sdt_dev_recall,2)} & {round(precision,2)} $\pm$ {round(sdt_dev_precision,2)} & {round(F1_score,2)} $\pm$ {round(sdt_dev_F1_score,2)} & {round(accuracy,2)} $\pm$ {round(sdt_dev_accuracy,2)}\\\\".replace("0.","."))