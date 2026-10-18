# Root fixed NEW PlanV2 own-SHA control capture from actual15368/15426 — REV1

SOURCE/HUMAN operational preparation only. This is not new software, scientific acceptance, production Source audit, stage, publication, archive, restore or ACTIVE. The sole new pureCPU job may be submitted by Root only after the actual915505B PlanV2 and33009B HANDOFF pass Root plus two independent whole STATIC reviews and metadata-only readonly seal. The current REV1 ROOTDOC itself must also pass whole STATIC review and be0444 before submission; readonly() enforces this without any waiver. No job ID or own Plan SHA is known or invented here.

Exact inputs: pending/final_source_plan_from14706_14925_15368_15426_v2/{final_source_plan.json,HANDOFF.md}, 915505/33009 bytes, inodes144115543165753490/491, mtime_ns1792041780000000000. Use actual qualified G=runs/final_source_inherited_entries_software_15368/runner OWN6 and SW6554/40c9d1ecaccb8d549bb98cf0d2fb89d62fe3a7e26144b5e69114e34e75173eda. Original P=pending/final_source_closure_v3_fixturefix2_inherited_entrypoints1 OWN6 stays unchanged. The entire previous15426 capture745012/758d0da8d9c6f90cc891c7ad90f888365258335d85b92697496683a7dc8ee7e4 and actual terminal metadata seal30996 are CONTROL-own bytes only; do not recurse their receipt children. This job hashes actual new Plan/HANDOFF and this human control itself; all output/claim/readiness/raw/log/terminal proofs are LATE Composer controls and cannot be prerequisites of their own Plan.

Root envelope: new distinct name test9_source_plan_v2_ownsha_cpu; organ/accountu21111210118/qosnormal/task1/CPU1/8G/10min; request no GPUs and actual current allocated GPU0. WorkDir S. New primary claim and output namespaces must be exclusive/absent. Use only this body through Root sbatch --wrap, R/env/core/bin/python -B, CUDA_VISIBLE_DEVICES empty/JAX_PLATFORMS cpu/PYTHONNOUSERSITE1/PYTHONDONTWRITEBYTECODE1/PYTHONPATH unset/OPENBLAS-OMP-MKL1. No -I, no old frozenG15118 phase2 path, no unqualified or pending source execution; only the exact accepted G15368 library is loaded, no historical Slurm, no compiler/tests/Cost/models/scientific receipt children.

The current unique RUNNING owner/account/organ CPU1/task1/8G10 name and all present scontrol TRES GPU namespaces are checked first. Actual own sacct six-column RUNNING readiness is bounded60 seconds/30 attempts/RPC5sec with timeout partial raw/nullRC and no proxies. Only after actual readiness, stdlib verifies accepted SW and full six frozen Source bytes/readonly single-link nonlink ancestry/exact six-directory roster before importlib exec_module. Qualified lib.cpu() independently re-queries current allocation. Original/frozen own6, accepted CORE conditional byte+stable identity, and software controls4 are checked before/end/afteroutput. Plan content parsing is pure control shape, all scientific child receipt IO forbidden. Final CPU descriptor stdout is emitted only after output fsync/444/full reread/end/afteroutput checks and outputdir555.

Require actual final stdout tuples, fresh exact COMPLETED0:0 terminal and actual running GPU0 basis, then Root plus independent full readback and metadata-only readonly seal before deriving a NEW adapter request. The frozen launcher hardcodes P; future production audit must use actual G15368 frozen adapter direct CORE-B with Root readiness, CPU1/16G30 and mandatory65 producer. None of those future gates is accepted by this control.

