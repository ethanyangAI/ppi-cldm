# ROOT FIXED PLAN V6 OWN SHA CONTROL CAPTURE FROM G16651 AND RECOVERED16847

状态：本文件是新的有限控制 CPU 程序及审查交接文档，尚未执行。只有 Root 与两份完整静态审查通过、只读封存及独立复核完成后，Root 才可独占提交一个 CPU 作业。任何新 Plan SHA 都必须来自该作业真实最终 stdout，并经实际成功终态与完整内容复核；文档不提供未来 SHA 或 Source 审计接受。

已接受的前置控制：16847 实际 COMPLETED 0:0/5 秒，CPU1/GPU0，8G/10min/organ，16:06:52→16:06:57 UTC。完整 capture.json71545 的 CPU SHA 为 4d19a6da7da578f68dab38d80e617acda682827889d2518afda03a7587bfec66，Root 与两份独立完整内容复核通过；终态只读回执 submissions/historical_source2_recovery16847_actual_terminal_metadata_seal/receipt.json222766 已获独立完整元数据 PASS。恢复副本源于实际原始创建记录3360/3362，两段全文仅作为数据，分别通过旧31 2225/75ee295f33b7e11ca48a9ea83ccd9f9bc79461c0b55f755b8e94391d026c7183 和旧87 1633/1d6ed0efed2d63b792cdae304ccc4017d7e3d9e254ff2d7b7c241abd5f0eeb01 的 CPU 全字节检查；两者在新 readonly recovered_sources 中保留原扩展名，旧程序从未执行。当前 canonical Source4 与16832/16847实际值保持不变；原16825失败组件及当时四个实际SHA仍未观测，不追认旧失败。

拟运行范围：仅新 pending/final_source_plan_from14706_14925_16651_16847_v6 的 Plan/HANDOFF、自身文档、Root PlanRO、真实16847恢复CAP/终态、原22有限 controls 和两个实际恢复 Source 的 own-byte SHA。新 Plan 除旧五 aliases 后追加两个精确全身份 aliases，以及 default 模块尾追加两条使用 OLD canonical receipt 的显式 Source 发布行外，其余值、类型、顺序和回退后的原序列化 bytes 必须与不可变 V5 完全一致。新总数640 Source、579 public destinations、3809 seeds、3736 unique seed identities、9 roles、17 parents；默认模块106 Source/41 seeds。纯322身份投影必须全覆盖，此投影不替代未来实际闭包审计。

执行边界：CPU1/task1/8G/10min/organ/GPU0，新名称 test9_source_plan_v6_ownsha_cpu；CORE -B、不使用 -I，CUDA empty/JAX cpu/PYTHONNOUSERSITE/PYTHONDONTWRITEBYTECODE/BLAS-OMP-MKL1、unset PYTHONPATH。先保存当前真实 scontrol 全TRES/GPU命名空间及唯一numeric RUNNING 六列；30次/60秒、RPC5秒，超时保留实际partial raws/returncode null。之后对原+冻结 Source12、四个软件证据 controls 和 CORE 作 literal whole SHA/稳定元数据检查，才允许导入唯一 G16651。随后实际 G.cpu() 必须再查询相同当前分配；无历史 Slurm 查询、Reader/audit/源码编译/软件测试/scientific children/cost/report/model execution。

所有30 own controls、Source12/SW4/Core、当前 canonical4 及新 PlanRO 声明的有限 protected metadata 均在读取前、结束、输出后及最终只读复读保持一致；恢复源的指纹必须不变且只作为数据读取。输出独占新目录，flush/fsync/444，全量复读，目录555，最后再检查全部输入，才能输出真实 CPU descriptor。无替换旧 Source、旧Plan、报告、统计、默认流程、Git、公开仓库、package、restore、ACTIVE 的能力。

生产后序：本作业 own SHA 仅是新 Plan 控制资格，仍需实际成功终态、只读封存、Root+两份内容复核与独立元数据复核。随后另建新 strict13 request，保留有限8 parent views/17 parents/实际当前 G16651 software122，再运行真实 Source production mandatory122 与完整 A/CA/I/C、vendor/worker proofs。只有实际 Source审计通过才可用 NEW inclusion.runner_source_snapshot 执行 CORE -B stage。未来 F 必须显式传入四条旧 Source q.exact_aliases（31/35/87/89），并另传 worker/vendor indices；Plan.aliases 不会自动传播。所有本作业新 claims/readiness/raw/logs/CAP/terminal/PlanH/文档晚期纳入 Composer，不能成为自身 Plan prerequisites；发布所有源文档须独立有限 Source/DOC publisher，seeds 不等于源发布。private full-history bundle、公共同完整树新commit唯一baseline parent/draft PR ATTACH、真实API readback、compose/package、显式CORE extract、全INDEX RAW restore、G13558 metadata/G14692 ROOT298 同pkg/root验证全部仍在后续；ACTIVE最后。

