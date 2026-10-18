#!/usr/bin/env python3
"""Exact addition-only common13423 controller metadata amendment; root-owned CPU only."""
import argparse,copy,datetime,fcntl,hashlib,importlib.util,io,json,os,re,stat,subprocess,sys,traceback,unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
S=R/"steps/24_benchmark_delivery"
USER="u21111210118"
D=Path(__file__).absolute().parent
FILES=("amendment.py","test_amendment.py","amendment_cpu.sbatch","HANDOFF.md")
TESTS=20
OWN_JOB_NAME="test9_common13423_metadata_amendment_v1"
P=S/"submissions/formal_common_pending_from13422_primary_claim/root_submission.json"
SUBMIT=P.parent/"submit_receipt.json"
J5=S/"submissions/root_gpu_journal/0005_formal_common_from13422.json"
EXTRA_KEYS=("raw_sbatch_stdout","raw_sbatch_stderr")
ACCEPTED="COMMON13423_ADDITION_ONLY_CONTROLLER_METADATA_CPU_ACCEPTED_NOT_SCIENCE_COST_OR_NEW_GPU"
OWN_STATUS="METADATA_ONLY_NOT_SCIENCE_COST_OR_NEW_GPU"
def pin(rel,n,h):return dict(path=str(R/rel),bytes=n,sha256=h)
COST_A=pin("steps/24_benchmark_delivery/runs/root_gpu_cost_contracts_13277/acceptance.json",3766,"c0a5d380dc18d12fdfa0ded176a5b89374211827a4f85a9d3f50b922374241e8")
COMMON_A=pin("steps/24_benchmark_delivery/runs/common_successor_contracts_13269/acceptance.json",6429,"da595226c4a6db5b0fd6ebcfdce9d29e92362fb76d849e15941d0ca5c4a8886d")
PREFLIGHT=pin("steps/24_benchmark_delivery/runs/formal_common_preflight_13407_13409/preflight.json",889318,"e30b4e61c45d8de80701d82199fda1d6c79176e9092d2a0f91c40e05598589e0")
PREVIOUS_AMENDMENT=pin("steps/25_reference_free_e2e/runs/controller_metadata_amendment_13315/acceptance.json",3901,"1d51a4002b690e569df1bbf6e07ac7fda62cd69dd05642535d064179eb93728d")
JOURNAL_ENTRIES=[
 dict(submission_id="formal13260",phase="formal_generation",kind="primary",receipt_path=str(R/"steps/22_matched_benchmark/formal_submission_13260/submit_receipt.json")),
 dict(submission_id="e2e_design_13304",phase="reference_free_e2e",kind="primary",receipt_path=str(R/"steps/25_reference_free_e2e/submissions/physical13294_e2e_design_primary_claim/submit_receipt.json")),
 dict(submission_id="e2e_evaluate_13311",phase="reference_free_e2e",kind="primary",receipt_path=str(R/"steps/25_reference_free_e2e/submissions/e2e_evaluate_after13309_primary_claim/submit_receipt.json")),
 dict(submission_id="formal_common_13423",phase="common_review",kind="primary",receipt_path=str(P))]
EXPECTED_OLD_KEYS={"array_job_id","cached_indices_not_rerun","concurrency_cap","entry","indices","launcher","owned_GPU_before","preflight","raw_stderr","raw_stdout","root_controller","schema","source_or_settings_changes","status","submit_argv","submitted_at_epoch","submitted_at_utc"}
COST_NAMES={"root_gpu_cost_audit.py","test_root_gpu_cost_audit.py","root_gpu_cost_cpu.sbatch","HANDOFF.md"}
COMMON_NAMES={"common_review_successor.py","test_common_review_successor.py","successor_bootstrap.py","common_review_cpu.sbatch","common_review_gpu.sbatch","intrinsic_clearance.py","HANDOFF.md"}
def need(v,msg):
 if not v:raise ValueError(msg)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def safe(p):
 p=Path(p);need(p.is_absolute() and p.is_relative_to(R) and p.resolve()==p,"Project absolute nonsymlink authority required: "+str(p))
 return p
def shape(r):
 need(isinstance(r,dict) and set(r)=={"path","bytes","sha256"},"Exact three-field receipt required")
 safe(r["path"]);need(type(r["bytes"])is int and r["bytes"]>=0 and isinstance(r["sha256"],str) and re.fullmatch("[0-9a-f]{64}",r["sha256"]),"Exact bytes/SHA required");return r
def metadata(p):
 p=safe(p);s=p.lstat()
 return dict(path=str(p),device=s.st_dev,inode=s.st_ino,mode=stat.S_IMODE(s.st_mode),uid=s.st_uid,gid=s.st_gid,size=s.st_size,mtime_ns=s.st_mtime_ns)
