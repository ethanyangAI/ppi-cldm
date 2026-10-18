#!/usr/bin/env bash
# Source inside Slurm inference allocation.
R=/lustre/users/u21111210118/projects/test9
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=1 DGLBACKEND=pytorch
unset PYTHONPATH
export TORCH_HOME="$R/env/cache/torch" DGL_DOWNLOAD_DIR="$R/env/cache/dgl"
source /opt/app/conda/etc/profile.d/conda.sh
conda activate "$R/env/rfd"
SITE="$R/env/rfd/lib/python3.10/site-packages"
export LD_LIBRARY_PATH="$R/env/rfd/lib:$SITE/torch/lib:$SITE/nvidia/cusparse/lib:$SITE/nvidia/cuda_runtime/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}"

