set -eu
umask 022
cd /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
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
D = S / "submissions" / ("source_plan_v11_ownsha_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_source_plan_v11_ownsha_cpu", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:10:00", "MinMemoryNode": "8G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/8G10/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-plan-v11-ownsha-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_PLAN_V11_OWN_SHA_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_PLAN_V11_OWN_SHA_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_PLAN_V11_OWN_SHA_NOT_EXECUTED"
obj = {"schema": "root-current-owned-plan-v11-ownsha-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
SPEC = json.loads("{\"qualified_source_software\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/acceptance.json\",\"bytes\":6693,\"sha256\":\"17652a5db832fb36d7df97ebe8279a0de8484041cb3aa91fb0f759ec4d64e4cb\"},\"qualified_original_source6\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_closure.py\",\"bytes\":300159,\"sha256\":\"74cd7b71abdf1202433ca3fbab7f180144926fbaa74916f81535c58bb3afb207\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/test_final_source_closure.py\",\"bytes\":294055,\"sha256\":\"b93f68140e6f0753c3d7f576cd1b108f8e0ab3c95881611ebb9b863d089d8da3\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_cpu.sbatch\",\"bytes\":1679,\"sha256\":\"c46298252a096f2727c749a8362dc55396ef730896336609a5431c37434a61cb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/HANDOFF.md\",\"bytes\":28119,\"sha256\":\"cf361787a35b00ff40ca63abb3910f873dadc7acfcd8100cd81b8b7fbdbdb968\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5269,\"sha256\":\"a363d0202d237c0d35ea5a8e3fb7d6deabdca27bb72916ee56b66b854b9b1da2\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_context_adapter.py\",\"bytes\":19697,\"sha256\":\"fc1caf2e408e95a77026e72f27fab2e2fe2c20e2c07da61888f5fd2dd14f64b6\"}],\"qualified_frozen_source6\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_closure.py\",\"bytes\":300159,\"sha256\":\"74cd7b71abdf1202433ca3fbab7f180144926fbaa74916f81535c58bb3afb207\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/test_final_source_closure.py\",\"bytes\":294055,\"sha256\":\"b93f68140e6f0753c3d7f576cd1b108f8e0ab3c95881611ebb9b863d089d8da3\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_cpu.sbatch\",\"bytes\":1679,\"sha256\":\"c46298252a096f2727c749a8362dc55396ef730896336609a5431c37434a61cb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/HANDOFF.md\",\"bytes\":28119,\"sha256\":\"cf361787a35b00ff40ca63abb3910f873dadc7acfcd8100cd81b8b7fbdbdb968\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5269,\"sha256\":\"a363d0202d237c0d35ea5a8e3fb7d6deabdca27bb72916ee56b66b854b9b1da2\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_context_adapter.py\",\"bytes\":19697,\"sha256\":\"fc1caf2e408e95a77026e72f27fab2e2fe2c20e2c07da61888f5fd2dd14f64b6\"}],\"qualified_source12_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_closure.py\",\"bytes\":300159,\"inode\":144115643443092649,\"mtime_ns\":1792120232000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/test_final_source_closure.py\",\"bytes\":294055,\"inode\":144115643443092650,\"mtime_ns\":1792120659000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_cpu.sbatch\",\"bytes\":1679,\"inode\":144115643443092651,\"mtime_ns\":1792117466000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/HANDOFF.md\",\"bytes\":28119,\"inode\":144115643443092652,\"mtime_ns\":1792120659000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5269,\"inode\":144115643443092653,\"mtime_ns\":1792120232000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_context_adapter.py\",\"bytes\":19697,\"inode\":144115643443092654,\"mtime_ns\":1792120010000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_closure.py\",\"bytes\":300159,\"inode\":144115643493459570,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/test_final_source_closure.py\",\"bytes\":294055,\"inode\":144115643493459571,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_cpu.sbatch\",\"bytes\":1679,\"inode\":144115643493459572,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/HANDOFF.md\",\"bytes\":28119,\"inode\":144115643493459573,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5269,\"inode\":144115643493459574,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_context_adapter.py\",\"bytes\":19697,\"inode\":144115643493459575,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"qualified_original_source_directory\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1\",\"bytes\":4096,\"inode\":144115643443092648,\"mtime_ns\":1792117363000000000,\"ctime_ns\":1792121074000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"qualified_frozen_source_directory\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner\",\"bytes\":4096,\"inode\":144115643493459569,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"qualified_software_controls\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/acceptance.json\",\"bytes\":6693,\"sha256\":\"17652a5db832fb36d7df97ebe8279a0de8484041cb3aa91fb0f759ec4d64e4cb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/contracts.json\",\"bytes\":2214,\"sha256\":\"238e578ec3dc30134a290b5ae3f8c626b5fa423055debf598d36dd0aca230e1a\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/contracts.txt\",\"bytes\":57823,\"sha256\":\"a48daf4898c227e63a16d0d9114df72f699f6bfb4493c21052f993e1ddec2e0c\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/source_snapshot.json\",\"bytes\":16095,\"sha256\":\"5e9b4ce1c164f0dbb22ba1152b22a5db0415ecbd23268faeeb80f9697e8f46ae\"}],\"qualified_software_control_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/acceptance.json\",\"bytes\":6693,\"inode\":144115643493469239,\"mtime_ns\":1792122343000000000,\"ctime_ns\":1792122343000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/contracts.json\",\"bytes\":2214,\"inode\":144115643493469237,\"mtime_ns\":1792122343000000000,\"ctime_ns\":1792122343000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/contracts.txt\",\"bytes\":57823,\"inode\":144115643493459576,\"mtime_ns\":1792122343000000000,\"ctime_ns\":1792122343000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/source_snapshot.json\",\"bytes\":16095,\"inode\":144115643493469238,\"mtime_ns\":1792122343000000000,\"ctime_ns\":1792122343000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"conditional_CORE_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/env/core/bin/python\",\"bytes\":10,\"inode\":144115618512131424,\"mtime_ns\":1790940371000000000,\"ctime_ns\":1790940371000000000,\"mode\":41471,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\",\"bytes\":25916456,\"inode\":144115618512129393,\"mtime_ns\":1790940364000000000,\"ctime_ns\":1790940383000000000,\"mode\":33277,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"source_software_terminal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_parent_diagnostic_history_software17015_actual_terminal_metadata_seal/receipt.json\",\"bytes\":10037419,\"inode\":144115643443092690,\"mtime_ns\":1792122863000000000,\"ctime_ns\":1792122863000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"software_outer_proof\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_parent_diagnostic_history_software_outer_17015/execution_control.json\",\"bytes\":107479,\"sha256\":\"40962234a42b9c2fb4c8587d4823df4f61bdd97bf3b37ff536575fd9d0d20487\"},\"software_outer_proof_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_parent_diagnostic_history_software_outer_17015/execution_control.json\",\"bytes\":107479,\"inode\":144115643493469240,\"mtime_ns\":1792122346000000000,\"ctime_ns\":1792122346000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"source_readonly_seal\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_parent_diagnostic_history_leaf1_source_metadata_readonly_seal/receipt.json\",\"bytes\":9987404,\"sha256\":\"8fba1c66622783b36933507bd15add13535cc64a62d775416352560a9ecb83bb\"},\"source_readonly_seal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_parent_diagnostic_history_leaf1_source_metadata_readonly_seal/receipt.json\",\"bytes\":9987404,\"inode\":144115643443092656,\"mtime_ns\":1792121077000000000,\"ctime_ns\":1792121077000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"software_humans_readonly_seal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_source_parent_diagnostic_history_software_human_metadata_readonly_seal/receipt.json\",\"bytes\":9987246,\"inode\":144115643443092659,\"mtime_ns\":1792121985000000000,\"ctime_ns\":1792121985000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"plan_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17015_v11/final_source_plan.json\",\"bytes\":2025808,\"inode\":144115643443092692,\"mtime_ns\":1792123307000000000,\"ctime_ns\":1792124063000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17015_v11/HANDOFF.md\",\"bytes\":25668,\"inode\":144115643443092693,\"mtime_ns\":1792123307000000000,\"ctime_ns\":1792124063000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"plan_directory_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17015_v11\",\"bytes\":4096,\"inode\":144115643443092691,\"mtime_ns\":1792123307000000000,\"ctime_ns\":1792124063000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"plan_readonly_seal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v11_from17015_metadata_readonly_seal/receipt.json\",\"bytes\":10039611,\"inode\":144115643443092695,\"mtime_ns\":1792124065000000000,\"ctime_ns\":1792124065000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"prior_qualified_plan_and_handoff\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17009_v10/final_source_plan.json\",\"bytes\":2010925,\"sha256\":\"c38b714cac8461176a1abd44e37862766a25a5a6f912d68d874bbf9bdbebe898\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17009_v10/HANDOFF.md\",\"bytes\":30810,\"sha256\":\"71befb14f0be5ac961687323feb8f29c142407d097e66c7594ad4853054d4ad3\"}],\"prior_qualified_plan_and_handoff_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17009_v10/final_source_plan.json\",\"bytes\":2010925,\"inode\":144115643443092558,\"mtime_ns\":1792111380000000000,\"ctime_ns\":1792111647000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17009_v10/HANDOFF.md\",\"bytes\":30810,\"inode\":144115643443092559,\"mtime_ns\":1792111380000000000,\"ctime_ns\":1792111647000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"current_canonical_Source4\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\",\"bytes\":2225,\"sha256\":\"d602956154fb396fd14d7737c360d7d35144b4e6ca6c3d1c51eb6dc401e42615\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\",\"bytes\":24234,\"sha256\":\"c8fe4495439826f0882b4c43952926e5de5361f88460320cc117d003352ff345\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\",\"bytes\":1633,\"sha256\":\"2d40850d19c7835d658e7154e5a1cb53ae763e31d360b41eec253397f2c5befb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\",\"bytes\":6148,\"sha256\":\"c83e427f73ff1545253d64dbb165c7e60328bb698721d1e03663e6ea7d7c403f\"}],\"current_canonical_Source4_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\",\"bytes\":2225,\"inode\":144115543165691905,\"mtime_ns\":1791727539000000000,\"ctime_ns\":1791727539000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\",\"bytes\":24234,\"inode\":144115543165691892,\"mtime_ns\":1791727495000000000,\"ctime_ns\":1791727495000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\",\"bytes\":1633,\"inode\":144115543165691947,\"mtime_ns\":1791727539000000000,\"ctime_ns\":1791727539000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\",\"bytes\":6148,\"inode\":144115543165691893,\"mtime_ns\":1791727495000000000,\"ctime_ns\":1791727495000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"root_control_human\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V11_OWN_SHA_FROM17015_20261016_REV1.md\",\"primary_wrap\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v11_ownsha_from17015_primary_claim/wrap.sh\",\"actual_additional_14_Source_rows\":[{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_closure.py\",\"bytes\":300159,\"sha256\":\"74cd7b71abdf1202433ca3fbab7f180144926fbaa74916f81535c58bb3afb207\"},\"repository_relative\":\"delivery_tools/source_closure_parent_diagnostic_history_leaf1/original/final_source_closure.py\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/test_final_source_closure.py\",\"bytes\":294055,\"sha256\":\"b93f68140e6f0753c3d7f576cd1b108f8e0ab3c95881611ebb9b863d089d8da3\"},\"repository_relative\":\"delivery_tools/source_closure_parent_diagnostic_history_leaf1/original/test_final_source_closure.py\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_cpu.sbatch\",\"bytes\":1679,\"sha256\":\"c46298252a096f2727c749a8362dc55396ef730896336609a5431c37434a61cb\"},\"repository_relative\":\"delivery_tools/source_closure_parent_diagnostic_history_leaf1/original/final_source_cpu.sbatch\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/HANDOFF.md\",\"bytes\":28119,\"sha256\":\"cf361787a35b00ff40ca63abb3910f873dadc7acfcd8100cd81b8b7fbdbdb968\"},\"repository_relative\":\"delivery_tools/source_closure_parent_diagnostic_history_leaf1/original/HANDOFF.md\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5269,\"sha256\":\"a363d0202d237c0d35ea5a8e3fb7d6deabdca27bb72916ee56b66b854b9b1da2\"},\"repository_relative\":\"delivery_tools/source_closure_parent_diagnostic_history_leaf1/original/FINAL_SOURCE_CHECKLIST.md\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_context_adapter.py\",\"bytes\":19697,\"sha256\":\"fc1caf2e408e95a77026e72f27fab2e2fe2c20e2c07da61888f5fd2dd14f64b6\"},\"repository_relative\":\"delivery_tools/source_closure_parent_diagnostic_history_leaf1/original/final_source_context_adapter.py\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_closure.py\",\"bytes\":300159,\"sha256\":\"74cd7b71abdf1202433ca3fbab7f180144926fbaa74916f81535c58bb3afb207\"},\"repository_relative\":\"delivery_tools/source_closure_parent_diagnostic_history_leaf1/software_17015/final_source_closure.py\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/test_final_source_closure.py\",\"bytes\":294055,\"sha256\":\"b93f68140e6f0753c3d7f576cd1b108f8e0ab3c95881611ebb9b863d089d8da3\"},\"repository_relative\":\"delivery_tools/source_closure_parent_diagnostic_history_leaf1/software_17015/test_final_source_closure.py\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_cpu.sbatch\",\"bytes\":1679,\"sha256\":\"c46298252a096f2727c749a8362dc55396ef730896336609a5431c37434a61cb\"},\"repository_relative\":\"delivery_tools/source_closure_parent_diagnostic_history_leaf1/software_17015/final_source_cpu.sbatch\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/HANDOFF.md\",\"bytes\":28119,\"sha256\":\"cf361787a35b00ff40ca63abb3910f873dadc7acfcd8100cd81b8b7fbdbdb968\"},\"repository_relative\":\"delivery_tools/source_closure_parent_diagnostic_history_leaf1/software_17015/HANDOFF.md\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5269,\"sha256\":\"a363d0202d237c0d35ea5a8e3fb7d6deabdca27bb72916ee56b66b854b9b1da2\"},\"repository_relative\":\"delivery_tools/source_closure_parent_diagnostic_history_leaf1/software_17015/FINAL_SOURCE_CHECKLIST.md\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_context_adapter.py\",\"bytes\":19697,\"sha256\":\"fc1caf2e408e95a77026e72f27fab2e2fe2c20e2c07da61888f5fd2dd14f64b6\"},\"repository_relative\":\"delivery_tools/source_closure_parent_diagnostic_history_leaf1/software_17015/final_source_context_adapter.py\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PARENT_DIAGNOSTIC_HISTORY_SOURCE_SOFTWARE_FROM17012_20261016.md\",\"bytes\":84442,\"sha256\":\"8763f0a522f160ecf8a37018cdd8919cd95915465e22d375d8abee8f4bb5196e\"},\"repository_relative\":\"delivery_tools/human_history/ROOT_FIXED_PARENT_DIAGNOSTIC_HISTORY_SOURCE_SOFTWARE_FROM17012_20261016.md\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_parent_diagnostic_history_leaf1_software_primary_claim/wrap.sh\",\"bytes\":78212,\"sha256\":\"3a5fd9acd36dd0d19912604ad99daf2b4234573831104ad889115ea8aadb84c4\"},\"repository_relative\":\"delivery_tools/root_operational_programs/final_source_parent_diagnostic_history_leaf1_software_primary_claim/wrap.sh\"}],\"actual_additional_3_historical_Source_rows\":[{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/source_receipt_parent_diagnostic_v1/diagnostic.py\",\"bytes\":2787,\"sha256\":\"3e3263606831e4c35dd29ac40f043e1c44cb6b8db9ee01f2b5acf139fd9ba265\"},\"repository_relative\":\"delivery_tools/historical_parent_diagnostic13290/source_receipt_parent_diagnostic_v1/diagnostic.py\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/source_refresh_relative_v4_13279/code/source_delivery_refresh_v4.py\",\"bytes\":21113,\"sha256\":\"e3b6a5965dae04d95b470c124e4b39d6569a689ac1a4ff5e9775060b981ef794\"},\"repository_relative\":\"delivery_tools/historical_parent_diagnostic13290/sealed_v4_13279/source_delivery_refresh_v4.py\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/source_receipt_parent_diagnostic_v1/diagnostic_cpu.sbatch\",\"bytes\":918,\"sha256\":\"288f180f15ac112391581236c807b8a281073a81f6a51b5772214dac9da75bff\"},\"repository_relative\":\"delivery_tools/historical_parent_diagnostic13290/source_receipt_parent_diagnostic_v1/diagnostic_cpu.sbatch\"}],\"prior_v10_ownsha_capture\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v10_ownsha_17010/capture.json\",\"bytes\":62672,\"sha256\":\"2238eb3fbe6980a8699f910a2994348b6cc36dabdb2931dddd8bf3d4fb49fb9b\"},\"prior_v10_ownsha_capture_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v10_ownsha_17010/capture.json\",\"bytes\":62672,\"inode\":144115643493457377,\"mtime_ns\":1792112305000000000,\"ctime_ns\":1792112305000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}}")
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
need(a["source_files"]==SPEC["qualified_frozen_source6"]and a["original_executing_sources"]==SPEC["qualified_original_source6"]and a["allocation"]["job_id"]=="17015","Actual17015 original/frozen software bindings required")
terminalpin,terminalmeta=ro(SPEC["source_software_terminal_metadata"]["path"],metadata=SPEC["source_software_terminal_metadata"])
terminal=read(terminalpin["path"])
need(terminal["schema"]=="root-final-source-parent-diagnostic-history-software17015-terminal-metadata-seal.v1"and terminal["actual_job_id"]=="17015"and terminal["Root_plus_two_whole_actual_software284_content_READBACK_PASS"]is True and terminal["actual_unique_named_tests"]==284 and terminal["historical238_names_and_relative_order_preserved"]is True and terminal["new46_actual_parent_diagnostic_history_contracts_PASS"]is True and terminal["actual_GPU0_from_current_readiness"]is True,"Actual accepted284 terminal context required")
need([terminal[k]for k in ["actual_software_acceptance","actual_contracts","actual_contract_log","actual_source_snapshot"]]==SW and terminal["fresh_terminal"]["returncode"]==0 and terminal["fresh_terminal"]["raw_stderr"]==""and terminal["fresh_terminal"]["numeric_9column_row"]==["17015","COMPLETED","0:0","89","1","test9_final_source_parent_diagnostic_history_v3","u21111210118","u21111210118","organ"],"Exact qualified17015 SW4/fresh terminal required")
# Import only the actual qualified frozen source after all literal byte and metadata guards.
ss=importlib.util.spec_from_file_location("root_qualified_source17015_plan_v11_ownsha",Path(SPEC["qualified_frozen_source6"][0]["path"]))
g=importlib.util.module_from_spec(ss);ss.loader.exec_module(g)
need(g.software_shape(a,ct)==SPEC["qualified_frozen_source6"],"Qualified284 software shape required")
allocation=g.cpu();runtime=g.conditional_core_runtime()
need(allocation["job_id"]==jid and allocation["allocated_CPUs"]==1 and allocation["allocated_gpus"]==0 and allocation["numeric_sacct_row"]==attempts[selected-1]["actual_row"]and runtime==a["conditional_core_runtime"],"Fresh current CPU1/GPU0/Core required")
snapshot=read(SW[3]["path"]);need(g.software_snapshot_shape(a,snapshot)==snapshot,"Qualified software snapshot shape required")
outerpin,outermeta=ro(SPEC["software_outer_proof"]["path"],SPEC["software_outer_proof"],SPEC["software_outer_proof_metadata"])
outer=read(outerpin["path"]);fixed=outer["fixed_control_receipts"]
need(outer["actual_job_id"]=="17015"and outer["actual_unique_tests"]==284 and outer["historical238_names_and_relative_order_preserved"]is True and len(fixed)==100 and outer["status"]=="ROOT_ACTUAL_NEW_SOURCE_SOFTWARE_AND_OWN_CONTROLS_READBACK_PASS_NOT_SOURCE_AUDIT_OR_SCIENCE"and outer["actual_software_acceptance"]==SW[0]and outer["source_files"]==SPEC["qualified_frozen_source6"]and outer["original_executing_sources"]==SPEC["qualified_original_source6"],"Exact actual17015 outer controls required")
sourceROpin,sourceROmeta=ro(SPEC["source_readonly_seal"]["path"],SPEC["source_readonly_seal"],SPEC["source_readonly_seal_metadata"])
sourceRO=read(sourceROpin["path"])
need(sourceRO["source_directory_after"]==source_dirs[0]and sourceRO["source_files_after"]==source_meta[:6]and outer["source_readonly_seal"]==sourceROpin,"Actual SourceRO original6 identity required")
HROpin,HROmeta=ro(SPEC["software_humans_readonly_seal_metadata"]["path"],metadata=SPEC["software_humans_readonly_seal_metadata"])
HRO=read(HROpin["path"])
need(len(HRO)==22 and HRO["Root_and_two_whole_Human_static_PASS"]is True,"Actual software Human readonly seal shape required")
additional=sourcepins+fixed[98:100]
destinations=["delivery_tools/source_closure_parent_diagnostic_history_leaf1/original/"+Path(x["path"]).name for x in additional[:6]]
destinations+=["delivery_tools/source_closure_parent_diagnostic_history_leaf1/software_17015/"+Path(x["path"]).name for x in additional[6:12]]
destinations+=["delivery_tools/human_history/"+Path(x["path"]).name for x in additional[12:13]]
destinations+=["delivery_tools/root_operational_programs/"+Path(additional[13]["path"]).parent.name+"/wrap.sh"]
additionalrows=[dict(receipt=r,repository_relative=d)for r,d in zip(additional,destinations)]
need(len(additional)==len(destinations)==len(set(destinations))==14 and additionalrows==SPEC["actual_additional_14_Source_rows"],"Exact actual fourteen Source/DOC ordered rows required")
additionalmeta=[ro(r["path"],r)[1]for r in additional]
historical=outer["fixed_historical_IMPLEMENTATION_Source2_own_CPU_receipts"]+outer["supplementary_historical_launcher_SOURCE_own_CPU_receipts"]
historicalrows=SPEC["actual_additional_3_historical_Source_rows"]
historicalmeta=outer["fixed_historical_Source2_metadata_after"]+outer["supplementary_historical_launcher_SOURCE_metadata_after"]
need(len(historical)==len(historicalrows)==len(historicalmeta)==3 and [x["receipt"]for x in historicalrows]==historical,"Exact actual Source2 and launcher own CPU tuples required")
need([ro(r["path"],r,m)[1]for r,m in zip(historical,historicalmeta)]==historicalmeta,"New historical Source3 exact readonly ownbytes and full metadata required")
need(outer["fixed_historical_Source2_metadata_before"]==outer["fixed_historical_Source2_metadata_after"]and outer["supplementary_historical_launcher_SOURCE_metadata_before"]==outer["supplementary_historical_launcher_SOURCE_metadata_after"]and outer["historical_Source2_and_launcher_never_imported_compiled_or_executed"]is True,"Qualified historical Source2 and launcher preserved without execution")
historicaldest=[x["repository_relative"]for x in historicalrows]
need(Path(historicaldest[0]).parent==Path(historicaldest[2]).parent and Path(historicaldest[1]).parent!=Path(historicaldest[0]).parent,"Producer and launcher same exact package, sealed V4 distinct history folder required")
planmeta=SPEC["plan_metadata"]
planpin,planbefore=ro(planmeta[0]["path"],metadata=planmeta[0]);handoffpin,handoffbefore=ro(planmeta[1]["path"],metadata=planmeta[1])
PLAN=Path(planpin["path"]);HANDOFF=Path(handoffpin["path"])
planROpin,planROmeta=ro(SPEC["plan_readonly_seal_metadata"]["path"],metadata=SPEC["plan_readonly_seal_metadata"])
planRO=read(planROpin["path"])
need(planRO["schema"]=="root-new-plan-v11-metadata-readonly-seal.v1"and planRO["Root_and_two_independent_whole_Plan_and_HANDOFF_static_PASS"]is True and planRO["after_files"]==planmeta and planRO["after_directory"]==SPEC["plan_directory_metadata"],"Actual new reviewed Plan2 readonly seal required")
need(md(authority(PLAN.parent))==SPEC["plan_directory_metadata"]and stat.S_IMODE(SPEC["plan_directory_metadata"]["mode"])==0o555 and {p.name for p in PLAN.parent.iterdir()}=={"final_source_plan.json","HANDOFF.md"},"Exact readonly Plan2 directory required")
priorpins=SPEC["prior_qualified_plan_and_handoff"]
for r,m in zip(priorpins,SPEC["prior_qualified_plan_and_handoff_metadata"]):ro(r["path"],r,m)
priorCAPpin,priorCAPmeta=ro(SPEC["prior_v10_ownsha_capture"]["path"],SPEC["prior_v10_ownsha_capture"],SPEC["prior_v10_ownsha_capture_metadata"])
priorCAP=read(priorCAPpin["path"])
need(priorCAP["actual_job_id"]=="17010"and[priorCAP["plan"],priorCAP["handoff"]]==priorpins,"Actual prior17010 qualified V10 Plan/H tuples required")
canonical=SPEC["current_canonical_Source4"];canonicalmeta=SPEC["current_canonical_Source4_metadata"]
need(priorCAP["current_canonical_Source4_receipts"]==canonical and priorCAP["current_canonical_Source4_metadata_after"]==canonicalmeta and len(canonical)==len(canonicalmeta)==4,"Exact current canonicalSource4 bindings required")
def canonical_end():
 for r,m in zip(canonical,canonicalmeta):
  p=authority(r["path"]);need(md(p)==m and stat.S_ISREG(m["mode"])and stat.S_IMODE(m["mode"])==0o664 and m["nlink"]==1,"Only four literal current mutable Source leaves permitted")
  need(g.rec(p)==r and md(p)==m,"Current canonicalSource4 ownbytes/fullMD drift")
canonical_end()
plan=read(PLAN);old=read(priorpins[0]["path"])
roles=["formal13260_terminal_v3","native74_cache_catalog","native74_cache_binding","reference_free_e2e","formal_common_review","independent_statistics","scientific_report","final_delivery_tools","default_workflow_integration"]
need(len(plan)==len(old)==34 and list(plan)==list(old)and plan["schema"]=="final-source-closure-plan.v3"and plan["library_software_acceptance"]==SW[0]and[m["role"]for m in plan["modules"]]==roles,"Same34 keys/order/exactnine roles/current17015 software required")
need(plan["modules"][7]["sources"][-14:]==additionalrows and plan["modules"][7]["seeds"][-18:]==additional+SW and plan["modules"][8]["sources"][-3:]==historicalrows and plan["modules"][8]["seeds"][-3:]==historical,"Exact finaltools Source14 safeSeed18 plus default Source3 safeSeed3 ordered tails required")
need(len(plan["context_parent_seeds"])==17 and plan["context_parent_seeds"]==old["context_parent_seeds"]and len(plan["aliases"])==7 and plan["aliases"]==old["aliases"],"Exact ordered17 parents and seven aliases unchanged")
rewound=json.loads(json.dumps(plan,allow_nan=False));rewound["library_software_acceptance"]=old["library_software_acceptance"];rewound["modules"][7]["sources"]=rewound["modules"][7]["sources"][:-14];rewound["modules"][7]["seeds"]=rewound["modules"][7]["seeds"][:-18];rewound["modules"][8]["sources"]=rewound["modules"][8]["sources"][:-3];rewound["modules"][8]["seeds"]=rewound["modules"][8]["seeds"][:-3]
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
need((json.dumps(rewound,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode()==Path(priorpins[0]["path"]).read_bytes(),"Entire serialized raw V10 must rewind exactly")
def identity(r):g.receipt_shape(r);return(r["path"],r["bytes"],r["sha256"])
allsources=[r for m in plan["modules"]for r in m["sources"]];allseeds=[r for m in plan["modules"]for r in m["seeds"]]
need(len(allsources)==733 and len({r["repository_relative"]for r in allsources})==672 and len(allseeds)==3922 and len({identity(r)for r in allseeds})==3849 and len(plan["modules"][7]["sources"])==531 and len(plan["modules"][7]["seeds"])==3773 and len(plan["modules"][8]["sources"])==109 and len(plan["modules"][8]["seeds"])==44,"Exact finite newPlan733/672/3922/3849/final531/3773/default109/44 required")
need(len(set(destinations+historicaldest))==17 and not set(destinations+historicaldest)&{r["repository_relative"]for m in old["modules"]for r in m["sources"]},"New17 destination collision or duplicate")
need(g.module_plan(plan)==plan["modules"],"Qualified module_plan pure object/lexical shape required, no child IO")
need(planpin["bytes"]==2025808 and planpin["bytes"]<2097152 and handoffpin["bytes"]==25668,"Exact reviewed newPlan/H sizes required")
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
 need([g.rec(r["path"])for r,m in controls]==[r for r,m in controls]and[md(authority(r["path"]))for r,m in controls]==[m for r,m in controls],"Qualified G17015.rec actual twelve own tuples/fullMD after each batch required")
qualified_rec_end()
protected=planRO["protected_inputs_after"]+planRO["protected_directories_after"]
need(planRO["protected_inputs_before"]==planRO["protected_inputs_after"]and planRO["protected_directories_before"]==planRO["protected_directories_after"]and len(protected)==9540,"Entire9540 protected metadata required")
def inputs_end():
 need(md(CORE)==core[0]and md(REAL)==core[1]and rec(REAL)==corepin and md(REAL)==core[1]and os.readlink(CORE)=="python3.11","Conditional CORE ownbytes/stableMD drift")
 for r,m in zip(sourcepins,source_meta):ro(r["path"],r,m)
 for x in source_dirs:need(md(authority(x["path"]))==x and {p.name for p in Path(x["path"]).iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Source6 directory drift")
 for r,m in zip(SW,SPEC["qualified_software_control_metadata"]):ro(r["path"],r,m)
 for r,m in controls+readyvalues:ro(r["path"],r,m)
 qualified_rec_end()
 for r,m in zip(additional+historical,additionalmeta+historicalmeta):ro(r["path"],r,m)
 for x in protected:need(md(authority(x["path"]))==x,"Finite protected fullmetadata drift")
 need(md(authority(PLAN.parent))==SPEC["plan_directory_metadata"]and {p.name for p in PLAN.parent.iterdir()}=={"final_source_plan.json","HANDOFF.md"},"Plan2 directory drift")
 canonical_end();need(g.conditional_core_runtime()==runtime,"Approved conditional interpreter drift")
inputs_end()
OUT=authority(S/"runs")/("final_source_plan_v11_ownsha_"+jid)
need(not OUT.exists()and not OUT.is_symlink(),"Exclusive absent new ownSHA output required")
OUT.mkdir(mode=0o755);phase="own_new_PlanV11_and_twelve_controls_no_receipt_child_IO"
try:
 out=dict(schema="root-fixed-source-plan-v11-own-sha-control-capture.v1",status="ACTUAL_NEW_PLAN_V11_OWN_SHA_AND17_PINNED_SOURCE_DOC_ADDITIONS_CPU_VERIFIED_NOT_SOURCE_AUDIT_ACCEPTANCE",actual_job_id=jid,allocation=allocation,current_actual_readiness=readiness,current_readiness_own_CPU_receipts=[x[0]for x in readyvalues],plan=planpin,handoff=handoffpin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,control_receipts=[r for r,m in controls],control_metadata_before=[m for r,m in controls],control_metadata_after=[md(r["path"])for r,m in controls],software_acceptance=SW[0],software_control_receipts=SW,software_control_metadata_before=SPEC["qualified_software_control_metadata"],software_control_metadata_after=[md(r["path"])for r in SW],source_files=SPEC["qualified_frozen_source6"],original_executing_sources=SPEC["qualified_original_source6"],qualified_source12_metadata=source_meta,conditional_core_runtime=runtime,qualified_software17015_terminal_own_CPU_receipt=terminalpin,prior_qualified_PlanV10_and_Handoff=priorpins,qualified_prior17010_ownsha_capture=priorCAPpin,additional_14_Source_rows=additionalrows,additional_14_Source_metadata=additionalmeta,additional_18_safe_seed_receipts=additional+SW,additional_3_historical_Source_rows=historicalrows,additional_3_historical_Source_metadata=historicalmeta,additional_3_historical_safe_seed_receipts=historical,current_canonical_Source4_receipts=canonical,current_canonical_Source4_metadata_before=canonicalmeta,current_canonical_Source4_metadata_after=[md(r["path"])for r in canonical],plan_directory_metadata_before=SPEC["plan_directory_metadata"],plan_directory_metadata_after=md(PLAN.parent),Source_n=733,destination_n=672,seed_n=3922,unique_seed_n=3849,role_n=9,parent_n=17,ordered_alias_n=7,all34keys_type_order_and_original_V10_serialized_bytes_rewind_PASS=True,qualified_module_plan_pure_shape_PASS=True,qualified_G17015_rec_all12_controls_pre_end_PASS=True,all_Source12_SW4_Core_controls12_Source17_canonical4_protected9540_pre_end_afteroutput_finalreadonly_PASS=True,plan_child_receipts_shape_only_no_child_IO=True,source_audit_executed=False,source_staged=False,published=False,ACTIVE_changed=False,compiler_or_tests_or_new_software_qualification_executed=False,scientific_receipt_children_read_or_hashed=False,historical_Slurm_queried=False,own_created_controls_LATE_COMPOSER_ONLY_NOT_PLAN_PREREQUISITES=True)
 raw=(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode();path=OUT/"capture.json"
 with path.open("xb")as f:f.write(raw);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444);os.fsync(f.fileno())
 outmeta=md(path);descriptor=g.rec(path);need(md(path)==outmeta,"First owned output qualified g.rec must preserve prehash full metadata")
 need(path.read_bytes()==raw and read(path)==out and stat.S_IMODE(outmeta["mode"])==0o444 and outmeta["nlink"]==1,"Whole exclusive capture readonly reread required")
 inputs_end();OUT.chmod(0o555)
 fd=os.open(str(OUT),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
 outdir=md(authority(OUT))
 need(stat.S_IMODE(outdir["mode"])==0o555 and outdir["nlink"]==2 and {p.name for p in OUT.iterdir()}=={"capture.json"}and path.read_bytes()==raw and read(path)==out and g.rec(path)==descriptor and md(path)==outmeta,"Final readonly own capture directory/fullbytes required")
 inputs_end();need(md(authority(OUT))==outdir and md(path)==outmeta,"Final output fullmetadata after input guards required")
 print(json.dumps(dict(status=out["status"],capture=descriptor,plan=planpin,handoff=handoffpin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,qualified_software17015_terminal_own_CPU_receipt=terminalpin,Source_n=733,destination_n=672,seed_n=3922,unique_seed_n=3849,role_n=9,parent_n=17,final_output_directory_metadata=outdir,Plan_own_SHA_qualified_only_AFTER_fresh_terminal_RO_Root_and_independent_content_readback=True),sort_keys=True),flush=True)
except BaseException as e:
 try:
  failure=(json.dumps(dict(status="ACTUAL_PLAN_V11_OWN_SHA_UNQUALIFIED",actual_job_id=jid,phase=phase,reason_type=type(e).__name__,reason=str(e),source_staged=False,published=False,ACTIVE_changed=False),indent=2)+"\n").encode()
  with(OUT/"typed_incomplete.json").open("xb")as f:f.write(failure);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 except Exception as se:print("Readonly failure output best-effort: "+repr(se),file=sys.stderr,flush=True)
 raise
PY
