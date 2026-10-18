# Root fixed inventory-history Source REV1 software qualification from diagnostic16966 — unexecuted operational control

This is one new software qualification, following Root plus two whole revised OWN6 static reviews and Root readonly Source seal with independent full metadata readback. The exact executing package is pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1. Its current prepared158 definitions preserve old122 and initial32, then add four genuine inherited-route tests. None has been executed at the time this Human is authored. The initial six-file candidate is preserved as readonly unexecuted and unqualified Source history.

Actual Source metadata seal: submissions/final_source_inventory_history_leaf1_rev1_source_metadata_readonly_seal/receipt.json2452003B444, inode144115643443092183/mtime1792087974000000000. It binds six files190920/112898/1658/16737/3224/10939, exact metadata, initial history six and current Core2,2240 protected old files100 directories and current Source4+bbf5. No Source bytes or hashes were read by the metadata seal. The full literal selected metadata below uses Python exact integers.

Root alone must submit exactly one new CPU1/task1/16G30organ/GPU0 job named test9_final_source_inventory_history_rev1_v3 after whole operational-code review and readonly Human seal. Do not replay16940/16966, amend old envelopes or run this code on login. Keep unoptimized CORE python -B/no-I, empty CUDA, JAXcpu, no user site/bytecode/PYTHONPATH, BLAS/OMP/MKL1. This control neither runs a Source production audit nor grants new receipt-parent/Source permissions.

Current scontrol must show unique real RUNNING owner/account/organ with CPU1/task1/16G30, all present TRES GPU namespaces zero. Bounded current-only sacct readiness requires one real six-column RUNNING CPU1/GPU0 row; sixty seconds/thirty attempts/RPC timeout five seconds, partial bytes and null return code retained on timeout. No source hash/import/compile/test occurs before this current allocation gate. The unchanged child software cpu() freshly queries current allocation again.

After readiness, verify conditional Core scalar25916456/76bfff and literal metadata, actual readonly original OWN6, Source seal and all protected metadata. Own hashes are captured for exactly21 declared Source/doc/control files, plus the Source seal and readiness controls; this includes six initial history files, six prior Root Human documents, three actual prior Root wrappers, diagnostic16966 own observation/two failed terminal seals/old122 log, this Human and its current primary wrap. Only their own bytes are hashed; no scientific receipt child is interpreted. Human's exact single Python fence must match the actual primary wrapper code. These control receipts are late Source/Composer evidence; they do not become prerequisites of their own future Plan.

Run exactly /bin/bash original sealed pending package/final_source_cpu.sbatch software. The launcher executes CORE-B source main and creates runs/final_source_inventory_history_rev1_software_JOB/runner and tmp/final_source_inventory_history_rev1_v3_JOB. Require actual child0, exact new status, compiler/Bash syntax,158 unique named allOK/no failures/errors/skips, all historical122 named tests retained. Verify original→frozen Source6, own source snapshot, conditional Core before/end/after output, actual current CPU1/GPU0 allocation and software-only flags. No old standalone122/130/201/other accepted suite is separately rerun.

Root's exclusive submissions/source_inventory_history_software_outer_JOB/execution_control.json is flushed/fsynced444, reread in full and its directory fsynced555. Recheck every source/control/readiness/output/old protected metadata and conditional Core after proof and final readonly operations, then emit actual CPU descriptor stdout. Failure emits typed incomplete and rethrows; no partial PASS is qualification. Root plus independent actual content and fresh terminal/readonly evidence must qualify actual software before a new Plan/request/production audit.

Future Source stages remain separate and unchanged: new qualified frozen adapter/direct CORE-B with new actual strict request and Plan, actual inclusion runner stage, explicit complete Source publication/private history bundle, distinct full public tree with sole live baseline parent and draft PR attachment, genuine API readback before qualification, F package/extract/full index restore, indexed13299 semantic replay and same-root metadata/ROOT298 fences; ACTIVE last. Current PlanV6/16888/Q13/G16651 and all SCI/report/default/cost accepted artifacts remain preserved. Scope is computational only; this is not Source audit/scientific/public/archive/restore acceptance.

