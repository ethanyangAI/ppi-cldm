import shutil
from util import *
platform_name=sys.argv[2] if len(sys.argv)>2 else "CPU"
if platform_name!="CPU":
 from ppiblocker.backends import require_gpu
 require_gpu()
slot=int(sys.argv[1]);name=("dev_14_bb145_seq0","dev_15_bb1144_seq1","native")[slot//3];seed=(3142,3143,3144)[slot%3]
run=Run(R,"85_strengthening_md",[record_file(SETUP),record_file(S/"protocol.json")]);shutil.copy2(__file__,run.path/"qc/driver.py");shutil.copy2(S/"md_worker.py",run.path/"qc/worker.py")
try:
 if name=="native":raw=verify_file(baseplan()["candidates"][0]["native"])
 else:
  found=[]
  for p in (R/"steps/75_af2_review_score/runs").glob("*/manifest.json"):
   m=read_json(p)
   if m["status"]=="AF2_REVIEW_SCORED" and m.get("entry_id")==name:found.append((p,m))
  require(len(found)==1,"MD_INPUT",name);p,m=found[0];data=read_json(verify_file(m["outputs"]["results"]))
  z=next(z for z in data["models"] if z["arm"]=="expanded" and z["weight"]==1 and z["seed"]==1042)
  raw=verify_file(z["relaxed_structure"]);run.manifest["inputs"].append(record_file(p))
 run.manifest.update(entry_id=name,seed=seed,platform=platform_name);run.manifest["inputs"].append(record_file(raw));run.save()
 case=run.path/"work/md"
 checked_command([R/"env/bindcraft/bin/python",S/"md_worker.py",raw,case,str(seed),platform_name],run.path/"work",run.path/"logs/md.log",env(platform_name!="CPU"),timeout=int(os.environ.get("PPI_MD_TIMEOUT_SECONDS","43200")))
 data=read_json(case/"result.json");require(len(data["trace"])==100,"MD_INCOMPLETE",str(len(data["trace"])))
 run.output("results",case/"result.json");run.output("trajectory",case/"trajectory.dcd");run.output("final",case/"final.pdb")
 print(run.finish("MD_DIAGNOSTIC_COMPLETE","computational_only"),flush=True)
except Exception as x:run.fail(x);raise

