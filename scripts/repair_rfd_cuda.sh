#!/usr/bin/env bash
set -euo pipefail
ROOT="/lustre/users/u21111210118/projects/test9"
export PYTHONNOUSERSITE=1 PIP_CACHE_DIR="$ROOT/env/pip_cache" DGLBACKEND=pytorch
unset PYTHONPATH
source "/opt/app/conda/etc/profile.d/conda.sh"
conda activate "$ROOT/env/rfd"
python -m pip install --no-index --find-links "$ROOT/env/wheels" 'nvidia-cusparse-cu11==11.7.5.86' 'nvidia-cuda-runtime-cu11==11.8.89'
python -m pip install six 'PyYAML==6.0.3' 'click<8.2'
export LD_LIBRARY_PATH="$ROOT/env/rfd/lib:$ROOT/env/rfd/lib/python3.10/site-packages/torch/lib:$ROOT/env/rfd/lib/python3.10/site-packages/nvidia/cusparse/lib:$ROOT/env/rfd/lib/python3.10/site-packages/nvidia/cuda_runtime/lib"
python -c 'import torch,dgl,se3_transformer,rfdiffusion; print(torch.__version__,dgl.__version__)'
python -m pip freeze > "$ROOT/env/rfd-freeze.txt"
python -m pip check

