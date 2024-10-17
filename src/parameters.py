# PATH #
NAMEPATH = "Baybars"


# MISC #
debug = False       #if True, return error messages when needed, else ignore
language = "ar"


# VECTORS #
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
#vectorizer = TfidfVectorizer(ngram_range=(1,1),encoding="utf-8",lowercase=True,stop_words=None,analyzer=lambda x: x.split(" "))
vectorizer = CountVectorizer(ngram_range=(1,1),encoding="utf-8",lowercase=True,stop_words=None,analyzer=lambda x: x.split(" "))


# LAYERS #
main_layer = "TOK"  #layer we base our study on
layers = {          #main_layer + other layers we take into account
    "TOK" : {
        "min":0,    #minimum TOK similarity required to be in the ranking
        "max":2     #maximum TOK similarity requited to be in the ranking
    },
    "POS" : {
        "min":0,    #minimum POS similarity required to be in the ranking
        "max":2     #maximum POS similarity requited to be in the ranking
    },
    "LEM" : {
        "min":0,    #minimum LEM similarity required to be in the ranking
        "max":2     #maximum LEM similarity requited to be in the ranking
    }
}


# RANKING #
nrow = 0            #max number of rows to show in ranking
minSim = 0          #minimum mean similarity required to be in the ranking
maxSim = 2          #maximum mean similarity required to be in the ranking
minFreq = 0         #minimal number of isolated segments to have to be in the ranking
latex = True        #create ranking in the form of a simple latex table

