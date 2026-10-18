#!/usr/bin/env bash
set -euo pipefail
ROOT="/lustre/users/u21111210118/projects/test9"
export PYTHONNOUSERSITE=1
unset PYTHONPATH
source "/opt/app/conda/etc/profile.d/conda.sh"
conda activate "$ROOT/env/core"
cd "$ROOT/source"
python -m pytest -q --junitxml="$ROOT/steps/00_bootstrap/runs/rebuild_20260920/unit-tests.xml"
ppiblocker --root "$ROOT" prepare configs/mdm2_tp53_benchmark.yaml

