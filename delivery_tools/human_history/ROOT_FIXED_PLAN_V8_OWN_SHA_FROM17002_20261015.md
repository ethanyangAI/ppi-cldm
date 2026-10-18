# Root fixed PlanV8 own SHA control — prepared, not executed

This new Root-only operational control is not a Source library change, production audit, stage, science, Git/public/archive/restore acceptance or ACTIVE promotion. Dispatch only the exact reviewed Python fence after V8 Plan/H Root plus two whole static reviews/Root readonly seal and independent metadata readback, then this Human's Root plus two whole static reviews/Root readonly seal and independent metadata readback. No primary claim or Slurm job exists at preparation time.

Use one unique CPU1/task1/8G/10min organ allocation, GPU0 requested, account u21111210118/qos normal, jobname test9_source_plan_v8_ownsha_cpu, chdir S, isolated CORE -B/no-I, CUDA empty/JAXcpu/no PYTHONPATH/usersite/pycache/BLAS-OMP-MKL1. Strict actual current scontrol plus a unique numeric six-column RUNNING sacct row precede Source imports or hashing. Deadline60s/at most30 attempts/RPC<=5s; timeout returncode stays null with actual partial raw. Only current owned allocation is queried; no historical/proxy/synthesized scheduler reply.

Software17002 actually completed0:0/40CPU1/GPU0/16G30organ, A6647/63ec99b8ac32cf6acba44f26028da40e8ffb09d6d38fc31c855e165042d098ef,196 unique named PASS (old158+38), Source12/SW4/Core and Root plus TWO whole content readbacks plus Root and ONE independent whole4931497 terminal readonly readback qualified. Literal original6/frozen6/SW4/Core bytes/native metadata precede import of its actual runner/final_source_closure.py. Calls are qualified software_shape, software_snapshot_shape, fresh cpu, conditional_core_runtime, pure module_plan and individual rec. No compiler/tests/software196 rerun/Source audit/stage/child scientific receipt/worker/data/model/archive-target IO.

New Plan1985977/H25414 retains34 ordered topkeys,688Source/627dest/3865Seeds/3792unique/finaltools489/3719. Only current librarySWA+15Source/19Seed tails change from qualified V7. Actual15=17002 original6/frozen6+outer.fixed_control_receipts[18,0,1] (originalHuman/REV1Human/actualwrap); all actual15/SW4 ownbytes/currentMD are checked before/end/afteroutput. Rewinding only15/19/currentSWA must reproduce entire1972684-byte V7 raw serialization and recursive types/key/list order. Nine primary roles+two root cost gates/17orderedparents/7aliases/finite8/683/four entrypoints/1003/588/all old history remain unchanged. Pure module_plan does not authorize child IO.

The fixed12 own control files are new Plan/H, this Human/precreated shell, new PlanRO, actualSourceRO/HRO,17002 outer/terminal,16999CAP and qualifiedV7Plan/H. A terminal/HRO/new seal/self file lacking earlier CPU ownSHA is pinned by literal full native metadata and actually hashed inside this CPU; no guessed/future SHA. Qualified G17002.rec independently reproduces all12 receipts followed by a complete post-read metadata fence each batch. Four literal current canonical Source files reuse actual16999CAP tuples/current0664 metadata and are hash-only. All4704 protected metadata entries in PlanRO remain exact including readonlyctime; nativeidentity excludes atime. CORE link/resolved binary are conditional bytes and never redistributed.

Output one exclusive capture.json/fullbyte/strictJSON reread/flush/fsync/0444/OUT0555-exactone-fsync; final descriptor prints only after final input/output guards. A PASS-shaped capture is unqualified until actual0:0/finaldescriptor match/Root plus two whole content/fresh successful terminal/readonly Root plus independent metadata pass. Failure output is best effort: before OUT no typed file; after readonly OUT typed writes can fail leaving stderr/nonzero. No sealed output mutation or failed-job retroacceptance.

