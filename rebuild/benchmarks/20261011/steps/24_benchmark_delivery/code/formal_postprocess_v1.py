#!/usr/bin/env python3
"""CPU receipt orchestration only. Frozen methods, accounting, native audits and
common preparation are delegated unchanged to their accepted implementations.
No inference, GPU submission, method settings, selection rules or publication.
"""
import argparse,collections,hashlib,importlib.util,json,os,re,shlex,stat,subprocess,sys
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
SELF=Path(__file__).resolve()
CORE=R/"env/core/bin/python"
PINS={
"budget":("steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py",84446,"b37227bd862ee1425a59f5308be1ee3f4824042dea5d71c1269ad0f406b318f9"),
"independent":("steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_independent.py",37640,"5128ce9776371dd88a48bac7c95fbe0a6e2c8496253394d0ea657799768aaa54"),
"formal":("steps/22_matched_benchmark/code/formal_contract_v2/source/formal_benchmark_contract.py",46984,"768c0ca8fbdf942638688ed6a12ea1e88a42b50d7c219b902bbc3d945ddeb4bc"),
"native":("steps/21_method_runtime/runs/native_collector_contracts_13166/source/audit_native_confidence_v8.py",16372,"eca561182d06eca52bde005b45f02dd261d57b916d70ea5e34e99e86a79830b5"),
"common":("steps/23_common_review/frozen/common_core_v2_13130/code/benchmark_common_review_v2.py",62153,"7d72314e0409fa1fb2a6ed86f593b198cf3e5c99f747c58d8cfa7d1fd0404d17"),
"msa":("steps/23_common_review/runs/msa_content_12983/msa.json",10412,"edfd913d745b84e8412bcb13a46dd2862f63fc9757d8e9c69c7e7ff153b9e61f"),
"previous_registry":("steps/23_common_review/inputs/registry7_bridge13010.json",37816,"e46a7a3985d6675d6f27ffba5e0870b3c665d275142dd21b68ae993d5ea6cae8")}
PREPARED=R/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/prepared_inputs.json"
TARGETS={"MDM2_1YCR","KEAP1_2FLU","EGFR_DIII_1IVO","BCLXL_2M04","HRAS_4G0N","CRK_SH3_1CKA","BBF111_9HAG"}
ACTIVE_STATES={"RUNNING","PENDING","CONFIGURING","COMPLETING","SUSPENDED","RESIZING","REQUEUED","REQUEUE_FED","SIGNALING","STAGE_OUT"}
def need(ok,why):
    if not ok: raise ValueError(why)
def rec(path):
    p=Path(path).resolve();h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
    return dict(path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest())
def read(path):return json.loads(Path(path).read_text())
def verify(r):
    need(rec(r["path"])==r,"Receipt mismatch: "+r["path"]);return Path(r["path"])
def dump(path,obj):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("x") as f:json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
    return rec(p)
def project(path):
    p=Path(path).resolve();p.relative_to(R);return p
def pin(key):
    rel,n,h=PINS[key];r=dict(path=str(R/rel),bytes=n,sha256=h);verify(r);return r
def module(key):
    path=verify(pin(key));spec=importlib.util.spec_from_file_location("postprocess_"+key,path)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
def cpu():
    need(os.environ.get("CUDA_VISIBLE_DEVICES","")=="","CPU orchestration requires exact empty CUDA mask")
    need(Path.cwd()==R/"steps/22_matched_benchmark","CPU orchestration working directory must be step22")
    need(os.environ.get("PYTHONDONTWRITEBYTECODE")=="1","Do not mutate frozen import trees with bytecode")
    return module("formal").cpu_guard()
def immutable():
    p=SELF.parent/"source_snapshot.json";snapshot=read(p)
    need(snapshot["schema"]=="formal_postprocess_source.v1","Invalid source context")
    need(snapshot["entry"]==rec(SELF),"Orchestrator differs from immutable snapshot")
    need(not(SELF.stat().st_mode&0o222) and not(SELF.parent.stat().st_mode&0o222),"Readonly source snapshot required")
    for item in snapshot["files"]:verify(item)
    for key in PINS:pin(key)
    return rec(p)
