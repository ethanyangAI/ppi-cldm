#!/usr/bin/env python3
import hashlib,importlib.util,json,os,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";V=R/"steps/22_matched_benchmark/settings/pilot_v6";O=S/f"runs/pilot_v6_delivery_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def write(p,v):
 assert not p.exists(),p
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n")
source=V/"source/benchmark_runtime.py";assert rec(source)["sha256"]=="1325556ccac5936bbae456344f040257b5041815190af5b48425cf016bc38e17"
sources={name:rec(V/"source"/name) for name in ["benchmark_runtime.py","rfd_env.sh","bindcraft_env.sh","test_runtime_contracts.py","pilot_v6_feature_bridge_audit.py"]}
manifest=R/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/KEAP1_2FLU/input_manifest.json";assert rec(manifest)["sha256"]=="c12846eeadb8b7d3fa58119237d2f8c4a9ee0ef31966779db6c41a51b07c4c8f"
feature=S/"runs/pilot_v6_bridge_features_13097/outputs/native_rf_all_channels_contract.json";actual_proof=S/"runs/pilot_v6_contracts_13092/outputs/actual_rfd_identity_proof.json";contracts=S/"runs/pilot_v6_contracts_13092/outputs/acceptance.json";frozen_tests=S/"runs/pilot_v6_features_13095/outputs/tests.txt";mpnn=S/"runs/pilot_v6_mpnn_13098/outputs/acceptance.json"
assert json.loads(feature.read_text())["status"]=="LITERAL_SEQUENCE_CB_INITIAL_GUESS_AND_ALL_TEMPLATE_CHANNELS_PASS"
assert json.loads(mpnn.read_text())["status"]=="ACTUAL_ORIGINAL_MPNN8_CHAIN_B_AND_INCREMENTAL_NATIVE_FASTA_PASS"
assert "Ran 23 tests" in frozen_tests.read_text() and frozen_tests.read_text().rstrip().endswith("OK")
configs={};v5=R/"steps/22_matched_benchmark/settings/pilot_v5"
for method in ["rf_diffusion","bindcraft"]:
 cfg=json.loads((v5/(method+".json")).read_text());records=[]
 for old in cfg["input_receipts"]:
  path=Path(old["path"])
  if path.name in ["native_rf_feature_contract.json","native_rf_all_channels_contract.json"]:continue
  if path.parent==v5/"source":records.append(sources[path.name])
  else:records.append(old)
 records.extend(rec(p) for p in [feature,actual_proof,contracts,frozen_tests,mpnn,manifest])
 cfg["input_receipts"]=records
 cfg["engineering_revision"]="pilot_v6 corrects official Sampler physical target A/binder B with complete TRB identity audit, numpy seed keyword compatibility, and exact Slurm array JobId selection; native scientific settings unchanged"
 if method=="rf_diffusion":cfg["native_af2"]["environment_script"]=sources["bindcraft_env.sh"]
 out=V/(method+".json");write(out,cfg);configs[method]=rec(out)
