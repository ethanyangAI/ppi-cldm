import argparse,importlib.util,json,os,re,sys
from pathlib import Path
import numpy as np
R=Path("/lustre/users/u21111210118/projects/test9")
CODE=R/"steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061/code"
sys.path.insert(0,str(CODE))
import bbf_input_diagnostic as b
from screening_transfer import rec,verify,read,dump,components,parse_ipsae,summary
from benchmark_common_review import units,read_structure,now
GUARD=dict(path=str(R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py"),bytes=84446,sha256="b37227bd862ee1425a59f5308be1ee3f4824042dea5d71c1269ad0f406b318f9")
def guard_module():
    verify(GUARD);spec=importlib.util.spec_from_file_location("posthoc_guard_v4",GUARD["path"]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def audit(plan_path,rawroots,out,require_all=False):
    b.cpu();plan=read(plan_path);guard=guard_module();rows=[];models=[];wanted={j["job_key"]:j for j in plan["jobs"]}
    features_path=R/"steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061/feature_manifest.json"
    features=read(features_path);featurejobs={j["job_key"]:j for j in features["jobs"]};verify(features["source"])
    if features["plan"]!=rec(plan_path):raise ValueError("Scientific feature plan receipt mismatch")
    for key,j in wanted.items():
        paths=[Path(root)/key/"worker.json" for root in rawroots if (Path(root)/key/"worker.json").exists()]
        if len(paths)>1:raise ValueError("Duplicate actual worker across roots "+key)
        if not paths:rows.append(dict(job_key=key,status="WORKER_NOT_RUN_OR_MISSING",models_expected=5));continue
        wp=paths[0];w=read(wp);alloc=w["allocation"]
        if w["job_key"]!=key or w["settings"]!=plan["settings"]:raise ValueError("Worker fixed science mismatch")
        raw_id=str(alloc.get("slurm_job_id",alloc.get("job_id","")))
        selected=guard.select_scheduler_record(alloc["scheduler_record"],raw_job_id=raw_id)
        identity=guard.scheduler_allocation_identity(selected)
        if "JobState=RUNNING" not in selected:raise ValueError("Invoking raw worker was not RUNNING")
        if guard.validate_scheduler_gpu_allocation(selected,1)!=alloc["scheduler_alloc_tres"]:raise ValueError("Selected actual GPU allocation TRES differs from original receipt")
        if alloc["allocated_gpu_count"]!=1:raise ValueError("Worker GPU count not1")
        hardware=alloc["hardware"];owned=alloc["owned_gpu_uuids"];env=hardware["assignment_environment"]
        if len(owned)!=1 or alloc["child_cuda_visible_devices"]!=owned[0]:raise ValueError("Owned UUID/child visible mismatch")
        physical={str(d["device_minor"]):d["uuid"] for d in hardware["physical_inventory"]}
        basis=next((name for name in ["SLURM_STEP_GPUS","SLURM_JOB_GPUS"] if env.get(name)),None)
        if basis is None:raise ValueError("Actual GPU ownership not Slurm identified")
        declared=env[basis].split(",")
        if len(declared)!=1:raise ValueError("Declared assigned GPU count not1")
        token=declared[0].strip();expected=token if token.startswith("GPU-") else physical.get(token)
        if expected!=owned[0]:raise ValueError("Physical minor to UUID ownership differs")
        selected_hw=[d for d in hardware["gpus"] if d["uuid"]==owned[0]]
        if len(selected_hw)!=1 or selected_hw[0]["name"]!="NVIDIA A100-PCIE-40GB":raise ValueError("Owned physical hardware model mismatch")
        if w["features_source_receipt"]!=features["source"] or w["features_cpu_receipt"]!=featurejobs[key]["features"]:raise ValueError("CPU actual feature provenance mismatch")
        b.feature_arrays(j,featurejobs[key])
        expectedslots={tuple(sorted(s.items())) for s in j["slots"]}
        if len(w["models"])!=5 or {tuple(sorted(v["slot"].items())) for v in w["models"]}!=expectedslots:raise ValueError("Model slots missing/duplicate")
        model_records=[]
        for v in w["models"]:
            if v["returncode"]!=0:
                if require_all:raise ValueError("Required model prediction failed")
                model_records.append(dict(slot=v["slot"],status="MODEL_PREDICTION_FAILED"));continue
            pp=Path(v["pdb_path"]);ss=Path(v["scores_path"]);conf=read(ss);ch,_=read_structure(pp)
            if len(ch)!=2 or ch[0]["id"]!="A" or ch[1]["id"]!="B" or ch[0]["sequence"]!=j["target_sequence"] or ch[1]["sequence"]!=j["binder_sequence"]:raise ValueError("PDB full target/binder query identity/order")
            total=len(j["target_sequence"])+len(j["binder_sequence"]);pl,pa=units(conf["plddt"],conf["pae"],total,100)
            pdbpl=np.array([r["bfactor"] for c in ch for r in c["residues"]])
            delta=float(np.max(np.abs(pdbpl-pl*100)))
            if delta>.02:raise ValueError("PDB/score pLDDT units or residue mapping mismatch")
            if conf["plddt_units"]!="0-100" or not conf["pae_units"].startswith("Angstrom"):raise ValueError("Explicit raw confidence units missing")
            if conf["seed"]!=v["slot"]["seed"] or conf["model"]!=v["slot"]["model"] or conf["query"]!=j["target_sequence"]+j["binder_sequence"]:raise ValueError("Actual fixed model/seed/query metadata mismatch")
            if conf["initial_guess"] or conf["initial_atom_pos"]:raise ValueError("Raw inference declares coordinate guess")
            if conf["iptm"]!=conf["globaliptm"] or not 0<=conf["iptm"]<=1:raise ValueError("Global ipTM identity/range")
            model_records.append(dict(slot=v["slot"],status="RAW_CONFIDENCE_UNITS_AND_FULL_QUERY_ACCEPTED",pdb=rec(pp),scores=rec(ss),pdb_plddt_max_abs_difference=delta))
            models.append(model_records[-1])
        rows.append(dict(job_key=key,status="WORKER_OWNERSHIP_RAW_CONTENT_ACCEPTED",worker=rec(wp),raw_allocation_identity=identity,selected_scheduler_record=selected,owned_gpu_uuids=owned,feature_file=featurejobs[key]["features"],models=model_records))
    completed=sum(row["status"]=="WORKER_OWNERSHIP_RAW_CONTENT_ACCEPTED" for row in rows)
    if require_all and completed!=22:raise ValueError("Full110 downstream requires all22 workers")
    result=dict(status="BBF_WORKER_CPU_POSTHOC_CONTENT_AND_RAW_ALLOCATION_ACCEPTED",plan=rec(plan_path),posthoc_guard=GUARD,source=rec(__file__),raw_roots=list(rawroots),rows=rows,jobs_expected=22,jobs_present_accepted=completed,models_expected=110,models_raw_valid=len(models),scientific_scope="DEVELOPMENT_ONLY_PARTIAL_UNLESS_ALL22_COMPLETED",settings=plan["settings"])
    dump(out,result);return result
def main():
    p=argparse.ArgumentParser();p.add_argument("--plan",required=True);p.add_argument("--raw-root",action="append",required=True);p.add_argument("--out",required=True);p.add_argument("--require-all",action="store_true");p.add_argument("--score-and-verify",action="store_true")
    a=p.parse_args();b.cpu();Path(a.out).parent.mkdir(parents=True,exist_ok=False)
    result=audit(a.plan,a.raw_root,a.out,a.require_all)
    if a.score_and_verify:
        merged=Path(a.out).parent/"raw_view";merged.mkdir()
        for row in result["rows"]:
            if row["status"]=="WORKER_OWNERSHIP_RAW_CONTENT_ACCEPTED":(merged/row["job_key"]).symlink_to(Path(row["worker"]["path"]).parent,target_is_directory=True)
        b.collect(a.plan,merged,Path(a.out).parent/"raw.json")
        b.score(a.plan,Path(a.out).parent/"raw.json",Path(a.out).parent/"score.json")
        b.verify_result(Path(a.out).parent/"score.json",Path(a.out).parent/"score_acceptance.json")
        scored=read(Path(a.out).parent/"score.json")
        pilot=[v for v in scored["results"] if any(row["job_key"]==v["id"]+"_"+v["arm"] and row["status"]=="WORKER_OWNERSHIP_RAW_CONTENT_ACCEPTED" for row in result["rows"])]
        valid=sum(m["status"] in {"VALID","NO_INTERFACE"} for row in pilot for m in row["models"])
        if valid!=result["models_raw_valid"]:raise ValueError("Pilot score completeness differs from raw accepted")
        final=dict(status="BBF_FIRST_JOB_FIVE_MODELS_CPU_CONTENT_ACCEPTED_NOT_FULL110" if not a.require_all else "BBF110_ALL_WORKERS_RAW_SCORES_CONTENT_ACCEPTED_DEVELOPMENT_ONLY",worker_audit=rec(a.out),score=rec(Path(a.out).parent/"score.json"),score_acceptance=rec(Path(a.out).parent/"score_acceptance.json"),accepted_pilot_results=pilot,n_models_accepted=valid,remaining_model_slots=110-valid,tests=b.run_tests(),operational_pass=None,independent_experimental_validation=False)
        dump(Path(a.out).parent/"acceptance.json",final)
        print(json.dumps(dict(status=final["status"],acceptance=rec(Path(a.out).parent/"acceptance.json"),pilot=[dict(id=v["id"],arm=v["arm"],R0=v["R0"],R1=v["R1"]) for v in pilot]),indent=2),flush=True)
    else:print(json.dumps(dict(status=result["status"],jobs=result["jobs_present_accepted"],models=result["models_raw_valid"]),indent=2),flush=True)
if __name__=="__main__":main()

