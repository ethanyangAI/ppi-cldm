#!/bin/bash
set -euo pipefail
cd /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery
unset PYTHONPATH
export CUDA_VISIBLE_DEVICES=""
export JAX_PLATFORMS=cpu
export PYTHONNOUSERSITE=1
export PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export TMPDIR="/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/source_plan_v13_stage_${SLURM_JOB_ID}"
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
# These three existing operational parents are metadata/name-only snapshots.
def initial_md(p):
    x=p.lstat();return dict(path=str(p),bytes=x.st_size,inode=x.st_ino,mtime_ns=x.st_mtime_ns,ctime_ns=x.st_ctime_ns,mode=x.st_mode,dev=x.st_dev,nlink=x.st_nlink,uid=x.st_uid,gid=x.st_gid)
operational_parent_before={}
operational_parent_names={}
for parent in (S/"submissions",S/"runs",S/"tmp"):
    before=initial_md(parent)
    if not stat.S_ISDIR(before["mode"]) or parent.is_symlink():raise SystemExit("Existing nonlink operational parent required")
    names=sorted(os.listdir(parent))
    if initial_md(parent)!=before:raise SystemExit("Operational parent changed during initial names read")
    operational_parent_before[str(parent)]=before
    operational_parent_names[str(parent)]=names
D = S / "submissions" / ("source_plan_v13_stage_current_sacct_readiness_" + jid)
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
    if "node" in values and (not re.fullmatch("[0-9]+", values["node"]) or int(values["node"]) != 1):
        raise ValueError("Actual allocated Node1 required when present")
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
    required = {"JobId": jid, "JobName": "test9_source_plan_v13_stage_cpu", "Account": "u21111210118", "QOS": "normal", "WorkDir": str(S), "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumNodes": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-source-v13-stage-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_SOURCE_V13_STAGE_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "stage_entered": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_SOURCE_V13_STAGE_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_SOURCE_V13_STAGE_NOT_EXECUTED"
obj = {"schema": "root-current-owned-source-v13-stage-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
       "current_scontrol_observation": ctl_saved, "current_scontrol_TRES": current_tres,
       "all_present_scontrol_TRES_fields_CPU1_GPU0": current_tres_fields, "attempts": attempts,
       "selected_actual_attempt": selected, "maximum_attempts": 30, "maximum_wait_seconds": 60,
       "environment": {"TZ": "UTC", "SLURM_TIME_FORMAT": "standard", **expected_env},
       "requested_GPUs": 0, "current_allocation_only_no_historical_GPU_inference": True,
       "no_source_or_request_hashes_or_imports_or_tests_by_wait": True,
       "unchanged_library_cpu_guard_will_freshly_requery": True, "actual_queries_not_proxy_or_synthesized_replies": True,
       "stage_entered": False,
       "additional_pin_or_source_audit_stage_Git_ACTIVE_acceptance": False}
persist("readiness.json", (json.dumps(obj, indent=2) + "\n").encode()); D.chmod(0o555)
readiness_directory_original=native_metadata(D)
readiness_names_original={Path(x["path"]).name for x in readiness_native_original}
if selected is None:
    raise SystemExit(72)
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "stage_next_not_acceptance": True}), flush=True)

# RAM SOURCE PROPOSAL ONLY. Root binds exactly this one finite data object.
# Future HRO is metadata-only; unknown own SHAs are captured on this actual CPU.
import hashlib, runpy
R=Path("/lustre/users/u21111210118/projects/test9")
CORE=R/"env/core/bin/python";REAL=CORE.with_name("python3.11")
I_PATH=S/"runs/final_source_plan_v13_production_17808/source_inclusion_final.json"
I_SHA="72282c88ae0483c5f42a1050e900eb2b015de246b589e414922d81ef4d35018d"
T_PATH=S/"submissions/final_source_plan_v13_production17808_actual_terminal_metadata_readonly_seal/receipt.json"
HUMAN=S/"handoffs/ROOT_FIXED_PLAN_V13_SOURCE_STAGE_FROM17808_20261016.md"
PRIMARY=S/"submissions/final_source_v13_stage_from17808_primary_claim/precreated_stage.sh"
HRO=S/"submissions/root_plan_v13_stage_human_metadata_readonly_seal/receipt.json"
OUT=S/"runs"/("final_source_plan_v13_stage_"+jid)
PD=S/"submissions"/("source_plan_v13_stage_"+jid+"_root_execution_control")
TMP=S/"tmp"/("source_plan_v13_stage_"+jid)
SPEC=json.loads("{\"source_terminal_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_production17808_actual_terminal_metadata_readonly_seal/receipt.json\",\"bytes\":16998922,\"inode\":144115643443094623,\"mtime_ns\":1792177305000000000,\"ctime_ns\":1792177305000000000,\"mode\":33060,\"dev\":1119461688,\"nlink\":1,\"uid\":6263900,\"gid\":6263900},\"source_terminal_directory_metadata\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v13_production17808_actual_terminal_metadata_readonly_seal\",\"bytes\":4096,\"inode\":144115643443094620,\"mtime_ns\":1792177305000000000,\"ctime_ns\":1792177305000000000,\"mode\":16749,\"dev\":1119461688,\"nlink\":2,\"uid\":6263900,\"gid\":6263900},\"shell_header\":\"#!/bin/bash\\nset -euo pipefail\\ncd /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery\\nunset PYTHONPATH\\nexport CUDA_VISIBLE_DEVICES=\\\"\\\"\\nexport JAX_PLATFORMS=cpu\\nexport PYTHONNOUSERSITE=1\\nexport PYTHONDONTWRITEBYTECODE=1\\nexport OPENBLAS_NUM_THREADS=1\\nexport OMP_NUM_THREADS=1\\nexport MKL_NUM_THREADS=1\\nexport TMPDIR=\\\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/tmp/source_plan_v13_stage_${SLURM_JOB_ID}\\\"\\nexec /lustre/users/u21111210118/projects/test9/env/core/bin/python -B - <<'PY'\\n\",\"extra_control_paths\":[]}")
SPEC_KEYS={"source_terminal_metadata","source_terminal_directory_metadata","shell_header","extra_control_paths"}
META={"path","bytes","inode","mtime_ns","ctime_ns","mode","dev","nlink","uid","gid"}
PAIR_KEYS=(("vendor_example_opaque_leaf_proof","vendor_example_opaque_aliases"),
 ("finite_worker_control_proof","finite_worker_control_aliases"),
 ("inventory_history_opaque_leaf_proof","inventory_history_opaque_aliases"),
 ("archive_parent_history_opaque_leaf_proof","archive_parent_history_opaque_aliases"),
 ("relative_diagnostic_history_opaque_leaf_proof","relative_diagnostic_history_opaque_aliases"),
 ("parent_diagnostic_history_opaque_leaf_proof","parent_diagnostic_history_opaque_aliases"))
