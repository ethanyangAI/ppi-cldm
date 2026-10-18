#!/usr/bin/env python3
"""Descriptor capture only: four exact accepted metadata targets, no scientific replay."""
from pathlib import Path
import hashlib, json, os, re, subprocess

R=Path("/lustre/users/u21111210118/projects/test9")
S=R/"steps/24_benchmark_delivery"
OWN=Path(__file__).parent
TARGETS={
 "nativebind13409":{"job":"13409","cpu":1,"name":"ppi_native74_cache_cpu","path":S/"runs/native74_cache_bind_13409/acceptance.json","bytes":4931,"contract_path":S/"runs/native74_cache_bind_13409/contracts.json","contract_count":24,"count_field":"tests"},
 "outer13264":{"job":"13264","cpu":2,"name":"ppi_formal13260_terminal_cpu","path":R/"steps/22_matched_benchmark/formal_terminal13260_cpu13264/acceptance.json","bytes":6720,"contract_path":R/"steps/22_matched_benchmark/formal_terminal13260_cpu13264/contracts.json","contract_count":34,"count_field":"tests_run"},
 "integration13325":{"job":"13325","cpu":1,"name":"test9_default_materialized_integration_v3","path":S/"runs/default_materialized_integration_software_13325/acceptance.json","bytes":13300,"contract_path":S/"runs/default_materialized_integration_software_13325/contracts.json","contract_count":84,"count_field":"tests"},
 "common13269":{"job":"13269","cpu":2,"name":"ppi_common_successor_cpu","path":S/"runs/common_successor_contracts_13269/acceptance.json","bytes":6429,"contract_path":S/"runs/common_successor_contracts_13269/contracts.json","contract_count":58,"count_field":"tests_run"},
}
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
 need(fields.get("JobState")=="RUNNING" and fields.get("UserId","").split("(")[0]=="u21111210118" and fields.get("Account")=="u21111210118" and fields.get("Partition")=="organ" and fields.get("JobName")=="test9_current_receipt_capture_v1","Exact owned organ RUNNING capture required")
 records=[allocated_tres(fields[k]) for k in ("AllocTRES","TRES") if fields.get(k)]
 need(records and all(c==1 and g==0 for d,c,g in records) and fields.get("NumCPUs")=="1" and fields.get("NumTasks")=="1","Actual current CPU1/GPU0 required")
 need(len(records)==1 or records[0][0]==records[1][0],"Contradictory current allocation fields")
 return {"job_id":j,"allocated_cpus":1,"allocated_gpus":0,"argv":["scontrol","show","job","-o",j],"returncode":c.returncode,"stdout":c.stdout,"stderr":c.stderr}
