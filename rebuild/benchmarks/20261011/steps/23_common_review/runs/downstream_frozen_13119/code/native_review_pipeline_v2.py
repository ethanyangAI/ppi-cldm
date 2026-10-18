#!/usr/bin/env python3
"""Native common-review CPU assembly, blinded score, independent raw audit and content verify."""
import argparse,importlib.util,json,math,os,re,shutil,sys,unittest
from pathlib import Path
import numpy as np
R=Path("/lustre/users/u21111210118/projects/test9")
S=R/"steps/23_common_review";CODE=S/"frozen/native_common_13051/code"
sys.path.insert(0,str(CODE))
import benchmark_common_review as c
from screening_transfer import rec,verify,read,dump
GUARD=R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py"
def gmodule():
    verify(dict(path=str(GUARD),bytes=84446,sha256="b37227bd862ee1425a59f5308be1ee3f4824042dea5d71c1269ad0f406b318f9"))
    spec=importlib.util.spec_from_file_location("native_posthoc_guard",GUARD);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);return g
def allocation_cpu():
    g=gmodule();env=dict(os.environ);job=env.get("SLURM_JOB_ID")
    if not job:raise RuntimeError("Slurm CPU allocation required")
    pr=c.subprocess.run(["scontrol","show","job",job,"-o"],capture_output=True,text=True,check=True)
    selected=g.select_scheduler_record(pr.stdout,raw_job_id=job)
    g.scheduler_allocation_identity(selected,env=env);g.validate_scheduler_gpu_allocation(selected,0)
    if env.get("CUDA_VISIBLE_DEVICES","")!="":raise ValueError("CPU scientific stages must mask CUDA")
    return dict(job_id=job,allocated_gpu_count=0,scheduler_record=pr.stdout,selected_scheduler_record=selected)
def select_worker(job,roots):
    ws=[Path(root)/job["job_key"]/"worker.json" for root in roots if (Path(root)/job["job_key"]/"worker.json").exists()]
    if len(ws)>1:raise ValueError("Duplicate native worker across immutable roots")
    return ws[0] if ws else None
def copy_file(source,destination):
    if source.is_symlink():raise ValueError("Symbolic link is not a self-contained scientific bytecopy")
    original=rec(source);destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,destination);copied=rec(destination)
    if (original["sha256"],original["bytes"])!=(copied["sha256"],copied["bytes"]):raise ValueError("Bytecopy/hash mismatch")
    return dict(original=original,copy=copied)
def assemble(plan,roots,out,pilot_only=False):
    out.mkdir();rows=[]
    for index,j in enumerate(plan["jobs"]):
        wp=select_worker(j,roots)
        if pilot_only and index!=0:rows.append(dict(index=index,job_key=j["job_key"],status="PILOT_READINESS_NOT_COPIED",models_expected=j["expected_models"]));continue
        if wp is None:rows.append(dict(index=index,job_key=j["job_key"],status="WORKER_MISSING_OR_FAILED_SCHEDULER_LEDGER_REQUIRED",models_expected=j["expected_models"]));continue
        worker=read(wp)
        if worker["settings"]!=c.SETTINGS or c.job_signature(worker["job"])!=c.job_signature(j):raise ValueError("Native worker scientific contract mismatch")
        if worker["source"]!=plan["source"] or worker["frozen_source_bundle"]!=plan["frozen_source_bundle"] or worker["runtime_locks"]!=plan["runtime_locks"]:raise ValueError("Original native worker source/feature provenance drift")
        items=[];origin=wp.parent;dest=out/j["job_key"];dest.mkdir()
        for source in sorted(origin.rglob("*")):
            if source.is_symlink():raise ValueError("Raw tree symlink forbidden")
            if source.is_file():items.append(copy_file(source,dest/source.relative_to(origin)))
        copied_worker=rec(dest/"worker.json")
        if copied_worker["sha256"]!=rec(wp)["sha256"]:raise ValueError("Original worker JSON bytes modified by assembly")
        rows.append(dict(index=index,job_key=j["job_key"],status="ALL_REGULAR_RAW_FILES_BYTECOPIED",models_expected=j["expected_models"],source_directory=str(origin),copy_directory=str(dest),files=items,original_worker=rec(wp),copied_worker=copied_worker))
    return dict(status="NATIVE_RAW_BYTECOPY_ASSEMBLY_RECEIPTS",n_jobs_expected=20,n_models_expected=74,n_jobs_copied=sum(v["status"]=="ALL_REGULAR_RAW_FILES_BYTECOPIED" for v in rows),rows=rows,pilot_readiness_only=pilot_only)
