#!/usr/bin/env python3
"""Postarchive exact-index-only root GPU accounting replay; no live accounting/science."""
import argparse,contextlib,copy,datetime,hashlib,importlib.util,json,os,re,stat,subprocess,sys,types,unittest
from pathlib import Path,PurePosixPath
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/24_benchmark_delivery"
D=Path(__file__).absolute().parent;USER="u21111210118"
FILES=("checker.py","test_checker.py","checker_cpu.sbatch","HANDOFF.md")
TESTS=24
JOB_NAME="test9_restored_root298_cost"
SOFTWARE="RESTORED_ROOT298_COST_VERIFIER_SOFTWARE_CPU_ACCEPTED_NOT_REAL_RESTORE"
CONTENT="RESTORED_ROOT298_GPU_COST_INDEPENDENT_RECOMPUTATION_ACCEPTED_NOT_SCIENCE"
SCOPE="RESTORED_ROOT_GPU_ACCOUNTING_ONLY_NOT_SCIENTIFIC_PUBLICATION_OR_ACTIVE_ACCEPTANCE"
def pin(rel,n,h):return dict(path=str(R/rel),bytes=n,sha256=h)
READER=pin("steps/24_benchmark_delivery/frozen/final_delivery_composer_v6_restoreindex1_fixturefix2_13377/code/restored_index_scope.py",34228,"9dec8043bcd8b44394869791f8046aff3f2787a491d8a285fcbc56a4c5e62fac")
CORE=pin("steps/24_benchmark_delivery/frozen/history_policy_13223/code/delivery_core_v2.py",21981,"eb46c9adf772433e06851f2328f47bd5b2b11a101288d97cce9424cea718eb06")
COST_ENTRY=pin("steps/24_benchmark_delivery/frozen/root_gpu_cost_v3_running_window_v1_14565/code/root_gpu_cost_audit.py",42022,"9db3aec7c9c09f2c91ce36d93255350be74a4d2a2a3f6afc73d88292af7d14ed")
COST_SW=pin("steps/24_benchmark_delivery/runs/root_gpu_cost_contracts_14565/acceptance.json",7539,"b46e1f1f7e8dd9ea30a2c8109843a62ee2ff83c0ecd9da779b5bd9d6718a24c6")
COST_A=pin("steps/24_benchmark_delivery/runs/root_gpu_cost_audit_14576/acceptance.json",15252,"ca6bac7a46bad01841a52804c2793b875934cf2cc7672d9ceb24de62a3c25ebd")
COST_SEAL=S/"submissions/root_gpu_cost_v3_audit14576_actual_full_cost_metadata_terminal_seal/receipt.json"
COST_SW_SEAL=S/"submissions/root_gpu_cost_v3_software14565_actual_metadata_terminal_seal/receipt.json"
COST_SW_TERMINAL=S/"submissions/root_gpu_cost_v3_software14565_scheduler_metadata_20261014T041441Z/receipt.json"
COST_NAMES=("root_gpu_cost_audit.py","test_root_gpu_cost_audit.py","root_gpu_cost_cpu.sbatch","HANDOFF.md")
def need(v,msg):
 if not v:raise ValueError(msg)
def lexical(p):
 raw=os.fspath(p);need(isinstance(raw,str)and raw.startswith("/")and all(x not in("","..",".")for x in raw.split("/")[1:]),"Absolute lexical path without traversal required");return Path(raw)
def local(p):
 p=lexical(p);need(p.is_relative_to(R)and p.resolve()==p,"Own CODE/control path outside authority or symlink");return p
def identity(r):return(r["path"],r["bytes"],r["sha256"])
def shape(r):
 need(isinstance(r,dict)and set(r)=={"path","bytes","sha256"}and type(r["bytes"])is int and r["bytes"]>=0 and re.fullmatch("[0-9a-f]{64}",r.get("sha256","")),"Exact three-field full identity required");lexical(r["path"]);return r
def rec(p):
 p=local(p);need(p.is_file()and not p.is_symlink()and not(p.stat().st_mode&0o222),"Readonly owned CODE/control required")
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def exact(r):
 shape(r);need(rec(r["path"])==r,"Qualified CODE/control bytes drift");return Path(r["path"]).read_bytes()
def parse_json(b):
 def pairs(items):
  result={}
  for k,v in items:need(k not in result,"Duplicate JSON key forbidden");result[k]=v
  return result
 def constant(v):raise ValueError("Nonfinite JSON constant forbidden: "+v)
 return json.loads(b,object_pairs_hook=pairs,parse_constant=constant)
