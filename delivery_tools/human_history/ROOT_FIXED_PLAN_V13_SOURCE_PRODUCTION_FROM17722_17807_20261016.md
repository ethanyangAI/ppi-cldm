# Root fixed Plan V13 Source production from software17722 and actual Plan ownSHA17807

TEXT STOP FOR WHOLE STATIC REVIEW. UNEXECUTED and UNQUALIFIED when authored. This document is an operational Root control, not a new software gate or Source acceptance.

The current library is the exact frozen six-file runner from actual software17722, with 356 unique named contracts accepted and actual software terminal independently qualified. Plan13 and HANDOFF are bound to actual owned CPU17807 tuples and its qualified terminal; strict13 Q13/M49 and QRO41 are actual reviewed readonly controls. Only software and Plan tuples changed versus old Q12. The embedded SPEC has exactly30 keys and authenticates current14537 original native records; integers retain Python exact values. The separate unbound author TXT draft is preserved as LATE history and never executed. No blanket replacement of historical namespaces was performed.

Run only after Root and TWO whole-document static reviews, followed by a Root metadata-only readonly seal of this Human and the unbound TXT draft and independent readback. Root alone submits ONE new job. The primary uses a readonly script FILE with #!/bin/bash, not --wrap:
- job name test9_source_plan_v13_production_cpu; one node/task/CPU,16G,30minutes,partitionorgan,accountu21111210118,qosnormal,GPU0,no override.
- chdir /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery; log basenames source_plan_v13_production_%j.out and .err under logs.
- CORE -B/no-I/unoptimized, empty CUDA_VISIBLE_DEVICES,JAX_PLATFORMS=cpu,PYTHONNOUSERSITE=1,PYTHONDONTWRITEBYTECODE=1,OPENBLAS/OMP/MKL threads1,PYTHONPATH unset.
- export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/source_plan_v13_production_${SLURM_JOB_ID}; do NOT precreate TMPDIR. The code checks absence and creates it after current allocation and input guards.
- primary fixed path /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_v13_production_from17722_17807_primary_claim/wrap.sh. The shell here-document must equal the entire Python fence below, with a final newline and PY delimiter.

The outer current-allocation check requires actual scontrol owner/name/account/qos/organ/CPU1/task1/16G30 and all present TRES GPU namespaces0, plus a unique actual six-column current RUNNING sacct row. It bounds readiness to60seconds/30attempts and each RPC5seconds, retaining partial raw outputs and null return code on timeout. Accepted G.cpu() then freshly rechecks actual allocation. No old-job live query, scheduler forecast or requested envelope substitutes for actual allocation.

Before first project import, fixed original/frozen Source12,software4,Core2 and twelve Root controls are authenticated. Those12 roles are Q,M,Plan,H,ownCAP,ownTRO,softwareTRO,softwareCO,QRO,PlanRO,selfHuman,primarywrap; they differ from ownSHA capture roles. Actual coupled SourceRO33 and softwareHRO31 are authenticated from CAP56 controls5/6; eight fixed control directories and two source-proof directories retain original metadata. Common is lstat-only, with no payload/hash/resolve/readlink/authority lookup. Fixed historical Source2 and supplementary launcher918 receive own-byte checks only and are never imported, compiled or executed. Four current canonical Source leaves retain their original0664 identities. No generic path permission or dedup change is granted.

The exact direct frozen adapter is invoked with --request actualQ13 --out newexclusiveOUT. No audit subcommand, request-sha flag, old software launcher or shell stage route is used. Its mandatory356 producer is runtime audit production; it is not a separate unchanged software qualification. A,CA,I,C must bind actual current allocation, actual tuples and exact new runner locations; I must be SOURCE_INCLUSION_AUDIT_PASS/appliedfalse/issues0. Full contract names/classes/order must equal actual17722 accepted356. The nine primary module gates, Base683, ordered17 contexts, seven aliases, finite8/16 metadata, inherited default109/44 and complete old Plan12 serialized inverse remain strict.

Exactly SIX finite preservation families are validated with current three-argument validators. Four history-v2 authorities and coupled20 contexts remain limited to actual observations. Worker23/22canonical logical/ancestor routes become metadata-only exceptions only after exact current proof verification; no worker scientific bytes are opened through that exception. Authenticated historical Source2 ordinary C/I coverage retains compatible identity/destination/kind and actual module roles, without generic dedup expansion. Catalog MSA projection is an additional pure graph check, not a seventh family: original producer metadata must be enrolled before Root reads its exact three inputs, their saved-native fences repeat, and full actual C projection is checked after every graph reread. No forced observation count replaces actual context observations.

After ALL A/CA/I/C JSON and fullbytes are reread, all output controls, six families, four history authorities, catalog projection, Source12/SW4/Core/controls12 and all saved native baselines are rechecked. Root exclusively writes/flushed/fsynced444 execution_control.json with60 fields, rereads full JSON/bytes, makes its directory555 and finishes with TRUE-LAST lstat-only union before final CPU descriptor. Any failure preserves partial artifacts and rethrows original error. PASS-shaped intermediate artifacts are UNQUALIFIED until actual fresh terminal, Root+TWO whole content readbacks and independent terminal readonly verification.

Nothing stages Source, writes Git/GitHub, packages, restores or promotes ACTIVE. This Human, draft, Root claims/readiness/logs/terminal controls and full CAP/Q/M/RO proof objects remain explicit finite LATE Composer/publication obligations and cannot become own Plan prerequisites. Failed fix12 history and all prior Plan/Q/source/proofs remain preserved. Actual audit success must precede selecting its NEW inclusion.runner_source_snapshot for CORE -B stage. A complete finite LATE publication and compatible Composer must precede complete private/public source trees and isolated full restore. Overall delivery stays INCOMPLETE. Scientific scope remains COMPUTATIONAL_ONLY, with no experimental binding/blockade, clinical efficacy, arbitrary-pair reliability or workflow superiority claim.

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
D = S / "submissions" / ("source_plan_v13_production_current_sacct_readiness_" + jid)
if D.exists() or D.is_symlink():
    raise SystemExit("Exclusive absent current readiness namespace required")
D.mkdir(mode=0o755, exist_ok=False)
readiness_native_original=[]
def native_metadata(p):
    p=Path(p);x=p.lstat();return dict(path=str(p),bytes=x.st_size,inode=x.st_ino,mtime_ns=x.st_mtime_ns,ctime_ns=x.st_ctime_ns,mode=x.st_mode,dev=x.st_dev,nlink=x.st_nlink,uid=x.st_uid,gid=x.st_gid)
def persist(name, data):
    p = D / name
    with p.open("xb") as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno()); os.fchmod(stream.fileno(), 0o444); os.fsync(stream.fileno())
    st = p.lstat()
    readiness_native_original.append(native_metadata(p))
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
    required = {"JobId": jid, "JobName": "test9_source_plan_v13_production_cpu", "Account": "u21111210118", "QOS": "normal", "WorkDir": str(S), "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-source-v13-production-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_SOURCE_V13_PRODUCTION_AUDIT_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_SOURCE_V13_PRODUCTION_AUDIT_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_SOURCE_V13_PRODUCTION_AUDIT_NOT_EXECUTED"
obj = {"schema": "root-current-owned-source-v13-production-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
readiness_directory_original=native_metadata(D)
readiness_names_original={Path(x["path"]).name for x in readiness_native_original}
if selected is None:
    raise SystemExit(72)
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "production_adapter_next_not_acceptance": True}), flush=True)

