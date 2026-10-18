#!/usr/bin/env python3
"""Exactly nine byte-unrecovered historical annotations. No recovery or external reads."""
import copy,json,re,subprocess
from pathlib import Path
import exact_relative_bbf_context as b
R=b.R
PARENT={"path":"/lustre/users/u21111210118/projects/test9/01_raw/recovered_inputs/recovered_three_candidates.json","bytes":4665,"sha256":"04a73810c339e4594e8dc989e2c89aa3ba90542f89d5644c92f9df2b755c482c"}
RECOVERY_MARKER={"status":"EXACT_SEQUENCE_FROM_HISTORICAL_OUTPUT_STRUCTURES_NOT_RECOVERED","source_session_id":"01a0bdc5-988d-70c1-8346-f463d4989fa2","record_number":7006,"corroborating_record_number":6378,"missing_files":"native, backbone, design_manifest paths are historical provenance, not currently restored files"}
ROWS=[{"source_field":["entries","0","native"],"original_logical_path":"/work/home/lvying/lvying20260610/project-1/test9/steps/03_design/runs/20260922T114002Z_de9505e8c15e/outputs/native.pdb","expected_bytes":181712,"expected_sha256":"cd328a743e389add7403d3f04fcf1f78ef9ae687d365737a419ee8f1cc6fe076"},{"source_field":["entries","0","backbone"],"original_logical_path":"/work/home/lvying/lvying20260610/project-1/test9/steps/03_design/runs/20260922T114002Z_de9505e8c15e/outputs/bb1144_seq1.pdb","expected_bytes":110612,"expected_sha256":"6c09a08416d772fa251556d6f12cced39ef270d35c6c96a859c3fd0bfe32e1e0"},{"source_field":["entries","0","design_manifest"],"original_logical_path":"/work/home/lvying/lvying20260610/project-1/test9/steps/03_design/runs/20260922T114002Z_de9505e8c15e/manifest.json","expected_bytes":12434,"expected_sha256":"97c239a9fdb423703dea7f532db18839b2afa0dd9711a7184fc2741cd3619820"},{"source_field":["entries","1","native"],"original_logical_path":"/work/home/lvying/lvying20260610/project-1/test9/steps/03_design/runs/20260922T113858Z_149ef033124f/outputs/native.pdb","expected_bytes":181712,"expected_sha256":"cd328a743e389add7403d3f04fcf1f78ef9ae687d365737a419ee8f1cc6fe076"},{"source_field":["entries","1","backbone"],"original_logical_path":"/work/home/lvying/lvying20260610/project-1/test9/steps/03_design/runs/20260922T113858Z_149ef033124f/outputs/bb144_seq1.pdb","expected_bytes":110612,"expected_sha256":"39978b06a6143c968e3e8de72e42edb97158aa947af0c19c8f4270845534a11c"},{"source_field":["entries","1","design_manifest"],"original_logical_path":"/work/home/lvying/lvying20260610/project-1/test9/steps/03_design/runs/20260922T113858Z_149ef033124f/manifest.json","expected_bytes":12402,"expected_sha256":"47bfbe1852aede63e479b88a1456a06aafc0797730453d003551091ff5251262"},{"source_field":["entries","2","native"],"original_logical_path":"/work/home/lvying/lvying20260610/project-1/test9/steps/03_design/runs/20260922T113858Z_149ef033124f/outputs/native.pdb","expected_bytes":181712,"expected_sha256":"cd328a743e389add7403d3f04fcf1f78ef9ae687d365737a419ee8f1cc6fe076"},{"source_field":["entries","2","backbone"],"original_logical_path":"/work/home/lvying/lvying20260610/project-1/test9/steps/03_design/runs/20260922T113858Z_149ef033124f/outputs/bb145_seq0.pdb","expected_bytes":110612,"expected_sha256":"4c18ec575b6361ab5c02383d01c615d35a3b541922d18df14b2b00fb75284fcb"},{"source_field":["entries","2","design_manifest"],"original_logical_path":"/work/home/lvying/lvying20260610/project-1/test9/steps/03_design/runs/20260922T113858Z_149ef033124f/manifest.json","expected_bytes":12402,"expected_sha256":"47bfbe1852aede63e479b88a1456a06aafc0797730453d003551091ff5251262"}]
SCHEMA="exact-unrecovered-historical-annotations.v1"
STATUS="EXACT_NINE_NONOPERATIVE_HISTORICAL_ANNOTATIONS_CPU_CLASSIFIED_ORIGINAL_JSON_UNCHANGED"
ROLE="NONOPERATIVE_HISTORICAL_PROVENANCE_ANNOTATION_UNRECOVERED_NOT_BYTE_ACCEPTED"
ANNOTATION_STATUS="HISTORICAL_PROVENANCE_ANNOTATION_UNRECOVERED_NOT_BYTE_ACCEPTED"
SOURCE_NAMES={"source_delivery_refresh_v10.py","relative_receipt_policy.py","test_relative_receipt_policy.py","source_refresh_bootstrap.py","source_refresh_cpu.sbatch","HANDOFF.md","delivery_core.py","delivery_graph_v2.py","provenance_aliases_v2.py","native_resource_closure_v2.py","reference_source_delivery_refresh_v1.py","historical_archive_member_context.py"}
SOURCE_CONTRACTS=122
def need(v,message):
 if not v:raise ValueError(message)
