from src.utils import *
from src.process import *
from src.align import *
from src.segment import *
from src.measure import *
from src.rank import *
from src.metadata import *
from src.results import *

total = 0
total2 = 0
stats = {}
for path in glob.glob("output/FrUIT/sorted/*.json"):
    data = openJson(path)
    seen = []

    nb = 0#len([i for i in data if max(i["similarities"]["meanLayer"]) > 0.5])
    nb2 = 0
    for i in data:
        maxi = max([[j,i] for i,j in enumerate(i["similarities"]["meanLayer"])])
        if maxi[0] > 0.5:
            nb += 1
            if " ".join(i["commonSegments"]["TOK"][maxi[1]]) not in seen:
                nb2 += 1
                seen.append(" ".join(i["commonSegments"]["TOK"][maxi[1]]))

    stats[path] = [nb,nb2]
    total += nb
    total2 += nb2
writeJson("stats_UP.json",sorted([[j,i] for i,j in stats.items()],reverse=True))
print(total)
print(total2)

#55,657 candidats
#7,482 formes uniques
#campagne d'annotation sur ces formes unique -> il faut au moins 20 formes unique par expression pour qu'elle soit annotable
#on ajoute ces tweets dans defricheur si ils y sont pas déjà

UP_stats = openJson("stats_UP.json")
UP2 = [i for i in UP_stats if i[0][1] >= 20]
writeJson("stats_UP_sorted.json",UP2)
print(len(UP2))

#il reste 36 expressions avec au moins 20 formes différentes trouvées:
# > pour chaque expression, on regarde jusqu'au top 50 candidats
# > faire papier UP sur ça + classif des expressions -> lesquelles ont donné des résultats, lesquelles ont rien donné