#!/usr/bin/env python3
"""CPU-only independent current root GPU submission-universe and cost closure."""
import argparse,datetime,hashlib,importlib.util,json,math,os,re,shutil,subprocess,sys,unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
USER="u21111210118"
PRIMARY_START="2026-10-11T14:25:00Z"
FORMAL_PLAN=dict(path=str(R/"steps/22_matched_benchmark/formal_freeze_13257/plan/frozen_plan.json"),bytes=20295,sha256="e913d1bbccd531bf88a73f6ba60e8a0de85bb03ad8bcd3455d8952ca4effe0b6")
POLICY=dict(path=str(R/"steps/22_matched_benchmark/formal_launchpolicy_13259/resource_policy.json"),bytes=6712,sha256="a996cac084eb6630dc4c34a62b581f2bf298d5d720350f4f702476adb8df073e")
FORMAL_SUB=R/"steps/22_matched_benchmark/formal_submission_13260/submit_receipt.json"
FILES=("root_gpu_cost_audit.py","test_root_gpu_cost_audit.py","root_gpu_cost_cpu.sbatch","HANDOFF.md")
CONTRACT_COUNT=88
SOFTWARE_SCHEMA="root-gpu-cost-software.v3"
ACCEPTED="ROOT_CURRENT_GPU_SUBMISSION_UNIVERSE_AND_TERMINAL_COST_CPU_ACCEPTED"
SOFTWARE="ROOT_GPU_COST_AUDITOR_SOFTWARE_CPU_ACCEPTED"
SCOPE_NAME=re.compile(r"^(?:test9_.*|ppi_formal_common.*)$")
FIELDS="JobID,JobIDRaw,JobName%256,User%64,Account%64,State,ElapsedRaw,AllocTRES,Submit,Start,End,NodeList,Partition,WorkDir%1024"
TERMINAL={"COMPLETED","FAILED","CANCELLED","TIMEOUT","OUT_OF_MEMORY","NODE_FAIL","PREEMPTED","BOOT_FAIL","DEADLINE","REVOKED","SPECIAL_EXIT"}
def need(value,message):
 if not value:raise ValueError(message)
def utc(value):
 need(isinstance(value,str),"UTC timestamp string required")
 v=value.replace("Z","+00:00");d=datetime.datetime.fromisoformat(v)
 need(d.tzinfo is not None and d.utcoffset()==datetime.timedelta(0),"Explicit UTC timestamp required")
 return d.timestamp()
def accounting_epoch(value):
 need(value not in {"","Unknown","None","N/A"},"Actual allocated Start/End unavailable")
 d=datetime.datetime.fromisoformat(value.replace("Z","+00:00"))
 if d.tzinfo is None:d=d.replace(tzinfo=datetime.timezone.utc)
 return d.timestamp()
def shape(r):
 need(isinstance(r,dict)and {"path","bytes","sha256"}<=r.keys(),"Exact path/bytes/SHA receipt required")
 need(isinstance(r["path"],str)and Path(r["path"]).is_absolute(),"Absolute receipt path required")
 need(isinstance(r["bytes"],int)and not isinstance(r["bytes"],bool)and r["bytes"]>=0,"Integer byte count required")
 need(isinstance(r["sha256"],str)and re.fullmatch("[0-9a-f]{64}",r["sha256"])is not None,"Exact SHA256 required")
 return r
def path(p):
 p=Path(p);need(p.is_absolute()and p.is_relative_to(R)and p.resolve()==p,"Authority path/symlink mismatch");return p
def rec(p):
 p=path(p);h=hashlib.sha256()
 with p.open("rb")as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return dict(path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest())
def same(a,b):return a["path"]==b["path"]and a["bytes"]==b["bytes"]and a["sha256"]==b["sha256"]
def verify(r,readonly=False):
 shape(r);p=path(r["path"]);need(p.is_file()and same(rec(p),r),"Receipt byte drift: "+str(p))
 need(not readonly or not(p.stat().st_mode&0o222),"Readonly immutable receipt required");return p
def read(p):return json.loads(Path(p).read_text())
def dump(p,obj):
 p=path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("x")as f:json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
 p.chmod(0o444);return rec(p)
def select_cpu_record(text,jid):
 rows=[v for v in text.splitlines()if re.search(r"\bJobId="+re.escape(jid)+r"(?:\s|$)",v)]
 need(len(rows)==1,"Unique actual CPU scheduler record required")
 f=dict(re.findall(r"(\w+)=(\S*)",rows[0]));need(f.get("JobState")=="RUNNING","RUNNING CPU job required")
 need(f.get("NumCPUs","").isdigit()and int(f["NumCPUs"])>=1 and f.get("UserId","").startswith(USER+"(")and f.get("Account")==USER and f.get("Partition")=="organ","Actual CPU ownership/account/organ allocation required")
 representations=[]
 for name in ("TRES","AllocTRES"):
  if name not in f:continue
  need(f[name],"Empty actual CPU TRES representation forbidden");values={}
  for token in f[name].split(","):
   need("="in token,"Malformed actual CPU TRES representation");key,value=token.split("=",1);need(key not in values,"Duplicate actual CPU TRES field");values[key]=value
  need(values.get("cpu","").isdigit()and int(values["cpu"])==int(f["NumCPUs"]),"Actual allocated CPU count differs from NumCPUs")
  need(gpu_count(f[name])==0,"CPU helper has actual allocated GPU")
  representations.append((name,values))
 need(representations,"Missing actual allocated TRES/AllocTRES CPU evidence")
 if len(representations)==2:need(representations[0][1]==representations[1][1],"Old/new live CPU TRES representations disagree")
 return dict(job_id=jid,selected_scheduler_record=rows[0],allocated_GPUs=0,allocated_CPUs=int(f["NumCPUs"]),allocated_TRES_fields=[name for name,_ in representations],CPU_TRES_guard_scope="Live pureCPU helper only; terminal GPU missing AllocTRES remains UNAVAILABLE_NOT_ZERO")
