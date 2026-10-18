#!/usr/bin/env python3
"""Prepared exact-parent/field relative context boundaries; CPU execution pending."""
import copy,hashlib,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import exact_relative_bbf_context as a
def mapping():
 return {"schema":a.SCHEMA,"status":a.STATUS,"parent_manifest":dict(a.PARENT),"declared_relative_root":str(a.ROOT),"original_json_unchanged":True,"entries":[a.expected_entry(i)for i in range(6)]}
def relative(i=0):
 e=a.expected_entry(i);return {"path":e["original_relative_path"],"bytes":e["expected_bytes"],"sha256":e["expected_sha256"]}
class ContextContracts(unittest.TestCase):
 def test_exact_six_mapping_accepts(self):self.assertEqual(len(a.validate_mapping(mapping())),6)
 def test_exact_all_six_parent_field_canonicalization(self):
  for i in range(6):
   r,c=a.normalise(relative(i),a.PARENT,("outputs",str(i)),mapping())
   self.assertEqual(r,a.expected_entry(i)["canonical_receipt"]);self.assertEqual(c["source_field"],["outputs",str(i)])
 def test_mapping_wrong_status_rejected(self):
  m=mapping();m["status"]="PENDING"
  with self.assertRaises(ValueError):a.validate_mapping(m)
 def test_mapping_wrong_schema_rejected(self):
  m=mapping();m["schema"]="generic-relative.v1"
  with self.assertRaises(ValueError):a.validate_mapping(m)
 def test_mapping_parent_hash_changed_rejected(self):
  m=mapping();m["parent_manifest"]["sha256"]="e"*64
  with self.assertRaises(ValueError):a.validate_mapping(m)
 def test_mapping_parent_byte_count_changed_rejected(self):
  m=mapping();m["parent_manifest"]["bytes"]+=1
  with self.assertRaises(ValueError):a.validate_mapping(m)
 def test_mapping_root_changed_rejected(self):
  m=mapping();m["declared_relative_root"]=str(a.R)
  with self.assertRaises(ValueError):a.validate_mapping(m)
 def test_original_rewritten_claim_rejected(self):
  m=mapping();m["original_json_unchanged"]=False
  with self.assertRaises(ValueError):a.validate_mapping(m)
 def test_missing_relative_permission_rejected(self):
  m=mapping();m["entries"].pop()
  with self.assertRaises(ValueError):a.validate_mapping(m)
 def test_duplicate_relative_permission_rejected(self):
  m=mapping();m["entries"][5]=copy.deepcopy(m["entries"][0])
  with self.assertRaises(ValueError):a.validate_mapping(m)
 def test_unknown_relative_path_rejected(self):
  r=relative();r["path"]="runs/other/metrics.json"
  with self.assertRaises(ValueError):a.normalise(r,a.PARENT,("outputs","0"),mapping())
 def test_unknown_parent_even_same_basename_rejected(self):
  p={**a.PARENT,"path":str(a.ROOT/"runs/other/manifest.json")}
  with self.assertRaises(ValueError):a.normalise(relative(),p,("outputs","0"),mapping())
 def test_same_parent_path_different_hash_rejected(self):
  p={**a.PARENT,"sha256":"e"*64}
  with self.assertRaises(ValueError):a.normalise(relative(),p,("outputs","0"),mapping())
 def test_same_relative_bytes_wrong_field_rejected(self):
  with self.assertRaises(ValueError):a.normalise(relative(),a.PARENT,("inputs","0"),mapping())
 def test_same_relative_bytes_wrong_output_index_rejected(self):
  with self.assertRaises(ValueError):a.normalise(relative(),a.PARENT,("outputs","1"),mapping())
 def test_relative_sha_changed_rejected(self):
  r={**relative(),"sha256":"a"*64}
  with self.assertRaises(ValueError):a.normalise(r,a.PARENT,("outputs","0"),mapping())
 def test_relative_size_changed_rejected(self):
  r={**relative(),"bytes":1}
  with self.assertRaises(ValueError):a.normalise(r,a.PARENT,("outputs","0"),mapping())
 def test_path_traversal_rejected(self):
  r={**relative(),"path":"runs/review_13226/../../metrics.json"}
  with self.assertRaises(ValueError):a.normalise(r,a.PARENT,("outputs","0"),mapping())
 def test_canonical_unrelated_absolute_alias_rejected(self):
  m=mapping();m["entries"][0]["canonical_receipt"]["path"]=str(a.R/"other/metrics.json")
  with self.assertRaises(ValueError):a.validate_mapping(m)
 def test_canonical_hash_alias_changed_rejected(self):
  m=mapping();m["entries"][0]["canonical_receipt"]["sha256"]="e"*64
  with self.assertRaises(ValueError):a.validate_mapping(m)
 def test_extra_relative_permission_field_rejected(self):
  m=mapping();m["entries"][0]["allow_any_parent"]=True
  with self.assertRaises(ValueError):a.validate_mapping(m)
 def test_ordinary_absolute_receipt_passes_without_relative_permission(self):
  r=a.expected_entry(0)["canonical_receipt"];got,ctx=a.normalise(r,None,(),None)
  self.assertEqual(got,r);self.assertIsNone(ctx)
 def test_boolean_byte_count_rejected(self):
  with self.assertRaises(ValueError):a.receipt({"path":"/abs","bytes":True,"sha256":"a"*64})
 def test_original_json_unchanged_by_nested_walk(self):
  obj={"outputs":[relative(i)for i in range(6)]};old=copy.deepcopy(obj)
  rows=list(a.receipt_edges(obj,a.PARENT,mapping()));self.assertEqual(len(rows),6);self.assertEqual(obj,old)
 def test_unapproved_duplicate_context_checked_before_caller_dedup(self):
  good={"outputs":[relative(i)for i in range(6)],"unapproved":[relative(0)]}
  with self.assertRaises(ValueError):list(a.receipt_edges(good,a.PARENT,mapping()))
 def test_login_environment_cannot_start_mapping_hash_verification(self):
  self.assertEqual(a.strict_tres("cpu=1,mem=8G,gres/gpu=0")["cpu"],1)
  for tres in ("cpu=1,cpu=2","cpu=1,gres/gpu=1,gres/gpu=0","cpu=1,gres/gpu=0,gres/gpu:a100=1","cpu=true","mem=8G"):
   with self.subTest(tres=tres):
    with self.assertRaises(ValueError):a.strict_tres(tres)
  with patch.dict(os.environ,{},clear=True):
   with self.assertRaises(ValueError):a.verify_mapping_receipt({"path":str(a.R/"not_read"),"bytes":0,"sha256":"a"*64})

