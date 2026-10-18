from pathlib import Path
import hashlib,json,os,subprocess,re
R=Path("/lustre/users/u21111210118/projects/test9")
HERE=Path(__file__).resolve().parent
def need(v,m):
 if not v:raise ValueError(m)
def safe(p):
 p=Path(p);need(p.is_absolute()and p.resolve()==p and p.is_relative_to(R)and p.is_file()and not p.is_symlink()and not(p.stat().st_mode&0o222),"Exact readonly regular file required: "+str(p));return p
def rec(p):
 p=safe(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def tres(s):
 d={}
 for item in s.split(","):
  key,sep,val=item.partition("=");need(sep and key not in d,"Malformed/duplicate TRES");d[key]=val
 need(d.get("cpu","").isdigit()and int(d["cpu"])==1,"Actual CPU1 required")
 for k,v in d.items():
  if k=="gpu"or k.startswith("gres/gpu")or k.startswith("gres:gpu"):
   need(v.isdigit()and int(v)==0,"GPU TRES must be integer zero")
 return d
def terminal(j,name,state="COMPLETED",exitcode="0:0"):
 p=subprocess.run(["sacct","-X","-j",j,"--format=JobIDRaw,User,Account,JobName%100,Partition,State,ExitCode,Elapsed,AllocCPUS,ReqTRES%1500,AllocTRES%1500","-n","-P"],text=True,capture_output=True,check=True)
 rows=[x.split("|")for x in p.stdout.splitlines()if x.split("|")[0]==j];need(len(rows)==1,"Exactly one numeric terminal record required")
 row=rows[0];need(len(row)>=11 and row[:7]==[j,"u21111210118","u21111210118",name,"organ",state,exitcode]and row[8]=="1","Actual numeric terminal identity differs")
 req,alloc=tres(row[9]),tres(row[10]);return dict(job_id=j,raw_sacct=p.stdout,requested_TRES=req,allocated_TRES=alloc,allocated_GPU=0)
j=os.environ.get("SLURM_JOB_ID","");need(j.isdigit()and j!="0"and not os.environ.get("CUDA_VISIBLE_DEVICES")and os.environ.get("JAX_PLATFORMS")=="cpu"and os.environ.get("PYTHONDONTWRITEBYTECODE")=="1"and "PYTHONPATH"not in os.environ,"Actual pureCPU isolated Slurm required")
show=subprocess.run(["scontrol","show","job",j,"-o"],text=True,capture_output=True,check=True).stdout
need("JobState=RUNNING "in show and "JobName=test9_source_e2e_descriptors "in show and "UserId=u21111210118("in show and "Account=u21111210118 "in show and "Partition=organ "in show and "NumCPUs=1 "in show,"Current CPU allocation identity differs")
tres_parts=re.findall(r"(?:^| )(?:TRES|AllocTRES)=([^ ]+)",show);need(bool(tres_parts),"Actual current TRES required")
for val in tres_parts:tres(val)
source0={n:rec(HERE/n)for n in ("capture.py","capture.sbatch")};need(not HERE.stat().st_mode&0o222,"Source dir readonly")
producers=[terminal("13316","test9_source_relative_v10"),terminal("13312","test9_reference_free_e2e_audit")]
spec=[
(R/"steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/acceptance.json","source-delivery-refresh.v3","CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY"),
(R/"steps/24_benchmark_delivery/runs/source_relative_contracts_13316/acceptance.json","source-refresh-relative-software-acceptance.v10","SOURCE_REFRESH_RELATIVE_SOFTWARE_CPU_ACCEPTED_ACTUAL_SOURCE_AUDIT_PENDING"),
(R/"steps/25_reference_free_e2e/runs/e2e_final_audit_after13311_root_20261012/acceptance.json","reference_free_e2e_independent_actual_closure.v1","REFERENCE_FREE_E2E_COMPUTATIONAL_CHAIN_CONTENT_ACCEPTED")]
checked=[]
for path,schema,status in spec:
 receipt=rec(path);obj=json.loads(path.read_bytes())
 need(obj.get("status")==status and(schema is None or obj.get("schema")==schema),"Pinned actual acceptance schema/status differs")
 if schema=="reference_free_e2e_independent_actual_closure.v1":need(obj.get("slurm_CPU_job_id")=="13312"and obj.get("GPU_allocated")==0,"Actual E2E CPU13312 binding differs")
 if schema=="source-delivery-refresh.v3":need(obj.get("source_issues")==0 and obj.get("exact_recovered_source_identity_n")==8 and obj.get("exact_original_source_edge_n")==12,"Actual full finite source acceptance differs")
 if schema=="source-refresh-relative-software-acceptance.v10":need(obj.get("tests_expected")==122,"Actual SourceV10 software count differs")
 need(rec(path)==receipt,"Producer changed during descriptor capture")
 checked.append(dict(receipt=receipt,schema=obj.get("schema"),status=status))
need({n:rec(HERE/n)for n in source0}==source0,"Capture source drift")
for row in checked:need(rec(row["receipt"]["path"])==row["receipt"],"Producer postread drift")
out=R/"steps/24_benchmark_delivery/runs"/("source_e2e_descriptor_capture_"+j);out.mkdir(exist_ok=False)
result=dict(schema="root-actual-source-and-e2e-descriptor-capture.v1",status="EXACT_EXISTING_ACCEPTANCE_DESCRIPTORS_CPU_CAPTURED_NOT_NEW_SCIENTIFIC_ACCEPTANCE",job_id=j,allocation=show,source_receipts=list(source0.values()),actual_producer_terminal=producers,acceptances=checked,source_current_executed_or_installed=False,scientific_settings_changed=False,allocated_GPU=0)
p=out/"descriptor_capture.json";p.write_text(json.dumps(result,indent=2)+"\n");p.chmod(0o444);out.chmod(0o555)
print(json.dumps(result))