def selected_allocation(worker,index):
    g=gmodule();a=worker["allocation"];raw_id=str(a["job_id"]);full=a.get("scheduler_record_full",a["scheduler_record"])
    selected=g.select_scheduler_record(full,raw_job_id=raw_id)
    identity=g.scheduler_allocation_identity(selected)
    if identity["array_task_id"]!=str(index):raise ValueError("Invoking native array index does not match frozen job")
    tres=g.validate_scheduler_gpu_allocation(selected,1)
    if a.get("allocated_gpu_count")!=1:raise ValueError("Native GPU allocation not1")
    if a.get("selected_scheduler_record") and selected.strip()!=a["selected_scheduler_record"].strip():raise ValueError("Declared selected native scheduler record mismatch")
    v=worker["gpu_visibility"];assignment=v["assignment"];probe=v["engine_cuda_probe"]
    if probe["actual_cuda_visible_count"]!=1 or probe["engine"]!=worker["job"]["engine"]:raise ValueError("Actual engine CUDA visibility mismatch")
    owned=assignment["device"]["uuid"];env=assignment["assignment_environment"];basis=next((name for name in ["SLURM_STEP_GPUS","SLURM_JOB_GPUS"] if env.get(name)),None)
    if basis is None:raise ValueError("Native GPU ownership lacks authoritative Slurm IDs")
    tokens=g.slurm_gpu_identifiers(env[basis]);physical=assignment["physical_minor_to_uuid_map"]
    if len(tokens)!=1:raise ValueError("Native Slurm ownership count not1")
    resolved=tokens[0] if tokens[0].startswith("GPU-") else physical.get(tokens[0])
    if resolved!=owned or assignment["cuda_visible_after"]!=owned:raise ValueError("Native physical minor/UUID/actual child mask mismatch")
    devices=[d for d in v["physical_inventory"] if d["uuid"]==owned]
    if len(devices)!=1 or devices[0]["name"]!="NVIDIA A100-PCIE-40GB":raise ValueError("Owned native physical GPU name mismatch")
    if "owned_gpu_guard" in a:
        additional=a["owned_gpu_guard"];additional_identity=g.scheduler_allocation_identity(additional["selected_scheduler_record"])
        if additional_identity!=identity or additional["owned_gpu_uuids"]!=[owned] or additional["child_cuda_visible_devices"]!=owned:raise ValueError("Native corrected ownership guard differs from actual engine assignment")
        refs=a["technical_reference_receipts"]
        for field in ["wrapper","scientific_source","scientific_plan","guard","guard_snapshot_manifest","guard_contract_tests"]:verify(refs[field])
        if refs["scientific_source"]!=worker["source"] or refs["settings"]!=worker["settings"]:raise ValueError("Technical wrapper changed science")
    return dict(raw_allocation_identity=identity,selected_scheduler_record=selected,scheduler_record_full=full,scheduler_alloc_tres=tres,owned_gpu_uuid=owned,actual_engine_CUDA_count=probe["actual_cuda_visible_count"])
