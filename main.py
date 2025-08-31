import time

from src.utils import *
from src.pairing import *
from src.align import *
from src.segment import *
from src.measure import *
from src.rank import *
from src.metadata import *
from src.results import *


def proceed(args):
    
    start = time.time()
    
    if args.pairing:
        print("Creating pairs...")
        pairingAll()
      
    if args.align:
        print("Creating alignments...")
        alignAll()
        
    if args.segment:
        print("Isolating segments...")
        segmentAll()
        
    if args.measure:
        print("Calculating similarities...")
        measureAll()
        
    if args.rank:
        print("Ranking candidates...")
        rankAll()

    if args.results:
        print("Getting some results...")
        results()

    if args.metadata:
        print("Getting some metadatas...")
        metadata()
        
    end = time.time()
    print(f"executed in {round(end - start,2)}")
  

if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-p", "--pairing", action="store_true", help="Create pairs between sentences and seeds.")
    parser.add_argument("-a", "--align", action="store_true", help="Create alignments between each sentence and their seed.")
    parser.add_argument("-s", "--segment", action="store_true", help="Search for common segments to isolate using the alignments.")
    parser.add_argument("-m", "--measure", action="store_true", help="Measure a similarity score between each sentence and their seed.")
    parser.add_argument("-r", "--rank", action="store_true", help="Rank each and every candidates in each seed category.")
    parser.add_argument("-R", "--results", action="store_true", help="Some results.")
    parser.add_argument("-M", "--metadata", action="store_true", help="Some metadata.")
    
    args = parser.parse_args()
    proceed(args)

