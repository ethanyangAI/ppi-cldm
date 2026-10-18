import json,os,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
def brief(x):
 if isinstance(x,dict): return {k:("list:"+str(len(v)) if isinstance(v,list) else "dict:"+",".join(v) if isinstance(v,dict) else v) for k,v in x.items()}
 return {"type":type(x).__name__}
p=R/"steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125"
for n in ("score.json","acceptance.json","worker_audit.json","raw.json","score_acceptance.json"):
 x=json.loads((p/n).read_text()); print(n,json.dumps(brief(x),ensure_ascii=False)); 
 if n=="worker_audit.json":
  for k,v in x.items():
   if isinstance(v,list) and v:print("FIRST",k,json.dumps(brief(v[0]),ensure_ascii=False))
plan=json.loads((R/"steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061/plan.json").read_text())
print("PLAN",json.dumps(brief(plan),ensure_ascii=False))
print("INPUTS",json.dumps(plan["inputs"],ensure_ascii=False))
print("CONTROL",json.dumps(plan["controls"][0],ensure_ascii=False))
print("JOB",json.dumps(plan["jobs"][0],ensure_ascii=False))
a=json.loads((p/"worker_audit.json").read_text())
for key in ("models","jobs","checked","workers"):
 if key in a and a[key]:print("AUDIT_DETAIL",json.dumps(a[key][0],ensure_ascii=False)[:10000])
print("qual files",list(str(v) for v in (R/"steps/14_control_qualification").glob("**/*overlay*.json")))

