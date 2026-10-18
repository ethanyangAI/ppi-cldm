#!/usr/bin/env python3
"""CPU-only terminal receipt sealing and invocation of immutable formal V2.
No model call, GPU submission, threshold change, early sampling or publication.
New bootstrap is readonly before root submission; exact source hash is first
computed in this CPU allocation. This does not claim a prior CPU contract run.
"""
import argparse,ast,datetime,hashlib,importlib.util,json,os,re,subprocess,sys,time,unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
D=R/"steps/22_matched_benchmark/code/formal13260_terminal_v3"
SELF=D/"formal13260_terminal.py"
CORE=R/"env/core/bin/python"
ARRAY="13260"
RUNROOT=R/"steps/22_matched_benchmark/formal_runs"
SUBMIT=R/"steps/22_matched_benchmark/formal_submission_13260/submit_receipt.json"
def receipt(rel,n,h):return dict(path=str(R/rel),bytes=n,sha256=h)
PINS={
"plan":receipt("steps/22_matched_benchmark/formal_freeze_13257/plan/frozen_plan.json",20295,"e913d1bbccd531bf88a73f6ba60e8a0de85bb03ad8bcd3455d8952ca4effe0b6"),
"protocol":receipt("steps/22_matched_benchmark/formal_freeze_13257/plan/protocol.json",10451,"26875ac0fa8382d812b89d9ed101428bd3cb2b79d661a987513a31ce309d2724"),
"policy":receipt("steps/22_matched_benchmark/formal_launchpolicy_13259/resource_policy.json",6712,"a996cac084eb6630dc4c34a62b581f2bf298d5d720350f4f702476adb8df073e"),
"launcher":receipt("steps/22_matched_benchmark/formal_launchpolicy_13259/formal_generation_cpu3.sbatch",1539,"5f02bf6ce198c26f2751a5eb3e32bc57530270ef99094572a229d6d313ef91fb"),
"original_launcher":receipt("steps/22_matched_benchmark/formal_freeze_13257/plan/formal_generation.sbatch",1539,"17275e9a2f3ef5290168e52cffa0466013e71e638b7d3e74f79d763034afe339"),
"pregeneration":receipt("steps/22_matched_benchmark/code/formal_pre_generation_13259/acceptance.json",147692,"0dbbf862c607311ae498b2d7aa4910f8b0bc40ec872927febc51ec5a02f7af23"),
"seeded":receipt("steps/22_matched_benchmark/code/seeded_supplemental13246_audit_13254/acceptance.json",16093,"c94d0d7f3cf05a83f1d6b6b621936296bdaeaccda00b852b314165e4bb35b04f"),
"entry":receipt("steps/24_benchmark_delivery/frozen/formal_postprocess_v2_13258/code/formal_postprocess_v2.py",35372,"b04fc8e8c01b7b5a646a854e031aba519081ba4dc2c13c38d83870146b1727a2"),
"entry_snapshot":receipt("steps/24_benchmark_delivery/frozen/formal_postprocess_v2_13258/code/source_snapshot.json",5627,"87969e3ec3177405a79039c37671eba159ac4bd0bc49b8e2e517406628265317"),
"resource":receipt("steps/22_matched_benchmark/code/resource_contract_v3/source/independent_resource_policy.py",17811,"8449b40f4ffbe3d9e321335bccb9bfcc163291ac3f67497c66fe1555bcd2f6bc"),
"independent":receipt("steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_independent.py",37640,"5128ce9776371dd88a48bac7c95fbe0a6e2c8496253394d0ea657799768aaa54"),
"native":receipt("steps/21_method_runtime/runs/native_collector_contracts_13166/source/audit_native_confidence_v8.py",16372,"eca561182d06eca52bde005b45f02dd261d57b916d70ea5e34e99e86a79830b5")
}
def need(condition,why):
    if not condition:raise ValueError(why)
def rec(path):
    p=Path(path).resolve();h=hashlib.sha256()
    with p.open("rb")as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    return dict(path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest())
