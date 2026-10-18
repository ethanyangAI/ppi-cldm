import json,shutil
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,atomic_json,require
root=Path("/lustre/users/u21111210118/projects/test9")
p=root/"source/benchmarks/development_20260922/calibration_protocol.json";run=Run(root,"46_calibration_preflight",[record_file(p)])
d=read_json(p);controls=read_json(d["inputs"][0])
require(len(controls)==60 and len({x["binder_id"] for x in controls})==60,"CONTROLS","60 unique expected")
for x in controls:
 require(all(k in x for k in ["binder_id","target_id","binder","A_seq","B_seq","archive_matches"]),"SCHEMA",x["binder_id"])
 require(x["target_id"] in d["split"] and x["binder"] in ["True","False"],"LABEL_SCHEMA",x["binder_id"])
 require(x["status"]=="AUTHOR_INPUT_SEQUENCE_MATCH","IDENTITY",x["binder_id"])
import py_compile
for p in (root/"source/benchmarks/development_20260922").glob("*.py"):py_compile.compile(str(p),doraise=True)
atomic_json(run.path/"outputs/preflight.json",dict(controls=60,family_groups=2,passed=True,calibrated_gate_promotion="NO_GO_PENDING_THIRD_QUALIFIED_FAMILY_AND_ASSAY_ADJUDICATION"))
run.output("preflight",run.path/"outputs/preflight.json")
print(run.finish("CALIBRATION_INPUT_CONTRACT_VALIDATED","engineering_not_calibration"),flush=True)
