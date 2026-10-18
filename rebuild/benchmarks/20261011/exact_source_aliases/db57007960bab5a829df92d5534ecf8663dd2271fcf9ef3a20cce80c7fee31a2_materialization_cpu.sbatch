#!/bin/bash
#SBATCH --job-name=test9_rfd_cache_materialization_cpu
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/rfd-cache-materialization-%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/rfd-cache-materialization-%j.err
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9
source "$R/steps/22_matched_benchmark/settings/pilot_v8/source/rfd_env.sh"
export PS1="${PS1:-}" CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
unset PYTHONPATH
F="$R/steps/24_benchmark_delivery/frozen/rfd_cache_materialization_v2_${SLURM_JOB_ID}/code"
export TMPDIR="$R/steps/24_benchmark_delivery/tmp/rfd_cache_materialization_${SLURM_JOB_ID}"
mkdir -p "$F" "$TMPDIR"
cp /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/rfd_cache_materialization_v2/materialization.py "$F/materialization.py"
cp /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/rfd_cache_materialization_v2/materialization_cpu.sbatch "$F/materialization_cpu.sbatch"
chmod -R a-w "$F"
exec "$R/env/rfd/bin/python" -B "$F/materialization.py"
