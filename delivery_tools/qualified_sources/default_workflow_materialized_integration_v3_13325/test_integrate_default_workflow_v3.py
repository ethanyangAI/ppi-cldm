import copy,json,os,shutil,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import integrate_default_workflow_v3 as m
class Base(unittest.TestCase):
 def setUp(self):
  parent=m.R/"steps/24_benchmark_delivery/tmp";parent.mkdir(parents=True,exist_ok=True)
  self.temp=tempfile.TemporaryDirectory(prefix="default_integration_fixture_",dir=parent);self.root=Path(self.temp.name)
 def tearDown(self):
  for p in self.root.rglob("*"):
   if p.is_dir():p.chmod(0o755)
   elif p.is_file():p.chmod(0o644)
  self.temp.cleanup()
 def file(self,name,data="fixture"):
  p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data);p.chmod(0o444);return m.rec(p)
 def receipt(self,p):return dict(path=str(p),bytes=1,sha256="a"*64)
 def plan(self):
  q=dict(schema="default-generic-materialized-integration-request.v2",root_approved=True,formal_array_job_id="13260",formal_sources_changed=False,expected_old_tree_sha256=m.BASE,gates={k:{}for k in m.GATES},operations=[dict(repository_relative=n,old=None if i==1 else self.receipt(m.R/"source"/n),new=self.receipt(self.root/("new"+str(i))))for i,n in enumerate(m.PATHS)],runtime_lock_policy="EXACT_REVIEWED_FULL226_RFD_ONLY_CORE_BOLTZ_UNCHANGED",regression_tests=[self.receipt(m.R/"source/tests"/n)for n in sorted(m.REGRESSIONS)],physical_tests=[self.receipt(self.root/n)for n in sorted(m.PHYSICAL)],staged_selector_test=self.receipt(self.root/"test_common_runtime_selector.py"),original_runtime_locks={c:self.receipt(m.R/"source/environment"/("runtime-lock-"+c+".json"))for c in ("core","rfd","boltz")})
  q["context_mapper_acceptance"]=self.receipt(self.root/"mapper_acceptance.json")
  return q
 def transaction(self):
  source=self.root/"source";source.mkdir();ops={}
  for i,n in enumerate(m.PATHS):
   old=None
   if i!=1:
    p=source/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text("old-"+str(i)+"\n");p.chmod(0o640);old=m.rec(p)
   ops[n]=dict(repository_relative=n,old=old,new=self.file("accepted/new"+str(i),"new-"+str(i)+"\n"))
  out=self.root/"out";out.mkdir();return source,ops,out
class PlanContracts(Base):
 def test_01_exact_three_path_plan(self):self.assertEqual(set(m.operation_plan(self.plan())),set(m.PATHS))
 def test_02_legacy_two_paths_rejected(self):
  q=self.plan();q["operations"].pop()
  with self.assertRaises(ValueError):m.operation_plan(q)
 def test_03_staged_common_fourth_path_rejected(self):
  q=self.plan();q["operations"].append(dict(repository_relative="src/ppiblocker/common.py",old=None,new=q["operations"][0]["new"]))
  with self.assertRaises(ValueError):m.operation_plan(q)
 def test_04_duplicate_destination_rejected(self):
  q=self.plan();q["operations"][2]["repository_relative"]=m.PATHS[0]
  with self.assertRaises(ValueError):m.operation_plan(q)
 def test_05_existing_helper_rejected(self):
  q=self.plan();q["operations"][1]["old"]=q["operations"][0]["old"]
  with self.assertRaises(ValueError):m.operation_plan(q)
 def test_06_absent_old_rfd_lock_rejected(self):
  q=self.plan();q["operations"][2]["old"]=None
  with self.assertRaises(ValueError):m.operation_plan(q)
 def test_07_old_partial_rfd_policy_rejected(self):
  q=self.plan();q["runtime_lock_policy"]="225_EXCLUDE_CACHE"
  with self.assertRaises(ValueError):m.operation_plan(q)
 def test_08_wrong_C3_identity_rejected(self):
  q=self.plan();q["expected_old_tree_sha256"]="b"*64
  with self.assertRaises(ValueError):m.operation_plan(q)
 def test_09_formal_source_change_rejected(self):
  q=self.plan();q["formal_sources_changed"]=True
  with self.assertRaises(ValueError):m.operation_plan(q)
 def test_10_incomplete_four_prerequisites_rejected(self):
  q=self.plan();q["gates"].pop("source_refresh_current")
  with self.assertRaises(ValueError):m.operation_plan(q)
 def test_11_regression_name_and_location_fixed(self):
  q=self.plan();q["regression_tests"][0]["path"]=str(self.root/"test_unknown.py")
  with self.assertRaises(ValueError):m.operation_plan(q)
 def test_12_staged_selector_suite_is_explicit(self):
  q=self.plan();q["staged_selector_test"]["path"]=str(self.root/"unknown.py")
  with self.assertRaises(ValueError):m.operation_plan(q)
 def test_13_core_default_lock_location_fixed(self):
  q=self.plan();q["original_runtime_locks"]["core"]["path"]=str(self.root/"runtime-lock-core.json")
  with self.assertRaises(ValueError):m.operation_plan(q)
