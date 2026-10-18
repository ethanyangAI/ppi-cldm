#!/usr/bin/env bash
#SBATCH --job-name=t9-pilot-v6-bridge
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=00:20:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/pilot_v6_bridge_features_%j.out
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9
S="$R/steps/21_method_runtime"
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=1 TMPDIR="$S/work" XDG_CACHE_HOME="$R/env/cache"
unset PYTHONPATH
source "$S/code/bindcraft_env.sh"
export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=""
python - <<'T9FREEZE'
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");src=R/"steps/21_method_runtime/code/pilot_v6_feature_bridge_audit.py";dest=R/"steps/22_matched_benchmark/settings/pilot_v6/source/pilot_v6_feature_bridge_audit.py"
assert not dest.exists()
dest.write_bytes(src.read_bytes());assert dest.read_bytes()==src.read_bytes()
T9FREEZE
python "$R/steps/22_matched_benchmark/settings/pilot_v6/source/pilot_v6_feature_bridge_audit.py"