def cpu():
 need(os.environ.get("SLURM_JOB_ID","").isdigit(),"Actual Slurm CPU allocation required")
 need(os.environ.get("CUDA_VISIBLE_DEVICES")==""and os.environ.get("JAX_PLATFORMS")=="cpu","Empty CUDA/JAXcpu required")
 need(os.environ.get("PYTHONNOUSERSITE")=="1"and os.environ.get("PYTHONDONTWRITEBYTECODE")=="1"and "PYTHONPATH"not in os.environ,"CPU import isolation required")
 need(os.environ.get("OPENBLAS_NUM_THREADS")=="1","CPU thread cap required")
 jid=os.environ["SLURM_JOB_ID"];text=subprocess.check_output(["scontrol","show","job",jid,"-o"],text=True)
 return select_cpu_record(text,jid)
def gpu_count(tres):
 e={}
 for token in tres.split(","):
  if "="in token:
   k,v=token.split("=",1);need(k not in e,"Duplicate allocated TRES key");e[k]=v
 generic=int(e["gres/gpu"])if"gres/gpu"in e else None
 typed_keys=[k for k in e if k.startswith("gres/gpu:")];typed=sum(int(e[k])for k in typed_keys)
 need((generic is None or generic>=0)and typed>=0,"Negative GPU allocation")
 if generic is not None and typed_keys:need(generic==typed,"Generic/typed GPU allocation differs")
 return typed if generic is None else generic
def parse_accounting(text):
 rows=[];excluded=[]
 for line in text.splitlines():
  if not line.strip():continue
  v=line.split("|");need(len(v)==14,"Expected14 explicit sacct fields")
  jid,raw,name,user,account,state,elapsed,tres,submit,start,end,node,partition,workdir=v
  if "."in jid:
   excluded.append(dict(logical_id=jid,raw_id=raw,reason="JOB_STEP_NOT_SEPARATE_GPU_ALLOCATION",raw_line=line));continue
  need(re.fullmatch(r"\d+",elapsed)is not None,"Numeric nonnegative ElapsedRaw required")
  state=state.split()[0].rstrip("+")
  count=gpu_count(tres)if any(x.split("=",1)[0].startswith("gres/gpu")for x in tres.split(","))else(0 if state=="CANCELLED"and int(elapsed)==0 and not tres and start in {"","Unknown","None","N/A"}else None)
  rows.append(dict(logical_id=jid,raw_id=raw,job_name=name,user=user,account=account,state=state,elapsed_seconds=int(elapsed),AllocTRES=tres,GPU_count=count,GPU_count_status="ACTUAL_GPU_TRES_COUNT"if count is not None else"UNAVAILABLE_NOT_ZERO",Submit=submit,Start=start,End=end,node=node,partition=partition,WorkDir=workdir,raw_line=line))
 return rows,excluded
def indices(v):
 need(isinstance(v,list)and v and all(isinstance(x,int)and not isinstance(x,bool)and x>=0 for x in v),"Nonempty explicit integer array indices required")
 need(v==sorted(set(v)),"Array indices must be unique ascending");return v
def base_argv(argv):
 need(isinstance(argv,list)and len(argv)>=3 and all(isinstance(x,str)for x in argv)and argv[:2]==["sbatch","--parsable"],"Exact root sbatch parsable argv required")
 return argv[2:]
def dependencies(tokens,controller,position=0):
 declared=controller.get("dependency")
 if declared is None:return tokens
 need(isinstance(declared,str)and re.fullmatch(r"after(?:any|ok):\d+(?:_\d+)?(?::\d+(?:_\d+)?)*",declared)is not None,"Unsupported declared dependency")
 need(len(tokens)>position and tokens[position]=="--dependency="+declared,"Exact declared dependency argv required")
 return tokens[:position]+tokens[position+1:]
def launcher_policy(text,phase=None,submission_workdir=None):
 values={}
 for key in ("job-name","gres","cpus-per-task","mem"):
  found=re.findall(r"^#SBATCH\s+--"+re.escape(key)+r"=(\S+)\s*$",text,re.M);need(len(found)==1,"One fixed launcher directive required: "+key);values[key]=found[0]
 need(values["gres"]=="gpu:1"and values["cpus-per-task"]=="3"and values["mem"]=="64G","CPU3/GPU1/64G policy changed")
 need(re.search(r"\bOMP_NUM_THREADS=4\b",text)is not None,"OMP4 literal required")
 dirs=re.findall(r"^#SBATCH\s+--chdir=(\S+)\s*$",text,re.M)
 if phase=="reference_free_e2e":
  need(not dirs and submission_workdir==str(R),"Only accepted legacy E2E missing-chdir launcher plus exact root WorkDir allowed")
  values["chdir"]=submission_workdir
 else:
  need(len(dirs)==1,"One fixed non-E2E launcher chdir required");values["chdir"]=dirs[0]
 need(Path(values["chdir"]).is_absolute()and Path(values["chdir"]).is_relative_to(R),"Launcher must bind exact project work directory")
 need(SCOPE_NAME.fullmatch(values["job-name"])is not None,"Launcher not within declared current test9 names")
 return values
