#!/usr/bin/env python3
"""UNBOUND V3 Source-only real-StrictIndex engineering control; no execution yet."""
import os,sys,stat,re,time,json,subprocess,importlib.util,builtins,contextlib,base64,io
from pathlib import Path
SOURCE_SPEC = ROOT_BIND_EXISTING_17848_SOFTWARE_HISTORICAL7_AND_PLANNED_V3_PATHS
SPEC=dict(SOURCE_SPEC)
R=Path("/lustre/users/u21111210118/projects/test9")
S=R/"steps/24_benchmark_delivery"
NATIVE_KEYS={"path","bytes","inode","mtime_ns","ctime_ns","mode","dev","nlink","uid","gid"}
SOURCE_SPEC_KEYS={"schema","job_name","run_prefix","proof_prefix","readiness_prefix","tmp_prefix",
 "shell_header","log_prefix","primary_directory","Human_path","script_path","proposal_path","proposal_handoff_path","proposal_directory","Human_readonly_path",
 "pair_source_readonly","pair_source_readonly_schema","pair_source_readonly_directory_metadata",
 "protected_terminal","protected_terminal_directory_metadata","protected_terminal_schema","protected_terminal_status",
 "Core_metadata","Common_metadata","source44","source44_metadata","source_directories",
 "software","software_contracts","actual_source_software_count","historical_software","current_software"}
REQUEST_KEYS={"schema","exact_sbatch_argv","Human_after","Human_readonly","Human_readonly_schema","Human_readonly_directory_after",
 "script_after","proposal_after","proposal_handoff_after","proposal_directory_after",
 "Root_whole_Human_STATIC_PASS","Root_and_two_whole_Human_STATIC_PASS",
 "whole_script_fence_equality_PASS","actual_inputs"}
REQUEST_SCHEMA="root-source-only-real-index-primary-request.v3"
HRO_SCHEMA="root-source-only-real-index-compatibility-human-metadata-readonly-seal.v3"
PAIR_SCHEMA="root-finite-publisher-v6-and-source-compatibility-v3-interim-pair-source-readonly-seal.v1"
SUBMIT_SCHEMA="root-source-only-real-index-primary-submit.v3"
V3_C=S/"submissions/root_final_source_compatibility_from17848_v3_primary_claim"
RUNTIME_KEYS={"publisher_terminal","publisher_terminal_schema","publisher_terminal_PASS_field",
 "publisher_terminal_control_field","publisher_terminal_RAW_field","publisher_native_table_fields",
 "publisher_directory_table_fields","publisher_native_extra","publisher_directory_extra",
 "publisher_control","publisher_control_preflight_field",
 "publisher_preflight","publisher_preflight_schema","binding_field","projection_field",
 "publisher_qualification_evidence_field"}

MAX_CONTROL=20*1024*1024
MAX_SOURCE_CLOSURE=100*1024*1024
MAX_OPERATIONAL=32*1024*1024
MAX_SELF=2*1024*1024
CORE=R/"env/core/bin/python"
CORE_REAL=R/"env/core/bin/python3.11"
CORE_BYTES=25916456
CORE_SHA="76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a"
COMMON=R/"source/rebuild/benchmark_common_review.py"
RAW_OS_OPEN=os.open; RAW_OPEN=builtins.open
RAW_LSTAT=os.lstat; RAW_STAT=os.stat; RAW_READLINK=os.readlink
RAW_PATH_OPEN=Path.open; RAW_PATH_READ_BYTES=Path.read_bytes
RAW_PATH_STAT=Path.stat; RAW_PATH_LSTAT=Path.lstat; RAW_PATH_RESOLVE=Path.resolve
RAW_PATH_READLINK=Path.readlink
RAW_IO_OPEN=io.open;RAW_LISTDIR=os.listdir;RAW_SCANDIR=os.scandir;RAW_ITERDIR=Path.iterdir
def need(v,m):
 if not v:raise ValueError(m)
def pairs(items):
 d={}
 for k,v in items:
  need(k not in d,"Duplicate JSON key");d[k]=v
 return d
def nonfinite(x):raise ValueError("Nonfinite JSON")
def exact(a,b):
 return json.dumps(a,sort_keys=True,separators=(",",":"),allow_nan=False)==json.dumps(b,sort_keys=True,separators=(",",":"),allow_nan=False)
def parse(raw):return json.loads(raw,object_pairs_hook=pairs,parse_constant=nonfinite)
def canonical_names(names):
 need(type(names)is list and all(type(x)is str and x not in("","..",".")and Path(x).name==x for x in names)
  and len(names)==len(set(names)),"Directory universe must be a duplicate-free string-name list")
 return sorted(names)
def lexical(p):
 raw=os.fspath(p)
 need(type(raw)is str and raw.startswith("/")and(raw=="/"or all(x not in("","..",".")for x in raw.split("/")[1:])),"Absolute exact lexical path")
 return Path(raw)
def md(p,fd=None):
 p=lexical(p);z=RAW_LSTAT(str(p))if fd is None else os.fstat(fd)
 return dict(path=str(p),bytes=z.st_size,inode=z.st_ino,mtime_ns=z.st_mtime_ns,ctime_ns=z.st_ctime_ns,
  mode=z.st_mode,dev=z.st_dev,nlink=z.st_nlink,uid=z.st_uid,gid=z.st_gid)
def mshape(z):
 need(type(z)is dict and set(z)==NATIVE_KEYS and type(z["path"])is str
  and all(type(z[k])is int and z[k]>=0 for k in NATIVE_KEYS-{"path"}),"Exact native Python integers")
 lexical(z["path"]);return z
def rid(r):
 need(type(r)is dict and set(r)=={"path","bytes","sha256"}and type(r["bytes"])is int
  and r["bytes"]>=0 and re.fullmatch("[0-9a-f]{64}",r.get("sha256","")),"Full three-field receipt")
 lexical(r["path"]);return(r["path"],r["bytes"],r["sha256"])
def fingerprint(r):rid(r);return(r["bytes"],r["sha256"])
def select(obj,field):
 need(type(field)is list and all(type(x)is str for x in field),"Explicit exact field path")
 for x in field:obj=obj[int(x)]if type(obj)is list else obj[x]
 return obj
def scheduler_fields(raw):
 need(type(raw)is str and raw.strip(),"Whole current scheduler record")
 fields={}
 for token in raw.split():
  need("="in token,"Malformed current scheduler field")
  k,v=token.split("=",1)
  need(re.fullmatch(r"[A-Za-z][A-Za-z0-9_/]*",k)and k not in fields,"Unknown or duplicate scheduler field")
  fields[k]=v
 return fields
def tres_shape(raw,actual=False):
 need(type(raw)is str,"Scheduler TRES string")
 need(raw not in("","(null)","N/A","None")or not actual,"Actual TRES unavailable")
 if raw in("","(null)","N/A","None"):return {}
 found={}
 for token in raw.split(","):
  need(token and token==token.strip(),"Malformed TRES token")
  if "="in token:k,v=token.split("=",1)
  else:
   match=re.fullmatch(r"(.+):([0-9]+)",token)
   need(match is not None,"Malformed TRES key/value")
   k,v=match.groups()
  need(k and v and k not in found,"Duplicate or empty TRES key/value")
  if "gpu"in k.lower():
   need(re.fullmatch(r"(?:gpu|gres/gpu|gres:gpu)(?::[A-Za-z0-9_.-]+)?",k,re.I)is not None
    and v.isdecimal()and int(v)==0,"Every known GPU namespace must be decimal zero; unknown GPU namespace denied")
  if k in("cpu","node"):need(v=="1","Every present CPU/node TRES must be one")
  found[k]=v
 if actual:need(found.get("cpu")=="1","Actual allocation TRES CPU1")
 return found
def gpu_zero(fields):
 allocations=[]
 scalar_names=("Gres","GRES","GresDetail","GresUsed")
 for name in fields:
  need("gpu"not in name.lower()or name in scalar_names,"Unknown GPU-containing scheduler FIELD name denied")
  if "tres"not in name.lower():continue
  parsed=tres_shape(fields[name],actual=name in("AllocTRES","TRES"))
  if name in("AllocTRES","TRES"):allocations.append(parsed)
 need(allocations and all(z.get("cpu")=="1"and z.get("node","1")=="1"for z in allocations),"Actual CPU1/node1 allocation namespace required")
 for name in scalar_names:
  raw=fields.get(name,"(null)")
  if raw in("(null)","N/A","None",""):continue
  if "gpu"in raw.lower():tres_shape(raw)
def gpu_environment():
 for name in("SLURM_JOB_GPUS","SLURM_STEP_GPUS"):
  need(os.environ.get(name,"")=="","Assigned GPU IDs must be absent or empty, including ID zero")
 for name in("SLURM_GPUS","SLURM_GPUS_ON_NODE","SLURM_GPUS_PER_NODE","SLURM_GPUS_PER_TASK","SLURM_GPUS_PER_SOCKET"):
  raw=os.environ.get(name,"")
  need(raw==""or raw.isdecimal()and int(raw)==0,"Every GPU count environment value must be absent, empty or decimal zero")
