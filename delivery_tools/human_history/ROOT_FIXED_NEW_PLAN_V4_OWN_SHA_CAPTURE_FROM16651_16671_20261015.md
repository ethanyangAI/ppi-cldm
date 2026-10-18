# ROOT fixed NEW PlanV4 own-SHA operational capture from qualified16651 and six-Doc16671 — 2026-10-15

This is a Root operational control specification, not new software acceptance or Source production acceptance. Its embedded Python must run only inside one new Root-owned organ CPU allocation after Root and two whole static reviews, this Human readonly seal and independent metadata readback. No login hash/import/compile/test is authorized by this document.

## Actual prerequisites and exact scope

- Actual software16651: COMPLETED0:0/25s/CPU1/GPU0/16G30organ; 122 named PASS/zero failures/errors/skips; acceptance6590 SHA5a8bfa759754985cd72bd35cb50192eb2aefef0df3fc73c28aebd4aed00adfe5. Frozen runner and original own6 remain immutable.
- Actual six-Doc16671: COMPLETED0:0/4s/CPU1/GPU0/8G10organ; capture30476 SHAbe19b601120c1849992df023d0d1b88c99e1081c7ca3f424c1990dfab84ec9c7; terminal metadata seal62365 Root+independent whole PASS.
- Actual PlanV4 final_source_plan.json1941606 and HANDOFF44899 in pending/final_source_plan_from14706_14925_16651_16671_v4 have Root+two whole static PASS and metadata RO32572+independent PASS. Plan638 Source memberships/577 destinations/3809 Seed memberships3736 unique; original nine roles, nine gates plus two Cost gates, 17 ordered context parents, three aliases, four maps and Base683 remain. Actual own SHA is UNKNOWN until this CPU capture.
- The exact post-RO Plan/Handoff metadata below comes from actual32572.after_files using Python exact integers. Own Plan/H/P ctime1792064285000000000 differs from receipt ctime1792064286000000000. Do not round or replace either.
- Exact seven own controls only: NEW Plan, its HANDOFF, this Root Human, actual16671 capture, actual16671 terminal seal, actual16651 software terminal seal, actualPlanV4 metadata seal. It hashes their own bytes, never receipt/table child paths. All captured scientific receipt children and worker bytes remain outside this operational capture.
- Prior capture/seal internal shapes and saved terminal row are checked as control bytes. No historical Slurm query and no reexecution of predecessor jobs or software tests.
- The Plan control is parsed with duplicate/nonfinite rejection and receipt_shape ONLY for its existing gate/source/seed/context-parent descriptors; those child descriptors cause no stat/open/hash/resolve. No generic Reader/parent/alias/source-identity changes.

## Exact allocation and isolation

One new sbatch only: job name test9_source_plan_v4_ownsha_cpu, account u21111210118, qos normal, partition organ, nodes1, ntasks1, cpus-per-task1, mem8G, time00:10:00, chdir S; no GPU request and no resource/time override. Root uses an exclusive primary claim; timeout/null return code or ambiguous submission is unresolved, never authorization to duplicate.

The wrap sets CUDA_VISIBLE_DEVICES empty, JAX_PLATFORMS cpu, PYTHONNOUSERSITE1, PYTHONDONTWRITEBYTECODE1, OPENBLAS/OMP/MKL1, unsets PYTHONPATH, and invokes the qualified conditional CORE interpreter with -B and no -I. The program first records actual current scontrol all present TRES/AllocTRES/ReqTRES and unique six-column RUNNING sacct owner/account/organ CPU1/GPU0. Maximum60s/30 attempts/RPC5s, raw partial replies and null rc on timeout retained. No Source/control hash or library import occurs before actual current readiness. The unchanged qualified G16651.cpu guard then freshly requeries current allocation.

## Source and own-output invariants

Literal SWA and six frozen Source SHA/bytes/readonly single-link nonlink ancestry are checked with stdlib before exec_module. Original/frozen Source12 must match actual qualified software snapshot FULL stable metadata (ctime included), bytes and SHA. Qualified software controls4 and conditional CORE logical/resolved metadata/scalar are checked before, end, after output, and after final readonly reread. No Core binary redistribution.

