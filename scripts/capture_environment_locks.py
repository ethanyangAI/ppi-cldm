import json,os,subprocess
from pathlib import Path
root=Path("/lustre/users/u21111210118/projects/test9")
out=root/"source/environment";out.mkdir(exist_ok=True)
env=os.environ.copy();env["PYTHONNOUSERSITE"]="1";env["MAMBA_ROOT_PREFIX"]=str(root/"env/mamba");env.pop("PYTHONPATH",None)
versions={}
for name in ("core","rfd","boltz"):
 python=root/"env"/name/"bin/python"
 raw=subprocess.check_output([str(python),"-m","pip","freeze"],text=True,env=env)
 lines=[s for s in raw.splitlines() if s and not s.startswith(("#","-e ")) and " @ file:" not in s]
 (out/f"{name}-pip-lock.txt").write_text("\n".join(lines)+"\n")
 explicit=subprocess.check_output([str(root/"env/tools/bin/micromamba"),"list","--no-rc","--explicit","-p",str(root/"env"/name)],text=True,env=env)
 (out/f"{name}-conda-explicit.txt").write_text(explicit)
 versions[name]=subprocess.check_output([str(python),"--version"],text=True,env=env).strip()
 print(name,len(lines),"pip packages",flush=True)
(out/"python-versions.json").write_text(json.dumps(versions,indent=2)+"\n")
