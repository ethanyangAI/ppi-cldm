#!/usr/bin/env bash
set -euo pipefail
ROOT="/lustre/users/u21111210118/projects/test9"
export PYTHONNOUSERSITE=1
unset PYTHONPATH
export CONDA_PKGS_DIRS="$ROOT/env/pkgs" PIP_CACHE_DIR="$ROOT/env/pip_cache"
source "/opt/app/conda/etc/profile.d/conda.sh"
conda activate "$ROOT/env/core"
python "$ROOT/source/scripts/fetch_vendor.py"
conda activate "$ROOT/env/rfd"
python -m pip install 'numpy==1.26.4' 'scipy==1.13.1' 'biopython==1.84' 'sympy==1.13.1' typing_extensions packaging opt_einsum_fx
python -m pip install 'dgl==1.1.3+cu117' -f https://data.dgl.ai/wheels/cu117/repo.html
python -m pip install "$ROOT/vendor/dllogger"
python -m pip install --no-deps "$ROOT/vendor/RFdiffusion/env/SE3Transformer"
python -m pip install --no-deps -e "$ROOT/vendor/RFdiffusion"
mkdir -p "$ROOT/assets/rfdiffusion"
python - <<'PY'
from pathlib import Path
import requests,hashlib,json
p=Path.home()/'lvying20260610/project-1/test9/assets/rfdiffusion/Complex_base_ckpt.pt'
url='https://files.ipd.uw.edu/pub/RFdiffusion/e29311f6f1bf1af907f9ef9f44b8328b/Complex_base_ckpt.pt'
if not p.exists():
 r=requests.get(url,stream=True,timeout=(30,180));r.raise_for_status()
 with p.with_suffix('.part').open('wb') as f:
  for b in r.iter_content(1024*1024):f.write(b)
 p.with_suffix('.part').replace(p)
h=hashlib.sha256()
with p.open('rb') as f:
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
p.with_suffix('.receipt.json').write_text(json.dumps({'url':url,'sha256':h.hexdigest(),'bytes':p.stat().st_size},indent=2))
print('RF_WEIGHTS',p.stat().st_size,h.hexdigest())
PY
python -m pip freeze > "$ROOT/env/rfd-freeze.txt"
python -c 'import torch,dgl,se3_transformer,rfdiffusion; print(torch.__version__,dgl.__version__)'
if [[ ! -x "$ROOT/env/boltz/bin/python" ]]; then
 conda create -y -p "$ROOT/env/boltz" --override-channels -c conda-forge python=3.11 pip
fi
conda activate "$ROOT/env/boltz"
python -m pip install 'torch==2.5.1' --index-url https://download.pytorch.org/whl/cu118
python -m pip install 'boltz==2.2.1' 'rdkit==2024.3.2' 'pandas==2.2.3' 'matplotlib==3.9.4' 'Pillow==9.5.0' --only-binary=:all: --no-binary=fairscale,antlr4-python3-runtime,modelcif,ihm
python -m pip freeze > "$ROOT/env/boltz-freeze.txt"
boltz predict --help > "$ROOT/env/boltz-cli.txt"

