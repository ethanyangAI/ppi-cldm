#!/usr/bin/env python3
"""Finite Source-delivery projections. Generic readers and source identities stay unchanged.

Only the fixed OWN15 semantics dependency is executable. Historical metadata is
provenance data; restored bytes are obtained exclusively through StrictIndex.
"""
import collections,hashlib,json,math,os,re,stat,sys,types
from pathlib import Path

R=Path("/lustre/users/u21111210118/projects/test9")
SEMANTICS_NAME="qualified_source_semantics.py"
SEMANTICS_FP=(344832,"761829c3cbf2dc4bf1f790c2ec80b7fd0fdb2802adf2854d69360164114fa516")
SCHEMA="finite-final-source-delivery-context.v2"
STATUS="EXACT_FINITE_SOURCE_DELIVERY_PROJECTIONS_VERIFIED_NOT_NEW_SCIENCE_OR_SOURCE_ACCEPTANCE"
PAIRS=(
 ("vendor_example_opaque_leaf_proof","vendor_example_opaque_aliases"),
 ("finite_worker_control_proof","finite_worker_control_aliases"),
 ("inventory_history_opaque_leaf_proof","inventory_history_opaque_aliases"),
 ("archive_parent_history_opaque_leaf_proof","archive_parent_history_opaque_aliases"),
 ("relative_diagnostic_history_opaque_leaf_proof","relative_diagnostic_history_opaque_aliases"),
 ("parent_diagnostic_history_opaque_leaf_proof","parent_diagnostic_history_opaque_aliases"))
PURE_NAMES=(
 "inventory_history_document_shape","inventory_history_proof_shape",
 "archive_parent_history_document_shape","archive_parent_history_proof_shape",
 "relative_diagnostic_history_document_shape","relative_diagnostic_history_proof_shape",
 "parent_diagnostic_history_document_shape","parent_diagnostic_history_proof_shape",
 "parent_diagnostic_history_source_coverage",
 "catalog_msa_gap_projection_native","catalog_msa_gap_projection_shape")
META_KEYS={"path","bytes","inode","mtime_ns","ctime_ns","mode","dev","nlink","uid","gid"}
BINDING_KEYS={"schema","root_owned","producer","semantics_source","stage_acceptance",
 "late_source_publication","transport_aliases","additional_control_receipts","source_routes"}
PRODUCER_KEYS={"acceptance","context_adapter_acceptance","source_inclusion","source_closure"}
MAX_CONTROL=20*1024*1024
MAX_SOURCE_CLOSURE=100*1024*1024

def need(value,message):
 if not value:raise ValueError(message)

def rid(r):
 need(type(r)is dict and set(r)=={"path","bytes","sha256"},"Exact finite full receipt required")
 need(type(r["path"])is str and Path(r["path"]).is_absolute()
      and ".."not in Path(r["path"]).parts,"Absolute finite receipt required")
 need(type(r["bytes"])is int and r["bytes"]>=0 and type(r["sha256"])is str
      and re.fullmatch("[0-9a-f]{64}",r["sha256"])is not None,"Invalid finite receipt scalar")
 return(r["path"],r["bytes"],r["sha256"])

def subset(r):
 need(isinstance(r,dict)and {"path","bytes","sha256"}<=set(r),"Receipt subset required")
 return {k:r[k]for k in("path","bytes","sha256")}

def fp(r):
 rid(subset(r));return(r["bytes"],r["sha256"])

def strict_json(raw):
 need(type(raw)in(bytes,str),"Strict JSON text required")
 if type(raw)is bytes:raw=raw.decode("utf-8","strict")
 def pairs(items):
  out={}
  for k,v in items:
   need(k not in out,"Duplicate finite JSON key");out[k]=v
  return out
 def invalid(value):raise ValueError("Nonfinite finite JSON number")
 def number(value):
  v=float(value);need(math.isfinite(v),"Overflow finite JSON number");return v
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid,parse_float=number)

def exact(left,right):
 return json.dumps(left,sort_keys=True,separators=(",",":"),allow_nan=False)==json.dumps(right,sort_keys=True,separators=(",",":"),allow_nan=False)

def metadata_shape(value,path=None,kind=None,mode=None):
 need(type(value)is dict and set(value)==META_KEYS and type(value["path"])is str
      and all(type(value[k])is int and value[k]>=0 for k in META_KEYS-{"path"}),"Exact original native metadata required")
 if path is not None:need(value["path"]==str(path),"Native metadata path differs")
 if kind=="file":need(stat.S_ISREG(value["mode"])and value["nlink"]==1,"Single-link regular native record required")
 if kind=="directory":need(stat.S_ISDIR(value["mode"])and value["nlink"]==2,"Exact finite directory native record required")
 if kind=="link":need(stat.S_ISLNK(value["mode"])and value["nlink"]==1,"Exact finite link native record required")
 if mode is not None:need(stat.S_IMODE(value["mode"])==mode,"Exact native permission differs")
 return value

def native(path):
 s=os.lstat(str(path))
 return dict(path=str(path),bytes=s.st_size,inode=s.st_ino,mtime_ns=s.st_mtime_ns,
             ctime_ns=s.st_ctime_ns,mode=s.st_mode,dev=s.st_dev,nlink=s.st_nlink,uid=s.st_uid,gid=s.st_gid)

def _safe_current(path):
 p=Path(path)
 need(p.is_absolute()and p.is_relative_to(R)and p.resolve()==p and not p.is_symlink(),
      "Finite current input outside ordinary nonlink authority")
 return p

def receipt_nodes(obj,trail=()):
 if isinstance(obj,dict):
  if {"path","bytes","sha256"}<=set(obj):
   r=subset(obj);rid(r);yield r,trail
  for k,v in obj.items():yield from receipt_nodes(v,trail+(str(k),))
 elif isinstance(obj,list):
  for i,v in enumerate(obj):yield from receipt_nodes(v,trail+(str(i),))

def _load_semantics_bytes(raw,receipt):
 need(Path(receipt["path"]).name==SEMANTICS_NAME and fp(receipt)==SEMANTICS_FP,
      "Only the exact owned qualified G semantics dependency is executable")
 need(type(raw)is bytes and(len(raw),hashlib.sha256(raw).hexdigest())==SEMANTICS_FP,
      "Qualified G semantics whole bytes differ")
 module=types.ModuleType("qualified_final_source_pure_semantics")
 module.__file__=receipt["path"]
 module.__package__=None
 exec(compile(raw,receipt["path"],"exec",dont_inherit=True),module.__dict__)
 need(all(callable(getattr(module,n,None))for n in PURE_NAMES),"Closed pure semantics exports missing")
 exports={n:getattr(module,n)for n in PURE_NAMES}
 pure_helpers=("key","kind","eligible_public","receipt_edges","_strict_vendor_json","_fixed_history_contexts",
  "parent_diagnostic_history_source_children","_catalog_msa_controls","_catalog_msa_old_fingerprint","_catalog_msa_projection")
 constants=("PACKAGE_NAMES","_FIXED_HISTORY_MAPPING_PARENTS","_WORKER_BASE","_WORKER_CLOSURE","_WORKER_PARENTS",
  "_WORKER_TABLE","_WORKER_MODULE","_WORKER_ROLE","_VENDOR_EXAMPLE_PARENT","_VENDOR_EXAMPLE_LEAF",
  "_VENDOR_EXAMPLE_MODULE","_VENDOR_EXAMPLE_ROLE")
 for n in pure_helpers+constants:exports[n]=getattr(module,n)
 for prefix in("_HISTORY","_ARCHIVE_PARENT_HISTORY","_RELATIVE_DIAGNOSTIC_HISTORY","_PARENT_DIAGNOSTIC_HISTORY"):
  for suffix in("_LEAF","_BASE","_ROLE","_FIELD","_MODULES","_PROOF_SCHEMA","_PROOF_STATUS","_ALIAS_STATUS","_PRODUCER","_SOFTWARE"):
   if hasattr(module,prefix+suffix):exports[prefix+suffix]=getattr(module,prefix+suffix)
 for n in("_CATALOG_MSA_ROLE","_CATALOG_MSA_CATALOG","_CATALOG_MSA_ACCEPTANCE","_CATALOG_MSA_BASE_C",
           "_CATALOG_MSA_FIELD","_CATALOG_MSA_DEFINITIONS","_CATALOG_MSA_MODULES","_CATALOG_MSA_KEYS","_CATALOG_MSA_EDGE_SEAL","_CATALOG_MSA_ROOT_DECISION"):
  exports[n]=getattr(module,n)
 # No live Scope, resolver, verify, rec, cpu, Core or saved_inputs export.
 return types.SimpleNamespace(**exports)

def _binding_shape(binding):
 need(type(binding)is dict and set(binding)==BINDING_KEYS and binding["schema"]==SCHEMA
      and binding["root_owned"]is True,"Closed Root finite Source binding required")
 need(type(binding["producer"])is dict and set(binding["producer"])==PRODUCER_KEYS,"Whole A/CA/I/C producer descriptors required")
 for r in binding["producer"].values():
  rid(r);need(r["path"]!=SOURCE_TEXT_ORIGIN,"Original TXT cannot be an operative producer/control")
 rid(binding["semantics_source"]);need(Path(binding["semantics_source"]["path"]).name==SEMANTICS_NAME
      and fp(binding["semantics_source"])==SEMANTICS_FP,"Wrong Source semantics binding")
 for k in("stage_acceptance","late_source_publication"):rid(binding[k])
 need(type(binding["transport_aliases"])is list and type(binding["additional_control_receipts"])is list,
      "Explicit finite transport/control rows required")
 seen={}
 for row in binding["transport_aliases"]:
  need(type(row)is dict and set(row)=={"original","archived","status","role"},"Closed finite transport row required")
  k=rid(row["original"]);rid(row["archived"])
  need(row["original"]["path"]!=SOURCE_TEXT_ORIGIN and row["archived"]["path"]!=SOURCE_TEXT_ORIGIN,"Original TXT cannot be a transport alias")
  need(fp(row["original"])==fp(row["archived"])and row["status"]=="READONLY_BYTE_IDENTICAL_ALIAS"
       and row["role"]in("FINITE_SOURCE_CONTROL_BYTES","FINITE_SOURCE_JSON_BYTES"),"Finite transport byte identity/role changed")
  need(Path(row["archived"]["path"]).name.endswith(".OPAQUE.txt"),"Opaque transport must be a physical TXT file")
  need(k not in seen or exact(seen[k],row),"Conflicting finite transport identity");seen[k]=row
 for r in binding["additional_control_receipts"]:rid(r)
 need(type(binding["source_routes"])is list,"Explicit finite Source route list required")
 for row in binding["source_routes"]:
  need(type(row)is dict and set(row)=={"original","selected_physical","repository_relative"},"Closed selected Source route row required")
  rid(row["original"]);rid(row["selected_physical"])
  need(type(row["repository_relative"])is str,"Selected Source destination required")
 return seen