def submission_contract(entry,controller,fetch,text):
 need(entry.get("phase")in {"formal_generation","common_review","reference_free_e2e"},"Unknown current GPU phase")
 need(entry.get("kind")in {"primary","technical_rerun"},"Submission identity kind required")
 launcher=shape(controller["launcher"]);policy=launcher_policy(text,entry["phase"],controller.get("submission_workdir"))
 argv=base_argv(controller["submit_argv"])
 phase=entry["phase"];stage=None;preflight=None
 argv=dependencies(argv,controller,1 if phase=="common_review"else 0)
 if phase=="formal_generation":
  need(controller.get("schema")in {"paired_formal_resource_submission.v1","paired_formal_resource_rerun_submission.v1"},"Wrong formal root receipt")
  need(controller["plan"]==FORMAL_PLAN and controller["resource_policy"]==POLICY,"Exact frozen current formal plan/policy required")
  frozen=fetch(FORMAL_PLAN);need(frozen.get("status")=="FROZEN_BEFORE_GENERATION"and len(frozen["tasks"])==28,"Actual frozen28 tasks required")
  job=str(controller["job_id"])
  if entry["kind"]=="primary":
   need(entry["receipt"]["path"]==str(FORMAL_SUB)and job=="13260"and controller["schema"]=="paired_formal_resource_submission.v1"and argv==[launcher["path"]],"Unique current formal13260 primary required")
   ix=list(range(28))
  else:
   ix=indices(controller["indices"]);need(set(ix)<=set(range(28)),"Unfrozen formal retry slot")
   need(controller["schema"]=="paired_formal_resource_rerun_submission.v1"and argv==["--array="+",".join(map(str,ix))+"%2",launcher["path"]],"Exact separate formal rerun indices/argv required")
 elif phase=="common_review":
  need(controller.get("schema")=="formal_common_root_submission.v1","Wrong common root receipt")
  preflight=shape(controller["preflight"]);pre=fetch(preflight)
  need(pre.get("status")=="COMMON_SUCCESSOR_CPU_PREFLIGHT_ACCEPTED_ROOT_PENDING_ONLY_GPU_SUBMISSION_REQUIRED","Actual accepted common CPU preflight required")
  need(pre.get("no_inference")is True and pre.get("root_submission_performed")is False,"Common CPU preflight evidence scope differs")
  ix=indices(controller["indices"]);need(ix==pre["root_pending_job_indices"]and controller["concurrency_cap"]==2,"Exact common pending-only indices/cap required")
  entry_source=next(x for x in pre["source"]["successor"]if Path(x["path"]).name=="common_review_successor.py")
  gpu_launcher=next(x for x in pre["source"]["successor"]if Path(x["path"]).name=="common_review_gpu.sbatch")
  need(controller["entry"]==entry_source and launcher==gpu_launcher,"Actual CPU-tested common source/launcher binding required")
  expected=["--export=ALL,COMMON_SUCCESSOR_ENTRY="+entry_source["path"],"--array="+",".join(map(str,ix))+"%2",launcher["path"],preflight["path"]]
  need(argv==expected,"Exact common argv/preflight/entry required; overrides forbidden")
  job=str(controller["array_job_id"])
 else:
  need(controller.get("schema")=="reference_free_root_model_submission.v1","Wrong E2E root GPU receipt")
  preflight=shape(controller["preflight_acceptance"]);pre=fetch(preflight)
  need(pre.get("status")=="CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED"and pre.get("GPU_allocated")==0 and pre["qualified_prediction"]["status"]=="POSE_ACCEPTED","Actual accepted physical source/pose required for model submission")
  need(controller["source_manifest"]==pre["source_manifest"],"E2E root source does not bind CPU qualification")
  snapshot=fetch(pre["source_manifest"]);records={Path(x["path"]).name:x for x in snapshot["files"]if Path(x["path"]).name in {"e2e_gpu_stage.sbatch","e2e_model_stage.py"}}
  need(launcher==records["e2e_gpu_stage.sbatch"]and controller["entry"]==records["e2e_model_stage.py"],"Accepted E2E source/launcher required")
  stage=controller["stage"];need(stage in {"design","evaluate"},"Unreviewed E2E stage")
  upstream=shape(controller["upstream"]);need(isinstance(controller.get("result_dir"),str),"Exact result directory required");path(controller["result_dir"])
  expected=["--chdir="+str(R),launcher["path"],stage,preflight["path"],upstream["path"],controller["result_dir"]]
  if stage=="design":need(upstream==pre["qualified_prediction"]["manifest"],"Design must consume exact qualified pose")
  else:
   dr=fetch(shape(controller["design_stage_result"]));da=fetch(shape(controller["design_audit_acceptance"]))
   need(dr.get("stage")=="design"and dr.get("status")=="ACTUAL_MODEL_STAGE_COMPLETE"and dr["result_manifest"]==upstream,"Evaluate must bind actual new design")
   need(da.get("status")=="REFERENCE_FREE_E2E_ACTUAL_DESIGN_CPU_CONTENT_ACCEPTED"and da["actual_design_manifest"]==upstream and da["actual_design_stage_result"]==controller["design_stage_result"],"Actual independent CPU design gate required")
   expected +=[controller["design_stage_result"]["path"],controller["design_audit_acceptance"]["path"]]
  need(argv==expected,"Exact E2E stage/upstream/result/source argv required; overrides forbidden")
  job=str(controller["job_id"]);ix=None
 need(re.fullmatch(r"\d+",job)is not None,"Actual numeric root submission ID required")
 need(isinstance(controller.get("raw_sbatch_stdout"),str)and controller["raw_sbatch_stdout"].strip()==job and not controller.get("raw_sbatch_stderr","").strip(),"Actual raw parsable submission differs/missing")
 return dict(submission_id=entry["submission_id"],phase=phase,kind=entry["kind"],job_id=job,indices=ix,stage=stage,preflight=preflight,launcher=launcher,job_name=policy["job-name"],WorkDir=policy["chdir"],expected_allocation_count=len(ix)if ix is not None else 1,rerun_of=entry.get("rerun_of"))
