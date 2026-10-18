import os,json,hashlib,statistics
from pathlib import Path
import numpy as np
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/15_specificity_review";D=S/"outputs/analysis_11863"
def rec(p):
 p=Path(p);return {"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}
def verify(r):
 p=Path(r["path"]);assert rec(p)["sha256"]==r["sha256"];return p
def new(p,obj):
 with Path(p).open("x") as f:json.dump(obj,f,indent=2,allow_nan=False);f.write("\n")
prior=json.loads((S/"outputs/independent_acceptance.json").read_text());assert prior["status"]=="SPECIFICITY_REVIEW_INDEPENDENTLY_VERIFIED"
attrreceipt=json.loads((S/"outputs/failure_attribution_receipt.json").read_text())
for row in attrreceipt["inputs"]+attrreceipt["outputs"]:verify(row)
attrs=json.loads((D/"failure_attribution.json").read_text());assert attrs["thresholds_changed"] is False
models=json.loads((D/"all_model_metrics.json").read_text())["models"];plan=json.loads((S/"plan.json").read_text())
bycondition={x["condition_id"]:x for x in attrs["conditions"]};targets={x["target"]:x for x in plan["targets"]}
annotations=json.loads((D/"summary.json").read_text())["construct_annotations"]
rawreasons={};regions=[]
for row in models:
 score=json.loads(verify(row["scores"]).read_text());n=row["coverage"]["query_target_length"];pl=np.array(score["plddt"])/100;pae=np.array(score["pae"])
 interface=row["interface_full_query"];positions=[i-1 for i in interface["target_residues"]]+[n+j-1 for j in interface["partner_residues"]]
 errors=[pae[i-1,n+j-1] for i,j in interface["residue_pairs"]]+[pae[n+j-1,i-1] for i,j in interface["residue_pairs"]]
 reasons=[]
 if score["iptm"]<.75:reasons.append("GLOBAL_IPTM_LT_0_75")
 if float(pl[n:].mean())<.8:reasons.append("BINDER_PLDDT_LT_0_8")
 if not positions:reasons.append("NO_INTERFACE_PLDDT")
 elif float(pl[positions].mean())<.8:reasons.append("INTERFACE_PLDDT_LT_0_8")
 if not errors:reasons.append("NO_CONTACT_PAE")
 elif float(np.mean(errors))>8:reasons.append("CONTACT_PAE_GT_8A")
 stored=next(x for x in bycondition[row["condition_id"]]["per_model_gate_reasons"] if (x["model"],x["seed"])==(row["model"],row["seed"]))
 assert reasons==stored["reasons"] and bool(not reasons)==row["baseline_confidence_pass"]
 rawreasons[(row["condition_id"],row["model"],row["seed"])]=reasons
 if row["role"]=="native" and row["analysis_track"]=="primary_declared_entity":
  t=targets[row["target"]];a=annotations[row["target"]];tm=t["construct_mapping"][0];lm=t["construct_mapping"][1]
  tags=set(a[0]["non_uniprot_mapped_positions"]);missing=set(tm["missing_entity_positions"])
  groups={"target_observed_core":(0,tm["observed_to_declared_positions"]),"target_tag_linker_extension":(0,sorted(tags)),"target_unobserved_native_mapped":(0,sorted(missing-tags)),"target_unobserved_internal_loop":(0,tm["internal_missing_positions"]),"ligand_observed_core":(n,lm["observed_to_declared_positions"]),"ligand_unobserved_flanks":(n,lm["missing_entity_positions"])}
  regions.append({"condition_id":row["condition_id"],"model":row["model"],"seed":row["seed"],"regions":{name:{"n_residues":len(pos),"mean_plddt":float(np.mean([pl[offset+i-1] for i in pos])) if pos else None} for name,(offset,pos) in groups.items()}})
for condition in attrs["conditions"]:
 cid=condition["condition_id"];rs=[v for k,v in rawreasons.items() if k[0]==cid];assert len(rs)==15
 for gate,count in condition["gate_failure_counts_not_mutually_exclusive"].items():assert count==sum(gate in r for r in rs)
 assert condition["baseline_pass"]==sum(not r for r in rs)
summ=[]
for gene in ("KEAP1","KLHL3","KLHL12"):
 cid=gene+"__native_"+targets[gene]["pdb"]+"__declared";rows=[r for r in regions if r["condition_id"]==cid];assert len(rows)==15
 entry={"target":gene,"condition_id":cid,"regions":{}}
 for name in rows[0]["regions"]:
  xs=[r["regions"][name] for r in rows];assert len({x["n_residues"] for x in xs})==1
  vals=[x["mean_plddt"] for x in xs if x["mean_plddt"] is not None]
  entry["regions"][name]={"n_residues":xs[0]["n_residues"],"median_model_mean_plddt":statistics.median(vals) if vals else None,"n_models":len(vals)}
 summ.append(entry)
rpath=D/"region_attribution.json";new(rpath,{"status":"DECLARED_NATIVE_REGION_CONFIDENCE_PARTITION_COMPLETE","models":regions,"summary":summ,"scope":"Confidence partition, not a causal intervention or new score threshold."})
def val(x):return "NA" if x is None else f"{x:.3f}"
lines=["# 核心、标签及未观测片段的置信度诊断","","以下数值是每个模型区域平均pLDDT在15个模型中的中位数，尺度0–1；括号内为残基数。没有改变原置信度门。","","| 原生靶点 | target实验核心 | target标签/连接区 | target未观测天然映射区 | target内部未观测loop | ligand观测核心 | ligand未观测侧翼 |","|---|---:|---:|---:|---:|---:|---:|"]
order=["target_observed_core","target_tag_linker_extension","target_unobserved_native_mapped","target_unobserved_internal_loop","ligand_observed_core","ligand_unobserved_flanks"]
for x in summ:
 cells=[f"{val(x['regions'][k]['median_model_mean_plddt'])} ({x['regions'][k]['n_residues']})" for k in order];lines.append("| "+x["target"]+" | "+" | ".join(cells)+" |")
lines+=["","KEAP1原生肽16个残基均有实验坐标，仍因整条配体pLDDT不足而全部未过联合门；目标标签区低分并非该配体门的直接组成项，不能把失败简单归因于His标签。","",
"KLHL12的声明原生肽包含7个未解析侧翼残基，其置信度与8个观测核心分开报告。完整序列的全局ipTM及整条配体pLDDT门未通过，而15/15可恢复预定几何；这是指标接受与姿态恢复不一致，不能描述成15个姿态全部失败。主分析仍保持0/15联合门通过。","",
"KLHL3原生结构的几何恢复和多项置信度均不足，不能仅归因于短肽侧翼或标签。declared/observed条件同时改变构建体及其MSA，不能从该比较隔离某段序列的因果贡献。",""]
md=D/"REGION_DIAGNOSTICS.md"
with md.open("x") as f:f.write("\n".join(lines))
complete=D/"SPECIFICITY_REVIEW_COMPLETE.md"
with complete.open("x") as f:
 f.write((D/"SPECIFICITY_REVIEW.md").read_text()+"\n---\n\n"+(D/"FAILURE_ATTRIBUTION_ADDENDUM.md").read_text()+"\n---\n\n"+md.read_text())
receipt={"status":"SPECIFICITY_FAILURE_ATTRIBUTION_INDEPENDENTLY_VERIFIED","job":os.environ["SLURM_JOB_ID"],"verified_raw_score_gate_decisions":270,"verified_condition_gate_counts":18,"declared_native_region_profiles":45,"thresholds_changed":False,"prior_full_geometry_validation":rec(S/"outputs/independent_acceptance.json"),"attribution_receipt":rec(S/"outputs/failure_attribution_receipt.json"),"outputs":[rec(rpath),rec(md),rec(complete)]}
rp=S/"outputs/attribution_independent_acceptance.json";new(rp,receipt)
manifest={"status":"SPECIFICITY_REVIEW_COMPLETE_AND_INDEPENDENTLY_ACCEPTED","main_plan":rec(S/"plan.json"),"msa_acceptance":rec(S/"inputs/msa_acceptance.json"),"technical_acceptance":rec(S/"outputs/acceptance_11863.json"),"numerical_acceptance":rec(S/"outputs/independent_acceptance.json"),"attribution_acceptance":rec(rp),"model_metrics_manifest":rec(D/"manifest.json"),"report":rec(complete),"counts":{"primary_new_models":180,"sensitivity_new_models":45,"reused_context_models":45,"unique_scored_models":270,"primary_conditions":12,"sensitivity_conditions":3,"additional_core_candidate_conditions":3},"gpu_budget":{"actual_aggregate_gpu_seconds":5820,"actual_gpu_hours":5820/3600,"array_start":"2026-10-02T21:53:06 cluster local time","array_end":"2026-10-02T22:41:48 cluster local time","maximum_simultaneous_gpus":2},"claims":{"old_coordinates_restored":False,"experimental_specificity":False,"experimental_blockade":False,"workflow_superiority":False}}
new(S/"manifest.json",manifest);print(json.dumps(manifest,indent=2));print(json.dumps(summ,indent=2))