class CurrentInputs:
 """Only the closed staged input phases may enroll a file before its first IO."""
 def __init__(self):self.original={};self.receipts={};self.payloads={}
 def read(self,receipt,limit=MAX_CONTROL):
  k=rid(receipt);need(receipt["path"]!=SOURCE_TEXT_ORIGIN,"Original TXT is nonoperative provenance, never a live input")
  p=_safe_current(receipt["path"])
  before=native(p);metadata_shape(before,p,"file",0o444)
  need(before["bytes"]==receipt["bytes"]and before["bytes"]<=limit,"Finite control byte bound differs")
  if str(p)in self.original:need(self.original[str(p)]==before,"Finite input native metadata changed")
  else:self.original[str(p)]=before
  raw=p.read_bytes()
  need((len(raw),hashlib.sha256(raw).hexdigest())==fp(receipt),"Finite control whole bytes changed")
  need(native(p)==before,"Finite input native metadata changed during read")
  self.receipts[k]=receipt;self.payloads[k]=raw;return raw
 def json(self,receipt,limit=MAX_CONTROL):return strict_json(self.read(receipt,limit))
 def enroll_native(self,expected):
  path=_safe_current(expected["path"]);kind="directory"if stat.S_ISDIR(expected["mode"])else"file"
  metadata_shape(expected,path,kind,0o555 if kind=="directory"else 0o444)
  need(native(path)==expected,"Finite producer original native provenance changed before first input read")
  if str(path)in self.original:need(self.original[str(path)]==expected,"Conflicting original finite native baseline")
  else:self.original[str(path)]=dict(expected)
 def end(self):
  for k,r in self.receipts.items():
   p=_safe_current(r["path"]);need(native(p)==self.original[str(p)],"Finite input native drift before final readback")
   raw=p.read_bytes();need((len(raw),hashlib.sha256(raw).hexdigest())==fp(r),"Finite input bytes drifted after projection")
  self.native_end()
 def native_end(self):
  for path,expected in self.original.items():
   need(native(path)==expected,"Finite Source original native union drifted")

def _payload(payloads,r):
 k=rid(r);need(k in payloads,"Required exact indexed/current Source input missing")
 raw=payloads[k];need(type(raw)is bytes and(len(raw),hashlib.sha256(raw).hexdigest())==fp(r),
                        "Required Source input whole bytes differ")
 return raw

def _json(payloads,r):return strict_json(_payload(payloads,r))

def _graph_shape(binding,payloads,g):
 refs=binding["producer"];a=_json(payloads,refs["acceptance"]);ca=_json(payloads,refs["context_adapter_acceptance"])
 i=_json(payloads,refs["source_inclusion"]);c=_json(payloads,refs["source_closure"])
 need(a.get("schema")=="final-source-closure-acceptance.v3"and a.get("status")=="FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED"
      and a.get("source_issues")==0 and a.get("source_staged")is False and a.get("source_published")is False
      and a.get("ACTIVE_changed")is False and a.get("whole6_source_prepost_PASS")is True
      and a.get("original_and_frozen_owned_bytes_identical")is True and a.get("conditional_runtime_prepost_PASS")is True,
      "Actual Source producer acceptance required")
 need(i.get("schema")=="benchmark-source-inclusion.v3"and i.get("status")=="SOURCE_INCLUSION_AUDIT_PASS"
      and i.get("applied")is False and i.get("issues")==[]and i.get("formal_array_job_id")=="13260","Actual nonstaging Source inclusion required")
 need(c.get("schema")=="final-source-receipt-closure.v2"
      and c.get("status")=="EXACT_NEW_SOURCE_DEPENDENCIES_WITH_INHERITED_TYPED_HISTORY","Actual current Source C required")
 need(ca.get("schema")=="final-source-materialized-context-read-view-acceptance.v3"
      and ca.get("status")=="FINAL_CURRENT_SOURCE_MATERIALIZED_FIVE_PARENT_CONTEXT_AND_DERIVED_V2_CPU_ACCEPTED_NOT_STAGED_NOT_PUBLISHED"
      and ca.get("raw_JSON_changed")is False and ca.get("unknown_relative_or_current_external_permission_added")is False
      and ca.get("source_staged")is False and ca.get("published")is False and ca.get("ACTIVE_changed")is False
      and ca.get("whole6_source_prepost_PASS")is True and ca.get("original_and_frozen_owned_bytes_identical")is True
      and ca.get("conditional_runtime_prepost_PASS")is True,
      "Actual strict Source adapter required")
 need(a["source_inclusion"]==refs["source_inclusion"]and a["source_closure"]==refs["source_closure"]
      and i["source_receipt_closure"]==refs["source_closure"]
      and ca["actual_new_library_acceptance"]==refs["acceptance"]
      and ca["source_inclusion"]==refs["source_inclusion"]and ca["source_closure"]==refs["source_closure"],
      "Whole A/CA/I/C pointers forked")
 out=Path(refs["acceptance"]["path"]).parent
 for name,basename in(("context_adapter_acceptance","context_adapter_acceptance.json"),
                       ("source_inclusion","source_inclusion_final.json"),("source_closure","source_receipt_closure_final.json")):
  need(refs[name]["path"]==str(out/basename),"Source graph owned path changed")
 allocation=a["allocation"]
 need(type(allocation)is dict and type(allocation.get("job_id"))is str and allocation["job_id"].isdigit()
      and type(allocation.get("allocated_CPUs"))is int and allocation["allocated_CPUs"]>=1
      and type(allocation.get("allocated_gpus"))is int and allocation["allocated_gpus"]==0
      and ca["allocation"]==allocation and i["allocation"]==allocation,"Actual same Source CPU allocation required")
 runners=i.get("runner_source_snapshot")
 need(type(runners)is list and len(runners)==6 and {Path(r["path"]).name for r in runners}==set(g.PACKAGE_NAMES),"Whole actual I.runner6 required")
 main=next(r for r in runners if Path(r["path"]).name=="final_source_closure.py")
 need(fp(main)==SEMANTICS_FP,"Actual I runner main differs from qualified semantics")
 for pk,ik in PAIRS:
  for obj in(a,ca,i,c):need(obj.get(pk)==a.get(pk)and obj.get(ik)==a.get(ik),"Six-family A/CA/I/C pointers differ")
  rid(a[pk]);rid(a[ik])
  need(a[pk]["path"]==str(out/(pk+".json"))and a[ik]["path"]==str(out/(ik+".json")),"Six-family actual owned paths differ")
 need(a.get("source_entries")==len(i["files"]),"Actual Source row denominator differs")
 return a,ca,i,c

def _history_definitions(g):
 return(
  ("inventory13299","_HISTORY",g.inventory_history_document_shape,g.inventory_history_proof_shape),
  ("archive13298","_ARCHIVE_PARENT_HISTORY",g.archive_parent_history_document_shape,g.archive_parent_history_proof_shape),
  ("relative13295","_RELATIVE_DIAGNOSTIC_HISTORY",g.relative_diagnostic_history_document_shape,g.relative_diagnostic_history_proof_shape),
  ("parent13290","_PARENT_DIAGNOSTIC_HISTORY",g.parent_diagnostic_history_document_shape,g.parent_diagnostic_history_proof_shape))

def history_graph_shape(saved,closure):
 """Pure ordered actual DATA edge correspondence, without any target read."""
 leaf=saved["original_diagnostic_data"]
 expected=[dict(receipt=leaf,parent=x["parent_manifest"]["path"],field=list(x["field"]),
  module=x["module"],physical=x["physical"],resolution_basis=x["resolution_basis"],role=x["role"],
  raw_bytes_preserved=True,receipt_children_interpreted=False,source_or_configuration_promotion=False)
  for x in saved["observations"]]
 selected=[e for e in closure["edges"]if isinstance(e.get("receipt"),dict)
  and(e["receipt"].get("path")==leaf["path"]or(e["receipt"].get("bytes"),e["receipt"].get("sha256"))==fp(leaf))]
 need(exact(selected,expected),"Actual ordered history DATA graph differs from complete saved observations")
 return True