def ledger_contract(ledger):
 need(ledger.get("schema")=="root-current-gpu-submission-universe.v1"and ledger.get("authority_root")==str(R),"Exact current-root universe schema required")
 need(ledger.get("scope_start_utc")==PRIMARY_START,"Current phase start cannot omit formal13260")
 end=utc(ledger["scope_end_utc"]);need(end>=utc(PRIMARY_START),"Invalid current phase scope")
 entries=ledger.get("entries");need(isinstance(entries,list)and entries,"Actual root submission universe required")
 ids=[x.get("submission_id")for x in entries];need(all(isinstance(x,str)and x for x in ids)and len(ids)==len(set(ids)),"Duplicate/empty root submission identity")
 need(ledger.get("formal_array_job_id")=="13260"and ledger.get("global_current_scope_gpu_cap")==2,"Current formal/cap identity differs")
 seen={}
 for e in entries:
  shape(e["receipt"])
  if e.get("kind")=="technical_rerun":
   need(e.get("rerun_of")in seen and seen[e["rerun_of"]]["phase"]==e["phase"],"Rerun must bind earlier same-phase identity")
   need(e.get("scientific_results_merged")is False,"Technical rerun cannot silently merge evidence")
  else:need(e.get("rerun_of")is None,"Primary cannot refer to hidden predecessor")
  seen[e["submission_id"]]=e
 need(sum(e.get("phase")=="formal_generation"and e.get("kind")=="primary"for e in entries)==1,"One current formal primary required")
 need(ledger.get("e2e_disposition")in {"upstream_rejected","attempted"},"Explicit E2E terminal disposition required")
 shape(ledger["common_preflight"]);shape(ledger["physical_preflight"])
 return entries,end
def journal_contract(doc):
 need(doc.get("schema")=="root-current-gpu-submission-journal.v1"and doc.get("authority_root")==str(R)and doc.get("scope_start_utc")==PRIMARY_START,"Exact current root journal authority required")
 entries=doc.get("entries");need(isinstance(entries,list)and entries,"Actual explicit submitted journal entries required")
 seen={};paths=set()
 for e in entries:
  sid=e.get("submission_id");need(isinstance(sid,str)and sid and sid not in seen,"Unique actual journal submission identity required")
  need(e.get("phase")in {"formal_generation","common_review","reference_free_e2e"}and e.get("kind")in {"primary","technical_rerun"},"Journal phase/identity kind differs")
  need(isinstance(e.get("receipt_path"),str)and Path(e["receipt_path"]).is_absolute()and Path(e["receipt_path"]).is_relative_to(R),"Explicit root metadata receipt path required")
  need(e["receipt_path"]not in paths,"Root receipt reused under different submission identities");paths.add(e["receipt_path"])
  if e["kind"]=="technical_rerun":
   need(e.get("rerun_of")in seen and seen[e["rerun_of"]]["phase"]==e["phase"]and e.get("scientific_results_merged")is False,"Journal technical repair ancestor/merge differs")
  else:need(e.get("rerun_of")is None,"Journal primary hidden predecessor")
  seen[sid]=e
 need(sum(e["phase"]=="formal_generation"and e["kind"]=="primary"and e["receipt_path"]==str(FORMAL_SUB)for e in entries)==1,"Journal must retain actual formal13260 primary")
 return entries
def journal_prefix(previous,current):
 journal_contract(previous);journal_contract(current)
 need(current["entries"][:len(previous["entries"])]==previous["entries"],"Append-only journal dropped or rewrote root submission")
def journal_chain(p):
 chain=[];seen=set();current=path(p)
 while True:
  need(str(current)not in seen and len(seen)<10000,"Journal predecessor cycle/ambiguous chain")
  seen.add(str(current));rr=rec(current);doc=read(verify(rr,True));journal_contract(doc);chain.append((rr,doc))
  prior=doc.get("previous_journal_path")
  if prior is None:break
  current=path(prior)
 chain.reverse()
 for (_,a),(_,b)in zip(chain,chain[1:]):journal_prefix(a,b)
 return chain
def software_contract(sw,ct,source):
 need(sw.get("schema")==SOFTWARE_SCHEMA and sw.get("status")==SOFTWARE and sw["source"]==source,"Exact current V3 cost software/source required")
 need(ct.get("status")=="PASS"and type(ct.get("tests_run"))is int and ct["tests_run"]==CONTRACT_COUNT and all(type(ct.get(k))is int and ct[k]==0 for k in ("failures","errors","skipped")),"Actual all88 V3 contracts without failures/errors/skips required")
 need(ct.get("tested_source")==source,"Contracts executed exact frozen V3 source4")
 for key in ("original_owned_pre_and_post_byte_readback_PASS","original_and_frozen_owned_byte_identities_equal","all_owned_python_compile_PASS","all_launchers_bash_syntax_PASS"):
  need(sw.get(key)is True,"V3 source execution qualification required: "+key)
 need(sw["entry"]==source[0]and sw["CPU_launcher"]==source[2],"Current accepted entry/CPU launcher exact source bindings")
 return source
def software_ready(descriptor):
 source=frozen_sources();sw=read(verify(descriptor,True));ct=read(verify(sw["contracts"],True))
 software_contract(sw,ct,source);verify(ct["log"],True)
 original_source_binding(sw["original_source"],source,Path(sw["original_source"][0]["path"]).parent,Path(source[0]["path"]).parent)
 need(source_metadata(Path(sw["original_source"][0]["path"]).parent)==sw["original_source_metadata_before"]==sw["original_source_metadata_after"],"Original reviewed source4 metadata remained unchanged")
 return source
def seal_ledger(args,out):
 allocation=cpu();source=software_ready(args.software_acceptance);chain=journal_chain(args.journal)
 end=utc(args.scope_end_utc);need(utc(PRIMARY_START)<=end<=datetime.datetime.now(datetime.timezone.utc).timestamp(),"Actual terminal UTC ledger bound required")
 entries=[];controllers=[]
 for e in chain[-1][1]["entries"]:
  rr=rec(e["receipt_path"]);controller=read(verify(rr,True));jid=str(controller.get("job_id",controller.get("array_job_id","")))
  need(re.fullmatch(r"\d+",jid)is not None and controller.get("raw_sbatch_stdout","").strip()==jid,"Actual immutable journal raw submission ID required")
  entries.append({**{k:v for k,v in e.items()if k!="receipt_path"},"receipt":rr});controllers.append(rr)
 common=rec(args.common_preflight);physical=rec(args.physical_preflight);verify(common,True);verify(physical,True)
 closure=dump(out/"root_submission_journal_closure.json",dict(schema="root-submission-journal-CPU-closure.v1",status="ROOT_SUBMISSION_JOURNAL_CHAIN_CPU_SEALED",journal_receipts=[r for r,_ in chain],final_journal=chain[-1][0],entries=entries,controller_receipts=controllers,root_no_new_source_hash_on_login=True,allocation=allocation))
 ledger=dict(schema="root-current-gpu-submission-universe.v1",authority_root=str(R),scope_start_utc=PRIMARY_START,scope_end_utc=args.scope_end_utc,formal_array_job_id="13260",global_current_scope_gpu_cap=2,entries=entries,common_preflight=common,physical_preflight=physical,e2e_disposition=args.e2e_disposition,journal_closure=closure)
 ledger_contract(ledger);lr=dump(out/"root_gpu_submission_ledger.json",ledger)
 return dump(out/"acceptance.json",dict(status="ROOT_GPU_SUBMISSION_JOURNAL_LEDGER_CPU_SEALED",ledger=lr,journal_closure=closure,source=source,software_acceptance=args.software_acceptance,allocation=allocation,terminal_cost_not_yet_accepted=True,no_GPU_submission=True))
