#!/usr/bin/env bash
set -euo pipefail
ROOT="$1";stage="$2";input="$3"
export PYTHONNOUSERSITE=1
unset PYTHONPATH
source "/opt/app/conda/etc/profile.d/conda.sh"
conda activate "$ROOT/env/core"
cd "$ROOT/source"
# Raise only this job soft address-space limit to the memory explicitly allocated by Slurm.
if [[ -n "$SLURM_MEM_PER_NODE" ]]; then ulimit -Sv "$((SLURM_MEM_PER_NODE * 1024))"; fi
if [[ "$stage" != prepare && "$stage" != reevaluate ]];then nvidia-smi;fi
ppiblocker --root "$ROOT" "$stage" "$input"