def read(path):return json.loads(Path(path).read_text())
def verify(r,readonly=True):
    p=Path(r["path"]);need(p.is_file()and not p.is_symlink(),"Regular nonsymlink authority required")
    need(rec(p)==r,"Exact receipt mismatch: "+str(p))
    need(not readonly or not(p.stat().st_mode&0o222),"Authority is writable: "+str(p))
    return p
def write(path,obj,readonly=False):
    p=Path(path)
    with p.open("x")as f:json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
    if readonly:p.chmod(0o444)
    return rec(p)
def module(name,r):
    p=verify(r);sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m);return m
def check_env(env,cwd):
    need(env.get("CUDA_VISIBLE_DEVICES")=="","CPU wrapper needs exact empty CUDA mask")
    need(env.get("PYTHONDONTWRITEBYTECODE")=="1","Frozen bytecode writes forbidden")
    need(env.get("PYTHONNOUSERSITE")=="1","User-site imports forbidden")
    need(env.get("OPENBLAS_NUM_THREADS")=="1","CPU BLAS threads must be1")
    need(env.get("JAX_PLATFORMS")=="cpu","CPU JAX required")
    need("PYTHONPATH"not in env,"External PYTHONPATH forbidden")
    need(env.get("SLURM_JOB_ID","").isdigit(),"Actual numeric Slurm allocation required")
    need(Path(cwd)==R/"steps/22_matched_benchmark","Wrong step22 working directory")
def check_submit(obj,policy_epoch):
    need(obj.get("schema")=="paired_formal_resource_submission.v1","Submission schema differs")
    need(str(obj.get("job_id"))==ARRAY,"Only root13260 primary array accepted")
    need(obj.get("submit_argv")==["sbatch","--parsable",PINS["launcher"]["path"]],"Any CLI override or extra scheduler invocation rejected")
    for field,key in [("launcher","launcher"),("resource_policy","policy"),("plan","plan"),("pre_generation_independent_gate","pregeneration"),("current_seeded_supplemental_independent_gate","seeded")]:
        need(obj.get(field)==PINS[key],"Submission exact authority differs: "+field)
    stamp=obj.get("submitted_at_epoch");need(isinstance(stamp,(int,float))and stamp>policy_epoch,"Submission predates immutable policy")
    need(obj.get("root_owned_primary_array")is True,"Root ownership assertion missing")
    need(obj.get("global_project_gpu_concurrency_cap")==2,"GPU concurrency cap differs")
    need(obj.get("source_settings_unchanged")is True,"Source/settings declaration changed")
    need(obj.get("raw_sbatch_stdout")=="13260\n","Raw sbatch allocation ID differs")
    need(obj.get("raw_sbatch_stderr")=="","Submission stderr needs separate review")
    need(obj.get("cpu_cgroup_isolation_status")=="UNOBSERVED","Cannot invent cgroup CPU observation")
    return True
def check_terminal(rows,queue_stdout):
    need(queue_stdout.strip()=="","Array still queued; no collect/selection permitted")
    need(bool(rows),"Actual scheduler allocation records missing")
    terminal={"COMPLETED","FAILED","CANCELLED","TIMEOUT","OUT_OF_MEMORY","NODE_FAIL","PREEMPTED","BOOT_FAIL"}
    need(all(x["state"]in terminal for x in rows.values()),"Nonterminal accounting row; no collect")
def command(argv,prefix,env=None):
    prefix=Path(prefix)
    with Path(str(prefix)+".stdout").open("x")as so,Path(str(prefix)+".stderr").open("x")as se:
        result=subprocess.run(argv,stdout=so,stderr=se,env=env)
    report=dict(argv=[str(x)for x in argv],returncode=result.returncode,stdout=rec(str(prefix)+".stdout"),stderr=rec(str(prefix)+".stderr"))
    write(str(prefix)+".command.json",report)
    return report
def readonly_tree(path):
    for p in path.rglob("*"):
        if p.is_file():p.chmod(0o444)
    for p in sorted(path.rglob("*"),reverse=True):
        if p.is_dir():p.chmod(0o555)
    path.chmod(0o555)
