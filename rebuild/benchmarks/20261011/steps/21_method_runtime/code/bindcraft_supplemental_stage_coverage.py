#!/usr/bin/env python3
"""Fixed-pose BindCraft API coverage. Supplemental engineering only; never a formal pool."""
import argparse,hashlib,importlib.util,json,math,os,sys,time,traceback
from pathlib import Path
ROOT=Path("/lustre/users/u21111210118/projects/test9")
S=ROOT/"steps/21_method_runtime"
V=ROOT/"steps/22_matched_benchmark/settings/pilot_v8"
GUARD=ROOT/"steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py"
RUNTIME=V/"source/benchmark_runtime.py"
CONF=S/"runs/native_collector_contracts_13166/source/audit_native_confidence_v8.py"
BASE=ROOT/"steps/22_matched_benchmark/engineering_pilot/runs_v5/13175_1"
POSE=BASE/"attempts/000000/generated/Trajectory/Clashing/attempt_l65_s791205.pdb"
TARGET=ROOT/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/KEAP1_2FLU/input_manifest.json"
EVENT_SEQUENCE="PREYSEPEIVEMVKDIYDNRDDPWDWMDLRDIMKHMTHSELAVVVRVLRSYGSTIPKEIRPYINM"
SEQUENCE="PREYSEPEIVECVKDIYDNRDDPWDWMDLRDIMKHMTHSELAVVVRVLRSYGSTIPKEIRPYINM"
IDENTITY=S/"runs/bc_native_identity_13217/outputs/identity.json"
SCOPE="ENGINEERING_STAGE_COVERAGE_ONLY_NOT_NATIVE_ACCEPTED_NOT_FORMAL"
def rec(p):
 p=Path(p);return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def atomic(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():raise FileExistsError(p)
 t=p.with_name(p.name+".partial")
 with t.open("x") as f:f.write(json.dumps(v,indent=2)+"\n");f.flush();os.fsync(f.fileno())
 os.replace(t,p)
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def check(v):
 p=Path(v["path"]).resolve()
 if ROOT not in p.parents or rec(p)!=v:raise RuntimeError("Supplemental pinned input mismatch")
 return p
def cpu():
 import subprocess
 if not os.environ.get("SLURM_JOB_ID") or os.environ.get("CUDA_VISIBLE_DEVICES")!="":raise RuntimeError("Explicit CPU Slurm required")
 raw=subprocess.check_output(["scontrol","show","job","-o",os.environ["SLURM_JOB_ID"]],text=True)
 for token in raw.split():
  if token.startswith(("AllocTRES=","TRES=")):
   if any(x.startswith("gres/gpu=") and int(x.split("=")[1])>0 for x in token.split("=",1)[1].split(",")):raise RuntimeError("CPU stage allocated GPU")
 return raw
def identity(p,target,binder):
 from Bio.PDB import PDBParser
 from Bio.SeqUtils import seq1
 import numpy as np
 structure=PDBParser(QUIET=True).get_structure("fixed-input",str(p))[0]
 seq={c.id:"".join(seq1(r.resname) for r in c if r.id[0]==" ") for c in structure}
 assert seq=={"A":target,"B":binder},seq
 assert all(np.isfinite(a.coord).all() for a in structure.get_atoms())
 assert all("CA" in r for c in structure for r in c if r.id[0]==" ")
 return {"chain_sequences":seq,"full_target_count":len(target),"binder_count":len(binder),"coordinates_finite":True}
def prepare(out):
 scheduler=cpu();out=Path(out);out.mkdir(parents=True,exist_ok=True)
 target=json.loads(TARGET.read_text());events=[json.loads(x) for x in (BASE/"attempts/000000/bindcraft_native_events.jsonl").read_text().splitlines()]
 trajectory=[x for x in events if x["event"]=="trajectory_complete"];assert len(trajectory)==1
 assert trajectory[0]["sequence"]==EVENT_SEQUENCE and trajectory[0]["native_termination"]=="Clashing"
 assert json.loads((BASE/"attempts/000000/attempt_result.json").read_text())["status"]=="SCIENTIFIC_REJECT"
 proof={"schema":"supplemental_fixed_pose.v1","status":"ACTUAL_FIRST_NATIVE_REJECTED_TRAJECTORY_QUERY_VERIFIED","pose":rec(POSE),"target_manifest":rec(TARGET),
 "base_run":rec(BASE/"run_receipt.json"),"base_terminal":rec(BASE/"attempts/000000/attempt_result.json"),
 "base_native_events":rec(BASE/"attempts/000000/bindcraft_native_events.jsonl"),"trajectory":trajectory[0],
 "identity":identity(POSE,target["target_sequence"],SEQUENCE),"identity_diagnostic":rec(IDENTITY),
 "physical_binder_sequence":SEQUENCE,"reported_hard_binder_sequence":EVENT_SEQUENCE,
 "physical_vs_reported_difference":[{"position":12,"physical_pseudo_argmax":"C","reported_hard_argmax":"M"}],
 "official_export_semantics":{"get_seq":"best aux seq.hard argmax","save_pdb":"best aux all.aatype from pseudo argmax","best_soft":trajectory[0]["native_logs"]["soft"],"best_hard":trajectory[0]["native_logs"]["hard"],"causal_scope":"Source-consistent export difference; actual lost soft/hard arrays not reconstructed"},
 "source_proof":[rec(ROOT/"vendor/ColabDesign"/p) for p in ["colabdesign/shared/model.py","colabdesign/af/model.py","colabdesign/af/utils.py"]],
 "selection_rule":"First and only actual trajectory; no quality-based pose or seed selection","scope":SCOPE}
 atomic(out/"fixed_pose.json",proof)
 cfg={"schema":"supplemental_bindcraft_stage_coverage.v1","scientific_scope":SCOPE,"selected_raw_pool_index":0,"seed":791205,"binder_length":65,
 "budget_gpu_seconds":3600,"expected_gpu_count":1,"expected_gpu_name":"NVIDIA A100-PCIE-40GB",
 "runtime_source":rec(RUNTIME),"native_config":rec(V/"bindcraft.json"),"environment":rec(V/"source/bindcraft_env.sh"),"gpu_guard":rec(GUARD),"confidence_collector":rec(CONF),
 "source":rec(Path(__file__).resolve()),"fixed_pose":rec(out/"fixed_pose.json"),"target_manifest":rec(TARGET),"pose":rec(POSE),
 "advanced":rec(ROOT/"vendor/BindCraft/settings_advanced/default_4stage_multimer.json"),
 "filters":rec(ROOT/"vendor/BindCraft/settings_filters/default_filters.json"),
 "official_source_files":[rec(ROOT/"vendor/BindCraft"/p) for p in ["bindcraft.py","functions/colabdesign_utils.py","functions/generic_utils.py","functions/pyrosetta_utils.py","functions/biopython_utils.py"]],
 "calls":[
 {"api":"pr_relax+score_interface","role":"Actual fixed-pose interface selection using unchanged native relaxation/scoring"},
 {"api":"mpnn_gen_sequence","num_seqs":20,"sampling_temp":0.1,"mpnn_fix_interface":True,"weights":"soluble","omit_AAs":"C"},
 {"api":"predict_binder_complex","prediction_models":[0],"role":"Official unchanged basic filters; supplemental split call"},
 {"api":"predict_binder_complex","prediction_models":[1],"role":"Official unchanged basic filters; independent model2 coverage even if model1 fails"},
 {"api":"pr_relax+score_interface+calc_ss_percentage+RMSD","role":"Supplemental diagnostics on same-aux archived PDB even when native rejects"},
 {"api":"predict_binder_alone","prediction_models":[0,1]},
 {"api":"calculate_averages+validate_design_sequence+check_filters","role":"Default filter API applied to actual diagnostics; never native acceptance or ranking"}],
 "omit_sampling_semantics":"omitC applies to newly sampled positions; fixed-interface literal C may remain; official force_reject_AA false retained",
 "identity_diagnostic":rec(IDENTITY),
 "rng_policy":"Python random.seed(root_seed) plus unchanged NumPy controlled_seed(seed=None); record every actual Python randint return and numpy entropy replacement without extra draws; explicit AF2/Rosetta seeds unchanged",
 "repair_of_supplemental_gpu_job":"13234 PythonKey seed not reconstructable; retained as history; corrected replay fixed before outputs, no outcome/quality selection",
 "python_key_sources":[rec(ROOT/"vendor/ColabDesign/colabdesign/shared/utils.py"),rec(ROOT/"env/bindcraft/lib/python3.10/site-packages/colabdesign/shared/utils.py")],
 "prohibited":"No hallucination rerun, filter changes, retry/seed hunting, best candidate selection, formal seq ledger or native acceptance"}
 advanced=json.loads(Path(cfg["advanced"]["path"]).read_text())
 assert (advanced["num_seqs"],advanced["sampling_temp"],advanced["mpnn_fix_interface"],advanced["mpnn_weights"],advanced["omit_AAs"],advanced["num_recycles_validation"])==(20,.1,True,"soluble","C",3)
 atomic(out/"config.json",cfg)
 atomic(out/"acceptance.json",{"status":"FIXED_SUPPLEMENTAL_INPUT_AND_CALL_PLAN_CPU_VERIFIED_GPU_NOT_RUN","config":rec(out/"config.json"),"fixed_pose":rec(out/"fixed_pose.json"),"source":rec(Path(__file__).resolve()),"scheduler_record":scheduler,"scientific_scope":SCOPE})
def install_python_rng_observer(random,root_seed,event):
 original=random.randint
 random.seed(int(root_seed))
 def observed_randint(a,b):
  value=original(a,b)
  event("python_random_randint_observed",lower=a,upper=b,value=value)
  return value
 random.randint=observed_randint
 return original
def make_seed_controller(np,root_seed,event):
 original=np.random.seed;entropy=np.random.default_rng(int(root_seed))
 def controlled_seed(seed=None):
  if seed is None:
   seed=int(entropy.integers(0,2**31-1));event("deterministic_entropy_seed",seed=seed)
  return original(seed)
 return controlled_seed,original
def cover_models(functions,model,sequence,design,target,pose,advanced,filters,paths,failure,observer):
 results={}
 # Model IDs and order are predeclared; each official API keeps its unchanged basic filters.
 for index in [0,1]:
  call=lambda i=index:functions.predict_binder_complex(model,sequence,design,target["target_pdb"]["path"],"A",65,str(pose),[i],advanced,filters,paths,failure)
  results[index+1]=observer(index,call)
 return results
def augment_metrics(functions,raw,relaxed,pose,target,advanced,stats):
 # Same official main-script metric mappings, on actual archived predictions.
 functions.pr_relax(str(raw),str(relaxed))
 interface,aa,residues=functions.score_interface(str(relaxed),"B")
 alpha,beta,loops,ia,ib,il,ip,sp=functions.calc_ss_percentage(str(raw),advanced,"B")
 mapping={"Binder_Energy_Score":"binder_score","Surface_Hydrophobicity":"surface_hydrophobicity","ShapeComplementarity":"interface_sc","PackStat":"interface_packstat",
 "dG":"interface_dG","dSASA":"interface_dSASA","dG/dSASA":"interface_dG_SASA_ratio","Interface_SASA_%":"interface_fraction","Interface_Hydrophobicity":"interface_hydrophobicity",
 "n_InterfaceResidues":"interface_nres","n_InterfaceHbonds":"interface_interface_hbonds","InterfaceHbondsPercentage":"interface_hbond_percentage",
 "n_InterfaceUnsatHbonds":"interface_delta_unsat_hbonds","InterfaceUnsatHbondsPercentage":"interface_delta_unsat_hbonds_percentage"}
 stats.update({k:interface[v] for k,v in mapping.items()})
 stats.update({"i_pLDDT":ip,"ss_pLDDT":sp,"Unrelaxed_Clashes":functions.calculate_clash_score(str(raw)),
 "Relaxed_Clashes":functions.calculate_clash_score(str(relaxed)),"InterfaceAAs":aa,
 "Interface_Helix%":ia,"Interface_BetaSheet%":ib,"Interface_Loop%":il,"Binder_Helix%":alpha,"Binder_BetaSheet%":beta,"Binder_Loop%":loops,
 "Hotspot_RMSD":functions.unaligned_rmsd(str(pose),str(raw),"B","B"),
 "Target_RMSD":functions.target_pdb_rmsd(str(raw),target["target_pdb"]["path"],"A")})
 return residues
def run(config,expected,out):
 cfg=json.loads(check({"path":config,"bytes":Path(config).stat().st_size,"sha256":expected}).read_text())
 assert cfg["schema"]=="supplemental_bindcraft_stage_coverage.v1" and cfg["scientific_scope"]==SCOPE and cfg["selected_raw_pool_index"]==0
 for key in ["source","runtime_source","native_config","environment","gpu_guard","confidence_collector","fixed_pose","target_manifest","pose","advanced","filters","identity_diagnostic"]:check(cfg[key])
 for x in cfg["official_source_files"]+cfg["python_key_sources"]:check(x)
 guard=load("budget_guard",check(cfg["gpu_guard"])).gpu_ownership_guard(expected_count=1,expected_gpu_name=cfg["expected_gpu_name"])
 os.environ["CUDA_VISIBLE_DEVICES"]=guard["child_cuda_visible_devices"]
 rt=load("supplement_runtime",check(cfg["runtime_source"]));out=Path(out).resolve()
 assert ROOT in out.parents and not out.exists();out.mkdir(parents=True)
 rt.atomic(out/"gpu_allocation.json",guard)
 os.environ.update({"BENCHMARK_TASK_ID":"SUPPLEMENTAL_BINDCRAFT_13175_FIRST_REJECT","BENCHMARK_ATTEMPT_INDEX":"0","BENCHMARK_REPLICATE_SEED":str(cfg["seed"]),
 "BENCHMARK_METHOD_CONFIG_SHA256":expected,"BENCHMARK_TARGET_MANIFEST_SHA256":cfg["target_manifest"]["sha256"]})
 target=json.loads(check(cfg["target_manifest"]).read_text());pose=check(cfg["pose"])
 sys.path.insert(0,str(ROOT/"vendor/BindCraft"));import functions
 import jax,numpy as np,random
 from colabdesign import mk_afdesign_model
 assert len([d for d in jax.devices() if d.platform=="gpu"])==1
 advanced=json.loads(check(cfg["advanced"]).read_text());filters=json.loads(check(cfg["filters"]).read_text())
 advanced.update({"af_params_dir":str(ROOT/"assets/colabfold"),"dssp_path":str(ROOT/"vendor/BindCraft/functions/dssp"),
 "dalphaball_path":str(ROOT/"vendor/BindCraft/functions/DAlphaBall.gcc")})
 functions.pr.init(f'-ignore_unrecognized_res -ignore_zero_occupancy -mute all -holes:dalphaball {advanced["dalphaball_path"]} -corrections::beta_nov16 true -relax:default_repeats 1')
 functions.pr.rosetta.numeric.random.rg().set_seed(cfg["seed"]);np.random.seed(cfg["seed"])
 paths=functions.generate_directories(str(out/"generated"));failure=str(out/"failure.csv");functions.generate_filter_pass_csv(failure,str(check(cfg["filters"])))
 events=out/"supplemental_events.jsonl"
 def event(stage,**kw):rt.append_stream(events,{"stage":stage,"scientific_scope":SCOPE,"completed_at_epoch":time.time(),**kw})
 original_randint=install_python_rng_observer(random,cfg["seed"],event)
 event("python_rng_seeded_before_official_constructors",root_seed=cfg["seed"],additional_draws=0)
 controlled_seed,original_seed=make_seed_controller(np,cfg["seed"],event)
 np.random.seed=controlled_seed;original_seed(cfg["seed"])
 def timed(stage,operation):
  rt.generation_gate();start=time.time();v=operation();event(stage,seconds=time.time()-start);return v
 start=time.time()
 try:
  relaxed=out/"generated/Trajectory/Relaxed/fixed_first_rejected.pdb"
  timed("fixed_pose_relax",lambda:functions.pr_relax(str(pose),str(relaxed)))
  interface,aa,fixed_residues=timed("fixed_pose_interface",lambda:functions.score_interface(str(relaxed),"B"))
  rt.atomic(out/"fixed_pose_interface.json",{"interface_residues":fixed_residues,"scores":rt.jsonable(interface),"aas":aa,"pose":str(pose),"relaxed":str(relaxed),"native_fix_interface":True,"fixed_cysteine_positions":[int(x[1:]) for x in fixed_residues.split(",") if x and SEQUENCE[int(x[1:])-1]=="C"],"physical_binder_sequence":SEQUENCE,"reported_hard_binder_sequence":EVENT_SEQUENCE})
  native_globals=functions.mpnn_gen_sequence.__globals__;original_factory=native_globals["mk_mpnn_model"]
  def observed_factory(*args,**kwargs):
   value=original_factory(*args,**kwargs)
   owner=getattr(getattr(value,"key",None),"__self__",None)
   event("actual_mpnn_constructor_key_seed_observed",seed=getattr(owner,"seed",None),constructor_kwargs=kwargs,additional_draws=0)
   return value
  native_globals["mk_mpnn_model"]=observed_factory
  try:pool=timed("official_soluble_mpnn20",lambda:functions.mpnn_gen_sequence(str(pose),"B",fixed_residues,advanced))
  finally:native_globals["mk_mpnn_model"]=original_factory
  assert len(pool["seq"])==20
  rows=[]
  for i,value in enumerate(pool["seq"]):
   sequence=str(value)[-65:];assert len(sequence)==65 and not set(sequence)-set("ACDEFGHIKLMNPQRSTVWY")
   row={"retained_fixed_cysteine_positions":[j+1 for j,aa in enumerate(sequence) if aa=="C"],"raw_pool_index":i,"sequence_record_id":"SUPPLEMENTAL_raw_"+str(i),"sequence":sequence,"score":float(pool["score"][i]),"seqid":float(pool["seqid"][i]),"scientific_scope":SCOPE}
   rows.append(row);rt.append_stream(out/"supplemental_sequences.jsonl",row)
  rt.atomic(out/"mpnn_pool.json",{"rows":rows,"selection_rule":"raw_pool_index0 predeclared before model output","scope":SCOPE})
  chosen=rows[0];sequence=chosen["sequence"];design="SUPPLEMENTAL_raw_index0"
  functions.clear_mem()
  model=mk_afdesign_model(protocol="binder",num_recycles=advanced["num_recycles_validation"],data_dir=advanced["af_params_dir"],
    use_multimer=False,use_initial_guess=advanced["predict_initial_guess"],use_initial_atom_pos=advanced["predict_bigbang"])
  model.prep_inputs(pdb_filename=target["target_pdb"]["path"],chain="A",binder_len=65,
    rm_target_seq=advanced["rm_template_seq_predict"],rm_target_sc=advanced["rm_template_sc_predict"],seed=cfg["seed"])
  archives={}
  def observer(index,operation):
   def after(args,kwargs):
    assert kwargs["models"]==[index]
    item=rt.save_native_confidence(model,out,"supplemental_model_"+str(index+1),"bindcraft",target["target_sequence"],sequence,
     {"native_design":design,"sequence_record_ids":[chosen["sequence_record_id"]],"model_names":[model._model_names[index]],
      "attempt_seed":cfg["seed"],"predict_seed_argument":kwargs.get("seed"),"num_recycles":kwargs.get("num_recycles"),
      "official_native_pdb_path":str(Path(paths["MPNN"])/(design+"_model"+str(index+1)+".pdb")),
      "target_chain":"A","binder_chain":"B","capture_scope":SCOPE})
    archives[index+1]=item
   stats,passed=timed("official_native_complex_ptm"+str(index+1),lambda:rt.observed_native_predict_call(model,after,operation))
   event("official_basic_filter_decision",model=index+1,basic_native_pass=bool(passed),statistics=rt.jsonable(stats),archive=archives[index+1])
   return {"statistics":rt.jsonable(stats),"official_basic_native_pass":bool(passed),"confidence":archives[index+1]}
  results=cover_models(functions,model,sequence,design,target,pose,advanced,filters,paths,failure,observer)
  rt.atomic(out/"native_basic_results.json",{"results":results,"scope":SCOPE,"not_native_accepted":True})
  stats={};interface_residues={}
  for index in [1,2]:
   info=json.loads(Path(archives[index]["path"]).read_text());raw=Path(info["raw_pdb"]["path"])
   relaxed=Path(paths["MPNN/Relaxed"])/(design+"_model"+str(index)+".pdb")
   stats[index]=dict(results[index]["statistics"][str(index)])
   interface_residues[index]=timed("supplemental_diagnostics_model"+str(index),lambda:augment_metrics(functions,raw,relaxed,pose,target,advanced,stats[index]))
  functions.clear_mem()
  binder=mk_afdesign_model(protocol="hallucination",use_templates=False,initial_guess=False,use_initial_atom_pos=False,
    num_recycles=advanced["num_recycles_validation"],data_dir=advanced["af_params_dir"],use_multimer=False)
  binder.prep_inputs(length=65,seed=cfg["seed"])
  binder_stats=timed("official_binder_alone_ptm1_and_2",lambda:functions.predict_binder_alone(binder,sequence,design,65,str(pose),"B",[0,1],advanced,paths))
  for index in [1,2]:
   binder_pdb=Path(paths["MPNN/Binder"])/(design+"_model"+str(index)+".pdb")
   binder_stats[index]["Binder_RMSD"]=functions.unaligned_rmsd(str(pose),str(binder_pdb),"B","A")
  complex_avg=functions.calculate_averages(stats,handle_aa=True);binder_avg=functions.calculate_averages(binder_stats)
  _,labels,_=functions.generate_dataframe_labels()
  values={"Design":design,"Protocol":advanced["design_algorithm"],"Length":65,"Seed":cfg["seed"],"Sequence":sequence,
    "InterfaceResidues":interface_residues[1],"MPNN_score":round(chosen["score"],2),"MPNN_seq_recovery":round(chosen["seqid"],2)}
  for key,value in complex_avg.items():values["Average_"+key]=value
  for index,metrics in stats.items():
   for key,value in metrics.items():values[str(index)+"_"+key]=value
  for key,value in binder_avg.items():values["Average_Binder_"+key if key!="Binder_RMSD" else "Average_Binder_RMSD"]=value
  for index,metrics in binder_stats.items():
   for key,value in metrics.items():values[str(index)+"_Binder_"+key if key!="Binder_RMSD" else str(index)+"_Binder_RMSD"]=value
  values["Notes"]=functions.validate_design_sequence(sequence,complex_avg.get("Relaxed_Clashes"),advanced)
  filtering=timed("official_final_filter_api_on_actual_supplemental_diagnostics",lambda:functions.check_filters([values.get(x) for x in labels],labels,filters))
  rt.atomic(out/"supplemental_final_filters.json",{"actual_complex_statistics":rt.jsonable(stats),"actual_binder_statistics":rt.jsonable(binder_stats),
   "complex_averages":rt.jsonable(complex_avg),"binder_averages":rt.jsonable(binder_avg),"filter_values":rt.jsonable(values),
   "default_filter_api_result":rt.jsonable(filtering),"official_basic_results":results,"scope":SCOPE,
   "interpretation":"API diagnostics only; no native acceptance, native ranking, accepted folder, or formal candidate eligibility"})
  rt.atomic(out/"worker_result.json",{"status":"SUPPLEMENTAL_OFFICIAL_APIS_COMPLETED_NOT_NATIVE_ACCEPTANCE","scientific_scope":SCOPE,
   "gpu_job":os.environ["SLURM_JOB_ID"],"config_path":config,"config_sha256":expected,"elapsed_seconds":time.time()-start,
   "raw_mpnn_count":20,"complex_models":[1,2],"binder_models":[1,2],"final_filter_called":True,"formal_sequences":0})
 except BaseException as exc:
  rt.atomic(out/"worker_failure.json",{"status":"SUPPLEMENTAL_TYPED_ENGINEERING_FAILURE","scientific_scope":SCOPE,"reason":repr(exc),"traceback":traceback.format_exc(),"elapsed_seconds":time.time()-start})
  raise
 finally:np.random.seed=original_seed;random.randint=original_randint
def collect(config,expected,out,report):
 scheduler=cpu();cfg=json.loads(check({"path":config,"bytes":Path(config).stat().st_size,"sha256":expected}).read_text());out=Path(out);report=Path(report)
 rt=load("collector_runtime",check(cfg["runtime_source"]));cc=load("collector_confidence",check(cfg["confidence_collector"]))
 result=json.loads((out/"worker_result.json").read_text());assert result["status"]=="SUPPLEMENTAL_OFFICIAL_APIS_COMPLETED_NOT_NATIVE_ACCEPTANCE" and result["formal_sequences"]==0
 guard=json.loads((out/"gpu_allocation.json").read_text());assert len(guard["owned_gpu_uuids"])==1 and "gres/gpu=1" in guard["scheduler_alloc_tres"]
 target=json.loads(check(cfg["target_manifest"]).read_text());pool=json.loads((out/"mpnn_pool.json").read_text())
 assert len(pool["rows"])==20 and [x["raw_pool_index"] for x in pool["rows"]]==list(range(20))
 observations=[cc.confidence_record(p,out,target,"bindcraft") for p in sorted((out/"native_confidence").glob("*.json"))]
 assert [x["model_names"] for x in observations]==[["model_1_ptm"],["model_2_ptm"]]
 assert all(x["context"]["sequence_record_ids"]==[pool["rows"][0]["sequence_record_id"]] for x in observations)
 final=json.loads((out/"supplemental_final_filters.json").read_text());assert final["scope"]==SCOPE
 sys.path.insert(0,str(ROOT/"vendor/BindCraft"));import functions
 _,labels,_=functions.generate_dataframe_labels();filters=json.loads(check(cfg["filters"]).read_text())
 actual=functions.check_filters([final["filter_values"].get(x) for x in labels],labels,filters)
 assert rt.jsonable(actual)==final["default_filter_api_result"]
 assert all(k in final["actual_complex_statistics"] for k in ["1","2"]) and all(k in final["actual_binder_statistics"] for k in ["1","2"])
 assert not (out/"sequences.jsonl").exists() and not (out/"native_screening.jsonl").exists()
 report.mkdir(parents=True,exist_ok=True)
 atomic(report/"acceptance.json",{"status":"SUPPLEMENTAL_NATIVE_API_STAGE_COVERAGE_CONTENT_CPU_ACCEPTED_NOT_SCIENTIFIC_ACCEPTANCE",
 "scientific_scope":SCOPE,"coverage_mode":"FIXED_REAL_REJECTED_TRAJECTORY_SUPPLEMENTAL_API_DIAGNOSTICS",
 "source":rec(Path(__file__).resolve()),"config":rec(Path(config)),"actual_worker":rec(out/"worker_result.json"),
 "gpu_allocation":rec(out/"gpu_allocation.json"),"actual_assigned_gpu_count":1,"fixed_pose":cfg["fixed_pose"],
 "mpnn_pool":rec(out/"mpnn_pool.json"),"raw_pool_count":20,"selected_raw_pool_index":0,
 "actual_native_predictions":observations,"basic_filter_decisions":rec(out/"native_basic_results.json"),
 "final_filter_diagnostics":rec(out/"supplemental_final_filters.json"),
 "stage_evidence":{"soluble_proteinmpnn":rec(out/"mpnn_pool.json"),"native_af2_ptm1_and_2":rec(out/"native_basic_results.json"),"native_filters":rec(out/"supplemental_final_filters.json")},
 "gpu_cost_scope":"Independent supplemental allocation, never added to formal native throughput; root obtains final Slurm accounting",
 "formal_sequences":0,"native_accepted_sequences":0,"cpu_job":os.environ["SLURM_JOB_ID"],"scheduler_record":scheduler})
def main():
 ap=argparse.ArgumentParser();ap.add_argument("command",choices=["prepare","run","collect"]);ap.add_argument("--output-dir",required=True);ap.add_argument("--config");ap.add_argument("--config-sha256");ap.add_argument("--report-dir");a=ap.parse_args()
 if a.command=="prepare":prepare(a.output_dir)
 elif a.command=="run":run(a.config,a.config_sha256,a.output_dir)
 else:collect(a.config,a.config_sha256,a.output_dir,a.report_dir)
if __name__=="__main__":main()
