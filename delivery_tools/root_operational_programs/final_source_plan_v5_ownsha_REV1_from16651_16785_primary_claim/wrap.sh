exec /bin/bash -c 'set -euo pipefail
unset PYTHONPATH
export CUDA_VISIBLE_DEVICES='\'''\'' JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python -B - <<'\''ROOT_FIXED_PLAN_V5_OWN_SHA_REV1_PY'\''
import os, sys, json, re, stat, time, datetime, subprocess
from pathlib import Path
S = Path("/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery")
jid = os.environ.get("SLURM_JOB_ID", "")
if not re.fullmatch("[0-9]+", jid):
    raise SystemExit("Current owned Slurm job ID required")
expected_env = {"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
if any(os.environ.get(k) != v for k, v in expected_env.items()) or "PYTHONPATH" in os.environ:
    raise SystemExit("Original CPU/import/thread isolation required")
D = S / "submissions" / ("source_plan_v5_ownsha_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_source_plan_v5_ownsha_cpu", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:10:00", "MinMemoryNode": "8G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/8G10/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-plan-v5-own-sha-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_PLAN_V5_OWN_SHA_CAPTURE_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "capture_program_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_PLAN_V5_OWN_SHA_CAPTURE_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_PLAN_V5_OWN_SHA_CAPTURE_NOT_EXECUTED"
obj = {"schema": "root-current-owned-plan-v5-own-sha-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
       "current_scontrol_observation": ctl_saved, "current_scontrol_TRES": current_tres,
       "all_present_scontrol_TRES_fields_CPU1_GPU0": current_tres_fields, "attempts": attempts,
       "selected_actual_attempt": selected, "maximum_attempts": 30, "maximum_wait_seconds": 60,
       "environment": {"TZ": "UTC", "SLURM_TIME_FORMAT": "standard", **expected_env},
       "requested_GPUs": 0, "current_allocation_only_no_historical_GPU_inference": True,
       "no_source_or_request_hashes_or_imports_or_tests_by_wait": True,
       "unchanged_library_cpu_guard_will_freshly_requery": True, "actual_queries_not_proxy_or_synthesized_replies": True,
       "capture_program_entered": False, "original15201_specific_cause_proven": False,
       "additional_pin_or_source_audit_stage_Git_ACTIVE_acceptance": False}
persist("readiness.json", (json.dumps(obj, indent=2) + "\n").encode()); D.chmod(0o555)
if selected is None:
    raise SystemExit(72)
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "fixed_control_capture_next_not_acceptance": True}), flush=True)




import hashlib
R=Path("/lustre/users/u21111210118/projects/test9")
G=S/"runs/final_source_finite_worker_alias_software_16651/runner"
P=S/"pending/final_source_closure_v3_fixturefix4_finite_worker_alias1"
CORE=R/"env/core/bin/python"; REAL=CORE.with_name("python3.11")
SOFTWARE=dict(path=str(S/"runs/final_source_finite_worker_alias_software_16651/acceptance.json"),bytes=6590,sha256="5a8bfa759754985cd72bd35cb50192eb2aefef0df3fc73c28aebd4aed00adfe5")
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
need(sys.flags.optimize==0 and sys.flags.isolated==0 and sys.dont_write_bytecode,"Unoptimized CORE-B without -I and no bytecode required")
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