# Only entered after actual current owned CPU1/GPU0 readiness.
import hashlib,importlib.util,runpy
R=Path("/lustre/users/u21111210118/projects/test9");CORE=R/"env/core/bin/python";REAL=CORE.with_name("python3.11")
SPEC=json.loads("{\"conditional_CORE_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/env/core/bin/python\",\"bytes\":10,\"inode\":144115618512131424,\"mtime_ns\":1790940371000000000,\"ctime_ns\":1790940371000000000,\"mode\":41471,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\",\"bytes\":25916456,\"inode\":144115618512129393,\"mtime_ns\":1790940364000000000,\"ctime_ns\":1790940383000000000,\"mode\":33277,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"qualified_original_source6\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_closure.py\",\"bytes\":344832,\"sha256\":\"761829c3cbf2dc4bf1f790c2ec80b7fd0fdb2802adf2854d69360164114fa516\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/test_final_source_closure.py\",\"bytes\":386616,\"sha256\":\"892a20501bbc27ef131a2824d067c9bd7e58256f1b2aff4b593bbf57cb1caa91\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_cpu.sbatch\",\"bytes\":1675,\"sha256\":\"67bda42b010ca2a67108bf3db349ef569ff5f93358e4a665f1c74e4b5a077a14\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/HANDOFF.md\",\"bytes\":19743,\"sha256\":\"be6d5a31b25e9f05906e313872942a9df89954b3bcd945d9e2c1f5983468bbe6\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5185,\"sha256\":\"2018fa544edd313211b2e8f1eef5fa12751b26f5122a688b898397dcaddcf1fb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_context_adapter.py\",\"bytes\":23970,\"sha256\":\"e593ad54990028e3b285d938a291058c39c3b86ebe647cd017265af9907adae3\"}],\"qualified_frozen_source6\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_closure.py\",\"bytes\":344832,\"sha256\":\"761829c3cbf2dc4bf1f790c2ec80b7fd0fdb2802adf2854d69360164114fa516\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/test_final_source_closure.py\",\"bytes\":386616,\"sha256\":\"892a20501bbc27ef131a2824d067c9bd7e58256f1b2aff4b593bbf57cb1caa91\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_cpu.sbatch\",\"bytes\":1675,\"sha256\":\"67bda42b010ca2a67108bf3db349ef569ff5f93358e4a665f1c74e4b5a077a14\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/HANDOFF.md\",\"bytes\":19743,\"sha256\":\"be6d5a31b25e9f05906e313872942a9df89954b3bcd945d9e2c1f5983468bbe6\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5185,\"sha256\":\"2018fa544edd313211b2e8f1eef5fa12751b26f5122a688b898397dcaddcf1fb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_context_adapter.py\",\"bytes\":23970,\"sha256\":\"e593ad54990028e3b285d938a291058c39c3b86ebe647cd017265af9907adae3\"}],\"qualified_source12_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_closure.py\",\"bytes\":344832,\"inode\":144115643443094275,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/test_final_source_closure.py\",\"bytes\":386616,\"inode\":144115643443094276,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_cpu.sbatch\",\"bytes\":1675,\"inode\":144115643443094277,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/HANDOFF.md\",\"bytes\":19743,\"inode\":144115643443094278,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5185,\"inode\":144115643443094279,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_context_adapter.py\",\"bytes\":23970,\"inode\":144115643443094280,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_closure.py\",\"bytes\":344832,\"inode\":144115643979967842,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/test_final_source_closure.py\",\"bytes\":386616,\"inode\":144115643979967843,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_cpu.sbatch\",\"bytes\":1675,\"inode\":144115643979967844,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/HANDOFF.md\",\"bytes\":19743,\"inode\":144115643979967845,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5185,\"inode\":144115643979967846,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_context_adapter.py\",\"bytes\":23970,\"inode\":144115643979967847,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"qualified_original_source_directory\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1\",\"bytes\":4096,\"inode\":144115643443094274,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"qualified_frozen_source_directory\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner\",\"bytes\":4096,\"inode\":144115643979967841,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"qualified_software_controls\":[{\"bytes\":6668,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/acceptance.json\",\"sha256\":\"edb92387fc2c6e3b37cee25968e06445f8180d9a3bef85af937232329d124a9a\"},{\"bytes\":2214,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/contracts.json\",\"sha256\":\"457b4fc15361ea4112ea88ce40fe9d8c61060c6398aac7544f98235f7197b1bd\"},{\"bytes\":73394,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/contracts.txt\",\"sha256\":\"39731c16206b887b472ef86d4a91a3e7261f76bf20f6837a0e1ed31c8a15e767\"},{\"bytes\":16019,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/source_snapshot.json\",\"sha256\":\"624fa07f9adad5d20e64d33a7e0001bee1323cb8ad5f368a1649b5cdea2d277a\"}],\"qualified_software_control_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/acceptance.json\",\"bytes\":6668,\"inode\":144115643979986259,\"mtime_ns\":1792167903000000000,\"ctime_ns\":1792167903000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/contracts.json\",\"bytes\":2214,\"inode\":144115643979986257,\"mtime_ns\":1792167903000000000,\"ctime_ns\":1792167903000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/contracts.txt\",\"bytes\":73394,\"inode\":144115643979967848,\"mtime_ns\":1792167903000000000,\"ctime_ns\":1792167903000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/source_snapshot.json\",\"bytes\":16019,\"inode\":144115643979986258,\"mtime_ns\":1792167903000000000,\"ctime_ns\":1792167903000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"qualified_source_software\":{\"bytes\":6668,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/acceptance.json\",\"sha256\":\"edb92387fc2c6e3b37cee25968e06445f8180d9a3bef85af937232329d124a9a\"},\"source_software_terminal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_catalog_msa_gap_contracts17722_actual_software_terminal_metadata_readonly_seal/receipt.json\",\"bytes\":15460810,\"inode\":144115643443094507,\"mtime_ns\":1792168494000000000,\"ctime_ns\":1792168494000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"source_software_terminal_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_catalog_msa_gap_contracts17722_actual_software_terminal_metadata_readonly_seal/receipt.json\",\"bytes\":15460810,\"sha256\":\"a692e6fcae56e2274bbf06138cf8ecacc21f3a51b828651aed20870ba2e07912\"},\"plan_own_capture\":{\"bytes\":65003,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_ownsha_17807/capture.json\",\"sha256\":\"a35e971c9cb9b0304b4b46d31180ed442931c36a2f1b69294d30d8e32d719858\"},\"plan_own_capture_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_ownsha_17807/capture.json\",\"bytes\":65003,\"inode\":144115643979987129,\"mtime_ns\":1792170809000000000,\"ctime_ns\":1792170809000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"new_request_path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17722_v13/request.json\",\"new_request2_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17722_v13/request.json\",\"bytes\":6550,\"inode\":144115643443094569,\"mtime_ns\":1792171714000000000,\"ctime_ns\":1792172077000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17722_v13/request_metadata.json\",\"bytes\":28480,\"inode\":144115643443094570,\"mtime_ns\":1792171714000000000,\"ctime_ns\":1792172077000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"plan_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17722_v13/final_source_plan.json\",\"bytes\":2063544,\"inode\":144115643443094510,\"mtime_ns\":1792168979000000000,\"ctime_ns\":1792169684000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17722_v13/HANDOFF.md\",\"bytes\":21636,\"inode\":144115643443094511,\"mtime_ns\":1792168979000000000,\"ctime_ns\":1792169684000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"plan_own_terminal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_ownsha17807_actual_terminal_metadata_readonly_seal/receipt.json\",\"bytes\":15497494,\"inode\":144115643443094567,\"mtime_ns\":1792171342000000000,\"ctime_ns\":1792171342000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"software_outer_proof\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_catalog_msa_gap_contracts_software_outer_17722/execution_control.json\",\"bytes\":372881,\"sha256\":\"04a968137922f20eeb323ad416612ac31dd8354a56c8f292662cfcaa32be0597\"},\"software_outer_proof_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_catalog_msa_gap_contracts_software_outer_17722/execution_control.json\",\"bytes\":372881,\"inode\":144115643979986260,\"mtime_ns\":1792167909000000000,\"ctime_ns\":1792167909000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"request_readonly_seal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_context_request_metadata_readonly_seal/receipt.json\",\"bytes\":15504515,\"inode\":144115643443094572,\"mtime_ns\":1792172078000000000,\"ctime_ns\":1792172078000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"plan_readonly_seal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_from17722_metadata_readonly_seal/receipt.json\",\"bytes\":15458052,\"inode\":144115643443094519,\"mtime_ns\":1792169685000000000,\"ctime_ns\":1792169685000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"root_control_human\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V13_SOURCE_PRODUCTION_FROM17722_17807_20261016.md\",\"primary_wrap\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_v13_production_from17722_17807_primary_claim/wrap.sh\",\"current_canonical_Source4\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\",\"bytes\":2225,\"sha256\":\"d602956154fb396fd14d7737c360d7d35144b4e6ca6c3d1c51eb6dc401e42615\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\",\"bytes\":24234,\"sha256\":\"c8fe4495439826f0882b4c43952926e5de5361f88460320cc117d003352ff345\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\",\"bytes\":1633,\"sha256\":\"2d40850d19c7835d658e7154e5a1cb53ae763e31d360b41eec253397f2c5befb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\",\"bytes\":6148,\"sha256\":\"c83e427f73ff1545253d64dbb165c7e60328bb698721d1e03663e6ea7d7c403f\"}],\"current_canonical_Source4_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\",\"bytes\":2225,\"inode\":144115543165691905,\"mtime_ns\":1791727539000000000,\"ctime_ns\":1791727539000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\",\"bytes\":24234,\"inode\":144115543165691892,\"mtime_ns\":1791727495000000000,\"ctime_ns\":1791727495000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\",\"bytes\":1633,\"inode\":144115543165691947,\"mtime_ns\":1791727539000000000,\"ctime_ns\":1791727539000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\",\"bytes\":6148,\"inode\":144115543165691893,\"mtime_ns\":1791727495000000000,\"ctime_ns\":1791727495000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"request_readonly_schema\":\"root-plan-v13-library356-strict13-context-request-metadata-readonly-seal.v1\",\"new_request_directory_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17722_v13\",\"bytes\":4096,\"inode\":144115643443094568,\"mtime_ns\":1792171714000000000,\"ctime_ns\":1792172077000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"fixed_control_directories\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_context_request_from17722_v13\",\"bytes\":4096,\"inode\":144115643443094568,\"mtime_ns\":1792171714000000000,\"ctime_ns\":1792172077000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_context_request_metadata_readonly_seal\",\"bytes\":4096,\"inode\":144115643443094571,\"mtime_ns\":1792172078000000000,\"ctime_ns\":1792172078000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17722_v13\",\"bytes\":4096,\"inode\":144115643443094509,\"mtime_ns\":1792168979000000000,\"ctime_ns\":1792169684000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_from17722_metadata_readonly_seal\",\"bytes\":4096,\"inode\":144115643443094518,\"mtime_ns\":1792169685000000000,\"ctime_ns\":1792169685000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v13_ownsha_17807\",\"bytes\":4096,\"inode\":144115643979987128,\"mtime_ns\":1792170809000000000,\"ctime_ns\":1792170811000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_ownsha17807_actual_terminal_metadata_readonly_seal\",\"bytes\":4096,\"inode\":144115643443094564,\"mtime_ns\":1792171342000000000,\"ctime_ns\":1792171342000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_catalog_msa_gap_contracts17722_actual_software_terminal_metadata_readonly_seal\",\"bytes\":4096,\"inode\":144115643443094504,\"mtime_ns\":1792168494000000000,\"ctime_ns\":1792168494000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_catalog_msa_gap_contracts_software_outer_17722\",\"bytes\":4096,\"inode\":144115643979967838,\"mtime_ns\":1792167909000000000,\"ctime_ns\":1792167912000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900}],\"protected_metadata_union_count\":14537,\"Common_original_metadata_only\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_common_review.py\",\"bytes\":58825,\"inode\":144115543165691265,\"mtime_ns\":1791695459000000000,\"ctime_ns\":1791695459000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}}")
DERIVED_EXPECTED9=json.loads("{\"acceptance\":{\"bytes\":8468,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/generic_design_qualification_13306/acceptance.json\",\"sha256\":\"367f191851f0aadc08ecb7799b82a36c70d6331632bb237bfa8bf8fce88a2617\"},\"contracts\":{\"bytes\":13825,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/generic_design_qualification_13306/contracts.json\",\"sha256\":\"c7998b1b899104e4181d31c3dfc8de77256b59987fd82f0d622654e349412ade\"},\"derived_source_manifest\":{\"bytes\":20743,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/generic_design_qualification_13306/derived_source_manifest.json\",\"sha256\":\"d655f08c027da649dd87bb1f283b46459f3eef8b5013af96b610b2825a2d28b3\"},\"derived_source_files\":[{\"bytes\":2110,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/generic_design_qualification_13306/package/patch_generic_design.py\",\"sha256\":\"1c4a8ae4b8e195d8afbc12de3272aab6ccbdb74750d2f450f975173add615a71\"},{\"bytes\":12478,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/generic_design_qualification_13306/package/test_generic_design.py\",\"sha256\":\"53371f7d4dd337bedec0e2c5a4a8de7f52ff4ba05e44a8e59eb113ce329e0c4c\"},{\"bytes\":22221,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/generic_design_qualification_13306/package/qualify_generic_design_cpu.py\",\"sha256\":\"d043993aa0739849457f1f6ad4e4ea22615d55fda663cf0e4d456c4538eb01c0\"},{\"bytes\":1213,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/generic_design_qualification_13306/package/generic_design_cpu.sbatch\",\"sha256\":\"847bd5013b5a68dfa2dcb8edb99b83502506368bca4c782e6a0a66b1267a7dcc\"},{\"bytes\":12419,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/generic_design_qualification_13306/package/HANDOFF.md\",\"sha256\":\"213ad4c628c04f4e9d7dbc0db2dcbaad97218a51525bd08885a38d1881c2dcab\"}],\"derived_pipeline\":{\"bytes\":26822,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/generic_design_qualification_13306/default_candidate_source/src/ppiblocker/pipeline.py\",\"sha256\":\"e5b9c1a3ef6451595509829ad1ddb836d6f06df6b7337e061a95f3c2a60de160\"},\"default_tree_sha256\":\"765724926bf401d6e4f2d54cfb22246a163d23f7d8f1da684fe1bf769f636923\",\"all_eight_actual_suite_rows_verified\":true,\"source_dependencies\":[{\"frozen\":{\"bytes\":3027,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/generic_design_qualification_13306/scripts/register_runtime_locks.py\",\"sha256\":\"52219919173e9f8681216fe26df7b8c4e1135c6d43a17c8c8411ff1c781884e7\"},\"original\":{\"bytes\":3027,\"path\":\"/lustre/users/u21111210118/projects/test9/source/scripts/register_runtime_locks.py\",\"sha256\":\"52219919173e9f8681216fe26df7b8c4e1135c6d43a17c8c8411ff1c781884e7\"},\"relative_path\":\"scripts/register_runtime_locks.py\",\"role\":\"UNCHANGED_GENERIC_RUNTIME_REGISTRATION_TEST_IMPORT_DEPENDENCY\"}],\"failed_predecessor\":{\"incomplete\":{\"bytes\":2072,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/generic_design_qualification_13303/typed_incomplete.json\",\"sha256\":\"164175be642f71c52ac3bec0fc0b3908533dacc563f412044ca39e43e4d297b9\"},\"old_acceptance_used\":false,\"repair_identity_is_distinct\":true,\"schema\":\"generic-design-qualification-failed-v1-history.v1\",\"status\":\"ACTUAL_FAILED13303_V1_PRESERVED_NOT_QUALIFIED\",\"terminal_numeric_accounting\":{\"allocated_CPUs\":1,\"allocated_GPUs\":0,\"elapsed_seconds\":19,\"exit_code\":\"1:0\",\"job_id\":\"13303\",\"raw\":\"13303|FAILED|1:0|19|billing=1,cpu=1,node=1|u21111210118|u21111210118|test9_generic_design_guard_v1|organ\\n\",\"row\":[\"13303\",\"FAILED\",\"1:0\",\"19\",\"billing=1,cpu=1,node=1\",\"u21111210118\",\"u21111210118\",\"test9_generic_design_guard_v1\",\"organ\"],\"state\":\"FAILED\"}}}")
def need(v,msg):
 if not v:raise ValueError(msg)
