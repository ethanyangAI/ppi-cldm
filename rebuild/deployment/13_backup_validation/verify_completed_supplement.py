import os,json,hashlib,tarfile,datetime
from pathlib import Path,PurePosixPath
R=Path("/lustre/users/u21111210118/projects/test9");A=R/"archive"
idxpath=A/"reconstruction_completed_modules_20261002.members.json";idx=json.loads(idxpath.read_text())
archive=Path(idx["archive"]);run=Path(idx["validation_run"]);out=run/"restored";out.mkdir(exist_ok=False)
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for data in iter(lambda:f.read(1048576),b""):h.update(data)
 return h.hexdigest()
assert sha(archive)==idx["archive_sha256"]
expected={x["path"]:x for x in idx["members"]};assert len(expected)==idx["member_count"];seen=set()
with tarfile.open(archive,"r:gz") as tar:
 for m in tar:
  p=PurePosixPath(m.name)
  assert not p.is_absolute() and ".." not in p.parts and "\\" not in m.name
  assert m.isfile() and not m.islnk() and not m.issym()
  assert m.name in expected and m.name not in seen;seen.add(m.name)
  dest=out.joinpath(*p.parts);assert dest.resolve().is_relative_to(out.resolve())
  dest.parent.mkdir(parents=True,exist_ok=True)
  h=hashlib.sha256();n=0
  with tar.extractfile(m) as f,dest.open("xb") as g:
   for data in iter(lambda:f.read(1048576),b""):g.write(data);h.update(data);n+=len(data)
  assert h.hexdigest()==expected[m.name]["sha256"] and n==expected[m.name]["bytes"],m.name
assert seen==set(expected)
assert seen=={str(p.relative_to(out)) for p in out.rglob("*") if p.is_file()}
for rel,row in expected.items():assert sha(out/rel)==row["sha256"]
def restored(row):
 p=out/Path(row["path"]).relative_to(R);assert p.is_file() and sha(p)==row["sha256"],row["path"];return p
evalacc=json.loads((out/"steps/09_boltz_restore/outputs/gpu_evaluation_acceptance_11787.json").read_text())
nativeacc=json.loads((out/"steps/09_boltz_restore/outputs/native_predict_acceptance_11801.json").read_text())
auto=json.loads((out/"steps/09_boltz_restore/outputs/auto_discovery_acceptance.json").read_text())
physics=json.loads((out/"steps/12_physics_reassessment/runs/20261002T120847Z_11767/acceptance.json").read_text())
assert evalacc["status"]=="BOLTZ_GPU_EVALUATION_ACCEPTED" and evalacc["candidate_status"]=="REJECTED" and evalacc["passing_samples"]==0
assert nativeacc["status"]=="BOLTZ_NATIVE_PREDICT_ENGINEERING_ACCEPTED" and nativeacc["prediction_status"]=="POSE_ACCEPTED"
assert auto["status"]=="AUTO_EXPERIMENTAL_DISCOVERY_ACCEPTED" and auto["pdb_chain_assembly_hint_provided"] is False and auto["exact_requested_constructs"]
for acc,key in ((evalacc,"evaluation_manifest"),(nativeacc,"prediction_manifest"),(auto,"manifest")):restored(acc[key])
assert len(evalacc["structure_sequence_checks"])==3 and len(nativeacc["comparison"])==3
for row in evalacc["structure_sequence_checks"]+nativeacc["comparison"]:restored(row["structure"])
assert physics["status"]=="ALL_18_CPU_PHYSICS_RUNS_VERIFIED" and len(physics["results"])==18
plan=json.loads(restored(physics["plan"]).read_text());assert len(plan["entries"])==18
identities=set()
for record in physics["results"]:
 result=json.loads(restored(record).read_text());restored(result["input"]);restored(result["relaxed_pdb"])
 assert result["status"]=="COMPUTED_NOT_EXPERIMENTAL_VALIDATION"
 identities.add((result["identity"],result["seed"]))
assert len(identities)==18 and len({x[0] for x in identities})==6 and {x[1] for x in identities}=={1042,1043,1044}
meta=json.loads((out/"_backup_supplement/manifest.json").read_text())
for record in meta["remapped_small_metadata"]:
 p=out/record["snapshot"]["path"];assert sha(p)==record["original"]["sha256"]
baseidxpath=A/"reconstruction_data_20261002.members.json";baseidx=json.loads(baseidxpath.read_text())
basereceiptpath=Path(baseidx["validation_run"])/"independent_restore_receipt.json";baseacc=json.loads(basereceiptpath.read_text())
assert sha(Path(baseidx["archive"]))==baseidx["archive_sha256"]
assert baseacc["status"]=="DATA_ARCHIVE_INDEPENDENTLY_RESTORED_AND_SHA256_VERIFIED"
baseexpected={x["path"]:x for x in baseidx["members"]}
overlap=set(baseexpected)&set(expected)
assert all(baseexpected[p]["sha256"]==expected[p]["sha256"] for p in overlap),"Package path collision differs"
receipt={"status":"SUPPLEMENT_ARCHIVE_INDEPENDENTLY_RESTORED_AND_SHA256_VERIFIED","job":os.environ["SLURM_JOB_ID"],"archive":str(archive),"archive_sha256":idx["archive_sha256"],"archive_bytes":idx["archive_bytes"],"members":len(seen),"all_member_sha256_verified":True,"relative_regular_members_only":True,"external_links":0,"restored_root":str(out),"scope_counts":meta["scope_counts"],"excluded_ongoing_modules":[],"compatible_with_base_package":True,"identical_overlap_members":len(overlap),"offsite_backup":False,"original_files_modified":False}
rp=run/"independent_restore_receipt.json";rp.write_text(json.dumps(receipt,indent=2)+"\n")
def file_receipt(p):return {"path":str(p),"sha256":sha(p),"bytes":p.stat().st_size}
def package(idx,ip,receiptpath):
 return {"archive":file_receipt(Path(idx["archive"])),"member_index":file_receipt(ip),"member_sha_list":file_receipt(ip.with_suffix(".sha256")),"restore_receipt":file_receipt(receiptpath),"member_count":idx["member_count"],"scope_counts":idx["scope_counts"]}
total={"schema":"test9-data-backup-set-v1","status":"BOTH_PACKAGES_INDEPENDENTLY_RESTORED_AND_ALL_MEMBERS_SHA256_VERIFIED","created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"verification_job":os.environ["SLURM_JOB_ID"],"packages":[package(baseidx,baseidxpath,basereceiptpath),package(idx,idxpath,rp)],"union_unique_member_count":len(set(baseexpected)|set(expected)),"identical_overlap_members":len(overlap),"excluded_ongoing_modules":[],"interpretation":"Base package preserves planning-time module exclusions; completed-modules supplement resolves all of them. Both packages are necessary for the complete reconstructed data snapshot.","active_source":"Separate validated Git bundle; not in these data archives.","offsite_backup":False,"experimental_blockade_proven":False,"workflow_superiority_proven":False}
indexpath=A/"reconstruction_backup_index_20261002.json"
with indexpath.open("x") as f:f.write(json.dumps(total,indent=2)+"\n")
print(json.dumps(receipt,indent=2),flush=True);print("BACKUP_SET_INDEX "+str(indexpath)+" "+sha(indexpath),flush=True)

