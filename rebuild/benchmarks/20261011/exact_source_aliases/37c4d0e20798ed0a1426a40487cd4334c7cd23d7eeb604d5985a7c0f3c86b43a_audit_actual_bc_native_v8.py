#!/usr/bin/env python3
"""CPU-only complete BindCraft engineering-content gate; incomplete stages stay typed."""
import argparse,hashlib,importlib.util,json,os,subprocess
from pathlib import Path
import numpy as np
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
ROOT=Path("/lustre/users/u21111210118/projects/test9")
def rec(p):
 p=Path(p);h=hashlib.sha256()
 with p.open("rb") as f:
  for block in iter(lambda:f.read(4*1024*1024),b""):h.update(block)
 return {"path":str(p),"bytes":p.stat().st_size,"sha256":h.hexdigest()}
def write(p,obj):
 if p.exists():raise FileExistsError(p)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+"\n")
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def streams(path):return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()] if Path(path).exists() else []
def main():
 ap=argparse.ArgumentParser()
 for name in ["attempt-dir","target-manifest","config","config-sha256","runtime-source","confidence-collector-source","plan","run-receipt","output-dir"]:ap.add_argument("--"+name,required=True)
 args=ap.parse_args()
 if not os.environ.get("SLURM_JOB_ID") or os.environ.get("CUDA_VISIBLE_DEVICES")!="":raise RuntimeError("CPU Slurm with empty CUDA mask required")
 scheduler=subprocess.check_output(["scontrol","show","job","-o",os.environ["SLURM_JOB_ID"]],text=True)
 if "gres/gpu=" in scheduler:raise RuntimeError("CPU collector may not allocate GPU")
 attempt=Path(args.attempt_dir).resolve();out=Path(args.output_dir).resolve();source=Path(args.runtime_source).resolve()
 plan_path=Path(args.plan).resolve();run_path=Path(args.run_receipt).resolve();manifest=Path(args.target_manifest).resolve()
 for p in [attempt,out,source,plan_path,run_path,manifest]:
  if ROOT not in p.parents:raise RuntimeError("Nonproject native audit path")
 out.mkdir(parents=True,exist_ok=True);rt=load("runtime",source);cc=load("confidence",Path(args.confidence_collector_source))
 cfg,target,cp,tp=rt.load_method_inputs(args.config,args.config_sha256,str(manifest));assert cfg["method"]=="bindcraft"
 plan=json.loads(plan_path.read_text());run=json.loads(run_path.read_text());assert run["plan"]==rec(plan_path) and attempt.parent.parent==run_path.parent
 task=run["task"];assert task["method_id"]=="bindcraft" and task in plan["tasks"]
 method=next(v for v in plan["protocol"]["methods"] if v["method_id"]=="bindcraft")
 assert rec(cp)==method["config_receipt"] and rec(source) in method["adapter_receipts"]
 target_def=next(v for v in plan["protocol"]["targets"] if v["target_id"]==task["target_id"]);assert rec(manifest)==target_def["input_manifest"]
 orchestrator=Path(plan["orchestrator"]["path"]);assert rec(orchestrator)==plan["orchestrator"]
 gpu_counts=[int(x.split("=",1)[1]) for x in run["scheduler_alloc_tres"].split(",") if x.startswith("gres/gpu=")]
 assert gpu_counts==[1] and len(run["hardware"]["gpus"])==len(run["hardware"]["owned_gpu_uuids"])==1
 assert run["child_cuda_visible_devices"]==run["hardware"]["owned_gpu_uuids"][0]
 events=streams(attempt/"bindcraft_native_events.jsonl");raw=streams(attempt/"sequences.jsonl")
 updates=streams(attempt/"native_screening.jsonl");timing=streams(attempt/"stage_timing.jsonl")
 terminal=json.loads((attempt/"attempt_result.json").read_text());assert terminal["status"] in ["COMPLETED","SCIENTIFIC_REJECT"]
 report=cc.audit_attempt(attempt,target,cfg,rt);write(out/"raw_confidence_audit.json",report)
 for observation in report["actual_native_predictions"]+report["complete_unindexed_sidecars"]:
  assert observation["task_id"]==task["task_id"] and int(observation["replicate_seed"])==int(task["seed"]) and int(observation["attempt_index"])==int(attempt.name)
  doc=json.loads(Path(observation["archive"]["path"]).read_text())
  assert doc["plan_sha256"]==rec(plan_path)["sha256"] and doc["method_config_sha256"]==rec(cp)["sha256"] and doc["target_manifest_sha256"]==rec(manifest)["sha256"]
 trajectories=[e for e in events if e["event"]=="trajectory_complete"];assert len(trajectories)==1
 trajectory=trajectories[0];assert len(trajectory["sequence"])==65
 pose=[p for p in (attempt/"generated/Trajectory").rglob(trajectory["design"]+".pdb") if "/Relaxed/" not in str(p)]
 assert len(pose)==1,pose
 structure=PDBParser(QUIET=True).get_structure("native-trajectory",str(pose[0]))[0]
 seqs={c.id:"".join(seq1(r.resname) for r in c if r.id[0]==" ") for c in structure}
 assert set(seqs)=={"A","B"} and seqs["A"]==target["target_sequence"] and len(seqs["B"])==65
 identity_path=ROOT/"steps/21_method_runtime/runs/bc_native_identity_13217/outputs/identity.json"
 identity_diag=json.loads(identity_path.read_text())
 assert identity_diag["pose"]==rec(pose[0]) and identity_diag["trajectory"]==trajectory
 assert seqs["B"]==identity_diag["chains"]["B"]["actual"] and trajectory["sequence"]==identity_diag["chains"]["B"]["expected"]
 trajectory_evidence={"status":"ACTUAL_COMPLETED_OFFICIAL_TRAJECTORY_IDENTITY_VERIFIED","trajectory":trajectory,"native_pose":rec(pose[0]),"identity_diagnostic":rec(identity_path),"physical_binder_sequence":seqs["B"],"reported_hard_sequence":trajectory["sequence"],"physical_vs_reported_mismatches":identity_diag["chains"]["B"]["mismatches"],"export_semantics":{"get_seq":"best aux seq.hard argmax","save_pdb":"best aux all.aatype from pseudo argmax","best_soft":trajectory["native_logs"]["soft"],"best_hard":trajectory["native_logs"]["hard"],"source_proof":[rec(ROOT/"vendor/ColabDesign"/p) for p in ["colabdesign/shared/model.py","colabdesign/af/model.py","colabdesign/af/utils.py"]]},"events":rec(attempt/"bindcraft_native_events.jsonl"),"target_manifest":rec(manifest),"scope":"engineering only; native early rejection retained"}
 write(out/"native_bindcraft_trajectory.json",trajectory_evidence)
 mpnn_events=[e for e in events if e["event"]=="mpnn_raw_batch_complete"]
 mpnn_covered=len(mpnn_events)==1 and mpnn_events[0]["n"]==20 and len(raw)==20
 if mpnn_covered:
  assert [r["mpnn_index"] for r in raw]==list(range(20)) and len({r["sequence_record_id"] for r in raw})==20
  assert all(len(r["sequence"])==65 and not(set(r["sequence"])-set("ACDEFGHIKLMNPQRSTVWY")) for r in raw)
  assert any(e["stage"]=="official_mpnn_gen_sequence" for e in timing)
  assert Path(mpnn_events[0]["source_pdb"]).resolve()==pose[0].resolve()
 mpnn_evidence={"status":"ACTUAL_SOLUBLE_MPNN20_RAW_POOL_RETURN_AND_LEDGER_VERIFIED" if mpnn_covered else "NOT_COVERED_NATIVE_EARLY_REJECTION",
  "events":mpnn_events,"raw_pool_ledger":rec(attempt/"sequences.jsonl") if (attempt/"sequences.jsonl").exists() else None,
  "complete_pool_sequences":raw,"count":len(raw),"official_advanced_settings":cfg["bindcraft"]["advanced"],
  "scope":"Raw official sample(num=1,batch=20) return; includes duplicate/internal-rejected sequences; no supplementary sequences imputed"}
 write(out/"soluble_proteinmpnn.json",mpnn_evidence)
 models={m for row in report["actual_native_predictions"] for m in row["model_names"]}
 final_events=[e for e in events if e["event"]=="native_final_filter_complete"]
 af_covered={"model_1_ptm","model_2_ptm"}.issubset(models)
 features=[];observations=report["actual_native_predictions"]
 if observations:
  import jax,jax.numpy as jnp
  from unittest.mock import patch
  from colabdesign import mk_afdesign_model
  from colabdesign.af.alphafold.common import residue_constants as rc
  advanced=json.loads(Path(cfg["bindcraft"]["advanced"]["path"]).read_text())
  assert advanced["predict_initial_guess"] is False and advanced["predict_bigbang"] is False
  model=mk_afdesign_model(protocol="binder",use_multimer=False,use_initial_guess=False,use_initial_atom_pos=False,num_recycles=int(advanced["num_recycles_validation"]),data_dir=str(ROOT/"assets/colabfold"),model_names=["model_1_ptm","model_2_ptm"])
  model.prep_inputs(pdb_filename=target["target_pdb"]["path"],chain=target["input_target_chain"],binder_len=65,
   rm_target_seq=advanced["rm_template_seq_predict"],rm_target_sc=advanced["rm_template_sc_predict"],seed=int(observations[0]["actual_model_rng_seed"]))
  model._inputs=jax.tree_util.tree_map(lambda x:jnp.asarray(x) if isinstance(x,np.ndarray) else x,model._inputs)
  for observation in observations:
   capture={}
   class Captured(Exception):pass
   def intercept(params,key,inputs):
    for name in ["aatype","msa_feat","template_all_atom_mask","template_all_atom_positions","template_pseudo_beta_mask","template_pseudo_beta"]:
     capture[name]=np.asarray(inputs[name]).copy()
    capture["initial_prev_pos"]=np.asarray(inputs["prev"]["prev_pos"]).copy();raise Captured()
   sequence=observation["actual_full_query"][int(target["residue_count"]):];index=observation["model_indices"][0]
   with patch.object(model._model["runner"],"apply",intercept),jax.disable_jit():
    try:model.predict(seq=sequence,models=[index],num_recycles=int(observation["context"]["num_recycles"]),verbose=False)
    except Captured:pass
   T=int(target["residue_count"]);actual="".join(rc.restypes[int(x)] for x in capture["aatype"])
   assert actual==observation["actual_full_query"] and capture["msa_feat"].shape[0]==1
   assert np.count_nonzero(capture["initial_prev_pos"])==0
   for name in ["template_all_atom_mask","template_all_atom_positions","template_pseudo_beta_mask","template_pseudo_beta"]:
    assert np.count_nonzero(capture[name][:,T:])==0 and np.count_nonzero(capture[name][:,:T])>0
   path=out/"features"/(observation["observation_id"]+".npz");path.parent.mkdir(exist_ok=True);np.savez_compressed(path,**capture)
   features.append({"observation":observation["archive"],"actual_model_names":observation["model_names"],"actual_full_query":actual,"actual_input_features":rec(path),"single_msa":True,
    "all_binder_template_channels_nonzero":0,"initial_prev_pos_nonzero":0,"no_new_AF2_prediction":True,
    "scope":"CPU intercept of same immutable official prep/update pipeline on actual GPU query; not an additional prediction"})
 validation_evidence={"status":"ACTUAL_NATIVE_PTM1_AND_PTM2_OUTPUTS_AND_INPUT_QUERIES_VERIFIED" if af_covered else "NOT_COVERED_NATIVE_PTMS_INCOMPLETE",
  "models_observed":sorted(models),"actual_prediction_count":len(observations),"confidence_audit":rec(out/"raw_confidence_audit.json"),"actual_query_feature_captures":features,
  "rejected_predictions_retained":True,"native_score_NA_not_imputed":True}
 write(out/"native_af2_ptm1_and_2.json",validation_evidence)
 filters_covered=len(final_events)>0
 filters_evidence={"status":"ACTUAL_NATIVE_DEFAULT_FINAL_FILTER_API_DECISIONS_INDEPENDENTLY_VERIFIED" if filters_covered else "NOT_COVERED_NATIVE_EARLY_REJECTION",
  "default_filters":cfg["bindcraft"]["filters"],"events":final_events,"confidence_and_filter_cpu_recomputation":rec(out/"raw_confidence_audit.json"),
  "native_scientific_positive_required":False}
 write(out/"native_filters.json",filters_evidence)
 stages={"native_bindcraft_trajectory":"PASS","soluble_proteinmpnn":"PASS" if mpnn_covered else "NOT_COVERED",
  "native_af2_ptm1_and_2":"PASS" if af_covered else "NOT_COVERED","native_filters":"PASS" if filters_covered else "NOT_COVERED"}
 complete=all(v=="PASS" for v in stages.values())
 accept={"status":"NATIVE_GPU_METHOD_WORKFLOW_CONTENT_ACCEPTED_ENGINEERING_ONLY" if complete else "NATIVE_GPU_METHOD_WORKFLOW_STAGE_COVERAGE_INCOMPLETE_ENGINEERING_ONLY",
  "method_id":"bindcraft","task_id":task["task_id"],"plan":rec(plan_path),"runtime_source":rec(source),"orchestrator_source":rec(orchestrator),
  "config_receipt":rec(cp),"target_manifest":rec(manifest),"run_receipt":rec(run_path),"actual_assigned_gpu_count":1,"scientific_scope":"ENGINEERING_ONLY",
  "coverage_mode":"primary_native_workflow","native_stage_status":stages,"stage_evidence":{k:rec(out/(k+".json")) for k in stages},
  "native_stages_covered":[k for k,v in stages.items() if v=="PASS"],"raw_confidence_audit":rec(out/"raw_confidence_audit.json"),
  "confidence_collector_source":rec(Path(args.confidence_collector_source)),"collector_source":rec(Path(__file__)),
  "raw_sequence_count":len(raw),"native_update_count":len(updates),"native_full_filter_decision_count":len(final_events),
  "cpu_job":os.environ["SLURM_JOB_ID"],"scheduler_record":scheduler,"no_new_GPU_model_predictions":True,
  "scope":"Full engineering method coverage only if all stages actually executed; early rejection does not satisfy formal readiness"}
 write(out/"acceptance.json",accept);print(json.dumps({"status":accept["status"],"receipt":rec(out/"acceptance.json")},indent=2))
if __name__=="__main__":main()
