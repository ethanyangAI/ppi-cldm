#!/bin/bash
#SBATCH --job-name=test9_restored_common13460_metadata
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/restored-common13460-metadata-%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/restored-common13460-metadata-%j.err
set -euo pipefail
export CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
unset PYTHONPATH
mode=${1:-contracts}
if [ "$mode" = contracts ]; then
  export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/restored_common13460_metadata_${SLURM_JOB_ID}
  mkdir -p "$TMPDIR"
  test "$#" -le 1
  exec /lustre/users/u21111210118/projects/test9/env/core/bin/python -B /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/restored_common13460_metadata_verifier_v1/checker.py contracts
fi
test "$mode" = verify
unset TMPDIR
test "$#" -ge 2
entry=$2
[[ "$entry" =~ ^/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/restored_common13460_metadata_verifier_v1_[0-9]+/code/checker\.py$ ]]
shift 2
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python "$entry" verify "$@"
