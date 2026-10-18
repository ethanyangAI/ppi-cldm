#!/bin/bash
set -euo pipefail
export PS1="" CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
unset PYTHONPATH
exec "/lustre/users/u21111210118/projects/test9/env/core/bin/python" -B - <<'PY'
import os, sys, json, re, stat, time, datetime, subprocess
from pathlib import Path
S = Path("/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery")
# UNBOUND FIX8 SOURCE PROPOSAL: genuine fixed metadata and planned paths only; post-HRO request binds self files. Prior failedTRO Native is a fixed qualified own-control input; no future SHA or Source permission.
SPEC = {'schema': 'root-final-composer-v7-software-control-binding.v2', 'stage_terminal_metadata': {'path': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_stage17809_actual_terminal_metadata_readonly_seal/receipt.json', 'bytes': 10871344, 'inode': 144115643443094681, 'mtime_ns': 1792180384000000000, 'ctime_ns': 1792180384000000000, 'mode': 33060, 'dev': 1119461688, 'nlink': 1, 'uid': 6263900, 'gid': 6263900}, 'stage_terminal_directory_metadata': {'path': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_stage17809_actual_terminal_metadata_readonly_seal', 'bytes': 4096, 'inode': 144115643443094678, 'mtime_ns': 1792180384000000000, 'ctime_ns': 1792180384000000000, 'mode': 16749, 'dev': 1119461688, 'nlink': 2, 'uid': 6263900, 'gid': 6263900}, 'source_readonly_metadata': {'path': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix8_source_metadata_readonly_seal/receipt.json', 'bytes': 9806167, 'inode': 144115643443095176, 'mtime_ns': 1792224532000000000, 'ctime_ns': 1792224532000000000, 'mode': 33060, 'dev': 1119461688, 'nlink': 1, 'uid': 6263900, 'gid': 6263900}, 'source_readonly_directory_metadata': {'path': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix8_source_metadata_readonly_seal', 'bytes': 4096, 'inode': 144115643443095175, 'mtime_ns': 1792224532000000000, 'ctime_ns': 1792224532000000000, 'mode': 16749, 'dev': 1119461688, 'nlink': 2, 'uid': 6263900, 'gid': 6263900}, 'source_readonly_schema': 'root-final-composer-v7-fix8-source-metadata-readonly-seal.v1', 'source_readonly_field_count': 35, 'source_protected_count': 17902, 'source_current_count': 17920, 'primary_claim_directory': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix8_software_from17837_v1_primary_claim', 'primary_claim_files': ['software_job.sh', 'request.json', 'in_progress.json', 'submit.json', 'sbatch.stdout', 'sbatch.stderr'], 'primary_request_path': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix8_software_from17837_v1_primary_claim/request.json', 'primary_submit_path': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix8_software_from17837_v1_primary_claim/submit.json', 'primary_raw_stdout_path': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix8_software_from17837_v1_primary_claim/sbatch.stdout', 'primary_raw_stderr_path': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix8_software_from17837_v1_primary_claim/sbatch.stderr', 'self_human_path': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_FINAL_COMPOSER_V7_FIX8_SOFTWARE_FROM17837_20261017.md', 'self_primary_path': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix8_software_from17837_v1_primary_claim/software_job.sh', 'self_proposal_path': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_composer_v7_fix8_software_control_from17837_v1/software_control.py', 'self_proposal_directory': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/root_final_composer_v7_fix8_software_control_from17837_v1', 'human_readonly_path': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix8_software_human_metadata_readonly_seal/receipt.json', 'human_readonly_directory': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix8_software_human_metadata_readonly_seal', 'human_readonly_schema': 'root-final-composer-v7-fix8-software-human-metadata-readonly-seal.v1', 'human_static_PASS_field': 'Root_and_two_whole_Human_STATIC_PASS', 'primary_request_schema': 'root-final-composer-v7-fix8-software-scriptfile-primary-request.v1', 'primary_submit_schema': 'root-final-composer-v7-fix8-software-scriptfile-primary-submission.v1', 'shell_header': '#!/bin/bash\nset -euo pipefail\nexport PS1="" CUDA_VISIBLE_DEVICES="" JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1\nunset PYTHONPATH\nexec "/lustre/users/u21111210118/projects/test9/env/core/bin/python" -B - <<\'PY\'\n', 'submit_argv': ['sbatch', '--parsable', '--account=u21111210118', '--qos=normal', '--partition=organ', '--nodes=1', '--ntasks=1', '--cpus-per-task=1', '--mem=16G', '--time=00:30:00', '--job-name=test9_final_composer_partial_cache_names_contracts_v7', '--chdir=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery', '--output=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final_composer_partial_cache_names_contracts_%j.out', '--error=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/logs/final_composer_partial_cache_names_contracts_%j.err', '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_final_composer_v7_fix8_software_from17837_v1_primary_claim/software_job.sh'], 'expected_test_count': 237, 'software_job_name': 'test9_final_composer_partial_cache_names_contracts_v7', 'readiness_namespace': 'root_final_composer_v7_fix8_software_readiness_', 'out_namespace': 'final_composer_operational_provenance_contracts_', 'frozen_namespace': 'final_delivery_composer_v7_operational_source_provenance_', 'tmp_namespace': 'final_composer_operational_provenance_v7_', 'proof_namespace': 'root_final_composer_v7_fix8_software_execution_control_', 'producer_acceptance_schema': 'final-composer-software.v7', 'producer_software_status': 'FINAL_DELIVERY_COMPOSER_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_ARCHIVE_ACCEPTANCE'}
jid = os.environ.get("SLURM_JOB_ID", "")
if not re.fullmatch("[0-9]+", jid):
    raise SystemExit("Current owned Slurm job ID required")
expected_env = {"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
if any(os.environ.get(k) != v for k, v in expected_env.items()) or "PYTHONPATH" in os.environ:
    raise SystemExit("Original CPU/import/thread isolation required")
# These three existing operational parents are metadata/name-only snapshots.
def initial_md(p):
    x=p.lstat();return dict(path=str(p),bytes=x.st_size,inode=x.st_ino,mtime_ns=x.st_mtime_ns,ctime_ns=x.st_ctime_ns,mode=x.st_mode,dev=x.st_dev,nlink=x.st_nlink,uid=x.st_uid,gid=x.st_gid)
operational_parent_before={}
operational_parent_names={}
for parent in (S/"submissions",S/"runs",S/"tmp",S/"frozen"):
    before=initial_md(parent)
    if not stat.S_ISDIR(before["mode"]) or parent.is_symlink():raise SystemExit("Existing nonlink operational parent required")
    names=sorted(os.listdir(parent))
    if initial_md(parent)!=before:raise SystemExit("Operational parent changed during initial names read")
    operational_parent_before[str(parent)]=before
    operational_parent_names[str(parent)]=names
D = S / "submissions" / (SPEC["readiness_namespace"] + jid)
if D.exists() or D.is_symlink():
    raise SystemExit("Exclusive absent current readiness namespace required")
D.mkdir(mode=0o755, exist_ok=False)
readiness_directory_creation=initial_md(D)
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
    if "node" in values and (not re.fullmatch("[0-9]+", values["node"]) or int(values["node"]) != 1):
        raise ValueError("Actual allocated Node1 required when present")
    gpu_values = [values[key] for key in gpu_keys]
    if any(not re.fullmatch("[0-9]+", value) for value in gpu_values) or any(int(value) != 0 for value in gpu_values):
        raise ValueError("Actual current GPU0 required")
    return values
query_env = dict(os.environ, TZ="UTC", SLURM_TIME_FORMAT="standard")
commands = []
operation_deadline = time.monotonic() + 60
gpu_scalar_fields = {}
gpu_environment = {key: os.environ.get(key) for key in ("SLURM_JOB_GPUS","SLURM_STEP_GPUS","SLURM_GPUS","SLURM_GPUS_ON_NODE","SLURM_GPUS_PER_NODE","SLURM_GPUS_PER_TASK","SLURM_GPUS_PER_SOCKET")}
explicit_GPU_state_validated = False
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
    gpu_scalar_fields = {key: fields[key] for key in ("Gres","GRES","TresPerNode","TresPerTask") if key in fields}
    required = {"JobId": jid, "JobName": SPEC["software_job_name"], "Account": "u21111210118", "QOS": "normal", "WorkDir": str(S), "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumNodes": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
    for namespace,value in gpu_scalar_fields.items():
        for token in value.split(","):
            if "gpu" in token.lower():
                matched=re.fullmatch(r"(?:gpu|gres/gpu|gres:gpu)(?::[A-Za-z0-9_.-]+)?[:=]([0-9]+)",token)
                if matched is None or int(matched.group(1))!=0:
                    raise ValueError("Every present scalar GPU namespace must explicitly declare zero")
    for key in ("SLURM_JOB_GPUS","SLURM_STEP_GPUS"):
        if gpu_environment[key] not in (None,""):
            raise ValueError("Assigned GPU identifier environment must be absent or empty, never GPU ID0")
    for key in ("SLURM_GPUS","SLURM_GPUS_ON_NODE","SLURM_GPUS_PER_NODE","SLURM_GPUS_PER_TASK","SLURM_GPUS_PER_SOCKET"):
        value=gpu_environment[key]
        if value not in (None,"") and (re.fullmatch("[0-9]+",value) is None or int(value)!=0):
            raise ValueError("Explicit Slurm GPU count environment must be absent/empty or decimal zero")
    explicit_GPU_state_validated = True
except Exception as e:
    obj = {"schema": "root-current-owned-final-composer-v7-fix3-software-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_FINAL_COMPOSER_V7_FIX3_SOFTWARE_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "software_entered": False, "all_present_scontrol_GPU_scalar_fields": gpu_scalar_fields, "explicit_SLURM_GPU_environment": gpu_environment, "explicit_GPU_state_validated": explicit_GPU_state_validated}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_FINAL_COMPOSER_V7_FIX3_SOFTWARE_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_FINAL_COMPOSER_V7_FIX3_SOFTWARE_NOT_EXECUTED"
obj = {"schema": "root-current-owned-final-composer-v7-fix3-software-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
       "current_scontrol_observation": ctl_saved, "current_scontrol_TRES": current_tres,
       "all_present_scontrol_TRES_fields_CPU1_GPU0": current_tres_fields, "all_present_scontrol_GPU_scalar_fields": gpu_scalar_fields, "explicit_SLURM_GPU_environment": gpu_environment, "explicit_GPU_state_validated": explicit_GPU_state_validated, "attempts": attempts,
       "selected_actual_attempt": selected, "maximum_attempts": 30, "maximum_wait_seconds": 60,
       "environment": {"TZ": "UTC", "SLURM_TIME_FORMAT": "standard", **expected_env},
       "requested_GPUs": 0, "current_allocation_only_no_historical_GPU_inference": True,
       "no_source_or_request_hashes_or_imports_or_tests_by_wait": True,
       "unchanged_library_cpu_guard_will_freshly_requery": True, "actual_queries_not_proxy_or_synthesized_replies": True,
       "software_entered": False,
       "additional_pin_or_source_audit_stage_Git_ACTIVE_acceptance": False}
persist("readiness.json", (json.dumps(obj, indent=2) + "\n").encode()); D.chmod(0o555)
readiness_directory_original=native_metadata(D)
readiness_names_original={Path(x["path"]).name for x in readiness_native_original}
if selected is None:
    raise SystemExit(72)
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "software_next_not_acceptance": True}), flush=True)


# Future owned-CPU operations below are not executed by Source text preparation.
import hashlib, io, runpy, ast, unittest
R=S.parent.parent
CORE_LOGICAL=R/"env/core/bin/python"
CORE_REAL=R/"env/core/bin/python3.11"
CORE_BYTES=25916456
CORE_SHA="76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a"
COMMON=R/"source/rebuild/benchmark_common_review.py"
SPEC_KEYS={"schema","stage_terminal_metadata","stage_terminal_directory_metadata",
 "source_readonly_metadata","source_readonly_directory_metadata","source_readonly_schema",
 "source_readonly_field_count","source_protected_count","source_current_count",
 "primary_claim_directory","primary_claim_files","primary_request_path","primary_submit_path",
 "primary_raw_stdout_path","primary_raw_stderr_path","self_human_path","self_primary_path",
 "self_proposal_path","self_proposal_directory","human_readonly_path","human_readonly_directory",
 "human_readonly_schema","human_static_PASS_field","primary_request_schema","primary_submit_schema",
 "shell_header","submit_argv","expected_test_count","software_job_name","readiness_namespace",
 "out_namespace","frozen_namespace","tmp_namespace","proof_namespace",
 "producer_acceptance_schema","producer_software_status"}
def need(value,message):
    if not value: raise ValueError(message)
need(type(SPEC)is dict and set(SPEC)==SPEC_KEYS and SPEC["schema"]=="root-final-composer-v7-software-control-binding.v2","Closed actual Root software SPEC required")
need(type(SPEC["expected_test_count"])is int and SPEC["expected_test_count"]>130,"Actual stopped software count required")
for key in ("source_readonly_field_count","source_protected_count","source_current_count"):
    need(type(SPEC[key])is int and SPEC[key]>0,"Actual previously sealed Source control denominator required")
for key in ("software_job_name","readiness_namespace","out_namespace","frozen_namespace","tmp_namespace","proof_namespace"):
    need(type(SPEC[key])is str and re.fullmatch("[A-Za-z0-9_]{5,120}",SPEC[key]),"Literal stopped profile/namespace required")
need(sys.flags.isolated==0 and sys.flags.no_user_site==1 and sys.flags.dont_write_bytecode==1,"CORE -B body without -I required")
need(Path(sys.executable)==CORE_LOGICAL or Path(sys.executable)==CORE_REAL,"Exact existing CORE runtime required")
MD_KEYS={"path","bytes","inode","mtime_ns","ctime_ns","mode","dev","nlink","uid","gid"}
def shape_md(value):
    need(type(value)is dict and set(value)==MD_KEYS and type(value["path"])is str and Path(value["path"]).is_absolute(),"Complete native metadata record required")
    need(all(type(value[k])is int for k in MD_KEYS-{"path"}),"Native integer fields required")
    return value
def ordinary_path(p):
    p=Path(p)
    need(p.is_absolute() and (p==R or R in p.parents),"Fixed internal authority path required")
    for q in [p]+list(p.parents):
        if q==R.parent:break
        need(not stat.S_ISLNK(q.lstat().st_mode),"Nonlink ordinary Source/control ancestry required")
    return p
def regular_record(value,readonly=True):
    shape_md(value);ordinary_path(value["path"])
    need(stat.S_ISREG(value["mode"]) and value["nlink"]==1,"Regular singlelink Source/control required")
    if readonly:need(not(value["mode"]&0o222),"Authenticated readonly Source/control required")
    need(native_metadata(Path(value["path"]))==value,"Original complete native record changed")
    return value
def receipt_shape(value):
    need(type(value)is dict and set(value)=={"path","bytes","sha256"} and type(value["path"])is str and Path(value["path"]).is_absolute(),"Complete own receipt required")
    need(type(value["bytes"])is int and value["bytes"]>=0 and type(value["sha256"])is str and re.fullmatch("[0-9a-f]{64}",value["sha256"]),"Complete CPU byte/SHA tuple required")
    return value
original={};created={};creation_events={};payload_paths=set();worker_paths=set()
shared_paths=set(operational_parent_before)
def enroll(rows):
    for value in rows:
        shape_md(value);key=value["path"]
        if key in original:need(original[key]==value,"Conflicting original metadata baselines")
        elif key in created:need(created[key]==value,"Conflicting original/creation baselines")
        else:original[key]=dict(value)
def enroll_created(rows):
    for value in rows:
        shape_md(value);key=value["path"]
        need(key not in original,"Own output collides with original authority")
        if key in created:need(created[key]==value,"Own output baseline cannot refresh")
        else:created[key]=dict(value)
def baseline(p):
    key=str(p);need(key in original or key in created,"Original metadata must be enrolled before first Root payload IO")
    return original.get(key,created.get(key))
def current_matches(p):
    key=str(p);value=creation_events.get(key,baseline(p))
    need(native_metadata(Path(key))==value,"Native changed from original authenticated baseline")
    return value
def allow_payload(rows):
    for value in rows:payload_paths.add(value["path"])
def cpu_rec(p):
    p=ordinary_path(p);need(str(p)!=str(COMMON) and str(p) not in worker_paths,"Common/worker payload is outside software Source/control purpose")
    need(str(p) in payload_paths,"Closed software own-payload path required")
    before=current_matches(p)
    need(stat.S_ISREG(before["mode"]) and before["nlink"]==1,"Singlelink regular own payload required")
    h=hashlib.sha256();size=0
    with p.open("rb")as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            size+=len(block);h.update(block)
    need(native_metadata(p)==before and size==before["bytes"],"Own payload changed during CPU full-byte hashing")
    return dict(path=str(p),bytes=size,sha256=h.hexdigest())
def own_bytes(p,limit):
    p=ordinary_path(p);need(str(p) in payload_paths and str(p)!=str(COMMON) and str(p) not in worker_paths,"Closed own Source/control read required")
    before=current_matches(p);need(before["bytes"]<=limit,"Bounded own Source/control required")
    raw=p.read_bytes()
    need(len(raw)==before["bytes"] and native_metadata(p)==before,"Own bytes/native drift during read")
    return raw
def reject_pairs(pairs):
    result={}
    for key,value in pairs:
        need(key not in result,"Duplicate JSON key");result[key]=value
    return result
def finite_float(value):
    number=float(value);need(number==number and abs(number)!=float("inf"),"Nonfinite/overflow JSON number");return number
def parse_json(raw):
    return json.loads(raw.decode("utf-8"),object_pairs_hook=reject_pairs,parse_float=finite_float,parse_constant=lambda x:(_ for _ in ()).throw(ValueError("Nonfinite JSON constant")))
def own_json(p,limit=20*1024*1024):
    return parse_json(own_bytes(p,limit))
def initial_control(md):
    regular_record(md);enroll([md]);allow_payload([md]);return own_json(md["path"])
def directory_control(md):
    shape_md(md);ordinary_path(md["path"])
    need(stat.S_ISDIR(md["mode"]) and native_metadata(Path(md["path"]))==md,"Original nonlink directory required")
    enroll([md])
# The primary request is generated AFTER Human/HRO/script sealing.
# Its closed schema contains no own MD/SHA, future job ID, or full primary-directory metadata.
# The claim directory baseline is captured only after complete six-file closure and final0555.
CLAIM=Path(SPEC["primary_claim_directory"])
claim_names=SPEC["primary_claim_files"]
need(type(claim_names)is list and len(claim_names)==len(set(claim_names))==6 and all(type(n)is str and Path(n).name==n and n not in ("",".","..")for n in claim_names),"Exactly six planned immutable primary claim basenames")
need(CLAIM.parent==S/"submissions","Literal primary claim directory authority")
for key in ("primary_request_path","primary_submit_path","primary_raw_stdout_path","primary_raw_stderr_path","self_primary_path"):
    need(Path(SPEC[key]).parent==CLAIM and Path(SPEC[key]).name in claim_names,"Literal planned primary file inside same closed claim")
need(len({SPEC[k]for k in ("primary_request_path","primary_submit_path","primary_raw_stdout_path","primary_raw_stderr_path","self_primary_path")})==5,"Distinct primary request/submit/raw/script paths")
claim_deadline=time.monotonic()+60
claim_observations=[];claim_md=None;claim_files=None
for claim_attempt in range(1,31):
    observed=dict(attempt=claim_attempt,complete_readonly=False)
    try:
        if CLAIM.is_symlink():raise ValueError("Primary claim cannot be symbolic")
        if CLAIM.exists():
            observed["directory"]=native_metadata(CLAIM)
            need(stat.S_ISDIR(observed["directory"]["mode"]),"Primary claim must be regular directory")
            observed["names"]=sorted(os.listdir(CLAIM))
            need(set(observed["names"])<=set(claim_names),"Unexpected primary claim member")
            if set(observed["names"])==set(claim_names)and stat.S_IMODE(observed["directory"]["mode"])==0o555:
                rows=[native_metadata(CLAIM/n)for n in claim_names]
                need(all(stat.S_ISREG(v["mode"])and stat.S_IMODE(v["mode"])==0o444 and v["nlink"]==1 for v in rows),"Complete primary files must be exact0444 regular singlelink")
                need(native_metadata(CLAIM)==observed["directory"]and [native_metadata(CLAIM/n)for n in claim_names]==rows,"Primary complete table changed during capture")
                claim_md=observed["directory"];claim_files=rows;observed["complete_readonly"]=True
    except FileNotFoundError:
        observed["temporarily_incomplete"]=True
    claim_observations.append(observed)
    if claim_md is not None:break
    if time.monotonic()>=claim_deadline or claim_attempt==30:break
    time.sleep(min(2,max(0,claim_deadline-time.monotonic())))
need(claim_md is not None,"Bounded wait exhausted before complete readonly six-file primary claim")
# No request/submit bytes have been opened yet. One ORIGINAL table is now enrolled for all six and D.
directory_control(claim_md)
for value in claim_files:regular_record(value)
enroll(claim_files);allow_payload(claim_files)
REQUEST=own_json(SPEC["primary_request_path"],2*1024*1024)
REQUEST_KEYS={"schema","status","stage_terminal_metadata","stage_terminal_directory_metadata",
 "source_readonly_metadata","source_readonly_directory_metadata","Human_after",
 "human_readonly_receipt_metadata","human_readonly_directory_metadata",
 "primary_script_metadata","source_proposal_metadata_after"}
need(type(REQUEST)is dict and set(REQUEST)==REQUEST_KEYS and REQUEST["schema"]==SPEC["primary_request_schema"]and REQUEST["status"]=="ACTUAL_SEALED_SCRIPTFILE_PRIMARY_INPUTS_NOT_SUBMISSION_OR_SOFTWARE_ACCEPTANCE","Closed actual post-HRO primary request")
for key in ("stage_terminal_metadata","stage_terminal_directory_metadata","source_readonly_metadata","source_readonly_directory_metadata"):
    need(REQUEST[key]==SPEC[key],"Actual request must match already-existing literal fixed metadata")
BINDING={"human_readonly_metadata":REQUEST["human_readonly_receipt_metadata"],
 "human_readonly_directory_metadata":REQUEST["human_readonly_directory_metadata"],
 "self_human_metadata":REQUEST["Human_after"],"self_primary_metadata":REQUEST["primary_script_metadata"]}
need(type(REQUEST["source_proposal_metadata_after"])is list and len(REQUEST["source_proposal_metadata_after"])==2,"Exact proposal file/D after seal")
BINDING["self_proposal_metadata"],BINDING["self_proposal_directory_metadata"]=REQUEST["source_proposal_metadata_after"]
BIND_PATHS={"human_readonly_metadata":"human_readonly_path","human_readonly_directory_metadata":"human_readonly_directory",
 "self_human_metadata":"self_human_path","self_primary_metadata":"self_primary_path",
 "self_proposal_metadata":"self_proposal_path","self_proposal_directory_metadata":"self_proposal_directory"}
for key,path_key in BIND_PATHS.items():
    shape_md(BINDING[key]);need(BINDING[key]["path"]==SPEC[path_key],"Exact planned path bound by post-HRO request")
for key in ("human_readonly_metadata","self_human_metadata","self_primary_metadata","self_proposal_metadata"):regular_record(BINDING[key])
for key in ("human_readonly_directory_metadata","self_proposal_directory_metadata"):directory_control(BINDING[key])
enroll(BINDING.values())
SUBMIT=own_json(SPEC["primary_submit_path"],2*1024*1024)
SUBMIT_KEYS={"schema","status","primary_request_path","primary_script_path","argv","returncode",
 "raw_stdout","raw_stderr","submitted_job_id","started_at_UTC","ended_at_UTC","timeout_seconds"}
need(type(SUBMIT)is dict and set(SUBMIT)==SUBMIT_KEYS and SUBMIT["schema"]==SPEC["primary_submit_schema"]and SUBMIT["status"]=="ACTUAL_UNIQUE_SCRIPTFILE_SBATCH_SUBMITTED_NOT_SOFTWARE_ACCEPTANCE","Closed separate actual submission receipt")
need(SUBMIT["primary_request_path"]==SPEC["primary_request_path"]and SUBMIT["primary_script_path"]==SPEC["self_primary_path"],"Actual submission references same sealed request/script")
need(type(SPEC["submit_argv"])is list and SPEC["submit_argv"]and SPEC["submit_argv"][0]=="sbatch"and SPEC["submit_argv"][-1]==SPEC["self_primary_path"]and all(type(v)is str and "--wrap"not in v for v in SPEC["submit_argv"]),"Explicit reviewed script-file transport, never --wrap")
need(SUBMIT["argv"]==SPEC["submit_argv"]and type(SUBMIT["returncode"])is int and SUBMIT["returncode"]==0 and SUBMIT["submitted_job_id"]==jid and SUBMIT["raw_stdout"]==jid+"\n"and SUBMIT["raw_stderr"]=="","Actual unique current numeric job submission")
need(own_bytes(SPEC["primary_raw_stdout_path"],4096)==SUBMIT["raw_stdout"].encode()and own_bytes(SPEC["primary_raw_stderr_path"],4096)==b"","Exact immutable saved sbatch raw files")
need(type(SUBMIT["started_at_UTC"])is str and type(SUBMIT["ended_at_UTC"])is str and type(SUBMIT["timeout_seconds"])in (int,float)and SUBMIT["timeout_seconds"]>0,"Actual submission timing facts")
need(sorted(os.listdir(CLAIM))==sorted(claim_names)and native_metadata(CLAIM)==claim_md,"Original complete claim after all primary JSON")
for value in claim_files:need(native_metadata(Path(value["path"]))==value,"Primary baseline drift after last request/submit JSON")
T=initial_control(SPEC["stage_terminal_metadata"])
directory_control(SPEC["stage_terminal_directory_metadata"])
need(T["schema"]=="root-plan-v13-stage17809-terminal-metadata-readonly-seal.v1" and len(T)==42 and T["actual_job_id"]=="17809" and T["Root_and_two_whole_content_PASS"]is True,"Qualified actual Stage17809 metadata control required")
need(T["Git_changed"]is False and T["published"]is False and T["ACTIVE_changed"]is False and T["full_final_delivery_accepted"]is False,"Stage custody is not final publication/science")
worker_rows=T["worker_exact_metadata_only_routes"]
need(type(worker_rows)is list and len(worker_rows)==68,"Qualified closed worker metadata-only routes required")
need(all(type(value)is str and Path(value).is_absolute()for value in worker_rows) and len(set(worker_rows))==68,"Exact worker metadata-only path set")
worker_paths=set(worker_rows)
core_rows=T["conditional_CORE_metadata_original"]
need(type(core_rows)is list and len(core_rows)==2 and {x["path"]for x in core_rows}=={str(CORE_LOGICAL),str(CORE_REAL)},"Exact existing Core2 native records required")
common_md=T["Common_original_metadata_only_original"];shape_md(common_md)
need(common_md["path"]==str(COMMON),"Exact Common metadata-only record required")
enroll(core_rows+[common_md])
stage_rows=T["protected_non_job_metadata"]+T["job_owned_metadata_after"]+T["fresh_terminal"]["raw_file_metadata"]+[SPEC["stage_terminal_metadata"],SPEC["stage_terminal_directory_metadata"]]
stage_map={}
for value in stage_rows:
    shape_md(value)
    if value["path"]in stage_map:need(stage_map[value["path"]]==value,"Conflicting Stage metadata")
    stage_map[value["path"]]=value
need(len(stage_map)==17516,"Exact accepted Stage17516 universe required")
enroll(stage_map.values())
need(worker_paths<=set(stage_map),"Original worker-route native records must exist in Stage protected custody")
Q=initial_control(SPEC["source_readonly_metadata"])
directory_control(SPEC["source_readonly_directory_metadata"])
need(Q["schema"]==SPEC["source_readonly_schema"] and len(Q)==SPEC["source_readonly_field_count"] and Q["Root_and_two_whole_STATIC_PASS"]is True and Q["protected_metadata_unchanged"]is True,"Actual qualified stopped SourceRO required")
need(Q["actual_Stage_terminal_metadata"]==SPEC["stage_terminal_metadata"] and Q["actual_Stage_terminal_directory_metadata"]==SPEC["stage_terminal_directory_metadata"],"SourceRO binds actual Stage terminal")
protected_map={}
for value in Q["protected_metadata_before"]:
    shape_md(value)
    if value["path"]in protected_map:need(protected_map[value["path"]]==value,"Conflicting original SourceRO protected records")
    protected_map[value["path"]]=value
need(len(protected_map)==SPEC["source_protected_count"] and all(protected_map.get(k)==v for k,v in stage_map.items()),"Actual SourceRO closed protected universe retains exact Stage17516")
enroll(protected_map.values())
need(Q["conditional_CORE_metadata_original"]==core_rows and Q["Common_original_metadata_only_original"]==common_md and Q["worker_exact_metadata_only_routes"]==worker_rows,"SourceRO Core/Common/worker metadata-only bindings")
GROUPS=("composer","existing_API_dependencies","context_API_dependencies")
sources=Q["source_groups_metadata_after"]
need(type(sources)is dict and set(sources)==set(GROUPS) and [len(sources[k])for k in GROUPS]==[15,15,14],"Closed Source44 three-group metadata required")
source_rows=[x for key in GROUPS for x in sources[key]]
need(len({x["path"]for x in source_rows})==44,"ALL44 Source paths separately enrolled; prior exact overlap must agree")
for value in source_rows:regular_record(value)
enroll(source_rows);allow_payload(source_rows)
OWN=Path(sources["composer"][0]["path"]).parent
OWN_NAMES=("final_delivery_composer.py","test_final_delivery_composer.py","composer_bootstrap.py","composer_cpu.sbatch","composer_contracts_cpu.sbatch","HANDOFF.md","composer_context_api.py","relative_archive_restore.py","github_export_context.py","test_github_export_context.py","restored_index_scope.py","test_restored_index_scope.py","finite_source_delivery_context.py","test_finite_source_delivery_context.py","qualified_source_semantics.py")
MAPPER_NAMES=("exact_relative_bbf_context.py","test_exact_relative_bbf_context.py","context_mapper_audit_cpu.py","context_mapper_cpu.sbatch","context_consumer.py","HANDOFF.md","historical_annotation_context.py","test_historical_annotation_context.py","recovered_five_context.py","test_recovered_five_context.py","archive_member_context.py","test_archive_member_context.py","finite_source_context.py","test_finite_source_context.py")
need([x["path"]for x in sources["composer"]]==[str(OWN/n)for n in OWN_NAMES],"Stopped ordered OWN15 roster")
need([Path(x["path"]).name for x in sources["context_API_dependencies"]]==list(MAPPER_NAMES),"Stopped Mapper14 order")
directory_control(Q["original_owned_directory_after"])
source_union=dict(protected_map)
for value in source_rows+[Q["original_owned_directory_after"],SPEC["source_readonly_metadata"],SPEC["source_readonly_directory_metadata"]]:
    if value["path"]in source_union:need(source_union[value["path"]]==value,"Conflicting SourceRO current universe")
    source_union[value["path"]]=value
need(len(source_union)==SPEC["source_current_count"],"Actual SourceRO current universe includes Source44/P/seal2 with exact duplicate agreement")
enroll(source_union.values())
DATA_EXPECTED=json.loads('[{"bytes":590526,"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_unknown_relative_inventory_13299/diagnostic.json","sha256":"8bc7232449d5469cc621e6e34b26716c3d8ff65fc4a52e10d04b3977d9229313"},{"bytes":50849,"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_v7_relative_context_diagnostic_13298/diagnostic.json","sha256":"d680badfc6f11aefdbb88f673f3ac611766e87be7e3b2c5be7633ba886ff2a07"},{"bytes":4407,"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_v6_relative_context_diagnostic_13295/diagnostic.json","sha256":"e1a3efe660dab843d37c8d216df927927d79ec8e5186cf9249a742ec328812be"},{"bytes":9679,"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_receipt_parent_diagnostic_13290/diagnostic.json","sha256":"bd46f9afe0cd0b64003fa7d77c5d5ef2b66235942a16376ab4a15a674267567f"}]')
need(Q["software_fixture_DATA_receipts"]==DATA_EXPECTED and len(Q["software_fixture_DATA_metadata_original"])==4,"Only four exact diagnostic own DATA inputs")
data_rows=Q["software_fixture_DATA_metadata_original"]
need([x["path"]for x in data_rows]==[x["path"]for x in DATA_EXPECTED],"Exact DATA metadata order")
for value in data_rows:regular_record(value)
enroll(data_rows);allow_payload(data_rows)
# Root's explicit six historical Source-byte fixtures are separate from CODE44 and DATA4.
SOURCE_BYTE_SCOPE="SOFTWARE_SOURCE_PROVENANCE_BYTE_FIXTURES_NOT_EXECUTED_EXACT_SIX_OWN_BYTES_AND_THREE_CONTROL_JSON_NO_CHILD_IO"
PRODUCER_BYTE_SCOPE="EXACT_SIX_RAW_OPERATIONAL_TXT_OWN_BYTES_NOT_EXECUTED_NO_CHILD_IO_NOT_CODE44"
SOURCE_BYTE_PATHS=[
 str(S/"submissions/final_source_byte_identity_observer_from16651_16700_REV1_primary_claim/wrap_command.txt"),
 str(S/"submissions/final_source_finite_parent_views_plan_v4_REV1_audit_from16687_16744_primary_claim/wrap_command.txt"),
 str(S/"submissions/final_source_finite_worker_alias_plan_v4_audit_from16687_primary_claim/wrap_command.txt"),
 str(S/"submissions/final_source_supplemental_test_identity_observer_from16651_16762_primary_claim/wrap_command.txt"),
 str(S/"submissions/final_source_inventory_history_leaf1_rev1_software_primary_claim/wrap_command.txt"),
 str(S/"submissions/final_source_finite_worker_alias1_software_primary_claim/wrap_command.txt")]
SOURCE_BYTE_SIZES=[34064,55723,39218,47239,33599,12013]
SOURCE_BYTE_LEGACY_FP=[(33599,"86cea4a2b2a7893833f7741766206b683388c11dbca82ed253c47cb9991eb31e"),(12013,"9be7574dcf3e1406bd40027e0cb4d10555d9d6e9cac828a6ee944fa17cd591e6")]
source_byte_rows=Q["software_fixture_SOURCE_BYTE_metadata_original"]
provenance_control_rows=Q["software_fixture_SOURCE_PROVENANCE_control_metadata_original"]
need(Q["software_fixture_SOURCE_BYTE_scope"]==SOURCE_BYTE_SCOPE and type(source_byte_rows)is list and len(source_byte_rows)==6,"Closed six nonexecuted Source-byte fixture purpose")
need([v["path"]for v in source_byte_rows]==SOURCE_BYTE_PATHS and [v["bytes"]for v in source_byte_rows]==SOURCE_BYTE_SIZES,"Exact ordered six historical raw Source-byte inputs")
for value in source_byte_rows:
    regular_record(value);need(stage_map.get(value["path"])==value,"Six original Source-byte native must equal qualified Stage17516")
CAP_PATH=S/"runs/root_wrapper_shell_byte_preservation_16998/capture.json"
PRIOR_FAILED_TRO_NATIVE=json.loads("{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_late_publication17837_actual_failed_terminal_metadata_readonly_seal/receipt.json\",\"bytes\":9951510,\"inode\":144115643443095158,\"mtime_ns\":1792220050000000000,\"ctime_ns\":1792220050000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900}")
need(type(provenance_control_rows)is list and len(provenance_control_rows)==3 and provenance_control_rows[0]==SPEC["stage_terminal_metadata"] and provenance_control_rows[1]["path"]==str(CAP_PATH) and provenance_control_rows[1]["bytes"]==32138 and provenance_control_rows[2]==PRIOR_FAILED_TRO_NATIVE,"Exact ordered StageTRO/CAP/qualified failed17837 own JSON provenance controls")
for value in provenance_control_rows:
    regular_record(value);need(source_union.get(value["path"])==value,"Provenance own control native must equal original qualified custody")
enroll(source_byte_rows+provenance_control_rows);allow_payload(source_byte_rows+provenance_control_rows)
for value in source_byte_rows:own_bytes(value["path"],1024*1024).decode("utf-8","strict")
source_byte_receipts=[cpu_rec(value["path"])for value in source_byte_rows]
need([(r["bytes"],r["sha256"])for r in source_byte_receipts[4:]]==SOURCE_BYTE_LEGACY_FP,"Two actual qualified legacy wrapper FP anchors")
provenance_control_receipts=[cpu_rec(value["path"])for value in provenance_control_rows]
H=initial_control(BINDING["human_readonly_metadata"])
directory_control(BINDING["human_readonly_directory_metadata"])
need(type(SPEC["human_static_PASS_field"])is str and H["schema"]==SPEC["human_readonly_schema"] and H[SPEC["human_static_PASS_field"]]is True,"Actual Root+TWO whole Human metadata seal required")
need({x["path"]:x for x in H["protected_metadata_before"]}==source_union and H["protected_metadata_after"]==H["protected_metadata_before"],"HRO preserves exact Source17563 original universe")
need(H["Human_after"]==BINDING["self_human_metadata"],"Bound actual readonly executing Human")
need(H["source_proposal_metadata_after"]==[BINDING["self_proposal_metadata"],BINDING["self_proposal_directory_metadata"]],"Actual sealed unexecuted proposal file/directory")
need(H["conditional_CORE_metadata_before"]==core_rows and H["conditional_CORE_metadata_after"]==core_rows and H["Common_original_metadata_only_before"]==common_md and H["Common_original_metadata_only_after"]==common_md,"HRO original Core/Common scope")
for key in ("self_human_metadata","self_primary_metadata","self_proposal_metadata"):regular_record(BINDING[key])
directory_control(BINDING["self_proposal_directory_metadata"])
enroll([BINDING[k]for k in ("self_human_metadata","self_primary_metadata","self_proposal_metadata")]);allow_payload([BINDING[k]for k in ("self_human_metadata","self_primary_metadata","self_proposal_metadata")])
need(Path(BINDING["self_proposal_metadata"]["path"])==Path(SPEC["self_proposal_path"]),"Exact preserved unbound proposal Source path")
need(sorted(os.listdir(Path(BINDING["self_proposal_directory_metadata"]["path"])))==["software_control.py"],"Exact proposal one-file namespace")
human_raw=own_bytes(BINDING["self_human_metadata"]["path"],2*1024*1024)
human=human_raw.decode("utf-8");fence=chr(96)*3
need(human.count(fence+"python\n")==1 and human.count("\n"+fence+"\n")==1,"One actual Human Python body required")
body=human.split(fence+"python\n",1)[1].split("\n"+fence,1)[0]+"\n"
need(own_bytes(BINDING["self_primary_metadata"]["path"],2*1024*1024)==SPEC["shell_header"].encode()+body.encode()+b"PY\n","Actual precreated shell file exactly transports bound Human body")
control_paths=[SPEC[k]["path"]for k in ("stage_terminal_metadata","source_readonly_metadata")]+[BINDING[k]["path"]for k in ("human_readonly_metadata","self_human_metadata","self_primary_metadata","self_proposal_metadata")]
control_paths += [row["path"]for row in claim_files if row["path"]not in control_paths]
control_paths += [row["path"]for row in provenance_control_rows if row["path"]not in control_paths]
control_receipts=[cpu_rec(p)for p in control_paths]
source_receipts={key:[cpu_rec(x["path"])for x in sources[key]]for key in GROUPS}
refs=Q["qualified_API_and_Mapper_reference_receipts"]
need(len(refs)==29,"Qualified API15+Mapper14 reference pins")
for item,r in zip(refs,source_receipts["existing_API_dependencies"]+source_receipts["context_API_dependencies"]):
    need(item["path"]==r["path"] and r["bytes"]==item["qualified_reference_receipt"]["bytes"] and r["sha256"]==item["qualified_reference_receipt"]["sha256"],"Exact previously qualified API/Mapper full FP")
semantics=source_receipts["composer"][14]
reference=Q["qualified_semantics_reference_receipt"]
need(semantics["bytes"]==reference["bytes"]==344832 and semantics["sha256"]==reference["sha256"],"Byte-identical qualified Source pure semantics copy; no original G read")
data_receipts=[cpu_rec(x["path"])for x in data_rows]
need(data_receipts==DATA_EXPECTED,"Actual CPU four DATA own-byte pins")

def core_check():
    bypath={x["path"]:x for x in core_rows}
    logical=bypath[str(CORE_LOGICAL)];real=bypath[str(CORE_REAL)]
    need(stat.S_ISLNK(logical["mode"]) and logical["bytes"]==10 and logical["nlink"]==1,"Existing exact conditional Core logical link")
    need(stat.S_ISREG(real["mode"]) and real["bytes"]==CORE_BYTES and real["nlink"]==1,"Existing exact conditional Core real binary")
    need(native_metadata(CORE_LOGICAL)==logical and native_metadata(CORE_REAL)==real,"Original Core2 metadata")
    need(os.readlink(CORE_LOGICAL)=="python3.11","Existing conditional Core link target")
    h=hashlib.sha256();size=0
    with CORE_REAL.open("rb")as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):size+=len(block);h.update(block)
    need(size==CORE_BYTES and h.hexdigest()==CORE_SHA,"Original fixed CORE bytes/SHA")
    need(native_metadata(CORE_LOGICAL)==logical and native_metadata(CORE_REAL)==real,"Core2 drift after full byte authentication")
