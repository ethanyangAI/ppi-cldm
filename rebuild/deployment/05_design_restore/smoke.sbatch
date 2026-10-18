#!/bin/bash
#SBATCH -J test9-design-smoke
#SBATCH -p organ
#SBATCH --gres=gpu:1
#SBATCH --oversubscribe
#SBATCH -c 4
#SBATCH --mem=64G
#SBATCH -t 01:30:00
#SBATCH -o /lustre/users/u21111210118/projects/test9/steps/05_design_restore/logs/smoke_%j.log
set -euo pipefail
cd /lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 DGLBACKEND=pytorch
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/05_design_restore/work XDG_CACHE_HOME=/lustre/users/u21111210118/projects/test9/env/cache
export LD_LIBRARY_PATH=/lustre/users/u21111210118/projects/test9/env/rfd/lib:/lustre/users/u21111210118/projects/test9/env/rfd/lib/python3.10/site-packages/torch/lib:/lustre/users/u21111210118/projects/test9/env/rfd/lib/python3.10/site-packages/nvidia/cusparse/lib:/lustre/users/u21111210118/projects/test9/env/rfd/lib/python3.10/site-packages/nvidia/cuda_runtime/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}
export PS1="${PS1:-}"
source /opt/app/conda/etc/profile.d/conda.sh
conda activate /lustre/users/u21111210118/projects/test9/env/rfd
python -c 'import torch,dgl; assert torch.cuda.is_available(); print(torch.cuda.get_device_name(0)); print((torch.ones(4,device="cuda")*2).cpu())'
conda activate /lustre/users/u21111210118/projects/test9/env/core
python - <<'PY'
from pathlib import Path
from ppiblocker.common import collect_runtime,atomic_json
r=Path("/lustre/users/u21111210118/projects/test9");p=r/"source/environment/runtime-lock-rfd.json"
assert not p.exists(),"Explicit initial registration only"
atomic_json(p,collect_runtime(r,"rfd"));print("RFD_RUNTIME_LOCK_REGISTERED")
PY
ppiblocker --root /lustre/users/u21111210118/projects/test9 design /lustre/users/u21111210118/projects/test9/steps/01_pose/runs/20261002T114406Z_8617d1e371ca/manifest.json
