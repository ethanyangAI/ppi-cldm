exec env -u PYTHONPATH CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /lustre/users/u21111210118/projects/test9/env/core/bin/python -B - <<'PY'
import os, sys, json, re, stat, time, datetime, subprocess
from pathlib import Path
S = Path("/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery")
jid = os.environ.get("SLURM_JOB_ID", "")
if not re.fullmatch("[0-9]+", jid):
    raise SystemExit("Current owned Slurm job ID required")
expected_env = {"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
if any(os.environ.get(k) != v for k, v in expected_env.items()) or "PYTHONPATH" in os.environ:
    raise SystemExit("Original CPU/import/thread isolation required")
D = S / "submissions" / ("source_plan_v9_ownsha_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_source_plan_v9_ownsha_cpu", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:10:00", "MinMemoryNode": "8G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/8G10/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-plan-v9-ownsha-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_PLAN_V9_OWN_SHA_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_PLAN_V9_OWN_SHA_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_PLAN_V9_OWN_SHA_NOT_EXECUTED"
obj = {"schema": "root-current-owned-plan-v9-ownsha-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "own_plan_hash_capture_next_not_acceptance": True}), flush=True)

# Only entered after actual current owned CPU1/GPU0 readiness.
import hashlib,importlib.util
R=Path("/lustre/users/u21111210118/projects/test9");CORE=R/"env/core/bin/python";REAL=CORE.with_name("python3.11")
SPEC = json.loads("{\"qualified_source_software\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/acceptance.json\", \"bytes\": 6562, \"sha256\": \"d7bb3b58dd24ed76ce3b55136a37a997774f1cd77c0debb94f484847c80d278d\"}, \"qualified_original_source6\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_closure.py\", \"bytes\": 223420, \"sha256\": \"895f34ae9444a5e08ab752cb557d17bd49c463475d39d5eb179d37cfb3be0608\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/test_final_source_closure.py\", \"bytes\": 159993, \"sha256\": \"012821051ca9708724e66ad39e7b66986f955f736c480901786cd6c2cb3893e8\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_cpu.sbatch\", \"bytes\": 1607, \"sha256\": \"2a19202da1fe8913b4284ded128706688a15a2d9b6c976bea693d9f6e100a7ef\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/HANDOFF.md\", \"bytes\": 17911, \"sha256\": \"7985ce5ba683b4305dc277e9f6b29a01429556cb84b9ae41375352703e0ee415\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 4611, \"sha256\": \"2b812507033aebfa05724433b46005bb67fc42740cfe1ecba554a7b78d882101\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_context_adapter.py\", \"bytes\": 12691, \"sha256\": \"f8379565b33c5efa5faea4dcddec9e48a416d5ca823bf9443255789cd463e07c\"}], \"qualified_frozen_source6\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_closure.py\", \"bytes\": 223420, \"sha256\": \"895f34ae9444a5e08ab752cb557d17bd49c463475d39d5eb179d37cfb3be0608\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/test_final_source_closure.py\", \"bytes\": 159993, \"sha256\": \"012821051ca9708724e66ad39e7b66986f955f736c480901786cd6c2cb3893e8\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_cpu.sbatch\", \"bytes\": 1607, \"sha256\": \"2a19202da1fe8913b4284ded128706688a15a2d9b6c976bea693d9f6e100a7ef\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/HANDOFF.md\", \"bytes\": 17911, \"sha256\": \"7985ce5ba683b4305dc277e9f6b29a01429556cb84b9ae41375352703e0ee415\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 4611, \"sha256\": \"2b812507033aebfa05724433b46005bb67fc42740cfe1ecba554a7b78d882101\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_context_adapter.py\", \"bytes\": 12691, \"sha256\": \"f8379565b33c5efa5faea4dcddec9e48a416d5ca823bf9443255789cd463e07c\"}], \"qualified_source12_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_closure.py\", \"bytes\": 223420, \"inode\": 144115643443092398, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/test_final_source_closure.py\", \"bytes\": 159993, \"inode\": 144115643443092399, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_cpu.sbatch\", \"bytes\": 1607, \"inode\": 144115643443092400, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/HANDOFF.md\", \"bytes\": 17911, \"inode\": 144115643443092401, \"mtime_ns\": 1792102471000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 4611, \"inode\": 144115643443092402, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_context_adapter.py\", \"bytes\": 12691, \"inode\": 144115643443092403, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_closure.py\", \"bytes\": 223420, \"inode\": 144115643493442364, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/test_final_source_closure.py\", \"bytes\": 159993, \"inode\": 144115643493442365, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_cpu.sbatch\", \"bytes\": 1607, \"inode\": 144115643493442366, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/HANDOFF.md\", \"bytes\": 17911, \"inode\": 144115643493442367, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 4611, \"inode\": 144115643493442368, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_context_adapter.py\", \"bytes\": 12691, \"inode\": 144115643493442369, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"qualified_original_source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1\", \"bytes\": 4096, \"inode\": 144115643443092397, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"qualified_frozen_source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner\", \"bytes\": 4096, \"inode\": 144115643493442363, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"qualified_software_controls\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/acceptance.json\", \"bytes\": 6562, \"sha256\": \"d7bb3b58dd24ed76ce3b55136a37a997774f1cd77c0debb94f484847c80d278d\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/contracts.json\", \"bytes\": 2137, \"sha256\": \"7d333ed0c2b3370759ceb5b2f775cd48c135f3a878319352f429a3c0022ca1df\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/contracts.txt\", \"bytes\": 36566, \"sha256\": \"3e746de3e0890a250c38b8aae0a6db4f8c9e4edaec4b7635abc3aa549c6e67d2\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/source_snapshot.json\", \"bytes\": 15783, \"sha256\": \"10f0397322fd26550e9a260053b784cc5d34b22aa3e46cfb77336a5ef8b90e90\"}], \"qualified_software_control_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/acceptance.json\", \"bytes\": 6562, \"inode\": 144115643493448230, \"mtime_ns\": 1792103360000000000, \"ctime_ns\": 1792103360000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/contracts.json\", \"bytes\": 2137, \"inode\": 144115643493448228, \"mtime_ns\": 1792103360000000000, \"ctime_ns\": 1792103360000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/contracts.txt\", \"bytes\": 36566, \"inode\": 144115643493442370, \"mtime_ns\": 1792103360000000000, \"ctime_ns\": 1792103360000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/source_snapshot.json\", \"bytes\": 15783, \"inode\": 144115643493448229, \"mtime_ns\": 1792103360000000000, \"ctime_ns\": 1792103360000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"conditional_CORE_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python\", \"bytes\": 10, \"inode\": 144115618512131424, \"mtime_ns\": 1790940371000000000, \"ctime_ns\": 1790940371000000000, \"mode\": 41471, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\", \"bytes\": 25916456, \"inode\": 144115618512129393, \"mtime_ns\": 1790940364000000000, \"ctime_ns\": 1790940383000000000, \"mode\": 33277, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"source_software_terminal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_final_readonly_software17005_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 5076915, \"inode\": 144115643443092431, \"mtime_ns\": 1792103622000000000, \"ctime_ns\": 1792103622000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"software_outer_proof\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_final_readonly_software_outer_17005/execution_control.json\", \"bytes\": 44435, \"sha256\": \"42453546dafb0b96abacbf871aed090d534a6276b88c26e8799c1f8e797e7533\"}, \"software_outer_proof_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_final_readonly_software_outer_17005/execution_control.json\", \"bytes\": 44435, \"inode\": 144115643493448231, \"mtime_ns\": 1792103361000000000, \"ctime_ns\": 1792103361000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"source_readonly_seal\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_final_readonly_lifecycle1_source_metadata_readonly_seal/receipt.json\", \"bytes\": 5033846, \"sha256\": \"f3c4f19642fa5e0e7cc28bd699562565b78eb16aced61ceda5d0085a2981c76a\"}, \"source_readonly_seal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_final_readonly_lifecycle1_source_metadata_readonly_seal/receipt.json\", \"bytes\": 5033846, \"inode\": 144115643443092405, \"mtime_ns\": 1792102949000000000, \"ctime_ns\": 1792102949000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"software_humans_readonly_seal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_readonly_source_software_human_metadata_readonly_seal/receipt.json\", \"bytes\": 5036672, \"inode\": 144115643443092408, \"mtime_ns\": 1792103242000000000, \"ctime_ns\": 1792103242000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"plan_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17005_v9/final_source_plan.json\", \"bytes\": 1998209, \"inode\": 144115643443092433, \"mtime_ns\": 1792103833000000000, \"ctime_ns\": 1792104052000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17005_v9/HANDOFF.md\", \"bytes\": 17477, \"inode\": 144115643443092434, \"mtime_ns\": 1792103833000000000, \"ctime_ns\": 1792104052000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"plan_directory_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17005_v9\", \"bytes\": 4096, \"inode\": 144115643443092432, \"mtime_ns\": 1792103833000000000, \"ctime_ns\": 1792104052000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"plan_readonly_seal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v9_from17005_metadata_readonly_seal/receipt.json\", \"bytes\": 5079045, \"inode\": 144115643443092436, \"mtime_ns\": 1792104053000000000, \"ctime_ns\": 1792104053000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"prior_qualified_plan_and_handoff\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17002_v8/final_source_plan.json\", \"bytes\": 1985977, \"sha256\": \"a73761d8c2af11f5bf4395620210307354e9afc53d39d712ccc1b88804b16ade\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17002_v8/HANDOFF.md\", \"bytes\": 25414, \"sha256\": \"91fe06073ce824ad5cc448fc389c24eac97f0d36c05cdb6abb5c17b4981df58b\"}], \"prior_qualified_plan_and_handoff_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17002_v8/final_source_plan.json\", \"bytes\": 1985977, \"inode\": 144115643443092344, \"mtime_ns\": 1792099748000000000, \"ctime_ns\": 1792099991000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17002_v8/HANDOFF.md\", \"bytes\": 25414, \"inode\": 144115643443092345, \"mtime_ns\": 1792099748000000000, \"ctime_ns\": 1792099991000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"current_canonical_Source4\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\", \"bytes\": 2225, \"sha256\": \"d602956154fb396fd14d7737c360d7d35144b4e6ca6c3d1c51eb6dc401e42615\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\", \"bytes\": 24234, \"sha256\": \"c8fe4495439826f0882b4c43952926e5de5361f88460320cc117d003352ff345\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\", \"bytes\": 1633, \"sha256\": \"2d40850d19c7835d658e7154e5a1cb53ae763e31d360b41eec253397f2c5befb\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\", \"bytes\": 6148, \"sha256\": \"c83e427f73ff1545253d64dbb165c7e60328bb698721d1e03663e6ea7d7c403f\"}], \"current_canonical_Source4_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\", \"bytes\": 2225, \"inode\": 144115543165691905, \"mtime_ns\": 1791727539000000000, \"ctime_ns\": 1791727539000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\", \"bytes\": 24234, \"inode\": 144115543165691892, \"mtime_ns\": 1791727495000000000, \"ctime_ns\": 1791727495000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\", \"bytes\": 1633, \"inode\": 144115543165691947, \"mtime_ns\": 1791727539000000000, \"ctime_ns\": 1791727539000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\", \"bytes\": 6148, \"inode\": 144115543165691893, \"mtime_ns\": 1791727495000000000, \"ctime_ns\": 1791727495000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"root_control_human\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V9_OWN_SHA_FROM17005_20261015_REV1.md\", \"primary_wrap\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v9_ownsha_from17005_REV1_primary_claim/wrap.sh\", \"actual_additional_14_Source_rows\": [{\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_closure.py\", \"bytes\": 223420, \"sha256\": \"895f34ae9444a5e08ab752cb557d17bd49c463475d39d5eb179d37cfb3be0608\"}, \"repository_relative\": \"delivery_tools/source_closure_final_readonly_lifecycle1/original/final_source_closure.py\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/test_final_source_closure.py\", \"bytes\": 159993, \"sha256\": \"012821051ca9708724e66ad39e7b66986f955f736c480901786cd6c2cb3893e8\"}, \"repository_relative\": \"delivery_tools/source_closure_final_readonly_lifecycle1/original/test_final_source_closure.py\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_cpu.sbatch\", \"bytes\": 1607, \"sha256\": \"2a19202da1fe8913b4284ded128706688a15a2d9b6c976bea693d9f6e100a7ef\"}, \"repository_relative\": \"delivery_tools/source_closure_final_readonly_lifecycle1/original/final_source_cpu.sbatch\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/HANDOFF.md\", \"bytes\": 17911, \"sha256\": \"7985ce5ba683b4305dc277e9f6b29a01429556cb84b9ae41375352703e0ee415\"}, \"repository_relative\": \"delivery_tools/source_closure_final_readonly_lifecycle1/original/HANDOFF.md\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 4611, \"sha256\": \"2b812507033aebfa05724433b46005bb67fc42740cfe1ecba554a7b78d882101\"}, \"repository_relative\": \"delivery_tools/source_closure_final_readonly_lifecycle1/original/FINAL_SOURCE_CHECKLIST.md\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_context_adapter.py\", \"bytes\": 12691, \"sha256\": \"f8379565b33c5efa5faea4dcddec9e48a416d5ca823bf9443255789cd463e07c\"}, \"repository_relative\": \"delivery_tools/source_closure_final_readonly_lifecycle1/original/final_source_context_adapter.py\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_closure.py\", \"bytes\": 223420, \"sha256\": \"895f34ae9444a5e08ab752cb557d17bd49c463475d39d5eb179d37cfb3be0608\"}, \"repository_relative\": \"delivery_tools/source_closure_final_readonly_lifecycle1/software_17005/final_source_closure.py\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/test_final_source_closure.py\", \"bytes\": 159993, \"sha256\": \"012821051ca9708724e66ad39e7b66986f955f736c480901786cd6c2cb3893e8\"}, \"repository_relative\": \"delivery_tools/source_closure_final_readonly_lifecycle1/software_17005/test_final_source_closure.py\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_cpu.sbatch\", \"bytes\": 1607, \"sha256\": \"2a19202da1fe8913b4284ded128706688a15a2d9b6c976bea693d9f6e100a7ef\"}, \"repository_relative\": \"delivery_tools/source_closure_final_readonly_lifecycle1/software_17005/final_source_cpu.sbatch\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/HANDOFF.md\", \"bytes\": 17911, \"sha256\": \"7985ce5ba683b4305dc277e9f6b29a01429556cb84b9ae41375352703e0ee415\"}, \"repository_relative\": \"delivery_tools/source_closure_final_readonly_lifecycle1/software_17005/HANDOFF.md\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 4611, \"sha256\": \"2b812507033aebfa05724433b46005bb67fc42740cfe1ecba554a7b78d882101\"}, \"repository_relative\": \"delivery_tools/source_closure_final_readonly_lifecycle1/software_17005/FINAL_SOURCE_CHECKLIST.md\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_context_adapter.py\", \"bytes\": 12691, \"sha256\": \"f8379565b33c5efa5faea4dcddec9e48a416d5ca823bf9443255789cd463e07c\"}, \"repository_relative\": \"delivery_tools/source_closure_final_readonly_lifecycle1/software_17005/final_source_context_adapter.py\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_FINAL_READONLY_SOURCE_SOFTWARE_FROM17004_20261015.md\", \"bytes\": 44713, \"sha256\": \"b2336883af3021f5c26dc7b1acaa78f7c5d382c0175c01a6019a21a4f13299a9\"}, \"repository_relative\": \"delivery_tools/human_history/ROOT_FIXED_FINAL_READONLY_SOURCE_SOFTWARE_FROM17004_20261015.md\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_final_readonly_lifecycle1_software_primary_claim/wrap.sh\", \"bytes\": 40374, \"sha256\": \"a6c02fece06dde382fbcacc0261b8de6a60b0a8cb1f4cef9d9849b6c12662518\"}, \"repository_relative\": \"delivery_tools/root_operational_programs/final_source_final_readonly_lifecycle1_software_primary_claim/wrap.sh\"}], \"prior_v8_ownsha_capture\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v8_ownsha_17003/capture.json\", \"bytes\": 61528, \"sha256\": \"d7d10162041c75d7e9a26425b997899f6acb11eca7b4fd20f8691fb2d50bc108\"}, \"prior_v8_ownsha_capture_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v8_ownsha_17003/capture.json\", \"bytes\": 61528, \"inode\": 144115643493442300, \"mtime_ns\": 1792100440000000000, \"ctime_ns\": 1792100440000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}}")
def need(v,msg):
 if not v:raise ValueError(msg)
def md(p):
 p=Path(p);x=p.lstat();return dict(path=str(p),bytes=x.st_size,inode=x.st_ino,mtime_ns=x.st_mtime_ns,ctime_ns=x.st_ctime_ns,mode=x.st_mode,dev=x.st_dev,nlink=x.st_nlink,uid=x.st_uid,gid=x.st_gid)
def authority(p):
 p=Path(p);need(p.is_absolute()and p.is_relative_to(R),"Exact authority path required")
 for a in [p]+list(p.parents):
  if a==R.parent:break
  need(not a.is_symlink(),"Nonlink ancestry required")
 return p
def rec(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open("rb")as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b);n+=len(b)
 return dict(path=str(p),bytes=n,sha256=h.hexdigest())
def ro(p,expected=None,metadata=None):
 p=authority(p);before=md(p);need(stat.S_ISREG(before["mode"])and stat.S_IMODE(before["mode"])==0o444 and before["nlink"]==1,"Readonly regular singlelink own file required")
 value=rec(p);need(md(p)==before,"Own file stable full metadata required")
 if expected is not None:need(value==expected,"Exact actual CPU-qualified own tuple required")
 if metadata is not None:need(before==metadata,"Exact qualified own metadata required")
 return value,before
def pairs(items):
 d={}
 for k,v in items:need(k not in d,"Duplicate own control JSON key");d[k]=v
 return d
def bad(s):raise ValueError("Nonfinite own control JSON "+s)
def finite_float(s):
 v=float(s);need(v==v and abs(v)!=float("inf"),"Finite own control JSON exponent required");return v
def read(p):
 with Path(p).open("r",encoding="utf-8")as f:return json.load(f,object_pairs_hook=pairs,parse_constant=bad,parse_float=finite_float)

need(Path(sys.executable)==CORE and sys.flags.optimize==0 and sys.flags.isolated==0 and sys.dont_write_bytecode,"Actual unoptimized CORE-B/no-I required")
core=SPEC["conditional_CORE_metadata"]
need(md(CORE)==core[0]and md(REAL)==core[1]and os.readlink(CORE)=="python3.11","Actual conditional CORE metadata/link required")
corepin=dict(path=str(REAL),bytes=25916456,sha256="76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a")
need(rec(REAL)==corepin and md(REAL)==core[1],"Actual conditional CORE ownbytes required")
sourcepins=SPEC["qualified_original_source6"]+SPEC["qualified_frozen_source6"];source_meta=SPEC["qualified_source12_metadata"]
need(len(sourcepins)==len(source_meta)==12,"Qualified original/frozen Source12 required")
for r,m in zip(sourcepins,source_meta):ro(r["path"],r,m)
source_dirs=[SPEC["qualified_original_source_directory"],SPEC["qualified_frozen_source_directory"]]
for x in source_dirs:
 need(md(authority(x["path"]))==x and stat.S_IMODE(x["mode"])==0o555 and x["nlink"]==2 and {p.name for p in Path(x["path"]).iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Exact readonly Source6 directory/universe required")
SW=SPEC["qualified_software_controls"]
for r,m in zip(SW,SPEC["qualified_software_control_metadata"]):ro(r["path"],r,m)
a=read(SW[0]["path"]);ct=read(SW[1]["path"])
need(a["source_files"]==SPEC["qualified_frozen_source6"]and a["original_executing_sources"]==SPEC["qualified_original_source6"]and a["allocation"]["job_id"]=="17005","Actual17005 original/frozen software bindings required")
terminalpin,terminalmeta=ro(SPEC["source_software_terminal_metadata"]["path"],metadata=SPEC["source_software_terminal_metadata"])
terminal=read(terminalpin["path"])
need(terminal["schema"]=="root-final-source-final-readonly-software17005-terminal-metadata-seal.v1"and terminal["actual_job_id"]=="17005"and terminal["Root_plus_two_whole_actual_software198_content_READBACK_PASS"]is True and terminal["actual_unique_named_tests"]==198 and terminal["historical196_names_and_relative_order_preserved"]is True and terminal["new2_actual_genuine_final_audit_PASS"]is True and terminal["actual_GPU0_from_current_readiness"]is True,"Actual accepted198 terminal context required")
need([terminal[k]for k in ["actual_software_acceptance","actual_contracts","actual_contract_log","actual_source_snapshot"]]==SW and terminal["fresh_terminal"]["returncode"]==0 and terminal["fresh_terminal"]["raw_stderr"]==""and terminal["fresh_terminal"]["numeric_9column_row"]==["17005","COMPLETED","0:0","42","1","test9_final_source_final_readonly_v3","u21111210118","u21111210118","organ"],"Exact qualified17005 SW4/fresh terminal required")
# Import only the actual qualified frozen source after all literal byte and metadata guards.
ss=importlib.util.spec_from_file_location("root_qualified_source17005_plan_v9_ownsha",Path(SPEC["qualified_frozen_source6"][0]["path"]))
g=importlib.util.module_from_spec(ss);ss.loader.exec_module(g)
need(g.software_shape(a,ct)==SPEC["qualified_frozen_source6"],"Qualified198 software shape required")
allocation=g.cpu();runtime=g.conditional_core_runtime()
need(allocation["job_id"]==jid and allocation["allocated_CPUs"]==1 and allocation["allocated_gpus"]==0 and allocation["numeric_sacct_row"]==attempts[selected-1]["actual_row"]and runtime==a["conditional_core_runtime"],"Fresh current CPU1/GPU0/Core required")
snapshot=read(SW[3]["path"]);need(g.software_snapshot_shape(a,snapshot)==snapshot,"Qualified software snapshot shape required")
outerpin,outermeta=ro(SPEC["software_outer_proof"]["path"],SPEC["software_outer_proof"],SPEC["software_outer_proof_metadata"])
outer=read(outerpin["path"]);fixed=outer["fixed_control_receipts"]
need(outer["actual_job_id"]=="17005"and outer["actual_unique_tests"]==198 and outer["historical196_names_and_relative_order_preserved"]is True and len(fixed)==36 and outer["status"]=="ROOT_ACTUAL_NEW_SOURCE_SOFTWARE_AND_OWN_CONTROLS_READBACK_PASS_NOT_SOURCE_AUDIT_OR_SCIENCE"and outer["actual_software_acceptance"]==SW[0]and outer["source_files"]==SPEC["qualified_frozen_source6"]and outer["original_executing_sources"]==SPEC["qualified_original_source6"],"Exact actual17005 outer controls required")
sourceROpin,sourceROmeta=ro(SPEC["source_readonly_seal"]["path"],SPEC["source_readonly_seal"],SPEC["source_readonly_seal_metadata"])
sourceRO=read(sourceROpin["path"])
need(sourceRO["source_directory_after"]==source_dirs[0]and sourceRO["source_files_after"]==source_meta[:6]and outer["source_readonly_seal"]==sourceROpin,"Actual SourceRO original6 identity required")
HROpin,HROmeta=ro(SPEC["software_humans_readonly_seal_metadata"]["path"],metadata=SPEC["software_humans_readonly_seal_metadata"])
HRO=read(HROpin["path"])
need(len(HRO)==22 and HRO["Root_and_two_whole_final_static_HUMAN_PASS"]is True,"Actual software Human readonly seal shape required")
additional=sourcepins+[fixed[0],fixed[1]]
destinations=["delivery_tools/source_closure_final_readonly_lifecycle1/original/"+Path(x["path"]).name for x in additional[:6]]
destinations+=["delivery_tools/source_closure_final_readonly_lifecycle1/software_17005/"+Path(x["path"]).name for x in additional[6:12]]
destinations+=["delivery_tools/human_history/"+Path(x["path"]).name for x in additional[12:13]]
destinations+=["delivery_tools/root_operational_programs/"+Path(additional[13]["path"]).parent.name+"/wrap.sh"]
additionalrows=[dict(receipt=r,repository_relative=d)for r,d in zip(additional,destinations)]
need(len(additional)==len(destinations)==len(set(destinations))==14 and additionalrows==SPEC["actual_additional_14_Source_rows"],"Exact actual fourteen Source/DOC ordered rows required")
additionalmeta=[ro(r["path"],r)[1]for r in additional]
planmeta=SPEC["plan_metadata"]
planpin,planbefore=ro(planmeta[0]["path"],metadata=planmeta[0]);handoffpin,handoffbefore=ro(planmeta[1]["path"],metadata=planmeta[1])
PLAN=Path(planpin["path"]);HANDOFF=Path(handoffpin["path"])
planROpin,planROmeta=ro(SPEC["plan_readonly_seal_metadata"]["path"],metadata=SPEC["plan_readonly_seal_metadata"])
planRO=read(planROpin["path"])
need(planRO["schema"]=="root-new-plan-v9-metadata-readonly-seal.v1"and planRO["Root_and_two_independent_whole_Plan_and_HANDOFF_static_PASS"]is True and planRO["after_files"]==planmeta and planRO["after_directory"]==SPEC["plan_directory_metadata"],"Actual new reviewed Plan2 readonly seal required")
need(md(authority(PLAN.parent))==SPEC["plan_directory_metadata"]and stat.S_IMODE(SPEC["plan_directory_metadata"]["mode"])==0o555 and {p.name for p in PLAN.parent.iterdir()}=={"final_source_plan.json","HANDOFF.md"},"Exact readonly Plan2 directory required")
priorpins=SPEC["prior_qualified_plan_and_handoff"]
for r,m in zip(priorpins,SPEC["prior_qualified_plan_and_handoff_metadata"]):ro(r["path"],r,m)
priorCAPpin,priorCAPmeta=ro(SPEC["prior_v8_ownsha_capture"]["path"],SPEC["prior_v8_ownsha_capture"],SPEC["prior_v8_ownsha_capture_metadata"])
priorCAP=read(priorCAPpin["path"])
need(priorCAP["actual_job_id"]=="17003"and[priorCAP["plan"],priorCAP["handoff"]]==priorpins,"Actual prior17003 qualified V8 Plan/H tuples required")
canonical=SPEC["current_canonical_Source4"];canonicalmeta=SPEC["current_canonical_Source4_metadata"]
need(priorCAP["current_canonical_Source4_receipts"]==canonical and priorCAP["current_canonical_Source4_metadata_after"]==canonicalmeta and len(canonical)==len(canonicalmeta)==4,"Exact current canonicalSource4 bindings required")
def canonical_end():
 for r,m in zip(canonical,canonicalmeta):
  p=authority(r["path"]);need(md(p)==m and stat.S_ISREG(m["mode"])and stat.S_IMODE(m["mode"])==0o664 and m["nlink"]==1,"Only four literal current mutable Source leaves permitted")
  need(g.rec(p)==r and md(p)==m,"Current canonicalSource4 ownbytes/fullMD drift")
canonical_end()
plan=read(PLAN);old=read(priorpins[0]["path"])
roles=["formal13260_terminal_v3","native74_cache_catalog","native74_cache_binding","reference_free_e2e","formal_common_review","independent_statistics","scientific_report","final_delivery_tools","default_workflow_integration"]
need(len(plan)==len(old)==34 and list(plan)==list(old)and plan["schema"]=="final-source-closure-plan.v3"and plan["library_software_acceptance"]==SW[0]and[m["role"]for m in plan["modules"]]==roles,"Same34 keys/order/exactnine roles/current17005 software required")
need(plan["modules"][7]["sources"][-14:]==additionalrows and plan["modules"][7]["seeds"][-18:]==additional+SW,"Exact Source14 safeSeed18 ordered tails required")
need(len(plan["context_parent_seeds"])==17 and plan["context_parent_seeds"]==old["context_parent_seeds"]and len(plan["aliases"])==7 and plan["aliases"]==old["aliases"],"Exact ordered17 parents and seven aliases unchanged")
rewound=json.loads(json.dumps(plan,allow_nan=False));rewound["library_software_acceptance"]=old["library_software_acceptance"];rewound["modules"][7]["sources"]=rewound["modules"][7]["sources"][:-14];rewound["modules"][7]["seeds"]=rewound["modules"][7]["seeds"][:-18]
def same(x,y):
 need(type(x)is type(y),"Preserved Plan type drift")
 if type(x)is dict:
  need(list(x)==list(y),"Preserved Plan key order drift")
  for k in x:same(x[k],y[k])
 elif type(x)is list:
  need(len(x)==len(y),"Preserved Plan list length drift")
  for a,b in zip(x,y):same(a,b)
 else:need(x==y,"Preserved Plan scalar drift")
same(rewound,old)
need((json.dumps(rewound,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode()==Path(priorpins[0]["path"]).read_bytes(),"Entire serialized raw V8 must rewind exactly")
def identity(r):g.receipt_shape(r);return(r["path"],r["bytes"],r["sha256"])
allsources=[r for m in plan["modules"]for r in m["sources"]];allseeds=[r for m in plan["modules"]for r in m["seeds"]]
need(len(allsources)==702 and len({r["repository_relative"]for r in allsources})==641 and len(allseeds)==3883 and len({identity(r)for r in allseeds})==3810 and len(plan["modules"][7]["sources"])==503 and len(plan["modules"][7]["seeds"])==3737,"Exact finite newPlan702/641/3883/3810/final503/3737 required")
need(not set(destinations)&{r["repository_relative"]for m in old["modules"]for r in m["sources"]},"New14 destination collision")
need(g.module_plan(plan)==plan["modules"],"Qualified module_plan pure object/lexical shape required, no child IO")
need(planpin["bytes"]==1998209 and planpin["bytes"]<2097152 and handoffpin["bytes"]==17477,"Exact reviewed newPlan/H sizes required")
ownhuman,ownhumanmeta=ro(SPEC["root_control_human"]);ownwrap,ownwrapmeta=ro(SPEC["primary_wrap"])
humantext=Path(ownhuman["path"]).read_text("utf-8");wraptext=Path(ownwrap["path"]).read_text("utf-8")
need(humantext.count("```python\n")==1 and wraptext.endswith("\nPY\n")and wraptext.partition("<<'PY'\n")[2][:-4].rstrip("\n")==humantext.split("```python\n",1)[1].split("\n```",1)[0].rstrip("\n"),"Actual precreated shell must bind whole reviewed Human")
readiness=read(D/"readiness.json");readyvalues=[ro(D/"readiness.json")]
for cmd in[readiness["current_scontrol_observation"]]+readiness["attempts"]:
 for key in["raw_stdout","raw_stderr"]:readyvalues.append(ro(cmd[key]["path"]))
controls=[(planpin,planbefore),(handoffpin,handoffbefore),(ownhuman,ownhumanmeta),(ownwrap,ownwrapmeta),(planROpin,planROmeta),(sourceROpin,sourceROmeta),(HROpin,HROmeta),(outerpin,outermeta),(terminalpin,terminalmeta),(priorCAPpin,priorCAPmeta)]
controls +=[(r,m)for r,m in zip(priorpins,SPEC["prior_qualified_plan_and_handoff_metadata"])]
need(len(controls)==len({r["path"]for r,m in controls})==12,"Twelve finite own Source/control files required")
def qualified_rec_end():
 need([g.rec(r["path"])for r,m in controls]==[r for r,m in controls]and[md(authority(r["path"]))for r,m in controls]==[m for r,m in controls],"Qualified G17005.rec actual twelve own tuples/fullMD after each batch required")
qualified_rec_end()
protected=planRO["protected_inputs_after"]+planRO["protected_directories_after"]
need(planRO["protected_inputs_before"]==planRO["protected_inputs_after"]and planRO["protected_directories_before"]==planRO["protected_directories_after"]and len(protected)==4874,"Entire4874 protected metadata required")
def inputs_end():
 need(md(CORE)==core[0]and md(REAL)==core[1]and rec(REAL)==corepin and md(REAL)==core[1]and os.readlink(CORE)=="python3.11","Conditional CORE ownbytes/stableMD drift")
 for r,m in zip(sourcepins,source_meta):ro(r["path"],r,m)
 for x in source_dirs:need(md(authority(x["path"]))==x and {p.name for p in Path(x["path"]).iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Source6 directory drift")
 for r,m in zip(SW,SPEC["qualified_software_control_metadata"]):ro(r["path"],r,m)
 for r,m in controls+readyvalues:ro(r["path"],r,m)
 qualified_rec_end()
 for r,m in zip(additional,additionalmeta):ro(r["path"],r,m)
 for x in protected:need(md(authority(x["path"]))==x,"Finite protected fullmetadata drift")
 need(md(authority(PLAN.parent))==SPEC["plan_directory_metadata"]and {p.name for p in PLAN.parent.iterdir()}=={"final_source_plan.json","HANDOFF.md"},"Plan2 directory drift")
 canonical_end();need(g.conditional_core_runtime()==runtime,"Approved conditional interpreter drift")
inputs_end()
OUT=authority(S/"runs")/("final_source_plan_v9_ownsha_"+jid)
need(not OUT.exists()and not OUT.is_symlink(),"Exclusive absent new ownSHA output required")
OUT.mkdir(mode=0o755);phase="own_new_PlanV9_and_twelve_controls_no_receipt_child_IO"
try:
 out=dict(schema="root-fixed-source-plan-v9-own-sha-control-capture.v1",status="ACTUAL_NEW_PLAN_V9_OWN_SHA_AND14_PINNED_SOURCE_DOC_ADDITIONS_CPU_VERIFIED_NOT_SOURCE_AUDIT_ACCEPTANCE",actual_job_id=jid,allocation=allocation,current_actual_readiness=readiness,current_readiness_own_CPU_receipts=[x[0]for x in readyvalues],plan=planpin,handoff=handoffpin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,control_receipts=[r for r,m in controls],control_metadata_before=[m for r,m in controls],control_metadata_after=[md(r["path"])for r,m in controls],software_acceptance=SW[0],software_control_receipts=SW,software_control_metadata_before=SPEC["qualified_software_control_metadata"],software_control_metadata_after=[md(r["path"])for r in SW],source_files=SPEC["qualified_frozen_source6"],original_executing_sources=SPEC["qualified_original_source6"],qualified_source12_metadata=source_meta,conditional_core_runtime=runtime,qualified_software17005_terminal_own_CPU_receipt=terminalpin,prior_qualified_PlanV8_and_Handoff=priorpins,qualified_prior17003_ownsha_capture=priorCAPpin,additional_14_Source_rows=additionalrows,additional_14_Source_metadata=additionalmeta,additional_18_safe_seed_receipts=additional+SW,current_canonical_Source4_receipts=canonical,current_canonical_Source4_metadata_before=canonicalmeta,current_canonical_Source4_metadata_after=[md(r["path"])for r in canonical],plan_directory_metadata_before=SPEC["plan_directory_metadata"],plan_directory_metadata_after=md(PLAN.parent),Source_n=702,destination_n=641,seed_n=3883,unique_seed_n=3810,role_n=9,parent_n=17,ordered_alias_n=7,all34keys_type_order_and_original_V8_serialized_bytes_rewind_PASS=True,qualified_module_plan_pure_shape_PASS=True,qualified_G17005_rec_all12_controls_pre_end_PASS=True,all_Source12_SW4_Core_controls12_Source14_canonical4_protected4874_pre_end_afteroutput_finalreadonly_PASS=True,plan_child_receipts_shape_only_no_child_IO=True,source_audit_executed=False,source_staged=False,published=False,ACTIVE_changed=False,compiler_or_tests_or_new_software_qualification_executed=False,scientific_receipt_children_read_or_hashed=False,historical_Slurm_queried=False,own_created_controls_LATE_COMPOSER_ONLY_NOT_PLAN_PREREQUISITES=True)
 raw=(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode();path=OUT/"capture.json"
 with path.open("xb")as f:f.write(raw);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444);os.fsync(f.fileno())
 descriptor=g.rec(path);outmeta=md(path)
 need(path.read_bytes()==raw and read(path)==out and stat.S_IMODE(outmeta["mode"])==0o444 and outmeta["nlink"]==1,"Whole exclusive capture readonly reread required")
 inputs_end();OUT.chmod(0o555)
 fd=os.open(str(OUT),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
 outdir=md(authority(OUT))
 need(stat.S_IMODE(outdir["mode"])==0o555 and outdir["nlink"]==2 and {p.name for p in OUT.iterdir()}=={"capture.json"}and path.read_bytes()==raw and read(path)==out and g.rec(path)==descriptor and md(path)==outmeta,"Final readonly own capture directory/fullbytes required")
 inputs_end();need(md(authority(OUT))==outdir and md(path)==outmeta,"Final output fullmetadata after input guards required")
 print(json.dumps(dict(status=out["status"],capture=descriptor,plan=planpin,handoff=handoffpin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,qualified_software17005_terminal_own_CPU_receipt=terminalpin,Source_n=702,destination_n=641,seed_n=3883,unique_seed_n=3810,role_n=9,parent_n=17,final_output_directory_metadata=outdir,Plan_own_SHA_qualified_only_AFTER_fresh_terminal_RO_Root_and_independent_content_readback=True),sort_keys=True),flush=True)
except BaseException as e:
 try:
  failure=(json.dumps(dict(status="ACTUAL_PLAN_V9_OWN_SHA_UNQUALIFIED",actual_job_id=jid,phase=phase,reason_type=type(e).__name__,reason=str(e),source_staged=False,published=False,ACTIVE_changed=False),indent=2)+"\n").encode()
  with(OUT/"typed_incomplete.json").open("xb")as f:f.write(failure);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 except Exception as se:print("Readonly failure output best-effort: "+repr(se),file=sys.stderr,flush=True)
 raise
PY
