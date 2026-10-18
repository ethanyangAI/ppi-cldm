#!/bin/bash
#SBATCH --job-name=test9_final_source_materialized_v3
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final_source_materialized_v3_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final_source_materialized_v3_%j.err
set -euo pipefail
MODE="${1:-software}"
[[ "$MODE" == software || "$MODE" == audit ]]
export PS1="${PS1:-}"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
unset PYTHONPATH
TASK_ROOT=/lustre/users/u21111210118/projects/test9
TASK_PACKAGE=$TASK_ROOT/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix1
export TMPDIR=$TASK_ROOT/steps/24_benchmark_delivery/tmp/final_source_materialized_v3_${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
if [[ "$MODE" == software ]]; then
 "$TASK_ROOT/env/core/bin/python" "$TASK_PACKAGE/final_source_closure.py" software --out "$TASK_ROOT/steps/24_benchmark_delivery/runs/final_source_materialized_software_${SLURM_JOB_ID}"
else
 [[ "$#" -eq 2 ]]
 "$TASK_ROOT/env/core/bin/python" "$TASK_PACKAGE/final_source_context_adapter.py" --request "$2" --out "$TASK_ROOT/steps/24_benchmark_delivery/runs/final_source_materialized_audit_${SLURM_JOB_ID}"
fi
