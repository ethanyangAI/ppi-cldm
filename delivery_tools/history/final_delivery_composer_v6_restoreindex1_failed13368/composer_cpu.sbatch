#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --job-name=ppi_final_composer_v6_restoreindex1
#SBATCH --time=04:00:00
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final-composer-%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final-composer-%j.err
set -euo pipefail
export PS1="" CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
export TMPDIR="$R/steps/24_benchmark_delivery/tmp/final_composer_v6_restoreindex1_$SLURM_JOB_ID"
mkdir -p "$TMPDIR"
ENTRY="$FINAL_COMPOSER_ENTRY"
test -n "$ENTRY"
exec "$R/env/core/bin/python" "$ENTRY" "$@"
