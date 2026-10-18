import sys,shutil,statistics,json
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json
root=Path("/lustre/users/u21111210118/projects/test9")
single_jobs=["185890","185891","185892","185902"]
msa_jobs=sys.argv[1:]
assert len(msa_jobs)==3
paths={
"boltz_summary":root/"steps/23_benchmark_report/runs/20260922T052344Z_6cb1d7733a0a/outputs/summary.json",
"matrix":root/"steps/23_benchmark_report/runs/20260922T052729Z_3fc714e8d511/manifest.json",
"pose_metrics":root/"steps/13_pose_truth_metrics/runs/20260922T042158Z_b0ea9949bffd/outputs/results.json",
"diversity":root/"steps/21_benchmark_analysis/runs/20260922T053720Z_d2498450e529/outputs/diversity.json",
"costs":root/"steps/23_benchmark_report/runs/20260922T054228Z_53e9121d4215/outputs/costs.json",
"repair":root/"steps/22_contract_repair/runs/20260922T052219Z_6b997422badc/manifest.json",
"plan":root/"steps/21_benchmark_analysis/runs/20260922T051817Z_f84fa156702c/outputs/af2_plan.json",
"msa":root/"steps/24_target_msa/runs/20260922T053230Z_5f5d81e4f519/manifest.json",
"msa_inputs":root/"steps/25_af2_msa_verification/runs/20260922T055222Z_30bdf3c291d1/manifest.json"}
def collect(step,jobs):
 selected={}
 for p in (root/"steps"/step/"runs").glob("*/manifest.json"):
  m=read_json(p);j=m.get("execution",{}).get("slurm_job_id")
  if j in jobs:
   assert j not in selected,(j,p)
   assert m["status"]=="AF2_VERIFICATION_COMPLETE",(j,m["status"])
   rows=read_json(verify_file(m["outputs"]["results"]))
   assert all(len(r["models"])==3 for r in rows)
   selected[j]=(p,rows)
 assert set(selected)==set(jobs),(selected.keys(),jobs)
 return selected
single=collect("19_af2_verification",single_jobs);msa=collect("25_af2_msa_verification",msa_jobs)
for label,items in [("single",single),("msa",msa)]:
 for j,(p,rows) in items.items():paths[label+"_"+j]=p
