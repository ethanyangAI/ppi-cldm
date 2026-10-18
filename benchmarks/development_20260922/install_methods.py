import os,sys,shutil,requests,tarfile,json
from pathlib import Path
from ppiblocker.common import Run,record_file,read_json,atomic_json,checked_command,require,verify_file
root=Path("/lustre/users/u21111210118/projects/test9");method=sys.argv[1]
run=Run(root,"40_method_install",[])
shutil.copy2(__file__,run.path/"qc/driver.py");run.manifest["method"]=method;run.save()
env=os.environ.copy();env.update(PYTHONNOUSERSITE="1",PIP_CACHE_DIR=str(root/"cache/pip"),CONDA_PKGS_DIRS=str(root/"cache/conda_pkgs"),TMPDIR=str(root/"cache/benchmark_tmp"))
env.pop("PYTHONPATH",None)
env["MAMBA_ROOT_PREFIX"]=str(root/"env/mamba")
def command(args,name,timeout=3600):return checked_command(args,run.path/"work",run.path/"logs"/(name+".log"),env,timeout)
def source(repo,revision,dest):
 if dest.exists():
  require((dest/".source_receipt.json").exists(),"UNPINNED_VENDOR",str(dest))
  require(read_json(dest/".source_receipt.json")["revision"]==revision,"VENDOR_REVISION",str(dest));return dest
 url=f"https://api.github.com/repos/{repo}/tarball/{revision}"
 p=run.path/"work"/(dest.name+".tar.gz")
 with requests.get(url,stream=True,timeout=(30,120)) as r:
  r.raise_for_status()
  with p.open("wb") as f:
   for b in r.iter_content(1024*1024):f.write(b)
 work=run.path/"work"/(dest.name+"_unpack");work.mkdir()
 with tarfile.open(p) as t:
  members=[];skipped=[]
  for m in t.getmembers():
   require(not (Path(m.name).is_absolute() or ".." in Path(m.name).parts),"ARCHIVE_PATH",m.name)
   if m.issym() or m.islnk():
    require("/docs/" in m.name,"ARCHIVE_LINK",m.name);skipped.append(dict(path=m.name,target=m.linkname));continue
   require(m.isfile() or m.isdir(),"ARCHIVE_SPECIAL",m.name);members.append(m)
  t.extractall(work,members=members)
  atomic_json(run.path/"qc"/(dest.name+"_skipped_documentation_links.json"),skipped)
 folders=list(work.iterdir());require(len(folders)==1,"ARCHIVE_ROOT",str(p));shutil.move(str(folders[0]),dest)
 atomic_json(dest/".source_receipt.json",dict(repo=repo,revision=revision,url=url,archive=record_file(p)))
 run.output(dest.name+"_source",dest/".source_receipt.json")
 return dest
try:
 conda=Path(os.environ["HOME"])/"miniconda3/bin/conda"
 if method=="bindcraft":
  vendor=source("martinpacesa/BindCraft","7713aa0d0d351e4117a8befeb8541f3a8ebd3368",root/"vendor/BindCraft")
  if (root/"vendor/ColabDesign/.source_receipt.json").exists():revision=read_json(root/"vendor/ColabDesign/.source_receipt.json")["revision"]
  else:
   api=requests.get("https://api.github.com/repos/sokrypton/ColabDesign/commits/main",timeout=60);api.raise_for_status();revision=api.json()["sha"]
  cd=source("sokrypton/ColabDesign",revision,root/"vendor/ColabDesign")
  prefix=root/"env/bindcraft"
  if not (prefix/"bin/python").exists():command([conda,"create","-y","--prefix",prefix,"--clone",root/"env/colabfold"],"conda",1800)
  py=prefix/"bin/python"
  command([py,"-m","pip","install","--no-deps",cd],"colabdesign",1200)
  command([py,"-m","pip","install","setuptools==80.9.0","numpy==1.24.3","pandas==1.5.3","matplotlib==3.10.9","seaborn==0.12.2","biopython==1.82","openmm==8.1.1","py3Dmol","joblib","tqdm"],"extras",1800)
  if (root/"vendor/pdbfixer/.source_receipt.json").exists():fixrev=read_json(root/"vendor/pdbfixer/.source_receipt.json")["revision"]
  else:
   fx=requests.get("https://api.github.com/repos/openmm/pdbfixer/commits/1.9",timeout=60);fx.raise_for_status();fixrev=fx.json()["sha"]
  fix=source("openmm/pdbfixer",fixrev,root/"vendor/pdbfixer")
  command([py,"-m","pip","install","--no-deps",fix],"pdbfixer",600)
  wheel_receipt=root/"steps/58_pyrosetta_download/runs/20260922T110912Z_25a67cd73080/outputs/receipt.json"
  wheel=verify_file(read_json(wheel_receipt)["wheel"]);run.output("pyrosetta_source",wheel_receipt)
  command([py,"-m","pip","install",wheel],"pyrosetta",1200)
  command([py,"-c","import colabdesign,pyrosetta,jax,pdbfixer;print(jax.__version__)"],"imports",600)
 else:
  vendor=source("RosettaCommons/foundry","b02eed6a6bdf8f44d14a80cc36e3da13c9f2291c",root/"vendor/foundry")
  prefix=root/"env/rfd3"
  if not (prefix/"bin/python").exists():command([conda,"create","-y","--prefix",prefix,"python=3.12","pip"],"conda",1200)
  py=prefix/"bin/python"
  command([root/"env/tools/bin/micromamba","install","-y","--prefix",prefix,"--override-channels","-c","conda-forge","rdkit=2024.09.6","numpy<2.3","pandas<2.3","scipy<1.16"],"rdkit_mamba",1800)
  command([py,"-m","pip","install","torch==2.5.1","--index-url","https://download.pytorch.org/whl/cu118"],"torch",3600)
  constraint=run.path/"work/constraints.txt";constraint.write_text("torch==2.5.1\nnumpy<2.3\npandas<2.3\nscipy<1.16\n")
  command([py,"-m","pip","install","--prefer-binary","-c",constraint,str(vendor)+"[rfd3]"],"foundry",3600)
  command([prefix/"bin/rfd3","--help"],"cli",600)
  # Only rfd3 weights, own project directory, no global cleanup.
  env["FOUNDRY_CHECKPOINT_DIRS"]=str(root/"assets/rfd3")
  command([prefix/"bin/foundry","install","rfd3","--checkpoint-dir",root/"assets/rfd3"],"weights",3600)
 command([py,"-m","pip","check"],"pipcheck",120)
 command([py,"-m","pip","freeze"],"freeze",120)
 run.output("freeze",run.path/"logs/freeze.log")
 print(run.finish("METHOD_INSTALL_IMPORT_ACCEPTED","installation_only_not_gpu_acceptance",dict(prefix=str(prefix))),flush=True)
except Exception as e:run.fail(e);raise

