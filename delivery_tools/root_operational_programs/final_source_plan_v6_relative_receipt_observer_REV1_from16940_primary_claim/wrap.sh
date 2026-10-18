exec /bin/bash -c 'set -euo pipefail
unset PYTHONPATH
export CUDA_VISIBLE_DEVICES='\'''\'' JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python -B - <<'\''ROOT_RELATIVE_RECEIPT_OBSERVER_V6_PY'\''
import os, sys, json, re, stat, time, datetime, subprocess
from pathlib import Path
S = Path("/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery")
jid = os.environ.get("SLURM_JOB_ID", "")
if not re.fullmatch("[0-9]+", jid):
    raise SystemExit("Current owned Slurm job ID required")
expected_env = {"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
if any(os.environ.get(k) != v for k, v in expected_env.items()) or "PYTHONPATH" in os.environ:
    raise SystemExit("Original CPU/import/thread isolation required")
D = S / "submissions" / ("source_relative_receipt_observer_v6_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_source_relative_receipt_observer_v6", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:30:00", "MinMemoryNode": "16G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/16G30/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-relative-receipt-observer-v6-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_RELATIVE_RECEIPT_OBSERVER_V6_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "production_audit_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_RELATIVE_RECEIPT_OBSERVER_V6_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_RELATIVE_RECEIPT_OBSERVER_V6_NOT_EXECUTED"
obj = {"schema": "root-current-owned-relative-receipt-observer-v6-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
need(sys.flags.optimize==0 and sys.flags.isolated==0 and sys.dont_write_bytecode,"Assertions and qualified strict verification must remain enabled")
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

# Fixed Plan/control qualification prelude; production follows only after all gates.
PLAN=S/"pending/final_source_plan_from14706_14925_16651_16847_v6/final_source_plan.json"
HANDOFF=PLAN.with_name("HANDOFF.md")
ROOTDOC=S/"handoffs/ROOT_FIXED_PLAN_V6_OWN_SHA_FROM16651_RECOVERED16847_20261015_REV1.md"
PLANRO=S/"submissions/final_source_plan_v6_from16651_16847_metadata_readonly_seal/receipt.json"
OLDPLAN=S/"pending/final_source_plan_from14706_14925_16651_16785_v5/final_source_plan.json"
OLDHANDOFF=OLDPLAN.with_name("HANDOFF.md")
CAP=S/"runs/historical_source2_byte_recovery_16847/capture.json"
CAPRO=S/"submissions/historical_source2_recovery16847_actual_terminal_metadata_seal/receipt.json"
CAPPIN=dict(path=str(CAP),bytes=71545,sha256="4d19a6da7da578f68dab38d80e617acda682827889d2518afda03a7587bfec66")
OLDPIN=dict(path=str(OLDPLAN),bytes=1942962,sha256="fa04bb5d1f0155659577cf2270c02ecd7ec42682e184707d5dd71c313c9e37fb")
OLDHPIN=dict(path=str(OLDHANDOFF),bytes=20566,sha256="d0f82b78557952a79a84294b4abd90ecd2de3211aa7efc3be090cef87a325ef8")
recovered=[dict(path=str(S/"runs/historical_source2_byte_recovery_16847/recovered_sources/bc_supplemental_gpu_launcher.sh"),bytes=2225,sha256="75ee295f33b7e11ca48a9ea83ccd9f9bc79461c0b55f755b8e94391d026c7183"),dict(path=str(S/"runs/historical_source2_byte_recovery_16847/recovered_sources/supplemental_launcher_freeze.py"),bytes=1633,sha256="1d6ed0efed2d63b792cdae304ccc4017d7e3d9e254ff2d7b7c241abd5f0eeb01")]
cap_r,cap_md=readonly(CAP,CAPPIN);cap=read_json(CAP)
need(cap["schema"]=="root-fixed-historical-supplemental-source-byte-recovery.v1"and cap["status"]=="ACTUAL_EXACT_OLD31_87_SOURCE_BYTES_RECOVERED_FROM_RECORDED_CREATION_AND_FROZEN13222_CPU_VERIFIED_NOT_PLAN_OR_SOURCE_AUDIT_ACCEPTANCE"and cap["actual_job_id"]=="16847"and cap["allocation"]["allocated_CPUs"]==1 and cap["allocation"]["allocated_gpus"]==0 and cap["Plan_SHA_not_qualified"]is True,"Actual recovered Source2 control required, not Plan acceptance")
need(cap["recovered_historical_Source_receipts"]==recovered and cap["recovered_Source_never_imported_compiled_or_executed"]is True and cap["both_literal_expected_hashes_checked_BEFORE_any_Source_copy_created"]is True,"Exact old31/87 recovered Source2 required")
capro_r,capro_md=readonly(CAPRO);capro=read_json(CAPRO)
need(capro["schema"]=="root-historical-source2-recovery-terminal-metadata-seal.v1"and capro["actual_job_id"]=="16847"and capro["actual_capture"]==CAPPIN and capro["Root_and_two_independent_WHOLE_RECOVERY_CONTENT_READBACK_PASS"]is True and capro["fresh_terminal"]["returncode"]==0 and capro["fresh_terminal"]["actual_row"]==["16847","COMPLETED","0:0","5","1","test9_historical_source2_recovery_cpu","u21111210118","u21111210118","organ"]and capro["actual_allocation"]==cap["allocation"],"Actual full Root+two/COMPLETED terminal control required")
need(capro["recovered_historical_Source_receipts"]==recovered and capro["Plan_SHA_not_qualified"]is True and capro["Source_acceptance"]is False,"Recovery qualification must not become Plan or Source audit acceptance")
recm=[readonly(r["path"],r)[1]for r in recovered]
need(recm==cap["recovered_historical_Source_metadata_before"]==cap["recovered_historical_Source_metadata_after"]and md(Path(recovered[0]["path"]).parent)==cap["recovered_historical_Source_directory_metadata"],"Actual readonly recovered Source2 full metadata required")
controls=[PLAN,HANDOFF,ROOTDOC,PLANRO,CAP,CAPRO]+[Path(r["path"])for r in cap["control_receipts"]]+[Path(r["path"])for r in recovered]
need(len(controls)==len(set(controls))==30,"Exactly thirty finite own control/Source paths required")
receipts=[];before=[]
for p in controls:
 r,m=readonly(p);receipts.append(r);before.append(m)
need(receipts[4]==CAPPIN and receipts[5]==capro_r and receipts[6:28]==cap["control_receipts"]and receipts[28:]==recovered and receipts[6]==OLDPIN and receipts[7]==OLDHPIN,"Actual previously CPU-qualified finite controls required")
planro=read_json(PLANRO)
need(planro["schema"]=="root-new-plan-v6-metadata-readonly-seal.v1"and planro["Root_and_two_independent_whole_Plan_and_HANDOFF_static_PASS"]is True and planro["after_files"]==before[:2]and planro["after_directory"]==md(PLAN.parent),"Whole reviewed new Plan/H and actual readonly seal required")
protected=planro["protected_inputs_after"];protected_dirs=planro["protected_directories_after"]
need(protected==planro["protected_inputs_before"]and protected_dirs==planro["protected_directories_before"],"Exact finite PlanRO protected metadata required")
plan_dir=md(authority(PLAN.parent));rec_dir=md(authority(Path(recovered[0]["path"]).parent))
need(stat.S_IMODE(plan_dir["mode"])==0o555 and {p.name for p in PLAN.parent.iterdir()}=={"final_source_plan.json","HANDOFF.md"},"Exclusive exact readonly Plan2 namespace required")
def metadata_readback():
 for row in protected+protected_dirs:
  authority(row["path"]);need(md(row["path"])==row,"Preserved finite PlanRO metadata differs")
 need(md(PLAN.parent)==plan_dir and md(Path(recovered[0]["path"]).parent)==rec_dir,"Plan or recovered directory differs")
metadata_readback()
need(cap["source_files"]==expected_frozen and cap["original_executing_sources"]==expected_original and cap["software_acceptance"]==SOFTWARE and cap["conditional_core_runtime"]==runtime,"Actual recovered Source12/SW/Core relation required")
canonical=[Path(x["path"])for x in cap["current_canonical_Source4_receipts"]]
canonical_expected=cap["current_canonical_Source4_receipts"]
canonical_before=[md(authority(p))for p in canonical]
need(canonical_before==cap["current_canonical_Source4_metadata_before"]==cap["current_canonical_Source4_metadata_after"]and all(stat.S_IMODE(x["mode"])==0o664 and x["nlink"]==1 for x in canonical_before),"Actual current canonical4 unchanged metadata required")
need([record(p)for p in canonical]==canonical_expected and [md(p)for p in canonical]==canonical_before,"Actual current canonical4 own SHA must match16847, not historical old31/87")
old=read_json(OLDPLAN);plan=read_json(PLAN)
need(list(old)==list(plan)and len(plan)==34 and old["aliases"]==plan["aliases"][:5]and len(plan["aliases"])==7,"Original five ordered aliases preserved plus exact two required")
logical=cap["exact_historical_logical_receipts"]
need(plan["aliases"][5:]==[dict(logical=a,physical=b)for a,b in zip(logical,recovered)],"Exact full-identity old31/87 aliases required")
roles=["formal13260_terminal_v3","native74_cache_catalog","native74_cache_binding","reference_free_e2e","formal_common_review","independent_statistics","scientific_report","final_delivery_tools","default_workflow_integration"]
need([m["role"]for m in plan["modules"]]==roles and len(plan["context_parent_seeds"])==17 and plan["library_software_acceptance"]==SOFTWARE and plan["schema"]=="final-source-closure-plan.v3"and plan["root_owned"]is True and plan["public_source_only"]is True and plan["no_scientific_settings_change"]is True,"Nine exact roles/current122/17/schema unchanged")
extra=plan["modules"][8]["sources"][-2:]
for a,r in zip(extra,logical):
 need(a==dict(receipt=r,repository_relative="rebuild/benchmarks/20261011/exact_source_aliases/"+r["sha256"]+"_"+Path(r["path"]).name),"Deterministic exact old logical Source publication destination required")
rewound=json.loads(json.dumps(plan));rewound["aliases"]=old["aliases"];rewound["modules"][8]["sources"]=rewound["modules"][8]["sources"][:-2]
def same(a,b):
 need(type(a)is type(b),"Preserved Plan type changed")
 if type(a)is dict:
  need(list(a)==list(b),"Preserved Plan key order changed")
  for k in a:same(a[k],b[k])
 elif type(a)is list:
  need(len(a)==len(b),"Preserved Plan list length changed")
  for x,y in zip(a,b):same(x,y)
 else:need(a==b,"Preserved Plan scalar changed")
same(rewound,old)
need((json.dumps(rewound,indent=2,ensure_ascii=False)+"\n").encode()==OLDPLAN.read_bytes(),"Only four appended alias/Source objects; all other serialized bytes required")
need(sum(len(m["sources"])for m in plan["modules"])==640 and sum(len(m["seeds"])for m in plan["modules"])==3809 and len(plan["plan_v3_original_source_provenance"])==61 and len(plan["late_Composer_control_history_from16454"])==83,"640Source/3809Seed/61/83 retained")
base=read_json(controls[14]);prior=read_json(controls[15])
need(len(base["files"])==683 and len(prior["files"])==322,"Exact fixed683 and322 controls required")
def identity(r):
 need(type(r)is dict and set(r)=={"path","bytes","sha256"}and type(r["bytes"])is int and r["bytes"]>=0 and type(r["path"])is str and Path(r["path"]).is_absolute()and type(r["sha256"])is str and re.fullmatch("[0-9a-f]{64}",r["sha256"]),"Exact receipt3 shape required")
 return(r["path"],r["sha256"],r["bytes"])
lookup={}
for row in base["files"]:lookup[identity(row["original_source"])]=row["source"]
for a in plan["aliases"]:
 need(a["logical"]["bytes"]==a["physical"]["bytes"]and a["logical"]["sha256"]==a["physical"]["sha256"],"Exact alias fingerprint required")
 lookup[identity(a["logical"])]=a["physical"]
miss=[i for i,row in enumerate(prior["files"])if identity(row["source"])not in lookup]
need(miss==[],"All322 prior identities require actual explicit aliases or Base683 mapping")

# Bind the REAL16888 own-SHA success before the distinct strict13 production.
own_controls=controls[:];own_receipts=receipts[:];own_before=before[:]
EXPECTED30=[{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16651_16847_v6/final_source_plan.json","bytes":1945102,"sha256":"47edaaf8defff84762a7995621b2b308dc507837212f97ba5dfeb4ef6f6d8306"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16651_16847_v6/HANDOFF.md","bytes":16769,"sha256":"13d0f9659e9270c708e620535534251e4fab0ad77fa7b13dbbedc978ad95f5cf"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_PLAN_V6_OWN_SHA_FROM16651_RECOVERED16847_20261015_REV1.md","bytes":33380,"sha256":"3a00bf9d00a45c59058fbe270c7e8bf01af63e10c3d6694e7999b2b9d372e3b2"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v6_from16651_16847_metadata_readonly_seal/receipt.json","bytes":211559,"sha256":"97224d4b19775334d9b5cc73a89dcf55198b13eb3e948722b4c9485290cd0229"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/historical_source2_byte_recovery_16847/capture.json","bytes":71545,"sha256":"4d19a6da7da578f68dab38d80e617acda682827889d2518afda03a7587bfec66"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/historical_source2_recovery16847_actual_terminal_metadata_seal/receipt.json","bytes":222766,"sha256":"07730148034746f28cfe6116f6cfe8323736395225407d0664dcdd56bb0fd1cd"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16651_16785_v5/final_source_plan.json","bytes":1942962,"sha256":"fa04bb5d1f0155659577cf2270c02ecd7ec42682e184707d5dd71c313c9e37fb"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16651_16785_v5/HANDOFF.md","bytes":20566,"sha256":"d0f82b78557952a79a84294b4abd90ecd2de3211aa7efc3be090cef87a325ef8"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_NEW_PLAN_V5_OWN_SHA_AND_SUPPLEMENTAL_SOURCE_CONTROL_CAPTURE_FROM16651_16785_20261015_REV1.md","bytes":40985,"sha256":"f72f88e57814acafdc5a106053a3b9f3d0b3d30f0f0b5d047b499f6e689853e9"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16651_16671_v4/final_source_plan.json","bytes":1941606,"sha256":"b7a8c58b5794ab9b221a70e46fc47614395af20b1fb3f32ef86bd507e387bf30"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16651_16671_v4/HANDOFF.md","bytes":44899,"sha256":"1d3ad683a6707b62dbab96ec37e0418ea350f7181a60a581c138363b930dd76f"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/source_supplemental_test_identity_failure_observer_16785/observation.json","bytes":52486,"sha256":"ca431a0eb8620e58604dae9e629f63600ff0a1f3f2a2eba64d3eb8d320e98695"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_supplemental_test_observer16785_actual_failed_diagnostic_terminal_metadata_seal/receipt.json","bytes":1251905,"sha256":"355d7e45783e254b5345ad423295acb3a06f9b87f1bc9deddf701bc23fdf7a94"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v5_from16651_16785_metadata_readonly_seal/receipt.json","bytes":146143,"sha256":"80e8dddc8d1f150f6b14330458dca7efb0ca60247580d58487c53e55e455984e"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/source_inclusion_v3.json","bytes":784715,"sha256":"8909e49a5a5396827135e9492af393bdc369e2a28d766cc8767ff24f03914f6a"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/handoff_13225/source_inclusion_v2.json","bytes":157235,"sha256":"be0710a2e2f21896c0698aae493478b41f4f82257e7ce7289577387d75968dcb"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/readonly_source_bytes/4a4b588a3d992a75be70aaad614a930a52280bdd8e127bb8a7b178554c52f1d8_bindcraft_supplemental_stage_coverage.py","bytes":22798,"sha256":"4a4b588a3d992a75be70aaad614a930a52280bdd8e127bb8a7b178554c52f1d8"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/readonly_source_bytes/11546e06354e914926820a2dbb0c74cf73e2d5762d383e3fba355413748db334_test_bindcraft_supplemental_stage_coverage.py","bytes":5446,"sha256":"11546e06354e914926820a2dbb0c74cf73e2d5762d383e3fba355413748db334"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_finite_worker_alias_software16651_actual_terminal_metadata_seal/receipt.json","bytes":37513,"sha256":"253ec381053d2cf22ae70a6ccfbb18ef067e784dfe195a053c289e35474729c3"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_FOUR_SUPPLEMENTAL_SOURCE_BYTE_OBSERVER_FROM16651_16825_20261015.md","bytes":42980,"sha256":"2023181fd13e74418e3adb9ef7e7d7a515ed1880ea8d7ee762ad24ee518757cb"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/final_source_plan_v5_ownsha16825_actual_failed_terminal_metadata_seal/receipt.json","bytes":166814,"sha256":"d252c00e1c1ac32f780b1d19edd786ce3ade40b5691c743b4d05b6915ba9710b"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/root_fixed_new_plan_v5_ownsha_REV1_humans_metadata_readonly_seal/receipt.json","bytes":148285,"sha256":"55e326b1aa17727caf00637b80788ab63278b9f59af50bfda5216861ab37b77d"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/ROOT_FIXED_HISTORICAL_SUPPLEMENTAL_SOURCE_BYTES_RECOVERY_FROM13222_RECORD_16832_20261015.md","bytes":59511,"sha256":"6203693c552be93f40eac028d0f54471fa0065d1750b3981c3e757ad7d0bf4e1"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/fixed_source4_byte_observer_16832/capture.json","bytes":54746,"sha256":"bfb799d1bfdc3e058800bddd1f47d05a9a729e98caed81e2322de5faff3eb96f"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/fixed_four_source_byte_observer16832_actual_diagnostic_terminal_metadata_seal/receipt.json","bytes":194105,"sha256":"91e2ee7c545cd795dd8eb884623ab1d8e8f2b7dd6b4a30ee5f1ce788e19ac073"},{"path":"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/runs/supplemental_launcher_13222/outputs/acceptance.json","bytes":4110,"sha256":"4550459be83aac49aba1476ca3728b93bf3518fe43e5414610ffbe21796c7316"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/original_supplemental_launcher13222_control_metadata_readonly_seal/receipt.json","bytes":182981,"sha256":"291d1d8d4afa9a54ba0fbe653262dd2a4009b2133c1ab0e01c7443fd2211fc5a"},{"path":"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/frozen/supplemental_launcher_13222/gpu_launcher.sh","bytes":2225,"sha256":"75ee295f33b7e11ca48a9ea83ccd9f9bc79461c0b55f755b8e94391d026c7183"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/historical_source2_byte_recovery_16847/recovered_sources/bc_supplemental_gpu_launcher.sh","bytes":2225,"sha256":"75ee295f33b7e11ca48a9ea83ccd9f9bc79461c0b55f755b8e94391d026c7183"},{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/historical_source2_byte_recovery_16847/recovered_sources/supplemental_launcher_freeze.py","bytes":1633,"sha256":"1d6ed0efed2d63b792cdae304ccc4017d7e3d9e254ff2d7b7c241abd5f0eeb01"}]
need(own_receipts==EXPECTED30,"Literal actual16888 thirty input descriptors required")
PLANPIN=EXPECTED30[0];HANDOFFPIN=EXPECTED30[1]
OWNCAP=S/"runs/final_source_plan_v6_ownsha_16888/capture.json"
OWNCAPPIN=dict(path=str(OWNCAP),bytes=63237,sha256="2f81c4917d6ace34e21edf3374d3425488fa9c9194c18b8fc8c73b8b52d59ebd")
OWNTERMINAL=S/"submissions/final_source_plan_v6_ownsha16888_actual_terminal_metadata_seal/receipt.json"
REQUEST=S/"pending/final_source_context_request_from16651_16888_v6/request.json"
REQUESTMETA=REQUEST.with_name("request_metadata.json")
ROOTDOC=S/"handoffs/ROOT_FIXED_PLAN_V6_RELATIVE_RECEIPT_FAILURE_OBSERVER_FROM16940_20261015_REV1.md"
REQUESTRO=S/"submissions/final_source_context_request_from16651_16888_v6_metadata_readonly_seal/receipt.json"
FINITE_PAIRS=[{"logical":{"path":"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json","bytes":11279,"sha256":"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47"},"physical":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/readonly_source_bytes/43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47_manifest.json","bytes":11279,"sha256":"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47"}},{"logical":{"path":"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13168/acceptance.json","bytes":3201,"sha256":"62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142"},"physical":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/readonly_source_bytes/62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142_acceptance.json","bytes":3201,"sha256":"62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142"}},{"logical":{"path":"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13180/acceptance.json","bytes":3201,"sha256":"b459d255ec8df34729b186b48fca4c3ba4ce46115ba5e5ce419ddbdd46c514eb"},"physical":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/readonly_source_bytes/b459d255ec8df34729b186b48fca4c3ba4ce46115ba5e5ce419ddbdd46c514eb_acceptance.json","bytes":3201,"sha256":"b459d255ec8df34729b186b48fca4c3ba4ce46115ba5e5ce419ddbdd46c514eb"}},{"logical":{"path":"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061/source_bundle.json","bytes":8124,"sha256":"9b89ed8b673597002e6ce52cc6561e009ad2041a253b6484cfacaa7896c8c1e9"},"physical":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/readonly_source_bytes/9b89ed8b673597002e6ce52cc6561e009ad2041a253b6484cfacaa7896c8c1e9_source_bundle.json","bytes":8124,"sha256":"9b89ed8b673597002e6ce52cc6561e009ad2041a253b6484cfacaa7896c8c1e9"}},{"logical":{"path":"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/native_common_13022/source_bundle.json","bytes":10053,"sha256":"729e3acd0cd371cf2a4dd571850d241c4a9a0fb2470090b178f36d8bc058f500"},"physical":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/readonly_source_bytes/729e3acd0cd371cf2a4dd571850d241c4a9a0fb2470090b178f36d8bc058f500_source_bundle.json","bytes":10053,"sha256":"729e3acd0cd371cf2a4dd571850d241c4a9a0fb2470090b178f36d8bc058f500"}},{"logical":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_bbf_recorded_recovery_diagnostic_13313/diagnostic.json","bytes":34363,"sha256":"f77e8e0ec5331da3003349792dcb735f4d8836d014d7fa484e07321c1b3b5f3f"},"physical":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/readonly_source_bytes/f77e8e0ec5331da3003349792dcb735f4d8836d014d7fa484e07321c1b3b5f3f_diagnostic.json","bytes":34363,"sha256":"f77e8e0ec5331da3003349792dcb735f4d8836d014d7fa484e07321c1b3b5f3f"}},{"logical":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_missing_operative_inventory_13308/diagnostic.json","bytes":207548,"sha256":"2a22a7f4aa4a787f934b72a1fe7ec4bf84c1891c08944120093519d4b469ba11"},"physical":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/readonly_source_bytes/2a22a7f4aa4a787f934b72a1fe7ec4bf84c1891c08944120093519d4b469ba11_diagnostic.json","bytes":207548,"sha256":"2a22a7f4aa4a787f934b72a1fe7ec4bf84c1891c08944120093519d4b469ba11"}},{"logical":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_saved_byte_recovery_diagnostic_13310/diagnostic.json","bytes":75704,"sha256":"48ce0453db4927cacea9804354fc9b0f598ca598922ff778f0f2024debc4b1ea"},"physical":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/readonly_source_bytes/48ce0453db4927cacea9804354fc9b0f598ca598922ff778f0f2024debc4b1ea_diagnostic.json","bytes":75704,"sha256":"48ce0453db4927cacea9804354fc9b0f598ca598922ff778f0f2024debc4b1ea"}}]
MAPPERPIN=dict(path=str(S/"runs/exact_context_mapper_v4_13319/acceptance.json"),bytes=15049,sha256="a66b8186aa4ba2c737fe3e607f84bb90ecc35b35f271022bbcb66ac3cb327890")
MAPPERPROOFPIN=dict(path=str(S/"runs/exact_context_mapper_v4_13319/finite_source_read_view_proof.json"),bytes=766915,sha256="cfeee0eecbf012f14165c3d76990616b5cfa6ec42e7848c9bb4c67aa9caa58b7")
controls=[REQUEST,REQUESTMETA,ROOTDOC,REQUESTRO,OWNCAP,OWNTERMINAL]+own_controls+[Path(MAPPERPIN["path"]),Path(MAPPERPROOFPIN["path"])]+[Path(pair[k]["path"])for pair in FINITE_PAIRS for k in ["logical","physical"]]
need(len(controls)==len(set(controls))==54,"Exactly54 unique fixed own controls required")
control_rows=[readonly(p)for p in controls]
control_receipts=[r for r,m in control_rows];control_before=[m for r,m in control_rows]
need(control_receipts[4]==OWNCAPPIN and control_receipts[6:36]==EXPECTED30 and control_receipts[36:38]==[MAPPERPIN,MAPPERPROOFPIN],"Actual CPU-qualified descriptors/Source/Mapper controls required")
for i,pair in enumerate(FINITE_PAIRS):
 need(control_receipts[38+2*i:40+2*i]==[pair["logical"],pair["physical"]],"Whole fixed logical/physical parent own-byte tuples required")