class ReceiptContracts(Base):
 def contracts(self,changes=None,sources=None):
  obj=dict(status="PASS",tests=46,failures=0,errors=0,log=self.file("log.txt"))
  if sources is not None:obj["source_files"]=sources
  if changes:obj.update(changes)
  return self.file("contracts.json",json.dumps(obj))
 def test_14_actual_saved_counts_pass(self):self.assertEqual(m.saved_contracts(self.contracts(),46)["tests"],46)
 def test_15_wrong_saved_count_rejected(self):
  with self.assertRaises(ValueError):m.saved_contracts(self.contracts(dict(tests=45)),46)
 def test_16_nonzero_saved_failures_rejected(self):
  with self.assertRaises(ValueError):m.saved_contracts(self.contracts(dict(failures=1)),46)
 def test_17_nonzero_saved_errors_rejected(self):
  with self.assertRaises(ValueError):m.saved_contracts(self.contracts(dict(errors=1)),46)
 def test_18_status_only_not_actual_PASS(self):
  with self.assertRaises(ValueError):m.saved_contracts(self.contracts(dict(status="PREPARED")),46)
 def test_19_entire_tested_source_universe_pass(self):
  sources=[self.file("helper.py")];self.assertEqual(m.saved_contracts(self.contracts(sources=sources),46,sources,1)["source_files"],sources)
 def test_20_dependency_drift_rejected(self):
  source=self.file("helper.py");r=self.contracts(sources=[source]);p=Path(source["path"]);p.chmod(0o644);p.write_text("drift");p.chmod(0o444)
  with self.assertRaises(ValueError):m.saved_contracts(r,46,[source],1)
 def test_21_writable_tested_helper_rejected(self):
  source=self.file("helper.py");r=self.contracts(sources=[source]);Path(source["path"]).chmod(0o644)
  with self.assertRaises(ValueError):m.saved_contracts(r,46,[source],1)
