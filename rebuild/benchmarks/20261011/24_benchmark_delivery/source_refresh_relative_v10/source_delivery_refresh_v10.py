#!/usr/bin/env python3
"""Current source inclusion extension; byte-preserving, CPU only, never result promotion."""
import argparse,ast,collections,copy,hashlib,io,json,os,shutil,subprocess,tokenize,traceback
from pathlib import Path
from delivery_core import cpu,rec,dump,SECRET_RE
from delivery_graph_v2 import source_entries,graph_nodes,SUFFIXES
from provenance_aliases_v2 import ReceiptResolver
from native_resource_closure_v2 import historical_gap,recompute_dependency
from relative_receipt_policy import ExactRelativeContext
from historical_archive_member_context import ExactHistoricalArchiveMembers
R=Path("/lustre/users/u21111210118/projects/test9")
SOURCE_EXT={".py",".sh",".sbatch"}
TEXT_EXT=SOURCE_EXT|{".md",".json"}
EXTRA_NODES=[
 ("CURRENT_FORMAL64_IMPLEMENTATION","steps/22_matched_benchmark/code/formal_contract_v2/source",True,TEXT_EXT),
 ("CURRENT_RESOURCE54_IMPLEMENTATION","steps/22_matched_benchmark/code/resource_contract_v3/source",True,TEXT_EXT),
 ("CURRENT_FORMAL28_BEFORE_GENERATION","steps/22_matched_benchmark/formal_freeze_13257/plan",True,TEXT_EXT),
 ("CURRENT_SHARED_CPU3_POLICY","steps/22_matched_benchmark/formal_launchpolicy_13259",True,TEXT_EXT),
 ("CURRENT_FORMAL_ARRAY13260_SUBMISSION","steps/22_matched_benchmark/formal_submission_13260/submit_receipt.json",False,TEXT_EXT),
 ("CURRENT_POSTPROCESS37_IMPLEMENTATION","steps/24_benchmark_delivery/frozen/formal_postprocess_v2_13258/code",True,TEXT_EXT),
 ("CURRENT_SEEDED_SUPPLEMENTAL_ACTUAL_SOURCE","steps/21_method_runtime/frozen/supplemental_bindcraft_13239",True,TEXT_EXT),
 ("CURRENT_SEEDED_SUPPLEMENTAL_ACTUAL_LAUNCHER","steps/21_method_runtime/frozen/supplemental_launcher_13241",True,TEXT_EXT),
 ("CURRENT_SEEDED_SUPPLEMENTAL_ACTUAL_COLLECTOR","steps/21_method_runtime/frozen/supplemental_content_collector_13244",True,TEXT_EXT),
 ("CURRENT_ALL_ATTEMPT_NATIVE_COLLECTOR","steps/21_method_runtime/runs/native_collector_contracts_13166/source",True,TEXT_EXT),
 ("CURRENT_ACTUAL_RF_WORKFLOW_COLLECTOR","steps/21_method_runtime/frozen/native_workflow_collectors_13207",True,TEXT_EXT),
 ("CURRENT_BBF_SCIENTIFIC_REVIEW_CODE","steps/23_common_review/bbf_diagnostics/scientific_review/code",True,SOURCE_EXT|{".md"}),
 ("CURRENT_BBF_SCIENTIFIC_REVIEW_EXACT_SOURCEPACK","steps/23_common_review/bbf_diagnostics/scientific_review/runs/review_sourcepack_13237/resources",True,SOURCE_EXT|{".md"}),
 ("CURRENT_LITERATURE_REFRESH_20261012","reports/LITERATURE_REFRESH_20261012.md",False,{".md"}),
 ("CURRENT_HUMAN_WORKFLOW_CAPABILITY_AUDIT_20261012","reports/WORKFLOW_CAPABILITY_STATIC_AUDIT_20261012.md",False,{".md"}),
 ("CURRENT_WORKFLOW_ENTRY_DOCUMENT","source/docs/WORKFLOW.md",False,{".md"}),
 ("CURRENT_FORMAL_POSTPROCESS_DOCUMENT","steps/24_benchmark_delivery/code/formal_postprocess_HANDOFF_V2.md",False,{".md"}),
]
SEED_REL=[
 "steps/22_matched_benchmark/formal_freeze_13257/plan/freeze_receipt.json",
 "steps/22_matched_benchmark/code/formal_pre_generation_13259/acceptance.json",
 "steps/22_matched_benchmark/code/formal_contract_v2/manifest.json",
 "steps/22_matched_benchmark/code/resource_contract_v3/manifest.json",
 "steps/22_matched_benchmark/formal_launchpolicy_13259/freeze_receipt.json",
 "steps/22_matched_benchmark/formal_submission_13260/submit_receipt.json",
 "steps/24_benchmark_delivery/frozen/formal_postprocess_v2_13258/code/source_snapshot.json",
 "steps/24_benchmark_delivery/runs/formal_postprocess_contracts_13258/acceptance.json",
 "steps/24_benchmark_delivery/runs/formal_postprocess_inputcheck_13251/acceptance.json",
 "steps/21_method_runtime/runs/supplemental_actual_current_13247/outputs/acceptance.json",
 "steps/22_matched_benchmark/code/seeded_supplemental13246_audit_13254/acceptance.json",
 "steps/21_method_runtime/runs/native_runtime_handoff_13256/outputs/manifest.json",
 "steps/24_benchmark_delivery/runs/native74_final_v2_13211/native74/acceptance.json",
 "steps/24_benchmark_delivery/runs/native74_edge_seal_13214/acceptance.json",
 "steps/23_common_review/bbf_diagnostics/scientific_review/runs/review_sourcepack_13237/manifest.json",
]
INDEX_REL="steps/24_benchmark_delivery/runs/native74_final_v2_13211/native74/closure/resource_aliases.json"
POLICY_REL="steps/24_benchmark_delivery/frozen/native74_final_v2_13211/code/native_msa_history_policy.json"
BBF_PACK_REL="steps/23_common_review/bbf_diagnostics/scientific_review/runs/review_sourcepack_13237/manifest.json"
PRIOR_INCLUSION_REL="steps/24_benchmark_delivery/runs/handoff_13225/source_inclusion_v2.json"
def read(p):return json.loads(Path(p).read_text())
def receipt_edges(obj,trail=()):
 if isinstance(obj,dict):
  if {"path","sha256","bytes"}<=obj.keys() and isinstance(obj["path"],str):yield obj,trail
  for k,v in obj.items():yield from receipt_edges(v,trail+(str(k),))
 elif isinstance(obj,list):
  for i,v in enumerate(obj):yield from receipt_edges(v,trail+(str(i),))

METADATA_ONLY_SCHEMAS=frozenset({"exact-resource-aliases.v2","native-resource-closure.v2"})
def recognized_metadata_schema(obj):
 """Only exact existing string markers are metadata; ordinary JSON is operative."""
 marker=obj.get("schema")if isinstance(obj,dict)else None
 return type(marker)is str and marker in METADATA_ONLY_SCHEMAS
def operative_receipt_edges(obj,trail=()):
 if recognized_metadata_schema(obj):return
 yield from receipt_edges(obj,trail)

def exact(p,r):
 p=Path(p)
 if p.is_symlink() or not p.resolve().is_relative_to(R.resolve()):raise ValueError("Source receipt escapes authority")
 return p.is_file() and p.stat().st_size==r["bytes"] and rec(p)["sha256"]==r["sha256"]

LEGACY_ROOT="/work/home/lvying/lvying20260610/project-1/test9"
LEGACY_ANCHOR={"path":LEGACY_ROOT+"/steps/03_design/runs/20260922T113858Z_149ef033124f/manifest.json","bytes":12402,"sha256":"47bfbe1852aede63e479b88a1456a06aafc0797730453d003551091ff5251262"}
ANNOTATION_PARENT={"path":str(R/"01_raw/recovered_inputs/recovered_three_candidates.json"),"bytes":4665,"sha256":"04a73810c339e4594e8dc989e2c89aa3ba90542f89d5644c92f9df2b755c482c"}
RECOVERY_MARKER={"status":"EXACT_SEQUENCE_FROM_HISTORICAL_OUTPUT_STRUCTURES_NOT_RECOVERED","source_session_id":"01a0bdc5-988d-70c1-8346-f463d4989fa2","record_number":7006,"corroborating_record_number":6378,"missing_files":"native, backbone, design_manifest paths are historical provenance, not currently restored files"}
ANNOTATION_STATUS="HISTORICAL_PROVENANCE_ANNOTATION_UNRECOVERED_NOT_BYTE_ACCEPTED"
ANNOTATION_ROWS=(
 (0,"native","20260922T114002Z_de9505e8c15e/outputs/native.pdb",181712,"cd328a743e389add7403d3f04fcf1f78ef9ae687d365737a419ee8f1cc6fe076"),
 (0,"backbone","20260922T114002Z_de9505e8c15e/outputs/bb1144_seq1.pdb",110612,"6c09a08416d772fa251556d6f12cced39ef270d35c6c96a859c3fd0bfe32e1e0"),
 (0,"design_manifest","20260922T114002Z_de9505e8c15e/manifest.json",12434,"97c239a9fdb423703dea7f532db18839b2afa0dd9711a7184fc2741cd3619820"),
 (1,"native","20260922T113858Z_149ef033124f/outputs/native.pdb",181712,"cd328a743e389add7403d3f04fcf1f78ef9ae687d365737a419ee8f1cc6fe076"),
 (1,"backbone","20260922T113858Z_149ef033124f/outputs/bb144_seq1.pdb",110612,"39978b06a6143c968e3e8de72e42edb97158aa947af0c19c8f4270845534a11c"),
 (1,"design_manifest","20260922T113858Z_149ef033124f/manifest.json",12402,"47bfbe1852aede63e479b88a1456a06aafc0797730453d003551091ff5251262"),
 (2,"native","20260922T113858Z_149ef033124f/outputs/native.pdb",181712,"cd328a743e389add7403d3f04fcf1f78ef9ae687d365737a419ee8f1cc6fe076"),
 (2,"backbone","20260922T113858Z_149ef033124f/outputs/bb145_seq0.pdb",110612,"4c18ec575b6361ab5c02383d01c615d35a3b541922d18df14b2b00fb75284fcb"),
 (2,"design_manifest","20260922T113858Z_149ef033124f/manifest.json",12402,"47bfbe1852aede63e479b88a1456a06aafc0797730453d003551091ff5251262"),
)
DIAGNOSTIC_REL="steps/24_benchmark_delivery/runs/source_receipt_path_diagnostic_13285/diagnostic.json"
PARENT_DIAGNOSTIC_REL="steps/24_benchmark_delivery/runs/source_receipt_parent_diagnostic_13290/diagnostic.json"
FAILED_V4_REL="steps/24_benchmark_delivery/runs/source_refresh_relative_v4_13279/typed_incomplete.json"
METADATA_SEAL_REL="steps/24_benchmark_delivery/submissions/source_scope_accepted_metadata_readonly_seal_20261012/metadata_seal.json"
SOFTWARE_TESTS=122
def scalar_identity(r):
 return {"original_logical_path":r["path"],"expected_bytes":r["bytes"],"expected_sha256":r["sha256"]}
def annotation_pins():
 return [(("entries",str(i),name),{"path":LEGACY_ROOT+"/steps/03_design/runs/"+tail,"bytes":n,"sha256":sha})for i,name,tail,n,sha in ANNOTATION_ROWS]
def external(r):
 p=Path(r["path"])
 if not p.is_absolute():raise ValueError("Unknown relative receipt outside BBF6 policy")
 return not p.is_relative_to(R)
def field_value(obj,trail):
 for token in trail:
  if not isinstance(token,str):raise ValueError("String field trail required")
  if isinstance(obj,list):
   if not token.isdigit() or str(int(token))!=token:raise ValueError("Exact field index required")
   obj=obj[int(token)]
  elif isinstance(obj,dict):obj=obj[token]
  else:raise ValueError("Receipt field does not exist in verified parent")
 return obj
def strict_snapshot(p,r):
 p=Path(p)
 if not p.is_absolute() or not p.is_relative_to(R) or p.resolve()!=p or p.is_symlink() or not p.is_file() or p.stat().st_mode&0o222:raise ValueError("Exact readonly accepted graph snapshot unavailable: "+str(p))
 if not exact(p,r):raise ValueError("Exact accepted graph snapshot bytes differ: "+str(p))
 return p
class HistoricalRecoveryAnnotations:
 """Only nine predeclared annotations in one exact current recovered sequence input."""
 def __init__(self,verify=strict_snapshot,reader=None):
  self.verify=verify;self.reader=reader or read;self.applied={}
 def parent_readback(self,physical=None):
  physical=physical or ANNOTATION_PARENT
  if (physical["bytes"],physical["sha256"])!=(ANNOTATION_PARENT["bytes"],ANNOTATION_PARENT["sha256"]):raise ValueError("Historical annotation canonical parent byte identity differs")
  self.verify(physical["path"],physical)
  obj=self.reader(physical["path"])
  self.verify(physical["path"],physical)
  if not isinstance(obj,dict) or obj.get("recovery")!=RECOVERY_MARKER or not isinstance(obj.get("entries"),list) or len(obj["entries"])!=3:raise ValueError("Exact existing unrecovered history marker/three-entry input required")
  for trail,r in annotation_pins():
   if field_value(obj,trail)!=r:raise ValueError("Complete nine predeclared history fields differ")
  return obj
 def classify(self,r,parent,trail):
  if parent is None or parent["logical"]["path"]!=ANNOTATION_PARENT["path"]:return None
  if parent["logical"]!=ANNOTATION_PARENT:raise ValueError("Historical annotation logical parent identity differs")
  expected=dict(annotation_pins()).get(tuple(trail))
  if expected is None:return None
  if r!=expected:raise ValueError("Historical annotation child exact field identity differs")
  physical=parent["physical"];self.parent_readback(physical)
  if field_value(self.reader(physical["path"]),trail)!=r:raise ValueError("Historical annotation parent field changed")
  self.verify(physical["path"],physical)
  row={**scalar_identity(r),"parent_original_logical_path":ANNOTATION_PARENT["path"],
   "parent_expected_bytes":ANNOTATION_PARENT["bytes"],"parent_expected_sha256":ANNOTATION_PARENT["sha256"],
   "parent_canonical_receipt":physical,"source_parent":physical,"source_field":list(trail),"canonical_receipt":None,
   "status":ANNOTATION_STATUS,"role":"NONOPERATIVE_HISTORICAL_PROVENANCE_ANNOTATION_UNRECOVERED_NOT_BYTE_ACCEPTED","current_execution_allowed":False,"raw_byte_acceptance":False,
   "historical_file_restored":False,"scope":"Existing declared historical provenance annotation only; not an operative source/raw requirement."}
  self.applied[tuple(trail)]=row
  return row
 def mapping(self,lineage):
  self.parent_readback()
  if set(self.applied)!=set(t for t,_ in annotation_pins()):raise ValueError("All nine historical annotation edges must be observed in actual source graph")
  return {"schema":"exact-unrecovered-historical-annotations.v1",
   "status":"EXACT_NINE_NONOPERATIVE_HISTORICAL_ANNOTATIONS_CPU_CLASSIFIED_ORIGINAL_JSON_UNCHANGED",
   "parent_manifest":ANNOTATION_PARENT,"recovery_marker":RECOVERY_MARKER,"recovery_status":RECOVERY_MARKER["status"],"recovery_missing_files":RECOVERY_MARKER["missing_files"],
   "anchor":{**scalar_identity(LEGACY_ANCHOR),"canonical_receipt":None,"status":ANNOTATION_STATUS,"historical_file_restored":False},
   "entries":[self.applied[t]for t,_ in annotation_pins()],"source_field_index_type":"STRING_DECIMAL_LIST_INDEX",
   "historical_annotation_n":9,"canonical_external_text_edge_n":0,"unresolved_current_external_edges_allowed":False,
   "original_json_unchanged":True,"external_files_read":False,"raw_byte_acceptance":False,
   "old_45_backbones_or_MD_restored":False,"actual_current_sequence_input_parent_bytes_verified":True,
   "scope":"Exact nine previously declared nonoperative historical annotations only. Unknown/current external source/raw edges are fatal; no reconstruction, generic outside-path exemption or new history waiver.",
   "accepted_lineage_receipts":lineage}
