#!/bin/bash
#SBATCH --job-name=test9_final_scientific_report_cpu
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final_scientific_report_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final_scientific_report_%j.err
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9
MODE="${1:-contracts}"
if [[ "$#" -gt 0 ]]; then shift; fi
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR="$R/steps/24_benchmark_delivery/tmp/final_scientific_report_${SLURM_JOB_ID}"
mkdir -p "$TMPDIR"
OUT="$R/steps/24_benchmark_delivery/runs/final_scientific_report_${MODE}_${SLURM_JOB_ID}"
if [[ "$MODE" == contracts ]]; then
 test "$#" -eq 0
 exec "$R/env/core/bin/python" "$R/steps/24_benchmark_delivery/pending/final_scientific_report_v1/final_scientific_report.py" contracts --out "$OUT"
elif [[ "$MODE" == build || "$MODE" == qa ]]; then
 exec "$R/env/core/bin/python" "${FINAL_SCIENTIFIC_REPORT_ENTRY:?exact CPU accepted frozen report entry required}" "$MODE" "$@" --out "$OUT"
else exit 2; fi
