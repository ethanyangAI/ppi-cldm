#!/usr/bin/env python3
"""Synthetic boundaries only; actual history/producer proofs are separate CPU gates."""
import copy,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import historical_annotation_context as a
import exact_relative_bbf_context as b
class AnnotationContracts(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.oldR=a.R;self.oldBR=b.R;self.oldP=a.PARENT
  a.R=b.R=self.root
  def text(name,s):
   p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s);p.chmod(0o444);return b.receipt(dict(path=str(p),bytes=p.stat().st_size,sha256=__import__("hashlib").sha256(p.read_bytes()).hexdigest()))
  def meta(name,obj):return text(name,json.dumps(obj,sort_keys=True)+"\n")
  self.text=text;self.meta=meta
  self.raw={"entries":[dict(sequence="SYNTHETIC_SEQUENCE_"+str(i),other={"keep":i})for i in range(3)],"recovery":copy.deepcopy(a.RECOVERY_MARKER),"other":[{"keep":"entire original object"}]}
  for row in a.ROWS:self.raw["entries"][int(row["source_field"][1])][row["source_field"][2]]=a.logical(row)
  self.parent=meta("parent.json",self.raw);a.PARENT=self.parent
  self.sources=[text("producer/"+n,"#SBATCH --job-name=test9_source_relative_v10\n"if n.endswith(".sbatch")else"SYNTHETIC_SOURCE_ONLY\n")for n in sorted(a.SOURCE_NAMES)]
  self.by={Path(r["path"]).name:r for r in self.sources}
  log=text("contracts.log","SYNTHETIC_SOFTWARE_BOUNDARY_ONLY\n");contracts=meta("contracts.json",dict(status="PASS",tests=122,failures=0,errors=0,log=log));snapshot=meta("snapshot.json",dict(source_receipts=self.sources))
  software=meta("software.json",dict(schema="source-refresh-relative-software-acceptance.v10",status="SOURCE_REFRESH_RELATIVE_SOFTWARE_CPU_ACCEPTED_ACTUAL_SOURCE_AUDIT_PENDING",tests_expected=122,compiled_all_python=True,bash_syntax_checked=True,contracts=contracts,source_snapshot=snapshot,allocation={"job_id":"SYNTHETIC"}))
  prior=meta("prior.json",{"status":"SYNTHETIC_HISTORY"});lineage=[meta("index.json",{}),meta("pack.json",{}),prior,self.by["delivery_graph_v2.py"],self.by["source_delivery_refresh_v10.py"],software]
  self.m=dict(schema=a.SCHEMA,status=a.STATUS,parent_manifest=dict(a.PARENT),recovery_status=a.RECOVERY_MARKER["status"],recovery_missing_files=a.RECOVERY_MARKER["missing_files"],recovery_marker=copy.deepcopy(a.RECOVERY_MARKER),entries=[a.expected_entry(i)for i in range(9)],anchor={**a.ROWS[8],"canonical_receipt":None,"historical_file_restored":False,"status":a.ANNOTATION_STATUS},historical_annotation_n=9,canonical_external_text_edge_n=0,unresolved_current_external_edges_allowed=False,original_json_unchanged=True,external_files_read=False,current_declared_graph_only=True,raw_byte_acceptance=False,actual_current_sequence_input_parent_bytes_verified=True,accepted_lineage_receipts=lineage,producer_executed_source=self.by["source_delivery_refresh_v10.py"],producer_actual_software_gate=software,source_graph_selector=self.by["delivery_graph_v2.py"],prior_accepted_inclusion=prior)
  self.mapping=meta("mapping.json",self.m)
 def tearDown(self):a.R=self.oldR;b.R=self.oldBR;a.PARENT=self.oldP;self.tmp.cleanup()
 def bad(self,mutator):
  m=copy.deepcopy(self.m);mutator(m)
  with self.assertRaises(ValueError):a.validate_mapping(m)
 def test_exact_nine_schema_accepts(self):self.assertEqual(len(a.validate_mapping(self.m)),9)
 def test_wrong_map_schema_rejected(self):self.bad(lambda m:m.update(schema="exact-recovered-legacy-receipt-context.v1"))
 def test_wrong_map_status_rejected(self):self.bad(lambda m:m.update(status="PENDING"))
 def test_parent_hash_changed_rejected(self):self.bad(lambda m:m["parent_manifest"].update(sha256="e"*64))
 def test_parent_size_changed_rejected(self):self.bad(lambda m:m["parent_manifest"].update(bytes=1))
 def test_recovery_marker_status_changed_rejected(self):self.bad(lambda m:m["recovery_marker"].update(status="STRUCTURES_RECOVERED"))
 def test_missing_files_literal_changed_rejected(self):self.bad(lambda m:m.update(recovery_missing_files="restored"))
 def test_history_canonical_child_cannot_be_manufactured(self):self.bad(lambda m:m["entries"][0].update(canonical_receipt=self.parent))
 def test_raw_history_acceptance_cannot_be_true(self):self.bad(lambda m:m["entries"][0].update(raw_byte_acceptance=True))
 def test_current_execution_cannot_be_true(self):self.bad(lambda m:m["entries"][0].update(current_execution_allowed=True))
 def test_historical_restored_cannot_be_true(self):self.bad(lambda m:m["entries"][0].update(historical_file_restored=True))
 def test_duplicate_annotation_field_rejected(self):self.bad(lambda m:m["entries"].__setitem__(8,copy.deepcopy(m["entries"][0])))
 def test_missing_annotation_field_rejected(self):self.bad(lambda m:m["entries"].pop())
 def test_unknown_tenth_annotation_rejected(self):self.bad(lambda m:m["entries"].append(copy.deepcopy(m["entries"][0])))
 def test_unknown_field_rejected(self):self.bad(lambda m:m["entries"][0].update(source_field=["entries","0","sequence"]))
 def test_nonstring_field_rejected(self):self.bad(lambda m:m["entries"][0].update(source_field=["entries",0,"native"]))
 def test_annotation_path_identity_changed_rejected(self):self.bad(lambda m:m["entries"][0].update(original_logical_path="/work/other/native.pdb"))
 def test_annotation_hash_identity_changed_rejected(self):self.bad(lambda m:m["entries"][0].update(expected_sha256="e"*64))
 def test_missing_actual_producer_lineage_rejected(self):self.bad(lambda m:m["accepted_lineage_receipts"].pop())
 def test_anchor_claiming_restored_bytes_rejected(self):self.bad(lambda m:m["anchor"].update(canonical_receipt=self.parent))
 def test_external_read_claim_rejected(self):self.bad(lambda m:m.update(external_files_read=True))
 def test_generic_external_permission_rejected(self):self.bad(lambda m:m.update(unresolved_current_external_edges_allowed=True))
 def test_actual_parent_view_only_nine_fields_changed(self):
  before=copy.deepcopy(self.raw);view,contexts=a.exact_manifest_view(a.PARENT,self.raw,self.m)
  self.assertEqual(self.raw,before);self.assertEqual(len(contexts),9)
  for row in a.ROWS:a.replace_field(view,row["source_field"],a.field_value(before,row["source_field"]))
  self.assertEqual(view,before)
 def test_new_scalar_proof_has_no_external_receipt_edges(self):
  view,contexts=a.exact_manifest_view(a.PARENT,self.raw,self.m)
  self.assertTrue(all(not({"path","bytes","sha256"}<=c.keys())for c in contexts))
  self.assertEqual(list(b.receipt_edges(view,a.PARENT,{})),[])
 def test_swapped_original_fields_rejected(self):
  raw=copy.deepcopy(self.raw);raw["entries"][0]["native"],raw["entries"][0]["backbone"]=raw["entries"][0]["backbone"],raw["entries"][0]["native"]
  with self.assertRaises(ValueError):a.exact_manifest_view(a.PARENT,raw,self.m)
 def test_same_historical_identity_wrong_field_context_rejected(self):
  with self.assertRaises(ValueError):a.normalise_edge(a.logical(a.ROWS[0]),a.PARENT,("entries","1","native"),self.m)
 def test_same_parent_path_wrong_sha_context_rejected(self):
  with self.assertRaises(ValueError):a.normalise_edge(a.logical(a.ROWS[0]),{**a.PARENT,"sha256":"e"*64},a.ROWS[0]["source_field"],self.m)
 def test_unknown_operative_external_edge_rejected(self):
  with self.assertRaises(ValueError):a.normalise_edge(dict(path="/work/current.pdb",bytes=1,sha256="e"*64),a.PARENT,("inputs","native"),self.m)
 def test_exact_annotation_returns_null_not_accepted_bytes(self):
  canonical,proof=a.normalise_edge(a.logical(a.ROWS[0]),a.PARENT,a.ROWS[0]["source_field"],self.m)
  self.assertIsNone(canonical);self.assertIs(proof["raw_byte_acceptance"],False)
 def test_actual_parent_producer_bytes_verified(self):
  proof=a.verify_content(self.m,lambda r:b.verify_bytes(r,True));self.assertEqual(proof["historical_annotation_n"],9);self.assertFalse(proof["raw_historical_bytes_accepted"])
 def test_producer_source_drift_rejected(self):
  p=Path(self.by["source_delivery_refresh_v10.py"]["path"]);p.chmod(0o644);p.write_text("DRIFT")
  with self.assertRaises(ValueError):a.verify_content(self.m,lambda r:b.verify_bytes(r,True))
 def test_parent_byte_drift_rejected(self):
  p=Path(self.parent["path"]);p.chmod(0o644);p.write_text("DRIFT")
  with self.assertRaises(ValueError):a.verify_content(self.m,lambda r:b.verify_bytes(r,True))
 def restored(self):
  files=[p for p in self.root.rglob("*")if p.is_file()];dest=self.root/"restored";dest.mkdir();index=[]
  for i,p in enumerate(files):
   r=dict(path=str(p),bytes=p.stat().st_size,sha256=__import__("hashlib").sha256(p.read_bytes()).hexdigest());rel=str(i)+"/"+p.name;target=dest/rel;target.parent.mkdir();shutil.copyfile(p,target);target.chmod(0o444);index.append(dict(logical=r,restored_relative=rel))
  return dest,index
 def test_restore_uses_only_restored_bytes_after_live_parent_drift(self):
  dest,index=self.restored();p=Path(self.parent["path"]);p.chmod(0o644);p.write_text("LIVE_DRIFT")
  with patch.object(b,"cpu_guard",return_value={"toy_only":True}):m,proof=a.verify_restored_mapping(self.mapping,dest,index)
  self.assertTrue(proof["no_live_root_fallback"]);self.assertTrue(all(Path(x).is_relative_to(dest)for x in proof["read_paths"]))
 def test_missing_restored_parent_never_falls_back_live(self):
  dest,index=self.restored();row=next(x for x in index if x["logical"]==self.parent);(dest/row["restored_relative"]).unlink()
  with patch.object(b,"cpu_guard",return_value={"toy_only":True}):
   with self.assertRaises(ValueError):a.verify_restored_mapping(self.mapping,dest,index)
 def test_missing_restored_producer_never_falls_back_live(self):
  dest,index=self.restored();row=next(x for x in index if x["logical"]==self.by["source_delivery_refresh_v10.py"]);(dest/row["restored_relative"]).unlink()
  with patch.object(b,"cpu_guard",return_value={"toy_only":True}):
   with self.assertRaises(ValueError):a.verify_restored_mapping(self.mapping,dest,index)
 def test_login_cannot_start_current_history_verification(self):
  with patch.dict(__import__("os").environ,{},clear=True):
   with self.assertRaises(ValueError):a.verify_mapping_receipt(self.mapping)
 def test_verified_view_preserves_disk_bytes_and_sequences(self):
  before=Path(self.parent["path"]).read_bytes()
  with patch.object(a,"verify_mapping_receipt",return_value=(self.m,{"toy_only":True})):
   reader=a.VerifiedHistoricalAnnotationReader(self.mapping,lambda p:json.loads(Path(p).read_text()));view=reader(self.parent["path"])
  self.assertEqual([e["sequence"]for e in view["entries"]],[e["sequence"]for e in self.raw["entries"]]);self.assertEqual(Path(self.parent["path"]).read_bytes(),before);self.assertEqual(len(reader.used[0]["contexts"]),9)
 def test_unrelated_path_read_passes_through(self):
  with patch.object(a,"verify_mapping_receipt",return_value=(self.m,{"toy_only":True})):
   reader=a.VerifiedHistoricalAnnotationReader(self.mapping,lambda p:{"other":str(p)});self.assertEqual(reader(str(self.root/"ordinary")),{"other":str(self.root/"ordinary")});self.assertFalse(reader.used)
 def test_unapproved_parent_alias_rejected(self):
  with patch.object(a,"verify_mapping_receipt",return_value=(self.m,{"toy_only":True})):
   with self.assertRaises(ValueError):a.VerifiedHistoricalAnnotationReader(self.mapping,lambda p:{},[{"logical":{**a.PARENT,"sha256":"e"*64},"physical":a.PARENT}])
 def terminal_map(self):
  m=copy.deepcopy(self.m);old=m["producer_actual_software_gate"];obj=json.loads(Path(old["path"]).read_text());obj["allocation"]["job_id"]="999"
  new=self.meta("terminal_software.json",obj);m["producer_actual_software_gate"]=new;m["accepted_lineage_receipts"]=[new if r==old else r for r in m["accepted_lineage_receipts"]];return m
 def test_actual_launcher_text_and_numeric_terminal_cpu_accept(self):
  m=self.terminal_map();raw="999|COMPLETED|0:0|7|cpu=1,node=1|u21111210118|u21111210118|test9_source_relative_v10|organ|\n"
  with patch.object(a.subprocess,"check_output",return_value=raw):got=a.producer_terminal(m,lambda r:b.verify_bytes(r,True))
  self.assertEqual(got["jobname"],"test9_source_relative_v10");self.assertEqual(got["allocated_GPUs"],0)
 def test_actual_wrong_launcher_name_or_terminal_gpu_owner_rejected(self):
  m=self.terminal_map();base="999|COMPLETED|0:0|7|cpu=1,node=1|u21111210118|u21111210118|test9_source_relative_v10|organ|\n"
  for raw in (base.replace("test9_source_relative_v10","test9_source_relative_v5"),base.replace("cpu=1,node=1","cpu=1,gres/gpu=1"),base.replace("|organ|","|wrongpartition|")):
   with self.subTest(raw=raw),patch.object(a.subprocess,"check_output",return_value=raw):
    with self.assertRaises(ValueError):a.producer_terminal(m,lambda r:b.verify_bytes(r,True))
 def test_restored_writable_authority_metadata_rejected(self):
  dest,index=self.restored()
  for logical in (self.mapping,self.parent,self.by["source_delivery_refresh_v10.py"]):
   with self.subTest(path=logical["path"]):
    row=next(x for x in index if x["logical"]==logical);target=dest/row["restored_relative"];target.chmod(0o644)
    with patch.object(b,"cpu_guard",return_value={"toy_only":True}):
     with self.assertRaises(ValueError):a.verify_restored_mapping(self.mapping,dest,index)
    target.chmod(0o444)
 def source_bundle_case(self):
  import context_consumer as c
  scope_patch=patch.object(c.s,"verify_source_alias_scope",return_value=({},{"SYNTHETIC_PREEXISTING_CONTEXT_BOUNDARY_ONLY":True}));scope_patch.start();self.addCleanup(scope_patch.stop)
  m=self.terminal_map();mapping=self.meta("bound_mapping.json",m);self.recovered=self.meta("recovered_pointer_only.json",dict(producer_executed_source=m["producer_executed_source"],producer_actual_software_gate=m["producer_actual_software_gate"]));relative=dict(path=str(self.root/"relative.json"),bytes=1,sha256="a"*64)
  import archive_member_context as arc
  apr=dict(schema=arc.PROOF_SCHEMA,status=arc.PROOF_STATUS,historical_archive_context_parent_n=len(arc.ARCHIVES),archive_member_n=arc.total(),all_regular_members_exactly_verified=True,original_index_JSON_bytes_unchanged=True,archive_extracted=False,archived_JSON_payload_parsed=False,current_file_restored=False,current_execution_authorized=False,new_scientific_inference=False,archives=[dict(**s,regular_members=[{k:v for k,v in arc.entry(s,i,dict(path="synthetic/"+str(j)+"/"+str(i)+".txt",bytes=1,sha256="a"*64)).items()if k!="source_parent"}for i in range(s["member_count"])],directory_n=0,archive_bytes_verified_before_and_after=True,extracted=False,archived_JSON_payload_parsed=False)for j,s in enumerate(arc.ARCHIVES)])
  producer_proof=self.meta("synthetic_archive_byte_proof.json",apr)
  am=dict(schema=arc.SCHEMA,status=arc.STATUS,current_declared_graph_only=True,historical_archive_context_parent_n=len(arc.ARCHIVES),archive_member_n=arc.total(),all588_declared_member_edges_observed=True,all588_member_bytes_independently_verified_in_archives=True,original_index_JSON_bytes_unchanged=True,archive_extracted=False,archived_JSON_payload_parsed=False,current_file_restored=False,current_execution_authorized=False,new_scientific_inference=False,unknown_relative_edges_allowed=False,external_files_read=False,archive_member_verification=producer_proof,archives=[dict(**s,entries=[arc.entry(s,i,dict(path="synthetic/"+str(j)+"/"+str(i)+".txt",bytes=1,sha256="a"*64))for i in range(s["member_count"])])for j,s in enumerate(arc.ARCHIVES)],accepted_lineage_receipts=m["accepted_lineage_receipts"],producer_executed_source=m["producer_executed_source"],producer_actual_software_gate=m["producer_actual_software_gate"],source_graph_selector=m["source_graph_selector"],prior_accepted_inclusion=m["prior_accepted_inclusion"])
  self.archive=self.meta("synthetic_archive_mapping.json",am)
  closure=self.meta("source_closure.json",dict(relative_receipt_context_mapping=relative,external_historical_receipt_context_mapping=mapping,current_recovered_relative_receipt_context_mapping=self.recovered,current_recovered_evidence_file_n=5,archive_member_receipt_context_mapping=self.archive,archive_member_verification=producer_proof,historical_archive_context_parent_n=2,archive_member_n=588,historical_provenance_annotation_n=9,external_files_read=False))
  binding=self.meta("software_gate_binding.json",dict(status="ACTUAL_SOFTWARE_GATE_BOUND_TO_SOURCE_REFRESH_V10",software_acceptance=m["producer_actual_software_gate"]))
  inclusion=self.meta("source_inclusion.json",dict(status="SOURCE_INCLUSION_AUDIT_PASS",applied=False,issues=[],source_receipt_closure=closure,allocation={"job_id":"999"},runner_source_snapshot=sorted([r for r in self.sources if Path(r["path"]).suffix in {".py",".sbatch"}],key=lambda r:r["path"])))
  base=self.meta("source_base.json",dict(schema="source-delivery-refresh.v3",status="CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY",source_issues=0,source_staged=False,relative_receipt_context_mapping=relative,external_historical_receipt_context_mapping=mapping,current_recovered_relative_receipt_context_mapping=self.recovered,current_recovered_evidence_file_n=5,archive_member_receipt_context_mapping=self.archive,archive_member_verification=producer_proof,historical_archive_context_parent_n=2,archive_member_n=588,historical_provenance_annotation_n=9,external_files_read=False,source_closure=closure,source_inclusion=inclusion,software_gate_binding=binding))
  return c,base,relative,mapping,inclusion,binding
 def test_actual_source_base_binds_same_v10_software_source_job(self):
  c,base,relative,mapping,inc,binding=self.source_bundle_case()
  got,closure=c.source_bundle(base,relative,mapping,lambda r:b.verify_bytes(r,True),self.recovered,self.archive);self.assertEqual(got["schema"],"source-delivery-refresh.v3")
 def test_source_base_wrong_job_software_pointer_or_v5_literal_rejected(self):
  c,base,relative,mapping,inc,binding=self.source_bundle_case();baseobj=json.loads(Path(base["path"]).read_text())
  for field,change in (("source_inclusion",{"allocation":{"job_id":"998"}}),("software_gate_binding",{"software_acceptance":self.parent}),("software_gate_binding",{"status":"ACTUAL_SOFTWARE_GATE_BOUND_TO_SOURCE_REFRESH_V5"})):
   with self.subTest(field=field,change=change):
    obj=json.loads(Path(baseobj[field]["path"]).read_text());obj.update(change)
    fork=self.meta("fork_"+str(len(list(self.root.glob("fork_*"))))+".json",obj);new=self.meta("base_"+str(len(list(self.root.glob("base_*"))))+".json",{**baseobj,field:fork})
    with self.assertRaises(ValueError):c.source_bundle(new,relative,mapping,lambda r:b.verify_bytes(r,True),self.recovered,self.archive)
