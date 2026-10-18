#!/usr/bin/env python3
"""Project-private official model runtime and budget-session adapters."""
import argparse, datetime, hashlib, importlib, importlib.metadata as md, json, os, platform, subprocess, sys
from pathlib import Path
ROOT=Path("/lustre/users/u21111210118/projects/test9")
STEP=ROOT/"steps/21_method_runtime"
_SESSION={}
_RFD_SAMPLER=None
_NATIVE_AF2_MODEL=None
_NATIVE_CHILD=None
_NATIVE_COUNTER=0
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""): h.update(b)
 return h.hexdigest()
def rec(p): return {"path":str(p),"bytes":p.stat().st_size,"sha256":sha(p)}
def run(args,cwd=None):
 p=subprocess.run(args,cwd=cwd,text=True,capture_output=True)
 return {"args":args,"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr}
def atomic(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists(): raise FileExistsError(p)
 t=p.with_name(p.name+".partial")
 t.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
 t.replace(p)
def probe(label,output):
 os.environ["JAX_PLATFORMS"]="cpu"
 os.environ["CUDA_VISIBLE_DEVICES"]=""
 mods={"core":["numpy","scipy","Bio","ppiblocker"],"rfd":["torch","dgl","e3nn","se3_transformer","rfdiffusion"],"colabfold":["jax","jaxlib","colabfold","alphafold","pdbfixer","openmm"],"boltz":["torch","boltz"],"physics":["pyrosetta","openmm"],"bindcraft":["jax","jaxlib","colabdesign","pyrosetta","pdbfixer","openmm","pandas","matplotlib","seaborn","scipy","Bio"]}[label]
 out={"label":label,"python":sys.executable,"version":sys.version,"prefix":sys.prefix,"platform":platform.platform(),"slurm_job_id":os.environ.get("SLURM_JOB_ID"),"modules":{},"pip_check":run([sys.executable,"-m","pip","check"])}
 for mod in mods:
  try:
   m=importlib.import_module(mod)
   version=getattr(m,"__version__",None)
   if version is None:
    try: version=md.version(mod)
    except md.PackageNotFoundError: version=None
   out["modules"][mod]={"import":"PASS","version":str(version),"file":getattr(m,"__file__",None)}
  except Exception as e: out["modules"][mod]={"import":"FAIL","error":repr(e)}
 if label=="bindcraft":
  vendor=ROOT/"vendor/BindCraft"
  sys.path.insert(0,str(vendor))
  try:
   m=importlib.import_module("functions")
   out["bindcraft_functions_import"]={"status":"PASS","file":m.__file__}
  except Exception as e: out["bindcraft_functions_import"]={"status":"FAIL","error":repr(e)}
 out["status"]="CPU_IMPORT_PROBE_COMPLETE"
 atomic(Path(output),out)
 print(json.dumps({k:v for k,v in out.items() if k not in {"pip_check"}},indent=2))
def inventory(output):
 out={"status":"EXISTING_RUNTIME_INVENTORY_COMPLETE","slurm_job_id":os.environ.get("SLURM_JOB_ID"),"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"repos":{},"assets":[],"locks":[]}
 for name in ["RFdiffusion","ProteinMPNN","dllogger","BindCraft","ColabDesign"]:
  p=ROOT/"vendor"/name
  if p.exists():
   out["repos"][name]={"path":str(p),"head":run(["git","rev-parse","HEAD"],p),"remote":run(["git","remote","-v"],p),"status":run(["git","status","--porcelain"],p),"license": [rec(x) for x in p.glob("*LICENSE*") if x.is_file()]}
 for name in ["rfdiffusion","colabfold","pyrosetta"]:
  p=ROOT/"assets"/name
  for x in sorted(p.rglob("*")):
   if x.is_file():out["assets"].append(rec(x))
 for p in sorted((ROOT/"env").glob("*-*.txt")):
  if p.is_file(): out["locks"].append(rec(p))
 for p in sorted((ROOT/"source/environment").glob("*")):
  if p.is_file():out["locks"].append(rec(p))
 atomic(Path(output),out);print("INVENTORY",len(out["assets"]),len(out["repos"]))
def inside_project(p):
 p=Path(p).resolve()
 if ROOT not in p.parents:raise RuntimeError("Path outside authoritative project")
 return p
def jsonable(x):
 if isinstance(x,dict):return {str(k):jsonable(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [jsonable(v) for v in x]
 if isinstance(x,Path):return str(x)
 if hasattr(x,"tolist"):return jsonable(x.tolist())
 if hasattr(x,"item"):
  try:return jsonable(x.item())
  except ValueError:pass
 if isinstance(x,float):
  import math
  return x if math.isfinite(x) else None
 if isinstance(x,(str,int,bool,type(None))):return x
 return repr(x)
def allocated_gpu_guard():
 import re
 job=os.environ.get("SLURM_JOB_ID")
 if not job:raise RuntimeError("Slurm allocation is mandatory")
 raw=subprocess.check_output(["scontrol","show","job","-o",job],text=True)
 # Numeric array masters can return sibling records as well as the real job.
 selected=[line for line in raw.splitlines() if re.search(r"(?:^|\s)JobId="+re.escape(job)+r"(?:\s|$)",line)]
 if len(selected)!=1:raise RuntimeError("Actual Slurm JobId scheduler record is absent or ambiguous")
 scheduler_record=selected[0]
 tres=re.findall(r"(?:^|\s)(?:AllocTRES|TRES)=([^\s]+)",scheduler_record)
 counts=[]
 for value in tres:
  for token in value.split(","):
   if token.startswith("gres/gpu="):counts.append(int(token.split("=",1)[1]))
 if not counts or any(n!=1 for n in counts):raise RuntimeError("Exactly one actually allocated GPU required; hardware visibility is insufficient")
 if "JobState=RUNNING" not in scheduler_record:raise RuntimeError("Inference job must be RUNNING")
 return {"slurm_job_id":job,"actually_allocated_gpu_count":1,"scontrol_job":raw,"selected_scheduler_record":scheduler_record,"environment":{k:os.environ.get(k) for k in ["CUDA_VISIBLE_DEVICES","SLURM_JOB_GPUS","SLURM_STEP_GPUS"]}}
def append_stream(p,obj):
 obj=jsonable(obj)
 with open(p,"a") as f:
  f.write(json.dumps(obj,ensure_ascii=False,separators=(",",":"))+"\n");f.flush();os.fsync(f.fileno())
def checked_small_record(v):
 p=inside_project(v["path"])
 if p.stat().st_size!=v["bytes"] or sha(p)!=v["sha256"]:raise RuntimeError("Pinned small input changed")
 return p
def load_method_inputs(config,expected_sha,target_manifest):
 p=inside_project(config)
 if sha(p)!=expected_sha:raise RuntimeError("Method config mismatch")
 cfg=json.loads(p.read_text())
 if cfg["schema"]!="matched_method_adapter.v1":raise RuntimeError("Unknown method adapter schema")
 target_path=inside_project(target_manifest)
 expected_target=os.environ.get("BENCHMARK_TARGET_MANIFEST_SHA256")
 if expected_target and sha(target_path)!=expected_target:raise RuntimeError("Prepared target manifest mismatch")
 target=json.loads(target_path.read_text())
 if target["schema"]!="prepared_benchmark_target.v1":raise RuntimeError("Prepared target schema required")
 checked_small_record(target["target_pdb"])
 if len(target["target_sequence"])!=target["residue_count"]:raise RuntimeError("Prepared target sequence length mismatch")
 if cfg["binder_length"]!=65:raise RuntimeError("Fixed 65-aa benchmark required")
 for v in cfg["input_receipts"]:checked_small_record(v)
 return cfg,target,p,target_path
def method_native_metrics(ref_pdb,pred_pdb,ref_target_chain,ref_binder_chain,pred_target_chain="A",pred_binder_chain="B"):
 import numpy as np
 from Bio.PDB import PDBParser
 parser=PDBParser(QUIET=True)
 ref=parser.get_structure("reference",ref_pdb)[0];pred=parser.get_structure("prediction",pred_pdb)[0]
 def ca(chain):return np.asarray([r["CA"].coord for r in chain if r.id[0]==" " and "CA" in r],dtype=float)
 rt,rb=ca(ref[ref_target_chain]),ca(ref[ref_binder_chain]);pt,pb=ca(pred[pred_target_chain]),ca(pred[pred_binder_chain])
 if rt.shape!=pt.shape or rb.shape!=pb.shape or rb.shape!=(65,3):raise RuntimeError("Native AF2/RFD chain identity or length mismatch")
 rc,pc=rt.mean(0),pt.mean(0);u,s,vt=np.linalg.svd((pt-pc).T@(rt-rc))
 flip=np.eye(3);flip[-1,-1]=np.linalg.det(u@vt);rotation=u@flip@vt
 target_rmsd=float(np.sqrt(np.mean(np.sum(((pt-pc)@rotation+rc-rt)**2,axis=1))))
 binder_rmsd=float(np.sqrt(np.mean(np.sum(((pb-pc)@rotation+rc-rb)**2,axis=1))))
 return {"target_ca_rmsd":target_rmsd,"binder_backbone_rmsd":binder_rmsd}
def generation_gate():
 """Do not start a further inference step once the frozen generation deadline passed."""
 import time
 deadline=os.environ.get("BENCHMARK_GENERATION_DEADLINE_EPOCH")
 if deadline is None or time.time()<float(deadline):return
 # The runner owns the hard cutoff and termination classification.
 # Wait without another model step until its process-group cleanup arrives.
 release=float(os.environ.get("BENCHMARK_ALLOCATION_DEADLINE_EPOCH",deadline))
 while time.time()<release:time.sleep(.05)
 raise TimeoutError("Allocation deadline elapsed after generation stopped")
def sanitize_template_positions(inputs):
 import jax.numpy as jnp
 if "template_all_atom_positions" in inputs:
  mask=inputs["template_all_atom_mask"]
  inputs["template_all_atom_positions"]=jnp.where(mask[...,None]>0,inputs["template_all_atom_positions"],0)
  # Monomer TemplateEmbedding reads pseudo-beta arrays directly; atom masking alone is insufficient.
  if "template_pseudo_beta_mask" in inputs:
   valid=jnp.any(mask>0,axis=-1)
   inputs["template_pseudo_beta_mask"]=jnp.where(valid,inputs["template_pseudo_beta_mask"],0)
   inputs["template_pseudo_beta"]=jnp.where(valid[...,None],inputs["template_pseudo_beta"],0)
def durable_json(path,obj):
 """Publish an observation only after its bytes are durable."""
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 temporary=path.with_name(path.name+".partial")
 if path.exists() or temporary.exists():raise FileExistsError(path)
 with open(temporary,"x") as handle:
  handle.write(json.dumps(jsonable(obj),ensure_ascii=False,indent=2)+"\n")
  handle.flush();os.fsync(handle.fileno())
 os.replace(temporary,path)
 directory=os.open(path.parent,os.O_RDONLY)
 try:os.fsync(directory)
 finally:os.close(directory)
def save_native_confidence(model,attempt,observation_id,method,target_sequence,binder_sequence,context):
 """Read-only after-predict capture: no model call, seed draw or state update."""
 import time
 import numpy as np
 if not observation_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in observation_id):
  raise RuntimeError("Unsafe native observation ID")
 directory=inside_project(attempt)/"native_confidence";directory.mkdir(parents=True,exist_ok=True)
 aux=model.aux;query=target_sequence+binder_sequence;L=len(query)
 arrays={key:np.array(aux[key],copy=True) for key in ["pae","plddt","aatype","i_ptm","ptm"]}
 if arrays["pae"].shape!=(L,L) or arrays["plddt"].shape!=(L,) or arrays["aatype"].shape!=(L,):
  raise RuntimeError("Actual native confidence full-query shapes rejected")
 if not all(np.isfinite(arrays[key]).all() for key in arrays):
  raise RuntimeError("Actual native confidence contains nonfinite values")
 alphabet="ARNDCQEGHILKMFPSTWYV"
 actual="".join(alphabet[int(n)] if 0<=int(n)<20 else "X" for n in arrays["aatype"])
 if actual!=query:raise RuntimeError("Actual native AF2 aatype query differs from declared full query")
 names=list(model._model_names)
 indices=[int(n) for n in aux["log"]["models"]]
 model_names=[names[n] for n in indices]
 if model_names!=context["model_names"]:raise RuntimeError("Actual native AF2 model identity differs from predict request")
 npz_path=directory/(observation_id+".npz");temporary=npz_path.with_name(npz_path.name+".partial")
 if npz_path.exists() or temporary.exists():raise FileExistsError(npz_path)
 with open(temporary,"xb") as handle:
  np.savez(handle,**arrays);handle.flush();os.fsync(handle.fileno())
 os.replace(temporary,npz_path)
 # Official save_pdb serializes the supplied aux without running a model or changing it.
 pdb_path=directory/(observation_id+".pdb")
 pdb_text=model.save_pdb(filename=None,get_best=False,aux=aux)
 with open(pdb_path,"x") as handle:
  handle.write(pdb_text);handle.flush();os.fsync(handle.fileno())
 owner=getattr(getattr(model,"key",None),"__self__",None)
 seed=getattr(owner,"seed",None);rng_key=getattr(owner,"key",None)
 record={"schema":"native_af2_observation.v1","status":"ACTUAL_PREDICT_RETURN_OBSERVED",
  "observation_only":True,"method":method,"observation_id":observation_id,
  "task_id":os.environ.get("BENCHMARK_TASK_ID"),"attempt_dir":str(inside_project(attempt)),
  "attempt_index":int(Path(attempt).name) if Path(attempt).name.isdecimal() else os.environ.get("BENCHMARK_ATTEMPT_INDEX"),
  "replicate_seed":os.environ.get("BENCHMARK_REPLICATE_SEED"),
  "protocol_sha256":os.environ.get("BENCHMARK_PROTOCOL_SHA256"),"plan_sha256":os.environ.get("BENCHMARK_PLAN_SHA256"),
  "method_config_sha256":os.environ.get("BENCHMARK_METHOD_CONFIG_SHA256"),
  "target_manifest_sha256":os.environ.get("BENCHMARK_TARGET_MANIFEST_SHA256"),
  "target_sequence":target_sequence,"binder_sequence":binder_sequence,"actual_full_query":actual,
  "target_length":len(target_sequence),"binder_length":len(binder_sequence),
  "array_keys":{"pae_angstrom":"pae","plddt_fraction":"plddt","actual_query_aatype":"aatype","raw_i_ptm":"i_ptm","raw_ptm":"ptm"},
  "units":{"pae":"angstrom; official get_pae output, no scale transformation",
           "plddt":"fraction 0-1; official get_plddt output, no scale transformation","i_ptm":"raw official aux i_ptm"},
  "actual_model_indices":indices,"actual_model_names":model_names,"native_aux_log":jsonable(aux["log"]),
  "actual_model_rng_seed":jsonable(seed),"actual_model_rng_key_after_predict":jsonable(rng_key),
  "arrays":{"path":str(npz_path),"bytes":npz_path.stat().st_size,"sha256_policy":"CPU collector computes SHA-256"},
  "raw_pdb":{"path":str(pdb_path),"bytes":pdb_path.stat().st_size,"sha256_policy":"CPU collector computes SHA-256",
             "source":"official save_pdb(filename=None,get_best=False,aux=same_actual_predict_aux)"},
  "context":jsonable(context),"completed_at_epoch":time.time()}
 path=directory/(observation_id+".json");durable_json(path,record)
 append_stream(inside_project(attempt)/"native_confidence.jsonl",
  {"observation_id":observation_id,"method":method,"path":str(path),"bytes":path.stat().st_size,
   "completed_at_epoch":time.time(),"context":context})
 return {"path":str(path),"bytes":path.stat().st_size,"observation_id":observation_id}
def observed_native_predict_call(model,observer,operation):
 """Wrap a specific official model only for the operation; preserve return/API/state."""
 import functools
 had_instance_attribute="predict" in vars(model);old_instance=vars(model).get("predict")
 original=model.predict
 @functools.wraps(original)
 def observed(*args,**kwargs):
  value=original(*args,**kwargs)
  observer(args,kwargs)
  return value
 model.predict=observed
 try:return operation()
 finally:
  if had_instance_attribute:model.predict=old_instance
  else:del model.predict
def native_af2_batch(config,config_sha,target_manifest,attempt_dir):
 import math,time
 import numpy as np
 import jax
 from colabdesign import mk_afdesign_model
 allocation=allocated_gpu_guard()
 cfg,target,_,_=load_method_inputs(config,config_sha,target_manifest)
 attempt=inside_project(attempt_dir);data=json.loads((attempt/"rf_native_inputs.json").read_text())
 af=cfg["native_af2"]
 if af["model_name"]!="model_1_ptm" or af["use_multimer"] is not False or af["use_initial_guess"] is not True:raise RuntimeError("Frozen single PTM RF-initial-guess and target-only-template native validator required")
 if len([d for d in jax.devices() if d.platform=="gpu"])!=1:raise RuntimeError("Exactly one JAX-visible GPU required")
 global _NATIVE_AF2_MODEL
 cold=_NATIVE_AF2_MODEL is None;ctor_start=time.time()
 if cold:
  _NATIVE_AF2_MODEL=mk_afdesign_model(protocol="binder",use_multimer=False,use_initial_guess=True,use_initial_atom_pos=False,pre_callback=sanitize_template_positions,
                        num_recycles=int(af["num_recycles"]),data_dir=af["params_dir"],model_names=["model_1_ptm"])
 model=_NATIVE_AF2_MODEL
 append_stream(attempt/"stage_timing.jsonl",{"stage":"native_af2_model_construction","cold":cold,"seconds":time.time()-ctor_start,"completed_at_epoch":time.time()})
 model.prep_inputs(pdb_filename=data["backbone_pdb"],chain=target["rfd_output_target_chain"],binder_chain=target["rfd_binder_chain"],binder_len=65,use_binder_template=False,
                   rm_target_seq=af["rm_target_seq"],rm_target_sc=af["rm_target_sc"],seed=int(data["seed"]))
 for row in data["sequences"]:
  generation_gate()
  model.predict(seq=row["sequence"],models=[0],num_recycles=int(af["num_recycles"]),verbose=False)
  path=attempt/"native_af2"/(row["sequence_record_id"]+".pdb");path.parent.mkdir(exist_ok=True)
  model.save_pdb(str(path))
  confidence=save_native_confidence(model,attempt,row["sequence_record_id"],"rf_diffusion",target["target_sequence"],row["sequence"],
   {"sequence_record_id":row["sequence_record_id"],"model_names":["model_1_ptm"],"attempt_seed":int(data["seed"]),
    "predict_seed_argument":None,"num_recycles":int(af["num_recycles"]),"official_native_pdb_path":str(path),
    "backbone_pdb":data["backbone_pdb"],"target_manifest_path":str(target_manifest),"target_chain":"A","binder_chain":"B"})
  log=jsonable(model.aux["log"])
  pae=np.asarray(model.aux["pae"],dtype=float);T=int(target["residue_count"])
  if pae.shape!=(T+65,T+65) or not np.isfinite(pae).all():raise RuntimeError("Native AF2 PAE matrix unavailable or malformed")
  cross=np.concatenate([pae[:T,T:].ravel(),pae[T:,:T].ravel()])
  metrics={"binder_plddt":float(np.asarray(model.aux["plddt"])[-65:].mean()),
           "cross_pae_mean_angstrom":float(cross.mean()),
           "global_iptm":float(log["i_ptm"]),
           **method_native_metrics(data["backbone_pdb"],str(path),target["rfd_output_target_chain"],target["rfd_binder_chain"],target["common_target_chain"],target["common_binder_chain"])}
  criteria=cfg["native_af2"]["criteria"]
  accepted=True
  for c in criteria:
   value=metrics.get(c["metric"])
   if value is None or not math.isfinite(value):accepted=None;break
   if c["op"]=="ge":good=value>=c["threshold"]
   elif c["op"]=="le":good=value<=c["threshold"]
   else:raise RuntimeError("Only explicit ge/le native criteria supported")
   accepted=accepted and good
  update={"sequence_record_id":row["sequence_record_id"],"internal_acceptance":accepted,
          "native_score":metrics["cross_pae_mean_angstrom"],"native_score_name":"native_single_AF2_PTM_pae_interaction",
          "completed_at_epoch":time.time(),"native_metrics":metrics,"native_model":"model_1_ptm",
          "native_structure_path":str(path),"native_confidence":confidence,"binder_template":False,"initial_guess":True,
          "initial_guess_source":data["backbone_pdb"],"initial_atom_position":False,
          "target_template_source":data["backbone_pdb"],"target_source_chain":target["rfd_output_target_chain"],
          "rfd_reference_target_chain":target["rfd_output_target_chain"],"rfd_reference_binder_chain":target["rfd_binder_chain"]}
  append_stream(attempt/"native_screening.jsonl",update)
def bindcraft_one_attempt(cfg,target,attempt,seed,target_manifest=None):
 import functools,random,runpy,time
 import numpy as np
 vendor=ROOT/"vendor/BindCraft"
 sys.path.insert(0,str(vendor));import functions
 advanced=json.loads(checked_small_record(cfg["bindcraft"]["advanced"]).read_text())
 filters=checked_small_record(cfg["bindcraft"]["filters"])
 # These retention/stopping settings only define one observable engineering attempt.
 advanced.update({"af_params_dir":str(ROOT/"assets/colabfold"),"dssp_path":str(vendor/"functions/dssp"),
                  "dalphaball_path":str(vendor/"functions/DAlphaBall.gcc"),"save_mpnn_fasta":True,
                  "remove_unrelaxed_trajectory":False,"remove_unrelaxed_complex":False,
                  "remove_binder_monomer":False,"enable_rejection_check":False,"max_trajectories":False})
 settings={"design_path":str(attempt/"generated"),"binder_name":"attempt",
           "starting_pdb":target["target_pdb"]["path"],"chains":target["input_target_chain"],
           "target_hotspot_residues":",".join(str(x) for x in target["hotspots"]),
           "lengths":[65,65],"number_of_final_designs":100000}
 settings_path=attempt/"settings.json";advanced_path=attempt/"advanced.json"
 settings_path.write_text(json.dumps(settings,indent=2)+"\n");advanced_path.write_text(json.dumps(advanced,indent=2)+"\n")
 events=attempt/"bindcraft_native_events.jsonl";streams=attempt/"sequences.jsonl";updates=attempt/"native_screening.jsonl"
 state={"started":0,"raw_by_sequence":{},"native_by_design":{},"native_updates":0,"confidence_by_design":{}}
 lineage=os.environ.get("BENCHMARK_TASK_ID","task")+"/attempt_"+os.environ.get("BENCHMARK_ATTEMPT_INDEX","0")+"/trajectory"
 def event(kind,**kw):append_stream(events,{"event":kind,"completed_at_epoch":time.time(),**kw})
 attempt_seed=int(seed)
 original_seed=np.random.seed;entropy=np.random.default_rng(attempt_seed)
 originals={};old_argv=list(sys.argv);old_cwd=os.getcwd()
 def controlled_seed(seed=None):
  # Keep the native numpy API: ColabDesign calls np.random.seed(seed=seed).
  if seed is None:
   seed=int(entropy.integers(0,2**31-1));event("deterministic_entropy_seed",seed=seed)
  return original_seed(seed)
 np.random.seed=controlled_seed;original_seed(attempt_seed);random.seed(attempt_seed)
 def wrap(name,before=None,after=None,invoke=None):
  original=getattr(functions,name);originals[name]=original
  @functools.wraps(original)
  def wrapped(*a,**kw):
   if before:before(a,kw)
   stage_start=time.time();v=invoke(original,a,kw) if invoke else original(*a,**kw)
   append_stream(attempt/"stage_timing.jsonl",{"stage":"official_"+name,"seconds":time.time()-stage_start,"completed_at_epoch":time.time()})
   if after:after(a,kw,v)
   return v
  setattr(functions,name,wrapped)
 original_check=functions.check_n_trajectories;originals["check_n_trajectories"]=original_check
 def one_trajectory_only(design_paths,advanced_settings):
  return True if state["started"]>=1 else original_check(design_paths,advanced_settings)
 functions.check_n_trajectories=one_trajectory_only
 def traj_start(a,k):
  state["started"]+=1
  if hasattr(functions,"pr"):
   functions.pr.rosetta.numeric.random.rg().set_seed(int(a[5]))
   event("rosetta_rng_seeded",seed=int(a[5]))
  event("trajectory_started",design=a[0],seed=a[5],length=a[4])
 def traj_done(a,k,v):event("trajectory_complete",design=a[0],sequence=v.get_seq(get_best=True)[0],native_termination=v.aux["log"].get("terminate"),native_logs=jsonable(v._tmp["best"]["aux"]["log"]))
 wrap("binder_hallucination",traj_start,traj_done)
 def mpnn_done(a,k,v):
  for i,raw in enumerate(v["seq"]):
   sequence=str(raw)[-65:]
   ident=hashlib.sha256((lineage+"/"+str(i)+"/"+sequence).encode()).hexdigest()[:24]
   row={"sequence":sequence,"sequence_record_id":ident,"lineage_id":lineage,"internal_acceptance":None,
        "native_score":None,"native_score_name":"native_BindCraft_average_AF2_iptm","completed_at_epoch":time.time(),
        "native_mpnn_score":float(v["score"][i]),"native_mpnn_seq_recovery":float(v["seqid"][i]),"mpnn_index":i}
   append_stream(streams,row);state["raw_by_sequence"].setdefault(sequence,[]).append(ident)
  event("mpnn_raw_batch_complete",n=len(v["seq"]),source_pdb=a[0],native_sampling_api="sample(num=1,batch=20); one JIT/vmap pool converted to numpy before return",complete_pool_returned_at_epoch=time.time())
 wrap("mpnn_gen_sequence",after=mpnn_done)
 def af_observed_invoke(original,a,k):
  model,sequence,design=a[:3];confidence=state["confidence_by_design"].setdefault(design,[])
  def observer(args,kwargs):
   indices=kwargs.get("models")
   if indices is None and len(args)>4:indices=args[4]
   if indices is None:raise RuntimeError("Native BindCraft explicit validation model absent")
   model_names=[model._model_names[int(n)] for n in indices]
   ident="bc_"+design+"_"+str(len(confidence))
   item=save_native_confidence(model,attempt,ident,"bindcraft",target["target_sequence"],sequence,
    {"native_design":design,"sequence_record_ids":state["raw_by_sequence"].get(sequence,[]),"model_names":model_names,
     "attempt_seed":attempt_seed,"predict_seed_argument":kwargs.get("seed"),"num_recycles":kwargs.get("num_recycles"),
     "official_native_pdb_path":str(Path(a[10]["MPNN"])/(design+"_model"+str(int(indices[0])+1)+".pdb")),
     "target_manifest_path":str(target_manifest) if target_manifest is not None else None,
     "target_manifest_sha256":os.environ.get("BENCHMARK_TARGET_MANIFEST_SHA256"),
     "target_chain":"A","binder_chain":"B","capture_scope":"official complex PTM predict including native filter rejection"})
   confidence.append(item);event("native_confidence_saved",design=design,confidence=item)
  return observed_native_predict_call(model,observer,lambda:original(*a,**k))
 def af_done(a,k,v):
  sequence,design=a[1],a[2];state["native_by_design"][design]={"sequence":sequence,"native_af2_pass":bool(v[1]),"statistics":jsonable(v[0])}
  event("native_af2_filter_complete",design=design,sequence=sequence,native_af2_pass=bool(v[1]),statistics=jsonable(v[0]),confidence_records=state["confidence_by_design"].get(design,[]))
  if not v[1]:
   for ident in state["raw_by_sequence"].get(sequence,[]):
    append_stream(updates,{"sequence_record_id":ident,"internal_acceptance":False,"native_score":None,
                  "native_score_name":"native_BindCraft_average_AF2_iptm","completed_at_epoch":time.time(),"reason":"Native AF2 filter rejected","native_confidence":state["confidence_by_design"].get(design,[])})
    state["native_updates"]+=1
 wrap("predict_binder_complex",after=af_done,invoke=af_observed_invoke)
 def filters_done(a,k,v):
  values=dict(zip(a[1],a[0]));design=values["Design"];sequence=values["Sequence"];score=values.get("Average_i_pTM")
  if score is not None:score=float(score)
  passed=v is True
  event("native_final_filter_complete",design=design,result=v,filter_values=jsonable(values))
  for ident in state["raw_by_sequence"].get(sequence,[]):
   append_stream(updates,{"sequence_record_id":ident,"internal_acceptance":passed,"native_score":score,
                "native_score_name":"native_BindCraft_average_AF2_iptm","completed_at_epoch":time.time(),"native_design":design,"native_filter_result":jsonable(v),"native_confidence":state["confidence_by_design"].get(design,[])})
  state["native_updates"]+=1
 wrap("check_filters",after=filters_done)
 event("instrumented_official_start",root_seed=seed,official_entry=str(vendor/"bindcraft.py"),
       modifications=["one trajectory per external attempt","retain unfiltered outputs","deterministic entropy for seed(None)","Rosetta RNG fixed to trajectory seed","record-only wrappers","durable actual native AF2 confidence observation after predict return"])
 sys.argv=[str(vendor/"bindcraft.py"),"--settings",str(settings_path),"--advanced",str(advanced_path),"--filters",str(filters)]
 try:
  os.chdir(vendor);runpy.run_path(str(vendor/"bindcraft.py"),run_name="__main__")
  event("official_one_attempt_complete",native_updates=state["native_updates"])
  return state
 finally:
  np.random.seed=original_seed;sys.argv=old_argv;os.chdir(old_cwd)
  for name,value in originals.items():setattr(functions,name,value)
def validate_rfd_output(output_pdb,trb_path,target):
 """Verify official Sampler PDB identity using TRB full-complex indices.

 receptor_con_hal_idx0 is receptor-local, while complex_con_hal_idx0 addresses
 the binder-first full output. ContigMap hal chain labels are abstract; the
 pinned Sampler preserves the source target chain and assigns new binder B.
 Final px0 is all-atom reconstructed, so target-coordinate differences are
 recorded, not silently overwritten or filtered by a posthoc tolerance.
 """
 import pickle
 import numpy as np
 from Bio.PDB import PDBParser
 from Bio.SeqUtils import seq1
 output_pdb=inside_project(output_pdb);trb_path=inside_project(trb_path)
 N=int(target["residue_count"]);length=65
 source_chain=target["input_target_chain"];target_chain=target["rfd_output_target_chain"];binder_chain=target["rfd_binder_chain"]
 if (source_chain,target_chain,binder_chain)!=("A","A","B"):
  raise RuntimeError("Prepared RFD physical mapping must match pinned Sampler: input target A, output target A, binder B")
 if target["rfd_contig"]!=f"A1-{N}/0 65-65":raise RuntimeError("Unexpected frozen target-plus-binder contig")
 parser=PDBParser(QUIET=True);native=parser.get_structure("rfd",output_pdb)[0]
 reference=parser.get_structure("target",target["target_pdb"]["path"])[0]
 chains={c.id:[r for r in c if r.id[0]==" "] for c in native}
 if set(chains)!={target_chain,binder_chain}:raise RuntimeError("RFD output chain set differs from prepared physical mapping")
 receptor=chains[target_chain];binder=chains[binder_chain]
 if len(receptor)!=N or "".join(seq1(r.resname) for r in receptor)!=target["target_sequence"]:
  raise RuntimeError("RFD output full target sequence/length rejected")
 if len(binder)!=length or "".join(seq1(r.resname) for r in binder)!="G"*length:
  raise RuntimeError("RFD output full de novo polyG binder rejected")
 if [r.id for r in receptor]!=[(" ",i+1," ") for i in range(N)] or [r.id for r in binder]!=[(" ",i+1," ") for i in range(length)]:
  raise RuntimeError("RFD output physical residue numbering rejected")
 # Only the current, project-owned official RFD attempt's TRB is unpickled.
 trb=pickle.loads(trb_path.read_bytes());refs=[tuple(x) for x in trb["receptor_con_ref_pdb_idx"]]
 expected=[("A",i+1) for i in range(N)]
 checks={"receptor_ref_pdb_exact":refs==expected,
  "complex_ref_pdb_equals_receptor":[tuple(x) for x in trb["complex_con_ref_pdb_idx"]]==expected,
  "receptor_local_hal_idx0_exact":np.array_equal(trb["receptor_con_hal_idx0"],np.arange(N)),
  "receptor_ref_idx0_exact":np.array_equal(trb["receptor_con_ref_idx0"],np.arange(N)),
  "complex_ref_idx0_exact":np.array_equal(trb["complex_con_ref_idx0"],np.arange(N)),
  "complex_full_hal_idx0_exact":np.array_equal(trb["complex_con_hal_idx0"],np.arange(length,length+N))}
 if not all(checks.values()):raise RuntimeError("RFD official TRB receptor/full-complex mapping rejected: "+repr(checks))
 all_res=[r for c in native for r in c if r.id[0]==" "];mapped=[all_res[int(i)] for i in trb["complex_con_hal_idx0"]]
 if [(r.parent.id,r.id[1]) for r in mapped]!=expected:
  raise RuntimeError("RFD TRB full indices do not map to physical output target A1-N")
 source=[reference[chain][int(index)] for chain,index in refs]
 if "".join(seq1(r.resname) for r in source)!=target["target_sequence"]:
  raise RuntimeError("RFD input target sequence differs from frozen query")
 for rs in [source,mapped,binder]:
  if any(atom not in r for r in rs for atom in ["N","CA","C","O"]):raise RuntimeError("RFD full backbone atom coverage rejected")
 src=np.asarray([r["CA"].coord for r in source],dtype=np.float64);dst=np.asarray([r["CA"].coord for r in mapped],dtype=np.float64)
 if not np.isfinite(src).all() or not np.isfinite(dst).all():raise RuntimeError("Nonfinite RFD fixed target coordinates")
 sc=src.mean(0);dc=dst.mean(0);u,sv,vt=np.linalg.svd((src-sc).T@(dst-dc));rotation=u@np.diag([1.,1.,np.linalg.det(u@vt)])@vt
 differences={a:[float(np.linalg.norm((r[a].coord-sc)@rotation+dc-d[a].coord)) for r,d in zip(source,mapped)] for a in ["N","CA","C","O"]}
 if not all(np.isfinite(v).all() for v in differences.values()):raise RuntimeError("Nonfinite RFD backbone audit")
 return {"schema":"rfd_output_identity.v1","status":"PASS","physical_target_chain":target_chain,"physical_binder_chain":binder_chain,
  "target_sequence":target["target_sequence"],"target_count":N,"binder_count":length,"strict_trb_checks":checks,
  "actual_target_ids":[[r.parent.id,r.id[1]] for r in mapped],"actual_binder_ids":[[r.parent.id,r.id[1]] for r in binder],
  "target_rigid_aligned_ca_rmsd_angstrom":float(np.sqrt(np.mean(np.sum(((src-sc)@rotation+dc-dst)**2,axis=-1)))),
  "target_rigid_aligned_backbone_max_displacement_angstrom":{k:max(v) for k,v in differences.items()},
  "coordinate_audit_role":"diagnostic only; no posthoc coordinate filter; official reconstructed target coordinates preserved",
  "mapping_semantics":"receptor hal_idx0 local; complex hal_idx0 full; actual physical chains from Sampler, not abstract ContigMap hal chains"}
def method_attempt(method,target_manifest,attempt_dir,seed,config,config_sha):
 import time
 cfg,target,cfgp,tp=load_method_inputs(config,config_sha,target_manifest)
 if cfg["method"]!=method:raise RuntimeError("Method differs from config")
 attempt=inside_project(attempt_dir);attempt.mkdir(parents=True,exist_ok=True)
 if (attempt/"attempt_result.json").exists() or (attempt/"sequences.jsonl").exists():raise FileExistsError("Attempt output already populated")
 started=time.time()
 try:
  if int(seed)<=0:raise RuntimeError("Explicit positive nonzero method seed required")
  allocation=allocated_gpu_guard()
  atomic(attempt/"allocated_gpu_receipt.json",allocation)
  if method=="bindcraft":
   state=bindcraft_one_attempt(cfg,target,attempt,int(seed),target_manifest=tp)
   status="COMPLETED" if state["raw_by_sequence"] else "SCIENTIFIC_REJECT"
   reason="One full official BindCraft trajectory completed" if state["raw_by_sequence"] else "Official trajectory rejected before ProteinMPNN"
  else:
   import torch
   if not torch.cuda.is_available() or torch.cuda.device_count()!=1:raise RuntimeError("Official RFD attempt requires exactly one CUDA-visible GPU")
   generated=attempt/"generated";generated.mkdir(exist_ok=True)
   prefix=generated/"backbone";output_pdb=Path(str(prefix)+"_"+str(seed)+".pdb")
   args=[sys.executable,str(ROOT/"vendor/RFdiffusion/scripts/run_inference.py"),
         "inference.input_pdb="+target["target_pdb"]["path"],"inference.output_prefix="+str(prefix),
         "inference.ckpt_override_path="+str(ROOT/"assets/rfdiffusion/Complex_base_ckpt.pt"),
         "inference.num_designs=1","inference.design_startnum="+str(seed),"inference.deterministic=True",
         "contigmap.contigs=["+target["rfd_contig"]+"]",
         "ppi.hotspot_res=["+",".join("A"+str(x) for x in target["hotspots"])+"]"]
   for k,v in cfg["rfd"]["overrides"].items():args.append(k+"="+str(v))
   stage_start=time.time()
   if _SESSION:resident_rfd(args[2:],attempt)
   else:subprocess.run(args,cwd=ROOT,check=True)
   append_stream(attempt/"stage_timing.jsonl",{"stage":"official_rfd_backbone","seconds":time.time()-stage_start,"completed_at_epoch":time.time(),"resident_process":bool(_SESSION)})
   if not output_pdb.is_file():raise RuntimeError("RFD complete backbone missing")
   identity=validate_rfd_output(output_pdb,output_pdb.with_suffix(".trb"),target)
   atomic(attempt/"rfd_output_identity.json",identity)
   mpnn=cfg["mpnn"];folder=generated/"mpnn"
   if mpnn["num_seq_per_target"]!=8 or mpnn["sampling_temp"]!=0.0001 or mpnn["use_soluble_model"] is not False:raise RuntimeError("Frozen RF comparator requires 8 original ProteinMPNN at T0.0001")
   omit=mpnn["omit_aas"]+("" if "X" in mpnn["omit_aas"] else "X")
   generation_gate()
   args=[sys.executable,str(ROOT/"vendor/ProteinMPNN/protein_mpnn_run.py"),"--pdb_path",str(output_pdb),
         "--pdb_path_chains",target["rfd_binder_chain"],"--out_folder",str(folder),
         "--num_seq_per_target","8","--batch_size",str(mpnn["batch_size"]),"--sampling_temp","0.0001",
         "--seed",str(seed),"--omit_AAs",omit,"--save_score","1"]
   fasta=folder/"seqs"/(output_pdb.stem+".fa");rows=[]
   lineage=os.environ.get("BENCHMARK_TASK_ID","task")+"/attempt_"+os.environ.get("BENCHMARK_ATTEMPT_INDEX","0")+"/backbone"
   def emit_mpnn_sequence(h,s):
    if len(s)!=65 or set(s)-set("ACDEFGHIKLMNPQRSTVWY"):raise RuntimeError("Native MPNN complete sequence malformed")
    ident=hashlib.sha256((lineage+"/"+str(len(rows))+"/"+s).encode()).hexdigest()[:24]
    row={"sequence":s,"lineage_id":lineage,"sequence_record_id":ident,"internal_acceptance":None,"native_score":None,
         "native_score_name":"native_single_AF2_PTM_pae_interaction","completed_at_epoch":time.time(),"mpnn_header":h,
         "completion_source":"official native FASTA completed sample write"}
    rows.append(row);append_stream(attempt/"sequences.jsonl",row)
   stage_start=time.time()
   resident_mpnn(args,fasta,emit_mpnn_sequence)
   append_stream(attempt/"stage_timing.jsonl",{"stage":"official_original_mpnn","seconds":time.time()-stage_start,"completed_at_epoch":time.time(),"resident_process":bool(_SESSION),"incremental_sequence_emission":True})
   header=None;sequence=[];verified_rows=[]
   def finish():
    if header is not None and "sample=" in header:
     s="".join(sequence)
     if len(s)!=65 or set(s)-set("ACDEFGHIKLMNPQRSTVWY"):raise RuntimeError("Native MPNN sequence malformed")
     verified_rows.append((header,s))
   for line in fasta.read_text().splitlines():
    if line.startswith(">"):finish();header=line[1:];sequence=[]
    else:sequence.append(line.strip())
   finish()
   if len(rows)!=8 or verified_rows!=[(r["mpnn_header"],r["sequence"]) for r in rows]:raise RuntimeError("Completed ProteinMPNN FASTA differs from incremental ledger or did not return 8 sequences")
   (attempt/"rf_native_inputs.json").write_text(json.dumps({"seed":int(seed),"backbone_pdb":str(output_pdb),"sequences":rows},indent=2)+"\n")
   import shlex
   environment=checked_small_record(cfg["native_af2"]["environment_script"])
   shell="source "+shlex.quote(str(environment))+"; exec python "+shlex.quote(str(Path(__file__).resolve()))+" native-af2-batch --config "+shlex.quote(str(cfgp))+" --config-sha256 "+shlex.quote(config_sha)+" --target-manifest "+shlex.quote(str(tp))+" --attempt-dir "+shlex.quote(str(attempt))
   stage_start=time.time()
   if _SESSION:resident_native_af2(cfgp,config_sha,tp,attempt)
   else:subprocess.run(["bash","-c",shell],cwd=ROOT,check=True)
   append_stream(attempt/"stage_timing.jsonl",{"stage":"native_af2_full_batch","seconds":time.time()-stage_start,"completed_at_epoch":time.time(),"resident_process":bool(_SESSION)})
   status="COMPLETED";reason="One RFD backbone, eight original ProteinMPNN sequences and all eight native single-model AF2 validations completed"
  result={"status":status,"reason":reason,"method":method,"seed":int(seed),"started_at_epoch":started,
          "completed_at_epoch":time.time(),"config_path":str(cfgp),"config_sha256":config_sha,
          "target_manifest_path":str(tp),"target_id":target["target_id"],
          "scope":"Engineering completion only; no shared-evaluator or experimental acceptance"}
  atomic(attempt/"attempt_result.json",result)
 except Exception as e:
  result={"status":"ENGINEERING_FAILURE","reason":repr(e),"method":method,"seed":int(seed),"completed_at_epoch":time.time()}
  if not (attempt/"attempt_result.json").exists():atomic(attempt/"attempt_result.json",result)
  raise

def resident_rfd(overrides,attempt):
 """Official main loop, with its supported Sampler.initialize model reuse."""
 import importlib.util,time
 import hydra
 from hydra.core.hydra_config import HydraConfig
 from rfdiffusion.inference import utils as iu
 global _RFD_SAMPLER
 cache=STEP/"work/rfd_schedules";cache.mkdir(parents=True,exist_ok=True)
 overrides=list(overrides)+["inference.schedule_directory_path="+str(cache)]
 with hydra.initialize_config_dir(config_dir=str(ROOT/"vendor/RFdiffusion/config/inference"),version_base=None):
  conf=hydra.compose(config_name="base",overrides=overrides,return_hydra_config=True)
 HydraConfig.instance().set_config(conf)
 from omegaconf import OmegaConf
 conf=OmegaConf.masked_copy(conf,[key for key in conf if key!="hydra"])
 name="_official_rfd_entry"
 if name not in sys.modules:
  spec=importlib.util.spec_from_file_location(name,ROOT/"vendor/RFdiffusion/scripts/run_inference.py")
  mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
 mod=sys.modules[name];original=iu.sampler_selector
 def selector(c):
  global _RFD_SAMPLER
  cold=_RFD_SAMPLER is None;started=time.time()
  if cold:_RFD_SAMPLER=original(c)
  else:_RFD_SAMPLER.initialize(c)
  append_stream(attempt/"stage_timing.jsonl",{"stage":"official_rfd_sampler_initialize","cold":cold,"seconds":time.time()-started,"completed_at_epoch":time.time()})
  return _RFD_SAMPLER
 iu.sampler_selector=selector
 try:mod.main.__wrapped__(conf)
 finally:iu.sampler_selector=original
def resident_mpnn(args,fasta_path=None,on_record=None):
 """Observe official complete FASTA sample writes without altering bytes or sampling."""
 import builtins,runpy
 vendor=ROOT/"vendor/ProteinMPNN";sys.path.insert(0,str(vendor))
 old_argv=list(sys.argv);old_cwd=os.getcwd();original_open=builtins.open
 expected=Path(fasta_path).resolve() if fasta_path is not None else None
 class ObservedWriter:
  def __init__(self,handle):self.handle=handle;self.tail="";self.header=None
  def __getattr__(self,key):return getattr(self.handle,key)
  def __enter__(self):self.handle.__enter__();return self
  def __exit__(self,*args):return self.handle.__exit__(*args)
  def write(self,value):
   written=self.handle.write(value)
   self.tail+=value
   while "\n" in self.tail:
    line,self.tail=self.tail.split("\n",1)
    if line.startswith(">"):self.header=line[1:]
    elif self.header is not None and "sample=" in self.header and line:
     on_record(self.header,line.strip())
   return written
 def observe_open(file,mode="r",*a,**kw):
  handle=original_open(file,mode,*a,**kw)
  if expected is not None and on_record is not None and isinstance(file,(str,os.PathLike)) and Path(file).resolve()==expected and "w" in mode:
   return ObservedWriter(handle)
  return handle
 try:
  builtins.open=observe_open;sys.argv=args[1:];os.chdir(ROOT);runpy.run_path(args[1],run_name="__main__")
 finally:builtins.open=original_open;sys.argv=old_argv;os.chdir(old_cwd)
def wait_ready(directory,process):
 import time
 deadline=float(os.environ["BENCHMARK_ALLOCATION_DEADLINE_EPOCH"])
 while not (directory/"READY.json").is_file():
  if process.poll() is not None:raise RuntimeError("Native AF2 resident session exited before readiness")
  if time.time()>=deadline:raise RuntimeError("Budget elapsed during native session initialization")
  time.sleep(.1)
def resident_native_af2(config,config_sha,target_manifest,attempt):
 import shlex,time
 global _NATIVE_CHILD,_NATIVE_COUNTER
 directory=inside_project(_SESSION["session_dir"])/"native_af2_session"
 if _NATIVE_CHILD is None:
  environment=checked_small_record(json.loads(config.read_text())["native_af2"]["environment_script"])
  shell="source "+shlex.quote(str(environment))+"; exec python "+shlex.quote(str(Path(__file__).resolve()))+" native-af2-session --session-dir "+shlex.quote(str(directory))+" --config "+shlex.quote(str(config))+" --config-sha256 "+shlex.quote(config_sha)+" --target-manifest "+shlex.quote(str(target_manifest))
  _NATIVE_CHILD=subprocess.Popen(["bash","-c",shell],cwd=ROOT)
  wait_ready(directory,_NATIVE_CHILD)
 ident=f"{_NATIVE_COUNTER:06d}";_NATIVE_COUNTER+=1
 request={"action":"native-af2-batch","request_id":ident,"attempt_dir":str(attempt),
          "attempt_index":int(attempt.name),"replicate_seed":os.environ.get("BENCHMARK_REPLICATE_SEED"),
          "task_id":os.environ.get("BENCHMARK_TASK_ID"),"protocol_id":os.environ.get("BENCHMARK_PROTOCOL_ID"),
          "method_config_sha256":config_sha,"target_manifest_sha256":sha(target_manifest),
          "protocol_sha256":_SESSION["protocol_sha256"],"plan_sha256":_SESSION["plan_sha256"],
          "allocation_deadline_epoch":float(os.environ["BENCHMARK_ALLOCATION_DEADLINE_EPOCH"]),
          "generation_deadline_epoch":float(os.environ.get("BENCHMARK_GENERATION_DEADLINE_EPOCH",os.environ["BENCHMARK_ALLOCATION_DEADLINE_EPOCH"]))}
 atomic(directory/"requests"/(ident+".json"),request)
 response=directory/"responses"/(ident+".json");deadline=request["allocation_deadline_epoch"]
 while not response.is_file():
  if _NATIVE_CHILD.poll() is not None:raise RuntimeError("Native AF2 resident session terminated")
  if time.time()>=deadline:raise RuntimeError("Budget elapsed during native AF2")
  time.sleep(.1)
 result=json.loads(response.read_text())
 if result["status"]!="COMPLETE":raise RuntimeError(result.get("reason","Native AF2 resident session failed"))
def validate_session_request(request,frozen):
 for key in ["method_config_sha256","target_manifest_sha256","protocol_sha256","plan_sha256"]:
  if request.get(key)!=frozen[key]:raise RuntimeError("Session request changed frozen "+key)
 inside_project(request["attempt_dir"])
def method_session(method,target_manifest,session_dir,config,config_sha,native_only=False):
 import time,traceback
 global _SESSION
 cfg,target,cfgp,tp=load_method_inputs(config,config_sha,target_manifest)
 if not native_only and cfg["method"]!=method:raise RuntimeError("Session method differs from frozen config")
 allocation=allocated_gpu_guard();directory=inside_project(session_dir);directory.mkdir(parents=True,exist_ok=True)
 for name in ["requests","responses"]:(directory/name).mkdir(exist_ok=True)
 if (directory/"READY.json").exists():raise FileExistsError("Session already initialized")
 started=time.time()
 _SESSION={"session_dir":str(directory),"protocol_sha256":os.environ.get("BENCHMARK_PROTOCOL_SHA256"),
           "plan_sha256":os.environ.get("BENCHMARK_PLAN_SHA256")}
 frozen={"schema":"paired-budget-session-v1","status":"READY","method":method,"method_config_sha256":config_sha,
         "target_manifest_sha256":sha(tp),**{k:_SESSION[k] for k in ["protocol_sha256","plan_sha256"]},
         "pid":os.getpid(),"slurm_job_id":os.environ["SLURM_JOB_ID"],"initialized_at_epoch":None}
 if native_only:
  import jax
  from colabdesign import mk_afdesign_model
  if len([d for d in jax.devices() if d.platform=="gpu"])!=1:raise RuntimeError("Native resident AF2 requires exactly one actual JAX GPU backend")
 elif method=="bindcraft":
  sys.path.insert(0,str(ROOT/"vendor/BindCraft"));import functions
  import jax
  if len([d for d in jax.devices() if d.platform=="gpu"])!=1:raise RuntimeError("BindCraft session requires exactly one actual JAX GPU backend")
 else:
  import torch
  import rfdiffusion
  sys.path.insert(0,str(ROOT/"vendor/ProteinMPNN"));import protein_mpnn_utils
  if not torch.cuda.is_available() or torch.cuda.device_count()!=1:raise RuntimeError("RFD session requires exactly one actual CUDA backend")
 frozen["cuda_visible_devices"]=os.environ.get("CUDA_VISIBLE_DEVICES")
 frozen["visible_gpu_count"]=1
 frozen["initialized_at_epoch"]=time.time()
 atomic(directory/"initialization.json",{"status":"RESIDENT_IMPORTS_COMPLETE","method":method,"seconds":time.time()-started,
            "allocation":allocation,"config":rec(cfgp),"target_manifest":rec(tp),"source_entry":rec(Path(__file__).resolve())})
 atomic(directory/"READY.json",frozen)
 done=set()
 while True:
  deadline=float(os.environ["BENCHMARK_ALLOCATION_DEADLINE_EPOCH"])
  if time.time()>=deadline:return
  requests=sorted(p for p in (directory/"requests").glob("*.json") if p.name not in done)
  if not requests:time.sleep(.1);continue
  for path in requests:
   generation_gate()
   request=json.loads(path.read_text());ident=str(request["request_id"])
   response=directory/"responses"/(path.stem+".json")
   try:
    if ident!=path.stem:raise RuntimeError("Session request id does not match filename")
    validate_session_request(request,frozen)
    if native_only and request["action"]!="native-af2-batch":raise RuntimeError("Native session action mismatch")
    if not native_only and request["action"]!="method-attempt":raise RuntimeError("Method session action mismatch")
    allocation_request=float(request["allocation_deadline_epoch"])
    if allocation_request!=deadline:raise RuntimeError("Session allocation deadline changed")
    generation_deadline=float(os.environ.get("BENCHMARK_GENERATION_DEADLINE_EPOCH",deadline))
    generation_request=float(request.get("generation_deadline_epoch",request.get("deadline_epoch",generation_deadline)))
    if generation_request!=generation_deadline:raise RuntimeError("Session generation deadline changed")
    for field,env in [("attempt_index","BENCHMARK_ATTEMPT_INDEX"),("replicate_seed","BENCHMARK_REPLICATE_SEED"),("remaining_seconds","BENCHMARK_REMAINING_SECONDS"),("task_id","BENCHMARK_TASK_ID"),("protocol_id","BENCHMARK_PROTOCOL_ID")]:
     if field in request:os.environ[env]=str(request[field])
    if native_only:
     native_af2_batch(str(cfgp),config_sha,str(tp),request["attempt_dir"])
     atomic(response,{"schema":"paired-budget-session-v1","status":"COMPLETE","request_id":ident,"completed_at_epoch":time.time()})
    else:
     method_attempt(method,str(tp),request["attempt_dir"],int(request["seed"]),str(cfgp),config_sha)
     result=inside_project(request["attempt_dir"])/"attempt_result.json"
     atomic(response,{"schema":"paired-budget-session-v1","status":"COMPLETE","request_id":ident,"attempt_result":rec(result),"completed_at_epoch":time.time()})
     if json.loads(result.read_text())["status"]=="ENGINEERING_FAILURE":return
   except BaseException as e:
    attempt=inside_project(request["attempt_dir"]);result=attempt/"attempt_result.json"
    if not native_only and not result.exists():atomic(result,{"status":"ENGINEERING_FAILURE","method":method,"reason":repr(e),"completed_at_epoch":time.time()})
    atomic(response,{"schema":"paired-budget-session-v1","status":"ENGINEERING_FAILURE" if native_only else "COMPLETE","request_id":ident,"reason":repr(e),
                   "attempt_result":rec(result) if result.exists() else None,"traceback":traceback.format_exc(),"completed_at_epoch":time.time()})
    return
   done.add(path.name)

def main():
 a=argparse.ArgumentParser(); sub=a.add_subparsers(dest="cmd",required=True)
 p=sub.add_parser("inventory");p.add_argument("--output",required=True)
 p=sub.add_parser("probe");p.add_argument("--label",required=True);p.add_argument("--output",required=True)
 p=sub.add_parser("method-attempt");p.add_argument("--method",required=True,choices=["rf_diffusion","bindcraft"]);p.add_argument("--target-manifest",required=True);p.add_argument("--attempt-dir",required=True);p.add_argument("--seed",required=True,type=int);p.add_argument("--config",required=True);p.add_argument("--config-sha256",required=True)
 for cmd in ["method-session","native-af2-session"]:
  p=sub.add_parser(cmd);p.add_argument("--method",choices=["rf_diffusion","bindcraft"],default="rf_diffusion");p.add_argument("--target-manifest",required=True);p.add_argument("--session-dir",required=True);p.add_argument("--config",required=True);p.add_argument("--config-sha256",required=True)
 p=sub.add_parser("native-af2-batch");p.add_argument("--target-manifest",required=True);p.add_argument("--attempt-dir",required=True);p.add_argument("--config",required=True);p.add_argument("--config-sha256",required=True)
 ns=a.parse_args()
 if not os.environ.get("SLURM_JOB_ID"):raise RuntimeError("Slurm job required")
 if ns.cmd=="inventory":inventory(ns.output)
 elif ns.cmd=="method-attempt":method_attempt(ns.method,ns.target_manifest,ns.attempt_dir,ns.seed,ns.config,ns.config_sha256)
 elif ns.cmd in {"method-session","native-af2-session"}:method_session(ns.method,ns.target_manifest,ns.session_dir,ns.config,ns.config_sha256,ns.cmd=="native-af2-session")
 elif ns.cmd=="native-af2-batch":native_af2_batch(ns.config,ns.config_sha256,ns.target_manifest,ns.attempt_dir)
 else:probe(ns.label,ns.output)
if __name__=="__main__":main()


