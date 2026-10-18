#!/bin/bash
#SBATCH --job-name=test9_controller_metadata_amendment
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:05:00
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/logs/controller_metadata_amendment_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/logs/controller_metadata_amendment_%j.err
set -euo pipefail
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
/lustre/users/u21111210118/projects/test9/env/core/bin/python -I -B /lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/pending/controller_metadata_amendment_v1/amendment.py
