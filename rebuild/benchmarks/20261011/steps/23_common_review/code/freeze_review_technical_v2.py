import importlib.util,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
R=Path("/lustre/users/u21111210118/projects/test9")
STEP=R/"steps/23_common_review"
BBF=STEP/"bbf_diagnostics/frozen/bbf_common_13061"
NATIVE=STEP/"runs/native_controls_frozen_13051"
sys.path.insert(0,str(BBF/"code"))
from screening_transfer import rec,verify,read,dump
from benchmark_common_review import now,SETTINGS,job_signature
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
w=module("technical_allocation",STEP/"code/common_allocation_v2.py")
cpu=w.allocation(0)
if os.environ.get("CUDA_VISIBLE_DEVICES","")!="":raise ValueError("CPU-only freeze CUDA mask required")
out=STEP/"runs"/("allocation_v2_"+os.environ["SLURM_JOB_ID"]);out.mkdir(exist_ok=False);(out/"code").mkdir()
guard=dict(path=str(w.GUARD),bytes=84446,sha256="b37227bd862ee1425a59f5308be1ee3f4824042dea5d71c1269ad0f406b318f9")
verify(guard);gm=read(w.GUARD.parent/"snapshot_manifest.json")
if gm["n_tests"]!=74:raise ValueError("Final v4 tested snapshot required")
for item in gm["files"]:verify(item["snapshot"])
verify(gm["contract_tests"])
science=dict(path=str(w.COMMON),bytes=59077,sha256="876d29f9b8a20cf3f8bbf526262de96b1071a30b47590b632e5d31f97c362391")
verify(science)
nativeplan=dict(path=str(NATIVE/"inference_plan.json"),bytes=30895,sha256="9c90d720d39f306e9c601a8281afaca0d29ac986872805dd6b913eb8f2e9373b")
verify(nativeplan);np=read(nativeplan["path"])
if np["settings"]!=SETTINGS or len(np["jobs"])!=20:raise ValueError("Native scientific contract drift")
bundle=read(BBF/"source_bundle.json")
for name in ["plan","source","common_source","backend","backend_env","feature_manifest","feature_acceptance"]:verify(bundle[name])
pilot=STEP/"bbf_diagnostics/runs/worker_validation_13096/acceptance.json"
pr=read(pilot)
if pr["status"]!="BBF_FIRST_JOB_FIVE_MODELS_CPU_CONTENT_ACCEPTED_NOT_FULL110" or pr["n_models_accepted"]!=5:raise ValueError("Actual first5 CPU acceptance required")
for name in ["worker_audit","score","score_acceptance"]:verify(pr[name])
audit=module("audit_bbf_workers",STEP/"bbf_diagnostics/code/audit_bbf_workers.py")
raw0=STEP/"bbf_diagnostics/runs/bbf_launch_13067/raw"
j0=read(bundle["plan"]["path"])["jobs"][0]
if j0["job_key"]!=pr["accepted_pilot_results"][0]["id"]+"_"+pr["accepted_pilot_results"][0]["arm"]:raise ValueError("Only index0 was accepted")
class Contracts(unittest.TestCase):
    def row(self,job,state="RUNNING",gpu=1,task=19):
        return "JobId="+str(job)+" ArrayJobId=13059 ArrayTaskId="+str(task)+" JobState="+state+" TRES=cpu=4,node=1,billing=4"+(",gres/gpu="+str(gpu) if gpu else "")+"\n"
    def env(self):return {"SLURM_JOB_ID":"13059","SLURM_ARRAY_JOB_ID":"13059","SLURM_ARRAY_TASK_ID":"19"}
    def test_multiline_sibling_first_and_last(self):
        own=self.row(13059);bad=self.row(13100,"FAILED",0,18)
        for text in [own+bad,bad+own]:
            result=w.scheduler_receipt(text,1,self.env());self.assertEqual(result["scheduler_record"].strip(),own.strip());self.assertEqual(result["scheduler_record_full"],text)
    def test_own_failed_not_sibling_running(self):
        with self.assertRaises(ValueError):w.scheduler_receipt(self.row(13100)+self.row(13059,"FAILED"),1,self.env())
    def test_own_gpu0_not_sibling_gpu1(self):
        with self.assertRaises(ValueError):w.scheduler_receipt(self.row(13100)+self.row(13059,gpu=0),1,self.env())
    def test_duplicate_or_unknown_raw_identity(self):
        for text in [self.row(13059)*2,self.row(13100)]:
            with self.assertRaises(ValueError):w.scheduler_receipt(text,1,self.env())
    def test_array_alias_mismatch(self):
        with self.assertRaises(ValueError):w.scheduler_receipt(self.row(13059,task=18),1,self.env())
    def test_no_invoking_identity(self):
        with self.assertRaises(RuntimeError):w.scheduler_receipt(self.row(13059),1,{})
    def test_actual_pilot_partial_denominator(self):
        result=audit.audit(bundle["plan"]["path"],[str(raw0)],out/"contract_pilot_audit.json")
        self.assertEqual((result["jobs_present_accepted"],result["models_raw_valid"],result["models_expected"]),(1,5,110))
    def test_duplicate_worker_roots_rejected(self):
        with self.assertRaisesRegex(ValueError,"Duplicate actual worker"):audit.audit(bundle["plan"]["path"],[str(raw0),str(raw0)],out/"duplicate_should_not_exist.json")
    def test_all110_cannot_accept_first5(self):
        with self.assertRaisesRegex(ValueError,"all22"):audit.audit(bundle["plan"]["path"],[str(raw0)],out/"full110_should_not_exist.json",True)
    def test_wrong_declared_units_rejected(self):
        with tempfile.TemporaryDirectory(prefix="CONTRACT_FIXTURE_",dir=out) as td:
            td=Path(td);p=td/j0["job_key"];p.mkdir();worker=read(raw0/j0["job_key"]/"worker.json")
            conf=read(worker["models"][0]["scores_path"]);conf["plddt_units"]="0-1";dump(p/"wrong_units.json",conf)
            worker["models"][0]["scores_path"]=str(p/"wrong_units.json");dump(p/"worker.json",worker)
            with self.assertRaisesRegex(ValueError,"units missing"):audit.audit(bundle["plan"]["path"],[str(td)],out/"wrong_units_should_not_exist.json")
