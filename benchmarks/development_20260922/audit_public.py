import csv,collections,hashlib,math,shutil
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,require
root=Path("/lustre/users/u21111210118/projects/test9")
up=root/"steps/31_calibration_sources/runs/20260922T095613Z_38be86bf866a/manifest.json"
protocol=root/"source/benchmarks/development_20260922/protocol.json"
run=Run(root,"36_public_label_audit",[record_file(up),record_file(protocol)])
shutil.copy2(__file__,run.path/"qc/driver.py")
p=verify_file(read_json(up)["outputs"]["feature_table"])
with p.open() as f: rows=list(csv.DictReader(f))
valid=[];excluded=[];conflicts=[]
for line,r in enumerate(rows,2):
 reason=[]
 if not r["binder_id"] or not r["target_id"]:reason.append("MISSING_ID")
 if r["binder"] not in ["True","False"]:reason.append("MISSING_BINARY_LABEL")
 if not r["A_seq"] or not r["B_seq"]:reason.append("MISSING_SEQUENCE")
 if reason:excluded.append(dict(line=line,id=r["binder_id"],reasons=reason));continue
 r["_line"]=line;r["_label"]=int(r["binder"]=="True")
 valid.append(r)
groups=collections.defaultdict(list)
for r in valid:groups[(r["target_id"],r["A_seq"],r["B_seq"])].append(r)
unique=[]
for key,rs in groups.items():
 labels={r["_label"] for r in rs}
 if len(labels)!=1:conflicts.append(dict(ids=[r["binder_id"] for r in rs],labels=sorted(labels)));continue
 unique.append(sorted(rs,key=lambda r:r["binder_id"])[0])
family_map={"pMHC_NY1":"MHC_I","pMHC_SILSY1":"MHC_I","FGFR2":"RTK","InsulinR":"RTK","EGFR":"RTK","TrkA":"RTK","LTK":"RTK",
 "IL7Ra":"cytokine_receptors","IL2Ra":"cytokine_receptors","IL10Ra":"cytokine_receptors","Mdm2":"MDM2","Pdl1":"PDL1","VirB8":"VirB8","SARS_CoV2_RBD":"viral_RBD","sntx":"toxin"}
# Family groups are conservative broad biological strata; sequence-homology review remains a prerequisite for a claimed independent test.
for r in unique:r["_family"]=family_map[r["target_id"]]
def metric(r,k):
 try:v=float(r[k]);return v if math.isfinite(v) else None
 except (ValueError,TypeError):return None
keys=["colab_iptm_avg","boltz1_iptm_avg","af3_iptm_avg","colab_ipSAE_min","boltz1_ipSAE_min","af3_ipSAE_min"]
def score(rs,k,threshold=None):
 vals=[(metric(r,k),r["_label"]) for r in rs];vals=[x for x in vals if x[0] is not None]
 if not vals:return dict(n=0,positive=0,negative=0,auc=None)
 x=np.array([x for x,y in vals]);y=np.array([y for x,y in vals]);pos=int(y.sum());neg=len(y)-pos
 out=dict(n=len(y),positive=pos,negative=neg,auc=float((rankdata(x)[y==1].sum()-pos*(pos+1)/2)/(pos*neg)) if pos and neg else None)
 if threshold is not None:
  pred=x>=threshold;tp=int((pred&(y==1)).sum());fp=int((pred&(y==0)).sum())
  out.update(threshold=threshold,tp=tp,fp=fp,fn=pos-tp,tn=neg-fp,
   sensitivity=tp/pos if pos else None,specificity=(neg-fp)/neg if neg else None,
   precision=tp/(tp+fp) if tp+fp else None,balanced_accuracy=(tp/pos+(neg-fp)/neg)/2 if pos and neg else None)
 return out
targets=sorted({r["target_id"] for r in unique})
summary=[]
for target in targets:
 rs=[r for r in unique if r["target_id"]==target]
 summary.append(dict(target=target,family=family_map[target],n=len(rs),positive=sum(r["_label"] for r in rs),
  binder_chains=dict(collections.Counter(r["binder_chain"] for r in rs)),target_chains=dict(collections.Counter(r["target_chains"] for r in rs)),
  sources=dict(collections.Counter(r["source"] for r in rs)),metrics={k:score(rs,k) for k in keys}))
