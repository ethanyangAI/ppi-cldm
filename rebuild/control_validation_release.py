"""Technical validation release; correct an earlier timestamp claim without altering frozen inference."""
import os,sys,json,hashlib,re
from pathlib import Path
import numpy as np
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/17_control_calibration";sys.path.insert(0,str(R/"source/rebuild"))
from control_review_v2 import rec,verify,dump,config_valid
from control_msa_check import verify_roundtrip
from control_score_v2 import test
test()
p=S/"plan_v2.json";plan=json.loads(p.read_text());preflight=json.loads(verify(plan["preflight"]).read_text());assert len(preflight["entries"])==78 and preflight["insertion_mutation_rejected"]
for row in plan["code"]:verify(row)
m=json.loads((S/"inputs/msa_acceptance_v2.json").read_text());verify(m["plan"])
checks=[]
for slot in (0,1):
 e=plan["conditions"][slot];mp=S/"runs/array_11941"/("task_"+str(slot))/"manifest.json";manifest=json.loads(mp.read_text());assert manifest["status"]=="PREDICTIONS_GENERATED_PENDING_CPU_ACCEPTANCE"
 for item in manifest["inputs"]:verify(item)
 out=Path(manifest["output_directory"]);cfg=json.loads((out/"config.json").read_text());config_valid(cfg)
 inp=next(x for x in m["conditions"] if x["condition_id"]==e["condition_id"])
 semantic=verify_roundtrip(verify(inp["input"]),out/(e["condition_id"]+".a3m"),e["target_sequence"],e["sequence"])
 ids=set()
 for pdb in out.glob("*_unrelaxed_rank_*.pdb"):
  match=re.search(r"_model_(\d+)_seed_(\d+)\.pdb$",pdb.name);model,seed=map(int,match.groups());ids.add((model,seed))
  st=PDBParser(QUIET=True).get_structure("x",pdb);chains=list(next(st.get_models()));assert [c.id for c in chains]==["A","B"]
  seqs=["".join(seq1(r.resname) for r in c if r.id[0]==" " and "CA" in r) for c in chains];assert seqs==[e["target_sequence"],e["sequence"]]
  assert all(np.isfinite(a.coord).all() for a in st.get_atoms())
  scores=json.loads(pdb.with_name(pdb.name.replace("_unrelaxed_","_scores_").replace(".pdb",".json")).read_text());n=sum(map(len,seqs))
  pae=np.asarray(scores["pae"]);plddt=np.asarray(scores["plddt"])
  assert pae.shape==(n,n) and plddt.shape==(n,) and np.isfinite(pae).all() and np.isfinite(plddt).all()
 assert ids=={(a,b) for a in range(1,6) for b in (1042,1043,1044)}
 checks.append({"slot":slot,"models":len(ids),"manifest":rec(mp),"started_utc":manifest["started_utc"],"finished_utc":manifest["finished_utc"],"msa_feature_status":semantic["status"]})
correction={"status":"V2_TECHNICAL_VALIDATION_RELEASED_AFTER_INITIAL_30_MODELS_NO_PROTOCOL_CHANGE","job":os.environ["SLURM_JOB_ID"],"inference_plan":rec(S/"plan.json"),"validation_plan":rec(p),"validation_msa":rec(S/"inputs/msa_acceptance_v2.json"),"semantic_preflight":plan["preflight"],"source_snapshot":[rec(R/"source/rebuild"/n) for n in ("control_review.py","control_score.py","control_run.sh","control_review_v2.py","control_score_v2.py","control_msa_check.py","control_validation_release.py")],"technical_preflight_models":checks,"metadata_correction":{"superseded_text":"REFROZEN_BEFORE_ANY_GPU_INFERENCE and Before any GPU inference in job11969/plan_v2","corrected_statement":"Original inference plan and code frozen by CPU11939 before any GPU. Array11941 slots0/1 completed 30 models before validation-only amendment11969. No inference settings, input sequences/MSAs, confidence formula, eligibility or family calibration were changed; no scores were used to choose the validation rule. v2 only replaces invalid byte identity by strictly equivalent parsed MSA features and raw row mapping.","reason":"GPU slots0/1 had already allocated before array hold applied to remaining slots. A cancellation request for CPU11969 arrived after it had successfully finished; retry11971 correctly refused to overwrite immutable preflight and is superseded."},"upstream_jobs":{"original_init":11939,"MSA":11940,"GPU_array":11941,"semantic_preflight":11969,"superseded_retry":11971,"accept_score":11974},"scope":"First30 technical preflight only; final acceptance still requires all1170 models. No biological score selection."}
dump(S/"outputs/validation_release.json",correction,True)
print(json.dumps({"status":correction["status"],"receipt":rec(S/"outputs/validation_release.json"),"models_checked":30},indent=2))

