# Root fixed Plan V9 production source audit from software 17005 and control 17006

This is a Root operational program, initially unexecuted. It authorizes one distinct CPU1/task1/16G/30min organ job, with job name test9_final_source_final_readonly_v3, GPU0, CORE -B without -I, CUDA empty, JAX cpu, user site and bytecode disabled, and BLAS/OMP/MKL1. Root alone submits it after Root and two whole static reviews, a metadata-only readonly seal, and an independent readonly readback.

Actual software 17005 passed 198 named tests. Actual control 17006 qualified Plan V9 and its HANDOFF. The readonly strict13 request uses those actual tuples and the unchanged Mapper, finite eight parent pairs, ordered17 parents, seven aliases, three false permission flags and four empty alias lists. It is not a Source acceptance until this actual production run completes and all saved content and terminal proofs pass independent readback. Metadata draft flags in request_metadata.json remain historical observations of its creation.

The program first captures strict actual current Slurm CPU1/GPU0 readiness with bounded RPCs and no proxy. It then verifies Source12, both source directories, software4, conditional CORE and the qualified software terminal before importing the frozen qualified main. The remaining finite controls, request, metadata, Plan, HANDOFF, control17006, terminal, software outer proof, request/Plan seals and Root Human/shell are checked after that qualified import and before production. All inputs and protected4915 metadata records are rechecked before, after, and after final readonly output creation. Exactly twelve own controls include the Plan and HANDOFF; qualified rec() also verifies those twelve and the four exact existing canonical hash-only sources. There is no generic live-source permission.

Production invokes only the actual frozen G17005 adapter through CORE -B with its actual --request and --out argv, using runpy and restoring sys.argv in finally. Its mandatory 198 producer sequence is part of the audit. No standalone unchanged software retest is requested. The program requires actual A/CA/I/C, SOURCE_INCLUSION_AUDIT_PASS, applied false, exact current allocation for A/CA/I (C has no allocation field), two new readonly runner6 sets, all198 unique named PASS without errors/failures/skips, and matching full four-family vendor/finite-worker/inventory13299/archive13298 proof/index pointers. It calls each preservation validator with its exact three arguments and the two history pure shape validators. Final whole artifact bytes and native metadata including ctime are checked after the final JSON seal. No metadata snapshot refresh, ctime exception, parent permission expansion, source identity rewrite, JSON rewrite or generic fallback is allowed.

This program neither stages Source nor writes Git/GitHub, packages, restores or promotes ACTIVE. New readiness, claims, Human/shell, root execution proof and terminal records are LATE Composer evidence, not prerequisites of their own Plan. Both original59376 unexecuted and REV160005 executed17006 Humans and their paired readonly proof must remain distinct for later finite Source publication. Previous failures and every original plan, request, source, logs, receipt and seal are immutable. The actual field/cause of failed17004 remains unobserved; the accepted final readonly fix is not retroactive cause proof.

