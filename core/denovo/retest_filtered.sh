#!/bin/bash
#SBATCH --partition=a100
#SBATCH --gres=gpu:1
#SBATCH --job-name=retest_filter
#SBATCH --output=%j_retest.log
#SBATCH --error=%j_retest.err
#SBATCH --time=2:00:00
source /home/huangym/anaconda/conda/etc/profile.d/conda.sh
conda activate ppi_env
cd ~/zjy/ppi_gen_project/core/denovo
python ppi_pipeline_universal.py --target MDM2_TP53 --n 50
