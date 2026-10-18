"""PureCPU synthetic tar namespace boundaries; none are scientific archive acceptance."""
import copy,hashlib,importlib.util,io,json,tarfile,tempfile,unittest
from pathlib import Path
from unittest import mock
import exact_relative_bbf_context as b
class ArchiveMemberContracts(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=b.R/"steps/24_benchmark_delivery/tmp",prefix="archive_namespace_fixture_");self.d=Path(self.tmp.name)
  spec=importlib.util.spec_from_file_location("synthetic_archive_context_"+self.d.name,Path(__file__).parent/"archive_member_context.py");self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
  self.specs=[];self.rows=[];self.payloads=[]
  for n in range(2):
   payloads=[("historical/"+str(n)+"/raw.txt",b"full synthetic raw byte evidence\n"),("historical/"+str(n)+"/manifest.json",b'{"path":"/MISSING_EXTERNAL_ANNOTATION_ONLY","bytes":1,"sha256":"'+b"0"*64+b'"}')]
   tar=self.d/("archive"+str(n)+".tar.gz");self.write_tar(tar,payloads)
   rows=[dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())for name,data in payloads]
   ar=self.rec(tar);obj=dict(archive=ar["path"],archive_bytes=ar["bytes"],archive_sha256=ar["sha256"],member_count=len(rows),members=rows,other_payload={"unchanged":True})
   parent=self.file("parent"+str(n)+".json",json.dumps(obj).encode());self.specs.append(dict(parent_manifest=parent,archive_receipt=ar,member_count=len(rows)));self.rows.append(rows);self.payloads.append(payloads)
  self.m.ARCHIVES=self.specs
  lineage=[self.file("lineage"+str(i)+".json",b"{}")for i in range(4)]
  pr=dict(schema=self.m.PROOF_SCHEMA,status=self.m.PROOF_STATUS,historical_archive_context_parent_n=len(self.specs),archive_member_n=self.m.total(),all_regular_members_exactly_verified=True,original_index_JSON_bytes_unchanged=True,archive_extracted=False,archived_JSON_payload_parsed=False,current_file_restored=False,current_execution_authorized=False,new_scientific_inference=False,archives=[dict(**s,regular_members=[{k:v for k,v in self.m.entry(s,i,r).items()if k!="source_parent"}for i,r in enumerate(rows)],directory_n=0,archive_bytes_verified_before_and_after=True,extracted=False,archived_JSON_payload_parsed=False)for s,rows in zip(self.specs,self.rows)])
  proof=self.file("producer_proof.json",json.dumps(pr).encode())
  self.mapping=dict(schema=self.m.SCHEMA,status=self.m.STATUS,current_declared_graph_only=True,historical_archive_context_parent_n=len(self.specs),archive_member_n=self.m.total(),all588_declared_member_edges_observed=True,all588_member_bytes_independently_verified_in_archives=True,original_index_JSON_bytes_unchanged=True,archive_extracted=False,archived_JSON_payload_parsed=False,current_file_restored=False,current_execution_authorized=False,new_scientific_inference=False,unknown_relative_edges_allowed=False,external_files_read=False,archive_member_verification=proof,archives=[dict(**s,entries=[self.m.entry(s,i,r)for i,r in enumerate(rows)])for s,rows in zip(self.specs,self.rows)],accepted_lineage_receipts=lineage,producer_executed_source=lineage[0],producer_actual_software_gate=lineage[1],source_graph_selector=lineage[2],prior_accepted_inclusion=lineage[3])
  self.mr=self.file("map.json",json.dumps(self.mapping).encode())
 def tearDown(self):self.tmp.cleanup()
 def rec(self,p):
  data=Path(p).read_bytes();return dict(path=str(p),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 def file(self,name,data):
  p=self.d/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);p.chmod(0o444);return self.rec(p)
 def write_tar(self,path,payloads,kind=None):
  path=Path(path)
  if path.exists():path.chmod(0o644)
  with tarfile.open(path,"w:gz")as f:
   for i,(name,data)in enumerate(payloads):
    info=tarfile.TarInfo(name);info.size=len(data)
    if kind and i==0:
     info.type=kind;info.linkname="historical/link_target";info.size=0;f.addfile(info)
    else:f.addfile(info,io.BytesIO(data))
  path.chmod(0o444)
 def exact(self,r):return b.verify_bytes(r,True)
 def obj(self,index=0):return json.loads(self.exact(self.specs[index]["parent_manifest"]).read_text())
 def mapping_copy(self):return copy.deepcopy(self.mapping)
 def restored(self,omit=None,writable=None):
  root=self.d/"restore";root.mkdir();index=[];receipts=[self.mr,self.mapping["archive_member_verification"],*self.mapping["accepted_lineage_receipts"],*[r for s in self.specs for r in (s["parent_manifest"],s["archive_receipt"])]]
  for i,r in enumerate(receipts):
   if r==omit:continue
   p=root/str(i);p.write_bytes(self.exact(r).read_bytes());p.chmod(0o644 if r==writable else 0o444);index.append(dict(logical=r,restored_relative=str(i)))
  return root,index,receipts
 def test_01_valid_map_complete_two_namespaces(self):self.assertEqual(len(self.m.validate_mapping(self.mapping)),2)
 def test_02_view_changes_only_members_and_preserves_raw_parent(self):
  obj=self.obj();before=self.exact(self.specs[0]["parent_manifest"]).read_bytes();view,contexts=self.m.exact_manifest_view(self.specs[0]["parent_manifest"],obj,self.mapping)
  self.assertEqual(view["other_payload"],obj["other_payload"]);self.assertEqual(view["archive"],obj["archive"]);self.assertEqual(len(contexts),2)
  self.assertNotIn("path",view["members"][0]);self.assertEqual(before,self.exact(self.specs[0]["parent_manifest"]).read_bytes())
 def test_03_normalise_returns_null_current_file(self):
  r,c=self.m.normalise_edge(self.rows[0][0],self.specs[0]["parent_manifest"],["members","0"],self.mapping);self.assertIsNone(r);self.assertFalse(c["current_file_restored"]);self.assertNotIn("original_receipt",c)
 def test_04_foreign_parent_before_dedup(self):
  with self.assertRaises(ValueError):self.m.normalise_edge(self.rows[0][0],self.specs[1]["parent_manifest"],["members","0"],self.mapping)
 def test_05_unknown_field_before_dedup(self):
  for trail in (["other","0"],["members","00"],["members","2"],["members",0]):
   with self.subTest(trail=trail),self.assertRaises(ValueError):self.m.normalise_edge(self.rows[0][0],self.specs[0]["parent_manifest"],trail,self.mapping)
 def test_06_changed_original_member_before_dedup(self):
  for k,v in (("path","historical/different.txt"),("bytes",9),("sha256","0"*64)):
   with self.subTest(key=k),self.assertRaises(ValueError):self.m.normalise_edge({**self.rows[0][0],k:v},self.specs[0]["parent_manifest"],["members","0"],self.mapping)
 def test_07_unknown_mapping_parent(self):
  m=self.mapping_copy();m["archives"][0]["parent_manifest"]["sha256"]="0"*64
  with self.assertRaises(ValueError):self.m.validate_mapping(m)
 def test_08_forked_archive_receipt(self):
  m=self.mapping_copy();m["archives"][0]["archive_receipt"]["sha256"]="0"*64
  with self.assertRaises(ValueError):self.m.validate_mapping(m)
 def test_09_missing_mapping_member(self):
  m=self.mapping_copy();m["archives"][0]["entries"].pop()
  with self.assertRaises(ValueError):self.m.validate_mapping(m)
 def test_10_duplicate_mapping_field(self):
  m=self.mapping_copy();m["archives"][0]["entries"][1]=copy.deepcopy(m["archives"][0]["entries"][0])
  with self.assertRaises(ValueError):self.m.validate_mapping(m)
 def test_11_duplicate_original_member_name(self):
  obj=self.obj();obj["members"][1]=copy.deepcopy(obj["members"][0])
  with self.assertRaises(ValueError):self.m.parent_rows(self.specs[0]["parent_manifest"],obj)
 def test_12_unsafe_names_and_source_extensions(self):
  for name in ("/absolute.txt","../escape.txt","a/../b.txt","a//b.txt","./relative.txt","a\\b.txt","a.py","a.sh","a.sbatch","a\x00b"):
   with self.subTest(name=name),self.assertRaises(ValueError):self.m.safe_member_name(name)
 def test_13_actual_full_tar_member_bytes_pass_without_payload_recursion(self):
  proof=self.m.verify_tar(self.exact(self.specs[0]["archive_receipt"]),self.specs[0],self.rows[0]);self.assertTrue(proof["all_member_bytes_verified"]);self.assertFalse(proof["member_JSON_payload_parsed"])
  tar=self.d/"valid_directories.tar.gz"
  with tarfile.open(tar,"w:gz")as f:
   for name in ("historical/","historical/0/"):
    info=tarfile.TarInfo(name);info.type=tarfile.DIRTYPE;f.addfile(info)
   for name,data in self.payloads[0]:
    info=tarfile.TarInfo(name);info.size=len(data);f.addfile(info,io.BytesIO(data))
  tar.chmod(0o444);self.assertEqual(self.m.verify_tar(tar,self.specs[0],self.rows[0])["directory_n"],2)
 def test_14_missing_actual_tar_member(self):
  tar=self.d/"missing.tar.gz";self.write_tar(tar,self.payloads[0][:1])
  with self.assertRaises(ValueError):self.m.verify_tar(tar,self.specs[0],self.rows[0])
 def test_15_extra_actual_tar_member(self):
  tar=self.d/"extra.tar.gz";self.write_tar(tar,self.payloads[0]+[("extra.txt",b"extra")])
  with self.assertRaises(ValueError):self.m.verify_tar(tar,self.specs[0],self.rows[0])
 def test_16_duplicate_actual_tar_member(self):
  tar=self.d/"duplicate.tar.gz";self.write_tar(tar,self.payloads[0]+self.payloads[0][:1])
  with self.assertRaises(ValueError):self.m.verify_tar(tar,self.specs[0],self.rows[0])
 def test_17_symlink_tar_member(self):
  tar=self.d/"symlink.tar.gz";self.write_tar(tar,self.payloads[0],tarfile.SYMTYPE)
  with self.assertRaises(ValueError):self.m.verify_tar(tar,self.specs[0],self.rows[0])
 def test_18_hardlink_tar_member(self):
  tar=self.d/"hardlink.tar.gz";self.write_tar(tar,self.payloads[0],tarfile.LNKTYPE)
  with self.assertRaises(ValueError):self.m.verify_tar(tar,self.specs[0],self.rows[0])
 def test_19_directory_tar_member(self):
  tar=self.d/"directory.tar.gz";self.write_tar(tar,self.payloads[0],tarfile.DIRTYPE)
  with self.assertRaises(ValueError):self.m.verify_tar(tar,self.specs[0],self.rows[0])
 def test_20_changed_actual_member_byte_size_or_SHA(self):
  for data in (b"changed size",b"x"*len(self.payloads[0][0][1])):
   with self.subTest(data=data):
    tar=self.d/"changed.tar.gz";self.write_tar(tar,[(self.payloads[0][0][0],data),self.payloads[0][1]])
    with self.assertRaises(ValueError):self.m.verify_tar(tar,self.specs[0],self.rows[0])
 def test_21_actual_live_full_content_independent(self):
  p=self.m.verify_content(self.mapping,self.exact);self.assertEqual(p["member_n"],4);self.assertTrue(p["no_extraction"]);self.assertFalse(p["new_scientific_inference"])
 def test_22_missing_producer_byte_proof(self):
  Path(self.mapping["archive_member_verification"]["path"]).unlink()
  with self.assertRaises(ValueError):self.m.verify_content(self.mapping,self.exact)
 def test_23_wrong_producer_proof_status_or_table(self):
  original=json.loads(self.exact(self.mapping["archive_member_verification"]).read_text())
  for key,val in (("status","PENDING"),("archive_member_n",3),("all_regular_members_exactly_verified",False),("archive_extracted",True),("archives",[])):
   m=self.mapping_copy();m["archive_member_verification"]=self.file("bad_producer_"+key+".json",json.dumps({**original,key:val}).encode())
   with self.subTest(key=key),self.assertRaises(ValueError):self.m.verify_content(m,self.exact)
  fork=copy.deepcopy(original);fork["archives"][0]["regular_members"][0]["expected_sha256"]="0"*64;m=self.mapping_copy();m["archive_member_verification"]=self.file("bad_producer_table.json",json.dumps(fork).encode())
  with self.assertRaises(ValueError):self.m.verify_content(m,self.exact)
 def test_24_member_canonical_current_permission_fork(self):
  for key,val in (("canonical_receipt",self.specs[0]["archive_receipt"]),("current_execution_allowed",True),("current_file_restored",True),("raw_member_bytes_verified_in_archive",False)):
   m=self.mapping_copy();m["archives"][0]["entries"][0][key]=val
   with self.subTest(key=key),self.assertRaises(ValueError):self.m.validate_mapping(m)
 def test_25_readonly_current_parent_and_tar_required(self):
  for r in (self.specs[0]["parent_manifest"],self.specs[0]["archive_receipt"]):
   p=Path(r["path"]);p.chmod(0o644)
   try:
    with self.assertRaises(ValueError):self.m.verify_content(self.mapping,self.exact)
   finally:p.chmod(0o444)
 def test_26_all_tar_and_parent_archived_restore_only(self):
  root,index,receipts=self.restored()
  for r in receipts:Path(r["path"]).unlink()
  with mock.patch.object(b,"cpu_guard",return_value=dict(job_id="SYNTHETIC")):_,proof=self.m.verify_restored_mapping(self.mr,root,index)
  self.assertTrue(proof["no_live_root_fallback"]);self.assertEqual(proof["member_n"],4);self.assertTrue(all(Path(p).is_relative_to(root)for p in proof["read_paths"]))
 def test_27_missing_restored_tar_cannot_live_fallback(self):
  r=self.specs[0]["archive_receipt"];root,index,_=self.restored(omit=r);self.assertTrue(Path(r["path"]).is_file())
  with mock.patch.object(b,"cpu_guard",return_value={}),self.assertRaises(ValueError):self.m.verify_restored_mapping(self.mr,root,index)
 def test_28_missing_restored_parent_or_producer_proof(self):
  for r in (self.specs[0]["parent_manifest"],self.mapping["archive_member_verification"]):
   root=self.d/"restore"
   if root.exists():__import__("shutil").rmtree(root)
   root,index,_=self.restored(omit=r)
   with self.subTest(r=r),mock.patch.object(b,"cpu_guard",return_value={}),self.assertRaises(ValueError):self.m.verify_restored_mapping(self.mr,root,index)
 def test_29_writable_restored_authority_or_tar(self):
  for r in (self.mr,self.specs[0]["parent_manifest"],self.specs[0]["archive_receipt"],self.mapping["archive_member_verification"]):
   root=self.d/"restore"
   if root.exists():__import__("shutil").rmtree(root)
   root,index,_=self.restored(writable=r)
   with self.subTest(r=r),mock.patch.object(b,"cpu_guard",return_value={}),self.assertRaises(ValueError):self.m.verify_restored_mapping(self.mr,root,index)
 def test_30_restored_symlink_escape(self):
  root,index,_=self.restored();p=root/index[-1]["restored_relative"];p.unlink();p.symlink_to(self.specs[-1]["archive_receipt"]["path"])
  with mock.patch.object(b,"cpu_guard",return_value={}),self.assertRaises(ValueError):self.m.verify_restored_mapping(self.mr,root,index)
 def test_31_missing_saved_independent_proof(self):
  accepted=dict(archive_member_receipt_context_mapping=self.mr,archive_member_verification=self.file("saved.json",b"{}"));Path(accepted["archive_member_verification"]["path"]).unlink()
  with self.assertRaises(ValueError):self.m.verify_saved_verification(accepted,self.exact)
 def test_32_forked_saved_independent_proof_and_legitimate_terminal(self):
  p=self.m.verify_content(self.mapping,self.exact);p["mapping_receipt"]=self.mr;r=self.file("saved_good.json",json.dumps(p).encode());accepted=dict(archive_member_receipt_context_mapping=self.mr,archive_member_verification=r);self.m.verify_saved_verification(accepted,self.exact)
  for k,v in (("mapping_receipt",self.specs[0]["archive_receipt"]),("member_n",3),("all_member_bytes_verified",False),("no_extraction",False),("parent_manifests",[]),("schema","WRONG_SCHEMA"),("archives",[]),("contexts",[]),("current_files_restored",True),("member_JSON_payload_parsed",True)):
   bad=self.file("saved_bad_"+k+".json",json.dumps({**p,k:v}).encode());accepted["archive_member_verification"]=bad
   with self.subTest(k=k),self.assertRaises(ValueError):self.m.verify_saved_verification(accepted,self.exact)
  for kind in ("missing_member","member_actual_SHA","member_current_role","duplicate_member","unsafe_directory","missing_scalar_context"):
   bad=copy.deepcopy(p)
   if kind=="missing_member":bad["archives"][0]["members"].pop()
   elif kind=="member_actual_SHA":bad["archives"][0]["members"][0]["actual_sha256"]="0"*64
   elif kind=="member_current_role":bad["archives"][0]["members"][0]["current_file_restored"]=True
   elif kind=="duplicate_member":bad["archives"][0]["members"][1]=copy.deepcopy(bad["archives"][0]["members"][0])
   elif kind=="unsafe_directory":bad["archives"][0]["directory_names"]=["../escape"];bad["archives"][0]["directory_n"]=1
   else:bad["contexts"].pop()
   accepted["archive_member_verification"]=self.file("saved_content_fork_"+kind+".json",json.dumps(bad).encode())
   with self.subTest(kind=kind),self.assertRaises(ValueError):self.m.verify_saved_verification(accepted,self.exact)
