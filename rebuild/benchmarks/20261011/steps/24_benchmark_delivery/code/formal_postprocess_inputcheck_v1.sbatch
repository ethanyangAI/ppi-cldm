#!/bin/bash
#SBATCH --job-name=ppi_formal_inputcheck
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:15:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/formal_postprocess_inputcheck_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/formal_postprocess_inputcheck_%j.err
set -euo pipefail
export PS1="${PS1:-}"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
FROZEN=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/formal_postprocess_inputcheck_${SLURM_JOB_ID}
mkdir -p "$FROZEN"
cp /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/code/formal_postprocess_inputcheck_v1.py "$FROZEN/"
chmod -R a-w "$FROZEN"
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python "$FROZEN/formal_postprocess_inputcheck_v1.py"

