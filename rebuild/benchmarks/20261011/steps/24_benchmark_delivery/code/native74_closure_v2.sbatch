#!/bin/bash
#SBATCH --job-name=ppi_native74_closure_v2
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/native74_closure_v2_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/native74_closure_v2_%j.err
set -euo pipefail
export PS1="${PS1:-}"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/native74_closure_v2_${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
SNAPSHOT=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/native74_closure_v2_${SLURM_JOB_ID}/code
mkdir -p "$SNAPSHOT"
cp /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/code/{native_resource_closure_v2.py,test_native_resource_closure_v2.py,provenance_aliases_v2.py,native74_closure_v2.sbatch} "$SNAPSHOT/"
chmod -R a-w "$SNAPSHOT"
export NATIVE_CLOSURE_TEST_OUTPUT=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/native74_closure_v2_${SLURM_JOB_ID}
/lustre/users/u21111210118/projects/test9/env/core/bin/python "$SNAPSHOT/test_native_resource_closure_v2.py"
/lustre/users/u21111210118/projects/test9/env/core/bin/python "$SNAPSHOT/native_resource_closure_v2.py" --old-run /lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/native74_review_13124 --out-dir "$NATIVE_CLOSURE_TEST_OUTPUT/native74"

