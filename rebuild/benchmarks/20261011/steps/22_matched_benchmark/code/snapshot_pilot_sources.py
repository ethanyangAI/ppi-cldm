#!/usr/bin/env python3
"""Immutable pilot orchestration snapshot, no biological computation."""
import hashlib,json,os,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
DEST=R/"steps/22_matched_benchmark/settings/pilot_v1/source"
SOURCE=[R/"source/rebuild/paired_budget_benchmark.py",
 R/"steps/22_matched_benchmark/code/paired_budget_independent.py",
 R/"steps/22_matched_benchmark/code/test_paired_budget_benchmark.py",
 R/"steps/22_matched_benchmark/code/PAIRED_BUDGET_API.md"]
def receipt(p):
 b=p.read_bytes();return {"path":str(p.resolve()),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
jid=os.environ["SLURM_JOB_ID"]
scheduler=subprocess.run(["scontrol","show","job",jid,"-o"],check=True,capture_output=True,text=True).stdout
import re
tres=re.search(r"\b(?:AllocTRES|TRES)=(\S+)",scheduler)[1]
if any(int(n)>0 for n in re.findall(r"(?:^|,)gres/gpu(?::[^,=]+)?=(\d+)",tres)):
 raise RuntimeError("CPU-only snapshot allocation contains GPU")
DEST.mkdir(parents=True,exist_ok=True)
records=[]
for source in SOURCE:
 target=DEST/source.name
 payload=source.read_bytes()
 if target.exists():
  if target.read_bytes()!=payload:raise FileExistsError("Snapshot path already has different bytes: "+str(target))
 else:
  with target.open("xb") as f:f.write(payload);f.flush();os.fsync(f.fileno())
 target.chmod(0o444)
 records.append({"original":receipt(source),"snapshot":receipt(target)})
manifest={"status":"IMMUTABLE_PILOT_ORCHESTRATION_SNAPSHOT","schema":"paired-budget-source-snapshot-v1",
 "slurm_job_id":jid,"scheduler_alloc_tres":tres,"scheduler":scheduler,
 "files":records,"contract_tests":receipt(R/"steps/22_matched_benchmark/code/tests_13006/receipt.json"),
 "scope":"Software source snapshot only; engineering pilot, no scientific outputs"}
out=DEST/"snapshot_manifest.json"
if out.exists():raise FileExistsError(out)
with out.open("x") as f:json.dump(manifest,f,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
out.chmod(0o444)
print(json.dumps({"status":manifest["status"],"manifest":receipt(out),"files":records},indent=2))