class TransactionContracts(Base):
 def test_22_success_installs_exact_three_files(self):
  source,ops,out=self.transaction();result=m.install(source,ops,out)
  self.assertEqual(set(result["replaced_paths"]),set(m.PATHS))
  for n in m.PATHS:self.assertEqual(m.fp(m.rec(source/n)),m.fp(ops[n]["new"]))
 def test_23_pipeline_history_exact(self):
  source,ops,out=self.transaction();result=m.install(source,ops,out)
  self.assertEqual(m.fp(result["old_pipeline_archive"]),m.fp(ops[m.PATHS[0]]["old"]))
 def test_24_rfd_history_exact(self):
  source,ops,out=self.transaction();result=m.install(source,ops,out)
  self.assertEqual(m.fp(result["old_rfd_lock_archive"]),m.fp(ops[m.PATHS[2]]["old"]))
 def test_25_staged_common_never_installed(self):
  source,ops,out=self.transaction();common=source/"src/ppiblocker/common.py";common.write_text("original-selector\n");before=m.rec(common);m.install(source,ops,out)
  self.assertEqual(m.rec(common),before)
 def test_26_postcheck_failure_rolls_back(self):
  source,ops,out=self.transaction()
  def fail():raise ValueError("postcheck failed")
  with self.assertRaises(ValueError):m.install(source,ops,out,fail)
  m.current_old(source,ops);self.assertFalse((source/m.PATHS[1]).exists());self.assertTrue((out/"rollback.json").exists())
 def test_27_rollback_restores_old_modes(self):
  source,ops,out=self.transaction()
  with self.assertRaises(ValueError):m.install(source,ops,out,lambda:(_ for _ in ()).throw(ValueError("fail")))
  self.assertEqual((source/m.PATHS[0]).stat().st_mode&0o777,0o640);self.assertEqual((source/m.PATHS[2]).stat().st_mode&0o777,0o640)
 def test_28_failure_during_rfd_install_rolls_back_helper(self):
  source,ops,out=self.transaction();original=m.atomic_bytes
  def inject(p,data,mode):
   if p==source/m.PATHS[2]and data.startswith(b"new"):raise OSError("injected write failure")
   return original(p,data,mode)
  with patch.object(m,"atomic_bytes",inject):
   with self.assertRaises(OSError):m.install(source,ops,out)
  m.current_old(source,ops)
 def test_29_unknown_concurrent_pipeline_preserved(self):
  source,ops,out=self.transaction()
  def mutate(): (source/m.PATHS[0]).write_text("unknown-concurrent");raise ValueError("postcheck")
  with self.assertRaises(RuntimeError):m.install(source,ops,out,mutate)
  self.assertEqual((source/m.PATHS[0]).read_text(),"unknown-concurrent");self.assertTrue((out/"rollback_failure.json").exists())
 def test_30_changed_old_pipeline_rejected_before_archive(self):
  source,ops,out=self.transaction();(source/m.PATHS[0]).write_text("changed")
  with self.assertRaises(ValueError):m.install(source,ops,out)
  self.assertFalse((out/"old_default_exact_history").exists())
 def test_31_unexpected_helper_rejected(self):
  source,ops,out=self.transaction();(source/m.PATHS[1]).write_text("unknown")
  with self.assertRaises(ValueError):m.install(source,ops,out)
 def test_32_unknown_destination_rejected(self):
  source,ops,out=self.transaction()
  with self.assertRaises(ValueError):m.destination_path(source,"src/ppiblocker/common.py")
 def test_33_destination_symlink_rejected(self):
  source,ops,out=self.transaction();p=source/m.PATHS[0];p.unlink();p.symlink_to(Path(ops[m.PATHS[0]]["new"]["path"]))
  with self.assertRaises(ValueError):m.install(source,ops,out)
 def test_34_destination_parent_symlink_rejected(self):
  source,ops,out=self.transaction();env=source/"environment";saved=source/"saved_env";env.rename(saved);env.symlink_to(saved,target_is_directory=True)
  with self.assertRaises(ValueError):m.install(source,ops,out)
 def test_35_accepted_new_byte_mismatch_rolls_back(self):
  source,ops,out=self.transaction();ops[m.PATHS[2]]["new"]["sha256"]="b"*64
  with self.assertRaises(ValueError):m.install(source,ops,out)
  m.current_old(source,ops)
 def test_36_writable_new_source_rolls_back(self):
  source,ops,out=self.transaction();Path(ops[m.PATHS[2]]["new"]["path"]).chmod(0o644)
  with self.assertRaises(ValueError):m.install(source,ops,out)
  m.current_old(source,ops)
 def test_37_stale_temp_file_not_overwritten(self):
  source,ops,out=self.transaction();p=source/m.PATHS[1];temp=p.with_name(p.name+".integration-"+os.environ.get("SLURM_JOB_ID","fixture")+".tmp");temp.write_text("unknown-temp")
  with self.assertRaises(FileExistsError):m.install(source,ops,out)
  self.assertEqual(temp.read_text(),"unknown-temp");m.current_old(source,ops)
 def test_38_journal_written_before_postchecks(self):
  source,ops,out=self.transaction()
  def check():self.assertTrue((out/"transaction_journal.json").exists());return{"actual":"checked"}
  self.assertEqual(m.install(source,ops,out,check)["postchecks"],{"actual":"checked"})
 def test_39_archive_readonly(self):
  source,ops,out=self.transaction();result=m.install(source,ops,out)
  for key in ("old_pipeline_archive","old_rfd_lock_archive"):self.assertFalse(Path(result[key]["path"]).stat().st_mode&0o222)
 def test_40_transaction_owned_new_helper_removed_on_rollback(self):
  source,ops,out=self.transaction()
  with self.assertRaises(ValueError):m.install(source,ops,out,lambda:(_ for _ in ()).throw(ValueError("failed")))
  self.assertFalse((source/m.PATHS[1]).exists())
 def test_41_core_and_boltz_lock_bytes_untouched(self):
  source,ops,out=self.transaction();extra={}
  for c in ("core","boltz"):
   p=source/"environment"/("runtime-lock-"+c+".json");p.write_text(c);extra[c]=m.rec(p)
  m.install(source,ops,out)
  for r in extra.values():self.assertEqual(m.rec(r["path"]),r)
 def test_42_rollback_keeps_unknown_new_helper(self):
  source,ops,out=self.transaction()
  def mutate():(source/m.PATHS[1]).write_text("unknown");raise ValueError("failed")
  with self.assertRaises(RuntimeError):m.install(source,ops,out,mutate)
  self.assertEqual((source/m.PATHS[1]).read_text(),"unknown")
 def test_43_all_checks_see_installed_complete_set(self):
  source,ops,out=self.transaction()
  def check():
   for n in m.PATHS:self.assertEqual(m.fp(m.rec(source/n)),m.fp(ops[n]["new"]))
   return{"complete":True}
  self.assertTrue(m.install(source,ops,out,check)["postchecks"]["complete"])
 def test_44_unknown_missing_old_destination_is_not_recreated(self):
  source,ops,out=self.transaction()
  def mutate():(source/m.PATHS[0]).unlink();raise ValueError("failed")
  with self.assertRaises(RuntimeError):m.install(source,ops,out,mutate)
  self.assertFalse((source/m.PATHS[0]).exists())
