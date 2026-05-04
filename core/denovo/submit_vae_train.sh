#!/bin/bash
#SBATCH --job-name=gruvae_train
#SBATCH --partition=a100
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=/home/huangym/zjy/ppi_gen_project/core/denovo/logs/train_%j.out
#SBATCH --error=/home/huangym/zjy/ppi_gen_project/core/denovo/logs/train_%j.err

set -e
mkdir -p /home/huangym/zjy/ppi_gen_project/core/denovo/logs

echo "=== GRU-VAE Training ==="
echo "Host: $(hostname)"
echo "Time: $(date)"
nvidia-smi | head -12

source /home/huangym/anaconda/conda/etc/profile.d/conda.sh
conda activate ppi_env

cd /home/huangym/zjy/ppi_gen_project/core/denovo
python train_vae.py

echo "=== Done: $(date) ==="