def jbytes(v):return(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode()
def dump(p,v):
 p=local(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("xb")as f:f.write(jbytes(v));f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 return rec(p)
def load(name,r):
 exact(r);p=Path(r["path"]);spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);need(Path(m.__file__).absolute()==p,"Executing module differs");return m
def tres(text):
 d={}
 for part in text.split(","):
  need("="in part,"Allocated TRES missing/malformed");k,v=part.split("=",1);need(k and v and k not in d,"Duplicate/empty TRES");d[k]=v
 need(d.get("cpu","").isdigit()and int(d["cpu"])>=1,"Positive numeric allocated CPU required")
 for k,v in d.items():
  if k.startswith("gres/gpu"):need(re.fullmatch(r"gres/gpu(?::[A-Za-z0-9_.-]+)?",k)and v.isdigit()and int(v)==0,"GPU allocation/malformed namespace forbidden")
 return d
def cpu():
 jid=os.environ.get("SLURM_JOB_ID","");need(jid.isdigit(),"Actual CPU before any hashes/content/imports")
 for k,v in {"CUDA_VISIBLE_DEVICES":"","JAX_PLATFORMS":"cpu","PYTHONNOUSERSITE":"1","PYTHONDONTWRITEBYTECODE":"1","OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1","MKL_NUM_THREADS":"1"}.items():need(os.environ.get(k)==v,"Pure CPU isolation differs")
 need("PYTHONPATH"not in os.environ,"PYTHONPATH injected")
 raw=subprocess.check_output(["scontrol","show","job",jid,"-o"],text=True)
 rows=[x for x in raw.splitlines()if re.search(r"\bJobId="+jid+r"(?:\s|$)",x)];need(len(rows)==1,"One actual CPU record")
 pairs=re.findall(r"(\w+)=(\S*)",rows[0]);keys={"JobId","JobName","JobState","UserId","Account","Partition","NumCPUs","TRES","AllocTRES"}
 need(all(sum(k==key for k,_ in pairs)<=1 for key in keys),"Duplicate live scheduler field");f=dict(pairs)
 need(f.get("JobName")==JOB_NAME and f.get("JobState")=="RUNNING"and f.get("UserId","").startswith(USER+"(")and f.get("Account")==USER and f.get("Partition")=="organ"and f.get("NumCPUs")=="1","Actual named CPU1 owner/account/organ required")
 ds=[tres(f[k])for k in("TRES","AllocTRES")if k in f];need(ds and all(x["cpu"]=="1"for x in ds)and(len(ds)==1 or ds[0]==ds[1]),"Actual CPU1/TRES agreement required")
 return dict(job_id=jid,allocated_CPUs=1,allocated_GPUs=0,selected_scheduler_record=rows[0])
def same_json(a,b):
 if type(a)is not type(b):return False
 if isinstance(a,dict):return set(a)==set(b)and all(same_json(a[k],b[k])for k in a)
 if isinstance(a,list):return len(a)==len(b)and all(same_json(x,y)for x,y in zip(a,b))
 return a==b
def pair_lists(original,frozen,names):
 need(len(original)==len(frozen)==len(names)and [Path(r["path"]).name for r in original]==list(names)and [Path(r["path"]).name for r in frozen]==list(names),"Whole source universe/order differs")
 need(all((a["bytes"],a["sha256"])==(b["bytes"],b["sha256"])for a,b in zip(original,frozen)),"Original/frozen source byte identities differ")
def input_bytes(scope,r):shape(r);return scope.verify(r).read_bytes()
def input_json(scope,r):return parse_json(input_bytes(scope,r))
def source_set(scope,rows,n,names=None):
 need(isinstance(rows,list)and len(rows)==n and len({r["path"]for r in rows})==n,"Exact unique source count required")
 if names is not None:need({Path(r["path"]).name for r in rows}==set(names),"Source names differ")
 for r in rows:input_bytes(scope,r)
def select_index(scope,path):
 keys=scope.paths.get(str(path),[]);need(len(keys)==1,"Unknown ownSHA requires one unambiguous explicit full index identity")
 need(keys[0]in scope.rows,"Required journal must be an actual index row")
 return scope.rows[keys[0]][0]
def counts(scope,r,n,source=None):
 c=input_json(scope,r);need(c.get("status")=="PASS"and type(c.get("tests_run"))is int and c["tests_run"]==n and type(c.get("failures"))is int and c["failures"]==0 and type(c.get("errors"))is int and c["errors"]==0 and type(c.get("skipped",0))is int and c.get("skipped",0)==0,"Saved contracts counts differ")
 if source is not None:need(same_json(c.get("tested_source_files"),source),"Saved owned contracts source differs")
 input_bytes(scope,c["log"]);return c

def own(original,frozen):
 pair_lists(original,frozen,FILES)
 for r in original+frozen:exact(r)
 return True
def metadata(rows):
 return [dict(path=r["path"],bytes=Path(r["path"]).stat().st_size,inode=Path(r["path"]).stat().st_ino,mtime_ns=Path(r["path"]).stat().st_mtime_ns,mode=Path(r["path"]).stat().st_mode&0o777)for r in rows]
def code_qualification():
 # Software bootstrap only. These external qualification inputs become indexed SOURCE in verify.
 for r in (READER,CORE,COST_ENTRY,COST_SW):exact(r)
 sw=parse_json(exact(COST_SW));need(sw.get("schema")=="root-gpu-cost-software.v3"and sw.get("status")=="ROOT_GPU_COST_AUDITOR_SOFTWARE_CPU_ACCEPTED"and sw["allocation"]["job_id"]=="14565","Actual accepted V3 software")
 rs=sw["source"];need(len(rs)==4 and [Path(r["path"]).name for r in rs]==list(COST_NAMES)and rs[0]==COST_ENTRY,"Qualified V3 source4")
 for r in rs+sw["original_source"]:exact(r)
 pair_lists(sw["original_source"],rs,COST_NAMES)
 ct=parse_json(exact(sw["contracts"]));exact(ct["log"])
 need(ct["status"]=="PASS"and ct["tests_run"]==88 and ct["failures"]==ct["errors"]==ct["skipped"]==0 and ct["tested_source"]==rs,"Actual saved88/source qualification")
 for key in ("original_owned_pre_and_post_byte_readback_PASS","original_and_frozen_owned_byte_identities_equal","all_owned_python_compile_PASS","all_launchers_bash_syntax_PASS"):need(sw.get(key)is True,"Actual V3 source qualification flag")
 return dict(reader=READER,cost_entry=COST_ENTRY,core_for_software_fixtures_only=CORE,cost_software=COST_SW,archived_qualification_evidence=rs+sw["original_source"]+[COST_SW,sw["contracts"],ct["log"],CORE,READER],old88_not_rerun=True,old130_and32_not_rerun=True)
def new_module(name,source,filename):
 module=types.ModuleType(name);module.__file__=filename
 # __name__ never equals __main__; only exact previously qualified CODE is compiled.
 exec(compile(source,filename,"exec",dont_inherit=True),module.__dict__)
 return module
def indexed_cost_module(scope,expected_sw=COST_SW):
 sw=input_json(scope,expected_sw)
 source=sw["source"];source_set(scope,source,4,COST_NAMES);source_set(scope,sw["original_source"],4,COST_NAMES);pair_lists(sw["original_source"],source,COST_NAMES)
 need(source[0]==COST_ENTRY,"Only exact qualified V3 main may execute")
 entry=scope.verify(COST_ENTRY);module=new_module("indexed_qualified_cost_pure",entry.read_bytes(),os.fspath(entry.physical()))
 need(module.CONTRACT_COUNT==88 and module.SOFTWARE_SCHEMA=="root-gpu-cost-software.v3"and module.R==R,"Exact pure cost module interface")
 ct=input_json(scope,sw["contracts"]);input_bytes(scope,ct["log"])
 module.software_contract(sw,ct,source)
 need(same_json(sw["original_source_metadata_before"],sw["original_source_metadata_after"]),"Historical original source metadata pre/end identity")
 return module,sw
@contextlib.contextmanager
def pure_cost_context(module,allowed_result_dirs):
 # Only two exact values from byte-bound E2E root controllers. This has no input-read capability.
 need(len(allowed_result_dirs)==2 and len(set(allowed_result_dirs))==2,"Two unique exact E2E scalar result_dir values")
 allowed=set()
 for value in allowed_result_dirs:
  p=lexical(value);need(p.is_relative_to(R),"E2E result scalar outside logical authority");allowed.add(str(p))
 saved={}
 def deny(*args,**kwargs):raise ValueError("Pure restored accounting forbids live I/O, queries or writers")
 def scalar_path(value):
  p=lexical(value);need(str(p)in allowed,"Only exact declared E2E scalar paths permitted")
  return PurePosixPath(str(p)) # No open/stat/resolve or filesystem/symlink claim.
 names=("rec","read","verify","dump","query","cpu","main","audit","contracts","seal_ledger","software_ready","frozen_sources","reviewed_sources","source_metadata","original_source_binding","root_accounting_queries","journal_chain","verify_journal_ledger")
 try:
  saved["path"]=module.path;module.path=scalar_path
  for name in names:saved[name]=getattr(module,name);setattr(module,name,deny)
  yield
 finally:
  for name,value in saved.items():setattr(module,name,value)
def indexed_journal(scope,module,ledger):
 closure=input_json(scope,ledger["journal_closure"])
 need(closure["status"]=="ROOT_SUBMISSION_JOURNAL_CHAIN_CPU_SEALED","Saved actual journal closure")
 rows=closure["journal_receipts"];need(rows and len({r["path"]for r in rows})==len(rows),"Exact unique journal universe")
 table={r["path"]:r for r in rows};chain=[];seen=set();current=closure["final_journal"]
 while True:
  need(current["path"]not in seen and current["path"]in table and current==table[current["path"]],"Indexed exact journal predecessor/cycle")
  seen.add(current["path"]);doc=input_json(scope,current);module.journal_contract(doc);chain.append((current,doc))
  prior=doc.get("previous_journal_path")
  if prior is None:break
  need(prior in table,"Undeclared journal predecessor");current=table[prior]
 chain.reverse();need([r for r,_ in chain]==rows,"All exact journals/order observed, no omitted branches")
 for (_,a),(_,b)in zip(chain,chain[1:]):module.journal_prefix(a,b)
 entries=[]
 for e in chain[-1][1]["entries"]:
  matches=[r for r in closure["controller_receipts"]if r["path"]==e["receipt_path"]]
  need(len(matches)==1,"Exactly one current controller full tuple")
  input_bytes(scope,matches[0]);entries.append({**{k:v for k,v in e.items()if k!="receipt_path"},"receipt":matches[0]})
 need(same_json(entries,ledger["entries"])and same_json(entries,closure["entries"])and [e["receipt"]for e in entries]==closure["controller_receipts"],"Exact journal/ledger/closure/current controller identity")
 return closure,[r for r,_ in chain]
def rebuild_dispatches(scope,module,ledger,acceptance):
 entries,end=module.ledger_contract(ledger)
 need([e["receipt"]for e in entries]==acceptance["root_gpu_submission_receipts"],"Accepted current root controllers bound to ledger")
 controllers=[input_json(scope,e["receipt"])for e in entries]
 e2e=[c["result_dir"]for e,c in zip(entries,controllers)if e["phase"]=="reference_free_e2e"]
 rebuilt=[]
 with pure_cost_context(module,e2e):
  indexed_journal(scope,module,ledger)
  for e,c in zip(entries,controllers):
   launcher=input_bytes(scope,c["launcher"]).decode("utf-8")
   if c.get("entry")is not None:input_bytes(scope,c["entry"])
   if e["phase"]=="formal_generation":input_bytes(scope,c["resource_policy"])
   rebuilt.append(module.submission_contract(e,c,lambda r:input_json(scope,r),launcher))
 need(len({d["job_id"]for d in rebuilt})==len(rebuilt)and sum(d["job_id"]=="13260"and d["kind"]=="primary"for d in rebuilt)==1,"Unique actual root numeric dispatch/formal primary")
 need(same_json(rebuilt,acceptance["dispatches"]),"Dispatches independently rebuilt from exact indexed parents")
 return rebuilt,end,e2e
def query_stream(scope,r,argv):
 q=input_json(scope,r)
 need(q["argv"]==argv and type(q["returncode"])is int and q["returncode"]==0 and q["TZ"]=="UTC"and q["SLURM_TIME_FORMAT"]=="standard","Exact saved successful independent accounting query")
 stdout=input_bytes(scope,q["stdout"]);stderr=input_bytes(scope,q["stderr"])
 need(stderr==b"","Actual saved accounting query stderr differs")
 return stdout.decode("utf-8"),q
def replay_streams(scope,module,dispatches,ledger,explicit_query,universe_query,saved_closure):
 ids=sorted({d["job_id"]for d in dispatches},key=int)
 e,ec=query_stream(scope,explicit_query,["sacct","-n","-P","-j",",".join(ids),"--format="+module.FIELDS])
 u,uc=query_stream(scope,universe_query,module.time_universe_argv(ledger))
 # Pure call: no other scope/query/code/writer entry is called.
 actual=module.close_rows(dispatches,e,u,module.utc(ledger["scope_end_utc"]))
 saved=input_json(scope,saved_closure)
 need(same_json(actual,saved),"Entire reconstructed closure differs, including rows/steps/flags/order/failures/concurrency")
 return actual,e,u
def select_unknown(scope,p,expected_size=None):
 r=select_index(scope,str(p))
 if expected_size is not None:need(r["bytes"]==expected_size,"Indexed unknown-SHA metadata size differs")
 return r
def saved_terminal(scope,seal_path,seal_size,jid,acceptance,key,expected_status):
 sr=select_unknown(scope,seal_path,seal_size);s=input_json(scope,sr)
 need(s["schema"]==("root-cost-v3-software-actual-terminal-metadata-only.v1"if jid=="14565"else"root-cost-v3-full-audit-actual-terminal-metadata-only.v1")and s["status"]==expected_status and s[key]==acceptance and s.get("metadata_only")is True and s.get("bytes_inode_mtime_unchanged")is True and s.get("mode_changes_only")is True,"Indexed terminal seal/status/accepted tuple")
 bound=input_json(scope,acceptance);need(s["allocation"]==bound["allocation"]and s["source"]==bound["source"],"Indexed completed producer source/allocation tie")
 if jid=="14565":
  ct=input_json(scope,bound["contracts"]);need(s["original_source"]==bound["original_source"]and s["contracts"]==bound["contracts"]and s["log"]==ct["log"]and s["contract_counts"]==dict(tests_run=88,failures=0,errors=0,skipped=0)and s["whole_original_frozen_compile_bash_source_qualification_PASS"]is True and s["original_source_prepost_metadata"]==bound["original_source_metadata_before"]and s["no_full_Cost_or_scientific_acceptance"]is True and s["no_GPU_submission"]is True,"Exact actual software terminal qualification")
 else:
  for k in("software_acceptance","ledger","journal_closure","root_gpu_submission_receipts","terminal_numeric_accounting_receipts","active_scope_query","CPU13266_unallocated_history"):
   sk={"software_acceptance":"software","root_gpu_submission_receipts":"current_root_gpu_receipts","terminal_numeric_accounting_receipts":"numeric_accounting_receipts","CPU13266_unallocated_history":"unallocated_history"}.get(k,k)
   need(s[sk]==bound[k],"Actual Cost terminal declared graph differs: "+k)
  need(s["actual_full_cost_status"]==bound["status"]and s["no_scientific_acceptance"]is True and s["no_new_GPU_or_ACTIVE_change"]is True and s["scope_start_utc"]==bound["scope_start_utc"]and s["scope_end_utc"]==bound["scope_end_utc"]and same_json(s["saved_CPU_scalar_results"],{k:bound[k]for k in("actual_GPU_seconds","allocated_failure_GPU_seconds","actual_current_scope_maximum_concurrent_GPUs")}),"Actual Cost terminal scope")
 q=s["terminal_query"];need(q["returncode"]==0 and q["TZ"]=="UTC"and q["SLURM_TIME_FORMAT"]=="standard","Saved terminal query protocol")
 need(q["argv"]==["sacct","-n","-P","-j",jid,"--format=JobID,JobName%256,User%64,Account%64,Partition,State,ExitCode,ElapsedRaw,AllocTRES,Submit,Start,End,Timelimit,AllocCPUS,ReqMem"],"Exact historical terminal request")
 r=select_unknown(scope,q["stdout"],q["stdout_bytes"]);err=select_unknown(scope,q["stderr"],q["stderr_bytes"])
 lines=[v for v in input_bytes(scope,r).decode().splitlines()if v.strip()];need(input_bytes(scope,err)==b""and q["selected_row"]in lines,"Indexed raw terminal selected row/stderr")
 selected=q["selected_row"].split("|")
 need(len(selected)==15 and selected[:7]==[jid,"ppi_root_gpu_cost_cpu",USER,USER,"organ","COMPLETED","0:0"]and selected[7]==("20"if jid=="14565"else"13")and selected[13]=="1"and tres(selected[8])["cpu"]=="1","Actual saved completed CPU1 producer, not a live query")
 before=s["files_before"];after=s["files_after"];need(len(before)==len(after)==(5 if jid=="14565"else18)and len({r["path"]for r in after})==len(after),"Unique exact sealed metadata universe")
 for a,b in zip(before,after):
  need(all(same_json(a[k],b[k])for k in("path","bytes","inode","mtime_ns"))and b["mode"]=="0444"and b["regular"]is True and b["symlink"]is False,"Original terminal metadata-only seal changed input identity")
  rr=select_unknown(scope,b["path"],b["bytes"]);input_bytes(scope,rr)
 return sr,s
def cost_content(scope,module,acceptance_receipt,software_receipt):
 a=input_json(scope,acceptance_receipt)
 need(a["schema"]=="root_current_gpu_cost_closure.v1"and a["status"]==module.ACCEPTED and a["software_acceptance"]==software_receipt,"Exact original Cost acceptance/source")
 need(a["source"][0]==COST_ENTRY and a["source"]==input_json(scope,software_receipt)["source"],"Actual Cost/SWA/code source4 identity")
 for key in("complete_root_gpu_submission_universe","allocated_failure_before_manifest_cost_retained"):need(a.get(key)is True,"Accepted cost must cover complete universe/positive failure")
 need(a.get("scientific_output_acceptance")is False and a.get("whole_historical_project_cost_claim")is False and a.get("new_GPU_submission")is False and a.get("ACTIVE_changed")is False,"Root-cost-only accepted scope")
 ledger=input_json(scope,a["ledger"]);dispatches,end,e2e=rebuild_dispatches(scope,module,ledger,a)
 need(a["journal_closure"]==ledger["journal_closure"]and a["scope_start_utc"]==ledger["scope_start_utc"]and a["scope_end_utc"]==ledger["scope_end_utc"]and a["job_name_scope"]==module.SCOPE_NAME.pattern,"Cost exact closed scope/journal")
 previous=ledger.get("previous_ledger")
 if previous:
  prior=input_json(scope,previous);module.ledger_contract(prior)
  need(same_json(ledger["entries"][:len(prior["entries"])],prior["entries"])and module.utc(prior["scope_end_utc"])<=end,"Previous indexed ledger prefix/window changed")
 common=input_json(scope,ledger["common_preflight"]);need(common.get("status")=="COMMON_SUCCESSOR_CPU_PREFLIGHT_ACCEPTED_ROOT_PENDING_ONLY_GPU_SUBMISSION_REQUIRED","Actual current common scope")
 prim=[d for d in dispatches if d["phase"]=="common_review"and d["kind"]=="primary"]
 if common["root_pending_job_indices"]:need(len(prim)==1 and prim[0]["preflight"]==ledger["common_preflight"],"Current common primary universe")
 else:need(not prim,"No pending common jobs but submitted primary")
 physical=input_json(scope,ledger["physical_preflight"]);need(physical.get("status")=="CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED"and physical.get("GPU_allocated")==0,"Actual current physical scope")
 e2e_dispatch=[d for d in dispatches if d["phase"]=="reference_free_e2e"]
 if ledger["e2e_disposition"]=="upstream_rejected":need(physical["qualified_prediction"]["status"]=="POSE_REJECTED"and not e2e_dispatch,"Physical rejection excludes forced model stages")
 else:need(physical["qualified_prediction"]["status"]=="POSE_ACCEPTED"and e2e_dispatch and all(d["preflight"]==ledger["physical_preflight"]for d in e2e_dispatch),"Attempted E2E exact accepted physical source")
 rows=a["terminal_numeric_accounting_receipts"];need(len(rows)==4 and rows[3]==a["terminal_costs"],"Exact original numeric receipt shape")
 closed,e,u=replay_streams(scope,module,dispatches,ledger,rows[0],rows[1],rows[3])
 need(same_json(module.preliminary_inventory(e,u),input_json(scope,rows[2])),"Original preclosure inventory independently reconstructed")
 need(a["actual_GPU_seconds"]==closed["actual_GPU_seconds"]and a["allocated_failure_GPU_seconds"]==closed["allocated_failure_GPU_seconds"]and a["actual_current_scope_maximum_concurrent_GPUs"]==closed["actual_maximum_current_scope_concurrent_GPUs"],"Original saved totals equal independently replayed values")
 # Original queue and unallocated CPU history are indexed captured evidence; never queried.
 queued,_=query_stream(scope,a["active_scope_query"],["squeue","-h","-u",USER,"-o","%i|%.256j|%T|%b"])
 for line in queued.splitlines():
  v=[x.strip()for x in line.split("|")];need(len(v)==4 and(not module.SCOPE_NAME.fullmatch(v[1])or"gpu"not in v[3].lower()),"Saved original neural scope was active/unregistered")
 h=input_json(scope,a["CPU13266_unallocated_history"])
 raw,hq=query_stream(scope,h["query"],["sacct","-n","-P","-j","13266","--format="+module.FIELDS])
 hr,hs=module.parse_accounting(raw);selected=[v for v in hr if v["logical_id"]=="13266"]
 need(len(selected)==1 and selected[0]["GPU_count"]==0 and selected[0]["elapsed_seconds"]==0 and selected[0]["state"]=="CANCELLED"and not selected[0]["AllocTRES"]and same_json(selected[0],h["row"])and same_json(hs,h["excluded_steps"])and h["not_GPU_submission"]is True and h["not_current_physical_preflight"]is True and h["no_scientific_run"]is True,"Original zero/unallocated CPU history exact")
 return dict(status=CONTENT,scope=SCOPE,original_cost_acceptance=acceptance_receipt,original_cost_software=software_receipt,ledger=a["ledger"],complete_closed_object=closed,full_original_closure_independently_equal=True,no_explicit_fill=True,no_live_accounting_query=True,scientific_recomputation_performed=False,scientific_acceptance=False,new_GPU=False,ACTIVE_changed=False)

def validate_cost(scope,module):
 result=cost_content(scope,module,COST_A,COST_SW)
 a=input_json(scope,COST_A);closed=result["complete_closed_object"]
 need(len(a["dispatches"])==4 and closed["expected_submitted_allocation_slots"]==closed["allocated_GPU_jobs"]==298 and closed["zero_unallocated_cancels"]==0 and(closed["actual_GPU_seconds"],closed["allocated_failure_GPU_seconds"],closed["actual_maximum_current_scope_concurrent_GPUs"])==(143583,312,2),"Actual fixed ROOT298 totals/universe")
 swr,swseal=saved_terminal(scope,COST_SW_SEAL,14649,"14565",COST_SW,"software","ACTUAL_COST_V3_SOFTWARE88_TERMINAL_METADATA_READBACK_PASS_NOT_FULL_COST")
 ar,aseal=saved_terminal(scope,COST_SEAL,24087,"14576",COST_A,"actual_full_cost_acceptance","ACTUAL_FULL_NUMERIC_COST_TERMINAL_METADATA_READBACK_PASS_NOT_SCIENTIFIC_ACCEPTANCE")
 need(swseal["source"]==aseal["source"]==a["source"]and aseal["ledger"]==a["ledger"]and aseal["journal_closure"]==a["journal_closure"],"Both exact producer terminal/source/ledger bindings")
 result["saved_producer_terminal_seals"]=[swr,ar]
 return result

def extraction_marker_guard(pkg,root,package_receipt,m):
 need(m.get("status")=="RESTORED_HASHES_VERIFIED_CONTENT_RECOMPUTATION_PENDING"and m.get("package")==package_receipt and m.get("authority_root")==str(R)and m.get("restore_root")==str(root)and type(m.get("files_verified"))is int and m["files_verified"]==len(pkg["manifest"]),"Exact unchanged-core extraction control")
def restore_scope(reader,package_receipt,root,out,owned,software_control,derived_controls):
 pkg=parse_json(exact(package_receipt));root=local(root);out=local(out)
 need(pkg["authority_root"]==str(R)and root!=R and root.is_dir()and out.is_relative_to(root)and out!=root and not out.exists(),"Separate actual restore root/new absent output")
 marker=rec(root/"RESTORE_HASH_ACCEPTANCE.json");extraction_marker_guard(pkg,root,package_receipt,parse_json(exact(marker)))
 for r in derived_controls:
  p=local(r["path"]);need(p.is_relative_to(root)and not p.is_relative_to(out),"Prerequisite output controls confined to same root/outside new output");exact(r)
 controls=[package_receipt,marker,software_control]+derived_controls
 base=reader.StrictIndex(pkg,root,out,controls=controls,owned=owned)
 config=input_json(base,pkg["config"]);aliases=input_json(base,config["resource_aliases"])if config.get("resource_aliases")else{}
 scope=reader.StrictIndex(pkg,root,out,aliases=aliases,controls=controls,owned=owned)
 input_bytes(scope,software_control);input_bytes(scope,pkg["config"])
 return scope,pkg,marker
def prerequisite_outputs(reader,pkg,root,package_receipt,marker,raw_r,metadata_r):
 # These exact postarchive outputs are controls, never SOURCE/index exceptions or archive prerequisites.
 raw=parse_json(exact(raw_r));meta=parse_json(exact(metadata_r))
 need(raw.get("status")=="INDEPENDENT_RESTORE_RAW_CONTENT_RECOMPUTATION_ACCEPTED"and raw.get("package")==package_receipt and raw.get("restore_root")==str(root)and raw.get("hash_acceptance")==marker and raw.get("original_scientific_evidence_read")is False,"Actual F full RAW prerequisite same package/root")
 ir=raw["strict_restored_package_index_acceptance"];sealr=raw["restored_input_metadata_readonly_seal"]
 for r in (ir,sealr):
  need(local(r["path"]).is_relative_to(root),"Exact derived F proof remains below same restore root");exact(r)
 ip=parse_json(exact(ir));sealed=parse_json(exact(sealr))
 need(ip["schema"]==reader.SCHEMA and ip["status"]==reader.STATUS and ip["indexed_file_n"]==len(pkg["manifest"])and ip["live_scientific_fallback"]is False and ip["unindexed_original_input_allowed"]is False and ip["source_JSON_rewritten"]is False and ip["whole_executing_source_pre_and_post_byte_readback_PASS"]is True,"Actual whole indexed F RAW proof, not old software130 alone")
 need(sealed["package"]==package_receipt and sealed["restore_root"]==str(root),"Actual F readonly restored input seal")
 need(meta.get("schema")=="restored-common13460-metadata-content.v1"and meta.get("status")=="RESTORED_COMMON13460_AND_J6_EXACT_INDEX_METADATA_CONTENT_ACCEPTED_NOT_SCIENCE"and meta.get("package_control")==package_receipt and meta.get("hash_extraction_control")==marker and meta.get("production_restore_verified")is True and meta.get("late_postarchive_receipt")is True and meta.get("archive_source_report_creation_prerequisite")is False and meta.get("only_two_aliases")is True and meta.get("separate13315_and13460_qualifications")is True,"Actual G13460/J6 prerequisite, same package/root")
 gp=meta["strict_restored_index_proof"];need(gp["indexed_file_n"]==len(pkg["manifest"])and gp["live_scientific_fallback"]is False and gp["unindexed_original_input_allowed"]is False and gp["source_JSON_rewritten"]is False,"G metadata strict restored-index proof")
 return [ir,sealr]
def software_evidence(scope,sw,sr):
 fs=sw["source_files"];source_set(scope,fs,4,FILES);source_set(scope,sw["original_executing_sources"],4,FILES);pair_lists(sw["original_executing_sources"],fs,FILES)
 ct=counts(scope,sw["contracts"],TESTS,fs);need(ct.get("source_files")==fs and ct.get("genuine_unchanged_core_package_extract")is True,"Actual new contract/source universe")
 need(sw.get("original_and_frozen_sources_byte_identical")is True and sw.get("original_prepost_verified")is True,"Actual original/frozen qualification")
 snap=input_json(scope,sw["source_snapshot"])
 need(same_json(sw["original_metadata_before"],sw["original_metadata_after"])and same_json(snap["original_metadata_before"],sw["original_metadata_before"])and snap["frozen_source_files"]==fs and snap["original_executing_sources"]==sw["original_executing_sources"]and snap["compile_owned_Python"]is True and snap["bash_returncode"]==0 and snap["allocation"]==sw["allocation"],"New archived software source/compile snapshot")
 need(sw["allocation"]["job_id"]==sw["actual_CPU_job_id"]and sw["allocation"]["allocated_CPUs"]==1 and sw["allocation"]["allocated_GPUs"]==0,"New actual software allocation")
 for r in sw["code_dependencies"]["archived_qualification_evidence"]:input_bytes(scope,r)
 # Future root captures saved software terminal metadata BEFORE source/package creation; never live sacct.
 jid=sw["actual_CPU_job_id"];r=select_unknown(scope,S/"submissions"/("restored_root298_cost_software_"+jid+"_actual_terminal_seal")/"receipt.json")
 terminal=input_json(scope,r)
 need(terminal["schema"]=="restored-root298-cost-software-terminal-seal.v1"and terminal["status"]=="ACTUAL_SOFTWARE_TERMINAL_METADATA_READBACK_PASS_NOT_REAL_COST_RESTORE"and terminal["software_acceptance_CPU_stdout_descriptor"]==sr and terminal["source_files"]==fs and terminal["metadata_only"]is True,"Actual new indexed software terminal/source binding")
 q=terminal["actual_terminal"]
 need(q["argv"]==["sacct","-X","-n","-P","-j",jid,"--format=JobID,JobName%128,User%64,Account%64,Partition%64,State,ExitCode,ElapsedRaw,AllocTRES"]and q["returncode"]==0 and q["stderr"]=="","Saved exact new software terminal")
 lines=[v for v in q["stdout"].splitlines()if v.strip()];need(len(lines)==1,"One indexed new software terminal")
 v=lines[0].split("|");need(len(v)==9 and v[:7]==[jid,JOB_NAME,USER,USER,"organ","COMPLETED","0:0"]and v[7].isdigit()and tres(v[8])["cpu"]=="1","Actual new software completed CPU1/GPU0")
 return r
def write_scoped(scope,out,name,obj):
 target=scope.output(Path(out)/name);target.parent.mkdir(parents=True,exist_ok=True)
 with target.open("xb")as f:
  f.write(jbytes(obj));f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 return scope.rec(target)
def run_verify(args,allocation):
 sr=rec(args.software);need(sr["sha256"]==args.software_sha,"New actual checker execution control")
 sw=parse_json(exact(sr));need(sw["schema"]=="restored-root298-cost-software.v1"and sw["status"]==SOFTWARE and sw["compiled_owned_Python"]is True and sw["bash_syntax_PASS"]is True and sw["original_prepost_verified"]is True and sw["production_restore_verified"]is False and sw["science_accepted"]is False,"New software-only source qualification")
 fs=sw["source_files"];need(len(fs)==4 and [Path(r["path"]).name for r in fs]==list(FILES)and all(Path(r["path"]).parent==D for r in fs)and D==S/"frozen"/("restored_root298_cost_verifier_v1_"+sw["actual_CPU_job_id"])/"code"and fs[0]["path"]==str(Path(__file__).absolute()),"Actual qualified frozen executing checker OWN4")
 need(set(p.name for p in D.iterdir())==set(FILES)and not(D.stat().st_mode&0o222),"Readonly exact executing source4")
 for r in fs:exact(r)
 code=sw["code_dependencies"];need(code["reader"]==READER and code["cost_entry"]==COST_ENTRY and code["core_for_software_fixtures_only"]==CORE and code["cost_software"]==COST_SW,"Finite exact CODE/source dependencies")
 reader=load("root298_strictindex_reader",READER);runtime=sw["conditional_core_runtime"]
 need(runtime["logical_executable"]==str(R/"env/core/bin/python")==sys.executable,"Actual qualified core interpreter")
 reader.verify_runtime(runtime)
 pr=rec(args.package);need(pr["sha256"]==args.package_sha,"Exact actual package control")
 rawr=rec(args.raw_restore);metar=rec(args.metadata_restore)
 need(rawr["sha256"]==args.raw_restore_sha and metar["sha256"]==args.metadata_restore_sha,"Exact actual F/G late output controls")
 scope,pkg,marker=restore_scope(reader,pr,args.restore_root,args.out,fs+[READER],sr,[rawr,metar])
 extra=prerequisite_outputs(reader,pkg,scope.root,pr,marker,rawr,metar)
 for r in extra:scope.controls[r["path"]]=r
 terminal=software_evidence(scope,sw,sr);scope.after(touched_only=True)
 module,oldsw=indexed_cost_module(scope)
 # Cost module was compiled only from exact INDEXED qualified bytes; no live source fallback.
 result=validate_cost(scope,module)
 scope.after(touched_only=True);reader.verify_runtime(runtime)
 for r in fs+[READER]:exact(r)
 out=Path(args.out);scope.output(out).mkdir(exist_ok=False)
 closed=result.pop("complete_closed_object");closedr=write_scoped(scope,out,"recomputed_root_gpu_cost.json",closed)
 scope.after(touched_only=True);reader.verify_runtime(runtime)
 for r in fs+[READER]:exact(r)
 target=scope.output(out/"acceptance.json")
 with target.open("xb")as f:
  result.update(schema="restored-root298-cost-content.v1",actual_CPU_job_id=allocation["job_id"],allocation=allocation,package_control=pr,hash_extraction_control=marker,restore_root=str(scope.root),checker_software_execution_control=sr,source_files=fs,code_dependencies=code,conditional_core_runtime=runtime,software_indexed_terminal_proof=terminal,previous_full_RAW_restore=rawr,previous_13460_metadata_restore=metar,recomputed_root_cost=closedr,strict_restored_index_proof=scope.proof(),production_restore_verified=True,late_postarchive_receipt=True,archive_source_report_creation_prerequisite=False,verification_scope="ROOT298_ACCOUNTING_ONLY_FULL_RAW_AND13460_METADATA_SEPARATE_PRIOR_GATES")
  f.write(jbytes(result));f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 print(json.dumps(dict(status=CONTENT,acceptance=scope.rec(target)),ensure_ascii=False))
def run_contracts(allocation,original,frozen,out,code):
 module=load("root298_checker_contracts",frozen[1]);module.CHECKER=sys.modules[__name__];module.READER=load("root298_fixture_reader",READER);module.CORE=load("root298_fixture_core",CORE);module.COST=load("root298_fixture_cost_pure",COST_ENTRY)
 runtime=module.READER.runtime_descriptor(sys.executable);need(runtime["logical_executable"]==str(R/"env/core/bin/python"),"Qualified conditional core runtime");module.READER.verify_runtime(runtime)
 suite=unittest.defaultTestLoader.loadTestsFromModule(module);need(suite.countTestCases()==TESTS,"Actual standalone new fixture definitions")
 with (out/"contracts.txt").open("x")as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite);log.flush();os.fsync(log.fileno());os.fchmod(log.fileno(),0o444)
 ct=dump(out/"contracts.json",dict(status="PASS"if result.wasSuccessful()else"FAIL",tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),source_files=frozen,tested_source_files=frozen,log=rec(out/"contracts.txt"),genuine_unchanged_core_package_extract=True,scope="SYNTHETIC_ACCOUNTING_METADATA_FIXTURES_ONLY_NOT_REAL_RESTORE"))
 need(result.wasSuccessful()and result.testsRun==TESTS and not result.skipped,"New standalone software fixtures")
 module.READER.verify_runtime(runtime);own(original,frozen)
 snapshot=parse_json(exact(rec(out/"source_snapshot.json")));after=metadata(original)
 need(snapshot["original_metadata_before"]==after,"Original executing source metadata unchanged before acceptance")
 for r in code["archived_qualification_evidence"]+[READER,COST_ENTRY,CORE]:exact(r)
 a=dump(out/"acceptance.json",dict(schema="restored-root298-cost-software.v1",status=SOFTWARE,actual_CPU_job_id=allocation["job_id"],allocation=allocation,source_files=frozen,original_executing_sources=original,original_and_frozen_sources_byte_identical=True,original_prepost_verified=True,original_metadata_before=snapshot["original_metadata_before"],original_metadata_after=after,contracts=ct,code_dependencies=code,source_snapshot=rec(out/"source_snapshot.json"),compiled_owned_Python=True,bash_syntax_PASS=True,conditional_core_runtime=runtime,production_restore_verified=False,science_accepted=False,no_GPU_submission=True,ACTIVE_changed=False))
 print(json.dumps(dict(status=SOFTWARE,acceptance=a),ensure_ascii=False))
