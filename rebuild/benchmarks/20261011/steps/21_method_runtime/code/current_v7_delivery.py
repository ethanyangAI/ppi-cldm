#!/usr/bin/env python3
import hashlib,importlib.util,json,os,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";V=R/"steps/22_matched_benchmark/settings/pilot_v7";O=S/f"runs/current_v7_delivery_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
def rec(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
 return {"path":str(p),"bytes":p.stat().st_size,"sha256":h.hexdigest()}
def write(p,v):
 assert not p.exists(),p
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n")
runtime=V/"source/benchmark_runtime.py";old_runtime=R/"steps/22_matched_benchmark/settings/pilot_v6/source/benchmark_runtime.py"
assert rec(runtime)["sha256"]=="1325556ccac5936bbae456344f040257b5041815190af5b48425cf016bc38e17" and runtime.read_bytes()==old_runtime.read_bytes()
rfd=S/"runs/current_rfd_readiness_13122/outputs/acceptance.json";bc=S/"runs/current_bc_readiness_13129/outputs/acceptance.json"
assert json.loads(rfd.read_text())["status"]=="CURRENT_RFD_AND_ORIGINAL_MPNN_CPU_CONSTRUCTORS_PASS"
assert json.loads(bc.read_text())["status"]=="BOTH_PRIVATE_METHOD_RUNTIMES_CPU_READY_GPU_ENGINEERING_PILOT_PENDING"
for output in [rfd.parent,bc.parent]:
 probe=json.loads((output/"import_probe.json").read_text())
 assert probe["pip_check"]["returncode"]==0 and all(row["import"]=="PASS" for row in probe["modules"].values())
 frozen=output/"pip_freeze.txt";p=subprocess.run([str(Path(probe["prefix"])/"bin/python"),"-m","pip","freeze"],capture_output=True,text=True,check=True);frozen.write_text(p.stdout)
sources={p.name:rec(p) for p in (V/"source").iterdir() if p.is_file()}
manifest=R/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/KEAP1_2FLU/input_manifest.json"
feature=S/"runs/pilot_v6_bridge_features_13097/outputs/native_rf_all_channels_contract.json";identity=S/"runs/pilot_v6_bridge_features_13097/outputs/actual_rfd_identity_proof.json";mpnn=S/"runs/pilot_v6_mpnn_13098/outputs/acceptance.json"
assert json.loads(feature.read_text())["runtime"]==rec(old_runtime)
assets=[]
for name in ["rfdiffusion","colabfold","pyrosetta"]:
 for p in sorted((R/"assets"/name).rglob("*")):
  if p.is_file() and not p.name.endswith(".partial"):assets.append(rec(p))
asset_receipt=O/"current_model_assets.json";write(asset_receipt,{"status":"CURRENT_PRIVATE_MODEL_ASSETS_HASHED_CPU","assets":assets})
dependency=O/"current_readiness_dependency.json"
write(dependency,{"status":"CURRENT_READONLY_PRIVATE_METHOD_DEPENDENCIES_CPU_ACCEPTED_GPU_PENDING","runtime_source":rec(runtime),"activation_sources":[sources["rfd_env.sh"],sources["bindcraft_env.sh"]],"current_rfd_constructor":rec(rfd),"current_bindcraft_constructor_and_sources":rec(bc),"current_import_probes":[rec(rfd.parent/"import_probe.json"),rec(bc.parent/"import_probe.json")],"current_environment_freezes":[rec(rfd.parent/"pip_freeze.txt"),rec(bc.parent/"pip_freeze.txt")],"current_assets":rec(asset_receipt),"current_helper_sources":[sources["current_rfd_readiness.py"],sources["current_bc_readiness_v2.py"]],"exact_immutable_source_equivalence":[{"current":rec(runtime),"previous_immutable":rec(old_runtime),"byte_identical":True}],"legacy_12980_dev_adapter_proof_currently_excluded":True,"legacy_13123_vendor_vs_pip_scope_failure_retained":True,"credentials_required_now":[],"cpu_only":True,"scientific_prediction_run":False})
configs={}
for method in ["rf_diffusion","bindcraft"]:
 old_cfg=R/"steps/22_matched_benchmark/settings/pilot_v6"/(method+".json");cfg=json.loads(old_cfg.read_text());original=json.loads(old_cfg.read_text())
 cfg["input_receipts"]=[rec(runtime),sources["bindcraft_env.sh"],rec(dependency),rec(feature),rec(identity),rec(mpnn),rec(manifest)]
 if method=="rf_diffusion":
  cfg["input_receipts"].append(sources["rfd_env.sh"]);cfg["native_af2"]["environment_script"]=sources["bindcraft_env.sh"]
 cfg["engineering_revision"]="pilot_v7 replaces mutable legacy development readiness with fresh immutable current CPU dependency closure; runtime code byte-identical to v6; all native scientific settings unchanged"
 def science(v):
  v=json.loads(json.dumps(v));v.pop("input_receipts",None);v.pop("engineering_revision",None)
  if "native_af2" in v:v["native_af2"].pop("environment_script",None)
  return v
 assert science(cfg)==science(original)
 out=V/(method+".json");write(out,cfg);configs[method]=rec(out)
spec=importlib.util.spec_from_file_location("rt",runtime);rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
for receipt in configs.values():rt.load_method_inputs(receipt["path"],receipt["sha256"],str(manifest))
settings={"status":"PILOT_V7_CURRENT_READONLY_CPU_DEPENDENCY_CLOSURE_PASS_GPU_PENDING","root":str(V),"sources":sources,"configs":configs,"current_dependency":rec(dependency),"prepared_keap1_manifest":rec(manifest),"native_rf_feature_proof":rec(feature),"actual_original_mpnn8":rec(mpnn),"native_science_unchanged_from_v6":True,"runtime_byte_identical_v6":True,"legacy_readiness_12980_and_failed_scope13123_retained_as_history":True,"no_gpu_submitted_by_this_agent":True}
write(O/"pilot_settings_receipt.json",settings)
report=O/"CURRENT_READINESS_AUDIT.md";report.write_text("""# 当前v7依赖闭包审计

当前运行代码与v6逐字节相同，SHA-256为1325556ccac5936bbae456344f040257b5041815190af5b48425cf016bc38e17。v7仅更新环境/模型/源文件/资产的当前验收与配置引用，不修改生成、AF2输入、筛选阈值或排序。

旧readiness12980在其生成时引用未归档开发代码33676字节，后来路径发生版本替换。此历史证明仍保留，但不再作为当前依赖闭包入口；没有重建或声称恢复缺失的旧开发代码。CPU13110同时确认最终v6 live与冻结文件均为43050字节且完全相同，因此不能把历史pointer drift写成当前v6代码漂移。

CPU13122使用只读v7运行代码及私有RFD环境，实际加载官方Complex_base checkpoint构造SelfConditioning模型，实际加载原始ProteinMPNN v_48_020权重并构造118状态张量的CPU模型，全部有限；未运行扩散模型预测。CPU13129独立核验私有BindCraft环境全部imports/pip、官方RF/MPNN/dllogger源文件189/109/11个、BindCraft/ColabDesign固定源码，以及实际安装的ColabDesign .py/.pkl对官方vendor逐字节相同。Pip未打包的vendor legacy文件明确列为包装范围，不声称它们已安装；13123误把vendor所有legacy文件都要求安装的失败保留。

所有10个PTM/Multimer-v3参数文件完整载入并验证有限张量；CPU实际构造RF原生PTM1 initialguess模型、BindCraft PTM1/PTM2无initialguess模型、Multimer设计模型及original/soluble MPNN。实际PyRosetta读取PDL1，DSSP运行、DAlphaBall动态链接和ffmpeg均通过。当前私有模型资产重新计算完整SHA-256，新的pip freeze和源码/helper均绑定到不可变v7路径。许可证记录来源于固定官方文档及既有私有学术资产，不新增凭证需求。

v7配置完全删除旧readiness/devcode证明作为current输入；继续引用v6不可变实际骨架AF2输入证明、原始MPNN8/FASTA增量证明及13094元数据修正输入。正式GPU验收仍需主任务执行完整工程分支并提供实际模型/结构/逐候选账本及独立预算验收；CPU构造通过不等于GPU推理或科学阳性。
""",encoding="utf-8")
accept={"status":settings["status"],"settings":rec(O/"pilot_settings_receipt.json"),"report":rec(report),"current_dependency":rec(dependency),"gpu_pending":True,"scientific_benchmark_completed":False,"slurm_job_id":os.environ["SLURM_JOB_ID"],"scheduler_record":subprocess.check_output(["scontrol","show","job","-o",os.environ["SLURM_JOB_ID"]],text=True)}
write(O/"acceptance.json",accept)
# Make the new proofs/configs/source tree read-only after complete byte verification.
for parent in [rfd.parent,bc.parent,O,V/"source"]:
 for p in parent.iterdir():
  if p.is_file():p.chmod(0o444)
 parent.chmod(0o555)
for method in configs:(V/(method+".json")).chmod(0o444)
V.chmod(0o555)
current=S/"RUNTIME_CPU_CURRENT.json";previous=S/f"runs/current_v7_delivery_{os.environ['SLURM_JOB_ID']}/previous_RUNTIME_CPU_CURRENT.json";previous.write_bytes(current.read_bytes());previous.chmod(0o444)
pointer={"schema":"private_runtime_authority.v1","acceptance":rec(O/"acceptance.json"),"scope":"readonly current v7 CPU dependency closure; byte-identical v6 method science; actual GPU engineering pending","previous_pointer":rec(previous)}
temp=current.with_suffix(".json.v7.partial");temp.write_text(json.dumps(pointer,indent=2)+"\n");temp.replace(current);assert json.loads(current.read_text())==pointer
print(json.dumps({"status":settings["status"],"settings":rec(O/"pilot_settings_receipt.json"),"dependency":rec(dependency),"configs":configs,"runtime_source":rec(runtime),"report":rec(report)},indent=2))

