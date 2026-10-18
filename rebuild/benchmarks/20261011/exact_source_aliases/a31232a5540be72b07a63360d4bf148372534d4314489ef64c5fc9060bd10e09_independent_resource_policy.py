#!/usr/bin/env python3
"""Independent Slurm CPU/GPU allocation checks. CPU audit only; no scheduler mutation."""
import argparse,datetime,hashlib,json,os,re,subprocess,time
from pathlib import Path
TERMINAL={"COMPLETED","FAILED","CANCELLED","TIMEOUT","OUT_OF_MEMORY","NODE_FAIL","PREEMPTED","BOOT_FAIL"}
def need(ok,message):
    if not ok:raise ValueError(message)
def rec(path):
    p=Path(path).resolve();h=hashlib.sha256()
    with p.open("rb")as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return {"path":str(p),"bytes":p.stat().st_size,"sha256":h.hexdigest()}
def verify(r,readonly=False):
    need(rec(r["path"])==r,"Receipt mismatch: "+r["path"])
    p=Path(r["path"]);need(not readonly or not p.stat().st_mode&0o222,"Frozen file is writable")
    return p
def read(p):return json.loads(Path(p).read_text())
def gpu_count(tres):
    generic=[];typed=[]
    for key,n in re.findall(r"(?:^|,)(gres/gpu(?::[^,=]+)?)=(\d+)(?=,|$)",tres):
        (generic if key=="gres/gpu"else typed).append(int(n))
    need(len(generic)<=1,"Duplicate generic GPU TRES")
    need(not generic or not typed or generic[0]==sum(typed),"Typed/generic GPU counts differ")
    return generic[0]if generic else sum(typed)
def cpu_count(tres):
    found=re.findall(r"(?:^|,)cpu=(\d+)(?=,|$)",tres)
    need(len(found)==1,"Unique actual cpu TRES required");return int(found[0])
def records(text):
    result=[]
    for line in text.splitlines():
        if not line.strip():continue
        fields={}
        for match in re.finditer(r"(?:^|\s)([A-Za-z][A-Za-z0-9_:/-]*)=(\S*)",line):
            key,value=match.groups();need(key not in fields,"Repeated scheduler field");fields[key]=value
        need(fields.get("JobId","").isdigit(),"Unique numeric scheduler JobId required")
        result.append((line.strip()+"\n",fields))
    return result
def selected(text,key):
    matches=[]
    for line,f in records(text):
        raw=f["JobId"];a=f.get("ArrayJobId");i=f.get("ArrayTaskId")
        need(bool(a)==bool(i),"Partial array identity")
        logical=a+"_"+i if a else raw
        if str(key)in(raw,logical):matches.append((line,f,logical))
    need(len(matches)==1,"Unique selected raw/logical scheduler record required")
    return matches[0]
def running_allocation(text,key,cpus,gpus):
    line,f,logical=selected(text,key);need(f.get("JobState")=="RUNNING","Selected allocation is not RUNNING")
    tres=f.get("AllocTRES",f.get("TRES"));need(tres is not None,"Actual allocated TRES required")
    need(cpu_count(tres)==cpus and gpu_count(tres)==gpus,"Actual CPU/GPU allocation differs")
    need(int(f["NumCPUs"])==cpus and int(f["CPUs/Task"])==cpus,"Actual CPU scheduler fields differ")
    return {"selected_record":line,"raw_allocation_id":f["JobId"],"logical_allocation_key":logical,"allocated_tres":tres,"cpus":cpus,"gpus":gpus,"start":f["StartTime"],"node":f["NodeList"],"partition":f["Partition"]}
def accounting_rows(text):
    result={};excluded=[]
    for line in text.splitlines():
        if not line.strip():continue
        cells=line.split("|")
        if cells[-1]=="":cells.pop()
        if cells[0]=="JobIDRaw":continue
        need(len(cells)in(8,9),"Expected8/9 sacct fields")
        if len(cells)==8:raw,elapsed,tres,state,start,end,node,partition=cells;alias=None
        else:raw,alias,elapsed,tres,state,start,end,node,partition=cells
        if "."in raw or "["in raw or(alias and("."in alias or"["in alias)):
            excluded.append(raw);continue
        need(raw.isdigit()and(alias is None or re.fullmatch(r"\d+(?:_\d+)?",alias)),"Invalid physical allocation identity")
        need(raw not in result,"Repeated physical allocation (master/alias double count)")
        need(int(elapsed)>=0,"Negative allocation duration")
        result[raw]={"raw_allocation_id":raw,"job_id_alias":alias,"elapsed_seconds":int(elapsed),"allocated_tres":tres,"gpu_count":gpu_count(tres),"state":state.split()[0],"start":start,"end":end,"node":node,"partition":partition}
    return result,excluded
