#!/usr/bin/env python3
"""Current source inclusion extension; byte-preserving, CPU only, never result promotion."""
import argparse,collections,hashlib,json,os,shutil,traceback
from pathlib import Path
from delivery_core import cpu,rec,dump,SECRET_RE
from delivery_graph_v2 import source_entries,graph_nodes,SUFFIXES
from provenance_aliases_v2 import ReceiptResolver
from native_resource_closure_v2 import historical_gap,recompute_dependency
from relative_receipt_policy import ExactRelativeContext
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
SOFTWARE_TESTS=46
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
def _audit(out,software_acceptance_path):
 allocation=cpu();out=Path(out);out.mkdir(parents=True,exist_ok=False)
 context=ExactRelativeContext()
 history=actual_failure_history()
 historical_annotations=HistoricalRecoveryAnnotations()
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
   add(p,Path("rebuild/benchmarks/20261011/24_benchmark_delivery/source_refresh_relative_v6")/p.name,"EXACT_SOURCE_REFRESH_RELATIVE_CONTEXT_SUCCESSOR")
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
 candidates=collections.defaultdict(list)
 for row in original_rows.values():candidates[row["path"].name].append(row["path"])
 cache={};edges=[];seen=set();sources={};gaps={};data_receipts={};deps={}
 metadata_only={"exact-resource-aliases.v2","native-resource-closure.v2"}
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
 queue=[(r,None,()) for r in seeds]
 while queue:
  r,parent_context,trail=queue.pop()
  parent=parent_context["logical"]["path"]if parent_context else None
  r,relative_context=context.normalize(r,parent,trail)
  annotation=annotation_or_external_failure(r,parent_context,trail,historical_annotations)
  if annotation is not None:
   edges.append({"historical_annotation":annotation,"field":list(trail),"role":ANNOTATION_STATUS})
   continue
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
  edges.append({"receipt":r,"parent":parent,"field":list(trail),"physical":rec(p),"resolution_basis":basis,"relative_context":relative_context,"role":"EXACT_TEXT_RECEIPT_READBACK"})
  if suffix in SOURCE_EXT:
   sources[k]={"logical":r,"physical":rec(p),"basis":basis}
   if not any(row["path"]==p for row in original_rows.values()):
    dest=Path("rebuild/benchmarks/20261011/exact_source_aliases")/(r["sha256"]+"_"+Path(r["path"]).name)
    add(p,dest,"RECURSIVE_OPERATIVE_OR_EXACT_HISTORICAL_SOURCE_DEPENDENCY",r)
  if suffix==".json":
   obj=read(p)
   if not isinstance(obj,dict) or obj.get("schema") not in metadata_only:
    # An independent closure report repeats the two gaps as annotations.
    # Validate annotation identity; it is not a new operative source edge.
    if "historical_MSA_gaps" in obj:
     annotations=obj["historical_MSA_gaps"]
     if r["path"]!=str(R/"steps/24_benchmark_delivery/runs/native74_edge_seal_13214/acceptance.json") or len(annotations)!=2:raise ValueError("Unexpected historical annotation context")
     expected={(e["logical_path"],e["expected_sha256"],e["expected_bytes"],e["parent_path"],tuple(e["field"])) for e in policy["entries"]}
     actual={(e["original"]["path"],e["original"]["sha256"],e["original"]["bytes"],e["parent"],tuple(e["trail"])) for e in annotations}
     if actual!=expected:raise ValueError("Historical closure annotations differ from exact policy")
     obj={k:v for k,v in obj.items() if k!="historical_MSA_gaps"}
    if not exact(p,r):raise ValueError("Verified text changed during readback")
    parent_record={"logical":r,"physical":rec(p)}
    queue.extend((n,parent_record,t) for n,t in receipt_edges(obj))
 # Operative source pins from accepted alias closure are independently included.
 for row in index.get("aliases",[]):
  r=row["original"]
  if Path(r["path"]).suffix in SOURCE_EXT:
   p,basis=resolve(r)
   if not any(item["path"]==p for item in original_rows.values()):
    add(p,Path("rebuild/benchmarks/20261011/exact_source_aliases")/(r["sha256"]+"_"+Path(r["path"]).name),"ACCEPTED_NATIVE74_SOURCE_CLOSURE_EXACT_BYTES",r)
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
 closure={"schema":"benchmark-source-receipt-closure.v1","status":"EXACT_CURRENT_TEXT_AND_SOURCE_DEPENDENCY_CLOSURE_WITH_TYPED_HISTORY","seeds":seeds,"edges":edges,"relative_receipt_context_mapping":canonical_map_receipt,"external_historical_receipt_context_mapping":annotation_map_receipt,"historical_provenance_annotation_n":9,"external_files_read":False,"original_failure_history":history,"recursive_text_and_source_receipt_n":len(cache),"source_receipts":list(sources.values()),"historical_gaps":list(gaps.values()),"conditional_inference_dependencies":list(deps.values()),"data_receipts_preserved_not_reaudited_n":len(data_receipts),"source_missing_allowed_only_exact_historical_edges":True,"raw_models_reaudited":False,"models_recomputed":False,"same_lustre_only":True}
 closure_receipt=dump(out/"source_receipt_closure.json",closure)
 result={"schema":"benchmark-source-inclusion.v3","status":"SOURCE_INCLUSION_AUDIT_PASS" if not issues else "SOURCE_INCLUSION_REVIEW_REQUIRED","authority_root":str(R),"declared_runtime_settings":"pilot_v8","prior_inclusion":rec(R/PRIOR_INCLUSION_REL),"graph_nodes":graph_nodes(R,"pilot_v8")+[{"role":role,"path":str(p),"recursive":recursive} for role,p,recursive,paths in extras],"files":rows,"issues":issues,"applied":False,"allocation":allocation,"source_receipt_closure":closure_receipt,"entry_kind_counts":dict(collections.Counter(x["kind"] for x in rows)),"actual_source_dependency_n":len(sources),"historical_gap_count":len(gaps),"formal_array_job_id":"13260","formal_benchmark_completed":False,"ACTIVE_changed":False,"scope":"Frozen public source/config/launcher/readiness only. Data evidence gates remain accepted originals; full formal GPU results/common review/package/restore/publication are pending.","immutable_staging_policy":"Stage only this exact audited frozen source byte set, verify expected audit SHA, refuse different existing destinations. No mtime or later graph re-enumeration."}
 result["runner_source_snapshot"]=[rec(p) for p in sorted(Path(__file__).parent.iterdir()) if p.is_file() and p.suffix in {".py",".sbatch"}]
 inclusion=dump(out/"source_inclusion_v3.json",result)
 software_gate=dump(out/"software_gate_binding.json",{"software_acceptance":rec(software_acceptance_path),"status":"ACTUAL_SOFTWARE_GATE_BOUND_TO_SOURCE_REFRESH_V6"})
 acceptance={"schema":"source-delivery-refresh.v3","relative_receipt_context_mapping":canonical_map_receipt,"external_historical_receipt_context_mapping":annotation_map_receipt,"historical_provenance_annotation_n":9,"external_files_read":False,"original_failure_history":history,"software_gate_binding":software_gate,"status":"CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY" if not issues else "SOURCE_REFRESH_REQUIRES_REVIEW","source_inclusion":inclusion,"source_closure":closure_receipt,"source_entries":len(rows),"source_issues":len(issues),"entry_kind_counts":result["entry_kind_counts"],"current_formal28_source_bound":True,"formal_runtime":"pilot_v8","formal_array_job_id":"13260","source_staged":False,"ACTIVE_changed":False,"GPU_submitted":False,"raw_models_recomputed":False}
 dump(out/"acceptance.json",acceptance);print(json.dumps(acceptance,ensure_ascii=False))
