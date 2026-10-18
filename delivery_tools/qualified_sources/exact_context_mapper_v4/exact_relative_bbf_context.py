#!/usr/bin/env python3
"""Exact BBF13226 relative-receipt context; no generic relative resolver or JSON rewrite.

Consumers first call verify_mapping_receipt on the actual accepted immutable mapping
under their CPU job, then call normalise before visited-node deduplication.
"""
import copy,hashlib,json,os,re,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
ROOT=R/"steps/23_common_review/bbf_diagnostics/scientific_review"
PARENT={"path":str(ROOT/"runs/review_13226/manifest.json"),"bytes":4108,"sha256":"d2d9093ee2dbe7f14a395457275ccfdd72b1e14221f50a2d18a1c01cf1e4af0f"}
ROWS=(
("metrics.json",54610,"069fd75a563a0920b68146798ebf37841cf7e04c33e0ee258ca5f1aced0950d1"),
("model_crosschecks.json",123769,"97010f22373eea440f54b5b7cb44091a9bdb2ac3b44e420a5edccf3ffb415a2c"),
("cases.tsv",4153,"99467a182086b1dd1fba1ea65ac41cc6d32b9feb0d0170084fe2c12d46793677"),
("paired_changes.tsv",818,"1abfb387468aded6165aa07073e77d395b27dc7a7b7473cac46b0e6f0b11757e"),
("original_labels.tsv",2468,"f4c1c2aef76133b38ce2b15e525337a4963a7480ecb30c042705b85c68d51b18"),
("REPORT_ZH.md",5869,"fd7c05de59549d477d68b7961173030ebdf89256c9f718a79e07567b537aa2af"))
SCHEMA="exact-context-relative-receipts.v1"
STATUS="EXACT_BBF13226_SIX_RELATIVE_OUTPUTS_CPU_VERIFIED_ORIGINAL_JSON_UNCHANGED"
CONTRACTS=201
PACKAGE_NAMES={"finite_source_context.py","test_finite_source_context.py","exact_relative_bbf_context.py","test_exact_relative_bbf_context.py","context_mapper_audit_cpu.py","context_mapper_cpu.sbatch","context_consumer.py","HANDOFF.md","historical_annotation_context.py","test_historical_annotation_context.py","recovered_five_context.py","test_recovered_five_context.py","archive_member_context.py","test_archive_member_context.py"}
def need(ok,message):
 if not ok:raise ValueError(message)
def receipt(r,absolute=True):
 need(isinstance(r,dict)and {"path","bytes","sha256"}<=r.keys(),"Exact descriptor required")
 need(isinstance(r["path"],str)and bool(r["path"]),"Path string required")
 need(Path(r["path"]).is_absolute()==absolute,"Wrong absolute/relative path tier")
 need(type(r["bytes"])is int and r["bytes"]>=0,"Exact nonnegative integer bytes required")
 need(isinstance(r["sha256"],str)and re.fullmatch(r"[0-9a-f]{64}",r["sha256"]),"Exact SHA256 required")
 return {"path":r["path"],"bytes":r["bytes"],"sha256":r["sha256"]}
def expected_entry(index):
 name,n,sha=ROWS[index];rel="runs/review_13226/"+name
 return {"source_parent":PARENT["path"],"source_field":["outputs",str(index)],"original_relative_path":rel,"expected_bytes":n,"expected_sha256":sha,"canonical_receipt":{"path":str(ROOT/rel),"bytes":n,"sha256":sha}}
