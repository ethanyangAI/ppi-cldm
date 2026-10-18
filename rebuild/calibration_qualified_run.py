"""Apply frozen qualification and calibration to the uniform, accepted step17 scores."""
import sys,json,os,datetime,math,hashlib
from pathlib import Path
import numpy as np
R=Path("/lustre/users/u21111210118/projects/test9")
sys.path.insert(0,str(R/"source/rebuild"))
import calibration_qualified as c
S=c.S
def load_inputs(score_path):
 freeze=c.read(S/"freeze_receipt.json")
 for v in freeze["outputs"]+[freeze["source"]]:c.verify(v)
 proto=c.read(S/"frozen/protocol.json")
 for v in proto["inputs"]:c.verify(v)
 fcheck=c.read(S/"validation/freeze_acceptance.json");assert fcheck["status"]=="INDEPENDENT_FREEZE_VALIDATION_PASS";c.verify(fcheck["freeze_receipt"]);c.verify(fcheck["tests"])
 sq=c.read(S/"validation/sequence_uniqueness.json");assert sq["status"]=="ALL78_BINDER_SEQUENCES_UNIQUE" and sq["unique_sequence_hashes"]==78;c.verify(sq["input"])
 summary=c.read(score_path);assert summary["status"]=="ALL_78_CONTROLS_SCORED_WITH_EXPLICIT_MISSINGNESS"
 for k in ["plan","acceptance","model_scores"]:c.verify(summary[k])
 acc=c.read(summary["acceptance"]["path"]);assert acc["status"]=="ALL_1170_CONTROL_MODELS_VERIFIED" and acc["model_count"]==1170
 accepted={x["condition"]["condition_id"]:x for x in acc["accepted_conditions"]}
 rows=c.read(S/"frozen/eligibility78.json")["entries"];scored={x["id"]:x for x in summary["entries"]}
 assert len(scored)==len(summary["entries"])==len(rows)==78 and set(scored)==set(accepted)=={x["id"] for x in rows}
 for row in rows:
  s=scored[row["id"]];a=accepted[row["id"]]
  assert s["sequence_sha256"]==row["sequence_sha256"] and s["target_sequence_sha256"]==row["target_sequence_sha256"]
  models=s["models"];assert len(models)==s["model_count"]==15
  assert {(x["model"],x["seed"]) for x in models}=={(m,se) for m in range(1,6) for se in [1042,1043,1044]}
  amap={(x["model"],x["seed"]):x for x in a["models"]}
  values=[]
  for x in models:
   am=amap[(x["model"],x["seed"])]
   assert x["pdb"]==am["pdb"] and x["scores"]==am["scores"]
   vals=[x["global_iptm"],x["binder_plddt"],x["interface_plddt"],x["bidirectional_contact_PAE_A"]]
   if all(c.finite(v) for v in vals):
    assert all(0<=v<=1 for v in vals[:3]) and vals[3]>=0
    if x["contact_residue_pair_count"]>0:
     val=min(vals[0]/.75,vals[1]/.8,vals[2]/.8,8/max(vals[3],.01))
    else:val=None
   else:val=None
   if val is None:assert x["confidence_baseline"] is None
   else:assert c.finite(x["confidence_baseline"]) and math.isclose(val,x["confidence_baseline"],rel_tol=1e-12,abs_tol=1e-12)
   values.append(val)
  good=[v for v in values if v is not None];median=float(np.median(good)) if len(good)==15 else None
  assert (median is None and s["confidence_baseline_median"] is None) or (median is not None and math.isclose(median,s["confidence_baseline_median"],abs_tol=1e-12))
  assert s["confidence_baseline_n_valid"]==len(good) and s["confidence_baseline_n_missing"]==15-len(good)
  row.update(confidence_score=median,n_confidence_models=len(good),n_missing_confidence_models=15-len(good),confidence_score_range=[min(good),max(good)] if good else None,score_status="complete" if median is not None else "missing_complete_ensemble")
 pairs=c.read(S/"frozen/cross_family_sequence_leakage.json")["pairs"]
 near={(v["id1"],v["id2"]) for v in pairs}|{(v["id2"],v["id1"]) for v in pairs}
 inputs=[c.rec(p) for p in [S/"freeze_receipt.json",S/"validation/freeze_acceptance.json",S/"validation/sequence_uniqueness.json",score_path]]+[summary[k] for k in ["plan","acceptance","model_scores"]]
 archive_path=S/"source_archive.json";archive=c.read(archive_path)
 assert archive["status"]=="EXECUTION_DRIVERS_ARCHIVED_BYTE_IDENTICAL"
 for pair in archive["drivers"]:
  c.verify(pair["execution_driver"]);c.verify(pair["source_snapshot"])
  assert pair["execution_driver"]["sha256"]==pair["source_snapshot"]["sha256"]
 inputs.append(c.rec(archive_path))
 return rows,near,inputs
