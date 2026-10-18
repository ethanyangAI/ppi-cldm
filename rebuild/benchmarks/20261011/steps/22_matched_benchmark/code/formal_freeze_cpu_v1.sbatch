#!/bin/bash
#SBATCH --job-name=test9_formal_freeze_cpu
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark
#SBATCH --output=/lustre/users/u21111210118/projects/test9/logs/formal-freeze-%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/logs/formal-freeze-%j.err
set -euo pipefail
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu
unset PYTHONPATH
export TMPDIR="/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/tmp/formal-freeze-${SLURM_JOB_ID}"
mkdir -p "$TMPDIR"
R=/lustre/users/u21111210118/projects/test9
RF="$R/steps/21_method_runtime/runs/actual_native_v8_13213/outputs/rf/acceptance.json"
BC="${BC_ENGINEERING_ACCEPTANCE:?Current corrected BC acceptance required}"
BUDGET="$R/steps/22_matched_benchmark/code/engineering13175_accounting_13209/independent_acceptance.json"
OUT="$R/steps/22_matched_benchmark/formal_freeze_${SLURM_JOB_ID}"
mkdir -p "$OUT"
# Both exact reviewed original helper bytes are checked inside this CPU allocation.
printf '%s\n' '0cb377a068ce893b08637ae50142dd5ac7a48f735279b74fecdde2ab2f37dd49  '"$R/steps/22_matched_benchmark/code/combine_engineering_acceptance_v1.py" 'e23f09c1f01f1459fe1281f2648dd1e3c0d7d0e9704b9024acdaf732b7c3b3d8  '"$R/steps/22_matched_benchmark/code/freeze_formal_benchmark_v3.py" | sha256sum -c -
"$R/env/core/bin/python" "$R/steps/22_matched_benchmark/code/combine_engineering_acceptance_v1.py" --rf "$RF" --bc "$BC" --accounting "$BUDGET" --out "$OUT/engineering_combined.json"
"$R/env/core/bin/python" "$R/steps/22_matched_benchmark/code/freeze_formal_benchmark_v3.py" --engineering-acceptance "$OUT/engineering_combined.json" --out "$OUT/plan"