spec=importlib.util.spec_from_file_location("rt",source);rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
for method,record in configs.items():rt.load_method_inputs(record["path"],record["sha256"],str(manifest))
settings={"status":"PILOT_V6_NATIVE_RUNTIME_REPAIRS_IMMUTABLE_CPU_ACCEPTED_GPU_PILOT_PENDING","root":str(V),"sources":sources,"configs":configs,"prepared_keap1_manifest":rec(manifest),"native_rf_feature_proof":rec(feature),"actual_rfd_identity_proof":rec(actual_proof),"cpu_contracts":rec(contracts),"immutable_cpu_tests":rec(frozen_tests),"actual_cpu_mpnn8":rec(mpnn),"prior_versions_retained":[1,2,3,4,5],"no_new_gpu_submitted":True}
write(O/"pilot_settings_receipt.json",settings)
report=O/"REPAIR_AUDIT.md";report.write_text("""# 工程试跑13069失败与v6修复审计

13069_0和13069_1均为工程失败，不属于方法的科学阴性结果，也不是正式benchmark。旧源代码、配置、输入、日志、已消耗算力和失败输出完整保留。

RFdiffusion实际PDB保留输入靶标链A（285残基，完整query一致），新生成binder为B（65个polyG残基）。旧适配器依据ContigMap抽象hal链推断A/B，与官方Sampler.sample_init最终chain_idx/idx_pdb不同。v6以冻结输入声明的物理链、完整序列/长度/连续编号和TRB receptor及complex映射严格核验；任何截断、错误query、陈旧链声明或把receptor局部索引当作完整complex索引均被拒绝。receptor_con_hal_idx0为局部0..284，complex_con_hal_idx0为完整65..349。

官方SelfConditioning.sample_step最终输出allatom重建px0，因此固定靶标并非逐原子复制。实际target CA刚体对齐RMSD为0.073895 Å，最大CA差0.335541 Å；N/C/O最大差为0.735998/0.336526/1.869458 Å。v6保存有限性、RMSD和最大差作为诊断，不新增事后坐标过滤，不替换原生重建坐标。13084和13085中被否定的索引/逐原子零差假设作为历史审计保留。

BindCraft13069_1已完成CUDA/JAX初始化、写READY并启动轨迹；失败发生在原生ColabDesign prep_inputs/restart/set_seed调用np.random.seed(seed=seed)时。旧包装形参value不接受关键字seed。v6保持NumPy原生seed关键字签名，并保留预定None熵流和恢复原始函数的逻辑。真实官方ColabDesign set_seed路径、关键字/位置/None调用与重复可复现性已CPU验证。不能把runner终止后的returncode -9误解释为初始CUDA失败。

补充Slurm实况：查询数字array master可能返回兄弟多行记录。v6的冗余实际分配检查选唯一JobId=SLURM_JOB_ID行，再检查RUNNING与AllocTRES/TRES GPU1。root拥有的budget_v4完整GPU所有权检查仍负责Slurm ID→physical minor→UUID、可见性和硬截止。

CPU13092和冻结源13095均通过23项合约。CPU13097针对实际RFD骨架及元数据修正后的13094 KEAP1 manifest截获真实AF2前向输入：target first，物理A/B映射正确，singleMSA、model_1_ptm、3recycles、完整骨架initial guess及几何CB；binder四种template通道全零。未运行AF2预测。CPU13098实际官方原始ProteinMPNN以binder B生成8条65aa完整序列；逐原生FASTA完成写入的ledger与原始文件逐条完全一致，omitC/X和固定seed不变。该CPU生成仅用于工程验证，不加入正式科学结果。

v6保留两法全部原生科学设置：RF原始MPNN8、T0.0001和单PTM原生AF2复核；RF原生筛选pLDDT>=0.8、跨块PAE均值<=10 Å、target-aligned binder CA RMSD<=1 Å，按pae_interaction升序。BindCraft官方default_4stage_multimer及default_filters不变，solubleMPNN20、最多2个原生accepted，按Average_i_pTM降序。两法不同原生pass率仍不能直接比较胜负，正式结论使用共同独立复核。

本次交付为CPU验收通过的不可变v6工程修复配置；仍需root执行新的完整GPU工程试跑并检查真实全链性能，之后才能冻结正式benchmark。未由本agent提交GPU、提交Git或覆盖v1–v5。
""",encoding="utf-8")
acceptance={"status":settings["status"],"settings":rec(O/"pilot_settings_receipt.json"),"repair_report":rec(report),"cpu_only":True,"slurm_job_id":os.environ["SLURM_JOB_ID"],"scheduler_record":subprocess.check_output(["scontrol","show","job","-o",os.environ["SLURM_JOB_ID"]],text=True),"scientific_benchmark_completed":False}
write(O/"acceptance.json",acceptance)
current=S/"RUNTIME_CPU_CURRENT.json";previous=O/"previous_RUNTIME_CPU_CURRENT.json";previous.write_bytes(current.read_bytes())
new={"schema":"private_runtime_authority.v1","acceptance":rec(O/"acceptance.json"),"scope":"CPU verified pilot_v6 repairs; prior delivery receipt preserved; GPU full-stage validation pending","previous_pointer":rec(previous),"previous_runtime_delivery":rec(S/"runs/delivery_13063/outputs/acceptance.json")}
tmp=current.with_suffix(".json.v6.partial");tmp.write_text(json.dumps(new,indent=2)+"\n");tmp.replace(current);assert json.loads(current.read_text())==new
print(json.dumps({"status":acceptance["status"],"settings":rec(O/"pilot_settings_receipt.json"),"report":rec(report),"configs":configs,"runtime":rec(source),"current_pointer":rec(current)},indent=2))