def receipt(r):return b.receipt(r)
def logical(e):return receipt(dict(path=e["original_logical_path"],bytes=e["expected_bytes"],sha256=e["expected_sha256"]))
def key(r):return r["path"],r["bytes"],r["sha256"]
def field_value(obj,trail):
 for token in trail:
  need(isinstance(token,str),"String exact field trail required")
  if isinstance(obj,list):
   need(token.isdigit()and str(int(token))==token,"Exact decimal list index required")
   obj=obj[int(token)]
  elif isinstance(obj,dict):obj=obj[token]
  else:raise ValueError("Exact annotation field missing")
 return obj
def replace_field(obj,trail,value):
 target=field_value(obj,trail[:-1]);last=trail[-1]
 if isinstance(target,list):target[int(last)]=value
 else:target[last]=value
def expected_entry(i):
 row=dict(ROWS[i])
 return dict(**row,source_parent=dict(PARENT),parent_canonical_receipt=dict(PARENT),parent_original_logical_path=PARENT["path"],parent_expected_bytes=PARENT["bytes"],parent_expected_sha256=PARENT["sha256"],canonical_receipt=None,raw_byte_acceptance=False,current_execution_allowed=False,historical_file_restored=False,status=ANNOTATION_STATUS,role=ROLE)
def validate_mapping(m):
 need(isinstance(m,dict)and m.get("schema")==SCHEMA and m.get("status")==STATUS,"Exact V10 nine-annotation map required")
 need(m.get("parent_manifest")==PARENT and m.get("recovery_status")==RECOVERY_MARKER["status"]and m.get("recovery_missing_files")==RECOVERY_MARKER["missing_files"]and m.get("recovery_marker")==RECOVERY_MARKER,"Exact recovered-sequence parent and explicit unrecovered marker required")
 need(m.get("original_json_unchanged")is True and m.get("external_files_read")is False and m.get("current_declared_graph_only")is True and m.get("raw_byte_acceptance")is False and m.get("actual_current_sequence_input_parent_bytes_verified")is True,"No raw JSON edit/external read permission allowed")
 need(m.get("historical_annotation_n")==9 and m.get("canonical_external_text_edge_n")==0 and m.get("unresolved_current_external_edges_allowed")is False,"Only nine annotations; no generic external aliases allowed")
 lineage=m.get("accepted_lineage_receipts");need(isinstance(lineage,list)and len(lineage)>=6 and len({key(receipt(r))for r in lineage})==len(lineage),"Exact unique accepted producer lineage required")
 for name in ("producer_executed_source","producer_actual_software_gate","source_graph_selector","prior_accepted_inclusion"):need(receipt(m[name])in lineage,"Actual source/software/selector/prior lineage binding required")
 entries=m.get("entries");need(isinstance(entries,list)and len(entries)==9,"Complete nine-field annotation map required")
 by={}
 for e in entries:
  need(isinstance(e,dict)and isinstance(e.get("source_field"),list)and all(isinstance(t,str)for t in e["source_field"]),"Exact string annotation field trail required")
  field=tuple(e["source_field"]);need(field not in by,"Duplicate historical annotation field")
  matching=[i for i,row in enumerate(ROWS)if row["source_field"]==e["source_field"]]
  need(len(matching)==1,"Unknown historical annotation field")
  expected=expected_entry(matching[0]);need(all(e.get(k)==v for k,v in expected.items()),"Historical annotation parent/path/size/SHA/role differs")
  if "accepted_lineage_receipts"in e:need(e["accepted_lineage_receipts"]==lineage,"Annotation lineage differs")
  by[field]=e
 need(set(by)=={tuple(r["source_field"])for r in ROWS},"All nine exact original field permissions required")
 anchor=m.get("anchor",{});anchorrow=next(r for r in ROWS if r["source_field"]==["entries","2","design_manifest"])
 need(all(anchor.get(k)==v for k,v in anchorrow.items()if k!="source_field")and anchor.get("canonical_receipt")is None and anchor.get("historical_file_restored")is False and anchor.get("status")==ANNOTATION_STATUS,"Original12402 anchor remains unrecovered, never manufactured byte acceptance")
 return by
