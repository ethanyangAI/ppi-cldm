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
  source=(Path(__file__).parent/"source_delivery_refresh_v10.py").read_text()
  a=source.index("r,relative_context=context.normalize(r,parent,trail)")
  self.assertLess(a,source.index("if k in seen:continue"));self.assertLess(a,source.index("if suffix not in TEXT_EXT:"));self.assertLess(source.index("annotation=annotation_or_external_failure(r,parent_context,trail,historical_annotations)"),source.index("if k in seen:continue"))
 def software_fixture(self):
  from source_delivery_refresh_v10 import SOFTWARE_PACKAGE_NAMES
  parent=R/"steps/24_benchmark_delivery/tmp";parent.mkdir(parents=True,exist_ok=True)
  t=tempfile.TemporaryDirectory(dir=parent,prefix="source-whole-binding-contract-");here=Path(t.name);rows=[]
  for name in SOFTWARE_PACKAGE_NAMES:
   p=here/name;p.write_bytes(b"fixture");p.chmod(0o444)
   rows.append({"path":str(p),"bytes":7,"sha256":hashlib.sha256(b"fixture").hexdigest()})
  return t,here,{"source_receipts":rows}
 def test_software_binding_helper_drift_rejected(self):
  from source_delivery_refresh_v10 import software_source_binding
  t,here,snapshot=self.software_fixture()
  try:
   software_source_binding(snapshot,here)
   p=here/"relative_receipt_policy.py";p.chmod(0o644);p.write_bytes(b"changed");p.chmod(0o444)
   with self.assertRaisesRegex(ValueError,"drift"):software_source_binding(snapshot,here)
  finally:t.cleanup()
 def test_software_binding_dependency_drift_rejected(self):
  from source_delivery_refresh_v10 import software_source_binding
  t,here,snapshot=self.software_fixture()
  try:
   p=here/"delivery_core.py";p.chmod(0o644);p.write_bytes(b"changed");p.chmod(0o444)
   with self.assertRaisesRegex(ValueError,"drift"):software_source_binding(snapshot,here)
  finally:t.cleanup()
 def test_software_binding_thin_snapshot_rejected(self):
  from source_delivery_refresh_v10 import software_source_binding
  t,here,snapshot=self.software_fixture()
  try:
   snapshot["source_receipts"].pop()
   with self.assertRaisesRegex(ValueError,"whole tested"):software_source_binding(snapshot,here)
  finally:t.cleanup()
 def test_actual_software_contract_counts_pass(self):
  from source_delivery_refresh_v10 import software_contract_counts
  self.assertEqual(software_contract_counts({"status":"PASS","tests":122,"failures":0,"errors":0})["tests"],122)
 def test_actual_software_fewer_contracts_rejected(self):
  from source_delivery_refresh_v10 import software_contract_counts
  with self.assertRaisesRegex(ValueError,"saved122"):software_contract_counts({"status":"PASS","tests":25,"failures":0,"errors":0})
 def test_actual_software_failure_count_rejected(self):
  from source_delivery_refresh_v10 import software_contract_counts
  with self.assertRaisesRegex(ValueError,"saved122"):software_contract_counts({"status":"PASS","tests":122,"failures":1,"errors":0})
 def test_actual_software_error_count_rejected(self):
  from source_delivery_refresh_v10 import software_contract_counts
  with self.assertRaisesRegex(ValueError,"saved122"):software_contract_counts({"status":"PASS","tests":122,"failures":0,"errors":1})

class AnnotationContracts(unittest.TestCase):
 """Finite literal-history fixtures; no missing historical file is created or opened."""
 def setUp(self):
  import source_delivery_refresh_v10 as m
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
  import source_delivery_refresh_v10 as m
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
  import source_delivery_refresh_v10 as current
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


