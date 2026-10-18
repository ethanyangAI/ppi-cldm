import os,json,hashlib,shutil,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";job=os.environ["SLURM_JOB_ID"]
out=S/"runs"/("supplemental_stage_prepare_"+job);out.mkdir(parents=True,exist_ok=True)
frozen=S/"frozen"/("supplemental_bindcraft_"+job);frozen.mkdir(parents=True)
for name in ["bindcraft_supplemental_stage_coverage.py","test_bindcraft_supplemental_stage_coverage.py"]:
 shutil.copyfile(S/"code"/name,frozen/name)
os.environ["SUPPLEMENTAL_SOURCE"]=str(frozen/"bindcraft_supplemental_stage_coverage.py")
subprocess.run(["python","-m","py_compile",os.environ["SUPPLEMENTAL_SOURCE"]],check=True)
subprocess.run(["python",str(frozen/"test_bindcraft_supplemental_stage_coverage.py")],check=True)
subprocess.run(["python",os.environ["SUPPLEMENTAL_SOURCE"],"prepare","--output-dir",str(out/"outputs")],check=True)
for p in frozen.iterdir():
 if p.is_file():p.chmod(0o444)
for p in (out/"outputs").glob("*.json"):p.chmod(0o444)
frozen.chmod(0o555)
print("SOURCE",os.environ["SUPPLEMENTAL_SOURCE"])
print("CONFIG",out/"outputs/config.json")
print("CONFIG_SHA256",hashlib.sha256((out/"outputs/config.json").read_bytes()).hexdigest())
