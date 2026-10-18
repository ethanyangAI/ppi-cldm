import sys,json,hashlib
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,require
root=Path("/lustre/users/u21111210118/projects/test9")
jobs=set(sys.argv[1:]);assert len(jobs)==7
selected=[]
for step in ["19_af2_verification","25_af2_msa_verification"]:
 for p in (root/"steps"/step/"runs").glob("*/manifest.json"):
  m=read_json(p)
  if m.get("execution",{}).get("slurm_job_id") in jobs:selected.append((step,p,m))
assert len(selected)==7
run=Run(root,"23_benchmark_report",[record_file(p) for _,p,_ in selected])
try:
 records=[];seen=set();n_models=0;configs=[]
 for step,p,m in selected:
  require(m["status"]=="AF2_VERIFICATION_COMPLETE","INCOMPLETE_AF2",str(p))
  rows=read_json(verify_file(m["outputs"]["results"]))
  config=read_json(p.parent/"work/af2/config.json")
  if step=="25_af2_msa_verification":
   assert config["msa_mode"]=="mmseqs2_uniref_env"
   assert config["max_seq"]==128 and config["max_extra_seq"]==256
  else:assert config["max_seq"]==1
  configs.append(dict(manifest=str(p),config=record_file(p.parent/"work/af2/config.json"),msa_mode=config["msa_mode"],max_seq=config["max_seq"],max_extra_seq=config["max_extra_seq"]))
  for row in rows:
   key=(step,row["id"]);assert key not in seen;seen.add(key)
   assert len(row["models"])==3
   seeds=set()
   for model in row["models"]:
    for field in ["pdb","scores"]:
     f=verify_file(model[field]);records.append(record_file(f))
    seeds.add(int(Path(model["pdb"]["path"]).stem.rsplit("_seed_",1)[1]))
   assert seeds=={1042,1043,1044}
   n_models+=3
 assert n_models==258
 output=run.path/"outputs/evidence_acceptance.json"
 atomic_json(output,dict(models=n_models,sequences=len(seen),verified_model_files=len(records),configs=configs,all_model_records=records))
 run.output("acceptance",output)
 print(run.finish("AF2_EVIDENCE_ACCEPTED","artifact_integrity"),flush=True)
except Exception as e:run.fail(e);raise