def validate_mapping(mapping):
 need(isinstance(mapping,dict)and mapping.get("schema")==SCHEMA and mapping.get("status")==STATUS,"Actual exact BBF13226 mapping schema/status required")
 need(mapping.get("parent_manifest")==PARENT and mapping.get("declared_relative_root")==str(ROOT)and mapping.get("original_json_unchanged")is True,"Exact parent/root/unchanged history identity required")
 entries=mapping.get("entries");need(isinstance(entries,list)and len(entries)==6,"All six exact relative fields required")
 by={}
 for item in entries:
  need(isinstance(item,dict),"Mapping entry object required")
  field=item.get("source_field");need(isinstance(field,list)and len(field)==2 and field[0]=="outputs"and str(field[1])in {str(i)for i in range(6)},"Only six declared output index fields allowed")
  index=int(str(field[1]));need(index not in by,"Duplicate exact context field")
  declared=expected_entry(index)
  normal={**item,"source_field":[str(x)for x in field]}
  need(all(normal.get(k)==v for k,v in declared.items()),"Exact relative context descriptor changed")
  need(set(item)==set(declared),"Unexpected mapping entry field; no blanket alias permission")
  receipt(item["canonical_receipt"]);by[index]=declared
 need(set(by)==set(range(6)),"Complete exact context universe required")
 return by
def normalise(r,parent,field,mapping):
 # Validate context permissions before any visited-node deduplication.
 if Path(r.get("path","")).is_absolute():return receipt(r),None
 original=receipt(r,False);by=validate_mapping(mapping)
 need(parent==PARENT,"Relative receipt has different parent bytes/path/SHA")
 need(isinstance(field,(tuple,list))and len(field)==2 and str(field[0])=="outputs"and str(field[1])in {str(i)for i in range(6)},"Relative receipt has unapproved field trail")
 entry=by[int(str(field[1]))]
 need(original=={"path":entry["original_relative_path"],"bytes":entry["expected_bytes"],"sha256":entry["expected_sha256"]},"Relative receipt differs from exact contextual identity")
 return dict(entry["canonical_receipt"]),{"role":"EXACT_BBF13226_RELATIVE_CONTEXT_CANONICALIZATION_NO_JSON_REWRITE","source_parent":dict(PARENT),"source_field":[str(x)for x in field],"original_relative_path":original["path"],"expected_bytes":original["bytes"],"expected_sha256":original["sha256"],"canonical_receipt":dict(entry["canonical_receipt"])}
def receipt_edges(value,parent,mapping,trail=()):
 if isinstance(value,dict):
  if {"path","bytes","sha256"}<=value.keys()and isinstance(value["path"],str):
   canonical,context=normalise(value,parent,trail,mapping)
   yield canonical,trail,context
  for k,v in value.items():yield from receipt_edges(v,parent,mapping,trail+(str(k),))
 elif isinstance(value,list):
  for i,v in enumerate(value):yield from receipt_edges(v,parent,mapping,trail+(str(i),))
def cpu_guard():
 jid=os.environ.get("SLURM_JOB_ID","")
 need(jid.isdigit()and os.environ.get("CUDA_VISIBLE_DEVICES")==""and os.environ.get("JAX_PLATFORMS")=="cpu"and os.environ.get("PYTHONNOUSERSITE")=="1","Actual isolated pureCPU job required before any hash/read")
 text=subprocess.check_output(["sacct","-X","-j",jid,"--noheader","--parsable2","--format=JobIDRaw,State,AllocTRES,User%64,Account%64,Partition%64"],text=True)
 rows=[x.split("|")for x in text.splitlines()if x.split("|",1)[0]==jid]
 need(len(rows)==1 and len(rows[0])>=6 and rows[0][1]=="RUNNING","Unique actual RUNNING CPU allocation required")
 need(rows[0][3:6]==["u21111210118","u21111210118","organ"],"Actual CPU owner/account/partition differs")
 vals=strict_tres(rows[0][2])
 def n(k):
  return vals.get(k,0)
 gpu=max(n("gres/gpu"),sum(n(k)for k in vals if k.startswith("gres/gpu:")))
 need(n("cpu")>=1 and gpu==0,"Actual GPU0 CPU allocation required")
 return {"job_id":jid,"numeric_sacct_record":rows[0],"GPU_count":0}