SOFTWARE_PACKAGE_NAMES=("source_delivery_refresh_v6.py","relative_receipt_policy.py","test_relative_receipt_policy.py","source_refresh_bootstrap.py","source_refresh_cpu.sbatch","HANDOFF.md","delivery_core.py","delivery_graph_v2.py","provenance_aliases_v2.py","native_resource_closure_v2.py","reference_source_delivery_refresh_v1.py")
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
 if obj.get("status")!="PASS" or obj.get("tests")!=SOFTWARE_TESTS or obj.get("failures")!=0 or obj.get("errors")!=0:raise ValueError("Actual saved46 software contracts/counts must pass")
 return obj
def audit(out,software_acceptance_path):
 cpu();software_path=Path(software_acceptance_path)
 if not software_path.is_absolute() or software_path.resolve()!=software_path or not software_path.is_relative_to(R) or software_path.stat().st_mode&0o222:raise ValueError("Readonly absolute actual software gate required")
 software=read(software_path)
 if software.get("status")!="SOURCE_REFRESH_RELATIVE_SOFTWARE_CPU_ACCEPTED_ACTUAL_SOURCE_AUDIT_PENDING" or software.get("tests_expected")!=SOFTWARE_TESTS:raise ValueError("Actual accepted CPU software preflight required")
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
  failure={"schema":"source-delivery-refresh-incomplete.v3","status":"SOURCE_REFRESH_INCOMPLETE_NO_STAGING_NO_RESULT_PROMOTION","failed_stage":"EXACT_CURRENT_SOURCE_AND_RECEIPT_CLOSURE","error_type":type(error).__name__,"error":str(error),"traceback":traceback.format_exc(),"failed_previous_source_job":"13262","failed_previous_relative_source_job":"13279","diagnostic_only_jobs":["13285","13290"],"previous_failure_retained":True,"external_files_read":False,"source_staged":False,"ACTIVE_changed":False,"GPU_submitted":False,"models_recomputed":False}
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

