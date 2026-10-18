import json,shutil
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,atomic_json,verify_file
root=Path("/lustre/users/u21111210118/projects/test9")
p=root/"steps/35_new_target_qualification/runs/20260922T100212Z_38e35f1ec856/outputs/qualification.json"
run=Run(root,"37_construct_review",[record_file(p)])
shutil.copy2(__file__,run.path/"qc/driver.py")
rows=[]
for c in read_json(p)["cases"]:
 good=[]
 for x in c.get("structural_candidates",[]):
  if x["reasons"]:continue
  changes=[]
  for i,(a,b) in enumerate(x["construct_bounds"]):
   seq=c["proteins"][i]["sequence"][a-1:b];obs=x["sequences"][i]
   changes.append(dict(accession=c["proteins"][i]["id"],bounds=[a,b],canonical_sequence=seq,observed_sequence=obs,exact=seq==obs))
  good.append(dict(pdb=x["pdb"],assembly=x["assembly"],chains=x["chains"],source=x["source"],identities=changes,
      all_exact=all(v["exact"] for v in changes),context=x["context"],identity=x["identity"]))
 rows.append(dict(id=c["case_id"],pair=c["target"]+"-"+c["partner"],status=c["status"],errors=c["errors"],candidates=good))
atomic_json(run.path/"outputs/constructs.json",rows);run.output("constructs",run.path/"outputs/constructs.json")
print(run.finish("CONSTRUCT_IDENTITY_REVIEW_COMPLETE","qualification_not_context_approval"),flush=True)
for r in rows:print(json.dumps(r),flush=True)

