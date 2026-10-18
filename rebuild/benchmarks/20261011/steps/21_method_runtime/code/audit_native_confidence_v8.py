#!/usr/bin/env python3
"""CPU audit of actual native AF2 observation archives, including rejects/partial runs."""
import argparse,hashlib,json,math,os,subprocess
from pathlib import Path
import numpy as np
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
ROOT=Path("/lustre/users/u21111210118/projects/test9")
def receipt(p):
 p=Path(p);h=hashlib.sha256()
 with p.open("rb") as f:
  for block in iter(lambda:f.read(4*1024*1024),b""):h.update(block)
 return {"path":str(p),"bytes":p.stat().st_size,"sha256":h.hexdigest()}
def checked_project(p,parent=None):
 p=Path(p).resolve()
 if ROOT not in p.parents:raise RuntimeError("Nonproject native archive path")
 if parent is not None and Path(parent).resolve() not in p.parents:raise RuntimeError("Native archive escapes its attempt")
 return p
def stream(p):
 p=Path(p)
 if not p.exists():return [],{"present":False,"complete_lines":0,"partial_tail_bytes":0}
 blob=p.read_bytes();parts=blob.split(b"\n");complete=parts[:-1];tail=parts[-1]
 rows=[json.loads(b) for b in complete if b.strip()]
 return rows,{"present":True,"receipt":receipt(p),"complete_lines":len(rows),"partial_tail_bytes":len(tail)}
def near(actual,declared,label,atol=2e-6):
 if not math.isfinite(float(actual)) or not math.isclose(float(actual),float(declared),rel_tol=0,abs_tol=atol):
  raise RuntimeError(f"Native confidence mismatch {label}: computed={actual},declared={declared}")
def confidence_record(path,attempt,target,method):
 path=checked_project(path,attempt);doc=json.loads(path.read_text())
 assert doc["schema"]=="native_af2_observation.v1" and doc["status"]=="ACTUAL_PREDICT_RETURN_OBSERVED"
 assert doc["method"]==method and doc["observation_only"] is True
 T=int(target["residue_count"]);L=T+65;query=target["target_sequence"]+doc["binder_sequence"]
 assert doc["target_sequence"]==target["target_sequence"] and doc["target_length"]==T and doc["binder_length"]==65
 assert doc["actual_full_query"]==query and len(doc["binder_sequence"])==65
 npz=checked_project(doc["arrays"]["path"],attempt);pdb=checked_project(doc["raw_pdb"]["path"],attempt)
 assert npz.stat().st_size==doc["arrays"]["bytes"] and pdb.stat().st_size==doc["raw_pdb"]["bytes"]
 with np.load(npz,allow_pickle=False) as bundle:arrays={k:bundle[k].copy() for k in bundle.files}
 assert set(arrays)=={"pae","plddt","aatype","i_ptm","ptm"}
 assert arrays["pae"].shape==(L,L) and arrays["plddt"].shape==(L,) and arrays["aatype"].shape==(L,)
 assert all(np.isfinite(x).all() for x in arrays.values())
 assert arrays["aatype"].dtype.kind in "iu" and np.all((arrays["aatype"]>=0)&(arrays["aatype"]<20))
 alphabet="ARNDCQEGHILKMFPSTWYV";actual="".join(alphabet[int(x)] for x in arrays["aatype"])
 assert actual==query and np.all((arrays["plddt"]>=0)&(arrays["plddt"]<=1))
 assert doc["array_keys"]=={"pae_angstrom":"pae","plddt_fraction":"plddt","actual_query_aatype":"aatype","raw_i_ptm":"i_ptm","raw_ptm":"ptm"}
 assert doc["units"]["pae"]=="angstrom; official get_pae output, no scale transformation"
 assert doc["units"]["plddt"]=="fraction 0-1; official get_plddt output, no scale transformation"
 models=doc["actual_model_names"];assert len(models)==len(doc["actual_model_indices"])==1
 assert models==doc["context"]["model_names"] and models[0] in (["model_1_ptm"] if method=="rf_diffusion" else ["model_1_ptm","model_2_ptm"])
 assert doc["actual_model_indices"]==[int(models[0].split("_")[1])-1] or method=="rf_diffusion"
 log=doc["native_aux_log"];assert log["models"]==doc["actual_model_indices"]
 pae=np.asarray(arrays["pae"],dtype=float);plddt=np.asarray(arrays["plddt"])
 cross=np.concatenate([pae[:T,T:].ravel(),pae[T:,:T].ravel()])
 recomputed={"binder_plddt":float(plddt[-65:].mean()),"cross_pae_mean_angstrom":float(cross.mean()),
  "raw_global_iptm":float(arrays["i_ptm"]),"raw_ptm":float(arrays["ptm"]),
  "native_BC_pae_normalized":float(((pae+pae.T)/2)[-65:].mean()/31.),
  "native_BC_i_pae_normalized":float(cross.mean()/31.)}
 for key,label in [("binder_plddt","plddt"),("raw_global_iptm","i_ptm"),("raw_ptm","ptm"),
                   ("native_BC_pae_normalized","pae"),("native_BC_i_pae_normalized","i_pae")]:
  near(recomputed[key],log[label],label,atol=3e-6)
 model=PDBParser(QUIET=True).get_structure("actual-native",str(pdb))[0]
 chainseq={c.id:"".join(seq1(r.resname) for r in c if r.id[0]==" ") for c in model}
 assert chainseq=={"A":target["target_sequence"],"B":doc["binder_sequence"]},chainseq
 for chain,selection in [("A",plddt[:T]),("B",plddt[T:])]:
  observed=[r["CA"].bfactor/100. for r in model[chain] if r.id[0]==" "]
  np.testing.assert_allclose(observed,selection,atol=.000051,rtol=0)
 official=doc["context"].get("official_native_pdb_path");official_receipt=None
 if official and Path(official).exists():
  original=checked_project(official,attempt);assert original.read_bytes()==pdb.read_bytes(),"Archived PDB differs from official same prediction"
  official_receipt=receipt(original)
 return {"observation_id":doc["observation_id"],"archive":receipt(path),"arrays":receipt(npz),"raw_pdb":receipt(pdb),
  "query_sha256":hashlib.sha256(actual.encode()).hexdigest(),"actual_full_query":actual,
  "target_chain":"A","binder_chain":"B","target_length":T,"binder_length":65,
  "model_names":models,"model_indices":doc["actual_model_indices"],"actual_model_rng_seed":doc["actual_model_rng_seed"],
  "actual_model_rng_key_after_predict":doc["actual_model_rng_key_after_predict"],"context":doc["context"],
  "task_id":doc["task_id"],"attempt_index":doc["attempt_index"],"replicate_seed":doc["replicate_seed"],
  "completed_at_epoch":doc["completed_at_epoch"],"metrics":recomputed,"native_aux_log":log,
  "official_native_pdb":official_receipt,"official_native_pdb_present":official_receipt is not None,
  "missing_official_pdb_interpretation":"May be native rejection cleanup or cutoff before official save; retained raw archive does not impute workflow completion" if official and official_receipt is None else None}