def fresh_out(path):
    p=project(path);p.mkdir(parents=True,exist_ok=False);return p
def load_plan(path,sha):
    path=project(path);receipt=rec(path)
    need(receipt["sha256"]==sha,"Exact root-frozen plan hash required")
    budget=module("budget");formal=module("formal")
    plan=budget.validate_frozen_plan(path,expected_sha256=sha,require_expected=True,require_current_orchestrator=False)
    formal.formal_protocol(plan["protocol"])
    need(plan["tasks"]==formal.task_matrix(plan["protocol"]),"Exact frozen28 matrix required")
    return plan,receipt
def expected_slots(plan,array_id,runroot):
    need(re.fullmatch(r"\d+",str(array_id)) is not None,"Numeric Slurm array ID required")
    ids=[t["task_id"] for t in plan["tasks"]]
    need(len(ids)==28 and len(set(ids))==28,"Unique complete28 slot matrix required")
    need([t["array_index"] for t in plan["tasks"]]==list(range(28)),"Frozen array index order differs")
    root=Path(runroot)
    return [dict(task=t,logical_allocation_key=str(array_id)+"_"+str(i),
                 expected_run_receipt=str(root/(str(array_id)+"_"+str(i))/"run_receipt.json"))
            for i,t in enumerate(plan["tasks"])]
def discover_receipts(plan,plan_receipt,array_id,runroot):
    slots=expected_slots(plan,array_id,runroot);receipts=[];seen=set()
    expected={x["expected_run_receipt"] for x in slots}
    for p in Path(runroot).glob(str(array_id)+"_*/run_receipt.json"):
        need(str(p) in expected,"Unexpected array-index receipt: "+str(p))
    for row in slots:
        p=Path(row["expected_run_receipt"])
        if not p.is_file():
            row.update(status="RUN_RECEIPT_UNAVAILABLE",run_receipt=None,
                       meaning="Unresolved generation; never an empty observed sequence pool")
            continue
        rr=rec(p);run=read(p)
        need(run["plan"]==plan_receipt and run["task"]==row["task"],"Run exact plan/task mismatch")
        logical=run.get("logical_allocation_key",run.get("allocation_key"))
        need(logical==row["logical_allocation_key"],"Run logical allocation differs from frozen array slot")
        raw=str(run.get("raw_allocation_id",run.get("allocation_identity",{}).get("raw_allocation_id","")))
        need(re.fullmatch(r"\d+",raw) is not None and raw not in seen,"Duplicate or invalid physical allocation ID")
        seen.add(raw);receipts.append(rr)
        row.update(status="DURABLE_RUN_RECEIPT_PRESENT",run_receipt=rr,raw_allocation_id=raw,run_status=run["status"])
    return slots,receipts
def scheduler_snapshot(array_id,out):
    args=["sacct","-X","-j",str(array_id),"--noheader","--parsable2",
          "--format=JobIDRaw,ElapsedRaw,AllocTRES,State,Start,End,NodeList,Partition"]
    result=subprocess.run(args,text=True,capture_output=True)
    (out/"sacct.stderr.txt").write_text(result.stderr)
    (out/"sacct_8.txt").write_text(result.stdout)
    dump(out/"sacct_command.json",dict(argv=args,returncode=result.returncode,raw=rec(out/"sacct_8.txt"),stderr=rec(out/"sacct.stderr.txt")))
    need(result.returncode==0,"sacct failed; raw error retained")
    budget=module("budget");rows,excluded=budget.parse_sacct(result.stdout)
    need(bool(rows),"No scheduler allocation rows returned")
    totals=dict(status="SCHEDULER_COST_ONLY_NOT_CONTENT_ACCEPTANCE",
       physical_rows=len(rows),allocated_gpu_seconds=sum(v["elapsed_seconds"]*v["gpu_count"] for v in rows.values()),
       rows=list(rows.values()),excluded_step_or_array_summary_rows=excluded,
       scope="Only this formal array. Engineering/control/supplemental costs remain separate; never counted again here.")
    dump(out/"scheduler_cost_inventory.json",totals)
    need(not any(v["state"] in ACTIVE_STATES for v in rows.values()),"Array contains nonterminal allocations; no downstream preparation")
    return result.stdout,rows
