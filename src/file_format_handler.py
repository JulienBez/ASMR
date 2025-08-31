from .utils import *
from conllu import parse
from . import parameters

def getASMRdata(path):
    "read a PARSEME conllu file and adapt it to ASMR json file format"

    try:
        conllu_file = parse(openFile(path)) #open conllu file with conllu parser package
    except:
        print(f"error for file {path}, maybe the file format is incorrect")
        return 0

    json_file = []
    
    for sentence in conllu_file:

        entry = { #ASMR json file format
            "sent": sentence.metadata["text"],
            "metadata": { #lots of metadata
                "id": sentence.metadata["source_sent_id"],
                "label": 0,
                "mwes": [],
                "mwes_ids": [],
                "mwes_categories": [],
                "mwes_discontiguities": [], #not documented in PARSEME, we find them ourselves
                "additionnal_metadata": {} #contains all PARSEME metadata for each sentence, helps us recreate cupt files later
            },
            "parsing": {prop:[] for prop in sentence[0]}
        }
        
        for i in sentence.metadata:
            entry["metadata"]["additionnal_metadata"][i] = sentence.metadata[i]
        
        mwes = {}
        mwes_discontiguity_counter = {} #to count the number of each discontiguities
        
        for wid,word in enumerate(sentence):

            for prop in word: #conllu header (id, form, lemma, upos, ...)
                #if prop != "parseme:mwe":
                entry["parsing"][prop].append(word[prop])

            if word["parseme:mwe"] != "*": #if the word is part of a mwe

                mwe_ids = word["parseme:mwe"].split(";") #split if word in multiple MWEs
                mwe_cat = ""

                for mwe_id in mwe_ids:

                    if ":" in mwe_id: #if it is the first word of the mwe, we extract its category
                        mwe_cat = mwe_id.split(":")[-1]
                        mwe_id = mwe_id.split(":")[0]

                    if mwe_id not in mwes:

                        mwes[mwe_id] = {
                            "category":mwe_cat,
                            "lemma": [],
                            "id": [],
                            "discont": []
                            }
                        
                        mwes_discontiguity_counter[mwe_id] = 0

                    mwes[mwe_id]["lemma"].append(word["lemma"])
                    mwes[mwe_id]["id"].append(wid)
                    mwes[mwe_id]["discont"].append(mwes_discontiguity_counter[mwe_id])

                    for mwe in mwes_discontiguity_counter.keys():
                        if mwe != mwe_id:
                            mwes_discontiguity_counter[mwe] += 1

            else: #if word is not part of mwe, we still count discontiguity length
                for mwe in mwes_discontiguity_counter.keys():
                    mwes_discontiguity_counter[mwe] += 1

        for k,v in mwes.items():

            entry["metadata"]["label"] = 1
            entry["metadata"]["mwes"].append(" ".join(v["lemma"]))
            entry["metadata"]["mwes_ids"].append(v["id"])
            entry["metadata"]["mwes_categories"].append(v["category"])
            entry["metadata"]["mwes_discontiguities"].append(v["discont"][1:])
            
        json_file.append(entry)

    writeJson(path.replace('.cupt','.json'),json_file)


def getASMRseeds(LANG=parameters.NAMEPATH):
    "fetch a list of all MWEs for each language from the ASMR json file created with getASMRdata"
    dict_seeds = {}
    for path in glob.glob(f"data/{LANG}/{parameters.TRAIN_DATA}.json"):
        data = openJson(path)
        for entry in data:
            for mwes_ids in entry["metadata"]["mwes_ids"]:
                seed = {}
                for key, value in entry["parsing"].items():
                    if key not in seed and key == "lemma":
                        seed["form"] = [value[i] for i in mwes_ids]
                        seed[key] = [value[i] for i in mwes_ids]
                    if key not in seed and key == "upos":
                        seed[key] = [value[i] for i in mwes_ids]
                mwe_key = " ".join(seed["lemma"])
                if mwe_key not in dict_seeds:
                    dict_seeds[mwe_key] = seed
    #if parameters.MASK_VERBS == "masked":
    #    dict_seeds = maskVerbsInSeeds(dict_seeds)
    writeJson(f"data/{LANG}.json",dict_seeds)


def maskVerbsInSeeds(dict_seed):
    """small test we made by masking the verbs in seeds, but does not work ATM"""

    #SMALL SCRIPT TO SEE IF SYMBOL IN PARSEME
    #total = 0
    #for path in tqdm(glob.glob("data/*/*.cupt")):
    #    conllu_file = parse(openFile(path))
    #    for sentence in conllu_file:
    #        if "¤" in sentence.metadata["text"]:
    #            print(sentence)
    #            total += 1
    #print(total)

    new_dict_seed = {}
    mask_symbol = "¤"
    for k,v in dict_seed.items():
        for i,word in enumerate(dict_seed[k]["upos"]):
            if word == "VERB":
                dict_seed[k]["form"][i] = mask_symbol
                dict_seed[k]["lemma"][i] = mask_symbol
                new_dict_seed[" ".join(dict_seed[k]["lemma"])] = dict_seed[k]
    return new_dict_seed
    

def ASMRtoCONLLU(data):
    "convert ASMR files to PARSEME conllu, to run evaluation script from PARSEME later"
    lines = []  
    for entry in data:
        for k,v in entry["metadata"]["additionnal_metadata"].items():
            lines.append(f"# {k} = {v}")
        for i,_ in enumerate(entry["parsing"]["id"]):       
            line = []
            for key, value in entry["parsing"].items():
                if value:
                    if type(value[i]) == list:
                        value[i] = "".join([str(j) for j in value[i]])
                    if type(value[i]) == dict:
                        value[i] = "|".join([f"{k}={v}" for k,v in value[i].items()])
                    if value[i] is None:
                        value[i] = "_"
                    line.append(str(value[i]))
            lines.append("\t".join(line))
        lines.append("")
    lines.append("")
    return "\n".join(lines)


def getASMRdataAll(LANG=parameters.NAMEPATH):
    """convert all data from conllu (cupt) to json"""
    for path in tqdm(glob.glob(f"data/{LANG}/*.cupt")):
        getASMRdata(path)
    print("")