class SourceV10Contracts(unittest.TestCase):
 def case(self):
  relative=dict(path="/fixture/relative.json",bytes=1,sha256="a"*64);history=dict(path="/fixture/history.json",bytes=1,sha256="b"*64)
  closure=dict(relative_receipt_context_mapping=relative,external_historical_receipt_context_mapping=history,historical_provenance_annotation_n=9,external_files_read=False)
  base=dict(schema="source-delivery-refresh.v3",status="CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY",source_issues=0,source_staged=False,**closure)
  return base,closure,relative,history
 def test_actual_v6_v3_source_schema_supported(self):self.assertTrue(a.source_base_contract(*self.case()))
 def test_old_v2_schema_cannot_be_relabelled(self):
  b0,c,r,h=self.case();b0["schema"]="source-delivery-refresh.v2"
  with self.assertRaises(ValueError):a.source_base_contract(b0,c,r,h)
 def test_history_map_pointer_fork_rejected(self):
  b0,c,r,h=self.case();c["external_historical_receipt_context_mapping"]={**h,"sha256":"e"*64}
  with self.assertRaises(ValueError):a.source_base_contract(b0,c,r,h)
 def test_wrong_annotation_or_external_count_rejected(self):
  for field,v in (("historical_provenance_annotation_n",8),("historical_provenance_annotation_n",10)):
   with self.subTest(field=field):
    b0,c,r,h=self.case();b0[field]=v
    with self.assertRaises(ValueError):a.source_base_contract(b0,c,r,h)
if __name__=="__main__":unittest.main()
