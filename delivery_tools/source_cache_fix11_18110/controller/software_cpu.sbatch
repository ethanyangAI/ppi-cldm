#!/bin/bash
set -euo pipefail
export PS1="" CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR="/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/final_source_cache_repair_$SLURM_JOB_ID"
mkdir -p "$TMPDIR"
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python -B /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_delivery_source_repair_18095_v1/software_control.py /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_delivery_source_repair_18095_v1/request.json