def vendor_saved_shape(g,saved,index,allocation,raw):
 """Pure equivalent of the fixed vendor saved-object contract, never its live API."""
 need(type(saved)is dict and type(index)is dict,"Whole vendor proof/index required")
 need(saved.get("schema")=="exact-vendor-example-opaque-data-leaf.v1"
      and saved.get("status")=="EXACT_PARENT18_FIELD15_VENDOR_DLLL52_DATA_BYTES_PRESERVED_CPU_VERIFIED","Wrong vendor proof schema")
 need(saved.get("allocation")==allocation and saved.get("parent_manifest")==g._VENDOR_EXAMPLE_PARENT
      and saved.get("original_data_leaf")==g._VENDOR_EXAMPLE_LEAF
      and saved.get("source_field")==["15"]and saved.get("module")==g._VENDOR_EXAMPLE_MODULE
      and saved.get("role")==g._VENDOR_EXAMPLE_ROLE,"Fixed vendor context changed")
 copy=saved["archived_opaque_data"];rid(copy)
 need(fp(copy)==fp(g._VENDOR_EXAMPLE_LEAF)and(len(raw),hashlib.sha256(raw).hexdigest())==fp(copy),
      "Whole preserved vendor DATA bytes differ")
 p=Path(copy["path"])
 need(p.parent.name=="opaque_vendor_example_bytes"and p.name==g._VENDOR_EXAMPLE_LEAF["sha256"]+"_example_resnet_log.OPAQUE.txt",
      "Fixed vendor copy destination changed")
 need(saved["exact_alias_index"]["path"]==str(p.parent.parent/"vendor_example_opaque_aliases.json"),"Vendor index path changed")
 for before,after,receipt,mode in(("parent_metadata_before","parent_metadata_after",g._VENDOR_EXAMPLE_PARENT,0o444),
                                ("original_metadata_before","original_metadata_after",g._VENDOR_EXAMPLE_LEAF,0o664)):
  metadata_shape(saved[before],receipt["path"],"file",mode)
  need(saved[before]==saved[after]and saved[before]["bytes"]==receipt["bytes"],"Vendor original native provenance forked")
 metadata_shape(saved["preserved_metadata"],copy["path"],"file",0o444)
 need(saved["preserved_metadata"]["bytes"]==copy["bytes"],"Vendor saved copy native bytes differ")
 need(type(saved.get("authorized_observation_n"))is int and saved["authorized_observation_n"]>=1
      and saved.get("vendor_inventory_row_n")==18 and saved.get("vendor_stream_record_n")==52,"Fixed vendor denominator changed")
 lines=raw.decode("utf-8","strict").splitlines()
 need(len(lines)==52 and all(line.startswith("DLLL ")for line in lines),"Vendor52 documentary DLLL lines required")
 types_count=collections.Counter()
 for line in lines:
  record=g._strict_vendor_json(line[5:])
  need(isinstance(record,dict)and type(record.get("type"))is str and record["type"]in("LOG","METADATA"),"Vendor documentary record kind differs")
  types_count[record["type"]]+=1
 need(set(types_count)=={"LOG","METADATA"}and saved["vendor_stream_record_types"]==dict(sorted(types_count.items())),"Vendor documentary record type projection differs")
 true=("original_bytes_and_metadata_unchanged","original_permission_unchanged","preserved_copy_readonly_fsynced_and_byte_identical")
 false=("original_JSON_or_parent_rewritten","receipt_children_interpreted","public_source_or_configuration_promoted",
        "scientific_content_accepted","generic_JSON_parser_or_context_permissions_changed","future_package_index_and_isolated_restore_acceptance")
 for k in true:need(saved.get(k)is True,"Vendor immutable flag changed")
 for k in false:need(saved.get(k)is False,"Vendor promotion flag changed")
 expected=dict(schema="exact-resource-aliases.v2",aliases=[dict(original=dict(g._VENDOR_EXAMPLE_LEAF),archived=copy,
                  status="READONLY_BYTE_IDENTICAL_ALIAS",role=g._VENDOR_EXAMPLE_ROLE)],historical_unresolved=[])
 # The source alias schema has an explicit status and documentary flags; compare every own field below.
 expected.update(status="EXACT_VENDOR_EXAMPLE_OPAQUE_DATA_BYTE_ALIAS_CPU_VERIFIED",
                 separate_original_JSON_physical_package_entry_forbidden=True,scientific_or_source_acceptance=False)
 need(exact(index,expected),"Fixed vendor alias bytes/context changed")
 proof_keys={"schema","status","parent_manifest","original_data_leaf","source_field","module","role",
  "archived_opaque_data","parent_metadata_before","parent_metadata_after","original_metadata_before",
  "original_metadata_after","preserved_metadata","authorized_observation_n","vendor_inventory_row_n",
  "vendor_stream_record_n","vendor_stream_record_types","allocation","exact_alias_index"}|set(true)|set(false)
 need(set(saved)==proof_keys,"Closed vendor saved proof keyset differs")
 return True

def worker_saved_shape(g,saved,index,allocation,payloads,closure):
 """Pure 23-slot/22-copy semantics; original worker paths are never accessed."""
 need(type(saved)is dict and saved.get("schema")=="exact-finite-worker-control-alias-preservation.v1"
      and saved.get("status")=="EXACT_BASE23_CONTEXTS_22_NORMAL_JSON_CONTROL_COPIES_CPU_VERIFIED","Wrong worker proof")
 need(saved.get("allocation")==allocation and saved.get("accepted_base")==g._WORKER_BASE
      and saved.get("accepted_base_closure")==g._WORKER_CLOSURE
      and saved.get("raw_parent_manifests")==g._WORKER_PARENTS,"Worker authority descriptors forked")
 table=g._WORKER_TABLE
 need(len(table)==23 and len({rid(x["logical"])for x in table})==23
      and len({rid(x["canonical"])for x in table})==22,"Qualified worker table denominator differs")
 need(saved.get("fixed_context_n")==23 and saved.get("canonical_target_n")==22
      and saved.get("observed_context_slots")==sorted(x["index"]for x in table),"Worker complete slot coverage missing")
 need(saved.get("authority_metadata_before")==saved.get("authority_metadata_after")
      and saved.get("source_metadata_before")==saved.get("source_metadata_after"),"Worker original provenance changed")
 source=saved["source_metadata_before"]
 need(type(source)is list and [x["index"]for x in source]==sorted(x["index"]for x in table),"All23 worker metadata records required")
 for item in source:
  need(type(item)is dict and set(item)=={"index","metadata"}and type(item["index"])is int,"Closed worker metadata slot required")
  row=next(x for x in table if x["index"]==item["index"]);m=item["metadata"]
  need(type(m)is dict and set(m)=={"logical","canonical","link","link_text"}and m["link_text"]==row["link_text"],"Worker exact link documentary binding differs")
  metadata_shape(m["logical"],row["logical"]["path"],"file",0o664)
  metadata_shape(m["canonical"],row["canonical"]["path"],"file",0o664)
  metadata_shape(m["link"],row["link_path"],"link")
  need(m["logical"]["bytes"]==row["logical"]["bytes"]and m["canonical"]["bytes"]==row["canonical"]["bytes"]
       and m["link"]["bytes"]==len(row["link_text"].encode("utf-8")),"Worker original native size/link-text binding changed")
 out=Path(saved["output_root_as_scalar"])
 need(out.is_absolute()and out.is_relative_to(R)and ".."not in out.parts,"Worker output root scalar outside authority")
 rid(saved["exact_alias_index"])
 need(saved["exact_alias_index"]["path"]==str(out/"finite_worker_control_aliases.json"),"Worker alias index output path changed")
 targets=saved["canonical_targets"];need(type(targets)is list and len(targets)==22,"Whole22 worker targets required")
 keys=sorted({g.key(x["canonical"])for x in table});copies={};children={}
 for slot,(key,target)in enumerate(zip(keys,targets)):
  row=next(x for x in table if g.key(x["canonical"])==key);r=target["preserved"];rid(r)
  need(r["path"]==str(Path(saved["output_root_as_scalar"])/"finite_worker_control_bytes"/("%03d_%s_worker.json"%(slot,row["canonical"]["sha256"])))
       and fp(r)==fp(row["canonical"]),"Worker canonical/copy mapping changed")
  need((target["canonical_path_as_scalar"],target["bytes_as_scalar"],target["sha256_as_scalar"])==rid(row["canonical"]),"Worker canonical scalar projection changed")
  metadata_shape(target["preserved_metadata"],r["path"],"file",0o444)
  need(target["preserved_metadata"]["bytes"]==r["bytes"],"Worker copy saved native bytes differ")
  obj=_json(payloads,r)
  expected=[dict(receipt=dict(child),field=list(field))for child,field in g.receipt_edges(obj)]
  need(exact(target["child_receipts"],expected),"Worker normal children lost or changed")
  copies[key]=r;children[key]=expected
 metadata_shape(saved["copy_directory_metadata"],str(Path(saved["output_root_as_scalar"])/"finite_worker_control_bytes"),"directory",0o555)
 observations=saved["observations"]
 need(type(observations)is list and len(observations)==saved.get("authorized_observation_n")and observations,"Actual worker observations required")
 observed=[]
 for x in observations:
  need(type(x)is dict and set(x)=={"index","receipt","parent","field","module","physical"},"Worker observation shape differs")
  need(type(x["index"])is int,"Worker observation slot must be an integer")
  matches=[row for row in table if exact(row["logical"],x["receipt"])]
  need(len(matches)==1,"Worker full logical identity changed");row=matches[0]
  need(x["index"]==row["index"]and x["parent"]==row["parent"]["path"]and x["field"]==row["field"]
       and x["module"]==g._WORKER_MODULE and x["physical"]==copies[g.key(row["canonical"])],"Worker exact context changed")
  observed.append(row["index"])
 need(set(observed)==set(x["index"]for x in table),"Worker actual23 contexts incomplete")
 expected_aliases=[dict(original=dict(row["logical"]),archived=copies[g.key(row["canonical"])],
                   status="READONLY_BYTE_IDENTICAL_ALIAS",role=g._WORKER_ROLE)for row in table]
 need(index.get("schema")=="exact-resource-aliases.v2"and index.get("status")=="EXACT_FIXED23_WORKER_CONTROL_ALIASES_CPU_VERIFIED"
      and index.get("aliases")==expected_aliases and index.get("historical_unresolved")==[]
      and index.get("canonical_target_n")==22,"Worker exact alias index forked")
 for k in("separate_original_symlink_physical_package_entry_forbidden","normal_JSON_receipt_children_retained"):
  need(index.get(k)is True,"Worker indexed transport policy changed")
 need(index.get("scientific_or_source_acceptance")is False,"Worker metadata promoted")
 for k in("original_worker_modes_unchanged_0664","all_inputs_copies_readlinks_pre_end_afteroutput_bound",
          "every_occurrence_authorized_before_seen","normal_JSON_receipt_children_retained","child_parent_is_original_logical_worker"):
  need(saved.get(k)is True,"Worker proof immutable flag changed")
 for k in("generic_reader_or_17_parent_permission_changed","source_or_scientific_promotion"):
  need(saved.get(k)is False,"Worker generic permission/promotion changed")
 worker_edges=[e for e in closure["edges"]if e.get("role")==g._WORKER_ROLE]
 need(len(worker_edges)==len(observations),"Worker actual C occurrence denominator differs")
 for e,x in zip(worker_edges,observations):
  need(all(e.get(k)==v for k,v in x.items()),"Worker C ordered occurrence differs")
 authority=saved["authority_metadata_before"]
 need(type(authority)is dict and set(authority)=={"base","closure","parents"}
      and type(authority["parents"])is list and len(authority["parents"])==2,"Closed worker original authority metadata required")
 for value,receipt in [(authority["base"],g._WORKER_BASE),(authority["closure"],g._WORKER_CLOSURE)]:
  metadata_shape(value,receipt["path"],"file",0o444);need(value["bytes"]==receipt["bytes"],"Worker authority metadata bytes differ")
 for value,receipt in zip(authority["parents"],g._WORKER_PARENTS):
  metadata_shape(value,receipt["path"],"file",0o664);need(value["bytes"]==receipt["bytes"],"Worker raw parent metadata bytes differ")
 base=_json(payloads,g._WORKER_BASE);accepted=_json(payloads,g._WORKER_CLOSURE)
 need(base.get("source_closure")==g._WORKER_CLOSURE and accepted.get("schema")=="benchmark-source-receipt-closure.v1",
      "Exact BaseA/BaseC worker authority objects required")
 scope=[]
 for row in table:
  need(accepted["edges"][row["index"]]==row["base_edge"] and row["base_edge"]["receipt"]==row["logical"]
       and row["base_edge"]["physical"]==row["logical"] and row["base_edge"]["parent"]==row["parent"]["path"]
       and row["base_edge"]["field"]==row["field"] and row["base_edge"]["role"]=="EXACT_TEXT_RECEIPT_READBACK"
       and row["parent"]in g._WORKER_PARENTS,"Exact BaseC23/raw-parent context differs")
  scope.append(dict(index=row["index"],original=dict(row["logical"]),parent_manifest=dict(row["parent"]),
       source_field=list(row["field"]),module=g._WORKER_MODULE,canonical_path_as_scalar=row["canonical"]["path"],
       canonical_bytes_as_scalar=row["canonical"]["bytes"],canonical_sha256_as_scalar=row["canonical"]["sha256"],
       exact_link_path_as_scalar=row["link_path"],exact_link_text_as_scalar=row["link_text"]))
 need(exact(saved["fixed_scope"],scope)and saved["unique_expected_fingerprint_n"]==len({fp(x["canonical"])for x in table}),
      "Worker closed23 scope/fingerprint table changed")
 proof_keys={"schema","status","accepted_base","accepted_base_closure","raw_parent_manifests","fixed_scope",
  "fixed_context_n","canonical_target_n","unique_expected_fingerprint_n","observed_context_slots",
  "authorized_observation_n","observations","output_root_as_scalar","authority_metadata_before","authority_metadata_after",
  "source_metadata_before","source_metadata_after","canonical_targets","copy_directory_metadata","allocation","exact_alias_index",
  "original_worker_modes_unchanged_0664","all_inputs_copies_readlinks_pre_end_afteroutput_bound","every_occurrence_authorized_before_seen",
  "normal_JSON_receipt_children_retained","child_parent_is_original_logical_worker","generic_reader_or_17_parent_permission_changed",
  "source_or_scientific_promotion"}
 need(set(saved)==proof_keys,"Closed worker saved proof keyset differs")
 need(set(index)=={"schema","status","aliases","historical_unresolved","canonical_target_n",
      "separate_original_symlink_physical_package_entry_forbidden","normal_JSON_receipt_children_retained",
      "scientific_or_source_acceptance"},"Closed worker alias index keyset differs")
 for target in targets:
  need(set(target)=={"canonical_path_as_scalar","bytes_as_scalar","sha256_as_scalar","preserved","preserved_metadata","child_receipts"},
       "Closed worker canonical target record required")
 for e,x in zip(worker_edges,observations):
  need(e.get("resolution_basis")=="EXACT_FINITE_READONLY_WORKER_CONTROL_BYTECOPY" and e.get("raw_bytes_preserved")is True
       and e.get("receipt_children_interpreted")is True and e.get("child_parent_is_original_logical_worker")is True
       and e.get("source_or_scientific_promotion")is False,"Worker actual C ordinary-child semantics changed")
 return copies,children

