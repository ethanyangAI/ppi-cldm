#!/bin/bash
set -euo pipefail
S='/lustre/users/u21111210118/projects/test9/steps/21_method_runtime'
source '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_v8/source/bindcraft_env.sh'
export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES='' OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR="$S/tmp/supplemental_prepare_${SLURM_JOB_ID}"
mkdir -p "$TMPDIR"
python '/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/prepare_bindcraft_supplemental_stage.py'
