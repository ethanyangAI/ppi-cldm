import sys,shutil,statistics,collections
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json
root=Path("/lustre/users/u21111210118/projects/test9")
summary=root/"steps/21_benchmark_analysis/runs/20260922T051817Z_f84fa156702c/outputs/summary.json"
controls=root/"steps/20_control_verification/runs/20260922T050110Z_9f8abb590ef6/outputs/results.json"
run=Run(root,"23_benchmark_report",[record_file(summary),record_file(controls)])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 rows=[]
 for r in read_json(summary):
  sels=[]
  for p in (root/"steps/07_benchmark_selection/runs").glob("*/manifest.json"):
   m=read_json(p)
   if r["evaluation_manifest"] and any(x["sha256"]==r["evaluation_manifest"]["sha256"] for x in m.get("inputs",[])):sels.append((p,m))
  assert len(sels)==1,(r["case"],r["method"],len(sels))
  p,m=sels[0];selection=read_json(verify_file(m["outputs"]["selection"]))
  models=[x for c in r["candidate_metrics"] for x in c["models"]]
  rows.append(dict(case=r["case"],method=r["method"],count=r["count"],selection_manifest=record_file(p),
   s0_eligible=selection["arms"]["s0"]["eligible_count"],s1_eligible=selection["arms"]["s1"]["eligible_count"],
   median_pair_iptm=statistics.median(x["metrics"]["pair_iptm"] for x in models),
   median_coverage=statistics.median(x["geometry"]["native_interface_coverage"] for x in models),
   median_binder_rmsd=statistics.median(x["geometry"]["binder_ca_rmsd_after_target_alignment"] for x in models),
   clusters=r["structural_clusters_single_link"],design_manifest=r["design_manifest"],evaluation_manifest=r["evaluation_manifest"],
   eligible_primary=r["case"]!="P32",exclusion="S63T coordinate-vs-canonical discrepancy; NMR-constrained docking reference" if r["case"]=="P32" else None))
 ct=[]
 for r in read_json(controls):
  assert r["status"]=="COMPLETE",r["id"]
  i=int(r["id"].split("-")[1])
  label="confirmed_binding" if i in [5,9,10,12,13] else ("no_binding_detected" if i in [1,2,4,8] else ("weak_unstructured_binding" if i in [6,7] else "expression_failure"))
  ct.append(dict(id=r["id"],label=label,
   median_pair_iptm=statistics.median(x["metrics"]["pair_iptm"] for x in r["models"]),
   binding_pass_samples=sum(x["binding_proxy_pass"] for x in r["models"]),
   joint_pass_samples=sum(x["binding_proxy_pass"] and x["competition_geometry_pass"] for x in r["models"]),
   median_interface_coverage=statistics.median(x["geometry"]["native_interface_coverage"] for x in r["models"])))
 positive=[x for x in ct if x["label"]=="confirmed_binding"];negative=[x for x in ct if x["label"]=="no_binding_detected"]
 auc=sum((a["median_pair_iptm"]>b["median_pair_iptm"])+.5*(a["median_pair_iptm"]==b["median_pair_iptm"]) for a in positive for b in negative)/(len(positive)*len(negative))
 metrics=dict(positive_n=len(positive),negative_n=len(negative),auc_pair_iptm=auc,
  positive_detected=sum(x["binding_pass_samples"]>=2 for x in positive),
  negative_rejected=sum(x["binding_pass_samples"]<2 for x in negative),
  caveat="Descriptive same-target retrospective controls; no held-out calibration, exact assay-construct match, or de novo blockade endpoint.")
 result=run.path/"outputs/summary.json";atomic_json(result,dict(pools=rows,controls=ct,control_metrics=metrics));run.output("summary",result)
 lines=["# Benchmark 实际运行汇总（AF2 复核前）","","本页只汇总已完成的 Boltz 复折叠，不是完整 benchmark 或优越性证明。","",
 "|体系|生成方法|候选|S0合格|S1合格|中位pair-ipTM|中位界面覆盖|中位binder RMSD Å|TM≥0.8簇数|",
 "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
 for r in rows:lines.append(f"|{r['case']}|{r['method']}|{r['count']}|{r['s0_eligible']}|{r['s1_eligible']}|{r['median_pair_iptm']:.3f}|{r['median_coverage']:.3f}|{r['median_binder_rmsd']:.2f}|{r['clusters']['0.8']}|")
 lines+=["","P32 排除主比较：坐标序列相对当前 P07900 有 S63T 差异，且 2K5B 是 NMR 约束对接模型。其他样本均属于开发集。","","|公开对照|文献实验分类|中位pair-ipTM|结合代理通过/3|结合+竞争几何通过/3|","|---|---|---:|---:|---:|"]
 for r in ct:lines.append(f"|{r['id']}|{r['label']}|{r['median_pair_iptm']:.3f}|{r['binding_pass_samples']}|{r['joint_pass_samples']}|")
 lines+=["",f"公开确认结合对照识别：{metrics['positive_detected']}/{len(positive)}；未检出结合对照排除：{metrics['negative_rejected']}/{len(negative)}。仅以中位 pair-ipTM 的描述性 AUC={auc:.3f}。",
 "该 AUC 来自同一靶标的回顾性对照，不能作为跨靶标泛化或阻断验证。KB-6/7 是弱结合但未形成设计折叠的类别，不并入主要阴性；KB-3/11 表达失败，不是结合阴性。",
 "公开研究 DOI: https://doi.org/10.1016/j.isci.2025.112621；序列逐条匹配补充 Table S1 与 Data S1。",
 "", "新设计每池只有2个骨架、4条序列、单个生成种子；复折叠的3个样本不是3个独立设计。"]
 report=run.path/"outputs/Boltz_实际运行汇总.md";report.write_text("\n".join(lines)+"\n");run.output("report",report)
 print(report.read_text(),flush=True);print(run.finish("BOLTZ_REPORT_COMPLETE","computational_only"),flush=True)
except Exception as e:run.fail(e);raise

