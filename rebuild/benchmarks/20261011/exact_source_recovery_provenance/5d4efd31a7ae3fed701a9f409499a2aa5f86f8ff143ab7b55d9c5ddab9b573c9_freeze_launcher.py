import os,sys,json
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
snap=R/"steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061"
sys.path.insert(0,str(snap/"code"))
from screening_transfer import rec,read,verify,dump
from benchmark_common_review import cpu,now
cpu()
bundle=read(snap/"source_bundle.json")
for name in ["plan","source","common_source","backend","backend_env","feature_manifest","feature_acceptance"]:verify(bundle[name])
guard=dict(path=str(R/"steps/22_matched_benchmark/settings/pilot_budget_v2/source/paired_budget_benchmark.py"),bytes=78406,sha256="633075ce84aa554bfb74d3fc1ddf1cc033840e791335e5d3572ebd47c3dd7f3f")
verify(guard)
import importlib.util
spec=importlib.util.spec_from_file_location("frozen_owned_budget",guard["path"]);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
if not callable(getattr(mod,"gpu_ownership_guard",None)):raise ValueError("New ownership guard API absent")
out=R/"steps/23_common_review/bbf_diagnostics/runs"/("bbf_launch_"+os.environ["SLURM_JOB_ID"]);out.mkdir(parents=True,exist_ok=False);(out/"logs").mkdir()
context=out/"worker_reference_receipts.json"
dump(context,dict(status="CPU_FROZEN_WORKER_SOURCE_REFERENCE_RECEIPTS_NO_GPU_HASH",plan=bundle["plan"],source_bundle=rec(snap/"source_bundle.json"),scorer=bundle["source"],backend=bundle["backend"],backend_env=bundle["backend_env"],features=bundle["feature_manifest"],feature_acceptance=bundle["feature_acceptance"],budget_guard=guard,hardware_inventory=bundle["hardware_inventory"],source=rec(__file__)))
launcher=out/"bbf_gpu.sbatch"
s="""#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --array=0-21%1
#SBATCH --job-name=test9_bbf_development_input_diagnostic
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/23_common_review
#SBATCH --output=__OUT__/logs/bbf_%A_%a.log
set -euo pipefail
export PS1="DOLLAR{PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
PLAN=__PLAN__
INDEX="DOLLAR{SLURM_ARRAY_TASK_ID:?}"
CODE=__CODE__
"DOLLARR/env/core/bin/python" -c 'import sys;sys.path.insert(0,sys.argv[1]);from benchmark_common_review import allocation;allocation(1)' "DOLLARCODE"
JOBKEY=$("DOLLARR/env/core/bin/python" -c 'import json,sys;print(json.load(open(sys.argv[1]))["jobs"][int(sys.argv[2])]["job_key"])' "DOLLARPLAN" "DOLLARINDEX")
RAWDIR="__OUT__/raw/DOLLARJOBKEY"
if [[ -e "DOLLARRAWDIR" ]]; then
  printf 'Refusing pre-existing inference outdir: %s\n' "DOLLARRAWDIR" >&2
  exit 2
fi
source __ENV__
python __BACKEND__ predict --plan "DOLLARPLAN" --job-key "DOLLARJOBKEY" --output-dir "DOLLARRAWDIR" --features-manifest __FEATURES__ --guard-source __GUARD__ --expected-gpu-name NVIDIA\\ A100-PCIE-40GB
cp --no-clobber __CONTEXT__ "DOLLARRAWDIR/worker_reference_receipts.json"
""".replace("__OUT__",str(out)).replace("__PLAN__",bundle["plan"]["path"]).replace("__CODE__",str(snap/"code")).replace("__ENV__",bundle["backend_env"]["path"]).replace("__BACKEND__",bundle["backend"]["path"]).replace("__FEATURES__",bundle["feature_manifest"]["path"]).replace("__GUARD__",guard["path"]).replace("__CONTEXT__",str(context)).replace("DOLLAR","$")
launcher.write_text(s);launcher.chmod(0o444);context.chmod(0o444)
acceptance=dict(status="BBF110_FROZEN_SCIENTIFIC_INPUTS_FEATURES_OWNERSHIP_AND_LAUNCHER_READY_FOR_ROOT_GPU_REVIEW_NOT_SUBMITTED",created_utc=now(),CPU_job=os.environ["SLURM_JOB_ID"],source_bundle=rec(snap/"source_bundle.json"),plan=bundle["plan"],actual_feature_acceptance=bundle["feature_acceptance"],backend=bundle["backend"],budget_guard=guard,worker_references=rec(context),GPU_launcher=rec(launcher),jobs=22,models=110,array_concurrency=1,global_GPU_cap_parent_controlled=2,scope="DEVELOPMENT_ONLY_NOT_INDEPENDENT_TEST",GPU_submitted_by_subagent=False)
dump(out/"launch_acceptance.json",acceptance);print(json.dumps(acceptance,indent=2),flush=True)

