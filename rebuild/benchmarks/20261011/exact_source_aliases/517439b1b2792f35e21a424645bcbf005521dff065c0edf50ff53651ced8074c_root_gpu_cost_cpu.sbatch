#!/bin/bash
#SBATCH --job-name=ppi_root_gpu_cost_cpu
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/root-gpu-cost-%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/root-gpu-cost-%j.err
set -euo pipefail
export PS1="${PS1:-}" CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
export TMPDIR="$R/steps/24_benchmark_delivery/tmp/root_gpu_cost_${SLURM_JOB_ID}"
mkdir -p "$TMPDIR"
MODE="${1:?contracts, seal-ledger or audit required}"
shift
OUT="$R/steps/24_benchmark_delivery/runs/root_gpu_cost_${MODE}_${SLURM_JOB_ID}"
if [[ "$MODE" == contracts ]]; then
  test "$#" -eq 0
  exec "$R/env/core/bin/python" "$R/steps/24_benchmark_delivery/pending/root_gpu_cost_closure_v2/root_gpu_cost_audit.py" contracts --out "$OUT"
elif [[ "$MODE" == audit || "$MODE" == seal-ledger ]]; then
  exec "$R/env/core/bin/python" "${ROOT_GPU_COST_ENTRY:?absolute accepted frozen auditor entry required}" "$MODE" "$@" --out "$OUT"
else exit 2; fi