def source_bootstrap(out):
    need(Path(__file__).resolve()==SELF,"Readonly wrapper absolute source identity differs")
    need(not(D.stat().st_mode&0o222),"Readonly wrapper source directory required")
    files=[]
    for name in ["formal13260_terminal.py","test_formal13260_terminal.py","formal13260_terminal_cpu.sbatch","HANDOFF.md"]:
        p=D/name;need(p.is_file()and not p.is_symlink()and not(p.stat().st_mode&0o222),"Readonly bootstrap source required")
        if p.suffix==".py":compile(p.read_bytes(),str(p),"exec",dont_inherit=True)
        files.append(rec(p))
    return write(out/"bootstrap_source.json",dict(schema="formal13260_terminal_source.v1",status="READONLY_SOURCE_FIRST_CPU_HASH_SEALED",files=files,
        pre_submission_cpu_contract_status="NOT_EXECUTED_RESOURCE_UNAVAILABLE",no_model_calls=True,no_gpu_submission=True))
def contracts(out):
    test=D/"test_formal13260_terminal.py"
    sp=importlib.util.spec_from_file_location("formal13260_terminal_tests",test);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    suite=unittest.defaultTestLoader.loadTestsFromModule(m)
    need(suite.countTestCases()==34,"Expected34 meaningful wrapper contracts")
    with(out/"contracts.txt").open("x")as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
    report=write(out/"contracts.json",dict(status="PASS"if result.wasSuccessful()else"FAIL",tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),
        source=rec(SELF),tests=rec(test),log=rec(out/"contracts.txt"),scientific_results=False))
    need(result.wasSuccessful(),"CPU wrapper contracts failed; no collect")
    return report
def first_initial(plan,policy,submit,out,res,ind):
    p=RUNROOT/"13260_0/initial.json";initial=read(p)
    need(initial["task"]==plan["tasks"][0]and initial["plan"]==PINS["plan"],"First task exact source identity differs")
    need(initial["allocation_key"]=="13260_0"and initial["raw_allocation_id"]=="13261","First actual raw/logical allocation differs")
    sched=verify(initial["scheduler_start"],readonly=False).read_text()
    raw=res.running_allocation(sched,"13260_0",3,1);_,fields,_=res.selected(sched,"13260_0")
    need(fields["Command"]==PINS["launcher"]["path"]and fields["ArrayJobId"]==ARRAY and fields["ArrayTaskId"]=="0","First actual launcher/master/index differs")
    stamp=datetime.datetime.fromisoformat(raw["start"]).timestamp()
    need(stamp>=int(policy["created_at_epoch"])and stamp>=int(submit["submitted_at_epoch"]),"First generation predates policy/submission (Slurm integer-second resolution)")
    need(stamp==initial["allocation_started_at_epoch"],"Initial preserved epoch differs from SlurmStart")
    wrapped=dict(initial,initial_receipt=rec(p))
    # Reuse accepted independent v4 ownership reconstruction with initial as its own preserved receipt.
    ind.audit_gpu_ownership(wrapped,plan["protocol"]);identity=ind.allocation_identity(wrapped)
    need(identity["raw_allocation_id"]==raw["raw_allocation_id"],"Independent physical allocation ID differs")
    memory=res.memory_record(fields,raw["allocated_tres"])
    return write(out/"first_allocation.json",dict(status="FIRST_FORMAL_ALLOCATION_INITIAL_RUNNING_CPU3_GPU1_OWNERSHIP_AND_TIME_CPU_VERIFIED_NOT_CONTENT_REVIEWED",
      initial_receipt=rec(p),scheduler=initial["scheduler_start"],allocation=raw,identity=identity,hardware=initial["hardware"],
      policy=PINS["policy"],submit_receipt=rec(SUBMIT),memory=memory,cgroup_cpu_isolation_status="UNOBSERVED",
      no_sequence_stream_read=True,no_cohort_selection=True,actual_terminal_budget_acceptance=False))
