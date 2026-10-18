#!/usr/bin/env bash
set -euo pipefail
ROOT=/lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1
unset PYTHONPATH
source "/opt/app/conda/etc/profile.d/conda.sh"
conda activate "$ROOT/env/core"
ulimit -Sv "$((SLURM_MEM_PER_NODE * 1024))"
cd "$ROOT/source"
python scripts/apply_benchmark_patch.py
python -m pytest -q --junitxml="$ROOT/steps/06_benchmark/logs/benchmark-tests.$SLURM_JOB_ID.xml"
python -m ppiblocker.benchmark --root "$ROOT" select "$ROOT/steps/04_evaluate/runs/20260920T100554Z_11f18130120e/manifest.json" --k 8