class DerivedStructuredContracts(Base):
 def fixture(self):
  names=("patch_generic_design.py","test_generic_design.py","qualify_generic_design_cpu.py","generic_design_cpu.sbatch","HANDOFF.md");sources=[self.file("derived_package/"+n)for n in names];manifest=self.file("derived_manifest.json",json.dumps({"synthetic_only":True}));suites=[]
  for name,count in (("owned_design_validation",50),("owned_source_dependencies",12),("generic_seven",7),("staged_physical",25),("staged_resource",9),("staged_design",8),("staged_selector",15),("default_physical",25)):
   row=dict(suite=name,returncode=0,tests=count,failures=0,errors=0,skipped=0,stdout=self.file("logs/"+name+".stdout",""if name in {"owned_design_validation","owned_source_dependencies","generic_seven"}else"Ran "+str(count)+" tests\n"),stderr=self.file("logs/"+name+".stderr",""))
   if name in {"owned_design_validation","owned_source_dependencies","generic_seven"}:row["junit"]=self.file("logs/"+name+".xml",'<testsuites><testsuite tests="'+str(count)+'" failures="0" errors="0" skipped="0"/></testsuites>')
   suites.append(row)
  c=dict(status="PASS",owned_tests=50,owned_dependency_tests=12,source_dependency_count=1,compiled_named_regression_dependencies=True,source_dependencies_readback_before_and_after_tests=True,generic_regression_file_count=7,staged_physical_suite_tests=57,default_physical_suite_tests=25,models_called=False,compiled_owned_and_derived=True,bash_syntax=True,source_files=sources,derived_source_manifest=manifest,suites=suites)
  return c,sources,manifest
 def run_contract(self,c,sources,manifest):return m.derived_contracts(self.file("structured_contracts.json",json.dumps(c)),sources,manifest)
 def test_45_actual_eight_structured_suites_pass_without_fake_aggregate(self):
  c,sources,manifest=self.fixture();self.assertNotIn("tests",c);self.assertEqual(len(self.run_contract(c,sources,manifest)["suites"]),8)
 def test_46_missing_selector_suite_rejected(self):
  c,sources,manifest=self.fixture();c["suites"].pop(6)
  with self.assertRaises(ValueError):self.run_contract(c,sources,manifest)
 def test_47_wrong_owned_50_count_rejected(self):
  c,sources,manifest=self.fixture();c["owned_tests"]=49
  with self.assertRaises(ValueError):self.run_contract(c,sources,manifest)
 def test_48_skipped_generic_suite_rejected(self):
  c,sources,manifest=self.fixture();c["suites"][2]["skipped"]=1
  with self.assertRaises(ValueError):self.run_contract(c,sources,manifest)
 def test_49_wrong_source_manifest_rejected(self):
  c,sources,manifest=self.fixture();c["derived_source_manifest"]=self.file("other_manifest.json")
  with self.assertRaises(ValueError):self.run_contract(c,sources,manifest)
 def test_50_owned_source_drift_rejected(self):
  c,sources,manifest=self.fixture();p=Path(sources[0]["path"]);p.chmod(0o644);p.write_text("drift");p.chmod(0o444)
  with self.assertRaises(ValueError):self.run_contract(c,sources,manifest)
 def test_51_actual_JUnit_count_mismatch_rejected(self):
  c,sources,manifest=self.fixture();c["suites"][2]["junit"]=self.file("other.xml",'<testsuites><testsuite tests="1"/></testsuites>')
  with self.assertRaises(ValueError):self.run_contract(c,sources,manifest)
 def test_52_tests_not_bound_to_whole_source_five_rejected(self):
  c,sources,manifest=self.fixture();c["source_files"]=sources[:-1]
  with self.assertRaises(ValueError):self.run_contract(c,sources,manifest)
 def test_53_unittest_log_count_mismatch_rejected(self):
  c,sources,manifest=self.fixture();c["suites"][3]["stdout"]=self.file("other.stdout","Ran 24 tests\n")
  with self.assertRaises(ValueError):self.run_contract(c,sources,manifest)
 def test_54_model_calls_cannot_be_software_qualification(self):
  c,sources,manifest=self.fixture();c["models_called"]=True
  with self.assertRaises(ValueError):self.run_contract(c,sources,manifest)

