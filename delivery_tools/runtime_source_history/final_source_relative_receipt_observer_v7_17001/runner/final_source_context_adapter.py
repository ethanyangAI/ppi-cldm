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
  proof=lib.dump(aux/"five_parent_context_reader_proof.json",reader.proof());accepted=lib.read(out/"acceptance.json")
  lib.need(accepted.get("schema")=="final-source-closure-acceptance.v3"and accepted.get("status")=="FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED","Actual new3path source closure did not qualify")
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
  inventory_proof=accepted["inventory_history_opaque_leaf_proof"];inventory_aliases=accepted["inventory_history_opaque_aliases"]
  lib.verify(inventory_proof,True);lib.verify(inventory_aliases,True)
  inventory=lib.read(inventory_proof["path"]);inventory_index=lib.read(inventory_aliases["path"])
  lib.need(inventory.get("exact_alias_index")==inventory_aliases,"Actual inventory history proof/index pointer differs")
  lib.verify_inventory_history_preservation(inventory,inventory_index,allocation)
  for name in ("source_inclusion","source_closure"):
   produced=lib.read(lib.verify(accepted[name],True))
   lib.need(produced.get("inventory_history_opaque_leaf_proof")==inventory_proof and produced.get("inventory_history_opaque_aliases")==inventory_aliases,"Source A/I/C inventory history proof/index pointers differ")
  for r in owned+library_sources+pins:lib.verify(r,True)
  result=dict(schema="final-source-materialized-context-read-view-acceptance.v3",status="FINAL_CURRENT_SOURCE_MATERIALIZED_FIVE_PARENT_CONTEXT_AND_DERIVED_V2_CPU_ACCEPTED_NOT_STAGED_NOT_PUBLISHED",request=lib.rec(request),library_software_acceptance=q["library_software_acceptance"],mapper_software_acceptance=q["mapper_software_acceptance"],source_files=owned,library_software_terminal=library_terminal,mapper_source_files=pins,allocation=allocation,read_view_proof=proof,actual_new_library_acceptance=lib.rec(out/"acceptance.json"),source_inclusion=accepted["source_inclusion"],source_closure=accepted["source_closure"],vendor_example_opaque_leaf_proof=opaque_proof,vendor_example_opaque_aliases=opaque_aliases,finite_worker_control_proof=worker_proof,finite_worker_control_aliases=worker_aliases,inventory_history_opaque_leaf_proof=inventory_proof,inventory_history_opaque_aliases=inventory_aliases,raw_JSON_changed=False,unknown_relative_or_current_external_permission_added=False,source_staged=False,published=False,ACTIVE_changed=False)
  base.owned_source_readback(executed,owned,executed_before,owned_before);base.need(base.conditional_core_runtime()==runtime,"Original adapter source6/CORE runtime changed before result")
  result.update(original_executing_sources=executed,whole6_source_prepost_PASS=True,original_and_frozen_owned_bytes_identical=True,conditional_core_runtime=runtime,conditional_runtime_prepost_PASS=True)
  lib.verify_vendor_example_preservation(opaque,alias_data,allocation)
  lib.verify_finite_worker_preservation(worker,worker_index,allocation)
  lib.verify_inventory_history_preservation(inventory,inventory_index,allocation)
  descriptor=lib.dump(out/"context_adapter_acceptance.json",result)
  lib.verify_finite_worker_preservation(worker,worker_index,allocation)
  lib.verify_inventory_history_preservation(inventory,inventory_index,allocation)
  lib.verify_vendor_example_preservation(opaque,alias_data,allocation)
  base.owned_source_readback(executed,owned,executed_before,owned_before);base.need(base.conditional_core_runtime()==runtime,"Original adapter source6/CORE runtime changed after result")
  print(json.dumps(dict(status=result["status"],acceptance=descriptor),sort_keys=True),flush=True)
 except Exception as e:
  base.dump(aux/"typed_incomplete.json",dict(status="FINAL_SOURCE_MATERIALIZED_CONTEXT_ADAPTER_TYPED_INCOMPLETE",failed_stage=phase,reason_type=type(e).__name__,reason=str(e),allocation=allocation,source_staged=False,raw_JSON_changed=False,ACTIVE_changed=False));raise
if __name__=="__main__":
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--request",required=True);ap.add_argument("--out",required=True);x=ap.parse_args();run(x.request,x.out)
