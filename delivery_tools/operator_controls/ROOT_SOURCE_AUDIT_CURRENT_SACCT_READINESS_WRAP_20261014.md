# Root current SACCT readiness operation for unchanged Source audit

Text proposal, not executed. Original15201 FAILED1s atLIB.cpu78 before output/freeze/53. Originalinstantquery raw unavailable; its specific cause remainsUNPROVEN.

The new unique Root sbatch --wrap must reproduce exact jobname test9_final_source_materialized_v3, accountu21111210118/qosnormal/organ/CPU1/task1/16G/00:30:00/chdirS and original logprefix final_source_materialized_v3_%j. No GPU request or software/source/request/Plan modification. Inside owned allocation onlycurrentJob scontrol plus bounded EXACTunchanged six-columnSACCT real raw queries are saved, never proxies. CurrentSLURMenvelope plusstrict unique numericCPU1/GPU0readyrow enables exactlyone exec bash originalqualifiedlauncher audit SAMEreadonlyrequest1243; unchanged LIB.cpu independentlyqueriesagain. Waitmax60s/30attempts; failures/exhaustion retainallactualraw and abort beforeaudit. No originalcausality/Source/science acceptance. AllRootwrapliteral/claims/queryproof/logs/terminal explicit lateComposerfinaltools executioncontrol sources/evidence; no tenth role/newsoftware qualification.

The readiness JSON unchanged_launcher_executed=false describes the state at durableproof creation BEFOREexec, not post-audit result. Only actual laterSourceacceptance establishes execution/outcome. Request/SourceControl hashes are not computed by wait. Licensed COREbinary is runtimeonly, not redistributed. StrictGPU parse missing keys is currentcontrolledpureCPUallocation only, backed by actualscontrolCPU-onlyTRES and explicitGPU0request, never historicalunknown-cost inference.

Exact proposed wrap literal:

