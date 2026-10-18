# Root exact two-wrapper shell-byte preservation from qualified16997 — unexecuted operational control

16997 is actual software-qualified: COMPLETED0:0/36 CPU1/GPU0,158 unique tests allPASS including old122 and new36, Root plus two whole content readbacks and independent terminal readonly metadata pass. Actual G is runs/final_source_inventory_history_rev1_software_16997/runner. The software acceptance6653 SHA04f86af25ee4057ed665268d03a19b637bc4898e00a3f0ffcf4424014eb4c4de and four software evidence controls/source12/Core are literal inputs below. Its terminal metadata seal2497247B444/inode144115643443092202/mtime1792089517000000000 is qualified metadata evidence; this new owned CPU captures its actual own SHA without reading any scientific child.

Two actual CPU-qualified wrapper text files cannot be declared public Source because current eligible_public admits .sh but .txt is receipt-only. Root/common independently inspected this exact API. Do not disguise a .txt input as a future .sh receipt or add a Plan alias permission. This operation creates actual byte-identical .sh preservation artifacts, no header/shebang/newline or other payload rewrite, then actual CPU tuples/full reread/terminal proofs. It does not execute either preserved wrapper or alter Source code/API/17 contexts/roles/default/science settings.

The two fixed inputs are:
- submissions/final_source_inventory_history_leaf1_rev1_software_primary_claim/wrap_command.txt33599/86cea4a2b2a7893833f7741766206b683388c11dbca82ed253c47cb9991eb31e.
- submissions/final_source_finite_worker_alias1_software_primary_claim/wrap_command.txt12013/9be7574dcf3e1406bd40027e0cb4d10555d9d6e9cac828a6ee944fa17cd591e6.

Root alone submits exactly one new CPU1/task1/8G10organ/GPU0 job, normal/account u21111210118, name test9_root_wrapper_shell_source_cpu, after Root plus two whole operational static reviews and readonly Human metadata readback. Existing16997/16966/16940 must not be replayed/requeued/amended. Keep exact CORE-B/no-I/unoptimized/empty CUDA/JAXcpu/no-user-site/bytecode/PYTHONPATH/BLAS1. Current-only scontrol allTRES and unique6column sacct RUNNING readiness precede any source hash/import, with60seconds/30attempts/RPC5 and actual timeout/nullRC/partialraw saved.

The new primary claim must create readonly wrap.sh before sbatch, containing the exact full actual --wrap shell string with this one whole Python fence. It is the third actual shell Source, independently hashed/read back inside owned CPU and bound to this Human. There is no SHA self-reference or dependency on the submit receipt. This Human .md is also captured inside the job. Never write future/null/string-placeholder pins into Plan.

Before exec_module, verify actual conditional Core metadata/fullscalar25916456/76bfff and all Source12 original+frozen byte identities/fullmetadata, both exact6 readonly source directories, and all four qualified software evidence controls. Import only the literal qualified frozen Source main after this guard; require software_shape on actual16997 A/contracts, fresh unchanged g.cpu() for the current new job, and exact g.conditional_core_runtime(). No software tests/compiler/audit/stage/child model/SCI/cost/report/public/Git call is made.

Verify fixed two wrappers readonly nonlink/singlelink and exact full tuples/current metadata. Capture this Human and actual current precreated wrapper own tuples/metadata. Check actual wrapper body equals the exact Human fence, preserve current readiness own files/CPU tuples, and metadata-check all2268 protected files106 directories/currentSource4+bbf from the qualified16997 terminal. The conditional Core2 is checked separately as its approved logical symlink and resolved binary, never redistributed.

Output is runs/root_wrapper_shell_byte_preservation_JOB/shell_sources/{root_source_software_16997_wrapper.sh,root_source_software_16651_wrapper.sh}. Create exactly two files with O_EXCL/O_NOFOLLOW, flush/fsync/0444/fsync and full byte reread. Freeze their exact two-file directory0555/nlink2/nonlink and bind complete metadata. Existing g.eligible_public must accept both actual .sh outputs, actual precreated primary wrap.sh and actual Human.md under unchanged Source rules. These four receipts become future explicit Source/DOC rows with distinct safe destinations after actual full acceptance.

