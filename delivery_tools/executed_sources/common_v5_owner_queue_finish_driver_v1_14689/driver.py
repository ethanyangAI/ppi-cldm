#!/usr/bin/env python3
"""Own CPU queue proof adapter; execute the unchanged accepted Common V5."""
import argparse, contextlib, datetime, hashlib, importlib.util, json, os, re, shutil, stat, subprocess, sys, unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
S=R/"steps/24_benchmark_delivery"
P=S/"pending/common_v5_owner_queue_finish_driver_v1"
FILES=("driver.py","test_driver.py","driver_cpu.sbatch","HANDOFF.md")
COMMON_FILES=("common_review_successor.py","test_common_review_successor.py","successor_bootstrap.py","common_review_cpu.sbatch","common_review_gpu.sbatch","intrinsic_clearance.py","HANDOFF.md")
OLD_D=S/"frozen/common_review_successor_v5_13269/code"
OLD_ENTRY=OLD_D/"common_review_successor.py"
USER="u21111210118"
ARRAY="13423"
JOB_NAME="test9_common_ownerqueue_finish_cpu"
COUNT=32
SW_SCHEMA="common-v5-owner-queue-driver-software.v1"
SW_STATUS="COMMON_V5_OWNER_QUEUE_FINISH_DRIVER_SOFTWARE_CPU_ACCEPTED_NOT_SCIENCE"
EXEC_STATUS="COMMON_V5_UNCHANGED_FINISH_DRIVER_CPU_COMPLETE_SEPARATE_PROOF"
CORE=R/"env/core/bin/python"
CORE_REAL=R/"env/core/bin/python3.11"
CORE_BYTES=25916456
CORE_SHA="76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a"
TARGET_ARGV=["squeue","-h","-j",ARRAY]
TARGET_KWARGS={"capture_output":True,"text":True,"check":True}
OWNER_ARGV=["squeue","-h","-u",USER,"-o","%i|%T"]
CACHED=(105,106,107,146,147,148,176,177,178,187,188,189,212,213,214,215,216,217,284,285)
PENDING=[i for i in range(288) if i not in CACHED]
def pin(path,n,h):return {"path":str(path),"bytes":n,"sha256":h}
COMMON_SW=pin(S/"runs/common_successor_contracts_13269/acceptance.json",6429,"da595226c4a6db5b0fd6ebcfdce9d29e92362fb76d849e15941d0ca5c4a8886d")
PREFLIGHT=pin(S/"runs/formal_common_preflight_13407_13409/preflight.json",889318,"e30b4e61c45d8de80701d82199fda1d6c79176e9092d2a0f91c40e05598589e0")
CONTROLLER=pin(S/"submissions/formal_common_pending_from13422_primary_claim/root_submission.json",5157,"a5bb7cf6bc20fca0d7e05127065dad7f6b5b1f6cff9b8b192a109318aa7f2a22")
COST=pin(S/"runs/root_gpu_cost_audit_14576/acceptance.json",15252,"ca6bac7a46bad01841a52804c2793b875934cf2cc7672d9ceb24de62a3c25ebd")
COST_SW=pin(S/"runs/root_gpu_cost_contracts_14565/acceptance.json",7539,"b46e1f1f7e8dd9ea30a2c8109843a62ee2ff83c0ecd9da779b5bd9d6718a24c6")
LEDGER=pin(S/"runs/root_gpu_cost_seal-ledger_13782/root_gpu_submission_ledger.json",2782,"b4601b7acabf198d22bc949985fcb2f707df9b82049f24886d01449944adf998")
NAMED_CONTROLS=(
 (S/"submissions/root_gpu_cost_v3_audit14576_actual_full_cost_metadata_terminal_seal/receipt.json",24087),
 (S/"submissions/formal_common_finish14600_actual_failed_typed_metadata_terminal_seal/receipt.json",5554),
 (S/"submissions/common13423_completed_controller_queue_diagnostic_metadata_20261014T043818Z/receipt.json",2267),
 (S/"submissions/common_ownerqueue_driver_native13211_input_metadata_readonly_seal/receipt.json",1455),
)
def need(v,msg):
 if not v:raise ValueError(msg)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def path(p):
 p=Path(p)
 need(p.is_absolute() and ".." not in p.parts and p.is_relative_to(R) and p.resolve()==p,"Canonical nonsymbolic test9 path required")
 return p
def shape(r):
 need(isinstance(r,dict) and {"path","bytes","sha256"}<=r.keys(),"Exact receipt required")
 need(isinstance(r["path"],str) and type(r["bytes"]) is int and r["bytes"]>=0 and isinstance(r["sha256"],str) and re.fullmatch("[0-9a-f]{64}",r["sha256"]),"Typed exact receipt required")
 path(r["path"]);return r
