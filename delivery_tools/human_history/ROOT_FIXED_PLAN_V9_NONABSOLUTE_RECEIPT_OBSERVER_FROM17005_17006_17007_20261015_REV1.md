# Root Plan V9 nonabsolute receipt frame observer REV1 from actual 17007 failure

This distinct Root operational diagnostic REV1 is PREPARED, UNEXECUTED. Original55002 is separately preserved UNEXECUTED and unqualified: independent review found a wrong historical17005 terminal job-name literal and rejection of legal parent=None contexts. REV1 corrects only that historical row, allows parent only None or bounded string, binds both original typed failures to their actual error/current allocation, and changes only its own Human/primary path bindings. Current observer job name, Source API and all existing reader permissions remain unchanged. Both original and REV1 require paired readonly preservation; ONLY REV1 may execute. Software17005/198, actual Plan V9 ownSHA17006 and strict readonly Qv9 remain unchanged. Actual17007 FAILED1:0/340s after198 unique tests passed in27.712s; its recursive dependency walk rejected a nonabsolute string receipt. The actual offending receipt, enclosing parent, physical path, trail and module were not captured. The saved13295 diagnostic is only a static candidate and is not assumed to be its cause. All original controls and failed outputs remain immutable.

One new owned CPU1/task1/16G/30min organ/GPU0 job is permitted only after Root plus two whole static reviews, Root metadata-only readonly seal and independent whole readback. Name test9_final_source_relative_receipt_observer_v9, CORE -B/no-I, empty CUDA/JAXcpu/BLAS-OMP-MKL1/user site and bytecode off/PYTHONPATH unset. Actual current strict scontrol all-present TRES/GPU namespaces and unique current RUNNING owner/account/organ sacct readiness precede hashing, project imports and mandatory198 producer execution. This is neither a standalone software requalification nor a production Source acceptance.

The unchanged qualified frozen G17005 adapter runs with actual --request/--out through runpy; sys.argv is restored in finally. Source12/SW4/Core/softwareterminal are qualified before project import. Remaining own controls are qualified after that import and before diagnostic audit. Exactly13 own controls include the original12 (including Plan/HANDOFF and this Human/shell) plus actual failed17007 terminal6292775 metadata receipt, whose ownSHA is captured only by this CPU. All existing4915 and the full failed6026 finite metadata union are checked before/end/after final readonly output, along with Source12/SW4/Core/canonical4. No generic Source, parent, relative-resolution, metadata-only or JSON permissions change.

On the exact original ValueError Absolute receipt path required, authenticate both new readonly runner6 sets against full qualified Source6 bytes and metadata before examining traceback scalar values. Require actual AUX frozenmain audit3344, receipt_edges152, receipt_shape49 and need40 frames and object identity between receipt_shape.r and selected receipt_edges.o. Capture only the offending path/bytes/SHA scalar values and types, extra key NAMES, inner trail, enclosing absolute receipt scalar fields, physical path/current native metadata, outer trail and audit parent None-or-bounded-string plus module/stage/basis bounded strings. Do not resolve, stat, open, read or hash the relative target, serialize the parent JSON or dump other object values. The observation describes this NEW run; original17007 context remains unobserved.

Require the diagnostic's actual198 unique named PASS/0fail/error/skip/compiler/Bash and both original typed-incomplete controls explicitly bound to the original error type/message, current allocation, expected Source/adapter status/stage and no staging/promotion, with A/CA/I/C absent. Write exclusive fsynced444 observation.json, reread whole own bytes, run all Source/runtime/control/metadata guards after the last JSON read, seal only the new proof directory555 and emit the final actualCPU tuple. Then use bare raise to preserve the original exception. Expected actual terminal is FAILED1:0; that nonzero status is required and never Source acceptance. A different failure, absent final descriptor, source drift or unexpected success leaves the diagnostic unqualified.

