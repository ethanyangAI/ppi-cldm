import os,shutil
from pathlib import Path
from ppiblocker.common import Run,record_file,atomic_json,checked_command,require
root=Path("/lustre/users/u21111210118/projects/test9");run=Run(root,"63_bindcraft_glibc",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
env=os.environ.copy();env.update(PYTHONNOUSERSITE="1",MAMBA_ROOT_PREFIX=str(root/"env/mamba"),CONDA_PKGS_DIRS=str(root/"cache/conda_pkgs"));env.pop("PYTHONPATH",None)
try:
 prefix=root/"env/bindcraft_compat"
 checked_command([root/"env/tools/bin/micromamba","create","-y","-p",prefix,"--override-channels","-c","conda-forge","sysroot_linux-64=2.28","patchelf"],run.path/"work",run.path/"logs/install.log",env,timeout=1800)
 candidates=list(prefix.glob("*/sysroot/lib64/ld-linux-x86-64.so.2"));require(len(candidates)==1,"LOADER_PATH",str(candidates));loader=candidates[0].resolve()
 # Break conda hardlinks before modifying our private interpreter.
 python=root/"env/bindcraft/bin/python3.10";backup=run.path/"qc/python3.10.before";shutil.copy2(python,backup)
 temp=python.with_name("python3.10.compat.tmp");shutil.copy2(python,temp);os.replace(temp,python)
 records=[]
 for src,dest in [(python,python),(root/"vendor/BindCraft/functions/dssp",root/"assets/bindcraft/bin/dssp"),(root/"vendor/BindCraft/functions/DAlphaBall.gcc",root/"assets/bindcraft/bin/DAlphaBall.gcc")]:
  dest.parent.mkdir(parents=True,exist_ok=True)
  if src!=dest:shutil.copy2(src,dest)
  dest.chmod(dest.stat().st_mode | 0o111)
  if dest.name=="dssp":
   records.append(record_file(dest));continue # Vendor DSSP is static: preserve and execute directly.
  checked_command([prefix/"bin/patchelf","--set-interpreter",loader,"--force-rpath","--set-rpath",str(loader.parent)+":"+str(root/"env/bindcraft/lib"),dest],run.path/"work",run.path/"logs"/(dest.name+"_patch.log"),env,timeout=120)
  records.append(record_file(dest))
 checked_command([python,"-c","import pyrosetta,colabdesign,jax,pdbfixer;pyrosetta.init('-mute all');print('IMPORT_AND_PYROSETTA_INIT_OK',jax.__version__)"],run.path/"work",run.path/"logs/imports.log",env,timeout=600)
 checked_command([root/"assets/bindcraft/bin/dssp","--version"],run.path/"work",run.path/"logs/dssp.log",env,timeout=120)
 checked_command([python,"-m","pip","check"],run.path/"work",run.path/"logs/pipcheck.log",env,timeout=120)
 checked_command([python,"-m","pip","freeze"],run.path/"work",run.path/"logs/freeze.log",env,timeout=120)
 atomic_json(run.path/"outputs/runtime.json",dict(scope="private BindCraft prefix only; host and other environments untouched",loader=record_file(loader),patched_binaries=records,original_python=record_file(backup),pyrosetta_source=record_file(root/"steps/58_pyrosetta_download/runs/20260922T110912Z_25a67cd73080/outputs/receipt.json")))
 run.output("runtime",run.path/"outputs/runtime.json");run.output("imports",run.path/"logs/imports.log");run.output("freeze",run.path/"logs/freeze.log")
 print(run.finish("BINDCRAFT_PRIVATE_RUNTIME_ACCEPTED","import_only_not_gpu_acceptance"),flush=True)
except Exception as e:run.fail(e);raise
