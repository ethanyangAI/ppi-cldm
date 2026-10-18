#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=08:00:00
#SBATCH --job-name=test9_common_cpu
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/23_common_review/logs/cpu_%j.log
set -euo pipefail
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=""
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
"$R/env/core/bin/python" "$R/source/rebuild/benchmark_common_review.py" "$@"

