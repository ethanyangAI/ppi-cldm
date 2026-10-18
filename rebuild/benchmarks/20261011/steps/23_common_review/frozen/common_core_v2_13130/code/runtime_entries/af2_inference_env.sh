#!/usr/bin/env bash
# Source only inside a Slurm GPU inference job. No inference is launched by this file.
ROOT=/lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=1
unset PYTHONPATH
source /opt/app/conda/etc/profile.d/conda.sh
conda activate "$ROOT/env/colabfold"
SITE="$ROOT/env/colabfold/lib/python3.10/site-packages"
export XLA_PYTHON_CLIENT_PREALLOCATE=false TF_FORCE_UNIFIED_MEMORY=0 TF_NUM_INTRAOP_THREADS=4 TF_NUM_INTEROP_THREADS=1
export XLA_FLAGS="--xla_gpu_cuda_data_dir=$SITE/nvidia/cuda_nvcc"
LIBS=
for P in "$SITE"/nvidia/*/lib; do
  [ -d "$P" ] && LIBS="${LIBS:+$LIBS:}$P"
done
export LD_LIBRARY_PATH="$LIBS:$ROOT/env/colabfold/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}"
export PATH="$ROOT/env/colabfold/bin:$SITE/nvidia/cuda_nvcc/bin:$PATH"