def producer_terminal():
 argv=["sacct","-X","-j",",".join(t["job"] for t in TARGETS.values()),"--noheader","--parsable2","--format=JobID%32,JobIDRaw,State,ExitCode,ElapsedRaw,AllocCPUS,AllocTRES%220,User%64,Account%64,Partition%64,JobName%128"]
 p=subprocess.run(argv,capture_output=True,text=True);need(p.returncode==0,"Actual producer terminal query failed")
 expected={t["job"]:t for t in TARGETS.values()};rows={}
 for line in p.stdout.splitlines():
  fields=line.strip().split("|")
  if fields and fields[-1]=="":fields.pop()
  need(len(fields)==11,"Unexpected producer numeric accounting schema")
  logical,raw,state,exitcode,elapsed,cpus,tres,owner,account,partition,name=fields
  need(logical==raw and raw in expected and raw not in rows,"Unknown/duplicate producer or aggregate/step row")
  t=expected[raw];parsed,c,g=allocated_tres(tres)
  need(state=="COMPLETED" and exitcode=="0:0" and re.fullmatch("[0-9]+",elapsed) and cpus==str(c)==str(t["cpu"]) and g==0 and owner==account=="u21111210118" and partition=="organ" and name==t["name"],"Exact accepted producer numeric terminal identity required")
  rows[raw]={"job_id":logical,"raw_job_id":raw,"state":state,"exit_code":exitcode,"elapsed_seconds":int(elapsed),"allocated_cpus":c,"allocated_gpus":g,"allocated_tres":parsed,"owner":owner,"account":account,"partition":partition,"job_name":name}
 need(set(rows)==set(expected),"All four exact terminal producers required")
 return {"argv":argv,"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr,"rows":rows}
def accepted_metadata(label,a,t):
 if label=="nativebind13409":
  need(a["status"]=="CPU_CACHE_GUARD_BIND_COMPLETE" and a["formal_binding"] is True and a["no_inference"] is True and a["no_GPU_submission"] is True and a["allocation"]["job_id"]=="13409" and a["allocation"]["allocated_gpu_count"]==0,"Actual accepted native binding metadata required")
 elif label=="outer13264":
  need(a["schema"]=="formal13260_terminal_wrapper.v1" and a["status"]=="FORMAL13260_TERMINAL_V2_COLLECTION_CPU_ACCEPTED_ROOT_COMMON_PREPARATION_PENDING" and a["cpu_allocation"]["job_id"]=="13264" and a["cpu_allocation"]["allocated_gpu_count"]==0 and a["no_new_predictions"] is True and a["no_gpu_submission"] is True and a["common_review_not_inferred"] is True and a["workflow_superiority"] is False,"Actual accepted collection wrapper metadata required")
 elif label=="integration13325":
  need(a["schema"]=="default-materialized-integration-software-acceptance.v2" and a["status"]=="DEFAULT_MATERIALIZED_INTEGRATION_SOFTWARE_CPU_ACCEPTED_NO_DEFAULT_WRITE" and a["allocation"]["job_id"]=="13325" and a["allocation"]["allocated_cpus"]==1 and a["allocation"]["allocated_gpus"]==0 and a["tests_expected"]==84 and a["compiled_all_python"] is True and a["bash_syntax_checked"] is True,"Actual accepted integration software metadata required")
  need(all(a[k] is False for k in ("default_written","science_accepted","models_recomputed","GPU_submitted","ACTIVE_changed")),"Software-only integration scope required")
 elif label=="common13269":
  need(a["status"]=="COMMON_SUCCESSOR_SOFTWARE_SOURCE_CPU_ACCEPTED_FUTURE_FORMAL_PREPARATION_PENDING" and a["actual_CPU_job_id"]=="13269" and a["no_inference"] is True and a["no_GPU_submission"] is True and a["future_formal_binding"] is False,"Actual accepted Common software metadata required")
 else:raise ValueError("Unknown target namespace")
 need(a["contracts"]["path"]==str(t["contract_path"]),"Exact producer contract metadata path required")
def main():
 allocation=current_cpu() # Before every source/target content hash; no scientific import.
 need(OWN==S/"pending/root_current_receipt_capture_v1","Exact owned capture source directory required")
 own={}
 for name in ("capture.py","capture_cpu.sbatch"):own[name]=rec(OWN/name)
 terminal=producer_terminal()
 original={}
 captured={}
 for label,t in TARGETS.items():
  r=rec(t["path"]);need(r["bytes"]==t["bytes"],"Exact current accepted target size required");original[label]=r
  a=json_read(t["path"]);accepted_metadata(label,a,t)
  contract=a["contracts"];verify(contract);c=json_read(contract["path"])
  need(c["status"]=="PASS" and c[t["count_field"]]==t["contract_count"] and c["failures"]==c["errors"]==0,"Actual saved contract status/count metadata required")
  captured[label]={"acceptance":r,"contracts":contract,"producer_terminal":terminal["rows"][t["job"]],"accepted_status":a["status"],"scope":"DESCRIPTOR_ONLY_PRESERVES_ORIGINAL_ACCEPTANCE_SCOPE"}
 out=safe(S/"runs"/("current_receipt_capture_"+allocation["job_id"]));need(not out.exists(),"Distinct new descriptor output required");out.mkdir()
 source_dir=out/"source";source_dir.mkdir();frozen=[]
 for name,r in own.items():
  dest=source_dir/name
  with dest.open("xb") as f:f.write(safe(r["path"]).read_bytes())
  dest.chmod(0o444);d=rec(dest);need(d["bytes"]==r["bytes"] and d["sha256"]==r["sha256"],"Whole2 executing-source snapshot mismatch")
  frozen.append({"original":r,"snapshot":d})
 for r in own.values():verify(r)
 for r in original.values():verify(r)
 for d in captured.values():verify(d["contracts"])
 result={"schema":"root-current-accepted-receipt-descriptor-capture.v1","status":"DESCRIPTOR_CAPTURE_ONLY_NOT_NEW_SCIENTIFIC_ACCEPTANCE","allocation":allocation,"producer_terminal_evidence":terminal,"targets":captured,"owned_source_count":2,"original_executing_sources":list(own.values()),"frozen_source_snapshots":frozen,"whole2_source_before_after_bytes_equal":True,"accepted_targets_before_after_bytes_equal":True,"scientific_recomputation_performed":False,"models_rerun":False,"GPU_submitted":False,"original_receipts_mutated":False,"ACTIVE_changed":False}
 p=out/"descriptor_capture.json"
 with p.open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write("\n")
 p.chmod(0o444)
 for r in own.values():verify(r)
 for r in original.values():verify(r)
 for d in captured.values():verify(d["contracts"])
 for d in frozen:verify(d["snapshot"])
 print(json.dumps({"job_id":allocation["job_id"],"descriptor_capture":rec(p),"targets":captured,"status":result["status"]},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
