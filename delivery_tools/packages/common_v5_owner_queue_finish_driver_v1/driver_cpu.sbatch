#!/bin/bash
#SBATCH --job-name=test9_common_ownerqueue_finish_cpu
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/common-ownerqueue-driver-%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/common-ownerqueue-driver-%j.err
set -euo pipefail
export PS1="${PS1:-}" CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
MODE="${1:?contracts or finish required}"
shift
export TMPDIR="$R/steps/24_benchmark_delivery/tmp/common_ownerqueue_driver_${SLURM_JOB_ID}"
mkdir -p "$TMPDIR"
if [[ "$MODE" == contracts ]]; then
  test "$#" -eq 0
  exec "$R/env/core/bin/python" -B "$R/steps/24_benchmark_delivery/pending/common_v5_owner_queue_finish_driver_v1/driver.py" contracts --out "$R/steps/24_benchmark_delivery/runs/common_v5_owner_queue_driver_contracts_${SLURM_JOB_ID}"
elif [[ "$MODE" == finish ]]; then
  exec "$R/env/core/bin/python" -B "${COMMON_FINISH_DRIVER_ENTRY:?exact accepted frozen driver entry required}" finish "$@"
else
  exit 2
fi