def terminal_allocation(row,key,cpus,gpus,max_seconds=3602):
    need(row["raw_allocation_id"]==str(key),"Physical actual allocation ID differs")
    need(row["state"]in TERMINAL,"Final allocated resource accounting required")
    need(row["gpu_count"]==gpus and cpu_count(row["allocated_tres"])==cpus,"Terminal actual CPU/GPU differs")
    need(0<row["elapsed_seconds"]<=max_seconds,"Positive allocation exceeds hard budget or missing duration")
    need(row["start"]not in("None","Unknown","")and row["end"]not in("None","Unknown",""),"Positive allocation missing terminal timestamps")
    return dict(row,allocated_gpu_seconds=row["elapsed_seconds"]*gpus,allocated_cpu_seconds=row["elapsed_seconds"]*cpus)
def cancelled_zero(row,key):
    need(row["raw_allocation_id"]==str(key)and row["state"]=="CANCELLED","Expected cancelled pending allocation")
    need(row["elapsed_seconds"]==0 and row["gpu_count"]==0 and row["allocated_tres"]=="","Cancelled allocation actually consumed resources")
    need(row["start"]in("None","Unknown",""),"Cancelled job actually started")
    return dict(row,allocated_gpu_seconds=0,allocated_cpu_seconds=0)
def formal_policy(policy):
    exact={"schema":"paired_formal_resource_policy.v1","scope":"ALL28_FORMAL_GENERATION_TASKS_AND_ALL_TECHNICAL_RERUNS",
      "expected_task_count":28,"cpus_per_task":3,"gpu_count":1,"memory_request_gib":64,"omp_num_threads_literal":4,
      "openblas_num_threads_literal":1,"gpu_name":"NVIDIA A100-PCIE-40GB","minimum_gpu_memory_mib":40000,
      "actual_allocation_required":True,"hardware_changes_allowed":False,"arm_specific_resource_overrides_allowed":False}
    for key,value in exact.items():need(policy.get(key)==value,"Frozen shared resource policy differs: "+key)
    return policy
def freeze_resource_policy(plan_path,original_launcher,output_dir):
    allocation=cpu_guard();plan_path=Path(plan_path).resolve();original_launcher=Path(original_launcher).resolve()
    plan=read(plan_path);protocol=plan["protocol"]
    need(len(plan["tasks"])==28 and protocol["gpu_count"]==1 and protocol["budget_gpu_seconds"]==3600,"Formal full28 budget required")
    need(protocol["binder_length"]==65 and protocol["replicate_seeds"]==[21011,21012],"Formal science fields differ")
    need(not plan_path.stat().st_mode&0o222 and not original_launcher.stat().st_mode&0o222,"Original plan/launcher must be readonly")
    protocol_receipt=plan["protocol_receipt"];verify(protocol_receipt,True);need(read(protocol_receipt["path"])==protocol,"Embedded/original protocol differs")
    original=original_launcher.read_text();need(original.count("#SBATCH --cpus-per-task=4")==1,"Original launcher CPU4 single directive required")
    need("OMP_NUM_THREADS=4"in original and "#SBATCH --mem=64G"in original and "#SBATCH --gres=gpu:1"in original,"Frozen unchanged threads/memory/GPU required")
    need(str(plan_path)in original and rec(plan_path)["sha256"]in original,"Original launcher must pin exact formal plan/hash")
    D=Path(output_dir).resolve();need(not D.exists(),"Do not overwrite a frozen policy")
    D.mkdir(parents=True);launcher=D/"formal_generation_cpu3.sbatch"
    launcher.write_text(original.replace("#SBATCH --cpus-per-task=4","#SBATCH --cpus-per-task=3",1));launcher.chmod(0o444)
    policy={"schema":"paired_formal_resource_policy.v1","scope":"ALL28_FORMAL_GENERATION_TASKS_AND_ALL_TECHNICAL_RERUNS",
      "expected_task_count":28,"cpus_per_task":3,"gpu_count":1,"memory_request_gib":64,"omp_num_threads_literal":4,
      "openblas_num_threads_literal":1,"gpu_name":"NVIDIA A100-PCIE-40GB","minimum_gpu_memory_mib":40000,
      "actual_allocation_required":True,"hardware_changes_allowed":False,"arm_specific_resource_overrides_allowed":False,
      "created_at_epoch":time.time(),"plan":rec(plan_path),"protocol":protocol_receipt,
      "original_launcher":rec(original_launcher),"launcher":rec(launcher),"source":rec(__file__),
      "original_launcher_execution_status":"AUDITED_NOT_EXECUTED","cpu_allocation":allocation,
      "amendment":"Only SBATCH cpus-per-task4->3; exact original science/config/seed/default calls/hardware/GPU budget unchanged",
      "cpu_bottleneck_possible":True,"memory_observation_policy":"Require64G scheduler MinMemory; AllocTRES mem if present reported; absent memory TRES is UNAVAILABLE, never zero"}
    formal_policy(policy);pp=D/"resource_policy.json";pp.write_text(json.dumps(policy,indent=2,sort_keys=True)+"\n");pp.chmod(0o444)
    receipt={"status":"SHARED_CPU3_POLICY_FROZEN_BEFORE_GENERATION_NOT_GPU_EXECUTED","policy":rec(pp),"launcher":rec(launcher),"source":rec(__file__),"cpu_allocation":allocation}
    rp=D/"freeze_receipt.json";rp.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n");rp.chmod(0o444);D.chmod(0o555)
    return receipt
