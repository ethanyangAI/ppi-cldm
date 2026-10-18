#!/usr/bin/env python3
"""Only five byte-preserving recovered evidence children of one exact parent."""
import copy,json
from pathlib import Path
import exact_relative_bbf_context as b
import historical_annotation_context as h
R=b.R
PARENT={"path":"/lustre/users/u21111210118/projects/test9/01_raw/recovered_inputs/candidate_recovery_receipt.json","bytes":2528,"sha256":"6398ad0dfafeb272c4bdfef6ce0a01ed14ebe526f1a2765ffbdd46dfe9b4e66c"}
ROWS=[["session_record_6378_stdout.txt",12759,"4d3412157347e37176386562547b14b572aec599c090199fcb02cfcae9ac52a4"],["session_record_7006_stdout.txt",9654,"dbdc7e78a30e408c52f3a5950e336fc9ac1e61fe93b7374907e89b03dd3b2f74"],["session_record_7013_partial_control_stdout.txt",3851,"c8e6b3ba28b2d874c725f6141fecc095c344528e370eb5cf460f4d3cf7d6ef1e"],["recovered_three_candidates.json",4665,"04a73810c339e4594e8dc989e2c89aa3ba90542f89d5644c92f9df2b755c482c"],["public_source_inventory_5001.json",33967,"b16e64d594e909db20b72c87a95a2b5c68fa6f91f360fa916ed4039405ca33f0"]]
SESSION="01a0bdc5-988d-70c1-8346-f463d4989fa2"
RECOVERY_TYPE="byte_preserving_evidence_extraction_no_new_scientific_inference"
SCHEMA="exact-current-recovered-five-relative-context.v1"
STATUS="EXACT_FIVE_CURRENT_RECOVERED_EVIDENCE_CPU_BYTE_ACCEPTED_ORIGINAL_JSON_UNCHANGED"
ENTRY_STATUS="EXACT_CURRENT_RECOVERED_EVIDENCE_BYTES_ACCEPTED_ORIGINAL_JSON_UNCHANGED"
def need(v,message):
 if not v:raise ValueError(message)
def expected_entry(i):
 name,n,sha=ROWS[i]
 return dict(source_parent=dict(PARENT),parent_original_logical_path=PARENT["path"],parent_expected_bytes=PARENT["bytes"],parent_expected_sha256=PARENT["sha256"],source_field=["files",str(i)],original_relative_path=name,expected_bytes=n,expected_sha256=sha,canonical_receipt=dict(path=str(Path(PARENT["path"]).parent/name),bytes=n,sha256=sha),status=ENTRY_STATUS,raw_byte_acceptance=True,new_scientific_inference=False,old_structures_backbones_or_MD_restored=False)
def relative(e):return b.receipt(dict(path=e["original_relative_path"],bytes=e["expected_bytes"],sha256=e["expected_sha256"]),absolute=False)
def validate_mapping(m):
 need(m.get("schema")==SCHEMA and m.get("status")==STATUS and m.get("parent_manifest")==PARENT,"Exact recovered-five mapping/parent identity required")
 need(m.get("session_id")==SESSION and m.get("recovery_type")==RECOVERY_TYPE and m.get("current_recovered_evidence_file_n")==5,"Original evidence recovery role differs")
 for k,v in dict(all_five_current_files_independently_verified=True,all_five_relative_edges_observed=True,original_json_unchanged=True,external_files_read=False,unknown_relative_edges_allowed=False,raw_byte_acceptance=True,new_scientific_inference=False,old_structures_backbones_or_MD_restored=False,current_declared_graph_only=True).items():need(m.get(k)is v,"Recovered-five policy differs: "+k)
 entries=m.get("entries",[]);need(len(entries)==5,"All five exact fields required")
 by={}
 for e in entries:
  trail=e.get("source_field");need(isinstance(trail,list)and all(isinstance(t,str)for t in trail),"String exact five-child trail required")
  matching=[i for i in range(5)if trail==["files",str(i)]];need(len(matching)==1 and tuple(trail)not in by,"Unknown/duplicate recovered-five field")
  expected=expected_entry(matching[0]);need(all(e.get(k)==v for k,v in expected.items()),"Recovered-five parent/field/child identity differs")
  by[tuple(trail)]=e
 lineage=m.get("accepted_lineage_receipts",[]);need(len(lineage)>=4 and len({h.key(b.receipt(r))for r in lineage})==len(lineage),"Actual unique recovered-five producer lineage required")
 need(m.get("producer_executed_source")in lineage and m.get("producer_actual_software_gate")in lineage,"Actual source/software lineage required")
 b.receipt(m["source_graph_selector"]);b.receipt(m["prior_accepted_inclusion"])
 return by
