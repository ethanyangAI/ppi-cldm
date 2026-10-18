# Root fixed additional SOURCE/DOC/CONTROL pin capture from accepted software15368 REV2
Prepared operational execution control only; UNEXECUTED. This is not a new helper software qualification, Source/science audit or tenth role.

Actual qualified software: runs/final_source_inherited_entries_software_15368/acceptance.json6554/SHA40c9d1ecaccb8d549bb98cf0d2fb89d62fe3a7e26144b5e69114e34e75173eda,65 allPASS; selected code is exact actual frozen runner/final_source_closure.py and its complete6. Current readiness occurs BEFORE hashing or importing selectedSource; the accepted library cpu() then independently re-queries currentSlurm. Whole original+frozen6/currententry/SWA+snapshot/contracts/log and conditional CORE stable fullbyte identity are bound before/end/afteroutput. These explicitly named software SOURCE/control children are read, while scientific receipt children are not followed. No tests/compiler/historicalSlurm/model/scientific/Cost execution.

REV1 is a narrow pre-execution correction from independently reviewed original19405: actualSWA6554/40c9 and six full literal qualifiedG pins/readonly nonlink ancestry are verified with stdlib AFTERcurrentSlurm readiness but BEFOREspec.exec_module. Optional source_public_destination is strictly string and passed unchanged library.destination safety checks. No scientific/Source permission or additional software is created. Original19405 remains immutable and was never executed.

REV2 narrowly completes the four software evidence controls' fullbyte/stable-metadata before/end/afteroutput checks (SWA,contracts,contractlog,source_snapshot) explicitly and records their table. It also uses the actual fixed request's required_as list schema, restricted to the four existing approved SOURCE/SEED or LATE/INDEX combinations; REV1's provisional string expectation was incompatible with actual prepared request data. This is operational text/data-shape repair, not Source/library/scientific changes. Both previous19405/22147 controls are preserved and were never executed.

The only new input is fixed pending/final_source_additional_control_pins_from15368_v1/request.json and sibling HANDOFF.md. They must be actual, independently reviewed and444/P555 before submission. Root request top-level exactschema final-source-additional-control-pin-request.v1/schema-root_owned-metadata_scope-targets; each existing explicit target metadata/coverage path is fixed by that reviewed JSON. Capture reads only each declared target's own bytes, verifies exactPythoninteger metadata before/end/afteroutput, never derives children or globs. Bounds<=2000targets,request2MiB,HANDOFF1MiB. No arbitrary command-line input or public/source permission is introduced. The current producer retains all coverage dispositions verbatim; it does not accept their scientific content.

Envelope: test9_source_additional_control_pins_cpu/accountu21111210118/qosnormal/organ/task1/CPU1/8G/00:10:00/GPU0 requested, chdirS; logs source_additional_control_pins_%j.out/.err; CUDAempty,JAXcpu/PYTHONNOUSER/PYTHONDONTWRITE/PYTHONPATHunset/BLAS-OMP-MKL1/CORE-B/no-I. This is a distinct control-capture envelope, not an amendment to old15368/15275 or science. Current strictTRES/realunique6colsSACCT/60s30attempts5sRPC/timeoutnullRC+partialraw readiness derives actual approvedRootREV2 proof. Allqueries/currentproof saved; original15201 cause remainsUNPROVEN.

Output fixed runs/final_source_additional_control_pins_ACTUALJOB/capture.json, readonlyexclusive/flushfsync/currentguards/prepost/reread and ownactualCPUdescriptor stdout. Actual fullcapture includes finite receipts; it and its own createdRootclaims/readiness/raws/logs/terminal are LATE_COMPOSER_ONLY, never operativeLIBJSON seeds because that would reintroduce explicit oldPlan/originalJSON hazards. Individual safe preexisting targets may become operativePlan sources/seeds according to requestdisposition. Explicit oldPlan-bearing and22 copiedJSON histories are preserved byte/index-only later, without new17parent permission. FutureComposer/restore ability must actually verify these controls; this proposal is not futureacceptance.

This document/literalROOTwrap, inputrequest/HANDOFF, actualclaims/readiness/raw/capture/logs/ROseal/currentruntimefacts must all remain explicit additional final_delivery_tools SOURCE/evidence coverage. Owncreatedproofs cannot prerequisite themselves or the Plan being captured. Root waits Source/control static reviews+RO before unique actualCPU; no futureJobID/SHA is asserted. ExistingSCI/report/cost/default/oldPlan/request/source/failedproofs/heartbeat remainunchanged.

