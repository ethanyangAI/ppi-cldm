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
  contracts=dict(status="PASS",tests=m.SOURCE_CONTRACTS,failures=0,errors=0,tested_source_files=sources,owned_python_compile_PASS=True,bash_syntax_PASS=True)
  self.assertEqual(m.SOURCE_CONTRACTS,356);self.assertEqual(m.software_shape(obj,contracts),sources)
  for field in ("whole6_source_prepost_PASS","original_and_frozen_owned_bytes_identical","conditional_runtime_prepost_PASS"):
   fork=copy.deepcopy(obj);fork[field]=False
   with self.subTest(field=field),self.assertRaises(ValueError):m.software_shape(fork,contracts)
  for field in ("source_snapshot","original_executing_sources","source_entry"):
   fork=copy.deepcopy(obj);fork.pop(field)
   with self.subTest(field=field),self.assertRaises((KeyError,ValueError)):m.software_shape(fork,contracts)
  for obsolete_count in (53,65,90,122,154,158,196,198,238,284,312,319,321):
   fork=copy.deepcopy(contracts);fork["tests"]=obsolete_count
   with self.subTest(obsolete_count=obsolete_count),self.assertRaises(ValueError):m.software_shape(obj,fork)
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


class VendorExampleOpaqueContracts(unittest.TestCase):
 def setUp(self):
  self.temp = tempfile.TemporaryDirectory()
  self.root = Path(self.temp.name)
  self.saved = {name: getattr(m, name) for name in ("R", "_VENDOR_EXAMPLE_PARENT", "_VENDOR_EXAMPLE_LEAF")}
  m.R = self.root
  self.parent = self.root / "vendor_inventory.json"
  self.leaf = self.root / "vendor" / "example.json"
  self.leaf.parent.mkdir()
  self.raw = "".join("DLLL " + json.dumps({"type": "METADATA" if i == 0 else "LOG", "synthetic_only": i}) + "\n" for i in range(52)).encode()
  self.leaf.write_bytes(self.raw)
  self.leaf.chmod(0o664)
  m._VENDOR_EXAMPLE_LEAF = m.rec(self.leaf)
  self.rows = [r(p=str(self.root / ("ordinary_" + str(i) + ".py"))) for i in range(18)]
  self.rows[15] = copy.deepcopy(m._VENDOR_EXAMPLE_LEAF)
  self.rewrite_parent(self.rows)
  self.out = self.root / "out"
  self.out.mkdir()
  self.scope = m.VendorExampleOpaqueLeaf(self.out)

 def tearDown(self):
  for name, value in self.saved.items():
   setattr(m, name, value)
  self.temp.cleanup()

 def rewrite_parent(self, value=None, raw=None):
  if self.parent.exists():
   self.parent.chmod(0o644)
  self.parent.write_bytes(raw if raw is not None else json.dumps(value, indent=2).encode())
  self.parent.chmod(0o444)
  m._VENDOR_EXAMPLE_PARENT = m.rec(self.parent)

 def replace_leaf(self, raw):
  self.leaf.write_bytes(raw)
  m._VENDOR_EXAMPLE_LEAF = m.rec(self.leaf)
  self.rows[15] = copy.deepcopy(m._VENDOR_EXAMPLE_LEAF)
  self.rewrite_parent(self.rows)

 def observe(self, receipt=None, parent=None, trail=("15",), module="default_workflow_integration"):
  return self.scope.edge(receipt or m._VENDOR_EXAMPLE_LEAF,
                         str(self.parent) if parent is None else parent, trail, module)

 def test_vendor01_exact_data_copy_and_alias_preserve_original_permission(self):
  before = m.stable_metadata(self.leaf)
  edge = self.observe()
  self.assertTrue(self.scope.require_complete(True))
  proof = self.scope.proof()
  aliases = self.scope.alias_index()["aliases"]
  self.assertEqual(edge["role"], m._VENDOR_EXAMPLE_ROLE)
  self.assertEqual(m.stable_metadata(self.leaf), before)
  self.assertEqual(self.leaf.stat().st_mode & 0o777, 0o664)
  self.assertEqual(Path(edge["physical"]["path"]).read_bytes(), self.raw)
  self.assertEqual(Path(edge["physical"]["path"]).stat().st_mode & 0o777, 0o444)
  self.assertEqual(Path(edge["physical"]["path"]).suffix, ".txt")
  self.assertEqual(aliases, [dict(original=m._VENDOR_EXAMPLE_LEAF, archived=edge["physical"],
                                status="READONLY_BYTE_IDENTICAL_ALIAS", role=m._VENDOR_EXAMPLE_ROLE)])
  self.assertEqual(proof["vendor_stream_record_n"], 52)
  self.assertFalse(proof["receipt_children_interpreted"])
  self.assertFalse(proof["public_source_or_configuration_promoted"])

 def test_vendor02_required_observation_cannot_be_omitted(self):
  with self.assertRaises(ValueError):
   self.scope.require_complete(True)
  self.assertFalse(self.scope.require_complete(False))
  self.assertFalse((self.out / "opaque_vendor_example_bytes").exists())

 def test_vendor03_parent_field_module_and_trail_types_are_exact(self):
  variants = [
   {"parent": str(self.root / "other.json")},
   {"trail": ("14",)}, {"trail": ("15", "extra")}, {"trail": [15]}, {"trail": ["15"]},
   {"module": "final_delivery_tools"}, {"parent": None, "trail": ()},
  ]
  for variant in variants:
   with self.subTest(variant=variant), self.assertRaises(ValueError):
    self.observe(**variant)

 def test_vendor04_leaf_fulltuple_forks_and_samebytes_differentpath_rejected(self):
  for field, value in (("path", str(self.root / "other.json")), ("bytes", 1), ("sha256", "0" * 64)):
   wrong = dict(m._VENDOR_EXAMPLE_LEAF)
   wrong[field] = value
   with self.subTest(field=field), self.assertRaises(ValueError):
    self.observe(receipt=wrong)
  self.assertIsNone(self.scope.edge(r(p=str(self.root / "ordinary.json")), None, (), "ordinary"))

 def test_vendor05_every_repeated_occurrence_is_authorized_before_any_seen_cache(self):
  self.observe()
  self.observe()
  self.assertEqual(self.scope.proof()["authorized_observation_n"], 2)
  with self.assertRaises(ValueError):
   self.observe(parent=str(self.root / "new_parent.json"))
  with self.assertRaises(ValueError):
   self.observe(module="scientific_report")
  self.assertEqual(self.scope.observed, 2)

 def test_vendor06_data_leaf_cannot_be_declared_public_source(self):
  value = plan()
  value["modules"][0]["sources"] = [dict(receipt=m._VENDOR_EXAMPLE_LEAF, repository_relative="demo.json")]
  with self.assertRaises(ValueError):
   m.module_plan(value)

 def test_vendor07_data_leaf_cannot_be_declared_direct_seed(self):
  value = plan()
  value["modules"][0]["seeds"] = [m._VENDOR_EXAMPLE_LEAF]
  with self.assertRaises(ValueError):
   m.module_plan(value)
  with self.assertRaises(ValueError):
   self.scope.edge(m._VENDOR_EXAMPLE_LEAF, None, (), "default_workflow_integration")

 def test_vendor08_data_leaf_cannot_be_gate_or_context_seed(self):
  value = plan()
  value["modules"][0]["gate"]["receipt"] = m._VENDOR_EXAMPLE_LEAF
  with self.assertRaises(ValueError):
   m.module_plan(value)
  value = plan()
  value["context_parent_seeds"] = [m._VENDOR_EXAMPLE_LEAF]
  with self.assertRaises(ValueError):
   m.module_plan(value)

 def test_vendor09_plan_alias_cannot_promote_or_redirect_data_scope(self):
  for field in ("logical", "physical"):
   value = plan()
   alias = dict(logical=r(), physical=r())
   alias[field] = m._VENDOR_EXAMPLE_LEAF
   value["aliases"] = [alias]
   with self.subTest(field=field), self.assertRaises(ValueError):
    m.module_plan(value)

 def test_vendor10_parent_row_count_and_exact_row_shape_are_required(self):
  for mutation in ("missing", "extra_field"):
   rows = copy.deepcopy(self.rows)
   if mutation == "missing":
    rows.pop()
   else:
    rows[0]["extra"] = True
   self.rewrite_parent(rows)
   with self.subTest(mutation=mutation), self.assertRaises(ValueError):
    self.observe()

 def test_vendor11_parent_row15_identity_cannot_be_substituted(self):
  for field, value in (("path", str(self.root / "wrong.json")), ("bytes", 2), ("sha256", "0" * 64)):
   rows = copy.deepcopy(self.rows)
   rows[15][field] = value
   self.rewrite_parent(rows)
   with self.subTest(field=field), self.assertRaises(ValueError):
    self.observe()

 def test_vendor12_duplicate_or_unsafe_parent_inventory_receipts_rejected(self):
  rows = copy.deepcopy(self.rows)
  rows[0] = copy.deepcopy(rows[1])
  self.rewrite_parent(rows)
  with self.assertRaises(ValueError):
   self.observe()
  rows = copy.deepcopy(self.rows)
  rows[0]["path"] = str(self.root / ".." / "outside.py")
  self.rewrite_parent(rows)
  with self.assertRaises(ValueError):
   self.observe()

 def test_vendor13_parent_json_duplicate_and_nonfinite_values_rejected(self):
  for raw in (b'[{"path":"x","path":"y"}]', b'[NaN]', b'[Infinity]', b'[-Infinity]'):
   self.rewrite_parent(raw=raw)
   with self.subTest(raw=raw), self.assertRaises(ValueError):
    self.observe()

 def test_vendor14_stream_requires_exact52_nonblank_records(self):
  for raw in (b"\n".join(self.raw.splitlines()[:-1]) + b"\n", self.raw + b"\n", self.raw + self.raw.splitlines()[0] + b"\n"):
   self.replace_leaf(raw)
   with self.subTest(length=len(raw)), self.assertRaises(ValueError):
    self.observe()

 def test_vendor15_stream_requires_prefix_dict_and_only_documented_types(self):
  rows = self.raw.splitlines()
  variants = [
   b"OTHER " + rows[0][5:],
   b'DLLL {"type":"OTHER"}',
   b'DLLL {"type":true}',
   b'DLLL {"type":{}}',
   b'DLLL ["LOG"]',
   b'DLLL {"type":"LOG"}',
  ]
  for first in variants:
   self.replace_leaf(b"\n".join([first] + rows[1:]) + b"\n")
   with self.subTest(first=first), self.assertRaises(ValueError):
    self.observe()

 def test_vendor16_stream_json_duplicate_keys_are_fatal(self):
  rows = self.raw.splitlines()
  rows[1] = b'DLLL {"type":"LOG","type":"LOG"}'
  self.replace_leaf(b"\n".join(rows) + b"\n")
  with self.assertRaises(ValueError):
   self.observe()

 def test_vendor17_stream_nonfinite_numbers_are_fatal(self):
  for token in (b"NaN", b"Infinity", b"-Infinity", b"1e999"):
   rows = self.raw.splitlines()
   rows[1] = b'DLLL {"type":"LOG","value":' + token + b'}'
   self.replace_leaf(b"\n".join(rows) + b"\n")
   with self.subTest(token=token), self.assertRaises(ValueError):
    self.observe()

 def test_vendor18_invalid_utf8_and_credential_text_are_not_preserved(self):
  credential = b"api_" + b"key=" + b"abcdefghijklmnop"
  secret_raw = self.raw.replace(b'"synthetic_only": 0', b'"synthetic_only": "' + credential + b'"')
  for raw in (b"\xff" + self.raw, secret_raw):
   self.replace_leaf(raw)
   with self.subTest(raw_prefix=raw[:20]), self.assertRaises((ValueError, UnicodeDecodeError)):
    self.observe()
  self.assertFalse((self.out / "opaque_vendor_example_bytes").exists())

 def test_vendor19_parent_drift_after_observation_is_fatal(self):
  self.observe()
  self.parent.chmod(0o644)
  with self.assertRaises(ValueError):
   self.scope.readback()
  self.assertFalse((self.out / "acceptance.json").exists())

 def test_vendor20_original_leaf_drift_is_not_hidden_by_readonly_copy(self):
  self.observe()
  self.leaf.write_bytes(self.raw + b"changed")
  with self.assertRaises(ValueError):
   self.scope.readback()

 def test_vendor21_opaque_copy_writable_or_byte_drift_fails_after_output(self):
  self.observe()
  proof = m.dump(self.out / "synthetic_proof.json", self.scope.proof())
  self.assertTrue(self.scope.readback())
  copied = Path(self.scope.copy_receipt["path"])
  copied.chmod(0o644)
  with self.assertRaises(ValueError):
   self.scope.readback()
  copied.write_bytes(b"changed")
  copied.chmod(0o444)
  with self.assertRaises(ValueError):
   self.scope.readback()
  self.assertTrue(Path(proof["path"]).exists())

 def test_vendor22_preservation_is_exclusive_and_does_not_overwrite(self):
  directory = self.out / "opaque_vendor_example_bytes"
  directory.mkdir()
  sentinel = directory / "sentinel"
  sentinel.write_text("SYNTHETIC_DO_NOT_OVERWRITE")
  before = m.stable_metadata(self.leaf)
  with self.assertRaises(FileExistsError):
   self.observe()
  self.assertEqual(sentinel.read_text(), "SYNTHETIC_DO_NOT_OVERWRITE")
  self.assertEqual(m.stable_metadata(self.leaf), before)
  self.assertEqual(self.scope.observed, 0)

 def test_vendor23_fsync_failure_retains_original_and_produces_no_acceptance(self):
  before = m.stable_metadata(self.leaf)
  patch = __import__("unittest.mock", fromlist=["patch"]).patch
  with patch.object(m.os, "fsync", side_effect=OSError("SYNTHETIC_FSYNC_FAILURE")):
   with self.assertRaisesRegex(OSError, "SYNTHETIC_FSYNC_FAILURE"):
    self.observe()
  self.assertEqual(m.stable_metadata(self.leaf), before)
  self.assertIsNone(self.scope.copy_receipt)
  self.assertEqual(self.scope.observed, 0)
  self.assertFalse((self.out / "acceptance.json").exists())

 def test_vendor24_ordinary_json_parser_and_upstream_dictionary_remain_unchanged(self):
  ordinary = self.root / "UPSTREAM.json"
  ordinary.write_text('{"source":"SYNTHETIC_UPSTREAM"}')
  self.assertEqual(m.read(ordinary), {"source": "SYNTHETIC_UPSTREAM"})
  ordinary.write_text('DLLL {"type":"LOG"}\n')
  with self.assertRaises(json.JSONDecodeError):
   m.read(ordinary)
  with self.assertRaises(json.JSONDecodeError):
   m.read(self.leaf)


 def test_vendor25_saved_full_proof_and_alias_forks_are_rejected(self):
  self.observe()
  allocation = {"job_id": "SYNTHETIC_CPU", "allocated_gpus": 0}
  aliases = self.scope.alias_index()
  alias_receipt = m.dump(self.out / "vendor_example_opaque_aliases.json", aliases)
  proof = dict(self.scope.proof(), allocation=allocation, exact_alias_index=alias_receipt)
  self.assertTrue(m.verify_vendor_example_preservation(proof, aliases, allocation))
  for field, value in (("schema", "OTHER"), ("authorized_observation_n", True),
                       ("vendor_stream_record_n", 51), ("source_field", ["14"]),
                       ("receipt_children_interpreted", True),
                       ("public_source_or_configuration_promoted", True)):
   fork = copy.deepcopy(proof)
   fork[field] = value
   with self.subTest(field=field), self.assertRaises(ValueError):
    m.verify_vendor_example_preservation(fork, aliases, allocation)
  fork = copy.deepcopy(aliases)
  fork["aliases"][0]["status"] = "OTHER"
  with self.assertRaises(ValueError):
   m.verify_vendor_example_preservation(proof, fork, allocation)
  with self.assertRaises(ValueError):
   m.verify_vendor_example_preservation(proof, aliases, {"job_id": "OTHER"})

  for name, path, readonly in (
      ("parent", self.parent, True),
      ("original", self.leaf, False),
      ("preserved", Path(self.scope.copy_receipt["path"]), True),
  ):
   hardlink = self.root / ("SYNTHETIC_HARDLINK_" + name)
   m.os.link(path, hardlink)
   try:
    with self.subTest(single_link_input=name), self.assertRaisesRegex(ValueError, "single-link"):
     self.scope._regular(path, readonly)
   finally:
    hardlink.unlink()