def data(p,readonly=True):
 p=safe(p);s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==os.geteuid(),"Owned regular file required: "+str(p))
 need(not readonly or not(stat.S_IMODE(s.st_mode)&0o222),"Readonly authority required: "+str(p))
 with p.open("rb")as f:b=f.read()
 need(metadata(p)==dict(path=str(p),device=s.st_dev,inode=s.st_ino,mode=stat.S_IMODE(s.st_mode),uid=s.st_uid,gid=s.st_gid,size=s.st_size,mtime_ns=s.st_mtime_ns),"Concurrent metadata change during read")
 return b
def receipt(p,readonly=True):
 b=data(p,readonly);return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def exact(r,readonly=True):
 shape(r);b=data(r["path"],readonly);need(len(b)==r["bytes"] and hashlib.sha256(b).hexdigest()==r["sha256"],"Exact input byte drift: "+r["path"]);return b
def obj(r):return json.loads(exact(r))
def encode(v):return (json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode()
def new_bytes(p,b):
 p=safe(p);need(p.parent.is_dir() and not p.exists(),"Exclusive new metadata output required")
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 try:
  with os.fdopen(fd,"wb")as f:f.write(b);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 except BaseException:raise
 return receipt(p)
def dump(p,v):return new_bytes(p,encode(v))
def allocation_values(v):
 need(isinstance(v,str)and v,"Numeric allocated CPU TRES required");d={}
 for part in v.split(","):
  need("="in part,"Malformed TRES");k,x=part.split("=",1);need(k and x and k not in d,"Duplicate/empty TRES");d[k]=x
 need(d.get("cpu","").isdigit() and int(d["cpu"])>=1,"Positive allocated CPU required")
 nums=[]
 for k,x in d.items():
  if k.startswith("gres/gpu"):
   need(re.fullmatch(r"gres/gpu(?::[A-Za-z0-9_.-]+)?",k)is not None,"Malformed allocated GPU TRES namespace")
   need(x.isdigit(),"Nonnegative integer GPU TRES required");nums.append((k,int(x)))
 aggregate=next((x for k,x in nums if k=="gres/gpu"),0);typed=sum(x for k,x in nums if k!="gres/gpu")
 need(max(aggregate,typed)==0,"CPU helper cannot have allocated GPU")
 return d
def live_record(text,jid,expected_name=None):
 rows=[x for x in text.splitlines()if re.search(r"\bJobId="+re.escape(jid)+r"(?:\s|$)",x)]
 need(len(rows)==1,"Exact unique current CPU record required")
 pairs=re.findall(r"(\w+)=(\S*)",rows[0]);relevant={"JobId","JobName","JobState","UserId","Account","Partition","NumCPUs","TRES","AllocTRES"}
 need(all(sum(k==key for k,_ in pairs)<=1 for key in relevant),"Duplicate relevant actual scontrol field")
 f=dict(pairs)
 need(expected_name is None or f.get("JobName")==expected_name,"Actual named CPU helper differs")
 need(f.get("JobState")=="RUNNING"and f.get("UserId","").startswith(USER+"(")and f.get("Account")==USER and f.get("Partition")=="organ"and f.get("NumCPUs")=="1","Actual RUNNING owner/account/organ/CPU1 required")
 ds=[allocation_values(f[k])for k in ("TRES","AllocTRES")if k in f]
 need(ds and all(d["cpu"]=="1"for d in ds),"Actual CPU1 allocation evidence required")
 need(len(ds)==1 or ds[0]==ds[1],"Live TRES/AllocTRES representations differ")
 return dict(job_id=jid,allocated_CPUs=1,allocated_GPUs=0,selected_scheduler_record=rows[0])
def cpu():
 jid=os.environ.get("SLURM_JOB_ID","");need(jid.isdigit(),"Owned Slurm CPU required before content/hash")
 for k,v in {"CUDA_VISIBLE_DEVICES":"","JAX_PLATFORMS":"cpu","PYTHONNOUSERSITE":"1","PYTHONDONTWRITEBYTECODE":"1","OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1","MKL_NUM_THREADS":"1"}.items():need(os.environ.get(k)==v,"CPU isolation differs: "+k)
 need("PYTHONPATH"not in os.environ,"Injected PYTHONPATH forbidden")
 return live_record(subprocess.check_output(["scontrol","show","job",jid,"-o"],text=True),jid,OWN_JOB_NAME)
def terminal_row(text,jid,cpus):
 rows=[x for x in text.splitlines()if x.strip()and x.split("|",1)[0]==jid]
 need(len(rows)==1,"Exact terminal producer row required")
 v=rows[0].split("|");need(len(v)==9,"Exact nine-column terminal proof required")
 job,name,user,account,partition,state,exitcode,elapsed,tres=v
 need(job==jid and name=={"13277":"ppi_root_gpu_cost_cpu","13269":"ppi_common_successor_cpu"}[jid]and user==USER and account==USER and partition=="organ"and state=="COMPLETED"and exitcode=="0:0"and elapsed.isdigit(),"Actual accepted CPU producer terminal required")
 d=allocation_values(tres);need(int(d["cpu"])==cpus,"Actual producer CPU count differs")
 return dict(job_id=jid,job_name=name,state=state,exit_code=exitcode,elapsed_seconds=int(elapsed),allocated_CPUs=cpus,allocated_GPUs=0,AllocTRES=tres,raw_line=rows[0])
def producer(jid,cpus,out):
 argv=["sacct","-X","-n","-P","-j",jid,"--format=JobID,JobName%128,User%64,Account%64,Partition%64,State,ExitCode,ElapsedRaw,AllocTRES"]
 c=subprocess.run(argv,text=True,capture_output=True);need(c.returncode==0 and not c.stderr.strip(),"Fresh producer sacct unavailable")
 rr=dump(out/("producer_"+jid+".json"),dict(argv=argv,returncode=c.returncode,stdout=c.stdout,stderr=c.stderr,captured_utc=now()))
 return dict(record=terminal_row(c.stdout,jid,cpus),actual_capture=rr)
def load(name,p):
 p=safe(p);spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);need(Path(m.__file__).absolute()==p,"Executing module source differs");return m
