#!/bin/bash
#SBATCH --job-name=test9_generic_design_guard_v2
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/generic_design_guard_v2_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/generic_design_guard_v2_%j.err
set -euo pipefail
[[ "$#" -eq 1 ]]
export PS1="${PS1:-}"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
unset PYTHONPATH
TASK_ROOT=/lustre/users/u21111210118/projects/test9
TASK_PACKAGE=$TASK_ROOT/steps/24_benchmark_delivery/pending/generic_design_qualification_v2
export TMPDIR=$TASK_ROOT/steps/24_benchmark_delivery/tmp/generic_design_guard_${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
"$TASK_ROOT/env/core/bin/python" "$TASK_PACKAGE/qualify_generic_design_cpu.py" --request "$1" --out "$TASK_ROOT/steps/24_benchmark_delivery/runs/generic_design_qualification_${SLURM_JOB_ID}"

