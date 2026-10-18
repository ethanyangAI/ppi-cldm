#!/bin/bash
#SBATCH --job-name=ppi_native74_cache_cpu
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=12G
#SBATCH --time=01:00:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/native74-cache-%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/native74-cache-%j.err
set -euo pipefail
export PS1="${PS1:-}"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
MODE="${1:?mode required}"
case "$MODE" in catalog|contracts|bind) ;; *) exit 2 ;; esac
OUT="/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/native74_cache_${MODE}_${SLURM_JOB_ID}"
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/code/native74_cache_guard_v1/native74_cache_guard.py "$@" --out "$OUT"