md=native_metadata
META={"path","bytes","inode","mtime_ns","ctime_ns","mode","dev","nlink","uid","gid"}
need(type(SPEC)is dict and set(SPEC)==set(["conditional_CORE_metadata","qualified_original_source6","qualified_frozen_source6","qualified_source12_metadata","qualified_original_source_directory","qualified_frozen_source_directory","qualified_software_controls","qualified_software_control_metadata","qualified_source_software","source_software_terminal_metadata","source_software_terminal_receipt","plan_own_capture","plan_own_capture_metadata","new_request_path","new_request2_metadata","plan_metadata","plan_own_terminal_metadata","software_outer_proof","software_outer_proof_metadata","request_readonly_seal_metadata","plan_readonly_seal_metadata","root_control_human","primary_wrap","current_canonical_Source4","current_canonical_Source4_metadata","request_readonly_schema","new_request_directory_metadata","fixed_control_directories","protected_metadata_union_count","Common_original_metadata_only"]),"Closed30 fixed production SPEC keys required")
original_native={};worker_metadata_routes=set()
def authority(p):
 p=Path(p);need(p.is_absolute()and p.is_relative_to(R),"Exact authority path required")
 for a in[p]+list(p.parents):
  if a==R.parent:break
  need(not a.is_symlink(),"Nonlink ancestry required")
 return p
def enrol(records):
 for x in records:
  need(type(x)is dict and set(x)==META and type(x["path"])is str and all(type(x[k])is int and x[k]>=0 for k in META-{"path"}),"Exact ORIGINAL native record required")
  old=original_native.get(x["path"]);need(old is None or old==x,"Conflicting ORIGINAL native baselines");original_native[x["path"]]=dict(x)
def native_path(path):
 if path==str(CORE):
  x=md(CORE);need(stat.S_ISLNK(x["mode"])and x["bytes"]==10 and x["nlink"]==1,"Exact conditional CORE logical native type required");return CORE
 if path==str(REAL):
  x=md(REAL);need(stat.S_ISREG(x["mode"])and x["bytes"]==25916456 and x["nlink"]==1,"Exact conditional CORE resolved native type required");return REAL
 if path==common['path']:return Path(path) # fixed Common lstat-only; no authority/resolve/payload.
 if path in worker_metadata_routes:
  p=Path(path);need(p.is_absolute()and p.is_relative_to(R),"Fixed authenticated worker metadata path required");return p
 return authority(path)
def native_end():
 # TRUE LAST: lstat/ancestry only. No payload, JSON, hash, rec, resolve, readlink or refreshed baseline.
 for path,before in original_native.items():need(md(native_path(path))==before,"Root final ORIGINAL saved-native union drift")
 return True
def rec(p):
 p=authority(p);h=hashlib.sha256();n=0
 with p.open("rb")as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b);n+=len(b)
 return dict(path=str(p),bytes=n,sha256=h.hexdigest())
def ro(p,expected=None,metadata=None):
 p=authority(p);before=md(p)
 need(stat.S_ISREG(before["mode"])and stat.S_IMODE(before["mode"])==0o444 and before["nlink"]==1,"Readonly regular singlelink own file required")
 if metadata is not None:need(before==metadata,"Exact qualified ORIGINAL own metadata required")
 enrol([metadata if metadata is not None else before]) # BEFORE FIRST owned hash, never ratchet.
 value=rec(p);need(md(p)==before,"Own full native changed during read")
 if expected is not None:need(value==expected,"Exact actual CPU-qualified own tuple required")
 return value,before
def pairs(items):
 d={}
 for k,v in items:need(k not in d,"Duplicate own control JSON key");d[k]=v
 return d
def bad(s):raise ValueError("Nonfinite own control JSON "+s)
def finite_float(s):
 v=float(s);need(v==v and abs(v)!=float("inf"),"Finite own JSON exponent required");return v
def read(p):
 with Path(p).open("r",encoding="utf-8")as f:return json.load(f,object_pairs_hook=pairs,parse_constant=bad,parse_float=finite_float)
def own_plan_terminal_shape(value,owncap,ownpin):
 need(type(value)is dict and len(value)==36 and value["schema"]=="root-fixed-plan-v13-ownsha17807-terminal-metadata-readonly-seal.v1" and value["status"]=="ACTUAL_PLAN13_OWN_SHA17807_COMPLETED_CONTENT_AND_TERMINAL_READONLY_PASS_NOT_SOURCE_AUDIT" and value["actual_job_id"]=="17807" and value["Root_and_two_whole_actual_content_readback_PASS"]is True and value["actual_capture"]==ownpin and value["actual_plan"]==owncap["plan"] and value["actual_handoff"]==owncap["handoff"] and value["all_Source12_SW4_control12_Source14_canonical4_pre_end_afteroutput_PASS"]is True and value["capture56_whole_content_Root_and_two_PASS"]is True,"Actual qualified17807 ownTRO36 required")
 need(value["actual_CPU1_GPU0_allocation"]==owncap["allocation"] and value["actual_current_readiness"]==owncap["current_actual_readiness"],"Actual own17807 allocation/readiness fork")
 descriptor=value["actual_final_CPU_descriptor"]
 need(len(descriptor)==16 and descriptor["capture"]==ownpin and descriptor["plan"]==owncap["plan"] and descriptor["handoff"]==owncap["handoff"] and descriptor["true_last_original_native_union_PASS"]is True,"Actual own17807 complete CPU descriptor fork")
 query=value["fresh_terminal_query"]
 need(len(query)==8 and query["returncode"]==0 and query["timeout_observed"]is False and query["raw_stderr"]=="" and query["environment"]=={"TZ":"UTC","SLURM_TIME_FORMAT":"standard"} and query["argv"]==["sacct","-X","-n","-P","-j","17807","--format=JobIDRaw,JobName%80,State,ExitCode,ElapsedRaw,AllocCPUS,AllocTRES%1000,Start,End"] and query["raw_stdout"]=="17807|test9_source_plan_v13_ownsha_cpu|COMPLETED|0:0|17|1|billing=1,cpu=1,node=1|2026-10-16T17:13:17|2026-10-16T17:13:34\n","Actual saved17807 fresh terminal differs")
 need(all(value[k]is False for k in("Source_audit_acceptance","source_staged","published","ACTIVE_changed")),"Own Plan qualification is not Source acceptance")
 return value
def unique_original_directory(table,path):
 matches=[value for value in table if value["path"]==str(path)]
 need(len(matches)==1,"Exact original control directory missing/ambiguous")
 value=matches[0]
 need(type(value)is dict and set(value)==META and stat.S_ISDIR(value["mode"]) and stat.S_IMODE(value["mode"])==0o555 and value["nlink"]==2,"Original readonly control directory required")
 return value