def need(v,msg):
    if not v:raise ValueError(msg)
def md(p):return native_metadata(Path(p))
def native_row(x):
    need(type(x)is dict and set(x)==META and type(x["path"])is str and all(type(x[k])is int and x[k]>=0 for k in META-{"path"}),"Exact native metadata row required")
    return x
def under(p,root):
    try:p.relative_to(root);return True
    except ValueError:return False
def ordinary(p):
    p=Path(p);need(p.is_absolute()and under(p,R)and ".."not in p.parts,"Exact ordinary authority path required")
    for a in [p]+list(p.parents):
        if a==R.parent:break
        if os.path.lexists(str(a)):need(not stat.S_ISLNK(a.lstat().st_mode),"No ordinary symlink ancestry")
    return p
original={};creation={};directory_events={};creation_directory_events={};worker_metadata_paths=set()
common_path=None
def enrol(rows,table=original):
    for row in rows:
        native_row(row);p=row["path"]
        need(p not in table or table[p]==row,"Conflicting original/creation native metadata")
        if table is creation:need(p not in original,"New output conflicts with original input")
        table[p]=dict(row)
def metadata_path(path):
    if path==str(CORE):
        x=md(CORE);need(stat.S_ISLNK(x["mode"])and x["bytes"]==10 and x["nlink"]==1,"Existing fixed Core logical type");return CORE
    if path==str(REAL):
        x=md(REAL);need(stat.S_ISREG(x["mode"])and x["bytes"]==25916456 and x["nlink"]==1,"Existing fixed Core real type");return REAL
    if path==common_path or path in worker_metadata_paths:return Path(path)
    return ordinary(path)
def native_sweep():
    # TRUE-LAST native-only; no payload, JSON, hash, rec, resolve or readlink.
    for path,before in original.items():
        expected=directory_events[path]["after"]if path in directory_events else before
        need(md(metadata_path(path))==expected,"Original native metadata changed outside declared directory event")
    for path,before in creation.items():
        expected=creation_directory_events[path]["after"]if path in creation_directory_events else before
        need(md(ordinary(path))==expected,"Created output native metadata changed outside its declared own-write event")
def capture_file(p):
    p=ordinary(p);x=md(p)
    need(stat.S_ISREG(x["mode"])and x["nlink"]==1,"Single-link regular owned output required")
    enrol([x],creation);return x
def fp(r):return r["bytes"],r["sha256"]
def receipt(r):
    need(type(r)is dict and set(r)=={"path","bytes","sha256"}and type(r["path"])is str and type(r["bytes"])is int and r["bytes"]>=0 and type(r["sha256"])is str and re.fullmatch("[0-9a-f]{64}",r["sha256"]),"Complete scalar receipt required")
    return r
def cpu_rec(p,cap=None):
    p=ordinary(p);need(str(p)!=common_path and str(p)not in worker_metadata_paths,"No original Common/worker payload IO")
    x=md(p);need(stat.S_ISREG(x["mode"])and x["nlink"]==1,"Exact nonlink regular payload input required")
    need(cap is None or x["bytes"]<=cap,"Explicit own-input byte cap exceeded")
    h=hashlib.sha256();n=0
    with p.open("rb")as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b);n+=len(b)
    need(md(p)==x and n==x["bytes"],"Payload native/size changed during CPU read")
    return dict(path=str(p),bytes=n,sha256=h.hexdigest())
