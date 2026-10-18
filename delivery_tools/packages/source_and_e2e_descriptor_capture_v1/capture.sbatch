#!/bin/bash
#SBATCH --job-name=test9_source_e2e_descriptors
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:05:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/source_e2e_descriptor_capture_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/source_e2e_descriptor_capture_%j.err
set -euo pipefail
export CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
unset PYTHONPATH
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python -I -B /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/source_and_e2e_descriptor_capture_v1/capture.py
