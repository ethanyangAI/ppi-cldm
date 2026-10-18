#!/bin/bash
#SBATCH --job-name=test9_bbf_source_diagnostic_v1
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=00:10:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/source_bbf_recorded_recovery_diagnostic_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/source_bbf_recorded_recovery_diagnostic_%j.err
set -euo pipefail
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
unset PYTHONPATH
ROOT=/lustre/users/u21111210118/projects/test9
"$ROOT/env/core/bin/python" "$ROOT/steps/24_benchmark_delivery/pending/source_bbf_recorded_recovery_diagnostic_v1/diagnostic.py"
