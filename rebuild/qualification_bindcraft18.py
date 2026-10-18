#!/usr/bin/env python3
"""Adjudicate frozen BindCraft18 primary assay evidence without altering base78 or registry.
Run in project core Python inside Slurm. This records a conditional published-SPR endpoint;
it is not a new binding experiment, a calibrated intrinsic-affinity truth set, or blockade validation.
"""
import csv,hashlib,json,os,shutil,subprocess,zipfile
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
from ppiblocker.structure import read_structure
R=Path("/lustre/users/u21111210118/projects/test9")
D=R/"steps/14_control_qualification/bindcraft18";S=D/"sources";O=D/"outputs";I=D/"inputs"
BASE=R/"steps/02_controls_recovery/runs/20261002T113406Z_11698/outputs/recovered_controls78.json"
CSV=R/"01_raw/control_sources/41586_2025_9429_MOESM4_ESM.csv"
ZIP=R/"01_raw/control_sources/DesignModels.zip"
def digest(p,algorithm="sha256"):
 h=hashlib.new(algorithm)
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":digest(p)}
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
def seqhash(s):return hashlib.sha256(s.encode()).hexdigest()
def main():
 assert os.environ.get("SLURM_JOB_ID"),"Slurm CPU allocation required"
 for d in (O,I):d.mkdir(parents=True,exist_ok=True)
 for p in (R/"00_admin/reconstruction_20261002.json",R/"steps/02_controls_recovery/runs/20261002T121226Z_11797_coverage_audit/outputs/coverage_audit.json"):
  dest=I/p.name
  if not dest.exists():shutil.copy2(p,dest)
 assert digest(CSV)=="c87fd6cd0a54fe57d840938be07449394abbd55318494c8cc0292b6417c16b4f"
 rows=json.loads(BASE.read_text())["entries"];chosen=[x for x in rows if x["id"].startswith("bc_")]
 assert len(chosen)==18 and Counter(x["target"] for x in chosen)=={"BBF-14":11,"BetV1":7}
 with CSV.open() as f:primary=list(csv.DictReader(f))
 scope=[{"source_csv_row":i+2,**r} for i,r in enumerate(primary) if r["Target"] in ("BBF-14","BetV1")]
 dump(O/"primary_target21_full_rows.json",scope)
 misleading=O/"primary_selected18_full_rows.json"
 if misleading.exists():misleading.unlink() # own provisional extraction name contained 21 target rows
 p18=[x for x in scope if x["Binding"] in ("0","1")]
 assert len(p18)==18
 dump(O/"primary_selected18_full_rows.json",p18)
 missing=[{"source_csv_row":x["source_csv_row"],"source_id":x["DesignName"],"binding_raw":x["Binding"],"reason":"no_binary_measurement_label_not_in_frozen18_not_a_negative"} for x in scope if x["Binding"] not in ("0","1")]
 dump(O/"unlabelled_source_rows_outside_frozen18.json",missing)
 sources={}
 source_urls={x["name"]:x for name in ("source_download_receipts.json","supplementary_download_receipts.json") for x in json.loads((S/name).read_text())}
 for key,name in {"article":"nature_article.html","SI":"supplementary_information.pdf","reporting":"reporting_summary.pdf","zenodo_v1":"zenodo_14249738.json","zenodo_v3":"zenodo_15277801.json","pdb9HAC":"pdb9HAC.cif","pdb9HAC_target":"pdb9HAC_entity1.json","pdb9HAC_binder":"pdb9HAC_entity2.json","uniprot_BetV1":"uniprot_P15494.json","github":"bindcraft_repo_tree.json"}.items():
  sources[key]={"artifact":rec(S/name),"url":source_urls[name]["url"]}
 sources["pdb7MXL_target"]={"artifact":rec(S/"pdb7MXL_entity3.json"),"url":"https://data.rcsb.org/rest/v1/core/polymer_entity/7MXL/3"}
 sources["primary_table"]={"artifact":rec(CSV),"url":"https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-025-09429-6/MediaObjects/41586_2025_9429_MOESM4_ESM.csv"}
 for item in source_urls.values():
  if item.get("status")=="DOWNLOADED":assert digest(Path(item["artifact"]["path"]))==item["artifact"]["sha256"]
 md5=digest(ZIP,"md5");matching_versions=[]
 for ver in ("14249738","15277801"):
  data=json.loads((S/f"zenodo_{ver}.json").read_text())
  for asset in data["files"]:
   if asset["key"]=="DesignModels.zip" and asset["checksum"]=="md5:"+md5:matching_versions.append(ver)
 assert matching_versions,"Author model archive must match official deposited version"
 sources["author_models"]={"artifact":rec(ZIP),"md5":md5,"official_zenodo_matching_versions":matching_versions,"url":"https://zenodo.org/records/"+matching_versions[0]}
 report_note={"source":"reporting","page":2,"method":"manual_visual_review_of_CPU_rendered_page","render":rec(O/"reporting_summary_page2.jpg"),"SPR":{"measurement_series":"single","concentration_levels":"multiple stated generally; prescreen 10 uM per Methods","negative_control":"parallel separate channel, exact control identity unknown","independent_replicate_n":"unknown","replication_statement":"general successful replication asserted, no per-design replicate count"},"ELISA":{"reporting_summary":"single replicates","main_figure_3i":"two technical replicates for three donors","interpretation":"do not infer independent biological replicate n beyond three donor sera; preserve reporting difference"}}
 dump(O/"reporting_summary_review.json",report_note)
 target9=json.loads((S/"pdb9HAC_entity1.json").read_text())["entity_poly"]["pdbx_seq_one_letter_code_can"]
 binder9=json.loads((S/"pdb9HAC_entity2.json").read_text())["entity_poly"]["pdbx_seq_one_letter_code_can"]
 uni=json.loads((S/"uniprot_P15494.json").read_text());canonical=uni["sequence"]["value"]
 ref7=json.loads((S/"pdb7MXL_entity3.json").read_text())["entity_poly"]["pdbx_seq_one_letter_code_can"]
 bbf=next(x["target_sequence"] for x in chosen if x["target"]=="BBF-14")
 bet=next(x["target_sequence"] for x in chosen if x["target"]=="BetV1")
 assert target9=="M"+bbf+"GSGWHHHHHH"
 assert canonical==ref7 and len(canonical)==len(bet)+1
 variants=[{"canonical_position":i+2,"model_position":i+1,"canonical":a,"model":b} for i,(a,b) in enumerate(zip(canonical[1:],bet)) if a!=b]
 assert variants==[{"canonical_position":63,"model_position":62,"canonical":"F","model":"L"}]
 natural=[x for x in uni["features"] if x["type"]=="Natural variant" and x["location"]["start"]["value"]==63 and "L" in x.get("alternativeSequence",{}).get("alternativeSequences",[])]
 assert len(natural)==1
 target_profiles={
 "BBF-14":{"identity":"synthetic beta barrel","model_core_sequence":bbf,"model_core_length":len(bbf),"deposited_crystal_target_sequence":target9,"terminal_changes":{"prefix":"M","suffix":"GSGWHHHHHH"},"model_core_vs_deposited_experimental_target":"EXACT_CONTIGUOUS_CORE_TERMINAL_TAGS_EXPLAINED","source_refs":["pdb9HAC_target","pdb9HAC","article"],"assay_target_full_sequence":"unknown; deposited crystal construct is direct supporting evidence, not per-well SPR sequence certification","native_PPI_partner":"none established; de novo scaffold binding endpoint"},
 "BetV1":{"identity":"birch allergen Bet v 1","model_core_sequence":bet,"model_core_length":len(bet),"canonical_accession":"P15494","canonical_sequence":canonical,"canonical_sequence_version":uni["entryAudit"]["sequenceVersion"],"canonical_sequence_last_update":uni["entryAudit"]["lastSequenceUpdateDate"],"reference_7MXL_target_sequence":ref7,"terminal_changes":{"canonical_initiator_M_absent_in_model":True},"internal_differences":variants,"variant_annotation":natural[0],"model_core_vs_canonical_target":"NATURAL_F63L_VARIANT_IN_MODEL_NOT_CANONICAL","assay_variant_identity":"unknown","model_core_vs_actual_assay_target":"UNRESOLVED","critical_for_exact_construct_calibration":True,"source_refs":["uniprot_BetV1","pdb7MXL_target","author_models"],"native_PPI_partner":"no single standardized native partner; serum IgE is heterogeneous and REGN antibodies are assay competitors"}}
 dump(O/"target_construct_comparison.json",target_profiles)
 assay={"id":"BindCraft2025_author_SPR_screen","endpoint":"author-reported binding detection versus non-detection under published SPR conditions","format":"purified recombinant proteins, immobilized target and soluble designed-binder analyte","expression":"E. coli BL21 CodonPlus(DE3), pET21b or pET11; per-row vector unknown","purification":"Ni-NTA then SEC at cohort level; per-row purity/yield/folding readouts not deposited","screen_concentration_uM":10,"kinetics":"serial dilutions for selected binders; exact row-specific ranges unknown","instrument":"Biacore8K","target_immobilization":"CM5 amine coupling, approximately100RU target level","buffer":{"HEPES_mM":10,"pH":7.4,"NaCl_mM":150,"EDTA_mM":3,"P20_percent":0.005},"flow_uL_min":30,"contact_time":"unknown_varied_by_assay","temperature_C":"unknown","positive_definition":"publisher Binding=1, observed SPR binding; raw numeric RU decision threshold unknown","negative_definition":"publisher Binding=0, not detected in stated screen; not untested and not proof of intrinsic absence of affinity","control":"separate parallel negative-control channel; exact control identity unknown","replicates_profile":"reporting_summary_review.json","source_refs":["article","reporting","primary_table"],"scope_exclusions":["not standardized thermodynamic monomer affinity","not an absence-of-binding claim at every concentration","not blockade","not calibrated assay detection probability"]}
 unknowns=[
 {"field":"full_assayed_binder_sequence_and_tag_linker","value":"unknown_except_crystal_BBF_b4_deposit","critical_for_conditioned_author_SPR_label":False,"critical_for_intrinsic_core_affinity_or_exact_construct":True},
 {"field":"per_design_purity_yield_solubility_folding_QC","value":"unknown","critical_for_conditioned_author_SPR_label":False,"critical_for_interpreting_negative_as_intrinsic_nonbinding":True},
 {"field":"raw_sensorgrams_RU_cutoff_detection_limit","value":"unknown_except_selected_plotted_panels","critical_for_conditioned_author_SPR_label":False,"critical_for_new_uniform_signal_threshold_reclassification":True},
 {"field":"independent_biological_replicate_n","value":"unknown","critical_for_conditioned_author_SPR_label":False,"critical_for_precision_reproducibility_estimation":True},
 {"field":"free_solution_oligomeric_state","value":"unknown_except_BetV1_b2_dimer","critical_for_conditioned_author_SPR_label":False,"critical_for_monomer_KD_interpretation":True}]
 entries=[]
 with zipfile.ZipFile(ZIP) as archive:
  assert archive.testzip() is None
  for base in chosen:
   pr=primary[base["source_csv_row"]-2]
   assert pr["DesignName"]==base["source_id"] and pr["Target"]==base["target"] and pr["Sequence"]==base["sequence"] and int(pr["Binding"])==base["binary_binding_label"]
   ap=Path(base["author_model"]["path"]);assert digest(ap)==base["author_model"]["sha256"] and archive.read(base["archive_member"])==ap.read_bytes()
   chains,context=read_structure(ap);seqs={c["id"]:c["sequence"] for c in chains}
   assert not context and len(chains)==2 and seqs[base["author_binder_chain"]]==base["sequence"] and seqs[base["author_target_chain"]]==base["target_sequence"]
   exact=base["target"]=="BBF-14";label=int(pr["Binding"]);name=base["source_id"]
   special=name in ("BBF_b4","BetV1_b2")
   valency={"free_solution_state":"dimer_measured_SEC_MALS" if name=="BetV1_b2" else "unknown","bound_complex_stoichiometry":"1:1 supported" if special else "unknown","measurement_source":"Fig3f_ExtendedData4f" if name=="BetV1_b2" else "PDB9HAC" if name=="BBF_b4" else "not_reported_individually","Fc_fusion":"not described for these targets; PD1 Fc results do not apply"}
   binder_construct={"core_sequence":base["sequence"],"core_length":len(base["sequence"]),"core_sequence_sha256":seqhash(base["sequence"]),"full_SPR_expression_sequence":"unknown","tag_linker_exact":"unknown","vector_per_row":"unknown_pET21b_or_pET11","model_vs_publisher_sequence":"EXACT","valency":valency}
   if name=="BBF_b4":
    assert binder9==base["sequence"]+"GSHHHHH"
    binder_construct.update(deposited_crystal_expression_sequence=binder9,deposited_crystal_suffix="GSHHHHH",core_vs_crystal="EXACT_CONTIGUOUS_CORE",tag_interpretation="terminal purification extension; not grounds for automatic exclusion; same SPR batch identity not independently certified")
   row={
    "id":base["id"],"source_id":name,"target":base["target"],"source_csv_row":base["source_csv_row"],"source_doi":"10.1038/s41586-025-09429-6","source_row_sha256":hashlib.sha256(json.dumps(pr,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
    "sequence":base["sequence"],"sequence_sha256":base["sequence_sha256"],"target_sequence":base["target_sequence"],"target_sequence_sha256":base["target_sequence_sha256"],"binary_binding_label":label,"primary_affinity_nM_raw":pr["Affinity_nM"],"reported_KD_nM":float(pr["Affinity_nM"]) if pr["Affinity_nM"] else None,
    "primary_trace":{"table_source_ref":"primary_table","csv_row_including_header":base["source_csv_row"],"all_primary_fields":pr,"cohort_statement":"11purified/6detected_BBF14" if exact else "7tested/2detected_BetV1","row_raw_sensorgram":"ExtendedData3b" if name=="BBF_b4" else "Fig3e" if name=="BetV1_b2" else "unknown_not_publicly_row_resolved"},
    "author_design_model":rec(ap),"archive_member":base["archive_member"],"binder_expression_construct":binder_construct,"target_construct_profile":base["target"],"assay_profile":"BindCraft2025_author_SPR_screen","observed_endpoint":"SPR_binding_detected" if label else "SPR_binding_not_detected","assay_result_is_not_missing":True,
    "expression_QC":{"purified_cohort_reported":True,"per_candidate_numeric_purity_yield":"unknown","independent_fold_confirmation":"experimental_bound_crystal_core" if name=="BBF_b4" else "SEC_MALS_and_binding_characterization" if name=="BetV1_b2" else "unknown","source_refs":["article"]},
    "adjudication":{"status":"binding-qualified","condition":"ONLY_original_author_SPR_screen_endpoint","binding_endpoint_qualified":True,"eligible_for_conditioned_author_label_analysis":True,"main_analysis_eligible":exact,"main_analysis_endpoint":"author_conditioned_SPR_screen_with_experimental_target_core_support_and_terminal_tag_context","sensitivity_analysis_eligible":True,"sensitivity_only":not exact,"analysis_assignment":"MAIN_CONDITIONED_SCREEN" if exact else "SENSITIVITY_ONLY_ASSAY_TARGET_VARIANT_UNRESOLVED","full_assayed_construct_sequence_certified":False,"exact_model_vs_assay_target_construct":"TERMINAL_TAG_EXPLAINED_EXPERIMENTAL_TARGET_CORE_SUPPORTED" if exact else "UNRESOLVED_ASSAY_F63_OR_L63","eligible_for_exact_target_construct_calibration":exact,"eligible_for_standardized_monomer_affinity_benchmark":False,"eligible_for_blockade_benchmark":False,"reason":"原表逐条测量标签、核心序列及作者模型一致，统一SPR方法/对照可追溯；仅资格化原实验条件检出端点，未据未知tag排除。"+("BBF实验目标核心与模型完全匹配，末端标签单列。" if exact else "BetV1模型F63L为已注释天然变体；实际SPR目标等位序列未公开，严格构建匹配待定。")},
    "unknowns_profile":"shared_unknowns","additional_unknowns":[{"field":"assayed_target_F63_L63_identity","value":"unknown","critical_for_conditioned_named_target_author_label":False,"critical_for_exact_target_construct_calibration":True}] if not exact else [],
    "secondary_evidence":{"affinity_interpretation":"published_condition_specific_KD_not_new_measurement" if special else "not_measured_or_not_reported_not_zero","blockade_status":"PARTIAL_IGE_BINDING_INHIBITION_REPORTED_SPECIFIC_ASSAY" if name=="BetV1_b2" else "NOT_TESTED_OR_NOT_REPORTED","blockade_generalization":False}}
   if name=="BetV1_b2":
    row["secondary_evidence"]["specific_functional_assay"]={"partner":"heterogeneous patient anti_BetV1_IgE","endpoint":"reduced captured_IgE binding of biotinylated BetV1","donors":3,"technical_replicates_per_main_figure":2,"replicate_caveat":"ReportingSummary calls ELISA single replicates; independent repetition n unknown","target_nM":1,"binder_start_uM":2,"binder_serial_dilution_factor":4,"observed_scope":"partial reduction up to approximately50percent in2of3donors","assay_variant_identity":"unknown","not_general_PPI_blockade_label":True,"source_refs":["article","reporting"]}
   entries.append(row)
 assert len(entries)==18 and sum(x["binary_binding_label"] for x in entries)==8
 assert len({x["id"] for x in entries})==18
 result={"schema_version":1,"status":"BINDCRAFT18_ENDPOINT_ADJUDICATION_COMPLETE","created_utc":datetime.now(timezone.utc).isoformat(),"slurm_job_id":os.environ["SLURM_JOB_ID"],"qualification_standard":"traceable_original_assay+exact_binder_core_identity+interpretable_conditioned_endpoint+explicit_construct_adaptation","scope":{"frozen_n":18,"included_n":18,"positive_labels":8,"negative_labels":10,"qual_status_counts":{"binding-qualified":18,"unresolved":0,"excluded":0},"separate_exact_target_construct_counts":{"supported_terminal_tag_context":11,"unresolved_assay_F63_L63":7},"main_analysis_eligible":11,"main_analysis_positive_labels":6,"main_analysis_negative_labels":5,"sensitivity_only":7,"sensitivity_only_positive_labels":2,"sensitivity_only_negative_labels":5,"expanded_sensitivity_n":18,"strict_monomer_KD_calibration_eligible":0,"blockade_benchmark_eligible":0,"published_selected_KD_values":2,"single_secondary_partial_IgE_inhibition_assay":1},"endpoint_definition":assay,"target_profiles":target_profiles,"shared_unknowns":unknowns,"sources":sources,"entries":entries,"outside_scope_unlabelled_rows":missing,"base_tables_or_registry_modified":False,"new_predictions_started":False,"no_inference":"qualification is source adjudication, not newly performed binding or blockade"}
 dump(O/"qualification_overlay.json",result)
 fields=["id","source_id","target","source_csv_row","binary_binding_label","status","conditioned_SPR_eligible","main_analysis_eligible","sensitivity_only","analysis_assignment","exact_target_construct_eligible","target_construct_status","reported_KD_nM","blockade_benchmark_eligible","sequence_sha256","target_sequence_sha256"]
 with (O/"qualification_summary.tsv").open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter="\t");w.writeheader()
  for x in entries:w.writerow({"id":x["id"],"source_id":x["source_id"],"target":x["target"],"source_csv_row":x["source_csv_row"],"binary_binding_label":x["binary_binding_label"],"status":x["adjudication"]["status"],"conditioned_SPR_eligible":True,"main_analysis_eligible":x["adjudication"]["main_analysis_eligible"],"sensitivity_only":x["adjudication"]["sensitivity_only"],"analysis_assignment":x["adjudication"]["analysis_assignment"],"exact_target_construct_eligible":x["adjudication"]["eligible_for_exact_target_construct_calibration"],"target_construct_status":x["adjudication"]["exact_model_vs_assay_target_construct"],"reported_KD_nM":x["reported_KD_nM"],"blockade_benchmark_eligible":False,"sequence_sha256":x["sequence_sha256"],"target_sequence_sha256":x["target_sequence_sha256"]})
 lines=["# BindCraft 18条对照：原始实验资格裁决","",
 "**18/18可作为作者原条件SPR检出/未检出端点：8检出、10未检出。** 这并不等于18条均有标准化单体结合真值。精确目标构建层面，BBF-14的11条有实验目标核心支持；Bet v1的7条实际实验F63/L63身份仍未明。所有18条均保留；没有据未知标签或寡聚状态自动排除。","",
 "主校准分析固定为BBF-14的11条（6检出/5未检出），端点限定为允许可解释末端标签、且有实验目标核心支持的作者条件SPR筛选。BetV1的7条（2检出/5未检出）不进入严格构建主分析，完整保留在预设扩展敏感性分析（合计18条）。这一分配只依据来源/构建资格，未按模型得分或表现选择。main_analysis_eligible不表示完整实验构建逐批认证，也不表示标准化单体KD资格。","", "## 已核对的原始依据","",
 "[Nature论文](https://www.nature.com/articles/s41586-025-09429-6)的Methods明确采用纯化蛋白SPR，初筛10µM，靶标固定于CM5芯片；原表Binding=1/0按检出/未检出解释。[Reporting Summary](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-025-09429-6/MediaObjects/41586_2025_9429_MOESM2_ESM.pdf)第2页注明独立通道阴性对照，但没有逐设计独立重复次数。具体缓冲液、流速、表达/纯化和未知项见overlay assay profile。","",
 "出版商MOESM4逐行、作者Zenodo模型双链及SHA-256完全复核。原有集合仅包含11条BBF-14和7条BetV1；BBF_b1/b9/b14的标签为空，在集合外单列，绝不转成阴性。[SI](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-025-09429-6/MediaObjects/41586_2025_9429_MOESM1_ESM.pdf)表1与作者模型提供设计目标上下文，不能替代实验表达构建证明。","",
 "## 构建与端点的具体裁决","",
 "[PDB9HAC](https://www.rcsb.org/structure/9HAC)确认BBF_b4核心序列及1:1结合构型。沉积binder为核心+GSHHHHH；target为M+111aa核心+GSGWHHHHHH。末端标签可解释，所以不据此否定结合检测；其他binder的完整表达序列、每批纯度及游离寡聚态仍unknown。","",
 "BetV1模型159aa相对[P15494](https://www.uniprot.org/uniprotkb/P15494/entry)及论文引用[7MXL](https://www.rcsb.org/structure/7MXL)去起始M后还有F63L（模型位置62），UniProt明确注释为天然变体。它不应擅自改回F，也不能据同名靶标声称SPR构建精确匹配；实际用F或L的实验样本序列仍unknown。","",
 "BBF_b4与BetV1_b2分别有作者20.9/120nM记录。后者游离二聚、结合复合物支持1:1，因此不能把120nM解释成统一裸单体亲和力。BetV1_b2还存在特定血清IgE结合抑制实验，作为独立次级证据保存；不能将其推广到其余17条或任意二蛋白的阻断标签。","",
 "## 逐条结果","",
 "|ID|源CSV行|原结合标签|原KD nM|条件SPR资格|精确目标构建|",
 "|---|---:|---:|---:|---|---|"]
 for x in entries:lines.append(f"|{x['source_id']}|{x['source_csv_row']}|{x['binary_binding_label']}|{x['reported_KD_nM'] if x['reported_KD_nM'] is not None else '未报告'}|binding-qualified|{'核心相同，末端标签单列' if x['target']=='BBF-14' else 'F63L实验身份待定'}|")
 lines.extend(["","## 未知项如何限制资格","",
 "原始每条sensorgram、统一RU阈值/检测限、逐条浓度误差、纯度/溶解度/折叠QC、完整表达标签与独立生物学重复数未完整公开。它们不阻断复述作者已测出的条件标签，但阻断将阴性解释为固有不结合、重定义统一阈值、估算独立实验不确定性或作标准化单体KD校准。存在KD空值不代表KD=0。","",
 "严格构建分析必须单列BetV1变体不确定性；可按已冻结方案进行包含/排除该目标的敏感性分析，不能看计算表现后选择。18条标签同出一篇论文且经作者计算过滤，不是随机设计总体，也不是独立于AF2选择的泛化证明。","",
 "本文件不修改原78表、历史标签或主registry。具体全长核心序列、每个源行所有字段、作者结构路径/哈希、逐项unknown的关键性、来源快照与裁决在qualification_overlay.json；扁平表在qualification_summary.tsv。",""])
 (O/"REPORT.md").write_text("\n".join(lines))
 dump(O/"source_receipts.json",sources)
 script=Path(__file__).resolve()
 inventory=[rec(p) for folder in (O,I,S) for p in sorted(folder.rglob("*")) if p.is_file()]
 manifest={"schema_version":1,"status":"QUALIFICATION_COMPLETE","root":str(R),"scope":"BindCraft18_only","slurm_job_id":os.environ["SLURM_JOB_ID"],"created_utc":datetime.now(timezone.utc).isoformat(),"source_script":rec(script),"source_git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=R/"source",text=True).strip(),"inputs":[rec(BASE),rec(CSV),rec(ZIP)],"outputs":{n:rec(O/n) for n in ("qualification_overlay.json","qualification_summary.tsv","REPORT.md","source_receipts.json","reporting_summary_review.json","target_construct_comparison.json")},"file_inventory":inventory,"counts":result["scope"],"modifies_base_registry":False,"new_model_predictions":0}
 dump(D/"manifest.json",manifest)
 print(json.dumps({"manifest":str(D/"manifest.json"),"counts":result["scope"]},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
