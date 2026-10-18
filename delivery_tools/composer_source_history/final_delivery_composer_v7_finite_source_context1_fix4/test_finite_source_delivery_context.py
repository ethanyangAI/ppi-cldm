"""Synthetic finite Source semantics only; no production Source acceptance.

Four exact historical diagnostic own documents are supplied by the owned CPU
bootstrap as DATA_FIXTURE_BYTES. No embedded receipt target is read.
"""
import copy,contextlib,hashlib,json,os,stat,tempfile,types,unittest
from pathlib import Path
from unittest import mock
import final_delivery_composer as m
import finite_source_delivery_context as f
DATA_FIXTURE_BYTES={}
ALLOC=dict(job_id="999999",allocated_CPUs=1,allocated_gpus=0,SYNTHETIC_SOFTWARE_ONLY=True)

def record(path,raw=b"synthetic"):
 return dict(path=str(path),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def md(receipt,directory=False,mode=0o444):
 return dict(path=receipt["path"],bytes=4096 if directory else receipt["bytes"],inode=91,
  mtime_ns=1000000000,ctime_ns=1000000000,mode=(stat.S_IFDIR|0o555)if directory else(stat.S_IFREG|mode),
  dev=7,nlink=2 if directory else 1,uid=1,gid=1)
def no_original_io():
 stack=contextlib.ExitStack()
 for name in("open","read_bytes","read_text","stat","lstat","resolve"):
  stack.enter_context(mock.patch.object(Path,name,side_effect=AssertionError("Original filesystem forbidden in pure semantic replay")))
 for name in("stat","lstat","readlink"):
  stack.enter_context(mock.patch.object(os,name,side_effect=AssertionError("Original native IO forbidden in pure semantic replay")))
 return stack
def semantics():
 p=m.D/f.SEMANTICS_NAME;r=m.rec(p)
 return f._load_semantics_bytes(p.read_bytes(),r)
def histories(g):
 return [(family,prefix,doc,proof)for family,prefix,doc,proof in f._history_definitions(g)]

def closed_binding():
 root=f.R/"steps/24_benchmark_delivery/tmp"/"FINITE_SYNTHETIC_BINDING"
 return dict(schema=f.SCHEMA,root_owned=True,
  producer={name:record(root/(name+".json"))for name in f.PRODUCER_KEYS},
  semantics_source=dict(path=str(root/f.SEMANTICS_NAME),bytes=f.SEMANTICS_FP[0],sha256=f.SEMANTICS_FP[1]),
  stage_acceptance=record(root/"stage.json"),late_source_publication=record(root/"late.json"),
  transport_aliases=[],additional_control_receipts=[],source_routes=[],operational_source_provenance=record(f.R/"steps/24_benchmark_delivery/submissions"/(f.OPERATIONAL_ROOT_PREFIX+ALLOC["job_id"])/"operational_source_provenance.json"))


def history_fixture(g,family,prefix,modules=("default_workflow_integration",),five=False):
 out=f.R/"steps/24_benchmark_delivery/tmp"/"FINITE_SYNTHETIC_INDEX_ONLY"
 code=prefix
 leaf=dict(getattr(g,code+"_LEAF"));base=dict(getattr(g,code+"_BASE"))
 role=getattr(g,code+"_ROLE");stem={"inventory13299":"inventory_history","archive13298":"archive_parent_history",
  "relative13295":"relative_diagnostic_history","parent13290":"parent_diagnostic_history"}[family]
 number=family[-5:]
 copy_r=dict(leaf,path=str(out/("opaque_"+stem+"_bytes")/(leaf["sha256"]+"_"+number+"_diagnostic.OPAQUE.txt")))
 pointer=record(out/(stem+"_opaque_aliases.json"),b"synthetic-index")
 contexts=g._fixed_history_contexts(family)
 observations=[]
 basis={"inventory13299":"EXACT_READONLY13299_DIAGNOSTIC_HISTORY_DATA_BYTECOPY",
 "archive13298":"EXACT_READONLY13298_DIAGNOSTIC_ARCHIVE_PARENT_HISTORY_DATA_BYTECOPY",
 "relative13295":"EXACT_READONLY13295_RELATIVE_DIAGNOSTIC_HISTORY_DATA_BYTECOPY",
 "parent13290":"EXACT_READONLY13290_PARENT_DIAGNOSTIC_HISTORY_DATA_BYTECOPY"}[family]
 for module in modules:
  for context in contexts if five else contexts[:1]:
   observations.append(dict(ordinal=len(observations),receipt=leaf,parent_manifest=context["parent_manifest"],
    field=context["field"],module=module,physical=copy_r,resolution_basis=basis,role=role))
 authorities=[base]+[dict(x["receipt"])for x in g._FIXED_HISTORY_MAPPING_PARENTS]
 native=[md(r)for r in authorities]
 saved=dict(schema=getattr(g,code+"_PROOF_SCHEMA"),status=getattr(g,code+"_PROOF_STATUS"),
  parent_manifest=base,original_diagnostic_data=leaf,source_field=list(getattr(g,code+"_FIELD")),role=role,
  allowed_modules=list(getattr(g,code+"_MODULES")),
  module_policy=dict(default_workflow_integration="FINITE_FIVE_ROWS_ACTUAL_RUNTIME_PARENT_FIELD_AUTHENTICATION_REQUIRED",
   final_delivery_tools="PROSPECTIVE_SAME_FIVE_ROWS_NOT_REQUIRED"),
  preserved_opaque_data=copy_r,exact_alias_index=pointer,allocation=ALLOC,
  parent_metadata_before=md(base),parent_metadata_after=md(base),original_metadata_before=md(leaf),
  original_metadata_after=md(leaf),preserved_metadata=md(copy_r),copy_directory_metadata=md(dict(path=str(Path(copy_r["path"]).parent)),True),
  observations=observations,authorized_observation_n=len(observations),
  actual_default_observation_n=sum(x["module"]=="default_workflow_integration"for x in observations),
  actual_finaltools_observation_n=sum(x["module"]=="final_delivery_tools"for x in observations),
  independent_BaseA_history_fields_retained=True,original_bytes_and_metadata_unchanged=True,
  original_permission_unchanged=True,preserved_copy_readonly_fsynced_and_byte_identical=True,
  source_or_configuration_promotion=False,archive_or_scientific_acceptance=False,
  original_JSON_or_parent_rewritten=False,generic_reader_or17_parent_scope_changed=False,
  separate_original_JSON_physical_package_entry_forbidden=True,future_package_index_and_isolated_restore_acceptance=False,
  authority_receipts=authorities,authority_metadata_before=native,authority_metadata_after=copy.deepcopy(native),
  authorized_parent_field_rows=contexts,
  authority_policy="FOUR_FULL_PINNED_AUTHORITIES_FIVE_EXACT_ROWS_NOT_PARENT_FIELD_CARTESIAN_PRODUCT",
  prospective_rows_require_actual_runtime_authentication=True,relative_BBF_mapping_parent_authorized=False,
  generic_parent_or_module_permission_added=False)
 if family in("inventory13299","archive13298"):
  saved.update(embedded_parent_n=2 if family=="inventory13299"else 1,
   embedded_member_counts=[193,395]if family=="inventory13299"else[193],
   embedded_observation_n=588 if family=="inventory13299"else 193,
   embedded_relative_targets_interpreted=False,member_paths_statted_or_opened=False)
 elif family=="relative13295":
  saved.update(embedded_parent_n=1,embedded_record_n=3,embedded_file_n=5,embedded_receipt_occurrence_n=6,
   embedded_unique_relative_path_n=5,embedded_relative_targets_interpreted=False,embedded_targets_statted_or_opened=False)
 else:
  saved.update(embedded_receipt_occurrence_n=5,embedded_unique_fingerprint_n=4,
   ordinary_source_children=g.parent_diagnostic_history_source_children(),
   ordinary_source_children_are_separate_graph_obligations=True,
   documentary_external_or_previous_targets_interpreted=False,documentary_targets_statted_or_opened=False)
 if family!="parent13290":
  saved.update(independent_source_producer=dict(getattr(g,code+"_PRODUCER")),
   independent_software_only_gate=dict(getattr(g,code+"_SOFTWARE")))
 index=dict(schema="exact-resource-aliases.v2",status=getattr(g,code+"_ALIAS_STATUS"),
  aliases=[dict(original=leaf,archived=copy_r,status="READONLY_BYTE_IDENTICAL_ALIAS",role=role)],
  historical_unresolved=[],separate_original_JSON_physical_package_entry_forbidden=True,
  scientific_or_source_or_archive_authorization=False)
 return saved,index

def source2_fixture(g,saved):
 data=[];sources=[];rows=[]
 for observation in saved["observations"]:
  data.append(dict(receipt=dict(g._PARENT_DIAGNOSTIC_HISTORY_LEAF),parent=observation["parent_manifest"]["path"],
   field=observation["field"],module=observation["module"],physical=saved["preserved_opaque_data"],
   resolution_basis=observation["resolution_basis"],role=g._PARENT_DIAGNOSTIC_HISTORY_ROLE,
   raw_bytes_preserved=True,documentary_receipt_children_interpreted=False,ordinary_Source_children_explicitly_enqueued=True,
   source_or_configuration_promotion=False))
  for child in reversed(g.parent_diagnostic_history_source_children()):
   sources.append(dict(receipt=child["receipt"],field=child["field"],module=observation["module"],
    parent=g._PARENT_DIAGNOSTIC_HISTORY_LEAF["path"],physical=dict(child["receipt"],path=str(f.R/"synthetic-copies"/Path(child["receipt"]["path"]).name)),
    role="EXACT_NEW_TEXT_RECEIPT_READBACK",resolution_basis="EXPLICIT_EXACT_BYTE_ALIAS"))
 for child in g.parent_diagnostic_history_source_children():
  rows.append(dict(source=dict(child["receipt"],path=str(f.R/"synthetic-copies"/Path(child["receipt"]["path"]).name)),
   original_source=child["receipt"],kind="IMPLEMENTATION",roles=sorted({x["module"]for x in saved["observations"]}),
   repository_relative="synthetic/"+Path(child["receipt"]["path"]).name))
 return dict(edges=data+sources),dict(files=rows)

class FiniteHistoryIndexContracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.g=semantics()
 def test_01_four_complete_document_inputs_are_DATA_not_Source(self):
  self.assertEqual(len(DATA_FIXTURE_BYTES),4)
  for family,prefix,document,proof in histories(self.g):
   r=getattr(self.g,prefix+"_LEAF");raw=DATA_FIXTURE_BYTES[f.rid(r)]
   self.assertEqual((len(raw),hashlib.sha256(raw).hexdigest()),f.fp(r))
   obj=f.strict_json(raw)
   with no_original_io():self.assertTrue(document(obj))
 def test_02_four_full_saved_proofs_and_aliases_no_original_IO(self):
  for family,prefix,document,proof in histories(self.g):
   saved,index=history_fixture(self.g,family,prefix)
   with no_original_io():self.assertTrue(proof(saved,index,ALLOC))
   if family!="parent13290":
    edge=dict(receipt=saved["original_diagnostic_data"],parent=saved["parent_manifest"]["path"],
     field=saved["source_field"],module="default_workflow_integration",physical=saved["preserved_opaque_data"],
     resolution_basis=saved["observations"][0]["resolution_basis"],role=saved["role"],raw_bytes_preserved=True,
     receipt_children_interpreted=False,source_or_configuration_promotion=False)
    with no_original_io():self.assertTrue(f.history_graph_shape(saved,dict(edges=[edge])))
    edge["field"]=["other"]
    with no_original_io(),self.assertRaisesRegex(ValueError,"Actual ordered history"):f.history_graph_shape(saved,dict(edges=[edge]))
 def test_03_twenty_coupled_rows_dual_modules_are_optional_actual_observations(self):
  for family,prefix,document,proof in histories(self.g):
   saved,index=history_fixture(self.g,family,prefix,("default_workflow_integration","final_delivery_tools"),True)
   self.assertEqual(len(saved["observations"]),10)
   with no_original_io():self.assertTrue(proof(saved,index,ALLOC))
 def test_04_parent_field_cross_product_is_rejected(self):
  for family,prefix,document,proof in histories(self.g):
   saved,index=history_fixture(self.g,family,prefix,five=True)
   saved["observations"][0]["parent_manifest"]=saved["observations"][-1]["parent_manifest"]
   with no_original_io(),self.assertRaises(ValueError):proof(saved,index,ALLOC)
 def test_05_unknown_module_and_noncontiguous_order_fail(self):
  for family,prefix,document,proof in histories(self.g):
   for field,value in(("module","unrelated"),("ordinal",91)):
    saved,index=history_fixture(self.g,family,prefix);saved["observations"][0][field]=value
    with no_original_io(),self.assertRaises(ValueError):proof(saved,index,ALLOC)
 def test_06_full_authority_native_table_swap_fails(self):
  for family,prefix,document,proof in histories(self.g):
   saved,index=history_fixture(self.g,family,prefix)
   saved["authority_metadata_before"][1],saved["authority_metadata_before"][2]=saved["authority_metadata_before"][2],saved["authority_metadata_before"][1]
   with no_original_io(),self.assertRaises(ValueError):proof(saved,index,ALLOC)
 def test_07_index_copy_and_allocation_tamper_fail(self):
  for family,prefix,document,proof in histories(self.g):
   for kind in("copy","allocation","index"):
    saved,index=history_fixture(self.g,family,prefix)
    if kind=="copy":saved["preserved_metadata"]["nlink"]=2
    elif kind=="allocation":saved["allocation"]=dict(ALLOC,allocated_gpus=1)
    else:index["aliases"][0]["role"]="SOURCE"
    with no_original_io(),self.assertRaises(ValueError):proof(saved,index,ALLOC)
 def test_08_original_false_flags_are_not_future_archive_acceptance(self):
  for family,prefix,document,proof in histories(self.g):
   saved,index=history_fixture(self.g,family,prefix);saved["future_package_index_and_isolated_restore_acceptance"]=True
   with no_original_io(),self.assertRaises(ValueError):proof(saved,index,ALLOC)
 def test_09_real_two_ordinary_Source_rows_and_ten_ordered_edges_required(self):
  g=self.g;saved,index=history_fixture(g,"parent13290","_PARENT_DIAGNOSTIC_HISTORY",five=True)
  c,i=source2_fixture(g,saved)
  self.assertEqual(len([x for x in c["edges"]if x.get("parent")==g._PARENT_DIAGNOSTIC_HISTORY_LEAF["path"]]),10)
  with no_original_io():self.assertTrue(g.parent_diagnostic_history_source_coverage(saved,c,i))
 def test_10_Source2_DATA_flags_cannot_replace_actual_implementation_rows(self):
  g=self.g;saved,index=history_fixture(g,"parent13290","_PARENT_DIAGNOSTIC_HISTORY")
  c,i=source2_fixture(g,saved);i["files"][0]["kind"]="DOCUMENT"
  with no_original_io(),self.assertRaises(ValueError):g.parent_diagnostic_history_source_coverage(saved,c,i)
 def test_11_Source2_dual_module_rows_need_both_roles(self):
  g=self.g;saved,index=history_fixture(g,"parent13290","_PARENT_DIAGNOSTIC_HISTORY",("default_workflow_integration","final_delivery_tools"))
  c,i=source2_fixture(g,saved)
  with no_original_io():self.assertTrue(g.parent_diagnostic_history_source_coverage(saved,c,i))
  i["files"][0]["roles"]=["default_workflow_integration"]
  with no_original_io(),self.assertRaises(ValueError):g.parent_diagnostic_history_source_coverage(saved,c,i)
 def test_12_Source2_original_parent_field_and_FP_cannot_be_substituted(self):
  g=self.g;saved,index=history_fixture(g,"parent13290","_PARENT_DIAGNOSTIC_HISTORY")
  for key,value in(("parent","/unknown"),("field",["other"]),("physical",dict(g._PARENT_DIAGNOSTIC_HISTORY_PRODUCER,sha256="0"*64))):
   c,i=source2_fixture(g,saved);c["edges"][-1][key]=value
   with no_original_io(),self.assertRaises(ValueError):g.parent_diagnostic_history_source_coverage(saved,c,i)

class FiniteIdentityContracts(unittest.TestCase):
 def row(self,path="/original.py",dest="history/original.py",raw=b"same"):
  r=record(path,raw);return dict(original_source=r,source=dict(r,path="/readonly-copy.py"),repository_relative=dest,
   kind="IMPLEMENTATION",roles=["final_delivery_tools"],logical_receipts=[])
 def test_13_same_FP_keeps_two_original_identities_and_destinations(self):
  a=self.row();b=self.row("/other.py","history/other.py")
  identities,multimap,dest=f.identity_multimap([a,b]);self.assertEqual((len(identities),len(multimap),len(dest)),(2,1,2))
 def test_14_all_logical_receipts_retain_candidates(self):
  a=self.row();a["logical_receipts"]=[record("/third.py",b"same")]
  self.assertEqual(len(f.identity_multimap([a])[0]),2)
 def test_15_destination_collision_with_different_FP_fails(self):
  with self.assertRaises(ValueError):f.identity_multimap([self.row(),self.row("/other.py",raw=b"different")])
 def test_16_unsafe_relative_public_destination_fails(self):
  for dest in("../escape",".git/config","/absolute"):
   with self.subTest(dest=dest),self.assertRaises(ValueError):f.identity_multimap([self.row(dest=dest)])
 def test_17_strict_JSON_rejects_duplicates_nonfinite_and_overflow(self):
  for raw in(b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":1e999}',b'{"x":"\xff"}'):
   with self.subTest(raw=repr(raw)),self.assertRaises((ValueError,UnicodeDecodeError)):f.strict_json(raw)
 def test_18_receipt_bool_and_opaque_wrong_extension_are_rejected(self):
  r=record("/x");r["bytes"]=True
  with self.assertRaises(ValueError):f.rid(r)
  binding=closed_binding();original=record(f.R/"original.json")
  binding["transport_aliases"]=[dict(original=original,archived=dict(original,path=str(f.R/"wrong.OPAQUE.json")),
   status="READONLY_BYTE_IDENTICAL_ALIAS",role="FINITE_SOURCE_CONTROL_BYTES")]
  with self.assertRaisesRegex(ValueError,"physical TXT"):f._binding_shape(binding)
 def test_19_semantics_loader_rejects_nonowned_name_and_wrong_wholebytes(self):
  raw=(m.D/f.SEMANTICS_NAME).read_bytes();r=record(m.D/f.SEMANTICS_NAME,raw)
  with self.assertRaises(ValueError):f._load_semantics_bytes(raw,dict(r,path="/arbitrary_module.py"))
  with self.assertRaises(ValueError):f._load_semantics_bytes(raw+b"\n",r)
 def test_20_exact_semantics_nonmain_load_has_no_FS_or_project_import(self):
  raw=(m.D/f.SEMANTICS_NAME).read_bytes();r=record(m.D/f.SEMANTICS_NAME,raw)
  with no_original_io():g=f._load_semantics_bytes(raw,r)
  self.assertEqual(tuple(n for n in f.PURE_NAMES if callable(getattr(g,n,None))),f.PURE_NAMES)

class FiniteCurrentLifecycleContracts(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(dir=m.R/"steps/24_benchmark_delivery/tmp",prefix="finite_source_context_")
  self.root=Path(self.temp.name)
 def tearDown(self):self.temp.cleanup()
 def file(self,name="control.json",raw=b'{"synthetic":true}'):
  p=self.root/name;p.write_bytes(raw);p.chmod(0o444);return record(p,raw)
 def test_21_full_current_native_baseline_before_first_read(self):
  r=self.file();io=f.CurrentInputs();self.assertEqual(io.json(r),{"synthetic":True});io.end()
 def test_22_native_only_real_late_utime_is_rejected(self):
  r=self.file();io=f.CurrentInputs();io.read(r);p=Path(r["path"]);old=os.lstat(p);os.utime(p,ns=(old.st_atime_ns,old.st_mtime_ns+2000000000))
  with self.assertRaisesRegex(ValueError,"native drift"):io.end()
 def test_23_same_length_bytes_tamper_is_rejected(self):
  r=self.file();io=f.CurrentInputs();io.read(r);p=Path(r["path"]);p.chmod(0o644);p.write_bytes(b'{"synthetic":null}');p.chmod(0o444)
  with self.assertRaises(ValueError):io.end()
 def test_24_hardlink_and_symlink_inputs_are_rejected(self):
  r=self.file();p=Path(r["path"]);os.link(p,self.root/"hard")
  with self.assertRaises(ValueError):f.CurrentInputs().read(r)
  (self.root/"hard").unlink();(self.root/"link").symlink_to(p)
  with self.assertRaises(ValueError):f.CurrentInputs().read(dict(r,path=str(self.root/"link")))
 def test_25_writable_control_is_not_metadata_control_exception(self):
  r=self.file();Path(r["path"]).chmod(0o664)
  with self.assertRaises(ValueError):f.CurrentInputs().read(r)
 def test_26_last_file_read_mutates_earlier_native_union(self):
  a=self.file("a.json");b=self.file("b.json");io=f.CurrentInputs();io.read(a);io.read(b);original=Path.read_bytes
  def read(path):
   raw=original(path)
   if str(path)==b["path"]:
    p=Path(a["path"]);old=os.lstat(p);os.utime(p,ns=(old.st_atime_ns,old.st_mtime_ns+2000000000))
   return raw
  with mock.patch.object(Path,"read_bytes",read),self.assertRaisesRegex(ValueError,"native union"):io.end()
 def test_27_fake_INDEX_object_cannot_supply_live_callback(self):
  with self.assertRaisesRegex(ValueError,"Actual package-owned StrictIndex"):f.indexed_payloads(closed_binding(), {}, types.SimpleNamespace())

def worker_fixture():
 out=f.R/"steps/24_benchmark_delivery/tmp"/"FINITE_SYNTHETIC_WORKER"
 parents=[record(out/("raw_parent%d.json"%i),b"ordinary-parent")for i in range(2)]
 table=[];payloads={};targets=[];canonical=[]
 for i in range(22):
  raw=json.dumps(dict(SYNTHETIC_SOFTWARE_ONLY=True,child=record(out/("child%d.txt"%i),b"unused-child"))).encode()
  canonical.append(record(out/("canonical%d.json"%i),raw))
  cp=dict(canonical[-1],path=str(out/"finite_worker_control_bytes"/("%03d_%s_worker.json"%(i,canonical[-1]["sha256"]))))
  targets.append(dict(canonical_path_as_scalar=canonical[-1]["path"],bytes_as_scalar=canonical[-1]["bytes"],
   sha256_as_scalar=canonical[-1]["sha256"],preserved=cp,preserved_metadata=md(cp),
   child_receipts=[dict(receipt=x,field=list(field))for x,field in f.receipt_nodes(f.strict_json(raw))]))
  payloads[f.rid(cp)]=raw
 # Production target order is canonical full-key lexical order, not fixture creation order.
 targets.sort(key=lambda x:(x["canonical_path_as_scalar"],x["sha256_as_scalar"],x["bytes_as_scalar"]))
 for i,target in enumerate(targets):
  old=target["preserved"];raw=payloads.pop(f.rid(old));new=dict(old,path=str(out/"finite_worker_control_bytes"/("%03d_%s_worker.json"%(i,old["sha256"]))))
  target["preserved"]=new;target["preserved_metadata"]=md(new);payloads[f.rid(new)]=raw
 for i in range(23):
  can=canonical[i%22];logical=dict(can,path=str(out/("logical%d.json"%i)));parent=parents[i%2];field=["workers",str(i)]
  edge=dict(receipt=logical,physical=logical,parent=parent["path"],field=field,role="EXACT_TEXT_RECEIPT_READBACK")
  table.append(dict(index=i,logical=logical,canonical=can,parent=parent,field=field,link_path=str(out/("link%d"%i)),link_text="../canonical",base_edge=edge))
 closure=dict(schema="benchmark-source-receipt-closure.v1",edges=[r["base_edge"]for r in table])
 raw=json.dumps(closure).encode();cr=record(out/"BaseC.json",raw);payloads[f.rid(cr)]=raw
 raw=json.dumps(dict(source_closure=cr)).encode();br=record(out/"BaseA.json",raw);payloads[f.rid(br)]=raw
 g=types.SimpleNamespace(_WORKER_BASE=br,_WORKER_CLOSURE=cr,_WORKER_PARENTS=parents,_WORKER_TABLE=table,
  _WORKER_MODULE="default_workflow_integration",_WORKER_ROLE="SYNTHETIC_FIXED_WORKER_ROLE",
  key=lambda r:(r["path"],r["sha256"],r["bytes"]),receipt_edges=f.receipt_nodes)
 copies={x["canonical_path_as_scalar"]:x["preserved"]for x in targets}
 observations=[dict(index=r["index"],receipt=r["logical"],parent=r["parent"]["path"],field=r["field"],
  module=g._WORKER_MODULE,physical=copies[r["canonical"]["path"]])for r in table]
 authority=dict(base=md(br),closure=md(cr),parents=[md(r,mode=0o664)for r in parents])
 source=[dict(index=r["index"],metadata=dict(logical=md(r["logical"],mode=0o664),canonical=md(r["canonical"],mode=0o664),
  link=dict(md(dict(path=r["link_path"],bytes=len(r["link_text"])),mode=0o777),mode=stat.S_IFLNK|0o777),link_text=r["link_text"]))for r in table]
 scope=[dict(index=r["index"],original=r["logical"],parent_manifest=r["parent"],source_field=r["field"],module=g._WORKER_MODULE,
  canonical_path_as_scalar=r["canonical"]["path"],canonical_bytes_as_scalar=r["canonical"]["bytes"],
  canonical_sha256_as_scalar=r["canonical"]["sha256"],exact_link_path_as_scalar=r["link_path"],exact_link_text_as_scalar=r["link_text"])for r in table]
 saved=dict(schema="exact-finite-worker-control-alias-preservation.v1",status="EXACT_BASE23_CONTEXTS_22_NORMAL_JSON_CONTROL_COPIES_CPU_VERIFIED",
  accepted_base=br,accepted_base_closure=cr,raw_parent_manifests=parents,fixed_scope=scope,fixed_context_n=23,canonical_target_n=22,
  unique_expected_fingerprint_n=22,observed_context_slots=list(range(23)),authorized_observation_n=23,observations=observations,
  output_root_as_scalar=str(out),authority_metadata_before=authority,authority_metadata_after=copy.deepcopy(authority),
  source_metadata_before=source,source_metadata_after=copy.deepcopy(source),canonical_targets=targets,
  copy_directory_metadata=md(dict(path=str(out/"finite_worker_control_bytes")),True),allocation=ALLOC,
  exact_alias_index=record(out/"finite_worker_control_aliases.json",b"synthetic-index"),
  original_worker_modes_unchanged_0664=True,all_inputs_copies_readlinks_pre_end_afteroutput_bound=True,
  every_occurrence_authorized_before_seen=True,normal_JSON_receipt_children_retained=True,child_parent_is_original_logical_worker=True,
  generic_reader_or_17_parent_permission_changed=False,source_or_scientific_promotion=False)
 index=dict(schema="exact-resource-aliases.v2",status="EXACT_FIXED23_WORKER_CONTROL_ALIASES_CPU_VERIFIED",
  aliases=[dict(original=r["logical"],archived=copies[r["canonical"]["path"]],status="READONLY_BYTE_IDENTICAL_ALIAS",role=g._WORKER_ROLE)for r in table],
  historical_unresolved=[],canonical_target_n=22,separate_original_symlink_physical_package_entry_forbidden=True,
  normal_JSON_receipt_children_retained=True,scientific_or_source_acceptance=False)
 actual=dict(edges=[dict(x,role=g._WORKER_ROLE,resolution_basis="EXACT_FINITE_READONLY_WORKER_CONTROL_BYTECOPY",
  raw_bytes_preserved=True,receipt_children_interpreted=True,child_parent_is_original_logical_worker=True,
  source_or_scientific_promotion=False)for x in observations])
 return g,saved,index,payloads,actual

def dispatch_fixture():
 g,saved,index,payloads,actual=worker_fixture()
 p=f.SavedProjection.__new__(f.SavedProjection)
 p.validated=True;p._g=g;p.proofs=[{},saved];p.indices=[{},index];p.identities={};p.source_physical={};p.source_copies={};p.source_bridge=None;p.opaque_leaf={}
 p.control_receipts={};p.transport={};p.binding={"source_context":"SYNTHETIC"};p.declarations=[]
 p.worker_copies,p.worker_children=f.worker_saved_shape(g,saved,index,ALLOC,payloads,actual)
 g._catalog_msa_old_fingerprint=lambda r:False
 return p,g,saved,index

class FiniteWorkerContextContracts(unittest.TestCase):
 def test_28_full23_context22_copy_projection_no_original_IO(self):
  g,saved,index,payloads,c=worker_fixture()
  with no_original_io():copies,children=f.worker_saved_shape(g,saved,index,ALLOC,payloads,c)
  self.assertEqual((len(copies),len(children),len(index["aliases"])),(22,22,23))
 def test_29_same_FP_keeps_distinct_raw_parent_field_slots(self):
  p,g,saved,index=dispatch_fixture();root=record("/root-request")
  first=g._WORKER_TABLE[0];other=g._WORKER_TABLE[22]
  self.assertEqual(f.fp(first["logical"]),f.fp(other["logical"]))
  for row in(first,other):
   action=p.dispatch(row["logical"],row["parent"],tuple(row["field"]),root)
   self.assertEqual(action["kind"],"WORKER_OPERATIVE");self.assertEqual(len(action["children"]),1)
  with self.assertRaisesRegex(ValueError,"exact Source-qualified"):p.dispatch(first["logical"],other["parent"],tuple(other["field"]),root)
 def test_30_wrong_context_after_valid_is_rejected_before_seen(self):
  p,g,saved,index=dispatch_fixture();row=g._WORKER_TABLE[0];root=record("/root-request")
  p.dispatch(row["logical"],row["parent"],tuple(row["field"]),root)
  with self.assertRaisesRegex(ValueError,"exact Source-qualified"):p.dispatch(row["logical"],row["parent"],("other",),root)
 def test_31_copy_directseed_has_no_ordinary_child_permission(self):
  p,g,saved,index=dispatch_fixture();cp=next(iter(p.worker_copies.values()))
  action=p.dispatch(cp,None,(),record("/root-request"))
  self.assertEqual(action["children"],[]);self.assertEqual(action["kind"],"CONTROL_BYTES")
 def test_32_documentary_declaration_is_not_an_operative_slot(self):
  p,g,saved,index=dispatch_fixture();row=g._WORKER_TABLE[0];parent=record("/bound-worker-proof")
  p.declarations=[(f.rid(parent),["fixed_scope","0","original"],f.rid(row["logical"]))]
  action=p.dispatch(row["logical"],parent,("fixed_scope","0","original"),record("/root-request"))
  self.assertEqual(action["children"],[])
  with self.assertRaises(ValueError):p.dispatch(row["logical"],parent,("fixed_scope","1","original"),record("/root-request"))
 def test_33_FP_clone_and_wrong_logical_alias_fail(self):
  p,g,saved,index=dispatch_fixture();row=g._WORKER_TABLE[0]
  with self.assertRaises(ValueError):p.dispatch(dict(row["logical"],path="/unknown.json"),row["parent"],tuple(row["field"]),record("/root-request"))
  alias=copy.deepcopy(index["aliases"][0]);alias["original"]["path"]="/unknown.json"
  with self.assertRaises(ValueError):p.worker_alias(alias)
 def test_34_worker_child_manifest_whole_semantics_cannot_be_erased(self):
  g,saved,index,payloads,c=worker_fixture();saved["canonical_targets"][0]["child_receipts"]=[]
  with no_original_io(),self.assertRaisesRegex(ValueError,"normal children"):f.worker_saved_shape(g,saved,index,ALLOC,payloads,c)
 def test_35_worker_authority_and_original_mode_cannot_be_refreshed(self):
  for change in("parent","native"):
   g,saved,index,payloads,c=worker_fixture()
   if change=="parent":saved["raw_parent_manifests"][0]=record("/different")
   else:saved["authority_metadata_before"]["parents"][0]["mode"]=stat.S_IFREG|0o444
   with no_original_io(),self.assertRaises(ValueError):f.worker_saved_shape(g,saved,index,ALLOC,payloads,c)
 def test_36_worker_all_ordered_C_occurrences_are_required(self):
  g,saved,index,payloads,c=worker_fixture();c["edges"].pop()
  with no_original_io(),self.assertRaisesRegex(ValueError,"denominator"):f.worker_saved_shape(g,saved,index,ALLOC,payloads,c)
 def test_37_worker_alias_index_full_object_not_partial_acceptance(self):
  g,saved,index,payloads,c=worker_fixture();index["unexpected"]=True
  with no_original_io(),self.assertRaisesRegex(ValueError,"keyset"):f.worker_saved_shape(g,saved,index,ALLOC,payloads,c)

def vendor_fixture():
 raw=("\n".join("DLLL "+json.dumps(dict(type="LOG"if i%2 else"METADATA",SYNTHETIC_SOFTWARE_ONLY=True,n=i))for i in range(52))+"\n").encode()
 out=f.R/"steps/24_benchmark_delivery/tmp"/"FINITE_SYNTHETIC_VENDOR"
 leaf=record(out/"original_vendor.json",raw);parent=record(out/"parent18.json",b"synthetic-parent")
 cp=dict(leaf,path=str(out/"opaque_vendor_example_bytes"/(leaf["sha256"]+"_example_resnet_log.OPAQUE.txt")))
 g=types.SimpleNamespace(_VENDOR_EXAMPLE_PARENT=parent,_VENDOR_EXAMPLE_LEAF=leaf,_VENDOR_EXAMPLE_MODULE="default_workflow_integration",
  _VENDOR_EXAMPLE_ROLE="SYNTHETIC_VENDOR_ROLE",_strict_vendor_json=f.strict_json)
 true=("original_bytes_and_metadata_unchanged","original_permission_unchanged","preserved_copy_readonly_fsynced_and_byte_identical")
 false=("original_JSON_or_parent_rewritten","receipt_children_interpreted","public_source_or_configuration_promoted",
  "scientific_content_accepted","generic_JSON_parser_or_context_permissions_changed","future_package_index_and_isolated_restore_acceptance")
 saved=dict(schema="exact-vendor-example-opaque-data-leaf.v1",status="EXACT_PARENT18_FIELD15_VENDOR_DLLL52_DATA_BYTES_PRESERVED_CPU_VERIFIED",
  parent_manifest=parent,original_data_leaf=leaf,source_field=["15"],module=g._VENDOR_EXAMPLE_MODULE,role=g._VENDOR_EXAMPLE_ROLE,
  archived_opaque_data=cp,parent_metadata_before=md(parent),parent_metadata_after=md(parent),
  original_metadata_before=md(leaf,mode=0o664),original_metadata_after=md(leaf,mode=0o664),preserved_metadata=md(cp),
  authorized_observation_n=1,vendor_inventory_row_n=18,vendor_stream_record_n=52,vendor_stream_record_types={"LOG":26,"METADATA":26},
  allocation=ALLOC,exact_alias_index=record(out/"vendor_example_opaque_aliases.json",b"index"))
 saved.update({k:True for k in true});saved.update({k:False for k in false})
 index=dict(schema="exact-resource-aliases.v2",status="EXACT_VENDOR_EXAMPLE_OPAQUE_DATA_BYTE_ALIAS_CPU_VERIFIED",
  aliases=[dict(original=leaf,archived=cp,status="READONLY_BYTE_IDENTICAL_ALIAS",role=g._VENDOR_EXAMPLE_ROLE)],
  historical_unresolved=[],separate_original_JSON_physical_package_entry_forbidden=True,scientific_or_source_acceptance=False)
 return g,saved,index,raw

def catalog_fixture(g):
 catalog={k:None for k in g._CATALOG_MSA_KEYS}
 old=record("/synthetic/operative_current_source.py",b"current-operative")
 catalog.update(schema="native74_cache_catalog.v1",status="NATIVE74_RAW_CACHE_CATALOG_VERIFIED_FUTURE_FORMAL_BINDING_PENDING",
  historical_MSA_derivation_gaps_preserved=copy.deepcopy(g._CATALOG_MSA_DEFINITIONS),historical_missing_exemption_for_current_inputs=False,
  independent_edge_seal=g._CATALOG_MSA_EDGE_SEAL,workers=20,raw_models=74,split_recovery_index18_retained=True,
  no_new_predictions=True,no_scores_transferred=True,new_inference_GPU_seconds=0,old_GPU_cost_not_recharged=True,
  future_formal_binding=False,old_source=old)
 accepted=dict(status="CPU_CACHE_GUARD_CATALOG_COMPLETE",result=g._CATALOG_MSA_CATALOG,
  no_inference=True,no_GPU_submission=True,formal_binding=False,SYNTHETIC_SOFTWARE_ONLY=True)
 gaps=[{"SYNTHETIC_OTHER_GAP":True}];edges=[]
 for definition in g._CATALOG_MSA_DEFINITIONS:
  gaps.append(dict(receipt=definition["original"],subtype=definition["subtype"],role=definition["role"],
   parent=definition["parent"],field=definition["trail"],shortest_receipt_chain=definition["shortest_receipt_chain"],
   root_decision=g._CATALOG_MSA_ROOT_DECISION,parent_sha256=definition["shortest_receipt_chain"][-1]["parent_sha256"],
   actual_operative_scientific_source=old))
  edges.append(dict(receipt=definition["original"],parent=definition["parent"],field=definition["trail"],
   role="TYPED_NONOPERATIVE_HISTORICAL_GAP"))
 base=dict(historical_gaps=gaps,edges=edges,source_missing_allowed_only_exact_historical_edges=True)
 native=[md(r)for r in g._catalog_msa_controls()]
 module="final_delivery_tools"
 actual=[dict(receipt=g._CATALOG_MSA_CATALOG,module=module,physical=g._CATALOG_MSA_CATALOG,role="EXACT_NEW_TEXT_RECEIPT_READBACK")]
 for slot in(1,0):
  actual.append(dict(receipt=g._CATALOG_MSA_DEFINITIONS[slot]["original"],parent=g._CATALOG_MSA_CATALOG["path"],
   field=[g._CATALOG_MSA_FIELD,str(slot),"original"],module=module,role=g._CATALOG_MSA_ROLE,
   catalog_msa_gap_projection=g._catalog_msa_projection(slot,native)))
 return catalog,accepted,base,dict(base_closure=g._CATALOG_MSA_BASE_C,edges=actual)

class FiniteVendorAndCatalogContracts(unittest.TestCase):
 def test_38_vendor52_saved_DATA_preserves0664_provenance_without_original_IO(self):
  g,saved,index,raw=vendor_fixture()
  with no_original_io():self.assertTrue(f.vendor_saved_shape(g,saved,index,ALLOC,raw))
 def test_39_vendor_documentary_children_do_not_become_reader_permissions(self):
  g,saved,index,raw=vendor_fixture();saved["receipt_children_interpreted"]=True
  with no_original_io(),self.assertRaises(ValueError):f.vendor_saved_shape(g,saved,index,ALLOC,raw)
 def test_40_vendor_fullproof_and_copy_bytes_tamper_fail(self):
  for kind in("bytes","proof","alias"):
   g,saved,index,raw=vendor_fixture()
   if kind=="bytes":raw=raw[:-1]
   elif kind=="proof":saved["unexpected"]=True
   else:index["scientific_or_source_acceptance"]=True
   with no_original_io(),self.assertRaises(ValueError):f.vendor_saved_shape(g,saved,index,ALLOC,raw)
 def test_41_catalog_three_object_projection_retains_two_ordered_gaps(self):
  g=semantics();catalog,a,base,c=catalog_fixture(g)
  with no_original_io():self.assertTrue(g.catalog_msa_gap_projection_shape(catalog,a,base,c))
  self.assertEqual(len(g.catalog_msa_gap_projection_native(c)),3)
 def test_42_catalog_current_input_exemption_and_role_promotion_fail(self):
  g=semantics()
  for kind in("exemption","role"):
   catalog,a,base,c=catalog_fixture(g)
   if kind=="exemption":catalog["historical_missing_exemption_for_current_inputs"]=True
   else:c["edges"][1]["role"]="EXACT_NEW_TEXT_RECEIPT_READBACK"
   with no_original_io(),self.assertRaises(ValueError):g.catalog_msa_gap_projection_shape(catalog,a,base,c)
 def test_43_catalog_fullmodule_parent_trail_order_and_native_binding_fail(self):
  g=semantics()
  for kind in("module","parent","field","order","native"):
   catalog,a,base,c=catalog_fixture(g)
   if kind=="module":c["edges"][1]["module"]="unrelated"
   elif kind=="parent":c["edges"][1]["parent"]="/other"
   elif kind=="field":c["edges"][1]["field"]=[g._CATALOG_MSA_FIELD,"0","original"]
   elif kind=="order":c["edges"][1],c["edges"][2]=c["edges"][2],c["edges"][1]
   else:c["edges"][2]["catalog_msa_gap_projection"]["original_metadata_after"][0]["ctime_ns"]+=1
   with no_original_io(),self.assertRaises(ValueError):g.catalog_msa_gap_projection_shape(catalog,a,base,c)
 def test_44_publication_kind_uses_original_JSON_not_TXT_extension(self):
  g=semantics();original=record(f.R/"history/plan.json",b"{}");physical=dict(original,path=str(f.R/"copies/plan.OPAQUE.txt"))
  source_i=record("/inclusion.json");stage=record("/stage.json")
  bridge,proof,raw=bridge_fixture(f.R/"steps/24_benchmark_delivery/tmp/SYNTHETIC_PUBLISHER")
  manifest=dict(schema="finite-late-source-publication.v2",status="EXACT_FINITE_LATE_SOURCE_TREE_BYTES_CPU_VERIFIED_NOT_SCIENTIFIC_ACCEPTANCE",
   source_inclusion=source_i,stage_acceptance=stage,files=[dict(logical_receipt=original,physical_receipt=physical,
   repository_relative="delivery_tools/history/plan.json",kind="CONFIGURATION_OR_LAUNCHER",roles=["final_delivery_tools"]),
   dict(logical_receipt=bridge["eligible_copy"],physical_receipt=bridge["eligible_copy"],repository_relative=f.SOURCE_TEXT_DEST,kind="IMPLEMENTATION",roles=["final_delivery_tools"])],
   source_text_provenance_bridges=[bridge],raw_JSON_rewritten=False,source_inclusion_rewritten=False,Source_IDs_invented=False,filename_SHA_inferred=False)
  with no_original_io():self.assertEqual(len(f.late_publication_shape(manifest,source_i,stage,g)[0]),2)
  manifest["files"][0]["kind"]="DOCUMENT"
  with no_original_io(),self.assertRaises(ValueError):f.late_publication_shape(manifest,source_i,stage,g)

class FiniteBindingRepairContracts(unittest.TestCase):
 def test_45_every_Source_receipt_candidate_requires_the_same_complete_FP(self):
  base=FiniteIdentityContracts().row()
  for field in("source","physical_receipt","original_source","logical_receipts"):
   for scalar,value in(("bytes",base["source"]["bytes"]+1),("sha256","0"*64)):
    row=copy.deepcopy(base);bad=dict(base["source"],path="/another-logical-or-copy.py");bad[scalar]=value
    if field=="logical_receipts":row[field]=[bad]
    else:row[field]=bad
    with self.subTest(field=field,scalar=scalar),no_original_io(),self.assertRaisesRegex(ValueError,"complete fingerprints differ"):
     f.identity_multimap([row])
 def test_46_same_name_INDEX_class_cannot_inject_a_reader(self):
  owned=m.restore_index_api();package={}
  forged=type("StrictIndex",(),{"__module__":owned.__name__})()
  forged.pkg=package;forged.rows={};forged.aliases={}
  forged.verify=mock.Mock(side_effect=AssertionError("Forged INDEX reader must not execute"))
  with no_original_io(),self.assertRaisesRegex(ValueError,"same-OWN loaded StrictIndex class identity"):
   f.indexed_payloads(closed_binding(),package,forged)
  self.assertFalse(forged.verify.called)


# Every object below is a synthetic software fixture. None is an actual Source,
# stage, publisher, package or restored acceptance. No original TXT is read.
def bridge_fixture(root):
 raw=b"# SYNTHETIC DATA BYTECOPY - NEVER EXECUTE\n"
 raw+=b" "*(f.SOURCE_TEXT_BYTES-len(raw))
 original=record(f.SOURCE_TEXT_ORIGIN,raw)
 copy_r=record(root/"source_text_bytes"/f.SOURCE_TEXT_PY,raw)
 bridge=dict(schema=f.BRIDGE_SCHEMA,role=f.BRIDGE_ROLE,original_text=original,
  original_metadata_before=md(original),original_metadata_after=md(original),
  eligible_copy=copy_r,eligible_copy_metadata=md(copy_r),repository_relative=f.SOURCE_TEXT_DEST,
  byte_identity_proof=record(f.R/"steps/24_benchmark_delivery/submissions/SYNTHETIC_PUBLISHER/proof.json"))
 proof={k:copy.deepcopy(v)for k,v in bridge.items()if k!="byte_identity_proof"}
 proof.update(source_inclusion=record("/inclusion.json"),stage_acceptance=record("/stage.json"),
  publisher_output_root=str(root),allocation=dict(ALLOC),original_or_copied_text_executed=False,
  original_text_promoted_to_Source=False,generic_reader_permission_changed=False)
 return bridge,proof,raw

def route_rows(root):
 raw=b"SYNTHETIC Source copies; never executed\n"
 original=record(f.R/"source/SYNTHETIC_original.py",raw)
 rows=[]
 for number in(1,2):
  p=root/("copy%d.py"%number);p.write_bytes(raw);p.chmod(0o444)
  rows.append(dict(original_source=original,source=record(p,raw),repository_relative="history/destination%d.py"%number,
   roles=["final_delivery_tools"],kind="IMPLEMENTATION",logical_receipts=[]))
 return rows

def route_projection(rows,routes,bridge=None):
 # Explicitly partial synthetic data-plane fixture, not full SavedProjection acceptance.
 p=f.SavedProjection.__new__(f.SavedProjection)
 p.identities,p.by_fp,p.destinations,p.source_copies,p.source_physical=f._source_route_table(rows,routes)
 p.source_rows=rows;p.source_routes=routes;p.source_bridge=bridge;p.transport={};p.validated=True
 p._g=types.SimpleNamespace(_WORKER_TABLE=[],_catalog_msa_old_fingerprint=lambda r:False)
 p.opaque_leaf={};p.worker_copies={};p.worker_children={};p.declarations=[]
 p.control_receipts={};p.binding={"source_context":"SYNTHETIC"}
 return p

def real_index(root,receipts,raw_by_id):
 owned=m.restore_index_api();restored=root/"restored";restored.mkdir()
 package=dict(schema="benchmark-delivery-package.v1",status="PACKAGED_AWAITING_INDEPENDENT_RESTORE",
  authority_root=str(f.R),manifest=[])
 for r in receipts:
  relative=Path(r["path"]).relative_to(f.R).as_posix();p=restored/relative;p.parent.mkdir(parents=True,exist_ok=True)
  p.write_bytes(raw_by_id[f.rid(r)]);p.chmod(0o444)
  package["manifest"].append(dict(receipt=r,relative=relative))
 index=owned.StrictIndex(package,restored,restored/"new_output")
 return owned,package,index

class FiniteIndexAndRouteContracts(unittest.TestCase):
 def test_47_real_same_OWN_StrictIndex_uses_its_actual_physical_Path(self):
  with tempfile.TemporaryDirectory()as td:
   root=Path(td);raw=b"actual indexed synthetic bytes";r=record(f.R/"history/INDEX_SOURCE.py",raw)
   owned,pkg,index=real_index(root,[r],{f.rid(r):raw})
   baseline={};self.assertEqual(f._indexed_source_bytes(pkg,index,r,{},baseline),raw)
   tag=index.verify(r);self.assertIsInstance(tag,owned.IndexedPath)
   self.assertNotEqual(tag.physical(),index.rows[f.rid(r)][1])
   self.assertEqual(index.physical(tag),index.rows[f.rid(r)][1])
   self.assertEqual(len(baseline),1);index.after()
 def test_48_real_StrictIndex_different_verified_tag_cannot_change_physical_route(self):
  with tempfile.TemporaryDirectory()as td:
   root=Path(td);raw=b"same synthetic bytes";a=record(f.R/"history/A.py",raw);b=record(f.R/"history/B.py",raw)
   owned,pkg,index=real_index(root,[a,b],{f.rid(a):raw,f.rid(b):raw})
   original=index.verify;calls=[]
   def changed_tag(r):
    calls.append(r);original(r);return original(b)
   with mock.patch.object(index,"verify",side_effect=changed_tag),self.assertRaisesRegex(ValueError,"verified physical route changed"):
    f._indexed_source_bytes(pkg,index,a,{}, {})
   self.assertEqual(calls,[a])
 def test_49_two_same_FP_copies_and_two_destinations_are_all_retained(self):
  with tempfile.TemporaryDirectory()as td:
   rows=route_rows(Path(td));r=rows[0]["original_source"]
   routes=[dict(original=r,selected_physical=rows[1]["source"],repository_relative=rows[1]["repository_relative"])]
   with no_original_io():p=route_projection(rows,routes)
   self.assertEqual(len(p.identities),1);self.assertEqual(len(p.source_copies),2);self.assertEqual(len(p.destinations),2)
   self.assertEqual(p.terminal_source_receipts(),[x["source"]for x in rows])
   self.assertEqual(p.selected_source_aliases()[0]["archived"],rows[1]["source"])
   self.assertEqual(p.dispatch(r,None,(),record("/root")).get("physical"),rows[1]["source"])
   for row in rows:self.assertEqual(p.dispatch(row["source"],None,(),record("/root"))["physical"],row["source"])
 def test_50_each_logical_identity_requires_exact_explicit_candidate_selection(self):
  with tempfile.TemporaryDirectory()as td:
   rows=route_rows(Path(td));r=rows[0]["original_source"]
   route=dict(original=r,selected_physical=rows[0]["source"],repository_relative=rows[0]["repository_relative"])
   bad=[[],[route,route],[dict(route,repository_relative="history/unknown.py")],
        [dict(route,selected_physical=dict(rows[0]["source"],path=str(Path(td)/"unknown.py")))],
        [dict(route,selected_physical=dict(rows[0]["source"],sha256="0"*64))],
        [dict(route,original=dict(r,path=str(f.R/"unknown.py")))]]
   for routes in bad:
    with self.subTest(routes=routes),no_original_io(),self.assertRaises(ValueError):f._source_route_table(rows,routes)
 def test_51_unselected_copy_with_different_FP_is_still_rejected(self):
  with tempfile.TemporaryDirectory()as td:
   rows=route_rows(Path(td));r=rows[0]["original_source"]
   route=dict(original=r,selected_physical=rows[0]["source"],repository_relative=rows[0]["repository_relative"])
   rows[1]["source"]["sha256"]="0"*64
   with no_original_io(),self.assertRaisesRegex(ValueError,"fingerprints differ"):f._source_route_table(rows,[route])
 def test_52_ALL_declared_copy_receipts_require_real_INDEX_entries(self):
  with tempfile.TemporaryDirectory()as td:
   root=Path(td);rows=route_rows(root);r=rows[0]["original_source"]
   p=route_projection(rows,[dict(original=r,selected_physical=rows[0]["source"],repository_relative=rows[0]["repository_relative"])])
   raw=(root/"copy1.py").read_bytes();all_copies=p.terminal_source_receipts()
   owned,pkg,index=real_index(root,[all_copies[0]],{f.rid(all_copies[0]):raw})
   self.assertEqual(f._indexed_source_bytes(pkg,index,all_copies[0],{},{}),raw)
   with self.assertRaisesRegex(ValueError,"absent from package INDEX"):f._indexed_source_bytes(pkg,index,all_copies[1],{},{})

class FiniteSourceTextBridgeContracts(unittest.TestCase):
 def setUp(self):self.g=semantics()
 def test_53_actual_synthetic_py_bytecopy_is_validated_without_original_TXT_IO(self):
  with tempfile.TemporaryDirectory()as td:
   root=Path(td);bridge,proof,raw=bridge_fixture(root)
   p=Path(bridge["eligible_copy"]["path"]);p.parent.mkdir();p.write_bytes(raw);p.chmod(0o444)
   observed=p.read_bytes();self.assertEqual(observed,raw);self.assertEqual(record(p,observed),bridge["eligible_copy"])
   bridge["eligible_copy_metadata"]=f.native(p);proof["eligible_copy_metadata"]=dict(bridge["eligible_copy_metadata"])
   with no_original_io():result=f.source_text_bridge_shape(bridge,proof,observed,proof["source_inclusion"],proof["stage_acceptance"],self.g)
   self.assertEqual(result["original"],bridge["original_text"]);self.assertTrue(result["original_is_nonoperative"])
 def test_54_wrong_original_path_or_complete_FP_cannot_be_bridged(self):
  bridge,proof,raw=bridge_fixture(f.R/"steps/24_benchmark_delivery/tmp/SYNTHETIC")
  for field,value in(("path",str(f.R/"history/other.txt")),("bytes",64943),("sha256","0"*64)):
   b=copy.deepcopy(bridge);b["original_text"][field]=value
   with self.subTest(field=field),no_original_io(),self.assertRaises(ValueError):f.source_text_bridge_shape(b,proof,raw,proof["source_inclusion"],proof["stage_acceptance"],self.g)
 def test_55_original_or_copy_native_provenance_cannot_drift_or_become_writable(self):
  bridge,proof,raw=bridge_fixture(f.R/"steps/24_benchmark_delivery/tmp/SYNTHETIC")
  for field,change in(("original_metadata_after",{"ctime_ns":2}),("original_metadata_before",{"mode":stat.S_IFREG|0o664}),
    ("eligible_copy_metadata",{"nlink":2}),("eligible_copy_metadata",{"path":"/wrong.py"})):
   b=copy.deepcopy(bridge);b[field].update(change)
   with self.subTest(field=field,change=change),no_original_io(),self.assertRaises(ValueError):f.source_text_bridge_shape(b,proof,raw,proof["source_inclusion"],proof["stage_acceptance"],self.g)
 def test_56_actual_publisher_proof_binds_I_stage_copy_flags_and_allocation(self):
  bridge,proof,raw=bridge_fixture(f.R/"steps/24_benchmark_delivery/tmp/SYNTHETIC")
  bad=[dict(proof,source_inclusion=record("/wrong.json")),dict(proof,stage_acceptance=record("/wrong_stage.json")),
   dict(proof,original_or_copied_text_executed=True),dict(proof,original_text_promoted_to_Source=True),
   dict(proof,generic_reader_permission_changed=True),dict(proof,allocation=dict(ALLOC,allocated_gpus=1)),
   dict(proof,unexpected={"path":f.SOURCE_TEXT_ORIGIN})]
  for p in bad:
   with no_original_io(),self.assertRaises(ValueError):f.source_text_bridge_shape(bridge,p,raw,proof["source_inclusion"],proof["stage_acceptance"],self.g)
 def test_57_unknown_copy_destination_root_or_wholebytes_is_rejected(self):
  bridge,proof,raw=bridge_fixture(f.R/"steps/24_benchmark_delivery/tmp/SYNTHETIC")
  for b,p,data in((dict(bridge,repository_relative="delivery_tools/other.py"),proof,raw),
    (bridge,dict(proof,publisher_output_root=str(f.R/"other")),raw),(bridge,proof,raw[:-1]+b"X"),
    (dict(bridge,eligible_copy=dict(bridge["eligible_copy"],path=str(f.R/"history/other.py"))),proof,raw)):
   with no_original_io(),self.assertRaises(ValueError):f.source_text_bridge_shape(b,p,data,proof["source_inclusion"],proof["stage_acceptance"],self.g)
 def test_58_only_two_exact_provenance_fields_dispatch_without_payload_or_Source(self):
  bridge,proof,raw=bridge_fixture(f.R/"steps/24_benchmark_delivery/tmp/SYNTHETIC")
  row=dict(original_source=bridge["eligible_copy"],source=bridge["eligible_copy"],repository_relative=f.SOURCE_TEXT_DEST,kind="IMPLEMENTATION",roles=["final_delivery_tools"],logical_receipts=[])
  p=route_projection([row],[dict(original=row["original_source"],selected_physical=row["source"],repository_relative=f.SOURCE_TEXT_DEST)],bridge)
  late=record("/late.json");p.binding["late_source_publication"]=late
  p.control_receipts={f.rid(late):late,f.rid(bridge["byte_identity_proof"]):bridge["byte_identity_proof"]}
  for parent,field in((late,("source_text_provenance_bridges","0","original_text")),(bridge["byte_identity_proof"],("original_text",))):
   with no_original_io():edge=p.dispatch(bridge["original_text"],parent,field,record("/root"))
   self.assertEqual(edge["kind"],"DOCUMENTARY_SOURCE_TEXT_PROVENANCE");self.assertIsNone(edge["physical"]);self.assertEqual(edge["children"],[])
   self.assertFalse(edge["original_is_Source"])
   control=p.dispatch(parent,None,(),record("/root"));self.assertEqual(len(control["children"]),1)
   self.assertEqual(control["children"][0],dict(receipt=bridge["original_text"],field=list(field)))
 def test_59_direct_TXT_wrong_context_and_after_valid_clone_fail_before_seen(self):
  bridge,proof,raw=bridge_fixture(f.R/"steps/24_benchmark_delivery/tmp/SYNTHETIC");p=route_projection([],[],bridge)
  late=record("/late.json");p.binding["late_source_publication"]=late;root=record("/root")
  p.dispatch(bridge["original_text"],late,("source_text_provenance_bridges","0","original_text"),root)
  cases=[(bridge["original_text"],None,()),(bridge["original_text"],late,("files","0","logical_receipt")),
   (bridge["original_text"],record("/other.json"),("original_text",)),
   (dict(bridge["original_text"],path=str(f.R/"unknown.txt")),None,()),
   (dict(bridge["original_text"],sha256="0"*64),late,("source_text_provenance_bridges","0","original_text"))]
  for r,parent,field in cases:
   with no_original_io(),self.assertRaises(ValueError):p.dispatch(r,parent,field,root)
 def test_60_v1_unknown_bridge_and_operative_TXT_publication_rows_are_rejected(self):
  bridge,proof,raw=bridge_fixture(f.R/"steps/24_benchmark_delivery/tmp/SYNTHETIC")
  py=dict(logical_receipt=bridge["eligible_copy"],physical_receipt=bridge["eligible_copy"],repository_relative=f.SOURCE_TEXT_DEST,roles=["final_delivery_tools"],kind="IMPLEMENTATION")
  manifest=dict(schema="finite-late-source-publication.v2",status="EXACT_FINITE_LATE_SOURCE_TREE_BYTES_CPU_VERIFIED_NOT_SCIENTIFIC_ACCEPTANCE",
   source_inclusion=proof["source_inclusion"],stage_acceptance=proof["stage_acceptance"],files=[py],source_text_provenance_bridges=[bridge],
   raw_JSON_rewritten=False,source_inclusion_rewritten=False,Source_IDs_invented=False,filename_SHA_inferred=False)
  with no_original_io():self.assertEqual(len(f.late_publication_shape(manifest,proof["source_inclusion"],proof["stage_acceptance"],self.g)[0]),1)
  for bad in(dict(manifest,schema="finite-late-source-publication.v1"),dict(manifest,unknown=bridge),
    dict(manifest,source_text_provenance_bridges=[]),dict(manifest,source_text_provenance_bridges=[dict(bridge,role="SOURCE")]),
    dict(manifest,files=[dict(py,logical_receipt=bridge["original_text"])])):
   with no_original_io(),self.assertRaises(ValueError):f.late_publication_shape(bad,proof["source_inclusion"],proof["stage_acceptance"],self.g)
 def test_61_original_TXT_and_unknown_same_FP_aliases_never_reach_generic_reader(self):
  bridge,proof,raw=bridge_fixture(f.R/"steps/24_benchmark_delivery/tmp/SYNTHETIC");p=route_projection([],[],bridge)
  original=bridge["original_text"]
  for r in(original,dict(original,path=str(f.R/"unknown.txt"))):
   e=dict(original=r,archived=bridge["eligible_copy"],status="READONLY_BYTE_IDENTICAL_ALIAS")
   with no_original_io(),mock.patch.object(m,"merge_alias",side_effect=AssertionError("Generic alias IO forbidden"))as generic,self.assertRaises(ValueError):
    m.merge_finite_aliases([e],{},p)
   generic.assert_not_called()
 def test_62_live_input_and_restored_INDEX_cannot_read_original_TXT(self):
  bridge,proof,raw=bridge_fixture(f.R/"steps/24_benchmark_delivery/tmp/SYNTHETIC")
  with no_original_io(),self.assertRaisesRegex(ValueError,"never a live input"):f.CurrentInputs().read(bridge["original_text"])
  with tempfile.TemporaryDirectory()as td:
   owned,pkg,index=real_index(Path(td),[bridge["original_text"]],{f.rid(bridge["original_text"]):raw})
   with mock.patch.object(index,"verify",side_effect=AssertionError("No indexed original TXT read"))as verify,self.assertRaisesRegex(ValueError,"cannot enter INDEX"):
    f.indexed_payloads(closed_binding(),pkg,index)
   verify.assert_not_called()

class FiniteSelectedAliasProjectionContracts(unittest.TestCase):
 def test_63_real_candidate_alias_order_and_repetition_cannot_undo_explicit_selection(self):
  with tempfile.TemporaryDirectory()as td:
   rows=route_rows(Path(td));original=rows[0]["original_source"]
   # copy1 sorts before copy2; the unchanged generic lexicographic policy would choose copy1.
   route=dict(original=original,selected_physical=rows[1]["source"],repository_relative=rows[1]["repository_relative"])
   p=route_projection(rows,[route]);candidates=[dict(original=original,archived=x["source"],status="READONLY_BYTE_IDENTICAL_ALIAS",role="EXACT_NATIVE_RESOURCE_BYTES")for x in rows]
   original_verify=m.verify;seen=[]
   def actual_verify(r,*args,**kwargs):
    seen.append(r);return original_verify(r,*args,**kwargs)
   for order in(candidates,list(reversed(candidates)),[candidates[1],candidates[0],candidates[0],candidates[1]]):
    aliases={}
    with mock.patch.object(m,"verify",side_effect=actual_verify):
     m.merge_finite_aliases(order,aliases,p)
     m.merge_finite_aliases(p.selected_source_aliases(),aliases,p)
     m.merge_finite_aliases([candidates[0]],aliases,p)
    self.assertEqual(aliases[m.key(original)]["archived"],rows[1]["source"])
   self.assertTrue(all(x["source"]in seen for x in rows))
   self.assertEqual(p.terminal_source_receipts(),[x["source"]for x in rows])
   self.assertEqual(set(p.destinations),{x["repository_relative"]for x in rows})
 def test_64_other_identity_candidate_and_same_FP_unknown_aliases_are_rejected(self):
  with tempfile.TemporaryDirectory()as td:
   root=Path(td);rows=route_rows(root);raw=(root/"copy1.py").read_bytes()
   other_copy=root/"other.py";other_copy.write_bytes(raw);other_copy.chmod(0o444)
   other_original=record(f.R/"source/SYNTHETIC_other.py",raw)
   other=dict(rows[0],original_source=other_original,source=record(other_copy,raw),repository_relative="history/other.py")
   all_rows=rows+[other];original=rows[0]["original_source"]
   routes=[dict(original=original,selected_physical=rows[1]["source"],repository_relative=rows[1]["repository_relative"]),
    dict(original=other_original,selected_physical=other["source"],repository_relative=other["repository_relative"])]
   p=route_projection(all_rows,routes)
   good=dict(original=original,archived=rows[0]["source"],status="READONLY_BYTE_IDENTICAL_ALIAS")
   bad=[dict(good,archived=other["source"]),dict(good,archived=dict(rows[0]["source"],path=str(root/"unmatched.py"))),
    dict(good,original=dict(original,path=str(f.R/"source/unknown_clone.py"))),dict(good,status="UNPROVEN")]
   for e in bad:
    with self.subTest(alias=e),mock.patch.object(m,"verify",side_effect=AssertionError("Rejected alias cannot read any candidate"))as verifier,self.assertRaises(ValueError):
     m.merge_finite_aliases([e],{},p)
    verifier.assert_not_called()


# Six fixed operational raw byte fixtures are captured only by the owned CPU bootstrap.
OPERATIONAL_FIXTURE_BYTES={}
def operational_fixture(root,known_cache=True):
 root=f.R/"steps/24_benchmark_delivery/submissions"/(f.OPERATIONAL_ROOT_PREFIX+ALLOC["job_id"])
 raw_by_id={};rows=[];new_four=[];legacy_entries=[];native_rows=[]
 source_i=record(root/"source_I.json");stage=record(root/"stage_A.json")
 def supply(r,raw):raw_by_id[f.rid(r)]=raw
 for n,fixed in enumerate(f.WRAPPER_NEW_FOUR):
  raw=OPERATIONAL_FIXTURE_BYTES[fixed[0]];original=record(fixed[0],raw)
  source=record(root/"operational_shell_sources"/(fixed[2]+".sh"),raw)
  evidence=record(root/"operational_evidence"/("wrapper_new_%02d.OPAQUE.txt"%n),raw)
  item=dict(original_text=original,original_metadata=md(original),evidence_copy=evidence,evidence_metadata=md(evidence),
   eligible_source=source,eligible_source_metadata=md(source),repository_relative=fixed[3])
  native_rows.append(item["original_metadata"]);new_four.append(item)
  rows.append(dict(original_source=source,source=source,repository_relative=fixed[3],kind="CONFIGURATION_OR_LAUNCHER",roles=["final_delivery_tools"],logical_receipts=[]))
  supply(source,raw);supply(evidence,raw)
 cap={key:None for key in f.LEGACY_CAP_KEYS}
 cap.update(schema="root-exact-wrapper-shell-source-byte-preservation.v1",
  status="ACTUAL_TWO_WRAPPER_BYTES_AND_OWN_OPERATIONAL_SHELL_SOURCE_CPU_PRESERVED_NOT_EXECUTED",
  actual_job_id="16998",allocation=dict(ALLOC,job_id="16998"),fixed_two_preservations=[])
 for key in("original_two_text_files_not_rewritten","no_header_or_payload_change","no_preserved_wrapper_execution",
  "no_new_Source_software_or_API_permission","source12_Core_fixed_inputs_pre_end_afteroutput_PASS",
  "no_tests_or_scientific_child_IO","whole_capture_and_claims_LATE_not_own_Plan_prerequisites"):cap[key]=True
 for key in("Source_audit_acceptance","source_staged","published","ACTIVE_changed"):cap[key]=False
 for n,fixed in enumerate(f.WRAPPER_LEGACY_TWO):
  raw=OPERATIONAL_FIXTURE_BYTES[fixed[0]];original=record(fixed[0],raw);source=record(fixed[3],raw)
  evidence=record(root/"operational_evidence"/("wrapper_legacy_%02d.OPAQUE.txt"%n),raw)
  item=dict(original_text=original,original_metadata=md(original),evidence_copy=evidence,evidence_metadata=md(evidence),
   eligible_source=source,eligible_source_metadata=md(source),repository_relative=fixed[4])
  native_rows.append(item["original_metadata"]);legacy_entries.append(item)
  cap["fixed_two_preservations"].append(dict(original=original,original_metadata_before=item["original_metadata"],
   preserved=source,preserved_metadata=item["eligible_source_metadata"],repository_relative=fixed[4],byte_identical=True,
   original_suffix=".txt",preserved_suffix=".sh",preserved_wrapper_not_executed=True))
  rows.append(dict(original_source=source,source=source,repository_relative=fixed[4],kind="CONFIGURATION_OR_LAUNCHER",roles=["final_delivery_tools"],logical_receipts=[]))
  supply(source,raw);supply(evidence,raw)
 directories=[md(dict(path=path),True)for path in f.CACHE_ROOTS];native_rows.extend(directories)
 members=[];names={}
 for n,path in enumerate(f.CACHE_ROOTS):
  raw=OPERATIONAL_FIXTURE_BYTES[f.WRAPPER_NEW_FOUR[0][0]]if n==0 else(b'{"synthetic_cache":'+str(n).encode()+b'}')
  original=record(Path(path)/("synthetic_%02d.py"%n),raw)
  evidence=record(root/"operational_evidence"/("cache_%05d.OPAQUE.txt"%n),raw)
  original_md=md(original);native_rows.append(original_md)
  members.append(dict(original_receipt=original,original_metadata=original_md,evidence_copy=evidence,evidence_metadata=md(evidence)))
  names[path]=[Path(original["path"]).name];supply(evidence,raw)
  if known_cache and n==0:
   rows.append(dict(original_source=original,source=original,repository_relative="synthetic/cache_known.py",
    kind="IMPLEMENTATION",roles=["final_delivery_tools"],logical_receipts=[]));supply(original,raw)
 tro=dict(schema="root-plan-v13-stage17809-terminal-metadata-readonly-seal.v1",
  status="ACTUAL_I_SELECTED_SOURCE_STAGE17809_ROOT_TWO_CONTENT_AND_TERMINAL_METADATA_READONLY_PASS_NOT_GIT_OR_PUBLICATION",
  actual_job_id="17809",Root_and_two_whole_content_PASS=True,metadata_only=True,Git_changed=False,published=False,ACTIVE_changed=False,
  protected_non_job_metadata=native_rows,job_owned_metadata_after=[],fixed_source_and_control_directory_children=names,
  actual_Stage_acceptance=stage,actual_CPU_descriptor=dict(source_inclusion=source_i,stage_acceptance=stage,
   true_last_original_native_union_PASS=True,allocation=dict(ALLOC,job_id="17809")),
  fresh_terminal=dict(returncode=0,raw_stderr="",raw_stdout="17809|synthetic|COMPLETED|0:0|50|1|billing=1,cpu=1,node=1|start|end\n"))
 tro_r=dict(path=f.STAGE_TERMINAL_PATH,bytes=f.STAGE_TERMINAL_NATIVE["bytes"],sha256="1"*64)
 cap_r=dict(path=f.LEGACY_CAPTURE_PATH,bytes=f.LEGACY_CAPTURE_NATIVE["bytes"],sha256="2"*64)
 saved=dict(schema=f.OPERATIONAL_SCHEMA,status=f.OPERATIONAL_STATUS,source_inclusion=source_i,stage_acceptance=stage,
  stage_terminal_metadata=tro_r,legacy_capture=cap_r,publisher_output_root=str(root),allocation=ALLOC,
  new_four=new_four,legacy_two=dict(capture=cap_r,entries=legacy_entries),
  cache_history=dict(directories=directories,members=members),original_bytes_and_native_pre_end_afteroutput_PASS=True,
  original_or_copied_programs_executed=False,original_text_promoted_to_Source=False,cache_Source_IDs_invented=False,
  generic_reader_permission_changed=False,scientific_or_restore_acceptance=False,ACTIVE_changed=False)
 return saved,tro,cap,rows,raw_by_id

def operational_route_fixture(root,known_cache=True):
 saved,tro,cap,rows,payloads=operational_fixture(root,known_cache)
 routes=[dict(original=row["original_source"],selected_physical=row["source"],repository_relative=row["repository_relative"])for row in rows]
 p=route_projection(rows,routes);p.operational_saved=saved;p.binding["operational_source_provenance"]=record(Path(saved["publisher_output_root"])/"operational_source_provenance.json")
 p.operational=f.operational_source_provenance_shape(saved,tro,cap,saved["source_inclusion"],saved["stage_acceptance"],rows,payloads,semantics())
 p.operational_routes={}
 for original,copy,field in p.operational["caches"]:
  known=f.rid(original)in p.identities
  p.operational_routes[f.rid(original)]=dict(original=original,physical=original if known else copy,
   role="EXISTING_SOURCE_ROUTE"if known else"INDEPENDENT_CACHE_EVIDENCE")
 p.control_receipts={f.rid(p.binding["operational_source_provenance"]):p.binding["operational_source_provenance"]}
 return p,saved,tro,cap,rows,payloads


class OperationalProvenanceContracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.g=semantics()
 def fixture(self):
  return operational_fixture(f.R/"steps/24_benchmark_delivery/tmp/SYNTHETIC_OP")
 def checked(self,packet):
  saved,tro,cap,rows,payloads=packet
  with no_original_io():return f.operational_source_provenance_shape(saved,tro,cap,saved["source_inclusion"],saved["stage_acceptance"],rows,payloads,self.g)
 def test_65_complete_six_and_fourteen_root_cache_proof_has_no_original_IO(self):
  packet=self.fixture();result=self.checked(packet)
  self.assertEqual((len(result["wrappers"]),len(result["caches"]),len(result["evidence"])),(6,14,20))
  self.assertEqual([x[0]["path"]for x in result["wrappers"]],list(f.WRAPPER_ORIGINAL_PATHS))
 def test_66_closed_schema_permissions_and_actual_CPU_allocation_are_required(self):
  for key,value in(("schema","unknown"),("generic_reader_permission_changed",True),("cache_Source_IDs_invented",True),
   ("original_or_copied_programs_executed",True),("original_bytes_and_native_pre_end_afteroutput_PASS",False),
   ("allocation",dict(ALLOC,allocated_gpus=1)),("extra",False)):
   packet=self.fixture();packet[0][key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):self.checked(packet)
 def test_67_exact_new_four_and_legacy_two_order_and_counts_cannot_change(self):
  for group in("new_four","legacy_two"):
   for operation in("omit","extra","reverse"):
    packet=self.fixture();entries=packet[0][group]if group=="new_four"else packet[0][group]["entries"]
    if operation=="omit":entries.pop()
    elif operation=="extra":entries.append(copy.deepcopy(entries[0]))
    else:entries.reverse()
    with self.subTest(group=group,operation=operation),self.assertRaises(ValueError):self.checked(packet)
 def test_68_new_shells_require_actual_Source_kind_roles_and_fixed_destinations(self):
  for field,value in(("kind","DOCUMENT"),("roles",["other"]),("repository_relative","wrong/shell.sh"),
   ("original_source",record("/wrong.sh"))):
   packet=self.fixture();packet[3][0][field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):self.checked(packet)
 def test_69_legacy_CAP_full_object_flags_and_existing_I_associations_are_exact(self):
  for key,value in(("actual_job_id","16999"),("Source_audit_acceptance",True),("no_preserved_wrapper_execution",False),("extra",None)):
   packet=self.fixture();packet[2][key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):self.checked(packet)
  packet=self.fixture();packet[3][4]["repository_relative"]="wrong/legacy.sh"
  with self.assertRaises(ValueError):self.checked(packet)
 def test_70_original_wrapper_metadata_must_equal_the_saved_Stage_native(self):
  for field,value in(("inode",92),("nlink",2),("mode",stat.S_IFREG|0o664),("ctime_ns",2)):
   packet=self.fixture();packet[0]["new_four"][0]["original_metadata"][field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):self.checked(packet)
 def test_71_all_cache_members_are_exact_sorted_saved_native_members(self):
  for operation in("omit","extra","reverse","outside"):
   packet=self.fixture();members=packet[0]["cache_history"]["members"]
   if operation=="omit":members.pop()
   elif operation=="extra":members.append(copy.deepcopy(members[0]))
   elif operation=="reverse":members.reverse()
   else:members[0]["original_receipt"]["path"]=str(f.R/"outside_cache.py")
   with self.subTest(operation=operation),self.assertRaises(ValueError):self.checked(packet)
 def test_72_cache_opaque_bytes_and_full_native_are_independently_verified(self):
  for key,value in(("sha256","0"*64),("path",str(f.R/"wrong.OPAQUE.txt")),("bytes",0)):
   packet=self.fixture();packet[0]["cache_history"]["members"][0]["evidence_copy"][key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):self.checked(packet)
  packet=self.fixture();packet[0]["cache_history"]["members"][0]["evidence_metadata"]["nlink"]=2
  with self.assertRaises(ValueError):self.checked(packet)
 def test_73_known_cache_Source_route_wins_and_independent_copy_is_still_EVIDENCE(self):
  p,saved,tro,cap,rows,payloads=operational_route_fixture(f.R/"steps/24_benchmark_delivery/tmp/ROUTE")
  original=saved["cache_history"]["members"][0]["original_receipt"];copy_r=saved["cache_history"]["members"][0]["evidence_copy"]
  with no_original_io():
   source=p.dispatch(original,None,(),record("/root"));evidence=p.dispatch(copy_r,None,(),record("/root"))
  self.assertEqual(source["kind"],"SOURCE_BYTES");self.assertEqual(source["physical"],original)
  self.assertEqual(evidence["kind"],"OPERATIONAL_EVIDENCE");self.assertEqual(evidence["physical"],copy_r)
  self.assertNotIn(f.rid(original),{f.rid(x["original"])for x in p.operational_aliases()})
 def test_74_raw_wrappers_only_accept_the_exact_proof_or_legacy_CAP_fields(self):
  p,saved,tro,cap,rows,payloads=operational_route_fixture(f.R/"steps/24_benchmark_delivery/tmp/CONTEXT")
  parent=p.binding["operational_source_provenance"];root=record("/root")
  for original,copy_r,field in p.operational["wrappers"]:
   with no_original_io():view=p.dispatch(original,parent,field,root)
   self.assertEqual(view["physical"],copy_r);self.assertEqual(view["children"],[]);self.assertFalse(view["original_is_Source"])
   for bad_parent,bad_field in((None,()),(parent,field+("wrong",)),(record("/other.json"),field)):
    with no_original_io(),self.assertRaises(ValueError):p.dispatch(original,bad_parent,bad_field,root)
  for n,(original,copy_r,field)in enumerate(p.operational["wrappers"][4:]):
   with no_original_io():self.assertEqual(p.dispatch(original,saved["legacy_capture"],("fixed_two_preservations",str(n),"original"),root)["physical"],copy_r)
 def test_75_unknown_cache_proof_fields_fail_before_generic_seen_after_valid_route(self):
  p,saved,tro,cap,rows,payloads=operational_route_fixture(f.R/"steps/24_benchmark_delivery/tmp/CACHE_CTX")
  original,copy_r,field=p.operational["caches"][1];parent=p.binding["operational_source_provenance"]
  with no_original_io():self.assertEqual(p.dispatch(original,parent,field,record("/root"))["physical"],copy_r)
  for r,pa,fi in((original,None,()),(original,parent,field+("other",)),
   (dict(original,sha256="0"*64),parent,field),(dict(original,path=str(f.R/"unknown_clone.py")),parent,field)):
   with no_original_io(),self.assertRaises(ValueError):p.dispatch(r,pa,fi,record("/root"))
 def test_76_generated_raw_aliases_go_only_to_exact_opaque_copies(self):
  p,saved,tro,cap,rows,payloads=operational_route_fixture(f.R/"steps/24_benchmark_delivery/tmp/ALIASES")
  for row in p.operational_aliases():
   with no_original_io():self.assertTrue(p.operational_alias(row))
   self.assertTrue(row["archived"]["path"].endswith(".OPAQUE.txt"))
  row=p.operational_aliases()[0]
  for bad in(dict(row,archived=saved["new_four"][0]["eligible_source"]),dict(row,role="SOURCE"),
   dict(row,original=dict(row["original"],path=str(f.R/"unknown_clone.txt")))):
   with no_original_io(),self.assertRaises(ValueError):p.operational_alias(bad)
 def test_77_real_INDEX_preserves_all_twenty_distinct_evidence_instances(self):
  with tempfile.TemporaryDirectory()as td:
   root=Path(td);packet=operational_fixture(root);result=self.checked(packet);receipts=result["evidence"]
   owned,pkg,index=real_index(root,receipts,packet[4]);baseline={}
   for r in receipts:self.assertEqual(f._indexed_source_bytes(pkg,index,r,{},baseline),packet[4][f.rid(r)])
   f.operational_index_native_end(index,baseline)
   self.assertEqual(len(index.rows),20);self.assertEqual(len(baseline),20)
   self.assertEqual(f.fp(receipts[0]),f.fp(receipts[6]))
   self.assertNotEqual(f.rid(receipts[0]),f.rid(receipts[6]))
 def test_78_real_INDEX_missing_one_same_FP_evidence_instance_is_rejected(self):
  with tempfile.TemporaryDirectory()as td:
   root=Path(td);packet=operational_fixture(root);result=self.checked(packet);receipts=result["evidence"]
   owned,pkg,index=real_index(root,receipts[:-1],packet[4])
   for r in receipts[:-1]:f._indexed_source_bytes(pkg,index,r,{}, {})
   with self.assertRaisesRegex(ValueError,"absent from package INDEX"):f._indexed_source_bytes(pkg,index,receipts[-1],{}, {})
 def test_79_raw_wrapper_physical_INDEX_entry_is_denied_before_any_verify(self):
  with tempfile.TemporaryDirectory()as td:
   root=Path(td);packet=operational_fixture(root);r=packet[0]["new_four"][0]["original_text"];raw=OPERATIONAL_FIXTURE_BYTES[r["path"]]
   owned,pkg,index=real_index(root,[r],{f.rid(r):raw})
   with mock.patch.object(index,"verify",side_effect=AssertionError("Raw original cannot be read"))as verifier,self.assertRaisesRegex(ValueError,"cannot enter INDEX"):
    f.indexed_payloads(closed_binding(),pkg,index)
   verifier.assert_not_called()
 def test_80_current_consumer_denies_all_six_original_wrapper_payload_reads(self):
  for path in f.WRAPPER_ORIGINAL_PATHS:
   r=record(path,OPERATIONAL_FIXTURE_BYTES[path])
   with no_original_io(),self.assertRaisesRegex(ValueError,"never a live input"):f.CurrentInputs().read(r)
 def test_81_pre_IO_plan_rejects_copy_paths_outside_the_fixed_publisher(self):
  packet=self.fixture();saved,tro,cap,rows,payloads=packet
  for group in("new_four","cache_history"):
   bad=copy.deepcopy(saved)
   entry=bad[group][0]if group=="new_four"else bad[group]["members"][0]
   entry["evidence_copy"]["path"]=str(f.R/"science/not_owned.OPAQUE.txt")
   with no_original_io(),self.assertRaises(ValueError):f._operational_input_plan(bad,tro)
 def test_82_terminal_I_stage_full_pointers_and_fresh_completion_are_required(self):
  for kind in("stage","I","terminal","CPU"):
   packet=self.fixture();tro=packet[1]
   if kind=="stage":tro["actual_Stage_acceptance"]=record("/wrong.json")
   elif kind=="I":tro["actual_CPU_descriptor"]["source_inclusion"]=record("/wrong_I.json")
   elif kind=="terminal":tro["fresh_terminal"]["raw_stdout"]=tro["fresh_terminal"]["raw_stdout"].replace("COMPLETED","FAILED")
   else:tro["actual_CPU_descriptor"]["allocation"]=dict(ALLOC,allocated_CPUs=2)
   with self.subTest(kind=kind),self.assertRaises(ValueError):self.checked(packet)
 def test_83_last_real_INDEX_read_cannot_adopt_earlier_evidence_native_drift(self):
  with tempfile.TemporaryDirectory()as td:
   root=Path(td);packet=operational_fixture(root);receipts=self.checked(packet)["evidence"][:2]
   owned,pkg,index=real_index(root,receipts,packet[4]);baseline={}
   f._indexed_source_bytes(pkg,index,receipts[0],{},baseline)
   first=index.rows[f.rid(receipts[0])][1];before=f.native(first);original=index.verify;calls=[]
   def drift(r):
    tag=original(r);calls.append(r)
    if r==receipts[1]:os.utime(first,ns=(before["mtime_ns"]+2000000000,before["mtime_ns"]+2000000000))
    return tag
   with mock.patch.object(index,"verify",side_effect=drift):
    f._indexed_source_bytes(pkg,index,receipts[1],{},baseline)
   with self.assertRaisesRegex(ValueError,"Restored Source current native drifted"):f.operational_index_native_end(index,baseline)
   self.assertEqual(calls,[receipts[1]])
 def test_84_v3_binding_adds_only_one_full_operational_control_receipt(self):
  binding=closed_binding();self.assertEqual(set(binding),f.BINDING_KEYS)
  self.assertIn("operational_source_provenance",binding);f._binding_shape(binding)
  for bad in(dict(binding,schema="finite-final-source-delivery-context.v2"),
   {k:v for k,v in binding.items()if k!="operational_source_provenance"},dict(binding,cache_callback=lambda:None)):
   with self.assertRaises(ValueError):f._binding_shape(bad)

if __name__=="__main__":unittest.main()
