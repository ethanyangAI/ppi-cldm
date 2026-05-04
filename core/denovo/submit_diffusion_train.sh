#!/bin/bash
#SBATCH --job-name=cldm_train
#SBATCH --partition=a100
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=06:00:00
#SBATCH --output=/home/huangym/zjy/ppi_gen_project/core/denovo/logs/diffusion_%j.out
#SBATCH --error=/home/huangym/zjy/ppi_gen_project/core/denovo/logs/diffusion_%j.err

set -e
echo "=== Diffusion Model Training ==="
echo "Host: $(hostname) | Time: $(date)"
nvidia-smi | head -8

source /home/huangym/anaconda/conda/etc/profile.d/conda.sh
conda activate ppi_env

cd /home/huangym/zjy/ppi_gen_project/core/denovo
python train_diffusion.py

echo "=== Done: $(date) ==="
