import sys,subprocess
from pathlib import Path
from ppiblocker.common import read_json,require,verify_file
root=Path("/lustre/users/u21111210118/projects/test9")
matched=[(p,read_json(p)) for p in (root/"steps/60_af2_control_inputs/runs").glob("*/manifest.json") if read_json(p)["status"]=="MSA_INPUTS_VALIDATED"]
require(len(matched)==1,"CALIBRATION_INPUT_MANIFEST_NOT_UNIQUE",str(len(matched)))
p,m=matched[0]
subprocess.run([sys.executable,root/"source/benchmarks/development_20260922/run_af2_calibration.py",root,verify_file(m["outputs"]["plan"]),f"batch_{int(sys.argv[1])}",p],check=True)