# Fixed own-control operational capture. No scientific receipt child I/O.
PLAN=S/"pending/final_source_plan_from14706_14925_16651_16785_v5/final_source_plan.json"
HANDOFF=PLAN.with_name("HANDOFF.md")
ROOTDOC=S/"handoffs/ROOT_FIXED_NEW_PLAN_V5_OWN_SHA_AND_SUPPLEMENTAL_SOURCE_CONTROL_CAPTURE_FROM16651_16785_20261015_REV1.md"
OLDPLAN=S/"pending/final_source_plan_from14706_14925_16651_16671_v4/final_source_plan.json"
OLDHANDOFF=OLDPLAN.with_name("HANDOFF.md")
OBS=S/"submissions/source_supplemental_test_identity_failure_observer_16785/observation.json"
TERMINAL=S/"submissions/final_source_supplemental_test_observer16785_actual_failed_diagnostic_terminal_metadata_seal/receipt.json"
PLANRO=S/"submissions/final_source_plan_v5_from16651_16785_metadata_readonly_seal/receipt.json"
BASEI=S/"runs/source_refresh_relative_v10_13316/source_inclusion_v3.json"
PRIORI=S/"runs/handoff_13225/source_inclusion_v2.json"
SWTERMINAL=S/"submissions/final_source_finite_worker_alias_software16651_actual_terminal_metadata_seal/receipt.json"
BASEPIN=dict(path=str(BASEI),bytes=784715,sha256="8909e49a5a5396827135e9492af393bdc369e2a28d766cc8767ff24f03914f6a")
PRIORPIN=dict(path=str(PRIORI),bytes=157235,sha256="be0710a2e2f21896c0698aae493478b41f4f82257e7ce7289577387d75968dcb")
OLDPLANPIN=dict(path=str(OLDPLAN),bytes=1941606,sha256="b7a8c58b5794ab9b221a70e46fc47614395af20b1fb3f32ef86bd507e387bf30")
OLDHPIN=dict(path=str(OLDHANDOFF),bytes=44899,sha256="1d3ad683a6707b62dbab96ec37e0418ea350f7181a60a581c138363b930dd76f")
OBSPIN=dict(path=str(OBS),bytes=52486,sha256="ca431a0eb8620e58604dae9e629f63600ff0a1f3f2a2eba64d3eb8d320e98695")
oldmain=dict(path=str(S/"runs/source_refresh_relative_v10_13316/readonly_source_bytes/4a4b588a3d992a75be70aaad614a930a52280bdd8e127bb8a7b178554c52f1d8_bindcraft_supplemental_stage_coverage.py"),bytes=22798,sha256="4a4b588a3d992a75be70aaad614a930a52280bdd8e127bb8a7b178554c52f1d8")
oldtest=dict(path=str(S/"runs/source_refresh_relative_v10_13316/readonly_source_bytes/11546e06354e914926820a2dbb0c74cf73e2d5762d383e3fba355413748db334_test_bindcraft_supplemental_stage_coverage.py"),bytes=5446,sha256="11546e06354e914926820a2dbb0c74cf73e2d5762d383e3fba355413748db334")
controls=[PLAN,HANDOFF,ROOTDOC,OLDPLAN,OLDHANDOFF,OBS,TERMINAL,PLANRO,BASEI,PRIORI,Path(oldmain["path"]),Path(oldtest["path"]),SWTERMINAL]
need(len(controls)==len(set(controls))==13,"Exact thirteen distinct own controls required")
before=[readonly(p)[1]for p in controls]
receipts=[readonly(p)[0]for p in controls]
for pin in [OLDPLANPIN,OLDHPIN,OBSPIN,BASEPIN,PRIORPIN,oldmain,oldtest]:
 need(receipts[controls.index(Path(pin["path"]))]==pin,"Fixed qualified control own bytes differ")
