#!/usr/bin/env bash
#SBATCH --job-name=t9-runtime-delivery
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:05:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/delivery_%j.out
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 TMPDIR="$R/steps/21_method_runtime/work"
unset PYTHONPATH
source /opt/app/conda/etc/profile.d/conda.sh
conda activate "$R/env/core"
python "$R/steps/21_method_runtime/code/runtime_delivery.py"

