"""CPU-only exact3path/source software boundary fixtures, never a science gate."""
import copy,importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
S=importlib.util.spec_from_file_location("closure_under_test",Path(__file__).with_name("final_source_closure.py"))
m=importlib.util.module_from_spec(S);S.loader.exec_module(m)
SHA="a"*64
def r(p="/lustre/users/u21111210118/projects/test9/x.py",n=1,h=SHA):return dict(path=p,bytes=n,sha256=h)

def current_software_fixture(sources):
 original=copy.deepcopy(sources)
 runtime=dict(schema="conditional-core-interpreter-byte-identity.v1",logical_executable=str(m.CORE_LOGICAL),link_text="python3.11",resolved_binary_identity=dict(logical_path=str(m.CORE_REAL),bytes_as_scalar=m.CORE_BYTES,sha256_as_scalar=m.CORE_SHA),conditional_excluded_not_archived=True)
 return dict(schema="final-source-materialized-software-acceptance.v3",status=m.SOFTWARE_STATUS,source_files=sources,original_executing_sources=original,
  source_entry=next(x for x in original if Path(x["path"]).name=="final_source_closure.py"),source_snapshot=r(p=str(m.R/"fixture/source_snapshot.json")),
  conditional_core_runtime=runtime,whole6_source_prepost_PASS=True,original_and_frozen_owned_bytes_identical=True,conditional_runtime_prepost_PASS=True)

def plan():
 modules=[]
 for role in sorted(m.REQUIRED_MODULES):
  status=next(iter(sorted(m.MODULE_GATE_STATUS.get(role,{"EXPLICIT_ACCEPTED_STATUS"}))))
  sources=[dict(receipt=r(),repository_relative="rebuild/x.py")]
  if role=="default_workflow_integration":
   sources=[dict(receipt=r(),repository_relative=x)for x in ("src/ppiblocker/pipeline.py","src/ppiblocker/pose_physical_gate.py","environment/runtime-lock-rfd.json")]
  modules.append(dict(role=role,gate=dict(receipt=r(p="/lustre/users/u21111210118/projects/test9/a.json"),expected_status=status),sources=sources,seeds=[]))
 return dict(schema="final-source-closure-plan.v3",root_owned=True,formal_array_job_id="13260",public_source_only=True,no_scientific_settings_change=True,root_integration_review=dict(new_generic_source_promotion_reviewed=True),modules=modules)
class Contracts(unittest.TestCase):
 def test_full_nine_roles(self):self.assertEqual(len(m.module_plan(plan())),9)
 def test_omitted_role_blocks(self):
  x=plan();x["modules"].pop()
  with self.assertRaises(ValueError):m.module_plan(x)
 def test_duplicate_role_blocks(self):
  x=plan();x["modules"].append(x["modules"][0])
  with self.assertRaises(ValueError):m.module_plan(x)
 def test_unknown_role_blocks(self):
  x=plan();x["modules"][0]["role"]="unqualified_extra"
  with self.assertRaises(ValueError):m.module_plan(x)
 def test_formal_array_cannot_drift(self):
  x=plan();x["formal_array_job_id"]="new"
  with self.assertRaises(ValueError):m.module_plan(x)
 def test_root_integration_required(self):
  x=plan();x["root_integration_review"]["new_generic_source_promotion_reviewed"]=False
  with self.assertRaises(ValueError):m.module_plan(x)
 def test_isolated_source_not_default_cli(self):
  x=plan();d=next(z for z in x["modules"]if z["role"]=="default_workflow_integration");d["sources"].pop()
  with self.assertRaises(ValueError):m.module_plan(x)
 def test_source_no_settings_change(self):
  x=plan();x["no_scientific_settings_change"]=False
  with self.assertRaises(ValueError):m.module_plan(x)
 def test_empty_module_sources_blocks(self):
  x=plan();x["modules"][0]["sources"]=[]
  with self.assertRaises(ValueError):m.module_plan(x)
 def test_current_terminal_status_exact(self):
  x=plan();d=next(z for z in x["modules"]if z["role"]=="formal13260_terminal_v3");d["gate"]["expected_status"]="PENDING"
  with self.assertRaises(ValueError):m.module_plan(x)
 def test_rejected_pose_terminal_supported(self):
  x=plan();d=next(z for z in x["modules"]if z["role"]=="reference_free_e2e");d["gate"]["expected_status"]="CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED"
  self.assertEqual(len(m.module_plan(x)),9)
 def test_zero_binder_final_supported(self):
  x=plan();d=next(z for z in x["modules"]if z["role"]=="reference_free_e2e");d["gate"]["expected_status"]="REFERENCE_FREE_E2E_COMPUTATIONAL_CHAIN_CONTENT_ACCEPTED"
  self.assertEqual(len(m.module_plan(x)),9)
 def test_corrupt_sha_rejected(self):
  with self.assertRaises(ValueError):m.receipt_shape(r(h="placeholder"))
 def test_boolean_size_rejected(self):
  with self.assertRaises(ValueError):m.receipt_shape(r(n=True))
 def test_missing_bytes_rejected(self):
  x=r();x.pop("bytes")
  with self.assertRaises(ValueError):m.receipt_shape(x)
 def test_relative_receipt_rejected(self):
  with self.assertRaises(ValueError):m.receipt_shape(r(p="x.py"))
 def test_escape_destination_rejected(self):
  with self.assertRaises(ValueError):m.destination("../out.py")
 def test_absolute_destination_rejected(self):
  with self.assertRaises(ValueError):m.destination("/tmp/out.py")
 def test_git_destination_rejected(self):
  with self.assertRaises(ValueError):m.destination(".git/hooks/a.py")
 def test_licensed_binary_excluded(self):
  with self.assertRaises(ValueError):m.eligible_public(r(p="/lustre/users/u21111210118/projects/test9/private.whl"),"x.whl")
 def test_weights_excluded(self):
  with self.assertRaises(ValueError):m.eligible_public(r(p="/lustre/users/u21111210118/projects/test9/assets/boltz/config.json"),"config.json")
 def test_asset_substring_not_conditional(self):
  self.assertFalse(m.conditional("/lustre/users/u21111210118/projects/test9/rebuild/boltz_score.py"))
 def test_receipt_nested_field_preserved(self):
  self.assertEqual(list(m.receipt_edges({"outer":[r()]}))[0][1],("outer","0"))
 def test_outside_authority_rejected(self):
  with self.assertRaises(ValueError):m.safe_path("/tmp/x.py")
 def test_only_accepted_old_pipeline_moves_to_history(self):
  old=r(h="b"*64);new=r(h="c"*64);helper=r(h="d"*64)
  ops={"src/ppiblocker/pipeline.py":dict(old=old,new=new),"src/ppiblocker/pose_physical_gate.py":dict(old=None,new=helper)}
  dest,roles=m.inherited_source_route(dict(repository_relative="src/ppiblocker/pipeline.py",source=old),ops)
  self.assertIn("exact_source_aliases",dest);self.assertEqual(roles,["SUPERSEDED_DEFAULT_GENERIC_EXACT_HISTORY"])
 def test_unrelated_or_wrong_old_bytes_never_replaced(self):
  old=r(h="b"*64);new=r(h="c"*64)
  ops={"src/ppiblocker/pipeline.py":dict(old=old,new=new)}
  with self.assertRaises(ValueError):m.inherited_source_route(dict(repository_relative="src/ppiblocker/pipeline.py",source=new),ops)
  d,roles=m.inherited_source_route(dict(repository_relative="rebuild/unrelated.py",source=new,roles=["CURRENT"]),ops)
  self.assertEqual(d,"rebuild/unrelated.py");self.assertEqual(roles,["CURRENT"])