class ExclusiveLockContracts(Base):
 def test_55_unowned_existing_identical_lock_never_deleted(self):
  p=self.root/"existing.lock";p.write_bytes(b"same-payload");m.release_lock(p,b"same-payload",False);self.assertTrue(p.exists())
 def test_56_unknown_replaced_owned_lock_never_deleted(self):
  p=self.root/"owned.lock";p.write_bytes(b"unknown-new-owner");m.release_lock(p,b"original-owned",True);self.assertEqual(p.read_bytes(),b"unknown-new-owner")
if __name__=="__main__":unittest.main()


class ActualResourceFieldContracts(unittest.TestCase):
 def test_actual_cluster_TRES_field_supported(self):
  self.assertEqual(m.allocated_cpu_tres({"TRES":"cpu=1,node=1,billing=1"})[:2],(1,0))
 def test_AllocTRES_field_supported(self):
  self.assertEqual(m.allocated_cpu_tres({"AllocTRES":"billing=1,cpu=1,node=1"})[:2],(1,0))
 def test_two_equal_fields_supported_independent_of_order(self):
  self.assertEqual(m.allocated_cpu_tres({"TRES":"cpu=1,node=1","AllocTRES":"node=1,cpu=1"})[:2],(1,0))
 def test_conflicting_allocation_fields_rejected(self):
  with self.assertRaises(ValueError):m.allocated_cpu_tres({"TRES":"cpu=1","AllocTRES":"cpu=2"})
 def test_duplicate_cpu_rejected(self):
  with self.assertRaises(ValueError):m.allocated_cpu_tres({"TRES":"cpu=1,cpu=2"})
 def test_missing_cpu_rejected(self):
  with self.assertRaises(ValueError):m.allocated_cpu_tres({"TRES":"node=1"})
 def test_noninteger_cpu_rejected(self):
  with self.assertRaises(ValueError):m.allocated_cpu_tres({"TRES":"cpu=1.5"})
 def test_typed_or_aggregate_gpu_is_retained_for_guard(self):
  self.assertEqual(m.allocated_cpu_tres({"TRES":"cpu=1,gres/gpu:a100=1"})[1],1)
  self.assertEqual(m.allocated_cpu_tres({"TRES":"cpu=1,gres/gpu=1,gres/gpu:a100=1"})[1],1)
 def test_noninteger_gpu_rejected(self):
  with self.assertRaises(ValueError):m.allocated_cpu_tres({"TRES":"cpu=1,gres/gpu=NaN"})
 def test_absent_allocated_tres_rejected(self):
  with self.assertRaises(ValueError):m.allocated_cpu_tres({"ReqTRES":"cpu=1"})

