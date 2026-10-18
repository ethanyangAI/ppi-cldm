#!/bin/bash
#SBATCH --job-name=test9_generic_materialized_repair_v3
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9
#SBATCH --output=/lustre/users/u21111210118/projects/test9/logs/generic_runtime_repair_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/logs/generic_runtime_repair_%j.err
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9
PKG="$R/steps/24_benchmark_delivery/pending/generic_report_runtime_repair_v3"
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
unset PYTHONPATH
: "${1:?Explicit reviewed actual13281 materialization repair request required}"
export TMPDIR="$R/steps/24_benchmark_delivery/tmp/generic_runtime_repair_${SLURM_JOB_ID}"
mkdir -p "$TMPDIR"
exec "$R/env/core/bin/python" -B "$PKG/science13263_content_barrier.py" --request "$1" --out "$R/steps/24_benchmark_delivery/runs/generic_runtime_repair_${SLURM_JOB_ID}"