run=Run(root,"23_benchmark_report",[record_file(p) for p in paths.values()])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 base=read_json(paths["boltz_summary"]);plan={r["id"]:r for r in read_json(paths["plan"])["entries"]}
 ss={r["id"]:r for p,rows in single.values() for r in rows};ms={r["id"]:r for p,rows in msa.values() for r in rows}
 assert len(ss)==45 and len(ms)==41,(len(ss),len(ms))
 def med(rows,key):return statistics.median(m["metrics"][key] for r in rows for m in r["models"])
 def af_stats(data,cid,method):
  rows=[r for id,r in data.items() if plan[id]["group"]==cid and plan[id].get("method")==method]
  if not rows:return None
  return dict(n=len(rows),binding=sum(r["binding_proxy_pass_count"]>=2 for r in rows),joint=sum(r["joint_proxy_pass_count"]>=2 for r in rows),iptm=med(rows,"global_iptm"))
 def af_control(data,id):
  r=data[id.replace("-","_")];return dict(iptm=med([r],"global_iptm"),binding=r["binding_proxy_pass_count"],joint=r["joint_proxy_pass_count"])
 results=[]
 for pool in base["pools"]:
  results.append(dict(**pool,af2_single=af_stats(ss,pool["case"],pool["method"]),af2_target_msa=af_stats(ms,pool["case"],pool["method"])))
 controls=[dict(**r,af2_single=af_control(ss,r["id"]),af2_target_msa=af_control(ms,r["id"])) for r in base["controls"]]
 def control_auc(field):
  pos=[r[field]["iptm"] for r in controls if r["label"]=="confirmed_binding"]
  neg=[r[field]["iptm"] for r in controls if r["label"]=="no_binding_detected"]
  return sum((a>b)+.5*(a==b) for a in pos for b in neg)/(len(pos)*len(neg))
 af_diagnostics={key:dict(positive_detected=sum(r[key]["binding"]>=2 for r in controls if r["label"]=="confirmed_binding"),
  negative_rejected=sum(r[key]["binding"]<2 for r in controls if r["label"]=="no_binding_detected"),auc=control_auc(key)) for key in ["af2_single","af2_target_msa"]}
 out=run.path/"outputs/final_summary.json";atomic_json(out,dict(pools=results,controls=controls,af2_control_diagnostics=af_diagnostics,
  full_six_target_pilot_complete=False,superiority_established=False,experimental_blockade=False));run.output("summary",out)
 lines=["# PPI blocker workflow：实际 benchmark 与项目审计报告",
 "",
 "日期：2026-09-22。结论：已完成本轮结构资格审查、工程修复、实际小规模生成比较及双验证器复核；尚未证明 workflow 的 blocker 命中率优于现有方法，也未实现对任意两蛋白都能产出有效 blocker。",
 "",
 "原定六靶标、四生成器、双种子、每格64候选的先导没有达到构建体资格门槛。本报告不把下面的小规模开发实验冒充该完整先导。实验阻断、选择性、表达和细胞可达性均未由本项目测定。",
 "",
 "## 1. 已实际完成的范围",
 "",
 "- 48个候选蛋白对和2个身份哨兵全量登记；扩大C0/C1结构检索，并对30个C2体系及2个哨兵追加坐标审查。每项裁决见同目录《50项测试矩阵执行状态》。有界检索失败不等于不存在互作或结构。",
 "- 两个匹配指定序列的开发构建体：WDR5–KMT2A，4ESG assembly 1；KEAP1–NFE2L2，2FLU assembly 1。二者都是孤立结构域–16残基肽，不代表全长生理复合体。",
 "- 主生成比较：2体系 × 3设计路线 × 4序列 = 24候选；路线为RFdiffusion+ProteinMPNN、保留完整原生肽的motif scaffolding、BoltzGen。它们不是三个完全独立的模型家族。",
 "- 另有WDR5预测pose输入消融4条，以及HSP90参考构建体挑战4条，共32条新序列。HSP90挑战排除主比较。",
 "- 每池2骨架×2序列，长度65，生成种子42；Boltz复核3样本。每池仅两个主要结构单元，不能把4条序列或12个模型视为独立靶标重复。",
 "- 13条已发表KEAP1设计逐条匹配补充Table S1与Data S1，完成Boltz和AF2复核。公开实验标签保留其原始含义，未当成本项目新实验。",
 f"- AF2单序列复核覆盖45条序列、135个模型；目标MSA敏感性复核覆盖41条、123个模型。后者不包括已排除的HSP90挑战。两者均无模板、无松弛，multimer-v3 model 1，种子1042–1044、3次recycle。",
 "",
 "## 2. 原生pose盲预测",
 "",
 "|体系|流程门控|置信度最高模型DockQ|三个模型DockQ范围|解释|",
 "|---|---|---:|---|---|"]
 for d in read_json(paths["pose_metrics"]):
  scores={r["index"]:r["dockq"]["best_dockq"] for r in d["models"]}
  top=scores[d["confidence_top1_index"]]
  lines.append(f"|{d['case_id']}|{d['prediction_status']}|{top:.3f}|{min(scores.values()):.3f}–{max(scores.values()):.3f}|同一构建体A/B固定链映射；非新binder DockQ|")
 lines+=["", "WDR5盲预测可进入后续设计；KEAP1虽接近参考结构，仍被原冻结门槛拒绝，主要涉及短肽pLDDT及多样本通过要求。这是门控可能漏检的证据，不能据此事后放宽主分析阈值。两例参考结构早于模型训练时代，盲输入不等于训练数据无泄漏。",
 "",
 "## 3. 共池筛选结果",
 "",
 "S0只用结合相关门槛，S1在同一候选池、同一排序下增加竞争几何门槛。K=8保留空名额；4条小池不能当成8次实验失败。",
 "",
 "|体系/分层|路线|候选|S0合格|S1合格|中位Boltz pair-ipTM|中位界面覆盖|中位binder RMSD Å|",
 "|---|---|---:|---:|---:|---:|---:|---:|"]
 for r in results:
  label=r["case"]+("（排除挑战）" if not r["eligible_primary"] else "（输入消融）" if r["method"]=="RF_predicted_pose" else "")
  lines.append(f"|{label}|{r['method']}|{r['count']}|{r['s0_eligible']}|{r['s1_eligible']}|{r['median_pair_iptm']:.3f}|{r['median_coverage']:.3f}|{r['median_binder_rmsd']:.2f}|")
 lines+=["","主比较没有足够S0合格候选，因此S1相对S0的真实阻断增益不可估计。界面覆盖较高仍可同时伴随低互作置信度或巨大骨架偏移；覆盖和排斥几何不能自行成为阻断金标准。当前小池失败不能证明这些靶标不可设计。",
 "",
 "## 4. AF2独立复核与MSA敏感性",
 "",
 "AF2的global ipTM与Boltz两个方向取最小值的pair-ipTM不是同一指标。下面是单独的探索性代理判据（至少2/3样本通过），不能直接替换主S0/S1。MSA分析因单序列对照失配而追加，属于事后诊断；候选池没有按分数删减。",
 "",
 "|体系|路线|单序列结合代理/候选|目标MSA结合代理/候选|目标MSA联合代理/候选|单序列中位ipTM|目标MSA中位ipTM|",
 "|---|---|---|---|---|---:|---:|"]
 for r in results:
  a=r["af2_single"];b=r["af2_target_msa"]
  lines.append(f"|{r['case']}|{r['method']}|{a['binding']}/{a['n']}|{str(b['binding'])+'/'+str(b['n']) if b else '不运行：排除挑战'}|{str(b['joint'])+'/'+str(b['n']) if b else '不适用'}|{a['iptm']:.3f}|{format(b['iptm'],'.3f') if b else '不适用'}|")
 lines+=["","仅两个公开靶蛋白结构域序列提交到ColabFold公共MSA服务；生成binder序列未提交。目标MSA在CPU取回、哈希固定；binder仅单序列，没有配对同源序列或模板。复合物A3M经过序列与链长度往返检查后才使用。",
 "",
 "## 5. 公开对照揭示评估器边界",
 "",
 "|对照|文献类别|Boltz中位pair-ipTM|Boltz通过/3|AF2单序列ipTM|AF2目标MSA ipTM|AF2目标MSA通过/3|",
 "|---|---|---:|---:|---:|---:|---:|"]
 labels={"confirmed_binding":"BLI/ITC支持结合","no_binding_detected":"未检出结合","weak_unstructured_binding":"弱结合/未形成设计折叠","expression_failure":"表达失败，结合不可判定"}
 for r in controls:lines.append(f"|{r['id']}|{labels[r['label']]}|{r['median_pair_iptm']:.3f}|{r['binding_pass_samples']}|{r['af2_single']['iptm']:.3f}|{r['af2_target_msa']['iptm']:.3f}|{r['af2_target_msa']['binding']}|")
 b=base["control_metrics"];a=af_diagnostics["af2_single"];m=af_diagnostics["af2_target_msa"]
 lines += ["",f"在5个确认结合和4个未检出结合的主要标签上：Boltz识别{b['positive_detected']}/5、排除{b['negative_rejected']}/4，描述性AUC={b['auc_pair_iptm']:.3f}；AF2单序列识别{a['positive_detected']}/5、排除{a['negative_rejected']}/4，AUC={a['auc']:.3f}；AF2目标MSA识别{m['positive_detected']}/5、排除{m['negative_rejected']}/4，AUC={m['auc']:.3f}。",
 "AUC只按连续置信度在同一靶标的9个回顾性标签上计算；阈值通过率另含结构与置信度门槛。不能称跨靶标独立验证，不能把表达失败或弱而无序的结合混成普通阴性。作者原研究已用AF2筛选，存在验证器选择偏差；本次KEAP1构建体也不是对原实验构建体的精确复现。",
 "高置信度放过部分表达失败/无序设计，说明模型不能替代表达、折叠、制备和特异性实验。公开阳性中的漏检也说明单一阈值不可被当作绝对生物真值。",
 "",
 "## 6. 结构多样性与成本",
 "",
 "TM-align在65残基binder上做对称归一化的最小TM分数，按单连接聚类；这只测池内结构差异，不是相对训练库的新颖性。",
 "",
 "|体系|序列数（含消融/挑战）|TM≥0.6簇|TM≥0.8簇|TM≥0.95簇|",
 "|---|---:|---:|---:|---:|"]
 for cid,d in read_json(paths["diversity"]).items():lines.append(f"|{cid}|{len(d['ids'])}|{len(d['clusters']['0.6'])}|{len(d['clusters']['0.8'])}|{len(d['clusters']['0.95'])}|")
 lines+=["","|体系|路线|成功生成命令分钟|共用Boltz复核分钟|","|---|---|---:|---:|"]
 for r in read_json(paths["costs"]):lines.append(f"|{r['case']}|{r['method']}|{r['generation_seconds']/60:.2f}|{r['refold_seconds']/60:.2f}|")
 lines+=["","成本表为成功后端命令墙钟时间，每作业申请1 GPU；不含排队、权重校验/启动I/O、原生pose推断和失败重试。motif恢复任务计入已成功且被复用的原RFdiffusion命令。没有独立GPU利用率/峰值显存测量，且节点存在共享负载；不能据此宣称确定的加速倍数。",
 "",
 "## 7. 审计发现与已修复缺陷",
 "",
 "1. 近似identity曾允许结构序列替代指定构建体。实际发现2K5B HSP90相对当前P07900的63位为T而非S；RCSB页面仍标注Mutation(s): No，所以不能只信元数据标签。已改为精确构建体匹配，并在使用历史pose启动设计前再次核验。WDR5/KEAP1逐残基完全一致。",
 "2. 外部候选导入原可缺少与内部设计一致的互作/背景审查。内部设计、外部输入导出、外部候选导入现共用validate_design_pose，禁止未审查的多链、辅因子背景和序列差异从旁路进入。",
 "3. 107项测试通过；实际WDR5和KEAP1重新prepare通过，P32旧输入按预期拒绝。修复提交af6248d8e18fcc2aacf26ed8e1af9d34b5e7057d；原生成主计算使用caf60647950f0624fde4b82349c9c73998099e21。历史产物未回写为新版通过。",
 "4. P32原盲预测使用canonical序列，参考设计使用观测差异序列，因此不得作为匹配pose消融。其参考还是NMR约束HADDOCK模型，单列不确定性挑战并排除主比较。此次不确认差异是人工突变还是历史序列注释差异。",
 "5. XIAP–DIABLO未因某份坐标未记录Zn而放行；必需背景仍应被模型显式支持。非蛋白小分子路线不属于本次RFdiffusion+MPNN蛋白binder的已验收范围。",
 "",
 "## 8. 与现有工作的关系及可支持的主张",
 "",
 "RFdiffusion、ProteinMPNN、motif scaffolding以及用AF2筛设计都已有先例。2025年KEAP1研究已将这些方法用于该互作并给出实验结果，因此不能把这一组合或KEAP1示例本身作为新颖性证明。[KEAP1原始研究](https://doi.org/10.1016/j.isci.2025.112621)",
 "",
 "可证明的工程改进是：精确身份和背景准入、原生伙伴pose溯源、同池S0/S1比较、失败/空名额保留、外部方法适配和审计链。待证明的科学增量是：在跨家族留出集及真实竞争实验中，伙伴pose条件与竞争筛选是否提高阻断命中率、选择性和单位成本收益。",
 "",
 "进一步文献与40维设计见2026-09-20调研方案；本轮增加公开对照与验证器失配诊断。现代方法官方实现见[BoltzGen](https://github.com/HannesStark/boltzgen)、[BindCraft](https://github.com/martinpacesa/BindCraft)、[RFdiffusion3](https://github.com/RosettaCommons/foundry)。BindCraft/RFD3在本轮未执行，不应出现在结果排行榜中。多维评测应防止单一验证器偏差与相关序列重复计数，参见[ProtDBench](https://arxiv.org/abs/2605.04118)。",
 "",
 "## 9. 完整性核查与停止升级条件",
 "",
 "|用户科学目标|当前状态|",
 "|---|---|",
 "|两蛋白身份解析、可用结构fetch、缺结构时pose推断|已实现并在限定构建体实际执行；无法承诺任意背景都可靠|",
 "|按原生互作pose生成蛋白binder|RFdiffusion+MPNN与BoltzGen均已真实运行；生成不等于有效阻断|",
 "|广类型测试矩阵与现有方法调研|50项逐项裁决及40维方案已交付；多数复杂背景尚未被当前二元路线支持|",
 "|可复现benchmark与评估器审查|本轮开发小池及公开对照完成；六靶标四方法完整先导未完成|",
 "|证明workflow优越|未建立；S0/S1真实阻断增益不可估计|",
 "|实验验证|未开展；需要实际平台、构建体、样品预算与实验执行|",
 "",
 "结论是NO_GO进入优越性主张或直接升级大规模主榜。继续扩大前，必须获得足够跨类型、精确序列且背景可建模的构建体，冻结家族/同源分组和训练泄漏审查，验收剩余生成器，并在开发数据上完成验证器校准后再固定留出测试规则。",
 "实验应分别测表达/可溶性、直接结合、原生伙伴竞争、同源/非相关靶标选择性及相关细胞功能。此前288个实验名额只是预算草案，未下单或启动实验。当前报告不把代码完成、任务结束或代理分数等同于上述实验终点。",
 "",
 "## 10. 复现与证据入口",
 "",
 "远端唯一计算权威：\`fudan:/lustre/users/u21111210118/projects/test9\`。本地仅交付人类可读报告。环境为独立Conda前缀，所有安装、分析与模型调用通过Slurm，未推送GitHub。",
 "",
 "生成：RFdiffusion Complex_base + ProteinMPNN（冻结vendor/权重指纹）；BoltzGen 0.3.2、FP32、关闭CUDA12可选kernel，显式固定权重与seed wrapper。复核：Boltz 2.2.1；ColabFold 1.5.5/AF2 multimer-v3、JAX 0.4.23 CUDA11。环境与权重校验、命令、资源、结构、分数、候选池均保留在各run的manifest及qc/logs。",
 "",
 "模型运行中的失败安装、下载、JSONL序列化和环境漂移均有日志；恢复任务引用已完成产物并保留失败来源，不按成功重写历史。完整指针和SHA-256见《运行证据索引》。",
 ""]
 report=run.path/"outputs/Benchmark_实际执行与审计报告.md";report.write_text("\n".join(lines)+"\n");run.output("report",report)
 index=["# 运行证据索引","","所有路径均位于远端test9；SHA-256对应本次报告读取的文件。","","|用途|路径|SHA-256|","|---|---|---|"]
 indexed={**paths}
 for r in results:
  for k in ["design_manifest","evaluation_manifest","selection_manifest"]:indexed[r["case"]+"_"+r["method"]+"_"+k]=Path(r[k]["path"])
 for key,p in indexed.items():
  rec=record_file(p);index.append(f"|{key}|{p}|{rec['sha256']}|")
 ix=run.path/"outputs/运行证据索引.md";ix.write_text("\n".join(index)+"\n");run.output("index",ix)
 print(run.finish("BENCHMARK_RUNTIME_AUDIT_COMPLETE","computational_benchmark_audit",dict(full_six_target_pilot_complete=False,superiority_established=False,generated_sequences=32,primary_comparison_sequences=24,af2_single_models=135,af2_target_msa_models=123)),flush=True)
except Exception as e:run.fail(e);raise