RECOVERED_PARENT={"path":str(R/"01_raw/recovered_inputs/candidate_recovery_receipt.json"),"bytes":2528,"sha256":"6398ad0dfafeb272c4bdfef6ce0a01ed14ebe526f1a2765ffbdd46dfe9b4e66c"}
RECOVERED_SESSION="01a0bdc5-988d-70c1-8346-f463d4989fa2"
RECOVERED_TYPE="byte_preserving_evidence_extraction_no_new_scientific_inference"
RECOVERED_FILES=(
 ("session_record_6378_stdout.txt",12759,"4d3412157347e37176386562547b14b572aec599c090199fcb02cfcae9ac52a4"),
 ("session_record_7006_stdout.txt",9654,"dbdc7e78a30e408c52f3a5950e336fc9ac1e61fe93b7374907e89b03dd3b2f74"),
 ("session_record_7013_partial_control_stdout.txt",3851,"c8e6b3ba28b2d874c725f6141fecc095c344528e370eb5cf460f4d3cf7d6ef1e"),
 ("recovered_three_candidates.json",4665,"04a73810c339e4594e8dc989e2c89aa3ba90542f89d5644c92f9df2b755c482c"),
 ("public_source_inventory_5001.json",33967,"b16e64d594e909db20b72c87a95a2b5c68fa6f91f360fa916ed4039405ca33f0"),
)
RECOVERED_DIAGNOSTIC={"path":str(R/"steps/24_benchmark_delivery/runs/source_v6_relative_context_diagnostic_13295/diagnostic.json"),"bytes":4407,"sha256":"e1a3efe660dab843d37c8d216df927927d79ec8e5186cf9249a742ec328812be"}
RECOVERED_METADATA_SEAL=R/"steps/24_benchmark_delivery/submissions/recovered_five_context_metadata_readonly_seal_20261012/receipt.json"
def recovered_pins():
 return [(("files",str(i)),{"path":n,"bytes":b,"sha256":s},{"path":str(Path(RECOVERED_PARENT["path"]).parent/n),"bytes":b,"sha256":s})for i,(n,b,s)in enumerate(RECOVERED_FILES)]
class RecoveredFiveCurrentContext:
 """Only five actual byte-preserving extracted evidence files; not missing structure recovery."""
 def __init__(self,verify=strict_snapshot,reader=None):
  self.verify=verify;self.reader=reader or read;self.applied={}
 def parent_readback(self,physical=None):
  physical=physical or RECOVERED_PARENT
  if (physical["bytes"],physical["sha256"])!=(RECOVERED_PARENT["bytes"],RECOVERED_PARENT["sha256"]):raise ValueError("Recovered five parent byte identity differs")
  self.verify(physical["path"],physical);obj=self.reader(physical["path"]);self.verify(physical["path"],physical)
  expected=[r for _,r,_ in recovered_pins()]
  if not isinstance(obj,dict)or obj.get("schema_version")!=1 or obj.get("session_id")!=RECOVERED_SESSION or obj.get("recovery_type")!=RECOVERED_TYPE or obj.get("files")!=expected:raise ValueError("Exact current recovered five parent marker/full files differ")
  for _,_,canonical in recovered_pins():self.verify(canonical["path"],canonical)
  return obj
 def normalize(self,r,parent,trail):
  if Path(r["path"]).is_absolute():return r,None
  if parent is None or parent["logical"]["path"]!=RECOVERED_PARENT["path"]:return r,None
  if parent["logical"]!=RECOVERED_PARENT:raise ValueError("Recovered five logical parent identity differs")
  rows={t:(relative,canonical)for t,relative,canonical in recovered_pins()}
  expected=rows.get(tuple(trail))
  if expected is None:raise ValueError("Unknown recovered five relative field")
  relative,canonical=expected
  if r!=relative:raise ValueError("Recovered five relative exact receipt differs")
  physical=parent["physical"];obj=self.parent_readback(physical)
  if field_value(obj,trail)!=r:raise ValueError("Recovered five actual parent field differs")
  self.verify(physical["path"],physical)
  context=dict(source_parent=physical,parent_original_logical_path=RECOVERED_PARENT["path"],parent_expected_bytes=RECOVERED_PARENT["bytes"],parent_expected_sha256=RECOVERED_PARENT["sha256"],source_field=list(trail),original_relative_path=r["path"],expected_bytes=r["bytes"],expected_sha256=r["sha256"],canonical_receipt=canonical,status="EXACT_CURRENT_RECOVERED_EVIDENCE_BYTES_ACCEPTED_ORIGINAL_JSON_UNCHANGED",raw_byte_acceptance=True,new_scientific_inference=False,old_structures_backbones_or_MD_restored=False)
  self.applied[tuple(trail)]=context
  return canonical,context
 def mapping(self,lineage):
  self.parent_readback()
  if set(self.applied)!={t for t,_,_ in recovered_pins()}:raise ValueError("All five recovered current relative edges must be observed before source acceptance")
  return dict(schema="exact-current-recovered-five-relative-context.v1",status="EXACT_FIVE_CURRENT_RECOVERED_EVIDENCE_CPU_BYTE_ACCEPTED_ORIGINAL_JSON_UNCHANGED",parent_manifest=RECOVERED_PARENT,session_id=RECOVERED_SESSION,recovery_type=RECOVERED_TYPE,entries=[self.applied[t]for t,_,_ in recovered_pins()],current_recovered_evidence_file_n=5,all_five_current_files_independently_verified=True,all_five_relative_edges_observed=True,source_field_index_type="STRING_DECIMAL_LIST_INDEX",original_json_unchanged=True,external_files_read=False,unknown_relative_edges_allowed=False,raw_byte_acceptance=True,new_scientific_inference=False,old_structures_backbones_or_MD_restored=False,accepted_lineage_receipts=lineage)
def recovered_failure_history():
 old={"path":str(R/"steps/24_benchmark_delivery/frozen/source_refresh_relative_v6_13293/code/source_delivery_refresh_v6.py"),"bytes":33958,"sha256":"0538c38223bafa65949b33f8d33961e0fb66fc09d83f904a805d0ec742b4633d"}
 software={"path":str(R/"steps/24_benchmark_delivery/runs/source_relative_contracts_13293/acceptance.json"),"bytes":2513,"sha256":"81871930a6f6b356c5901e66ab18de99f6e012c7233cc96cec22413cca1e4a48"}
 strict_snapshot(old["path"],old);strict_snapshot(software["path"],software);strict_snapshot(RECOVERED_DIAGNOSTIC["path"],RECOVERED_DIAGNOSTIC)
 diag=read(RECOVERED_DIAGNOSTIC["path"]);strict_snapshot(RECOVERED_DIAGNOSTIC["path"],RECOVERED_DIAGNOSTIC)
 if diag.get("status")!="EXACT_RELATIVE_PARENT_DIAGNOSED_STRICT_GUARD_UNCHANGED_NOT_SOURCE_ACCEPTANCE"or diag.get("slurm_job_id")!="13295"or diag.get("CPUs")!=1 or diag.get("GPUs")!=0 or diag.get("failed_source_job")!="13293"or diag.get("source_producer")!=old or diag.get("original_software_only_acceptance")!=software or any(diag.get(k)is not False for k in ("external_files_read","source_staged","default_changed","formal_outputs_read")):raise ValueError("Actual13295 diagnostic/source history differs")
 details=diag["diagnostic"]
 if details.get("parent")!=RECOVERED_PARENT or details.get("source_field")!=["files","4"]or details.get("offending_receipt")!=recovered_pins()[4][1]or details.get("error")!="Unknown relative receipt parent":raise ValueError("Actual13295 exact recovered parent/field differs")
 current=RecoveredFiveCurrentContext().parent_readback()
 if details.get("parent_JSON")!=current:raise ValueError("Actual13295 parent JSON/current parent differs")
 failure,f=exact_readback(R/"steps/24_benchmark_delivery/runs/source_refresh_relative_v6_13293/typed_incomplete.json")
 if failure.get("status")!="SOURCE_REFRESH_INCOMPLETE_NO_STAGING_NO_RESULT_PROMOTION"or failure.get("error")!="Unknown relative receipt parent":raise ValueError("Actual13293 failed source history differs")
 metadata,m=exact_readback(RECOVERED_METADATA_SEAL,True)
 return dict(actual13293_failed_source_preserved=f,original13293_executing_source=old,original13293_software_only_acceptance=software,actual13295_relative_diagnostic_only=RECOVERED_DIAGNOSTIC,recovered_five_metadata_readonly_seal=m,diagnostic_and_metadata_are_not_byte_acceptance=True,original_json_or_source_modified=False)

def annotation_or_external_failure(r,parent,trail,context):
 row=context.classify(r,parent,trail)
 if row is not None:return row
 if external(r):raise ValueError("Current operative external receipt is not an exact declared historical annotation: "+r["path"])
 return None
def exact_readback(p,readonly=False):
 p=Path(p)
 if not p.is_absolute() or not p.is_relative_to(R) or p.resolve()!=p or p.is_symlink() or not p.is_file():raise ValueError("Exact internal JSON source required")
 if readonly and p.stat().st_mode&0o222:raise ValueError("Readonly accepted lineage required")
 receipt=rec(p);obj=read(p)
 if rec(p)!=receipt:raise ValueError("Lineage JSON changed while reading")
 return obj,receipt
def actual_failure_history():
 diagnostic,d=exact_readback(R/DIAGNOSTIC_REL,True)
 parent_diagnostic,pd=exact_readback(R/PARENT_DIAGNOSTIC_REL,True)
 failure,f=exact_readback(R/FAILED_V4_REL)
 old={"path":str(R/"steps/24_benchmark_delivery/frozen/source_refresh_relative_v4_13279/code/source_delivery_refresh_v4.py"),"bytes":21113,"sha256":"e3b6a5965dae04d95b470c124e4b39d6569a689ac1a4ff5e9775060b981ef794"}
 for obj,jid in ((diagnostic,"13285"),(parent_diagnostic,"13290")):
  if obj.get("status")!="DIAGNOSTIC_ONLY_NOT_SOURCE_ACCEPTANCE" or obj.get("allocation",{}).get("job_id")!=jid or obj.get("allocation",{}).get("allocated_gpus")!=0 or obj.get("original_sealed_V4_source")!=old or obj.get("replay_unexpectedly_completed")is not False or obj.get("strict_authority_guard_weakened")is not False:raise ValueError("Exact actual diagnostic/source history binding differs")
 strict_snapshot(old["path"],old)
 if json.loads(diagnostic["error"]).get("attempted_receipt")!=LEGACY_ANCHOR:raise ValueError("Diagnostic external historical anchor differs")
 details=parent_diagnostic.get("failure_context",{});c=details.get("context",{})
 if details.get("attempted_receipt")!=LEGACY_ANCHOR or details.get("external_original_not_read")is not True or c.get("parent_original_logical_path")!=ANNOTATION_PARENT["path"] or c.get("source_field")!=["entries","2","design_manifest"] or c.get("previous_verified_parent_edge",{}).get("receipt")!=ANNOTATION_PARENT or c.get("exact_declared_alias_hit")is not False:raise ValueError("Actual13290 parent/field diagnostic differs")
 if failure.get("status")!="SOURCE_REFRESH_INCOMPLETE_NO_STAGING_NO_RESULT_PROMOTION" or failure.get("error")!="Source receipt escapes authority":raise ValueError("Original13279 failure identity differs")
 return {"actual13279_failed_source_preserved":f,"actual13285_diagnostic_only":d,"actual13290_parent_diagnostic_only":pd,
  "original13279_failed_executing_source":old,"old13262_failed_source_preserved":True,
  "sealedV5_prepared_unexecuted_not_current":True,"diagnostics_are_not_acceptance":True,"old_json_or_source_modified":False}


ARCHIVE_DIAGNOSTIC={"path":str(R/"steps/24_benchmark_delivery/runs/source_v7_relative_context_diagnostic_13298/diagnostic.json"),"bytes":50849,"sha256":"d680badfc6f11aefdbb88f673f3ac611766e87be7e3b2c5be7633ba886ff2a07"}
ARCHIVE_INVENTORY={"path":str(R/"steps/24_benchmark_delivery/runs/source_unknown_relative_inventory_13299/diagnostic.json"),"bytes":590526,"sha256":"8bc7232449d5469cc621e6e34b26716c3d8ff65fc4a52e10d04b3977d9229313"}
ARCHIVE_METADATA_SEAL=R/"steps/24_benchmark_delivery/submissions/historical_archive_two_context_metadata_readonly_seal_20261012/receipt.json"
FAILED_V7_SOURCE={"path":str(R/"steps/24_benchmark_delivery/frozen/source_refresh_relative_v7_13297/code/source_delivery_refresh_v7.py"),"bytes":42275,"sha256":"c2e9bd2502edc353055b038d50bce79ae70ee92685df095d88cfb74fabe260b1"}
FAILED_V7_SOFTWARE={"path":str(R/"steps/24_benchmark_delivery/runs/source_relative_contracts_13297/acceptance.json"),"bytes":2513,"sha256":"cd7c356bc2736b76d593426cade0438bcd404b3a5addc80da10aff8716d6b4f1"}
def archive_failure_history(archive_context):
 strict_snapshot(FAILED_V7_SOURCE["path"],FAILED_V7_SOURCE);strict_snapshot(FAILED_V7_SOFTWARE["path"],FAILED_V7_SOFTWARE)
 software=read(FAILED_V7_SOFTWARE["path"])
 if software.get("schema")!="source-refresh-relative-software-acceptance.v7"or software.get("status")!="SOURCE_REFRESH_RELATIVE_SOFTWARE_CPU_ACCEPTED_ACTUAL_SOURCE_AUDIT_PENDING"or software.get("tests_expected")!=58 or software.get("allocation",{}).get("job_id")!="13297"or software.get("allocation",{}).get("allocated_gpus")!=0:raise ValueError("Actual failedV7 software58 history differs")
 strict_snapshot(software["contracts"]["path"],software["contracts"]);contracts=read(software["contracts"]["path"])
 if any(contracts.get(k)!=v for k,v in {"status":"PASS","tests":58,"failures":0,"errors":0}.items()):raise ValueError("Actual failedV7 saved58 contracts differ")
 strict_snapshot(software["source_snapshot"]["path"],software["source_snapshot"]);snapshot=read(software["source_snapshot"]["path"])
 oldnames={"source_delivery_refresh_v7.py","relative_receipt_policy.py","test_relative_receipt_policy.py","source_refresh_bootstrap.py","source_refresh_cpu.sbatch","HANDOFF.md","delivery_core.py","delivery_graph_v2.py","provenance_aliases_v2.py","native_resource_closure_v2.py","reference_source_delivery_refresh_v1.py"}
 rows=snapshot.get("source_receipts",[])
 if len(rows)!=11 or {Path(x["path"]).name for x in rows}!=oldnames or FAILED_V7_SOURCE not in rows:raise ValueError("FailedV7 whole11 source history differs")
 for x in rows:strict_snapshot(x["path"],x)
 failure,f=exact_readback(R/"steps/24_benchmark_delivery/runs/source_refresh_relative_v7_13297/typed_incomplete.json")
 if failure.get("status")!="SOURCE_REFRESH_INCOMPLETE_NO_STAGING_NO_RESULT_PROMOTION"or failure.get("error")!="Unknown relative receipt parent":raise ValueError("Actual13297 strict failure must remain failed")
 for pin in (ARCHIVE_DIAGNOSTIC,ARCHIVE_INVENTORY):strict_snapshot(pin["path"],pin)
 diagnostic=read(ARCHIVE_DIAGNOSTIC["path"]);inventory=read(ARCHIVE_INVENTORY["path"])
 if diagnostic.get("status")!="EXACT_RELATIVE_PARENT_DIAGNOSED_STRICT_GUARD_UNCHANGED_NOT_SOURCE_ACCEPTANCE"or diagnostic.get("slurm_job_id")!="13298"or diagnostic.get("GPUs")!=0 or diagnostic.get("source_producer")!=FAILED_V7_SOURCE:raise ValueError("Actual13298 diagnostic-only binding differs")
 wanted={"status":"FINITE_UNKNOWN_RELATIVE_EDGES_COLLECTED_NO_SOURCE_ACCEPTANCE_NO_AUTHORIZATION","job_id":"13299","CPU":1,"GPU":0,"failed_source_job":"13297","parent_count":2,"edge_count":588,"guard_modified_only_in_diagnostic_process":True,"production_source_bytes_unchanged":True,"default_changed":False,"source_staged":False,"formal_outputs_read":False,"model_inference":False,"archive_bytes_read":False,"unrecognized_children_not_recursively_read":True,"all_unknown_nested_contexts_claimed":False,"scientific_acceptance":False}
 if any(inventory.get(k)!=v for k,v in wanted.items())or inventory.get("source_producer")!=FAILED_V7_SOURCE or inventory.get("software_only_gate")!=FAILED_V7_SOFTWARE:raise ValueError("Actual13299 finite diagnostic scope differs")
 expected={ (p["parent_manifest"]["path"],p["parent_manifest"]["bytes"],p["parent_manifest"]["sha256"])for p in archive_context.pins }
 actual={(x["parent"]["path"],x["parent"]["bytes"],x["parent"]["sha256"])for x in inventory.get("parents",[])}
 if actual!=expected or len(inventory.get("parents",[]))!=2:raise ValueError("Actual inventory exact two archive parents differ")
 edges=inventory.get("edges",[]);observed=set()
 for e in edges:
  parent=e.get("parent");pin=next((p for p in archive_context.pins if p["parent_manifest"]==parent),None);trail=e.get("field")
  if pin is None or not isinstance(trail,list)or len(trail)!=2 or trail[0]!="members"or not isinstance(trail[1],str)or not trail[1].isdigit()or str(int(trail[1]))!=trail[1]:raise ValueError("Inventory unknown historical archive context")
  i=int(trail[1]);table=archive_context.parents[parent["path"]]["members"]
  if i>=len(table)or e.get("original_relative_receipt")!=table[i]or e.get("diagnostic_only_edge_skipped")is not True or e.get("authorization_granted")is not False or e.get("current_canonical_child")is not None:raise ValueError("Inventory declared member identity/scope differs")
  observed.add((parent["path"],i))
 expected_edges={(p["parent_manifest"]["path"],i)for p in archive_context.pins for i in range(p["member_count"])}
 if len(edges)!=588 or observed!=expected_edges:raise ValueError("Actual all588 finite diagnostic edges required")
 metadata,seal=exact_readback(ARCHIVE_METADATA_SEAL,True)
 return dict(actual13297_failed_source_preserved=f,original13297_failed_executing_source=FAILED_V7_SOURCE,actual13297_software58_only=FAILED_V7_SOFTWARE,actual13298_archive_parent_diagnostic_only=ARCHIVE_DIAGNOSTIC,actual13299_complete_accessible_finite_inventory_diagnostic_only=ARCHIVE_INVENTORY,historical_archive_two_context_metadata_readonly_seal=seal,archive_namespace_not_live_path=True,diagnostic_nested_unknown_coverage_claimed=False,diagnostics_are_not_archive_or_source_acceptance=True)

