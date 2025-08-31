import subprocess

from .utils import *
from . import parameters

def getEvaluation(path,LANG=parameters.NAMEPATH,SEG=parameters.SEGMENT_VERSION):
    """"""
    filename = path.split("/")[-1].replace(".cupt",".txt")
    out_file = f"output/{LANG}/results/{parameters.TEST_DATA}_{SEG}/{filename}"
    with open(out_file, 'w') as f:
        subprocess.run(["python",
                        "src/evaluate.py",
                        "--train",
                        f"data/{LANG}/{parameters.TRAIN_DATA}.cupt",
                        "--gold",
                        f"data/{LANG}/{parameters.TEST_DATA}.cupt",
                        "--pred",
                        path,
                    ],stdout=f, stderr=subprocess.PIPE)


def readResFiles(path):
    """"""
    dict_res = {}
    with open(path,'r',encoding='utf-8') as f:
        res = [i.replace("\n","") for i in f.readlines()]
    for line in res:
        if "F=" in line:
            line = line.replace("* ","").replace(":","").split(" ")
            dict_res[line[0]] = {}
            for item in line[1:]:
                item_split = item.split("=")
                if item_split[0] in ["P","R","F"]:
                    dict_res[line[0]][item_split[0]] = float(item_split[-1])                
    return dict_res


def getAllEvaluations(LANG=parameters.NAMEPATH,SEG=parameters.SEGMENT_VERSION):
    """"""
    createFolders(f"output/{LANG}/results/{parameters.TEST_DATA}_{SEG}")
    for path in tqdm(glob.glob(f"output/{LANG}/labelled/{parameters.TEST_DATA}_{SEG}/*.cupt")):
        getEvaluation(path,LANG=LANG,SEG=SEG)


def compileResults(LANG=parameters.NAMEPATH,SEG=parameters.SEGMENT_VERSION):
    """"""
    dict_res = {}
    for path in tqdm(glob.glob(f"output/{LANG}/results/{parameters.TEST_DATA}_{SEG}/*.txt")):
        params = path.split("/")[-1].replace(".txt","")
        res = readResFiles(path)
        dict_res[params] = res
    writeJson(f"output/{LANG}/{parameters.TEST_DATA}_{SEG}_results.json",dict_res)
    