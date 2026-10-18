#!/usr/bin/env python3
"""CPU full-content supplemental API audit and explicit BC mixed engineering gate."""
import argparse,hashlib,importlib.util,json,os,subprocess,traceback
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime"
WORKER=S/"frozen/supplemental_bindcraft_13239/bindcraft_supplemental_stage_coverage.py"
CONFIG=S/"runs/supplemental_stage_prepare_13239/outputs/config.json"
CONFIG_SHA="e26c63af40a729a07cc7ce0dc1675babd74589ef43d1eee3cf93a4b30c427970"
BASE=S/"runs/actual_bc_v8_identity_13220/outputs/acceptance.json"
def rec(p):
 p=Path(p);return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():raise FileExistsError(p)
 p.write_text(json.dumps(v,indent=2)+"\n")
def basic_decision(log,index,filters):
 names=[("pLDDT","plddt","ge"),("pTM","ptm","ge"),("i_pTM","i_ptm","ge"),("pAE","pae","le"),("i_pAE","i_pae","le")]
 failures=[]
 for prefix,name,op in names:
  key=str(index)+"_"+prefix;threshold=filters.get(key,{}).get("threshold")
  if threshold is None:continue
  if (op=="ge" and log[name]<threshold) or (op=="le" and log[name]>threshold):failures.append(key)
 return not failures,failures
def check_pool(rows,fixed_positions,physical_sequence):
 assert len(rows)==20 and [r["raw_pool_index"] for r in rows]==list(range(20))
 for row in rows:
  assert len(row["sequence"])==65 and not set(row["sequence"])-set("ACDEFGHIKLMNPQRSTVWY")
  for position,aa in enumerate(row["sequence"],1):
   if aa=="C":assert position in fixed_positions and physical_sequence[position-1]=="C","Newly sampled omitted C observed"
