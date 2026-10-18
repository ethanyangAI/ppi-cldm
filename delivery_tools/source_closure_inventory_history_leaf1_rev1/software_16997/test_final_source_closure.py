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
  self.assertEqual(m.SOURCE_CONTRACTS,158);self.assertEqual(m.software_shape(obj,contracts),sources)
  for field in ("whole6_source_prepost_PASS","original_and_frozen_owned_bytes_identical","conditional_runtime_prepost_PASS"):
   fork=copy.deepcopy(obj);fork[field]=False
   with self.subTest(field=field),self.assertRaises(ValueError):m.software_shape(fork,contracts)
  for field in ("source_snapshot","original_executing_sources","source_entry"):
   fork=copy.deepcopy(obj);fork.pop(field)
   with self.subTest(field=field),self.assertRaises((KeyError,ValueError)):m.software_shape(fork,contracts)
  for obsolete_count in (53,65,90,122,154):
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


class InventoryHistoryDataContracts(unittest.TestCase):
    """Synthetic own-byte fixtures; no live member/SCI source is opened by these cases."""

    private_names = ("_HISTORY_BASE", "_HISTORY_AUTHORITY", "_HISTORY_LEAF",
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
        allowed = {self.base_path, self.leaf}

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
