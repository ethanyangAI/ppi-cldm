#!/usr/bin/env python3
"""Primary-source qualification of the frozen original60 RFdiffusion controls."""
import argparse,datetime,hashlib,json,os,re,sys,time
from pathlib import Path
import requests
R=Path("/lustre/users/u21111210118/projects/test9")
S=R/"steps/14_control_qualification/rfd60"
def receipt(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def atomic(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+".partial");t.write_text(json.dumps(x,indent=2,allow_nan=False)+"\n");t.replace(p)
def check(r):
 actual=receipt(r["path"]);assert actual["sha256"]==r["sha256"] and actual["bytes"]==r["bytes"],r["path"]
def jobrun(phase):
 assert os.environ.get("SLURM_JOB_ID"),"Slurm required"
 name=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"_"+os.environ["SLURM_JOB_ID"]+"_"+phase
 p=S/"runs"/name;p.mkdir(parents=True,exist_ok=False);return p
def inventory():
 run=jobrun("inventory");authority=R/"00_admin/reconstruction_20261002.json";a=json.loads(authority.read_text())
 assert a["authority"]=="u21111210118@192.168.81.6:22560:"+str(R)
 keys=["controls_manifest","controls_independent","author_models","author_models_independent","controls_qualification_audit"]
 for k in keys:check(a["evidence"][k])
 old=R/"steps/02_controls_recovery/runs/20261002T113406Z_11698/outputs/local_control_candidates.json"
 assert receipt(old)["sha256"]=="a2991f204d8d2abfd01c9db0b985b844f0fe7127a7efdca57068d47cfa0c9086"
 entries=json.loads(old.read_text())["entries"];assert len(entries)==60
 overlay=[dict(id="ctrl_"+hashlib.sha256(e["binder_id"].encode()).hexdigest()[:12],source_id=e["binder_id"],target=e["target_id"],frozen_curated_label=e["binder"],sequence=e["A_seq"],target_sequence=e["B_seq"],sequence_sha256=hashlib.sha256(e["A_seq"].encode()).hexdigest(),target_sequence_sha256=hashlib.sha256(e["B_seq"].encode()).hexdigest()) for e in entries]
 atomic(S/"inputs/frozen60_identity_inventory.json",dict(status="FROZEN60_IDENTITIES_AND_PRIOR_EVIDENCE_HASH_VERIFIED",entries=overlay))
 out=dict(status="FROZEN60_IDENTITIES_AND_PRIOR_EVIDENCE_HASH_VERIFIED",job=os.environ["SLURM_JOB_ID"],authority=receipt(authority),verified=[a["evidence"][k] for k in keys],original60=receipt(old),inventory=receipt(S/"inputs/frozen60_identity_inventory.json"))
 atomic(run/"manifest.json",out);print(out["status"],run/"manifest.json")
 for e in overlay:print(e["target"],e["source_id"],e["frozen_curated_label"])
def fetch(spec_path):
 run=jobrun("fetch");spec=json.loads(Path(spec_path).read_text());results=[]
 for item in spec:
  dest=S/"raw"/item["name"];dest.parent.mkdir(parents=True,exist_ok=True)
  result=dict(request=item,started=time.time(),attempts=[])
  if dest.exists():
   result.update(status="EXISTS_NO_OVERWRITE",file=receipt(dest));results.append(result);continue
  for attempt in range(2):
   tmp=dest.with_name(dest.name+".partial")
   try:
    response=requests.request(item.get("method","GET"),item["url"],json=item.get("json"),timeout=(20,120),stream=True,headers={"User-Agent":"Research-data-recovery/1.0"})
    details=dict(status_code=response.status_code,url=response.url,content_type=response.headers.get("Content-Type"),headers={k:response.headers[k] for k in ("Content-Length","ETag","Last-Modified") if k in response.headers})
    total=0
    with tmp.open("wb") as f:
     for block in response.iter_content(1<<20):
      total+=len(block)
      if total>item.get("max_bytes",100000000):raise RuntimeError("Download size cap reached")
      f.write(block)
    if response.status_code==200 and total>0:
     tmp.replace(dest);result.update(status="DOWNLOADED",file=receipt(dest));details["file"]=result["file"];result["attempts"].append(details)
     break
    failure=run/(item["name"].replace("/","_")+".http_error_body");tmp.replace(failure);details["error_body"]=receipt(failure);result["attempts"].append(details)
    if response.status_code<500:break
   except Exception as e:
    result["attempts"].append(dict(error=repr(e)))
    if tmp.exists():tmp.unlink()
   if attempt==0:time.sleep(2)
  result.setdefault("status","UNAVAILABLE");results.append(result)
  print(item["name"],result["status"],result.get("file",{}).get("bytes"),flush=True)
 atomic(run/"fetch_manifest.json",dict(status="PRIMARY_SOURCE_FETCH_ATTEMPTS_RECORDED",job=os.environ["SLURM_JOB_ID"],spec=receipt(spec_path),requests=results))
 print("FETCH_MANIFEST",run/"fetch_manifest.json")

def qualify():
 import collections,csv,io,zipfile
 run=jobrun("qualification_v1_1")
 old=R/"steps/02_controls_recovery/runs/20261002T113406Z_11698/outputs/local_control_candidates.json"
 assert receipt(old)["sha256"]=="a2991f204d8d2abfd01c9db0b985b844f0fe7127a7efdca57068d47cfa0c9086"
 cp=S/"inputs/primary_identity_crosswalk60.json"
 assert receipt(cp)["sha256"]=="115ecb69fed9503028ec0433574f886945168dd2a07944564c594fc00a15e09f"
 cross=json.loads(cp.read_text());archive=S/"raw/RFdiffusion_designs.zip"
 assert receipt(archive)["sha256"]==cross["archive_sha256"]
 z=zipfile.ZipFile(archive);entries=cross["entries"];assert len(entries)==60
 paper_url="https://www.nature.com/articles/s41586-023-06415-8"
 supplement_url="https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-023-06415-8/MediaObjects/41586_2023_6415_MOESM1_ESM.pdf"
 archive_url="https://ndownloader.figshare.com/files/40226533"
 sources={
  "author_archive":dict(receipt(archive),doi="10.6084/m9.figshare.22662094",url=archive_url,title="Extended Data 2 from Broadly applicable protein design with RoseTTAFold Diffusion",role="Primary author experimental labels and model sequences"),
  "main_paper":dict(receipt(S/"raw/nature_main.pdf"),doi="10.1038/s41586-023-06415-8",url=paper_url),
  "supplement":dict(receipt(S/"raw/nature_supplement_media.pdf"),doi="10.1038/s41586-023-06415-8",url=supplement_url),
  "reporting":dict(receipt(S/"raw/nature_reporting.pdf"),doi="10.1038/s41586-023-06415-8",role="Generic reporting summary; does not establish per-design replicate counts"),
  "identity_crosswalk":receipt(cp),
  "frozen_original60":receipt(old)
 }
 for name in ("nature_article.html","pmc_article.html","datacite_paper_related.json","alphaproteo_paper.html"):
  p=S/"raw"/name
  if p.exists():sources[name]=receipt(p)
 def ref(key,**loc):
  return dict(source_key=key,source_sha256=sources[key]["sha256"],**loc)
 def field(value,refs,status="reported",**extra):
  return dict(value=value,status=status,provenance=refs,**extra)
 methods=[ref("supplement",pdf_pages=[109,110],printed_pages=[108,109],section="6.8")]
 tags=[ref("supplement",pdf_pages=[102],printed_pages=[101],section="6.1")]
 purification=[ref("supplement",pdf_pages=[102,103],printed_pages=[101,102],section="6.2")]
 protocol=dict(
  assay=field("Single-point biolayer interferometry",methods),
  instrument=field("Octet Red96 (ForteBio)",methods),
  immobilization=field("Biotinylated target on streptavidin tips (Sartorius 18-5019)",methods),
  target_loading=field(dict(concentration_nM=40,duration_s=300,post_loading_baseline_s=60),methods),
  screen_cycles=field(dict(baseline_s=120,association_s=120,dissociation_s=120),methods),
  buffer=field("HBS-EP+ with 0.1% w/v BSA",methods),
  blank_control=field("Each design tested against unloaded tips; paired unloaded-tip baseline response subtracted",methods),
  endpoint=field("Mean response over 105-115 s of association; author binary hit call",methods),
  binder_construct=field("Core design with N-terminal three-residue expression prefix and C-terminal SNAC cleavage and 6xHis affinity tags in LM0627",tags),
  tag_cleavage_before_assay=field(None,tags+purification,"unknown",reason="Construct encoding is documented; actual tag cleavage for each of these BLI screen samples is not documented"),
  binder_expression=field("BL21(DE3), auto-induction; Ni-NTA purification followed by SEC",purification),
  sec_column=field("Superdex75 Increase 5/150 GL (Cytiva 29148722)",purification),
  target_assay_full_construct_sequence=field(None,methods,"unknown",reason="Target identity and biotinylation are reported; per-target full assayed construct sequence, tags and exact boundaries not recovered"),
  target_assay_valency=field(None,methods,"unknown",reason="Surface immobilization is known; molecular oligomerization and fusion valency not established per target"),
  per_design_replicates=field(None,[ref("reporting",pdf_pages=[2],section="Study design / Replication")],"unknown",reason="Generic statement of independent measurements is not a per-design BLI replicate count"),
  biological_blockade=field(None,methods,"not_tested_by_this_endpoint",reason="BLI binding screen is not native-partner competition or functional inhibition"),
  detection_limit=field(None,methods,"unknown",reason="Relative hit threshold is not an absolute instrument detection limit")
 )
 criteria=dict(version="rfd60-primary-qualification-1.1",denominator=60,
  basis="2026-09-28 frozen contract: primary measured label, exact sequence identity, interpretable assay endpoint, relevant construct",
  decisions=[
   "Identity requires exact CSV AF2 ID, author PDB member under the same experimentally_tested target directory, and full binder and target core sequence matches to the frozen input.",
   "An author Binder=True with exact identity is an assay-qualified binding positive for the published tagged surface-BLI construct. Nonmonomeric samples retain that measured positive endpoint but cannot establish monomer affinity.",
   "An author Binder=False with Monomeric=True is a conditional negative for the published relative-hit screen, not a universal nonbinder. Missing actual per-design concentration is a substantive uncertainty flag.",
   "Binder=False with Monomeric=False is unresolved for monomeric binding interpretation because the negative is confounded by sample oligomeric quality. Its measured author screen_non_hit label is retained.",
   "No binary hit threshold is recalculated. Unknown replicates, exact target tags, and raw sensorgrams remain unknown rather than fabricating fields or deleting all primary evidence.",
   "These source- and assay-specific labels do not establish blockade or independent generalization. No performance benchmark or threshold optimization is performed."
  ],
  eligibility_definitions={
   "source_matched_bli_screen":"qualified positive or monomeric conditional screen negative; per-record dose and oligomer caveats mandatory",
   "monomeric_bli_screen":"source_matched_bli_screen and author Monomeric=True",
   "main_analysis":"Monomeric author BLI positive, or monomeric MDM2 conditional non-hit at the paper-reported 10 uM protocol; original tagged binding assay only, not tag-free affinity or blockade",
   "conservative_monomer_binding_subset":"same membership as explicit main_analysis; 15 positives and 6 MDM2 conditional negatives",
   "fixed_actual_10uM_negative":"requires per-ID measured concentration; unavailable for all selected negatives; do not silently equate nominal with measured",
   "blockade":"requires native-partner competition or functional blockade; absent from these author CSV labels"
  })
 out=[]
 for e in entries:
  csvdata=z.read(e["csv_member"]);assert hashlib.sha256(csvdata).hexdigest()==e["csv_sha256"]
  rows=list(csv.DictReader(io.StringIO(csvdata.decode())))
  row=rows[e["csv_line"]-2]
  assert row==e["original_csv_row"] and row["AF2_prediction"]==e["source_id"]
  assert e["both_chain_sequences_exact"] and row["Binder"]==e["frozen_curated_label"]
  assert hashlib.sha256(z.read(e["primary_pdb_member"])).hexdigest()==e["primary_pdb_sha256"]
  assert hashlib.sha256(z.read(e["fasta_member"])).hexdigest()==e["fasta_sha256"]
  positive=row["Binder"]=="True";mono=row["Monomeric"]=="True";mdm=e["target"]=="Mdm2"
  decision="ASSAY_QUALIFIED_BINDING_POSITIVE" if positive else ("CONDITIONAL_SCREEN_NEGATIVE" if mono else "UNRESOLVED_QC_CONFOUNDED_NONHIT")
  csvref=ref("author_archive",member=e["csv_member"],member_sha256=e["csv_sha256"],line_1_based=e["csv_line"],columns=["RFdiffusion_output","AF2_prediction","Binder","Monomeric"])
  pdbref=ref("author_archive",member=e["primary_pdb_member"],member_sha256=e["primary_pdb_sha256"],binder_chain=e["primary_binder_chain"],target_chain=e["primary_target_chain"])
  fastaref=ref("author_archive",member=e["fasta_member"],member_sha256=e["fasta_sha256"],matching_entries=e["fasta_sequence_matches"])
  paperrefs=[ref("main_paper",pdf_pages=[7,8],figure="4d/e")] if mdm else [ref("main_paper",pdf_pages=[9,10,27],figure="6 and Extended Data 8g")]
  flags=["FULL_ASSAY_TARGET_CONSTRUCT_AND_VALENCY_UNKNOWN","PER_DESIGN_REPLICATES_UNKNOWN","RAW_SENSORGRAMS_AND_NUMERIC_RESPONSE_NOT_AVAILABLE"]
  if not mono:flags+=["AUTHOR_SEC_NONMONOMERIC","NO_MONOMER_SPECIFIC_AFFINITY_INTERPRETATION"]
  if not mdm:flags+=["ACTUAL_SCREEN_DOSE_UNKNOWN_AND_LOW_DOSE_FALSE_NEGATIVES_DOCUMENTED"]
  if not e["fasta_exact_header_match"]:flags+=["AUTHOR_IL7RA_FASTA_HEADER_MISLABEL_RESOLVED_VIA_EXPLICIT_PDB_ID"]
  if mdm:flags+=["MDM2_MAIN_CAPTION_95_VS_CSV_AND_TEXT_96_DENOMINATOR_DISCREPANCY","MDM2_CAPTION_MAX_RESPONSE_VS_GENERIC_CONTROL_THRESHOLD_WORDING"]
  dose=field(dict(nominal_binder_uM=10,actual_binder_uM=None,actual_per_id_verified=False,reported_low_dose_exceptions=(not mdm)),paperrefs,"nominal_protocol_only",reason=("Paper describes MDM2 screen at 10 uM; no per-ID measured concentration table" if mdm else "Article explicitly allows lower-than-10 uM samples, but CSV does not map dose to design IDs"))
  threshold=field(("Author Binder call retained; Fig.4e describes >50% maximum response, while generic BLI methods use >50% positive control" if mdm else "Author Binder call retained; methods use >50% positive-control response and main/Extended Data captions use >=50%; no boundary reclassification"),paperrefs+methods)
  reason=("Original author BLI hit, exact core identity and relevant target; scope is the published tagged/surface assay" if positive else ("Original author BLI non-hit with SEC monomer status; only a conditional screen negative under its nominal assay protocol" if mono else "Original author BLI non-hit but SEC not monomeric; poor sample state confounds monomer binding interpretation"))
  if positive and not mono:reason+="; observed binding does not establish a monomeric interaction because SEC was nonmonomeric"
  if not positive and not mdm:reason+="; actual concentration unavailable, and authors warn of low-dose false negatives"
  ent=dict(id=e["id"],source_id=e["source_id"],target=e["target"],original_design_id=row["RFdiffusion_output"],
   frozen_curated_label=e["frozen_curated_label"],primary_label_concordance=True,
   identity=dict(status="PRIMARY_AUTHOR_CSV_AND_PDB_BOTH_CORE_CHAINS_EXACT",binder_sequence_sha256=e["binder_sequence_sha256"],target_sequence_sha256=e["target_sequence_sha256"],primary_pdb_bytes_equal_prior=e["primary_pdb_bytes_equal_prior"],fasta_header_exact=e["fasta_exact_header_match"],provenance=[csvref,pdbref,fastaref],scope="Both modeled core chains exact; full experimentally assayed target boundaries and tags not fully recoverable"),
   author_binding_label=field(positive,[csvref]),author_monomeric=field(mono,[csvref]+purification),
   source_endpoint=field("BLI_hit" if positive else "BLI_screen_non_hit",[csvref]+methods),
   nominal_and_actual_concentration=dose,positive_definition=threshold,
   continuous_response=field(None,[csvref]+methods,"unknown",reason="Primary CSV contains binary label, not per-ID response or sensorgrams"),
   per_id_expression_yield=field(None,[csvref]+purification,"unknown",reason="Expression/purification and SEC screen reported, but no per-ID numerical yield table in the released archive"),
   per_id_kd=field(0.7 if e["source_id"]=="p53_AF2_89" else None,[ref("main_paper",pdf_pages=[7],figure="4d")] if e["source_id"]=="p53_AF2_89" else [csvref],"reported" if e["source_id"]=="p53_AF2_89" else "unknown",units="nM",reason="Selected p53 design 89 explicitly labeled in Fig.4d" if e["source_id"]=="p53_AF2_89" else "No per-ID KD assigned from unlabeled or ambiguous plots"),
   assay_protocol_key="watson_bli_screen",
   qualification=dict(classification=decision,reason=reason,eligible_main_analysis=(mono and (positive or mdm)),main_analysis_endpoint="AUTHOR_TAGGED_SEC_MONOMERIC_BLI_HIT_VS_MDM2_NOMINAL_10UM_NONHIT",main_analysis_label=(1 if positive else 0) if (mono and (positive or mdm)) else None,main_analysis_exclusion_reason=(None if (mono and (positive or mdm)) else ("NONMONOMERIC_CONSTRUCT_QC" if not mono else "ACTUAL_DOSE_UNKNOWN_WITH_DOCUMENTED_LOW_DOSE_EXCEPTIONS")),eligible_dose_uncertain_monomer_sensitivity=(mono and not positive and not mdm),eligible_source_matched_bli_screen=(positive or mono),eligible_monomeric_bli_screen=mono,eligible_conservative_monomer_binding_subset=(mono and (positive or mdm)),eligible_fixed_actual_10uM_negative=False,eligible_blockade=False,eligible_independent_test=False,flags=flags,criteria_version=criteria["version"]))
  out.append(ent)
 counts=collections.Counter(e["qualification"]["classification"] for e in out)
 bytarget={}
 for t in sorted({e["target"] for e in out}):
  sub=[e for e in out if e["target"]==t]
  bytarget[t]=dict(n=len(sub),classifications=dict(collections.Counter(e["qualification"]["classification"] for e in sub)),monomeric_positives=sum(e["author_binding_label"]["value"] and e["author_monomeric"]["value"] for e in sub),monomeric_nonhits=sum(not e["author_binding_label"]["value"] and e["author_monomeric"]["value"] for e in sub))
 summary=dict(status="ALL60_PRIMARY_ASSAY_RECORDS_ADJUDICATED_WITH_EXPLICIT_CONTEXT_LIMITS",criteria_version=criteria["version"],job=os.environ["SLURM_JOB_ID"],n_input=60,n_identity_exact=60,n_original_primary_label_concordant=60,n_fasta_content_exact=60,n_fasta_header_anomaly=20,n_primary_pdb_byte_identical_to_curated=0,classifications=dict(counts),by_target=bytarget,
  n_positive_nonmonomeric=sum(e["author_binding_label"]["value"] and not e["author_monomeric"]["value"] for e in out),
  n_source_matched_bli_screen=sum(e["qualification"]["eligible_source_matched_bli_screen"] for e in out),
  n_monomeric_bli_screen=sum(e["qualification"]["eligible_monomeric_bli_screen"] for e in out),
  n_main_analysis=21,n_main_positive=15,n_main_conditional_negative=6,n_main_excluded=39,n_sensitivity_only_dose_uncertain_negative=13,n_source_endpoint_only_nonmonomeric_positive=15,
  n_conservative_monomer_binding_subset=sum(e["qualification"]["eligible_conservative_monomer_binding_subset"] for e in out),
  n_conditional_negatives_actual_dose_uncertain=19,n_conditional_negatives_with_documented_low_dose_exception_scope=13,
  n_actual_per_id_concentration_verified=0,n_full_assay_target_construct_verified=0,n_per_id_replicates_verified=0,n_blockade_qualified=0,
  source_doi="10.6084/m9.figshare.22662094",paper_doi="10.1038/s41586-023-06415-8",
  unresolved_ids=[e["source_id"] for e in out if e["qualification"]["classification"].startswith("UNRESOLVED")],
  missing_items=["Per-ID actual assay concentration and normalized response/sensorgrams","Exact assayed target boundaries, fusion tags, oligomeric valency and tag cleavage status","Per-ID replicates, numeric yield and assay QC traces","Native-partner blockade outcomes for these specific labels"],
  next_steps=["Request original sensorgram export and concentration/sample ledger, prioritizing 13 IL7Ra/PDL1 monomeric non-hits","Request full target construct/vendor records and exact fusion/biotinylation context","Resolve or repeat 11 nonmonomeric non-hits with monomeric purified material before treating as binding negatives","Retain this 60-input identity denominator; integrate the separate 18-control audit without merging binding and blockade labels"],
  warnings=["All labels are retrospective author-screen evidence, not independent model validation","Main analysis: MDM2 5 positive / 6 conditional negative; IL7Ra 7 positive / 0 negative; Pdl1 3 positive / 0 negative. With only this source, every family holdout lacks a class in training or test; report undefined calibration metrics explicitly","15 measured positives are nonmonomeric; assay positivity cannot be converted to monomer KD","49 source-matched screen labels are not 49 universal or blockade labels","Original tables, thresholds, and registry remain unchanged"])
 output=run/"outputs";output.mkdir()
 atomic(output/"qualification_overlay60.json",dict(schema_version=1,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),criteria=criteria,sources=sources,protocols={"watson_bli_screen":protocol},entries=out))
 atomic(output/"qualification_summary.json",summary)
 # All inspected metadata in the three relevant experimental folders; the archive contains no raw sensorgrams.
 meta=[n for n in z.namelist() if not n.endswith("/") and not n.endswith(".pdb")]
 relevant=[n for n in meta if any("/"+folder+"/" in n for folder in ["Mdm2_binders","IL7Ra_binders","Pdl1_binders"])]
 atomic(output/"source_coverage.json",dict(archive=sources["author_archive"],n_members=len(z.namelist()),all_non_pdb_members=meta,relevant_non_pdb_members=relevant,primary_csv_rows={"Mdm2":96,"IL7Ra":95,"Pdl1":95},n_selected=60,all_selected_processed=True,not_found=["per-ID concentrations","raw BLI sensorgrams","replicate counts","full target assay constructs"],scope="Entire official ZIP metadata inventory and primary article, supplement and reporting summary; unavailable fields remain unknown"))
 attempts=[]
 for p in sorted((S/"runs").glob("*_fetch/fetch_manifest.json")):
  m=json.loads(p.read_text())
  for a in m.get("requests",[]):
   attempts.append(dict(manifest=receipt(p),request=a["request"],status=a["status"],valid_nonempty_200=(a["status"]=="DOWNLOADED" and a.get("file",{}).get("bytes",0)>0 and any(t.get("status_code")==200 for t in a.get("attempts",[]))),attempts=a.get("attempts",[])))
 atomic(output/"retrieval_routes.json",dict(routes=attempts,official_success=archive_url,empty202_not_evidence=True))
 lines=["# 原始60条RFdiffusion对照：原作者实验标签逐条审计","",f"版本：{criteria['version']}。全部60条已完成审计；原目录不覆盖。","",
 "60/60输入与原作者CSV精确连接，旧标签60/60一致；原作者PDB的binder和target核心序列均与冻结输入精确一致。作者公开包DOI为10.6084/m9.figshare.22662094，论文DOI为10.1038/s41586-023-06415-8。","",
 "## 裁决","",
 "|靶标|输入|结合阳性|条件性筛选阴性|QC混杂未解决|单体阳性|","|---|---:|---:|---:|---:|---:|"]
 for t,v in bytarget.items():
  k=v["classifications"];lines.append(f"|{t}|{v['n']}|{k.get('ASSAY_QUALIFIED_BINDING_POSITIVE',0)}|{k.get('CONDITIONAL_SCREEN_NEGATIVE',0)}|{k.get('UNRESOLVED_QC_CONFOUNDED_NONHIT',0)}|{v['monomeric_positives']}|")
 lines += ["","共30条作者BLI阳性、19条单体条件性筛选阴性、11条非单体非命中仍无法用于单体结合阴性解释。30条阳性中15条作者SEC记录非单体：其在发表构建体条件下的实测结合成立，但不能作为单体亲和力证明。","",
 "49条可用于来源匹配的BLI筛选端点，其中34条作者SEC为单体；主分析资格明确为21条（15单体阳性、6条MDM2单体条件性阴性）。这些数字不是49条通用结合/阻断真值，也不是新独立验证集。主报告应同时保留完整60条目录和上述分层，不能只展示有利子集。15条非单体阳性退出严格主分析；13条剂量不明的单体非命中仅用于预先声明的敏感性；11条非单体非命中不作为结合阴性。以这60条单独进行家族留出时，每折的训练或测试缺少一类，必须把对应阈值/AUROC记为不可估计。","",
 "## 实验条件与解释","",
 "原实验为纯化表达样品的单点BLI，生物素化目标固定于链霉亲和素探针。方法记录40 nM目标加载300秒，基线/结合/解离各120秒，扣除对应空探针信号后读取结合末期105–115秒的平均值。作者用相对于阳性对照的响应阈值给出Binder标签，本次直接保留原始二值标签，未从图估计或重设阈值。","",
 "binder采用LM0627表达构建，包含N端表达前缀、C端SNAC和6xHis标签；在BL21(DE3)表达、Ni-NTA纯化并用SEC评估。目标全长实验构建边界、融合标签/价态及逐条剪切状态尚未恢复。因此资格范围限定于作者报告的带标签、固定目标的BLI端点；不外推为无标签单体或细胞环境的亲和力。","",
 "名义binder浓度为10 µM。IL7Ra/PDL1论文明确存在因材料不足而低浓度测试的样品，但没有逐ID实际浓度表；13条相关单体非命中仅能列为剂量不明的条件性筛选阴性。MDM2正文报告10 µM，本次亦仅记录论文协议浓度，不虚构逐样品测定浓度。所有60条的逐ID技术/生物重复数、原始传感曲线与数值化响应均未公开恢复。","",
 "## 来源异常与解决","",
 "IL7Ra目录的FASTA把条目标题写成Trka；20条所选核心内容均匹配，但不能依靠改名推断。本次以明确AF2编号的同目录作者PDB、CSV行以及两链精确一致建立独立连接；保留原FASTA异常。60条官方PDB文件与旧curated PDB均非字节一致，故只接受已核验的序列/身份一致性，不声称坐标原件相同。","",
 "MDM2图4标题写95个设计，正文和作者CSV为96；图4采用maximum response措辞，通用BLI方法使用positive control。原始标签来源没有矛盾，因此保持CSV二值标签，显式记录文字边界。所选p53_AF2_89在图4d有0.7 nM测量，但它的作者SEC标签非单体；不据此重写其他样品状态。","",
 "## 检索覆盖与尚缺材料","",
 "原Figshare分享链接及部分官方代理返回202空体或403，均保存尝试证据。通过DataCite关联到正式Springer Nature Figshare归档，经官方ndownloader下载251,665,498字节ZIP并校验。检查全部11,817成员、所有非PDB元数据、三个相关实验目录的CSV/FASTA，以及正文、补充方法和报告摘要；未找到逐ID浓度/传感曲线或完整实验目标构建清单。","",
 "下一步应取得作者原始BLI导出及浓度样品台账，优先处理13条剂量不明单体非命中；补全目标实验构建记录；对11条非单体非命中进行样品质控或单体条件复测。现有记录没有把这些未解决项变为阴性，也没有提供本项目候选的阻断实验证据。","",
 "## 逐条裁决","",
 "|来源ID|作者CSV行|原Binder|原Monomeric|裁决|","|---|---:|---|---|---|"]
 for e in out:
  cr=e["identity"]["provenance"][0];lines.append(f"|{e['source_id']}|{cr['line_1_based']}|{e['author_binding_label']['value']}|{e['author_monomeric']['value']}|{e['qualification']['classification']}|")
 lines += ["","每个字段的源文件SHA-256、ZIP成员与成员SHA、CSV行、PDF页和缺项理由在qualification_overlay60.json中；下载失败路径在retrieval_routes.json。禁止把本轮回顾性资格清理计为独立泛化验证。",""]
 (output/"原始60对照实验资格审计.md").write_text("\n".join(lines))
 outputs=[receipt(p) for p in sorted(output.iterdir())]
 manifest=dict(status="ALL60_PRIMARY_ASSAY_RECORDS_ADJUDICATED_WITH_EXPLICIT_CONTEXT_LIMITS",created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),job=os.environ["SLURM_JOB_ID"],source=receipt(Path(__file__)),inputs=[receipt(cp),receipt(old),receipt(archive),receipt(S/"raw/nature_main.pdf"),receipt(S/"raw/nature_supplement_media.pdf"),receipt(S/"raw/nature_reporting.pdf")],outputs=outputs,requires_independent_validation=True,supersedes_draft="20261003T031638Z_11901_qualification_v1; v1.1 adds explicit main-analysis eligibility without changing primary labels",original60_unchanged=(receipt(old)["sha256"]=="a2991f204d8d2abfd01c9db0b985b844f0fe7127a7efdca57068d47cfa0c9086"))
 atomic(run/"manifest.json",manifest)
 print(json.dumps(summary,indent=2));print("QUALIFICATION_MANIFEST",run/"manifest.json")

def main():
 p=argparse.ArgumentParser();p.add_argument("--phase",choices=["inventory","fetch","qualify"],required=True);p.add_argument("--spec");args=p.parse_args()
 if args.phase=="inventory":inventory()
 elif args.phase=="fetch":fetch(args.spec)
 elif args.phase=="qualify":qualify()
if __name__=="__main__":main()