A successful CPU final stdout descriptor remains unqualified until fresh terminal COMPLETED0:0, Root plus two whole content readbacks and metadata-only readonly sealing with independent whole readback. Any actual failure must retain its output, traceback and controls without replaying this job. The remaining chain is new inclusion runner stage, finite late Source publication, private full-history CPU bundle, complete-tree public distinct sole-baseline-parent commit and draft PR attachment, genuine public CPU readback before qualification, F compose/package, explicit CORE extract, full indexed restore plus history semantics and both metadata/ROOT298 checks, ACTIVE last. Scope remains COMPUTATIONAL_ONLY, without experimental binding, blockade, clinical or superiority claims.

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
D = S / "submissions" / ("final_source_v9_production_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_final_source_final_readonly_v3", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-source-v9-production-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_SOURCE_V9_PRODUCTION_AUDIT_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_SOURCE_V9_PRODUCTION_AUDIT_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_SOURCE_V9_PRODUCTION_AUDIT_NOT_EXECUTED"
obj = {"schema": "root-current-owned-source-v9-production-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
SPEC = json.loads("{\"qualified_source_software\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/acceptance.json\", \"bytes\": 6562, \"sha256\": \"d7bb3b58dd24ed76ce3b55136a37a997774f1cd77c0debb94f484847c80d278d\"}, \"qualified_original_source6\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_closure.py\", \"bytes\": 223420, \"sha256\": \"895f34ae9444a5e08ab752cb557d17bd49c463475d39d5eb179d37cfb3be0608\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/test_final_source_closure.py\", \"bytes\": 159993, \"sha256\": \"012821051ca9708724e66ad39e7b66986f955f736c480901786cd6c2cb3893e8\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_cpu.sbatch\", \"bytes\": 1607, \"sha256\": \"2a19202da1fe8913b4284ded128706688a15a2d9b6c976bea693d9f6e100a7ef\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/HANDOFF.md\", \"bytes\": 17911, \"sha256\": \"7985ce5ba683b4305dc277e9f6b29a01429556cb84b9ae41375352703e0ee415\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 4611, \"sha256\": \"2b812507033aebfa05724433b46005bb67fc42740cfe1ecba554a7b78d882101\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_context_adapter.py\", \"bytes\": 12691, \"sha256\": \"f8379565b33c5efa5faea4dcddec9e48a416d5ca823bf9443255789cd463e07c\"}], \"qualified_frozen_source6\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_closure.py\", \"bytes\": 223420, \"sha256\": \"895f34ae9444a5e08ab752cb557d17bd49c463475d39d5eb179d37cfb3be0608\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/test_final_source_closure.py\", \"bytes\": 159993, \"sha256\": \"012821051ca9708724e66ad39e7b66986f955f736c480901786cd6c2cb3893e8\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_cpu.sbatch\", \"bytes\": 1607, \"sha256\": \"2a19202da1fe8913b4284ded128706688a15a2d9b6c976bea693d9f6e100a7ef\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/HANDOFF.md\", \"bytes\": 17911, \"sha256\": \"7985ce5ba683b4305dc277e9f6b29a01429556cb84b9ae41375352703e0ee415\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 4611, \"sha256\": \"2b812507033aebfa05724433b46005bb67fc42740cfe1ecba554a7b78d882101\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_context_adapter.py\", \"bytes\": 12691, \"sha256\": \"f8379565b33c5efa5faea4dcddec9e48a416d5ca823bf9443255789cd463e07c\"}], \"qualified_source12_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_closure.py\", \"bytes\": 223420, \"inode\": 144115643443092398, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/test_final_source_closure.py\", \"bytes\": 159993, \"inode\": 144115643443092399, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_cpu.sbatch\", \"bytes\": 1607, \"inode\": 144115643443092400, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/HANDOFF.md\", \"bytes\": 17911, \"inode\": 144115643443092401, \"mtime_ns\": 1792102471000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 4611, \"inode\": 144115643443092402, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1/final_source_context_adapter.py\", \"bytes\": 12691, \"inode\": 144115643443092403, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_closure.py\", \"bytes\": 223420, \"inode\": 144115643493442364, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/test_final_source_closure.py\", \"bytes\": 159993, \"inode\": 144115643493442365, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_cpu.sbatch\", \"bytes\": 1607, \"inode\": 144115643493442366, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/HANDOFF.md\", \"bytes\": 17911, \"inode\": 144115643493442367, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/FINAL_SOURCE_CHECKLIST.md\", \"bytes\": 4611, \"inode\": 144115643493442368, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner/final_source_context_adapter.py\", \"bytes\": 12691, \"inode\": 144115643493442369, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"qualified_original_source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix7_final_readonly_lifecycle1\", \"bytes\": 4096, \"inode\": 144115643443092397, \"mtime_ns\": 1792102410000000000, \"ctime_ns\": 1792102948000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"qualified_frozen_source_directory\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/runner\", \"bytes\": 4096, \"inode\": 144115643493442363, \"mtime_ns\": 1792103323000000000, \"ctime_ns\": 1792103323000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"qualified_software_controls\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/acceptance.json\", \"bytes\": 6562, \"sha256\": \"d7bb3b58dd24ed76ce3b55136a37a997774f1cd77c0debb94f484847c80d278d\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/contracts.json\", \"bytes\": 2137, \"sha256\": \"7d333ed0c2b3370759ceb5b2f775cd48c135f3a878319352f429a3c0022ca1df\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/contracts.txt\", \"bytes\": 36566, \"sha256\": \"3e746de3e0890a250c38b8aae0a6db4f8c9e4edaec4b7635abc3aa549c6e67d2\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/source_snapshot.json\", \"bytes\": 15783, \"sha256\": \"10f0397322fd26550e9a260053b784cc5d34b22aa3e46cfb77336a5ef8b90e90\"}], \"qualified_software_control_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/acceptance.json\", \"bytes\": 6562, \"inode\": 144115643493448230, \"mtime_ns\": 1792103360000000000, \"ctime_ns\": 1792103360000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/contracts.json\", \"bytes\": 2137, \"inode\": 144115643493448228, \"mtime_ns\": 1792103360000000000, \"ctime_ns\": 1792103360000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/contracts.txt\", \"bytes\": 36566, \"inode\": 144115643493442370, \"mtime_ns\": 1792103360000000000, \"ctime_ns\": 1792103360000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_final_readonly_software_17005/source_snapshot.json\", \"bytes\": 15783, \"inode\": 144115643493448229, \"mtime_ns\": 1792103360000000000, \"ctime_ns\": 1792103360000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"conditional_CORE_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python\", \"bytes\": 10, \"inode\": 144115618512131424, \"mtime_ns\": 1790940371000000000, \"ctime_ns\": 1790940371000000000, \"mode\": 41471, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\", \"bytes\": 25916456, \"inode\": 144115618512129393, \"mtime_ns\": 1790940364000000000, \"ctime_ns\": 1790940383000000000, \"mode\": 33277, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"source_software_terminal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_final_readonly_software17005_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 5076915, \"inode\": 144115643443092431, \"mtime_ns\": 1792103622000000000, \"ctime_ns\": 1792103622000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"software_outer_proof\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_final_readonly_software_outer_17005/execution_control.json\", \"bytes\": 44435, \"sha256\": \"42453546dafb0b96abacbf871aed090d534a6276b88c26e8799c1f8e797e7533\"}, \"software_outer_proof_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_final_readonly_software_outer_17005/execution_control.json\", \"bytes\": 44435, \"inode\": 144115643493448231, \"mtime_ns\": 1792103361000000000, \"ctime_ns\": 1792103361000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"plan_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17005_v9/final_source_plan.json\", \"bytes\": 1998209, \"inode\": 144115643443092433, \"mtime_ns\": 1792103833000000000, \"ctime_ns\": 1792104052000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17005_v9/HANDOFF.md\", \"bytes\": 17477, \"inode\": 144115643443092434, \"mtime_ns\": 1792103833000000000, \"ctime_ns\": 1792104052000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"plan_readonly_seal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v9_from17005_metadata_readonly_seal/receipt.json\", \"bytes\": 5079045, \"inode\": 144115643443092436, \"mtime_ns\": 1792104053000000000, \"ctime_ns\": 1792104053000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"current_canonical_Source4\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\", \"bytes\": 2225, \"sha256\": \"d602956154fb396fd14d7737c360d7d35144b4e6ca6c3d1c51eb6dc401e42615\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\", \"bytes\": 24234, \"sha256\": \"c8fe4495439826f0882b4c43952926e5de5361f88460320cc117d003352ff345\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\", \"bytes\": 1633, \"sha256\": \"2d40850d19c7835d658e7154e5a1cb53ae763e31d360b41eec253397f2c5befb\"}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\", \"bytes\": 6148, \"sha256\": \"c83e427f73ff1545253d64dbb165c7e60328bb698721d1e03663e6ea7d7c403f\"}], \"current_canonical_Source4_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\", \"bytes\": 2225, \"inode\": 144115543165691905, \"mtime_ns\": 1791727539000000000, \"ctime_ns\": 1791727539000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\", \"bytes\": 24234, \"inode\": 144115543165691892, \"mtime_ns\": 1791727495000000000, \"ctime_ns\": 1791727495000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\", \"bytes\": 1633, \"inode\": 144115543165691947, \"mtime_ns\": 1791727539000000000, \"ctime_ns\": 1791727539000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\", \"bytes\": 6148, \"inode\": 144115543165691893, \"mtime_ns\": 1791727495000000000, \"ctime_ns\": 1791727495000000000, \"mode\": 33204, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"source_software_terminal_receipt\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_final_readonly_software17005_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 5076915, \"sha256\": \"0f5e71fd36b6796fa86a78a4859c13b5a5cab1ae6e78eedbd0d8f7e4ea055406\"}, \"new_request_path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17005_v9/request.json\", \"new_request2_metadata\": [{\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17005_v9/request.json\", \"bytes\": 6538, \"inode\": 144115643443092457, \"mtime_ns\": 1792105091000000000, \"ctime_ns\": 1792105451000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17005_v9/request_metadata.json\", \"bytes\": 25215, \"inode\": 144115643443092458, \"mtime_ns\": 1792105091000000000, \"ctime_ns\": 1792105451000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}], \"new_request_directory_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17005_v9\", \"bytes\": 4096, \"inode\": 144115643443092456, \"mtime_ns\": 1792105091000000000, \"ctime_ns\": 1792105451000000000, \"mode\": 16749, \"dev\": 1119461688, \"nlink\": 2, \"uid\": 6263900, \"gid\": 6263900}, \"request_readonly_seal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_context_request_v9_from17005_metadata_readonly_seal/receipt.json\", \"bytes\": 5108894, \"inode\": 144115643443092460, \"mtime_ns\": 1792105452000000000, \"ctime_ns\": 1792105452000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"plan_own_capture\": {\"bytes\": 61469, \"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v9_ownsha_17006/capture.json\", \"sha256\": \"dae77e40b7f01741646d6c222952d183595c995117f6c29193ef175f3c5292ca\"}, \"plan_own_capture_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v9_ownsha_17006/capture.json\", \"bytes\": 61469, \"inode\": 144115643493448243, \"mtime_ns\": 1792104650000000000, \"ctime_ns\": 1792104650000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"plan_own_terminal_metadata\": {\"path\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_plan_v9_ownsha17006_actual_terminal_metadata_seal/receipt.json\", \"bytes\": 5121460, \"inode\": 144115643443092455, \"mtime_ns\": 1792104877000000000, \"ctime_ns\": 1792104877000000000, \"mode\": 33060, \"dev\": 1119461688, \"nlink\": 1, \"uid\": 6263900, \"gid\": 6263900}, \"root_control_human\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_FINAL_SOURCE_PLAN_V9_PRODUCTION_AUDIT_FROM17005_17006_20261015.md\", \"primary_wrap\": \"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v9_production_audit_from17005_17006_primary_claim/wrap.sh\", \"protected_metadata_union_count\": 4915}")
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
OUT=authority(S/"runs")/("final_source_final_readonly_audit_"+jid)
AUX=OUT.with_name(OUT.name+"_context_adapter")
PROOF=authority(S/"submissions")/("final_source_final_readonly_audit_"+jid+"_root_execution_control")
need(all(not p.exists()and not p.is_symlink()for p in(OUT,AUX,PROOF)),"Exclusive absent audit/AUX/rootproof namespaces required")
adapter=Path(SPEC["qualified_frozen_source6"][-1]["path"])
need(adapter.name=="final_source_context_adapter.py","Exact actual frozen adapter required")
actual_argv=[str(adapter),"--request",str(QP),"--out",str(OUT)]
savedargv=list(sys.argv);phase="actual_frozen_G17005_adapter_mandatory198_producer"
try:
 sys.argv=actual_argv
 try:runpy.run_path(str(adapter),run_name="__main__")
 finally:sys.argv=savedargv
 need(sys.argv==savedargv,"Root process argv lifecycle not restored")
 phase="actual_A_CA_I_C_and_four_finite_preservation_proofs"
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
 need(contracts["status"]=="PASS"and type(contracts["tests"])is int and contracts["tests"]==198 and contracts["failures"]==0 and contracts["errors"]==0 and contracts["owned_python_compile_PASS"]is True and contracts["bash_syntax_PASS"]is True,"Mandatory actual198 producer/compiler/bash required")
 output_controls.append(ro(contracts["log"]["path"],contracts["log"]))
 log=Path(contracts["log"]["path"]).read_text()
 need(re.findall(r"(?:^|\n)Ran ([0-9]+) tests?\b",log)==["198"]and re.search(r"(?:^|\n)OK(?:\n|$)",log)and not re.search(r"(?:FAIL|ERROR|skipped=|\[SKIP\])",log),"Actual198 contract log must be complete")
 need(contracts["tested_source_files"]==I["runner_source_snapshot"],"Actual198 tested current runner6 required")
 case_lines=[x for x in log.splitlines()if x.startswith("test")]
 named198=re.findall(r"(?m)^(test[^\n]+) \.\.\. ok$",log)
 need(len(case_lines)==len(named198)==len(set(named198))==198 and all(x.endswith(" ... ok")for x in case_lines),"Exactly198 unique namedPASS with no skipped or other test result required")
 output_dirs=[]
 for directory in(OUT/"runner",AUX/"runner"):
  before=md(authority(directory))
  need(stat.S_ISDIR(before["mode"])and stat.S_IMODE(before["mode"])==0o555 and before["nlink"]==2 and{p.name for p in directory.iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Actual two new readonly runner6 directory universes required")
  output_dirs.append(before)
 proof_families=[("vendor_example_opaque_leaf_proof","vendor_example_opaque_aliases",g.verify_vendor_example_preservation),("finite_worker_control_proof","finite_worker_control_aliases",g.verify_finite_worker_preservation),("inventory_history_opaque_leaf_proof","inventory_history_opaque_aliases",g.verify_inventory_history_preservation),("archive_parent_history_opaque_leaf_proof","archive_parent_history_opaque_aliases",g.verify_archive_parent_history_preservation)]
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
 need(all(x.get("source_staged")is False and x.get("ACTIVE_changed")is False for x in(A,CA,I)),"No Source stage or promotion allowed")
 def outputs_end():
  for x in output_dirs:need(md(authority(x["path"]))==x and{p.name for p in Path(x["path"]).iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Actual new runner6 directory metadata/universe drift")
  for r,x in output_controls:ro(r["path"],r,x)
  for p,i,f in proof_objects:f(p,i,allocation)
  for r,x in output_controls:need(md(authority(r["path"]))==x,"Output metadata drift after finite proof verification")
  for x in output_dirs:need(md(authority(x["path"]))==x and{p.name for p in Path(x["path"]).iterdir()}=={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]},"Actual new runner6 directories drift after finite proof verification")
 outputs_end();inputs_end()
 phase="exclusive_final_root_execution_proof_no_staging"
 PROOF.mkdir(mode=0o755)
 result=dict(schema="root-actual-final-source-v9-production-execution-control.v1",status="ROOT_ACTUAL_NEW_SOURCE198_A_CA_I_C_AND_FOUR_FINITE_PRESERVATION_PROOFS_CPU_VERIFIED_NOT_STAGED_NOT_PUBLISHED",actual_job_id=jid,allocation=allocation,current_actual_readiness=readiness,current_readiness_own_CPU_receipts=[r for r,x in readyvalues],actual_direct_frozen_adapter_argv=actual_argv,actual_new_library_acceptance=output_controls[0][0],actual_new_adapter_acceptance=output_controls[1][0],actual_new_inclusion=output_controls[2][0],actual_new_closure=output_controls[3][0],actual_new_runner_source_snapshot=I["runner_source_snapshot"],qualified_software_acceptance=SPEC["qualified_source_software"],qualified_source12=sourcepins,qualified_source12_metadata=source_meta,qualified_software4=SPEC["qualified_software_controls"],conditional_core_runtime=runtime,control_receipts=[r for r,x in controls],control_metadata_before=[x for r,x in controls],control_metadata_after=[md(r["path"])for r,x in controls],current_canonical_Source4_receipts=canonical,current_canonical_Source4_metadata_before=canonicalmeta,current_canonical_Source4_metadata_after=[md(r["path"])for r in canonical],protected_input_metadata_unique=len(protected),mandatory_contracts=contractpin,mandatory_198_producer_PASS=True,mandatory_198_unique_named_PASS_no_failure_error_skip=True,mandatory_198_named_tests=named198,actual_new_runner6_directory_metadata=output_dirs,qualified_G17005_rec_all12_and_postread_metadata_PASS=True,actual_current_source_and_runtime_pre_end_after_final_readonly_PASS=True,all_A_CA_I_C_finite_proof_alias_pointers_equal=True,exact_four_finite_preservation_validators_three_arguments_PASS=True,output_artifact_receipts=[r for r,x in output_controls],output_artifact_metadata=[x for r,x in output_controls],request_own_cpu_tuple=qpin,metadata_own_cpu_tuple=mpin,Root_Human_and_precreated_shell_own_CPU_tuples=[ownhuman,ownwrap],source_staged=False,published=False,ACTIVE_changed=False,raw_JSON_changed=False,scientific_endpoint_acceptance_performed=False,own_created_controls_LATE_not_Plan_prerequisites=True,qualification_requires_fresh_actual_terminal_Root_plus_two_content_and_independent_RO=True)
 raw=(json.dumps(result,indent=2,allow_nan=False,ensure_ascii=False)+"\n").encode();rp=PROOF/"execution_control.json"
 with rp.open("xb")as f:f.write(raw);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444);os.fsync(f.fileno())
 proofpin=g.rec(rp);proofmeta=md(rp)
 need(rp.read_bytes()==raw and read(rp)==result and stat.S_IMODE(proofmeta["mode"])==0o444 and proofmeta["nlink"]==1,"Whole own final proof readonly reread required")
 outputs_end();inputs_end();PROOF.chmod(0o555)
 fd=os.open(str(PROOF),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
 finaldir=md(authority(PROOF))
 need(stat.S_IMODE(finaldir["mode"])==0o555 and finaldir["nlink"]==2 and{p.name for p in PROOF.iterdir()}=={"execution_control.json"}and rp.read_bytes()==raw and read(rp)==result and g.rec(rp)==proofpin and md(rp)==proofmeta,"Final own proof exact readonly universe required")
 outputs_end();inputs_end()
 need(md(PROOF)==finaldir and md(rp)==proofmeta,"Final own proof metadata after all input/output checks differs")
 print(json.dumps(dict(status=result["status"],execution_control=proofpin,acceptance=output_controls[0][0],context_adapter_acceptance=output_controls[1][0],inclusion=output_controls[2][0],closure=output_controls[3][0],actual_new_runner_source_snapshot=I["runner_source_snapshot"],request=qpin,request_metadata=mpin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,qualification_still_requires_fresh_terminal_and_full_Root_two_independent_readbacks=True),sort_keys=True),flush=True)
except BaseException as e:
 try:
  if not PROOF.exists():PROOF.mkdir(mode=0o755)
  if stat.S_IMODE(PROOF.stat().st_mode)&0o222:
   fail=(json.dumps(dict(schema="root-final-source-v9-production-incomplete.v1",status="ROOT_FINAL_SOURCE_V9_PRODUCTION_UNQUALIFIED_NO_STAGING",actual_job_id=jid,phase=phase,reason_type=type(e).__name__,reason=str(e),actual_argv=actual_argv,source_staged=False,published=False,ACTIVE_changed=False),indent=2)+"\n").encode()
   with(PROOF/"typed_incomplete.json").open("xb")as f:f.write(fail);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 except Exception as se:print("Failure proof best-effort "+repr(se),file=sys.stderr,flush=True)
 raise
```
