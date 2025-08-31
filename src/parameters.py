# RUN ASMR ON <NAMEPATH> #
NAMEPATH = "NULL"
SEGMENT_VERSION = "NULL"
#MASK_VERBS = "unmasked"


# ADDED PARAMETERS FOR PARSEME RUNS #
TRAIN_DATA = "train"
TEST_DATA = "test"


# PARAMETERS #
PROCESS_VERSION = "sortByDistances" #sortByDistances, sortByCommons


# MISC #
debug = False #if True, return error messages when needed, else ignore


# VECTORS #
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
#vectorizer = TfidfVectorizer(ngram_range=(1,2),encoding="utf-8",lowercase=True,stop_words=None,analyzer="word") #for FrUIT
#vectorizer = CountVectorizer(ngram_range=(1,1),encoding="utf-8",lowercase=True,stop_words=None,analyzer=lambda x: x.split(" ")) #for Baybars
#vectorizer = TfidfVectorizer(ngram_range=(2,3),encoding="utf-8",lowercase=True,stop_words=None,analyzer="word") #for catchphrase
vectorizer = TfidfVectorizer(ngram_range=(2,3),encoding="utf-8",lowercase=True,stop_words=None,analyzer="char")
POS_vectorizer = TfidfVectorizer(ngram_range=(1,1),encoding="utf-8",lowercase=True,stop_words=None,analyzer="word")

# LAYERS #
main_layer = "lemma" #layer we base our study on

TOK_layer = "form" #token layer
POS_layer = "upos" #pos tags layer
LEM_layer = "lemma" #lemma layer
SEM_layer = "SEM"

layers = {          #main_layer + other layers we take into account
    "form" : {
        "min":0,    #minimum TOK similarity required to be in the ranking
        "max":2     #maximum TOK similarity requited to be in the ranking
    },
    "upos" : {
        "min":0,    #minimum POS similarity required to be in the ranking
        "max":2     #maximum POS similarity requited to be in the ranking
    },
    "lemma" : {
        "min":0,    #minimum LEM similarity required to be in the ranking
        "max":2     #maximum LEM similarity requited to be in the ranking
    }#,
#    "SEM" : {
#        "min":0,
#        "max":2
#    }
}


# RANKING #
nrow = 0            #max number of rows to show in ranking
minSim = 0          #minimum mean similarity required to be in the ranking
maxSim = 2          #maximum mean similarity required to be in the ranking
minFreq = 0         #minimal number of isolated segments to have to be in the ranking
latex = True        #create ranking in the form of a simple latex table


# RESULTS #
RtoL = False #for languages written from right to left, only used by results.py and rank.py
studied_sequences = []

# studied_sequences list examples:
# ["Travailler plus pour gagner plus","Que la force soit avec toi","c'est le deuxième effet Kisscool"]
# ["غضب غضبا شديد ","قلب الضيا بعينه ظلام ","فلما سمع فلان من فلان ذلك الكلام "]
# ["فز واثب على الاقدام ","بات ذلك الليله ","وعند فراغه من ذلك الكلام "]
# unwanted = 'فلما سمع فلان من فلان ذلك الكلام ' #to remove
