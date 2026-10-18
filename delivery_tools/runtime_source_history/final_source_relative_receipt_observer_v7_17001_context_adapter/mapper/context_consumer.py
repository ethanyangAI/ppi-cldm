#!/usr/bin/env python3
"""Five exact parent readers and restored-only proof verification; no raw edits."""
import json,re
from pathlib import Path
import exact_relative_bbf_context as b
import historical_annotation_context as h
import recovered_five_context as f
import archive_member_context as a
import finite_source_context as s
def need(v,message):
 if not v:raise ValueError(message)
def normalize_edge(r,parent,trail,relative_mapping,historical_mapping,recovered_mapping,archive_mapping=None,source_qualified=None,source_read_bytes=None):
 if source_qualified is not None:
  r,context=s.normalize_source_edge(r,parent,trail,source_qualified,source_read_bytes or s.alias_read_bytes)
  if context is not None:return r,context
 if not Path(r.get("path","")).is_absolute():
  if any(parent==s["parent_manifest"]for s in a.ARCHIVES):return a.normalise_edge(r,parent,trail,archive_mapping)
  if parent==f.PARENT:return f.normalise_edge(r,parent,trail,recovered_mapping)
  return b.normalise(r,parent,trail,relative_mapping)
 r=b.receipt(r)
 if Path(r["path"]).is_relative_to(b.R):return r,None
 return h.normalise_edge(r,parent,trail,historical_mapping)
def source_bundle(base_receipt,relative_mapping,historical_mapping,read_exact,recovered_mapping,archive_mapping):
 base=json.loads(read_exact(base_receipt).read_text());closure=json.loads(read_exact(base["source_closure"]).read_text())
 h.source_base_contract(base,closure,relative_mapping,historical_mapping)
 need(base.get("current_recovered_relative_receipt_context_mapping")==closure.get("current_recovered_relative_receipt_context_mapping")==recovered_mapping and base.get("current_recovered_evidence_file_n")==closure.get("current_recovered_evidence_file_n")==5,"Actual base/closure recovered-five chain required")
 need(base.get("archive_member_receipt_context_mapping")==closure.get("archive_member_receipt_context_mapping")==archive_mapping and base.get("historical_archive_context_parent_n")==closure.get("historical_archive_context_parent_n")==len(a.ARCHIVES) and base.get("archive_member_n")==closure.get("archive_member_n")==a.total(),"Actual V10 base/closure finite archive namespaces required")
 history=json.loads(read_exact(historical_mapping).read_text());h.validate_mapping(history)
 recovered=json.loads(read_exact(recovered_mapping).read_text());archive=json.loads(read_exact(archive_mapping).read_text());a.validate_mapping(archive)
 for other in (recovered,archive):need(other.get("producer_executed_source")==history["producer_executed_source"]and other.get("producer_actual_software_gate")==history["producer_actual_software_gate"],"All contexts must bind same actual V10 source/software")
 need(base.get("archive_member_verification")==closure.get("archive_member_verification")==archive.get("archive_member_verification"),"Actual archive member producer proof pointer differs")
 a.saved_producer_proof(archive,read_exact)
 binding=json.loads(read_exact(base["software_gate_binding"]).read_text())
 need(binding.get("status")=="ACTUAL_SOFTWARE_GATE_BOUND_TO_SOURCE_REFRESH_V10"and binding.get("software_acceptance")==history["producer_actual_software_gate"],"Actual sourcebase V10 software binding differs")
 software=json.loads(read_exact(binding["software_acceptance"]).read_text());inclusion=json.loads(read_exact(base["source_inclusion"]).read_text());jid=software.get("allocation",{}).get("job_id")
 need(isinstance(jid,str)and jid.isdigit()and inclusion.get("status")=="SOURCE_INCLUSION_AUDIT_PASS"and inclusion.get("applied")is False and not inclusion.get("issues")and inclusion.get("source_receipt_closure")==base["source_closure"]and inclusion.get("allocation",{}).get("job_id")==jid,"Actual base inclusion does not bind same V9 executing CPU job/closure")
 snapshot=json.loads(read_exact(software["source_snapshot"]).read_text());expected=[r for r in snapshot.get("source_receipts",[])if Path(r["path"]).suffix in {".py",".sbatch"}]
 need(len(expected)==11 and inclusion.get("runner_source_snapshot")==sorted(expected,key=lambda r:r["path"]),"Base executing source differs from exact tested V10 source snapshot")
 s.verify_source_alias_scope(base,closure,read_exact,restore=getattr(read_exact,"restored_only",False))
 return base,closure