def identity_multimap(rows):
 """Preserve every logical identity and destination even when bytes coincide."""
 identities={};by_fp=collections.defaultdict(list);destinations={}
 for row in rows:
  need(type(row)is dict and type(row.get("repository_relative"))is str
       and type(row.get("roles"))is list and row["roles"]and all(type(v)is str for v in row["roles"]),"Full Source identity/roles row required")
  r=subset(row.get("original_source",row.get("logical_receipt")));k=rid(r)
  physical=subset(row.get("source",row.get("physical_receipt")))
  rid(physical)
  need(fp(r)==fp(physical),"Source row original/physical complete fingerprints differ")
  for field in("source","physical_receipt","original_source","logical_receipt"):
   if field in row:
    need(fp(subset(row[field]))==fp(physical),"Source row declared receipt complete fingerprints differ")
  need(type(row.get("logical_receipts",[]))is list,"Source logical receipt candidates require a list")
  d=row["repository_relative"];p=Path(d)
  need(not p.is_absolute()and str(p)not in("","." )and ".."not in p.parts and ".git"not in p.parts,"Unsafe finite Source destination")
  need(row.get("kind")in("IMPLEMENTATION","TEST","CONFIGURATION_OR_LAUNCHER","DOCUMENT"),"Source kind changed")
  if d in destinations:need(fp(destinations[d])==fp(r),"Conflicting finite Source public destination")
  destinations[d]=r
  candidates=[r]+row.get("logical_receipts",[])
  for original in candidates:
   kr=rid(original)
   need(fp(original)==fp(physical),"Source row logical/physical complete fingerprints differ")
   if kr not in identities:identities[kr]=[]
   if row not in identities[kr]:identities[kr].append(row)
   if kr not in by_fp[fp(original)]:by_fp[fp(original)].append(kr)
 return identities,dict(by_fp),destinations

SOURCE_TEXT_ORIGIN=str(R/"steps/24_benchmark_delivery/handoffs/ROOT_PLAN_V13_PRODUCTION_UNBOUND_AUTHOR_TEMPLATE_20261016.txt")
SOURCE_TEXT_BYTES=64944
SOURCE_TEXT_PY="ROOT_PLAN_V13_PRODUCTION_UNBOUND_AUTHOR_TEMPLATE_20261016.py"
SOURCE_TEXT_DEST="delivery_tools/root_operational_programs/"+SOURCE_TEXT_PY
BRIDGE_SCHEMA="finite-source-text-provenance-bridge.v1"
BRIDGE_ROLE="NONOPERATIVE_SOURCE_TEXT_PROVENANCE_ONLY"
BRIDGE_KEYS={"schema","role","original_text","original_metadata_before","original_metadata_after",
 "eligible_copy","eligible_copy_metadata","repository_relative","byte_identity_proof"}
BRIDGE_PROOF_KEYS=(BRIDGE_KEYS-{"byte_identity_proof"})|{"source_inclusion","stage_acceptance","publisher_output_root",
 "allocation","original_or_copied_text_executed","original_text_promoted_to_Source","generic_reader_permission_changed"}
def _source_route_table(rows,routes):
 identities,by_fp,destinations=identity_multimap(rows);copies={};selected={}
 for row in rows:copies[rid(subset(row["source"]))]=subset(row["source"])
 for route in routes:
  need(type(route)is dict and set(route)=={"original","selected_physical","repository_relative"},"Closed selected Source route row required")
  k=rid(route["original"]);physical=subset(route["selected_physical"]);rid(physical)
  need(k in identities and k not in selected,"Selected Source identity missing or duplicated")
  candidates=identities[k]
  need(any(subset(row["source"])==physical and row["repository_relative"]==route["repository_relative"]for row in candidates),
       "Selected Source physical/destination is not this logical identity candidate")
  need(fp(physical)==fp(route["original"]),"Selected Source fingerprint changed")
  if k in copies:need(rid(physical)==k,"Indexed Source copy cannot be redirected to another physical copy")
  selected[k]=physical
 need(set(selected)==set(identities),"Every Source logical identity requires one explicit selected route")
 return identities,by_fp,destinations,copies,selected

def _bridge_basic(row):
 need(type(row)is dict and set(row)==BRIDGE_KEYS and row["schema"]==BRIDGE_SCHEMA
      and row["role"]==BRIDGE_ROLE,"Closed nonoperative Source-text bridge required")
 original=row["original_text"];copy=row["eligible_copy"];rid(original);rid(copy);rid(row["byte_identity_proof"])
 need(original["path"]==SOURCE_TEXT_ORIGIN and original["bytes"]==SOURCE_TEXT_BYTES,
      "Only exact fixed original Source-text identity is documentary")
 need(Path(copy["path"]).name==SOURCE_TEXT_PY and Path(copy["path"]).is_relative_to(R)
      and copy["path"]!=original["path"]and fp(copy)==fp(original),"Eligible Source-text bytecopy path/FP changed")
 need(row["repository_relative"]==SOURCE_TEXT_DEST,"Fixed Source-text public destination changed")
 before=row["original_metadata_before"];after=row["original_metadata_after"]
 metadata_shape(before,original["path"],"file",0o444);metadata_shape(after,original["path"],"file",0o444)
 need(exact(before,after)and before["bytes"]==original["bytes"],"Original Source-text native provenance changed")
 metadata_shape(row["eligible_copy_metadata"],copy["path"],"file",0o444)
 need(row["eligible_copy_metadata"]["bytes"]==copy["bytes"],"Eligible Source-text copy native size changed")
 return original,copy

