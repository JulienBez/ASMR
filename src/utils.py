import os
import json
import glob
import shutil

import pandas as pd
from tqdm import tqdm

def openJson(path):
    "open a json file"
    with open(path,'r',encoding='utf-8') as f:
        data = json.load(f)
    return data

  
def writeJson(path,data):
    "create a json file"
    with open(path,"w",encoding='utf-8') as f:
        json.dump(data,f,indent=4,ensure_ascii=False)


def createFolder(path):
    "create an empty folder"
    if not os.path.exists(path):
        os.mkdir(path)


def createFolders(path):
    "create several folders"
    if not os.path.exists(path):
        os.makedirs(path)


def deleteFolderContent(path):
    "delete everything in a given folder"
    if os.path.exists(path):
        shutil.rmtree(path)
        for p in glob.glob(path):
            if os.path.exists(p):
                shutil.rmtree(p)
                os.remove(p)

