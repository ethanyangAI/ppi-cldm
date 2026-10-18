#!/bin/bash
#SBATCH --job-name=ppi_delivery_v2_contracts
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:15:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/contracts_v2_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/contracts_v2_%j.err
set -euo pipefail
export PS1="${PS1:-}"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/contracts_v2_${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
SNAPSHOT=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/delivery_v2_${SLURM_JOB_ID}/code
mkdir -p "$SNAPSHOT"
cp /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/code/*.py "$SNAPSHOT/"
cp /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/code/*.md "$SNAPSHOT/"
cp /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/code/contracts_v2.sbatch "$SNAPSHOT/"
chmod -R a-w "$SNAPSHOT"
export DELIVERY_V2_OUTPUT=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/contracts_v2_${SLURM_JOB_ID}
/lustre/users/u21111210118/projects/test9/env/core/bin/python "$SNAPSHOT/test_delivery_v2.py"
/lustre/users/u21111210118/projects/test9/env/core/bin/python "$SNAPSHOT/delivery_graph_v2.py" source-audit --root /lustre/users/u21111210118/projects/test9 --out "$DELIVERY_V2_OUTPUT/source_inclusion_v2.json" --runtime-settings pilot_v7
/lustre/users/u21111210118/projects/test9/env/core/bin/python "$SNAPSHOT/delivery_graph_v2.py" historical-aliases --root /lustre/users/u21111210118/projects/test9 --out "$DELIVERY_V2_OUTPUT/historical_aliases"