def raw_model(job,entity,slot,raw):
    p,sc,pa,pl=c.find_raw(job,raw,slot);chains,_=c.read_structure(p);conf=read(sc)
    if len(chains)!=2 or [v["id"] for v in chains]!=["A","B"] or chains[0]["sequence"]!=entity["target_sequence"] or chains[1]["sequence"]!=entity["binder_sequence"]:raise ValueError("Full exact native query/chain order mismatch")
    n=len(entity["target_sequence"])+len(entity["binder_sequence"])
    if job["engine"]=="boltz":
        pp,paa=c.units(np.load(pl,allow_pickle=False)["plddt"],np.load(pa,allow_pickle=False)["pae"],n,1);units="Boltz official pLDDT0-1, PAE Angstrom";files=[rec(p),rec(sc),rec(pa),rec(pl)]
    else:pp,paa=c.units(conf["plddt"],conf["pae"],n,100);units="AF2 official pLDDT0-100, PAE Angstrom";files=[rec(p),rec(sc)]
    bfactor=np.array([r["bfactor"] for ch in chains for r in ch["residues"]]);delta=float(np.max(np.abs(bfactor-pp*100)))
    if delta>.02:raise ValueError("Native PDB/confidence units/order mismatch")
    iptm=float(conf["iptm"])
    if not math.isfinite(iptm) or not 0<=iptm<=1:raise ValueError("Raw native global ipTM range mismatch")
    return dict(status="RAW_EXACT_QUERY_CONFIDENCE_UNITS_ACCEPTED",slot=slot,files=files,global_iptm=iptm,pdb_confidence_max_delta=delta,units=units)
def independent_audit(plan,assembled,score):
    entities={v["blind_id"]:v for v in plan["entities"]};scored={v["job_key"]:v for v in score["results"]};rows=[]
    if len(scored)!=20 or score["models_expected"]!=74:raise ValueError("Native full20/74 denominator lost")
    for index,j in enumerate(plan["jobs"]):
        row=scored[j["job_key"]];wp=Path(assembled)/j["job_key"]/"worker.json";models=[]
        if not wp.exists():
            if any(m["status"]!="MODEL_UNRESOLVED" or m["R0"] is not None or m["R1"] is not None for m in row["models"]):raise ValueError("Missing native worker assigned a score")
            rows.append(dict(index=index,job_key=j["job_key"],status="WORKER_MISSING_TYPED_UNRESOLVED",models_expected=j["expected_models"]));continue
        worker=read(wp);allocation=selected_allocation(worker,index)
        if c.job_signature(worker["job"])!=c.job_signature(j) or row["worker_record"]!=rec(wp):raise ValueError("Score does not bind exact native copied worker")
        for m in row["models"]:
            try:actual=raw_model(j,entities[j["blind_id"]],m["slot"],assembled)
            except (FileNotFoundError,ValueError,KeyError) as error:
                if m["status"]!="MODEL_UNRESOLVED" or m["R0"] is not None or m["R1"] is not None:raise ValueError("Unresolved native raw model received scientific score") from error
                actual=dict(status="RAW_MODEL_UNRESOLVED",slot=m["slot"],reason=str(error))
            if actual["status"]=="RAW_EXACT_QUERY_CONFIDENCE_UNITS_ACCEPTED" and m["status"] in {"VALID","NO_INTERFACE"}:
                if actual["files"]!=m["raw_files"] or actual["global_iptm"]!=m["global_iptm"]:raise ValueError("Native scored confidence/file content differs from independently read raw")
            elif actual["status"]=="RAW_EXACT_QUERY_CONFIDENCE_UNITS_ACCEPTED":
                actual["score_status"]=m["status"];actual["score_unresolved_reason"]=m.get("reason")
            models.append(actual)
        rows.append(dict(index=index,job_key=j["job_key"],status="NATIVE_ACTUAL_GPU_OWNERSHIP_AND_RAW_CONTENT_AUDITED",allocation=allocation,engine_returncodes=[v["returncode"] for v in worker["runs"]],models=models))
    valid=sum(m["status"]=="RAW_EXACT_QUERY_CONFIDENCE_UNITS_ACCEPTED" for row in rows for m in row.get("models",[]))
    return dict(status="NATIVE74_INDEPENDENT_RAW_GPU_AND_UNITS_AUDIT",n_jobs_expected=20,n_models_expected=74,n_raw_confidence_accepted=valid,n_raw_unresolved=74-valid,rows=rows,settings=plan["settings"])
