#!/usr/bin/env bash
#SBATCH --job-name=t9-runtime-inventory
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=interactive
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/inventory_%j.out
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9
S="$R/steps/21_method_runtime"
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=1 DGLBACKEND=pytorch
unset PYTHONPATH
export CONDA_PKGS_DIRS="$R/env/pkgs" PIP_CACHE_DIR="$R/env/cache/pip" TMPDIR="$S/work" XDG_CACHE_HOME="$R/env/cache"
mkdir -p "$S/runs/inventory_$SLURM_JOB_ID/outputs"
source /opt/app/conda/etc/profile.d/conda.sh
for LABEL in core rfd colabfold boltz physics; do
 conda activate "$R/env/$LABEL"
 python "$R/source/rebuild/benchmark_runtime.py" probe --label "$LABEL" --output "$S/runs/inventory_$SLURM_JOB_ID/outputs/$LABEL.json"
done
conda activate "$R/env/core"
python "$R/source/rebuild/benchmark_runtime.py" inventory --output "$S/runs/inventory_$SLURM_JOB_ID/outputs/inventory.json"
