#!/bin/bash
#SBATCH --job-name=ppi_generate
#SBATCH --partition=a100
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=/home/huangym/zjy/ppi_gen_project/core/denovo/logs/gen_%j.out
#SBATCH --error=/home/huangym/zjy/ppi_gen_project/core/denovo/logs/gen_%j.err

# Usage:
#   sbatch slurm_generate.sh                          # default: MDM2_TP53, 100 molecules
#   TARGET=KRAS_SOS1 sbatch slurm_generate.sh
#   TARGET=MENIN_MLL N_MOLS=200 sbatch slurm_generate.sh

TARGET="${TARGET:-MDM2_TP53}"
N_MOLS="${N_MOLS:-100}"

source /home/huangym/anaconda/conda/etc/profile.d/conda.sh
conda activate ppi_env

DENOVO=/home/huangym/zjy/ppi_gen_project/core/denovo

python "$DENOVO/ppi_pipeline_universal.py" \
    --target "$TARGET" \
    --n "$N_MOLS" \
    --vae vae_ppi.pt

echo "=== Done: $(date) ==="
