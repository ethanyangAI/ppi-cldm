import os,sys,shutil,re,json
from pathlib import Path
import numpy as np
from ppiblocker.common import *
from ppiblocker.af2_review import inspect,pose_distance,atom_overlap
from ppiblocker.structure import read_structure
root=Path("/lustre/users/u21111210118/projects/test9");slot=int(sys.argv[1]);run=Run(root,"75_af2_review_score",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 found=[(p,read_json(p)) for p in (root/"steps/74_af2_review_predict/runs").glob("*/manifest.json") if read_json(p)["status"]=="AF2_REVIEW_PREDICTION_COMPLETE" and read_json(p)["slot"]==slot]
 require(len(found)==1,"PREDICTION_NOT_UNIQUE",str(slot));up,m=found[0];data=read_json(verify_file(m["outputs"]["predictions"]));e=data["entry"]
 setup=[read_json(p) for p in (root/"steps/73_af2_review_setup/runs").glob("*/manifest.json") if read_json(p)["status"]=="AF2_REVIEW_INPUTS_READY"];require(len(setup)==1,"SETUP_NOT_UNIQUE",str(len(setup)))
 source=read_json(verify_file(setup[0]["outputs"]["ipsae_source"]));ipsae=verify_file(source["files"]["ipsae.py"])
 run.manifest.update(inputs=[record_file(up),setup[0]["outputs"]["ipsae_source"],data["protocol"]],slot=slot,entry_id=e["id"]);run.save()
 env=os.environ.copy();env.update(PYTHONNOUSERSITE="1",CUDA_VISIBLE_DEVICES="",JAX_PLATFORMS="cpu",OPENMM_CPU_THREADS="2",OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="2");env.pop("PYTHONPATH",None);env.pop("LD_LIBRARY_PATH",None)
 worker=root/"source/benchmarks/af2_review_20260923/relax_worker.py"
 cycles={}
 for line in (up.parent/"logs/expanded.log").read_text().splitlines():
  found=re.search(r"model_(\d+)_seed_(\d+).*took.*\((\d+) recycles\)",line)
  if found:cycles[(int(found[1]),int(found[2]))]=int(found[3])
 rows=[];structures={}
 for arm in ("baseline","expanded"):
  structures[arm]=[]
  for i,z in enumerate(data[arm]):
   raw=verify_file(z["pdb"]);scores=verify_file(z["scores"]);match=re.search(r"model_(\d+)_seed_(\d+)",raw.name)
   require(match,"MODEL_NAME",raw.name)
   case=run.path/"work"/f"{arm}_{i:02d}";case.mkdir();p=case/"model.pdb";shutil.copy2(raw,p)
   original,cs=inspect(e,p,scores);structures[arm].append(cs)
   row=dict(arm=arm,weight=int(match[1]),seed=int(match[2]),actual_recycles=cycles.get((int(match[1]),int(match[2]))) if arm=="expanded" else None,raw_structure=record_file(raw),scores=record_file(scores),raw=original,relaxation_status="PENDING",ipsae=[])
   # ipSAE operates on copies to avoid writing into immutable upstream runs.
   for cutoff in (10,15):
    checked_command([root/"env/core/bin/python",ipsae,scores,p,str(cutoff),"15"],case,run.path/"logs"/f"{arm}_{i:02d}_ipsae_{cutoff}.log",env,timeout=120)
    files=list(case.glob(f"model_{cutoff:02d}_15.txt"));require(len(files)==1,"IPSAE_OUTPUT",str(list(case.iterdir())))
    lines=files[0].read_text().splitlines();parsed=[]
    for line in lines:
     fields=line.split()
     if len(fields)>6 and fields[0] in ("A","B") and fields[1] in ("A","B") and fields[4] in ("asym","max"):
      parsed.append(dict(chain1=fields[0],chain2=fields[1],type=fields[4],ipSAE=float(fields[5])))
    require(len(parsed)>=2,"IPSAE_PARSE",str(files[0]))
    row["ipsae"].append(dict(pae_cutoff=cutoff,distance_cutoff=15,scores=parsed,output=record_file(files[0])))
   relaxed=case/"relaxed.pdb";rr=case/"relaxation.json"
   try:
    checked_command([root/"env/bindcraft/bin/python",worker,p,relaxed,rr],case,run.path/"logs"/f"{arm}_{i:02d}_relax.log",env,timeout=600)
    relaxed_metrics,relaxed_cs=inspect(e,relaxed,scores)
    row.update(relaxation_status="COMPLETE",relaxed_structure=record_file(relaxed),relaxation=read_json(rr),relaxed=relaxed_metrics,relaxation_movement=pose_distance(cs,relaxed_cs),network_confidence_recomputed=False)
   except Exception as error:row.update(relaxation_status="FAILED",relaxation_error=str(error))
   rows.append(row);atomic_json(run.path/"outputs/results.json",dict(entry=e,models=rows))
   print(e["id"],arm,i,row["relaxation_status"],flush=True)
 dispersion={}
 for arm,models in structures.items():
  distances=[pose_distance(models[i],models[j])["binder_ca_after_target_alignment"] for i in range(len(models)) for j in range(i)]
  dispersion[arm]=dict(pairs=len(distances),median=float(np.median(distances)),max=float(max(distances)))
 result=dict(entry=e,models=rows,pose_dispersion=dispersion,claims=dict(experimental_binding=False,experimental_blockade=False,thresholds_promoted=False),warning="ipSAE and relaxation are diagnostic; no cherry-picking best model; control reference is author design only")
 atomic_json(run.path/"outputs/results.json",result);run.output("results",run.path/"outputs/results.json")
 print(run.finish("AF2_REVIEW_SCORED" if all(x["relaxation_status"]=="COMPLETE" for x in rows) else "AF2_REVIEW_SCORED_WITH_RELAX_FAILURES","computational_only",dict(models=len(rows),relaxation_failures=sum(x["relaxation_status"]!="COMPLETE" for x in rows))),flush=True)
except Exception as error:run.fail(error);raise

