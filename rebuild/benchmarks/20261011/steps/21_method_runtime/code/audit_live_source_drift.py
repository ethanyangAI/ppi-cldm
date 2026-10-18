#!/usr/bin/env python3
import difflib,hashlib,json,os,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";O=S/f"runs/live_source_drift_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
def rec(p):
 stat=p.stat();return {"path":str(p),"bytes":stat.st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"mtime_ns":stat.st_mtime_ns,"ctime_ns":stat.st_ctime_ns,"mode":oct(stat.st_mode),"uid":stat.st_uid,"gid":stat.st_gid}
live=R/"source/rebuild/benchmark_runtime.py";frozen=R/"steps/22_matched_benchmark/settings/pilot_v6/source/benchmark_runtime.py";diff=list(difflib.unified_diff(frozen.read_text().splitlines(),live.read_text().splitlines(),fromfile="immutable_v6",tofile="current_live",lineterm=""))
out={"status":"IDENTICAL" if live.read_bytes()==frozen.read_bytes() else "DRIFT_FOUND","live":rec(live),"frozen":rec(frozen),"diff":diff,"source_modified_by_diagnostic":False,"collector":rec(S/"code/audit_actual_rf_native.py"),"cpu_only":True}
(O/"diagnosis.json").write_text(json.dumps(out,indent=2)+"\n")
(O/"source.diff").write_text("\n".join(diff)+"\n")
import py_compile
py_compile.compile(str(S/"code/audit_actual_rf_native.py"),doraise=True)
print(json.dumps(out,indent=2))

