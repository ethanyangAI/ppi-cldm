# Root fixed separate13298 archive-parent-history SOURCE software qualification — UNEXECUTED

This is a new Root operational program, based on the actual software16997 operational guard, for exactly the newly reviewed and readonly OWN6 at pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1. It is not a Source API or a scientific gate. Source196 definitions are prepared: old158 semantics retained plus38 meaningful new finite13298 DATA cases. Root, common and successor completed whole final Source reviews; current Source metadata seal is submissions/final_source_archive_parent_history_leaf1_source_metadata_readonly_seal/receipt.json4892297. Independent whole SourceRO readback and Root plus two whole checks of this actual program, followed by its own metadata-only readonly seal, are prerequisites of the one Root submission. No job is submitted by authoring this text.

Qualified diagnostic17001 proved only its own exact BaseA/default/13298 diagnostic.offending_receipt context. The relative metadata tuple is not an input authorization and its byte/SHA checks after line49 did not run. Original17000 context remains UNOBSERVED. The diagnostic's86035-byte full observation and4976589-byte expected-failure terminal RO are fixed own CONTROL bytes hashed only after the new current owned CPU readiness. This program never follows their embedded receipts. It preserves the protected4652 exact metadata union in the new SourceRO, and the conditional Core pair separately. Old16997 software158 and all old Source/Plan/Q/SCI/report/default/cost/proofs remain unchanged.

Actual future resource envelope: CPU1/task1/16G/00:30:00/organ/account u21111210118/qos normal, requested GPU0, jobname test9_final_source_archive_parent_history_v3. Before any hash, import of project code, compile or test, bounded60s/30attempt/RPC5s strict current scontrol all-present-TRES/GPU-namespace and unique six-column RUNNING owner/account/organ checks must pass. Partial raw/timeout/null returncode are preserved truthfully. No historical Slurm queries are made by this Root program. The new Source launcher/library may perform its already-reviewed current CPU guard.

After readiness, this program checks actual Source6 fullmetadata/readonly seal/protected metadata/Core bytes and metadata, then hashes ONLY those own Source/control bytes. It validates fifteen prior actual CPU tuples, captures eighteen fixed own control tuples including this Human and its precreated primary wrap.sh, and confirms their code-fence equivalence. The Source6/P is readonly before execution. The sole child invocation is /bin/bash NEW_P/final_source_cpu.sbatch software, under CORE -B/no-I and original CUDA/JAX/BLAS/import isolation. Its exact software OUT is runs/final_source_archive_parent_history_software_JOB/runner. The wrapper creates the exclusive absent per-job TMP directory before entering this program; the reviewed child launcher's mkdir -p only reuses that same owned TMP.

Acceptance requires actual196 unique named tests/zero failure-error-skip/compile+Bash, all historical16997 actual158 names retained, exact original→frozen6/snapshot/pre-end metadata/Core and same actual CPU1/GPU0 allocation. All four outputs, twelve Source files, eighteen controls, SourceRO/protected4652/readiness/Core are checked before/end/after final readonly output. The last own JSON reads are followed by fullnative metadata checks. A separate readonly Root execution_control.json records full real tuples and final descriptor; any child/guard failure leaves typed incomplete evidence and the Slurm failure. A PASS-shaped child artifact alone cannot qualify this run. Fresh completed terminal, Root plus two full content and independent readonly-terminal seal are still required after execution.

Own Human/wrap/claims/readiness/raw/sourceRO/Root execution proof/terminal are explicit LATE Composer controls and finite Source-publication obligations, not prerequisites of their own Source Plan. No Source production audit, stage, Source publication, Git, public API write, package, restore or ACTIVE promotion is performed here. SCI remains COMPUTATIONAL_ONLY; this software job adds no experimental evidence or inference/model call.