def verify_journal_ledger(ledger):
 closure=read(verify(shape(ledger["journal_closure"]),True));need(closure.get("status")=="ROOT_SUBMISSION_JOURNAL_CHAIN_CPU_SEALED","Actual pureCPU journal closure required")
 chain=journal_chain(closure["final_journal"]["path"])
 need([r for r,_ in chain]==closure["journal_receipts"]and chain[-1][0]==closure["final_journal"],"Root journal history byte identities drifted")
 entries=[{**{k:v for k,v in e.items()if k!="receipt_path"},"receipt":rec(verify(rec(e["receipt_path"]),True))}for e in chain[-1][1]["entries"]]
 need(entries==ledger["entries"]==closure["entries"]and [e["receipt"]for e in entries]==closure["controller_receipts"],"Final ledger omits/rewrites actual journal root universe")
 return closure
def expand_zero_row(row):
 match=re.fullmatch(r"(\d+)_\[([0-9,\-]+)(?:%\d+)?\]",row["logical_id"])
 if not match:return [row]
 need(row["GPU_count"]==0 and row["elapsed_seconds"]==0 and row["state"]=="CANCELLED","Compressed nonzero/active allocation is ambiguous")
 vals=[]
 for term in match[2].split(","):
  if "-"in term:
   a,b=map(int,term.split("-",1));need(0<=a<=b and b-a<10000,"Compressed cancellation range invalid");vals.extend(range(a,b+1))
  else:vals.append(int(term))
 need(len(vals)==len(set(vals)),"Compressed cancellation duplicate indices")
 return [dict(row,logical_id=match[1]+"_"+str(i),original_compressed_logical_id=row["logical_id"],zero_unallocated_expansion=True)for i in vals]
def expected_allocations(dispatches):
 result={};arrays=set()
 for d in dispatches:
  logical=[d["job_id"]+"_"+str(i)for i in d["indices"]]if d["indices"]is not None else[d["job_id"]]
  if d["indices"]is not None:arrays.add(d["job_id"])
  for key in logical:
   need(key not in result,"Logical allocation appears under multiple submissions");result[key]=d
 return result,arrays