The owned capture.json records actual input/copy pairs, complete input/output metadata, qualified Source12/software controls/Core/currentallocation/readiness, actual Human/primary shell tuples and the four Source candidates. It is exclusive/flushed/fsynced0444/full reread. Recheck all fixed original bytes, Source12, four software controls, own program/readiness, protected metadata and copy bytes/dir before/end/after output and final OUT0555/universe/fsync. Only after those final checks emit the actual CPU descriptor stdout. A PASS-shaped capture alone is not acceptance; require real rc0, final CPU descriptor, full content readback and fresh readonly terminal/independent proof. Typed failure output is best-effort; post-readonly failures retain original nonzero/stderr, and sealed outputs must not be reopened.

Both original .txt files remain immutable late INDEX history. Complete capture/claims/readiness/terminal and new operational proofs are LATE Composer controls, not their own Plan prerequisites or operative JSON seeds. Only the actual four Source/DOC leaf tuples are added to a future new Plan after qualification; no self-cycle, parent expansion, generic suffix/relative exception or permission waiver. Source production audit, new inclusion runner stage, full Source publisher/private history/public parity, F/full restore and ACTIVE remain separate later gates. This operation claims no scientific, experimental binding/blockade, clinical, Source audit, publication or final-delivery acceptance.

## Exact current-owned-CPU program

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
D = S / "submissions" / ("root_wrapper_shell_source_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_root_wrapper_shell_source_cpu", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:10:00", "MinMemoryNode": "8G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/8G10/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-wrapper-shell-source-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_WRAPPER_SOURCE_PRESERVATION_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_WRAPPER_SOURCE_PRESERVATION_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_WRAPPER_SOURCE_PRESERVATION_NOT_EXECUTED"
obj = {"schema": "root-current-owned-wrapper-shell-source-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "wrapper_source_byte_preservation_next_not_acceptance": True}), flush=True)

# Only entered after actual current owned CPU1/GPU0 readiness.
import hashlib,importlib.util
R=Path("/lustre/users/u21111210118/projects/test9");CORE=R/"env/core/bin/python";REAL=CORE.with_name("python3.11")
SPEC=json.loads("{\"qualified_source_software\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/acceptance.json\", \"bytes\": 6653, \"sha256\": \"04f86af25ee4057ed665268d03a19b637bc4898e00a3f0ffcf4424014eb4c4de\"}, \"qualified_software_controls\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/acceptance.json\", \"bytes\": 6653, \"sha256\": \"04f86af25ee4057ed665268d03a19b637bc4898e00a3f0ffcf4424014eb4c4de\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/contracts.json\", \"bytes\": 2193, \"sha256\": \"f9e7e3519f79e964221e1b9b7613714bad0dd096bd7fc8b8eb09500e6819d35a\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/contracts.txt\", \"bytes\": 27318, \"sha256\": \"8b16f21f28de4fcf3bebd2d99523976b68b4e9f2dc53d7e9bb458bdec6aba839\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/source_snapshot.json\", \"bytes\": 15984, \"sha256\": \"8d7f5d980827b58d558cba5d16439a63dd669b7a8acdd9156d2ca88410c629e1\"}], \"qualified_software_control_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/acceptance.json\", \"bytes\": 6653, \"inode\": 144115643493424905, \"mtime_ns\": 1792089023000000000, \"ctime_ns\": 1792089023000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/contracts.json\", \"bytes\": 2193, \"inode\": 144115643493424903, \"mtime_ns\": 1792089023000000000, \"ctime_ns\": 1792089023000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/contracts.txt\", \"bytes\": 27318, \"inode\": 144115643493420123, \"mtime_ns\": 1792089023000000000, \"ctime_ns\": 1792089023000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/source_snapshot.json\", \"bytes\": 15984, \"inode\": 144115643493424904, \"mtime_ns\": 1792089023000000000, \"ctime_ns\": 1792089023000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"qualified_original_source6\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_closure.py\", \"bytes\": 190920, \"sha256\": \"d4a94d4a8e1e8c32a688679ae930e50d64d06efacfd02d9dfa9516115b82d8b5\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/test_final_source_closure.py\", \"bytes\": 112898, \"sha256\": \"0ee02015d3edad2ee7066693bba285761a9decc3a7a586e87c4d81ff95e3b6e1\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_cpu.sbatch\", \"bytes\": 1658, \"sha256\": \"f3f0d3d461f0bcc51f8f22babdeac6d8b63be987aa3ed34f3dd39b06e26cc322\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/HANDOFF.md\", \"bytes\": 16737, \"sha256\": \"c32eacc9badb1799011998d90fabd840f1935daeb0e3c8ede6617b5a1d70f1be\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3224, \"sha256\": \"787184624c400a14f4155b74afa9fbdd87cdd8e79bdaec9c7977663d9cd74aa5\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_context_adapter.py\", \"bytes\": 10939, \"sha256\": \"e151b2ba918c702d011fc72d3879f60e35972a6c8fcee8f7afe468819944938b\"}], \"qualified_frozen_source6\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/final_source_closure.py\", \"bytes\": 190920, \"sha256\": \"d4a94d4a8e1e8c32a688679ae930e50d64d06efacfd02d9dfa9516115b82d8b5\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/test_final_source_closure.py\", \"bytes\": 112898, \"sha256\": \"0ee02015d3edad2ee7066693bba285761a9decc3a7a586e87c4d81ff95e3b6e1\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/final_source_cpu.sbatch\", \"bytes\": 1658, \"sha256\": \"f3f0d3d461f0bcc51f8f22babdeac6d8b63be987aa3ed34f3dd39b06e26cc322\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/HANDOFF.md\", \"bytes\": 16737, \"sha256\": \"c32eacc9badb1799011998d90fabd840f1935daeb0e3c8ede6617b5a1d70f1be\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3224, \"sha256\": \"787184624c400a14f4155b74afa9fbdd87cdd8e79bdaec9c7977663d9cd74aa5\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/final_source_context_adapter.py\", \"bytes\": 10939, \"sha256\": \"e151b2ba918c702d011fc72d3879f60e35972a6c8fcee8f7afe468819944938b\"}], \"qualified_source12_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_closure.py\", \"bytes\": 190920, \"inode\": 144115643443092175, \"mtime_ns\": 1792087604000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/test_final_source_closure.py\", \"bytes\": 112898, \"inode\": 144115643443092176, \"mtime_ns\": 1792087698000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_cpu.sbatch\", \"bytes\": 1658, \"inode\": 144115643443092177, \"mtime_ns\": 1792087604000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/HANDOFF.md\", \"bytes\": 16737, \"inode\": 144115643443092178, \"mtime_ns\": 1792087698000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3224, \"inode\": 144115643443092179, \"mtime_ns\": 1792087698000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_context_adapter.py\", \"bytes\": 10939, \"inode\": 144115643443092180, \"mtime_ns\": 1792087604000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/final_source_closure.py\", \"bytes\": 190920, \"inode\": 144115643493420117, \"mtime_ns\": 1792088995000000000, \"ctime_ns\": 1792088995000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/test_final_source_closure.py\", \"bytes\": 112898, \"inode\": 144115643493420118, \"mtime_ns\": 1792088995000000000, \"ctime_ns\": 1792088995000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/final_source_cpu.sbatch\", \"bytes\": 1658, \"inode\": 144115643493420119, \"mtime_ns\": 1792088995000000000, \"ctime_ns\": 1792088995000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/HANDOFF.md\", \"bytes\": 16737, \"inode\": 144115643493420120, \"mtime_ns\": 1792088995000000000, \"ctime_ns\": 1792088995000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3224, \"inode\": 144115643493420121, \"mtime_ns\": 1792088995000000000, \"ctime_ns\": 1792088995000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner/final_source_context_adapter.py\", \"bytes\": 10939, \"inode\": 144115643493420122, \"mtime_ns\": 1792088995000000000, \"ctime_ns\": 1792088995000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"qualified_frozen_source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/runner\", \"bytes\": 4096, \"inode\": 144115643493420116, \"mtime_ns\": 1792088995000000000, \"ctime_ns\": 1792088995000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"qualified_original_source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1\", \"bytes\": 4096, \"inode\": 144115643443092174, \"mtime_ns\": 1792087604000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"conditional_CORE_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python\", \"bytes\": 10, \"inode\": 144115618512131424, \"mtime_ns\": 1790940371000000000, \"ctime_ns\": 1790940371000000000, \"mode\": 41471, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\", \"bytes\": 25916456, \"inode\": 144115618512129393, \"mtime_ns\": 1790940364000000000, \"ctime_ns\": 1790940383000000000, \"mode\": 33277, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"source_software_terminal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_inventory_history_software16997_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 2497247, \"inode\": 144115643443092202, \"mtime_ns\": 1792089517000000000, \"ctime_ns\": 1792089517000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"fixed_wrapper_inputs\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_inventory_history_leaf1_rev1_software_primary_claim/wrap_command.txt\", \"bytes\": 33599, \"sha256\": \"86cea4a2b2a7893833f7741766206b683388c11dbca82ed253c47cb9991eb31e\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_finite_worker_alias1_software_primary_claim/wrap_command.txt\", \"bytes\": 12013, \"sha256\": \"9be7574dcf3e1406bd40027e0cb4d10555d9d6e9cac828a6ee944fa17cd591e6\"}], \"fixed_wrapper_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_inventory_history_leaf1_rev1_software_primary_claim/wrap_command.txt\", \"bytes\": 33599, \"inode\": 144115643443092189, \"mtime_ns\": 1792088987000000000, \"ctime_ns\": 1792088987000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_finite_worker_alias1_software_primary_claim/wrap_command.txt\", \"bytes\": 12013, \"inode\": 144115643443090783, \"mtime_ns\": 1792061188000000000, \"ctime_ns\": 1792061188000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"root_control_human\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_TWO_WRAPPER_SHELL_BYTE_PRESERVATION_FROM16997_20261015.md\", \"primary_wrap\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_wrapper_shell_byte_preservation_from16997_primary_claim/wrap.sh\"}")
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
def read(p):
 with Path(p).open("r",encoding="utf-8")as f:return json.load(f,object_pairs_hook=pairs,parse_constant=bad)
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
terminalpin,terminalmeta=ro(terminalpath,metadata=SPEC["source_software_terminal_metadata"])
terminal=read(terminalpath)
need(terminal["actual_job_id"]=="16997"and terminal["Root_plus_two_whole_actual_content_READBACK_PASS"]is True and terminal["mandatory158_unique_allPASS_old122_preserved_new36"]is True,"Actual accepted16997 terminal software context required")
# No Source import occurs before all qualified six-byte identities and current CPU readiness.
entry=Path(SPEC["qualified_frozen_source6"][0]["path"])
ss=importlib.util.spec_from_file_location("root_qualified_source16997_wrapper_preservation",entry)
g=importlib.util.module_from_spec(ss);ss.loader.exec_module(g)
need(g.software_shape(a,ct)==SPEC["qualified_frozen_source6"],"Unchanged qualified Source software shape required")
allocation=g.cpu();runtime=g.conditional_core_runtime()
need(allocation["job_id"]==jid and allocation["allocated_CPUs"]==1 and allocation["allocated_gpus"]==0 and allocation["numeric_sacct_row"]==attempts[selected-1]["actual_row"]and runtime==a["conditional_core_runtime"],"Actual fresh Source current CPU/Core required")
fixedpins=SPEC["fixed_wrapper_inputs"];fixedmeta=SPEC["fixed_wrapper_metadata"]
need(len(fixedpins)==len(fixedmeta)==2 and[Path(x["path"]).suffix for x in fixedpins]==[".txt",".txt"],"Exactly two actual original wrapper text files required")
for pin,meta in zip(fixedpins,fixedmeta):ro(pin["path"],pin,meta)
humanpin,humanmeta=ro(SPEC["root_control_human"]);ownwrappin,ownwrapmeta=ro(SPEC["primary_wrap"])
need(Path(ownwrappin["path"]).suffix==".sh","Actual precreated primary wrapper must itself be eligible shell Source")
humantext=Path(humanpin["path"]).read_text("utf-8");wraptext=Path(ownwrappin["path"]).read_text("utf-8")
marker="```python\n";need(humantext.count(marker)==1 and wraptext.endswith("\nPY\n"),"One whole Human code fence/current wrapper required")
need(wraptext.partition("<<'PY'\n")[2][:-4].rstrip("\n")==humantext.split(marker,1)[1].split("\n```",1)[0].rstrip("\n"),"Actual primary shell bytes must bind exact whole Human program")
readiness=read(D/"readiness.json");readyvalues=[ro(D/"readiness.json")]
for cmd in [readiness["current_scontrol_observation"]]+readiness["attempts"]:
 for k in ["raw_stdout","raw_stderr"]:readyvalues.append(ro(cmd[k]["path"]))
protected=terminal["protected_inputs_after"]+terminal["protected_directories_after"]+terminal["current_fixed_Source4_and_bbf_metadata_after"]
def inputs_end():
 need(md(CORE)==core[0]and md(REAL)==core[1]and rec(REAL)==corepin and md(REAL)==core[1]and os.readlink(CORE)=="python3.11","Conditional CORE drift")
 for pin,meta in zip(sourcepins,source_meta):ro(pin["path"],pin,meta)
 for x in source_dirs:
  need(md(authority(x["path"]))==x and{p.name for p in Path(x["path"]).iterdir()}=={Path(v["path"]).name for v in SPEC["qualified_frozen_source6"]},"Qualified source directories drift")
 for pin,meta in zip(SPEC["qualified_software_controls"],SPEC["qualified_software_control_metadata"]):ro(pin["path"],pin,meta)
 for pin,meta in zip(fixedpins,fixedmeta):ro(pin["path"],pin,meta)
 ro(humanpin["path"],humanpin,humanmeta);ro(ownwrappin["path"],ownwrappin,ownwrapmeta);ro(terminalpath,terminalpin,terminalmeta)
 for pin,meta in readyvalues:ro(pin["path"],pin,meta)
 for x in protected:need(md(authority(x["path"]))==x,"Protected16997/input metadata drift")
 need(g.conditional_core_runtime()==runtime,"Qualified Source conditional runtime drift")
inputs_end()
OUT=S/"runs"/("root_wrapper_shell_byte_preservation_"+jid);COPY=OUT/"shell_sources"
authority(OUT.parent)
need(not OUT.exists()and not OUT.is_symlink(),"Exclusive absent wrapper preservation output required")
OUT.mkdir(mode=0o755);COPY.mkdir(mode=0o755)
phase="actual_two_fixed_wrapper_byte_preservation";rows=[]
def dump(name,obj):
 p=OUT/name;raw=(json.dumps(obj,indent=2,allow_nan=False)+"\n").encode()
 with p.open("xb")as f:f.write(raw);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 need(p.read_bytes()==raw,"Full own control output reread required")
 return rec(p)
def syncdir(p):
 fd=os.open(str(p),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
try:
 names=["root_source_software_16997_wrapper.sh","root_source_software_16651_wrapper.sh"]
 for original,originalmeta,name in zip(fixedpins,fixedmeta,names):
  raw=Path(original["path"]).read_bytes();need(rec(original["path"])==original and md(original["path"])==originalmeta,"Original own wrapper drift before preservation")
  target=COPY/name;flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW
  fd=os.open(str(target),flags,0o444)
  with os.fdopen(fd,"wb")as f:f.write(raw);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444);os.fsync(f.fileno())
  copied,copiedmeta=ro(target)
  need(target.read_bytes()==raw and copied["bytes"]==original["bytes"]and copied["sha256"]==original["sha256"],"Complete byte-identical shell preservation required; no header rewrite")
  need(g.eligible_public(target),"Actual existing eligible public shell Source required")
  rows.append(dict(original=original,original_metadata_before=originalmeta,preserved=copied,preserved_metadata=copiedmeta,byte_identical=True,original_suffix=".txt",preserved_suffix=".sh",preserved_wrapper_not_executed=True))
 COPY.chmod(0o555);syncdir(COPY);copydir=md(authority(COPY))
 public=[x["preserved"]for x in rows]+[ownwrappin,humanpin]
 need(all(g.eligible_public(Path(x["path"]))for x in public),"All four actual existing public Source/DOC suffixes required")
 def outputs_end():
  need(md(authority(COPY))==copydir and stat.S_IMODE(copydir["mode"])==0o555 and copydir["nlink"]==2 and{p.name for p in COPY.iterdir()}==set(names),"Actual readonly two-copy directory metadata/universe drift")
  for x in rows:ro(x["preserved"]["path"],x["preserved"],x["preserved_metadata"])
  inputs_end()
 outputs_end()
 obj=dict(schema="root-exact-wrapper-shell-source-byte-preservation.v1",status="ACTUAL_TWO_WRAPPER_BYTES_AND_OWN_OPERATIONAL_SHELL_SOURCE_CPU_PRESERVED_NOT_EXECUTED",actual_job_id=jid,allocation=allocation,current_readiness=readiness,current_readiness_own_CPU_receipts=[x[0]for x in readyvalues],qualified_Source_software=SPEC["qualified_source_software"],qualified_source12=sourcepins,qualified_source12_metadata=source_meta,qualified_software_controls=SPEC["qualified_software_controls"],source_software_terminal=terminalpin,conditional_core_runtime=runtime,fixed_two_preservations=rows,readonly_two_copy_directory_metadata=copydir,own_Human=humanpin,own_Human_metadata=humanmeta,actual_precreated_own_primary_shell=ownwrappin,own_primary_shell_metadata=ownwrapmeta,actual_four_Source_DOC_candidates=public,original_two_text_files_not_rewritten=True,no_header_or_payload_change=True,no_preserved_wrapper_execution=True,no_new_Source_software_or_API_permission=True,source12_Core_fixed_inputs_pre_end_afteroutput_PASS=True,no_tests_or_scientific_child_IO=True,Source_audit_acceptance=False,source_staged=False,published=False,ACTIVE_changed=False,whole_capture_and_claims_LATE_not_own_Plan_prerequisites=True)
 cap=dump("capture.json",obj);outputs_end()
 need(ro(cap["path"],cap)[0]==cap and read(cap["path"])==obj,"Whole capture own-byte reread required")
 OUT.chmod(0o555);syncdir(OUT);outmeta=md(authority(OUT))
 need(stat.S_IMODE(outmeta["mode"])==0o555 and{p.name for p in OUT.iterdir()}=={"shell_sources","capture.json"},"Final readonly preservation output universe required")
 outputs_end();need(md(authority(OUT))==outmeta and ro(cap["path"],cap)[0]==cap,"Final output metadata/full own bytes drift")
 print(json.dumps(dict(status=obj["status"],capture=cap,actual_four_Source_DOC_candidates=public,actual_source_software_terminal=terminalpin,final_output_directory_metadata=outmeta),sort_keys=True),flush=True)
except BaseException as e:
 try:
  dump("typed_incomplete.json",dict(status="ACTUAL_WRAPPER_SHELL_SOURCE_PRESERVATION_UNQUALIFIED",actual_job_id=jid,phase=phase,reason_type=type(e).__name__,reason=str(e),source_staged=False,published=False,ACTIVE_changed=False))
 except Exception as se:print("Readonly failure output best-effort: "+repr(se),file=sys.stderr,flush=True)
 raise
```
