import time

from src.utils import *
from src.process import *
from src.align import *
from src.segment import *
#from src.measure import *
from src.rank import *
from src.metadata import *
from src.results import *

from src.file_format_handler import *
from src.evaluation_files import *
from src.evaluation import *
from src.results_analysis import *
from src.parseme_metadata import *

from src import parameters

for path in glob.glob("output/*/dev_combined_best_runs.json"):
    lang = path.split("/")[-2]
    paramStudy("exact",thresholds=["1","0.7","0.4","0.1"],langu=lang)
paramStudy("exact")
1/0

a = False
if a:
    test = []
    mwes = openJson("data/FR.json").keys()
    for path in tqdm(glob.glob("output/FR/sorted/*.json")):
        p = openJson(path)
        test = test + p
    nb_test = 1297
    nb_good = 0
    for i in tqdm(test):
        i_mwes = i["metadata"]["mwes"]
        seed = i["paired_with"]["seed"]
        if seed in i_mwes:
            nb_good += 1
    print(nb_test,nb_good,nb_good/nb_test)
    1/0

#parsemeHistogram()
#paramStudy("exact")
#getTable(category="MWE-based",measure="F",n=10)
#allMeans("combined")
#bestParamExtraction()
#exampleRankingParseme()
#1/0

#Arabic,Bulgarian,Czech,German,Greek,English,Spanish,Basque,Persian,French,Irish,Hebrew,Hindi,Croatian,Hungarian,Italian,Lithuanian,Maltese,Polish,Portuguese,Romanian,Slovenian,Serbian,Swedish,Turkish,Chinese
#languages = set()
#for path in glob.glob("data/*.json"):
#    lang = path.split("/")[-1].replace(".json","")
#    languages.add(lang)
#print(",".join(sorted(list(languages))))
#1/0
    

"""
V = parameters.vectorizer
def vectorizer(V,seed,sents,metric="cosine"):
    "vectorize in unigrams and bigrams the seed and the sent"
    X = V.fit_transform([" ".join(sent) for sent in sents]) #to ensure there odds items don't ruin the process
    Y = V.transform([" ".join(seed)])
    return pairwise_kernels(Y,X,metric=metric)[0]

a = "some men just want to watch the world burn".split(" ")
b_exact = "some really just want to want to watch the world".split(" ")
b_fuzzy = "some people really do just want to watch the world freeze".split(" ")
b_combi = "some people just want to watch the world freeze".split(" ")

sent = [b_exact,b_fuzzy,b_combi]

print(vectorizer(V,a,sent))"""
#1/0

#python main.py -L HI -S exact -FpasmTE
def proceed(args):
    
    start = time.time()

    LANG = parameters.NAMEPATH
    if args.lang:
        LANG = args.lang

    SEG = parameters.SEGMENT_VERSION
    if args.seg:
        SEG = args.seg

    if args.format:
        print("Converting cupt to json...")
        getASMRdataAll(LANG=LANG)
        getASMRseeds(LANG=LANG)
    
    if args.process:
        print("Processing data...")
        process(LANG=LANG)
      
    if args.align:
        print("Creating alignments...")
        alignAll(LANG=LANG)
        
    if args.segment:
        print("Isolating segments...")
        segmentAll(LANG=LANG,SEG=SEG)
        
    if args.measure:
        print("Calculating similarities...")
        measureAll(LANG=LANG)
        
    if args.rank:
        print("Ranking candidates...")
        rankAll(LANG=LANG)

    if args.results:
        print("Getting some results...")
        results(LANG=LANG)

    if args.metadata:
        print("Getting some metadatas...")
        metadata(LANG=LANG)

    if args.test_threshold:        
        print("Getting labelled cupt files...")
        wanted_res = []
        if parameters.TEST_DATA == "test" and os.path.exists(f"output/{LANG}/dev_{SEG}_results.json"):
            wanted_res = sortResults(LANG,SEG,"MWE-based","F",10)
            print(wanted_res)
        createEvaluationFiles(wanted_res=wanted_res,LANG=LANG,SEG=SEG)
        print("")

    if args.parseme_eval:
        print("Getting parseme results using parseme scripts...")
        getAllEvaluations(LANG=LANG,SEG=SEG)
        compileResults(LANG=LANG,SEG=SEG)
        print("")

    if args.ranking_parseme:
        exampleRankingParseme()
    
        
    end = time.time()
    print(f"executed in {round(end - start,2)}")
  

if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-L","--lang",type=str,help="The language we want to run on.")
    parser.add_argument("-S","--seg",type=str,help="The matching method we use.")

    parser.add_argument("-F", "--format", action="store_true", help="Convert CUPT files to ASMR-ready JSON files.")
    
    parser.add_argument("-p", "--process", action="store_true", help="Clean and sort input data.")
    parser.add_argument("-a", "--align", action="store_true", help="Create alignments between each sentence and their seed.")
    parser.add_argument("-s", "--segment", action="store_true", help="Search for common segments to isolate using the alignments.")
    parser.add_argument("-m", "--measure", action="store_true", help="Measure a similarity score between each sentence and their seed.")
    parser.add_argument("-r", "--rank", action="store_true", help="Rank each and every candidates in each seed category.")
    parser.add_argument("-R", "--results", action="store_true", help="Some results.")
    parser.add_argument("-M", "--metadata", action="store_true", help="Some metadata.")

    parser.add_argument("-T", "--test_threshold", action="store_true", help="Create labelled files according to various thresholds.")
    parser.add_argument("-E", "--parseme_eval", action="store_true", help="Runs parseme evaluation scripts.")
    parser.add_argument("--ranking_parseme", action="store_true",help="Generate a ranking for each language")

    args = parser.parse_args()
    proceed(args)
