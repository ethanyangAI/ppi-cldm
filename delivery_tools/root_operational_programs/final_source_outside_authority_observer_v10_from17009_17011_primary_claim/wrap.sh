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
D = S / "submissions" / ("source_outside_authority_v10_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_final_source_outside_authority_observer_v10", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-source-v10-outside-authority-observer-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_SOURCE_V10_OUTSIDE_AUTHORITY_OBSERVER_AUDIT_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_SOURCE_V10_OUTSIDE_AUTHORITY_OBSERVER_AUDIT_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_SOURCE_V10_OUTSIDE_AUTHORITY_OBSERVER_AUDIT_NOT_EXECUTED"
obj = {"schema": "root-current-owned-source-v10-outside-authority-observer-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
SPEC = json.loads("{\"qualified_source_software\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/acceptance.json\", \"bytes\": 6724, \"sha256\": \"4ca2851722ca1c9423e65ea0c787880bd6a99026c9649a32183ce937b949fcc7\"}, \"qualified_original_source6\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix8_relative_diagnostic_history_leaf1/final_source_closure.py\", \"bytes\": 257679, \"sha256\": \"2578d4b88f669516fb2f0fdf7916c7af707e51fdd37e88baebcef0900602163c\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix8_relative_diagnostic_history_leaf1/test_final_source_closure.py\", \"bytes\": 210569, \"sha256\": \"faf7cdef1f50665062dc05af869c978e048f1c5bb802ba4a302cd462e9207ff6\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix8_relative_diagnostic_history_leaf1/final_source_cpu.sbatch\", \"bytes\": 1693, \"sha256\": \"51b585305c4cc16872e825d75dc04bde127b0b56a99d4b0043be59ecd72cdab1\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix8_relative_diagnostic_history_leaf1/HANDOFF.md\", \"bytes\": 18168, \"sha256\": \"891d4a401db6f3e83b04ba125bc1b45a552b3756fe152a19fa3784103797b20b\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix8_relative_diagnostic_history_leaf1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3561, \"sha256\": \"144d195372a6e1540a74aec335b98bf76ce620f295fce38e1cb81299f5e93023\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix8_relative_diagnostic_history_leaf1/final_source_context_adapter.py\", \"bytes\": 14700, \"sha256\": \"444e7604252f952a936c70cc6167662471f1936cd7c358d4d14c575c1fad1353\"}], \"qualified_frozen_source6\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/runner/final_source_closure.py\", \"bytes\": 257679, \"sha256\": \"2578d4b88f669516fb2f0fdf7916c7af707e51fdd37e88baebcef0900602163c\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/runner/test_final_source_closure.py\", \"bytes\": 210569, \"sha256\": \"faf7cdef1f50665062dc05af869c978e048f1c5bb802ba4a302cd462e9207ff6\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/runner/final_source_cpu.sbatch\", \"bytes\": 1693, \"sha256\": \"51b585305c4cc16872e825d75dc04bde127b0b56a99d4b0043be59ecd72cdab1\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/runner/HANDOFF.md\", \"bytes\": 18168, \"sha256\": \"891d4a401db6f3e83b04ba125bc1b45a552b3756fe152a19fa3784103797b20b\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3561, \"sha256\": \"144d195372a6e1540a74aec335b98bf76ce620f295fce38e1cb81299f5e93023\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/runner/final_source_context_adapter.py\", \"bytes\": 14700, \"sha256\": \"444e7604252f952a936c70cc6167662471f1936cd7c358d4d14c575c1fad1353\"}], \"qualified_source12_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix8_relative_diagnostic_history_leaf1/final_source_closure.py\", \"bytes\": 257679, \"inode\": 144115643443092523, \"mtime_ns\": 1792109003000000000, \"ctime_ns\": 1792109730000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix8_relative_diagnostic_history_leaf1/test_final_source_closure.py\", \"bytes\": 210569, \"inode\": 144115643443092524, \"mtime_ns\": 1792109104000000000, \"ctime_ns\": 1792109730000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix8_relative_diagnostic_history_leaf1/final_source_cpu.sbatch\", \"bytes\": 1693, \"inode\": 144115643443092525, \"mtime_ns\": 1792108739000000000, \"ctime_ns\": 1792109730000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix8_relative_diagnostic_history_leaf1/HANDOFF.md\", \"bytes\": 18168, \"inode\": 144115643443092526, \"mtime_ns\": 1792108967000000000, \"ctime_ns\": 1792109730000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix8_relative_diagnostic_history_leaf1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3561, \"inode\": 144115643443092527, \"mtime_ns\": 1792108901000000000, \"ctime_ns\": 1792109730000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix8_relative_diagnostic_history_leaf1/final_source_context_adapter.py\", \"bytes\": 14700, \"inode\": 144115643443092528, \"mtime_ns\": 1792108739000000000, \"ctime_ns\": 1792109730000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/runner/final_source_closure.py\", \"bytes\": 257679, \"inode\": 144115643493450412, \"mtime_ns\": 1792110490000000000, \"ctime_ns\": 1792110490000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/runner/test_final_source_closure.py\", \"bytes\": 210569, \"inode\": 144115643493450413, \"mtime_ns\": 1792110490000000000, \"ctime_ns\": 1792110490000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/runner/final_source_cpu.sbatch\", \"bytes\": 1693, \"inode\": 144115643493450414, \"mtime_ns\": 1792110490000000000, \"ctime_ns\": 1792110490000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/runner/HANDOFF.md\", \"bytes\": 18168, \"inode\": 144115643493450415, \"mtime_ns\": 1792110490000000000, \"ctime_ns\": 1792110490000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3561, \"inode\": 144115643493450416, \"mtime_ns\": 1792110490000000000, \"ctime_ns\": 1792110490000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/runner/final_source_context_adapter.py\", \"bytes\": 14700, \"inode\": 144115643493450417, \"mtime_ns\": 1792110490000000000, \"ctime_ns\": 1792110490000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"qualified_original_source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix8_relative_diagnostic_history_leaf1\", \"bytes\": 4096, \"inode\": 144115643443092522, \"mtime_ns\": 1792108578000000000, \"ctime_ns\": 1792109730000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"qualified_frozen_source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/runner\", \"bytes\": 4096, \"inode\": 144115643493450411, \"mtime_ns\": 1792110490000000000, \"ctime_ns\": 1792110490000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"qualified_software_controls\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/acceptance.json\", \"bytes\": 6724, \"sha256\": \"4ca2851722ca1c9423e65ea0c787880bd6a99026c9649a32183ce937b949fcc7\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/contracts.json\", \"bytes\": 2228, \"sha256\": \"a69acd857d9442e0ae2f30226b22bef206699998d921e78be8ad032439c22001\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/contracts.txt\", \"bytes\": 46440, \"sha256\": \"57268b64d71761e01d344c2ca4164d2decc86f37e8300b58964d58a6d3bb1d80\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/source_snapshot.json\", \"bytes\": 16169, \"sha256\": \"012676e56921c784d9d1b6089b377aaa4a8e1203b077e1fd0d64fa5fe50d00a9\"}], \"qualified_software_control_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/acceptance.json\", \"bytes\": 6724, \"inode\": 144115643493457364, \"mtime_ns\": 1792110529000000000, \"ctime_ns\": 1792110529000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/contracts.json\", \"bytes\": 2228, \"inode\": 144115643493457362, \"mtime_ns\": 1792110529000000000, \"ctime_ns\": 1792110529000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/contracts.txt\", \"bytes\": 46440, \"inode\": 144115643493450418, \"mtime_ns\": 1792110529000000000, \"ctime_ns\": 1792110529000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_relative_diagnostic_history_software_17009/source_snapshot.json\", \"bytes\": 16169, \"inode\": 144115643493457363, \"mtime_ns\": 1792110529000000000, \"ctime_ns\": 1792110529000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"conditional_CORE_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python\", \"bytes\": 10, \"inode\": 144115618512131424, \"mtime_ns\": 1790940371000000000, \"ctime_ns\": 1790940371000000000, \"mode\": 41471, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\", \"bytes\": 25916456, \"inode\": 144115618512129393, \"mtime_ns\": 1790940364000000000, \"ctime_ns\": 1790940383000000000, \"mode\": 33277, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"source_software_terminal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_relative_diagnostic_history_software17009_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 7522392, \"inode\": 144115643443092556, \"mtime_ns\": 1792110893000000000, \"ctime_ns\": 1792110893000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"software_outer_proof\": {\"bytes\": 79363, \"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_relative_diagnostic_history_software_outer_17009/execution_control.json\", \"sha256\": \"7c1a66592c8f5b733155aa436df7c9e3c95c20b2f6e6465632201ca9a9c50204\"}, \"software_outer_proof_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_relative_diagnostic_history_software_outer_17009/execution_control.json\", \"bytes\": 79363, \"inode\": 144115643493457365, \"mtime_ns\": 1792110531000000000, \"ctime_ns\": 1792110531000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"plan_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17009_v10/final_source_plan.json\", \"bytes\": 2010925, \"inode\": 144115643443092558, \"mtime_ns\": 1792111380000000000, \"ctime_ns\": 1792111647000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17009_v10/HANDOFF.md\", \"bytes\": 30810, \"inode\": 144115643443092559, \"mtime_ns\": 1792111380000000000, \"ctime_ns\": 1792111647000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"plan_readonly_seal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v10_from17009_metadata_readonly_seal/receipt.json\", \"bytes\": 7524472, \"inode\": 144115643443092561, \"mtime_ns\": 1792111648000000000, \"ctime_ns\": 1792111648000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"current_canonical_Source4\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\", \"bytes\": 2225, \"sha256\": \"d602956154fb396fd14d7737c360d7d35144b4e6ca6c3d1c51eb6dc401e42615\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\", \"bytes\": 24234, \"sha256\": \"c8fe4495439826f0882b4c43952926e5de5361f88460320cc117d003352ff345\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\", \"bytes\": 1633, \"sha256\": \"2d40850d19c7835d658e7154e5a1cb53ae763e31d360b41eec253397f2c5befb\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\", \"bytes\": 6148, \"sha256\": \"c83e427f73ff1545253d64dbb165c7e60328bb698721d1e03663e6ea7d7c403f\"}], \"current_canonical_Source4_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\", \"bytes\": 2225, \"inode\": 144115543165691905, \"mtime_ns\": 1791727539000000000, \"ctime_ns\": 1791727539000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\", \"bytes\": 24234, \"inode\": 144115543165691892, \"mtime_ns\": 1791727495000000000, \"ctime_ns\": 1791727495000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\", \"bytes\": 1633, \"inode\": 144115543165691947, \"mtime_ns\": 1791727539000000000, \"ctime_ns\": 1791727539000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\", \"bytes\": 6148, \"inode\": 144115543165691893, \"mtime_ns\": 1791727495000000000, \"ctime_ns\": 1791727495000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"source_software_terminal_receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_relative_diagnostic_history_software17009_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 7522392, \"sha256\": \"630ab2154fe6416cac8b9b5acf1e30c989deee9d7c89b7a7f518823be1aea1bd\"}, \"new_request_path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17009_v10/request.json\", \"new_request2_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17009_v10/request.json\", \"bytes\": 6552, \"inode\": 144115643443092582, \"mtime_ns\": 1792112863000000000, \"ctime_ns\": 1792113138000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17009_v10/request_metadata.json\", \"bytes\": 25652, \"inode\": 144115643443092583, \"mtime_ns\": 1792112863000000000, \"ctime_ns\": 1792113138000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"new_request_directory_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17009_v10\", \"bytes\": 4096, \"inode\": 144115643443092581, \"mtime_ns\": 1792112863000000000, \"ctime_ns\": 1792113138000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"request_readonly_seal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_context_request_from17009_v10_metadata_readonly_seal/receipt.json\", \"bytes\": 7554490, \"inode\": 144115643443092585, \"mtime_ns\": 1792113139000000000, \"ctime_ns\": 1792113139000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"plan_own_capture\": {\"bytes\": 62672, \"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v10_ownsha_17010/capture.json\", \"sha256\": \"2238eb3fbe6980a8699f910a2994348b6cc36dabdb2931dddd8bf3d4fb49fb9b\"}, \"plan_own_capture_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v10_ownsha_17010/capture.json\", \"bytes\": 62672, \"inode\": 144115643493457377, \"mtime_ns\": 1792112305000000000, \"ctime_ns\": 1792112305000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"plan_own_terminal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_plan_v10_ownsha17010_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 7567104, \"inode\": 144115643443092580, \"mtime_ns\": 1792112609000000000, \"ctime_ns\": 1792112609000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"root_control_human\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V10_OUTSIDE_AUTHORITY_FAILURE_OBSERVER_FROM17009_17011_20261016_REV1.md\", \"primary_wrap\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_outside_authority_observer_v10_from17009_17011_primary_claim/wrap.sh\", \"protected_metadata_union_count\": 7229, \"failed17011_terminal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_relative_diagnostic_history_audit17011_actual_failed_terminal_metadata_seal/receipt.json\", \"bytes\": 8831286, \"inode\": 144115643443092620, \"mtime_ns\": 1792115255000000000, \"ctime_ns\": 1792115255000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}}")
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
need(a["source_files"]==SPEC["qualified_frozen_source6"]and a["original_executing_sources"]==SPEC["qualified_original_source6"]and a["allocation"]["job_id"]=="17009","Actual software17009 Source6 bindings required")
terminalpath=Path(SPEC["source_software_terminal_metadata"]["path"])
terminalpin,terminalmeta=ro(terminalpath,SPEC["source_software_terminal_receipt"],SPEC["source_software_terminal_metadata"])
terminal=read(terminalpath)
need(terminal["schema"]=="root-final-source-relative-diagnostic-history-software17009-terminal-metadata-seal.v1"and terminal["actual_job_id"]=="17009"and terminal["Root_plus_two_whole_actual_software238_content_READBACK_PASS"]is True and terminal["actual_unique_named_tests"]==238 and terminal["historical198_names_and_relative_order_preserved"]is True and terminal["new40_actual_relative_diagnostic_history_contracts_PASS"]is True and terminal["actual_GPU0_from_current_readiness"]is True,"Actual accepted17009 terminal software238 context required")
need(len(terminal)==32 and[terminal[k]for k in["actual_software_acceptance","actual_contracts","actual_contract_log","actual_source_snapshot"]]==SPEC["qualified_software_controls"]and terminal["fresh_terminal"]["returncode"]==0 and terminal["fresh_terminal"]["raw_stderr"]==""and terminal["fresh_terminal"]["numeric_9column_row"]==["17009","COMPLETED","0:0","51","1","test9_final_source_relative_diagnostic_history_v3","u21111210118","u21111210118","organ"],"Exact qualified17009 software controls and actual terminal row required")
# All twelve exact own control bytes are also guarded with stdlib before the first project import.
pre_cap_pin,pre_cap_md=ro(SPEC["plan_own_capture"]["path"],SPEC["plan_own_capture"],SPEC["plan_own_capture_metadata"])
pre_cap=read(pre_cap_pin["path"])
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
ss=importlib.util.spec_from_file_location("root_qualified_source17009_production_control",entry)
g=importlib.util.module_from_spec(ss);ss.loader.exec_module(g)
need(g.software_shape(a,ct)==SPEC["qualified_frozen_source6"],"Unchanged qualified Source software shape required")
allocation=g.cpu();runtime=g.conditional_core_runtime()
need(allocation["job_id"]==jid and allocation["allocated_CPUs"]==1 and allocation["allocated_gpus"]==0 and allocation["numeric_sacct_row"]==attempts[selected-1]["actual_row"]and runtime==a["conditional_core_runtime"],"Actual fresh Source current CPU/Core required")
snapshot=read(SPEC["qualified_software_controls"][3]["path"])
need(g.software_snapshot_shape(a,snapshot)==snapshot,"Actual qualified software six snapshot required")

QP=Path(SPEC["new_request_path"]);MP=QP.with_name("request_metadata.json")
QRO=Path(SPEC["request_readonly_seal_metadata"]["path"])
qropin,qrometa=ro(QRO,metadata=SPEC["request_readonly_seal_metadata"]);qr=read(QRO)
need(qr["schema"]=="root-new-plan-v10-strict13-request-metadata-readonly-seal.v1"and qr["Root_and_two_independent_whole_Q_and_metadata_static_PASS"]is True,"Actual reviewed strict13 QRO required")
need(qr["after_files"]==SPEC["new_request2_metadata"]and qr["after_directory"]==SPEC["new_request_directory_metadata"],"Exact readonly Q2/P metadata required")
qpin,qmeta=ro(QP,metadata=SPEC["new_request2_metadata"][0]);mpin,mmeta=ro(MP,metadata=SPEC["new_request2_metadata"][1])
q=read(QP);m=read(MP)
cap_pin,cap_meta=ro(SPEC["plan_own_capture"]["path"],SPEC["plan_own_capture"],SPEC["plan_own_capture_metadata"])
cap=read(cap_pin["path"])
t7pin,t7meta=ro(SPEC["plan_own_terminal_metadata"]["path"],metadata=SPEC["plan_own_terminal_metadata"])
t7=read(t7pin["path"])
need(t7["schema"]=="root-plan-v10-ownsha17010-terminal-metadata-seal.v1"and t7["actual_job_id"]=="17010"and t7["Root_plus_two_whole_actual_content_READBACK_PASS"]is True and t7["actual_CPU_final_descriptor"]["capture"]==cap_pin,"Actual qualified Plan ownSHA17010 terminal required")
need(t7["fresh_terminal"]["returncode"]==0 and t7["fresh_terminal"]["raw_stderr"]==""and t7["fresh_terminal"]["numeric_9column_row"]==["17010","COMPLETED","0:0","10","1","test9_source_plan_v10_ownsha_cpu","u21111210118","u21111210118","organ"],"Actual ownPlan17010 terminal row required")
planpin,planmeta=ro(cap["plan"]["path"],cap["plan"],SPEC["plan_metadata"][0]);hpin,hmeta=ro(cap["handoff"]["path"],cap["handoff"],SPEC["plan_metadata"][1])
plan=read(planpin["path"])
need(q["final_source_plan"]==planpin and q["library_software_acceptance"]==SPEC["qualified_source_software"]==plan["library_software_acceptance"]and q["mapper_software_acceptance"]==plan["mapper_software_acceptance"],"Exact Q/actual17009/V10Plan software bindings required")
need(len(q)==13 and list(q)==m["exact13_key_order"]and q["root_owned"]is True and len(q["finite_source_parent_aliases"])==8 and len(plan["context_parent_seeds"])==17 and len(plan["aliases"])==7,"Exact strict13/finite8/17/7 request required")
for k in("raw_JSON_rewrite_allowed","generic_relative_resolution_allowed","generic_external_resolution_allowed"):need(q[k]is False,"No generic permission granted")
for k in("bbf_parent_aliases","historical_parent_aliases","recovered_parent_aliases","archive_parent_aliases"):need(type(q[k])is list and q[k]==[],"No generic parent alias added")
need(cap["actual_job_id"]=="17010"and cap["Source_n"]==716 and cap["destination_n"]==655 and cap["seed_n"]==3901 and cap["unique_seed_n"]==3828 and cap["role_n"]==9 and cap["parent_n"]==17 and cap["source_audit_executed"]is False,"Actual newPlan716/655/3901/3828/9/17 scope required")
need(g.module_plan(plan)==plan["modules"],"Qualified pure-shape module plan required")
need(m["root_and_two_independent_actual17010_content_readback_PASS"]is True and m["root_and_independent_actual17010_terminal_RO_readback_PASS"]is True and m["accepted_Plan"]==planpin and m["accepted_Plan_HANDOFF"]==hpin and m["actual17010_Plan_own_capture"]==cap_pin,"Whole qualified17010 metadata bindings required")
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
 need([g.rec(r["path"])for r,x in controls]==[r for r,x in controls]and[md(authority(r["path"]))for r,x in controls]==[x for r,x in controls],"Qualified rec12/postread fullmetadata differs")
 for x in protected.values():need(md(authority(x["path"]))==x,"Finite protected metadata drift")
 for r,x in zip(canonical,canonicalmeta):
  need(md(authority(r["path"]))==x and stat.S_IMODE(x["mode"])==0o664 and x["nlink"]==1 and stat.S_ISREG(x["mode"]),"Only exact canonical4 hash-only leaves allowed")
  need(g.rec(r["path"])==r and md(r["path"])==x,"Canonical4 ownbyte drift")
 need(g.conditional_core_runtime()==runtime,"Qualified current CORE runtime differs")
inputs_end()

# Read only the fixed actual failed17011 control, never the unobserved bad target.
failed_path=Path(SPEC["failed17011_terminal_metadata"]["path"])
failed_pin,failed_meta=ro(failed_path,metadata=SPEC["failed17011_terminal_metadata"])
failed=read(failed_path)
need(len(failed)==37 and failed["actual_job_id"]=="17011"and failed["actual_238_unique_named_PASS"]is True and failed["actual_offending_receipt_parent_physical_trail_and_module_UNOBSERVED"]is True and failed["fresh_terminal"]["numeric_9column_row"]==["17011","FAILED","1:0","331","1","test9_final_source_relative_diagnostic_history_v3","u21111210118","u21111210118","organ"],"Actual failed17011 unqualified history required")
need(failed["protected_inputs_before"]==failed["protected_inputs_after"]and len(failed["protected_inputs_after"])==7262 and len(failed["after_files"])==1077 and len(failed["after_directories"])==13,"Exact actual failed17011 preservation bounds required")
failed_protected={}
for x in failed["protected_inputs_after"]+failed["after_files"]+failed["after_directories"]+[md(failed_path),md(failed_path.parent)]:
 if x["path"]in failed_protected:need(failed_protected[x["path"]]==x,"No conflicting failed17011 history metadata")
 failed_protected[x["path"]]=x
need(len(failed_protected)==8354,"Exact failed17011 protected finite union8354 required")
controls.append((failed_pin,failed_meta))
need(len(controls)==len({r["path"]for r,x in controls})==13,"Exactly13 own observer controls required")
def observer_inputs_end():
 inputs_end()
 for x in failed_protected.values():need(md(authority(x["path"]))==x,"Failed17011 history full native metadata drift")
observer_inputs_end()
OUT=authority(S/"runs")/("final_source_outside_authority_observer_v10_"+jid)
AUX=OUT.with_name(OUT.name+"_context_adapter")
PROOF=authority(S/"submissions")/("source_outside_authority_observer_v10_"+jid)
need(all(not p.exists()and not p.is_symlink()for p in[OUT,AUX,PROOF]),"Exclusive absent diagnostic output namespaces required")
adapter=Path(SPEC["qualified_frozen_source6"][-1]["path"])
actual_argv=[str(adapter),"--request",str(QP),"--out",str(OUT)]
savedargv=list(sys.argv)
try:
 sys.argv=actual_argv
 try:runpy.run_path(str(adapter),run_name="__main__")
 finally:sys.argv=savedargv
except ValueError as original_error:
 need(sys.argv==savedargv and type(original_error)is ValueError and str(original_error)=="Receipt outside authority","Exact original outside-authority ValueError required")
 new_source_rows=[];new_source_meta=[];new_source_dirs=[]
 for folder in[OUT/"runner",AUX/"runner"]:
  dm=md(authority(folder));need(dm["mode"]==stat.S_IFDIR|0o555 and dm["nlink"]==2 and {p.name for p in folder.iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Actual new diagnostic frozen6 directory required")
  new_source_dirs.append(dm)
  for expected in SPEC["qualified_frozen_source6"]:
   p=folder/Path(expected["path"]).name;rr,mm=ro(p)
   need((rr["bytes"],rr["sha256"])==(expected["bytes"],expected["sha256"]),"Actual observed executable source must match qualifiedG17009")
   new_source_rows.append(rr);new_source_meta.append(mm)
 observer_inputs_end()
 OBS_MODULES={"formal13260_terminal_v3","native74_cache_catalog","native74_cache_binding","reference_free_e2e","formal_common_review","independent_statistics","scientific_report","final_delivery_tools","default_workflow_integration","EXACT_ACCEPTED_CONTEXT_PARENT"}
 observed_code_file=str(AUX/"runner/final_source_closure.py")
 source_frames=[];tb=original_error.__traceback__
 while tb is not None:
  frame=tb.tb_frame
  if frame.f_code.co_filename==observed_code_file:source_frames.append((frame,tb.tb_lineno))
  tb=tb.tb_next
 expected_chain=[("audit",3825),("resolve",3742),("verify",63),("safe_path",59),("need",40)]
 need([(f.f_code.co_name,line)for f,line in source_frames]==expected_chain,"Unique exact outside-authority frame chain required")
 af,rf,vf,sf,nf=[f for f,line in source_frames]
 need([f.f_code.co_qualname for f in[af,rf,vf,sf,nf]]==["audit","audit.<locals>.resolve","verify","safe_path","need"],"Exact authenticated function qualifications required")
 need(all(f.f_globals is af.f_globals for f in[rf,vf,sf,nf]),"All authenticated functions must share actual qualified module globals")
 need({"r","parent","trail","module","stage","resolve"}<=af.f_locals.keys()and {"r","aliases"}<=rf.f_locals.keys()and {"r","readonly"}<=vf.f_locals.keys()and "p"in sf.f_locals,"Actual declared frame locals required")
 need(getattr(af.f_locals.get("resolve"),"__code__",None)is rf.f_code,"Actual nested audit resolver required")
 for frame,name in[(af,"audit"),(vf,"verify"),(sf,"safe_path"),(nf,"need")]:
  need(getattr(frame.f_globals.get(name),"__code__",None)is frame.f_code,"Authenticated global source function required")
 need(nf.f_locals.get("v")is False and nf.f_locals.get("msg")=="Receipt outside authority"and sf.f_globals.get("R")==R,"Actual original need40/source authority required")
 ar=af.f_locals["r"];rr=rf.f_locals["r"];vr=vf.f_locals["r"]
 need(type(ar)is dict and ar is rr and rr is vr,"Audit resolve verify must carry SAME actual receipt object")
 need({"path","bytes","sha256"}<=ar.keys()and all(type(k)is str and len(k)<=8192 for k in ar),"Required receipt scalar fields and bounded key names")
 raw_path=ar["path"];byte_n=ar["bytes"];sha=ar["sha256"]
 need(type(raw_path)is str and len(raw_path)<=8192 and Path(raw_path).is_absolute(),"Already-shaped absolute string receipt path required")
 need(type(byte_n)is int and byte_n>=0 and type(sha)is str and re.fullmatch("[0-9a-f]{64}",sha)is not None,"Already-shaped nonboolean bytes and exact SHA scalar required")
 need(vf.f_locals["readonly"]is False,"Exact verify(r) fallback invocation required")
 extra_names=sorted(k for k in ar if k not in{"path","bytes","sha256"});need(len(extra_names)<=256,"Bounded extra key names only")
 # Every operation on lexical_p/raw_path below is purely lexical. Never target IO.
 lexical_p=sf.f_locals["p"]
 need(type(lexical_p)is type(Path("/"))and lexical_p==Path(raw_path),"Actual safe_path lexical Path matches raw receipt string")
 need(lexical_p.is_absolute()and not lexical_p.is_relative_to(R),"Exact lexical outside-authority branch required")
 aliases=rf.f_locals["aliases"]
 need(type(aliases)is dict and(raw_path,sha,byte_n)not in aliases,"Actual resolve3742 exact alias lookup MISS required")
 parent=af.f_locals["parent"]
 need(parent is None or(type(parent)is str and len(parent)<=8192),"Actual parent must be None or bounded string")
 trail=af.f_locals["trail"]
 need(type(trail)is tuple and len(trail)<=256 and all(type(x)is str and len(x)<=8192 for x in trail),"Actual bounded audit trail required")
 module=af.f_locals["module"];stage=af.f_locals["stage"]
 need(type(module)is str and module in OBS_MODULES and type(stage)is str and stage=="recursive_exact_new_dependencies","Actual existing module or context annotation and recursive stage required")
 # Do not read audit physical/basis/obj or verify p: each may be from a prior loop.
 offender=dict(path=dict(type="str",value=raw_path),bytes=dict(type="int",value=byte_n),sha256=dict(type="str",value=sha),extra_key_names=extra_names)
 context=dict(parent_path=parent,trail=list(trail),module=module,stage=stage)
 ctpin,ctmeta=ro(OUT/"contracts.json");ct=read(ctpin["path"]);logpin,logmeta=ro(ct["log"]["path"],ct["log"]);log=Path(logpin["path"]).read_text()
 named=re.findall(r"(?m)^(test[^\n]+) \.\.\. ok$",log)
 need(ct["status"]=="PASS"and ct["tests"]==238 and ct["errors"]==ct["failures"]==0 and ct["owned_python_compile_PASS"]is True and ct["bash_syntax_PASS"]is True and len(named)==len(set(named))==238 and re.findall(r"(?:^|\n)Ran ([0-9]+) tests?\b",log)==["238"]and log.rstrip().endswith("OK"),"Actual diagnostic mandatory238 producer required")
 need(ct["tested_source_files"]==new_source_rows[:6],"Actual contracts bind newOUT runner6")
 qualified_log=Path(SPEC["qualified_software_controls"][2]["path"]).read_text()
 need(named==re.findall(r"(?m)^(test[^\n]+) \.\.\. ok$",qualified_log),"Actual mandatory238 names and order equal qualified238")
 for name in["acceptance.json","context_adapter_acceptance.json","source_inclusion_final.json","source_receipt_closure_final.json"]:need(not(OUT/name).exists()and not(OUT/name).is_symlink(),"No actual Source acceptance may exist")
 need(all((p/"typed_incomplete.json").is_file()for p in[OUT,AUX]),"Original audit and adapter failure controls required")
 typed_values=[ro(p/"typed_incomplete.json")for p in[OUT,AUX]];typed_objects=[read(r["path"])for r,x in typed_values]
 need(all(v["reason_type"]==type(original_error).__name__ and v["reason"]==str(original_error)and v["allocation"]==allocation and v["source_staged"]is False and v["ACTIVE_changed"]is False for v in typed_objects),"Both original typed failures bind actual exception/allocation")
 need(typed_objects[0]["status"]=="FINAL_SOURCE_CLOSURE_TYPED_INCOMPLETE_NO_STAGING"and typed_objects[0]["failed_stage"]=="recursive_exact_new_dependencies"and typed_objects[1]["status"]=="FINAL_SOURCE_MATERIALIZED_CONTEXT_ADAPTER_TYPED_INCOMPLETE"and typed_objects[1]["failed_stage"]=="actual_frozen_library_audit_with_module_local_context_reader","Exact original Source and adapter typed stages required")
 ownfixed=[(ctpin,ctmeta),(logpin,logmeta)]+typed_values
 def new_outputs_end():
  for r,x in zip(new_source_rows,new_source_meta):ro(r["path"],r,x)
  for x in new_source_dirs:need(md(authority(x["path"]))==x and {p.name for p in Path(x["path"]).iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Actual diagnostic source directory drift")
  for r,x in ownfixed:ro(r["path"],r,x)
 new_outputs_end();observer_inputs_end()
 PROOF.mkdir(mode=0o755)
 result=dict(schema="root-source-v10-outside-authority-receipt-frame-observation.v1",status="DIAGNOSTIC_ONLY_ACTUAL_OUTSIDE_AUTHORITY_RECEIPT_FRAME_OBSERVED_ORIGINAL_ERROR_WILL_BE_RERAISED",actual_job_id=jid,allocation=allocation,current_actual_readiness=readiness,actual_direct_frozen_adapter_argv=actual_argv,original_exception_type=type(original_error).__name__,original_exception_message=str(original_error),authenticated_frames=[dict(file=f.f_code.co_filename,line=ln,name=f.f_code.co_name,qualname=f.f_code.co_qualname)for f,ln in source_frames],offending_receipt_scalar_observation=offender,actual_safe_path_lexical_p_as_scalar=str(lexical_p),audit_context_scalar=context,exact_alias_lookup_miss=True,resolution_branch="EXACT_ORIGINAL_PENDING_VERIFY",current_physical_and_resolution_basis_UNASSIGNED_at_failure=True,stale_audit_physical_basis_obj_and_verify_p_not_observed=True,no_offending_or_parent_target_or_ancestor_filesystem_IO=True,new_diagnostic_context_only_not_retrospective_17011=True,original17011_context_remains_UNOBSERVED=True,no_parent_JSON_or_other_object_dumped=True,qualified_source12=sourcepins,qualified_source12_metadata=source_meta,qualified_software4=SPEC["qualified_software_controls"],conditional_core_runtime=runtime,control_receipts=[r for r,x in controls],control_metadata_before=[x for r,x in controls],control_metadata_after=[md(r["path"])for r,x in controls],failed17011_terminal_own_CPU_receipt=failed_pin,failed17011_protected_metadata_n=len(failed_protected),actual_new_frozen_source12=new_source_rows,actual_new_frozen_source12_metadata=new_source_meta,actual_new_frozen_source2_directory_metadata=new_source_dirs,mandatory_contracts=ctpin,mandatory_log=logpin,actual238_unique_named_PASS=True,actual_two_original_typed_failures_bound_to_current_error_and_allocation=True,mandatory_named_tests=named,all_source_runtime_controls_pre_end_afteroutput_finalreadonly_PASS=True,source_staged=False,published=False,ACTIVE_changed=False,Source_audit_acceptance=False,own_created_controls_LATE_Composer_not_Plan_prerequisites=True,expected_actual_terminal_FAILED1_0=True,observation_qualification_requires_fresh_terminal_and_independent_whole_readback=True)
 rp=PROOF/"observation.json";raw=(json.dumps(result,indent=2,allow_nan=False,ensure_ascii=False)+"\n").encode()
 with rp.open("xb")as f:f.write(raw);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444);os.fsync(f.fileno())
 pin=g.rec(rp);rpm=md(rp);need(rp.read_bytes()==raw and read(rp)==result and md(rp)==rpm,"Whole own observation reread required")
 new_outputs_end();observer_inputs_end();PROOF.chmod(0o555)
 fd=os.open(str(PROOF),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
 pd=md(authority(PROOF));need(pd["mode"]==stat.S_IFDIR|0o555 and {p.name for p in PROOF.iterdir()}=={"observation.json"}and rp.read_bytes()==raw and read(rp)==result and g.rec(rp)==pin and md(rp)==rpm,"Final readonly observation universe required")
 new_outputs_end();observer_inputs_end()
 need(md(PROOF)==pd and md(rp)==rpm,"Final observer output metadata guard required")
 print(json.dumps(dict(status=result["status"],observation=pin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,failed17011_terminal=failed_pin,expected_terminal_FAILED1_0=True,Source_audit_acceptance=False),sort_keys=True),flush=True)
 raise
else:
 raise RuntimeError("Expected original outside-authority receipt failure was not observed; no diagnostic or Source qualification")
PY
