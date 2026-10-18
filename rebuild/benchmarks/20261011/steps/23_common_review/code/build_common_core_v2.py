import ast,importlib.util,json,os,shutil,sys,unittest
from pathlib import Path
from unittest.mock import patch
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/23_common_review";OLD=S/"frozen/native_common_13051/code"
sys.path.insert(0,str(OLD))
from screening_transfer import rec,read,verify,dump
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
technical=load("technical_cpu",S/"runs/allocation_v2_13106/code/common_allocation_v2.py");cpu=technical.allocation(0)
source=OLD/"benchmark_common_review.py";verify(dict(path=str(source),bytes=59077,sha256="876d29f9b8a20cf3f8bbf526262de96b1071a30b47590b632e5d31f97c362391"))
text=source.read_text().replace("import argparse,collections","import importlib.util\nimport argparse,collections")
text=text.replace("from screening_transfer import rec,verify,read,dump,summary,components,parse_ipsae,REVISION",'_DEP_CODE=Path(__file__).resolve().parent\nif not (_DEP_CODE/"src/ppiblocker").exists():_DEP_CODE=Path("/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/native_common_13051/code")\nsys.path.insert(0,str(_DEP_CODE))\nfrom screening_transfer import rec,verify,read,dump,summary,components,parse_ipsae,REVISION')
text=text.replace("FROZEN_DIR=Path(__file__).resolve().parent","FROZEN_DIR=_DEP_CODE")
guard_def='GPU_GUARD_RECEIPT=dict(path=str(ROOT/"steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py"),bytes=84446,sha256="b37227bd862ee1425a59f5308be1ee3f4824042dea5d71c1269ad0f406b318f9")\n'
text=text.replace('sys.path.insert(0,str(FROZEN_DIR/"src"))',guard_def+'sys.path.insert(0,str(FROZEN_DIR/"src"))')
start=text.index("def allocation(expected_gpu):");end=text.index("def assigned_gpu_environment(",start)
technical_functions="""def gpu_guard_module():
    spec=importlib.util.spec_from_file_location("common_core_guard_v4",GPU_GUARD_RECEIPT["path"])
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def selected_scheduler_receipt(text,expected_gpu,environment):
    g=gpu_guard_module();job=environment.get("SLURM_JOB_ID")
    if not job:raise RuntimeError("Production common review requires actual Slurm allocation")
    logical=None
    if environment.get("SLURM_ARRAY_JOB_ID") is not None or environment.get("SLURM_ARRAY_TASK_ID") is not None:
        if not environment.get("SLURM_ARRAY_JOB_ID") or environment.get("SLURM_ARRAY_TASK_ID") is None:raise ValueError("Incomplete invoking array identity")
        logical=environment["SLURM_ARRAY_JOB_ID"]+"_"+environment["SLURM_ARRAY_TASK_ID"]
    selected=g.select_scheduler_record(text,raw_job_id=job,logical_key=logical)
    identity=g.scheduler_allocation_identity(selected,logical_key=logical,env=environment)
    tres=g.validate_scheduler_gpu_allocation(selected,expected_gpu)
    return dict(job_id=job,expected_gpu=expected_gpu,allocated_gpu_count=expected_gpu,scheduler_record=selected,
                scheduler_record_full=text,selected_scheduler_record=selected,scheduler_alloc_tres=tres,
                raw_allocation_identity=identity,guard_source_receipt=GPU_GUARD_RECEIPT)
def allocation(expected_gpu):
    env=dict(os.environ);job=env.get("SLURM_JOB_ID")
    if not job:raise RuntimeError("Production common review requires actual Slurm allocation")
    pr=subprocess.run(["scontrol","show","job",job,"-o"],capture_output=True,text=True,check=True)
    result=selected_scheduler_receipt(pr.stdout,expected_gpu,env)
    if expected_gpu==1:
        g=gpu_guard_module();owned=g.gpu_ownership_guard(expected_count=1,expected_gpu_name="NVIDIA A100-PCIE-40GB",env=env)
        identity=g.scheduler_allocation_identity(owned["selected_scheduler_record"],env=env)
        tres=g.validate_scheduler_gpu_allocation(owned["selected_scheduler_record"],1)
        if identity!=result["raw_allocation_identity"] or tres!=result["scheduler_alloc_tres"]:raise ValueError("Scheduler/ownership identity or TRES mismatch")
        os.environ["CUDA_VISIBLE_DEVICES"]=owned["child_cuda_visible_devices"];result["owned_gpu_guard"]=owned
    return result
def require_immutable_source_context():
    if FROZEN_DIR!=Path(__file__).resolve().parent:raise RuntimeError("Prepare/worker requires frozen common_core_v2/code, not live source/rebuild")
    bundle=read(FROZEN_DIR.parent/"source_bundle.json")
    if bundle["source"]["path"]!=str(Path(__file__).resolve()):raise ValueError("Source bundle does not bind this actual corrected core")
    return bundle
"""
text=text[:start]+technical_functions+text[end:]
text=text.replace("    cpu();registry=read(registry_path)","    require_immutable_source_context();cpu();verify(GPU_GUARD_RECEIPT);registry=read(registry_path)")
text=text.replace('runtime_locks=dict(physical_hardware_inventory=HARDWARE_INVENTORY,','runtime_locks=dict(gpu_ownership_guard=GPU_GUARD_RECEIPT,physical_hardware_inventory=HARDWARE_INVENTORY,')
text=text.replace("def worker(plan_path,index,out):\n    allocated=allocation(1)","def worker(plan_path,index,out):\n    require_immutable_source_context()\n    allocated=allocation(1)")
text=text.replace('    plan=read(plan_path);job=plan["jobs"][index]\n    visible=', '    plan=read(plan_path);job=plan["jobs"][index]\n    if plan["source"]["path"]!=str(Path(__file__).resolve()) or plan["frozen_source_bundle"]["path"]!=str(FROZEN_DIR.parent/"source_bundle.json"):raise ValueError("GPU plan source does not bind this immutable corrected core")\n    visible=')
text=text.replace('    for receipt in plan["runtime_locks"].values():verify(receipt)','    for runtime_receipt in plan["runtime_locks"].values():verify(runtime_receipt)')
text=text.replace('            if allocated_gpu_count(w["allocation"]["scheduler_record"])!=1:raise ValueError("Worker did not allocate exactly one GPU")','            allocated=w["allocation"]\n            original=allocated.get("scheduler_record_full",allocated["scheduler_record"])\n            raw_id=str(allocated.get("job_id",w["job_id"]))\n            selected=gpu_guard_module().select_scheduler_record(original,raw_job_id=raw_id)\n            gpu_guard_module().validate_scheduler_gpu_allocation(selected,1)')
tree0=ast.parse(source.read_text());tree2=ast.parse(text)
def functions(tree):return {node.name:ast.dump(node,include_attributes=False) for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
fo,fn=functions(tree0),functions(tree2)
protected=["job_signature","units","geometry","one_score","blind_entities","a3m_rows","assert_mapping","seqcheck","transform_fit","find_raw"]
if any(fo[name]!=fn[name] for name in protected):raise ValueError("Scientific scoring/input/geometry function AST changed")
target=R/"source/rebuild/benchmark_common_review_v2.py";target.write_text(text)
snap=S/"frozen"/("common_core_v2_"+os.environ["SLURM_JOB_ID"]);code=snap/"code";code.mkdir(parents=True,exist_ok=False)
files=[]
for path in sorted(OLD.rglob("*")):
    if path.is_file() and "__pycache__" not in path.parts:
        dest=code/path.relative_to(OLD);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest);dest.chmod(0o555 if dest.name in {"boltz","colabfold_batch"} else 0o444);files.append(dict(original=rec(path),frozen=rec(dest)))