def capture_features(rt,cfg,target,query,observations,out):
 import numpy as np
 import jax,jax.numpy as jnp
 from unittest.mock import patch
 from colabdesign import mk_afdesign_model
 from colabdesign.af.alphafold.common import residue_constants as rc
 adv=json.loads(Path(cfg["advanced"]["path"]).read_text())
 model=mk_afdesign_model(protocol="binder",use_multimer=False,use_initial_guess=False,use_initial_atom_pos=False,num_recycles=adv["num_recycles_validation"],
  data_dir=str(R/"assets/colabfold"),model_names=["model_1_ptm","model_2_ptm"])
 model.prep_inputs(pdb_filename=target["target_pdb"]["path"],chain="A",binder_len=65,rm_target_seq=adv["rm_template_seq_predict"],rm_target_sc=adv["rm_template_sc_predict"],seed=cfg["seed"])
 model._inputs=jax.tree_util.tree_map(lambda x:jnp.asarray(x) if isinstance(x,np.ndarray) else x,model._inputs)
 result=[]
 for observation in observations:
  capture={}
  class Captured(Exception):pass
  def intercept(params,key,inputs):
   for name in ["aatype","msa_feat","template_all_atom_mask","template_all_atom_positions","template_pseudo_beta_mask","template_pseudo_beta"]:
    capture[name]=np.asarray(inputs[name]).copy()
   capture["initial_prev_pos"]=np.asarray(inputs["prev"]["prev_pos"]).copy();raise Captured()
  with patch.object(model._model["runner"],"apply",intercept),jax.disable_jit():
   try:model.predict(seq=query,models=observation["model_indices"],num_recycles=adv["num_recycles_validation"],verbose=False)
   except Captured:pass
  assert capture,"Actual feature call was not intercepted"
  T=int(target["residue_count"]);actual="".join(rc.restypes[int(x)] for x in capture["aatype"])
  assert actual==target["target_sequence"]+query==observation["actual_full_query"]
  assert capture["msa_feat"].shape[0]==1 and np.count_nonzero(capture["initial_prev_pos"])==0
  for name in ["template_all_atom_mask","template_all_atom_positions","template_pseudo_beta_mask","template_pseudo_beta"]:
   value=capture[name];assert value.shape[1]==T+65 and np.count_nonzero(value[:,T:])==0,(name,value.shape)
  assert np.count_nonzero(capture["template_all_atom_mask"][:,:T])>0
  path=out/("actual_query_model_"+str(observation["model_indices"][0]+1)+".npz");np.savez(path,**capture)
  result.append({"model":observation["model_names"],"features":rec(path),"query_sha256":observation["query_sha256"],
   "target_template_enabled":True,"binder_template_channels_all_zero":True,"initial_prev_pos_all_zero":True,
   "single_msa":True,"constructor_matches_actual_supplemental_worker":True,"cpu_intercept_no_AF2_inference":True})
 return result
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--gpu-output",required=True);ap.add_argument("--output-dir",required=True);a=ap.parse_args()
 worker=load("supplemental_worker",WORKER);scheduler=worker.cpu();out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True);gpu=Path(a.gpu_output)
 if not (gpu/"worker_result.json").exists():
  failure=json.loads((gpu/"worker_failure.json").read_text()) if (gpu/"worker_failure.json").exists() else {"status":"SUPPLEMENTAL_CUTOFF_OR_MISSING_TERMINAL"}
  write(out/"typed_incomplete.json",{"status":"SUPPLEMENTAL_STAGE_COVERAGE_INCOMPLETE_NOT_FORMAL_READY","worker_failure":failure,"gpu_output":str(gpu),"source":rec(Path(__file__).resolve()),"scope":worker.SCOPE,"cpu_job":os.environ["SLURM_JOB_ID"]})
  raise RuntimeError("Supplemental actual stage coverage incomplete; preserve partial artifacts; no PASS")
 cfg=json.loads(CONFIG.read_text());assert rec(CONFIG)["sha256"]==CONFIG_SHA
 assert rec(WORKER)==cfg["source"]
 for key in ["source","runtime_source","native_config","environment","gpu_guard","confidence_collector","fixed_pose","target_manifest","pose","advanced","filters","identity_diagnostic"]:worker.check(cfg[key])
 for entry in cfg["official_source_files"]+cfg["python_key_sources"]:worker.check(entry)
 assert rec(BASE)["sha256"]=="9dd2fab2a80caf84548edc0b540ed86f34f6fc3ee1e7a13f22dc66dd93c724f4"
 worker.collect(str(CONFIG),CONFIG_SHA,str(gpu),str(out/"supplemental_base_audit"))
 supplemental=json.loads((out/"supplemental_base_audit/acceptance.json").read_text())
 rt=load("supplemental_runtime",Path(cfg["runtime_source"]["path"]));target=json.loads(Path(cfg["target_manifest"]["path"]).read_text())
 observations=supplemental["actual_native_predictions"];assert len(observations)==2
 pool=json.loads((gpu/"mpnn_pool.json").read_text());chosen=pool["rows"][0]["sequence"]
 fixed=json.loads((gpu/"fixed_pose_interface.json").read_text());allowed_fixed={int(x[1:]) for x in fixed["interface_residues"].split(",") if x}
 check_pool(pool["rows"],allowed_fixed,worker.SEQUENCE)
 basic=json.loads((gpu/"native_basic_results.json").read_text());filters=json.loads(Path(cfg["filters"]["path"]).read_text())
 checks=[]
 for row in observations:
  index=row["model_indices"][0]+1;log=row["native_aux_log"];observed=basic["results"][str(index)]
  passed,failed=basic_decision(log,index,filters)
  assert passed==observed["official_basic_native_pass"]
  stats=observed["statistics"][str(index)]
  for key,logkey in [("pLDDT","plddt"),("pTM","ptm"),("i_pTM","i_ptm"),("pAE","pae"),("i_pAE","i_pae")]:
   assert stats[key]==round(log[logkey],2),(index,key,stats[key],log[logkey])
  assert row["actual_full_query"]==target["target_sequence"]+chosen and int(row["actual_model_rng_seed"])==cfg["seed"]
  checks.append({"model":index,"raw_archives":[row["archive"],row["arrays"],row["raw_pdb"]],"query_sha256":row["query_sha256"],"official_basic_native_pass":passed,"failed_unchanged_default_filters":failed,"native_raw_statistics_rounding_verified":True})
 events=[json.loads(x) for x in (gpu/"supplemental_events.jsonl").read_text().splitlines()]
 assert len([x for x in events if x["stage"]=="official_soluble_mpnn20"])==1
 assert len([x for x in events if x["stage"]=="official_native_complex_ptm1"])==1 and len([x for x in events if x["stage"]=="official_native_complex_ptm2"])==1
 seeded=[x for x in events if x["stage"]=="python_rng_seeded_before_official_constructors"]
 assert len(seeded)==1 and seeded[0]["root_seed"]==cfg["seed"] and seeded[0]["additional_draws"]==0
 python_draws=[x for x in events if x["stage"]=="python_random_randint_observed"]
 mpnn_seeds=[x for x in events if x["stage"]=="actual_mpnn_constructor_key_seed_observed"]
 assert len(mpnn_seeds)==1 and mpnn_seeds[0]["additional_draws"]==0
 assert python_draws and mpnn_seeds[0]["seed"]==python_draws[0]["value"]
 import random
 independent=random.Random(cfg["seed"])
 for draw in python_draws:assert draw["value"]==independent.randint(draw["lower"],draw["upper"])
 assert seeded[0]["completed_at_epoch"]<python_draws[0]["completed_at_epoch"]<=mpnn_seeds[0]["completed_at_epoch"]
 entropy=[x for x in events if x["stage"]=="deterministic_entropy_seed"]
 assert entropy and all(0<=x["seed"]<2**31-1 for x in entropy)
 featureout=out/"features";featureout.mkdir()
 features=capture_features(rt,cfg,target,chosen,observations,featureout)
 parent=gpu.parent;launch=parent/"launcher_budget.txt";assert launch.exists()
 launchdict=dict(line.split("=",1) for line in launch.read_text().splitlines())
 result=json.loads((gpu/"worker_result.json").read_text());gpujob=result["gpu_job"]
 accounting=subprocess.check_output(["sacct","-j",str(gpujob),"-n","-P","--format=JobIDRaw,JobID,State,Start,End,ElapsedRaw,AllocTRES,ExitCode"],text=True)
 write(out/"supplemental_gpu_cost.json",{"status":"ACTUAL_SEPARATE_SUPPLEMENTAL_ALLOCATION_ACCOUNTING_SNAPSHOT","job":gpujob,"actual_allocation":rec(gpu/"gpu_allocation.json"),"sacct":accounting,
  "budget_gpu_seconds":3600,"launcher_budget":rec(launch),"actual_worker":rec(gpu/"worker_result.json"),"scope":worker.SCOPE,
  "interpretation":"Root independently accepts terminal Slurm billing; this cost never enters formal workflow throughput"})
 write(out/"actual_query_features.json",{"status":"ACTUAL_SUPPLEMENTAL_TWO_NATIVE_MODEL_QUERY_FEATURES_CPU_VALIDATED","rows":features,"source":rec(Path(__file__).resolve()),"scope":worker.SCOPE})
 write(out/"native_confidence_and_basic_filters.json",{"status":"TWO_ACTUAL_NATIVE_COMPLEX_MODELS_RAW_CONFIDENCE_BASIC_FILTER_DECISIONS_CPU_RECOMPUTED","checks":checks,"supplemental_audit":rec(out/"supplemental_base_audit/acceptance.json"),"features":rec(out/"actual_query_features.json"),"scope":worker.SCOPE})
 write(out/"soluble_proteinmpnn.json",{"status":"ACTUAL_OFFICIAL_SOLUBLE_MPNN20_COMPLETE_POOL_FIXED_INTERFACE_CPU_VERIFIED","raw_pool":rec(gpu/"mpnn_pool.json"),"ledger":rec(gpu/"supplemental_sequences.jsonl"),"fixed_interface":rec(gpu/"fixed_pose_interface.json"),"raw_pool_count":20,"selected_raw_pool_index":0,"actual_rng_events":rec(gpu/"supplemental_events.jsonl"),"actual_mpnn_key_seed":mpnn_seeds[0]["seed"],"default_calls":rec(CONFIG),"scope":worker.SCOPE,"cost":rec(out/"supplemental_gpu_cost.json")})
 write(out/"deterministic_rng.json",{"status":"ACTUAL_OFFICIAL_PYTHON_KEY_SEEDS_AND_NUMPY_ENTROPY_RECOMPUTED_FROM_PREDECLARED_ROOT_SEED",
 "root_seed":cfg["seed"],"actual_mpnn_constructor":mpnn_seeds,"actual_python_randint_returns":python_draws,"numpy_entropy_events":entropy,
 "events":rec(gpu/"supplemental_events.jsonl"),"official_python_key_sources":cfg["python_key_sources"],"additional_model_rng_draws":0,"scope":worker.SCOPE})
 write(out/"native_filters.json",{"status":"ACTUAL_OFFICIAL_NATIVE_BASIC_AND_FULL_DEFAULT_FILTER_API_COVERAGE_CPU_VERIFIED_NOT_NATIVE_ACCEPTANCE","confidence_and_basic_filters":rec(out/"native_confidence_and_basic_filters.json"),"actual_full_filter_diagnostics":rec(gpu/"supplemental_final_filters.json"),"source":rec(WORKER),"config":rec(CONFIG),"scope":worker.SCOPE,"cost":rec(out/"supplemental_gpu_cost.json")})
 base=json.loads(BASE.read_text());assert base["status"]=="NATIVE_GPU_METHOD_WORKFLOW_STAGE_COVERAGE_INCOMPLETE_ENGINEERING_ONLY"
 assert base["native_stage_status"]["native_bindcraft_trajectory"]=="PASS"
 assert all(base["native_stage_status"][x]=="NOT_COVERED" for x in ["soluble_proteinmpnn","native_af2_ptm1_and_2","native_filters"])
 doc={k:base[k] for k in ["method_id","task_id","plan","runtime_source","orchestrator_source","config_receipt","target_manifest","run_receipt","actual_assigned_gpu_count"]}
 doc.update({"status":"NATIVE_GPU_METHOD_WORKFLOW_CONTENT_ACCEPTED_ENGINEERING_ONLY","scientific_scope":"ENGINEERING_ONLY",
  "coverage_mode":"main_rejected_trajectory_plus_separate_supplemental_stage_coverage","main_workflow_terminal":"SCIENTIFIC_REJECT_BEFORE_MPNN",
  "main_workflow_full_native_chain_completed":False,"main_workflow_sequence_count":0,"supplemental_sequence_count":20,"supplemental_formal_eligible_sequences":0,
  "base_method_audit":rec(BASE),"supplemental_source":rec(WORKER),"supplemental_config":rec(CONFIG),"supplemental_audit":rec(out/"supplemental_base_audit/acceptance.json"),
  "supplemental_cost":rec(out/"supplemental_gpu_cost.json"),"supplemental_deterministic_rng":rec(out/"deterministic_rng.json"),
  "superseded_rng_unresolved_history":{"gpu_job":"13234","actual_content_audit":rec(S/"runs/supplemental_actual_content_13235/outputs/acceptance.json"),"scope":"ENGINEERING_HISTORY_ONLY_PYTHON_KEY_SEED_NOT_RECONSTRUCTABLE","extra_cost_must_be_independently_retained":True},"supplemental_launcher_receipt":rec(S/"runs/supplemental_launcher_13241/outputs/acceptance.json"),
  "native_stage_status":{"native_bindcraft_trajectory":"PASS","soluble_proteinmpnn":"PASS","native_af2_ptm1_and_2":"PASS","native_filters":"PASS"},
  "stage_evidence":{"native_bindcraft_trajectory":base["stage_evidence"]["native_bindcraft_trajectory"],"soluble_proteinmpnn":rec(out/"soluble_proteinmpnn.json"),
    "native_af2_ptm1_and_2":rec(out/"native_confidence_and_basic_filters.json"),"native_filters":rec(out/"native_filters.json")},
  "explicit_limit":"Engineering API coverage only; does not establish native positive acceptance or scientific benchmark superiority",
  "collector_source":rec(Path(__file__).resolve()),"cpu_job":os.environ["SLURM_JOB_ID"],"scheduler_record":scheduler})
 write(out/"acceptance.json",doc);print(json.dumps({"status":doc["status"],"coverage_mode":doc["coverage_mode"],"receipt":rec(out/"acceptance.json")},indent=2))
if __name__=="__main__":main()
