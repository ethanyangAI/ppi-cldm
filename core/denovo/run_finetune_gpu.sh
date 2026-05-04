#!/bin/bash
#SBATCH --partition=a100
#SBATCH --gres=gpu:1
#SBATCH --job-name=vae_large
#SBATCH --output=vae_large_%j.log
#SBATCH --time=02:00:00

source /home/huangym/anaconda/conda/etc/profile.d/conda.sh
conda activate ppi_env
cd ~/zjy/ppi_gen_project/core/denovo
python finetune_large_molecules.py