def manifest():
 return {"job_id":"13226","status":"BBF110_INDEPENDENT_DEVELOPMENT_DIAGNOSIS_CONTENT_ACCEPTED","outputs":[relative(i)for i in range(6)],"scores":{"negative_count":110},"inputs":[{"path":"/fixture/ordinary.json","bytes":1,"sha256":"a"*64}]}
class ReadViewAndRestoreContracts(unittest.TestCase):
 def mapper_contracts(self):
  sources=[{"path":"/fixture/"+n,"bytes":1,"sha256":"a"*64}for n in sorted(a.PACKAGE_NAMES)]
  accepted={"schema":"exact-current-context-mapper-acceptance.v4","status":"EXACT_BBF6_RECOVERED5_NINE_ANNOTATIONS_ARCHIVE588_AND_EIGHT_SOURCE_ALIASES_MAPPER_CPU_ACCEPTED","source_files":sources}
  return accepted,{"status":"PASS","tests":a.CONTRACTS,"failures":0,"errors":0,"tested_source_files":sources,"owned_python_compile_PASS":True,"bash_syntax_PASS":True}
 def test_saved_exact_mapper_contracts_and_source_universe_accept(self):
  accepted,c=self.mapper_contracts();self.assertEqual(len(a.mapper_contract_shape(accepted,c)),14)
 def test_saved_pending_mapper_contracts_rejected(self):
  accepted,c=self.mapper_contracts();c["status"]="PENDING"
  with self.assertRaises(ValueError):a.mapper_contract_shape(accepted,c)
 def test_saved_wrong_mapper_contract_count_rejected(self):
  accepted,c=self.mapper_contracts();c["tests"]-=1
  with self.assertRaises(ValueError):a.mapper_contract_shape(accepted,c)
 def test_saved_mapper_tested_source_mismatch_rejected(self):
  accepted,c=self.mapper_contracts();c["tested_source_files"]=copy.deepcopy(c["tested_source_files"]);c["tested_source_files"][0]["sha256"]="e"*64
  with self.assertRaises(ValueError):a.mapper_contract_shape(accepted,c)
 def test_saved_duplicate_mapper_source_rejected(self):
  accepted,c=self.mapper_contracts();accepted["source_files"][5]=copy.deepcopy(accepted["source_files"][0])
  with self.assertRaises(ValueError):a.mapper_contract_shape(accepted,c)
 def test_saved_unrelated_mapper_source_rejected(self):
  accepted,c=self.mapper_contracts();accepted["source_files"][5]["path"]="/fixture/unrelated.py"
  with self.assertRaises(ValueError):a.mapper_contract_shape(accepted,c)
 def test_new_context_proof_has_only_absolute_receipt_edges(self):
  _,contexts=a.exact_manifest_view(a.PARENT,manifest(),mapping())
  edges=list(a.receipt_edges({"proof":contexts},None,mapping()))
  self.assertEqual(len(edges),12);self.assertTrue(all(Path(r["path"]).is_absolute()for r,_,_ in edges))
  self.assertTrue(all("original_receipt"not in c for c in contexts))
 def test_view_changes_only_six_path_fields(self):
  obj=manifest();old=copy.deepcopy(obj);view,contexts=a.exact_manifest_view(a.PARENT,obj,mapping())
  self.assertEqual(obj,old);self.assertEqual(len(contexts),6)
  for i in range(6):view["outputs"][i]["path"]=old["outputs"][i]["path"]
  self.assertEqual(view,old)
 def test_wrong_manifest_role_rejected(self):
  obj=manifest();obj["status"]="SOFTWARE_PASS"
  with self.assertRaises(ValueError):a.exact_manifest_view(a.PARENT,obj,mapping())
 def test_wrong_manifest_job_rejected(self):
  obj=manifest();obj["job_id"]="13227"
  with self.assertRaises(ValueError):a.exact_manifest_view(a.PARENT,obj,mapping())
 def test_extra_manifest_output_rejected(self):
  obj=manifest();obj["outputs"].append(relative())
  with self.assertRaises(ValueError):a.exact_manifest_view(a.PARENT,obj,mapping())
 def test_swapped_manifest_outputs_rejected(self):
  obj=manifest();obj["outputs"][0],obj["outputs"][1]=obj["outputs"][1],obj["outputs"][0]
  with self.assertRaises(ValueError):a.exact_manifest_view(a.PARENT,obj,mapping())
 def test_prealtered_raw_manifest_rejected(self):
  obj=manifest();obj["outputs"][0]["path"]=a.expected_entry(0)["canonical_receipt"]["path"]
  with self.assertRaises(ValueError):a.exact_manifest_view(a.PARENT,obj,mapping())
 def test_unrelated_reader_path_passes_through(self):
  with patch.object(a,"verify_mapping_receipt",return_value=(mapping(),{"fixture_only":True})):
   reader=a.VerifiedContextReader({},lambda p:{"other":str(p)})
   self.assertEqual(reader("/other"),{"other":"/other"});self.assertEqual(reader.used,[])
 def test_exact_reader_view_preserves_negative_score(self):
  with patch.object(a,"verify_mapping_receipt",return_value=(mapping(),{"fixture_only":True})),patch.object(a,"verify_bytes",return_value=Path(a.PARENT["path"])):
   reader=a.VerifiedContextReader({},lambda p:manifest());view=reader(a.PARENT["path"])
   self.assertEqual(view["scores"],{"negative_count":110});self.assertEqual(len(reader.proof()["read_views_used"]),1)
 def test_reader_unknown_alias_rejected(self):
  with patch.object(a,"verify_mapping_receipt",return_value=(mapping(),{"fixture_only":True})):
   with self.assertRaises(ValueError):a.VerifiedContextReader({},lambda p:{},[{"logical":{**a.PARENT,"path":"/wrong"},"physical":a.PARENT}])
 def test_reader_alias_different_bytes_rejected(self):
  with patch.object(a,"verify_mapping_receipt",return_value=(mapping(),{"fixture_only":True})):
   with self.assertRaises(ValueError):a.VerifiedContextReader({},lambda p:{},[{"logical":a.PARENT,"physical":{**a.PARENT,"bytes":1}}])
 def test_reader_duplicate_alias_rejected(self):
  with patch.object(a,"verify_mapping_receipt",return_value=(mapping(),{"fixture_only":True})),patch.object(a,"verify_bytes",return_value=Path(a.PARENT["path"])):
   with self.assertRaises(ValueError):a.VerifiedContextReader({},lambda p:{},[{"logical":a.PARENT,"physical":a.PARENT}])
 def test_restored_index_accepts_explicit_nested_path(self):
  with tempfile.TemporaryDirectory()as d:
   root,entries=a.restored_index([{"logical":a.PARENT,"restored_relative":"metadata/manifest.json"}],d)
   self.assertEqual(next(iter(entries.values())),Path(d)/"metadata/manifest.json")
 def test_restored_index_rejects_absolute_path(self):
  with tempfile.TemporaryDirectory()as d:
   with self.assertRaises(ValueError):a.restored_index([{"logical":a.PARENT,"restored_relative":"/tmp/manifest"}],d)
 def test_restored_index_rejects_parent_traversal(self):
  with tempfile.TemporaryDirectory()as d:
   with self.assertRaises(ValueError):a.restored_index([{"logical":a.PARENT,"restored_relative":"../manifest"}],d)
 def test_restored_index_rejects_dot_normalization(self):
  with tempfile.TemporaryDirectory()as d:
   with self.assertRaises(ValueError):a.restored_index([{"logical":a.PARENT,"restored_relative":"metadata/./manifest"}],d)
 def test_restored_index_rejects_duplicate_identity(self):
  with tempfile.TemporaryDirectory()as d:
   row={"logical":a.PARENT,"restored_relative":"manifest"}
   with self.assertRaises(ValueError):a.restored_index([row,row],d)
 def test_restored_index_rejects_symlink_escape(self):
  with tempfile.TemporaryDirectory()as d:
   (Path(d)/"escape").symlink_to("/tmp")
   with self.assertRaises(ValueError):a.restored_index([{"logical":a.PARENT,"restored_relative":"escape/manifest"}],d)
 def test_restored_root_symlink_rejected(self):
  with tempfile.TemporaryDirectory()as d:
   (Path(d)/"alias").symlink_to(d)
   with self.assertRaises(ValueError):a.restored_index([],str(Path(d)/"alias"))
 def test_restored_root_cannot_be_live_scientific_tree(self):
  with patch.object(Path,"is_dir",return_value=True),patch.object(Path,"resolve",lambda p:p):
   with self.assertRaises(ValueError):a.restored_index([],str(a.ROOT))
 def test_restored_root_cannot_be_live_authority_root(self):
  with patch.object(Path,"is_dir",return_value=True),patch.object(Path,"resolve",lambda p:p):
   with self.assertRaises(ValueError):a.restored_index([],str(a.R))
 def test_restored_missing_index_never_opens_live_path(self):
  with tempfile.TemporaryDirectory()as d:
   with patch.object(Path,"open",side_effect=AssertionError("must not read live bytes")):
    with self.assertRaises(ValueError):a.restored_bytes(a.PARENT,Path(d),{})
 def test_restored_index_different_sha_cannot_substitute(self):
  with tempfile.TemporaryDirectory()as d:
   root,entries=a.restored_index([{"logical":{**a.PARENT,"sha256":"e"*64},"restored_relative":"manifest"}],d)
   with self.assertRaises(ValueError):a.restored_bytes(a.PARENT,root,entries)
 def test_restored_toy_bytes_exact_match(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/"toy";p.write_bytes(b"toy")
   logical={"path":"/fixture/toy","bytes":3,"sha256":hashlib.sha256(b"toy").hexdigest()}
   root,entries=a.restored_index([{"logical":logical,"restored_relative":"toy"}],d)
   self.assertEqual(a.restored_bytes(logical,root,entries),p)
 def test_restored_wrong_toy_bytes_rejected(self):
  with tempfile.TemporaryDirectory()as d:
   (Path(d)/"toy").write_bytes(b"bad")
   logical={"path":"/fixture/toy","bytes":3,"sha256":hashlib.sha256(b"toy").hexdigest()}
   root,entries=a.restored_index([{"logical":logical,"restored_relative":"toy"}],d)
   with self.assertRaises(ValueError):a.restored_bytes(logical,root,entries)
 def test_login_environment_cannot_start_restored_hash_verification(self):
  with patch.dict(os.environ,{},clear=True):
   with self.assertRaises(ValueError):a.verify_restored_mapping({}, "/not_read",[])
if __name__=="__main__":unittest.main()

