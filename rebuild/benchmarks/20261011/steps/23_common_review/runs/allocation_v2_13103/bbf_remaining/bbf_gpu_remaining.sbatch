#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/23_common_review
#SBATCH --array=1-21%1
#SBATCH --job-name=test9_bbf_remaining_v4_guard
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/logs/bbf_%A_%a.log
set -euo pipefail
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
INDEX="${SLURM_ARRAY_TASK_ID:?}"
PLAN=/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061/plan.json
JOBKEY=$("$R/env/core/bin/python" -c 'import json,sys;print(json.load(open(sys.argv[1]))["jobs"][int(sys.argv[2])]["job_key"])' "$PLAN" "$INDEX")
RAWDIR="/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/$JOBKEY"
if [[ -e "$RAWDIR" ]]; then exit 2; fi
source /lustre/users/u21111210118/projects/test9/steps/21_method_runtime/frozen/bbf_backend_v2/bindcraft_env.sh
python /lustre/users/u21111210118/projects/test9/steps/21_method_runtime/frozen/bbf_backend_v2/bbf_feature_backend.py predict --plan "$PLAN" --job-key "$JOBKEY" --output-dir "$RAWDIR" --features-manifest /lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061/feature_manifest.json --guard-source /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py --expected-gpu-name 'NVIDIA A100-PCIE-40GB'
cp --no-clobber /lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/worker_reference_receipts.json "$RAWDIR/worker_reference_receipts.json"
