#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/23_common_review
#SBATCH --array=18-18%1
#SBATCH --job-name=test9_native18_allocation_v2
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/23_common_review/engineering_history/native_index18_20261011/logs/native_%A_%a.log
set -euo pipefail
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
INDEX="${SLURM_ARRAY_TASK_ID:?}"
PLAN=/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/native_controls_frozen_13051/inference_plan.json
CODE=/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/native_common_13051/code
ENGINE=$("$R/env/core/bin/python" -c 'import json,sys;print(json.load(open(sys.argv[1]))["jobs"][int(sys.argv[2])]["engine"])' "$PLAN" "$INDEX")
if [[ "$ENGINE" == af2 ]]; then source "$CODE/runtime_entries/af2_inference_env.sh"; elif [[ "$ENGINE" != boltz ]]; then exit 2; fi
"$R/env/core/bin/python" /lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13106/code/common_allocation_v2.py worker --plan "$PLAN" --index "$INDEX" --out /lustre/users/u21111210118/projects/test9/steps/23_common_review/engineering_history/native_index18_20261011/raw

