###########################################################
#                                                         #
# segment.py :                                            #
#                                                         #
#   - isolate a common segment between a sent and a seed  #
#   - indicate where we had to fill the segment           #
#                                                         #
###########################################################

import parameters
from .utils import *

def commonSegment(seed,sent):
    """common segment isolation between a seed and a sent using list comprehension"""

    tags = [] #NC = not common, NF = not found, C = common
    for i,w in enumerate(seed):
        if sent[i] != "-" and seed[i] == "-": #tokens from the sent that are not in the seed
            tags.append("NC")
        if sent[i] == "-" and seed[i] != "-": #tokens from the seed not found in the sent
            tags.append("NF")
        if sent[i] != "-" and seed[i] != "-": #common tokens between the sent and the seed
            tags.append("C")  
        if sent[i] == "-" and seed[i] == "-": #this case should not be possible
            print("error",seed,sent)
    
    common = [i for i,w in enumerate(tags) if w=="C"]
    NF_head = [i for i,w in enumerate(tags) if w=="NF" and i<common[0]] #not found BEFORE the first common token
    NF_body = [i for i,w in enumerate(tags) if w=="NF" and i>common[0] and i<common[-1]] #not found BETWEEN the first and the last common token
    NF_tail = [i for i,w in enumerate(tags) if w=="NF" and i>common[-1]] #not found AFTER the last common token
    
    segment_first_word = common[0]-len(NF_head) #we have to take into account not founds to find good ids of tokens
    segment_last_word = common[-1]-len(NF_head)-len(NF_body)+1 #+1 to include last word
    
    head = [segment_first_word-1-i for i in range(len(NF_head))] 
    body = list(range(segment_first_word,segment_last_word))
    tail = [segment_last_word+i for i in range(len(NF_tail)) if segment_last_word+i < len(tags)-len(NF_tail+NF_body+NF_head)]
    
    return sorted(head + body + tail)


def segment(path):
    """for each sent of a json file (path), get its common segments with its seed"""
    
    data = openJson(path)
    new_data = []

    for entry in data:
        
        try:
            entry["commonSegments"] = {}
            entry["commonSegmentsIndexes"] = []
                
            for alignment in entry["alignments"]:

                commonSeg = commonSegment(alignment[1],alignment[0])
                if len(commonSeg) > len(entry["parsing"][layer]):
                    commonSeg = [i for i in range(len(entry["parsing"][parameters.main_layer]))] #if the sentence is shorter than the seed

                entry["commonSegmentsIndexes"].append(commonSeg)
                    
                for layer in entry["parsing"].keys():
                    if layer not in entry["commonSegments"]:
                        entry["commonSegments"][layer] = []
                    
                    seg = [entry["parsing"][layer][i] for i in commonSeg] 
                    entry["commonSegments"][layer].append(seg)

            new_data.append(entry)

        except IndexError: #if there is no common elements between a sentence and a seed
            pass

    writeJson(path,new_data)


def segmentAll():
    """process segment function on every file in 'sorted/' folder"""
    for path in tqdm(glob.glob("output/sorted/*.json")):
        segment(path)
    print("")
