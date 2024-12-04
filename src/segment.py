from . import parameters
from .utils import *

def exactSegment(seed_align):
    """we ignore misalignment lists"""
    return sorted([i for i in seed_align if type(i) == int])


def fuzzySegment(seed_align):
    """we take everything between first and last common elements"""
    """if the Xth and Yth first and last elements from seed are missing,"""
    """we take X and Y elements at the begining and the end of the sentence to compensate"""
    if type(seed_align[0]) == list:
        seed_align[0] = seed_align[1] - len(seed_align[0])
    if type(seed_align[-1]) == list:
        seed_align[-1] = seed_align[-2] + len(seed_align[-1])
    return [i for i in range(seed_align[0],seed_align[-1]+1)]


def combinedSegment(seed_align,sent_align,entry):
    """"""
    return "not implemented yet"


def commonSegment(seed,sent,entry):
    """common segment isolation between a seed and a sent using list comprehension"""

    #to vizualise multiple tokens substitution (example with "Max a cassé sa pipe" and "Max a bien dégommé sa pipe")
    seed_align = [] #[0, 1, ['casser'], 4, 5]
    sent_align = [] #[0, 1, ['bien', 'dégommer'], 4, 5]
    #we see that 'casser' is replaced by either 'bien' or 'dégommer' if we only take into account our alignments

    #to create the sublists ["casser"] and ["bien","dégommer"]
    seed_subalign = []
    sent_subalign = []
    
    index_counter = 0 #we want to retrieve the indexes of the original sentence, so we increment this variable when needed only
    for i in range(len(seed)): #for each element in our alignments...

        if sent[i] == seed[i]: #if its a match

            #we add the sublists if there are misaligned elements
            if seed_subalign and sent_subalign:
                seed_align.append(seed_subalign)
                sent_align.append(sent_subalign)

            #we note the index of the match for both lists
            seed_align.append(index_counter)
            sent_align.append(index_counter)

            #we reset our sublists in case of match, to get ready to create others sublists
            seed_subalign = []
            sent_subalign = []

            index_counter += 1 #we take a step

        if sent[i] == "-" and seed[i] != "-": #if there is an element of the seed we can't find in the sent
            seed_subalign.append(seed[i])

        if sent[i] != "-" and seed[i] == "-": #if there is an element of the sent we can't find in the seed
            sent_subalign.append(sent[i])
            index_counter += 1

    if parameters.VERSION == "exact":
        commonSeg = exactSegment(seed_align)

    elif parameters.VERSION == "fuzzy":
        commonSeg = fuzzySegment(seed_align)

    elif parameters.VERSION == "combined":
        commonSeg = combinedSegment(seed_align,sent_align,entry)

    else:
        print("parameters.py : VERSION does not match any know version, aborting...")
        return 0
    
    return commonSeg


def segment(path):
    """for each sent of a json file (path), get its common segments with its seed"""
    
    data = openJson(path)
    new_data = []

    for entry in data:
        
        try:
            entry["commonSegments"] = {}
            entry["commonSegmentsIndexes"] = []
                
            for alignment in entry["alignments"]:

                commonSeg = commonSegment(alignment[1],alignment[0],entry)

                if len(commonSeg) > len(entry["parsing"][parameters.main_layer]):
                    commonSeg = [i for i in range(len(entry["parsing"][parameters.main_layer]))] #if the sentence is shorter than the seed

                entry["commonSegmentsIndexes"].append(commonSeg)
                    
                for layer in parameters.layers.keys():
                    if layer not in entry["commonSegments"]:
                        entry["commonSegments"][layer] = []
                    
                    seg = [entry["parsing"][layer][i] for i in commonSeg] 
                    entry["commonSegments"][layer].append(seg)

            new_data.append(entry)

        except IndexError: #if there is no common elements between a sentence and a seed
            debug(f"[ERROR 02] There should be at least one common element between a sent and a seed !\nproblematic sent ID: {entry['metadata']['id']}")

    writeJson(path,new_data)


def segmentAll():
    """process segment function on every file in 'sorted/' folder"""
    for path in tqdm(glob.glob(f"output/{parameters.NAMEPATH}/sorted/*.json")):
        segment(path)
    print("")
