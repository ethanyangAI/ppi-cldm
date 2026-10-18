import os,json,hashlib,tarfile,io,datetime,uuid
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9").resolve();A=R/"archive";S=R/"steps/13_backup_validation"
name="reconstruction_completed_modules_20261002";archive=A/(name+".tar.gz")
assert not archive.exists(),"Never overwrite a frozen archive"
rid=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"_supplement_"+os.environ["SLURM_JOB_ID"]+"_"+uuid.uuid4().hex[:8]
run=S/"runs"/rid;run.mkdir(parents=True,exist_ok=False)
selected={};excluded={};loaded=set();remapped=[];seedlist=[]
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for data in iter(lambda:f.read(1048576),b""):h.update(data)
 return h.hexdigest()
def exclude(p):
 try:rel=p.relative_to(R)
 except ValueError:return "OUTSIDE_PROJECT_ROOT_REFERENCE"
 if rel.parts[0] in ("env","assets","vendor","source","archive","cache"):return "ENVIRONMENT_ASSET_CACHE_OR_SEPARATE_SOURCE_ARCHIVE"
 if p.suffix in (".py",".sh",".sbatch",".pyc"):return "SOURCE_SEPARATELY_BUNDLED"
 if any(x in rel.parts for x in ("__pycache__","conda_pkgs","pip_cache")):return "CACHE"
 if str(p).endswith((".tar",".tar.gz",".tar.zst",".zip",".whl")):return "BULK_REDOWNLOADABLE_ARCHIVE"
 return None
def add(p,expected=None,reason="explicit accepted seed",recurse=True):
 p=Path(p);p=p if p.is_absolute() else R/p
 why=exclude(p)
 if why:
  excluded[str(p)]={"path":str(p),"reason":why}
  if expected:excluded[str(p)]["record"]=expected
  return
 assert p.is_file() and not p.is_symlink(),str(p)
 assert p.resolve().is_relative_to(R)
 row={"path":str(p.relative_to(R)),"sha256":sha(p),"bytes":p.stat().st_size,"reason":reason}
 if expected:
  assert row["sha256"]==expected["sha256"],str(p)
  if "bytes" in expected:assert row["bytes"]==expected["bytes"],str(p)
 if row["path"] in selected:assert selected[row["path"]]["sha256"]==row["sha256"]
 selected[row["path"]]=row
 if recurse and p.suffix==".json" and row["path"] not in loaded:
  loaded.add(row["path"]);walk(json.loads(p.read_text()),row["path"])
def walk(obj,origin):
 if isinstance(obj,dict):
  if isinstance(obj.get("path"),str) and isinstance(obj.get("sha256"),str) and Path(obj["path"]).is_absolute():add(obj["path"],obj,"manifest reference: "+origin)
  for v in obj.values():walk(v,origin)
 elif isinstance(obj,list):
  for v in obj:walk(v,origin)
seeds=[
"steps/09_boltz_restore/outputs/gpu_evaluation_acceptance_11787.json",
"steps/09_boltz_restore/outputs/native_predict_acceptance_11801.json",
"steps/09_boltz_restore/outputs/auto_discovery_acceptance.json",
"steps/09_boltz_restore/outputs/GPU_VALIDATION_REPORT.md",
"steps/09_boltz_restore/outputs/gpu_validation_metrics.tsv",
"steps/09_boltz_restore/outputs/auto_discovery_stdout.json",
"steps/09_boltz_restore/outputs/auto_discovery_stderr.txt",
"steps/12_physics_reassessment/runs/20261002T120847Z_11767/acceptance.json",
"steps/01_pose/runs/20261002T122613Z_0699ff01fe57/manifest.json"]
for p in seeds:add(p);seedlist.append(p)
# Retain small exact metadata as evidence snapshots, not an environment/cache tree.
auto=json.loads((R/seeds[2]).read_text())
physics=json.loads((R/seeds[7]).read_text())
assert auto["status"]=="AUTO_EXPERIMENTAL_DISCOVERY_ACCEPTED"
assert physics["status"]=="ALL_18_CPU_PHYSICS_RUNS_VERIFIED" and physics["verified_count"]==18
first=json.loads(Path(physics["results"][0]["path"]).read_text())
for label,record in (("auto_discovery_search.json",auto["search_receipt"]),("physics_environment_freeze.txt",first["environment_freeze"])):
 source=Path(record["path"]);assert sha(source)==record["sha256"]
 assert source.stat().st_size<1048576
 dest=run/"evidence_snapshots"/label;dest.parent.mkdir(exist_ok=True);dest.write_bytes(source.read_bytes())
 add(dest,reason="explicit small metadata snapshot")
 remapped.append({"original":record,"snapshot":selected[str(dest.relative_to(R))]})