def native_union_sweep(final_shared=False):
    # True-last guard: ONLY lstat/type/native equality. No rec/JSON/payload/hash/resolve/readlink.
    for key,value in list(original.items())+list(created.items()):
        if key in shared_paths:
            if not final_shared:continue
            expected=shared_parent_after[key]
        else:expected=creation_events.get(key,value)
        if key==str(CORE_LOGICAL):
            need(stat.S_ISLNK(expected["mode"]) and expected["bytes"]==10 and expected["nlink"]==1,"Exact Core logical native-only scope")
        elif key==str(CORE_REAL):
            need(stat.S_ISREG(expected["mode"]) and expected["bytes"]==CORE_BYTES and expected["nlink"]==1,"Exact Core real native-only scope")
        elif key in worker_paths:
            need(key in stage_map and stage_map[key]==expected,"Same qualified exact worker metadata-only route")
        else:ordinary_path(key)
        need(native_metadata(Path(key))==expected,"TRUE_LAST original-native union changed: "+key)
    if final_shared:
        for key,value in shared_parent_after.items():
            need(native_metadata(Path(key))==value,"TRUE_LAST shared jobtime directory event changed")
directory_children=dict(Q["protected_directory_children"])
directory_children[str(CLAIM)]=sorted(claim_names)
for key,names in Q["source_directory_children"].items():
    if key in directory_children:need(sorted(directory_children[key])==sorted(names),"Conflicting fixed directory universes")
    directory_children[key]=sorted(names)
