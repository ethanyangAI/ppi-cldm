#!/bin/bash
#SBATCH --job-name=ppi_formal2_meta_contracts
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/logs/formal2_meta_contracts_%j.log
set -euo pipefail
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
/lustre/users/u21111210118/projects/test9/env/core/bin/python -u /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/test_formal_v2_driver.py