def live_current():
 need(os.environ.get("SLURM_JOB_ID","").isdigit(),"Actual Slurm ID required")
 jid=os.environ["SLURM_JOB_ID"];gpu_environment();readiness_deadline=time.monotonic()+60
 need(os.environ.get("CUDA_VISIBLE_DEVICES")==""and os.environ.get("JAX_PLATFORMS")=="cpu"
  and os.environ.get("PYTHONNOUSERSITE")=="1"and os.environ.get("PYTHONDONTWRITEBYTECODE")=="1"
  and "PYTHONPATH"not in os.environ and all(os.environ.get(k)=="1"for k in
   ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS")),"Actual isolated CPU environment")
 def raw_bytes(value):
  if value is None:return b""
  return value.encode("utf-8")if type(value)is str else value
 def rpc(argv):
  started=time.monotonic()
  try:
   remaining=readiness_deadline-time.monotonic();need(remaining>0,"Readiness deadline exhausted before RPC")
   q=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=min(5,remaining),
    env=dict(os.environ,TZ="UTC",SLURM_TIME_FORMAT="standard"))
   out,err=q.stdout,q.stderr;rc=q.returncode;timed=False;failure=None
  except subprocess.TimeoutExpired as e:
   out,err=raw_bytes(e.stdout),raw_bytes(e.stderr);rc=None;timed=True;failure="TimeoutExpired"
  except OSError as e:
   out,err=b"",str(e).encode("utf-8");rc=None;timed=False;failure=type(e).__name__
  item=dict(argv=argv,returncode=rc,stdout=out.decode("utf-8",errors="replace"),
   stderr=err.decode("utf-8",errors="replace"),stdout_base64=base64.b64encode(out).decode("ascii"),
   stderr_base64=base64.b64encode(err).decode("ascii"),timed_out=timed,error_type=failure,
   elapsed_seconds=time.monotonic()-started)
  return item
 start=time.monotonic()
 argv=["scontrol","show","job",jid,"-o"]
 sc=rpc(argv);READINESS["current_scontrol"]=sc
 need(sc["returncode"]==0 and not sc["timed_out"]and base64.b64decode(sc["stderr_base64"])==b"",
  "Actual current Scontrol rc0; timeout/null/error fails without another query")
 f=scheduler_fields(sc["stdout"])
 need(f.get("JobId")==jid and f.get("JobState")=="RUNNING"and f.get("JobName")==SPEC["job_name"]
  and f.get("NumCPUs")=="1"and f.get("NumTasks")=="1"and f.get("NumNodes")=="1"and f.get("CPUs/Task")=="1"
  and f.get("Account")=="u21111210118"and f.get("UserId","").split("(")[0]=="u21111210118"
  and f.get("Partition")=="organ"and f.get("QOS")=="normal"and f.get("WorkDir")==str(S)
  and f.get("TimeLimit")=="00:30:00"and f.get("MinMemoryNode")in("16G","16384M"),"Exact current CPU1/task1/node1/16G30/organ profile")
 gpu_zero(f)
 # Every present allocation/request TRES namespace was independently validated above.
 chosen=None
 for n in range(30):
  if time.monotonic()>=readiness_deadline:break
  argv=["sacct","-X","-n","-P","-j",jid,"--format=JobIDRaw,State,AllocTRES,User,Account,Partition"]
  item=rpc(argv);READINESS["attempts"].append(item)
  need(item["returncode"]==0 and not item["timed_out"]and base64.b64decode(item["stderr_base64"])==b"",
   "Actual current Sacct RPC must succeed; null/error fails without another query")
  rows=[x.split("|")for x in item["stdout"].splitlines()if x]
  rows=[x for x in rows if x and x[0]==jid]
  if len(rows)==1 and len(rows[0])==6 and rows[0][1]=="RUNNING":
   row=rows[0];need(row[3:]==["u21111210118","u21111210118","organ"],"Current own accounting row")
   tres=tres_shape(row[2],actual=True);need(tres.get("node","1")=="1","Current accounting node1")
   chosen=row;break
  remaining=readiness_deadline-time.monotonic()
  if remaining>0:time.sleep(min(1,remaining))
 need(chosen is not None,"No unique exact current RUNNING six-column row before hashing/import")
 READINESS.update(selected_numeric_row=chosen,selected_attempt=len(READINESS["attempts"]),guard_succeeded=True)
 return jid,READINESS

need(type(SOURCE_SPEC)is dict and set(SOURCE_SPEC)==SOURCE_SPEC_KEYS and SOURCE_SPEC["schema"]=="root-source-only-real-strict-index-control.v3","Closed existing-input/planned-path Source SPEC; no future publisher tuples")
need(type(SOURCE_SPEC["actual_source_software_count"])is int and SOURCE_SPEC["actual_source_software_count"]==237,"Only actual qualified purpose-fixed F17848 software profile")
HISTORICAL_KEYS={"software","software_contracts","Source7_human_readonly","Source7_human_readonly_directory_metadata",
 "Source7_human_readonly_schema","Source7_metadata_original","Source7_names_original"}
CURRENT_KEYS={"terminal","terminal_directory_metadata","terminal_schema","terminal_status","Root_execution_control","source_directory_metadata"}
HIST=SOURCE_SPEC["historical_software"];CUR=SOURCE_SPEC["current_software"]
need(type(HIST)is dict and set(HIST)==HISTORICAL_KEYS and type(CUR)is dict and set(CUR)==CURRENT_KEYS,"Two exact existing-input provenance profiles")
need(type(HIST["Source7_metadata_original"])is dict and type(HIST["Source7_names_original"])is dict
 and set(HIST["Source7_metadata_original"])==set(HIST["Source7_names_original"])and len(HIST["Source7_metadata_original"])==7,
 "Historical seven-directory authority stays exact and separate")
need(type(CUR["source_directory_metadata"])is dict and set(CUR["source_directory_metadata"])==set(SOURCE_SPEC["source_directories"]),
 "Separate current code-parent Native vector; no historical seven replacement")
need(HIST["Source7_human_readonly"]["metadata"]["path"]==str(S/"submissions/root_final_source_index_compatibility_v2_human_metadata_readonly_seal/receipt.json")
 and CUR["terminal"]["metadata"]["path"]==str(S/"submissions/final_composer17848_actual_terminal_metadata_readonly_seal/receipt.json")
 and CUR["Root_execution_control"]["receipt"]["path"]==str(S/"submissions/root_final_composer_v7_fix10_software_execution_control_17848/execution_control.json")
 and SOURCE_SPEC["software"]["receipt"]["path"]==str(S/"runs/final_composer_operational_provenance_contracts_17848/acceptance.json")
 and SOURCE_SPEC["software_contracts"]["receipt"]["path"]==str(S/"runs/final_composer_operational_provenance_contracts_17848/contracts.json"),
 "Exact already-qualified historical7/current17848 controls only; no generic own-control or future receipt")
need(SOURCE_SPEC["primary_directory"]==str(V3_C)and SOURCE_SPEC["script_path"]==str(V3_C/"compatibility_job.sh")
 and SOURCE_SPEC["job_name"]=="test9_final_source_compatibility_v3"
 and SOURCE_SPEC["proposal_directory"]==str(S/"pending/root_final_source_compatibility_from17848_v3")
 and SOURCE_SPEC["proposal_path"]==str(S/"pending/root_final_source_compatibility_from17848_v3/finite_source_compatibility_control.py")
 and SOURCE_SPEC["proposal_handoff_path"]==str(S/"pending/root_final_source_compatibility_from17848_v3/HANDOFF.md")
 and SOURCE_SPEC["Human_path"]==str(S/"handoffs/ROOT_FIXED_FINAL_SOURCE_COMPATIBILITY_FROM17848_REV3_20261017.md"),
 "Literal distinct V3 Source4 and one future mutable primary")
need(SOURCE_SPEC["run_prefix"]=="final_source_compatibility_v3_"and SOURCE_SPEC["log_prefix"]=="final_source_compatibility_v3_"
 and SOURCE_SPEC["proof_prefix"]=="root_final_source_compatibility_v3_execution_control_"
 and SOURCE_SPEC["readiness_prefix"]=="root_final_source_compatibility_v3_readiness_"
 and SOURCE_SPEC["tmp_prefix"]=="root_final_source_compatibility_v3_",
 "Exact distinct prospective owned runtime namespaces; actual numeric job ID comes only from current CPU")
need(str(V3_C)not in HIST["Source7_metadata_original"]and str(V3_C)not in HIST["Source7_names_original"]
 and str(V3_C)not in CUR["source_directory_metadata"]and str(V3_C)not in SPEC["source_directories"],
 "The one primary directory is transaction history, never Source7/current-code immutable custody")
SPEC["protected_directory_children"]={}
SPEC["protected_extra_metadata"]=[]
SPEC["source_directories"]={p:canonical_names(names)for p,names in SOURCE_SPEC["source_directories"].items()}
JID=os.environ.get("SLURM_JOB_ID","")
need(JID.isdigit(),"Numeric actual Slurm ID before any own proof creation")
READINESS=dict(current_scontrol=None,attempts=[],selected_numeric_row=None,selected_attempt=None,guard_succeeded=False)
# Hashing/project imports are granted only after live_current returns successfully.
ORIGINAL={};READ_PINS={};NEW_FILES={};NEW_DIRS={};EVENTS={};DENIALS=[];PRIMARY_FINAL={}
PHASE="actual_current_CPU_guard"
RUN=S/"runs"/(SPEC["run_prefix"]+JID)
PD=S/"submissions"/(SPEC["proof_prefix"]+JID)
RD=S/"submissions"/(SPEC["readiness_prefix"]+JID)
TMP=S/"tmp"/(SPEC["tmp_prefix"]+JID)
ROOT=RUN/"engineering_inputs";OUT=ROOT/"source_only_new_outputs"
SHARED=[S/"submissions",S/"runs",S/"tmp",S/"frozen"]
SHARED_BEFORE={str(p):md(p)for p in SHARED}
need(all(stat.S_ISDIR(z["mode"])for z in SHARED_BEFORE.values()),"Original shared parents must be nonlink directories")
SHARED_AFTER={};SHARED_EVENTS=[]
SHARED_NAMES={str(p):sorted(os.listdir(p))for p in SHARED}
SHARED_ADDITIONS={str(S/"runs"):{RUN.name},str(S/"submissions"):{PD.name,RD.name},
 str(S/"tmp"):{TMP.name},str(S/"frozen"):set()}
def enroll(z):
 mshape(z);p=z["path"]
 need(p not in ORIGINAL or ORIGINAL[p]==z,"Original baseline must never refresh")
 need(md(p)==z,"Original native differs before first IO")
 ORIGINAL[p]=z;return z
def regular(z,readonly=True):
 need(stat.S_ISREG(z["mode"])and z["nlink"]==1 and(not readonly or not(z["mode"]&0o222)),"Regular readonly single-link file")
def check_names():
 for p,names in SPEC["protected_directory_children"].items():need(sorted(os.listdir(p))==names,"Original fixed universe changed")
 for p,names in HIST["Source7_names_original"].items():need(sorted(os.listdir(p))==canonical_names(names),"Historical Source7 original universe changed")
 for p,names in SPEC["source_directories"].items():need(sorted(os.listdir(p))==names,"Exact current Source directory universe changed")
 if PRIMARY_FINAL:need(sorted(os.listdir(V3_C))==PRIMARY_FINAL["names"],"Actual sealed six-file primary universe changed")
 for p,event in EVENTS.items():need(sorted(os.listdir(p))==event["children"],"Exact owned sealed directory universe changed")
 for p,old in SHARED_NAMES.items():need(sorted(os.listdir(p))==sorted(set(old)|SHARED_ADDITIONS[p]),"Shared exact original plus owned additions changed")
def capture_shared_after(additions):
 need(not SHARED_AFTER and additions==SHARED_ADDITIONS,"Only one saved shared-parent after event")
 for p,before in SHARED_BEFORE.items():
  after=md(p);added=additions[p];old=SHARED_NAMES[p]
  need(sorted(os.listdir(p))==sorted(set(old)|added),"Only exact own top-level additions")
  if not added:need(after==before,"Zero-addition frozen parent must retain all ten original native fields")
  else:
   need(all(after[k]==before[k]for k in NATIVE_KEYS-{"bytes","mtime_ns","ctime_ns","nlink"})
    and after["nlink"]==before["nlink"]+len(added),"Exact original identity/permissions/link transition")
  SHARED_AFTER[p]=after
  SHARED_EVENTS.append(dict(path=p,before=before,after=after,names_before=old,
   declared_added_children=sorted(added),names_after=sorted(set(old)|added)))
def check_native():
 # EVERY universe operation precedes this final native-only union; no baseline refresh.
 check_names()
 for p,z in ORIGINAL.items():need(md(p)==z,"Original saved native union changed")
 for p,z in NEW_FILES.items():need(md(p)==z,"New file original baseline changed")
 for p,z in NEW_DIRS.items():need(md(p)==EVENTS[p]["after"]if p in EVENTS else md(p)==z,"New directory original/event native changed")
 need(set(SHARED_AFTER)==set(SHARED_BEFORE),"One original shared-parent after vector must exist")
 for p,z in SHARED_AFTER.items():need(md(p)==z,"Shared full saved after native changed")
 if PRIMARY_FINAL:need(PRIMARY_FINAL["source_history_join_verified"]is True and md(V3_C)==PRIMARY_FINAL["metadata"],"Separate full primary transaction Native; never Original refresh")
def check_original_only():
 for p,z in ORIGINAL.items():need(md(p)==z,"Original saved native union changed")
 for p,z in SHARED_AFTER.items():need(md(p)==z,"Saved original shared after-event native changed")
 if PRIMARY_FINAL:need(PRIMARY_FINAL["source_history_join_verified"]is True and md(V3_C)==PRIMARY_FINAL["metadata"],"Joined primary transaction Native remains separate from immutable Source pool")
def raw_file(p,limit):
 p=lexical(p);need(p.is_relative_to(R),"Finite declared own-file path must stay inside authority")
 for parent in p.parents:
  if parent==R.parent:break
  need(stat.S_ISDIR(RAW_LSTAT(str(parent)).st_mode),"Own input ancestor must be an existing nonlink directory")
 if PRIMARY_FINAL:need(md(V3_C)==PRIMARY_FINAL["metadata"],"Typed sealed primary transaction Native stable before input payload")
 z=md(p);regular(z,p!=CORE_REAL);need(z["bytes"]<=limit,"Explicit own-input bound")
 need(str(p)in ORIGINAL and ORIGINAL[str(p)]==z or str(p)in NEW_FILES and NEW_FILES[str(p)]==z,"File enrolled before any read")
 fd=RAW_OS_OPEN(str(p),os.O_RDONLY|getattr(os,"O_NOFOLLOW",0))
 with os.fdopen(fd,"rb")as stream:
  need(md(p,stream.fileno())==z and md(p)==z,"Whole Native10 FD/path binding before payload")
  raw=stream.read(limit+1)
  need(md(p,stream.fileno())==z and md(p)==z,"Whole Native10 FD/path binding after payload")
 need(len(raw)==z["bytes"]and md(p)==z,"Whole own-input bytes/native stable")
 if PRIMARY_FINAL:need(md(V3_C)==PRIMARY_FINAL["metadata"],"Typed sealed primary transaction Native stable after input payload")
 return raw
def payload_limit(r):
 rid(r)
 if r["path"]==str(CORE_REAL):return CORE_BYTES
 if "binding"in globals():
  for original,limit in [(binding["producer"]["source_closure"],MAX_SOURCE_CLOSURE),(binding["operational_source_provenance"],MAX_OPERATIONAL)]:
   if rid(r)==rid(original):return limit
   for row in binding["transport_aliases"]:
    if row["original"]==original and rid(r)==rid(row["archived"]):return limit
 if r["path"]in(SPEC["Human_path"],SPEC["script_path"],SPEC["proposal_path"]):return MAX_SELF
 if "publisher_terminal"in SPEC and r["path"]==SPEC["publisher_terminal"]["metadata"]["path"]:return 64*1024*1024
 return MAX_CONTROL
def hashed(p,limit):
 raw=raw_file(p,limit);r=dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest());READ_PINS[rid(r)]=r;return r,raw
