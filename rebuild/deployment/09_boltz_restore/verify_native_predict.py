import json, os, sys
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from ppiblocker.common import read_json,load_run,record_file,atomic_json,require,verify_file
from ppiblocker.structure import read_structure,superpose,interface
R=Path("/lustre/users/u21111210118/projects/test9");O=R/"steps/09_boltz_restore/outputs";job=sys.argv[1]
cli=read_json(O/f"native_predict_result_{job}.json")
manifest=Path(cli["manifest"])
m=load_run(manifest,{"POSE_ACCEPTED","POSE_REJECTED","PREDICTION_INCOMPLETE"})
prep_receipt=read_json(O/"native_predict_prepare_receipt.json")
prep=load_run(prep_receipt["prepare_manifest"]["path"],{"NEEDS_PREDICTION"})
require(m["inputs"][0]==prep_receipt["prepare_manifest"],"PREDICT_INPUT_MISMATCH","Wrong sequence input")
require(m["execution"]["slurm_job_id"]==job,"PREDICT_JOB_MISMATCH",job)
require(m["runtime_validation"]=="live_capture_matches_reviewed_lock_v2","RUNTIME_NOT_VERIFIED","Missing lock validation")
retrieval=read_json(prep["outputs"]["retrieval"]["path"])
require(retrieval["search_performed"] is False and retrieval["experimental_coordinates_accessed"] is False,"REFERENCE_LEAKAGE","Prediction preparation accessed coordinates")
cfg=read_json(prep["outputs"]["config"]["path"])
require(cfg["structure"]=={"mode":"predict_only"},"REFERENCE_LEAKAGE","Unexpected structure options")
reference=load_run(prep_receipt["withheld_reference_manifest"]["path"],{"POSE_ACCEPTED"})
require(cfg["gates"]==read_json(reference["outputs"]["config"]["path"])["gates"],"GATES_CHANGED","Withheld benchmark changed gates")
native,_=read_structure(verify_file(prep_receipt["withheld_reference_structure"]))
proteins=read_json(prep["outputs"]["proteins"]["path"])
ensemble=read_json(m["outputs"]["ensemble"]["path"])
native_contacts={tuple(p) for p in interface(*native,cutoff=cfg["gates"]["contact_cutoff"])["residue_pairs"]}
comparisons=[]
ca=lambda chain:np.asarray([res["ca"] for res in chain["residues"]])
for i,row in enumerate(ensemble["models"]):
 p=verify_file(m["outputs"][f"model_{i}_structure"])
 require(p.is_relative_to(manifest.parent),"STALE_PREDICTION_PATH",str(p))
 chains,_=read_structure(p)
 require([c["sequence"] for c in chains]==[x["sequence"] for x in proteins],"PREDICTION_SEQUENCE_MISMATCH",str(p))
 require([c["sequence"] for c in chains]==[c["sequence"] for c in native],"REFERENCE_CONSTRUCT_MISMATCH","Withheld reference must match construct exactly")
 rotation,translation,target_rmsd=superpose(ca(chains[0]),ca(native[0]))
 partner_rmsd=float(np.sqrt(np.mean(np.sum((ca(chains[1])@rotation+translation-ca(native[1]))**2,axis=1))))
 predicted_contacts={tuple(p) for p in interface(*chains,cutoff=cfg["gates"]["contact_cutoff"])["residue_pairs"]}
 comparisons.append({"model_index":i,"structure":record_file(p),"sequence_identity_exact":True,"target_ca_rmsd_angstrom":target_rmsd,"partner_ca_rmsd_after_target_alignment_angstrom":partner_rmsd,"native_contact_recall_at_5A":len(native_contacts & predicted_contacts)/len(native_contacts),"native_contact_count":len(native_contacts),"predicted_contact_count":len(predicted_contacts),"prediction_metrics":row.get("metrics"),"prediction_reasons":row.get("reasons"),"model_status":row.get("status","EVALUATED")})
complete=m["status"] in {"POSE_ACCEPTED","POSE_REJECTED"} and len(comparisons)==cfg["prediction"]["samples"]==3 and not any(x["model_status"]!="EVALUATED" for x in comparisons)
receipt={"status":"BOLTZ_NATIVE_PREDICT_ENGINEERING_ACCEPTED" if complete else "BOLTZ_NATIVE_PREDICT_INCOMPLETE","accepted_utc":datetime.now(timezone.utc).isoformat(),"cpu_audit_job_id":os.environ["SLURM_JOB_ID"],"gpu_job_id":job,"prediction_manifest":record_file(manifest),"prepare_manifest":record_file(prep_receipt["prepare_manifest"]["path"]),"withheld_reference_manifest":prep_receipt["withheld_reference_manifest"],"manifest_files_verified":len(m.get("file_inventory",[])),"prediction_status":m["status"],"convergent_model_indices":ensemble["convergent_model_indices"],"comparison":comparisons,"evidence_boundary":{"engineering_acceptance":complete,"single_known_interaction_smoke":True,"training_overlap":"unknown","reference_input_to_model":False,"external_msa_used":False,"thresholds_changed":False,"generalization_or_workflow_superiority_established":False,"experimental_blockade":False}}
atomic_json(O/f"native_predict_acceptance_{job}.json",receipt)
print(json.dumps(receipt,indent=2),flush=True)
require(complete,"NATIVE_PREDICT_INCOMPLETE","Inspect manifest and failure records")
