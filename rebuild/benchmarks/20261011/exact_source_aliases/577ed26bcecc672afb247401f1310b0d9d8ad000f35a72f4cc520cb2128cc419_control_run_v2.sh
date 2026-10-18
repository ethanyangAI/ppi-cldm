#!/usr/bin/env bash
set -euo pipefail
ROOT=/lustre/users/u21111210118/projects/test9
export PS1="${PS1:-}"
source "$ROOT/steps/03_af2_restore/inference_env.sh"
export JAX_PLATFORMS=cuda
export MPLCONFIGDIR="$ROOT/steps/17_control_calibration/cache/matplotlib" XDG_CACHE_HOME="$ROOT/steps/17_control_calibration/cache/xdg"
export TMPDIR="$ROOT/steps/17_control_calibration/tmp/$SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID"
mkdir -p "$MPLCONFIGDIR" "$XDG_CACHE_HOME" "$TMPDIR"
cd "$ROOT"
python "$ROOT/source/rebuild/control_review_v2.py" worker "$SLURM_ARRAY_TASK_ID"

