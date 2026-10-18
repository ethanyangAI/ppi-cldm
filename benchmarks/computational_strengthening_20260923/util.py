import os,sys,copy
from pathlib import Path
import numpy as np
from Bio.PDB import PDBParser,MMCIFParser
from Bio.SeqUtils import seq1
from ppiblocker.common import *
from ppiblocker.structure import superpose,interface,transform,write_pdb
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"source/benchmarks/computational_strengthening_20260923"
SETUP=R/"steps/79_strengthening_setup/runs/20260923T152051Z_d7a87092fe92/manifest.json"
def baseplan():return read_json(verify_file(read_json(SETUP)["outputs"]["plan"]))
def one(step,status):
 found=[(p,read_json(p)) for p in (R/"steps"/step/"runs").glob("*/manifest.json") if read_json(p)["status"]==status]
 require(len(found)==1,"AMBIGUOUS_RUN",str((step,len(found))));return found[0]
def chains(path):
 parser=MMCIFParser(QUIET=True,auth_chains=False) if str(path).endswith(".cif") else PDBParser(QUIET=True)
 out=[]
 for c in next(parser.get_structure("x",str(path)).get_models()):
  rs=[];aa=[];heavy=[]
  for r in c:
   l=seq1(r.resname)
   if l=="X" or "CA" not in r:continue
   a=[(v.name,v.element,np.asarray(v.coord,float)) for v in r if v.element not in ("H","D")]
   rs.append(dict(name=r.resname,letter=l,number=r.id[1],icode=r.id[2].strip(),bfactor=float(r["CA"].bfactor),ca=np.asarray(r["CA"].coord,float)));aa.append(a);heavy.append(np.array([v[2] for v in a]))
  if rs:out.append(dict(id=c.id,sequence="".join(r["letter"] for r in rs),residues=rs,atoms=aa,heavy=heavy))
 return out
def ca(c):return np.array([r["ca"] for r in c["residues"]])
def env(gpu=False):
 e=os.environ.copy();e.update(PYTHONNOUSERSITE="1",OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="2",MKL_NUM_THREADS="1",OPENMM_CPU_THREADS="2");e.pop("PYTHONPATH",None)
 if gpu:
  site=R/"env/colabfold/lib/python3.10/site-packages"
  e.update(XLA_PYTHON_CLIENT_PREALLOCATE="false",TF_FORCE_UNIFIED_MEMORY="0",TF_NUM_INTRAOP_THREADS="4",TF_NUM_INTEROP_THREADS="1",XLA_FLAGS="--xla_gpu_cuda_data_dir="+str(site/"nvidia/cuda_nvcc"))
  e["LD_LIBRARY_PATH"]=":".join(str(x) for x in sorted((site/"nvidia").glob("*/lib")))+":"+str(R/"env/colabfold/lib")
  e["PATH"]=str(R/"env/colabfold/bin")+":"+str(site/"nvidia/cuda_nvcc/bin")+":"+e.get("PATH","")
 else:e.update(CUDA_VISIBLE_DEVICES="",JAX_PLATFORMS="cpu");e.pop("LD_LIBRARY_PATH",None)
 return e