for md in (SPEC["stage_terminal_directory_metadata"],SPEC["source_readonly_directory_metadata"],BINDING["human_readonly_directory_metadata"]):
    key=md["path"]
    names=sorted(os.listdir(key))
    need(native_metadata(Path(key))==md,"Fixed own seal directory names/native")
    if key in directory_children:need(sorted(directory_children[key])==names,"Seal directory universe mismatch")
    directory_children[key]=names
directory_children[BINDING["self_proposal_directory_metadata"]["path"]]=["software_control.py"]
def input_check():
    for path,expected in zip(control_paths,control_receipts):need(cpu_rec(path)==expected,"Actual fixed operational control bytes changed")
    for key in GROUPS:
        need([cpu_rec(x["path"])for x in sources[key]]==source_receipts[key],"Whole reviewed Source44 changed")
    need([cpu_rec(x["path"])for x in data_rows]==data_receipts,"Four own DATA bytes changed")
    need([cpu_rec(x["path"])for x in source_byte_rows]==source_byte_receipts,"Six nonexecuted Source-byte fixture bytes changed")
    need([cpu_rec(x["path"])for x in provenance_control_rows]==provenance_control_receipts,"Three provenance own JSON control bytes changed")
    for key,names in directory_children.items():
        if key not in shared_paths:need(sorted(os.listdir(key))==sorted(names),"Fixed protected directory member set changed: "+key)
    core_check()
    native_union_sweep()
