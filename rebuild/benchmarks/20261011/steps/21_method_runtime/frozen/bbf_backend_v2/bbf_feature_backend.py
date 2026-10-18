#!/usr/bin/env python3
"""BBF development AF2-Multimer inference: CPU actual-feature audit and frozen GPU worker.
No sequence optimization, binder coordinates/templates or previous-position guesses.
"""
import argparse,copy,gc,hashlib,importlib.util,json,os,re,subprocess,time,traceback
from pathlib import Path
ROOT=Path("/lustre/users/u21111210118/projects/test9")
def inside(p):
 p=Path(p).resolve()
 if not p.is_relative_to(ROOT):raise ValueError("Project-private path required")
 return p
def receipt(p):
 p=inside(p);return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def atomic(p,v):
 p=inside(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+".tmp")
 tmp.write_text(json.dumps(v,indent=2,allow_nan=False)+"\n");tmp.replace(p)
def verify_cpu(rec):
 p=inside(rec["path"])
 if receipt(p)!=rec:raise ValueError("Input receipt mismatch "+str(p))
 return p
def load_plan(p):
 p=inside(p);plan=json.loads(p.read_text());settings=plan["settings"]
 if settings["models"]!=[1,2,3,4,5] or settings["seed"]!=31031 or settings["recycles"]!=3:raise ValueError("Fixed 5x1x3 diagnosis required")
 if settings["use_initial_guess"] or settings["use_initial_atom_pos"]:raise ValueError("No coordinate guess allowed")
 return p,plan
def sanitize_template(inputs):
 import jax.numpy as jnp
 mask=inputs["template_all_atom_mask"];valid=jnp.any(mask>0,axis=-1)
 inputs["template_all_atom_positions"]=jnp.where(mask[...,None]>0,inputs["template_all_atom_positions"],0)
 inputs["template_pseudo_beta_mask"]=jnp.where(valid,inputs["template_pseudo_beta_mask"],0)
 inputs["template_pseudo_beta"]=jnp.where(valid[...,None],inputs["template_pseudo_beta"],0)
def make_model():
 from colabdesign import mk_afdesign_model
 return mk_afdesign_model(protocol="binder",use_multimer=True,use_initial_guess=False,use_initial_atom_pos=False,
                          pre_callback=sanitize_template,num_recycles=3,data_dir=str(ROOT/"assets/colabfold"),
                          model_names=["model_"+str(i)+"_multimer_v3" for i in range(1,6)])
def prepare_job(model,job):
 import numpy as np
 from colabdesign.af.prep import get_multi_id
 from colabdesign.af.alphafold.common import protein,residue_constants as rc
 target,binder=job["target_sequence"],job["binder_sequence"];T,B=len(target),len(binder)
 if T not in [111,112] or not binder or any(x not in rc.restypes for x in target+binder):raise ValueError("Exact full control queries required")
 if job["binder_template_enabled"]:raise ValueError("Binder templates prohibited")
 source=inside(job["target_template_pdb"]["path"])
 raw=protein.from_pdb_string(source.read_text(),chain_id="A")
 if len(raw.aatype)!=111:raise ValueError("9HAG chain A111 expected")
 positions=np.zeros((T+B,37,3),dtype=np.float32);mask=np.zeros((T+B,37),dtype=np.float32)
 aatype=np.asarray([rc.restype_order[x] for x in target+binder],dtype=np.int32)
 mapping=job["target_query_to_template_indices"]
 if not isinstance(mapping,dict) or len(mapping)!=111:raise ValueError("Explicit one-based mapping of 111 observed residues required")
 for query_pos,source_pos in mapping.items():
  qi,si=int(query_pos)-1,int(source_pos)-1
  if not 0<=qi<T or not 0<=si<111 or aatype[qi]!=raw.aatype[si]:raise ValueError("Target query/template sequence mapping mismatch")
  positions[qi]=raw.atom_positions[si];mask[qi]=raw.atom_mask[si]
 model._tmp.pop("save",None)
 model.prep_inputs(pdb_filename=str(source),chain="A",binder_len=B,rm_target=not job["target_template_enabled"],rm_target_seq=False,rm_target_sc=False,seed=31031)
 model._target_len=T;model._binder_len=B;model._len=B;model._lengths=[T,B]
 batch={"aatype":aatype,"all_atom_positions":positions,"all_atom_mask":mask}
 model._pdb["batch"]=batch;model._pdb["lengths"]=[T,B]
 model._inputs=model._prep_features(num_res=T+B,num_seq=1)
 model._inputs["batch"]=batch
 model._inputs["residue_index"]=np.concatenate([np.arange(T),T-1+np.arange(B)+50])
 model._inputs.update(get_multi_id([T,B]))
 for name,removed_target in [("rm_template",not job["target_template_enabled"]),("rm_template_seq",False),("rm_template_sc",False)]:
  model._inputs[name]=np.concatenate([np.full(T,removed_target),np.ones(B,dtype=bool)])
 model._args["redesign"]=False
 model._prep_model(seed=31031)
 return T,B
