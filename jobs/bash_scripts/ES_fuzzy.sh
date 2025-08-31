#!/bin/sh

#SBATCH --job-name=ES_PARSEME_ASMR
#SBATCH --output=ES_PARSEME_ASMR_%j.out
#SBATCH --mail-user=julienbesancon@gmail.com
#SBATCH --mail-type=ALL
#SBATCH --partition=std
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=16G
#SBATCH --time=00-15:00:00

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

module purge

module load conda/2024.02

source activate /home/bezancoj/test_install2

cd /home/bezancoj/ASMRPARSEME

python main.py -L ES -S fuzzy -smTE

exit 0