class CurrentConsumerContracts(Base):
 def source_fixture(self):
  rows=[self.receipt(self.root/"source_v9"/n)for n in sorted(m.SOURCE_NAMES)]
  runner=sorted([r for r in rows if Path(r["path"]).suffix in {".py",".sbatch"}],key=lambda r:r["path"])
  source=dict(historical_archive_context_parent_n=2,archive_member_n=588,current_recovered_evidence_file_n=5,historical_provenance_annotation_n=9,**{k:self.receipt(self.root/(k+".json"))for k in (*m.MAP_FIELDS,"archive_member_verification")})
  sw=dict(schema="source-refresh-relative-software-acceptance.v10",status="SOURCE_REFRESH_RELATIVE_SOFTWARE_CPU_ACCEPTED_ACTUAL_SOURCE_AUDIT_PENDING",tests_expected=122,allocation={"job_id":"991"},compiled_all_python=True,bash_syntax_checked=True)
  return source,runner,sw,dict(status="PASS",tests=122,failures=0,errors=0),dict(source_receipts=rows),"991"
 def test_source_v10_whole12_runner11_saved122_positive(self):
  self.assertEqual(len(m.source_contract_shape(*self.source_fixture())),12)
 def test_prior_v8_schema_or_saved84_rejected(self):
  for index,key,value in ((2,"schema","source-refresh-relative-software-acceptance.v8"),(3,"tests",84)):
   x=list(copy.deepcopy(self.source_fixture()));x[index][key]=value
   with self.assertRaises(ValueError):m.source_contract_shape(*x)
 def test_wrong_source_job_runner_or_main_rejected(self):
  for mode in ("job","runner","main"):
   x=list(copy.deepcopy(self.source_fixture()))
   if mode=="job":x[2]["allocation"]["job_id"]="990"
   if mode=="runner":x[1].pop()
   if mode=="main":x[4]["source_receipts"][0]["path"]=str(self.root/"wrong.py")
   with self.assertRaises(ValueError):m.source_contract_shape(*x)
 def test_missing_archive_scope_or_fourth_map_rejected(self):
  for key in ("archive_member_n","archive_member_verification","archive_member_receipt_context_mapping"):
   x=list(copy.deepcopy(self.source_fixture()));x[0].pop(key)
   with self.assertRaises((ValueError,KeyError)):m.source_contract_shape(*x)
 def mapper_fixture(self):
  source=self.source_fixture()[0];base=self.receipt(self.root/"base.json");source["source_closure"]=self.receipt(self.root/"closure.json");source.update({n:self.receipt(self.root/(n+".json"))for n in ("finite_source_recovery_inputs_qualification","finite_source_alias_verification","finite_exact_source_alias_index")});source.update(exact_recovered_source_identity_n=8,exact_original_source_edge_n=12)
  rows=[self.receipt(self.root/"mapper_v4"/n)for n in sorted(m.MAPPER_NAMES)]
  ma=dict(schema="exact-current-context-mapper-acceptance.v4",status="EXACT_BBF6_RECOVERED5_NINE_ANNOTATIONS_ARCHIVE588_AND_EIGHT_SOURCE_ALIASES_MAPPER_CPU_ACCEPTED",source_files=rows,base_acceptance=base,source_closure=source["source_closure"],**{k:source[k]for k in m.MAP_FIELDS},**{k:source[k]for k in ("finite_source_recovery_inputs_qualification","finite_source_alias_verification","finite_exact_source_alias_index","exact_recovered_source_identity_n","exact_original_source_edge_n")})
  c=dict(status="PASS",tests=201,failures=0,errors=0,tested_source_files=rows,owned_python_compile_PASS=True,bash_syntax_PASS=True)
  return ma,source,base,c
 def test_mapper_v4_source14_saved201_same_four_maps_positive(self):
  self.assertEqual(len(m.mapper_binding_shape(*self.mapper_fixture())),14)
 def test_mapper_truncated_sources_or_stale_v3_rejected(self):
  for kind in ("source","schema","count"):
   x=list(copy.deepcopy(self.mapper_fixture()))
   if kind=="source":x[0]["source_files"].pop()
   if kind=="schema":x[0]["schema"]="exact-current-context-mapper-acceptance.v3"
   if kind=="count":x[3]["tests"]=132
   with self.assertRaises(ValueError):m.mapper_binding_shape(*x)
 def test_mapper_current_base_closure_or_archive_map_fork_rejected(self):
  for key in ("base_acceptance","source_closure","archive_member_receipt_context_mapping"):
   x=list(copy.deepcopy(self.mapper_fixture()));x[0][key]=self.receipt(self.root/"fork.json")
   with self.assertRaises(ValueError):m.mapper_binding_shape(*x)
