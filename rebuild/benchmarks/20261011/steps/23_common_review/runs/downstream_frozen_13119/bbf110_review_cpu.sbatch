#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:45:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/23_common_review
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_%j.log
set -euo pipefail
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=""
unset PYTHONPATH
/lustre/users/u21111210118/projects/test9/env/core/bin/python /lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/code/audit_bbf_workers_v2.py --plan /lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061/plan.json --raw-root /lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/runs/bbf_launch_13067/raw --raw-root /lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw --out /lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_${SLURM_JOB_ID}/worker_audit.json --require-all --score-and-verify
