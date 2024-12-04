import glob
import subprocess
import numpy as np
from src.utils import *

def checkDiscontiguities(commonSeg,allowedDiscontiguitiesSize):
    """"""
    if allowedDiscontiguitiesSize == -1:
        return True
    return all(num <= 3 for num in [commonSeg[i] - commonSeg[i - 1] for i in range(1, len(commonSeg))])


createFolders("runOnParseme")

languages = set()
for path in glob.glob("data/parseme_*.json"):
    languages.add(path.split("_")[-1].replace(".json",""))

discont_sizes = [0,1,2,3,4,-1]
thresholds = [1] + np.arange(0.9,0,-0.1).tolist()

for language in ["FR"]:#languages:

    # Initialization #

    createFolders(f"runOnParseme/{language}")
    print(f"Running on {language}...")

    # Modifying parameters #

    with open("src/parameters.py",'r',encoding='utf-8') as f:
        params = f.readlines()

    target = f"parseme_1-2_{language}"
    params[1] = f"NAMEPATH = \"{target}\"\n"

    with open('src/parameters.py','w',encoding='utf-8') as f:
        f.write("".join(params))

    # Running ASMR on target language #

    #subprocess.run(["python","main.py","-pasmr"])

    # Getting results for evaluation #

    for discont_size in discont_sizes:
        for threshold in thresholds:

            asmr_res = {}
            sent_mwes_counter = {}

            for path in glob.glob(f"output/{target}/sorted/*.json"):    
                data = openJson(path)

                for entry in data:
                    sent_id = entry["metadata"]["id"]

                    #old discont count, with discont lists as possible outputs
                    #discont_count = []
                    #for i, indexes in enumerate(entry["commonSegmentsIndexes"]):
                    #    discont_count.append ([all(num <= 3 for num in [indexes[i] - indexes[i - 1] for i in range(1, len(indexes))]),i]) #false si discont trop longue
                    #discont_match = [i[1] for i in discont_count if i[0] == True]
            
                    discont_match = [i for i,indexes in enumerate(entry["commonSegmentsIndexes"]) if checkDiscontiguities(indexes,discont_size)]
                    if len(discont_match) > 0:

                        max_res = max([entry["similarities"]["lemma"][i] for i in discont_match]) #problème peut-être quand on récupère la meilleure similarité
                        max_res_index = entry["similarities"]["lemma"].index(max_res)

                        if max_res > threshold:

                            if sent_id not in asmr_res:
                                asmr_res[sent_id] = ["*" for i in entry["parsing"]["form"]]
                                sent_mwes_counter[sent_id] = 0
                            sent_mwes_counter[sent_id] += 1
                            
                            for i in entry["commonSegmentsIndexes"][max_res_index]:
                                
                                if asmr_res[sent_id][i] == "*":
                                    asmr_res[sent_id][i] = str(sent_mwes_counter[sent_id])

                                else:
                                    asmr_res[sent_id][i] = f"{asmr_res[sent_id][i]};{str(sent_mwes_counter[sent_id])}"

            writeJson(f"runOnParseme/{language}/test_{discont_size}_Threshold_{threshold}.asmr",asmr_res)