evalacc=json.loads((R/seeds[0]).read_text());nativeacc=json.loads((R/seeds[1]).read_text())
assert evalacc["status"]=="BOLTZ_GPU_EVALUATION_ACCEPTED" and evalacc["candidate_status"]=="REJECTED"
assert nativeacc["status"]=="BOLTZ_NATIVE_PREDICT_ENGINEERING_ACCEPTED" and nativeacc["prediction_status"]=="POSE_ACCEPTED"
assert len(evalacc["structure_sequence_checks"])==3 and len(nativeacc["comparison"])==3
assert len(physics["results"])==18
for record in physics["results"]:
 result=json.loads(Path(record["path"]).read_text())
 assert result["status"]=="COMPUTED_NOT_EXPERIMENTAL_VALIDATION"
 assert str(Path(result["relaxed_pdb"]["path"]).relative_to(R)) in selected
baseidx=json.loads((A/"reconstruction_data_20261002.members.json").read_text())
basereceipt=Path(baseidx["validation_run"])/"independent_restore_receipt.json"
baseacc=json.loads(basereceipt.read_text())
assert baseacc["status"]=="DATA_ARCHIVE_INDEPENDENTLY_RESTORED_AND_SHA256_VERIFIED"
base={"archive":baseidx["archive"],"sha256":baseidx["archive_sha256"],"members_index":str(A/"reconstruction_data_20261002.members.json"),"members_index_sha256":sha(A/"reconstruction_data_20261002.members.json"),"restore_receipt":str(basereceipt),"restore_receipt_sha256":sha(basereceipt)}
counts={"boltz_native_predicted_structures":3,"boltz_new_binder_evaluated_structures":3,"boltz_new_binder_candidates_rejected":1,"cpu_physics_results_and_relaxed_structures":18,"auto_experimental_discovery_successes":1}
meta={"schema":"test9-completed-modules-supplement-v1","created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"FROZEN_COMPLETED_MODULES_SNAPSHOT","builder_job":os.environ["SLURM_JOB_ID"],"original_root":str(R),"base_package":base,"included_completed_modules":["Boltz native prediction","Boltz generated binder evaluation with computational rejection retained","18 CPU Rosetta diagnostics","Automatic experimental structure discovery"],"excluded_ongoing_modules":[],"base_snapshot_exclusions_resolved_by_this_package":True,"scope_counts":counts,"authority_seeds":seedlist,"excluded_references":list(excluded.values()),"remapped_small_metadata":remapped,"payload_members":[selected[x] for x in sorted(selected)],"claims":{"offsite_backup":False,"experimental_blockade":False,"workflow_superiority":False}}
mb=(json.dumps(meta,indent=2,ensure_ascii=False)+"\n").encode()
rows=[{k:row[k] for k in ("path","sha256","bytes")} for _,row in sorted(selected.items())]
rows.append({"path":"_backup_supplement/manifest.json","bytes":len(mb),"sha256":hashlib.sha256(mb).hexdigest()})
sums="".join(x["sha256"]+"  "+x["path"]+"\n" for x in rows).encode()
rows.append({"path":"_backup_supplement/SHA256SUMS","bytes":len(sums),"sha256":hashlib.sha256(sums).hexdigest()})
tmp=archive.with_suffix(".gz.partial");assert not tmp.exists()
with tarfile.open(tmp,"w:gz",compresslevel=6,format=tarfile.PAX_FORMAT) as tar:
 for row in rows:
  p=row["path"]
  data=mb if p=="_backup_supplement/manifest.json" else sums if p=="_backup_supplement/SHA256SUMS" else (R/p).read_bytes()
  assert len(data)==row["bytes"] and hashlib.sha256(data).hexdigest()==row["sha256"],p
  info=tarfile.TarInfo(p);info.size=len(data);info.mode=0o644;info.mtime=0;tar.addfile(info,io.BytesIO(data))
tmp.replace(archive)
idx={"archive":str(archive),"archive_bytes":archive.stat().st_size,"archive_sha256":sha(archive),"member_count":len(rows),"members":rows,"validation_run":str(run),"scope_counts":counts,"base_package":base,"excluded_ongoing_modules":[]}
for p,body in ((A/(name+".members.json"),json.dumps(idx,indent=2)+"\n"),(A/(name+".members.sha256"),"".join(x["sha256"]+"  "+x["path"]+"\n" for x in rows)),(A/(name+".sha256"),idx["archive_sha256"]+"  "+archive.name+"\n"),(run/"build_receipt.json",json.dumps(idx,indent=2)+"\n")):
 with p.open("x") as f:f.write(body)
print(json.dumps({k:v for k,v in idx.items() if k!="members"},indent=2),flush=True)

