import shutil,time
from util import *
bp=baseplan();entries=bp["all_controls"]+bp["candidates"];slot=int(sys.argv[1])
if slot>=len(entries):
 _,ext=one("82_strengthening_extensions","EXTENSION_INPUTS_READY");entries += [e for e in read_json(verify_file(ext["outputs"]["plan"]))["entries"] if e["kind"]!="monomer"]
e=entries[slot] if slot<113 else read_json(verify_file(one("89_strengthening_positive_control","HOMOLOG_POSITIVE_CONTROL_READY")[1]["outputs"]["entry"]))
run=Run(R,"84_strengthening_physics",[record_file(SETUP),record_file(S/"protocol.json")]);shutil.copy2(__file__,run.path/"qc/driver.py");shutil.copy2(S/"physics_worker.py",run.path/"qc/worker.py")
try:
 deadline=time.monotonic()+5400
 while True:
  found=[]
  for stage in ("74_af2_review_predict","80_strengthening_predict","83_strengthening_extension_predict"):
   for p in (R/"steps"/stage/"runs").glob("*/manifest.json"):
    m=read_json(p)
    if m["status"] in ("AF2_REVIEW_PREDICTION_COMPLETE","EXTENSION_PREDICTION_COMPLETE") and m.get("entry_id")==e["id"]:found.append((p,m))
  if found or time.monotonic()>=deadline:break
  time.sleep(30)
 require(len(found)==1,"PREDICTION_UNIQUE",e["id"]);p,m=found[0];pred=read_json(verify_file(m["outputs"].get("predictions",m["outputs"].get("results"))))
 z=next(z for z in pred.get("expanded",pred.get("models")) if z["weight"]==1 and z["seed"]==1042);raw=verify_file(z["pdb"])
 run.manifest.update(inputs=run.manifest["inputs"]+[record_file(p)],entry_id=e["id"]);run.save()
 rows=[]
 for seed in (2142,2143,2144):
  case=run.path/"work"/str(seed)
  checked_command([R/"env/bindcraft/bin/python",S/"physics_worker.py",raw,case,str(seed)],run.path/"work",run.path/"logs"/f"{seed}.log",env(),timeout=1800)
  v=read_json(case/"result.json");v["relaxed_pdb"]=record_file(v["relaxed_pdb"]);cs=chains(verify_file(v["relaxed_pdb"]))
  require([c["sequence"] for c in cs]==[e["target_sequence"],e["sequence"]],"SEQUENCE_CHANGED","physics")
  rows.append(v)
 atomic_json(run.path/"outputs/results.json",dict(entry=e,models=rows));run.output("results",run.path/"outputs/results.json")
 print(run.finish("PHYSICS_COMPLETE","computational_only"),flush=True)
except Exception as x:run.fail(x);raise

