import os,json,hashlib,statistics
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/15_specificity_review";D=S/"outputs/analysis_11863"
models=json.loads((D/"all_model_metrics.json").read_text())["models"];conditions=json.loads((D/"summary.json").read_text())["conditions"]
def receipt(p):return {"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}
def med(xs):return statistics.median(xs) if xs else None
def reasons(x):
 c=x["confidence"];r=[]
 if c["AF2_global_iptm"]<.75:r.append("GLOBAL_IPTM_LT_0_75")
 if c["binder_plddt"]<.8:r.append("BINDER_PLDDT_LT_0_8")
 if c["interface_plddt"] is None:r.append("NO_INTERFACE_PLDDT")
 elif c["interface_plddt"]<.8:r.append("INTERFACE_PLDDT_LT_0_8")
 if c["bidirectional_contact_pae"]["mean"] is None:r.append("NO_CONTACT_PAE")
 elif c["bidirectional_contact_pae"]["mean"]>8:r.append("CONTACT_PAE_GT_8A")
 assert (len(r)==0)==x["baseline_confidence_pass"];return r
rows=[]
allgates=("GLOBAL_IPTM_LT_0_75","BINDER_PLDDT_LT_0_8","NO_INTERFACE_PLDDT","INTERFACE_PLDDT_LT_0_8","NO_CONTACT_PAE","CONTACT_PAE_GT_8A")
for c in conditions:
 xs=[x for x in models if x["condition_id"]==c["condition_id"]];assert len(xs)==15
 geo=[x for x in xs if x["role"]=="native" and x["geometry"]["ligand_CA_RMSD_after_target_alignment_A"]<=5 and x["geometry"]["native_contact_recall"]>=.5]
 row={"condition_id":c["condition_id"],"target":c["target"],"role":c["role"],"track":c["analysis_track"],"n_models":15,"baseline_pass":sum(not reasons(x) for x in xs),"gate_failure_counts_not_mutually_exclusive":{g:sum(g in reasons(x) for x in xs) for g in allgates},"global_iptm_median":med([x["confidence"]["AF2_global_iptm"] for x in xs]),"full_ligand_plddt_median":med([x["confidence"]["binder_plddt"] for x in xs]),"interface_plddt_median":med([x["confidence"]["interface_plddt"] for x in xs if x["confidence"]["interface_plddt"] is not None]),"observed_ligand_plddt_median":med([x["plddt_regions"]["experimental_observed_ligand"]["mean"] for x in xs if "experimental_observed_ligand" in x["plddt_regions"]]),"observed_core_target_plddt_median":med([x["plddt_regions"]["experimental_observed_target_core"]["mean"] for x in xs]),"target_tag_or_extension_plddt_median":med([x["plddt_regions"]["tag_linker_or_unmapped_target_extension"]["mean"] for x in xs if x["plddt_regions"]["tag_linker_or_unmapped_target_extension"]["mean"] is not None]),"contact_pae_median":med([x["confidence"]["bidirectional_contact_pae"]["mean"] for x in xs if x["confidence"]["bidirectional_contact_pae"]["mean"] is not None]),"geometry_only_recovery_count":len(geo) if c["role"]=="native" else None,"geometry_recovered_but_baseline_failed_count":sum(bool(reasons(x)) for x in geo) if c["role"]=="native" else None,"per_model_gate_reasons":[{"model":x["model"],"seed":x["seed"],"reasons":reasons(x)} for x in xs]}
 rows.append(row)
result={"status":"FIXED_THRESHOLD_FAILURE_ATTRIBUTION_COMPLETE","job":os.environ["SLURM_JOB_ID"],"input":[receipt(D/"all_model_metrics.json"),receipt(D/"summary.json")],"thresholds_changed":False,"new_inference":False,"conditions":rows,"interpretation_boundary":"Geometry recovery and confidence acceptance are separate axes. Confidence-gate failure does not imply pose failure or absence of binding. Construction/MSA sensitivity cannot isolate a single causal residue."}
p=D/"failure_attribution.json"
with p.open("x") as f:json.dump(result,f,indent=2);f.write("\n")
def f(x):return "NA" if x is None else f"{x:.3f}"
lines=["# 特异性复核：固定门槛失败归因补充","","原置信度门与主/敏感性分母均保持不变。本表把原生姿态恢复和置信度接受分开，避免将后者失败写成“没有恢复结合姿态”。","","| 原生条件 | 几何恢复/15 | 几何恢复但置信度失败 | ipTM失败 | ligand pLDDT失败 | interface pLDDT失败 | contact PAE失败 | ligand/observed ligand pLDDT中位 |","|---|---:|---:|---:|---:|---:|---:|---|"]
for x in rows:
 if x["role"]=="native":
  g=x["gate_failure_counts_not_mutually_exclusive"];lines.append(f"| {x['condition_id']} | {x['geometry_only_recovery_count']} | {x['geometry_recovered_but_baseline_failed_count']} | {g['GLOBAL_IPTM_LT_0_75']} | {g['BINDER_PLDDT_LT_0_8']} | {g['INTERFACE_PLDDT_LT_0_8']} | {g['CONTACT_PAE_GT_8A']} | {f(x['full_ligand_plddt_median'])}/{f(x['observed_ligand_plddt_median'])} |")
lines+=["","几何恢复定义仍为实验观测核心对齐后配体Cα RMSD≤5Å且5Å接触召回≥0.5，单独呈现，不代替要求置信度的原生阳性充分规则。每列失败计数可重叠。","",
"## 解读",""]
for gene in ("KEAP1","KLHL3","KLHL12"):
 a=next(x for x in rows if x["target"]==gene and x["role"]=="native" and x["track"]=="primary_declared_entity");b=next(x for x in rows if x["target"]==gene and x["role"]=="native" and x["track"]=="sensitivity_observed_construct")
 lines.append(f"- {gene}：declared原生几何恢复 {a['geometry_only_recovery_count']}/15、联合置信度通过 {a['baseline_pass']}/15；observed分别为 {b['geometry_only_recovery_count']}/15 与 {b['baseline_pass']}/15。主分析仍按declared报告，不能用敏感性更高的通过率替换。")
lines+=["","KLHL3候选的global ipTM可以较高而联合门不通过，逐模型失败原因已完整保存；因此不得仅看一个ipTM数字或一个最终布尔标签作特异性结论。","",
"置信度阈值原用于候选设计筛选，在短原生肽中可能与真实姿态恢复不一致。本轮结果只支持报告这种失配，不在这些已知阳性上重调阈值并宣称获得独立校准。原生对照不充分时，候选低分不支持无脱靶结论。即使对照充分，计算低分也不是实验不结合证据。","",
"本补充与SPECIFICITY_REVIEW.md共同构成完整报告；不覆盖已验收的原报告或历史基准。",""]
md=D/"FAILURE_ATTRIBUTION_ADDENDUM.md"
with md.open("x") as f:f.write("\n".join(lines))
r={"status":"FAILURE_ATTRIBUTION_ADDENDUM_VERIFIED_FROM_FROZEN_MODEL_METRICS","job":os.environ["SLURM_JOB_ID"],"inputs":result["input"],"outputs":[receipt(p),receipt(md)],"count_conditions":18,"count_models":270,"all_gate_boolean_values_reproduced":True,"changed_thresholds":False}
out=S/"outputs/failure_attribution_receipt.json"
with out.open("x") as f:json.dump(r,f,indent=2);f.write("\n")
print(json.dumps([x for x in rows if x["role"]=="native"],indent=2));print(json.dumps(r,indent=2))

