import shutil
from collections import Counter
from util import *
run=Run(R,"90_strengthening_report",[record_file(S/"protocol.json"),record_file(S/"EXECUTION_ADDENDUM.md")]);shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 p,cm=one("88_strengthening_calibration","HELD_FAMILY_CALIBRATION_COMPLETE");cal=read_json(verify_file(cm["outputs"]["results"]));run.manifest["inputs"].append(record_file(p))
 p,gm=one("86_strengthening_geometry","COMPETITION_CONTEXT_COMPLETE");geo=read_json(verify_file(gm["outputs"]["results"]));run.manifest["inputs"].append(record_file(p))
 p,im=one("91_strengthening_context_identity","CONTEXT_IDENTITIES_RECORDED");identities=read_json(verify_file(im["outputs"]["results"]));run.manifest["inputs"].append(record_file(p))
 extensions={};physics={};md=[]
 for stage,status,dest in (("87_strengthening_extension_score","EXTENSION_SCORED",extensions),("84_strengthening_physics","PHYSICS_COMPLETE",physics)):
  for p in (R/"steps"/stage/"runs").glob("*/manifest.json"):
   m=read_json(p)
   if m["status"]==status:
    v=read_json(verify_file(m["outputs"]["results"]));key=v["entry"]["id"];require(key not in dest,"DUPLICATE_ACCEPTED",key);dest[key]=v;run.manifest["inputs"].append(record_file(p))
 require(len(extensions)==129 and len(physics)==114,"MODULE_COUNTS",str((len(extensions),len(physics))))
 for p in (R/"steps/85_strengthening_md/runs").glob("*/manifest.json"):
  m=read_json(p)
  if m["status"]=="MD_DIAGNOSTIC_COMPLETE":
   v=read_json(verify_file(m["outputs"]["results"]));require(len(v["trace"])==100,"MD_TRACE_COUNT",str(p));md.append(dict(id=m["entry_id"],seed=m["seed"],data=v,manifest=record_file(p)));run.manifest["inputs"].append(record_file(p))
 require(len(md)==9 and len({(v["id"],v["seed"]) for v in md})==9,"MD_COVERAGE",str(len(md)))
 p,tm=one("93_strengthening_trajectory_review","ALL_TRAJECTORIES_VERIFIED");traces=read_json(verify_file(tm["outputs"]["results"]))["trajectories"];run.manifest["inputs"].append(record_file(p))
 for v in md:
  reviewed=next(x for x in traces if x["id"]==v["id"] and x["seed"]==v["seed"])
  v["online_trace_preserved_in_source"]=True;v["data"]["online_starting_contact_pairs_equilibration_end"]=v["data"].pop("starting_contact_pairs");v["data"]["trace_reference"]="first saved production DCD frame at 10 ps";v["data"]["trace"]=reviewed["trace"];v["dcd_final_pdb_rmsd"]=reviewed["final_pdb_rmsd"]
 run.save()
 # Reconcile labels/construct qualification without upgrading pending assay metadata.
 old=read_json(R/"steps/41_control_constructs/runs/20260922T101321Z_2f8f58bad35d/outputs/controls.json")
 ext=read_json(R/"steps/52_control_extension/runs/20260922T103806Z_35c0f36f8467/outputs/controls.json")
 labels=[]
 for e in baseplan()["all_controls"]:
  pool=ext if e["id"].startswith("bc_") else old
  row=next(v for v in pool if v.get("id",v.get("binder_id"))==e["source_id"])
  label=str(row.get("label",row.get("binder"))).lower() in ("true","1");require(label==e["positive"],"LABEL_CHANGED",e["id"])
  sequence=row.get("sequence",row.get("A_seq"));require(sequence==e["sequence"],"CONTROL_SEQUENCE_CHANGED",e["id"])
  labels.append(dict(id=e["id"],target=e["target"],label=label,primary_label_verified=row.get("primary_label_verified",False),assay_construct_match=row["assay_construct_match"]))
 med=lambda xs:float(np.median(xs))
 fmt=lambda v:"不可估计" if v is None else f"{v:.3f}"
 lines=["# 蛋白互作阻断设计：计算加强完整报告","","执行ID：COMPUTATIONAL-STRENGTHENING-20260923。全部预定模块的技术输出均已验收；所有候选结论仍属计算证据。","",
 "## 完整性与证据边界","",
 "- 78条公开结合对照＋3条KEAP1候选：1215个新方案复合物预测；其中195个沿用前轮同协议结果，另补1020个。旧方案243个模型用于配对诊断。",
 "- 96条游离单体（含15条消融序列）及33条原生/消融/特异性/全长/自缔合复合物：129项×15模型＝1935个预测。",
 "- 114项界面物理检查，每项3个固定随机种子，共342次Rosetta松弛及界面分析。",
 "- 3个体系×3种子：9条隐式溶剂MD轨迹（运行平台逐条记录），每条100ps平衡＋1ns生产；总生产9ns。",
 "- 127项代码测试通过。全部失败尝试保留；完成计数仅使用通过内容验收的唯一输出。","",
 "这些计算不能证明实验结合、亲和力、细胞内递送或竞争阻断，也不能证明整个workflow相对其他生成方法的优越性。","",
 "## 公开对照校准","",
 "使用4个保守靶标家族留出；IL7Ra和Pdl1归入同组。阈值仅在训练家族选择；跨折≥80%全长相似binder从训练中移除。三个特征组预先固定。每条序列为一个统计单位，15次预测不是15个独立实验。","",
 "|方案|TP|FN|FP|TN|召回率|假阳性率|样本内精确率|","|---|---|---|---|---|---|---|---|"]
 for name,c in list(cal["legacy"].items())+list(cal["pooled"].items()):lines.append(f'|{name}|{c["TP"]}|{c["FN"]}|{c["FP"]}|{c["TN"]}|{fmt(c["TPR"])}|{fmt(c["FPR"])}|{fmt(c["precision"])}|')
 lines+=["","legacy行为按固定旧门槛；新组合行为来自留出家族预测。精确率依赖本队列阳性比例，不可解释为未来实验成功率。","",
 "|留出家族|测试/训练条目|特征组|AUROC|FPR|召回率|Top3阳性/条目|","|---|---|---|---|---|---|---|"]
 for f in cal["folds"]:
  for name,c in f["variants"].items():
   top=c["topK"]["3"];lines.append(f'|{f["family"]}|{f["n_test"]}/{f["n_train"]}|{name}|{fmt(c["AUROC"])}|{fmt(c["FPR"])}|{fmt(c["TPR"])}|{top["positive"]}/{top["n"]}|')
 lines+=["","|特征组|家族bootstrap召回率95%区间|家族bootstrap假阳性率95%区间|","|---|---|---|"]
 for name,v in cal["family_bootstrap"].items():
  a=v.get("TPR");b=v.get("FPR")
  lines.append(f'|{name}|{fmt(a["low"])}–{fmt(a["high"])}|{fmt(b["low"])}–{fmt(b["high"])}|')
 lines+=["","bootstrap以家族为单位重复2000次；只有4个家族，区间粗糙，不能视为精确泛化保证。原始研究可能已用AF2筛选，完整实验标签/构建体仍有缺口；不能称为独立前瞻验证。竞争几何没有相应的78条阻断标签，因此不计算虚假的阻断准确率。","",
 "## 三条候选：游离折叠与界面物理","",
 "|候选|双向ipSAE最小值中位数|游离pLDDT|游离/结合骨架RMSD Å|游离支持比例|界面能量/面积×100|形状互补|界面未满足极性差值/1000Å²|","|---|---|---|---|---|---|---|---|"]
 candidates=[v for v in cal["rows"] if v["role"]=="candidate"]
 for v in candidates:lines.append(f'|{v["id"]}|{fmt(v["ipsae_min"])}|{fmt(v["monomer_plddt"])}|{fmt(v["monomer_bound_rmsd"])}|{fmt(v["monomer_support"])}|{fmt(v["interface_dG_per_area"])}|{fmt(v["shape_complementarity"])}|{fmt(v["unsat_per_1000A2"])}|')
 lines+=["","物理检查统一从AF2 model1/seed1042出发，三次仅改变Rosetta随机种子，未覆盖全部AF2姿态。游离支持比例：单体pLDDT≥80且相对固定model1/seed1042结合态骨架RMSD≤2Å的模型占比。能量为Rosetta单位，不是实验结合自由能；未满足极性使用ddG-style差值，可为负。SASA路径为Rosetta默认VSASA，不能套用DAlphaBall阈值。","",
 "## 原生竞争区域与结构背景","",
 "|候选|原生接触加权覆盖中位数|ETGE谷氨酸接触区域覆盖中位数|参考结构投影数量|","|---|---|---|---|"]
 for v in candidates:
  gs=[g for g in geo["models"] if g["id"]==v["id"]];lines.append(f'|{v["id"]}|{fmt(med([g["native_contact_weighted_coverage"] for g in gs]))}|{fmt(med([g["ETGE_glutamate_contact_residue_coverage"] for g in gs]))}|{sum(len(g["contexts"]) for g in gs)}|')
 lines+=["","|候选|参考背景|对齐靶标RMSD中位数 Å|原生短肽碰撞原子对<1.5Å中位数|额外结构域碰撞原子对<1.5Å中位数|","|---|---|---|---|---|"]
 for v in candidates:
  gs=[g for g in geo["models"] if g["id"]==v["id"]]
  for ref in ("2FLU","1X2R","2DYH","3WN7","AFDB_full"):
   cc=[c for g in gs for c in g["contexts"] if c["structure"]==ref]
   pp=[p["steric_overlap"]["pairs_under_1_5A"] for c in cc for p in c["partners"] if "sequence" in p]
   xx=[c["extra_domain_atoms_collision"]["pairs_under_1_5A"] for c in cc if c["extra_domain_atoms_collision"] is not None]
   lines.append(f'|{v["id"]}|{ref}|{fmt(med([c["target_ca_rmsd"] for c in cc])) if cc else "不可估计"}|{fmt(med(pp)) if pp else "不适用"}|{fmt(med(xx)) if xx else "不适用"}|')
 lines+=["","覆盖基于5Å接触；热点为接触推导代理，未当作实验能量热点。2FLU、1X2R、2DYH、3WN7保留逐残基映射、突变/物种差异及配体重叠记录；非同序列参考仅用于敏感性分析。AFDB全长投影的域间位置不确定，不能据此证明生物学二聚体可达性。","",
 "## 基序与支架消融、特异性及自缔合","",
 "所有合成扰动均未赋予实验阴性标签。跨长度/靶标的置信度和能量差异不是亲和力差异。KEAP1_single为同源蛋白比较的匹配单序列输入；KEAP1_full为完整序列构象诊断；两个同源靶标均包含原生阳性参考。","",
 "|条目|类型|ipTM中位数|ipSAE最小值中位数|原生覆盖中位数|Rosetta界面能量/面积×100|","|---|---|---|---|---|---|"]
 for key,v in extensions.items():
  if v["entry"]["kind"]=="monomer":continue
  rs=v["models"];cov=[r["competition_geometry"]["native_coverage"] for r in rs if "competition_geometry" in r]
  lines.append(f'|{key}|{v["entry"]["kind"]}|{fmt(med([r["iptm"] for r in rs]))}|{fmt(med([r["ipsae_min"] for r in rs]))}|{fmt(med(cov)) if cov else "不适用"}|{fmt(med([r["dG_per_area_x100"] for r in physics[key]["models"]]))}|')
 lines+=["","### 消融序列的游离折叠诊断","","|消融序列|游离pLDDT中位数|相对该突变体结合态RMSD中位数Å|折叠支持模型/15|","|---|---|---|---|"]
 for v in extensions.values():
  if v["entry"].get("original_parent"):
   rs=v["models"];lines.append(f'|{v["entry"]["parent"]}|{fmt(med([r["plddt"] for r in rs]))}|{fmt(med([r["bound_fold_rmsd"] for r in rs]))}|{sum(r["plddt"]>=80 and r["bound_fold_rmsd"]<=2 for r in rs)}/15|')
 lines+=["","若同源靶标原生阳性也得低分，候选对该靶标的低分不能当作特异性证据。全序列/侧翼打乱仅为压力测试，模型低分不能代替湿实验阴性。","",
 "## 多重复MD","",
 "|体系|种子|平台|末200ps姿态RMSD中位数 Å|末200ps自身折叠RMSD中位数 Å|末200ps初始接触保留率|","|---|---|---|---|---|---|"]
 for v in md:
  tail=v["data"]["trace"][-20:];lines.append(f'|{v["id"]}|{v["seed"]}|{v["data"]["platform"]}|{fmt(med([x["binder_pose_rmsd"] for x in tail]))}|{fmt(med([x["binder_fold_rmsd"] for x in tail]))}|{fmt(med([x["initial_atom_contact_retention"] for x in tail]))}|')
 lines+=["","每个体系的三个重复从同一固定构象出发，改变随机速度；未进行不同初始构象采样。报告中的几何指标从已保存DCD独立重算，参考状态统一为生产阶段第一个保存帧（10ps）；原始在线100ps平衡末参考的记录另行保留。末帧坐标与最终PDB逐原子核对，误差须<0.002Å。生产阶段无坐标约束。1ns仅诊断快速结构失稳，不能宣称收敛、停留时间或结合自由能；各时间点存在自相关，不作独立样本检验。隐式溶剂结果不能替代显式溶剂与实验验证。","",
 "## 构建体与标签验收","",
 f'78条标签与原始入库表逐项一致；具有上游primary_label_verified标记的条目为{sum(v["primary_label_verified"] for v in labels)}。其余保持上游未完成状态，不升级为原文验证。',"",
 "|构建体状态|数量|","|---|---|"]
 for k,v in Counter(x["assay_construct_match"] for x in labels).items():lines.append(f"|{k}|{v}|")
 lines+=["","## 方法与复现","",
 "- [BindCraft](https://doi.org/10.1038/s41586-025-09429-6)：重新预测及界面物理检查；本轮不是其原样复现。",
 "- [ipSAE](https://github.com/DunbrackLab/IPSAE)：沿用冻结源码和双向分数。",
 "- [Rosetta InterfaceAnalyzer](https://docs.rosettacommons.org/docs/latest/application_documentation/analysis/interface-analyzer)：分离后重排、能量、埋藏面积和形状互补。",
 "- [BuriedUnsatHbonds](https://docs.rosettacommons.org/docs/latest/scripting_documentation/RosettaScripts/Filters/filter_pages/BuriedUnsatHbondsFilter)：默认SASA路线与ddG-style差值。",
 "- [OpenMM](https://docs.openmm.org/latest/userguide/application/02_running_sims.html)：CPU隐式溶剂模拟。",
 "- [KLHL3–WNK4](https://www.rcsb.org/structure/4CH9)、[KLHL12–DVL1](https://www.rcsb.org/structure/6TTK)：特异性预测的原生阳性参考。","",
 "protocol.json与EXECUTION_ADDENDUM.md记录冻结方案。逐项分数、轨迹、原始模型和错误记录仅保存在远端权威目录；本地仅镜像人类可读报告。","",
 f"权威路径：fudan:{R}","",
 "## 逐项完整性索引",""]
 for inp in run.manifest["inputs"]:lines.append("- "+inp["path"]+" SHA256 "+inp["sha256"])
 lines+=["","## 参考结构身份附录","","|参考结构|实体|名称|来源物种|登记突变数|","|---|---|---|---|---|"]
 for x in identities:
  organisms=", ".join(sorted({o.get("ncbi_scientific_name","未知") for o in x["organisms"]}))
  lines.append(f'|{x["pdb"]}|{x["entity"]}|{x["description"]}|{organisms}|{x["mutations"] if x["mutations"] is not None else "未登记"}|')
 output=run.path/"outputs/计算加强完整报告.md";output.write_text("\n".join(lines)+"\n");run.output("report",output)
 atomic_json(run.path/"outputs/summary.json",dict(calibration=cal,geometry=geo,labels=labels,md=md,extension_count=len(extensions),physics_count=len(physics),all_modules_complete=True,experimental_binding=False,experimental_blockade=False,superiority_established=False));run.output("summary",run.path/"outputs/summary.json")
 destination=R/"reports/computational_strengthening_20260923";destination.mkdir(exist_ok=True)
 for source,name in ((output,output.name),(S/"EXECUTION_ADDENDUM.md","执行方案与方法说明.md")):
  dest=destination/name;shutil.copy2(source,dest);require(digest(dest)==digest(source),"MIRROR_HASH",str(dest))
 print(run.finish("ALL_COMPUTATIONAL_STRENGTHENING_COMPLETE","computational_only",dict(controls=78,candidates=3,extensions=129,physics=114,md_replicates=9)),flush=True)
except Exception as x:run.fail(x);raise

