#!/bin/bash
#SBATCH -J t9-design-restore
#SBATCH -p interactive
#SBATCH -c 4
#SBATCH --mem=12G
#SBATCH -t 02:00:00
#SBATCH -o /lustre/users/u21111210118/projects/test9/steps/05_design_restore/logs/install_%j.log
set -euo pipefail
cd /lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 DGLBACKEND=pytorch
unset PYTHONPATH
export PPIBLOCKER_ROOT=/lustre/users/u21111210118/projects/test9 CONDA_PKGS_DIRS=/lustre/users/u21111210118/projects/test9/env/pkgs PIP_CACHE_DIR=/lustre/users/u21111210118/projects/test9/env/cache/pip
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/05_design_restore/work XDG_CACHE_HOME=/lustre/users/u21111210118/projects/test9/env/cache
export PS1="${PS1:-}"
source /opt/app/conda/etc/profile.d/conda.sh
conda activate /lustre/users/u21111210118/projects/test9/env/core
python steps/01_recovery/work/recovered_source/scripts/fetch_vendor.py
cat vendor/RFdiffusion/env/SE3Transformer/requirements.txt
conda create -y --override-channels -c conda-forge -p /lustre/users/u21111210118/projects/test9/env/rfd python=3.10 pip
conda activate /lustre/users/u21111210118/projects/test9/env/rfd
python -m pip install 'torch==2.0.1' --index-url https://download.pytorch.org/whl/cu117
python -m pip install 'numpy==1.26.4' 'scipy==1.13.1' 'biopython==1.84' 'e3nn==0.3.3' 'hydra-core==1.3.2' 'omegaconf==2.3.0' 'pyrsistent==0.19.3' 'einops==0.6.1' opt_einsum_fx icecream networkx tqdm requests
python -m pip install 'dgl==1.1.3+cu117' -f https://data.dgl.ai/wheels/cu117/repo.html
python -m pip install vendor/dllogger
python -m pip install --no-deps vendor/RFdiffusion/env/SE3Transformer
python -m pip install --no-deps -e vendor/RFdiffusion
python -c 'import torch,dgl,se3_transformer,rfdiffusion; print("DESIGN_IMPORTS_OK",torch.__version__,dgl.__version__)'
python -m pip check
python -m pip freeze > env/rfd-freeze.txt
conda list --explicit > env/rfd-explicit.txt
