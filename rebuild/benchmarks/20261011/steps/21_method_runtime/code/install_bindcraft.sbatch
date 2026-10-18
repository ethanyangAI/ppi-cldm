#!/usr/bin/env bash
#SBATCH --job-name=t9-bindcraft-install
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=interactive
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=04:00:00
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/install_%j.out
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9
S="$R/steps/21_method_runtime"
O="$S/runs/install_$SLURM_JOB_ID/outputs"
mkdir -p "$O"
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=1
unset PYTHONPATH
export CONDA_PKGS_DIRS="$R/env/pkgs" PIP_CACHE_DIR="$R/env/cache/pip" TMPDIR="$S/work" XDG_CACHE_HOME="$R/env/cache"
source /opt/app/conda/etc/profile.d/conda.sh
conda activate "$R/env/core"
python - <<'PY'
import hashlib,json,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");src=json.loads((R/"steps/21_method_runtime/runs/source_12947/outputs/sources.json").read_text())
for name,v in src.items():
 p=Path(v["path"])
 assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=p,text=True).strip()==v["revision"]
 for rel,rec in v["files"].items():
  x=p/rel
  assert x.stat().st_size==rec["bytes"] and hashlib.sha256(x.read_bytes()).hexdigest()==rec["sha256"]
pr=R/"assets/pyrosetta/receipt.json";v=json.loads(pr.read_text());x=Path(v["path"])
assert x.stat().st_size==v["bytes"] and hashlib.sha256(x.read_bytes()).hexdigest()==v["sha256"]
print("PINNED_SOURCES_AND_EXISTING_PYROSETTA_WHEEL_VERIFIED")
PY
if [ -e "$R/env/bindcraft" ]; then
 echo "BindCraft environment already exists: refusing unattended replacement"
 exit 2
fi
conda create -y --clone "$R/env/colabfold" -p "$R/env/bindcraft"
conda activate "$R/env/bindcraft"
conda install -y --freeze-installed --override-channels -c conda-forge openmm=8.1.1 pdbfixer=1.9 ffmpeg=6.1.1 libgfortran5
python -m pip install --no-deps "$R/vendor/ColabDesign"
python -m pip install --no-deps "$R/assets/pyrosetta/pyrosetta-2026.29+releasequarterly.80a0635615-cp310-cp310-linux_x86_64.whl"
python -m pip install 'seaborn==0.13.2' 'py3Dmol==2.5.3' 'fsspec==2026.9.0'
chmod u+x "$R/vendor/BindCraft/functions/dssp" "$R/vendor/BindCraft/functions/DAlphaBall.gcc"
python -m pip check
python "$R/source/rebuild/benchmark_runtime.py" probe --label bindcraft --output "$O/bindcraft.json"
python -m pip freeze > "$O/bindcraft-freeze.txt"
conda list --explicit > "$O/bindcraft-explicit.txt"
python - <<'PY'
import json,os,subprocess,hashlib
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");O=R/f"steps/21_method_runtime/runs/install_{os.environ['SLURM_JOB_ID']}/outputs"
v=json.loads((O/"bindcraft.json").read_text())
assert all(x["import"]=="PASS" for x in v["modules"].values()),v
assert v["bindcraft_functions_import"]["status"]=="PASS",v
assert v["pip_check"]["returncode"]==0,v
records=[]
for p in [O/"bindcraft.json",O/"bindcraft-freeze.txt",O/"bindcraft-explicit.txt"]:
 records.append({"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size})
out={"status":"BINDCRAFT_PRIVATE_CPU_RUNTIME_VERIFIED_GPU_SMOKE_PENDING","job_id":os.environ["SLURM_JOB_ID"],"environment":str(R/"env/bindcraft"),"source_freeze":str(R/"steps/21_method_runtime/runs/source_12947/outputs/sources.json"),"records":records,"uses_existing_weights":str(R/"assets/colabfold/params"),"license_scope":"Official BindCraft MIT and ColabDesign dependencies; existing academic PyRosetta asset retained. No claim of commercial license.","gpu_smoke_submitted":False}
(O/"acceptance.json").write_text(json.dumps(out,indent=2)+"\n")
print(out["status"])
PY