def audit_attempt(attempt,target,cfg,runtime):
 attempt=checked_project(attempt);method=cfg["method"]
 observed,index_meta=stream(attempt/"native_confidence.jsonl");raw,raw_meta=stream(attempt/"sequences.jsonl")
 updates,update_meta=stream(attempt/"native_screening.jsonl");events,event_meta=stream(attempt/"bindcraft_native_events.jsonl")
 rows=[];ids=set()
 for item in observed:
  assert item["observation_id"] not in ids;ids.add(item["observation_id"])
  path=checked_project(item["path"],attempt);assert path.stat().st_size==item["bytes"]
  row=confidence_record(path,attempt,target,method);assert row["observation_id"]==item["observation_id"] and item["method"]==method
  rows.append(row)
 published={r["archive"]["path"] for r in rows}
 orphan=[str(p) for p in sorted((attempt/"native_confidence").glob("*")) if str(p) not in published and p.suffix in [".npz",".pdb",".partial",".json"]]
 # Sidecar JSON is the durable completion marker; a cutoff may precede its index line.
 orphan_sidecars=[];partial=[]
 for name in orphan:
  p=Path(name)
  if p.suffix==".json":
   orphan_sidecars.append(confidence_record(p,attempt,target,method))
  elif p.suffix==".partial" or not p.with_suffix(".json").exists():partial.append(receipt(p))
 all_rows=rows+orphan_sidecars
 raw_by_id={r["sequence_record_id"]:r for r in raw};assert len(raw_by_id)==len(raw)
 ranking=[]
 if method=="rf_diffusion":
  by_sequence={r["context"]["sequence_record_id"]:r for r in all_rows};assert len(by_sequence)==len(all_rows)
  data_path=attempt/"rf_native_inputs.json";data=json.loads(data_path.read_text()) if data_path.exists() else None
  for update_index,update in enumerate(updates):
   ident=update["sequence_record_id"];assert ident in raw_by_id and ident in by_sequence
   row=by_sequence[ident];assert row["actual_full_query"]==target["target_sequence"]+raw_by_id[ident]["sequence"]
   assert update["native_confidence"]["path"]==row["archive"]["path"]
   original=update["native_metrics"];metrics=row["metrics"]
   for key in ["binder_plddt","cross_pae_mean_angstrom"]:near(metrics[key],original[key],key,atol=1e-12)
   near(metrics["raw_global_iptm"],original["global_iptm"],"global_iptm",atol=3e-6)
   assert data is not None
   pdb=Path(update["native_structure_path"]);rmsd=runtime.method_native_metrics(data["backbone_pdb"],str(pdb),target["rfd_output_target_chain"],target["rfd_binder_chain"],"A","B")
   for key,value in rmsd.items():near(value,original[key],key,atol=1e-12)
   full={**original,**metrics,**rmsd};accepted=True
   for criterion in cfg["native_af2"]["criteria"]:
    value=full[criterion["metric"]]
    accepted=accepted and (value>=criterion["threshold"] if criterion["op"]=="ge" else value<=criterion["threshold"])
   assert accepted is bool(update["internal_acceptance"])
   near(metrics["cross_pae_mean_angstrom"],update["native_score"],"RF emitted ranking score",atol=1e-12)
   assert update["native_score_name"]=="native_single_AF2_PTM_pae_interaction"
   ranking.append({"sequence_record_id":ident,"native_update_index":update_index,"ranking_status":"EMITTED_NATIVE_SCORE_INDEPENDENTLY_RECOMPUTED","update":update,
    "observations":[{k:row[k] for k in ["archive","arrays","raw_pdb","query_sha256","model_names","model_indices"]}],"native_score_recomputed":metrics["cross_pae_mean_angstrom"],
    "native_acceptance_recomputed":accepted,"target_aligned_rmsd_recomputed":rmsd,"actual_raw_arrays_verified":True})
 else:
  filter_path=checked_project(cfg["bindcraft"]["filters"]["path"]);assert receipt(filter_path)==cfg["bindcraft"]["filters"]
  filters=json.loads(filter_path.read_text())
  import ast
  official_filter_source=ROOT/"vendor/BindCraft/functions/generic_utils.py"
  tree=ast.parse(official_filter_source.read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="check_filters")
  namespace={};exec(compile(ast.Module(body=[node],type_ignores=[]),str(official_filter_source),"exec"),namespace)
  check_filters=namespace["check_filters"]
  final_events={e["design"]:e for e in events if e["event"]=="native_final_filter_complete"}
  by_design={}
  for row in all_rows:
   design=row["context"]["native_design"];by_design.setdefault(design,[]).append(row)
   for ident in row["context"]["sequence_record_ids"]:
    assert ident in raw_by_id and row["actual_full_query"]==target["target_sequence"]+raw_by_id[ident]["sequence"]
  af_events={}
  for event in events:
   if event["event"]!="native_af2_filter_complete":continue
   design=event["design"];af_events[design]=event;available=by_design.get(design,[])
   assert len(available)==len(event["statistics"])
   independently_passed=True
   for row in available:
    num=str(row["model_indices"][0]+1);stats=event["statistics"][num];log=row["native_aux_log"]
    for label,key in [("pLDDT","plddt"),("pTM","ptm"),("i_pTM","i_ptm"),("pAE","pae"),("i_pAE","i_pae")]:
     near(round(float(log[key]),2),stats[label],label,atol=1e-12)
    for label,key,higher in [("pLDDT","plddt",True),("pTM","ptm",True),("i_pTM","i_ptm",True),("pAE","pae",False),("i_pAE","i_pae",False)]:
     threshold=filters.get(num+"_"+label,{}).get("threshold")
     if threshold is not None:independently_passed=independently_passed and (log[key]>=threshold if higher else log[key]<=threshold)
   assert independently_passed is event["native_af2_pass"],"Actual BC base AF2 filter result disagrees with full raw arrays"
   if independently_passed:assert {r["model_names"][0] for r in available}=={"model_1_ptm","model_2_ptm"}
  for update_index,update in enumerate(updates):
   ident=update["sequence_record_id"];assert ident in raw_by_id
   observation_paths={v["path"] for v in update.get("native_confidence",[])}
   matched=[r for r in all_rows if r["archive"]["path"] in observation_paths]
   assert len(matched)==len(observation_paths)
   for row in matched:assert ident in row["context"]["sequence_record_ids"]
   if update["native_score"] is None:
    ranking.append({"sequence_record_id":ident,"native_update_index":update_index,"ranking_status":"NATIVE_SCORE_NOT_AVAILABLE","update":update,"actual_models_completed":len(matched),
     "observations":[{k:r[k] for k in ["archive","arrays","raw_pdb","query_sha256","model_names","model_indices"]} for r in matched],
     "native_score_recomputed":None,"reason":"Official native ranking score NA retained; incomplete/rejected models are not imputed"})
    continue
   design=update["native_design"];available=by_design[design];assert {r["model_names"][0] for r in available}=={"model_1_ptm","model_2_ptm"}
   assert af_events[design]["native_af2_pass"] is True
   raw_mean=float(np.mean([r["metrics"]["raw_global_iptm"] for r in available]))
   rounded_author_score=round(sum(round(r["metrics"]["raw_global_iptm"],2) for r in available)/len(available),2)
   near(rounded_author_score,update["native_score"],"BC official rounded average i_pTM ranking score",atol=1e-12)
   assert update["native_score_name"]=="native_BindCraft_average_AF2_iptm"
   final=final_events[design];values=final["filter_values"]
   result=check_filters(list(values.values()),list(values),filters)
   assert result==final["result"]==update["native_filter_result"]
   assert (result is True) is bool(update["internal_acceptance"])
   ranking.append({"sequence_record_id":ident,"native_update_index":update_index,"ranking_status":"EMITTED_NATIVE_SCORE_INDEPENDENTLY_RECOMPUTED","update":update,"actual_models_completed":len(available),
    "observations":[{k:r[k] for k in ["archive","arrays","raw_pdb","query_sha256","model_names","model_indices"]} for r in available],"raw_mean_iptm":raw_mean,"native_score_recomputed":rounded_author_score,
    "native_rounding":"official rounds each model i_pTM to 2 decimals, then mean and round to 2 decimals",
    "actual_raw_arrays_verified":True,"native_default_filters_independently_recomputed":True,"native_filter_result":result,
    "native_filter_source":receipt(official_filter_source),"native_filter_settings":receipt(filter_path)})
 return {"schema":"native_confidence_cpu_audit.v1","status":"ACTUAL_NATIVE_CONFIDENCE_ARCHIVES_AND_EMITTED_RANKING_VALUES_CPU_AUDITED",
  "method":method,"attempt_dir":str(attempt),"collector_source":receipt(Path(__file__)),"runtime_source":receipt(Path(runtime.__file__)),
  "streams":{"observations":index_meta,"raw_sequences":raw_meta,"native_updates":update_meta,"bc_events":event_meta},
  "complete_observation_count":len(all_rows),"complete_indexed_observation_count":len(rows),"complete_unindexed_sidecars":orphan_sidecars,
  "partial_unpublished_artifacts":partial,"actual_native_predictions":rows,"ranking_value_and_criteria_checks":ranking,
  "native_updates_without_extra_inference":len(updates),"scientific_scope":"ENGINEERING_ONLY","no_new_predictions":True,
  "scope":"Actual raw outputs audited including reject/NA/partial; this alone does not assert full workflow completion or formal cutoff eligibility"}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--attempt-dir",required=True);ap.add_argument("--target-manifest",required=True)
 ap.add_argument("--config",required=True);ap.add_argument("--config-sha256",required=True);ap.add_argument("--runtime-source",required=True);ap.add_argument("--output-dir",required=True)
 args=ap.parse_args()
 if not os.environ.get("SLURM_JOB_ID") or os.environ.get("CUDA_VISIBLE_DEVICES")!="":raise RuntimeError("CPU Slurm and empty CUDA mask required")
 scheduler=subprocess.check_output(["scontrol","show","job","-o",os.environ["SLURM_JOB_ID"]],text=True)
 if "gres/gpu=" in scheduler:raise RuntimeError("CPU collector must not allocate GPU")
 import importlib.util
 source=checked_project(args.runtime_source);spec=importlib.util.spec_from_file_location("rt",source);runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
 cfg,target,cp,tp=runtime.load_method_inputs(args.config,args.config_sha256,args.target_manifest)
 report=audit_attempt(args.attempt_dir,target,cfg,runtime);report.update({"method_config":receipt(cp),"target_manifest":receipt(tp),"cpu_job":os.environ["SLURM_JOB_ID"],"scheduler_record":scheduler})
 out=checked_project(args.output_dir);out.mkdir(parents=True,exist_ok=True);path=out/"acceptance.json"
 if path.exists():raise FileExistsError(path)
 path.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps({"status":report["status"],"receipt":receipt(path)},indent=2))
if __name__=="__main__":main()

