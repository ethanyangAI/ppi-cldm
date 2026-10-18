#!/usr/bin/env bash
set -euo pipefail
ROOT=/lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 PIP_DEFAULT_TIMEOUT=40 PIP_RETRIES=2
export CONDA_PKGS_DIRS="$ROOT/env/pkgs" PIP_CACHE_DIR="$ROOT/env/cache/pip"
unset PYTHONPATH
if [[ ! -x "$ROOT/env/boltz/bin/python" ]]; then
 /opt/app/conda/bin/conda create -y -p "$ROOT/env/boltz" --override-channels -c conda-forge python=3.11 pip
fi
P="$ROOT/env/boltz/bin/python"
"$P" -m pip install 'torch==2.5.1' --index-url https://download.pytorch.org/whl/cu118
"$P" -m pip install 'boltz==2.2.1' 'rdkit==2024.9.6' 'numpy==1.26.4' 'pandas==2.2.3' 'matplotlib==3.9.4'
"$P" -m pip check
"$P" -m pip freeze > "$ROOT/env/boltz-freeze.txt"
/opt/app/conda/bin/conda list -p "$ROOT/env/boltz" --explicit > "$ROOT/env/boltz-explicit.txt"
"$ROOT/env/boltz/bin/boltz" predict --help > "$ROOT/env/boltz-cli.txt"
"$P" - <<'PY'
import json,importlib.metadata as m
from pathlib import Path
import torch,numpy,rdkit,boltz
R=Path("/lustre/users/u21111210118/projects/test9")
d={k:m.version(k) for k in ("boltz","torch","numpy","rdkit","pandas","matplotlib")}
assert d["boltz"]=="2.2.1"
assert d["torch"]=="2.5.1+cu118"
assert d["rdkit"]=="2024.9.6"
d.update(status="BOLTZ_RUNTIME_READY_NO_INFERENCE",cuda_runtime=torch.version.cuda)
(R/"steps/09_boltz_restore/outputs/runtime_receipt.json").write_text(json.dumps(d,indent=2)+"\n")
print(json.dumps(d,indent=2))
PY