def accepted_sources(out):
 ca=obj(COST_A);co=obj(COMMON_A)
 need(ca.get("status")=="ROOT_GPU_COST_AUDITOR_SOFTWARE_CPU_ACCEPTED"and ca.get("no_GPU_submission")is True and ca.get("no_accounting_science_run")is True and ca["allocation"]["job_id"]=="13277","Actual cost software scope differs")
 need(co.get("status")=="COMMON_SUCCESSOR_SOFTWARE_SOURCE_CPU_ACCEPTED_FUTURE_FORMAL_PREPARATION_PENDING"and co.get("no_inference")is True and co.get("no_GPU_submission")is True and co.get("actual_CPU_job_id")=="13269","Actual common software scope differs")
 source=ca["source"]+co["source"]["successor"]
 for rows,names,root in [(ca["source"],COST_NAMES,S/"frozen/root_gpu_cost_v2_13277/code"),(co["source"]["successor"],COMMON_NAMES,S/"frozen/common_review_successor_v5_13269/code")]:
  need(len(rows)==len(names)and {Path(r["path"]).name for r in rows}==names and all(Path(r["path"]).parent==root for r in rows),"Exact accepted source universe required")
  for r in rows:exact(r)
 evidence=[COST_A,COMMON_A]+source
 for a,n in [(ca,76),(co,58)]:
  cs=obj(a["contracts"]);need(cs.get("status")=="PASS"and cs.get("tests_run")==n and cs.get("failures")==0 and cs.get("errors")==0,"Saved actual software counts differ")
  exact(cs["log"]);evidence.extend([a["contracts"],cs["log"]])
 ce=next(r for r in ca["source"]if Path(r["path"]).name=="root_gpu_cost_audit.py");me=next(r for r in co["source"]["successor"]if Path(r["path"]).name=="common_review_successor.py")
 need(ca["entry"]==ce and co["entry"]==me,"Accepted executing contract source differs")
 fresh=dict(cost=producer("13277",1,out),common=producer("13269",2,out))
 cost=load("common13423_amendment_frozen_cost",ce["path"]);common=load("common13423_amendment_frozen_common",me["path"])
 return dict(cost=cost,common=common,common_sources=co["source"]["successor"],source_receipts=source,evidence=evidence,producer_terminal=fresh)
def journal_guard(j):
 need(j.get("schema")=="root-current-gpu-submission-journal.v1"and j.get("authority_root")==str(R)and j.get("scope_start_utc")=="2026-10-11T14:25:00Z","Exact current journal scope required")
 need(j.get("previous_journal_path")==str(S/"submissions/root_gpu_journal/0004_controller_metadata_amendment_13315.json")and j.get("entries")==JOURNAL_ENTRIES,"Exact immutable four-entry journal universe required")
 need(j.get("metadata_only_controller_amendment_CPU_qualifications")==[PREVIOUS_AMENDMENT]and "metadata_only_common_controller_amendment_CPU_qualifications"not in j,"Original13315 qualification retained; no new journal written here")
 return copy.deepcopy(j["entries"][-1])
