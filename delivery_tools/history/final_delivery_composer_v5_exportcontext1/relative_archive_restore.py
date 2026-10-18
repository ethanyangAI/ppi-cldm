#!/usr/bin/env python3
"""Narrow archive/restore adapter for accepted BBF13226 context. No publication."""
import argparse,json,os,re,sys
from pathlib import Path
import final_delivery_composer as m

def context_module():
 return m.context_api().load_bundle().b
def receipt_id(r):return(r["path"],r["bytes"],r["sha256"])
def executing_source_binding(accepted_source):
 actual=m.sources();m.need(actual==accepted_source,"Whole executing composer and library source differs from archived tested source")
 return actual
def index_from_package(pkg,root):
 m.need(pkg.get("schema")=="benchmark-delivery-package.v1"and pkg.get("status")=="PACKAGED_AWAITING_INDEPENDENT_RESTORE"and pkg.get("authority_root")==str(m.R),"Exact accepted authority package required")
 ctx=context_module();rows=[];seen=set()
 for item in pkg["manifest"]:
  r=ctx.receipt(item["receipt"]);rel=item["relative"]
  m.need(Path(r["path"]).is_relative_to(m.R)and Path(r["path"]).relative_to(m.R).as_posix()==rel,"Package logical path/relative mismatch")
  key=receipt_id(r);m.need(key not in seen,"Duplicate package logical identity");seen.add(key)
  rows.append(dict(logical=r,restored_relative=rel))
 ctx.restored_index(rows,root)
 return rows
def with_aliases(ctx,root,index,aliases):
 _,entries=ctx.restored_index(index,root);rows=list(index);seen={receipt_id(x["logical"])for x in rows}
 for e in aliases.get("aliases",[]):
  m.need(e.get("status")=="READONLY_BYTE_IDENTICAL_ALIAS","Unknown restored alias status")
  logical=ctx.receipt(e["original"]);physical=ctx.receipt(e["archived"])
  m.need(Path(logical["path"]).is_relative_to(m.R)and Path(physical["path"]).is_relative_to(m.R),"Restored logical alias outside authority")
  m.need(m.identity(logical)==m.identity(physical),"Restored alias changes exact byte identity")
  restored=ctx.restored_bytes(physical,Path(root),entries)
  if receipt_id(logical)not in seen:
   rows.append(dict(logical=logical,restored_relative=restored.relative_to(root).as_posix()));seen.add(receipt_id(logical))
 ctx.restored_index(rows,root)
 return rows
def mapper_terminal_shape(binding,mapper):
 proof=binding["actual_mapper_prerequisite"]
 m.need(proof["source_files"]==mapper["source_files"]and proof["contracts"]==mapper["contracts"],"Archived mapper source/contracts fork")
 bundle=m.context_api().load_bundle();bundle.c.terminal_proof(proof,mapper,binding["mapper_acceptance"])
 return proof