need(control_before[0]["bytes"]==6549 and control_before[0]["inode"]==144115643443091842 and control_before[1]["bytes"]==22355 and control_before[1]["inode"]==144115643443091843 and all(control_before[i]["mtime_ns"]==1792082593000000000 and control_before[i]["ctime_ns"]==1792082868000000000 for i in [0,1]),"Actual reviewed readonly Q/M required")
need(control_before[3]["bytes"]==238870 and control_before[3]["inode"]==144115643443091928 and control_before[3]["mtime_ns"]==control_before[3]["ctime_ns"]==1792082868000000000,"Actual new strictQ RO control required")
need(control_before[5]["bytes"]==237589 and control_before[5]["inode"]==144115643443091834 and control_before[5]["mtime_ns"]==control_before[5]["ctime_ns"]==1792082422000000000,"Actual16888 fresh terminal RO control required")
q=read_json(REQUEST);prep=read_json(REQUESTMETA);own=read_json(OWNCAP);terminal=read_json(OWNTERMINAL);reqseal=read_json(REQUESTRO)
keys=["schema","root_owned","raw_JSON_rewrite_allowed","generic_relative_resolution_allowed","generic_external_resolution_allowed","library_software_acceptance","mapper_software_acceptance","final_source_plan","bbf_parent_aliases","historical_parent_aliases","recovered_parent_aliases","archive_parent_aliases","finite_source_parent_aliases"]
need(list(q)==keys and q["schema"]=="final-source-materialized-context-read-view-request.v3"and q["root_owned"]is True and all(q[k]is False for k in keys[2:5])and all(type(q[k])is list and not q[k]for k in keys[8:12])and q[keys[12]]==FINITE_PAIRS,"Exact strict13/threefalse/fourempty/finite8 required")
need(q["library_software_acceptance"]==SOFTWARE and q["mapper_software_acceptance"]==MAPPERPIN and q["final_source_plan"]==PLANPIN,"Actual qualified software122/Mapper/PlanV6 required")
need(own["schema"]=="root-fixed-source-plan-v6-own-sha-control-capture.v1"and own["status"]=="ACTUAL_NEW_PLAN_V6_OWN_SHA_AND_EXACT_RECOVERED_SOURCE_ALIASES_CPU_VERIFIED_NOT_SOURCE_AUDIT_ACCEPTANCE"and own["actual_job_id"]=="16888"and own["plan"]==PLANPIN and own["handoff"]==HANDOFFPIN,"Actual16888 Plan own-SHA capture required")
a=own["allocation"];rd=own["current_actual_readiness"];selected_old=rd["selected_actual_attempt"]
need(a["job_id"]=="16888"and type(a["allocated_CPUs"])is int and a["allocated_CPUs"]==1 and type(a["allocated_gpus"])is int and a["allocated_gpus"]==0 and a["numeric_sacct_row"][:2]==["16888","RUNNING"]and a["numeric_sacct_row"][3:]==["u21111210118","u21111210118","organ"],"Actual16888 RUNNING CPU1GPU0 basis required")
tres(a["numeric_sacct_row"][2])
need(rd["schema"]=="root-current-owned-plan-v6-ownsha-sacct-readiness.v1"and rd["status"]=="CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_PLAN_V6_OWN_SHA_NOT_YET_EXECUTED"and rd["actual_job_id"]=="16888"and type(selected_old)is int and 1<=selected_old<=len(rd["attempts"])and rd["attempts"][selected_old-1]["actual_row"]==a["numeric_sacct_row"]and rd["requested_GPUs"]==0 and rd["actual_queries_not_proxy_or_synthesized_replies"]is True,"Actual saved16888 readiness bound, no historical livequery")
need(own["control_receipts"]==EXPECTED30 and own["control_metadata_before"]==own["control_metadata_after"]==own_before and own["root_control_human"]==EXPECTED30[2],"Whole literal fixed30 capture/prepost/current required")
need(own["recovery_capture"]==CAPPIN and own["recovery_terminal_control"]==capro_r and own["exact_historical_logical_receipts"]==logical and own["recovered_historical_Source_receipts"]==recovered and own["recovered_historical_Source_metadata"]==recm,"Actual16847 recovered Source2/terminal relation required")
need(own["current_canonical_Source4_receipts"]==canonical_expected and own["current_canonical_Source4_metadata_before"]==own["current_canonical_Source4_metadata_after"]==canonical_before,"Currentcanonical4 bound toactual16847/16888, not historical SHA")
need(own["software_acceptance"]==SOFTWARE and own["source_files"]==expected_frozen and own["original_executing_sources"]==expected_original and own["source_metadata_original_before"]+own["source_metadata_frozen_before"]==source_before and own["software_control_receipts"]==software_controls and own["software_control_metadata_before"]==own["software_control_metadata_after"]==software_before and own["conditional_core_runtime"]==runtime and own["plan_directory_metadata_before"]==own["plan_directory_metadata_after"]==plan_dir,"Actual16888 Source12/SW4/Core/current Plan directory required")
need({k:own[k]for k in ["Source_n","seed_n","role_n","parent_n"]}==dict(Source_n=640,seed_n=3809,role_n=9,parent_n=17)and own["prior322_projection"]==dict(prior_row_n=322,alias_hit_n=322,ordinary_strict_row_indices=[]),"Actual full reviewed V6 counts/projection required")
for k in ["ordered5_alias_prefix_preserved","two_aliases_and_two_explicit_Source_rows_only_delta","all_Source12_SW4_Core_controls30_Source4_and_finite_protected_metadata_pre_end_afteroutput_finalreadonly_bound","plan_child_receipts_shape_only_no_child_IO","recovered_Source_never_imported_compiled_or_executed","oldPlanV5_SHA_unqualified_not_retroactively_qualified","original16825_failing_component_still_UNOBSERVED","own_created_controls_LATE_COMPOSER_ONLY_NOT_PLAN_PREREQUISITES"]:need(own[k]is True,"Actual16888 qualifier flag required: "+k)
for k in ["scientific_receipt_children_read_or_hashed","compiler_or_tests_or_new_software_qualification_executed","historical_Slurm_queried","source_audit_executed","source_staged","published","ACTIVE_changed"]:need(own[k]is False,"Actual16888 narrow control scope required: "+k)
need(terminal["schema"]=="root-source-plan-v6-own-sha-actual-terminal-metadata-seal.v1"and terminal["status"]=="ACTUAL_NEW_PLAN_V6_OWN_SHA_CONTENT_AND_TERMINAL_METADATA_READBACK_PASS_NOT_SOURCE_ACCEPTANCE"and terminal["actual_job_id"]=="16888"and terminal["actual_capture"]==OWNCAPPIN and terminal["actual_plan"]==PLANPIN and terminal["actual_handoff"]==HANDOFFPIN and terminal["actual_allocation"]==a and terminal["Root_plus_two_whole_saved_content_READBACK_PASS"]is True,"Actual qualified16888 content and terminal required")
tr=terminal["fresh_terminal"]
need(tr["returncode"]==0 and tr["actual_row"]==["16888","COMPLETED","0:0","2","1","test9_source_plan_v6_ownsha_cpu","u21111210118","u21111210118","organ"]and tr["stdout"]=="|".join(tr["actual_row"])+"\n"and tr["stderr"]=="","Actual saved16888 COMPLETED2 numeric terminal required")
need(reqseal["schema"]=="root-plan-v6-strict-finite8-adapter-request-metadata-readonly-seal.v1"and reqseal["status"]=="ROOT_PLAN_V6_STRICT13_FINITE8_PARENT_VIEW_REQUEST_WHOLE_STATIC_AND_METADATA_RO_PASS_NOT_SOURCE_ACCEPTANCE"and reqseal["Root_plus_two_independent_whole_STATIC_READBACK_PASS"]is True and reqseal["actual16888_Root_two_content_and_independent_terminal_RO_PASS"]is True and reqseal["after_files"]==control_before[:2],"Actual strict Q13/M50 reviewed readonly seal required")
request_directory_before=md(authority(REQUEST.parent));plan_directory_before=md(authority(PLAN.parent))
need(request_directory_before==reqseal["after_directory"]and plan_directory_before==plan_dir and stat.S_IMODE(request_directory_before["mode"])==stat.S_IMODE(plan_directory_before["mode"])==0o555,"Exact readonly Q/Plan directories required")
need(set(p.name for p in REQUEST.parent.iterdir())=={"request.json","request_metadata.json"},"Exact NEW request two-file namespace required")
META_KEYS=["schema","prepared_at_UTC","metadata_only","text_preparation_only","no_login_hash","request_current_initial_metadata","request_schema","exact13_key_order","only_request_field_changed","old_request_retained_unchanged_LATE_scalar","old_request_metadata_retained_unchanged_LATE_scalar","old_initial_metadata_TXT_retained_unchanged_LATE_scalar","accepted_Plan","accepted_Plan_HANDOFF","accepted_library_software","accepted_Mapper","actual16888_Plan_own_capture","actual16888_terminal_RO_reference_scalar","root_and_two_independent_actual16888_content_readback_PASS","root_and_independent_actual16888_terminal_RO_readback_PASS","actual16888_scope","finite_parent_alias_n","finite_source_parent_copy_n","finite_proof_parent_copy_n","ordered_Plan17_indices","ordered_BaseI_files_indices","finite_parent_alias_scope_rows","accepted_BaseI","accepted_Mapper_finite_source_read_view_proof","exact17_logical_parents_unchanged","Plan_alias_n","request_does_not_modify_Plan_aliases","Source_IDs_and_existing22_late_hazard_classification_unchanged","no_new_role_or_software_gate","new_request_own_SHA_not_yet_captured","request_readonly_seal_not_yet_performed","request_current_mode_is_draft_0664","new_request_executed","Source_audit_accepted","source_staged","published","ACTIVE_changed","scientific_acceptance","raw_JSON_changed","generic_relative_permission_added","generic_external_permission_added","new_logical_parent_permission_added","scientific_receipt_children_opened","current_execution_authorized","own_created_controls_LATE_Composer_not_Plan_prerequisites"]
need(list(prep)==META_KEYS and len(prep)==50 and prep["schema"]=="root-plan-v6-strict-finite-parent-view-request-text-preparation-metadata.v1"and prep["exact13_key_order"]==keys and prep["only_request_field_changed"]=="final_source_plan","Fresh exact closed50 active preparation metadata required")
need(prep["accepted_Plan"]==PLANPIN and prep["accepted_Plan_HANDOFF"]==HANDOFFPIN and prep["accepted_library_software"]==SOFTWARE and prep["accepted_Mapper"]==MAPPERPIN and prep["accepted_BaseI"]==EXPECTED30[14]and prep["accepted_Mapper_finite_source_read_view_proof"]==MAPPERPROOFPIN and prep["actual16888_Plan_own_capture"]==OWNCAPPIN,"Actual preparation qualified graph pointers required")
need({k:prep["request_current_initial_metadata"][k]for k in reqseal["before_files"][0]}==reqseal["before_files"][0]and prep["request_current_initial_metadata"]["regular"]is True and prep["request_current_initial_metadata"]["directory"]is False and prep["request_current_initial_metadata"]["nonlink"]is True,"Preparation initialQ metadata matches actual RO transition")
tref=prep["actual16888_terminal_RO_reference_scalar"]
need(tref["logical_path"]==str(OWNTERMINAL)and tref["metadata_bytes_as_scalar"]==237589 and {k:tref["current_metadata"][k]for k in control_before[5]}==control_before[5]and tref["own_SHA_not_yet_CPU_captured"]is True,"Actual terminal scalar metadata, no invented preparation SHA")
for k in ["root_and_two_independent_actual16888_content_readback_PASS","root_and_independent_actual16888_terminal_RO_readback_PASS","metadata_only","text_preparation_only","no_login_hash","exact17_logical_parents_unchanged","request_does_not_modify_Plan_aliases","Source_IDs_and_existing22_late_hazard_classification_unchanged","no_new_role_or_software_gate","new_request_own_SHA_not_yet_captured","request_readonly_seal_not_yet_performed","request_current_mode_is_draft_0664","own_created_controls_LATE_Composer_not_Plan_prerequisites"]:need(prep[k]is True,"Preparation flag required: "+k)
for k in ["new_request_executed","Source_audit_accepted","source_staged","published","ACTIVE_changed","scientific_acceptance","raw_JSON_changed","generic_relative_permission_added","generic_external_permission_added","new_logical_parent_permission_added","scientific_receipt_children_opened","current_execution_authorized"]:need(prep[k]is False,"Preparation narrow scope required: "+k)
BASEIPIN=EXPECTED30[14];base_i=base;map_a=read_json(MAPPERPIN["path"])
need(map_a["finite_source_read_view_proof"]==MAPPERPROOFPIN and plan["mapper_software_acceptance"]==MAPPERPIN,"Accepted mapper finite proof and Plan binding required")
plan_indices=[7,8,9,10,12,13,14,16];base_indices=[238,249,265,263,250,283,228,239]
derived=[(i,j)for i,parent in enumerate(plan["context_parent_seeds"])for j,row in enumerate(base_i["files"])if row["original_source"]==parent]
need(derived==list(zip(plan_indices,base_indices))and FINITE_PAIRS==[dict(logical=plan["context_parent_seeds"][i],physical=base_i["files"][j]["source"])for i,j in derived],"Exact complete17x683 finite8 source/proof inventory required")
need(reqseal["finite_parent_aliases"]==FINITE_PAIRS and reqseal["fixed_Plan17_indices"]==prep["ordered_Plan17_indices"]==plan_indices and reqseal["fixed_BaseI_indices"]==prep["ordered_BaseI_files_indices"]==base_indices and reqseal["existing_finite_source_parent_n"]==prep["finite_source_parent_copy_n"]==3 and reqseal["existing_finite_proof_parent_n"]==prep["finite_proof_parent_copy_n"]==5 and prep["finite_parent_alias_n"]==8 and prep["Plan_alias_n"]==7,"Same3SOURCE/5PROOF/17/7 scope required")
need(type(prep["finite_parent_alias_scope_rows"])is list and len(prep["finite_parent_alias_scope_rows"])==8,"Exact eight finite classification rows required")
for i,row in enumerate(prep["finite_parent_alias_scope_rows"]):
 need(row["plan17_index"]==plan_indices[i]and row["BaseI_files_index"]==base_indices[i]and row["reader_group"]==("FINITE_SOURCE_PARENT"if i<3 else"FINITE_PROOF_PARENT")and row["logical"]==FINITE_PAIRS[i]["logical"]and row["physical"]==FINITE_PAIRS[i]["physical"],"Exact finite parent classification required")
 for k,idx in [("logical",38+2*i),("physical",39+2*i)]:
  need({n:row[k+"_current_metadata"][n]for n in control_before[idx]}==control_before[idx],"Actual finite parent complete metadata differs")
