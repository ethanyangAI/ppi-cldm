#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=interactive
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --job-name=test9_screen_prepare
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/20_screening_improvement/logs/prepare_%j.log
set -euo pipefail
export PS1="${PS1:-}"
export PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
"$R/env/core/bin/python" -m py_compile "$R/source/rebuild/screening_transfer.py"
"$R/env/core/bin/python" "$R/source/rebuild/screening_transfer.py" test
"$R/env/core/bin/python" "$R/steps/20_screening_improvement/code/prepare.py"
