#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=00:30:00
#SBATCH --job-name=test9_review_technical_v2_1
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/23_common_review
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/23_common_review/logs/review_technical_v2_1_%j.log
set -euo pipefail
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=""
unset PYTHONPATH
/lustre/users/u21111210118/projects/test9/env/core/bin/python /lustre/users/u21111210118/projects/test9/steps/23_common_review/code/freeze_review_technical_v2_1.py