need(before[6]["bytes"]==1251905 and before[6]["inode"]==144115643443091491 and before[6]["mtime_ns"]==before[6]["ctime_ns"]==1792075467000000000,"Actual16785 failed terminal seal required")
need(before[7]["bytes"]==146143 and before[7]["inode"]==144115643443091578 and before[7]["mtime_ns"]==before[7]["ctime_ns"]==1792077032000000000,"Actual PlanV5 readonly seal required")
need(before[12]["bytes"]==37513 and before[12]["inode"]==144115643443090816 and before[12]["mtime_ns"]==before[12]["ctime_ns"]==1792061818000000000,"Actual16651 software terminal seal required")
planro=read_json(PLANRO)
need(planro["schema"]=="root-new-plan-v5-metadata-readonly-seal.v1"and planro["status"]=="ROOT_NEW_PLAN_V5_WHOLE_STATIC_AND_METADATA_RO_PASS_NOT_CPU_OWN_SHA_OR_SOURCE_ACCEPTANCE"and planro["Root_and_two_independent_whole_Plan_and_HANDOFF_static_PASS"]is True,"Actual Root+two reviewed PlanV5 RO control required")
need(planro["after_files"]==before[:2]and planro["after_directory"]==md(PLAN.parent),"Actual Plan/Handoff/directory full stable metadata required")
need(before[0]["bytes"]==1942962 and before[0]["inode"]==144115643443091539 and before[1]["bytes"]==20566 and before[1]["inode"]==144115643443091540,"Exact actual reviewed Plan/Handoff identity required")
plan_directory_before=md(authority(PLAN.parent))
need(stat.S_IMODE(plan_directory_before["mode"])==0o555 and {x.name for x in PLAN.parent.iterdir()}=={"final_source_plan.json","HANDOFF.md"},"Exact readonly two-file Plan namespace required")
protected=planro["protected_inputs_after"];protected_dirs=planro["protected_directories_after"]
need(protected==planro["protected_inputs_before"]and protected_dirs==planro["protected_directories_before"]and len(protected)==113 and len(protected_dirs)==46,"Whole finite PlanRO protected metadata required")
def protected_metadata_readback():
 for row in protected+protected_dirs:
  authority(row["path"]);need(md(row["path"])==row,"Preserved finite protected metadata differs")
 need(md(PLAN.parent)==plan_directory_before,"Plan directory drift")
protected_metadata_readback()
need(planro["conditional_CORE_metadata_after"]==[md(CORE),md(REAL)],"PlanRO/current CORE metadata differs")
obs=read_json(OBS);terminal=read_json(TERMINAL)
need(obs["schema"]=="root-fixed-source-byte-identity-failure-observation.v1"and obs["status"]=="ACTUAL_FIXED_SOURCE_BYTE_IDENTITY_EXCEPTION_FRAME_OBSERVED_DIAGNOSTIC_ONLY_NOT_SOURCE_ACCEPTANCE"and obs["actual_job_id"]=="16785","Qualified actual diagnostic control required")
need(obs["allocation"]["job_id"]=="16785"and obs["allocation"]["allocated_CPUs"]==1 and obs["allocation"]["allocated_gpus"]==0 and obs["Source_acceptance"]is False and obs["original16762_failed_expected_receipt_context_still_unobserved"]is True,"Distinct16785 diagnostic-only/currentGPU0 qualification required")
need(obs["software_acceptance"]==SOFTWARE and obs["source_files"]==expected_frozen and obs["original_executing_sources"]==expected_original and obs["source_metadata_before"]==source_before and obs["conditional_core_runtime"]==runtime,"Actual diagnostic/source12/SWA/Core basis required")
need(terminal["schema"]=="root-fixed-supplemental-test-source-observer-failed-diagnostic-terminal-metadata-seal.v1"and terminal["status"]=="ACTUAL16785_FIXED_SOURCE_IDENTITY_DIAGNOSTIC_AND_FAILED_TERMINAL_METADATA_READBACK_PASS_NOT_SOURCE_ACCEPTANCE"and terminal["actual_observation"]==OBSPIN and terminal["actual_job_id"]=="16785","Actual diagnostic failed terminal own control required")
tr=terminal["fresh_terminal"]
need(tr["returncode"]==0 and tr["actual_row"]==["16785","FAILED","1:0","145","1","test9_final_source_supplemental_test_observer_v6","u21111210118","u21111210118","organ"]and tr["stdout"]=="|".join(tr["actual_row"])+"\n" and tr["stderr"]=="","Exact saved actual FAILED145 terminal required")
need(terminal["actual_GPU0_basis"]==obs["allocation"]and terminal["Source_acceptance"]is False and terminal["Root_whole_saved_content_and_final_stdout_READBACK_PASS"]is True and terminal["actual_mandatory122_contracts_saved_PASS"]is True,"Actual terminal diagnostic qualifier required")
need(terminal["final_actual_CPU_stdout_descriptor"]["observation"]==OBSPIN,"Actual final CPU observation descriptor required")
swseal=read_json(SWTERMINAL)
need(swseal["schema"]=="final-source-finite-worker-alias-software-terminal-metadata-seal.v1"and swseal["status"]=="ACTUAL122_SOFTWARE_CONTENT_AND_TERMINAL_METADATA_READBACK_PASS_NOT_SOURCE_PRODUCTION_ACCEPTANCE"and swseal["actual_job_id"]=="16651"and swseal["actual_software_acceptance"]==SOFTWARE and swseal["tests"]==122,"Actual122 software terminal control differs")
base=read_json(BASEI);prior=read_json(PRIORI);old=read_json(OLDPLAN);plan=read_json(PLAN)
need(base["prior_inclusion"]==PRIORPIN and len(base["files"])==683 and prior["schema"]=="benchmark-source-inclusion.v2"and prior["status"]=="SOURCE_INCLUSION_AUDIT_PASS"and prior["applied"]is False and len(prior["files"])==322,"Actual accepted Base683/direct prior322 control relation required")
need(base["files"][79]["source"]==oldmain and base["files"][30]["source"]==oldtest and base["files"][79]["kind"]=="IMPLEMENTATION"and base["files"][30]["kind"]=="TEST","Exact historical Source row identities required")
def exact_receipt(r):
 need(type(r)is dict and set(r)=={"path","bytes","sha256"}and type(r["path"])is str and Path(r["path"]).is_absolute()and type(r["bytes"])is int and r["bytes"]>=0 and type(r["sha256"])is str and re.fullmatch("[0-9a-f]{64}",r["sha256"]),"Exact own receipt3 required")
 return r
