#!/usr/bin/env bash
#SBATCH --job-name=t9-native-collector-freeze
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:05:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/native_workflow_collectors_%j.out
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 TMPDIR="$R/steps/21_method_runtime/work"
unset PYTHONPATH
source "$R/steps/22_matched_benchmark/settings/pilot_v8/source/bindcraft_env.sh"
export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=""
python "$R/steps/21_method_runtime/code/freeze_native_collectors.py"