core=code/"benchmark_common_review_v2.py";shutil.copy2(target,core);core.chmod(0o444);files.append(dict(original=rec(target),frozen=rec(core)))
dump(snap/"source_bundle.json",dict(status="IMMUTABLE_CORRECTED_COMMON_CORE_V2_SOURCE_BUNDLE",source=rec(core),source_pre_correction=rec(source),files=files,guard=technical.guard_module() and rec(technical.GUARD),scientific_function_AST_preserved=protected,SETTINGS_and_job_signature_preserved=True,changes=["unique invoking Slurm rawID+arrayalias selected scheduler record","score input plan receipt loop variable shadowing","prepare/worker source must bind actual frozen corrected source","guard source receipt bound in runtime locks"],CPU_freeze_job=os.environ["SLURM_JOB_ID"]))
(snap/"source_bundle.json").chmod(0o444)
for name in list(sys.modules):
    if name in ["screening_transfer","benchmark_common_review_v2","ppiblocker"] or name.startswith("ppiblocker."):del sys.modules[name]
sys.path.insert(0,str(code));v2=load("benchmark_common_review_v2",core);original=load("original_scientific",source)
if v2.SETTINGS!=original.SETTINGS:raise ValueError("Corrected core changed SETTINGS")
tests=v2.run_tests()
out=S/"runs"/("common_core_v2_validation_"+os.environ["SLURM_JOB_ID"]);out.mkdir()
class Extra(unittest.TestCase):
    def test_multi_record_actual_id_alias_order_invariance(self):
        own="JobId=13059 ArrayJobId=13059 ArrayTaskId=19 JobState=RUNNING TRES=cpu=4,gres/gpu=1\n"
        sib="JobId=13100 ArrayJobId=13059 ArrayTaskId=18 JobState=FAILED TRES=cpu=2\n"
        env={"SLURM_JOB_ID":"13059","SLURM_ARRAY_JOB_ID":"13059","SLURM_ARRAY_TASK_ID":"19"}
        for full in [own+sib,sib+own]:self.assertEqual(v2.selected_scheduler_receipt(full,1,env)["selected_scheduler_record"].strip(),own.strip())
    def test_wrong_array_alias_rejected(self):
        with self.assertRaises(ValueError):v2.selected_scheduler_receipt("JobId=13059 ArrayJobId=13059 ArrayTaskId=18 JobState=RUNNING TRES=cpu=4,gres/gpu=1\n",1,{"SLURM_JOB_ID":"13059","SLURM_ARRAY_JOB_ID":"13059","SLURM_ARRAY_TASK_ID":"19"})
    def test_dynamic_runtime_not_identity(self):
        env={"SLURM_JOB_ID":"13059","SLURM_ARRAY_JOB_ID":"13059","SLURM_ARRAY_TASK_ID":"19"}
        row="JobId=13059 ArrayJobId=13059 ArrayTaskId=19 JobState=RUNNING TRES=cpu=4,gres/gpu=1"
        a=v2.selected_scheduler_receipt(row+" RunTime=00:00:00\n",1,env);b=v2.selected_scheduler_receipt(row+" RunTime=00:00:01\n",1,env)
        self.assertEqual(a["raw_allocation_identity"],b["raw_allocation_identity"]);self.assertEqual(a["scheduler_alloc_tres"],b["scheduler_alloc_tres"])
