#!/bin/bash
#SBATCH --job-name=ppi_v4_unexecuted_history
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:05:00
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/logs/engineering_v4_history_%j.log
set -euo pipefail
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
/lustre/users/u21111210118/projects/test9/env/core/bin/python -u /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/register_engineering_v4_unexecuted.py
