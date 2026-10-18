#!/usr/bin/env python3
"""CPU-only boundary contracts; fixtures do not certify production BBF bytes."""
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from relative_receipt_policy import ExactRelativeContext,PARENT,R,S,pinned_rows,byte_verify
class Contracts(unittest.TestCase):
 def setUp(self):
  self.calls=[]
  self.obj={"job_id":"13226","status":"BBF110_INDEPENDENT_DEVELOPMENT_DIAGNOSIS_CONTENT_ACCEPTED","outputs":pinned_rows()}
  self.ctx=ExactRelativeContext(verify=lambda p,r:self.calls.append((p,copy.deepcopy(r))),reader=lambda p:copy.deepcopy(self.obj))
 def norm(self,i=0,r=None,parent=None,trail=None):
  return self.ctx.normalize(r or pinned_rows()[i],PARENT["path"]if parent is None else parent,("outputs",str(i))if trail is None else trail)
 def test_six_exact_canonical_paths(self):
  for i in range(6):
   r,row=self.norm(i);self.assertEqual(r["path"],str(S/pinned_rows()[i]["path"]));self.assertEqual(row["source_field"],["outputs",str(i)])
 def test_complete_mapping_all_six(self):
  m=self.ctx.complete_mapping();self.assertEqual(len(m["entries"]),6);self.assertTrue(m["original_json_unchanged"])
 def test_complete_mapping_schema_literal(self):
  self.assertEqual(self.ctx.complete_mapping()["status"],"EXACT_BBF13226_SIX_RELATIVE_OUTPUTS_CPU_VERIFIED_ORIGINAL_JSON_UNCHANGED")
 def test_absolute_receipt_unchanged(self):
  r={"path":str(R/"absolute.json"),"bytes":1,"sha256":"a"*64};a,c=self.norm(r=r);self.assertIs(a,r);self.assertIsNone(c);self.assertEqual(self.calls,[])
 def test_wrong_parent_rejected(self):
  with self.assertRaisesRegex(ValueError,"parent"):self.norm(parent=str(S/"other/manifest.json"))
 def test_none_parent_rejected(self):
  with self.assertRaisesRegex(ValueError,"parent"):self.ctx.normalize(pinned_rows()[0],None,())
 def test_wrong_field_rejected(self):
  with self.assertRaisesRegex(ValueError,"field"):self.norm(trail=("inputs","0"))
 def test_wrong_index_rejected(self):
  with self.assertRaisesRegex(ValueError,"field"):self.norm(trail=("outputs","6"))
 def test_negative_index_rejected(self):
  with self.assertRaisesRegex(ValueError,"field"):self.norm(trail=("outputs","-1"))
 def test_wrong_nested_field_rejected(self):
  with self.assertRaisesRegex(ValueError,"field"):self.norm(trail=("nested","outputs","0"))
 def test_wrong_slot_rejected(self):
  with self.assertRaisesRegex(ValueError,"identity"):self.norm(i=1,r=pinned_rows()[0])
 def test_same_basename_wrong_path_rejected(self):
  r=pinned_rows()[0];r["path"]="other/"+Path(r["path"]).name
  with self.assertRaisesRegex(ValueError,"identity"):self.norm(r=r)
 def test_changed_child_sha_rejected(self):
  r=pinned_rows()[0];r["sha256"]="a"*64
  with self.assertRaisesRegex(ValueError,"identity"):self.norm(r=r)
 def test_changed_child_size_rejected(self):
  r=pinned_rows()[0];r["bytes"]+=1
  with self.assertRaisesRegex(ValueError,"identity"):self.norm(r=r)
 def test_parent_hash_verified_before_child(self):
  self.norm();self.assertEqual(self.calls[0],(PARENT["path"],PARENT));self.assertEqual(self.calls[1][0],str(S/pinned_rows()[0]["path"]))
 def test_parent_byte_failure_fatal(self):
  self.ctx.verify=lambda p,r:(_ for _ in ()).throw(ValueError("parent drift"))
  with self.assertRaisesRegex(ValueError,"parent drift"):self.norm()
 def test_child_byte_failure_fatal(self):
  def fail(p,r):
   if p!=PARENT["path"]:raise ValueError("child drift")
  self.ctx.verify=fail
  with self.assertRaisesRegex(ValueError,"child drift"):self.norm()
 def test_parent_role_failure_fatal(self):
  self.obj["job_id"]="other"
  with self.assertRaisesRegex(ValueError,"role"):self.norm()
 def test_parent_outputs_changed_fatal(self):
  self.obj["outputs"].reverse()
  with self.assertRaisesRegex(ValueError,"outputs"):self.norm()
 def test_prior_allowed_edge_does_not_authorize_new_parent(self):
  self.norm()
  with self.assertRaisesRegex(ValueError,"parent"):self.norm(parent=str(S/"unexpected.json"))
 def test_byte_verifier_rejects_real_drift_and_symlink(self):
  parent=R/"steps/24_benchmark_delivery/tmp";parent.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(dir=parent,prefix="source-relative-contract-")as d:
   p=Path(d)/"x.json";p.write_bytes(b"fixture")
   r={"path":str(p),"bytes":7,"sha256":hashlib.sha256(b"fixture").hexdigest()}
   self.assertEqual(byte_verify(p,r),p);p.write_bytes(b"changed")
   with self.assertRaisesRegex(ValueError,"drift"):byte_verify(p,r)
   link=Path(d)/"link";link.symlink_to(p)
   with self.assertRaisesRegex(ValueError,"symlink"):byte_verify(link,r)
 def test_controller_normalizes_before_dedup_and_kind_branch(self):
  source=(Path(__file__).parent/"source_delivery_refresh_v8.py").read_text()
  a=source.index("r,relative_context=context.normalize(r,parent,trail)")
  self.assertLess(a,source.index("if k in seen:continue"));self.assertLess(a,source.index("if suffix not in TEXT_EXT:"));self.assertLess(source.index("annotation=annotation_or_external_failure(r,parent_context,trail,historical_annotations)"),source.index("if k in seen:continue"))
 def software_fixture(self):
  from source_delivery_refresh_v8 import SOFTWARE_PACKAGE_NAMES
  parent=R/"steps/24_benchmark_delivery/tmp";parent.mkdir(parents=True,exist_ok=True)
  t=tempfile.TemporaryDirectory(dir=parent,prefix="source-whole-binding-contract-");here=Path(t.name);rows=[]
  for name in SOFTWARE_PACKAGE_NAMES:
   p=here/name;p.write_bytes(b"fixture");p.chmod(0o444)
   rows.append({"path":str(p),"bytes":7,"sha256":hashlib.sha256(b"fixture").hexdigest()})
  return t,here,{"source_receipts":rows}
 def test_software_binding_helper_drift_rejected(self):
  from source_delivery_refresh_v8 import software_source_binding
  t,here,snapshot=self.software_fixture()
  try:
   software_source_binding(snapshot,here)
   p=here/"relative_receipt_policy.py";p.chmod(0o644);p.write_bytes(b"changed");p.chmod(0o444)
   with self.assertRaisesRegex(ValueError,"drift"):software_source_binding(snapshot,here)
  finally:t.cleanup()
 def test_software_binding_dependency_drift_rejected(self):
  from source_delivery_refresh_v8 import software_source_binding
  t,here,snapshot=self.software_fixture()
  try:
   p=here/"delivery_core.py";p.chmod(0o644);p.write_bytes(b"changed");p.chmod(0o444)
   with self.assertRaisesRegex(ValueError,"drift"):software_source_binding(snapshot,here)
  finally:t.cleanup()
 def test_software_binding_thin_snapshot_rejected(self):
  from source_delivery_refresh_v8 import software_source_binding
  t,here,snapshot=self.software_fixture()
  try:
   snapshot["source_receipts"].pop()
   with self.assertRaisesRegex(ValueError,"whole tested"):software_source_binding(snapshot,here)
  finally:t.cleanup()
 def test_actual_software_contract_counts_pass(self):
  from source_delivery_refresh_v8 import software_contract_counts
  self.assertEqual(software_contract_counts({"status":"PASS","tests":84,"failures":0,"errors":0})["tests"],84)
 def test_actual_software_fewer_contracts_rejected(self):
  from source_delivery_refresh_v8 import software_contract_counts
  with self.assertRaisesRegex(ValueError,"saved84"):software_contract_counts({"status":"PASS","tests":25,"failures":0,"errors":0})
 def test_actual_software_failure_count_rejected(self):
  from source_delivery_refresh_v8 import software_contract_counts
  with self.assertRaisesRegex(ValueError,"saved84"):software_contract_counts({"status":"PASS","tests":84,"failures":1,"errors":0})
 def test_actual_software_error_count_rejected(self):
  from source_delivery_refresh_v8 import software_contract_counts
  with self.assertRaisesRegex(ValueError,"saved84"):software_contract_counts({"status":"PASS","tests":84,"failures":0,"errors":1})

