#!/bin/bash
#SBATCH --job-name=test9_common13423_metadata_amendment_v1
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/common13423-metadata-amendment-%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/common13423-metadata-amendment-%j.err
set -euo pipefail
export CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/common13423_metadata_amendment_${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/common_root_receipt_metadata_amendment_v1/amendment.py
