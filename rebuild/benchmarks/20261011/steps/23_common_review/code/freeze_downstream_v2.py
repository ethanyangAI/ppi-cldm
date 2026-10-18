import importlib.util,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/23_common_review";CODE=S/"frozen/native_common_13051/code"
sys.path.insert(0,str(CODE));from screening_transfer import rec,verify,read,dump
def mod(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
native=mod("native_pipeline_ready",S/"code/native_review_pipeline_v2.py");cpu=native.allocation_cpu()
out=S/"runs"/("downstream_frozen_"+os.environ["SLURM_JOB_ID"]);out.mkdir(exist_ok=False);(out/"code").mkdir()
nh=out/"code/native_review_pipeline_v2.py";shutil.copy2(S/"code/native_review_pipeline_v2.py",nh);nh.chmod(0o444)
bh=out/"code/audit_bbf_workers_v2.py";shutil.copy2(S/"bbf_diagnostics/code/audit_bbf_workers_v2.py",bh);bh.chmod(0o444)
audit=mod("BBF_audit_ready",bh)
nativeplan=S/"runs/native_controls_frozen_13051/inference_plan.json";np=read(nativeplan)
plan=S/"bbf_diagnostics/frozen/bbf_common_13061/plan.json";bp=read(plan)
raw0=S/"bbf_diagnostics/runs/bbf_launch_13067/raw";key0=bp["jobs"][0]["job_key"]
class Contracts(unittest.TestCase):
    def test_plan_receipt_metadata_repair_only(self):
        original={"plan":list(np["runtime_locks"].values())[-1],"results":[{"R0":1.13,"R1":.72}],"models_expected":74}
        normalized,repair=native.normalize_score_plan(original,np,nativeplan)
        self.assertEqual(normalized["plan"],rec(nativeplan));self.assertEqual(normalized["results"],original["results"]);self.assertEqual(repair["changed_fields"],["plan"]);self.assertTrue(repair["all_other_fields_equal"])
    def test_unknown_score_plan_receipt_rejected(self):
        with self.assertRaisesRegex(ValueError,"Unrecognized"):native.normalize_score_plan({"plan":{"path":"unexpected"}},np,nativeplan)
    def test_raw_symlink_rejected(self):
        with tempfile.TemporaryDirectory(prefix="CONTRACT_FIXTURE_",dir=out) as td:
            td=Path(td);(td/"source.txt").write_text("scientific fixture");(td/"link.txt").symlink_to(td/"source.txt")
            with self.assertRaisesRegex(ValueError,"Symbolic"):native.copy_file(td/"link.txt",td/"dest.txt")
    def test_native_worker_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError,"Duplicate"):native.select_worker(np["jobs"][0],[str(S/"runs/native_controls_frozen_13051/raw")]*2)
    def test_absent_native_raw_never_receives_score(self):
        fake=dict(models_expected=74,results=[dict(job_key=j["job_key"],models=[dict(slot=s,status="MODEL_UNRESOLVED",R0=None,R1=None) for s in j["slots"]]) for j in np["jobs"]])
        fake["results"][0]["models"][0].update(status="VALID",R0=1,R1=.8)
        with self.assertRaisesRegex(ValueError,"assigned a score"):native.independent_audit(np,out/"NO_SCIENTIFIC_RAW",fake)
    def test_native_bytecopy_worker_preserves_exact_bytes(self):
        with tempfile.TemporaryDirectory(prefix="CONTRACT_FIXTURE_",dir=out) as td:
            source=S/"runs/native_controls_frozen_13051/raw"/np["jobs"][0]["job_key"]/"worker.json"
            pair=native.copy_file(source,Path(td)/"worker.json");self.assertEqual(pair["original"]["sha256"],pair["copy"]["sha256"])
    def test_BBF_reference_backend_provenance_rejected(self):
        with tempfile.TemporaryDirectory(prefix="CONTRACT_FIXTURE_",dir=out) as td:
            td=Path(td);wd=td/key0;wd.mkdir()
            shutil.copy2(raw0/key0/"worker.json",wd/"worker.json");refs=read(raw0/key0/"worker_reference_receipts.json")
            refs["backend"]=refs["budget_guard"];dump(wd/"worker_reference_receipts.json",refs)
            with self.assertRaisesRegex(ValueError,"backend provenance"):audit.audit(plan,[str(td)],out/"should_not_exist.json")
    def test_BBF_reference_receipt_required(self):
        with tempfile.TemporaryDirectory(prefix="CONTRACT_FIXTURE_",dir=out) as td:
            td=Path(td);wd=td/key0;wd.mkdir();shutil.copy2(raw0/key0/"worker.json",wd/"worker.json")
            with self.assertRaises(FileNotFoundError):audit.audit(plan,[str(td)],out/"should_not_exist.json")
