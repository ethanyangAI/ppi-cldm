#!/usr/bin/env bash
set -euo pipefail
ROOT=/lustre/users/u21111210118/projects/test9
STEP="$ROOT/steps/03_af2_restore"
export PYTHONNOUSERSITE=1 CONDA_PKGS_DIRS="$STEP/conda_pkgs" PIP_CACHE_DIR="$STEP/pip_cache" TMPDIR="$STEP/tmp" PIP_DEFAULT_TIMEOUT=60
unset PYTHONPATH
mkdir -p "$CONDA_PKGS_DIRS" "$PIP_CACHE_DIR" "$TMPDIR"
source /opt/app/conda/etc/profile.d/conda.sh
if [ ! -x "$ROOT/env/colabfold/bin/python" ]; then
  timeout 3600 conda create -y -p "$ROOT/env/colabfold" --override-channels -c https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge python=3.10 pip
fi
conda activate "$ROOT/env/colabfold"
timeout 14400 python -m pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple --retries 3 \
 "colabfold[alphafold]==1.5.5" "jax[cuda11_pip]==0.4.23" "jaxlib==0.4.23+cuda11.cudnn86" \
 "numpy==1.24.3" "scipy==1.12.0" "nvidia-cudnn-cu11==8.9.6.50" \
 "tensorflow-cpu==2.12.1" "ml-dtypes==0.2.0" "flax==0.7.5" "optax==0.1.9" \
 "chex==0.1.86" "orbax-checkpoint==0.4.4" "dm-tree==0.1.8" \
 "grpcio==1.54.2" "typing-extensions==4.5.0" "google-auth==2.29.0" \
 "cryptography==41.0.7" "tensorstore==0.1.45" "etils==1.5.2" \
 --find-links https://storage.googleapis.com/jax-releases/jax_cuda_releases.html \
 --only-binary=:all: --no-binary=alphafold-colabfold
python -m pip check
python -m pip freeze > "$STEP/colabfold-freeze.txt"
conda list --explicit > "$STEP/colabfold-explicit.txt"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu
colabfold_batch --help > "$STEP/colabfold-help.txt"
python "$STEP/verify_runtime.py"