def source_text_bridge_shape(row,proof,py_bytes,source_i,stage,g):
 """INDEX objects/bytes only: original TXT is never opened or executable."""
 original,copy=_bridge_basic(row)
 need(type(proof)is dict and set(proof)==BRIDGE_PROOF_KEYS,"Closed publisher Source-text byte-identity proof required")
 need(exact({k:proof[k]for k in BRIDGE_KEYS-{"byte_identity_proof"}},{k:row[k]for k in BRIDGE_KEYS-{"byte_identity_proof"}}),
      "Publisher Source-text proof and manifest bridge differ")
 need(proof["source_inclusion"]==source_i and proof["stage_acceptance"]==stage,"Publisher Source-text proof I/stage binding changed")
 root=Path(proof["publisher_output_root"]);need(root.is_absolute()and root.is_relative_to(R)
      and copy["path"]==str(root/"source_text_bytes"/SOURCE_TEXT_PY),"Source-text copy is not exact publisher-owned output")
 allocation=proof["allocation"]
 need(type(allocation)is dict and type(allocation.get("job_id"))is str and allocation["job_id"].isdigit()
      and type(allocation.get("allocated_CPUs"))is int and allocation["allocated_CPUs"]==1
      and type(allocation.get("allocated_gpus"))is int and allocation["allocated_gpus"]==0,
      "Actual Source-text publisher CPU1/GPU0 allocation required")
 need(proof["original_or_copied_text_executed"]is False and proof["original_text_promoted_to_Source"]is False
      and proof["generic_reader_permission_changed"]is False,"Source-text bridge became operative permission")
 need(type(py_bytes)is bytes and(len(py_bytes),hashlib.sha256(py_bytes).hexdigest())==fp(copy),"Indexed eligible Source-text whole bytes changed")
 g.eligible_public(copy,row["repository_relative"])
 need(g.kind(copy["path"])=="IMPLEMENTATION","Eligible .py copy must retain IMPLEMENTATION kind")
 return dict(original=original,copy=copy,proof=row["byte_identity_proof"],role=BRIDGE_ROLE,
             original_is_nonoperative=True,original_filesystem_read=False)

def late_publication_shape(manifest,source_inclusion,stage_receipt,g):
 need(type(manifest)is dict and set(manifest)=={"schema","status","source_inclusion","stage_acceptance","files","source_text_provenance_bridges","raw_JSON_rewritten","source_inclusion_rewritten","Source_IDs_invented","filename_SHA_inferred"}and manifest.get("schema")=="finite-late-source-publication.v2"
      and manifest.get("status")=="EXACT_FINITE_LATE_SOURCE_TREE_BYTES_CPU_VERIFIED_NOT_SCIENTIFIC_ACCEPTANCE"
      and manifest.get("source_inclusion")==source_inclusion and manifest.get("stage_acceptance")==stage_receipt,
      "Actual finite late Source publication required")
 need(type(manifest.get("files"))is list,"Explicit finite late Source rows required")
 need(type(manifest.get("source_text_provenance_bridges"))is list and len(manifest["source_text_provenance_bridges"])==1,"Exactly one fixed nonoperative Source-text bridge required")
 _bridge_basic(manifest["source_text_provenance_bridges"][0])
 for row in manifest["files"]:
  need(type(row)is dict and {"logical_receipt","physical_receipt","repository_relative","kind","roles"}<=set(row)<= {"logical_receipt","physical_receipt","repository_relative","kind","roles","logical_receipts"},"Closed finite publication Source row required")
  original=row["logical_receipt"];physical=row["physical_receipt"];rid(original);rid(physical)
  need(Path(original["path"]).is_relative_to(R)and Path(physical["path"]).is_relative_to(R),"Late Source identity or own copy outside declared authority")
  need(original["path"]!=SOURCE_TEXT_ORIGIN and physical["path"]!=SOURCE_TEXT_ORIGIN and all(x["path"]!=SOURCE_TEXT_ORIGIN for x in row.get("logical_receipts",[])),"Original TXT cannot be an operative Source identity/copy")
  g.eligible_public(original,row["repository_relative"])
  need(g.kind(original["path"])==row["kind"]and fp(original)==fp(physical),"Late Source original kind/byte identity changed")
  need(type(row["roles"])is list and row["roles"]and all(type(x)is str for x in row["roles"]),"Late Source roles missing")
 bridge=manifest["source_text_provenance_bridges"][0]
 need(any(row["logical_receipt"]==bridge["eligible_copy"]and row["repository_relative"]==SOURCE_TEXT_DEST and row["kind"]=="IMPLEMENTATION"for row in manifest["files"]),"Eligible Source-text .py publication row missing")
 need(manifest.get("raw_JSON_rewritten")is False and manifest.get("source_inclusion_rewritten")is False
      and manifest.get("Source_IDs_invented")is False and manifest.get("filename_SHA_inferred")is False,
      "Late Source identity/publication policy changed")
 return identity_multimap(manifest["files"])

def _initial_receipts(binding):
 _binding_shape(binding)
 return [binding["semantics_source"]]+list(binding["producer"].values())+[binding["stage_acceptance"],binding["late_source_publication"]]

def _late_bridge_receipts(late):
 need(late.get("schema")=="finite-late-source-publication.v2"and type(late.get("source_text_provenance_bridges"))is list and len(late["source_text_provenance_bridges"])==1,"Closed v2 publication bridge required")
 row=late["source_text_provenance_bridges"][0];_bridge_basic(row)
 p=Path(row["byte_identity_proof"]["path"])
 need(p.suffix==".json"and p.is_relative_to(R/"steps/24_benchmark_delivery/submissions"),"Only exact owned publisher bridge JSON proof is a control")
 return[row["byte_identity_proof"],row["eligible_copy"]]

def _proof_receipts(a):
 return [a[k]for pair in PAIRS for k in pair]

def _derived_receipts(a,i,proofs,g):
 rows=[]
 for n,proof in enumerate(proofs):
  rows.append(proof["archived_opaque_data"]if n==0 else proof["preserved_opaque_data"]if n>=2 else proof["exact_alias_index"])
 rows.extend([g._WORKER_BASE,g._WORKER_CLOSURE])
 rows.extend(x["preserved"]for x in proofs[1]["canonical_targets"])
 for proof in proofs[2:]:rows.extend(proof["authority_receipts"])
 rows.extend(g._catalog_msa_controls())
 for expected in g.parent_diagnostic_history_source_children():
  matches=[row for row in i["files"]if fp(row["source"])==fp(expected["receipt"])
           and row.get("kind")=="IMPLEMENTATION"]
  need(matches,"Ordinary Source2 physical implementation row missing")
  rows.extend(row["source"]for row in matches)
 rows.extend(i["runner_source_snapshot"])
 return rows

