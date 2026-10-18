#!/usr/bin/env python3
"""Immutable v2 ownership-hardened snapshot; CPU allocation only."""
import hashlib,json,os,re,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
DEST=R/"steps/22_matched_benchmark/settings/pilot_budget_v2/source"
CODE=R/"steps/22_matched_benchmark/code"
SOURCE=[R/"source/rebuild/paired_budget_benchmark.py",CODE/"paired_budget_independent.py",
 CODE/"test_paired_budget_benchmark.py",CODE/"PAIRED_BUDGET_API.md"]
def receipt(p):
 p=Path(p);b=p.read_bytes();return {"path":str(p.resolve()),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def require_equal(found,expected,label):
 if found!=expected:raise RuntimeError("Identity mismatch: "+label)
def write_exclusive(path,payload):
 with path.open("xb") as f:f.write(payload);f.flush();os.fsync(f.fileno())
jid=os.environ["SLURM_JOB_ID"]
scheduler=subprocess.run(["scontrol","show","job",jid,"-o"],check=True,capture_output=True,text=True).stdout
require_equal(re.search(r"\bJobId=(\S+)",scheduler)[1],jid,"Slurm JobId")
require_equal(re.search(r"\bJobState=(\S+)",scheduler)[1],"RUNNING","CPU snapshot state")
match=re.search(r"\b(?:AllocTRES|TRES)=(\S+)",scheduler)
if not match:raise RuntimeError("Actual allocation TRES unavailable")
tres=match[1]
if any(int(n)>0 for n in re.findall(r"(?:^|,)gres/gpu(?::[^,=]+)?=(\d+)",tres)):
 raise RuntimeError("CPU-only snapshot allocation contains GPU")
test_path=CODE/"tests_13056/receipt.json";tests=json.loads(test_path.read_text())
require_equal(tests["status"],"PAIRED_BUDGET_CPU_CONTRACT_TESTS_PASS","tests")
require_equal(tests["n_tests"],64,"test count")
require_equal(tests["n_errors"],0,"test errors")
require_equal(tests["n_failures"],0,"test failures")
require_equal(tests["source_unchanged_during_tests"],True,"source unchanged")
for key,source in zip(["source","independent_verifier","tests"],SOURCE[:3]):
 require_equal(receipt(source),tests[key],"tested "+key)
old=R/"steps/22_matched_benchmark/settings/pilot_v1/source"
old_manifest=old/"snapshot_manifest.json"
require_equal(receipt(old_manifest)["sha256"],"62a985429fe4c67ec1660d12ac97ba415864cfd52452e42ab2ea8d6c01ed922d","original v1 manifest")
old_doc=json.loads(old_manifest.read_text())
old_preserved=[receipt(old_manifest)]
for entry in old_doc["files"]:
 p=Path(entry["snapshot"]["path"])
 require_equal(receipt(p),entry["snapshot"],"old snapshot "+p.name)
 old_preserved.append(receipt(p))
old_test_path=CODE/"tests_13006/receipt.json"
require_equal(receipt(old_test_path),old_doc["contract_tests"],"old tests receipt")
old_test=json.loads(old_test_path.read_text())
require_equal(old_test["n_tests"],57,"old 57-test receipt")
require_equal(old_test["source"]["sha256"],"858aa2c994dbe168caecd55e589ef901e987406eeefca20051197b150788d7e2","old source")
old_preserved.append(receipt(old_test_path))
hardware=R/"steps/23_common_review/inputs/proc_gpu_inventory_13044.json"
require_equal(receipt(hardware)["sha256"],"eb4a7eb9d026b85d228a2983e85c60a883a117c6438babadecbcbe106e1a29e7","CPU-only physical inventory")
if DEST.exists():raise FileExistsError("New immutable snapshot destination already exists")
DEST.mkdir(parents=True)
records=[]
for source in SOURCE:
 target=DEST/source.name;write_exclusive(target,source.read_bytes());target.chmod(0o444)
 a,b=receipt(source),receipt(target)
 require_equal((a["bytes"],a["sha256"]),(b["bytes"],b["sha256"]),"snapshot readback "+source.name)
 records.append({"original":a,"snapshot":b})
manifest={"status":"IMMUTABLE_OWNERSHIP_HARDENED_PILOT_BUDGET_SNAPSHOT",
 "schema":"paired-budget-source-snapshot-v2","slurm_job_id":jid,
 "scheduler_alloc_tres":tres,"scheduler":scheduler,"files":records,
 "contract_tests":receipt(test_path),"n_tests":64,
 "previous_pilot_v1_preserved":old_preserved,"physical_inventory_reference":receipt(hardware),
 "ownership_guard":{"requires":"RUNNING actual allocated GPU + Slurm STEP/JOB global ownership",
 "numeric_resolution":"proc Device Minor -> physical GPU UUID -> NVML UUID",
 "child_mask":"owned full GPU UUID before method-session launch",
 "independent_raw_receipt_verification":True},
 "scope":"CPU software snapshot only; no GPU/model inference, generation or scientific outcomes",
 "snapshot_utility":receipt(Path(__file__))}
out=DEST/"snapshot_manifest.json"
write_exclusive(out,(json.dumps(manifest,indent=2)+"\n").encode());out.chmod(0o444)
DEST.chmod(0o555)
summary={"status":manifest["status"],"manifest":receipt(out),"files":records,
 "contract_tests":receipt(test_path),"previous_pilot_v1_all_bytes_unchanged":True,
 "snapshot_directory_mode":oct(DEST.stat().st_mode & 0o777),"actual_cpu_alloc_tres":tres}
write_exclusive(CODE/("snapshot_budget_v2_"+jid+".json"),(json.dumps(summary,indent=2)+"\n").encode())
print(json.dumps(summary,indent=2))

