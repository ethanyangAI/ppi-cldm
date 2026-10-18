#!/usr/bin/env bash
#SBATCH --job-name=t9-method-smoke
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --gres=gpu:1
#SBATCH --oversubscribe
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/gpu_smoke_%j.out
set -euo pipefail
: "${BENCHMARK_SMOKE_CONFIG:?}"
: "${BENCHMARK_SMOKE_CONFIG_SHA256:?}"
: "${BENCHMARK_SMOKE_TARGET_MANIFEST:?}"
: "${BENCHMARK_SMOKE_SEED:?}"
: "${BENCHMARK_SMOKE_ATTEMPT_DIR:?}"
: "${BENCHMARK_SMOKE_METHOD:?}"
R=/lustre/users/u21111210118/projects/test9
export TMPDIR="$R/steps/21_method_runtime/work" XDG_CACHE_HOME="$R/env/cache"
case "$BENCHMARK_SMOKE_METHOD" in
 rf_diffusion) source "$R/steps/21_method_runtime/code/rfd_env.sh" ;;
 bindcraft) source "$R/steps/21_method_runtime/code/bindcraft_env.sh" ;;
 *) echo "Unsupported method"; exit 2 ;;
esac
printf 'CUDA_VISIBLE_DEVICES=%s\nSLURM_JOB_GPUS=%s\nSLURM_STEP_GPUS=%s\n' "${CUDA_VISIBLE_DEVICES:-}" "${SLURM_JOB_GPUS:-}" "${SLURM_STEP_GPUS:-}"
nvidia-smi --query-gpu=index,name,memory.total,uuid --format=csv,noheader,nounits
python "$R/source/rebuild/benchmark_runtime.py" method-attempt --method "$BENCHMARK_SMOKE_METHOD" --target-manifest "$BENCHMARK_SMOKE_TARGET_MANIFEST" --attempt-dir "$BENCHMARK_SMOKE_ATTEMPT_DIR" --seed "$BENCHMARK_SMOKE_SEED" --config "$BENCHMARK_SMOKE_CONFIG" --config-sha256 "$BENCHMARK_SMOKE_CONFIG_SHA256"