class DependencySuiteContracts(DerivedStructuredContracts):
 def test_named_dependency_eighth_actual_JUnit_positive(self):
  c,s,manifest=self.fixture();self.assertEqual(self.run_contract(c,s,manifest)["owned_dependency_tests"],12)
 def test_missing_dependency_row_or_compilation_rejected(self):
  complete,s,manifest=self.fixture()
  for mode in ("row","compile","readback"):
   c=copy.deepcopy(complete)
   if mode=="row":c["suites"].pop(1)
   if mode=="compile":c["compiled_named_regression_dependencies"]=False
   if mode=="readback":c["source_dependencies_readback_before_and_after_tests"]=False
   with self.subTest(mode=mode):
    with self.assertRaises(ValueError):m.derived_contracts(self.file("structured_contracts_"+mode+".json",json.dumps(c)),s,manifest)
 def test_dependency_actual_JUnit_count_mismatch_rejected(self):
  c,s,manifest=self.fixture();c["suites"][1]["junit"]=self.file("dependency_wrong.xml",'<testsuites><testsuite tests="11" failures="0" errors="0" skipped="0"/></testsuites>')
  with self.assertRaises(ValueError):self.run_contract(c,s,manifest)
for _inherited in ("test_45_actual_eight_structured_suites_pass_without_fake_aggregate","test_46_missing_selector_suite_rejected","test_47_wrong_owned_50_count_rejected","test_48_skipped_generic_suite_rejected","test_49_wrong_source_manifest_rejected","test_50_owned_source_drift_rejected","test_51_actual_JUnit_count_mismatch_rejected","test_52_tests_not_bound_to_whole_source_five_rejected","test_53_unittest_log_count_mismatch_rejected","test_54_model_calls_cannot_be_software_qualification"):
 setattr(DependencySuiteContracts,_inherited,None)

