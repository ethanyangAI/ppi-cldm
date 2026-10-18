"""All-78 control inference with immutable input receipts and CPU validation."""
import os,sys,json,time,re,hashlib,subprocess,shutil,datetime
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/17_control_calibration"
def rec(p):
 p=Path(p);return {"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}
def verify(row):
 r=rec(row["path"]);assert r["sha256"]==row["sha256"],row["path"]
 if "bytes" in row:assert r["bytes"]==row["bytes"]
 return Path(row["path"])
def dump(p,obj,exclusive=False):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 if exclusive:
  with p.open("x") as f:json.dump(obj,f,indent=2,allow_nan=False);f.write("\n")
 else:
  tmp=p.with_suffix(p.suffix+".partial");tmp.write_text(json.dumps(obj,indent=2,allow_nan=False)+"\n");tmp.replace(p)
def config_valid(cfg):
 assert cfg["max_seq"]==128 and cfg["max_extra_seq"]==256
 assert cfg["num_recycles"]==12 and cfg["num_models"]==5 and cfg["num_seeds"]==3
 assert cfg["num_relax"]==0 and cfg["use_templates"] is False
 assert cfg["model_type"]=="alphafold2_multimer_v3"
 assert cfg["random_seed"]==1042
 assert cfg["recycle_early_stop_tolerance"]==0.5
def worker(slot):
 plan=json.loads((S/"plan.json").read_text());msa=json.loads((S/"inputs/msa_acceptance.json").read_text())
 verify(msa["plan"]);e=plan["conditions"][slot];assert e["new_slot"]==slot
 inp=next(x for x in msa["conditions"] if x["condition_id"]==e["condition_id"]);verify(inp["input"])
 verify(plan["runtime_acceptance"]);verify(plan["runtime_environment"])
 for x in plan["code"]:verify(x)
 array=os.environ["SLURM_ARRAY_JOB_ID"];run=S/"runs"/("array_"+array)/("task_"+str(slot))
 run.mkdir(parents=True,exist_ok=False)
 for name in ("outputs","logs","qc"):(run/name).mkdir()
 shutil.copy2(__file__,run/"qc/executed_control_review.py");shutil.copy2(S/"plan.json",run/"qc/plan.json")
 m={"status":"RUNNING","array_job_id":array,"job_id":os.environ["SLURM_JOB_ID"],"slot":slot,"condition":e,"inputs":[rec(S/"plan.json"),rec(S/"inputs/msa_acceptance.json"),inp["input"],plan["runtime_acceptance"],plan["runtime_environment"]],"started_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"coordinate_provenance":"NEW_CONTROL_PREDICTION_NOT_OLD_COORDINATES"}
 dump(run/"manifest.json",m)
 try:
  import jax
  devices=jax.devices();assert devices and all(x.platform=="gpu" for x in devices);m["gpu"]=[str(x) for x in devices]
  argv=[str(R/"env/colabfold/bin/colabfold_batch"),inp["input"]["path"],str(run/"outputs/af2"),"--model-type","alphafold2_multimer_v3","--num-models","5","--model-order","1,2,3,4,5","--num-seeds","3","--random-seed","1042","--num-recycle","12","--recycle-early-stop-tolerance","0.5","--max-msa","128:256","--msa-mode","mmseqs2_uniref_env","--num-relax","0","--data",str(R/"assets/colabfold")]
  m["argv"]=argv;dump(run/"manifest.json",m);print("RUN_START",str(run),e["condition_id"],flush=True)
  with (run/"logs/colabfold.log").open("w") as log:
   proc=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT);started=time.time();checked=False
   try:
    while True:
     cp=run/"outputs/af2/config.json"
     if cp.exists() and not checked:
      cfg=json.loads(cp.read_text());config_valid(cfg);m["effective_config"]=cfg;dump(run/"manifest.json",m);checked=True
     if proc.poll() is not None:
      if proc.returncode:raise subprocess.CalledProcessError(proc.returncode,argv)
      break
     if time.time()-started>110*60:raise TimeoutError("Bounded inference exceeded 110 minutes")
     time.sleep(5)
   except BaseException:
    proc.terminate()
    try:proc.wait(timeout=10)
    except subprocess.TimeoutExpired:proc.kill();proc.wait()
    raise
  assert checked
  assert len(list((run/"outputs/af2").glob("*_unrelaxed_rank_*.pdb")))==15
  assert len(list((run/"outputs/af2").glob("*_scores_rank_*.json")))==15
  m.update(status="PREDICTIONS_GENERATED_PENDING_CPU_ACCEPTANCE",finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsed_seconds=time.time()-started,output_directory=str(run/"outputs/af2"))
  dump(run/"manifest.json",m);print("RUN_COMPLETE",e["condition_id"],flush=True)
 except BaseException as exc:
  m.update(status="FAILED",error=repr(exc));dump(run/"manifest.json",m);raise
def validate(array):
 import numpy as np
 from Bio.PDB import PDBParser
 from Bio.SeqUtils import seq1
 plan=json.loads((S/"plan.json").read_text());rows=[];errors=[]
 msa=json.loads((S/"inputs/msa_acceptance.json").read_text());verify(msa["plan"])
 for x in plan["code"]:verify(x)
 for t in msa["targets"].values():verify(t["input"])
 for e in plan["conditions"]:
  try:
   inp=next(x for x in msa["conditions"] if x["condition_id"]==e["condition_id"]);verify(inp["input"])
   mp=S/"runs"/("array_"+array)/("task_"+str(e["new_slot"]))/"manifest.json";m=json.loads(mp.read_text())
   assert m["status"]=="PREDICTIONS_GENERATED_PENDING_CPU_ACCEPTANCE";assert m["condition"]==e
   for record in m["inputs"]:verify(record)
   cfgp=Path(m["output_directory"])/"config.json";cfg=json.loads(cfgp.read_text());assert cfg==m["effective_config"];config_valid(cfg)
   out=Path(m["output_directory"]);models=[];identities=set()
   savedmsa=out/(e["condition_id"]+".a3m")
   assert savedmsa.exists() and savedmsa.read_bytes()==Path(inp["input"]["path"]).read_bytes(),"actual saved MSA differs"
   for pdb in sorted(out.glob("*_unrelaxed_rank_*.pdb")):
    match=re.search(r"_model_(\d+)_seed_(\d+)\.pdb$",pdb.name);assert match
    model,seed=map(int,match.groups());assert (model,seed) not in identities;identities.add((model,seed))
    score=pdb.with_name(pdb.name.replace("_unrelaxed_","_scores_").replace(".pdb",".json"));sc=json.loads(score.read_text())
    st=PDBParser(QUIET=True).get_structure("x",pdb);pdbmodels=list(st.get_models());assert len(pdbmodels)==1
    chainobjs=list(pdbmodels[0]);assert [c.id for c in chainobjs]==["A","B"]
    res=[[r for r in c if r.id[0]==" "] for c in chainobjs]
    assert all("CA" in r and r.id[2]==" " for chain in res for r in chain)
    chains=["".join(seq1(r.resname) for r in chain) for chain in res]
    assert chains==[e["target_sequence"],e["sequence"]]
    assert all(np.isfinite(a.coord).all() for a in st.get_atoms())
    n=sum(map(len,chains));pae=np.asarray(sc["pae"]);plddt=np.asarray(sc["plddt"])
    assert pae.shape==(n,n) and plddt.shape==(n,) and np.isfinite(pae).all() and np.isfinite(plddt).all()
    assert (pae>=0).all() and ((plddt>=0)&(plddt<=100)).all()
    assert np.isfinite(sc["ptm"]) and np.isfinite(sc["iptm"]) and 0<=sc["iptm"]<=1 and 0<=sc["ptm"]<=1
    models.append({"model":model,"seed":seed,"pdb":rec(pdb),"scores":rec(score),"chain_lengths":list(map(len,chains)),"pae_shape":list(pae.shape)})
   assert identities=={(a,b) for a in range(1,6) for b in (1042,1043,1044)}
   assert len(list(out.glob("*_scores_rank_*.json")))==15
   rows.append({"condition":e,"manifest":rec(mp),"config":rec(cfgp),"actual_msa":rec(savedmsa),"models":models})
  except Exception as exc:errors.append({"condition_id":e["condition_id"],"error":repr(exc)})
 report={"status":"ALL_1170_CONTROL_MODELS_VERIFIED" if not errors and len(rows)==78 else "INCOMPLETE_CONTROL_MODELS","job_id":os.environ.get("SLURM_JOB_ID"),"array_job_id":array,"plan":rec(S/"plan.json"),"msa_acceptance":rec(S/"inputs/msa_acceptance.json"),"accepted_conditions":rows,"model_count":sum(len(x["models"]) for x in rows),"errors":errors,"scope":"Full sequences, chain/residue/model/seed completeness, finite coordinates/full PAE, effective config, exact actual saved MSA and input hashes. No experimental claims."}
 path=S/"outputs"/("acceptance_"+array+".json");dump(path,report,True)
 print(json.dumps({k:v for k,v in report.items() if k!="accepted_conditions"},indent=2),flush=True)
 if errors:raise RuntimeError(errors)
 dump(S/"outputs/acceptance.json",{"status":report["status"],"receipt":rec(path)},True)
if __name__=="__main__":
 command=sys.argv[1]
 if command=="worker":worker(int(sys.argv[2]))
 elif command=="validate":validate(sys.argv[2])
 else:raise ValueError(command)

