import os,json,hashlib,pathlib,subprocess,datetime
R=pathlib.Path("/lustre/users/u21111210118/projects/test9")
BASE=R/"steps/25_reference_free_e2e"
P=BASE/"submissions/e2e_evaluate_after13309_primary_claim/submit_receipt.json"
J=R/"steps/24_benchmark_delivery/submissions/root_gpu_journal/0003_e2e_evaluate_13311.json"
def need(v,m):
 if not v:raise RuntimeError(m)
def rec(p):
 p=pathlib.Path(p);need(p.is_file() and not p.is_symlink() and p.resolve()==p and p.is_relative_to(R) and p.stat().st_mode&0o222==0,"Unsafe or writable metadata file")
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def allocation_values(text):
 need(isinstance(text,str) and bool(text),"Missing actual allocated TRES")
 vals={}
 for part in text.split(","):
  need(part.count("=")==1,"Malformed allocated TRES");key,value=part.split("=")
  need(key and value and key not in vals,"Missing or duplicate allocated TRES");vals[key]=value
 need(vals.get("cpu")=="1","Positive numeric cpu=1 allocation required")
 for key,value in vals.items():
  if key=="gres/gpu" or key.startswith("gres/gpu:"):
   need(value.isdecimal() and int(value)==0,"Noninteger, negative or allocated GPU forbidden")
 return vals
def verify(r):
 need(rec(r["path"])==r,"Actual metadata byte identity differs");return pathlib.Path(r["path"])
def dump(p,d):
 need(not p.exists(),"Refuse reused metadata output");p.write_text(json.dumps(d,indent=2)+"\n");p.chmod(0o444);return rec(p)
jid=os.environ.get("SLURM_JOB_ID");need(jid and os.environ.get("CUDA_VISIBLE_DEVICES")=="","PureCPU Slurm required")
s=subprocess.run(["scontrol","show","job",jid,"-o"],capture_output=True,text=True,check=True).stdout
vals=dict(x.split("=",1) for x in s.split() if "=" in x)
tres=allocation_values(vals.get("TRES",vals.get("AllocTRES","")))
if "TRES" in vals and "AllocTRES" in vals:need(allocation_values(vals["TRES"])==allocation_values(vals["AllocTRES"]),"Actual live TRES/AllocTRES conflict")
need(vals.get("JobId")==jid and vals.get("JobState")=="RUNNING" and vals.get("Partition")=="organ" and vals.get("Account")=="u21111210118" and vals.get("UserId","").startswith("u21111210118(") and vals.get("NumCPUs")=="1","Actual owned CPU allocation differs")
need(not os.environ.get("SLURM_JOB_GPUS"),"No GPU permitted")
out=BASE/"runs"/("controller_metadata_amendment_"+jid);out.mkdir(exist_ok=False)
original_record=rec(P);jr=rec(J)
owned_sources=[rec(pathlib.Path(__file__).resolve()),rec(pathlib.Path(__file__).resolve().with_name("amendment.sbatch"))]
old_bytes=P.read_bytes();old=json.loads(old_bytes);journal_bytes=J.read_bytes();journal=json.loads(journal_bytes)
need(old["job_id"]=="13311" and old["stage"]=="evaluate" and old["schema"]=="reference_free_root_model_submission.v1" and "design_audit_acceptance" not in old,"Wrong or already amended controller")
need(old["raw_sbatch_stdout"].strip()=="13311" and not old["raw_sbatch_stderr"].strip(),"Original actual submission raw ID differs")
need(journal.get("schema")=="root-current-gpu-submission-journal.v1" and journal.get("authority_root")==str(R),"Actual root journal identity differs")
entries=[e for e in journal["entries"] if e.get("submission_id")=="e2e_evaluate_13311"]
need(len(entries)==1 and entries[0]==dict(submission_id="e2e_evaluate_13311",phase="reference_free_e2e",kind="primary",receipt_path=str(P)),"Literal actual journal receipt entry differs")
ap=pathlib.Path(old["design_audit_acceptance_path"]);ar=rec(ap);a=json.loads(ap.read_text())
need(a.get("status")=="REFERENCE_FREE_E2E_ACTUAL_DESIGN_CPU_CONTENT_ACCEPTED" and a.get("slurm_CPU_job_id")=="13309" and a.get("proposal_count")==1,"Actual design CPU content gate required")
need(a["actual_design_stage_result"]==old["design_stage_result"] and a["actual_design_manifest"]==old["upstream"] and a["source_manifest"]==old["source_manifest"] and a["preflight_acceptance"]==old["preflight_acceptance"],"Actual design/input chain differs")
for key in ["actual_design_stage_result","actual_design_manifest","source_manifest","preflight_acceptance"]:verify(a[key])
p=subprocess.run(["sacct","-X","-n","-P","-j","13309","--format=JobIDRaw,User%64,Account%64,Partition%64,JobName%100,State%40,ExitCode,AllocCPUS,AllocTRES%300"],capture_output=True,text=True,check=True)
rows=[x.split("|") for x in p.stdout.splitlines() if x.split("|")[0]=="13309"]
need(len(rows)==1,"Missing actual design CPU terminal row");row=rows[0]
need(row[1:8]==["u21111210118","u21111210118","organ","test9_reference_free_design_audit","COMPLETED","0:0","1"],"Actual design CPU terminal resources differ")
allocation_values(row[8])
need(old["submit_argv"][-1]==str(ap) and old["submit_argv"][-2]==a["actual_design_stage_result"]["path"],"Exact original evaluate argv/input differs")
archive=out/"original_submit_receipt_before_metadata_amendment.json";archive.write_bytes(old_bytes);archive.chmod(0o444);arch=rec(archive)
new=dict(old,design_audit_acceptance=ar)
need(set(new)-set(old)=={"design_audit_acceptance"} and {k:v for k,v in new.items() if k!="design_audit_acceptance"}==old,"Metadata diff not exactly one addition")
for key in ["actual_design_stage_result","actual_design_manifest","source_manifest","preflight_acceptance"]:verify(a[key])
need(rec(P)==original_record and P.read_bytes()==old_bytes and rec(J)==jr and J.read_bytes()==journal_bytes and rec(ap)==ar and all(rec(x["path"])==x for x in owned_sources),"Metadata/source drift before replacement")
parent=P.parent;old_mode=parent.stat().st_mode&511;need(old_mode==0o555,"Root primary claim not readonly")
temp=parent/(".metadata_amendment_"+jid+".json");need(not temp.exists() and not temp.is_symlink(),"Refuse reused exclusive amendment temp")
parent.chmod(0o755)
try:
 temp.write_text(json.dumps(new,indent=2)+"\n");temp.chmod(0o444);os.replace(temp,P)
