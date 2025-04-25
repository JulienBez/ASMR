from Levenshtein import ratio

from . import parameters
from .utils import *

def exactSegment(seed_align):
    """we ignore misalignment lists"""
    return sorted([i for i in seed_align if type(i) == int])


def fuzzySegment(seed_align,sent_align):
    """we take everything between first and last common elements"""
    """if the Xth and Yth first and last elements from seed are missing,"""
    """we take X and Y elements at the begining and the end of the sentence to compensate"""
    if type(seed_align[0]) == list:
        seed_align[0] = seed_align[1] - min([len(seed_align[0]),len(sent_align[0])]) #if sent_align is min, then we don"t go beyond list limit
    if type(seed_align[-1]) == list:
        seed_align[-1] = seed_align[-2] + min([len(seed_align[-1]),len(sent_align[-1])])
    return [i for i in range(seed_align[0],seed_align[-1]+1)]


def combinedSegment(seed_align,sent_align,entry,seeds,discont=parameters.discont):
    """for each misalignment list, we try to find a substitue for each missing words using rules"""
    """rule 1: we take the first word in misalignment list with the same POS tag (takes distance and POS sim into account)"""
    """rule 2: if no common POS tag, we look for the word with the biggest number of similarities for each misaligned word"""

    combined = []
    for i in range(len(seed_align)):

        if seed_align[i] == sent_align[i] and type(seed_align[i]) != list: #if alignment 
            combined.append(seed_align[i])

        else: #if there is a misalignment, there is a list

            if len(seed_align[i]) == len(sent_align[i]): #if the misalignment lists have the same size
                for j in sent_align[i]:
                    combined.append(j) #we add every elements from sent in our candidate

            else:

                for not_found in seed_align[i]: #for each word we couldn't find in seed
                    
                    candidates_pos = []
                    candidates_sim = {}

                    tok_not_found = seeds[entry["paired_with"]["seed"]][parameters.TOK_layer][not_found]
                    if parameters.POS_layer in parameters.layers.keys():
                        pos_not_found = seeds[entry["paired_with"]["seed"]][parameters.POS_layer][not_found]

                    for candidate in sent_align[i][:discont]: #for each word in the misalignment list (i.e. for each substitute candidate)

                        tok_candidate = entry["parsing"][parameters.TOK_layer][candidate]
                        if parameters.POS_layer in parameters.layers.keys():
                            pos_candidate = entry["parsing"][parameters.POS_layer][candidate]

                        if parameters.POS_layer in parameters.layers.keys() and pos_candidate == pos_not_found: #if they have the same pos tags
                            candidates_pos.append(candidate)

                        else: #else we estimate how close are each word with the not_found token
                            sim_score = ratio(" ".join(tok_candidate)," ".join(tok_not_found))
                            #sim_score = len(tok_not_found & tok_candidate)/max([len(tok_not_found),len(tok_candidate)])
                            candidates_sim[candidate] = sim_score

                    if candidates_pos:
                        substitute = candidates_pos[0]
                        combined.append(substitute)
                        sent_align[i].remove(substitute)

                    elif candidates_sim:    
                        substitute = sorted([[v,k] for k,v in candidates_sim.items()],reverse=True)[0][1]
                        combined.append(substitute)
                        sent_align[i].remove(substitute)
    
    #if len(seeds[entry["paired_with"]["seed"]]["lemma"]) != len([entry["parsing"]["lemma"][i] for i in combined]):
    #    print([entry["parsing"]["lemma"][i] for i in combined])
    #    print(seeds[entry["paired_with"]["seed"]]["lemma"])
    #    print()

    return combined          


