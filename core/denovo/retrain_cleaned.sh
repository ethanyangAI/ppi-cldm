#!/bin/bash
#SBATCH --partition=a100
#SBATCH --gres=gpu:1
#SBATCH --job-name=diff_cleaned
#SBATCH --output=%j_diff_cleaned.log
#SBATCH --error=%j_diff_cleaned.err
#SBATCH --time=48:00:00
source /home/huangym/anaconda/conda/etc/profile.d/conda.sh
conda activate ppi_env
cd ~/zjy/ppi_gen_project/core/denovo
python train_diffusion_large.py
