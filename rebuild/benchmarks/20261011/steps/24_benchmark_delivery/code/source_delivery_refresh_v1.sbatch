#!/bin/bash
#SBATCH --job-name=test9_source_refresh_v1
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/source_refresh_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/source_refresh_%j.err
set -euo pipefail
export PS1="${PS1:-}"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/source_refresh_${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
SNAPSHOT=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/source_refresh_v1_${SLURM_JOB_ID}/code
mkdir -p "$SNAPSHOT"
cp /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/code/{source_delivery_refresh_v1.py,delivery_graph_v2.py,delivery_core.py,provenance_aliases_v2.py,native_resource_closure_v2.py,source_delivery_refresh_v1.sbatch} "$SNAPSHOT/"
chmod -R a-w "$SNAPSHOT"
OUT=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_${SLURM_JOB_ID}
/lustre/users/u21111210118/projects/test9/env/core/bin/python "$SNAPSHOT/source_delivery_refresh_v1.py" audit --out "$OUT"

