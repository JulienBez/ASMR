from src.utils import *
from src.align import *
from src.segment import *
from src.measure import *
from src.evaluation import *

def sortAndFormat(data_type):
    "convert all data from CATCHPHRASE paper into json-ready file for ASMR + create seeds file"

    with open(f"data/snowclone_reference_data_{data_type}",'r',encoding="utf-8") as f:
        lines = f.readlines()
    lines = [l.replace("\n","") for l in lines]

    data = {}
    id_counter = 0

    for line in lines:

        line = line.split(",")
        seed = line[0]

        if len(line) != 3:
            print(f"error, inconsistant number of columns : {line}")

        entry = {
            "sent":line[1],
            "metadata": {
                "id":id_counter,
                "snowclone_label":int(line[-1])
                },
            "paired_with": {
                "seed":line[0],
                "distance":None
            }
        }

        id_counter += 1

        if seed not in data:
            data[seed] = []
        data[seed].append(entry)

    createFolders(f"output/{data_type}/sorted")
    seeds = {}

    for s,d in data.items():

        s_path = "".join(x for x in s.replace(" ","_") if x.isalnum() or x == "_")
        writeJson(f"output/{data_type}/sorted/{s_path}.json",d)

        seeds[s] = {}
    
    writeJson(f"output/{data_type}/seeds.json",seeds)


def parseSeeds(data_type):
    """create a log file with every seed and its NLP treatment if not exists"""
    seeds = openJson(f"output/{data_type}/seeds.json")
    for seed,value in seeds.items(): 
        seeds[seed] = {**value,**myParser(seed)}
    writeJson(f"output/{data_type}/seeds.json",seeds)


def parseTweets(data_type):
    """for each tweet do NLP treatment on it"""
    for path in tqdm(glob.glob(f"output/{data_type}/sorted/*.json")):
        data = openJson(path)
        for entry in data:
            sent = entry["sent"]
            entry["parsing"] = myParser(sent)
        writeJson(path,data)


def runParametersModififier(data_type):
    """"""

    studied_layers = [["TOK"]]#[["TOK"],["LEM"],["POS"],["TOK","LEM"],["TOK","POS"],["LEM","POS"],["TOK","LEM","POS"]]
    main_layers = ["TOK"]
    ngrams = [(1,2),(1,3),(2,3),(2,4),(3,4),(3,5),(4,5),(4,6)]
    analyzers = ["word","char","char_wb"]
    thresholds = [1] + np.arange(0.9,0,-0.1).tolist()
    versions = ["combined","fuzzy","exact"]

    total = len(studied_layers)*len(main_layers)*len(ngrams)*len(analyzers)*len(thresholds)*len(versions)
    counter = 1

    for main_layer in main_layers:
        alignAll(main_layer,data_type)

        for studied_layer in studied_layers:
            for version in versions:
                segmentAll(main_layer,data_type,studied_layer,version)

                for analyzer in analyzers:

                    for ngram in ngrams:
                        measureAll(ngram,analyzer,studied_layer,data_type)

                        for threshold in thresholds:

                            print(f"{counter}/{total}",end="\r")
                            counter += 1

                            res = getResults(data_type,threshold=threshold,printit=False)
                            results = openJson(f"output/results/{data_type}.json")
                            ngram_show = '-'.join([str(i) for i in ngram])
                            results[version][f"{'-'.join(studied_layer)}_{main_layer}_{ngram_show}_{analyzer}_{threshold}_{version}"] = res
                            writeJson(f"output/results/{data_type}.json",results)


def catchphraseStats():
    ""

    overlaps = {}
    print("#Token & #Sentence & #Snowclone \\\\")
    for data_type in ["train","val","test","all"]:

        with open(f"data/snowclone_reference_data_{data_type}",'r',encoding="utf-8") as f:
            lines = f.readlines()
        lines = [l.replace("\n","") for l in lines]

        tok = 0
        sent = 0
        label_1 = 0

        for line in lines:
            line = line.split(",")

            tok += len(line[1].split(" "))
            sent += 1
            
            if line[-1] == "1":
                label_1 += 1

        for data_type2 in ["train","val","test"]:
            if data_type != data_type2:
                with open(f"data/snowclone_reference_data_{data_type2}",'r',encoding="utf-8") as f:
                    lines2 = f.readlines()
                lines2 = [l.replace("\n","") for l in lines2]
                counter = 0
                for l in lines2:
                    if l in lines:
                        counter += 1
                overlaps[f"{data_type}-{data_type2}"] = counter

        print(f"{tok} & {sent} & {label_1} \\\\")
        print(overlaps)


if __name__ == "__main__":

    #catchphraseStats()

    for data_type in ["train","val","test"]: #["all"]: #

        search_parameters = True

        if not os.path.exists(f"output/{data_type}/seeds.json"):

            print("getting data and parsing...")
            createFolders("output")

            from src.parse import *
            sortAndFormat(data_type)
            parseSeeds(data_type)
            parseTweets(data_type)

        if search_parameters == True and not os.path.exists(f"output/results/{data_type}.json"):

            createFolders(f"output/results")
            createFolders(f"logs/{data_type}")

            print("searching for the best parameters...")
            writeJson(f"output/results/{data_type}.json",{"exact":{},"fuzzy":{},"combined":{}})
            runParametersModififier(data_type)

        print("sorting data according to best parameters...")

        results = openJson(f"output/results/{data_type}.json")
        for k,v in results.items():
            results[k] = sorted(results[k].items(), key=lambda x:x[1]["F1score"],reverse=True)
        writeJson(f"output/results/{data_type}_sorted.json",results)

        for key,value in results.items():

            best_run,best_run_res = list(results[key][0])
            print(f"best run for {data_type}: {best_run}")
            for k,v in best_run_res.items():
                print(f" > {k}: {v}")

            best_run_params = best_run.split("_")
            ngrams_split = best_run_params[2].split("-")
            ngram = (int(ngrams_split[0]),int(ngrams_split[1]))
            main_layer = best_run_params[1]
            studied_layer = best_run_params[0].split("-")
            analyzer = best_run_params[3]
            version = best_run_params[-1]

            #ngram = (2,4)
            #main_layer = "TOK" 
            #studied_layer = ["TOK"] 
            #analyzer = "char" 
            #version = "combined" 

            alignAll(main_layer,data_type)
            segmentAll(main_layer,data_type,studied_layer,version)
            measureAll(ngram,analyzer,studied_layer,data_type)

            plotResults(data_type,studied_layer,main_layer,ngram,analyzer,version)


"""
    entry = openJson("output/val/sorted/im_going_to_make_him_an_offer_he_cant_refuse.json")[0]
    seeds = openJson("output/val/seeds.json")
    seed = entry["alignments"][0][1]
    sent = entry["alignments"][0][0]
    studied_layer = ["TOK"]
    version = "combined"

    commonSegment(seed,sent,entry,seeds,studied_layer,version)
    1/0
"""