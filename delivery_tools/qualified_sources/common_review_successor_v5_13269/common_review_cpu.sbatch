#!/bin/bash
#SBATCH --job-name=ppi_common_successor_cpu
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/common-successor-%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/common-successor-%j.err
set -euo pipefail
export PS1="${PS1:-}" CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR="/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/common_successor_${SLURM_JOB_ID}"
mkdir -p "$TMPDIR"
MODE="${1:?contracts, preflight or finish required}"
R=/lustre/users/u21111210118/projects/test9
if [[ "$MODE" == contracts ]]; then
  exec "$R/env/core/bin/python" "$R/steps/24_benchmark_delivery/code/common_review_successor_v5/successor_bootstrap.py"
elif [[ "$MODE" == preflight || "$MODE" == finish ]]; then
  exec "$R/env/core/bin/python" "${COMMON_SUCCESSOR_ENTRY:?absolute accepted frozen successor entry required}" "$@"
else exit 2; fi
