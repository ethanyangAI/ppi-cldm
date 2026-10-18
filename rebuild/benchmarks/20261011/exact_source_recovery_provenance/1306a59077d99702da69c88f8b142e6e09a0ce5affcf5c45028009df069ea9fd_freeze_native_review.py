import os,sys,shutil,json
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
sys.path.insert(0,str(R/"source/rebuild"))
import benchmark_common_review as original
from screening_transfer import rec,read,dump
original.cpu()
jid=os.environ["SLURM_JOB_ID"]
snap=R/"steps/23_common_review/frozen"/("native_common_"+jid)
code=snap/"code";code.mkdir(parents=True,exist_ok=False)
files=[]
def copy(src,dest):
    src=Path(src);dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,dest)
    files.append(dict(original=rec(src),frozen=rec(dest)))
    return dest
for name in ["benchmark_common_review.py","screening_transfer.py","control_msa_check.py"]:
    copy(R/"source/rebuild"/name,code/name)
for src in sorted((R/"source/src/ppiblocker").rglob("*.py")):
    copy(src,code/"src/ppiblocker"/src.relative_to(R/"source/src/ppiblocker"))
copy(R/"vendor/IPSAE_6174cf9e71cb/ipsae.py",code/"vendor/ipsae.py")
copy(R/"steps/03_af2_restore/inference_env.sh",code/"runtime_entries/af2_inference_env.sh")
copy(R/"env/colabfold/bin/colabfold_batch",code/"runtime_entries/colabfold_batch")
copy(R/"env/boltz/bin/boltz",code/"runtime_entries/boltz")
common=code/"benchmark_common_review.py"
s=common.read_text()
s=s.replace('STEP=ROOT/"steps/23_common_review"','STEP=ROOT/"steps/23_common_review"\nFROZEN_DIR=Path(__file__).resolve().parent')
s=s.replace('sys.path.insert(0,str(ROOT/"source/src"))','sys.path.insert(0,str(FROZEN_DIR/"src"))')
s=s.replace('ROOT/"source/rebuild/screening_transfer.py"','FROZEN_DIR/"screening_transfer.py"')
s=s.replace('ROOT/"source/rebuild/control_msa_check.py"','FROZEN_DIR/"control_msa_check.py"')
s=s.replace('ROOT/"source/src/ppiblocker/structure.py"','FROZEN_DIR/"src/ppiblocker/structure.py"')
s=s.replace('ROOT/"steps/03_af2_restore/inference_env.sh"','FROZEN_DIR/"runtime_entries/af2_inference_env.sh"')
s=s.replace('ROOT/"env/colabfold/bin/colabfold_batch"','FROZEN_DIR/"runtime_entries/colabfold_batch"')
s=s.replace('ROOT/"env/boltz/bin/boltz"','FROZEN_DIR/"runtime_entries/boltz"')
s=s.replace('ROOT/"vendor"/("IPSAE_"+REVISION[:12])/"ipsae.py"','FROZEN_DIR/"vendor/ipsae.py"')
s=s.replace('str(ROOT/"source/rebuild"),job["input"]["path"]','str(FROZEN_DIR),job["input"]["path"]')
s=s.replace('method_origin_present=False)','method_origin_present=False,frozen_source_bundle=rec(FROZEN_DIR.parent/"source_bundle.json"))')
s=s.replace('allocation=allocated,runs=runs)','allocation=allocated,runs=runs,source=plan["source"],frozen_source_bundle=plan["frozen_source_bundle"],runtime_locks=plan["runtime_locks"],receipt_policy="CPU_PRECOMPUTED_SOURCE_AND_DEPENDENCY_HASH_REFERENCES_NO_GPU_HASH_TASK")')
common.write_text(s)
for item in files:
    item["frozen"]=rec(item["frozen"]["path"])
bundle=snap/"source_bundle.json"
dump(bundle,dict(status="IMMUTABLE_COMMON_REVIEW_SOURCE_BUNDLE",created_utc=original.now(),freeze_job=jid,files=files,source=rec(common),runtime_dependency_policy="Original isolated environment versions and model assets verified by frozen prepare and recorded in inference plan",scope="NATIVE_RECOVERY_CONTROLS_ONLY_SAME_EXACT_QUERY_MSA_GATE_COHORT"))
for item in files:
    path=Path(item["frozen"]["path"])
    path.chmod(0o555 if path.name in ["boltz","colabfold_batch"] else 0o444)
