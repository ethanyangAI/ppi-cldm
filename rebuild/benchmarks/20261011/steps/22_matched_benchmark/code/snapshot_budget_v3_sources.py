#!/usr/bin/env python3
"""Immutable array-accounting-v3 source snapshot; CPU only."""
import hashlib,json,os,re,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");CODE=R/"steps/22_matched_benchmark/code"
DEST=R/"steps/22_matched_benchmark/settings/pilot_budget_v3/source"
SOURCE=[R/"source/rebuild/paired_budget_benchmark.py",CODE/"paired_budget_independent.py",
 CODE/"test_paired_budget_benchmark.py",CODE/"PAIRED_BUDGET_API.md"]
def rec(p):
 p=Path(p);b=p.read_bytes();return {"path":str(p.resolve()),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def eq(a,b,label):
 if a!=b:raise RuntimeError("Identity mismatch "+label)
def write(p,b):
 with p.open("xb") as f:f.write(b);f.flush();os.fsync(f.fileno())
jid=os.environ["SLURM_JOB_ID"]
scheduler=subprocess.run(["scontrol","show","job",jid,"-o"],check=True,capture_output=True,text=True).stdout
eq(re.search(r"\bJobId=(\S+)",scheduler)[1],jid,"CPU job")
eq(re.search(r"\bJobState=(\S+)",scheduler)[1],"RUNNING","CPU state")
tres=re.search(r"\b(?:AllocTRES|TRES)=(\S+)",scheduler)[1]
if any(int(n)>0 for n in re.findall(r"(?:^|,)gres/gpu(?::[^,=]+)?=(\d+)",tres)):raise RuntimeError("CPU job has GPU")
testpath=CODE/"tests_13079/receipt.json";test=json.loads(testpath.read_text())
eq(test["status"],"PAIRED_BUDGET_CPU_CONTRACT_TESTS_PASS","tests status")
eq(test["n_tests"],70,"70 tests");eq(test["n_failures"],0,"failures");eq(test["n_errors"],0,"errors")
eq(test["source_unchanged_during_tests"],True,"source unchanged")
for key,source in zip(["source","independent_verifier","tests"],SOURCE[:3]):eq(rec(source),test[key],"tested "+key)
preserved=[]
for name,sha in [("pilot_v1","62a985429fe4c67ec1660d12ac97ba415864cfd52452e42ab2ea8d6c01ed922d"),
                 ("pilot_budget_v2","429a4232dd1f52b438e36985f404d75f208a6031c2c54fd1d54dfd913923a22c")]:
 manifestpath=R/"steps/22_matched_benchmark/settings"/name/"source/snapshot_manifest.json"
 eq(rec(manifestpath)["sha256"],sha,"prior "+name)
 manifest=json.loads(manifestpath.read_text());records=[rec(manifestpath)]
 for entry in manifest["files"]:
  record=entry["snapshot"];eq(rec(record["path"]),record,name+" snapshot");records.append(record)
 eq(rec(manifest["contract_tests"]["path"]),manifest["contract_tests"],name+" prior tests")
 records.append(manifest["contract_tests"]);preserved.append({"snapshot":name,"all_original_bytes_unchanged":True,"receipts":records})
if DEST.exists():raise FileExistsError(DEST)
DEST.mkdir(parents=True);files=[]
for original in SOURCE:
 p=DEST/original.name;write(p,original.read_bytes());p.chmod(0o444)
 a,b=rec(original),rec(p);eq((a["bytes"],a["sha256"]),(b["bytes"],b["sha256"]),"copy "+p.name)
 files.append({"original":a,"snapshot":b})
manifest={"schema":"paired-budget-source-snapshot-v3","status":"IMMUTABLE_ARRAY_ACCOUNTING_PILOT_BUDGET_SNAPSHOT",
 "slurm_job_id":jid,"scheduler":scheduler,"scheduler_alloc_tres":tres,"files":files,
 "contract_tests":rec(testpath),"n_tests":70,"previous_snapshots_preserved":preserved,
 "fix":"Original scontrol numeric physical allocation ID and array alias; unique GPU accounting; 8/9-field sacct",
 "scope":"CPU software snapshot only; no GPU/model inference or scientific results","snapshot_utility":rec(Path(__file__))}
p=DEST/"snapshot_manifest.json";write(p,(json.dumps(manifest,indent=2)+"\n").encode());p.chmod(0o444);DEST.chmod(0o555)
summary={"status":manifest["status"],"manifest":rec(p),"files":files,"contract_tests":rec(testpath),
 "prior_v1_v2_bytes_unchanged":True,"actual_cpu_alloc_tres":tres,"snapshot_directory_mode":oct(DEST.stat().st_mode & 0o777)}
write(CODE/("snapshot_budget_v3_"+jid+".json"),(json.dumps(summary,indent=2)+"\n").encode())
print(json.dumps(summary,indent=2))

