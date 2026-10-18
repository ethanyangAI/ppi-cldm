#!/bin/bash
#SBATCH --job-name=test9_formal_failed_atom_coverage_v1
#SBATCH --partition=organ
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=00:10:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9
#SBATCH --output=/lustre/users/u21111210118/projects/test9/logs/formal-failed-atom-coverage-%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/logs/formal-failed-atom-coverage-%j.err
set -euo pipefail
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1
unset PYTHONPATH
task_root=/lustre/users/u21111210118/projects/test9
export TMPDIR="$task_root/steps/24_benchmark_delivery/tmp/formal_failed_atom_coverage_${SLURM_JOB_ID}"
mkdir -p "$TMPDIR"
exec "$task_root/env/rfd/bin/python" "$task_root/steps/24_benchmark_delivery/pending/formal_failed_atom_coverage_diagnostic_v1/diagnostic.py" --out "$task_root/steps/24_benchmark_delivery/runs/formal_failed_atom_coverage_${SLURM_JOB_ID}"