rr=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
if not rr.wasSuccessful():raise RuntimeError("Downstream contracts failed")
pilot_args=[str(R/"env/core/bin/python"),str(nh),"--plan",str(nativeplan),"--analysis",str(nativeplan.with_name("analysis_plan.json")),"--membership",str(nativeplan.with_name("membership.json")),"--raw-root",str(nativeplan.parent/"raw"),"--raw-root",str(S/"runs/allocation_v2_13106/native_index19/raw"),"--out-dir",str(out/"native_readiness_first3"),"--pilot-only"]
subprocess.run(pilot_args,check=True)
subprocess.run([str(R/"env/core/bin/python"),str(bh),"--plan",str(plan),"--raw-root",str(raw0),"--out",str(out/"BBF_readiness_first5/worker_audit.json"),"--score-and-verify"],check=True)
na=read(out/"native_readiness_first3/acceptance.json");ba=read(out/"BBF_readiness_first5/acceptance.json")
if na["models_raw_confidence_accepted"]!=3 or ba["n_models_accepted"]!=5:raise ValueError("Actual pilot readiness lost valid slots")
prefix="""#!/bin/bash
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:45:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/23_common_review
#SBATCH --output=__OUT__/__LABEL___%j.log
set -euo pipefail
export PS1="DOLLAR{PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=""
unset PYTHONPATH
""".replace("__OUT__",str(out))
native_launcher=out/"native74_review_cpu.sbatch"
nt=prefix.replace("__LABEL__","native74_review")+str(R/"env/core/bin/python")+" "+str(nh)+" --plan "+str(nativeplan)+" --analysis "+str(nativeplan.with_name("analysis_plan.json"))+" --membership "+str(nativeplan.with_name("membership.json"))+" --raw-root "+str(nativeplan.parent/"raw")+" --raw-root "+str(S/"runs/allocation_v2_13106/native_index19/raw")+" --out-dir "+str(out)+"/native74_review_DOLLAR{SLURM_JOB_ID}\n"
native_launcher.write_text(nt.replace("DOLLAR","$"));native_launcher.chmod(0o444)
bbf_launcher=out/"bbf110_review_cpu.sbatch"
roots=[raw0,S/"runs/allocation_v2_13103/bbf_remaining/raw"]
bt=prefix.replace("__LABEL__","bbf110_review")+str(R/"env/core/bin/python")+" "+str(bh)+" --plan "+str(plan)+" "+" ".join("--raw-root "+str(r) for r in roots)+" --out "+str(out)+"/bbf110_review_DOLLAR{SLURM_JOB_ID}/worker_audit.json --require-all --score-and-verify\n"
bbf_launcher.write_text(bt.replace("DOLLAR","$"));bbf_launcher.chmod(0o444)
for path in [native_launcher,bbf_launcher]:subprocess.run(["bash","-n",str(path)],check=True)
dispositions=dict(status="TECHNICAL_HISTORY_PRESERVED",native_GPU_wrapper_authority="allocation_v2_13106",native13103="DO_NOT_LAUNCH_DYNAMIC_RUNTIME_COMPARISON_SUPERSEDED",transitional13105="NOT_AUTHORITY_RE_FREEZED_FROM_VERSIONED_UTILITY13106",BBF_science_authority="bbf_common_13061",BBF_remaining_launcher13103="VALID_V4_GUARD_SCIENCE_UNCHANGED",BBF_remaining_launcher13106="ALTERNATIVE_SAME_SCIENCE_NOT_BOTH_DUPLICATE_ROOTS_REJECTED",CPU_downstream_authority=str(out))
dump(out/"technical_dispositions.json",dispositions)
ready=dict(status="NATIVE74_AND_BBF110_CPU_DOWNSTREAM_FROZEN_PILOT_CONTENT_TESTED_READY",CPU_allocation=cpu,source=rec(__file__),native_helper=rec(nh),native_launcher=rec(native_launcher),BBF_helper=rec(bh),BBF_launcher=rec(bbf_launcher),native_plan=rec(nativeplan),BBF_plan=rec(plan),native_pilot_readiness_acceptance=rec(out/"native_readiness_first3/acceptance.json"),BBF_pilot_readiness_acceptance=rec(out/"BBF_readiness_first5/acceptance.json"),contract_tests=dict(status="PASSED",n_tests=rr.testsRun),native_existing_tests=na["tests"],BBF_existing_tests=ba["tests"],technical_dispositions=rec(out/"technical_dispositions.json"),native_full_result=False,BBF_full_result=False,GPU_submitted_by_subagent=False,scope="CPU_READINESS_ONLY_FULL_RUNS_REQUIRE_ROOT_GPU_TERMINAL_OUTPUTS")
dump(out/"readiness.json",ready);print(json.dumps(dict(ready,readiness_receipt=rec(out/"readiness.json")),ensure_ascii=False,indent=2),flush=True)
