"""Synthetic five-child boundaries only; actual producer proof is a separate CPU gate."""
import copy,hashlib,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import recovered_five_context as a
import exact_relative_bbf_context as b
class RecoveredFiveContracts(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.saved=(b.R,a.R,a.PARENT,a.ROWS);b.R=a.R=self.root
  def file(name,text):
   p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);p.chmod(0o444);return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
  def meta(name,obj):return file(name,json.dumps(obj,sort_keys=True)+"\n")
  self.file=file;self.meta=meta
  self.children=[file("evidence/"+name,"SYNTHETIC_BYTE_EVIDENCE_"+str(i))for i,(name,_,_)in enumerate(a.ROWS)]
  a.ROWS=[(Path(r["path"]).name,r["bytes"],r["sha256"])for r in self.children]
  self.raw=dict(schema_version=1,session_id=a.SESSION,recovery_type=a.RECOVERY_TYPE,files=[dict(path=n,bytes=size,sha256=sha)for n,size,sha in a.ROWS],records=[dict(keep="ORIGINAL_OTHER_PAYLOAD")],other={"preserve":True})
  a.PARENT=meta("evidence/candidate_recovery_receipt.json",self.raw);self.parent=a.PARENT
  self.lineage=[meta("lineage/"+str(i)+".json",{"SYNTHETIC":i})for i in range(4)]
  self.mapping=dict(schema=a.SCHEMA,status=a.STATUS,parent_manifest=a.PARENT,session_id=a.SESSION,recovery_type=a.RECOVERY_TYPE,entries=[a.expected_entry(i)for i in range(5)],current_recovered_evidence_file_n=5,all_five_current_files_independently_verified=True,all_five_relative_edges_observed=True,original_json_unchanged=True,external_files_read=False,unknown_relative_edges_allowed=False,raw_byte_acceptance=True,new_scientific_inference=False,old_structures_backbones_or_MD_restored=False,current_declared_graph_only=True,accepted_lineage_receipts=self.lineage,producer_executed_source=self.lineage[0],producer_actual_software_gate=self.lineage[1],source_graph_selector=self.lineage[2],prior_accepted_inclusion=self.lineage[3])
  self.receipt=meta("mapping.json",self.mapping)
 def tearDown(self):b.R,a.R,a.PARENT,a.ROWS=self.saved;self.tmp.cleanup()
 def bad(self,mutator):
  obj=copy.deepcopy(self.mapping);mutator(obj)
  with self.assertRaises(ValueError):a.validate_mapping(obj)
 def test_01_exact_all_five_accepts(self):self.assertEqual(len(a.validate_mapping(self.mapping)),5)
 def test_02_parent_fork_rejected(self):self.bad(lambda x:x["parent_manifest"].update(sha256="e"*64))
 def test_03_unknown_schema_rejected(self):self.bad(lambda x:x.update(schema="UNSCOPED"))
 def test_04_incomplete_children_rejected(self):self.bad(lambda x:x["entries"].pop())
 def test_05_duplicate_fields_rejected(self):self.bad(lambda x:x["entries"].__setitem__(1,copy.deepcopy(x["entries"][0])))
 def test_06_wrong_field_rejected(self):self.bad(lambda x:x["entries"][0].update(source_field=["outputs","0"]))
 def test_07_wrong_child_bytes_rejected(self):self.bad(lambda x:x["entries"][0].update(expected_bytes=1))
 def test_08_wrong_canonical_path_rejected(self):self.bad(lambda x:x["entries"][0]["canonical_receipt"].update(path="/tmp/same-name"))
 def test_09_external_permission_rejected(self):self.bad(lambda x:x.update(external_files_read=True))
 def test_10_new_inference_permission_rejected(self):self.bad(lambda x:x.update(new_scientific_inference=True))
 def test_11_missing_structure_recovery_rejected(self):self.bad(lambda x:x.update(old_structures_backbones_or_MD_restored=True))
 def test_12_all_five_actual_bytes_verified(self):self.assertTrue(a.verify_content(self.mapping,lambda r:b.verify_bytes(r,True))["all_five_actual_bytes_verified"])
 def test_13_missing_child_rejected(self):
  Path(self.children[0]["path"]).unlink()
  with self.assertRaises(ValueError):a.verify_content(self.mapping,lambda r:b.verify_bytes(r,True))
 def test_14_child_byte_drift_rejected(self):
  p=Path(self.children[0]["path"]);p.chmod(0o644);p.write_text("drift");p.chmod(0o444)
  with self.assertRaises(ValueError):a.verify_content(self.mapping,lambda r:b.verify_bytes(r,True))
 def test_15_child_writable_rejected(self):
  Path(self.children[0]["path"]).chmod(0o644)
  with self.assertRaises(ValueError):a.verify_content(self.mapping,lambda r:b.verify_bytes(r,True))
 def test_16_parent_payload_kept_and_raw_unchanged(self):
  before=Path(self.parent["path"]).read_bytes();view,contexts=a.exact_manifest_view(self.parent,self.raw,self.mapping)
  self.assertEqual(view["records"],self.raw["records"]);self.assertEqual(view["other"],self.raw["other"]);self.assertEqual(Path(self.parent["path"]).read_bytes(),before);self.assertEqual(len(contexts),5)
 def test_17_only_five_path_fields_change(self):
  view,_=a.exact_manifest_view(self.parent,self.raw,self.mapping)
  for i,r in enumerate(self.children):self.assertEqual(view["files"][i],r)
  altered=copy.deepcopy(view)
  for i,row in enumerate(self.raw["files"]):altered["files"][i]=row
  self.assertEqual(altered,self.raw)
 def test_18_parent_marker_drift_rejected(self):
  raw=copy.deepcopy(self.raw);raw["recovery_type"]="NEW_STRUCTURES"
  with self.assertRaises(ValueError):a.exact_manifest_view(self.parent,raw,self.mapping)
 def test_19_normalise_exact_before_dedup(self):
  for i in range(5):
   result,proof=a.normalise_edge(self.raw["files"][i],self.parent,["files",str(i)],self.mapping);self.assertEqual(result,self.children[i]);self.assertNotIn("original_receipt",proof);self.assertEqual(proof["original_relative_path"],a.ROWS[i][0])
 def test_20_wrong_context_cannot_same_hash_rescue(self):
  for parent,trail in ((dict(self.parent,path=str(self.root/"other.json")),["files","0"]),(self.parent,["files","01"]),(self.parent,["other","0"])):
   with self.subTest(trail=trail),self.assertRaises(ValueError):a.normalise_edge(self.raw["files"][0],parent,trail,self.mapping)
 def restore(self):
  root=self.root/"restore";root.mkdir();index=[]
  for i,r in enumerate([self.receipt,self.parent,*self.children,*self.lineage]):
   target=root/str(i);shutil.copyfile(r["path"],target);target.chmod(0o444);index.append(dict(logical=r,restored_relative=str(i)))
  return root,index
 def test_21_restored_only_exact_five_no_live_fallback(self):
  root,index=self.restore()
  with patch.object(b,"cpu_guard",return_value={"SYNTHETIC_CPU_ONLY":True}):_,proof=a.verify_restored_mapping(self.receipt,root,index)
  self.assertTrue(proof["no_live_root_fallback"]);self.assertEqual(len(proof["contexts"]),5)
 def test_22_restored_missing_child_blocks_even_live_present(self):
  root,index=self.restore();index=[r for r in index if r["logical"]!=self.children[0]]
  with patch.object(b,"cpu_guard",return_value={}),self.assertRaises(ValueError):a.verify_restored_mapping(self.receipt,root,index)
 def test_23_restored_map_parent_and_child_writable_rejected(self):
  for logical in (self.receipt,self.parent,self.children[0]):
   root=self.root/("restore_"+Path(logical["path"]).name);root.mkdir();index=[]
   for i,r in enumerate([self.receipt,self.parent,*self.children,*self.lineage]):
    target=root/str(i);shutil.copyfile(r["path"],target);target.chmod(0o644 if r==logical else 0o444);index.append(dict(logical=r,restored_relative=str(i)))
   with self.subTest(logical=logical["path"]),patch.object(b,"cpu_guard",return_value={}),self.assertRaises(ValueError):a.verify_restored_mapping(self.receipt,root,index)
 def test_24_restored_child_drift_and_symlink_rejected(self):
  for mode in ("drift","symlink"):
   root=self.root/("badrestore_"+mode);root.mkdir();index=[]
   for i,r in enumerate([self.receipt,self.parent,*self.children,*self.lineage]):
    target=root/str(i);shutil.copyfile(r["path"],target);target.chmod(0o444);index.append(dict(logical=r,restored_relative=str(i)))
   target=root/"2";target.chmod(0o644);target.unlink()
   if mode=="symlink":target.symlink_to(self.children[0]["path"])
   else:target.write_text("drift");target.chmod(0o444)
   with self.subTest(mode=mode),patch.object(b,"cpu_guard",return_value={}),self.assertRaises(ValueError):a.verify_restored_mapping(self.receipt,root,index)
 def test_25_saved_recovered_proof_missing_restored_index_blocks_live_rescue(self):
  proof=self.meta("savedproof.json",dict(mapping_receipt=self.receipt,parent_manifest=self.parent,all_five_actual_bytes_verified=True,original_json_unchanged=True));accepted=dict(current_recovered_verification=proof,current_recovered_relative_receipt_context_mapping=self.receipt);root,index=self.restore()
  self.assertTrue(Path(proof["path"]).exists())
  _,lookup=b.restored_index(index,root)
  with self.assertRaises(ValueError):a.verify_saved_verification(accepted,lambda r:b.restored_bytes(r,root,lookup))
 def test_26_saved_recovered_proof_identity_or_boolean_fork_rejected(self):
  accepted=dict(current_recovered_relative_receipt_context_mapping=self.receipt)
  for key,value in (("mapping_receipt",self.parent),("parent_manifest",self.receipt),("all_five_actual_bytes_verified",False),("original_json_unchanged",False)):
   data=dict(mapping_receipt=self.receipt,parent_manifest=self.parent,all_five_actual_bytes_verified=True,original_json_unchanged=True);data[key]=value;accepted["current_recovered_verification"]=self.meta("fork_"+key+".json",data)
   with self.subTest(key=key),self.assertRaises(ValueError):a.verify_saved_verification(accepted,lambda r:b.verify_bytes(r,True))
if __name__=="__main__":unittest.main()

