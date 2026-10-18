#!/usr/bin/env python3
"""Strict current-job scheduler readiness before the unchanged accepted apply."""
import argparse,hashlib,importlib.util,json,os,re,shutil,subprocess,sys,time,traceback,unittest
from pathlib import Path
ROOT=Path("/lustre/users/u21111210118/projects/test9")
S=ROOT/"steps/24_benchmark_delivery"
D=Path(__file__).resolve().parent
OWN=("default_apply_bootstrap.py","test_default_apply_bootstrap.py","default_apply_bootstrap_software_cpu.sbatch","default_apply_bootstrap_cpu.sbatch","HANDOFF.md")
LIB_NAMES={"final_source_closure.py","test_final_source_closure.py","final_source_cpu.sbatch","HANDOFF.md","FINAL_SOURCE_CHECKLIST.md","final_source_context_adapter.py"}
INT_NAMES={"integrate_default_workflow_v3.py","test_integrate_default_workflow_v3.py","default_integration_cpu_v3.sbatch","HANDOFF.md"}
LIB_A=S/"runs/final_source_materialized_software_13322/acceptance.json"
INT_A=S/"runs/default_materialized_integration_software_13325/acceptance.json"
OP_REQUEST=S/"submissions/default_materialized_integration_root_request_v3/request.json"
INT_PENDING=S/"pending/default_workflow_materialized_integration_v3_fixturefix1"
INT_FROZEN=S/"frozen/default_workflow_materialized_integration_v3_13325/code"
SOFTWARE_JOB="test9_default_scheduler_readiness_v1"
APPLY_JOB="test9_default_materialized_integration_v3"
STATUS="DEFAULT_APPLY_SCHEDULER_READINESS_SOFTWARE_CPU_ACCEPTED_NO_DEFAULT_WRITE"
SCHEMA="default-apply-scheduler-readiness-software.v1"
TESTS=20
MAX_WAIT_SECONDS=120
MAX_ATTEMPTS=30
POLL_SECONDS=2
FORMAT="JobIDRaw,State,AllocTRES,User%64,Account%64,Partition%64"
TERMINAL_FORMAT="JobIDRaw,State,ExitCode,ElapsedRaw,AllocTRES,User%64,Account%64,JobName%100,Partition%64"
class ReadinessError(ValueError):pass
def need(value,message):
 if not value:raise ReadinessError(message)
def numeric(value,label):
 need(isinstance(value,str)and re.fullmatch(r"[0-9]+",value) is not None,"Noninteger "+label);return int(value)
def tres(value):
 need(isinstance(value,str),"TRES text required");out={}
 if value:
  for token in value.split(","):
   need(token.count("=")==1,"Malformed allocated TRES token")
   key,v=token.split("=",1);need(key and v and key not in out,"Duplicate or empty allocated TRES")
   out[key]=v
 for key,v in out.items():
  if key=="cpu"or key.startswith("gres/gpu"):
   need(key=="cpu"or key=="gres/gpu"or(key.startswith("gres/gpu:")and len(key)>len("gres/gpu:")),"Malformed GPU TRES namespace");numeric(v,key)
 gpu=max(numeric(out.get("gres/gpu","0"),"GPU"),sum(numeric(v,k)for k,v in out.items()if k.startswith("gres/gpu:")))
 return out,numeric(out.get("cpu","0"),"CPU"),gpu
