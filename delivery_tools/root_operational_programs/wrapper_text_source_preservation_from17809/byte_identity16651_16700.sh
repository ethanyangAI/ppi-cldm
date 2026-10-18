exec env -u PYTHONPATH CUDA_VISIBLE_DEVICES= JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /lustre/users/u21111210118/projects/test9/env/core/bin/python -B - <<'ROOT_FIXED_SOURCE_BYTE_IDENTITY_OBSERVER_REV1'
import os, sys, json, re, stat, time, datetime, subprocess
from pathlib import Path
S = Path("/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery")
jid = os.environ.get("SLURM_JOB_ID", "")
if not re.fullmatch("[0-9]+", jid):
    raise SystemExit("Current owned Slurm job ID required")
expected_env = {"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
if any(os.environ.get(k) != v for k, v in expected_env.items()) or "PYTHONPATH" in os.environ:
    raise SystemExit("Original CPU/import/thread isolation required")
D = S / "submissions" / ("source_plan_v4_source_byte_observer_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_final_source_byte_identity_observer_v4", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-plan-v4-source-byte-observer-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_PLAN_V4_FIXED_SOURCE_BYTE_OBSERVER_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_PLAN_V4_FIXED_SOURCE_BYTE_OBSERVER_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_PLAN_V4_FIXED_SOURCE_BYTE_OBSERVER_NOT_EXECUTED"
obj = {"schema": "root-current-owned-plan-v4-source-byte-observer-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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



# All operations below occur only after actual current owned CPU1/GPU0 readiness.
# This is a Root operational envelope; execute only the qualified frozen adapter.
import hashlib
R=Path("/lustre/users/u21111210118/projects/test9")
G=S/"runs/final_source_finite_worker_alias_software_16651/runner"
P=S/"pending/final_source_closure_v3_fixturefix4_finite_worker_alias1"
CORE=R/"env/core/bin/python"; REAL=CORE.with_name("python3.11")
REQUEST=S/"pending/final_source_context_request_from16651_16687_v4/request.json"
PLAN=S/"pending/final_source_plan_from14706_14925_16651_16671_v4/final_source_plan.json"
HANDOFF=PLAN.with_name("HANDOFF.md")
ROOTDOC=S/"handoffs/ROOT_FIXED_PLAN_V4_PRODUCTION_SOURCE_AUDIT_FROM16651_16687_20261015.md"
SOFTWARE=dict(path=str(S/"runs/final_source_finite_worker_alias_software_16651/acceptance.json"),bytes=6590,sha256="5a8bfa759754985cd72bd35cb50192eb2aefef0df3fc73c28aebd4aed00adfe5")
PLANPIN=dict(path=str(PLAN),bytes=1941606,sha256="b7a8c58b5794ab9b221a70e46fc47614395af20b1fb3f32ef86bd507e387bf30")
HANDOFFPIN=dict(path=str(HANDOFF),bytes=44899,sha256="1d3ad683a6707b62dbab96ec37e0418ea350f7181a60a581c138363b930dd76f")
CAPPIN=dict(path=str(S/"runs/final_source_plan_v4_ownsha_16687/capture.json"),bytes=24887,sha256="b95e3e4c1956db7ec5db948bf27eaa0ffdd59806bdbb6adae73021e43a2272c5")
source_pins=[["final_source_closure.py",164179,"4106c23e585c0e66c5541b22c10af8b80dce277dbc4c137dc037d3a87e896956"],["test_final_source_closure.py",78857,"607ddb717d51d93e89f786e5f4cad5ea2ec6727d91c4c27c9694e77c68dbfe67"],["final_source_cpu.sbatch",1613,"3cb2d517d0763b587218f3587ca87e8cdb97ed148926b4c936bee71c9b2e8c6f"],["HANDOFF.md",15973,"b63c1bf9ded2adc24e09b4ca795345387b58ad689886e4355ebd67b09ebbe5f3"],["FINAL_SOURCE_CHECKLIST.md",3280,"7b7a6ca1fc5ef2d49968af033310557d28684ac97aaaa5f944d819928a01cb56"],["final_source_context_adapter.py",9850,"2db4ff9a01d189eea237acadf432fb7046292b927ba08fbb9522aff2b839785e"]]
def need(value,message):
 if not value: raise ValueError(message)
def md(p):
 p=Path(p); t=p.lstat()
 return dict(path=str(p),bytes=t.st_size,inode=t.st_ino,mtime_ns=t.st_mtime_ns,ctime_ns=t.st_ctime_ns,mode=t.st_mode,dev=t.st_dev,nlink=t.st_nlink,uid=t.st_uid,gid=t.st_gid)
def authority(p,leaf_link=False):
 p=Path(p);need(p.is_absolute()and p.is_relative_to(R),"Exact authority path required")
 for node in [p]+list(p.parents):
  if node==R.parent: break
  need(not stat.S_ISLNK(node.lstat().st_mode)or (leaf_link and node==p),"Nonlink exact ancestry required")
 return p
def record(p):
 p=Path(p); h=hashlib.sha256();n=0
 with p.open("rb")as f:
  for block in iter(lambda:f.read(1048576),b""):h.update(block);n+=len(block)
 return dict(path=str(p),bytes=n,sha256=h.hexdigest())
def readonly(p,pin=None):
 p=authority(p); a=md(p)
 need(stat.S_ISREG(a["mode"])and stat.S_IMODE(a["mode"])==0o444 and a["nlink"]==1,"Readonly single-link exact SOURCE/CONTROL required: "+str(p))
 r=record(p);need(md(p)==a,"Stable own-byte read metadata required")
 if pin is not None:need(r==pin,"Exact qualified bytes fork: "+str(p))
 return r,a
def pairs(items):
 result={}
 for k,v in items:
  need(k not in result,"Duplicate JSON control key");result[k]=v
 return result
def finite_float(value):
 result=float(value)
 need(result==result and abs(result)!=float("inf"),"Nonfinite exponent forbidden")
 return result
def read_json(p):
 return json.loads(Path(p).read_text("utf-8"),object_pairs_hook=pairs,parse_constant=lambda x: (_ for _ in ()).throw(ValueError("Nonfinite JSON")),parse_float=finite_float)
need(sys.flags.optimize==0,"Assertions and qualified strict verification must remain enabled")
software_r,software_md=readonly(SOFTWARE["path"],SOFTWARE)
swa=read_json(SOFTWARE["path"])
need(swa["schema"]=="final-source-materialized-software-acceptance.v3"and swa["status"]=="FINAL_SOURCE_MATERIALIZED_INHERITED_ENTRYPOINTS_OPAQUE_VENDOR_AND_FINITE_WORKER_CONTROL_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_INTEGRATION","Qualified actual software122 status required")
expected_frozen=[dict(path=str(G/n),bytes=z,sha256=h)for n,z,h in source_pins]
expected_original=[dict(path=str(P/n),bytes=z,sha256=h)for n,z,h in source_pins]
need(swa["source_files"]==expected_frozen and swa["original_executing_sources"]==expected_original,"Exact original+frozen qualified source12 required")
sources=expected_original+expected_frozen;source_before=[]
for directory in [P,G]:
 authority(directory);t=directory.lstat()
 need(stat.S_ISDIR(t.st_mode)and stat.S_IMODE(t.st_mode)==0o555 and {x.name for x in directory.iterdir()}=={x[0]for x in source_pins},"Exact readonly source6 directory required")
for pin in sources: source_before.append(readonly(pin["path"],pin)[1])
source_directories_before=[md(P),md(G)]
software_controls=[
 SOFTWARE,
 dict(path=str(S/"runs/final_source_finite_worker_alias_software_16651/contracts.json"),bytes=2170,sha256="bb6bce77eaf671fcf952ec5766047526f46d93de08039d012fb8666d2c174cff"),
 dict(path=str(S/"runs/final_source_finite_worker_alias_software_16651/contracts.txt"),bytes=20352,sha256="2b75aeaff9273de828d6d4629a0eb815b6c73087f777ef47e115fdb626f861e2"),
 dict(path=str(S/"runs/final_source_finite_worker_alias_software_16651/source_snapshot.json"),bytes=15766,sha256="7b000f699f424138e9b44f5cd74d12d268d8567d2b98d6b9e45c02f305315d4d")]
software_before=[readonly(r["path"],r)[1]for r in software_controls]
ct=read_json(software_controls[1]["path"]);snapshot=read_json(software_controls[3]["path"])
need(swa["contracts"]==software_controls[1]and ct["log"]==software_controls[2]and swa["source_snapshot"]==software_controls[3],"Whole four software evidence controls required")
need(snapshot["original_executing_sources"]==expected_original and snapshot["source_files"]==expected_frozen and snapshot["original_metadata_before"]==snapshot["original_metadata_after"]==source_before[:6]and snapshot["frozen_metadata_before"]==snapshot["frozen_metadata_after"]==source_before[6:],"Actual qualified snapshot/current source12 stable metadata required")
runtime=swa["conditional_core_runtime"]
def core_readback():
 need(Path(sys.executable)==CORE,"Exact logical approved CORE executable required")
 authority(CORE,True);authority(REAL);a=md(CORE);b=md(REAL)
 need(CORE.is_symlink()and os.readlink(CORE)=="python3.11"and CORE.resolve()==REAL and stat.S_ISREG(b["mode"])and not REAL.is_symlink(),"Exact CORE link and resolved regular interpreter required")
 r=record(REAL)
 need(r["bytes"]==25916456 and r["sha256"]=="76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a","Conditional CORE whole-byte identity required")
 need(md(CORE)==a and md(REAL)==b and a==runtime["logical_metadata"]and b==runtime["resolved_metadata"],"Qualified conditional CORE stable metadata required")
 need(runtime["schema"]=="conditional-core-interpreter-byte-identity.v1"and runtime["logical_executable"]==str(CORE)and runtime["link_text"]=="python3.11"and runtime["conditional_excluded_not_archived"]is True and runtime["atime_excluded_from_stable_identity"]is True,"Conditional CORE scalar-only scope required")
 return runtime
core_readback()
DIAGDOC=S/"handoffs/ROOT_FIXED_SOURCE_BYTE_IDENTITY_FAILURE_OBSERVER_FROM16651_16700_20261015_REV1.md"
FAILEDSEAL=S/"submissions/final_source_finite_worker_alias_audit16700_actual_failed_terminal_metadata_seal/receipt.json"
controls=[REQUEST,REQUEST.with_name("request_metadata.json"),PLAN,HANDOFF,ROOTDOC,S/"submissions/final_source_context_request_from16651_16687_v4_metadata_readonly_seal/receipt.json",S/"submissions/final_source_plan_v4_from16651_16671_metadata_readonly_seal/receipt.json",Path(CAPPIN["path"]),S/"submissions/final_source_plan_v4_ownsha16687_actual_terminal_metadata_seal/receipt.json"]+[DIAGDOC,FAILEDSEAL]
control_rows=[readonly(p)for p in controls];control_receipts=[r for r,m in control_rows];control_before=[m for r,m in control_rows]
need(control_receipts[2]==PLANPIN and control_receipts[3]==HANDOFFPIN and control_receipts[7]==CAPPIN,"Actual16687 Plan/Handoff/CAP bytes required")
need(control_receipts[0]["bytes"]==1263 and control_before[0]["inode"]==144115643443090881 and control_before[0]["mtime_ns"]==1792065789000000000 and control_before[0]["ctime_ns"]==1792066016000000000,"Fixed readonly new strict request required")
need(control_receipts[1]["bytes"]==1745 and control_before[1]["inode"]==144115643443090882 and control_before[1]["mtime_ns"]==1792065789000000000 and control_before[1]["ctime_ns"]==1792066016000000000,"Fixed readonly new request preparation metadata required")
need(control_receipts[5]["bytes"]==38596 and control_before[5]["inode"]==144115643443090884 and control_before[5]["mtime_ns"]==1792066016000000000,"Actual reviewed strict request seal required")
need(control_receipts[8]["bytes"]==62458 and control_before[8]["inode"]==144115643443090879 and control_before[8]["mtime_ns"]==1792065630000000000,"Actual accepted16687 terminal own-control required")
q=read_json(REQUEST)
keys=["schema","root_owned","raw_JSON_rewrite_allowed","generic_relative_resolution_allowed","generic_external_resolution_allowed","library_software_acceptance","mapper_software_acceptance","final_source_plan","bbf_parent_aliases","historical_parent_aliases","recovered_parent_aliases","archive_parent_aliases","finite_source_parent_aliases"]
need(list(q)==keys and q["schema"]=="final-source-materialized-context-read-view-request.v3"and q["root_owned"]is True,"Exact strict13 request required")
need(all(q[k]is False for k in keys[2:5])and all(type(q[k])is list and not q[k]for k in keys[8:]),"Threefalse/fiveempty aliases required")
need(q["library_software_acceptance"]==SOFTWARE and q["final_source_plan"]==PLANPIN and q["mapper_software_acceptance"]==dict(path=str(S/"runs/exact_context_mapper_v4_13319/acceptance.json"),bytes=15049,sha256="a66b8186aa4ba2c737fe3e607f84bb90ecc35b35f271022bbcb66ac3cb327890"),"Exact qualified software122/Plan/Mapper request tuples required")
plan=read_json(PLAN);cap=read_json(CAPPIN["path"]);terminal=read_json(controls[8]);reqseal=read_json(controls[5]);planseal=read_json(controls[6])
need(cap["schema"]=="root-new-plan-v4-own-sha-capture.v1"and cap["status"]=="ACTUAL_NEW_PLAN_V4_OWN_SHA_CPU_CAPTURED_NOT_SOURCE_AUDIT_STAGE_OR_SCIENCE"and cap["plan"]==PLANPIN and cap["handoff"]==HANDOFFPIN and cap["actual_job_id"]=="16687","Accepted actual16687 Plan tuples required")
need(terminal["schema"]=="root-source-plan-v4-own-sha-actual-terminal-metadata-seal.v1"and terminal["status"]=="ACTUAL_NEW_PLAN_V4_OWN_SHA_CONTENT_AND_TERMINAL_METADATA_READBACK_PASS_NOT_SOURCE_ACCEPTANCE"and terminal["actual_job_id"]=="16687"and terminal["actual_capture"]==CAPPIN and terminal["actual_plan"]==PLANPIN and terminal["actual_handoff"]==HANDOFFPIN,"Actual16687 successful terminal seal required")
need(terminal["fresh_terminal"]["returncode"]==0 and terminal["fresh_terminal"]["actual_row"]==["16687","COMPLETED","0:0","5","1","test9_source_plan_v4_ownsha_cpu","u21111210118","u21111210118","organ"]and terminal["actual_allocation"]==cap["allocation"]and terminal["Root_plus_two_whole_saved_content_READBACK_PASS"]is True,"Actual16687 terminal and actual RUNNING CPU1/GPU0 basis required")
need(reqseal["schema"]=="root-new-source-materialized-adapter-request-metadata-readonly-seal.v1"and reqseal["status"]=="ROOT_NEW_STRICT_ADAPTER_REQUEST_WHOLE_STATIC_AND_METADATA_READONLY_PASS_NOT_SOURCE_AUDIT_STAGE_OR_SCIENCE"and reqseal["Root_plus_two_independent_whole_STATIC_READBACK_PASS"]is True and reqseal["after_files"]==control_before[:2],"Actual strict request readonly source-control seal required")
need(planseal["schema"]=="root-final-source-plan-v4-metadata-readonly-seal.v1"and planseal["after_files"]==control_before[2:4],"Actual reviewed immutable Plan/Handoff metadata seal required")
request_directory_before=md(authority(REQUEST.parent));plan_directory_before=md(authority(PLAN.parent))
need(request_directory_before==reqseal["after_directory"]and plan_directory_before==planseal["after_directory"]==cap["plan_directory_metadata_after"]and stat.S_ISDIR(request_directory_before["mode"])and stat.S_ISDIR(plan_directory_before["mode"])and stat.S_IMODE(request_directory_before["mode"])==stat.S_IMODE(plan_directory_before["mode"])==0o555,"Exact reviewed readonly request/Plan directories required")
need(plan["library_software_acceptance"]==SOFTWARE and plan["mapper_software_acceptance"]==q["mapper_software_acceptance"]and len(plan["modules"])==9 and len(plan["context_parent_seeds"])==17 and len(plan["aliases"])==3,"Fixed actual9/17/3/currentsoftware shape required")
need(sum(len(m["sources"])for m in plan["modules"])==638 and sum(len(m["seeds"])for m in plan["modules"])==3809 and len(plan["late_Composer_additional_control_history"])==27 and len(plan["plan_v3_original_source_provenance"])==61 and len(plan["late_Composer_control_history_from16454"])==83,"Fixed reviewed whole Plan shape required")
need(cap["software_acceptance"]==SOFTWARE and cap["source_files"]==expected_frozen and cap["original_executing_sources"]==expected_original and cap["conditional_core_runtime"]==runtime,"Actual16687 qualified source/software/runtime pointers required")
need(cap["control_metadata_after"][:2]==control_before[2:4]and cap["source_metadata_original_before"]+cap["source_metadata_frozen_before"]==source_before and cap["software_control_metadata_after"]==software_before,"Actual16687 current Plan/Handoff/Source12/software4 metadata required")
need(all(cap[k]is True for k in ["whole6_source_pre_end_afteroutput_bound","conditional_runtime_pre_end_afteroutput_bound","software4_control_pre_end_afteroutput_bound","all7_controls_pre_end_afteroutput_bound","plan_child_receipts_shape_only_no_child_IO","prior_capture_and_seal_own_bytes_only_no_child_IO"]),"Actual16687 complete seven-control qualification required")
need(all(cap[k]is False for k in ["scientific_receipt_children_read_or_hashed","compiler_or_tests_or_new_software_executed","historical_Slurm_queried","source_audit_executed","source_staged","published","ACTIVE_changed"]),"Actual16687 narrow control scope required")

def final_readback():
 need([md(authority(p))for p in[P,G]]==source_directories_before and md(authority(REQUEST.parent))==request_directory_before and md(authority(PLAN.parent))==plan_directory_before,"Readonly Source/request/Plan directories changed")
 need([readonly(r["path"],r)[1]for r in sources]==source_before,"Qualified original+frozen source12 changed")
 need([readonly(r["path"],r)[1]for r in software_controls]==software_before,"Qualified software4 controls changed")
 need([readonly(r["path"],r)[1]for r in control_receipts]==control_before,"Root own request/Plan/control bytes or stable metadata changed")
 core_readback()
final_readback()


failure_seal=read_json(FAILEDSEAL)
need(control_receipts[10]["bytes"]==1147726 and control_before[10]["inode"]==144115643443091081 and control_before[10]["mtime_ns"]==1792067895000000000,"Actual qualified16700 failed terminal own-control required")
need(failure_seal["schema"]=="root-plan-v4-finite-worker-source-audit-failed-terminal-metadata-seal.v1"and failure_seal["status"]=="ACTUAL16700_FAILED_SOURCE_BYTES_GUARD_AND_OWNED_OUTPUT_METADATA_READBACK_PASS_NOT_SOURCE_ACCEPTANCE"and failure_seal["actual_job_id"]=="16700"and failure_seal["fresh_terminal"]["returncode"]==0 and failure_seal["fresh_terminal"]["actual_row"]==["16700","FAILED","1:0","354","1","test9_final_source_finite_worker_alias_v3","u21111210118","u21111210118","organ"],"Actual preserved16700 failed terminal control differs")
need(failure_seal["original_failure_expected_receipt_parent_trail_module_UNOBSERVED"]is True and failure_seal["Source_acceptance"]is False,"Original failed16700 expected tuple/context remains unobserved")
NAMED=R/"source/rebuild/bbf_input_diagnostic.py"
named_expected_metadata=dict(path=str(NAMED),bytes=24830,inode=144115543165691303,mtime_ns=1791695234000000000,ctime_ns=1791695234000000000,mode=33204,dev=1119461688,nlink=1,uid=6263900,gid=6263900)
authority(NAMED);named_before=md(NAMED)
need(named_before==named_expected_metadata and stat.S_ISREG(named_before["mode"])and named_before["nlink"]==1,"Exact current regular nonlink single-link fixed SOURCE metadata required")
# This is the only additional non-control own-byte read allowed by the observer.
# It is fixed SOURCE code, never a Worker or scientific parent/child.
named_actual=record(NAMED);need(md(NAMED)==named_before,"Fixed SOURCE changed during initial actual CPU own-byte read")
def observer_readback():
 final_readback();authority(NAMED)
 need(md(NAMED)==named_before and record(NAMED)==named_actual and md(NAMED)==named_before,"Fixed SOURCE own bytes/full stable metadata changed")
observer_readback()
OUT=S/"runs"/("final_source_byte_identity_observer_"+jid)
AUX=OUT.with_name(OUT.name+"_context_adapter");AUX_MAIN=AUX/"runner/final_source_closure.py"
OBS=S/"submissions"/("source_byte_identity_failure_observer_"+jid)
for path in[OUT,AUX,OBS]:need(not path.exists()and not path.is_symlink(),"Exclusive absent diagnostic namespaces required")
OBS.mkdir(mode=0o755,exist_ok=False)
def write_observation(name,value):
 path=OBS/name;data=(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode()
 with path.open("xb")as stream:stream.write(data);stream.flush();os.fsync(stream.fileno());os.fchmod(stream.fileno(),0o444)
 result=record(path);need(path.read_bytes()==data,"Whole durable observer output reread differs");return result
argv=[str(G/"final_source_context_adapter.py"),"--request",str(REQUEST),"--out",str(OUT)]
import runpy
saved_argv=list(sys.argv)
try:
 sys.argv=argv
 try:
  runpy.run_path(str(G/"final_source_context_adapter.py"),run_name="__main__")
 finally:sys.argv=saved_argv
except BaseException as original_error:
 try:
  need(type(original_error)is ValueError and str(original_error)=="Required exact bytes changed: "+str(NAMED),"Exact fixed SOURCE guard failure required for qualified observation")
  # Only the exact current qualified AUX own6 module is inspected.
  actual_aux=[dict(path=str(AUX/"runner"/n),bytes=z,sha256=h)for n,z,h in source_pins]
  aux_metadata=[readonly(r["path"],r)[1]for r in actual_aux]
  need(stat.S_IMODE(authority(AUX/"runner").lstat().st_mode)==0o555 and {x.name for x in(AUX/"runner").iterdir()}=={x[0]for x in source_pins},"Exact actual frozen AUX own6 directory required")
  frames=[];tb=original_error.__traceback__
  while tb is not None:
   frame=tb.tb_frame
   if frame.f_code.co_filename==str(AUX_MAIN):
    frames.append((frame.f_code.co_name,tb.tb_lineno,frame))
   tb=tb.tb_next
  selected={}
  required_frames={"audit":2422,"resolve":2350,"verify":65,"need":40}
  for name,line in required_frames.items():
   hits=[frame for fn,ln,frame in frames if fn==name and ln==line]
   need(len(hits)==1,"Exact current AUX exception frame missing or ambiguous: "+name);selected[name]=hits[0]
  af=selected["audit"].f_locals;rf=selected["resolve"].f_locals;vf=selected["verify"].f_locals
  r=af["r"];need(isinstance(r,dict)and {"path","bytes","sha256"}<=r.keys(),"Exact failed receipt scalar3 required")
  need(isinstance(r["path"],str)and Path(r["path"])==NAMED and type(r["bytes"])is int and r["bytes"]>=0 and isinstance(r["sha256"],str)and re.fullmatch("[0-9a-f]{64}",r["sha256"])is not None,"Exact fixed SOURCE failed receipt shape required")
  need(rf["r"]is r and vf["r"]is r and type(vf["p"])is type(NAMED)and vf["p"]==NAMED,"Exact audit/resolve/verify receipt and physical SOURCE path binding required")
  need((named_actual["bytes"],named_actual["sha256"])!=(r["bytes"],r["sha256"]),"Actual fixed SOURCE fingerprint must differ from failed request")
  failed_receipt={k:r[k]for k in["path","bytes","sha256"]}
  receipt_extra_keys=sorted(k for k in r if k not in failed_receipt)
  parent=af["parent"];trail=af["trail"];module=af["module"]
  need(parent is None or isinstance(parent,str),"Parent must remain original scalar or null")
  need(type(trail)is tuple and all(isinstance(x,str)for x in trail)and module in({m["role"]for m in plan["modules"]}|{"EXACT_ACCEPTED_CONTEXT_PARENT"}),"Original field trail/module scalar shape required")
  need(af["stage"]=="recursive_exact_new_dependencies","Actual recursive dependency stage required")
  aliases=rf["aliases"];need(isinstance(aliases,dict),"Actual exact alias lookup mapping required")
  lookup=(r["path"],r["sha256"],r["bytes"]);need(lookup not in aliases,"Original fallback branch requires exact lookup miss")
  candidates=[]
  for key,value in aliases.items():
   if isinstance(key,tuple)and len(key)==3 and isinstance(key[0],str)and Path(key[0])==NAMED:
    need(isinstance(value,dict)and {"path","bytes","sha256"}<=value.keys(),"Actual SOURCE-only alias physical shape required")
    need(isinstance(value["path"],str)and Path(value["path"]).is_absolute()and type(value["bytes"])is int and value["bytes"]>=0 and isinstance(value["sha256"],str)and re.fullmatch("[0-9a-f]{64}",value["sha256"])is not None and all(isinstance(k,str)for k in value),"Actual SOURCE-only alias scalar3 shape required")
    physical={k:value[k]for k in["path","bytes","sha256"]}
    candidates.append(dict(original_lookup_key=list(key),physical=physical,physical_extra_keys_as_scalars=sorted(k for k in value if k not in physical)))
  candidates.sort(key=lambda x:(x["original_lookup_key"][0],x["original_lookup_key"][1],x["original_lookup_key"][2]))
  allocation=af["allocation"];row=allocation["numeric_sacct_row"]
  need(allocation["job_id"]==jid and allocation["allocated_CPUs"]==1 and allocation["allocated_gpus"]==0 and len(row)==6 and row[:2]==[jid,"RUNNING"]and row[3:]==["u21111210118","u21111210118","organ"],"Actual fresh unchanged library CPU1/GPU0 descriptor required")
  tres(row[2])
  observer_readback()
  obj=dict(schema="root-fixed-source-byte-identity-failure-observation.v1",status="ACTUAL_FIXED_SOURCE_BYTE_IDENTITY_EXCEPTION_FRAME_OBSERVED_DIAGNOSTIC_ONLY_NOT_SOURCE_ACCEPTANCE",actual_job_id=jid,original_failure_job_id_as_scalar="16700",original16700_failed_expected_receipt_context_still_unobserved=True,allocation=allocation,current_actual_readiness=read_json(D/"readiness.json"),actual_failing_receipt=failed_receipt,actual_receipt_extra_keys_as_scalars=receipt_extra_keys,actual_verified_physical_path_as_scalar=str(vf["p"]),actual_parent_as_scalar=parent,actual_field_trail=list(trail),actual_module=module,actual_failed_stage=af["stage"],actual_exact_alias_lookup_key=list(lookup),actual_exact_alias_lookup_present=False,actual_existing_fixed_SOURCE_alias_entries=candidates,failed_resolve_branch="ORIGINAL_VERIFY_AFTER_EXACT_ALIAS_LOOKUP_MISS",failed_resolve_did_not_return_a_basis=True,qualified_exception_frames=[dict(function=fn,line=ln,path=str(AUX_MAIN))for fn,ln,frame in frames],reason_type=type(original_error).__name__,reason=str(original_error),fixed_SOURCE_actual_cpu_own_tuple=named_actual,fixed_SOURCE_metadata_before=named_before,fixed_SOURCE_metadata_after=md(NAMED),fixed_SOURCE_mode_not_changed=True,diagnostic_runpy_argv=argv,expected_original_exception_will_be_reraised=True,software_acceptance=SOFTWARE,source_files=expected_frozen,original_executing_sources=expected_original,source_metadata_before=source_before,actual_aux_source_files=actual_aux,actual_aux_metadata_before=aux_metadata,software_control_receipts=software_controls,software_control_metadata_before=software_before,control_receipts=control_receipts,control_metadata_before=control_before,conditional_core_runtime=runtime,source12_software4_controls11_Core_and_fixed_SOURCE_pre_end_afteroutput_bound=True,Worker_or_scientific_parent_or_child_bytes_read_or_hashed_by_observer=False,reader_or_Source_algorithm_or_alias_or17_permission_changed=False,Source_acceptance=False,source_staged=False,published=False,ACTIVE_changed=False,own_created_controls_LATE_Composer_not_own_Plan_prerequisites=True)
  descriptor=write_observation("observation.json",obj)
  observer_readback()
  need([readonly(x["path"],x)[1]for x in actual_aux]==aux_metadata,"Actual frozen AUX source6 changed after observer output")
  OBS.chmod(0o555)
  need(readonly(descriptor["path"],descriptor)[0]==descriptor and read_json(descriptor["path"])==obj,"Final readonly full observation reread differs")
  observer_readback()
  need([readonly(x["path"],x)[1]for x in actual_aux]==aux_metadata,"Actual frozen AUX source6 changed after final readonly observation reread")
  print(json.dumps(dict(status=obj["status"],observation=descriptor,actual_failing_receipt=failed_receipt,actual_verified_physical_path_as_scalar=str(NAMED),actual_parent_as_scalar=parent,actual_field_trail=list(trail),actual_module=module,fixed_SOURCE_actual_cpu_own_tuple=named_actual,diagnostic_control_human=control_receipts[9]),sort_keys=True),flush=True)
 except BaseException as qualification_error:
  try:
   write_observation("diagnostic_unqualified.json",dict(schema="root-fixed-source-byte-observer-unqualified.v1",status="DIAGNOSTIC_OBSERVER_NOT_QUALIFIED_NO_SOURCE_ACCEPTANCE",actual_job_id=jid,original_reason_type=type(original_error).__name__,original_reason=str(original_error),guard_reason_type=type(qualification_error).__name__,guard_reason=str(qualification_error),source_staged=False,published=False,ACTIVE_changed=False))
   OBS.chmod(0o555)
  except BaseException as writer_error:print("Diagnostic writer failure: "+repr(writer_error),file=sys.stderr,flush=True)
  print("DIAGNOSTIC_OBSERVER_NOT_QUALIFIED: "+repr(qualification_error),file=sys.stderr,flush=True)
 raise
else:
 write_observation("diagnostic_unqualified.json",dict(schema="root-fixed-source-byte-observer-unqualified.v1",status="EXPECTED_FIXED_SOURCE_FAILURE_DID_NOT_OCCUR_NOT_SOURCE_ACCEPTANCE",actual_job_id=jid,source_staged=False,published=False,ACTIVE_changed=False))
 OBS.chmod(0o555)
 raise SystemExit(86)

ROOT_FIXED_SOURCE_BYTE_IDENTITY_OBSERVER_REV1
