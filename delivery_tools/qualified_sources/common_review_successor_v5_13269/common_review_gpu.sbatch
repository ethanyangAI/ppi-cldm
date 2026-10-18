#!/bin/bash
#SBATCH --job-name=ppi_formal_common_pending
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=3
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/formal-common-%A_%a.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/formal-common-%A_%a.err
set -euo pipefail
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4
unset PYTHONPATH JAX_PLATFORMS
R=/lustre/users/u21111210118/projects/test9
ENTRY="${COMMON_SUCCESSOR_ENTRY:?absolute CPU-tested frozen entry required}"
PRE="${1:?absolute actual CPU preflight JSON required}"
INDEX="${SLURM_ARRAY_TASK_ID:?root pending-only array required}"
ENGINE=$("$R/env/core/bin/python" "$ENTRY" engine --preflight "$PRE" --index "$INDEX")
if [[ "$ENGINE" == af2 ]]; then
  source "$R/steps/23_common_review/frozen/common_core_v2_13130/code/runtime_entries/af2_inference_env.sh"
elif [[ "$ENGINE" != boltz ]]; then exit 2; fi
exec "$R/env/core/bin/python" "$ENTRY" worker --preflight "$PRE" --index "$INDEX"
