import os,json,hashlib,tarfile
from pathlib import Path,PurePosixPath
R=Path("/lustre/users/u21111210118/projects/test9");A=R/"archive"
indexpath=A/"reconstruction_data_20261002.members.json";idx=json.loads(indexpath.read_text())
archive=Path(idx["archive"]);run=Path(idx["validation_run"]);out=run/"restored"
out.mkdir(exist_ok=False)
def digest(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
assert digest(archive)==idx["archive_sha256"]
expected={r["path"]:r for r in idx["members"]};assert len(expected)==idx["member_count"]
seen=set()
with tarfile.open(archive,"r:gz") as tar:
 for m in tar:
  rel=PurePosixPath(m.name)
  assert not rel.is_absolute() and ".." not in rel.parts and "\\" not in m.name
  assert m.isfile() and not (m.issym() or m.islnk()),m.name
  assert m.name in expected and m.name not in seen;seen.add(m.name)
  dest=out.joinpath(*rel.parts);assert dest.resolve().is_relative_to(out.resolve())
  dest.parent.mkdir(parents=True,exist_ok=True)
  h=hashlib.sha256();n=0
  with tar.extractfile(m) as f,dest.open("xb") as g:
   for data in iter(lambda:f.read(1048576),b""):g.write(data);h.update(data);n+=len(data)
  assert n==expected[m.name]["bytes"] and h.hexdigest()==expected[m.name]["sha256"],m.name
assert seen==set(expected)
assert {str(p.relative_to(out)) for p in out.rglob("*") if p.is_file()}==seen
for rel,row in expected.items():assert digest(out/rel)==row["sha256"],rel
# Independent semantic read-back uses only extracted payload, not the source files.
def restored_record(row):
 p=out/Path(row["path"]).relative_to(R)
 assert p.is_file() and digest(p)==row["sha256"],row["path"]
 return p
meta=json.loads((out/"_backup/manifest.json").read_text())
af2=json.loads((out/"steps/08_candidate_refolds/outputs/acceptance.json").read_text())
assert af2["status"]=="ALL_90_AF2_MODELS_VERIFIED" and af2["model_count"]==90 and len(af2["accepted_entries"])==6
for entry in af2["accepted_entries"]:
 assert len(entry["models"])==15
 assert {(m["model"],m["seed"]) for m in entry["models"]}=={(m,s) for m in range(1,6) for s in (1042,1043,1044)}
 restored_record(entry["run_manifest"])
 for m in entry["models"]:
  restored_record(m["pdb"]);restored_record(m["scores"])
cand=json.loads((out/"01_raw/recovered_inputs/recovered_three_candidates.json").read_text());assert len(cand["entries"])==3
reg=json.loads((out/"00_admin/reconstruction_20261002.json").read_text())
controls=json.loads(restored_record(reg["evidence"]["controls_manifest"]).read_text())
table=json.loads(restored_record(controls["outputs"]["controls78"]).read_text())["entries"];assert len(table)==78
auth=json.loads(restored_record(reg["evidence"]["author_models"]).read_text())
authorrows=json.loads(restored_record(auth["outputs"]["author_models60"]).read_text())["entries"]
authorpaths=set()
for entry in authorrows+table:
 if "author_model" in entry:
  p=restored_record(entry["author_model"]);authorpaths.add(str(p))
assert len(authorpaths)==78
nativeids=set()
for suffix in ("20261002T114000Z_11716","20261002T114903Z_11737"):
 m=json.loads((out/"steps/06_native_diagnostics/runs"/suffix/"manifest.json").read_text())
 assert m["status"]=="EXPERIMENTAL_NATIVE_REFERENCES_PREPARED_NOT_PREDICTIVE_VALIDATION"
 for name,row in m["outputs"].items():
  restored_record(row)
  if name.endswith("_normalized.pdb"):nativeids.add(name[:4])
assert nativeids=={"2FLU","4CH9","6TTK"}
for key in ("pose_manifest","pose_independent","primary_medoids","controls_independent","author_models_independent"):restored_record(reg["evidence"][key])
receipt={"status":"DATA_ARCHIVE_INDEPENDENTLY_RESTORED_AND_SHA256_VERIFIED","job":os.environ.get("SLURM_JOB_ID"),"archive":str(archive),"archive_sha256":idx["archive_sha256"],"archive_bytes":idx["archive_bytes"],"members":len(seen),"all_member_sha256_verified":True,"relative_regular_members_only":True,"external_links":0,"restored_root":str(out),"scope_counts":meta["scope_counts"],"excluded_ongoing_modules":meta["excluded_ongoing_modules"],"offsite_backup":False,"original_files_modified":False}
(run/"independent_restore_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2),flush=True)