def scontrol_view(raw,jid,jobname):
 need(isinstance(jid,str)and re.fullmatch(r"[1-9][0-9]*",jid),"Exact numeric current job")
 lines=[l for l in raw.splitlines()if l.strip()]
 need(len(lines)==1,"One exact current-job controller row")
 def field(key):
  values=re.findall(r"(?:^|\s)"+re.escape(key)+r"=(\S+)",lines[0]);need(len(values)==1,"Unique controller field "+key);return values[0]
 need(field("JobId")==jid and field("JobName")==jobname and field("JobState")=="RUNNING","Actual current CPU job/name/RUNNING required")
 need(field("UserId").split("(",1)[0]=="u21111210118"and field("Account")=="u21111210118"and field("Partition")=="organ","Actual current owner/account/organ required")
 need(numeric(field("NumCPUs"),"NumCPUs")==1,"Actual CPU1 required")
 vals=re.findall(r"(?:^|\s)(AllocTRES|TRES)=(\S+)",lines[0]);need(vals and len({k for k,_ in vals})==len(vals),"Unique actual allocated TRES fields required")
 parsed=[tres(v)for _,v in vals];need(all(c==1 and g==0 for _,c,g in parsed),"Actual CPU1/GPU0 TRES required")
 return dict(job_id=jid,jobname=jobname,state="RUNNING",allocated_CPUs=1,allocated_GPUs=0,raw_controller=raw)
def sacct_argv(jid):
 return ["sacct","-X","-j",jid,"--noheader","--parsable2","--format="+FORMAT]
def accounting_view(raw,jid):
 rows=[];excluded=[]
 for line in raw.splitlines():
  if not line.strip():continue
  r=line.split("|")
  if r[0]==jid:rows.append(r)
  elif r[0].startswith(jid+"."):excluded.append(line)
  else:raise ReadinessError("Unexpected other job in current-job accounting")
 need(len(rows)<=1,"Duplicate exact current-job accounting rows")
 if not rows:return dict(ready=False,reason="CURRENT_JOB_NOT_YET_VISIBLE",excluded=excluded)
 r=rows[0]
 if len(r)==7 and r[-1]=="":r=r[:-1]
 need(len(r)==6,"Exact original LIB six accounting columns required")
 job,state,value,user,account,partition=r
 need(all(not v or v==wanted for v,wanted in ((user,"u21111210118"),(account,"u21111210118"),(partition,"organ"))),"Wrong current accounting owner/account/partition")
 need(state in {"RUNNING","PENDING","CONFIGURING"},"Terminal or unsupported current accounting state")
 vals,cpu,gpu=tres(value);need(gpu==0,"Current accounting GPU allocation refused")
 need(cpu in(0,1),"Current accounting CPU conflicts with controller CPU1")
 ready=state=="RUNNING"and [user,account,partition]==["u21111210118","u21111210118","organ"]and cpu==1
 return dict(ready=ready,reason=None if ready else"CURRENT_ACCOUNTING_NOT_FULLY_RUNNING",row=r,allocated_CPUs=cpu,allocated_GPUs=gpu,excluded=excluded)
def environment():
 need(os.environ.get("SLURM_JOB_ID","").isdigit()and os.environ.get("CUDA_VISIBLE_DEVICES")==""and os.environ.get("JAX_PLATFORMS")=="cpu","Owned Slurm/empty CUDA/CPU platform required")
 need(os.environ.get("PYTHONNOUSERSITE")=="1"and os.environ.get("PYTHONDONTWRITEBYTECODE")=="1"and"PYTHONPATH"not in os.environ,"Readonly import isolation required")
 for k in("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS"):need(os.environ.get(k)=="1","Single CPU thread required")
 return os.environ["SLURM_JOB_ID"]
def rec(path):
 p=Path(path);h=hashlib.sha256()
 with p.open("rb")as f:
  for block in iter(lambda:f.read(1048576),b""):h.update(block)
 return dict(path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest())
def readonly(path):
 p=Path(path);need(p.is_file()and not p.is_symlink()and p.resolve()==p and not(p.stat().st_mode&0o222),"Exact readonly regular input required");return p
def verify(r):
 p=readonly(r["path"]);need(rec(p)==r,"Current byte identity changed: "+str(p));return p
def dump(path,obj):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("x")as f:json.dump(obj,f,indent=2,sort_keys=True,allow_nan=False);f.write("\n")
 p.chmod(0o444);return rec(p)
