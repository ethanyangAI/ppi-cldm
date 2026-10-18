#!/bin/bash
#SBATCH -J t9-physics-plan
#SBATCH -p interactive
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -t 00:15:00
#SBATCH -o /lustre/users/u21111210118/projects/test9/steps/12_physics_reassessment/logs/plan_%j.log
set -euo pipefail
export PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
export PS1="${PS1:-}"
source /opt/app/conda/etc/profile.d/conda.sh
conda activate /lustre/users/u21111210118/projects/test9/env/core
python /lustre/users/u21111210118/projects/test9/steps/12_physics_reassessment/code/prepare.py