def control(entry,limit=MAX_CONTROL):
 need(type(entry)is dict and set(entry)=={"receipt","metadata"},"Exact known own control receipt/native")
 r=entry["receipt"];rid(r);z=enroll(entry["metadata"]);need(z["path"]==r["path"]and z["bytes"]==r["bytes"],"Control native binding")
 a,raw=hashed(r["path"],limit);need(a==r,"Actual own control full bytes changed");return parse(raw)

def own_directory(z,names):
 enroll(z);need(stat.S_ISDIR(z["mode"])and stat.S_IMODE(z["mode"])==0o555 and z["nlink"]>=2,"Exact readonly own-control directory")
 need(sorted(os.listdir(z["path"]))==sorted(names),"Exact own-control directory universe")
 SPEC["protected_directory_children"][z["path"]]=sorted(names)
 return z

def first_pin_control(entry,purpose,limit=MAX_CONTROL):
 need(type(entry)is dict and set(entry)=={"metadata"},"Only closed unknown-own-SHA metadata authority")
 z=entry["metadata"];enroll(z);regular(z)
 allowed={SOURCE_SPEC["protected_terminal"]["metadata"]["path"],SOURCE_SPEC["Human_readonly_path"],SOURCE_SPEC["pair_source_readonly"]["metadata"]["path"],
  HIST["Source7_human_readonly"]["metadata"]["path"],CUR["terminal"]["metadata"]["path"]}
 if "publisher_terminal"in SPEC:allowed.add(SPEC["publisher_terminal"]["metadata"]["path"])
 need(z["path"]in allowed and purpose in("QUALIFIED_ST47","OWN_HRO","QUALIFIED_PUBLISHER_TRO","OWN_PAIR_SOURCE_RO","HISTORICAL_SOURCE7_HRO","QUALIFIED_CURRENT_SW47"),
  "Unknown-own-SHA authority is only literal historical/current software controls, own pair/HRO, or qualified publisher TRO")
 r,raw=hashed(z["path"],limit);return parse(raw),r

def add_dir(p,mode=0o700):
 p=lexical(p);need(not p.exists(),"New exclusive directory must be absent");os.mkdir(str(p),mode)
 z=md(p);need(stat.S_ISDIR(z["mode"])and z["nlink"]==2 and stat.S_IMODE(z["mode"])==mode,"New exact directory")
 fd=RAW_OS_OPEN(str(p),os.O_RDONLY|getattr(os,"O_DIRECTORY",0)|getattr(os,"O_NOFOLLOW",0))
 try:need(md(p,fd)==z and sorted(RAW_LISTDIR(str(p)))==[]and md(p,fd)==z and md(p)==z,"Exclusive empty directory full Native10 FD/path identity")
 finally:os.close(fd)
 NEW_DIRS[str(p)]=z;return p
def parents(p):
 for q in reversed(lexical(p).parents):
  if q==RUN or q==PD or q==ROOT or str(q)in NEW_DIRS:break
 for q in [lexical(p).parent]+list(lexical(p).parent.parents):
  if q==RUN or q==PD or q==ROOT:break
  need(q.is_relative_to(RUN)or q.is_relative_to(PD),"Owned output containment")
 def create(q):
  if str(q)in NEW_DIRS:return
  if q!=RUN and q!=PD:create(q.parent)
  add_dir(q)
 create(lexical(p).parent)
def durable(p,raw,mode=0o444):
 p=lexical(p);need(p.is_relative_to(RUN)or p.is_relative_to(PD)or p.is_relative_to(RD),"Only owned new outputs")
 parents(p)if not p.is_relative_to(RD)else None
 fd=RAW_OS_OPEN(str(p),os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,"O_NOFOLLOW",0),0o600)
 with os.fdopen(fd,"wb")as stream:
  stream.write(raw);stream.flush();os.fsync(stream.fileno());os.fchmod(stream.fileno(),mode);os.fsync(stream.fileno())
 z=md(p);regular(z);NEW_FILES[str(p)]=z
 a,observed=hashed(p,max(MAX_CONTROL,len(raw)));need(observed==raw,"Durable output full readback")
 return a