def restored_qualification(ctx,root,index,binding):
 s=dict(composer=binding["composer_source"],existing_API_dependencies=binding["existing_API_dependencies"],context_API_dependencies=binding["context_API_dependencies"])
 executing_source_binding(s)
 _,entries=ctx.restored_index(index,root)
 def file(r):
  p=ctx.restored_bytes(r,Path(root),entries);m.need(not(p.stat().st_mode&0o222),"Restored readonly qualification metadata/source required");return p
 def read(r):return json.loads(file(r).read_text())
 bundle=m.context_api().load_bundle()
 accepted=read(binding["mapper_acceptance"]);contracts=read(accepted["contracts"])
 pins=ctx.mapper_contract_shape(accepted,contracts)
 m.context_api().executed_mapper_binding(pins,s["context_API_dependencies"],m.identity)
 for r in pins+s["composer"]+s["existing_API_dependencies"]+s["context_API_dependencies"]:file(r)
 for r in contracts["compiled_python_sources"]:file(r)
 for name in ("stdout","stderr"):file(contracts["bash_syntax"][name])
 file(contracts["log"])
 request=read(accepted["request"])
 m.need(request.get("schema")=="exact-current-context-mapper-request.v4"and request.get("root_owned")is True and request.get("raw_JSON_rewrite_allowed")is False and request.get("generic_relative_resolution_allowed")is False and request.get("generic_external_resolution_allowed")is False,"Archived exact five-parent root request required")
 for key,value in (("base_acceptance",binding["base_acceptance"]),("relative_receipt_context_mapping",binding["mapping"]),("external_historical_receipt_context_mapping",binding["historical_mapping"]),("current_recovered_relative_receipt_context_mapping",binding["current_recovered_mapping"]),("archive_member_receipt_context_mapping",binding["archive_member_mapping"])):m.need(request.get(key)==value,"Archived root mapper request field differs")
 terminal=mapper_terminal_shape(binding,accepted)
 saved_terminal=read(binding["mapper_terminal_qualification"]);m.need(saved_terminal==terminal,"Archived immutable mapper terminal proof differs")
 sw=read(binding["composer_software"]);m.need(sw.get("schema")=="final-composer-software.v5"and sw.get("status")==m.SOFTWARE_STATUS and sw.get("source")==s,"Restored exact V5 composer software source differs")
 tests=read(sw["contracts"]);m.need(tests.get("status")=="PASS"and tests.get("tests_run")==m.SOFTWARE_TESTS and tests.get("failures")==0 and tests.get("errors")==0 and tests.get("tested_source")==s and tests.get("all_owned_and_context_python_compile_PASS")is True and tests.get("all_launchers_bash_syntax_PASS")is True,"Actual V5 composer contracts/source/syntax missing");file(tests["log"])
 helper=m.export_api();export_q,export_result,export_inputs=helper.required(binding,lambda r:file(r).read_bytes(),restore=True,source=s)
 export_reader=helper.ExportContextReader(export_q,export_result,lambda r:file(r).read_bytes(),lambda p:json.loads(file(next(r for r in export_inputs if r["path"]==str(p))).read_bytes()))
 export_reader(export_q["manifest"]["path"]);export_reader(export_q["inventory"]["path"]);export_reader.require_both_used()
 controller=m.qualify_controller_amendment(binding["controller_metadata_amendment"],file,restore=True)
 proof=bundle.c.verify_restored_bundle(binding["mapper_acceptance"],binding["mapper_terminal_qualification"],binding["base_acceptance"],binding["mapping"],binding["historical_mapping"],root,index,binding["current_recovered_mapping"],binding["archive_member_mapping"])
 return dict(mapper_acceptance=binding["mapper_acceptance"],composer_software=binding["composer_software"],mapper_contracts=accepted["contracts"],all_mapper_composer_library_sources_restored_and_verified=True,actual_mapper_prerequisite=terminal,controller_metadata_amendment_restored_qualification=controller,github_export_context_restored_qualification=binding["github_export_context_qualification"],github_export_read_view=export_reader.proof(),all_committed_Git_blob_bytes_restored_and_tree_reconstructed=True,context_restored_proof=proof,no_live_mapper_acceptance_verifier_called=True)
def require_current_context_archive(config,bundle,source_qualification=None,finite_receipts=()):
 declared={receipt_id(x["receipt"])for x in config["files"]};required=[bundle.b.PARENT,bundle.h.PARENT,bundle.f.PARENT]+[r for spec in bundle.a.ARCHIVES for r in (spec["parent_manifest"],spec["archive_receipt"])]+[bundle.f.expected_entry(i)["canonical_receipt"]for i in range(5)]
 if source_qualification is not None:
  required+=bundle.s.required_parent_receipts(source_qualification)+source_qualification["canonical_source_and_provenance_inputs"]+list(finite_receipts)
 m.need(all(receipt_id(r)in declared for r in required),"All five original parents, both whole tar archives and five current evidence children must be archived")
 return required