def close_rows(dispatches,explicit_text,universe_text,scope_end):
 expected,arrays=expected_allocations(dispatches)
 exp,steps=parse_accounting(explicit_text);universe,universe_steps=parse_accounting(universe_text);selected={};masters=[]
 for rawrow in exp:
  for row in expand_zero_row(rawrow):
   key=row["logical_id"]
   if key in arrays:
    need(row["GPU_count"]in {None,0}and not row["AllocTRES"]and row["elapsed_seconds"]==0,"Array master has ambiguous positive allocation cost")
    masters.append(dict(row,reason="ZERO_ARRAY_PARENT_NOT_TASK_ALLOCATION"));continue
   need(key in expected,"Unexpected root explicit allocation")
   need(key not in selected,"Duplicate logical terminal allocation")
   need(row["state"]in TERMINAL,"Root allocation nonterminal/unknown state")
   d=expected[key]
   need(row["GPU_count"]is not None,"Missing actual GPU AllocTRES is UNAVAILABLE_NOT_ZERO")
   need(row["WorkDir"]==d["WorkDir"],"Actual root launcher WorkDir differs")
   need(utc(PRIMARY_START)<=accounting_epoch(row["Submit"])<=scope_end+1,"Actual submission escapes declared current scope")
   need(row["user"]==USER and row["account"]==USER and row["job_name"]==d["job_name"]and row["partition"]=="organ","Actual root/account/name/partition differs")
   need(re.fullmatch(r"\d+",row["raw_id"])is not None,"Actual numeric raw allocation identity required")
   if row["GPU_count"]==0:
    need(row["elapsed_seconds"]==0 and row["state"]=="CANCELLED"and not row["AllocTRES"],"Zero cost requires unallocated terminal cancellation")
    row=dict(row,allocation_kind="ZERO_UNALLOCATED_CANCEL",actual_GPU_seconds=0)
   else:
    need(row["GPU_count"]==1,"Current scope requests exactly one GPU per allocation")
    vals=dict(x.split("=",1)for x in row["AllocTRES"].split(",")if "="in x);need(vals.get("cpu")=="3","Actual current scope CPU3 differs")
    start=accounting_epoch(row["Start"]);end=accounting_epoch(row["End"])
    need(start>=utc(PRIMARY_START)and end>=start and end<=scope_end+1,"Actual GPU interval escapes declared current closed scope")
    need(abs((end-start)-row["elapsed_seconds"])<=2,"Actual numeric elapsed vs interval differs")
    row=dict(row,allocation_kind="ACTUAL_GPU_ALLOCATION",actual_GPU_seconds=row["elapsed_seconds"],start_epoch=start,end_epoch=end,actual_memory_AllocTRES=vals.get("mem","UNAVAILABLE_NOT_ZERO"))
    need("mem"not in vals or vals["mem"]in {"64G","65536M"},"Actual allocated memory differs from64G policy")
   selected[key]=dict(row,submission_id=d["submission_id"],phase=d["phase"],submission_kind=d["kind"],stage=d["stage"],rerun_of=d["rerun_of"],result_manifest_required_for_cost=False)
 need(set(selected)==set(expected),"Expected root submitted allocation slots missing")
 allocated=[r for r in selected.values()if r["GPU_count"]>0]
 need(len({r["raw_id"]for r in allocated})==len(allocated),"Duplicate actual numeric GPU allocation identity")
 covered=set();universe_allocated_ids=set();universe_raw_ids=set();scope_zero_cancels=[]
 for rawrow in universe:
  for row in expand_zero_row(rawrow):
   if row["user"]!=USER or row["account"]!=USER or not SCOPE_NAME.fullmatch(row["job_name"]):continue
   if row["logical_id"]in arrays and row["GPU_count"]in {None,0}and not row["AllocTRES"]and row["elapsed_seconds"]==0:continue
   if row["GPU_count"]is None:
    need(row["logical_id"]not in selected,"Declared GPU allocation absent actual GPU TRES in time-universe query")
    need(row["job_name"]not in {d["job_name"]for d in dispatches},"GPU-dispatch name has missing actual allocation TRES")
    continue
   if row["GPU_count"]==0 and row["elapsed_seconds"]==0 and row["state"]=="CANCELLED":scope_zero_cancels.append(row)
   if row["GPU_count"]>0:
    need(row["logical_id"]not in universe_allocated_ids and row["raw_id"]not in universe_raw_ids,"Duplicate positive allocation in time-universe query")
    universe_allocated_ids.add(row["logical_id"]);universe_raw_ids.add(row["raw_id"])
    need(row["logical_id"]in selected,"Unmapped allocated GPU job in declared current project/time/names scope")
    known=selected[row["logical_id"]]
    for k in ("raw_id","state","elapsed_seconds","GPU_count","AllocTRES","Submit","Start","End","WorkDir"):need(row[k]==known[k],"Explicit/time-universe accounting differs: "+k)
    covered.add(row["logical_id"])
 need(covered=={r["logical_id"]for r in allocated},"Bounded time-universe query did not independently cover every actual GPU allocation")
 events=[]
 for row in allocated:
  if row["end_epoch"]>row["start_epoch"]:
   events +=[(row["start_epoch"],1,row["logical_id"]),(row["end_epoch"],-1,row["logical_id"])]
 active=maximum=0
 for t,delta,key in sorted(events,key=lambda x:(x[0],x[1],x[2])):
  active+=delta;need(active>=0,"Invalid GPU concurrency interval accounting");maximum=max(maximum,active)
 need(maximum<=2,"Declared current project scope exceeded global GPU cap2")
 return dict(rows=list(selected.values()),excluded_job_steps=steps,excluded_universe_steps=universe_steps,excluded_zero_array_parent_rows=masters,universe_observed_zero_unallocated_cancels=scope_zero_cancels,
  expected_submitted_allocation_slots=len(expected),allocated_GPU_jobs=len(allocated),zero_unallocated_cancels=sum(r["GPU_count"]==0 for r in selected.values()),
  actual_GPU_seconds=sum(r["actual_GPU_seconds"]for r in selected.values()),allocated_failure_GPU_seconds=sum(r["actual_GPU_seconds"]for r in selected.values()if r["state"]!="COMPLETED"),
  actual_maximum_current_scope_concurrent_GPUs=maximum,concurrency_resolution="Slurm Start/End seconds; end event before start at equal timestamp",
  result_manifests_read_for_cost=False,complete_root_gpu_submission_universe=True,allocated_failure_before_manifest_cost_retained=True)
def reviewed_sources(d):
 d=path(d);need(d.is_dir()and not(d.stat().st_mode&0o222)and {p.name for p in d.iterdir()}==set(FILES),"Exact readonly owned source4 directory required")
 return [rec(verify(rec(d/n),True))for n in FILES]
def source_metadata(d):
 d=path(d);records=[]
 for n in FILES:
  p=path(d/n);st=p.stat();records.append(dict(path=str(p),bytes=st.st_size,inode=st.st_ino,mtime_ns=st.st_mtime_ns,mode=st.st_mode&0o777))
 return records
def original_source_binding(original,source,original_dir,frozen_dir):
 need(len(original)==len(source)==len(FILES)and [r["path"]for r in original]==[str(original_dir/n)for n in FILES]and [r["path"]for r in source]==[str(frozen_dir/n)for n in FILES],"Exact original and frozen owned4 path universe/order")
 need(reviewed_sources(original_dir)==original and reviewed_sources(frozen_dir)==source,"Original/frozen executing source bytes drift")
 for a,b in zip(original,source):need(a["bytes"]==b["bytes"]and a["sha256"]==b["sha256"],"Frozen source is not the reviewed original bytes")
 return True
def frozen_sources():
 d=Path(__file__).resolve().parent
 need(d.is_relative_to(R/"steps/24_benchmark_delivery/frozen")and not(d.stat().st_mode&0o222),"Use accepted immutable cost auditor source only")
 return reviewed_sources(d)
