import json,shutil,zipfile,collections,hashlib
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,require
from ppiblocker.structure import read_structure,write_pdb
root=Path("/lustre/users/u21111210118/projects/test9");p=root/"steps/51_bindcraft_labels/runs/20260922T103545Z_9e362c8c1852/outputs/label_join.json"
am=read_json(root/"steps/34_calibration_assets/runs/20260922T100035Z_9d23276b14e3/manifest.json");archive=verify_file(am["outputs"]["DesignModels.zip"])
run=Run(root,"52_control_extension",[record_file(p),record_file(archive)])
shutil.copy2(__file__,run.path/"qc/driver.py")
rows=read_json(p);cross=collections.Counter((r["primary_binding"],r["matches"][0].get("binder"),r["matches"][0].get("expression")) for r in rows)
print("LABEL_CROSS",list(cross.items()),flush=True)
selected=[r for r in rows if r["primary_target"] in ["BBF-14","BetV1"] and r["primary_binding"] in ["0","1"]]
inventory=[];extracted=[]
with zipfile.ZipFile(archive) as z:
 for n in z.namelist():
  if not n.endswith(".pdb"):continue
  inventory.append(n);name=Path(n).name
  # Keep all small deposited design models as evidence in this run, never overwrite source archive.
  dest=run.path/"work"/(hashlib.sha256(n.encode()).hexdigest()[:10]+"_"+name)
  dest.write_bytes(z.read(n));extracted.append((n,dest))
out=[]
for r in selected:
 matches=[]
 for name,path in extracted:
  try:cs,ctx=read_structure(path)
  except Exception:continue
  binder=[c for c in cs if c["sequence"]==r["sequence"]]
  if len(binder)==1:
   target=[c for c in cs if c is not binder[0]]
   if len(target)==1 and not ctx:matches.append((name,path,target[0],binder[0]))
 item=dict(id=r["primary_name"],target=r["primary_target"],label=r["primary_binding"],sequence=r["sequence"],primary_label_verified=True,structure_matches=len(matches),assay_construct_match="CORE_SEQUENCE_VERIFIED_TAG_AND_FULL_ASSAY_CONSTRUCT_PENDING",status="STRUCTURE_UNRESOLVED")
 if len(matches)==1:
  name,path,t,b=matches[0];norm=run.path/"outputs"/(hashlib.sha256(r["primary_name"].encode()).hexdigest()[:12]+".pdb");write_pdb(norm,[t,b])
  item.update(status="AUTHOR_MODEL_EXACT_BINDER_CORE",target_sequence=t["sequence"],backbone=record_file(norm),archive_member=name,source_model=record_file(path))
 out.append(item)
atomic_json(run.path/"outputs/controls.json",out);run.output("controls",run.path/"outputs/controls.json")
atomic_json(run.path/"outputs/label_audit.json",dict(primary_counts=dict(collections.Counter(r["primary_binding"] for r in rows)),cross=[dict(primary=k[0],secondary=k[1],expression=k[2],n=v) for k,v in cross.items()],selection="All explicitly measured BBF-14 and BetV1 rows; no score-based selection",n=len(out)))
run.output("label_audit",run.path/"outputs/label_audit.json")
print("CONTROLS",[(x["target"],x["id"],x["label"],x["structure_matches"]) for x in out],flush=True)
print("ARCHIVE_EXAMPLES",inventory[:15],flush=True)
print(run.finish("PRIMARY_CONTROL_EXTENSION_AUDITED","published_binding_not_blockade"),flush=True)