rr=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Extra))
if not rr.wasSuccessful():raise RuntimeError("Corrected allocation core tests failed")
np=S/"runs/native_controls_frozen_13051/inference_plan.json";oldplan=read(np)
prior=S/"runs/native_controls_13018";newplan=out/"rebased_native_plan.json"
v2.prepare(S/"inputs/registry7_bridge13010.json",S/"runs/msa_content_12983/msa.json",prior/"native_controls_only.json",newplan,prior/"predeclared_gate.json")
rebased=read(newplan)
if rebased["source"]!=rec(core) or rebased["runtime_locks"]["gpu_ownership_guard"]!=v2.GPU_GUARD_RECEIPT:raise ValueError("Prepared actual source/guard binding mismatch")
if [v2.job_signature(j) for j in rebased["jobs"]]!=[original.job_signature(j) for j in oldplan["jobs"]]:raise ValueError("Corrected rebase changed science/job signatures")
# Real pilot data use the original exact plan; this is a CPU scorer validation, never new GPU inference.
assembled=S/"runs/downstream_frozen_13119/native_readiness_first3/assembled_raw"
v2.score(np,np.with_name("analysis_plan.json"),assembled,out/"pilot_score_v2.json")
scored=read(out/"pilot_score_v2.json")
if scored["plan"]!=rec(np):raise ValueError("Corrected scorer still emits wrong plan receipt")
v2.verify_result(out/"pilot_score_v2.json",np.with_name("membership.json"),out/"pilot_score_v2_acceptance.json")
prior_score=read(S/"runs/downstream_frozen_13119/native_readiness_first3/score.json")
def numeric(row):
    return dict(job_key=row["job_key"],R0=row["R0"],R1=row["R1"],models=[{k:v for k,v in m.items() if k not in {"raw_files","derived_files"}} for m in row["models"]])
if [numeric(row) for row in scored["results"]]!=[numeric(row) for row in prior_score["results"]]:raise ValueError("Corrected core changed actual pilot scientific scores")
accept=dict(status="CORRECTED_COMMON_CORE_V2_CPU_SOURCE_BINDING_AND_TRUE_SCORE_VERIFIED_READY_NO_GPU_SUBMITTED",source=rec(core),live_new_source=rec(target),source_bundle=rec(snap/"source_bundle.json"),old_source_unchanged=rec(source),old_native_plan_unchanged=rec(np),rebased_plan=rec(newplan),rebased_analysis=rec(out/"analysis_plan.json"),rebased_membership=rec(out/"membership.json"),pilot_score=rec(out/"pilot_score_v2.json"),pilot_acceptance=rec(out/"pilot_score_v2_acceptance.json"),tests=dict(existing=tests,new=dict(status="PASSED",n_tests=rr.testsRun)),scientific_AST_preserved=protected,SETTINGS_identical=True,job_signatures_identical=True,pilot_scores_identical=True,guard=rec(technical.GUARD),CPU_allocation=cpu,GPU_submitted=False,native_or_BBF_existing_workers_modified=False)
dump(out/"acceptance.json",accept);print(json.dumps(dict(accept,acceptance_receipt=rec(out/"acceptance.json")),ensure_ascii=False,indent=2),flush=True)
