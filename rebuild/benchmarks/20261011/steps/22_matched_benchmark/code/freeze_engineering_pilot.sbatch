#!/bin/bash
#SBATCH --job-name=t9-freeze-pilot
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark
#SBATCH --output=/lustre/users/u21111210118/projects/test9/logs/freeze-pilot-%j.out
set -euo pipefail
export PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/tmp/freeze-pilot-${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/freeze_engineering_pilot.py

