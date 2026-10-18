#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --job-name=test9_sync_accepted
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/20_screening_improvement/logs/sync_%j.log
set -euo pipefail
export PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES="" PS1="${PS1:-}"
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
"$R/env/core/bin/python" "$R/steps/20_screening_improvement/code/sync_pointer.py"