class FiniteWorkerControlContracts(unittest.TestCase):
    """Synthetic normal-JSON CONTROL fixtures; never read actual historical workers."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        names = ("R", "_WORKER_BASE", "_WORKER_CLOSURE", "_WORKER_PARENTS", "_WORKER_TABLE")
        self.saved = {name: getattr(m, name) for name in names}
        m.R = self.root
        self.out = self.root / "out"
        self.out.mkdir()
        self.parents = [self.root / "validation" / "raw.json",
                        self.root / "downstream" / "raw.json"]
        self.canonical = []
        for slot in range(22):
            path = self.root / "canonical" / ("worker_%02d" % slot) / "worker.json"
            path.parent.mkdir(parents=True)
            content = {"synthetic": slot,
                       "source": r(str(self.root / "synthetic_code.py"), 7, "a" * 64),
                       "nested": [{"result": r(str(self.root / "synthetic_model.pdb"), 9, "b" * 64)}]}
            path.write_text(json.dumps(content))
            path.chmod(0o664)
            self.canonical.append(path)
        self.rows = []
        for index in range(23):
            parent_slot = 0 if index == 0 else 1
            job = 0 if index == 0 else index - 1
            slot = 0 if index == 0 else index - 1
            link = self.parents[parent_slot].parent / "raw_view" / ("worker_%02d" % job)
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(self.canonical[slot].parent, target_is_directory=True)
            logical = dict(m.rec(self.canonical[slot]), path=str(link / "worker.json"))
            self.rows.append(dict(index=index, logical=logical,
                                  canonical=m.rec(self.canonical[slot]),
                                  parent=None, field=["jobs", str(job), "worker"],
                                  link_path=str(link), link_text=str(self.canonical[slot].parent),
                                  base_edge=None))
        self.base_path = self.root / "base.json"
        self.closure_path = self.root / "closure.json"
        self.refresh_authority()
        self.scope = self.new_scope()

    def tearDown(self):
        for name, value in self.saved.items():
            setattr(m, name, value)
        self.temp.cleanup()

    def write_control(self, path, obj):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.unlink()
        path.write_text(json.dumps(obj, allow_nan=False))
        path.chmod(0o444)

    def refresh_authority(self):
        parent_values = [{"jobs": [{"worker": copy.deepcopy(self.rows[0]["logical"])}]},
                         {"jobs": [{"worker": copy.deepcopy(row["logical"])}
                                   for row in self.rows[1:]]}]
        for path, value in zip(self.parents, parent_values):
            self.write_control(path, value)
            path.chmod(0o664)
        m._WORKER_PARENTS = [m.rec(path) for path in self.parents]
        for row in self.rows:
            parent = m._WORKER_PARENTS[0 if row["index"] == 0 else 1]
            row["parent"] = copy.deepcopy(parent)
            row["base_edge"] = dict(receipt=copy.deepcopy(row["logical"]),
                                    parent=parent["path"], field=list(row["field"]),
                                    physical=copy.deepcopy(row["logical"]),
                                    resolution_basis="EXACT_ORIGINAL",
                                    relative_context=None, current_recovered_relative_context=None,
                                    finite_exact_source_alias_context=None,
                                    role="EXACT_TEXT_RECEIPT_READBACK")
        self.write_control(self.closure_path,
                           {"schema": "benchmark-source-receipt-closure.v1",
                            "edges": [row["base_edge"] for row in self.rows]})
        m._WORKER_CLOSURE = m.rec(self.closure_path)
        self.write_control(self.base_path, {"source_closure": m._WORKER_CLOSURE})
        m._WORKER_BASE = m.rec(self.base_path)
        m._WORKER_TABLE = copy.deepcopy(self.rows)

    def new_scope(self):
        return m.FiniteWorkerControlAliases(self.out, m._WORKER_BASE, m._WORKER_CLOSURE)

    def observe(self, index=0, receipt=None, parent=None, trail=None,
                module="default_workflow_integration"):
        row = m._WORKER_TABLE[index]
        return self.scope.edge(receipt if receipt is not None else row["logical"],
                               row["parent"]["path"] if parent is None else parent,
                               tuple(row["field"]) if trail is None else trail, module)

    def complete(self):
        edges = [self.observe(index) for index in range(23)]
        self.assertTrue(self.scope.require_complete())
        return edges

    def saved_proof(self):
        self.complete()
        allocation = {"job_id": "50001", "allocated_CPUs": 1, "allocated_gpus": 0}
        aliases = self.scope.alias_index()
        pointer = m.dump(self.out / "finite_worker_control_aliases.json", aliases)
        proof = dict(self.scope.proof(), allocation=allocation, exact_alias_index=pointer)
        return proof, aliases, allocation

    def replace_worker(self, slot, raw):
        self.canonical[slot].write_bytes(raw)
        for row in self.rows:
            if row["canonical"]["path"] == str(self.canonical[slot]):
                row["canonical"] = m.rec(self.canonical[slot])
                row["logical"] = dict(row["canonical"], path=row["logical"]["path"])
        self.refresh_authority()
        self.scope = self.new_scope()

    def test_worker01_all23_contexts_and22_copies_are_actual_and_normal_json(self):
        before = [m.stable_metadata(path) for path in self.canonical]
        edges = self.complete()
        self.assertEqual(len(self.scope.observations), 23)
        self.assertEqual(len(self.scope.copies), 22)
        self.assertEqual(before, [m.stable_metadata(path) for path in self.canonical])
        self.assertEqual(len({edge["physical"]["path"] for edge in edges}), 22)
        self.assertTrue(all(Path(edge["physical"]["path"]).suffix == ".json" for edge in edges))
        self.assertTrue(all(edge["receipt_children_interpreted"] for edge in edges))
        self.assertTrue(all(not edge["source_or_scientific_promotion"] for edge in edges))

    def test_worker02_repeat_is_authorized_before_seen_and_copy_dedup(self):
        edge = self.observe()
        before = m.stable_metadata(edge["physical"]["path"])
        again = self.observe()
        self.assertEqual(edge, again)
        self.assertEqual(len(self.scope.observations), 2)
        self.assertEqual(m.stable_metadata(edge["physical"]["path"]), before)
        self.assertEqual(len(self.scope.copies), 1)

    def test_worker03_wrong_parent_fails_before_and_after_valid_occurrence(self):
        for already_seen in (False, True):
            if already_seen:
                self.observe()
            with self.subTest(already_seen=already_seen), self.assertRaises(ValueError):
                self.observe(parent=str(self.root / "wrong_parent.json"))

    def test_worker04_exact_field_and_tuple_trail_type_are_mandatory(self):
        for trail in (("jobs", "1", "worker"), ("worker",), ["jobs", "0", "worker"], ()):
            with self.subTest(trail=trail), self.assertRaises(ValueError):
                self.observe(trail=trail)
        self.assertFalse(self.scope.directory.exists())

    def test_worker05_other_modules_cannot_reuse_a_valid_worker_identity(self):
        for module in sorted(m.REQUIRED_MODULES - {"default_workflow_integration"}) + ["UNKNOWN"]:
            with self.subTest(module=module), self.assertRaises(ValueError):
                self.observe(module=module)
        self.assertFalse(self.scope.directory.exists())

    def test_worker06_full_logical_path_size_and_sha_are_fixed(self):
        for field, value in (("path", str(self.root / "unknown_worker.json")),
                             ("bytes", 0), ("sha256", "0" * 64)):
            receipt = copy.deepcopy(m._WORKER_TABLE[0]["logical"])
            receipt[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.observe(receipt=receipt)

    def test_worker07_same_fingerprint_unknown_path_never_gets_alias_permission(self):
        self.observe()
        receipt = dict(m._WORKER_TABLE[0]["logical"], path=str(self.root / "same_bytes_other.json"))
        with self.assertRaises(ValueError):
            self.observe(receipt=receipt)
        self.assertEqual(len(self.scope.observations), 1)

    def test_worker08_known_canonical_full_tuple_keeps_only_ordinary_route(self):
        canonical = m._WORKER_TABLE[0]["canonical"]
        self.assertFalse(m._worker_related(canonical))
        self.assertIsNone(self.scope.edge(canonical, "UNCHANGED_ORDINARY_PARENT",
                                         ("worker",), "formal_common_review"))
        for field, value in (("bytes", 0), ("sha256", "0" * 64)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                m._worker_related(dict(canonical, **{field: value}))
        self.assertFalse(self.scope.directory.exists())

    def test_worker09_direct_source_gate_seed_context_or_plan_alias_is_forbidden(self):
        receipt = m._WORKER_TABLE[0]["logical"]
        for category in ("source", "gate", "seed", "context", "alias"):
            value = plan()
            module = value["modules"][0]
            if category == "source":
                module["sources"][0]["receipt"] = receipt
            elif category == "gate":
                module["gate"]["receipt"] = receipt
            elif category == "seed":
                module["seeds"] = [receipt]
            elif category == "context":
                value["context_parent_seeds"] = [receipt]
            else:
                value["aliases"] = [{"logical": receipt, "physical": receipt}]
            with self.subTest(category=category), self.assertRaises(ValueError):
                m.module_plan(value)

    def test_worker10_unrelated_ordinary_json_does_not_enter_finite_scope(self):
        ordinary = r(str(self.root / "ordinary.json"), 2, "c" * 64)
        self.assertIsNone(self.scope.edge(ordinary, None, (), "scientific_report"))
        self.assertFalse(self.scope.directory.exists())
        self.assertFalse(m._worker_related(ordinary))

    def test_worker11_missing_one_context_cannot_be_filled_by_shared_copy(self):
        for index in range(1, 23):
            self.observe(index)
        self.assertEqual(len(self.scope.copies), 22)
        with self.assertRaises(ValueError):
            self.scope.require_complete()

    def test_worker12_shared_canonical_still_requires_both_logical_occurrences(self):
        first = self.observe(0)
        second = self.observe(1)
        self.assertNotEqual(first["receipt"]["path"], second["receipt"]["path"])
        self.assertEqual(first["physical"], second["physical"])
        self.assertEqual(self.scope.seen_indices, {0, 1})
        self.assertEqual(len(self.scope.observations), 2)

    def test_worker13_table_slot_count_and_duplicate_indices_are_rejected(self):
        original = m._WORKER_TABLE
        try:
            for value in (original[:-1], original + [copy.deepcopy(original[0])]):
                m._WORKER_TABLE = value
                with self.subTest(count=len(value)), self.assertRaises(ValueError):
                    m._worker_authority()
        finally:
            m._WORKER_TABLE = original

    def test_worker14_pinned_base_edge_fields_cannot_be_forked(self):
        closure = json.loads(self.closure_path.read_text())
        closure["edges"][0]["field"] = ["jobs", "1", "worker"]
        self.write_control(self.closure_path, closure)
        m._WORKER_CLOSURE = m.rec(self.closure_path)
        self.write_control(self.base_path, {"source_closure": m._WORKER_CLOSURE})
        m._WORKER_BASE = m.rec(self.base_path)
        self.scope = self.new_scope()
        with self.assertRaisesRegex(ValueError, "BaseC worker edge"):
            self.observe()

    def test_worker15_foreign_base_or_closure_cannot_activate_exception(self):
        foreign = r(str(self.root / "foreign_base.json"))
        scope = m.FiniteWorkerControlAliases(self.out, foreign, m._WORKER_CLOSURE)
        row = m._WORKER_TABLE[0]
        with self.assertRaises(ValueError):
            scope.edge(row["logical"], row["parent"]["path"], tuple(row["field"]), m._WORKER_MODULE)
        with self.assertRaises(ValueError):
            m.FiniteWorkerControlAliases(self.out, m._WORKER_BASE, foreign)
        self.assertFalse(scope.require_complete())

    def test_worker16_parent_full_byte_pin_is_not_path_only_authority(self):
        path = self.parents[0]
        path.write_text(path.read_text() + " ")
        with self.assertRaisesRegex(ValueError, "authority/control bytes"):
            self.observe()
        self.assertFalse(self.scope.directory.exists())

    def test_worker17_parent_field_full_receipt_is_checked_independently(self):
        parent = json.loads(self.parents[0].read_text())
        parent["jobs"][0]["worker"]["sha256"] = "0" * 64
        self.parents[0].write_text(json.dumps(parent))
        changed = m.rec(self.parents[0])
        m._WORKER_PARENTS[0] = changed
        m._WORKER_TABLE[0]["parent"] = changed
        with self.assertRaisesRegex(ValueError, "raw parent worker field"):
            self.observe()

    def test_worker18_duplicate_nonfinite_and_overflow_worker_json_are_rejected(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e9999}'):
            self.replace_worker(0, raw)
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                self.observe()
        self.assertFalse(self.scope.directory.exists())

    def test_worker19_worker_invalid_utf8_or_non_json_never_becomes_opaque(self):
        for raw in (b"\xff", b'DLLL {"type":"LOG"}\n', b"not JSON"):
            self.replace_worker(0, raw)
            with self.subTest(raw=raw), self.assertRaises((ValueError, UnicodeError)):
                self.observe()
        self.assertFalse(self.scope.directory.exists())

    def test_worker20_canonical_byte_drift_is_not_hidden_by_copy(self):
        self.observe()
        self.canonical[0].write_bytes(b'{"changed":true}')
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_worker21_exact_link_text_and_link_metadata_are_bound(self):
        self.observe()
        link = Path(m._WORKER_TABLE[0]["link_path"])
        link.unlink()
        link.symlink_to(self.canonical[1].parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_worker22_canonical_symlink_or_extra_ancestor_is_not_permitted(self):
        canonical = self.canonical[0]
        moved = canonical.with_name("actual_worker.json")
        canonical.rename(moved)
        canonical.symlink_to(moved)
        with self.assertRaisesRegex(ValueError, "(?i)symlink"):
            self.observe()
        canonical.unlink()
        moved.rename(canonical)
        raw_view = Path(m._WORKER_TABLE[0]["link_path"]).parent
        actual_view = raw_view.with_name("actual_raw_view")
        raw_view.rename(actual_view)
        raw_view.symlink_to(actual_view, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "(?i)symlink"):
            self.observe()
        self.assertFalse(self.scope.directory.exists())

    def test_worker23_real_hardlinks_reject_parents_canonical_and_owned_copies(self):
        for label, path, readonly in (("parent", self.parents[0], False),
                                     ("canonical", self.canonical[0], False)):
            alias = self.root / ("hardlink_" + label)
            m.os.link(path, alias)
            try:
                with self.subTest(label=label), self.assertRaisesRegex(ValueError, "single-link"):
                    m._worker_regular(path, readonly)
            finally:
                alias.unlink()
        edge = self.observe()
        path = Path(edge["physical"]["path"])
        alias = self.root / "hardlink_copy"
        m.os.link(path, alias)
        try:
            with self.assertRaisesRegex(ValueError, "single-link"):
                self.scope.readback()
        finally:
            alias.unlink()

    def test_worker24_parent_and_base_metadata_drift_are_detected_after_observation(self):
        self.observe()
        self.parents[0].chmod(0o444)
        with self.assertRaisesRegex(ValueError, "permission"):
            self.scope.readback()
        self.parents[0].chmod(0o664)
        self.closure_path.chmod(0o644)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_worker25_owned_copy_writable_or_changed_after_output_is_fatal(self):
        edge = self.observe()
        path = Path(edge["physical"]["path"])
        path.chmod(0o644)
        with self.assertRaises(ValueError):
            self.scope.readback()
        path.write_text('{"changed":true}')
        path.chmod(0o444)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_worker26_exclusive_directory_and_file_collisions_never_overwrite(self):
        self.observe(0)
        row = m._WORKER_TABLE[2]
        collision = self.scope.directory / self.scope._copy_name(row)
        collision.write_text("SYNTHETIC_SENTINEL")
        with self.assertRaises(FileExistsError):
            self.observe(2)
        self.assertEqual(collision.read_text(), "SYNTHETIC_SENTINEL")
        self.assertEqual(len(self.scope.observations), 1)
        other_out = self.root / "other_out"
        other_out.mkdir()
        other = m.FiniteWorkerControlAliases(other_out, m._WORKER_BASE, m._WORKER_CLOSURE)
        other.directory.mkdir()
        sentinel = other.directory / "SYNTHETIC_DIRECTORY_SENTINEL"
        sentinel.write_text("DO_NOT_OVERWRITE")
        row = m._WORKER_TABLE[0]
        with self.assertRaises(FileExistsError):
            other.edge(row["logical"], row["parent"]["path"], tuple(row["field"]), m._WORKER_MODULE)
        self.assertEqual(sentinel.read_text(), "DO_NOT_OVERWRITE")
        self.assertFalse(other.observations)

    def test_worker27_fsync_error_retains_original_and_never_accepts(self):
        before = m.stable_metadata(self.canonical[0])
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        with patch.object(m.os, "fsync", side_effect=OSError("SYNTHETIC_FSYNC_FAILURE")):
            with self.assertRaisesRegex(OSError, "SYNTHETIC_FSYNC_FAILURE"):
                self.observe()
        self.assertEqual(m.stable_metadata(self.canonical[0]), before)
        self.assertFalse(self.scope.observations)
        self.assertFalse((self.out / "acceptance.json").exists())

    def test_worker28_saved_full_proof_alias_and_allocation_are_strict(self):
        proof, aliases, allocation = self.saved_proof()
        self.assertTrue(m.verify_finite_worker_preservation(proof, aliases, allocation))
        for field, value in (("schema", "OTHER"), ("fixed_context_n", True),
                             ("canonical_target_n", 21), ("observed_context_slots", []),
                             ("normal_JSON_receipt_children_retained", False)):
            fork = copy.deepcopy(proof)
            fork[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.verify_finite_worker_preservation(fork, aliases, allocation)
        fork = copy.deepcopy(aliases)
        fork["aliases"][0]["status"] = "OTHER"
        with self.assertRaises(ValueError):
            m.verify_finite_worker_preservation(proof, fork, allocation)
        fork = copy.deepcopy(proof)
        fork["exact_alias_index"] = dict(fork["exact_alias_index"], path=str(self.root / "other_index.json"))
        with self.assertRaises(ValueError):
            m.verify_finite_worker_preservation(fork, aliases, allocation)
        fork = copy.deepcopy(proof)
        fork["source_metadata_before"][0]["metadata"]["link"]["nlink"] = True
        with self.assertRaises(ValueError):
            m.verify_finite_worker_preservation(fork, aliases, allocation)
        fork = copy.deepcopy(proof)
        fork["observations"][1]["index"] = True
        with self.assertRaises(ValueError):
            m.verify_finite_worker_preservation(fork, aliases, allocation)
        with self.assertRaises(ValueError):
            m.verify_finite_worker_preservation(proof, aliases, {"job_id": "OTHER"})
        directory = self.scope.directory
        directory.chmod(0o755)
        synchronized = copy.deepcopy(proof)
        synchronized["copy_directory_metadata"] = m.stable_metadata(directory)
        try:
            with self.assertRaisesRegex(ValueError, "readonly0555"):
                m.verify_finite_worker_preservation(synchronized, aliases, allocation)
        finally:
            directory.chmod(0o555)

    def test_worker29_all_nested_code_and_data_receipts_keep_original_parent(self):
        edge = self.observe()
        obj = self.scope.parse(m._WORKER_TABLE[0]["logical"], edge)
        children = list(m.receipt_edges(obj))
        self.assertEqual(len(children), 2)
        self.assertEqual({Path(child["path"]).suffix for child, trail in children}, {".py", ".pdb"})
        queued = [(child, edge["receipt"]["path"], trail, edge["module"]) for child, trail in children]
        self.assertTrue(all(parent == m._WORKER_TABLE[0]["logical"]["path"] for child, parent, trail, module in queued))
        self.assertTrue(all(parent != edge["physical"]["path"] for child, parent, trail, module in queued))

    def test_worker30_proof_or_other_parent_cannot_reenter_after_complete_seen(self):
        self.complete()
        count = len(self.scope.observations)
        with self.assertRaises(ValueError):
            self.observe(parent=str(self.out / "finite_worker_control_proof.json"))
        self.assertEqual(len(self.scope.observations), count)

    def test_worker31_ordinary_canonical_json_children_remain_intact_without_alias_scope(self):
        receipt = m._WORKER_TABLE[0]["canonical"]
        self.assertFalse(m._worker_related(receipt))
        self.assertEqual(Path(m.verify(receipt)).read_bytes(), self.canonical[0].read_bytes())
        children = list(m.receipt_edges(m.read(receipt["path"])))
        self.assertEqual(len(children), 2)
        self.assertIsNone(self.scope.edge(receipt, "EXISTING_CANONICAL_PARENT", ("worker",), "formal_common_review"))
        with self.assertRaises(ValueError):
            m.reject_worker_declaration(receipt)
        self.assertFalse(self.scope.directory.exists())

    def test_worker32_directory_universe_and_afteroutput_metadata_drift_fail(self):
        self.complete()
        self.scope.directory.chmod(0o755)
        extra = self.scope.directory / "unexpected.json"
        extra.write_text("{}")
        self.scope.directory.chmod(0o555)
        with self.assertRaises(ValueError):
            self.scope.readback()
        self.assertFalse((self.out / "acceptance.json").exists())



_MAPPING_FIXTURE_TEMPLATES = copy.deepcopy(m._FIXED_HISTORY_MAPPING_PARENTS)


def install_fixed_mapping_fixture(case, base, family, operative=False):
    """Owned TMP controls; old single-slot fixtures keep their prior queue scope."""
    root = case.base_path.parent
    provenance = dict(
        producer_executed_source=case.write(root / "mapping_producer.py", b"# MAPPING_SOURCE_COPY_ONLY\n"),
        producer_actual_software_gate=case.write(root / "mapping_software.json", b'{"status":"SYNTHETIC_MAPPING_GATE"}\n'),
        source_graph_selector=case.write(root / "mapping_selector.py", b"# MAPPING_GRAPH_COPY_ONLY\n"))
    m._FIXED_HISTORY_MAPPING_PROVENANCE = provenance
    entries = copy.deepcopy(_MAPPING_FIXTURE_TEMPLATES)
    history = base["original_failure_history"]
    definition_names = (
        ("inventory13299", "_HISTORY"), ("archive13298", "_ARCHIVE_PARENT_HISTORY"),
        ("relative13295", "_RELATIVE_DIAGNOSTIC_HISTORY"), ("parent13290", "_PARENT_DIAGNOSTIC_HISTORY"))
    for slot, entry in enumerate(entries):
        lineage = [dict(provenance["producer_actual_software_gate"]) for unused in range(8)]
        for selected_family, prefix in definition_names:
            field = getattr(m, prefix + "_FIELD")
            leaf = getattr(m, prefix + "_LEAF")
            target_slot, index = m._FIXED_HISTORY_LINEAGE_SLOTS[selected_family]
            if target_slot == slot and history.get(field[1]) == leaf:
                lineage[index] = dict(leaf)
        # Existing 284 single-slot fixtures did not recurse three Map histories.
        # This is a fixture-only table value, never a production METADATA_ONLY change.
        if not operative:
            entry["schema"] = "benchmark-source-receipt-closure.v1"
        obj = dict(schema=entry["schema"], status=entry["status"],
                   original_failure_history=copy.deepcopy(history),
                   accepted_lineage_receipts=lineage, **provenance)
        entry["receipt"] = case.write(root / ("fixed_mapping_" + str(slot) + ".json"),
                                      json.dumps(obj, allow_nan=False).encode("utf-8"))
        base[entry["base_field"]] = dict(entry["receipt"])
    m._FIXED_HISTORY_MAPPING_PARENTS = tuple(entries)
    return base


class InventoryHistoryDataContracts(unittest.TestCase):
    """Synthetic own-byte fixtures; no live member/SCI source is opened by these cases."""

    private_names = ("_FIXED_HISTORY_MAPPING_PARENTS", "_FIXED_HISTORY_MAPPING_PROVENANCE", "_HISTORY_BASE", "_HISTORY_AUTHORITY", "_HISTORY_LEAF",
                     "_HISTORY_PRODUCER", "_HISTORY_SOFTWARE", "_HISTORY_MANIFESTS")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_root = m.R
        self.old_private = {name: copy.deepcopy(getattr(m, name)) for name in self.private_names}
        m.R = self.root
        self.install(self.root / "case")
        self.out = self.root / "out"
        self.out.mkdir()
        self.scope = m.InventoryHistoryOpaqueLeaf(self.out, m._HISTORY_BASE)

    def tearDown(self):
        for name, value in self.old_private.items():
            setattr(m, name, value)
        m.R = self.old_root
        for path in self.root.rglob("*"):
            if path.is_dir() and not path.is_symlink():
                path.chmod(0o755)
        self.tmp.cleanup()

    @staticmethod
    def write(path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.chmod(0o644)
        path.write_bytes(raw)
        path.chmod(0o444)
        return m.rec(path)

    def install(self, root):
        root.mkdir(parents=True, exist_ok=True)
        m._HISTORY_AUTHORITY = str(m.R)
        self.producer = root / "producer.py"
        self.software = root / "software.json"
        m._HISTORY_PRODUCER = self.write(self.producer, b"SYNTHETIC_SOURCE_ONLY\n")
        m._HISTORY_SOFTWARE = self.write(self.software, b'{"status":"SYNTHETIC_SOFTWARE_HISTORY"}\n')
        manifests = []
        parents = []
        edges = []
        for slot, count in enumerate((193, 395)):
            manifest = r(str(root / ("never_open_manifest_" + str(slot) + ".json")),
                         10 + slot, str(slot + 1) * 64)
            manifests.append((manifest, count))
            members = [dict(path="never_open_relative_namespace/" + str(slot) + "/" + str(index),
                            bytes=index, sha256="a" * 64) for index in range(count)]
            parents.append(dict(parent=manifest, physical_parent=manifest,
                                parent_JSON=dict(member_count=count, members=members)))
            edges.extend(dict(parent=manifest, field=["members", str(index)],
                              original_relative_receipt=members[index],
                              diagnostic_only_edge_skipped=True, authorization_granted=False,
                              current_canonical_child=None) for index in reversed(range(count)))
        m._HISTORY_MANIFESTS = tuple(manifests)
        self.document = dict(
            schema="source-unknown-relative-finite-inventory-diagnostic-only.v1",
            status="FINITE_UNKNOWN_RELATIVE_EDGES_COLLECTED_NO_SOURCE_ACCEPTANCE_NO_AUTHORIZATION",
            job_id="13299", failed_source_job="13297", CPU=1, GPU=0,
            source_producer=m._HISTORY_PRODUCER, software_only_gate=m._HISTORY_SOFTWARE,
            parent_count=2, edge_count=588, parents=parents, edges=edges,
            **{name: False for name in m._HISTORY_FALSE_FLAGS},
            **{name: True for name in m._HISTORY_TRUE_FLAGS})
        self.leaf = root / "diagnostic.json"
        self.base_path = root / "base.json"
        self.replace_document(self.document)

    def replace_document(self, document=None, raw=None, base_overlay=None):
        if document is not None:
            self.document = document
        if raw is None:
            raw = json.dumps(self.document, allow_nan=False).encode("utf-8")
        self.content = raw
        m._HISTORY_LEAF = self.write(self.leaf, raw)
        history = {
            m._HISTORY_FIELD[1]: m._HISTORY_LEAF,
            "original13297_failed_executing_source": m._HISTORY_PRODUCER,
            "actual13297_software58_only": m._HISTORY_SOFTWARE,
        }
        base = dict(base_overlay or {},
                    schema="source-delivery-refresh.v3",
                    status="CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY",
                    source_issues=0, source_staged=False, original_failure_history=history)
        base = install_fixed_mapping_fixture(self, base, "inventory13299")
        m._HISTORY_BASE = self.write(self.base_path, json.dumps(base).encode("utf-8"))
        if hasattr(self, "out") and self.out.is_relative_to(m.R):
            self.scope = m.InventoryHistoryOpaqueLeaf(self.out, m._HISTORY_BASE)

    def observe(self, receipt=None, parent=None, trail=None,
                module="default_workflow_integration"):
        return self.scope.edge(
            m._HISTORY_LEAF if receipt is None else receipt,
            m._HISTORY_BASE["path"] if parent is None else parent,
            m._HISTORY_FIELD if trail is None else trail, module)

    def saved(self):
        self.observe()
        allocation = {"job_id": "50001", "allocated_CPUs": 1, "allocated_gpus": 0}
        aliases = self.scope.alias_index()
        pointer = m.dump(self.out / "inventory_history_opaque_aliases.json", aliases)
        proof = dict(self.scope.proof(), exact_alias_index=pointer, allocation=allocation)
        return proof, aliases, allocation

    def run_genuine_audit(self, invalid_after_valid=False, direct_alias=False):
        fixture = ClosureFixtureContracts("test_real_closure_preserves_old_and_accepts_new_default")
        fixture.setUp()
        saved = {name: copy.deepcopy(getattr(m, name)) for name in self.private_names}
        try:
            self.install(fixture.root / "history_case")
            original_base = m.read(fixture.p["base_acceptance"]["path"])
            self.replace_document(self.document, base_overlay=original_base)
            fixture.p["base_acceptance"] = m._HISTORY_BASE
            default = next(x for x in fixture.p["modules"] if x["role"] == "default_workflow_integration")
            default["seeds"] = [m._HISTORY_BASE]
            fixture.p["modules"] = [x for x in fixture.p["modules"] if x is not default] + [default]
            if invalid_after_valid:
                bad = fixture.meta("wrong_history_parent.json", {"wrong": m._HISTORY_LEAF})
                other = next(x for x in fixture.p["modules"] if x["role"] == "formal_common_review")
                other["seeds"] = [bad]
            if direct_alias:
                fixture.p["aliases"] = [{"logical": m._HISTORY_LEAF, "physical": m._HISTORY_LEAF}]
            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            with patch.object(m, "cpu", return_value={"job_id": "50002", "allocated_CPUs": 1,
                                                      "allocated_gpus": 0}):
                if invalid_after_valid or direct_alias:
                    with self.assertRaises(ValueError):
                        fixture.run_fixture()
                    out = fixture.root / "audit_out"
                    self.assertFalse((out / "acceptance.json").exists())
                    if invalid_after_valid:
                        self.assertTrue((out / "opaque_inventory_history_bytes").is_dir())
                        self.assertTrue((out / "typed_incomplete.json").is_file())
                    return None
                inclusion = fixture.run_fixture()
                out = fixture.root / "audit_out"
                closure = m.read(out / "source_receipt_closure_final.json")
                acceptance = m.read(out / "acceptance.json")
                self.assertEqual(inclusion["inventory_history_opaque_leaf_proof"],
                                 acceptance["inventory_history_opaque_leaf_proof"])
                self.assertEqual(closure["inventory_history_opaque_aliases"],
                                 acceptance["inventory_history_opaque_aliases"])
                producers = [x for x in closure["edges"] if x.get("receipt") == m._HISTORY_PRODUCER]
                software = [x for x in closure["edges"] if x.get("receipt") == m._HISTORY_SOFTWARE]
                self.assertTrue(producers and software)
                self.assertTrue(all(x["role"] == "EXACT_NEW_TEXT_RECEIPT_READBACK"
                                    for x in producers + software))
                self.assertTrue(any(m.fp(row["source"]) == m.fp(m._HISTORY_PRODUCER)
                                    for row in inclusion["files"]))
                self.assertFalse(any(m.fp(row["source"]) == m.fp(m._HISTORY_LEAF)
                                     for row in inclusion["files"]))
                return inclusion
        finally:
            for name, value in saved.items():
                setattr(m, name, value)
            fixture.tearDown()

    def test_history01_default_preserves_all_bytes_without_member_io(self):
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        original_open = Path.open
        allowed = {self.base_path, self.leaf} | {Path(entry["receipt"]["path"]) for entry in m._FIXED_HISTORY_MAPPING_PARENTS}

        def guarded_open(path, *args, **kwargs):
            if Path(path) not in allowed and Path(path).parent != self.scope.directory:
                raise AssertionError("Unexpected child IO: " + str(path))
            return original_open(path, *args, **kwargs)

        before = [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)]
        with patch.object(Path, "open", guarded_open):
            edge = self.observe()
            self.assertTrue(self.scope.require_complete())
        self.assertEqual(Path(edge["physical"]["path"]).read_bytes(), self.content)
        self.assertEqual(before, [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)])
        self.assertFalse(edge["receipt_children_interpreted"])
        self.assertFalse(edge["source_or_configuration_promotion"])

    def test_history02_prospective_module_is_allowed_but_not_forced_or_sufficient(self):
        self.observe(module="final_delivery_tools")
        with self.assertRaises(ValueError):
            self.scope.proof()
        self.observe()
        proof = self.scope.proof()
        self.assertEqual(proof["actual_default_observation_n"], 1)
        self.assertEqual(proof["actual_finaltools_observation_n"], 1)
        other = m.InventoryHistoryOpaqueLeaf(self.root / "other", m._HISTORY_BASE)
        other.out.mkdir()
        other.edge(m._HISTORY_LEAF, m._HISTORY_BASE["path"], m._HISTORY_FIELD,
                   "default_workflow_integration")
        self.assertEqual(other.proof()["actual_finaltools_observation_n"], 0)

    def test_history03_repeat_preserves_order_but_deduplicates_only_copy_io(self):
        first = self.observe()
        before = m.stable_metadata(first["physical"]["path"])
        second = self.observe()
        self.assertEqual(first, second)
        self.assertEqual([x["ordinal"] for x in self.scope.observations], [0, 1])
        self.assertEqual(m.stable_metadata(first["physical"]["path"]), before)

    def test_history04_wrong_parent_fails_before_and_after_valid_seen_identity(self):
        with self.assertRaises(ValueError):
            self.observe(parent=str(self.root / "wrong.json"))
        self.observe()
        with self.assertRaises(ValueError):
            self.observe(parent=str(self.out / "inventory_history_opaque_leaf_proof.json"))
        self.assertEqual(len(self.scope.observations), 1)

    def test_history05_exact_field_and_tuple_trail_are_mandatory(self):
        for trail in ((), ("original_failure_history",), list(m._HISTORY_FIELD),
                      ("other", m._HISTORY_FIELD[1])):
            with self.subTest(trail=trail), self.assertRaises(ValueError):
                self.observe(trail=trail)
        self.assertFalse(self.scope.directory.exists())

    def test_history06_unknown_module_is_rejected_even_after_valid_duplicate(self):
        self.observe()
        for module in sorted(m.REQUIRED_MODULES - set(m._HISTORY_MODULES)) + ["UNKNOWN"]:
            with self.subTest(module=module), self.assertRaises(ValueError):
                self.observe(module=module)
        self.assertEqual(len(self.scope.observations), 1)

    def test_history07_full_original_tuple_cannot_fork(self):
        for key, value in (("path", str(self.root / "unknown.json")),
                           ("bytes", 0), ("sha256", "0" * 64)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.observe(receipt=dict(m._HISTORY_LEAF, **{key: value}))
        self.assertFalse(self.scope.directory.exists())

    def test_history08_same_fingerprint_clone_path_never_gains_permission(self):
        self.observe()
        clone = dict(m._HISTORY_LEAF, path=str(self.root / "clone.json"))
        with self.assertRaises(ValueError):
            self.observe(receipt=clone)
        with self.assertRaises(ValueError):
            m.reject_inventory_history_declaration(clone)
        self.assertEqual(len(self.scope.observations), 1)

    def test_history09_direct_plan_declarations_cannot_bypass_edge_scope(self):
        for category in ("source", "gate", "seed", "context", "logical_alias", "physical_alias",
                         "allocation_closure_gate", "root_terminal_rejection_gate",
                         "base_acceptance", "library_software_acceptance", "mapper_software_acceptance"):
            value = plan()
            module = value["modules"][0]
            leaf = dict(m._HISTORY_LEAF)
            if category == "source":
                module["sources"][0]["receipt"] = leaf
            elif category == "gate":
                module["gate"]["receipt"] = leaf
            elif category == "seed":
                module["seeds"] = [leaf]
            elif category == "context":
                value["context_parent_seeds"] = [leaf]
            elif category == "logical_alias":
                value["aliases"] = [{"logical": leaf, "physical": r(str(self.root / "copy.txt"))}]
            elif category == "physical_alias":
                value["aliases"] = [{"logical": r(str(self.root / "ordinary.json")), "physical": leaf}]
            elif category in ("allocation_closure_gate", "root_terminal_rejection_gate"):
                module[category] = {"receipt": leaf}
            else:
                value[category] = leaf
            with self.subTest(category=category), self.assertRaises(ValueError):
                m.module_plan(value)

    def test_history10_unrelated_receipt_remains_on_ordinary_route(self):
        ordinary = r(str(self.root / "ordinary.json"), 2, "c" * 64)
        self.assertIsNone(self.scope.edge(ordinary, None, (), "scientific_report"))
        m.reject_inventory_history_declaration(ordinary)
        self.assertFalse(self.scope.directory.exists())

    def test_history11_zero_actual_or_foreign_base_cannot_be_accepted(self):
        with self.assertRaises(ValueError):
            self.scope.require_complete()
        scope = m.InventoryHistoryOpaqueLeaf(self.out, r(str(self.root / "foreign.json")))
        self.assertFalse(scope.require_complete())
        with self.assertRaises(ValueError):
            scope.edge(m._HISTORY_LEAF, m._HISTORY_BASE["path"], m._HISTORY_FIELD,
                       "default_workflow_integration")
        self.assertFalse(scope.directory.exists())

    def test_history12_schema_status_and_all_diagnostic_policy_flags_are_strict(self):
        for field in ("schema", "status") + m._HISTORY_FALSE_FLAGS + m._HISTORY_TRUE_FLAGS:
            document = copy.deepcopy(self.document)
            document[field] = "OTHER" if field in ("schema", "status") else not document[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.inventory_history_document_shape(document)

    def test_history13_utf8_duplicate_nonfinite_and_overflow_are_rejected(self):
        for raw in (b"\xff", b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e9999}'):
            self.replace_document(raw=raw)
            with self.subTest(raw=raw), self.assertRaises((ValueError, UnicodeDecodeError)):
                self.observe()
            self.assertFalse(self.scope.directory.exists())

    def test_history14_two_parent_and193_395_member_shapes_cannot_drift(self):
        for kind in ("parent_count", "edge_count", "parents", "manifest", "count", "members", "bool_size"):
            document = copy.deepcopy(self.document)
            if kind in ("parent_count", "edge_count"):
                document[kind] = True
            elif kind == "parents":
                document["parents"].reverse()
            elif kind == "manifest":
                document["parents"][0]["parent"] = r(str(self.root / "other_manifest.json"))
            elif kind == "count":
                document["parents"][1]["parent_JSON"]["member_count"] = 394
            elif kind == "members":
                document["parents"][0]["parent_JSON"]["members"].pop()
            else:
                document["parents"][0]["parent_JSON"]["members"][0]["bytes"] = True
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                m.inventory_history_document_shape(document)

    def test_history15_all588_ordered_history_edges_remain_non_authorizing(self):
        self.assertTrue(m.inventory_history_document_shape(self.document))
        for kind in ("order", "field", "authorization", "canonical", "missing"):
            document = copy.deepcopy(self.document)
            if kind == "order":
                document["edges"].reverse()
            elif kind == "field":
                document["edges"][0]["field"] = ["members", "0"]
            elif kind == "authorization":
                document["edges"][0]["authorization_granted"] = True
            elif kind == "canonical":
                document["edges"][0]["current_canonical_child"] = r()
            else:
                document["edges"].pop()
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                m.inventory_history_document_shape(document)

    def test_history16_full_base_authority_and_independent_edges_are_mandatory(self):
        original = self.base_path.read_bytes()
        self.base_path.chmod(0o644)
        self.base_path.write_bytes(original + b" ")
        self.base_path.chmod(0o444)
        with self.assertRaises(ValueError):
            self.observe()
        for field in (m._HISTORY_FIELD[1], "original13297_failed_executing_source",
                      "actual13297_software58_only"):
            base = json.loads(original)
            base["original_failure_history"][field] = r(str(self.root / "wrong.json"))
            m._HISTORY_BASE = self.write(self.base_path, json.dumps(base).encode())
            self.scope = m.InventoryHistoryOpaqueLeaf(self.out, m._HISTORY_BASE)
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.observe()

    def test_history17_writable_original_or_parent_is_forbidden(self):
        for path in (self.base_path, self.leaf):
            path.chmod(0o644)
            try:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    self.observe()
            finally:
                path.chmod(0o444)

    def test_history18_symlink_leaf_and_ancestor_are_not_alias_permissions(self):
        backup = self.root / "backup.json"
        self.write(backup, self.content)
        self.leaf.unlink()
        self.leaf.symlink_to(backup)
        with self.assertRaises(ValueError):
            self.observe()
        self.leaf.unlink()
        self.write(self.leaf, self.content)
        linked = self.root / "linked"
        linked.symlink_to(self.leaf.parent, target_is_directory=True)
        clone = dict(m._HISTORY_LEAF, path=str(linked / self.leaf.name))
        with self.assertRaises(ValueError):
            self.observe(receipt=clone)

    def test_history19_parent_original_and_copy_hardlinks_are_rejected(self):
        for path in (self.base_path, self.leaf):
            link = self.root / "hardlink"
            m.os.link(path, link)
            try:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    self.observe()
            finally:
                link.unlink()
        edge = self.observe()
        link = self.root / "copy_hardlink"
        m.os.link(edge["physical"]["path"], link)
        try:
            with self.assertRaises(ValueError):
                self.scope.readback()
        finally:
            link.unlink()

    def test_history20_input_metadata_drift_after_valid_output_is_detected(self):
        self.observe()
        before = m.stable_metadata(self.leaf)
        changed = before["mtime_ns"] + 2000000000
        m.os.utime(self.leaf, ns=(changed, changed))
        with self.assertRaises(ValueError):
            self.scope.readback()
        self.assertFalse((self.out / "acceptance.json").exists())

    def test_history21_changed_original_bytes_are_not_reaccepted(self):
        self.observe()
        self.leaf.chmod(0o644)
        self.leaf.write_bytes(self.content + b" ")
        self.leaf.chmod(0o444)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_history22_copy_writability_or_changed_content_is_fatal(self):
        edge = self.observe()
        path = Path(edge["physical"]["path"])
        path.chmod(0o644)
        with self.assertRaises(ValueError):
            self.scope.readback()
        path.write_bytes(b"CHANGED")
        path.chmod(0o444)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_history23_directory0555_is_independent_of_synchronized_proof_metadata(self):
        proof, aliases, allocation = self.saved()
        self.scope.directory.chmod(0o755)
        proof["copy_directory_metadata"] = m.stable_metadata(self.scope.directory)
        with self.assertRaisesRegex(ValueError, "readonly0555"):
            m.inventory_history_proof_shape(proof, aliases, allocation)
        with self.assertRaises(ValueError):
            m.verify_inventory_history_preservation(proof, aliases, allocation)

    def test_history24_exclusive_collision_and_exact_one_file_universe(self):
        self.scope.directory.mkdir()
        sentinel = self.scope.directory / "SENTINEL"
        sentinel.write_text("DO_NOT_OVERWRITE")
        with self.assertRaises(FileExistsError):
            self.observe()
        self.assertEqual(sentinel.read_text(), "DO_NOT_OVERWRITE")
        sentinel.unlink()
        self.scope.directory.rmdir()
        self.observe()
        self.scope.directory.chmod(0o755)
        (self.scope.directory / "extra.txt").write_text("EXTRA")
        self.scope.directory.chmod(0o555)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_history25_fsync_failure_never_accepts_or_changes_originals(self):
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        before = [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)]
        with patch.object(m.os, "fsync", side_effect=OSError("SYNTHETIC_FSYNC_FAILURE")):
            with self.assertRaises(OSError):
                self.observe()
        self.assertEqual(before, [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)])
        self.assertFalse(self.scope.observations)
        self.assertFalse((self.out / "acceptance.json").exists())

    def test_history26_pure_full_proof_rejects_flags_metadata_counts_and_extra_keys(self):
        proof, aliases, allocation = self.saved()
        self.assertTrue(m.inventory_history_proof_shape(proof, aliases, allocation))
        for field, value in (("schema", "OTHER"), ("authorized_observation_n", True),
                             ("embedded_observation_n", 587), ("member_paths_statted_or_opened", True),
                             ("archive_or_scientific_acceptance", True), ("unexpected", 1)):
            fork = copy.deepcopy(proof)
            fork[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.inventory_history_proof_shape(fork, aliases, allocation)
        fork = copy.deepcopy(proof)
        fork["original_metadata_before"]["inode"] = True
        with self.assertRaises(ValueError):
            m.inventory_history_proof_shape(fork, aliases, allocation)

    def test_history27_alias_pointer_status_allocation_and_context_tampering_fail(self):
        proof, aliases, allocation = self.saved()
        for kind in ("alias_status", "alias_receipt", "pointer", "allocation", "module", "order", "ordinal"):
            fork, index = copy.deepcopy(proof), copy.deepcopy(aliases)
            if kind == "alias_status":
                index["aliases"][0]["status"] = "OTHER"
            elif kind == "alias_receipt":
                index["aliases"][0]["archived"]["sha256"] = "0" * 64
            elif kind == "pointer":
                fork["exact_alias_index"]["path"] = str(self.root / "other.json")
            elif kind == "allocation":
                fork["allocation"] = {"job_id": "OTHER"}
            elif kind == "module":
                fork["observations"][0]["module"] = "scientific_report"
            elif kind == "order":
                fork["observations"][0]["field"].reverse()
            else:
                fork["observations"][0]["ordinal"] = True
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                m.inventory_history_proof_shape(fork, index, allocation)

    def test_history28_pure_validator_has_no_filesystem_or_live_source_calls(self):
        proof, aliases, allocation = self.saved()
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        with patch.object(Path, "open", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "stat", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "lstat", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "resolve", side_effect=AssertionError("NO_FS")), \
             patch.object(m, "rec", side_effect=AssertionError("NO_LIVE_SHA")), \
             patch.object(m, "verify", side_effect=AssertionError("NO_LIVE_VERIFY")):
            self.assertTrue(m.inventory_history_proof_shape(proof, aliases, allocation))

    def test_history29_production_saved_verifier_checks_current_bytes_and_index(self):
        proof, aliases, allocation = self.saved()
        self.assertTrue(m.verify_inventory_history_preservation(proof, aliases, allocation))
        pointer = Path(proof["exact_alias_index"]["path"])
        pointer.chmod(0o644)
        pointer.write_text(json.dumps({"schema": "CHANGED"}))
        pointer.chmod(0o444)
        with self.assertRaises(ValueError):
            m.verify_inventory_history_preservation(proof, aliases, allocation)

    def test_history30_genuine_audit_retains_independent_producer_software_and_data_role(self):
        self.assertIsNotNone(self.run_genuine_audit())

    def test_history31_genuine_queue_rejects_wrong_context_after_valid_seen_copy(self):
        self.run_genuine_audit(invalid_after_valid=True)

    def test_history32_genuine_audit_cannot_use_plan_alias_as_direct_data_permission(self):
        self.run_genuine_audit(direct_alias=True)



class InventoryHistoryInheritedRouteContracts(unittest.TestCase):
    """Reach nested actual audit guards with test-only row/edge isolation."""

    def run_route(self, route):
        import inspect
        fixture = ClosureFixtureContracts("test_real_closure_preserves_old_and_accepts_new_default")
        fixture.setUp()
        case = InventoryHistoryDataContracts("test_history01_default_preserves_all_bytes_without_member_io")
        saved_private = {name: copy.deepcopy(getattr(m, name)) for name in case.private_names}
        guard_calls = []
        mutation_calls = []
        original_guard = m.reject_inventory_history_declaration
        original_route = m.inherited_source_route
        try:
            case.install(fixture.root / "inherited_history_case")
            base = m.read(fixture.p["base_acceptance"]["path"])
            if route == "closure_physical_alias":
                closure = dict(schema="benchmark-source-receipt-closure.v1", edges=[
                    dict(receipt=r(str(fixture.root / "ordinary_alias.py"), 1, "c" * 64),
                         parent=str(fixture.asset / "ordinary_parent.json"), field=["source"],
                         physical=m._HISTORY_LEAF, resolution_basis="EXACT_ORIGINAL",
                         role="EXACT_TEXT_RECEIPT_READBACK")])
                closure_receipt = fixture.meta("history_alias_closure.json", closure)
                inclusion = m.read(base["source_inclusion"]["path"])
                inclusion["source_receipt_closure"] = closure_receipt
                inclusion_receipt = fixture.meta("history_alias_inclusion.json", inclusion)
                base["source_closure"] = closure_receipt
                base["source_inclusion"] = inclusion_receipt
            case.replace_document(case.document, base_overlay=base)
            fixture.p["base_acceptance"] = m._HISTORY_BASE
            default = next(x for x in fixture.p["modules"] if x["role"] == "default_workflow_integration")
            if route == "resolve":
                default["seeds"] = [m._HISTORY_BASE]
                fixture.p["modules"] = [x for x in fixture.p["modules"] if x is not default] + [default]

            def guard_spy(receipt):
                caller = inspect.currentframe().f_back
                if receipt == m._HISTORY_LEAF:
                    guard_calls.append(dict(caller=caller.f_code.co_name,
                                            r=copy.deepcopy(caller.f_locals.get("r")),
                                            logical=copy.deepcopy(caller.f_locals.get("logical")),
                                            receipt=copy.deepcopy(receipt)))
                return original_guard(receipt)

            def route_wrapper(row, operations):
                result = original_route(row, operations)
                if row["repository_relative"] == "rebuild/unrelated.py":
                    if route == "add_source":
                        row["source"] = dict(m._HISTORY_LEAF)
                    elif route == "add_logical":
                        self.assertNotEqual(m.fp(row["source"]), m.fp(m._HISTORY_LEAF))
                        row["original_source"] = dict(m._HISTORY_LEAF)
                    mutation_calls.append(route)
                return result

            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            stack = __import__("contextlib").ExitStack()
            with stack:
                stack.enter_context(patch.object(m, "cpu", return_value={
                    "job_id": "50003", "allocated_CPUs": 1, "allocated_gpus": 0}))
                stack.enter_context(patch.object(m, "reject_inventory_history_declaration",
                                                new=guard_spy))
                if route in ("add_source", "add_logical"):
                    stack.enter_context(patch.object(m, "inherited_source_route",
                                                    side_effect=route_wrapper))
                elif route == "resolve":
                    # Only a synthetic edge route is disabled to exercise later defense.
                    stack.enter_context(patch.object(m.InventoryHistoryOpaqueLeaf, "edge",
                                                    return_value=None))
                with self.assertRaisesRegex(
                        ValueError, "Fixed13299 diagnostic DATA cannot be direct SOURCE/gate/seed/context/Plan alias"):
                    fixture.run_fixture()
            out = fixture.root / "audit_out"
            self.assertFalse((out / "acceptance.json").exists())
            self.assertFalse((out / "source_inclusion_final.json").exists())
            self.assertFalse((out / "opaque_inventory_history_bytes").exists())
            self.assertFalse((out / "inventory_history_opaque_leaf_proof.json").exists())
            incomplete = m.read(out / "typed_incomplete.json")
            expected_stage = "recursive_exact_new_dependencies" if route == "resolve" else "base_readback"
            self.assertEqual(incomplete["failed_stage"], expected_stage)
            self.assertEqual(incomplete["reason_type"], "ValueError")
            self.assertEqual(incomplete["reason"],
                             "Fixed13299 diagnostic DATA cannot be direct SOURCE/gate/seed/context/Plan alias")
            expected_caller = "add" if route.startswith("add_") else "alias" if route == "closure_physical_alias" else "resolve"
            hits = [x for x in guard_calls if x["caller"] == expected_caller]
            self.assertEqual(len(hits), 1)
            if route == "add_source":
                self.assertEqual(hits[0]["r"], m._HISTORY_LEAF)
                self.assertNotEqual(hits[0]["logical"], m._HISTORY_LEAF)
                self.assertEqual(mutation_calls, ["add_source"])
            elif route == "add_logical":
                self.assertEqual(hits[0]["logical"], m._HISTORY_LEAF)
                self.assertNotEqual(m.fp(hits[0]["r"]), m.fp(m._HISTORY_LEAF))
                self.assertEqual(mutation_calls, ["add_logical"])
            elif route == "resolve":
                self.assertEqual(hits[0]["r"], m._HISTORY_LEAF)
            else:
                self.assertEqual(hits[0]["receipt"], m._HISTORY_LEAF)
        finally:
            for name, value in saved_private.items():
                setattr(m, name, value)
            fixture.tearDown()

    def test_history33_inherited_source_reaches_actual_add_r_direct_guard(self):
        self.run_route("add_source")

    def test_history34_inherited_logical_reaches_actual_add_logical_guard(self):
        self.run_route("add_logical")

    def test_history35_inherited_closure_physical_alias_reaches_actual_nested_alias_guard(self):
        self.run_route("closure_physical_alias")

    def test_history36_queue_edge_isolation_reaches_actual_nested_resolve_guard(self):
        self.run_route("resolve")


class ArchiveParentHistoryDataContracts(unittest.TestCase):
    """Synthetic own-byte fixtures; no live member/SCI source is opened by these cases."""

    private_names = ("_FIXED_HISTORY_MAPPING_PARENTS", "_FIXED_HISTORY_MAPPING_PROVENANCE", "_ARCHIVE_PARENT_HISTORY_BASE", "_ARCHIVE_PARENT_HISTORY_AUTHORITY", "_ARCHIVE_PARENT_HISTORY_LEAF",
                     "_ARCHIVE_PARENT_HISTORY_PRODUCER", "_ARCHIVE_PARENT_HISTORY_SOFTWARE", "_ARCHIVE_PARENT_HISTORY_MANIFEST")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_root = m.R
        self.old_private = {name: copy.deepcopy(getattr(m, name)) for name in self.private_names}
        m.R = self.root
        self.install(self.root / "case")
        self.out = self.root / "out"
        self.out.mkdir()
        self.scope = m.ArchiveParentHistoryOpaqueLeaf(self.out, m._ARCHIVE_PARENT_HISTORY_BASE)

    def tearDown(self):
        for name, value in self.old_private.items():
            setattr(m, name, value)
        m.R = self.old_root
        for path in self.root.rglob("*"):
            if path.is_dir() and not path.is_symlink():
                path.chmod(0o755)
        self.tmp.cleanup()

    @staticmethod
    def write(path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.chmod(0o644)
        path.write_bytes(raw)
        path.chmod(0o444)
        return m.rec(path)

    def install(self, root):
        root.mkdir(parents=True, exist_ok=True)
        m._ARCHIVE_PARENT_HISTORY_AUTHORITY = str(m.R)
        self.producer = root / "producer.py"
        self.software = root / "software.json"
        m._ARCHIVE_PARENT_HISTORY_PRODUCER = self.write(self.producer, b"SYNTHETIC_SOURCE_ONLY\n")
        m._ARCHIVE_PARENT_HISTORY_SOFTWARE = self.write(self.software, b'{"status":"SYNTHETIC_SOFTWARE_HISTORY"}\n')
        m._ARCHIVE_PARENT_HISTORY_MANIFEST = r(str(root / "never_open_manifest.json"), 10, "1" * 64)
        members = [dict(path="never_open_relative_namespace/" + str(i), bytes=i, sha256="a" * 64)
                   for i in range(193)]
        parent_json = dict(archive="never_open_archive.tar.gz", archive_bytes=123, archive_sha256="b" * 64,
                           member_count=193, members=members, validation_run="never_open_validation",
                           scope_counts={"documentary_only": 1},
                           base_package={name: "never_open_" + name for name in
                                         ("archive", "sha256", "members_index", "members_index_sha256",
                                          "restore_receipt", "restore_receipt_sha256")},
                           excluded_ongoing_modules=[])
        self.document = dict(
            schema="source-v7-relative-context-diagnostic-only.v1",
            status="EXACT_RELATIVE_PARENT_DIAGNOSED_STRICT_GUARD_UNCHANGED_NOT_SOURCE_ACCEPTANCE",
            slurm_job_id="13298", failed_source_job="13297", CPUs=1, GPUs=0,
            source_producer=m._ARCHIVE_PARENT_HISTORY_PRODUCER,
            original_software_only_acceptance=m._ARCHIVE_PARENT_HISTORY_SOFTWARE,
            diagnostic=dict(parent=m._ARCHIVE_PARENT_HISTORY_MANIFEST,
                            parent_relative_to_authority="archive/reconstruction_completed_modules_20261002.members.json",
                            source_field=["members", "192"], offending_receipt=copy.deepcopy(members[192]),
                            parent_JSON=parent_json, error_type="ValueError", error="Unknown relative receipt parent"),
            **{name: False for name in m._ARCHIVE_PARENT_HISTORY_FALSE_FLAGS})
        self.leaf = root / "diagnostic.json"
        self.base_path = root / "base.json"
        self.replace_document(self.document)

    def replace_document(self, document=None, raw=None, base_overlay=None):
        if document is not None:
            self.document = document
        if raw is None:
            raw = json.dumps(self.document, allow_nan=False).encode("utf-8")
        self.content = raw
        m._ARCHIVE_PARENT_HISTORY_LEAF = self.write(self.leaf, raw)
        history = {
            m._ARCHIVE_PARENT_HISTORY_FIELD[1]: m._ARCHIVE_PARENT_HISTORY_LEAF,
            "original13297_failed_executing_source": m._ARCHIVE_PARENT_HISTORY_PRODUCER,
            "actual13297_software58_only": m._ARCHIVE_PARENT_HISTORY_SOFTWARE,
        }
        base = dict(base_overlay or {},
                    schema="source-delivery-refresh.v3",
                    status="CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY",
                    source_issues=0, source_staged=False, original_failure_history=history)
        base = install_fixed_mapping_fixture(self, base, "archive13298")
        m._ARCHIVE_PARENT_HISTORY_BASE = self.write(self.base_path, json.dumps(base).encode("utf-8"))
        if hasattr(self, "out") and self.out.is_relative_to(m.R):
            self.scope = m.ArchiveParentHistoryOpaqueLeaf(self.out, m._ARCHIVE_PARENT_HISTORY_BASE)

    def observe(self, receipt=None, parent=None, trail=None,
                module="default_workflow_integration"):
        return self.scope.edge(
            m._ARCHIVE_PARENT_HISTORY_LEAF if receipt is None else receipt,
            m._ARCHIVE_PARENT_HISTORY_BASE["path"] if parent is None else parent,
            m._ARCHIVE_PARENT_HISTORY_FIELD if trail is None else trail, module)

    def saved(self):
        self.observe()
        allocation = {"job_id": "50001", "allocated_CPUs": 1, "allocated_gpus": 0}
        aliases = self.scope.alias_index()
        pointer, unused = m._archive_parent_history_write_control(self.out / "archive_parent_history_opaque_aliases.json", aliases)
        proof = dict(self.scope.proof(), exact_alias_index=pointer, allocation=allocation)
        return proof, aliases, allocation

    def run_genuine_audit(self, invalid_after_valid=False, direct_alias=False):
        fixture = ClosureFixtureContracts("test_real_closure_preserves_old_and_accepts_new_default")
        fixture.setUp()
        saved = {name: copy.deepcopy(getattr(m, name)) for name in self.private_names}
        try:
            self.install(fixture.root / "history_case")
            original_base = m.read(fixture.p["base_acceptance"]["path"])
            self.replace_document(self.document, base_overlay=original_base)
            fixture.p["base_acceptance"] = m._ARCHIVE_PARENT_HISTORY_BASE
            default = next(x for x in fixture.p["modules"] if x["role"] == "default_workflow_integration")
            default["seeds"] = [m._ARCHIVE_PARENT_HISTORY_BASE]
            fixture.p["modules"] = [x for x in fixture.p["modules"] if x is not default] + [default]
            if invalid_after_valid:
                bad = fixture.meta("wrong_history_parent.json", {"wrong": m._ARCHIVE_PARENT_HISTORY_LEAF})
                other = next(x for x in fixture.p["modules"] if x["role"] == "formal_common_review")
                other["seeds"] = [bad]
            if direct_alias:
                fixture.p["aliases"] = [{"logical": m._ARCHIVE_PARENT_HISTORY_LEAF, "physical": m._ARCHIVE_PARENT_HISTORY_LEAF}]
            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            with patch.object(m, "cpu", return_value={"job_id": "50002", "allocated_CPUs": 1,
                                                      "allocated_gpus": 0}):
                if invalid_after_valid or direct_alias:
                    with self.assertRaises(ValueError):
                        fixture.run_fixture()
                    out = fixture.root / "audit_out"
                    self.assertFalse((out / "acceptance.json").exists())
                    if invalid_after_valid:
                        self.assertTrue((out / "opaque_archive_parent_history_bytes").is_dir())
                        self.assertTrue((out / "typed_incomplete.json").is_file())
                    return None
                inclusion = fixture.run_fixture()
                out = fixture.root / "audit_out"
                closure = m.read(out / "source_receipt_closure_final.json")
                acceptance = m.read(out / "acceptance.json")
                self.assertEqual(inclusion["archive_parent_history_opaque_leaf_proof"],
                                 acceptance["archive_parent_history_opaque_leaf_proof"])
                self.assertEqual(closure["archive_parent_history_opaque_aliases"],
                                 acceptance["archive_parent_history_opaque_aliases"])
                producers = [x for x in closure["edges"] if x.get("receipt") == m._ARCHIVE_PARENT_HISTORY_PRODUCER]
                software = [x for x in closure["edges"] if x.get("receipt") == m._ARCHIVE_PARENT_HISTORY_SOFTWARE]
                self.assertTrue(producers and software)
                self.assertTrue(all(x["role"] == "EXACT_NEW_TEXT_RECEIPT_READBACK"
                                    for x in producers + software))
                self.assertTrue(any(m.fp(row["source"]) == m.fp(m._ARCHIVE_PARENT_HISTORY_PRODUCER)
                                    for row in inclusion["files"]))
                self.assertFalse(any(m.fp(row["source"]) == m.fp(m._ARCHIVE_PARENT_HISTORY_LEAF)
                                     for row in inclusion["files"]))
                return inclusion
        finally:
            for name, value in saved.items():
                setattr(m, name, value)
            fixture.tearDown()

    def test_archive_parent_history01_default_preserves_all_bytes_without_member_io(self):
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        original_open = Path.open
        allowed = {self.base_path, self.leaf} | {Path(entry["receipt"]["path"]) for entry in m._FIXED_HISTORY_MAPPING_PARENTS}

        def guarded_open(path, *args, **kwargs):
            if Path(path) not in allowed and Path(path).parent != self.scope.directory:
                raise AssertionError("Unexpected child IO: " + str(path))
            return original_open(path, *args, **kwargs)

        before = [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)]
        with patch.object(Path, "open", guarded_open):
            edge = self.observe()
            self.assertTrue(self.scope.require_complete())
        self.assertEqual(Path(edge["physical"]["path"]).read_bytes(), self.content)
        self.assertEqual(before, [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)])
        self.assertFalse(edge["receipt_children_interpreted"])
        self.assertFalse(edge["source_or_configuration_promotion"])

    def test_archive_parent_history02_prospective_module_is_allowed_but_not_forced_or_sufficient(self):
        self.observe(module="final_delivery_tools")
        with self.assertRaises(ValueError):
            self.scope.proof()
        self.observe()
        proof = self.scope.proof()
        self.assertEqual(proof["actual_default_observation_n"], 1)
        self.assertEqual(proof["actual_finaltools_observation_n"], 1)
        other = m.ArchiveParentHistoryOpaqueLeaf(self.root / "other", m._ARCHIVE_PARENT_HISTORY_BASE)
        other.out.mkdir()
        other.edge(m._ARCHIVE_PARENT_HISTORY_LEAF, m._ARCHIVE_PARENT_HISTORY_BASE["path"], m._ARCHIVE_PARENT_HISTORY_FIELD,
                   "default_workflow_integration")
        self.assertEqual(other.proof()["actual_finaltools_observation_n"], 0)

    def test_archive_parent_history03_repeat_preserves_order_but_deduplicates_only_copy_io(self):
        first = self.observe()
        before = m.stable_metadata(first["physical"]["path"])
        second = self.observe()
        self.assertEqual(first, second)
        self.assertEqual([x["ordinal"] for x in self.scope.observations], [0, 1])
        self.assertEqual(m.stable_metadata(first["physical"]["path"]), before)

    def test_archive_parent_history04_wrong_parent_fails_before_and_after_valid_seen_identity(self):
        with self.assertRaises(ValueError):
            self.observe(parent=str(self.root / "wrong.json"))
        self.observe()
        with self.assertRaises(ValueError):
            self.observe(parent=str(self.out / "archive_parent_history_opaque_leaf_proof.json"))
        self.assertEqual(len(self.scope.observations), 1)

    def test_archive_parent_history05_exact_field_and_tuple_trail_are_mandatory(self):
        for trail in ((), ("original_failure_history",), list(m._ARCHIVE_PARENT_HISTORY_FIELD),
                      ("other", m._ARCHIVE_PARENT_HISTORY_FIELD[1])):
            with self.subTest(trail=trail), self.assertRaises(ValueError):
                self.observe(trail=trail)
        self.assertFalse(self.scope.directory.exists())

    def test_archive_parent_history06_unknown_module_is_rejected_even_after_valid_duplicate(self):
        self.observe()
        for module in sorted(m.REQUIRED_MODULES - set(m._ARCHIVE_PARENT_HISTORY_MODULES)) + ["UNKNOWN"]:
            with self.subTest(module=module), self.assertRaises(ValueError):
                self.observe(module=module)
        self.assertEqual(len(self.scope.observations), 1)

    def test_archive_parent_history07_full_original_tuple_cannot_fork(self):
        for key, value in (("path", str(self.root / "unknown.json")),
                           ("bytes", 0), ("sha256", "0" * 64)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.observe(receipt=dict(m._ARCHIVE_PARENT_HISTORY_LEAF, **{key: value}))
        self.assertFalse(self.scope.directory.exists())

    def test_archive_parent_history08_same_fingerprint_clone_path_never_gains_permission(self):
        self.observe()
        clone = dict(m._ARCHIVE_PARENT_HISTORY_LEAF, path=str(self.root / "clone.json"))
        with self.assertRaises(ValueError):
            self.observe(receipt=clone)
        with self.assertRaises(ValueError):
            m.reject_archive_parent_history_declaration(clone)
        self.assertEqual(len(self.scope.observations), 1)

    def test_archive_parent_history09_direct_plan_declarations_cannot_bypass_edge_scope(self):
        for category in ("source", "gate", "seed", "context", "logical_alias", "physical_alias",
                         "allocation_closure_gate", "root_terminal_rejection_gate",
                         "base_acceptance", "library_software_acceptance", "mapper_software_acceptance"):
            value = plan()
            module = value["modules"][0]
            leaf = dict(m._ARCHIVE_PARENT_HISTORY_LEAF)
            if category == "source":
                module["sources"][0]["receipt"] = leaf
            elif category == "gate":
                module["gate"]["receipt"] = leaf
            elif category == "seed":
                module["seeds"] = [leaf]
            elif category == "context":
                value["context_parent_seeds"] = [leaf]
            elif category == "logical_alias":
                value["aliases"] = [{"logical": leaf, "physical": r(str(self.root / "copy.txt"))}]
            elif category == "physical_alias":
                value["aliases"] = [{"logical": r(str(self.root / "ordinary.json")), "physical": leaf}]
            elif category in ("allocation_closure_gate", "root_terminal_rejection_gate"):
                module[category] = {"receipt": leaf}
            else:
                value[category] = leaf
            with self.subTest(category=category), self.assertRaises(ValueError):
                m.module_plan(value)

    def test_archive_parent_history10_unrelated_receipt_remains_on_ordinary_route(self):
        ordinary = r(str(self.root / "ordinary.json"), 2, "c" * 64)
        self.assertIsNone(self.scope.edge(ordinary, None, (), "scientific_report"))
        m.reject_archive_parent_history_declaration(ordinary)
        self.assertFalse(self.scope.directory.exists())

    def test_archive_parent_history11_zero_actual_or_foreign_base_cannot_be_accepted(self):
        with self.assertRaises(ValueError):
            self.scope.require_complete()
        scope = m.ArchiveParentHistoryOpaqueLeaf(self.out, r(str(self.root / "foreign.json")))
        self.assertFalse(scope.require_complete())
        with self.assertRaises(ValueError):
            scope.edge(m._ARCHIVE_PARENT_HISTORY_LEAF, m._ARCHIVE_PARENT_HISTORY_BASE["path"], m._ARCHIVE_PARENT_HISTORY_FIELD,
                       "default_workflow_integration")
        self.assertFalse(scope.directory.exists())

    def test_archive_parent_history12_schema_status_and_all_diagnostic_policy_flags_are_strict(self):
        for field in ("schema", "status") + m._ARCHIVE_PARENT_HISTORY_FALSE_FLAGS + m._ARCHIVE_PARENT_HISTORY_TRUE_FLAGS:
            document = copy.deepcopy(self.document)
            document[field] = "OTHER" if field in ("schema", "status") else not document[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.archive_parent_history_document_shape(document)

    def test_archive_parent_history13_utf8_duplicate_nonfinite_and_overflow_are_rejected(self):
        for raw in (b"\xff", b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e9999}'):
            self.replace_document(raw=raw)
            with self.subTest(raw=raw), self.assertRaises((ValueError, UnicodeDecodeError)):
                self.observe()
            self.assertFalse(self.scope.directory.exists())

    def test_archive_parent_history14_thirteen_keys_and193_member_metadata_are_strict(self):
        for kind in ("extra_top", "missing_top", "identity_bool", "extra_diagnostic", "manifest", "count", "members", "bool_size", "duplicate_path"):
            document = copy.deepcopy(self.document)
            diagnostic = document["diagnostic"]
            members = diagnostic["parent_JSON"]["members"]
            if kind == "extra_top":
                document["unexpected"] = True
            elif kind == "missing_top":
                document.pop("CPUs")
            elif kind == "identity_bool":
                document["CPUs"] = True
            elif kind == "extra_diagnostic":
                diagnostic["unexpected"] = 1
            elif kind == "manifest":
                diagnostic["parent"] = r(str(self.root / "other_manifest.json"))
            elif kind == "count":
                diagnostic["parent_JSON"]["member_count"] = True
            elif kind == "members":
                members.pop()
            elif kind == "bool_size":
                members[0]["bytes"] = True
            else:
                members[1]["path"] = members[0]["path"]
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                m.archive_parent_history_document_shape(document)

    def test_archive_parent_history15_member192_is_documentary_and_existing588_policy_unchanged(self):
        for kind in ("source_field", "offending", "error", "relative_parent"):
            document = copy.deepcopy(self.document)
            diagnostic = document["diagnostic"]
            if kind == "source_field":
                diagnostic["source_field"] = ["members", "0"]
            elif kind == "offending":
                diagnostic["offending_receipt"] = diagnostic["parent_JSON"]["members"][0]
            elif kind == "error":
                diagnostic["error"] = "AUTHORIZED"
            else:
                diagnostic["parent_relative_to_authority"] = "other.json"
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                m.archive_parent_history_document_shape(document)
        old = InventoryHistoryDataContracts("test_history01_default_preserves_all_bytes_without_member_io")
        old.setUp()
        try:
            self.assertTrue(m.inventory_history_document_shape(old.document))
            self.assertEqual([len(x["parent_JSON"]["members"]) for x in old.document["parents"]], [193, 395])
            self.assertEqual(len(old.document["edges"]), 588)
        finally:
            old.tearDown()

    def test_archive_parent_history16_full_base_authority_and_independent_edges_are_mandatory(self):
        original = self.base_path.read_bytes()
        self.base_path.chmod(0o644)
        self.base_path.write_bytes(original + b" ")
        self.base_path.chmod(0o444)
        with self.assertRaises(ValueError):
            self.observe()
        for field in (m._ARCHIVE_PARENT_HISTORY_FIELD[1], "original13297_failed_executing_source",
                      "actual13297_software58_only"):
            base = json.loads(original)
            base["original_failure_history"][field] = r(str(self.root / "wrong.json"))
            m._ARCHIVE_PARENT_HISTORY_BASE = self.write(self.base_path, json.dumps(base).encode())
            self.scope = m.ArchiveParentHistoryOpaqueLeaf(self.out, m._ARCHIVE_PARENT_HISTORY_BASE)
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.observe()

    def test_archive_parent_history17_writable_original_or_parent_is_forbidden(self):
        for path in (self.base_path, self.leaf):
            path.chmod(0o644)
            try:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    self.observe()
            finally:
                path.chmod(0o444)

    def test_archive_parent_history18_symlink_leaf_and_ancestor_are_not_alias_permissions(self):
        backup = self.root / "backup.json"
        self.write(backup, self.content)
        self.leaf.unlink()
        self.leaf.symlink_to(backup)
        with self.assertRaises(ValueError):
            self.observe()
        self.leaf.unlink()
        self.write(self.leaf, self.content)
        linked = self.root / "linked"
        linked.symlink_to(self.leaf.parent, target_is_directory=True)
        clone = dict(m._ARCHIVE_PARENT_HISTORY_LEAF, path=str(linked / self.leaf.name))
        with self.assertRaises(ValueError):
            self.observe(receipt=clone)

    def test_archive_parent_history19_parent_original_and_copy_hardlinks_are_rejected(self):
        for path in (self.base_path, self.leaf):
            link = self.root / "hardlink"
            m.os.link(path, link)
            try:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    self.observe()
            finally:
                link.unlink()
        edge = self.observe()
        link = self.root / "copy_hardlink"
        m.os.link(edge["physical"]["path"], link)
        try:
            with self.assertRaises(ValueError):
                self.scope.readback()
        finally:
            link.unlink()

    def test_archive_parent_history20_input_metadata_drift_after_valid_output_is_detected(self):
        self.observe()
        before = m.stable_metadata(self.leaf)
        changed = before["mtime_ns"] + 2000000000
        m.os.utime(self.leaf, ns=(changed, changed))
        with self.assertRaises(ValueError):
            self.scope.readback()
        self.assertFalse((self.out / "acceptance.json").exists())

    def test_archive_parent_history21_changed_original_bytes_are_not_reaccepted(self):
        self.observe()
        self.leaf.chmod(0o644)
        self.leaf.write_bytes(self.content + b" ")
        self.leaf.chmod(0o444)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_archive_parent_history22_copy_writability_or_changed_content_is_fatal(self):
        edge = self.observe()
        path = Path(edge["physical"]["path"])
        path.chmod(0o644)
        with self.assertRaises(ValueError):
            self.scope.readback()
        path.write_bytes(b"CHANGED")
        path.chmod(0o444)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_archive_parent_history23_directory0555_is_independent_of_synchronized_proof_metadata(self):
        proof, aliases, allocation = self.saved()
        self.scope.directory.chmod(0o755)
        proof["copy_directory_metadata"] = m.stable_metadata(self.scope.directory)
        with self.assertRaisesRegex(ValueError, "readonly0555"):
            m.archive_parent_history_proof_shape(proof, aliases, allocation)
        with self.assertRaises(ValueError):
            m.verify_archive_parent_history_preservation(proof, aliases, allocation)

    def test_archive_parent_history24_exclusive_collision_and_exact_one_file_universe(self):
        self.scope.directory.mkdir()
        sentinel = self.scope.directory / "SENTINEL"
        sentinel.write_text("DO_NOT_OVERWRITE")
        with self.assertRaises(FileExistsError):
            self.observe()
        self.assertEqual(sentinel.read_text(), "DO_NOT_OVERWRITE")
        sentinel.unlink()
        self.scope.directory.rmdir()
        self.observe()
        self.scope.directory.chmod(0o755)
        (self.scope.directory / "extra.txt").write_text("EXTRA")
        self.scope.directory.chmod(0o555)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_archive_parent_history25_fsync_failure_never_accepts_or_changes_originals(self):
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        before = [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)]
        with patch.object(m.os, "fsync", side_effect=OSError("SYNTHETIC_FSYNC_FAILURE")):
            with self.assertRaises(OSError):
                self.observe()
        self.assertEqual(before, [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)])
        self.assertFalse(self.scope.observations)
        self.assertFalse((self.out / "acceptance.json").exists())

    def test_archive_parent_history26_pure_full_proof_rejects_flags_metadata_counts_and_extra_keys(self):
        proof, aliases, allocation = self.saved()
        self.assertTrue(m.archive_parent_history_proof_shape(proof, aliases, allocation))
        for field, value in (("schema", "OTHER"), ("authorized_observation_n", True),
                             ("embedded_observation_n", 192), ("member_paths_statted_or_opened", True),
                             ("archive_or_scientific_acceptance", True), ("unexpected", 1)):
            fork = copy.deepcopy(proof)
            fork[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.archive_parent_history_proof_shape(fork, aliases, allocation)
        fork = copy.deepcopy(proof)
        fork["original_metadata_before"]["inode"] = True
        with self.assertRaises(ValueError):
            m.archive_parent_history_proof_shape(fork, aliases, allocation)

    def test_archive_parent_history27_alias_pointer_status_allocation_and_context_tampering_fail(self):
        proof, aliases, allocation = self.saved()
        for kind in ("alias_status", "alias_receipt", "pointer", "allocation", "module", "order", "ordinal"):
            fork, index = copy.deepcopy(proof), copy.deepcopy(aliases)
            if kind == "alias_status":
                index["aliases"][0]["status"] = "OTHER"
            elif kind == "alias_receipt":
                index["aliases"][0]["archived"]["sha256"] = "0" * 64
            elif kind == "pointer":
                fork["exact_alias_index"]["path"] = str(self.root / "other.json")
            elif kind == "allocation":
                fork["allocation"] = {"job_id": "OTHER"}
            elif kind == "module":
                fork["observations"][0]["module"] = "scientific_report"
            elif kind == "order":
                fork["observations"][0]["field"].reverse()
            else:
                fork["observations"][0]["ordinal"] = True
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                m.archive_parent_history_proof_shape(fork, index, allocation)

    def test_archive_parent_history28_pure_validator_has_no_filesystem_or_live_source_calls(self):
        proof, aliases, allocation = self.saved()
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        with patch.object(Path, "open", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "stat", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "lstat", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "resolve", side_effect=AssertionError("NO_FS")), \
             patch.object(m, "rec", side_effect=AssertionError("NO_LIVE_SHA")), \
             patch.object(m, "verify", side_effect=AssertionError("NO_LIVE_VERIFY")):
            self.assertTrue(m.archive_parent_history_proof_shape(proof, aliases, allocation))

    def test_archive_parent_history29_production_saved_verifier_checks_current_bytes_and_index(self):
        proof, aliases, allocation = self.saved()
        self.assertTrue(m.verify_archive_parent_history_preservation(proof, aliases, allocation))
        pointer = Path(proof["exact_alias_index"]["path"])
        pointer.chmod(0o644)
        pointer.write_text(json.dumps({"schema": "CHANGED"}))
        pointer.chmod(0o444)
        with self.assertRaises(ValueError):
            m.verify_archive_parent_history_preservation(proof, aliases, allocation)

    def test_archive_parent_history30_genuine_audit_retains_independent_producer_software_and_data_role(self):
        self.assertIsNotNone(self.run_genuine_audit())

    def test_archive_parent_history31_genuine_queue_rejects_wrong_context_after_valid_seen_copy(self):
        self.run_genuine_audit(invalid_after_valid=True)

    def test_archive_parent_history32_genuine_audit_cannot_use_plan_alias_as_direct_data_permission(self):
        self.run_genuine_audit(direct_alias=True)



class ArchiveParentHistoryInheritedRouteContracts(unittest.TestCase):
    """Reach nested actual audit guards with test-only row/edge isolation."""

    def run_route(self, route):
        import inspect
        fixture = ClosureFixtureContracts("test_real_closure_preserves_old_and_accepts_new_default")
        fixture.setUp()
        case = ArchiveParentHistoryDataContracts("test_archive_parent_history01_default_preserves_all_bytes_without_member_io")
        saved_private = {name: copy.deepcopy(getattr(m, name)) for name in case.private_names}
        guard_calls = []
        mutation_calls = []
        original_guard = m.reject_archive_parent_history_declaration
        original_route = m.inherited_source_route
        try:
            case.install(fixture.root / "inherited_history_case")
            base = m.read(fixture.p["base_acceptance"]["path"])
            if route == "closure_physical_alias":
                closure = dict(schema="benchmark-source-receipt-closure.v1", edges=[
                    dict(receipt=r(str(fixture.root / "ordinary_alias.py"), 1, "c" * 64),
                         parent=str(fixture.asset / "ordinary_parent.json"), field=["source"],
                         physical=m._ARCHIVE_PARENT_HISTORY_LEAF, resolution_basis="EXACT_ORIGINAL",
                         role="EXACT_TEXT_RECEIPT_READBACK")])
                closure_receipt = fixture.meta("history_alias_closure.json", closure)
                inclusion = m.read(base["source_inclusion"]["path"])
                inclusion["source_receipt_closure"] = closure_receipt
                inclusion_receipt = fixture.meta("history_alias_inclusion.json", inclusion)
                base["source_closure"] = closure_receipt
                base["source_inclusion"] = inclusion_receipt
            case.replace_document(case.document, base_overlay=base)
            fixture.p["base_acceptance"] = m._ARCHIVE_PARENT_HISTORY_BASE
            default = next(x for x in fixture.p["modules"] if x["role"] == "default_workflow_integration")
            if route == "resolve":
                default["seeds"] = [m._ARCHIVE_PARENT_HISTORY_BASE]
                fixture.p["modules"] = [x for x in fixture.p["modules"] if x is not default] + [default]

            def guard_spy(receipt):
                caller = inspect.currentframe().f_back
                if receipt == m._ARCHIVE_PARENT_HISTORY_LEAF:
                    guard_calls.append(dict(caller=caller.f_code.co_name,
                                            r=copy.deepcopy(caller.f_locals.get("r")),
                                            logical=copy.deepcopy(caller.f_locals.get("logical")),
                                            receipt=copy.deepcopy(receipt)))
                return original_guard(receipt)

            def route_wrapper(row, operations):
                result = original_route(row, operations)
                if row["repository_relative"] == "rebuild/unrelated.py":
                    if route == "add_source":
                        row["source"] = dict(m._ARCHIVE_PARENT_HISTORY_LEAF)
                    elif route == "add_logical":
                        self.assertNotEqual(m.fp(row["source"]), m.fp(m._ARCHIVE_PARENT_HISTORY_LEAF))
                        row["original_source"] = dict(m._ARCHIVE_PARENT_HISTORY_LEAF)
                    mutation_calls.append(route)
                return result

            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            stack = __import__("contextlib").ExitStack()
            with stack:
                stack.enter_context(patch.object(m, "cpu", return_value={
                    "job_id": "50003", "allocated_CPUs": 1, "allocated_gpus": 0}))
                stack.enter_context(patch.object(m, "reject_archive_parent_history_declaration",
                                                new=guard_spy))
                if route in ("add_source", "add_logical"):
                    stack.enter_context(patch.object(m, "inherited_source_route",
                                                    side_effect=route_wrapper))
                elif route == "resolve":
                    # Only a synthetic edge route is disabled to exercise later defense.
                    stack.enter_context(patch.object(m.ArchiveParentHistoryOpaqueLeaf, "edge",
                                                    return_value=None))
                with self.assertRaisesRegex(
                        ValueError, "Fixed13298 diagnostic DATA cannot be direct SOURCE/gate/seed/context/Plan alias"):
                    fixture.run_fixture()
            out = fixture.root / "audit_out"
            self.assertFalse((out / "acceptance.json").exists())
            self.assertFalse((out / "source_inclusion_final.json").exists())
            self.assertFalse((out / "opaque_archive_parent_history_bytes").exists())
            self.assertFalse((out / "archive_parent_history_opaque_leaf_proof.json").exists())
            incomplete = m.read(out / "typed_incomplete.json")
            expected_stage = "recursive_exact_new_dependencies" if route == "resolve" else "base_readback"
            self.assertEqual(incomplete["failed_stage"], expected_stage)
            self.assertEqual(incomplete["reason_type"], "ValueError")
            self.assertEqual(incomplete["reason"],
                             "Fixed13298 diagnostic DATA cannot be direct SOURCE/gate/seed/context/Plan alias")
            expected_caller = "add" if route.startswith("add_") else "alias" if route == "closure_physical_alias" else "resolve"
            hits = [x for x in guard_calls if x["caller"] == expected_caller]
            self.assertEqual(len(hits), 1)
            if route == "add_source":
                self.assertEqual(hits[0]["r"], m._ARCHIVE_PARENT_HISTORY_LEAF)
                self.assertNotEqual(hits[0]["logical"], m._ARCHIVE_PARENT_HISTORY_LEAF)
                self.assertEqual(mutation_calls, ["add_source"])
            elif route == "add_logical":
                self.assertEqual(hits[0]["logical"], m._ARCHIVE_PARENT_HISTORY_LEAF)
                self.assertNotEqual(m.fp(hits[0]["r"]), m.fp(m._ARCHIVE_PARENT_HISTORY_LEAF))
                self.assertEqual(mutation_calls, ["add_logical"])
            elif route == "resolve":
                self.assertEqual(hits[0]["r"], m._ARCHIVE_PARENT_HISTORY_LEAF)
            else:
                self.assertEqual(hits[0]["receipt"], m._ARCHIVE_PARENT_HISTORY_LEAF)
        finally:
            for name, value in saved_private.items():
                setattr(m, name, value)
            fixture.tearDown()

    def test_archive_parent_history33_inherited_source_reaches_actual_add_r_direct_guard(self):
        self.run_route("add_source")

    def test_archive_parent_history34_inherited_logical_reaches_actual_add_logical_guard(self):
        self.run_route("add_logical")

    def test_archive_parent_history35_inherited_closure_physical_alias_reaches_actual_nested_alias_guard(self):
        self.run_route("closure_physical_alias")

    def test_archive_parent_history36_queue_edge_isolation_reaches_actual_nested_resolve_guard(self):
        self.run_route("resolve")


class ArchiveParentHistoryOutputControlContracts(unittest.TestCase):
    def test_archive_parent_history37_fixed_control_writer_is_exclusive_fsynced_and_failure_retains_data(self):
        case = ArchiveParentHistoryDataContracts("test_archive_parent_history01_default_preserves_all_bytes_without_member_io")
        case.setUp()
        try:
            case.observe()
            alias = case.scope.alias_index()
            path = case.out / "archive_parent_history_opaque_aliases.json"
            pointer, metadata = m._archive_parent_history_write_control(path, alias)
            actual, after = m._archive_parent_history_control_readback(pointer, metadata)
            self.assertEqual(actual, alias)
            self.assertEqual(after, metadata)
            self.assertEqual(metadata["mode"] & 0o777, 0o444)
            self.assertEqual(metadata["nlink"], 1)
            with self.assertRaises(FileExistsError):
                m._archive_parent_history_write_control(path, alias)
            failure = case.out / "archive_parent_history_opaque_leaf_proof.json"
            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            with patch.object(m.os, "fsync", side_effect=OSError("SYNTHETIC_CONTROL_FSYNC")):
                with self.assertRaisesRegex(OSError, "SYNTHETIC_CONTROL_FSYNC"):
                    m._archive_parent_history_write_control(failure, {"fixture": True})
            self.assertEqual(Path(case.scope.copy_receipt["path"]).read_bytes(), case.content)
            self.assertFalse((case.out / "acceptance.json").exists())
        finally:
            case.tearDown()

    def test_archive_parent_history38_both_controls_reject_mode_hardlink_native_drift_and_post_json_mutation(self):
        case = ArchiveParentHistoryDataContracts("test_archive_parent_history01_default_preserves_all_bytes_without_member_io")
        case.setUp()
        try:
            proof, alias, allocation = case.saved()
            proof_pointer, proof_metadata = m._archive_parent_history_write_control(
                case.out / "archive_parent_history_opaque_leaf_proof.json", proof)
            for pointer in (proof_pointer, proof["exact_alias_index"]):
                path = Path(pointer["path"])
                expected = m._archive_parent_history_control_metadata(path)
                path.chmod(0o400)
                with self.subTest(control=path.name, boundary="exact444"), self.assertRaises(ValueError):
                    m._archive_parent_history_control_readback(pointer)
                path.chmod(0o444)
                link = case.root / (path.name + ".hardlink")
                m.os.link(path, link)
                try:
                    with self.subTest(control=path.name, boundary="singlelink"), self.assertRaises(ValueError):
                        m._archive_parent_history_control_readback(pointer)
                finally:
                    link.unlink()
                expected = m._archive_parent_history_control_metadata(path)
                raw = path.read_bytes()
                original_json = m._strict_archive_parent_history_json
                hits = []
                def mutate_after_json(text):
                    value = original_json(text)
                    if text.encode("utf-8") == raw:
                        current = m.stable_metadata(path)
                        changed = current["mtime_ns"] + 2000000000
                        m.os.utime(path, ns=(changed, changed))
                        hits.append(path.name)
                    return value
                patch = __import__("unittest.mock", fromlist=["patch"]).patch
                with patch.object(m, "_strict_archive_parent_history_json", side_effect=mutate_after_json):
                    with self.subTest(control=path.name, boundary="post_last_JSON"), self.assertRaisesRegex(
                            ValueError, "Fixed13298 control changed during own JSON readback"):
                        m._archive_parent_history_control_readback(pointer, expected)
                self.assertEqual(hits, [path.name])
                with self.subTest(control=path.name, boundary="stored_metadata"), self.assertRaises(ValueError):
                    m._archive_parent_history_control_readback(pointer, expected)
            self.assertEqual(Path(case.scope.copy_receipt["path"]).read_bytes(), case.content)
            self.assertFalse((case.out / "acceptance.json").exists())
        finally:
            case.tearDown()


class ArchiveParentHistoryFinalReadonlyLifecycleContracts(unittest.TestCase):
    """Exercise the unchanged genuine audit through its final readonly loop."""

    def run_final_readonly_fixture(self, writable_output):
        import inspect
        case = ArchiveParentHistoryDataContracts(
            "test_archive_parent_history01_default_preserves_all_bytes_without_member_io")
        case.setUp()
        original_audit = m.audit
        original_writer = m._archive_parent_history_write_control
        original_dump = m.dump
        original_chmod = Path.chmod
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        controls = {}
        repeated_chmods = []
        writable_chmods = []
        writable = {}
        completed = []
        control_names = {"archive_parent_history_opaque_leaf_proof.json",
                         "archive_parent_history_opaque_aliases.json"}

        def remember_writer(path, obj):
            result = original_writer(path, obj)
            path = Path(path)
            self.assertIn(path.name, control_names)
            self.assertNotIn(path, controls)
            controls[path] = (copy.deepcopy(result[0]), copy.deepcopy(result[1]))
            return result

        def observe_chmod(path, mode, *args, **kwargs):
            path = Path(path)
            if path in controls and mode == 0o444 and path.lstat().st_mode & 0o7777 == 0o444:
                # The old final loop would reach this real same-mode chmod.
                # Make its own-fixture metadata effect deterministic, without
                # replacing any metadata reader or production drift guard.
                repeated_chmods.append(str(path))
                result = original_chmod(path, mode, *args, **kwargs)
                native = path.lstat()
                m.os.utime(path, ns=(native.st_atime_ns,
                                    native.st_mtime_ns + 2000000000))
                return result
            if path == writable.get("path"):
                caller = inspect.currentframe().f_back.f_code.co_name
                before = m.stable_metadata(path)
                result = original_chmod(path, mode, *args, **kwargs)
                writable_chmods.append(dict(caller=caller, requested_mode=mode,
                                            before=before, after=m.stable_metadata(path)))
                return result
            return original_chmod(path, mode, *args, **kwargs)

        def publish_with_writable_output(path, obj):
            receipt = original_dump(path, obj)
            path = Path(path)
            if writable_output and path.name == "acceptance.json" and path.parent.name == "audit_out":
                self.assertFalse(writable)
                target = path.parent / "synthetic_final_readonly_writable.json"
                content = b'{"fixture_only": true, "no_child_receipts": true}\n'
                flags = m.os.O_WRONLY | m.os.O_CREAT | m.os.O_EXCL | getattr(m.os, "O_NOFOLLOW", 0)
                fd = m.os.open(target, flags, 0o600)
                with m.os.fdopen(fd, "wb") as stream:
                    stream.write(content)
                    stream.flush()
                    m.os.fsync(stream.fileno())
                writable.update(path=target, content=content,
                                metadata=m.stable_metadata(target))
                self.assertEqual(writable["metadata"]["mode"] & 0o7777, 0o600)
            return receipt

        def audit_and_check_final_readback(*args, **kwargs):
            result = original_audit(*args, **kwargs)
            self.assertEqual({path.name for path in controls}, control_names)
            self.assertEqual(len(controls), 2)
            for path, (receipt, metadata) in controls.items():
                self.assertEqual(m.rec(path), receipt)
                self.assertEqual(m.stable_metadata(path), metadata)
                self.assertEqual(metadata["mode"] & 0o7777, 0o444)
                self.assertEqual(metadata["nlink"], 1)
            self.assertEqual(repeated_chmods, [])
            if writable_output:
                self.assertIn("path", writable)
                self.assertEqual(len(writable_chmods), 1)
                event = writable_chmods[0]
                self.assertEqual(event["caller"], "audit")
                self.assertEqual(event["requested_mode"], 0o444)
                self.assertEqual(event["before"], writable["metadata"])
                self.assertEqual(event["before"]["mode"] & 0o7777, 0o600)
                self.assertEqual(event["after"]["mode"] & 0o7777, 0o444)
                self.assertEqual(event["after"]["nlink"], 1)
                self.assertEqual(writable["path"].read_bytes(), writable["content"])
                self.assertEqual(m.stable_metadata(writable["path"]), event["after"])
            else:
                self.assertEqual(writable, {})
                self.assertEqual(writable_chmods, [])
            completed.append(True)
            return result

        try:
            with patch.object(m, "_archive_parent_history_write_control", side_effect=remember_writer), \
                 patch.object(m, "dump", side_effect=publish_with_writable_output), \
                 patch.object(Path, "chmod", new=observe_chmod), \
                 patch.object(m, "audit", side_effect=audit_and_check_final_readback):
                self.assertIsNotNone(case.run_genuine_audit())
            self.assertEqual(completed, [True])
            self.assertIs(m.audit, original_audit)
            self.assertIs(m.dump, original_dump)
            self.assertIs(m._archive_parent_history_write_control, original_writer)
            self.assertIs(Path.chmod, original_chmod)
        finally:
            case.tearDown()

    def test_archive_parent_history39_genuine_audit_final_seal_preserves_exact444_control_metadata(self):
        self.run_final_readonly_fixture(writable_output=False)

    def test_archive_parent_history40_genuine_audit_final_seal_converts_writable_owned_JSON(self):
        self.run_final_readonly_fixture(writable_output=True)


class RelativeDiagnosticHistoryDataContracts(unittest.TestCase):
    """Synthetic own-byte fixtures; no live member/SCI source is opened by these cases."""

    private_names = ("_FIXED_HISTORY_MAPPING_PARENTS", "_FIXED_HISTORY_MAPPING_PROVENANCE", "_RELATIVE_DIAGNOSTIC_HISTORY_BASE", "_RELATIVE_DIAGNOSTIC_HISTORY_AUTHORITY", "_RELATIVE_DIAGNOSTIC_HISTORY_LEAF",
                     "_RELATIVE_DIAGNOSTIC_HISTORY_PRODUCER", "_RELATIVE_DIAGNOSTIC_HISTORY_SOFTWARE", "_RELATIVE_DIAGNOSTIC_HISTORY_RECOVERED_PARENT")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_root = m.R
        self.old_private = {name: copy.deepcopy(getattr(m, name)) for name in self.private_names}
        m.R = self.root
        self.install(self.root / "case")
        self.out = self.root / "out"
        self.out.mkdir()
        self.scope = m.RelativeDiagnosticHistoryOpaqueLeaf(self.out, m._RELATIVE_DIAGNOSTIC_HISTORY_BASE)

    def tearDown(self):
        for name, value in self.old_private.items():
            setattr(m, name, value)
        m.R = self.old_root
        for path in self.root.rglob("*"):
            if path.is_dir() and not path.is_symlink():
                path.chmod(0o755)
        self.tmp.cleanup()

    @staticmethod
    def write(path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.chmod(0o644)
        path.write_bytes(raw)
        path.chmod(0o444)
        return m.rec(path)

    def install(self, root):
        root.mkdir(parents=True, exist_ok=True)
        m._RELATIVE_DIAGNOSTIC_HISTORY_AUTHORITY = str(m.R)
        self.producer = root / "producer.py"
        self.software = root / "software.json"
        m._RELATIVE_DIAGNOSTIC_HISTORY_PRODUCER = self.write(self.producer, b"SYNTHETIC_SOURCE_ONLY\n")
        m._RELATIVE_DIAGNOSTIC_HISTORY_SOFTWARE = self.write(self.software, b'{"status":"SYNTHETIC_SOFTWARE_HISTORY"}\n')
        m._RELATIVE_DIAGNOSTIC_HISTORY_RECOVERED_PARENT = r(str(root / "never_open_recovered_parent.json"), 10, "1" * 64)
        files = [dict(path=name, bytes=i, sha256="a" * 64)
                 for i, name in enumerate(m._RELATIVE_DIAGNOSTIC_HISTORY_FILE_NAMES)]
        records = [dict(record_number=number, ordinal=number - 1,
                        timestamp="2026-09-23T09:22:11.398Z", original_jsonl_line_sha256="b" * 64,
                        output_file=files[i]["path"], output_sha256=files[i]["sha256"],
                        extraction="SYNTHETIC documentary scalar only")
                   for i, number in enumerate(m._RELATIVE_DIAGNOSTIC_HISTORY_RECORD_NUMBERS)]
        parent_json = dict(schema_version=1, session_id="01a0bdc5-988d-70c1-8346-f463d4989fa2",
                           source_session_file="/Users/yangzijian/.codex/sessions/2026/09/20/rollout-2026-09-20T15-43-58-01a0bdc5-988d-70c1-8346-f463d4989fa2.jsonl",
                           recovery_type="byte_preserving_evidence_extraction_no_new_scientific_inference",
                           records=records, files=files)
        self.document = dict(
            schema="source-v6-relative-context-diagnostic-only.v1",
            status="EXACT_RELATIVE_PARENT_DIAGNOSED_STRICT_GUARD_UNCHANGED_NOT_SOURCE_ACCEPTANCE",
            slurm_job_id="13295", failed_source_job="13293", CPUs=1, GPUs=0,
            source_producer=m._RELATIVE_DIAGNOSTIC_HISTORY_PRODUCER,
            original_software_only_acceptance=m._RELATIVE_DIAGNOSTIC_HISTORY_SOFTWARE,
            diagnostic=dict(parent=m._RELATIVE_DIAGNOSTIC_HISTORY_RECOVERED_PARENT,
                            parent_relative_to_authority="01_raw/recovered_inputs/candidate_recovery_receipt.json",
                            source_field=["files", "4"], offending_receipt=copy.deepcopy(files[4]),
                            parent_JSON=parent_json, error_type="ValueError", error="Unknown relative receipt parent"),
            **{name: False for name in m._RELATIVE_DIAGNOSTIC_HISTORY_FALSE_FLAGS})
        self.leaf = root / "diagnostic.json"
        self.base_path = root / "base.json"
        self.replace_document(self.document)

    def replace_document(self, document=None, raw=None, base_overlay=None):
        if document is not None:
            self.document = document
        if raw is None:
            raw = json.dumps(self.document, allow_nan=False).encode("utf-8")
        self.content = raw
        m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF = self.write(self.leaf, raw)
        history = {
            m._RELATIVE_DIAGNOSTIC_HISTORY_FIELD[1]: m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF,
            "original13293_executing_source": m._RELATIVE_DIAGNOSTIC_HISTORY_PRODUCER,
            "original13293_software_only_acceptance": m._RELATIVE_DIAGNOSTIC_HISTORY_SOFTWARE,
        }
        base = dict(base_overlay or {},
                    schema="source-delivery-refresh.v3",
                    status="CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY",
                    source_issues=0, source_staged=False, original_failure_history=history)
        base = install_fixed_mapping_fixture(self, base, "relative13295")
        m._RELATIVE_DIAGNOSTIC_HISTORY_BASE = self.write(self.base_path, json.dumps(base).encode("utf-8"))
        if hasattr(self, "out") and self.out.is_relative_to(m.R):
            self.scope = m.RelativeDiagnosticHistoryOpaqueLeaf(self.out, m._RELATIVE_DIAGNOSTIC_HISTORY_BASE)

    def observe(self, receipt=None, parent=None, trail=None,
                module="default_workflow_integration"):
        return self.scope.edge(
            m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF if receipt is None else receipt,
            m._RELATIVE_DIAGNOSTIC_HISTORY_BASE["path"] if parent is None else parent,
            m._RELATIVE_DIAGNOSTIC_HISTORY_FIELD if trail is None else trail, module)

    def saved(self):
        self.observe()
        allocation = {"job_id": "50001", "allocated_CPUs": 1, "allocated_gpus": 0}
        aliases = self.scope.alias_index()
        pointer, unused = m._relative_diagnostic_history_write_control(self.out / "relative_diagnostic_history_opaque_aliases.json", aliases)
        proof = dict(self.scope.proof(), exact_alias_index=pointer, allocation=allocation)
        return proof, aliases, allocation

    def run_genuine_audit(self, invalid_after_valid=False, direct_alias=False):
        fixture = ClosureFixtureContracts("test_real_closure_preserves_old_and_accepts_new_default")
        fixture.setUp()
        saved = {name: copy.deepcopy(getattr(m, name)) for name in self.private_names}
        try:
            self.install(fixture.root / "history_case")
            original_base = m.read(fixture.p["base_acceptance"]["path"])
            self.replace_document(self.document, base_overlay=original_base)
            fixture.p["base_acceptance"] = m._RELATIVE_DIAGNOSTIC_HISTORY_BASE
            default = next(x for x in fixture.p["modules"] if x["role"] == "default_workflow_integration")
            default["seeds"] = [m._RELATIVE_DIAGNOSTIC_HISTORY_BASE]
            fixture.p["modules"] = [x for x in fixture.p["modules"] if x is not default] + [default]
            if invalid_after_valid:
                bad = fixture.meta("wrong_history_parent.json", {"wrong": m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF})
                other = next(x for x in fixture.p["modules"] if x["role"] == "formal_common_review")
                other["seeds"] = [bad]
            if direct_alias:
                fixture.p["aliases"] = [{"logical": m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF, "physical": m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF}]
            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            with patch.object(m, "cpu", return_value={"job_id": "50002", "allocated_CPUs": 1,
                                                      "allocated_gpus": 0}):
                if invalid_after_valid or direct_alias:
                    with self.assertRaises(ValueError):
                        fixture.run_fixture()
                    out = fixture.root / "audit_out"
                    self.assertFalse((out / "acceptance.json").exists())
                    incomplete = m.read(out / "typed_incomplete.json")
                    if invalid_after_valid:
                        self.assertTrue((out / "opaque_relative_diagnostic_history_bytes").is_dir())
                        self.assertEqual(incomplete["failed_stage"], "recursive_exact_new_dependencies")
                        self.assertEqual(incomplete["reason"],
                                         "Fixed inherited history requires exact parent/field/two-module/fulltuple context")
                    else:
                        self.assertFalse((out / "opaque_relative_diagnostic_history_bytes").exists())
                        self.assertEqual(incomplete["failed_stage"], "explicit_plan")
                        self.assertEqual(incomplete["reason"],
                                         "Fixed13295 diagnostic DATA cannot be direct SOURCE/gate/seed/context/Plan alias")
                    self.assertEqual(incomplete["reason_type"], "ValueError")
                    return None
                inclusion = fixture.run_fixture()
                out = fixture.root / "audit_out"
                closure = m.read(out / "source_receipt_closure_final.json")
                acceptance = m.read(out / "acceptance.json")
                self.assertEqual(inclusion["relative_diagnostic_history_opaque_leaf_proof"],
                                 acceptance["relative_diagnostic_history_opaque_leaf_proof"])
                self.assertEqual(closure["relative_diagnostic_history_opaque_aliases"],
                                 acceptance["relative_diagnostic_history_opaque_aliases"])
                producers = [x for x in closure["edges"] if x.get("receipt") == m._RELATIVE_DIAGNOSTIC_HISTORY_PRODUCER]
                software = [x for x in closure["edges"] if x.get("receipt") == m._RELATIVE_DIAGNOSTIC_HISTORY_SOFTWARE]
                self.assertTrue(producers and software)
                self.assertTrue(all(x["role"] == "EXACT_NEW_TEXT_RECEIPT_READBACK"
                                    for x in producers + software))
                self.assertTrue(any(m.fp(row["source"]) == m.fp(m._RELATIVE_DIAGNOSTIC_HISTORY_PRODUCER)
                                    for row in inclusion["files"]))
                self.assertFalse(any(m.fp(row["source"]) == m.fp(m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF)
                                     for row in inclusion["files"]))
                return inclusion
        finally:
            for name, value in saved.items():
                setattr(m, name, value)
            fixture.tearDown()

    def test_relative_diagnostic_history01_default_preserves_all_bytes_without_member_io(self):
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        original_open = Path.open
        allowed = {self.base_path, self.leaf} | {Path(entry["receipt"]["path"]) for entry in m._FIXED_HISTORY_MAPPING_PARENTS}

        def guarded_open(path, *args, **kwargs):
            if Path(path) not in allowed and Path(path).parent != self.scope.directory:
                raise AssertionError("Unexpected child IO: " + str(path))
            return original_open(path, *args, **kwargs)

        before = [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)]
        with patch.object(Path, "open", guarded_open):
            edge = self.observe()
            self.assertTrue(self.scope.require_complete())
        self.assertEqual(Path(edge["physical"]["path"]).read_bytes(), self.content)
        self.assertEqual(before, [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)])
        self.assertFalse(edge["receipt_children_interpreted"])
        self.assertFalse(edge["source_or_configuration_promotion"])

    def test_relative_diagnostic_history02_prospective_module_is_allowed_but_not_forced_or_sufficient(self):
        self.observe(module="final_delivery_tools")
        with self.assertRaises(ValueError):
            self.scope.proof()
        self.observe()
        proof = self.scope.proof()
        self.assertEqual(proof["actual_default_observation_n"], 1)
        self.assertEqual(proof["actual_finaltools_observation_n"], 1)
        other = m.RelativeDiagnosticHistoryOpaqueLeaf(self.root / "other", m._RELATIVE_DIAGNOSTIC_HISTORY_BASE)
        other.out.mkdir()
        other.edge(m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF, m._RELATIVE_DIAGNOSTIC_HISTORY_BASE["path"], m._RELATIVE_DIAGNOSTIC_HISTORY_FIELD,
                   "default_workflow_integration")
        self.assertEqual(other.proof()["actual_finaltools_observation_n"], 0)

    def test_relative_diagnostic_history03_repeat_preserves_order_but_deduplicates_only_copy_io(self):
        first = self.observe()
        before = m.stable_metadata(first["physical"]["path"])
        second = self.observe()
        self.assertEqual(first, second)
        self.assertEqual([x["ordinal"] for x in self.scope.observations], [0, 1])
        self.assertEqual(m.stable_metadata(first["physical"]["path"]), before)

    def test_relative_diagnostic_history04_wrong_parent_fails_before_and_after_valid_seen_identity(self):
        with self.assertRaises(ValueError):
            self.observe(parent=str(self.root / "wrong.json"))
        self.observe()
        with self.assertRaises(ValueError):
            self.observe(parent=str(self.out / "relative_diagnostic_history_opaque_leaf_proof.json"))
        self.assertEqual(len(self.scope.observations), 1)

    def test_relative_diagnostic_history05_exact_field_and_tuple_trail_are_mandatory(self):
        for trail in ((), ("original_failure_history",), list(m._RELATIVE_DIAGNOSTIC_HISTORY_FIELD),
                      ("other", m._RELATIVE_DIAGNOSTIC_HISTORY_FIELD[1])):
            with self.subTest(trail=trail), self.assertRaises(ValueError):
                self.observe(trail=trail)
        self.assertFalse(self.scope.directory.exists())

    def test_relative_diagnostic_history06_unknown_module_is_rejected_even_after_valid_duplicate(self):
        self.observe()
        for module in sorted(m.REQUIRED_MODULES - set(m._RELATIVE_DIAGNOSTIC_HISTORY_MODULES)) + ["UNKNOWN"]:
            with self.subTest(module=module), self.assertRaises(ValueError):
                self.observe(module=module)
        self.assertEqual(len(self.scope.observations), 1)

    def test_relative_diagnostic_history07_full_original_tuple_cannot_fork(self):
        for key, value in (("path", str(self.root / "unknown.json")),
                           ("bytes", 0), ("sha256", "0" * 64)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.observe(receipt=dict(m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF, **{key: value}))
        self.assertFalse(self.scope.directory.exists())

    def test_relative_diagnostic_history08_same_fingerprint_clone_path_never_gains_permission(self):
        self.observe()
        clone = dict(m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF, path=str(self.root / "clone.json"))
        with self.assertRaises(ValueError):
            self.observe(receipt=clone)
        with self.assertRaises(ValueError):
            m.reject_relative_diagnostic_history_declaration(clone)
        self.assertEqual(len(self.scope.observations), 1)

    def test_relative_diagnostic_history09_direct_plan_declarations_cannot_bypass_edge_scope(self):
        for category in ("source", "gate", "seed", "context", "logical_alias", "physical_alias",
                         "allocation_closure_gate", "root_terminal_rejection_gate",
                         "base_acceptance", "library_software_acceptance", "mapper_software_acceptance"):
            value = plan()
            module = value["modules"][0]
            leaf = dict(m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF)
            if category == "source":
                module["sources"][0]["receipt"] = leaf
            elif category == "gate":
                module["gate"]["receipt"] = leaf
            elif category == "seed":
                module["seeds"] = [leaf]
            elif category == "context":
                value["context_parent_seeds"] = [leaf]
            elif category == "logical_alias":
                value["aliases"] = [{"logical": leaf, "physical": r(str(self.root / "copy.txt"))}]
            elif category == "physical_alias":
                value["aliases"] = [{"logical": r(str(self.root / "ordinary.json")), "physical": leaf}]
            elif category in ("allocation_closure_gate", "root_terminal_rejection_gate"):
                module[category] = {"receipt": leaf}
            else:
                value[category] = leaf
            with self.subTest(category=category), self.assertRaises(ValueError):
                m.module_plan(value)

    def test_relative_diagnostic_history10_unrelated_receipt_remains_on_ordinary_route(self):
        ordinary = r(str(self.root / "ordinary.json"), 2, "c" * 64)
        self.assertIsNone(self.scope.edge(ordinary, None, (), "scientific_report"))
        m.reject_relative_diagnostic_history_declaration(ordinary)
        self.assertFalse(self.scope.directory.exists())

    def test_relative_diagnostic_history11_zero_actual_or_foreign_base_cannot_be_accepted(self):
        with self.assertRaises(ValueError):
            self.scope.require_complete()
        scope = m.RelativeDiagnosticHistoryOpaqueLeaf(self.out, r(str(self.root / "foreign.json")))
        self.assertFalse(scope.require_complete())
        with self.assertRaises(ValueError):
            scope.edge(m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF, m._RELATIVE_DIAGNOSTIC_HISTORY_BASE["path"], m._RELATIVE_DIAGNOSTIC_HISTORY_FIELD,
                       "default_workflow_integration")
        self.assertFalse(scope.directory.exists())

    def test_relative_diagnostic_history12_schema_status_and_all_diagnostic_policy_flags_are_strict(self):
        for field in ("schema", "status") + m._RELATIVE_DIAGNOSTIC_HISTORY_FALSE_FLAGS + m._RELATIVE_DIAGNOSTIC_HISTORY_TRUE_FLAGS:
            document = copy.deepcopy(self.document)
            document[field] = "OTHER" if field in ("schema", "status") else not document[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.relative_diagnostic_history_document_shape(document)

    def test_relative_diagnostic_history13_utf8_duplicate_nonfinite_and_overflow_are_rejected(self):
        for raw in (b"\xff", b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e9999}'):
            self.replace_document(raw=raw)
            with self.subTest(raw=raw), self.assertRaises((ValueError, UnicodeDecodeError)):
                self.observe()
            self.assertFalse(self.scope.directory.exists())

    def test_relative_diagnostic_history14_thirteen_keys_three_records_five_file_metadata_are_strict(self):
        kinds = ("extra_top", "missing_top", "identity_bool", "extra_diagnostic", "parent", "schema_bool",
                 "record_count", "file_count", "bool_size", "duplicate_path", "record_bool", "ordinal_bool",
                 "record_keys", "record_link", "record_sha", "session_path", "recovery_type")
        for kind in kinds:
            document = copy.deepcopy(self.document)
            diagnostic = document["diagnostic"]
            snapshot = diagnostic["parent_JSON"]
            files = snapshot["files"]
            if kind == "extra_top":
                document["unexpected"] = True
            elif kind == "missing_top":
                document.pop("CPUs")
            elif kind == "identity_bool":
                document["CPUs"] = True
            elif kind == "extra_diagnostic":
                diagnostic["unexpected"] = 1
            elif kind == "parent":
                diagnostic["parent"] = r(str(self.root / "other_parent.json"))
            elif kind == "schema_bool":
                snapshot["schema_version"] = True
            elif kind == "record_count":
                snapshot["records"].pop()
            elif kind == "file_count":
                files.pop()
            elif kind == "bool_size":
                files[0]["bytes"] = True
            elif kind == "duplicate_path":
                files[1]["path"] = files[0]["path"]
            elif kind == "record_bool":
                snapshot["records"][0]["record_number"] = True
            elif kind == "ordinal_bool":
                snapshot["records"][0]["ordinal"] = True
            elif kind == "record_keys":
                snapshot["records"][0]["extra"] = True
            elif kind == "record_link":
                snapshot["records"][0]["output_file"] = files[1]["path"]
            elif kind == "record_sha":
                snapshot["records"][0]["output_sha256"] = "c" * 64
            elif kind == "session_path":
                snapshot["source_session_file"] = "NEVER_OPEN_OTHER_SESSION"
            else:
                snapshot["recovery_type"] = "AUTHORIZED"
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                m.relative_diagnostic_history_document_shape(document)

    def test_relative_diagnostic_history15_files4_is_scalar_and_old_two_history_shapes_remain_unchanged(self):
        for kind in ("source_field", "offending", "error", "relative_parent"):
            document = copy.deepcopy(self.document)
            diagnostic = document["diagnostic"]
            if kind == "source_field":
                diagnostic["source_field"] = ["files", "0"]
            elif kind == "offending":
                diagnostic["offending_receipt"] = diagnostic["parent_JSON"]["files"][0]
            elif kind == "error":
                diagnostic["error"] = "AUTHORIZED"
            else:
                diagnostic["parent_relative_to_authority"] = "other.json"
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                m.relative_diagnostic_history_document_shape(document)
        old = InventoryHistoryDataContracts("test_history01_default_preserves_all_bytes_without_member_io")
        old.setUp()
        try:
            self.assertTrue(m.inventory_history_document_shape(old.document))
            self.assertEqual([len(x["parent_JSON"]["members"]) for x in old.document["parents"]], [193, 395])
            self.assertEqual(len(old.document["edges"]), 588)
        finally:
            old.tearDown()
        archive = ArchiveParentHistoryDataContracts("test_archive_parent_history01_default_preserves_all_bytes_without_member_io")
        archive.setUp()
        try:
            self.assertTrue(m.archive_parent_history_document_shape(archive.document))
            self.assertEqual(len(archive.document["diagnostic"]["parent_JSON"]["members"]), 193)
        finally:
            archive.tearDown()

    def test_relative_diagnostic_history16_full_base_authority_and_independent_edges_are_mandatory(self):
        original = self.base_path.read_bytes()
        self.base_path.chmod(0o644)
        self.base_path.write_bytes(original + b" ")
        self.base_path.chmod(0o444)
        with self.assertRaises(ValueError):
            self.observe()
        for field in (m._RELATIVE_DIAGNOSTIC_HISTORY_FIELD[1], "original13293_executing_source",
                      "original13293_software_only_acceptance"):
            base = json.loads(original)
            base["original_failure_history"][field] = r(str(self.root / "wrong.json"))
            m._RELATIVE_DIAGNOSTIC_HISTORY_BASE = self.write(self.base_path, json.dumps(base).encode())
            self.scope = m.RelativeDiagnosticHistoryOpaqueLeaf(self.out, m._RELATIVE_DIAGNOSTIC_HISTORY_BASE)
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.observe()

    def test_relative_diagnostic_history17_writable_original_or_parent_is_forbidden(self):
        for path in (self.base_path, self.leaf):
            path.chmod(0o644)
            try:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    self.observe()
            finally:
                path.chmod(0o444)

    def test_relative_diagnostic_history18_symlink_leaf_and_ancestor_are_not_alias_permissions(self):
        backup = self.root / "backup.json"
        self.write(backup, self.content)
        self.leaf.unlink()
        self.leaf.symlink_to(backup)
        with self.assertRaises(ValueError):
            self.observe()
        self.leaf.unlink()
        self.write(self.leaf, self.content)
        linked = self.root / "linked"
        linked.symlink_to(self.leaf.parent, target_is_directory=True)
        clone = dict(m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF, path=str(linked / self.leaf.name))
        with self.assertRaises(ValueError):
            self.observe(receipt=clone)

    def test_relative_diagnostic_history19_parent_original_and_copy_hardlinks_are_rejected(self):
        for path in (self.base_path, self.leaf):
            link = self.root / "hardlink"
            m.os.link(path, link)
            try:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    self.observe()
            finally:
                link.unlink()
        edge = self.observe()
        link = self.root / "copy_hardlink"
        m.os.link(edge["physical"]["path"], link)
        try:
            with self.assertRaises(ValueError):
                self.scope.readback()
        finally:
            link.unlink()

    def test_relative_diagnostic_history20_input_metadata_drift_after_valid_output_is_detected(self):
        self.observe()
        before = m.stable_metadata(self.leaf)
        changed = before["mtime_ns"] + 2000000000
        m.os.utime(self.leaf, ns=(changed, changed))
        with self.assertRaises(ValueError):
            self.scope.readback()
        self.assertFalse((self.out / "acceptance.json").exists())

    def test_relative_diagnostic_history21_changed_original_bytes_are_not_reaccepted(self):
        self.observe()
        self.leaf.chmod(0o644)
        self.leaf.write_bytes(self.content + b" ")
        self.leaf.chmod(0o444)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_relative_diagnostic_history22_copy_writability_or_changed_content_is_fatal(self):
        edge = self.observe()
        path = Path(edge["physical"]["path"])
        path.chmod(0o644)
        with self.assertRaises(ValueError):
            self.scope.readback()
        path.write_bytes(b"CHANGED")
        path.chmod(0o444)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_relative_diagnostic_history23_directory0555_is_independent_of_synchronized_proof_metadata(self):
        proof, aliases, allocation = self.saved()
        self.scope.directory.chmod(0o755)
        proof["copy_directory_metadata"] = m.stable_metadata(self.scope.directory)
        with self.assertRaisesRegex(ValueError, "readonly0555"):
            m.relative_diagnostic_history_proof_shape(proof, aliases, allocation)
        with self.assertRaises(ValueError):
            m.verify_relative_diagnostic_history_preservation(proof, aliases, allocation)

    def test_relative_diagnostic_history24_exclusive_collision_and_exact_one_file_universe(self):
        self.scope.directory.mkdir()
        sentinel = self.scope.directory / "SENTINEL"
        sentinel.write_text("DO_NOT_OVERWRITE")
        with self.assertRaises(FileExistsError):
            self.observe()
        self.assertEqual(sentinel.read_text(), "DO_NOT_OVERWRITE")
        sentinel.unlink()
        self.scope.directory.rmdir()
        self.observe()
        self.scope.directory.chmod(0o755)
        (self.scope.directory / "extra.txt").write_text("EXTRA")
        self.scope.directory.chmod(0o555)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_relative_diagnostic_history25_fsync_failure_never_accepts_or_changes_originals(self):
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        before = [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)]
        with patch.object(m.os, "fsync", side_effect=OSError("SYNTHETIC_FSYNC_FAILURE")):
            with self.assertRaises(OSError):
                self.observe()
        self.assertEqual(before, [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)])
        self.assertFalse(self.scope.observations)
        self.assertFalse((self.out / "acceptance.json").exists())

    def test_relative_diagnostic_history26_pure_full_proof_rejects_flags_metadata_counts_and_extra_keys(self):
        proof, aliases, allocation = self.saved()
        self.assertTrue(m.relative_diagnostic_history_proof_shape(proof, aliases, allocation))
        for field, value in (("schema", "OTHER"), ("authorized_observation_n", True),
                             ("embedded_receipt_occurrence_n", 5), ("embedded_targets_statted_or_opened", True),
                             ("archive_or_scientific_acceptance", True), ("unexpected", 1)):
            fork = copy.deepcopy(proof)
            fork[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.relative_diagnostic_history_proof_shape(fork, aliases, allocation)
        fork = copy.deepcopy(proof)
        fork["original_metadata_before"]["inode"] = True
        with self.assertRaises(ValueError):
            m.relative_diagnostic_history_proof_shape(fork, aliases, allocation)

    def test_relative_diagnostic_history27_alias_pointer_status_allocation_and_context_tampering_fail(self):
        proof, aliases, allocation = self.saved()
        for kind in ("alias_status", "alias_receipt", "pointer", "allocation", "module", "order", "ordinal"):
            fork, index = copy.deepcopy(proof), copy.deepcopy(aliases)
            if kind == "alias_status":
                index["aliases"][0]["status"] = "OTHER"
            elif kind == "alias_receipt":
                index["aliases"][0]["archived"]["sha256"] = "0" * 64
            elif kind == "pointer":
                fork["exact_alias_index"]["path"] = str(self.root / "other.json")
            elif kind == "allocation":
                fork["allocation"] = {"job_id": "OTHER"}
            elif kind == "module":
                fork["observations"][0]["module"] = "scientific_report"
            elif kind == "order":
                fork["observations"][0]["field"].reverse()
            else:
                fork["observations"][0]["ordinal"] = True
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                m.relative_diagnostic_history_proof_shape(fork, index, allocation)

    def test_relative_diagnostic_history28_pure_validator_has_no_filesystem_or_live_source_calls(self):
        proof, aliases, allocation = self.saved()
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        with patch.object(Path, "open", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "stat", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "lstat", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "resolve", side_effect=AssertionError("NO_FS")), \
             patch.object(m, "rec", side_effect=AssertionError("NO_LIVE_SHA")), \
             patch.object(m, "verify", side_effect=AssertionError("NO_LIVE_VERIFY")), \
             patch.object(m.os, "open", side_effect=AssertionError("NO_OS_OPEN")):
            self.assertTrue(m.relative_diagnostic_history_document_shape(self.document))
            self.assertTrue(m.relative_diagnostic_history_proof_shape(proof, aliases, allocation))

    def test_relative_diagnostic_history29_production_saved_verifier_checks_current_bytes_and_index(self):
        proof, aliases, allocation = self.saved()
        self.assertTrue(m.verify_relative_diagnostic_history_preservation(proof, aliases, allocation))
        pointer = Path(proof["exact_alias_index"]["path"])
        pointer.chmod(0o644)
        pointer.write_text(json.dumps({"schema": "CHANGED"}))
        pointer.chmod(0o444)
        with self.assertRaises(ValueError):
            m.verify_relative_diagnostic_history_preservation(proof, aliases, allocation)

    def test_relative_diagnostic_history30_genuine_audit_retains_independent_producer_software_and_data_role(self):
        self.assertIsNotNone(self.run_genuine_audit())

    def test_relative_diagnostic_history31_genuine_queue_rejects_wrong_context_after_valid_seen_copy(self):
        self.run_genuine_audit(invalid_after_valid=True)

    def test_relative_diagnostic_history32_genuine_audit_cannot_use_plan_alias_as_direct_data_permission(self):
        self.run_genuine_audit(direct_alias=True)



class RelativeDiagnosticHistoryInheritedRouteContracts(unittest.TestCase):
    """Reach nested actual audit guards with test-only row/edge isolation."""

    def run_route(self, route):
        import inspect
        fixture = ClosureFixtureContracts("test_real_closure_preserves_old_and_accepts_new_default")
        fixture.setUp()
        case = RelativeDiagnosticHistoryDataContracts("test_relative_diagnostic_history01_default_preserves_all_bytes_without_member_io")
        saved_private = {name: copy.deepcopy(getattr(m, name)) for name in case.private_names}
        guard_calls = []
        mutation_calls = []
        original_guard = m.reject_relative_diagnostic_history_declaration
        original_route = m.inherited_source_route
        try:
            case.install(fixture.root / "inherited_history_case")
            base = m.read(fixture.p["base_acceptance"]["path"])
            if route == "closure_physical_alias":
                closure = dict(schema="benchmark-source-receipt-closure.v1", edges=[
                    dict(receipt=r(str(fixture.root / "ordinary_alias.py"), 1, "c" * 64),
                         parent=str(fixture.asset / "ordinary_parent.json"), field=["source"],
                         physical=m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF, resolution_basis="EXACT_ORIGINAL",
                         role="EXACT_TEXT_RECEIPT_READBACK")])
                closure_receipt = fixture.meta("history_alias_closure.json", closure)
                inclusion = m.read(base["source_inclusion"]["path"])
                inclusion["source_receipt_closure"] = closure_receipt
                inclusion_receipt = fixture.meta("history_alias_inclusion.json", inclusion)
                base["source_closure"] = closure_receipt
                base["source_inclusion"] = inclusion_receipt
            case.replace_document(case.document, base_overlay=base)
            fixture.p["base_acceptance"] = m._RELATIVE_DIAGNOSTIC_HISTORY_BASE
            default = next(x for x in fixture.p["modules"] if x["role"] == "default_workflow_integration")
            if route == "resolve":
                default["seeds"] = [m._RELATIVE_DIAGNOSTIC_HISTORY_BASE]
                fixture.p["modules"] = [x for x in fixture.p["modules"] if x is not default] + [default]

            def guard_spy(receipt):
                caller = inspect.currentframe().f_back
                if receipt == m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF:
                    guard_calls.append(dict(caller=caller.f_code.co_name,
                                            r=copy.deepcopy(caller.f_locals.get("r")),
                                            logical=copy.deepcopy(caller.f_locals.get("logical")),
                                            receipt=copy.deepcopy(receipt)))
                return original_guard(receipt)

            def route_wrapper(row, operations):
                result = original_route(row, operations)
                if row["repository_relative"] == "rebuild/unrelated.py":
                    if route == "add_source":
                        row["source"] = dict(m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF)
                    elif route == "add_logical":
                        self.assertNotEqual(m.fp(row["source"]), m.fp(m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF))
                        row["original_source"] = dict(m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF)
                    mutation_calls.append(route)
                return result

            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            stack = __import__("contextlib").ExitStack()
            with stack:
                stack.enter_context(patch.object(m, "cpu", return_value={
                    "job_id": "50003", "allocated_CPUs": 1, "allocated_gpus": 0}))
                stack.enter_context(patch.object(m, "reject_relative_diagnostic_history_declaration",
                                                new=guard_spy))
                if route in ("add_source", "add_logical"):
                    stack.enter_context(patch.object(m, "inherited_source_route",
                                                    side_effect=route_wrapper))
                elif route == "resolve":
                    # Only a synthetic edge route is disabled to exercise later defense.
                    stack.enter_context(patch.object(m.RelativeDiagnosticHistoryOpaqueLeaf, "edge",
                                                    return_value=None))
                with self.assertRaisesRegex(
                        ValueError, "Fixed13295 diagnostic DATA cannot be direct SOURCE/gate/seed/context/Plan alias"):
                    fixture.run_fixture()
            out = fixture.root / "audit_out"
            self.assertFalse((out / "acceptance.json").exists())
            self.assertFalse((out / "source_inclusion_final.json").exists())
            self.assertFalse((out / "opaque_relative_diagnostic_history_bytes").exists())
            self.assertFalse((out / "relative_diagnostic_history_opaque_leaf_proof.json").exists())
            incomplete = m.read(out / "typed_incomplete.json")
            expected_stage = "recursive_exact_new_dependencies" if route == "resolve" else "base_readback"
            self.assertEqual(incomplete["failed_stage"], expected_stage)
            self.assertEqual(incomplete["reason_type"], "ValueError")
            self.assertEqual(incomplete["reason"],
                             "Fixed13295 diagnostic DATA cannot be direct SOURCE/gate/seed/context/Plan alias")
            expected_caller = "add" if route.startswith("add_") else "alias" if route == "closure_physical_alias" else "resolve"
            hits = [x for x in guard_calls if x["caller"] == expected_caller]
            self.assertEqual(len(hits), 1)
            if route == "add_source":
                self.assertEqual(hits[0]["r"], m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF)
                self.assertNotEqual(hits[0]["logical"], m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF)
                self.assertEqual(mutation_calls, ["add_source"])
            elif route == "add_logical":
                self.assertEqual(hits[0]["logical"], m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF)
                self.assertNotEqual(m.fp(hits[0]["r"]), m.fp(m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF))
                self.assertEqual(mutation_calls, ["add_logical"])
            elif route == "resolve":
                self.assertEqual(hits[0]["r"], m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF)
            else:
                self.assertEqual(hits[0]["receipt"], m._RELATIVE_DIAGNOSTIC_HISTORY_LEAF)
        finally:
            for name, value in saved_private.items():
                setattr(m, name, value)
            fixture.tearDown()

    def test_relative_diagnostic_history33_inherited_source_reaches_actual_add_r_direct_guard(self):
        self.run_route("add_source")

    def test_relative_diagnostic_history34_inherited_logical_reaches_actual_add_logical_guard(self):
        self.run_route("add_logical")

    def test_relative_diagnostic_history35_inherited_closure_physical_alias_reaches_actual_nested_alias_guard(self):
        self.run_route("closure_physical_alias")

    def test_relative_diagnostic_history36_queue_edge_isolation_reaches_actual_nested_resolve_guard(self):
        self.run_route("resolve")


class RelativeDiagnosticHistoryOutputControlContracts(unittest.TestCase):
    def test_relative_diagnostic_history37_fixed_control_writer_is_exclusive_fsynced_and_failure_retains_data(self):
        case = RelativeDiagnosticHistoryDataContracts("test_relative_diagnostic_history01_default_preserves_all_bytes_without_member_io")
        case.setUp()
        try:
            case.observe()
            alias = case.scope.alias_index()
            path = case.out / "relative_diagnostic_history_opaque_aliases.json"
            pointer, metadata = m._relative_diagnostic_history_write_control(path, alias)
            actual, after = m._relative_diagnostic_history_control_readback(pointer, metadata)
            self.assertEqual(actual, alias)
            self.assertEqual(after, metadata)
            self.assertEqual(metadata["mode"] & 0o777, 0o444)
            self.assertEqual(metadata["nlink"], 1)
            with self.assertRaises(FileExistsError):
                m._relative_diagnostic_history_write_control(path, alias)
            failure = case.out / "relative_diagnostic_history_opaque_leaf_proof.json"
            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            with patch.object(m.os, "fsync", side_effect=OSError("SYNTHETIC_CONTROL_FSYNC")):
                with self.assertRaisesRegex(OSError, "SYNTHETIC_CONTROL_FSYNC"):
                    m._relative_diagnostic_history_write_control(failure, {"fixture": True})
            self.assertEqual(Path(case.scope.copy_receipt["path"]).read_bytes(), case.content)
            self.assertFalse((case.out / "acceptance.json").exists())
        finally:
            case.tearDown()

    def test_relative_diagnostic_history38_both_controls_reject_mode_hardlink_native_drift_and_post_json_mutation(self):
        case = RelativeDiagnosticHistoryDataContracts("test_relative_diagnostic_history01_default_preserves_all_bytes_without_member_io")
        case.setUp()
        try:
            proof, alias, allocation = case.saved()
            proof_pointer, proof_metadata = m._relative_diagnostic_history_write_control(
                case.out / "relative_diagnostic_history_opaque_leaf_proof.json", proof)
            for pointer in (proof_pointer, proof["exact_alias_index"]):
                path = Path(pointer["path"])
                expected = m._relative_diagnostic_history_control_metadata(path)
                path.chmod(0o400)
                with self.subTest(control=path.name, boundary="exact444"), self.assertRaises(ValueError):
                    m._relative_diagnostic_history_control_readback(pointer)
                path.chmod(0o444)
                link = case.root / (path.name + ".hardlink")
                m.os.link(path, link)
                try:
                    with self.subTest(control=path.name, boundary="singlelink"), self.assertRaises(ValueError):
                        m._relative_diagnostic_history_control_readback(pointer)
                finally:
                    link.unlink()
                expected = m._relative_diagnostic_history_control_metadata(path)
                raw = path.read_bytes()
                original_json = m._strict_relative_diagnostic_history_json
                hits = []
                def mutate_after_json(text):
                    value = original_json(text)
                    if text.encode("utf-8") == raw:
                        current = m.stable_metadata(path)
                        changed = current["mtime_ns"] + 2000000000
                        m.os.utime(path, ns=(changed, changed))
                        hits.append(path.name)
                    return value
                patch = __import__("unittest.mock", fromlist=["patch"]).patch
                with patch.object(m, "_strict_relative_diagnostic_history_json", side_effect=mutate_after_json):
                    with self.subTest(control=path.name, boundary="post_last_JSON"), self.assertRaisesRegex(
                            ValueError, "Fixed13295 control changed during own JSON readback"):
                        m._relative_diagnostic_history_control_readback(pointer, expected)
                self.assertEqual(hits, [path.name])
                with self.subTest(control=path.name, boundary="stored_metadata"), self.assertRaises(ValueError):
                    m._relative_diagnostic_history_control_readback(pointer, expected)
            self.assertEqual(Path(case.scope.copy_receipt["path"]).read_bytes(), case.content)
            self.assertFalse((case.out / "acceptance.json").exists())
        finally:
            case.tearDown()


class RelativeDiagnosticHistoryFinalReadonlyLifecycleContracts(unittest.TestCase):
    """Exercise the unchanged genuine audit through its final readonly loop."""

    def run_final_readonly_fixture(self, writable_output):
        import inspect
        case = RelativeDiagnosticHistoryDataContracts(
            "test_relative_diagnostic_history01_default_preserves_all_bytes_without_member_io")
        case.setUp()
        original_audit = m.audit
        original_writer = m._relative_diagnostic_history_write_control
        original_dump = m.dump
        original_chmod = Path.chmod
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        controls = {}
        repeated_chmods = []
        writable_chmods = []
        writable = {}
        completed = []
        control_names = {"relative_diagnostic_history_opaque_leaf_proof.json",
                         "relative_diagnostic_history_opaque_aliases.json"}

        def remember_writer(path, obj):
            result = original_writer(path, obj)
            path = Path(path)
            self.assertIn(path.name, control_names)
            self.assertNotIn(path, controls)
            controls[path] = (copy.deepcopy(result[0]), copy.deepcopy(result[1]))
            return result

        def observe_chmod(path, mode, *args, **kwargs):
            path = Path(path)
            if path in controls and mode == 0o444 and path.lstat().st_mode & 0o7777 == 0o444:
                # The old final loop would reach this real same-mode chmod.
                # Make its own-fixture metadata effect deterministic, without
                # replacing any metadata reader or production drift guard.
                repeated_chmods.append(str(path))
                result = original_chmod(path, mode, *args, **kwargs)
                native = path.lstat()
                m.os.utime(path, ns=(native.st_atime_ns,
                                    native.st_mtime_ns + 2000000000))
                return result
            if path == writable.get("path"):
                caller = inspect.currentframe().f_back.f_code.co_name
                before = m.stable_metadata(path)
                result = original_chmod(path, mode, *args, **kwargs)
                writable_chmods.append(dict(caller=caller, requested_mode=mode,
                                            before=before, after=m.stable_metadata(path)))
                return result
            return original_chmod(path, mode, *args, **kwargs)

        def publish_with_writable_output(path, obj):
            receipt = original_dump(path, obj)
            path = Path(path)
            if writable_output and path.name == "acceptance.json" and path.parent.name == "audit_out":
                self.assertFalse(writable)
                target = path.parent / "synthetic_final_readonly_writable.json"
                content = b'{"fixture_only": true, "no_child_receipts": true}\n'
                flags = m.os.O_WRONLY | m.os.O_CREAT | m.os.O_EXCL | getattr(m.os, "O_NOFOLLOW", 0)
                fd = m.os.open(target, flags, 0o600)
                with m.os.fdopen(fd, "wb") as stream:
                    stream.write(content)
                    stream.flush()
                    m.os.fsync(stream.fileno())
                writable.update(path=target, content=content,
                                metadata=m.stable_metadata(target))
                self.assertEqual(writable["metadata"]["mode"] & 0o7777, 0o600)
            return receipt

        def audit_and_check_final_readback(*args, **kwargs):
            result = original_audit(*args, **kwargs)
            self.assertEqual({path.name for path in controls}, control_names)
            self.assertEqual(len(controls), 2)
            for path, (receipt, metadata) in controls.items():
                self.assertEqual(m.rec(path), receipt)
                self.assertEqual(m.stable_metadata(path), metadata)
                self.assertEqual(metadata["mode"] & 0o7777, 0o444)
                self.assertEqual(metadata["nlink"], 1)
            self.assertEqual(repeated_chmods, [])
            if writable_output:
                self.assertIn("path", writable)
                self.assertEqual(len(writable_chmods), 1)
                event = writable_chmods[0]
                self.assertEqual(event["caller"], "audit")
                self.assertEqual(event["requested_mode"], 0o444)
                self.assertEqual(event["before"], writable["metadata"])
                self.assertEqual(event["before"]["mode"] & 0o7777, 0o600)
                self.assertEqual(event["after"]["mode"] & 0o7777, 0o444)
                self.assertEqual(event["after"]["nlink"], 1)
                self.assertEqual(writable["path"].read_bytes(), writable["content"])
                self.assertEqual(m.stable_metadata(writable["path"]), event["after"])
            else:
                self.assertEqual(writable, {})
                self.assertEqual(writable_chmods, [])
            completed.append(True)
            return result

        try:
            with patch.object(m, "_relative_diagnostic_history_write_control", side_effect=remember_writer), \
                 patch.object(m, "dump", side_effect=publish_with_writable_output), \
                 patch.object(Path, "chmod", new=observe_chmod), \
                 patch.object(m, "audit", side_effect=audit_and_check_final_readback):
                self.assertIsNotNone(case.run_genuine_audit())
            self.assertEqual(completed, [True])
            self.assertIs(m.audit, original_audit)
            self.assertIs(m.dump, original_dump)
            self.assertIs(m._relative_diagnostic_history_write_control, original_writer)
            self.assertIs(Path.chmod, original_chmod)
        finally:
            case.tearDown()

    def test_relative_diagnostic_history39_genuine_audit_final_seal_preserves_exact444_control_metadata(self):
        self.run_final_readonly_fixture(writable_output=False)

    def test_relative_diagnostic_history40_genuine_audit_final_seal_converts_writable_owned_JSON(self):
        self.run_final_readonly_fixture(writable_output=True)


class ParentDiagnosticHistoryDataContracts(unittest.TestCase):
    """Synthetic own-byte fixtures; no live member/SCI source is opened by these cases."""

    private_names = ("_FIXED_HISTORY_MAPPING_PARENTS", "_FIXED_HISTORY_MAPPING_PROVENANCE", "_PARENT_DIAGNOSTIC_HISTORY_BASE", "_PARENT_DIAGNOSTIC_HISTORY_AUTHORITY", "_PARENT_DIAGNOSTIC_HISTORY_LEAF",
                     "_PARENT_DIAGNOSTIC_HISTORY_PRODUCER", "_PARENT_DIAGNOSTIC_HISTORY_V4_SOURCE", "_PARENT_DIAGNOSTIC_HISTORY_RECOVERED_PARENT",
                     "_PARENT_DIAGNOSTIC_HISTORY_PREVIOUS_EDGE_PARENT")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_root = m.R
        self.old_private = {name: copy.deepcopy(getattr(m, name)) for name in self.private_names}
        m.R = self.root
        self.install(self.root / "case")
        self.out = self.root / "out"
        self.out.mkdir()
        self.scope = m.ParentDiagnosticHistoryOpaqueLeaf(self.out, m._PARENT_DIAGNOSTIC_HISTORY_BASE)

    def tearDown(self):
        for name, value in self.old_private.items():
            setattr(m, name, value)
        m.R = self.old_root
        for path in self.root.rglob("*"):
            if path.is_dir() and not path.is_symlink():
                path.chmod(0o755)
        self.tmp.cleanup()

    @staticmethod
    def write(path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.chmod(0o644)
        path.write_bytes(raw)
        path.chmod(0o444)
        return m.rec(path)

    def install(self, root):
        root.mkdir(parents=True, exist_ok=True)
        m._PARENT_DIAGNOSTIC_HISTORY_AUTHORITY = str(m.R)
        self.producer = root / "producer.py"
        self.v4_source = root / "sealed_v4.py"
        m._PARENT_DIAGNOSTIC_HISTORY_PRODUCER = self.write(self.producer, b"raise AssertionError('SOURCE_COPY_ONLY_MUST_NOT_EXECUTE')\n")
        m._PARENT_DIAGNOSTIC_HISTORY_V4_SOURCE = self.write(self.v4_source, b"raise RuntimeError('SEALED_SOURCE_COPY_ONLY_MUST_NOT_EXECUTE')\n")
        m._PARENT_DIAGNOSTIC_HISTORY_RECOVERED_PARENT = r(str(root / "never_open_recovered_parent.json"), 4665, "1" * 64)
        m._PARENT_DIAGNOSTIC_HISTORY_PREVIOUS_EDGE_PARENT = str(root / "never_open_previous_edge_parent.json")
        previous = dict(receipt=m._PARENT_DIAGNOSTIC_HISTORY_RECOVERED_PARENT,
                        parent=m._PARENT_DIAGNOSTIC_HISTORY_PREVIOUS_EDGE_PARENT, field=["inputs"],
                        physical=m._PARENT_DIAGNOSTIC_HISTORY_RECOVERED_PARENT,
                        resolution_basis="EXACT_ORIGINAL", relative_context=None, role="EXACT_TEXT_RECEIPT_READBACK")
        failure = dict(diagnostic_only=True, source_V4_guard_unchanged=True, external_original_not_read=True,
                       attempted_receipt=copy.deepcopy(m._PARENT_DIAGNOSTIC_HISTORY_ATTEMPT),
                       original_error_type="ValueError", original_error="Source receipt escapes authority",
                       context=dict(parent_original_logical_path=m._PARENT_DIAGNOSTIC_HISTORY_RECOVERED_PARENT["path"],
                                    source_field=["entries", "2", "design_manifest"], previous_verified_parent_edge=previous,
                                    declared_basename_candidates=[], declared_same_size_candidates=[], exact_declared_alias_hit=False))
        self.document = dict(schema="source-closure-exact-parent-diagnostic.v1",
                             status="DIAGNOSTIC_ONLY_NOT_SOURCE_ACCEPTANCE",
                             allocation=dict(job_id="13290", scheduler_record="JobId=13290 NumCPUs=1 TRES=cpu=1,node=1 ", allocated_gpus=0),
                             source=m._PARENT_DIAGNOSTIC_HISTORY_PRODUCER, original_sealed_V4_source=m._PARENT_DIAGNOSTIC_HISTORY_V4_SOURCE,
                             actual13279_and13285_history_preserved=True, strict_authority_guard_weakened=False,
                             default_or_scientific_inputs_changed=False, GPU_allocated=0, replay_unexpectedly_completed=False,
                             exact_calls=1660, failure_context=failure, error_type="ValueError",
                             error=json.dumps(failure), traceback="ValueError: Source receipt escapes authority\nSYNTHETIC_HISTORY")
        self.leaf = root / "diagnostic.json"
        self.base_path = root / "base.json"
        self.replace_document(self.document)

    def replace_document(self, document=None, raw=None, base_overlay=None):
        if document is not None:
            self.document = document
        if raw is None:
            raw = json.dumps(self.document, allow_nan=False).encode("utf-8")
        self.content = raw
        m._PARENT_DIAGNOSTIC_HISTORY_LEAF = self.write(self.leaf, raw)
        # Source1 has NO alternate sibling/seed: only the actual ordinary child
        # emitter can create its inclusion row. V4 keeps its independent sibling.
        history = {m._PARENT_DIAGNOSTIC_HISTORY_FIELD[1]: m._PARENT_DIAGNOSTIC_HISTORY_LEAF,
                   "original13279_failed_executing_source": m._PARENT_DIAGNOSTIC_HISTORY_V4_SOURCE}
        base = dict(base_overlay or {}, schema="source-delivery-refresh.v3",
                    status="CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY",
                    source_issues=0, source_staged=False, original_failure_history=history)
        base = install_fixed_mapping_fixture(self, base, "parent13290")
        m._PARENT_DIAGNOSTIC_HISTORY_BASE = self.write(self.base_path, json.dumps(base).encode("utf-8"))
        if hasattr(self, "out") and self.out.is_relative_to(m.R):
            self.scope = m.ParentDiagnosticHistoryOpaqueLeaf(self.out, m._PARENT_DIAGNOSTIC_HISTORY_BASE)

    def observe(self, receipt=None, parent=None, trail=None,
                module="default_workflow_integration"):
        return self.scope.edge(
            m._PARENT_DIAGNOSTIC_HISTORY_LEAF if receipt is None else receipt,
            m._PARENT_DIAGNOSTIC_HISTORY_BASE["path"] if parent is None else parent,
            m._PARENT_DIAGNOSTIC_HISTORY_FIELD if trail is None else trail, module)

    def saved(self):
        self.observe()
        allocation = {"job_id": "50001", "allocated_CPUs": 1, "allocated_gpus": 0}
        aliases = self.scope.alias_index()
        pointer, unused = m._parent_diagnostic_history_write_control(self.out / "parent_diagnostic_history_opaque_aliases.json", aliases)
        proof = dict(self.scope.proof(), exact_alias_index=pointer, allocation=allocation)
        return proof, aliases, allocation

    def run_genuine_audit(self, invalid_after_valid=False, direct_alias=False, coverage_tamper=False):
        fixture = ClosureFixtureContracts("test_real_closure_preserves_old_and_accepts_new_default")
        fixture.setUp()
        saved = {name: copy.deepcopy(getattr(m, name)) for name in self.private_names}
        try:
            self.install(fixture.root / "history_case")
            original_base = m.read(fixture.p["base_acceptance"]["path"])
            self.replace_document(self.document, base_overlay=original_base)
            fixture.p["base_acceptance"] = m._PARENT_DIAGNOSTIC_HISTORY_BASE
            default = next(x for x in fixture.p["modules"] if x["role"] == "default_workflow_integration")
            default["seeds"] = [m._PARENT_DIAGNOSTIC_HISTORY_BASE]
            fixture.p["modules"] = [x for x in fixture.p["modules"] if x is not default] + [default]
            if invalid_after_valid:
                bad = fixture.meta("wrong_history_parent.json", {"wrong": m._PARENT_DIAGNOSTIC_HISTORY_LEAF})
                other = next(x for x in fixture.p["modules"] if x["role"] == "formal_common_review")
                other["seeds"] = [bad]
            if direct_alias:
                fixture.p["aliases"] = [{"logical": m._PARENT_DIAGNOSTIC_HISTORY_LEAF, "physical": m._PARENT_DIAGNOSTIC_HISTORY_LEAF}]
            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            with patch.object(m, "cpu", return_value={"job_id": "50002", "allocated_CPUs": 1,
                                                      "allocated_gpus": 0}):
                if invalid_after_valid or direct_alias:
                    with self.assertRaises(ValueError):
                        fixture.run_fixture()
                    out = fixture.root / "audit_out"
                    self.assertFalse((out / "acceptance.json").exists())
                    incomplete = m.read(out / "typed_incomplete.json")
                    if invalid_after_valid:
                        self.assertTrue((out / "opaque_parent_diagnostic_history_bytes").is_dir())
                        self.assertEqual(incomplete["failed_stage"], "recursive_exact_new_dependencies")
                        self.assertEqual(incomplete["reason"],
                                         "Fixed inherited history requires exact parent/field/two-module/fulltuple context")
                    else:
                        self.assertFalse((out / "opaque_parent_diagnostic_history_bytes").exists())
                        self.assertEqual(incomplete["failed_stage"], "explicit_plan")
                        self.assertEqual(incomplete["reason"],
                                         "Fixed13290 diagnostic DATA cannot be direct SOURCE/gate/seed/context/Plan alias")
                    self.assertEqual(incomplete["reason_type"], "ValueError")
                    return None
                inclusion = fixture.run_fixture()
                out = fixture.root / "audit_out"
                closure = m.read(out / "source_receipt_closure_final.json")
                acceptance = m.read(out / "acceptance.json")
                self.assertEqual(inclusion["parent_diagnostic_history_opaque_leaf_proof"],
                                 acceptance["parent_diagnostic_history_opaque_leaf_proof"])
                self.assertEqual(closure["parent_diagnostic_history_opaque_aliases"],
                                 acceptance["parent_diagnostic_history_opaque_aliases"])
                proof = m.read(acceptance["parent_diagnostic_history_opaque_leaf_proof"]["path"])
                self.assertTrue(m.parent_diagnostic_history_source_coverage(proof, closure, inclusion))
                source_edges = [x for x in closure["edges"] if x.get("parent") == m._PARENT_DIAGNOSTIC_HISTORY_LEAF["path"]]
                self.assertEqual([x["field"] for x in source_edges], [["original_sealed_V4_source"], ["source"]])
                self.assertTrue(all(x["role"] == "EXACT_NEW_TEXT_RECEIPT_READBACK" and x["module"] == "default_workflow_integration" for x in source_edges))
                for expected in (m._PARENT_DIAGNOSTIC_HISTORY_PRODUCER, m._PARENT_DIAGNOSTIC_HISTORY_V4_SOURCE):
                    self.assertTrue(any(m.fp(row["source"]) == m.fp(expected) and row["kind"] == "IMPLEMENTATION" for row in inclusion["files"]))
                self.assertTrue(any(x.get("receipt") == m._PARENT_DIAGNOSTIC_HISTORY_V4_SOURCE and x.get("parent") == m._PARENT_DIAGNOSTIC_HISTORY_BASE["path"] for x in closure["edges"]))
                if coverage_tamper:self.check_actual_coverage_boundaries(proof, closure, inclusion)
                self.assertFalse(any(m.fp(row["source"]) == m.fp(m._PARENT_DIAGNOSTIC_HISTORY_LEAF)
                                     for row in inclusion["files"]))
                return inclusion
        finally:
            for name, value in saved.items():
                setattr(m, name, value)
            fixture.tearDown()

    def check_actual_coverage_boundaries(self, proof, closure, inclusion):
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        with patch.object(Path, "open", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "stat", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "lstat", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "resolve", side_effect=AssertionError("NO_FS")), \
             patch.object(m, "rec", side_effect=AssertionError("NO_LIVE_SHA")), \
             patch.object(m, "verify", side_effect=AssertionError("NO_LIVE_VERIFY")):
            self.assertTrue(m.parent_diagnostic_history_source_coverage(proof, closure, inclusion))
            for kind in ("missing_edge", "field", "module", "role", "physical", "I_missing", "I_kind", "I_role", "I_identity", "DATA_missing"):
                c, included = copy.deepcopy(closure), copy.deepcopy(inclusion)
                edge = next(x for x in c["edges"] if x.get("parent") == m._PARENT_DIAGNOSTIC_HISTORY_LEAF["path"])
                if kind == "missing_edge":c["edges"].remove(edge)
                elif kind == "field":edge["field"] = ["other"]
                elif kind == "module":edge["module"] = "scientific_report"
                elif kind == "role":edge["role"] = "DATA_RECEIPT_RETAINED_NOT_RAW_REAUDITED"
                elif kind == "physical":edge["physical"]["sha256"] = "0" * 64
                elif kind == "DATA_missing":c["edges"] = [x for x in c["edges"] if x.get("receipt") != m._PARENT_DIAGNOSTIC_HISTORY_LEAF]
                elif kind == "I_missing":included["files"] = [x for x in included["files"] if m.fp(x["source"]) != m.fp(edge["receipt"])]
                else:
                    for row in included["files"]:
                        if m.fp(row["source"]) == m.fp(edge["receipt"]):
                            if kind == "I_kind":row["kind"] = "DOCUMENT"
                            elif kind == "I_role":row["roles"] = ["OTHER"]
                            else:row["original_source"] = dict(row["original_source"], path=str(self.root / "identity_fork.py"));row["logical_receipts"] = []
                with self.subTest(kind=kind), self.assertRaises(ValueError):
                    m.parent_diagnostic_history_source_coverage(proof, c, included)

    def test_parent_diagnostic_history01_default_preserves_all_bytes_without_member_io(self):
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        original_open = Path.open
        allowed = {self.base_path, self.leaf} | {Path(entry["receipt"]["path"]) for entry in m._FIXED_HISTORY_MAPPING_PARENTS}

        def guarded_open(path, *args, **kwargs):
            if Path(path) not in allowed and Path(path).parent != self.scope.directory:
                raise AssertionError("Unexpected child IO: " + str(path))
            return original_open(path, *args, **kwargs)

        before = [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)]
        with patch.object(Path, "open", guarded_open):
            edge = self.observe()
            self.assertTrue(self.scope.require_complete())
        self.assertEqual(Path(edge["physical"]["path"]).read_bytes(), self.content)
        self.assertEqual(before, [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)])
        self.assertFalse(edge["documentary_receipt_children_interpreted"])
        self.assertFalse(edge["source_or_configuration_promotion"])

    def test_parent_diagnostic_history02_prospective_module_is_allowed_but_not_forced_or_sufficient(self):
        self.observe(module="final_delivery_tools")
        with self.assertRaises(ValueError):
            self.scope.proof()
        self.observe()
        proof = self.scope.proof()
        self.assertEqual(proof["actual_default_observation_n"], 1)
        self.assertEqual(proof["actual_finaltools_observation_n"], 1)
        other = m.ParentDiagnosticHistoryOpaqueLeaf(self.root / "other", m._PARENT_DIAGNOSTIC_HISTORY_BASE)
        other.out.mkdir()
        other.edge(m._PARENT_DIAGNOSTIC_HISTORY_LEAF, m._PARENT_DIAGNOSTIC_HISTORY_BASE["path"], m._PARENT_DIAGNOSTIC_HISTORY_FIELD,
                   "default_workflow_integration")
        self.assertEqual(other.proof()["actual_finaltools_observation_n"], 0)

    def test_parent_diagnostic_history03_repeat_preserves_order_but_deduplicates_only_copy_io(self):
        first = self.observe()
        before = m.stable_metadata(first["physical"]["path"])
        second = self.observe()
        self.assertEqual(first, second)
        self.assertEqual([x["ordinal"] for x in self.scope.observations], [0, 1])
        self.assertEqual(m.stable_metadata(first["physical"]["path"]), before)

    def test_parent_diagnostic_history04_wrong_parent_fails_before_and_after_valid_seen_identity(self):
        with self.assertRaises(ValueError):
            self.observe(parent=str(self.root / "wrong.json"))
        self.observe()
        with self.assertRaises(ValueError):
            self.observe(parent=str(self.out / "parent_diagnostic_history_opaque_leaf_proof.json"))
        self.assertEqual(len(self.scope.observations), 1)

    def test_parent_diagnostic_history05_exact_field_and_tuple_trail_are_mandatory(self):
        for trail in ((), ("original_failure_history",), list(m._PARENT_DIAGNOSTIC_HISTORY_FIELD),
                      ("other", m._PARENT_DIAGNOSTIC_HISTORY_FIELD[1])):
            with self.subTest(trail=trail), self.assertRaises(ValueError):
                self.observe(trail=trail)
        self.assertFalse(self.scope.directory.exists())

    def test_parent_diagnostic_history06_unknown_module_is_rejected_even_after_valid_duplicate(self):
        self.observe()
        for module in sorted(m.REQUIRED_MODULES - set(m._PARENT_DIAGNOSTIC_HISTORY_MODULES)) + ["UNKNOWN"]:
            with self.subTest(module=module), self.assertRaises(ValueError):
                self.observe(module=module)
        self.assertEqual(len(self.scope.observations), 1)

    def test_parent_diagnostic_history07_full_original_tuple_cannot_fork(self):
        for key, value in (("path", str(self.root / "unknown.json")),
                           ("bytes", 0), ("sha256", "0" * 64)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.observe(receipt=dict(m._PARENT_DIAGNOSTIC_HISTORY_LEAF, **{key: value}))
        self.assertFalse(self.scope.directory.exists())

    def test_parent_diagnostic_history08_same_fingerprint_clone_path_never_gains_permission(self):
        self.observe()
        clone = dict(m._PARENT_DIAGNOSTIC_HISTORY_LEAF, path=str(self.root / "clone.json"))
        with self.assertRaises(ValueError):
            self.observe(receipt=clone)
        with self.assertRaises(ValueError):
            m.reject_parent_diagnostic_history_declaration(clone)
        self.assertEqual(len(self.scope.observations), 1)

    def test_parent_diagnostic_history09_direct_plan_declarations_cannot_bypass_edge_scope(self):
        for category in ("source", "gate", "seed", "context", "logical_alias", "physical_alias",
                         "allocation_closure_gate", "root_terminal_rejection_gate",
                         "base_acceptance", "library_software_acceptance", "mapper_software_acceptance"):
            value = plan()
            module = value["modules"][0]
            leaf = dict(m._PARENT_DIAGNOSTIC_HISTORY_LEAF)
            if category == "source":
                module["sources"][0]["receipt"] = leaf
            elif category == "gate":
                module["gate"]["receipt"] = leaf
            elif category == "seed":
                module["seeds"] = [leaf]
            elif category == "context":
                value["context_parent_seeds"] = [leaf]
            elif category == "logical_alias":
                value["aliases"] = [{"logical": leaf, "physical": r(str(self.root / "copy.txt"))}]
            elif category == "physical_alias":
                value["aliases"] = [{"logical": r(str(self.root / "ordinary.json")), "physical": leaf}]
            elif category in ("allocation_closure_gate", "root_terminal_rejection_gate"):
                module[category] = {"receipt": leaf}
            else:
                value[category] = leaf
            with self.subTest(category=category), self.assertRaises(ValueError):
                m.module_plan(value)

    def test_parent_diagnostic_history10_unrelated_receipt_remains_on_ordinary_route(self):
        ordinary = r(str(self.root / "ordinary.json"), 2, "c" * 64)
        self.assertIsNone(self.scope.edge(ordinary, None, (), "scientific_report"))
        m.reject_parent_diagnostic_history_declaration(ordinary)
        self.assertFalse(self.scope.directory.exists())

    def test_parent_diagnostic_history11_zero_actual_or_foreign_base_cannot_be_accepted(self):
        with self.assertRaises(ValueError):
            self.scope.require_complete()
        scope = m.ParentDiagnosticHistoryOpaqueLeaf(self.out, r(str(self.root / "foreign.json")))
        self.assertFalse(scope.require_complete())
        with self.assertRaises(ValueError):
            scope.edge(m._PARENT_DIAGNOSTIC_HISTORY_LEAF, m._PARENT_DIAGNOSTIC_HISTORY_BASE["path"], m._PARENT_DIAGNOSTIC_HISTORY_FIELD,
                       "default_workflow_integration")
        self.assertFalse(scope.directory.exists())

    def test_parent_diagnostic_history12_schema_status_and_all_diagnostic_policy_flags_are_strict(self):
        for field in ("schema", "status") + m._PARENT_DIAGNOSTIC_HISTORY_FALSE_FLAGS + m._PARENT_DIAGNOSTIC_HISTORY_TRUE_FLAGS:
            document = copy.deepcopy(self.document)
            document[field] = "OTHER" if field in ("schema", "status") else not document[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.parent_diagnostic_history_document_shape(document)

    def test_parent_diagnostic_history13_utf8_duplicate_nonfinite_and_overflow_are_rejected(self):
        for raw in (b"\xff", b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":1e9999}'):
            self.replace_document(raw=raw)
            with self.subTest(raw=raw), self.assertRaises((ValueError, UnicodeDecodeError)):
                self.observe()
            self.assertFalse(self.scope.directory.exists())

    def test_parent_diagnostic_history14_exact_fifteen_three_seven_six_seven_keys_and_integer_types(self):
        kinds = ("extra_top", "missing_top", "counter_bool", "gpu_bool", "allocation", "allocation_gpu_bool",
                 "source", "sealed_source", "failure_keys", "attempt", "failure_flag", "context_keys",
                 "field", "candidates", "alias_hit", "previous_keys", "previous_receipt", "previous_physical",
                 "previous_field", "previous_basis", "previous_relative", "previous_role", "error", "traceback")
        for kind in kinds:
            document = copy.deepcopy(self.document)
            failure = document["failure_context"];context = failure["context"];previous = context["previous_verified_parent_edge"]
            if kind == "extra_top":document["unexpected"] = True
            elif kind == "missing_top":document.pop("allocation")
            elif kind == "counter_bool":document["exact_calls"] = True
            elif kind == "gpu_bool":document["GPU_allocated"] = False
            elif kind == "allocation":document["allocation"]["job_id"] = "OTHER"
            elif kind == "allocation_gpu_bool":document["allocation"]["allocated_gpus"] = False
            elif kind == "source":document["source"]["bytes"] += 1
            elif kind == "sealed_source":document["original_sealed_V4_source"]["sha256"] = "0" * 64
            elif kind == "failure_keys":failure["unexpected"] = True
            elif kind == "attempt":failure["attempted_receipt"]["bytes"] = True
            elif kind == "failure_flag":failure["external_original_not_read"] = False
            elif kind == "context_keys":context["unexpected"] = 1
            elif kind == "field":context["source_field"] = ["entries", "1", "design_manifest"]
            elif kind == "candidates":context["declared_same_size_candidates"] = ["UNVALIDATED"]
            elif kind == "alias_hit":context["exact_declared_alias_hit"] = True
            elif kind == "previous_keys":previous["unexpected"] = 1
            elif kind == "previous_receipt":previous["receipt"]["sha256"] = "0" * 64
            elif kind == "previous_physical":previous["physical"]["bytes"] = True
            elif kind == "previous_field":previous["field"] = ["other"]
            elif kind == "previous_basis":previous["resolution_basis"] = "AUTHORIZED"
            elif kind == "previous_relative":previous["relative_context"] = {}
            elif kind == "previous_role":previous["role"] = "CURRENT_RECEIPT"
            elif kind == "error":document["error"] = "{}"
            else:document["traceback"] = None
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                m.parent_diagnostic_history_document_shape(document)


    def test_parent_diagnostic_history15_duplicate_error_is_documentary_and_old_three_history_shapes_unchanged(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":1e9999}', '[]'):
            document = copy.deepcopy(self.document);document["error"] = raw
            with self.subTest(raw=raw), self.assertRaises(ValueError):m.parent_diagnostic_history_document_shape(document)
        for cls, method, validator in (
                (InventoryHistoryDataContracts, "test_history01_default_preserves_all_bytes_without_member_io", m.inventory_history_document_shape),
                (ArchiveParentHistoryDataContracts, "test_archive_parent_history01_default_preserves_all_bytes_without_member_io", m.archive_parent_history_document_shape),
                (RelativeDiagnosticHistoryDataContracts, "test_relative_diagnostic_history01_default_preserves_all_bytes_without_member_io", m.relative_diagnostic_history_document_shape)):
            case = cls(method);case.setUp()
            try:self.assertTrue(validator(case.document))
            finally:case.tearDown()


    def test_parent_diagnostic_history16_full_base_authority_and_independent_edges_are_mandatory(self):
        original = self.base_path.read_bytes()
        self.base_path.chmod(0o644)
        self.base_path.write_bytes(original + b" ")
        self.base_path.chmod(0o444)
        with self.assertRaises(ValueError):
            self.observe()
        for field in (m._PARENT_DIAGNOSTIC_HISTORY_FIELD[1], "original13279_failed_executing_source"):
            base = json.loads(original)
            base["original_failure_history"][field] = r(str(self.root / "wrong.json"))
            m._PARENT_DIAGNOSTIC_HISTORY_BASE = self.write(self.base_path, json.dumps(base).encode())
            self.scope = m.ParentDiagnosticHistoryOpaqueLeaf(self.out, m._PARENT_DIAGNOSTIC_HISTORY_BASE)
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.observe()

    def test_parent_diagnostic_history17_writable_original_or_parent_is_forbidden(self):
        for path in (self.base_path, self.leaf):
            path.chmod(0o644)
            try:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    self.observe()
            finally:
                path.chmod(0o444)

    def test_parent_diagnostic_history18_symlink_leaf_and_ancestor_are_not_alias_permissions(self):
        backup = self.root / "backup.json"
        self.write(backup, self.content)
        self.leaf.unlink()
        self.leaf.symlink_to(backup)
        with self.assertRaises(ValueError):
            self.observe()
        self.leaf.unlink()
        self.write(self.leaf, self.content)
        linked = self.root / "linked"
        linked.symlink_to(self.leaf.parent, target_is_directory=True)
        clone = dict(m._PARENT_DIAGNOSTIC_HISTORY_LEAF, path=str(linked / self.leaf.name))
        with self.assertRaises(ValueError):
            self.observe(receipt=clone)

    def test_parent_diagnostic_history19_parent_original_and_copy_hardlinks_are_rejected(self):
        for path in (self.base_path, self.leaf):
            link = self.root / "hardlink"
            m.os.link(path, link)
            try:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    self.observe()
            finally:
                link.unlink()
        edge = self.observe()
        link = self.root / "copy_hardlink"
        m.os.link(edge["physical"]["path"], link)
        try:
            with self.assertRaises(ValueError):
                self.scope.readback()
        finally:
            link.unlink()

    def test_parent_diagnostic_history20_input_metadata_drift_after_valid_output_is_detected(self):
        self.observe()
        before = m.stable_metadata(self.leaf)
        changed = before["mtime_ns"] + 2000000000
        m.os.utime(self.leaf, ns=(changed, changed))
        with self.assertRaises(ValueError):
            self.scope.readback()
        self.assertFalse((self.out / "acceptance.json").exists())

    def test_parent_diagnostic_history21_changed_original_bytes_are_not_reaccepted(self):
        self.observe()
        self.leaf.chmod(0o644)
        self.leaf.write_bytes(self.content + b" ")
        self.leaf.chmod(0o444)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_parent_diagnostic_history22_copy_writability_or_changed_content_is_fatal(self):
        edge = self.observe()
        path = Path(edge["physical"]["path"])
        path.chmod(0o644)
        with self.assertRaises(ValueError):
            self.scope.readback()
        path.write_bytes(b"CHANGED")
        path.chmod(0o444)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_parent_diagnostic_history23_directory0555_is_independent_of_synchronized_proof_metadata(self):
        proof, aliases, allocation = self.saved()
        self.scope.directory.chmod(0o755)
        proof["copy_directory_metadata"] = m.stable_metadata(self.scope.directory)
        with self.assertRaisesRegex(ValueError, "readonly0555"):
            m.parent_diagnostic_history_proof_shape(proof, aliases, allocation)
        with self.assertRaises(ValueError):
            m.verify_parent_diagnostic_history_preservation(proof, aliases, allocation)

    def test_parent_diagnostic_history24_exclusive_collision_and_exact_one_file_universe(self):
        self.scope.directory.mkdir()
        sentinel = self.scope.directory / "SENTINEL"
        sentinel.write_text("DO_NOT_OVERWRITE")
        with self.assertRaises(FileExistsError):
            self.observe()
        self.assertEqual(sentinel.read_text(), "DO_NOT_OVERWRITE")
        sentinel.unlink()
        self.scope.directory.rmdir()
        self.observe()
        self.scope.directory.chmod(0o755)
        (self.scope.directory / "extra.txt").write_text("EXTRA")
        self.scope.directory.chmod(0o555)
        with self.assertRaises(ValueError):
            self.scope.readback()

    def test_parent_diagnostic_history25_fsync_failure_never_accepts_or_changes_originals(self):
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        before = [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)]
        with patch.object(m.os, "fsync", side_effect=OSError("SYNTHETIC_FSYNC_FAILURE")):
            with self.assertRaises(OSError):
                self.observe()
        self.assertEqual(before, [m.stable_metadata(self.base_path), m.stable_metadata(self.leaf)])
        self.assertFalse(self.scope.observations)
        self.assertFalse((self.out / "acceptance.json").exists())

    def test_parent_diagnostic_history26_pure_full_proof_rejects_flags_metadata_counts_and_extra_keys(self):
        proof, aliases, allocation = self.saved()
        self.assertTrue(m.parent_diagnostic_history_proof_shape(proof, aliases, allocation))
        for field, value in (("schema", "OTHER"), ("authorized_observation_n", True),
                             ("embedded_receipt_occurrence_n", 6), ("documentary_targets_statted_or_opened", True),
                             ("archive_or_scientific_acceptance", True), ("unexpected", 1)):
            fork = copy.deepcopy(proof)
            fork[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.parent_diagnostic_history_proof_shape(fork, aliases, allocation)
        fork = copy.deepcopy(proof)
        fork["original_metadata_before"]["inode"] = True
        with self.assertRaises(ValueError):
            m.parent_diagnostic_history_proof_shape(fork, aliases, allocation)

    def test_parent_diagnostic_history27_alias_pointer_status_allocation_and_context_tampering_fail(self):
        proof, aliases, allocation = self.saved()
        for kind in ("alias_status", "alias_receipt", "pointer", "allocation", "module", "order", "ordinal"):
            fork, index = copy.deepcopy(proof), copy.deepcopy(aliases)
            if kind == "alias_status":
                index["aliases"][0]["status"] = "OTHER"
            elif kind == "alias_receipt":
                index["aliases"][0]["archived"]["sha256"] = "0" * 64
            elif kind == "pointer":
                fork["exact_alias_index"]["path"] = str(self.root / "other.json")
            elif kind == "allocation":
                fork["allocation"] = {"job_id": "OTHER"}
            elif kind == "module":
                fork["observations"][0]["module"] = "scientific_report"
            elif kind == "order":
                fork["observations"][0]["field"].reverse()
            else:
                fork["observations"][0]["ordinal"] = True
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                m.parent_diagnostic_history_proof_shape(fork, index, allocation)

    def test_parent_diagnostic_history28_pure_validator_has_no_filesystem_or_live_source_calls(self):
        proof, aliases, allocation = self.saved()
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        with patch.object(Path, "open", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "stat", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "lstat", side_effect=AssertionError("NO_FS")), \
             patch.object(Path, "resolve", side_effect=AssertionError("NO_FS")), \
             patch.object(m, "rec", side_effect=AssertionError("NO_LIVE_SHA")), \
             patch.object(m, "verify", side_effect=AssertionError("NO_LIVE_VERIFY")), \
             patch.object(m.os, "open", side_effect=AssertionError("NO_OS_OPEN")):
            self.assertTrue(m.parent_diagnostic_history_document_shape(self.document))
            self.assertTrue(m.parent_diagnostic_history_proof_shape(proof, aliases, allocation))

    def test_parent_diagnostic_history29_production_saved_verifier_checks_current_bytes_and_index(self):
        proof, aliases, allocation = self.saved()
        self.assertTrue(m.verify_parent_diagnostic_history_preservation(proof, aliases, allocation))
        pointer = Path(proof["exact_alias_index"]["path"])
        pointer.chmod(0o644)
        pointer.write_text(json.dumps({"schema": "CHANGED"}))
        pointer.chmod(0o444)
        with self.assertRaises(ValueError):
            m.verify_parent_diagnostic_history_preservation(proof, aliases, allocation)

    def test_parent_diagnostic_history30_genuine_audit_retains_both_Source2_original_fields_and_independent_V4_sibling(self):
        self.assertIsNotNone(self.run_genuine_audit())

    def test_parent_diagnostic_history31_genuine_queue_rejects_wrong_context_after_valid_seen_copy(self):
        self.run_genuine_audit(invalid_after_valid=True)

    def test_parent_diagnostic_history32_genuine_audit_cannot_use_plan_alias_as_direct_data_permission(self):
        self.run_genuine_audit(direct_alias=True)



class ParentDiagnosticHistoryInheritedRouteContracts(unittest.TestCase):
    """Reach nested actual audit guards with test-only row/edge isolation."""

    def run_route(self, route):
        import inspect
        fixture = ClosureFixtureContracts("test_real_closure_preserves_old_and_accepts_new_default")
        fixture.setUp()
        case = ParentDiagnosticHistoryDataContracts("test_parent_diagnostic_history01_default_preserves_all_bytes_without_member_io")
        saved_private = {name: copy.deepcopy(getattr(m, name)) for name in case.private_names}
        guard_calls = []
        mutation_calls = []
        original_guard = m.reject_parent_diagnostic_history_declaration
        original_route = m.inherited_source_route
        try:
            case.install(fixture.root / "inherited_history_case")
            base = m.read(fixture.p["base_acceptance"]["path"])
            if route == "closure_physical_alias":
                closure = dict(schema="benchmark-source-receipt-closure.v1", edges=[
                    dict(receipt=r(str(fixture.root / "ordinary_alias.py"), 1, "c" * 64),
                         parent=str(fixture.asset / "ordinary_parent.json"), field=["source"],
                         physical=m._PARENT_DIAGNOSTIC_HISTORY_LEAF, resolution_basis="EXACT_ORIGINAL",
                         role="EXACT_TEXT_RECEIPT_READBACK")])
                closure_receipt = fixture.meta("history_alias_closure.json", closure)
                inclusion = m.read(base["source_inclusion"]["path"])
                inclusion["source_receipt_closure"] = closure_receipt
                inclusion_receipt = fixture.meta("history_alias_inclusion.json", inclusion)
                base["source_closure"] = closure_receipt
                base["source_inclusion"] = inclusion_receipt
            case.replace_document(case.document, base_overlay=base)
            fixture.p["base_acceptance"] = m._PARENT_DIAGNOSTIC_HISTORY_BASE
            default = next(x for x in fixture.p["modules"] if x["role"] == "default_workflow_integration")
            if route == "resolve":
                default["seeds"] = [m._PARENT_DIAGNOSTIC_HISTORY_BASE]
                fixture.p["modules"] = [x for x in fixture.p["modules"] if x is not default] + [default]

            def guard_spy(receipt):
                caller = inspect.currentframe().f_back
                if receipt == m._PARENT_DIAGNOSTIC_HISTORY_LEAF:
                    guard_calls.append(dict(caller=caller.f_code.co_name,
                                            r=copy.deepcopy(caller.f_locals.get("r")),
                                            logical=copy.deepcopy(caller.f_locals.get("logical")),
                                            receipt=copy.deepcopy(receipt)))
                return original_guard(receipt)

            def route_wrapper(row, operations):
                result = original_route(row, operations)
                if row["repository_relative"] == "rebuild/unrelated.py":
                    if route == "add_source":
                        row["source"] = dict(m._PARENT_DIAGNOSTIC_HISTORY_LEAF)
                    elif route == "add_logical":
                        self.assertNotEqual(m.fp(row["source"]), m.fp(m._PARENT_DIAGNOSTIC_HISTORY_LEAF))
                        row["original_source"] = dict(m._PARENT_DIAGNOSTIC_HISTORY_LEAF)
                    mutation_calls.append(route)
                return result

            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            stack = __import__("contextlib").ExitStack()
            with stack:
                stack.enter_context(patch.object(m, "cpu", return_value={
                    "job_id": "50003", "allocated_CPUs": 1, "allocated_gpus": 0}))
                stack.enter_context(patch.object(m, "reject_parent_diagnostic_history_declaration",
                                                new=guard_spy))
                if route in ("add_source", "add_logical"):
                    stack.enter_context(patch.object(m, "inherited_source_route",
                                                    side_effect=route_wrapper))
                elif route == "resolve":
                    # Only a synthetic edge route is disabled to exercise later defense.
                    stack.enter_context(patch.object(m.ParentDiagnosticHistoryOpaqueLeaf, "edge",
                                                    return_value=None))
                with self.assertRaisesRegex(
                        ValueError, "Fixed13290 diagnostic DATA cannot be direct SOURCE/gate/seed/context/Plan alias"):
                    fixture.run_fixture()
            out = fixture.root / "audit_out"
            self.assertFalse((out / "acceptance.json").exists())
            self.assertFalse((out / "source_inclusion_final.json").exists())
            self.assertFalse((out / "opaque_parent_diagnostic_history_bytes").exists())
            self.assertFalse((out / "parent_diagnostic_history_opaque_leaf_proof.json").exists())
            incomplete = m.read(out / "typed_incomplete.json")
            expected_stage = "recursive_exact_new_dependencies" if route == "resolve" else "base_readback"
            self.assertEqual(incomplete["failed_stage"], expected_stage)
            self.assertEqual(incomplete["reason_type"], "ValueError")
            self.assertEqual(incomplete["reason"],
                             "Fixed13290 diagnostic DATA cannot be direct SOURCE/gate/seed/context/Plan alias")
            expected_caller = "add" if route.startswith("add_") else "alias" if route == "closure_physical_alias" else "resolve"
            hits = [x for x in guard_calls if x["caller"] == expected_caller]
            self.assertEqual(len(hits), 1)
            if route == "add_source":
                self.assertEqual(hits[0]["r"], m._PARENT_DIAGNOSTIC_HISTORY_LEAF)
                self.assertNotEqual(hits[0]["logical"], m._PARENT_DIAGNOSTIC_HISTORY_LEAF)
                self.assertEqual(mutation_calls, ["add_source"])
            elif route == "add_logical":
                self.assertEqual(hits[0]["logical"], m._PARENT_DIAGNOSTIC_HISTORY_LEAF)
                self.assertNotEqual(m.fp(hits[0]["r"]), m.fp(m._PARENT_DIAGNOSTIC_HISTORY_LEAF))
                self.assertEqual(mutation_calls, ["add_logical"])
            elif route == "resolve":
                self.assertEqual(hits[0]["r"], m._PARENT_DIAGNOSTIC_HISTORY_LEAF)
            else:
                self.assertEqual(hits[0]["receipt"], m._PARENT_DIAGNOSTIC_HISTORY_LEAF)
        finally:
            for name, value in saved_private.items():
                setattr(m, name, value)
            fixture.tearDown()

    def test_parent_diagnostic_history33_inherited_source_reaches_actual_add_r_direct_guard(self):
        self.run_route("add_source")

    def test_parent_diagnostic_history34_inherited_logical_reaches_actual_add_logical_guard(self):
        self.run_route("add_logical")

    def test_parent_diagnostic_history35_inherited_closure_physical_alias_reaches_actual_nested_alias_guard(self):
        self.run_route("closure_physical_alias")

    def test_parent_diagnostic_history36_queue_edge_isolation_reaches_actual_nested_resolve_guard(self):
        self.run_route("resolve")


class ParentDiagnosticHistoryOutputControlContracts(unittest.TestCase):
    def test_parent_diagnostic_history37_fixed_control_writer_is_exclusive_fsynced_and_failure_retains_data(self):
        case = ParentDiagnosticHistoryDataContracts("test_parent_diagnostic_history01_default_preserves_all_bytes_without_member_io")
        case.setUp()
        try:
            case.observe()
            alias = case.scope.alias_index()
            path = case.out / "parent_diagnostic_history_opaque_aliases.json"
            pointer, metadata = m._parent_diagnostic_history_write_control(path, alias)
            actual, after = m._parent_diagnostic_history_control_readback(pointer, metadata)
            self.assertEqual(actual, alias)
            self.assertEqual(after, metadata)
            self.assertEqual(metadata["mode"] & 0o777, 0o444)
            self.assertEqual(metadata["nlink"], 1)
            with self.assertRaises(FileExistsError):
                m._parent_diagnostic_history_write_control(path, alias)
            failure = case.out / "parent_diagnostic_history_opaque_leaf_proof.json"
            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            with patch.object(m.os, "fsync", side_effect=OSError("SYNTHETIC_CONTROL_FSYNC")):
                with self.assertRaisesRegex(OSError, "SYNTHETIC_CONTROL_FSYNC"):
                    m._parent_diagnostic_history_write_control(failure, {"fixture": True})
            self.assertEqual(Path(case.scope.copy_receipt["path"]).read_bytes(), case.content)
            self.assertFalse((case.out / "acceptance.json").exists())
        finally:
            case.tearDown()

    def test_parent_diagnostic_history38_both_controls_reject_mode_hardlink_native_drift_and_post_json_mutation(self):
        case = ParentDiagnosticHistoryDataContracts("test_parent_diagnostic_history01_default_preserves_all_bytes_without_member_io")
        case.setUp()
        try:
            proof, alias, allocation = case.saved()
            proof_pointer, proof_metadata = m._parent_diagnostic_history_write_control(
                case.out / "parent_diagnostic_history_opaque_leaf_proof.json", proof)
            for pointer in (proof_pointer, proof["exact_alias_index"]):
                path = Path(pointer["path"])
                expected = m._parent_diagnostic_history_control_metadata(path)
                path.chmod(0o400)
                with self.subTest(control=path.name, boundary="exact444"), self.assertRaises(ValueError):
                    m._parent_diagnostic_history_control_readback(pointer)
                path.chmod(0o444)
                link = case.root / (path.name + ".hardlink")
                m.os.link(path, link)
                try:
                    with self.subTest(control=path.name, boundary="singlelink"), self.assertRaises(ValueError):
                        m._parent_diagnostic_history_control_readback(pointer)
                finally:
                    link.unlink()
                expected = m._parent_diagnostic_history_control_metadata(path)
                raw = path.read_bytes()
                original_json = m._strict_parent_diagnostic_history_json
                hits = []
                def mutate_after_json(text):
                    value = original_json(text)
                    if text.encode("utf-8") == raw:
                        current = m.stable_metadata(path)
                        changed = current["mtime_ns"] + 2000000000
                        m.os.utime(path, ns=(changed, changed))
                        hits.append(path.name)
                    return value
                patch = __import__("unittest.mock", fromlist=["patch"]).patch
                with patch.object(m, "_strict_parent_diagnostic_history_json", side_effect=mutate_after_json):
                    with self.subTest(control=path.name, boundary="post_last_JSON"), self.assertRaisesRegex(
                            ValueError, "Fixed13290 control changed during own JSON readback"):
                        m._parent_diagnostic_history_control_readback(pointer, expected)
                self.assertEqual(hits, [path.name])
                with self.subTest(control=path.name, boundary="stored_metadata"), self.assertRaises(ValueError):
                    m._parent_diagnostic_history_control_readback(pointer, expected)
            self.assertEqual(Path(case.scope.copy_receipt["path"]).read_bytes(), case.content)
            self.assertFalse((case.out / "acceptance.json").exists())
        finally:
            case.tearDown()


class ParentDiagnosticHistoryFinalReadonlyLifecycleContracts(unittest.TestCase):
    """Exercise the unchanged genuine audit through its final readonly loop."""

    def run_final_readonly_fixture(self, writable_output):
        import inspect
        case = ParentDiagnosticHistoryDataContracts(
            "test_parent_diagnostic_history01_default_preserves_all_bytes_without_member_io")
        case.setUp()
        original_audit = m.audit
        original_writer = m._parent_diagnostic_history_write_control
        original_dump = m.dump
        original_chmod = Path.chmod
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        controls = {}
        repeated_chmods = []
        writable_chmods = []
        writable = {}
        completed = []
        control_names = {"parent_diagnostic_history_opaque_leaf_proof.json",
                         "parent_diagnostic_history_opaque_aliases.json"}

        def remember_writer(path, obj):
            result = original_writer(path, obj)
            path = Path(path)
            self.assertIn(path.name, control_names)
            self.assertNotIn(path, controls)
            controls[path] = (copy.deepcopy(result[0]), copy.deepcopy(result[1]))
            return result

        def observe_chmod(path, mode, *args, **kwargs):
            path = Path(path)
            if path in controls and mode == 0o444 and path.lstat().st_mode & 0o7777 == 0o444:
                # The old final loop would reach this real same-mode chmod.
                # Make its own-fixture metadata effect deterministic, without
                # replacing any metadata reader or production drift guard.
                repeated_chmods.append(str(path))
                result = original_chmod(path, mode, *args, **kwargs)
                native = path.lstat()
                m.os.utime(path, ns=(native.st_atime_ns,
                                    native.st_mtime_ns + 2000000000))
                return result
            if path == writable.get("path"):
                caller = inspect.currentframe().f_back.f_code.co_name
                before = m.stable_metadata(path)
                result = original_chmod(path, mode, *args, **kwargs)
                writable_chmods.append(dict(caller=caller, requested_mode=mode,
                                            before=before, after=m.stable_metadata(path)))
                return result
            return original_chmod(path, mode, *args, **kwargs)

        def publish_with_writable_output(path, obj):
            receipt = original_dump(path, obj)
            path = Path(path)
            if writable_output and path.name == "acceptance.json" and path.parent.name == "audit_out":
                self.assertFalse(writable)
                target = path.parent / "synthetic_final_readonly_writable.json"
                content = b'{"fixture_only": true, "no_child_receipts": true}\n'
                flags = m.os.O_WRONLY | m.os.O_CREAT | m.os.O_EXCL | getattr(m.os, "O_NOFOLLOW", 0)
                fd = m.os.open(target, flags, 0o600)
                with m.os.fdopen(fd, "wb") as stream:
                    stream.write(content)
                    stream.flush()
                    m.os.fsync(stream.fileno())
                writable.update(path=target, content=content,
                                metadata=m.stable_metadata(target))
                self.assertEqual(writable["metadata"]["mode"] & 0o7777, 0o600)
            return receipt

        def audit_and_check_final_readback(*args, **kwargs):
            result = original_audit(*args, **kwargs)
            self.assertEqual({path.name for path in controls}, control_names)
            self.assertEqual(len(controls), 2)
            for path, (receipt, metadata) in controls.items():
                self.assertEqual(m.rec(path), receipt)
                self.assertEqual(m.stable_metadata(path), metadata)
                self.assertEqual(metadata["mode"] & 0o7777, 0o444)
                self.assertEqual(metadata["nlink"], 1)
            self.assertEqual(repeated_chmods, [])
            if writable_output:
                self.assertIn("path", writable)
                self.assertEqual(len(writable_chmods), 1)
                event = writable_chmods[0]
                self.assertEqual(event["caller"], "audit")
                self.assertEqual(event["requested_mode"], 0o444)
                self.assertEqual(event["before"], writable["metadata"])
                self.assertEqual(event["before"]["mode"] & 0o7777, 0o600)
                self.assertEqual(event["after"]["mode"] & 0o7777, 0o444)
                self.assertEqual(event["after"]["nlink"], 1)
                self.assertEqual(writable["path"].read_bytes(), writable["content"])
                self.assertEqual(m.stable_metadata(writable["path"]), event["after"])
            else:
                self.assertEqual(writable, {})
                self.assertEqual(writable_chmods, [])
            completed.append(True)
            return result

        try:
            with patch.object(m, "_parent_diagnostic_history_write_control", side_effect=remember_writer), \
                 patch.object(m, "dump", side_effect=publish_with_writable_output), \
                 patch.object(Path, "chmod", new=observe_chmod), \
                 patch.object(m, "audit", side_effect=audit_and_check_final_readback):
                self.assertIsNotNone(case.run_genuine_audit())
            self.assertEqual(completed, [True])
            self.assertIs(m.audit, original_audit)
            self.assertIs(m.dump, original_dump)
            self.assertIs(m._parent_diagnostic_history_write_control, original_writer)
            self.assertIs(Path.chmod, original_chmod)
        finally:
            case.tearDown()

    def test_parent_diagnostic_history39_genuine_audit_final_seal_preserves_exact444_control_metadata(self):
        self.run_final_readonly_fixture(writable_output=False)

    def test_parent_diagnostic_history40_genuine_audit_final_seal_converts_writable_owned_JSON(self):
        self.run_final_readonly_fixture(writable_output=True)


class ParentDiagnosticHistoryOrdinarySourceCoverageContracts(unittest.TestCase):
    def test_parent_diagnostic_history41_actual_source_bytes_tamper_reaches_ordinary_resolve_verification(self):
        import inspect
        for child_field in ("source", "original_sealed_V4_source"):
            case = ParentDiagnosticHistoryDataContracts("test_parent_diagnostic_history01_default_preserves_all_bytes_without_member_io")
            case.setUp()
            original_edge = m.ParentDiagnosticHistoryOpaqueLeaf.edge
            original_verify = m.verify
            original_run = ClosureFixtureContracts.run_fixture
            changed = [];calls = [];failures = []
            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            def edge_then_tamper(scope, receipt, parent, trail, module):
                result = original_edge(scope, receipt, parent, trail, module)
                if result is not None and not changed:
                    target = m._PARENT_DIAGNOSTIC_HISTORY_PRODUCER if child_field == "source" else m._PARENT_DIAGNOSTIC_HISTORY_V4_SOURCE
                    path = Path(target["path"]);path.chmod(0o644);path.write_bytes(b"SYNTHETIC_CHANGED_SOURCE_BYTES\n");path.chmod(0o444)
                    changed.append(copy.deepcopy(target))
                return result
            def verify_spy(receipt, readonly=False):
                if changed and receipt == changed[0]:
                    calls.append((inspect.currentframe().f_back.f_code.co_name, copy.deepcopy(receipt)))
                return original_verify(receipt, readonly)
            def record_failure_before_cleanup(fixture):
                try:return original_run(fixture)
                except ValueError:
                    out = fixture.root / "audit_out"
                    self.assertFalse((out / "acceptance.json").exists())
                    self.assertFalse((out / "source_inclusion_final.json").exists())
                    self.assertTrue((out / "opaque_parent_diagnostic_history_bytes").is_dir())
                    incomplete = m.read(out / "typed_incomplete.json")
                    self.assertEqual(incomplete["failed_stage"], "recursive_exact_new_dependencies")
                    self.assertEqual(incomplete["reason_type"], "ValueError")
                    self.assertEqual(incomplete["reason"], "Required exact bytes changed: " + changed[0]["path"])
                    failures.append(copy.deepcopy(incomplete))
                    raise
            try:
                with patch.object(m.ParentDiagnosticHistoryOpaqueLeaf, "edge", new=edge_then_tamper), \
                     patch.object(m, "verify", new=verify_spy), \
                     patch.object(ClosureFixtureContracts, "run_fixture", new=record_failure_before_cleanup):
                    with self.subTest(child=child_field), self.assertRaisesRegex(ValueError, "Required exact bytes changed"):
                        case.run_genuine_audit()
                self.assertEqual(len(changed), 1)
                self.assertEqual(len(failures), 1)
                self.assertTrue(any(caller == "resolve" and receipt == changed[0] for caller, receipt in calls))
            finally:case.tearDown()

    def test_parent_diagnostic_history42_actual_C_I_coverage_is_pure_and_rejects_child_loss_or_reclassification(self):
        case = ParentDiagnosticHistoryDataContracts("test_parent_diagnostic_history01_default_preserves_all_bytes_without_member_io")
        case.setUp()
        try:self.assertIsNotNone(case.run_genuine_audit(coverage_tamper=True))
        finally:case.tearDown()


class ParentDiagnosticHistoryRepeatedSourceAndGraphContracts(unittest.TestCase):
    """Genuine seen/copy/role routing and cross-control last-read drift boundaries."""

    def run_repeated_source_fixture(self, dual=False, incompatible=None):
        import inspect
        case = ParentDiagnosticHistoryDataContracts("test_parent_diagnostic_history01_default_preserves_all_bytes_without_member_io")
        case.setUp()
        fixture = ClosureFixtureContracts("test_real_closure_preserves_old_and_accepts_new_default")
        fixture.setUp()
        original_edge = m.ParentDiagnosticHistoryOpaqueLeaf.edge
        original_eligible = m.eligible_public
        eligible_calls = [];authorized = [];snapshots = {};injected = []
        try:
            case.install(fixture.root / "repeated_source_history_case")
            case.replace_document(case.document, base_overlay=m.read(fixture.p["base_acceptance"]["path"]))
            fixture.p["base_acceptance"] = m._PARENT_DIAGNOSTIC_HISTORY_BASE
            children = m.parent_diagnostic_history_source_children()
            destinations = {child["receipt"]["path"]: "rebuild/fixed_source2/" + Path(child["receipt"]["path"]).name for child in children}
            finaltools = next(x for x in fixture.p["modules"] if x["role"] == "final_delivery_tools")
            finaltools["sources"] += [dict(receipt=child["receipt"], repository_relative=destinations[child["receipt"]["path"]]) for child in children]
            if incompatible == "ambiguity":
                finaltools["sources"].append(dict(receipt=children[0]["receipt"], repository_relative="rebuild/fixed_source2/duplicate_producer.py"))
            default = next(x for x in fixture.p["modules"] if x["role"] == "default_workflow_integration")
            # The TWO ordinary seeds are popped BEFORE BaseA, so the later exact
            # authorized Source children really are already in the global seen set.
            default["seeds"] = [m._PARENT_DIAGNOSTIC_HISTORY_BASE] + [child["receipt"] for child in children]
            fixture.p["modules"] = [x for x in fixture.p["modules"] if x is not default] + [default]

            def edge_spy(scope, receipt, parent, trail, module):
                caller = inspect.currentframe().f_back
                result = original_edge(scope, receipt, parent, trail, module)
                if result is not None:
                    self.assertEqual(caller.f_code.co_name, "audit")
                    rows = caller.f_locals["rows"]
                    seen = caller.f_locals["seen"]
                    self.assertTrue(all(m.key(child["receipt"]) in seen for child in children))
                    if not authorized:
                        for child in children:
                            selected = rows[destinations[child["receipt"]["path"]]]
                            self.assertEqual(selected["roles"], ["final_delivery_tools"])
                            snapshots[child["receipt"]["path"]] = copy.deepcopy(selected)
                        if incompatible not in (None, "ambiguity"):
                            selected = rows[destinations[children[0]["receipt"]["path"]]]
                            if incompatible == "identity":
                                selected["original_source"] = dict(selected["original_source"], path=str(fixture.root / "same_fp_unknown_identity.py"))
                                selected["logical_receipts"] = []
                            elif incompatible == "kind":selected["kind"] = "DOCUMENT"
                            elif incompatible == "roles":selected["roles"] = ["UNDECLARED_SOURCE_ROLE"]
                            elif incompatible == "destination":selected["repository_relative"] = "../unsafe_source2.py"
                        if dual:
                            # Fixture-only queue instrumentation creates a second
                            # exact allowed context that normal BaseA seen may omit.
                            # The real Scope.edge and every guard remain unchanged.
                            caller.f_locals["queue"].append((dict(m._PARENT_DIAGNOSTIC_HISTORY_LEAF), m._PARENT_DIAGNOSTIC_HISTORY_BASE["path"], m._PARENT_DIAGNOSTIC_HISTORY_FIELD, "final_delivery_tools"))
                            injected.append("final_delivery_tools")
                    authorized.append(module)
                return result

            def eligible_spy(receipt, destination):
                caller = inspect.currentframe().f_back
                if authorized and any(receipt == child["receipt"] for child in children):
                    eligible_calls.append(dict(caller=caller.f_code.co_name, receipt=copy.deepcopy(receipt), destination=destination,
                                               roles=copy.deepcopy(caller.f_locals.get("roles")), logical=copy.deepcopy(caller.f_locals.get("logical"))))
                return original_eligible(receipt, destination)

            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            with patch.object(m, "cpu", return_value={"job_id": "50004", "allocated_CPUs": 1, "allocated_gpus": 0}), \
                 patch.object(m.ParentDiagnosticHistoryOpaqueLeaf, "edge", new=edge_spy), \
                 patch.object(m, "eligible_public", new=eligible_spy):
                if incompatible:
                    expected = "Fixed Source2 existing fingerprint has ambiguous public destinations" if incompatible == "ambiguity" else "Unsafe repository destination" if incompatible == "destination" else "Fixed Source2 existing public identity/kind/roles are incompatible"
                    with self.assertRaisesRegex(ValueError, expected):fixture.run_fixture()
                    out = fixture.root / "audit_out"
                    self.assertFalse((out / "acceptance.json").exists())
                    self.assertFalse((out / "source_inclusion_final.json").exists())
                    self.assertTrue((out / "opaque_parent_diagnostic_history_bytes").is_dir())
                    incomplete = m.read(out / "typed_incomplete.json")
                    self.assertEqual(incomplete["failed_stage"], "recursive_exact_new_dependencies")
                    self.assertEqual(incomplete["reason_type"], "ValueError")
                    self.assertIn(expected, incomplete["reason"])
                    self.assertEqual(authorized, ["default_workflow_integration"])
                    return
                inclusion = fixture.run_fixture()
            out = fixture.root / "audit_out"
            closure = m.read(out / "source_receipt_closure_final.json")
            proof = m.read(inclusion["parent_diagnostic_history_opaque_leaf_proof"]["path"])
            self.assertTrue(m.parent_diagnostic_history_source_coverage(proof, closure, inclusion))
            expected_modules = ["default_workflow_integration", "final_delivery_tools"] if dual else ["default_workflow_integration"]
            self.assertEqual(authorized, expected_modules)
            self.assertEqual(injected, ["final_delivery_tools"] if dual else [])
            self.assertEqual([x["module"] for x in proof["observations"]], expected_modules)
            for child in children:
                receipt = child["receipt"]
                row = next(x for x in inclusion["files"] if x["repository_relative"] == destinations[receipt["path"]])
                before = snapshots[receipt["path"]]
                for field in ("source", "original_source", "repository_relative", "kind", "cluster_specific"):
                    self.assertEqual(row[field], before[field])
                self.assertEqual(set(row["roles"]), {"default_workflow_integration", "final_delivery_tools", "RECURSIVE_OPERATIVE_SOURCE"})
                actual_add = [x for x in eligible_calls if x["caller"] == "add" and x["receipt"] == receipt]
                self.assertEqual(len(actual_add), len(expected_modules))
                self.assertEqual([x["roles"] for x in actual_add], [[module, "RECURSIVE_OPERATIVE_SOURCE"] for module in expected_modules])
                self.assertTrue(all(x["destination"] == before["repository_relative"] and x["logical"] == receipt for x in actual_add))
                child_edges = [x for x in closure["edges"] if x.get("parent") == m._PARENT_DIAGNOSTIC_HISTORY_LEAF["path"] and x.get("receipt") == receipt]
                self.assertEqual([x["module"] for x in child_edges], expected_modules)
        finally:
            fixture.tearDown()
            case.tearDown()

    def test_parent_diagnostic_history43_genuine_preseen_and_dualmodule_use_original_add_and_preserve_identity(self):
        for dual in (False, True):
            with self.subTest(dual=dual):self.run_repeated_source_fixture(dual=dual)

    def test_parent_diagnostic_history44_genuine_preseen_rejects_ambiguous_or_incompatible_existing_Source_rows(self):
        for incompatible in ("ambiguity", "identity", "kind", "roles", "destination"):
            with self.subTest(incompatible=incompatible):self.run_repeated_source_fixture(incompatible=incompatible)

    def test_parent_diagnostic_history45_genuine_later_graph_or_final_control_read_detects_earlier_C_native_drift(self):
        import inspect
        for trigger in ("source_inclusion_final.json", "acceptance.json", "final_proof_read"):
            case = ParentDiagnosticHistoryDataContracts("test_parent_diagnostic_history01_default_preserves_all_bytes_without_member_io")
            case.setUp()
            original_read = m.read
            original_coverage = m.parent_diagnostic_history_source_coverage
            original_control_readback = m._parent_diagnostic_history_control_readback
            original_run = ClosureFixtureContracts.run_fixture
            armed = [];changed = [];failures = []
            def mutate_earlier_C(path):
                cpath = Path(path).parent / "source_receipt_closure_final.json"
                before = m.stable_metadata(cpath)
                native = cpath.lstat()
                m.os.utime(cpath, ns=(native.st_atime_ns, native.st_mtime_ns + 2000000000))
                self.assertNotEqual(m.stable_metadata(cpath), before)
                changed.append(str(cpath))
            def read_then_mutate(path):
                caller = inspect.currentframe().f_back
                result = original_read(path)
                if caller.f_code.co_name == "parent_diagnostic_history_output_readback" and Path(path).name == trigger and not changed:
                    self.assertIn("source_receipt_closure_final.json", caller.f_locals["parent_diagnostic_graph_controls"])
                    mutate_earlier_C(path)
                return result
            def coverage_then_arm(saved, closure, inclusion):
                result = original_coverage(saved, closure, inclusion)
                caller = inspect.currentframe().f_back
                if trigger == "final_proof_read" and caller.f_code.co_name == "parent_diagnostic_history_output_readback" and len(caller.f_locals["parent_diagnostic_graph_controls"]) >= 2:
                    armed.append(True)
                return result
            def final_control_then_mutate(receipt, expected_metadata=None):
                result = original_control_readback(receipt, expected_metadata)
                if trigger == "final_proof_read" and armed and not changed:
                    mutate_earlier_C(receipt["path"])
                return result
            def failure_before_cleanup(fixture):
                try:return original_run(fixture)
                except ValueError:
                    out = fixture.root / "audit_out"
                    incomplete = m.read(out / "typed_incomplete.json")
                    expected = "Actual13290 graph control changed after final proof/index readback" if trigger == "final_proof_read" else "Actual13290 graph control changed after all final JSON and coverage reads"
                    self.assertEqual(incomplete["reason"], expected)
                    self.assertEqual(incomplete["reason_type"], "ValueError")
                    self.assertEqual(incomplete["failed_stage"], "inclusion")
                    self.assertTrue((out / "opaque_parent_diagnostic_history_bytes").is_dir())
                    failures.append(copy.deepcopy(incomplete))
                    raise
            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            try:
                with patch.object(m, "read", new=read_then_mutate), \
                     patch.object(m, "parent_diagnostic_history_source_coverage", new=coverage_then_arm), \
                     patch.object(m, "_parent_diagnostic_history_control_readback", new=final_control_then_mutate), \
                     patch.object(ClosureFixtureContracts, "run_fixture", new=failure_before_cleanup):
                    with self.assertRaisesRegex(ValueError, "Actual13290 graph control changed after"):
                        case.run_genuine_audit()
                self.assertEqual(len(changed), 1)
                self.assertEqual(len(failures), 1)
            finally:case.tearDown()


class ParentDiagnosticHistoryAdapterCAContracts(unittest.TestCase):
    """Execute the actual adapter late lifecycle with genuine new DATA/Source2 outputs."""

    def test_parent_diagnostic_history46_actual_adapter_CA_enrollment_rejects_later_proof_native_drift(self):
        import contextlib, importlib.util, inspect, io, types
        mapping_final_drift = getattr(self, "_mapping_final_drift", False)
        mapping_graph_drift = getattr(self, "_mapping_final_graph_drift", None)
        for tamper in (False, True):
            case = ParentDiagnosticHistoryDataContracts("test_parent_diagnostic_history01_default_preserves_all_bytes_without_member_io")
            case.setUp()
            original_audit = m.audit
            original_read = m.read
            original_control_readback = m._parent_diagnostic_history_control_readback
            original_core = m.conditional_core_runtime
            original_rec = m.rec
            completed = [];initial_CA = [];changed = [];captured = []
            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            def audit_then_actual_adapter(plan_path, out):
                # Produce the new DATA proof, normal Source2 C/I and immutable TXT
                # through the REAL main audit before exercising the adapter.
                result = original_audit(plan_path, out)
                out = Path(out)
                accepted = original_read(out / "acceptance.json")
                actual_C = original_read(accepted["source_closure"]["path"])
                actual_I = original_read(accepted["source_inclusion"]["path"])
                # Unchanged older-family/mapper/software prerequisite protocols
                # are synthetic in this focused adapter fixture. Their own full
                # suites remain separate; no new DATA/live guard is patched.
                families = [
                    ("vendor_example", "vendor_example_opaque_leaf_proof", "vendor_example_opaque_aliases"),
                    ("finite_worker", "finite_worker_control_proof", "finite_worker_control_aliases"),
                    ("inventory_history", "inventory_history_opaque_leaf_proof", "inventory_history_opaque_aliases"),
                    ("archive_parent_history", "archive_parent_history_opaque_leaf_proof", "archive_parent_history_opaque_aliases"),
                    ("relative_diagnostic_history", "relative_diagnostic_history_opaque_leaf_proof", "relative_diagnostic_history_opaque_aliases")]
                mapping_baseline = [m.stable_metadata(m._PARENT_DIAGNOSTIC_HISTORY_BASE["path"])] + [m.stable_metadata(entry["receipt"]["path"]) for entry in m._FIXED_HISTORY_MAPPING_PARENTS]
                genuine_parent_saved = original_read(accepted["parent_diagnostic_history_opaque_leaf_proof"]["path"])
                for prefix, proof_key, alias_key in families:
                    index = dict(schema="exact-resource-aliases.v2", aliases=[{"fixture_only": True}])
                    alias_receipt = m.dump(out / (alias_key + ".json"), index)
                    proof_obj = dict(schema="exact-vendor-example-opaque-data-leaf.v1" if prefix == "vendor_example" else "SYNTHETIC_OLD_FAMILY_PROTOCOL_ONLY",
                                     exact_alias_index=alias_receipt)
                    if prefix in ("inventory_history", "archive_parent_history", "relative_diagnostic_history"):
                        proof_obj["authority_metadata_before"] = copy.deepcopy(mapping_baseline)
                        for name in ("original_metadata_before", "preserved_metadata", "copy_directory_metadata"):
                            proof_obj[name] = copy.deepcopy(genuine_parent_saved[name])
                    proof_receipt = m.dump(out / (proof_key + ".json"), proof_obj)
                    for obj in (accepted, actual_C, actual_I):
                        obj[proof_key] = proof_receipt;obj[alias_key] = alias_receipt
                # Generic dump is intentionally exclusive. Replace ONLY these
                # already-read OWN synthetic TMP fixture outputs for the unrelated
                # old-family protocol overlay, never any production/input file.
                # Genuine new DATA/copy/proof and Source2 edges/rows stay unchanged.
                for name in ("source_receipt_closure_final.json", "source_inclusion_final.json", "acceptance.json"):
                    target = out / name
                    self.assertTrue(target.is_relative_to(m.R))
                    self.assertEqual(target.parent, out)
                    self.assertTrue(target.is_file())
                    self.assertFalse(target.is_symlink())
                    target.unlink()
                closed = m.dump(out / "source_receipt_closure_final.json", actual_C)
                actual_I["source_receipt_closure"] = closed
                inclusion = m.dump(out / "source_inclusion_final.json", actual_I)
                accepted["source_closure"] = closed;accepted["source_inclusion"] = inclusion
                m.dump(out / "acceptance.json", accepted)
                assets = out / "adapter_fixture_inputs";assets.mkdir()
                qualified_sources, unused = m.owned_source_bundle(Path(m.__file__).parent)
                runtime = m.conditional_core_runtime()
                log = case.write(assets / "software_fixture.log", b"SYNTHETIC_PREREQUISITE_PROTOCOL_ONLY\n")
                contracts = m.dump(assets / "contracts.json", dict(log=log, fixture_only=True))
                snapshot = m.dump(assets / "snapshot.json", {"fixture_only": True})
                software = m.dump(assets / "software.json", dict(contracts=contracts, source_snapshot=snapshot,
                                      conditional_core_runtime=runtime, allocation={"job_id": "50002"}))
                mapper_names = ["finite_source_context.py", "test_finite_source_context.py", "exact_relative_bbf_context.py", "test_exact_relative_bbf_context.py", "context_mapper_audit_cpu.py", "context_mapper_cpu.sbatch", "context_consumer.py", "HANDOFF.md", "historical_annotation_context.py", "test_historical_annotation_context.py", "recovered_five_context.py", "test_recovered_five_context.py", "archive_member_context.py", "test_archive_member_context.py"]
                mapper_pins = [case.write(assets / "mapper" / name, b"SYNTHETIC_MAPPER_PROTOCOL_ONLY\n") for name in mapper_names]
                mapper_acceptance = m.dump(assets / "mapper.json", dict(source_files=mapper_pins))
                parent_receipts = [m.dump(assets / ("parent%d.json" % index), {"fixture_only": index}) for index in range(17)]
                fixture_plan = dict(library_software_acceptance=software, mapper_software_acceptance=mapper_acceptance,
                                    base_acceptance=m._PARENT_DIAGNOSTIC_HISTORY_BASE,
                                    relative_receipt_context_mapping={"fixture_only": True}, external_historical_receipt_context_mapping={"fixture_only": True},
                                    current_recovered_relative_receipt_context_mapping={"fixture_only": True}, archive_member_receipt_context_mapping={"fixture_only": True},
                                    context_parent_seeds=parent_receipts)
                plan_receipt = m.dump(assets / "plan.json", fixture_plan)
                request = m.dump(assets / "request.json", dict(schema="final-source-materialized-context-read-view-request.v3", root_owned=True,
                              raw_JSON_rewrite_allowed=False, generic_relative_resolution_allowed=False, generic_external_resolution_allowed=False,
                              library_software_acceptance=software, mapper_software_acceptance=mapper_acceptance, final_source_plan=plan_receipt,
                              bbf_parent_aliases=[], historical_parent_aliases=[], recovered_parent_aliases=[], archive_parent_aliases=[], finite_source_parent_aliases=[]))
                adapter_path = Path(m.__file__).with_name("final_source_context_adapter.py")
                spec = importlib.util.spec_from_file_location("synthetic_fix9_actual_adapter", adapter_path)
                adapter = importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
                adapter.base = m
                class FixtureReader:
                    def __init__(self, *args):self.original = args[4]
                    def __call__(self, path):return self.original(path)
                    def require_both_used(self):return True
                    def proof(self):return {"SYNTHETIC_MAPPER_PROTOCOL_ONLY": True}
                protocols = {
                    "final_source_closure": m,
                    "exact_relative_bbf_context": types.SimpleNamespace(PARENT=parent_receipts[0]),
                    "historical_annotation_context": types.SimpleNamespace(PARENT=parent_receipts[1]),
                    "recovered_five_context": types.SimpleNamespace(PARENT=parent_receipts[2]),
                    "archive_member_context": types.SimpleNamespace(ARCHIVES=[{"parent_manifest": parent_receipts[3]}, {"parent_manifest": parent_receipts[4]}]),
                    "finite_source_context": types.SimpleNamespace(verify_source_alias_scope=lambda *args: ({"fixture_only": True}, None), required_parent_receipts=lambda qualification: parent_receipts[5:]),
                    "context_consumer": types.SimpleNamespace(source_bundle=lambda *args: ({"fixture_only": True}, {"fixture_only": True}), VerifiedContextReader=FixtureReader)}
                def read_with_CA_observation(path):
                    caller = inspect.currentframe().f_back
                    obj = original_read(path)
                    if Path(path).name == "context_adapter_acceptance.json" and caller.f_code.co_name == "run":
                        initial_CA.append(m.stable_metadata(path))
                    return obj
                def proof_then_actual_CA_drift(receipt, expected_metadata=None):
                    obj = original_control_readback(receipt, expected_metadata)
                    caller = inspect.currentframe().f_back
                    if tamper and not mapping_final_drift and not mapping_graph_drift and initial_CA and not changed and caller.f_code.co_name == "parent_diagnostic_controls_readback" and "context_adapter_acceptance" in caller.f_locals.get("graph_objects", {}):
                        ca_receipt = caller.f_locals["parent_diagnostic_graph_receipts"]["context_adapter_acceptance"]
                        ca_path = Path(ca_receipt["path"])
                        before = m.stable_metadata(ca_path)
                        native = ca_path.lstat()
                        m.os.utime(ca_path, ns=(native.st_atime_ns, native.st_mtime_ns + 2000000000))
                        self.assertNotEqual(m.stable_metadata(ca_path), before)
                        changed.append(str(ca_path))
                    return obj
                def core_then_actual_mapping_drift():
                    value = original_core()
                    caller = inspect.currentframe().f_back
                    if mapping_final_drift and tamper and initial_CA and not changed and caller.f_code.co_name == "run" and "parent_ca_metadata" in caller.f_locals:
                        self.assertEqual(caller.f_locals["parent_ca_metadata"], initial_CA[0])
                        target = Path(m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]["path"])
                        before = m.stable_metadata(target);native = target.stat()
                        m.os.utime(target, ns=(native.st_atime_ns, native.st_mtime_ns + 2000000000))
                        self.assertNotEqual(m.stable_metadata(target), before)
                        changed.append(str(target))
                    return value
                def final_graph_rec_then_mapping_or_C_drift(path):
                    value = original_rec(path)
                    caller = inspect.currentframe().f_back
                    if mapping_graph_drift and tamper and initial_CA and not changed and caller.f_code.co_name == "run" and caller.f_locals.get("name") == "context_adapter_acceptance" and "parent_ca_metadata" in caller.f_locals and Path(path).name == "context_adapter_acceptance.json":
                        target = Path(m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]["path"]) if mapping_graph_drift == "Map" else Path(accepted["source_closure"]["path"])
                        state = target.stat()
                        m.os.utime(target, ns=(state.st_atime_ns, state.st_mtime_ns + 2000000000))
                        changed.append(str(target))
                    return value
                stdout = io.StringIO();old_sys_path = list(m.sys.path)
                try:
                    with contextlib.ExitStack() as stack:
                        stack.enter_context(contextlib.redirect_stdout(stdout))
                        stack.enter_context(patch.object(adapter, "module", side_effect=lambda name, path: protocols[name]))
                        stack.enter_context(patch.object(m, "audit", return_value=None))
                        stack.enter_context(patch.object(m, "software_shape", return_value=qualified_sources))
                        stack.enter_context(patch.object(m, "software_snapshot_shape", return_value=True))
                        stack.enter_context(patch.object(m, "terminal_cpu", return_value={"fixture_only": True}))
                        for name in ("verify_vendor_example_preservation", "verify_finite_worker_preservation", "verify_inventory_history_preservation", "verify_archive_parent_history_preservation", "verify_relative_diagnostic_history_preservation"):
                            stack.enter_context(patch.object(m, name, return_value=True))
                        # ONLY this owned synthetic unrelated-family overlay:
                        # same genuine BaseA+three Map native tables, no fence bypass.
                        for name in ("_HISTORY_BASE", "_ARCHIVE_PARENT_HISTORY_BASE", "_RELATIVE_DIAGNOSTIC_HISTORY_BASE"):
                            stack.enter_context(patch.object(m, name, new=copy.deepcopy(m._PARENT_DIAGNOSTIC_HISTORY_BASE)))
                        stack.enter_context(patch.object(m, "conditional_core_runtime", new=core_then_actual_mapping_drift))
                        stack.enter_context(patch.object(m, "rec", new=final_graph_rec_then_mapping_or_C_drift))
                        stack.enter_context(patch.object(m, "read", new=read_with_CA_observation))
                        stack.enter_context(patch.object(m, "_parent_diagnostic_history_control_readback", new=proof_then_actual_CA_drift))
                        if tamper:
                            with self.assertRaisesRegex(ValueError, "Fixed history final native union drifted" if mapping_graph_drift else "Fixed inherited history authority changed after final control read" if mapping_final_drift else "Actual adapter13290 graph control changed after final proof/index readback"):
                                adapter.run(request["path"], out)
                        else:adapter.run(request["path"], out)
                finally:m.sys.path[:] = old_sys_path
                captured.append(stdout.getvalue())
                self.assertEqual(len(initial_CA), 1)
                ca_path = out / "context_adapter_acceptance.json"
                ca = original_read(ca_path)
                self.assertEqual(ca["parent_diagnostic_history_opaque_leaf_proof"], accepted["parent_diagnostic_history_opaque_leaf_proof"])
                self.assertEqual(ca["parent_diagnostic_history_opaque_aliases"], accepted["parent_diagnostic_history_opaque_aliases"])
                if tamper:
                    if mapping_graph_drift:
                        self.assertEqual(changed, [m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]["path"]] if mapping_graph_drift == "Map" else [accepted["source_closure"]["path"]])
                        self.assertEqual(m.stable_metadata(ca_path), initial_CA[0])
                    elif mapping_final_drift:
                        self.assertEqual(changed, [m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]["path"]])
                        self.assertEqual(m.stable_metadata(ca_path), initial_CA[0])
                    else:
                        self.assertEqual(changed, [str(ca_path)])
                        self.assertNotEqual(m.stable_metadata(ca_path), initial_CA[0])
                    incomplete = original_read(out.with_name(out.name + "_context_adapter") / "typed_incomplete.json")
                    self.assertEqual(incomplete["reason"], "Fixed history final native union drifted" if mapping_graph_drift else "Fixed inherited history authority changed after final control read" if mapping_final_drift else "Actual adapter13290 graph control changed after final proof/index readback")
                    self.assertEqual(incomplete["reason_type"], "ValueError")
                    self.assertEqual(incomplete["failed_stage"], "actual_frozen_library_audit_with_module_local_context_reader")
                    self.assertFalse(any('"acceptance"' in line for line in stdout.getvalue().splitlines()))
                else:
                    self.assertEqual(changed, [])
                    self.assertEqual(m.stable_metadata(ca_path), initial_CA[0])
                    descriptor = json.loads(stdout.getvalue().splitlines()[-1])
                    self.assertEqual(descriptor["acceptance"], m.rec(ca_path))
                    self.assertEqual(descriptor["status"], ca["status"])
                completed.append(tamper)
                return result
            try:
                with patch.object(m, "audit", side_effect=audit_then_actual_adapter):
                    self.assertIsNotNone(case.run_genuine_audit())
                self.assertEqual(completed, [tamper])
                self.assertEqual(len(captured), 1)
            finally:case.tearDown()


class InheritedMappingHistoryContextContracts(unittest.TestCase):
    """Twenty fixed rows, real Map traversal, and unchanged ordinary Source2 routes."""
    families = (
        ("inventory13299", "_HISTORY", InventoryHistoryDataContracts, "InventoryHistoryOpaqueLeaf", "inventory_history"),
        ("archive13298", "_ARCHIVE_PARENT_HISTORY", ArchiveParentHistoryDataContracts, "ArchiveParentHistoryOpaqueLeaf", "archive_parent_history"),
        ("relative13295", "_RELATIVE_DIAGNOSTIC_HISTORY", RelativeDiagnosticHistoryDataContracts, "RelativeDiagnosticHistoryOpaqueLeaf", "relative_diagnostic_history"),
        ("parent13290", "_PARENT_DIAGNOSTIC_HISTORY", ParentDiagnosticHistoryDataContracts, "ParentDiagnosticHistoryOpaqueLeaf", "parent_diagnostic_history"))

    def with_case(self, family, callback):
        config = next(x for x in self.families if x[0] == family)
        case = config[2](next(name for name in config[2].__dict__ if name.startswith("test_")))
        case.setUp()
        try:return callback(case, config)
        finally:case.tearDown()

    def save_current(self, case, config):
        family, prefix, cls, scope_name, stem = config
        index = case.scope.alias_index()
        target = case.out / (stem.replace("inventory_history", "inventory_history") + "_opaque_aliases.json")
        if family == "inventory13299":
            pointer = m.dump(target, index)
        else:
            pointer, unused = getattr(m, "_" + stem + "_write_control")(target, index)
        allocation = dict(job_id="50007", allocated_CPUs=1, allocated_gpus=0)
        proof = dict(case.scope.proof(), exact_alias_index=pointer, allocation=allocation)
        return proof, index, allocation

    def allowed_matrix(self, family):
        def check(case, config):
            definition = m._fixed_history_definition(family)
            rows = m._fixed_history_contexts(family)
            self.assertEqual(len(rows), 5)
            for module in definition["modules"]:
                for row in rows:
                    edge = case.scope.edge(definition["leaf"], row["parent_manifest"]["path"], tuple(row["field"]), module)
                    self.assertEqual(edge["parent"], row["parent_manifest"]["path"])
                    self.assertEqual(edge["field"], row["field"])
            proof, index, allocation = self.save_current(case, config)
            self.assertEqual(proof["authorized_observation_n"], 10)
            self.assertEqual(proof["authority_receipts"], [definition["base"]] + [e["receipt"] for e in m._FIXED_HISTORY_MAPPING_PARENTS])
            self.assertEqual(proof["authority_metadata_before"], proof["authority_metadata_after"])
            self.assertEqual(proof["authorized_parent_field_rows"], rows)
            self.assertEqual([x["parent_manifest"] for x in proof["observations"]], [r["parent_manifest"] for r in rows] * 2)
            self.assertTrue(getattr(m, config[4] + "_proof_shape")(proof, index, allocation))
            self.assertEqual(Path(proof["preserved_opaque_data"]["path"]).read_bytes(), case.content)
            self.assertEqual(len(list(case.scope.directory.iterdir())), 1)
        self.with_case(family, check)

    def rebind_map(self, case, config, slot, raw):
        entries = copy.deepcopy(m._FIXED_HISTORY_MAPPING_PARENTS)
        path = Path(entries[slot]["receipt"]["path"])
        entries[slot]["receipt"] = case.write(path, raw)
        m._FIXED_HISTORY_MAPPING_PARENTS = tuple(entries)
        base = m.read(case.base_path)
        base[entries[slot]["base_field"]] = dict(entries[slot]["receipt"])
        setattr(m, config[1] + "_BASE", case.write(case.base_path, json.dumps(base).encode("utf-8")))
        case.scope = getattr(m, config[3])(case.out, getattr(m, config[1] + "_BASE"))

    def for_families(self, callback):
        for config in self.families:
            with self.subTest(family=config[0]):self.with_case(config[0], callback)

    def test_mapping01_inventory_five_rows_two_modules_and_v2_ordered_projection(self):
        self.allowed_matrix("inventory13299")

    def test_mapping02_archive_five_rows_two_modules_and_v2_ordered_projection(self):
        self.allowed_matrix("archive13298")

    def test_mapping03_relative_five_rows_two_modules_and_v2_ordered_projection(self):
        self.allowed_matrix("relative13295")

    def test_mapping04_parent_five_rows_two_modules_and_v2_ordered_projection(self):
        self.allowed_matrix("parent13290")

    def test_mapping05_parent_field_crossproduct_is_rejected_before_and_after_valid_copy(self):
        def check(case, config):
            family = config[0];definition = m._fixed_history_definition(family)
            lineage = m._fixed_history_contexts(family)[-1]
            wrong = next(x for x in m._fixed_history_contexts(family) if x["parent_manifest"] != lineage["parent_manifest"])
            for after in (False, True):
                if after:case.observe()
                with self.assertRaisesRegex(ValueError, "exact parent/field"):
                    case.scope.edge(definition["leaf"], wrong["parent_manifest"]["path"], tuple(lineage["field"]), "default_workflow_integration")
                self.assertEqual(len(case.scope.observations), int(after))
        self.for_families(check)

    def test_mapping06_same_parent_bytes_at_unknown_path_do_not_create_authority(self):
        def check(case, config):
            entry = m._FIXED_HISTORY_MAPPING_PARENTS[0]
            clone = case.write(case.root / "parent_clone.json", Path(entry["receipt"]["path"]).read_bytes())
            self.assertEqual(m.fp(clone), m.fp(entry["receipt"]))
            with self.assertRaisesRegex(ValueError, "exact parent/field"):
                case.observe(parent=clone["path"])
            self.assertFalse(case.scope.directory.exists())
        self.for_families(check)

    def test_mapping07_full_leaf_tuple_and_unknown_module_fail_even_after_valid_observation(self):
        def check(case, config):
            case.observe()
            definition = m._fixed_history_definition(config[0])
            row = m._fixed_history_contexts(config[0])[1]
            for receipt, module in ((dict(definition["leaf"], bytes=definition["leaf"]["bytes"] + 1), "default_workflow_integration"),
                                    (dict(definition["leaf"], path=str(case.root / "known_fp_clone.json")), "default_workflow_integration"),
                                    (definition["leaf"], "formal_common_review")):
                with self.assertRaises(ValueError):
                    case.scope.edge(receipt, row["parent_manifest"]["path"], tuple(row["field"]), module)
            self.assertEqual(len(case.scope.observations), 1)
        self.for_families(check)

    def test_mapping08_relative_BBF_control_remains_outside_the_closed_four_parents(self):
        def check(case, config):
            row = m._fixed_history_contexts(config[0])[-1]
            unrelated = case.write(case.root / "relative_mapping.json", b'{"schema":"exact-context-relative-receipts.v1"}')
            for field in (m._fixed_history_definition(config[0])["field"], tuple(row["field"])):
                with self.assertRaisesRegex(ValueError, "exact parent/field"):
                    case.observe(parent=unrelated["path"], trail=field)
            self.assertFalse(case.scope.directory.exists())
        self.for_families(check)

    def test_mapping09_any_mapping_ownbyte_drift_is_rejected_with_original_copy_retained(self):
        def check(case, config):
            case.observe()
            path = Path(m._FIXED_HISTORY_MAPPING_PARENTS[2]["receipt"]["path"])
            original = path.read_bytes()
            changed = original.replace(b'": ', b'" :', 1)
            self.assertNotEqual(changed, original)
            self.assertEqual(len(changed), len(original))
            self.assertEqual(json.loads(changed.decode("utf-8")), json.loads(original.decode("utf-8")))
            path.chmod(0o644);path.write_bytes(changed);path.chmod(0o444)
            native = m.stable_metadata(path)
            self.assertTrue(m.stat.S_ISREG(native["mode"]))
            self.assertEqual(m.stat.S_IMODE(native["mode"]), 0o444)
            self.assertEqual(native["nlink"], 1)
            self.assertEqual(native["bytes"], len(original))
            self.assertEqual(m.safe_path(path), path)
            with self.assertRaises(ValueError) as raised:case.scope.readback()
            self.assertEqual(str(raised.exception), "Fixed inherited mapping own bytes changed")
            self.assertEqual(Path(case.scope.copy_receipt["path"]).read_bytes(), case.content)
            self.assertFalse((case.out / "acceptance.json").exists())
        self.for_families(check)

    def test_mapping10_each_native_mapping_snapshot_is_rechecked_including_ctime(self):
        for slot in range(3):
            def check(case, config):
                case.observe();path = Path(m._FIXED_HISTORY_MAPPING_PARENTS[slot]["receipt"]["path"])
                before = m.stable_metadata(path)
                m.os.utime(path, ns=(path.stat().st_atime_ns, before["mtime_ns"] + 2000000000))
                with self.assertRaisesRegex(ValueError, "four-authority native metadata drifted"):case.scope.readback()
                self.assertNotEqual(m.stable_metadata(path), before)
            self.with_case("parent13290", check)

    def test_mapping11_fixed_mapping_symlink_and_hardlink_are_not_readonly_authorities(self):
        for kind in ("symlink", "hardlink"):
            def check(case, config):
                path = Path(m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]["path"])
                backup = path.with_name("backing_mapping.json")
                if kind == "symlink":path.rename(backup);path.symlink_to(backup)
                else:m.os.link(path, backup)
                with self.assertRaises(ValueError):case.observe()
                self.assertFalse(case.scope.directory.exists())
            self.with_case("inventory13299", check)

    def test_mapping12_BaseA_descriptor_must_bind_the_entire_mapping_receipt(self):
        def check(case, config):
            base = m.read(case.base_path)
            name = m._FIXED_HISTORY_MAPPING_PARENTS[1]["base_field"]
            base[name] = dict(base[name], sha256="f" * 64)
            setattr(m, config[1] + "_BASE", case.write(case.base_path, json.dumps(base).encode()))
            case.scope = getattr(m, config[3])(case.out, getattr(m, config[1] + "_BASE"))
            with self.assertRaisesRegex(ValueError, "BaseA mapping descriptor changed"):case.observe()
        self.for_families(check)

    def test_mapping13_mapping_history_must_equal_the_whole_BaseA_history_object(self):
        def check(case, config):
            obj = m.read(m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]["path"])
            obj["original_failure_history"]["unreviewed_history_claim"] = True
            self.rebind_map(case, config, 0, json.dumps(obj).encode())
            with self.assertRaisesRegex(ValueError, "schema/history/producer provenance changed"):case.observe()
        self.for_families(check)

    def test_mapping14_mapping_producer_and_selector_fulltuple_forks_fail_closed(self):
        for name in ("producer_executed_source", "producer_actual_software_gate", "source_graph_selector"):
            def check(case, config):
                obj = m.read(m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]["path"])
                obj[name] = dict(obj[name], bytes=obj[name]["bytes"] + 1)
                self.rebind_map(case, config, 0, json.dumps(obj).encode())
                with self.assertRaisesRegex(ValueError, "schema/history/producer provenance changed"):case.observe()
            self.with_case("archive13298", check)

    def test_mapping15_leaf_specific_lineage_index_cannot_be_swapped_or_forked(self):
        def check(case, config):
            slot, index = m._FIXED_HISTORY_LINEAGE_SLOTS[config[0]]
            obj = m.read(m._FIXED_HISTORY_MAPPING_PARENTS[slot]["receipt"]["path"])
            obj["accepted_lineage_receipts"][index] = dict(m._fixed_history_definition(config[0])["leaf"], sha256="f" * 64)
            self.rebind_map(case, config, slot, json.dumps(obj).encode())
            with self.assertRaisesRegex(ValueError, "lineage slot changed"):case.observe()
        self.for_families(check)

    def test_mapping16_strict_mapping_own_JSON_rejects_duplicate_nonfinite_and_invalid_UTF8(self):
        for raw in (b'{"schema":1,"schema":2}', b'{"x":NaN}', b'{"x":1e999}', b"\xff"):
            def check(case, config):
                self.rebind_map(case, config, 0, raw)
                with self.assertRaises((ValueError, UnicodeDecodeError)):case.observe()
                self.assertFalse(case.scope.directory.exists())
            self.with_case("relative13295", check)

    def test_mapping17_later_mapping_read_mutating_earlier_mapping_is_caught_after_last_JSON(self):
        def check(case, config):
            paths = [Path(x["receipt"]["path"]) for x in m._FIXED_HISTORY_MAPPING_PARENTS]
            original = Path.read_bytes;changed = []
            def read_bytes(path):
                raw = original(path)
                if Path(path) == paths[2] and not changed:
                    state = paths[0].stat()
                    m.os.utime(paths[0], ns=(state.st_atime_ns, state.st_mtime_ns + 2000000000));changed.append(True)
                return raw
            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            with patch.object(Path, "read_bytes", new=read_bytes):
                with self.assertRaisesRegex(ValueError, "authority changed after the last mapping JSON read"):case.observe()
            self.assertEqual(changed, [True]);self.assertFalse(case.scope.directory.exists())
        self.for_families(check)

    def test_mapping18_pure_v2_rejects_authority_table_order_and_fullreceipt_changes(self):
        def check(case, config):
            case.observe();proof, index, allocation = self.save_current(case, config)
            for operation in ("order", "tuple", "extra"):
                bad = copy.deepcopy(proof)
                if operation == "order":bad["authority_receipts"][1:3] = reversed(bad["authority_receipts"][1:3])
                elif operation == "tuple":bad["authority_receipts"][1]["bytes"] += 1
                else:bad["authority_receipts"].append(copy.deepcopy(bad["authority_receipts"][0]))
                with self.assertRaises(ValueError):getattr(m, config[4] + "_proof_shape")(bad, index, allocation)
        self.for_families(check)

    def test_mapping19_pure_v2_rejects_native_receipt_desync_and_changed_after_table(self):
        def check(case, config):
            case.observe();proof, index, allocation = self.save_current(case, config)
            for operation in ("path", "after", "bool", "mode"):
                bad = copy.deepcopy(proof)
                if operation == "path":bad["authority_metadata_before"][1]["path"] = bad["authority_receipts"][2]["path"]
                elif operation == "after":bad["authority_metadata_after"][1]["ctime_ns"] += 1
                elif operation == "bool":bad["authority_metadata_before"][1]["inode"] = True
                else:bad["authority_metadata_before"][1]["mode"] = m.stat.S_IFREG | 0o644
                with self.assertRaises(ValueError):getattr(m, config[4] + "_proof_shape")(bad, index, allocation)
        self.for_families(check)

    def test_mapping20_pure_v2_rejects_selected_parent_field_crossslot_and_noncontiguous_order(self):
        def check(case, config):
            lineage = m._fixed_history_contexts(config[0])[-1]
            case.observe(parent=lineage["parent_manifest"]["path"], trail=tuple(lineage["field"]))
            proof, index, allocation = self.save_current(case, config)
            for operation in ("parent", "field", "ordinal", "context_table"):
                bad = copy.deepcopy(proof)
                if operation == "parent":bad["observations"][0]["parent_manifest"] = bad["authority_receipts"][0]
                elif operation == "field":bad["observations"][0]["field"] = ["accepted_lineage_receipts", "99"]
                elif operation == "ordinal":bad["observations"][0]["ordinal"] = 1
                else:bad["authorized_parent_field_rows"].reverse()
                with self.assertRaises(ValueError):getattr(m, config[4] + "_proof_shape")(bad, index, allocation)
        self.for_families(check)

    def test_mapping21_pure_v2_rejects_alias_swap_oldschema_and_false_default_count(self):
        def check(case, config):
            case.observe();proof, index, allocation = self.save_current(case, config)
            for operation in ("index", "schema", "default"):
                bad = copy.deepcopy(proof);aliases = copy.deepcopy(index)
                if operation == "index":aliases["aliases"][0]["original"]["sha256"] = "f" * 64
                elif operation == "schema":bad["schema"] = bad["schema"].rsplit(".", 1)[0] + ".v1"
                else:bad["actual_default_observation_n"] = 0
                with self.assertRaises(ValueError):getattr(m, config[4] + "_proof_shape")(bad, aliases, allocation)
        self.for_families(check)

    def test_mapping22_all_four_pure_INDEX_shapes_have_no_live_filesystem_fallback(self):
        def check(case, config):
            case.observe();proof, index, allocation = self.save_current(case, config)
            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            with patch.object(Path, "open", side_effect=AssertionError("NO_LIVE_FS")), \
                 patch.object(Path, "stat", side_effect=AssertionError("NO_LIVE_STAT")), \
                 patch.object(m, "rec", side_effect=AssertionError("NO_LIVE_REC")), \
                 patch.object(m, "verify", side_effect=AssertionError("NO_LIVE_VERIFY")):
                self.assertTrue(getattr(m, config[4] + "_proof_shape")(proof, index, allocation))
        self.for_families(check)

    def test_mapping23_three_arg_live_verifiers_restore_and_guard_all_four_authorities(self):
        def check(case, config):
            row = m._fixed_history_contexts(config[0])[-1]
            case.observe(parent=row["parent_manifest"]["path"], trail=tuple(row["field"]))
            proof, index, allocation = self.save_current(case, config)
            verify = getattr(m, "verify_" + config[4] + "_preservation")
            self.assertTrue(verify(proof, index, allocation))
            path = Path(m._FIXED_HISTORY_MAPPING_PARENTS[1]["receipt"]["path"]);state = path.stat()
            m.os.utime(path, ns=(state.st_atime_ns, state.st_mtime_ns + 2000000000))
            with self.assertRaisesRegex(ValueError, "four-authority native metadata drifted"):verify(proof, index, allocation)
        self.for_families(check)

    def run_matrix_audit(self, dual=False, wrong=False, drift=None):
        """Real schemas + ordinary declarations/seeds; never patch queue or seen."""
        import inspect
        fixture = ClosureFixtureContracts("test_real_closure_preserves_old_and_accepts_new_default")
        fixture.setUp()
        names = tuple(dict.fromkeys(name for config in self.families for name in config[2].private_names))
        saved = {name: copy.deepcopy(getattr(m, name)) for name in names}
        original_read = m.read;original_eligible = m.eligible_public
        added = [];changed = []
        try:
            cases = []
            for config in self.families:
                case = config[2](next(name for name in config[2].__dict__ if name.startswith("test_")))
                case.root = fixture.root
                case.install(fixture.root / config[0])
                cases.append(case)
            # The two 13297 documents share the same immutable producer/gate identities.
            m._ARCHIVE_PARENT_HISTORY_PRODUCER = dict(m._HISTORY_PRODUCER)
            m._ARCHIVE_PARENT_HISTORY_SOFTWARE = dict(m._HISTORY_SOFTWARE)
            cases[1].document["source_producer"] = dict(m._HISTORY_PRODUCER)
            cases[1].document["original_software_only_acceptance"] = dict(m._HISTORY_SOFTWARE)
            cases[1].replace_document(cases[1].document)
            history = {}
            for case in cases:
                for name, value in original_read(case.base_path)["original_failure_history"].items():
                    if name in history:self.assertEqual(history[name], value)
                    history[name] = copy.deepcopy(value)
            base = dict(original_read(fixture.p["base_acceptance"]["path"]),
                        schema="source-delivery-refresh.v3",
                        original_failure_history=history)
            base = install_fixed_mapping_fixture(cases[-1], base, "parent13290", operative=True)
            accepted = cases[-1].write(fixture.asset / "matrix_base.json", json.dumps(base).encode())
            for config in self.families:setattr(m, config[1] + "_BASE", dict(accepted))
            fixture.p["base_acceptance"] = dict(accepted)
            children = m.parent_diagnostic_history_source_children()
            destinations = {child["receipt"]["path"]: "rebuild/matrix_source2/" + Path(child["receipt"]["path"]).name for child in children}
            finaltools = next(x for x in fixture.p["modules"] if x["role"] == "final_delivery_tools")
            finaltools["sources"] += [dict(receipt=x["receipt"], repository_relative=destinations[x["receipt"]["path"]]) for x in children]
            default = next(x for x in fixture.p["modules"] if x["role"] == "default_workflow_integration")
            default["seeds"] = ([m._FIXED_HISTORY_MAPPING_PARENTS[2]["receipt"]] if dual else [accepted]) + [x["receipt"] for x in children]
            if dual:finaltools["seeds"] = [accepted]
            fixture.p["modules"] = [x for x in fixture.p["modules"] if x is not default] + [default]
            if wrong:
                bad = fixture.meta("wrong_mapping_history.json", {"unqualified": m._HISTORY_LEAF})
                next(x for x in fixture.p["modules"] if x["role"] == "formal_common_review")["seeds"] = [bad]

            def eligible(receipt, destination):
                caller = inspect.currentframe().f_back
                if caller.f_code.co_name == "add" and caller.f_back.f_locals.get("parent_diagnostic_source_child"):
                    added.append(dict(receipt=copy.deepcopy(receipt), destination=destination,
                                      roles=copy.deepcopy(caller.f_locals["roles"]), logical=copy.deepcopy(caller.f_locals["logical"])))
                return original_eligible(receipt, destination)

            def read(path):
                obj = original_read(path)
                out = fixture.root / "audit_out"
                if drift and Path(path) == out / "source_inclusion_final.json" and not changed and inspect.currentframe().f_back.f_code.co_name == "parent_diagnostic_history_output_readback":
                    target = Path(m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]["path"]) if drift == "mapping" else out / "source_receipt_closure_final.json"
                    state = target.stat()
                    m.os.utime(target, ns=(state.st_atime_ns, state.st_mtime_ns + 2000000000))
                    changed.append(str(target))
                return obj

            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            with patch.object(m, "cpu", return_value=dict(job_id="50008", allocated_CPUs=1, allocated_gpus=0)), \
                 patch.object(m, "eligible_public", new=eligible), patch.object(m, "read", new=read):
                if wrong or drift:
                    message = "exact parent/field" if wrong else "^Fixed inherited history authority changed after final control read$" if drift == "mapping" else "Actual13290 graph control changed after all final JSON and coverage reads"
                    with self.assertRaisesRegex(ValueError, message):fixture.run_fixture()
                    out = fixture.root / "audit_out"
                    incomplete = original_read(out / "typed_incomplete.json")
                    self.assertEqual(incomplete["failed_stage"], "recursive_exact_new_dependencies" if wrong else "inclusion")
                    self.assertFalse((out / "acceptance.json").exists())
                    self.assertTrue((out / "opaque_inventory_history_bytes").is_dir())
                    if drift:self.assertEqual(len(changed), 1)
                    if drift == "mapping":
                        mapping_receipt = m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]
                        self.assertEqual(changed, [mapping_receipt["path"]])
                        self.assertEqual(m.rec(mapping_receipt["path"]), mapping_receipt)
                        retained_closure = original_read(out / "source_receipt_closure_final.json")
                        for case, config in zip(cases, self.families):
                            retained = original_read(retained_closure[config[4] + "_opaque_leaf_proof"]["path"])
                            copy_receipt = retained["preserved_opaque_data"]
                            self.assertEqual(Path(copy_receipt["path"]).read_bytes(), case.content)
                            self.assertEqual(m.rec(copy_receipt["path"]), copy_receipt)
                    return
                inclusion = fixture.run_fixture()
            out = fixture.root / "audit_out"
            closure = original_read(out / "source_receipt_closure_final.json")
            for family, prefix, cls, scope_name, stem in self.families:
                proof = original_read(inclusion[stem + "_opaque_leaf_proof"]["path"])
                self.assertEqual(proof["authorized_observation_n"], 5)
                observed = {(x["parent_manifest"]["path"], tuple(x["field"])) for x in proof["observations"]}
                expected = {(x["parent_manifest"]["path"], tuple(x["field"])) for x in m._fixed_history_contexts(family)}
                self.assertEqual(observed, expected)
                self.assertEqual(proof["actual_default_observation_n"], 2 if dual and family in ("inventory13299", "archive13298") else 1 if dual else 5)
                self.assertEqual(proof["actual_finaltools_observation_n"], 5 - proof["actual_default_observation_n"])
                self.assertEqual(proof["authority_receipts"], [accepted] + [x["receipt"] for x in m._FIXED_HISTORY_MAPPING_PARENTS])
                self.assertFalse(any(m.fp(row["source"]) == m.fp(getattr(m, prefix + "_LEAF")) for row in inclusion["files"]))
            proof = original_read(inclusion["parent_diagnostic_history_opaque_leaf_proof"]["path"])
            self.assertTrue(m.parent_diagnostic_history_source_coverage(proof, closure, inclusion))
            edges = [x for x in closure["edges"] if x.get("parent") == m._PARENT_DIAGNOSTIC_HISTORY_LEAF["path"]]
            self.assertEqual(len(edges), 10)
            for child in children:
                row = next(x for x in inclusion["files"] if x["repository_relative"] == destinations[child["receipt"]["path"]])
                self.assertEqual(m.fp(row["source"]), m.fp(child["receipt"]))
                physical = m.safe_path(row["source"]["path"])
                self.assertEqual(physical.parent, out / "readonly_source_bytes")
                self.assertFalse(physical.is_symlink())
                native = m.stable_metadata(physical)
                self.assertTrue(m.stat.S_ISREG(native["mode"]))
                self.assertEqual(m.stat.S_IMODE(native["mode"]), 0o444)
                self.assertEqual(native["nlink"], 1)
                self.assertEqual(m.rec(physical), row["source"])
                self.assertEqual(row["original_source"], child["receipt"])
                self.assertIn(child["receipt"], row["logical_receipts"])
                self.assertEqual(row["kind"], "IMPLEMENTATION")
                self.assertEqual(set(row["roles"]), {"default_workflow_integration", "final_delivery_tools", "RECURSIVE_OPERATIVE_SOURCE"})
                calls = [x for x in added if x["receipt"] == child["receipt"]]
                self.assertEqual(len(calls), 5)
                self.assertTrue(all(x["destination"] == destinations[child["receipt"]["path"]] and x["logical"] == child["receipt"] for x in calls))
                self.assertEqual([x["roles"] for x in calls], [[observation["module"], "RECURSIVE_OPERATIVE_SOURCE"] for observation in proof["observations"]])
            self.assertEqual(original_read(accepted["path"])["original_failure_history"], history)
            self.assertEqual(original_read(accepted["path"])["original_failure_history"]["original13279_failed_executing_source"], m._PARENT_DIAGNOSTIC_HISTORY_V4_SOURCE)
        finally:
            for name, value in saved.items():setattr(m, name, value)
            fixture.tearDown()

    def test_mapping24_genuine_all_four_histories_five_default_contexts_and_ten_Source2_edges(self):
        self.run_matrix_audit()

    def test_mapping25_genuine_natural_dualmodule_Map_seeds_preserve_preseen_Source2_identity_and_add(self):
        self.run_matrix_audit(dual=True)

    def test_mapping26_genuine_wrong_parent_after_valid_Map_copy_is_rejected_before_seen(self):
        self.run_matrix_audit(wrong=True)

    def test_mapping27_genuine_later_graph_JSON_mapping_native_drift_rejects_final_readback(self):
        self.run_matrix_audit(drift="mapping")

    def test_mapping28_genuine_later_graph_JSON_mutating_earlier_graph_control_is_rejected(self):
        self.run_matrix_audit(drift="graph")


    def test_mapping29_last_live_alias_JSON_mutation_of_earlier_Map_hits_final_authority_fence(self):
        import inspect
        for family in ("archive13298", "relative13295", "parent13290"):
            def check(case, config):
                case.observe();proof, index, allocation = self.save_current(case, config)
                name = "_" + config[4] + "_control_readback";original = getattr(m, name)
                verifier_name = "verify_" + config[4] + "_preservation"
                changed = []
                def last_index(receipt, expected_metadata=None):
                    obj = original(receipt, expected_metadata)
                    caller = inspect.currentframe().f_back
                    if receipt == proof["exact_alias_index"] and expected_metadata is not None and caller.f_code.co_name == verifier_name and not changed:
                        path = Path(m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]["path"])
                        state = path.stat()
                        m.os.utime(path, ns=(state.st_atime_ns, state.st_mtime_ns + 2000000000))
                        changed.append(caller.f_code.co_name)
                    return obj
                patch = __import__("unittest.mock", fromlist=["patch"]).patch
                with patch.object(m, name, new=last_index):
                    with self.assertRaisesRegex(ValueError, "authority changed after final control read"):
                        getattr(m, verifier_name)(proof, index, allocation)
                self.assertEqual(changed, [verifier_name])
                self.assertFalse((case.out / "acceptance.json").exists())
                self.assertEqual(Path(case.scope.copy_receipt["path"]).read_bytes(), case.content)
            with self.subTest(family=family):self.with_case(family, check)

    def test_mapping30_inventory_last_scope_proof_JSON_readback_is_followed_by_original_baseline_fence(self):
        import inspect
        def check(case, config):
            case.observe();proof, index, allocation = self.save_current(case, config)
            original = m.InventoryHistoryOpaqueLeaf.proof;changed = []
            def proof_then_drift(scope):
                obj = original(scope)
                caller = inspect.currentframe().f_back
                if caller.f_code.co_name == "verify_inventory_history_preservation" and not changed:
                    path = Path(m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]["path"])
                    state = path.stat()
                    m.os.utime(path, ns=(state.st_atime_ns, state.st_mtime_ns + 2000000000))
                    changed.append(caller.f_code.co_name)
                return obj
            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            with patch.object(m.InventoryHistoryOpaqueLeaf, "proof", new=proof_then_drift):
                with self.assertRaisesRegex(ValueError, "authority changed after final control read"):
                    m.verify_inventory_history_preservation(proof, index, allocation)
            self.assertEqual(changed, ["verify_inventory_history_preservation"])
        self.with_case("inventory13299", check)

    def run_final_producer_boundary(self, trigger):
        import contextlib, inspect, io
        case = ParentDiagnosticHistoryDataContracts("test_parent_diagnostic_history01_default_preserves_all_bytes_without_member_io")
        case.setUp()
        original_control = m._parent_diagnostic_history_control_readback
        original_core = m.conditional_core_runtime
        original_audit = m.audit
        original_rec = m.rec
        changed = [];failures = [];final_alias_reads = []
        def mutate(frame, target):
            before = m.stable_metadata(target);native = target.stat()
            m.os.utime(target, ns=(native.st_atime_ns, native.st_mtime_ns + 2000000000))
            self.assertNotEqual(m.stable_metadata(target), before)
            changed.append(dict(target=str(target), caller=frame.f_code.co_name, final_mode=frame.f_locals.get("final_mode")))
        def final_index(receipt, expected_metadata=None):
            obj = original_control(receipt, expected_metadata)
            caller = inspect.currentframe().f_back
            outer = caller.f_back
            if trigger == "final_index" and caller.f_code.co_name == "parent_diagnostic_history_output_readback" and "final_mode" in outer.f_locals and Path(receipt["path"]).name == "parent_diagnostic_history_opaque_aliases.json":
                final_alias_reads.append(receipt["path"])
                if len(final_alias_reads) == 2 and not changed:
                    mutate(outer, Path(m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]["path"]))
            return obj
        def final_core():
            value = original_core()
            caller = inspect.currentframe().f_back
            if trigger in ("final_core_Map", "final_core_graph") and caller.f_code.co_name == "audit" and "final_mode" in caller.f_locals and not changed:
                target = Path(m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]["path"]) if trigger == "final_core_Map" else Path(caller.f_locals["closed"]["path"])
                mutate(caller, target)
            return value
        def final_graph_rec(path):
            value = original_rec(path)
            caller = inspect.currentframe().f_back
            if trigger in ("final_graph_Map", "final_graph_C") and caller.f_code.co_name == "audit" and "final_mode" in caller.f_locals and caller.f_locals.get("receipt") == caller.f_locals.get("descriptor") and Path(path).name == "acceptance.json" and not changed:
                target = Path(m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]["path"]) if trigger == "final_graph_Map" else Path(caller.f_locals["closed"]["path"])
                mutate(caller, target)
            return value
        def audit_capture(plan_path, out):
            try:return original_audit(plan_path, out)
            except ValueError:
                path = Path(out)
                incomplete = m.read(path / "typed_incomplete.json")
                self.assertEqual(incomplete["failed_stage"], "inclusion")
                self.assertTrue((path / "parent_diagnostic_history_opaque_leaf_proof.json").is_file())
                self.assertTrue((path / "opaque_parent_diagnostic_history_bytes").is_dir())
                self.assertTrue((path / "acceptance.json").is_file())
                failures.append(copy.deepcopy(incomplete))
                raise
        patch = __import__("unittest.mock", fromlist=["patch"]).patch
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout), patch.object(m, "audit", new=audit_capture), \
                 patch.object(m, "_parent_diagnostic_history_control_readback", new=final_index), \
                 patch.object(m, "conditional_core_runtime", new=final_core), \
                 patch.object(m, "rec", new=final_graph_rec):
                expected = "Fixed history final native union drifted" if trigger in ("final_graph_Map", "final_graph_C") else "Actual finite history final graph bytes/native metadata changed before final status" if trigger == "final_core_graph" else "Fixed inherited history authority changed after final control read"
                with self.assertRaisesRegex(ValueError, expected):case.run_genuine_audit()
            self.assertEqual(len(changed), 1);self.assertEqual(len(failures), 1)
            self.assertEqual(changed[0]["caller"], "audit")
            self.assertIs(type(changed[0]["final_mode"]), int)
            self.assertEqual(failures[0]["reason"], expected)
            # The earlier intermediate acceptance JSON is historical output only.
            # The actual final status must never be emitted after final guard failure.
            self.assertNotIn("FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED", stdout.getvalue())
            if trigger == "final_index":self.assertEqual(len(final_alias_reads), 2)
        finally:case.tearDown()

    def test_mapping31_genuine_final_callback_last_alias_JSON_Map_drift_rejects_final_status(self):
        self.run_final_producer_boundary("final_index")

    def test_mapping32_genuine_after_final_Source_Core_Map_drift_rejects_final_status(self):
        self.run_final_producer_boundary("final_core_Map")

    def test_mapping33_actual_adapter_after_final_Source_Core_Map_drift_rejects_descriptor(self):
        case = ParentDiagnosticHistoryAdapterCAContracts("test_parent_diagnostic_history46_actual_adapter_CA_enrollment_rejects_later_proof_native_drift")
        case._mapping_final_drift = True
        case.test_parent_diagnostic_history46_actual_adapter_CA_enrollment_rejects_later_proof_native_drift()

    def test_mapping34_genuine_after_final_Source_Core_graph_drift_rejects_final_status(self):
        self.run_final_producer_boundary("final_core_graph")

    def test_mapping35_final_four_authority_fence_never_parses_JSON_or_refreshes_saved_native(self):
        def check(case, config):
            case.observe();before = copy.deepcopy(case.scope.authorities_before)
            patch = __import__("unittest.mock", fromlist=["patch"]).patch
            with patch.object(m, "_strict_history_json", side_effect=AssertionError("NO_JSON")), \
                 patch.object(m, "read", side_effect=AssertionError("NO_JSON")), \
                 patch.object(case.scope, "_inputs", side_effect=AssertionError("NO_SCOPE_INPUTS")), \
                 patch.object(case.scope, "readback", side_effect=AssertionError("NO_SCOPE_READBACK")):
                self.assertTrue(m._fixed_history_authority_fence(config[0], before))
            self.assertEqual(before, case.scope.authorities_before)
            target = Path(m._FIXED_HISTORY_MAPPING_PARENTS[0]["receipt"]["path"]);native = target.stat()
            m.os.utime(target, ns=(native.st_atime_ns, native.st_mtime_ns + 2000000000))
            with self.assertRaisesRegex(ValueError, "authority changed after final control read"):
                m._fixed_history_authority_fence(config[0], before)
            self.assertEqual(before, case.scope.authorities_before)
        self.for_families(check)

    def test_mapping36_genuine_LAST_graph_real_receipt_then_earlier_Map_or_C_native_drift_rejects_final_status(self):
        for target in ("final_graph_Map", "final_graph_C"):
            with self.subTest(target=target):self.run_final_producer_boundary(target)

    def test_mapping37_actual_adapter_LAST_CA_real_receipt_then_earlier_Map_or_C_native_drift_rejects_descriptor(self):
        for target in ("Map", "C"):
            case = ParentDiagnosticHistoryAdapterCAContracts("test_parent_diagnostic_history46_actual_adapter_CA_enrollment_rejects_later_proof_native_drift")
            case._mapping_final_graph_drift = target
            with self.subTest(target=target):case.test_parent_diagnostic_history46_actual_adapter_CA_enrollment_rejects_later_proof_native_drift()


class CatalogMSAGapContextContracts(unittest.TestCase):
    """Exact documentary slots, ordinary siblings, and real final native guards."""
    private_names=("_CATALOG_MSA_CATALOG","_CATALOG_MSA_ACCEPTANCE","_CATALOG_MSA_BASE_C",
                   "_CATALOG_MSA_EDGE_SEAL","_CATALOG_MSA_DEFINITIONS")
    def setUp(self):
        self.fixture=ClosureFixtureContracts("test_real_closure_preserves_old_and_accepts_new_default")
        self.fixture.setUp();self.root=self.fixture.root;self.out=self.root/"audit_out"
        self.saved={n:copy.deepcopy(getattr(m,n))for n in self.private_names}
        self.original_read=m.read;self.original_rec=m.rec;self.patch=__import__("unittest.mock",fromlist=["patch"]).patch
        self.common=self.root/"source/rebuild/benchmark_common_review.py"
        self.common.parent.mkdir(parents=True);self.common.write_text("raise RuntimeError('OWN_TMP_CURRENT_SOURCE_MUST_NOT_EXECUTE')\n");self.common.chmod(0o444)
        self.current=m.rec(self.common)
        self.old=self.fixture.file("accepted_frozen_native.py","raise RuntimeError('FROZEN_NATIVE_SOURCE_DATA_ONLY')\n")
        self.new=self.fixture.file("accepted_frozen_common_v2.py","raise RuntimeError('FROZEN_NEW_SOURCE_DATA_ONLY')\n")
        definitions=copy.deepcopy(m._CATALOG_MSA_DEFINITIONS)
        for slot,d in enumerate(definitions):
            d["original"]["path"]=str(self.common)
            d["parent"]=str(self.fixture.asset/("historical_msa_%d.json"%slot))
            d["shortest_receipt_chain"][-1]["parent_path"]=d["parent"]
        m._CATALOG_MSA_DEFINITIONS=definitions
        self.definitions=definitions
        self.edge_seal=self.fixture.meta("catalog_edge_seal.json",dict(status="SYNTHETIC_EDGE_SEAL_ONLY",historical_MSA_gaps=definitions))
        Path(self.edge_seal["path"]).chmod(0o664)
        m._CATALOG_MSA_EDGE_SEAL=dict(self.edge_seal)
        dummy=dict(receipt=r(p=str(self.fixture.asset/"unavailable_runtime.py")),parent=str(self.fixture.asset/"runtime_parent.json"),
                   field=["adapter_source"],subtype="HISTORICAL_UNRESOLVED_PROVENANCE",
                   role="OLD_READINESS_ENGINEERING_HISTORY_NOT_ACTUAL_NATIVE_INFERENCE_SOURCE")
        gaps=[dummy];edges=[dict(receipt=dummy["receipt"],parent=dummy["parent"],field=dummy["field"],role="TYPED_NONOPERATIVE_HISTORICAL_GAP")]
        for d in definitions:
            gap=dict(receipt=d["original"],parent=d["parent"],field=d["trail"],subtype=d["subtype"],role=d["role"],
                     root_decision=m._CATALOG_MSA_ROOT_DECISION,parent_sha256=d["shortest_receipt_chain"][-1]["parent_sha256"],
                     actual_operative_scientific_source=self.old,shortest_receipt_chain=d["shortest_receipt_chain"])
            gaps.append(gap);edges.append(dict(receipt=d["original"],parent=d["parent"],field=d["trail"],role="TYPED_NONOPERATIVE_HISTORICAL_GAP"))
        self.base=dict(schema="benchmark-source-receipt-closure.v1",edges=edges,historical_gaps=gaps,source_missing_allowed_only_exact_historical_edges=True)
        self.base_receipt=self.fixture.meta("catalog_base_closure.json",self.base)
        m._CATALOG_MSA_BASE_C=dict(self.base_receipt)
        base_A=self.original_read(self.fixture.p["base_acceptance"]["path"])
        base_I=self.original_read(base_A["source_inclusion"]["path"])
        base_I["source_receipt_closure"]=self.base_receipt
        base_A["source_inclusion"]=self.fixture.meta("catalog_base_inclusion.json",base_I)
        base_A["source_closure"]=self.base_receipt
        self.fixture.p["base_acceptance"]=self.fixture.meta("catalog_source_base_A.json",base_A)
        self.catalog=dict(schema="native74_cache_catalog.v1",status="NATIVE74_RAW_CACHE_CATALOG_VERIFIED_FUTURE_FORMAL_BINDING_PENDING",
                          native_acceptance=self.fixture.meta("ordinary_catalog_native_A.json",dict(status="OWN_CONTROL_NOT_SCIENCE")),
                          independent_edge_seal=self.edge_seal,old_plan=self.fixture.meta("ordinary_catalog_plan.json",{"ordinary":True}),
                          old_source=self.old,new_source=self.new,new_source_bundle=self.fixture.meta("ordinary_source_bundle.json",{"ordinary":True}),
                          source_compatibility={},rows=[],workers=20,raw_models=74,source_roots=["documentary1","documentary2","documentary3"],
                          split_recovery_index18_retained=True,historical_MSA_derivation_gaps_preserved=definitions,
                          historical_missing_exemption_for_current_inputs=False,old_runtime_locks={},old_af2_parameter_receipts=[],
                          no_new_predictions=True,no_scores_transferred=True,new_inference_GPU_seconds=0,
                          old_GPU_cost_not_recharged=True,future_formal_binding=False)
        self.catalog_path=self.fixture.asset/"actual_catalog.json"
        self.acceptance_path=self.fixture.asset/"actual_catalog_A.json"
        self.rewrite_catalog(self.catalog)
        self.install_module("final_delivery_tools")
    def tearDown(self):
        for n,value in self.saved.items():setattr(m,n,value)
        self.fixture.tearDown()
    def write_replace(self,path,obj):
        if path.exists():
            self.assertFalse(path.is_symlink());self.assertEqual(path.lstat().st_nlink,1)
            path.unlink()
        return m.dump(path,obj)
    def rewrite_catalog(self,obj):
        self.catalog=copy.deepcopy(obj)
        self.catalog_receipt=self.write_replace(self.catalog_path,self.catalog)
        m._CATALOG_MSA_CATALOG=dict(self.catalog_receipt)
        self.acceptance=dict(status="CPU_CACHE_GUARD_CATALOG_COMPLETE",result=self.catalog_receipt,
                             no_inference=True,no_GPU_submission=True,formal_binding=False)
        self.acceptance_receipt=self.write_replace(self.acceptance_path,self.acceptance)
        m._CATALOG_MSA_ACCEPTANCE=dict(self.acceptance_receipt)
        if hasattr(self,"fixture"):
            gate=next(x for x in self.fixture.p["modules"]if x["role"]=="native74_cache_catalog")
            gate["gate"]=dict(receipt=self.acceptance_receipt,expected_status="CPU_CACHE_GUARD_CATALOG_COMPLETE")
    def install_module(self,module):
        selected=next(x for x in self.fixture.p["modules"]if x["role"]==module)
        if module=="final_delivery_tools":selected["seeds"]=[self.acceptance_receipt]
        self.fixture.p["modules"]=[x for x in self.fixture.p["modules"]if x is not selected]+[selected]
    def scope(self):
        value=m.CatalogMSAGapContexts(self.base_receipt);value.bind_base(self.base)
        value.opened(self.catalog_receipt,Path(self.catalog_receipt["path"]),copy.deepcopy(self.catalog),"final_delivery_tools")
        return value
    def observe_pair(self,scope,module="final_delivery_tools"):
        return [scope.edge(self.definitions[slot]["original"],self.catalog_receipt["path"],
                           (m._CATALOG_MSA_FIELD,str(slot),"original"),module,{})for slot in (1,0)]
    def graph(self,scope,observations):
        readback=dict(receipt=self.catalog_receipt,parent=self.acceptance_receipt["path"],field=["result"],
                      module=scope.parses[-1],physical=self.catalog_receipt,role="EXACT_NEW_TEXT_RECEIPT_READBACK")
        return dict(base_closure=self.base_receipt,edges=[readback]+observations)
    def genuine(self,module="final_delivery_tools",mutation=None):
        self.install_module(module);observed=[];opened=[];changed=[];printed=[]
        original_edge=m.CatalogMSAGapContexts.edge;original_open=Path.open
        original_parse=m._catalog_msa_json
        originals={name:getattr(Path,name)for name in ("stat","lstat","resolve")}
        def metadata_method(name):
            def call(path,*args,**kwargs):
                if Path(path)==self.common:
                    opened.append(str(path));raise AssertionError("UNRESOLVED_COMMON_TARGET_METADATA_IO")
                return originals[name](path,*args,**kwargs)
            return call
        def edge(scope,receipt,parent,trail,role,history):
            result=original_edge(scope,receipt,parent,trail,role,history)
            if result is not None:
                caller=__import__("inspect").currentframe().f_back
                self.assertEqual(caller.f_code.co_name,"audit")
                self.assertEqual(caller.f_locals["stage"],"recursive_exact_new_dependencies")
                self.assertEqual(result["role"],m._CATALOG_MSA_ROLE)
                observed.append(copy.deepcopy(result))
            return result
        def open(path,*args,**kwargs):
            if Path(path)==self.common:
                opened.append(str(path));raise AssertionError("UNRESOLVED_COMMON_TARGET_PAYLOAD_IO")
            return original_open(path,*args,**kwargs)
        def read(path):
            value=self.original_read(path)
            if mutation=="last_JSON" and Path(path)==self.out/"acceptance.json" and not changed:
                target=Path(self.base_receipt["path"]);before=target.stat()
                m.os.utime(target,ns=(before.st_atime_ns,before.st_mtime_ns+2000000000));changed.append(str(target))
            return value
        def parse(text):
            value=original_parse(text)
            if mutation=="last_JSON" and value.get("schema")=="final-source-closure-acceptance.v3" and not changed:
                target=Path(self.base_receipt["path"]);before=target.stat()
                m.os.utime(target,ns=(before.st_atime_ns,before.st_mtime_ns+2000000000));changed.append(str(target))
            return value
        def rec(path):
            value=self.original_rec(path)
            if mutation=="last_graph" and Path(path)==self.out/"acceptance.json" and Path(path).exists() and not changed:
                caller=__import__("inspect").currentframe().f_back
                if caller.f_code.co_name=="audit" and caller.f_lineno>0 and caller.f_locals.get("descriptor") and caller.f_locals.get("stage")=="inclusion":
                    target=Path(self.base_receipt["path"]);before=target.stat()
                    m.os.utime(target,ns=(before.st_atime_ns,before.st_mtime_ns+2000000000));changed.append(str(target))
            return value
        original_print=__import__("builtins").print
        def print(*args,**kwargs):
            printed.extend(str(x)for x in args);return original_print(*args,**kwargs)
        with self.patch.object(m.CatalogMSAGapContexts,"edge",new=edge),self.patch.object(Path,"open",new=open),\
             self.patch.object(m,"read",new=read),self.patch.object(m,"rec",new=rec),self.patch.object(m,"_catalog_msa_json",new=parse),self.patch("builtins.print",new=print),\
             self.patch.object(Path,"stat",new=metadata_method("stat")),self.patch.object(Path,"lstat",new=metadata_method("lstat")),\
             self.patch.object(Path,"resolve",new=metadata_method("resolve")):
            if mutation:
                with self.assertRaisesRegex(ValueError,"^Fixed history final native union drifted$"):self.fixture.run_fixture()
            else:included=self.fixture.run_fixture()
        self.assertFalse(opened)
        self.assertEqual(len(observed),2)
        self.assertEqual([x["field"][1]for x in observed],["1","0"])
        self.assertTrue(all(x["module"]==module for x in observed))
        if mutation:
            self.assertEqual(changed,[self.base_receipt["path"]])
            self.assertNotIn("FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED",printed)
            self.assertEqual(self.original_read(self.out/"typed_incomplete.json")["failed_stage"],"inclusion")
            return
        C=self.original_read(self.out/"source_receipt_closure_final.json")
        self.assertTrue(m.catalog_msa_gap_projection_shape(self.catalog,self.acceptance,self.base,C))
        for receipt in (self.old,self.new):
            row=next(x for x in included["files"]if m.fp(x["source"])==m.fp(receipt))
            self.assertEqual(row["original_source"],receipt);self.assertIn(receipt,row["logical_receipts"])
            self.assertEqual(row["kind"],"IMPLEMENTATION")
            self.assertIn("RECURSIVE_OPERATIVE_SOURCE",row["roles"])
            self.assertTrue(any(e.get("receipt")==receipt and e.get("parent")==self.catalog_receipt["path"]
                                and e.get("role")=="EXACT_NEW_TEXT_RECEIPT_READBACK"for e in C["edges"]))
        self.assertFalse(any(m._catalog_msa_old_fingerprint(x["source"])for x in included["files"]))
        self.assertEqual(len(self.base["historical_gaps"]),3)
        self.assertEqual(m.stat.S_IMODE(Path(self.edge_seal["path"]).stat().st_mode),0o664)
        self.assertFalse(any(x.name.startswith("catalog")for x in self.out.iterdir()))
        return C,included,observed
    def test_catalog01_genuine_finaltools_both_slots_ordinary_current_sources_and_no_target_IO(self):
        self.genuine()
    def test_catalog02_genuine_nativecatalog_prospective_route_both_slots(self):
        self.genuine("native74_cache_catalog")
    def test_catalog03_exact_full_catalog_identity_rejects_wrong_tuple_and_FP_clone(self):
        scope=self.scope()
        for value in (dict(self.catalog_receipt,bytes=self.catalog_receipt["bytes"]+1),dict(self.catalog_receipt,path=str(self.root/"clone.json"))):
            with self.assertRaisesRegex(ValueError,"Exact accepted catalog identity"):scope.incoming(value,"final_delivery_tools")
    def test_catalog04_only_two_modules_and_no_context_parent_permission(self):
        scope=self.scope()
        for module in ("EXACT_ACCEPTED_CONTEXT_PARENT","default_workflow_integration","formal_common_review"):
            with self.assertRaisesRegex(ValueError,"two-module context"):scope.incoming(self.catalog_receipt,module)
    def test_catalog05_accepted_A_result_fulltuple_is_required(self):
        wrong=copy.deepcopy(self.acceptance);wrong["result"]["bytes"]+=1
        with self.assertRaisesRegex(ValueError,"A/result"):m._catalog_msa_definition_shape(self.catalog,wrong,self.base)
    def test_catalog06_exact_23_keys_schema_status_and_false_exemption(self):
        for field,value in (("schema","other"),("status","other"),("historical_missing_exemption_for_current_inputs",True)):
            obj=copy.deepcopy(self.catalog);obj[field]=value
            with self.assertRaises(ValueError):m._catalog_msa_definition_shape(obj,self.acceptance,self.base)
        obj=copy.deepcopy(self.catalog);obj["generic_permission"]=True
        with self.assertRaises(ValueError):m._catalog_msa_definition_shape(obj,self.acceptance,self.base)
    def test_catalog07_ordered_definitions_subtype_role_and_whole_chain_are_exact(self):
        for kind in ("order","role","subtype","chain"):
            obj=copy.deepcopy(self.catalog)
            if kind=="order":obj[m._CATALOG_MSA_FIELD].reverse()
            elif kind=="chain":obj[m._CATALOG_MSA_FIELD][0]["shortest_receipt_chain"][0]["field"]=["other"]
            else:obj[m._CATALOG_MSA_FIELD][0][kind]="other"
            with self.assertRaises(ValueError):m._catalog_msa_definition_shape(obj,self.acceptance,self.base)
    def test_catalog08_BaseC_root_decision_parent_SHA_and_operative_source_are_exact(self):
        for field,value in (("root_decision","other"),("parent_sha256","a"*64),("actual_operative_scientific_source",self.definitions[0]["original"])):
            base=copy.deepcopy(self.base);base["historical_gaps"][1][field]=value
            with self.assertRaises(ValueError):m._catalog_msa_definition_shape(self.catalog,self.acceptance,base)
    def test_catalog09_unique_typed_edges_and_original_three_gap_denominator(self):
        base=copy.deepcopy(self.base);base["edges"].append(copy.deepcopy(base["edges"][1]))
        with self.assertRaisesRegex(ValueError,"Unique original"):m._catalog_msa_definition_shape(self.catalog,self.acceptance,base)
        base=copy.deepcopy(self.base);base["historical_gaps"].pop(0)
        with self.assertRaisesRegex(ValueError,"Original three"):m._catalog_msa_definition_shape(self.catalog,self.acceptance,base)
    def test_catalog10_exact_slot_tuple_module_and_parent_are_coupled_before_seen(self):
        for wrong in ("slot","tuple","module","parent"):
            scope=self.scope();r=self.definitions[1]["original"];parent=self.catalog_receipt["path"]
            trail=(m._CATALOG_MSA_FIELD,"1","original");module="final_delivery_tools"
            if wrong=="slot":trail=(m._CATALOG_MSA_FIELD,"0","original")
            if wrong=="tuple":r=dict(r,bytes=r["bytes"]+1)
            if wrong=="module":module="default_workflow_integration"
            if wrong=="parent":parent=str(self.root/"wrong.json")
            with self.assertRaises(ValueError):scope.edge(r,parent,trail,module,{})
            self.assertFalse(scope.observations)
    def test_catalog11_valid_pair_then_wrong_context_and_FP_clone_still_reject(self):
        scope=self.scope();self.observe_pair(scope)
        for value in (self.definitions[0]["original"],dict(self.definitions[0]["original"],path=str(self.root/"clone.py"))):
            with self.assertRaisesRegex(ValueError,"cannot authorize"):scope.edge(value,str(self.root/"other.json"),("source",),"final_delivery_tools",{})
        self.assertEqual(len(scope.observations),2)
    def test_catalog12_original_exact_accepted_history_context_is_unchanged(self):
        scope=self.scope();d=self.definitions[0];ek=(m.key(d["original"]),d["parent"],tuple(d["trail"]))
        self.assertIsNone(scope.edge(d["original"],d["parent"],tuple(d["trail"]),"default_workflow_integration",{ek:{"role":"TYPED_NONOPERATIVE_HISTORICAL_GAP"}}))
        self.assertFalse(scope.observations)
    def test_catalog13_direct_Source_gate_seed_context_parent_and_alias_reject(self):
        for kind in ("source","gate","seed","context","logical","physical"):
            p=copy.deepcopy(self.fixture.p);module=p["modules"][0];old=self.definitions[0]["original"]
            if kind=="source":module["sources"][0]["receipt"]=old
            elif kind=="gate":module["gate"]["receipt"]=old
            elif kind=="seed":module["seeds"]=[old]
            elif kind=="context":p["context_parent_seeds"]=[old]
            else:p["aliases"]=[dict(logical=old if kind=="logical"else self.old,physical=old if kind=="physical"else self.old)]
            with self.assertRaisesRegex(ValueError,"Catalog MSA historical declaration"):m.module_plan(p)
    def test_catalog14_current_other_fingerprint_sharing_Common_path_is_ordinary(self):
        self.assertNotEqual(m.fp(self.current),m.fp(self.definitions[0]["original"]))
        self.assertIsNone(m.reject_catalog_msa_gap_declaration(self.current))
        scope=self.scope()
        self.assertIsNone(scope.edge(self.current,str(self.root/"ordinary.json"),("source",),"final_delivery_tools",{}))
        self.assertEqual(m.verify(self.current),self.common)
    def test_catalog15_genuine_other_current_catalog_child_cannot_use_historical_exemption(self):
        obj=copy.deepcopy(self.catalog);obj["new_source"]=self.definitions[0]["original"];self.rewrite_catalog(obj)
        seen=[];original=m.CatalogMSAGapContexts.edge
        def edge(scope,*args):
            value=original(scope,*args)
            if value:seen.append(value)
            return value
        with self.patch.object(m.CatalogMSAGapContexts,"edge",new=edge):
            with self.assertRaisesRegex(ValueError,"cannot authorize"):self.fixture.run_fixture()
        self.assertEqual(len(seen),2)
        self.assertEqual(self.original_read(self.out/"typed_incomplete.json")["failed_stage"],"recursive_exact_new_dependencies")
        self.assertFalse((self.out/"acceptance.json").exists())
    def test_catalog16_genuine_inherited_BaseI_source_rejects_before_target_verify(self):
        accepted=self.original_read(self.fixture.p["base_acceptance"]["path"])
        inclusion=self.original_read(accepted["source_inclusion"]["path"])
        inclusion["files"][2]["source"]=self.definitions[0]["original"]
        accepted["source_inclusion"]=self.fixture.meta("bad_inherited_I.json",inclusion)
        self.fixture.p["base_acceptance"]=self.fixture.meta("bad_inherited_A.json",accepted)
        # The targeted inherited Source declaration guard precedes verify(row.source).
        called=[];original=m.reject_catalog_msa_gap_declaration
        def guard(receipt):
            if m._catalog_msa_old_fingerprint(receipt):
                called.append(__import__("inspect").currentframe().f_back.f_code.co_name)
            return original(receipt)
        with self.patch.object(m,"reject_catalog_msa_gap_declaration",new=guard):
            with self.assertRaisesRegex(ValueError,"Catalog MSA historical declaration"):self.fixture.run_fixture()
        self.assertEqual(called,["audit"])
        self.assertEqual(self.original_read(self.out/"typed_incomplete.json")["failed_stage"],"base_readback")
        self.assertFalse((self.out/"acceptance.json").exists())
    def inherited_add_route(self,logical):
        original=m.inherited_source_route;called=[];original_guard=m.reject_catalog_msa_gap_declaration
        def route(row,ops):
            result=original(row,ops)
            if row["repository_relative"]=="rebuild/unrelated.py":
                row["original_source" if logical else "source"]=self.definitions[0]["original"]
            return result
        def guard(receipt):
            caller=__import__("inspect").currentframe().f_back
            if m._catalog_msa_old_fingerprint(receipt):
                called.append((caller.f_code.co_name,caller.f_locals.get("r"),caller.f_locals.get("logical")))
            return original_guard(receipt)
        with self.patch.object(m,"inherited_source_route",new=route),self.patch.object(m,"reject_catalog_msa_gap_declaration",new=guard):
            with self.assertRaisesRegex(ValueError,"Catalog MSA historical declaration"):self.fixture.run_fixture()
        self.assertEqual(len(called),1);self.assertEqual(called[0][0],"add")
        self.assertEqual(called[0][2] if logical else called[0][1],self.definitions[0]["original"])
        self.assertEqual(self.original_read(self.out/"typed_incomplete.json")["failed_stage"],"base_readback")
        self.assertFalse((self.out/"acceptance.json").exists())
    def test_catalog17_genuine_after_alias_inherited_add_r_guard(self):
        self.inherited_add_route(False)
    def test_catalog18_genuine_after_alias_inherited_add_logical_guard(self):
        self.inherited_add_route(True)
    def test_catalog19_genuine_BaseC_physical_alias_guard_rejects_historical_FP(self):
        base=copy.deepcopy(self.base);base["edges"].append(dict(receipt=self.old,parent=None,field=[],physical=self.definitions[0]["original"],role="EXACT_TEXT_RECEIPT_READBACK"))
        receipt=self.fixture.meta("alias_base_C.json",base);m._CATALOG_MSA_BASE_C=receipt;self.base_receipt=receipt;self.base=base
        accepted=self.original_read(self.fixture.p["base_acceptance"]["path"]);included=self.original_read(accepted["source_inclusion"]["path"])
        included["source_receipt_closure"]=receipt;accepted["source_closure"]=receipt
        accepted["source_inclusion"]=self.fixture.meta("alias_base_I.json",included)
        self.fixture.p["base_acceptance"]=self.fixture.meta("alias_base_A.json",accepted)
        called=[];original=m.reject_catalog_msa_gap_declaration
        def guard(r):
            if m._catalog_msa_old_fingerprint(r):called.append(__import__("inspect").currentframe().f_back.f_code.co_name)
            return original(r)
        with self.patch.object(m,"reject_catalog_msa_gap_declaration",new=guard):
            with self.assertRaisesRegex(ValueError,"Catalog MSA historical declaration"):self.fixture.run_fixture()
        self.assertEqual(called,["alias"]);self.assertFalse((self.out/"acceptance.json").exists())
    def test_catalog20_genuine_resolve_defense_with_only_fixture_edge_bypass(self):
        obj=copy.deepcopy(self.catalog);obj["new_source"]=self.definitions[0]["original"];self.rewrite_catalog(obj)
        called=[];original=m.reject_catalog_msa_gap_declaration
        def guard(r):
            if m._catalog_msa_old_fingerprint(r):called.append(__import__("inspect").currentframe().f_back.f_code.co_name)
            return original(r)
        with self.patch.object(m.CatalogMSAGapContexts,"edge",return_value=None),self.patch.object(m,"reject_catalog_msa_gap_declaration",new=guard):
            with self.assertRaisesRegex(ValueError,"Catalog MSA historical declaration"):self.fixture.run_fixture()
        self.assertEqual(called,["resolve"]);self.assertEqual(self.original_read(self.out/"typed_incomplete.json")["failed_stage"],"recursive_exact_new_dependencies")
        self.assertFalse((self.out/"acceptance.json").exists())
    def test_catalog21_native_metadata_after_last_graph_JSON_rejects_final_status(self):
        self.genuine(mutation="last_JSON")
    def test_catalog22_final_graph_real_receipt_then_earlier_BaseC_drift_rejects(self):
        self.genuine(mutation="last_graph")
    def test_catalog23_whole_input_byte_drift_is_not_a_historical_waiver(self):
        scope=self.scope();self.observe_pair(scope)
        path=self.catalog_path;original=path.read_bytes();changed=original.replace(b'": ',b'" :',1)
        self.assertEqual(len(changed),len(original));self.assertNotEqual(changed,original);self.assertEqual(json.loads(changed),json.loads(original))
        path.chmod(0o644);path.write_bytes(changed);path.chmod(0o444)
        with self.assertRaisesRegex(ValueError,"own bytes/native changed"):scope.fence()
        self.assertFalse((self.out/"acceptance.json").exists())
    def test_catalog24_native_symlink_hardlink_and_writable_controls_reject(self):
        for kind in ("symlink","hardlink","writable"):
            path=self.acceptance_path;original=path.read_bytes();saved=m._CATALOG_MSA_ACCEPTANCE
            if kind=="symlink":
                backing=path.with_name("backing_A.json");path.rename(backing);path.symlink_to(backing)
            elif kind=="hardlink":m.os.link(path,path.with_name("linked_A.json"))
            else:path.chmod(0o664)
            with self.assertRaises(ValueError):m.CatalogMSAGapContexts(self.base_receipt)
            if kind=="symlink":path.unlink();backing.rename(path)
            elif kind=="hardlink":path.with_name("linked_A.json").unlink()
            else:path.chmod(0o444)
            self.assertEqual(path.read_bytes(),original);m._CATALOG_MSA_ACCEPTANCE=saved
    def test_catalog25_strict_JSON_duplicate_nonfinite_overflow_and_UTF8_reject(self):
        for text in ('{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}','{"x":1e999}'):
            with self.assertRaises(ValueError):m._catalog_msa_json(text)
        self.catalog_path.chmod(0o644);self.catalog_path.write_bytes(b"\xff");self.catalog_path.chmod(0o444)
        self.catalog_receipt=m.rec(self.catalog_path);m._CATALOG_MSA_CATALOG=dict(self.catalog_receipt)
        self.acceptance["result"]=self.catalog_receipt
        self.acceptance_receipt=self.write_replace(self.acceptance_path,self.acceptance)
        m._CATALOG_MSA_ACCEPTANCE=dict(self.acceptance_receipt)
        scope=m.CatalogMSAGapContexts(self.base_receipt);scope.bind_base(self.base)
        with self.assertRaises(UnicodeDecodeError):
            scope.opened(self.catalog_receipt,self.catalog_path,self.catalog,"final_delivery_tools")
    def test_catalog26_pure_INDEX_replay_has_no_filesystem_rec_or_verify_calls(self):
        scope=self.scope();edges=self.observe_pair(scope);C=self.graph(scope,edges)
        with self.patch.object(m,"rec",side_effect=AssertionError("NO_HASH")),self.patch.object(m,"verify",side_effect=AssertionError("NO_LIVE_VERIFY")),\
             self.patch.object(m,"stable_metadata",side_effect=AssertionError("NO_FS")),self.patch.object(m,"safe_path",side_effect=AssertionError("NO_PATH")):
            self.assertTrue(m.catalog_msa_gap_projection_shape(self.catalog,self.acceptance,self.base,C))
            self.assertEqual(m.catalog_msa_gap_projection_native(C),scope.original_metadata)
    def test_catalog27_pure_INDEX_context_order_slot_native_and_flags_tamper_reject(self):
        scope=self.scope();C=self.graph(scope,self.observe_pair(scope))
        for kind in ("order","slot","module","native","flags","BaseC"):
            value=copy.deepcopy(C)
            if kind=="order":value["edges"][1:]=reversed(value["edges"][1:])
            elif kind=="slot":value["edges"][1]["field"][1]="0"
            elif kind=="module":value["edges"][1]["module"]="default_workflow_integration"
            elif kind=="native":value["edges"][1]["catalog_msa_gap_projection"]["original_metadata_after"][0]["ctime_ns"]+=1
            elif kind=="flags":value["edges"][1]["catalog_msa_gap_projection"]["old_source_restored"]=True
            else:value["base_closure"]["sha256"]="a"*64
            with self.assertRaises(ValueError):m.catalog_msa_gap_projection_shape(self.catalog,self.acceptance,self.base,value)
    def test_catalog28_pure_INDEX_rejects_missing_duplicate_or_operative_old_Source_edges(self):
        scope=self.scope();C=self.graph(scope,self.observe_pair(scope))
        for kind in ("missing","duplicate","operative"):
            value=copy.deepcopy(C)
            if kind=="missing":value["edges"].pop()
            elif kind=="duplicate":value["edges"].append(copy.deepcopy(value["edges"][1]))
            else:value["edges"].append(dict(receipt=self.definitions[0]["original"],parent=self.catalog_receipt["path"],field=["new_source"],role="EXACT_NEW_TEXT_RECEIPT_READBACK"))
            with self.assertRaises(ValueError):m.catalog_msa_gap_projection_shape(self.catalog,self.acceptance,self.base,value)
    def test_catalog29_optional_prospective_module_not_forced_and_original_table_not_refreshed(self):
        scope=self.scope();before=copy.deepcopy(scope.original_metadata)
        edges=self.observe_pair(scope);self.assertTrue(scope.require_complete())
        self.assertEqual(scope.parses,["final_delivery_tools"])
        self.assertTrue(m.catalog_msa_gap_projection_shape(self.catalog,self.acceptance,self.base,self.graph(scope,edges)))
        self.assertEqual(scope.original_metadata,before)
    def test_catalog30_saved_adapter_input_checks_reuse_producer_original_native(self):
        scope=self.scope();C=self.graph(scope,self.observe_pair(scope))
        self.assertTrue(m.catalog_msa_gap_saved_inputs(C))
        baseline=copy.deepcopy(m.catalog_msa_gap_projection_native(C))
        state=self.acceptance_path.stat();m.os.utime(self.acceptance_path,ns=(state.st_atime_ns,state.st_mtime_ns+2000000000))
        with self.assertRaisesRegex(ValueError,"native union drifted"):m.catalog_msa_gap_saved_inputs(C)
        self.assertEqual(m.catalog_msa_gap_projection_native(C),baseline)

    def adapter_graph(self):
        C,I,unused=self.genuine()
        A=self.original_read(self.out/"acceptance.json")
        receipts={name:self.original_rec(self.out/path)for name,path in
                  (("acceptance","acceptance.json"),("source_closure","source_receipt_closure_final.json"),("source_inclusion","source_inclusion_final.json"))}
        CA=dict(schema="final-source-materialized-context-read-view-acceptance.v3",
                status="FINAL_CURRENT_SOURCE_MATERIALIZED_FIVE_PARENT_CONTEXT_AND_DERIVED_V2_CPU_ACCEPTED_NOT_STAGED_NOT_PUBLISHED",
                actual_new_library_acceptance=receipts["acceptance"],source_closure=receipts["source_closure"],source_inclusion=receipts["source_inclusion"],
                SYNTHETIC_CA_PROTOCOL_ONLY=True)
        receipts["context_adapter_acceptance"]=m.dump(self.out/"context_adapter_acceptance.json",CA)
        return {name:(receipt,m.stable_metadata(receipt["path"]))for name,receipt in receipts.items()}
    def test_catalog31_actual_producer_graph_and_synthetic_CA_use_current_adapter_helper(self):
        controls=self.adapter_graph()
        self.assertEqual(m.catalog_msa_gap_graph_readback(controls),
                         m.catalog_msa_gap_projection_native(self.original_read(controls["source_closure"][0]["path"])))
        self.assertEqual(len(controls),4)
    def test_catalog32_later_fixed_input_JSON_real_CA_native_drift_rejects(self):
        controls=self.adapter_graph();CA=Path(controls["context_adapter_acceptance"][0]["path"]);changed=[]
        original=m._catalog_msa_json
        def parse(text):
            value=original(text)
            if value.get("schema")=="benchmark-source-receipt-closure.v1" and not changed:
                state=CA.stat();m.os.utime(CA,ns=(state.st_atime_ns,state.st_mtime_ns+2000000000));changed.append(str(CA))
            return value
        with self.patch.object(m,"_catalog_msa_json",new=parse):
            with self.assertRaisesRegex(ValueError,"graph changed after all final JSON"):m.catalog_msa_gap_graph_readback(controls)
        self.assertEqual(changed,[str(CA)])
    def test_catalog33_later_CA_JSON_real_earlier_C_native_drift_rejects(self):
        controls=self.adapter_graph();target=Path(controls["source_closure"][0]["path"]);changed=[]
        original=m._catalog_msa_json
        def parse(text):
            value=original(text)
            if value.get("SYNTHETIC_CA_PROTOCOL_ONLY")is True and not changed:
                state=target.stat();m.os.utime(target,ns=(state.st_atime_ns,state.st_mtime_ns+2000000000));changed.append(str(target))
            return value
        with self.patch.object(m,"_catalog_msa_json",new=parse):
            with self.assertRaisesRegex(ValueError,"graph changed after all final JSON"):m.catalog_msa_gap_graph_readback(controls)
        self.assertEqual(changed,[str(target)])
    def test_catalog34_true_LAST_graph_receipt_then_earlier_input_native_drift_rejects(self):
        controls=self.adapter_graph();changed=[];original=m.rec
        CA=controls["context_adapter_acceptance"][0]["path"];target=Path(self.base_receipt["path"])
        def rec(path):
            value=original(path);caller=__import__("inspect").currentframe().f_back
            if str(path)==CA and caller.f_code.co_name=="catalog_msa_gap_graph_readback" and caller.f_locals.get("catalog_inputs")is not None and not changed:
                state=target.stat();m.os.utime(target,ns=(state.st_atime_ns,state.st_mtime_ns+2000000000));changed.append(str(target))
            return value
        with self.patch.object(m,"rec",new=rec):
            with self.assertRaisesRegex(ValueError,"Fixed history final native union drifted"):m.catalog_msa_gap_graph_readback(controls)
        self.assertEqual(changed,[str(target)])

    def test_catalog35_actual_adapter_first_C_JSON_native_drift_rejects_original_baseline(self):
        """Real adapter startup; synthetic unrelated protocols, no native/rec guard mocks."""
        import builtins,inspect
        method="test_parent_diagnostic_history46_actual_adapter_CA_enrollment_rejects_later_proof_native_drift"
        for tamper in (False,True):
            with self.subTest(tamper=tamper):
                original_text=Path.read_text;original_dump=m.dump;original_print=builtins.print
                events=[];changed=[];incomplete=[];descriptors=[]
                def actual_run_frame():
                    frame=inspect.currentframe().f_back
                    while frame is not None:
                        if frame.f_code.co_name=="run" and Path(frame.f_code.co_filename).name=="final_source_context_adapter.py":
                            return frame
                        frame=frame.f_back
                    return None
                def read_text(path,*args,**kwargs):
                    text=original_text(path,*args,**kwargs)
                    frame=actual_run_frame()
                    if frame is not None and "accepted"in frame.f_locals and "catalog_C"not in frame.f_locals:
                        target=Path(frame.f_locals["accepted"]["source_closure"]["path"])
                        if Path(path)==target:
                            objects=json.loads(text)
                            self.assertEqual(objects["schema"],"final-source-receipt-closure.v2")
                            native=m.stable_metadata(target)
                            before=copy.deepcopy(frame.f_locals.get("parent_diagnostic_graph_metadata",{}))
                            receipts=copy.deepcopy(frame.f_locals.get("parent_diagnostic_graph_receipts",{}))
                            events.append(dict(path=str(target),native=native,original_table=before,receipts=receipts))
                            if tamper and not changed:
                                actual=m.rec(target);state=target.lstat()
                                m.os.utime(target,ns=(state.st_atime_ns,state.st_mtime_ns+2000000000))
                                after=m.stable_metadata(target)
                                self.assertNotEqual(after,native)
                                self.assertEqual(m.rec(target),actual)
                                changed.append(dict(path=str(target),before=native,after=after,receipt=actual))
                    return text
                def dump(path,obj):
                    receipt=original_dump(path,obj)
                    if obj.get("status")=="FINAL_SOURCE_MATERIALIZED_CONTEXT_ADAPTER_TYPED_INCOMPLETE" and changed:
                        frame=actual_run_frame()
                        self.assertIsNotNone(frame)
                        out=Path(frame.f_locals["out"])
                        self.assertFalse((out/"context_adapter_acceptance.json").exists())
                        self.assertTrue((out/"acceptance.json").is_file())
                        self.assertTrue((out/"source_receipt_closure_final.json").is_file())
                        self.assertTrue((out/"source_inclusion_final.json").is_file())
                        incomplete.append(copy.deepcopy(obj))
                    return receipt
                def print(*args,**kwargs):
                    frame=actual_run_frame()
                    if frame is not None and "result"in frame.f_locals:
                        descriptors.extend(str(value)for value in args)
                    return original_print(*args,**kwargs)
                with self.patch.object(Path,"read_text",new=read_text),self.patch.object(m,"dump",new=dump),\
                     self.patch.object(builtins,"print",new=print):
                    case=ParentDiagnosticHistoryAdapterCAContracts(method)
                    if tamper:
                        with self.assertRaisesRegex(ValueError,"^Actual adapter source closure changed during first JSON read$"):
                            getattr(case,method)()
                    else:getattr(case,method)()
                self.assertEqual(len(events),1 if tamper else 2)
                for event in events:
                    self.assertEqual(set(event["original_table"]),{"acceptance","source_closure","source_inclusion"})
                    self.assertEqual(set(event["receipts"]),set(event["original_table"]))
                    self.assertEqual(event["original_table"]["source_closure"],event["native"])
                    for name,metadata in event["original_table"].items():
                        self.assertEqual(metadata["path"],event["receipts"][name]["path"])
                        self.assertEqual(metadata["bytes"],event["receipts"][name]["bytes"])
                        self.assertTrue(m.stat.S_ISREG(metadata["mode"]))
                        self.assertEqual(m.stat.S_IMODE(metadata["mode"]),0o444)
                        self.assertEqual(metadata["nlink"],1)
                if tamper:
                    self.assertEqual(len(changed),1)
                    self.assertEqual(changed[0]["path"],events[0]["path"])
                    self.assertEqual(changed[0]["before"],events[0]["original_table"]["source_closure"])
                    self.assertEqual(len(incomplete),1)
                    self.assertEqual(incomplete[0]["failed_stage"],"actual_frozen_library_audit_with_module_local_context_reader")
                    self.assertEqual(incomplete[0]["reason_type"],"ValueError")
                    self.assertEqual(incomplete[0]["reason"],"Actual adapter source closure changed during first JSON read")
                    self.assertEqual(descriptors,[])
                else:
                    self.assertEqual(changed,[])
                    self.assertEqual(incomplete,[])
                    self.assertEqual(len(descriptors),1)
                    self.assertIn('"acceptance"',descriptors[0])