need(Path(sys.executable)==CORE and sys.flags.optimize==0 and sys.flags.isolated==0 and sys.dont_write_bytecode,"Actual unoptimized CORE-B/no-I required")
common=SPEC["Common_original_metadata_only"]
need(common["path"]==str(R/"source/rebuild/benchmark_common_review.py"),"Exact fixed Common native-only path required")
enrol([common]);need(md(Path(common["path"]))==common,"Original Common native-only drift")
core=SPEC["conditional_CORE_metadata"];need(len(core)==2 and[x["path"]for x in core]==[str(CORE),str(REAL)],"Exact original Core2 order required");enrol(core)
need(md(CORE)==core[0]and md(REAL)==core[1]and os.readlink(CORE)=="python3.11","Actual conditional CORE metadata/link required")
corepin=dict(path=str(REAL),bytes=25916456,sha256="76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a")
need(rec(REAL)==corepin and md(REAL)==core[1],"Actual conditional CORE own bytes required")
sourcepins=SPEC["qualified_original_source6"]+SPEC["qualified_frozen_source6"];source_meta=SPEC["qualified_source12_metadata"]
need(len(sourcepins)==len(source_meta)==12,"Exact Source12 required");enrol(source_meta)
for pin,meta in zip(sourcepins,source_meta):ro(pin["path"],pin,meta)
source_dirs=[SPEC["qualified_original_source_directory"],SPEC["qualified_frozen_source_directory"]];enrol(source_dirs)
source_names={Path(v["path"]).name for v in SPEC["qualified_frozen_source6"]}
for x in source_dirs:need(md(authority(x["path"]))==x and stat.S_ISDIR(x["mode"])and stat.S_IMODE(x["mode"])==0o555 and x["nlink"]==2 and{p.name for p in Path(x["path"]).iterdir()}==source_names,"Exact readonly Source6 directory/universe required")
SW=SPEC["qualified_software_controls"];SWmeta=SPEC["qualified_software_control_metadata"];need(len(SW)==len(SWmeta)==4,"Exact software4 required");enrol(SWmeta)
for pin,meta in zip(SW,SWmeta):ro(pin["path"],pin,meta)
a=read(SW[0]["path"]);ct=read(SW[1]["path"])
need(SW[0]==SPEC["qualified_source_software"] and len(a)==18 and a["allocation"]["job_id"]=="17722" and a["source_files"]==SPEC["qualified_frozen_source6"]and a["original_executing_sources"]==SPEC["qualified_original_source6"],"Actual17722 software Source12 bindings required")
outerpin,outermeta=ro(SPEC["software_outer_proof"]["path"],SPEC["software_outer_proof"],SPEC["software_outer_proof_metadata"]);outer=read(outerpin["path"]);given_outer=outer;fixed=outer["fixed_control_receipts"]
need(len(outer)==51 and outer["schema"]=="root-catalog-msa-gap-contracts-source-software-operational-control.v1"and outer["actual_job_id"]=="17722"and outer["actual_unique_tests"]==356 and outer["historical321_names_classes_and_relative_order_preserved"]is True and len(outer["actual_new_named_tests"])==35 and len(fixed)==len(outer["fixed_control_metadata"])==457 and outer["status"]=="ROOT_ACTUAL_NEW_SOURCE_SOFTWARE_AND_OWN_CONTROLS_READBACK_PASS_NOT_SOURCE_AUDIT_OR_SCIENCE"and outer["source_files"]==SPEC["qualified_frozen_source6"]and outer["original_executing_sources"]==SPEC["qualified_original_source6"]and outer["allocation"]==a["allocation"]and all(outer[k]is False for k in ["Source_audit_acceptance","source_staged","published","ACTIVE_changed"]),"Exact actual17722 CO51/457/software356 required")
need([outer[k]for k in ["actual_software_acceptance","actual_contracts","actual_contract_log","actual_source_snapshot"]]==SW,"Exact CO SW4 pointers required")
terminalpin,terminalmeta=ro(SPEC["source_software_terminal_metadata"]["path"],expected=SPEC["source_software_terminal_receipt"],metadata=SPEC["source_software_terminal_metadata"]);terminal=read(terminalpin["path"])
need(len(terminal)==41 and terminal["schema"]=="root-catalog-msa-gap-contracts-software17722-terminal-metadata-readonly-seal.v1"and terminal["status"]=="ACTUAL_SOFTWARE17722_COMPLETED_CONTENT_AND_METADATA_READBACK_PASS_NOT_SOURCE_OR_SCIENCE"and terminal["actual_job_id"]=="17722"and terminal["Root_and_two_whole_actual_content_readback_PASS"]is True and terminal["actual_unique_named_tests"]==356 and terminal["failures"]==terminal["errors"]==terminal["skips"]==0 and terminal["compiler_and_bash_PASS"]is True and terminal["Source12_whole_bytes_and_native_prepost_PASS"]is True and terminal["actual_Root_execution_control"]==outerpin,"Actual qualified software356 TRO41 required")
need([terminal[k]for k in ["actual_software_acceptance","actual_contracts","actual_contract_log","actual_source_snapshot"]]==SW,"Exact terminal SW4 pointers required")
td=terminal["actual_final_Root_CPU_descriptor"]
need(len(td)==10 and td["software_acceptance"]==SW[0]and td["contracts"]==SW[1]and td["contract_log"]==SW[2]and td["source_snapshot"]==SW[3]and td["actual_frozen_sources"]==SPEC["qualified_frozen_source6"]and td["original_source_files"]==SPEC["qualified_original_source6"]and td["root_execution_control"]==outerpin,"Exact final17722 CPU descriptor required")
tq=terminal["fresh_terminal_query"];need(len(tq)==8 and tq["returncode"]==0 and tq["raw_stderr"]==""and tq["timeout_observed"]is False and tq["environment"]=={"TZ":"UTC","SLURM_TIME_FORMAT":"standard"}and tq["argv"]==["sacct","-X","-n","-P","-j","17722","--format=JobIDRaw,JobName%80,State,ExitCode,ElapsedRaw,AllocCPUS,AllocTRES%1000,Start,End"],"Actual saved fresh terminal query required")
tr=[line.split("|")for line in tq["raw_stdout"].splitlines()]
need(len(tr)==1 and tr[0]==["17722","test9_final_source_catalog_msa_gap_contracts_v3","COMPLETED","0:0","167","1","billing=1,cpu=1,node=1","2026-10-16T16:22:30","2026-10-16T16:25:17"],"Exact actual17722 nine-column terminal row required");tres(tr[0][6])
ta=a["allocation"];tre=outer["current_actual_readiness"]
need(ta==outer["allocation"]and ta["job_id"]=="17722"and ta["allocated_CPUs"]==1 and ta["allocated_gpus"]==0 and tre["actual_job_id"]=="17722"and tre["requested_GPUs"]==0,"Saved actual17722 owner CPU1/GPU0 allocation required")
tri=tre["selected_actual_attempt"];need(type(tri)is int and 1<=tri<=len(tre["attempts"]),"Saved actual selected readiness required")
trar=tre["attempts"][tri-1];need(trar["accepted_current_readiness"]is True and trar["actual_row"]==ta["numeric_sacct_row"]and trar["actual_row"][:2]==["17722","RUNNING"]and trar["actual_row"][3:]==["u21111210118","u21111210118","organ"],"Saved actual six-column owner/account/organ required");tres(trar["actual_row"][2])

pre_cap_pin,pre_cap_md=ro(SPEC["plan_own_capture"]["path"],SPEC["plan_own_capture"],SPEC["plan_own_capture_metadata"]);pre_cap=read(pre_cap_pin["path"])
need(len(pre_cap)==56 and pre_cap["schema"]=="root-fixed-source-plan-v13-own-sha-control-capture.v1" and pre_cap["status"]=="ACTUAL_NEW_PLAN_V13_OWN_SHA_AND14_PINNED_SOURCE_DOC_ADDITIONS_CPU_VERIFIED_NOT_SOURCE_AUDIT_ACCEPTANCE" and pre_cap["actual_job_id"]=="17807" and pre_cap["software_acceptance"]==SW[0] and pre_cap["source_files"]==SPEC["qualified_frozen_source6"] and pre_cap["original_executing_sources"]==SPEC["qualified_original_source6"],"Actual qualified17807 CAP56 required")
need(SPEC["source_software_terminal_receipt"]==pre_cap["qualified_software17722_terminal_own_CPU_receipt"],"Actual software17722 terminal CPU pin differs")
need(pre_cap["qualified_source12_metadata"]==source_meta==outer["original_source_metadata"]+outer["frozen_source_metadata"] and pre_cap["software_control_receipts"]==SW and pre_cap["software_control_metadata_before"]==pre_cap["software_control_metadata_after"]==SWmeta and pre_cap["conditional_core_runtime"]==a["conditional_core_runtime"],"Qualified software/CAP original Source12/SW4/Core metadata fork")
added_source_rows=pre_cap["additional_14_Source_rows"];added_source_metadata=pre_cap["additional_14_Source_metadata"]
need(len(added_source_rows)==len(added_source_metadata)==14 and pre_cap["additional_18_safe_seed_receipts"]==[row["receipt"]for row in added_source_rows]+SW,"Actual ordered14Source/18safeSeed bindings required");enrol(added_source_metadata)
for row,meta in zip(added_source_rows,added_source_metadata):ro(row["receipt"]["path"],row["receipt"],meta)
pre_q,pre_qmd=ro(SPEC["new_request_path"],metadata=SPEC["new_request2_metadata"][0])
pre_m,pre_mmd=ro(Path(SPEC["new_request_path"]).with_name("request_metadata.json"),metadata=SPEC["new_request2_metadata"][1])
pre_plan,pre_planmd=ro(pre_cap["plan"]["path"],pre_cap["plan"],SPEC["plan_metadata"][0]);pre_h,pre_hmd=ro(pre_cap["handoff"]["path"],pre_cap["handoff"],SPEC["plan_metadata"][1])
pre_t,pre_tmd=ro(SPEC["plan_own_terminal_metadata"]["path"],metadata=SPEC["plan_own_terminal_metadata"])
pre_outer,pre_outermd=ro(SPEC["software_outer_proof"]["path"],SPEC["software_outer_proof"],SPEC["software_outer_proof_metadata"])
pre_qro,pre_qromd=ro(SPEC["request_readonly_seal_metadata"]["path"],metadata=SPEC["request_readonly_seal_metadata"])
pre_pro,pre_promd=ro(SPEC["plan_readonly_seal_metadata"]["path"],metadata=SPEC["plan_readonly_seal_metadata"])
pre_human,pre_humanmd=ro(SPEC["root_control_human"]);pre_wrap,pre_wrapmd=ro(SPEC["primary_wrap"])
preimport_controls=[(pre_q,pre_qmd),(pre_m,pre_mmd),(pre_plan,pre_planmd),(pre_h,pre_hmd),(pre_cap_pin,pre_cap_md),(pre_t,pre_tmd),(terminalpin,terminalmeta),(pre_outer,pre_outermd),(pre_qro,pre_qromd),(pre_pro,pre_promd),(pre_human,pre_humanmd),(pre_wrap,pre_wrapmd)]
need(len(preimport_controls)==len({r["path"]for r,x in preimport_controls})==12,"Twelve exact controls before first project import required")
canonical=SPEC["current_canonical_Source4"];canonicalmeta=SPEC["current_canonical_Source4_metadata"];need(len(canonical)==len(canonicalmeta)==4 and pre_cap["current_canonical_Source4_receipts"]==canonical and pre_cap["current_canonical_Source4_metadata_after"]==canonicalmeta,"Exact current canonical4 required");enrol(canonicalmeta)
def canonical_end():
 for pin,meta in zip(canonical,canonicalmeta):
  p=authority(pin["path"]);need(md(p)==meta and stat.S_ISREG(meta["mode"])and stat.S_IMODE(meta["mode"])==0o664 and meta["nlink"]==1,"Only four fixed canonical mutable Source leaves permitted")
  need(rec(p)==pin and md(p)==meta,"Canonical4 exact ownbytes/native drift")