class MetadataSchemaTypeContracts(unittest.TestCase):
 def source(self):
  import source_delivery_refresh_v10 as m
  return m
 def r(self,path=None):
  m=self.source();return dict(path=path or str(m.R/"unknown_current.py"),bytes=1,sha256="f"*64)
 def test_metadata_known_exact_string_markers_only(self):
  m=self.source()
  for marker in ("exact-resource-aliases.v2","native-resource-closure.v2"):
   obj=dict(schema=marker,nested=[self.r()]);self.assertTrue(m.recognized_metadata_schema(obj));self.assertEqual(list(m.operative_receipt_edges(obj)),[])
 def test_metadata_unknown_string_is_full_operative_walk(self):
  m=self.source();child=self.r();obj=dict(schema="ordinary-config-schema",nested=[child])
  self.assertFalse(m.recognized_metadata_schema(obj));self.assertEqual(list(m.operative_receipt_edges(obj)),[(child,("nested","0"))])
 def test_metadata_dict_schema_is_operative_and_schema_edges_propagate(self):
  m=self.source();inside=self.r("relative_inside_schema.py");child=self.r()
  obj=dict(schema=dict(source=inside),nested=[child])
  self.assertFalse(m.recognized_metadata_schema(obj));self.assertEqual(list(m.operative_receipt_edges(obj)),[(inside,("schema","source")),(child,("nested","0"))])
 def test_metadata_list_schema_is_operative_and_schema_edges_propagate(self):
  m=self.source();inside=self.r("relative_inside_schema.py");child=self.r()
  obj=dict(schema=[inside],nested=[child])
  self.assertFalse(m.recognized_metadata_schema(obj));self.assertEqual(list(m.operative_receipt_edges(obj)),[(inside,("schema","0")),(child,("nested","0"))])
 def test_metadata_null_schema_remains_full_operative_walk(self):
  m=self.source();child=self.r();obj=dict(schema=None,nested=[child])
  self.assertFalse(m.recognized_metadata_schema(obj));self.assertEqual(list(m.operative_receipt_edges(obj)),[(child,("nested","0"))])
 def test_metadata_missing_boolean_numeric_schema_not_special(self):
  m=self.source();child=self.r()
  for values in ({},{"schema":True},{"schema":0},{"schema":1.2}):
   with self.subTest(values=values):
    obj={**values,"nested":[child]};self.assertFalse(m.recognized_metadata_schema(obj));self.assertEqual(list(m.operative_receipt_edges(obj)),[(child,("nested","0"))])
 def test_metadata_top_level_list_and_scalar_walk_without_type_assumption(self):
  m=self.source();child=self.r()
  self.assertEqual(list(m.operative_receipt_edges([child])),[(child,("0",))])
  for obj in (None,False,0,"ordinary"):
   with self.subTest(obj=obj):self.assertFalse(m.recognized_metadata_schema(obj));self.assertEqual(list(m.operative_receipt_edges(obj)),[])
 def test_metadata_unusual_schema_cannot_hide_unknown_relative_or_external_edge(self):
  m=self.source()
  for schema in ({},[],None,"ordinary"):
   for path in ("unknown_relative.py","/unapproved/current.py"):
    obj=dict(schema=schema,nested=[self.r(path)])
    edges=list(m.operative_receipt_edges(obj));self.assertEqual(len(edges),1)
    child,trail=edges[0];self.assertEqual(trail,("nested","0"))
    with self.subTest(schema=schema,path=path):
     if Path(path).is_absolute():
      with self.assertRaisesRegex(ValueError,"Current operative external"):
       m.annotation_or_external_failure(child,None,trail,m.HistoricalRecoveryAnnotations())
     else:
      with self.assertRaisesRegex(ValueError,"Unknown relative"):
       m.ExactRelativeContext().normalize(child,str(m.R/"ordinary_schema.json"),trail)