def selected_nodes():
 out=[]
 for role,rel,recursive,ext in EXTRA_NODES:
  p=R/rel
  if not p.exists():raise FileNotFoundError("Required operative graph node unavailable: "+str(p))
  choices=p.rglob("*") if p.is_dir() and recursive else [p]
  paths=[x for x in sorted(choices) if x.is_file() and "__pycache__" not in x.parts and x.suffix in ext]
  if not paths:raise ValueError("Operative graph node has no selected source/config/launcher: "+str(p))
  out.append((role,p,recursive,paths))
 return out

FAILED_V8_SOURCE={"path":str(R/"steps/24_benchmark_delivery/frozen/source_refresh_relative_v8_13305/code/source_delivery_refresh_v8.py"),"bytes":50400,"sha256":"6ade3ba1f77cc53f0060adea2ab1816022f240fced6e92f42e8c361d5d733cd5"}
FAILED_V8_SNAPSHOT={"path":str(R/"steps/24_benchmark_delivery/runs/source_relative_contracts_13305/source_snapshot.json"),"bytes":6379,"sha256":"5a267f0058b486b33956c2f153f6a8eaff1a11a287c137e453a0df3522ccfc71"}
FAILED_V8_CONTRACTS={"path":str(R/"steps/24_benchmark_delivery/runs/source_relative_contracts_13305/contracts.json"),"bytes":323,"sha256":"91f13c07d97240a01eda34dd4b5b53ec0fb81d47182d1f4c3fce67b0069a8d8e"}
def schema_failure_history():
 strict_snapshot(FAILED_V8_SOURCE["path"],FAILED_V8_SOURCE)
 software,software_receipt=exact_readback(R/"steps/24_benchmark_delivery/runs/source_relative_contracts_13305/acceptance.json",True)
 expected={"schema":"source-refresh-relative-software-acceptance.v8","status":"SOURCE_REFRESH_RELATIVE_SOFTWARE_CPU_ACCEPTED_ACTUAL_SOURCE_AUDIT_PENDING","tests_expected":84,"compiled_all_python":True,"bash_syntax_checked":True,"source_staged":False,"models_recomputed":False,"GPU_submitted":False,"ACTIVE_changed":False}
 if any(software.get(k)!=v for k,v in expected.items())or software.get("allocation",{}).get("job_id")!="13305"or software.get("allocation",{}).get("allocated_gpus")!=0 or software.get("source_snapshot")!=FAILED_V8_SNAPSHOT or software.get("contracts")!=FAILED_V8_CONTRACTS:raise ValueError("Actual13305 failedV8 software84 history differs")
 strict_snapshot(FAILED_V8_SNAPSHOT["path"],FAILED_V8_SNAPSHOT);strict_snapshot(FAILED_V8_CONTRACTS["path"],FAILED_V8_CONTRACTS)
 snapshot=read(FAILED_V8_SNAPSHOT["path"]);contracts=read(FAILED_V8_CONTRACTS["path"])
 if any(contracts.get(k)!=v for k,v in {"status":"PASS","tests":84,"failures":0,"errors":0}.items()):raise ValueError("Actual savedV8 84 software-only contracts differ")
 oldnames={"source_delivery_refresh_v8.py","historical_archive_member_context.py","relative_receipt_policy.py","test_relative_receipt_policy.py","source_refresh_bootstrap.py","source_refresh_cpu.sbatch","HANDOFF.md","delivery_core.py","delivery_graph_v2.py","provenance_aliases_v2.py","native_resource_closure_v2.py","reference_source_delivery_refresh_v1.py"}
 rows=snapshot.get("source_receipts",[])
 if len(rows)!=12 or len({r["path"]for r in rows})!=12 or {Path(r["path"]).name for r in rows}!=oldnames or FAILED_V8_SOURCE not in rows:raise ValueError("FailedV8 whole12 executing source differs")
 for r in rows:strict_snapshot(r["path"],r)
 failure,failure_receipt=exact_readback(R/"steps/24_benchmark_delivery/runs/source_refresh_relative_v8_13305/typed_incomplete.json")
 if failure.get("status")!="SOURCE_REFRESH_INCOMPLETE_NO_STAGING_NO_RESULT_PROMOTION"or failure.get("error_type")!="TypeError"or failure.get("error")!="unhashable type: 'dict'"or FAILED_V8_SOURCE["path"]not in failure.get("traceback","")or failure.get("source_staged")is not False or failure.get("GPU_submitted")is not False or failure.get("models_recomputed")is not False:raise ValueError("Original13305 parser failure must remain failed")
 return dict(actual13305_failed_source_preserved=failure_receipt,original13305_failed_executing_source=FAILED_V8_SOURCE,actual13305_software84_only=software_receipt,actual13305_software_snapshot=FAILED_V8_SNAPSHOT,actual13305_saved84_contracts=FAILED_V8_CONTRACTS,old_parser_failure_is_not_source_acceptance=True,metadata_schema_fix_has_no_new_metadata_marker=True)

"""Integrated finite source-alias policy; real pureCPU qualification repeats all actual proofs.
No restored or historical source code is executed. Unknown source permissions remain fatal.
"""
import ast,copy,json
from pathlib import Path

PREPARED_PLAN=json.loads("{\"schema\":\"prepared-finite-operative-source-alias-plan.v1\",\"status\":\"EXACT_LITERAL_SOURCE_SCOPE_FOR_NEW_CPU_REQUALIFICATION_NOT_ACCEPTED\",\"source_base\":\"source_refresh_relative_v9\",\"actual_failed_source_job\":\"13307\",\"actual_missing_diagnostic\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_missing_operative_inventory_13308/diagnostic.json\",\"bytes\":207548,\"sha256\":\"2a22a7f4aa4a787f934b72a1fe7ec4bf84c1891c08944120093519d4b469ba11\"},\"actual_saved_byte_diagnostic\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_saved_byte_recovery_diagnostic_13310/diagnostic.json\",\"bytes\":75704,\"sha256\":\"48ce0453db4927cacea9804354fc9b0f598ca598922ff778f0f2024debc4b1ea\"},\"original_alias_registry\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"bytes\":11279,\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"source_identity_n\":8,\"original_edge_n\":12,\"aliases\":[{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_common_review.py\",\"sha256\":\"3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740\",\"bytes\":50747},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_saved_byte_recovery_diagnostic_13310/reconstructed_historical_source/3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740_benchmark_common_review.py\",\"bytes\":50747,\"sha256\":\"3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740\"},\"basis\":\"RECONSTRUCTED_HISTORICAL_SOURCE_NOT_FOUND_ORIGINAL\"},{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/bbf_input_diagnostic.py\",\"sha256\":\"a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3\",\"bytes\":23056},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_bbf_recorded_recovery_diagnostic_13313/reconstructed_historical_source/a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3_bbf_input_diagnostic.py\",\"bytes\":23056,\"sha256\":\"a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3\"},\"basis\":\"EXACT_RECORDED_BBF_SOURCE_RECONSTRUCTION_NOT_FOUND_ORIGINAL\"},{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_runtime.py\",\"bytes\":36014,\"sha256\":\"f3726e2fbbede3678c029ffe3e3f3cac5b52a9826325459d8d3e6756ded505e7\"},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_v3/source/benchmark_runtime.py\",\"bytes\":36014,\"sha256\":\"f3726e2fbbede3678c029ffe3e3f3cac5b52a9826325459d8d3e6756ded505e7\"},\"basis\":\"EXISTING_READONLY_RUNTIME_SNAPSHOT\"},{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_runtime.py\",\"bytes\":37816,\"sha256\":\"773dc1b7d2e0cbbfdaca8c021e07f70323012a3f2c70bcbd6d744bb0ca50fc50\"},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_v5/source/benchmark_runtime.py\",\"bytes\":37816,\"sha256\":\"773dc1b7d2e0cbbfdaca8c021e07f70323012a3f2c70bcbd6d744bb0ca50fc50\"},\"basis\":\"EXISTING_READONLY_RUNTIME_SNAPSHOT\"},{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/formal_benchmark_contract.py\",\"bytes\":46892,\"sha256\":\"13a00de2de298bbc5645f36352bf8da400d3cddb9ce6d5397c623f75d49133ae\"},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/history_exact_bytes/formal_contract_v2_tests_13180_source.py\",\"bytes\":46892,\"sha256\":\"13a00de2de298bbc5645f36352bf8da400d3cddb9ce6d5397c623f75d49133ae\"},\"basis\":\"EXISTING_REGISTERED_FORMAL_READONLY_BYTECOPY\"},{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/freeze_formal_benchmark_v3.py\",\"bytes\":11563,\"sha256\":\"cd7aabd6d4720e909e92dafa0754ab3bb84f766896e3c89e3cfec4e62aa58666\"},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/history_exact_bytes/formal_contract_v2_tests_13168_reviewed_root_formal_helper.py\",\"bytes\":11563,\"sha256\":\"cd7aabd6d4720e909e92dafa0754ab3bb84f766896e3c89e3cfec4e62aa58666\"},\"basis\":\"EXISTING_REGISTERED_FORMAL_READONLY_BYTECOPY\"},{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/test_formal_benchmark_contract.py\",\"bytes\":27208,\"sha256\":\"56256254866dd3c784ebfd2ea084ed4fec82e31921542bd142e484cc5e65a396\"},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/history_exact_bytes/formal_contract_v2_tests_13168_contracts.py\",\"bytes\":27208,\"sha256\":\"56256254866dd3c784ebfd2ea084ed4fec82e31921542bd142e484cc5e65a396\"},\"basis\":\"EXISTING_REGISTERED_FORMAL_READONLY_BYTECOPY\"},{\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/formal_benchmark_contract.py\",\"bytes\":29945,\"sha256\":\"09fd0dff2e9cc1760fc835a586660cc78b3bba685aad8a110b9c610a4eb86063\"},\"canonical\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/history_exact_bytes/formal_contract_v2_tests_13168_source.py\",\"bytes\":29945,\"sha256\":\"09fd0dff2e9cc1760fc835a586660cc78b3bba685aad8a110b9c610a4eb86063\"},\"basis\":\"EXISTING_REGISTERED_FORMAL_READONLY_BYTECOPY\"}],\"edges\":[{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/inputs/plan_v2.json\",\"bytes\":110268,\"sha256\":\"df19c8d6a06afa220844a4c7d713fcbbcd0b7e9972de5e80b62efbbfff7ed7e6\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/inputs/plan_v2.json\",\"bytes\":110268,\"sha256\":\"df19c8d6a06afa220844a4c7d713fcbbcd0b7e9972de5e80b62efbbfff7ed7e6\"},\"source_field\":[\"common_score_source\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_common_review.py\",\"sha256\":\"3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740\",\"bytes\":50747}},{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/inputs/plan_v2.json\",\"bytes\":110268,\"sha256\":\"df19c8d6a06afa220844a4c7d713fcbbcd0b7e9972de5e80b62efbbfff7ed7e6\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/inputs/plan_v2.json\",\"bytes\":110268,\"sha256\":\"df19c8d6a06afa220844a4c7d713fcbbcd0b7e9972de5e80b62efbbfff7ed7e6\"},\"source_field\":[\"source\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/bbf_input_diagnostic.py\",\"sha256\":\"a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3\",\"bytes\":23056}},{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/runs/rf_feature_reaudit_13030/outputs/native_rf_all_channels_contract.json\",\"bytes\":2240,\"sha256\":\"79347625bf297b8530a91fd5a200966d01128794babf7e75bb6d66bef7e72a0b\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/runs/rf_feature_reaudit_13030/outputs/native_rf_all_channels_contract.json\",\"bytes\":2240,\"sha256\":\"79347625bf297b8530a91fd5a200966d01128794babf7e75bb6d66bef7e72a0b\"},\"source_field\":[\"runtime\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_runtime.py\",\"bytes\":36014,\"sha256\":\"f3726e2fbbede3678c029ffe3e3f3cac5b52a9826325459d8d3e6756ded505e7\"}},{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/runs/rf_feature_reaudit_13058/outputs/native_rf_all_channels_contract.json\",\"bytes\":2240,\"sha256\":\"77d3e543e2b56fe22dacf4cbc167d9c7a86fd8af9d5486aa07811824e84e7fa7\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/21_method_runtime/runs/rf_feature_reaudit_13058/outputs/native_rf_all_channels_contract.json\",\"bytes\":2240,\"sha256\":\"77d3e543e2b56fe22dacf4cbc167d9c7a86fd8af9d5486aa07811824e84e7fa7\"},\"source_field\":[\"runtime\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_runtime.py\",\"bytes\":37816,\"sha256\":\"773dc1b7d2e0cbbfdaca8c021e07f70323012a3f2c70bcbd6d744bb0ca50fc50\"}},{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13180/acceptance.json\",\"bytes\":3201,\"sha256\":\"b459d255ec8df34729b186b48fca4c3ba4ce46115ba5e5ce419ddbdd46c514eb\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13180/acceptance.json\",\"bytes\":3201,\"sha256\":\"b459d255ec8df34729b186b48fca4c3ba4ce46115ba5e5ce419ddbdd46c514eb\"},\"source_field\":[\"source\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/formal_benchmark_contract.py\",\"bytes\":46892,\"sha256\":\"13a00de2de298bbc5645f36352bf8da400d3cddb9ce6d5397c623f75d49133ae\"}},{\"source_parent\":{\"bytes\":11279,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"bytes\":11279,\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"source_field\":[\"historical_exact_byte_aliases\",\"3\",\"logical_receipt\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/formal_benchmark_contract.py\",\"bytes\":46892,\"sha256\":\"13a00de2de298bbc5645f36352bf8da400d3cddb9ce6d5397c623f75d49133ae\"}},{\"source_parent\":{\"bytes\":11279,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"bytes\":11279,\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"source_field\":[\"historical_exact_byte_aliases\",\"2\",\"logical_receipt\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/freeze_formal_benchmark_v3.py\",\"bytes\":11563,\"sha256\":\"cd7aabd6d4720e909e92dafa0754ab3bb84f766896e3c89e3cfec4e62aa58666\"}},{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13168/acceptance.json\",\"bytes\":3201,\"sha256\":\"62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13168/acceptance.json\",\"bytes\":3201,\"sha256\":\"62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142\"},\"source_field\":[\"reviewed_root_formal_helper\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/freeze_formal_benchmark_v3.py\",\"bytes\":11563,\"sha256\":\"cd7aabd6d4720e909e92dafa0754ab3bb84f766896e3c89e3cfec4e62aa58666\"}},{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13168/acceptance.json\",\"bytes\":3201,\"sha256\":\"62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13168/acceptance.json\",\"bytes\":3201,\"sha256\":\"62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142\"},\"source_field\":[\"contracts\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/test_formal_benchmark_contract.py\",\"bytes\":27208,\"sha256\":\"56256254866dd3c784ebfd2ea084ed4fec82e31921542bd142e484cc5e65a396\"}},{\"source_parent\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13168/acceptance.json\",\"bytes\":3201,\"sha256\":\"62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_tests_13168/acceptance.json\",\"bytes\":3201,\"sha256\":\"62170ec0b5ddbb6179f53825213bd223ba2fa5b9080e33e39747b1483d9ae142\"},\"source_field\":[\"source\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/formal_benchmark_contract.py\",\"bytes\":29945,\"sha256\":\"09fd0dff2e9cc1760fc835a586660cc78b3bba685aad8a110b9c610a4eb86063\"}},{\"source_parent\":{\"bytes\":11279,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"bytes\":11279,\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"source_field\":[\"historical_exact_byte_aliases\",\"1\",\"logical_receipt\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/test_formal_benchmark_contract.py\",\"bytes\":27208,\"sha256\":\"56256254866dd3c784ebfd2ea084ed4fec82e31921542bd142e484cc5e65a396\"}},{\"source_parent\":{\"bytes\":11279,\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"parent_canonical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json\",\"bytes\":11279,\"sha256\":\"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47\"},\"source_field\":[\"historical_exact_byte_aliases\",\"0\",\"logical_receipt\"],\"original\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal_contract_v2_preparation/formal_benchmark_contract.py\",\"bytes\":29945,\"sha256\":\"09fd0dff2e9cc1760fc835a586660cc78b3bba685aad8a110b9c610a4eb86063\"}}],\"source_acceptance\":false,\"current_execution_authorized\":false,\"raw_model_acceptance\":false,\"scientific_settings_changed\":false,\"licensed_runtime_or_model_assets_included\":false,\"BBF_actual_diagnostic\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_bbf_recorded_recovery_diagnostic_13313/diagnostic.json\",\"bytes\":34363,\"sha256\":\"f77e8e0ec5331da3003349792dcb735f4d8836d014d7fa484e07321c1b3b5f3f\"}}")
ALLOWED_FOUND_BASES=frozenset({"EXISTING_REGISTERED_FORMAL_READONLY_BYTECOPY","EXISTING_READONLY_RUNTIME_SNAPSHOT"})
RECONSTRUCTED_BASIS="RECONSTRUCTED_HISTORICAL_SOURCE_NOT_FOUND_ORIGINAL"

