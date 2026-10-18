#!/bin/bash
set -euo pipefail
R='/lustre/users/u21111210118/projects/test9'
S='/lustre/users/u21111210118/projects/test9/steps/21_method_runtime'
mkdir -p "$S/runs/actual_native_v8_${SLURM_JOB_ID}/outputs" "$S/tmp/actual_native_v8_${SLURM_JOB_ID}"
export TMPDIR="$S/tmp/actual_native_v8_${SLURM_JOB_ID}"
source '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_v8/source/bindcraft_env.sh'
export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES='' PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
OUT="$S/runs/actual_native_v8_${SLURM_JOB_ID}/outputs"
set +e
python '/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/frozen/native_workflow_collectors_13207/audit_actual_rf_native_v8.py' --attempt-dir '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/engineering_pilot/runs_v5/13175_0/attempts/000000' --target-manifest '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/KEAP1_2FLU/input_manifest.json' --runtime-source '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_v8/source/benchmark_runtime.py' --confidence-collector-source '/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/runs/native_collector_contracts_13166/source/audit_native_confidence_v8.py' --plan '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/engineering_pilot/plan_v5/frozen_plan.json' --run-receipt '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/engineering_pilot/runs_v5/13175_0/run_receipt.json' --output-dir "$OUT/rf" --features > "$OUT/rf_stdout.log" 2> "$OUT/rf_stderr.log"
RC=$?
printf '%s\n' "$RC" > "$OUT/rf_returncode.txt"
set -e
set +e
python '/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/frozen/native_workflow_collectors_13207/audit_actual_bc_native_v8.py' --attempt-dir '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/engineering_pilot/runs_v5/13175_1/attempts/000000' --target-manifest '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/KEAP1_2FLU/input_manifest.json' --runtime-source '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_v8/source/benchmark_runtime.py' --confidence-collector-source '/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/runs/native_collector_contracts_13166/source/audit_native_confidence_v8.py' --plan '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/engineering_pilot/plan_v5/frozen_plan.json' --run-receipt '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/engineering_pilot/runs_v5/13175_1/run_receipt.json' --output-dir "$OUT/bc" --config '/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_v8/bindcraft.json' --config-sha256 ede838ddf98e459aceb1175c682df47439dc38f2125afd3c9c328c286e70c29f > "$OUT/bc_stdout.log" 2> "$OUT/bc_stderr.log"
RC=$?
printf '%s\n' "$RC" > "$OUT/bc_returncode.txt"
set -e
test "$(cat "$OUT/rf_returncode.txt")" = 0
test "$(cat "$OUT/bc_returncode.txt")" = 0
