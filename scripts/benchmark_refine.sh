#!/usr/bin/env bash
set -euo pipefail
ROOT=/lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1
unset PYTHONPATH
source "/opt/app/conda/etc/profile.d/conda.sh"
conda activate "$ROOT/env/core"
ulimit -Sv "$((SLURM_MEM_PER_NODE * 1024))"
cd "$ROOT/source"
python scripts/refine_benchmark_checks.py
python -m pytest -q --junitxml="$ROOT/steps/06_benchmark/logs/benchmark-tests.$SLURM_JOB_ID.xml"
python -u scripts/qualify_benchmark.py "$ROOT" "$ROOT/00_admin/benchmark/proposal_matrix_20260920.json"

