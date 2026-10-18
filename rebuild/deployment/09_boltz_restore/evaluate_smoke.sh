#!/bin/bash
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9
cd "$R"
export PYTHONNOUSERSITE=1
unset PYTHONPATH
export LD_LIBRARY_PATH="/usr/local/nvidia/lib:/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}"
export TMPDIR="$R/steps/09_boltz_restore/work/tmp_$SLURM_JOB_ID"
export MPLCONFIGDIR="$R/env/matplotlib"
export HF_HOME="$R/cache/huggingface"
export XDG_CACHE_HOME="$R/cache"
mkdir -p "$TMPDIR" "$MPLCONFIGDIR"
"$R/env/boltz/bin/python" -c 'import torch; assert torch.cuda.is_available(), "CUDA unavailable"; print({"torch":torch.__version__,"cuda":torch.version.cuda,"gpu":torch.cuda.get_device_name(0),"device_count":torch.cuda.device_count()},flush=True)'
"$R/env/core/bin/python" -m ppiblocker.cli --root "$R" evaluate "$R/steps/03_design/runs/20261002T114616Z_cfa6d86555db/manifest.json" > "$R/steps/09_boltz_restore/outputs/evaluate_result_$SLURM_JOB_ID.json"
cat "$R/steps/09_boltz_restore/outputs/evaluate_result_$SLURM_JOB_ID.json"
