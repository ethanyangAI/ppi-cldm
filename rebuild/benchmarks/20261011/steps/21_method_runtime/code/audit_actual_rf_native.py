#!/usr/bin/env python3
"""CPU-only independent audit of a completed RF-native engineering attempt."""
import argparse,hashlib,importlib.util,json,math,os,subprocess
from pathlib import Path
import numpy as np
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
R=Path("/lustre/users/u21111210118/projects/test9")
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def write(p,v):
 if p.exists():raise FileExistsError(p)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+"\n")
def streams(p):return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
def fasta_samples(p):
 rows=[];header=None;sequence=[]
 def finish():
  if header is not None and "sample=" in header:rows.append((header,"".join(sequence)))
 for line in p.read_text().splitlines():
  if line.startswith(">"):finish();header=line[1:];sequence=[]
  else:sequence.append(line.strip())
 finish();return rows
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--attempt-dir",required=True);ap.add_argument("--target-manifest",required=True);ap.add_argument("--output-dir",required=True);ap.add_argument("--runtime-source",required=True);ap.add_argument("--features",action="store_true");a=ap.parse_args()
 if not os.environ.get("SLURM_JOB_ID"):raise RuntimeError("CPU Slurm required")
 if os.environ.get("CUDA_VISIBLE_DEVICES")!="":raise RuntimeError("CPU audit requires explicit CUDA_VISIBLE_DEVICES empty")
 job=os.environ["SLURM_JOB_ID"];scheduler=subprocess.check_output(["scontrol","show","job","-o",job],text=True)
 if any(t.startswith("gres/gpu=") and int(t.split("=")[1])>0 for line in scheduler.splitlines() for token in line.split() if token.startswith(("TRES=","AllocTRES=")) for t in token.split("=",1)[1].split(",")):raise RuntimeError("CPU audit may not allocate a GPU")
 attempt=Path(a.attempt_dir).resolve();out=Path(a.output_dir).resolve();source=Path(a.runtime_source).resolve();manifest=Path(a.target_manifest).resolve()
 for p in [attempt,out,source,manifest]:
  if R not in p.parents:raise RuntimeError("Nonproject path")
 out.mkdir(parents=True,exist_ok=True);spec=importlib.util.spec_from_file_location("rt",source);rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
 terminal=json.loads((attempt/"attempt_result.json").read_text());assert terminal["status"]=="COMPLETED",terminal
 cfg,target,cp,tp=rt.load_method_inputs(terminal["config_path"],terminal["config_sha256"],str(manifest));assert cfg["method"]=="rf_diffusion"
 data=json.loads((attempt/"rf_native_inputs.json").read_text());backbone=Path(data["backbone_pdb"]);identity=rt.validate_rfd_output(backbone,backbone.with_suffix(".trb"),target)
 raw=streams(attempt/"sequences.jsonl");updates=streams(attempt/"native_screening.jsonl");samples=fasta_samples(attempt/"generated/mpnn/seqs"/(backbone.stem+".fa"))
 assert len(raw)==8 and len(updates)==8 and samples==[(row["mpnn_header"],row["sequence"]) for row in raw]
 assert data["sequences"]==raw and len({row["sequence_record_id"] for row in raw})==8
 by_id={row["sequence_record_id"]:row for row in updates};assert set(by_id)=={row["sequence_record_id"] for row in raw} and len(by_id)==8
 parser=PDBParser(QUIET=True);structures=[];features=[];model=None
 if a.features:
  import jax,jax.numpy as jnp
  from unittest.mock import patch
  from colabdesign import mk_afdesign_model
  from colabdesign.af.alphafold.common import residue_constants as rc
  assert jax.default_backend()=="cpu"
  model=mk_afdesign_model(protocol="binder",use_multimer=False,use_initial_guess=True,use_initial_atom_pos=False,pre_callback=rt.sanitize_template_positions,num_recycles=3,data_dir=cfg["native_af2"]["params_dir"],model_names=["model_1_ptm"])
  model.prep_inputs(pdb_filename=str(backbone),chain=target["rfd_output_target_chain"],binder_chain=target["rfd_binder_chain"],binder_len=65,use_binder_template=False,rm_target_seq=False,rm_target_sc=False,seed=int(data["seed"]))
  model._inputs=jax.tree_util.tree_map(lambda x:jnp.asarray(x) if isinstance(x,np.ndarray) else x,model._inputs)
 T=int(target["residue_count"])
 for row in raw:
  update=by_id[row["sequence_record_id"]];pdb=Path(update["native_structure_path"]);native=parser.get_structure("native",pdb)[0]
  chainseq={c.id:"".join(seq1(r.resname) for r in c if r.id[0]==" ") for c in native}
  assert chainseq=={"A":target["target_sequence"],"B":row["sequence"]},chainseq
  metric=rt.method_native_metrics(str(backbone),str(pdb),target["rfd_output_target_chain"],target["rfd_binder_chain"],target["common_target_chain"],target["common_binder_chain"])
  confidence=float(np.mean([r["CA"].bfactor for r in native["B"] if r.id[0]==" "]))/100.
  original=update["native_metrics"]
  for key,value in metric.items():assert math.isclose(value,original[key],abs_tol=1e-6),(key,value,original[key])
  assert math.isclose(confidence,original["binder_plddt"],abs_tol=.00011)
  assert update["native_score_name"]=="native_single_AF2_PTM_pae_interaction"
  assert math.isclose(update["native_score"],original["cross_pae_mean_angstrom"],abs_tol=1e-12)
  accepted=confidence>=.8 and original["cross_pae_mean_angstrom"]<=10 and metric["binder_backbone_rmsd"]<=1.
  # Confidence PDB rounding may cross an exact threshold; native raw confidence remains the declared criterion.
  raw_accepted=original["binder_plddt"]>=.8 and original["cross_pae_mean_angstrom"]<=10 and metric["binder_backbone_rmsd"]<=1.
  assert bool(update["internal_acceptance"])==raw_accepted
  structures.append({"sequence_record_id":row["sequence_record_id"],"native_pdb":rec(pdb),"full_query_and_physical_chains_verified":True,"native_metrics_recomputed":metric,"binder_plddt_from_pdb":confidence,"declared_pae_angstrom":original["cross_pae_mean_angstrom"],"pae_verification_scope":"actual immutable native code validated full aux.pae; full PAE matrix was not exported, so this CPU audit checks the emitted value rather than independently recomputing AF2","native_criteria_consistent":True})
  if model is not None:
   capture={}
   class Captured(Exception):pass
   def intercept(params,key,inputs):
    for k in ["aatype","msa_feat","template_all_atom_mask","template_all_atom_positions","template_pseudo_beta_mask","template_pseudo_beta","atom37_atom_exists"]:capture[k]=np.asarray(inputs[k]).copy()
    capture["initial_guess_prev_pos"]=np.asarray(inputs["prev"]["prev_pos"]).copy()
    capture["batch_all_atom_mask"]=np.asarray(inputs["batch"]["all_atom_mask"]).copy()
    capture["batch_all_atom_positions"]=np.asarray(inputs["batch"]["all_atom_positions"]).copy()
    raise Captured()
   with patch.object(model._model["runner"],"apply",intercept),jax.disable_jit():
    try:model.predict(seq=row["sequence"],models=[0],num_recycles=3,verbose=False)
    except Captured:pass
   query="".join(rc.restypes[int(i)] for i in capture["aatype"]);assert query==target["target_sequence"]+row["sequence"]
   for key in ["template_all_atom_mask","template_all_atom_positions","template_pseudo_beta_mask","template_pseudo_beta"]:
    assert np.count_nonzero(capture[key][:,T:])==0 and np.count_nonzero(capture[key][:,:T])>0
   assert np.array_equal(capture["initial_guess_prev_pos"],capture["batch_all_atom_positions"])
   cb=rc.atom_order["CB"];nongly=capture["aatype"][T:]!=rc.restype_order["G"]
   assert np.all(capture["batch_all_atom_mask"][T:,cb]>0) and np.all(np.any(capture["initial_guess_prev_pos"][T:,cb,:]!=0,axis=-1))
   assert capture["msa_feat"].shape[0]==1
   path=out/"features"/(row["sequence_record_id"]+".npz");path.parent.mkdir(exist_ok=True);np.savez_compressed(path,**capture)
   features.append({"sequence_record_id":row["sequence_record_id"],"query":query,"npz":rec(path),"binder_all_template_channels_nonzero":0,"full_initial_guess_verified":True,"single_msa_verified":True,"model_forward_executed":False,"capture_scope":"same immutable ColabDesign prep/update/pre_callback pipeline intercepted at actual runner.apply on CPU; no AF2 computation"})
 report={"status":"ACTUAL_GPU_RF_NATIVE_COMPLETE_BRANCH_CPU_INDEPENDENT_AUDIT_PASS","attempt_result":rec(attempt/"attempt_result.json"),"raw_sequences":rec(attempt/"sequences.jsonl"),"native_updates":rec(attempt/"native_screening.jsonl"),"target_manifest":rec(manifest),"method_config":rec(cp),"runtime_source":rec(source),"collector_source":rec(Path(__file__)),"rfd_identity":identity,"complete_mpnn_sequences":8,"complete_native_validations":8,"native_structures":structures,"actual_queries_feature_captures":features,"feature_capture_completed":len(features)==8,"no_new_gpu_prediction":True,"cpu_job":job,"scheduler_record":scheduler,"scope":"engineering acceptance only; not common endpoint, experiment or blockade proof"}
 write(out/"acceptance.json",report);print(json.dumps({"status":report["status"],"receipt":rec(out/"acceptance.json")},indent=2))
if __name__=="__main__":main()