## Exact owned-CPU Python program

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
D = S / "submissions" / ("source_inventory_history_software_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_final_source_inventory_history_rev1_v3", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-inventory-history-software-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_SOURCE_INVENTORY_HISTORY_SOFTWARE_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_SOURCE_INVENTORY_HISTORY_SOFTWARE_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_SOURCE_INVENTORY_HISTORY_SOFTWARE_NOT_EXECUTED"
obj = {"schema": "root-current-owned-inventory-history-software-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
P=S/"pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1"
CORE=R/"env/core/bin/python";REAL=CORE.with_name("python3.11")
SOURCE_SPEC=json.loads("{\"source_readonly_seal\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_inventory_history_leaf1_rev1_source_metadata_readonly_seal/receipt.json\", \"bytes\": 2452003, \"inode\": 144115643443092183, \"mtime_ns\": 1792087974000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"source_files\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_closure.py\", \"bytes\": 190920, \"inode\": 144115643443092175, \"mtime_ns\": 1792087604000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/test_final_source_closure.py\", \"bytes\": 112898, \"inode\": 144115643443092176, \"mtime_ns\": 1792087698000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_cpu.sbatch\", \"bytes\": 1658, \"inode\": 144115643443092177, \"mtime_ns\": 1792087604000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/HANDOFF.md\", \"bytes\": 16737, \"inode\": 144115643443092178, \"mtime_ns\": 1792087698000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3224, \"inode\": 144115643443092179, \"mtime_ns\": 1792087698000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1/final_source_context_adapter.py\", \"bytes\": 10939, \"inode\": 144115643443092180, \"mtime_ns\": 1792087604000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1_rev1\", \"bytes\": 4096, \"inode\": 144115643443092174, \"mtime_ns\": 1792087604000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"conditional_CORE_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python\", \"bytes\": 10, \"inode\": 144115618512131424, \"mtime_ns\": 1790940371000000000, \"ctime_ns\": 1790940371000000000, \"mode\": 41471, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\", \"bytes\": 25916456, \"inode\": 144115618512129393, \"mtime_ns\": 1790940364000000000, \"ctime_ns\": 1790940383000000000, \"mode\": 33277, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"initial_unexecuted_source_history\": {\"directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1\", \"bytes\": 4096, \"inode\": 144115643443092147, \"mtime_ns\": 1792085992000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"files\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1/final_source_closure.py\", \"bytes\": 190922, \"inode\": 144115643443092148, \"mtime_ns\": 1792086411000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1/test_final_source_closure.py\", \"bytes\": 106017, \"inode\": 144115643443092149, \"mtime_ns\": 1792086630000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1/final_source_cpu.sbatch\", \"bytes\": 1623, \"inode\": 144115643443092150, \"mtime_ns\": 1792086563000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1/HANDOFF.md\", \"bytes\": 14914, \"inode\": 144115643443092151, \"mtime_ns\": 1792086508000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3001, \"inode\": 144115643443092152, \"mtime_ns\": 1792086508000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1/final_source_context_adapter.py\", \"bytes\": 10939, \"inode\": 144115643443092153, \"mtime_ns\": 1792086199000000000, \"ctime_ns\": 1792087974000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}]}, \"fixed_control_paths\": [\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_INVENTORY_HISTORY_SOURCE_REV1_SOFTWARE_FROM16966_20261015.md\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V6_OWN_SHA_FROM16651_RECOVERED16847_20261015.md\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V6_OWN_SHA_FROM16651_RECOVERED16847_20261015_REV1.md\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V6_SOURCE_AUDIT_FROM16651_16888_20261015.md\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V6_SOURCE_AUDIT_FROM16651_16888_20261015_REV1.md\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V6_RELATIVE_RECEIPT_FAILURE_OBSERVER_FROM16940_20261015.md\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V6_RELATIVE_RECEIPT_FAILURE_OBSERVER_FROM16940_20261015_REV1.md\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_relative_receipt_observer_v6_outer_16966/observation.json\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_relative_receipt_observer16966_actual_failed_diagnostic_terminal_metadata_seal/receipt.json\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v6_audit16940_actual_failed_terminal_metadata_seal/receipt.json\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_finite_worker_alias_software_16651/contracts.txt\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_inventory_history_leaf1_rev1_software_primary_claim/wrap_command.txt\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v6_production_REV1_from16651_16888_primary_claim/wrap.sh\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v6_relative_receipt_observer_REV1_from16940_primary_claim/wrap.sh\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_finite_worker_alias1_software_primary_claim/wrap_command.txt\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1/final_source_closure.py\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1/test_final_source_closure.py\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1/final_source_cpu.sbatch\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1/HANDOFF.md\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1/FINAL_SOURCE_CHECKLIST.md\", \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix5_inventory_history_leaf1/final_source_context_adapter.py\"], \"root_control_human\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_INVENTORY_HISTORY_SOURCE_REV1_SOFTWARE_FROM16966_20261015.md\", \"primary_wrap\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_inventory_history_leaf1_rev1_software_primary_claim/wrap_command.txt\", \"expected_software_tests\": 158, \"expected_software_status\": \"FINAL_SOURCE_MATERIALIZED_FINITE_WORKER_AND_INVENTORY_HISTORY_DATA_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_INTEGRATION\", \"qualified_old122_log\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_finite_worker_alias_software_16651/contracts.txt\", \"bytes\": 20352, \"sha256\": \"2b75aeaff9273de828d6d4629a0eb815b6c73087f777ef47e115fdb626f861e2\"}}")
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
need(sys.flags.optimize==0 and sys.flags.isolated==0 and sys.dont_write_bytecode,"Exact unoptimized CORE-B/no-I required")
need(os.readlink(CORE)=="python3.11"and md(CORE)==SOURCE_SPEC["conditional_CORE_metadata"][0]and md(REAL)==SOURCE_SPEC["conditional_CORE_metadata"][1],"Exact conditional interpreter metadata required")
core_pin=dict(path=str(REAL),bytes=25916456,sha256="76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a")
need(rec(REAL)==core_pin and md(REAL)==SOURCE_SPEC["conditional_CORE_metadata"][1],"Exact conditional interpreter bytes required")
SRO=Path(SOURCE_SPEC["source_readonly_seal"]["path"])
sro_pin,sro_meta=ro(SRO);need(sro_meta==SOURCE_SPEC["source_readonly_seal"],"Actual final Root source RO metadata required")
seal=read(SRO)
need(seal["Root_and_two_whole_final_static_SOURCE_PASS"]is True and seal["source_software_not_executed"]is True and seal["source_tests_defined"]==158,"Actual Root plus two final158 source reviews required")
need(seal["source_files_after"]==SOURCE_SPEC["source_files"]and seal["source_directory_after"]==SOURCE_SPEC["source_directory"]and seal["conditional_CORE_metadata_after"]==SOURCE_SPEC["conditional_CORE_metadata"],"Actual sealed source6/Core metadata must equal reviewed literal")
original_metadata=SOURCE_SPEC["source_files"];source_directory=SOURCE_SPEC["source_directory"]
need(len(original_metadata)==6 and {Path(x["path"]).name for x in original_metadata}=={"final_source_closure.py","test_final_source_closure.py","final_source_cpu.sbatch","HANDOFF.md","FINAL_SOURCE_CHECKLIST.md","final_source_context_adapter.py"},"Exactly OWN6 reviewed original Source required")
need(md(authority(P))==source_directory and stat.S_IMODE(source_directory["mode"])==0o555,"Exact readonly original Source directory required")
for x in original_metadata:need(md(authority(x["path"]))==x,"Actual reviewed Source fullmetadata required")
source_values=[ro(x["path"])for x in original_metadata]
source_pins=[x[0]for x in source_values];need([x[1]for x in source_values]==original_metadata,"Source6 metadata and actual own CPU bytes required")
control_paths=[Path(x)for x in SOURCE_SPEC["fixed_control_paths"]]
control_values=[ro(p)for p in control_paths];control_pins=[x[0]for x in control_values];control_metadata=[x[1]for x in control_values]
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
initial_history=SOURCE_SPEC["initial_unexecuted_source_history"]
need(seal["initial_unexecuted_unqualified_Source_history_after"]==initial_history,"Preserved initial Source metadata must equal actual seal")
def all_inputs_end():
 need(md(P)==source_directory,"Original Source directory changed")
 need(md(authority(initial_history["directory"]["path"]))==initial_history["directory"]and[md(authority(x["path"]))for x in initial_history["files"]]==initial_history["files"],"Unexecuted initial Source history metadata drift")
 for pin,meta in readiness_values:need(ro(pin["path"],pin)[1]==meta,"Actual readiness own bytes/metadata drift")
 need([ro(x["path"],x)[1]for x in source_pins]==original_metadata,"Original source6 bytes or metadata changed")
 need([ro(x["path"],x)[1]for x in control_pins]==control_metadata and ro(SRO,sro_pin)[1]==sro_meta,"Fixed own controls changed")
 need(md(CORE)==SOURCE_SPEC["conditional_CORE_metadata"][0]and md(REAL)==SOURCE_SPEC["conditional_CORE_metadata"][1]and rec(REAL)==core_pin and md(REAL)==SOURCE_SPEC["conditional_CORE_metadata"][1],"Conditional interpreter changed")
 for x in seal["protected_inputs_after"]+seal["protected_directories_after"]+seal["current_fixed_Source4_and_bbf_metadata_after"]:need(md(authority(x["path"]))==x,"Protected metadata changed")
all_inputs_end()
OUT=S/"runs"/("final_source_inventory_history_rev1_software_"+jid)
PROOF=S/"submissions"/("source_inventory_history_software_outer_"+jid)
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
phase="actual_reviewed_original_source_software_158";child_returncode=None
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
 old_log_path=Path(SOURCE_SPEC["qualified_old122_log"]["path"]);ro(old_log_path,SOURCE_SPEC["qualified_old122_log"])
 old_named=re.findall(r"^(test_\S+) \(([^)]*)\) \.\.\. ok$",old_log_path.read_text("utf-8"),re.M)
 need(len(old_named)==len(set(old_named))==122 and set(old_named)<=set(named),"Every historical122 named test must remain in new producer")
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
 need(stat.S_IMODE(md(authority(OUT/"runner"))["mode"])==0o555 and {p.name for p in(OUT/"runner").iterdir()}=={Path(x["path"]).name for x in source_pins},"Exact readonly frozen6 directory required")
 def output_end():
  for pin,meta in[(a_pin,a_md),(ct_pin,ct_md),(log_pin,log_md),(snap_pin,snap_md)]:need(ro(pin["path"],pin)[1]==meta,"Actual software output controls changed")
  need([ro(x["path"],x)[1]for x in frozen]==frozen_meta and read(OUT/"acceptance.json")==a and read(OUT/"contracts.json")==ct and read(OUT/"source_snapshot.json")==snap,"Whole actual software output reread required")
 output_end();all_inputs_end()
 result=dict(schema="root-finite-inventory-history-source-software-operational-control.v1",status="ROOT_ACTUAL_NEW_SOURCE_SOFTWARE_AND_OWN_CONTROLS_READBACK_PASS_NOT_SOURCE_AUDIT_OR_SCIENCE",actual_job_id=jid,allocation=a["allocation"],current_actual_readiness=readiness_obj,current_readiness_own_CPU_receipts=[x[0]for x in readiness_values],actual_child_argv=argv,child_returncode=child_returncode,actual_software_acceptance=a_pin,actual_contracts=ct_pin,actual_contract_log=log_pin,actual_source_snapshot=snap_pin,source_readonly_seal=sro_pin,source_files=frozen,original_executing_sources=source_pins,original_source_metadata=original_metadata,frozen_source_metadata=frozen_meta,fixed_control_receipts=control_pins,fixed_control_metadata=control_metadata,conditional_core_runtime=a["conditional_core_runtime"],actual_unique_tests=SOURCE_SPEC["expected_software_tests"],historical122_names_preserved=True,actual_new_named_tests=[list(x)for x in named if x not in set(old_named)],source12_Runtime_controls_pre_end_afteroutput_finalreadonly_PASS=True,Source_audit_acceptance=False,source_staged=False,published=False,ACTIVE_changed=False,own_created_controls_LATE_Composer_not_own_Plan_prerequisites=True)
 descriptor=dump_proof("execution_control.json",result)
 output_end();all_inputs_end();seal_proof()
 need(ro(descriptor["path"],descriptor)[0]==descriptor and read(descriptor["path"])==result,"Final readonly full Root control reread required")
 output_end();all_inputs_end()
 print(json.dumps(dict(status=result["status"],root_execution_control=descriptor,software_acceptance=a_pin,contracts=ct_pin,contract_log=log_pin,source_snapshot=snap_pin,source_readonly_seal=sro_pin,original_source_files=source_pins,actual_frozen_sources=frozen),sort_keys=True),flush=True)
except BaseException as e:
 try:
  dump_proof("typed_incomplete.json",dict(schema="root-finite-inventory-history-software-operational-typed-incomplete.v1",status="ACTUAL_NEW_SOURCE_SOFTWARE_NOT_QUALIFIED",actual_job_id=jid,phase=phase,child_returncode=child_returncode,reason_type=type(e).__name__,reason=str(e),source_staged=False,published=False,ACTIVE_changed=False));seal_proof()
 except Exception as se:print("Root software failure control seal error: "+repr(se),file=sys.stderr,flush=True)
 raise
```
