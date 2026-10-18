#!/usr/bin/env bash
set -euo pipefail
ROOT="/lustre/users/u21111210118/projects/test9"
export PYTHONNOUSERSITE=1 PIP_CACHE_DIR="$ROOT/env/pip_cache" CONDA_PKGS_DIRS="$ROOT/env/pkgs"
unset PYTHONPATH
source "/opt/app/conda/etc/profile.d/conda.sh"
if [[ ! -x "$ROOT/env/boltz/bin/python" ]]; then
 conda create -y -p "$ROOT/env/boltz" --override-channels -c conda-forge python=3.11 pip
fi
conda activate "$ROOT/env/boltz"
python -m pip install 'torch==2.5.1' --index-url https://download.pytorch.org/whl/cu118
python -m pip install 'boltz==2.2.1' 'rdkit==2024.3.5' 'pandas==2.2.3' 'matplotlib==3.9.4'
python -m pip freeze > "$ROOT/env/boltz-freeze.txt"
boltz predict --help > "$ROOT/env/boltz-cli.txt"
python -m pip check

