#!/bin/bash
#SBATCH --job-name=ppi_delivery_source_v8
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:15:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/source_audit_v8_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/source_audit_v8_%j.err
set -euo pipefail
export PS1="${PS1:-}"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/source_audit_v8_${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
SNAPSHOT=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/source_audit_v8_${SLURM_JOB_ID}/code
mkdir -p "$SNAPSHOT"
cp /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/code/{delivery_graph_v2.py,delivery_core.py,provenance_aliases_v2.py} "$SNAPSHOT/"
chmod -R a-w "$SNAPSHOT"
OUTPUT=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_audit_v8_${SLURM_JOB_ID}
mkdir -p "$OUTPUT"
/lustre/users/u21111210118/projects/test9/env/core/bin/python "$SNAPSHOT/delivery_graph_v2.py" source-audit --root /lustre/users/u21111210118/projects/test9 --out "$OUTPUT/source_inclusion_v2.json" --runtime-settings pilot_v8

