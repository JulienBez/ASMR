# ENCODING
encoding = "utf-8"

# VECTORS
ngram_range = (1,2)
lowercase = True
stop_words = None
analyzer = lambda x: x.split(" ")

# PROCESS
main_layer = "TOK"  #layer we base our study on

# RANKING
nrow = 0            #max number of rows to show in ranking
minSim = 0          #minimum mean similarity required to be in the ranking
maxSim = 2          #maximum mean similarity required to be in the ranking
minfreq = 0         #minimal number of isolated segments to have to be in the ranking
latex = True        #create ranking in the form of a simple latex table

layers = {
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