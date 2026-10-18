#!/usr/bin/env bash
#SBATCH --job-name=t9-runtime-freeze
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=00:30:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/finalize_%j.out
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9;S="$R/steps/21_method_runtime";O="$S/runs/finalize_$SLURM_JOB_ID/outputs"
mkdir -p "$O"
export TMPDIR="$S/work" XDG_CACHE_HOME="$R/env/cache" PIP_CACHE_DIR="$R/env/cache/pip" CONDA_PKGS_DIRS="$R/env/pkgs" JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES="" PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
source /opt/app/conda/etc/profile.d/conda.sh
conda activate "$R/env/core"
python -m py_compile "$R/source/rebuild/benchmark_runtime.py" "$S/code/test_runtime_contracts.py"
python "$S/code/test_runtime_contracts.py" > "$O/tests.txt" 2>&1
source "$S/code/rfd_env.sh"
export CUDA_VISIBLE_DEVICES=""
python "$S/code/finalize_runtime.py" rfd
source "$S/code/bindcraft_env.sh"
export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=""
python "$S/code/finalize_runtime.py" bindcraft

