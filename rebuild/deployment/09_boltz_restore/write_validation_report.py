import csv,json,os
from pathlib import Path
from ppiblocker.common import read_json,record_file,atomic_json,verify_file,require
R=Path("/lustre/users/u21111210118/projects/test9");O=R/"steps/09_boltz_restore/outputs"
E=O/"gpu_evaluation_acceptance_11787.json";P=O/"native_predict_acceptance_11801.json"
e=read_json(E);p=read_json(P)
require(e["status"]=="BOLTZ_GPU_EVALUATION_ACCEPTED" and p["status"]=="BOLTZ_NATIVE_PREDICT_ENGINEERING_ACCEPTED","AUDIT_FAILED","Both CPU audit receipts required")
for x in (e["evaluation_manifest"],e["upstream_design_manifest"],p["prediction_manifest"],p["prepare_manifest"],p["withheld_reference_manifest"]):verify_file(x)
rows=[]
for x in e["model_summaries"]:
 rows.append({"track":"fresh_KEAP1_candidate_refold","model_index":x["model_index"],"pair_iptm":x["metrics"]["pair_iptm"],"interface_pae_mean_A":x["metrics"]["interface_pae_mean"],"partner_plddt":x["metrics"]["partner_plddt"],"target_ca_rmsd_A":x["geometry"]["target_ca_rmsd"],"partner_ca_rmsd_after_target_alignment_A":x["geometry"]["binder_ca_rmsd_after_target_alignment"],"comparison_reference":"RFdiffusion_designed_backbone","native_contact_recall_at_5A":"","native_target_interface_coverage":x["geometry"]["native_interface_coverage"],"gate_reasons":";".join(x["reasons"])})
for x in p["comparison"]:
 rows.append({"track":"MDM2_p53_sequence_only_native_pose","model_index":x["model_index"],"pair_iptm":x["prediction_metrics"]["pair_iptm"],"interface_pae_mean_A":x["prediction_metrics"]["interface_pae_mean"],"partner_plddt":x["prediction_metrics"]["partner_plddt"],"target_ca_rmsd_A":x["target_ca_rmsd_angstrom"],"partner_ca_rmsd_after_target_alignment_A":x["partner_ca_rmsd_after_target_alignment_angstrom"],"comparison_reference":"withheld_1YCR_experimental_observed_construct","native_contact_recall_at_5A":x["native_contact_recall_at_5A"],"native_target_interface_coverage":"","gate_reasons":";".join(x["prediction_reasons"])})
tsv=O/"gpu_validation_metrics.tsv"
with tsv.open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t");w.writeheader();w.writerows(rows)
lines=["# Boltz 新部署 GPU 验收报告","",
"2026-10-02；唯一根目录："+str(R)+"。",
"",
"工程验收完成：实验结构来源的新 KEAP1 RFdiffusion+ProteinMPNN 候选进入 Boltz 三样本复核；另一个 MDM2/p53 样例完成严格 sequence-only 原始互作 pose 预测。所有预测来自本次新作业，没有引用消失的旧 run。","",
"## 新候选复核","",
"KEAP1 候选 bb42_seq0（65 aa）全流程运行完成，但筛选结果为 REJECTED，0/3 样本通过。三个样本均出现 LOW_PAIR_IPTM、HIGH_INTERFACE_PAE、DESIGNED_POSE_NOT_RECOVERED。目标自身结构稳定，binder 自身折叠接近设计，但结合相对位置未恢复。","",
"|样本|pair ipTM|界面PAE (Å)|目标对齐后的binder CA RMSD (Å)|原生目标界面覆盖|",
"|---|---:|---:|---:|---:|"]
for x in e["model_summaries"]:
 lines.append(f"|{x['model_index']}|{x['metrics']['pair_iptm']:.3f}|{x['metrics']['interface_pae_mean']:.2f}|{x['geometry']['binder_ca_rmsd_after_target_alignment']:.2f}|{x['geometry']['native_interface_coverage']:.1%}|")
lines.extend(["","界面覆盖、全局pLDDT或空间竞争本身不能抵消结合姿态与界面置信度失败；本候选不是合格 blocker。","",
"## 盲序列互作预测","",
"MDM2 25–109 / p53 17–29；不输入实验坐标、模板或contacts，不调用外部MSA。3/3样本符合原固定门槛且相互一致，状态 POSE_ACCEPTED。1YCR 仅在完成预测后用于独立CPU几何比较。","",
"|样本|pair ipTM|界面PAE (Å)|目标CA RMSD (Å)|目标对齐后的p53 CA RMSD (Å)|原生5Å接触召回|",
"|---|---:|---:|---:|---:|---:|"])
for x in p["comparison"]:
 lines.append(f"|{x['model_index']}|{x['prediction_metrics']['pair_iptm']:.3f}|{x['prediction_metrics']['interface_pae_mean']:.2f}|{x['target_ca_rmsd_angstrom']:.2f}|{x['partner_ca_rmsd_after_target_alignment_angstrom']:.2f}|{x['native_contact_recall_at_5A']:.1%}|")
lines.extend(["","该已知复合物可能出现在模型训练资料中，训练重叠未知；本结果只验收预测分支的实际可运行性，不证明未知蛋白对泛化能力、工作流优越性或实验阻断。","",
"## 可追溯性与验收","",
"- CPU 初次 runtime lock登记11763；新增 source/environment/runtime-lock-boltz.json，没有自动刷新旧lock。",
"- GPU11787（KEAP1复核）和11801（MDM2/p53预测）均0:0完成；A100-40GB，单作业1卡。完整运行13:01/08:59，主要为Lustre冷读取/验证/加载；Boltz预测进度段22/16秒不是端到端运行时间。",
"- CPU11814/11815独立验收32+35个manifest inventory文件SHA-256，以及6个PDB的两条链精确序列；全部通过。",
"- 本次未改核心源码、科学门槛、输入候选序列或模型版本。没有实验binding/blockade证明。",
"",
"完整评价 manifest："+e["evaluation_manifest"]["path"],
"","原始互作预测 manifest："+p["prediction_manifest"]["path"],
"","机器可读验收："+str(E)+"；"+str(P),
"","汇总指标："+str(tsv),""])
report=O/"GPU_VALIDATION_REPORT.md";report.write_text("\n".join(lines))
atomic_json(O/"gpu_validation_report_receipt.json",{"status":"BOLTZ_FRESH_TWO_BRANCH_VALIDATION_COMPLETE","cpu_report_job_id":os.environ["SLURM_JOB_ID"],"inputs":[record_file(E),record_file(P)],"outputs":[record_file(report),record_file(tsv)],"source_code_modified":False,"scientific_thresholds_modified":False})
print(json.dumps({"report":record_file(report),"metrics":record_file(tsv),"evaluation":"REJECTED_0_OF_3","native_predict":"POSE_ACCEPTED_3_OF_3"}),flush=True)
