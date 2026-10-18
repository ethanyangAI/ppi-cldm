#!/bin/bash
#SBATCH --job-name=t9-engineering-pilot
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --array=0-1%1
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark
#SBATCH --output=/lustre/users/u21111210118/projects/test9/logs/engineering-pilot-v5-%A_%a.out
set -euo pipefail
export PS1="${PS1:-}"
export PYTHONNOUSERSITE=1
unset PYTHONPATH
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=4
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/tmp/pilot-${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
TASK_ID=$(/lustre/users/u21111210118/projects/test9/env/core/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1]))["tasks"][int(sys.argv[2])]["task_id"])' /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/engineering_pilot/plan_v5/frozen_plan.json "$SLURM_ARRAY_TASK_ID")
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py run-task --plan /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/engineering_pilot/plan_v5/frozen_plan.json --plan-sha256 8b47944f5ba5662c2e382b2f6b52553760d95a0ed678ea4a4c9d44396cb038bb --task-id "$TASK_ID" --output-dir /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/engineering_pilot/runs_v5/${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}
