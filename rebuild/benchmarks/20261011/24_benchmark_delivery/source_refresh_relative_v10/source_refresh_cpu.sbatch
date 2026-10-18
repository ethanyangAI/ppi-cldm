#!/bin/bash
#SBATCH --job-name=test9_source_relative_v10
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=00:15:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/source_relative_v10_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/source_relative_v10_%j.err
set -euo pipefail
MODE="${1:-contracts}"
[[ "$MODE" == contracts || "$MODE" == audit ]]
export PS1="${PS1:-}"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
unset PYTHONPATH
ROOT=/lustre/users/u21111210118/projects/test9
SOURCE_PACKAGE=$ROOT/steps/24_benchmark_delivery/pending/source_refresh_relative_v10
SNAPSHOT=$ROOT/steps/24_benchmark_delivery/frozen/source_refresh_relative_v10_${SLURM_JOB_ID}/code
OUT=$ROOT/steps/24_benchmark_delivery/runs/source_relative_contracts_${SLURM_JOB_ID}
export TMPDIR=$ROOT/steps/24_benchmark_delivery/tmp/source_relative_v10_${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
[[ ! -e "$SNAPSHOT" ]]
mkdir -p "$SNAPSHOT"
for NAME in source_delivery_refresh_v10.py historical_archive_member_context.py relative_receipt_policy.py test_relative_receipt_policy.py source_refresh_bootstrap.py source_refresh_cpu.sbatch HANDOFF.md delivery_core.py delivery_graph_v2.py provenance_aliases_v2.py native_resource_closure_v2.py reference_source_delivery_refresh_v1.py; do
 cp "$SOURCE_PACKAGE/$NAME" "$SNAPSHOT/$NAME"
done
chmod -R a-w "$SNAPSHOT"
PYTHON=$ROOT/env/core/bin/python
"$PYTHON" "$SNAPSHOT/source_refresh_bootstrap.py" --out "$OUT"
if [[ "$MODE" == audit ]]; then
 "$PYTHON" "$SNAPSHOT/source_delivery_refresh_v10.py" audit --software-acceptance "$OUT/acceptance.json" --out "$ROOT/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_${SLURM_JOB_ID}"
fi