```sh
exec env -u PYTHONPATH CUDA_VISIBLE_DEVICES= JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /lustre/users/u21111210118/projects/test9/env/core/bin/python -B - <<'CURRENT_SOURCE_SACCT_READINESS'
import os, sys, json, re, stat, time, datetime, subprocess
from pathlib import Path
S = Path("/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery")
P = S / "pending/final_source_closure_v3_fixturefix1"
REQUEST = S / "submissions/final_source_materialized_context_from15195_request/request.json"
jid = os.environ.get("SLURM_JOB_ID", "")
if not re.fullmatch("[0-9]+", jid):
    raise SystemExit("Current owned Slurm job ID required")
expected_env = {"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
if any(os.environ.get(k) != v for k, v in expected_env.items()) or "PYTHONPATH" in os.environ:
    raise SystemExit("Original CPU/import/thread isolation required")
D = S / "submissions" / ("source_audit_current_sacct_readiness_" + jid)
if D.exists() or D.is_symlink():
    raise SystemExit("Exclusive absent current readiness namespace required")
D.mkdir(mode=0o755, exist_ok=False)
def persist(name, data):
    p = D / name
    with p.open("xb") as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno()); os.fchmod(stream.fileno(), 0o444)
    st = p.lstat()
    return {"path": str(p), "bytes": st.st_size, "inode": st.st_ino, "mtime_ns": st.st_mtime_ns, "mode": stat.S_IMODE(st.st_mode)}
def tres(text):
    values = {}
    for item in text.split(","):
        if item.count("=") != 1:
            raise ValueError("Malformed allocated TRES")
        key, value = item.split("=", 1)
        if not key or not value or key in values:
            raise ValueError("Empty or duplicate allocated TRES key")
        if key.startswith("gres/gpu") and key != "gres/gpu" and not re.fullmatch("gres/gpu:[A-Za-z0-9_-]+", key):
            raise ValueError("Malformed typed GPU key")
        values[key] = value
    if "cpu" not in values or not re.fullmatch("[0-9]+", values["cpu"]) or int(values["cpu"]) != 1:
        raise ValueError("Actual CPU1 required")
    gpu_values = [value for key, value in values.items() if key == "gres/gpu" or key.startswith("gres/gpu:")]
    if any(not re.fullmatch("[0-9]+", value) for value in gpu_values) or any(int(value) != 0 for value in gpu_values):
        raise ValueError("Actual current GPU0 required")
    return values
query_env = dict(os.environ, TZ="UTC", SLURM_TIME_FORMAT="standard")
commands = []
def query(argv, prefix):
    r = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=query_env)
    a = {"argv": argv, "returncode": r.returncode,
         "raw_stdout": persist(prefix + ".stdout", r.stdout),
         "raw_stderr": persist(prefix + ".stderr", r.stderr)}
    commands.append(a)
    return r, a
control_argv = ["scontrol", "show", "job", jid, "-o"]
ctl, ctl_saved = query(control_argv, "current_scontrol")
try:
    if ctl.returncode != 0 or ctl.stderr:
        raise ValueError("Actual current scontrol rc0/empty stderr required")
    fields = {}
    for token in ctl.stdout.decode("utf-8").split():
        if "=" in token:
            key, value = token.split("=", 1)
            if key in fields:
                raise ValueError("Duplicate scontrol field")
            fields[key] = value
    required = {"JobId": jid, "JobName": "test9_final_source_materialized_v3", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres = tres(fields["TRES"])
except Exception as e:
    obj = {"schema": "root-current-owned-source-audit-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_UNCHANGED_AUDIT_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "unchanged_launcher_executed": False, "original15201_specific_cause_proven": False}
    persist("readiness.json", (json.dumps(obj, indent=2) + "\n").encode()); D.chmod(0o555); raise
argv = ["sacct", "-X", "-j", jid, "--noheader", "--parsable2", "--format=JobIDRaw,State,AllocTRES,User%64,Account%64,Partition%64"]
attempts = []; selected = None; deadline = time.monotonic() + 60
for number in range(1, 31):
    r, observation = query(argv, "attempt_%03d" % number)
    try:
        if r.returncode != 0 or r.stderr:
            raise ValueError("Actual current sacct rc0/empty stderr required")
        rows = [line.split("|") for line in r.stdout.decode("utf-8").splitlines() if line.split("|", 1)[0] == jid]
        if len(rows) != 1 or len(rows[0]) != 6 or rows[0][1] != "RUNNING" or rows[0][3:] != ["u21111210118", "u21111210118", "organ"]:
            raise ValueError("Unique actual current six-column RUNNING owner/account/organ row required")
        values = tres(rows[0][2])
        observation.update({"accepted_current_readiness": True, "actual_row": rows[0], "parsed_tres": values})
        selected = number
    except Exception as e:
        observation.update({"accepted_current_readiness": False, "reason_type": type(e).__name__, "reason": str(e)})
    attempts.append(observation)
    if selected is not None or time.monotonic() >= deadline or number == 30:
        break
    time.sleep(min(2, max(0, deadline - time.monotonic())))
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_UNCHANGED_AUDIT_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_UNCHANGED_AUDIT_NOT_EXECUTED"
obj = {"schema": "root-current-owned-source-audit-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
       "current_scontrol_observation": ctl_saved, "current_scontrol_TRES": current_tres, "attempts": attempts,
       "selected_actual_attempt": selected, "maximum_attempts": 30, "maximum_wait_seconds": 60,
       "environment": {"TZ": "UTC", "SLURM_TIME_FORMAT": "standard", **expected_env},
       "requested_GPUs": 0, "current_allocation_only_no_historical_GPU_inference": True,
       "no_source_or_request_hashes_or_imports_or_tests_by_wait": True,
       "unchanged_library_cpu_guard_will_freshly_requery": True, "actual_queries_not_proxy_or_synthesized_replies": True,
       "unchanged_launcher_executed": False, "original15201_specific_cause_proven": False,
       "source_audit_stage_Git_ACTIVE_acceptance": False}
persist("readiness.json", (json.dumps(obj, indent=2) + "\n").encode()); D.chmod(0o555)
if selected is None:
    raise SystemExit(72)
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "unchanged_audit_launcher_execution_next_not_acceptance": True}), flush=True)
os.execv("/bin/bash", ["bash", str(P / "final_source_cpu.sbatch"), "audit", str(REQUEST)])

CURRENT_SOURCE_SACCT_READINESS
```
