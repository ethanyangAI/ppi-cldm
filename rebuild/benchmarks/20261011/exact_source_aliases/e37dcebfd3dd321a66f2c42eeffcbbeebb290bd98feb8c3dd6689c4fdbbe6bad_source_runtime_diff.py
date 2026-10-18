#!/usr/bin/env python3
import os,sys,json,hashlib,subprocess,traceback,shutil
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
OUT=R/"steps/24_benchmark_delivery/runs"/("runtime_drift_diagnostic_"+os.environ["SLURM_JOB_ID"])
OUT.mkdir(parents=True,exist_ok=False)
def rec(p):
 p=Path(p).resolve(); h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return {"path":str(p),"sha256":h.hexdigest(),"bytes":p.stat().st_size}
def save(n,x):
 p=OUT/n;p.write_text(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+"\n");return rec(p)
def diff(a,b,p="$"):
 if type(a)!=type(b):return [{"path":p,"expected":a,"actual":b}]
 if isinstance(a,dict):
  z=[]
  for k in sorted(set(a)|set(b)):
   if k not in a or k not in b:z.append({"path":p+"."+k,"expected":a.get(k),"actual":b.get(k),"missing_expected":k not in a,"missing_actual":k not in b})
   else:z.extend(diff(a[k],b[k],p+"."+k))
  return z
 if isinstance(a,list):
  if a==b:return []
  return [{"path":p,"expected":a,"actual":b}]
 return [] if a==b else [{"path":p,"expected":a,"actual":b}]
result={"schema":"runtime-drift-diagnostic.v1","status":"RUNNING","claims":{"runtime_accepted":False,"locks_updated":False,"model_inference_performed":False},"job_id":os.environ["SLURM_JOB_ID"],"components":{}}
try:
 assert os.environ.get("CUDA_VISIBLE_DEVICES")==""
 assert not os.environ.get("SLURM_JOB_GPUS") and not os.environ.get("SLURM_STEP_GPUS")
 sources=[Path(__file__),R/"source/src/ppiblocker/common.py",R/"source/src/ppiblocker/runtime_probe.py"]
 result["operative_sources"]=[rec(p) for p in sources]
 sys.path.insert(0,str(R/"source/src"))
 from ppiblocker.common import collect_runtime,tree_records
 hist={
 "core":(R/"steps/02_predict/runs/20261002T121305Z_be69fbefc530/qc/runtime-lock-core.json","cdc5a1e8814498c185315e4a4543f8f2c468f1615fe09925f915a6c79729a032",2823),
 "boltz":(R/"steps/02_predict/runs/20261002T121305Z_be69fbefc530/qc/runtime-lock-boltz.json","5e0b40950d3746a0b345d6770a26df989c4491e7f302a1cdad313d20a979eb69",38197),
 "rfd":(R/"steps/03_design/runs/20261002T114616Z_cfa6d86555db/qc/runtime-lock-rfd.json","77617214f2c978381ace222e41599a45de410b6bd1ad6fc1b6725994df47c03d",117798)}
 for component in ("core","rfd","boltz"):
  lp=R/"source/environment"/("runtime-lock-"+component+".json")
  hp,sha,n=hist[component];hr=rec(hp);assert hr["sha256"]==sha and hr["bytes"]==n
  expected=json.loads(lp.read_text());historical=json.loads(hp.read_text())
  actual=collect_runtime(R,component)
  ds=diff(expected,actual);hd=diff(historical,expected)
  result["components"][component]={"expected":rec(lp),"historical":hr,"actual_snapshot":save(component+"_actual.json",actual),"expected_snapshot":save(component+"_current_expected.json",expected),"historical_snapshot":save(component+"_historical.json",historical),"actual_vs_current_expected":ds,"historical_vs_current_expected":hd,"live_matches_expected":not ds}
  print(component+" diff_count="+str(len(ds))+" historical_diff_count="+str(len(hd)),flush=True)
 for repo in ("RFdiffusion","ProteinMPNN","dllogger"):
  vp=R/"vendor"/repo
  result.setdefault("vendor_file_inventories",{})[repo]=save("vendor_"+repo+"_files.json",tree_records(vp))
  cmds=[["git","status","--porcelain=v1","--untracked-files=all"],["git","diff","--stat"],["git","rev-parse","HEAD"]]
  values=[]
  for argv in cmds:
   c=subprocess.run(argv,cwd=vp,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=False)
   values.append({"argv":argv,"returncode":c.returncode,"stdout":c.stdout,"stderr":c.stderr})
  result.setdefault("vendor_git_metadata",{})[repo]=values
 result["status"]="DIAGNOSTIC_CAPTURE_COMPLETE_RUNTIME_NOT_ACCEPTED"
 result["runtime_mismatch_components"]=[k for k,v in result["components"].items() if not v["live_matches_expected"]]
 result["operative_source_end"]=[rec(p) for p in sources]
 assert result["operative_source_end"]==result["operative_sources"]
except Exception as e:
 result["status"]="DIAGNOSTIC_TYPED_INCOMPLETE";result["error"]={"type":type(e).__name__,"message":str(e),"traceback":traceback.format_exc()}
 save("diagnostic.json",result);raise
receipt=save("diagnostic.json",result)
print(json.dumps({"diagnostic":receipt,"status":result["status"],"runtime_mismatch_components":result["runtime_mismatch_components"]}),flush=True)
