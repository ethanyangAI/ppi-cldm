#!/bin/bash
#SBATCH --job-name=test9_source_stage_exact
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:15:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/source_stage_%j.out
#SBATCH --error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/source_stage_%j.err
set -euo pipefail
export PS1="${PS1:-}"
export CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
: "${AUDITED_ENTRY:?Explicit accepted readonly adapter entry required}"
: "${ENTRY_SHA256:?Exact accepted adapter SHA required}"
: "${SOURCE_AUDIT:?Exact accepted source_inclusion_v3.json required}"
: "${SOURCE_AUDIT_SHA256:?Exact accepted source inclusion SHA required}"
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/source_stage_${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
OUT=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_stage_${SLURM_JOB_ID}
/lustre/users/u21111210118/projects/test9/env/core/bin/python - "$AUDITED_ENTRY" "$ENTRY_SHA256" "$SOURCE_AUDIT" "$SOURCE_AUDIT_SHA256" "$OUT" <<'PY'
import hashlib,pathlib,subprocess,sys
entry,sha,audit,audit_sha,out=sys.argv[1:]
root=pathlib.Path("/lustre/users/u21111210118/projects/test9").resolve()
p=pathlib.Path(entry)
if p.is_symlink() or not p.resolve().is_relative_to(root) or p.stat().st_mode&0o222:
 raise ValueError("Readonly accepted adapter within authority required")
if hashlib.sha256(p.read_bytes()).hexdigest()!=sha:
 raise ValueError("Stage entry source differs from accepted CPU audit")
subprocess.run([str(root/"env/core/bin/python"),entry,"stage","--audit",audit,"--audit-sha256",audit_sha,"--out",out],check=True)
PY