All new own controls/Human/primary/readiness/raw/CAP/logs/terminal remain LATE Composer and finite Source publication obligations, never prerequisites of their own Plan. New15 does not exhaust V7H/older Root Human revisions/shells/failed runners/configuration duties. Accepted production Source+NEWstage precede separately qualified finite late Source publisher/private history/public COMPLETE tree. No generic Reader/relative/17parent/JSON/Source identity waiver, fake gate or selfcycle. Source/history/SCI/report/default/cost/MainERR1–10 stay unchanged. Actual A/CA/I/C and all four finite preservation families are future.

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
D = S / "submissions" / ("source_plan_v8_ownsha_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_source_plan_v8_ownsha_cpu", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:10:00", "MinMemoryNode": "8G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/8G10/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-plan-v8-ownsha-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_PLAN_V8_OWN_SHA_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_PLAN_V8_OWN_SHA_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_PLAN_V8_OWN_SHA_NOT_EXECUTED"
obj = {"schema": "root-current-owned-plan-v8-ownsha-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
SPEC=json.loads("{\"qualified_source_software\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/acceptance.json\", \"bytes\": 6647, \"sha256\": \"63ec99b8ac32cf6acba44f26028da40e8ffb09d6d38fc31c855e165042d098ef\"}, \"qualified_original_source6\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/final_source_closure.py\", \"bytes\": 223307, \"sha256\": \"07a656eea18e16c80d7d48fac361a8f246a2fc7aa737f45e365636215194434d\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/test_final_source_closure.py\", \"bytes\": 153907, \"sha256\": \"a032716cd9f1860461707bd02b7ae9f1922170c3f942b4e2e3f2eedfea3ddedd\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/final_source_cpu.sbatch\", \"bytes\": 1658, \"sha256\": \"1e1791bdd8ff8e3c9fa87f2d17317f3288a3b969f772857f1bb98254473e6e3e\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/HANDOFF.md\", \"bytes\": 15237, \"sha256\": \"49c0e63458f74b82cb71c87267f92039afbec72281a2f58f18933c03fe9e980d\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3886, \"sha256\": \"ff1186b6ac1b09e15e28fac290b372142665da9b9fa32c2532c10521efe78f0f\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/final_source_context_adapter.py\", \"bytes\": 12691, \"sha256\": \"f8379565b33c5efa5faea4dcddec9e48a416d5ca823bf9443255789cd463e07c\"}], \"qualified_frozen_source6\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/final_source_closure.py\", \"bytes\": 223307, \"sha256\": \"07a656eea18e16c80d7d48fac361a8f246a2fc7aa737f45e365636215194434d\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/test_final_source_closure.py\", \"bytes\": 153907, \"sha256\": \"a032716cd9f1860461707bd02b7ae9f1922170c3f942b4e2e3f2eedfea3ddedd\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/final_source_cpu.sbatch\", \"bytes\": 1658, \"sha256\": \"1e1791bdd8ff8e3c9fa87f2d17317f3288a3b969f772857f1bb98254473e6e3e\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/HANDOFF.md\", \"bytes\": 15237, \"sha256\": \"49c0e63458f74b82cb71c87267f92039afbec72281a2f58f18933c03fe9e980d\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3886, \"sha256\": \"ff1186b6ac1b09e15e28fac290b372142665da9b9fa32c2532c10521efe78f0f\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/final_source_context_adapter.py\", \"bytes\": 12691, \"sha256\": \"f8379565b33c5efa5faea4dcddec9e48a416d5ca823bf9443255789cd463e07c\"}], \"qualified_source12_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/final_source_closure.py\", \"bytes\": 223307, \"inode\": 144115643443092316, \"mtime_ns\": 1792097651000000000, \"ctime_ns\": 1792098246000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/test_final_source_closure.py\", \"bytes\": 153907, \"inode\": 144115643443092317, \"mtime_ns\": 1792097651000000000, \"ctime_ns\": 1792098246000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/final_source_cpu.sbatch\", \"bytes\": 1658, \"inode\": 144115643443092318, \"mtime_ns\": 1792097353000000000, \"ctime_ns\": 1792098246000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/HANDOFF.md\", \"bytes\": 15237, \"inode\": 144115643443092320, \"mtime_ns\": 1792097901000000000, \"ctime_ns\": 1792098246000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3886, \"inode\": 144115643443092321, \"mtime_ns\": 1792097651000000000, \"ctime_ns\": 1792098246000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/final_source_context_adapter.py\", \"bytes\": 12691, \"inode\": 144115643443092319, \"mtime_ns\": 1792097651000000000, \"ctime_ns\": 1792098246000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/final_source_closure.py\", \"bytes\": 223307, \"inode\": 144115643493436622, \"mtime_ns\": 1792098928000000000, \"ctime_ns\": 1792098928000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/test_final_source_closure.py\", \"bytes\": 153907, \"inode\": 144115643493436623, \"mtime_ns\": 1792098928000000000, \"ctime_ns\": 1792098928000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/final_source_cpu.sbatch\", \"bytes\": 1658, \"inode\": 144115643493436624, \"mtime_ns\": 1792098928000000000, \"ctime_ns\": 1792098928000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/HANDOFF.md\", \"bytes\": 15237, \"inode\": 144115643493436625, \"mtime_ns\": 1792098928000000000, \"ctime_ns\": 1792098928000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3886, \"inode\": 144115643493436626, \"mtime_ns\": 1792098928000000000, \"ctime_ns\": 1792098928000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/final_source_context_adapter.py\", \"bytes\": 12691, \"inode\": 144115643493436627, \"mtime_ns\": 1792098928000000000, \"ctime_ns\": 1792098928000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"qualified_original_source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1\", \"bytes\": 4096, \"inode\": 144115643443092315, \"mtime_ns\": 1792097480000000000, \"ctime_ns\": 1792098246000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"qualified_frozen_source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner\", \"bytes\": 4096, \"inode\": 144115643493436621, \"mtime_ns\": 1792098928000000000, \"ctime_ns\": 1792098928000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"qualified_software_controls\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/acceptance.json\", \"bytes\": 6647, \"sha256\": \"63ec99b8ac32cf6acba44f26028da40e8ffb09d6d38fc31c855e165042d098ef\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/contracts.json\", \"bytes\": 2193, \"sha256\": \"2a8a30f3457e03524554bee0f3fb198b07edb1b424ffbef947ea072fcde73cc5\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/contracts.txt\", \"bytes\": 36056, \"sha256\": \"504a99b94c600ffe81403ebbd378bb37671b90c92cd674ce07562df9fb61e492\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/source_snapshot.json\", \"bytes\": 15984, \"sha256\": \"9ea92225e06252c47222c0e32912d670735103b3d8ecfe3014992169fedca337\"}], \"qualified_software_control_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/acceptance.json\", \"bytes\": 6647, \"inode\": 144115643493442289, \"mtime_ns\": 1792098962000000000, \"ctime_ns\": 1792098962000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/contracts.json\", \"bytes\": 2193, \"inode\": 144115643493442287, \"mtime_ns\": 1792098962000000000, \"ctime_ns\": 1792098962000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/contracts.txt\", \"bytes\": 36056, \"inode\": 144115643493436628, \"mtime_ns\": 1792098962000000000, \"ctime_ns\": 1792098962000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/source_snapshot.json\", \"bytes\": 15984, \"inode\": 144115643493442288, \"mtime_ns\": 1792098962000000000, \"ctime_ns\": 1792098962000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"conditional_CORE_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python\", \"bytes\": 10, \"inode\": 144115618512131424, \"mtime_ns\": 1790940371000000000, \"ctime_ns\": 1790940371000000000, \"mode\": 41471, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\", \"bytes\": 25916456, \"inode\": 144115618512129393, \"mtime_ns\": 1790940364000000000, \"ctime_ns\": 1790940383000000000, \"mode\": 33277, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"source_software_terminal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_archive_parent_history_software17002_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 4931497, \"inode\": 144115643443092342, \"mtime_ns\": 1792099323000000000, \"ctime_ns\": 1792099323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"software_outer_proof\": {\"bytes\": 43564, \"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_archive_parent_history_software_outer_17002/execution_control.json\", \"sha256\": \"0b9febdcc5d43779164f7ed0ea33535a4fd42f43dfe36044d2a3af274a379a25\"}, \"software_outer_proof_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_archive_parent_history_software_outer_17002/execution_control.json\", \"bytes\": 43564, \"inode\": 144115643493442290, \"mtime_ns\": 1792098963000000000, \"ctime_ns\": 1792098963000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"source_readonly_seal\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_archive_parent_history_leaf1_source_metadata_readonly_seal/receipt.json\", \"bytes\": 4892297, \"sha256\": \"64aba260689bfbf4d5c730d878bdced9658760cf7ae13e20de1e4342c704378f\"}, \"source_readonly_seal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_archive_parent_history_leaf1_source_metadata_readonly_seal/receipt.json\", \"bytes\": 4892297, \"inode\": 144115643443092323, \"mtime_ns\": 1792098247000000000, \"ctime_ns\": 1792098247000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"software_humans_readonly_seal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_archive_parent_history_software_REV1_humans_metadata_readonly_seal/receipt.json\", \"bytes\": 4895685, \"inode\": 144115643443092327, \"mtime_ns\": 1792098776000000000, \"ctime_ns\": 1792098777000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"actual_additional_15_Source_rows\": [{\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/final_source_closure.py\", \"bytes\": 223307, \"sha256\": \"07a656eea18e16c80d7d48fac361a8f246a2fc7aa737f45e365636215194434d\"}, \"repository_relative\": \"delivery_tools/source_closure_archive_parent_history_leaf1/original/final_source_closure.py\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/test_final_source_closure.py\", \"bytes\": 153907, \"sha256\": \"a032716cd9f1860461707bd02b7ae9f1922170c3f942b4e2e3f2eedfea3ddedd\"}, \"repository_relative\": \"delivery_tools/source_closure_archive_parent_history_leaf1/original/test_final_source_closure.py\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/final_source_cpu.sbatch\", \"bytes\": 1658, \"sha256\": \"1e1791bdd8ff8e3c9fa87f2d17317f3288a3b969f772857f1bb98254473e6e3e\"}, \"repository_relative\": \"delivery_tools/source_closure_archive_parent_history_leaf1/original/final_source_cpu.sbatch\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/HANDOFF.md\", \"bytes\": 15237, \"sha256\": \"49c0e63458f74b82cb71c87267f92039afbec72281a2f58f18933c03fe9e980d\"}, \"repository_relative\": \"delivery_tools/source_closure_archive_parent_history_leaf1/original/HANDOFF.md\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3886, \"sha256\": \"ff1186b6ac1b09e15e28fac290b372142665da9b9fa32c2532c10521efe78f0f\"}, \"repository_relative\": \"delivery_tools/source_closure_archive_parent_history_leaf1/original/FINAL_SOURCE_CHECKLIST.md\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix6_archive_parent_history_leaf1/final_source_context_adapter.py\", \"bytes\": 12691, \"sha256\": \"f8379565b33c5efa5faea4dcddec9e48a416d5ca823bf9443255789cd463e07c\"}, \"repository_relative\": \"delivery_tools/source_closure_archive_parent_history_leaf1/original/final_source_context_adapter.py\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/final_source_closure.py\", \"bytes\": 223307, \"sha256\": \"07a656eea18e16c80d7d48fac361a8f246a2fc7aa737f45e365636215194434d\"}, \"repository_relative\": \"delivery_tools/source_closure_archive_parent_history_leaf1/software_17002/final_source_closure.py\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/test_final_source_closure.py\", \"bytes\": 153907, \"sha256\": \"a032716cd9f1860461707bd02b7ae9f1922170c3f942b4e2e3f2eedfea3ddedd\"}, \"repository_relative\": \"delivery_tools/source_closure_archive_parent_history_leaf1/software_17002/test_final_source_closure.py\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/final_source_cpu.sbatch\", \"bytes\": 1658, \"sha256\": \"1e1791bdd8ff8e3c9fa87f2d17317f3288a3b969f772857f1bb98254473e6e3e\"}, \"repository_relative\": \"delivery_tools/source_closure_archive_parent_history_leaf1/software_17002/final_source_cpu.sbatch\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/HANDOFF.md\", \"bytes\": 15237, \"sha256\": \"49c0e63458f74b82cb71c87267f92039afbec72281a2f58f18933c03fe9e980d\"}, \"repository_relative\": \"delivery_tools/source_closure_archive_parent_history_leaf1/software_17002/HANDOFF.md\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 3886, \"sha256\": \"ff1186b6ac1b09e15e28fac290b372142665da9b9fa32c2532c10521efe78f0f\"}, \"repository_relative\": \"delivery_tools/source_closure_archive_parent_history_leaf1/software_17002/FINAL_SOURCE_CHECKLIST.md\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_archive_parent_history_software_17002/runner/final_source_context_adapter.py\", \"bytes\": 12691, \"sha256\": \"f8379565b33c5efa5faea4dcddec9e48a416d5ca823bf9443255789cd463e07c\"}, \"repository_relative\": \"delivery_tools/source_closure_archive_parent_history_leaf1/software_17002/final_source_context_adapter.py\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_ARCHIVE_PARENT_HISTORY_SOURCE_SOFTWARE_FROM17001_20261015.md\", \"bytes\": 38353, \"sha256\": \"207aae208c3946b9d7ddbb5b45f1e95ce982c9144c60e97ef06a1eeb26a45a03\"}, \"repository_relative\": \"delivery_tools/human_history/ROOT_FIXED_ARCHIVE_PARENT_HISTORY_SOURCE_SOFTWARE_FROM17001_20261015.md\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_ARCHIVE_PARENT_HISTORY_SOURCE_SOFTWARE_FROM17001_20261015_REV1.md\", \"bytes\": 39117, \"sha256\": \"316cc99bda4a9ef744436d04e7007b552f7e74ed4463daad1fe98f68d9e00fce\"}, \"repository_relative\": \"delivery_tools/human_history/ROOT_FIXED_ARCHIVE_PARENT_HISTORY_SOURCE_SOFTWARE_FROM17001_20261015_REV1.md\"}, {\"receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_archive_parent_history_leaf1_REV1_software_primary_claim/wrap.sh\", \"bytes\": 34566, \"sha256\": \"8aafa1426cf5221ef0321a375c50eb2a43d0af7d096e77020640575661817b9d\"}, \"repository_relative\": \"delivery_tools/root_operational_programs/final_source_archive_parent_history_leaf1_REV1_software_primary_claim/wrap.sh\"}], \"plan_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17002_v8/final_source_plan.json\", \"bytes\": 1985977, \"inode\": 144115643443092344, \"mtime_ns\": 1792099748000000000, \"ctime_ns\": 1792099991000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17002_v8/HANDOFF.md\", \"bytes\": 25414, \"inode\": 144115643443092345, \"mtime_ns\": 1792099748000000000, \"ctime_ns\": 1792099991000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"plan_directory_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17002_v8\", \"bytes\": 4096, \"inode\": 144115643443092343, \"mtime_ns\": 1792099748000000000, \"ctime_ns\": 1792099991000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"plan_readonly_seal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v8_from17002_metadata_readonly_seal/receipt.json\", \"bytes\": 4933641, \"inode\": 144115643443092347, \"mtime_ns\": 1792099992000000000, \"ctime_ns\": 1792099992000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"prior_qualified_plan_and_handoff\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16997_16998_v7/final_source_plan.json\", \"bytes\": 1972684, \"sha256\": \"4557cabef9bb50dcb0b01d2caccb779b85e85f1e928b57b9e45d19a5206018c2\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16997_16998_v7/HANDOFF.md\", \"bytes\": 36650, \"sha256\": \"ba88d946c514bbae9c8245922b5ccd3640931f327460900a5b4ed1888f370855\"}], \"prior_qualified_plan_and_handoff_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16997_16998_v7/final_source_plan.json\", \"bytes\": 1972684, \"inode\": 144115643443092223, \"mtime_ns\": 1792091925000000000, \"ctime_ns\": 1792092303000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16997_16998_v7/HANDOFF.md\", \"bytes\": 36650, \"inode\": 144115643443092224, \"mtime_ns\": 1792091925000000000, \"ctime_ns\": 1792092303000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"prior_v7_ownsha_capture\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v7_ownsha_16999/capture.json\", \"bytes\": 86484, \"sha256\": \"8967114008b8325713f80546f5b1153612561e5c5c1f040681e345bf08e08365\"}, \"prior_v7_ownsha_capture_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v7_ownsha_16999/capture.json\", \"bytes\": 86484, \"inode\": 144115643493424937, \"mtime_ns\": 1792093448000000000, \"ctime_ns\": 1792093448000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"current_canonical_Source4\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\", \"bytes\": 2225, \"sha256\": \"d602956154fb396fd14d7737c360d7d35144b4e6ca6c3d1c51eb6dc401e42615\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\", \"bytes\": 24234, \"sha256\": \"c8fe4495439826f0882b4c43952926e5de5361f88460320cc117d003352ff345\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\", \"bytes\": 1633, \"sha256\": \"2d40850d19c7835d658e7154e5a1cb53ae763e31d360b41eec253397f2c5befb\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\", \"bytes\": 6148, \"sha256\": \"c83e427f73ff1545253d64dbb165c7e60328bb698721d1e03663e6ea7d7c403f\"}], \"current_canonical_Source4_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\", \"bytes\": 2225, \"inode\": 144115543165691905, \"mtime_ns\": 1791727539000000000, \"ctime_ns\": 1791727539000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\", \"bytes\": 24234, \"inode\": 144115543165691892, \"mtime_ns\": 1791727495000000000, \"ctime_ns\": 1791727495000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\", \"bytes\": 1633, \"inode\": 144115543165691947, \"mtime_ns\": 1791727539000000000, \"ctime_ns\": 1791727539000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\", \"bytes\": 6148, \"inode\": 144115543165691893, \"mtime_ns\": 1791727495000000000, \"ctime_ns\": 1791727495000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"root_control_human\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V8_OWN_SHA_FROM17002_20261015.md\", \"primary_wrap\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v8_ownsha_from17002_primary_claim/wrap.sh\"}")
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
need(a["source_files"]==SPEC["qualified_frozen_source6"]and a["original_executing_sources"]==SPEC["qualified_original_source6"]and a["allocation"]["job_id"]=="17002","Actual17002 original/frozen software bindings required")
terminalpin,terminalmeta=ro(SPEC["source_software_terminal_metadata"]["path"],metadata=SPEC["source_software_terminal_metadata"])
terminal=read(terminalpin["path"])
need(terminal["schema"]=="root-final-source-archive-parent-history-software17002-terminal-metadata-seal.v1"and terminal["actual_job_id"]=="17002"and terminal["Root_plus_two_whole_actual_software196_content_READBACK_PASS"]is True and terminal["actual_unique_named_tests"]==196 and terminal["historical158_names_preserved"]is True and terminal["new38_actual_PASS"]is True and terminal["actual_GPU0_from_current_readiness"]is True,"Actual accepted196 terminal context required")
need([terminal[k]for k in ["actual_software_acceptance","actual_contracts","actual_contract_log","actual_source_snapshot"]]==SW and terminal["fresh_terminal"]["returncode"]==0 and terminal["fresh_terminal"]["raw_stderr"]==""and terminal["fresh_terminal"]["numeric_9column_row"]==["17002","COMPLETED","0:0","40","1","test9_final_source_archive_parent_history_v3","u21111210118","u21111210118","organ"],"Exact qualified17002 SW4/fresh terminal required")
# Import only the actual qualified frozen source after all literal byte and metadata guards.
ss=importlib.util.spec_from_file_location("root_qualified_source17002_plan_v8_ownsha",Path(SPEC["qualified_frozen_source6"][0]["path"]))
g=importlib.util.module_from_spec(ss);ss.loader.exec_module(g)
need(g.software_shape(a,ct)==SPEC["qualified_frozen_source6"],"Qualified196 software shape required")
allocation=g.cpu();runtime=g.conditional_core_runtime()
need(allocation["job_id"]==jid and allocation["allocated_CPUs"]==1 and allocation["allocated_gpus"]==0 and allocation["numeric_sacct_row"]==attempts[selected-1]["actual_row"]and runtime==a["conditional_core_runtime"],"Fresh current CPU1/GPU0/Core required")
snapshot=read(SW[3]["path"]);need(g.software_snapshot_shape(a,snapshot)==snapshot,"Qualified software snapshot shape required")
outerpin,outermeta=ro(SPEC["software_outer_proof"]["path"],SPEC["software_outer_proof"],SPEC["software_outer_proof_metadata"])
outer=read(outerpin["path"]);fixed=outer["fixed_control_receipts"]
need(outer["actual_job_id"]=="17002"and outer["actual_unique_tests"]==196 and outer["historical158_names_preserved"]is True and len(fixed)==19 and outer["status"]=="ROOT_ACTUAL_NEW_SOURCE_SOFTWARE_AND_OWN_CONTROLS_READBACK_PASS_NOT_SOURCE_AUDIT_OR_SCIENCE"and outer["actual_software_acceptance"]==SW[0]and outer["source_files"]==SPEC["qualified_frozen_source6"]and outer["original_executing_sources"]==SPEC["qualified_original_source6"],"Exact actual17002 outer controls required")
sourceROpin,sourceROmeta=ro(SPEC["source_readonly_seal"]["path"],SPEC["source_readonly_seal"],SPEC["source_readonly_seal_metadata"])
sourceRO=read(sourceROpin["path"])
need(sourceRO["source_directory_after"]==source_dirs[0]and sourceRO["source_files_after"]==source_meta[:6]and outer["source_readonly_seal"]==sourceROpin,"Actual SourceRO original6 identity required")
HROpin,HROmeta=ro(SPEC["software_humans_readonly_seal_metadata"]["path"],metadata=SPEC["software_humans_readonly_seal_metadata"])
HRO=read(HROpin["path"])
need(len(HRO)==21 and HRO["Root_and_two_whole_final_static_HUMAN_PASS"]is True,"Actual software Human readonly seal shape required")
additional=sourcepins+[fixed[18],fixed[0],fixed[1]]
destinations=["delivery_tools/source_closure_archive_parent_history_leaf1/original/"+Path(x["path"]).name for x in additional[:6]]
destinations+=["delivery_tools/source_closure_archive_parent_history_leaf1/software_17002/"+Path(x["path"]).name for x in additional[6:12]]
destinations+=["delivery_tools/human_history/"+Path(x["path"]).name for x in additional[12:14]]
destinations+=["delivery_tools/root_operational_programs/"+Path(additional[14]["path"]).parent.name+"/wrap.sh"]
additionalrows=[dict(receipt=r,repository_relative=d)for r,d in zip(additional,destinations)]
need(len(additional)==len(destinations)==len(set(destinations))==15 and additionalrows==SPEC["actual_additional_15_Source_rows"],"Exact actual fifteen Source/DOC ordered rows required")
additionalmeta=[ro(r["path"],r)[1]for r in additional]
planmeta=SPEC["plan_metadata"]
planpin,planbefore=ro(planmeta[0]["path"],metadata=planmeta[0]);handoffpin,handoffbefore=ro(planmeta[1]["path"],metadata=planmeta[1])
PLAN=Path(planpin["path"]);HANDOFF=Path(handoffpin["path"])
planROpin,planROmeta=ro(SPEC["plan_readonly_seal_metadata"]["path"],metadata=SPEC["plan_readonly_seal_metadata"])
planRO=read(planROpin["path"])
need(planRO["schema"]=="root-new-plan-v8-metadata-readonly-seal.v1"and planRO["Root_and_two_independent_whole_Plan_and_HANDOFF_static_PASS"]is True and planRO["after_files"]==planmeta and planRO["after_directory"]==SPEC["plan_directory_metadata"],"Actual new reviewed Plan2 readonly seal required")
need(md(authority(PLAN.parent))==SPEC["plan_directory_metadata"]and stat.S_IMODE(SPEC["plan_directory_metadata"]["mode"])==0o555 and {p.name for p in PLAN.parent.iterdir()}=={"final_source_plan.json","HANDOFF.md"},"Exact readonly Plan2 directory required")
priorpins=SPEC["prior_qualified_plan_and_handoff"]
for r,m in zip(priorpins,SPEC["prior_qualified_plan_and_handoff_metadata"]):ro(r["path"],r,m)
priorCAPpin,priorCAPmeta=ro(SPEC["prior_v7_ownsha_capture"]["path"],SPEC["prior_v7_ownsha_capture"],SPEC["prior_v7_ownsha_capture_metadata"])
priorCAP=read(priorCAPpin["path"])
need(priorCAP["actual_job_id"]=="16999"and[priorCAP["plan"],priorCAP["handoff"]]==priorpins,"Actual prior16999 qualified V7 Plan/H tuples required")
canonical=SPEC["current_canonical_Source4"];canonicalmeta=SPEC["current_canonical_Source4_metadata"]
need(priorCAP["current_canonical_Source4_receipts"]==canonical and priorCAP["current_canonical_Source4_metadata_after"]==canonicalmeta and len(canonical)==len(canonicalmeta)==4,"Exact current canonicalSource4 bindings required")
def canonical_end():
 for r,m in zip(canonical,canonicalmeta):
  p=authority(r["path"]);need(md(p)==m and stat.S_ISREG(m["mode"])and stat.S_IMODE(m["mode"])==0o664 and m["nlink"]==1,"Only four literal current mutable Source leaves permitted")
  need(g.rec(p)==r and md(p)==m,"Current canonicalSource4 ownbytes/fullMD drift")
canonical_end()
plan=read(PLAN);old=read(priorpins[0]["path"])
roles=["formal13260_terminal_v3","native74_cache_catalog","native74_cache_binding","reference_free_e2e","formal_common_review","independent_statistics","scientific_report","final_delivery_tools","default_workflow_integration"]
need(len(plan)==len(old)==34 and list(plan)==list(old)and plan["schema"]=="final-source-closure-plan.v3"and plan["library_software_acceptance"]==SW[0]and[m["role"]for m in plan["modules"]]==roles,"Same34 keys/order/exactnine roles/current17002 software required")
need(plan["modules"][7]["sources"][-15:]==additionalrows and plan["modules"][7]["seeds"][-19:]==additional+SW,"Exact Source15 safeSeed19 ordered tails required")
need(len(plan["context_parent_seeds"])==17 and plan["context_parent_seeds"]==old["context_parent_seeds"]and len(plan["aliases"])==7 and plan["aliases"]==old["aliases"],"Exact ordered17 parents and seven aliases unchanged")
rewound=json.loads(json.dumps(plan,allow_nan=False));rewound["library_software_acceptance"]=old["library_software_acceptance"];rewound["modules"][7]["sources"]=rewound["modules"][7]["sources"][:-15];rewound["modules"][7]["seeds"]=rewound["modules"][7]["seeds"][:-19]
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
need((json.dumps(rewound,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode()==Path(priorpins[0]["path"]).read_bytes(),"Entire serialized raw V7 must rewind exactly")
def identity(r):g.receipt_shape(r);return(r["path"],r["bytes"],r["sha256"])
allsources=[r for m in plan["modules"]for r in m["sources"]];allseeds=[r for m in plan["modules"]for r in m["seeds"]]
need(len(allsources)==688 and len({r["repository_relative"]for r in allsources})==627 and len(allseeds)==3865 and len({identity(r)for r in allseeds})==3792 and len(plan["modules"][7]["sources"])==489 and len(plan["modules"][7]["seeds"])==3719,"Exact finite newPlan688/627/3865/3792/final489/3719 required")
need(not set(destinations)&{r["repository_relative"]for m in old["modules"]for r in m["sources"]},"New15 destination collision")
need(g.module_plan(plan)==plan["modules"],"Qualified module_plan pure object/lexical shape required, no child IO")
need(planpin["bytes"]==1985977 and planpin["bytes"]<2097152 and handoffpin["bytes"]==25414,"Exact reviewed newPlan/H sizes required")
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
 need([g.rec(r["path"])for r,m in controls]==[r for r,m in controls]and[md(authority(r["path"]))for r,m in controls]==[m for r,m in controls],"Qualified G17002.rec actual twelve own tuples/fullMD after each batch required")
qualified_rec_end()
protected=planRO["protected_inputs_after"]+planRO["protected_directories_after"]
need(planRO["protected_inputs_before"]==planRO["protected_inputs_after"]and planRO["protected_directories_before"]==planRO["protected_directories_after"]and len(protected)==4704,"Entire4704 protected metadata required")
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
OUT=authority(S/"runs")/("final_source_plan_v8_ownsha_"+jid)
need(not OUT.exists()and not OUT.is_symlink(),"Exclusive absent new ownSHA output required")
OUT.mkdir(mode=0o755);phase="own_new_PlanV8_and_twelve_controls_no_receipt_child_IO"
try:
 out=dict(schema="root-fixed-source-plan-v8-own-sha-control-capture.v1",status="ACTUAL_NEW_PLAN_V8_OWN_SHA_AND15_PINNED_SOURCE_DOC_ADDITIONS_CPU_VERIFIED_NOT_SOURCE_AUDIT_ACCEPTANCE",actual_job_id=jid,allocation=allocation,current_actual_readiness=readiness,current_readiness_own_CPU_receipts=[x[0]for x in readyvalues],plan=planpin,handoff=handoffpin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,control_receipts=[r for r,m in controls],control_metadata_before=[m for r,m in controls],control_metadata_after=[md(r["path"])for r,m in controls],software_acceptance=SW[0],software_control_receipts=SW,software_control_metadata_before=SPEC["qualified_software_control_metadata"],software_control_metadata_after=[md(r["path"])for r in SW],source_files=SPEC["qualified_frozen_source6"],original_executing_sources=SPEC["qualified_original_source6"],qualified_source12_metadata=source_meta,conditional_core_runtime=runtime,qualified_software17002_terminal_own_CPU_receipt=terminalpin,prior_qualified_PlanV7_and_Handoff=priorpins,qualified_prior16999_ownsha_capture=priorCAPpin,additional_15_Source_rows=additionalrows,additional_15_Source_metadata=additionalmeta,additional_19_safe_seed_receipts=additional+SW,current_canonical_Source4_receipts=canonical,current_canonical_Source4_metadata_before=canonicalmeta,current_canonical_Source4_metadata_after=[md(r["path"])for r in canonical],plan_directory_metadata_before=SPEC["plan_directory_metadata"],plan_directory_metadata_after=md(PLAN.parent),Source_n=688,destination_n=627,seed_n=3865,unique_seed_n=3792,role_n=9,parent_n=17,ordered_alias_n=7,all34keys_type_order_and_original_V7_serialized_bytes_rewind_PASS=True,qualified_module_plan_pure_shape_PASS=True,qualified_G17002_rec_all12_controls_pre_end_PASS=True,all_Source12_SW4_Core_controls12_Source15_canonical4_protected4704_pre_end_afteroutput_finalreadonly_PASS=True,plan_child_receipts_shape_only_no_child_IO=True,source_audit_executed=False,source_staged=False,published=False,ACTIVE_changed=False,compiler_or_tests_or_new_software_qualification_executed=False,scientific_receipt_children_read_or_hashed=False,historical_Slurm_queried=False,own_created_controls_LATE_COMPOSER_ONLY_NOT_PLAN_PREREQUISITES=True)
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
 print(json.dumps(dict(status=out["status"],capture=descriptor,plan=planpin,handoff=handoffpin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,qualified_software17002_terminal_own_CPU_receipt=terminalpin,Source_n=688,destination_n=627,seed_n=3865,unique_seed_n=3792,role_n=9,parent_n=17,final_output_directory_metadata=outdir,Plan_own_SHA_qualified_only_AFTER_fresh_terminal_RO_Root_and_independent_content_readback=True),sort_keys=True),flush=True)
except BaseException as e:
 try:
  failure=(json.dumps(dict(status="ACTUAL_PLAN_V8_OWN_SHA_UNQUALIFIED",actual_job_id=jid,phase=phase,reason_type=type(e).__name__,reason=str(e),source_staged=False,published=False,ACTIVE_changed=False),indent=2)+"\n").encode()
  with(OUT/"typed_incomplete.json").open("xb")as f:f.write(failure);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 except Exception as se:print("Readonly failure output best-effort: "+repr(se),file=sys.stderr,flush=True)
 raise
```