def json_input(path):return json.loads(readonly(path).read_text())
def run_query(argv,prefix,timeout=10):
 try:
  r=subprocess.run(argv,capture_output=True,text=True,timeout=timeout);so_text,se_text,rc,timed_out=r.stdout,r.stderr,r.returncode,False
 except subprocess.TimeoutExpired as error:
  def txt(v):return v.decode("utf-8",errors="replace")if isinstance(v,bytes)else(v or"")
  so_text,se_text,rc,timed_out=txt(error.stdout),txt(error.stderr),None,True
 so=Path(str(prefix)+".stdout");se=Path(str(prefix)+".stderr")
 with so.open("x")as f:f.write(so_text)
 with se.open("x")as f:f.write(se_text)
 so.chmod(0o444);se.chmod(0o444)
 return so_text,dict(argv=argv,returncode=rc,timed_out=timed_out,stdout=rec(so),stderr=rec(se),timeout_seconds=timeout)
def query_success(r):need(r.get("returncode")==0 and r.get("timed_out")is False,"Actual scheduler query failed or timed out")
def wait_ready(jid,jobname,query,clock=time.monotonic,pause=time.sleep,max_wait=MAX_WAIT_SECONDS,max_attempts=MAX_ATTEMPTS):
 start=clock();rows=[]
 def remaining():
  value=max_wait-(clock()-start);need(value>0,"Current-job accounting readiness timeout");return value
 try:
  for attempt in range(max_attempts):
   row=dict(attempt=attempt);rows.append(row)
   sc,sc_record=query(["scontrol","show","job",jid,"-o"],"controller",attempt,min(10,remaining()));row["controller_query"]=sc_record;query_success(sc_record)
   controller=scontrol_view(sc,jid,jobname);row["controller"]=controller
   ac,ac_record=query(sacct_argv(jid),"accounting",attempt,min(10,remaining()));row["accounting_query"]=ac_record;query_success(ac_record)
   view=accounting_view(ac,jid);row["accounting"]=view;remaining()
   if view["ready"]:return dict(schema="strict-current-job-scheduler-readiness.v1",status="ACTUAL_CONTROLLER_AND_ORIGINAL_LIB_ACCOUNTING_RUNNING_CPU1_GPU0",job_id=jid,jobname=jobname,attempts=rows,actual_controller=controller,original_LIB_numeric_sacct_row=view["row"],PENDING_accepted=False,owner_or_TRES_waived=False,maximum_wait_seconds=max_wait,maximum_attempts=max_attempts)
   if attempt+1<max_attempts:pause(min(POLL_SECONDS,remaining()))
  raise ReadinessError("Current-job accounting readiness attempt limit")
 except Exception as error:
  error.readiness_attempts=rows;raise
def live_readiness(jid,jobname,out):
 queries=out/"scheduler_queries";queries.mkdir(exist_ok=False)
 def query(argv,label,attempt,timeout):return run_query(argv,queries/("%03d_"%attempt+label),timeout=timeout)
 try:return wait_ready(jid,jobname,query)
 except Exception as error:
  dump(out/"failed_current_job_readiness.json",dict(schema="strict-current-job-scheduler-readiness-incomplete.v1",status="CURRENT_JOB_READINESS_INCOMPLETE_NO_APPLY_DISPATCH",job_id=jid,error_type=type(error).__name__,error=str(error),attempts=getattr(error,"readiness_attempts",[]),PENDING_accepted=False,owner_or_TRES_waived=False,default_apply_dispatched=False))
  raise
 finally:queries.chmod(0o555)
def terminal_view(raw,jid,jobname,state="COMPLETED",exit_code="0:0"):
 rows=[line.split("|")for line in raw.splitlines()if line.strip()]
 need(len(rows)==1,"Unique exact terminal CPU row")
 r=rows[0]
 if len(r)==10 and r[-1]=="":r=r[:-1]
 need(len(r)==9 and r[0]==jid and r[1]==state and r[2]==exit_code and r[5:9]==["u21111210118","u21111210118",jobname,"organ"],"Actual exact terminal CPU identity/state/exit/owner/job/organ")
 elapsed=numeric(r[3],"elapsed");_,cpus,gpus=tres(r[4]);need(cpus==1 and gpus==0,"Actual terminal CPU1/GPU0")
 return dict(job_id=jid,state=state,exit_code=exit_code,elapsed_seconds=elapsed,allocated_CPUs=cpus,allocated_GPUs=gpus,numeric_sacct_row=r)
