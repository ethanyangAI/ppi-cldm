#!/usr/bin/env python3
import hashlib,json,os,shutil
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";V=R/"steps/22_matched_benchmark/settings/pilot_v6";snapshot=V/"source";snapshot.mkdir(parents=True,exist_ok=True)
O=S/f"runs/pilot_v6_features_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
runtime=R/"source/rebuild/benchmark_runtime.py";assert rec(runtime)["sha256"]=="1325556ccac5936bbae456344f040257b5041815190af5b48425cf016bc38e17"
sources={}
for src in [runtime,S/"code/rfd_env.sh",S/"code/bindcraft_env.sh",S/"code/pilot_v6_feature_audit.py"]:
 dest=snapshot/src.name
 if dest.exists():raise FileExistsError(dest)
 shutil.copyfile(src,dest);assert dest.read_bytes()==src.read_bytes();sources[dest.name]=rec(dest)
tests=snapshot/"test_runtime_contracts.py";assert not tests.exists()
tests.write_text((S/"code/test_runtime_contracts.py").read_text().replace('R/"source/rebuild/benchmark_runtime.py"','R/"steps/22_matched_benchmark/settings/pilot_v6/source/benchmark_runtime.py"'));sources[tests.name]=rec(tests)
receipt=O/"frozen_source_receipt.json";receipt.write_text(json.dumps({"status":"PILOT_V6_IMMUTABLE_SOURCE_COPY_READBACK_PASS","sources":sources,"prior_versions_retained":True,"cpu_only":True},indent=2)+"\n");print(json.dumps(rec(receipt)))

