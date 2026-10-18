import os,sys,json,time,hashlib,datetime,uuid,subprocess,shutil
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/08_candidate_refolds"
slot=int(sys.argv[1]);plan=json.loads((S/"plan.json").read_text());entry=plan["entries"][slot];assert entry["slot"]==slot
def rec(p):
 b=p.read_bytes();return {"path":str(p),"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
def verify(x):assert rec(Path(x["path"]))==x
verify(entry["input"]);verify(plan["runtime_acceptance"]);verify(plan["runtime_environment"])
rid=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"_"+uuid.uuid4().hex[:12]
run=S/"runs"/rid
for d in ("outputs","logs","qc"):(run/d).mkdir(parents=True,exist_ok=False)
shutil.copy2(__file__,run/"qc/worker.py");shutil.copy2(S/"plan.json",run/"qc/plan.json")
manifest={"status":"RUNNING","run_id":rid,"entry":entry,"slot":slot,"job_id":os.environ.get("SLURM_JOB_ID"),"array_job_id":os.environ.get("SLURM_ARRAY_JOB_ID"),"inputs":[rec(S/"plan.json"),entry["input"],plan["runtime_acceptance"]],"started":time.time(),"coordinate_provenance":"NEW_PREDICTIONS_NOT_RESTORED_OLD_COORDINATES"}
def save():
 p=run/"manifest.json";tmp=p.with_suffix(".partial");tmp.write_text(json.dumps(manifest,indent=2)+"\n");tmp.replace(p)
save()
try:
 import jax
 devices=jax.devices();assert devices and all(d.platform=="gpu" for d in devices),devices
 manifest["gpu"]={"devices":[str(d) for d in devices],"nvidia_smi":subprocess.check_output(["nvidia-smi","--query-gpu=name,driver_version,memory.total","--format=csv,noheader"],text=True).strip()}
 argv=[str(R/"env/colabfold/bin/colabfold_batch"),entry["input"]["path"],str(run/"outputs/af2"),"--model-type",entry["model_type"],"--num-models","5","--model-order","1,2,3,4,5","--num-seeds","3","--random-seed","1042","--num-recycle","12","--recycle-early-stop-tolerance","0.5","--max-msa","128:256","--msa-mode",("mmseqs2_uniref_env" if entry["mode"]=="complex" else "single_sequence"),"--num-relax","0","--data",str(R/"assets/colabfold")]
 manifest["argv"]=argv;save();print("RUN_START",rid,slot,entry["id"],entry["mode"],flush=True)
 with (run/"logs/colabfold.log").open("w") as f:
  proc=subprocess.Popen(argv,stdout=f,stderr=subprocess.STDOUT)
  started=time.time()
  try:
   while True:
    cfgpath=run/"outputs/af2/config.json"
    if cfgpath.exists():
     cfg=json.loads(cfgpath.read_text())
     assert cfg["max_seq"]==(128 if entry["mode"]=="complex" else 1),cfg
     assert cfg["max_extra_seq"]==(256 if entry["mode"]=="complex" else 1),cfg
     assert cfg["num_recycles"]==12 and cfg["num_models"]==5 and cfg["num_seeds"]==3
     assert cfg["num_relax"]==0 and cfg["use_templates"] is False
     manifest["effective_config"]=cfg;save()
    if proc.poll() is not None:
     if proc.returncode:raise subprocess.CalledProcessError(proc.returncode,argv)
     break
    if time.time()-started>23*3600:raise TimeoutError("AF2 worker walltime exceeded")
    time.sleep(5)
  except BaseException:
   proc.terminate()
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:proc.kill();proc.wait()
   raise
 pdbs=list((run/"outputs/af2").glob("*_unrelaxed_rank_*.pdb"));scores=list((run/"outputs/af2").glob("*_scores_rank_*.json"))
 assert len(pdbs)==15 and len(scores)==15,(len(pdbs),len(scores))
 manifest.update(status="AF2_PREDICTIONS_GENERATED_PENDING_CPU_ACCEPTANCE",finished=time.time(),model_count=len(pdbs),output_directory=str(run/"outputs/af2"));save();print("RUN_PREDICTIONS_COMPLETE",rid,flush=True)
except BaseException as e:
 manifest.update(status="FAILED",finished=time.time(),error=repr(e));save();raise
