#!/usr/bin/env bash
#SBATCH --job-name=t9-bindcraft-source
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=interactive
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/source_%j.out
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9
S="$R/steps/21_method_runtime"
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1
unset PYTHONPATH
export TMPDIR="$S/work" XDG_CACHE_HOME="$R/env/cache"
source /opt/app/conda/etc/profile.d/conda.sh
conda activate "$R/env/core"
if [ ! -d "$R/vendor/BindCraft" ]; then git clone https://github.com/martinpacesa/BindCraft "$R/vendor/BindCraft"; fi
if [ ! -d "$R/vendor/ColabDesign" ]; then git clone https://github.com/sokrypton/ColabDesign "$R/vendor/ColabDesign"; fi
mkdir -p "$S/runs/source_$SLURM_JOB_ID/outputs"
python - <<'PY'
import hashlib,json,os,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";out={}
for name in ["BindCraft","ColabDesign"]:
 p=R/"vendor"/name
 def cmd(args):return subprocess.check_output(args,cwd=p,text=True).strip()
 head=cmd(["git","rev-parse","HEAD"])
 subprocess.run(["git","checkout","--detach",head],cwd=p,check=True)
 files={}
 for x in sorted(p.rglob("*")):
  if x.is_file() and ".git" not in x.relative_to(p).parts:
   files[str(x.relative_to(p))]={"bytes":x.stat().st_size,"sha256":hashlib.sha256(x.read_bytes()).hexdigest()}
 out[name]={"path":str(p),"revision":head,"origin":cmd(["git","remote","get-url","origin"]),"tracked_status":cmd(["git","status","--porcelain"]),"files":files,"license":[x for x in files if "license" in x.lower()]}
(S/f"runs/source_{os.environ['SLURM_JOB_ID']}/outputs/sources.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps({k:{kk:vv for kk,vv in v.items() if kk!="files"} for k,v in out.items()},indent=2))
PY
cat "$R/vendor/ColabDesign/setup.py"
cat "$R/vendor/BindCraft/functions/__init__.py"
