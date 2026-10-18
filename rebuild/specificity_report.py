import os,json,hashlib
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/15_specificity_review";D=S/"outputs/analysis_11863"
report=json.loads((D/"summary.json").read_text());acc=json.loads((S/"outputs/acceptance_11863.json").read_text());plan=json.loads((S/"plan.json").read_text())
assert report["status"]=="MATCHED_SPECIFICITY_REVIEW_COMPLETE" and acc["model_count"]==225
def f(x):return "不可估计" if x is None else f"{x:.3f}"
lines=["# 特异性阳性对照故障归因与匹配候选复核","",
"本报告是新计算诊断。旧预测坐标已丢失，不能对旧运行作直接坐标级归因；不代表实验特异性、结合或阻断验证。","",
"## 冻结矩阵与执行","",
"- 主分析：完整作者实验 entity 构建体，3 个靶点 ×（原生配体 + 3 个候选）× 5 个 AF2-Multimer-v3 模型 × 3 个种子，共 180 个新模型。",
"- 预定构建敏感性：三种观测构建体各 15 个原生配体模型，共 45 个；两轨同时报告，不择优。",
"- 另列 KEAP1 观测核心臂：复用已验收 45 个候选模型，与这次 15 个 observed native 模型匹配。后者已在敏感性分母中；唯一结构总数 270，新增 225。",
"- 全部采用 12 recycles、early-stop 0.5、目标 MSA 128:256、配体单序列、无模板、无原生坐标输入、无松弛；全部模型/种子和精确完整序列通过验证。",
"- 模型/种子是技术重复，不作为独立生物学实验。","",
"## 构建差异","",
"| 靶点/原生配体 | target observed→declared | ligand observed→declared | 关键差异 |",
"|---|---:|---:|---|",
"| KEAP1–Nrf2 / 2FLU | 285→308 | 16→16 | 未观测23 aa中19 aa为His-tag/连接序列，4 aa为UniProt映射序列；没有内部缺口 |",
"| KLHL3–WNK4 / 4CH9 | 286→292 | 9→11 | target N端4及C端2未观测（前2 aa SM在UniProt映射外）；配体C端HQ未观测 |",
"| KLHL12–DVL1 / 6TTK | 285→301 | 8→15 | target N端12及内部entity87–90未观测；配体N端6与C端1未观测 |","",
"主分析保留完整声明序列。RMSD和原生接触比较只使用实验实际观测且具有明确 entity 位置对应的残基；逐模型文件保存完整query长度、映射分母、观测覆盖率，以及核心、UniProt映射区和标签/延伸区分别的pLDDT。这样避免将标签缺失误称天然核心缺失。","",
"## 原生阳性结果","",
"| 靶点 | 构建轨道 | 置信度通过/15 | 姿态+置信度恢复/15 | ligand姿态RMSD中位Å | contact recall中位 | 阳性诊断充分 |",
"|---|---|---:|---:|---:|---:|---|"]
for d in report["conditions"]:
 if d["role"]=="native":
  lines.append(f"| {d['target']} | {d['analysis_track']} | {d['baseline_confidence_pass_count']} | {d['native_control_recovery_count']} | {f(d['native_ligand_pose_RMSD_A']['median'])} | {f(d['native_contact_recall']['median'])} | {'是' if d['native_positive_adequate'] else '否'} |")
lines+=["","置信度门保留 AF2 global ipTM≥0.75、binder及界面pLDDT≥0.8、双向5Å接触PAE均值≤8Å。AF2 global ipTM不等同Boltz minimum directional pair ipTM。双向PAE分别保留，界面无接触时均值为不可估计。","",
"本轮原生恢复的操作性规则在预测前冻结：上述置信度通过，且实验核心对齐后的配体Cα姿态RMSD≤5Å、原生5Å残基接触召回≥0.5；15个模型至少8个满足且覆盖至少2个种子，才标记该靶点阳性诊断充分。它是本轮诊断规则，不是校准过的生物学阈值。","",
"## 匹配候选结果","",
"| 靶点 | 候选 | 轨道 | 置信度通过/15 | global ipTM中位 | 接触PAE中位Å | 匹配原生阳性充分 | 解释 |",
"|---|---|---|---:|---:|---:|---|---|"]
for d in report["conditions"]:
 if d["role"]=="candidate":
  meaning="低分不可解释为特异性" if not d["matched_native_adequate"] else "仅计算复核，不能证明无结合"
  lines.append(f"| {d['target']} | {d['ligand_id']} | {d['analysis_track']} | {d['baseline_confidence_pass_count']} | {f(d['AF2_global_iptm']['median'])} | {f(d['contact_pae']['median'])} | {'是' if d['matched_native_adequate'] else '否'} | {meaning} |")
lines+=["","## 故障归因边界","",
"1. 身份与评分实现：三组原生参照的物种、entity和残基映射已核验；自比较测试给出接近零RMSD、100%原生接触召回。非对称合成PAE检查确认两个方向保留正确，且内部缺口映射不会错位。新225模型均通过完整序列、有限数值、完整PAE和模型/种子覆盖验收。",
"2. 构建问题：历史仅按可见坐标拼接序列会把KLHL12未解析内部loop当作删除，且其它家族存在末端和配体范围差异。本轮主分析修复为作者声明构建，观测构建只作预定敏感性。",
"3. 预测问题：若主原生对照仍无法恢复，则该条件下的候选低分不能用于排除脱靶。观察到的declared/observed差异不能单独证明某一残基或标签导致故障，因为不同目标构建使用各自冻结的MSA。",
"4. 历史归因限制：旧coordinates不存在；本轮只能描述新条件下的表现，不能把新的成功改写为旧预测已通过。",
"5. 推断边界：即使原生阳性充分，候选低置信度也不是实验不结合证据；没有竞争阻断实验，不能将空间占位或接触覆盖写成已验证阻断。","",
"## 可追溯产物","",
f"- 技术验收：{S/'outputs/acceptance_11863.json'}",
f"- 逐模型完整指标及分母：{D/'all_model_metrics.json'}",
f"- 条件汇总：{D/'condition_summary.tsv'}",
f"- 冻结输入与协议：{S/'plan.json'}",
f"- 冻结MSA验收：{S/'inputs/msa_acceptance.json'}","",
"方法依据：[ColabFold](https://www.nature.com/articles/s41592-022-01488-1)、[AlphaFold-Multimer](https://www.biorxiv.org/content/10.1101/2021.10.04.463034)；实验参照：[2FLU](https://www.rcsb.org/structure/2FLU)、[4CH9](https://www.rcsb.org/structure/4CH9)、[6TTK](https://www.rcsb.org/structure/6TTK)。已知PDB结构可能与模型训练重叠，本轮不作为盲测泛化准确率。",""]
p=D/"SPECIFICITY_REVIEW.md"
with p.open("x") as f:f.write("\n".join(lines))
receipt={"status":"SPECIFICITY_DIAGNOSTIC_REPORT_WRITTEN","job":os.environ["SLURM_JOB_ID"],"report":{"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}}
(S/"outputs/report_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n");print(json.dumps(receipt,indent=2))