bundle.chmod(0o444)
for name in list(sys.modules):
    if name in ["benchmark_common_review","screening_transfer","control_msa_check"] or name=="ppiblocker" or name.startswith("ppiblocker."):
        del sys.modules[name]
sys.path.insert(0,str(code))
import benchmark_common_review as frozen
tests=frozen.run_tests()
if tests["status"]!="PASSED" or tests["n_tests"]!=10:raise ValueError("Frozen source tests failed")
out=R/"steps/23_common_review/runs"/("native_controls_frozen_"+jid);out.mkdir(exist_ok=False)
registry=R/"steps/23_common_review/inputs/registry7_bridge13010.json"
msa=R/"steps/23_common_review/runs/msa_content_12983/msa.json"
prior=R/"steps/23_common_review/runs/native_controls_13018"
plan=out/"inference_plan.json"
prepared=frozen.prepare(registry,msa,prior/"native_controls_only.json",plan,prior/"predeclared_gate.json")
p=read(plan)
old=read(prior/"inference_plan.json")
if [frozen.job_signature(j) for j in p["jobs"]]!=[frozen.job_signature(j) for j in old["jobs"]]:
    raise ValueError("Rebase changed input content or fixed protocol")
if len(p["jobs"])!=20 or sum(j["expected_models"] for j in p["jobs"])!=74:raise ValueError("Native fixed denominator changed")
logs=out/"logs";logs.mkdir()
launcher=out/"native_review.sbatch"
launch="""#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --array=0-19%1
#SBATCH --job-name=test9_native_common_review
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/23_common_review
#SBATCH --output=__OUT__/logs/native_%A_%a.log
set -euo pipefail
export PS1="DOLLAR{PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
PLAN=__PLAN__
CODE=__CODE__
INDEX="DOLLAR{SLURM_ARRAY_TASK_ID:?}"
"DOLLARR/env/core/bin/python" -c 'import sys;sys.path.insert(0,sys.argv[1]);from benchmark_common_review import allocation;allocation(1)' "DOLLARCODE"
ENGINE=$("DOLLARR/env/core/bin/python" -c 'import json,sys;print(json.load(open(sys.argv[1]))["jobs"][int(sys.argv[2])]["engine"])' "DOLLARPLAN" "DOLLARINDEX")
if [[ "DOLLARENGINE" == af2 ]]; then
  source "DOLLARCODE/runtime_entries/af2_inference_env.sh"
elif [[ "DOLLARENGINE" != boltz ]]; then
  printf 'Unknown frozen engine: %s\n' "DOLLARENGINE" >&2
  exit 2
fi
"DOLLARR/env/core/bin/python" "DOLLARCODE/benchmark_common_review.py" worker --plan "DOLLARPLAN" --index "DOLLARINDEX" --out __OUT__/raw
""".replace("__OUT__",str(out)).replace("__PLAN__",str(plan)).replace("__CODE__",str(code)).replace("DOLLAR","$")
launcher.write_text(launch);launcher.chmod(0o444)
dump(out/"freeze_receipt.json",dict(status="READY_FOR_ROOT_REVIEW_AND_GPU_SUBMISSION_NOT_SUBMITTED",created_utc=frozen.now(),cpu_job=jid,source_bundle=rec(bundle),source=rec(common),plan=rec(plan),analysis=rec(out/"analysis_plan.json"),membership=rec(out/"membership.json"),gpu_launcher=rec(launcher),test_results=tests,denominator=dict(entities=len(p["entities"]),jobs=len(p["jobs"]),models=sum(j["expected_models"] for j in p["jobs"]),array_concurrency=1,global_gpu_cap_parent_controlled=2),input_rebase_from=rec(prior/"inference_plan.json"),input_content_and_protocol_unchanged=True,per_index_output="raw/job_key each immutable unique index",gpu_hash_policy="CPU hashes frozen before submission; worker copies exact hash references"))
print(json.dumps(read(out/"freeze_receipt.json"),ensure_ascii=False,indent=2),flush=True)