enroll_created(readiness_native_original+[readiness_directory_creation])
allow_payload(readiness_native_original)
creation_events[str(D)]=readiness_directory_original
need(stat.S_IMODE(readiness_directory_creation["mode"])==0o755 and stat.S_IMODE(readiness_directory_original["mode"])==0o555 and readiness_directory_original["inode"]==readiness_directory_creation["inode"],"Declared own readiness755-to555 event")
readiness_pins=[cpu_rec(x["path"])for x in readiness_native_original]
core_check()
input_check()
MODULE_TEST_FILES=(
 ("sealed_final_composer_tests","test_final_delivery_composer.py"),
 ("sealed_export_context_tests","test_github_export_context.py"),
 ("sealed_restore_index_tests","test_restored_index_scope.py"),
 ("sealed_finite_source_context_tests","test_finite_source_delivery_context.py"))
expected_ids=[]
expected_modules={}
for module_name,name in MODULE_TEST_FILES:
    # AST use happens ONLY inside this actual owned CPU after Source44/Core authentication.
    tree=ast.parse(own_bytes(OWN/name,4*1024*1024).decode("utf-8"),filename=str(OWN/name))
    classes={}
    for node in tree.body:
        if isinstance(node,ast.ClassDef):
            methods=sorted(x.name for x in node.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))and x.name.startswith("test_"))
            if methods:classes[node.name]=methods
    ids=[module_name+"."+cls+"."+name for cls in sorted(classes)for name in classes[cls]]
    need(len(ids)==len(set(ids)),"Unique declared class/method test IDs required")
    expected_modules[module_name]=ids;expected_ids.extend(ids)
