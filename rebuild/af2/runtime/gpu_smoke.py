import os,json,time,subprocess
from pathlib import Path
import jax,jax.numpy as jnp
from alphafold.model import config,data
s=Path("/lustre/users/u21111210118/projects/test9/steps/03_af2_restore")
devices=jax.devices();assert devices and all(x.platform=="gpu" for x in devices),devices
x=jnp.arange(512*512,dtype=jnp.float32).reshape(512,512)/262144
y=jax.jit(lambda a:a@a.T)(x);y.block_until_ready()
assert bool(jnp.isfinite(y).all())
cfg=config.model_config("model_1_multimer_v3")
receipt={"status":"GPU_KERNEL_SMOKE_VERIFIED_PROTEIN_INFERENCE_PENDING","slurm_job_id":os.environ.get("SLURM_JOB_ID"),"timestamp":time.time(),"devices":[str(x) for x in devices],"jax":jax.__version__,"gpu_operation":"JIT512x512matmul finite output","scope":"CUDA/JAX runtime check only; no AF2 protein prediction claimed.","nvidia_smi":subprocess.check_output(["nvidia-smi","--query-gpu=name,driver_version,memory.total","--format=csv,noheader"],text=True).strip()}
(s/"gpu_smoke_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n");print(json.dumps(receipt,indent=2),flush=True)
