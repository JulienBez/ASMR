import plotly.graph_objects as go
from src.utils import *

def paramStudy():
    """"""

    #    ["1-2","1-3","2-3","2-4","3-4","3-5","4-5","4-6"]
    #    ["word","char","char_wb"]

    param_thresholds = ["word","char","char_wb"]
    Fscores = {} #list of list

    for part in ["test","train","val"]:
        data = openJson(f"output/results/{part}_sorted.json")

        for param in param_thresholds:
            if param not in Fscores:
                Fscores[param] = []

            for approach in ["exact","fuzzy","combined"]:
                m =  [i[1]["F1score"] for i in data[approach] if param in i[0]] # and float(i[0].replace("char_wb","charwb").split("_")[4]) < 0.3
                Fscores[param] = Fscores[param] + m

    #plotpy graph
    
    #check if there is no len issue
    #lenght = len(Fscores["tok"]["1"])
    #for k1,v1 in Fscores.items():
    #    for k2,v2 in v1.items():
    #        if len(v2) != lenght:
    #            print('ARG')

    g_len = len(Fscores["char"])
    x = []
    for param in param_thresholds:
        x = x + [param for i in range(g_len)]

    fig = go.Figure()

    for param in param_thresholds:
        fig.add_trace(go.Box(
            y=Fscores[param],
            name=param,
            #marker_color='#B2BEB5',
            boxpoints=False
        ))

    fig.update_layout(
        showlegend=False,
        font=dict(
            #family="Courier New, monospace",
            size=21,
        ),
    )


    fig.update_layout(width=1500)

    fig.write_image("logs/boxplot.png")

paramStudy()