def memory_gib(text):
    match=re.fullmatch(r"(\d+(?:\.\d+)?)([KMGT]?)",text);need(match is not None,"Unknown actual/request memory units")
    return float(match[1])*{"":1/1024/1024/1024,"K":1/1024/1024,"M":1/1024,"G":1,"T":1024}[match[2]]
def memory_record(fields,tres):
    requested=fields.get("MinMemoryNode",fields.get("MinMemoryCPU"));need(requested is not None,"Required scheduler memory64G is missing")
    # A per-CPU memory request is scaled by actual NumCPUs; node-level64G remains unchanged.
    requested_gib=memory_gib(requested)*(int(fields["NumCPUs"])if"MinMemoryNode"not in fields else 1)
    need(requested_gib==64,"Shared64G memory request differs")
    mem=re.findall(r"(?:^|,)mem=([^,]+)",tres);need(len(mem)<=1,"Duplicate actual memory TRES")
    actual=memory_gib(mem[0])if mem else None
    need(actual is None or actual>=64,"Actual allocated memory smaller than64G")
    return {"requested_memory_gib":64,"actual_allocated_memory_gib":actual,"actual_memory_status":"OBSERVED_ALLOC_TRES"if mem else"UNAVAILABLE_NOT_ZERO"}
def formal_resources(policy_path,run_receipts,sacct_text,submit_receipts,require_all28=True):
    policy_receipt=rec(policy_path);policy=read(verify(policy_receipt,True));formal_policy(policy)
    plan=read(verify(policy["plan"],True));need(plan["protocol_receipt"]==policy["protocol"],"Policy exact protocol differs");verify(policy["protocol"],True)
    launcher=verify(policy["launcher"],True).read_text();original=verify(policy["original_launcher"],True).read_text()
    need(launcher==original.replace("#SBATCH --cpus-per-task=4","#SBATCH --cpus-per-task=3",1),"Only declared launcherCPU directive may change")
    submitted_masters=set()
    for receipt in submit_receipts:
        submit=read(verify(receipt,True));need(submit["launcher"]==policy["launcher"]and submit["resource_policy"]==policy_receipt and submit["plan"]==policy["plan"],"Submit exact policy/plan/launcher differs")
        argv=submit["submit_argv"];need(argv[:2]==["sbatch","--parsable"]and argv[-1]==policy["launcher"]["path"],"Wrong launch command")
        need(all(not x.startswith(("--cpus","--gres","--mem","--partition","--qos","--account","--time"))for x in argv[2:-1]),"Undeclared resourceCLI override")
        jid=str(submit["job_id"]);need(jid.isdigit()and jid not in submitted_masters,"Unique submitted master ID required");submitted_masters.add(jid)
    need(submitted_masters,"Every actual allocation needs predeclared submitted master")
    rows,excluded=accounting_rows(sacct_text);task_ids={t["task_id"]for t in plan["tasks"]};need(len(task_ids)==28,"Exact28 frozen tasks required")
    counts={t:0 for t in task_ids};seen=set();checked=[]
    for receipt in run_receipts:
        run=read(verify(receipt));tid=run["task"]["task_id"];need(tid in task_ids and run["plan"]==policy["plan"],"Unknown/unfrozen task or plan")
        rawtext=verify(run["scheduler_start"]).read_text();raw=running_allocation(rawtext,run["allocation_key"],3,1);_,fields,_=selected(rawtext,run["allocation_key"])
        jid=raw["raw_allocation_id"];master=fields.get("ArrayJobId",jid)
        need(master in submitted_masters and fields.get("Command")==policy["launcher"]["path"],"Allocation command/master not frozen")
        need(jid not in seen,"Physical allocation repeated across task runs");seen.add(jid)
        need(datetime.datetime.fromisoformat(raw["start"]).timestamp()>=policy["created_at_epoch"],"GPU generation predates frozen resource policy")
        need(jid in rows,"Missing actual terminal accounting")
        final=terminal_allocation(rows[jid],jid,3,1)
        need(raw["start"]==final["start"]and raw["node"]==final["node"],"Start/node differs")
        memory=memory_record(fields,raw["allocated_tres"])
        if re.search(r"(?:^|,)mem=",final["allocated_tres"]):need(memory_gib(re.search(r"(?:^|,)mem=([^,]+)",final["allocated_tres"])[1])>=64,"Terminal actual memory smaller than64G")
        need(len(run["hardware"]["gpus"])==1 and run["hardware"]["gpus"][0]["name"]==policy["gpu_name"]and run["hardware"]["gpus"][0]["memory_total_mib"]>=40000,"Hardware differs")
        counts[tid]+=1;checked.append(dict(final,task_id=tid,run_receipt=receipt,memory=memory))
    positive={key for key,row in rows.items()if row["gpu_count"]>0}
    need(positive==seen,"Unrecorded positive allocation/attempt excluded from shared-resource denominator")
    need(not require_all28 or all(counts.values()),"Resource gate cannot omit frozen tasks")
    return {"status":"ALL28_AND_ALL_RECORDED_RERUNS_SHARED_RESOURCES_CPU_AUDITED"if require_all28 else"PARTIAL_SHARED_RESOURCE_AUDIT_NOT_FULL_MATRIX",
      "policy":policy_receipt,"task_count":sum(bool(n)for n in counts.values()),"allocation_count":len(checked),"allocations":checked,
      "cpu_count":3,"gpu_count":1,"omp_num_threads_literal":4,"cpu_bottleneck_possible":True,"excluded_step_rows":excluded,"run_receipts_input":run_receipts,"submit_receipts_input":submit_receipts}
