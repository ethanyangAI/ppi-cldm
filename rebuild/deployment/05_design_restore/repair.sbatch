#!/bin/bash
#SBATCH -J t9-rfd-fix
#SBATCH -p interactive
#SBATCH -c 2
#SBATCH --mem=6G
#SBATCH -t 00:20:00
#SBATCH -o /lustre/users/u21111210118/projects/test9/steps/05_design_restore/logs/repair_%j.log
set -euo pipefail
cd /lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1 DGLBACKEND=pytorch OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
export PIP_CACHE_DIR=/lustre/users/u21111210118/projects/test9/env/cache/pip TMPDIR=/lustre/users/u21111210118/projects/test9/steps/05_design_restore/work
export PS1="${PS1:-}"
source /opt/app/conda/etc/profile.d/conda.sh
conda activate /lustre/users/u21111210118/projects/test9/env/rfd
python -m pip install nvidia-cusparse-cu11==11.7.5.86 nvidia-cuda-runtime-cu11==11.8.89
export LD_LIBRARY_PATH=/lustre/users/u21111210118/projects/test9/env/rfd/lib:/lustre/users/u21111210118/projects/test9/env/rfd/lib/python3.10/site-packages/torch/lib:/lustre/users/u21111210118/projects/test9/env/rfd/lib/python3.10/site-packages/nvidia/cusparse/lib:/lustre/users/u21111210118/projects/test9/env/rfd/lib/python3.10/site-packages/nvidia/cuda_runtime/lib:${LD_LIBRARY_PATH:-}
python -c 'import torch,dgl,se3_transformer,rfdiffusion; print("DESIGN_IMPORTS_OK",torch.__version__,dgl.__version__)'
python -m pip check
python -m pip freeze > env/rfd-freeze.txt
conda list --explicit > env/rfd-explicit.txt