Own seven controls and readonly Plan directory555 are checked before, end, after output and after final readonly reread. NEW output runs/final_source_plan_v4_ownsha_JOB must be absent; capture.json is exclusive xb, flushed/fsynced, mode444, fully reread; output directory555, readonly reread plus all final checks again. Final stdout descriptor is emitted only after those checks. Fresh terminal COMPLETED0:0 plus final CPU stdout, full saved content/current metadata, Root and independent readbacks and terminal readonly seal are mandatory before accepting Plan own SHA.

## Late-history and future boundaries

This Human's actual CPU tuple is emitted by its own job. This Human, its ownSHA capture, primary claims, readonly seal, readiness/raw/logs/terminal controls are explicit LATE Composer controls and later finite Source/DOC publication where applicable; none is an operative prerequisite of its own Plan. Preserve all earlier controls, failure rosters, dated scheduler/raw, source histories and Human originals. Thirty-two new Plan late controls are only an additional subset of that full preservation obligation. Do not edit Plan to introduce this job's output or self-cycle.

No compiler/tests/new software, Worker/scientific bytes, Cost/statistics/model scoring, Source audit, staging, Git/GitHub/publication/package/extract/restore/default/ACTIVE changes occur here. Software122 is software only; this capture is operational control only. Actual Source audit/stage/private full history bundle/public complete-tree draft PR and real readback/packaging/isolated restore/G13558/G14692ROOT298/ACTIVE remain future gates. Computational-only evidence remains distinct from experimental binding/blockade/clinical/arbitrary-pair reliability or superiority.

## Exact CPU program