def contracts(out):
 allocation=cpu();jid=os.environ["SLURM_JOB_ID"];entry=Path(__file__);need(entry.is_absolute()and entry.resolve()==entry,"Actual original executing source path must be canonical")
 d=entry.parent;original=reviewed_sources(d);metadata_before=source_metadata(d)
 frozen=R/"steps/24_benchmark_delivery/frozen"/("root_gpu_cost_v3_running_window_v1_"+jid)/"code";frozen.mkdir(parents=True,exist_ok=False)
 for n in FILES:
  shutil.copyfile(verify(original[FILES.index(n)],True),frozen/n);(frozen/n).chmod(0o444)
 frozen.chmod(0o555)
 spec=importlib.util.spec_from_file_location("sealed_cost",frozen/FILES[0]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);sys.modules["root_gpu_cost_audit"]=m
 need(Path(m.__file__)==frozen/FILES[0]and m.FILES==FILES and m.CONTRACT_COUNT==CONTRACT_COUNT,"Actual tested module executes sealed V3 source")
 source=m.frozen_sources();m.original_source_binding(original,source,d,frozen)
 for n in FILES:
  if n.endswith(".py"):compile((frozen/n).read_bytes(),str(frozen/n),"exec")
  if n.endswith(".sbatch"):need(subprocess.run(["bash","-n",str(frozen/n)],capture_output=True,text=True).returncode==0,"CPU launcher syntax")
 spec=importlib.util.spec_from_file_location("cost_contracts",frozen/FILES[1]);tests=importlib.util.module_from_spec(spec);spec.loader.exec_module(tests)
 with(out/"contracts.txt").open("x")as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
 (out/"contracts.txt").chmod(0o444)
 rr=m.dump(out/"contracts.json",dict(status="PASS"if result.wasSuccessful()else"FAIL",tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),tested_source=source,log=m.rec(out/"contracts.txt")))
 m.need(result.wasSuccessful()and result.testsRun==CONTRACT_COUNT and not result.skipped,"Meaningful V3 cost universe contracts failed")
 m.original_source_binding(original,source,d,frozen);metadata_after=m.source_metadata(d)
 m.need(metadata_before==metadata_after and source==m.frozen_sources(),"Whole original/frozen executing source4 prepost identity")
 return m.dump(out/"acceptance.json",dict(schema=SOFTWARE_SCHEMA,status=SOFTWARE,source=source,contracts=rr,entry=m.rec(frozen/FILES[0]),CPU_launcher=m.rec(frozen/FILES[2]),allocation=allocation,original_source=original,original_source_metadata_before=metadata_before,original_source_metadata_after=metadata_after,original_owned_pre_and_post_byte_readback_PASS=True,original_and_frozen_owned_byte_identities_equal=True,all_owned_python_compile_PASS=True,all_launchers_bash_syntax_PASS=True,no_GPU_submission=True,no_accounting_science_run=True))
def query(argv,out,name):
 env={**os.environ,"TZ":"UTC","SLURM_TIME_FORMAT":"standard"}
 p=subprocess.run(argv,capture_output=True,text=True,env=env,check=False);(out/(name+".stdout")).write_text(p.stdout);(out/(name+".stderr")).write_text(p.stderr)
 (out/(name+".stdout")).chmod(0o444);(out/(name+".stderr")).chmod(0o444)
 rr=dump(out/(name+".command.json"),dict(argv=argv,TZ="UTC",SLURM_TIME_FORMAT="standard",returncode=p.returncode,stdout=rec(out/(name+".stdout")),stderr=rec(out/(name+".stderr"))))
 need(p.returncode==0,"Actual numeric accounting query failed");return p.stdout,rr
def time_universe_argv(ledger):
 need(ledger.get("scope_start_utc")==PRIMARY_START,"Independent query cannot shift frozen scope start")
 end=ledger["scope_end_utc"];need(utc(end)>=utc(PRIMARY_START),"Closed explicit UTC scope end required")
 return ["sacct","-n","-P","-u",USER,"-S",ledger["scope_start_utc"].replace("Z",""),"-E",end.replace("Z",""),"--state=RUNNING","--format="+FIELDS]
def root_accounting_queries(jobs,ledger,out):
 text,explicit=query(["sacct","-n","-P","-j",",".join(sorted(set(jobs),key=int)),"--format="+FIELDS],out,"explicit_root_submissions")
 universe,uquery=query(time_universe_argv(ledger),out,"bounded_current_name_universe")
 return text,explicit,universe,uquery
def preliminary_inventory(explicit_text,universe_text):
 rows,steps=parse_accounting(explicit_text);universe,usteps=parse_accounting(universe_text)
 return dict(status="ACTUAL_NUMERIC_ACCOUNTING_RETAINED_CLOSURE_PENDING",explicit_rows=rows,time_universe_rows=universe,excluded_steps=steps,excluded_universe_steps=usteps,positive_failure_rows=[r for r in rows if r["GPU_count"]is not None and r["GPU_count"]>0 and r["elapsed_seconds"]>0 and r["state"]!="COMPLETED"],missing_GPU_TRES_rows=[r for r in rows if r["GPU_count"]is None],result_manifest_required=False,duplicate_or_unmapped_rows_are_accepted_cost=False)
