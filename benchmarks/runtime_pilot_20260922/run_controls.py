import sys,shutil,traceback
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,runtime_provenance
from ppiblocker.backends import boltz_predict,confidence_reasons
from ppiblocker.pipeline import model_pair
from ppiblocker.structure import read_structure,competition
root=Path(sys.argv[1])
controls=root/"steps/17_published_controls/runs/20260922T045641Z_92eb165c93ff/outputs/controls.json"
pose=root/"steps/01_pose/runs/20260920T125044Z_6e90b25258de/manifest.json"
run=Run(root,"20_control_verification",[record_file(controls),record_file(pose)])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 runtime_provenance(run,root,["boltz"])
 up=read_json(pose);native=verify_file(up["outputs"]["native"]);nt,np=read_structure(native)[0]
 cfg=read_json(verify_file(up["outputs"]["config"]))
 results=[]
 for row in read_json(controls):
  try:
   proteins=[dict(sequence=nt["sequence"],canonical_start=325),dict(sequence=row["sequence"],canonical_start=1,de_novo=True)]
   models=boltz_predict(root,run.path/"work"/row["id"],proteins,cfg["refold"],run.path/"logs"/(row["id"]+".log"))
   records=[]
   for model in models:
    a,b,pair,metrics=model_pair(model,proteins,cfg["gates"])
    geometry=competition(nt,np,a,b,a,b);geometry.pop("binder_ca_rmsd_after_target_alignment")
    reasons=confidence_reasons(metrics,cfg["gates"])
    records.append(dict(model=model,metrics=metrics,geometry=geometry,confidence_reasons=reasons,
     binding_proxy_pass=not reasons and pair["interface"]["minimum_distance"]>=1.5,
     competition_geometry_pass=geometry["native_interface_coverage"]>=.5 and geometry["partner_overlap_atom_count_2A"]>=5))
   results.append(dict(id=row["id"],label=row["evidence_label"],models=records,status="COMPLETE"))
  except Exception as e:
   traceback.print_exc();results.append(dict(id=row["id"],label=row["evidence_label"],status="FAILED",error=str(e)))
  atomic_json(run.path/"outputs/results.json",results)
 run.output("results",run.path/"outputs/results.json")
 print(run.finish("CONTROL_VERIFICATION_COMPLETE" if all(r["status"]=="COMPLETE" for r in results) else "CONTROL_VERIFICATION_INCOMPLETE","computational_only",dict(construct_note="Published controls evaluated against benchmark KEAP1 325-609; not an exact reproduction of the published assay construct.")),flush=True)
except Exception as e:run.fail(e);raise