def check(r):
    receipt(r);need(r["path"]in original or r["path"]in creation,"Original native must precede first payload hash")
    need(cpu_rec(r["path"])==r,"Actual CPU fulltuple mismatch");return r
def strict_pairs(items):
    out={}
    for k,v in items:need(k not in out,"Duplicate control JSON key");out[k]=v
    return out
def strict_json(raw):
    return json.loads(raw.decode("utf-8"),object_pairs_hook=strict_pairs,parse_constant=lambda v:(_ for _ in()).throw(ValueError("Nonfinite JSON")))
def load_control(r,cap):
    check(r);p=ordinary(r["path"]);need(r["bytes"]<=cap,"Bounded own control required")
    before=md(p);raw=p.read_bytes();need(md(p)==before and len(raw)==r["bytes"],"Control changed during last JSON read")
    v=strict_json(raw);need(md(p)==before,"Control native changed after JSON parse");return v
def capture_json(p,cap):
    p=ordinary(p);before=md(p);need(stat.S_ISREG(before["mode"])and before["nlink"]==1 and before["bytes"]<=cap,"Bounded new readonly control required")
    raw=p.read_bytes();need(md(p)==before,"New control changed during first JSON read")
    value=strict_json(raw);need(md(p)==before,"New control changed after JSON parse");return value,raw
def fsync_dir(p):
    fd=os.open(str(p),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)
def directory_state(p):
    p=ordinary(p);x=md(p);need(stat.S_ISDIR(x["mode"]),"Exact nonlink directory required")
    names=sorted(os.listdir(p));need(md(p)==x,"Directory changed while enumerating exact finite names");return x,names
def directory_event(path,before,names_before,added_names,new_subdirs):
    after,names_after=directory_state(path)
    need(set(names_after)==set(names_before)|set(added_names)and not(set(names_before)&set(added_names)),"Directory children differ from exact planned additions")
    for k in ("path","inode","mode","dev","uid","gid"):need(after[k]==before[k],"Existing directory identity/permissions changed")
    need(after["nlink"]==before["nlink"]+new_subdirs,"Existing directory link count inconsistent with exact child directories")
    if not added_names:need(after==before,"Unmodified existing directory native drift")
    event=dict(before=before,after=after,children_before=names_before,children_after=names_after,exact_added_children=sorted(added_names),exact_added_subdirectories=new_subdirs)
    old=directory_events.get(path);need(old is None or old==event,"Directory event cannot refresh an earlier original")
    directory_events[path]=event;return event
def core_check():
    need(md(CORE)==core_original[0]and md(REAL)==core_original[1],"Original Core native drift")
    need(os.readlink(str(CORE))=="python3.11","Exact existing conditional Core link binding")
    # Exact fixed Core exception only; it is never an ordinary Source/worker route.
    h=hashlib.sha256();n=0
    with REAL.open("rb")as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b);n+=len(b)
    need(n==25916456 and h.hexdigest()=="76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a","Exact qualified Core bytes required")
    need(md(CORE)==core_original[0]and md(REAL)==core_original[1],"Core changed during full byte read")
need(type(SPEC)is dict and set(SPEC)==SPEC_KEYS,"Closed actual stage SPEC required")
need(Path(SPEC["source_terminal_metadata"]["path"])==T_PATH and Path(SPEC["source_terminal_directory_metadata"]["path"])==T_PATH.parent,"Literal qualified Source terminal binding")
need(md(T_PATH)==native_row(SPEC["source_terminal_metadata"])and md(T_PATH.parent)==native_row(SPEC["source_terminal_directory_metadata"]),"Qualified Source terminal native mismatch")
need(stat.S_IMODE(md(T_PATH)["mode"])==0o444 and md(T_PATH)["nlink"]==1 and stat.S_IMODE(md(T_PATH.parent)["mode"])==0o555,"Exact Source terminal readonly binding")
# Before the first JSON/hash of each new HRO control, capture its ORIGINAL native.
hro_md=md(ordinary(HRO));hro_d=md(ordinary(HRO.parent))
need(stat.S_ISREG(hro_md["mode"])and stat.S_IMODE(hro_md["mode"])==0o444 and hro_md["nlink"]==1,"Actual stage HRO readonly single file")
need(stat.S_ISDIR(hro_d["mode"])and stat.S_IMODE(hro_d["mode"])==0o555 and sorted(os.listdir(HRO.parent))==["receipt.json"],"Exact one-file stage HRO directory")
enrol([SPEC["source_terminal_metadata"],SPEC["source_terminal_directory_metadata"],hro_md,hro_d])
T,t_raw=capture_json(T_PATH,20*1024*1024)
need(T["schema"]=="root-plan-v13-source-production17808-terminal-metadata-readonly-seal.v1"and T["status"]=="ACTUAL_SOURCE17808_COMPLETED_CONTENT_AND_READONLY_METADATA_PASS_NOT_STAGED_NOT_PUBLISHED"and T["Root_and_two_whole_actual_content_PASS"]is True,"Qualified Source17808 terminal identity")
need(T["protected_inputs_before"]==T["protected_inputs_after"]and T["dynamic_original_metadata_before"]==T["dynamic_original_metadata_after"],"Original Source protected/dynamic native tables changed")
base_rows=T["protected_inputs_after"]+T["dynamic_original_metadata_after"]+T["owned_metadata_after"]+[T["initial_incomplete_preflight_preserved"]["receipt"],T["initial_incomplete_preflight_preserved"]["directory"],T["qualified_preflight_metadata"],T["qualified_preflight_directory_metadata"]]+T["fresh_terminal_raw_metadata"]+[SPEC["source_terminal_metadata"],SPEC["source_terminal_directory_metadata"]]
base_map={}
for row in base_rows:
    native_row(row);need(row["path"]not in base_map or base_map[row["path"]]==row,"Conflicting Source terminal original tables");base_map[row["path"]]=row