Full fixed control body follows. It is a reviewed operational wrap, not a new source library API or software qualification.

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
D = S / "submissions" / ("source_plan_v2_ownsha_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_source_plan_v2_ownsha_cpu", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:10:00", "MinMemoryNode": "8G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/8G10/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-plan-v2-own-sha-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_PLAN_V2_OWN_SHA_CAPTURE_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "capture_program_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_PLAN_V2_OWN_SHA_CAPTURE_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_PLAN_V2_OWN_SHA_CAPTURE_NOT_EXECUTED"
obj = {"schema": "root-current-owned-plan-v2-own-sha-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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


# Only after current owned CPU1/GPU0 readiness; qualified source API only.
import importlib.util,hashlib
R=Path("/lustre/users/u21111210118/projects/test9")
G=S/"runs/final_source_inherited_entries_software_15368/runner"
P=S/"pending/final_source_closure_v3_fixturefix2_inherited_entrypoints1"
PLAN=S/"pending/final_source_plan_from14706_14925_15368_15426_v2/final_source_plan.json"
HANDOFF=PLAN.with_name("HANDOFF.md")
ROOTDOC=S/"handoffs/ROOT_FIXED_NEW_PLAN_V2_OWN_SHA_CAPTURE_FROM15368_15426_20261015_REV1.md"
PRIOR={"path":str(S/"runs/final_source_additional_control_pins_15426/capture.json"),"bytes":745012,"sha256":"758d0da8d9c6f90cc891c7ad90f888365258335d85b92697496683a7dc8ee7e4"}
SEAL=S/"submissions/final_source_additional_control_pins15426_actual_terminal_metadata_seal/receipt.json"
SOFTWARE={"path":str(S/"runs/final_source_inherited_entries_software_15368/acceptance.json"),"bytes":6554,"sha256":"40c9d1ecaccb8d549bb98cf0d2fb89d62fe3a7e26144b5e69114e34e75173eda"}
def require(value,message):
 if not value:raise ValueError(message)
def preimport_source(path,n,h):
 path=Path(path);path.relative_to(R)
 for node in [path]+list(path.parents):
  if node==R.parent:break
  require(not stat.S_ISLNK(node.lstat().st_mode),"Preimport SOURCE ancestry must be nonlink")
 st=path.lstat();require(stat.S_ISREG(st.st_mode)and stat.S_IMODE(st.st_mode)==0o444 and st.st_nlink==1,"Qualified readonly single-link SOURCE required before import")
 raw=path.read_bytes();require(len(raw)==n and hashlib.sha256(raw).hexdigest()==h,"Qualified SOURCE/SWA bytes fork before import")
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
require(swa["source_files"]==expected and stat.S_IMODE(G.lstat().st_mode)==0o555 and not G.is_symlink()and {x.name for x in G.iterdir()}=={x[0]for x in pins},"Exact qualified frozen own6 required")
for name,n,h in pins:preimport_source(G/name,n,h)
sp=importlib.util.spec_from_file_location("root_new_plan_v2_ownsha_qualified_lib",G/"final_source_closure.py")
lib=importlib.util.module_from_spec(sp);sp.loader.exec_module(lib)
allocation=lib.cpu();runtime=lib.conditional_core_runtime()
software=lib.read(lib.verify(SOFTWARE,True));ct=lib.read(lib.verify(software["contracts"],True))
lib.software_shape(software,ct);lib.verify(ct["log"],True)
lib.software_snapshot_shape(software,lib.read(lib.verify(software["source_snapshot"],True)))
software_controls=[SOFTWARE,software["contracts"],ct["log"],software["source_snapshot"]]
software_before=[lib.stable_metadata(lib.verify(r,True))for r in software_controls]
require(software["conditional_core_runtime"]==runtime,"Qualified software/current CORE differs")
original,original_before=lib.owned_source_bundle(P);frozen,frozen_before=lib.owned_source_bundle(G)
require(original==software["original_executing_sources"]and frozen==software["source_files"],"Original/frozen SOURCE universe fork")
def readonly(p):
 p=lib.safe_path(p);s=p.lstat()
 require(stat.S_ISREG(s.st_mode)and stat.S_IMODE(s.st_mode)==0o444 and s.st_nlink==1,"Readonly single-link control required")
 return lib.stable_metadata(p)
require(PLAN.lstat().st_size==915505 and PLAN.lstat().st_ino==144115543165753490 and PLAN.lstat().st_mtime_ns==1792041780000000000,"Fixed actual NEW Plan metadata fork")
require(HANDOFF.lstat().st_size==33009 and HANDOFF.lstat().st_ino==144115543165753491 and HANDOFF.lstat().st_mtime_ns==1792041780000000000,"Fixed actual NEW Handoff metadata fork")
controls=[PLAN,HANDOFF,ROOTDOC,Path(PRIOR["path"]),SEAL]
before=[readonly(p)for p in controls]
prior=lib.read(lib.verify(PRIOR,True))
require(prior["actual_job_id"]=="15426"and prior["target_n"]==607 and prior["allocation"]["allocated_CPUs"]==1 and prior["allocation"]["allocated_gpus"]==0,"Actual predecessor607 control required")
seal=lib.read(SEAL)
require(SEAL.lstat().st_size==30996 and seal["status"]=="ACTUAL_FIXED607_CONTROL_PIN_CAPTURE_TERMINAL_METADATA_READBACK_PASS_NOT_SOURCE_AUDIT_STAGE_OR_SCIENCE"and seal["actual_CPU_stdout"]["capture"]==PRIOR,"Actual accepted predecessor terminal RO required")
# Pure control JSON shape only; no receipt child stat/read/resolve/hash.
def unique_pairs(items):
 d={}
 for k,v in items:
  require(k not in d,"Duplicate control JSON key");d[k]=v
 return d
q=json.loads(PLAN.read_text("utf-8"),object_pairs_hook=unique_pairs)
roles=["formal13260_terminal_v3","native74_cache_catalog","native74_cache_binding","reference_free_e2e","formal_common_review","independent_statistics","scientific_report","final_delivery_tools","default_workflow_integration"]
require(q["schema"]=="final-source-closure-plan.v3"and q["root_owned"]is True and q["public_source_only"]is True and q["no_scientific_settings_change"]is True,"Exact actual Plan control shape required")
require([m["role"]for m in q["modules"]]==roles and len(q["context_parent_seeds"])==17 and len(q["aliases"])==3 and q["library_software_acceptance"]==SOFTWARE,"Actual9/17/3/current65 shape required")
require(sum(len(m["sources"])for m in q["modules"])==480 and sum(len(m["seeds"])for m in q["modules"])==1935 and len(q["late_Composer_additional_control_history"])==27,"Fixed reviewed NEW Plan universe required")
receipts=[lib.rec(p)for p in controls]
def final_readback():
 require([readonly(p)for p in controls]==before and [lib.rec(p)for p in controls]==receipts,"Owned Plan/control bytes or stable metadata changed")
 lib.owned_source_readback(original,frozen,original_before,frozen_before)
 require(lib.conditional_core_runtime()==runtime,"Qualified CORE changed")
 require([lib.stable_metadata(lib.verify(r,True))for r in software_controls]==software_before,"Qualified software evidence changed")
final_readback()
OUT=lib.safe_path(S/"runs"/("final_source_plan_v2_ownsha_"+jid))
require(not OUT.exists()and not OUT.is_symlink(),"Exclusive absent NEW Plan descriptor output required")
OUT.mkdir(mode=0o755,exist_ok=False)
obj=dict(schema="root-new-plan-v2-own-sha-capture.v1",status="ACTUAL_NEW_PLAN_V2_OWN_SHA_CPU_CAPTURED_NOT_SOURCE_AUDIT_STAGE_OR_SCIENCE",actual_job_id=jid,allocation=allocation,plan=receipts[0],handoff=receipts[1],root_control_human=receipts[2],accepted_predecessor607_capture=receipts[3],accepted_predecessor607_terminal_metadata_seal=receipts[4],software_acceptance=SOFTWARE,source_files=frozen,original_executing_sources=original,source_metadata_original_before=original_before,source_metadata_frozen_before=frozen_before,conditional_core_runtime=runtime,software_control_receipts=software_controls,software_control_metadata_before=software_before,software_control_metadata_after=[lib.stable_metadata(lib.verify(r,True))for r in software_controls],control_metadata_before=before,control_metadata_after=[readonly(p)for p in controls],whole6_source_pre_end_afteroutput_bound=True,conditional_runtime_pre_end_afteroutput_bound=True,software4_control_pre_end_afteroutput_bound=True,control_pre_end_afteroutput_bound=True,plan_child_receipts_shape_only_no_child_IO=True,scientific_receipt_children_read_or_hashed=False,compiler_or_tests_or_new_software_executed=False,historical_Slurm_queried=False,source_audit_executed=False,source_staged=False,published=False,ACTIVE_changed=False,own_created_controls_LATE_COMPOSER_ONLY_NOT_PLAN_PREREQUISITES=True)
data=(json.dumps(obj,indent=2,ensure_ascii=False)+"\n").encode("utf-8");path=OUT/"capture.json"
with path.open("xb")as f:f.write(data);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
descriptor=lib.rec(path);require(lib.read(lib.verify(descriptor,True))==obj,"Actual NEW Plan output reread fork")
final_readback();OUT.chmod(0o555)
print(json.dumps(dict(status=obj["status"],capture=descriptor,plan=receipts[0],handoff=receipts[1],root_control_human=receipts[2],predecessor_terminal=receipts[4]),sort_keys=True),flush=True)

```

No source identity/17parent/alias/JSON content/general relative reader permission changes. Preserve original oldPlan628318/fab604 and all prior failures, source, guides Main+ERR1-10, checkpoints and predictions. Keep existing heartbeat active; never duplicate15426 or this eventual unique primary claim. Computational evidence only; no binding/blockade/clinical/arbitrary-pair/superiority or full completion claim.

REV1 preserves the original20200B proposal unexecuted. Changes are limited to the two human execution/read-only clarifications and the literal ROOTDOC self path in the body pointing to this REV1 document. No qualified library/source/API, job envelope, guard, child-IO boundary or output lifecycle is changed.
