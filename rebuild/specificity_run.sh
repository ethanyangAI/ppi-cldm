#!/usr/bin/env bash
set -euo pipefail
ROOT=/lustre/users/u21111210118/projects/test9
export PS1="${PS1:-}"
source "$ROOT/steps/03_af2_restore/inference_env.sh"
export JAX_PLATFORMS=cuda
export MPLCONFIGDIR="$ROOT/steps/15_specificity_review/cache/matplotlib" XDG_CACHE_HOME="$ROOT/steps/15_specificity_review/cache/xdg"
export TMPDIR="$ROOT/steps/15_specificity_review/tmp/$SLURM_ARRAY_JOB_ID/$SLURM_ARRAY_TASK_ID"
mkdir -p "$MPLCONFIGDIR" "$XDG_CACHE_HOME" "$TMPDIR"
cd "$ROOT"
python "$ROOT/source/rebuild/specificity_review.py" worker "$SLURM_ARRAY_TASK_ID"