def old_shape(old,fact,pre):
 need(isinstance(old,dict)and set(old)==EXPECTED_OLD_KEYS,"Exact legacy controller key universe required")
 need(old["schema"]=="formal_common_root_submission.v1"and old["status"]=="ROOT_PENDING_ONLY_COMMON_GPU_SUBMITTED_CONTENT_ACCEPTANCE_PENDING"and type(old["array_job_id"])is str and old["array_job_id"]=="13423","Exact legacy13423 controller required")
 for k,v in [("root_controller",True),("source_or_settings_changes",False),("cached_indices_not_rerun",True)]:need(old[k]is v,"Original controller scope differs: "+k)
 need(type(old["owned_GPU_before"])is int and old["owned_GPU_before"]==0,"Original pre-submit GPU observation differs")
 need(old["preflight"]==PREFLIGHT and type(old["concurrency_cap"])is int and old["concurrency_cap"]==2 and old["indices"]==pre["root_pending_job_indices"]and len(old["indices"])==268 and old["indices"]==sorted(set(old["indices"]))and all(type(i)is int and 0<=i<288 for i in old["indices"]),"Exact actual pending268/cap2 required")
 need(old["raw_stdout"]=="13423\n"and old["raw_stderr"]=="","Actual original raw parsable submission required")
 need(fact.get("returncode")==0 and type(fact.get("returncode"))is int and fact.get("stdout")==old["raw_stdout"]and fact.get("stderr")==old["raw_stderr"]and fact.get("argv")==old["submit_argv"],"Factual submit1598 differs from controller")
 need(type(old["submitted_at_epoch"])is float and old["submitted_at_epoch"]==1791795572.8823664 and old["submitted_at_utc"]=="2026-10-12T08:59:32.882302+00:00","Original actual submission time identity required")
 return old
def json_identical(a,b):
 if type(a)is not type(b):return False
 if isinstance(a,dict):return set(a)==set(b)and all(json_identical(a[k],b[k])for k in a)
 if isinstance(a,list):return len(a)==len(b)and all(json_identical(x,y)for x,y in zip(a,b))
 return a==b
def addition_only(old,new):
 need(isinstance(new,dict)and set(new)==set(old)|set(EXTRA_KEYS)and not(set(old)&set(EXTRA_KEYS)),"Only two new alias keys permitted")
 need(all(json_identical(new[k],v)for k,v in old.items()),"Any existing controller field change forbidden")
 need(new["raw_sbatch_stdout"]==old["raw_stdout"]and new["raw_sbatch_stderr"]==old["raw_stderr"],"Aliases must equal factual original raw fields")
 return new
def proposal(old):
 n=copy.deepcopy(old);n.update(raw_sbatch_stdout=old["raw_stdout"],raw_sbatch_stderr=old["raw_stderr"]);return addition_only(old,n)
def contracts(ctx,sub):
 def fetch(r):
  need(r==PREFLIGHT,"Contract fetch restricted to exact actual preflight")
  exact(r);return ctx["pre"]
 text=exact(sub["launcher"]).decode()
 c=ctx["cost"].submission_contract(ctx["journal_entry"],sub,fetch,text)
 m=ctx["common"].submission_contract(sub,PREFLIGHT,ctx["pre"])
 need(c["job_id"]=="13423"and c["indices"]==sub["indices"]and c["expected_allocation_count"]==268 and m[0]=="13423"and m[1]==sub["launcher"],"Original contract returned different root identity")
 return dict(cost=c,common=dict(job_id=m[0],launcher=m[1]),no_suites_rerun=True)
def before_after(rs,metas):
 for r in rs:exact(r)
 for m in metas:need(metadata(m["path"])==m,"Unchanged input metadata drift: "+m["path"])
 return True
def authority(target,fixture_root=None):
 target=safe(target)
 if fixture_root is None:need(target==P,"Only actual canonical common13423 target permitted")
 else:
  root=safe(fixture_root);need(root.parent==S/"tmp"and root.name.startswith("common_amendment_fixture_")and target==root/"claim/root_submission.json","Only contained owned synthetic fixture target permitted")
 parent=target.parent;ps=parent.lstat();need(stat.S_ISDIR(ps.st_mode)and ps.st_uid==os.geteuid()and stat.S_IMODE(ps.st_mode)==0o555,"Exact owned readonly555 claim parent required")
 need(stat.S_IMODE(target.lstat().st_mode)==0o444,"Canonical immutable444 metadata required")
 return metadata(parent)
