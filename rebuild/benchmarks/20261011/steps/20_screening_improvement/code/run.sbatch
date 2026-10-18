#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=interactive
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=02:00:00
#SBATCH --job-name=test9_screen_transfer
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/20_screening_improvement/logs/run_%j.log
set -euo pipefail
export PS1="${PS1:-}"
export PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
"$R/env/core/bin/python" "$R/source/rebuild/screening_transfer.py" run "$R/steps/20_screening_improvement/inputs/preparation_receipt.json"