def terminal_cpu(jid,jobname,out,label,state="COMPLETED",exit_code="0:0"):
 argv=["sacct","-X","-j",jid,"--noheader","--parsable2","--format="+TERMINAL_FORMAT]
 raw,record=run_query(argv,out/label);query_success(record)
 result=terminal_view(raw,jid,jobname,state,exit_code);result["query"]=record;return result
def failed13408(out):
 a=S/"logs/default_materialized_integration_v3_13408.err";b=S/"logs/default_materialized_integration_v3_13408.out"
 er,sr=rec(readonly(a)),rec(readonly(b));text=a.read_text()
 need(er["bytes"]==1669 and sr["bytes"]==0 and "integrate_default_workflow_v3.py\", line 464"in text and "library/final_source_closure.py\", line 78"in text and "Unique actual CPU owner/account/partition required"in text,"Actual recorded original failure required")
 need(not(S/"runs/default_materialized_integration_13408").exists(),"Original13408 unexpectedly has output/transaction directory")
 seal=rec(readonly(S/"submissions/default13408_actual_failure_metadata_terminal_seal/receipt.json"))
 j=json_input(seal["path"]);need(j.get("actual_job")=="13408"and j.get("failed_guard_sacct_response_not_saved_do_not_guess_cause")is True,"Original instantaneous sacct cause remains unproven")
 return dict(schema="default13408-failed-before-transaction-history.v1",status="ACTUAL_FAILED13408_BEFORE_TRANSACTION_PRESERVED_CAUSE_UNPROVEN",job_id="13408",terminal=terminal_cpu("13408",APPLY_JOB,out,"failed13408_sacct","FAILED","1:0"),stderr=er,stdout=sr,metadata_readonly_seal=seal,original_output_directory_absent=True,original_sacct_response_saved=False,accounting_lag_proven=False,original_LIB53_and_integration84_unchanged=True)
def source_rows():
 need({p.name for p in D.iterdir()}==set(OWN)and not(D.stat().st_mode&0o222),"Exact readonly five-source universe required")
 return [rec(readonly(D/n))for n in OWN]
def row_identity(r):return r["bytes"],r["sha256"]
def original_readback(original,frozen):
 need(len(original)==len(frozen)==5 and {Path(r["path"]).name for r in original}==set(OWN),"Whole original/frozen5 required")
 by={Path(r["path"]).name:r for r in frozen}
 for r in original:need(row_identity(rec(verify(r)))==row_identity(by[Path(r["path"]).name]),"Original executing source differs from tested frozen source")