protected=reqseal["protected_inputs_after"];protected_dirs=reqseal["protected_directories_after"]
need(protected==reqseal["protected_inputs_before"]and protected_dirs==reqseal["protected_directories_before"]and len(protected)==191 and len(protected_dirs)==73,"Actual whole request RO protected191/73 required")
protected_by_path={row["path"]:row for row in protected}
need(len(protected_by_path)==191 and all(protected_by_path.get(control_before[i]["path"])==control_before[i]for i in list(range(4,54))),"All50 fixed existing controls bound by reviewed QRO metadata")
def seal_directory(p):
 p.chmod(0o555);fd=os.open(str(p),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
 need(stat.S_IMODE(md(p)["mode"])==0o555,"Readonly Root proof directory required")
def final_readback():
 need([md(authority(p))for p in [P,G]]==source_directories_before and md(authority(REQUEST.parent))==request_directory_before and md(authority(PLAN.parent))==plan_directory_before,"Readonly Source/Q/Plan directories changed")
 need([readonly(r["path"],r)[1]for r in sources]==source_before,"Qualified original+frozen Source12 changed")
 need([readonly(r["path"],r)[1]for r in software_controls]==software_before,"Qualified SW4 changed")
 need([readonly(r["path"],r)[1]for r in control_receipts]==control_before,"All54 own control whole bytes/stable metadata changed")
 need([md(p)for p in canonical]==canonical_before and [record(p)for p in canonical]==canonical_expected and [md(p)for p in canonical]==canonical_before,"Currentcanonical4 bytes/fullmetadata changed")
 metadata_readback();core_readback()
final_readback()
# Qualified G main is imported only after current CPU/GPU0, literal source12/SW4/CORE/control checks.
import importlib.util
vendor_spec=importlib.util.spec_from_file_location("root_current_vendor_and_worker_preservation",G/"final_source_closure.py")
need(vendor_spec is not None and vendor_spec.loader is not None,"Qualified vendor verifier loader required")
vendor_lib=importlib.util.module_from_spec(vendor_spec)
vendor_spec.loader.exec_module(vendor_lib)
root_allocation=vendor_lib.cpu()
need(root_allocation["job_id"]==jid and root_allocation["allocated_CPUs"]==1 and root_allocation["allocated_gpus"]==0 and root_allocation["numeric_sacct_row"]==attempts[selected-1]["actual_row"],"Fresh qualified current root CPU1/GPU0 required")
tres(root_allocation["numeric_sacct_row"][2])
vendor_lib.software_shape(swa,ct);vendor_lib.software_snapshot_shape(swa,snapshot)
need(vendor_lib.conditional_core_runtime()==runtime,"Actual qualified/current CORE differs")
final_readback()
OUT=S/"runs"/("final_source_relative_receipt_observer_v6_"+jid)
AUX=OUT.with_name(OUT.name+"_context_adapter")
PROOF=S/"submissions"/("source_relative_receipt_observer_v6_outer_"+jid)
for p in [OUT,AUX,PROOF]:need(not p.exists()and not p.is_symlink(),"Exclusive absent actual production output required")
PROOF.mkdir(mode=0o755,exist_ok=False)
def proof_write(name,value):
 p=PROOF/name;data=(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode()
 with p.open("xb")as f:f.write(data);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 need(p.read_bytes()==data,"Whole actual Root output reread required")
 return record(p)

# Historical failed16940 qualification is saved-control-only; never query that job here.
FAILED_SEAL=S/"submissions/final_source_plan_v6_audit16940_actual_failed_terminal_metadata_seal/receipt.json"
expected_failed_seal_metadata=dict(path=str(FAILED_SEAL),bytes=1336028,inode=144115643443092111,mtime_ns=1792084412000000000,ctime_ns=1792084412000000000,mode=33060,dev=1119461688,nlink=1,uid=6263900,gid=6263900)
need(md(authority(FAILED_SEAL))==expected_failed_seal_metadata,"Actual Root and independently reviewed failed16940 seal required")
FAILED_OUT=S/"runs/final_source_plan_v6_audit_16940"
FAILED_AUX=FAILED_OUT.with_name(FAILED_OUT.name+"_context_adapter")
FAILED_PROOF=S/"submissions/source_plan_v6_production_outer_16940"
extra_paths=[FAILED_SEAL,S/"handoffs/ROOT_FIXED_PLAN_V6_SOURCE_AUDIT_FROM16651_16888_20261015_REV1.md",S/"submissions/root_fixed_plan_v6_production_REV1_humans_metadata_readonly_seal/receipt.json",FAILED_OUT/"contracts.json",FAILED_OUT/"contracts.txt",FAILED_OUT/"typed_incomplete.json",FAILED_AUX/"typed_incomplete.json",FAILED_PROOF/"typed_incomplete.json",S/"logs/final_source_plan_v6_audit_16940.out",S/"logs/final_source_plan_v6_audit_16940.err"]
extra_sizes=[1336028,81234,236614,2065,20352,634,667,1049,702,4108]
extra_values=[readonly(p)for p in extra_paths]
extra_receipts=[v[0]for v in extra_values];extra_metadata=[v[1]for v in extra_values]
need([r["bytes"]for r in extra_receipts]==extra_sizes,"Fixed ten historical own control byte lengths required")
failed=read_json(FAILED_SEAL)
need(failed["schema"]=="root-source-plan-v6-production-actual-failed-terminal-metadata-seal.v1"and failed["status"]=="ACTUAL_FAILED16940_SOURCE_OUTPUTS_PRESERVED_READONLY_NOT_SOURCE_ACCEPTANCE"and failed["actual_job_id"]=="16940","Actual failed16940 preserved terminal metadata control required")
need(failed["fresh_terminal"]["actual_row"]==["16940","FAILED","1:0","336","1","test9_final_source_plan_v6_audit_cpu","u21111210118","u21111210118","organ"]and failed["fresh_terminal"]["returncode"]==0,"Saved actual16940 terminal, not a historical live query, required")
need(failed["mandatory_122_unique_named_OK_no_fail_error_skip"]is True and failed["Source_acceptance"]is False and failed["actual_offending_receipt_parent_trail_module_STILL_UNOBSERVED"]is True,"Historical contract pass is not production acceptance or observed context")
need(len(failed["after_files"])==1008 and len(failed["after_directories"])==9 and len(failed["protected_inputs_after"])==210 and len(failed["protected_directories_after"])==78,"Full old output and protected finite metadata universes required")
def failure_metadata_readback():
 need(md(authority(FAILED_SEAL))==expected_failed_seal_metadata,"Historical failed16940 seal changed")
 for row in failed["after_files"]+failed["after_directories"]+failed["protected_inputs_after"]+failed["protected_directories_after"]+failed["current_fixed_Source4_and_bbf_metadata_after"]:
  need(md(authority(row["path"]))==row,"Preserved failed16940 output or protected input metadata changed: "+row["path"])
 need([md(x["path"])for x in failed["conditional_CORE_metadata_after"]]==failed["conditional_CORE_metadata_after"],"Historical fixed Core metadata changed")
 need([readonly(r["path"],r)[1]for r in extra_receipts]==extra_metadata,"Historical own ten control bytes or stable metadata changed")
failure_metadata_readback();final_readback()
TMP=S/"tmp"/("final_source_relative_receipt_observer_v6_"+jid)
need(not TMP.exists()and not TMP.is_symlink(),"Exclusive diagnostic fixture TMP required")
TMP.mkdir(mode=0o755)
old_tmp_present="TMPDIR"in os.environ;old_tmp=os.environ.get("TMPDIR");old_argv=sys.argv[:]
os.environ["TMPDIR"]=str(TMP)
actual_adapter_argv=[str(G/"final_source_context_adapter.py"),"--request",str(REQUEST),"--out",str(OUT)]
phase="actual_unchanged_qualified_adapter_runpy_122_no_hooks_or_patches"
def diagnostic_incomplete(exc):
 proof_write("typed_incomplete.json",dict(schema="root-relative-receipt-observer-v6-typed-incomplete.v1",status="DIAGNOSTIC_CONTEXT_NOT_QUALIFIED_DO_NOT_STAGE_OR_PUBLISH",actual_job_id=jid,phase=phase,reason_type=type(exc).__name__,reason=str(exc),original16940_context_still_UNOBSERVED=True,source_staged=False,published=False,ACTIVE_changed=False))
 seal_directory(PROOF)
try:
 import runpy
 sys.argv=actual_adapter_argv[:]
 try:
  runpy.run_path(str(G/"final_source_context_adapter.py"),run_name="__main__")
 except BaseException as observed_error:
  phase="authenticate_original_unhandled_failure_traceback"
  if type(observed_error)is not ValueError or str(observed_error)!="Absolute receipt path required":
   diagnostic_incomplete(observed_error);raise
  # Retain original exception and frames. Do not trace, patch, replace, or synthesize any library call.
  traceback_rows=[];tb=observed_error.__traceback__
  while tb is not None:
   traceback_rows.append((tb.tb_frame,tb.tb_lineno));tb=tb.tb_next
  main_path=str(AUX/"runner/final_source_closure.py")
  relevant=[(f,n)for f,n in traceback_rows if f.f_code.co_filename==main_path]
  audit_rows=[(f,n)for f,n in relevant if f.f_code.co_name=="audit"]
  shape_rows=[(f,n)for f,n in relevant if f.f_code.co_name=="receipt_shape"]
  edges_rows=[(f,n)for f,n in relevant if f.f_code.co_name=="receipt_edges"]
  need_rows=[(f,n)for f,n in relevant if f.f_code.co_name=="need"]
  need(len(audit_rows)==len(shape_rows)==len(need_rows)==1 and audit_rows[0][1]==2436 and shape_rows[0][1]==49 and need_rows[0][1]==40 and edges_rows and edges_rows[-1][1]==152 and all(n in(152,153,155)for f,n in edges_rows),"Exact qualified actual traceback consumer, recursive edge, shape, and guard frames required")
  audit_frame=audit_rows[0][0];shape_frame=shape_rows[0][0];inner=edges_rows[-1][0]
  bad=shape_frame.f_locals.get("r");enclosing=audit_frame.f_locals.get("r")
  need(type(bad)is dict and bad is inner.f_locals.get("o")and edges_rows[0][0].f_locals.get("o")is audit_frame.f_locals.get("obj"),"Actual offending nested object identity and enclosing parsed object identity required")
  need(all(k in bad for k in("path","bytes","sha256"))and type(enclosing)is dict,"Actual receipt-shaped nested object and enclosing receipt required")
  need(not(isinstance(bad["path"],str)and Path(bad["path"]).is_absolute()),"Actual line49 nonabsolute or type-invalid path failure required; do not inspect its target")
  actual_runner_controls=[dict(path=str(folder/name),bytes=n,sha256=h)for folder in[AUX/"runner",OUT/"runner"]for name,n,h in source_pins]
  actual_runner_metadata=[readonly(r["path"],r)[1]for r in actual_runner_controls]
  need(all(stat.S_IMODE(md(authority(folder))["mode"])==0o555 for folder in[AUX/"runner",OUT/"runner"]),"Exact actual AUX and audit frozen source directories must already be readonly")
  def scalar(value):
   import math
   t=type(value)
   if isinstance(value,Path):return dict(type=t.__name__,lexical_path_scalar=str(value),no_filesystem_operation=True)
   if value is None or t in(str,bool,int):return dict(type=t.__name__,scalar=value)
   if t is float:return dict(type="float",finite=math.isfinite(value),scalar=value if math.isfinite(value)else None)
   return dict(type=t.__name__,scalar_omitted=True)
  def receipt_projection(value):
   need(type(value)is dict and all(type(k)is str for k in value),"Exact string-key receipt object required")
   return dict(path=scalar(value.get("path")),bytes=scalar(value.get("bytes")),sha256=scalar(value.get("sha256")),extra_key_names=sorted(k for k in value if k not in("path","bytes","sha256")))
  def trail_projection(value):
   need(type(value)is tuple and all(type(v)is str for v in value),"Actual string tuple trail required")
   return list(value)
  outer_names=["physical","parent","trail","module","stage","basis"]
  need(all(k in audit_frame.f_locals for k in outer_names),"Complete enclosing actual audit context fields required")
  outer={k:scalar(audit_frame.f_locals[k])for k in outer_names if k!="trail"}
  outer["trail"]=trail_projection(audit_frame.f_locals["trail"])
  observations=dict(original_exception_type=type(observed_error).__name__,original_exception_message=str(observed_error),qualified_actual_main_path=main_path,authenticated_frames=[dict(function=f.f_code.co_name,line=n)for f,n in relevant],offending_nested_receipt=receipt_projection(bad),offending_nested_receipt_inner_trail=trail_projection(inner.f_locals["trail"]),enclosing_receipt=receipt_projection(enclosing),enclosing_audit_context=outer,receipt_edges_trails=[dict(line=n,container_type=type(f.f_locals.get("o")).__name__,trail=trail_projection(f.f_locals["trail"]))for f,n in edges_rows],object_identity_shape_r_is_innermost_edges_o=True,object_identity_outermost_edges_o_is_audit_obj=True,bytes_and_sha_checks_after_line49_not_executed=True,relative_offending_path_not_resolved_statted_opened_or_hashed=True,no_full_object_or_queue_or_locals_dump=True)
  phase="actual_diagnostic_contracts_and_narrow_context_readback"
  new_contract_pin,new_contract_metadata=readonly(OUT/"contracts.json")
  new_log_pin,new_log_metadata=readonly(OUT/"contracts.txt")
  new_contracts=read_json(OUT/"contracts.json");new_log=(OUT/"contracts.txt").read_text()
  need(new_contracts["status"]=="PASS"and new_contracts["tests"]==122 and new_contracts["failures"]==new_contracts["errors"]==0 and new_contracts["owned_python_compile_PASS"]is True and new_contracts["bash_syntax_PASS"]is True and new_contracts["log"]==new_log_pin,"Actual mandatory producer122 must pass before diagnostic context qualification")
  named_ok=re.findall(r"^(test_\S+) \(([^)]*)\) \.\.\. ok$",new_log,re.M)
  need(len(named_ok)==122 and len(set(named_ok))==122 and re.search(r"^Ran 122 tests in [0-9.]+s$",new_log,re.M)is not None and new_log.rstrip().endswith("OK")and "skipped"not in new_log.lower()and "FAILED"not in new_log,"Actual122 unique named producer tests allOK/zero skipped required")
  need(new_contracts["tested_source_files"]==actual_runner_controls[6:],"Actual mandatory producer used this new readonly audit runner6")
  incomplete_paths=[OUT/"typed_incomplete.json",AUX/"typed_incomplete.json"]
  incomplete_values=[readonly(p)for p in incomplete_paths]
  incomplete_controls=[v[0]for v in incomplete_values];incomplete_metadata=[v[1]for v in incomplete_values]
  incompletes=[read_json(p)for p in incomplete_paths]
  need(all(v["reason_type"]=="ValueError"and v["reason"]=="Absolute receipt path required"and v["source_staged"]is False and v["ACTIVE_changed"]is False for v in incompletes),"Actual original diagnostic child typed incomplete controls required")
  need(incompletes[0]["failed_stage"]=="recursive_exact_new_dependencies"and incompletes[0]["allocation"]==root_allocation,"Exact diagnostic loop stage/current CPU allocation required")
  missing=[OUT/"acceptance.json",OUT/"context_adapter_acceptance.json",OUT/"source_inclusion_final.json",OUT/"source_receipt_closure_final.json"]
  def diagnostic_output_readback():
   need([readonly(r["path"],r)[1]for r in actual_runner_controls]==actual_runner_metadata,"Actual executing AUX/audit source12 changed")
   need([readonly(r["path"],r)[1]for r in[new_contract_pin,new_log_pin]+incomplete_controls]==[new_contract_metadata,new_log_metadata]+incomplete_metadata,"Actual diagnostic contract, log, and typed controls changed")
   need(read_json(OUT/"contracts.json")==new_contracts and [read_json(p)for p in incomplete_paths]==incompletes,"Actual diagnostic full own control reread required")
   need(all(not p.exists()and not p.is_symlink()for p in missing),"Actual diagnostic failure must not be accepted as Source")
  diagnostic_output_readback();failure_metadata_readback();final_readback()
  phase="exclusive_diagnostic_observation_control_flush_fsync_readonly"
  result=dict(schema="root-plan-v6-relative-receipt-unhandled-failure-observation.v1",status="ACTUAL_RELATIVE_RECEIPT_FAILURE_CONTEXT_CPU_OBSERVED_DIAGNOSTIC_ONLY_NOT_SOURCE_ACCEPTANCE",actual_job_id=jid,allocation=root_allocation,current_actual_readiness=read_json(D/"readiness.json"),actual_unchanged_adapter_argv=actual_adapter_argv,original16940_context_still_UNOBSERVED=True,this_observer_proves_only_its_own_actual_context=True,observation=observations,mandatory_producer_contracts=new_contract_pin,mandatory_producer_log=new_log_pin,mandatory_122_unique_named_OK_no_error_failure_skip=True,actual_typed_incomplete_controls=incomplete_controls,actual_executing_AUX_and_audit_source_files=actual_runner_controls,actual_executing_source_metadata_before=actual_runner_metadata,actual_executing_source_metadata_after=actual_runner_metadata,source_files=expected_frozen,original_executing_sources=expected_original,source_metadata_before=source_before,source_metadata_after=source_before,qualified_software_acceptance=SOFTWARE,software_control_receipts=software_controls,software_control_metadata_before=software_before,software_control_metadata_after=software_before,control_receipts=control_receipts,control_metadata_before=control_before,control_metadata_after=control_before,historical_failed_control_receipts=extra_receipts,historical_failed_control_metadata_before=extra_metadata,historical_failed_control_metadata_after=extra_metadata,historical_failed_own1008_directories9_and_protected210_directories78_full_metadata_PASS=True,conditional_core_runtime=runtime,Source12_SW4_Core_controls54_and_historical10_pre_end_afteroutput_finalreadonly_PASS=True,source_staged=False,published=False,ACTIVE_changed=False,Source_acceptance=False,no_receipt_shape_or_reader_patch=True,no_trace_hook_or_return_value_replacement=True,no_scientific_observation_or_child_target_bytes_captured_by_observer=True,original_exception_will_be_bare_rethrown=True,expected_Slurm_terminal="FAILED|1:0",own_created_controls_LATE_Composer_not_own_Plan_prerequisites=True)
  descriptor=proof_write("observation.json",result)
  diagnostic_output_readback();failure_metadata_readback();final_readback()
  seal_directory(PROOF)
  need(readonly(descriptor["path"],descriptor)[0]==descriptor and read_json(descriptor["path"])==result,"Final readonly diagnostic observation complete reread required")
  diagnostic_output_readback();failure_metadata_readback();final_readback()
  print(json.dumps(dict(status=result["status"],observation=descriptor,actual_job_id=jid,request=control_receipts[0],plan=PLANPIN,root_control_human=control_receipts[2],expected_original_exception_will_be_rethrown=True,Source_acceptance=False),sort_keys=True),flush=True)
  raise
 else:
  phase="unexpected_source_audit_success_not_a_qualified_diagnostic"
  e=ValueError("Expected original relative receipt failure not observed; do not qualify or stage")
  diagnostic_incomplete(e);raise e
except BaseException as envelope_error:
 if not(PROOF/"observation.json").exists()and not(PROOF/"typed_incomplete.json").exists():
  try:diagnostic_incomplete(envelope_error)
  except Exception as seal_error:print("Diagnostic failure-control seal error: "+repr(seal_error),file=sys.stderr,flush=True)
 raise
finally:
 sys.argv=old_argv
 if old_tmp_present:os.environ["TMPDIR"]=old_tmp
 else:os.environ.pop("TMPDIR",None)
ROOT_RELATIVE_RECEIPT_OBSERVER_V6_PY
'