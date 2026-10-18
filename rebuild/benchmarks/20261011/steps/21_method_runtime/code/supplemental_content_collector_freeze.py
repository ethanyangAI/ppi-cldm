import os,shutil,hashlib,json,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";job=os.environ["SLURM_JOB_ID"]
frozen=S/"frozen"/("supplemental_content_collector_"+job);frozen.mkdir()
for name in ["audit_supplemental_bindcraft_v1.py","test_audit_supplemental_bindcraft_v1.py"]:shutil.copyfile(S/"code"/name,frozen/name)
source=frozen/"audit_supplemental_bindcraft_v1.py";os.environ["COLLECTOR_SOURCE"]=str(source)
subprocess.run(["python","-m","py_compile",str(source)],check=True)
subprocess.run(["python",str(frozen/"test_audit_supplemental_bindcraft_v1.py")],check=True)
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
out=S/"runs"/("supplemental_content_collector_"+job)/"outputs";out.mkdir(parents=True)
doc={"status":"SUPPLEMENTAL_NATIVE_CONTENT_COLLECTOR_CPU_CONTRACTS_PASS_GPU_DATA_PENDING","collector":rec(source),"test_source":rec(frozen/"test_audit_supplemental_bindcraft_v1.py"),"contracts":9,"scope":"Engineering mixed coverage gate preserves independent cost/early native reject; no model inference"}
(out/"acceptance.json").write_text(json.dumps(doc,indent=2)+"\n")
for p in frozen.iterdir():
 if p.is_file():p.chmod(0o444)
frozen.chmod(0o555)
print(json.dumps(doc,indent=2))