def package(validation_receipt,out,part_mib):
 allocation=m.cpu();source=m.sources();validation=json.loads(m.verify(validation_receipt,True).read_text())
 m.need(validation.get("status")=="FINAL_DELIVERY_CONFIG_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY","Actual core final validation required")
 config=json.loads(m.verify(validation["config"],True).read_text());binding=config["exact_relative_context"]["bindings"]
 bundle,current=m.context_bindings(dict(mapper_acceptance=binding["mapper_acceptance"],mapping=binding["mapping"],base_acceptance=binding["base_acceptance"],historical_mapping=binding["historical_mapping"],current_recovered_mapping=binding["current_recovered_mapping"],archive_member_mapping=binding["archive_member_mapping"]))
 executing_source_binding(dict(composer=binding["composer_source"],existing_API_dependencies=binding["existing_API_dependencies"],context_API_dependencies=binding["context_API_dependencies"]))
 m.software(binding["composer_software"],source)
 for k in ("mapper_acceptance","base_acceptance","mapping","historical_mapping","current_recovered_mapping","archive_member_mapping","accepted_mapper_sources","executed_mapper_sources","finite_source_artifacts","finite_mapper_proofs"):m.need(binding[k]==current[k],"Actual package context binding differs")
 m.need(json.loads(m.verify(binding["mapper_terminal_qualification"],True).read_text())==binding["actual_mapper_prerequisite"],"Saved terminal qualification bytes differ")
 aliases=json.loads(m.verify(config["resource_aliases"],True).read_text())
 def parents(parent):return [dict(logical=parent,physical=e["archived"])for e in aliases.get("aliases",[])if e["original"]==parent and e["archived"]["path"]!=parent["path"]]
 reader=bundle.c.VerifiedContextReader(binding["mapper_acceptance"],binding["base_acceptance"],binding["mapping"],binding["historical_mapping"],lambda p:json.loads(Path(p).read_text()),parents(bundle.b.PARENT),parents(bundle.h.PARENT),binding["current_recovered_mapping"],parents(bundle.f.PARENT),binding["archive_member_mapping"],[r for spec in bundle.a.ARCHIVES for r in parents(spec["parent_manifest"])],[r for parent in bundle.s.required_parent_receipts(bundle.source_qualification)for r in parents(parent)])
 for parent in (bundle.b.PARENT,bundle.h.PARENT,bundle.f.PARENT,*[spec["parent_manifest"]for spec in bundle.a.ARCHIVES],*bundle.s.required_parent_receipts(bundle.source_qualification)):reader(parent["path"])
 reader.require_both_used()
 helper=m.export_api();export_q,export_result,export_inputs=helper.required(binding,source=source)
 reader=helper.ExportContextReader(export_q,export_result,helper.local_bytes,reader)
 reader(export_q["manifest"]["path"]);reader(export_q["inventory"]["path"]);reader.require_both_used()
 declared={receipt_id(x["receipt"])for x in config["files"]};m.need(all(receipt_id(r)in declared for r in export_inputs),"Every export parent/payload/full Git blob/remote/source proof must be archived")
 controller=m.qualify_controller_amendment(binding["controller_metadata_amendment"])
 saved_controller=json.loads(m.verify(binding["controller_metadata_amendment"]["independent_proof"],True).read_text());m.need(saved_controller==controller,"Actual independent controller amendment proof differs before package")
 require_current_context_archive(config,bundle,bundle.source_qualification,list(binding["finite_source_artifacts"].values())+list(binding["finite_mapper_proofs"].values())+controller["all_exact_inputs"]+[binding["controller_metadata_amendment"]["independent_proof"]])
 api=m.load("context_unchanged_package_API",m.LIB/"delivery_core_v2.py")
 result=api.package(validation_receipt["path"],str(out),part_mib)
 proof=m.dump(out/"exact_context_package_acceptance.json",dict(status="UNCHANGED_CORE_PACKAGE_WITH_FIVE_EXACT_PARENT_CONTEXTS_CURRENT_BYTES_REVERIFIED",allocation=allocation,validation=validation_receipt,package=m.rec(out/"packaging_receipt.json"),context_binding=binding,current_mapper_prerequisite=current["actual_mapper_prerequisite"],read_view_proof=reader.proof(),all_five_current_evidence_files_in_archive=True,all_two_whole_tar_archives_and_indices_in_archive=True,original_JSON_bytes_changed=False,independent_restore_pending=True,published=False))
 return result,proof
