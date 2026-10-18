#!/bin/bash
#SBATCH --job-name=test9_final_composer_source_contexts_v7
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final_delivery_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final_delivery_%j.err
set -euo pipefail
unset PYTHONPATH
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python -B /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_delivery_complete_from18110_v4/delivery_driver.py "$@"