def source_alias_identity(r):
 if not isinstance(r,dict)or set(("path","bytes","sha256"))-set(r):raise ValueError("Complete source descriptor required")
 if type(r["path"])is not str or type(r["bytes"])is not int or r["bytes"]<0 or type(r["sha256"])is not str or len(r["sha256"])!=64:raise ValueError("Exact source identity types required")
 return r["path"],r["bytes"],r["sha256"]
def source_alias_field_value(obj,trail):
 for token in trail:
  if type(token)is not str:raise ValueError("String source field trail required")
  if isinstance(obj,list):
   if not token.isdigit()or str(int(token))!=token:raise ValueError("Exact decimal field index required")
   obj=obj[int(token)]
  elif isinstance(obj,dict):obj=obj[token]
  else:raise ValueError("Missing parent source field")
 return obj
def recorded_literal_replacements(freezer_bytes,expected):
 """One exact common-source s=common.read_text; twelve assignments; common.write_text(s) block."""
 tree=ast.parse(freezer_bytes.decode("utf-8"));body=tree.body
 anchors=[i for i,n in enumerate(body)if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id=="s"and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Attribute)and n.value.func.attr=="read_text"and isinstance(n.value.func.value,ast.Name)and n.value.func.value.id=="common"and not n.value.args and not n.value.keywords]
 if len(anchors)!=1:raise ValueError("One authoritative common source read block required")
 i=anchors[0];rows=[]
 for n in body[i+1:i+13]:
  if not(isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id=="s"and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Attribute)and isinstance(n.value.func.value,ast.Name)and n.value.func.value.id=="s"and n.value.func.attr=="replace"and len(n.value.args)==2 and not n.value.keywords and all(isinstance(a,ast.Constant)and type(a.value)is str for a in n.value.args)):raise ValueError("Only twelve recorded s.replace assignments allowed")
  rows.append([a.value for a in n.value.args])
 end=body[i+13]if len(body)>i+13 else None
 if not(isinstance(end,ast.Expr)and isinstance(end.value,ast.Call)and isinstance(end.value.func,ast.Attribute)and isinstance(end.value.func.value,ast.Name)and end.value.func.value.id=="common"and end.value.func.attr=="write_text"and len(end.value.args)==1 and isinstance(end.value.args[0],ast.Name)and end.value.args[0].id=="s"and not end.value.keywords):raise ValueError("Authoritative common block closing write required")
 if rows!=expected:raise ValueError("Exact twelve recorded common transformations required")
 return rows

def independent_recorded_replay(frozen_bytes,original_bytes,freezer_bytes,expected):
 tuples=recorded_literal_replacements(freezer_bytes,expected)
 text=frozen_bytes.decode("utf-8");reverse=[]
 for i,(old,new)in reversed(list(enumerate(tuples))):
  n=text.count(new)
  if n<1:raise ValueError("Recorded inverse anchor missing")
  text=text.replace(new,old);reverse.append({"recorded_index":i,"replacements":n})
 if text.encode("utf-8")!=original_bytes:raise ValueError("Independent inverse does not equal exact historical bytes")
 forward=[]
 for i,(old,new)in enumerate(tuples):
  n=text.count(old)
  if n<1:raise ValueError("Recorded forward anchor missing")
  text=text.replace(old,new);forward.append({"recorded_index":i,"replacements":n})
 if text.encode("utf-8")!=frozen_bytes:raise ValueError("Independent forward replay is not byte-identical")
 return dict(classification=RECONSTRUCTED_BASIS,inverse_equals_original_bytes=True,forward_equals_frozen_bytes=True,
  exact_replacement_tuples=tuples,reverse_log=reverse,forward_log=forward,freezer_executed=False,reconstructed_source_executed=False,current_execution_authorized=False)

class FiniteOperativeSourceAliases:
 """Verify each permission before caller dedup; there is no basename or unknown-path fallback."""
 def __init__(self,rows,edges,verify_readonly,reader,provenance_verifier,declared=PREPARED_PLAN):
  self.declared=copy.deepcopy(declared);self.verify=verify_readonly;self.reader=reader;self.provenance=provenance_verifier
  expected={source_alias_identity(x["original"]):x for x in self.declared["aliases"]}
  if len(expected)!=8 or len(rows)!=8:raise ValueError("Exactly eight predeclared source identities required")
  self.rows={};self.observed={}
  for row in rows:
   k=source_alias_identity(row["original"])
   if k not in expected or k in self.rows:raise ValueError("Unknown or duplicate finite source alias")
   pin=expected[k];canonical=row.get("canonical")
   if canonical is None:raise ValueError("Exact BBF evidence unresolved; no partial eight-source qualification")
   if source_alias_identity(canonical)[1:]!=k[1:]:raise ValueError("Alias changes source bytes")
   if pin["canonical"]is not None and canonical!=pin["canonical"]:raise ValueError("Selected literal readonly source snapshot differs")
   if row["basis"]!=pin["basis"]and pin["basis"]!="PENDING_EXACT_BBF_BYTE_PROOF":raise ValueError("Source provenance classification differs")
   if row["basis"]not in ALLOWED_FOUND_BASES|{RECONSTRUCTED_BASIS,"EXACT_RECORDED_BBF_SOURCE_RECONSTRUCTION_NOT_FOUND_ORIGINAL","EXISTING_EXACT_BBF_READONLY_BYTECOPY"}:raise ValueError("Unknown source provenance basis")
   self.verify(canonical["path"],canonical)
   proof=self.provenance(row)
   if not isinstance(proof,dict)or proof.get("classification")!=row["basis"]or proof.get("canonical_receipt")!=canonical or proof.get("current_execution_authorized")is not False:raise ValueError("Independently verified finite source provenance required")
   self.verify(canonical["path"],canonical)
   self.rows[k]={**copy.deepcopy(row),"independent_provenance":proof}
  expected_edges=self.declared["edges"]
  if edges!=expected_edges or len(edges)!=12:raise ValueError("Exact predeclared twelve source edge contexts required")
  self.edges={(source_alias_identity(e["source_parent"]),tuple(e["source_field"]),source_alias_identity(e["original"])):e for e in edges}
  if len(self.edges)!=12:raise ValueError("Duplicate predeclared source edge")
 def authorize(self,r,parent_context,trail):
  k=source_alias_identity(r)
  if k not in self.rows:return None
  if parent_context is None:raise ValueError("Known historical source requires its exact parent field")
  logical=parent_context["logical"];physical=parent_context["physical"];t=tuple(trail)
  edge=self.edges.get((source_alias_identity(logical),t,k))
  if edge is None:raise ValueError("Unknown parent/field permission for finite source identity")
  if physical!=edge["parent_canonical_receipt"]:raise ValueError("Source parent canonical identity differs")
  self.verify(physical["path"],physical)
  obj=self.reader(physical["path"])
  if source_alias_field_value(obj,t)!=r:raise ValueError("Actual source parent field differs")
  self.verify(physical["path"],physical)
  row=self.rows[k];self.verify(row["canonical"]["path"],row["canonical"])
  observed=dict(source_parent=logical,parent_canonical_receipt=physical,source_field=list(t),
   original_logical_path=r["path"],expected_bytes=r["bytes"],expected_sha256=r["sha256"],
   canonical_receipt=row["canonical"],basis=row["basis"],current_execution_authorized=False)
  self.observed[(source_alias_identity(logical),t,k)]=observed
  return observed
 def require_complete(self):
  if set(self.observed)!=set(self.edges):raise ValueError("All twelve original source edges must be actually observed")
  if {source_alias_identity(e["canonical_receipt"])for e in self.observed.values()}!={source_alias_identity(r["canonical"])for r in self.rows.values()}:raise ValueError("All eight source identities must be observed")
  for row in self.rows.values():self.verify(row["canonical"]["path"],row["canonical"])
  for edge in self.edges.values():
   parent=edge["parent_canonical_receipt"];self.verify(parent["path"],parent)
   if source_alias_field_value(self.reader(parent["path"]),tuple(edge["source_field"]))!=edge["original"]:raise ValueError("Final exact parent field changed")
   self.verify(parent["path"],parent)
  return dict(schema="finite-operative-source-alias-verification.v1",
   status="EXACT_EIGHT_SOURCE_IDENTITIES_AND_TWELVE_ORIGINAL_EDGES_CPU_VERIFIED_NOT_CURRENT_EXECUTION",
   source_identity_n=8,original_edge_n=12,aliases=list(self.rows.values()),observed_edges=list(self.observed.values()),
   original_JSON_bytes_unchanged=True,unknown_source_aliases_allowed=False,current_execution_authorized=False,
   historical_reconstruction_not_found_original=True,raw_models_reaudited=False,scientific_acceptance=False)


