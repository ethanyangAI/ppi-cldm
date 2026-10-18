import ctypes,os,subprocess,json
from pathlib import Path
for k in ("CUDA_VISIBLE_DEVICES","LD_LIBRARY_PATH","XLA_FLAGS","PATH"):print(k,os.environ.get(k),flush=True)
subprocess.run(["nvidia-smi"],check=False)
for lib in ["libcuda.so.1","libcudart.so.11.0","libcublas.so.11","libcusolver.so.11","libcudnn.so.8","libcufft.so.10","libcusparse.so.11","libnccl.so.2"]:
 try:
  ctypes.CDLL(lib);print("LOAD_OK",lib,flush=True)
 except Exception as e:print("LOAD_FAIL",lib,str(e),flush=True)
import jax
print(jax.devices(),flush=True)
