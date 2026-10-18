#!/bin/bash
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
D = S / "submissions" / ("source_plan_v13_ownsha_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_source_plan_v13_ownsha_cpu", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:10:00", "MinMemoryNode": "8G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/8G10/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-plan-v13-ownsha-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_PLAN_V13_OWN_SHA_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_PLAN_V13_OWN_SHA_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_PLAN_V13_OWN_SHA_NOT_EXECUTED"
obj = {"schema": "root-current-owned-plan-v13-ownsha-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "own_plan_hash_capture_next_not_acceptance": True}), flush=True)

# Only entered after actual current owned CPU1/GPU0 readiness.
import hashlib, importlib.util
R=Path("/lustre/users/u21111210118/projects/test9")
CORE=R/"env/core/bin/python";REAL=CORE.with_name("python3.11")
SPEC=json.loads("{\"conditional_CORE_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/env/core/bin/python\",\"bytes\":10,\"inode\":144115618512131424,\"mtime_ns\":1790940371000000000,\"ctime_ns\":1790940371000000000,\"mode\":41471,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11\",\"bytes\":25916456,\"inode\":144115618512129393,\"mtime_ns\":1790940364000000000,\"ctime_ns\":1790940383000000000,\"mode\":33277,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"qualified_original_source6\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_closure.py\",\"bytes\":344832,\"sha256\":\"761829c3cbf2dc4bf1f790c2ec80b7fd0fdb2802adf2854d69360164114fa516\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/test_final_source_closure.py\",\"bytes\":386616,\"sha256\":\"892a20501bbc27ef131a2824d067c9bd7e58256f1b2aff4b593bbf57cb1caa91\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_cpu.sbatch\",\"bytes\":1675,\"sha256\":\"67bda42b010ca2a67108bf3db349ef569ff5f93358e4a665f1c74e4b5a077a14\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/HANDOFF.md\",\"bytes\":19743,\"sha256\":\"be6d5a31b25e9f05906e313872942a9df89954b3bcd945d9e2c1f5983468bbe6\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5185,\"sha256\":\"2018fa544edd313211b2e8f1eef5fa12751b26f5122a688b898397dcaddcf1fb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_context_adapter.py\",\"bytes\":23970,\"sha256\":\"e593ad54990028e3b285d938a291058c39c3b86ebe647cd017265af9907adae3\"}],\"qualified_frozen_source6\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_closure.py\",\"bytes\":344832,\"sha256\":\"761829c3cbf2dc4bf1f790c2ec80b7fd0fdb2802adf2854d69360164114fa516\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/test_final_source_closure.py\",\"bytes\":386616,\"sha256\":\"892a20501bbc27ef131a2824d067c9bd7e58256f1b2aff4b593bbf57cb1caa91\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_cpu.sbatch\",\"bytes\":1675,\"sha256\":\"67bda42b010ca2a67108bf3db349ef569ff5f93358e4a665f1c74e4b5a077a14\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/HANDOFF.md\",\"bytes\":19743,\"sha256\":\"be6d5a31b25e9f05906e313872942a9df89954b3bcd945d9e2c1f5983468bbe6\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5185,\"sha256\":\"2018fa544edd313211b2e8f1eef5fa12751b26f5122a688b898397dcaddcf1fb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_context_adapter.py\",\"bytes\":23970,\"sha256\":\"e593ad54990028e3b285d938a291058c39c3b86ebe647cd017265af9907adae3\"}],\"qualified_source12_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_closure.py\",\"bytes\":344832,\"inode\":144115643443094275,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/test_final_source_closure.py\",\"bytes\":386616,\"inode\":144115643443094276,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_cpu.sbatch\",\"bytes\":1675,\"inode\":144115643443094277,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/HANDOFF.md\",\"bytes\":19743,\"inode\":144115643443094278,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5185,\"inode\":144115643443094279,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_context_adapter.py\",\"bytes\":23970,\"inode\":144115643443094280,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_closure.py\",\"bytes\":344832,\"inode\":144115643979967842,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/test_final_source_closure.py\",\"bytes\":386616,\"inode\":144115643979967843,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_cpu.sbatch\",\"bytes\":1675,\"inode\":144115643979967844,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/HANDOFF.md\",\"bytes\":19743,\"inode\":144115643979967845,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5185,\"inode\":144115643979967846,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_context_adapter.py\",\"bytes\":23970,\"inode\":144115643979967847,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"qualified_original_source_directory\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1\",\"bytes\":4096,\"inode\":144115643443094274,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"qualified_frozen_source_directory\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner\",\"bytes\":4096,\"inode\":144115643979967841,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"qualified_software_controls\":[{\"bytes\":6668,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/acceptance.json\",\"sha256\":\"edb92387fc2c6e3b37cee25968e06445f8180d9a3bef85af937232329d124a9a\"},{\"bytes\":2214,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/contracts.json\",\"sha256\":\"457b4fc15361ea4112ea88ce40fe9d8c61060c6398aac7544f98235f7197b1bd\"},{\"bytes\":73394,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/contracts.txt\",\"sha256\":\"39731c16206b887b472ef86d4a91a3e7261f76bf20f6837a0e1ed31c8a15e767\"},{\"bytes\":16019,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/source_snapshot.json\",\"sha256\":\"624fa07f9adad5d20e64d33a7e0001bee1323cb8ad5f368a1649b5cdea2d277a\"}],\"qualified_software_control_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/acceptance.json\",\"bytes\":6668,\"inode\":144115643979986259,\"mtime_ns\":1792167903000000000,\"ctime_ns\":1792167903000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/contracts.json\",\"bytes\":2214,\"inode\":144115643979986257,\"mtime_ns\":1792167903000000000,\"ctime_ns\":1792167903000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/contracts.txt\",\"bytes\":73394,\"inode\":144115643979967848,\"mtime_ns\":1792167903000000000,\"ctime_ns\":1792167903000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/source_snapshot.json\",\"bytes\":16019,\"inode\":144115643979986258,\"mtime_ns\":1792167903000000000,\"ctime_ns\":1792167903000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"source_software_terminal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_catalog_msa_gap_contracts17722_actual_software_terminal_metadata_readonly_seal/receipt.json\",\"bytes\":15460810,\"inode\":144115643443094507,\"mtime_ns\":1792168494000000000,\"ctime_ns\":1792168494000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"software_outer_proof\":{\"bytes\":372881,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_catalog_msa_gap_contracts_software_outer_17722/execution_control.json\",\"sha256\":\"04a968137922f20eeb323ad416612ac31dd8354a56c8f292662cfcaa32be0597\"},\"software_outer_proof_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_catalog_msa_gap_contracts_software_outer_17722/execution_control.json\",\"bytes\":372881,\"inode\":144115643979986260,\"mtime_ns\":1792167909000000000,\"ctime_ns\":1792167909000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"source_readonly_seal\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_catalog_msa_gap_contracts1_source_metadata_readonly_seal/receipt.json\",\"bytes\":15256984,\"sha256\":\"4fbba17486a03087f5ad0d39a9c14b0666eeb851cf72a653c2e85b3e69acab41\"},\"source_readonly_seal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_catalog_msa_gap_contracts1_source_metadata_readonly_seal/receipt.json\",\"bytes\":15256984,\"inode\":144115643443094326,\"mtime_ns\":1792167040000000000,\"ctime_ns\":1792167040000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"source_readonly_seal_directory_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_catalog_msa_gap_contracts1_source_metadata_readonly_seal\",\"bytes\":4096,\"inode\":144115643443094325,\"mtime_ns\":1792167040000000000,\"ctime_ns\":1792167040000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"software_humans_readonly_seal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_source_catalog_msa_gap_contracts_software_human_metadata_readonly_seal/receipt.json\",\"bytes\":15408276,\"inode\":144115643443094372,\"mtime_ns\":1792167583000000000,\"ctime_ns\":1792167583000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"actual_additional_14_Source_rows\":[{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_closure.py\",\"bytes\":344832,\"sha256\":\"761829c3cbf2dc4bf1f790c2ec80b7fd0fdb2802adf2854d69360164114fa516\"},\"repository_relative\":\"delivery_tools/source_closure_catalog_msa_gap_contracts1/original/final_source_closure.py\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/test_final_source_closure.py\",\"bytes\":386616,\"sha256\":\"892a20501bbc27ef131a2824d067c9bd7e58256f1b2aff4b593bbf57cb1caa91\"},\"repository_relative\":\"delivery_tools/source_closure_catalog_msa_gap_contracts1/original/test_final_source_closure.py\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_cpu.sbatch\",\"bytes\":1675,\"sha256\":\"67bda42b010ca2a67108bf3db349ef569ff5f93358e4a665f1c74e4b5a077a14\"},\"repository_relative\":\"delivery_tools/source_closure_catalog_msa_gap_contracts1/original/final_source_cpu.sbatch\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/HANDOFF.md\",\"bytes\":19743,\"sha256\":\"be6d5a31b25e9f05906e313872942a9df89954b3bcd945d9e2c1f5983468bbe6\"},\"repository_relative\":\"delivery_tools/source_closure_catalog_msa_gap_contracts1/original/HANDOFF.md\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5185,\"sha256\":\"2018fa544edd313211b2e8f1eef5fa12751b26f5122a688b898397dcaddcf1fb\"},\"repository_relative\":\"delivery_tools/source_closure_catalog_msa_gap_contracts1/original/FINAL_SOURCE_CHECKLIST.md\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_context_adapter.py\",\"bytes\":23970,\"sha256\":\"e593ad54990028e3b285d938a291058c39c3b86ebe647cd017265af9907adae3\"},\"repository_relative\":\"delivery_tools/source_closure_catalog_msa_gap_contracts1/original/final_source_context_adapter.py\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_closure.py\",\"bytes\":344832,\"sha256\":\"761829c3cbf2dc4bf1f790c2ec80b7fd0fdb2802adf2854d69360164114fa516\"},\"repository_relative\":\"delivery_tools/source_closure_catalog_msa_gap_contracts1/software_17722/final_source_closure.py\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/test_final_source_closure.py\",\"bytes\":386616,\"sha256\":\"892a20501bbc27ef131a2824d067c9bd7e58256f1b2aff4b593bbf57cb1caa91\"},\"repository_relative\":\"delivery_tools/source_closure_catalog_msa_gap_contracts1/software_17722/test_final_source_closure.py\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_cpu.sbatch\",\"bytes\":1675,\"sha256\":\"67bda42b010ca2a67108bf3db349ef569ff5f93358e4a665f1c74e4b5a077a14\"},\"repository_relative\":\"delivery_tools/source_closure_catalog_msa_gap_contracts1/software_17722/final_source_cpu.sbatch\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/HANDOFF.md\",\"bytes\":19743,\"sha256\":\"be6d5a31b25e9f05906e313872942a9df89954b3bcd945d9e2c1f5983468bbe6\"},\"repository_relative\":\"delivery_tools/source_closure_catalog_msa_gap_contracts1/software_17722/HANDOFF.md\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5185,\"sha256\":\"2018fa544edd313211b2e8f1eef5fa12751b26f5122a688b898397dcaddcf1fb\"},\"repository_relative\":\"delivery_tools/source_closure_catalog_msa_gap_contracts1/software_17722/FINAL_SOURCE_CHECKLIST.md\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_context_adapter.py\",\"bytes\":23970,\"sha256\":\"e593ad54990028e3b285d938a291058c39c3b86ebe647cd017265af9907adae3\"},\"repository_relative\":\"delivery_tools/source_closure_catalog_msa_gap_contracts1/software_17722/final_source_context_adapter.py\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_CATALOG_MSA_GAP_CONTRACTS_SOURCE_SOFTWARE_FROM17556_20261016.md\",\"bytes\":211855,\"sha256\":\"82a753135360f39fd9be1b3185af984d642a5c03b262f1af4d34a19a2c5056a6\"},\"repository_relative\":\"delivery_tools/human_history/ROOT_FIXED_CATALOG_MSA_GAP_CONTRACTS_SOURCE_SOFTWARE_FROM17556_20261016.md\"},{\"receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_catalog_msa_gap_contracts_software_from17556_primary_claim/wrap.sh\",\"bytes\":208446,\"sha256\":\"2558a72b18c21516607f876d12c26953e8774e89ae37b5825769a0f4b32d4c45\"},\"repository_relative\":\"delivery_tools/root_operational_programs/final_source_catalog_msa_gap_contracts_software_from17556_primary_claim/wrap.sh\"}],\"actual_additional_14_Source_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_closure.py\",\"bytes\":344832,\"inode\":144115643443094275,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/test_final_source_closure.py\",\"bytes\":386616,\"inode\":144115643443094276,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_cpu.sbatch\",\"bytes\":1675,\"inode\":144115643443094277,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/HANDOFF.md\",\"bytes\":19743,\"inode\":144115643443094278,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5185,\"inode\":144115643443094279,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix13_catalog_msa_gap_contracts1/final_source_context_adapter.py\",\"bytes\":23970,\"inode\":144115643443094280,\"mtime_ns\":1792166609000000000,\"ctime_ns\":1792167039000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_closure.py\",\"bytes\":344832,\"inode\":144115643979967842,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/test_final_source_closure.py\",\"bytes\":386616,\"inode\":144115643979967843,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_cpu.sbatch\",\"bytes\":1675,\"inode\":144115643979967844,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/HANDOFF.md\",\"bytes\":19743,\"inode\":144115643979967845,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/FINAL_SOURCE_CHECKLIST.md\",\"bytes\":5185,\"inode\":144115643979967846,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_catalog_msa_gap_contracts_software_17722/runner/final_source_context_adapter.py\",\"bytes\":23970,\"inode\":144115643979967847,\"mtime_ns\":1792167758000000000,\"ctime_ns\":1792167758000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_CATALOG_MSA_GAP_CONTRACTS_SOURCE_SOFTWARE_FROM17556_20261016.md\",\"bytes\":211855,\"inode\":144115643443094364,\"mtime_ns\":1792167278000000000,\"ctime_ns\":1792167582000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_catalog_msa_gap_contracts_software_from17556_primary_claim/wrap.sh\",\"bytes\":208446,\"inode\":144115643443094374,\"mtime_ns\":1792167747000000000,\"ctime_ns\":1792167747000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"plan_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17722_v13/final_source_plan.json\",\"bytes\":2063544,\"inode\":144115643443094510,\"mtime_ns\":1792168979000000000,\"ctime_ns\":1792169684000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17722_v13/HANDOFF.md\",\"bytes\":21636,\"inode\":144115643443094511,\"mtime_ns\":1792168979000000000,\"ctime_ns\":1792169684000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"plan_directory_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17722_v13\",\"bytes\":4096,\"inode\":144115643443094509,\"mtime_ns\":1792168979000000000,\"ctime_ns\":1792169684000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"plan_readonly_seal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_from17722_metadata_readonly_seal/receipt.json\",\"bytes\":15458052,\"inode\":144115643443094519,\"mtime_ns\":1792169685000000000,\"ctime_ns\":1792169685000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"plan_readonly_seal_directory_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_from17722_metadata_readonly_seal\",\"bytes\":4096,\"inode\":144115643443094518,\"mtime_ns\":1792169685000000000,\"ctime_ns\":1792169685000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"prior_qualified_plan_and_handoff\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17118_v12/final_source_plan.json\",\"bytes\":2051027,\"sha256\":\"d662372e24f243cae6acfe12ec66e20a1b791c07cc6637cb96d0593d84845e50\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17118_v12/HANDOFF.md\",\"bytes\":24047,\"sha256\":\"4b5a1ef668365a6b69ba1541ee505c1197faf11e9a012550687e08581363ad19\"}],\"prior_qualified_plan_and_handoff_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17118_v12/final_source_plan.json\",\"bytes\":2051027,\"inode\":144115643443093228,\"mtime_ns\":1792145754000000000,\"ctime_ns\":1792146116000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_17118_v12/HANDOFF.md\",\"bytes\":24047,\"inode\":144115643443093229,\"mtime_ns\":1792145754000000000,\"ctime_ns\":1792146116000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"prior_v12_ownsha_capture\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v12_ownsha_17119/capture.json\",\"bytes\":79438,\"sha256\":\"a3bcee82b64481ff06c8652cda2183fbf347433373e52902f0d6201d5a8d20dc\"},\"prior_v12_ownsha_capture_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_plan_v12_ownsha_17119/capture.json\",\"bytes\":79438,\"inode\":144115643493505155,\"mtime_ns\":1792147989000000000,\"ctime_ns\":1792147989000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"current_canonical_Source4\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\",\"bytes\":2225,\"sha256\":\"d602956154fb396fd14d7737c360d7d35144b4e6ca6c3d1c51eb6dc401e42615\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\",\"bytes\":24234,\"sha256\":\"c8fe4495439826f0882b4c43952926e5de5361f88460320cc117d003352ff345\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\",\"bytes\":1633,\"sha256\":\"2d40850d19c7835d658e7154e5a1cb53ae763e31d360b41eec253397f2c5befb\"},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\",\"bytes\":6148,\"sha256\":\"c83e427f73ff1545253d64dbb165c7e60328bb698721d1e03663e6ea7d7c403f\"}],\"current_canonical_Source4_metadata\":[{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bc_supplemental_gpu_launcher.sh\",\"bytes\":2225,\"inode\":144115543165691905,\"mtime_ns\":1791727539000000000,\"ctime_ns\":1791727539000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py\",\"bytes\":24234,\"inode\":144115543165691892,\"mtime_ns\":1791727495000000000,\"ctime_ns\":1791727495000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/supplemental_launcher_freeze.py\",\"bytes\":1633,\"inode\":144115543165691947,\"mtime_ns\":1791727539000000000,\"ctime_ns\":1791727539000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py\",\"bytes\":6148,\"inode\":144115543165691893,\"mtime_ns\":1791727495000000000,\"ctime_ns\":1791727495000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}],\"root_control_human\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V13_OWN_SHA_FROM17722_20261016_REV1.md\",\"primary_wrap\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_ownsha_from17722_primary_claim/wrap.sh\",\"Common_original_metadata_only\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_common_review.py\",\"bytes\":58825,\"inode\":144115543165691265,\"mtime_ns\":1791695459000000000,\"ctime_ns\":1791695459000000000,\"mode\":33204,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}}")
def need(v,msg):
 if not v:raise ValueError(msg)
md=native_metadata
META={"path","bytes","inode","mtime_ns","ctime_ns","mode","dev","nlink","uid","gid"}
original_native={}
def authority(p):
 p=Path(p);need(p.is_absolute() and p.is_relative_to(R),"Exact authority path required")
 for a in [p]+list(p.parents):
  if a==R.parent:break
  need(not a.is_symlink(),"Nonlink ancestry required")
 return p
def enrol(records):
 for value in records:
  need(type(value)is dict and set(value)==META and type(value["path"])is str and all(type(value[k])is int and value[k]>=0 for k in META-{"path"}),"Exact ORIGINAL native record required")
  old=original_native.get(value["path"])
  need(old is None or old==value,"Conflicting ORIGINAL native baselines")
  original_native[value["path"]]=dict(value)
def native_only_path(path):
 if path==str(CORE):
  value=md(CORE);need(stat.S_ISLNK(value["mode"]) and value["bytes"]==10 and value["nlink"]==1,"Exact conditional CORE logical native type required");return CORE
 if path==str(REAL):
  value=md(REAL);need(stat.S_ISREG(value["mode"]) and value["bytes"]==25916456 and value["nlink"]==1,"Exact conditional CORE resolved native type required");return REAL
 if path==SPEC["Common_original_metadata_only"]["path"]:
  return Path(path) # Exact fixed Common native-only exception: no authority/resolve/payload.
 return authority(path)
def native_end():
 # TRUE-LAST: no payload read, JSON, hash, rec, readlink or refreshed baseline.
 for path,before in original_native.items():
  need(md(native_only_path(path))==before,"Final ORIGINAL saved-native union drift")
 return True
def rec(p):
 p=authority(p);h=hashlib.sha256();n=0
 with p.open("rb")as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b);n+=len(b)
 return dict(path=str(p),bytes=n,sha256=h.hexdigest())
def ro(p,expected=None,metadata=None):
 p=authority(p);before=md(p)
 need(stat.S_ISREG(before["mode"])and stat.S_IMODE(before["mode"])==0o444 and before["nlink"]==1,"Readonly regular singlelink own file required")
 if metadata is not None:need(before==metadata,"Exact qualified original own metadata required")
 enrol([metadata if metadata is not None else before])
 value=rec(p);need(md(p)==before,"Own file full metadata changed while reading")
 if expected is not None:need(value==expected,"Exact actual CPU own fulltuple required")
 return value,before
def pairs(items):
 obj={}
 for k,v in items:need(k not in obj,"Duplicate own JSON key");obj[k]=v
 return obj
def bad(s):raise ValueError("Nonfinite own JSON "+s)
def finite_float(s):
 v=float(s);need(v==v and abs(v)!=float("inf"),"Finite own JSON exponent required");return v
def read(p):
 with Path(p).open("r",encoding="utf-8")as f:return json.load(f,object_pairs_hook=pairs,parse_constant=bad,parse_float=finite_float)
need(Path(sys.executable)==CORE and sys.flags.optimize==0 and sys.flags.isolated==0 and sys.dont_write_bytecode,"Actual unoptimized CORE-B/no-I required")
need(len(SPEC)==30,"Exact literal SPEC30 required")
common=SPEC["Common_original_metadata_only"];need(common["path"]==str(R/"source/rebuild/benchmark_common_review.py") and md(Path(common["path"]))==common,"Exact original Common native-only baseline required");enrol([common])
core=SPEC["conditional_CORE_metadata"];need(len(core)==2 and [x["path"]for x in core]==[str(CORE),str(REAL)],"Exact Core2 order required");enrol(core)
need(md(CORE)==core[0]and md(REAL)==core[1]and os.readlink(CORE)=="python3.11","Exact conditional Core original native/link required")
corepin=dict(path=str(REAL),bytes=25916456,sha256="76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a")
need(rec(REAL)==corepin and md(REAL)==core[1],"Exact conditional Core ownbytes required")
sourcepins=SPEC["qualified_original_source6"]+SPEC["qualified_frozen_source6"]
source_meta=SPEC["qualified_source12_metadata"];need(len(sourcepins)==len(source_meta)==12,"Exact Source12 required");enrol(source_meta)
for r,m in zip(sourcepins,source_meta):ro(r["path"],r,m)
source_dirs=[SPEC["qualified_original_source_directory"],SPEC["qualified_frozen_source_directory"]]
enrol(source_dirs)
source_names={Path(r["path"]).name for r in SPEC["qualified_frozen_source6"]}
for x in source_dirs:
 need(md(authority(x["path"]))==x and stat.S_IMODE(x["mode"])==0o555 and x["nlink"]==2 and {p.name for p in Path(x["path"]).iterdir()}==source_names,"Exact Source6 directory/universe required")
SW=SPEC["qualified_software_controls"];SWmeta=SPEC["qualified_software_control_metadata"]
need(len(SW)==len(SWmeta)==4,"Exact SW4 required");enrol(SWmeta)
for r,m in zip(SW,SWmeta):ro(r["path"],r,m)
a=read(SW[0]["path"]);ct=read(SW[1]["path"])
need(len(a)==18 and a["allocation"]["job_id"]=="17722" and a["source_files"]==SPEC["qualified_frozen_source6"]and a["original_executing_sources"]==SPEC["qualified_original_source6"],"Actual17722 software Source12 bindings required")
outerpin,outermeta=ro(SPEC["software_outer_proof"]["path"],SPEC["software_outer_proof"],SPEC["software_outer_proof_metadata"]);outer=read(outerpin["path"]);fixed=outer["fixed_control_receipts"]
need(len(outer)==51 and outer["schema"]=="root-catalog-msa-gap-contracts-source-software-operational-control.v1"and outer["actual_job_id"]=="17722"and outer["actual_unique_tests"]==356 and outer["historical321_names_classes_and_relative_order_preserved"]is True and len(outer["actual_new_named_tests"])==35 and len(fixed)==len(outer["fixed_control_metadata"])==457 and outer["status"]=="ROOT_ACTUAL_NEW_SOURCE_SOFTWARE_AND_OWN_CONTROLS_READBACK_PASS_NOT_SOURCE_AUDIT_OR_SCIENCE"and outer["source_files"]==SPEC["qualified_frozen_source6"]and outer["original_executing_sources"]==SPEC["qualified_original_source6"]and outer["allocation"]==a["allocation"]and all(outer[k]is False for k in ["Source_audit_acceptance","source_staged","published","ACTIVE_changed"]),"Exact actual17722 CO51/457/software356 required")
need([outer[k]for k in ["actual_software_acceptance","actual_contracts","actual_contract_log","actual_source_snapshot"]]==SW,"Exact CO SW4 pointers required")
terminalpin,terminalmeta=ro(SPEC["source_software_terminal_metadata"]["path"],metadata=SPEC["source_software_terminal_metadata"]);terminal=read(terminalpin["path"])
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
sourceROpin,sourceROmeta=ro(SPEC["source_readonly_seal"]["path"],SPEC["source_readonly_seal"],SPEC["source_readonly_seal_metadata"]);sourceRO=read(sourceROpin["path"])
need(len(sourceRO)==33 and sourceRO["schema"]=="root-catalog-msa-gap-contracts1-source-metadata-readonly-seal.v1"and sourceRO["Root_and_two_whole_final_static_SOURCE_PASS"]is True and sourceRO["source_tests_defined"]==356 and sourceRO["source_directory_after"]==source_dirs[0]and sourceRO["source_files_after"]==source_meta[:6]and outer["source_readonly_seal"]==sourceROpin,"Actual SRO33 original Source6 required")
need(sourceRO["Common_original_metadata_only_before"]==sourceRO["Common_original_metadata_only_after"]==outer["Common_original_metadata_only_before"]==outer["Common_original_metadata_only_after"]==terminal["Common_original_metadata_only_before"]==terminal["Common_original_metadata_only_after"]==common and md(Path(common["path"]))==common,"Original Common metadata-only coupled baselines required")
sro_dir=SPEC["source_readonly_seal_directory_metadata"];enrol([sro_dir])
need(md(authority(sro_dir["path"]))==sro_dir and {p.name for p in Path(sro_dir["path"]).iterdir()}=={"receipt.json"},"Exact original SourceRO directory required")
HROpin,HROmeta=ro(SPEC["software_humans_readonly_seal_metadata"]["path"],metadata=SPEC["software_humans_readonly_seal_metadata"]);HRO=read(HROpin["path"])
need(len(HRO)==31 and HRO["schema"]=="root-catalog-msa-gap-contracts-software-human-metadata-readonly-seal.v1"and HRO["Root_and_two_whole_Human_STATIC_PASS"]is True and HRO["human_metadata_after"]==outer["fixed_control_metadata"][455]and HRO["qualified_source_files"]==source_meta[:6]and HRO["qualified_source_directory"]==source_dirs[0]and HRO["Common_original_metadata_only_before"]==HRO["Common_original_metadata_only_after"]==common,"Actual SOFTWARE HRO31, not self-HRO, required")
ss=importlib.util.spec_from_file_location("root_qualified_source17722_plan_v13_ownsha",Path(SPEC["qualified_frozen_source6"][0]["path"]))
g=importlib.util.module_from_spec(ss);ss.loader.exec_module(g)
need(g.software_shape(a,ct)==SPEC["qualified_frozen_source6"],"Qualified356 pure software shape required")
allocation=g.cpu();runtime=g.conditional_core_runtime()
need(allocation["job_id"]==jid and allocation["allocated_CPUs"]==1 and allocation["allocated_gpus"]==0 and allocation["numeric_sacct_row"]==attempts[selected-1]["actual_row"]and runtime==a["conditional_core_runtime"],"Fresh current owned CPU1/GPU0/Core required")
snapshot=read(SW[3]["path"]);need(g.software_snapshot_shape(a,snapshot)==snapshot,"Qualified snapshot pure shape required")
fixed_by_path={}
for r in fixed:
 g.receipt_shape(r);need(r["path"]not in fixed_by_path,"Duplicate fixed-control path");fixed_by_path[r["path"]]=r
def fixedpin(p):need(str(p)in fixed_by_path,"Explicit fullpath absent actual CO457");return dict(fixed_by_path[str(p)])
names=["final_source_closure.py","test_final_source_closure.py","final_source_cpu.sbatch","HANDOFF.md","FINAL_SOURCE_CHECKLIST.md","final_source_context_adapter.py"]
additionalrows=[]
def addrow(r,d):additionalrows.append(dict(receipt=dict(r),repository_relative=d))
for r in SPEC["qualified_original_source6"]:addrow(r,"delivery_tools/source_closure_catalog_msa_gap_contracts1/original/"+Path(r["path"]).name)
for r in SPEC["qualified_frozen_source6"]:addrow(r,"delivery_tools/source_closure_catalog_msa_gap_contracts1/software_17722/"+Path(r["path"]).name)
h="ROOT_FIXED_CATALOG_MSA_GAP_CONTRACTS_SOURCE_SOFTWARE_FROM17556_20261016.md";addrow(fixedpin(S/"handoffs"/h),"delivery_tools/human_history/"+h)
w="final_source_catalog_msa_gap_contracts_software_from17556_primary_claim";addrow(fixedpin(S/"submissions"/w/"wrap.sh"),"delivery_tools/root_operational_programs/"+w+"/wrap.sh")
need([r["receipt"]for r in additionalrows[-2:]]==fixed[455:457],"Exact currentCO455/456 Human/W required")
need(len(additionalrows)==14 and additionalrows==SPEC["actual_additional_14_Source_rows"],"Exact actual ordered14 Source rows required")
additional=[x["receipt"]for x in additionalrows];additionalmeta=SPEC["actual_additional_14_Source_metadata"];need(len(additionalmeta)==14,"Exact original additional14 metadata required");enrol(additionalmeta)
for r,m in zip(additional,additionalmeta):ro(r["path"],r,m)
planmeta=SPEC["plan_metadata"];need(len(planmeta)==2,"Exact Plan/H metadata required");enrol(planmeta)
planpin,planbefore=ro(planmeta[0]["path"],metadata=planmeta[0]);handoffpin,handoffbefore=ro(planmeta[1]["path"],metadata=planmeta[1])
PLAN=Path(planpin["path"]);HANDOFF=Path(handoffpin["path"])
planROpin,planROmeta=ro(SPEC["plan_readonly_seal_metadata"]["path"],metadata=SPEC["plan_readonly_seal_metadata"]);planRO=read(planROpin["path"])
need(len(planRO)==33 and planRO["schema"]=="root-final-source-plan-v13-from17722-metadata-readonly-seal.v1"and planRO["Root_and_two_whole_Plan_STATIC_PASS"]is True and [planRO["plan_metadata_after"],planRO["handoff_metadata_after"]]==planmeta and planRO["plan_directory_after"]==SPEC["plan_directory_metadata"]and planRO["qualified_software_acceptance"]==SW[0]and planRO["qualified_software_terminal_metadata"]==terminalmeta and planRO["Common_original_metadata_only_before"]==planRO["Common_original_metadata_only_after"]==common,"Actual independently accepted Plan13 RO33 required")
plan_dir=SPEC["plan_directory_metadata"];plan_ro_dir=SPEC["plan_readonly_seal_directory_metadata"];enrol([plan_dir,plan_ro_dir])
need(md(authority(PLAN.parent))==plan_dir and stat.S_IMODE(plan_dir["mode"])==0o555 and {p.name for p in PLAN.parent.iterdir()}=={"final_source_plan.json","HANDOFF.md"},"Exact readonly Plan2 universe required")
need(md(authority(plan_ro_dir["path"]))==plan_ro_dir and {p.name for p in Path(plan_ro_dir["path"]).iterdir()}=={"receipt.json"},"Exact original PlanRO file/D required")
priorpins=SPEC["prior_qualified_plan_and_handoff"];priormeta=SPEC["prior_qualified_plan_and_handoff_metadata"]
need(len(priorpins)==len(priormeta)==2,"Exact prior Plan12/H required")
for r,m in zip(priorpins,priormeta):ro(r["path"],r,m)
priorCAPpin,priorCAPmeta=ro(SPEC["prior_v12_ownsha_capture"]["path"],SPEC["prior_v12_ownsha_capture"],SPEC["prior_v12_ownsha_capture_metadata"]);priorCAP=read(priorCAPpin["path"])
need(priorCAP["actual_job_id"]=="17119"and[priorCAP["plan"],priorCAP["handoff"]]==priorpins,"Actual prior17119 Plan12/H required")
canonical=SPEC["current_canonical_Source4"];canonicalmeta=SPEC["current_canonical_Source4_metadata"]
need(priorCAP["current_canonical_Source4_receipts"]==canonical and priorCAP["current_canonical_Source4_metadata_after"]==canonicalmeta and len(canonical)==len(canonicalmeta)==4,"Exact unchanged canonical4 from actual17119 required");enrol(canonicalmeta)
def canonical_end():
 for r,m in zip(canonical,canonicalmeta):
  p=authority(r["path"]);need(md(p)==m and stat.S_ISREG(m["mode"])and stat.S_IMODE(m["mode"])==0o664 and m["nlink"]==1,"Only four literal canonical mutable leaves permitted")
  need(g.rec(p)==r and md(p)==m,"Exact canonical4 fullbyte/native drift")
canonical_end()
plan=read(PLAN);old=read(priorpins[0]["path"])
roles=["formal13260_terminal_v3","native74_cache_catalog","native74_cache_binding","reference_free_e2e","formal_common_review","independent_statistics","scientific_report","final_delivery_tools","default_workflow_integration"]
need(len(plan)==len(old)==34 and list(plan)==list(old)and plan["schema"]=="final-source-closure-plan.v3"and plan["library_software_acceptance"]==SW[0]and[m["role"]for m in plan["modules"]]==roles,"Exact Plan13 top34/roles/current17722 required")
need(plan["modules"][7]["sources"][-14:]==additionalrows and plan["modules"][7]["seeds"][-18:]==additional+SW,"Only finaltools14/18 ordered tails required")
need(plan["modules"][8]==old["modules"][8]and len(plan["modules"][8]["sources"])==109 and len(plan["modules"][8]["seeds"])==44,"Default WHOLE object109/44 unchanged")
need(plan["context_parent_seeds"]==old["context_parent_seeds"]and len(plan["context_parent_seeds"])==17 and plan["aliases"]==old["aliases"]and len(plan["aliases"])==7,"Ordered17 and seven aliases unchanged")
rewound=json.loads(json.dumps(plan,allow_nan=False));rewound["library_software_acceptance"]=old["library_software_acceptance"];del rewound["modules"][7]["sources"][-14:];del rewound["modules"][7]["seeds"][-18:]
def same(x,y):
 need(type(x)is type(y),"Preserved Plan type drift")
 if type(x)is dict:
  need(list(x)==list(y),"Preserved Plan key order drift")
  for k in x:same(x[k],y[k])
 elif type(x)is list:
  need(len(x)==len(y),"Preserved Plan list length drift")
  for a,b in zip(x,y):same(a,b)
 else:need(x==y,"Preserved Plan scalar drift")
same(rewound,old);oldraw=Path(priorpins[0]["path"]).read_bytes()
need(len(oldraw)==2051027 and(json.dumps(rewound,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode()==oldraw,"ENTIRE raw Plan12 rewind required")
def identity(r):g.receipt_shape(r);return(r["path"],r["bytes"],r["sha256"])
allsources=[r for m in plan["modules"]for r in m["sources"]];allseeds=[r for m in plan["modules"]for r in m["seeds"]]
need(len(allsources)==776 and len({x["repository_relative"]for x in allsources})==715 and len(allseeds)==3973 and len({identity(r)for r in allseeds})==3900 and len(plan["modules"][7]["sources"])==574 and len(plan["modules"][7]["seeds"])==3824,"Exact Plan13 counts required")
destinations=[x["repository_relative"]for x in additionalrows]
need(len(set(destinations))==14 and not set(destinations)&{r["repository_relative"]for m in old["modules"]for r in m["sources"]},"New14 destination collision")
need(g.module_plan(plan)==plan["modules"],"Qualified module_plan pure shape only required")
need(planpin["bytes"]==2063544 and planpin["bytes"]<2097152 and handoffpin["bytes"]==21636,"Exact reviewed Plan13/H sizes required")
ownhuman,ownhumanmeta=ro(SPEC["root_control_human"]);ownwrap,ownwrapmeta=ro(SPEC["primary_wrap"])
humantext=Path(ownhuman["path"]).read_text("utf-8");wraptext=Path(ownwrap["path"]).read_text("utf-8")
need(humantext.count("```python\n")==1 and wraptext.endswith("\nPY\n")and wraptext.partition("<<'PY'\n")[2][:-4].rstrip("\n")==humantext.split("```python\n",1)[1].split("\n```",1)[0].rstrip("\n"),"Actual precreated wrapper must equal whole reviewed Human fence")
enrol(readiness_native_original+[readiness_directory_original])
need(md(authority(D))==readiness_directory_original and {p.name for p in D.iterdir()}==readiness_names_original,"Original readiness D/universe required")
readiness=read(D/"readiness.json");readyvalues=[]
for m in readiness_native_original:readyvalues.append(ro(m["path"],metadata=m))
controls=[(planpin,planbefore),(handoffpin,handoffbefore),(ownhuman,ownhumanmeta),(ownwrap,ownwrapmeta),(planROpin,planROmeta),(sourceROpin,sourceROmeta),(HROpin,HROmeta),(outerpin,outermeta),(terminalpin,terminalmeta),(priorCAPpin,priorCAPmeta)]+list(zip(priorpins,priormeta))
need(len(controls)==len({r["path"]for r,m in controls})==12,"Twelve closed control roles required")
def qualified_rec_end():
 for r,m in controls:need(g.rec(r["path"])==r and md(authority(r["path"]))==m,"Qualified G17722.rec twelve fulltuples/native drift")
qualified_rec_end()
protected=planRO["protected_inputs_after"]
need(planRO["protected_inputs_before"]==protected and len(protected)==len({x["path"]for x in protected})==14490,"Original protected14490 universe required");enrol(protected)
original_names=planRO["original_owned_directory_children"];need(len(original_names)==44,"Exact44 prior directory universes required")
def inputs_end():
 need(md(CORE)==core[0]and md(REAL)==core[1]and rec(REAL)==corepin and md(REAL)==core[1]and os.readlink(CORE)=="python3.11","Conditional Core fullbyte/native drift")
 for r,m in zip(sourcepins,source_meta):ro(r["path"],r,m)
 for x in source_dirs:need(md(authority(x["path"]))==x and {p.name for p in Path(x["path"]).iterdir()}==source_names,"Original Source6 directory/universe drift")
 for r,m in zip(SW,SWmeta):ro(r["path"],r,m)
 for r,m in controls+readyvalues:ro(r["path"],r,m)
 qualified_rec_end()
 for r,m in zip(additional,additionalmeta):ro(r["path"],r,m)
 for x in protected:need(md(native_only_path(x["path"]))==x,"Original protected native drift")
 need(md(authority(PLAN.parent))==plan_dir and md(authority(plan_ro_dir["path"]))==plan_ro_dir and md(authority(sro_dir["path"]))==sro_dir and md(authority(D))==readiness_directory_original,"Original finite directory drift")
 need({p.name for p in PLAN.parent.iterdir()}=={"final_source_plan.json","HANDOFF.md"}and {p.name for p in Path(plan_ro_dir["path"]).iterdir()}=={"receipt.json"}and {p.name for p in Path(sro_dir["path"]).iterdir()}=={"receipt.json"}and {p.name for p in D.iterdir()}==readiness_names_original,"Original exact directory universes drift")
 for dp,children in original_names.items():need(sorted(v.name for v in Path(dp).iterdir())==children,"Original protected directory universe drift")
 need(md(Path(common["path"]))==common,"Original Common lstat-only drift")
 canonical_end();need(g.conditional_core_runtime()==runtime,"Approved conditional interpreter drift")
inputs_end();native_end()
OUT=authority(S/"runs")/("final_source_plan_v13_ownsha_"+jid)
need(not OUT.exists()and not OUT.is_symlink(),"Exclusive absent Plan13 capture required")
OUT.mkdir(mode=0o755);phase="own_new_PlanV13_twelve_controls_and14Source_no_child_IO"
try:
 out=dict(Common_original_metadata_only_before=common,Common_original_metadata_only_after=md(Path(common["path"])),Root_Common_metadata_only_no_payload_IO=True,schema="root-fixed-source-plan-v13-own-sha-control-capture.v1",status="ACTUAL_NEW_PLAN_V13_OWN_SHA_AND14_PINNED_SOURCE_DOC_ADDITIONS_CPU_VERIFIED_NOT_SOURCE_AUDIT_ACCEPTANCE",actual_job_id=jid,allocation=allocation,current_actual_readiness=readiness,current_readiness_own_CPU_receipts=[r for r,m in readyvalues],plan=planpin,handoff=handoffpin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,control_receipts=[r for r,m in controls],control_metadata_before=[m for r,m in controls],control_metadata_after=[md(r["path"])for r,m in controls],software_acceptance=SW[0],software_control_receipts=SW,software_control_metadata_before=SWmeta,software_control_metadata_after=[md(r["path"])for r in SW],source_files=SPEC["qualified_frozen_source6"],original_executing_sources=SPEC["qualified_original_source6"],qualified_source12_metadata=source_meta,conditional_core_runtime=runtime,qualified_software17722_terminal_own_CPU_receipt=terminalpin,prior_qualified_PlanV12_and_Handoff=priorpins,qualified_prior17119_ownsha_capture=priorCAPpin,additional_14_Source_rows=additionalrows,additional_14_Source_metadata=additionalmeta,additional_18_safe_seed_receipts=additional+SW,current_canonical_Source4_receipts=canonical,current_canonical_Source4_metadata_before=canonicalmeta,current_canonical_Source4_metadata_after=[md(r["path"])for r in canonical],plan_directory_metadata_before=plan_dir,plan_directory_metadata_after=md(PLAN.parent),Source_n=776,destination_n=715,seed_n=3973,unique_seed_n=3900,role_n=9,parent_n=17,ordered_alias_n=7,all34keys_type_order_and_original_V12_serialized_bytes_rewind_PASS=True,qualified_module_plan_pure_shape_PASS=True,qualified_G17722_rec_all12_controls_pre_end_PASS=True,all_Source12_SW4_Core_controls12_Source14_canonical4_protected14490_pre_end_afteroutput_finalreadonly_required=True,true_last_original_native_union_required_for_final_descriptor=True,plan_child_receipts_shape_only_no_child_IO=True,source_audit_executed=False,source_staged=False,published=False,ACTIVE_changed=False,compiler_or_tests_or_new_software_qualification_executed=False,scientific_receipt_children_read_or_hashed=False,historical_Slurm_queried=False,own_created_controls_LATE_COMPOSER_ONLY_NOT_PLAN_PREREQUISITES=True)
 need(len(out)==56,"Exact56 own-CAP fields required")
 raw=(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode();path=OUT/"capture.json"
 with path.open("xb")as f:f.write(raw);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444);os.fsync(f.fileno())
 outmeta=md(path);enrol([outmeta]) # BASELINE BEFORE FIRST g.rec(CAP).
 descriptor=g.rec(path);need(md(path)==outmeta,"First CAP g.rec changed original native")
 need(path.read_bytes()==raw and read(path)==out and stat.S_IMODE(outmeta["mode"])==0o444 and outmeta["nlink"]==1,"Whole CAP readonly full reread required")
 inputs_end()
 OUT.chmod(0o555)
 fd=os.open(str(OUT),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
 outdir=md(authority(OUT));enrol([outdir])
 need(stat.S_IMODE(outdir["mode"])==0o555 and outdir["nlink"]==2 and {p.name for p in OUT.iterdir()}=={"capture.json"}and path.read_bytes()==raw and read(path)==out and g.rec(path)==descriptor and md(path)==outmeta,"Final CAP/D wholebyte and exact namespace required")
 inputs_end()
 need(md(authority(OUT))==outdir and md(path)==outmeta,"Final output original metadata after input guards required")
 native_end() # TRUE-LAST: no later payload/JSON/hash/rec or baseline creation.
 print(json.dumps(dict(status=out["status"],capture=descriptor,plan=planpin,handoff=handoffpin,root_control_human=ownhuman,actual_precreated_primary_shell=ownwrap,qualified_software17722_terminal_own_CPU_receipt=terminalpin,Source_n=776,destination_n=715,seed_n=3973,unique_seed_n=3900,role_n=9,parent_n=17,final_output_directory_metadata=outdir,true_last_original_native_union_PASS=True,Plan_own_SHA_qualified_only_AFTER_fresh_terminal_RO_Root_and_independent_content_readback=True),sort_keys=True),flush=True)
except BaseException as e:
 try:
  failure=(json.dumps(dict(status="ACTUAL_PLAN_V13_OWN_SHA_UNQUALIFIED",actual_job_id=jid,phase=phase,reason_type=type(e).__name__,reason=str(e),source_staged=False,published=False,ACTIVE_changed=False),indent=2)+"\n").encode()
  with(OUT/"typed_incomplete.json").open("xb")as f:f.write(failure);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 except Exception as se:print("Readonly failure output best-effort: "+repr(se),file=sys.stderr,flush=True)
 raise
PY