canonical_end()
outer=read(pre_outer["path"])
need(given_outer==outer,"Software CO changed between preimport own reads")
pre_own_terminal=own_plan_terminal_shape(read(pre_t["path"]),pre_cap,pre_cap_pin)
need(len(pre_cap["control_receipts"])==len(pre_cap["control_metadata_before"])==len(pre_cap["control_metadata_after"])==12 and pre_cap["control_metadata_before"]==pre_cap["control_metadata_after"],"OwnCAP control12 original table fork")
coupled_source_controls=[]
for position in(5,6):
 pin=pre_cap["control_receipts"][position];meta=pre_cap["control_metadata_after"][position]
 coupled_source_controls.append(ro(pin["path"],pin,meta))
sourceRO=read(coupled_source_controls[0][0]["path"]);softwareHRO=read(coupled_source_controls[1][0]["path"])
need(len(sourceRO)==33 and sourceRO["schema"]=="root-catalog-msa-gap-contracts1-source-metadata-readonly-seal.v1" and sourceRO["Root_and_two_whole_final_static_SOURCE_PASS"]is True and sourceRO["source_tests_defined"]==356 and sourceRO["source_files_after"]==source_meta[:6] and sourceRO["source_directory_after"]==source_dirs[0] and coupled_source_controls[0][0]==outer["source_readonly_seal"],"Actual SRO33 Source6 fork")
need(len(softwareHRO)==31 and softwareHRO["schema"]=="root-catalog-msa-gap-contracts-software-human-metadata-readonly-seal.v1" and softwareHRO["Root_and_two_whole_Human_STATIC_PASS"]is True and softwareHRO["human_metadata_after"]==outer["fixed_control_metadata"][455] and softwareHRO["qualified_source_files"]==source_meta[:6] and softwareHRO["qualified_source_directory"]==source_dirs[0],"Actual softwareHRO31 Source6/Human fork")
need(pre_cap["Root_Common_metadata_only_no_payload_IO"]is True and outer["Root_Common_metadata_only_no_payload_IO"]is True,"Common payload hash permission absent")
for value in(pre_cap,pre_own_terminal,outer,terminal,sourceRO,softwareHRO):
 need(value["Common_original_metadata_only_before"]==value["Common_original_metadata_only_after"]==common,"Coupled original Common native-only metadata fork")
historical3=outer["fixed_historical_IMPLEMENTATION_Source2_own_CPU_receipts"]+outer["supplementary_historical_launcher_SOURCE_own_CPU_receipts"]
historical3meta=outer["fixed_historical_Source2_metadata_before"]+outer["supplementary_historical_launcher_SOURCE_metadata_before"]
need(len(historical3)==len(historical3meta)==3 and outer["fixed_historical_Source2_metadata_before"]==outer["fixed_historical_Source2_metadata_after"] and outer["supplementary_historical_launcher_SOURCE_metadata_before"]==outer["supplementary_historical_launcher_SOURCE_metadata_after"] and outer["historical_Source2_and_launcher_never_imported_compiled_or_executed"]is True,"Fixed historical Source2 and launcher ownbytes only required")
for pin,meta in zip(historical3,historical3meta):ro(pin["path"],pin,meta)
TMP=authority(S/"tmp")/("source_plan_v13_production_"+jid)
need(os.environ.get("TMPDIR")==str(TMP)and not TMP.exists()and not TMP.is_symlink(),"Exact exclusive owned TMPDIR required; wrapper exports but does not precreate it")
TMP.mkdir(mode=0o775)
# Current literal Source12/SW4/Core and ALL12 controls are authenticated BEFORE this project import.
entry=Path(SPEC["qualified_frozen_source6"][0]["path"]);ss=importlib.util.spec_from_file_location("root_qualified_source17722_production_control",entry);g=importlib.util.module_from_spec(ss);ss.loader.exec_module(g)
need(g.software_shape(a,ct)==SPEC["qualified_frozen_source6"],"Qualified software356 pure shape required")
allocation=g.cpu();runtime=g.conditional_core_runtime()
need(allocation["job_id"]==jid and allocation["allocated_CPUs"]==1 and allocation["allocated_gpus"]==0 and allocation["numeric_sacct_row"]==attempts[selected-1]["actual_row"]and runtime==a["conditional_core_runtime"],"Fresh current owned CPU1/GPU0/Core required")
snapshot=read(SW[3]["path"]);need(g.software_snapshot_shape(a,snapshot)==snapshot,"Qualified software snapshot pure shape required")
QP=Path(SPEC["new_request_path"]);MP=QP.with_name("request_metadata.json");QRO=Path(SPEC["request_readonly_seal_metadata"]["path"])
qropin,qrometa=ro(QRO,metadata=SPEC["request_readonly_seal_metadata"]);qr=read(QRO)
need(qr["schema"]==SPEC["request_readonly_schema"]and qr["Root_and_two_independent_whole_request_and_metadata_static_PASS"]is True and qr["after_files"]==SPEC["new_request2_metadata"]and qr["after_directory"]==SPEC["new_request_directory_metadata"],"Actual independently accepted new strict13 QRO required")
qpin,qmeta=ro(QP,metadata=SPEC["new_request2_metadata"][0]);mpin,mmeta=ro(MP,metadata=SPEC["new_request2_metadata"][1]);q=read(QP);m=read(MP)
cap_pin,cap_meta=ro(SPEC["plan_own_capture"]["path"],SPEC["plan_own_capture"],SPEC["plan_own_capture_metadata"]);cap=read(cap_pin["path"])
t7pin,t7meta=ro(SPEC["plan_own_terminal_metadata"]["path"],metadata=SPEC["plan_own_terminal_metadata"]);t7=read(t7pin["path"])
own_plan_terminal_shape(t7,cap,cap_pin)
need(t7==pre_own_terminal,"OwnTRO36 changed after first project import")
planpin,planmeta=ro(cap["plan"]["path"],cap["plan"],SPEC["plan_metadata"][0]);hpin,hmeta=ro(cap["handoff"]["path"],cap["handoff"],SPEC["plan_metadata"][1]);plan=read(planpin["path"])
keys=["schema","root_owned","raw_JSON_rewrite_allowed","generic_relative_resolution_allowed","generic_external_resolution_allowed","library_software_acceptance","mapper_software_acceptance","final_source_plan","bbf_parent_aliases","historical_parent_aliases","recovered_parent_aliases","archive_parent_aliases","finite_source_parent_aliases"]
need(len(q)==13 and list(q)==keys==m["exact13_key_order"]and q["schema"]=="final-source-materialized-context-read-view-request.v3"and q["root_owned"]is True,"Exact ordered strict13 request required")
need(q["final_source_plan"]==planpin and q["library_software_acceptance"]==SW[0]==plan["library_software_acceptance"]and q["mapper_software_acceptance"]==plan["mapper_software_acceptance"],"Q/Plan/current17722 software bindings required")
for k in("raw_JSON_rewrite_allowed","generic_relative_resolution_allowed","generic_external_resolution_allowed"):need(q[k]is False,"No generic permission granted")
for k in("bbf_parent_aliases","historical_parent_aliases","recovered_parent_aliases","archive_parent_aliases"):need(type(q[k])is list and q[k]==[],"No generic parent alias added")
need(len(plan)==34 and len(plan["modules"])==9 and len(plan["context_parent_seeds"])==17 and len(plan["aliases"])==7 and len(q["finite_source_parent_aliases"])==8,"Exact top34/nine primary/17/seven/finite8 required")
need(cap==pre_cap and[cap[k]for k in["Source_n","destination_n","seed_n","unique_seed_n","role_n","parent_n","ordered_alias_n"]]==[776,715,3973,3900,9,17,7]and cap["source_audit_executed"]is False and cap["all34keys_type_order_and_original_V12_serialized_bytes_rewind_PASS"]is True and cap["true_last_original_native_union_required_for_final_descriptor"]is True,"Actual qualified Plan13 exact scope required")
need(g.module_plan(plan)==plan["modules"]and plan["modules"][7]["sources"][-14:]==added_source_rows and plan["modules"][7]["seeds"][-18:]==cap["additional_18_safe_seed_receipts"],"Exact finaltools14Source/18safeSeed tails required")
priorpin=cap["prior_qualified_PlanV12_and_Handoff"][0]
need(cap["control_receipts"][10]==priorpin,"Exact ownCAP priorPlan12 control role required")
priorplanro=ro(priorpin["path"],priorpin,cap["control_metadata_after"][10]);priorplan=read(priorpin["path"])
need(plan["modules"][8]==priorplan["modules"][8]and len(plan["modules"][8]["sources"])==109 and len(plan["modules"][8]["seeds"])==44 and plan["context_parent_seeds"]==priorplan["context_parent_seeds"]and plan["aliases"]==priorplan["aliases"],"Default WHOLE109/44, ordered17 and seven aliases unchanged")
rewound=json.loads(json.dumps(plan,allow_nan=False));rewound["library_software_acceptance"]=priorplan["library_software_acceptance"];del rewound["modules"][7]["sources"][-14:];del rewound["modules"][7]["seeds"][-18:]
def typed_same(left,right):
 need(type(left)is type(right),"Preserved Plan type drift")
 if type(left)is dict:
  need(list(left)==list(right),"Preserved Plan key order drift")
  for key in left:typed_same(left[key],right[key])
 elif type(left)is list:
  need(len(left)==len(right),"Preserved Plan list drift")
  for aa,bb in zip(left,right):typed_same(aa,bb)
 else:need(left==right,"Preserved Plan scalar drift")