def cpu_features(plan_path,outdir):
 import numpy as np,jax,jax.numpy as jnp
 from unittest.mock import patch
 assert os.environ.get("SLURM_JOB_ID") and jax.default_backend()=="cpu" and os.environ.get("CUDA_VISIBLE_DEVICES")=="" 
 path,plan=load_plan(plan_path);outdir=inside(outdir);outdir.mkdir(parents=True,exist_ok=True)
 for j in plan["jobs"]:verify_cpu(j["target_template_pdb"])
 # CPU-only ownership guard unit checks; no scheduler GPU or NVML invocation.
 probe={"gpus":[{"index":2,"name":"NVIDIA A100-PCIE-40GB","uuid":"GPU-owned"}]}
 for cuda in ["0","2","GPU-owned"]:assert_owned_cuda(probe,{"SLURM_JOB_GPUS":"2","CUDA_VISIBLE_DEVICES":cuda})
 for env in [{"CUDA_VISIBLE_DEVICES":"GPU-owned"},{"SLURM_JOB_GPUS":"2","CUDA_VISIBLE_DEVICES":"GPU-other"},{"SLURM_JOB_GPUS":"2","CUDA_VISIBLE_DEVICES":"0,1"},{"SLURM_JOB_GPUS":"2","CUDA_VISIBLE_DEVICES":"9"}]:
  try:assert_owned_cuda(probe,env)
  except RuntimeError:pass
  else:raise AssertionError("Unowned or extra CUDA device accepted")
 model=make_model();records=[]
 for job in plan["jobs"]:
  T,B=prepare_job(model,job)
  model._inputs=jax.tree_util.tree_map(lambda x:jnp.asarray(x) if isinstance(x,np.ndarray) else x,model._inputs)
  captures=[]
  class Capture(Exception):pass
  def intercept(params,key,inputs):
   d={k:np.asarray(inputs[k]).copy() for k in ["aatype","msa_feat","template_all_atom_mask","template_all_atom_positions","template_pseudo_beta_mask","template_pseudo_beta"]}
   d["prev_pos"]=np.asarray(inputs["prev"]["prev_pos"]).copy()
   d["batch_all_atom_mask"]=np.asarray(inputs["batch"]["all_atom_mask"]).copy()
   d["batch_all_atom_positions"]=np.asarray(inputs["batch"]["all_atom_positions"]).copy()
   captures.append(d);raise Capture()
  for slot in job["slots"]:
   with patch.object(model._model["runner"],"apply",intercept),jax.disable_jit():
    try:model.predict(seq=job["binder_sequence"],models=[slot["model"]-1],num_recycles=3,seed=slot["seed"],verbose=False)
    except Capture:pass
  if len(captures)!=5:raise ValueError("Every model must expose literal forward features")
  first=captures[0]
  for captured in captures:
   for key in first:assert np.array_equal(first[key],captured[key]),(job["job_key"],key)
  from colabdesign.af.alphafold.common import residue_constants as rc
  query="".join(rc.restypes[int(i)] for i in first["aatype"])
  assert query==job["target_sequence"]+job["binder_sequence"]
  for key in ["template_all_atom_mask","template_all_atom_positions","template_pseudo_beta_mask","template_pseudo_beta"]:assert np.count_nonzero(first[key][:,T:])==0
  assert np.count_nonzero(first["prev_pos"])==0
  mapped={int(k)-1 for k in job["target_query_to_template_indices"]}
  extra=[i for i in range(T) if i not in mapped]
  for i in extra:
   assert np.count_nonzero(first["template_all_atom_mask"][:,i])==0 and np.count_nonzero(first["template_all_atom_positions"][:,i])==0
  effective=int(np.count_nonzero(first["template_all_atom_mask"][:,:T]))
  if job["target_template_enabled"]:assert effective>0
  else:assert effective==0 and np.count_nonzero(first["template_all_atom_positions"])==0
  assert first["msa_feat"].shape[0]==1
  first["query_aatype"]=first["aatype"];first["query_msa"]=first["msa_feat"][...,:22].argmax(-1)
  first["deletion_matrix_int"]=np.zeros((1,T+B),dtype=np.int32)
  first["rm_template"]=np.asarray(model._inputs["rm_template"])
  file=outdir/job["job_key"]/"features.npz";file.parent.mkdir(exist_ok=True)
  np.savez_compressed(file,**first)
  records.append({"job_key":job["job_key"],"features":receipt(file),"mask_key":"template_all_atom_mask","position_key":"template_all_atom_positions",
   "query_aatype_key":"query_aatype","msa_key":"query_msa","deletion_key":"deletion_matrix_int","msa_feat_key":"msa_feat","msa_feature_key":"msa_feat","initial_prev_pos_key":"prev_pos",
   "binder_template_atom_mask_count":0,"binder_template_coordinate_nonzero_count":0,"initial_guess_enabled":False,"initial_atom_position_enabled":False,
   "target_msa_rows":1,"binder_msa_rows":1,"extra_target_terminal_template_atom_mask_count":0,
   "observed_target_template_atom_mask_count":effective,"exact_target_query":job["target_sequence"],"exact_binder_query":job["binder_sequence"],
   "actual_validated_model_slots":job["slots"],"all_models_feature_arrays_identical":True,"mapped_target_residues":len(mapped)})
  print(job["job_key"]+" 5 literal model features PASS",flush=True);del captures,first;gc.collect()
 manifest={"status":"ALL22_JOBS_110_LITERAL_MODEL_INPUTS_CPU_VERIFIED","plan":receipt(path),"source":receipt(Path(__file__)),"settings":plan["settings"],
 "masking_source":"official pinned ColabDesign af/inputs.py _update_template lines100-109 applies rm_template to atommask; pre_callback sanitize_template in this frozen backend masks coordinate+pseudo-beta channels used by forward models",
 "raw_source_scope":"experimental 9HAG A observed atom coordinates/masks only; no imputed CB or unobserved prefixM coordinates",
 "feature_capture":"official forward sequence/template pipeline through pre_callback; runner.apply intercepted before real model computation",
 "gpu_hardware_receipt":receipt(ROOT/"steps/23_common_review/inputs/proc_gpu_inventory_13044.json"),"gpu_hardware_model":"NVIDIA A100-PCIE-40GB",
 "no_gpu_or_real_model_inference":True,"hardware_guard_cpu_contracts":7,"constructor_arguments":{"protocol":"binder","use_multimer":True,"use_initial_guess":False,"use_initial_atom_pos":False,"num_recycles":3,"model_names":["model_"+str(i)+"_multimer_v3" for i in range(1,6)]},"jobs":records}
 atomic(outdir/"feature_manifest.json",manifest);return manifest
