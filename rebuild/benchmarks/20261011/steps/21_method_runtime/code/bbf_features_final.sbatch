#!/usr/bin/env bash
#SBATCH --job-name=t9-bbf-feature-audit
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=00:30:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/bbf_features_%j.out
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9;S="$R/steps/21_method_runtime"
export TMPDIR="$S/work" XDG_CACHE_HOME="$R/env/cache" CONDA_PKGS_DIRS="$R/env/pkgs" PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
source "$S/code/bindcraft_env.sh"
export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=""
python -m py_compile "$S/code/bbf_feature_backend.py" "$S/code/bindcraft_native_feature_audit.py"
python "$S/code/bindcraft_native_feature_audit.py"
python "$S/code/bbf_feature_backend.py" features --plan "$R/steps/23_common_review/bbf_diagnostics/inputs/plan_v2.json" --output-dir "$S/runs/bbf_features_$SLURM_JOB_ID/outputs"

