#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --mem=16G
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --job-name=test9_final_composer_source_contexts_contracts_v7
#SBATCH --time=00:30:00
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final-composer-contracts-%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final-composer-contracts-%j.err
set -euo pipefail
export PS1="" CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
export TMPDIR="$R/steps/24_benchmark_delivery/tmp/final_composer_finite_source_context_v7_$SLURM_JOB_ID"
mkdir -p "$TMPDIR"
exec "$R/env/core/bin/python" -B "$R/steps/24_benchmark_delivery/pending/final_delivery_composer_v7_finite_source_context1_fix3/composer_bootstrap.py"
