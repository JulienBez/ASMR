import numpy as np
import matplotlib.pyplot as plt

from .utils import *

def getIdsLabelsAndScores(data_type):
    """"""

    ids = []
    scores = []
    labels = []

    for path in glob.glob(f"output/{data_type}/sorted/*.json"):
        data = openJson(path)
        
        for entry in data:

            ids.append(entry["metadata"]["id"])
            scores.append(max(entry["similarities"]["TOK"]))
            labels.append(entry["metadata"]["snowclone_label"])

    return ids,scores,labels
            

def getPrecision(true_positive,false_positive):
    ""
    return true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0


def getRecall(true_positive,false_negative):
    ""
    return true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0


def getF1Score(recall,precision):
    ""
    return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0


def getAccuracy(correct_labels,found_labels):
    ""
    return sum(i == j for i, j in zip(correct_labels, found_labels)) / len(correct_labels)


def getResults(data_type,threshold=0.5,printit=True,save_ids=True):
    """"""

    ids,scores,labels = getIdsLabelsAndScores(data_type)
    asmr_labels = []

    for i,_ in enumerate(ids):
        if scores[i] > threshold:
            asmr_labels.append(1)
        else:
            asmr_labels.append(0)

    true_positive = sum((c == 1 and f == 1) for c, f in zip(labels,asmr_labels))
    false_positive = sum((c == 0 and f == 1) for c, f in zip(labels,asmr_labels))
    false_negative = sum((c == 1 and f == 0) for c, f in zip(labels,asmr_labels))
    #true_negative = sum((c == 0 and f == 0) for c, f in zip(labels,asmr_labels))

    recall = getRecall(true_positive,false_negative)
    precision = getRecall(true_positive,false_positive)
    F1score = getF1Score(recall,precision)
    accuracy = getAccuracy(labels,asmr_labels)

    if printit:
        print(f"results obtained with threshold = {threshold}:")
        print(f" > recall: {recall}")
        print(f" > precision: {precision}")
        print(f" > F1 score: {F1score}")
        print(f" > accuracy: {accuracy}")

    return {"recall":recall,"precision":precision,"F1score":F1score,"accuracy":accuracy}


def plotResults(data_type,studied_layers,main_layer,ngram,analyzer,version):
    """"""

    createFolders(f"logs/{data_type}")

    thresholds = np.arange(0.99,-0.01,-0.01).tolist()

    all_recalls = []
    all_precisions = []
    all_f1scores = []
    all_accuracies = []

    for threshold in thresholds:
        
        results = getResults(data_type,threshold=threshold,printit=False)

        all_recalls.append(results["recall"])
        all_precisions.append(results["precision"])
        all_f1scores.append(results["F1score"])
        all_accuracies.append(results["accuracy"])

    plt.plot(thresholds, all_recalls, linestyle='-', color="royalblue", alpha=0.8, label="recall")
    plt.plot(thresholds, all_precisions, linestyle='-', color="limegreen", alpha=0.8, label="precision")
    plt.plot(thresholds, all_f1scores, linestyle='-', color="coral", alpha=0.8, label="F1 score")
    plt.plot(thresholds, all_accuracies, linestyle='-', color="gold", alpha=0.8, label="accuracy")

    plt.xlabel('Threshold')
    plt.ylabel('Metric score')

    plt.legend()
    #plt.xlim(thresholds[0],thresholds[-1])

    ngram_show = '-'.join([str(i) for i in ngram])

    plt.tight_layout()
    plt.savefig(f"logs/{data_type}/{'-'.join(studied_layers)}_{main_layer}_{ngram_show}_{analyzer}_{version}.png")
    plt.close()