class ActualTerminalAccountingContracts(unittest.TestCase):
 def raw(self,tres="cpu=1,node=1",state="COMPLETED",elapsed="3"):
  return "999|"+state+"|0:0|"+elapsed+"|"+tres+"|u21111210118|u21111210118|test9_source_relative_v10|organ|\n"
 def test_terminal_actual_cpu_positive_and_typed_zero_gpu_pass(self):
  with patch.object(m.subprocess,"check_output",return_value=self.raw("cpu=1,gres/gpu=0,gres/gpu:a100=0")):
   row=m.terminal("999",jobname="test9_source_relative_v10");self.assertEqual((row["allocated_CPUs"],row["allocated_GPUs"]),(1,0))
 def test_terminal_aggregate_zero_cannot_hide_typed_positive_gpu(self):
  with patch.object(m.subprocess,"check_output",return_value=self.raw("cpu=1,gres/gpu=0,gres/gpu:a100=1")),self.assertRaises(ValueError):m.terminal("999")
 def test_terminal_duplicate_or_nonnumeric_allocated_resources_rejected(self):
  for tres in ("cpu=1,cpu=1","cpu=1,gres/gpu=0,gres/gpu=0","cpu=NaN","cpu=1,gres/gpu:a100=1.5","node=1"):
   with self.subTest(tres=tres),patch.object(m.subprocess,"check_output",return_value=self.raw(tres)),self.assertRaises(ValueError):m.terminal("999")
 def test_terminal_explicit_pending_cancel_zero_cost_and_other_empty_rejected(self):
  with patch.object(m.subprocess,"check_output",return_value=self.raw("","CANCELLED","0")):
   self.assertEqual(m.terminal("999","CANCELLED")["allocated_CPUs"],0)
  for state,elapsed in (("COMPLETED","0"),("FAILED","0"),("CANCELLED","2")):
   with self.subTest(state=state),patch.object(m.subprocess,"check_output",return_value=self.raw("",state,elapsed)),self.assertRaises(ValueError):m.terminal("999",state)
  # Known13267 zero-time cancellation is unallocated only with empty actual TRES/CPU0.
  for tres,cpus in (("",0),("cpu=1",1)):
   def stub(jid,state="COMPLETED",jobname=None):
    return dict(job_id=str(jid),state=state,elapsed_seconds=0 if jid=="13267"else 2,allocated_CPUs=cpus if jid=="13267"else 1,allocated_GPUs=0,allocated_TRES=tres if jid=="13267"else"cpu=1")
   with patch.object(m,"terminal",side_effect=stub):
    if cpus==0:self.assertEqual(m.history()["13267"]["allocated_CPUs"],0)
    else:
     with self.assertRaises(ValueError):m.history()

class CurrentSourceAliasPointerContracts(unittest.TestCase):
 def case(self):
  s={n:dict(path="/synthetic/"+n,bytes=1,sha256="a"*64)for n in ("finite_source_recovery_inputs_qualification","finite_source_alias_verification","finite_exact_source_alias_index")}
  s.update(exact_recovered_source_identity_n=8,exact_original_source_edge_n=12);return s,copy.deepcopy(s)
 def test_actual_three_source_artifacts_and_denominators(self):
  s,ma=self.case();self.assertTrue(m.source_alias_pointer_shape(s,ma))
 def test_missing_source_alias_artifact_rejected(self):
  s,ma=self.case();s.pop("finite_exact_source_alias_index")
  with self.assertRaises(ValueError):m.source_alias_pointer_shape(s,ma)
 def test_source_mapper_artifact_fork_rejected(self):
  s,ma=self.case();ma["finite_source_alias_verification"]={**ma["finite_source_alias_verification"],"sha256":"b"*64}
  with self.assertRaises(ValueError):m.source_alias_pointer_shape(s,ma)
 def test_source_mapper_denominator_fork_rejected(self):
  s,ma=self.case();ma["exact_original_source_edge_n"]=11
  with self.assertRaises(ValueError):m.source_alias_pointer_shape(s,ma)
