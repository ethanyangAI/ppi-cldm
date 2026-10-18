import json, os, sys
from pathlib import Path
from datetime import datetime, timezone
from ppiblocker.common import read_json, load_run, record_file, atomic_json, require, verify_file
from ppiblocker.structure import read_structure
R=Path("/lustre/users/u21111210118/projects/test9")
O=R/"steps/09_boltz_restore/outputs"
job=sys.argv[1]
receipt_path=O/f"evaluate_result_{job}.json"
cli=read_json(receipt_path)
manifest=Path(cli["manifest"])
m=load_run(manifest,{"EVALUATION_COMPLETE","EVALUATION_INCOMPLETE"})
upstream=R/"steps/03_design/runs/20261002T114616Z_cfa6d86555db/manifest.json"
design=load_run(upstream,{"DESIGNS_GENERATED"})
require(m["inputs"][0]==record_file(upstream),"SMOKE_PROVENANCE_MISMATCH","Unexpected upstream design")
require(m["execution"]["slurm_job_id"]==job,"SMOKE_JOB_MISMATCH",job)
require(m["runtime_validation"]=="live_capture_matches_reviewed_lock_v2","RUNTIME_NOT_VERIFIED","Missing runtime lock validation")
evaluation=read_json(m["outputs"]["evaluation"]["path"])
candidates=read_json(design["outputs"]["candidates"]["path"])
config=read_json(design["outputs"]["config"]["path"])
require(evaluation["gates"]==config["gates"],"GATES_CHANGED","Original design thresholds changed")
require(len(evaluation["candidates"])==len(candidates)==1,"SMOKE_SCOPE_MISMATCH","Expected one candidate")
checks=[]; summaries=[]
for row,candidate in zip(evaluation["candidates"],candidates):
 require((row["id"],row["sequence"])==(candidate["id"],candidate["sequence"]),"SMOKE_CANDIDATE_MISMATCH","Sequence differs")
 models=row.get("models",[])
 for i,model in enumerate(models):
  key=f"{row['id']}_{i}_structure"
  p=verify_file(m["outputs"][key])
  require(p.is_relative_to(manifest.parent),"STALE_PREDICTION_PATH",str(p))
  chains,_=read_structure(p)
  seqs=[x["sequence"] for x in chains]
  require(seqs==[candidate["target_sequence"],candidate["sequence"]],"PREDICTION_SEQUENCE_MISMATCH",str(p))
  checks.append({"model_index":i,"structure":record_file(p),"exact_target_and_binder_sequences":True})
  summaries.append({"candidate_id":row["id"],"model_index":i,"metrics":model.get("metrics"),"geometry":model.get("geometry"),"reasons":model.get("reasons"),"model_status":model.get("status","EVALUATED")})
 complete=(m["status"]=="EVALUATION_COMPLETE" and len(models)==config["refold"]["samples"]==3 and row.get("evaluation_failed_samples")==0)
 receipt={"status":"BOLTZ_GPU_EVALUATION_ACCEPTED" if complete else "BOLTZ_GPU_EVALUATION_INCOMPLETE","accepted_utc":datetime.now(timezone.utc).isoformat(),"cpu_audit_job_id":os.environ["SLURM_JOB_ID"],"gpu_job_id":job,"gpu_result":record_file(receipt_path),"evaluation_manifest":record_file(manifest),"upstream_design_manifest":record_file(upstream),"runtime_registration":record_file(O/"runtime_lock_registration.json"),"manifest_files_verified":len(m.get("file_inventory",[])),"structure_sequence_checks":checks,"candidate_status":row["status"],"passing_samples":row.get("passing_samples"),"requested_samples":row.get("requested_samples"),"model_summaries":summaries,"scope":{"new_candidates":1,"blind_refold_samples":3,"msas":"single_sequence_explicit_opt_in","fresh_prediction_only":True},"evidence_boundary":{"engineering_acceptance":complete,"computational_competition_candidate":row["status"]=="COMPUTATIONAL_COMPETITION_CANDIDATE","thresholds_calibrated":False,"experimental_binding":False,"experimental_blockade":False,"workflow_superiority_established":False}}
 atomic_json(O/f"gpu_evaluation_acceptance_{job}.json",receipt)
 print(json.dumps(receipt,indent=2),flush=True)
 require(complete,"GPU_EVALUATION_INCOMPLETE","Inspect receipt and run failure records")