## Literal Root sbatch --wrap control
```sh
exec env -u PYTHONPATH CUDA_VISIBLE_DEVICES= JAX_PLATFORMS=cpu PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /lustre/users/u21111210118/projects/test9/env/core/bin/python -B - <<'ROOT_FIXED_ADDITIONAL_CONTROL_PIN_CAPTURE'
import os, sys, json, re, stat, time, datetime, subprocess
from pathlib import Path
S = Path("/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery")
jid = os.environ.get("SLURM_JOB_ID", "")
if not re.fullmatch("[0-9]+", jid):
    raise SystemExit("Current owned Slurm job ID required")
expected_env = {"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
if any(os.environ.get(k) != v for k, v in expected_env.items()) or "PYTHONPATH" in os.environ:
    raise SystemExit("Original CPU/import/thread isolation required")
D = S / "submissions" / ("source_additional_control_pins_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_source_additional_control_pins_cpu", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:10:00", "MinMemoryNode": "8G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/8G10/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-additional-control-pin-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_ADDITIONAL_CONTROL_PIN_CAPTURE_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "capture_program_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_ADDITIONAL_CONTROL_PIN_CAPTURE_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_ADDITIONAL_CONTROL_PIN_CAPTURE_NOT_EXECUTED"
obj = {"schema": "root-current-owned-additional-control-pin-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "fixed_control_pin_capture_execution_next_not_acceptance": True}), flush=True)

# Only after actual current Slurm readiness; execute accepted source API, no tests.
import importlib.util
G=S/"runs/final_source_inherited_entries_software_15368/runner"
P=S/"pending/final_source_closure_v3_fixturefix2_inherited_entrypoints1"
REQUEST=S/"pending/final_source_additional_control_pins_from15368_v1/request.json"
HANDOFF=REQUEST.with_name("HANDOFF.md")
SOFTWARE={"path":str(S/"runs/final_source_inherited_entries_software_15368/acceptance.json"),"bytes":6554,"sha256":"40c9d1ecaccb8d549bb98cf0d2fb89d62fe3a7e26144b5e69114e34e75173eda"}
# Explicit acceptedSOURCE pins are checked with stdlib before module execution.
import hashlib
R=Path("/lustre/users/u21111210118/projects/test9")
def preimport_need(value,message):
 if not value:raise ValueError(message)
def preimport_source(path,expected_bytes,expected_sha):
 path=Path(path);preimport_need(path.is_absolute()and ".."not in path.parts,"Fixed absolute Source path required")
 path.relative_to(R)
 for node in [path]+list(path.parents):
  if node==R.parent:break
  st=node.lstat();preimport_need(not stat.S_ISLNK(st.st_mode),"Source/ancestor symlink forbidden before import")
 preimport_need(stat.S_ISREG(path.lstat().st_mode)and stat.S_IMODE(path.lstat().st_mode)==0o444 and path.lstat().st_nlink==1,"Readonly regular single-link qualifiedSource before import required")
 raw=path.read_bytes();preimport_need(len(raw)==expected_bytes and hashlib.sha256(raw).hexdigest()==expected_sha,"Actual qualifiedSource/SWA bytes fork before import")
 return raw
swa_raw=preimport_source(SOFTWARE["path"],SOFTWARE["bytes"],SOFTWARE["sha256"])
swa=json.loads(swa_raw)
pins=[
 ("final_source_closure.py",64604,"60f636b276449e2ceb327fb4a65a289488f9150e7d3fe1e344541a8ccfc6d63d"),
 ("test_final_source_closure.py",42430,"cd0102300081ec49122b0cb70db633c441ee760dd4b45f115f190b01a9b5087a"),
 ("final_source_cpu.sbatch",1597,"8054622a7c509e73aece25dc58304c6f8f9943f9acec616ffdcb026f78825826"),
 ("HANDOFF.md",11213,"23b693135e5707f7b01132bdfd4990ef7f0a8201b70946ecffb182f40bfb374b"),
 ("FINAL_SOURCE_CHECKLIST.md",3084,"ca0c155dcc1a89a9a009e2347bb054f34b63332fb487eada5ce1735010f9c548"),
 ("final_source_context_adapter.py",8030,"e77a9a85293af4cd22ea33c7ea1c7512df3f027a120378fb34d7639e9472bf5f")]
expected=[dict(path=str(G/name),bytes=n,sha256=h)for name,n,h in pins]
preimport_need(swa["source_files"]==expected and G.is_dir()and not G.is_symlink()and stat.S_IMODE(G.lstat().st_mode)==0o555 and {x.name for x in G.iterdir()}=={x[0]for x in pins},"Exact accepted frozen own6 directory required before import")
for name,n,h in pins:preimport_source(G/name,n,h)
sp=importlib.util.spec_from_file_location("root_fixed_additional_control_capture_lib",G/"final_source_closure.py")
lib=importlib.util.module_from_spec(sp);sp.loader.exec_module(lib)
allocation=lib.cpu()
runtime=lib.conditional_core_runtime()
software=lib.read(lib.verify(SOFTWARE,True));ct=lib.read(lib.verify(software["contracts"],True))
lib.software_shape(software,ct);lib.verify(ct["log"],True)
lib.software_snapshot_shape(software,lib.read(lib.verify(software["source_snapshot"],True)))
software_control_receipts=[SOFTWARE,software["contracts"],ct["log"],software["source_snapshot"]]
software_control_metadata_before=[lib.stable_metadata(lib.verify(r,True))for r in software_control_receipts]
def software_control_readback():
 lib.need([lib.stable_metadata(lib.verify(r,True))for r in software_control_receipts]==software_control_metadata_before,"Qualified software evidence bytes/stable metadata changed")
 return True
software_control_readback()
lib.need(software["conditional_core_runtime"]==runtime,"Qualified software/current conditional CORE differs")
original,original_before=lib.owned_source_bundle(P);frozen,frozen_before=lib.owned_source_bundle(G)
lib.need(original==software["original_executing_sources"] and frozen==software["source_files"],"Executed qualified own6 source universe differs")
lib.need(lib.rec(G/"final_source_closure.py")==next(r for r in frozen if Path(r["path"]).name=="final_source_closure.py"),"Actual selected entry differs")
lib.owned_source_readback(original,frozen,original_before,frozen_before)
def exact_json(left,right):
 if type(left)is not type(right):return False
 if isinstance(left,dict):return set(left)==set(right)and all(exact_json(left[k],right[k])for k in left)
 if isinstance(left,list):return len(left)==len(right)and all(exact_json(a,b)for a,b in zip(left,right))
 return left==right
def metadata(p):
 p=lib.safe_path(p);st=p.lstat()
 return dict(bytes=st.st_size,inode=st.st_ino,mtime_ns=st.st_mtime_ns,mode=stat.S_IMODE(st.st_mode),nlink=st.st_nlink,regular=stat.S_ISREG(st.st_mode),nonlink=not stat.S_ISLNK(st.st_mode))
def readonly(p):
 value=metadata(p)
 lib.need(value["regular"] is True and value["nonlink"] is True and value["mode"]==0o444 and value["nlink"]==1,"Declared readonly nonlink regular single-link control required")
 return value
def duplicate_guard(pairs):
 value={}
 for key,item in pairs:
  lib.need(key not in value,"Duplicate input JSON key")
  value[key]=item
 return value
def reject_nonfinite(value):
 raise ValueError("Nonfinite input JSON value")
rm=readonly(REQUEST);hm=readonly(HANDOFF)
lib.need(rm["bytes"]<=2*1024*1024 and hm["bytes"]<=1024*1024,"Bounded fixed request/HUMAN required")
request=lib.rec(REQUEST);handoff=lib.rec(HANDOFF)
q=json.loads(REQUEST.read_text("utf-8"),object_pairs_hook=duplicate_guard,parse_constant=reject_nonfinite)
lib.need(set(q)=={"schema","root_owned","metadata_scope","targets"}and q["schema"]=="final-source-additional-control-pin-request.v1"and q["root_owned"]is True and isinstance(q["metadata_scope"],str),"Exact fixed additional-control request required")
targets=q["targets"];lib.need(isinstance(targets,list)and 1<=len(targets)<=2000,"Finite explicitly reviewed targets required")
names=set();captured=[]
for row in targets:
 lib.need(isinstance(row,dict)and set(row)=={"path","input_kind","metadata","roles","required_as","preservation_route"}or isinstance(row,dict)and set(row)=={"path","input_kind","metadata","roles","required_as","preservation_route","source_public_destination"},"Exact fixed target fields required")
 lib.need(isinstance(row["path"],str)and row["path"]not in names and row["input_kind"]in{"SOURCE","DOC","CONTROL"}and row["roles"]==["final_delivery_tools"]and row["required_as"]in[["SOURCE","SEED"],["SEED"],["LATE_COMPOSER_SOURCE_HISTORY","INDEX_ONLY"],["LATE_COMPOSER_ONLY"]]and isinstance(row["preservation_route"],str),"Finite unique SOURCE/DOC/control coverage required")
 if "source_public_destination"in row:
  lib.need(isinstance(row["source_public_destination"],str),"Source public destination must be a string");lib.destination(row["source_public_destination"])
 names.add(row["path"]);expected=row["metadata"]
 lib.need(isinstance(expected,dict)and set(expected)=={"bytes","inode","mtime_ns","mode","nlink","regular","nonlink"}and all(type(expected[k])is int and expected[k]>=0 for k in ("bytes","inode","mtime_ns","mode","nlink"))and expected["mode"]==0o444 and expected["nlink"]==1 and expected["regular"]is True and expected["nonlink"]is True,"Exact Python integer target metadata required")
 p=lib.safe_path(row["path"]);before=readonly(p)
 lib.need(exact_json(before,expected),"Fixed target metadata fork")
 receipt=lib.rec(p);after=readonly(p)
 lib.need(exact_json(before,after)and receipt["path"]==row["path"]and receipt["bytes"]==expected["bytes"],"Target drift while hashing")
 captured.append(dict(input_kind=row["input_kind"],receipt=receipt,metadata_before=before,metadata_after=after,coverage={k:v for k,v in row.items()if k not in ("path","input_kind","metadata")}))
lib.need(readonly(REQUEST)==rm and readonly(HANDOFF)==hm and lib.rec(REQUEST)==request and lib.rec(HANDOFF)==handoff,"Fixed request/HUMAN drift after capture")
lib.owned_source_readback(original,frozen,original_before,frozen_before);lib.need(lib.conditional_core_runtime()==runtime,"Qualified source/CORE drift after targets")
software_control_readback()
OUT=lib.safe_path(S/"runs"/("final_source_additional_control_pins_"+jid))
lib.need(not OUT.exists()and not OUT.is_symlink(),"Exclusive absent fixed-control output namespace required")
OUT.mkdir(mode=0o755,exist_ok=False)
def persist_control(name,obj):
 path=OUT/name
 data=(json.dumps(obj,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
 with path.open("xb")as stream:
  stream.write(data);stream.flush();os.fsync(stream.fileno());os.fchmod(stream.fileno(),0o444)
 return lib.rec(path)
obj=dict(schema="root-fixed-additional-source-control-pin-capture.v1",status="ACTUAL_FIXED_ADDITIONAL_SOURCE_CONTROL_PINS_CPU_CAPTURED_NOT_SOURCE_AUDIT_STAGE_OR_SCIENCE",actual_job_id=jid,allocation=allocation,request=request,handoff=handoff,software_acceptance=SOFTWARE,source_files=frozen,original_executing_sources=original,conditional_core_runtime=runtime,source_metadata_original_before=original_before,source_metadata_frozen_before=frozen_before,target_n=len(captured),captures=captured,software_control_receipts=software_control_receipts,software_control_metadata_before=software_control_metadata_before,software_control_metadata_after=[lib.stable_metadata(lib.verify(r,True))for r in software_control_receipts],software_evidence_pre_end_afteroutput_bound=True,whole6_source_prepost_PASS=True,conditional_runtime_prepost_PASS=True,all_target_metadata_prepost_PASS=True,only_declared_SOURCE_DOC_CONTROL_bytes_read=True,scientific_receipt_children_read_or_hashed=False,explicit_qualified_software_SOURCE_and_CONTROL_children_checked=True,historical_Slurm_queried=False,compiler_or_tests_or_new_software_executed=False,new_parent_permissions=False,scientific_or_cost_computation=False,source_staged=False,published=False,ACTIVE_changed=False,own_created_controls_and_full_capture_LATE_COMPOSER_ONLY_NOT_OPERATIVE_LIB_SEED=True)
descriptor=persist_control("capture.json",obj)
lib.need(lib.read(lib.verify(descriptor,True))==obj,"Actual full capture output reread differs")
for value in captured:
 p=Path(value["receipt"]["path"]);lib.need(exact_json(readonly(p),value["metadata_after"])and lib.rec(p)==value["receipt"],"Fixed target drift after output")
lib.need(readonly(REQUEST)==rm and readonly(HANDOFF)==hm and lib.rec(REQUEST)==request and lib.rec(HANDOFF)==handoff,"Request/HUMAN changed after output")
lib.owned_source_readback(original,frozen,original_before,frozen_before);lib.need(lib.conditional_core_runtime()==runtime,"Qualified source/CORE drift after output")
software_control_readback()
OUT.chmod(0o555)
print(json.dumps(dict(status=obj["status"],capture=descriptor,request=request,handoff=handoff,target_n=len(captured)),sort_keys=True),flush=True)
ROOT_FIXED_ADDITIONAL_CONTROL_PIN_CAPTURE
```