def exact_manifest_view(parent,obj,m):
 need(parent==PARENT,"Historical annotation view requires exact4665 parent descriptor")
 by=validate_mapping(m)
 need(isinstance(obj,dict)and obj.get("recovery")==RECOVERY_MARKER and isinstance(obj.get("entries"),list)and len(obj["entries"])==3,"Original explicit recovery role changed")
 view=copy.deepcopy(obj);contexts=[]
 for field,e in by.items():
  need(receipt(field_value(obj,field))==logical(e),"Exact original annotation field identity changed")
  replacement={k:e[k]for k in ("original_logical_path","expected_bytes","expected_sha256","source_field","canonical_receipt","raw_byte_acceptance","current_execution_allowed","historical_file_restored","status","role")}
  # Scalar identity is intentionally not a receipt-shaped dictionary.
  replace_field(view,field,replacement);contexts.append(replacement)
 return view,contexts
def verify_content(m,read_exact):
 validate_mapping(m)
 for r in m["accepted_lineage_receipts"]:read_exact(r)
 def read(r):return json.loads(read_exact(r).read_text())
 producer=read(m["producer_actual_software_gate"])
 need(producer.get("schema")=="source-refresh-relative-software-acceptance.v10"and producer.get("status")=="SOURCE_REFRESH_RELATIVE_SOFTWARE_CPU_ACCEPTED_ACTUAL_SOURCE_AUDIT_PENDING"and producer.get("tests_expected")==SOURCE_CONTRACTS and producer.get("compiled_all_python")is True and producer.get("bash_syntax_checked")is True,"Actual V10 software122/syntax qualification required")
 contracts=read(producer["contracts"]);need(contracts.get("status")=="PASS"and contracts.get("tests")==SOURCE_CONTRACTS and contracts.get("failures")==0 and contracts.get("errors")==0,"Actual saved V10 software122 PASS required");read_exact(contracts["log"])
 snapshot=read(producer["source_snapshot"]);sources=snapshot.get("source_receipts",[])
 need(len(sources)==12 and {Path(r["path"]).name for r in sources}==SOURCE_NAMES and len({key(receipt(r))for r in sources})==12 and m["producer_executed_source"]in sources and m["source_graph_selector"]in sources,"Whole exact tested V10 twelve-file source universe required")
 for r in sources:read_exact(r)
 parent=read(PARENT);view,contexts=exact_manifest_view(PARENT,parent,m)
 return dict(parent_manifest=dict(PARENT),recovery_marker=RECOVERY_MARKER,all_nine_contexts=contexts,historical_annotation_n=9,raw_historical_bytes_accepted=False,historical_files_restored=False,original_JSON_changed=False,external_files_read=False,producer_source_files=sources,producer_software_gate=m["producer_actual_software_gate"])
def verify_mapping_receipt(r):
 allocation=b.cpu_guard();m=json.loads(b.verify_bytes(r,True).read_text());proof=verify_content(m,lambda x:b.verify_bytes(x,True))
 proof.update(mapping_receipt=receipt(r),allocation=allocation,producer_terminal_accounting=producer_terminal(m,lambda x:b.verify_bytes(x,True)));return m,proof
def normalise_edge(r,parent,trail,m):
 r=receipt(r)
 if Path(r["path"]).is_relative_to(R):return r,None
 by=validate_mapping(m);need(parent==PARENT,"Unknown external parent/context forbidden")
 field=tuple(trail);need(field in by and isinstance(trail,(tuple,list))and all(isinstance(t,str)for t in trail),"Unknown external field forbidden before dedup")
 e=by[field];need(logical(e)==r,"Unknown external original descriptor forbidden")
 return None,{k:e[k]for k in ("original_logical_path","expected_bytes","expected_sha256","source_field","canonical_receipt","raw_byte_acceptance","current_execution_allowed","historical_file_restored","status","role")}