def identity(r):
 exact_receipt(r);return(r["path"],r["sha256"],r["bytes"])
def fingerprint(r):return(r["bytes"],r["sha256"])
logicalmain=prior["files"][35]["source"];logicaltest=prior["files"][89]["source"]
need(logicalmain==dict(path=str(R/"steps/21_method_runtime/code/bindcraft_supplemental_stage_coverage.py"),bytes=22798,sha256=oldmain["sha256"])and logicaltest==dict(path=str(R/"steps/21_method_runtime/code/test_bindcraft_supplemental_stage_coverage.py"),bytes=5446,sha256=oldtest["sha256"]),"Exact priorI35/89 canonical historical receipts required")
newaliases=[dict(logical=logicalmain,physical=oldmain),dict(logical=logicaltest,physical=oldtest)]
need(type(plan)is dict and list(plan)==list(old)and len(plan)==34 and plan["aliases"]==old["aliases"]+newaliases and len(plan["aliases"])==5,"Only original ordered3 plus two explicit historical aliases allowed")
rewound=dict(plan);rewound["aliases"]=old["aliases"]
def exact_object(a,b):
 need(type(a)is type(b),"Control value type differs")
 if type(a)is dict:
  need(list(a)==list(b),"Control key order differs")
  for k in a:exact_object(a[k],b[k])
 elif type(a)is list:
  need(len(a)==len(b),"Control list length differs")
  for x,y in zip(a,b):exact_object(x,y)
 else:need(a==b,"Control scalar differs")
exact_object(rewound,old)
need((json.dumps(rewound,indent=2,ensure_ascii=False)+"\n").encode()==OLDPLAN.read_bytes(),"All unchanged fields and actual original serialization required")
roles=["formal13260_terminal_v3","native74_cache_catalog","native74_cache_binding","reference_free_e2e","formal_common_review","independent_statistics","scientific_report","final_delivery_tools","default_workflow_integration"]
need(plan["schema"]=="final-source-closure-plan.v3"and plan["root_owned"]is True and plan["public_source_only"]is True and plan["no_scientific_settings_change"]is True and plan["library_software_acceptance"]==SOFTWARE,"Exact actual reviewed Plan schema/flags/currentsoftware required")
need([m["role"]for m in plan["modules"]]==roles and len(plan["context_parent_seeds"])==17 and sum(len(m["sources"])for m in plan["modules"])==638 and sum(len(m["seeds"])for m in plan["modules"])==3809 and len(plan["plan_v3_original_source_provenance"])==61 and len(plan["late_Composer_control_history_from16454"])==83,"All9roles/17/638Source/3809Seeds/61/83 preserved")
need(obs["actual_failing_receipt"]==logicaltest and obs["actual_parent_as_scalar"]==str(PRIORI)and obs["actual_field_trail"]==["files","89","source"]and obs["actual_module"]=="default_workflow_integration"and obs["actual_failed_stage"]=="recursive_exact_new_dependencies","Exact16785 observed context required; no16762 retroactive claim")
# Pure finite projection, no closure/worker/scientific control read or child access.
def projected(aliases):
 lookup={}
 def add(logical,physical):
  k=identity(logical);identity(physical);need(fingerprint(logical)==fingerprint(physical),"Alias changes bytes")
  if k in lookup:need(fingerprint(lookup[k])==fingerprint(physical),"Conflicting exact alias")
  lookup[k]=physical
 for row in base["files"]:add(row["original_source"],row["source"])
 for a in aliases:add(a["logical"],a["physical"])
 missed=[i for i,row in enumerate(prior["files"])if identity(row["source"])not in lookup]
 return dict(prior_row_n=len(prior["files"]),alias_hit_n=len(prior["files"])-len(missed),ordinary_strict_row_indices=missed)