need(len(base_map)==15813 and T["counts"]["actual_current_union_after_TRO"]==15813,"Exact qualified Source original universe")
worker_metadata_paths=set(T["worker_exact_metadata_only_routes"])
need(len(worker_metadata_paths)==len(T["worker_exact_metadata_only_routes"])and worker_metadata_paths<=set(base_map),"Finite authenticated worker native-only path set")
core_original=T["conditional_CORE_metadata_after"]
need(core_original==T["conditional_CORE_metadata_before"]and len(core_original)==2 and [x["path"]for x in core_original]==[str(CORE),str(REAL)],"Original qualified Core2 table")
common=T["Common_original_metadata_only_after"];need(common==T["Common_original_metadata_only_before"],"Original Common metadata-only binding")
common_path=common["path"]
enrol(base_map.values());enrol(core_original);enrol([common])
hr,hr_raw=capture_json(HRO,20*1024*1024)
need(hr["schema"]=="root-plan-v13-stage-human-metadata-readonly-seal.v1","Proposed actual Stage HRO schema")
def table(rows):
    out={}
    for x in rows:
        native_row(x);need(x["path"]not in out or out[x["path"]]==x,"Conflicting HRO native table");out[x["path"]]=x
    return out
need(table(hr["protected_metadata_before"])==base_map==table(hr["protected_metadata_after"]),"Stage HRO must retain exact Source15813 original rows")
need(hr["conditional_CORE_metadata_before"]==core_original==hr["conditional_CORE_metadata_after"]and hr["Common_original_metadata_only_before"]==common==hr["Common_original_metadata_only_after"],"Stage HRO Core/Common original binding")
human_md=native_row(hr["Human_after"]);need(human_md["path"]==str(HUMAN)and stat.S_IMODE(human_md["mode"])==0o444 and human_md["nlink"]==1,"HRO exact own Human binding")
enrol([human_md])
proposal_rows=hr["source_proposal_metadata_after"]
proposal_path=S/"pending/root_plan_v13_source_stage_control_from17808_v1/stage_control.py"
proposal_directory=proposal_path.parent
need(type(proposal_rows)is list and len(proposal_rows)==2 and [x["path"]for x in proposal_rows]==[str(proposal_path),str(proposal_directory)],"Exact original proposal file/directory HRO binding")
need(stat.S_ISREG(proposal_rows[0]["mode"])and stat.S_IMODE(proposal_rows[0]["mode"])==0o444 and proposal_rows[0]["nlink"]==1 and stat.S_ISDIR(proposal_rows[1]["mode"])and stat.S_IMODE(proposal_rows[1]["mode"])==0o555 and proposal_rows[1]["nlink"]==2,"Exact readonly proposal file/D")
need(sorted(os.listdir(proposal_directory))==["stage_control.py"],"Closed proposal directory universe")
enrol(proposal_rows)
pmd=md(ordinary(PRIMARY));need(stat.S_ISREG(pmd["mode"])and stat.S_IMODE(pmd["mode"])==0o444 and pmd["nlink"]==1,"Precreated actual stage primary shell")
enrol([pmd]);enrol(operational_parent_before.values())
enrol(readiness_native_original,creation);enrol([readiness_directory_original],creation)
# Operational parent additions so far are exclusively the readiness D; finish their event after PD/OUT/TMP are created.
core_check()
for path,before in original.items():
    if path not in operational_parent_before:need(md(metadata_path(path))==before,"Input changed before first project import")