class VerifiedContextReader:
 def __init__(self,mapper_acceptance,base_acceptance,relative_mapping,historical_mapping,reader,bbf_parent_aliases=(),historical_parent_aliases=(),recovered_mapping=None,recovered_parent_aliases=(),archive_mapping=None,archive_parent_aliases=(),finite_source_parent_aliases=()):
  self.accepted,self.qualification=b.verify_mapper_acceptance(mapper_acceptance,relative_mapping,base_acceptance,historical_mapping,recovered_mapping,archive_mapping)
  base,closure=source_bundle(base_acceptance,relative_mapping,historical_mapping,lambda r:b.verify_bytes(r,True),recovered_mapping,archive_mapping)
  self.archives=a.VerifiedArchiveMemberReader(archive_mapping,reader,archive_parent_aliases)
  self.recovered=f.VerifiedRecoveredFiveReader(recovered_mapping,self.archives,recovered_parent_aliases)
  self.historical=h.VerifiedHistoricalAnnotationReader(historical_mapping,self.recovered,historical_parent_aliases)
  self.relative=b.VerifiedContextReader(relative_mapping,self.historical,bbf_parent_aliases);self.finite=s.VerifiedFiniteSourceReader(base,closure,self.relative,lambda r:b.verify_bytes(r,True),finite_source_parent_aliases);self.reader=self.finite
 def __call__(self,path):return self.reader(path)
 def require_both_used(self):
  need(bool(self.relative.used)and bool(self.historical.used)and bool(self.recovered.used)and {h.key(x["logical_parent"])for x in self.archives.used}=={h.key(x["parent_manifest"])for x in a.ARCHIVES},"Actual BBF6/recovered5/historical9/two tar namespace parents must all be traversed")
  self.finite.require_all_used()
  return True
 def proof(self):
  return dict(mapper_qualification=self.qualification,relative_context=self.relative.proof(),historical_annotation_context=self.historical.proof(),current_recovered_context=self.recovered.proof(),archive_member_context=self.archives.proof(),finite_source_context=self.finite.proof(),raw_JSON_changed=False,module_local_reader_only=True,unknown_relative_or_current_external_permission_added=False)
def terminal_proof(qualification,accepted,acceptance_receipt):
 need(qualification.get("mapper_acceptance")==acceptance_receipt,"Archived actual mapper terminal proof identity differs")
 saved=qualification.get("actual_terminal_accounting",{});raw=saved.get("raw");row=saved.get("row")
 need(isinstance(raw,str)and isinstance(row,list)and len(row)>=9 and "|".join(row)in raw,"Actual saved numeric terminal sacct row required")
 job,state,exitcode,elapsed,tres,user,account,name,partition=row[:9]
 need(job==accepted.get("allocation",{}).get("job_id")and state=="COMPLETED"and exitcode=="0:0"and elapsed.isdigit()and user==account=="u21111210118"and partition=="organ"and name=="test9_exact_context_v4","Archived terminal mapper state/owner differs")
 vals=b.strict_tres(tres)
 def n(k):
  return vals.get(k,0)
 need(n("cpu")>=1 and max(n("gres/gpu"),sum(n(k)for k in vals if k.startswith("gres/gpu:")))==0 and saved.get("allocated_GPUs")==0,"Archived mapper terminal GPU0/CPU required");return True
