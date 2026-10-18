#!/usr/bin/env python3
"""Distinct three-path final-source adapter using actual qualified V4 five-parent source."""
import argparse,importlib.util,json,shutil,sys
from pathlib import Path
S=importlib.util.spec_from_file_location("bootstrap_final_source_closure",Path(__file__).with_name("final_source_closure.py"))
base=importlib.util.module_from_spec(S);S.loader.exec_module(base)
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def run(request_path,out):
 allocation=base.cpu();runtime=base.conditional_core_runtime();executed,executed_before=base.owned_source_bundle(Path(__file__).resolve().parent);out=base.safe_path(out);aux=out.with_name(out.name+"_context_adapter");aux.mkdir(parents=True,exist_ok=False);phase="readonly_request_library_and_mapper_source"
 try:
  request=base.safe_path(request_path);base.need(request.is_file()and not(request.stat().st_mode&0o222),"Readonly root adapter request required");q=base.read(request)
  base.need(q.get("schema")=="final-source-materialized-context-read-view-request.v3"and q.get("root_owned")is True and q.get("raw_JSON_rewrite_allowed")is False and q.get("generic_relative_resolution_allowed")is False and q.get("generic_external_resolution_allowed")is False,"Distinct exact root three-path/context adapter request required")
  owned=base.freeze_runner(aux);owned_before=[base.stable_metadata(r["path"])for r in owned]
  base.owned_source_readback(executed,owned,executed_before,owned_before)
  software=base.read(base.verify(q["library_software_acceptance"],True));contracts=base.read(base.verify(software["contracts"],True));library_sources=base.software_shape(software,contracts);base.verify(contracts["log"],True)
  base.software_snapshot_shape(software,base.read(base.verify(software["source_snapshot"],True)))
  base.need(software["conditional_core_runtime"]==runtime,"Actual qualified library/current CORE runtime differs")
  library_terminal=base.terminal_cpu(software.get("allocation",{}).get("job_id"),base.SOFTWARE_JOB_NAME)
  for r in library_sources:
   base.verify(r,True);executing=next(x for x in owned if Path(x["path"]).name==Path(r["path"]).name);base.need(base.fp(executing)==base.fp(r),"Executed library differs from qualified source6")
  lib=module("final_source_closure",aux/"runner/final_source_closure.py")
  ma=lib.read(lib.verify(q["mapper_software_acceptance"],True));pins=ma.get("source_files",[]);names={"finite_source_context.py","test_finite_source_context.py","exact_relative_bbf_context.py","test_exact_relative_bbf_context.py","context_mapper_audit_cpu.py","context_mapper_cpu.sbatch","context_consumer.py","HANDOFF.md","historical_annotation_context.py","test_historical_annotation_context.py","recovered_five_context.py","test_recovered_five_context.py","archive_member_context.py","test_archive_member_context.py"}
  lib.need(len(pins)==14 and {Path(r["path"]).name for r in pins}==names,"Whole actual accepted mapper14 required")
  mapper=aux/"mapper";mapper.mkdir()
  for r in pins:
   p=lib.verify(r,True);target=mapper/p.name;shutil.copyfile(p,target);target.chmod(0o444);lib.need(lib.fp(lib.rec(target))==lib.fp(r),"Qualified mapper copy bytes differ")
  mapper.chmod(0o555);sys.path.insert(0,str(mapper))
  context=module("exact_relative_bbf_context",mapper/"exact_relative_bbf_context.py");history=module("historical_annotation_context",mapper/"historical_annotation_context.py");recovered=module("recovered_five_context",mapper/"recovered_five_context.py");archives=module("archive_member_context",mapper/"archive_member_context.py");finite=module("finite_source_context",mapper/"finite_source_context.py");consumer=module("context_consumer",mapper/"context_consumer.py")
  phase="exact_actual_mapper_base_context_prerequisites"
  plan_path=lib.verify(q["final_source_plan"],True);plan=lib.read(plan_path)
  lib.need(plan.get("mapper_software_acceptance")==q["mapper_software_acceptance"]and plan.get("library_software_acceptance")==q["library_software_acceptance"],"Plan/adapter software prerequisites differ")
  sourcebase,sourceclosure=consumer.source_bundle(plan["base_acceptance"],plan["relative_receipt_context_mapping"],plan["external_historical_receipt_context_mapping"],lambda r:lib.verify(r,True),plan["current_recovered_relative_receipt_context_mapping"],plan["archive_member_receipt_context_mapping"])
  source_qualification,_=finite.verify_source_alias_scope(sourcebase,sourceclosure,lambda r:lib.verify(r,True))
  lib.need(plan.get("context_parent_seeds")==[context.PARENT,history.PARENT,recovered.PARENT,*[x["parent_manifest"]for x in archives.ARCHIVES],*finite.required_parent_receipts(source_qualification)],"Only five current-context/six source/five proof/one generated closure exact accepted raw parent seeds may be declared")
  reader=consumer.VerifiedContextReader(q["mapper_software_acceptance"],plan["base_acceptance"],plan["relative_receipt_context_mapping"],plan["external_historical_receipt_context_mapping"],lib.read,q.get("bbf_parent_aliases",[]),q.get("historical_parent_aliases",[]),plan["current_recovered_relative_receipt_context_mapping"],q.get("recovered_parent_aliases",[]),plan["archive_member_receipt_context_mapping"],q.get("archive_parent_aliases",[]),q.get("finite_source_parent_aliases",[]))
  phase="actual_frozen_library_audit_with_module_local_context_reader"
  original=lib.read;lib.read=reader
  try:lib.audit(str(plan_path),str(out))
  finally:lib.read=original
  lib.need(lib.read is original,"Module-local source library reader was not restored");reader.require_both_used()
  acceptance_path=lib.safe_path(out/"acceptance.json")
  acceptance_metadata=lib.stable_metadata(acceptance_path)
  lib._parent_diagnostic_history_metadata_shape(acceptance_metadata,str(acceptance_path),acceptance_metadata["bytes"])
  acceptance_receipt=lib.rec(acceptance_path)
  lib.need(acceptance_receipt["bytes"]==acceptance_metadata["bytes"]and lib.stable_metadata(acceptance_path)==acceptance_metadata,
           "Actual adapter acceptance changed before first JSON read")
  proof=lib.dump(aux/"five_parent_context_reader_proof.json",reader.proof())
  accepted=lib.read(acceptance_path)
  lib.need(lib.rec(acceptance_path)==acceptance_receipt and lib.stable_metadata(acceptance_path)==acceptance_metadata,
           "Actual adapter acceptance changed during first JSON read")
  lib.need(accepted.get("schema")=="final-source-closure-acceptance.v3"and accepted.get("status")=="FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED",
           "Actual new3path source closure did not qualify")
  parent_diagnostic_graph_receipts={"acceptance":acceptance_receipt,"source_closure":accepted["source_closure"],"source_inclusion":accepted["source_inclusion"]}
  parent_diagnostic_graph_metadata={"acceptance":acceptance_metadata}
  for name in ("source_closure","source_inclusion"):
   receipt=lib.receipt_shape(parent_diagnostic_graph_receipts[name])
   path=lib.safe_path(receipt["path"])
   metadata=lib.stable_metadata(path)
   lib._parent_diagnostic_history_metadata_shape(metadata,str(path),receipt["bytes"])
   parent_diagnostic_graph_metadata[name]=metadata
  # BOTH authenticated C/I original native snapshots exist before ANY C/I payload read/hash.
  catalog_C=lib.read(lib.verify(parent_diagnostic_graph_receipts["source_closure"],True))
  lib.need(lib.rec(accepted["source_closure"]["path"])==parent_diagnostic_graph_receipts["source_closure"]
           and lib.stable_metadata(accepted["source_closure"]["path"])==parent_diagnostic_graph_metadata["source_closure"],
           "Actual adapter source closure changed during first JSON read")
  for name,metadata in parent_diagnostic_graph_metadata.items():
   lib.need(lib.stable_metadata(metadata["path"])==metadata,
            "Actual adapter original graph native changed during first closure JSON read")
  catalog_original_native=lib.catalog_msa_gap_projection_native(catalog_C)
  if catalog_original_native:lib.catalog_msa_gap_saved_inputs(catalog_C)
  opaque_proof=accepted["vendor_example_opaque_leaf_proof"];opaque_aliases=accepted["vendor_example_opaque_aliases"]
  lib.verify(opaque_proof,True);lib.verify(opaque_aliases,True)
  opaque=lib.read(opaque_proof["path"]);alias_data=lib.read(opaque_aliases["path"])
  lib.need(opaque.get("schema")=="exact-vendor-example-opaque-data-leaf.v1"and opaque.get("exact_alias_index")==opaque_aliases and alias_data.get("schema")=="exact-resource-aliases.v2"and len(alias_data.get("aliases",[]))==1,"Actual finite vendor preservation proof/alias scope required")
  lib.verify_vendor_example_preservation(opaque,alias_data,allocation)
  worker_proof=accepted["finite_worker_control_proof"];worker_aliases=accepted["finite_worker_control_aliases"]
  lib.verify(worker_proof,True);lib.verify(worker_aliases,True)
  worker=lib.read(worker_proof["path"]);worker_index=lib.read(worker_aliases["path"])
  lib.need(worker.get("exact_alias_index")==worker_aliases,"Actual worker proof/index pointer differs")
  lib.verify_finite_worker_preservation(worker,worker_index,allocation)
  for name in ("source_inclusion","source_closure"):
   produced=lib.read(lib.verify(accepted[name],True))
   lib.need(produced.get("finite_worker_control_proof")==worker_proof and produced.get("finite_worker_control_aliases")==worker_aliases,"Source A/I/C worker proof/index pointers differ")
  parent_diagnostic_proof=accepted["parent_diagnostic_history_opaque_leaf_proof"];parent_diagnostic_aliases=accepted["parent_diagnostic_history_opaque_aliases"]
  parent_diagnostic_proof_metadata=lib._parent_diagnostic_history_control_metadata(parent_diagnostic_proof["path"])
  parent_diagnostic_alias_metadata=lib._parent_diagnostic_history_control_metadata(parent_diagnostic_aliases["path"])
  history_native_records=list(executed_before)+list(owned_before)+[runtime["logical_metadata"],runtime["resolved_metadata"]]+list(catalog_original_native)
  history_control_native=[parent_diagnostic_proof_metadata,parent_diagnostic_alias_metadata]
  def history_final_native_sweep():
   records=list(history_native_records)+list(history_control_native)+list(parent_diagnostic_graph_metadata.values())
   return lib._fixed_history_native_union_sweep(records)
  def catalog_projection_readback():
   if catalog_original_native:
    controls={name:(receipt,parent_diagnostic_graph_metadata[name])for name,receipt in parent_diagnostic_graph_receipts.items()}
    records=lib.catalog_msa_gap_graph_readback(controls)
    lib.need(lib.exact_json(records,catalog_original_native),"Actual adapter catalog original native table fork")
    history_final_native_sweep()
  catalog_projection_readback()
  def parent_diagnostic_controls_readback():
   saved,unused=lib._parent_diagnostic_history_control_readback(parent_diagnostic_proof,parent_diagnostic_proof_metadata)
   index,unused=lib._parent_diagnostic_history_control_readback(parent_diagnostic_aliases,parent_diagnostic_alias_metadata)
   lib.verify_parent_diagnostic_history_preservation(saved,index,allocation)
   history_native_records.extend(lib._fixed_history_saved_native_records(saved))
   graph_objects={}
   for name,receipt in parent_diagnostic_graph_receipts.items():
    path=lib.verify(receipt,True);before=lib.stable_metadata(path)
    lib._parent_diagnostic_history_metadata_shape(before,str(path),receipt["bytes"])
    lib.need(lib.exact_json(before,parent_diagnostic_graph_metadata[name]),"Actual adapter13290 graph control native metadata drifted")
    produced=lib.read(path)
    lib.need(produced.get("parent_diagnostic_history_opaque_leaf_proof")==parent_diagnostic_proof and produced.get("parent_diagnostic_history_opaque_aliases")==parent_diagnostic_aliases,"Actual adapter A/I/C parent-diagnostic pointer fork")
    lib.need(lib.rec(path)==receipt and lib.stable_metadata(path)==before,"Actual adapter13290 graph control changed during final JSON read")
    if name=="acceptance":lib.need(lib.exact_json(produced,accepted),"Actual adapter13290 original acceptance object fork")
    if name=="context_adapter_acceptance":lib.need(lib.exact_json(produced,result),"Actual adapter13290 complete CA object fork")
    graph_objects[name]=produced
   lib.parent_diagnostic_history_source_coverage(saved,graph_objects["source_closure"],graph_objects["source_inclusion"])
   for name,receipt in parent_diagnostic_graph_receipts.items():
    lib.need(lib.rec(receipt["path"])==receipt and lib.stable_metadata(receipt["path"])==parent_diagnostic_graph_metadata[name],"Actual adapter13290 graph control changed after final coverage readback")
   lib._parent_diagnostic_history_control_readback(parent_diagnostic_proof,parent_diagnostic_proof_metadata)
   lib._parent_diagnostic_history_control_readback(parent_diagnostic_aliases,parent_diagnostic_alias_metadata)
   lib._fixed_history_authority_fence("parent13290",saved["authority_metadata_before"])
   for name,receipt in parent_diagnostic_graph_receipts.items():
    lib.need(lib.rec(receipt["path"])==receipt and lib.stable_metadata(receipt["path"])==parent_diagnostic_graph_metadata[name],"Actual adapter13290 graph control changed after final proof/index readback")
   history_final_native_sweep()
   return saved,index
  parent_diagnostic,parent_diagnostic_index=parent_diagnostic_controls_readback()
  lib.need(parent_diagnostic.get("exact_alias_index")==parent_diagnostic_aliases,"Actual parent-diagnostic history proof/index pointer differs")
  parent_diagnostic_controls_readback()
  catalog_projection_readback()
  for name in ("source_inclusion","source_closure"):
   produced=lib.read(lib.verify(accepted[name],True))
   lib.need(produced.get("parent_diagnostic_history_opaque_leaf_proof")==parent_diagnostic_proof and produced.get("parent_diagnostic_history_opaque_aliases")==parent_diagnostic_aliases,"Source A/I/C parent-diagnostic proof/index pointers differ")
  relative_diagnostic_proof=accepted["relative_diagnostic_history_opaque_leaf_proof"];relative_diagnostic_aliases=accepted["relative_diagnostic_history_opaque_aliases"]
  relative_diagnostic_proof_metadata=lib._relative_diagnostic_history_control_metadata(relative_diagnostic_proof["path"])
  relative_diagnostic_alias_metadata=lib._relative_diagnostic_history_control_metadata(relative_diagnostic_aliases["path"])
  history_control_native.extend([relative_diagnostic_proof_metadata,relative_diagnostic_alias_metadata])
  def relative_diagnostic_controls_readback():
   saved,unused=lib._relative_diagnostic_history_control_readback(relative_diagnostic_proof,relative_diagnostic_proof_metadata)
   index,unused=lib._relative_diagnostic_history_control_readback(relative_diagnostic_aliases,relative_diagnostic_alias_metadata)
   lib.verify_relative_diagnostic_history_preservation(saved,index,allocation)
   history_native_records.extend(lib._fixed_history_saved_native_records(saved))
   lib._relative_diagnostic_history_control_readback(relative_diagnostic_proof,relative_diagnostic_proof_metadata)
   lib._relative_diagnostic_history_control_readback(relative_diagnostic_aliases,relative_diagnostic_alias_metadata)
   lib._fixed_history_authority_fence("relative13295",saved["authority_metadata_before"])
   history_final_native_sweep()
   return saved,index
  relative_diagnostic,relative_diagnostic_index=relative_diagnostic_controls_readback()
  lib.need(relative_diagnostic.get("exact_alias_index")==relative_diagnostic_aliases,"Actual relative-diagnostic history proof/index pointer differs")
  relative_diagnostic_controls_readback()
  parent_diagnostic_controls_readback()
  catalog_projection_readback()
  for name in ("source_inclusion","source_closure"):
   produced=lib.read(lib.verify(accepted[name],True))
   lib.need(produced.get("relative_diagnostic_history_opaque_leaf_proof")==relative_diagnostic_proof and produced.get("relative_diagnostic_history_opaque_aliases")==relative_diagnostic_aliases,"Source A/I/C relative-diagnostic proof/index pointers differ")
  archive_parent_proof=accepted["archive_parent_history_opaque_leaf_proof"];archive_parent_aliases=accepted["archive_parent_history_opaque_aliases"]
  archive_parent_proof_metadata=lib._archive_parent_history_control_metadata(archive_parent_proof["path"])
  archive_parent_alias_metadata=lib._archive_parent_history_control_metadata(archive_parent_aliases["path"])
  history_control_native.extend([archive_parent_proof_metadata,archive_parent_alias_metadata])
  def archive_parent_controls_readback():
   saved,unused=lib._archive_parent_history_control_readback(archive_parent_proof,archive_parent_proof_metadata)
   index,unused=lib._archive_parent_history_control_readback(archive_parent_aliases,archive_parent_alias_metadata)
   lib.verify_archive_parent_history_preservation(saved,index,allocation)
   history_native_records.extend(lib._fixed_history_saved_native_records(saved))
   lib._archive_parent_history_control_readback(archive_parent_proof,archive_parent_proof_metadata)
   lib._archive_parent_history_control_readback(archive_parent_aliases,archive_parent_alias_metadata)
   lib._fixed_history_authority_fence("archive13298",saved["authority_metadata_before"])
   history_final_native_sweep()
   return saved,index
  archive_parent,archive_parent_index=archive_parent_controls_readback()
  lib.need(archive_parent.get("exact_alias_index")==archive_parent_aliases,"Actual archive-parent history proof/index pointer differs")
  archive_parent_controls_readback()
  relative_diagnostic_controls_readback()
  parent_diagnostic_controls_readback()
  catalog_projection_readback()
  for name in ("source_inclusion","source_closure"):
   produced=lib.read(lib.verify(accepted[name],True))
   lib.need(produced.get("archive_parent_history_opaque_leaf_proof")==archive_parent_proof and produced.get("archive_parent_history_opaque_aliases")==archive_parent_aliases,"Source A/I/C archive-parent proof/index pointers differ")
  inventory_proof=accepted["inventory_history_opaque_leaf_proof"];inventory_aliases=accepted["inventory_history_opaque_aliases"]
  history_control_native.extend([lib.stable_metadata(inventory_proof["path"]),lib.stable_metadata(inventory_aliases["path"])])
  lib.verify(inventory_proof,True);lib.verify(inventory_aliases,True)
  inventory=lib.read(inventory_proof["path"]);inventory_index=lib.read(inventory_aliases["path"])
  lib.need(inventory.get("exact_alias_index")==inventory_aliases,"Actual inventory history proof/index pointer differs")
  lib.verify_inventory_history_preservation(inventory,inventory_index,allocation)
  history_native_records.extend(lib._fixed_history_saved_native_records(inventory))
  archive_parent_controls_readback()
  relative_diagnostic_controls_readback()
  parent_diagnostic_controls_readback()
  catalog_projection_readback()
  for name in ("source_inclusion","source_closure"):
   produced=lib.read(lib.verify(accepted[name],True))
   lib.need(produced.get("inventory_history_opaque_leaf_proof")==inventory_proof and produced.get("inventory_history_opaque_aliases")==inventory_aliases,"Source A/I/C inventory history proof/index pointers differ")
  for r in owned+library_sources+pins:lib.verify(r,True)
  result=dict(schema="final-source-materialized-context-read-view-acceptance.v3",status="FINAL_CURRENT_SOURCE_MATERIALIZED_FIVE_PARENT_CONTEXT_AND_DERIVED_V2_CPU_ACCEPTED_NOT_STAGED_NOT_PUBLISHED",request=lib.rec(request),library_software_acceptance=q["library_software_acceptance"],mapper_software_acceptance=q["mapper_software_acceptance"],source_files=owned,library_software_terminal=library_terminal,mapper_source_files=pins,allocation=allocation,read_view_proof=proof,actual_new_library_acceptance=lib.rec(out/"acceptance.json"),source_inclusion=accepted["source_inclusion"],source_closure=accepted["source_closure"],vendor_example_opaque_leaf_proof=opaque_proof,vendor_example_opaque_aliases=opaque_aliases,finite_worker_control_proof=worker_proof,finite_worker_control_aliases=worker_aliases,inventory_history_opaque_leaf_proof=inventory_proof,inventory_history_opaque_aliases=inventory_aliases,archive_parent_history_opaque_leaf_proof=archive_parent_proof,archive_parent_history_opaque_aliases=archive_parent_aliases,relative_diagnostic_history_opaque_leaf_proof=relative_diagnostic_proof,relative_diagnostic_history_opaque_aliases=relative_diagnostic_aliases,parent_diagnostic_history_opaque_leaf_proof=parent_diagnostic_proof,parent_diagnostic_history_opaque_aliases=parent_diagnostic_aliases,raw_JSON_changed=False,unknown_relative_or_current_external_permission_added=False,source_staged=False,published=False,ACTIVE_changed=False)
  base.owned_source_readback(executed,owned,executed_before,owned_before);base.need(base.conditional_core_runtime()==runtime,"Original adapter source6/CORE runtime changed before result")
  result.update(original_executing_sources=executed,whole6_source_prepost_PASS=True,original_and_frozen_owned_bytes_identical=True,conditional_core_runtime=runtime,conditional_runtime_prepost_PASS=True)
  lib.verify_vendor_example_preservation(opaque,alias_data,allocation)
  lib.verify_finite_worker_preservation(worker,worker_index,allocation)
  lib.verify_inventory_history_preservation(inventory,inventory_index,allocation)
  archive_parent_controls_readback()
  relative_diagnostic_controls_readback()
  parent_diagnostic_controls_readback()
  catalog_projection_readback()
  descriptor=lib.dump(out/"context_adapter_acceptance.json",result)
  parent_ca_metadata=lib.stable_metadata(descriptor["path"])
  parent_ca=lib.read(lib.verify(descriptor,True))
  lib.need(parent_ca.get("parent_diagnostic_history_opaque_leaf_proof")==parent_diagnostic_proof and parent_ca.get("parent_diagnostic_history_opaque_aliases")==parent_diagnostic_aliases,"Actual CA parent-diagnostic pointer fork")
  lib.need(lib.rec(descriptor["path"])==descriptor and lib.stable_metadata(descriptor["path"])==parent_ca_metadata,"Actual CA changed during final parent-diagnostic JSON read")
  parent_diagnostic_graph_receipts["context_adapter_acceptance"]=descriptor
  parent_diagnostic_graph_metadata["context_adapter_acceptance"]=parent_ca_metadata
  parent_diagnostic_controls_readback()
  catalog_projection_readback()
  lib.verify_finite_worker_preservation(worker,worker_index,allocation)
  lib.verify_inventory_history_preservation(inventory,inventory_index,allocation)
  archive_parent_controls_readback()
  relative_diagnostic_controls_readback()
  parent_diagnostic_controls_readback()
  catalog_projection_readback()
  lib.verify_vendor_example_preservation(opaque,alias_data,allocation)
  base.owned_source_readback(executed,owned,executed_before,owned_before);base.need(base.conditional_core_runtime()==runtime,"Original adapter source6/CORE runtime changed after result")
  for family,saved in (("inventory13299",inventory),("archive13298",archive_parent),
                       ("relative13295",relative_diagnostic),("parent13290",parent_diagnostic)):
   lib._fixed_history_authority_fence(family,saved["authority_metadata_before"])
  lib.catalog_msa_gap_saved_fence(catalog_original_native)
  for name,receipt in parent_diagnostic_graph_receipts.items():
   lib.need(lib.rec(receipt["path"])==receipt and lib.stable_metadata(receipt["path"])==parent_diagnostic_graph_metadata[name],"Actual adapter13290 final graph bytes/native metadata changed before descriptor")
  history_final_native_sweep()
  print(json.dumps(dict(status=result["status"],acceptance=descriptor),sort_keys=True),flush=True)
 except Exception as e:
  base.dump(aux/"typed_incomplete.json",dict(status="FINAL_SOURCE_MATERIALIZED_CONTEXT_ADAPTER_TYPED_INCOMPLETE",failed_stage=phase,reason_type=type(e).__name__,reason=str(e),allocation=allocation,source_staged=False,raw_JSON_changed=False,ACTIVE_changed=False));raise
if __name__=="__main__":
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--request",required=True);ap.add_argument("--out",required=True);x=ap.parse_args();run(x.request,x.out)