def resource_closure(out,initial):
    visited=set();resources=[];queue=list(initial)
    assembly=read(out/"assembly.json")
    existing={p["original"]["path"]:p["copy"] for row in assembly["rows"] for p in row.get("files",[])}
    while queue:
        receipt=queue.pop()
        if not isinstance(receipt,dict) or not {"path","sha256","bytes"}<=receipt.keys():continue
        path=Path(receipt["path"])
        if str(path) in visited:continue
        visited.add(str(path))
        if not path.resolve().is_relative_to(R):raise ValueError("Scientific resource outside project private scope")
        recompute=any(part in str(path) for part in ["/env/","/assets/colabfold/params/","/assets/boltz/","/assets/mmseqs/","/assets/rfdiffusion/","/assets/bindcraft/"])
        if recompute:resources.append(dict(original=receipt,scope="ENGINE_RECOMPUTE_DEPENDENCY_NOT_REQUIRED_TO_REVIEW_FROZEN_RAW",copied=False));continue
        verify(receipt)
        if str(path) in existing:
            verify(existing[str(path)]);resources.append(dict(original=receipt,copy=existing[str(path)],scope="ORIGINAL_RAW_MAPPED_TO_HASH_IDENTICAL_ASSEMBLED_BYTECOPY",copied=True))
        elif path.is_relative_to(out):resources.append(dict(original=receipt,copy=receipt,scope="CURRENT_CPU_RESULT_SELF_CONTAINED",copied=True))
        else:
            dest=out/"evidence_resources"/path.relative_to(R);pair=copy_file(path,dest);resources.append(dict(pair,scope="SCIENTIFIC_SOURCE_INPUT_REFERENCE_OR_RAW_EVIDENCE",copied=True))
        if path.suffix==".json":
            def scan(value):
                if isinstance(value,dict):
                    if {"path","sha256","bytes"}<=value.keys():queue.append(value)
                    for v in value.values():scan(v)
                elif isinstance(value,list):
                    for v in value:scan(v)
            scan(read(path))
    return dict(status="NATIVE_CPU_SCIENTIFIC_RESOURCE_CLOSURE_WITH_EXPLICIT_ENGINE_DEPENDENCIES",resources=resources,
                evidence_copy_n=sum(v["copied"] for v in resources),engine_recompute_dependency_n=sum(not v["copied"] for v in resources),
                resolver_contract="Preserve original receipts; resolve scientific original paths to hash-identical copied paths in this closure. No raw symlink fallback.",
                offline_GPU_recompute_guaranteed=False)
def normalize_score_plan(scored,plan,plan_path):
    expected=rec(plan_path);original=scored["plan"]
    if original==expected:return dict(scored),dict(status="PLAN_RECEIPT_ALREADY_CORRECT",changed_fields=[])
    known=list(plan["runtime_locks"].values())[-1]
    if original!=known:raise ValueError("Unrecognized engine score plan receipt; no automatic metadata repair")
    corrected=dict(scored);corrected["plan"]=expected
    before={k:v for k,v in scored.items() if k!="plan"};after={k:v for k,v in corrected.items() if k!="plan"}
    if before!=after:raise ValueError("Metadata repair changed score content")
    return corrected,dict(status="SCORER_LOOP_VARIABLE_SHADOWING_METADATA_ONLY_REPAIRED",changed_fields=["plan"],
                          original_plan_field=original,correct_plan_field=expected,all_other_fields_equal=True,
                          score_content_digest_without_plan=c.digest(before),scientific_source_or_scores_changed=False)