def dump(p,obj,limit=MAX_CONTROL):
 raw=(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode()
 need(len(raw)<=limit,"Explicit control size bound before writer");return durable(p,raw)
def seal_dir(p):
 p=lexical(p);before=md(p);need(str(p)in NEW_DIRS,"Owned original directory")
 initial=NEW_DIRS[str(p)]
 direct_dirs=[z for path,z in NEW_DIRS.items()if Path(path).parent==p]
 need(all(before[k]==initial[k]for k in NATIVE_KEYS-{"bytes","mtime_ns","ctime_ns","nlink"})
  and before["nlink"]==initial["nlink"]+len(direct_dirs),"Only declared own-child fill may change original directory fields")
 fd=RAW_OS_OPEN(str(p),os.O_RDONLY|getattr(os,"O_DIRECTORY",0)|getattr(os,"O_NOFOLLOW",0))
 try:
  need(md(p,fd)==before and md(p)==before,"Whole directory Native10 FD/path before seal")
  os.fchmod(fd,0o555);os.fsync(fd)
  need(md(p,fd)==md(p),"Whole directory Native10 FD/path after seal")
 finally:os.close(fd)
 after=md(p);need(all(after[k]==before[k]for k in NATIVE_KEYS-{"mode","ctime_ns"}),"Directory seal changed nonpermission fields")
 expected_names=sorted({Path(x).name for x in list(NEW_FILES)+list(NEW_DIRS)if str(Path(x).parent)==str(p)})
 need(sorted(os.listdir(p))==expected_names,"Own directory changed outside exact recorded children")
 EVENTS[str(p)]=dict(original_creation=NEW_DIRS[str(p)],before_seal=before,after=after,children=expected_names)
def core_end():
 logical,real=SPEC["Core_metadata"];need(logical["path"]==str(CORE)and real["path"]==str(CORE_REAL),"Exact Core2 routes")
 need(stat.S_ISLNK(logical["mode"])and logical["bytes"]==10 and logical["nlink"]==1 and stat.S_ISREG(real["mode"])
  and real["bytes"]==CORE_BYTES and real["nlink"]==1,"Exact native-only Core2 exceptions")
 need(md(CORE)==logical and md(CORE_REAL)==real and RAW_READLINK(str(CORE))=="python3.11","Exact Core native/link")
 r,_=hashed(CORE_REAL,CORE_BYTES);need(fingerprint(r)==(CORE_BYTES,CORE_SHA),"Actual Core whole bytes changed")
def primary_source_history(value,script):
 keys={"before","after","children_before","children_after","unchanged_identity_fields","permitted_fill_metadata_fields"}
 need(type(value)is dict and set(value)==keys,"Closed immutable Source-creation history for only V3 primary")
 before=mshape(value["before"]);after=mshape(value["after"])
 need(before["path"]==after["path"]==str(V3_C)and stat.S_ISDIR(before["mode"])
  and stat.S_IMODE(before["mode"])==stat.S_IMODE(after["mode"])==0o775 and before["nlink"]==after["nlink"]==2,
  "V3 primary Source creation directory is ordinary775")
 fixed=["path","inode","dev","uid","gid","mode","nlink"]
 need(value["unchanged_identity_fields"]==fixed and value["permitted_fill_metadata_fields"]==["bytes","mtime_ns","ctime_ns"]
  and all(before[k]==after[k]for k in fixed)
  and value["children_before"]==[]and value["children_after"]==["compatibility_job.sh"]
  and script["path"]==str(V3_C/"compatibility_job.sh"),"Exact exclusive empty-to-W-only Source history")
 return after
def primary_postpublisher_fill(value,source_after,final):
 keys={"before","filled_before_seal","children_before","children_after","unchanged_identity_fields","permitted_fill_metadata_fields"}
 need(type(value)is dict and set(value)==keys,"Closed actual postpublisher six-file primary fill event")
 before=mshape(value["before"]);filled=mshape(value["filled_before_seal"])
 names=sorted(["compatibility_job.sh","request.json","in_progress.json","submit_receipt.json","sbatch.stdout","sbatch.stderr"])
 fixed=["path","inode","dev","uid","gid","mode","nlink"]
 need(before==source_after and filled["path"]==str(V3_C)and stat.S_IMODE(filled["mode"])==0o775
  and value["unchanged_identity_fields"]==fixed and value["permitted_fill_metadata_fields"]==["bytes","mtime_ns","ctime_ns"]
  and all(before[k]==filled[k]for k in fixed)
  and value["children_before"]==["compatibility_job.sh"]and value["children_after"]==names,
  "Exact original W-only Source history to real postpublisher six-file fill; no baseline refresh")
 need(final["path"]==filled["path"]and stat.S_IMODE(final["mode"])==0o555
  and all(final[k]==filled[k]for k in NATIVE_KEYS-{"mode","ctime_ns"}),"Only final primary mode/ctime may change at the sealed barrier")
 return value
def wait_primary():
 d=lexical(SPEC["primary_directory"]);deadline=time.monotonic()+60
 names={"compatibility_job.sh","request.json","in_progress.json","submit_receipt.json","sbatch.stdout","sbatch.stderr"}
 while time.monotonic()<deadline:
  try:
   if set(os.listdir(d))==names and stat.S_IMODE(md(d)["mode"])==0o555:break
  except FileNotFoundError:pass
  time.sleep(1)
 else:raise ValueError("Complete sealed six-file actual primary barrier absent")
 final_primary=md(d)
 PRIMARY_FINAL.update(metadata=final_primary,names=sorted(names),source_history_join_verified=False);primary={}
 for name in sorted(names):
  p=d/name;enroll(md(p));_,raw=hashed(p,MAX_SELF)
  primary[name]=parse(raw)if name.endswith(".json")else raw
 need(primary["sbatch.stdout"]==(JID+"\n").encode()and primary["sbatch.stderr"]==b"","Actual one submission raw bytes")
 sub=primary["submit_receipt.json"]
 submit_keys={"schema","actual_job_id","exact_sbatch_argv","returncode","timed_out","stdout","stderr",
  "stdout_base64","stderr_base64","timeout_seconds","execution_completed","primary_directory_input_fill_event"}
 need(type(sub)is dict and set(sub)==submit_keys and sub["schema"]==SUBMIT_SCHEMA
  and type(sub["returncode"])is int and sub["returncode"]==0 and sub["actual_job_id"]==JID
  and sub["timed_out"]is False and sub["execution_completed"]is True and type(sub["timeout_seconds"])is int and sub["timeout_seconds"]==60
  and sub["stdout"]==JID+"\n"and sub["stderr"]==""
  and base64.b64decode(sub["stdout_base64"],validate=True)==primary["sbatch.stdout"]
  and base64.b64decode(sub["stderr_base64"],validate=True)==b"","Actual one completed submission with whole raw evidence")
 req=primary["request.json"]
 need(type(req)is dict and set(req)==REQUEST_KEYS and req["schema"]==REQUEST_SCHEMA
  and req["Root_whole_Human_STATIC_PASS"]is True and req["Root_and_two_whole_Human_STATIC_PASS"]is True,"Closed post-HRO request authority")
 H=req["Human_after"];enroll(H);need(H["path"]==SPEC["Human_path"],"Exact Human")
 need(req["Human_readonly"]["metadata"]["path"]==SOURCE_SPEC["Human_readonly_path"],"Exact planned own HRO")
 own_directory(req["Human_readonly_directory_after"],["receipt.json"])
 need(req["Human_readonly_directory_after"]["path"]==str(Path(SOURCE_SPEC["Human_readonly_path"]).parent),"Exact own HRO parent")
 hro,hro_r=first_pin_control(req["Human_readonly"],"OWN_HRO")
 need(hro["schema"]==req["Human_readonly_schema"]==HRO_SCHEMA and hro["Root_and_two_whole_STATIC_PASS"]is True,"Accepted compatibility Human/script RO")
 need(hro["mutable_compatibility_primary_directory_EXCLUDED_from_immutable_custody"]is True
  and str(V3_C)not in {z["path"]for z in hro["protected_metadata_before"]}
  and str(V3_C)not in hro["protected_directory_children"]
  and hro["Source44_parent_metadata_original"]==HIST["Source7_metadata_original"]
  and hro["Source44_parent_names_original"]==HIST["Source7_names_original"]
  and hro["required_future_source_parent_binding_equality"]is True,
  "Own HRO retains exact historical seven and excludes only literal future mutable primary")
 source_primary_after=primary_source_history(hro["primary_directory_creation_metadata_HISTORY_ONLY"],req["script_after"])
 primary_postpublisher_fill(sub["primary_directory_input_fill_event"],source_primary_after,final_primary)
 PRIMARY_FINAL.update(source_history_join_verified=True,source_creation_history=hro["primary_directory_creation_metadata_HISTORY_ONLY"],
  postpublisher_fill_event=sub["primary_directory_input_fill_event"])
 need(hro["Human_after"]==H and hro["script_after"]==req["script_after"]
  and hro["source_proposal_metadata_after"]==[req["proposal_after"],req["proposal_handoff_after"],req["proposal_directory_after"]],
  "Exact own HRO Human/script/proposal native bindings")
 script=req["script_after"];enroll(script);need(script["path"]==SPEC["script_path"],"Exact sealed script")
 proposal=req["proposal_after"];enroll(proposal);need(proposal["path"]==SPEC["proposal_path"],"Exact adopted proposal")
 handoff=req["proposal_handoff_after"];enroll(handoff);need(handoff["path"]==SPEC["proposal_handoff_path"],"Exact truthful HANDOFF")
 directory=req["proposal_directory_after"];enroll(directory)
 need(directory["path"]==SPEC["proposal_directory"]and stat.S_ISDIR(directory["mode"])and stat.S_IMODE(directory["mode"])==0o555,"Exact sealed compatibility Source directory")
 need(sorted(os.listdir(directory["path"]))==["HANDOFF.md","finite_source_compatibility_control.py"],"Exact compatibility OWN2")
 own_directory(SOURCE_SPEC["pair_source_readonly_directory_metadata"],["receipt.json"])
 need(SOURCE_SPEC["pair_source_readonly_directory_metadata"]["path"]==str(Path(SOURCE_SPEC["pair_source_readonly"]["metadata"]["path"]).parent),"Exact pair SourceRO directory")
 pair_sro,pair_r=first_pin_control(SOURCE_SPEC["pair_source_readonly"],"OWN_PAIR_SOURCE_RO")
 need(str(V3_C)not in {z["path"]for z in pair_sro["protected_metadata_before"]}
  and str(V3_C)not in pair_sro["protected_directory_children"],"Pair SourceRO never freezes future mutable compatibility primary")
 need(pair_sro["schema"]==SOURCE_SPEC["pair_source_readonly_schema"]==PAIR_SCHEMA
  and pair_sro["Root_and_two_whole_STATIC_PASS"]is True and pair_sro["protected_metadata_unchanged"]is True
  and len(pair_sro["source_metadata_after"])==6 and pair_sro["source_metadata_after"][3:]==[proposal,handoff,directory],"Accepted prepublication pair SourceRO exact compatibility OWN2/P")
 _,human=hashed(H["path"],MAX_SELF);_,shell=hashed(script["path"],MAX_SELF)
 fence=chr(96)*3;text=human.decode()
 need(text.count(fence+"python\n")==1 and text.count("\n"+fence+"\n")==1,"One whole Human Python fence")
 code=text.split(fence+"python\n",1)[1].split("\n"+fence+"\n",1)[0].encode()
 need(shell==SPEC["shell_header"].encode()+code+b"\nPY\n"and req["whole_script_fence_equality_PASS"]is True,"Exact entire sealed Human/script body")
 _,source_raw=hashed(proposal["path"],MAX_SELF);hashed(handoff["path"],MAX_SELF)
 marker=b"\nSOURCE_SPEC = ROOT_BIND_EXISTING_17848_SOFTWARE_HISTORICAL7_AND_PLANNED_V3_PATHS\n"
 need(source_raw.count(marker)==1,"Exactly one anchored unbound proposal SPEC slot")
 spec_json=json.dumps(SOURCE_SPEC,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)
 expected_source=source_raw.replace(marker,b"\nSOURCE_SPEC = json.loads("+json.dumps(spec_json,ensure_ascii=True).encode()+b")\n")
 need(code+b"\n"==expected_source,"Whole bound Human equals the proposal with its one exact existing-input SPEC binding")
 argv=req["exact_sbatch_argv"]
 expected_argv=["sbatch","--parsable","--account=u21111210118","--qos=normal","--job-name="+SPEC["job_name"],
  "--cpus-per-task=1","--ntasks=1","--nodes=1","--mem=16G","--time=00:30:00","--partition=organ","--chdir="+str(S),
  "--output="+str(S/"logs"/(SPEC["log_prefix"]+"%j.out")),"--error="+str(S/"logs"/(SPEC["log_prefix"]+"%j.err")),SPEC["script_path"]]
 need(argv==expected_argv and sub["exact_sbatch_argv"]==argv,"Exact actual fifteen-argument script-file submission profile")
 need(type(req["actual_inputs"])is dict and set(req["actual_inputs"])==RUNTIME_KEYS
  and not(set(req["actual_inputs"])&set(SOURCE_SPEC)),"Only exact later actual publisher input data; no static Source override")
 SPEC.update(req["actual_inputs"])
 return req,primary,pair_sro

def preserve_failed_current_guard(original):
 # This failure scope writes only actual readiness bytes/native; no input read/hash/project import.
 need(not READINESS["guard_succeeded"]and not os.path.lexists(str(RD)),"Exclusive failed-readiness namespace")
 os.mkdir(str(RD),0o700);created=md(RD);written=[];failure_events=[]
 for p,before in SHARED_BEFORE.items():
  added={RD.name}if p==str(S/"submissions")else set();after=md(p);names=sorted(set(SHARED_NAMES[p])|added)
  need(sorted(os.listdir(p))==names,"Failed guard adds only its one exclusive RD")
  if not added:need(after==before,"Untouched shared parent retains complete original metadata")
  else:need(all(after[k]==before[k]for k in NATIVE_KEYS-{"bytes","mtime_ns","ctime_ns","nlink"})and after["nlink"]==before["nlink"]+1,"One exact failed-readiness creation event")
  failure_events.append(dict(path=p,before=before,after=after,names_before=SHARED_NAMES[p],declared_added_children=sorted(added),names_after=names))
 def put(name,data):
  p=RD/name;fd=RAW_OS_OPEN(str(p),os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,"O_NOFOLLOW",0),0o600)
  with os.fdopen(fd,"wb")as stream:
   stream.write(data);stream.flush();os.fsync(stream.fileno());os.fchmod(stream.fileno(),0o444);os.fsync(stream.fileno())
  before=md(p);need(stat.S_ISREG(before["mode"])and before["nlink"]==1,"Own failed readiness file")
  need(p.read_bytes()==data and md(p)==before,"Failed readiness raw full bytes/native")
  written.append(before)
 if READINESS["current_scontrol"]is not None:
  sc=READINESS["current_scontrol"]
  put("current_scontrol.stdout",base64.b64decode(sc["stdout_base64"]))
  put("current_scontrol.stderr",base64.b64decode(sc["stderr_base64"]))
 for n,item in enumerate(READINESS["attempts"]):
  put("sacct_%02d.stdout"%n,base64.b64decode(item["stdout_base64"]))
  put("sacct_%02d.stderr"%n,base64.b64decode(item["stderr_base64"]))
 failure=dict(schema="root-source-only-index-current-readiness-incomplete.v3",
  status="ACTUAL_CURRENT_GUARD_FAILED_RAW_PRESERVED_NO_INPUT_PERMISSION_OR_INDEX_ACCEPTANCE",
  actual_job_id=JID,readiness=READINESS,error_type=type(original).__name__,error=str(original),
  guard_succeeded=False,input_hash_or_project_import_started=False,extra_RPC_after_failure=False,
  operational_shared_parent_addition_events=failure_events,
  original_exception_preserved=True,production_package_or_scientific_restore_accepted=False)
 put("readiness_failure.json",(json.dumps(failure,indent=2,sort_keys=True,allow_nan=False)+"\n").encode())
 before_seal=md(RD);fd=RAW_OS_OPEN(str(RD),os.O_RDONLY|os.O_DIRECTORY|getattr(os,"O_NOFOLLOW",0))
 try:os.fchmod(fd,0o555);os.fsync(fd)
 finally:os.close(fd)
 after=md(RD);need(all(after[k]==before_seal[k]for k in NATIVE_KEYS-{"mode","ctime_ns"}),"Own failed-readiness seal changes only mode/ctime")
 expected=sorted(Path(z["path"]).name for z in written)
 need(sorted(os.listdir(RD))==expected,"Exact failed-readiness raw universe")
 for event in failure_events:need(sorted(os.listdir(event["path"]))==event["names_after"],"Failed-readiness final shared universe")
 for event in failure_events:need(md(event["path"])==event["after"],"Failed-readiness final original saved shared after native")
 for z in written:need(md(z["path"])==z,"Final failed-readiness original file native")
 need(md(RD)==after,"Final failed-readiness saved directory native")

