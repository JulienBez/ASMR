
import glob
import numpy as np
from .utils import *
from .file_format_handler import *

def checkDiscontiguities(commonSeg,allowedDiscontiguitiesSize = 4):
    """maximum discontiguities size allowed before to remove a candidate from our set"""
    if allowedDiscontiguitiesSize == -1:
        return True
    return all(num <= 3 for num in [commonSeg[i] - commonSeg[i - 1] for i in range(1, len(commonSeg))])


def checkLemmas(commonSeg,entry,seeds):
    """return true if commonSeg lemmas are identical to those of the mwes we search for"""
    return sorted([entry["parsing"]["upos"][i] for i in commonSeg]) == sorted(seeds[entry["paired_with"]["seed"]]["upos"])


def checkPOStags(commonSeg,entry,seeds):
    """return true if commonSeg pos tags are identical to those of the mwes we search for"""
    return sorted([entry["parsing"]["lemma"][i] for i in commonSeg]) == sorted(seeds[entry["paired_with"]["seed"]]["lemma"])


def findLabels(condition_name,seeds,thres_tok,thres_lem,thres_pos,thres_sem,LANG=parameters.NAMEPATH):
    """given a condition, create label lists for each sentence in PARSEME json files"""

    asmr_res = {} #the final lists of labels
    sent_mwes_counter = {} #helps us attribute different numbers if multiple MWE seen in a sentence
    vues = {} #helps us avoid to tag multiple times the same MWE

    for path in glob.glob(f"output/{LANG}/sorted/*.json"):    
        data = openJson(path)
        for entry in data:
                
            sent_id = entry["sent"] + entry["metadata"]["id"] #ids are not fiables, there is two ids ". EL-33-51-test2018-05.cupt 8" in EL for instance
            sorted_scores = sorted([[indexes,i] for i,indexes in enumerate(entry["similarities"]["meanLayer"])],reverse=True) #we start by the elements with the best score
            is_condition_valid = False #to avoid taking into account too many elements

            for i in [x[1] for x in sorted_scores]:
                indexes = entry["commonSegmentsIndexes"][i]

                #depending of the condition, the criterions to be labelled as part of MWE change
                if condition_name == "threshold":
                    condition = checkDiscontiguities(indexes) and entry["similarities"]["form"][i] > thres_tok and entry["similarities"]["upos"][i] > thres_pos and entry["similarities"]["lemma"][i] > thres_lem# and entry["similarities"]["SEM"][i] > thres_sem
                elif condition_name == "ruleBased":
                    condition = checkDiscontiguities(indexes) and checkPOStags(indexes,entry,seeds) and checkLemmas(indexes,entry,seeds)
                #elif condition_name == "threshold_discontiguities":
                #    condition = checkDiscontiguities(indexes) and entry["similarities"]["form"][i] > thres_tok and entry["similarities"]["upos"][i] > thres_pos and entry["similarities"]["lemma"][i] > thres_lem and entry["similarities"]["SEM"][i] > thres_sem

                if condition and not is_condition_valid:#
 
                    if sent_id not in asmr_res:
                        asmr_res[sent_id] = ["*" for i in entry["parsing"]["form"]]
                        sent_mwes_counter[sent_id] = 0
                        vues[sent_id] = []
                    sent_mwes_counter[sent_id] += 1
   
                    if all(isinstance(x, list) for x in entry["commonSegmentsIndexes"]):
                        if sorted(entry["commonSegmentsIndexes"]) not in vues[sent_id]:
                            vues[sent_id].append(sorted(entry["commonSegmentsIndexes"]))
                            
                            for j in entry["commonSegmentsIndexes"][i]:
                                if asmr_res[sent_id][j] == "*":
                                    asmr_res[sent_id][j] = str(sent_mwes_counter[sent_id])

                                else:
                                    asmr_res[sent_id][j] = f"{asmr_res[sent_id][j]};{str(sent_mwes_counter[sent_id])}"

                    is_condition_valid = True           
    return asmr_res


def applyLabels(data_main,condition_name,seeds,thres_tok,thres_lem,thres_pos,thres_sem,LANG=parameters.NAMEPATH,SEG=parameters.SEGMENT_VERSION):
    """write cupt giles with found labels for each sentence"""
    asmr_res = findLabels(condition_name,seeds,thres_tok,thres_lem,thres_pos,thres_sem,LANG=LANG)
    for i,entry in enumerate(data_main):
        data_main[i]["parsing"]["parseme:mwe"] = ["*" for form in entry["parsing"]["form"]]
        unique_id = entry["sent"]+entry["metadata"]["id"]
        if unique_id in asmr_res:
            data_main[i]["parsing"]["parseme:mwe"] = asmr_res[unique_id]
    if condition_name == "threshold": #or condition_name == "threshold_discontiguities":
        writeFile(f"output/{LANG}/labelled/{parameters.TEST_DATA}_{SEG}/{condition_name}_tok{round(thres_tok,1)}_upos{round(thres_pos,1)}_lem{round(thres_lem,1)}_sem{round(thres_sem,1)}.cupt",ASMRtoCONLLU(data_main))
    else:
        writeFile(f"output/{LANG}/labelled/{parameters.TEST_DATA}_{SEG}/{condition_name}.cupt",ASMRtoCONLLU(data_main))


def createEvaluationFiles(wanted_res=[],LANG=parameters.NAMEPATH,SEG=parameters.SEGMENT_VERSION):
    """for a given set of conditions and threshold, apply them to create multiple labelled cupt files"""
    createFolders(f"output/{LANG}/labelled/{parameters.TEST_DATA}_{SEG}")
    seeds = openJson(f"data/{LANG}.json")
    data_main = openJson(f"data/{LANG}/{parameters.TEST_DATA}.json")  
    #thresholds = [1] + np.arange(0.9,0,-0.1).tolist()
    #thresholds = [1] + np.arange(0.8,0,-0.2).tolist()
    thresholds = [1] + np.arange(0.7,0,-0.3).tolist()
    for thres_tok in tqdm(thresholds, leave=True): 
        for thres_pos in tqdm(thresholds, leave=False):
            for thres_lem in tqdm(thresholds, leave=False):
                #for thres_sem in tqdm(thresholds, leave=False):
                thres_sem = 0
                thesh_pred = f"threshold_tok{round(thres_tok,1)}_upos{round(thres_pos,1)}_lem{round(thres_lem,1)}_sem{round(thres_sem,1)}"
                    #thesh_disc_pred = f"threshold_discontiguities_tok{round(thres_tok,1)}_upos{round(thres_pos,1)}_lem{round(thres_lem,1)}_sem{round(thres_sem,1)}"
                if len(wanted_res) == 0 or thesh_pred in wanted_res:
                    applyLabels(data_main,"threshold",seeds,thres_tok,thres_lem,thres_pos,thres_sem,LANG=LANG,SEG=SEG)
                    #if len(wanted_res) == 0 or thesh_disc_pred in wanted_res:
                    #    applyLabels(data_main,"threshold_discontiguities",seeds,thres_tok,thres_lem,thres_pos,thres_sem,LANG=LANG,SEG=SEG)
    #applyLabels(data_main,"ruleBased",seeds,thres_tok,thres_lem,thres_pos,thres_sem,LANG=LANG,SEG=SEG)
