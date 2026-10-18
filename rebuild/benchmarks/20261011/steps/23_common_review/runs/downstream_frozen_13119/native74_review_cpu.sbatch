#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:45:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/23_common_review
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/native74_review_%j.log
set -euo pipefail
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=""
unset PYTHONPATH
/lustre/users/u21111210118/projects/test9/env/core/bin/python /lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/code/native_review_pipeline_v2.py --plan /lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/native_controls_frozen_13051/inference_plan.json --analysis /lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/native_controls_frozen_13051/analysis_plan.json --membership /lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/native_controls_frozen_13051/membership.json --raw-root /lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/native_controls_frozen_13051/raw --raw-root /lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13106/native_index19/raw --out-dir /lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/native74_review_${SLURM_JOB_ID}