def atomic_amend(target,old_bytes,new_bytes,postcheck,job_id,fixture_root=None,precommit=None):
 """Only canonical target, or the finite owned software fixture path; unknown external bytes are never overwritten on rollback."""
 pm=authority(target,fixture_root);need(job_id.isdigit(),"Numeric CPU transaction identity required")
 old=json.loads(old_bytes);new=json.loads(new_bytes);addition_only(old,new)
 need(data(target)==old_bytes,"Canonical byte drift before transaction")
 temp=target.parent/(".common13423_metadata_amendment_"+job_id+".tmp")
 need(not temp.exists()and not temp.is_symlink(),"Exclusive transaction temp absent required")
 record=dict(logical_target_path=str(target),parent_before=pm,temporary_name=temp.name,committed=False,rollback_performed=False,rollback_conflict=False,parent_mode_restored=False)
 dfd=os.open(target.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);oldfd=os.open(target,os.O_RDONLY|os.O_NOFOLLOW)
 primary=None;cleanup=[];owned_temp_inode=None;parent_was_made_writable=False
 try:
  fcntl.flock(oldfd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  need(os.fstat(dfd).st_ino==pm["inode"]and os.fstat(dfd).st_dev==pm["device"],"Claim parent replaced")
  if precommit:precommit()
  need(data(target)==old_bytes and target.lstat().st_ino==os.fstat(oldfd).st_ino,"Canonical replaced or changed before commit")
  os.fchmod(dfd,pm["mode"]|0o200);parent_was_made_writable=True;record["parent_writable_mode"]=stat.S_IMODE(os.fstat(dfd).st_mode)
  owned_temp_inode=new_bytes_file_at(dfd,temp.name,new_bytes)
  need(data(target)==old_bytes and target.lstat().st_ino==os.fstat(oldfd).st_ino,"Canonical concurrency conflict before replace")
  os.replace(temp.name,target.name,src_dir_fd=dfd,dst_dir_fd=dfd);os.fsync(dfd);record["committed"]=True
  newmeta=metadata(target);record["replacement_inode"]=newmeta["inode"];record["replacement_metadata"]=newmeta
  need(data(target)==new_bytes and newmeta["mode"]==0o444,"Actual candidate byte/mode readback differs")
  postcheck(target)
  need(data(target)==new_bytes and metadata(target)==newmeta,"Canonical changed during postcheck")
  record["current_new_verified"]=True
 except BaseException as exc:
  primary=exc;record["exception_type"]=type(exc).__name__;record["exception_text"]=str(exc)
  if record["committed"]:
   try:
    need(data(target)==new_bytes and metadata(target)["inode"]==record["replacement_inode"],"Unknown concurrent replacement; rollback must not overwrite")
    need(not temp.exists(),"Unexpected temp at rollback")
    owned_temp_inode=new_bytes_file_at(dfd,temp.name,old_bytes)
    os.replace(temp.name,target.name,src_dir_fd=dfd,dst_dir_fd=dfd);os.fsync(dfd)
    need(data(target)==old_bytes,"Rollback byte readback differs");record["rollback_performed"]=True
   except BaseException as rollback_exc:record["rollback_conflict"]=True;record["rollback_error"]=str(rollback_exc)
 finally:
  if temp.exists():
   try:
    need(owned_temp_inode is not None and temp.lstat().st_ino==owned_temp_inode and not temp.is_symlink(),"Unknown temporary replacement cannot be removed")
    os.unlink(temp.name,dir_fd=dfd)
   except BaseException as exc:cleanup.append("Own temporary file removal: "+str(exc))
  try:
   if parent_was_made_writable:os.fchmod(dfd,pm["mode"]);os.fsync(dfd)
   after=metadata(target.parent)
   if not parent_was_made_writable:need(after==pm,"Precommit failure must leave all parent metadata unchanged")
   need(after["device"]==pm["device"]and after["inode"]==pm["inode"]and after["uid"]==pm["uid"]and after["gid"]==pm["gid"]and after["mode"]==pm["mode"],"Original parent identity/mode restoration differs")
   record["parent_after"]=after;record["parent_mode_restored"]=True
  except BaseException as exc:cleanup.append("Parent restoration: "+str(exc))
  for descriptor in (oldfd,dfd):
   try:os.close(descriptor)
   except BaseException as exc:cleanup.append("Owned file descriptor close: "+str(exc))
  record["cleanup_errors"]=cleanup
 if primary is not None:
  primary.amendment_transaction=record;raise primary
 if cleanup:
  exc=RuntimeError("Transaction cleanup failed: "+repr(record));exc.amendment_transaction=record;raise exc
 return record
def committed_guard(target,candidate_bytes,transaction):
 need(transaction.get("committed")is True and transaction.get("current_new_verified")is True and transaction.get("parent_mode_restored")is True and not transaction.get("rollback_performed")and not transaction.get("cleanup_errors"),"Successful known atomic transaction required")
 need(data(target)==candidate_bytes and metadata(target)==transaction["replacement_metadata"]and metadata(target)["inode"]==transaction["replacement_inode"],"Unknown current canonical byte/metadata/inode change after commit")
 return receipt(target)
def new_bytes_file_at(dfd,name,b):
 fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=dfd)
 with os.fdopen(fd,"wb")as f:f.write(b);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444);inode=os.fstat(f.fileno()).st_ino
 return inode
