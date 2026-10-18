# ROOT unique vendor-log successor software qualification envelope — SOURCE preparation

This operational HUMAN text records the exact Root stdlib current-allocation readiness and metadata guard before the reviewed OWN6 software entry. It is UNEXECUTED until Root submits a unique owned CPU job and saves the real primary claim. The changed library has 90 prepared contracts, not an acceptance. Existing 65 acceptance/16338 failure/16357 diagnostic and all old inputs remain immutable.

Exact source package: S/pending/final_source_closure_v3_fixturefix3_vendor_log_leaf1, OWN6 bytes 79372/55559/1585/14897/3517/8888, SourceRO seal submissions/final_source_vendor_log_leaf1_source_metadata_readonly_seal/receipt.json6719. Root and two whole-source static reviews passed; Source6 444/P555, bytes/inode/mtime/nlink unchanged, only mode/ctime changed. The actual current SourceRO receipt is checked inside the owned CPU before execution.

The stdlib readiness derives from actual reviewed Root16357 recipe with only proof/name/schema labels changed. It requires current scontrol RUNNING owner/account/organ/name test9_final_source_vendor_log_leaf_v3/CPU1/task1/16G/00:30:00 and all present TRES GPU namespaces zero, then fresh unique six-column sacct RUNNING owner/account/organ/CPU1/GPU0 within30 attempts/60 seconds, per-RPC<=5 seconds. Every real raw reply/returncode/timeout/partial bytes is preserved; no proxy or historical GPU inference. On exhaustion it stops before project source/compile/tests/hash. Original15201 cause remains unproven.

After readiness the exact final source path/size/inode/mtime/mode444/nlink1/nonlink ancestry and whole current SourceRO stable metadata table are checked; then os.execv runs /bin/bash exact reviewed launcher software mode. That launcher supplies the original isolated CPU environment/BLAS1/CORE-B/no-I and unique job-derived TMP/OUT. Its software routine actually hashes original6/frozen6, captures snapshot and conditional CORE, compiles only own Python files/bash syntax, runs all90 contracts, checks source12/runtime before/end/after acceptance output, and emits the actual software descriptor only after checks. No Source audit/stage/model/Cost/science/report/Git/public/package/restore/ACTIVE operation is performed.

Root will require full actual software acceptance/contracts/log/snapshot/source12/Core CPU stdout proof, fresh terminal0:0/current GPU0 readiness, metadata-only RO seal and independent full saved-content readback. Tests within this changed qualification are justified; no unchanged standalone old65/53/84/F130 repeat. Partial/PASS-shaped files alone never qualify a failed job.

This HUMAN and its later primary claim/readiness/raw/logs/metadata seals are explicit late Composer/source-history coverage, not the library's own software inputs or its own Plan/audit prerequisites. Future Source inclusion must explicitly publish this .md containing the operational source; no self-cycle or invented current SHA is allowed.

## Exact Root CPU prelude and software dispatch