class ClosureFixtureContracts(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.oldroot=m.R;m.R=self.root
  self.source=self.root/"source";self.source.mkdir();self.asset=self.root/"fixture";self.asset.mkdir()
  def file(name,text,readonly=True):
   p=self.asset/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
   if readonly:p.chmod(0o444)
   return m.rec(p)
  def meta(name,value):return m.dump(self.asset/name,value)
  self.file=file;self.meta=meta
  self.oldpipe=file("old_pipeline.py","old\n");self.newpipe=file("new_pipeline.py","new\n");self.helper=file("new_helper.py","helper\n")
  self.oldrfd=file("old_rfd.json",json.dumps({"cache":"old225"}));self.newrfd=file("new_rfd.json",json.dumps({"cache":"full226"}))
  self.integration_sources=[file("integration/"+n,"SYNTHETIC_SOURCE_ONLY")for n in sorted(m.INTEGRATION_NAMES)]
  self.oldother=file("old_other.py","old_other\n");self.newother=file("new_other.py","new_other\n")
  for rel,rr in [("src/ppiblocker/pipeline.py",self.newpipe),("src/ppiblocker/pose_physical_gate.py",self.helper),("environment/runtime-lock-rfd.json",self.newrfd)]:
   p=self.source/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(Path(rr["path"]).read_bytes())
  current=[m.rec(self.source/rel)for rel in ("src/ppiblocker/pipeline.py","src/ppiblocker/pose_physical_gate.py","environment/runtime-lock-rfd.json")]
  manifest=meta("source_manifest.json",{"source":"accepted"})
  integration_request=meta("integration_request.json",dict(schema="default-generic-materialized-integration-request.v2",root_approved=True,source_manifest=manifest,expected_old_tree_sha256="b"*64,expected_new_tree_sha256="c"*64,
   operations=[dict(repository_relative="src/ppiblocker/pipeline.py",old=self.oldpipe,new=self.newpipe),dict(repository_relative="src/ppiblocker/pose_physical_gate.py",old=None,new=self.helper),dict(repository_relative="environment/runtime-lock-rfd.json",old=self.oldrfd,new=self.newrfd)]))
  integration=meta("integration.json",dict(schema="default-materialized-generic-integration-acceptance.v2",source_files=self.integration_sources,status="DEFAULT_GENERIC_PHYSICAL_GATE_AND_MATERIALIZED_RUNTIME_INTEGRATION_CPU_VERIFIED_NOT_PUBLISHED",request=integration_request,source_manifest=manifest,old_tree_sha256="b"*64,new_tree_sha256="c"*64,
   replacement=dict(replaced_paths=["src/ppiblocker/pipeline.py","src/ppiblocker/pose_physical_gate.py","environment/runtime-lock-rfd.json"],old_pipeline_archive=self.oldpipe,old_rfd_lock_archive=self.oldrfd,new_default_files=current)))
  closure=meta("base_closure.json",dict(schema="benchmark-source-receipt-closure.v1",edges=[]))
  inc=meta("base_inclusion.json",dict(status="SOURCE_INCLUSION_AUDIT_PASS",applied=False,issues=[],formal_array_job_id="13260",source_receipt_closure=closure,
   files=[dict(source=self.oldpipe,original_source=dict(self.oldpipe,path=str(self.source/"src/ppiblocker/pipeline.py")),repository_relative="src/ppiblocker/pipeline.py",roles=["BASE"]),dict(source=self.oldrfd,original_source=dict(self.oldrfd,path=str(self.source/"environment/runtime-lock-rfd.json")),repository_relative="environment/runtime-lock-rfd.json",roles=["BASE"]),dict(source=self.oldother,original_source=self.oldother,repository_relative="rebuild/unrelated.py",roles=["BASE"])]))
  accepted=meta("base_acceptance.json",dict(status="CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY",source_issues=0,source_staged=False,source_inclusion=inc,source_closure=closure))
  cost=meta("cost.json",dict(status="ROOT_CURRENT_GPU_SUBMISSION_UNIVERSE_AND_TERMINAL_COST_CPU_ACCEPTED",complete_root_gpu_submission_universe=True,allocated_failure_before_manifest_cost_retained=True,root_gpu_submission_receipts=[],terminal_numeric_accounting_receipts=[]))
  self.p=plan();self.p["base_acceptance"]=accepted
  for module in self.p["modules"]:
   role=module["role"];status=module["gate"]["expected_status"]
   if role=="reference_free_e2e":status="REFERENCE_FREE_E2E_COMPUTATIONAL_CHAIN_CONTENT_ACCEPTED"
   gate=integration if role=="default_workflow_integration"else meta(role+".json",dict(status=status))
   module["gate"]=dict(receipt=gate,expected_status=status)
   module["sources"]=[dict(receipt=self.newother,repository_relative="rebuild/"+role+".py")]
   if role=="default_workflow_integration":
    module["sources"]=[dict(receipt=rr,repository_relative=rel)for rr,rel in zip(current,("src/ppiblocker/pipeline.py","src/ppiblocker/pose_physical_gate.py","environment/runtime-lock-rfd.json"))]+[dict(receipt=rr,repository_relative="rebuild/integration/"+Path(rr["path"]).name)for rr in self.integration_sources]
   if role in {"reference_free_e2e","formal_common_review"}:module["allocation_closure_gate"]=dict(receipt=cost,expected_status="ROOT_CURRENT_GPU_SUBMISSION_UNIVERSE_AND_TERMINAL_COST_CPU_ACCEPTED")
  self.patcher1=__import__("unittest.mock",fromlist=["patch"]).patch.object(m,"cpu",return_value={"allocated_gpus":0,"job_id":"CPU_FIXTURE"})
  self.original_module_file=m.__file__;original_package=Path(m.__file__).parent;fixture_package=self.root/"owned_fixture_library";fixture_package.mkdir()
  for name in m.PACKAGE_NAMES:
   shutil.copyfile(original_package/name,fixture_package/name);(fixture_package/name).chmod(0o444)
  fixture_package.chmod(0o555);m.__file__=str(fixture_package/"final_source_closure.py")
  self.patcher2=__import__("unittest.mock",fromlist=["patch"]).patch.object(m,"freeze_runner",wraps=m.freeze_runner)
  self.patcher3=__import__("unittest.mock",fromlist=["patch"]).patch.object(m,"contracts",side_effect=lambda out:m.dump(out/"contracts.json",{"status":"FIXTURE_ONLY"}))
  self.patcher4=__import__("unittest.mock",fromlist=["patch"]).patch.object(m,"require_context_reader",return_value={"SYNTHETIC_ONLY":True})
  self.patcher5=__import__("unittest.mock",fromlist=["patch"]).patch.object(m,"derived_qualification_binding",return_value={"SYNTHETIC_ONLY":True})
  for x in (self.patcher1,self.patcher2,self.patcher3,self.patcher4,self.patcher5):x.start()
 def tearDown(self):
  for x in (self.patcher1,self.patcher2,self.patcher3,self.patcher4,self.patcher5):x.stop()
  m.__file__=self.original_module_file;m.R=self.oldroot;self.tmp.cleanup()
 def run_fixture(self):
  p=self.asset/"final_plan.json";p.write_text(json.dumps(self.p));p.chmod(0o444);out=self.root/"audit_out"
  m.audit(p,out);return m.read(out/"source_inclusion_final.json")
 def test_real_closure_preserves_old_and_accepts_new_default(self):
  result=self.run_fixture();rows={x["repository_relative"]:x for x in result["files"]}
  self.assertEqual(m.fp(rows["src/ppiblocker/pipeline.py"]["source"]),m.fp(self.newpipe))
  self.assertEqual(m.fp(rows["environment/runtime-lock-rfd.json"]["source"]),m.fp(self.newrfd))
  self.assertTrue(any("SUPERSEDED_DEFAULT_RFD_LOCK_EXACT_HISTORY"in row["roles"]and m.fp(row["source"])==m.fp(self.oldrfd)for row in result["files"]))
  history=[x for x in result["files"]if "SUPERSEDED_DEFAULT_GENERIC_EXACT_HISTORY"in x["roles"]]
  self.assertEqual(len(history),1);self.assertEqual(m.fp(history[0]["source"]),m.fp(self.oldpipe))
 def test_real_unrelated_conflict_blocks_no_acceptance(self):
  module=next(x for x in self.p["modules"]if x["role"]=="formal_common_review")
  module["sources"]=[dict(receipt=self.newother,repository_relative="rebuild/unrelated.py")]
  with self.assertRaises(ValueError):self.run_fixture()
  self.assertFalse((self.root/"audit_out/acceptance.json").exists())
 def test_forged_old_pipeline_archive_blocks(self):
  module=next(x for x in self.p["modules"]if x["role"]=="default_workflow_integration")
  gate=m.read(module["gate"]["receipt"]["path"]);gate["replacement"]["old_pipeline_archive"]=self.newpipe
  module["gate"]["receipt"]=self.meta("forged_integration.json",gate)
  with self.assertRaises(ValueError):self.run_fixture()
 def test_new_current_missing_source_blocks(self):
  module=next(x for x in self.p["modules"]if x["role"]=="independent_statistics")
  module["sources"]=[dict(receipt=dict(self.newother,path=str(self.asset/"missing.py")),repository_relative="rebuild/missing.py")]
  with self.assertRaises(ValueError):self.run_fixture()


class PublicWrapperContract(unittest.TestCase):
 def test_self_authored_pyrosetta_wrapper_is_public_source(self):
  self.assertEqual(m.eligible_public(r(p="/lustre/users/u21111210118/projects/test9/scripts/check_pyrosetta_version.py"),"scripts/check_pyrosetta_version.py"),"scripts/check_pyrosetta_version.py")
class MaterializedSuccessorContracts(unittest.TestCase):
 def test_old_rfd_only_exact_archived_identity_routes_history(self):
  old=r(p=str(m.R/"lock.json"),h="b"*64);new=r(p=str(m.R/"locknew.json"),h="c"*64);ops={"environment/runtime-lock-rfd.json":dict(old=old,new=new)}
  dest,roles=m.inherited_source_route(dict(source=old,repository_relative="environment/runtime-lock-rfd.json"),ops)
  self.assertIn("runtime-lock-rfd.json",dest);self.assertEqual(roles,["SUPERSEDED_DEFAULT_RFD_LOCK_EXACT_HISTORY"])
  with self.assertRaises(ValueError):m.inherited_source_route(dict(source=new,repository_relative="environment/runtime-lock-rfd.json"),ops)
 def test_three_current_default_destinations_required(self):
  x=plan();module=next(z for z in x["modules"]if z["role"]=="default_workflow_integration");module["sources"]=[z for z in module["sources"]if z["repository_relative"]!="environment/runtime-lock-rfd.json"]
  with self.assertRaises(ValueError):m.module_plan(x)
 def test_old_two_path_status_not_accepted(self):
  x=plan();module=next(z for z in x["modules"]if z["role"]=="default_workflow_integration");module["gate"]["expected_status"]="DEFAULT_GENERIC_PHYSICAL_GATE_INTEGRATION_CPU_VERIFIED_NOT_PUBLISHED"
  with self.assertRaises(ValueError):m.module_plan(x)
 def test_exact_six_owned53_software_gate_accepts(self):
  sources=[r(p=str(m.R/"fixture"/n))for n in m.PACKAGE_NAMES]
  obj=current_software_fixture(sources);contracts=dict(status="PASS",tests=m.SOURCE_CONTRACTS,failures=0,errors=0,tested_source_files=sources,owned_python_compile_PASS=True,bash_syntax_PASS=True)
  self.assertEqual(len(m.software_shape(obj,contracts)),6)
 def test_wrong_software_source_or_count_rejected(self):
  sources=[r(p=str(m.R/"fixture"/n))for n in m.PACKAGE_NAMES];obj=current_software_fixture(sources)
  contracts=dict(status="PASS",tests=40,failures=0,errors=0,tested_source_files=sources,owned_python_compile_PASS=True,bash_syntax_PASS=True)
  with self.assertRaises(ValueError):m.software_shape(obj,contracts)
  contracts["tests"]=m.SOURCE_CONTRACTS;obj["source_files"]=[dict(row)for row in sources];obj["source_files"][0]["path"]=str(m.R/"unrelated.py")
  with self.assertRaises(ValueError):m.software_shape(obj,contracts)
  obj["source_files"]=sources
  for field in ("owned_python_compile_PASS","bash_syntax_PASS"):
   with self.subTest(missing_required_qualification=field):
    fork=dict(contracts);fork[field]=False
    with self.assertRaises(ValueError):m.software_shape(obj,fork)
class NewRFDTransactionFixtureContracts(ClosureFixtureContracts):
 # Reuse setup/run only; inherited tests are suppressed so no duplicate science fixture.
 test_real_closure_preserves_old_and_accepts_new_default=None
 test_real_unrelated_conflict_blocks_no_acceptance=None
 test_forged_old_pipeline_archive_blocks=None
 test_new_current_missing_source_blocks=None
 def test_forged_old_rfd_archive_blocks(self):
  module=next(x for x in self.p["modules"]if x["role"]=="default_workflow_integration");gate=m.read(module["gate"]["receipt"]["path"]);gate["replacement"]["old_rfd_lock_archive"]=self.newrfd;module["gate"]["receipt"]=self.meta("forged_rfd_integration.json",gate)
  with self.assertRaises(ValueError):self.run_fixture()
 def test_new_rfd_current_byte_mismatch_blocks(self):
  module=next(x for x in self.p["modules"]if x["role"]=="default_workflow_integration")
  for row in module["sources"]:
   if row["repository_relative"]=="environment/runtime-lock-rfd.json":row["receipt"]=self.oldrfd
  with self.assertRaises(ValueError):self.run_fixture()
class DerivedContractShapeFixtures(unittest.TestCase):
 def make(self):
  pipe=r(p=str(m.R/"qualified/pipeline.py"));helper=r(p=str(m.R/"physical/pose_physical_gate.py"));oldpipe=r(p=str(m.R/"physical/pipeline.py"),h="b"*64);common=r(p=str(m.R/"base/common.py"),h="c"*64);stagedcommon=r(p=str(m.R/"staged/common.py"),h="d"*64);pre=r(p=str(m.R/"physical/acceptance.json"));manifest_receipt=r(p=str(m.R/"physical/source_manifest.json"));derived_manifest=r(p=str(m.R/"derived/manifest.json"));ar=r(p=str(m.R/"derived/acceptance.json"))
  sources=[r(p=str(m.R/"derived/package"/n))for n in sorted(m.DERIVED_NAMES)]
  request=dict(source_manifest=manifest_receipt,derived_pipeline_qualification=ar,gates={"physical_preflight_v3_current":{"receipt":pre}},expected_new_tree_sha256="e"*64)
  ops={"src/ppiblocker/pipeline.py":{"new":pipe},"src/ppiblocker/pose_physical_gate.py":{"new":helper}}
  snapshot=dict(default_promotion_files=[{"repository_relative":"src/ppiblocker/pipeline.py","source":oldpipe},{"repository_relative":"src/ppiblocker/pose_physical_gate.py","source":helper}],staged_runtime_selector=dict(original_common=common,staged_common=stagedcommon))
  d=dict(schema="generic-design-input-empty-pool-qualification.v2",status="GENERIC_DESIGN_INPUT_AND_NONEMPTY_POOL_WITH_REGRESSION_DEPENDENCY_V2_CPU_ACCEPTED",parent_source_manifest=manifest_receipt,parent_physical_preflight=pre,original_physical_pipeline=oldpipe,derived_pipeline=pipe,physical_helper_unchanged=helper,default_common_original=common,staged_common_unchanged=stagedcommon,default_python_source_sha256_without_staged_runtime_selector="e"*64,staged_python_source_sha256="f"*64,default_source_unchanged=True,model_inference_performed=False,formal_benchmark_mutated=False,experimental_binding=False,experimental_blockade=False,source_staged=False,source_files=sources,derived_source_manifest=derived_manifest)
  counts={"owned_design_validation":50,"owned_source_dependencies":12,"generic_seven":73,"staged_physical":25,"staged_resource":9,"staged_design":8,"staged_selector":15,"default_physical":25}
  suites=[dict(suite=n,tests=v,returncode=0,failures=0,errors=0,skipped=0,argv=["python","EXPLICIT_SYNTHETIC_FIXTURE"],stdout=r(p=str(m.R/"fixture"/(n+".stdout"))),stderr=r(p=str(m.R/"fixture"/(n+".stderr"))),**({"junit":r(p=str(m.R/"fixture"/(n+".xml")))}if n in {"owned_design_validation","owned_source_dependencies","generic_seven"}else{}))for n,v in counts.items()]
  c=dict(status="PASS",source_files=sources,derived_source_manifest=derived_manifest,owned_tests=50,owned_dependency_tests=12,source_dependency_count=1,compiled_named_regression_dependencies=True,source_dependencies_readback_before_and_after_tests=True,generic_regression_file_count=7,staged_physical_suite_tests=57,default_physical_suite_tests=25,models_called=False,compiled_owned_and_derived=True,bash_syntax=True,suites=suites)
  manifest=dict(schema="generic-design-derived-source.v2",**{k:d[k]for k in ("parent_physical_preflight","parent_source_manifest","original_physical_pipeline","derived_pipeline","source_files","staged_python_source_sha256","default_python_source_sha256_without_staged_runtime_selector","physical_helper_unchanged","default_common_original")},staged_common=stagedcommon,formal28_112_empty_null_semantics_changed=False,generic_regression_sources=[dict(original=r(p=str(m.R/"source/tests"/n)),frozen=r(p=str(m.R/"derived/tests"/n)))for n in m.REGRESSION7])
  for key,com in (("staged_source_files",stagedcommon),("default_candidate_source_files",common)):
   manifest[key]=[dict(pipe,path=str(m.R/key/"src/ppiblocker/pipeline.py")),dict(helper,path=str(m.R/key/"src/ppiblocker/pose_physical_gate.py")),dict(com,path=str(m.R/key/"src/ppiblocker/common.py"))]
  dependency=dict(relative_path="scripts/register_runtime_locks.py",role="UNCHANGED_GENERIC_RUNTIME_REGISTRATION_TEST_IMPORT_DEPENDENCY",original=r(p=str(m.R/"source/scripts/register_runtime_locks.py")),frozen=r(p=str(m.R/"derived/scripts/register_runtime_locks.py")))
  failed=dict(schema="generic-design-qualification-failed-v1-history.v1",status="ACTUAL_FAILED13303_V1_PRESERVED_NOT_QUALIFIED",incomplete=r(p=str(m.R/"failed13303/typed_incomplete.json")),terminal_numeric_accounting=dict(job_id="13303",state="FAILED",exit_code="1:0",allocated_CPUs=1,allocated_GPUs=0),repair_identity_is_distinct=True,old_acceptance_used=False)
  for obj in (d,c,manifest):obj["source_dependencies"]=[copy.deepcopy(dependency)]
  d["failed_predecessor"]=copy.deepcopy(failed);manifest["failed_predecessor"]=copy.deepcopy(failed)
  return d,c,manifest,request,ops,snapshot
 def test_actual_seven_suite_shape_positive_and_mandatory_parent(self):
  args=self.make();self.assertEqual(len(m.derived_contract_shape(*args)),8)
  for kind in ("missing","fork"):
   x=copy.deepcopy(args)
   if kind=="missing":x[3].pop("derived_pipeline_qualification")
   else:x[0]["parent_source_manifest"]=r(h="1"*64)
   with self.subTest(kind=kind),self.assertRaises(ValueError):m.derived_contract_shape(*x)
 def test_seven_suite_schema_rejects_empty_duplicate_or_aggregate_rescue(self):
  for kind in ("zero","wrong_count","duplicate","aggregate","skip"):
   x=list(copy.deepcopy(self.make()))
   if kind=="zero":x[1]["suites"][1]["tests"]=0
   elif kind=="wrong_count":x[1]["suites"][0]["tests"]=49
   elif kind=="duplicate":x[1]["suites"][1]=copy.deepcopy(x[1]["suites"][0])
   elif kind=="aggregate":x[1]=dict(status="PASS",tests=150,failures=0,errors=0,log=r(),source_files=x[0]["source_files"])
   else:x[1]["suites"][0]["skipped"]=1
   with self.subTest(kind=kind),self.assertRaises(ValueError):m.derived_contract_shape(*x)
 def test_qualified_pipeline_helper_common_source_and_identity_forks_rejected(self):
  for kind in ("pipeline","helper","common","source","tree"):
   x=list(copy.deepcopy(self.make()))
   if kind=="pipeline":x[0]["derived_pipeline"]=r(h="1"*64)
   elif kind=="helper":x[0]["physical_helper_unchanged"]=r(h="1"*64)
   elif kind=="common":x[0]["default_common_original"]=r(h="1"*64)
   elif kind=="source":x[0]["source_files"].pop()
   else:x[0]["default_python_source_sha256_without_staged_runtime_selector"]="1"*64
   with self.subTest(kind=kind),self.assertRaises(ValueError):m.derived_contract_shape(*x)

class ArchiveScalarAndMetadataContracts(unittest.TestCase):
 def make(self):
  parent=r(p=str(m.R/"archive/synthetic.members.json"));tar=r(p=str(m.R/"archive/synthetic.tar.gz"),h="b"*64)
  entry=dict(source_parent=parent,source_field=["members","0"],original_member_path="synthetic/raw.json",expected_bytes=7,expected_sha256="c"*64,canonical_receipt=None,current_execution_allowed=False,current_file_restored=False,raw_member_bytes_verified_in_archive=True)
  mapping=dict(archives=[dict(parent_manifest=parent,archive_receipt=tar,member_count=1,entries=[entry])])
  reader=__import__("types").SimpleNamespace(archives=__import__("types").SimpleNamespace(mapping=mapping))
  scalar={**entry,"archive_receipt":tar,"role":"HISTORICAL_ARCHIVE_NAMESPACE_MEMBER_BYTE_VERIFIED_NOT_CURRENT_FILE_OR_NEW_SCIENCE"}
  edge=dict(historical_archive_member=scalar,field=["members","0"],role=scalar["role"])
  return edge,reader
 def test_archive_scalar_exact_parent_field_policy_accepted(self):
  edge,reader=self.make();self.assertEqual(m.inherited_archive_edge(edge,reader),edge);self.assertNotIn("receipt",edge)
 def test_archive_scalar_unknown_parent_field_or_hash_blocks_before_dedup(self):
  for kind in ("parent","field","hash","current","canonical"):
   edge,reader=self.make()
   if kind=="parent":edge["historical_archive_member"]["source_parent"]=r(h="0"*64)
   elif kind=="field":edge["historical_archive_member"]["source_field"]=["other","0"]
   elif kind=="hash":edge["historical_archive_member"]["expected_sha256"]="0"*64
   elif kind=="current":edge["historical_archive_member"]["current_execution_allowed"]=True
   else:edge["historical_archive_member"]["canonical_receipt"]=r()
   with self.subTest(kind=kind),self.assertRaises(ValueError):m.inherited_archive_edge(edge,reader)
 def test_unqualified_archive_scalar_mapping_missing_or_role_fork_rejected(self):
  edge,reader=self.make()
  with self.assertRaises(ValueError):m.inherited_archive_edge(edge,__import__("types").SimpleNamespace())
  edge["role"]="HISTORY_ANY"
  with self.assertRaises(ValueError):m.inherited_archive_edge(edge,reader)
 def test_nonstring_or_unknown_metadata_marker_keeps_nested_receipts(self):
  for value in ({},[],None,1,True,"ordinary-unknown"):
   raw=dict(schema=value,operative=r())
   with self.subTest(value=value):
    self.assertFalse(m.metadata_only(raw));self.assertEqual(list(m.receipt_edges(raw))[0][0],raw["operative"])
  for value in m.METADATA_ONLY:self.assertTrue(m.metadata_only(dict(schema=value)))
class DerivedV2DependencyContracts(DerivedContractShapeFixtures):
 test_actual_seven_suite_shape_positive_and_mandatory_parent=None
 test_seven_suite_schema_rejects_empty_duplicate_or_aggregate_rescue=None
 test_qualified_pipeline_helper_common_source_and_identity_forks_rejected=None
 def test_actual_eighth_dependency_suite_and_original_sibling_binding(self):
  args=self.make();self.assertEqual(len(m.derived_contract_shape(*args)),8);dep=m.derived_dependency_shape(*args[:3]);self.assertTrue(dep["frozen"]["path"].endswith("/derived/scripts/register_runtime_locks.py"))
 def test_missing_or_wrong_dependency_suite_compile_flags_rejected(self):
  for key,change in (("suites",None),("owned_dependency_tests",11),("compiled_named_regression_dependencies",False),("source_dependencies_readback_before_and_after_tests",False)):
   args=list(copy.deepcopy(self.make()))
   if key=="suites":args[1]["suites"]=[x for x in args[1]["suites"]if x["suite"]!="owned_source_dependencies"]
   else:args[1][key]=change
   with self.subTest(key=key),self.assertRaises(ValueError):m.derived_contract_shape(*args)
 def test_dependency_current_path_frozen_bytes_or_manifest_forks_rejected(self):
  for kind in ("missing","original","frozen","byte","manifest"):
   args=list(copy.deepcopy(self.make()))
   if kind=="missing":args[0]["source_dependencies"]=[]
   elif kind=="original":args[0]["source_dependencies"][0]["original"]["path"]=str(m.R/"source/scripts/other.py")
   elif kind=="frozen":args[0]["source_dependencies"][0]["frozen"]["path"]=str(m.R/"other/scripts/register_runtime_locks.py")
   elif kind=="byte":args[0]["source_dependencies"][0]["frozen"]["sha256"]="0"*64
   else:args[2]["source_dependencies"]=[]
   with self.subTest(kind=kind),self.assertRaises(ValueError):m.derived_contract_shape(*args)
 def test_failed13303_v1_history_cannot_qualify_or_be_absent(self):
  for kind in ("missing","job","state","gpu","boolcpu","reused","incomplete"):
   args=list(copy.deepcopy(self.make()))
   if kind=="missing":args[0].pop("failed_predecessor")
   elif kind=="job":args[0]["failed_predecessor"]["terminal_numeric_accounting"]["job_id"]="1"
   elif kind=="state":args[0]["failed_predecessor"]["terminal_numeric_accounting"]["state"]="COMPLETED"
   elif kind=="gpu":args[0]["failed_predecessor"]["terminal_numeric_accounting"]["allocated_GPUs"]=1
   elif kind=="boolcpu":args[0]["failed_predecessor"]["terminal_numeric_accounting"]["allocated_CPUs"]=True
   elif kind=="reused":args[0]["failed_predecessor"]["old_acceptance_used"]=True
   else:args[0]["failed_predecessor"].pop("incomplete")
   with self.subTest(kind=kind),self.assertRaises((ValueError,KeyError)):m.derived_contract_shape(*args)

if __name__=="__main__":unittest.main()

class FiniteReaderBindingContracts(unittest.TestCase):
 def case(self):
  from types import SimpleNamespace
  fields=("relative_receipt_context_mapping","external_historical_receipt_context_mapping","current_recovered_relative_receipt_context_mapping","archive_member_receipt_context_mapping")
  artifacts={n:{"path":"/synthetic/"+n,"bytes":1,"sha256":"a"*64}for n in ("finite_source_recovery_inputs_qualification","finite_source_alias_verification","finite_exact_source_alias_index")}
  plan={"mapper_software_acceptance":{"path":"/synthetic/mapper","bytes":1,"sha256":"b"*64},"base_acceptance":{"path":"/synthetic/base","bytes":1,"sha256":"c"*64},**{n:{"path":"/synthetic/"+n,"bytes":1,"sha256":"d"*64}for n in fields}}
  accepted={"schema":"exact-current-context-mapper-acceptance.v4","status":"EXACT_BBF6_RECOVERED5_NINE_ANNOTATIONS_ARCHIVE588_AND_EIGHT_SOURCE_ALIASES_MAPPER_CPU_ACCEPTED","base_acceptance":plan["base_acceptance"],**{n:plan[n]for n in fields},**artifacts,"exact_recovered_source_identity_n":8,"exact_original_source_edge_n":12}
  verification={"schema":"independent-source-alias-and-provenance-verification.v1","status":"EXACT_V10_SELECTED8_ORIGINAL12_AND_FIVE_PROOF_PARENTS_INDEPENDENTLY_CPU_VERIFIED","artifacts":artifacts}
  reader=SimpleNamespace(accepted=accepted,qualification={"mapper_acceptance":plan["mapper_software_acceptance"]},finite=SimpleNamespace(verification=verification),proof=lambda:{"SYNTHETIC_BINDING_BOUNDARY":True},require_both_used=lambda:True)
  return plan,reader
 def test_complete_finite_source_reader_binding_accepts(self):
  p,r=self.case();self.assertTrue(m.require_context_reader(p,r,True)["SYNTHETIC_BINDING_BOUNDARY"])
 def test_missing_finite_source_reader_rejected(self):
  p,r=self.case();r.finite=None
  with self.assertRaises(ValueError):m.require_context_reader(p,r)
 def test_forked_finite_source_artifact_rejected(self):
  p,r=self.case();r.accepted["finite_source_alias_verification"]={"path":"/different","bytes":1,"sha256":"e"*64}
  with self.assertRaises(ValueError):m.require_context_reader(p,r)
 def test_incomplete_known_source_denominator_rejected(self):
  p,r=self.case();r.accepted["exact_original_source_edge_n"]=11
  with self.assertRaises(ValueError):m.require_context_reader(p,r)


class InheritedEntryPointAndSourceIdentityContracts(unittest.TestCase):
 """SOURCE-only fixtures. Padding rows are synthetic metadata, never a science result."""
 def case(self):
  files=[dict(source=r(p=str(m.R/"synthetic_inherited"/(str(i)+".py"))),repository_relative="rebuild/synthetic_inherited/"+str(i)+".py",roles=["SYNTHETIC_SOURCE_ONLY"])for i in range(683)]
  for record in m.INHERITED_ENTRYPOINT_CONTEXTS:files[record["index"]]=copy.deepcopy(record["row"])
  return files,m.InheritedEntryPointScope(copy.deepcopy(m.INHERITED_ENTRYPOINT_BASE),copy.deepcopy(m.INHERITED_ENTRYPOINT_INCLUSION),files)
 def observe(self,scope,index,row):
  d,k=scope.permission(index,row,row["source"],row["repository_relative"],row["roles"]);scope.mark_retained(index,row);return d,k
 def complete(self,files,scope):
  return [self.observe(scope,i,row)for i,row in enumerate(files)]
 def test_all_four_contexts_are_authorized_before_two_physical_identities_dedup(self):
  files,scope=self.case();result=self.complete(files,scope);proof=scope.proof()
  self.assertEqual(proof["authorized_context_n"],4);self.assertEqual(len({m.key(x["row"]["source"])for x in proof["authorized_contexts"]}),2)
  for record in m.INHERITED_ENTRYPOINT_CONTEXTS:
   self.assertEqual(result[record["index"]],(record["row"]["repository_relative"],"IMPLEMENTATION"))
   self.assertEqual(record["row"]["roles"],[record["row"]["role"]])
 def test_entrypoint_source_and_original_fulltuple_forks_rejected(self):
  for field in ("source","original_source"):
   for part,value in (("path",str(m.R/"wrong_entry")),("bytes",999),("sha256","0"*64)):
    files,scope=self.case();row=files[561];row[field][part]=value
    with self.subTest(field=field,part=part),self.assertRaises(ValueError):self.observe(scope,561,row)
 def test_entrypoint_destination_role_kind_and_metadata_type_forks_rejected(self):
  for field,value in (("repository_relative","rebuild/other/boltz"),("role","OTHER"),("roles",["OTHER"]),("kind","DOCUMENT"),("cluster_specific",1),("logical_receipts",[r()])):
   files,scope=self.case();row=files[561];row[field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):self.observe(scope,561,row)
  files,scope=self.case();files[561]["extra"]=True
  with self.assertRaises(ValueError):self.observe(scope,561,files[561])
 def test_unknown_extensionless_and_generic_module_sources_have_no_permission(self):
  for name in ("boltz","colabfold_batch","unknown"):
   files,scope=self.case();row=files[0];row["source"]=r(p=str(m.R/"unknown"/name))
   scope=m.InheritedEntryPointScope(m.INHERITED_ENTRYPOINT_BASE,m.INHERITED_ENTRYPOINT_INCLUSION,files)
   with self.subTest(name=name),self.assertRaisesRegex(ValueError,"Only four exact accepted"):self.observe(scope,0,row)
  for record in m.INHERITED_ENTRYPOINT_CONTEXTS:
   with self.subTest(path=record["row"]["source"]["path"]),self.assertRaises(ValueError):m.eligible_public(record["row"]["source"],record["row"]["repository_relative"])
  with self.assertRaises(ValueError):m.eligible_public(r(p=str(m.R/"wrong.txt")),"rebuild/wrong.txt")
 def test_exact_base_inclusion_parents_and_683_count_are_mandatory(self):
  for which in ("base","inclusion"):
   for part,value in (("path",str(m.R/"other.json")),("bytes",1),("sha256","0"*64)):
    files,unused=self.case();base=copy.deepcopy(m.INHERITED_ENTRYPOINT_BASE);inc=copy.deepcopy(m.INHERITED_ENTRYPOINT_INCLUSION)
    (base if which=="base"else inc)[part]=value
    with self.subTest(which=which,part=part),self.assertRaises(ValueError):m.InheritedEntryPointScope(base,inc,files)
  files,unused=self.case()
  with self.assertRaises(ValueError):m.InheritedEntryPointScope(m.INHERITED_ENTRYPOINT_BASE,m.INHERITED_ENTRYPOINT_INCLUSION,files[:-1])
 def test_missing_known_context_is_rejected_even_if_all_row_ids_are_retained(self):
  files,scope=self.case();files[561]=dict(source=r(p=str(m.R/"ordinary.py")),repository_relative="rebuild/ordinary.py",roles=["SYNTHETIC_SOURCE_ONLY"])
  scope=m.InheritedEntryPointScope(m.INHERITED_ENTRYPOINT_BASE,m.INHERITED_ENTRYPOINT_INCLUSION,files)
  with self.assertRaises(ValueError):self.complete(files,scope)
 def test_duplicate_context_observation_cannot_hide_behind_source_dedup(self):
  files,scope=self.case();self.observe(scope,561,files[561])
  with self.assertRaises(ValueError):self.observe(scope,561,files[561])
  with self.assertRaises(ValueError):scope.permission(562,files[561],files[561]["source"],files[561]["repository_relative"],files[561]["roles"])
 def test_all_683_retention_and_no_dropped_row_proof(self):
  files,scope=self.case();self.complete(files,scope);proof=scope.proof()
  self.assertEqual(proof["inherited_source_row_n"],683);self.assertEqual(proof["retained_inherited_source_row_n"],683);self.assertTrue(proof["every_inherited_row_retained"])
  files,scope=self.case();self.complete(files,scope);scope.retained.remove(10)
  with self.assertRaises(ValueError):scope.proof()
 def test_actual_two_literal_entrypoint_source_bytes_are_readonly_utf8_not_runtime(self):
  for record in m.INHERITED_ENTRYPOINT_CONTEXTS:
   source=record["row"]["source"];p=m.verify(source,True);value=p.read_bytes()
   self.assertEqual(len(value),source["bytes"]);self.assertEqual(m.rec(p),source);self.assertIn("import sys",value.decode("utf-8"));self.assertFalse(m.conditional(p))
   self.assertEqual(record["row"]["kind"],"IMPLEMENTATION")
 def test_original_and_frozen_six_real_toy_files_reject_drift_writable_and_symlink(self):
  with tempfile.TemporaryDirectory()as temp:
   d=Path(temp);oldroot=m.R;m.R=d
   try:
    originals=d/"original";frozen=d/"frozen";originals.mkdir();frozen.mkdir()
    for name in m.PACKAGE_NAMES:
     (originals/name).write_text("SYNTHETIC_SOURCE_ONLY\n");(frozen/name).write_text("SYNTHETIC_SOURCE_ONLY\n");(originals/name).chmod(0o444);(frozen/name).chmod(0o444)
    originals.chmod(0o555);frozen.chmod(0o555)
    left,lm=m.owned_source_bundle(originals);right,rm=m.owned_source_bundle(frozen)
    self.assertTrue(m.owned_source_readback(left,right,lm,rm))
    p=originals/m.PACKAGE_NAMES[0];p.chmod(0o644)
    with self.assertRaises(ValueError):m.owned_source_readback(left,right,lm,rm)
    p.write_text("CHANGED_SOURCE\n");p.chmod(0o444)
    with self.assertRaises(ValueError):m.owned_source_readback(left,right,lm,rm)
    originals.chmod(0o755);p.unlink();p.symlink_to(frozen/m.PACKAGE_NAMES[0])
    with self.assertRaises(ValueError):m.owned_source_bundle(originals)
   finally:
    originals.chmod(0o755);frozen.chmod(0o755);m.R=oldroot
 def test_software65_gate_requires_whole_source_snapshot_and_runtime_flags(self):
  sources=[r(p=str(m.R/"synthetic"/n))for n in m.PACKAGE_NAMES];obj=current_software_fixture(sources)
  contracts=dict(status="PASS",tests=65,failures=0,errors=0,tested_source_files=sources,owned_python_compile_PASS=True,bash_syntax_PASS=True)
  self.assertEqual(m.SOURCE_CONTRACTS,65);self.assertEqual(m.software_shape(obj,contracts),sources)
  for field in ("whole6_source_prepost_PASS","original_and_frozen_owned_bytes_identical","conditional_runtime_prepost_PASS"):
   fork=copy.deepcopy(obj);fork[field]=False
   with self.subTest(field=field),self.assertRaises(ValueError):m.software_shape(fork,contracts)
  for field in ("source_snapshot","original_executing_sources","source_entry"):
   fork=copy.deepcopy(obj);fork.pop(field)
   with self.subTest(field=field),self.assertRaises((KeyError,ValueError)):m.software_shape(fork,contracts)
  fork=copy.deepcopy(contracts);fork["tests"]=53
  with self.assertRaises(ValueError):m.software_shape(obj,fork)
 def test_conditional_core_and_snapshot_metadata_forks_are_rejected(self):
  sources=[r(p=str(m.R/"synthetic"/n))for n in m.PACKAGE_NAMES];obj=current_software_fixture(sources)
  self.assertEqual(m.core_runtime_shape(obj["conditional_core_runtime"]),obj["conditional_core_runtime"])
  for field,value in (("link_text","other"),("logical_executable","/tmp/python"),("conditional_excluded_not_archived",False)):
   fork=copy.deepcopy(obj["conditional_core_runtime"]);fork[field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):m.core_runtime_shape(fork)
  for field,value in (("bytes_as_scalar",1),("sha256_as_scalar","0"*64),("logical_path","/tmp/other")):
   fork=copy.deepcopy(obj["conditional_core_runtime"]);fork["resolved_binary_identity"][field]=value
   with self.subTest(identity_field=field),self.assertRaises(ValueError):m.core_runtime_shape(fork)
  def table(rows):return [dict(path=r["path"],bytes=r["bytes"],inode=i+1,mtime_ns=1,ctime_ns=1,mode=0o100444,dev=1,nlink=1,uid=1,gid=1)for i,r in enumerate(rows)]
  snap=dict(schema="final-source-owned-six-byte-snapshot.v1",source_entry=obj["source_entry"],original_executing_sources=obj["original_executing_sources"],source_files=sources,
   original_metadata_before=table(obj["original_executing_sources"]),original_metadata_after=table(obj["original_executing_sources"]),frozen_metadata_before=table(sources),frozen_metadata_after=table(sources),
   conditional_core_runtime=obj["conditional_core_runtime"],whole6_source_prepost_PASS=True,original_and_frozen_owned_bytes_identical=True,conditional_runtime_prepost_PASS=True)
  self.assertEqual(m.software_snapshot_shape(obj,snap),snap)
  for kind in ("schema","dtype","writable","drift","path","runtime"):
   fork=copy.deepcopy(snap)
   if kind=="schema":fork["schema"]="other"
   elif kind=="dtype":fork["original_metadata_before"][0]["inode"]=True;fork["original_metadata_after"][0]["inode"]=True
   elif kind=="writable":fork["original_metadata_before"][0]["mode"]=0o100644;fork["original_metadata_after"][0]["mode"]=0o100644
   elif kind=="drift":fork["frozen_metadata_after"][0]["mtime_ns"]=2
   elif kind=="path":fork["original_metadata_before"][0]["path"]="/tmp/other";fork["original_metadata_after"][0]["path"]="/tmp/other"
   else:fork["conditional_core_runtime"]["resolved_binary_identity"]["sha256_as_scalar"]="0"*64
   with self.subTest(kind=kind),self.assertRaises(ValueError):m.software_snapshot_shape(obj,fork)
