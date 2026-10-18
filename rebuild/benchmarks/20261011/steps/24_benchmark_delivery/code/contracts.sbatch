#!/bin/bash
#SBATCH --job-name=ppi_delivery_contracts
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:15:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/contracts_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/contracts_%j.err
set -euo pipefail
export PS1="${PS1:-}"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/contracts_${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
TASK_SNAPSHOT=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/source_snapshots/contracts_${SLURM_JOB_ID}
mkdir -p "$TASK_SNAPSHOT"
cp /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/code/*.py "$TASK_SNAPSHOT/"
cp /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/code/contracts.sbatch "$TASK_SNAPSHOT/"
chmod -R a-w "$TASK_SNAPSHOT"
/lustre/users/u21111210118/projects/test9/env/core/bin/python "$TASK_SNAPSHOT/test_delivery.py"
/lustre/users/u21111210118/projects/test9/env/core/bin/python /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/code/delivery_core.py source-audit --root /lustre/users/u21111210118/projects/test9 --out /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/contracts_${SLURM_JOB_ID}/source_inclusion.json

