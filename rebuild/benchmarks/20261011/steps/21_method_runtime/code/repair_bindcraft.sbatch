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
python - <<'PY'
import sys,numpy,jax,jaxlib
assert sys.prefix=="/lustre/users/u21111210118/projects/test9/env/bindcraft"
assert numpy.__version__=="1.24.3"
assert jax.__version__=="0.4.23"
assert jaxlib.__version__=="0.4.23"
print("FAILED_CONDA_CLONE_RETAINED_AND_CORE_PINS_INTACT")
PY
if [ ! -e "$S/sources/PDBFixer" ]; then
 git clone --branch 1.9 --depth 1 https://github.com/openmm/pdbfixer.git "$S/sources/PDBFixer"
fi
git -C "$S/sources/PDBFixer" checkout --detach 1.9
python -m pip download --only-binary=:all: --no-deps -d "$S/wheels" 'OpenMM==8.1.1' 'seaborn==0.13.2' 'py3Dmol==2.5.3' 'fsspec==2026.9.0' 'imageio-ffmpeg==0.6.0' 'joblib==1.4.2'
python -m pip install --no-deps --no-index --find-links "$S/wheels" 'OpenMM==8.1.1' 'seaborn==0.13.2' 'py3Dmol==2.5.3' 'fsspec==2026.9.0' 'imageio-ffmpeg==0.6.0'
python -m pip install --no-deps --no-build-isolation "$S/sources/PDBFixer" "$R/vendor/ColabDesign"
python -m pip install --no-deps "$R/assets/pyrosetta/pyrosetta-2026.29+releasequarterly.80a0635615-cp310-cp310-linux_x86_64.whl"
python - <<'PY'
import hashlib,json,os,subprocess
from pathlib import Path
import imageio_ffmpeg,numpy,jax,jaxlib
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";O=S/f"runs/repair_{os.environ['SLURM_JOB_ID']}/outputs"
assert numpy.__version__=="1.24.3" and jax.__version__=="0.4.23" and jaxlib.__version__=="0.4.23"
exe=Path(imageio_ffmpeg.get_ffmpeg_exe());link=R/"env/bindcraft/bin/ffmpeg"
if link.exists():assert link.resolve()==exe.resolve()
else:link.symlink_to(exe)
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
vendor=S/"sources/PDBFixer"
v={"status":"PRIVATE_FIXED_WHEELS_INSTALLED","recovery_from_jobs":["12948","12974"],"job_id":os.environ["SLURM_JOB_ID"],"wheels":[rec(p) for p in sorted((S/"wheels").glob("*.whl"))],"pdbfixer":{"repository":"https://github.com/openmm/pdbfixer.git","tag":"1.9","revision":subprocess.check_output(["git","rev-parse","HEAD"],cwd=vendor,text=True).strip(),"tracked_files":{str(p.relative_to(vendor)):rec(p) for p in vendor.rglob("*") if p.is_file() and ".git" not in p.parts}},"ffmpeg":rec(exe)}
(O/"dependency_receipts.json").write_text(json.dumps(v,indent=2)+"\n")
print(v["status"])
PY
chmod u+x "$R/vendor/BindCraft/functions/dssp" "$R/vendor/BindCraft/functions/DAlphaBall.gcc"
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