def cpu_guard():
    need(os.environ.get("CUDA_VISIBLE_DEVICES","")in("","-1","NoDevFiles"),"CPU audit must disable CUDA")
    jid=os.environ.get("SLURM_JOB_ID");need(jid is not None,"Slurm CPU allocation required")
    raw=subprocess.check_output(["scontrol","show","job","-o",jid],text=True);line,f,logical=selected(raw,jid)
    need(f.get("JobState")=="RUNNING","CPU audit requires RUNNING")
    tres=f.get("AllocTRES",f.get("TRES"));need(tres is not None and gpu_count(tres)==0,"CPU audit actually allocated GPU")
    return {"job_id":jid,"scheduler_record_full":raw,"selected_scheduler_record":line,"actual_allocated_tres":tres,"allocated_gpu_count":0}

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest="command",required=True)
    p=sub.add_parser("freeze");p.add_argument("--plan",required=True);p.add_argument("--original-launcher",required=True);p.add_argument("--output-dir",required=True)
    p=sub.add_parser("audit");p.add_argument("--policy",required=True);p.add_argument("--run-receipts",required=True);p.add_argument("--sacct",required=True);p.add_argument("--submit-receipts",required=True);p.add_argument("--output-dir",required=True)
    a=ap.parse_args()
    if a.command=="freeze":report=freeze_resource_policy(a.plan,a.original_launcher,a.output_dir)
    else:
        allocation=cpu_guard();report=formal_resources(a.policy,read(a.run_receipts),Path(a.sacct).read_text(),read(a.submit_receipts))
        report["cpu_allocation"]=allocation;report["source"]=rec(__file__);D=Path(a.output_dir);need(not D.exists(),"Do not overwrite audit");D.mkdir(parents=True)
        (D/"acceptance.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report))
if __name__=="__main__":main()

