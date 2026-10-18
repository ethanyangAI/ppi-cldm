#!/usr/bin/env bash
set -euo pipefail
ROOT="/lustre/users/u21111210118/projects/test9"
export PYTHONNOUSERSITE=1 CONDA_PKGS_DIRS="$ROOT/env/pkgs" MAMBA_ROOT_PREFIX="$ROOT/env/mamba"
unset PYTHONPATH
if [[ -n "${SLURM_MEM_PER_NODE:-}" ]]; then ulimit -Sv "$((SLURM_MEM_PER_NODE * 1024))"; fi
MAMBA="$ROOT/env/tools/bin/micromamba"
"$MAMBA" install --no-rc --dry-run --json -p "$ROOT/env/boltz" --override-channels -c conda-forge 'rdkit=2024.09.6' 'python=3.11.16' 'numpy=1.26.4' > "$ROOT/env/rdkit-mamba-plan.json"
"$ROOT/env/boltz/bin/python" -m pip uninstall -y rdkit
"$MAMBA" install --no-rc -y -p "$ROOT/env/boltz" --override-channels -c conda-forge 'rdkit=2024.09.6' 'python=3.11.16' 'numpy=1.26.4'
"$ROOT/env/boltz/bin/python" -c 'import rdkit,torch,numpy; print(rdkit.__version__,torch.__version__,numpy.__version__)'
"$ROOT/env/boltz/bin/python" -m pip check
"$ROOT/env/boltz/bin/python" -m pip freeze > "$ROOT/env/boltz-freeze.txt"
"$MAMBA" list --no-rc --explicit -p "$ROOT/env/boltz" > "$ROOT/env/boltz-conda-explicit.txt"
