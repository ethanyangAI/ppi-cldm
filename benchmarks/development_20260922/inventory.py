import csv,collections,json,shutil
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json
root=Path("/lustre/users/u21111210118/projects/test9")
source=root/"steps/31_calibration_sources/runs/20260922T095613Z_38be86bf866a/manifest.json"
run=Run(root,"32_calibration_inventory",[record_file(source)])
shutil.copy2(__file__,run.path/"qc/driver.py")
m=read_json(source)
p=verify_file(m["outputs"]["feature_table"])
with p.open() as f:
 rd=csv.DictReader(f);cols=rd.fieldnames
 rows=list(rd)
summary=dict(rows=len(rows),columns=cols,group_columns={},examples=[])
for k in cols:
 if k.lower() in ["binder_id","target_id","binder","source","sequence","target_sequence","binder_sequence","target","binding","kd"] or any(s in k.lower() for s in ["sequence","construct"]):
  if "sequence" in k.lower():summary["group_columns"][k]=dict(nonempty=sum(bool(r[k]) for r in rows),example=rows[0][k][:300])
  elif k!="binder_id":summary["group_columns"][k]=dict(collections.Counter(r[k] for r in rows))
summary["examples"]=[{k:r[k] for k in cols if k in ["binder_id","target_id","binder","source"]} for r in rows[:6]]
atomic_json(run.path/"outputs/schema.json",summary);run.output("schema",run.path/"outputs/schema.json")
public={}
for key in ["meta_dataset","bindcraft_models","bindcraft_tree","scoring_tree","rfd3_tree","bindcraft_paper"]:
 obj=read_json(verify_file(m["outputs"][key]))
 if "files" in obj:public[key]=[dict(name=f["key"],bytes=f["size"],checksum=f["checksum"],url=f["links"]["self"]) for f in obj["files"]]
 elif "tree" in obj:public[key]=dict(sha=obj.get("sha"),paths=[x["path"] for x in obj["tree"] if x["type"]=="blob" and (x["path"].endswith((".csv",".tsv",".json",".yaml",".yml",".md",".txt")) or "install" in x["path"])])
 else:public[key]=obj
atomic_json(run.path/"outputs/public_inventory.json",public);run.output("public_inventory",run.path/"outputs/public_inventory.json")
old=root/"steps/12_extended_qualification/runs/20260922T040335Z_5b613065df6e/outputs/qualification.json"
candidates=[]
for c in read_json(old)["cases"]:
 cc=[dict(pdb=x["pdb"],assembly=x["assembly"],chains=x["chains"],bounds=x["construct_bounds"],reasons=x["reasons"],context=x["context"][:8]) for x in c["structural_candidates"]]
 candidates.append(dict(id=c["case_id"],pair=c["target"]+"-"+c["partner"],candidate_count=len(cc),reason_counts=dict(collections.Counter(r for x in cc for r in x["reasons"])),best=sorted(cc,key=lambda x:len(x["reasons"]))[:4]))
atomic_json(run.path/"outputs/qualification_gaps.json",candidates);run.output("qualification_gaps",run.path/"outputs/qualification_gaps.json")
print(run.finish("CALIBRATION_SCHEMA_INVENTORIED","metadata_only"),flush=True)
print(json.dumps({k:v for k,v in summary.items() if k!="columns"},ensure_ascii=False),flush=True)
print("COLUMNS",json.dumps(cols),flush=True)
print("PUBLIC",json.dumps(public),flush=True)