# Exact code restoration is source provenance; it never runs the old programs.
SOURCE_ALIAS_DIAGNOSTICS=(PREPARED_PLAN["actual_missing_diagnostic"],PREPARED_PLAN["actual_saved_byte_diagnostic"],PREPARED_PLAN["BBF_actual_diagnostic"])
BBF_REPLAY_PINS=json.loads("{\"target\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/bbf_input_diagnostic.py\",\"bytes\":23056,\"sha256\":\"a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3\"},\"bundle\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061/source_bundle.json\",\"bytes\":8124,\"sha256\":\"9b89ed8b673597002e6ce52cc6561e009ad2041a253b6484cfacaa7896c8c1e9\"},\"freezer\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/code/freeze_bbf.py\",\"bytes\":3857,\"sha256\":\"31fce180c514667831a736e34c340769a72836d641ea81d5a753d25910e30d02\"},\"launcher\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/code/freeze_launcher.py\",\"bytes\":4050,\"sha256\":\"5d4efd31a7ae3fed701a9f409499a2aa5f86f8ff143ab7b55d9c5ddab9b573c9\"},\"frozen\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061/code/bbf_input_diagnostic.py\",\"bytes\":24842,\"sha256\":\"d2eefb850802a0b93a6724051218c5e686d556c9358d08ab17c7a28dabc247ca\"},\"records\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/source_bbf_recorded_recovery_diagnostic_v1/historical_patch_records.json\",\"bytes\":6584,\"sha256\":\"e28d3267075826d7e728fac58dcea4df700c328ee74c5c6ef381db4a1c553b33\"},\"transforms\":[[\"ROOT/\\\"source/rebuild/benchmark_common_review.py\\\"\",\"Path(__file__).resolve().parent/\\\"benchmark_common_review.py\\\"\"],[\"ROOT/\\\"vendor\\\"/(\\\"IPSAE_\\\"+REVISION[:12])/\\\"ipsae.py\\\"\",\"Path(__file__).resolve().parent/\\\"vendor/ipsae.py\\\"\"]],\"reconstructed\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_bbf_recorded_recovery_diagnostic_13313/reconstructed_historical_source/a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3_bbf_input_diagnostic.py\",\"bytes\":23056,\"sha256\":\"a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3\"},\"record_proofs\":[{\"record_line\":1381,\"timestamp\":\"2026-10-11T05:06:04.414Z\",\"tool_item_id\":\"ctc_00918a3c2e5efc41016acb192eb7048191a4013912e378d57f\",\"call_id\":\"call_1507b4e1755942269e8cf5d83799737f\",\"raw_record_sha256\":\"764f91b32b9838d7ea24d5df9c90ca1911096244323db3d8d8bf58c5f69f39b2\",\"input_sha256\":\"05f3c35c1f3e7f6912736e8113256f1ff139d34fb7e29be491c352bb85719ab2\",\"literal_patch_count\":10,\"extracted_patches\":[{\"record_line\":1381,\"input_line\":2,\"old\":\"msa=np.asarray(data[f[\\\"msa_feature_key\\\"]])\",\"new\":\"msa=np.asarray(data[f.get(\\\"msa_feature_key\\\",f.get(\\\"msa_feat_key\\\"))])\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":3,\"old\":\"    mapping={int(k)-1:int(v)-1 for k,v in job[\\\"target_query_to_template_indices\\\"].items()}\",\"new\":\"    prev=np.asarray(data[f.get(\\\"initial_prev_pos_key\\\",\\\"prev_pos\\\")],float)\\n    if prev.shape!=(L,37,3) or not np.isfinite(prev).all() or prev.any():raise ValueError(\\\"Initial previous-position guess leaked\\\")\\n    cbmask=np.asarray(data[\\\"template_pseudo_beta_mask\\\"],float);cbpos=np.asarray(data[\\\"template_pseudo_beta\\\"],float)\\n    if cbmask.shape!=(1,L) or cbpos.shape!=(1,L,3) or not np.isfinite(cbmask).all() or not np.isfinite(cbpos).all():raise ValueError(\\\"Pseudo-beta template features malformed\\\")\\n    rawmask=np.asarray(data[\\\"batch_all_atom_mask\\\"],float);rawpos=np.asarray(data[\\\"batch_all_atom_positions\\\"],float)\\n    if rawmask.shape!=(L,37) or rawpos.shape!=(L,37,3):raise ValueError(\\\"Raw target-only source batch shape\\\")\\n    mapping={int(k)-1:int(v)-1 for k,v in job[\\\"target_query_to_template_indices\\\"].items()}\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":4,\"old\":\"    if mask[:,T:].any() or pos[:,T:].any():\",\"new\":\"    if rawmask[T:].any() or rawpos[T:].any() or cbmask[:,T:].any() or cbpos[:,T:].any():raise ValueError(\\\"Binder raw/template pseudo-beta leakage\\\")\\n    if absent and (rawmask[absent].any() or rawpos[absent].any() or cbmask[:,absent].any() or cbpos[:,absent].any()):raise ValueError(\\\"Missing target raw/pseudo-beta leakage\\\")\\n    if mask[:,T:].any() or pos[:,T:].any():\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":5,\"old\":\"    if not job[\\\"target_template_enabled\\\"] and n!=0:\",\"new\":\"    if not job[\\\"target_template_enabled\\\"] and (cbmask.any() or cbpos.any()):raise ValueError(\\\"No-template pseudo-beta channel leaked\\\")\\n    if not job[\\\"target_template_enabled\\\"] and n!=0:\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":6,\"old\":\"actual_query_length=L)\",\"new\":\"actual_query_length=L,initial_prev_pos_nonzero=0,all_models_features_verified=f.get(\\\"all_models_feature_arrays_identical\\\"))\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":7,\"old\":\"        if worker.get(\\\"allocation\\\",{}).get(\\\"allocated_gpu_count\\\")!=1:raise ValueError(\\\"GPU worker actual scheduler allocation missing/not1\\\")\",\"new\":\"        allocation_receipt=worker.get(\\\"allocation\\\",{})\\n        if allocation_receipt.get(\\\"allocated_gpu_count\\\")!=1:raise ValueError(\\\"GPU worker actual scheduler allocation missing/not1\\\")\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":8,\"old\":\"components(conf[\\\"iptm\\\"],float(pp[na:].mean()),ip,cp)\",\"new\":\"components(conf.get(\\\"iptm\\\",conf.get(\\\"globaliptm\\\")),float(pp[na:].mean()),ip,cp)\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":9,\"old\":\"global_iptm=float(conf[\\\"iptm\\\"])\",\"new\":\"global_iptm=float(conf.get(\\\"iptm\\\",conf.get(\\\"globaliptm\\\")))\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":10,\"old\":\"        np.savez(path,mask=mask,pos=pos,aatype=query,msa=np.zeros((1,L,49)))\",\"new\":\"        cbmask=np.zeros((1,L));cbpos=np.zeros((1,L,3))\\n        np.savez(path,mask=mask,pos=pos,aatype=query,msa=np.zeros((1,L,49)),prev_pos=np.zeros((L,37,3)),template_pseudo_beta_mask=cbmask,template_pseudo_beta=cbpos,batch_all_atom_mask=np.zeros((L,37)),batch_all_atom_positions=np.zeros((L,37,3)))\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1381,\"input_line\":11,\"old\":\"actual_query_length=L,initial_prev_pos_nonzero=0,all_models_features_verified=f.get(\\\"all_models_feature_arrays_identical\\\"))\",\"new\":\"actual_query_length=L,initial_prev_pos_nonzero=0)\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"}],\"historical_exec_input_executed\":false},{\"record_line\":1408,\"timestamp\":\"2026-10-11T05:07:12.719Z\",\"tool_item_id\":\"ctc_00918a3c2e5efc41016acb197e379c81918ceebce2e037ab7f\",\"call_id\":\"call_695893637f52466ba2c6f5638ac69a8b\",\"raw_record_sha256\":\"1d348fde3009169f67d9639b364db152ef288ff831f07a23e565f5d0ed6073a0\",\"input_sha256\":\"6488e36acaa4fb96916e70175981a62a4280e225a224a4ffb44ba9f98a242c41\",\"literal_patch_count\":2,\"extracted_patches\":[{\"record_line\":1408,\"input_line\":2,\"old\":\"    checked=[]\\n    for key,job\",\"new\":\"    verify(features[\\\"source\\\"])\\n    checked=[]\\n    for key,job\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"},{\"record_line\":1408,\"input_line\":3,\"old\":\"        f=actual[key];actual_stats=feature_arrays(job,f)\",\"new\":\"        f=actual[key];actual_stats=feature_arrays(job,f)\\n        if f[\\\"actual_validated_model_slots\\\"]!=job[\\\"slots\\\"] or not f[\\\"all_models_feature_arrays_identical\\\"]:raise ValueError(\\\"Every fixed model actual forward feature proof required\\\")\",\"replace_semantics\":\"JAVASCRIPT_LITERAL_FIRST_OCCURRENCE\"}],\"historical_exec_input_executed\":false}]}")
COMMON_REPLAY_PINS=json.loads("{\"status\":\"RECONSTRUCTED_EXACT_HISTORICAL_SOURCE_FROM_RECORDED_FREEZER_REVERSE_AND_FORWARD_REPLAY_NOT_CURRENT_EXECUTION\",\"classification\":\"RECONSTRUCTED_HISTORICAL_SOURCE_NOT_FOUND_ORIGINAL\",\"original_logical_receipt\":{\"path\":\"/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_common_review.py\",\"bytes\":50747,\"sha256\":\"3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740\"},\"historical_bundle\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/native_common_13022/source_bundle.json\",\"bytes\":10053,\"sha256\":\"729e3acd0cd371cf2a4dd571850d241c4a9a0fb2470090b178f36d8bc058f500\"},\"source_field\":[\"files\",\"0\"],\"recorded_freezer\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/code/freeze_native_review.py\",\"bytes\":6790,\"sha256\":\"1306a59077d99702da69c88f8b142e6e09a0ce5affcf5c45028009df069ea9fd\"},\"frozen_source\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/native_common_13022/code/benchmark_common_review.py\",\"bytes\":50999,\"sha256\":\"78fbf3a5dc7c2b7ca1729ad7d2a94fffd6ca0110c4ab203becddd2a737ceeae4\"},\"reconstructed_source\":{\"path\":\"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_saved_byte_recovery_diagnostic_13310/reconstructed_historical_source/3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740_benchmark_common_review.py\",\"bytes\":50747,\"sha256\":\"3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740\"},\"exact_twelve_replacements\":[[\"STEP=ROOT/\\\"steps/23_common_review\\\"\",\"STEP=ROOT/\\\"steps/23_common_review\\\"\\nFROZEN_DIR=Path(__file__).resolve().parent\"],[\"sys.path.insert(0,str(ROOT/\\\"source/src\\\"))\",\"sys.path.insert(0,str(FROZEN_DIR/\\\"src\\\"))\"],[\"ROOT/\\\"source/rebuild/screening_transfer.py\\\"\",\"FROZEN_DIR/\\\"screening_transfer.py\\\"\"],[\"ROOT/\\\"source/rebuild/control_msa_check.py\\\"\",\"FROZEN_DIR/\\\"control_msa_check.py\\\"\"],[\"ROOT/\\\"source/src/ppiblocker/structure.py\\\"\",\"FROZEN_DIR/\\\"src/ppiblocker/structure.py\\\"\"],[\"ROOT/\\\"steps/03_af2_restore/inference_env.sh\\\"\",\"FROZEN_DIR/\\\"runtime_entries/af2_inference_env.sh\\\"\"],[\"ROOT/\\\"env/colabfold/bin/colabfold_batch\\\"\",\"FROZEN_DIR/\\\"runtime_entries/colabfold_batch\\\"\"],[\"ROOT/\\\"env/boltz/bin/boltz\\\"\",\"FROZEN_DIR/\\\"runtime_entries/boltz\\\"\"],[\"ROOT/\\\"vendor\\\"/(\\\"IPSAE_\\\"+REVISION[:12])/\\\"ipsae.py\\\"\",\"FROZEN_DIR/\\\"vendor/ipsae.py\\\"\"],[\"str(ROOT/\\\"source/rebuild\\\"),job[\\\"input\\\"][\\\"path\\\"]\",\"str(FROZEN_DIR),job[\\\"input\\\"][\\\"path\\\"]\"],[\"method_origin_present=False)\",\"method_origin_present=False,frozen_source_bundle=rec(FROZEN_DIR.parent/\\\"source_bundle.json\\\"))\"],[\"allocation=allocated,runs=runs)\",\"allocation=allocated,runs=runs,source=plan[\\\"source\\\"],frozen_source_bundle=plan[\\\"frozen_source_bundle\\\"],runtime_locks=plan[\\\"runtime_locks\\\"],receipt_policy=\\\"CPU_PRECOMPUTED_SOURCE_AND_DEPENDENCY_HASH_REFERENCES_NO_GPU_HASH_TASK\\\")\"]],\"reverse_log\":[{\"recorded_index\":11,\"source_line\":38,\"replacements\":1},{\"recorded_index\":10,\"source_line\":37,\"replacements\":1},{\"recorded_index\":9,\"source_line\":36,\"replacements\":1},{\"recorded_index\":8,\"source_line\":35,\"replacements\":2},{\"recorded_index\":7,\"source_line\":34,\"replacements\":1},{\"recorded_index\":6,\"source_line\":33,\"replacements\":2},{\"recorded_index\":5,\"source_line\":32,\"replacements\":1},{\"recorded_index\":4,\"source_line\":31,\"replacements\":1},{\"recorded_index\":3,\"source_line\":30,\"replacements\":1},{\"recorded_index\":2,\"source_line\":29,\"replacements\":1},{\"recorded_index\":1,\"source_line\":28,\"replacements\":1},{\"recorded_index\":0,\"source_line\":27,\"replacements\":1}],\"forward_log\":[{\"recorded_index\":0,\"source_line\":27,\"replacements\":1},{\"recorded_index\":1,\"source_line\":28,\"replacements\":1},{\"recorded_index\":2,\"source_line\":29,\"replacements\":1},{\"recorded_index\":3,\"source_line\":30,\"replacements\":1},{\"recorded_index\":4,\"source_line\":31,\"replacements\":1},{\"recorded_index\":5,\"source_line\":32,\"replacements\":1},{\"recorded_index\":6,\"source_line\":33,\"replacements\":2},{\"recorded_index\":7,\"source_line\":34,\"replacements\":1},{\"recorded_index\":8,\"source_line\":35,\"replacements\":2},{\"recorded_index\":9,\"source_line\":36,\"replacements\":1},{\"recorded_index\":10,\"source_line\":37,\"replacements\":1},{\"recorded_index\":11,\"source_line\":38,\"replacements\":1}],\"old_source_size_and_SHA_verified\":true,\"forward_replay_byte_identical\":true,\"historical_freezer_executed\":false,\"reconstructed_source_executed\":false,\"current_execution_authorized\":false,\"new_alias_accepted\":false,\"source_acceptance\":false}")
def source_alias_need(value,message):
 if not value:raise ValueError(message)
def alias_read_bytes(r):
 p=strict_snapshot(r["path"],r);value=p.read_bytes();strict_snapshot(r["path"],r);return value
def alias_json(r,read_bytes):
 data=read_bytes(r);obj=json.loads(data.decode("utf-8"))
 source_alias_need(read_bytes(r)==data,"Source proof changed during read");return obj
def alias_terminal(job,name,state="COMPLETED",exit_code="0:0"):
 raw=subprocess.check_output(["sacct","-X","-j",job,"--noheader","--parsable2","--format=JobIDRaw,User%64,Account%64,Partition%64,JobName%100,State%40,ExitCode,AllocCPUS,AllocTRES%300"],text=True)
 rows=[x.split("|")for x in raw.splitlines()if x.strip()and x.split("|")[0]==job]
 source_alias_need(len(rows)==1,"One actual exact diagnostic job required")
 result=dict(job_id=job,expected_job_name=name,expected_state=state,expected_exit_code=exit_code,raw_sacct=raw)
 source_alias_terminal_record(result);return result
def source_alias_terminal_record(result):
 jid=result["job_id"];raw=result["raw_sacct"];rows=[x.split("|")for x in raw.splitlines()if x.strip()and x.split("|")[0]==jid]
 source_alias_need(len(rows)==1,"One saved diagnostic job required")
 row=rows[0];source_alias_need(len(row)==9 and row[1:8]==["u21111210118","u21111210118","organ",result["expected_job_name"],result.get("expected_state","COMPLETED"),result.get("expected_exit_code","0:0"),"1"],"Actual diagnostic CPU terminal ownership differs")
 tres={}
 for part in row[8].split(","):
  source_alias_need("="in part,"Malformed diagnostic allocated TRES");k,v=part.split("=",1);source_alias_need(k not in tres,"Duplicate diagnostic TRES");tres[k]=v
 source_alias_need(tres.get("cpu")=="1","Allocated diagnostic CPU1 required")
 for k,v in tres.items():
  if k.startswith("gres/gpu"):source_alias_need(v.isdecimal()and int(v)==0,"Diagnostic allocated GPU must be0")
 return result

def js_literal(token):
 source_alias_need(len(token)>=2 and token[0]in ("'",'"')and token[-1]==token[0]and not token.startswith(token[0]*3),"Only simple JS quoted literal supported")
 result=[];i=1
 escapes={"n":"\n","r":"\r","t":"\t","b":"\b","f":"\f","v":"\v","\\":"\\","'":"'",'"':'"'}
 while i<len(token)-1:
  c=token[i]
  if c=="\\":
   i+=1;source_alias_need(i<len(token)-1 and token[i]in escapes,"Unknown/nonshared JavaScript escape rejected");result.append(escapes[token[i]])
  else:
   source_alias_need(c not in ("\n","\r",token[0]),"Unescaped JS quoted literal delimiter");result.append(c)
  i+=1
 return "".join(result)