The following sole Python block is the entire operational payload. Root must extract this exact block; no dynamic source edits or Reader patches.

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
D = S / "submissions" / ("source_plan_v4_ownsha_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_source_plan_v4_ownsha_cpu", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:10:00", "MinMemoryNode": "8G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/8G10/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-plan-v4-own-sha-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_PLAN_V4_OWN_SHA_CAPTURE_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "capture_program_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_PLAN_V4_OWN_SHA_CAPTURE_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_PLAN_V4_OWN_SHA_CAPTURE_NOT_EXECUTED"
obj = {"schema": "root-current-owned-plan-v4-own-sha-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
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
G=S/"runs/final_source_finite_worker_alias_software_16651/runner"
P=S/"pending/final_source_closure_v3_fixturefix4_finite_worker_alias1"
SOFTWARE={"path":str(S/"runs/final_source_finite_worker_alias_software_16651/acceptance.json"),"bytes":6590,"sha256":"5a8bfa759754985cd72bd35cb50192eb2aefef0df3fc73c28aebd4aed00adfe5"}
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
pins=[["final_source_closure.py",164179,"4106c23e585c0e66c5541b22c10af8b80dce277dbc4c137dc037d3a87e896956"],["test_final_source_closure.py",78857,"607ddb717d51d93e89f786e5f4cad5ea2ec6727d91c4c27c9694e77c68dbfe67"],["final_source_cpu.sbatch",1613,"3cb2d517d0763b587218f3587ca87e8cdb97ed148926b4c936bee71c9b2e8c6f"],["HANDOFF.md",15973,"b63c1bf9ded2adc24e09b4ca795345387b58ad689886e4355ebd67b09ebbe5f3"],["FINAL_SOURCE_CHECKLIST.md",3280,"7b7a6ca1fc5ef2d49968af033310557d28684ac97aaaa5f944d819928a01cb56"],["final_source_context_adapter.py",9850,"2db4ff9a01d189eea237acadf432fb7046292b927ba08fbb9522aff2b839785e"]]
expected=[dict(path=str(G/name),bytes=n,sha256=h)for name,n,h in pins]
preimport_need(swa["source_files"]==expected and G.is_dir()and not G.is_symlink()and stat.S_IMODE(G.lstat().st_mode)==0o555 and {x.name for x in G.iterdir()}=={x[0]for x in pins},"Exact accepted frozen own6 directory required before import")
for name,n,h in pins:preimport_source(G/name,n,h)
sp=importlib.util.spec_from_file_location("root_fixed_plan_v4_ownsha_lib",G/"final_source_closure.py")
lib=importlib.util.module_from_spec(sp);sp.loader.exec_module(lib)
allocation=lib.cpu()
runtime=lib.conditional_core_runtime()
software=lib.read(lib.verify(SOFTWARE,True));ct=lib.read(lib.verify(software["contracts"],True))
lib.software_shape(software,ct);lib.verify(ct["log"],True)
snapshot=lib.software_snapshot_shape(software,lib.read(lib.verify(software["source_snapshot"],True)))
software_control_receipts=[SOFTWARE,software["contracts"],ct["log"],software["source_snapshot"]]
software_control_metadata_before=[lib.stable_metadata(lib.verify(r,True))for r in software_control_receipts]
def software_control_readback():
 lib.need([lib.stable_metadata(lib.verify(r,True))for r in software_control_receipts]==software_control_metadata_before,"Qualified software evidence bytes/stable metadata changed")
 return True
software_control_readback()
lib.need(software["conditional_core_runtime"]==runtime,"Qualified software/current conditional CORE differs")
original,original_before=lib.owned_source_bundle(P);frozen,frozen_before=lib.owned_source_bundle(G)
lib.need(original==software["original_executing_sources"] and frozen==software["source_files"],"Executed qualified own6 source universe differs")
lib.need(original_before==snapshot["original_metadata_before"] and frozen_before==snapshot["frozen_metadata_before"],"Actual Source12 stable metadata must equal qualified software snapshot")
for rows in (original_before,frozen_before):
 lib.need(all(x["nlink"]==1 and stat.S_IMODE(x["mode"])==0o444 for x in rows),"Exact readonly single-link source12 required")
lib.need(lib.rec(G/"final_source_closure.py")==next(r for r in frozen if Path(r["path"]).name=="final_source_closure.py"),"Actual selected entry differs")
lib.owned_source_readback(original,frozen,original_before,frozen_before)

PLAN=S/"pending/final_source_plan_from14706_14925_16651_16671_v4/final_source_plan.json"
HANDOFF=PLAN.with_name("HANDOFF.md")
ROOTDOC=S/"handoffs/ROOT_FIXED_NEW_PLAN_V4_OWN_SHA_CAPTURE_FROM16651_16671_20261015.md"
PRIOR={"path":str(S/"runs/final_source_additional_control_pins_16671/capture.json"),"bytes":30476,"sha256":"be19b601120c1849992df023d0d1b88c99e1081c7ca3f424c1990dfab84ec9c7"}
TERMINAL=S/"submissions/final_source_v4_doc_pins16671_actual_terminal_metadata_seal/receipt.json"
SWTERMINAL=S/"submissions/final_source_finite_worker_alias_software16651_actual_terminal_metadata_seal/receipt.json"
PLANRO=S/"submissions/final_source_plan_v4_from16651_16671_metadata_readonly_seal/receipt.json"
def require(value,message):
 if not value:raise ValueError(message)
def readonly(p):
 p=lib.safe_path(p);s=p.lstat()
 require(stat.S_ISREG(s.st_mode)and stat.S_IMODE(s.st_mode)==0o444 and s.st_nlink==1,"Readonly regular single-link own control required")
 return lib.stable_metadata(p)
EXPECTED_PLAN_METADATA={'path': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16651_16671_v4/final_source_plan.json', 'bytes': 1941606, 'inode': 144115643443090856, 'mtime_ns': 1792063791000000000, 'ctime_ns': 1792064285000000000, 'mode': 33060, 'dev': 1119461688, 'nlink': 1, 'uid': 6263900, 'gid': 6263900}
EXPECTED_HANDOFF_METADATA={'path': '/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_plan_from14706_14925_16651_16671_v4/HANDOFF.md', 'bytes': 44899, 'inode': 144115643443090857, 'mtime_ns': 1792063791000000000, 'ctime_ns': 1792064285000000000, 'mode': 33060, 'dev': 1119461688, 'nlink': 1, 'uid': 6263900, 'gid': 6263900}
require(readonly(PLAN)==EXPECTED_PLAN_METADATA and readonly(HANDOFF)==EXPECTED_HANDOFF_METADATA,"Exact actual reviewed NEW Plan/Handoff stable metadata required")
controls=[PLAN,HANDOFF,ROOTDOC,Path(PRIOR["path"]),TERMINAL,SWTERMINAL,PLANRO]
before=[readonly(p)for p in controls]
c=lib.read(lib.verify(PRIOR,True))
require(c["schema"]=="root-fixed-additional-source-control-pin-capture.v1"and c["status"]=="ACTUAL_FIXED_ADDITIONAL_SOURCE_CONTROL_PINS_CPU_CAPTURED_NOT_SOURCE_AUDIT_STAGE_OR_SCIENCE"and c["actual_job_id"]=="16671"and type(c["target_n"])is int and c["target_n"]==6,"Actual qualified six-Doc predecessor own-control required")
require(c["allocation"]["job_id"]=="16671"and c["allocation"]["allocated_CPUs"]==1 and c["allocation"]["allocated_gpus"]==0 and c["software_acceptance"]==SOFTWARE and c["source_files"]==frozen and c["original_executing_sources"]==original,"Actual predecessor qualified software/Source12/allocation differs")
require(c["conditional_core_runtime"]==runtime and c["source_metadata_original_before"]==original_before and c["source_metadata_frozen_before"]==frozen_before and c["software_control_metadata_before"]==c["software_control_metadata_after"]==software_control_metadata_before,"Predecessor actual Source12/software4/Core differs")
seal=lib.read(TERMINAL)
require(TERMINAL.lstat().st_size==62365 and seal["schema"]=="root-source-v4-six-doc-pin-actual-terminal-metadata-seal.v1"and seal["status"]=="ACTUAL_FIXED6_DOC_CAPTURE_CONTENT_AND_TERMINAL_METADATA_READBACK_PASS_NOT_SOURCE_PRODUCTION_ACCEPTANCE"and seal["actual_job_id"]=="16671"and seal["actual_capture"]==PRIOR and seal["actual_target_n"]==6,"Actual qualified six-Doc terminal control differs")
tr=seal["fresh_terminal"]
require(tr["returncode"]==0 and tr["actual_row"]==["16671","COMPLETED","0:0","4","1","test9_source_v4_doc_pins_cpu","u21111210118","u21111210118","organ"],"Actual saved predecessor terminal required, no historical live query")
require(seal["actual_allocation"]==c["allocation"]and seal["protected_inputs_before"]==seal["protected_inputs_after"]and seal["protected_directories_before"]==seal["protected_directories_after"]and seal["conditional_CORE_metadata_before"]==seal["conditional_CORE_metadata_after"]and seal["bytes_inode_mtime_nlink_type_dev_uid_gid_unchanged"]is True,"Predecessor actual current-GPU0/protected metadata basis differs")
swseal=lib.read(SWTERMINAL)
require(SWTERMINAL.lstat().st_size==37513 and swseal["schema"]=="final-source-finite-worker-alias-software-terminal-metadata-seal.v1"and swseal["status"]=="ACTUAL122_SOFTWARE_CONTENT_AND_TERMINAL_METADATA_READBACK_PASS_NOT_SOURCE_PRODUCTION_ACCEPTANCE"and swseal["actual_job_id"]=="16651"and swseal["actual_software_acceptance"]==SOFTWARE and swseal["tests"]==122,"Actual software122 terminal own-control differs")
ps=lib.read(PLANRO)
require(ps["schema"]=="root-final-source-plan-v4-metadata-readonly-seal.v1"and ps["status"]=="ROOT_AND_TWO_WHOLE_STATIC_FINAL_SOURCE_PLAN_V4_METADATA_RO_PASS_NOT_SOURCE_ACCEPTANCE"and ps["after_files"]==[EXPECTED_PLAN_METADATA,EXPECTED_HANDOFF_METADATA],"Actual reviewed Plan/Handoff metadata seal differs")
plan_directory_before=lib.stable_metadata(lib.safe_path(PLAN.parent))
require(plan_directory_before==ps["after_directory"]and stat.S_ISDIR(plan_directory_before["mode"])and stat.S_IMODE(plan_directory_before["mode"])==0o555,"Actual reviewed readonly Plan directory required")
# These prior captures/seals are OWN controls only. No captures, metadata-table
# paths, terminal-raw children or scientific receipt children are stat/open/hash'd.
def unique_pairs(items):
 d={}
 for k,v in items:
  require(k not in d,"Duplicate control JSON key");d[k]=v
 return d
def reject_nonfinite(value):raise ValueError("Nonfinite Plan control JSON forbidden")
def finite_float(value):
 result=float(value);require(result==result and abs(result)!=float("inf"),"Nonfinite exponent in Plan control JSON forbidden");return result
q=json.loads(PLAN.read_text("utf-8"),object_pairs_hook=unique_pairs,parse_constant=reject_nonfinite,parse_float=finite_float)
roles=["formal13260_terminal_v3","native74_cache_catalog","native74_cache_binding","reference_free_e2e","formal_common_review","independent_statistics","scientific_report","final_delivery_tools","default_workflow_integration"]
require(q["schema"]=="final-source-closure-plan.v3"and q["root_owned"]is True and q["public_source_only"]is True and q["no_scientific_settings_change"]is True,"Exact actual Plan control shape required")
require([m["role"]for m in q["modules"]]==roles and len(q["context_parent_seeds"])==17 and len(q["aliases"])==3 and q["library_software_acceptance"]==SOFTWARE,"Actual9/17/3/current122 shape required")
require(sum(len(m["sources"])for m in q["modules"])==638 and sum(len(m["seeds"])for m in q["modules"])==3809 and len(q["plan_v3_original_source_provenance"])==61 and len(q["late_Composer_control_history_from16454"])==83,"Exact reviewed NEW Plan finite universe required")
for m in q["modules"]:
 lib.receipt_shape(m["gate"]["receipt"])
 for s in m["sources"]:lib.receipt_shape(s["receipt"])
 for r in m["seeds"]:lib.receipt_shape(r)
for r in q["context_parent_seeds"]:lib.receipt_shape(r)
receipts=[lib.rec(p)for p in controls]
def final_readback():
 require([readonly(p)for p in controls]==before and [lib.rec(p)for p in controls]==receipts,"Owned seven Plan/control bytes or stable metadata changed")
 require(lib.stable_metadata(lib.safe_path(PLAN.parent))==plan_directory_before,"Readonly Plan directory metadata changed")
 lib.owned_source_readback(original,frozen,original_before,frozen_before);require(lib.conditional_core_runtime()==runtime,"Qualified CORE changed");software_control_readback()
final_readback()
OUT=lib.safe_path(S/"runs"/("final_source_plan_v4_ownsha_"+jid))
require(not OUT.exists()and not OUT.is_symlink(),"Exclusive absent NEW Plan descriptor output required")
OUT.mkdir(mode=0o755,exist_ok=False)
obj=dict(schema="root-new-plan-v4-own-sha-capture.v1",status="ACTUAL_NEW_PLAN_V4_OWN_SHA_CPU_CAPTURED_NOT_SOURCE_AUDIT_STAGE_OR_SCIENCE",actual_job_id=jid,allocation=allocation,plan=receipts[0],handoff=receipts[1],root_control_human=receipts[2],accepted_prior_control_receipts=receipts[3:],software_acceptance=SOFTWARE,source_files=frozen,original_executing_sources=original,source_metadata_original_before=original_before,source_metadata_frozen_before=frozen_before,conditional_core_runtime=runtime,software_control_receipts=software_control_receipts,software_control_metadata_before=software_control_metadata_before,software_control_metadata_after=[lib.stable_metadata(lib.verify(r,True))for r in software_control_receipts],plan_directory_metadata_before=plan_directory_before,plan_directory_metadata_after=lib.stable_metadata(PLAN.parent),control_metadata_before=before,control_metadata_after=[readonly(p)for p in controls],whole6_source_pre_end_afteroutput_bound=True,conditional_runtime_pre_end_afteroutput_bound=True,software4_control_pre_end_afteroutput_bound=True,all7_controls_pre_end_afteroutput_bound=True,plan_child_receipts_shape_only_no_child_IO=True,prior_capture_and_seal_own_bytes_only_no_child_IO=True,scientific_receipt_children_read_or_hashed=False,compiler_or_tests_or_new_software_executed=False,historical_Slurm_queried=False,source_audit_executed=False,source_staged=False,published=False,ACTIVE_changed=False,own_created_controls_LATE_COMPOSER_ONLY_NOT_PLAN_PREREQUISITES=True)
data=(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode("utf-8");path=OUT/"capture.json"
with path.open("xb")as f:f.write(data);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
descriptor=lib.rec(path);require(lib.read(lib.verify(descriptor,True))==obj,"Actual NEW Plan output reread differs")
final_readback();OUT.chmod(0o555)
require(lib.read(lib.verify(descriptor,True))==obj,"Final readonly NEW Plan capture reread differs")
final_readback()
print(json.dumps(dict(status=obj["status"],capture=descriptor,plan=receipts[0],handoff=receipts[1],root_control_human=receipts[2],accepted_prior_control_receipts=receipts[3:]),sort_keys=True),flush=True)

```
