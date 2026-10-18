#!/usr/bin/env bash
#SBATCH --job-name=t9-v7-bc-readiness
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=00:20:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/current_bc_readiness_%j.out
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9
S="$R/steps/21_method_runtime"
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=1 TMPDIR="$S/work" XDG_CACHE_HOME="$R/env/cache" CONDA_PKGS_DIRS="$R/env/pkgs" PIP_CACHE_DIR="$R/env/cache/pip"
unset PYTHONPATH
source "$R/steps/22_matched_benchmark/settings/pilot_v7/source/bindcraft_env.sh"
export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=""
O="$S/runs/current_bc_readiness_$SLURM_JOB_ID/outputs"
mkdir -p "$O"
python "$R/steps/22_matched_benchmark/settings/pilot_v7/source/benchmark_runtime.py" probe --label bindcraft --output "$O/import_probe.json"
python "$R/steps/22_matched_benchmark/settings/pilot_v7/source/current_bc_readiness.py"

