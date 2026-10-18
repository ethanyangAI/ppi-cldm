# Root fixed materialization launcher SOURCE pin from software16390 — UNEXECUTED SOURCE preparation

This distinct operational text reuses the reviewed Root16454 fixed own-byte capture program. Only its fixed input namespace changes. Current exact software16390/90, literal G6/SWA6509 full pins, source12/software4/CORE pre-end-afteroutput, current strong CPU readiness, bounds and output lifecycle remain unchanged. No new software/API, compiler, contracts, historical Slurm, scientific child IO or Source audit is authorized by this text.

Actual control16454 captured1915 own-byte tuples and completed0:0/23sCPU1/GPU0 actualguard. CAP2290948/2c438edaef9016f249386a96b6f30b846809d7abe1c2fb2f7548271ebc2e43af and terminalRO44663 were fully read back by Root and independent reviewers. Its1734 Source-history copies had122 rows/61 unique FP outside the known Source pool. Root+independents have located60 original Source receipts from actual13275 vendor inventories,13289 source_files[6:9],13281 source_records[0], matching120 copy rows. Saved Source identities are not current original-byte acceptance.

The remaining1446-byte launcher has no persisted complete original-path CPU tuple: failed16338/16357 retained copied Source bytes and did not reach closure/inclusion writers. This new capture closes that prerequisite using the explicit frozen launcher path established by actual13281 source/runtime history and the directly reviewed launcher copy command. The existing CPU-captured copy fingerprint1446/db57007960bab5a829df92d5534ecf8663dd2271fcf9ef3a20cce80c7fee31a2 is an expected comparison value, not a fabricated original receipt or a hash inferred from its filename. Root must compare the newly emitted actual original tuple to both actual16454 copy tuples after terminal success. A mismatch remains a Source identity failure.

The separately reviewed fixed request is pending/final_source_materialization_launcher_original_pin_from16390_v1/request.json and sibling HANDOFF.md. Its finite two-target roster contains ONLY frozen/rfd_cache_materialization_v2_13281/code/materialization_cpu.sbatch and this Human at handoffs/ROOT_FIXED_MATERIALIZATION_LAUNCHER_SOURCE_PIN_FROM16390_20261015.md. Both must already be readonly0444, regular, nlink1, nonlink ancestry with exact Python integer metadata. No pending original, data, cache, weights, scientific receipt or children are captured. The launcher belongs to default_workflow_integration source history; operational pin coverage shares final_delivery_tools without changing existing roles. Its public original-source destination follows the unchanged exact_source_aliases recipe only if the actual captured tuple matches the known copy FP. This Human has a distinct delivery_tools/human_history source destination.

Root finalizes/reviews/seals this Human before request/HANDOFF finalization so its own bytes can be captured as an explicit DOC row. The request has no future SHA/null placeholder or selftarget. Schema final-source-additional-control-pin-request.v1/root_ownedtrue/metadata_scope FIXED_SOURCE_DOC_CONTROL_BYTES_ONLY_NO_SCIENTIFIC_RECEIPT_CHILD_IO and all four existing ordered dispositions remain unchanged; these two targets require [SOURCE,SEED]. Bounds stay<=2000/request2MiB/H1MiB. Input request/HANDOFF ownCPUtuples, wholeCAP and its created claims/readiness/raw/logs/terminal are LATEComposer evidence, never ownPlan prerequisites. Existing16454/16390/16338/16357/16323/15426, oldplans and all originals remain immutable.

Envelope: organ/CPU1/task1/8G/00:10:00/GPU0requested/accountu21111210118/qosnormal/jobname test9_source_additional_control_pins_cpu/chdirS/logs source_additional_control_pins_%j.out/.err. CORE-B/no-I/emptyCUDA/JAXcpu/PYTHONNOUSER1/bytecodeoff/PYTHONPATHunset/BLAS-OMP-MKL1. Strict all present TRES GPU namespaces and unique current actual RUNNING six-column row precede hashes/import; 60s/30attempts/RPC5/nullRC+partialraw preserved. Qualified lib.cpu() freshly verifies actual CPU1/GPU0. Exclusive output runs/final_source_additional_control_pins_ACTUALJOB/capture.json uses flush/fsync/0444/fullreread/O555 and final CPU descriptor only after every check.

Root alone may submit one new control job after Root+two whole Human/request reviews, metadataRO and independent readback. Root requires actual COMPLETED0:0, whole content, terminal RO and independent readback before original Source reuse or PlanV3. No oldjob resubmit/requeue/amend or heartbeat duplicate. No Source staging/Git/public/package/extract/realrestore/ACTIVE change. Overall delivery remains incomplete and computational only.

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
if sys.flags.optimize != 0:
 raise ValueError("Unoptimized Python required for qualified operational capture")
G=S/"runs/final_source_vendor_log_leaf_software_16390/runner"
P=S/"pending/final_source_closure_v3_fixturefix3_vendor_log_leaf1"
REQUEST=S/"pending/final_source_materialization_launcher_original_pin_from16390_v1/request.json"
HANDOFF=REQUEST.with_name("HANDOFF.md")
SOFTWARE={"path":str(S/"runs/final_source_vendor_log_leaf_software_16390/acceptance.json"),"bytes":6509,"sha256":"44a979371f5764bb3b4766546f333dd518afad7ed2118074be8f67b9628312aa"}
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
 ("final_source_closure.py",79372,"bd353bfbcefd02fc087298bdaa3dc39b7976ce1aeabeead8fc22979b36812fe9"),
 ("test_final_source_closure.py",55559,"1d686539e5b47f2c6588500a8475c6c04ef0d7b3414ad9acde93812e212a3aee"),
 ("final_source_cpu.sbatch",1585,"2f31f7483394823e423927797998153dfe5ab9c4b6f80767a8f8d7e2fb61d0e6"),
 ("HANDOFF.md",14897,"059ea12fbb6962811f76f6edc27be837609a76909228431d4c398a3fb713f5e2"),
 ("FINAL_SOURCE_CHECKLIST.md",3517,"9eb23a50b1092639e73f64f4771c0bbeab195249d172f7cb5a092744c1d98b81"),
 ("final_source_context_adapter.py",8888,"19fbc69b7339abb7091ea51ca3520e8ee52bdda83835d4c83190ee9892aaaded")]
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
lib.need(set(q)=={"schema","root_owned","metadata_scope","targets"}and q["schema"]=="final-source-additional-control-pin-request.v1"and q["root_owned"]is True and q["metadata_scope"]=="FIXED_SOURCE_DOC_CONTROL_BYTES_ONLY_NO_SCIENTIFIC_RECEIPT_CHILD_IO","Exact fixed additional-control request required")
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