tro_tuple=cpu_rec(T_PATH);hro_tuple=cpu_rec(HRO);human_tuple=cpu_rec(HUMAN);primary_tuple=cpu_rec(PRIMARY);proposal_tuple=cpu_rec(proposal_path)
human_raw=HUMAN.read_bytes();primary_raw=PRIMARY.read_bytes()
need(md(HUMAN)==human_md and md(PRIMARY)==pmd,"Own Human/shell changed during byte readback")
fence=b"\n```python\n"
need(human_raw.count(fence)==1,"Exactly one Human Python fence")
python=human_raw.split(fence,1)[1].split(b"\n```",1)[0]
header=SPEC["shell_header"].encode("utf-8")
need(header.startswith(b"#!/bin/bash\n")and primary_raw==header+python+b"\nPY\n","Exact precreated primary header plus whole Human Python fence")
co_r=receipt(T["actual_Root_execution_control"])
CO=load_control(co_r,1024*1024)
need(CO["actual_job_id"]=="17808"and CO["actual_new_inclusion"]==T["actual_inclusion"]and CO["actual_new_closure"]==T["actual_closure"]and CO["actual_new_library_acceptance"]==T["actual_library_acceptance"]and CO["actual_new_adapter_acceptance"]==T["actual_adapter_acceptance"],"Accepted Source control graph must bind actual A/CA/I/C")
I_r=receipt(T["actual_inclusion"]);need(I_r==dict(path=str(I_PATH),bytes=1823791,sha256=I_SHA),"Explicit exact accepted I fulltuple")
I=load_control(I_r,2*1024*1024)
need(I["schema"]=="benchmark-source-inclusion.v3"and I["status"]=="SOURCE_INCLUSION_AUDIT_PASS"and I["formal_array_job_id"]=="13260"and I["applied"]is False and I["issues"]==[],"Only actual nonstaging accepted I")
runners=I["runner_source_snapshot"];need(runners==CO["actual_new_runner_source_snapshot"]and len(runners)==6 and len({Path(x["path"]).name for x in runners})==6,"Exact I-selected frozen six")
main=next(x for x in runners if Path(x["path"]).name=="final_source_closure.py")
need(Path(main["path"]).parent==I_PATH.parent/"runner","Execute actual new I runner, never software fallback")
pins={}
def add_pins(rows):
    for r in rows:
        receipt(r);need(r["path"]not in pins or pins[r["path"]]==r,"Conflicting expected fulltuple");pins[r["path"]]=r
add_pins(CO["qualified_source12"]);need(len(CO["qualified_source12"])==12,"Qualified Source12")
add_pins(CO["qualified_software4"]);need(len(CO["qualified_software4"])==4,"Qualified software4")
add_pins(CO["control_receipts"]);need(len(CO["control_receipts"])==12,"Exact old production controls12")
add_pins(CO["current_readiness_own_CPU_receipts"])
add_pins(runners);add_pins([co_r,T["actual_library_acceptance"],T["actual_adapter_acceptance"],I_r,T["actual_closure"]])
add_pins([I[k]for pair in PAIR_KEYS for k in pair])
need(type(SPEC["extra_control_paths"])is list and len(set(SPEC["extra_control_paths"]))==len(SPEC["extra_control_paths"]),"Literal finite extra metadata-authenticated control paths")
for path in SPEC["extra_control_paths"]:
    need(path in base_map and path not in worker_metadata_paths and path!=common_path and under(Path(path),S/"submissions")and Path(path).suffix==".json","Only explicitly fixed own submissions JSON controls, never child/source permissions")
    actual=cpu_rec(path)
    need(path not in pins or pins[path]==actual,"An extra control cannot replace an existing expected fulltuple")
    pins[path]=actual
A=load_control(T["actual_library_acceptance"],1024*1024);CA=load_control(T["actual_adapter_acceptance"],1024*1024)
for pair in PAIR_KEYS:
    for k in pair:need(A[k]==I[k]==CA[k],"Preserved six-family actual pointer equality")
need(I["source_receipt_closure"]==T["actual_closure"],"Actual closure pointer")
for r in pins.values():check(r)
# Source only own bytes: there is no live preservation-validator call or child receipt traversal here.
physical={};destinations={};ordered=[]
for row in I["files"]:
    r=receipt(row["source"]);need(r["path"]in base_map,"Every physical Source must have qualified original native")
    need(r["path"]not in worker_metadata_paths and r["path"]!=common_path,"Only accepted physical Source copies, not original worker/Common targets")
    need(r["path"]not in physical or physical[r["path"]]==r,"Physical Source identity cannot switch FP");physical[r["path"]]=r
    rel=row["repository_relative"];q=Path(rel)
    need(type(rel)is str and not q.is_absolute()and rel not in ("",".")and ".."not in q.parts and ".git"not in q.parts and q.as_posix()==rel,"Exact audited destination spelling")
    target=ordinary(R/"source"/q);need(str(target)not in destinations,"Exact accepted I must have unique declared destinations")
    destinations[str(target)]=r;ordered.append((r,target,row))
for r in physical.values():check(r)
def target_readback(path,expected,purpose):
    # This exact existing I destination is SOURCE installation/readback, not Source-audit Common analysis.
    need(purpose=="INSTALLED_TARGET_SOURCE_BYTES","Closed installed-target readback purpose")
    p=ordinary(path);receipt(expected)
    need(str(p)in destinations and destinations[str(p)]==expected,"Exact accepted I destination and physical Source pin required")
    if str(p)!=common_path:
        actual=cpu_rec(p)
    else:
        need(str(p)==str(R/"source/rebuild/benchmark_common_review.py")and fp(expected)==(58825,"ad8edf0ac5250e587709c26e61957101072ea4343f83514271634b3bf7c36b5b"),"Only exact authenticated current I Common target may be read")
        need(md(p)==common and stat.S_IMODE(common["mode"])==0o664 and common["nlink"]==1,"Exact original Common native/0664 must be unchanged")
        h=hashlib.sha256();n=0
        with p.open("rb")as stream:
            for b in iter(lambda:stream.read(1048576),b""):h.update(b);n+=len(b)
        need(md(p)==common,"Installed Common Source target changed during readback")
        actual=dict(path=str(p),bytes=n,sha256=h.hexdigest())
    need(fp(actual)==fp(expected),"Installed target Source fullFP mismatch")
    return actual
