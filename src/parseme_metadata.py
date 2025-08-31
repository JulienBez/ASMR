import plotly.graph_objects as go
import matplotlib.pyplot as plt

import numpy

from . import parameters
from .utils import *

def parsemeHistogram():
    """"""

    languages = set()
    for path in glob.glob("data/*.json"):
        lang = path.split("/")[-1].replace(".json","")
        languages.add(lang)

    X_lang = [] 
    Y_sent = [] 
    Z_mwes = [] 

    for lang in tqdm(languages):
        y = 0
        z = 0
        for path in glob.glob(f"data/{lang}/*.json"):
            data = openJson(path)
            y += len(data)
            for entry in data:
                z += len(entry["metadata"]["mwes"])
        X_lang.append(lang)
        Y_sent.append(y)
        Z_mwes.append(z)

    font = {'family' : 'normal',
            #'weight' : 'bold',
            'size'   : 22}

    plt.rc('font', **font)
    
    X_axis = numpy.arange(len(X_lang)) 
    plt.figure(figsize=(20,10))
    
    plt.bar(X_axis - 0.2, Y_sent, 0.4, label = 'Phrases') 
    plt.bar(X_axis + 0.2, Z_mwes, 0.4, label = 'EMM') 
    
    plt.xticks(X_axis, X_lang) 
    plt.xlabel("Langues") 
    plt.ylabel("Nombre d'instances")  
    plt.legend() 
    plt.savefig("logs/parseme_metadata.png")
    plt.yscale('log')
    plt.savefig("logs/parseme_metadata_log.png")


def paramStudy(segment,thresholds=["1","0.7","0.4","0.1"],langu="all"):
    """"""

    if langu == "all":
        languages = set()
        for path in glob.glob("output/*/dev_combined_best_runs.json"):
            lang = path.split("/")[-2]
            languages.add(lang)

    else:
        languages = [langu]

    param_thresholds = ["tok","lem","upos","sem"]
    Fscores = {} #list of list

    for lang in languages:
        data = openJson(f"output/{lang}/dev_{segment}_results.json")

        for param in param_thresholds:
            if param not in Fscores:
                Fscores[param] = {}

            for thres in thresholds:

                if thres not in Fscores[param]:
                    Fscores[param][thres] = []

                m =  [data[k]["MWE-based"]["F"] for k,v in data.items() if f"{param}{thres}" in k and k !='ruleBased']
                Fscores[param][thres] = Fscores[param][thres] + m

    #plotpy graph
    
    #check if there is no len issue
    #lenght = len(Fscores["tok"]["1"])
    #for k1,v1 in Fscores.items():
    #    for k2,v2 in v1.items():
    #        if len(v2) != lenght:
    #            print('ARG')

    g_len = len(Fscores["tok"]["1"])
    x = ["token" for i in range(g_len)] + ["lemma" for i in range(g_len)] + ["upos" for i in range(g_len)] + ["semantic" for i in range(g_len)]

    layout = go.Layout(title=f"{langu}")
    fig = go.Figure(layout=layout)
    fig.update_yaxes(range = [0,1])

    fig.add_trace(go.Box(
        y=Fscores["tok"]["0.1"] + Fscores["lem"]["0.1"] + Fscores["upos"]["0.1"] + Fscores["sem"]["0.1"],
        x=x,
        name='0.1',
        marker_color= '#bfbfbf', #'#17becf',
        boxpoints=False
    ))

    fig.add_trace(go.Box(
        y=Fscores["tok"]["0.4"] + Fscores["lem"]["0.4"] + Fscores["upos"]["0.4"] + Fscores["sem"]["0.4"],
        x=x,
        name='0.4',
        marker_color= '#7f7f7f', #'#d62728',
        boxpoints=False
    ))

    fig.add_trace(go.Box(
        y=Fscores["tok"]["0.7"] + Fscores["lem"]["0.7"] + Fscores["upos"]["0.7"] + Fscores["sem"]["0.7"],
        x=x,
        name='0.7',
        marker_color= '#404040', #'#9467bd',
        boxpoints=False
    ))

    fig.add_trace(go.Box(
        y=Fscores["tok"]["1"] + Fscores["lem"]["1"] + Fscores["upos"]["1"] + Fscores["sem"]["1"],
        x=x,
        name='1',
        marker_color= '#000000', #'#e377c2',
        boxpoints=False
    ))

    fig.update_layout(
        font=dict(
            #family="Courier New, monospace",
            size=21,
        ),
        yaxis=dict(
            title=dict(
                text='F-score')
        ),
        boxmode='group' # group together boxes of the different traces for each value of x
    )


    fig.update_layout(width=1500)

    if langu == "all":
        fig.write_image("logs/boxplot_all.png")
    else:
        fig.write_image(f"logs/boxplot_{lang}.png")


