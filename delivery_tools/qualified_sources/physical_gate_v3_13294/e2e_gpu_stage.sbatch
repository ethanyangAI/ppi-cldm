#!/bin/bash
#SBATCH --job-name=test9_reference_free_e2e_model
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --gres=gpu:1
#SBATCH --oversubscribe
#SBATCH --cpus-per-task=3
#SBATCH --mem=64G
#SBATCH --time=1-00:00:00
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/logs/model_stage_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/logs/model_stage_%j.err
set -euo pipefail
if [[ $# != 4 && $# != 6 ]]; then
 echo "Use: stage CPU_ACCEPTANCE EXACT_UPSTREAM NEW_RESULT_DIR [EXACT_DESIGN_STAGE_RESULT EXACT_CPU_DESIGN_ACCEPTANCE]" >&2
 exit 2
fi
stage="$1"; acceptance="$2"; upstream="$3"; resultdir="$4"
cd /lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 PS1="${PS1:-}"
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/00_admin/job_tmp XDG_CACHE_HOME=/lustre/users/u21111210118/projects/test9/env/cache
export LD_LIBRARY_PATH="/usr/local/nvidia/lib:/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}"
source /opt/app/conda/etc/profile.d/conda.sh
conda activate /lustre/users/u21111210118/projects/test9/env/core
args=(--stage "$stage" --preflight-acceptance "$acceptance" --upstream "$upstream" --output-dir "$resultdir")
if [[ $# == 6 ]]; then args+=(--design-stage-result "$5" --design-audit-acceptance "$6"); fi
srun --cpu-bind=cores /lustre/users/u21111210118/projects/test9/env/core/bin/python -B "/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/frozen/physical_gate_v3_13294/e2e_model_stage.py" "${args[@]}"
