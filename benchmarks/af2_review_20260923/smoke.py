import os,shutil
from pathlib import Path
from ppiblocker.common import *
from ppiblocker.af2_review import inspect,pose_distance
root=Path("/lustre/users/u21111210118/projects/test9");run=Run(root,"76_af2_review_smoke",[]);shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 p=next((root/"steps/73_af2_review_setup/runs").glob("*/manifest.json"));m=read_json(p);e=read_json(verify_file(m["outputs"]["plan"]))["entries"][2];z=e["baseline_models"][0]
 raw=verify_file(z["pdb"]);scores=verify_file(z["scores"]);local=run.path/"work/model.pdb";shutil.copy2(raw,local)
 env=os.environ.copy();env.update(PYTHONNOUSERSITE="1",CUDA_VISIBLE_DEVICES="",JAX_PLATFORMS="cpu",OPENMM_CPU_THREADS="2",OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="2");env.pop("PYTHONPATH",None);env.pop("LD_LIBRARY_PATH",None)
 out=run.path/"outputs/relaxed.pdb";rr=run.path/"outputs/relaxation.json"
 checked_command([root/"env/bindcraft/bin/python",root/"source/benchmarks/af2_review_20260923/relax_worker.py",local,out,rr],run.path/"work",run.path/"logs/relax.log",env,timeout=600)
 before,a=inspect(e,local,scores);after,b=inspect(e,out,scores)
 source=read_json(verify_file(m["outputs"]["ipsae_source"]));code=verify_file(source["files"]["ipsae.py"])
 checked_command([root/"env/core/bin/python",code,scores,local,"10","15"],run.path/"work",run.path/"logs/ipsae.log",env,timeout=120)
 atomic_json(run.path/"outputs/comparison.json",dict(id=e["id"],before=before,after=after,movement=pose_distance(a,b)))
 run.output("comparison",run.path/"outputs/comparison.json");run.output("relaxation",rr);run.output("ipsae",run.path/"work/model_10_15.txt")
 print(run.finish("RELAX_AND_IPSAE_SMOKE_PASSED","engineering_only"),flush=True)
except Exception as e:run.fail(e);raise

