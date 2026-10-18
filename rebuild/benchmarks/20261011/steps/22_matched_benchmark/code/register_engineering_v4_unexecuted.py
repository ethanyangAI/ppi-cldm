import hashlib,json,os,re,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");C=R/"steps/22_matched_benchmark/code";j=os.environ["SLURM_JOB_ID"]
raw=subprocess.check_output(["scontrol","show","job",j,"-o"],text=True)
assert "JobState=RUNNING"in raw
tres=re.search(r"(?:AllocTRES|TRES)=(\S+)",raw)[1];assert not re.search(r"gres/gpu[^=]*=[1-9]",tres)
def rec(p):
 p=Path(p).resolve();return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
plan=R/"steps/22_matched_benchmark/engineering_pilot/plan_v4/frozen_plan.json"
accepted=C/"engineering_plan_v4_audit_13141/acceptance.json"
assert rec(accepted)["sha256"]=="3ffd973d7ed6a41e829f1f5d046a8566312ee37b3e421e100d2482459896dd49"
runs=R/"steps/22_matched_benchmark/engineering_pilot/runs_v4"
assert not runs.exists()or not any(runs.iterdir())
compile((C/"audit_engineering_actual_array.py").read_text(),str(C/"audit_engineering_actual_array.py"),"exec")
status=dict(status="AUDITED_UNEXECUTED_ENGINEERING_HISTORY",plan=rec(plan),independent_preflight=rec(accepted),
 science_or_gpu_results=False,gpu_launches=0,execution_state_evidence="Root controller explicitly stated no GPU launch; independent filesystem has no runs_v4 allocation artifacts.",
 superseded_reason="Observation-only full native confidence archive requires next v8 runtime/new plan; original v4 and preflight hashes retained.",
 cpu_job=j,cpu_scheduler=raw,actual_alloc_tres=tres,posthoc_wrapper_syntax=rec(C/"audit_engineering_actual_array.py"))
out=C/"engineering_plan_v4_audit_13141/EXECUTION_STATUS.json";out.write_text(json.dumps(status,indent=2)+"\n")
for p in (out,accepted,C/"audit_engineering_plan_v4_v2.py"):p.chmod(0o444)
out.parent.chmod(0o555)
print(json.dumps(rec(out)));print(json.dumps(status,indent=2))
