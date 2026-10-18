#!/bin/bash
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9
cd "$R"
export PYTHONNOUSERSITE=1
unset PYTHONPATH
export LD_LIBRARY_PATH="/usr/local/nvidia/lib:/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}"
export TMPDIR="$R/steps/09_boltz_restore/work/native_tmp_$SLURM_JOB_ID"
export MPLCONFIGDIR="$R/env/matplotlib"
export HF_HOME="$R/cache/huggingface"
export XDG_CACHE_HOME="$R/cache"
mkdir -p "$TMPDIR" "$MPLCONFIGDIR"
"$R/env/boltz/bin/python" -c 'import torch; assert torch.cuda.is_available(), "CUDA unavailable"; print({"torch":torch.__version__,"cuda":torch.version.cuda,"gpu":torch.cuda.get_device_name(0),"device_count":torch.cuda.device_count()},flush=True)'
IFS= read -r upstream < "$R/steps/09_boltz_restore/outputs/native_predict_manifest_path.txt"
set +e
"$R/env/core/bin/python" -m ppiblocker.cli --root "$R" predict "$upstream" > "$R/steps/09_boltz_restore/outputs/native_predict_result_$SLURM_JOB_ID.json"
status=$?
set -e
cat "$R/steps/09_boltz_restore/outputs/native_predict_result_$SLURM_JOB_ID.json"
printf '%s\n' "$status" > "$R/steps/09_boltz_restore/outputs/native_predict_exit_$SLURM_JOB_ID.txt"
exit "$status"
