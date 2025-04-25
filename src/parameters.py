# RUN ASMR ON <NAMEPATH> #
NAMEPATH = "FrUIT"            # corpus we work on (must have a folder and a json file with this name)


# PARAMETERS #
PAIRING_VERSION = "sortByCommons"   # sortByDistances, sortByCommons
SEGMENT_VERSION = "combined"        # exact, fuzzy, combined
debug = False                       # if True, return error messages when needed, else ignore


# VECTORS #
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
vectorizer = TfidfVectorizer(ngram_range=(1,2),encoding="utf-8",lowercase=True,stop_words=None,analyzer="word")                     # for catchphrase
#vectorizer = TfidfVectorizer(ngram_range=(3,4),encoding="utf-8",lowercase=True,stop_words=None,analyzer="char")                    # for FrUIT
#vectorizer = CountVectorizer(ngram_range=(1,1),encoding="utf-8",lowercase=True,stop_words=None,analyzer=lambda x: x.split(" "))    # for Baybars
POS_vectorizer = TfidfVectorizer(ngram_range=(1,1),encoding="utf-8",lowercase=True,stop_words=None,analyzer="word")


# LAYERS #
main_layer = "TOK"                  # layer we base our study on
discont = 4                         # max length of discontinuities

TOK_layer = "TOK"                   # token layer
POS_layer = "POS"                   # pos tags layer
LEM_layer = "LEM"                   # lemma layer

layers = {                          # main_layer + other layers we take into account
    "TOK" : {
        "min":0,                    # minimum TOK similarity required to be in the ranking
        "max":2                     # maximum TOK similarity requited to be in the ranking
    },
    "POS" : {
        "min":0,                    # minimum POS similarity required to be in the ranking
        "max":2                     # maximum POS similarity requited to be in the ranking
    },
    "LEM" : {
        "min":0,                    # minimum LEM similarity required to be in the ranking
        "max":2                     # maximum LEM similarity requited to be in the ranking
    }
}


# RANKING #
nrow = 0                            # max number of rows to show in ranking
minSim = 0                          # minimum mean similarity required to be in the ranking
maxSim = 2                          # maximum mean similarity required to be in the ranking
minFreq = 0                         # minimal number of isolated segments to have to be in the ranking
latex = True                        # create ranking in the form of a simple latex table


# RESULTS #
RtoL = False                        # for languages written from right to left, only used by results.py and rank.py
studied_sequences = [] 
unwanted = ""

# studied_sequences list examples:
# ["Travailler plus pour gagner plus","Que la force soit avec toi","c'est le deuxième effet Kisscool"]      # FrUIT
# ["غضب غضبا شديد ","قلب الضيا بعينه ظلام ","فلما سمع فلان من فلان ذلك الكلام "]                                # Baybars      
# ["فز واثب على الاقدام ","بات ذلك الليله ","وعند فراغه من ذلك الكلام "]                                      # Baybars
# unwanted = 'فلما سمع فلان من فلان ذلك الكلام '                                                               # to remove from data viz
