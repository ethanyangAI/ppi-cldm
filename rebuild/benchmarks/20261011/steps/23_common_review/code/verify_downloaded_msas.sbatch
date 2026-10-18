#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=00:20:00
#SBATCH --job-name=test9_msa_content
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/23_common_review/logs/msa_content_%j.log
set -euo pipefail
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=""
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
"$R/env/core/bin/python" "$R/source/rebuild/benchmark_common_review.py" test --out "$R/steps/23_common_review/outputs/tests_${SLURM_JOB_ID}.json"
"$R/env/core/bin/python" "$R/steps/23_common_review/code/verify_downloaded_msas.py"
