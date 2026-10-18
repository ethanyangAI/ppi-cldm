#!/bin/bash
#SBATCH -J t9-physics
#SBATCH -p interactive
#SBATCH -c 1
#SBATCH --mem=6G
#SBATCH -t 04:00:00
#SBATCH -o /lustre/users/u21111210118/projects/test9/steps/12_physics_reassessment/logs/physics_%A_%a.log
set -euo pipefail
export PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/12_physics_reassessment/work
export PS1="${PS1:-}"
source /opt/app/conda/etc/profile.d/conda.sh
conda activate /lustre/users/u21111210118/projects/test9/env/physics
srun --cpu-bind=cores python /lustre/users/u21111210118/projects/test9/source/rebuild/physics_reassessment_worker.py "$1" "$SLURM_ARRAY_TASK_ID" "$2/outputs/task_$SLURM_ARRAY_TASK_ID"

