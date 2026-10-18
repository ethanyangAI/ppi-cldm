#!/usr/bin/env bash
# Source inside Slurm inference allocation; shared/system packages stay read-only.
R=/lustre/users/u21111210118/projects/test9
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=1
unset PYTHONPATH
unset JAX_PLATFORMS
export TORCH_HOME="$R/env/cache/torch"
source /opt/app/conda/etc/profile.d/conda.sh
conda activate "$R/env/bindcraft"
SITE="$R/env/bindcraft/lib/python3.10/site-packages"
export XLA_PYTHON_CLIENT_PREALLOCATE=false TF_FORCE_UNIFIED_MEMORY=0 TF_NUM_INTRAOP_THREADS=4 TF_NUM_INTEROP_THREADS=1
export XLA_FLAGS="--xla_gpu_cuda_data_dir=$SITE/nvidia/cuda_nvcc"
LIBS=
for P in "$SITE"/nvidia/*/lib; do
 [ -d "$P" ] && LIBS="${LIBS:+$LIBS:}$P"
done
export LD_LIBRARY_PATH="$LIBS:$R/env/bindcraft/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}"
export PATH="$R/env/bindcraft/bin:$SITE/nvidia/cuda_nvcc/bin:$PATH"
export MPLBACKEND=Agg

