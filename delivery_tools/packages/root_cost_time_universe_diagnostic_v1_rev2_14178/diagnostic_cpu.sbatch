#!/bin/bash
#SBATCH --job-name=test9_root_cost_universe_diagnostic
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/root-cost-universe-diagnostic-%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/root-cost-universe-diagnostic-%j.err
set -euo pipefail
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
unset PYTHONPATH
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python -B /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_cost_time_universe_diagnostic_v1_rev2_14178/diagnostic.py --out "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/root_cost_universe_diagnostic_${SLURM_JOB_ID}"