def fixed_inputs():
 la=rec(readonly(LIB_A));need(la["bytes"]==2692 and la["sha256"]=="95a8afdc09e7bb4afe5d3e89747e9806e10091e69e586abe576b918f8f1e0ce7","Actual LIB13322 acceptance identity")
 lib=json_input(LIB_A);lc=json_input(verify(lib["contracts"]))
 need(lib.get("schema")=="final-source-materialized-software-acceptance.v3"and lib.get("status")=="FINAL_SOURCE_MATERIALIZED_ARCHIVE_CONTEXT_AND_DERIVED_V2_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_INTEGRATION","Accepted unchanged library53 required")
 lr=lib["source_files"];need(len(lr)==6 and{Path(r["path"]).name for r in lr}==LIB_NAMES,"Exact accepted library6")
 need(lc.get("status")=="PASS"and lc.get("tests")==53 and lc.get("errors")==lc.get("failures")==0 and lc.get("tested_source_files")==lr and lc.get("owned_python_compile_PASS")is True and lc.get("bash_syntax_PASS")is True,"Saved actual library53 source/contracts")
 for r in lr:verify(r)
 verify(lc["log"])
 ia=rec(readonly(INT_A));need(ia["bytes"]==13300,"Existing integration acceptance bytes")
 integ=json_input(INT_A);ic=json_input(verify(integ["contracts"]))
 need(integ.get("schema")=="default-materialized-integration-software-acceptance.v2"and integ.get("status")=="DEFAULT_MATERIALIZED_INTEGRATION_SOFTWARE_CPU_ACCEPTED_NO_DEFAULT_WRITE"and integ.get("tests_expected")==84 and integ.get("compiled_all_python")is True and integ.get("bash_syntax_checked")is True,"Unchanged actual integration84 required")
 ir=integ["source_files"];originals=integ["original_source_files"]
 need(len(ir)==10 and len(originals)==4 and{Path(r["path"]).name for r in originals}==INT_NAMES,"Accepted integration4/library6 source universe")
 need(ic.get("status")=="PASS"and ic.get("tests")==84 and ic.get("errors")==ic.get("failures")==0 and ic.get("source_files")==ir,"Saved actual integration84 contracts/source")
 need(integ["library_software_binding"]["receipt"]==la and integ["library_software_binding"]["source_files"]==lr,"Actual same library prerequisite")
 own=[r for r in ir if Path(r["path"]).parent==INT_FROZEN];copies=[r for r in ir if Path(r["path"]).parent==INT_FROZEN/"library"]
 need(len(own)==4 and{Path(r["path"]).name for r in own}==INT_NAMES and len(copies)==6 and{Path(r["path"]).name for r in copies}==LIB_NAMES,"Only accepted frozen integration source locations")
 need(all(Path(r["path"]).parent==INT_PENDING for r in originals),"Original accepted dispatcher locations")
 by={Path(r["path"]).name:r for r in own}
 for r in originals:need(row_identity(r)==row_identity(by[Path(r["path"]).name]),"Original/frozen integration source mismatch")
 lib_by={Path(r["path"]).name:r for r in lr}
 for r in copies:need(row_identity(r)==row_identity(lib_by[Path(r["path"]).name]),"Executing/tested unchanged library bytes")
 for r in ir+originals:verify(r)
 verify(ic["log"])
 q=json_input(OP_REQUEST);op=rec(OP_REQUEST)
 need(op["bytes"]==8226 and q.get("schema")=="default-generic-materialized-integration-request.v2"and q.get("root_approved")is True and q.get("formal_array_job_id")=="13260"and q.get("formal_sources_changed")is False,"Exact approved unchanged root request")
 need(len(q["operations"])==3 and{v["repository_relative"]for v in q["operations"]}=={"src/ppiblocker/pipeline.py","src/ppiblocker/pose_physical_gate.py","environment/runtime-lock-rfd.json"},"Same exact three destinations")
 launcher=next(r for r in originals if Path(r["path"]).name=="default_integration_cpu_v3.sbatch")
 entry=next(r for r in lr if Path(r["path"]).name=="final_source_closure.py")
 return dict(library_acceptance=la,integration_software_acceptance=ia,operation_request=op,unchanged_accepted_apply_launcher=launcher,original_library_cpu_source=entry,all_input_sources=ir+originals+lr,library_contracts=lib["contracts"],integration_contracts=integ["contracts"],library_contract_log=lc["log"],integration_contract_log=ic["log"],unchanged_software_counts=[53,84],unchanged_three_destinations=True)
def probe_contract(record,jid):
 need(isinstance(record,dict)and record.get("job_id")==jid and record.get("allocated_CPUs")==1 and record.get("allocated_gpus")==0,"Actual unchanged LIB.cpu result required")
 view=accounting_view(record.get("scheduler_record",""),jid)
 need(view["ready"]and record.get("numeric_sacct_row")==view["row"],"Actual original LIB.cpu six-column result independently checked")
 return record