The exact executable Python body is below. Root must submit it only once after all static and readonly gates; no replay, requeue, duplicate or envelope amendment is authorized by this document.

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
D = S / "submissions" / ("source_archive_parent_history_software_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_final_source_archive_parent_history_v3", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-archive-parent-history-software-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_SOURCE_ARCHIVE_PARENT_HISTORY_SOFTWARE_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_SOURCE_ARCHIVE_PARENT_HISTORY_SOFTWARE_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_SOURCE_ARCHIVE_PARENT_HISTORY_SOFTWARE_NOT_EXECUTED"
obj = {"schema": "root-current-owned-archive-parent-history-software-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "source_audit_execution_next_not_acceptance": True}), flush=True)

# Actual reviewed and sealed source metadata; all own hashes below run only after current CPU readiness.
import hashlib
R=Path("/lustre/users/u21111210118/projects/test9")
P=S/"pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1"
SOURCE_SPEC=json.loads("{\"source_readonly_seal\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_archive_parent_history_leaf1_source_metadata_readonly_seal/receipt.json\", \"bytes\": 4892297, \"inode\": 144115643443092323, \"mtime_ns\": 1792098247000000000, \"ctime_ns\": 1792098247000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"source_files\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/final_source_closure.py\", \"bytes\": 223307, \"inode\": 144115643443092316, \"mtime_ns\": 1792097651000000000, \"ctime_ns\": 1792098246000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/test_final_source_closure.py\", \"bytes\": 153907, \"inode\": 144115643443092317, \"mtime_ns\": 1792097651000000000, \"ctime_ns\": 1792098246000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/final_source_cpu.sbatch\", \"bytes\": 1658, \"inode\": 144115643443092318, \"mtime_ns\": 1792097353000000000, \"ctime_ns\": 1792098246000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/HANDOFF.md\", \"bytes\": 15237, \"inode\": 144115643443092320, \"mtime_ns\": 1792097901000000000, \"ctime_ns\": 1792098246000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3886, \"inode\": 144115643443092321, \"mtime_ns\": 1792097651000000000, \"ctime_ns\": 1792098246000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/final_source_context_adapter.py\", \"bytes\": 12691, \"inode\": 144115643443092319, \"mtime_ns\": 1792097651000000000, \"ctime_ns\": 1792098246000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1\", \"bytes\": 4096, \"inode\": 144115643443092315, \"mtime_ns\": 1792097480000000000, \"ctime_ns\": 1792098246000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"conditional_CORE_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python\", \"bytes\": 10, \"inode\": 144115618512131424, \"mtime_ns\": 1790940371000000000, \"ctime_ns\": 1790940371000000000, \"mode\": 41471, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\", \"bytes\": 25916456, \"inode\": 144115618512129393, \"mtime_ns\": 1790940364000000000, \"ctime_ns\": 1790940383000000000, \"mode\": 33277, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"fixed_control_paths\": [\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_ARCHIVE_PARENT_HISTORY_SOURCE_SOFTWARE_FROM17001_20261015.md\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_archive_parent_history_leaf1_software_primary_claim/wrap.sh\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/acceptance.json\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/contracts.json\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/contracts.txt\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/source_snapshot.json\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_inventory_history_software_outer_16997/execution_control.json\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_inventory_history_software16997_actual_terminal_metadata_seal/receipt.json\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_relative_receipt_observer_v7_17001_observation/observation.json\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from16997_16999_v7/request.json\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from16997_16999_v7/request_metadata.json\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16997_16998_v7/final_source_plan.json\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16997_16998_v7/HANDOFF.md\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v7_ownsha_16999/capture.json\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_plan_v7_ownsha16999_actual_terminal_metadata_seal/receipt.json\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V7_RELATIVE_RECEIPT_FAILURE_OBSERVER_FROM17000_20261015_REV1.md\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_relative_receipt_observer_v7_from17000_primary_claim/wrap.sh\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_relative_receipt_observer17001_actual_expected_failed_terminal_metadata_seal/receipt.json\"], \"root_control_human\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_ARCHIVE_PARENT_HISTORY_SOURCE_SOFTWARE_FROM17001_20261015.md\", \"primary_wrap\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_archive_parent_history_leaf1_software_primary_claim/wrap.sh\", \"expected_software_tests\": 196, \"expected_software_status\": \"FINAL_SOURCE_MATERIALIZED_FINITE_WORKER_AND_TWO_HISTORY_DATA_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_INTEGRATION\", \"qualified_old158_log\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/contracts.txt\", \"bytes\": 27318, \"sha256\": \"8b16f21f28de4fcf3bebd2d99523976b68b4e9f2dc53d7e9bb458bdec6aba839\"}, \"qualified_known_control_receipts\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/acceptance.json\", \"bytes\": 6653, \"sha256\": \"04f86af25ee4057ed665268d03a19b637bc4898e00a3f0ffcf4424014eb4c4de\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/contracts.json\", \"bytes\": 2193, \"sha256\": \"f9e7e3519f79e964221e1b9b7613714bad0dd096bd7fc8b8eb09500e6819d35a\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/contracts.txt\", \"bytes\": 27318, \"sha256\": \"8b16f21f28de4fcf3bebd2d99523976b68b4e9f2dc53d7e9bb458bdec6aba839\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_inventory_history_rev1_software_16997/source_snapshot.json\", \"bytes\": 15984, \"sha256\": \"8d7f5d980827b58d558cba5d16439a63dd669b7a8acdd9156d2ca88410c629e1\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_inventory_history_software_outer_16997/execution_control.json\", \"bytes\": 42221, \"sha256\": \"5d3b59f5537bbb2cdfe47f3922fb228e31b971eb7a3c76d8b0b0766a4a02a207\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_inventory_history_software16997_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 2497247, \"sha256\": \"951cd49a206cb3b83d9941298f839f6d3dd243e8c378e68b7a36deb68c375071\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_relative_receipt_observer_v7_17001_observation/observation.json\", \"bytes\": 86035, \"sha256\": \"4095d13a952aedcc7d029d13d89d35f39c7fcdd806480e7547869dae8a29577a\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from16997_16999_v7/request.json\", \"bytes\": 6552, \"sha256\": \"d9ce15011e1ce5dfa7ae016f47d2a0d94b4ed0481a63ce02dcca8e33a204984d\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from16997_16999_v7/request_metadata.json\", \"bytes\": 21997, \"sha256\": \"f226bc506b97ced3b0490d0970461a2fd4b3c8053c301e0b880b70d129f31cd6\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16997_16998_v7/final_source_plan.json\", \"bytes\": 1972684, \"sha256\": \"4557cabef9bb50dcb0b01d2caccb779b85e85f1e928b57b9e45d19a5206018c2\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16997_16998_v7/HANDOFF.md\", \"bytes\": 36650, \"sha256\": \"ba88d946c514bbae9c8245922b5ccd3640931f327460900a5b4ed1888f370855\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v7_ownsha_16999/capture.json\", \"bytes\": 86484, \"sha256\": \"8967114008b8325713f80546f5b1153612561e5c5c1f040681e345bf08e08365\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_plan_v7_ownsha16999_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 2560442, \"sha256\": \"14a61adf67f9cb99fee37b2594b38169b2885acc53721d0a4899bd07a84d83f8\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V7_RELATIVE_RECEIPT_FAILURE_OBSERVER_FROM17000_20261015_REV1.md\", \"bytes\": 59466, \"sha256\": \"f1751dcb3e1de8bf4acb1df87a4891c4595086452584c2539e972449e99f7574\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_relative_receipt_observer_v7_from17000_primary_claim/wrap.sh\", \"bytes\": 54856, \"sha256\": \"55e46cd7a0bb775049d23dd2f998627aeff8e6ae8d1cdf4596a5284e66d2f603\"}]}")
CORE=R/"env/core/bin/python";REAL=CORE.with_name("python3.11")
def need(v,m):
 if not v:raise ValueError(m)
def md(p):
 p=Path(p);x=p.lstat();return dict(path=str(p),bytes=x.st_size,inode=x.st_ino,mtime_ns=x.st_mtime_ns,ctime_ns=x.st_ctime_ns,mode=x.st_mode,dev=x.st_dev,nlink=x.st_nlink,uid=x.st_uid,gid=x.st_gid)
def authority(p):
 p=Path(p);need(p.is_absolute()and p.is_relative_to(R),"Exact authority path required")
 for n in [p]+list(p.parents):
  if n==R.parent:break
  need(not n.is_symlink(),"Nonlink ancestry required: "+str(n))
 return p
def rec(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open("rb")as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b);n+=len(b)
 return dict(path=str(p),bytes=n,sha256=h.hexdigest())
def ro(p,expected=None):
 p=authority(p);a=md(p);need(stat.S_ISREG(a["mode"])and stat.S_IMODE(a["mode"])==0o444 and a["nlink"]==1,"Readonly own singlelink bytes required")
 v=rec(p);need(md(p)==a,"Own-byte stable metadata required")
 if expected is not None:need(v==expected,"Exact qualified byte identity required")
 return v,a
def pairs(items):
 d={}
 for k,v in items:need(k not in d,"Duplicate own JSON key");d[k]=v
 return d
def badconst(s):raise ValueError("Nonfinite own JSON: "+s)
def read(p):
 with Path(p).open("r",encoding="utf-8")as f:return json.load(f,object_pairs_hook=pairs,parse_constant=badconst)
need(Path(sys.executable)==CORE and sys.flags.optimize==0 and sys.flags.isolated==0 and sys.dont_write_bytecode,"Exact executing CORE unoptimized-B/no-I required")
need(os.readlink(CORE)=="python3.11"and md(CORE)==SOURCE_SPEC["conditional_CORE_metadata"][0]and md(REAL)==SOURCE_SPEC["conditional_CORE_metadata"][1],"Exact conditional interpreter metadata required")
core_pin=dict(path=str(REAL),bytes=25916456,sha256="76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a")
need(rec(REAL)==core_pin and md(REAL)==SOURCE_SPEC["conditional_CORE_metadata"][1],"Exact conditional interpreter bytes required")
SRO=Path(SOURCE_SPEC["source_readonly_seal"]["path"])
sro_pin,sro_meta=ro(SRO);need(sro_meta==SOURCE_SPEC["source_readonly_seal"],"Actual final Root source RO metadata required")
seal=read(SRO)
need(seal["Root_and_two_whole_final_static_SOURCE_PASS"]is True and seal["source_software_not_executed"]is True and seal["source_tests_defined"]==SOURCE_SPEC["expected_software_tests"],"Actual Root plus two complete new source reviews required")
need(seal["source_files_after"]==SOURCE_SPEC["source_files"]and seal["source_directory_after"]==SOURCE_SPEC["source_directory"]and seal["conditional_CORE_metadata_after"]==SOURCE_SPEC["conditional_CORE_metadata"],"Actual sealed source6/Core metadata must equal reviewed literal")
original_metadata=SOURCE_SPEC["source_files"];source_directory=SOURCE_SPEC["source_directory"]
need(len(original_metadata)==6 and {Path(x["path"]).name for x in original_metadata}=={"final_source_closure.py","test_final_source_closure.py","final_source_cpu.sbatch","HANDOFF.md","FINAL_SOURCE_CHECKLIST.md","final_source_context_adapter.py"},"Exactly OWN6 reviewed original Source required")
need(md(authority(P))==source_directory and stat.S_IMODE(source_directory["mode"])==0o555,"Exact readonly original Source directory required")
for x in original_metadata:need(md(authority(x["path"]))==x,"Actual reviewed Source fullmetadata required")
source_values=[ro(x["path"])for x in original_metadata]
source_pins=[x[0]for x in source_values];need([x[1]for x in source_values]==original_metadata,"Source6 metadata and actual own CPU bytes required")
control_paths=[Path(x)for x in SOURCE_SPEC["fixed_control_paths"]]
control_values=[ro(p)for p in control_paths];control_pins=[x[0]for x in control_values];control_metadata=[x[1]for x in control_values]
for pin in SOURCE_SPEC["qualified_known_control_receipts"]:need(pin in control_pins,"Prior actual CPU-qualified control bytes must match literal")
readiness_obj=read(D/"readiness.json")
readiness_values=[ro(D/"readiness.json")]
for query_item in [readiness_obj["current_scontrol_observation"]]+readiness_obj["attempts"]:
 for field in ["raw_stdout","raw_stderr"]:readiness_values.append(ro(query_item[field]["path"]))
human_text=Path(SOURCE_SPEC["root_control_human"]).read_text("utf-8")
wrap_text=Path(SOURCE_SPEC["primary_wrap"]).read_text("utf-8")
marker="```python\n"
need(human_text.count(marker)==1 and wrap_text.endswith("\nPY\n"),"Exact single HUMAN code fence and actual primary wrapper required")
human_code=human_text.split(marker,1)[1].split("\n```",1)[0].rstrip("\n")
need(wrap_text.partition("<<'PY'\n")[2][:-4].rstrip("\n")==human_code,"Actual primary wrapper code must equal whole reviewed HUMAN fence")
def all_inputs_end():
 need(md(P)==source_directory,"Original Source directory changed")
 for pin,meta in readiness_values:need(ro(pin["path"],pin)[1]==meta,"Actual readiness own bytes/metadata drift")
 need([ro(x["path"],x)[1]for x in source_pins]==original_metadata,"Original source6 bytes or metadata changed")
 need([ro(x["path"],x)[1]for x in control_pins]==control_metadata and ro(SRO,sro_pin)[1]==sro_meta,"Fixed own controls changed")
 need(md(CORE)==SOURCE_SPEC["conditional_CORE_metadata"][0]and md(REAL)==SOURCE_SPEC["conditional_CORE_metadata"][1]and rec(REAL)==core_pin and md(REAL)==SOURCE_SPEC["conditional_CORE_metadata"][1],"Conditional interpreter changed")
 for x in seal["protected_inputs_after"]:need(md(authority(x["path"]))==x,"Protected metadata changed")
all_inputs_end()
OUT=S/"runs"/("final_source_archive_parent_history_software_"+jid)
PROOF=S/"submissions"/("source_archive_parent_history_software_outer_"+jid)
need(not OUT.exists()and not OUT.is_symlink()and not PROOF.exists()and not PROOF.is_symlink(),"Exclusive actual software output namespaces required")
PROOF.mkdir(mode=0o755)
def dump_proof(name,obj):
 p=PROOF/name;b=(json.dumps(obj,indent=2,allow_nan=False)+"\n").encode()
 with p.open("xb")as f:f.write(b);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 need(p.read_bytes()==b,"Full own proof output reread required")
 return rec(p)
def seal_proof():
 PROOF.chmod(0o555);fd=os.open(str(PROOF),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
argv=["/bin/bash",str(P/"final_source_cpu.sbatch"),"software"]
phase="actual_reviewed_original_source_software_196";child_returncode=None
try:
 child=subprocess.run(argv,cwd=str(S),env=dict(os.environ));child_returncode=child.returncode
 all_inputs_end();need(child_returncode==0,"Actual new Source software child returned nonzero")
 a_pin,a_md=ro(OUT/"acceptance.json");a=read(OUT/"acceptance.json")
 ct_pin,ct_md=ro(OUT/"contracts.json",a["contracts"]);ct=read(OUT/"contracts.json")
 log_pin,log_md=ro(OUT/"contracts.txt",ct["log"]);log=(OUT/"contracts.txt").read_text("utf-8")
 snap_pin,snap_md=ro(OUT/"source_snapshot.json",a["source_snapshot"]);snap=read(OUT/"source_snapshot.json")
 need(a["schema"]=="final-source-materialized-software-acceptance.v3"and a["status"]==SOURCE_SPEC["expected_software_status"],"Actual new version software acceptance required")
 need(ct["status"]=="PASS"and ct["tests"]==SOURCE_SPEC["expected_software_tests"]and ct["failures"]==ct["errors"]==0 and ct["owned_python_compile_PASS"]is True and ct["bash_syntax_PASS"]is True,"Actual complete new contracts/compiler/bash required")
 named=re.findall(r"^(test_\S+) \(([^)]*)\) \.\.\. ok$",log,re.M)
 need(len(named)==len(set(named))==SOURCE_SPEC["expected_software_tests"]and re.search(r"^Ran "+str(SOURCE_SPEC["expected_software_tests"])+r" tests in [0-9.]+s$",log,re.M)is not None and log.rstrip().endswith("OK")and "skipped"not in log.lower()and "FAILED"not in log,"Actual unique new mandatory tests allOK required")
 old_log_path=Path(SOURCE_SPEC["qualified_old158_log"]["path"]);ro(old_log_path,SOURCE_SPEC["qualified_old158_log"])
 old_named=re.findall(r"^(test_\S+) \(([^)]*)\) \.\.\. ok$",old_log_path.read_text("utf-8"),re.M)
 need(len(old_named)==len(set(old_named))==158 and set(old_named)<=set(named),"Every historical158 named test must remain in new producer")
 frozen=[dict(path=str(OUT/"runner"/Path(x["path"]).name),bytes=x["bytes"],sha256=x["sha256"])for x in source_pins]
 frozen_meta=[ro(x["path"],x)[1]for x in frozen]
 need(a["original_executing_sources"]==source_pins and a["source_files"]==frozen and ct["tested_source_files"]==frozen and a["source_entry"]==source_pins[0],"Actual original-frozen own6 identity and tested source chain required")
 need(snap["schema"]=="final-source-owned-six-byte-snapshot.v1"and snap["source_files"]==frozen and snap["original_executing_sources"]==source_pins and snap["source_entry"]==source_pins[0],"Whole actual new source snapshot required")
 need(snap["original_metadata_before"]==snap["original_metadata_after"]==original_metadata and snap["frozen_metadata_before"]==snap["frozen_metadata_after"]==frozen_meta,"Whole original+frozen6 prepost metadata required")
 for obj in [a,snap]:
  for k in ["whole6_source_prepost_PASS","original_and_frozen_owned_bytes_identical","conditional_runtime_prepost_PASS"]:need(obj[k]is True,"Actual source/runtime guards required")
 need(a["conditional_core_runtime"]==snap["conditional_core_runtime"]and a["conditional_core_runtime"]["resolved_binary_identity"]["bytes_as_scalar"]==25916456 and a["conditional_core_runtime"]["resolved_binary_identity"]["sha256_as_scalar"]==core_pin["sha256"],"Whole actual conditional Core identity required")
 need(a["allocation"]["job_id"]==jid and a["allocation"]["allocated_CPUs"]==1 and a["allocation"]["allocated_gpus"]==0 and a["allocation"]["numeric_sacct_row"]==attempts[selected-1]["actual_row"],"Actual same current owned CPU1/GPU0 required")
 for k in ["science_or_integration_accepted","source_staged","published","ACTIVE_changed"]:need(a[k]is False,"Software-only boundary required")
 need(a["no_model_calls"]is True and a["no_GPU_submission"]is True,"No model or GPU calls required")
 runner_path=authority(OUT/"runner");runner_metadata=md(runner_path)
 need(stat.S_ISDIR(runner_metadata["mode"])and stat.S_IMODE(runner_metadata["mode"])==0o555 and runner_metadata["nlink"]==2 and {p.name for p in runner_path.iterdir()}=={Path(x["path"]).name for x in source_pins},"Exact readonly frozen6 directory required")
 def output_end():
  need(md(authority(runner_path))==runner_metadata and stat.S_IMODE(runner_metadata["mode"])==0o555 and {p.name for p in runner_path.iterdir()}=={Path(x["path"]).name for x in source_pins},"Actual frozen6 directory metadata/mode/universe drift")
  for pin,meta in[(a_pin,a_md),(ct_pin,ct_md),(log_pin,log_md),(snap_pin,snap_md)]:need(ro(pin["path"],pin)[1]==meta,"Actual software output controls changed")
  need([ro(x["path"],x)[1]for x in frozen]==frozen_meta and read(OUT/"acceptance.json")==a and read(OUT/"contracts.json")==ct and read(OUT/"source_snapshot.json")==snap,"Whole actual software output reread required")
  need([md(pin["path"])for pin in [a_pin,ct_pin,log_pin,snap_pin]]==[a_md,ct_md,log_md,snap_md] and [md(pin["path"])for pin in frozen]==frozen_meta and md(runner_path)==runner_metadata,"Post-last-JSON full output/Source6/directory metadata drift")
 output_end();all_inputs_end()
 result=dict(schema="root-finite-archive-parent-history-source-software-operational-control.v1",status="ROOT_ACTUAL_NEW_SOURCE_SOFTWARE_AND_OWN_CONTROLS_READBACK_PASS_NOT_SOURCE_AUDIT_OR_SCIENCE",actual_job_id=jid,allocation=a["allocation"],current_actual_readiness=readiness_obj,current_readiness_own_CPU_receipts=[x[0]for x in readiness_values],actual_child_argv=argv,child_returncode=child_returncode,actual_software_acceptance=a_pin,actual_contracts=ct_pin,actual_contract_log=log_pin,actual_source_snapshot=snap_pin,source_readonly_seal=sro_pin,source_files=frozen,original_executing_sources=source_pins,original_source_metadata=original_metadata,frozen_source_metadata=frozen_meta,frozen_source_directory_metadata=runner_metadata,fixed_control_receipts=control_pins,fixed_control_metadata=control_metadata,conditional_core_runtime=a["conditional_core_runtime"],actual_unique_tests=SOURCE_SPEC["expected_software_tests"],historical158_names_preserved=True,actual_new_named_tests=[list(x)for x in named if x not in set(old_named)],source12_Runtime_controls_pre_end_afteroutput_finalreadonly_PASS=True,Source_audit_acceptance=False,source_staged=False,published=False,ACTIVE_changed=False,own_created_controls_LATE_Composer_not_own_Plan_prerequisites=True)
 descriptor=dump_proof("execution_control.json",result)
 output_end();all_inputs_end();seal_proof()
 proof_directory_metadata=md(authority(PROOF))
 need(stat.S_ISDIR(proof_directory_metadata["mode"])and stat.S_IMODE(proof_directory_metadata["mode"])==0o555 and proof_directory_metadata["nlink"]==2 and {p.name for p in PROOF.iterdir()}=={"execution_control.json"},"Final Root proof readonly directory/universe required")
 proof_pin,proof_meta=ro(descriptor["path"],descriptor)
 need(proof_pin==descriptor and read(descriptor["path"])==result and md(descriptor["path"])==proof_meta,"Final readonly full Root control reread and post-last-JSON native metadata required")
 output_end();all_inputs_end()
 need(md(authority(PROOF))==proof_directory_metadata and {p.name for p in PROOF.iterdir()}=={"execution_control.json"} and ro(descriptor["path"],descriptor)[1]==proof_meta,"Final Root proof file/directory metadata/bytes/universe drift")
 print(json.dumps(dict(status=result["status"],final_root_output_directory_metadata=proof_directory_metadata,root_execution_control=descriptor,software_acceptance=a_pin,contracts=ct_pin,contract_log=log_pin,source_snapshot=snap_pin,source_readonly_seal=sro_pin,original_source_files=source_pins,actual_frozen_sources=frozen),sort_keys=True),flush=True)
except BaseException as e:
 try:
  dump_proof("typed_incomplete.json",dict(schema="root-finite-archive-parent-history-software-operational-typed-incomplete.v1",status="ACTUAL_NEW_SOURCE_SOFTWARE_NOT_QUALIFIED",actual_job_id=jid,phase=phase,child_returncode=child_returncode,reason_type=type(e).__name__,reason=str(e),source_staged=False,published=False,ACTIVE_changed=False));seal_proof()
 except Exception as se:print("Root software failure control seal error: "+repr(se),file=sys.stderr,flush=True)
 raise
```