def assert_owned_cuda(probe,env,expected_gpu_name="NVIDIA A100-PCIE-40GB"):
 if not (env.get("SLURM_STEP_GPUS") or env.get("SLURM_JOB_GPUS")):raise RuntimeError("Explicit scheduler physical GPU ownership required")
 if len(probe["gpus"])!=1 or probe["gpus"][0]["name"]!=expected_gpu_name:raise RuntimeError("Assigned GPU differs from frozen physical GPU model")
 cuda=env.get("CUDA_VISIBLE_DEVICES")
 if not cuda or len(cuda.split(","))!=1:raise RuntimeError("Exactly one explicit CUDA_VISIBLE_DEVICES entry required")
 gpu=probe["gpus"][0]
 if cuda.startswith("GPU-") and cuda!=gpu["uuid"]:raise RuntimeError("CUDA visible UUID not scheduler-owned")
 if not cuda.startswith("GPU-") and cuda not in ["0",str(gpu["index"])]:raise RuntimeError("CUDA visible numeric device neither global assignment nor local zero")
 return gpu,cuda

def gpu_guard(source,expected_gpu_name):
 """Use the frozen budget ownership guard, including Linux-minor to NVML-UUID mapping."""
 spec=importlib.util.spec_from_file_location("frozen_budget_guard",inside(source));mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 if not hasattr(mod,"gpu_ownership_guard"):raise RuntimeError("A newly verified frozen gpu_ownership_guard API is required; old selection-only guard forbidden")
 guard=mod.gpu_ownership_guard(expected_count=1,expected_gpu_name=expected_gpu_name,env=dict(os.environ))
 owned=guard["owned_gpu_uuids"]
 if len(owned)!=1 or guard["child_cuda_visible_devices"]!=owned[0]:raise RuntimeError("Frozen ownership guard did not produce one owned physical UUID")
 os.environ["CUDA_VISIBLE_DEVICES"]=guard["child_cuda_visible_devices"]
 return {**guard,"allocated_gpu_count":1,"slurm_job_id":os.environ["SLURM_JOB_ID"]}