need(len(expected_ids)==len(set(expected_ids))==SPEC["expected_test_count"],"Actual stopped direct definitions/count; real loader must confirm masks/inheritance")
loader=unittest.defaultTestLoader
loader_had_instance="loadTestsFromModule"in loader.__dict__
loader_instance_original=loader.__dict__.get("loadTestsFromModule")
loader_original=loader.loadTestsFromModule
loaded_modules=[]
def flatten_suite(suite):
    result=[]
    for item in suite:
        if isinstance(item,unittest.TestSuite):result.extend(flatten_suite(item))
        else:result.append(item.id())
    return result
def authentic_loader(module,*args,**kwargs):
    suite=loader_original(module,*args,**kwargs)
    name=module.__name__
    need(len(loaded_modules)<4 and name==MODULE_TEST_FILES[len(loaded_modules)][0],"Exact original bootstrap test module order")
    ids=flatten_suite(suite)
    need(ids==expected_modules[name],"Actual unchanged default loader IDs must equal complete declared names/classes/method order")
    loaded_modules.append(dict(module=name,actual_loader_ids=ids))
    return suite
class RootTee:
    def __init__(self,underlying):
        self.underlying=underlying;self.capture=io.StringIO();self.count=0
    def write(self,value):
        self.count+=len(value);need(self.count<=20*1024*1024,"Bounded own software stdout")
        self.underlying.write(value);self.capture.write(value);return len(value)
    def flush(self):self.underlying.flush()
