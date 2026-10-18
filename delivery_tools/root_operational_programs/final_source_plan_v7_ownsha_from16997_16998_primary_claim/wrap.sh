set -euo pipefail
unset PYTHONPATH
export CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python -B - <<'PY'
import os, sys, json, re, stat, time, datetime, subprocess
from pathlib import Path
S = Path("/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery")
jid = os.environ.get("SLURM_JOB_ID", "")
if not re.fullmatch("[0-9]+", jid):
    raise SystemExit("Current owned Slurm job ID required")
expected_env = {"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
if any(os.environ.get(k) != v for k, v in expected_env.items()) or "PYTHONPATH" in os.environ:
    raise SystemExit("Original CPU/import/thread isolation required")
D = S / "submissions" / ("source_plan_v7_ownsha_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_source_plan_v7_ownsha_cpu", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:10:00", "MinMemoryNode": "8G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/8G10/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-plan-v7-ownsha-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_PLAN_V7_OWN_SHA_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_PLAN_V7_OWN_SHA_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_PLAN_V7_OWN_SHA_NOT_EXECUTED"
obj = {"schema": "root-current-owned-plan-v7-ownsha-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
SPEC=json.loads("{\"qualified_source_software\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/acceptance.json\", \"bytes\": 6653, \"sha256\": \"04f86af25ee4057ed665268d03a19b637bc4898e00a3f0ffcf4424014eb4c4de\"}, \"qualified_original_source6\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_closure.py\", \"bytes\": 190920, \"sha256\": \"d4a94d4a8e1e8c32a688679ae930e50d64d06efacfd02d9dfa9516115b82d8b5\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/test_final_source_closure.py\", \"bytes\": 112898, \"sha256\": \"0ee02015d3edad2ee7066693bba285761a9decc3a7a586e87c4d81ff95e3b6e1\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_cpu.sbatch\", \"bytes\": 1658, \"sha256\": \"f3f0d3d461f0bcc51f8f22babdeac6d8b63be987aa3ed34f3dd39b06e26cc322\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/HANDOFF.md\", \"bytes\": 16737, \"sha256\": \"c32eacc9badb1799011998d90fabd840f1935daeb0e3c8ede6617b5a1d70f1be\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3224, \"sha256\": \"787184624c400a14f4155b74afa9fbdd87cdd8e79bdaec9c7977663d9cd74aa5\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_context_adapter.py\", \"bytes\": 10939, \"sha256\": \"e151b2ba918c702d011fc72d3879f60e35972a6c8fcee8f7afe468819944938b\"}], \"qualified_frozen_source6\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/final_source_closure.py\", \"bytes\": 190920, \"sha256\": \"d4a94d4a8e1e8c32a688679ae930e50d64d06efacfd02d9dfa9516115b82d8b5\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/test_final_source_closure.py\", \"bytes\": 112898, \"sha256\": \"0ee02015d3edad2ee7066693bba285761a9decc3a7a586e87c4d81ff95e3b6e1\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/final_source_cpu.sbatch\", \"bytes\": 1658, \"sha256\": \"f3f0d3d461f0bcc51f8f22babdeac6d8b63be987aa3ed34f3dd39b06e26cc322\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/HANDOFF.md\", \"bytes\": 16737, \"sha256\": \"c32eacc9badb1799011998d90fabd840f1935daeb0e3c8ede6617b5a1d70f1be\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3224, \"sha256\": \"787184624c400a14f4155b74afa9fbdd87cdd8e79bdaec9c7977663d9cd74aa5\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/final_source_context_adapter.py\", \"bytes\": 10939, \"sha256\": \"e151b2ba918c702d011fc72d3879f60e35972a6c8fcee8f7afe468819944938b\"}], \"qualified_source12_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_closure.py\", \"bytes\": 190920, \"inode\": 144115643443092175, \"mtime_ns\": 1792087604000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/test_final_source_closure.py\", \"bytes\": 112898, \"inode\": 144115643443092176, \"mtime_ns\": 1792087698000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_cpu.sbatch\", \"bytes\": 1658, \"inode\": 144115643443092177, \"mtime_ns\": 1792087604000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/HANDOFF.md\", \"bytes\": 16737, \"inode\": 144115643443092178, \"mtime_ns\": 1792087698000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3224, \"inode\": 144115643443092179, \"mtime_ns\": 1792087698000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_context_adapter.py\", \"bytes\": 10939, \"inode\": 144115643443092180, \"mtime_ns\": 1792087604000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/final_source_closure.py\", \"bytes\": 190920, \"inode\": 144115643493420117, \"mtime_ns\": 1792088995000000000, \"ctime_ns\": 1792088995000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/test_final_source_closure.py\", \"bytes\": 112898, \"inode\": 144115643493420118, \"mtime_ns\": 1792088995000000000, \"ctime_ns\": 1792088995000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/final_source_cpu.sbatch\", \"bytes\": 1658, \"inode\": 144115643493420119, \"mtime_ns\": 1792088995000000000, \"ctime_ns\": 1792088995000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/HANDOFF.md\", \"bytes\": 16737, \"inode\": 144115643493420120, \"mtime_ns\": 1792088995000000000, \"ctime_ns\": 1792088995000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3224, \"inode\": 144115643493420121, \"mtime_ns\": 1792088995000000000, \"ctime_ns\": 1792088995000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/final_source_context_adapter.py\", \"bytes\": 10939, \"inode\": 144115643493420122, \"mtime_ns\": 1792088995000000000, \"ctime_ns\": 1792088995000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"qualified_original_source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1\", \"bytes\": 4096, \"inode\": 144115643443092174, \"mtime_ns\": 1792087604000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"qualified_frozen_source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner\", \"bytes\": 4096, \"inode\": 144115643493420116, \"mtime_ns\": 1792088995000000000, \"ctime_ns\": 1792088995000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"qualified_software_controls\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/acceptance.json\", \"bytes\": 6653, \"sha256\": \"04f86af25ee4057ed665268d03a19b637bc4898e00a3f0ffcf4424014eb4c4de\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/contracts.json\", \"bytes\": 2193, \"sha256\": \"f9e7e3519f79e964221e1b9b7613714bad0dd096bd7fc8b8eb09500e6819d35a\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/contracts.txt\", \"bytes\": 27318, \"sha256\": \"8b16f21f28de4fcf3bebd2d99523976b68b4e9f2dc53d7e9bb458bdec6aba839\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/source_snapshot.json\", \"bytes\": 15984, \"sha256\": \"8d7f5d980827b58d558cba5d16439a63dd669b7a8acdd9156d2ca88410c629e1\"}], \"qualified_software_control_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/acceptance.json\", \"bytes\": 6653, \"inode\": 144115643493424905, \"mtime_ns\": 1792089023000000000, \"ctime_ns\": 1792089023000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/contracts.json\", \"bytes\": 2193, \"inode\": 144115643493424903, \"mtime_ns\": 1792089023000000000, \"ctime_ns\": 1792089023000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/contracts.txt\", \"bytes\": 27318, \"inode\": 144115643493420123, \"mtime_ns\": 1792089023000000000, \"ctime_ns\": 1792089023000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/source_snapshot.json\", \"bytes\": 15984, \"inode\": 144115643493424904, \"mtime_ns\": 1792089023000000000, \"ctime_ns\": 1792089023000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"conditional_CORE_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python\", \"bytes\": 10, \"inode\": 144115618512131424, \"mtime_ns\": 1790940371000000000, \"ctime_ns\": 1790940371000000000, \"mode\": 41471, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\", \"bytes\": 25916456, \"inode\": 144115618512129393, \"mtime_ns\": 1790940364000000000, \"ctime_ns\": 1790940383000000000, \"mode\": 33277, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"source_software_terminal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_inventory_history_software16997_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 2497247, \"inode\": 144115643443092202, \"mtime_ns\": 1792089517000000000, \"ctime_ns\": 1792089517000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"source_software_terminal_receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_inventory_history_software16997_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 2497247, \"sha256\": \"951cd49a206cb3b83d9941298f839f6d3dd243e8c378e68b7a36deb68c375071\"}, \"software_outer_proof\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_inventory_history_software_outer_16997/execution_control.json\", \"bytes\": 42221, \"sha256\": \"5d3b59f5537bbb2cdfe47f3922fb228e31b971eb7a3c76d8b0b0766a4a02a207\"}, \"software_outer_proof_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_inventory_history_software_outer_16997/execution_control.json\", \"bytes\": 42221, \"inode\": 144115643493424906, \"mtime_ns\": 1792089024000000000, \"ctime_ns\": 1792089024000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"wrapper_capture\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/root_wrapper_shell_byte_preservation_16998/capture.json\", \"bytes\": 32138, \"sha256\": \"a665124984b928dbf7525d2d90059ed6dccccdaa2e80605ddc2f789ba4cf6325\"}, \"wrapper_capture_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/root_wrapper_shell_byte_preservation_16998/capture.json\", \"bytes\": 32138, \"inode\": 144115643493424923, \"mtime_ns\": 1792091207000000000, \"ctime_ns\": 1792091207000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"wrapper_terminal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_wrapper_shell_source16998_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 2529798, \"inode\": 144115643443092221, \"mtime_ns\": 1792091667000000000, \"ctime_ns\": 1792091667000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"plan_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16997_16998_v7/final_source_plan.json\", \"bytes\": 1972684, \"inode\": 144115643443092223, \"mtime_ns\": 1792091925000000000, \"ctime_ns\": 1792092303000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16997_16998_v7/HANDOFF.md\", \"bytes\": 36650, \"inode\": 144115643443092224, \"mtime_ns\": 1792091925000000000, \"ctime_ns\": 1792092303000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"plan_directory_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16997_16998_v7\", \"bytes\": 4096, \"inode\": 144115643443092222, \"mtime_ns\": 1792091925000000000, \"ctime_ns\": 1792092303000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"plan_readonly_seal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v7_from16997_16998_metadata_readonly_seal/receipt.json\", \"bytes\": 2522020, \"inode\": 144115643443092226, \"mtime_ns\": 1792092304000000000, \"ctime_ns\": 1792092304000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"prior_qualified_plan_and_handoff\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16651_16847_v6/final_source_plan.json\", \"bytes\": 1945102, \"sha256\": \"47edaaf8defff84762a7995621b2b308dc507837212f97ba5dfeb4ef6f6d8306\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16651_16847_v6/HANDOFF.md\", \"bytes\": 16769, \"sha256\": \"13d0f9659e9270c708e620535534251e4fab0ad77fa7b13dbbedc978ad95f5cf\"}], \"prior_qualified_plan_and_handoff_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16651_16847_v6/final_source_plan.json\", \"bytes\": 1945102, \"inode\": 144115643443091707, \"mtime_ns\": 1792081415000000000, \"ctime_ns\": 1792081774000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16651_16847_v6/HANDOFF.md\", \"bytes\": 16769, \"inode\": 144115643443091708, \"mtime_ns\": 1792081415000000000, \"ctime_ns\": 1792081774000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"prior_v6_ownsha_capture\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v6_ownsha_16888/capture.json\", \"bytes\": 63237, \"sha256\": \"2f81c4917d6ace34e21edf3374d3425488fa9c9194c18b8fc8c73b8b52d59ebd\"}, \"prior_v6_ownsha_capture_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v6_ownsha_16888/capture.json\", \"bytes\": 63237, \"inode\": 144115643493406052, \"mtime_ns\": 1792082102000000000, \"ctime_ns\": 1792082102000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"current_canonical_Source4\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\", \"bytes\": 2225, \"sha256\": \"d602956154fb396fd14d7737c360d7d35144b4e6ca6c3d1c51eb6dc401e42615\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\", \"bytes\": 24234, \"sha256\": \"c8fe4495439826f0882b4c43952926e5de5361f88460320cc117d003352ff345\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\", \"bytes\": 1633, \"sha256\": \"2d40850d19c7835d658e7154e5a1cb53ae763e31d360b41eec253397f2c5befb\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\", \"bytes\": 6148, \"sha256\": \"c83e427f73ff1545253d64dbb165c7e60328bb698721d1e03663e6ea7d7c403f\"}], \"current_canonical_Source4_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\", \"bytes\": 2225, \"inode\": 144115543165691905, \"mtime_ns\": 1791727539000000000, \"ctime_ns\": 1791727539000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\", \"bytes\": 24234, \"inode\": 144115543165691892, \"mtime_ns\": 1791727495000000000, \"ctime_ns\": 1791727495000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\", \"bytes\": 1633, \"inode\": 144115543165691947, \"mtime_ns\": 1791727539000000000, \"ctime_ns\": 1791727539000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\", \"bytes\": 6148, \"inode\": 144115543165691893, \"mtime_ns\": 1791727495000000000, \"ctime_ns\": 1791727495000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"root_control_human\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V7_OWN_SHA_FROM16997_WRAPPERS16998_20261015_REV3.md\", \"primary_wrap\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v7_ownsha_from16997_16998_primary_claim/wrap.sh\"}")
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
need(rec(REAL)==corepin and md(REAL)==core[1],"Actual conditional CORE own bytes required")
sourcepins=SPEC["qualified_original_source6"]+SPEC["qualified_frozen_source6"]
source_meta=SPEC["qualified_source12_metadata"]
need(len(sourcepins)==len(source_meta)==12,"Qualified Source12 literal required")
for pin,meta in zip(sourcepins,source_meta):ro(pin["path"],pin,meta)
source_dirs=[SPEC["qualified_original_source_directory"],SPEC["qualified_frozen_source_directory"]]
for x in source_dirs:
 need(md(authority(x["path"]))==x and stat.S_IMODE(x["mode"])==0o555 and{p.name for p in Path(x["path"]).iterdir()}=={Path(v["path"]).name for v in SPEC["qualified_frozen_source6"]},"Exact source6 directory metadata/universe required")
for pin,meta in zip(SPEC["qualified_software_controls"],SPEC["qualified_software_control_metadata"]):ro(pin["path"],pin,meta)
a=read(SPEC["qualified_source_software"]["path"]);ct=read(SPEC["qualified_software_controls"][1]["path"])
need(a["source_files"]==SPEC["qualified_frozen_source6"]and a["original_executing_sources"]==SPEC["qualified_original_source6"]and a["allocation"]["job_id"]=="16997","Actual software16997 Source6 bindings required")
terminalpath=Path(SPEC["source_software_terminal_metadata"]["path"])
terminalpin,terminalmeta=ro(terminalpath,SPEC["source_software_terminal_receipt"],SPEC["source_software_terminal_metadata"])
terminal=read(terminalpath)
need(terminal["actual_job_id"]=="16997"and terminal["Root_plus_two_whole_actual_content_READBACK_PASS"]is True and terminal["mandatory158_unique_allPASS_old122_preserved_new36"]is True,"Actual accepted16997 terminal software context required")
# No Source import occurs before all qualified six-byte identities and current CPU readiness.
entry=Path(SPEC["qualified_frozen_source6"][0]["path"])
ss=importlib.util.spec_from_file_location("root_qualified_source16997_wrapper_preservation",entry)
g=importlib.util.module_from_spec(ss);ss.loader.exec_module(g)
need(g.software_shape(a,ct)==SPEC["qualified_frozen_source6"],"Unchanged qualified Source software shape required")
allocation=g.cpu();runtime=g.conditional_core_runtime()
need(allocation["job_id"]==jid and allocation["allocated_CPUs"]==1 and allocation["allocated_gpus"]==0 and allocation["numeric_sacct_row"]==attempts[selected-1]["actual_row"]and runtime==a["conditional_core_runtime"],"Actual fresh Source current CPU/Core required")
snapshot=read(SPEC["qualified_software_controls"][3]["path"])
need(g.software_snapshot_shape(a,snapshot)==snapshot,"Actual qualified software six snapshot required")
outerpin,outermeta=ro(SPEC["software_outer_proof"]["path"],SPEC["software_outer_proof"],SPEC["software_outer_proof_metadata"])
outer=read(outerpin["path"]);fixed=outer["fixed_control_receipts"]
wrapperpin,wrappermeta=ro(SPEC["wrapper_capture"]["path"],SPEC["wrapper_capture"],SPEC["wrapper_capture_metadata"])
wrapper=read(wrapperpin["path"])
wrappertermpin,wrappertermmeta=ro(SPEC["wrapper_terminal_metadata"]["path"],metadata=SPEC["wrapper_terminal_metadata"])
wrapperterm=read(wrappertermpin["path"])
need(wrapper["actual_job_id"]=="16998"and wrapper["status"]=="ACTUAL_TWO_WRAPPER_BYTES_AND_OWN_OPERATIONAL_SHELL_SOURCE_CPU_PRESERVED_NOT_EXECUTED"and wrapper["qualified_Source_software"]==SPEC["qualified_source_software"],"Actual qualified wrapper16998 capture required")
need(wrapperterm["actual_job_id"]=="16998"and wrapperterm["Root_plus_two_whole_actual_content_READBACK_PASS"]is True and wrapperterm["actual_CPU_final_descriptor"]["capture"]==wrapperpin and wrapperterm["fresh_terminal"]["returncode"]==0 and wrapperterm["fresh_terminal"]["raw_stderr"]==""and wrapperterm["fresh_terminal"]["numeric_9column_row"]==["16998","COMPLETED","0:0","9","1","test9_root_wrapper_shell_source_cpu","u21111210118","u21111210118","organ"],"Actual full16998 CPU successful terminal/Root two readback required")
need(wrapperterm["actual_CPU_final_descriptor"]["actual_five_Source_DOC_candidates"]==wrapper["actual_five_Source_DOC_candidates"]and wrapperterm["actual_CPU_final_descriptor"]["actual_five_Source_DOC_rows"]==wrapper["actual_five_Source_DOC_rows"],"Qualified same five Source/DOC leaves and destinations required")
need(len(fixed)==22 and outer["status"]=="ROOT_ACTUAL_NEW_SOURCE_SOFTWARE_AND_OWN_CONTROLS_READBACK_PASS_NOT_SOURCE_AUDIT_OR_SCIENCE","Qualified actual16997 own22 controls required")
additional=SPEC["qualified_original_source6"]+SPEC["qualified_frozen_source6"]+fixed[16:22]+fixed[0:8]+[fixed[13],fixed[14]]+wrapper["actual_five_Source_DOC_candidates"]
need(len(additional)==33,"Exactly thirty-three already CPU-qualified additional Source/DOC leaves required")
destinations=["delivery_tools/source_closure_inventory_history_leaf1_rev1/original/"+Path(x["path"]).name for x in additional[:6]]
destinations+=["delivery_tools/source_closure_inventory_history_leaf1_rev1/software_16997/"+Path(x["path"]).name for x in additional[6:12]]
destinations+=["delivery_tools/source_closure_inventory_history_leaf1_initial/"+Path(x["path"]).name for x in additional[12:18]]
destinations+=["delivery_tools/human_history/"+Path(x["path"]).name for x in additional[18:26]]
destinations+=["delivery_tools/root_operational_programs/"+Path(x["path"]).parent.name+"/wrap.sh"for x in additional[26:28]]
destinations+=[x["repository_relative"]for x in wrapper["actual_five_Source_DOC_rows"]]
additionalrows=[dict(receipt=r,repository_relative=d)for r,d in zip(additional,destinations)]
need(len(destinations)==len(set(destinations))==33,"Thirty-three distinct repository destinations required")
additionalmeta=[ro(r["path"],r)[1]for r in additional]
planmeta=SPEC["plan_metadata"];planpin,planbefore=ro(planmeta[0]["path"],metadata=planmeta[0]);handoffpin,handoffbefore=ro(planmeta[1]["path"],metadata=planmeta[1])
PLAN=Path(planpin["path"]);HANDOFF=Path(handoffpin["path"]);PLANRO=Path(SPEC["plan_readonly_seal_metadata"]["path"])
planro_pin,planro_meta=ro(PLANRO,metadata=SPEC["plan_readonly_seal_metadata"]);planro=read(PLANRO)
need(planro["schema"]=="root-new-plan-v7-metadata-readonly-seal.v1"and planro["Root_and_two_independent_whole_Plan_and_HANDOFF_static_PASS"]is True and planro["after_files"]==planmeta and planro["after_directory"]==SPEC["plan_directory_metadata"],"Actual whole reviewed new Plan2 readonly seal required")
need(md(authority(PLAN.parent))==SPEC["plan_directory_metadata"]and stat.S_IMODE(SPEC["plan_directory_metadata"]["mode"])==0o555 and{p.name for p in PLAN.parent.iterdir()}=={"final_source_plan.json","HANDOFF.md"},"Exact readonly Plan2 directory required")
priorpins=SPEC["prior_qualified_plan_and_handoff"]
for r,m in zip(priorpins,SPEC["prior_qualified_plan_and_handoff_metadata"]):ro(r["path"],r,m)
priorcap_pin,priorcap_meta=ro(SPEC["prior_v6_ownsha_capture"]["path"],SPEC["prior_v6_ownsha_capture"],SPEC["prior_v6_ownsha_capture_metadata"])
priorcap=read(priorcap_pin["path"])
need(priorcap["actual_job_id"]=="16888"and[priorcap["plan"],priorcap["handoff"]]==priorpins,"Actual earlier16888 ownPlan2 CPU tuples required, not a newPlan tuple")
canonical=SPEC["current_canonical_Source4"];canonicalmeta=SPEC["current_canonical_Source4_metadata"]
need(priorcap["current_canonical_Source4_receipts"]==canonical and priorcap["current_canonical_Source4_metadata_after"]==canonicalmeta and len(canonical)==len(canonicalmeta)==4,"Exact current canonicalSource4 required")
def canonical_end():
 for r,m in zip(canonical,canonicalmeta):
  p=authority(r["path"]);before=md(p)
  need(before==m and stat.S_ISREG(before["mode"])and stat.S_IMODE(before["mode"])==0o664 and before["nlink"]==1,"Only four literal current mutable source leaves permitted")
  need(g.rec(p)==r and md(p)==m,"Actual current canonicalSource4 ownbytes/fullmetadata differ")
canonical_end()
plan=read(PLAN);old=read(priorpins[0]["path"])
roles=["formal13260_terminal_v3","native74_cache_catalog","native74_cache_binding","reference_free_e2e","formal_common_review","independent_statistics","scientific_report","final_delivery_tools","default_workflow_integration"]
need(len(plan)==len(old)==34 and list(plan)==list(old)and plan["schema"]=="final-source-closure-plan.v3"and plan["library_software_acceptance"]==SPEC["qualified_source_software"]and[m["role"]for m in plan["modules"]]==roles,"Same34 keys/order/exactnine roles/current16997 software required")
need(plan["modules"][7]["sources"][-33:]==additionalrows and plan["modules"][7]["seeds"][-37:]==additional+SPEC["qualified_software_controls"],"Exact new Source33 and safeSeed37 ordered tails required")
need(len(plan["context_parent_seeds"])==17 and plan["context_parent_seeds"]==old["context_parent_seeds"]and len(plan["aliases"])==7 and plan["aliases"]==old["aliases"],"Exact ordered17 parents and seven aliases unchanged")
rewound=json.loads(json.dumps(plan,allow_nan=False));rewound["library_software_acceptance"]=old["library_software_acceptance"];rewound["modules"][7]["sources"]=rewound["modules"][7]["sources"][:-33];rewound["modules"][7]["seeds"]=rewound["modules"][7]["seeds"][:-37]
def same(x,y):
 need(type(x)is type(y),"Preserved Plan value type changed")
 if type(x)is dict:
  need(list(x)==list(y),"Preserved Plan key order changed")
  for k in x:same(x[k],y[k])
 elif type(x)is list:
  need(len(x)==len(y),"Preserved Plan list length changed")
  for a,b in zip(x,y):same(a,b)
 else:need(x==y,"Preserved Plan scalar changed")
same(rewound,old)
need((json.dumps(rewound,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode()==Path(priorpins[0]["path"]).read_bytes(),"Whole serialized V6 bytes must be recoverable exactly")
def identity(r):g.receipt_shape(r);return(r["path"],r["bytes"],r["sha256"])
allsources=[r for m in plan["modules"]for r in m["sources"]];allseeds=[r for m in plan["modules"]for r in m["seeds"]]
need(len(allsources)==673 and len({r["repository_relative"]for r in allsources})==612 and len(allseeds)==3846 and len({identity(r)for r in allseeds})==3773 and len(plan["modules"][7]["sources"])==474 and len(plan["modules"][7]["seeds"])==3700,"Exact finite new Plan673/612/3846/3773/final474/3700 counts required")
need(not set(destinations)&{r["repository_relative"]for m in old["modules"]for r in m["sources"]},"New33 destinations collide with old Source destinations")
need(g.module_plan(plan)==plan["modules"],"Qualified module_plan pure-shape validation required, no receipt child IO")
need(planpin["bytes"]==1972684 and planpin["bytes"]<2097152 and handoffpin["bytes"]==36650,"Exact reviewed Plan/Handoff byte sizes required")
ownhuman,ownhumanmeta=ro(SPEC["root_control_human"]);ownwrap,ownwrapmeta=ro(SPEC["primary_wrap"])
humantext=Path(ownhuman["path"]).read_text("utf-8");wraptext=Path(ownwrap["path"]).read_text("utf-8")
need(humantext.count("```python\n")==1 and wraptext.endswith("\nPY\n")and wraptext.partition("<<'PY'\n")[2][:-4].rstrip("\n")==humantext.split("```python\n",1)[1].split("\n```",1)[0].rstrip("\n"),"Actual precreated primary shell must bind whole reviewed Human")
readiness=read(D/"readiness.json")
readyvalues=[ro(D/"readiness.json")]
for cmd in[readiness["current_scontrol_observation"]]+readiness["attempts"]:
 for key in["raw_stdout","raw_stderr"]:readyvalues.append(ro(cmd[key]["path"]))
controls=[(planpin,planbefore),(handoffpin,handoffbefore),(ownhuman,ownhumanmeta),(ownwrap,ownwrapmeta),(planro_pin,planro_meta),(wrapperpin,wrappermeta),(wrappertermpin,wrappertermmeta),(outerpin,outermeta),(terminalpin,terminalmeta),(priorcap_pin,priorcap_meta)]
controls +=[(r,m)for r,m in zip(priorpins,SPEC["prior_qualified_plan_and_handoff_metadata"])]
need(len(controls)==len({r["path"]for r,m in controls})==12,"Twelve finite own control/SourceDoc files required")
need([g.rec(r["path"])for r,m in controls]==[r for r,m in controls]and[md(authority(r["path"]))for r,m in controls]==[m for r,m in controls],"Qualified G16997.rec must independently reproduce all twelve actual own tuples including new Plan and Handoff with full metadata stable after the qualified reads")
protected=planro["protected_inputs_after"]+planro["protected_directories_after"]
need(planro["protected_inputs_before"]==planro["protected_inputs_after"]and planro["protected_directories_before"]==planro["protected_directories_after"],"Exact readonly PlanRO protected metadata required")
def inputs_end():
 need(md(CORE)==core[0]and md(REAL)==core[1]and rec(REAL)==corepin and md(REAL)==core[1]and os.readlink(CORE)=="python3.11","Conditional CORE ownbytes/stablemetadata drift")
 for r,m in zip(sourcepins,source_meta):ro(r["path"],r,m)
 for x in source_dirs:need(md(authority(x["path"]))==x and{p.name for p in Path(x["path"]).iterdir()}=={Path(v["path"]).name for v in SPEC["qualified_frozen_source6"]},"Qualified Source6 directory drift")
 for r,m in zip(SPEC["qualified_software_controls"],SPEC["qualified_software_control_metadata"]):ro(r["path"],r,m)
 for r,m in controls+readyvalues:ro(r["path"],r,m)
 need([g.rec(r["path"])for r,m in controls]==[r for r,m in controls]and[md(authority(r["path"]))for r,m in controls]==[m for r,m in controls],"Qualified G16997.rec final own-control tuple or post-read metadata drift")
 for r,m in zip(additional,additionalmeta):ro(r["path"],r,m)
 for x in protected:need(md(authority(x["path"]))==x,"Finite protected metadata drift")
 need(md(authority(PLAN.parent))==SPEC["plan_directory_metadata"]and{p.name for p in PLAN.parent.iterdir()}=={"final_source_plan.json","HANDOFF.md"},"Plan2 directory drift")
 canonical_end();need(g.conditional_core_runtime()==runtime,"Current approved conditional interpreter differs")
inputs_end()
OUT=authority(S/"runs")/("final_source_plan_v7_ownsha_"+jid)
need(not OUT.exists()and not OUT.is_symlink(),"Exclusive absent new PlanV7 own-SHA output required")
OUT.mkdir(mode=0o755)
phase="own_new_PlanV7_and_twelve_controls_no_receipt_child_IO"
try:
 out=dict(schema="root-fixed-source-plan-v7-own-sha-control-capture.v1",status="ACTUAL_NEW_PLAN_V7_OWN_SHA_AND33_PINNED_SOURCE_DOC_ADDITIONS_CPU_VERIFIED_NOT_SOURCE_AUDIT_ACCEPTANCE",actual_job_id=jid,allocation=allocation,current_actual_readiness=readiness,current_readiness_own_CPU_receipts=[x[0]for x in readyvalues],plan=planpin,handoff=handoffpin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,control_receipts=[r for r,m in controls],control_metadata_before=[m for r,m in controls],control_metadata_after=[md(r["path"])for r,m in controls],software_acceptance=SPEC["qualified_source_software"],software_control_receipts=SPEC["qualified_software_controls"],software_control_metadata_before=SPEC["qualified_software_control_metadata"],software_control_metadata_after=[md(r["path"])for r in SPEC["qualified_software_controls"]],source_files=SPEC["qualified_frozen_source6"],original_executing_sources=SPEC["qualified_original_source6"],qualified_source12_metadata=source_meta,conditional_core_runtime=runtime,qualified_wrapper16998_capture=wrapperpin,qualified_wrapper16998_terminal_own_CPU_receipt=wrappertermpin,qualified_software16997_terminal_own_CPU_receipt=terminalpin,prior_qualified_PlanV6_and_Handoff=priorpins,additional_33_Source_rows=additionalrows,additional_33_Source_metadata=additionalmeta,additional_37_safe_seed_receipts=additional+SPEC["qualified_software_controls"],current_canonical_Source4_receipts=canonical,current_canonical_Source4_metadata_before=canonicalmeta,current_canonical_Source4_metadata_after=[md(r["path"])for r in canonical],plan_directory_metadata_before=SPEC["plan_directory_metadata"],plan_directory_metadata_after=md(PLAN.parent),Source_n=673,destination_n=612,seed_n=3846,unique_seed_n=3773,role_n=9,parent_n=17,ordered_alias_n=7,all34keys_type_order_and_original_V6_serialized_bytes_rewind_PASS=True,qualified_module_plan_pure_shape_PASS=True,qualified_G16997_rec_all12_controls_pre_end_PASS=True,all_Source12_SW4_Core_controls12_Source33_canonical4_protected_pre_end_afteroutput_finalreadonly_PASS=True,plan_child_receipts_shape_only_no_child_IO=True,source_audit_executed=False,source_staged=False,published=False,ACTIVE_changed=False,compiler_or_tests_or_new_software_qualification_executed=False,scientific_receipt_children_read_or_hashed=False,historical_Slurm_queried=False,own_created_controls_LATE_COMPOSER_ONLY_NOT_PLAN_PREREQUISITES=True)
 raw=(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode();path=OUT/"capture.json"
 with path.open("xb")as f:f.write(raw);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444);os.fsync(f.fileno())
 descriptor=g.rec(path);outmeta=md(path)
 need(path.read_bytes()==raw and read(path)==out and stat.S_IMODE(outmeta["mode"])==0o444 and outmeta["nlink"]==1,"Whole exclusive own capture readonly reread required")
 inputs_end();OUT.chmod(0o555)
 fd=os.open(str(OUT),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
 outdir=md(authority(OUT))
 need(stat.S_IMODE(outdir["mode"])==0o555 and outdir["nlink"]==2 and{p.name for p in OUT.iterdir()}=={"capture.json"}and path.read_bytes()==raw and read(path)==out and g.rec(path)==descriptor and md(path)==outmeta,"Final readonly own capture directory/fullbytes required")
 inputs_end();need(md(authority(OUT))==outdir and md(path)==outmeta,"Final output fullmetadata after all input checks required")
 print(json.dumps(dict(status=out["status"],capture=descriptor,plan=planpin,handoff=handoffpin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,qualified_wrapper16998_terminal_own_CPU_receipt=wrappertermpin,Source_n=673,destination_n=612,seed_n=3846,unique_seed_n=3773,role_n=9,parent_n=17,final_output_directory_metadata=outdir,Plan_own_SHA_qualified_only_AFTER_fresh_terminal_RO_Root_and_independent_content_readback=True),sort_keys=True),flush=True)
except BaseException as e:
 try:
  failure=(json.dumps(dict(status="ACTUAL_PLAN_V7_OWN_SHA_UNQUALIFIED",actual_job_id=jid,phase=phase,reason_type=type(e).__name__,reason=str(e),source_staged=False,published=False,ACTIVE_changed=False),indent=2)+"\n").encode()
  with(OUT/"typed_incomplete.json").open("xb")as f:f.write(failure);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 except Exception as se:print("Readonly failure output best-effort: "+repr(se),file=sys.stderr,flush=True)
 raise
PY