def check_allocation_joins(rows,receipts):
    used=[str(read(verify(r)).get("raw_allocation_id","")) for r in receipts]
    need(len(used)==len(set(used)),"Duplicate physical allocation receipts")
    missing=[k for k,v in rows.items() if v["gpu_count"]>0 and v["elapsed_seconds"]>0 and k not in used]
    need(not missing,"Positive GPU allocations have no receipt: "+",".join(missing))
    need(set(used)<=set(rows),"Run allocation absent from scheduler snapshot")
    return dict(positive_allocations_joined=True,zero_cost_unjoined_rows=[k for k in rows if k not in used],
                missing_receipts_do_not_mean_zero_sequences=True)
def run_cpu(argv,outprefix):
    env=dict(os.environ,CUDA_VISIBLE_DEVICES="",JAX_PLATFORMS="cpu",PYTHONNOUSERSITE="1",
             OPENBLAS_NUM_THREADS="1",PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH",None)
    outprefix=Path(outprefix)
    with Path(str(outprefix)+".stdout").open("x") as so,Path(str(outprefix)+".stderr").open("x") as se:
        completed=subprocess.run(argv,env=env,stdout=so,stderr=se)
    result=dict(argv=[str(v) for v in argv],returncode=completed.returncode,
                stdout=rec(str(outprefix)+".stdout"),stderr=rec(str(outprefix)+".stderr"))
    dump(str(outprefix)+".command.json",result)
    need(completed.returncode==0,"Frozen CPU API failed; see "+str(outprefix)+".stderr")
    return result
def read_run_ledgers(run):
    b=module("budget")
    attempts=b.rows_jsonl(b.verified(run["attempt_ledger"]))
    events=b.rows_jsonl(b.verified(run["sequence_ledger"]))
    updates=b.rows_jsonl(b.verified(run["native_screening_ledger"])) if run.get("native_screening_ledger") else []
    return attempts,events,updates
def audit_attempts(plan,plan_receipt,receipts,out):
    formal=module("formal");native=pin("native");bundle=dict(schema="formal_native_output_audit_bundle.v1",
        plan=plan_receipt,collector_source=native,attempts=[])
    raw=[];issues=[];attempt_total=0
    for rr in receipts:
        run=read(verify(rr));attempts,events,updates=read_run_ledgers(run)
        raw.append(dict(run_receipt=rr,**formal.raw_closure(run,attempts,events,updates,65)))
        task=run["task"];method=next(m for m in plan["protocol"]["methods"] if m["method_id"]==task["method_id"])
        target=next(t["input_manifest"] for t in plan["protocol"]["targets"] if t["target_id"]==task["target_id"])
        runtime=method["adapter_receipts"][0];verify(runtime);verify(target);verify(method["config_receipt"])
        for attempt in attempts:
            attempt_total+=1;i=attempt["attempt_index"];folder=out/"native_attempts"/task["task_id"]/("%06d"%i)
            folder.parent.mkdir(parents=True,exist_ok=True)
            stem=folder.parent/("%06d_collector"%i)
            argv=[str(CORE),native["path"],"--attempt-dir",str(Path(rr["path"]).parent/"attempts"/("%06d"%i)),
                  "--target-manifest",target["path"],"--config",method["config_receipt"]["path"],
                  "--config-sha256",method["config_receipt"]["sha256"],"--runtime-source",runtime["path"],
                  "--output-dir",str(folder)]
            try:
                run_cpu(argv,stem);accept=folder/"acceptance.json"
                item=read(accept)
                need(item["no_new_predictions"] is True,"Native collector must never predict")
                bundle["attempts"].append(dict(run_receipt=rr,task_id=task["task_id"],attempt_index=i,acceptance=rec(accept)))
            except Exception as e:
                issues.append(dict(task_id=task["task_id"],run_receipt=rr,attempt_index=i,
                                   status="NATIVE_CPU_AUDIT_UNRESOLVED",reason=str(e),log_prefix=str(stem)))
    dump(out/"all_attempt_observation_inventory.json",dict(attempt_count=attempt_total,accepted=len(bundle["attempts"]),
        issues=issues,raw_length_and_dual_stream_closure=raw,zero_attempt_runs=[r["run_receipt"] for r in raw if r["n_attempts"]==0]))
    need(not issues and len(bundle["attempts"])==attempt_total,"Some native attempts unresolved; no cohort selection permitted")
    closures=[]
    for rr in receipts:
        run=read(verify(rr));attempts,events,updates=read_run_ledgers(run)
        closures.append(dict(run_receipt=rr,**formal.native_output_closure(plan,rr,run,attempts,events,updates,bundle)))
    dump(out/"native_audits.json",bundle)
    dump(out/"native_independent_closure.json",dict(status="ALL_ACTUAL_ATTEMPTS_NATIVE_RAW_ARRAYS_AND_UPDATES_VERIFIED",
         plan=plan_receipt,collector=native,independent_source=pin("formal"),closures=closures,
         attempt_count=attempt_total,no_new_predictions=True))
    return bundle
def collect(args):
    guard=cpu();source=immutable();plan,pr=load_plan(args.plan,args.plan_sha256);out=fresh_out(args.out)
    try:
        slots,receipts=discover_receipts(plan,pr,args.array_job_id,project(args.run_root))
        dump(out/"fixed_generation_slots.json",dict(plan=pr,slots=slots,frozen_count=28))
        dump(out/"run_receipts.json",receipts)
        raw,rows=scheduler_snapshot(args.array_job_id,out)
        joins=check_allocation_joins(rows,receipts);dump(out/"allocation_joins.json",joins)
        b=module("budget");account=b.independent_accounting(plan,receipts,raw)
        account.update(plan=pr,raw_sacct=rec(out/"sacct_8.txt"))
        dump(out/"accounting.json",account)
        # All score identities are independently checked before native cohort ranking.
        audit_attempts(plan,pr,receipts,out)
        cohorts=b.cohorts(plan,account["inventory"],account["tasks"])
        cohorts.update(frozen_plan=pr,accounting=rec(out/"accounting.json"))
        dump(out/"cohorts.json",cohorts)
        ind=module("independent").audit(Path(args.plan),out/"run_receipts.json",out/"sacct_8.txt",out/"accounting.json",out/"cohorts.json")
        ind.update(slurm_job_id=os.environ["SLURM_JOB_ID"]);dump(out/"independent_budget.json",ind)
        matrix=module("formal").generation_matrix(plan,account,cohorts,ind)
        dump(out/"generation_contract.json",dict(status="FROZEN_28_GENERATION_AND_COHORT_MATRIX_VERIFIED",result=matrix,
            coverage_count=len(cohorts["coverage"]),selected_count=len(cohorts["selected"])))
        files={n:rec(out/(n+".json")) for n in ["fixed_generation_slots","run_receipts","allocation_joins","accounting","native_audits",
             "native_independent_closure","all_attempt_observation_inventory","cohorts","independent_budget","generation_contract","scheduler_cost_inventory"]}
        result=dict(schema="formal_postprocess_collection.v1",status="FORMAL_ALLOCATION_NATIVE_AND_COHORT_CLOSURE_ACCEPTED",
            plan=pr,source_snapshot=source,allocation=guard,array_job_id=str(args.array_job_id),run_root=str(project(args.run_root)),files=files,
            sources={k:pin(k) for k in ["budget","independent","formal","native"]},
            frozen_tasks=28,receipt_count=len(receipts),coverage_count=28,
            full_budget_comparable_tasks=ind["full_budget_comparable_tasks"],selected_members=len(cohorts["selected"]),
            actual_array_gpu_seconds=ind["all_allocated_gpu_seconds"],no_new_predictions=True,no_gpu_submission=True,
            experimental_binding_or_blockade=False,workflow_superiority=False)
        final=dump(out/"acceptance.json",result);print(json.dumps(final))
    except Exception as e:
        dump(out/"typed_incomplete.json",dict(schema="formal_postprocess_incomplete.v1",
            status="FORMAL_POSTPROCESS_TYPED_INCOMPLETE",plan=pr,source_snapshot=source,allocation=guard,
            reason_type=type(e).__name__,reason=str(e),no_cohort_or_common_promotion=True,
            existing_files=[rec(p) for p in sorted(out.glob("*.json"))],
            no_new_predictions=True,no_gpu_submission=True))
        raise
def exact_membership(cohorts,membership):
    selected=cohorts["selected"];members=membership["members"]
    ids=[m["cohort_record_id"] for m in members];expected=[m["cohort_record_id"] for m in selected]
    need(len(set(ids))==len(ids) and len(set(expected))==len(expected),"Duplicate cohort membership IDs")
    need(set(ids)==set(expected),"Blind membership lost/added cohort")
    by={m["cohort_record_id"]:m for m in members}
    for row in selected:
        need(all(by[row["cohort_record_id"]].get(k)==v for k,v in row.items()),"Blind mapping altered preselected identity")
    need(membership["coverage"]==cohorts["coverage"],"Empty/unresolved task coverage changed")
    return dict(selected_members=len(selected),membership_members=len(members),fixed_task_coverage=len(cohorts["coverage"]))
def prepare_common(args):
    guard=cpu();source=immutable();accepted_path=project(args.collection);accepted=read(accepted_path)
    need(rec(accepted_path)["sha256"]==args.collection_sha256,"Exact collection acceptance required")
    need(accepted["status"]=="FORMAL_ALLOCATION_NATIVE_AND_COHORT_CLOSURE_ACCEPTED","Native/accounting/cohort gate not accepted")
    for r in accepted["files"].values():verify(r)
    plan,pr=load_plan(verify(accepted["plan"]),accepted["plan"]["sha256"])
    out=fresh_out(args.out);common=module("common");msa=pin("msa");old_registry=read(verify(pin("previous_registry")))
    try:
        prepared=read(PREPARED);entries=common.target_entries(prepared)
        actual={x["target_id"]:x.get("input_manifest",x.get("identity")) for x in entries}
        expected={x["target_id"]:x["input_manifest"] for x in plan["protocol"]["targets"]}
        need(actual==expected,"Prepared chainfix13094 inputs differ from frozen formal targets")
        common.target_registry(PREPARED,out/"registry.json")
        registry=read(out/"registry.json");old={x["target_id"]:x for x in old_registry["targets"]}
        need({x["target_id"] for x in registry["targets"]}==TARGETS,"Seven exact common targets required")
        for target in registry["targets"]:
            before={k:v for k,v in old[target["target_id"]].items() if k!="input_manifest"}
            after={k:v for k,v in target.items() if k!="input_manifest"}
            need(before==after,"Metadata-only chainfix changed common scientific input: "+target["target_id"])
        common.prepare(out/"registry.json",verify(msa),verify(accepted["files"]["cohorts"]),out/"inference_plan.json",verify(plan["protocol_receipt"]))
        inference=read(out/"inference_plan.json");membership=read(out/"membership.json");cohorts=read(verify(accepted["files"]["cohorts"]))
        mapping=exact_membership(cohorts,membership)
        need(inference["method_origin_present"] is False,"Inference plan is not blinded")
        jobs=inference["jobs"];keys=[x["job_key"] for x in jobs]
        need(len(keys)==len(set(keys)),"Duplicate blind inference jobs")
        launch=dict(schema="formal_common_review_dispatch.v1",status="CPU_PREPARED_ROOT_GPU_SUBMISSION_REQUIRED",
            inference_plan=rec(out/"inference_plan.json"),analysis_plan=rec(out/"analysis_plan.json"),
            membership=rec(out/"membership.json"),jobs=[dict(index=i,job_key=j["job_key"],engine=j["engine"],
                variant=j["variant"],expected_models=j["expected_models"],signature=common.job_signature(j)) for i,j in enumerate(jobs)],
            job_count=len(jobs),frozen_model_slots=sum(j["expected_models"] for j in jobs),global_project_gpu_concurrency_cap=2,
            worker_source=pin("common"),submission_performed=False,
            cache_policy="No cache substitution performed here. Root must bind exact accepted worker/job signatures for any reuse; otherwise the fixed slot remains pending.",
            independent_claims=False)
        dump(out/"root_dispatch.json",launch)
        final=dump(out/"acceptance.json",dict(schema="formal_common_preparation.v1",
           status="FORMAL_BLIND_COMMON_REVIEW_PREPARED_NOT_INFERRED",source_snapshot=source,allocation=guard,
           collection=rec(accepted_path),plan=pr,prepared_inputs=rec(PREPARED),source=pin("common"),msa=msa,
           input_science_identical_to_accepted_registry=True,membership_closure=mapping,
           outputs={n:rec(out/(n+".json")) for n in ["registry","inference_plan","analysis_plan","membership","root_dispatch"]},
           no_new_predictions=True,no_gpu_submission=True))
        print(json.dumps(final))
    except Exception as e:
        dump(out/"typed_incomplete.json",dict(status="FORMAL_COMMON_PREPARATION_INCOMPLETE",reason_type=type(e).__name__,
             reason=str(e),collection=rec(accepted_path),no_new_predictions=True,no_gpu_submission=True))
        raise
def freeze_snapshot(args):
    allocation=cpu();out=Path(args.out).resolve()
    need(out==SELF.parent/"source_snapshot.json","Source snapshot must sit beside entry")
    launcher=SELF.parent/"formal_postprocess_cpu_v1.sbatch"
    text=launcher.read_text();need(text.count("__FROZEN_FORMAL_POSTPROCESS_ENTRY__")==1,"Unfrozen launcher placeholder required")
    launcher.write_text(text.replace("__FROZEN_FORMAL_POSTPROCESS_ENTRY__",shlex.quote(str(SELF))))
    files=[rec(p) for p in sorted(SELF.parent.glob("formal_postprocess_*")) if p.is_file() and p.suffix in {".py",".sbatch",".md"}]
    need(bool(files),"No sources to freeze")
    d=dict(schema="formal_postprocess_source.v1",status="CPU_ORCHESTRATION_SOURCE_FROZEN_NO_INFERENCE",
           entry=rec(SELF),files=files,source_pins={k:pin(k) for k in PINS},allocation=allocation,
           prepared_inputs=rec(PREPARED),no_settings_or_selection_changes=True)
    dump(out,d)
    for p in SELF.parent.iterdir():
        if p.is_file():p.chmod(0o444)
    SELF.parent.chmod(0o555)
    print(json.dumps(rec(out)))
def main():
    p=argparse.ArgumentParser(description=__doc__);sp=p.add_subparsers(dest="command",required=True)
    a=sp.add_parser("freeze-snapshot");a.add_argument("--out",required=True)
    a=sp.add_parser("collect")
    for name in ["plan","plan-sha256","array-job-id","run-root","out"]:a.add_argument("--"+name,required=True)
    a=sp.add_parser("prepare-common")
    for name in ["collection","collection-sha256","out"]:a.add_argument("--"+name,required=True)
    a=p.parse_args()
    {"freeze-snapshot":freeze_snapshot,"collect":collect,"prepare-common":prepare_common}[a.command](a)
if __name__=="__main__":main()