def metadata(p):
 p=path(p);s=p.lstat()
 return dict(path=str(p),bytes=s.st_size,inode=s.st_ino,mtime_ns=s.st_mtime_ns,mode=stat.S_IMODE(s.st_mode),regular=stat.S_ISREG(s.st_mode),directory=stat.S_ISDIR(s.st_mode),symlink=stat.S_ISLNK(s.st_mode))
def record(p):
 p=path(p);need(p.is_file(),"Regular file required")
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 return pin(p,p.stat().st_size,h.hexdigest())
def verify(r,readonly=True):
 shape(r);p=path(r["path"]);need(record(p)==r,"Exact byte receipt drift: "+str(p))
 need(not readonly or not(p.stat().st_mode&0o222),"Readonly input required: "+str(p));return p
def read(r):return json.loads(verify(r).read_text())
def dump(p,obj):
 p=path(p);need(not p.exists(),"Exclusive output required")
 with p.open("x") as f:json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
 p.chmod(0o444);return record(p)
def gpu_tres(value):
 values={}
 for token in value.split(","):
  need("=" in token,"Malformed allocated TRES")
  k,v=token.split("=",1);need(k and k not in values,"Duplicate allocated TRES");values[k]=v
  need(not k.startswith("gres/gpu") or k=="gres/gpu" or re.fullmatch(r"gres/gpu:[A-Za-z0-9_.-]+",k),"Malformed GPU namespace")
 need(values.get("cpu","").isdigit(),"Actual numeric CPU TRES required")
 gpu=[(k,v) for k,v in values.items() if k=="gres/gpu" or k.startswith("gres/gpu:")]
 need(all(re.fullmatch(r"\d+",v) for k,v in gpu),"Numeric GPU TRES required")
 generic=int(values["gres/gpu"]) if "gres/gpu" in values else None
 typed=sum(int(v) for k,v in gpu if k.startswith("gres/gpu:"))
 if generic is not None and any(k.startswith("gres/gpu:") for k,v in gpu):need(generic==typed,"GPU TRES representations differ")
 return values,typed if generic is None else generic
def select_cpu(text,jid,production=False):
 rows=[line for line in text.splitlines() if re.search(r"\bJobId="+re.escape(jid)+r"(?:\s|$)",line)]
 need(len(rows)==1,"Unique actual current CPU row required")
 pairs=re.findall(r"(\w+)=(\S*)",rows[0]);fields={}
 for k,v in pairs:
  need(k not in fields,"Duplicate current scheduler field");fields[k]=v
 need(fields.get("JobState")=="RUNNING" and fields.get("JobName")==JOB_NAME,"Actual RUNNING driver job required")
 need(fields.get("UserId","").startswith(USER+"(") and fields.get("Account")==USER and fields.get("Partition")=="organ","Actual driver ownership/account/organ required")
 need(fields.get("NumCPUs","").isdigit() and int(fields["NumCPUs"])>=1,"Actual CPU allocation required")
 representations=[]
 for k in ("TRES","AllocTRES"):
  if k in fields:
   values,gpus=gpu_tres(fields[k]);need(int(values["cpu"])==int(fields["NumCPUs"]) and gpus==0,"Allocated CPU/GPU guard differs");representations.append((k,values))
 need(representations,"Actual allocated CPU TRES required")
 if len(representations)==2:need(representations[0][1]==representations[1][1],"Dual allocated TRES differs")
 if production:need(fields["NumCPUs"]=="2" and fields.get("MinMemoryNode") in {"16G","16384M"} and fields.get("TimeLimit")=="04:00:00","Production CPU2/16G/4h envelope required")
 return dict(job_id=jid,selected_scheduler_record=rows[0],allocated_CPUs=int(fields["NumCPUs"]),allocated_GPUs=0,allocated_TRES_fields=[k for k,v in representations])