def commonSegment(seed,sent,entry,seeds):
    """common segment isolation between a seed and a sent using list comprehension"""

    #to vizualise multiple tokens substitution (example with "Max a cassé sa pipe" and "Max a bien dégommé sa pipe")
    seed_align = [] #[0, 1, ['casser'], 4, 5]
    sent_align = [] #[0, 1, ['bien', 'dégommer'], 4, 5]
    #we see that 'casser' is replaced by either 'bien' or 'dégommer' if we only take into account our alignments

    #to create the sublists ["casser"] and ["bien","dégommer"]
    seed_subalign = []
    sent_subalign = []

    #to find the true ids of words in sent and seed, the one they had before alignment
    sep_counter_seed = 0
    sep_counter_sent = 0
    
    index_counter = 0 #we want to retrieve the indexes of the original sentence, so we increment this variable when needed only
    for i in range(len(seed)): #for each element in our alignments...

        if sent[i] == seed[i]: #if its a match

            #we add the sublists if there are misaligned elements
            if seed_subalign and sent_subalign:
                seed_align.append(seed_subalign)
                sent_align.append(sent_subalign)

            #we note the index of the match for both lists
            seed_align.append(index_counter-sep_counter_seed)
            sent_align.append(index_counter-sep_counter_seed) #very important, I struggled with this one for some reason

            #we reset our sublists in case of match, to get ready to create others sublists
            seed_subalign = []
            sent_subalign = []

            index_counter += 1 #we take a step

        if sent[i] == "-" and seed[i] != "-": #if there is an element of the seed we can't find in the sent
            #seed_subalign.append(seed[i])
            sep_counter_seed += 1
            seed_subalign.append(i-sep_counter_sent)
            index_counter += 1

        if sent[i] != "-" and seed[i] == "-": #if there is an element of the sent we can't find in the seed
            #sent_subalign.append(sent[i])
            sep_counter_sent += 1
            sent_subalign.append(i-sep_counter_seed)
            index_counter += 1

    if seed_subalign and sent_subalign: #to fetch the last terms 
        seed_align.append(seed_subalign)
        sent_align.append(sent_subalign)

    if len(sent_align) > 1 and len(seed_align) > 1:

        if parameters.SEGMENT_VERSION == "exact":
            commonSeg = exactSegment(seed_align)

        elif parameters.SEGMENT_VERSION == "fuzzy":
            commonSeg = fuzzySegment(seed_align,sent_align)

        elif parameters.SEGMENT_VERSION == "combined":
            commonSeg = combinedSegment(seed_align,sent_align,entry,seeds)

        else:
            print("parameters.py : VERSION does not match any know version, aborting...")
            return 0
        
    else:
        commonSeg = ""
    
    return commonSeg


def segment(path):
    """for each sent of a json file (path), get its common segments with its seed"""
    
    data = openJson(path)
    new_data = []
    seeds = openJson(f"data/{parameters.NAMEPATH}.json")

    for entry in data:
        
        #try:

        entry["commonSegments"] = {}
        entry["commonSegmentsIndexes"] = []
                
        for alignment in entry["alignments"]:

            commonSeg = commonSegment(alignment[1],alignment[0],entry,seeds)

            if len(commonSeg) > len(entry["parsing"][parameters.main_layer]):
                commonSeg = [i for i in range(len(entry["parsing"][parameters.main_layer]))] #if the sentence is shorter than the seed

            entry["commonSegmentsIndexes"].append(commonSeg)
                    
            for layer in parameters.layers.keys():
                if layer not in entry["commonSegments"]:
                    entry["commonSegments"][layer] = []
                    
                seg = [entry["parsing"][layer][i] for i in commonSeg] 
                entry["commonSegments"][layer].append(seg)

        new_data.append(entry)

        #except IndexError: #if there is no common elements between a sentence and a seed
        #    debug(f"[ERROR 02] There should be at least one common element between a sent and a seed !\nproblematic sent ID: {entry['metadata']['id']}")

    writeJson(path,new_data)


def segmentAll():
    """process segment function on every file in 'sorted/' folder"""
    for path in tqdm(glob.glob(f"output/{parameters.NAMEPATH}/sorted/*.json")):
        segment(path)
    print("")