class SavedProjection:
 """Data semantics after exact bytes were supplied; it has no original-path IO."""
 def __init__(self,binding,payloads):
  self.binding=binding;self.transport=_binding_shape(binding);self.payloads=payloads
  self._g=_load_semantics_bytes(_payload(payloads,binding["semantics_source"]),binding["semantics_source"])
  self.a,self.ca,self.i,self.c=_graph_shape(binding,payloads,self._g)
  self.allocation=self.a["allocation"];self.proofs=[];self.indices=[]
  for pk,ik in PAIRS:
   proof=_json(payloads,self.a[pk]);index=_json(payloads,self.a[ik])
   need(proof.get("exact_alias_index")==self.a[ik],"Six-family proof/index pointer changed")
   self.proofs.append(proof);self.indices.append(index)
  self.source_rows=list(self.i["files"])
  stage=_json(payloads,binding["stage_acceptance"])
  need(stage.get("status")=="EXACT_AUDITED_FROZEN_SOURCE_SET_INSTALLED_NOT_GIT_STAGED"
       and stage.get("source_inclusion")==binding["producer"]["source_inclusion"]
       and stage.get("working_tree_commit_or_stage_performed")is False,"Actual I-selected stage required")
  need(set(stage)=={"status","source_inclusion","allocation","entry_n","created_files",
       "working_tree_commit_or_stage_performed","ACTIVE_changed","GPU_submitted"}
       and stage["entry_n"]==len(self.i["files"])and stage["ACTIVE_changed"]is False and stage["GPU_submitted"]is False,
       "Exact actual G stage object/denominator changed")
  installed={str(R/"source"/row["repository_relative"])for row in self.i["files"]}
  need(type(stage["created_files"])is list and len(stage["created_files"])==len(set(stage["created_files"]))
       and set(stage["created_files"])<=installed,"Stage created-file paths exceed exact I destinations")
  stage_allocation=stage["allocation"]
  need(type(stage_allocation)is dict and type(stage_allocation.get("job_id"))is str and stage_allocation["job_id"].isdigit()
       and type(stage_allocation.get("allocated_CPUs"))is int and stage_allocation["allocated_CPUs"]>=1
       and type(stage_allocation.get("allocated_gpus"))is int and stage_allocation["allocated_gpus"]==0,
       "Actual stage CPU/GPU0 allocation required")
  self.late=_json(payloads,binding["late_source_publication"])
  late_publication_shape(self.late,binding["producer"]["source_inclusion"],binding["stage_acceptance"],self._g)
  for row in self.late["files"]:
   self.source_rows.append(dict(original_source=row["logical_receipt"],source=row["physical_receipt"],
       repository_relative=row["repository_relative"],roles=row["roles"],kind=row["kind"],logical_receipts=row.get("logical_receipts",[])))
  self.identities,self.by_fp,self.destinations,self.source_copies,self.source_physical=_source_route_table(self.source_rows,binding["source_routes"])
  self.source_routes=list(binding["source_routes"])
  self.source_bridge=self.late["source_text_provenance_bridges"][0]
  self.bridge_proof=_json(payloads,self.source_bridge["byte_identity_proof"])
  self.bridge_shape=source_text_bridge_shape(self.source_bridge,self.bridge_proof,_payload(payloads,self.source_bridge["eligible_copy"]),binding["producer"]["source_inclusion"],binding["stage_acceptance"],self._g)
  need(any(row["original_source"]==self.source_bridge["eligible_copy"]and row["repository_relative"]==SOURCE_TEXT_DEST and row["kind"]=="IMPLEMENTATION"for row in self.source_rows),"Eligible Source-text .py Source row is missing")
  need(all(rid(self.source_bridge["original_text"])not in self.identities and row["source"]["path"]!=SOURCE_TEXT_ORIGIN and row["original_source"]["path"]!=SOURCE_TEXT_ORIGIN for row in self.source_rows),"Original TXT cannot enter Source row identities")
  self.worker_copies={};self.worker_children={};self.opaque_leaf={};self.control_receipts={}
  self.validated=False

 def validate(self):
  g=self._g
  vendor_saved_shape(g,self.proofs[0],self.indices[0],self.allocation,
                     _payload(self.payloads,self.proofs[0]["archived_opaque_data"]))
  # Original parent is verified only by unchanged ordinary F traversal.
  vendor_expected=dict(receipt=dict(g._VENDOR_EXAMPLE_LEAF),parent=g._VENDOR_EXAMPLE_PARENT["path"],
   field=["15"],module=g._VENDOR_EXAMPLE_MODULE,physical=self.proofs[0]["archived_opaque_data"],
   resolution_basis="EXACT_READONLY_OPAQUE_DATA_BYTECOPY",role=g._VENDOR_EXAMPLE_ROLE,
   raw_bytes_preserved=True,receipt_children_interpreted=False,source_or_configuration_promotion=False)
  vendor_actual=[e for e in self.c["edges"]if e.get("receipt")==g._VENDOR_EXAMPLE_LEAF]
  need(exact(vendor_actual,[vendor_expected]*self.proofs[0]["authorized_observation_n"]),
       "Vendor actual C occurrence context/count changed")
  self.worker_copies,self.worker_children=worker_saved_shape(g,self.proofs[1],self.indices[1],self.allocation,self.payloads,self.c)
  for number,(family,prefix,doc_shape,proof_shape)in enumerate(_history_definitions(g),2):
   saved=self.proofs[number];index=self.indices[number]
   proof_shape(saved,index,self.allocation)
   if family!="parent13290":history_graph_shape(saved,self.c)
   leaf=saved["preserved_opaque_data"]
   doc_shape(_json(self.payloads,leaf))
   need(fp(leaf)==fp(getattr(g,prefix+"_LEAF")),"History copy byte identity changed")
   self.opaque_leaf[rid(getattr(g,prefix+"_LEAF"))]=(leaf,family,saved)
   # The original authority documents are indexed whole documentary inputs, not new reader parents.
   authority_objects=[_json(self.payloads,r)for r in saved["authority_receipts"]]
   base=authority_objects[0]
   need(base.get("original_failure_history")is not None,"Whole BaseA history document required")
   for r,obj in zip(saved["authority_receipts"][1:],authority_objects[1:]):
    need(type(obj)is dict and "original_failure_history"in obj,"Whole Map inherited history required")
   for selected in saved["authorized_parent_field_rows"]:
    parent=selected["parent_manifest"];obj=authority_objects[saved["authority_receipts"].index(parent)]
    for token in selected["field"]:obj=obj[int(token)]if isinstance(obj,list)else obj[token]
    need(obj==getattr(g,prefix+"_LEAF"),"Actual authority/field leaf projection changed")
  g.parent_diagnostic_history_source_coverage(self.proofs[5],self.c,self.i)
  catalog=[_json(self.payloads,r)for r in g._catalog_msa_controls()]
  g.catalog_msa_gap_projection_shape(catalog[0],catalog[1],catalog[2],self.c)
  self.catalog_original_native=g.catalog_msa_gap_projection_native(self.c)
  self.catalog_controls=g._catalog_msa_controls()
  forbidden={fp(g._VENDOR_EXAMPLE_LEAF)}|{fp(x["logical"])for x in g._WORKER_TABLE}
  forbidden.update(fp(getattr(g,prefix+"_LEAF"))for family,prefix,doc,proof in _history_definitions(g))
  for row in self.source_rows:
   need(fp(row["source"])not in forbidden and not g._catalog_msa_old_fingerprint(row["original_source"]),
        "Historical DATA/worker/gap identity cannot be promoted to Source")
  self.opaque_leaf[rid(g._VENDOR_EXAMPLE_LEAF)]=(self.proofs[0]["archived_opaque_data"],"vendor",self.proofs[0])
  required=list(self.binding["producer"].values())+_proof_receipts(self.a)+list(self.catalog_controls)+[g._WORKER_BASE,g._WORKER_CLOSURE]
  for saved in self.proofs[2:]:required.extend(saved["authority_receipts"])
  required.extend(self.binding["additional_control_receipts"])
  required.extend([self.binding["stage_acceptance"],self.binding["late_source_publication"],self.source_bridge["byte_identity_proof"]])
  for r in required:self.control_receipts[rid(r)]=r
  # Every semantic JSON and every accepted JSON SOURCE is physically TXT-only.
  for r in required:
   need(rid(r)in self.transport,"Semantic JSON requires an explicit physical TXT byte transport")
  for physical in self.source_copies.values():
   if Path(physical["path"]).suffix==".json":
    need(rid(physical)in self.transport,"JSON SOURCE requires explicit physical TXT-only transport")
  for row in self.transport.values():
   need(row["original"]["path"]!=SOURCE_TEXT_ORIGIN and row["archived"]["path"]!=SOURCE_TEXT_ORIGIN,"Original TXT cannot become a physical or alias route")
   _payload(self.payloads,row["archived"])
  for r in required:
   need(fp(self.transport[rid(r)]["archived"])==fp(r),"Semantic control transport changed bytes")
  self.declarations=[]
  for slot,row in enumerate(g._WORKER_TABLE):
   self.declarations.extend([(rid(self.a[PAIRS[1][0]]),["fixed_scope",str(slot),"original"],rid(row["logical"])),
       (rid(self.a[PAIRS[1][1]]),["aliases",str(slot),"original"],rid(row["logical"])),
       (rid(g._WORKER_CLOSURE),["edges",str(row["index"]),"receipt"],rid(row["logical"])),
       (rid(g._WORKER_CLOSURE),["edges",str(row["index"]),"physical"],rid(row["logical"]))])
  for n,row in enumerate(self.proofs[1]["observations"]):
   self.declarations.append((rid(self.a[PAIRS[1][0]]),["observations",str(n),"receipt"],rid(row["receipt"])))
  self.validated=True
  return self.proof()

 def proof(self):
  need(self.validated,"Complete Source projection has not been validated")
  return dict(schema=SCHEMA,status=STATUS,producer=self.binding["producer"],
      six_family_pairs=[dict(proof=self.a[p],alias_index=self.a[i])for p,i in PAIRS],
      source_allocation=self.allocation,semantics_source=self.binding["semantics_source"],
      explicit_source_routes=self.source_routes,all_declared_physical_Source_copies=list(self.source_copies.values()),
      all_Source_public_destinations=[dict(source=row["source"],original_source=row["original_source"],repository_relative=row["repository_relative"],kind=row["kind"],roles=row["roles"])for row in self.source_rows],
      nonoperative_source_text_provenance=self.bridge_shape,
      admitted_history_context_n=20,actual_history_context_n=sum(len(x["observations"])for x in self.proofs[2:]),
      worker_logical_n=23,worker_canonical_n=22,source_identity_n=len(self.identities),
      source_identity_fingerprint_multimap=[dict(bytes=k[0],sha256=k[1],logical_identities=[dict(path=x[0],bytes=x[1],sha256=x[2])for x in values])for k,values in sorted(self.by_fp.items())],
      catalog_three_controls=list(self.catalog_controls),catalog_original_metadata_as_provenance=self.catalog_original_native,
      stage_acceptance=self.binding["stage_acceptance"],late_source_publication=self.binding["late_source_publication"],
      original_JSON_changed=False,Source_IDs_invented=False,Source_inclusion_rewritten=False,
      original_worker_or_history_payload_fallback=False,generic_17_parent_permission_changed=False,
      new_scientific_or_Source_acceptance=False,preservation_family_n=6)

 def aliases(self):
  need(self.validated,"Validated Source projection required")
  return list(self.binding["transport_aliases"])+[e for index in self.indices for e in index["aliases"]]

 def selected_source_aliases(self):
  need(self.validated,"Validated Source projection required")
  return[dict(original=dict(path=k[0],bytes=k[1],sha256=k[2]),archived=self._transport_target(physical),status="READONLY_BYTE_IDENTICAL_ALIAS",role="EXACT_FINAL_SOURCE_BYTES")for k,physical in self.source_physical.items()]

 def project_source_alias(self,row):
  """Project only exact authenticated Source logical identities to explicit routes."""
  need(self.validated,"Validated Source projection required")
  original=subset(row.get("original",{}));archived=subset(row.get("archived",{}))
  k=rid(original);rid(archived)
  if k not in self.identities:
   known=set(self.source_copies)|{rid(self._transport_target(v))for v in self.source_copies.values()}
   need(not any(original["path"]==known_key[0]for known_key in self.identities)and(fp(original)not in self.by_fp or k in known),"Unknown path/FP Source alias identity")
   return None
  need(row.get("status")=="READONLY_BYTE_IDENTICAL_ALIAS","Source alias status changed")
  candidates=[]
  for candidate in self.identities[k]:
   physical=subset(candidate["source"])
   for r in(physical,self._transport_target(physical)):
    if r not in candidates:candidates.append(r)
  need(archived in candidates,"Source alias archived tuple is not this logical identity candidate")
  selected=self._transport_target(self.source_physical[k])
  need(selected in candidates,"Selected Source route lost its authenticated candidate")
  return dict(original=original,archived=selected,status="READONLY_BYTE_IDENTICAL_ALIAS",role="EXACT_FINAL_SOURCE_BYTES")

 def check_source_text_alias(self,row):
  if self.source_bridge is None:return True
  known=set(self.identities)|set(self.source_copies)|{rid(self._transport_target(v))for v in self.source_copies.values()}
  for field in("original","archived"):
   r=row.get(field,{})
   need(r.get("path")!=SOURCE_TEXT_ORIGIN,"Original TXT cannot be an operative alias")
   if isinstance(r,dict)and{"path","bytes","sha256"}<=set(r)and fp(r)==fp(self.source_bridge["original_text"]):
    need(rid(subset(r))in known,"Unknown Source-text FP clone cannot be an alias")
  return True

 def worker_alias(self,row):
  original=row.get("original",{});related=any(original.get("path")==r["logical"]["path"]or
       (isinstance(original,dict)and {"bytes","sha256"}<=set(original)and fp(original)==fp(r["logical"]))for r in self._g._WORKER_TABLE)
  if not related:return False
  need(row in self.indices[1]["aliases"],"Only same23 Source-qualified worker aliases are admitted")
  return True

 def _transport_target(self,r):
  return self.transport[rid(r)]["archived"]if rid(r)in self.transport else r

 def terminal_source_receipts(self):
  need(self.validated,"Validated Source projection required")
  rows=[]
  for physical in self.source_copies.values():
   target=self._transport_target(physical)
   if target not in rows:rows.append(target)
  return rows

 def semantic_control_receipts(self):
  need(self.validated,"Validated Source projection required")
  rows=[self._transport_target(r)for r in self.control_receipts.values()]
  rows.extend(self.worker_copies.values())
  rows.extend(pair[0]for pair in self.opaque_leaf.values())
  return list({rid(r):r for r in rows}.values())

 def dispatch(self,r,parent,trail,root_request):
  """BEFORE generic normalization/shape/seen. No Source module is invented for F."""
  need(self.validated,"Validated Source projection required")
  if not(isinstance(r,dict)and {"path","bytes","sha256"}<=set(r)):return None
  raw={name:r[name]for name in("path","bytes","sha256")}
  if type(raw["path"])is not str or not Path(raw["path"]).is_absolute():
   candidates=list(self.source_copies.values())+[row["logical"]for row in self._g._WORKER_TABLE]
   if self.source_bridge is not None:candidates.append(self.source_bridge["original_text"])
   candidates.extend(dict(path=x[0],bytes=x[1],sha256=x[2])for x in self.opaque_leaf)
   need(not any((raw["bytes"],raw["sha256"])==fp(x)for x in candidates),
        "Known finite byte identity cannot become a relative generic route")
   return None
  r3=subset(r);k=rid(r3);parent_key=rid(parent)if parent is not None else None
  need(type(trail)is tuple and all(type(x)is str for x in trail),"Exact composer field tuple required")
  # Current Root request fields declare the closed already-validated binding; they do not grant child routes.
  declaration=False
  if parent_key==rid(root_request):
   declaration=any(r3==x and trail==("source_context",)+field for x,field in receipt_nodes(self.binding))
  if self.source_bridge is not None:
   original=self.source_bridge["original_text"]
   if r3["path"]==SOURCE_TEXT_ORIGIN:
    allowed=((parent_key==rid(self.binding["late_source_publication"])and trail==("source_text_provenance_bridges","0","original_text"))
      or(parent_key==rid(self.source_bridge["byte_identity_proof"])and trail==("original_text",)))
    need(r3==original and allowed,"Original TXT requires exact nonoperative provenance parent/field before seen")
    return dict(kind="DOCUMENTARY_SOURCE_TEXT_PROVENANCE",receipt=r3,physical=None,children=[],role=BRIDGE_ROLE,
                original_is_Source=False,original_payload_read=False,byte_identity_proof=self.source_bridge["byte_identity_proof"])
   related=fp(r3)==fp(original)
   admitted=k in self.identities or k in self.source_copies or k in {rid(self._transport_target(v))for v in self.source_copies.values()}
   need(not related or admitted,"Known Source-text fingerprint clone cannot become an operative route")
  source_related=k in self.identities or k in self.source_copies or k in {rid(self._transport_target(v))for v in self.source_copies.values()}
  if source_related:
   physical=self.source_physical.get(k,r3)
   return dict(kind="SOURCE_BYTES",receipt=r3,physical=self._transport_target(physical),children=[],
               role="SOURCE_QUALIFIED_TERMINAL_BYTES_ORIGINAL_KIND_RETAINED",producer_module_is_not_composer_caller=True)
  # Exact physical copies are own-byte inputs. They never imply a logical child route.
  if k in {rid(v)for v in self.worker_copies.values()}:
   return dict(kind="CONTROL_BYTES",receipt=r3,physical=r3,children=[],
               role="FIXED_WORKER_CANONICAL_COPY_DIRECT_SEED_NO_CHILD_PERMISSION")
  if k in {rid(v[0])for v in self.opaque_leaf.values()}:
   return dict(kind="DATA_BYTES",receipt=r3,physical=r3,children=[],role="EXACT_PRESERVED_DATA_COPY_OWN_BYTES_ONLY")
  for table_row in self._g._WORKER_TABLE:
   related=r3["path"]==table_row["logical"]["path"]or fp(r3)==fp(table_row["logical"])
   if related:
    if declaration or (parent_key,list(trail),k) in self.declarations:
     need(r3==table_row["logical"],"Worker declaration clone identity changed")
     return dict(kind="CONTROL_BYTES",receipt=r3,physical=self.worker_copies[self._g.key(table_row["canonical"])],children=[],
                 role="SOURCE_QUALIFIED_WORKER_DECLARATION_NOT_OPERATIVE_CHILD_PERMISSION")
    need(r3==table_row["logical"]and parent==table_row["parent"]and list(trail)==table_row["field"],
         "Worker requires exact Source-qualified raw parent/field/fulltuple before seen")
    matches=[x for x in self.proofs[1]["observations"]if x["receipt"]==r3 and x["parent"]==parent["path"]and x["field"]==list(trail)]
    need(matches,"Worker operative occurrence lacks actual Source proof")
    physical=self.worker_copies[self._g.key(table_row["canonical"])]
    children=self.worker_children[self._g.key(table_row["canonical"])]
    return dict(kind="WORKER_OPERATIVE",receipt=r3,physical=physical,children=children,
                role="SOURCE_QUALIFIED_WORKER_RAW_PARENT_ORDINARY_CHILDREN",source_producer_module=self._g._WORKER_MODULE)
  for original,(copy,family,saved)in self.opaque_leaf.items():
   if r3["path"]==original[0]or fp(r3)==original[1:]:
    need(k==original,"Known documentary DATA clone cannot gain an edge")
    if declaration:return dict(kind="DATA_BYTES",receipt=r3,physical=copy,children=[],role="CLOSED_SOURCE_DATA_DECLARATION")
    if family=="vendor":
     need(parent==self._g._VENDOR_EXAMPLE_PARENT and trail==("15",),"Vendor exact parent/field required")
    else:
     need(any(x["parent_manifest"]==parent and x["field"]==list(trail)for x in saved["observations"]),
          "Historical DATA requires an actual Source-qualified coupled parent/field")
    return dict(kind="DATA_BYTES",receipt=r3,physical=copy,children=[],role="SOURCE_QUALIFIED_DOCUMENTARY_DATA_NOT_CHILD_RECEIPT")
  old=self._g._catalog_msa_old_fingerprint(r3)
  if old:
   matches=[e for e in self.c["edges"]if e.get("role")==self._g._CATALOG_MSA_ROLE and e.get("receipt")==r3
            and e.get("parent")==self._g._CATALOG_MSA_CATALOG["path"]and e.get("field")==list(trail)]
   need(parent==self._g._CATALOG_MSA_CATALOG and matches,"Catalog MSA gap requires exact Source C/catalog context before seen")
   return dict(kind="DOCUMENTARY_GAP",receipt=r3,physical=None,children=[],
       role=self._g._CATALOG_MSA_ROLE,source_producer_modules=sorted({e["module"]for e in matches}),
       current_input_exemption=False,old_bytes_accepted=False)
  if k in self.control_receipts:
   need(parent is None or declaration or parent_key in {rid(x)for x in self.control_receipts.values()},
        "Semantic Source control used outside the finite declaration")
   children=[]
   if self.source_bridge is not None:
    if k==rid(self.binding["late_source_publication"]):children=[dict(receipt=self.source_bridge["original_text"],field=["source_text_provenance_bridges","0","original_text"])]
    elif k==rid(self.source_bridge["byte_identity_proof"]):children=[dict(receipt=self.source_bridge["original_text"],field=["original_text"])]
   return dict(kind="CONTROL_BYTES",receipt=r3,physical=self._transport_target(r3),children=children,
               role="WHOLE_SOURCE_SEMANTIC_CONTROL_WITH_INDEPENDENT_PURE_PROJECTION")
  if k in {rid(v)for v in self.worker_copies.values()}:
   return dict(kind="CONTROL_BYTES",receipt=r3,physical=r3,children=[],
               role="FIXED_WORKER_CANONICAL_COPY_DIRECT_SEED_NO_CHILD_PERMISSION")
  if k in {rid(x["archived"])for x in self.transport.values()}:
   return dict(kind="CONTROL_BYTES",receipt=r3,physical=r3,children=[],role="FINITE_PHYSICAL_TXT_TRANSPORT_ONLY")
  known=list(self.control_receipts.values())+list(self.source_copies.values())
  known.extend(dict(path=x[0],bytes=x[1],sha256=x[2])for x in self.identities)
  if any(r3["path"]==x["path"]or fp(r3)==fp(x)for x in known):
   need(False,"Known finite Source/control identity cannot fall through to generic seen")
  return None