old_targets={};expected_created=[];parent_before={};parent_names={};new_dirs=set()
for r,target,row in ordered:
    if os.path.lexists(str(target)):
        x=md(target);need(stat.S_ISREG(x["mode"])and x["nlink"]==1,"Existing destination must be nonlink single regular")
        enrol([x]);old_targets[str(target)]=x;target_readback(target,r,"INSTALLED_TARGET_SOURCE_BYTES")
    else:expected_created.append(str(target))
    p=target.parent
    while under(p,R/"source"):
        if os.path.lexists(str(p)):
            if str(p)not in parent_before:
                x,names=directory_state(p);parent_before[str(p)]=x;parent_names[str(p)]=names;enrol([x])
        else:new_dirs.add(str(p))
        if p==R/"source":break
        p=p.parent
need(not os.path.lexists(str(OUT))and not os.path.lexists(str(PD))and not os.path.lexists(str(TMP)),"Exclusive absent stage OUT/proof/TMP required")
need(os.environ.get("TMPDIR")==str(TMP),"Exact distinct job TMPDIR required")
# Original missing target/directory absence is rechecked immediately before the unchanged stage entry.
for path in expected_created+sorted(new_dirs):need(not os.path.lexists(path),"Missing target namespace changed before stage")
for path,before in old_targets.items():need(md(path)==before,"Existing installed file changed before stage")
for path,before in parent_before.items():need(md(path)==before,"Existing target parent changed before stage")
for path,before in original.items():
    if path not in operational_parent_before:need(md(metadata_path(path))==before,"Input native drift before stage")
TMP.mkdir(mode=0o775,exist_ok=False);enrol([md(TMP)],creation);need(os.listdir(TMP)==[],"Owned stage TMP starts empty")
PD.mkdir(mode=0o755,exist_ok=False);proof_dir_created=md(PD);enrol([proof_dir_created],creation)
stage_entered=False;stage_returned=False;result=None;stage_receipt=None
installed=[];directory_event_rows=[];root_proof=None
def checked_installed():
    out=[]
    for r,target,row in ordered:
        actual=target_readback(target,r,"INSTALLED_TARGET_SOURCE_BYTES")
        out.append(dict(repository_relative=row["repository_relative"],actual=actual,original_source=row.get("original_source"),roles=row["roles"],kind=row["kind"]))
    return out
def verify_inputs():
    core_check()
    for r in pins.values():check(r)
    for r in physical.values():check(r)
    need(cpu_rec(T_PATH)==tro_tuple and cpu_rec(HRO)==hro_tuple and cpu_rec(HUMAN)==human_tuple and cpu_rec(PRIMARY)==primary_tuple and cpu_rec(proposal_path)==proposal_tuple,"Root bound input control drift")
    need(sorted(os.listdir(proposal_directory))==["stage_control.py"],"Original Source proposal directory universe changed")
