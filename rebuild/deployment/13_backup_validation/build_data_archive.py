import os,json,time,hashlib,tarfile,io,datetime,uuid
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9").resolve()
A=R/"archive";A.mkdir(exist_ok=True)
name="reconstruction_data_20261002"
archive=A/(name+".tar.gz");members_json=A/(name+".members.json");members_sha=A/(name+".members.sha256")
assert not any(p.exists() for p in (archive,members_json,members_sha)),"Refuse overwriting previous archive"
S=R/"steps/13_backup_validation";rid=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"_data_"+os.environ.get("SLURM_JOB_ID","nojob")+"_"+uuid.uuid4().hex[:8]
run=S/"runs"/rid;run.mkdir(parents=True,exist_ok=False)
selected={};excluded={};loaded=set();snapshot={}
registry_path=R/"00_admin/reconstruction_20261002.json"
snapshot[str(registry_path)]=registry_path.read_bytes()
registry=json.loads(snapshot[str(registry_path)])
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def exclusion(p):
 try:rel=p.relative_to(R)
 except ValueError:return "OUTSIDE_CURRENT_ROOT_HISTORICAL_REFERENCE"
 if rel.parts[0] in ("env","vendor","assets","cache","source","archive"):return "RECREATABLE_ENV_VENDOR_ASSET_OR_SEPARATE_SOURCE_BUNDLE"
 if any(x in rel.parts for x in ("__pycache__","conda_pkgs","pip_cache")):return "CACHE"
 if any(x in rel.parts for x in ("09_boltz_restore","11_physics_restore","12_physics_reassessment","02_predict","04_evaluate")):return "ONGOING_MODULE_EXCLUDED"
 if p.suffix in (".py",".sh",".sbatch",".pyc"):return "SOURCE_CODE_SEPARATE_GIT_BUNDLE"
 if str(p).endswith((".tar",".tar.gz",".tar.zst",".zip",".whl")):return "PUBLIC_BULK_ARCHIVE_REDOWNLOADABLE"
 if rel==Path("01_raw/control_sources/final_dataset.csv"):return "PUBLIC_BULK_TABLE_REDOWNLOADABLE_SELECTED_ROWS_INCLUDED"
 return None
def add(p,expected=None,reason="explicit seed",recurse=True):
 p=Path(p)
 if not p.is_absolute():p=R/p
 why=exclusion(p)
 if why:
  excluded[str(p)]={"path":str(p),"reason":why}
  if expected:excluded[str(p)]["original_record"]=expected
  return
 assert not p.is_symlink(),"Symlink input not permitted: "+str(p)
 assert p.is_file(),"Required archive input absent: "+str(p)
 assert p.resolve().is_relative_to(R)
 rel=str(p.relative_to(R))
 raw=snapshot.get(str(p))
 actual={"path":rel,"bytes":len(raw) if raw is not None else p.stat().st_size,"sha256":hashlib.sha256(raw).hexdigest() if raw is not None else sha(p)}
 if expected:
  assert actual["sha256"]==expected["sha256"],("Input checksum mismatch",p)
  if "bytes" in expected:assert actual["bytes"]==expected["bytes"],("Size mismatch",p)
 if rel in selected:assert selected[rel]["sha256"]==actual["sha256"]
 else:selected[rel]={**actual,"selection_reason":reason}
 if recurse and p.suffix==".json" and rel not in loaded:
  loaded.add(rel)
  obj=json.loads(raw if raw is not None else p.read_bytes())
  walk(obj,rel)
def walk(obj,origin):
 if isinstance(obj,dict):
  if isinstance(obj.get("path"),str) and isinstance(obj.get("sha256"),str):
   # Only full file receipts, not relative source-file inventories or bare asset labels.
   if Path(obj["path"]).is_absolute():add(obj["path"],obj,reason="manifest reference: "+origin)
  for v in obj.values():walk(v,origin)
 elif isinstance(obj,list):
  for v in obj:walk(v,origin)
# Explicit authority roots: never infer acceptance from directory mtime or newest filename.
for p in ("CLUSTER_BINDING.md","00_admin/reconstruction_20261002.json",
"01_raw/recovered_inputs/candidate_recovery_receipt.json","01_raw/recovered_inputs/recovered_three_candidates.json",
"steps/03_af2_restore/manifest.json","steps/08_candidate_refolds/outputs/acceptance.json",
"steps/06_native_diagnostics/runs/20261002T114000Z_11716/manifest.json",
"steps/06_native_diagnostics/runs/20261002T114000Z_11716/outputs/independent_validation_11722.json",
"steps/06_native_diagnostics/runs/20261002T114903Z_11737/manifest.json",
"steps/06_native_diagnostics/runs/20261002T114903Z_11737/outputs/independent_validation_11749.json",
"01_raw/experimental_structures/manifest.json"):
 add(p,reason="explicit authority/accepted run seed")
for key in ("controls_manifest","controls_independent","author_models","author_models_independent","pose_manifest","pose_independent","primary_medoids","KEAP1_prepared","MDM2_prepared","RFdiffusion_design","history_handoff"):
 x=registry["evidence"][key];add(x["path"],x,reason="registered evidence: "+key)
# History events are archival evidence, explicitly requested; not executable restored source.
for p in ("source_body_events.json","source_additional_events.json","events_manifest.json","extraction_receipt.json","literal_inventory.json","body_syntax_diagnostics.json","pending_edits.json","python_edit_candidates.json"):
 add(R/"01_raw/history"/p,reason="explicit recovery history",recurse=False)
