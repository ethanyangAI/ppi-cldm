#!/usr/bin/env bash
# HISTORICAL_WRAPPER_DISABLED: do not translate old resource semantics automatically.
printf '%s\n' 'Historical Fudan wrapper disabled. Use scripts/submit_public.sh with the reviewed public-cluster config and explicit manifests.' >&2
exit 2

# Original body retained below for audit only; unreachable by this wrapper.
#!/usr/bin/env bash
set -euo pipefail
ROOT="${PPIBLOCKER_ROOT:-/lustre/users/u21111210118/projects/test9}"
stage="${1:?Usage: submit_stage.sh prepare|predict|design|evaluate|reevaluate CONFIG_OR_MANIFEST}"
input="${2:?Explicit config or upstream manifest required}"
case "$stage" in
 prepare|reevaluate) resources=(-p c02 -w c02n02 -c 4 --mem=12G -t 01:00:00);;
 predict|design|evaluate) resources=(-p 8gpu --gres=gpu:1 -c 8 --mem=48G -t 06:00:00);;
 *) echo "Unknown stage" >&2;exit 2;;
esac
mkdir -p "$ROOT/steps/00_submission/logs"
sbatch "${resources[@]}" -J "t9_${stage}" \
 -o "$ROOT/steps/00_submission/logs/%j.out" -e "$ROOT/steps/00_submission/logs/%j.err" \
 "$ROOT/source/scripts/stage_job.sh" "$ROOT" "$stage" "$input"

