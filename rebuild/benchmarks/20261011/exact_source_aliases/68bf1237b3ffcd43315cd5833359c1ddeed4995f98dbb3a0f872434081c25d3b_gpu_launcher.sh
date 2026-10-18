#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=01:01:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/bc_supplemental_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/bc_supplemental_%j.err
set -euo pipefail
S=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime
V=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_v8
SOURCE="$S/frozen/supplemental_bindcraft_13224/bindcraft_supplemental_stage_coverage.py"
CONFIG="$S/runs/supplemental_stage_prepare_13224/outputs/config.json"
CONFIG_SHA=d3e36732289706f31c672d7d42fb32d184e9edf8ba5b554861ebf65eedd053ff
OUT="$S/runs/bindcraft_supplemental_gpu_$SLURM_JOB_ID/outputs"
export TMPDIR="$S/tmp/bc_supplemental_$SLURM_JOB_ID"
mkdir -p "$TMPDIR"
source "$V/source/bindcraft_env.sh"
# Root-reviewed independent engineering allocation: startup and diagnostic scoring count.
# Strict exact ownership helper runs before JAX/CUDA imports in worker.
SELECTED=$(scontrol show job -o "$SLURM_JOB_ID" | awk -v id="$SLURM_JOB_ID" '$1==("JobId="id){print}')
test -n "$SELECTED"
START=$(printf '%s\n' "$SELECTED" | sed -n 's/.* StartTime=\([^ ]*\).*/\1/p')
START_EPOCH=$(date -d "$START" +%s)
NOW=$(date +%s)
REMAIN=$((START_EPOCH+3590-NOW))
test "$REMAIN" -gt 0
export BENCHMARK_GENERATION_DEADLINE_EPOCH=$((START_EPOCH+3590))
export BENCHMARK_ALLOCATION_DEADLINE_EPOCH=$((START_EPOCH+3600))
mkdir -p "$(dirname "$OUT")"
printf '%s\n' "$SELECTED" > "$(dirname "$OUT")/scheduler_at_launch.txt"
printf '%s\n' "scope=ENGINEERING_STAGE_COVERAGE_ONLY_NOT_NATIVE_ACCEPTED_NOT_FORMAL" "allocation_start_epoch=$START_EPOCH" "generation_deadline_epoch=$BENCHMARK_GENERATION_DEADLINE_EPOCH" "allocation_deadline_epoch=$BENCHMARK_ALLOCATION_DEADLINE_EPOCH" "selected_raw_pool_index=0" > "$(dirname "$OUT")/launcher_budget.txt"
timeout --signal=TERM --kill-after=10 "$REMAIN"s python "$SOURCE" run --config "$CONFIG" --config-sha256 "$CONFIG_SHA" --output-dir "$OUT"