finally:parent.chmod(old_mode)
for key in ["actual_design_stage_result","actual_design_manifest","source_manifest","preflight_acceptance"]:verify(a[key])
need(json.loads(P.read_text())==new and rec(J)==jr and J.read_bytes()==journal_bytes and archive.read_bytes()==old_bytes and rec(archive)==arch and rec(ap)==ar and all(rec(x["path"])==x for x in owned_sources),"Archive/current/journal/source readback differs")
amend=dump(out/"amendment.json",dict(schema="root-controller-traceable-metadata-only-amendment.v1",original_controller_logical_path=str(P),original_controller_exact_byte_archive=arch,amended_controller=rec(P),addition_only={"design_audit_acceptance":ar},original_other_fields_unchanged=True,journal=jr,journal_bytes_unchanged=True,actual_original_GPU_job_id="13311",new_GPU_job_submitted=False,scientific_settings_changed=False,actual_design_CPU_terminal_raw=p.stdout))
accepted=dump(out/"acceptance.json",dict(schema="root-controller-metadata-amendment-CPU-qualification.v1",status="ROOT_ACTUAL_EVALUATE_CONTROLLER_SINGLE_DESCRIPTOR_ADDITION_CPU_ACCEPTED",amendment=amend,archived_original_controller=arch,amended_controller=rec(P),actual_design_CPU_acceptance=ar,journal=jr,source=owned_sources,allocation=dict(slurm_job_id=jid,allocated_GPU_count=0,allocated_CPU_count=1,actual_running_scheduler_record=s),all_original_submission_fields_and_journal_entries_unchanged=True,actual_job_id="13311",completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
out.chmod(0o555);print(json.dumps({"acceptance":accepted,"status":"ROOT_ACTUAL_EVALUATE_CONTROLLER_SINGLE_DESCRIPTOR_ADDITION_CPU_ACCEPTED"}))
