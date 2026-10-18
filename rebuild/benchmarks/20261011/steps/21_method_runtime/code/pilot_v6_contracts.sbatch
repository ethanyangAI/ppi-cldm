#!/usr/bin/env bash
#SBATCH --job-name=t9-pilot-v6-contracts
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:20:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/pilot_v6_contracts_%j.out
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9
S="$R/steps/21_method_runtime"
O="$S/runs/pilot_v6_contracts_$SLURM_JOB_ID/outputs"
mkdir -p "$O"
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=1 TMPDIR="$S/work" XDG_CACHE_HOME="$R/env/cache" JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=""
unset PYTHONPATH
source "$S/code/bindcraft_env.sh"
export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=""
python -m py_compile "$R/source/rebuild/benchmark_runtime.py" "$S/code/test_runtime_contracts.py"
python "$S/code/test_runtime_contracts.py" > "$O/tests.txt" 2>&1
python "$S/code/pilot_v6_identity_acceptance.py"