## Exact fixed CPU payload — SOURCE/TEXT ONLY UNTIL QUALIFIED ROOT SUBMISSION

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
D = S / "submissions" / ("source_plan_v6_ownsha_current_sacct_readiness_" + jid)
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
    required = {"JobId": jid, "JobName": "test9_source_plan_v6_ownsha_cpu", "Account": "u21111210118", "Partition": "organ", "JobState": "RUNNING", "NumCPUs": "1", "NumTasks": "1", "CPUs/Task": "1", "TimeLimit": "00:10:00", "MinMemoryNode": "8G"}
    if any(fields.get(k) != v for k, v in required.items()) or not re.fullmatch("u21111210118\\([0-9]+\\)", fields.get("UserId", "")):
        raise ValueError("Actual current owner/name/CPU1/8G10/organ envelope required")
    current_tres_fields = {key: tres(fields[key]) for key in ("TRES", "AllocTRES", "ReqTRES") if key in fields}
    if "TRES" not in current_tres_fields:
        raise ValueError("Actual current TRES field required")
    current_tres = current_tres_fields["TRES"]
except Exception as e:
    obj = {"schema": "root-current-owned-plan-v6-ownsha-sacct-readiness.v1", "status": "CURRENT_SCONTROL_ENVELOPE_FAILED_PLAN_V6_OWN_SHA_NOT_EXECUTED", "actual_job_id": jid, "commands": commands, "reason_type": type(e).__name__, "reason": str(e), "own_plan_hash_capture_entered": False, "original15201_specific_cause_proven": False}
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
status = "CURRENT_REAL_OWNER_CPU1_GPU0_SACCT_READY_PLAN_V6_OWN_SHA_NOT_YET_EXECUTED" if selected is not None else "CURRENT_SACCT_READINESS_WAIT_EXHAUSTED_PLAN_V6_OWN_SHA_NOT_EXECUTED"
obj = {"schema": "root-current-owned-plan-v6-ownsha-sacct-readiness.v1", "status": status, "actual_job_id": jid, "metadata_only": True,
       "current_scontrol_observation": ctl_saved, "current_scontrol_TRES": current_tres,
       "all_present_scontrol_TRES_fields_CPU1_GPU0": current_tres_fields, "attempts": attempts,
       "selected_actual_attempt": selected, "maximum_attempts": 30, "maximum_wait_seconds": 60,
       "environment": {"TZ": "UTC", "SLURM_TIME_FORMAT": "standard", **expected_env},
       "requested_GPUs": 0, "current_allocation_only_no_historical_GPU_inference": True,
       "no_source_or_request_hashes_or_imports_or_tests_by_wait": True,
       "unchanged_library_cpu_guard_will_freshly_requery": True, "actual_queries_not_proxy_or_synthesized_replies": True,
       "own_plan_hash_capture_entered": False, "original15201_specific_cause_proven": False,
       "additional_pin_or_source_audit_stage_Git_ACTIVE_acceptance": False}
persist("readiness.json", (json.dumps(obj, indent=2) + "\n").encode()); D.chmod(0o555)
if selected is None:
    raise SystemExit(72)
print(json.dumps({"status": status, "actual_job_id": jid, "selected_actual_attempt": selected, "readiness_proof_path": str(D / "readiness.json"), "own_plan_hash_capture_next_not_acceptance": True}), flush=True)




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


# Fixed own-control capture; no production Source audit or scientific child IO.
PLAN=S/"pending/final_source_plan_from14706_14925_16651_16847_v6/final_source_plan.json"
HANDOFF=PLAN.with_name("HANDOFF.md")
ROOTDOC=S/"handoffs/ROOT_FIXED_PLAN_V6_OWN_SHA_FROM16651_RECOVERED16847_20261015.md"
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
# The only imported project code is the literally checked qualified G16651.
import importlib.util
spec=importlib.util.spec_from_file_location("root_fixed_plan_v6_ownsha_lib",G/"final_source_closure.py")
lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib)
allocation=lib.cpu()
need(allocation["job_id"]==jid and allocation["allocated_CPUs"]==1 and allocation["allocated_gpus"]==0 and allocation["numeric_sacct_row"]==attempts[selected-1]["actual_row"],"Fresh actual qualified current exactCPU1/GPU0 row required")
tres(allocation["numeric_sacct_row"][2]);lib.software_shape(swa,ct);lib.software_snapshot_shape(swa,snapshot)
need(lib.conditional_core_runtime()==runtime,"Actual qualified/current CORE differs")
for m in plan["modules"]:
 lib.receipt_shape(m["gate"]["receipt"])
 for row in m["sources"]:lib.receipt_shape(row["receipt"])
 for r in m["seeds"]:lib.receipt_shape(r)