def verify_restored_bundle(mapper_acceptance,mapper_qualification,base_acceptance,relative_mapping,historical_mapping,restore_root,index,recovered_mapping,archive_mapping):
 allocation=b.cpu_guard();root,lookup=b.restored_index(index,restore_root);read_paths=[]
 def exact(r):
  p=b.restored_bytes(r,root,lookup);need(not(p.stat().st_mode&0o222),"Readonly restored mapper/base authority metadata/source required");read_paths.append(str(p));return p
 exact.restored_only=True
 accepted=json.loads(exact(mapper_acceptance).read_text());contracts=json.loads(exact(accepted["contracts"]).read_text());sources=b.mapper_contract_shape(accepted,contracts)
 need(accepted.get("base_acceptance")==base_acceptance and accepted.get("relative_receipt_context_mapping")==relative_mapping and accepted.get("external_historical_receipt_context_mapping")==historical_mapping and accepted.get("current_recovered_relative_receipt_context_mapping")==recovered_mapping and accepted.get("archive_member_receipt_context_mapping")==archive_mapping,"Restored mapper/base/four-map chain differs")
 for r in sources:exact(r)
 exact(contracts["log"]);qualification=json.loads(exact(mapper_qualification).read_text())
 if "mapper_qualification"in qualification:qualification=qualification["mapper_qualification"]
 terminal_proof(qualification,accepted,mapper_acceptance)
 base,closure=source_bundle(base_acceptance,relative_mapping,historical_mapping,exact,recovered_mapping,archive_mapping)
 need(accepted.get("source_closure")==base.get("source_closure"),"Restored mapper accepted closure differs from actual base closure")
 f.verify_saved_verification(accepted,exact);a.verify_saved_verification(accepted,exact)
 source_qualified,source_proof=s.verify_saved_alias_proofs(accepted,base,closure,exact,restore=True)
 saved_relative=json.loads(exact(accepted["mapping_verification"]).read_text());need(saved_relative.get("mapping_receipt")==relative_mapping and saved_relative.get("all_six_actual_bytes_verified")is True,"Archived real BBF6 verification missing")
 saved_history=json.loads(exact(accepted["historical_annotation_verification"]).read_text());need(saved_history.get("mapping_receipt")==historical_mapping and saved_history.get("parent_manifest")==h.PARENT and saved_history.get("historical_annotation_n")==9 and saved_history.get("raw_historical_bytes_accepted")is False,"Archived real nine-annotation verification missing")
 for field,n,parent in [("read_view_proof",6,b.PARENT),("historical_annotation_read_view_proof",9,h.PARENT),("current_recovered_read_view_proof",5,f.PARENT),*[("archive_member_read_view_proof",s["member_count"],s["parent_manifest"])for s in a.ARCHIVES]]:
  proof=json.loads(exact(accepted[field]).read_text());need(proof.get("raw_JSON_changed")is False and proof.get("module_local_reader_only")is True and any(e.get("logical_parent")==parent and len(e.get("contexts",[]))==n for e in proof.get("read_views_used",[])),"Archived actual bounded read-view proof missing")
 rm,rproof=b.verify_restored_mapping(relative_mapping,root,index);hm,hproof=h.verify_restored_mapping(historical_mapping,root,index);fm,fproof=f.verify_restored_mapping(recovered_mapping,root,index);am,aproof=a.verify_restored_mapping(archive_mapping,root,index)
 return dict(mapper_acceptance=mapper_acceptance,mapper_qualification=mapper_qualification,base_acceptance=base_acceptance,relative_receipt_context_mapping=relative_mapping,external_historical_receipt_context_mapping=historical_mapping,current_recovered_relative_receipt_context_mapping=recovered_mapping,archive_member_receipt_context_mapping=archive_mapping,current_recovered_restored_verification=fproof,archive_member_restored_verification=aproof,finite_source_restored_verification=source_proof,finite_source_recovery_inputs_qualification=base["finite_source_recovery_inputs_qualification"],finite_source_alias_verification=base["finite_source_alias_verification"],finite_exact_source_alias_index=base["finite_exact_source_alias_index"],mapper_source_files=sources,relative_restored_verification=rproof,historical_restored_verification=hproof,restored_root=str(root),read_paths=read_paths,all_read_paths_under_restored_root=True,no_live_root_fallback=True,raw_JSON_changed=False,allocation=allocation)