"""Sixteen prepared software-only contracts. Run only after actual pureCPU Slurm guard."""
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
import source_delivery_refresh_v10 as m
class FiniteAliasContracts(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.addCleanup(self.temp.cleanup)
  self.rows=[]
  for i in range(8):
   p=self.root/("saved_"+str(i)+".py");p.write_bytes(("VALUE="+str(i)+"\n").encode());p.chmod(0o444)
   r=self.receipt(p);original={**r,"path":str(self.root/("old_"+str(i)+".py"))}
   self.rows.append(dict(original=original,canonical=r,basis="EXISTING_READONLY_RUNTIME_SNAPSHOT"))
  parent=self.root/"parent.json";obj={("e"+str(i)):self.rows[i%8]["original"]for i in range(12)}
  parent.write_text(json.dumps(obj));parent.chmod(0o444);self.parent=self.receipt(parent)
  self.edges=[dict(source_parent=self.parent,parent_canonical_receipt=self.parent,source_field=["e"+str(i)],original=self.rows[i%8]["original"])for i in range(12)]
  self.declared=dict(aliases=copy.deepcopy(self.rows),edges=copy.deepcopy(self.edges))
 def receipt(self,p):
  data=p.read_bytes();return dict(path=str(p),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 def verify(self,path,r):
  p=Path(path)
  if p.is_symlink()or p.resolve()!=p or not p.is_file()or p.stat().st_mode&0o222 or self.receipt(p)!=r:raise ValueError("Readonly exact source drift")
  return p
 def proof(self,row):
  return dict(classification=row["basis"],canonical_receipt=row["canonical"],current_execution_authorized=False)
 def policy(self,rows=None,edges=None,provenance=None):
  return m.FiniteOperativeSourceAliases(rows or self.rows,edges or self.edges,self.verify,lambda p:json.loads(Path(p).read_text()),provenance or self.proof,self.declared)
 def context(self):return dict(logical=self.parent,physical=self.parent)
 def observe(self,p):
  for e in self.edges:p.authorize(e["original"],self.context(),e["source_field"])
 def test_real_exact_eight_twelve_closure(self):
  p=self.policy();self.observe(p);v=p.require_complete();self.assertEqual(v["source_identity_n"],8);self.assertEqual(v["original_edge_n"],12);self.assertFalse(v["current_execution_authorized"])
 def test_pending_bbf_blocks_before_partial_alias(self):
  rows=copy.deepcopy(self.rows);rows[1]["canonical"]=None
  with self.assertRaisesRegex(ValueError,"unresolved"):self.policy(rows)
 def test_unknown_ninth_source_rejected(self):
  rows=copy.deepcopy(self.rows);rows.append(copy.deepcopy(rows[0]))
  with self.assertRaisesRegex(ValueError,"eight"):self.policy(rows)
 def test_duplicate_source_identity_rejected(self):
  rows=copy.deepcopy(self.rows);rows[1]=copy.deepcopy(rows[0])
  with self.assertRaisesRegex(ValueError,"duplicate"):self.policy(rows)
 def test_unknown_source_not_given_alias(self):
  p=self.policy();r={**self.rows[0]["original"],"path":str(self.root/"unknown.py")}
  self.assertIsNone(p.authorize(r,self.context(),["e0"]))
 def test_wrong_parent_identity_denied_before_dedup(self):
  p=self.policy();p.authorize(self.rows[0]["original"],self.context(),["e0"])
  context=self.context();context["logical"]={**self.parent,"sha256":"f"*64}
  with self.assertRaisesRegex(ValueError,"Unknown parent"):p.authorize(self.rows[0]["original"],context,["e0"])
 def test_wrong_field_denied_after_seen_source(self):
  p=self.policy();p.authorize(self.rows[0]["original"],self.context(),["e0"])
  with self.assertRaisesRegex(ValueError,"Unknown parent"):p.authorize(self.rows[0]["original"],self.context(),["e1"])
 def test_changed_canonical_parent_denied(self):
  p=self.policy();context=self.context();context["physical"]={**self.parent,"path":str(self.root/"alias_parent.json")}
  with self.assertRaisesRegex(ValueError,"canonical identity"):p.authorize(self.rows[0]["original"],context,["e0"])
 def test_source_byte_drift_denied(self):
  p=Path(self.rows[0]["canonical"]["path"]);p.chmod(0o644);p.write_bytes(b"DIFFERENT");p.chmod(0o444)
  with self.assertRaisesRegex(ValueError,"drift"):self.policy()
 def test_writable_source_denied(self):
  Path(self.rows[0]["canonical"]["path"]).chmod(0o644)
  with self.assertRaisesRegex(ValueError,"drift"):self.policy()
 def test_selected_physical_path_fork_denied(self):
  rows=copy.deepcopy(self.rows);rows[0]["canonical"]["path"]=str(self.root/"another.py")
  with self.assertRaisesRegex(ValueError,"Selected literal"):self.policy(rows)
 def test_all_edges_observed_required(self):
  p=self.policy();p.authorize(self.rows[0]["original"],self.context(),["e0"])
  with self.assertRaisesRegex(ValueError,"All twelve"):p.require_complete()
  self.observe(p);parent=Path(self.parent["path"]);parent.chmod(0o644);parent.write_text("{}");parent.chmod(0o444)
  with self.assertRaisesRegex(ValueError,"drift"):p.require_complete()
 def test_permission_table_fork_denied(self):
  edges=copy.deepcopy(self.edges);edges[0]["source_field"]=["different"]
  with self.assertRaisesRegex(ValueError,"twelve"):self.policy(edges=edges)
 def test_source_provenance_false_or_execution_authority_denied(self):
  for value in ({},dict(classification=self.rows[0]["basis"],canonical_receipt=self.rows[0]["canonical"],current_execution_authorized=True)):
   with self.subTest(value=value):
    with self.assertRaisesRegex(ValueError,"provenance"):self.policy(provenance=lambda row:value)
 def test_recorded_chain_inverse_forward_and_no_execution(self):
  tuples=[["OLD%02d"%i,"NEW%02d"%i]for i in range(12)]
  script=("s=common.read_text()\n"+"".join("s=s.replace(%r,%r)\n"%(old,new)for old,new in tuples)+"common.write_text(s)\n").encode()
  proof=m.independent_recorded_replay("|".join(new for old,new in tuples).encode(),"|".join(old for old,new in tuples).encode(),script,tuples)
  self.assertTrue(proof["forward_equals_frozen_bytes"]);self.assertFalse(proof["freezer_executed"]);self.assertFalse(proof["reconstructed_source_executed"])
 def test_recorded_replay_wrong_anchors_nonliteral_duplicate_and_bytes_denied(self):
  cases=[(b"x=x.replace('A','B')\n",b"C",b"A",[["A","B"]]),(b"x=x.replace(a,b)\n",b"B",b"A",[["A","B"]]),(b"x=x.replace('A','B')\ny=y.replace('A','B')\n",b"B",b"A",[["A","B"]]),(b"x=x.replace('A','B')\n",b"B",b"AA",[["A","B"]])]
  for script,frozen,original,tuples in cases:
   with self.subTest(script=script):
    with self.assertRaises(ValueError):m.independent_recorded_replay(frozen,original,script,tuples)


class SourceRecoveryProofContracts(unittest.TestCase):
 """Independent software fixtures: source bytes, literal grammar, saved proof boundaries."""
 def common(self):
  pairs=[["OLD%02d"%i,"NEW%02d"%i]for i in range(12)]
  source="s=common.read_text()\n"+"".join("s=s.replace(%r,%r)\n"%tuple(p)for p in pairs)+"common.write_text(s)\n"
  return pairs,source
 def terminal(self,state="COMPLETED",exit_code="0:0",tres="cpu=1,node=1,billing=1"):
  return dict(job_id="13308",expected_job_name="test9_missing_source_diagnostic_v1",expected_state=state,expected_exit_code=exit_code,raw_sacct="13308|u21111210118|u21111210118|organ|test9_missing_source_diagnostic_v1|"+state+"|"+exit_code+"|1|"+tres+"\n")
 def test_common_only_authoritative_twelve_block(self):
  pairs,source=self.common()
  self.assertEqual(m.recorded_literal_replacements(("unused.replace('X','Y')\n"+source).encode(),pairs),pairs)
 def test_common_block_malformed_or_duplicate_read_rejected(self):
  pairs,source=self.common()
  cases=[source.replace("s=s.replace('OLD00','NEW00')","s=s.replace(old,new)"),source.replace("common.write_text(s)","other.write_text(s)"),"s=common.read_text()\n"+source,source.replace("s=s.replace('OLD11','NEW11')\n","")]
  for value in cases:
   with self.subTest(value=value):
    with self.assertRaises(ValueError):m.recorded_literal_replacements(value.encode(),pairs)
 def test_common_expected_pair_fork_rejected(self):
  pairs,source=self.common();pairs[7][1]="DIFFERENT"
  with self.assertRaises(ValueError):m.recorded_literal_replacements(source.encode(),pairs)
 def test_actual_two_JS_records_parse_twelve_literal_pairs(self):
  data=json.loads("{\"schema\":\"exact-two-historical-BBF-patch-records-data-only.v1\",\"original_session_id\":\"01a12917-8539-7e20-89ae-37dd9dcc35c1\",\"original_local_session_file\":\"/Users/yangzijian/.codex/sessions/2026/10/11/rollout-2026-10-11T11-52-49-01a12917-8539-7e20-89ae-37dd9dcc35c1.jsonl\",\"records\":[{\"record_line\":1381,\"raw_JSONL_record\":\"{\\\"timestamp\\\":\\\"2026-10-11T05:06:04.414Z\\\",\\\"ordinal\\\":1380,\\\"type\\\":\\\"response_item\\\",\\\"payload\\\":{\\\"type\\\":\\\"custom_tool_call\\\",\\\"id\\\":\\\"ctc_00918a3c2e5efc41016acb192eb7048191a4013912e378d57f\\\",\\\"status\\\":\\\"completed\\\",\\\"call_id\\\":\\\"call_1507b4e1755942269e8cf5d83799737f\\\",\\\"name\\\":\\\"exec\\\",\\\"input\\\":\\\"let c=load(\\\\\\\"bbf_diagnostic_code_v2\\\\\\\");\\\\nc=c.replace('msa=np.asarray(data[f[\\\\\\\"msa_feature_key\\\\\\\"]])','msa=np.asarray(data[f.get(\\\\\\\"msa_feature_key\\\\\\\",f.get(\\\\\\\"msa_feat_key\\\\\\\"))])');\\\\nc=c.replace('    mapping={int(k)-1:int(v)-1 for k,v in job[\\\\\\\"target_query_to_template_indices\\\\\\\"].items()}','    prev=np.asarray(data[f.get(\\\\\\\"initial_prev_pos_key\\\\\\\",\\\\\\\"prev_pos\\\\\\\")],float)\\\\\\\\n    if prev.shape!=(L,37,3) or not np.isfinite(prev).all() or prev.any():raise ValueError(\\\\\\\"Initial previous-position guess leaked\\\\\\\")\\\\\\\\n    cbmask=np.asarray(data[\\\\\\\"template_pseudo_beta_mask\\\\\\\"],float);cbpos=np.asarray(data[\\\\\\\"template_pseudo_beta\\\\\\\"],float)\\\\\\\\n    if cbmask.shape!=(1,L) or cbpos.shape!=(1,L,3) or not np.isfinite(cbmask).all() or not np.isfinite(cbpos).all():raise ValueError(\\\\\\\"Pseudo-beta template features malformed\\\\\\\")\\\\\\\\n    rawmask=np.asarray(data[\\\\\\\"batch_all_atom_mask\\\\\\\"],float);rawpos=np.asarray(data[\\\\\\\"batch_all_atom_positions\\\\\\\"],float)\\\\\\\\n    if rawmask.shape!=(L,37) or rawpos.shape!=(L,37,3):raise ValueError(\\\\\\\"Raw target-only source batch shape\\\\\\\")\\\\\\\\n    mapping={int(k)-1:int(v)-1 for k,v in job[\\\\\\\"target_query_to_template_indices\\\\\\\"].items()}');\\\\nc=c.replace('    if mask[:,T:].any() or pos[:,T:].any():','    if rawmask[T:].any() or rawpos[T:].any() or cbmask[:,T:].any() or cbpos[:,T:].any():raise ValueError(\\\\\\\"Binder raw/template pseudo-beta leakage\\\\\\\")\\\\\\\\n    if absent and (rawmask[absent].any() or rawpos[absent].any() or cbmask[:,absent].any() or cbpos[:,absent].any()):raise ValueError(\\\\\\\"Missing target raw/pseudo-beta leakage\\\\\\\")\\\\\\\\n    if mask[:,T:].any() or pos[:,T:].any():');\\\\nc=c.replace('    if not job[\\\\\\\"target_template_enabled\\\\\\\"] and n!=0:','    if not job[\\\\\\\"target_template_enabled\\\\\\\"] and (cbmask.any() or cbpos.any()):raise ValueError(\\\\\\\"No-template pseudo-beta channel leaked\\\\\\\")\\\\\\\\n    if not job[\\\\\\\"target_template_enabled\\\\\\\"] and n!=0:');\\\\nc=c.replace('actual_query_length=L)','actual_query_length=L,initial_prev_pos_nonzero=0,all_models_features_verified=f.get(\\\\\\\"all_models_feature_arrays_identical\\\\\\\"))');\\\\nc=c.replace('        if worker.get(\\\\\\\"allocation\\\\\\\",{}).get(\\\\\\\"allocated_gpu_count\\\\\\\")!=1:raise ValueError(\\\\\\\"GPU worker actual scheduler allocation missing/not1\\\\\\\")','        allocation_receipt=worker.get(\\\\\\\"allocation\\\\\\\",{})\\\\\\\\n        if allocation_receipt.get(\\\\\\\"allocated_gpu_count\\\\\\\")!=1:raise ValueError(\\\\\\\"GPU worker actual scheduler allocation missing/not1\\\\\\\")');\\\\nc=c.replace('components(conf[\\\\\\\"iptm\\\\\\\"],float(pp[na:].mean()),ip,cp)','components(conf.get(\\\\\\\"iptm\\\\\\\",conf.get(\\\\\\\"globaliptm\\\\\\\")),float(pp[na:].mean()),ip,cp)');\\\\nc=c.replace('global_iptm=float(conf[\\\\\\\"iptm\\\\\\\"])','global_iptm=float(conf.get(\\\\\\\"iptm\\\\\\\",conf.get(\\\\\\\"globaliptm\\\\\\\")))');\\\\nc=c.replace('        np.savez(path,mask=mask,pos=pos,aatype=query,msa=np.zeros((1,L,49)))','        cbmask=np.zeros((1,L));cbpos=np.zeros((1,L,3))\\\\\\\\n        np.savez(path,mask=mask,pos=pos,aatype=query,msa=np.zeros((1,L,49)),prev_pos=np.zeros((L,37,3)),template_pseudo_beta_mask=cbmask,template_pseudo_beta=cbpos,batch_all_atom_mask=np.zeros((L,37)),batch_all_atom_positions=np.zeros((L,37,3)))');\\\\nc=c.replace('actual_query_length=L,initial_prev_pos_nonzero=0,all_models_features_verified=f.get(\\\\\\\"all_models_feature_arrays_identical\\\\\\\"))','actual_query_length=L,initial_prev_pos_nonzero=0)');\\\\nstore(\\\\\\\"bbf_diagnostic_code_v3\\\\\\\",c);store(\\\\\\\"bbf_diagnostic_code_v2\\\\\\\",c);\\\\nconst q=s=>\\\\\\\"'\\\\\\\"+s.replace(/'/g,\\\\\\\"'\\\\\\\\\\\\\\\\''\\\\\\\")+\\\\\\\"'\\\\\\\";\\\\ntext(await tools.exec_command({cmd:load(\\\\\\\"screen_ssh\\\\\\\")+\\\\\\\" \\\\\\\"+q(\\\\\\\"cat > /lustre/users/u21111210118/projects/test9/source/rebuild/bbf_input_diagnostic.py <<'PY'\\\\\\\\n\\\\\\\"+c+\\\\\\\"\\\\\\\\nPY\\\\\\\\nsbatch /lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/code/cpu.sbatch test --out /lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/inputs/test_v3.json\\\\\\\\nsacct -j 13036 --format=JobID,State,ExitCode,Elapsed -n\\\\\\\\ntail -n 40 /lustre/users/u21111210118/projects/test9/steps/23_common_review/logs/hardware_13036.log\\\\\\\"),max_output_tokens:2000}));\\\\n\\\",\\\"internal_chat_message_metadata_passthrough\\\":{\\\"turn_id\\\":\\\"01a12928-f105-7cd3-bed9-6c73e91f0804\\\",\\\"create_time\\\":1791695150.7349188}}}\"},{\"record_line\":1408,\"raw_JSONL_record\":\"{\\\"timestamp\\\":\\\"2026-10-11T05:07:12.719Z\\\",\\\"ordinal\\\":1407,\\\"type\\\":\\\"response_item\\\",\\\"payload\\\":{\\\"type\\\":\\\"custom_tool_call\\\",\\\"id\\\":\\\"ctc_00918a3c2e5efc41016acb197e379c81918ceebce2e037ab7f\\\",\\\"status\\\":\\\"completed\\\",\\\"call_id\\\":\\\"call_695893637f52466ba2c6f5638ac69a8b\\\",\\\"name\\\":\\\"exec\\\",\\\"input\\\":\\\"let c=load(\\\\\\\"bbf_diagnostic_code_v3\\\\\\\");\\\\nc=c.replace('    checked=[]\\\\\\\\n    for key,job','    verify(features[\\\\\\\"source\\\\\\\"])\\\\\\\\n    checked=[]\\\\\\\\n    for key,job');\\\\nc=c.replace('        f=actual[key];actual_stats=feature_arrays(job,f)','        f=actual[key];actual_stats=feature_arrays(job,f)\\\\\\\\n        if f[\\\\\\\"actual_validated_model_slots\\\\\\\"]!=job[\\\\\\\"slots\\\\\\\"] or not f[\\\\\\\"all_models_feature_arrays_identical\\\\\\\"]:raise ValueError(\\\\\\\"Every fixed model actual forward feature proof required\\\\\\\")');\\\\nstore(\\\\\\\"bbf_diagnostic_code_v3\\\\\\\",c);store(\\\\\\\"bbf_diagnostic_code_v2\\\\\\\",c);\\\\nconst q=s=>\\\\\\\"'\\\\\\\"+s.replace(/'/g,\\\\\\\"'\\\\\\\\\\\\\\\\''\\\\\\\")+\\\\\\\"'\\\\\\\";\\\\ntext(await tools.exec_command({cmd:load(\\\\\\\"screen_ssh\\\\\\\")+\\\\\\\" \\\\\\\"+q(\\\\\\\"cat > /lustre/users/u21111210118/projects/test9/source/rebuild/bbf_input_diagnostic.py <<'PY'\\\\\\\\n\\\\\\\"+c+\\\\\\\"\\\\\\\\nPY\\\\\\\"),max_output_tokens:300}));\\\\n\\\",\\\"internal_chat_message_metadata_passthrough\\\":{\\\"turn_id\\\":\\\"01a12928-f105-7cd3-bed9-6c73e91f0804\\\",\\\"create_time\\\":1791695230.221601}}}\"}],\"recorded_tool_calls_executed\":false,\"scope\":\"Only exact two original JSONL records copied as data; AST literal replace statements only, no history execution.\"}")
  pairs,proof=m.recorded_js_patches(m.BBF_REPLAY_PINS["records"],lambda r:json.dumps(data).encode())
  self.assertEqual(len(pairs),12);self.assertEqual(proof,m.BBF_REPLAY_PINS["record_proofs"])
 def test_JS_record_metadata_or_nonliteral_fork_rejected(self):
  data=json.loads("{\"schema\":\"exact-two-historical-BBF-patch-records-data-only.v1\",\"original_session_id\":\"01a12917-8539-7e20-89ae-37dd9dcc35c1\",\"original_local_session_file\":\"/Users/yangzijian/.codex/sessions/2026/10/11/rollout-2026-10-11T11-52-49-01a12917-8539-7e20-89ae-37dd9dcc35c1.jsonl\",\"records\":[{\"record_line\":1381,\"raw_JSONL_record\":\"{\\\"timestamp\\\":\\\"2026-10-11T05:06:04.414Z\\\",\\\"ordinal\\\":1380,\\\"type\\\":\\\"response_item\\\",\\\"payload\\\":{\\\"type\\\":\\\"custom_tool_call\\\",\\\"id\\\":\\\"ctc_00918a3c2e5efc41016acb192eb7048191a4013912e378d57f\\\",\\\"status\\\":\\\"completed\\\",\\\"call_id\\\":\\\"call_1507b4e1755942269e8cf5d83799737f\\\",\\\"name\\\":\\\"exec\\\",\\\"input\\\":\\\"let c=load(\\\\\\\"bbf_diagnostic_code_v2\\\\\\\");\\\\nc=c.replace('msa=np.asarray(data[f[\\\\\\\"msa_feature_key\\\\\\\"]])','msa=np.asarray(data[f.get(\\\\\\\"msa_feature_key\\\\\\\",f.get(\\\\\\\"msa_feat_key\\\\\\\"))])');\\\\nc=c.replace('    mapping={int(k)-1:int(v)-1 for k,v in job[\\\\\\\"target_query_to_template_indices\\\\\\\"].items()}','    prev=np.asarray(data[f.get(\\\\\\\"initial_prev_pos_key\\\\\\\",\\\\\\\"prev_pos\\\\\\\")],float)\\\\\\\\n    if prev.shape!=(L,37,3) or not np.isfinite(prev).all() or prev.any():raise ValueError(\\\\\\\"Initial previous-position guess leaked\\\\\\\")\\\\\\\\n    cbmask=np.asarray(data[\\\\\\\"template_pseudo_beta_mask\\\\\\\"],float);cbpos=np.asarray(data[\\\\\\\"template_pseudo_beta\\\\\\\"],float)\\\\\\\\n    if cbmask.shape!=(1,L) or cbpos.shape!=(1,L,3) or not np.isfinite(cbmask).all() or not np.isfinite(cbpos).all():raise ValueError(\\\\\\\"Pseudo-beta template features malformed\\\\\\\")\\\\\\\\n    rawmask=np.asarray(data[\\\\\\\"batch_all_atom_mask\\\\\\\"],float);rawpos=np.asarray(data[\\\\\\\"batch_all_atom_positions\\\\\\\"],float)\\\\\\\\n    if rawmask.shape!=(L,37) or rawpos.shape!=(L,37,3):raise ValueError(\\\\\\\"Raw target-only source batch shape\\\\\\\")\\\\\\\\n    mapping={int(k)-1:int(v)-1 for k,v in job[\\\\\\\"target_query_to_template_indices\\\\\\\"].items()}');\\\\nc=c.replace('    if mask[:,T:].any() or pos[:,T:].any():','    if rawmask[T:].any() or rawpos[T:].any() or cbmask[:,T:].any() or cbpos[:,T:].any():raise ValueError(\\\\\\\"Binder raw/template pseudo-beta leakage\\\\\\\")\\\\\\\\n    if absent and (rawmask[absent].any() or rawpos[absent].any() or cbmask[:,absent].any() or cbpos[:,absent].any()):raise ValueError(\\\\\\\"Missing target raw/pseudo-beta leakage\\\\\\\")\\\\\\\\n    if mask[:,T:].any() or pos[:,T:].any():');\\\\nc=c.replace('    if not job[\\\\\\\"target_template_enabled\\\\\\\"] and n!=0:','    if not job[\\\\\\\"target_template_enabled\\\\\\\"] and (cbmask.any() or cbpos.any()):raise ValueError(\\\\\\\"No-template pseudo-beta channel leaked\\\\\\\")\\\\\\\\n    if not job[\\\\\\\"target_template_enabled\\\\\\\"] and n!=0:');\\\\nc=c.replace('actual_query_length=L)','actual_query_length=L,initial_prev_pos_nonzero=0,all_models_features_verified=f.get(\\\\\\\"all_models_feature_arrays_identical\\\\\\\"))');\\\\nc=c.replace('        if worker.get(\\\\\\\"allocation\\\\\\\",{}).get(\\\\\\\"allocated_gpu_count\\\\\\\")!=1:raise ValueError(\\\\\\\"GPU worker actual scheduler allocation missing/not1\\\\\\\")','        allocation_receipt=worker.get(\\\\\\\"allocation\\\\\\\",{})\\\\\\\\n        if allocation_receipt.get(\\\\\\\"allocated_gpu_count\\\\\\\")!=1:raise ValueError(\\\\\\\"GPU worker actual scheduler allocation missing/not1\\\\\\\")');\\\\nc=c.replace('components(conf[\\\\\\\"iptm\\\\\\\"],float(pp[na:].mean()),ip,cp)','components(conf.get(\\\\\\\"iptm\\\\\\\",conf.get(\\\\\\\"globaliptm\\\\\\\")),float(pp[na:].mean()),ip,cp)');\\\\nc=c.replace('global_iptm=float(conf[\\\\\\\"iptm\\\\\\\"])','global_iptm=float(conf.get(\\\\\\\"iptm\\\\\\\",conf.get(\\\\\\\"globaliptm\\\\\\\")))');\\\\nc=c.replace('        np.savez(path,mask=mask,pos=pos,aatype=query,msa=np.zeros((1,L,49)))','        cbmask=np.zeros((1,L));cbpos=np.zeros((1,L,3))\\\\\\\\n        np.savez(path,mask=mask,pos=pos,aatype=query,msa=np.zeros((1,L,49)),prev_pos=np.zeros((L,37,3)),template_pseudo_beta_mask=cbmask,template_pseudo_beta=cbpos,batch_all_atom_mask=np.zeros((L,37)),batch_all_atom_positions=np.zeros((L,37,3)))');\\\\nc=c.replace('actual_query_length=L,initial_prev_pos_nonzero=0,all_models_features_verified=f.get(\\\\\\\"all_models_feature_arrays_identical\\\\\\\"))','actual_query_length=L,initial_prev_pos_nonzero=0)');\\\\nstore(\\\\\\\"bbf_diagnostic_code_v3\\\\\\\",c);store(\\\\\\\"bbf_diagnostic_code_v2\\\\\\\",c);\\\\nconst q=s=>\\\\\\\"'\\\\\\\"+s.replace(/'/g,\\\\\\\"'\\\\\\\\\\\\\\\\''\\\\\\\")+\\\\\\\"'\\\\\\\";\\\\ntext(await tools.exec_command({cmd:load(\\\\\\\"screen_ssh\\\\\\\")+\\\\\\\" \\\\\\\"+q(\\\\\\\"cat > /lustre/users/u21111210118/projects/test9/source/rebuild/bbf_input_diagnostic.py <<'PY'\\\\\\\\n\\\\\\\"+c+\\\\\\\"\\\\\\\\nPY\\\\\\\\nsbatch /lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/code/cpu.sbatch test --out /lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/inputs/test_v3.json\\\\\\\\nsacct -j 13036 --format=JobID,State,ExitCode,Elapsed -n\\\\\\\\ntail -n 40 /lustre/users/u21111210118/projects/test9/steps/23_common_review/logs/hardware_13036.log\\\\\\\"),max_output_tokens:2000}));\\\\n\\\",\\\"internal_chat_message_metadata_passthrough\\\":{\\\"turn_id\\\":\\\"01a12928-f105-7cd3-bed9-6c73e91f0804\\\",\\\"create_time\\\":1791695150.7349188}}}\"},{\"record_line\":1408,\"raw_JSONL_record\":\"{\\\"timestamp\\\":\\\"2026-10-11T05:07:12.719Z\\\",\\\"ordinal\\\":1407,\\\"type\\\":\\\"response_item\\\",\\\"payload\\\":{\\\"type\\\":\\\"custom_tool_call\\\",\\\"id\\\":\\\"ctc_00918a3c2e5efc41016acb197e379c81918ceebce2e037ab7f\\\",\\\"status\\\":\\\"completed\\\",\\\"call_id\\\":\\\"call_695893637f52466ba2c6f5638ac69a8b\\\",\\\"name\\\":\\\"exec\\\",\\\"input\\\":\\\"let c=load(\\\\\\\"bbf_diagnostic_code_v3\\\\\\\");\\\\nc=c.replace('    checked=[]\\\\\\\\n    for key,job','    verify(features[\\\\\\\"source\\\\\\\"])\\\\\\\\n    checked=[]\\\\\\\\n    for key,job');\\\\nc=c.replace('        f=actual[key];actual_stats=feature_arrays(job,f)','        f=actual[key];actual_stats=feature_arrays(job,f)\\\\\\\\n        if f[\\\\\\\"actual_validated_model_slots\\\\\\\"]!=job[\\\\\\\"slots\\\\\\\"] or not f[\\\\\\\"all_models_feature_arrays_identical\\\\\\\"]:raise ValueError(\\\\\\\"Every fixed model actual forward feature proof required\\\\\\\")');\\\\nstore(\\\\\\\"bbf_diagnostic_code_v3\\\\\\\",c);store(\\\\\\\"bbf_diagnostic_code_v2\\\\\\\",c);\\\\nconst q=s=>\\\\\\\"'\\\\\\\"+s.replace(/'/g,\\\\\\\"'\\\\\\\\\\\\\\\\''\\\\\\\")+\\\\\\\"'\\\\\\\";\\\\ntext(await tools.exec_command({cmd:load(\\\\\\\"screen_ssh\\\\\\\")+\\\\\\\" \\\\\\\"+q(\\\\\\\"cat > /lustre/users/u21111210118/projects/test9/source/rebuild/bbf_input_diagnostic.py <<'PY'\\\\\\\\n\\\\\\\"+c+\\\\\\\"\\\\\\\\nPY\\\\\\\"),max_output_tokens:300}));\\\\n\\\",\\\"internal_chat_message_metadata_passthrough\\\":{\\\"turn_id\\\":\\\"01a12928-f105-7cd3-bed9-6c73e91f0804\\\",\\\"create_time\\\":1791695230.221601}}}\"}],\"recorded_tool_calls_executed\":false,\"scope\":\"Only exact two original JSONL records copied as data; AST literal replace statements only, no history execution.\"}")
  for token in ("timestamp","name","input"):
   altered=copy.deepcopy(data);item=json.loads(altered["records"][0]["raw_JSONL_record"])
   if token=="timestamp":item[token]="2020-01-01"
   elif token=="name":item["payload"][token]="different"
   else:item["payload"][token]=item["payload"][token].replace("c=c.replace(","c=other.replace(",1)
   altered["records"][0]["raw_JSONL_record"]=json.dumps(item)
   with self.subTest(token=token):
    with self.assertRaises(ValueError):m.recorded_js_patches(m.BBF_REPLAY_PINS["records"],lambda r:json.dumps(altered).encode())
 def test_JS_quoted_escape_positive_and_unknown_rejected(self):
  self.assertEqual(m.js_literal("'a\\nb'"),"a\nb")
  for token in ("'a\\q'","'''x'''","'line\nbreak'"):
   with self.subTest(token=token):
    with self.assertRaises(ValueError):m.js_literal(token)
 def test_numeric_terminal_complete_and_failed_predecessor(self):
  for state,code in (("COMPLETED","0:0"),("FAILED","1:0")):
   self.assertEqual(m.source_alias_terminal_record(self.terminal(state,code))["expected_state"],state)
 def test_numeric_terminal_GPU_duplicate_and_fraction_rejected(self):
  for tres in ("cpu=1,gres/gpu=0,gres/gpu:a100=1","cpu=1,cpu=1","cpu=1,gres/gpu=0.0","cpu=2"):
   with self.subTest(tres=tres):
    with self.assertRaises(ValueError):m.source_alias_terminal_record(self.terminal(tres=tres))
 def test_numeric_terminal_owner_or_state_fork_rejected(self):
  for bad in ("u21111210118|u21111210118","COMPLETED|0:0","organ|"):
   row=self.terminal();row["raw_sacct"]=row["raw_sacct"].replace(bad,"wrong|")
   with self.subTest(bad=bad):
    with self.assertRaises(ValueError):m.source_alias_terminal_record(row)
 def test_source_proof_view_scalarizes_only_called_exact_parent(self):
  r=dict(path="/synthetic/proof.json",bytes=4,sha256="a"*64);obj=dict(observed=dict(path="/old/file.py",bytes=8,sha256="b"*64),label="KEEP")
  saved=dict(proof_parent_views=[dict(parent_manifest=r,view=m.scalar_source_proof_view(obj))])
  view=m.source_alias_proof_parent_view(r,saved,lambda receipt:json.dumps(obj).encode())
  self.assertEqual(view["label"],"KEEP");self.assertEqual(list(m.receipt_edges(view)),[])
  self.assertIsNone(m.source_alias_proof_parent_view({**r,"sha256":"c"*64},saved,lambda receipt:json.dumps(obj).encode()))
 def test_source_proof_view_changed_parent_payload_rejected(self):
  r=dict(path="/synthetic/proof.json",bytes=4,sha256="a"*64);obj=dict(label="OLD")
  saved=dict(proof_parent_views=[dict(parent_manifest=r,view=m.scalar_source_proof_view(obj))])
  with self.assertRaises(ValueError):m.source_alias_proof_parent_view(r,saved,lambda receipt:b'{"label":"NEW"}')
 def test_exported_qualification_preserves_canonical_not_old_receipt_edge(self):
  original=dict(path="/old/source.py",bytes=8,sha256="b"*64);canonical={**original,"path":"/readonly/source.py"}
  qualified=dict(aliases=[dict(original=original,canonical=canonical,basis="EXISTING_READONLY_RUNTIME_SNAPSHOT")],reconstruction_proofs=dict(BBF=dict(original_byte_identity=original)))
  out=m.export_source_alias_qualification(qualified)
  self.assertEqual(out["aliases"][0]["canonical_receipt"],canonical);self.assertEqual(out["aliases"][0]["original_logical_path"],original["path"])
  self.assertEqual([r for r,trail in m.receipt_edges(out)],[canonical])

 def test_all_provenance_inputs_postwalk_drift_is_rejected(self):
  with tempfile.TemporaryDirectory()as directory:
   path=Path(directory)/"frozen_origin.py";path.write_bytes(b"VALUE=7\n");path.chmod(0o444)
   receipt=dict(path=str(path),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
   qualified=dict(canonical_source_and_provenance_inputs=[receipt])
   def reader(r):
    current=Path(r["path"]);data=current.read_bytes()
    if current.stat().st_mode&0o222 or len(data)!=r["bytes"]or hashlib.sha256(data).hexdigest()!=r["sha256"]:raise ValueError("Postwalk provenance input drift")
    return data
   self.assertEqual(m.source_alias_provenance_postreadback(qualified,reader)["verified_inputs"],[receipt])
   path.chmod(0o644);path.write_bytes(b"VALUE=8\n");path.chmod(0o444)
   with self.assertRaisesRegex(ValueError,"Postwalk"):m.source_alias_provenance_postreadback(qualified,reader)
 def test_restore_requires_explicit_reader_without_live_default(self):
  with self.assertRaisesRegex(ValueError,"explicit restored-index"):m.verify_exported_source_alias_qualification({},restore=True)
  from unittest.mock import patch
  qualified=dict(aliases=[],reconstruction_proofs=dict(BBF=dict(original_byte_identity=dict(path="/old.py",bytes=1,sha256="a"*64))),terminal_accounting=[])
  saved=m.export_source_alias_qualification(qualified);reader=lambda receipt:b"ONLY_RESTORED_TOY_BYTES"
  with patch.object(m,"qualify_source_alias_inputs",return_value=qualified)as call:
   self.assertEqual(m.verify_exported_source_alias_qualification(saved,reader,restore=True),qualified)
   call.assert_called_once_with(reader,[])
if __name__=="__main__":unittest.main()
