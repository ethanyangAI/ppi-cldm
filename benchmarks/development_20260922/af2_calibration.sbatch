#!/usr/bin/env bash
#SBATCH --partition=8gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=06:30:00
set -euo pipefail
ROOT=/lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1 TMPDIR="$ROOT/cache/benchmark_tmp"
unset PYTHONPATH
source "/opt/app/conda/etc/profile.d/conda.sh"
conda activate "$ROOT/env/core"
ulimit -Sv "$((SLURM_MEM_PER_NODE * 1024))"
cd "$ROOT/source"
python -u benchmarks/development_20260922/launch_af2_calibration.py "$SLURM_ARRAY_TASK_ID"

