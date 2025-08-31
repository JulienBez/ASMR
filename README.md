# PENSE-BÊTE

- Ajouter les fichiers PARSEME dans data (data/{langue}/*.cupt)
- déterminer TRAIN_DATA (train) et TEST_DATA (dev)
- tout convertir de .cupt en .json
- créer les fichiers de seeds selon TRAIN_DATA

- (anonymiser les verbes dans les seeds)
- process les fichiers TEST_DATA
- aligner les fichiers TEST_DATA
- segmenter les fichiers TEST_DATA
- mesurer les fichiers TEST_DATA

- pour chaque threshold, générer un fichier de résultats avec métriques de PARSEME
- récupérer les résultats de ces métriques pour savoir qu'elle est la meilleure

- on prend la meilleure run et on change TEST_DATA (test) afin de faire l'expérience avec cette meilleure run
- on recommence pour les 3 versions d'ASMR

En gros on utilise train pour les seeds. On utilise ensuite dev pour déterminer le meilleur threshold (on run pour chaque threshold le script d'évaluation de PARSEME). Enfin, on utilise ce threshold sur le test de PARSEME avec ASMR pour l'expérience.


- file_format_handler.py : transforme les cupt en ASMR et vice-versa + crée les fichiers de seeds selon TRAIN_DATA

# TODO : 

- on peut faire les runs sur train et dev, faire programme pour déterminer best run après et extraire les meilleurs params (meilleur threshold)
- retirer les LIMIT FOR TEST dans process.py

# PROCESS : 

- on commence avec combined et masked sur train/dev, si on voit que les résultats sont trop mauvais on fera sans masked sur combined, fuzzy et exact.
- on a pas run sur tout mais les résultats semblent trop mauvais, on passe à unmasked
- on fait train/dev sur unmasked avec toutes les langues
- pour chaque langue, on cherche les 10 meilleurs sets de paramètre pour chaque algo de matching
- on fait train/test sur unmasked avec toutes les langues sur ces 10 sets de paramètre
- enjoy :-)

# PROCESS UPDATED : 

- supprime output/

- parameters.py : TEST_DATA = "dev"
- ssh bezancoj@login.mesu.sorbonne-universite.fr
- cd jobs
- sbatch run_format.sh
- rm -rf *.out
- sbatch run_exact.sh
- rm -rf *.out
- sbatch run_fuzzy.sh
- rm -rf *.out
- sbatch run_combined.sh

- parameters.py : TEST_DATA = "test"
- ssh bezancoj@login.mesu.sorbonne-universite.fr
- cd jobs
- sbatch run_format.sh
- rm -rf *.out
- sbatch run_exact.sh
- rm -rf *.out
- sbatch run_fuzzy.sh
- rm -rf *.out
- sbatch run_combined.sh