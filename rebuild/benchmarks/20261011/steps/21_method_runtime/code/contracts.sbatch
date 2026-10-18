#!/usr/bin/env bash
#SBATCH --job-name=t9-runtime-contracts
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --partition=organ
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime
#SBATCH --output=/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/logs/contracts_%j.out
set -euo pipefail
R=/lustre/users/u21111210118/projects/test9;S="$R/steps/21_method_runtime";O="$S/runs/contracts_$SLURM_JOB_ID/outputs"
mkdir -p "$O"
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=1 TMPDIR="$S/work" XDG_CACHE_HOME="$R/env/cache"
unset PYTHONPATH
source /opt/app/conda/etc/profile.d/conda.sh
conda activate "$R/env/core"
python -m py_compile "$R/source/rebuild/benchmark_runtime.py" "$S/code/test_runtime_contracts.py"
python "$S/code/test_runtime_contracts.py" > "$O/tests.txt" 2>&1
source "$S/code/rfd_env.sh"
python "$R/source/rebuild/benchmark_runtime.py" probe --label rfd --output "$O/rfd_activation_corrected.json"
python - <<'PY' > "$O/contig.txt"
from rfdiffusion.contigs import ContigMap
c=ContigMap({"pdb_idx":[("A",i) for i in range(1,86)]},contigs=["A1-85/0 65-65"])
assert c.hal[:65]==[("A",i) for i in range(1,66)],c.hal[:65]
assert {p[0] for p in c.hal[65:]}=={"B"},c.hal[65:]
assert c.ref[:65]==[("_","_")]*65,c.ref[:65]
assert c.ref[65:]==[("A",i) for i in range(1,86)],c.ref[65:]
print("ACTUAL_CONTIGMAP_CONFIRMED_INPUT_TARGET_A_OUTPUT_BINDER_A_OUTPUT_TARGET_B")
print("FIRST_BINDER",c.hal[:3],"FIRST_TARGET",c.hal[65:68])
PY
conda activate "$R/env/core"
python - <<'PY'
import hashlib,json,os
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");O=R/f"steps/21_method_runtime/runs/contracts_{os.environ['SLURM_JOB_ID']}/outputs"
probe=json.loads((O/"rfd_activation_corrected.json").read_text())
assert all(x["import"]=="PASS" for x in probe["modules"].values()),probe
assert probe["pip_check"]["returncode"]==0,probe
ps=[R/"source/rebuild/benchmark_runtime.py",R/"steps/21_method_runtime/code/test_runtime_contracts.py",O/"tests.txt",O/"contig.txt",O/"rfd_activation_corrected.json"]
records=[{"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in ps]
v={"status":"RUNTIME_ADAPTER_CPU_CONTRACTS_AND_RFD_MAPPING_VERIFIED","job_id":os.environ["SLURM_JOB_ID"],"unit_tests":14,"gpu_requested":False,"records":records}
(O/"acceptance.json").write_text(json.dumps(v,indent=2)+"\n");print(v["status"])
PY