def verify_bytes(r,readonly=False):
 r=receipt(r);p=Path(r["path"])
 need(p.is_relative_to(R)and p.resolve()==p and not p.is_symlink()and p.is_file(),"Regular exact path within authority required")
 need(not readonly or not(p.stat().st_mode&0o222),"Accepted external mapping must be readonly")
 h=hashlib.sha256();n=0
 with p.open("rb")as handle:
  for b in iter(lambda:handle.read(1048576),b""):h.update(b);n+=len(b)
 need(n==r["bytes"]and h.hexdigest()==r["sha256"],"Exact declared bytes unavailable or changed")
 return p
def verify_mapping_receipt(mapping_receipt):
 allocation=cpu_guard();path=verify_bytes(mapping_receipt,True);mapping=json.loads(path.read_text());entries=validate_mapping(mapping)
 parent=verify_bytes(PARENT);original=json.loads(parent.read_text())
 # Parent is immutable content by descriptor; original JSON itself stays byte-identical.
 need(isinstance(original.get("outputs"),list)and len(original["outputs"])==6,"Original output shape changed")
 paired=[]
 for index in range(6):
  canonical,context=normalise(original["outputs"][index],PARENT,("outputs",str(index)),mapping);verify_bytes(canonical)
  paired.append(context)
 return mapping,{"mapping_receipt":receipt(mapping_receipt),"parent_manifest":dict(PARENT),"all_six_contexts":paired,"all_six_actual_bytes_verified":True,"original_json_unchanged":True,"allocation":allocation}

def normalize_edge(r,parent,field,mapping):
 return normalise(r,parent,field,mapping)
def exact_manifest_view(parent,obj,mapping):
 need(parent==PARENT,"Read-view requires one exact logical parent descriptor")
 validate_mapping(mapping)
 need(isinstance(obj,dict)and obj.get("job_id")=="13226"and obj.get("status")=="BBF110_INDEPENDENT_DEVELOPMENT_DIAGNOSIS_CONTENT_ACCEPTED","Historical manifest role changed")
 expected=[{"path":"runs/review_13226/"+name,"bytes":n,"sha256":sha}for name,n,sha in ROWS]
 need(obj.get("outputs")==expected,"Exactly six unchanged original output records required")
 view=copy.deepcopy(obj)
 contexts=[]
 for i,raw in enumerate(obj["outputs"]):
  canonical,context=normalise(raw,parent,("outputs",str(i)),mapping)
  view["outputs"][i]["path"]=canonical["path"];contexts.append(context)
 # The result is an in-memory read view. No disk write, score truncation or metadata removal.
 return view,contexts
class VerifiedContextReader:
 """Install only as one frozen library module's read(), restore in finally."""
 def __init__(self,mapping_receipt,reader,parent_aliases=()):
  self.mapping,self.verification=verify_mapping_receipt(mapping_receipt)
  self.reader=reader;self.parents={PARENT["path"]:dict(PARENT)};self.used=[]
  for item in parent_aliases:
   need(isinstance(item,dict)and item.get("logical")==PARENT,"Only explicit accepted exact-parent byte aliases allowed")
   physical=receipt(item["physical"])
   need((physical["bytes"],physical["sha256"])==(PARENT["bytes"],PARENT["sha256"]),"Read-view alias changes parent bytes")
   verify_bytes(physical);need(physical["path"]not in self.parents,"Duplicate read-view parent alias")
   self.parents[physical["path"]]=physical
 def __call__(self,path):
  key=str(Path(path));obj=None
  if key in self.parents:
   physical=self.parents[key];verify_bytes(physical);obj=self.reader(path)
   view,contexts=exact_manifest_view(PARENT,obj,self.mapping)
   self.used.append({"physical_parent":physical,"logical_parent":dict(PARENT),"contexts":contexts,"raw_JSON_changed":False})
   return view
  return self.reader(path)
 def proof(self):
  return {"mapping_verification":self.verification,"read_views_used":list(self.used),"scope":"EXACT_ONE_PARENT_SIX_OUTPUT_PATH_READ_VIEW_ONLY","raw_JSON_changed":False,"module_local_reader_only":True}
