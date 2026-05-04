#!/bin/bash
#SBATCH --job-name=ppi_full
#SBATCH --partition=a100
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/home/huangym/zjy/ppi_gen_project/core/denovo/logs/full_%j.out
#SBATCH --error=/home/huangym/zjy/ppi_gen_project/core/denovo/logs/full_%j.err

# Generation + docking + counter-screening in a single job.
# Usage:
#   sbatch slurm_full_pipeline.sh
#   TARGET=BCL2_BAX N_MOLS=200 CS_TOP=50 sbatch slurm_full_pipeline.sh

TARGET="${TARGET:-MDM2_TP53}"
N_MOLS="${N_MOLS:-100}"
CS_TOP="${CS_TOP:-30}"

source /home/huangym/anaconda/conda/etc/profile.d/conda.sh
conda activate ppi_env

DENOVO=/home/huangym/zjy/ppi_gen_project/core/denovo

python "$DENOVO/ppi_pipeline_universal.py" \
    --target "$TARGET" \
    --n "$N_MOLS" \
    --vae vae_ppi.pt \
    --counter_screen \
    --cs_top_n "$CS_TOP" \
    --cs_workers 4

echo "=== Done: $(date) ==="
