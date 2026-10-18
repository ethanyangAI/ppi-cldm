import os, json, time, importlib.metadata as m, hashlib
from pathlib import Path
import jax, numpy, scipy
from colabfold.batch import run
from alphafold.model import config, data, model
root=Path("/lustre/users/u21111210118/projects/test9")
s=root/"steps/03_af2_restore"
packages={p:m.version(p) for p in ["colabfold","alphafold-colabfold","jax","jaxlib","dm-haiku","numpy","scipy","tensorflow-cpu","flax","optax","chex","orbax-checkpoint","dm-tree"]}
assert packages["colabfold"]=="1.5.5"
assert packages["jaxlib"]=="0.4.23+cuda11.cudnn86"
receipt={"status":"CPU_RUNTIME_IMPORTS_VERIFIED_GPU_INFERENCE_PENDING","timestamp":time.time(),"slurm_job_id":os.environ.get("SLURM_JOB_ID"),"packages":packages,"cpu_devices":[str(x) for x in jax.devices()],"scope":"Package installation/import test only; no protein prediction or GPU readiness claimed.","protocol":{"model_type":"alphafold2_multimer_v3","num_models":5,"num_seeds":3,"random_seed":1042,"num_recycle":12,"max_msa":"128:256","templates":False}}
(s/"runtime_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2),flush=True)