def restored_index(index,restore_root):
 declared=Path(restore_root);root=declared.resolve()
 need(declared.is_absolute()and declared==root and root.is_dir()and not declared.is_symlink(),"Exact nonsymlink restored directory required")
 need(root!=R and not ROOT.is_relative_to(root)and not root.is_relative_to(ROOT),"Restored-only root cannot be live scientific tree or its ancestor")
 need(isinstance(index,list),"Explicit restored receipt index required")
 entries={}
 for row in index:
  need(isinstance(row,dict)and set(row)=={"logical","restored_relative"},"Exact logical-to-restored index shape required")
  logical=receipt(row["logical"]);declared_relative=row["restored_relative"]
  need(isinstance(declared_relative,str)and bool(declared_relative),"Restored relative path string required")
  relative=Path(declared_relative)
  need(not relative.is_absolute()and relative.parts and relative.as_posix()==declared_relative and ".."not in relative.parts and "."not in relative.parts,"Unsafe restored relative path")
  physical=root/relative
  need(physical.resolve()==physical and not physical.is_symlink()and physical.is_relative_to(root),"Restored path escapes tree")
  key=(logical["path"],logical["bytes"],logical["sha256"]);need(key not in entries,"Duplicate restored logical identity")
  entries[key]=physical
 return root,entries
def restored_bytes(r,root,entries):
 logical=receipt(r);key=(logical["path"],logical["bytes"],logical["sha256"])
 need(key in entries,"Required exact receipt missing from restored-only index; no live fallback")
 physical=entries[key]
 need(physical.is_relative_to(root)and physical.is_file()and physical.resolve()==physical,"Missing restored-only bytes")
 h=hashlib.sha256();n=0
 with physical.open("rb")as handle:
  for b in iter(lambda:handle.read(1048576),b""):h.update(b);n+=len(b)
 need(n==logical["bytes"]and h.hexdigest()==logical["sha256"],"Restored-only byte identity differs")
 return physical
def verify_restored_mapping(mapping_receipt,restore_root,index):
 allocation=cpu_guard();root,entries=restored_index(index,restore_root)
 map_path=restored_bytes(mapping_receipt,root,entries);need(not(map_path.stat().st_mode&0o222),"Readonly restored BBF map metadata required");mapping=json.loads(map_path.read_text());validate_mapping(mapping)
 parent_path=restored_bytes(PARENT,root,entries);need(not(parent_path.stat().st_mode&0o222),"Readonly restored BBF original parent metadata required");obj=json.loads(parent_path.read_text())
 view,contexts=exact_manifest_view(PARENT,obj,mapping)
 child_paths=[]
 for i in range(6):
  child=expected_entry(i)["canonical_receipt"]
  child_paths.append(str(restored_bytes(child,root,entries)))
 return mapping,{"mapping_receipt":receipt(mapping_receipt),"restored_root":str(root),"mapping_restored_path":str(map_path),"parent_restored_path":str(parent_path),"children_restored_paths":child_paths,"contexts":contexts,"all_six_actual_bytes_verified":True,"all_read_paths_under_restored_root":True,"no_live_root_fallback":True,"raw_JSON_changed":False,"allocation":allocation}

def mapper_contract_shape(accepted,contracts):
 need(accepted.get("schema")=="exact-current-context-mapper-acceptance.v4"and accepted.get("status")=="EXACT_BBF6_RECOVERED5_NINE_ANNOTATIONS_ARCHIVE588_AND_EIGHT_SOURCE_ALIASES_MAPPER_CPU_ACCEPTED","Actual mapper source/content acceptance required")
 sources=accepted.get("source_files")
 need(isinstance(sources,list)and len(sources)==14 and {Path(r["path"]).name for r in sources}==PACKAGE_NAMES,"Exactly fourteen accepted mapper sources required")
 for r in sources:receipt(r)
 need(contracts.get("status")=="PASS"and contracts.get("tests")==CONTRACTS and contracts.get("failures")==0 and contracts.get("errors")==0,"Saved exact mapper software contracts did not pass")
 need(contracts.get("owned_python_compile_PASS")is True and contracts.get("bash_syntax_PASS")is True,"Actual mapper Python/bash syntax qualification missing")
 need(contracts.get("tested_source_files")==sources,"Saved tested sources differ from accepted mapper source universe")
 return sources
