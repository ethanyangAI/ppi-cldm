#!/usr/bin/env python3
import copy,hashlib,importlib.util,json,os,shutil,time
from pathlib import Path
from unittest.mock import patch
import jax,jax.numpy as jnp,numpy as np
from colabdesign import mk_afdesign_model
from colabdesign.af.alphafold.common import residue_constants as rc
from colabdesign.af.alphafold.model.modules import pseudo_beta_fn
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";O=S/f"runs/pilot_v6_features_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
def receipt(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():raise FileExistsError(p)
 p.write_text(json.dumps(v,indent=2)+"\n")
assert jax.default_backend()=="cpu" and os.environ["CUDA_VISIBLE_DEVICES"]==""
spec=importlib.util.spec_from_file_location("runtime",R/"steps/22_matched_benchmark/settings/pilot_v6/source/benchmark_runtime.py");rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
af=mk_afdesign_model(protocol="binder",use_multimer=False,use_initial_guess=True,use_initial_atom_pos=False,pre_callback=rt.sanitize_template_positions,num_recycles=3,data_dir=str(R/"assets/colabfold"),model_names=["model_1_ptm"])
fixture=R/"steps/22_matched_benchmark/engineering_pilot/runs/13069_0/attempts/000000/generated/backbone_1436254356.pdb"
af.prep_inputs(pdb_filename=str(fixture),chain="A",binder_chain="B",binder_len=65,use_binder_template=False,rm_target_seq=False,rm_target_sc=False,seed=1042)
af._inputs=jax.tree_util.tree_map(lambda x:jnp.asarray(x) if isinstance(x,np.ndarray) else x,af._inputs)
binder=("ARNDQEGHILKMFPSTWYV"*4)[:65];capture={}
class Captured(Exception):pass
def intercept(params,key,inputs):
 for k in ["aatype","msa_feat","template_all_atom_mask","template_all_atom_positions","template_pseudo_beta_mask","template_pseudo_beta","atom37_atom_exists"]:
  capture[k]=np.asarray(inputs[k]).copy()
 capture["initial_guess_prev_pos"]=np.asarray(inputs["prev"]["prev_pos"]).copy()
 capture["batch_all_atom_mask"]=np.asarray(inputs["batch"]["all_atom_mask"]).copy()
 capture["batch_all_atom_positions"]=np.asarray(inputs["batch"]["all_atom_positions"]).copy()
 raise Captured()
with patch.object(af._model["runner"],"apply",intercept),jax.disable_jit():
 try:af.predict(seq=binder,models=[0],num_recycles=3,verbose=False,seed=1042)
 except Captured:pass
assert capture,"Literal pre-model inputs not captured"
T=285;query="".join(rc.restypes[int(i)] for i in capture["aatype"])
manifest=R/"steps/22_matched_benchmark/input_preparation/prepared_7_13010/KEAP1_2FLU/input_manifest.json"
target=json.loads(manifest.read_text())["target_sequence"];assert query==target+binder
for k in ["template_all_atom_mask","template_all_atom_positions","template_pseudo_beta_mask","template_pseudo_beta"]:
 assert np.count_nonzero(capture[k][:,T:])==0,(k,"binder leak")
 assert np.count_nonzero(capture[k][:,:T])>0,(k,"target absent")
assert np.array_equal(capture["initial_guess_prev_pos"],capture["batch_all_atom_positions"])
cb=rc.atom_order["CB"];ca=rc.atom_order["CA"];ids=capture["aatype"][T:];nongly=ids!=rc.restype_order["G"]
assert np.all(capture["batch_all_atom_mask"][T:,cb]>0)
assert np.all(np.any(capture["initial_guess_prev_pos"][T:,cb,:]!=0,axis=-1))
assert np.all(capture["atom37_atom_exists"][T:,cb][nongly]==1)
pseudo=np.asarray(pseudo_beta_fn(capture["aatype"],capture["initial_guess_prev_pos"],None))[T:]
expected=np.where(nongly[:,None],capture["initial_guess_prev_pos"][T:,cb,:],capture["initial_guess_prev_pos"][T:,ca,:])
assert np.array_equal(pseudo,expected)
assert capture["msa_feat"].shape[0]==1
npz=O/"literal_query_features.npz";np.savez_compressed(npz,**capture)
proof={"status":"LITERAL_SEQUENCE_CB_INITIAL_GUESS_AND_ALL_TEMPLATE_CHANNELS_PASS","actual_forward_interception":"official _model input pipeline after update_seq/update_aatype/update_template/pre_callback; intercepted runner.apply before model computation","fixture_scope":"preserved actual official RFD engineering backbone 13069_0 with full target A/binder B; synthetic query for CPU feature validation only, never a scientific candidate","actual_backbone":receipt(fixture),"target_sequence":target,"binder_sequence":binder,"full_query_sequence":query,"nongly_binder_residues":int(nongly.sum()),"nongly_initial_guess_CB_present":True,"gly_initial_guess_pseudo_beta_is_CA":True,"binder_template_all_atom_mask_nonzero":0,"binder_template_positions_nonzero":0,"binder_template_pseudo_beta_mask_nonzero":0,"binder_template_pseudo_beta_nonzero":0,"target_template_atom_mask_nonzero":int(np.count_nonzero(capture["template_all_atom_mask"][:,:T])),"initial_guess_scope":"N/CA/C/O plus ColabDesign official geometric CB completion; no distal sidechain construction or FastRelax","msa_rows":1,"use_initial_guess":True,"use_initial_atom_pos":False,"model":"model_1_ptm","recycles":3,"npz":receipt(npz),"runtime":receipt(R/"source/rebuild/benchmark_runtime.py"),"real_model_inference":False}
write(O/"native_rf_all_channels_contract.json",proof)
print(json.dumps({"status":proof["status"],"literal_proof":receipt(O/"native_rf_all_channels_contract.json"),"runtime":proof["runtime"],"actual_backbone":proof["actual_backbone"]},indent=2))