def original_lib_probe(inputs):
 p=verify(inputs["original_library_cpu_source"]);spec=importlib.util.spec_from_file_location("unchanged_actual_LIB53_cpu_probe",p);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 record=probe_contract(m.cpu(),os.environ["SLURM_JOB_ID"])
 return dict(source=inputs["original_library_cpu_source"],actual_original_LIB_cpu_result=record,LIB_source_changed=False,LIB_CPU_implementation_replaced=False)
def readiness_contract(r,jid,jobname):
 need(r.get("schema")=="strict-current-job-scheduler-readiness.v1"and r.get("status")=="ACTUAL_CONTROLLER_AND_ORIGINAL_LIB_ACCOUNTING_RUNNING_CPU1_GPU0"and r.get("job_id")==jid and r.get("jobname")==jobname and r.get("PENDING_accepted")is False and r.get("owner_or_TRES_waived")is False,"Actual saved wrapper readiness content")
 controller=r["actual_controller"];need(scontrol_view(controller["raw_controller"],jid,jobname)==controller,"Saved exact controller content")
 view=accounting_view("|".join(r["original_LIB_numeric_sacct_row"])+"\n",jid);need(view["ready"],"Saved exact RUNNING accounting content")
 need(r.get("attempts")and r["attempts"][-1]["accounting"]["row"]==view["row"],"Saved actual observed ready row")
 for row in r["attempts"]:
  for key in("controller_query","accounting_query"):
   query_success(row[key]);verify(row[key]["stdout"]);verify(row[key]["stderr"])
def software_contract(a,c,rows):
 need(a.get("schema")==SCHEMA and a.get("status")==STATUS and a.get("source_files")==rows and len(rows)==5 and{Path(r["path"]).name for r in rows}==set(OWN),"Actual same-source wrapper qualification required")
 need(c.get("tested_source")==rows and c.get("tests")==TESTS and c.get("status")=="PASS"and c.get("errors")==c.get("failures")==c.get("skipped")==0 and c.get("compiled_all_owned_python")is True and c.get("bash_syntax_PASS")is True,"Actual wrapper20 contracts/syntax/source required")
 need(a.get("original_and_frozen_pre_post_readback_PASS")is True and a.get("software53_and84_retested")is False and a.get("default_written")is False and a.get("science_accepted")is False and a.get("GPU_requested")is False and a.get("ACTIVE_changed")is False,"Wrapper qualification cannot imply source install/science")
 original_readback(a["original_executing_sources"],rows)
def failure(out,mode,error):
 if out.exists()and not(out/"typed_incomplete.json").exists():
  dump(out/"typed_incomplete.json",dict(schema="default-scheduler-bootstrap-incomplete.v1",status="SCHEDULER_BOOTSTRAP_INCOMPLETE_NO_DEFAULT_DISPATCH",mode=mode,actual_job_id=os.environ.get("SLURM_JOB_ID"),error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc(),default_apply_dispatched=False,default_written=False,science_accepted=False,owner_or_TRES_waived=False))
  out.chmod(0o555)
def readback_inputs(inputs):
 for key in("library_acceptance","integration_software_acceptance","operation_request","unchanged_accepted_apply_launcher","original_library_cpu_source","library_contracts","integration_contracts","library_contract_log","integration_contract_log"):verify(inputs[key])
 for r in inputs["all_input_sources"]:verify(r)
