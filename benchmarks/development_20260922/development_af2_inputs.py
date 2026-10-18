import sys,shutil,hashlib,collections,os
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,require,checked_command
from ppiblocker.structure import read_structure
root=Path("/lustre/users/u21111210118/projects/test9")
protocol=root/"source/benchmarks/development_20260922/orthogonal_protocol.json"
run=Run(root,"62_development_af2_inputs",[record_file(protocol)])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 cells=collections.defaultdict(list)
 for p in (root/"steps/33_generation_development/runs").glob("*/manifest.json"):
  m=read_json(p)
  if m["status"]=="DEVELOPMENT_POOL_GENERATED":cells[m["cell_index"]].append((p,m))
 require(set(cells)==set(range(16)) and all(len(v)==1 for v in cells.values()),"GENERATION_CELLS_INCOMPLETE",str({k:len(v) for k,v in cells.items()}))
 entries=[];receipts=[]
 for idx in range(16):
  p,m=cells[idx][0];receipts.append(record_file(p));design=verify_file(m["design_manifest"]);dm=read_json(design)
  candidates=read_json(verify_file(dm["outputs"]["candidates"]));require(len(candidates)==16,"CANDIDATE_COUNT",str(idx))
  groups=collections.defaultdict(list)
  for c in candidates:groups[c["backbone"]["sha256"]].append(c)
  require(len(groups)>=4,"BACKBONE_DIVERSITY_FOR_SAMPLING",str(idx))
  chosen=sorted(groups,key=lambda x:hashlib.sha256(("orthogonal-dev-v1:"+str(idx)+":"+x).encode()).hexdigest())[:4]
  native=verify_file(dm["outputs"]["native"]);target=read_structure(native)[0][0]["sequence"]
  for h in chosen:
   c=min(groups[h],key=lambda x:hashlib.sha256(("sequence-choice-v1:"+x["sequence"]).encode()).hexdigest())
   entries.append(dict(id=f"dev_{idx:02d}_{c['id']}",source_id=c["id"],group=m["case"],case=m["case"],condition=m["condition"],seed=m["seed"],cell_index=idx,sequence=c["sequence"],target_sequence=target,native=record_file(native),backbone=c["backbone"],design_manifest=record_file(design)))
 require(len(entries)==64,"SUBSAMPLE_COUNT",str(len(entries)))
 plan=run.path/"outputs/plan.json";atomic_json(plan,dict(entries=entries,selection="4 independent backbones per generation cell, SHA256 deterministic ordering; one sequence per backbone; no refold scores consulted",generation_manifests=receipts));run.output("plan",plan)
 msa_up=root/"steps/24_target_msa/runs/20260922T053230Z_5f5d81e4f519/manifest.json";msa=verify_file(read_json(msa_up)["outputs"]["receipt"])
 run.manifest["inputs"].append(record_file(msa_up));run.save()
 worker=root/"source/benchmarks/runtime_pilot_20260922/serialize_msa_parallel.py";shutil.copy2(worker,run.path/"qc/worker.py")
 env=os.environ.copy();env.update(PYTHONNOUSERSITE="1",JAX_PLATFORMS="cpu",CUDA_VISIBLE_DEVICES="");env.pop("PYTHONPATH",None)
 checked_command([root/"env/colabfold/bin/python",worker,plan,msa,run.path/"outputs/msa_queries"],run.path/"work",run.path/"logs/serialize.log",env,timeout=1800)
 run.output("inputs",run.path/"outputs/msa_queries/inputs.json")
 print(run.finish("MSA_INPUTS_VALIDATED","prespecified_orthogonal_subsample"),flush=True)
except Exception as e:run.fail(e);raise