typed_same(rewound,priorplan);priorraw=Path(priorpin["path"]).read_bytes()
need(len(priorraw)==2051027 and(json.dumps(rewound,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode()==priorraw,"Whole actual Plan12 serialized rewind required")
need(cap["plan"]["bytes"]==2063544 and cap["handoff"]["bytes"]==21636,"Exact reviewed Plan13/H sizes required")
need(len(m)==49 and m["schema"]=="root-plan-v13-strict-finite-parent-view-request-text-preparation-metadata.v1"and m["root_and_two_independent_actual17807_content_readback_PASS"]is True and m["root_and_independent_actual17807_terminal_RO_readback_PASS"]is True and m["accepted_Plan"]==planpin and m["accepted_Plan_HANDOFF"]==hpin and m["actual17807_Plan_own_capture"]==cap_pin,"Actual newM49 qualified17807 facts required")
# Draft mode fields in M describe its immutable preparation event; current RO authority is QRO, not rewritten M.
need(m["ordered_Plan17_indices"]==[7,8,9,10,12,13,14,16]and m["ordered_BaseI_files_indices"]==[238,249,265,263,250,283,228,239],"Exact finite8 index order required")
finite_rows=m["finite_parent_alias_scope_rows"];need(len(finite_rows)==8 and q["finite_source_parent_aliases"]==[dict(logical=x["logical"],physical=x["physical"])for x in finite_rows],"Exact finite8 Source3/Proof5 full tuple pairs required")
for index,row in enumerate(finite_rows):
 need(row["logical"]==plan["context_parent_seeds"][m["ordered_Plan17_indices"][index]]and row["reader_group"]==("FINITE_SOURCE_PARENT"if index<3 else"FINITE_PROOF_PARENT"),"Finite existing parent group/identity fork")
 for field in("logical_current_metadata","physical_current_metadata"):
  native={k:row[field][k]for k in META};enrol([native]);need(md(authority(native["path"]))==native and stat.S_ISREG(native["mode"])and stat.S_IMODE(native["mode"])==0o444 and native["nlink"]==1,"Finite original16 parent metadata drift")
outerpin,outermeta=ro(SPEC["software_outer_proof"]["path"],SPEC["software_outer_proof"],SPEC["software_outer_proof_metadata"]);planropin,planrometa=ro(SPEC["plan_readonly_seal_metadata"]["path"],metadata=SPEC["plan_readonly_seal_metadata"])
ownhuman,ownhumanmeta=ro(SPEC["root_control_human"]);ownwrap,ownwrapmeta=ro(SPEC["primary_wrap"]);fence=chr(96)*3
humantext=Path(ownhuman["path"]).read_text("utf-8");wraptext=Path(ownwrap["path"]).read_text("utf-8")
need(humantext.count(fence+"python\n")==1 and wraptext.endswith("\nPY\n")and wraptext.partition("<<'PY'\n")[2][:-4].rstrip("\n")==humantext.split(fence+"python\n",1)[1].split("\n"+fence,1)[0].rstrip("\n"),"Actual primary shell equals whole reviewed Human fence")
controls=[(qpin,qmeta),(mpin,mmeta),(planpin,planmeta),(hpin,hmeta),(cap_pin,cap_meta),(t7pin,t7meta),(terminalpin,terminalmeta),(outerpin,outermeta),(qropin,qrometa),(planropin,planrometa),(ownhuman,ownhumanmeta),(ownwrap,ownwrapmeta)]
need(controls==preimport_controls,"All12 own control tuples/native equal preimport originals")
protected={}
for x in qr["protected_inputs_after"]+qr["protected_directories_after"]+qr["after_files"]+[qr["after_directory"],SPEC["request_readonly_seal_metadata"]]:
 need(x["path"]not in protected or protected[x["path"]]==x,"Protected original overlap conflict");protected[x["path"]]=x
required_dir_paths={str(QP.parent),str(QRO.parent),str(Path(planpin["path"]).parent),str(Path(planropin["path"]).parent),str(Path(cap_pin["path"]).parent),str(Path(t7pin["path"]).parent),str(Path(terminalpin["path"]).parent),str(Path(outerpin["path"]).parent)}
fixed_dirs=SPEC["fixed_control_directories"]
need(len(fixed_dirs)==len(required_dir_paths)==8 and{x["path"]for x in fixed_dirs}==required_dir_paths,"Closed exact eight accepted control directory originals required")
software_hro_directory=unique_original_directory(t7["protected_inputs_after"],Path(coupled_source_controls[1][0]["path"]).parent)
source_proof_dirs=[outer["source_readonly_seal_directory_metadata"],software_hro_directory];enrol(source_proof_dirs)
planRO=read(planropin["path"])
need(len(planRO)==33 and planRO["schema"]=="root-final-source-plan-v13-from17722-metadata-readonly-seal.v1" and planRO["Root_and_two_whole_Plan_STATIC_PASS"]is True and[planRO["plan_metadata_after"],planRO["handoff_metadata_after"]]==SPEC["plan_metadata"] and planRO["qualified_software_acceptance"]==SW[0] and planRO["qualified_software_terminal_metadata"]==terminalmeta and planRO["Common_original_metadata_only_before"]==planRO["Common_original_metadata_only_after"]==common,"Actual PlanRO33 original binding required")
enrol(fixed_dirs)
for x in fixed_dirs+source_proof_dirs:
 need(md(authority(x["path"]))==x and stat.S_ISDIR(x["mode"])and stat.S_IMODE(x["mode"])==0o555,"Original accepted control directory drift")
 if x["path"]==str(QRO.parent):protected[x["path"]]=x
need(len(protected)==SPEC["protected_metadata_union_count"]and qr["protected_inputs_before"]==qr["protected_inputs_after"]and qr["protected_directories_before"]==qr["protected_directories_after"],"Exact accepted newQRO protected original finite union required")
enrol(list(protected.values()));enrol(readiness_native_original+[readiness_directory_original])
need(md(authority(D))==readiness_directory_original and{p.name for p in D.iterdir()}==readiness_names_original,"Creation-time readiness original directory/universe required")
readiness=read(D/"readiness.json");readyvalues=[ro(x["path"],metadata=x)for x in readiness_native_original]
def inputs_end():
 need(md(CORE)==core[0]and md(REAL)==core[1]and rec(REAL)==corepin and md(REAL)==core[1]and os.readlink(CORE)=="python3.11","Conditional CORE ownbytes/original-native drift")
 for pin,meta in zip(sourcepins,source_meta):ro(pin["path"],pin,meta)
 for x in source_dirs:need(md(authority(x["path"]))==x and{p.name for p in Path(x["path"]).iterdir()}==source_names,"Source6 original directory/universe drift")
 for pin,meta in zip(SW,SWmeta):ro(pin["path"],pin,meta)
 for pin,meta in controls+readyvalues+[priorplanro]+coupled_source_controls:ro(pin["path"],pin,meta)
 for row,meta in zip(added_source_rows,added_source_metadata):ro(row["receipt"]["path"],row["receipt"],meta)
 for pin,meta in zip(historical3,historical3meta):ro(pin["path"],pin,meta)
 need([g.rec(pin["path"])for pin,meta in controls]==[pin for pin,meta in controls]and[md(authority(pin["path"]))for pin,meta in controls]==[meta for pin,meta in controls],"Qualified G17722.rec all12 ORIGINAL native drift")
 for x in protected.values():need(md(native_path(x["path"]))==x,"Protected ORIGINAL native drift")
 for x in fixed_dirs+source_proof_dirs:need(md(authority(x["path"]))==x,"Original fixed directory drift")
 need(md(authority(D))==readiness_directory_original and{p.name for p in D.iterdir()}==readiness_names_original,"Original readiness namespace drift")
 need(md(Path(common["path"]))==common,"Original Common lstat-only drift")
 canonical_end();need(g.conditional_core_runtime()==runtime,"Qualified current conditional CORE runtime drift")
inputs_end();native_end()
OUT=authority(S/"runs")/("final_source_plan_v13_production_"+jid);AUX=OUT.with_name(OUT.name+"_context_adapter");PROOF=authority(S/"submissions")/("source_plan_v13_production_"+jid+"_root_execution_control")
need(all(not p.exists()and not p.is_symlink()for p in(OUT,AUX,PROOF)),"Exclusive absent OUT/AUX/Rootproof namespaces required")
adapter=Path(SPEC["qualified_frozen_source6"][-1]["path"]);need(adapter.name=="final_source_context_adapter.py","Exact qualified17722 frozen adapter required")
actual_argv=[str(adapter),"--request",str(QP),"--out",str(OUT)];savedargv=list(sys.argv);phase="actual_frozen_G17722_adapter_mandatory356_producer"
try:
 sys.argv=actual_argv
 try:runpy.run_path(str(adapter),run_name="__main__")
 finally:sys.argv=savedargv
 need(sys.argv==savedargv,"Root realargv lifecycle not restored")
 phase="actual_A_CA_I_C_six_finite_proofs_and_ordinary_Source2"
 paths=[OUT/"acceptance.json",OUT/"context_adapter_acceptance.json",OUT/"source_inclusion_final.json",OUT/"source_receipt_closure_final.json"]
 output_controls=[ro(p)for p in paths];A,CA,I,C=[read(p)for p in paths]
 need(A["schema"]=="final-source-closure-acceptance.v3"and A["status"]=="FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED"and A["source_issues"]==0 and A["explicit_plan"]==planpin,"Actual new source A required")
 need(CA["schema"]=="final-source-materialized-context-read-view-acceptance.v3"and CA["status"]=="FINAL_CURRENT_SOURCE_MATERIALIZED_FIVE_PARENT_CONTEXT_AND_DERIVED_V2_CPU_ACCEPTED_NOT_STAGED_NOT_PUBLISHED"and CA["request"]==qpin and CA["library_software_acceptance"]==SW[0]and CA["actual_new_library_acceptance"]==output_controls[0][0],"Actual CA/current source A bindings required")
 need(I["schema"]=="benchmark-source-inclusion.v3"and I["status"]=="SOURCE_INCLUSION_AUDIT_PASS"and I["applied"]is False and I["issues"]==[]and I["source_receipt_closure"]==output_controls[3][0]and I["explicit_plan"]==planpin,"Actual nonstaging inclusion issues0 required")
 need(C["schema"]=="final-source-receipt-closure.v2"and C["status"]=="EXACT_NEW_SOURCE_DEPENDENCIES_WITH_INHERITED_TYPED_HISTORY","Actual closure required")
 need(all(x["allocation"]==allocation for x in(A,CA,I))and A["source_inclusion"]==CA["source_inclusion"]==output_controls[2][0]and A["source_closure"]==CA["source_closure"]==output_controls[3][0],"Actual allocation/A-CA-I-C pointer bindings required")
 catalog_native=g.catalog_msa_gap_projection_native(C)
 need(type(catalog_native)is list and len(catalog_native)==3,"Current bound catalog actual annotation observations required")
 enrol(catalog_native) # ORIGINAL producer records before Root g.rec/read of any catalog input.
 catalog_objects=g.catalog_msa_gap_saved_inputs(C)
 need(type(catalog_objects)is list and len(catalog_objects)==3 and g.catalog_msa_gap_projection_shape(catalog_objects[0],catalog_objects[1],catalog_objects[2],C)is True,"Actual catalog/A/BaseC pure projection required")
 catalog_control_records=[]
 for pin,meta in zip(g._catalog_msa_controls(),catalog_native):catalog_control_records.append(ro(pin["path"],pin,meta))
 for rows,parent in[(I["runner_source_snapshot"],OUT/"runner"),(A["original_executing_sources"],AUX/"runner"),(CA["source_files"],AUX/"runner"),(CA["original_executing_sources"],adapter.parent)]:
  need(len(rows)==6 and{Path(r["path"]).name for r in rows}==source_names and{Path(r["path"]).parent for r in rows}=={parent},"Actual runtime Source6 location/universe required")
  for pin in rows:
   expected=next(x for x in SPEC["qualified_frozen_source6"]if Path(x["path"]).name==Path(pin["path"]).name)
   need(g.fp(pin)==g.fp(expected),"Actual runtime Source differs from qualified17722 bytes");output_controls.append(ro(pin["path"],pin))
 contractpin=A["contracts"];output_controls.append(ro(contractpin["path"],contractpin));contracts=read(contractpin["path"])
 need(contracts["status"]=="PASS"and type(contracts["tests"])is int and contracts["tests"]==356 and type(contracts["failures"])is int and type(contracts["errors"])is int and contracts["failures"]==contracts["errors"]==0 and contracts["owned_python_compile_PASS"]is True and contracts["bash_syntax_PASS"]is True and contracts["tested_source_files"]==I["runner_source_snapshot"],"Actual mandatory356/compiler/bash/runtimeSource6 required")
 output_controls.append(ro(contracts["log"]["path"],contracts["log"]));log=Path(contracts["log"]["path"]).read_text()
 need(re.findall(r"(?:^|\n)Ran ([0-9]+) tests?\b",log)==["356"]and re.search(r"(?:^|\n)OK(?:\n|$)",log)and not re.search(r"(?:FAIL|ERROR|skipped=|\[SKIP\])",log),"Complete356 contract log required")
 named356=re.findall(r"(?m)^(test[^\n]+) \.\.\. ok$",log);case_lines=[x for x in log.splitlines()if x.startswith("test")]
 qualified_named356=re.findall(r"(?m)^(test[^\n]+) \.\.\. ok$",Path(SW[2]["path"]).read_text())
 need(len(case_lines)==len(named356)==len(set(named356))==356 and all(x.endswith(" ... ok")for x in case_lines)and named356==qualified_named356 and len(set(qualified_named356))==356,"Exact full356 names/classes/order equal actual17722 qualification required")
 output_dirs=[]
 for directory in(OUT/"runner",AUX/"runner"):
  before=md(authority(directory));need(stat.S_ISDIR(before["mode"])and stat.S_IMODE(before["mode"])==0o555 and before["nlink"]==2 and{p.name for p in directory.iterdir()}==source_names,"Actual new readonly runner6 directory/universe required");enrol([before]);output_dirs.append(before)
 for directory in(OUT,AUX,AUX/"mapper",TMP):
  before=md(authority(directory));need(stat.S_ISDIR(before["mode"]),"Owned output directory required")
  if directory==AUX/"mapper":need(stat.S_IMODE(before["mode"])==0o555 and before["nlink"]==2,"Actual Mapper14 copy directory must be readonly0555")
  if directory==TMP:need(not list(directory.iterdir()),"All genuine contract TMP outputs must be cleaned")
  enrol([before]);output_dirs.append(before)
 proof_families=[("vendor_example_opaque_leaf_proof","vendor_example_opaque_aliases",g.verify_vendor_example_preservation),("finite_worker_control_proof","finite_worker_control_aliases",g.verify_finite_worker_preservation),("inventory_history_opaque_leaf_proof","inventory_history_opaque_aliases",g.verify_inventory_history_preservation),("archive_parent_history_opaque_leaf_proof","archive_parent_history_opaque_aliases",g.verify_archive_parent_history_preservation),("relative_diagnostic_history_opaque_leaf_proof","relative_diagnostic_history_opaque_aliases",g.verify_relative_diagnostic_history_preservation),("parent_diagnostic_history_opaque_leaf_proof","parent_diagnostic_history_opaque_aliases",g.verify_parent_diagnostic_history_preservation)]
 proof_objects=[]
 for number,(pkey,ikey,verify_family)in enumerate(proof_families):
  pp=A[pkey];ip=A[ikey];need(all(x[pkey]==pp and x[ikey]==ip for x in(CA,I,C))and pp["path"]==str(OUT/(pkey+".json"))and ip["path"]==str(OUT/(ikey+".json")),"All A-CA-I-C six-family exact owned paths/pointers must match")
  output_controls.extend([ro(pp["path"],pp),ro(ip["path"],ip)]);proof,index=read(pp["path"]),read(ip["path"])
  need(proof["exact_alias_index"]==ip,"Exact proof/index pointer binding required")
  if number>=2:
   enrol(g._fixed_history_saved_native_records(proof))
  elif number==0:
   enrol([proof["parent_metadata_before"],proof["original_metadata_before"],proof["preserved_metadata"]])
   copy=proof["archived_opaque_data"];copydir=md(authority(Path(copy["path"]).parent));need(stat.S_ISDIR(copydir["mode"])and stat.S_IMODE(copydir["mode"])==0o555 and copydir["nlink"]==2,"Exact vendor preservation directory required");enrol([copydir])
   need(Path(copy["path"]).parent==OUT/"opaque_vendor_example_bytes"and{p.name for p in Path(copydir["path"]).iterdir()}=={Path(copy["path"]).name},"Exact vendor one-copy owned namespace required")
  else:
   authority_saved=proof["authority_metadata_before"];enrol([authority_saved["base"],authority_saved["closure"]]+authority_saved["parents"])
   fixed={x["index"]:x for x in g._WORKER_TABLE};need(len(fixed)==23 and len(proof["source_metadata_before"])==23,"Exact worker23 metadata table required")
   pending_routes=set()
   for item in proof["source_metadata_before"]:
    row=fixed[item["index"]];records=item["metadata"]
    need(records["logical"]["path"]==row["logical"]["path"]and records["canonical"]["path"]==row["canonical"]["path"]and records["link"]["path"]==row["link_path"]and records["link_text"]==row["link_text"],"Worker ORIGINAL native paths must be the same exact qualified table")
    enrol([records["logical"],records["canonical"],records["link"]]);pending_routes.update([row["logical"]["path"],row["link_path"]])
   need(pending_routes=={x["logical"]["path"]for x in g._WORKER_TABLE}|{x["link_path"]for x in g._WORKER_TABLE},"Closed23 logical/ancestor worker metadata route set required")
   need(proof["output_root_as_scalar"]==str(OUT),"Actual worker proof must bind this new audit output")
   enrol([proof["copy_directory_metadata"]]+[target["preserved_metadata"]for target in proof["canonical_targets"]])
  verify_family(proof,index,allocation)
  if number==1:
   worker_metadata_routes.update(pending_routes) # ONLY after current full qualified worker verification.
   for target in proof["canonical_targets"]:output_controls.append(ro(target["preserved"]["path"],target["preserved"],target["preserved_metadata"]))
  else:
   copy=proof["archived_opaque_data"]if number==0 else proof["preserved_opaque_data"]
   output_controls.append(ro(copy["path"],copy,proof["preserved_metadata"]))
  proof_objects.append((proof,index,verify_family))
 for position,shape in[(2,g.inventory_history_proof_shape),(3,g.archive_parent_history_proof_shape),(4,g.relative_diagnostic_history_proof_shape),(5,g.parent_diagnostic_history_proof_shape)]:shape(proof_objects[position][0],proof_objects[position][1],allocation)
 g.parent_diagnostic_history_source_coverage(proof_objects[5][0],C,I)
 need(all(x.get("source_staged")is False and x.get("ACTIVE_changed")is False for x in(A,CA,I)),"No Source stage/promotion permitted")
 mapper_pins=CA["mapper_source_files"];need(len(mapper_pins)==14 and{Path(x["path"]).name for x in mapper_pins}=={p.name for p in(AUX/"mapper").iterdir()},"Exact actual Mapper14 directory/universe required")
 for pin in mapper_pins:
  copied=AUX/"mapper"/Path(pin["path"]).name;output_controls.append(ro(pin["path"],pin));value,before=ro(copied);need(g.fp(value)==g.fp(pin),"Actual Mapper14 copy differs");output_controls.append((value,before))
 need(CA["read_view_proof"]["path"]==str(AUX/"five_parent_context_reader_proof.json"),"Actual adapter context proof destination required")
 output_controls.append(ro(CA["read_view_proof"]["path"],CA["read_view_proof"]))
 need(A["exact_five_parent_context_reader_proof"]["path"]==str(OUT/"exact_five_parent_context_reader_proof.json"),"Actual library exact context proof destination required")
 output_controls.append(ro(A["exact_five_parent_context_reader_proof"]["path"],A["exact_five_parent_context_reader_proof"]))
 pin=A['inherited_entrypoint_source_scope']
 need(pin==I['inherited_entrypoint_source_scope']==C['inherited_entrypoint_source_scope'] and pin['path']==str(OUT/'inherited_entrypoint_source_scope.json'),'Actual inherited entrypoint scope pointer/destination differs')
 output_controls.append(ro(pin['path'],pin))
 dq=A['mandatory_derived_pipeline_qualification']
 need(type(dq)is dict and set(dq)==set(DERIVED_EXPECTED9)|{'actual_terminal_accounting'},'Mandatory derived qualification must be exact composite10, not a receipt')
 need(g.exact_json({k:dq[k]for k in DERIVED_EXPECTED9},DERIVED_EXPECTED9)and dq['all_eight_actual_suite_rows_verified']is True,'Current producer derived composite fixed9 binding differs')
 dm=plan['modules'][8]
 need(dm['role']=='default_workflow_integration'and g.exact_json(dm['gate'],{'receipt':{'path':'/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/default_materialized_integration_13420/acceptance.json','bytes':66643,'sha256':'8c0be93c1c7d800fba69fc4a93533eb2df58767df3e85776377e6e2e24ff194c'},'expected_status':'DEFAULT_GENERIC_PHYSICAL_GATE_AND_MATERIALIZED_RUNTIME_INTEGRATION_CPU_VERIFIED_NOT_PUBLISHED'}),'Exact inherited default integration Plan gate differs')
 da=dq['actual_terminal_accounting']
 need(type(da)is dict and set(da)=={'raw','row','job_id','state','exit_code','allocated_CPUs','allocated_GPUs','elapsed_seconds'},'Derived actual terminal accounting shape differs')
 need(type(da['raw'])is str and type(da['row'])is list and len(da['row'])>=9 and all(type(x)is str for x in da['row']),'Derived terminal raw/row types differ')
 dr=da['row'];need(dr[0:3]==['13306','COMPLETED','0:0']and dr[3].isdigit()and dr[5:9]==['u21111210118','u21111210118','test9_generic_design_guard_v2','organ']and [x.split('|')for x in da['raw'].splitlines()if x.split('|',1)[0]=='13306']==[dr],'Derived exact saved current terminal row differs')
 dv=dict(x.split('=',1)for x in dr[4].split(',')if '='in x)
 def derived_numeric_tres(key):
  value=dv.get(key,'0');need(re.fullmatch('[0-9]+',value)is not None,'Derived terminal numeric TRES required');return int(value)
 dc=derived_numeric_tres('cpu');dg=max(derived_numeric_tres('gres/gpu'),sum(derived_numeric_tres(k)for k in dv if k.startswith('gres/gpu:')))
 need(dc>=1 and dg==0 and all(type(da[k])is int for k in('allocated_CPUs','allocated_GPUs','elapsed_seconds'))and da['job_id']=='13306'and da['state']=='COMPLETED'and da['exit_code']=='0:0'and da['allocated_CPUs']==dc and da['allocated_GPUs']==0 and da['elapsed_seconds']==int(dr[3]),'Derived producer actual COMPLETED0 CPU/GPU0 accounting differs')
 def graph_full_readback():
  final_graph=[read(pin["path"])for pin,meta in output_controls[:4]]
  need(all(g.exact_json(got,want)for got,want in zip(final_graph,[A,CA,I,C])),"All four graph objects changed after final JSON")
  g.parent_diagnostic_history_source_coverage(proof_objects[5][0],final_graph[3],final_graph[2])
  need(g.exact_json(g.catalog_msa_gap_projection_native(final_graph[3]),catalog_native),"Catalog original native projection fork")
  need(g.catalog_msa_gap_projection_shape(catalog_objects[0],catalog_objects[1],catalog_objects[2],final_graph[3])is True,"Catalog pure final C projection fork")
  for pin,meta in output_controls[:4]:ro(pin["path"],pin,meta)
 def outputs_end():
  graph_full_readback()
  for pin,meta in output_controls:ro(pin["path"],pin,meta)
  for proof,index,verify_family in proof_objects:verify_family(proof,index,allocation)
  for family,position in[("inventory13299",2),("archive13298",3),("relative13295",4),("parent13290",5)]:g._fixed_history_authority_fence(family,proof_objects[position][0]["authority_metadata_before"])
  g.catalog_msa_gap_saved_fence(catalog_native)
  for pin,meta in catalog_control_records:ro(pin["path"],pin,meta)
  graph_full_readback()
  for pin,meta in output_controls:ro(pin["path"],pin,meta)
  for before in output_dirs:need(md(authority(before["path"]))==before,"Actual owned output directory native drift")
  g.catalog_msa_gap_saved_fence(catalog_native)
 outputs_end();inputs_end();native_end()
 phase="exclusive_final_root_proof_no_staging";PROOF.mkdir(mode=0o755)
 result=dict(Common_original_metadata_only_before=common,Common_original_metadata_only_after=md(Path(common["path"])),Root_Common_metadata_only_no_payload_IO=True,catalog_msa_gap_projection_original_metadata=catalog_native,catalog_msa_gap_projection_actual_control_receipts=[pin for pin,meta in catalog_control_records],schema="root-actual-final-source-v13-production-execution-control.v1",status="ROOT_ACTUAL_NEW_SOURCE356_A_CA_I_C_AND_SIX_FINITE_PRESERVATION_PROOFS_AND_CATALOG_MSA_PROJECTION_CPU_VERIFIED_NOT_STAGED_NOT_PUBLISHED",actual_job_id=jid,allocation=allocation,current_actual_readiness=readiness,current_readiness_own_CPU_receipts=[pin for pin,meta in readyvalues],actual_direct_frozen_adapter_argv=actual_argv,actual_new_library_acceptance=output_controls[0][0],actual_new_adapter_acceptance=output_controls[1][0],actual_new_inclusion=output_controls[2][0],actual_new_closure=output_controls[3][0],actual_new_runner_source_snapshot=I["runner_source_snapshot"],qualified_software_acceptance=SW[0],qualified_source12=sourcepins,qualified_source12_metadata=source_meta,actual_own_pinned_Source14_rows=added_source_rows,actual_own_pinned_Source14_metadata=added_source_metadata,historical_Source2_and_launcher_own_CPU_receipts=historical3,historical_Source2_and_launcher_hash_only_never_imported_compiled_or_executed_by_Root=True,qualified_software4=SW,conditional_core_runtime=runtime,control_receipts=[pin for pin,meta in controls],control_metadata_before=[meta for pin,meta in controls],control_metadata_after=[md(pin["path"])for pin,meta in controls],current_canonical_Source4_receipts=canonical,current_canonical_Source4_metadata_before=canonicalmeta,current_canonical_Source4_metadata_after=[md(pin["path"])for pin in canonical],protected_input_metadata_unique=len(protected),mandatory_contracts=contractpin,mandatory_356_producer_PASS=True,mandatory_356_unique_named_PASS_no_failure_error_skip=True,mandatory_356_named_tests=named356,mandatory_356_named_cases_and_order_equal_qualified_software356=True,actual_new_output_directory_metadata=output_dirs,qualified_G17722_rec_all12_and_postread_metadata_PASS=True,actual_current_source_and_runtime_pre_end_after_final_readonly_PASS=True,all_A_CA_I_C_finite_proof_alias_pointers_equal=True,exact_six_finite_preservation_validators_three_arguments_PASS=True,history_v2_four_authorities_coupled20_only_actual_observations_required=True,parent_diagnostic_Source2_ordinary_C_I_actual_coverage_PASS=True,parent_diagnostic_all4_graph_fullobjects_afterlastJSON_PASS=True,output_artifact_receipts=[pin for pin,meta in output_controls],output_artifact_metadata=[meta for pin,meta in output_controls],request_own_cpu_tuple=qpin,metadata_own_cpu_tuple=mpin,Root_Human_and_precreated_shell_own_CPU_tuples=[ownhuman,ownwrap],true_last_original_native_union_required=True,worker_metadata_only_routes_from_exact_current_verified23_table=True,source_staged=False,published=False,ACTIVE_changed=False,raw_JSON_changed=False,scientific_endpoint_acceptance_performed=False,own_created_controls_LATE_not_Plan_prerequisites=True,qualification_requires_fresh_actual_terminal_Root_plus_two_content_and_independent_RO=True)
 raw=(json.dumps(result,indent=2,allow_nan=False,ensure_ascii=False)+"\n").encode();rp=PROOF/"execution_control.json"
 with rp.open("xb")as f:f.write(raw);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444);os.fsync(f.fileno())
 proofmeta=md(rp);enrol([proofmeta]) # BEFORE FIRST Root g.rec of its output proof.
 proofpin=g.rec(rp);need(md(rp)==proofmeta and rp.read_bytes()==raw and read(rp)==result and proofmeta["nlink"]==1,"Root proof first hash/fullJSON/native required")
 outputs_end();inputs_end();PROOF.chmod(0o555)
 fd=os.open(str(PROOF),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
 finaldir=md(authority(PROOF));enrol([finaldir])
 need(stat.S_ISDIR(finaldir["mode"])and stat.S_IMODE(finaldir["mode"])==0o555 and finaldir["nlink"]==2 and{p.name for p in PROOF.iterdir()}=={"execution_control.json"}and rp.read_bytes()==raw and read(rp)==result and g.rec(rp)==proofpin and md(rp)==proofmeta,"Final exact Root proof/D fullbytes/native required")
 outputs_end();inputs_end()
 need(md(PROOF)==finaldir and md(rp)==proofmeta,"Final Root proof/D drift after last inputs")
 native_end() # TRUE LAST: no later filesystem/JSON/hash/rec/readlink/payload or baseline creation.
 print(json.dumps(dict(status=result["status"],execution_control=proofpin,acceptance=output_controls[0][0],context_adapter_acceptance=output_controls[1][0],inclusion=output_controls[2][0],closure=output_controls[3][0],actual_new_runner_source_snapshot=I["runner_source_snapshot"],request=qpin,request_metadata=mpin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,true_last_original_native_union_PASS=True,qualification_still_requires_fresh_terminal_and_full_Root_two_independent_readbacks=True),sort_keys=True),flush=True)
except BaseException as e:
 try:
  if not PROOF.exists():PROOF.mkdir(mode=0o755)
  if stat.S_IMODE(PROOF.stat().st_mode)&0o222:
   fail=(json.dumps(dict(schema="root-final-source-v13-production-incomplete.v1",status="ROOT_FINAL_SOURCE_V13_PRODUCTION_UNQUALIFIED_NO_STAGING",actual_job_id=jid,phase=phase,reason_type=type(e).__name__,reason=str(e),actual_argv=actual_argv,source_staged=False,published=False,ACTIVE_changed=False),indent=2)+"\n").encode()
   with(PROOF/"typed_incomplete.json").open("xb")as f:f.write(fail);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 except Exception as se:print("Failure proof best-effort "+repr(se),file=sys.stderr,flush=True)
 raise
```