def load_current(binding):
 """Closed phase reads; no supplied reader/callback/path scope can be injected."""
 _binding_shape(binding);io=CurrentInputs()
 for r in _initial_receipts(binding):
  io.read(r,MAX_SOURCE_CLOSURE if r==binding["producer"]["source_closure"]else MAX_CONTROL)
 g=_load_semantics_bytes(io.payloads[rid(binding["semantics_source"])],binding["semantics_source"])
 a,ca,i,c=_graph_shape(binding,io.payloads,g)
 for r in _proof_receipts(a):io.read(r)
 proofs=[io.json(a[p])for p,k in PAIRS]
 native_records=[proofs[0]["preserved_metadata"]]+[x["preserved_metadata"]for x in proofs[1]["canonical_targets"]]
 native_records.append(proofs[1]["copy_directory_metadata"])
 native_records.extend([proofs[1]["authority_metadata_before"]["base"],proofs[1]["authority_metadata_before"]["closure"]])
 for saved in proofs[2:]:
  native_records.extend(saved["authority_metadata_before"])
  native_records.extend([saved["preserved_metadata"],saved["copy_directory_metadata"]])
 native_records.extend(g.catalog_msa_gap_projection_native(c))
 for expected in native_records:io.enroll_native(expected)
 vendor_copy=Path(proofs[0]["archived_opaque_data"]["path"]);vendor_directory=_safe_current(vendor_copy.parent)
 vendor_directory_before=native(vendor_directory);metadata_shape(vendor_directory_before,vendor_directory,"directory",0o555)
 need({p.name for p in vendor_directory.iterdir()}=={vendor_copy.name},"Exact one-file vendor copy directory required")
 io.enroll_native(vendor_directory_before)
 for r in _derived_receipts(a,i,proofs,g):io.read(r)
 late=io.json(binding["late_source_publication"])
 bridge_receipts=_late_bridge_receipts(late)
 io.enroll_native(late["source_text_provenance_bridges"][0]["eligible_copy_metadata"])
 for r in bridge_receipts:io.read(r)
 for r in binding["additional_control_receipts"]:
  need(Path(r["path"]).suffix==".json"and Path(r["path"]).is_relative_to(R/"steps/24_benchmark_delivery/submissions"),
       "Only explicit owned metadata controls may extend the Source projection")
  io.read(r)
 for row in binding["transport_aliases"]:io.read(row["archived"],MAX_SOURCE_CLOSURE if row["original"]==binding["producer"]["source_closure"]else MAX_CONTROL)
 projection=SavedProjection(binding,io.payloads);projection.validate()
 for r in projection.terminal_source_receipts():io.read(r)
 io.end()
 return CurrentProjection(projection,io)

