from Bio.Seq import Seq
from Bio import pairwise2

import parameters
from .utils import *

def deleteBadAlignments(path):
    """sometime we align two different words between the seed and the sent, we remove those occurrences"""
    data = openJson(path)
    for entry in data:
        new_alignments = []
        for alignments in entry["alignments"]:
            erroned = False
            for i,w in enumerate(alignments[0]):
                if w != "-" and alignments[1][i] != "-" and w != alignments[1][i]:
                    erroned = True
            if not erroned:
                new_alignments.append(alignments)
        entry["alignments"] = new_alignments
    writeJson(path,data)


def alignment(seed,sent):
    """align a seed and a sent using Biopython function"""
    alignments = pairwise2.align.globalms(sent,seed,2,-1,-0.5,-0.1, gap_char=["-"]) #biopython function, only gap_char matters here
    return [[align[0],align[1]] for align in alignments] #0 and 1 indexes are aligned list in returned biopython object


def align(path,main_layer=parameters.main_layer):
    """for each sent in json (path), tokenize this sent and align it with its seed"""
    data = openJson(path)
    seed = openJson("logs/seeds.json")[data[0]["paired_with"]["seed"]]
    for entry in data:
        entry["alignments"] = alignment(seed[main_layer],entry["parsing"][main_layer])
    writeJson(path,data)
  

def alignAll():
    """process align function on every file in 'sorted/' folder"""
    for path in tqdm(glob.glob("output/sorted/*.json")):
        align(path)
    deleteBadAlignments(path)
    print("")