def main():
 p=argparse.ArgumentParser();sp=p.add_subparsers(dest="mode",required=True);sp.add_parser("contracts");v=sp.add_parser("verify")
 for key in("software","software-sha","package","package-sha","restore-root","out","raw-restore","raw-restore-sha","metadata-restore","metadata-restore-sha"):v.add_argument("--"+key,required=True)
 args=p.parse_args();allocation=cpu()
 if args.mode=="verify":run_verify(args,allocation);return
 need(D==S/"pending/restored_root298_cost_verifier_v1"and set(p.name for p in D.iterdir())==set(FILES)and not(D.stat().st_mode&0o222),"Exact reviewed readonly original OWN4")
 original=[rec(D/n)for n in FILES];before=metadata(original)
 fd=S/"frozen"/("restored_root298_cost_verifier_v1_"+allocation["job_id"])/"code";fd.mkdir(parents=True,exist_ok=False);frozen=[]
 for r in original:
  target=fd/Path(r["path"]).name
  with target.open("xb")as f:f.write(exact(r));f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
  frozen.append(rec(target))
 fd.chmod(0o555);fd.parent.chmod(0o555);own(original,frozen)
 out=S/"runs"/("restored_root298_cost_software_"+allocation["job_id"]);out.mkdir(exist_ok=False)
 for r in frozen:
  if Path(r["path"]).suffix==".py":compile(exact(r),r["path"],"exec")
 b=subprocess.run(["bash","-n",str(fd/"checker_cpu.sbatch")],text=True,capture_output=True);need(b.returncode==0,"Launcher syntax")
 dump(out/"source_snapshot.json",dict(original_executing_sources=original,frozen_source_files=frozen,original_metadata_before=before,compile_owned_Python=True,bash_argv=b.args,bash_returncode=b.returncode,bash_stdout=b.stdout,bash_stderr=b.stderr,allocation=allocation))
 code=code_qualification();sealed=load("restored_root298_sealed_checker",frozen[0])
 sealed.run_contracts(allocation,original,frozen,out,code)
if __name__=="__main__":main()