class CurrentProjection:
 def __init__(self,projection,inputs):self.projection=projection;self.inputs=inputs
 def end(self):
  self.inputs.end()
  repeated=SavedProjection(self.projection.binding,self.inputs.payloads);repeated.validate()
  need(exact(repeated.proof(),self.projection.proof()),"Full Source saved semantic projection changed")
  self.inputs.native_end()
 def native_end(self):self.inputs.native_end()
 def ordinary_parent_receipts(self):
  return [dict(self.projection._g._VENDOR_EXAMPLE_PARENT)]+[dict(r)for r in self.projection._g._WORKER_PARENTS]
 def enroll_ordinary_parents(self):
  p=self.projection
  originals=[p.proofs[0]["parent_metadata_before"]]+p.proofs[1]["authority_metadata_before"]["parents"]
  for r,expected in zip(self.ordinary_parent_receipts(),originals):
   path=_safe_current(r["path"]);before=native(path);metadata_shape(before,path,"file")
   need(before==expected,"Original finite parent native provenance changed before ordinary verification")
   if str(path)in self.inputs.original:need(self.inputs.original[str(path)]==before,"Finite parent original baseline conflict")
   else:self.inputs.original[str(path)]=before
   self.inputs.receipts[rid(r)]=r
 def enroll_installed(self,row):
  need(row in self.projection.source_rows,"Only actual I/Late Source rows may enroll installed bytes")
  expected=dict(subset(row["source"]),path=str(R/"source"/row["repository_relative"]))
  path=_safe_current(expected["path"]);before=native(path)
  metadata_shape(before,path,"file")
  need(stat.S_IMODE(before["mode"])in(0o444,0o644,0o664)and before["bytes"]==expected["bytes"],
       "Installed Source original permission/size changed")
  if str(path)in self.inputs.original:need(self.inputs.original[str(path)]==before,"Installed Source native baseline conflict")
  else:self.inputs.original[str(path)]=before
  self.inputs.receipts[rid(expected)]=expected
  return expected

def _indexed_source_bytes(package,index,r,transports,baseline):
 """One actual same-OWN StrictIndex primitive; no injected reader/import fallback."""
 need(type(index).__name__=="StrictIndex"and index.pkg is package
      and type(index.rows)is dict and type(index.aliases)is dict,"Actual package-owned StrictIndex required")
 cls=type(index);module=sys.modules.get(cls.__module__)
 need(isinstance(module,types.ModuleType)and getattr(module,"StrictIndex",None)is cls
      and getattr(module,"__name__",None)==cls.__module__
      and Path(getattr(module,"__file__",""))==Path(__file__).parent/"restored_index_scope.py",
      "Exact same-OWN loaded StrictIndex class identity required")
 k=rid(r);target=index.aliases.get(k,k)
 if k in transports:
  need(k not in index.rows and target==rid(transports[k]["archived"]),
       "Semantic original JSON must have only its exact physical TXT index entry")
 need(target in index.rows,"Source semantic input absent from package INDEX")
 descriptor,physical=index.rows[target]
 need(fp(descriptor)==fp(r)and physical.is_relative_to(index.root),"StrictIndex physical target differs")
 path=str(physical);before=native(physical);metadata_shape(before,path,"file",0o444)
 if path in baseline:need(baseline[path]==before,"Restored current baseline conflict")
 else:baseline[path]=before
 tag=index.verify(r);need(index.physical(tag)==physical,"StrictIndex verified physical route changed")
 raw=physical.read_bytes()
 need(native(physical)==before and(len(raw),hashlib.sha256(raw).hexdigest())==fp(r),"Restored semantic input whole bytes/native changed during last read")
 return raw

def indexed_payloads(binding,package,index):
 """Read only actual fixed StrictIndex entries; no original path or live G fallback."""
 transports=_binding_shape(binding);payloads={};baseline={}
 need(not any(k[0]==SOURCE_TEXT_ORIGIN for k in index.rows)
      and not any(k[0]==SOURCE_TEXT_ORIGIN for k in index.aliases),"Nonoperative original TXT cannot enter INDEX rows/aliases")
 def obtain(r):
  k=rid(r)
  if k not in payloads:payloads[k]=_indexed_source_bytes(package,index,r,transports,baseline)
  return payloads[k]
 for r in _initial_receipts(binding):obtain(r)
 g=_load_semantics_bytes(obtain(binding["semantics_source"]),binding["semantics_source"])
 a,ca,i,c=_graph_shape(binding,payloads,g)
 for r in _proof_receipts(a):obtain(r)
 proofs=[_json(payloads,a[p])for p,k in PAIRS]
 for r in _derived_receipts(a,i,proofs,g):obtain(r)
 for r in _late_bridge_receipts(_json(payloads,binding["late_source_publication"])):obtain(r)
 for r in binding["additional_control_receipts"]:obtain(r)
 for row in binding["transport_aliases"]:obtain(row["archived"])
 projection=SavedProjection(binding,payloads);projection.validate()
 for r in projection.terminal_source_receipts():obtain(r)
 for row in projection.aliases()+projection.selected_source_aliases():
  projection.check_source_text_alias(row)
  selected=projection.project_source_alias(row)
  original=rid(row["original"]);archived=rid(selected["archived"]if selected is not None else projection._transport_target(row["archived"]))
  need(index.aliases.get(original)==archived and(original not in index.rows or original==archived),
       "Finite Source alias must match explicit selected INDEX route")
 need(not any(k[0]==SOURCE_TEXT_ORIGIN for k in index.rows)
      and not any(k[0]==SOURCE_TEXT_ORIGIN for k in index.aliases),"Nonoperative original TXT cannot enter INDEX rows/aliases")
 index.after(touched_only=True)
 for path,expected in baseline.items():need(native(path)==expected,"Restored Source current native drifted")
 return projection,baseline

def write_context_proof(current,out):
 """Only this new own control uses a durable exclusive writer; old dump is unchanged."""
 need(isinstance(current,CurrentProjection),"Actual closed current Source projection required")
 path=_safe_current(Path(out)/"finite_source_delivery_context_proof.json")
 raw=(json.dumps(current.projection.proof(),indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode("utf-8")
 fd=os.open(str(path),os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,"O_NOFOLLOW",0),0o600)
 with os.fdopen(fd,"wb")as stream:
  stream.write(raw);stream.flush();os.fsync(stream.fileno());os.fchmod(stream.fileno(),0o444);os.fsync(stream.fileno())
 before=native(path);metadata_shape(before,path,"file",0o444)
 receipt=dict(path=str(path),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
 need(path.read_bytes()==raw and native(path)==before,"New finite Source proof durable readback changed")
 current.inputs.original[str(path)]=before;current.inputs.receipts[rid(receipt)]=receipt
 return receipt
