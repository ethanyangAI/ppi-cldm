import hashlib,json,os,re,subprocess,sys
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");C=R/"steps/22_matched_benchmark/code";j=os.environ["SLURM_JOB_ID"]
raw=subprocess.check_output(["scontrol","show","job",j,"-o"],text=True)
assert "JobState=RUNNING"in raw
tres=re.search(r"(?:AllocTRES|TRES)=(\S+)",raw)[1];assert not re.search(r"gres/gpu[^=]*=[1-9]",tres)
result=subprocess.run([sys.executable,str(C/"test_formal_benchmark_contract.py")],capture_output=True,text=True)
print(result.stdout);print(result.stderr)
def rec(p):
 p=Path(p);return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
out=C/("formal_contracts_"+j);out.mkdir()
report=dict(status="INDEPENDENT_FORMAL_CONTRACT_TESTS_PASS"if result.returncode==0 else"CONTRACT_TESTS_FAILED",cpu_job_id=j,cpu_scheduler_record=raw,actual_allocated_tres=tres,
 n_tests=int(re.search(r"Ran (\d+) tests",result.stderr)[1])if re.search(r"Ran (\d+) tests",result.stderr)else None,
 source=rec(C/"formal_benchmark_contract.py"),tests=rec(C/"test_formal_benchmark_contract.py"),
 reviewed_root_formal_helper=rec(C/"freeze_formal_benchmark.py"),reviewed_target_statistics=rec(R/"steps/24_benchmark_delivery/code/target_statistics.py"),no_formal_freeze_or_gpu_submission=True)
p=out/"receipt.json";p.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(rec(p)));sys.exit(result.returncode)