def own_readback(original,frozen):
 need(len(original)==len(frozen)==len(FILES)and all(Path(x["path"]).parent==S/"pending/common_root_receipt_metadata_amendment_v1"for x in original)and all(Path(x["path"]).parent==Path(frozen[0]["path"]).parent for x in frozen)and [Path(x["path"]).name for x in original]==list(FILES)and [Path(x["path"]).name for x in frozen]==list(FILES),"Whole OWN4 source universe required")
 for a,b in zip(original,frozen):
  exact(a);exact(b);need(a["bytes"]==b["bytes"]and a["sha256"]==b["sha256"],"Original/frozen executing source differs")
 return True
def perform(allocation,original,frozen,out):
 state=dict(stage="BEFORE_EXTERNAL_QUALIFICATION",canonical_commit_returned=False,old_identity=None,candidate_archive=None,transaction=None,transaction_receipt=None)
 try:return perform_inner(allocation,original,frozen,out,state)
 except BaseException as exc:
  transaction=getattr(exc,"amendment_transaction",None)or state["transaction"]
  source_check=dict(verified=False,error=None)
  try:own_readback(original,frozen);source_check["verified"]=True
  except BaseException as source_exc:source_check["error"]=type(source_exc).__name__+": "+str(source_exc)
  current=dict(logical_path=str(P),observation_available=False)
  try:
   b=data(P);current.update(observation_available=True,observed_bytes=len(b),observed_sha256=hashlib.sha256(b).hexdigest(),metadata=metadata(P))
  except BaseException as read_exc:current["typed_observation_error"]=type(read_exc).__name__+": "+str(read_exc)
  failure=dict(schema="common13423-controller-metadata-amendment-failure.v1",status="METADATA_AMENDMENT_INCOMPLETE_NOT_ACCEPTED",scope=OWN_STATUS,actual_CPU_job_id=allocation["job_id"],allocation=allocation,stage=state["stage"],canonical_commit_returned=state["canonical_commit_returned"],old_identity=state["old_identity"],candidate_archive=state["candidate_archive"],transaction=transaction,transaction_receipt=state["transaction_receipt"],current_canonical_observation_scalar=current,exception_type=type(exc).__name__,exception_text=str(exc),traceback=traceback.format_exc(),original_executing_sources=original,frozen_source_files=frozen,source_postreadback=source_check,no_new_GPU=True,no_journal_write=True,science_accepted=False,cost_closure_accepted=False,no_unsafe_postcommit_rollback=True)
  try:
   fr=dump(out/"failure.json",failure);print(json.dumps(dict(status=failure["status"],failure=fr),ensure_ascii=False))
  except BaseException as proof_exc:
   exc.failure_proof_write_error=type(proof_exc).__name__+": "+str(proof_exc)
   print("Typed incomplete metadata proof write failed; original exception preserved: "+exc.failure_proof_write_error,file=sys.stderr)
  raise