class VerifiedHistoricalAnnotationReader:
 def __init__(self,mapping_receipt,reader,parent_aliases=()):
  self.mapping_receipt=receipt(mapping_receipt);self.mapping,self.verification=verify_mapping_receipt(mapping_receipt);self.reader=reader;self.used=[]
  self.parents={PARENT["path"]:dict(PARENT)}
  for row in parent_aliases:
   need(isinstance(row,dict)and set(row)=={"logical","physical"}and row["logical"]==PARENT,"Only explicit exact parent byte alias allowed")
   physical=receipt(row["physical"]);need((physical["bytes"],physical["sha256"])==(PARENT["bytes"],PARENT["sha256"])and physical["path"]not in self.parents,"Historical parent alias changes bytes or duplicates")
   b.verify_bytes(physical,True);self.parents[physical["path"]]=physical
 def __call__(self,path):
  p=Path(path);need(p.is_absolute()and p.is_relative_to(R)and p.resolve()==p,"External filesystem reads forbidden")
  if str(p)not in self.parents:return self.reader(path)
  physical=self.parents[str(p)];b.verify_bytes(physical,True);obj=self.reader(path)
  view,contexts=exact_manifest_view(PARENT,obj,self.mapping)
  self.used.append(dict(physical_parent=physical,logical_parent=dict(PARENT),contexts=contexts,raw_JSON_changed=False))
  return view
 def proof(self):return dict(mapping_receipt=self.mapping_receipt,verification=self.verification,read_views_used=self.used,scope="EXACT_ONE_PARENT_NINE_UNRECOVERED_ANNOTATION_SCALAR_VIEW_ONLY",raw_JSON_changed=False,module_local_reader_only=True,external_files_read=False)
def verify_restored_mapping(mapping_receipt,restore_root,index):
 allocation=b.cpu_guard();root,lookup=b.restored_index(index,restore_root);read_paths=[]
 need(root!=R and not R.is_relative_to(root)and not Path(PARENT["path"]).is_relative_to(root),"Restore-only root cannot contain live parent authority")
 def exact(r):
  p=b.restored_bytes(r,root,lookup);need(not(p.stat().st_mode&0o222),"Readonly restored V10 authority metadata/source required");read_paths.append(str(p));return p
 m=json.loads(exact(mapping_receipt).read_text());proof=verify_content(m,exact)
 proof.update(mapping_receipt=receipt(mapping_receipt),restored_root=str(root),read_paths=read_paths,all_read_paths_under_restored_root=True,no_live_root_fallback=True,allocation=allocation)
 return m,proof
def source_base_contract(base,closure,relative_mapping,history_mapping):
 need(base.get("schema")=="source-delivery-refresh.v3"and base.get("status")=="CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY"and base.get("source_issues")==0 and base.get("source_staged")is False and base.get("external_files_read")is False,"Actual unchanged-schema V10 source .v3 acceptance required")
 need(relative_mapping==base.get("relative_receipt_context_mapping")==closure.get("relative_receipt_context_mapping")and history_mapping==base.get("external_historical_receipt_context_mapping")==closure.get("external_historical_receipt_context_mapping"),"Exact base/closure/two-map identity chain required")
 need(base.get("historical_provenance_annotation_n")==9 and closure.get("historical_provenance_annotation_n")==9 and closure.get("external_files_read")is False,"Actual nine nonoperative annotations required")
 return True

def producer_terminal(mapping,read_exact=b.verify_bytes):
 software=json.loads(read_exact(mapping["producer_actual_software_gate"]).read_text());jid=software.get("allocation",{}).get("job_id")
 need(isinstance(jid,str)and jid.isdigit(),"Actual V10 producer CPU job identity required")
 launcher=next(r for r in verify_content(mapping,lambda r:read_exact(r))["producer_source_files"]if Path(r["path"]).name=="source_refresh_cpu.sbatch")
 text=read_exact(launcher).read_text();names=re.findall(r"^#SBATCH --job-name=(\S+)$",text,re.M)
 need(len(names)==1 and names[0]=="test9_source_relative_v10","Exact submitted V10 launcher jobname required")
 raw=subprocess.check_output(["sacct","-X","-j",jid,"--noheader","--parsable2","--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocTRES,User%64,Account%64,JobName%100,Partition%64"],text=True)
 rows=[x.split("|")for x in raw.splitlines()if x.split("|",1)[0]==jid]
 need(len(rows)==1 and len(rows[0])>=9,"Unique sourceV10 terminal CPU accounting required")
 job,state,exitcode,elapsed,tres,user,account,name,partition=rows[0][:9]
 vals=b.strict_tres(tres)
 def n(k):
  return vals.get(k,0)
 need(state=="COMPLETED"and exitcode=="0:0"and elapsed.isdigit()and user==account=="u21111210118"and partition=="organ"and name==names[0]and n("cpu")>=1 and max(n("gres/gpu"),sum(n(k)for k in vals if k.startswith("gres/gpu:")))==0,"Actual sourceV10 COMPLETED0/pureCPU owner/name required")
 return dict(raw=raw,job_id=jid,state=state,exit_code=exitcode,allocated_CPUs=n("cpu"),allocated_GPUs=0,elapsed_seconds=int(elapsed),user=user,account=account,partition=partition,jobname=name)
