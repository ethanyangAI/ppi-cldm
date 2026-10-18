"""Independent coverage appendix; extends delivery without rewriting accepted artifacts."""
import datetime,hashlib,json,os
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
S=R/"steps/18_qualified_calibration"
def rec(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(Path(p).read_text())
def verify(x):
 r=rec(x["path"]);assert r["sha256"]==x["sha256"] and r["bytes"]==x.get("bytes",r["bytes"])
def write(p,x):
 p=Path(p)
 with p.open("x") as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
def main():
 completion=read(S/"completion.json")
 assert completion["status"]=="QUALIFIED_CONFIDENCE_CALIBRATION_ACCEPTED"
 for key in ["calibration_manifest","independent_acceptance"]:verify(completion[key])
 independent=read(completion["independent_acceptance"]["path"])
 assert independent["status"]=="INDEPENDENT_QUALIFIED_CALIBRATION_VALIDATION_PASS"
 manifest=read(completion["calibration_manifest"]["path"])
 for x in manifest["inputs"]+manifest["source"]+manifest["outputs"]:verify(x)
 result=read(next(x["path"] for x in manifest["outputs"] if x["path"].endswith("/calibration.json")))
 lines=["# 原始confidence分数、OOF覆盖与bootstrap补充说明","",
 "本附录在独立校准验收通过后生成。它补足主报告所称“原始score覆盖另列”的具体表格；不修改已冻结资格、计算规则、主结果、独立验收或原报告哈希。","",
 "原始score完整覆盖指该设计全部15个AF2模型具有有效confidence分数；OOF覆盖指训练fold具备两类且该设计可以计算训练经验百分位；预测覆盖指能应用本fold阈值。三种覆盖单独呈现，未计分/未预测都不会自动成为负类。","",
 "| 集合 | 范围 | 资格n（阳/阴） | 原始完整score（其中阳/阴） | OOF百分位 | 预测 |",
 "|---|---|---:|---:|---:|---:|"]
 allrows=result["all78_rows"]
 for name,key,n in [("main","main_eligible",32),("screen_sensitivity","screen_sensitivity_eligible",67)]:
  res=result["analyses"][name];eligible=[v for v in allrows if v[key]];assert len(eligible)==n
  scopes=[("全部",eligible,res["raw_confidence_coverage"],res["pooled"])]
  for fold in res["folds"]:
   scopes.append((fold["family"],[v for v in eligible if v["family"]==fold["family"]],fold["raw_confidence_coverage"],fold["metrics"]))
  for label,rows,raw,met in scopes:
   assert raw["n_complete"]==sum(v["confidence_score"] is not None for v in rows)
   assert raw["n_eligible"]==len(rows)==met["n_eligible"]
   assert raw["n_complete_positive"]+raw["n_complete_negative"]==raw["n_complete"]
   np=sum(v["positive"] for v in rows);nn=len(rows)-np
   lines.append(f"| {name} | {label} | {len(rows)}（{np}/{nn}） | {raw['n_complete']}/{len(rows)}（{raw['n_complete_positive']}/{raw['n_complete_negative']}） | {met['n_scored']}/{len(rows)} | {met['n_predicted']}/{len(rows)} |")
 lines+=["","主分析Ig_like只有阳性，故该测试fold的FPR与AUROC无定义；这与训练缺类别导致整个fold不能校准是两种不同情况。原始score完整也不保证OOF可估计。","",
 "## Family bootstrap有效重复数","",
 "每集合固定抽样2000次（seed4142）。仅3/4个family，区间粗糙。某次抽样若不含某一真实类别，相应类别率无定义；区间仅使用有定义的重复，未将其填零。","",
 "| 集合 | 指标 | 有效重复 | 无定义重复 | 2.5% | 97.5% |",
 "|---|---|---:|---:|---:|---:|"]
 def fmt(x):return "不可估计" if x is None else f"{x:.3f}"
 for name,res in result["analyses"].items():
  for key,values in res["bootstrap"]["intervals"].items():
   assert values["valid_replicates"]+values["undefined_replicates"]==2000
   lines.append(f"| {name} | {key} | {values['valid_replicates']} | {values['undefined_replicates']} | {fmt(values['low'])} | {fmt(values['high'])} |")
 lines+=["","OOF百分位AUROC只在合格训练fold和可评分的测试条目上估计，逐family结果优先。所有结果限于回顾性作者条件结合screen，不建立标准化亲和力、阻断、前瞻命中率或workflow优越性。","",
 f"原有效完成入口：{S/'completion.json'}","",f"本轮完整交付入口：{S/'delivery.json'}",""]
 run=Path(completion["calibration_manifest"]["path"]).parent
 report=run/"outputs/RAW_COVERAGE_APPENDIX.md";assert not report.exists();report.write_text("\n".join(lines)+"\n")
 source=R/"source/rebuild/calibration_qualified_coverage.py"
 assert rec(__file__)["sha256"]==rec(source)["sha256"]
 supplement=dict(status="ACCEPTED_CALIBRATION_COVERAGE_APPENDIX",job_id=os.environ["SLURM_JOB_ID"],created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputs=[rec(S/"completion.json"),completion["calibration_manifest"],completion["independent_acceptance"]],source=[rec(__file__),rec(source)],outputs=[rec(report)],scientific_outputs_modified=False)
 sm=run/"coverage_appendix_manifest.json";write(sm,supplement)
 delivery=dict(status="QUALIFIED_CONFIDENCE_CALIBRATION_ACCEPTED_WITH_COVERAGE_APPENDIX",original_completion=rec(S/"completion.json"),required_original_completion_status="QUALIFIED_CONFIDENCE_CALIBRATION_ACCEPTED",coverage_appendix_manifest=rec(sm),reports=[next(x for x in manifest["outputs"] if x["path"].endswith("/REPORT.md")),rec(report)],scientific_scope=completion["scope"])
 write(S/"delivery.json",delivery)
 print(json.dumps(delivery,indent=2),flush=True)
if __name__=="__main__":main()