def recorded_js_patches(receipt,read_bytes):
 data=alias_json(receipt,read_bytes)
 source_alias_need(data.get("schema")=="exact-two-historical-BBF-patch-records-data-only.v1"and data.get("original_session_id")=="01a12917-8539-7e20-89ae-37dd9dcc35c1"and data.get("original_local_session_file")=="/Users/yangzijian/.codex/sessions/2026/10/11/rollout-2026-10-11T11-52-49-01a12917-8539-7e20-89ae-37dd9dcc35c1.jsonl"and data.get("recorded_tool_calls_executed")is False,"Only exact authorized two historical input records permitted")
 declarations=[
  (1381,"2026-10-11T05:06:04.414Z","ctc_00918a3c2e5efc41016acb192eb7048191a4013912e378d57f","call_1507b4e1755942269e8cf5d83799737f",'let c=load("bbf_diagnostic_code_v2");',10),
  (1408,"2026-10-11T05:07:12.719Z","ctc_00918a3c2e5efc41016acb197e379c81918ceebce2e037ab7f","call_695893637f52466ba2c6f5638ac69a8b",'let c=load("bbf_diagnostic_code_v3");',2)]
 source_alias_need(len(data["records"])==2,"Exactly two historical input records required")
 patches=[];proofs=[]
 for row,decl in zip(data["records"],declarations):
  line,timestamp,item_id,call_id,start,wanted=decl
  source_alias_need(row["record_line"]==line and type(row["raw_JSONL_record"])is str,"Authorized historical record identity differs")
  item=json.loads(row["raw_JSONL_record"]);payload=item["payload"];code=payload["input"];lines=code.splitlines()
  source_alias_need(item["type"]=="response_item"and item["timestamp"]==timestamp and payload["type"]=="custom_tool_call"and payload["id"]==item_id and payload["call_id"]==call_id and payload["name"]=="exec"and type(code)is str and lines[0]==start,"Exact historical tool input metadata differs")
  statements=[(i+1,text)for i,text in enumerate(lines)if text.lstrip().startswith("c=")]
  source_alias_need(len(statements)==wanted and all(text.startswith("c=c.replace(")for _,text in statements),"Only exact literal c.replace chain permitted")
  extracted=[]
  for innerline,text in statements:
   parsed=ast.parse(text);source_alias_need(len(parsed.body)==1 and isinstance(parsed.body[0],ast.Assign),"One literal assignment statement required")
   node=parsed.body[0];value=node.value
   source_alias_need(len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id=="c"and isinstance(value,ast.Call)and isinstance(value.func,ast.Attribute)and isinstance(value.func.value,ast.Name)and value.func.value.id=="c"and value.func.attr=="replace"and len(value.args)==2 and not value.keywords and all(isinstance(x,ast.Constant)and type(x.value)is str for x in value.args),"Only c.replace(two literal strings) AST permitted")
   tokens=[t.string for t in tokenize.generate_tokens(io.StringIO(text).readline)if t.type==tokenize.STRING]
   source_alias_need(len(tokens)==2,"Implicit concatenation/multiple literals forbidden")
   pair=tuple(js_literal(t)for t in tokens);source_alias_need(pair==tuple(x.value for x in value.args)and pair[0]and pair[1]and pair[0]!=pair[1]and "$"not in pair[1],"Shared JS/AST literal decoding or replacement expansion differs")
   extracted.append(dict(record_line=line,input_line=innerline,old=pair[0],new=pair[1],replace_semantics="JAVASCRIPT_LITERAL_FIRST_OCCURRENCE"));patches.append(pair)
  proofs.append(dict(record_line=line,timestamp=timestamp,tool_item_id=item_id,call_id=call_id,raw_record_sha256=hashlib.sha256(row["raw_JSONL_record"].encode()).hexdigest(),input_sha256=hashlib.sha256(code.encode()).hexdigest(),literal_patch_count=wanted,extracted_patches=extracted,historical_exec_input_executed=False))
 source_alias_need(len(patches)==12,"Exact total10+2 historical transformations required")
 return patches,proofs

def alias_literal_freeze_chain(node):
 if isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and node.func.attr=="replace":
  source_alias_need(len(node.args)==2 and not node.keywords and all(isinstance(a,ast.Constant)and type(a.value)is str for a in node.args),"Literal recorded BBF freeze pair required")
  return alias_literal_freeze_chain(node.func.value)+[[a.value for a in node.args]]
 source_alias_need(isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and node.func.attr=="read_text"and isinstance(node.func.value,ast.Name)and node.func.value.id=="own"and not node.args and not node.keywords,"Authoritative BBF own.read_text origin required")
 return []
def scalar_source_proof_view(obj):
 """Only called for five exact independently verified provenance parents below."""
 if isinstance(obj,dict):
  if {"path","bytes","sha256"}<=obj.keys()and isinstance(obj["path"],str):
   metadata={"original_logical_path":obj["path"],"expected_bytes":obj["bytes"],"expected_sha256":obj["sha256"],"role":"EXACT_SOURCE_PROVENANCE_OBSERVATION_NOT_CURRENT_INPUT_OR_RAW_ACCEPTANCE","current_execution_authorized":False,"raw_byte_acceptance":False}
   return {"source_provenance_observation":metadata,"additional_metadata":{k:scalar_source_proof_view(v)for k,v in obj.items()if k not in {"path","bytes","sha256"}}}
  return {k:scalar_source_proof_view(v)for k,v in obj.items()}
 if isinstance(obj,list):return [scalar_source_proof_view(v)for v in obj]
 return obj
def alias_restore_proof_parents(qualified,read_bytes):
 # No schema-only marker: parent descriptors, full expected bytes, and complete
 # verified reconstruction inputs are bound to the actual Source CPU proof.
 actual=qualify_source_alias_inputs(read_bytes,qualified["terminal_accounting"])
 source_alias_need(actual["schema"]==qualified["schema"]and actual["aliases"]==qualified["aliases"]and actual["reconstruction_proofs"]==qualified["reconstruction_proofs"]and actual["proof_parent_views"]==qualified["proof_parent_views"]and actual["canonical_source_and_provenance_inputs"]==qualified["canonical_source_and_provenance_inputs"],"Saved source provenance proof fork/truncation")
 return actual
def qualify_source_alias_inputs(read_bytes=alias_read_bytes,terminal_accounting=None):
 jobs=(("13308","test9_missing_source_diagnostic_v1","COMPLETED","0:0"),("13310","test9_saved_source_diagnostic_v1","COMPLETED","0:0"),("13313","test9_bbf_source_diagnostic_v1","COMPLETED","0:0"),("13307","test9_source_relative_v9","FAILED","1:0"))
 terminal_accounting=[alias_terminal(*j)for j in jobs]if terminal_accounting is None else terminal_accounting
 source_alias_need(len(terminal_accounting)==4 and [(r["job_id"],r["expected_job_name"],r.get("expected_state","COMPLETED"),r.get("expected_exit_code","0:0"))for r in terminal_accounting]==list(jobs),"Exact three diagnostics and failed V9 numeric terminal records required")
 for row in terminal_accounting:source_alias_terminal_record(row)
 missing,saved,final=[alias_json(r,read_bytes)for r in SOURCE_ALIAS_DIAGNOSTICS]
 source_alias_need(missing.get("schema")=="source-missing-exact-operative-inventory-diagnostic-only.v1"and missing.get("status")=="FINITE_ACCESSIBLE_MISSING_OPERATIVE_TEXT_EDGES_DIAGNOSED_NO_SOURCE_ACCEPTANCE_NO_AUTHORIZATION"and missing.get("job_id")=="13308"and missing.get("missing_identity_count")==8 and missing.get("parent_count")==6 and missing.get("missing_edge_count")==12 and missing.get("source_acceptance")is False,"Actual13308 complete finite failed-source inventory required")
 actual_edges=[dict(source_parent=e["parent"],parent_canonical_receipt=e["physical_parent"],source_field=e["field"],original=e["operative_receipt_after_declared_context_normalization"])for e in missing["edges"]]
 source_alias_need(actual_edges==PREPARED_PLAN["edges"],"Actual eight-source twelve-edge identity fork")
 source_alias_need(saved.get("schema")=="saved-source-exact-byte-recovery-diagnostic-only.v1"and saved.get("status")=="FINITE_EIGHT_SOURCE_IDENTITIES_SEARCHED_NO_SOURCE_OR_ALIAS_ACCEPTANCE"and saved.get("job_id")=="13310"and saved.get("input_missing_inventory")==SOURCE_ALIAS_DIAGNOSTICS[0]and {source_alias_identity(r)for r in saved["targets"]}=={source_alias_identity(r["original"])for r in PREPARED_PLAN["aliases"]}and saved.get("matched_identity_count")==6 and saved.get("reconstructed_historical_identity_count")==1,"Actual13310 whole finite source identity required")
 source_alias_need(final.get("schema")=="bbf-recorded-source-recovery-diagnostic-only.v1"and final.get("status")=="EXACT_PRECEDING_SEVEN_IDENTITIES_AND_ONLY_RECORDED_BBF_TRANSFORM_CPU_DIAGNOSED_NO_SOURCE_ACCEPTANCE"and final.get("job_id")=="13313"and final.get("previous_actual_diagnostic")==SOURCE_ALIAS_DIAGNOSTICS[1]and final.get("whole_missing_identity_count")==8 and final.get("all_eight_byte_identities_closed")is True and final.get("unresolved_source_identities")==[],"Actual13313 eight identities closed required")
 for obj,jid in zip((missing,saved,final),("13308","13310","13313")):
  source_alias_need(obj.get("actual_allocation",{}).get("job_id")==jid and obj.get("source_acceptance")is False and obj.get("current_execution_authorized",False)is False and obj.get("default_changed")is False,"Diagnostic-only scope/current source preservation required")
 inputs={source_alias_identity(r):r for r in SOURCE_ALIAS_DIAGNOSTICS}
 def add(r):
  read_bytes(r);inputs[source_alias_identity(r)]=r
 for r in saved["executed_source_files"]+final["executed_source_files"]:add(r)
 for k in ("failed_source","failed_source_software92","failed_source_snapshot","failed_source_contracts","failed_source_typed_incomplete"):add(missing[k])
 registry=PREPARED_PLAN["original_alias_registry"];reg=alias_json(registry,read_bytes);add(registry)
 source_alias_need(saved["original_five_alias_registry"]==registry and len(reg["historical_exact_byte_aliases"])==5 and len(saved["existing_five_declared_aliases"])==5,"Original five-row registered source aliases required")
 for i,item in enumerate(saved["existing_five_declared_aliases"]):
  raw=reg["historical_exact_byte_aliases"][i]
  source_alias_need(raw["logical_receipt"]==item["logical_receipt"]and raw["resolved_readonly_exact_byte_receipt"]==item["physical_receipt"]and raw["historical_report"]==item["historical_report"]and raw["original_mutable_path_hash_claimed_equal"]is False,"Actual registered original/frozen source lineage differs")
  source_alias_need(source_alias_identity(item["logical_receipt"])[1:]==source_alias_identity(item["physical_receipt"])[1:],"Registered original byte identity differs")
  add(item["physical_receipt"]);add(item["historical_report"])
 common=saved["recorded_common_reconstruction"]
 source_alias_need(common==COMMON_REPLAY_PINS,"Actual common recorded reconstruction proof differs")
 for k in ("historical_bundle","recorded_freezer","frozen_source","reconstructed_source"):add(common[k])
 cb=alias_json(common["historical_bundle"],read_bytes)
 source_alias_need(cb.get("status")=="IMMUTABLE_COMMON_REVIEW_SOURCE_BUNDLE"and cb.get("freeze_job")=="13022"and cb.get("source")==common["frozen_source"]and cb["files"][0]["original"]==common["original_logical_receipt"]and cb["files"][0]["frozen"]==common["frozen_source"],"Original common source bundle lineage differs")
 # Every actual frozen origin source is qualified; original mutable fields in
 # the immutable source bundle remain provenance observations only.
 for pair in cb["files"]:add(pair["frozen"])
 common_replay=independent_recorded_replay(read_bytes(common["frozen_source"]),read_bytes(common["reconstructed_source"]),read_bytes(common["recorded_freezer"]),common["exact_twelve_replacements"])
 source_alias_need(common_replay["reverse_log"]==[{k:r[k]for k in ("recorded_index","replacements")}for r in common["reverse_log"]]and common_replay["forward_log"]==[{k:r[k]for k in ("recorded_index","replacements")}for r in common["forward_log"]],"Actual common inverse/forward numeric logs differ")
 actual_bbf=final["bbf_recorded_transform"]
 source_alias_need(actual_bbf["requested_logical_receipt"]==BBF_REPLAY_PINS["target"]and actual_bbf["historical_source_bundle"]==BBF_REPLAY_PINS["bundle"]and actual_bbf["recorded_freezer"]==BBF_REPLAY_PINS["freezer"]and actual_bbf["recorded_launcher_source"]==BBF_REPLAY_PINS["launcher"]and actual_bbf["frozen_source"]==BBF_REPLAY_PINS["frozen"]and actual_bbf["historical_patch_records"]==BBF_REPLAY_PINS["records"]and actual_bbf["reconstructed_source"]==BBF_REPLAY_PINS["reconstructed"],"Exact recorded BBF proof lineage differs")
 for k in ("bundle","freezer","launcher","frozen","records","reconstructed"):add(BBF_REPLAY_PINS[k])
 bb=alias_json(BBF_REPLAY_PINS["bundle"],read_bytes)
 source_alias_need(bb.get("status")=="BBF110_SCIENTIFIC_INPUTS_AND_SOURCE_CONTENT_ACCEPTED_AWAIT_NEW_BUDGET_GUARD_LAUNCHER"and bb.get("cpu_job")=="13061"and bb["source"]==BBF_REPLAY_PINS["frozen"]and bb["source_files"][0]==BBF_REPLAY_PINS["frozen"],"Exact BBF frozen provenance bundle differs")
 for r in bb["source_files"]:add(r)
 patches,patch_proofs=recorded_js_patches(BBF_REPLAY_PINS["records"],read_bytes)
 source_alias_need(patch_proofs==BBF_REPLAY_PINS["record_proofs"]and actual_bbf["historical_patch_record_proofs"]==patch_proofs,"BBF literal record data/proof fork")
 tree=ast.parse(read_bytes(BBF_REPLAY_PINS["freezer"]).decode());nodes=[n for n in tree.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id=="source"]
 source_alias_need(len(nodes)==1 and nodes[0].lineno==13,"Exact BBF recorded source block required")
 transforms=alias_literal_freeze_chain(nodes[0].value);source_alias_need(transforms==BBF_REPLAY_PINS["transforms"],"Only recorded BBF Python freeze2 allowed")
 frozen=read_bytes(BBF_REPLAY_PINS["frozen"]);candidate=frozen.decode();freeze_reverse=[]
 for i,(old,new)in reversed(list(enumerate(transforms))):
  count=candidate.count(new);source_alias_need(count>0,"BBF freeze inverse missing");freeze_reverse.append(dict(index=i,replacements=count));candidate=candidate.replace(new,old)
 post=candidate.encode();patch_reverse=[]
 for i,(old,new)in reversed(list(enumerate(patches))):
  count=candidate.count(new);source_alias_need(count>0,"BBF JS inverse missing");patch_reverse.append(dict(index=i,available_occurrences=count,replacements=1,replace_semantics="JAVASCRIPT_LITERAL_FIRST_OCCURRENCE"));candidate=candidate.replace(new,old,1)
 original=read_bytes(BBF_REPLAY_PINS["reconstructed"]);source_alias_need(candidate.encode()==original,"BBF inverse does not equal exact old source")
 patch_forward=[]
 for i,(old,new)in enumerate(patches):
  count=candidate.count(old);source_alias_need(count>0,"BBF JS forward missing");patch_forward.append(dict(index=i,available_occurrences=count,replacements=1,replace_semantics="JAVASCRIPT_LITERAL_FIRST_OCCURRENCE"));candidate=candidate.replace(old,new,1)
 source_alias_need(candidate.encode()==post and len(post)==24830 and hashlib.sha256(post).hexdigest()=="c0d6528aeb736ac34cf80fe88e9dde203f89959306d50e7a6a8dffb7eee82583","BBF intermediate exact content differs")
 freeze_forward=[]
 for i,(old,new)in enumerate(transforms):
  count=candidate.count(old);source_alias_need(count>0,"BBF Python forward missing");freeze_forward.append(dict(index=i,replacements=count,replace_semantics="PYTHON_LITERAL_ALL_OCCURRENCES"));candidate=candidate.replace(old,new)
 source_alias_need(candidate.encode()==frozen and actual_bbf["reverse_log"]==freeze_reverse and actual_bbf["forward_log"]==freeze_forward and actual_bbf["historical_patch_reverse_log"]==patch_reverse and actual_bbf["historical_patch_forward_log"]==patch_forward,"BBF full independent replay/saved log differs")
 bbf_replay=dict(classification="EXACT_RECORDED_BBF_SOURCE_RECONSTRUCTION_NOT_FOUND_ORIGINAL",historical_patch_record_proofs=patch_proofs,python_freeze_pairs=transforms,freeze_reverse=freeze_reverse,freeze_forward=freeze_forward,JS_first_reverse=patch_reverse,JS_first_forward=patch_forward,original_byte_identity=BBF_REPLAY_PINS["target"],intermediate_bytes=24830,intermediate_sha256="c0d6528aeb736ac34cf80fe88e9dde203f89959306d50e7a6a8dffb7eee82583",inverse_equals_original=True,forward_equals_frozen=True,source_or_historical_exec_executed=False,current_execution_authorized=False)
 aliases=[]
 for row in PREPARED_PLAN["aliases"]:
  source_alias_need(row["canonical"]is not None and source_alias_identity(row["original"])[1:]==source_alias_identity(row["canonical"])[1:],"All eight exact source bytes required");add(row["canonical"])
  if row["basis"]=="EXISTING_READONLY_RUNTIME_SNAPSHOT":
   source_alias_need(any(c["physical_content_receipt"]==row["canonical"]and row["original"]in c["matches_missing_receipts"]and c["readonly"]is True for c in saved["source_candidates"]),"Runtime exact actual source origin missing")
  aliases.append(dict(original=row["original"],canonical=row["canonical"],basis=row["basis"]))
 proof_parents=list(SOURCE_ALIAS_DIAGNOSTICS)+[common["historical_bundle"],BBF_REPLAY_PINS["bundle"]]
 views=[dict(parent_manifest=r,view=scalar_source_proof_view(alias_json(r,read_bytes)),role="EXACT_INDEPENDENTLY_VERIFIED_SOURCE_PROVENANCE_VIEW_NOT_CURRENT_INPUT_OR_RAW_GATE")for r in proof_parents]
 for r in list(inputs.values()):read_bytes(r)
 return dict(schema="finite-source-recovery-inputs-qualification.v1",status="EXACT_SELECTED8_SOURCE_BYTES_RECORDS_REPLAYS_AND_PROOF_PARENTS_CPU_VERIFIED_NOT_CURRENT_EXECUTION",terminal_accounting=terminal_accounting,diagnostics=list(SOURCE_ALIAS_DIAGNOSTICS),aliases=aliases,reconstruction_proofs=dict(common=common_replay,BBF=bbf_replay),proof_parent_views=views,canonical_source_and_provenance_inputs=list(inputs.values()),source_identity_n=8,original_known_edge_n=12,original_JSON_bytes_unchanged=True,raw_byte_acceptance=False,current_execution_authorized=False,models_executed=False)
