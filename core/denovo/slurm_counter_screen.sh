#!/bin/bash
#SBATCH --job-name=ppi_cs
#SBATCH --partition=basic
#SBATCH --array=0-39
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=04:00:00
#SBATCH --output=/home/huangym/zjy/ppi_gen_project/core/denovo/logs/cs_%A_%a.out
#SBATCH --error=/home/huangym/zjy/ppi_gen_project/core/denovo/logs/cs_%A_%a.err

# Full counter-screening against 83 off-target receptors.
# Runs as a 40-task array job; each task handles ~15 molecules.
# Submit: sbatch slurm_counter_screen.sh

source /home/huangym/anaconda/conda/etc/profile.d/conda.sh
conda activate ppi_env

DENOVO=/home/huangym/zjy/ppi_gen_project/core/denovo

python "$DENOVO/full_counter_screen.py"

echo "=== Task $SLURM_ARRAY_TASK_ID done: $(date) ==="
