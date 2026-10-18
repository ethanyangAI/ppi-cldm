#!/usr/bin/env python3
"""Capture only the actual accepted default13420 descriptor; no source/science replay."""
from pathlib import Path
import hashlib, json, os, re, subprocess
R=Path("/lustre/users/u21111210118/projects/test9")
S=R/"steps/24_benchmark_delivery"
OWN=Path(__file__).parent
A=S/"runs/default_materialized_integration_13420/acceptance.json"
FROZEN=S/"frozen/default_workflow_materialized_integration_v3_13325/code"
OWN_NAMES={"integrate_default_workflow_v3.py","test_integrate_default_workflow_v3.py","default_integration_cpu_v3.sbatch","HANDOFF.md"}
LIB_NAMES={"final_source_closure.py","test_final_source_closure.py","final_source_cpu.sbatch","HANDOFF.md","FINAL_SOURCE_CHECKLIST.md","final_source_context_adapter.py"}
PATHS=("src/ppiblocker/pipeline.py","src/ppiblocker/pose_physical_gate.py","environment/runtime-lock-rfd.json")
BASE="c3d528bb6801a7a571cdd20bfd90652e397a8540a136e1f0510ef0ccc5488dde"
M=R/"steps/default_runtime_integration_recheck/runs/20261012T091410Z_2b7999c2b5d4/manifest.json"
POINTER={"path":str(S/"runs/default_materialized_integration_13420/installed_default_runtime3.stdout"),"bytes":197,"sha256":"85a5a6e841300a21b01ea7618284de0e341a3737ffe998c61cff4c6863b77a2b"}
def need(ok,message):
 if not ok:raise ValueError(message)
def safe(p):
 p=Path(p);need(p.is_absolute() and str(p)==os.path.normpath(str(p)) and R in p.parents,"Exact internal absolute path required")
 for q in [p]+list(p.parents):
  if q==R.parent:break
  need(not q.is_symlink(),"Symlink target/source path rejected: "+str(q))
 return p
