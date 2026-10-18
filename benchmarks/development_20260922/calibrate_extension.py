import sys,shutil,traceback
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,runtime_provenance,require
from ppiblocker.backends import boltz_predict,confidence_reasons
from ppiblocker.pipeline import model_pair,attach_models
from ppiblocker.structure import read_structure,competition
root=Path("/lustre/users/u21111210118/projects/test9");idx=int(sys.argv[1])
controls=root/"steps/52_control_extension/runs/20260922T103806Z_35c0f36f8467/outputs/controls.json"
protocol=root/"source/benchmarks/development_20260922/calibration_extension_protocol.json"
rows=read_json(controls)[idx*9:(idx+1)*9];require(len(rows)==9,"CONTROL_BATCH_SIZE",str(idx))
settings=read_json(protocol)["inference"]
run=Run(root,"55_extension_calibration",[record_file(controls),record_file(protocol)])
shutil.copy2(__file__,run.path/"qc/driver.py")
run.manifest.update(batch_index=idx,endpoint="primary_binary_binding_label",threshold_promotion_permitted=False,protocol=settings);run.save()
try:
 runtime_provenance(run,root,["boltz"]);results=[]
 for row in rows:
  try:
   require(row["status"]=="AUTHOR_MODEL_EXACT_BINDER_CORE","CONTROL_IDENTITY",row["id"])
   source=verify_file(row["backbone"]);target,binder=read_structure(source)[0]
   proteins=[dict(sequence=row["target_sequence"],canonical_start=1),dict(sequence=row["sequence"],canonical_start=1,de_novo=True)]
   models=boltz_predict(root,run.path/"work"/row["id"],proteins,settings,run.path/"logs"/(row["id"]+".log"))
   records=[];attach_models(run,row["id"],models)
   for model in models:
    a,b,pair,metrics=model_pair(model,proteins,{})
    records.append(dict(model=model,metrics=metrics,geometry=competition(target,binder,target,binder,a,b),legacy_confidence_reasons=confidence_reasons(metrics,{})))
   results.append(dict(id=row["id"],target=row["target"],label=row["label"],status="COMPLETE",models=records,assay_construct_match=row["assay_construct_match"],author_input_structure=record_file(source)))
  except Exception as e:traceback.print_exc();results.append(dict(id=row["id"],status="FAILED",error=str(e)))
  atomic_json(run.path/"outputs/results.json",results);run.output("results",run.path/"outputs/results.json")
 print(run.finish("LOCAL_CONTROL_INFERENCE_COMPLETE" if all(x["status"]=="COMPLETE" for x in results) else "LOCAL_CONTROL_INFERENCE_INCOMPLETE","calibration_inputs_not_validated_probabilities",dict(completed=sum(x["status"]=="COMPLETE" for x in results))),flush=True)
except Exception as e:run.fail(e);raise
