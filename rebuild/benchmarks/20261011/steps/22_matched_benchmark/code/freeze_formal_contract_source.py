import hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");C=R/"steps/22_matched_benchmark/code";jid=os.environ["SLURM_JOB_ID"]
def rec(p):
 p=Path(p).resolve();h=hashlib.sha256()
 with p.open("rb")as stream:
  for block in iter(lambda:stream.read(8*1024*1024),b""):h.update(block)
 return dict(path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest())
sched=subprocess.check_output(["scontrol","show","job",jid,"-o"],text=True)
assert "JobState=RUNNING"in sched
tres=re.search(r"(?:AllocTRES|TRES)=(\S+)",sched)[1];assert not re.search(r"gres/gpu[^=]*=[1-9]",tres)
result=subprocess.run([sys.executable,str(C/"test_formal_benchmark_contract.py")],capture_output=True,text=True)
print(result.stdout);print(result.stderr)
assert result.returncode==0
dest=C/"formal_contract_v1";dest.mkdir();source=dest/"source";source.mkdir()
records=[]
for name in ["formal_benchmark_contract.py","test_formal_benchmark_contract.py","FORMAL_FAIRNESS_ACCEPTANCE.md"]:
 before=rec(C/name);target=source/name;shutil.copyfile(C/name,target);after=rec(target)
 assert before["bytes"]==after["bytes"]and before["sha256"]==after["sha256"]
 target.chmod(0o444);records.append(dict(original=before,snapshot=after))
n=int(re.search(r"Ran (\d+) tests",result.stderr)[1])
report=dict(status="INDEPENDENT_FORMAL_CONTRACT_READONLY_SOURCE_SNAPSHOT_PASS",cpu_job_id=jid,cpu_scheduler_record=sched,actual_alloc_tres=tres,n_tests=n,
 reviewed_formal_v2_helper=rec(C/"freeze_formal_benchmark_v2.py"),
 reviewed_current_target_statistics=rec(R/"steps/24_benchmark_delivery/code/target_statistics.py"),
 existing_budget_v4_source=rec(R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py"),
 existing_budget_v4_independent=rec(R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_independent.py"),
 records=records,no_formal_freeze=True,no_gpu_submission=True,no_accepted_v4_mutation=True)
manifest=dest/"manifest.json";manifest.write_text(json.dumps(report,indent=2)+"\n");manifest.chmod(0o444);source.chmod(0o555);dest.chmod(0o555)
print(json.dumps(dict(status=report["status"],manifest=rec(manifest),n_tests=n,source_records=records),indent=2))