OUT=S/"runs"/(SPEC["out_namespace"]+jid)
FROZEN=S/"frozen"/(SPEC["frozen_namespace"]+jid)
CODE=FROZEN/"code";MAPPER=FROZEN/"context_mapper_v4"
TMP=S/"tmp"/(SPEC["tmp_namespace"]+jid)
PD=S/"submissions"/(SPEC["proof_namespace"]+jid)
for path in (OUT,FROZEN,TMP,PD):need(not path.exists() and not path.is_symlink(),"Exclusive absent current software output namespace")
os.umask(0o002)
TMP.mkdir(mode=0o775);PD.mkdir(mode=0o755)
enroll_created([native_metadata(TMP),native_metadata(PD)])
os.environ["TMPDIR"]=str(TMP)
argv_object=sys.argv;argv_before=list(sys.argv)
path_object=sys.path;path_before=list(sys.path)
stdout_before=sys.stdout
tee=RootTee(stdout_before)
def durable_existing(p):
    p=ordinary_path(p);before=current_matches(p)
    need(stat.S_ISREG(before["mode"])and before["nlink"]==1 and not(before["mode"]&0o222),"Existing readonly own file durable readback")
    fd=os.open(str(p),os.O_RDONLY|os.O_NOFOLLOW)
    try:
        x=os.fstat(fd)
        need(x.st_ino==before["inode"]and x.st_dev==before["dev"]and x.st_mode==before["mode"]and x.st_nlink==1,"Exact own file fd binding")
        os.fsync(fd)
    finally:os.close(fd)
    need(native_metadata(p)==before,"Own file metadata changed during fsync")