def software_frozen(out,original):
 jid=environment();rows=source_rows();out=Path(out);out.mkdir(parents=True,exist_ok=False)
 try:
  readiness=live_readiness(jid,SOFTWARE_JOB,out);inputs=fixed_inputs();probe=original_lib_probe(inputs);old=failed13408(out)
  prerequisites=[terminal_cpu("13322","test9_final_source_materialized_v3",out,"accepted_LIB13322_sacct"),terminal_cpu("13325",APPLY_JOB,out,"accepted_Integration13325_sacct")]
  original_readback(original,rows)
  for r in rows:
   if Path(r["path"]).suffix==".py":compile(verify(r).read_bytes(),r["path"],"exec",dont_inherit=True)
   if Path(r["path"]).suffix==".sbatch":subprocess.run(["bash","-n",r["path"]],check=True)
  spec=importlib.util.spec_from_file_location("frozen_scheduler_tests",D/"test_default_apply_bootstrap.py");tests=importlib.util.module_from_spec(spec);spec.loader.exec_module(tests);tests.m=sys.modules[__name__]
  suite=unittest.defaultTestLoader.loadTestsFromModule(tests);need(suite.countTestCases()==TESTS,"Actual20 named wrapper tests")
  with(out/"contracts.txt").open("x")as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
  (out/"contracts.txt").chmod(0o444)
  contracts=dump(out/"contracts.json",dict(status="PASS"if result.wasSuccessful()else"FAIL",tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),log=rec(out/"contracts.txt"),tested_source=rows,compiled_all_owned_python=True,bash_syntax_PASS=True))
  need(result.wasSuccessful()and result.testsRun==TESTS and not result.skipped,"Actual20 wrapper contracts failed")
  need(source_rows()==rows,"Whole frozen wrapper sources changed");original_readback(original,rows);readback_inputs(inputs)
  ready=dump(out/"actual_current_job_readiness.json",readiness);probed=dump(out/"actual_unchanged_LIB_cpu_probe.json",probe);history=dump(out/"failed13408_history.json",old)
  for r in(old["stderr"],old["stdout"],old["metadata_readonly_seal"]):verify(r)
  acceptance=dump(out/"acceptance.json",dict(schema=SCHEMA,status=STATUS,actual_CPU_job_id=jid,source_files=rows,original_executing_sources=original,original_and_frozen_pre_post_readback_PASS=True,contracts=contracts,actual_current_job_readiness=ready,actual_unchanged_LIB_cpu_probe=probed,fixed_accepted_inputs=inputs,actual_existing_source_terminal_prerequisites=prerequisites,failed13408_history=history,software53_and84_retested=False,default_written=False,science_accepted=False,GPU_requested=False,ACTIVE_changed=False,original13408_failed_raw_sacct_not_recorded_cause_unproven=True))
  out.chmod(0o555);print(json.dumps(acceptance),flush=True)
 except Exception as error:failure(out,"software",error);raise
def qualify():
 jid=environment();raw=subprocess.check_output(["scontrol","show","job",jid,"-o"],text=True);scontrol_view(raw,jid,SOFTWARE_JOB)
 original=source_rows();snap=S/"frozen"/("default_apply_scheduler_bootstrap_v1_"+jid)/"code";snap.mkdir(parents=True,exist_ok=False)
 for n in OWN:shutil.copyfile(verify(next(r for r in original if Path(r["path"]).name==n)),snap/n);(snap/n).chmod(0o444)
 snap.chmod(0o555);spec=importlib.util.spec_from_file_location("frozen_scheduler_bootstrap",snap/OWN[0]);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 m.software_frozen(S/"runs"/("default_scheduler_software_"+jid),original)