def rec(p):
 p=safe(p);need(p.is_file() and p.stat().st_mode&0o222==0,"Readonly regular metadata/source required: "+str(p))
 b=p.read_bytes();return {"path":str(p),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def verify(r):
 need(type(r) is dict and set(r)=={"path","bytes","sha256"} and type(r["bytes"]) is int and r["bytes"]>=0 and re.fullmatch("[0-9a-f]{64}",r["sha256"]),"Exact descriptor shape required")
 need(rec(r["path"])==r,"Readonly metadata/source byte identity drift: "+r["path"])
def json_read(p):
 def pairs(items):
  result={}
  for k,v in items:need(k not in result,"Duplicate metadata JSON key");result[k]=v
  return result
 return json.loads(safe(p).read_bytes(),object_pairs_hook=pairs)
def allocated_tres(value):
 result={}
 for item in value.split(","):
  need(item and "=" in item,"Explicit allocated CPU TRES required")
  k,v=item.split("=",1);need(k and k not in result,"Duplicate/empty allocated TRES key");result[k]=v
 need("cpu" in result and re.fullmatch("[0-9]+",result["cpu"]),"Numeric allocated CPU required")
 values=[]
 for k,v in result.items():
  if k=="gres/gpu" or k.startswith("gres/gpu:"):
   need(re.fullmatch("[0-9]+",v),"Numeric allocated GPU required");values.append((k,int(v)))
 gpu=max(dict(values).get("gres/gpu",0),sum(v for k,v in values if k!="gres/gpu"))
 return result,int(result["cpu"]),gpu
def current_cpu():
 j=os.environ.get("SLURM_JOB_ID","");need(re.fullmatch("[0-9]+",j),"Actual owned Slurm CPU allocation required")
 need(os.environ.get("CUDA_VISIBLE_DEVICES") == "" and os.environ.get("JAX_PLATFORMS")=="cpu","CPU-only visibility/platform required")
 c=subprocess.run(["scontrol","show","job","-o",j],capture_output=True,text=True);need(c.returncode==0,"Current scheduler query failed")
 lines=[x for x in c.stdout.splitlines() if re.search(r"(?:^|\s)JobId="+re.escape(j)+r"(?:\s|$)",x)]
 need(len(lines)==1,"Current numeric scheduler allocation absent/ambiguous")
 items=re.findall(r"(\S+?)=(\S+)",lines[0]);fields={}
 for k,v in items:need(k not in fields,"Duplicate current scheduler field");fields[k]=v
 need(fields.get("JobState")=="RUNNING" and fields.get("UserId","").split("(")[0]=="u21111210118" and fields.get("Account")=="u21111210118" and fields.get("Partition")=="organ" and fields.get("JobName")=="test9_default13420_receipt_capture_v1","Exact owned organ RUNNING capture required")
 records=[allocated_tres(fields[k]) for k in ("AllocTRES","TRES") if fields.get(k)]
 need(records and all(c==1 and g==0 for d,c,g in records) and fields.get("NumCPUs")=="1" and fields.get("NumTasks")=="1","Actual current CPU1/GPU0 required")
 need(len(records)==1 or records[0][0]==records[1][0],"Contradictory current allocation fields")
 return {"job_id":j,"allocated_cpus":1,"allocated_gpus":0,"argv":["scontrol","show","job","-o",j],"returncode":c.returncode,"stdout":c.stdout,"stderr":c.stderr}
def descriptor_shape(r):
 need(type(r) is dict and set(r)=={"path","bytes","sha256"} and type(r["bytes"]) is int and r["bytes"]>=0 and type(r["path"]) is str and type(r["sha256"]) is str and re.fullmatch("[0-9a-f]{64}",r["sha256"]),"Exact embedded metadata descriptor shape required")
 # Metadata shape only. No child path is opened or hashed.
def producer_terminal():
 argv=["sacct","-X","-j","13420","--noheader","--parsable2","--format=JobID%32,JobIDRaw,State,ExitCode,ElapsedRaw,AllocCPUS,AllocTRES%220,User%64,Account%64,Partition%64,JobName%128"]
 p=subprocess.run(argv,capture_output=True,text=True);need(p.returncode==0,"Actual default13420 terminal query failed")
 lines=p.stdout.splitlines();need(len(lines)==1,"Unique original13420 terminal allocation required")
 fields=lines[0].strip().split("|")
 if fields and fields[-1]=="":fields.pop()
 need(len(fields)==11,"Exact producer accounting schema required")
 job,raw,state,exitcode,elapsed,cpus,tres,owner,account,partition,name=fields
 parsed,c,g=allocated_tres(tres)
 need(job==raw=="13420" and state=="COMPLETED" and exitcode=="0:0" and elapsed=="2252" and cpus==str(c)=="1" and g==0 and owner==account=="u21111210118" and partition=="organ" and name=="test9_default_materialized_integration_v3","Actual accepted default13420 CPU1/GPU0 terminal identity required")
 return {"argv":argv,"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr,"job_id":job,"raw_job_id":raw,"state":state,"exit_code":exitcode,"elapsed_seconds":int(elapsed),"allocated_cpus":c,"allocated_gpus":g,"allocated_tres":parsed,"owner":owner,"account":account,"partition":partition,"job_name":name}
def accepted_metadata(a):
 need(a["schema"]=="default-materialized-generic-integration-acceptance.v2" and a["status"]=="DEFAULT_GENERIC_PHYSICAL_GATE_AND_MATERIALIZED_RUNTIME_INTEGRATION_CPU_VERIFIED_NOT_PUBLISHED" and a["slurm_job_id"]==a["allocation"]["job_id"]=="13420" and a["allocation"]["allocated_cpus"]==1 and a["allocation"]["allocated_gpus"]==0,"Exact accepted default integration metadata required")
 need(all(a[k] is False for k in ("formal_sources_changed","models_recomputed","GPU_submitted","Git_changed","ACTIVE_changed","experimental_binding","experimental_blockade")),"Original no model/GPU/Git/ACTIVE/experimental scope required")
 need(a["staged_common_never_installed"] is True and a["three_actual_runtime_components_verified"] is True,"Original common/runtime acceptance metadata required")
 for field,expected in (("source_files",{str(FROZEN/n) for n in OWN_NAMES}),("executed_library_sources",{str(FROZEN/"library"/n) for n in LIB_NAMES})):
  rows=a[field];need(type(rows) is list and len(rows)==len(expected) and {r["path"] for r in rows}==expected,"Exact accepted own4/library6 source metadata universe required")
  for r in rows:descriptor_shape(r)
 replacement=a["replacement"]
 for checks in (a["expected_default_checks"],replacement["postchecks"]):
  generic=checks["generic_regression"]
  need(generic["tests"]==125 and all(generic[k]==0 for k in ("failures","errors","skipped","returncode")) and checks["physical_tests"]==42 and checks["staged_selector_tests"]==15 and checks["all_relevant_physical_contracts"]==57,"Actual saved before/after check metadata counts125/42/15 required")
  suites=checks["physical_suites"]
  need(type(suites) is list and len(suites)==3 and sorted(x["tests"] for x in suites)==[8,9,25] and all(x["returncode"]==0 for x in suites) and checks["staged_selector_suite"]["returncode"]==0 and checks["current_runtime"]["returncode"]==0,"Actual saved complete check-command metadata required")
 need(replacement["replaced_paths"]==list(PATHS),"Exactly three accepted destination metadata operations required")
 new=replacement["new_default_files"];need(type(new) is list and len(new)==3 and {r["path"] for r in new}=={str(R/"source"/n) for n in PATHS},"Exact installed three-path metadata required")
 for r in new:descriptor_shape(r)
 history=S/"runs/default_materialized_integration_13420/old_default_exact_history"
 for key,name in (("old_pipeline_archive",PATHS[0]),("old_rfd_lock_archive",PATHS[2])):
  r=replacement[key];descriptor_shape(r);need(r["path"]==str(history/name),"Exact preserved old archive metadata path required")
 descriptor_shape(replacement["transaction_journal"])
 need(replacement["transaction_journal"]["path"]==str(S/"runs/default_materialized_integration_13420/transaction_journal.json"),"Exact original transaction metadata pointer required")
 need(a["old_tree_sha256"]==BASE and re.fullmatch("[0-9a-f]{64}",a["new_tree_sha256"]) and a["new_tree_sha256"]!=BASE,"Actual old/new default tree metadata identities required")
 return {"source_file_count":4,"executed_library_source_count":6,"installed_destination_count":3,"replaced_paths":list(PATHS),"old_tree_sha256":a["old_tree_sha256"],"new_tree_sha256":a["new_tree_sha256"],"scope":"READ_ONLY_EMBEDDED_SOURCE_METADATA_NOT_FRESH_SOURCE_REQUALIFICATION"}
def runtime_manifest_metadata(a):
 command=a["replacement"]["postchecks"]["current_runtime"]
 need(command["returncode"]==0 and command["stdout"]==POINTER,"Exact actual completed runtime command/pointer evidence required")
 verify(POINTER)
 pointer=json_read(POINTER["path"])
 need(type(pointer) is dict and set(pointer)=={"runtime_manifest","components"} and pointer["runtime_manifest"]==str(M) and pointer["components"]==["core","rfd","boltz"],"Single exact actual runtime manifest pointer required")
 manifest=rec(M);need(manifest["bytes"]==2823,"Exact current runtime manifest size required")
 m=json_read(M)
 need(m["schema_version"]==1 and m["status"]=="RUNNING" and m["run_id"]==M.parent.name and m["step"]=="default_runtime_integration_recheck" and m["execution"]["slurm_job_id"]=="13420" and m["execution"]["cuda_visible_devices"]=="" and m["runtime_validation"]=="live_capture_matches_reviewed_lock_v2" and m["evidence_tier"]=="engineering_only","Exact actual CPU-bound runtime manifest metadata required")
 need(m["claims"]["experimental_binding"] is False and m["claims"]["experimental_blockade"] is False and set(m["runtime"])=={"core","rfd","boltz"},"Actual runtime three-component/nonexperimental scope required")
 for component,row in m["runtime"].items():
  need(type(row) is dict and set(row)=={"snapshot","lock"},"Exact declared snapshot/lock metadata required")
  for key,prefix in (("snapshot","runtime-"),("lock","runtime-lock-")):
   r=row[key];descriptor_shape(r);need(r["path"]==str(M.parent/"qc"/(prefix+component+".json")),"Exact actual runtime child metadata namespace required")
  need(row["snapshot"]["bytes"]==row["lock"]["bytes"] and row["snapshot"]["sha256"]==row["lock"]["sha256"],"Actual declared snapshot/lock metadata equality required")
 return manifest,{"pointer_stdout":POINTER,"runtime_manifest":manifest,"run_id":m["run_id"],"step":m["step"],"recorded_run_status":m["status"],"status_scope":"COMMON_RUNTIME_RECORD_STATUS_IS_NOT_GENERAL_RUN_ACCEPTANCE","components":["core","rfd","boltz"],"runtime_validation":m["runtime_validation"],"child_metadata_only_not_opened_or_hashed":True}
def main():
 allocation=current_cpu() # Mandatory before all content hashes; no scientific import.
 need(OWN==S/"pending/root_default13420_receipt_capture_v1","Exact distinct source directory required")
 own={name:rec(OWN/name) for name in ("capture.py","capture_cpu.sbatch")}
 terminal=producer_terminal()
 acceptance=rec(A);need(acceptance["bytes"]==66643,"Exact root-declared current acceptance size required")
 a=json_read(A);metadata=accepted_metadata(a)
 manifest,runtime_metadata=runtime_manifest_metadata(a)
 out=safe(S/"runs"/("default13420_receipt_capture_"+allocation["job_id"]));need(not out.exists(),"Distinct new descriptor output required");out.mkdir()
 directory=out/"source";directory.mkdir();snapshots=[]
 for name,r in own.items():
  p=directory/name
  with p.open("xb") as f:f.write(safe(r["path"]).read_bytes())
  p.chmod(0o444);snapshot=rec(p)
  need(snapshot["bytes"]==r["bytes"] and snapshot["sha256"]==r["sha256"],"Whole2 executing source snapshot mismatch")
  snapshots.append({"original":r,"snapshot":snapshot})
 for r in own.values():verify(r)
 verify(acceptance);verify(manifest);verify(POINTER)
 result={"schema":"root-default13420-receipt-descriptor-capture.v1","status":"DESCRIPTOR_CAPTURE_ONLY_NOT_NEW_SOFTWARE_OR_SCIENTIFIC_ACCEPTANCE","allocation":allocation,"producer_terminal":terminal,"acceptance":acceptance,"runtime_manifest":manifest,"runtime_manifest_pointer_evidence":runtime_metadata,"accepted_default_metadata":metadata,"owned_source_count":2,"original_executing_sources":list(own.values()),"source_snapshots":snapshots,"whole2_sources_before_after_bytes_equal":True,"accepted_target_before_after_bytes_equal":True,"runtime_manifest_and_pointer_before_after_bytes_equal":True,"hash_scope":"ONLY_ACTUAL_ACCEPTANCE_RUNTIME_MANIFEST_TINY_DECLARED_STDOUT_AND_OWN2_SNAPSHOTS","default_source_or_archive_children_opened":False,"scientific_recomputation_performed":False,"software53_or84_retested":False,"models_rerun":False,"GPU_submitted":False,"Git_changed":False,"ACTIVE_changed":False,"original_receipts_mutated":False}
 p=out/"descriptor_capture.json"
 with p.open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write("\n")
 p.chmod(0o444)
 for r in own.values():verify(r)
 verify(acceptance);verify(manifest);verify(POINTER)
 for r in snapshots:verify(r["snapshot"])
 print(json.dumps({"job_id":allocation["job_id"],"acceptance":acceptance,"runtime_manifest":manifest,"pointer_stdout":POINTER,"descriptor_capture":rec(p),"status":result["status"]},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
