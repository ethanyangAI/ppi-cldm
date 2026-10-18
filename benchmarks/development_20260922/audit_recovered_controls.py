from pathlib import Path
import shutil
from ppiblocker.common import *
root=Path("/lustre/users/u21111210118/projects/test9");run=Run(root,"69_repaired_control_audit",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 rows=[];upstream=[];seen=set()
 for step in ("45_local_calibration","55_extension_calibration","66_calibration_recovery"):
  for p in sorted((root/"steps"/step/"runs").glob("*/manifest.json")):
   m=read_json(p)
   if m["status"]!="LOCAL_CONTROL_INFERENCE_COMPLETE":continue
   upstream.append(record_file(p))
   for x in read_json(verify_file(m["outputs"]["results"])):
    key=(x["target"],x["id"]);require(key not in seen,"DUPLICATE_CONTROL",str(key));seen.add(key)
    require(x["status"]=="COMPLETE" and len(x["models"])==3,"INCOMPLETE_CONTROL",str(key))
    for model in x["models"]:
     for k in ("structure","confidence","pae"):verify_file(model["model"][k])
    rows.append(x)
 require(len(rows)==78,"CONTROL_COUNT",str(len(rows)))
 run.manifest["inputs"]=upstream;run.save()
 atomic_json(run.path/"outputs/controls.json",rows);run.output("controls",run.path/"outputs/controls.json")
 text="78/78 controls; 234/234 structure, confidence and PAE triplets verified. Ten controls recovered by CPU postprocessing without repeating inference. Binding labels are not experimental blockade; full assay construct matching remains unresolved. No thresholds promoted.\n"
 p=run.path/"outputs/audit.md";p.write_text(text);run.output("report",p)
 print(run.finish("ALL_78_CONTROL_OUTPUTS_VERIFIED","computational_only",dict(controls=78,models=234)))
except Exception as e:run.fail(e);raise