def source_alias_provenance_verifier(qualified,row):
 expected=next((r for r in qualified["aliases"]if r["original"]==row["original"]),None)
 source_alias_need(expected=={k:row[k]for k in ("original","canonical","basis")},"Qualified selected source provenance differs")
 return dict(classification=row["basis"],canonical_receipt=row["canonical"],full_input_qualification_schema=qualified["schema"],reconstruction=qualified["reconstruction_proofs"]["common"if row["original"]["path"].endswith("benchmark_common_review.py")else"BBF"]if "RECONSTRUCTION"in row["basis"]or row["basis"]==RECONSTRUCTED_BASIS else None,current_execution_authorized=False)

def export_source_alias_qualification(qualified):
 """New proof fields never embed a historical receipt-shaped original child."""
 value=copy.deepcopy(qualified)
 value["aliases"]=[dict(original_logical_path=r["original"]["path"],expected_bytes=r["original"]["bytes"],expected_sha256=r["original"]["sha256"],canonical_receipt=r["canonical"],basis=r["basis"])for r in qualified["aliases"]]
 bbf=value["reconstruction_proofs"]["BBF"]
 bbf["original_byte_identity"]=scalar_identity(bbf["original_byte_identity"])
 return value
def verify_exported_source_alias_qualification(saved,read_bytes=alias_read_bytes,restore=False):
 source_alias_need(not restore or read_bytes is not alias_read_bytes,"Restore requires an explicit restored-index byte reader; live default is forbidden")
 actual=qualify_source_alias_inputs(read_bytes,saved["terminal_accounting"]if restore else None)
 expected=export_source_alias_qualification(actual)
 source_alias_need(saved==expected,"Exact source alias qualification changed, truncated or forked")
 return actual
def source_alias_provenance_postreadback(qualified,read_bytes=alias_read_bytes):
 rows=qualified["canonical_source_and_provenance_inputs"]
 source_alias_need(len({source_alias_identity(r)for r in rows})==len(rows),"Duplicate qualified provenance input")
 for r in rows:read_bytes(r)
 return dict(status="ALL_EXACT_CANONICAL_SOURCE_AND_PROVENANCE_INPUTS_REVERIFIED_AFTER_GRAPH_WALK",input_n=len(rows),verified_inputs=copy.deepcopy(rows),unknown_source_permission_added=False)
def source_alias_proof_parent_view(r,qualified,read_bytes=alias_read_bytes):
 rows=[x for x in qualified["proof_parent_views"]if x["parent_manifest"]==r]
 if not rows:return None
 source_alias_need(len(rows)==1,"Duplicate exact source proof parent")
 obj=alias_json(r,read_bytes)
 source_alias_need(scalar_source_proof_view(obj)==rows[0]["view"],"Exact verified source proof parent view differs")
 return copy.deepcopy(rows[0]["view"])
def export_finite_source_alias_verification(value):
 out=copy.deepcopy(value)
 for row in out["aliases"]:
  original=row.pop("original");row.update(scalar_identity(original))
  replay=row["independent_provenance"].get("reconstruction")
  if replay and "original_byte_identity"in replay:replay["original_byte_identity"]=scalar_identity(replay["original_byte_identity"])
 return out

def _audit(out,software_acceptance_path):
 allocation=cpu();out=Path(out);out.mkdir(parents=True,exist_ok=False)
 context=ExactRelativeContext()
 archive_context=ExactHistoricalArchiveMembers()
 history={**actual_failure_history(),**recovered_failure_history(),**archive_failure_history(archive_context),**schema_failure_history()}
 alias_qualification=qualify_source_alias_inputs()
 alias_qualification_receipt=dump(out/"finite_source_recovery_inputs_qualification.json",export_source_alias_qualification(alias_qualification))
 Path(alias_qualification_receipt["path"]).chmod(0o444)
 finite_aliases=FiniteOperativeSourceAliases(alias_qualification["aliases"],PREPARED_PLAN["edges"],strict_snapshot,read,lambda row:source_alias_provenance_verifier(alias_qualification,row))
 proof_parent_used=set()
 historical_annotations=HistoricalRecoveryAnnotations()
 recovered_context=RecoveredFiveCurrentContext()
 canonical_map=context.complete_mapping()
 canonical_map_receipt=dump(out/"relative_receipt_context_mapping.json",canonical_map)
 Path(canonical_map_receipt["path"]).chmod(0o444)
 prior=read(R/PRIOR_INCLUSION_REL)
 if prior["status"]!="SOURCE_INCLUSION_AUDIT_PASS" or prior["applied"]:raise ValueError("Prior nonstaging source handoff changed role")
 original_rows={}
 def add(p,dest,role,logical=None):
  p=Path(p)
  if not p.is_file() or p.is_symlink():raise ValueError("Required source not regular: "+str(p))
  dest=Path(dest)
  if dest.is_absolute() or ".." in dest.parts:raise ValueError("Unsafe source destination")
  key=(str(p),str(dest))
  if key not in original_rows:original_rows[key]={"path":p,"destination":dest,"roles":set(),"logical_receipts":[]}
  original_rows[key]["roles"].add(role)
  if logical and logical not in original_rows[key]["logical_receipts"]:original_rows[key]["logical_receipts"].append(logical)
 for p,dest,role in source_entries(R,"pilot_v8"):add(p,dest,role)
 extras=selected_nodes()
 for role,node,recursive,paths in extras:
  for p in paths:
   dest=Path("docs/WORKFLOW.md") if p==R/"source/docs/WORKFLOW.md" else Path("rebuild/benchmarks/20261011")/p.relative_to(R)
   add(p,dest,role)
 for p in sorted(Path(__file__).resolve().parent.iterdir()):
  if p.is_file() and p.suffix in TEXT_EXT:
   add(p,Path("rebuild/benchmarks/20261011/24_benchmark_delivery/source_refresh_relative_v10")/p.name,"EXACT_SOURCE_REFRESH_RELATIVE_CONTEXT_SUCCESSOR")
 index,index_receipt=exact_readback(R/INDEX_REL,True)
 policy,policy_receipt=exact_readback(R/POLICY_REL,True)
 pack,pack_receipt=exact_readback(R/BBF_PACK_REL,True)
 _,metadata_seal_receipt=exact_readback(R/METADATA_SEAL_REL,True)
 if pack.get("status")!="BBF_SCIENCE_REVIEW_DOCUMENTS_AND_SOURCE_BYTECOPIES_ACCEPTED" or pack.get("job_id")!="13237" or pack.get("allocated_gpu_count")!=0:raise ValueError("Accepted exact BBF sourcepack lineage required")
 if len(policy.get("entries",[]))!=2 or any(x.get("current_execution_allowed") is not False for x in policy["entries"]):raise ValueError("Only exact two nonoperative historical MSA gaps allowed")
 resolver=ReceiptResolver(R,index=index)
 aliases={}
 for row in index.get("aliases",[]):
  r=row["original"];aliases[(r["path"],r["sha256"])]=Path(row["archived"]["path"])
 for row in pack["copies"]:
  r=row["original"];c=row["copy"]
  if r["sha256"]!=c["sha256"] or r["bytes"]!=c["bytes"] or row.get("byte_identical") is not True:raise ValueError("BBF explanatory/sourcepack alias changes bytes")
  aliases[(r["path"],r["sha256"])]=Path(c["path"])
 for row in alias_qualification["aliases"]:
  original=row["original"];aliases[(original["path"],original["sha256"])]=Path(row["canonical"]["path"])
 for source_input in alias_qualification["canonical_source_and_provenance_inputs"]:
  if Path(source_input["path"]).suffix in TEXT_EXT:
   add(Path(source_input["path"]),Path("rebuild/benchmarks/20261011/exact_source_recovery_provenance")/(source_input["sha256"]+"_"+Path(source_input["path"]).name),"EXACT_SOURCE_RECOVERY_BYTES_AND_REPLAY_PROVENANCE")
 candidates=collections.defaultdict(list)
 for row in original_rows.values():candidates[row["path"].name].append(row["path"])
 cache={};edges=[];seen=set();sources={};gaps={};data_receipts={};deps={}
 def resolve(r):
  if external(r):raise ValueError("Current operative external original cannot be read or inferred from a basename")
  k=(r["path"],r["sha256"],r["bytes"])
  if k in cache:return cache[k]
  a=aliases.get((r["path"],r["sha256"]))
  if a is not None:
   if not exact(a,r):raise ValueError("Exact declared alias drift: "+r["path"])
   p=a;basis="EXACT_ACCEPTED_BYTECOPY_ALIAS"
  elif exact(r["path"],r):p=Path(r["path"]);basis="EXACT_ORIGINAL"
  else:
   found=[p for p in candidates[Path(r["path"]).name] if exact(p,r)]
   if not found:raise FileNotFoundError("Exact operative bytes unavailable: "+r["path"]+" "+r["sha256"])
   p=sorted(found)[0];basis="EXACT_DECLARED_SNAPSHOT_ALIAS"
  cache[k]=(p,basis);return p,basis
 seeds=[rec(R/rel) for rel in SEED_REL]+[rec(R/INDEX_REL),rec(R/POLICY_REL)]
 seeds+=alias_qualification["canonical_source_and_provenance_inputs"]+[e["parent_canonical_receipt"]for e in PREPARED_PLAN["edges"]]
 queue=[(r,None,()) for r in seeds]
 while queue:
  r,parent_context,trail=queue.pop()
  parent=parent_context["logical"]["path"]if parent_context else None
  r,archive_context_row=archive_context.normalize(r,parent_context,trail)
  if r is None:
   edges.append({"historical_archive_member":archive_context_row,"field":list(trail),"role":"HISTORICAL_ARCHIVE_NAMESPACE_MEMBER_BYTE_VERIFIED_NOT_CURRENT_FILE_OR_NEW_SCIENCE"});continue
  r,current_relative_context=recovered_context.normalize(r,parent_context,trail)
  r,relative_context=context.normalize(r,parent,trail)
  annotation=annotation_or_external_failure(r,parent_context,trail,historical_annotations)
  if annotation is not None:
   edges.append({"historical_annotation":annotation,"field":list(trail),"role":ANNOTATION_STATUS})
   continue
  source_alias_context=finite_aliases.authorize(r,parent_context,trail)
  k=(r["path"],r["sha256"],r["bytes"])
  suffix=Path(r["path"]).suffix
  if recompute_dependency(r["path"]):
   deps[k]=r;edges.append({"receipt":r,"parent":parent,"field":list(trail),"role":"CONDITIONAL_INFERENCE_DEPENDENCY_NOT_PUBLIC_SOURCE_NOT_REHASHED"});continue
  # Edge-specific historical permission is checked before visited-node deduplication.
  historical=historical_gap(r,parent,trail,policy,resolver) if parent else None
  if historical is not None:
   gaps[(k,parent,trail)]={"receipt":r,"parent":parent,"field":list(trail),**historical}
   edges.append({"receipt":r,"parent":parent,"field":list(trail),"role":"TYPED_NONOPERATIVE_HISTORICAL_GAP"});continue
  if k in seen:continue
  seen.add(k)
  if suffix not in TEXT_EXT:
   data_receipts[k]=r
   # Data byte acceptance belongs to existing raw gates and final packaging validation.
   edges.append({"receipt":r,"parent":parent,"field":list(trail),"role":"DATA_RECEIPT_RETAINED_FOR_FINAL_PACKAGE_NOT_RAW_CONTENT_REAUDIT"});continue
  p,basis=resolve(r)
  edges.append({"receipt":r,"parent":parent,"field":list(trail),"physical":rec(p),"resolution_basis":basis,"relative_context":relative_context,"current_recovered_relative_context":current_relative_context,"finite_exact_source_alias_context":source_alias_context,"role":"EXACT_TEXT_RECEIPT_READBACK"})
  if suffix in SOURCE_EXT:
   sources[k]={"logical":r,"physical":rec(p),"basis":basis}
   if not any(row["path"]==p for row in original_rows.values()):
    dest=Path("rebuild/benchmarks/20261011/exact_source_aliases")/(r["sha256"]+"_"+Path(r["path"]).name)
    add(p,dest,"RECURSIVE_OPERATIVE_OR_EXACT_HISTORICAL_SOURCE_DEPENDENCY",r)
  if suffix==".json":
   obj=read(p)
   proof_view=source_alias_proof_parent_view(rec(p),alias_qualification)
   if proof_view is not None:
    obj=proof_view;proof_parent_used.add(source_alias_identity(rec(p)))
   if not recognized_metadata_schema(obj):
    # An independent closure report repeats the two gaps as annotations.
    # Validate annotation identity; it is not a new operative source edge.
    if isinstance(obj,dict) and "historical_MSA_gaps" in obj:
     annotations=obj["historical_MSA_gaps"]
     if r["path"]!=str(R/"steps/24_benchmark_delivery/runs/native74_edge_seal_13214/acceptance.json") or len(annotations)!=2:raise ValueError("Unexpected historical annotation context")
     expected={(e["logical_path"],e["expected_sha256"],e["expected_bytes"],e["parent_path"],tuple(e["field"])) for e in policy["entries"]}
     actual={(e["original"]["path"],e["original"]["sha256"],e["original"]["bytes"],e["parent"],tuple(e["trail"])) for e in annotations}
     if actual!=expected:raise ValueError("Historical closure annotations differ from exact policy")
     obj={k:v for k,v in obj.items() if k!="historical_MSA_gaps"}
    if not exact(p,r):raise ValueError("Verified text changed during readback")
    parent_record={"logical":r,"physical":rec(p)}
    queue.extend((n,parent_record,t) for n,t in operative_receipt_edges(obj))
 provenance_after_graph=source_alias_provenance_postreadback(alias_qualification)
 finite_source_verification=finite_aliases.require_complete()
 source_alias_need(proof_parent_used=={source_alias_identity(x["parent_manifest"])for x in alias_qualification["proof_parent_views"]},"All exact verified source proof parents must actually use their scoped view")
 for parent_view in alias_qualification["proof_parent_views"]:source_alias_proof_parent_view(parent_view["parent_manifest"],alias_qualification)
 finite_source_verification_receipt=dump(out/"finite_source_alias_verification.json",export_finite_source_alias_verification(finite_source_verification))
 Path(finite_source_verification_receipt["path"]).chmod(0o444)
 finite_source_index={"schema":"finite-exact-source-alias-index.v1","status":"EXACT_EIGHT_HISTORICAL_SOURCE_BYTES_AND_TWELVE_CONTEXTS_CPU_ACCEPTED_NO_CURRENT_EXECUTION","qualification":alias_qualification_receipt,"verification":finite_source_verification_receipt,"aliases":export_source_alias_qualification(alias_qualification)["aliases"],"edges":finite_source_verification["observed_edges"],"source_identity_n":8,"original_edge_n":12,"current_execution_authorized":False,"raw_byte_acceptance":False,"original_JSON_bytes_unchanged":True}
 finite_source_index_receipt=dump(out/"finite_exact_source_alias_index.json",finite_source_index)
 Path(finite_source_index_receipt["path"]).chmod(0o444)
 # Operative source pins from accepted alias closure are independently included.
 for row in index.get("aliases",[]):
  r=row["original"]
  if Path(r["path"]).suffix in SOURCE_EXT:
   p,basis=resolve(r)
   if not any(item["path"]==p for item in original_rows.values()):
    add(p,Path("rebuild/benchmarks/20261011/exact_source_aliases")/(r["sha256"]+"_"+Path(r["path"]).name),"ACCEPTED_NATIVE74_SOURCE_CLOSURE_EXACT_BYTES",r)
 archive_verification_receipt=dump(out/"archive_member_verification.json",archive_context.verification())
 Path(archive_verification_receipt["path"]).chmod(0o444)
 archive_map=archive_context.mapping(archive_verification_receipt,[rec(Path(__file__)),rec(software_acceptance_path),history["actual13298_archive_parent_diagnostic_only"],history["actual13299_complete_accessible_finite_inventory_diagnostic_only"],history["historical_archive_two_context_metadata_readonly_seal"]])
 archive_map.update(producer_executed_source=rec(Path(__file__)),producer_actual_software_gate=rec(software_acceptance_path),source_graph_selector=rec(Path(__file__).parent/"delivery_graph_v2.py"),prior_accepted_inclusion=rec(R/PRIOR_INCLUSION_REL),original_failure_history=history)
 archive_map_receipt=dump(out/"archive_member_receipt_context_mapping.json",archive_map)
 Path(archive_map_receipt["path"]).chmod(0o444)
 recovered_map=recovered_context.mapping([rec(Path(__file__)),rec(software_acceptance_path),history["actual13295_relative_diagnostic_only"],history["recovered_five_metadata_readonly_seal"]])
 recovered_map.update(producer_executed_source=rec(Path(__file__)),producer_actual_software_gate=rec(software_acceptance_path),source_graph_selector=rec(Path(__file__).parent/"delivery_graph_v2.py"),prior_accepted_inclusion=rec(R/PRIOR_INCLUSION_REL),current_declared_graph_only=True,original_failure_history=history)
 recovered_map_receipt=dump(out/"current_recovered_relative_receipt_context_mapping.json",recovered_map)
 Path(recovered_map_receipt["path"]).chmod(0o444)
 annotation_map=historical_annotations.mapping([index_receipt,pack_receipt,rec(R/PRIOR_INCLUSION_REL),rec(Path(__file__).parent/"delivery_graph_v2.py"),rec(Path(__file__)),rec(software_acceptance_path),history["actual13290_parent_diagnostic_only"],metadata_seal_receipt])
 annotation_map.update(producer_executed_source=rec(Path(__file__)),producer_actual_software_gate=rec(software_acceptance_path),source_graph_selector=rec(Path(__file__).parent/"delivery_graph_v2.py"),prior_accepted_inclusion=rec(R/PRIOR_INCLUSION_REL),original_failure_history=history,root_metadata_readonly_seal=metadata_seal_receipt,current_declared_graph_only=True)
 annotation_map_receipt=dump(out/"external_historical_receipt_context_mapping.json",annotation_map)
 Path(annotation_map_receipt["path"]).chmod(0o444)
 rows=[];issues=[];frozen=out/"readonly_source_bytes";frozen.mkdir()
 for row in sorted(original_rows.values(),key=lambda x:(str(x["destination"]),str(x["path"]))):
  p=row["path"];data=p.read_bytes();text=data.decode("utf-8")
  if SECRET_RE.search(text) or "-----BEGIN "+"OPENSSH PRIVATE KEY-----" in text:issues.append({"path":str(p),"reason":"POTENTIAL_CREDENTIAL_REQUIRES_REVIEW"})
  original=rec(p);copy=frozen/(original["sha256"]+"_"+p.name)
  if copy.exists():
   if copy.read_bytes()!=data:raise ValueError("Frozen source collision")
  else:copy.write_bytes(data);copy.chmod(0o444)
  roles=sorted(row["roles"])
  kind="TEST" if p.name.startswith("test_") or "contract" in p.name and p.name not in {"formal_benchmark_contract.py"} and p.name.endswith(".py") else "DOCUMENT" if p.suffix==".md" else "CONFIGURATION_OR_LAUNCHER" if p.suffix in {".json",".sh",".sbatch"} else "IMPLEMENTATION"
  rows.append({"source":rec(copy),"original_source":original,"repository_relative":str(row["destination"]),"role":";".join(roles),"roles":roles,"kind":kind,"logical_receipts":row["logical_receipts"],"cluster_specific":"/lustre/users/" in text or "#SBATCH" in text})
 destination={}
 for row in rows:
  d=row["repository_relative"]
  if d in destination and destination[d]!=row["source"]["sha256"]:raise ValueError("Repository source destination conflict")
  destination[d]=row["source"]["sha256"]
 frozen.chmod(0o555)
 source_alias_provenance_postreadback(alias_qualification)
 software_source_binding(read(read(software_acceptance_path)["source_snapshot"]["path"]),Path(__file__).resolve().parent)
 closure={"source_provenance_input_postwalk_readback":provenance_after_graph,"finite_exact_source_alias_index":finite_source_index_receipt,"finite_source_recovery_inputs_qualification":alias_qualification_receipt,"finite_source_alias_verification":finite_source_verification_receipt,"exact_recovered_source_identity_n":8,"exact_original_source_edge_n":12,"schema":"benchmark-source-receipt-closure.v1","status":"EXACT_CURRENT_TEXT_AND_SOURCE_DEPENDENCY_CLOSURE_WITH_TYPED_HISTORY","seeds":seeds,"edges":edges,"relative_receipt_context_mapping":canonical_map_receipt,"external_historical_receipt_context_mapping":annotation_map_receipt,"current_recovered_relative_receipt_context_mapping":recovered_map_receipt,"archive_member_receipt_context_mapping":archive_map_receipt,"archive_member_verification":archive_verification_receipt,"historical_archive_context_parent_n":2,"archive_member_n":588,"current_recovered_evidence_file_n":5,"historical_provenance_annotation_n":9,"external_files_read":False,"original_failure_history":history,"recursive_text_and_source_receipt_n":len(cache),"source_receipts":list(sources.values()),"historical_gaps":list(gaps.values()),"conditional_inference_dependencies":list(deps.values()),"data_receipts_preserved_not_reaudited_n":len(data_receipts),"source_missing_allowed_only_exact_historical_edges":True,"raw_models_reaudited":False,"models_recomputed":False,"same_lustre_only":True}
 closure_receipt=dump(out/"source_receipt_closure.json",closure)
 result={"finite_exact_source_alias_index":finite_source_index_receipt,"finite_source_recovery_inputs_qualification":alias_qualification_receipt,"finite_source_alias_verification":finite_source_verification_receipt,"exact_recovered_source_identity_n":8,"exact_original_source_edge_n":12,"schema":"benchmark-source-inclusion.v3","status":"SOURCE_INCLUSION_AUDIT_PASS" if not issues else "SOURCE_INCLUSION_REVIEW_REQUIRED","authority_root":str(R),"declared_runtime_settings":"pilot_v8","prior_inclusion":rec(R/PRIOR_INCLUSION_REL),"graph_nodes":graph_nodes(R,"pilot_v8")+[{"role":role,"path":str(p),"recursive":recursive} for role,p,recursive,paths in extras],"files":rows,"issues":issues,"applied":False,"allocation":allocation,"source_receipt_closure":closure_receipt,"entry_kind_counts":dict(collections.Counter(x["kind"] for x in rows)),"actual_source_dependency_n":len(sources),"historical_gap_count":len(gaps),"formal_array_job_id":"13260","formal_benchmark_completed":False,"ACTIVE_changed":False,"scope":"Frozen public source/config/launcher/readiness only. Data evidence gates remain accepted originals; full formal GPU results/common review/package/restore/publication are pending.","immutable_staging_policy":"Stage only this exact audited frozen source byte set, verify expected audit SHA, refuse different existing destinations. No mtime or later graph re-enumeration."}
 result["runner_source_snapshot"]=[rec(p) for p in sorted(Path(__file__).parent.iterdir()) if p.is_file() and p.suffix in {".py",".sbatch"}]
 inclusion=dump(out/"source_inclusion_v3.json",result)
 software_gate=dump(out/"software_gate_binding.json",{"software_acceptance":rec(software_acceptance_path),"status":"ACTUAL_SOFTWARE_GATE_BOUND_TO_SOURCE_REFRESH_V10"})
 acceptance={"finite_exact_source_alias_index":finite_source_index_receipt,"finite_source_recovery_inputs_qualification":alias_qualification_receipt,"finite_source_alias_verification":finite_source_verification_receipt,"exact_recovered_source_identity_n":8,"exact_original_source_edge_n":12,"schema":"source-delivery-refresh.v3","relative_receipt_context_mapping":canonical_map_receipt,"external_historical_receipt_context_mapping":annotation_map_receipt,"current_recovered_relative_receipt_context_mapping":recovered_map_receipt,"archive_member_receipt_context_mapping":archive_map_receipt,"archive_member_verification":archive_verification_receipt,"historical_archive_context_parent_n":2,"archive_member_n":588,"current_recovered_evidence_file_n":5,"historical_provenance_annotation_n":9,"external_files_read":False,"original_failure_history":history,"software_gate_binding":software_gate,"status":"CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY" if not issues else "SOURCE_REFRESH_REQUIRES_REVIEW","source_inclusion":inclusion,"source_closure":closure_receipt,"source_entries":len(rows),"source_issues":len(issues),"entry_kind_counts":result["entry_kind_counts"],"current_formal28_source_bound":True,"formal_runtime":"pilot_v8","formal_array_job_id":"13260","source_staged":False,"ACTIVE_changed":False,"GPU_submitted":False,"raw_models_recomputed":False}
 dump(out/"acceptance.json",acceptance)
 for output in out.iterdir():
  if output.is_file():output.chmod(0o444)
 out.chmod(0o555)
 print(json.dumps(acceptance,ensure_ascii=False))