```python
import os, sys, json, re, stat, time, datetime, subprocess
from pathlib import Path
S = Path("/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery")
jid = os.environ.get("SLURM_JOB_ID", "")
if not re.fullmatch("[0-9]+", jid):
    raise SystemExit("Current owned Slurm job ID required")
expected_env = {"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
if any(os.environ.get(k) != v for k, v in expected_env.items()) or "PYTHONPATH" in os.environ:
    raise SystemExit("Original CPU/import/thread isolation required")
D = S / "submissions" / ("source_vendor_log_leaf_software_current_sacct_readiness_" + jid)
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
    gpu_keys = []
    gpu_bases = ("gpu", "gres/gpu", "gres:gpu")
    for item in text.split(","):
        if item.count("=") != 1:
            raise ValueError("Malformed allocated TRES")
        key, value = item.split("=", 1)
        if not key or not value or key in values:
            raise ValueError("Empty or duplicate allocated TRES key")
        gpu_base = next((base for base in gpu_bases if key == base or key.startswith(base + ":")), None)
        if gpu_base is not None:
            if key != gpu_base and not re.fullmatch("[A-Za-z0-9_.-]+", key[len(gpu_base) + 1:]):
                raise ValueError("Malformed typed GPU key")
            gpu_keys.append(key)
        elif "gpu" in key.lower():
            raise ValueError("Unrecognized GPU allocation namespace")
        values[key] = value
    if "cpu" not in values or not re.fullmatch("[0-9]+", values["cpu"]) or int(values["cpu"]) != 1:
        raise ValueError("Actual CPU1 required")
    gpu_values = [values[key] for key in gpu_keys]
    if any(not re.fullmatch("[0-9]+", value) for value in gpu_values) or any(int(value) != 0 for value in gpu_values):
        raise ValueError("Actual current GPU0 required")
    return values
query_env = dict(os.environ, TZ="UTC", SLURM_TIME_FORMAT="standard")
commands = []
operation_deadline = time.monotonic() + 60
def query(argv, prefix):
    timeout = max(0.001, min(5, operation_deadline - time.monotonic()))
    timeout_observed = False
    try:
        r = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=query_env, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        class IncompleteQuery:
            returncode = None
            stdout = e.stdout or b""
            stderr = e.stderr or b""
        r = IncompleteQuery()
        timeout_observed = True
    a = {"argv": argv, "returncode": r.returncode,
         "raw_stdout": persist(prefix + ".stdout", r.stdout),
         "raw_stderr": persist(prefix + ".stderr", r.stderr),
         "timeout_seconds": timeout, "timeout_observed": timeout_observed,
         "query_completed": not timeout_observed}
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
    required = {"JobId": jid, "JobName": "test9_final_source_vendor_log_leaf_v3", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-source-vendor-log-leaf-software-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_SOURCE_VENDOR_LOG_LEAF_SOFTWARE_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
    persist("readiness.json", (json.dumps(obj, indent=2) + "\n").encode()); D.chmod(0o555); raise
argv = ["sacct", "-X", "-j", jid, "--noheader", "--parsable2", "--format=JobIDRaw,State,AllocTRES,User%64,Account%64,Partition%64"]
attempts = []; selected = None; deadline = operation_deadline
for number in range(1, 31):
    if time.monotonic() >= deadline:
        break
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_SOURCE_VENDOR_LOG_LEAF_SOFTWARE_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_SOURCE_VENDOR_LOG_LEAF_SOFTWARE_NOT_EXECUTED"
obj = {"schema": "root-current-owned-source-vendor-log-leaf-software-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
       "current_scontrol_observation": ctl_saved, "current_scontrol_TRES": current_tres,
       "all_present_scontrol_TRES_fields_CPU1_GPU0": current_tres_fields, "attempts": attempts,
       "selected_actual_attempt": selected, "maximum_attempts": 30, "maximum_wait_seconds": 60,
       "environment": {"TZ": "UTC", "SLURM_TIME_FORMAT": "standard", **expected_env},
       "requested_GPUs": 0, "current_allocation_only_no_historical_GPU_inference": True,
       "no_source_or_request_hashes_or_imports_or_tests_by_wait": True,
       "unchanged_library_cpu_guard_will_freshly_requery": True, "actual_queries_not_proxy_or_synthesized_replies": True,
       "production_audit_entered": False, "original15201_specific_cause_proven": False,
       "additional_pin_or_source_audit_stage_Git_ACTIVE_acceptance": False}
persist("readiness.json", (json.dumps(obj, indent=2) + "\n").encode()); D.chmod(0o555)
if selected is None:
    raise SystemExit(72)
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "software_execution_next_not_acceptance": True}), flush=True)




# Reviewed original OWN6 software entry only; no Source audit or model operation.
P=S/"pending/final_source_closure_v3_fixturefix3_vendor_log_leaf1"
names=("final_source_closure.py","test_final_source_closure.py","final_source_cpu.sbatch","HANDOFF.md","FINAL_SOURCE_CHECKLIST.md","final_source_context_adapter.py")
sizes=(79372,55559,1585,14897,3517,8888)
mtimes=(1792047094000000000,1792047094000000000,1792046759000000000,1792047094000000000,1792047094000000000,1792046518000000000)
assert set(x.name for x in P.iterdir())==set(names) and P.lstat().st_ino==144115543165753680 and stat.S_IMODE(P.lstat().st_mode)==0o555
for index,(name,size,mtime) in enumerate(zip(names,sizes,mtimes)):
 p=P/name
 for a in [p]+list(p.parents): assert not stat.S_ISLNK(a.lstat().st_mode)
 s=p.lstat()
 assert stat.S_ISREG(s.st_mode) and stat.S_IMODE(s.st_mode)==0o444 and s.st_nlink==1 and s.st_size==size and s.st_ino==144115543165753681+index and s.st_mtime_ns==mtime
seal=S/"submissions/final_source_vendor_log_leaf1_source_metadata_readonly_seal/receipt.json"
assert stat.S_IMODE(seal.lstat().st_mode)==0o444 and seal.lstat().st_nlink==1
saved=json.loads(seal.read_text())
assert saved["Root_plus_two_independent_whole_STATIC_PASS"]is True and saved["status"]=="REVIEWED_FINAL_SOURCE_VENDOR_LOG_LEAF_OWN6_METADATA_RO_PASS_90_PREPARED_NOT_EXECUTED"
assert saved["after_files"]==[dict(path=str(P/name),bytes=(P/name).lstat().st_size,inode=(P/name).lstat().st_ino,mtime_ns=(P/name).lstat().st_mtime_ns,ctime_ns=(P/name).lstat().st_ctime_ns,mode=(P/name).lstat().st_mode,dev=(P/name).lstat().st_dev,nlink=(P/name).lstat().st_nlink,uid=(P/name).lstat().st_uid,gid=(P/name).lstat().st_gid)for name in names]
os.execv("/bin/bash",["/bin/bash",str(P/"final_source_cpu.sbatch"),"software"])
```
