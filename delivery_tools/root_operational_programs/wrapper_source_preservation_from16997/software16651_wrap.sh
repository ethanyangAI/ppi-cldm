set -euo pipefail
export CUDA_VISIBLE_DEVICES='' JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
unset PYTHONPATH
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python -B - <<'ROOT_FINITE_WORKER_SOFTWARE'
import os, sys, json, re, stat, time, datetime, subprocess
from pathlib import Path
S = Path("/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery")
jid = os.environ.get("SLURM_JOB_ID", "")
if not re.fullmatch("[0-9]+", jid):
    raise SystemExit("Current owned Slurm job ID required")
expected_env = {"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
if any(os.environ.get(k) != v for k, v in expected_env.items()) or "PYTHONPATH" in os.environ:
    raise SystemExit("Original CPU/import/thread isolation required")
D = S / "submissions" / ("source_finite_worker_alias_software_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_final_source_finite_worker_alias_v3", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-source-finite-worker-alias-software-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_SOURCE_FINITE_WORKER_ALIAS_SOFTWARE_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_SOURCE_FINITE_WORKER_ALIAS_SOFTWARE_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_SOURCE_FINITE_WORKER_ALIAS_SOFTWARE_NOT_EXECUTED"
obj = {"schema": "root-current-owned-source-finite-worker-alias-software-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "software_execution_next_not_acceptance": True}), flush=True)




# Reviewed original OWN6 software entry only; no Source audit or model operation.
def dispatch_need(value,message):
 if not value: raise ValueError(message)
dispatch_need(sys.flags.optimize==0,"Unoptimized Python required for reviewed software dispatch")
P=S/"pending/final_source_closure_v3_fixturefix4_finite_worker_alias1"
names=("final_source_closure.py","test_final_source_closure.py","final_source_cpu.sbatch","HANDOFF.md","FINAL_SOURCE_CHECKLIST.md","final_source_context_adapter.py")
sizes=(164179,78857,1613,15973,3280,9850)
mtimes=(1792060567000000000,1792060567000000000,1792059367000000000,1792060567000000000,1792059752000000000,1792059367000000000)
def dispatch_md(path):
 path=Path(path)
 for a in [path]+list(path.parents):
  dispatch_need(not stat.S_ISLNK(a.lstat().st_mode),"Nonlink software/control ancestry required")
 t=path.lstat()
 return dict(path=str(path),bytes=t.st_size,inode=t.st_ino,mtime_ns=t.st_mtime_ns,ctime_ns=t.st_ctime_ns,mode=t.st_mode,dev=t.st_dev,nlink=t.st_nlink,uid=t.st_uid,gid=t.st_gid)
pd=dispatch_md(P)
dispatch_need(stat.S_ISDIR(pd["mode"])and stat.S_IMODE(pd["mode"])==0o555 and pd["inode"]==144115643443090536 and pd["mtime_ns"]==1792059367000000000 and pd["ctime_ns"]==1792060781000000000 and set(x.name for x in P.iterdir())==set(names),"Exact postseal readonly OWN6 directory required")
current=[]
for index,(name,size,mtime) in enumerate(zip(names,sizes,mtimes)):
 value=dispatch_md(P/name)
 dispatch_need(stat.S_ISREG(value["mode"])and stat.S_IMODE(value["mode"])==0o444 and value["nlink"]==1 and value["bytes"]==size and value["inode"]==(144115643443090537,144115643443090540,144115643443090539,144115643443090541,144115643443090542,144115643443090538)[index] and value["mtime_ns"]==mtime and value["ctime_ns"]==1792060781000000000,"Exact postseal reviewed source identity required")
 current.append(value)
seal=S/"submissions/final_source_finite_worker_alias1_source_metadata_readonly_seal/receipt.json"
sm=dispatch_md(seal);sd=dispatch_md(seal.parent)
dispatch_need(stat.S_ISREG(sm["mode"])and stat.S_IMODE(sm["mode"])==0o444 and sm["nlink"]==1 and sm["bytes"]==6756 and sm["inode"]==144115643443090763 and sm["mtime_ns"]==sm["ctime_ns"]==1792060781000000000,"Exact actual SourceRO6756 identity required")
dispatch_need(stat.S_ISDIR(sd["mode"])and stat.S_IMODE(sd["mode"])==0o555 and sd["inode"]==144115643443090762 and sd["mtime_ns"]==sd["ctime_ns"]==1792060781000000000,"Exact readonly SourceRO directory required")
saved=json.loads(seal.read_text())
dispatch_need(saved.get("schema")=="final-source-finite-worker-alias-source-metadata-readonly-seal.v1"and saved.get("status")=="REVIEWED_FINAL_SOURCE_FINITE_WORKER_ALIAS_OWN6_METADATA_RO_PASS_122_PREPARED_NOT_EXECUTED"and saved.get("Root_plus_two_independent_whole_STATIC_PASS")is True and saved.get("metadata_only")is True and type(saved.get("prepared_contracts"))is int and saved["prepared_contracts"]==122 and saved.get("retained_predecessor_contracts")==90 and saved.get("additional_finite_worker_CONTROL_contracts")==32,"Exact reviewed SourceRO header/count required")
dispatch_need(saved.get("software_accepted")is False and saved.get("source_audit_accepted")is False and saved.get("source_staged")is False and saved.get("ACTIVE_changed")is False and saved.get("after_files")==current and saved.get("after_directory")==pd,"Exact complete postseal table and nonacceptance required")
dispatch_need(dispatch_md(seal)==sm and dispatch_md(seal.parent)==sd and dispatch_md(P)==pd and [dispatch_md(P/name)for name in names]==current,"Source/control metadata drift during dispatch preparation")
os.execv("/bin/bash",["/bin/bash",str(P/"final_source_cpu.sbatch"),"software"])
ROOT_FINITE_WORKER_SOFTWARE
