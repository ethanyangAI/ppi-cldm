import os,sys,shutil
from pathlib import Path
from ppiblocker.common import Run,record_file,atomic_json,checked_command
root=Path("/lustre/users/u21111210118/projects/test9")
plan=root/"steps/21_benchmark_analysis/runs/20260922T051817Z_f84fa156702c/outputs/af2_plan.json"
run=Run(root,"24_target_msa",[record_file(plan)])
shutil.copy2(__file__,run.path/"qc/driver.py")
worker=root/"steps/24_target_msa/code/fetch.py";shutil.copy2(worker,run.path/"qc/fetch.py")
try:
 env=os.environ.copy();env.update(PYTHONNOUSERSITE="1",JAX_PLATFORMS="cpu",CUDA_VISIBLE_DEVICES="");env.pop("PYTHONPATH",None)
 checked_command([root/"env/colabfold/bin/python",worker,plan,run.path/"work/msa"],run.path/"work",run.path/"logs/retrieval.log",env,timeout=1200)
 records={cid:record_file(run.path/"work/msa"/(cid+".a3m")) for cid in ["P06","P09"]}
 out=run.path/"outputs/msa_receipt.json";atomic_json(out,dict(targets=records,endpoint="https://api.colabfold.com",uploaded="Only the two public reference target-domain sequences; no generated binder sequences.",paired_msa=False,templates=False,track="posthoc target-MSA verifier sensitivity"));run.output("receipt",out)
 print(run.finish("PUBLIC_TARGET_MSA_COMPLETE","input_metadata"),flush=True)
except Exception as e:run.fail(e);raise

