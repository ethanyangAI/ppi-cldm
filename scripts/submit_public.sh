#!/usr/bin/env bash
set -euo pipefail
ROOT="/lustre/users/u21111210118/projects/test9"
if [[ $# != 2 ]]; then echo "Usage: $0 prepare|predict|design|evaluate|reevaluate CONFIG_OR_MANIFEST" >&2; exit 2; fi
stage="$1"; input="$(realpath "$2")"
case "$input" in "$ROOT"/*) ;; *) echo "Input must belong to test9" >&2; exit 2;; esac
case "$stage" in
 prepare|reevaluate) resources=(-p interactive -c 2 --mem=8G -t 01:00:00);;
 predict|design|evaluate) resources=(-p organ --gres=gpu:1 --oversubscribe -c 4 --mem=64G -t 1-00:00:00);;
 *) echo "Unsupported stage" >&2; exit 2;;
esac
mkdir -p "$ROOT/00_admin/submissions" "$ROOT/00_admin/job_logs" "$ROOT/env/cache" "$ROOT/00_admin/job_tmp"
script="$(mktemp "$ROOT/00_admin/submissions/${stage}.XXXXXX.sh")"
cat > "$script" <<'BODY'
#!/usr/bin/env bash
set -euo pipefail
ROOT="/lustre/users/u21111210118/projects/test9"
cd "$ROOT"
export PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR="$ROOT/00_admin/job_tmp" XDG_CACHE_HOME="$ROOT/env/cache"
export LD_LIBRARY_PATH="/usr/local/nvidia/lib:/usr/local/nvidia/lib64:${LD_LIBRARY_PATH:-}"
export PS1="${PS1:-}"
source /opt/app/conda/etc/profile.d/conda.sh
conda activate "$ROOT/env/core"
BODY
printf 'srun --cpu-bind=cores ppiblocker --root %q %q %q\n' "$ROOT" "$stage" "$input" >> "$script"
sbatch --account=u21111210118 --qos=normal "${resources[@]}" --job-name="test9-$stage" --output="$ROOT/00_admin/job_logs/${stage}_%j.log" "$script"