def perform_inner(allocation,original,frozen,out,state):
 need(Path(__file__).absolute()==Path(frozen[0]["path"])and D==S/"frozen"/("common_root_receipt_metadata_amendment_v1_"+allocation["job_id"])/"code","Execute exact current sealed amendment module only")
 need(out==S/"runs"/("common_root_receipt_metadata_amendment_"+allocation["job_id"]),"Only exact current owned output namespace permitted")
 snapshot_r=receipt(out/"source_snapshot.json");snapshot=obj(snapshot_r);syntax=obj(snapshot["syntax"])
 need(snapshot["original_executing_sources"]==original and snapshot["frozen_source_files"]==frozen and snapshot["allocation"]==allocation and snapshot["scope"]==OWN_STATUS,"Actual bootstrap snapshot/source/allocation differs")
 need(syntax.get("compile_owned_Python")is True and syntax.get("bash_returncode")==0 and syntax.get("source_files")==frozen and syntax.get("bash_argv")==["bash","-n",str(D/"amendment_cpu.sbatch")],"Actual owned compile/bash and source binding required")
 own_readback(original,frozen);ctx=accepted_sources(out);state["stage"]="CONTROL_AND_PREFLIGHT_QUALIFICATION"
 control_paths=[J5,P.parent/"submit_receipt.json",P.parent/"submission_in_progress.json",P.parent/"request.json"]+[Path(e["receipt_path"])for e in JOURNAL_ENTRIES[:3]]
 need({p.name for p in P.parent.iterdir()}=={"root_submission.json","submit_receipt.json","submission_in_progress.json","request.json"},"Exact original claim4 file universe required")
 saved=[receipt(p)for p in control_paths];metas=[metadata(p)for p in control_paths]
 need([r["bytes"]for r in saved]==[1792,1598,1574,5349,1874,2755,3626],"Exact original journal/claim/other-controller metadata sizes required")
 old_bytes=data(P);need(len(old_bytes)==5096,"Exact legacy5096 bytes required");old=json.loads(old_bytes);old_meta=metadata(P)
 fact=json.loads(exact(saved[1]));need(saved[1]["bytes"]==1598,"Actual submit1598 metadata required")
 ctx["pre"]=obj(PREFLIGHT);ctx["journal_entry"]=journal_guard(json.loads(exact(saved[0])))
 need(ctx["pre"].get("schema")=="formal_common_successor_preflight.v1"and ctx["pre"].get("status")=="COMMON_SUCCESSOR_CPU_PREFLIGHT_ACCEPTED_ROOT_PENDING_ONLY_GPU_SUBMISSION_REQUIRED"and ctx["pre"].get("no_inference")is True and ctx["pre"].get("root_submission_performed")is False and ctx["pre"]["source"]["successor"]==ctx["common_sources"],"Actual accepted preflight binds software/source7")
 old_shape(old,fact,ctx["pre"]);new=proposal(old)
 need(old["entry"]==next(r for r in ctx["common_sources"]if Path(r["path"]).name=="common_review_successor.py")and old["launcher"]==next(r for r in ctx["common_sources"]if Path(r["path"]).name=="common_review_gpu.sbatch"),"Current root entry/launcher must equal tested Common7")
 evidence=ctx["evidence"]+[PREFLIGHT,PREVIOUS_AMENDMENT]+saved
 before_after(evidence,metas)
 ctx["common"].submission_contract(old,PREFLIGHT,ctx["pre"])
 try:contracts(ctx,old)
 except ValueError as exc:need(str(exc)=="Actual raw parsable submission differs/missing","Legacy cost rejection must be the exact absent raw alias guard");legacy_rejection=dict(type=type(exc).__name__,message=str(exc),expected=True)
 else:raise ValueError("Legacy controller unexpectedly passed COST; wrong scope")
 proposed_contracts=contracts(ctx,new)
 tests=load("common13423_amendment_owned_tests",Path(frozen[1]["path"]));tests.AMEND=sys.modules[__name__];tests.CONTEXT=dict(ctx=ctx,old=old,new=new,fact=fact)
 state["stage"]="OWN_METADATA_GUARD_FIXTURES";suite=unittest.defaultTestLoader.loadTestsFromModule(tests)
 need(suite.countTestCases()==TESTS,"Actual own fixture definition count differs")
 log=out/"contracts.txt"
 with log.open("x")as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 counts=dump(out/"contracts.json",dict(status="PASS"if result.wasSuccessful()else"FAIL",tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),log=receipt(log),scope="OWN_SMALL_METADATA_GUARDS_ONLY_NO76_OR58_SUITE_RERUN",tested_source_files=frozen))
 need(result.wasSuccessful()and result.testsRun==TESTS and not result.skipped,"Own metadata guard contracts failed before canonical mutation")
 own_readback(original,frozen);before_after(evidence,metas);need(data(P)==old_bytes and metadata(P)==old_meta,"Original canonical drift before archive")
 archive=new_bytes(out/"original_root_submission_before_metadata_amendment.json",old_bytes)
 need(exact(archive)==old_bytes,"Readonly archive must equal original bytes")
 old_scalar=dict(logical_original_path=str(P),observed_bytes=5096,observed_sha256=hashlib.sha256(old_bytes).hexdigest(),readonly_archive=archive,original_metadata=old_meta)
 state["old_identity"]=old_scalar
 new_encoded=encode(new);candidate=new_bytes(out/"candidate_root_submission_only_two_aliases.json",new_encoded);state["candidate_archive"]=candidate;state["stage"]="CANONICAL_TRANSACTION"
 def precommit():
  need(cpu()["job_id"]==allocation["job_id"],"Actual owned CPU identity before canonical write")
  own_readback(original,frozen);before_after(evidence,metas);need(data(P)==old_bytes and metadata(P)==old_meta,"Canonical precommit byte/metadata drift")
 def postcheck(target):
  readback=json.loads(data(target));addition_only(old,readback);contracts(ctx,readback)
  own_readback(original,frozen);before_after(evidence,metas);exact(archive)
 transaction=atomic_amend(P,old_bytes,new_encoded,postcheck,allocation["job_id"],precommit=precommit)
 state["canonical_commit_returned"]=True;state["transaction"]=transaction;state["stage"]="DURABLE_POSTCOMMIT_TRANSACTION"
 transaction_r=dump(out/"transaction.json",dict(schema="common13423-addition-only-atomic-transaction.v1",scope=OWN_STATUS,old_identity=old_scalar,candidate_archive=candidate,transaction=transaction))
 state["transaction_receipt"]=transaction_r;state["stage"]="FINAL_METADATA_READBACK_AND_ACCEPTANCE"
 actual=committed_guard(P,exact(candidate),transaction);readback=json.loads(exact(actual));addition_only(old,readback);actual_contracts=contracts(ctx,readback)
 own_readback(original,frozen);before_after(evidence,metas);exact(archive);exact(candidate);exact(transaction_r)
 diff=dump(out/"amendment.json",dict(schema="common13423-controller-metadata-addition-only.v1",scope=OWN_STATUS,old_identity=old_scalar,new_canonical=actual,candidate_archive=candidate,transaction_receipt=transaction_r,added_fields={k:new[k]for k in EXTRA_KEYS},all_original_fields_exactly_preserved=True,actual_factual_submit_receipt=saved[1],legacy_COST_expected_rejection=legacy_rejection,legacy_Common_contract_PASS=True,proposed_contracts=proposed_contracts,current_contracts=actual_contracts,transaction=transaction,journal_0005_unchanged=saved[0],unchanged_three_claim_files=saved[1:4],unchanged_three_other_GPU_controllers=saved[4:],journal_entries_unchanged=JOURNAL_ENTRIES,no_journal_write=True,no_new_GPU=True,no_science_or_settings_change=True))
 acceptance=dict(schema="common13423-controller-metadata-amendment-acceptance.v1",status=ACCEPTED,scope=OWN_STATUS,actual_CPU_job_id=allocation["job_id"],allocation=allocation,old_identity=old_scalar,new_canonical=actual,candidate_archive=candidate,transaction_receipt=transaction_r,amendment=diff,contracts=counts,source_snapshot=snapshot_r,owned_source_syntax=snapshot["syntax"],compiled_owned_Python=True,bash_syntax_passed=True,source_files=frozen,original_executing_sources=original,original_source_entry=original[0],executing_frozen_entry=frozen[0],whole_OWN_source_n=4,external_contract_source_files=ctx["source_receipts"],accepted_COST_software=COST_A,accepted_Common_software=COMMON_A,actual_producer_terminal=ctx["producer_terminal"],preflight=PREFLIGHT,factual_submit_receipt=saved[1],journal_0005_unchanged=saved[0],unchanged_three_claim_files=saved[1:4],unchanged_three_other_GPU_controllers=saved[4:],previous13315_amendment_preserved=PREVIOUS_AMENDMENT,declared_root_GPU_submission_journal_entries_before_and_after=JOURNAL_ENTRIES,original_source_prepost_equal=True,original_and_frozen_sources_byte_identical=True,all_control_prepost_bytes_and_metadata_equal=True,only_added_keys=list(EXTRA_KEYS),original_all_fields_preserved=True,canonical_parent_mode_restored=True,no_journal_write=True,new_GPU_submission=False,technical_GPU_rerun=False,science_accepted=False,cost_closure_accepted=False,source_or_settings_changed=False,default_changed=False,Git_changed=False,ACTIVE_changed=False,root_next_step="Root appends0006 with same entries/previous0005 and distinct metadata_only_common_controller_amendment_CPU_qualifications; original13315 list unchanged")
 need(committed_guard(P,exact(candidate),transaction)==actual,"Exact known canonical identity through final acceptance")
 own_readback(original,frozen);before_after(evidence,metas);exact(archive);exact(transaction_r)
 ar=dump(out/"acceptance.json",acceptance);print(json.dumps(dict(status=ACCEPTED,acceptance=ar,amendment=diff,current_canonical=actual,old_archive=archive),ensure_ascii=False))
