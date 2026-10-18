import os,json,time,hashlib
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/08_candidate_refolds";A=R/"steps/03_af2_restore"
def rec(p):
 b=p.read_bytes();return {"path":str(p),"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
ready=json.loads((A/"manifest.json").read_text());assert ready["status"]=="AF2_RUNTIME_ASSETS_AND_INPUTS_READY"
mr=json.loads((A/"target_msa/receipt.json").read_text())
entries=[]
for mode in ("complex","monomer"):
 for e in mr["entries"]:
  slot=len(entries);p=Path(e["msa"]["path"]) if mode=="complex" else S/"inputs"/(e["id"]+"_monomer.fasta")
  if mode=="monomer":p.write_text(">"+e["id"]+"_monomer\n"+e["sequence"]+"\n")
  entries.append({"slot":slot,"id":e["id"],"mode":mode,"input":rec(p),"target_sequence":e["target_sequence"] if mode=="complex" else "","sequence":e["sequence"],"model_type":"alphafold2_multimer_v3" if mode=="complex" else "alphafold2_ptm"})
plan={"status":"FROZEN_NEW_AF2_RECOVERY_PLAN","timestamp":time.time(),"job_id":os.environ.get("SLURM_JOB_ID"),"runtime_acceptance":rec(A/"manifest.json"),"runtime_environment":rec(A/"inference_env.sh"),"target_msa_receipt":rec(A/"target_msa/receipt.json"),"entries":entries,"protocol":{"model_order":[1,2,3,4,5],"seeds":[1042,1043,1044],"num_recycle":12,"recycle_early_stop_tolerance":0.5,"max_msa":"128:256","templates":False,"num_relax":0},"coordinate_provenance":"NEW_PREDICTIONS_NOT_RESTORED_OLD_COORDINATES","limitations":["Historic targetMSA snapshot and generated design backbones unavailable.","No old-design poseRMSD can be computed from missing reference structures.","The regenerated targetMSA is frozen with a new checksum."]}
(S/"plan.json").write_text(json.dumps(plan,indent=2)+"\n");print(json.dumps(plan,indent=2),flush=True)