def verify_mapper_acceptance(acceptance_receipt,mapping_receipt=None,base_receipt=None,history_mapping_receipt=None,recovered_mapping_receipt=None,archive_mapping_receipt=None):
 allocation=cpu_guard();accepted=json.loads(verify_bytes(acceptance_receipt,True).read_text())
 contracts=json.loads(verify_bytes(accepted["contracts"],True).read_text());sources=mapper_contract_shape(accepted,contracts)
 for r in sources:verify_bytes(r,True)
 verify_bytes(contracts["log"],True)
 if mapping_receipt is not None:need(accepted.get("relative_receipt_context_mapping")==mapping_receipt,"Mapper accepted mapping differs")
 if base_receipt is not None:need(accepted.get("base_acceptance")==base_receipt,"Mapper accepted source base differs")
 verification=json.loads(verify_bytes(accepted["mapping_verification"],True).read_text())
 need(verification.get("mapping_receipt")==accepted.get("relative_receipt_context_mapping")and verification.get("parent_manifest")==PARENT and verification.get("all_six_actual_bytes_verified")is True and verification.get("original_json_unchanged")is True,"Actual saved parent/six verification proof missing")
 view=json.loads(verify_bytes(accepted["read_view_proof"],True).read_text())
 need(view.get("raw_JSON_changed")is False and view.get("module_local_reader_only")is True and any(x.get("logical_parent")==PARENT and len(x.get("contexts",[]))==6 for x in view.get("read_views_used",[])),"Actual saved six-output read-view proof missing")
 jid=accepted.get("allocation",{}).get("job_id");need(isinstance(jid,str)and jid.isdigit(),"Accepted mapper CPU job identity missing")
 raw=subprocess.check_output(["sacct","-X","-j",jid,"--noheader","--parsable2","--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocTRES,User%64,Account%64,JobName%100,Partition%64"],text=True)
 rows=[x.split("|")for x in raw.splitlines()if x.split("|",1)[0]==jid]
 need(len(rows)==1 and len(rows[0])>=9,"Unique accepted mapper terminal accounting required")
 job,state,exitcode,elapsed,tres,user,account,name,partition=rows[0][:9]
 need(state=="COMPLETED"and exitcode=="0:0"and elapsed.isdigit()and user=="u21111210118"and account=="u21111210118"and partition=="organ"and name=="test9_exact_context_v4","Mapper actual terminal owner/state differs")
 vals=strict_tres(tres)
 def n(k):
  return vals.get(k,0)
 need(n("cpu")>=1 and max(n("gres/gpu"),sum(n(k)for k in vals if k.startswith("gres/gpu:")))==0,"Mapper accepted job is not real pureCPU")
 import historical_annotation_context as history
 if history_mapping_receipt is not None:need(accepted.get("external_historical_receipt_context_mapping")==history_mapping_receipt,"Mapper accepted history map differs")
 saved_history=json.loads(verify_bytes(accepted["historical_annotation_verification"],True).read_text())
 need(saved_history.get("mapping_receipt")==accepted.get("external_historical_receipt_context_mapping")and saved_history.get("parent_manifest")==history.PARENT and saved_history.get("historical_annotation_n")==9 and saved_history.get("raw_historical_bytes_accepted")is False,"Actual saved nine-annotation parent verification missing")
 history_view=json.loads(verify_bytes(accepted["historical_annotation_read_view_proof"],True).read_text())
 need(history_view.get("raw_JSON_changed")is False and history_view.get("module_local_reader_only")is True and any(x.get("logical_parent")==history.PARENT and len(x.get("contexts",[]))==9 for x in history_view.get("read_views_used",[])),"Actual saved nine-scalar read-view missing")
 verify_mapping_receipt(accepted["relative_receipt_context_mapping"])
 history.verify_mapping_receipt(accepted["external_historical_receipt_context_mapping"])
 import recovered_five_context as recovered
 if recovered_mapping_receipt is not None:need(accepted.get("current_recovered_relative_receipt_context_mapping")==recovered_mapping_receipt,"Mapper accepted recovered-five map differs")
 saved_recovered=json.loads(verify_bytes(accepted["current_recovered_verification"],True).read_text())
 need(saved_recovered.get("mapping_receipt")==accepted.get("current_recovered_relative_receipt_context_mapping")and saved_recovered.get("parent_manifest")==recovered.PARENT and saved_recovered.get("all_five_actual_bytes_verified")is True and saved_recovered.get("original_json_unchanged")is True,"Actual saved five current evidence byte verification missing")
 recovered_view=json.loads(verify_bytes(accepted["current_recovered_read_view_proof"],True).read_text())
 need(recovered_view.get("raw_JSON_changed")is False and recovered_view.get("module_local_reader_only")is True and any(x.get("logical_parent")==recovered.PARENT and len(x.get("contexts",[]))==5 for x in recovered_view.get("read_views_used",[])),"Actual saved five current evidence read-view missing")
 recovered.verify_mapping_receipt(accepted["current_recovered_relative_receipt_context_mapping"])
 import archive_member_context as archive
 if archive_mapping_receipt is not None:need(accepted.get("archive_member_receipt_context_mapping")==archive_mapping_receipt,"Mapper accepted archive map differs")
 archive.verify_saved_verification(accepted,lambda r:verify_bytes(r,True))
 archive_view=json.loads(verify_bytes(accepted["archive_member_read_view_proof"],True).read_text())
 need(archive_view.get("raw_JSON_changed")is False and archive_view.get("module_local_reader_only")is True and all(any(x.get("logical_parent")==s["parent_manifest"]and len(x.get("contexts",[]))==s["member_count"]for x in archive_view.get("read_views_used",[]))for s in archive.ARCHIVES),"Actual saved two archive namespace read views missing")
 archive.verify_mapping_receipt(accepted["archive_member_receipt_context_mapping"])
 import context_consumer as consumer
 actualbase,actualclosure=consumer.source_bundle(accepted["base_acceptance"],accepted["relative_receipt_context_mapping"],accepted["external_historical_receipt_context_mapping"],lambda r:verify_bytes(r,True),accepted["current_recovered_relative_receipt_context_mapping"],accepted["archive_member_receipt_context_mapping"])
 need(accepted.get("source_closure")==actualbase.get("source_closure"),"Actual mapper accepted closure differs from actual SourceV10 closure")
 import finite_source_context as finite
 finite.verify_saved_alias_proofs(accepted,actualbase,actualclosure,lambda r:verify_bytes(r,True))
 return accepted,{"mapper_acceptance":receipt(acceptance_receipt),"contracts":accepted["contracts"],"source_files":sources,"mapping_verification":accepted["mapping_verification"],"read_view_proof":accepted["read_view_proof"],"actual_terminal_accounting":{"raw":raw,"row":rows[0],"allocated_GPUs":0},"verification_allocation":allocation}

def strict_tres(tres):
 values={}
 need(isinstance(tres,str),"Actual numeric TRES string required")
 for token in tres.split(","):
  need("="in token,"Malformed actual TRES token");key,value=token.split("=",1)
  need(key and value and key not in values,"Duplicate/malformed actual allocated TRES")
  if key=="cpu"or key=="gres/gpu"or key.startswith("gres/gpu:"):
   need(re.fullmatch(r"[0-9]+",value),"Noninteger actual CPU/GPU allocated TRES");values[key]=int(value)
  else:values[key]=value
 need(values.get("cpu",0)>=1,"Actual CPU allocation required")
 need(max(values.get("gres/gpu",0),sum(v for k,v in values.items()if k.startswith("gres/gpu:")))==0,"Actual GPU0 allocation required")
 return values