Fresh actual terminal, Root plus two whole observation/content readbacks and metadata-only terminal sealing with independent readback remain mandatory before using the new scalar evidence to design a narrow repair. No Source API changes, generic relative resolver, parent17 expansion, META whitelist, child IO, staging, Git/public write, package, restore or ACTIVE action is authorized by this diagnostic. All new Human/wrap/claims/readiness/observation/terminal bytes remain LATE Composer evidence and finite Source-publication obligations, not inputs of their own Plan. Scope remains COMPUTATIONAL_ONLY; all accepted science/report/Default/Cost records remain unchanged.

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
D = S / "submissions" / ("source_relative_receipt_v9_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_final_source_relative_receipt_observer_v9", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-source-v9-relative-receipt-observer-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_SOURCE_V9_RELATIVE_RECEIPT_OBSERVER_AUDIT_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_SOURCE_V9_RELATIVE_RECEIPT_OBSERVER_AUDIT_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_SOURCE_V9_RELATIVE_RECEIPT_OBSERVER_AUDIT_NOT_EXECUTED"
obj = {"schema": "root-current-owned-source-v9-relative-receipt-observer-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
SPEC = json.loads("{\"qualified_source_software\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/acceptance.json\", \"bytes\": 6562, \"sha256\": \"d7bb3b58dd24ed76ce3b55136a37a997774f1cd77c0debb94f484847c80d278d\"}, \"qualified_original_source6\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_closure.py\", \"bytes\": 223420, \"sha256\": \"895f34ae9444a5e08ab752cb557d17bd49c463475d39d5eb179d37cfb3be0608\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/test_final_source_closure.py\", \"bytes\": 159993, \"sha256\": \"012821051ca9708724e66ad39e7b66986f955f736c480901786cd6c2cb3893e8\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_cpu.sbatch\", \"bytes\": 1607, \"sha256\": \"2a19202da1fe8913b4284ded128706688a15a2d9b6c976bea693d9f6e100a7ef\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/HANDOFF.md\", \"bytes\": 17911, \"sha256\": \"7985ce5ba683b4305dc277e9f6b29a01429556cb84b9ae41375352703e0ee415\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 4611, \"sha256\": \"2b812507033aebfa05724433b46005bb67fc42740cfe1ecba554a7b78d882101\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_context_adapter.py\", \"bytes\": 12691, \"sha256\": \"f8379565b33c5efa5faea4dcddec9e48a416d5ca823bf9443255789cd463e07c\"}], \"qualified_frozen_source6\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_closure.py\", \"bytes\": 223420, \"sha256\": \"895f34ae9444a5e08ab752cb557d17bd49c463475d39d5eb179d37cfb3be0608\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/test_final_source_closure.py\", \"bytes\": 159993, \"sha256\": \"012821051ca9708724e66ad39e7b66986f955f736c480901786cd6c2cb3893e8\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_cpu.sbatch\", \"bytes\": 1607, \"sha256\": \"2a19202da1fe8913b4284ded128706688a15a2d9b6c976bea693d9f6e100a7ef\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/HANDOFF.md\", \"bytes\": 17911, \"sha256\": \"7985ce5ba683b4305dc277e9f6b29a01429556cb84b9ae41375352703e0ee415\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 4611, \"sha256\": \"2b812507033aebfa05724433b46005bb67fc42740cfe1ecba554a7b78d882101\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_context_adapter.py\", \"bytes\": 12691, \"sha256\": \"f8379565b33c5efa5faea4dcddec9e48a416d5ca823bf9443255789cd463e07c\"}], \"qualified_source12_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_closure.py\", \"bytes\": 223420, \"inode\": 144115643443092398, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/test_final_source_closure.py\", \"bytes\": 159993, \"inode\": 144115643443092399, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_cpu.sbatch\", \"bytes\": 1607, \"inode\": 144115643443092400, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/HANDOFF.md\", \"bytes\": 17911, \"inode\": 144115643443092401, \"mtime_ns\": 1792102471000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 4611, \"inode\": 144115643443092402, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_context_adapter.py\", \"bytes\": 12691, \"inode\": 144115643443092403, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_closure.py\", \"bytes\": 223420, \"inode\": 144115643493442364, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/test_final_source_closure.py\", \"bytes\": 159993, \"inode\": 144115643493442365, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_cpu.sbatch\", \"bytes\": 1607, \"inode\": 144115643493442366, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/HANDOFF.md\", \"bytes\": 17911, \"inode\": 144115643493442367, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 4611, \"inode\": 144115643493442368, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_context_adapter.py\", \"bytes\": 12691, \"inode\": 144115643493442369, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"qualified_original_source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1\", \"bytes\": 4096, \"inode\": 144115643443092397, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"qualified_frozen_source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner\", \"bytes\": 4096, \"inode\": 144115643493442363, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"qualified_software_controls\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/acceptance.json\", \"bytes\": 6562, \"sha256\": \"d7bb3b58dd24ed76ce3b55136a37a997774f1cd77c0debb94f484847c80d278d\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/contracts.json\", \"bytes\": 2137, \"sha256\": \"7d333ed0c2b3370759ceb5b2f775cd48c135f3a878319352f429a3c0022ca1df\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/contracts.txt\", \"bytes\": 36566, \"sha256\": \"3e746de3e0890a250c38b8aae0a6db4f8c9e4edaec4b7635abc3aa549c6e67d2\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/source_snapshot.json\", \"bytes\": 15783, \"sha256\": \"10f0397322fd26550e9a260053b784cc5d34b22aa3e46cfb77336a5ef8b90e90\"}], \"qualified_software_control_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/acceptance.json\", \"bytes\": 6562, \"inode\": 144115643493448230, \"mtime_ns\": 1792103360000000000, \"ctime_ns\": 1792103360000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/contracts.json\", \"bytes\": 2137, \"inode\": 144115643493448228, \"mtime_ns\": 1792103360000000000, \"ctime_ns\": 1792103360000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/contracts.txt\", \"bytes\": 36566, \"inode\": 144115643493442370, \"mtime_ns\": 1792103360000000000, \"ctime_ns\": 1792103360000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/source_snapshot.json\", \"bytes\": 15783, \"inode\": 144115643493448229, \"mtime_ns\": 1792103360000000000, \"ctime_ns\": 1792103360000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"conditional_CORE_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python\", \"bytes\": 10, \"inode\": 144115618512131424, \"mtime_ns\": 1790940371000000000, \"ctime_ns\": 1790940371000000000, \"mode\": 41471, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\", \"bytes\": 25916456, \"inode\": 144115618512129393, \"mtime_ns\": 1790940364000000000, \"ctime_ns\": 1790940383000000000, \"mode\": 33277, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"source_software_terminal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_final_readonly_software17005_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 5076915, \"inode\": 144115643443092431, \"mtime_ns\": 1792103622000000000, \"ctime_ns\": 1792103622000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"software_outer_proof\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_final_readonly_software_outer_17005/execution_control.json\", \"bytes\": 44435, \"sha256\": \"42453546dafb0b96abacbf871aed090d534a6276b88c26e8799c1f8e797e7533\"}, \"software_outer_proof_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_final_readonly_software_outer_17005/execution_control.json\", \"bytes\": 44435, \"inode\": 144115643493448231, \"mtime_ns\": 1792103361000000000, \"ctime_ns\": 1792103361000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"plan_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17005_v9/final_source_plan.json\", \"bytes\": 1998209, \"inode\": 144115643443092433, \"mtime_ns\": 1792103833000000000, \"ctime_ns\": 1792104052000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17005_v9/HANDOFF.md\", \"bytes\": 17477, \"inode\": 144115643443092434, \"mtime_ns\": 1792103833000000000, \"ctime_ns\": 1792104052000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"plan_readonly_seal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v9_from17005_metadata_readonly_seal/receipt.json\", \"bytes\": 5079045, \"inode\": 144115643443092436, \"mtime_ns\": 1792104053000000000, \"ctime_ns\": 1792104053000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"current_canonical_Source4\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\", \"bytes\": 2225, \"sha256\": \"d602956154fb396fd14d7737c360d7d35144b4e6ca6c3d1c51eb6dc401e42615\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\", \"bytes\": 24234, \"sha256\": \"c8fe4495439826f0882b4c43952926e5de5361f88460320cc117d003352ff345\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\", \"bytes\": 1633, \"sha256\": \"2d40850d19c7835d658e7154e5a1cb53ae763e31d360b41eec253397f2c5befb\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\", \"bytes\": 6148, \"sha256\": \"c83e427f73ff1545253d64dbb165c7e60328bb698721d1e03663e6ea7d7c403f\"}], \"current_canonical_Source4_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\", \"bytes\": 2225, \"inode\": 144115543165691905, \"mtime_ns\": 1791727539000000000, \"ctime_ns\": 1791727539000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\", \"bytes\": 24234, \"inode\": 144115543165691892, \"mtime_ns\": 1791727495000000000, \"ctime_ns\": 1791727495000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\", \"bytes\": 1633, \"inode\": 144115543165691947, \"mtime_ns\": 1791727539000000000, \"ctime_ns\": 1791727539000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\", \"bytes\": 6148, \"inode\": 144115543165691893, \"mtime_ns\": 1791727495000000000, \"ctime_ns\": 1791727495000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"source_software_terminal_receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_final_readonly_software17005_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 5076915, \"sha256\": \"0f5e71fd36b6796fa86a78a4859c13b5a5cab1ae6e78eedbd0d8f7e4ea055406\"}, \"new_request_path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17005_v9/request.json\", \"new_request2_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17005_v9/request.json\", \"bytes\": 6538, \"inode\": 144115643443092457, \"mtime_ns\": 1792105091000000000, \"ctime_ns\": 1792105451000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17005_v9/request_metadata.json\", \"bytes\": 25215, \"inode\": 144115643443092458, \"mtime_ns\": 1792105091000000000, \"ctime_ns\": 1792105451000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"new_request_directory_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17005_v9\", \"bytes\": 4096, \"inode\": 144115643443092456, \"mtime_ns\": 1792105091000000000, \"ctime_ns\": 1792105451000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"request_readonly_seal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_context_request_v9_from17005_metadata_readonly_seal/receipt.json\", \"bytes\": 5108894, \"inode\": 144115643443092460, \"mtime_ns\": 1792105452000000000, \"ctime_ns\": 1792105452000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"plan_own_capture\": {\"bytes\": 61469, \"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v9_ownsha_17006/capture.json\", \"sha256\": \"dae77e40b7f01741646d6c222952d183595c995117f6c29193ef175f3c5292ca\"}, \"plan_own_capture_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v9_ownsha_17006/capture.json\", \"bytes\": 61469, \"inode\": 144115643493448243, \"mtime_ns\": 1792104650000000000, \"ctime_ns\": 1792104650000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"plan_own_terminal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_plan_v9_ownsha17006_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 5121460, \"inode\": 144115643443092455, \"mtime_ns\": 1792104877000000000, \"ctime_ns\": 1792104877000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"root_control_human\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V9_NONABSOLUTE_RECEIPT_OBSERVER_FROM17005_17006_17007_20261015_REV1.md\", \"primary_wrap\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_nonabsolute_receipt_observer_v9_from17005_17006_17007_REV1_primary_claim/wrap.sh\", \"protected_metadata_union_count\": 4915, \"failed17007_terminal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_final_readonly_audit17007_actual_failed_terminal_metadata_seal/receipt.json\", \"bytes\": 6292775, \"inode\": 144115643443092494, \"mtime_ns\": 1792106707000000000, \"ctime_ns\": 1792106707000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}}")
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
need(a["source_files"]==SPEC["qualified_frozen_source6"]and a["original_executing_sources"]==SPEC["qualified_original_source6"]and a["allocation"]["job_id"]=="17005","Actual software17005 Source6 bindings required")
terminalpath=Path(SPEC["source_software_terminal_metadata"]["path"])
terminalpin,terminalmeta=ro(terminalpath,SPEC["source_software_terminal_receipt"],SPEC["source_software_terminal_metadata"])
terminal=read(terminalpath)
need(terminal["schema"]=="root-final-source-final-readonly-software17005-terminal-metadata-seal.v1"and terminal["actual_job_id"]=="17005"and terminal["Root_plus_two_whole_actual_software198_content_READBACK_PASS"]is True and terminal["actual_unique_named_tests"]==198 and terminal["historical196_names_and_relative_order_preserved"]is True and terminal["new2_actual_genuine_final_audit_PASS"]is True and terminal["actual_GPU0_from_current_readiness"]is True,"Actual accepted17005 terminal software198 context required")
need(len(terminal)==32 and[terminal[k]for k in["actual_software_acceptance","actual_contracts","actual_contract_log","actual_source_snapshot"]]==SPEC["qualified_software_controls"]and terminal["fresh_terminal"]["returncode"]==0 and terminal["fresh_terminal"]["raw_stderr"]==""and terminal["fresh_terminal"]["numeric_9column_row"]==["17005","COMPLETED","0:0","42","1","test9_final_source_final_readonly_v3","u21111210118","u21111210118","organ"],"Exact qualified17005 software controls and actual terminal row required")
# No Source import occurs before all qualified six-byte identities and current CPU readiness.
entry=Path(SPEC["qualified_frozen_source6"][0]["path"])
ss=importlib.util.spec_from_file_location("root_qualified_source17005_production_control",entry)
g=importlib.util.module_from_spec(ss);ss.loader.exec_module(g)
need(g.software_shape(a,ct)==SPEC["qualified_frozen_source6"],"Unchanged qualified Source software shape required")
allocation=g.cpu();runtime=g.conditional_core_runtime()
need(allocation["job_id"]==jid and allocation["allocated_CPUs"]==1 and allocation["allocated_gpus"]==0 and allocation["numeric_sacct_row"]==attempts[selected-1]["actual_row"]and runtime==a["conditional_core_runtime"],"Actual fresh Source current CPU/Core required")
snapshot=read(SPEC["qualified_software_controls"][3]["path"])
need(g.software_snapshot_shape(a,snapshot)==snapshot,"Actual qualified software six snapshot required")

QP=Path(SPEC["new_request_path"]);MP=QP.with_name("request_metadata.json")
QRO=Path(SPEC["request_readonly_seal_metadata"]["path"])
qropin,qrometa=ro(QRO,metadata=SPEC["request_readonly_seal_metadata"]);qr=read(QRO)
need(qr["schema"]=="root-new-plan-v9-strict13-request-metadata-readonly-seal.v1"and qr["Root_and_two_independent_whole_Q_and_metadata_static_PASS"]is True,"Actual reviewed strict13 QRO required")
need(qr["after_files"]==SPEC["new_request2_metadata"]and qr["after_directory"]==SPEC["new_request_directory_metadata"],"Exact readonly Q2/P metadata required")
qpin,qmeta=ro(QP,metadata=SPEC["new_request2_metadata"][0]);mpin,mmeta=ro(MP,metadata=SPEC["new_request2_metadata"][1])
q=read(QP);m=read(MP)
cap_pin,cap_meta=ro(SPEC["plan_own_capture"]["path"],SPEC["plan_own_capture"],SPEC["plan_own_capture_metadata"])
cap=read(cap_pin["path"])
t7pin,t7meta=ro(SPEC["plan_own_terminal_metadata"]["path"],metadata=SPEC["plan_own_terminal_metadata"])
t7=read(t7pin["path"])
need(t7["schema"]=="root-plan-v9-ownsha17006-terminal-metadata-seal.v1"and t7["actual_job_id"]=="17006"and t7["Root_plus_two_whole_actual_content_READBACK_PASS"]is True and t7["actual_CPU_final_descriptor"]["capture"]==cap_pin,"Actual qualified Plan ownSHA17006 terminal required")
need(t7["fresh_terminal"]["returncode"]==0 and t7["fresh_terminal"]["raw_stderr"]==""and t7["fresh_terminal"]["numeric_9column_row"]==["17006","COMPLETED","0:0","7","1","test9_source_plan_v9_ownsha_cpu","u21111210118","u21111210118","organ"],"Actual ownPlan17006 terminal row required")
planpin,planmeta=ro(cap["plan"]["path"],cap["plan"],SPEC["plan_metadata"][0]);hpin,hmeta=ro(cap["handoff"]["path"],cap["handoff"],SPEC["plan_metadata"][1])
plan=read(planpin["path"])
need(q["final_source_plan"]==planpin and q["library_software_acceptance"]==SPEC["qualified_source_software"]==plan["library_software_acceptance"]and q["mapper_software_acceptance"]==plan["mapper_software_acceptance"],"Exact Q/actual17005/V9Plan software bindings required")
need(len(q)==13 and list(q)==m["exact13_key_order"]and q["root_owned"]is True and len(q["finite_source_parent_aliases"])==8 and len(plan["context_parent_seeds"])==17 and len(plan["aliases"])==7,"Exact strict13/finite8/17/7 request required")
for k in("raw_JSON_rewrite_allowed","generic_relative_resolution_allowed","generic_external_resolution_allowed"):need(q[k]is False,"No generic permission granted")
for k in("bbf_parent_aliases","historical_parent_aliases","recovered_parent_aliases","archive_parent_aliases"):need(type(q[k])is list and q[k]==[],"No generic parent alias added")
need(cap["actual_job_id"]=="17006"and cap["Source_n"]==702 and cap["destination_n"]==641 and cap["seed_n"]==3883 and cap["unique_seed_n"]==3810 and cap["role_n"]==9 and cap["parent_n"]==17 and cap["source_audit_executed"]is False,"Actual newPlan702/641/3883/3810/9/17 scope required")
need(g.module_plan(plan)==plan["modules"],"Qualified pure-shape module plan required")
need(m["root_and_two_independent_actual17006_content_readback_PASS"]is True and m["root_and_independent_actual17006_terminal_RO_readback_PASS"]is True and m["accepted_Plan"]==planpin and m["accepted_Plan_HANDOFF"]==hpin and m["actual17006_Plan_own_capture"]==cap_pin,"Whole qualified17006 metadata bindings required")
outerpin,outermeta=ro(SPEC["software_outer_proof"]["path"],SPEC["software_outer_proof"],SPEC["software_outer_proof_metadata"])
planropin,planrometa=ro(SPEC["plan_readonly_seal_metadata"]["path"],metadata=SPEC["plan_readonly_seal_metadata"])
ownhuman,ownhumanmeta=ro(SPEC["root_control_human"]);ownwrap,ownwrapmeta=ro(SPEC["primary_wrap"])
humantext=Path(ownhuman["path"]).read_text("utf-8");wraptext=Path(ownwrap["path"]).read_text("utf-8")
need(humantext.count("```python\n")==1 and wraptext.endswith("\nPY\n")and wraptext.partition("<<'PY'\n")[2][:-4].rstrip("\n")==humantext.split("```python\n",1)[1].split("\n```",1)[0].rstrip("\n"),"Actual primary shell must bind whole reviewed Root Human")
controls=[(qpin,qmeta),(mpin,mmeta),(planpin,planmeta),(hpin,hmeta),(cap_pin,cap_meta),(t7pin,t7meta),(terminalpin,terminalmeta),(outerpin,outermeta),(qropin,qrometa),(planropin,planrometa),(ownhuman,ownhumanmeta),(ownwrap,ownwrapmeta)]
need(len(controls)==len({r["path"]for r,x in controls})==12,"Exactly twelve own control inputs required")
protected={}
for x in qr["protected_inputs_after"]+qr["after_files"]+[qr["after_directory"],md(QRO),md(QRO.parent)]:
 if x["path"]in protected:need(protected[x["path"]]==x,"Protected metadata overlap differs")
 protected[x["path"]]=x
need(len(protected)==SPEC["protected_metadata_union_count"],"Exact actual reviewed finite protected metadata union required")
need(qr["protected_inputs_before"]==qr["protected_inputs_after"],"Whole request metadata protection differs")
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
# This fixed control is metadata-only history of actual failed17007, never an own-Plan prerequisite.
failed_path=Path(SPEC["failed17007_terminal_metadata"]["path"])
failed_pin,failed_meta=ro(failed_path,metadata=SPEC["failed17007_terminal_metadata"])
failed=read(failed_path)
need(failed["actual_job_id"]=="17007"and failed["actual_198_unique_named_PASS"]is True and failed["actual_offending_receipt_parent_physical_trail_and_module_UNOBSERVED"]is True and failed["fresh_terminal"]["numeric_9column_row"]==["17007","FAILED","1:0","340","1","test9_final_source_final_readonly_v3","u21111210118","u21111210118","organ"],"Actual failed17007 unqualified history required")
failed_protected={}
for x in failed["protected_inputs_after"]+failed["after_files"]+failed["after_directories"]+[md(failed_path),md(failed_path.parent)]:
 if x["path"]in failed_protected:need(failed_protected[x["path"]]==x,"No conflicting failed17007 history metadata")
 failed_protected[x["path"]]=x
need(len(failed_protected)==6026,"Exact failed17007 protected finite union6026 required")
controls.append((failed_pin,failed_meta))
need(len(controls)==len({r["path"]for r,x in controls})==13,"Exactly13 own observer controls required")
def observer_inputs_end():
 inputs_end()
 for x in failed_protected.values():need(md(authority(x["path"]))==x,"Failed17007 history current native metadata drift")
observer_inputs_end()
OUT=authority(S/"runs")/("final_source_relative_receipt_observer_v9_"+jid)
AUX=OUT.with_name(OUT.name+"_context_adapter")
PROOF=authority(S/"submissions")/("source_relative_receipt_observer_v9_"+jid)
need(all(not p.exists()and not p.is_symlink()for p in[OUT,AUX,PROOF]),"Exclusive absent diagnostic output namespaces required")
adapter=Path(SPEC["qualified_frozen_source6"][-1]["path"])
actual_argv=[str(adapter),"--request",str(QP),"--out",str(OUT)]
savedargv=list(sys.argv)
try:
 sys.argv=actual_argv
 try:runpy.run_path(str(adapter),run_name="__main__")
 finally:sys.argv=savedargv
except ValueError as original_error:
 need(sys.argv==savedargv and str(original_error)=="Absolute receipt path required","Exact original relative-receipt failure required")
 new_source_rows=[];new_source_meta=[];new_source_dirs=[]
 for folder in[OUT/"runner",AUX/"runner"]:
  dm=md(authority(folder));need(dm["mode"]==stat.S_IFDIR|0o555 and {p.name for p in folder.iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Actual new diagnostic frozen6 directory required")
  new_source_dirs.append(dm)
  for expected in SPEC["qualified_frozen_source6"]:
   p=folder/Path(expected["path"]).name;rr,mm=ro(p)
   need((rr["bytes"],rr["sha256"])==(expected["bytes"],expected["sha256"]),"Actual observed executable source must match qualifiedG17005")
   new_source_rows.append(rr);new_source_meta.append(mm)
 tb=original_error.__traceback__;frames=[]
 while tb is not None:
  frame=tb.tb_frame
  if frame.f_code.co_filename==str(AUX/"runner/final_source_closure.py"):
   frames.append((frame,tb.tb_lineno,frame.f_code.co_name))
  tb=tb.tb_next
 need(frames and frames[-1][2:] == ("need",)and frames[-1][1]==40,"Authenticated original need40 frame required")
 shaped=[x for x in frames if x[2]=="receipt_shape"and x[1]==49]
 edges=[x for x in frames if x[2]=="receipt_edges"and x[1]==152]
 audits=[x for x in frames if x[2]=="audit"and x[1]==3344]
 need(len(shaped)==len(edges)==len(audits)==1,"Exact actual audit3344/receipt_edges152/receipt_shape49 frame chain required")
 offending=shaped[0][0].f_locals.get("r");edge_obj=edges[0][0].f_locals.get("o")
 need(type(offending)is dict and offending is edge_obj and {"path","bytes","sha256"}<=set(offending),"Authenticated same offending receipt object required")
 path=offending["path"];need(type(path)is str and len(path)<=8192 and not Path(path).is_absolute(),"Observed nonabsolute string only; no target IO")
 def scalar(value):
  t=type(value)
  if t in[str,int,bool,type(None)]:
   if t is str:need(len(value)<=8192,"Bounded observed scalar")
   return dict(type=t.__name__,value=value)
  return dict(type=t.__name__,value_not_serialized=True)
 offender=dict(path=scalar(path),bytes=scalar(offending["bytes"]),sha256=scalar(offending["sha256"]),extra_key_names=sorted(str(k)for k in offending if k not in{"path","bytes","sha256"}))
 inner=edges[0][0].f_locals.get("trail");need(type(inner)is tuple and all(type(x)is str for x in inner)and len(inner)<=256,"Exact inner trail tuple required")
 al=audits[0][0].f_locals
 enclosing=al.get("r");need(type(enclosing)is dict and {"path","bytes","sha256"}<=set(enclosing)and type(enclosing["path"])is str and Path(enclosing["path"]).is_absolute(),"Actual enclosing absolute receipt required")
 enclosing_scalar={k:scalar(enclosing[k])for k in["path","bytes","sha256"]}
 physical=al.get("physical");need(type(physical)is str or isinstance(physical,Path),"Actual physical scalar path required")
 physical_path=authority(str(physical));physical_meta=md(physical_path)
 need(stat.S_ISREG(physical_meta["mode"])and physical_meta["nlink"]==1,"Actual already-read enclosing physical regular metadata required")
 parent_value=al.get("parent");need(parent_value is None or(type(parent_value)is str and len(parent_value)<=8192),"Actual parent must be None or bounded string")
 context={"parent":parent_value}
 for k in["module","stage","basis"]:
  value=al.get(k);need(type(value)is str and len(value)<=8192,"Actual context scalar required: "+k);context[k]=value
 outer=al.get("trail");need(type(outer)is tuple and all(type(x)is str for x in outer)and len(outer)<=256,"Actual outer trail required")
 ctpin,ctmeta=ro(OUT/"contracts.json");ct=read(ctpin["path"]);logpin,logmeta=ro(ct["log"]["path"],ct["log"]);log=Path(logpin["path"]).read_text()
 named=re.findall(r"(?m)^(test[^\n]+) \.\.\. ok$",log)
 need(ct["status"]=="PASS"and ct["tests"]==198 and ct["errors"]==ct["failures"]==0 and ct["owned_python_compile_PASS"]is True and ct["bash_syntax_PASS"]is True and len(named)==len(set(named))==198 and re.findall(r"(?:^|\n)Ran ([0-9]+) tests?\b",log)==["198"]and log.rstrip().endswith("OK"),"Actual diagnostic mandatory198 producer required")
 for name in["acceptance.json","context_adapter_acceptance.json","source_inclusion_final.json","source_receipt_closure_final.json"]:need(not(OUT/name).exists(),"No actual Source acceptance may exist")
 need(all((p/"typed_incomplete.json").is_file()for p in[OUT,AUX]),"Original audit/adapter failure controls required")
 typed_values=[ro(p/"typed_incomplete.json")for p in[OUT,AUX]]
 typed_objects=[read(r["path"])for r,x in typed_values]
 need(all(v["reason_type"]==type(original_error).__name__ and v["reason"]==str(original_error)and v["allocation"]==allocation and v["source_staged"]is False and v["ACTIVE_changed"]is False for v in typed_objects),"Both original typed failures must bind actual exception/allocation")
 need(typed_objects[0]["status"]=="FINAL_SOURCE_CLOSURE_TYPED_INCOMPLETE_NO_STAGING"and typed_objects[0]["failed_stage"]=="recursive_exact_new_dependencies"and typed_objects[1]["status"]=="FINAL_SOURCE_MATERIALIZED_CONTEXT_ADAPTER_TYPED_INCOMPLETE"and typed_objects[1]["failed_stage"]=="actual_frozen_library_audit_with_module_local_context_reader","Exact original Source and adapter typed stages required")
 ownfixed=[(ctpin,ctmeta),(logpin,logmeta)]+typed_values
 readiness=read(D/"readiness.json")
 def new_outputs_end():
  for r,x in zip(new_source_rows,new_source_meta):ro(r["path"],r,x)
  for x in new_source_dirs:need(md(authority(x["path"]))==x and {p.name for p in Path(x["path"]).iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Actual diagnostic source directory drift")
  for r,x in ownfixed:ro(r["path"],r,x)
  need(md(physical_path)==physical_meta,"Already-read enclosing physical native metadata drift")
 new_outputs_end();observer_inputs_end()
 PROOF.mkdir(mode=0o755)
 result=dict(schema="root-source-v9-nonabsolute-receipt-frame-observation.v1",status="DIAGNOSTIC_ONLY_ACTUAL_NONABSOLUTE_RECEIPT_FRAME_OBSERVED_ORIGINAL_ERROR_WILL_BE_RERAISED",actual_job_id=jid,allocation=allocation,current_actual_readiness=readiness,actual_direct_frozen_adapter_argv=actual_argv,original_exception_type=type(original_error).__name__,original_exception_message=str(original_error),authenticated_frames=[dict(file=f.f_code.co_filename,line=ln,name=nm)for f,ln,nm in frames],offending_receipt_scalar_observation=offender,inner_receipt_edges_trail=list(inner),enclosing_receipt_scalar_observation=enclosing_scalar,enclosing_physical_path=str(physical_path),enclosing_physical_native_metadata=physical_meta,audit_context_scalar=context,outer_audit_trail=list(outer),original17007_context_remains_UNOBSERVED=True,static13295_candidate_not_assumed_cause=True,no_relative_target_resolve_stat_open_hash_or_read=True,no_parent_JSON_or_other_object_dumped=True,qualified_source12=sourcepins,qualified_source12_metadata=source_meta,qualified_software4=SPEC["qualified_software_controls"],conditional_core_runtime=runtime,control_receipts=[r for r,x in controls],control_metadata_before=[x for r,x in controls],control_metadata_after=[md(r["path"])for r,x in controls],failed17007_terminal_own_CPU_receipt=failed_pin,failed17007_protected_metadata_n=len(failed_protected),actual_new_frozen_source12=new_source_rows,actual_new_frozen_source12_metadata=new_source_meta,actual_new_frozen_source2_directory_metadata=new_source_dirs,mandatory_contracts=ctpin,mandatory_log=logpin,actual198_unique_named_PASS=True,actual_two_original_typed_failures_bound_to_current_error_and_allocation=True,mandatory_named_tests=named,all_source_runtime_controls_pre_end_afteroutput_finalreadonly_PASS=True,source_staged=False,published=False,ACTIVE_changed=False,Source_audit_acceptance=False,own_created_controls_LATE_Composer_not_Plan_prerequisites=True,expected_actual_terminal_FAILED1_0=True,observation_qualification_requires_fresh_terminal_and_independent_whole_readback=True)
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
 print(json.dumps(dict(status=result["status"],observation=pin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,failed17007_terminal=failed_pin,expected_terminal_FAILED1_0=True,Source_audit_acceptance=False),sort_keys=True),flush=True)
 raise
else:
 raise RuntimeError("Expected original nonabsolute receipt failure was not observed; no diagnostic or Source qualification")
```