for p in ("history_handoff_receipt.json","history_patch_interpretation.json","history_recovered_syntax.json","history_recovery_inventory.json","history_recovery_summary.json","history_text_edits.json","history_unresolved_adjudicated.json","history_unresolved.json"):
 add(R/"steps/01_recovery/work"/p,reason="explicit handoff/adjudication record",recurse=False)
for p in ("steps/03_af2_restore/logs/finaltests_11818.out","steps/03_af2_restore/logs/finaltests_11818.err","steps/03_af2_restore/source_audit.json","steps/03_af2_restore/logs/activation_11808.out","steps/03_af2_restore/logs/locktest_11788.out"):
 add(p,reason="independent software/deployment validation",recurse=False)
af2=json.loads((R/"steps/08_candidate_refolds/outputs/acceptance.json").read_text())
assert af2["status"]=="ALL_90_AF2_MODELS_VERIFIED" and af2["model_count"]==90
assert len(af2["accepted_entries"])==6
badids=("20261002T114655Z_eae89fb33495","20261002T114821Z_621c642a008e")
assert not any(any(x in rel for x in badids) for rel in selected),"Invalid AF2 attempted run included"
controls=json.loads(Path(registry["evidence"]["controls_manifest"]["path"]).read_text())
ct=Path(controls["outputs"]["controls78"]["path"]);ctrows=json.loads(ct.read_text())["entries"];assert len(ctrows)==78
author=json.loads(Path(registry["evidence"]["author_models"]["path"]).read_text())
ar=json.loads(Path(author["outputs"]["author_models60"]["path"]).read_text())["entries"];assert len(ar)==60
author_paths={e["author_model"]["path"] for e in ar}|{e["author_model"]["path"] for e in ctrows if "author_model" in e}
assert len(author_paths)==78
assert all(str(Path(p).relative_to(R)) in selected for p in author_paths)
assert all(str(Path(model[key]["path"]).relative_to(R)) in selected for e in af2["accepted_entries"] for model in e["models"] for key in ("pdb","scores"))
metadata={"schema":"test9-data-reconstruction-backup-v1","status":"FROZEN_ACCEPTED_DATA_SNAPSHOT","created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"original_root":str(R),"builder_job":os.environ.get("SLURM_JOB_ID"),"run_id":rid,"registry_snapshot_sha256":hashlib.sha256(snapshot[str(registry_path)]).hexdigest(),"scope_counts":{"recovered_candidates":3,"control_identities":78,"author_input_models":78,"new_af2_models":90,"new_af2_complex_models":45,"new_af2_monomer_models":45,"native_references":3},"excluded_ongoing_modules":[{"module":"Boltz native-pose and generated-binder evaluation","reason":"Still in progress at archive planning; no outputs claimed accepted in this package."},{"module":"Rosetta physics reassessment","reason":"Still in progress at archive planning; reserved for explicit supplementary archive."}],"excluded_references":list(excluded.values()),"payload_members":[selected[k] for k in sorted(selected)],"claims":{"old_lost_coordinates_restored":False,"offsite_backup":False,"experimental_blockade":False},"source_code_note":"Active source belongs to a separately validated Git bundle. Requested history source-body events are retained solely as reconstruction evidence.","portability":"Tar members are relative regular files only; original absolute paths inside untouched receipts retain provenance. Independent read-back rebases those paths to extracted root."}
metabytes=(json.dumps(metadata,indent=2,ensure_ascii=False)+"\n").encode()
allrecords=[{k:v for k,v in selected[x].items() if k in ("path","bytes","sha256")} for x in sorted(selected)]
allrecords.append({"path":"_backup/manifest.json","bytes":len(metabytes),"sha256":hashlib.sha256(metabytes).hexdigest()})
sums="".join(x["sha256"]+"  "+x["path"]+"\n" for x in allrecords).encode()
allrecords.append({"path":"_backup/SHA256SUMS","bytes":len(sums),"sha256":hashlib.sha256(sums).hexdigest()})
tmp=archive.with_suffix(archive.suffix+".partial")
assert not tmp.exists()
with tarfile.open(tmp,"w:gz",compresslevel=6,format=tarfile.PAX_FORMAT) as tar:
 for record in allrecords:
  rel=record["path"]
  if rel=="_backup/manifest.json":data=metabytes
  elif rel=="_backup/SHA256SUMS":data=sums
  else:
   p=R/rel;data=snapshot.get(str(p))
   if data is None:data=p.read_bytes()
  assert len(data)==record["bytes"] and hashlib.sha256(data).hexdigest()==record["sha256"],("Changed during archive",rel)
  info=tarfile.TarInfo(rel);info.size=len(data);info.mode=0o644;info.mtime=0
  tar.addfile(info,io.BytesIO(data))
tmp.replace(archive)
external={"archive":str(archive),"archive_bytes":archive.stat().st_size,"archive_sha256":sha(archive),"member_count":len(allrecords),"members":allrecords,"validation_run":str(run),"scope_counts":metadata["scope_counts"],"excluded_ongoing_modules":metadata["excluded_ongoing_modules"]}
members_json.write_text(json.dumps(external,indent=2)+"\n")
members_sha.write_text("".join(x["sha256"]+"  "+x["path"]+"\n" for x in allrecords))
(A/(name+".sha256")).write_text(external["archive_sha256"]+"  "+archive.name+"\n")
(run/"build_receipt.json").write_text(json.dumps(external,indent=2)+"\n")
print(json.dumps({k:v for k,v in external.items() if k!="members"},indent=2),flush=True)
