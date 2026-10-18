#!/bin/bash
set -euo pipefail
source '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_v8/source/bindcraft_env.sh'
export CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu OPENBLAS_NUM_THREADS=1
export TMPDIR='/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/tmp/native_runtime_handoff_'$SLURM_JOB_ID
mkdir -p "$TMPDIR"
python '/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/native_runtime_handoff.py'

