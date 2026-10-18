#!/bin/bash
#SBATCH --job-name=ppi_13175_actual_audit
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:20:00
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/logs/engineering13175_accounting_%j.log
set -euo pipefail
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
/lustre/users/u21111210118/projects/test9/env/core/bin/python -u /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/audit_engineering_actual_array.py --plan /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/engineering_pilot/plan_v5/frozen_plan.json --run-root /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/engineering_pilot/runs_v5 --array-job-id 13175 --out /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/engineering13175_accounting_${SLURM_JOB_ID}

