#!/bin/bash
#SBATCH --job-name=test9_paired_formal_generation
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=3
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --array=0-27%2
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark
#SBATCH --output=/lustre/users/u21111210118/projects/test9/logs/formal-generation-%A_%a.out
set -euo pipefail
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/tmp/formal-${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
TASK_ID=$(/lustre/users/u21111210118/projects/test9/env/core/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1]))["tasks"][int(sys.argv[2])]["task_id"])' /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/formal_freeze_13257/plan/frozen_plan.json "$SLURM_ARRAY_TASK_ID")
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py run-task --plan /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/formal_freeze_13257/plan/frozen_plan.json --plan-sha256 e913d1bbccd531bf88a73f6ba60e8a0de85bb03ad8bcd3455d8952ca4effe0b6 --task-id "$TASK_ID" --output-dir /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/formal_runs/${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}