suite=unittest.defaultTestLoader.loadTestsFromTestCase(Contracts)
rr=unittest.TextTestRunner(verbosity=2).run(suite)
if not rr.wasSuccessful():raise RuntimeError("Technical/downstream contract failure")
wrapper=out/"code/common_allocation_v2.py";shutil.copy2(STEP/"code/common_allocation_v2.py",wrapper);wrapper.chmod(0o444)
ah=out/"code/audit_bbf_workers.py";shutil.copy2(STEP/"bbf_diagnostics/code/audit_bbf_workers.py",ah);ah.chmod(0o444)
context=out/"code/wrapper_receipts.json"
dump(context,dict(status="CPU_PREHASHED_TECHNICAL_ALLOCATION_WRAPPER_REFERENCES",wrapper=rec(wrapper),scientific_source=science,scientific_plan=nativeplan,
                 settings=SETTINGS,native_job_signatures=[job_signature(j) for j in np["jobs"]],guard=guard,
                 guard_snapshot_manifest=rec(w.GUARD.parent/"snapshot_manifest.json"),guard_contract_tests=gm["contract_tests"]))
context.chmod(0o444)
bb=out/"bbf_remaining";bb.mkdir();(bb/"logs").mkdir()
nc=out/"native_index19";nc.mkdir();(nc/"logs").mkdir()
common_header="""#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/23_common_review
"""
env="""set -euo pipefail
export PS1="DOLLAR{PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
R=/lustre/users/u21111210118/projects/test9
INDEX="DOLLAR{SLURM_ARRAY_TASK_ID:?}"
"""
bs=common_header+"#SBATCH --array=1-21%1\n#SBATCH --job-name=test9_bbf_remaining_v4_guard\n#SBATCH --output="+str(bb)+"/logs/bbf_%A_%a.log\n"+env
bs+="PLAN="+bundle["plan"]["path"]+"\n"
bs+='JOBKEY=$("DOLLARR/env/core/bin/python" -c \'import json,sys;print(json.load(open(sys.argv[1]))["jobs"][int(sys.argv[2])]["job_key"])\' "DOLLARPLAN" "DOLLARINDEX")\n'
bs+='RAWDIR="'+str(bb)+'/raw/DOLLARJOBKEY"\nif [[ -e "DOLLARRAWDIR" ]]; then exit 2; fi\nsource '+bundle["backend_env"]["path"]+"\n"
bs+='python '+bundle["backend"]["path"]+' predict --plan "DOLLARPLAN" --job-key "DOLLARJOBKEY" --output-dir "DOLLARRAWDIR" --features-manifest '+bundle["feature_manifest"]["path"]+" --guard-source "+guard["path"]+" --expected-gpu-name 'NVIDIA A100-PCIE-40GB'\n"
bs+="cp --no-clobber "+str(bb/"worker_reference_receipts.json")+' "DOLLARRAWDIR/worker_reference_receipts.json"\n'
# No old common allocation preflight: immutable backend invokes v4 ownership guard before JAX.
bl=bb/"bbf_gpu_remaining.sbatch";bl.write_text(bs.replace("DOLLAR","$"));bl.chmod(0o444)
bc=dict(status="CPU_FROZEN_BBF_REMAINING21_REFERENCE_RECEIPTS",plan=bundle["plan"],source_bundle=rec(BBF/"source_bundle.json"),backend=bundle["backend"],backend_env=bundle["backend_env"],features=bundle["feature_manifest"],feature_acceptance=bundle["feature_acceptance"],budget_guard=guard,guard_snapshot_manifest=rec(w.GUARD.parent/"snapshot_manifest.json"),hardware_inventory=bundle["hardware_inventory"],first5_acceptance=rec(pilot),old_index0_worker=rec(raw0/j0["job_key"]/"worker.json"),new_launcher=rec(bl))
dump(bb/"worker_reference_receipts.json",bc);(bb/"worker_reference_receipts.json").chmod(0o444)
ns=common_header+"#SBATCH --array=19-19%1\n#SBATCH --job-name=test9_native19_allocation_v2\n#SBATCH --output="+str(nc)+"/logs/native_%A_%a.log\n"+env
ns+='PLAN='+nativeplan["path"]+'\nCODE='+str(w.COMMON.parent)+'\n'
ns+='ENGINE=$("DOLLARR/env/core/bin/python" -c \'import json,sys;print(json.load(open(sys.argv[1]))["jobs"][int(sys.argv[2])]["engine"])\' "DOLLARPLAN" "DOLLARINDEX")\n'
ns+='if [[ "DOLLARENGINE" == af2 ]]; then source "DOLLARCODE/runtime_entries/af2_inference_env.sh"; elif [[ "DOLLARENGINE" != boltz ]]; then exit 2; fi\n'
ns+='"DOLLARR/env/core/bin/python" '+str(wrapper)+' worker --plan "DOLLARPLAN" --index "DOLLARINDEX" --out '+str(nc/"raw")+'\n'
nl=nc/"native19_gpu.sbatch";nl.write_text(ns.replace("DOLLAR","$"));nl.chmod(0o444)
ds="""#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G
#SBATCH --time=00:30:00
#SBATCH --job-name=test9_bbf110_cpu_content_review
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/23_common_review
#SBATCH --output=__OUT__/bbf110_review_%j.log
set -euo pipefail
export PS1="DOLLAR{PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=""
unset PYTHONPATH
__PYTHON__ __AUDIT__ --plan __PLAN__ --raw-root __OLDROOT__ --raw-root __NEWROOT__ --out __OUT__/bbf110_review_DOLLAR{SLURM_JOB_ID}/worker_audit.json --require-all --score-and-verify
""".replace("__OUT__",str(out)).replace("__PYTHON__",str(R/"env/core/bin/python")).replace("__AUDIT__",str(ah)).replace("__PLAN__",bundle["plan"]["path"]).replace("__OLDROOT__",str(raw0)).replace("__NEWROOT__",str(bb/"raw")).replace("DOLLAR","$")
dl=out/"bbf110_downstream_cpu.sbatch";dl.write_text(ds);dl.chmod(0o444)
for script in [bl,nl,dl]:subprocess.run(["bash","-n",str(script)],check=True)
# Rebase technical references only; no scientific source, query, model settings or plan changes.
accept=dict(status="TECHNICAL_V2_NATIVE19_AND_BBF_REMAINING21_FROZEN_READY_FOR_ROOT_GPU_SUBMISSION",
            created_utc=now(),CPU_allocation=cpu,source=rec(__file__),science_source_unchanged=science,native_plan_unchanged=nativeplan,
            BBF_plan_unchanged=bundle["plan"],wrapper=rec(wrapper),wrapper_references=rec(context),
            guard=guard,guard_snapshot_manifest=rec(w.GUARD.parent/"snapshot_manifest.json"),guard_contract_tests=gm["contract_tests"],n_guard_tests=74,
            contract_tests=dict(status="PASSED",n_tests=rr.testsRun),contract_pilot_audit=rec(out/"contract_pilot_audit.json"),first5_acceptance=rec(pilot),
            BBF_launcher=rec(bl),BBF_worker_references=rec(bb/"worker_reference_receipts.json"),BBF_indices=list(range(1,22)),BBF_expected_new_models=105,
            native19_launcher=rec(nl),native19_job_signature=job_signature(np["jobs"][19]),
            BBF_downstream_launcher=rec(dl),BBF_downstream_helper=rec(ah),
            global_GPU_cap=2,GPU_submitted_by_subagent=False,science_or_frozen13051_changed=False,
            purpose="Scheduler ownership correction only; development diagnostics are not independent biological validation")
dump(out/"acceptance.json",accept);(out/"acceptance.json").chmod(0o444)
print(json.dumps(accept,ensure_ascii=False,indent=2),flush=True)