projection_old=projected(old["aliases"]);projection_new=projected(plan["aliases"])
need(projection_old==dict(prior_row_n=322,alias_hit_n=318,ordinary_strict_row_indices=[31,35,87,89])and projection_new==dict(prior_row_n=322,alias_hit_n=320,ordinary_strict_row_indices=[31,87]),"Exact finite322 prior control alias projection differs")
canonical=[Path(prior["files"][i]["source"]["path"])for i in [31,35,87,89]]
canonical_before=[md(authority(p))for p in canonical]
need(canonical_before==planro["current_fixed_canonical_Source4_metadata_after"],"Exact reviewed canonical four Source metadata required")
for a in canonical_before:need(stat.S_ISREG(a["mode"])and stat.S_IMODE(a["mode"])==0o664 and a["nlink"]==1,"Current canonical Source664 single-link retained required")
canonical_expected=[prior["files"][31]["source"],base["files"][316]["original_source"],prior["files"][87]["source"],base["files"][380]["original_source"]]
need([p.as_posix()for p in canonical]==[r["path"]for r in canonical_expected],"Fixed canonical row identities differ")
canonical_receipts=[record(p)for p in canonical]
need(canonical_receipts==canonical_expected and [md(p)for p in canonical]==canonical_before,"Actual ordinary31/87 SHA and current35/89 Source identities required")
# Only now import exact qualified source. No audit/compiler/contracts/tests called.
import importlib.util
spec=importlib.util.spec_from_file_location("root_fixed_plan_v5_ownsha_lib",G/"final_source_closure.py")
lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib)
allocation=lib.cpu()
need(allocation["job_id"]==jid and allocation["allocated_CPUs"]==1 and allocation["allocated_gpus"]==0 and allocation["numeric_sacct_row"]==attempts[selected-1]["actual_row"],"Fresh actual qualified current exactCPU1/GPU0 row required")
tres(allocation["numeric_sacct_row"][2])
lib.software_shape(swa,ct);lib.software_snapshot_shape(swa,snapshot)
need(lib.conditional_core_runtime()==runtime,"Actual qualified/current CORE differs")
for m in plan["modules"]:
 lib.receipt_shape(m["gate"]["receipt"])
 for row in m["sources"]:lib.receipt_shape(row["receipt"])
 for receipt in m["seeds"]:lib.receipt_shape(receipt)
for receipt in plan["context_parent_seeds"]:lib.receipt_shape(receipt)
for a in plan["aliases"]:
 exact_receipt(a["logical"]);exact_receipt(a["physical"]);lib.receipt_shape(a["logical"]);lib.receipt_shape(a["physical"])
for r in receipts+canonical_receipts:exact_receipt(r)
need([lib.rec(p)for p in controls]==receipts and [lib.rec(p)for p in canonical]==canonical_receipts,"Actual qualified rec own-byte descriptors required")
def final_readback():
 need([readonly(p)[0]for p in controls]==receipts and [md(p)for p in controls]==before,"All13 own controls bytes/metadata changed")
 need([md(p)for p in canonical]==canonical_before and [record(p)for p in canonical]==canonical_receipts and [md(p)for p in canonical]==canonical_before,"All4 canonical ownbytes/metadata changed")
 need([readonly(r["path"],r)[1]for r in sources]==source_before and [md(P),md(G)]==source_directories_before,"Actual original+frozen Source12/dirs changed")
 need([readonly(r["path"],r)[1]for r in software_controls]==software_before,"Actual software4 changed")
 protected_metadata_readback();core_readback()
