import os,shutil
from pathlib import Path
from ppiblocker.common import Run,record_file,read_json,verify_file,checked_command
root=Path("/lustre/users/u21111210118/projects/test9")
up=root/"steps/24_target_msa/runs/20260922T053230Z_5f5d81e4f519/manifest.json"
plan=root/"steps/21_benchmark_analysis/runs/20260922T051817Z_f84fa156702c/outputs/af2_plan.json"
run=Run(root,"25_af2_msa_verification",[record_file(up),record_file(plan)])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 m=read_json(up);assert m["status"]=="PUBLIC_TARGET_MSA_COMPLETE"
 receipt=verify_file(m["outputs"]["receipt"]);run.output("msa_receipt",receipt)
 worker=root/"steps/25_af2_msa_verification/code/serialize_parallel.py";shutil.copy2(worker,run.path/"qc/serialize.py")
 env=os.environ.copy();env.update(PYTHONNOUSERSITE="1",JAX_PLATFORMS="cpu",CUDA_VISIBLE_DEVICES="");env.pop("PYTHONPATH",None)
 checked_command([root/"env/colabfold/bin/python",worker,plan,receipt,run.path/"outputs/msa_queries"],run.path/"work",run.path/"logs/serialize.log",env,timeout=5400)
 run.output("inputs",run.path/"outputs/msa_queries/inputs.json")
 print(run.finish("MSA_INPUTS_VALIDATED","input_metadata"),flush=True)
except Exception as e:run.fail(e);raise