def audit(args,out):
 allocation=cpu();software=shape(args.software_acceptance);source=software_ready(software)
 ledgerrec=shape(args.ledger);ledger=read(verify(ledgerrec,True));entries,end=ledger_contract(ledger)
 need(end<=datetime.datetime.now(datetime.timezone.utc).timestamp(),"Future closed scope forbidden")
 # Root submission proof/IDs precede accounting. No downstream model result is consumed here.
 controllers=[];rootreceipts=[];jobs=[]
 for e in entries:
  controller=read(verify(e["receipt"],True));jid=str(controller.get("job_id",controller.get("array_job_id","")))
  need(re.fullmatch(r"\d+",jid)is not None,"Immutable root receipt must supply actual numeric submitted ID")
  controllers.append((e,controller));rootreceipts.append(e["receipt"]);jobs.append(jid)
 queued,qreceipt=query(["squeue","-h","-u",USER,"-o","%i|%.256j|%T|%b"],out,"current_scope_squeue")
 text,explicit,universe,uquery=root_accounting_queries(jobs,ledger,out)
 inventory=dump(out/"preclosure_numeric_inventory.json",preliminary_inventory(text,universe))
 need(len(jobs)==len(set(jobs)),"Duplicate root submission numeric job ID")
 # Every downstream lineage/gate/mapping issue now retains actual numeric/raw allocations first.
 journalproof=verify_journal_ledger(ledger)
 previous=ledger.get("previous_ledger")
 if previous:
  prior=read(verify(previous,True));ledger_contract(prior)
  need(ledger["entries"][:len(prior["entries"])]==prior["entries"],"Immutable root ledger dropped/rewrote prior submission")
  need(utc(prior["scope_end_utc"])<=end,"Root ledger scope end moved backwards")
 for line in queued.splitlines():
  vals=[v.strip()for v in line.split("|")];need(len(vals)==4,"Malformed active scope scheduler row")
  need(not SCOPE_NAME.fullmatch(vals[1])or "gpu"not in vals[3].lower(),"Current scope neural GPU job remains active or unregistered")
 dispatches=[]
 def fetch(r):return read(verify(r,True))
 for e,controller in controllers:
  verify(controller["launcher"],True)
  if controller.get("entry")is not None:verify(controller["entry"],True)
  if e["phase"]=="formal_generation":verify(controller["resource_policy"],True)
  dispatches.append(submission_contract(e,controller,fetch,Path(controller["launcher"]["path"]).read_text()))
 need(sum(d["job_id"]=="13260"and d["kind"]=="primary"for d in dispatches)==1,"Current formal primary actual identity absent")
 common=read(verify(ledger["common_preflight"],True));need(common.get("status")=="COMMON_SUCCESSOR_CPU_PREFLIGHT_ACCEPTED_ROOT_PENDING_ONLY_GPU_SUBMISSION_REQUIRED","Actual current common scope required")
 prim=[d for d in dispatches if d["phase"]=="common_review"and d["kind"]=="primary"]
 if common["root_pending_job_indices"]:need(len(prim)==1 and prim[0]["preflight"]==ledger["common_preflight"],"Current common primary universe incomplete")
 else:need(not prim,"No pending common jobs but GPU primary submitted")
 physical=read(verify(ledger["physical_preflight"],True));need(physical.get("status")=="CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED"and physical.get("GPU_allocated")==0,"Actual current physical scope required")
 e2e=[d for d in dispatches if d["phase"]=="reference_free_e2e"]
 if ledger["e2e_disposition"]=="upstream_rejected":need(physical["qualified_prediction"]["status"]=="POSE_REJECTED"and not e2e,"Physical rejection must have no forced new model stages")
 else:need(physical["qualified_prediction"]["status"]=="POSE_ACCEPTED"and e2e and all(d["preflight"]==ledger["physical_preflight"]for d in e2e),"Attempted E2E must bind actual qualified source")
 closed=close_rows(dispatches,text,universe,end);cost=dump(out/"terminal_numeric_cost_closure.json",closed)
 historical,hquery=query(["sacct","-n","-P","-j","13266","--format="+FIELDS],out,"non_GPU_unallocated_history_13266")
 hrows,hsteps=parse_accounting(historical);selected=[r for r in hrows if r["logical_id"]=="13266"]
 need(len(selected)==1 and selected[0]["GPU_count"]==0 and selected[0]["elapsed_seconds"]==0 and selected[0]["state"]=="CANCELLED"and not selected[0]["AllocTRES"],"CPU13266 must remain exact unallocated cancelled history")
 history=dump(out/"non_GPU_history_13266.json",dict(row=selected[0],query=hquery,excluded_steps=hsteps,not_GPU_submission=True,not_current_physical_preflight=True,no_scientific_run=True))
 return dump(out/"acceptance.json",dict(schema="root_current_gpu_cost_closure.v1",status=ACCEPTED,source=source,software_acceptance=software,ledger=ledgerrec,dispatches=dispatches,
  scope_start_utc=PRIMARY_START,scope_end_utc=ledger["scope_end_utc"],job_name_scope=SCOPE_NAME.pattern,complete_root_gpu_submission_universe=True,allocated_failure_before_manifest_cost_retained=True,
  root_gpu_submission_receipts=rootreceipts,journal_closure=ledger["journal_closure"],terminal_numeric_accounting_receipts=[explicit,uquery,inventory,cost],active_scope_query=qreceipt,
  terminal_costs=cost,CPU13266_unallocated_history=history,actual_GPU_seconds=closed["actual_GPU_seconds"],allocated_failure_GPU_seconds=closed["allocated_failure_GPU_seconds"],
  actual_current_scope_maximum_concurrent_GPUs=closed["actual_maximum_current_scope_concurrent_GPUs"],allocation=allocation,result_manifests_required_for_cost=False,
  scientific_output_acceptance=False,whole_historical_project_cost_claim=False,new_GPU_submission=False,ACTIVE_changed=False))
def main():
 p=argparse.ArgumentParser();sp=p.add_subparsers(dest="mode",required=True);a=sp.add_parser("contracts");a.add_argument("--out",required=True)
 for mode in ("audit","seal-ledger"):
  a=sp.add_parser(mode)
  for k in ("software-acceptance","software-sha256","out"):a.add_argument("--"+k,required=True)
  if mode=="audit":
   for k in ("ledger","ledger-sha256"):a.add_argument("--"+k,required=True)
  else:
   for k in ("journal","common-preflight","physical-preflight","scope-end-utc","e2e-disposition"):a.add_argument("--"+k,required=True)
 a=p.parse_args();out=path(a.out);out.mkdir(parents=True,exist_ok=False)
 try:
  if a.mode=="contracts":r=contracts(out)
  else:
   cpu() # No scientific source/receipt hashing is permitted before actual CPU guard.
   sr=rec(a.software_acceptance);need(sr["sha256"]==a.software_sha256,"Exact tested source CLI acceptance required");a.software_acceptance=sr
   if a.mode=="seal-ledger":r=seal_ledger(a,out)
   else:
    lr=rec(a.ledger);need(lr["sha256"]==a.ledger_sha256,"Exact CPU ledger CLI acceptance required");a.ledger=lr;r=audit(a,out)
  print(json.dumps(r))
 except Exception as e:
  dump(out/"typed_incomplete.json",dict(status="ROOT_GPU_COST_UNIVERSE_TYPED_INCOMPLETE",mode=a.mode,reason_type=type(e).__name__,reason=str(e),raw_accounting_preserved=[str(x)for x in out.glob("*.stdout")],no_cost_imputation=True,no_scientific_promotion=True));raise
if __name__=="__main__":main()