def predict(plan_path,key,outdir,feature_manifest,guard_source,expected_gpu_name):
 features=json.loads(inside(feature_manifest).read_text())
 if expected_gpu_name!=features["gpu_hardware_model"]:raise RuntimeError("GPU model differs from frozen CPU hardware declaration")
 allocation=gpu_guard(guard_source,expected_gpu_name)
 import jax,numpy as np
 if len([d for d in jax.devices() if d.platform=="gpu"])!=1:raise RuntimeError("Exactly one JAX visible GPU required")
 _,plan=load_plan(plan_path);job=next(j for j in plan["jobs"] if j["job_key"]==key)
 entry=next(j for j in features["jobs"] if j["job_key"]==key)
 if features["status"]!="ALL22_JOBS_110_LITERAL_MODEL_INPUTS_CPU_VERIFIED" or entry["exact_target_query"]!=job["target_sequence"] or entry["exact_binder_query"]!=job["binder_sequence"]:raise RuntimeError("Frozen CPU feature manifest mismatch")
 outdir=inside(outdir);outdir.mkdir(parents=True,exist_ok=True);worker=outdir/"worker.json"
 data={"job_key":key,"settings":plan["settings"],"allocation":allocation,"features_source_receipt":features["source"],"features_cpu_receipt":entry["features"],"models":[]}
 atomic(worker,data);model=make_model();prepare_job(model,job)
 for slot in job["slots"]:
  started=time.time();row={"slot":slot}
  try:
   model.predict(seq=job["binder_sequence"],models=[slot["model"]-1],num_recycles=3,seed=slot["seed"],verbose=False)
   pdb=outdir/("model_"+str(slot["model"])+".pdb");scores=outdir/("model_"+str(slot["model"])+"_scores.json");model.save_pdb(str(pdb))
   plddt=np.asarray(model.aux["plddt"],dtype=float)*100;pae=np.asarray(model.aux["pae"],dtype=float);L=len(job["target_sequence"])+len(job["binder_sequence"])
   if plddt.shape!=(L,) or pae.shape!=(L,L) or not np.isfinite(plddt).all() or not np.isfinite(pae).all():raise RuntimeError("Malformed actual AF2 confidence arrays")
   atomic(scores,{"plddt":plddt.tolist(),"pae":pae.tolist(),"globaliptm":float(model.aux["i_ptm"]),"iptm":float(model.aux["i_ptm"]),"ptm":float(model.aux["ptm"]),
   "plddt_units":"0-100","pae_units":"Angstrom (ColabDesign get_pae raw matrix; no normalization multiplier)","query":job["target_sequence"]+job["binder_sequence"],
   "chains":{"A":"target","B":"binder"},"initial_guess":False,"initial_atom_pos":False,"seed":slot["seed"],"model":slot["model"]})
   row.update({"pdb_path":str(pdb),"scores_path":str(scores),"returncode":0})
  except Exception as exc:row.update({"returncode":1,"error":str(exc),"traceback":traceback.format_exc()})
  row["elapsed"]=time.time()-started;data["models"].append(row);atomic(worker,data)
 data["status"]="COMPLETE" if all(x["returncode"]==0 for x in data["models"]) else "COMPLETE_WITH_TYPED_MODEL_FAILURES";atomic(worker,data)
 return data
def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest="command",required=True)
 a=sub.add_parser("features");a.add_argument("--plan",required=True);a.add_argument("--output-dir",required=True)
 a=sub.add_parser("predict");a.add_argument("--plan",required=True);a.add_argument("--job-key",required=True);a.add_argument("--output-dir",required=True);a.add_argument("--features-manifest",required=True);a.add_argument("--guard-source",required=True);a.add_argument("--expected-gpu-name",required=True)
 a=p.parse_args()
 if a.command=="features":cpu_features(a.plan,a.output_dir)
 else:predict(a.plan,a.job_key,a.output_dir,a.features_manifest,a.guard_source,a.expected_gpu_name)
if __name__=="__main__":main()