def bestParamExtraction():
    """"""

    languages = set()
    for path in glob.glob("data/*.json"):
        lang = path.split("/")[-1].replace(".json","")
        languages.add(lang)

    lines = [" & tok & upos & lem & sem & tok & upos & lem & sem & tok & upos & lem & sem \\\\"]
    for language in sorted(list(languages)):
        line = [language]
        for segment in ["exact","fuzzy","combined"]:
            data = openJson(f"output/{language}/test_{segment}_results.json")
            best_run = sorted([[v["MWE-based"]["F"],k] for k,v in data.items() if k != "ruleBased"],reverse=True)[0][1]
            for param in best_run.split("_")[1:]:
                line.append(param.replace("tok","").replace("upos","").replace("lem","").replace("sem",""))
        lines.append(" & ".join(line)+" \\\\")

    writeFile("logs/parseme_best_runs.tex","\n".join(lines))


def bestCandidates(language,num_candidates=3):
    """"""

    candidates = []
    seen = set()
    for path in glob.glob(f"output/{language}/sorted/*.json"):
        data = openJson(path)
        mwe = data[0]["paired_with"]["seed"]

        mean_data = []
        for entry in data:
            if " ".join(entry['commonSegments']['form'][0]) not in seen:
                seen.add(" ".join(entry['commonSegments']['form'][0]))
                mean_data.append([entry["similarities"]["meanLayer"][0],entry["metadata"]["id"]])
        mean_data = sorted(mean_data,reverse=True)[:num_candidates]

        if len(mean_data) == num_candidates:
            mean = sum([i[0] for i in mean_data])/len(mean_data)
            candidates.append([mean,[i[1] for i in mean_data],path])

    best_candidate = sorted(candidates,reverse=True)[0]
    data_best = openJson(best_candidate[-1])

    line = []
    for entry in data_best:
        if entry["metadata"]["id"] in best_candidate[1]:
            line.append(f" & {' '.join(entry['commonSegments']['form'][0])} & {round(entry['similarities']['meanLayer'][0],2)} & {round(entry['similarities']['form'][0],2)} & {round(entry['similarities']['upos'][0],2)} & {round(entry['similarities']['lemma'][0],2)} \\\\") #& {round(entry['similarities']['SEM'][0],2)} \\\\")
    return line
        


def exampleRankingParseme(num_candidate=3):
    """"""

    languages = set()
    for path in glob.glob("data/*.json"):
        lang = path.split("/")[-1].replace(".json","")
        languages.add(lang)

    lines = ["Language & Candidate & mean & tok & upos & lem & sem \\\\"]
    for language in tqdm(sorted(languages)):
        line = [f"""\\multirow{{{num_candidate}}}{{*}}{{{language}}}"""]
        line = line + bestCandidates(language,num_candidates=num_candidate) + ["\n"]
        lines.append("\n".join(line))

    writeFile("logs/ranking_parseme.tex","\n\\hline\n".join(lines))

        
def parsemeTableStats():
    ""

    languages = set()
    for path in glob.glob("data/*.json"):
        lang = path.split("/")[-1].replace(".json","")
        languages.add(lang)

    total_tok = 0
    total_phrases = 0
    total_mwes = 0
    table_res = []
    for lang in languages:
        dict_lang = {}
        for path in glob.glob(f"data/{lang}/*.json"):
            data = openJson(path)
            dict_lang[path.split("/")[-1].replace(".json","")] = {"sent":len(data),"mwe":sum([len(i["metadata"]["mwes"]) for i in data]),"token":sum([len(i["parsing"]["id"]) for i in data])}
            total_phrases += dict_lang[path.split("/")[-1].replace(".json","")]["sent"]
            total_mwes += dict_lang[path.split("/")[-1].replace(".json","")]["mwe"]
            total_tok += dict_lang[path.split("/")[-1].replace(".json","")]["token"]
        table_res.append(" & ".join([str(i) for i in [lang,dict_lang["train"]["sent"],dict_lang["dev"]["sent"],dict_lang["test"]["sent"],
                          dict_lang["train"]["mwe"],dict_lang["dev"]["mwe"],dict_lang["test"]["mwe"],
                          dict_lang["train"]["token"],dict_lang["dev"]["token"],dict_lang["test"]["token"]]]) + "\\\\")
        
    writeFile("logs/table_stats_parseme.tex","\n".join(sorted(table_res)))
    print("MWEs : ",total_mwes)
    print("Phrases : ",total_phrases)
    print("Tokens : ",total_tok)