#!/bin/bash
#SBATCH --job-name=test9_reference_free_e2e_audit
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=04:00:00
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/logs/final_audit_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/logs/final_audit_%j.err
set -euo pipefail
if [[ $# != 5 ]]; then echo "Use: CPU_PREFLIGHT_ACCEPTANCE EXACT_DESIGN_STAGE_RESULT EXACT_DESIGN_CPU_ACCEPTANCE EXACT_EVALUATE_STAGE_RESULT NEW_FINAL_AUDIT_DIR" >&2; exit 2; fi
cd /lustre/users/u21111210118/projects/test9
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/00_admin/job_tmp
/lustre/users/u21111210118/projects/test9/env/core/bin/python -B "/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/frozen/physical_gate_v3_13294/e2e_final_audit_cpu.py" --preflight-acceptance "$1" --design-stage-result "$2" --design-audit-acceptance "$3" --evaluate-stage-result "$4" --output-dir "$5"
