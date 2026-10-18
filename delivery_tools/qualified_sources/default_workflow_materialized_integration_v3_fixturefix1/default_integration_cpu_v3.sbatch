#!/bin/bash
#SBATCH --job-name=test9_default_materialized_integration_v3
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/default_materialized_integration_v3_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/default_materialized_integration_v3_%j.err
set -euo pipefail
MODE="${1:?software or apply required}"
LIBRARY_ACCEPTANCE="${2:?Actual readonly finalsource library software acceptance required}"
[[ "$MODE" == software || "$MODE" == apply ]]
export PS1="${PS1:-}"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
unset PYTHONPATH
TASK_ROOT=/lustre/users/u21111210118/projects/test9
TASK_PACKAGE=$TASK_ROOT/steps/24_benchmark_delivery/pending/default_workflow_materialized_integration_v3_fixturefix1
export TMPDIR=$TASK_ROOT/steps/24_benchmark_delivery/tmp/default_materialized_integration_v3_${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
PYTHON=$TASK_ROOT/env/core/bin/python
if [[ "$MODE" == software ]]; then
 [[ "$#" -eq 2 ]]
 "$PYTHON" -B "$TASK_PACKAGE/integrate_default_workflow_v3.py" software --library-acceptance "$LIBRARY_ACCEPTANCE" --out "$TASK_ROOT/steps/24_benchmark_delivery/runs/default_materialized_integration_software_${SLURM_JOB_ID}" --freeze "$TASK_ROOT/steps/24_benchmark_delivery/frozen/default_workflow_materialized_integration_v3_${SLURM_JOB_ID}/code"
else
 [[ "$#" -eq 4 ]]
 "$PYTHON" -B "$TASK_PACKAGE/integrate_default_workflow_v3.py" dispatch --library-acceptance "$LIBRARY_ACCEPTANCE" --request "$3" --software-acceptance "$4" --out "$TASK_ROOT/steps/24_benchmark_delivery/runs/default_materialized_integration_${SLURM_JOB_ID}"
fi
