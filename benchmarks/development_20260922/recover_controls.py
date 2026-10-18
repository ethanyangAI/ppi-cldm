import shutil
from pathlib import Path
from ppiblocker.common import *
from ppiblocker.pipeline import model_pair
from ppiblocker.structure import read_structure,competition
from ppiblocker.backends import confidence_reasons
root=Path("/lustre/users/u21111210118/projects/test9")
old=root/"steps/45_local_calibration/runs/20260922T102847Z_5a66ab5e0e81/manifest.json"
controls=root/"steps/41_control_constructs/runs/20260922T101321Z_2f8f58bad35d/outputs/controls.json"
run=Run(root,"66_calibration_recovery",[record_file(old),record_file(controls)])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 outputs=read_json(old)["outputs"];results=[]
 for row in read_json(controls)[:10]:
  cs,_=read_structure(verify_file(row["archive_matches"][0]))
  target=next(c for c in cs if c["sequence"]==row["B_seq"]);binder=next(c for c in cs if c["sequence"]==row["A_seq"])
  proteins=[dict(sequence=row["B_seq"],canonical_start=1),dict(sequence=row["A_seq"],canonical_start=1,de_novo=True)]
  models=[]
  for i in range(3):
   model={k:outputs[f'{row["binder_id"]}_{i}_{k}'] for k in ("structure","confidence","pae")}
   for receipt in model.values():verify_file(receipt)
   a,b,pair,metrics=model_pair(model,proteins,{})
   models.append(dict(model=model,metrics=metrics,geometry=competition(target,binder,target,binder,a,b),legacy_confidence_reasons=confidence_reasons(metrics,{})))
  results.append(dict(id=row["binder_id"],target=row["target_id"],label=row["binder"],status="COMPLETE",models=models,assay_construct_match=row["assay_construct_match"],author_input_structure=row["archive_matches"][0]))
 atomic_json(run.path/"outputs/results.json",results);run.output("results",run.path/"outputs/results.json")
 print(run.finish("LOCAL_CONTROL_INFERENCE_COMPLETE","computational_only",dict(completed=10,gpu_inference_repeated=False)))
except Exception as e:run.fail(e);raise

