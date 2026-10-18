import os,sys,shutil,json,collections
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,checked_command,require,tree_fingerprint
from ppiblocker.pipeline import validate_design_pose
from ppiblocker.backends import require_gpu
from ppiblocker.structure import read_structure,write_pdb,interface
from ppiblocker.benchmark_adapters import import_pool
root=Path("/lustre/users/u21111210118/projects/test9")
pose=root/"steps/01_pose/runs/20260920T125042Z_8e4ecd8ead82/manifest.json"
run=Run(root,"54_bindcraft_acceptance",[record_file(pose)])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 require_gpu();_,_,native=validate_design_pose(read_json(pose));t,p=read_structure(native)[0]
 runtime=run.path/"qc/runtime.json";vendor=root/"vendor/BindCraft"
 receipts=[read_json(x) for x in (root/"steps/50_bindcraft_full_weights/runs").glob("*/manifest.json")]
 good=[x for x in receipts if x["status"]=="BINDCRAFT_ALL_WEIGHTS_PREPARED"];require(len(good)==1,"WEIGHTS_NOT_ACCEPTED",str(len(good)))
 weights=read_json(verify_file(good[0]["outputs"]["weights"]))
 for w in weights["weights"]:verify_file(w)
 compat=[(p,read_json(p)) for p in (root/"steps/63_bindcraft_glibc/runs").glob("*/manifest.json") if read_json(p)["status"]=="BINDCRAFT_PRIVATE_RUNTIME_ACCEPTED"]
 require(len(compat)==1,"BINDCRAFT_COMPATIBILITY_NOT_ACCEPTED",str(len(compat)))
 run.manifest["inputs"].append(record_file(compat[0][0]));run.save()
 wrapper=root/"source/benchmarks/development_20260922/bindcraft_bounded.py"
 atomic_json(runtime,dict(vendor=record_file(vendor/".source_receipt.json"),colabdesign=record_file(root/"vendor/ColabDesign/.source_receipt.json"),
  private_runtime=record_file(verify_file(compat[0][1]["outputs"]["runtime"])),wrapper=record_file(wrapper),weights=good[0]["outputs"]["weights"],profile="full4stage_two_attempts_two_mpnn_per_successful_trajectory",
  package_fingerprint=tree_fingerprint(root/"env/bindcraft/lib/python3.10/site-packages/colabdesign")))
 counts=collections.Counter(a for a,b in interface(t,p)["residue_pairs"]);anchors=sorted(counts,key=lambda a:(-counts[a],a))[:3]
 target=run.path/"outputs/target_only.pdb";write_pdb(target,[t]);out=run.path/"work/bindcraft"
 settings=dict(design_path=str(out),binder_name="P06_runtime",starting_pdb=str(target),chains="A",target_hotspot_residues=",".join(f"A{x}" for x in anchors),lengths=[65,65],number_of_final_designs=999)
 advanced=read_json(vendor/"settings_advanced/default_4stage_multimer.json")
 advanced.update(af_params_dir=str(root/"assets/bindcraft"),dssp_path=str(root/"assets/bindcraft/bin/dssp"),dalphaball_path=str(root/"assets/bindcraft/bin/DAlphaBall.gcc"),num_seqs=2,max_mpnn_sequences=2,max_trajectories=False,
  save_design_animations=False,save_design_trajectory_plots=False,save_mpnn_fasta=True,remove_unrelaxed_trajectory=False,remove_unrelaxed_complex=False,remove_binder_monomer=False)
 for name,value in [("settings",settings),("advanced",advanced)]:atomic_json(run.path/"outputs"/(name+".json"),value);run.output(name,run.path/"outputs"/(name+".json"))
 env=os.environ.copy();env.update(PYTHONNOUSERSITE="1",XLA_PYTHON_CLIENT_PREALLOCATE="false",TF_FORCE_UNIFIED_MEMORY="0",OMP_NUM_THREADS=str(os.environ.get("SLURM_CPUS_PER_TASK","4")))
 site=root/"env/bindcraft/lib/python3.10/site-packages"
 env["LD_LIBRARY_PATH"]=":".join(str(x) for x in sorted((site/"nvidia").glob("*/lib")))+":"+str(root/"env/bindcraft/lib")+":"+env.get("LD_LIBRARY_PATH","")
 env["PATH"]=str(root/"env/bindcraft/bin")+":"+str(site/"nvidia/cuda_nvcc/bin")+":"+env.get("PATH","")
 env["XLA_FLAGS"]="--xla_gpu_cuda_data_dir="+str(site/"nvidia/cuda_nvcc");env.pop("PYTHONPATH",None)
 events=run.path/"outputs/budget_events.jsonl"
 checked_command([root/"env/bindcraft/bin/python",wrapper,vendor,"2142","2",events,"--settings",run.path/"outputs/settings.json","--advanced",run.path/"outputs/advanced.json","--filters",vendor/"settings_filters/default_filters.json"],vendor,run.path/"logs/bindcraft.log",env,timeout=10800)
 pdbs=list(out.rglob("*.pdb"));require(pdbs,"NO_MODEL_OUTPUT","No BindCraft trajectory output")
 inventory=[];rows=[];seen=set()
 for f in sorted(pdbs):
  try:
   cs,ctx=read_structure(f)
   if len(cs)!=2 or ctx:continue
   a,b=cs
   if a["sequence"]!=t["sequence"] or len(b["sequence"])!=65:continue
   inventory.append(dict(path=record_file(f),sequence=b["sequence"],relative_path=str(f.relative_to(out))))
   # Export generated MPNN complexes even if they fail native filters; keep disposition.
   if "MPNN" not in str(f.relative_to(out)) or b["sequence"] in seen:continue
   seen.add(b["sequence"]);cid=f"bc_{len(rows):03d}"
   normalized=run.path/"outputs"/(cid+".pdb");write_pdb(normalized,[a,b])
   rows.append(dict(id=cid,sequence=b["sequence"],backbone=record_file(normalized),native_method_disposition=str(f.relative_to(out))))
  except Exception as e:inventory.append(dict(path=str(f),error=str(e)))
 atomic_json(run.path/"outputs/inventory.json",inventory);run.output("inventory",run.path/"outputs/inventory.json");run.output("runtime",runtime);run.output("budget_events",events)
 if rows:
  pool=dict(schema_version=1,pose_manifest=record_file(pose),method="BindCraft",code_revision=read_json(vendor/".source_receipt.json")["revision"],runtime_record=record_file(runtime),candidate_budget=dict(max_attempts=2,mpnn_per_successful_trajectory=2,profile="runtime_acceptance"),candidates=rows)
  cp=run.path/"outputs/pool_contract.json";atomic_json(cp,pool);run.output("pool",cp)
  result=import_pool(root,pose,cp);run.output("design_manifest",result)
 print(run.finish("BINDCRAFT_RUNTIME_ACCEPTED_WITH_POOL" if rows else "BINDCRAFT_RUNTIME_ACCEPTED_ZERO_MPNN_EXPORT","engineering_only",dict(exported_sequences=len(rows),trajectory_structures=len(inventory),superiority_established=False)),flush=True)
except Exception as e:run.fail(e);raise