def cpu(production=False):
 jid=os.environ.get("SLURM_JOB_ID","");need(jid.isdigit(),"Allocated Slurm job required")
 need(os.environ.get("CUDA_VISIBLE_DEVICES")=="" and os.environ.get("JAX_PLATFORMS")=="cpu","Pure CPU mask required")
 need(os.environ.get("PYTHONNOUSERSITE")=="1" and os.environ.get("PYTHONDONTWRITEBYTECODE")=="1" and "PYTHONPATH" not in os.environ,"Import isolation required")
 need(all(os.environ.get(k)=="1" for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS")),"CPU thread caps required")
 return select_cpu(subprocess.check_output(["scontrol","show","job",jid,"-o"],text=True),jid,production)
def runtime_core(executable=None):
 need(CORE.is_symlink() and os.readlink(CORE)=="python3.11" and CORE.resolve()==CORE_REAL and Path(sys.executable if executable is None else executable).resolve()==CORE_REAL,"Exact accepted conditional core interpreter required")
 link=CORE.lstat();s=CORE_REAL.stat();need(stat.S_ISREG(s.st_mode) and s.st_size==CORE_BYTES,"Conditional core binary shape")
 h=hashlib.sha256()
 with CORE_REAL.open("rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 need(h.hexdigest()==CORE_SHA,"Conditional core binary drift")
 return dict(scope="CONDITIONAL_INSTALLED_CPU_RUNTIME_NOT_ARCHIVE_SOURCE",logical_interpreter=str(CORE),resolved_interpreter=str(CORE_REAL),link_target=os.readlink(CORE),link_inode=link.st_ino,link_mtime_ns=link.st_mtime_ns,binary_inode=s.st_ino,binary_mtime_ns=s.st_mtime_ns,binary_mode=stat.S_IMODE(s.st_mode),bytes_as_scalar=s.st_size,sha256_as_scalar=h.hexdigest())
def reviewed(d):
 d=path(d);need(d.is_dir() and not(d.stat().st_mode&0o222) and {p.name for p in d.iterdir()}==set(FILES),"Exact readonly OWN4 universe required")
 return [record(verify(record(d/n))) for n in FILES]
def source_binding(original,frozen,original_dir,frozen_dir):
 need(len(original)==len(frozen)==4 and [r["path"] for r in original]==[str(original_dir/n) for n in FILES] and [r["path"] for r in frozen]==[str(frozen_dir/n) for n in FILES],"OWN4 path order/universe differs")
 need(reviewed(original_dir)==original and reviewed(frozen_dir)==frozen,"OWN4 current byte drift")
 need(all(a["bytes"]==b["bytes"] and a["sha256"]==b["sha256"] for a,b in zip(original,frozen)),"Original/frozen OWN4 differs")
 return True
def load_module(name,p):
 spec=importlib.util.spec_from_file_location(name,str(p));m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def old_contract(sw,ct,source):
 need(sw.get("status")=="COMMON_SUCCESSOR_SOFTWARE_SOURCE_CPU_ACCEPTED_FUTURE_FORMAL_PREPARATION_PENDING" and sw.get("actual_CPU_job_id")=="13269" and sw.get("source")==source,"Exact old Common software/source required")
 need(ct.get("status")=="PASS" and type(ct.get("tests_run")) is int and ct["tests_run"]==58 and type(ct.get("failures")) is int and ct["failures"]==0 and type(ct.get("errors")) is int and ct["errors"]==0,"Saved old58 contracts unqualified")
 need(sw["entry"]==source["successor"][0] and sw["CPU_launcher"]==source["successor"][3] and sw["GPU_launcher"]==source["successor"][4],"Old source launcher/entry identities differ")
def old_identity(m):
 need(Path(m.__file__)==OLD_ENTRY and m.SELF==OLD_ENTRY and m.D==OLD_D and m.FILES==COMMON_FILES and m.CORE==CORE,"Preserve actual OLD __file__/SELF/D/FILES/CORE")
 return True
def old_module():
 sw=read(COMMON_SW);ct=read(sw["contracts"]);verify(ct["log"])
 own=sw["source"]["successor"]
 need(len(own)==7 and [r["path"] for r in own]==[str(OLD_D/n) for n in COMMON_FILES],"Exact accepted OLD source7 universe/order")
 need({p.name for p in OLD_D.iterdir()}==set(COMMON_FILES) and not(OLD_D.stat().st_mode&0o222),"Old source directory drift")
 for r in own:verify(r)
 need(sw["entry"]["path"]==str(OLD_ENTRY),"Old accepted entry required")
 m=load_module("accepted_common_v5_ownerqueue",verify(sw["entry"]))
 old_identity(m)
 source=m.sources();old_contract(sw,ct,source)
 need(m.subprocess is subprocess,"Old module global subprocess must be original standard library object")
 return m,sw,ct,source
def control_semantics(m,source,pre,sub,cost):
 need(pre.get("status")=="COMMON_SUCCESSOR_CPU_PREFLIGHT_ACCEPTED_ROOT_PENDING_ONLY_GPU_SUBMISSION_REQUIRED" and pre["source"]==source and pre["software_acceptance"]==COMMON_SW,"Exact actual old-source preflight required")
 need(all(type(i) is int for i in pre["root_pending_job_indices"]) and pre["root_pending_job_indices"]==PENDING and pre["expected_jobs"]==288 and pre["expected_models"]==1124,"Actual pending268/native20/fixed model universe differs")
 need(all(type(i) is int for i in sub["indices"]) and sub["array_job_id"]==ARRAY and sub["preflight"]==PREFLIGHT and sub["indices"]==PENDING and sub["concurrency_cap"]==2,"Root common array/preflight/indices differ")
 need(sub.get("raw_sbatch_stdout")==sub.get("raw_stdout")=="13423\n" and sub.get("raw_sbatch_stderr")==sub.get("raw_stderr")=="","Canonical current controller aliases differ")
 array,launcher=m.submission_contract(sub,PREFLIGHT,pre);need(array==ARRAY,"Unchanged Common submission contract differs")
 need(cost.get("schema")=="root_current_gpu_cost_closure.v1" and cost.get("status")=="ROOT_CURRENT_GPU_SUBMISSION_UNIVERSE_AND_TERMINAL_COST_CPU_ACCEPTED","Actual FULL numeric Cost required")
 need(cost["software_acceptance"]==COST_SW and cost["ledger"]==LEDGER and cost["scope_start_utc"]=="2026-10-11T14:25:00Z" and cost["scope_end_utc"]=="2026-10-12T16:39:19Z","FULL Cost source/ledger/scope differs")
 need(cost["complete_root_gpu_submission_universe"] is True and cost["allocated_failure_before_manifest_cost_retained"] is True and type(cost["actual_current_scope_maximum_concurrent_GPUs"]) is int and 0<=cost["actual_current_scope_maximum_concurrent_GPUs"]<=2,"FULL Cost closure incomplete")
 need(CONTROLLER in cost["root_gpu_submission_receipts"] and cost["allocation"]["job_id"]=="14576" and type(cost["allocation"]["allocated_CPUs"]) is int and cost["allocation"]["allocated_CPUs"]==1 and type(cost["allocation"]["allocated_GPUs"]) is int and cost["allocation"]["allocated_GPUs"]==0,"Actual Cost/current controller allocation binding")
 current=[d for d in cost["dispatches"] if d["phase"]=="common_review"]
 need(len(current)==1 and current[0]["job_id"]==ARRAY and current[0]["indices"]==PENDING and current[0]["preflight"]==PREFLIGHT and current[0]["launcher"]==launcher,"Cost exact current array namespace differs")
 need(all(cost.get(k) is False for k in ("scientific_output_acceptance","new_GPU_submission","ACTIVE_changed")),"Cost cannot promote science or new GPU")
 return launcher
def fixed_state():
 m,sw,ct,source=old_module()
 pre=read(PREFLIGHT);sub=read(CONTROLLER);cost=read(COST);csw=read(COST_SW)
 control_semantics(m,source,pre,sub,cost)
 need(csw["source"]==cost["source"] and csw["status"]=="ROOT_GPU_COST_AUDITOR_SOFTWARE_CPU_ACCEPTED" and csw["schema"]=="root-gpu-cost-software.v3","Actual Cost88 software/source differs")
 cct=read(csw["contracts"]);verify(cct["log"]);need(cct["status"]=="PASS" and cct["tests_run"]==88 and all(cct[k]==0 for k in ("failures","errors","skipped")),"Saved actual Cost88 metadata required")
 receipts=[COMMON_SW,sw["contracts"],ct["log"],PREFLIGHT,CONTROLLER,COST,COST_SW,csw["contracts"],cct["log"],LEDGER,cost["journal_closure"]]+source["successor"]+list(m.PINS.values())+cost["source"]
 bundle=read(m.PINS["bundle"])
 receipts +=[pair["frozen"] for pair in bundle["files"]]
 named=[]
 for p,n in NAMED_CONTROLS:
  need(path(p).stat().st_size==n,"Named root control byte count differs")
  rr=record(p);verify(rr);named.append(rr);receipts.append(rr)
 fullseal=read(named[0]);need(fullseal["schema"]=="root-cost-v3-full-audit-actual-terminal-metadata-only.v1" and fullseal["status"]=="ACTUAL_FULL_NUMERIC_COST_TERMINAL_METADATA_READBACK_PASS_NOT_SCIENTIFIC_ACCEPTANCE" and fullseal["actual_full_cost_acceptance"]==COST and fullseal["source"]==cost["source"],"Actual FULL Cost terminal proof required")
 terminal=fullseal["terminal_query"]
 for k in ("stdout","stderr"):receipts.append(record(terminal[k]))
 need(terminal["returncode"]==0 and terminal["selected_row"] in Path(terminal["stdout"]).read_text().splitlines() and not Path(terminal["stderr"]).read_text(),"Saved Cost terminal raw differs")
 cells=terminal["selected_row"].split("|");need(len(cells)==15 and cells[:8]==["14576","ppi_root_gpu_cost_cpu",USER,USER,"organ","COMPLETED","0:0","13"] and cells[-2:]==["1","8G"],"Actual Cost terminal identity differs")
 failed=read(named[1]);need(failed["job_id"]=="14600" and failed["output_acceptance_absent"] is True and failed["original_failed_squeue_reply_stdout_stderr_not_saved"] is True and failed["original_query_failure_cause_unproven"] is True,"Failed14600 provenance must remain unresolved")
 later=read(named[2]);need(later["original14600_failed_squeue_reply_not_saved_cause_unproven"] is True and later["not_retroactive_original_reply"] is True,"Later scheduler reply is not original14600 failure")
 native_seal=read(named[3]);native_meta=metadata(m.PINS["native"]["path"])
 need(native_seal["schema"]=="common-ownerqueue-driver-historical-native-input-metadata-only.v1" and native_seal["status"]=="HISTORICAL_QUALIFIED_NATIVE_CONTROL_METADATA_READBACK_PASS_NOT_NEW_SCIENCE_ACCEPTANCE" and native_seal["file_after"]=={k:(format(native_meta[k],"04o") if k=="mode" else native_meta[k]) for k in ("path","bytes","inode","mtime_ns","mode","regular","symlink")},"Historical native readonly control seal metadata differs")
 need(native_seal["file_before"]==dict(native_seal["file_after"],mode="0664") and native_seal["file_after"]["mode"]=="0444" and native_seal["byte_inode_mtime_unchanged"] is True and native_seal["only_mode_0664_to_0444"] is True,"Historical native seal may change only readonly mode")
 for r in fullseal["files_after"]+failed["files_after"]:
  need(metadata(r["path"])=={k:(int(r[k],8) if k=="mode" else r[k]) for k in ("path","bytes","inode","mtime_ns","mode","regular","directory","symlink")},"Root terminal metadata table drift")
  receipts.append(record(r["path"]))
 for q in later["queries"]:
  for k in ("stdout","stderr"):
   need(path(q[k]).stat().st_size==q[k+"_bytes"],"Later diagnostic raw metadata differs");receipts.append(record(q[k]))
 bypath={}
 for rr in receipts:
  verify(rr);need(rr["path"] not in bypath or bypath[rr["path"]]==rr,"Control/source receipt fork");bypath[rr["path"]]=rr
 table=[dict(receipt=rr,metadata=metadata(rr["path"])) for rr in sorted(bypath.values(),key=lambda r:r["path"])]
 return m,dict(old_software=COMMON_SW,old_source=source,root_preflight=PREFLIGHT,current_controller=CONTROLLER,actual_full_cost=COST,cost_software=COST_SW,ledger=LEDGER,late_root_controls=named,actually_consumed_source_and_controls=table)
def readback(table):
 for r in table:verify(r["receipt"]);need(metadata(r["receipt"]["path"])==r["metadata"],"Executing input/control metadata drift")
 return True
def parse_owner_queue(text):
 need(isinstance(text,str),"Actual owner queue text required")
 rows=[];seen=set()
 for line in text.splitlines():
  need(line and line==line.strip() and line.count("|")==1,"Malformed owner queue row")
  jid,state=line.split("|")
  need(re.fullmatch(r"[1-9]\d*(?:_(?:0|[1-9]\d*)|_\[(?:\d+(?:-\d+)?)(?:,\d+(?:-\d+)?)*(?:%\d+)?\])?",jid),"Malformed logical scheduler ID")
  need(re.fullmatch("[A-Z][A-Z_]*",state),"Malformed scheduler state")
  need(jid not in seen,"Duplicate owner queue logical ID");seen.add(jid)
  if "_[" in jid:
   inside=jid.split("_[",1)[1][:-1];terms=inside.split("%")
   need(len(terms)<=2 and (len(terms)==1 or int(terms[1])>0),"Invalid compressed throttle")
   ranges=[]
   for term in terms[0].split(","):
    v=term.split("-");need(all(re.fullmatch(r"(?:0|[1-9]\d*)",x) for x in v),"Noncanonical compressed index");lo=int(v[0]);hi=int(v[-1]);need(lo<=hi,"Inverted compressed index range")
    need(not any(max(lo,a)<=min(hi,b) for a,b in ranges),"Overlapping compressed index terms");ranges.append((lo,hi))
  rows.append(dict(logical_id=jid,state=state))
 return rows
def derive_queue(text,returncode):
 need(type(returncode) is int and returncode==0,"Owner query failure is not empty queue")
 rows=parse_owner_queue(text)
 matches=[r for r in rows if r["logical_id"]==ARRAY or r["logical_id"].startswith(ARRAY+"_")]
 need(not matches,"Any current target-array parent/task/range record blocks finish")
 return dict(status="DERIVED_TARGET_ONLY_ABSENCE_FROM_ACTUAL_OWNER_QUEUE",target_array_id=ARRAY,owner=USER,owner_rows=rows,target_rows=[],derived_stdout="",derived_stderr="",original_target_query_executed=False,original_request_role="INTERCEPTED_NOT_EXECUTED",no_original_raw_reply_fabricated=True)
def observe_queue(control,backend=subprocess,timeout=60):
 control=path(control);env={**os.environ,"TZ":"UTC","SLURM_TIME_FORMAT":"standard"};started=now()
 try:
  p=backend.run(list(OWNER_ARGV),capture_output=True,text=True,check=False,env=env,timeout=timeout)
  stdout=p.stdout;stderr=p.stderr;rc=p.returncode;exception=None
 except subprocess.TimeoutExpired as e:
  def text(v):return v.decode("utf-8",errors="replace") if isinstance(v,bytes) else(v or "")
  stdout=text(e.stdout);stderr=text(e.stderr);rc=None;exception=dict(type="TimeoutExpired",reason=str(e))
 except Exception as e:
  stdout="";stderr="";rc=None;exception=dict(type=type(e).__name__,reason=str(e))
 for name,value in (("owner_queue.stdout",stdout),("owner_queue.stderr",stderr)):
  with(control/name).open("x") as f:f.write(value)
  (control/name).chmod(0o444)
 command=dump(control/"owner_queue.command.json",dict(argv=OWNER_ARGV,TZ="UTC",SLURM_TIME_FORMAT="standard",returncode=rc,exception=exception,started_utc=started,finished_utc=now(),stdout=record(control/"owner_queue.stdout"),stderr=record(control/"owner_queue.stderr")))
 need(exception is None,"Actual owner query exception; raw retained")
 derived=derive_queue(stdout,rc)
 proof=dump(control/"target_queue_proof.json",{**derived,"schema":"common-v5-owner-queue-target-derived-proof.v1","actual_owner_query":command,"original_request":{"argv":TARGET_ARGV,"kwargs":TARGET_KWARGS,"execution":"INTERCEPTED_NOT_EXECUTED"},"old_finish_squeue_txt_role":"DERIVED_TARGET_ONLY_NOT_ORIGINAL_SQUEUE_J_REPLY"})
 return proof,derived
def verify_queue_proof(proof,derived):
 doc=read(proof)
 need(doc["schema"]=="common-v5-owner-queue-target-derived-proof.v1" and {k:doc[k] for k in derived}==derived,"Derived queue proof identity drift")
 need(doc["original_request"]=={"argv":TARGET_ARGV,"kwargs":TARGET_KWARGS,"execution":"INTERCEPTED_NOT_EXECUTED"},"Original request must remain unexecuted")
 command=read(doc["actual_owner_query"])
 need(command["argv"]==OWNER_ARGV and command["returncode"]==0 and command["exception"] is None and command["TZ"]=="UTC" and command["SLURM_TIME_FORMAT"]=="standard","Actual owner command identity drift")
 stdout=verify(command["stdout"]).read_text();verify(command["stderr"])
 need(derive_queue(stdout,command["returncode"])==derived,"Actual owner raw/derived proof differs")
 return doc
class QueueProxy:
 def __init__(self,backend,proof,derived):
  self.backend=backend;self.proof=proof;self.derived=derived;self.calls=0
 def __getattr__(self,name):return getattr(self.backend,name)
 def run(self,*args,**kwargs):
  if len(args)==1 and args[0]==TARGET_ARGV:
   need(kwargs==TARGET_KWARGS and all(kwargs[k] is True for k in TARGET_KWARGS),"Only exact old target squeue signature may be intercepted")
   need(self.calls==0,"Target queue proof cannot be consumed repeatedly")
   doc=verify_queue_proof(self.proof,self.derived)
   need(doc["derived_stdout"]==self.derived["derived_stdout"]=="" and doc["derived_stderr"]=="","Derived target-only queue reply differs")
   self.calls+=1
   return subprocess.CompletedProcess(list(TARGET_ARGV),0,stdout="",stderr="")
  return self.backend.run(*args,**kwargs)
def with_old_finish(m,proxy,args,out,typed_failure):
 original=m.subprocess
 need(original is proxy.backend,"Proxy must delegate exact original module subprocess")
 global_library=subprocess
 m.subprocess=proxy
 try:return m.finish(args,out)
 except Exception as e:
  typed_failure(e)
  raise
 finally:
  m.subprocess=original
  need(subprocess is global_library and m.subprocess is original,"Module-local subprocess binding not restored")
def driver_software_contract(sw,ct,source):
 need(sw.get("schema")==SW_SCHEMA and sw.get("status")==SW_STATUS and sw.get("source")==source,"Actual current driver software/source required")
 need(sw["entry"]==source[0] and sw["CPU_launcher"]==source[2],"Driver software exact entry/launcher source bindings")
 need(ct.get("status")=="PASS" and type(ct.get("tests_run")) is int and ct["tests_run"]==COUNT and all(type(ct.get(k)) is int and ct[k]==0 for k in ("failures","errors","skipped")) and ct["tested_source"]==source,"Actual all32 driver contracts without errors/skips required")
 need(sw["old_common_software"]==COMMON_SW and sw["root_preflight"]==PREFLIGHT and sw["current_controller"]==CONTROLLER and sw["actual_full_cost"]==COST,"Driver software exact controls required")
 need(all(sw.get(k) is True for k in ("all_owned_python_compile_PASS","all_launchers_bash_syntax_PASS","original_owned_pre_and_post_byte_readback_PASS","original_and_frozen_owned_byte_identities_equal","old_source_and_control_prepost_PASS","conditional_core_runtime_prepost_PASS")),"Driver source execution flags required")
 return True
def software_ready(r):
 sw=read(r);d=Path(__file__).parent
 need(d.is_relative_to(S/"frozen") and Path(__file__).resolve()==Path(__file__),"Production uses actual accepted frozen driver entry only")
 source=reviewed(d);ct=read(sw["contracts"]);verify(ct["log"]);driver_software_contract(sw,ct,source)
 original_dir=Path(sw["original_source"][0]["path"]).parent
 source_binding(sw["original_source"],source,original_dir,d)
 need([metadata(original_dir/n) for n in FILES]==sw["original_metadata_before"]==sw["original_metadata_after"],"Original reviewed driver metadata drift")
 readback(sw["source_and_control_snapshot"]["actually_consumed_source_and_controls"])
 return sw,source
def contracts(out,allocation):
 d=Path(__file__).parent;need(d==P and Path(__file__).resolve()==Path(__file__),"Only reviewed pending source qualifies software")
 original=reviewed(d);before=[metadata(d/n) for n in FILES];runtime=runtime_core();old,control=fixed_state()
 frozen=S/"frozen"/("common_v5_owner_queue_finish_driver_v1_"+allocation["job_id"])/"code";frozen.mkdir(parents=True,exist_ok=False)
 for n,r in zip(FILES,original):shutil.copyfile(verify(r),frozen/n);(frozen/n).chmod(0o444)
 frozen.chmod(0o555)
 m=load_module("sealed_common_v5_ownerqueue_driver",frozen/"driver.py");need(Path(m.__file__)==frozen/"driver.py" and m.FILES==FILES and m.COUNT==COUNT,"Actual tested driver executes exact sealed OWN4");sys.modules["common_v5_owner_queue_finish_driver"]=m
 source=m.reviewed(frozen);m.source_binding(original,source,d,frozen)
 for n in FILES:
  if n.endswith(".py"):compile((frozen/n).read_bytes(),str(frozen/n),"exec",dont_inherit=True)
  if n.endswith(".sbatch"):need(subprocess.run(["bash","-n",str(frozen/n)],capture_output=True,text=True).returncode==0,"Driver launcher syntax")
 tests=load_module("common_ownerqueue_contracts",frozen/"test_driver.py")
 with(out/"contracts.txt").open("x") as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
 (out/"contracts.txt").chmod(0o444)
 cr=dump(out/"contracts.json",dict(status="PASS" if result.wasSuccessful() else "FAIL",tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),tested_source=source,log=record(out/"contracts.txt")))
 need(result.wasSuccessful() and result.testsRun==COUNT and not result.skipped,"Meaningful driver32 contracts failed")
 m.source_binding(original,source,d,frozen);after=[metadata(d/n) for n in FILES];need(before==after,"Original driver metadata prepost")
 need(old.sources()==control["old_source"],"OLD accepted Common source drift");readback(control["actually_consumed_source_and_controls"]);need(runtime_core()==runtime,"Conditional core runtime drift")
 return dump(out/"acceptance.json",dict(schema=SW_SCHEMA,status=SW_STATUS,source=source,original_source=original,original_metadata_before=before,original_metadata_after=after,contracts=cr,entry=source[0],CPU_launcher=source[2],allocation=allocation,old_common_software=COMMON_SW,root_preflight=PREFLIGHT,current_controller=CONTROLLER,actual_full_cost=COST,source_and_control_snapshot=control,conditional_core_runtime=runtime,all_owned_python_compile_PASS=True,all_launchers_bash_syntax_PASS=True,original_owned_pre_and_post_byte_readback_PASS=True,original_and_frozen_owned_byte_identities_equal=True,old_source_and_control_prepost_PASS=True,conditional_core_runtime_prepost_PASS=True,scientific_finish_executed=False,old58_rerun=False,no_GPU_submission=True,ACTIVE_changed=False))
def finish(args,out,allocation):
 swr=record(args.software_acceptance);need(swr["sha256"]==args.software_sha256,"Actual driver software CLI pin")
 sw,source=software_ready(swr);runtime=runtime_core();m,control=fixed_state()
 own_before=reviewed(Path(__file__).parent)
 driver_control=out/"owner_queue_driver_control";driver_control.mkdir()
 proof,derived=observe_queue(driver_control)
 # The actual user query and readonly DERIVED_TARGET_ONLY proof precede invocation of old finish.
 proxy=QueueProxy(subprocess,proof,derived)
 oldargs=argparse.Namespace(preflight=PREFLIGHT["path"],preflight_sha256=PREFLIGHT["sha256"],submission=CONTROLLER["path"],submission_sha256=CONTROLLER["sha256"])
 def oldtyped(e):
  p=out/"typed_incomplete.json"
  if not p.exists():m.dump(p,dict(status="COMMON_SUCCESSOR_TYPED_INCOMPLETE",stage="finish",reason_type=type(e).__name__,reason=str(e),no_automatic_retry=True,no_promotion=True,existing_files=[str(p) for p in out.rglob("*") if p.is_file()]))
 primary=with_old_finish(m,proxy,oldargs,out,oldtyped)
 need(proxy.calls==1 and m.subprocess is subprocess,"Old finish exact target query was intercepted once and restored")
 primary_doc=m.read(m.verify(primary,True))
 need(primary_doc["status"]=="FORMAL_COMMON_RAW_CONTENT_INDEPENDENT_AND112_ACCEPTED_COMPUTATIONAL_ONLY" and primary_doc["source"]==control["old_source"] and primary_doc["preflight"]==PREFLIGHT and primary_doc["root_submission"]==CONTROLLER,"Actual unchanged old Common primary acceptance differs")
 sq=out/"squeue.txt";need(sq.is_file() and sq.read_text()=="","Old squeue.txt must contain only derived target-empty text")
 derived_file=record(sq)
 need(reviewed(Path(__file__).parent)==own_before==source and m.sources()==control["old_source"],"Executing driver/OLD source prepost")
 readback(control["actually_consumed_source_and_controls"]);verify_queue_proof(proof,derived);need(runtime_core()==runtime,"Conditional core runtime prepost")
 return dump(driver_control/"driver_execution_acceptance.json",dict(schema="common-v5-owner-queue-finish-driver-execution.v1",status=EXEC_STATUS,source=source,software_acceptance=swr,old_common_software=COMMON_SW,old_common_entry=control["old_source"]["successor"][0],old_common_source=control["old_source"],actual_full_cost=COST,root_preflight=PREFLIGHT,current_controller=CONTROLLER,primary_common_acceptance=primary,target_queue_proof=proof,old_squeue_txt=derived_file,old_squeue_txt_role="DERIVED_TARGET_ONLY_NOT_ORIGINAL_SQUEUE_J_REPLY",original_target_query_executed=False,exact_target_interceptions=proxy.calls,module_local_subprocess_restored=True,stdlib_subprocess_unmodified=True,source_and_control_snapshot=control,conditional_core_runtime=runtime,source_control_runtime_prepost_PASS=True,allocation=allocation,new_neural_or_GPU_execution=False,old58_rerun=False,primary_common_acceptance_rewritten=False,ACTIVE_changed=False,whole_final_restore_accepted=False))
def main():
 p=argparse.ArgumentParser();sp=p.add_subparsers(dest="mode",required=True)
 a=sp.add_parser("contracts");a.add_argument("--out",required=True)
 a=sp.add_parser("finish")
 for key in ("software-acceptance","software-sha256","out"):a.add_argument("--"+key,required=True)
 args=p.parse_args();allocation=cpu(args.mode=="finish");out=path(args.out);out.mkdir(parents=True,exist_ok=False)
 try:
  rr=contracts(out,allocation) if args.mode=="contracts" else finish(args,out,allocation);print(json.dumps(rr))
 except Exception as e:
  control=out/"owner_queue_driver_control" if (out/"owner_queue_driver_control").is_dir() else out
  if not(control/"driver_typed_incomplete.json").exists():dump(control/"driver_typed_incomplete.json",dict(status="COMMON_V5_OWNER_QUEUE_DRIVER_TYPED_INCOMPLETE",mode=args.mode,reason_type=type(e).__name__,reason=str(e),no_automatic_retry=True,no_scientific_promotion=True,source_or_old_acceptance_not_rewritten=True))
  raise
if __name__=="__main__":main()