def exact_manifest_view(parent,obj,m):
 need(parent==PARENT,"Exact original2528 recovered parent required");by=validate_mapping(m)
 need(isinstance(obj,dict)and obj.get("schema_version")==1 and obj.get("session_id")==SESSION and obj.get("recovery_type")==RECOVERY_TYPE,"Original recovered-five parent marker differs")
 need(obj.get("files")==[relative(expected_entry(i))for i in range(5)],"Full five original child descriptors differ")
 view=copy.deepcopy(obj);contexts=[]
 for field,e in by.items():
  need(b.receipt(h.field_value(obj,field),False)==relative(e),"Exact original recovered-five field changed")
  h.replace_field(view,field,e["canonical_receipt"])
  contexts.append({k:e[k]for k in ("source_parent","source_field","original_relative_path","expected_bytes","expected_sha256","canonical_receipt","status","raw_byte_acceptance","new_scientific_inference","old_structures_backbones_or_MD_restored")})
 return view,contexts
def normalise_edge(r,parent,trail,m):
 if Path(r.get("path","")).is_absolute():return b.receipt(r),None
 by=validate_mapping(m);need(parent==PARENT,"Unknown recovered-relative parent forbidden before dedup")
 field=tuple(trail);need(isinstance(trail,(tuple,list))and all(isinstance(t,str)for t in trail)and field in by,"Unknown recovered-relative field forbidden before dedup")
 e=by[field];need(b.receipt(r,False)==relative(e),"Unknown recovered-relative child identity forbidden")
 return e["canonical_receipt"],{k:e[k]for k in ("source_parent","source_field","original_relative_path","expected_bytes","expected_sha256","canonical_receipt","status","raw_byte_acceptance","new_scientific_inference","old_structures_backbones_or_MD_restored")}
def verify_content(m,read_exact):
 validate_mapping(m)
 for r in m["accepted_lineage_receipts"]+[m["source_graph_selector"],m["prior_accepted_inclusion"]]:read_exact(r)
 obj=json.loads(read_exact(PARENT).read_text());view,contexts=exact_manifest_view(PARENT,obj,m)
 for i in range(5):read_exact(expected_entry(i)["canonical_receipt"])
 return dict(parent_manifest=PARENT,all_five_actual_bytes_verified=True,all_five_original_fields_verified=True,contexts=contexts,original_json_unchanged=True,external_files_read=False,new_scientific_inference=False,old_structures_backbones_or_MD_restored=False)
def verify_mapping_receipt(receipt):
 allocation=b.cpu_guard();m=json.loads(b.verify_bytes(receipt,True).read_text());proof=verify_content(m,lambda r:b.verify_bytes(r,True));proof.update(mapping_receipt=b.receipt(receipt),allocation=allocation);return m,proof
class VerifiedRecoveredFiveReader:
 def __init__(self,mapping_receipt,reader,parent_aliases=()):
  self.mapping_receipt=b.receipt(mapping_receipt);self.mapping,self.verification=verify_mapping_receipt(mapping_receipt);self.reader=reader;self.used=[];self.parents={PARENT["path"]:PARENT}
  for row in parent_aliases:
   need(isinstance(row,dict)and set(row)=={"logical","physical"}and row["logical"]==PARENT,"Only explicit exact recovered parent alias allowed")
   p=b.receipt(row["physical"]);need((p["bytes"],p["sha256"])==(PARENT["bytes"],PARENT["sha256"])and p["path"]not in self.parents,"Recovered parent alias byte/duplicate mismatch")
   b.verify_bytes(p,True);self.parents[p["path"]]=p
 def __call__(self,path):
  p=Path(path);need(p.is_absolute()and p.is_relative_to(b.R)and p.resolve()==p,"External recovered reads forbidden")
  if str(p)not in self.parents:return self.reader(path)
  physical=self.parents[str(p)];b.verify_bytes(physical,True);obj=self.reader(path);view,contexts=exact_manifest_view(PARENT,obj,self.mapping);b.verify_bytes(physical,True)
  self.used.append(dict(physical_parent=physical,logical_parent=PARENT,contexts=contexts,raw_JSON_changed=False));return view
 def proof(self):return dict(mapping_receipt=self.mapping_receipt,verification=self.verification,read_views_used=self.used,raw_JSON_changed=False,module_local_reader_only=True,scope="EXACT_ONE_PARENT_FIVE_CURRENT_EVIDENCE_PATH_FIELDS_ONLY")
def verify_restored_mapping(mapping_receipt,restore_root,index):
 allocation=b.cpu_guard();root,lookup=b.restored_index(index,restore_root);read_paths=[]
 def exact(r):
  p=b.restored_bytes(r,root,lookup);need(not(p.stat().st_mode&0o222),"Readonly restored recovered-five metadata/source/evidence required");read_paths.append(str(p));return p
 m=json.loads(exact(mapping_receipt).read_text());proof=verify_content(m,exact)
 proof.update(mapping_receipt=b.receipt(mapping_receipt),allocation=allocation,restored_root=str(root),read_paths=read_paths,all_read_paths_under_restored_root=True,no_live_root_fallback=True)
 return m,proof

def verify_saved_verification(accepted,read_exact):
 saved=json.loads(read_exact(accepted["current_recovered_verification"]).read_text())
 need(saved.get("mapping_receipt")==accepted.get("current_recovered_relative_receipt_context_mapping")and saved.get("parent_manifest")==PARENT and saved.get("all_five_actual_bytes_verified")is True and saved.get("original_json_unchanged")is True,"Actual saved recovered-five verification proof differs")
 return saved
