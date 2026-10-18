import json,shutil
from pathlib import Path
import numpy as np
from ppiblocker.common import *
root=Path("/lustre/users/u21111210118/projects/test9");run=Run(root,"77_af2_review_report",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 manifests=[]
 for p in (root/"steps/75_af2_review_score/runs").glob("*/manifest.json"):
  m=read_json(p)
  if m["status"] in ("AF2_REVIEW_SCORED","AF2_REVIEW_SCORED_WITH_RELAX_FAILURES"):manifests.append((p,m))
 require(len(manifests)==13 and {m["slot"] for p,m in manifests}==set(range(13)),"INCOMPLETE_REVIEW","Require all 13 distinct entries")
 output=[];paired_controls=[]
 def stats(models):
  n=len(models);good=[x for x in models if x["relaxation_status"]=="COMPLETE"]
  ip=[min(z["ipSAE"] for z in next(v for v in x["ipsae"] if v["pae_cutoff"]==10)["scores"] if z["type"]=="asym") for x in models]
  return dict(n=n,median_iptm=float(np.median([x["raw"]["confidence"]["global_iptm"] for x in models])),median_min_directional_ipsae10=float(np.median(ip)),confidence_pass=sum(x["raw"]["legacy_confidence_only"] for x in models),raw_binding_proxy_pass=sum(x["raw"]["legacy_raw_binding_proxy"] for x in models),design_pose_within2A=sum(x["raw"]["design_recovery"]["binder_ca_after_target_alignment"]<=2 for x in models),median_pose_rmsd=float(np.median([x["raw"]["design_recovery"]["binder_ca_after_target_alignment"] for x in models])),raw_clash_models=sum(x["raw"]["sterics"]["pairs_under_1_5A"]>0 for x in models),raw_backbone_clash_models=sum(x["raw"]["sterics"]["backbone_pairs_under_1_5A"]>0 for x in models),post_relax_binding_proxy_pass=sum(x["raw"]["legacy_confidence_only"] and x["relaxed"]["sterics"]["minimum_heavy_distance"]>=1.5 for x in good),relaxation_complete=len(good),relaxed_models_with_residue_violations=sum(any(v>0 for v in x["relaxation"]["residue_violations"]) for x in good),relaxed_clash_models=sum(x["relaxed"]["sterics"]["pairs_under_1_5A"]>0 for x in good),relaxed_backbone_clash_models=sum(x["relaxed"]["sterics"]["backbone_pairs_under_1_5A"]>0 for x in good),median_relax_pose_movement=float(np.median([x["relaxation_movement"]["binder_ca_after_target_alignment"] for x in good])) if good else None,recycle_cap_reached=sum(x.get("actual_recycles")==12 for x in models))
 for p,m in sorted(manifests,key=lambda v:v[1]["slot"]):
  data=read_json(verify_file(m["outputs"]["results"]));e=data["entry"];rows=data["models"]
  require(len(rows)==18,"MODEL_COUNT",e["id"])
  arms={arm:[x for x in rows if x["arm"]==arm] for arm in ("baseline","expanded")}
  require(len(arms["baseline"])==3 and len(arms["expanded"])==15,"ARM_COUNTS",e["id"])
  a=stats(arms["baseline"]);b=stats(arms["expanded"]);paired=stats([x for x in arms["expanded"] if x["weight"]==1])
  output.append(dict(id=e["id"],target=e["target"],role=e["role"],positive=e.get("positive"),baseline=a,expanded=b,paired_model1=paired,pose_dispersion=data["pose_dispersion"],evidence=record_file(p)))
  if e["role"]=="control":paired_controls.append(dict(id=e["id"],target=e["target"],positive=e["positive"],baseline_pass=a["raw_binding_proxy_pass"]>=2,baseline_post_relax_pass=a["post_relax_binding_proxy_pass"]>=2,paired_model1_pass=paired["raw_binding_proxy_pass"]>=2,paired_model1_post_relax_pass=paired["post_relax_binding_proxy_pass"]>=2))
  run.manifest["inputs"].append(record_file(p))
 run.save()
 atomic_json(run.path/"outputs/summary.json",dict(entries=output,paired_controls=paired_controls,claims=dict(thresholds_promoted=False,superiority_established=False,experimental_binding=False,experimental_blockade=False)))
 run.output("summary",run.path/"outputs/summary.json")
 def fmt(x):return "NA" if x is None else f"{x:.2f}"
 lines=["# AF2 复核改进：实施与配对诊断结果","","完成3条候选和10条公开对照：195个扩展预测、39个旧协议模型（其中缺失基线已补齐）。以下均为计算诊断，不是实验结合/阻断证据。","",
 "## 三条候选的结构复核","","各项分开报告；不只展示最高分模型。姿态 RMSD 为对齐靶标后相对设计骨架的位置偏差。","",
 "|候选|方案|模型数|ipTM中位数|置信度达旧门槛|设计姿态≤2Å|原始碰撞模型|松弛后碰撞/完成松弛|松弛位移中位数Å|",
 "|---|---|---|---|---|---|---|---|---|"]
 for e in output:
  if e["role"]!="candidate":continue
  for arm,label in (("baseline","旧单权重"),("expanded","新五权重")):
   x=e[arm];lines.append(f'|{e["id"]}|{label}|{x["n"]}|{fmt(x["median_iptm"])}|{x["confidence_pass"]}/{x["n"]}|{x["design_pose_within2A"]}/{x["n"]}|{x["raw_clash_models"]}/{x["n"]}|{x["relaxed_clash_models"]}/{x["relaxation_complete"]}|{fmt(x["median_relax_pose_movement"])}|')
 lines+=["","“碰撞”在本表指跨链重原子距离<1.5Å；完整结果另含主链、侧链及范德华重叠计数，不是 MolProbity clashscore。松弛后保留原网络置信度，不以消除碰撞自动升级候选。","",
 "## 公开对照：同权重、同种子配对比较","","每个靶标1阳性/1阴性，样本极小。松弛后列沿用原始网络置信度门槛，仅将最短距离替换为松弛后值，是对照诊断，不是正式门槛升级。此处仅使用新方案的 model1 与旧方案的 model1 比较，均要求三次中至少两次通过旧原始结构 binding proxy；不使用设计骨架相似度代替实验结合标签。","","|靶标|文献标签|旧方案原始|旧方案松弛后诊断|新model1原始|新model1松弛后诊断|","|---|---|---|---|---|---|"]
 for c in paired_controls:lines.append(f'|{c["target"]}|{"阳性" if c["positive"] else "阴性"}|{c["baseline_pass"]}|{c["baseline_post_relax_pass"]}|{c["paired_model1_pass"]}|{c["paired_model1_post_relax_pass"]}|')
 lines+=["","对照从公开数据按ID哈希抽取，未按AF2分数选择；构建体完整标签/实验条件仍有未解决之处，不得推导人群PPV或独立外部验证结论。","",
 "## 全部条目与技术状态","","|条目|角色|完整松弛/18|残留几何违规模型|新模型达到12轮上限|新模型姿态两两RMSD中位数Å|","|---|---|---|---|---|---|"]
 for e in output:lines.append(f'|{e["id"]}|{e["role"]}|{e["baseline"]["relaxation_complete"]+e["expanded"]["relaxation_complete"]}/18|{e["baseline"]["relaxed_models_with_residue_violations"]+e["expanded"]["relaxed_models_with_residue_violations"]}|{e["expanded"]["recycle_cap_reached"]}/15|{fmt(e["pose_dispersion"]["expanded"]["median"])}|')
 lines+=["","## 方法依据与边界","","- [BindCraft](https://doi.org/10.1038/s41586-025-09429-6)：参考其重新预测与物理检查思路。本轮Multimer+Amber不是论文monomer+Rosetta流程的原样复现。",
 "- [ColabFold官方说明](https://github.com/sokrypton/ColabFold/wiki/v1.5.0/702284308448d74c2a49b85036283631f8781484)：模型/种子采样与recycle收敛控制。12轮是本轮预算上限，不是最优值结论。",
 "- [官方ipSAE](https://github.com/DunbrackLab/IPSAE)：PAE 10/15Å、距离15Å，输出双方向分数，无自动阈值升级。",
 "- [OpenMM单位定义](https://docs.openmm.org/latest/api-python/generated/openmm.app.simulation.Simulation.html)：旧AF2容差到OpenMM8的力单位兼容转换已显式记录。",
 "","公开设计可能已在原研究中经过AF2设计/筛选，不构成完全独立验证集。复合物中的自身对齐RMSD不等于游离折叠稳定性。不得把15次预测视为15次独立实验；不得按本轮候选结果调整通过门槛。正式优越性比较仍须合格靶标、完整基线和实验验证。","",
 "## 复现入口",""]
 for e in output:lines.append(f'- {e["id"]}: {e["evidence"]["path"]}')
 p=run.path/"outputs/AF2_复核改进与结果.md";p.write_text("\n".join(lines)+"\n");run.output("report",p)
 print(run.finish("AF2_REVIEW_DIAGNOSTIC_COMPLETE","computational_only",dict(entries=13,expanded_models=195,baseline_models=39,relaxation_failures=sum(18-e["baseline"]["relaxation_complete"]-e["expanded"]["relaxation_complete"] for e in output))),flush=True)
except Exception as e:run.fail(e);raise

