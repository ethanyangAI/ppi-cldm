#!/usr/bin/env python3
import gc,hashlib,importlib,importlib.util,json,os,shutil,subprocess,sys,time,types
from pathlib import Path
from unittest.mock import patch
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";O=S/f"runs/finalize_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def write(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():raise FileExistsError(path)
 path.write_text(json.dumps(value,indent=2)+"\n")
assert os.environ["CUDA_VISIBLE_DEVICES"]=="" and os.environ["JAX_PLATFORMS"]=="cpu"
mode=sys.argv[1]
if mode=="rfd":
 spec=importlib.util.spec_from_file_location("runtime",R/"source/rebuild/benchmark_runtime.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 from rfdiffusion.inference import utils as iu
 fake=types.ModuleType("_official_rfd_entry");calls=[]
 class Sampler:
  def __init__(self,conf):self.calls=[conf]
  def initialize(self,conf):self.calls.append(conf)
 def main(conf):
  assert "hydra" not in conf
  assert conf.contigmap.contigs==["A1-85/0 65-65"]
  sampler=iu.sampler_selector(conf);calls.append(sampler)
 fake.main=types.SimpleNamespace(__wrapped__=main)
 attempt=O/"rfd_cache_fixture";attempt.mkdir()
 with patch.dict("sys.modules",{"_official_rfd_entry":fake}),patch.object(iu,"sampler_selector",Sampler):
  for seed in [1042,1043]:
   m.resident_rfd(["inference.input_pdb="+str(R/"vendor/BindCraft/example/PDL1.pdb"),"inference.output_prefix="+str(attempt/"unused"),"inference.ckpt_override_path="+str(R/"assets/rfdiffusion/Complex_base_ckpt.pt"),"inference.num_designs=1","inference.design_startnum="+str(seed),"inference.deterministic=True","contigmap.contigs=[A1-85/0 65-65]"],attempt)
 assert calls[0] is calls[1] and len(calls[0].calls)==2
 write(O/"resident_rfd_hydra_contract.json",{"status":"OFFICIAL_HYDRA_COMPOSITION_AND_SUPPORTED_SAMPLER_REINITIALIZATION_PASS","real_model_inference":False,"sampler_instances":1,"attempts":2})
else:
 import colabdesign,pyrosetta,numpy,jax,openmm,pdbfixer
 assert numpy.__version__=="1.24.3" and jax.__version__=="0.4.23" and jax.default_backend()=="cpu"
 pyrosetta.init("-mute all -ignore_unrecognized_res -ignore_zero_occupancy")
 rng=pyrosetta.rosetta.numeric.random.rg();rng.set_seed(1042);a=[rng.uniform() for _ in range(4)];rng.set_seed(1042);b=[rng.uniform() for _ in range(4)];assert a==b
 write(O/"rosetta_rng_contract.json",{"status":"OFFICIAL_ROSETTA_RANDOM_GENERATOR_EXPLICIT_SEED_REPRODUCIBLE","seed":1042,"draws":a})
 root_package=Path(colabdesign.__file__).parent;vendor=R/"vendor/ColabDesign/colabdesign";checked=0
 for installed in root_package.rglob("*"):
  if installed.is_file() and installed.suffix in [".py",".pkl"]:
   path=vendor/installed.relative_to(root_package)
   assert path.is_file() and hashlib.sha256(installed.read_bytes()).hexdigest()==hashlib.sha256(path.read_bytes()).hexdigest(),installed
   checked+=1
 write(O/"installed_source_contract.json",{"status":"INSTALLED_COLABDESIGN_PYTHON_AND_MPNN_WEIGHTS_MATCH_PINNED_SOURCE","files_checked":checked,"package":str(root_package),"pdbfixer_path":pdbfixer.__file__,"openmm_platforms":[openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())]})
 subprocess.run([sys.executable,"-m","pip","check"],check=True)
 with open(O/"bindcraft-freeze.txt","w") as f:subprocess.run([sys.executable,"-m","pip","freeze"],stdout=f,check=True)
 with open(O/"bindcraft-explicit.txt","w") as f:subprocess.run(["conda","list","--explicit"],stdout=f,check=True)

 # Literal CPU feature audit on a synthetic full RF complex; no prediction.
 import copy
 from Bio.PDB import PDBParser,PDBIO
 from Bio.PDB.Structure import Structure
 from Bio.PDB.Model import Model
 from Bio.PDB.Chain import Chain
 from Bio.PDB.Residue import Residue
 from colabdesign import mk_afdesign_model
 import jax.numpy as jnp
 target_pdb=R/"steps/22_matched_benchmark/input_preparation/prepared_7_13010/KEAP1_2FLU/input_manifest.json"
 target_manifest=json.loads(target_pdb.read_text());observed=PDBParser(QUIET=True).get_structure("target",target_manifest["target_pdb"]["path"])[0]["A"]
 fixture=Structure("cpu_fixture");frame=Model(0);fixture.add(frame);binder=Chain("A");receptor=Chain("B");frame.add(binder);frame.add(receptor)
 for i,residue in enumerate(observed,1):
  r=Residue((" ",65+i," "),residue.resname," ")
  for atom in residue:
   if atom.name in ["N","CA","C","O"]:r.add(copy.deepcopy(atom))
  receptor.add(r)
  if i<=65:
   b=Residue((" ",i," "),"GLY"," ")
   for atom in residue:
    if atom.name in ["N","CA","C","O"]:
     a=copy.deepcopy(atom);a.set_coord(a.coord+numpy.asarray([0.,0.,40.]));b.add(a)
   binder.add(b)
 fixture_pdb=O/"native_initial_guess_fixture.pdb";writer=PDBIO();writer.set_structure(fixture);writer.save(str(fixture_pdb))
 spec=importlib.util.spec_from_file_location("runtime",R/"source/rebuild/benchmark_runtime.py");runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
 af=mk_afdesign_model(protocol="binder",use_multimer=False,use_initial_guess=True,use_initial_atom_pos=False,pre_callback=runtime.sanitize_template_positions,num_recycles=3,data_dir=str(R/"assets/colabfold"),model_names=["model_1_ptm"])
 af.prep_inputs(pdb_filename=str(fixture_pdb),chain="B",binder_chain="A",binder_len=65,use_binder_template=False,rm_target_seq=False,rm_target_sc=False,seed=1042)
 assert af._lengths==[285,65] and af._args["use_initial_guess"] is True and af._args["use_initial_atom_pos"] is False
 features=jax.tree_util.tree_map(lambda x:jnp.asarray(x) if isinstance(x,numpy.ndarray) else x,copy.deepcopy(af._inputs));features["opt"]=af.opt
 af._update_template(features,jax.random.PRNGKey(1042));runtime.sanitize_template_positions(features)
 mask=numpy.asarray(features["template_all_atom_mask"]);position=numpy.asarray(features["template_all_atom_positions"])
 assert numpy.count_nonzero(mask[:,285:])==0 and numpy.count_nonzero(position[:,285:])==0
 assert numpy.count_nonzero(mask[:,:285])>0 and numpy.count_nonzero(position[:,:285])>0
 capture={}
 class CaptureInitialGuess(Exception):pass
 def capture_forward(*a,**kw):
  capture["prev_pos"]=numpy.asarray(af._inputs["prev"]["prev_pos"]).copy()
  raise CaptureInitialGuess()
 with patch.object(af,"_single",capture_forward):
  try:af._recycle(None,num_recycles=3,backprop=False)
  except CaptureInitialGuess:pass
 assert numpy.array_equal(capture["prev_pos"],numpy.asarray(af._inputs["batch"]["all_atom_positions"]))
 assert numpy.count_nonzero(capture["prev_pos"][:285])>0 and numpy.count_nonzero(capture["prev_pos"][285:])>0
 assert af._inputs["msa_feat"].shape[0]==1
 npz=O/"native_rf_actual_features.npz";numpy.savez_compressed(npz,template_all_atom_mask=mask,template_all_atom_positions=position,initial_guess_prev_pos=capture["prev_pos"],rm_template=numpy.asarray(af._inputs["rm_template"]),batch_all_atom_positions=numpy.asarray(af._inputs["batch"]["all_atom_positions"]))
 write(O/"native_rf_feature_contract.json",{"status":"LITERAL_RF_FULL_COMPLEX_INITIAL_GUESS_TARGET_ONLY_TEMPLATE_SINGLE_MSA_PASS","fixture_scope":"CPU synthetic geometry engineering test; never a scientific candidate","feature_arrays":rec(npz),"rfd_target_chain":"B","rfd_binder_chain":"A","model_query_order":["target","binder"],"target_residues":285,"binder_residues":65,"binder_template_mask_nonzero":0,"binder_template_positions_nonzero":0,"target_template_mask_nonzero":int(numpy.count_nonzero(mask[:,:285])),"full_complex_initial_guess_nonzero":int(numpy.count_nonzero(capture["prev_pos"])),"binder_initial_guess_nonzero":int(numpy.count_nonzero(capture["prev_pos"][285:])),"initial_atom_positions_enabled":False,"model_name":"model_1_ptm","recycles":3,"msa_rows":1,"real_model_inference":False})
 del af,features;gc.collect()
 source=S/"sources/dl_binder_design"
 if not source.exists():subprocess.run(["git","clone","--depth","1","https://github.com/nrbennet/dl_binder_design.git",str(source)],check=True)
 revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=source,text=True).strip()
 subprocess.run(["git","checkout","--detach",revision],cwd=source,check=True)
 primary=[]
 for relative in ["README.md","af2_initial_guess/README.md","af2_initial_guess/predict.py","af2_initial_guess/af2_util.py"]:
  path=source/relative
  if path.is_file():primary.append({"relative":relative,"receipt":rec(path),"url":f"https://github.com/nrbennet/dl_binder_design/blob/{revision}/{relative}"})
 write(O/"native_method_primary_source.json",{"repository":"https://github.com/nrbennet/dl_binder_design","revision":revision,"primary_sources":primary,"implemented_backend":"Pinned ColabDesign model_1_ptm, not direct execution of dl_binder_design modified AlphaFold package","matching_declared_semantics":["RF full-complex coordinates as previous-position initial guess","target-only template; binder template atom mask and coordinate array zero","single sequence/MSA","three recycles","binder CA RMSD after aligning target CA"],"native_rank":"mean of both full PAE matrix cross blocks, Angstrom, lower is better","criteria_label":"predeclared paper-aligned computational criteria; not exact filters from every published campaign"})

 root_settings=R/"steps/22_matched_benchmark/settings/pilot_v1";snap=root_settings/"source";snap.mkdir(parents=True,exist_ok=True)
 sources={}
 for original in [R/"source/rebuild/benchmark_runtime.py",S/"code/rfd_env.sh",S/"code/bindcraft_env.sh"]:
  target=snap/original.name
  if target.exists():assert target.read_bytes()==original.read_bytes(),target
  else:
   with target.open("xb") as f:f.write(original.read_bytes())
  sources[original.name]=rec(target)
 readiness=S/"runs/readiness_12980/outputs/acceptance.json";old=json.loads(readiness.read_text());assert old["status"]=="BOTH_PRIVATE_METHOD_RUNTIMES_CPU_READY_GPU_ENGINEERING_PILOT_PENDING"
 for item in old["records"]:
  path=Path(item["path"]);assert rec(path)==item,item
 config_inputs=[sources["benchmark_runtime.py"],rec(S/"runs/source_12947/outputs/sources.json"),rec(R/"source/environment/vendor-lock.json"),rec(readiness),rec(O/"bindcraft-freeze.txt"),rec(O/"installed_source_contract.json"),rec(O/"rosetta_rng_contract.json"),rec(O/"native_rf_feature_contract.json"),rec(O/"native_method_primary_source.json")]
 native={"model_name":"model_1_ptm","use_multimer":False,"use_initial_guess":True,"num_recycles":3,"params_dir":str(R/"assets/colabfold"),"rm_target_seq":False,"rm_target_sc":False,"environment_script":sources["bindcraft_env.sh"],"criteria":[{"metric":"binder_plddt","op":"ge","threshold":0.8},{"metric":"cross_pae_mean_angstrom","op":"le","threshold":10.0},{"metric":"binder_backbone_rmsd","op":"le","threshold":1.0}]}
 rf={"schema":"matched_method_adapter.v1","method":"rf_diffusion","binder_length":65,"execution_mode":"persistent_session","rfd":{"overrides":{"inference.write_trajectory":False}},"mpnn":{"num_seq_per_target":8,"sampling_temp":0.0001,"use_soluble_model":False,"batch_size":1,"omit_aas":"C"},"native_af2":native,"input_receipts":config_inputs+[sources["rfd_env.sh"],sources["bindcraft_env.sh"]],"native_score_name":"native_single_AF2_PTM_pae_interaction","native_score_direction":"lower_is_better"}
 bc={"schema":"matched_method_adapter.v1","method":"bindcraft","binder_length":65,"execution_mode":"persistent_session","bindcraft":{"advanced":rec(R/"vendor/BindCraft/settings_advanced/default_4stage_multimer.json"),"filters":rec(R/"vendor/BindCraft/settings_filters/default_filters.json")},"input_receipts":config_inputs+[sources["bindcraft_env.sh"]],"native_score_name":"native_BindCraft_average_AF2_iptm","native_score_direction":"higher_is_better"}
 write(root_settings/"rf_diffusion.json",rf);write(root_settings/"bindcraft.json",bc)
 write(O/"pilot_settings_receipt.json",{"status":"IMMUTABLE_ENGINEERING_PILOT_CONFIGS_AND_SESSION_SOURCE_SNAPSHOTS_PREPARED","root":str(root_settings),"sources":sources,"configs":{"rf_diffusion":rec(root_settings/"rf_diffusion.json"),"bindcraft":rec(root_settings/"bindcraft.json")},"prepared_keap1_manifest":rec(R/"steps/22_matched_benchmark/input_preparation/prepared_7_13010/KEAP1_2FLU/input_manifest.json"),"no_gpu_model_started":True})
 records=[rec(p) for p in sorted(O.iterdir()) if p.is_file()]
 acceptance={"status":"FINAL_PERSISTENT_METHOD_RUNTIME_CPU_VERIFIED_ENGINEERING_PILOT_READY","job_id":os.environ["SLURM_JOB_ID"],"gpu_requested":False,"gpu_models_run":False,"contracts_tests":14,"records":records,"upstream_readiness":rec(readiness),"latest_adapter":sources["benchmark_runtime.py"],"known_required_credentials":[],"unresolved":["actual GPU/JAX CUDA full-workflow engineering pilot","scientific benchmark not started"],"failed_install_jobs_preserved":["12948","12974","12982","12990"],"recovered_install_job":"12993"}
 write(O/"acceptance.json",acceptance)
 (S/"RUNTIME_CPU_CURRENT.json").write_text(json.dumps({"status":acceptance["status"],"acceptance":rec(O/"acceptance.json"),"settings_receipt":rec(O/"pilot_settings_receipt.json")},indent=2)+"\n")
 print(acceptance["status"],flush=True)

