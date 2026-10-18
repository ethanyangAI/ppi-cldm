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
D = S / "submissions" / ("final_source_v11_production_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_final_source_parent_diagnostic_history_v3", "Account": "u21111210118", "QOS": "normal", "WorkDir": str(S), "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-source-v11-production-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_SOURCE_V11_PRODUCTION_AUDIT_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_SOURCE_V11_PRODUCTION_AUDIT_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_SOURCE_V11_PRODUCTION_AUDIT_NOT_EXECUTED"
obj = {"schema": "root-current-owned-source-v11-production-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
SPEC = json.loads("{\"qualified_source_software\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/acceptance.json\",\"bytes\":6693,\"sha256\":\"17652a5db832fb36d7df97ebe8279a0de8484041cb3aa91fb0f759ec4d64e4cb\"},\"qualified_original_source6\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_closure.py\",\"bytes\":300159,\"sha256\":\"74cd7b71abdf1202433ca3fbab7f180144926fbaa74916f81535c58bb3afb207\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/test_final_source_closure.py\",\"bytes\":294055,\"sha256\":\"b93f68140e6f0753c3d7f576cd1b108f8e0ab3c95881611ebb9b863d089d8da3\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_cpu.sbatch\",\"bytes\":1679,\"sha256\":\"c46298252a096f2727c749a8362dc55396ef730896336609a5431c37434a61cb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/HANDOFF.md\",\"bytes\":28119,\"sha256\":\"cf361787a35b00ff40ca63abb3910f873dadc7acfcd8100cd81b8b7fbdbdb968\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5269,\"sha256\":\"a363d0202d237c0d35ea5a8e3fb7d6deabdca27bb72916ee56b66b854b9b1da2\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_context_adapter.py\",\"bytes\":19697,\"sha256\":\"fc1caf2e408e95a77026e72f27fab2e2fe2c20e2c07da61888f5fd2dd14f64b6\"}],\"qualified_frozen_source6\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_closure.py\",\"bytes\":300159,\"sha256\":\"74cd7b71abdf1202433ca3fbab7f180144926fbaa74916f81535c58bb3afb207\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/test_final_source_closure.py\",\"bytes\":294055,\"sha256\":\"b93f68140e6f0753c3d7f576cd1b108f8e0ab3c95881611ebb9b863d089d8da3\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_cpu.sbatch\",\"bytes\":1679,\"sha256\":\"c46298252a096f2727c749a8362dc55396ef730896336609a5431c37434a61cb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/HANDOFF.md\",\"bytes\":28119,\"sha256\":\"cf361787a35b00ff40ca63abb3910f873dadc7acfcd8100cd81b8b7fbdbdb968\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5269,\"sha256\":\"a363d0202d237c0d35ea5a8e3fb7d6deabdca27bb72916ee56b66b854b9b1da2\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_context_adapter.py\",\"bytes\":19697,\"sha256\":\"fc1caf2e408e95a77026e72f27fab2e2fe2c20e2c07da61888f5fd2dd14f64b6\"}],\"qualified_source12_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_closure.py\",\"bytes\":300159,\"inode\":144115643443092649,\"mtime_ns\":1792120232000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/test_final_source_closure.py\",\"bytes\":294055,\"inode\":144115643443092650,\"mtime_ns\":1792120659000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_cpu.sbatch\",\"bytes\":1679,\"inode\":144115643443092651,\"mtime_ns\":1792117466000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/HANDOFF.md\",\"bytes\":28119,\"inode\":144115643443092652,\"mtime_ns\":1792120659000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5269,\"inode\":144115643443092653,\"mtime_ns\":1792120232000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1/final_source_context_adapter.py\",\"bytes\":19697,\"inode\":144115643443092654,\"mtime_ns\":1792120010000000000,\"ctime_ns\":1792121074000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_closure.py\",\"bytes\":300159,\"inode\":144115643493459570,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/test_final_source_closure.py\",\"bytes\":294055,\"inode\":144115643493459571,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_cpu.sbatch\",\"bytes\":1679,\"inode\":144115643493459572,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/HANDOFF.md\",\"bytes\":28119,\"inode\":144115643493459573,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5269,\"inode\":144115643493459574,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner/final_source_context_adapter.py\",\"bytes\":19697,\"inode\":144115643493459575,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"qualified_original_source_directory\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix9_parent_diagnostic_history_leaf1\",\"bytes\":4096,\"inode\":144115643443092648,\"mtime_ns\":1792117363000000000,\"ctime_ns\":1792121074000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"qualified_frozen_source_directory\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/runner\",\"bytes\":4096,\"inode\":144115643493459569,\"mtime_ns\":1792122277000000000,\"ctime_ns\":1792122277000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"qualified_software_controls\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/acceptance.json\",\"bytes\":6693,\"sha256\":\"17652a5db832fb36d7df97ebe8279a0de8484041cb3aa91fb0f759ec4d64e4cb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/contracts.json\",\"bytes\":2214,\"sha256\":\"238e578ec3dc30134a290b5ae3f8c626b5fa423055debf598d36dd0aca230e1a\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/contracts.txt\",\"bytes\":57823,\"sha256\":\"a48daf4898c227e63a16d0d9114df72f699f6bfb4493c21052f993e1ddec2e0c\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/source_snapshot.json\",\"bytes\":16095,\"sha256\":\"5e9b4ce1c164f0dbb22ba1152b22a5db0415ecbd23268faeeb80f9697e8f46ae\"}],\"qualified_software_control_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/acceptance.json\",\"bytes\":6693,\"inode\":144115643493469239,\"mtime_ns\":1792122343000000000,\"ctime_ns\":1792122343000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/contracts.json\",\"bytes\":2214,\"inode\":144115643493469237,\"mtime_ns\":1792122343000000000,\"ctime_ns\":1792122343000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/contracts.txt\",\"bytes\":57823,\"inode\":144115643493459576,\"mtime_ns\":1792122343000000000,\"ctime_ns\":1792122343000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_parent_diagnostic_history_software_17015/source_snapshot.json\",\"bytes\":16095,\"inode\":144115643493469238,\"mtime_ns\":1792122343000000000,\"ctime_ns\":1792122343000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"conditional_CORE_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/env/core/bin/python\",\"bytes\":10,\"inode\":144115618512131424,\"mtime_ns\":1790940371000000000,\"ctime_ns\":1790940371000000000,\"mode\":41471,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\",\"bytes\":25916456,\"inode\":144115618512129393,\"mtime_ns\":1790940364000000000,\"ctime_ns\":1790940383000000000,\"mode\":33277,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"source_software_terminal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_parent_diagnostic_history_software17015_actual_terminal_metadata_seal/receipt.json\",\"bytes\":10037419,\"inode\":144115643443092690,\"mtime_ns\":1792122863000000000,\"ctime_ns\":1792122863000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"software_outer_proof\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_parent_diagnostic_history_software_outer_17015/execution_control.json\",\"bytes\":107479,\"sha256\":\"40962234a42b9c2fb4c8587d4823df4f61bdd97bf3b37ff536575fd9d0d20487\"},\"software_outer_proof_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_parent_diagnostic_history_software_outer_17015/execution_control.json\",\"bytes\":107479,\"inode\":144115643493469240,\"mtime_ns\":1792122346000000000,\"ctime_ns\":1792122346000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"plan_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17015_v11/final_source_plan.json\",\"bytes\":2025808,\"inode\":144115643443092692,\"mtime_ns\":1792123307000000000,\"ctime_ns\":1792124063000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17015_v11/HANDOFF.md\",\"bytes\":25668,\"inode\":144115643443092693,\"mtime_ns\":1792123307000000000,\"ctime_ns\":1792124063000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"plan_readonly_seal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v11_from17015_metadata_readonly_seal/receipt.json\",\"bytes\":10039611,\"inode\":144115643443092695,\"mtime_ns\":1792124065000000000,\"ctime_ns\":1792124065000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"current_canonical_Source4\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\",\"bytes\":2225,\"sha256\":\"d602956154fb396fd14d7737c360d7d35144b4e6ca6c3d1c51eb6dc401e42615\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\",\"bytes\":24234,\"sha256\":\"c8fe4495439826f0882b4c43952926e5de5361f88460320cc117d003352ff345\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\",\"bytes\":1633,\"sha256\":\"2d40850d19c7835d658e7154e5a1cb53ae763e31d360b41eec253397f2c5befb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\",\"bytes\":6148,\"sha256\":\"c83e427f73ff1545253d64dbb165c7e60328bb698721d1e03663e6ea7d7c403f\"}],\"current_canonical_Source4_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\",\"bytes\":2225,\"inode\":144115543165691905,\"mtime_ns\":1791727539000000000,\"ctime_ns\":1791727539000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\",\"bytes\":24234,\"inode\":144115543165691892,\"mtime_ns\":1791727495000000000,\"ctime_ns\":1791727495000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\",\"bytes\":1633,\"inode\":144115543165691947,\"mtime_ns\":1791727539000000000,\"ctime_ns\":1791727539000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\",\"bytes\":6148,\"inode\":144115543165691893,\"mtime_ns\":1791727495000000000,\"ctime_ns\":1791727495000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"source_software_terminal_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_parent_diagnostic_history_software17015_actual_terminal_metadata_seal/receipt.json\",\"bytes\":10037419,\"sha256\":\"ff7ee26804bd2376b61793a2c06cb8cd2c5d827f40651e6d4e8f2c2e72434944\"},\"new_request_path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17015_v11/request.json\",\"new_request2_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17015_v11/request.json\",\"bytes\":6550,\"inode\":144115643443092718,\"mtime_ns\":1792126278000000000,\"ctime_ns\":1792126758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17015_v11/request_metadata.json\",\"bytes\":36270,\"inode\":144115643443092719,\"mtime_ns\":1792126278000000000,\"ctime_ns\":1792126758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"new_request_directory_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17015_v11\",\"bytes\":4096,\"inode\":144115643443092717,\"mtime_ns\":1792126278000000000,\"ctime_ns\":1792126758000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"request_readonly_seal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_context_request_from17015_v11_metadata_readonly_seal/receipt.json\",\"bytes\":10070815,\"inode\":144115643443092721,\"mtime_ns\":1792126760000000000,\"ctime_ns\":1792126760000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"plan_own_capture\":{\"bytes\":67754,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v11_ownsha_17016/capture.json\",\"sha256\":\"6330c73f670e947cd0604e2c8862d69ebe8ea9a013191d58114746b6d3563d9a\"},\"plan_own_capture_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v11_ownsha_17016/capture.json\",\"bytes\":67754,\"inode\":144115643493469254,\"mtime_ns\":1792125336000000000,\"ctime_ns\":1792125336000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"plan_own_terminal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v11_ownsha17016_actual_terminal_metadata_seal/receipt.json\",\"bytes\":10069834,\"inode\":144115643443092716,\"mtime_ns\":1792125704000000000,\"ctime_ns\":1792125704000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"root_control_human\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V11_SOURCE_PRODUCTION_FROM17015_17016_20261016_REV1.md\",\"primary_wrap\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_v11_production_from17015_17016_primary_claim/wrap.sh\",\"protected_metadata_union_count\":9583}")
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
# No Source import occurs before all qualified Source12/SW4/Core and twelve own control identities/current readiness.

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
controls=[(qpin,qmeta),(mpin,mmeta),(planpin,planmeta),(hpin,hmeta),(cap_pin,cap_meta),(t7pin,t7meta),(terminalpin,terminalmeta),(outerpin,outermeta),(qropin,qrometa),(planropin,planrometa),(ownhuman,ownhumanmeta),(ownwrap,ownwrapmeta)]
need(len(controls)==len({r["path"]for r,x in controls})==12 and controls==preimport_controls,"Exactly twelve own controls equal preimport byte and metadata bindings required")
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
 need([g.rec(r["path"])for r,x in controls]==[r for r,x in controls]and[md(authority(r["path"]))for r,x in controls]==[x for r,x in controls],"Qualified rec12/postread fullmetadata differs")
 for x in protected.values():need(md(authority(x["path"]))==x,"Finite protected metadata drift")
 for r,x in zip(canonical,canonicalmeta):
  need(md(authority(r["path"]))==x and stat.S_IMODE(x["mode"])==0o664 and x["nlink"]==1 and stat.S_ISREG(x["mode"]),"Only exact canonical4 hash-only leaves allowed")
  need(g.rec(r["path"])==r and md(r["path"])==x,"Canonical4 ownbyte drift")
 need(g.conditional_core_runtime()==runtime,"Qualified current CORE runtime differs")
inputs_end()
OUT=authority(S/"runs")/("final_source_parent_diagnostic_history_audit_"+jid)
AUX=OUT.with_name(OUT.name+"_context_adapter")
PROOF=authority(S/"submissions")/("final_source_parent_diagnostic_history_audit_"+jid+"_root_execution_control")
need(all(not p.exists()and not p.is_symlink()for p in(OUT,AUX,PROOF)),"Exclusive absent audit/AUX/rootproof namespaces required")
adapter=Path(SPEC["qualified_frozen_source6"][-1]["path"])
need(adapter.name=="final_source_context_adapter.py","Exact actual frozen adapter required")
actual_argv=[str(adapter),"--request",str(QP),"--out",str(OUT)]
savedargv=list(sys.argv);phase="actual_frozen_G17015_adapter_mandatory284_producer"
try:
 sys.argv=actual_argv
 try:runpy.run_path(str(adapter),run_name="__main__")
 finally:sys.argv=savedargv
 need(sys.argv==savedargv,"Root process argv lifecycle not restored")
 phase="actual_A_CA_I_C_and_six_finite_preservation_proofs"
 paths=[OUT/"acceptance.json",OUT/"context_adapter_acceptance.json",OUT/"source_inclusion_final.json",OUT/"source_receipt_closure_final.json"]
 output_controls=[ro(p)for p in paths];A,CA,I,C=[read(p)for p in paths]
 need(A["schema"]=="final-source-closure-acceptance.v3"and A["status"]=="FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED"and A["source_issues"]==0 and A["explicit_plan"]==planpin,"Actual new source A scope required")
 need(CA["schema"]=="final-source-materialized-context-read-view-acceptance.v3"and CA["status"]=="FINAL_CURRENT_SOURCE_MATERIALIZED_FIVE_PARENT_CONTEXT_AND_DERIVED_V2_CPU_ACCEPTED_NOT_STAGED_NOT_PUBLISHED"and CA["request"]==qpin and CA["library_software_acceptance"]==SPEC["qualified_source_software"]and CA["actual_new_library_acceptance"]==output_controls[0][0],"Actual new adapter A bindings required")
 need(I["schema"]=="benchmark-source-inclusion.v3"and I["status"]=="SOURCE_INCLUSION_AUDIT_PASS"and I["applied"]is False and I["issues"]==[]and I["source_receipt_closure"]==output_controls[3][0]and I["explicit_plan"]==planpin,"Actual inclusion must be nonstaged/issues0")
 need(C["schema"]=="final-source-receipt-closure.v2"and C["status"]=="EXACT_NEW_SOURCE_DEPENDENCIES_WITH_INHERITED_TYPED_HISTORY","Actual new closure required")
 need(all(x["allocation"]==allocation for x in(A,CA,I)),"Exact current allocation bindings required")
 need(A["source_inclusion"]==CA["source_inclusion"]==output_controls[2][0]and A["source_closure"]==CA["source_closure"]==output_controls[3][0],"Four actual output pointers differ")
 need(len(I["runner_source_snapshot"])==6 and{Path(r["path"]).name for r in I["runner_source_snapshot"]}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Actual new inclusion runner6 required")
 for rows,parent in[(I["runner_source_snapshot"],OUT/"runner"),(A["original_executing_sources"],AUX/"runner"),(CA["source_files"],AUX/"runner"),(CA["original_executing_sources"],adapter.parent)]:
  need(len(rows)==6 and {Path(r["path"]).parent for r in rows}=={parent},"Actual four source6 runner locations differ")
  for r in rows:
   expected=next(v for v in SPEC["qualified_frozen_source6"]if Path(v["path"]).name==Path(r["path"]).name)
   need(g.fp(r)==g.fp(expected),"Actual runner differs from qualified source6")
   output_controls.append(ro(r["path"],r))
 contractpin=A["contracts"];output_controls.append(ro(contractpin["path"],contractpin));contracts=read(contractpin["path"])
 need(contracts["status"]=="PASS"and type(contracts["tests"])is int and contracts["tests"]==284 and contracts["failures"]==0 and contracts["errors"]==0 and contracts["owned_python_compile_PASS"]is True and contracts["bash_syntax_PASS"]is True,"Mandatory actual284 producer/compiler/bash required")
 output_controls.append(ro(contracts["log"]["path"],contracts["log"]))
 log=Path(contracts["log"]["path"]).read_text()
 need(re.findall(r"(?:^|\n)Ran ([0-9]+) tests?\b",log)==["284"]and re.search(r"(?:^|\n)OK(?:\n|$)",log)and not re.search(r"(?:FAIL|ERROR|skipped=|\[SKIP\])",log),"Actual284 contract log must be complete")
 need(contracts["tested_source_files"]==I["runner_source_snapshot"],"Actual284 tested current runner6 required")
 case_lines=[x for x in log.splitlines()if x.startswith("test")]
 named284=re.findall(r"(?m)^(test[^\n]+) \.\.\. ok$",log)
 need(len(case_lines)==len(named284)==len(set(named284))==284 and all(x.endswith(" ... ok")for x in case_lines),"Exactly284 unique namedPASS with no skipped or other test result required")
 qualified_software_log=Path(SPEC["qualified_software_controls"][2]["path"]).read_text()
 qualified_named284=re.findall(r"(?m)^(test[^\n]+) \.\.\. ok$",qualified_software_log)
 need(len(qualified_named284)==len(set(qualified_named284))==284 and named284==qualified_named284,"All actual284 names/classes and order must equal qualified17015 software284")

 output_dirs=[]
 for directory in(OUT/"runner",AUX/"runner"):
  before=md(authority(directory))
  need(stat.S_ISDIR(before["mode"])and stat.S_IMODE(before["mode"])==0o555 and before["nlink"]==2 and{p.name for p in directory.iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Actual two new readonly runner6 directory universes required")
  output_dirs.append(before)
 proof_families=[("vendor_example_opaque_leaf_proof","vendor_example_opaque_aliases",g.verify_vendor_example_preservation),("finite_worker_control_proof","finite_worker_control_aliases",g.verify_finite_worker_preservation),("inventory_history_opaque_leaf_proof","inventory_history_opaque_aliases",g.verify_inventory_history_preservation),("archive_parent_history_opaque_leaf_proof","archive_parent_history_opaque_aliases",g.verify_archive_parent_history_preservation),("relative_diagnostic_history_opaque_leaf_proof","relative_diagnostic_history_opaque_aliases",g.verify_relative_diagnostic_history_preservation),("parent_diagnostic_history_opaque_leaf_proof","parent_diagnostic_history_opaque_aliases",g.verify_parent_diagnostic_history_preservation)]
 proof_objects=[]
 for pkey,ikey,verify_family in proof_families:
  pp=A[pkey];ip=A[ikey]
  need(all(x[pkey]==pp and x[ikey]==ip for x in(CA,I,C)),"A/CA/I/C finite preservation pointers differ")
  output_controls.extend([ro(pp["path"],pp),ro(ip["path"],ip)])
  proof,index=read(pp["path"]),read(ip["path"])
  need(proof["exact_alias_index"]==ip,"Finite proof index binding differs")
  verify_family(proof,index,allocation)
  proof_objects.append((proof,index,verify_family))
 g.inventory_history_proof_shape(proof_objects[2][0],proof_objects[2][1],allocation)
 g.archive_parent_history_proof_shape(proof_objects[3][0],proof_objects[3][1],allocation)
 g.relative_diagnostic_history_proof_shape(proof_objects[4][0],proof_objects[4][1],allocation)
 g.parent_diagnostic_history_proof_shape(proof_objects[5][0],proof_objects[5][1],allocation)
 g.parent_diagnostic_history_source_coverage(proof_objects[5][0],C,I)
 need(all(x.get("source_staged")is False and x.get("ACTIVE_changed")is False for x in(A,CA,I)),"No Source stage or promotion allowed")
 def graph_full_readback():
  final_graph=[read(r["path"])for r,x in output_controls[:4]]
  need(all(g.exact_json(got,want)for got,want in zip(final_graph,[A,CA,I,C])),"All four actual output objects changed after final graph JSON read")
  g.parent_diagnostic_history_source_coverage(proof_objects[5][0],final_graph[3],final_graph[2])
  for r,x in output_controls[:4]:ro(r["path"],r,x)
 def outputs_end():
  graph_full_readback()
  for x in output_dirs:need(md(authority(x["path"]))==x and{p.name for p in Path(x["path"]).iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Actual new runner6 directory metadata/universe drift")
  for r,x in output_controls:ro(r["path"],r,x)
  for p,i,f in proof_objects:f(p,i,allocation)
  graph_full_readback()
  for r,x in output_controls:ro(r["path"],r,x)
  for x in output_dirs:need(md(authority(x["path"]))==x and{p.name for p in Path(x["path"]).iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Actual new runner6 directories drift after finite proof verification")
 outputs_end();inputs_end()
 phase="exclusive_final_root_execution_proof_no_staging"
 PROOF.mkdir(mode=0o755)
 result=dict(schema="root-actual-final-source-v11-production-execution-control.v1",status="ROOT_ACTUAL_NEW_SOURCE284_A_CA_I_C_AND_SIX_FINITE_PRESERVATION_PROOFS_CPU_VERIFIED_NOT_STAGED_NOT_PUBLISHED",actual_job_id=jid,allocation=allocation,current_actual_readiness=readiness,current_readiness_own_CPU_receipts=[r for r,x in readyvalues],actual_direct_frozen_adapter_argv=actual_argv,actual_new_library_acceptance=output_controls[0][0],actual_new_adapter_acceptance=output_controls[1][0],actual_new_inclusion=output_controls[2][0],actual_new_closure=output_controls[3][0],actual_new_runner_source_snapshot=I["runner_source_snapshot"],qualified_software_acceptance=SPEC["qualified_source_software"],qualified_source12=sourcepins,qualified_source12_metadata=source_meta,actual_own_pinned_Source17_rows=added_source_rows,actual_own_pinned_Source17_metadata=added_source_metadata,historical_Source2_and_launcher_hash_only_never_imported_compiled_or_executed_by_Root=True,qualified_software4=SPEC["qualified_software_controls"],conditional_core_runtime=runtime,control_receipts=[r for r,x in controls],control_metadata_before=[x for r,x in controls],control_metadata_after=[md(r["path"])for r,x in controls],current_canonical_Source4_receipts=canonical,current_canonical_Source4_metadata_before=canonicalmeta,current_canonical_Source4_metadata_after=[md(r["path"])for r in canonical],protected_input_metadata_unique=len(protected),mandatory_contracts=contractpin,mandatory_284_producer_PASS=True,mandatory_284_unique_named_PASS_no_failure_error_skip=True,mandatory_284_named_tests=named284,mandatory_284_named_cases_and_order_equal_qualified_software284=True,actual_new_runner6_directory_metadata=output_dirs,qualified_G17015_rec_all12_and_postread_metadata_PASS=True,actual_current_source_and_runtime_pre_end_after_final_readonly_PASS=True,all_A_CA_I_C_finite_proof_alias_pointers_equal=True,exact_six_finite_preservation_validators_three_arguments_PASS=True,parent_diagnostic_Source2_ordinary_C_I_actual_coverage_PASS=True,parent_diagnostic_all4_graph_fullobjects_afterlastJSON_PASS=True,output_artifact_receipts=[r for r,x in output_controls],output_artifact_metadata=[x for r,x in output_controls],request_own_cpu_tuple=qpin,metadata_own_cpu_tuple=mpin,Root_Human_and_precreated_shell_own_CPU_tuples=[ownhuman,ownwrap],source_staged=False,published=False,ACTIVE_changed=False,raw_JSON_changed=False,scientific_endpoint_acceptance_performed=False,own_created_controls_LATE_not_Plan_prerequisites=True,qualification_requires_fresh_actual_terminal_Root_plus_two_content_and_independent_RO=True)
 raw=(json.dumps(result,indent=2,allow_nan=False,ensure_ascii=False)+"\n").encode();rp=PROOF/"execution_control.json"
 with rp.open("xb")as f:f.write(raw);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444);os.fsync(f.fileno())
 proofmeta=md(rp);proofpin=g.rec(rp);need(md(rp)==proofmeta,"First owned root proof prehash fullmetadata must remain stable")
 need(rp.read_bytes()==raw and read(rp)==result and stat.S_IMODE(proofmeta["mode"])==0o444 and proofmeta["nlink"]==1,"Whole own final proof readonly reread required")
 outputs_end();inputs_end();PROOF.chmod(0o555)
 fd=os.open(str(PROOF),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
 finaldir=md(authority(PROOF))
 need(stat.S_IMODE(finaldir["mode"])==0o555 and finaldir["nlink"]==2 and{p.name for p in PROOF.iterdir()}=={"execution_control.json"}and rp.read_bytes()==raw and read(rp)==result and g.rec(rp)==proofpin and md(rp)==proofmeta,"Final own proof exact readonly universe required")
 outputs_end();inputs_end()
 for receipt,metadata in output_controls:need(md(authority(receipt["path"]))==metadata,"Final all output fullmetadata after last input/Core operations differs")
 for directory in output_dirs:need(md(authority(directory["path"]))==directory and{p.name for p in Path(directory["path"]).iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Final actual runner6 directory metadata/universe after last inputs differs")
 need(md(PROOF)==finaldir and md(rp)==proofmeta,"Final own proof metadata after all input/output checks differs")
 print(json.dumps(dict(status=result["status"],execution_control=proofpin,acceptance=output_controls[0][0],context_adapter_acceptance=output_controls[1][0],inclusion=output_controls[2][0],closure=output_controls[3][0],actual_new_runner_source_snapshot=I["runner_source_snapshot"],request=qpin,request_metadata=mpin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,qualification_still_requires_fresh_terminal_and_full_Root_two_independent_readbacks=True),sort_keys=True),flush=True)
except BaseException as e:
 try:
  if not PROOF.exists():PROOF.mkdir(mode=0o755)
  if stat.S_IMODE(PROOF.stat().st_mode)&0o222:
   fail=(json.dumps(dict(schema="root-final-source-v11-production-incomplete.v1",status="ROOT_FINAL_SOURCE_V11_PRODUCTION_UNQUALIFIED_NO_STAGING",actual_job_id=jid,phase=phase,reason_type=type(e).__name__,reason=str(e),actual_argv=actual_argv,source_staged=False,published=False,ACTIVE_changed=False),indent=2)+"\n").encode()
   with(PROOF/"typed_incomplete.json").open("xb")as f:f.write(fail);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 except Exception as se:print("Failure proof best-effort "+repr(se),file=sys.stderr,flush=True)
 raise

PY
