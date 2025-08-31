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