# Fully specified simple threshold search; target-balanced training objective, never test labels.
grid=[.3,.4,.5,.6,.7,.75,.8,.85,.9]
cv=[]
for family in sorted(set(family_map.values())):
 train=[r for r in unique if r["_family"]!=family];test=[r for r in unique if r["_family"]==family]
 for k in keys:
  scores=[]
  for cutoff in grid:
   vals=[score([r for r in train if r["target_id"]==t],k,cutoff)["balanced_accuracy"] for t in sorted({r["target_id"] for r in train})]
   vals=[v for v in vals if v is not None]
   if vals:scores.append((float(np.mean(vals)),cutoff))
  if not scores:continue
  objective,cutoff=max(scores)
  for t in sorted({r["target_id"] for r in test}):
   cv.append(dict(heldout_family=family,target=t,metric=k,training_objective=objective,**score([r for r in test if r["target_id"]==t],k,cutoff)))
# Fixed case-control audit sample for exact local protocol rerun, not population precision estimation.
selected=[]
for target,source in [("Mdm2","Mdm2 Watson et al"),("IL7Ra","IL7Ra Watson et al"),("Pdl1","Pdl1 Watson et al")]:
 for label in [0,1]:
  rs=[r for r in unique if r["target_id"]==target and r["source"]==source and r["_label"]==label]
  rs=sorted(rs,key=lambda r:hashlib.sha256(("local-calibration-v1:"+r["binder_id"]).encode()).hexdigest())[:10]
  for r in rs:selected.append({k:r[k] for k in ["binder_id","target_id","binder_chain","target_chains","target_chain_range","binder","source","A_seq","B_seq","A_length","B_length"]})
output=dict(source_rows=len(rows),eligible_rows=len(valid),unique_sequence_pairs=len(unique),excluded=excluded,duplicate_groups=sum(len(rs)>1 for rs in groups.values()),
 conflicting_groups=conflicts,paper_title_count=3766,count_matches_title=len(rows)==3766,targets=summary,threshold_grid=grid,heldout_results=cv,
 analysis_status="RETROSPECTIVE_PUBLISHED_METRIC_AUDIT_NOT_LOCAL_CALIBRATION",
 assay_labels="author_binary_binding_labels; failed_expression_and_assay_conditions_require_primary_source_adjudication",
 family_status="conservative_biological_strata_pending_sequence_homology_review",competition_calibrated=False,local_protocol_calibrated=False)
atomic_json(run.path/"outputs/audit.json",output);run.output("audit",run.path/"outputs/audit.json")
atomic_json(run.path/"outputs/local_control_candidates.json",dict(entries=selected,status="CONSTRUCT_AND_LABEL_REVIEW_PENDING",sampling="deterministic_label_stratified_max10_each_per_target",not_prevalence_representative=True));run.output("local_controls",run.path/"outputs/local_control_candidates.json")
lines=["# 公开实验标签与评价指标审计","",
f"下载文件共{len(rows)}行，含{len(excluded)}行缺失身份/标签/序列；可用行{len(valid)}，精确靶标-双链序列去重且排除冲突后{len(unique)}。文献标题为3,766，不能用标题数字替代实际文件计数。来源：https://doi.org/10.5281/zenodo.15722219。",
"","这是作者公开特征的回顾性检查。Boltz-1不等于本项目Boltz-2，作者ColabFold设置不等于本项目协议；不能将下列阈值直接移植或宣布本地筛选已校准。",
"","|靶标|去重条数|阳性|阴性|ColabFold ipTM AUC|Boltz-1 ipTM AUC|AF3 ipTM AUC|","|---|---:|---:|---:|---:|---:|---:|"]
fmt=lambda x:"不可估计" if x is None else f"{x:.3f}"
for r in summary:lines.append(f"|{r['target']}|{r['n']}|{r['positive']}|{r['n']-r['positive']}|"+ "|".join(fmt(r["metrics"][k]["auc"]) for k in keys[:3])+"|")
lines+=["","按预定义生物学类别留出，训练折内在固定阈值网格上最大化靶标平均balanced accuracy，再评价留出靶标。亲缘分组仍待序列复核，不能称严格跨家族独立验证。未测定竞争阻断。","",
f"选出{len(selected)}条来自RFdiffusion原研究的分层对照候选，供精确构建体和标签核对。抽样使用固定ID哈希，未按模型分数选取；尚未启动其本地推断。"]
md=run.path/"outputs/公开对照审计.md";md.write_text("\n".join(lines)+"\n");run.output("report",md)
print(run.finish("PUBLIC_LABEL_AUDIT_COMPLETE","retrospective_published_metrics"),flush=True)
print("SAMPLE",selected[:2],flush=True)

