#!/usr/bin/env python3
import hashlib,json,os,shutil
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";V=R/"steps/22_matched_benchmark/settings/pilot_v7";dest=V/"source";dest.mkdir(parents=True,exist_ok=True)
O=S/f"runs/current_v7_freeze_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
sources={}
for src in [R/"steps/22_matched_benchmark/settings/pilot_v6/source/benchmark_runtime.py",R/"steps/22_matched_benchmark/settings/pilot_v6/source/rfd_env.sh",R/"steps/22_matched_benchmark/settings/pilot_v6/source/bindcraft_env.sh",S/"code/current_bc_readiness.py",S/"code/current_rfd_readiness.py"]:
 out=dest/src.name;assert not out.exists(),out;shutil.copyfile(src,out);assert out.read_bytes()==src.read_bytes();out.chmod(0o444);sources[out.name]=rec(out)
assert sources["benchmark_runtime.py"]["sha256"]=="1325556ccac5936bbae456344f040257b5041815190af5b48425cf016bc38e17"
(O/"acceptance.json").write_text(json.dumps({"status":"CURRENT_V7_SOURCE_IMMUTABLE_COPY_READBACK_PASS","sources":sources,"science_source_exact_equal_v6":True,"legacy_dev_readiness_12980_not_used":True},indent=2)+"\n")
print(json.dumps(sources,indent=2))