for r in plan["context_parent_seeds"]:lib.receipt_shape(r)
for a in plan["aliases"]:lib.receipt_shape(a["logical"]);lib.receipt_shape(a["physical"])
need([lib.rec(p)for p in controls]==receipts,"Actual qualified rec all30 own control descriptors required")
def final_readback():
 need([readonly(p)[0]for p in controls]==receipts and [md(p)for p in controls]==before,"All30 own controls bytes/metadata differ")
 need([md(p)for p in canonical]==canonical_before and [record(p)for p in canonical]==canonical_expected and [md(p)for p in canonical]==canonical_before,"All4 current canonical ownbytes/metadata differ")
 need([readonly(r["path"],r)[1]for r in sources]==source_before and [md(P),md(G)]==source_directories_before,"Actual original+frozen Source12/dirs differ")
 need([readonly(r["path"],r)[1]for r in software_controls]==software_before,"Actual software4 differs")
 metadata_readback();core_readback()
final_readback()
OUT=authority(S/"runs")/("final_source_plan_v6_ownsha_"+jid)
need(not OUT.exists()and not OUT.is_symlink(),"Exclusive absent V6 own-SHA output required")
OUT.mkdir(mode=0o755,exist_ok=False)
out=dict(schema="root-fixed-source-plan-v6-own-sha-control-capture.v1",status="ACTUAL_NEW_PLAN_V6_OWN_SHA_AND_EXACT_RECOVERED_SOURCE_ALIASES_CPU_VERIFIED_NOT_SOURCE_AUDIT_ACCEPTANCE",actual_job_id=jid,allocation=allocation,current_actual_readiness=obj,plan=receipts[0],handoff=receipts[1],root_control_human=receipts[2],control_receipts=receipts,control_metadata_before=before,control_metadata_after=[md(p)for p in controls],recovery_capture=CAPPIN,recovery_terminal_control=capro_r,exact_historical_logical_receipts=logical,recovered_historical_Source_receipts=recovered,recovered_historical_Source_metadata=recm,current_canonical_Source4_receipts=canonical_expected,current_canonical_Source4_metadata_before=canonical_before,current_canonical_Source4_metadata_after=[md(p)for p in canonical],original16825_failing_component_still_UNOBSERVED=True,oldPlanV5_SHA_unqualified_not_retroactively_qualified=True,ordered5_alias_prefix_preserved=True,two_aliases_and_two_explicit_Source_rows_only_delta=True,Source_n=640,seed_n=3809,role_n=9,parent_n=17,prior322_projection=dict(prior_row_n=322,alias_hit_n=322,ordinary_strict_row_indices=[]),software_acceptance=SOFTWARE,source_files=expected_frozen,original_executing_sources=expected_original,source_metadata_original_before=source_before[:6],source_metadata_frozen_before=source_before[6:],software_control_receipts=software_controls,software_control_metadata_before=software_before,software_control_metadata_after=[md(r["path"])for r in software_controls],conditional_core_runtime=runtime,plan_directory_metadata_before=plan_dir,plan_directory_metadata_after=md(PLAN.parent),all_Source12_SW4_Core_controls30_Source4_and_finite_protected_metadata_pre_end_afteroutput_finalreadonly_bound=True,plan_child_receipts_shape_only_no_child_IO=True,recovered_Source_never_imported_compiled_or_executed=True,scientific_receipt_children_read_or_hashed=False,compiler_or_tests_or_new_software_qualification_executed=False,historical_Slurm_queried=False,source_audit_executed=False,source_staged=False,published=False,ACTIVE_changed=False,own_created_controls_LATE_COMPOSER_ONLY_NOT_PLAN_PREREQUISITES=True)
data=(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode("utf-8");path=OUT/"capture.json"
with path.open("xb")as f:f.write(data);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
descriptor=lib.rec(path);out_metadata=md(path)
need(path.read_bytes()==data and read_json(path)==out and stat.S_IMODE(out_metadata["mode"])==0o444 and out_metadata["nlink"]==1,"Actual capture full ownbytes reread required")
final_readback();OUT.chmod(0o555)
fd=os.open(str(OUT),os.O_RDONLY)
try:os.fsync(fd)
finally:os.close(fd)
need(path.read_bytes()==data and read_json(path)==out and lib.rec(path)==descriptor and md(path)==out_metadata and stat.S_IMODE(md(OUT)["mode"])==0o555 and {p.name for p in OUT.iterdir()}=={"capture.json"},"Final readonly capture whole reread required")
final_readback()
print(json.dumps(dict(status=out["status"],capture=descriptor,plan=receipts[0],handoff=receipts[1],root_control_human=receipts[2],recovered_historical_Source_receipts=recovered,Source_n=640,seed_n=3809,role_n=9,parent_n=17,Plan_own_SHA_qualified_only_AFTER_fresh_terminal_RO_Root_and_independent_content_readback=True),sort_keys=True),flush=True)
```
