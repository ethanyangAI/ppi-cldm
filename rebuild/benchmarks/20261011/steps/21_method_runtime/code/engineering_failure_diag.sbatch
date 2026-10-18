#!/usr/bin/env bash
#SBATCH --job-name=t9-pilot-failure-diag
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/pilot_failure_diag_%j.out
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 TMPDIR="$R/steps/21_method_runtime/work" CUDA_VISIBLE_DEVICES=""
unset PYTHONPATH
source /opt/app/conda/etc/profile.d/conda.sh
conda activate "$R/env/core"
python "$R/steps/21_method_runtime/code/engineering_failure_diag.py"

