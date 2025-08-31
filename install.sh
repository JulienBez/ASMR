#!/bin/bash

#SBATCH --job-name=install
#SBATCH --output=install_%j.out
#SBATCH --mail-user=sacado@marceau-h.fr
#SBATCH --mail-type=ALL
#SBATCH --partition=std
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=32G
#SBATCH --time=00-00:30:00

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

module purge

module load conda/2024.02

conda create -y --prefix /home/bezancoj/test_install2 biopython scikit-learn pandas tqdm matplotlib sentence-transformers conllu python-levenshtein python-bidi arabic-reshaper -c mpcabd -c conda-forge -c anaconda

source activate /home/bezancoj/test_install2

which python

exit 0