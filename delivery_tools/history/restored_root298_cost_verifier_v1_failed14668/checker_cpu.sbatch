#!/bin/bash
#SBATCH --job-name=test9_restored_root298_cost
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/restored_root298_cost_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/restored_root298_cost_%j.err
set -euo pipefail
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
if [[ "${1:-contracts}" == contracts ]]; then
 export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/restored_root298_cost_${SLURM_JOB_ID}
 mkdir -p "$TMPDIR"
 exec /lustre/users/u21111210118/projects/test9/env/core/bin/python -B /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/restored_root298_cost_verifier_v1/checker.py contracts
fi
[[ "$1" == verify ]]
shift
[[ -n "${ROOT298_CHECKER_ENTRY:-}" ]]
[[ "$ROOT298_CHECKER_ENTRY" =~ ^/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/restored_root298_cost_verifier_v1_[0-9]+/code/checker\.py$ ]]
unset TMPDIR
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python -B "$ROOT298_CHECKER_ENTRY" verify "$@"
