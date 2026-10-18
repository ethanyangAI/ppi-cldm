import sys,shutil,traceback
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,runtime_provenance,require
from ppiblocker.backends import boltz_predict,confidence_reasons
from ppiblocker.pipeline import model_pair,attach_models
from ppiblocker.structure import read_structure,competition
root=Path("/lustre/users/u21111210118/projects/test9");idx=int(sys.argv[1])
controls=root/"steps/41_control_constructs/runs/20260922T101321Z_2f8f58bad35d/outputs/controls.json"
rows=read_json(controls)[idx*10:(idx+1)*10];require(len(rows)==10,"CONTROL_BATCH_SIZE",str(idx))
settings=dict(samples=3,recycles=3,sampling_steps=200,seed=1042,allow_single_sequence=True,allow_external_msa=False)
run=Run(root,"45_local_calibration",[record_file(controls)])
shutil.copy2(__file__,run.path/"qc/driver.py")
run.manifest.update(batch_index=idx,endpoint="author_binary_binding_label",assay_identity="pending_primary_adjudication",threshold_promotion_permitted=False,protocol=settings);run.save()
try:
 runtime_provenance(run,root,["boltz"])
 results=[]
 for row in rows:
  try:
   require(row["status"]=="AUTHOR_INPUT_SEQUENCE_MATCH","CONTROL_IDENTITY",row["binder_id"])
   source=verify_file(row["archive_matches"][0]);cs,context=read_structure(source)
   target=next(c for c in cs if c["sequence"]==row["B_seq"])
   binder=next(c for c in cs if c["sequence"]==row["A_seq"])
   proteins=[dict(sequence=row["B_seq"],canonical_start=1),dict(sequence=row["A_seq"],canonical_start=1,de_novo=True)]
   models=boltz_predict(root,run.path/"work"/row["binder_id"],proteins,settings,run.path/"logs"/(row["binder_id"]+".log"))
   records=[];attach_models(run,row["binder_id"],models)
   for model in models:
    a,b,pair,metrics=model_pair(model,proteins,{})
    geometry=competition(target,binder,target,binder,a,b)
    records.append(dict(model=model,metrics=metrics,geometry=geometry,legacy_confidence_reasons=confidence_reasons(metrics,{})))
   results.append(dict(id=row["binder_id"],target=row["target_id"],label=row["binder"],status="COMPLETE",models=records,
    assay_construct_match=row["assay_construct_match"],author_input_structure=record_file(source)))
  except Exception as e:
   traceback.print_exc();results.append(dict(id=row["binder_id"],status="FAILED",error=str(e)))
  atomic_json(run.path/"outputs/results.json",results);run.output("results",run.path/"outputs/results.json")
 print(run.finish("LOCAL_CONTROL_INFERENCE_COMPLETE" if all(x["status"]=="COMPLETE" for x in results) else "LOCAL_CONTROL_INFERENCE_INCOMPLETE","calibration_inputs_not_validated_probabilities",dict(completed=sum(x["status"]=="COMPLETE" for x in results))),flush=True)
except Exception as e:run.fail(e);raise