class AnnotationContracts(unittest.TestCase):
 """Finite literal-history fixtures; no missing historical file is created or opened."""
 def setUp(self):
  import source_delivery_refresh_v8 as m
  self.m=m;self.calls=[]
  self.obj={"entries":[{}for _ in range(3)],"recovery":copy.deepcopy(m.RECOVERY_MARKER)}
  for (entries,i,name),r in m.annotation_pins():self.obj["entries"][int(i)][name]=copy.deepcopy(r)
  self.ctx=m.HistoricalRecoveryAnnotations(verify=lambda p,r:self.calls.append((p,copy.deepcopy(r))),reader=lambda p:copy.deepcopy(self.obj))
  self.parent={"logical":copy.deepcopy(m.ANNOTATION_PARENT),"physical":copy.deepcopy(m.ANNOTATION_PARENT)}
 def norm(self,i=0,r=None,parent=None,trail=None):
  t,pinned=self.m.annotation_pins()[i]
  return self.m.annotation_or_external_failure(r or pinned,self.parent if parent is None else parent,t if trail is None else trail,self.ctx)
 def complete(self):
  for i in range(9):self.norm(i)
  return self.ctx.mapping([self.m.ANNOTATION_PARENT])
 def test_exact_nine_predeclared_fields_classified(self):
  result=self.complete();self.assertEqual(len(result["entries"]),9);self.assertEqual(result["historical_annotation_n"],9)
  self.assertEqual([r["source_field"]for r in result["entries"]],[list(t)for t,_ in self.m.annotation_pins()])
 def test_all_children_null_unrestored_not_byte_accepted(self):
  for row in self.complete()["entries"]:
   self.assertIsNone(row["canonical_receipt"]);self.assertFalse(row["raw_byte_acceptance"]);self.assertFalse(row["historical_file_restored"]);self.assertFalse(row["current_execution_allowed"])
 def test_anchor_is_unrecovered_not_manufactured(self):
  a=self.complete()["anchor"];self.assertIsNone(a["canonical_receipt"]);self.assertFalse(a["historical_file_restored"])
  self.assertEqual(a["expected_sha256"],self.m.LEGACY_ANCHOR["sha256"])
 def test_parent_only_read_verified_never_external_files(self):
  self.complete();self.assertTrue(self.calls)
  self.assertTrue(all(p==self.m.ANNOTATION_PARENT["path"]for p,_ in self.calls))
 def test_unknown_parent_same_descriptor_bytes_fatal(self):
  parent=copy.deepcopy(self.parent);parent["logical"]["path"]=str(self.m.R/"unknown-parent.json")
  with self.assertRaisesRegex(ValueError,"Current operative external"):self.norm(parent=parent)
  self.assertEqual(self.calls,[])
 def test_wrong_parent_sha_fatal(self):
  parent=copy.deepcopy(self.parent);parent["logical"]["sha256"]="e"*64
  with self.assertRaisesRegex(ValueError,"parent identity"):self.norm(parent=parent)
  self.assertEqual(self.calls,[])
 def test_wrong_child_sha_size_or_path_fatal(self):
  for key,value in (("sha256","a"*64),("bytes",1),("path",self.m.LEGACY_ROOT+"/other/native.pdb")):
   r=copy.deepcopy(self.m.annotation_pins()[0][1]);r[key]=value
   with self.assertRaisesRegex(ValueError,"child exact"):self.norm(r=r)
 def test_unknown_field_with_known_child_is_not_allowed(self):
  with self.assertRaisesRegex(ValueError,"Current operative external"):self.norm(trail=("current_input","0"))
 def test_previous_annotation_does_not_authorize_new_current_edge(self):
  self.norm()
  with self.assertRaisesRegex(ValueError,"Current operative external"):self.norm(trail=("inputs","0"))
 def test_marker_status_drift_fatal(self):
  self.obj["recovery"]["status"]="RECOVERED"
  with self.assertRaisesRegex(ValueError,"unrecovered history marker"):self.norm()
 def test_missing_files_marker_drift_fatal(self):
  self.obj["recovery"]["missing_files"]="currently restored"
  with self.assertRaisesRegex(ValueError,"unrecovered history marker"):self.norm()
 def test_complete_parent_nine_identity_guard(self):
  self.obj["entries"][2]["backbone"]["sha256"]="a"*64
  with self.assertRaisesRegex(ValueError,"Complete nine"):self.norm()
 def test_only_eight_observed_edges_cannot_close_mapping(self):
  for i in range(8):self.norm(i)
  with self.assertRaisesRegex(ValueError,"All nine"):self.ctx.mapping([])
 def test_scalar_map_has_no_external_receipt_shapes(self):
  obj=self.complete()
  for r,_ in self.m.receipt_edges(obj):self.assertTrue(Path(r["path"]).is_relative_to(self.m.R))
 def test_unknown_operative_external_same_old_child_under_wrong_parent_fails(self):
  r=self.m.annotation_pins()[8][1]
  with self.assertRaisesRegex(ValueError,"Current operative external"):self.m.annotation_or_external_failure(r,None,(),self.ctx)
 def test_actual_parent_byte_drift_is_rejected(self):
  from unittest.mock import patch
  parent=self.m.R/"steps/24_benchmark_delivery/tmp";parent.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(dir=parent,prefix="annotation-byte-contract-")as d:
   p=Path(d)/"synthetic-parent.json";p.write_text(json.dumps(self.obj));p.chmod(0o444);pin=self.m.rec(p)
   with patch.object(self.m,"ANNOTATION_PARENT",pin):
    c=self.m.HistoricalRecoveryAnnotations();c.parent_readback()
    p.chmod(0o644);p.write_bytes(b"changed");p.chmod(0o444)
    with self.assertRaisesRegex(ValueError,"bytes differ"):c.parent_readback()
 def test_actual_parent_symlink_or_writable_is_rejected(self):
  from unittest.mock import patch
  parent=self.m.R/"steps/24_benchmark_delivery/tmp";parent.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(dir=parent,prefix="annotation-boundary-contract-")as d:
   p=Path(d)/"synthetic-parent.json";p.write_text(json.dumps(self.obj));p.chmod(0o444);pin=self.m.rec(p)
   link=Path(d)/"parent-link.json";link.symlink_to(p)
   with patch.object(self.m,"ANNOTATION_PARENT",pin):
    c=self.m.HistoricalRecoveryAnnotations()
    with self.assertRaisesRegex(ValueError,"readonly"):c.parent_readback({**pin,"path":str(link)})
    p.chmod(0o644)
    with self.assertRaisesRegex(ValueError,"readonly"):c.parent_readback()

