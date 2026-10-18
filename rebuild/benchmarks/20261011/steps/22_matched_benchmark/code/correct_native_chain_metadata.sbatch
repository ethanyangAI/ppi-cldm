#!/bin/bash
#SBATCH --job-name=t9-chain-metadata
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark
#SBATCH --output=/lustre/users/u21111210118/projects/test9/logs/chain-metadata-%j.out
set -euo pipefail
export PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/tmp/chain-metadata-${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
scontrol show job "$SLURM_JOB_ID" -o > "$TMPDIR/scontrol_start.txt"
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/correct_native_chain_metadata.py --previous /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/input_preparation/prepared_7_13010/prepared_inputs.json --native-proof /lustre/users/u21111210118/projects/test9/steps/21_method_runtime/runs/pilot_v6_contracts_13092/outputs/actual_rfd_identity_proof.json --out /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_${SLURM_JOB_ID}

