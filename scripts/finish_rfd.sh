#!/usr/bin/env bash
set -euo pipefail
ROOT="/lustre/users/u21111210118/projects/test9"
export PYTHONNOUSERSITE=1 PIP_CACHE_DIR="$ROOT/env/pip_cache"
unset PYTHONPATH
source "/opt/app/conda/etc/profile.d/conda.sh"
conda activate "$ROOT/env/rfd"
python -m pip install networkx tqdm 'scipy==1.13.1' 'numpy==1.26.4'
python - <<'PY'
from pathlib import Path
import requests,hashlib,json
p=Path.home()/'lvying20260610/project-1/test9/assets/rfdiffusion/Complex_base_ckpt.pt'
url='https://files.ipd.uw.edu/pub/RFdiffusion/e29311f6f1bf1af907f9ef9f44b8328b/Complex_base_ckpt.pt'
q=p.with_suffix('.part')
if not p.exists():
 offset=q.stat().st_size if q.exists() else 0
 r=requests.get(url,headers={'Range':f'bytes={offset}-'} if offset else {},stream=True,timeout=(30,180));r.raise_for_status()
 mode='ab' if offset and r.status_code==206 else 'wb'
 print('RF_DOWNLOAD',mode,offset,r.status_code,flush=True)
 with q.open(mode) as f:
  for b in r.iter_content(1024*1024):f.write(b)
 q.replace(p)
h=hashlib.sha256()
with p.open('rb') as f:
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
p.with_suffix('.receipt.json').write_text(json.dumps({'url':url,'sha256':h.hexdigest(),'bytes':p.stat().st_size},indent=2))
print('RF_WEIGHTS',p.stat().st_size,h.hexdigest(),flush=True)
PY
python -c 'import torch,dgl,se3_transformer,rfdiffusion; print(torch.__version__,dgl.__version__)'
python -m pip freeze > "$ROOT/env/rfd-freeze.txt"
python -m pip check