class RecoveredFiveActualBytes(unittest.TestCase):
 def setUp(self):
  import source_delivery_refresh_v8 as m
  from unittest.mock import patch
  self.m=m;parent=m.R/"steps/24_benchmark_delivery/tmp";parent.mkdir(parents=True,exist_ok=True)
  self.temp=tempfile.TemporaryDirectory(dir=parent,prefix="recovered-five-software-fixture-");self.dir=Path(self.temp.name);rows=[]
  for i in range(5):
   p=self.dir/("synthetic"+str(i)+".json");p.write_text(json.dumps({"synthetic_only":i}));p.chmod(0o444);r=m.rec(p);rows.append((p.name,r["bytes"],r["sha256"]))
  self.obj=dict(schema_version=1,session_id=m.RECOVERED_SESSION,recovery_type=m.RECOVERED_TYPE,files=[dict(path=n,bytes=b,sha256=s)for n,b,s in rows])
  self.path=self.dir/"synthetic-parent.json";self.path.write_text(json.dumps(self.obj));self.path.chmod(0o444);self.pin=m.rec(self.path)
  self.patches=[patch.object(m,"RECOVERED_PARENT",self.pin),patch.object(m,"RECOVERED_FILES",tuple(rows))]
  for p in self.patches:p.start()
  self.ctx=m.RecoveredFiveCurrentContext();self.parent={"logical":self.pin,"physical":self.pin}
 def tearDown(self):
  for p in self.patches:p.stop()
  for p in self.dir.iterdir():
   if p.is_file()and not p.is_symlink():p.chmod(0o644)
  self.temp.cleanup()
 def norm(self,i=0,trail=None,r=None,parent=None):
  t,relative,_=self.m.recovered_pins()[i]
  return self.ctx.normalize(r or relative,parent or self.parent,t if trail is None else trail)
 def test_current_all_five_real_bytes_and_all_observed(self):
  for i in range(5):self.norm(i)
  result=self.ctx.mapping([]);self.assertEqual(result["current_recovered_evidence_file_n"],5)
  self.assertTrue(all(x["raw_byte_acceptance"]and not x["new_scientific_inference"]for x in result["entries"]))
 def test_other_unvisited_child_missing_is_fatal(self):
  Path(self.m.recovered_pins()[4][2]["path"]).unlink()
  with self.assertRaisesRegex(ValueError,"unavailable"):self.norm(0)
 def test_other_child_drift_is_fatal(self):
  p=Path(self.m.recovered_pins()[4][2]["path"]);p.chmod(0o644);p.write_text("drift");p.chmod(0o444)
  with self.assertRaisesRegex(ValueError,"bytes differ"):self.norm(0)
 def test_child_symlink_is_fatal(self):
  p=Path(self.m.recovered_pins()[4][2]["path"]);p.unlink();p.symlink_to(Path(self.m.recovered_pins()[0][2]["path"]))
  with self.assertRaisesRegex(ValueError,"unavailable"):self.norm(0)
 def test_child_writable_is_fatal(self):
  Path(self.m.recovered_pins()[4][2]["path"]).chmod(0o644)
  with self.assertRaisesRegex(ValueError,"unavailable"):self.norm(0)
 def test_wrong_parent_sha_is_fatal(self):
  parent={"logical":{**self.pin,"sha256":"f"*64},"physical":self.pin}
  with self.assertRaisesRegex(ValueError,"logical parent"):self.norm(parent=parent)
 def test_wrong_field_before_repeated_seen_is_fatal(self):
  self.norm()
  with self.assertRaisesRegex(ValueError,"Unknown recovered"):self.norm(trail=("files","01"))
 def test_relative_child_exact_hash_required(self):
  r={**self.m.recovered_pins()[0][1],"sha256":"f"*64}
  with self.assertRaisesRegex(ValueError,"relative exact"):self.norm(r=r)
 def test_unknown_relative_parent_remains_old_strict_guard(self):
  r=self.m.recovered_pins()[0][1];parent={"logical":{**self.pin,"path":str(self.dir/"unknown.json")},"physical":self.pin}
  normalized,context=self.ctx.normalize(r,parent,("files","0"));self.assertIsNone(context)
  with self.assertRaisesRegex(ValueError,"Unknown relative"):self.m.ExactRelativeContext().normalize(normalized,parent["logical"]["path"],("files","0"))
 def test_parent_marker_drift_rejected(self):
  # Reader fixture tests the explicit marker independently of actual immutable parent hash.
  obj={**self.obj,"recovery_type":"new_scientific_inference"}
  ctx=self.m.RecoveredFiveCurrentContext(reader=lambda p:obj)
  with self.assertRaisesRegex(ValueError,"marker"):ctx.normalize(self.m.recovered_pins()[0][1],self.parent,("files","0"))
 def test_four_observed_cannot_close_mapping(self):
  for i in range(4):self.norm(i)
  with self.assertRaisesRegex(ValueError,"All five"):self.ctx.mapping([])
 def test_map_proof_emits_only_canonical_absolute_receipts(self):
  for i in range(5):self.norm(i)
  result=self.ctx.mapping([])
  for r,_ in self.m.receipt_edges(result):self.assertTrue(Path(r["path"]).is_absolute()and Path(r["path"]).is_relative_to(self.m.R))
  self.assertFalse(result["old_structures_backbones_or_MD_restored"]);self.assertTrue(result["original_json_unchanged"])


