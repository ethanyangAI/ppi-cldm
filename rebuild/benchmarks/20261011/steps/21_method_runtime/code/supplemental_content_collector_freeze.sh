#!/bin/bash
set -euo pipefail
source '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_v8/source/bindcraft_env.sh'
export CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu TMPDIR='/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/tmp'
python '/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_content_collector_freeze.py'
