import sys,shutil
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,require
from ppiblocker.pipeline import evaluate
root=Path("/lustre/users/u21111210118/projects/test9");idx=int(sys.argv[1])
matches=[]
for p in (root/"steps/33_generation_development/runs").glob("*/manifest.json"):
 m=read_json(p)
 if m.get("cell_index")==idx and m["status"]=="DEVELOPMENT_POOL_GENERATED":matches.append((p,m))
require(len(matches)==1,"GENERATION_CELL_NOT_UNIQUE",str([(str(p),m["status"]) for p,m in matches]))
p,m=matches[0];design=verify_file(m["design_manifest"])
run=Run(root,"43_development_refold",[record_file(p),record_file(design)])
shutil.copy2(__file__,run.path/"qc/driver.py")
run.manifest.update(cell_index=idx,case=m["case"],condition=m["condition"],seed=m["seed"],analysis_role="DEVELOPMENT",gate_version="legacy_engineering_gates_uncalibrated");run.save()
try:
 result=evaluate(root,design)
 run.output("evaluation_manifest",result)
 status=read_json(result)["status"]
 print(run.finish("DEVELOPMENT_REFOLD_COMPLETE" if status=="EVALUATION_COMPLETE" else "DEVELOPMENT_REFOLD_INCOMPLETE","computational_only",dict(upstream_status=status)),flush=True)
except Exception as e:run.fail(e);raise
