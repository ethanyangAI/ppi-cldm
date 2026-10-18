#!/usr/bin/env bash
#SBATCH --job-name=t9-method-readiness
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=01:00:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/readiness_%j.out
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9;S="$R/steps/21_method_runtime"
export TMPDIR="$S/work" XDG_CACHE_HOME="$R/env/cache" PIP_CACHE_DIR="$R/env/cache/pip" CONDA_PKGS_DIRS="$R/env/pkgs"
source "$S/code/bindcraft_env.sh"
export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=""
python "$S/code/cpu_readiness.py"

