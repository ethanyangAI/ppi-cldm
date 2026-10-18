#!/usr/bin/env python3
"""Independent supplemental engineering accounting/content, never formal generation."""
import argparse,hashlib,importlib.util,json,math,os,re,subprocess
from pathlib import Path
import independent_resource_policy as res
R=Path("/lustre/users/u21111210118/projects/test9")
S=R/"steps/21_method_runtime"
SCOPE="ENGINEERING_STAGE_COVERAGE_ONLY_NOT_NATIVE_ACCEPTED_NOT_FORMAL"
CONFIG={"path":str(S/"runs/supplemental_stage_prepare_13224/outputs/config.json"),"bytes":6289,"sha256":"d3e36732289706f31c672d7d42fb32d184e9edf8ba5b554861ebf65eedd053ff"}
LAUNCHER={"path":str(S/"frozen/supplemental_launcher_13227/gpu_launcher.sh"),"bytes":2225,"sha256":"68bf1237b3ffcd43315cd5833359c1ddeed4995f98dbb3a0f872434081c25d3b"}
INDEPENDENT={"path":str(R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_independent.py"),"bytes":37640,"sha256":"5128ce9776371dd88a48bac7c95fbe0a6e2c8496253394d0ea657799768aaa54"}
FORMAL={"path":str(R/"steps/22_matched_benchmark/code/formal_contract_v2/source/formal_benchmark_contract.py"),"bytes":46984,"sha256":"768c0ca8fbdf942638688ed6a12ea1e88a42b50d7c219b902bbc3d945ddeb4bc"}
MAIN={"path":str(R/"steps/22_matched_benchmark/code/engineering13175_accounting_13209/independent_acceptance.json"),"bytes":2235,"sha256":"143050799e9c9f75f964541c8d583b54edba5309c8b5c41d525708dc9fac33a2"}
AA=set("ACDEFGHIKLMNPQRSTVWY")
need=res.need;rec=res.rec;verify=res.verify;read=res.read
def load_module(name,receipt):
    p=verify(receipt,True);spec=importlib.util.spec_from_file_location(name,p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def receipt_graph(obj,seen=None):
    seen=set()if seen is None else seen
    if isinstance(obj,dict):
        if set(("path","bytes","sha256"))<=set(obj):
            key=(obj["path"],obj["sha256"])
            if key not in seen:verify({k:obj[k]for k in("path","bytes","sha256")});seen.add(key)
        for value in obj.values():receipt_graph(value,seen)
    elif isinstance(obj,list):
        for value in obj:receipt_graph(value,seen)
    return seen
def amendment_contract(amendment,new_job,old_job):
    exact={"schema":"supplemental_cpu_resource_amendment.v1","scientific_scope":SCOPE,"cancelled_pending_job":str(old_job),
      "actual_submitted_job":str(new_job),"launcher":LAUNCHER,"submit_argv":["sbatch","--parsable","--cpus-per-task=2",LAUNCHER["path"]],
      "original_requested_cpu_count":4,"amended_requested_cpu_count":2,"gpu_count":1,"gpu_budget_seconds":3600,
      "source_config_seed_default_model_calls_unchanged":True,"formal_generation_unchanged":True,"formal_candidate_pool":False}
    for key,value in exact.items():need(amendment.get(key)==value,"Resource-only amendment differs: "+key)
    return exact
def allocation_contract(sacct_text,new_job,old_job):
    rows,excluded=res.accounting_rows(sacct_text);need(set(rows)=={str(new_job),str(old_job)},"Only one supplemental positive allocation plus cancelled prior request allowed")
    cancelled=res.cancelled_zero(rows[str(old_job)],old_job)
    actual=res.terminal_allocation(rows[str(new_job)],new_job,2,1)
    need(str(new_job)not in("13175","13181","13069","13070"),"Main/historical allocation cannot be supplementary")
    return {"actual":actual,"cancelled":cancelled,"allocated_gpu_seconds":actual["allocated_gpu_seconds"],"excluded_step_rows":excluded}
def raw_pool_contract(pool,stream):
    rows=pool["rows"];need(len(rows)==20 and [x["raw_pool_index"]for x in rows]==list(range(20)),"Full original20 MPNN rows/order required")
    need(stream==rows,"Supplemental sequence stream differs from original complete20 pool")
    ids=set()
    for row in rows:
        need(row["scientific_scope"]==SCOPE,"Raw supplemental sequence has wrong scope")
        ident=row["sequence_record_id"];need(ident not in ids,"Original MPNN sequence_record_id duplicate");ids.add(ident)
        seq=row["sequence"];need(type(seq)is str and len(seq)==65 and set(seq)<=AA,"Every raw complete sequence must be65canonicalaa")
        need(row.get("native_score")is None and row.get("internal_acceptance")in(None,False),"Supplemental diagnostics cannot emit a native ranking/acceptance")
        need(row.get("retained_fixed_cysteine_positions")==[i+1 for i,aa in enumerate(seq)if aa=="C"],"Retained fixed C positions differ")
    # Exact duplicate sequence identities remain separate original lineages; no post-result dedup/sample.
    return {"raw_records":20,"unique_sequence_identities":len({x["sequence"]for x in rows}),"selected_raw_pool_index":0,"selected_sequence_record_id":rows[0]["sequence_record_id"],"all_complete_length":65}
def jsonl_complete(path):
    rows=[]
    for i,line in enumerate(Path(path).read_text().splitlines(keepends=True),1):
        need(line.endswith("\n"),"Partial supplemental raw stream cannot establish complete20 pool")
        need(line.strip(),"Blank raw sequence ledger row");rows.append(json.loads(line))
    return rows
def worker_contract(worker,new_job):
    exact={"status":"SUPPLEMENTAL_OFFICIAL_APIS_COMPLETED_NOT_NATIVE_ACCEPTANCE","scientific_scope":SCOPE,"gpu_job":str(new_job),
      "config_path":CONFIG["path"],"config_sha256":CONFIG["sha256"],"raw_mpnn_count":20,"complex_models":[1,2],"binder_models":[1,2],
      "final_filter_called":True,"formal_sequences":0}
    for key,value in exact.items():need(worker.get(key)==value,"Actual supplemental worker proof differs: "+key)
    need(type(worker["elapsed_seconds"])in(int,float)and math.isfinite(worker["elapsed_seconds"])and 0<worker["elapsed_seconds"]<=3602,"Invalid worker duration")
    return True
def content_contract(acceptance,out,cfg,new_job):
    need(acceptance["status"]=="SUPPLEMENTAL_NATIVE_API_STAGE_COVERAGE_CONTENT_CPU_ACCEPTED_NOT_SCIENTIFIC_ACCEPTANCE","Required independent CPU content collection missing")
    need(acceptance["scientific_scope"]==SCOPE and acceptance["coverage_mode"]=="FIXED_REAL_REJECTED_TRAJECTORY_SUPPLEMENTAL_API_DIAGNOSTICS","Supplemental scope misrepresented")
    for field,expected in {"source":cfg["source"],"config":CONFIG,"fixed_pose":cfg["fixed_pose"],"actual_worker":rec(out/"worker_result.json"),"gpu_allocation":rec(out/"gpu_allocation.json"),"mpnn_pool":rec(out/"mpnn_pool.json"),"basic_filter_decisions":rec(out/"native_basic_results.json"),"final_filter_diagnostics":rec(out/"supplemental_final_filters.json")}.items():
        need(acceptance[field]==expected,"Supplemental content receipt differs: "+field);verify(expected)
    need(acceptance["formal_sequences"]==acceptance["native_accepted_sequences"]==0 and acceptance["raw_pool_count"]==20 and acceptance["selected_raw_pool_index"]==0 and acceptance["actual_assigned_gpu_count"]==1,"Supplemental pool/acceptance denominator differs")
    evidence={"soluble_proteinmpnn":rec(out/"mpnn_pool.json"),"native_af2_ptm1_and_2":rec(out/"native_basic_results.json"),"native_filters":rec(out/"supplemental_final_filters.json")}
    need(acceptance["stage_evidence"]==evidence,"Required native API stage receipts differ")
    cpu_id=str(acceptance["cpu_job"]);_,f,_=res.selected(acceptance["scheduler_record"],cpu_id)
    need(f.get("JobState")=="RUNNING"and res.gpu_count(f.get("AllocTRES",f.get("TRES","")))==0,"Content collector must be actualRUNNING GPU0")
    return True
def timing_contract(launcher_budget,scheduler_launch,guard,new_job,start_epoch):
    items={}
    for line in launcher_budget.splitlines():
        key,value=line.split("=",1);need(key not in items,"Duplicate launcher budget metadata");items[key]=value
    need(items["scope"]==SCOPE and items["selected_raw_pool_index"]=="0","Budget scientific scope/raw index differs")
    need(int(items["allocation_start_epoch"])==start_epoch and int(items["generation_deadline_epoch"])==start_epoch+3590 and int(items["allocation_deadline_epoch"])==start_epoch+3600,"Slurm allocation-start budget differs")
    start=res.running_allocation(scheduler_launch,new_job,2,1)
    actual=res.running_allocation(guard["scheduler_record"],new_job,2,1)
    need(start["raw_allocation_id"]==actual["raw_allocation_id"]and start["start"]==actual["start"]and start["node"]==actual["node"],"Launcher/guard actual allocation identity differs")
    return start
def independent_ownership(guard,out_report):
    auditor=load_module("budget_independent_v4",INDEPENDENT);D=Path(out_report);D.mkdir(parents=True,exist_ok=True)
    raw=D/"original_gpu_guard_scheduler.txt";raw.write_text(guard["scheduler_record"])
    projection={"allocation_key":str(guard["job_id"]),"scheduler_start":rec(raw),"scheduler_selected_record":guard["selected_scheduler_record"],
        "hardware":guard["hardware"],"scheduler_alloc_tres":guard["scheduler_alloc_tres"],"child_cuda_visible_devices":guard["child_cuda_visible_devices"],"gpu_ownership_status":guard["status"]}
    initial=D/"derived_gpu_guard_projection.json";initial.write_text(json.dumps(projection,indent=2)+"\n");projection["initial_receipt"]=rec(initial)
    auditor.audit_gpu_ownership(projection,{"gpu_count":1,"hardware":{"gpu_name":"NVIDIA A100-PCIE-40GB"}})
    need(len(guard["hardware"]["gpus"])==1 and guard["hardware"]["gpus"][0]["memory_total_mib"]>=40000,"Actual GPU hardware memory differs")
    return {"status":"INDEPENDENT_PHYSICAL_GPU_OWNERSHIP_AND_CHILD_VISIBILITY_VERIFIED","derived_projection":rec(initial),"preserved_raw_scheduler":rec(raw),"independent_source":INDEPENDENT,"child_cuda_visible_devices":guard["child_cuda_visible_devices"],"hardware":guard["hardware"]["gpus"]}
def native_content(acceptance,out,cfg,new_job):
    formal=load_module("native_raw_array_independent_v2",FORMAL)
    target=read(verify(cfg["target_manifest"]))["target_sequence"];pool=read(out/"mpnn_pool.json");seq=pool["rows"][0]["sequence"]
    predictions=acceptance["actual_native_predictions"];need(len(predictions)==2,"Exactly two actual native complex model observations required")
    need(sorted(x["model_indices"]for x in predictions)==[[0],[1]]and sorted(x["model_names"]for x in predictions)==[["model_1_ptm"],["model_2_ptm"]],"Native API model identity differs")
    need({str(Path(x["archive"]["path"]).resolve())for x in predictions}=={str(p.resolve())for p in(out/"native_confidence").glob("*.json")},"Complete published observation universe differs")
    checks=[]
    for row in predictions:
        doc,metrics=formal.independent_native_arrays(row,target,seq)
        need(doc["method"]=="bindcraft"and doc["task_id"]=="SUPPLEMENTAL_BINDCRAFT_13175_FIRST_REJECT"and int(doc["attempt_index"])==0 and int(doc["replicate_seed"])==cfg["seed"],"Supplemental query lineage/replicate differs")
        need(doc["method_config_sha256"]==CONFIG["sha256"]and doc["target_manifest_sha256"]==cfg["target_manifest"]["sha256"],"Supplemental config/target archive identity differs")
        need(row["context"]["sequence_record_ids"]==[pool["rows"][0]["sequence_record_id"]],"Predetermined rawindex0 lineage differs")
        for key,value in metrics.items():need(math.isclose(value,row["metrics"][key],rel_tol=0,abs_tol=3e-6 if key=="binder_plddt"else 1e-12),"CPU content/rawarrays metric differs:"+key)
        checks.append({"archive":row["archive"],"arrays":row["arrays"],"raw_pdb":row["raw_pdb"],"model_names":row["model_names"],"metrics":metrics,"ranking_eligible":False})
    final=read(out/"supplemental_final_filters.json")
    need(final["scope"]==SCOPE and set(final["actual_complex_statistics"])=={"1","2"}and set(final["actual_binder_statistics"])=={"1","2"},"Actual two-model late API statistics missing")
    # Original default API results, including every rejection, are retained; no positivity requirement.
    return {"status":"ALL2_ACTUAL_RAW_ARRAY_QUERY_PDB_CONFIDENCE_INDEPENDENTLY_RECOMPUTED","observations":checks,"default_filter_api_result":final["default_filter_api_result"],"native_basic_results":rec(out/"native_basic_results.json"),"final_diagnostics":rec(out/"supplemental_final_filters.json"),"native_accepted_sequences":0}
def audit(actual_job,cancelled_job,amendment_path,output_dir,content_acceptance,report_dir):
    cpu=res.cpu_guard();D=Path(report_dir);need(not D.exists(),"Never overwrite independent evidence");D.mkdir(parents=True)
    verify(CONFIG,True);verify(LAUNCHER,True);cfg=read(CONFIG["path"]);graph=receipt_graph(cfg)
    amendment=read(verify(rec(amendment_path),True));amendment_contract(amendment,actual_job,cancelled_job)
    sacct_argv=["sacct","-X","-P","-n","-j",str(actual_job)+","+str(cancelled_job),"--format=JobIDRaw,ElapsedRaw,AllocTRES,State,Start,End,NodeList,Partition"]
    sacct_raw=subprocess.check_output(sacct_argv,text=True);(D/"sacct_raw.txt").write_text(sacct_raw);account=allocation_contract(sacct_raw,actual_job,cancelled_job)
    out=Path(output_dir).resolve();need(out==S/("runs/bindcraft_supplemental_gpu_"+str(actual_job))/"outputs","Actual output allocation directory differs")
    guard=read(out/"gpu_allocation.json");need(str(guard["job_id"])==str(actual_job),"Guard actual allocation ID differs")
    ownership=independent_ownership(guard,D/"ownership");_,fields,_=res.selected(guard["scheduler_record"],actual_job)
    start_epoch=int(__import__("datetime").datetime.fromisoformat(fields["StartTime"]).timestamp())
    timing=timing_contract((out.parent/"launcher_budget.txt").read_text(),(out.parent/"scheduler_at_launch.txt").read_text(),guard,actual_job,start_epoch)
    need(timing["start"]==account["actual"]["start"]and timing["node"]==account["actual"]["node"]and account["actual"]["partition"]=="organ","Initial/terminal allocation identity differs")
    worker=read(out/"worker_result.json");worker_contract(worker,actual_job)
    pool=raw_pool_contract(read(out/"mpnn_pool.json"),jsonl_complete(out/"supplemental_sequences.jsonl"))
    need(not(out/"sequences.jsonl").exists()and not(out/"native_screening.jsonl").exists(),"Supplemental sequences leaked into formal ledger")
    content_receipt=rec(content_acceptance);acceptance=read(verify(content_receipt));content_contract(acceptance,out,cfg,actual_job)
    native=native_content(acceptance,out,cfg,actual_job)
    main=read(verify(MAIN,True));need(main["all_allocated_gpu_seconds"]==591 and main["expected_tasks"]==2 and main["allocation_count"]==2,"Main591 exacttwo allocations altered")
    report={"schema":"independent_supplemental_allocation_and_content.v1","status":"INDEPENDENT_SUPPLEMENTAL_BUDGET_OWNERSHIP_AND_ACTUAL_CONTENT_AUDIT_PASS",
      "scientific_scope":SCOPE,"coverage_mode":"supplemental_api_coverage","full_budget_comparable":False,"formal_sequences":0,"native_accepted_sequences":0,
      "source":rec(__file__),"resource_source":rec(res.__file__),"cpu_allocation":cpu,"config":CONFIG,"launcher":LAUNCHER,"amendment":rec(amendment_path),
      "content_acceptance":content_receipt,"original_gpu_guard":rec(out/"gpu_allocation.json"),"sacct_argv":sacct_argv,"sacct_raw":rec(D/"sacct_raw.txt"),
      "accounting":account,"allocated_gpu_seconds":account["allocated_gpu_seconds"],"allocated_cpu_count":2,"ownership":ownership,"launcher_timing":timing,
      "pool":pool,"native_content":native,"config_graph_receipt_count":len(graph),"raw_sequences":rec(out/"supplemental_sequences.jsonl"),
      "main_accounting_unchanged":MAIN,"main_gpu_seconds_not_in_supplemental_cost":591,"main_physical_ids_excluded":["13181","13175"],
      "cancelled_prior_request_gpu_seconds":0,"scientific_interpretation":"Supplemental later API coverage on a fixed real scientifically rejected pose; no formal throughput or superiority claim"}
    (D/"acceptance.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps(report))
    return report
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--actual-job",required=True);ap.add_argument("--cancelled-job",default="13229");ap.add_argument("--amendment",required=True);ap.add_argument("--output-dir",required=True);ap.add_argument("--content-acceptance",required=True);ap.add_argument("--report-dir",required=True);a=ap.parse_args()
    audit(a.actual_job,a.cancelled_job,a.amendment,a.output_dir,a.content_acceptance,a.report_dir)
if __name__=="__main__":main()