def persist_proof(value,directory=PD):
    p=directory/"execution_control.json";raw=(json.dumps(value,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
    with p.open("xb")as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno());os.fchmod(stream.fileno(),0o444);os.fsync(stream.fileno())
    capture_file(p)
    need(p.read_bytes()==raw and strict_json(p.read_bytes())==value,"Whole Root proof JSON/byte readback")
    fd=os.open(str(directory),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        first=creation[str(directory)];now=md(directory)
        need(all(now[k]==first[k]for k in ("path","inode","mode","dev","uid","gid","nlink"))and sorted(os.listdir(directory))==["execution_control.json"],"Exact original Root proof directory creation and one declared file")
        os.fchmod(fd,0o555);os.fsync(fd)
    finally:os.close(fd)
    after=md(directory)
    need(str(directory)not in creation_directory_events,"Root proof directory cannot refresh a prior seal event")
    creation_directory_events[str(directory)]=dict(before=creation[str(directory)],after=after,created_children=["execution_control.json"],mode_transition="EXCLUSIVE_OWN_DIRECTORY_0755_TO_0555_AFTER_OWN_WRITE")
    fsync_dir(directory.parent)
    return cpu_rec(p)
try:
    stage_entered=True
    argv_before=sys.argv[:]
    try:
        sys.argv=[main["path"],"stage","--audit",str(I_PATH),"--audit-sha256",I_SHA,"--out",str(OUT)]
        runpy.run_path(main["path"],run_name="__main__")
        stage_returned=True
    finally:sys.argv=argv_before
    need(sorted(os.listdir(OUT))==["acceptance.json"],"Stage emits exactly one actual own output")
    stage_file=ordinary(OUT/"acceptance.json");stage_first_native=md(stage_file)
    need(stat.S_ISREG(stage_first_native["mode"])and stat.S_IMODE(stage_first_native["mode"])==0o444 and stage_first_native["nlink"]==1,"Exact unchanged stage acceptance regular444")
    stage_fd=os.open(str(stage_file),os.O_RDONLY|os.O_NOFOLLOW)
    try:
        fs=os.fstat(stage_fd)
        need((fs.st_size,fs.st_ino,fs.st_mtime_ns,fs.st_ctime_ns,fs.st_mode,fs.st_dev,fs.st_nlink,fs.st_uid,fs.st_gid)==tuple(stage_first_native[k]for k in("bytes","inode","mtime_ns","ctime_ns","mode","dev","nlink","uid","gid")),"Stage acceptance fd/fullnative binding")
        os.fsync(stage_fd)
    finally:os.close(stage_fd)
    fsync_dir(OUT)
    need(md(stage_file)==stage_first_native,"Stage acceptance unchanged by durable fsync")
    enrol([md(OUT)],creation);capture_file(OUT/"acceptance.json")
    for path in expected_created:capture_file(path)
    for path in sorted(new_dirs):
        x,names=directory_state(path);enrol([x],creation)
        expected_names=sorted({Path(n).name for n in expected_created+list(new_dirs)if str(Path(n).parent)==path})
        need(names==expected_names,"New target directory contains only exact declared stage children")
    all_new_nodes=expected_created+sorted(new_dirs)
    for path,before in parent_before.items():
        added={Path(n).name for n in all_new_nodes if str(Path(n).parent)==path}
        nnew=sum(str(Path(n).parent)==path for n in new_dirs)
        directory_event_rows.append(directory_event(path,before,parent_names[path],added,nnew))
    op_nodes=[str(D),str(PD),str(OUT),str(TMP)]
    for path,before in operational_parent_before.items():
        added={Path(n).name for n in op_nodes if str(Path(n).parent)==path}
        directory_event_rows.append(directory_event(path,before,operational_parent_names[path],added,len(added)))
    stage_receipt=cpu_rec(OUT/"acceptance.json")
    result=load_control(stage_receipt,1024*1024)
    need(set(result)=={"status","source_inclusion","allocation","entry_n","created_files","working_tree_commit_or_stage_performed","ACTIVE_changed","GPU_submitted"},"Exact eight-field stage output, no schema")
    need(result["status"]=="EXACT_AUDITED_FROZEN_SOURCE_SET_INSTALLED_NOT_GIT_STAGED"and result["source_inclusion"]==I_r and result["entry_n"]==len(ordered)and result["created_files"]==expected_created,"Exact stage I/count/ordered newly-created list")
    need(result["working_tree_commit_or_stage_performed"]is False and result["ACTIVE_changed"]is False and result["GPU_submitted"]is False,"Stage is not Git/publication/ACTIVE")
    allocation=result["allocation"];need(allocation["job_id"]==jid and allocation["allocated_CPUs"]==1 and allocation["allocated_gpus"]==0 and allocation["numeric_sacct_row"][0]==jid and allocation["numeric_sacct_row"][1]=="RUNNING","Actual fresh new stage CPU allocation, not source17808")
    need(allocation["numeric_sacct_row"][3:]==["u21111210118","u21111210118","organ"],"New stage Source cpu owner/account/organ")
    installed=checked_installed();verify_inputs()
    need(cpu_rec(OUT/"acceptance.json")==stage_receipt and strict_json((OUT/"acceptance.json").read_bytes())==result,"Stage whole output after input/end reads")
    native_sweep()
    proof=dict(schema="root-plan-v13-exact-I-selected-stage-control.v1",status="ACTUAL_EXACT_I_SELECTED_STAGE_RETURNED_AND_ROOT_FULL_READBACK_NOT_GIT_OR_PUBLICATION",
        actual_job_id=jid,source_inclusion=I_r,actual_I_selected_runner_source_snapshot=runners,actual_stage_argv=[main["path"],"stage","--audit",str(I_PATH),"--audit-sha256",I_SHA,"--out",str(OUT)],
        allocation=allocation,readiness=obj,readiness_cpu_receipts=[cpu_rec(x["path"])for x in readiness_native_original],
        source_terminal_own_CPU_tuple=tro_tuple,stage_HRO_own_CPU_tuple=hro_tuple,Root_Human_own_CPU_tuple=human_tuple,primary_script_own_CPU_tuple=primary_tuple,unexecuted_Source_proposal_own_CPU_tuple=proposal_tuple,stage_acceptance_fsync_without_permission_change=True,
        accepted_input_control_receipts=list(pins.values()),physical_Source_count=len(physical),physical_Source_receipts=list(physical.values()),
        entry_count=len(ordered),existing_target_count=len(old_targets),exact_created_files=expected_created,installed_Source_readbacks=installed,
        existing_target_native_before=list(old_targets.values()),new_output_native_first_capture=list(creation.values()),exact_directory_events=directory_event_rows,
        original_native_union_count=len(original),stage_acceptance=stage_receipt,stage_acceptance_object=result,
        all_installed_modes_left_as_stage_produced=True,existing_file_modes_and_native_unchanged=True,no_repeat_software_audit_or_preservation_validators=True,
        Common_metadata_only_outside_exact_I_installed_target_readback=True,worker_original_metadata_only=True,
        exact_Common_installed_target_purpose="INSTALLED_TARGET_SOURCE_BYTES",own_proof_directory_creation_before=proof_dir_created,
        source_staged=True,Git_changed=False,published=False,ACTIVE_changed=False,
        partial_failure_requires_preservation_and_no_blind_rerun=True,qualification_still_requires_fresh_terminal_Root_two_content_and_independent_TRO=True,
        true_last_native_sweep_REQUIRED_after_all_following_reads=True)
    root_proof=persist_proof(proof)
    verify_inputs();need(checked_installed()==installed,"All installed fulltuples changed after Root proof output")
    need(cpu_rec(OUT/"acceptance.json")==stage_receipt,"Stage result changed after Root proof")
    # Actual last payload read/hash is this full Root-proof receipt and whole JSON reread.
    need(cpu_rec(PD/"execution_control.json")==root_proof and strict_json((PD/"execution_control.json").read_bytes())==proof,"Root proof final whole-object readback")
    need(os.listdir(TMP)==[] and set(os.listdir(D))==readiness_names_original,"Readiness/TMP exact finite children")
    native_sweep()
    print(json.dumps(dict(status="ROOT_EXACT_NEW_I_SELECTED_STAGE_FULL_SOURCE_READBACK_NOT_GIT_OR_PUBLICATION",
        actual_job_id=jid,allocation=allocation,source_inclusion=I_r,stage_acceptance=stage_receipt,execution_control=root_proof,
        entry_n=len(ordered),created_files_n=len(expected_created),physical_Source_n=len(physical),
        unexecuted_Source_proposal_own_CPU_tuple=proposal_tuple,stage_acceptance_fsync_without_permission_change=True,own_proof_directory_creation_event=creation_directory_events[str(PD)],true_last_original_native_union_PASS=True,
        qualification_requires_fresh_terminal_Root_plus_two_content_and_independent_TRO=True),sort_keys=True),flush=True)
except BaseException as original_error:
    # Original stage/readback exception always survives; these outcomes are not qualification.
    outcomes=[]
    def failure_guard(name,callback):
        try:
            callback();outcomes.append(dict(name=name,completed=True,error_type=None,error=None))
        except BaseException as guard_error:
            outcomes.append(dict(name=name,completed=False,error_type=type(guard_error).__name__,error=str(guard_error)))
    failure_guard("protected_inputs_end",verify_inputs)
    failure_guard("existing_destination_original_native",lambda:need(all(md(path)==before for path,before in old_targets.items()),"Existing installed original file changed"))
    failure_guard("native_before_failure_packet",native_sweep)
    try:
        FD=S/"submissions"/("source_plan_v13_stage_"+jid+"_root_typed_incomplete")
        need(not os.path.lexists(str(FD)),"Exclusive typed failure namespace")
        FD.mkdir(mode=0o755,exist_ok=False);enrol([md(FD)],creation)
        failure=dict(schema="root-plan-v13-exact-I-selected-stage-failure.v1",status="ACTUAL_STAGE_OR_ROOT_READBACK_FAILED_PARTIAL_OUTPUTS_RETAINED_NOT_ACCEPTED",
            actual_job_id=jid,stage_entered=stage_entered,stage_returned=stage_returned,source_inclusion=I_r,exact_runner=main,
            reason_type=type(original_error).__name__,reason=str(original_error),source_publication_or_Git_acceptance=False,
            expected_created_files=expected_created,actually_present_targets=[md(p)for p in expected_created if os.path.lexists(p)],
            actually_present_new_directories=[md(p)for p in sorted(new_dirs)if os.path.lexists(p)],
            stage_OUT_metadata=md(OUT)if os.path.lexists(str(OUT))else None,
            original_native_guard_outcomes_before_failure_packet=outcomes,
            successful_looking_prior_Root_proof_preserved=str(PD/"execution_control.json")if os.path.lexists(str(PD/"execution_control.json"))else None,
            all_partial_outputs_retained=True,no_blind_rerun=True,qualified=False)
        failed_receipt=persist_proof(failure,FD)
        failure_guard("protected_inputs_after_failure_packet",verify_inputs)
        failure_guard("TRUE_LAST_native_after_failure_packet",native_sweep)
        # Failure diagnostics only: never emit a successful stage/qualification descriptor.
        print(json.dumps({"status":"ROOT_STAGE_FAILED_ORIGINAL_EXCEPTION_RETHROWN","actual_job_id":jid,
            "typed_failure":failed_receipt,"final_guard_outcomes":outcomes,"qualified":False}),flush=True)
    except BaseException as preserve_error:
        print(json.dumps({"status":"ROOT_STAGE_FAILURE_PRESERVATION_ALSO_FAILED","actual_job_id":jid,"preserve_error_type":type(preserve_error).__name__,"qualified":False}),flush=True)
    raise
PY