def snapshot_pin_readonly(key):
    # AcceptedV2 scientific input receipts are exact-byte authorities, not source snapshots.
    # Do not chmod them or demand a new readonly rule after formal generation began.
    return key not in {"msa","previous_registry"}
def checks_and_seal(out,res,ind):
    verified={key:rec(verify(value))for key,value in PINS.items()}
    snap=read(PINS["entry_snapshot"]["path"])
    need(snap["schema"]=="formal_postprocess_source.v2"and snap["entry"]==PINS["entry"],"FrozenV2 source snapshot differs")
    for r in snap["files"]:verify(r)
    for key,r in snap["source_pins"].items():verify(r,readonly=snapshot_pin_readonly(key))
    plan=read(PINS["plan"]["path"]);protocol=read(PINS["protocol"]["path"]);policy=read(PINS["policy"]["path"])
    need(plan["protocol"]==protocol and plan["protocol_receipt"]==PINS["protocol"],"Actual plan/protocol authority differs")
    need(len(plan["tasks"])==28 and [x["array_index"]for x in plan["tasks"]]==list(range(28)),"Full28 array task definitions required")
    need(len({x["task_id"]for x in plan["tasks"]})==28,"Duplicate formal task identities")
    res.formal_policy(policy)
    need(policy["plan"]==PINS["plan"]and policy["protocol"]==PINS["protocol"]and policy["launcher"]==PINS["launcher"],"Actual policy pins differ")
    need(policy["sequence_universe"]==res.sequence_universe(protocol),"Frozen MPNN-only scope differs")
    need(Path(PINS["launcher"]["path"]).read_text()==Path(PINS["original_launcher"]["path"]).read_text().replace("#SBATCH --cpus-per-task=4","#SBATCH --cpus-per-task=3",1),"Undeclared launcher byte changes")
    pre=read(PINS["pregeneration"]["path"]);seeded=read(PINS["seeded"]["path"])
    need(pre["status"]=="INDEPENDENT_FORMAL28_READONLY_AUTHORITY_CURRENT_SEEDED_GATE_AND_SHARED_CPU3_PRE_GENERATION_AUDIT_PASS","Pregeneration gate notPASS")
    need(seeded["status"]=="INDEPENDENT_CURRENT_SEEDED_SUPPLEMENTAL_BUDGET_OWNERSHIP_RAW_CONTENT_AND_RNG_AUDIT_PASS","Current corrected supplemental independent gate notPASS")
    need(SUBMIT.is_file()and not SUBMIT.is_symlink()and not(SUBMIT.stat().st_mode&0o222),"Root submission must already be immutable")
    submit=read(SUBMIT);check_submit(submit,policy["created_at_epoch"])
    first=first_initial(plan,policy,submit,out,res,ind)
    seal=out/"seal";seal.mkdir()
    submission=rec(SUBMIT)
    listed=write(seal/"submit_receipts.json",[submission],readonly=True)
    result=write(seal/"acceptance.json",dict(schema="formal_submission_cpu_seal.v1",status="IMMUTABLE_ROOT13260_SUBMISSION_AND_FIXED_SOURCE_INPUTS_CPU_SEALED",
      submit_receipts_list=listed,submission_receipts=[submission],fixed_pins=verified,first_allocation=first,
      cpu_allocation=res.cpu_guard(),only_primary13260=True,all_technical_reruns_require_separate_review=True,
      no_predictions=True,no_sequence_selection=True,no_gpu_submission=True,experimental_evidence=False),readonly=True)
    seal.chmod(0o555)
    return listed,result
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("mode",choices=["collect","contracts-only"])
    ap.add_argument("--collection-out",default=str(R/"steps/24_benchmark_delivery/runs/formal_collection_13260"))
    args=ap.parse_args();check_env(os.environ,Path.cwd())
    res=module("terminal_resource",PINS["resource"]);cpu=res.cpu_guard()
    out=R/"steps/22_matched_benchmark"/("formal_terminal13260_cpu"+os.environ["SLURM_JOB_ID"])
    out.mkdir(exist_ok=False);step="bootstrap"
    try:
        source=source_bootstrap(out);step="contracts";ct=contracts(out)
        if args.mode=="contracts-only":
            write(out/"acceptance.json",dict(status="CPU34_WRAPPER_CONTRACTS_AND_BOOTSTRAP_SOURCE_SEALED_NO_COLLECTION",source=source,contracts=ct,cpu_allocation=cpu,no_gpu_submission=True))
            readonly_tree(out);return
        step="fixed_inputs_and_submission_seal";ind=module("terminal_independent",PINS["independent"])
        listed,sealed=checks_and_seal(out,res,ind)
        step="terminal_scheduler_only"
        sq=command(["squeue","-h","-j",ARRAY,"-o","%i|%T"],out/"squeue")
        need(sq["returncode"]==0,"squeue failed; no terminal status authority")
        sa=command(["sacct","-X","-j",ARRAY,"--noheader","--parsable2","--format=JobIDRaw,ElapsedRaw,AllocTRES,State,Start,End,NodeList,Partition"],out/"sacct")
        need(sa["returncode"]==0,"sacct failed; no terminal status authority")
        rows,excluded=res.accounting_rows(Path(sa["stdout"]["path"]).read_text())
        check_terminal(rows,Path(sq["stdout"]["path"]).read_text())
        write(out/"terminal_scheduler.json",dict(status="FORMAL_ARRAY_TERMINAL_NO_SELECTION_YET",array_job_id=ARRAY,rows=list(rows.values()),excluded_step_rows=excluded,sacct=sa,squeue=sq))
        target=Path(args.collection_out).resolve();target.relative_to(R/"steps/24_benchmark_delivery/runs")
        need(not target.exists(),"Never overwrite an existing V2 collection")
        argv=[str(CORE),PINS["entry"]["path"],"collect","--plan",PINS["plan"]["path"],"--plan-sha256",PINS["plan"]["sha256"],
          "--array-job-id",ARRAY,"--run-root",str(RUNROOT),"--resource-policy",PINS["policy"]["path"],"--policy-sha256",PINS["policy"]["sha256"],
          "--submit-receipts",listed["path"],"--submit-receipts-sha256",listed["sha256"],"--out",str(target)]
        # Recheck bytes immediately before executing the accepted entry. No eval/import of mutable adapters.
        for key in PINS:verify(PINS[key])
        step="immutable_V2_collect";execution=command(argv,out/"collect_v2",dict(os.environ))
        need(execution["returncode"]==0,"AcceptedV2 collect returned typed incomplete/nonzero; root must inspect exact preserved output")
        final=read(target/"acceptance.json")
        need(final["status"]=="FORMAL_ALLOCATION_NATIVE_AND_COHORT_CLOSURE_ACCEPTED","V2 acceptance status missing")
        need(final["array_job_id"]==ARRAY and final["plan"]==PINS["plan"]and final["resource_policy"]==PINS["policy"]and final["submit_receipts_list"]==listed,"V2 identity differs from sealed invocation")
        write(out/"acceptance.json",dict(schema="formal13260_terminal_wrapper.v1",status="FORMAL13260_TERMINAL_V2_COLLECTION_CPU_ACCEPTED_ROOT_COMMON_PREPARATION_PENDING",
          source=source,contracts=ct,submission_seal=sealed,submit_receipts_list=listed,collection=rec(target/"acceptance.json"),collect_execution=execution,
          cpu_allocation=cpu,no_new_predictions=True,no_gpu_submission=True,common_review_not_inferred=True,workflow_superiority=False))
        readonly_tree(out)
    except Exception as e:
        write(out/"typed_incomplete.json",dict(schema="formal13260_terminal_incomplete.v1",status="CPU_WRAPPER_TYPED_INCOMPLETE_NO_PROMOTION",
          failed_stage=step,reason_type=type(e).__name__,reason=str(e),cpu_allocation=cpu,no_gpu_submission=True,
          no_workflow_superiority_claim=True,partial_artifacts_retained=True))
        readonly_tree(out);raise
if __name__=="__main__":main()

