#!/usr/bin/env bash
#SBATCH --job-name=t9-bindcraft-repair
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=01:30:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/repair_%j.out
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9;S="$R/steps/21_method_runtime";O="$S/runs/repair_$SLURM_JOB_ID/outputs"
mkdir -p "$O" "$S/wheels" "$S/sources"
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=1 CONDA_PKGS_DIRS="$R/env/pkgs" PIP_CACHE_DIR="$R/env/cache/pip" TMPDIR="$S/work" XDG_CACHE_HOME="$R/env/cache" JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=""
unset PYTHONPATH
source /opt/app/conda/etc/profile.d/conda.sh
conda activate "$R/env/bindcraft"
python -m pip install --no-deps --no-index --find-links "$S/wheels" 'joblib==1.4.2'
python - <<'PY' > "$O/openmm_platforms.json"
import json,openmm,numpy,jax,os,sys
assert numpy.__version__=="1.24.3" and jax.__version__=="0.4.23"
v={"job_id":os.environ["SLURM_JOB_ID"],"openmm_version":openmm.__version__,"platforms":[openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())],"python":sys.executable}
assert "CPU" in v["platforms"] and "Reference" in v["platforms"]
print(json.dumps(v,indent=2))
PY
cp "$S/runs/repair_12982/outputs/dependency_receipts.json" "$O/dependency_receipts.json"
source "$S/code/bindcraft_env.sh"
export JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES=""
python -m pip check
python "$R/source/rebuild/benchmark_runtime.py" probe --label bindcraft --output "$O/bindcraft.json"
python -m pip freeze > "$O/bindcraft-freeze.txt"
conda list --explicit > "$O/bindcraft-explicit.txt"
python - <<'PY'
import json,os,hashlib
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");O=R/f"steps/21_method_runtime/runs/repair_{os.environ['SLURM_JOB_ID']}/outputs"
v=json.loads((O/"bindcraft.json").read_text())
assert all(x["import"]=="PASS" for x in v["modules"].values()),v
assert v["bindcraft_functions_import"]["status"]=="PASS",v
assert v["pip_check"]["returncode"]==0,v
ps=[O/"bindcraft.json",O/"bindcraft-freeze.txt",O/"bindcraft-explicit.txt",O/"dependency_receipts.json"]
out={"status":"BINDCRAFT_PRIVATE_CPU_RUNTIME_VERIFIED_GPU_SMOKE_PENDING","job_id":os.environ["SLURM_JOB_ID"],"environment":str(R/"env/bindcraft"),"source_freeze":str(R/"steps/21_method_runtime/runs/source_12947/outputs/sources.json"),"records":[{"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in ps],"gpu_smoke_submitted":False}
(O/"acceptance.json").write_text(json.dumps(out,indent=2)+"\n");print(out["status"])
PY