def bootstrap(acceptance_path,expected_sha):
 jid=environment();raw=subprocess.check_output(["scontrol","show","job",jid,"-o"],text=True);scontrol_view(raw,jid,APPLY_JOB)
 rows=source_rows();ar=rec(readonly(acceptance_path));need(ar["sha256"]==expected_sha,"Exact root wrapper acceptance SHA")
 a=json_input(ar["path"]);c=json_input(verify(a["contracts"]));software_contract(a,c,rows)
 verify(c["log"])
 out=S/"runs"/("default_scheduler_dispatch_"+jid);out.mkdir(exist_ok=False)
 try:
  qualified_jid=a["actual_CPU_job_id"];need(str(qualified_jid).isdigit()and qualified_jid!=jid,"Distinct completed actual wrapper qualification")
  terminal=terminal_cpu(qualified_jid,SOFTWARE_JOB,out,"actual_wrapper_software_terminal")
  ready=json_input(verify(a["actual_current_job_readiness"]));readiness_contract(ready,qualified_jid,SOFTWARE_JOB)
  oldprobe=json_input(verify(a["actual_unchanged_LIB_cpu_probe"]));probe_contract(oldprobe["actual_original_LIB_cpu_result"],qualified_jid)
  need(oldprobe["source"]==a["fixed_accepted_inputs"]["original_library_cpu_source"]and oldprobe["LIB_source_changed"]is False and oldprobe["LIB_CPU_implementation_replaced"]is False,"Actual original LIB probe source binding")
  oldhistory=json_input(verify(a["failed13408_history"]));need(oldhistory.get("status")=="ACTUAL_FAILED13408_BEFORE_TRANSACTION_PRESERVED_CAUSE_UNPROVEN"and oldhistory.get("accounting_lag_proven")is False,"Original13408 failure retained honestly")
  for r in(oldhistory["stderr"],oldhistory["stdout"],oldhistory["metadata_readonly_seal"]):verify(r)
  readiness=live_readiness(jid,APPLY_JOB,out);inputs=fixed_inputs();need(inputs==a["fixed_accepted_inputs"],"Accepted existing apply inputs changed");probe=original_lib_probe(inputs)
  readback_inputs(inputs);need(source_rows()==rows,"Wrapper source changed before dispatch");original_readback(a["original_executing_sources"],rows);verify(ar)
  argv=["bash",inputs["unchanged_accepted_apply_launcher"]["path"],"apply",str(LIB_A),str(OP_REQUEST),str(INT_A)]
  dump(out/"scheduler_ready_before_unchanged_apply.json",dict(schema="scheduler-ready-default-apply-dispatch.v1",status="ACTUAL_SCHEDULER_READY_UNCHANGED_ACCEPTED_APPLY_EXECUTION_NEXT",actual_CPU_job_id=jid,wrapper_software=ar,actual_wrapper_software_terminal=terminal,source_files=rows,readiness=readiness,actual_unchanged_LIB_cpu_probe=probe,failed13408_history=a["failed13408_history"],fixed_accepted_inputs=inputs,argv=argv,default_apply_acceptance=False,source_gate_or_owner_TRES_waived=False,software53_and84_retested=False))
  out.chmod(0o555)
 except Exception as error:failure(out,"bootstrap_before_apply",error);raise
 os.execv("/bin/bash",argv)
def dispatch(acceptance_path,expected_sha):
 jid=environment();raw=subprocess.check_output(["scontrol","show","job",jid,"-o"],text=True);scontrol_view(raw,jid,APPLY_JOB)
 original=source_rows();ar=rec(readonly(acceptance_path));need(ar["sha256"]==expected_sha,"Exact root wrapper acceptance SHA")
 a=json_input(ar["path"]);rows=a["source_files"];need(a.get("schema")==SCHEMA and a.get("status")==STATUS and a["original_executing_sources"]==original,"Same accepted original dispatcher source")
 original_readback(original,rows)
 expected=S/"frozen"/("default_apply_scheduler_bootstrap_v1_"+a["actual_CPU_job_id"])/"code"
 need({Path(r["path"]).parent for r in rows}=={expected}and{Path(r["path"]).name for r in rows}==set(OWN),"Exact accepted wrapper frozen namespace")
 for r in rows:verify(r)
 entry=expected/OWN[0];spec=importlib.util.spec_from_file_location("accepted_frozen_scheduler_bootstrap",entry);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 m.bootstrap(acceptance_path,expected_sha)
def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest="mode",required=True);sub.add_parser("qualify");b=sub.add_parser("bootstrap");b.add_argument("--software",required=True);b.add_argument("--software-sha256",required=True);a=p.parse_args()
 if a.mode=="qualify":qualify()
 else:dispatch(a.software,a.software_sha256)
if __name__=="__main__":main()
