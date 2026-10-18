#!/bin/bash
#SBATCH --job-name=test9_final_source_plan_pin_capture_v1_rev1
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final-source-pin-rev1-%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final-source-pin-rev1-%j.err
set -euo pipefail
export CUDA_VISIBLE_DEVICES=""
export JAX_PLATFORMS=cpu
export PYTHONNOUSERSITE=1
export PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
unset PYTHONPATH
test "${1:-}" = capture -o "${1:-}" = plan
entry="${FINAL_SOURCE_PLAN_PIN_CAPTURE_ENTRY:-/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_pin_capture_v1_rev1/capture.py}"
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python -B "$entry" "$@"
