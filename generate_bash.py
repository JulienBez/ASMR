from src.utils import *

# This script will generate one bash script per language.
# Those bash scripts are meant to be run on SACADO

deleteFolderContent("jobs")
createFolders("jobs/bash_scripts")
all_scripts = {"exact":[],"fuzzy":[],"combined":[]}
all_scripts_format = set()

languages = set()
for path in glob.glob("data/*/"):
    languages.add(path.split("/")[1])

for seg in ["exact","fuzzy","combined"]:
    for lang in languages:

        bash_command = f"""\
#!/bin/sh

#SBATCH --job-name={lang}_PARSEME_ASMR
#SBATCH --output={lang}_PARSEME_ASMR_%j.out
#SBATCH --mail-user=julienbesancon@gmail.com
#SBATCH --mail-type=ALL
#SBATCH --partition=std
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=16G
#SBATCH --time=00-15:00:00

export OMP_NUM_THREADS=${{SLURM_CPUS_PER_TASK}}

module purge

module load conda/2024.02

source activate /home/bezancoj/test_install2

cd /home/bezancoj/ASMRPARSEME

python main.py -L {lang} -S {seg} -smTE

exit 0
"""
        
        bash_command_format = f"""\
#!/bin/sh

#SBATCH --job-name={lang}_PARSEME_ASMR
#SBATCH --output={lang}_PARSEME_ASMR_%j.out
#SBATCH --mail-user=julienbesancon@gmail.com
#SBATCH --mail-type=ALL
#SBATCH --partition=std
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=16G
#SBATCH --time=00-5:00:00

export OMP_NUM_THREADS=${{SLURM_CPUS_PER_TASK}}

module purge

module load conda/2024.02

source activate /home/bezancoj/test_install2

cd /home/bezancoj/ASMRPARSEME

python main.py -L {lang} -S {seg} -Fpa

exit 0
"""

        all_scripts[seg].append("sbatch " + f"bash_scripts/{lang}_{seg}.sh")
        all_scripts_format.add("sbatch " + f"bash_scripts/{lang}_format.sh")

        writeFile(f"jobs/bash_scripts/{lang}_{seg}.sh",bash_command)
        writeFile(f"jobs/bash_scripts/{lang}_format.sh",bash_command_format)


for seg in ["exact","fuzzy","combined"]:
    writeFile(f"jobs/run_{seg}.sh","#!/bin/bash \n" + "\n".join(all_scripts[seg]))

writeFile(f"jobs/run_format.sh","#!/bin/bash \n" + "\n".join(list(all_scripts_format)))

bash_command_rank = f"""\
#!/bin/sh

#SBATCH --job-name={lang}_PARSEME_ASMR
#SBATCH --output={lang}_PARSEME_ASMR_%j.out
#SBATCH --mail-user=julienbesancon@gmail.com
#SBATCH --mail-type=ALL
#SBATCH --partition=std
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=16G
#SBATCH --time=00-5:00:00

export OMP_NUM_THREADS=${{SLURM_CPUS_PER_TASK}}

module purge

module load conda/2024.02

source activate /home/bezancoj/test_install2

cd /home/bezancoj/ASMRPARSEME

python main.py --ranking_parseme

exit 0
"""

writeFile(f"jobs/run_ranking.sh",bash_command_rank)