def durable_directory(p):
    p=ordinary_path(p);before=current_matches(p);need(stat.S_ISDIR(before["mode"]),"Own nonlink directory fsync")
    fd=os.open(str(p),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)
    need(native_metadata(p)==before,"Own directory metadata changed during fsync")
shared_parent_after={};shared_parent_events=[]
def final_parent_events():
    additions={str(S/"submissions"):{D.name,PD.name},str(S/"runs"):{OUT.name},str(S/"frozen"):{FROZEN.name},str(S/"tmp"):{TMP.name}}
    result=[]
    for key,before in operational_parent_before.items():
        path=Path(key);after=native_metadata(path);names=sorted(os.listdir(path))
        need(set(names)==set(operational_parent_names[key])|additions[key],"Only exact current own persistent operational namespace additions")
        need(all(after[k]==before[k]for k in ("inode","dev","uid","gid","mode")),"Shared parent identity/permissions preserved")
        need(after["nlink"]==before["nlink"]+len(additions[key]),"Exact created immediate directory-link additions")
        if key in shared_parent_after:need(shared_parent_after[key]==after,"Shared directory event must not refresh")
        shared_parent_after[key]=after
        result.append(dict(before=before,after=after,before_children=operational_parent_names[key],after_children=names,exact_created_children=sorted(additions[key]),transient_fixture_directory_history_not_global_immutable=True))
    shared_parent_events[:]=result