try:
 JID,READINESS=live_current()
 import hashlib
 PHASE="fixed_input_and_primary_authentication"
 add_dir(RD);add_dir(RUN);add_dir(PD);add_dir(TMP);add_dir(ROOT)
 capture_shared_after(SHARED_ADDITIONS)
 if READINESS["current_scontrol"]is not None:
  durable(RD/"current_scontrol.stdout",base64.b64decode(READINESS["current_scontrol"]["stdout_base64"]))
  durable(RD/"current_scontrol.stderr",base64.b64decode(READINESS["current_scontrol"]["stderr_base64"]))
 for n,item in enumerate(READINESS["attempts"]):
  durable(RD/("sacct_%02d.stdout"%n),base64.b64decode(item["stdout_base64"]))
  durable(RD/("sacct_%02d.stderr"%n),base64.b64decode(item["stderr_base64"]))
 readiness_r=dump(RD/"readiness.json",READINESS);seal_dir(RD)
 own_directory(SOURCE_SPEC["protected_terminal_directory_metadata"],["fresh_sacct.stderr","fresh_sacct.stdout","receipt.json"])
 need(SOURCE_SPEC["protected_terminal_directory_metadata"]["path"]==str(Path(SOURCE_SPEC["protected_terminal"]["metadata"]["path"]).parent),"Exact existing ST47 parent")
 T,T_r=first_pin_control(SOURCE_SPEC["protected_terminal"],"QUALIFIED_ST47")
 need(T["schema"]==SOURCE_SPEC["protected_terminal_schema"]=="root-final-composer-v7-17811-terminal-metadata-readonly-seal.v1"
  and T["status"]==SOURCE_SPEC["protected_terminal_status"]=="ACTUAL_SOFTWARE215_AND_ROOT_EXECUTION_CONTROL_FULL_CONTENT_AND_TERMINAL_METADATA_ACCEPTED_NOT_SOURCE_INDEX_SCIENCE_OR_DELIVERY"
  and len(T)==47 and T["actual_job_id"]=="17811"and T["Root_and_two_whole_content_PASS"]is True,"Existing qualified software ST47")
 BASE_ROWS={}
 for z in T["protected_metadata_before"]+T["job_owned_metadata_after"]+[T["actual_terminal"]["raw_stdout_metadata"],T["actual_terminal"]["raw_stderr_metadata"]]:
  mshape(z);need(z["path"]not in BASE_ROWS,"Existing ST47 unique baseline rows");BASE_ROWS[z["path"]]=z
 for p,names in list(T["protected_directory_children"].items())+list(T["job_owned_directory_children"].items()):
  need(p not in SPEC["protected_directory_children"],"Unique existing saved name tables");SPEC["protected_directory_children"][p]=canonical_names(names)
 for z in SOURCE_SPEC["Core_metadata"]:enroll(z)
 enroll(SOURCE_SPEC["Common_metadata"]);need(SOURCE_SPEC["Common_metadata"]["path"]==str(COMMON),"Common fixed metadata only")
 for p,z in HIST["Source7_metadata_original"].items():
  need(z["path"]==p,"Historical Source7 Native key");enroll(z)
 for p,names in HIST["Source7_names_original"].items():
  need(sorted(os.listdir(p))==canonical_names(names),"Historical Source7 original names before current code custody")
 for p,z in CUR["source_directory_metadata"].items():
  need(z["path"]==p and stat.S_ISDIR(z["mode"]),"Current exact code-parent Native key");enroll(z)
 for p,names in SPEC["source_directories"].items():need(sorted(os.listdir(p))==names,"Current exact code-parent names after Native enrollment")
 for z in SOURCE_SPEC["source44_metadata"]:enroll(z)
 own_directory(HIST["Source7_human_readonly_directory_metadata"],["receipt.json"])
 need(HIST["Source7_human_readonly_directory_metadata"]["path"]==str(Path(HIST["Source7_human_readonly"]["metadata"]["path"]).parent),"Historical Source7 HRO directory")
 OLD_HRO,OLD_HRO_r=first_pin_control(HIST["Source7_human_readonly"],"HISTORICAL_SOURCE7_HRO")
 need(len(OLD_HRO)==40 and OLD_HRO["schema"]==HIST["Source7_human_readonly_schema"]=="root-source-only-real-index-compatibility-human-metadata-readonly-seal.v1"
  and OLD_HRO["Root_and_two_whole_STATIC_PASS"]is True and OLD_HRO["protected_metadata_unchanged"]is True
  and OLD_HRO["future_publisher_and_compatibility_request_native7_equal_this_original_vector_required"]is True
  and OLD_HRO["Source44_parent_metadata_original"]==HIST["Source7_metadata_original"]
  and OLD_HRO["Source44_parent_names_original"]==HIST["Source7_names_original"],"Sealed historical seven observations, never a refreshed current vector")
 req,primary,PAIR=wait_primary()
 for z in PAIR["protected_metadata_before"]:
  mshape(z);need(z["path"]not in BASE_ROWS or BASE_ROWS[z["path"]]==z,"Pair SRO must preserve every ST47 original baseline")
  BASE_ROWS[z["path"]]=z
 for z in PAIR["source_metadata_after"]+[SOURCE_SPEC["pair_source_readonly"]["metadata"],SOURCE_SPEC["pair_source_readonly_directory_metadata"]]:
  mshape(z);need(z["path"]not in BASE_ROWS or BASE_ROWS[z["path"]]==z,"Original pair Source or SRO baseline cannot refresh")
  BASE_ROWS[z["path"]]=z
 for p,names in PAIR["protected_directory_children"].items():
  need(p not in SPEC["protected_directory_children"]or SPEC["protected_directory_children"][p]==canonical_names(names),"Pair source seal preserves original name universe")
  SPEC["protected_directory_children"][p]=canonical_names(names)
 for p,names in PAIR["source_package_children"].items():
  need(p not in SPEC["protected_directory_children"]or SPEC["protected_directory_children"][p]==canonical_names(names),"Pair OWN2 names cannot shadow")
  SPEC["protected_directory_children"][p]=canonical_names(names)
 OLD_SW=control(HIST["software"]);OLD_CT=control(HIST["software_contracts"])
 need(OLD_SW["schema"]=="final-composer-software.v7"and OLD_CT["status"]=="PASS"and OLD_CT["tests_run"]==215
  and OLD_CT["failures"]==OLD_CT["errors"]==0 and OLD_CT["tested_source"]==OLD_SW["source"]
  and T["actual_Source_groups_frozen"]==OLD_SW["source"]and T["actual_software_acceptance"]==HIST["software"]["receipt"]
  and T["actual_contracts"]==HIST["software_contracts"]["receipt"],"Historical17811 software215 provenance is retained separately")
 need(T["actual_terminal"]["row"][:6]==["17811","test9_final_composer_worker_identity_contracts_v7","COMPLETED","0:0","87","1"],"Historical17811 genuine terminal row")
 own_directory(CUR["terminal_directory_metadata"],["fresh_sacct.stderr","fresh_sacct.stdout","receipt.json"])
 need(CUR["terminal_directory_metadata"]["path"]==str(Path(CUR["terminal"]["metadata"]["path"]).parent),"Current software terminal own directory")
 CURRENT_ST,CURRENT_ST_r=first_pin_control(CUR["terminal"],"QUALIFIED_CURRENT_SW47")
 need(len(CURRENT_ST)==47 and CURRENT_ST["schema"]==CUR["terminal_schema"]=="root-final-composer-v7-17848-terminal-metadata-readonly-seal.v1"
  and CURRENT_ST["status"]==CUR["terminal_status"]=="ACTUAL_SOFTWARE237_AND_ROOT_EXECUTION_CONTROL_FULL_CONTENT_AND_TERMINAL_METADATA_ACCEPTED_NOT_SOURCE_INDEX_SCIENCE_OR_DELIVERY"
  and CURRENT_ST["actual_job_id"]=="17848"and CURRENT_ST["Root_and_two_whole_content_PASS"]is True
  and CURRENT_ST["actual_terminal"]["row"][:6]==["17848","test9_final_composer_partial_cache_names_contracts_v7","COMPLETED","0:0","190","1"],
  "Actual accepted purpose-fixed software17848 terminal; no future software profile")
 SW=control(SOURCE_SPEC["software"]);CT=control(SOURCE_SPEC["software_contracts"]);CURRENT_CO=control(CUR["Root_execution_control"])
 need(SW["schema"]=="final-composer-software.v7"and SW["status"]=="FINAL_DELIVERY_COMPOSER_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_ARCHIVE_ACCEPTANCE"
  and CT["status"]=="PASS"and type(CT["tests_run"])is int and CT["tests_run"]==237 and all(type(CT[k])is int and CT[k]==0 for k in("failures","errors"))
  and CT["tested_source"]==SW["source"]and CT["all_owned_and_context_python_compile_PASS"]is True
  and CT["all_launchers_bash_syntax_PASS"]is True,"Qualified actual237 software/Source/syntax")
 need(CURRENT_ST["actual_Source_groups_frozen"]==SW["source"]and CURRENT_ST["actual_software_acceptance"]==SOURCE_SPEC["software"]["receipt"]
  and CURRENT_ST["actual_contracts"]==SOURCE_SPEC["software_contracts"]["receipt"]
  and CURRENT_ST["actual_Root_execution_control"]==CUR["Root_execution_control"]["receipt"],
  "Actual current SW47 cryptographic software/CT/Root control chain")
 need(CURRENT_CO["actual_frozen_source_groups"]==SW["source"]and CURRENT_CO["zero_failure_error_skip"]is True
  and CURRENT_CO["actual_test_count"]==237 and CURRENT_CO["actual_producer_acceptance"]==SOURCE_SPEC["software"]["receipt"]
  and CURRENT_CO["actual_contracts"]==SOURCE_SPEC["software_contracts"]["receipt"],"Qualified Root237 producer associations")
 need(type(SPEC["publisher_native_extra"])is list and len(SPEC["publisher_native_extra"])==7
  and {z["path"]:z for z in SPEC["publisher_native_extra"]}==HIST["Source7_metadata_original"]
  and SPEC["publisher_directory_extra"]==HIST["Source7_names_original"],
  "Later Root request must carry exactly the sealed historical seven Native/names; no current recapture")
 PUBT,PUBT_r=first_pin_control(SPEC["publisher_terminal"],"QUALIFIED_PUBLISHER_TRO",64*1024*1024)
 PUB=control(SPEC["publisher_control"]);PRE=control(SPEC["publisher_preflight"])
 need(PUBT["schema"]==SPEC["publisher_terminal_schema"]and PUBT[SPEC["publisher_terminal_PASS_field"]]is True
  and PRE["schema"]==SPEC["publisher_preflight_schema"],"Actual future publisher qualified terminal and preflight, never a future Source literal")
 need(select(PUBT,SPEC["publisher_terminal_control_field"])==SPEC["publisher_control"]["receipt"]
  and select(PUB,SPEC["publisher_control_preflight_field"])==SPEC["publisher_preflight"]["receipt"],"Actual whole publisher terminal/preflight chain")
 need(select(PUBT,SPEC["publisher_qualification_evidence_field"])["Root_and_two_whole_content_PASS"]is True,"Actual publisher Root+two content qualification")
 pubrow=select(PUBT,SPEC["publisher_terminal_RAW_field"]).strip().split("|")
 need(len(pubrow)==9 and pubrow[2:4]==["COMPLETED","0:0"]and pubrow[5]=="1","Actual publisher fresh completed CPU1 terminal")
 # Publisher namespace events preserve earlier authority; they are not baseline refreshes.
 publisher_events={}
 for e in PUB["parent_child_addition_events"]+PUB["operational_shared_parent_addition_events"]:
  need(type(e)is dict and {"path","before","after","names_before","declared_added_children","names_after"}<=set(e),"Actual typed publisher directory event")
  mshape(e["before"]);mshape(e["after"]);p=e["path"]
  need(e["before"]["path"]==e["after"]["path"]==p and(p==str(R/"source")or Path(p).is_relative_to(R/"source")or p in {str(q)for q in SHARED}),
   "Only authenticated installed-Source/shared-parent events")
  need(all(e["before"][k]==e["after"][k]for k in ("inode","dev","uid","gid","mode"))
   and set(canonical_names(e["names_after"]))==set(canonical_names(e["names_before"]))|set(canonical_names(e["declared_added_children"])),"Original identity/permissions/names retained")
  need(p not in publisher_events,"One exact publisher event per directory");publisher_events[p]=e
 current_rows={}
 for field in SPEC["publisher_native_table_fields"]:
  rows=select(PUBT,field);need(type(rows)is list,"Authenticated publisher current-native table")
  for z in rows:
   mshape(z);need(z["path"]not in current_rows or current_rows[z["path"]]==z,"Qualified current native conflict");current_rows[z["path"]]=z
 for p,z in HIST["Source7_metadata_original"].items():
  need(p in current_rows and current_rows[p]==z,"Qualified actual publisher TRO must itself contain unchanged historical Source7 Native")
 for z in SPEC["publisher_native_extra"]:
  mshape(z);need(z["path"]not in current_rows or current_rows[z["path"]]==z,"Actual current extra cannot shadow");current_rows[z["path"]]=z
 need(str(V3_C)not in BASE_ROWS and str(V3_C)not in current_rows,"Future mutable compatibility primary must stay outside immutable publisher Native tables")
 for p,z in BASE_ROWS.items():
  expected=z
  if p in publisher_events:
   e=publisher_events[p];need(e["before"]==z,"Publisher event must retain original ST47 native");expected=e["after"]
  if p in current_rows:need(current_rows[p]==expected,"Qualified current native must equal original or exact declared event")
  # The four shared parents are job-time mutable history; this job snapshots them separately.
  if p not in {str(q)for q in SHARED}:enroll(expected)
 for p,z in current_rows.items():
  if p not in {str(q)for q in SHARED}:enroll(z)
 current_names={}
 for field in SPEC["publisher_directory_table_fields"]:
  rows=select(PUBT,field);need(type(rows)is dict,"Authenticated publisher exact-name table")
  for p,names in rows.items():
   need(p not in current_names or current_names[p]==canonical_names(names),"Qualified name-table conflict");current_names[p]=canonical_names(names)
 for p,names in HIST["Source7_names_original"].items():
  need(p in current_names and current_names[p]==canonical_names(names),"Qualified actual publisher TRO must itself retain all seven original name universes")
 for p,names in SPEC["publisher_directory_extra"].items():
  need(p not in current_names or current_names[p]==canonical_names(names),"Exact historical Source7 extra cannot change publisher-saved names");current_names[p]=canonical_names(names)
 need(str(V3_C)not in SPEC["protected_directory_children"]and str(V3_C)not in current_names,
  "Future mutable compatibility primary must stay outside immutable saved-name tables")
 for p,names in list(SPEC["protected_directory_children"].items()):
  expected=names
  if p in publisher_events:
   e=publisher_events[p];need(canonical_names(e["names_before"])==canonical_names(names),"Publisher event retains old saved name universe");expected=canonical_names(e["names_after"])
  if p in current_names:need(current_names[p]==expected,"Current names must be old or exact declared Source additions")
  SPEC["protected_directory_children"][p]=expected
 for p,names in current_names.items():SPEC["protected_directory_children"][p]=canonical_names(names)
 for p in {str(q)for q in SHARED}:SPEC["protected_directory_children"].pop(p,None)
 binding=select(PRE,SPEC["binding_field"])
 expected_proof=select(PRE,SPEC["projection_field"])
 need(type(binding)is dict and type(expected_proof)is dict and PUB["source_context"]==binding,"Whole actual qualified publisher binding/preflight data")
 need(len(SPEC["source44"])==len(SPEC["source44_metadata"])==44,"Whole Source44 before project imports")
 source_by={z["path"]:z for z in SPEC["source44_metadata"]}
 for r in SPEC["source44"]:
  need(source_by[r["path"]]["bytes"]==r["bytes"],"Source44 exact native")
  a,_=hashed(r["path"],1024*1024);need(a==r,"Source44 actual full CPU tuple before import")
 need({rid(r)for group in SW["source"].values()for r in group}=={rid(r)for r in SPEC["source44"]},"Software actual executing Source44")
 core_end();check_original_only()
 # Load only the reviewed exact frozen caller and exactly one registered StrictIndex module.
 own=[r for r in SPEC["source44"]if Path(r["path"]).name=="final_delivery_composer.py"]
 need(len(own)==1,"One actual sealed caller")
 spec=importlib.util.spec_from_file_location("root_source_index_qualified_caller",own[0]["path"])
 m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 api=m.restore_index_api();helper=m.finite_source_api()
 need(Path(api.__file__).parent==Path(helper.__file__).parent==Path(own[0]["path"]).parent,"Same-OWN helper/real constructor")
 need(m.SOFTWARE_TESTS==SPEC["actual_source_software_count"],"Exact qualified Source software profile")
 semantics=[r for r in SPEC["source44"]if Path(r["path"]).name==helper.SEMANTICS_NAME]
 need(len(semantics)==1 and fingerprint(semantics[0])==helper.SEMANTICS_FP,"Qualified G is exactly executable CODE44")
 helper._load_semantics_bytes(raw_file(semantics[0]["path"],1024*1024),semantics[0])
 need(PUB["source_software"]==SOURCE_SPEC["software"]["receipt"],"Actual publisher used the same accepted purpose-fixed17848 Source software")
 need(all(type(r)is dict and r["path"]not in {str(V3_C)}for r in SPEC["source44"]),"Current Source44 are qualified code files, never mutable primary directories")
 need(helper.SCHEMA==binding["schema"],"Exact Source binding API")
 need(helper.SCHEMA=="finite-final-source-delivery-context.v4"
  and binding["partial_cache_software_authority"]==dict(software_acceptance=SOURCE_SPEC["software"]["receipt"],
   Root_execution_control=CUR["Root_execution_control"]["receipt"]),
  "Only actual qualified17848 software/RootCO whole-control authority; no selfselected scalar or future pair")
 transports=helper._binding_shape(binding)
 # Construction replay uses only the existing qualified pure APIs and closed typed receipt phases.
 # It never instantiates a fake INDEX and never reads documentary originals or cache originals.
 PAYLOADS={}
 def transport_target(r):
  row=transports.get(rid(r));return row["archived"]if row is not None else r
 cache_carriers={}
 def obtain(r):
  k=rid(r)
  if k in PAYLOADS:return PAYLOADS[k]
  physical_r=transport_target(r)
  carrier=cache_carriers.get(rid(physical_r),physical_r)
  need(carrier["path"]in ORIGINAL,"Authenticated current native before construction IO")
  need(carrier["path"]not in helper.WRAPPER_ORIGINAL_PATHS and carrier["path"]!=helper.SOURCE_TEXT_ORIGIN,
   "Original documentary TXT is never a construction input")
  need(not any(Path(carrier["path"])==Path(x)or Path(carrier["path"]).is_relative_to(Path(x))for x in helper.CACHE_ROOTS),
   "Cache original bytes are never a construction fallback; use independent authenticated evidence carrier")
  need(fingerprint(carrier)==fingerprint(r),"Authorized whole carrier keeps exact complete identity")
  actual,raw=hashed(carrier["path"],payload_limit(r));need(actual==carrier,"Actual construction carrier bytes/native")
  PAYLOADS[k]=raw;PAYLOADS[rid(physical_r)]=raw;return raw
 for r in helper._initial_receipts(binding):obtain(r)
 pure_g=helper._load_semantics_bytes(obtain(binding["semantics_source"]),binding["semantics_source"])
 a,ca,i,c=helper._graph_shape(binding,PAYLOADS,pure_g)
 for r in helper._partial_cache_software_input_plan(binding,PAYLOADS):obtain(r)
 partial_software=helper.partial_cache_software_authority_shape(binding,PAYLOADS)
 need(partial_software["software_acceptance"]==SOURCE_SPEC["software"]["receipt"]
  and partial_software["Root_execution_control"]==CUR["Root_execution_control"]["receipt"]
  and partial_software["contracts"]==SOURCE_SPEC["software_contracts"]["receipt"]
  and partial_software["software_source_groups"]==SW["source"]and partial_software["actual_software_job_id"]=="17848",
  "Actual current software Source44/CT/priorTRO whole-control lineage")
 OP=helper.strict_json(obtain(binding["operational_source_provenance"]))
 for e in OP["cache_history"]["members"]:
  need(fingerprint(e["original_receipt"])==fingerprint(e["evidence_copy"]),"All exact cache evidence identities")
  cache_carriers[rid(e["original_receipt"])]=e["evidence_copy"]
 need(len(cache_carriers)==13060,"Complete all-cache membership, not a selected subset")
 obtain(OP["stage_terminal_metadata"]);obtain(OP["legacy_capture"])
 partial_record=helper._partial_cache_authority_record(OP)
 need(partial_record["control_receipt"]==partial_software["control_receipt"],
  "Publisher OP partial-name authority must equal genuine software-captured priorTRO tuple before read")
 obtain(partial_record["control_receipt"])
 STAGE_OBJ=helper.strict_json(PAYLOADS[rid(OP["stage_terminal_metadata"])])
 partial_names=helper.partial_cache_name_authority_shape(OP,STAGE_OBJ,PAYLOADS,partial_software["control_receipt"])
 partial_authority,cache_universes=helper.operational_cache_directory_universes(OP,STAGE_OBJ,PAYLOADS,partial_software["control_receipt"])
 need(len(cache_universes)==14 and len(cache_universes[helper.CACHE_ROOTS[-1]])==553 and len(OP["cache_history"]["members"])==13060,
  "All14 original cache Native and13060 selected opaque instances remain mandatory; additional543 are names only")
 derived_operational,_=helper._operational_input_plan(OP,STAGE_OBJ)
 for r in derived_operational:obtain(r)
 for r in helper._proof_receipts(a):obtain(r)
 proofs=[helper.strict_json(PAYLOADS[rid(a[p])])for p,k in helper.PAIRS]
 for r in helper._derived_receipts(a,i,proofs,pure_g):obtain(r)
 late=helper.strict_json(obtain(binding["late_source_publication"]))
 for r in helper._late_bridge_receipts(late):obtain(r)
 for r in binding["additional_control_receipts"]:
  need(Path(r["path"]).suffix==".json"and Path(r["path"]).is_relative_to(S/"submissions"),"Existing additional-own-control scope")
  obtain(r)
 for row in binding["transport_aliases"]:obtain(row["archived"])
 construction_projection=helper.SavedProjection(binding,PAYLOADS);construction_projection.validate()
 for r in construction_projection.terminal_source_receipts():obtain(r)
 need(exact(construction_projection.proof(),expected_proof),"Whole actual publisher preflight equality before copy")
 plan_receipts={rid(r):r for r in construction_projection.terminal_source_receipts()+construction_projection.semantic_control_receipts()}
 for row in binding["transport_aliases"]:plan_receipts[rid(row["archived"])]=row["archived"]
 source_keys={rid(r)for r in construction_projection.terminal_source_receipts()}
 evidence_keys={rid(r)for r in construction_projection.operational["evidence"]}
 alias_targets={}
 for row in construction_projection.selected_source_aliases()+construction_projection.aliases():
  construction_projection.check_source_text_alias(row)
  chosen=row if construction_projection.operational_alias(row)else construction_projection.project_source_alias(row)or row
  target=chosen["archived"]if construction_projection.operational_alias(row)else construction_projection._transport_target(chosen["archived"])
  key=rid(chosen["original"]);value=rid(target)
  need(value in plan_receipts and(key not in alias_targets or alias_targets[key]==value),"Full exact alias/physical closure")
  alias_targets[key]=value
 aliases=[dict(original=dict(path=k[0],bytes=k[1],sha256=k[2]),archived=plan_receipts[target],
  status="READONLY_BYTE_IDENTICAL_ALIAS")for k,target in sorted(alias_targets.items())]
 # Semantic controls that are also authenticated logical Source identities use the selected exact alias route.
 # Physical Source copies and independent evidence instances remain explicit rows and can only route to themselves.
 for key,target in alias_targets.items():
  if key in plan_receipts and key!=target:
   need(key not in source_keys and key not in evidence_keys,"Every physical Source/EVIDENCE instance must retain its independent self route")
   del plan_receipts[key]
 for target in alias_targets.values():need(target in plan_receipts,"One-hop exact alias target must remain a physical row")
 RAW_ORIGINALS=set(helper.WRAPPER_ORIGINAL_PATHS)|{helper.SOURCE_TEXT_ORIGIN}
 CACHE_ROOTS=[Path(p)for p in helper.CACHE_ROOTS]
 plan={}
 for k,r in plan_receipts.items():
  need(r["path"]not in RAW_ORIGINALS and k in PAYLOADS,"Every physical Source/control/evidence row is actual supplied bytes")
  need(k not in plan,"No duplicate engineering identity")
  role="OPERATIONAL_EVIDENCE"if k in evidence_keys else"SOURCE"if k in source_keys else"SEMANTIC_CONTROL"
  plan[k]=dict(receipt=r,role=role)
 need(plan and len({r["receipt"]["path"]for r in plan.values()})==len(plan),"Distinct authenticated physical paths; conflicting identities cannot share one INDEX row")
 PHASE="complete_Source_only_engineering_copy_construction"
 manifest=[];copy_receipts={}
 for k,entry in sorted(plan.items()):
  r=entry["receipt"];carrier=cache_carriers.get(k,r)
  need(fingerprint(carrier)==fingerprint(r),"Exact authorized carrier cannot change Source identity")
  need(carrier["path"]not in RAW_ORIGINALS and not any(Path(carrier["path"])==x or Path(carrier["path"]).is_relative_to(x)for x in CACHE_ROOTS),
   "Original cache/raw payload is never a construction fallback")
  need(carrier["path"]in ORIGINAL,"Carrier native enrolled from qualified actual controls")
  raw=PAYLOADS[k]
  need(len(raw)==r["bytes"]and hashlib.sha256(raw).hexdigest()==r["sha256"],"Complete authenticated construction bytes, no original IO fallback")
  relative=Path(r["path"]).relative_to(R).as_posix();p=ROOT/relative
  copied=durable(p,raw);need(fingerprint(copied)==fingerprint(r),"Engineering restored physical bytes differ")
  manifest.append(dict(receipt=r,relative=relative,role=entry["role"]));copy_receipts[k]=copied
 pkg=dict(schema="benchmark-delivery-package.v1",status="PACKAGED_AWAITING_INDEPENDENT_RESTORE",
  authority_root=str(R),manifest=manifest,engineering_scope="SOURCE_ONLY_REAL_STRICT_INDEX_NOT_PRODUCTION_ARCHIVE",
  scientific_restore_accepted=False,production_package_accepted=False,published=False,ACTIVE_changed=False)
 pkg_r=dump(PD/"engineering_index_manifest.json",pkg,MAX_CONTROL)
 alias_obj=dict(aliases=aliases);alias_r=dump(PD/"engineering_aliases.json",alias_obj,MAX_CONTROL)
 for z in sorted(NEW_DIRS.values(),key=lambda z:len(Path(z["path"]).parts),reverse=True):
  p=Path(z["path"])
  if p.is_relative_to(ROOT):seal_dir(p)
 restored_names={str(p):sorted(os.listdir(p))for p in [Path(z["path"])for z in NEW_DIRS.values()if Path(z["path"]).is_relative_to(ROOT)]}
 PHASE="real_StrictIndex_positive_and_focused_negative_qualification"
 traps=[];expected_traps=[];cases=[]
 original_sources=set(ORIGINAL)
 source_exec={str(Path(r["path"]))for r in SPEC["source44"]}
 ancestors=set()
 for p in [ROOT,OUT,PD]+[Path(x)for x in source_exec]:
  ancestors.update(str(x)for x in p.parents)
 poison_fds=set()
 def permitted(p,operation,writing=False):
  if isinstance(p,int):return p in poison_fds
  path=lexical(p);s=str(path)
  if writing:return path.is_relative_to(PD)or path.is_relative_to(OUT)
  if path.is_relative_to(ROOT):return True
  if s in source_exec:return True
  if operation in("stat","lstat","resolve","readlink")and s in ancestors:return True
  return False
 def deny(p,operation,writing=False):
  if not permitted(p,operation,writing):
   traps.append(dict(path=str(p),operation=operation));raise AssertionError("Original filesystem denied in SOURCE-only INDEX: "+str(p))
 @contextlib.contextmanager
 def poison():
  saved=[]
  def patch(obj,name,value):
   saved.append((obj,name,getattr(obj,name)));setattr(obj,name,value)
  def po(p,*a,**k):
   mode=a[0]if a else k.get("mode","r");deny(p,"open",any(x in mode for x in("w","a","x","+")));return RAW_PATH_OPEN(p,*a,**k)
  def bo(p,*a,**k):
   mode=a[0]if a else k.get("mode","r");deny(p,"open",any(x in mode for x in("w","a","x","+")));return RAW_OPEN(p,*a,**k)
  def io_open(p,*a,**k):
   mode=a[0]if a else k.get("mode","r");deny(p,"io.open",any(x in mode for x in("w","a","x","+")));return RAW_IO_OPEN(p,*a,**k)
  def oo(p,flags,*a,**k):
   deny(p,"os.open",bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
   fd=RAW_OS_OPEN(p,flags,*a,**k);poison_fds.add(fd);return fd
  def list_directory(p="."):deny(p,"os.listdir");return RAW_LISTDIR(p)
  def scan_directory(p="."):deny(p,"os.scandir");return RAW_SCANDIR(p)
  def iterate_directory(p):deny(p,"Path.iterdir");return RAW_ITERDIR(p)
  def st(p,*a,**k):deny(p,"stat");return RAW_STAT(p,*a,**k)
  def ls(p,*a,**k):deny(p,"lstat");return RAW_LSTAT(p,*a,**k)
  def rl(p,*a,**k):deny(p,"readlink");return RAW_READLINK(p,*a,**k)
  def pst(p,*a,**k):deny(p,"stat");return RAW_PATH_STAT(p,*a,**k)
  def pls(p,*a,**k):deny(p,"lstat");return RAW_PATH_LSTAT(p,*a,**k)
  def prs(p,*a,**k):deny(p,"resolve");return RAW_PATH_RESOLVE(p,*a,**k)
  def prl(p,*a,**k):deny(p,"readlink");return RAW_PATH_READLINK(p,*a,**k)
  try:
   for obj,name,value in[(builtins,"open",bo),(io,"open",io_open),(os,"open",oo),(os,"listdir",list_directory),
    (os,"scandir",scan_directory),(os,"stat",st),(os,"lstat",ls),(os,"readlink",rl),(Path,"iterdir",iterate_directory),
    (Path,"open",po),(Path,"stat",pst),(Path,"lstat",pls),(Path,"resolve",prs),(Path,"readlink",prl)]:patch(obj,name,value)
   yield
  finally:
   for obj,name,value in reversed(saved):setattr(obj,name,value)
 with poison():
  index=api.StrictIndex(pkg,ROOT,OUT,alias_obj)
  projection,baseline=helper.indexed_payloads(binding,pkg,index)
  need(exact(projection.proof(),expected_proof),"Whole actual publisher Source projection proof must match real INDEX")
  need(not traps,"Positive SOURCE replay touched original filesystem")
  for p,z in baseline.items():need(NEW_FILES.get(p)==z,"Restored baseline must equal saved first-created full native")
  all_copies=projection.terminal_source_receipts()
  evidence=projection.operational["evidence"]
  def selected_physical(r):
   key=rid(r);target=index.aliases.get(key,key)
   need(target in index.rows,"Authenticated complete real INDEX physical target")
   return index.rows[target][0]
  def omitted(label,r):
   target=rid(selected_physical(r))
   reduced=dict(pkg,manifest=[row for row in pkg["manifest"]if rid(row["receipt"])!=target])
   reduced_aliases=dict(aliases=[e for e in aliases if rid(e["archived"])!=target])
   neg=api.StrictIndex(reduced,ROOT,ROOT/("negative_"+label),reduced_aliases)
   before=len(traps)
   try:helper._indexed_source_bytes(reduced,neg,r,transports,{})
   except ValueError as e:cases.append(dict(case=label,status="EXPECTED_VALUEERROR",required_receipt=r,physical_target=index.rows[target][0],error=str(e)))
   else:raise ValueError("Real INDEX omission was accepted: "+label)
   need(len(traps)==before,"Omission denial attempted original fallback")
  alternatives=[]
  for key,candidate_rows in sorted(projection.identities.items()):
   if key in projection.source_copies:continue
   candidate_physical={rid(projection._transport_target(row["source"])):projection._transport_target(row["source"])for row in candidate_rows}
   chosen=projection._transport_target(projection.source_physical[key])
   for candidate in candidate_physical.values():
    if rid(candidate)!=rid(chosen):
     alternatives.append((dict(path=key[0],bytes=key[1],sha256=key[2]),chosen,candidate))
  need(alternatives,"Actual full logical Source identity must have a genuinely unselected declared copy")
  selected_original,selected_copy,unselected_copy=alternatives[0]
  omitted("unselected_declared_Source_copy",unselected_copy)
  known_cache=[];unknown_cache=[]
  for original,copy,field in projection.operational["caches"]:
   route=projection.operational_routes[rid(original)]
   (unknown_cache if route["role"]=="INDEPENDENT_CACHE_EVIDENCE"else known_cache).append(copy)
  need(known_cache and unknown_cache,"Both admitted and non-Source cache evidence classes are required")
  omitted("known_Source_cache_independent_EVIDENCE",known_cache[0])
  omitted("unknown_cache_independent_EVIDENCE",unknown_cache[0])
  omitted("new_four_eligible_shell_Source",OP["new_four"][0]["eligible_source"])
  omitted("legacy_two_existing_shell_Source",OP["legacy_two"]["entries"][0]["eligible_source"])
  omitted("new_four_independent_raw_OPAQUE",OP["new_four"][0]["evidence_copy"])
  omitted("legacy_two_independent_raw_OPAQUE",OP["legacy_two"]["entries"][0]["evidence_copy"])
  bridge_inputs=helper._late_bridge_receipts(late)
  omitted("sole_bridge_eligible_python_Source",bridge_inputs[1])
  omitted("sole_bridge_byte_identity_proof",bridge_inputs[0])
  required_controls=set(projection.control_receipts)
  control_transports=[row for row in binding["transport_aliases"]if rid(row["original"])in required_controls]
  need(control_transports,"Actual authenticated control transport is required")
  omitted("declared_semantic_JSON_OPAQUE_transport",control_transports[0]["original"])
  for label,r in [("actual237_software_acceptance",SOURCE_SPEC["software"]["receipt"]),
   ("actual237_Root_execution_control",CUR["Root_execution_control"]["receipt"]),
   ("actual237_derived_contracts",SOURCE_SPEC["software_contracts"]["receipt"]),
   ("fixed_prior_failed17837_name_authority",partial_software["control_receipt"])]:
   need(rid(r)in required_controls,"Whole current authority control must be a mandatory semantic CONTROL_BYTES row")
   omitted(label,r)
  wrong_source_aliases=[dict(e)for e in aliases];found=0
  for e in wrong_source_aliases:
   if rid(e["original"])==rid(selected_original):e["archived"]=unselected_copy;found+=1
  need(found==1 and fingerprint(selected_copy)==fingerprint(unselected_copy),"Exact conditional same-FP Source alias negative")
  wrong_source=api.StrictIndex(pkg,ROOT,ROOT/"negative_wrong_selected_Source_alias",dict(aliases=wrong_source_aliases))
  before=len(traps)
  try:helper.indexed_payloads(binding,pkg,wrong_source)
  except ValueError as e:cases.append(dict(case="selected_Source_alias_redirected_to_other_declared_copy",status="EXPECTED_VALUEERROR",original=selected_original,selected=selected_copy,wrong=unselected_copy,error=str(e)))
  else:raise ValueError("Wrong selected Source alias was accepted")
  need(len(traps)==before,"Selected Source alias denial attempted original fallback")
  raw_receipt=OP["new_four"][0]["original_text"]
  bad=dict(pkg,manifest=list(pkg["manifest"])+[dict(receipt=raw_receipt,relative=Path(raw_receipt["path"]).relative_to(R).as_posix(),role="INVALID_RAW_ORIGINAL")])
  bad_aliases=dict(aliases=[e for e in aliases if rid(e["original"])!=rid(raw_receipt)])
  bad_index=api.StrictIndex(bad,ROOT,ROOT/"negative_raw_original",bad_aliases)
  before=len(traps)
  try:helper.indexed_payloads(binding,bad,bad_index)
  except ValueError as e:cases.append(dict(case="raw_original_INDEX_row",status="EXPECTED_VALUEERROR",error=str(e)))
  else:raise ValueError("Raw documentary original INDEX row was accepted")
  need(len(traps)==before,"Raw original was read before denial")
  wrong_aliases=[dict(e)for e in aliases];raw_key=rid(raw_receipt);found=0
  for e in wrong_aliases:
   if rid(e["original"])==raw_key:e["archived"]=selected_physical(OP["new_four"][0]["eligible_source"]);found+=1
  need(found==1,"Actual exact raw-evidence alias is required")
  wrong=api.StrictIndex(pkg,ROOT,ROOT/"negative_wrong_raw_alias",dict(aliases=wrong_aliases))
  before=len(traps)
  try:helper.operational_index_alias_shape(projection,wrong)
  except ValueError as e:cases.append(dict(case="raw_opaque_alias_redirected_to_same_FP_shell_Source",status="EXPECTED_VALUEERROR",error=str(e)))
  else:raise ValueError("Wrong operational raw alias was accepted")
  need(len(traps)==before,"Raw alias denial attempted original IO")
  text_receipt=projection.source_bridge["original_text"]
  text_bad=dict(pkg,manifest=list(pkg["manifest"])+[dict(receipt=text_receipt,relative=Path(text_receipt["path"]).relative_to(R).as_posix(),role="INVALID_64944_ORIGINAL_TXT")])
  text_index=api.StrictIndex(text_bad,ROOT,ROOT/"negative_64944_original_row",alias_obj)
  before=len(traps)
  try:helper.indexed_payloads(binding,text_bad,text_index)
  except ValueError as e:cases.append(dict(case="64944_original_TXT_INDEX_row",status="EXPECTED_VALUEERROR",error=str(e)))
  else:raise ValueError("64944 original TXT INDEX row was accepted")
  need(len(traps)==before,"64944 row denial attempted original IO")
  text_aliases=list(aliases)+[dict(original=text_receipt,archived=selected_physical(bridge_inputs[1]),status="READONLY_BYTE_IDENTICAL_ALIAS")]
  text_alias_index=api.StrictIndex(pkg,ROOT,ROOT/"negative_64944_original_alias",dict(aliases=text_aliases))
  before=len(traps)
  try:helper.indexed_payloads(binding,pkg,text_alias_index)
  except ValueError as e:cases.append(dict(case="64944_original_TXT_INDEX_alias",status="EXPECTED_VALUEERROR",error=str(e)))
  else:raise ValueError("64944 original TXT alias was accepted")
  need(len(traps)==before,"64944 alias denial attempted original IO")
  for original in [OP["new_four"][0]["original_text"],projection.source_bridge["original_text"]]:
   p=Path(original["path"])
   for operation in [lambda: p.read_bytes(),lambda: builtins.open(p,"rb"),lambda: io.open(p,"rb"),
    lambda: os.open(str(p),os.O_RDONLY),lambda: os.stat(str(p)),lambda: os.lstat(str(p)),lambda: p.resolve(),lambda: os.readlink(str(p))]:
    start=len(traps)
    try:operation()
    except AssertionError:expected_traps.extend(traps[start:]);del traps[start:]
    else:raise ValueError("Original-FS open/stat/lstat/resolve/readlink poison is not active")
  original_cache=Path(helper.CACHE_ROOTS[-1])
  for operation in [lambda: list(original_cache.iterdir()),lambda: os.listdir(str(original_cache)),lambda: list(os.scandir(str(original_cache)))]:
   start=len(traps)
   try:operation()
   except AssertionError:expected_traps.extend(traps[start:]);del traps[start:]
   else:raise ValueError("Original cache directory-listing poison is not active")
  need(not traps,"Unexpected original filesystem attempt")
  helper.operational_index_alias_shape(projection,index)
  index.after()
  helper.operational_index_native_end(index,baseline)
 # No original payload is opened in final metadata custody. Code and approved controls are separate outer scope.
 PHASE="durable_Source_only_compatibility_proofs_and_true_last_guards"
 projection_r=dump(PD/"source_only_projection.json",projection.proof(),MAX_CONTROL)
 def final_index_end():
  with poison():
   repeated,again=helper.indexed_payloads(binding,pkg,index)
   need(exact(repeated.proof(),projection.proof()),"Repeated complete actual SOURCE projection")
   for p,z in again.items():need(p in baseline and baseline[p]==z,"Original restored native baseline cannot refresh")
   index.after();helper.operational_index_native_end(index,baseline)
  need(not traps,"True-last replay attempted original filesystem")
  for p,names in restored_names.items():need(sorted(os.listdir(p))==names,"Engineering restored exact universe")
 def original_end():
  for k,r in READ_PINS.copy().items():
   if Path(r["path"]).is_relative_to(ROOT):continue
   a,_=hashed(r["path"],payload_limit(r));need(a==r,"Whole fixed own inputs changed")
  core_end();check_original_only()
 final_index_end();original_end()
 result=dict(schema="root-source-only-real-strict-index-compatibility.v3",
  status="ACTUAL_SOURCE_ONLY_REAL_STRICT_INDEX_CPU_COMPATIBLE_NOT_PRODUCTION_PACKAGE_OR_SCIENTIFIC_RESTORE",
  allocation=dict(job_id=JID,allocated_CPUs=1,allocated_gpus=0,current_readiness=READINESS),
  Source44=SPEC["source44"],qualified_software=SPEC["software"]["receipt"],
  qualified_current_Root_execution_control=CUR["Root_execution_control"]["receipt"],qualified_current_software_terminal=CURRENT_ST_r,
  historical_software215=HIST["software"]["receipt"],historical_Source7_HRO=OLD_HRO_r,
  historical_Source7_metadata_original=HIST["Source7_metadata_original"],historical_Source7_names_original=HIST["Source7_names_original"],
  current_code_parent_metadata_separate=CUR["source_directory_metadata"],
  primary_directory_Source_creation_history=PRIMARY_FINAL["source_creation_history"],
  actual_primary_transaction=PRIMARY_FINAL,primary_directory_is_not_immutable_Original=True,
  actual_prior_failed17837_control=partial_software["control_receipt"],all_other13_cache_universes_Stage_derived=True,
  fixed_partial_root_current553_names_only=True,additional543_leaf_IO_or_reader_permission=False,
  qualified_publisher=SPEC["publisher_control"]["receipt"],publisher_terminal=PUBT_r,
  engineering_manifest=pkg_r,engineering_aliases=alias_r,whole_Source_projection=projection_r,
  physical_INDEX_entries=len(index.rows),full_aliases=len(index.aliases),all_Source_rows=len(projection.source_rows),
  all_Source_copy_receipts=len(all_copies),all_independent_operational_EVIDENCE_copies=len(evidence),
  all_13060_cache_instances_indexed=True,original_raw6_not_indexed=True,original64944_not_indexed_or_aliased=True,
  complete_publisher_projection_equal=True,real_same_OWN_StrictIndex_constructor=True,
  expected_negative_cases=cases,unexpected_original_filesystem_attempts=traps,
  deliberate_poison_selfchecks=expected_traps,StrictIndex_proof=index.proof(),
  protected_original_native_authority=T_r,publisher_current_native_authority=PUBT_r,
  protected_original_native_extra=SPEC["protected_extra_metadata"],
  restored_metadata_before_first_INDEX_io=[NEW_FILES[str(ROOT/row["relative"])]for row in manifest],
  full_original_native_union_PASS=True,operational_shared_parent_addition_events=SHARED_EVENTS,original_installed_Source_permissions_changed=False,
  scientific_recomputation_performed=False,production_archive_or_full_restore_accepted=False,
  Git_changed=False,published=False,ACTIVE_changed=False)
 acceptance_r=dump(PD/"acceptance.json",result,MAX_CONTROL)
 for p in [RUN,TMP]:
  seal_dir(p)
 seal_dir(PD)
 # The original restored baselines remain those captured before first indexed reads.
 final_index_end();original_end()
 need(parse(raw_file(acceptance_r["path"],MAX_CONTROL))==result,"Final acceptance JSON whole readback")
 final_r,_=hashed(acceptance_r["path"],MAX_CONTROL);need(final_r==acceptance_r,"Final actual acceptance full bytes")
 core_end();check_native()
 # No payload/hash/JSON follows this combined original/restored/new-output native fence.
 for p,z in baseline.items():need(md(p)==z,"True-last original restored metadata changed")
 for p,names in restored_names.items():need(sorted(os.listdir(p))==names,"True-last restored universe changed")
 check_native()
 print(json.dumps(dict(schema="root-source-only-real-index-final-CPU-descriptor.v3",actual_job_id=JID,
  acceptance=acceptance_r,engineering_manifest=pkg_r,engineering_aliases=alias_r,whole_Source_projection=projection_r,
  actual_physical_entries=len(index.rows),actual_full_aliases=len(index.aliases),
  actual_original_native_union_n=len(ORIGINAL),actual_restored_native_n=len(baseline),
  final_owned_proof_directory_metadata=EVENTS[str(PD)]["after"],final_owned_proof_directory_children=EVENTS[str(PD)]["children"],
  true_last_original_native_union_PASS=True,Source_only_compatibility=True,
  production_package_or_scientific_restore_acceptance=False,Git_changed=False,published=False,ACTIVE_changed=False),
  sort_keys=True,allow_nan=False))
except BaseException as original:
 if not READINESS["guard_succeeded"]:
  try:preserve_failed_current_guard(original)
  except BaseException as diagnostic:
   print(json.dumps(dict(status="READINESS_FAILURE_PRESERVATION_ERROR_NOT_QUALIFICATION",error_type=type(diagnostic).__name__,error=str(diagnostic))),file=sys.stderr)
  raise
 failure=dict(schema="root-source-only-real-index-incomplete.v3",status="ACTUAL_CPU_INCOMPLETE_NO_SOURCE_INDEX_ACCEPTANCE",
  actual_job_id=JID,phase=PHASE,error_type=type(original).__name__,error=str(original),
  created_paths=sorted(NEW_FILES),created_directories=sorted(NEW_DIRS),original_filesystem_attempts=globals().get("traps",[]),
  original_exception_preserved=True,production_package_accepted=False,scientific_restore_accepted=False,
  Git_changed=False,published=False,ACTIVE_changed=False)
 try:
  if str(PD)in NEW_DIRS and stat.S_IMODE(md(PD)["mode"])&0o222:dump(PD/"typed_incomplete.json",failure)
 except BaseException as diagnostic:
  if hasattr(original,"add_note"):original.add_note("Own diagnostic failure: "+type(diagnostic).__name__+": "+str(diagnostic))
 raise