def main():
 allocation=cpu()
 need(D==S/"pending/common_root_receipt_metadata_amendment_v1","Execute exact root-reviewed original pending entry")
 need({p.name for p in D.iterdir()}==set(FILES),"Exact OWN4 pending universe")
 original=[receipt(D/n)for n in FILES]
 need(not(D.stat().st_mode&0o222),"Original package directory readonly required")
 out=S/"runs"/("common_root_receipt_metadata_amendment_"+allocation["job_id"]);safe(out);out.mkdir(exist_ok=False)
 fd=S/"frozen"/("common_root_receipt_metadata_amendment_v1_"+allocation["job_id"])/"code";fd.mkdir(parents=True,exist_ok=False)
 frozen=[]
 for r in original:frozen.append(new_bytes(fd/Path(r["path"]).name,exact(r)))
 fd.chmod(0o555);fd.parent.chmod(0o555);own_readback(original,frozen)
 for r in frozen:
  if Path(r["path"]).suffix==".py":compile(exact(r),r["path"],"exec")
 b=subprocess.run(["bash","-n",str(fd/"amendment_cpu.sbatch")],text=True,capture_output=True)
 syntax=dump(out/"owned_source_syntax.json",dict(compile_owned_Python=True,bash_argv=b.args,bash_returncode=b.returncode,bash_stdout=b.stdout,bash_stderr=b.stderr,source_files=frozen))
 need(b.returncode==0,"Owned launcher syntax failed")
 dump(out/"source_snapshot.json",dict(original_executing_sources=original,frozen_source_files=frozen,syntax=syntax,allocation=allocation,scope=OWN_STATUS))
 m=load("common13423_metadata_amendment_sealed",fd/"amendment.py")
 m.perform(allocation,original,frozen,out)
if __name__=="__main__":main()