def restore(package_receipt,restore_root,out):
 allocation=m.cpu();pkg=json.loads(m.verify(package_receipt).read_text());root=m.safe(restore_root);out=m.safe(out)
 m.need(root.is_dir()and out.is_relative_to(root)and not out.exists(),"Separate new recomputation output below restored tree required")
 ctx=context_module();index=index_from_package(pkg,root);_,entries=ctx.restored_index(index,root)
 hashes=json.loads((root/"RESTORE_HASH_ACCEPTANCE.json").read_text())
 m.need(hashes.get("status")=="RESTORED_HASHES_VERIFIED_CONTENT_RECOMPUTATION_PENDING"and hashes.get("package")==package_receipt and hashes.get("restore_root")==str(root)and hashes.get("files_verified")==len(pkg["manifest"]),"Actual exact hash-verified extraction required")
 config=json.loads(ctx.restored_bytes(pkg["config"],root,entries).read_text());aliases=json.loads(ctx.restored_bytes(config["resource_aliases"],root,entries).read_text());index=with_aliases(ctx,root,index,aliases)
 binding=config["exact_relative_context"]["bindings"];qualification=restored_qualification(ctx,root,index,binding)
 api=m.load("context_unchanged_independent_restore_API",m.LIB/"restore_verify_v2.py")
 core=api.run(package_receipt["path"],str(root),str(out))
 def indexed_readonly_bytes(r):
  p=ctx.restored_bytes(r,root,ctx.restored_index(index,root)[1]);m.need(not(p.stat().st_mode&0o222),"Restored readonly qualification required after scientific recomputation");return p.read_bytes()
 helper=m.export_api();helper.required(binding,indexed_readonly_bytes,restore=True,source=m.sources())
 proof=m.dump(out/"exact_context_restore_acceptance.json",dict(status="RESTORED_ONLY_MAPPER_SOURCE_BBF6_RECOVERED5_NINE_ANNOTATIONS_AND588_ARCHIVE_MEMBERS_ACCEPTED",allocation=allocation,package=package_receipt,qualification=qualification,raw_JSON_changed=False,scientific_live_fallback=False))
 successor=dict(core,exact_relative_context_acceptance=proof,unchanged_core_restore_acceptance=m.rec(out/"acceptance.json"),original_scientific_evidence_read=False)
 acceptance=m.dump(out/"context_restore_acceptance.json",successor);return successor,acceptance
def main():
 p=argparse.ArgumentParser();sp=p.add_subparsers(dest="mode",required=True)
 pp=sp.add_parser("package");pp.add_argument("--validation",required=True);pp.add_argument("--validation-sha256",required=True);pp.add_argument("--out",required=True);pp.add_argument("--part-mib",type=int,default=512)
 rp=sp.add_parser("restore");rp.add_argument("--package",required=True);rp.add_argument("--package-sha256",required=True);rp.add_argument("--restore-root",required=True);rp.add_argument("--out",required=True)
 a=p.parse_args();m.cpu()
 source=m.sources() # Reviewed, immutable software only; no scientific read before CPU guard.
 if a.mode=="package":
  r=m.rec(a.validation);m.need(r["sha256"]==a.validation_sha256,"Exact CLI validation SHA differs");out=m.safe(a.out);m.need(not out.exists(),"New package output required");result,receipt=package(r,out,a.part_mib)
 else:
  r=m.rec(a.package);m.need(r["sha256"]==a.package_sha256,"Exact CLI package SHA differs");result,receipt=restore(r,a.restore_root,a.out)
 print(json.dumps(receipt))
if __name__=="__main__":main()
