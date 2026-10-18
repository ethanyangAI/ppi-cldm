#!/usr/bin/env bash
#SBATCH --partition=c02
#SBATCH --nodelist=c02n02
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=04:00:00
set -euo pipefail
ROOT=/lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1 TMPDIR="$ROOT/cache/benchmark_tmp"
unset PYTHONPATH
source "/opt/app/conda/etc/profile.d/conda.sh"
conda activate "$ROOT/env/core"
ulimit -Sv "$((SLURM_MEM_PER_NODE * 1024))"
cd "$ROOT/source"
srun --cpu-bind=cores python -u benchmarks/computational_strengthening_20260923/score.py "$SLURM_ARRAY_TASK_ID"