def raw_coverage(rows):
 return dict(n_eligible=len(rows),n_complete=sum(v["confidence_score"] is not None for v in rows),n_missing=sum(v["confidence_score"] is None for v in rows),n_complete_positive=sum(v["confidence_score"] is not None and v["positive"] for v in rows),n_complete_negative=sum(v["confidence_score"] is not None and not v["positive"] for v in rows))
def report(data):
 def fmt(x):return "不可估计" if x is None else f"{x:.3f}"
 lines=["# 资格清理后的 confidence-only 校准报告","",f"本报告由 Slurm CPU 作业 {data['job_id']} 生成；UTC 时间 {data['created_utc']}。","",
 "原78条控制全部保留身份和原始标签。资格在本轮AF2评分前冻结；主分析32条（21阳性、11条件阴性），扩展screen敏感性67条（38阳性、29条件阴性）。11条非单体非命中保留为QC未解决，未强行计为负类。78个binder序列SHA均唯一。","",
 "每个设计统一5个AF2-Multimer v3模型权重×3种子，共15个模型；统计单位为设计序列。全部15个模型confidence分数有效才纳入主分数中位数。训练归一化、阈值选择只用相应训练family。","",
 "## 逐family留出结果","",
 "留出family结果优先；Ig_like主分析没有条件阴性，因此FPR与AUROC不可估计。训练FPR≤0.20是阈值选择约束，不保证留出FPR≤0.20。表中评分coverage为可计算的留出百分位；原始AF2完整score覆盖另列，训练单类不等同于AF2分数缺失。","",
 "| 集合 | 留出family | 资格n（阳/阴） | 可评分/可预测 | TPR | FPR | AUROC | 阈值（训练百分位） |","|---|---|---:|---:|---:|---:|---:|---:|"]
 for name,res in data["analyses"].items():
  for fold in res["folds"]:
   m=fold["metrics"];lines.append(f"| {name} | {fold['family']} | {m['n_eligible']}（{m['n_positive']}/{m['n_negative']}） | {m['n_scored']}/{m['n_predicted']} | {fmt(m['TPR'])} | {fmt(m['FPR'])} | {fmt(m['AUROC'])} | {fmt(fold['fit']['threshold'])} |")
 lines+=["","## 汇总与覆盖","",
 "| 集合 | 全资格分母 | 评分coverage | 预测coverage | TP/FP/TN/FN | TPR | FPR | OOF百分位AUROC |","|---|---:|---:|---:|---|---:|---:|---:|"]
 for name,res in data["analyses"].items():
  m=res["pooled"];lines.append(f"| {name} | {m['n_eligible']} | {m['n_scored']}/{m['n_eligible']} | {m['n_predicted']}/{m['n_eligible']} | {m['TP']}/{m['FP']}/{m['TN']}/{m['FN']} | {fmt(m['TPR'])} | {fmt(m['FPR'])} | {fmt(m['AUROC'])} |")
 lines+=["","混淆矩阵及率使用有预测的子集；缺失预测不计为失败或阴性。表中同时保留完整资格分母；OOF AUROC仅对各fold的训练经验百分位计算，不能替代各family结果。","",
 "## 固定confidence参考及family bootstrap","",
 "固定参考使用同一次复核的原始confidence score≥1，不重新调整标签，不与已丢失的历史模型作伪配对比较。"]
 for name,res in data["analyses"].items():
  m=res["fixed_confidence_reference"];bs=res["bootstrap"]["intervals"]
  lines+=[f"- {name}固定参考：TP/FP/TN/FN={m['TP']}/{m['FP']}/{m['TN']}/{m['FN']}；TPR={fmt(m['TPR'])}，FPR={fmt(m['FPR'])}，预测覆盖={m['n_predicted']}/{m['n_eligible']}。",
   f"- {name}校准family bootstrap（2000次，seed4142；{res['bootstrap']['families']}个family）：TPR区间[{fmt(bs['TPR']['low'])}, {fmt(bs['TPR']['high'])}]，FPR区间[{fmt(bs['FPR']['low'])}, {fmt(bs['FPR']['high'])}]。"]
 lines+=["","## 解释边界","",
 "只有3或4个靶蛋白family，bootstrap区间粗糙。模型由既有设计流程挑选，数据为回顾性作者筛选集合；类别比例不代表新设计命中率。RF完整实测target构建、实际逐设计浓度/重复仍未完整公开；BBF分析对应作者SPR条件。扩展集合额外包含剂量、单体状态及BetV1 F63/L63构建不确定性。","",
 "本报告检验confidence与原作者条件结合标签的一致性，不建立标准化亲和力、天然伴侣阻断、前瞻成功概率或workflow优越性。ipSAE、单体折叠、物理评分、竞争几何与特异性均未加入本轮联合门槛。","",
 "原始实验资格来源：[RFdiffusion论文](https://www.nature.com/articles/s41586-023-06415-8)、[作者数据](https://doi.org/10.6084/m9.figshare.22662094)、[BindCraft论文](https://www.nature.com/articles/s41586-025-09429-6)。逐行证据及哈希见step14资格overlay与本报告manifest。","",
 "## 复现入口","",f"结果：{data['run_dir']}/outputs/calibration.json","",f"验收：{data['run_dir']}/manifest.json。独立复核通过后方可作为本轮完成结果引用。"]
 return "\n".join(lines)+"\n"
