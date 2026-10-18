import os,sys,json
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
CODE=R/"steps/23_common_review/frozen/native_common_13051/code"
sys.path.insert(0,str(CODE))
import benchmark_common_review as c
from screening_transfer import rec,verify,read,dump,summary,components,parse_ipsae
c.cpu()
work=R/"steps/23_common_review/runs/native_controls_frozen_13051"
plan=read(work/"inference_plan.json");analysis=read(work/"analysis_plan.json");job=plan["jobs"][0]
if job["engine"]!="boltz" or job["variant"]!="primary":raise ValueError("Fixed native index0 pilot changed")
worker=work/"raw"/job["job_key"]/"worker.json";w=read(worker)
if c.job_signature(w["job"])!=c.job_signature(job) or w["settings"]!=c.SETTINGS:raise ValueError("Actual worker frozen protocol mismatch")
if c.allocated_gpu_count(w["allocation"]["scheduler_record"])!=1 or "JobState=RUNNING" not in w["allocation"]["scheduler_record"]:raise ValueError("Worker allocation not RUNNING GPU1")
vis=w["gpu_visibility"]
if vis["engine_cuda_probe"]["actual_cuda_visible_count"]!=1 or vis["engine_cuda_probe"]["name"]!="NVIDIA A100-PCIE-40GB":raise ValueError("Wrong actual CUDA runtime visibility/hardware")
assignment=vis["assignment"]
if assignment["cuda_visible_after"]!=assignment["physical_minor_to_uuid_map"][assignment["assigned_physical_device_minor"]]:raise ValueError("Wrong physical assignment UUID")
if w["source"]!=plan["source"] or w["frozen_source_bundle"]!=plan["frozen_source_bundle"]:raise ValueError("Source freeze references mismatch")
verify(w["source"]);verify(w["frozen_source_bundle"])
for lock in plan["runtime_locks"].values():verify(lock)
if len(w["runs"])!=3 or any(v["returncode"]!=0 for v in w["runs"]):raise ValueError("Incomplete/failed actual three-seed engine pilot")
out=R/"steps/23_common_review/runs"/("native_pilot_validation_"+os.environ["SLURM_JOB_ID"]);out.mkdir(exist_ok=False)
entity=next(v for v in plan["entities"] if v["blind_id"]==job["blind_id"])
target=next(v for v in analysis["targets"] if v["target_id"]==job["target_id"])
models=[]
for slot in job["slots"]:
    m=c.one_score(job,entity,target,slot,work/"raw",out/"scores"/(str(slot["seed"])+"_"+str(slot["model"])),True)
    for f in m["raw_files"]+m["derived_files"]:verify(f)
    recomputed=components(m["global_iptm"],m["binder_plddt_fraction"],m["interface_plddt_fraction"],m["bidirectional_contact_PAE_A"])
    if m["components"]!=recomputed or m["R0"]!=recomputed["score"]:raise ValueError("R0 component recomputation mismatch")
    tables={Path(f["path"]).name:f for f in m["derived_files"]}
    for cut in ("10","15"):
        if parse_ipsae(Path(tables["model_"+cut+"_15.txt"]["path"]).read_text(),"A","B")!=m["ipsae"][cut]:raise ValueError("Official directional ipSAE output mismatch")
    if m["R1"]!=(m["ipsae"]["10"]["maximum"] if m["status"]=="VALID" else None):raise ValueError("R1/no-interface policy mismatch")
    models.append(m)
result=dict(status="ONE_NATIVE_BOLTZ_RUNTIME_PILOT_CONTENT_ACCEPTED_NOT_FULL74_RESULT",input_plan=rec(work/"inference_plan.json"),source=rec(c.__file__),worker=rec(worker),GPU_job="13053_0",CPU_job=os.environ["SLURM_JOB_ID"],target_id=job["target_id"],native_control=True,engine="boltz",n_expected=3,n_raw_confidence_valid=3,n_interface_valid=sum(m["status"]=="VALID" for m in models),R0=summary([m["R0"] for m in models],3),R1=summary([m["R1"] for m in models],3),models=models,actual_ownership=vis,tests=c.run_tests(),full_native_control_models_pending=71,operational_pass=None,independent_experimental_validation=False)
dump(out/"acceptance.json",result)
dump(out/"manifest.json",dict(status=result["status"],source=rec(__file__),input_plan=result["input_plan"],outputs=[rec(out/"acceptance.json")],scope="ENGINE_RUNTIME_AND_RAW_FORMAT_PILOT_NOT_COMPLETE_BENCHMARK"))
print(json.dumps(dict(status=result["status"],acceptance=rec(out/"acceptance.json"),R0=result["R0"],R1=result["R1"],n_interface_valid=result["n_interface_valid"],geometry=[m["geometry"] for m in models]),indent=2),flush=True)

