import os,sys,shutil,re
from pathlib import Path
from ppiblocker.common import *
from ppiblocker.backends import require_gpu
root=Path("/lustre/users/u21111210118/projects/test9");slot=int(sys.argv[1]);run=Run(root,"80_strengthening_predict",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 require_gpu()
 found=[(p,read_json(p)) for p in (root/"steps/79_strengthening_setup/runs").glob("*/manifest.json") if read_json(p)["status"]=="STRENGTHENING_INPUTS_READY"]
 require(len(found)==1,"SETUP_NOT_UNIQUE",str(len(found)));up,m=found[0];plan=verify_file(m["outputs"]["plan"]);e=read_json(plan)["entries"][slot]
 protocol_path=verify_file(read_json(plan)["protocol"]);protocol=read_json(protocol_path)["prediction"]
 run.manifest.update(inputs=[record_file(up),record_file(plan),record_file(protocol_path)],entry_id=e["id"],slot=slot);run.save()
 assets=root/"env/colabfold-assets.json"
 for f in read_json(assets)["weights"]:verify_file(f)
 run.output("assets",assets)
 inputs=run.path/"work/inputs";inputs.mkdir();shutil.copy2(verify_file(e["msa"]),inputs/(e["id"]+".a3m"))
 env=os.environ.copy();site=root/"env/colabfold/lib/python3.10/site-packages"
 env.update(PYTHONNOUSERSITE="1",XLA_PYTHON_CLIENT_PREALLOCATE="false",TF_FORCE_UNIFIED_MEMORY="0",OMP_NUM_THREADS="4",OPENBLAS_NUM_THREADS="1",MKL_NUM_THREADS="1",TF_NUM_INTRAOP_THREADS="4",TF_NUM_INTEROP_THREADS="1",PYTHONUNBUFFERED="1")
 env.pop("PYTHONPATH",None);env["LD_LIBRARY_PATH"]=":".join(str(x) for x in sorted((site/"nvidia").glob("*/lib")))+":"+str(root/"env/colabfold/lib")
 env["PATH"]=str(root/"env/colabfold/bin")+":"+str(site/"nvidia/cuda_nvcc/bin")+":"+env.get("PATH","")
 env["XLA_FLAGS"]="--xla_gpu_cuda_data_dir="+str(site/"nvidia/cuda_nvcc")
 def predict(arm,num,recycles):
  out=run.path/"work"/arm
  args=[root/"env/colabfold/bin/colabfold_batch",inputs,out,"--model-type","alphafold2_multimer_v3","--num-models",str(num),"--model-order",",".join(map(str,range(1,num+1))),"--num-seeds","3","--random-seed","1042","--num-recycle",str(recycles),"--recycle-early-stop-tolerance","0.5","--stop-at-score","100","--msa-mode","mmseqs2_uniref_env","--max-msa","128:256","--num-relax","0","--data",root/"assets/colabfold"]
  checked_command(args,run.path/"work",run.path/"logs"/(arm+".log"),env,timeout=18000)
  pdbs=sorted(out.glob(e["id"]+"_unrelaxed_rank_*.pdb"));require(len(pdbs)==3*num,"MODEL_COUNT",str(len(pdbs)))
  models=[];keys=set()
  for p in pdbs:
   match=re.search(r"model_(\d+)_seed_(\d+)",p.name);require(match,"MODEL_NAME",p.name)
   key=tuple(map(int,match.groups()));keys.add(key)
   scores=p.with_name(p.name.replace("_unrelaxed_","_scores_").replace(".pdb",".json"))
   models.append(dict(pdb=record_file(p),scores=record_file(scores),weight=key[0],seed=key[1]))
  require(keys=={(i,s) for i in range(1,num+1) for s in (1042,1043,1044)},"ENSEMBLE_COVERAGE",str(keys))
  return models
 baseline=e["baseline_models"]
 if not baseline:baseline=predict("legacy_missing",1,3)
 else:
  for z in baseline:verify_file(z["pdb"]);verify_file(z["scores"])
 revised=predict("expanded",5,12)
 atomic_json(run.path/"outputs/predictions.json",dict(entry=e,baseline=baseline,expanded=revised,protocol=record_file(protocol_path),scientific_parameters_unchanged_except_ensemble_and_recycles=True))
 run.output("predictions",run.path/"outputs/predictions.json")
 print(run.finish("AF2_REVIEW_PREDICTION_COMPLETE","computational_only",dict(expanded_models=15,baseline_models=3)),flush=True)
except Exception as e:run.fail(e);raise