def persist_root(name,obj):
    path=PD/name;raw=(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode("utf-8")
    fd=os.open(str(path),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o664)
    try:
        with os.fdopen(fd,"wb",closefd=False)as stream:stream.write(raw);stream.flush();os.fsync(fd)
        os.fchmod(fd,0o444);os.fsync(fd)
    finally:os.close(fd)
    md=native_metadata(path);enroll_created([md]);allow_payload([md])
    need(own_bytes(path,len(raw)+1)==raw and own_json(path)==obj,"Root own proof full JSON/byte reread")
    return path
output_paths=[];output_pins=[];output_names={};rootproof=None
try:
    sys.argv=[str(OWN/"composer_bootstrap.py")]
    sys.stdout=tee
    loader.loadTestsFromModule=authentic_loader
    try:
        runpy.run_path(str(OWN/"composer_bootstrap.py"),run_name="__main__")
    finally:
        sys.stdout=stdout_before
        if loader_had_instance:loader.loadTestsFromModule=loader_instance_original
        else:del loader.__dict__["loadTestsFromModule"]
        sys.argv=argv_object;argv_object[:]=argv_before
        sys.path=path_object;path_object[:]=path_before
    need([x["module"]for x in loaded_modules]==[x[0]for x in MODULE_TEST_FILES],"All four original test modules executed once")
    need(len([y for x in loaded_modules for y in x["actual_loader_ids"]])==SPEC["expected_test_count"],"Complete actual producer suite loader denominator")
    output_paths=[OUT/"contracts.txt",OUT/"contracts.json",OUT/"acceptance.json"]+[CODE/n for n in OWN_NAMES]+[MAPPER/n for n in MAPPER_NAMES]
    need(len(output_paths)==32 and len(set(output_paths))==32,"Actual bootstrap successful output32 closure")
    # Enrol complete current file/directory native records BEFORE first Root output read/hash.
    own_rows=[native_metadata(p)for p in output_paths]
    own_dirs=[native_metadata(p)for p in (OUT,FROZEN,CODE,MAPPER)]
    for value in own_rows:regular_record(value)
    enroll_created(own_rows+own_dirs);allow_payload(own_rows)
    output_names={str(OUT):["acceptance.json","contracts.json","contracts.txt"],str(FROZEN):["code","context_mapper_v4"],str(CODE):sorted(OWN_NAMES),str(MAPPER):sorted(MAPPER_NAMES)}
    for path,names in output_names.items():
        need(sorted(os.listdir(path))==names,"Exact own bootstrap output directory universe")
    need(sorted(os.listdir(TMP))==[],"Owned software TMP must be empty after suite")
    tmp_before=created[str(TMP)];tmp_after=native_metadata(TMP)
    need(all(tmp_after[k]==tmp_before[k]for k in ("inode","dev","uid","gid","mode","nlink")),"Owned TMP identity/mode preserved despite test lifecycle")
    creation_events[str(TMP)]=tmp_after
    pd_after=native_metadata(PD)
    need(pd_after==created[str(PD)],"Root proof directory empty before first Root output")
    for p in output_paths:durable_existing(p)
    for p in (OUT,FROZEN,CODE,MAPPER):durable_directory(p)
    output_pins=[cpu_rec(p)for p in output_paths]
    contract_log=own_bytes(OUT/"contracts.txt",8*1024*1024).decode("utf-8")
    actual_ids=[]
    for line in contract_log.splitlines():
        if line.startswith("test_"):
            match=re.fullmatch(r"(test_[A-Za-z0-9_]+) \(([A-Za-z0-9_.]+)\) \.\.\. ok",line)
            need(match is not None,"Every actual test must have one physical named OK line; no FAIL/ERROR/skip/docstring split")
            need(match.group(2).endswith("."+match.group(1)),"Actual unittest full ID and method label must agree")
            actual_ids.append(match.group(2))
    need(actual_ids==expected_ids and len(actual_ids)==len(set(actual_ids))==SPEC["expected_test_count"],"Whole named class/module/method order exactly equals actual original loader")
    need(re.search(r"^Ran "+str(SPEC["expected_test_count"])+r" tests in [0-9.]+s$",contract_log,re.M)is not None and contract_log.rstrip().endswith("OK"),"Complete actual suite summary and OK")
    need(not re.search(r"^(FAILED|ERROR:|FAIL:)|\.\.\. skipped",contract_log,re.M),"Zero failure/error/skip mandatory")
    CT=own_json(OUT/"contracts.json");A=own_json(OUT/"acceptance.json")
    need(CT["status"]=="PASS"and CT["tests_run"]==SPEC["expected_test_count"]and CT["errors"]==0 and CT["failures"]==0 and CT["all_owned_and_context_python_compile_PASS"]is True and CT["all_launchers_bash_syntax_PASS"]is True,"Actual software contracts/compiler/bash denominator")
    need(CT["log"]==output_pins[0],"Actual whole contracts log pin")
    sealed=sys.modules.get("final_delivery_composer")
    need(sealed is sys.modules.get("sealed_final_composer")and Path(sealed.__file__)==CODE/"final_delivery_composer.py","Actual same frozen producer module; no alternate import")
    need(tuple(sealed.FILES)==OWN_NAMES and sealed.SOFTWARE_TESTS==SPEC["expected_test_count"],"Current qualified OWN/count/profile")
    need(A["schema"]==SPEC["producer_acceptance_schema"]and A["status"]==SPEC["producer_software_status"]==sealed.SOFTWARE_STATUS and A["actual_CPU_job_id"]==jid,"Actual software-only acceptance")
    need(A["contracts"]==output_pins[1] and A["entry"]==output_pins[3] and A["CPU_launcher"]==output_pins[6],"Actual software acceptance own output pins")
    frozen_source={"composer":output_pins[3:18],"existing_API_dependencies":source_receipts["existing_API_dependencies"],"context_API_dependencies":output_pins[18:32]}
    need(A["source"]==frozen_source and CT["tested_source"]==frozen_source,"Exact frozen three-group Source44 closure")
    for old,new in zip(source_receipts["composer"]+source_receipts["context_API_dependencies"],output_pins[3:18]+output_pins[18:32]):
        need((old["bytes"],old["sha256"])==(new["bytes"],new["sha256"]),"Original/frozen Source byte identity")
    need(A["original_executing_sources"]==source_receipts["composer"] and A["original_source_entry"]==source_receipts["composer"][2]and A["original_owned_pre_and_post_byte_readback_PASS"]is True,"Actual original reviewed OWN15 execution binding")
    need(A["scientific_scope"]=="SOFTWARE_FIXTURES_ONLY"and A["production_science_accepted"]is False and A["archive_or_restore_complete"]is False and A["ACTIVE_changed"]is False and A["no_GPU_submission"]is True,"Software fixture evidence only")
    for obj in (A,CT):
        need(obj["software_fixture_inputs"]==data_receipts and obj["software_fixture_input_native_before"]==data_rows,"Exact four DATA own-byte/native fixture scope")
    need(A["software_fixture_input_native_after"]==data_rows and A["software_fixture_scope"]=="EXACT_FOUR_DIAGNOSTIC_DOCUMENT_OWN_BYTES_DATA_NO_CHILD_TARGET_IO","No diagnostic child target permissions")
    for obj in (A,CT):
        need(obj["software_operational_source_provenance_byte_fixture_receipts"]==source_byte_receipts and obj["software_operational_source_provenance_byte_fixture_metadata"]==source_byte_rows,"Exact six Source-byte own tuples/native remain separate from CODE44")
        need(obj["software_operational_control_fixture_receipts"]==provenance_control_receipts and obj["software_operational_fixture_scope"]==PRODUCER_BYTE_SCOPE,"Exact three own JSON controls/no Source-byte execution or child IO")
    allocation=sealed.cpu()
    need(A["allocation"]["job_id"]==jid and allocation["job_id"]==jid and A["allocation"]["allocated_gpus"]==0 and allocation["allocated_gpus"]==0,"Original fresh current producer CPU guard")
    printed=[line for line in tee.capture.getvalue().splitlines()if line.strip()]
    need(printed and parse_json(printed[-1].encode("utf-8"))==output_pins[2],"Actual bootstrap final stdout A receipt; intermediate fixtures not acceptance")
    input_check()
    for p,pin in zip(output_paths,output_pins):need(cpu_rec(p)==pin,"Output32 whole byte repeat")
    need(own_json(OUT/"contracts.json")==CT and own_json(OUT/"acceptance.json")==A,"Complete actual output object repeat")
    input_check()
    final_parent_events()
    proof_obj=dict(schema="root-final-composer-v7-software-execution-control.v1",
        status="ACTUAL_SOFTWARE_CONTRACTS_FULL_READBACK_NOT_SCIENCE_SOURCE_OR_INDEX_COMPATIBILITY",
        actual_job_id=jid,actual_readiness=cpu_rec(D/"readiness.json"),actual_fresh_allocation=allocation,
        actual_producer_acceptance=output_pins[2],actual_contracts=output_pins[1],actual_contract_log=output_pins[0],
        actual_named_loader_ids=actual_ids,actual_test_count=SPEC["expected_test_count"],zero_failure_error_skip=True,
        actual_source_groups_original=source_receipts,actual_frozen_source_groups=frozen_source,
        actual_fixture_DATA_inputs=data_receipts,original_fixture_DATA_native=data_rows,
        actual_fixture_SOURCE_BYTE_inputs=source_byte_receipts,original_fixture_SOURCE_BYTE_native=source_byte_rows,
        actual_fixture_SOURCE_PROVENANCE_control_inputs=provenance_control_receipts,
        Source_BYTE_fixture_scope=SOURCE_BYTE_SCOPE,Source_BYTE_never_compiled_imported_executed_or_promoted_to_CODE44=True,
        actual_fixed_control_own_CPU_tuples=control_receipts,
        actual_closed_primary_request=REQUEST,actual_submit_receipt=SUBMIT,
        primary_claim_metadata_original=claim_md,primary_files_metadata_original=claim_files,
        actual_primary_readonly_wait=claim_observations,
        exact_Source44_original_native=source_rows,exact_Output32_original_native=own_rows,
        exact_output_directory_native=own_dirs,exact_output_directory_children=output_names,
        protected_SourceRO_universe_count=len(source_union),exact_HRO_metadata=BINDING["human_readonly_metadata"],
        original_metadata_before_all_Root_IO=list(original.values()),
        own_creation_original_metadata=list(created.values()),
        explicit_own_creation_events=[dict(before=created[k],after=v)for k,v in creation_events.items()if k in created],
        exact_shared_parent_jobtime_events=shared_parent_events,
        compiler_and_bash_are_actual_bootstrap_only=True,
        Root_readback_never_opens_installed_Common_worker_or_science=True,
        Source_or_INDEX_compatibility_accepted=False,package_restore_accepted=False,
        production_science_accepted=False,Git_changed=False,published=False,ACTIVE_changed=False,
        actual_final_qualification_requires_Root_two_content_and_fresh_terminal_RO=True)
    rootproof=persist_root("execution_control.json",proof_obj)
    pd_before=created[str(PD)];PD.chmod(0o555);pd_final=native_metadata(PD)
    need(all(pd_final[k]==pd_before[k]for k in ("inode","dev","uid","gid"))and stat.S_IMODE(pd_final["mode"])==0o555,"Declared own Root proof directory seal event")
    creation_events[str(PD)]=pd_final;durable_directory(PD)
    proof_pin=cpu_rec(rootproof)
    need(own_json(rootproof)==proof_obj,"Root proof full final JSON repeat")
    input_check()
    for p,pin in zip(output_paths,output_pins):need(cpu_rec(p)==pin,"Actual output whole bytes after Root proof")
    for row,pin in zip(readiness_native_original,readiness_pins):need(cpu_rec(row["path"])==pin,"Actual raw readiness complete byte repeat")
    need(own_json(OUT/"acceptance.json")==A and own_json(OUT/"contracts.json")==CT,"Actual final object repeats after Root proof")
    input_check()
    need(cpu_rec(rootproof)==proof_pin,"Final Root proof complete own bytes")
    need(sorted(os.listdir(PD))==["execution_control.json"],"Exclusive actual Root proof output")
    for path,names in output_names.items():need(sorted(os.listdir(path))==names,"Final output32 namespace unchanged")
    need(set(os.listdir(D))==readiness_names_original and not os.listdir(TMP),"Final readiness and emptyTMP namespaces")
    # Last native-only sweep follows ALL JSON/payload hashes/Core calls without creating/refreshing baselines.
    native_union_sweep(final_shared=True)
    print(json.dumps(dict(status=proof_obj["status"],actual_job_id=jid,
        actual_software_acceptance=output_pins[2],actual_Root_execution_control=proof_pin,
        actual_test_count=SPEC["expected_test_count"],actual_Source_groups=44,actual_output_files=32,
        TRUE_LAST_NO_JSON_NO_HASH_ORIGINAL_NATIVE_UNION_PASS=True,
        software_only=True,Source_or_INDEX_compatibility_accepted=False,
        actual_Root_proof_directory_after_creation_event=pd_final,
        production_science_accepted=False,Git_changed=False,published=False,ACTIVE_changed=False)),flush=True)
except BaseException as source_exception:
    # Preserve the original producer/control exception; diagnostic failures cannot replace it.
    sys.stdout=stdout_before
    if loader_had_instance:loader.loadTestsFromModule=loader_instance_original
    elif "loadTestsFromModule"in loader.__dict__:del loader.__dict__["loadTestsFromModule"]
    sys.argv=argv_object;argv_object[:]=argv_before
    sys.path=path_object;path_object[:]=path_before
    outcomes=[]
    for name,operation in (("fixed_inputs",input_check),("original_native",native_union_sweep)):
        try:operation();outcomes.append(dict(check=name,PASS=True))
        except BaseException as error:outcomes.append(dict(check=name,PASS=False,error_type=type(error).__name__,error=str(error)[:4096]))
    try:
        partial=[]
        for path in [OUT,FROZEN,CODE,MAPPER,TMP,PD]:
            if path.exists()or path.is_symlink():partial.append(native_metadata(path))
        for path in output_paths:
            if path.exists()or path.is_symlink():partial.append(native_metadata(path))
        failure=dict(schema="root-final-composer-v7-software-failure-control.v1",status="UNQUALIFIED_PARTIAL_SOFTWARE_OUTPUTS_PRESERVED_NO_REPLAY",
            actual_job_id=jid,error_type=type(source_exception).__name__,error=str(source_exception)[:8192],
            fixed_guard_outcomes=outcomes,partial_owned_metadata=partial,
            actual_readiness_path=str(D/"readiness.json"),loaded_original_modules=loaded_modules,
            Source_or_INDEX_compatibility_accepted=False,production_science_accepted=False,Git_changed=False,published=False,ACTIVE_changed=False)
        if not(PD/"failure.json").exists():persist_root("failure.json",failure)
    except BaseException as diagnostic_error:
        print(json.dumps(dict(status="UNQUALIFIED_SOFTWARE_FAILURE_CONTROL_INCOMPLETE",actual_job_id=jid,
            original_error_type=type(source_exception).__name__,diagnostic_error_type=type(diagnostic_error).__name__)),file=sys.stderr,flush=True)
    raise
PY