class HistoricalArchiveNamespaceContracts(unittest.TestCase):
 def setUp(self):
  import importlib.util,io,tarfile
  self.io=io;self.tarfile=tarfile;self.tmp=tempfile.TemporaryDirectory();self.dir=Path(self.tmp.name)
  spec=importlib.util.spec_from_file_location("synthetic_archive_namespace_"+self.dir.name,Path(__file__).with_name("historical_archive_member_context.py"))
  self.h=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.h);self.h.R=self.dir;self.h.EXPECTED_MEMBERS=5
  self.originals=[{"old/one.json":b"NOT_PARSED_JSON","old/two.bin":b"historical"}, {"base/a.txt":b"A","base/b.npz":b"B","base/c.pdb":b"C"}]
  self.pins=[]
  for i,files in enumerate(self.originals):
   archive=self.dir/(str(i)+".tar.gz");self.write_tar(archive,list(files.items()))
   rows=[dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())for n,b in files.items()]
   ar=self.h.rec(archive);obj=dict(archive=ar["path"],archive_bytes=ar["bytes"],archive_sha256=ar["sha256"],member_count=len(rows),members=rows,scope="SYNTHETIC_OLD_ARCHIVE_NOT_SCIENCE")
   parent=self.dir/(str(i)+".members.json");parent.write_text(json.dumps(obj));parent.chmod(0o444)
   self.pins.append(dict(parent_manifest=self.h.rec(parent),archive_receipt=ar,member_count=len(rows)))
  self.h.PINS=copy.deepcopy(self.pins)
 def tearDown(self):self.tmp.cleanup()
 def write_tar(self,path,items,kind=None):
  if path.exists():path.chmod(0o644)
  with self.tarfile.open(path,"w:gz")as t:
   for name,data in items:
    inf=self.tarfile.TarInfo(name);inf.size=len(data)
    if kind in {"symlink","hardlink","special","directory"}:
     inf.type={"symlink":self.tarfile.SYMTYPE,"hardlink":self.tarfile.LNKTYPE,"special":self.tarfile.CHRTYPE,"directory":self.tarfile.DIRTYPE}[kind];inf.linkname="target";inf.size=0;t.addfile(inf)
    else:t.addfile(inf,self.io.BytesIO(data))
  path.chmod(0o444)
 def ctx(self):return self.h.ExactHistoricalArchiveMembers(guard=lambda:dict(SYNTHETIC_SOFTWARE_ONLY=True))
 def norm(self,ctx=None,i=0,j=0,trail=None,r=None,parent=None):
  ctx=ctx or self.ctx();pin=self.h.PINS[i];raw=json.loads(Path(pin["parent_manifest"]["path"]).read_text())["members"][j]
  return ctx.normalize(r or raw,parent or dict(logical=pin["parent_manifest"],physical=pin["parent_manifest"]),trail or ("members",str(j)))
 def reindex_tar(self,i,items,kind=None):
  self.write_tar(Path(self.h.PINS[i]["archive_receipt"]["path"]),items,kind);ar=self.h.rec(self.h.PINS[i]["archive_receipt"]["path"]);pin=self.h.PINS[i];pin["archive_receipt"]=ar
  p=Path(pin["parent_manifest"]["path"]);obj=json.loads(p.read_text());obj.update(archive_bytes=ar["bytes"],archive_sha256=ar["sha256"]);p.chmod(0o644);p.write_text(json.dumps(obj));p.chmod(0o444);pin["parent_manifest"]=self.h.rec(p)
 def verification_receipt(self,ctx):
  p=self.dir/"verification.json";p.write_text(json.dumps(ctx.verification()));p.chmod(0o444);return self.h.rec(p)
 def test_archive_all_bytes_streamed_without_JSON_parse_or_extraction(self):
  before=set(self.dir.iterdir());ctx=self.ctx();proof=ctx.verification()
  self.assertEqual(sum(x["member_count"]for x in proof["archives"]),5);self.assertEqual(set(self.dir.iterdir()),before)
  self.assertFalse(proof["archive_extracted"]);self.assertFalse(proof["archived_JSON_payload_parsed"]);self.assertFalse(proof["new_scientific_inference"])
 def test_archive_scalar_edge_never_claims_current_path(self):
  r,row=self.norm();self.assertIsNone(r);self.assertIsNone(row["canonical_receipt"]);self.assertFalse(row["current_execution_allowed"]);self.assertFalse(row["current_file_restored"]);self.assertTrue(row["raw_member_bytes_verified_in_archive"])
 def test_archive_partial_observation_cannot_close(self):
  ctx=self.ctx();self.norm(ctx);vr=self.verification_receipt(ctx)
  with self.assertRaisesRegex(ValueError,"All finite"):ctx.mapping(vr,[])
 def test_archive_whole_observation_closes_only_scalar_member_proofs(self):
  ctx=self.ctx()
  for i,p in enumerate(self.h.PINS):
   for j in range(p["member_count"]):self.norm(ctx,i,j)
  result=ctx.mapping(self.verification_receipt(ctx),[])
  self.assertEqual(len(result["archives"]),2);self.assertEqual(result["archive_member_n"],5)
  import source_delivery_refresh_v8 as current
  for r,_ in current.receipt_edges(result):self.assertTrue(Path(r["path"]).is_absolute())
 def test_archive_unknown_parent_passes_to_existing_strict_guard(self):
  ctx=self.ctx();parent=dict(logical={**self.pins[0]["parent_manifest"],"path":str(self.dir/"unknown.json")},physical=self.pins[0]["parent_manifest"])
  r,row=self.norm(ctx,parent=parent);self.assertIsNone(row)
  from relative_receipt_policy import ExactRelativeContext
  with self.assertRaisesRegex(ValueError,"Unknown relative"):ExactRelativeContext().normalize(r,parent["logical"]["path"],("members","0"))
 def test_archive_wrong_parent_sha_cannot_authorize(self):
  parent=dict(logical={**self.pins[0]["parent_manifest"],"sha256":"0"*64},physical=self.pins[0]["parent_manifest"]);r,row=self.norm(parent=parent)
  self.assertIsNone(row);self.assertFalse(Path(r["path"]).is_absolute())
 def test_archive_wrong_field_rejected_before_repeat_dedup(self):
  ctx=self.ctx();self.norm(ctx)
  with self.assertRaisesRegex(ValueError,"field"):self.norm(ctx,trail=("outputs","0"))
 def test_archive_changed_member_sha_rejected(self):
  raw=json.loads(Path(self.pins[0]["parent_manifest"]["path"]).read_text())["members"][0]
  with self.assertRaisesRegex(ValueError,"identity"):self.norm(r={**raw,"sha256":"0"*64})
 def test_archive_changed_member_bytes_rejected(self):
  raw=json.loads(Path(self.pins[0]["parent_manifest"]["path"]).read_text())["members"][0]
  with self.assertRaisesRegex(ValueError,"identity"):self.norm(r={**raw,"bytes":raw["bytes"]+1})
 def test_archive_zero_padded_field_rejected(self):
  with self.assertRaisesRegex(ValueError,"field"):self.norm(trail=("members","00"))
 def test_archive_boolean_member_bytes_rejected(self):
  raw=json.loads(Path(self.pins[0]["parent_manifest"]["path"]).read_text())["members"][0]
  with self.assertRaises(ValueError):self.norm(r={**raw,"bytes":True})
 def test_archive_absolute_current_receipt_unchanged(self):
  r=dict(path=str(self.dir/"current.json"),bytes=1,sha256="a"*64);a,row=self.ctx().normalize(r,None,())
  self.assertIs(a,r);self.assertIsNone(row)
 def test_archive_index_writable_rejected(self):
  Path(self.pins[0]["parent_manifest"]["path"]).chmod(0o644)
  with self.assertRaisesRegex(ValueError,"Readonly"):self.ctx()
 def test_archive_tar_writable_rejected(self):
  Path(self.pins[0]["archive_receipt"]["path"]).chmod(0o644)
  with self.assertRaisesRegex(ValueError,"Readonly"):self.ctx()
 def test_archive_index_symlink_rejected(self):
  p=Path(self.pins[0]["parent_manifest"]["path"]);q=self.dir/"parentcopy";p.rename(q);p.symlink_to(q)
  with self.assertRaisesRegex(ValueError,"nonsymlink"):self.ctx()
 def test_archive_tar_symlink_rejected(self):
  p=Path(self.pins[0]["archive_receipt"]["path"]);q=self.dir/"archivecopy";p.rename(q);p.symlink_to(q)
  with self.assertRaisesRegex(ValueError,"nonsymlink"):self.ctx()
 def test_archive_index_byte_drift_rejected(self):
  p=Path(self.pins[0]["parent_manifest"]["path"]);p.chmod(0o644);p.write_text("{}");p.chmod(0o444)
  with self.assertRaisesRegex(ValueError,"bytes differ"):self.ctx()
 def test_archive_outer_digest_drift_rejected(self):
  p=Path(self.pins[0]["archive_receipt"]["path"]);p.chmod(0o644);p.write_bytes(b"drift");p.chmod(0o444)
  with self.assertRaisesRegex(ValueError,"bytes differ"):self.ctx()
 def test_archive_member_digest_drift_rejected_even_when_outer_rebound(self):
  self.reindex_tar(0,[("old/one.json",b"CHANGED_______"),("old/two.bin",b"historical")])
  with self.assertRaisesRegex(ValueError,"member byte"):self.ctx()
 def test_archive_missing_regular_member_rejected(self):
  self.reindex_tar(0,[("old/one.json",b"NOT_PARSED_JSON")])
  with self.assertRaisesRegex(ValueError,"Missing"):self.ctx()
 def test_archive_extra_regular_member_rejected(self):
  self.reindex_tar(0,[*self.originals[0].items(),("unknown.txt",b"X")])
  with self.assertRaisesRegex(ValueError,"Unexpected"):self.ctx()
 def test_archive_duplicate_regular_member_rejected(self):
  self.reindex_tar(0,[*self.originals[0].items(),("old/one.json",b"NOT_PARSED_JSON")])
  with self.assertRaisesRegex(ValueError,"duplicate"):self.ctx()
 def test_archive_symbolic_member_rejected(self):
  for kind in ("symlink","hardlink","special"):
   self.reindex_tar(0,[("old/one.json",b"")],kind=kind)
   with self.subTest(kind=kind),self.assertRaisesRegex(ValueError,"special member"):self.ctx()
  for items in ([("extra",b"")],[("old",b""),("old",b"")],[("old/one.json",b"")]):
   self.reindex_tar(0,items,kind="directory")
   with self.subTest(items=items),self.assertRaisesRegex(ValueError,"directory"):self.ctx()
 def test_archive_unsafe_member_namespace_rejected(self):
  p=Path(self.h.PINS[0]["parent_manifest"]["path"]);obj=json.loads(p.read_text());obj["members"][0]["path"]="../escape.json";p.chmod(0o644);p.write_text(json.dumps(obj));p.chmod(0o444);self.h.PINS[0]["parent_manifest"]=self.h.rec(p)
  with self.assertRaisesRegex(ValueError,"Unsafe"):self.ctx()
 def test_archive_operative_source_member_not_in_authorized_scope(self):
  p=Path(self.h.PINS[0]["parent_manifest"]["path"]);obj=json.loads(p.read_text());obj["members"][0]["path"]="new.py";p.chmod(0o644);p.write_text(json.dumps(obj));p.chmod(0o444);self.h.PINS[0]["parent_manifest"]=self.h.rec(p)
  with self.assertRaisesRegex(ValueError,"operative source"):self.ctx()
 def test_archive_drift_after_tar_verification_blocks_proof(self):
  ctx=self.ctx();p=Path(self.h.PINS[0]["archive_receipt"]["path"]);p.chmod(0o644);p.write_bytes(b"later");p.chmod(0o444)
  with self.assertRaisesRegex(ValueError,"bytes differ"):ctx.verification()

if __name__=="__main__":unittest.main()
