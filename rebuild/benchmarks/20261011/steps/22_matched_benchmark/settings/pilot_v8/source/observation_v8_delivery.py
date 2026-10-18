#!/usr/bin/env python3
import hashlib,importlib.util,json,os,shutil,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime"
OLD=R/"steps/22_matched_benchmark/settings/pilot_v7";V=R/"steps/22_matched_benchmark/settings/pilot_v8"
O=S/f"runs/observation_v8_delivery_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True)
def rec(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for block in iter(lambda:f.read(4*1024*1024),b""):h.update(block)
 return {"path":str(p),"bytes":p.stat().st_size,"sha256":h.hexdigest()}
def checked(v):
 p=Path(v["path"]);assert rec(p)==v,(v,rec(p));return p
def write(p,obj):
 assert not p.exists(),p;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
scheduler=subprocess.check_output(["scontrol","show","job","-o",os.environ["SLURM_JOB_ID"]],text=True)
assert "gres/gpu=" not in scheduler,scheduler
proof=S/"runs/observation_v8_contracts_13153/outputs/acceptance.json";accept=json.loads(proof.read_text())
assert accept["status"]=="OBSERVATION_ONLY_NATIVE_AF2_V8_CPU_CONTRACTS_PASS" and accept["tests_run"]==31 and accept["errors"]==accept["failures"]==0
assert not V.exists();(V/"source").mkdir(parents=True)
runtime=V/"source/benchmark_runtime.py";shutil.copyfile(checked(accept["runtime_source"]),runtime)
for name in ["rfd_env.sh","bindcraft_env.sh"]:shutil.copyfile(OLD/"source"/name,V/"source"/name)
for key,name in [("contracts_source","test_runtime_contracts.py"),("driver_source","contract_driver.py")]:
 shutil.copyfile(checked(accept[key]),V/"source"/name)
shutil.copyfile(Path(__file__),V/"source/observation_v8_delivery.py")
for source in accept["official_output_unit_and_serializer_sources"]:checked(source)
old_settings=S/"runs/current_v7_delivery_13133/outputs/pilot_settings_receipt.json"
current_dep=checked(json.loads(old_settings.read_text())["current_dependency"])
current=json.loads(current_dep.read_text());checked(current["current_rfd_constructor"]);checked(current["current_bindcraft_constructor_and_sources"]);checked(current["current_assets"])
for v in current["current_environment_freezes"]:checked(v)
pip=subprocess.run([str(R/"env/bindcraft/bin/python"),"-m","pip","freeze"],text=True,capture_output=True,check=True)
assert pip.stdout==(Path(current["current_environment_freezes"][1]["path"])).read_text(),"Environment changed after clean readiness"
(O/"bindcraft_pip_freeze.txt").write_text(pip.stdout)
sources={p.name:rec(p) for p in (V/"source").iterdir() if p.is_file()}
dependency=O/"current_observation_dependency.json"
write(dependency,{"schema":"observation_runtime_dependency.v1","status":"CURRENT_NATIVE_METHOD_READINESS_PLUS_OBSERVATION_V8_CPU_ACCEPTED_GPU_PENDING",
 "runtime_source":rec(runtime),"observation_contracts":rec(proof),"current_environment_asset_readiness":rec(current_dep),
 "activation_sources":[sources["rfd_env.sh"],sources["bindcraft_env.sh"]],"current_pip_freeze":rec(O/"bindcraft_pip_freeze.txt"),
 "source_change_scope":"Only read-only after-return native AF2 confidence/PDB serialization and observational RPC join metadata; no model inputs, random calls, settings, filters, native selection or model count changes",
 "previous_runtime":rec(OLD/"source/benchmark_runtime.py"),"official_output_sources":accept["official_output_unit_and_serializer_sources"],
 "no_gpu_inference":True,"legacy_12980_development_proof_not_used":True})
configs={}
for method in ["rf_diffusion","bindcraft"]:
 cfg=json.loads((OLD/(method+".json")).read_text());previous=json.loads((OLD/(method+".json")).read_text())
 cfg["input_receipts"]=[sources["benchmark_runtime.py"],sources["bindcraft_env.sh"],rec(dependency)]+cfg["input_receipts"][3:]+[rec(proof)]
 if method=="rf_diffusion":
  cfg["input_receipts"]=[sources["rfd_env.sh"] if Path(v["path"]).name=="rfd_env.sh" else v for v in cfg["input_receipts"]]
  cfg["native_af2"]["environment_script"]=sources["bindcraft_env.sh"]
 cfg["native_output_observation"]={"schema":"native_af2_observation.v1","raw_arrays":["pae","plddt","aatype","i_ptm","ptm"],
  "pae_units":"angstrom","plddt_units":"fraction","raw_pdb":"same actual prediction aux through official serializer",
  "capture_scope":"RF native validation; BC native complex PTM validation including early rejection",
  "additional_predictions":0,"rng_draws":0,"cpu_collector_hashes_outputs":True,"durable_before_native_update":True}
 cfg["engineering_revision"]="pilot_v8 observation-only durable native AF2 raw confidence/PDB logging; all native scientific settings and model calls unchanged from v7; clean current13133 readiness plus31 CPU observation contracts"
 def science(v):
  v=json.loads(json.dumps(v))
  for key in ["input_receipts","engineering_revision","native_output_observation"]:v.pop(key,None)
  if "native_af2" in v:v["native_af2"].pop("environment_script",None)
  return v
 assert science(cfg)==science(previous),"Scientific settings changed"
 file=V/(method+".json");write(file,cfg);configs[method]=rec(file)
spec=importlib.util.spec_from_file_location("rt",runtime);rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
manifest=R/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/KEAP1_2FLU/input_manifest.json"
for v in configs.values():rt.load_method_inputs(v["path"],v["sha256"],str(manifest))
report=O/"OBSERVATION_RUNTIME_AUDIT.md"
report.write_text("""# v8 原生AF2实际输出观察审计

新版本仅保存已有预测返回的完整PAE（Å）、pLDDT（0–1）、实际aatype查询、原始i_pTM/pTM以及同一aux的原始PDB。RF每个原生PTM1预测记录后再发布原生筛选更新；BindCraft仅在原生complex PTM1/2 validation API作用期间包裹同一对象predict，返回后观察并finally恢复。不观察设计优化、不新增模型调用或随机抽样、不修改输入、原生阈值、排序或官方状态。日志IO计入GPU预算；GPU记录durable路径/字节，CPU collector计算SHA并复算指标，保留所有拒绝、未完成及NA情况。

保存PDB调用官方save_pdb(filename=None,get_best=False,aux=同一实际aux)，从相同预测的all字段序列化，不修改model._tmp/best/opt/inputs，不改返回对象。NPZ/PDB字节fsync后才发布durableJSON与观察流。若中断仅留下数组/未完整日志，不补造预测或原生结果。原生科学配置与v7精确比较相同，当前私有环境/参数/官方源码仍引用清洁CPU13133闭包及完整包、真实构造13122/13129；不复用缺失旧开发代码12980作为current。

CPU13148/13150/13152的测试失败完整保留。faulthandler定位ml_dtypes第二次C扩展导入；旧mock使用patch.dict(sys.modules)删除了mock作用期间首次导入的JAX/ColabDesign模块，随后新增测试重导入触发段错误。CPU13153在mock前完整预加载实际私有JAX/ColabDesign/BindCraft functions及CPUKey，31合同全部通过。它执行真实官方PAE/pLDDT getter、真实save_pdb和原生BindCraft early-reject API；验证完整数组/查询/单位/模型/种子与文件hash、参数/返回值/调用数、模型状态和RNG保持、拒绝后官方删除PDB而独立副本保留、写入边界失败不发布伪完整记录。测试夹具不进入科学输出。该修复只涉及测试加载顺序，生产不mock sys.modules；完整私有包导入再次通过，未升级环境。

GPU完整原生分支仍由主任务在新engineering plan冻结并独立预算验收后运行。此报告是CPU技术验收，不代表GPU预测完成、设计方法胜出或实验证实阻断。
""",encoding="utf-8")
settings={"status":"PILOT_V8_OBSERVATION_ONLY_CURRENT_CPU_CLOSURE_PASS_GPU_PENDING","root":str(V),"sources":sources,
 "configs":configs,"current_dependency":rec(dependency),"observation_contracts":rec(proof),"prepared_keap1_manifest":rec(manifest),
 "native_scientific_configs_unchanged_from_v7":True,"no_additional_prediction_or_rng_calls":True,
 "previous_immutable_v7_preserved":True,"no_gpu_submitted_by_this_agent":True}
write(O/"pilot_settings_receipt.json",settings)
final={"status":settings["status"],"settings":rec(O/"pilot_settings_receipt.json"),"report":rec(report),
 "current_dependency":rec(dependency),"slurm_job_id":os.environ["SLURM_JOB_ID"],"scheduler_record":scheduler,
 "gpu_pending":True,"scientific_benchmark_completed":False}
write(O/"acceptance.json",final)
for parent in [V/"source",O]:
 for p in parent.iterdir():
  if p.is_file():p.chmod(0o444)
 parent.chmod(0o555)
for method in configs:(V/(method+".json")).chmod(0o444)
V.chmod(0o555)
current_pointer=S/"RUNTIME_CPU_CURRENT.json";previous=O.parent/"previous_RUNTIME_CPU_CURRENT.json";previous.write_bytes(current_pointer.read_bytes());previous.chmod(0o444)
pointer={"schema":"private_runtime_authority.v1","acceptance":rec(O/"acceptance.json"),
 "scope":"current v8 native confidence observation only; unchanged v7 scientific methods; actual GPU native branch pending","previous_pointer":rec(previous)}
temp=current_pointer.with_suffix(".json.v8.partial");temp.write_text(json.dumps(pointer,indent=2)+"\n");temp.replace(current_pointer)
print(json.dumps({"status":settings["status"],"settings":rec(O/"pilot_settings_receipt.json"),"dependency":rec(dependency),
 "configs":configs,"runtime_source":rec(runtime),"report":rec(report)},indent=2))

