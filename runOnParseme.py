import glob
import subprocess

languages = set()
for path in glob.glob("data/parseme_*.json"):
    languages.add(path.split("_")[-1].replace(".json",""))


for language in languages:

    print(f"Running on {language}...")

    with open("src/parameters.py",'r',encoding='utf-8') as f:
        parameters = f.readlines()

    target = f"\"parseme_1-2_{language}\""
    parameters[1] = f"NAMEPATH = {target}\n"

    with open('src/parameters.py','w',encoding='utf-8') as f:
        f.write("".join(parameters))

    subprocess.run([
        "python",
        "main.py",
        "-pasmr"
    ])