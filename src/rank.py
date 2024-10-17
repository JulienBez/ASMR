from . import parameters
from .utils import *

def filterByRules(data):
    """"""
    new_data = []
    for entry in data:
        filtered = False
        for layer, rules in parameters.layers.items():
            if max(entry["similarities"][layer]) >= rules["min"] and max(entry["similarities"][layer]) <= rules["max"]:
                pass
            else:
                filtered = True
        if filtered == False:
            new_data.append(entry)
    return new_data


def filterLines(lines):
    """"""
    new_lines = [line for line in lines if line["meanLayer"] >= parameters.minSim and line["meanLayer"] <= parameters.maxSim and line["frequence"] >= parameters.minFreq]
    if parameters.nrow != 0:
        new_lines = new_lines[:parameters.nrow]
    return new_lines


def createTexTable(lines,path,kept=["shown","meanLayer","frequence"]):
    """write a latex table from a dict of lines"""
    tex_lines = []
    for line in lines:
        line["meanLayer"] = round(line["meanLayer"],2)
        line["shown"] = f"\\<{line['shown']}>"
        tex_lines.append([str(v) for k,v in line.items() if k in kept])
    tex_lines.insert(0,kept)
    tex_lines_write = "\n".join([" & ".join(tl)+"\\\\" for tl in tex_lines])
    with open(path,"w", encoding="utf-8") as f:
        f.write(tex_lines_write)

   
def rank(path):
    """rank sents of a json (path) and create csv files containing our ranking"""
    
    data = filterByRules(openJson(path))
    
    if len(data) > 0:
        new_data_path = f"output/{parameters.NAMEPATH}/ranking/" + "".join(x for x in data[0]["paired_with"]["seed"].replace(" ","_") if x.isalnum() or x == "_") #seed
        createFolders(new_data_path)
        
    lines = []
    for entry in data:
        for i in range(len(entry["alignments"])):
            
            line = {
				"compare":{
					"shown":" ".join(entry["commonSegments"]["TOK"][i]),
					"meanLayer":entry["similarities"]["meanLayer"][i], 
				},
				"add":{
					"frequence":1,
					"sent_ids":[entry["metadata"]["id"]]
				}
			}
            
            for layer,_ in parameters.layers.items():
                line["compare"][layer] = " ".join(entry["commonSegments"][layer][i])
                line["compare"][f"{layer}_cos"] = entry["similarities"][layer][i]
        
        lines.append(line)

    new_lines = []
    for line in lines:
        
        found = False
        for i,nl in enumerate(new_lines):
            
            if line["compare"] == nl["compare"]:
                found = True
                
                new_lines[i]["add"]["frequence"] += 1
                new_lines[i]["add"]["sent_ids"] = new_lines[i]["add"]["sent_ids"] + line["add"]["sent_ids"] #set those sents and rework freq count !!!
                
        if found == False:
            new_lines.append(line)
    
    new_lines = [{**l["compare"],**l["add"]} for l in new_lines]
    sorted_lines = filterLines(sorted(new_lines, key=lambda x: x["meanLayer"],reverse=True))

    if len(sorted_lines) > 0:
        df = pd.DataFrame.from_records(sorted_lines)
        filename = "_".join([f"{k}sim{v['min']}-{v['max']}" for k,v in parameters.layers.items()]) + ".csv"
        df.to_csv(f"{new_data_path}/{filename}",sep="\t",encoding="utf-8",index=False)
        
        if parameters.latex:
            filenameTex = filename.replace(".csv",".tex")
            createTexTable(sorted_lines,f"{new_data_path}/{filenameTex}")


def rankAll():
    """process rankSegments function on every file in 'sorted/' folder"""
    createFolders(f"output/{parameters.NAMEPATH}/ranking")
    for path in tqdm(glob.glob(f"output/{parameters.NAMEPATH}/sorted/*.json")):
        rank(path)
    print("")