def score_with_metadata_receipt_correction(plan_path,analysis_path,worker,out):
    out=Path(out);engine=out.with_name(out.stem+"_engine_original.json")
    c.score(plan_path,analysis_path,worker,engine)
    corrected,repair=normalize_score_plan(read(engine),read(plan_path),plan_path)
    dump(out,corrected)
    dump(out.with_name(out.stem+"_metadata_repair.json"),dict(repair,engine_original=rec(engine),canonical_score=rec(out),source=rec(__file__)))
    return rec(out)
def main():
    p=argparse.ArgumentParser();p.add_argument("--plan",required=True);p.add_argument("--analysis",required=True);p.add_argument("--membership",required=True);p.add_argument("--raw-root",action="append",required=True);p.add_argument("--out-dir",required=True);p.add_argument("--pilot-only",action="store_true");a=p.parse_args()
    cpu=allocation_cpu();plan=read(a.plan)
    if plan["settings"]!=c.SETTINGS or len(plan["jobs"])!=20 or sum(j["expected_models"] for j in plan["jobs"])!=74:raise ValueError("Native frozen20/74 protocol required")
    out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=False)
    assembly=assemble(plan,a.raw_root,out/"assembled_raw",a.pilot_only);dump(out/"assembly.json",assembly)
    score_with_metadata_receipt_correction(a.plan,a.analysis,out/"assembled_raw",out/"score.json")
    audit=independent_audit(plan,out/"assembled_raw",read(out/"score.json"));dump(out/"raw_audit.json",audit)
    c.verify_result(out/"score.json",a.membership,out/"score_acceptance.json")
    # Post-score hash readback protects bytecopies from accidental linked-file modification.
    for row in assembly["rows"]:
        for pair in row.get("files",[]):verify(pair["original"]);verify(pair["copy"])
    closure=resource_closure(out,[rec(a.plan),rec(a.analysis),rec(a.membership),rec(out/"assembly.json"),rec(out/"score.json"),rec(out/"raw_audit.json"),rec(out/"score_acceptance.json"),rec(out/"score_engine_original.json"),rec(out/"score_metadata_repair.json"),rec(CODE.parent/"source_bundle.json"),rec(__file__)])
    dump(out/"resource_closure.json",closure)
    acceptance=read(out/"score_acceptance.json")
    status="NATIVE_FIRST3_PIPELINE_READINESS_ACCEPTED_NOT_ALL74" if a.pilot_only else ("NATIVE74_PIPELINE_CONTENT_ACCEPTED_WITH_TYPED_UNRESOLVED" if audit["n_raw_unresolved"] or assembly["n_jobs_copied"]<20 else "NATIVE74_ALL_RAW_CONFIDENCE_PIPELINE_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY")
    final=dict(status=status,CPU_allocation=cpu,source=rec(__file__),plan=rec(a.plan),analysis=rec(a.analysis),membership=rec(a.membership),
               assembly=rec(out/"assembly.json"),score=rec(out/"score.json"),original_engine_score=rec(out/"score_engine_original.json"),metadata_receipt_repair=rec(out/"score_metadata_repair.json"),independent_raw_audit=rec(out/"raw_audit.json"),score_acceptance=rec(out/"score_acceptance.json"),resource_closure=rec(out/"resource_closure.json"),
               jobs_expected=20,models_expected=74,jobs_original_workers_copied=assembly["n_jobs_copied"],models_raw_confidence_accepted=audit["n_raw_confidence_accepted"],models_contact_valid=acceptance["n_models_valid"],models_no_interface_or_unresolved=acceptance["n_unresolved_or_no_interface"],tests=acceptance["tests"],
               original_worker_bytes_modified=False,raw_symlinks=False,engines_summarized_separately=True,experimental_probability=None,independent_experimental_validation=False,pilot_readiness_only=a.pilot_only)
    dump(out/"acceptance.json",final)
    print(json.dumps(final,ensure_ascii=False,indent=2),flush=True)
if __name__=="__main__":main()
