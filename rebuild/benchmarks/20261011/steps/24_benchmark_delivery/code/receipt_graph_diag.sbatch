#!/bin/bash
#SBATCH --job-name=ppi_receipt_chain_diag
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:15:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/receipt_graph_diag_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/receipt_graph_diag_%j.err
set -euo pipefail
export PS1="${PS1:-}"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/receipt_graph_${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
export NATIVE_CLOSURE_TEST_OUTPUT=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/receipt_graph_${SLURM_JOB_ID}
mkdir -p "$NATIVE_CLOSURE_TEST_OUTPUT"
/lustre/users/u21111210118/projects/test9/env/core/bin/python /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/code/receipt_chain_diagnostic_v2.py

