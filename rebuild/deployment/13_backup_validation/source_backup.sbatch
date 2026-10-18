#!/bin/bash
#SBATCH -J t9-source-backup
#SBATCH -p interactive
#SBATCH -c 2
#SBATCH --mem=6G
#SBATCH -t 00:30:00
#SBATCH -o /lustre/users/u21111210118/projects/test9/steps/13_backup_validation/logs/source_%j.log
set -euo pipefail
export PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 PS1="${PS1:-}"
unset PYTHONPATH
export PS1="${PS1:-}"
source /opt/app/conda/etc/profile.d/conda.sh
conda activate /lustre/users/u21111210118/projects/test9/env/core
python /lustre/users/u21111210118/projects/test9/steps/13_backup_validation/code/source_backup.py