SOFTWARE_PACKAGE_NAMES=("source_delivery_refresh_v10.py","historical_archive_member_context.py","relative_receipt_policy.py","test_relative_receipt_policy.py","source_refresh_bootstrap.py","source_refresh_cpu.sbatch","HANDOFF.md","delivery_core.py","delivery_graph_v2.py","provenance_aliases_v2.py","native_resource_closure_v2.py","reference_source_delivery_refresh_v1.py")
def software_source_binding(snapshot,here):
 here=Path(here)
 expected={str(here/name)for name in SOFTWARE_PACKAGE_NAMES}
 rows=snapshot.get("source_receipts",[])
 paths=[r.get("path")for r in rows]
 if len(paths)!=len(set(paths)) or set(paths)!=expected:raise ValueError("Exact whole tested software package required")
 for r in rows:
  p=Path(r["path"])
  if not p.is_absolute() or p.resolve()!=p or p.is_symlink() or not p.is_file() or p.stat().st_mode&0o222:raise ValueError("Readonly tested software source unavailable")
  if rec(p)!=r:raise ValueError("Tested software helper/dependency/source drift: "+str(p))
 return rows
def software_contract_counts(obj):
 if obj.get("status")!="PASS" or obj.get("tests")!=SOFTWARE_TESTS or obj.get("failures")!=0 or obj.get("errors")!=0:raise ValueError("Actual saved122 software contracts/counts must pass")
 return obj
def audit(out,software_acceptance_path):
 cpu();software_path=Path(software_acceptance_path)
 if not software_path.is_absolute() or software_path.resolve()!=software_path or not software_path.is_relative_to(R) or software_path.stat().st_mode&0o222:raise ValueError("Readonly absolute actual software gate required")
 software=read(software_path)
 if software.get("schema")!="source-refresh-relative-software-acceptance.v10"or software.get("status")!="SOURCE_REFRESH_RELATIVE_SOFTWARE_CPU_ACCEPTED_ACTUAL_SOURCE_AUDIT_PENDING"or software.get("tests_expected")!=SOFTWARE_TESTS or software.get("compiled_all_python")is not True or software.get("bash_syntax_checked")is not True:raise ValueError("Actual accepted CPU software preflight required")
 snapshot=read(software["source_snapshot"]["path"])
 if rec(software["source_snapshot"]["path"])!=software["source_snapshot"]:raise ValueError("Software snapshot drift")
 software_source_binding(snapshot,Path(__file__).resolve().parent)
 if rec(software["contracts"]["path"])!=software["contracts"]:raise ValueError("Actual accepted software contracts differ")
 software_contract_counts(read(software["contracts"]["path"]))
 out=Path(out)
 if out.exists():raise FileExistsError("Fresh output required; previous failed/accepted outputs are never rewritten")
 try:return _audit(out,software_acceptance_path)
 except Exception as error:
  out.mkdir(parents=True,exist_ok=True)
  failure={"schema":"source-delivery-refresh-incomplete.v3","status":"SOURCE_REFRESH_INCOMPLETE_NO_STAGING_NO_RESULT_PROMOTION","failed_stage":"EXACT_CURRENT_SOURCE_AND_RECEIPT_CLOSURE","error_type":type(error).__name__,"error":str(error),"traceback":traceback.format_exc(),"failed_previous_source_job":"13262","failed_previous_relative_source_job":"13279","failed_previous_context_source_job":"13293","failed_previous_five_context_source_job":"13297","diagnostic_only_jobs":["13285","13290","13295","13298","13299"],"previous_failure_retained":True,"external_files_read":False,"source_staged":False,"ACTIVE_changed":False,"GPU_submitted":False,"models_recomputed":False}
  dump(out/"typed_incomplete.json",failure)
  raise
def stage(audit_path,expected,out):
 allocation=cpu();original=rec(audit_path)
 if original["sha256"]!=expected:raise ValueError("Exact accepted source audit SHA required")
 obj=read(audit_path)
 for runner in obj["runner_source_snapshot"]:
  p=Path(runner["path"])
  if not exact(p,runner) or p.stat().st_mode&0o222:raise ValueError("Accepted source-stage runner package drift")
 if obj["status"]!="SOURCE_INCLUSION_AUDIT_PASS" or obj["applied"] or obj.get("issues"):raise ValueError("Nonstaging accepted source audit required")
 out=Path(out);out.mkdir(parents=True,exist_ok=False)
 checked=[];created=[]
 for row in obj["files"]:
  p=Path(row["source"]["path"])
  if not exact(p,row["source"]) or p.stat().st_mode&0o222:raise ValueError("Readonly audited source bytes drift")
  d=R/"source"/row["repository_relative"]
  if d.is_symlink() or not d.resolve().is_relative_to((R/"source").resolve()):raise ValueError("Unsafe repository destination")
  if d.exists() and d.read_bytes()!=p.read_bytes():raise FileExistsError("Existing different source requires explicit root review: "+str(d))
  checked.append((p,d,row))
 for p,d,row in checked:
  d.parent.mkdir(parents=True,exist_ok=True)
  if not d.exists():shutil.copyfile(p,d);created.append(str(d))
  if rec(d)["sha256"]!=row["source"]["sha256"]:raise ValueError("Staged source readback failed")
 result={"schema":"source-delivery-stage.v1","status":"EXACT_AUDITED_FROZEN_SOURCE_SET_INSTALLED_NOT_GIT_STAGED","source_inclusion":original,"allocation":allocation,"entry_n":len(checked),"created_files":created,"working_tree_commit_or_stage_performed":False,"ACTIVE_changed":False,"GPU_submitted":False}
 dump(out/"acceptance.json",result);print(result["status"])
def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest="command",required=True)
 x=sub.add_parser("audit");x.add_argument("--out",required=True);x.add_argument("--software-acceptance",required=True)
 x=sub.add_parser("stage");x.add_argument("--audit",required=True);x.add_argument("--audit-sha256",required=True);x.add_argument("--out",required=True)
 a=p.parse_args()
 if a.command=="audit":audit(a.out,a.software_acceptance)
 else:stage(a.audit,a.audit_sha256,a.out)
if __name__=="__main__":main()