final_readback()
OUT=authority(S/"runs")/("final_source_plan_v5_ownsha_"+jid)
need(not OUT.exists()and not OUT.is_symlink(),"Exclusive absent V5 ownSHA output required")
OUT.mkdir(mode=0o755,exist_ok=False)
out=dict(schema="root-new-plan-v5-own-sha-and-fixed-source-control-capture.v1",status="ACTUAL_NEW_PLAN_V5_OWN_SHA_AND_FIXED_SUPPLEMENTAL_SOURCE_CONTROL_BYTES_CPU_CAPTURED_NOT_SOURCE_AUDIT_STAGE_OR_SCIENCE",actual_job_id=jid,allocation=allocation,current_actual_readiness=obj,plan=receipts[0],handoff=receipts[1],root_control_human=receipts[2],control_receipts=receipts,control_metadata_before=before,control_metadata_after=[md(p)for p in controls],current_canonical_Source4_receipts=canonical_receipts,current_canonical_Source4_metadata_before=canonical_before,current_canonical_Source4_metadata_after=[md(p)for p in canonical],historical_two_exact_global_aliases=newaliases,finite_prior322_projection_before=projection_old,finite_prior322_projection_after=projection_new,ordinary31_87_actual_CPU_byte_identity_PASS=True,all_other_Plan_fields_types_order_and_serialized_bytes_unchanged=True,original_ordered3_aliases_preserved=True,software_acceptance=SOFTWARE,source_files=expected_frozen,original_executing_sources=expected_original,source_metadata_original_before=source_before[:6],source_metadata_frozen_before=source_before[6:],software_control_receipts=software_controls,software_control_metadata_before=software_before,software_control_metadata_after=[md(r["path"])for r in software_controls],conditional_core_runtime=runtime,plan_directory_metadata_before=plan_directory_before,plan_directory_metadata_after=md(PLAN.parent),all_Source12_SW4_Core_controls13_Source4_and_metadata_finite113dirs46_pre_end_afteroutput_finalreadonly_bound=True,plan_child_receipts_shape_only_no_child_IO=True,saved_control_receipts_ownbytes_only_no_child_IO=True,original16762_failure_context_still_unobserved=True,alias35_prospective_history_not_observed_failure=True,alias89_actual16785_context_distinct_from_original16762=True,scientific_receipt_children_read_or_hashed=False,compiler_or_tests_or_new_software_qualification_executed=False,historical_Slurm_queried=False,source_audit_executed=False,source_staged=False,published=False,ACTIVE_changed=False,own_created_controls_LATE_COMPOSER_ONLY_NOT_PLAN_PREREQUISITES=True)
data=(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode("utf-8");path=OUT/"capture.json"
with path.open("xb")as f:f.write(data);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
descriptor=lib.rec(path);out_metadata=md(path)
need(path.read_bytes()==data and read_json(path)==out and stat.S_IMODE(out_metadata["mode"])==0o444 and out_metadata["nlink"]==1,"Actual capture full ownbytes reread required")
final_readback();OUT.chmod(0o555)
fd=os.open(str(OUT),os.O_RDONLY)
try:os.fsync(fd)
finally:os.close(fd)
need(path.read_bytes()==data and read_json(path)==out and lib.rec(path)==descriptor and md(path)==out_metadata and stat.S_IMODE(md(OUT)["mode"])==0o555,"Final readonly capture whole reread required")
final_readback()
print(json.dumps(dict(status=out["status"],capture=descriptor,plan=receipts[0],handoff=receipts[1],root_control_human=receipts[2],current_canonical_Source4_receipts=canonical_receipts),sort_keys=True),flush=True)

ROOT_FIXED_PLAN_V5_OWN_SHA_REV1_PY
'