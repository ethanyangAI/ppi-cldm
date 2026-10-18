#!/usr/bin/env python3
"""Current source inclusion extension; byte-preserving, CPU only, never result promotion."""
import argparse,collections,hashlib,json,os,shutil
from pathlib import Path
from delivery_core import cpu,rec,dump,SECRET_RE
from delivery_graph_v2 import source_entries,graph_nodes,SUFFIXES
from provenance_aliases_v2 import ReceiptResolver
from native_resource_closure_v2 import historical_gap,recompute_dependency
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
def audit(out):
 allocation=cpu();out=Path(out);out.mkdir(parents=True,exist_ok=False)
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
 index=read(R/INDEX_REL);policy=read(R/POLICY_REL);pack=read(R/BBF_PACK_REL)
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
  r,parent,trail=queue.pop()
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
  edges.append({"receipt":r,"parent":parent,"field":list(trail),"physical":rec(p),"resolution_basis":basis,"role":"EXACT_TEXT_RECEIPT_READBACK"})
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
    queue.extend((n,r["path"],t) for n,t in receipt_edges(obj))
 # Operative source pins from accepted alias closure are independently included.
 for row in index.get("aliases",[]):
  r=row["original"]
  if Path(r["path"]).suffix in SOURCE_EXT:
   p,basis=resolve(r)
   if not any(item["path"]==p for item in original_rows.values()):
    add(p,Path("rebuild/benchmarks/20261011/exact_source_aliases")/(r["sha256"]+"_"+Path(r["path"]).name),"ACCEPTED_NATIVE74_SOURCE_CLOSURE_EXACT_BYTES",r)
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
 closure={"schema":"benchmark-source-receipt-closure.v1","status":"EXACT_CURRENT_TEXT_AND_SOURCE_DEPENDENCY_CLOSURE_WITH_TYPED_HISTORY","seeds":seeds,"edges":edges,"recursive_text_and_source_receipt_n":len(cache),"source_receipts":list(sources.values()),"historical_gaps":list(gaps.values()),"conditional_inference_dependencies":list(deps.values()),"data_receipts_preserved_not_reaudited_n":len(data_receipts),"source_missing_allowed_only_exact_historical_edges":True,"raw_models_reaudited":False,"models_recomputed":False,"same_lustre_only":True}
 closure_receipt=dump(out/"source_receipt_closure.json",closure)
 result={"schema":"benchmark-source-inclusion.v3","status":"SOURCE_INCLUSION_AUDIT_PASS" if not issues else "SOURCE_INCLUSION_REVIEW_REQUIRED","authority_root":str(R),"declared_runtime_settings":"pilot_v8","prior_inclusion":rec(R/PRIOR_INCLUSION_REL),"graph_nodes":graph_nodes(R,"pilot_v8")+[{"role":role,"path":str(p),"recursive":recursive} for role,p,recursive,paths in extras],"files":rows,"issues":issues,"applied":False,"allocation":allocation,"source_receipt_closure":closure_receipt,"entry_kind_counts":dict(collections.Counter(x["kind"] for x in rows)),"actual_source_dependency_n":len(sources),"historical_gap_count":len(gaps),"formal_array_job_id":"13260","formal_benchmark_completed":False,"ACTIVE_changed":False,"scope":"Frozen public source/config/launcher/readiness only. Data evidence gates remain accepted originals; full formal GPU results/common review/package/restore/publication are pending.","immutable_staging_policy":"Stage only this exact audited frozen source byte set, verify expected audit SHA, refuse different existing destinations. No mtime or later graph re-enumeration."}
 result["runner_source_snapshot"]=[rec(p) for p in sorted(Path(__file__).parent.iterdir()) if p.is_file() and p.suffix in {".py",".sbatch"}]
 inclusion=dump(out/"source_inclusion_v3.json",result)
 acceptance={"schema":"source-delivery-refresh.v1","status":"CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY" if not issues else "SOURCE_REFRESH_REQUIRES_REVIEW","source_inclusion":inclusion,"source_closure":closure_receipt,"source_entries":len(rows),"source_issues":len(issues),"entry_kind_counts":result["entry_kind_counts"],"current_formal28_source_bound":True,"formal_runtime":"pilot_v8","formal_array_job_id":"13260","source_staged":False,"ACTIVE_changed":False,"GPU_submitted":False,"raw_models_recomputed":False}
 dump(out/"acceptance.json",acceptance);print(json.dumps(acceptance,ensure_ascii=False))
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
 x=sub.add_parser("audit");x.add_argument("--out",required=True)
 x=sub.add_parser("stage");x.add_argument("--audit",required=True);x.add_argument("--audit-sha256",required=True);x.add_argument("--out",required=True)
 a=p.parse_args()
 if a.command=="audit":audit(a.out)
 else:stage(a.audit,a.audit_sha256,a.out)
if __name__=="__main__":main()

