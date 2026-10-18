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
D = S / "submissions" / ("source_inventory_context_observer_v11_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_source_inventory_context_observer_v11", "Account": "u21111210118", "QOS": "normal", "WorkDir": str(S), "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-source-v11-inventory-observer-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_SOURCE_V11_INVENTORY_CONTEXT_OBSERVER_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_SOURCE_V11_INVENTORY_CONTEXT_OBSERVER_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_SOURCE_V11_INVENTORY_CONTEXT_OBSERVER_NOT_EXECUTED"
obj = {"schema": "root-current-owned-source-v11-inventory-observer-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "production_adapter_next_not_acceptance": True}), flush=True)

# Only entered after actual current owned CPU1/GPU0 readiness.
import hashlib,importlib.util,runpy
R=Path("/lustre/users/u21111210118/projects/test9");CORE=R/"env/core/bin/python";REAL=CORE.with_name("python3.11")
SPEC = json.loads("{\"qualified_source_software\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/acceptance.json\",\"bytes\":6693,\"sha256\":\"17652a5db832fb36d7df97ebe8279a0de8484041cb3aa91fb0f759ec4d64e4cb\"},\"qualified_original_source6\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_closure.py\",\"bytes\":300159,\"sha256\":\"74cd7b71abdf1202433ca3fbab7f180144926fbaa74916f81535c58bb3afb207\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/test_final_source_closure.py\",\"bytes\":294055,\"sha256\":\"b93f68140e6f0753c3d7f576cd1b108f8e0ab3c95881611ebb9b863d089d8da3\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_cpu.sbatch\",\"bytes\":1679,\"sha256\":\"c46298252a096f2727c749a8362dc55396ef730896336609a5431c37434a61cb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/HANDOFF.md\",\"bytes\":28119,\"sha256\":\"cf361787a35b00ff40ca63abb3910f873dadc7acfcd8100cd81b8b7fbdbdb968\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5269,\"sha256\":\"a363d0202d237c0d35ea5a8e3fb7d6deabdca27bb72916ee56b66b854b9b1da2\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_context_adapter.py\",\"bytes\":19697,\"sha256\":\"fc1caf2e408e95a77026e72f27fab2e2fe2c20e2c07da61888f5fd2dd14f64b6\"}],\"qualified_frozen_source6\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_closure.py\",\"bytes\":300159,\"sha256\":\"74cd7b71abdf1202433ca3fbab7f180144926fbaa74916f81535c58bb3afb207\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/test_final_source_closure.py\",\"bytes\":294055,\"sha256\":\"b93f68140e6f0753c3d7f576cd1b108f8e0ab3c95881611ebb9b863d089d8da3\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_cpu.sbatch\",\"bytes\":1679,\"sha256\":\"c46298252a096f2727c749a8362dc55396ef730896336609a5431c37434a61cb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/HANDOFF.md\",\"bytes\":28119,\"sha256\":\"cf361787a35b00ff40ca63abb3910f873dadc7acfcd8100cd81b8b7fbdbdb968\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5269,\"sha256\":\"a363d0202d237c0d35ea5a8e3fb7d6deabdca27bb72916ee56b66b854b9b1da2\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_context_adapter.py\",\"bytes\":19697,\"sha256\":\"fc1caf2e408e95a77026e72f27fab2e2fe2c20e2c07da61888f5fd2dd14f64b6\"}],\"qualified_source12_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_closure.py\",\"bytes\":300159,\"inode\":144115643443092649,\"mtime_ns\":1792120232000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/test_final_source_closure.py\",\"bytes\":294055,\"inode\":144115643443092650,\"mtime_ns\":1792120659000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_cpu.sbatch\",\"bytes\":1679,\"inode\":144115643443092651,\"mtime_ns\":1792117466000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/HANDOFF.md\",\"bytes\":28119,\"inode\":144115643443092652,\"mtime_ns\":1792120659000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5269,\"inode\":144115643443092653,\"mtime_ns\":1792120232000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_context_adapter.py\",\"bytes\":19697,\"inode\":144115643443092654,\"mtime_ns\":1792120010000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_closure.py\",\"bytes\":300159,\"inode\":144115643493459570,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/test_final_source_closure.py\",\"bytes\":294055,\"inode\":144115643493459571,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_cpu.sbatch\",\"bytes\":1679,\"inode\":144115643493459572,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/HANDOFF.md\",\"bytes\":28119,\"inode\":144115643493459573,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5269,\"inode\":144115643493459574,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_context_adapter.py\",\"bytes\":19697,\"inode\":144115643493459575,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"qualified_original_source_directory\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1\",\"bytes\":4096,\"inode\":144115643443092648,\"mtime_ns\":1792117363000000000,\"ctime_ns\":1792121074000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"qualified_frozen_source_directory\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner\",\"bytes\":4096,\"inode\":144115643493459569,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"qualified_software_controls\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/acceptance.json\",\"bytes\":6693,\"sha256\":\"17652a5db832fb36d7df97ebe8279a0de8484041cb3aa91fb0f759ec4d64e4cb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/contracts.json\",\"bytes\":2214,\"sha256\":\"238e578ec3dc30134a290b5ae3f8c626b5fa423055debf598d36dd0aca230e1a\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/contracts.txt\",\"bytes\":57823,\"sha256\":\"a48daf4898c227e63a16d0d9114df72f699f6bfb4493c21052f993e1ddec2e0c\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/source_snapshot.json\",\"bytes\":16095,\"sha256\":\"5e9b4ce1c164f0dbb22ba1152b22a5db0415ecbd23268faeeb80f9697e8f46ae\"}],\"qualified_software_control_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/acceptance.json\",\"bytes\":6693,\"inode\":144115643493469239,\"mtime_ns\":1792122343000000000,\"ctime_ns\":1792122343000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/contracts.json\",\"bytes\":2214,\"inode\":144115643493469237,\"mtime_ns\":1792122343000000000,\"ctime_ns\":1792122343000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/contracts.txt\",\"bytes\":57823,\"inode\":144115643493459576,\"mtime_ns\":1792122343000000000,\"ctime_ns\":1792122343000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/source_snapshot.json\",\"bytes\":16095,\"inode\":144115643493469238,\"mtime_ns\":1792122343000000000,\"ctime_ns\":1792122343000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"conditional_CORE_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/env/core/bin/python\",\"bytes\":10,\"inode\":144115618512131424,\"mtime_ns\":1790940371000000000,\"ctime_ns\":1790940371000000000,\"mode\":41471,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\",\"bytes\":25916456,\"inode\":144115618512129393,\"mtime_ns\":1790940364000000000,\"ctime_ns\":1790940383000000000,\"mode\":33277,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"source_software_terminal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_parent_diagnostic_history_software17015_actual_terminal_metadata_seal/receipt.json\",\"bytes\":10037419,\"inode\":144115643443092690,\"mtime_ns\":1792122863000000000,\"ctime_ns\":1792122863000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"software_outer_proof\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_parent_diagnostic_history_software_outer_17015/execution_control.json\",\"bytes\":107479,\"sha256\":\"40962234a42b9c2fb4c8587d4823df4f61bdd97bf3b37ff536575fd9d0d20487\"},\"software_outer_proof_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_parent_diagnostic_history_software_outer_17015/execution_control.json\",\"bytes\":107479,\"inode\":144115643493469240,\"mtime_ns\":1792122346000000000,\"ctime_ns\":1792122346000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"plan_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17015_v11/final_source_plan.json\",\"bytes\":2025808,\"inode\":144115643443092692,\"mtime_ns\":1792123307000000000,\"ctime_ns\":1792124063000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17015_v11/HANDOFF.md\",\"bytes\":25668,\"inode\":144115643443092693,\"mtime_ns\":1792123307000000000,\"ctime_ns\":1792124063000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"plan_readonly_seal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v11_from17015_metadata_readonly_seal/receipt.json\",\"bytes\":10039611,\"inode\":144115643443092695,\"mtime_ns\":1792124065000000000,\"ctime_ns\":1792124065000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"current_canonical_Source4\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\",\"bytes\":2225,\"sha256\":\"d602956154fb396fd14d7737c360d7d35144b4e6ca6c3d1c51eb6dc401e42615\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\",\"bytes\":24234,\"sha256\":\"c8fe4495439826f0882b4c43952926e5de5361f88460320cc117d003352ff345\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\",\"bytes\":1633,\"sha256\":\"2d40850d19c7835d658e7154e5a1cb53ae763e31d360b41eec253397f2c5befb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\",\"bytes\":6148,\"sha256\":\"c83e427f73ff1545253d64dbb165c7e60328bb698721d1e03663e6ea7d7c403f\"}],\"current_canonical_Source4_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\",\"bytes\":2225,\"inode\":144115543165691905,\"mtime_ns\":1791727539000000000,\"ctime_ns\":1791727539000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\",\"bytes\":24234,\"inode\":144115543165691892,\"mtime_ns\":1791727495000000000,\"ctime_ns\":1791727495000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\",\"bytes\":1633,\"inode\":144115543165691947,\"mtime_ns\":1791727539000000000,\"ctime_ns\":1791727539000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\",\"bytes\":6148,\"inode\":144115543165691893,\"mtime_ns\":1791727495000000000,\"ctime_ns\":1791727495000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"source_software_terminal_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_parent_diagnostic_history_software17015_actual_terminal_metadata_seal/receipt.json\",\"bytes\":10037419,\"sha256\":\"ff7ee26804bd2376b61793a2c06cb8cd2c5d827f40651e6d4e8f2c2e72434944\"},\"new_request_path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17015_v11/request.json\",\"new_request2_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17015_v11/request.json\",\"bytes\":6550,\"inode\":144115643443092718,\"mtime_ns\":1792126278000000000,\"ctime_ns\":1792126758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17015_v11/request_metadata.json\",\"bytes\":36270,\"inode\":144115643443092719,\"mtime_ns\":1792126278000000000,\"ctime_ns\":1792126758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"new_request_directory_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17015_v11\",\"bytes\":4096,\"inode\":144115643443092717,\"mtime_ns\":1792126278000000000,\"ctime_ns\":1792126758000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"request_readonly_seal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_context_request_from17015_v11_metadata_readonly_seal/receipt.json\",\"bytes\":10070815,\"inode\":144115643443092721,\"mtime_ns\":1792126760000000000,\"ctime_ns\":1792126760000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"plan_own_capture\":{\"bytes\":67754,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v11_ownsha_17016/capture.json\",\"sha256\":\"6330c73f670e947cd0604e2c8862d69ebe8ea9a013191d58114746b6d3563d9a\"},\"plan_own_capture_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v11_ownsha_17016/capture.json\",\"bytes\":67754,\"inode\":144115643493469254,\"mtime_ns\":1792125336000000000,\"ctime_ns\":1792125336000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"plan_own_terminal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v11_ownsha17016_actual_terminal_metadata_seal/receipt.json\",\"bytes\":10069834,\"inode\":144115643443092716,\"mtime_ns\":1792125704000000000,\"ctime_ns\":1792125704000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"root_control_human\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V11_INVENTORY_CONTEXT_FAILURE_OBSERVER_FROM17015_17017_20261016_REV1.md\",\"primary_wrap\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_inventory_context_observer_v11_from17015_17017_primary_claim/wrap.sh\",\"protected_metadata_union_count\":9583,\"failed17017_terminal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_parent_diagnostic_history_audit17017_actual_failed_terminal_metadata_seal/receipt.json\",\"bytes\":11309451,\"inode\":144115643443092756,\"mtime_ns\":1792128533000000000,\"ctime_ns\":1792128533000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}}")
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
need(a["source_files"]==SPEC["qualified_frozen_source6"]and a["original_executing_sources"]==SPEC["qualified_original_source6"]and a["allocation"]["job_id"]=="17015","Actual software17015 Source6 bindings required")
terminalpath=Path(SPEC["source_software_terminal_metadata"]["path"])
terminalpin,terminalmeta=ro(terminalpath,SPEC["source_software_terminal_receipt"],SPEC["source_software_terminal_metadata"])
terminal=read(terminalpath)
need(len(terminal)==32 and terminal["schema"]=="root-final-source-parent-diagnostic-history-software17015-terminal-metadata-seal.v1"and terminal["actual_job_id"]=="17015"and terminal["Root_plus_two_whole_actual_software284_content_READBACK_PASS"]is True and terminal["actual_unique_named_tests"]==284 and terminal["historical238_names_and_relative_order_preserved"]is True and terminal["new46_actual_parent_diagnostic_history_contracts_PASS"]is True and terminal["actual_GPU0_from_current_readiness"]is True,"Actual accepted284 terminal context required")
need([terminal[k]for k in ["actual_software_acceptance","actual_contracts","actual_contract_log","actual_source_snapshot"]]==SPEC["qualified_software_controls"] and terminal["fresh_terminal"]["returncode"]==0 and terminal["fresh_terminal"]["raw_stderr"]==""and terminal["fresh_terminal"]["numeric_9column_row"]==["17015","COMPLETED","0:0","89","1","test9_final_source_parent_diagnostic_history_v3","u21111210118","u21111210118","organ"],"Exact qualified17015 SW4/fresh terminal required")
# All twelve exact own control bytes are also guarded with stdlib before the first project import.
pre_cap_pin,pre_cap_md=ro(SPEC["plan_own_capture"]["path"],SPEC["plan_own_capture"],SPEC["plan_own_capture_metadata"])
pre_cap=read(pre_cap_pin["path"])
need(len(pre_cap)==55 and pre_cap["schema"]=="root-fixed-source-plan-v11-own-sha-control-capture.v1"and pre_cap["actual_job_id"]=="17016","Actual qualified current Plan11 capture55 required")
added_source_rows=pre_cap["additional_14_Source_rows"]+pre_cap["additional_3_historical_Source_rows"]
added_source_metadata=pre_cap["additional_14_Source_metadata"]+pre_cap["additional_3_historical_Source_metadata"]
need(len(added_source_rows)==len(added_source_metadata)==17,"Exact own-pinned Source17 additions required")
for row,meta in zip(added_source_rows,added_source_metadata):ro(row["receipt"]["path"],row["receipt"],meta)
pre_q,pre_qmd=ro(SPEC["new_request_path"],metadata=SPEC["new_request2_metadata"][0])
pre_m,pre_mmd=ro(Path(SPEC["new_request_path"]).with_name("request_metadata.json"),metadata=SPEC["new_request2_metadata"][1])
pre_plan,pre_planmd=ro(pre_cap["plan"]["path"],pre_cap["plan"],SPEC["plan_metadata"][0])
pre_h,pre_hmd=ro(pre_cap["handoff"]["path"],pre_cap["handoff"],SPEC["plan_metadata"][1])
pre_t,pre_tmd=ro(SPEC["plan_own_terminal_metadata"]["path"],metadata=SPEC["plan_own_terminal_metadata"])
pre_outer,pre_outermd=ro(SPEC["software_outer_proof"]["path"],SPEC["software_outer_proof"],SPEC["software_outer_proof_metadata"])
pre_qro,pre_qromd=ro(SPEC["request_readonly_seal_metadata"]["path"],metadata=SPEC["request_readonly_seal_metadata"])
pre_pro,pre_promd=ro(SPEC["plan_readonly_seal_metadata"]["path"],metadata=SPEC["plan_readonly_seal_metadata"])
pre_human,pre_humanmd=ro(SPEC["root_control_human"]);pre_wrap,pre_wrapmd=ro(SPEC["primary_wrap"])
preimport_controls=[(pre_q,pre_qmd),(pre_m,pre_mmd),(pre_plan,pre_planmd),(pre_h,pre_hmd),(pre_cap_pin,pre_cap_md),(pre_t,pre_tmd),(terminalpin,terminalmeta),(pre_outer,pre_outermd),(pre_qro,pre_qromd),(pre_pro,pre_promd),(pre_human,pre_humanmd),(pre_wrap,pre_wrapmd)]
need(len(preimport_controls)==len({v["path"]for v,x in preimport_controls})==12,"Twelve exact own controls before first project import required")
# This is a new diagnostic, not a retry or acceptance of failed17017.
failed_path=Path(SPEC["failed17017_terminal_metadata"]["path"])
failed_pin,failed_meta=ro(failed_path,metadata=SPEC["failed17017_terminal_metadata"])
failed=read(failed_path)
need(len(failed)==33 and failed["schema"]=="root-source-v11-production17017-failed-terminal-metadata-readonly-seal.v1"and failed["actual_job_id"]=="17017"and failed["Root_and_independent_whole_saved_failure_content_READBACK_PASS"]is True and failed["actual_all284_named_PASS_no_fail_error_skip"]is True and failed["actual_offending_r_parent_trail_module_unobserved"]is True and failed["source_audit_accepted"]is False,"Actual preserved failed17017 control required")
need(failed["actual_reason"]=="Fixed13299 DATA requires exact BaseA/field/two-module/fulltuple context"and failed["fresh_terminal_query"]["returncode"]==0 and failed["fresh_terminal_query"]["raw_stderr"]==""and failed["fresh_terminal_query"]["raw_stdout"]=="17017|FAILED|1:0|372|1|test9_final_source_parent_diagnostic_history_v3|u21111210118|u21111210118|organ\n","Exact actual17017 failure and fresh saved terminal required")
need(failed["protected_inputs_before"]==failed["protected_inputs_after"]and len(failed["protected_inputs_after"])==9616 and len(failed["after_files"])==1087 and len(failed["after_directories"])==14 and failed["conditional_CORE_metadata_before"]==failed["conditional_CORE_metadata_after"]==core,"Exact full failed17017 preservation bounds required")
failed_protected={}
for x in failed["protected_inputs_after"]+failed["after_files"]+failed["after_directories"]+[md(failed_path),md(failed_path.parent)]:
 need(x["path"]not in failed_protected,"No duplicate failed17017 history metadata")
 failed_protected[x["path"]]=x
need(len(failed_protected)==10719,"Exact failed17017 protected union10719 required")
for x in failed_protected.values():need(md(authority(x["path"]))==x,"Failed17017 history current metadata before import differs")
preimport_controls.append((failed_pin,failed_meta))
need(len(preimport_controls)==len({r["path"]for r,x in preimport_controls})==13,"Exactly13 own controls before project import required")
# No project import before Source12/SW4/Core/Source17/own13/current readiness.

entry=Path(SPEC["qualified_frozen_source6"][0]["path"])
ss=importlib.util.spec_from_file_location("root_qualified_source17015_production_control",entry)
g=importlib.util.module_from_spec(ss);ss.loader.exec_module(g)
need(g.software_shape(a,ct)==SPEC["qualified_frozen_source6"],"Unchanged qualified Source software shape required")
allocation=g.cpu();runtime=g.conditional_core_runtime()
need(allocation["job_id"]==jid and allocation["allocated_CPUs"]==1 and allocation["allocated_gpus"]==0 and allocation["numeric_sacct_row"]==attempts[selected-1]["actual_row"]and runtime==a["conditional_core_runtime"],"Actual fresh Source current CPU/Core required")
snapshot=read(SPEC["qualified_software_controls"][3]["path"])
need(g.software_snapshot_shape(a,snapshot)==snapshot,"Actual qualified software six snapshot required")

QP=Path(SPEC["new_request_path"]);MP=QP.with_name("request_metadata.json")
QRO=Path(SPEC["request_readonly_seal_metadata"]["path"])
qropin,qrometa=ro(QRO,metadata=SPEC["request_readonly_seal_metadata"]);qr=read(QRO)
need(qr["schema"]=="root-new-plan-v11-strict13-request-metadata-readonly-seal.v1"and qr["Root_and_two_independent_whole_Q_and_metadata_static_PASS"]is True,"Actual reviewed strict13 QRO required")
need(qr["after_files"]==SPEC["new_request2_metadata"]and qr["after_directory"]==SPEC["new_request_directory_metadata"],"Exact readonly Q2/P metadata required")
qpin,qmeta=ro(QP,metadata=SPEC["new_request2_metadata"][0]);mpin,mmeta=ro(MP,metadata=SPEC["new_request2_metadata"][1])
q=read(QP);m=read(MP)
cap_pin,cap_meta=ro(SPEC["plan_own_capture"]["path"],SPEC["plan_own_capture"],SPEC["plan_own_capture_metadata"])
cap=read(cap_pin["path"])
t7pin,t7meta=ro(SPEC["plan_own_terminal_metadata"]["path"],metadata=SPEC["plan_own_terminal_metadata"])
t7=read(t7pin["path"])
need(t7["schema"]=="root-source-plan-v11-ownsha17016-terminal-metadata-readonly-seal.v1"and len(t7)==35 and t7["actual_job_id"]=="17016"and t7["Root_and_independent_whole_actual_capture55_content_READBACK_PASS"]is True and t7["actual_capture_own_CPU_receipt"]==cap_pin and t7["actual_Plan_own_CPU_receipt"]==cap["plan"]and t7["actual_HANDOFF_own_CPU_receipt"]==cap["handoff"],"Actual qualified Plan ownSHA17016 terminal required")
need(t7["fresh_terminal_query"]["returncode"]==0 and t7["fresh_terminal_query"]["raw_stderr"]==""and t7["fresh_terminal_query"]["raw_stdout"]=="17016|COMPLETED|0:0|11|1|test9_source_plan_v11_ownsha_cpu|u21111210118|u21111210118|organ\n","Actual ownPlan17016 terminal row required")
planpin,planmeta=ro(cap["plan"]["path"],cap["plan"],SPEC["plan_metadata"][0]);hpin,hmeta=ro(cap["handoff"]["path"],cap["handoff"],SPEC["plan_metadata"][1])
plan=read(planpin["path"])
need(q["final_source_plan"]==planpin and q["library_software_acceptance"]==SPEC["qualified_source_software"]==plan["library_software_acceptance"]and q["mapper_software_acceptance"]==plan["mapper_software_acceptance"],"Exact Q/actual17015/V11Plan software bindings required")
need(len(q)==13 and list(q)==m["exact13_key_order"]and q["root_owned"]is True and len(q["finite_source_parent_aliases"])==8 and len(plan["context_parent_seeds"])==17 and len(plan["aliases"])==7,"Exact strict13/finite8/17/7 request required")
for k in("raw_JSON_rewrite_allowed","generic_relative_resolution_allowed","generic_external_resolution_allowed"):need(q[k]is False,"No generic permission granted")
for k in("bbf_parent_aliases","historical_parent_aliases","recovered_parent_aliases","archive_parent_aliases"):need(type(q[k])is list and q[k]==[],"No generic parent alias added")
need(cap==pre_cap and cap["actual_job_id"]=="17016"and cap["Source_n"]==733 and cap["destination_n"]==672 and cap["seed_n"]==3922 and cap["unique_seed_n"]==3849 and cap["role_n"]==9 and cap["parent_n"]==17 and cap["source_audit_executed"]is False,"Actual newPlan733/672/3922/3849/9/17 scope required")
need(g.module_plan(plan)==plan["modules"],"Qualified pure-shape module plan required")
need(plan["modules"][7]["sources"][-14:]==added_source_rows[:14]and plan["modules"][8]["sources"][-3:]==added_source_rows[14:],"Exact current Source17 Plan tails must match qualified own capture")
need(cap["additional_18_safe_seed_receipts"]==plan["modules"][7]["seeds"][-18:]and cap["additional_3_historical_safe_seed_receipts"]==plan["modules"][8]["seeds"][-3:],"Exact qualified Source17 and software4 safe Seed tails required")
need(m["root_and_two_independent_actual17016_content_readback_PASS"]is True and m["root_and_independent_actual17016_terminal_RO_readback_PASS"]is True and m["accepted_Plan"]==planpin and m["accepted_Plan_HANDOFF"]==hpin and m["actual17016_Plan_own_capture"]==cap_pin,"Whole qualified17016 metadata bindings required")
outerpin,outermeta=ro(SPEC["software_outer_proof"]["path"],SPEC["software_outer_proof"],SPEC["software_outer_proof_metadata"])
planropin,planrometa=ro(SPEC["plan_readonly_seal_metadata"]["path"],metadata=SPEC["plan_readonly_seal_metadata"])
ownhuman,ownhumanmeta=ro(SPEC["root_control_human"]);ownwrap,ownwrapmeta=ro(SPEC["primary_wrap"])
humantext=Path(ownhuman["path"]).read_text("utf-8");wraptext=Path(ownwrap["path"]).read_text("utf-8")
need(humantext.count("```python\n")==1 and wraptext.endswith("\nPY\n")and wraptext.partition("<<'PY'\n")[2][:-4].rstrip("\n")==humantext.split("```python\n",1)[1].split("\n```",1)[0].rstrip("\n"),"Actual primary shell must bind whole reviewed Root Human")
controls=[(qpin,qmeta),(mpin,mmeta),(planpin,planmeta),(hpin,hmeta),(cap_pin,cap_meta),(t7pin,t7meta),(terminalpin,terminalmeta),(outerpin,outermeta),(qropin,qrometa),(planropin,planrometa),(ownhuman,ownhumanmeta),(ownwrap,ownwrapmeta),(failed_pin,failed_meta)]
need(len(controls)==len({r["path"]for r,x in controls})==13 and controls==preimport_controls,"Exactly13 own controls equal preimport byte and metadata bindings required")
protected={}
for x in qr["protected_inputs_after"]+qr["protected_directories_after"]+qr["after_files"]+[qr["after_directory"],md(QRO),md(QRO.parent)]:
 if x["path"]in protected:need(protected[x["path"]]==x,"Protected metadata overlap differs")
 protected[x["path"]]=x
need(len(protected)==SPEC["protected_metadata_union_count"],"Exact actual reviewed finite protected metadata union required")
need(qr["protected_inputs_before"]==qr["protected_inputs_after"] and qr["protected_directories_before"]==qr["protected_directories_after"],"Whole request file and directory metadata protection differs")
readiness=read(D/"readiness.json");readyvalues=[ro(D/"readiness.json")]
for cmd in[readiness["current_scontrol_observation"]]+readiness["attempts"]:
 for k in("raw_stdout","raw_stderr"):readyvalues.append(ro(cmd[k]["path"]))
canonical=SPEC["current_canonical_Source4"];canonicalmeta=SPEC["current_canonical_Source4_metadata"]
def inputs_end():
 need(md(CORE)==core[0]and md(REAL)==core[1]and rec(REAL)==corepin and md(REAL)==core[1]and os.readlink(CORE)=="python3.11","Conditional CORE ownbytes/stablemetadata drift")
 for r,x in zip(sourcepins,source_meta):ro(r["path"],r,x)
 for x in source_dirs:need(md(authority(x["path"]))==x and{p.name for p in Path(x["path"]).iterdir()}=={Path(v["path"]).name for v in SPEC["qualified_frozen_source6"]},"Qualified source directory drift")
 for r,x in zip(SPEC["qualified_software_controls"],SPEC["qualified_software_control_metadata"]):ro(r["path"],r,x)
 for r,x in controls+readyvalues:ro(r["path"],r,x)
 for row,x in zip(added_source_rows,added_source_metadata):ro(row["receipt"]["path"],row["receipt"],x)
 need([g.rec(r["path"])for r,x in controls]==[r for r,x in controls]and[md(authority(r["path"]))for r,x in controls]==[x for r,x in controls],"Qualified rec13/postread fullmetadata differs")
 for x in protected.values():need(md(authority(x["path"]))==x,"Finite protected metadata drift")
 for r,x in zip(canonical,canonicalmeta):
  need(md(authority(r["path"]))==x and stat.S_IMODE(x["mode"])==0o664 and x["nlink"]==1 and stat.S_ISREG(x["mode"]),"Only exact canonical4 hash-only leaves allowed")
  need(g.rec(r["path"])==r and md(r["path"])==x,"Canonical4 ownbyte drift")
 need(g.conditional_core_runtime()==runtime,"Qualified current CORE runtime differs")
inputs_end()
def observer_inputs_end():
 inputs_end()
 for x in failed_protected.values():need(md(authority(x["path"]))==x,"Failed17017 history full native metadata drift")
observer_inputs_end()
OUT=authority(S/"runs")/("final_source_inventory_context_observer_v11_"+jid)
AUX=OUT.with_name(OUT.name+"_context_adapter")
PROOF=authority(S/"submissions")/("source_inventory_context_observer_v11_"+jid)
need(all(not p.exists()and not p.is_symlink()for p in[OUT,AUX,PROOF]),"Exclusive absent new diagnostic output namespaces required")
adapter=Path(SPEC["qualified_frozen_source6"][-1]["path"])
actual_argv=[str(adapter),"--request",str(QP),"--out",str(OUT)]
savedargv=list(sys.argv)
try:
 sys.argv=actual_argv
 try:runpy.run_path(str(adapter),run_name="__main__")
 finally:sys.argv=savedargv
except ValueError as original_error:
 need(sys.argv==savedargv and type(original_error)is ValueError and str(original_error)=="Fixed13299 DATA requires exact BaseA/field/two-module/fulltuple context","Exact original inventory-history context ValueError required")
 new_source_rows=[];new_source_meta=[];new_source_dirs=[]
 for folder in[OUT/"runner",AUX/"runner"]:
  dm=md(authority(folder));need(dm["mode"]==stat.S_IFDIR|0o555 and dm["nlink"]==2 and {p.name for p in folder.iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Actual new diagnostic frozen6 directory required")
  new_source_dirs.append(dm)
  for expected in SPEC["qualified_frozen_source6"]:
   p=folder/Path(expected["path"]).name;rr,mm=ro(p)
   need((rr["bytes"],rr["sha256"])==(expected["bytes"],expected["sha256"]),"Actual observed executable source must match qualifiedG17015")
   new_source_rows.append(rr);new_source_meta.append(mm)
 observer_inputs_end()
 OBS_MODULES=set(m["role"]for m in plan["modules"])|{"EXACT_ACCEPTED_CONTEXT_PARENT"}
 observed_code_file=str(AUX/"runner/final_source_closure.py")
 source_frames=[];adapter_frames=[];tb=original_error.__traceback__
 while tb is not None:
  frame=tb.tb_frame
  if frame.f_code.co_filename==observed_code_file:source_frames.append((frame,tb.tb_lineno))
  if frame.f_code.co_filename==str(adapter)and frame.f_code.co_name=="run":adapter_frames.append((frame,tb.tb_lineno))
  tb=tb.tb_next
 need([(f.f_code.co_name,line)for f,line in source_frames]==[("audit",4343),("edge",788),("need",40)],"Exact actual inventory-history traceback chain required")
 need(len(adapter_frames)==1 and adapter_frames[0][1]==39,"Actual unchanged adapter.run39 required")
 af,ef,nf=[f for f,line in source_frames]
 need([f.f_code.co_qualname for f in(af,ef,nf)]==["audit","InventoryHistoryOpaqueLeaf.edge","need"],"Exact authenticated Source function qualifications required")
 need(ef.f_globals is af.f_globals and nf.f_globals is af.f_globals,"Actual same qualified Source module globals required")
 for frame,name in[(af,"audit"),(nf,"need")]:need(getattr(frame.f_globals.get(name),"__code__",None)is frame.f_code,"Authenticated global Source function required")
 need({"r","parent","trail","module","stage","inventory_history"}<=af.f_locals.keys()and {"self","receipt","parent","trail","module"}<=ef.f_locals.keys(),"Declared actual audit and edge locals required")
 cls=ef.f_globals.get("InventoryHistoryOpaqueLeaf");scope=ef.f_locals["self"]
 need(type(cls)is type and type(scope)is cls and scope is af.f_locals["inventory_history"]and getattr(getattr(cls,"edge",None),"__code__",None)is ef.f_code,"Actual InventoryHistoryOpaqueLeaf instance and unchanged edge code required")
 need(nf.f_locals.get("v")is False and nf.f_locals.get("msg")=="Fixed13299 DATA requires exact BaseA/field/two-module/fulltuple context"and af.f_globals.get("R")==R,"Actual failed need40 and authority required")
 df=adapter_frames[0][0];lib=df.f_locals.get("lib")
 need(getattr(df.f_globals.get("run"),"__code__",None)is df.f_code and type(lib)is type(g)and lib.__dict__ is af.f_globals,"Actual adapter.run39 must own authenticated Source module globals")
 ar=af.f_locals["r"]
 need(type(ar)is dict and ar is ef.f_locals["receipt"]and {"path","bytes","sha256"}<=ar.keys()and all(type(k)is str and len(k)<=8192 for k in ar),"Same actual receipt dict and bounded scalar keys required")
 raw_path,byte_n,sha=ar["path"],ar["bytes"],ar["sha256"]
 need(type(raw_path)is str and len(raw_path)<=8192 and Path(raw_path).is_absolute()and type(byte_n)is int and byte_n>=0 and type(sha)is str and re.fullmatch("[0-9a-f]{64}",sha)is not None,"Already-shaped nonboolean absolute receipt scalar3 required")
 extra_names=sorted(k for k in ar if k not in{"path","bytes","sha256"});need(len(extra_names)<=256,"Bounded extra key names only; no extra values")
 parent,trail,module=[af.f_locals[k]for k in("parent","trail","module")]
 need(parent is None or(type(parent)is str and len(parent)<=8192),"Bounded actual parent scalar")
 need(type(trail)is tuple and len(trail)<=256 and all(type(x)is str and len(x)<=8192 for x in trail),"Bounded original tuple trail")
 need(type(module)is str and module in OBS_MODULES and af.f_locals["stage"]=="recursive_exact_new_dependencies","Actual existing queue module and stage")
 need(all(af.f_locals[k]is ef.f_locals[k]for k in("parent","trail","module")),"Audit and edge must carry same actual context objects")
 LEAF=dict(path=str(S/"runs/source_unknown_relative_inventory_13299/diagnostic.json"),bytes=590526,sha256="8bc7232449d5469cc621e6e34b26716c3d8ff65fc4a52e10d04b3977d9229313")
 BASE=dict(path=str(S/"runs/source_refresh_relative_v10_13316/acceptance.json"),bytes=10963,sha256="fcaeb34bb139bc2c4a271e44dd72f23260592af23c872c4ae2bb7a8f67c47e58")
 FIELD=("original_failure_history","actual13299_complete_accessible_finite_inventory_diagnostic_only");MODULES=("default_workflow_integration","final_delivery_tools")
 need(ef.f_globals.get("_HISTORY_LEAF")==LEAF and ef.f_globals.get("_HISTORY_BASE")==BASE and ef.f_globals.get("_HISTORY_FIELD")==FIELD and ef.f_globals.get("_HISTORY_MODULES")==MODULES,"Actual fixed context globals unchanged")
 projected=dict(path=raw_path,bytes=byte_n,sha256=sha)
 related_by_path=raw_path==LEAF["path"];related_by_fingerprint=(byte_n,sha)==(LEAF["bytes"],LEAF["sha256"])
 full3_equal=set(ar)=={"path","bytes","sha256"}and projected==LEAF
 checks=dict(receipt_full_exact3_equal=full3_equal,parent_equals_exact_BaseA_path=parent==BASE["path"],trail_is_original_tuple=type(trail)is tuple,trail_equals_exact_field=trail==FIELD,module_is_one_of_two_allowed=module in MODULES)
 need((related_by_path or related_by_fingerprint)and not all(checks.values())and type(scope.active)is bool,"Actual matching guard and failed exact conjunction must be reproduced")
 offender=dict(path=dict(type="str",value=raw_path),bytes=dict(type="int",value=byte_n),sha256=dict(type="str",value=sha),extra_key_names=extra_names)
 context=dict(parent_path=parent,trail=list(trail),module=module,stage=af.f_locals["stage"])
 inventory_guard_scalar=dict(related_by_path=related_by_path,related_by_fingerprint=related_by_fingerprint,exact_conjunction_checks=checks,scope_active=scope.active,current_failed_edge_inputs_not_entered=True)
 # No capture reads of stale physical/basis/obj, resolve, aliases, seen/history/queue,
 # extra values, copy bytes, or offending/parent paths and ancestors.
 ctpin,ctmeta=ro(OUT/"contracts.json");ct=read(ctpin["path"]);logpin,logmeta=ro(ct["log"]["path"],ct["log"]);log=Path(logpin["path"]).read_text()
 named=re.findall(r"(?m)^(test[^\n]+) \.\.\. ok$",log)
 need(ct["status"]=="PASS"and type(ct["tests"])is int and ct["tests"]==284 and ct["errors"]==ct["failures"]==0 and ct["owned_python_compile_PASS"]is True and ct["bash_syntax_PASS"]is True and len(named)==len(set(named))==284 and re.findall(r"(?:^|\n)Ran ([0-9]+) tests?\b",log)==["284"]and log.rstrip().endswith("OK"),"Actual diagnostic mandatory284 producer required")
 need(ct["tested_source_files"]==new_source_rows[:6],"Actual contracts bind newOUT runner6")
 qualified_log=Path(SPEC["qualified_software_controls"][2]["path"]).read_text()
 need(named==re.findall(r"(?m)^(test[^\n]+) \.\.\. ok$",qualified_log),"Actual mandatory284 names and order equal qualified284")
 case_lines=[line for line in log.splitlines()if line.startswith("test")];qualified_case_lines=[line for line in qualified_log.splitlines()if line.startswith("test")]
 need(len(case_lines)==284 and all(line.endswith(" ... ok")for line in case_lines)and case_lines==qualified_case_lines and not re.search(r"(?:FAIL|ERROR|skipped=|\[SKIP\])",log),"All actual284 case lines and full relative order require explicit zero extra failure error skip")
 for name in["acceptance.json","context_adapter_acceptance.json","source_inclusion_final.json","source_receipt_closure_final.json"]:need(not(OUT/name).exists()and not(OUT/name).is_symlink(),"No actual Source acceptance may exist")
 need(all((p/"typed_incomplete.json").is_file()for p in[OUT,AUX]),"Original audit and adapter failure controls required")
 typed_values=[ro(p/"typed_incomplete.json")for p in[OUT,AUX]];typed_objects=[read(r["path"])for r,x in typed_values]
 need(all(v["reason_type"]==type(original_error).__name__ and v["reason"]==str(original_error)and v["allocation"]==allocation and v["source_staged"]is False and v["ACTIVE_changed"]is False for v in typed_objects),"Both original typed failures bind actual exception and current allocation")
 need(typed_objects[0]["status"]=="FINAL_SOURCE_CLOSURE_TYPED_INCOMPLETE_NO_STAGING"and typed_objects[0]["failed_stage"]=="recursive_exact_new_dependencies"and typed_objects[1]["status"]=="FINAL_SOURCE_MATERIALIZED_CONTEXT_ADAPTER_TYPED_INCOMPLETE"and typed_objects[1]["failed_stage"]=="actual_frozen_library_audit_with_module_local_context_reader","Exact original Source and adapter typed stages required")
 ownfixed=[(ctpin,ctmeta),(logpin,logmeta)]+typed_values
 def new_outputs_end():
  for r,x in zip(new_source_rows,new_source_meta):ro(r["path"],r,x)
  for x in new_source_dirs:need(md(authority(x["path"]))==x and {p.name for p in Path(x["path"]).iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Actual diagnostic Source directory drift")
  for r,x in ownfixed:ro(r["path"],r,x)
  need(read(ctpin["path"])==ct and [read(r["path"])for r,x in typed_values]==typed_objects,"Actual contracts and original typed controls changed during final reread")
 def new_outputs_metadata_only_end():
  for r,x in zip(new_source_rows,new_source_meta):need(md(authority(r["path"]))==x,"Final actual Source fullmetadata after last input operations differs")
  for r,x in ownfixed:need(md(authority(r["path"]))==x,"Final actual controls fullmetadata after last input operations differs")
  for x in new_source_dirs:need(md(authority(x["path"]))==x and {p.name for p in Path(x["path"]).iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Final actual runner6 directory metadata and universe differs")
 new_outputs_end();observer_inputs_end();new_outputs_metadata_only_end()
 PROOF.mkdir(mode=0o755)
 result=dict(schema="root-source-v11-inventory-context-receipt-frame-observation.v1",status="DIAGNOSTIC_ONLY_ACTUAL_INVENTORY13299_CONTEXT_FRAME_OBSERVED_ORIGINAL_ERROR_WILL_BE_RERAISED",actual_job_id=jid,allocation=allocation,current_actual_readiness=readiness,actual_direct_frozen_adapter_argv=actual_argv,original_exception_type=type(original_error).__name__,original_exception_message=str(original_error),authenticated_frames=[dict(file=f.f_code.co_filename,line=ln,name=f.f_code.co_name,qualname=f.f_code.co_qualname)for f,ln in source_frames],authenticated_adapter_run_frame=dict(file=df.f_code.co_filename,line=adapter_frames[0][1],name=df.f_code.co_name),offending_receipt_scalar_observation=offender,audit_context_scalar=context,inventory_history_guard_scalar_observation=inventory_guard_scalar,observer_added_capture_performs_no_offender_parent_target_or_ancestor_filesystem_IO=True,current_failed_edge_inputs_not_entered_prior_authorized_observations_not_excluded=True,new_diagnostic_context_only_not_retrospective_17017=True,original17017_context_remains_UNOBSERVED=True,no_parent_JSON_or_other_object_dumped=True,no_stale_physical_basis_obj_alias_seen_queue_or_extra_values_dumped=True,qualified_source12=sourcepins,qualified_source12_metadata=source_meta,qualified_software4=SPEC["qualified_software_controls"],additional17_own_CPU_pinned_Source_rows=added_source_rows,conditional_core_runtime=runtime,control_receipts=[r for r,x in controls],control_metadata_before=[x for r,x in controls],control_metadata_after=[md(r["path"])for r,x in controls],failed17017_terminal_own_CPU_receipt=failed_pin,failed17017_protected_metadata_n=len(failed_protected),actual_new_frozen_source12=new_source_rows,actual_new_frozen_source12_metadata=new_source_meta,actual_new_frozen_source2_directory_metadata=new_source_dirs,mandatory_contracts=ctpin,mandatory_log=logpin,actual284_unique_named_PASS=True,actual_two_original_typed_failures_bound_to_current_error_and_allocation=True,mandatory_named_tests=named,all_source_runtime_controls_pre_end_afteroutput_finalreadonly_PASS=True,source_staged=False,published=False,ACTIVE_changed=False,Source_audit_acceptance=False,own_created_controls_LATE_Composer_not_Plan_prerequisites=True,expected_actual_terminal_FAILED1_0=True,observation_qualification_requires_fresh_terminal_and_independent_whole_readback=True)
 rp=PROOF/"observation.json";raw=(json.dumps(result,indent=2,allow_nan=False,ensure_ascii=False)+"\n").encode()
 with rp.open("xb")as f:f.write(raw);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444);os.fsync(f.fileno())
 rpm=md(rp);pin=g.rec(rp);need(rp.read_bytes()==raw and read(rp)==result and md(rp)==rpm,"Whole own observation reread and prehash metadata required")
 new_outputs_end();observer_inputs_end();new_outputs_metadata_only_end();PROOF.chmod(0o555)
 fd=os.open(str(PROOF),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
 pd=md(authority(PROOF));need(pd["mode"]==stat.S_IFDIR|0o555 and {p.name for p in PROOF.iterdir()}=={"observation.json"}and rp.read_bytes()==raw and read(rp)==result and g.rec(rp)==pin and md(rp)==rpm,"Final readonly observation universe required")
 new_outputs_end();observer_inputs_end();new_outputs_metadata_only_end()
 need(md(PROOF)==pd and md(rp)==rpm,"Final observer output metadata guard required")
 print(json.dumps(dict(status=result["status"],observation=pin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,failed17017_terminal=failed_pin,expected_terminal_FAILED1_0=True,Source_audit_acceptance=False),sort_keys=True),flush=True)
 raise
else:
 raise RuntimeError("Expected original inventory-context failure was not observed; no diagnostic or Source qualification")
PY
