#!/usr/bin/env bash
set -euo pipefail
ROOT=/lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1
export TMPDIR="$ROOT/cache/benchmark_tmp"
mkdir -p "$TMPDIR"
unset PYTHONPATH
source "/opt/app/conda/etc/profile.d/conda.sh"
conda activate "$ROOT/env/core"
ulimit -Sv "$((SLURM_MEM_PER_NODE * 1024))"
cd "$ROOT/source"
python -m compileall -q src/ppiblocker
python -m pytest -q --basetemp="$ROOT/cache/benchmark_tmp/pytest_$SLURM_JOB_ID" --junitxml="$ROOT/steps/06_benchmark/logs/benchmark-tests.$SLURM_JOB_ID.xml"

