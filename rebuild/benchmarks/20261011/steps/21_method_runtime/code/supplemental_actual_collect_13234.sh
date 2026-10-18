#!/bin/bash
set -euo pipefail
source '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_v8/source/bindcraft_env.sh'
export CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu OPENBLAS_NUM_THREADS=1
export TMPDIR='/lustre/users/u21111210118/projects/test9/steps/21_method_runtime'/tmp/supplemental_actual_$SLURM_JOB_ID
mkdir -p "$TMPDIR"
python '/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/frozen/supplemental_content_collector_13233/audit_supplemental_bindcraft_v1.py' --gpu-output '/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/runs/bindcraft_supplemental_gpu_13234/outputs' --output-dir '/lustre/users/u21111210118/projects/test9/steps/21_method_runtime'/runs/supplemental_actual_content_$SLURM_JOB_ID/outputs
