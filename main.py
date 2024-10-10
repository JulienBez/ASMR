import time

from src.utils import *
from src.process import *
from src.align import *
from src.segment import *
from src.measure import *
from src.rank import *
from src.metadata import *
from src.results import *

def proceed(args):
    
    start = time.time()
    
    if args.process:
        process()
      
    if args.align:
        alignAll()
        
    if args.segment:
        segmentAll()
        
    if args.measure:
        measureAll()
        
    if args.rank:
        rankAll()

    if args.all:
        print("Processing data...")
        process()
        print("Creating alignments...")
        alignAll()
        print("Creating segments...")
        segmentAll()
        print("Calculating similarities...")
        measureAll()
        print("ranking candidates...")
        rankAll()

    if args.results:
        plotScores()
        clusterSegments()

    if args.metadata:
        tokenProportions()
        
    end = time.time()
    print(f"executed in {round(end - start,2)}")
  

if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-p", "--process", action="store_true", help="Clean and sort input data.")
    
    parser.add_argument("-a", "--align", action="store_true", help="Create alignments between each sentence and their seed.")
    parser.add_argument("-s", "--segment", action="store_true", help="Search for common segments using the alignments.")
    parser.add_argument("-m", "--measure", action="store_true", help="Measure a similarity score between each sentence and their seed.")
    parser.add_argument("-r", "--rank", action="store_true", help="Rank each and every candidates in each seed category.")
    
    parser.add_argument("-A", "--all", action="store_true", help="Execut all scripts.")
    parser.add_argument("-R", "--results", action="store_true", help="Some results functions.")
    parser.add_argument("-M", "--metadata", action="store_true", help="Some metadata.")
    
    args = parser.parse_args()
    proceed(args)

