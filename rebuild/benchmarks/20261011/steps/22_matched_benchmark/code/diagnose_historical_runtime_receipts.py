import json,os,hashlib,subprocess,re
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");j=os.environ["SLURM_JOB_ID"]
sched=subprocess.check_output(["scontrol","show","job",j,"-o"],text=True)
assert "JobState=RUNNING"in sched and not re.search(r"gres/gpu[^=]*=[1-9]",re.search(r"(?:AllocTRES|TRES)=(\\S+)",sched)[1])
seen=set();out=[]
def walk(o,ctx):
 if isinstance(o,dict):
  if {"path","bytes","sha256"}<=set(o):
   p=Path(o["path"]);key=(str(p),o["sha256"])
   if p.name=="benchmark_runtime.py":
    actual=hashlib.sha256(p.read_bytes()).hexdigest()if p.is_file()else None
    if actual!=o["sha256"]:out.append(dict(expected=o,current_sha256=actual,context=ctx))
   if key not in seen and p.suffix==".json"and p.is_file()and p.stat().st_size<4000000:
    seen.add(key);walk(json.loads(p.read_text()),ctx+[str(p)])
  else:
   for k,v in o.items():walk(v,ctx+[k])
 elif isinstance(o,list):
  for i,v in enumerate(o):walk(v,ctx+[str(i)])
p=R/"steps/22_matched_benchmark/engineering_pilot/plan_v3/frozen_plan.json"
walk(json.loads(p.read_text()),[str(p)])
dest=R/"steps/22_matched_benchmark/code"/("historical_source_context_"+j+".json")
dest.write_text(json.dumps(dict(cpu_job=j,scheduler=sched,mutable_runtime_mismatches=out),indent=2)+"\\n")
print(dest);print(json.dumps(out,indent=2))
