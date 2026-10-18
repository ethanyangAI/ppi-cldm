#!/bin/bash
#SBATCH --job-name=test9_native_physical_preflight_v3
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=04:00:00
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/logs/physical_preflight_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/logs/physical_preflight_%j.err
set -euo pipefail
cd /lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/tmp/physical_v3_${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
/lustre/users/u21111210118/projects/test9/env/core/bin/python -B /lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/pending/physical_gate_v3/physical_preflight_cpu.py --request "${1:?Exact reviewed actual generic/runtime/materialization request required}"