def main():
 score_path=Path(sys.argv[1])
 rows,near,inputs=load_inputs(score_path)
 tests=c.selftest();assert tests["status"]=="PASS"
 job=os.environ["SLURM_JOB_ID"];run=S/"runs"/(datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"_"+job)
 run.mkdir(parents=True,exist_ok=False);(run/"outputs").mkdir()
 analyses={key:c.evaluate([dict(v) for v in rows if v[field]],near) for key,field in [("main","main_eligible"),("screen_sensitivity","screen_sensitivity_eligible")]}
 for name,field in [("main","main_eligible"),("screen_sensitivity","screen_sensitivity_eligible")]:
  eligible=[v for v in rows if v[field]]
  analyses[name]["raw_confidence_coverage"]=raw_coverage(eligible)
  for fold in analyses[name]["folds"]:
   fold["raw_confidence_coverage"]=raw_coverage([v for v in eligible if v["family"]==fold["family"]])
 result=dict(status="QUALIFIED_CONFIDENCE_CALIBRATION_COMPLETE_PENDING_INDEPENDENT_VALIDATION",created_utc=c.now(),job_id=job,run_dir=str(run),all78_rows=rows,analyses=analyses,score_coverage_all78=dict(n=78,complete=sum(v["confidence_score"] is not None for v in rows),missing=sum(v["confidence_score"] is None for v in rows)),frozen_cross_family_near_pairs=len(near)//2,inputs=inputs,independent_experimental_validation=False)
 c.write(run/"outputs/calibration.json",result,True);c.write(run/"outputs/tests.json",tests,True)
 (run/"outputs/REPORT.md").write_text(report(result))
 man=dict(status=result["status"],job_id=job,created_utc=c.now(),inputs=inputs,source=[c.rec(__file__),c.rec(c.__file__),c.rec(c.MATH)],outputs=[c.rec(run/"outputs"/p) for p in ["calibration.json","tests.json","REPORT.md"]])
 c.write(run/"manifest.json",man,True)
 c.write(S/"calibration_pointer.json",dict(status=man["status"],manifest=c.rec(run/"manifest.json")),True)
 print(json.dumps(dict(status=man["status"],manifest=c.rec(run/"manifest.json"),coverage=result["score_coverage_all78"],analyses={k:v["pooled"] for k,v in analyses.items()}),indent=2),flush=True)
if __name__=="__main__":main()

