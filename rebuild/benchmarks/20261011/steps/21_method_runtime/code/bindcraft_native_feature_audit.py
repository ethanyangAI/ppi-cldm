#!/usr/bin/env python3
import copy,hashlib,json,os,sys
from pathlib import Path
from unittest.mock import patch
import jax,jax.numpy as jnp,numpy as np
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";O=S/f"runs/bcf_feature_audit_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
assert jax.default_backend()=="cpu" and os.environ["CUDA_VISIBLE_DEVICES"]==""
sys.path.insert(0,str(R/"vendor/BindCraft"));import functions
from colabdesign import mk_afdesign_model
from colabdesign.af.alphafold.common import residue_constants as rc
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
advanced_path=R/"vendor/BindCraft/settings_advanced/default_4stage_multimer.json";advanced=json.loads(advanced_path.read_text())
design_models,prediction_models,multimer_validation=functions.load_af2_models(advanced["use_multimer_design"])
assert multimer_validation is False and advanced["predict_initial_guess"] is False and advanced["predict_bigbang"] is False
manifest_path=R/"steps/22_matched_benchmark/input_preparation/prepared_7_13010/KEAP1_2FLU/input_manifest.json";target=json.loads(manifest_path.read_text())
model=mk_afdesign_model(protocol="binder",num_recycles=advanced["num_recycles_validation"],data_dir=str(R/"assets/colabfold"),use_multimer=multimer_validation,use_initial_guess=advanced["predict_initial_guess"],use_initial_atom_pos=advanced["predict_bigbang"])
model.prep_inputs(pdb_filename=target["target_pdb"]["path"],chain=target["input_target_chain"],binder_len=65,rm_target_seq=advanced["rm_template_seq_predict"],rm_target_sc=advanced["rm_template_sc_predict"])
model._inputs=jax.tree_util.tree_map(lambda x:jnp.asarray(x) if isinstance(x,np.ndarray) else x,model._inputs)
binder=("ARNDQEGHILKMFPSTWYV"*4)[:65];captures=[]
class Capture(Exception):pass
def intercept(params,key,inputs):
 row={k:np.asarray(inputs[k]).copy() for k in ["aatype","msa_feat","template_all_atom_mask","template_all_atom_positions","template_pseudo_beta_mask","template_pseudo_beta"]}
 row["prev_pos"]=np.asarray(inputs["prev"]["prev_pos"]).copy()
 row["batch_all_atom_mask"]=np.asarray(inputs["batch"]["all_atom_mask"]).copy();row["batch_all_atom_positions"]=np.asarray(inputs["batch"]["all_atom_positions"]).copy()
 captures.append(row);raise Capture()
for i in prediction_models:
 with patch.object(model._model["runner"],"apply",intercept),jax.disable_jit():
  try:model.predict(seq=binder,models=[i],num_recycles=advanced["num_recycles_validation"],verbose=False,seed=1042)
  except Capture:pass
assert len(captures)==len(prediction_models)==2
T=target["residue_count"]
for c in captures:
 query="".join(rc.restypes[int(i)] for i in c["aatype"]);assert query==target["target_sequence"]+binder
 for key in ["template_all_atom_mask","template_all_atom_positions","template_pseudo_beta_mask","template_pseudo_beta"]:
  assert np.count_nonzero(c[key][:,T:])==0,key
  assert np.count_nonzero(c[key][:,:T])>0,key
 assert np.count_nonzero(c["prev_pos"])==0 and np.count_nonzero(c["batch_all_atom_positions"][T:])==0
 assert c["msa_feat"].shape[0]==1
npz=O/"bindcraft_native_actual_features.npz";np.savez_compressed(npz,**captures[0])
result={"status":"OFFICIAL_BINDCRAFT_DEFAULT_NATIVE_TEMPLATE_NO_BINDER_LEAKAGE_LITERAL_FEATURES_PASS","official_advanced":rec(advanced_path),"prepared_keap1":rec(manifest_path),"actual_model_indices":prediction_models,"model_names":[model._model_names[i] for i in prediction_models],"use_multimer_validation":multimer_validation,"predict_initial_guess":False,"predict_bigbang":False,"recycles":advanced["num_recycles_validation"],"binder_template_atom_mask_nonzero":0,"binder_template_positions_nonzero":0,"binder_template_pseudo_beta_mask_nonzero":0,"binder_template_pseudo_beta_nonzero":0,"initial_guess_prev_pos_nonzero":0,"template_source":"official default target-only starting PDB; padded binder coordinates/masks all zero","our_sanitization_callback_applied":False,"native_official_scientific_settings_modified":False,"actual_features":rec(npz),"real_model_inference":False,"source":rec(Path(__file__))}
(O/"acceptance.json").write_text(json.dumps(result,indent=2)+"\n")
print(result["status"],flush=True)

