#!/bin/bash
#SBATCH --job-name=ppi_formal_postprocess_contracts
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:20:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/formal_postprocess_contracts_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/formal_postprocess_contracts_%j.err
set -euo pipefail
export PS1="${PS1:-}"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
SNAPSHOT="$R/steps/24_benchmark_delivery/frozen/formal_postprocess_v1_${SLURM_JOB_ID}/code"
mkdir -p "$SNAPSHOT" "$R/steps/24_benchmark_delivery/tmp"
cp "$R/steps/24_benchmark_delivery/code/formal_postprocess_v1.py" "$R/steps/24_benchmark_delivery/code/formal_postprocess_contracts_v1.py" "$R/steps/24_benchmark_delivery/code/formal_postprocess_cpu_v1.sbatch" "$R/steps/24_benchmark_delivery/code/formal_postprocess_contracts_v1.sbatch" "$SNAPSHOT/"
"$R/env/core/bin/python" "$SNAPSHOT/formal_postprocess_v1.py" freeze-snapshot --out "$SNAPSHOT/source_snapshot.json"
export FORMAL_POSTPROCESS_TEST_OUTPUT="$R/steps/24_benchmark_delivery/runs/formal_postprocess_contracts_${SLURM_JOB_ID}"
"$R/env/core/bin/python" "$SNAPSHOT/formal_postprocess_contracts_v1.py"

