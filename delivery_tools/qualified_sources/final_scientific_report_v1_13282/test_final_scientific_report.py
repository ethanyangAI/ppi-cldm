#!/usr/bin/env python3
"""Synthetic software contracts only; never actual scientific result acceptance."""
import importlib.util,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location("report_fixture_source",Path(__file__).parent/"final_scientific_report.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def matrix():
 ts=[dict(target_id="T"+str(i),analysis_role="primary"if i<6 else"diagnostic")for i in range(7)]
 p=dict(status="FROZEN_BEFORE_GENERATION",protocol=dict(targets=ts,scientific_scope="COMPUTATIONAL_ONLY",methods=[dict(method_id=k)for k in("rf_diffusion","bindcraft")],replicate_seeds=[1,2]),tasks=[])
 for t in ts:
  for meth in("rf_diffusion","bindcraft"):
   for seed in(1,2):p["tasks"].append(dict(target_id=t["target_id"],method_id=meth,seed=seed,task_id=str(len(p["tasks"])),array_index=len(p["tasks"])))
 flat=[dict(t,analysis_role=ts[int(t["target_id"][1:])]["analysis_role"],cohort=c,engine=e,n_requested=3 if c=="uniform_all_complete"else 2,n_selected=0,n_R1_complete=0,underfilled=True,quality_R1=None,reason="EMPTY_COHORT",model_coverage=dict(expected=0,valid=0))for t in p["tasks"]for c in m.COHORTS for e in m.ENGINES]
 return dict(schema="paired-target-statistics.v2",status="FROZEN_COMPLETE_DENOMINATOR_DESCRIPTIVE_STATISTICS_RECOMPUTED",n_cohort_engine_rows=112,rows=[{}for _ in range(56)],n_primary_targets=6,complete_matrix_macro_requires_all_six_pairs=True,missing_quality="NULL_NEVER_ZERO",scientific_scope="COMPUTATIONAL_ONLY",inference_mode="descriptive_only",posthoc_target_dropping=False,flat_cohort_engine_rows=flat),p
def comparisons():
 return dict(comparisons=[dict(engine=e,cohort=c,n_primary_targets=6,n_paired_available=0,status="FULL_MATRIX_COMPARISON_UNRESOLVED",pairs=[dict(target_id="T"+str(i),rf_quality_R1=None,bindcraft_quality_R1=None,RF_minus_BindCraft=None)for i in range(6)],RF_target_median_R1=None,BindCraft_target_median_R1=None,paired_macro_mean_RF_minus_BindCraft=None,paired_macro_median_RF_minus_BindCraft=None,inferential_p_value=None,inferential_confidence_interval=None,experimental_probability=None)for e in m.ENGINES for c in m.COHORTS])
def costfixture():
 _,p=matrix();rows=[dict(logical_id="13260_"+str(i),raw_id=str(40000+i),phase="formal_generation",submission_kind="primary",GPU_count=1,elapsed_seconds=3600,actual_GPU_seconds=3600,state="COMPLETED",result_manifest_required_for_cost=False)for i in range(28)]
 c=dict(status=m.COST,complete_root_gpu_submission_universe=True,allocated_failure_before_manifest_cost_retained=True,result_manifests_required_for_cost=False,whole_historical_project_cost_claim=False,actual_GPU_seconds=100800,allocated_failure_GPU_seconds=0)
 return c,dict(rows=rows,actual_GPU_seconds=100800,allocated_failure_GPU_seconds=0),p
def structures():
 jobs=[];targets=[];controls=[]
 for i in range(7):
  bid="B"+str(i);tid="T"+str(i);controls.append(dict(blind_id=bid,target_id=tid));targets.append(dict(target_id=tid,family="F",synthetic=i==6,reference_complex=dict(path="/reference.pdb",bytes=1,sha256="a"*64)))
  for e in m.ENGINES:
   for v in(["primary","single_sensitivity"]if e=="boltz"and i<6 else["primary"]):
    slots=[dict(seed=31011+j,model=0)for j in range(3)]if e=="boltz"else[dict(seed=31021,model=j)for j in range(1,6)]
    jobs.append(dict(job_key=bid+e+v,blind_id=bid,target_id=tid,engine=e,variant=v,slots=slots))
 scored=[];physical=[]
 for j in jobs:
  models=[]
  for slot in j["slots"]:
   models.append(dict(slot=slot,status="MODEL_UNRESOLVED",R0=None,R1=None,reason="SYNTHETIC_MISSING"))
   physical.append(dict(job_key=j["job_key"],slot=slot,source_qualification="PASSED_CURRENT_WORKER_SOURCE_OWNERSHIP_AND_SLOT_LINEAGE",confidence_content_status="MODEL_UNRESOLVED",minimum_distance_A=None,severe_lt_1p5_A=None,raw_PDB=None,status="INTRINSIC_COORDINATE_DIAGNOSTIC_TYPED_UNRESOLVED",reason="SYNTHETIC_MISSING"))
  scored.append(dict(job_key=j["job_key"],models=models))
 phy=dict(rows=physical,expected_models=74,status="ALL_FIXED_COMMON_MODEL_INTRINSIC_DIAGNOSTICS_RECORDED",experimental_binding_or_blockade=False,policy=dict(severe_flag_cutoff_A=1.5,severe_flag_operator="<",ranking_or_filter_changes=False,formal_primary_R1_changes=False))
 return dict(results=scored,models_expected=74),dict(jobs=jobs),dict(targets=targets),dict(controls=controls,members=[]),phy
class Contracts(unittest.TestCase):
 def rejected_matrix(self,change):
  s,p=matrix();change(s)
  with self.assertRaises(ValueError):m.fixed_matrix(s,p)
 def test_all112_empty_rows_kept_null(self):
  s,p=matrix();self.assertEqual(len(m.fixed_matrix(s,p)),112);self.assertTrue(all(r["quality_R1"]is None for r in s["flat_cohort_engine_rows"]))
 def test_missing_matrix_row_rejected(self):self.rejected_matrix(lambda s:s["flat_cohort_engine_rows"].pop())
 def test_duplicate_matrix_row_rejected(self):self.rejected_matrix(lambda s:s["flat_cohort_engine_rows"].__setitem__(-1,s["flat_cohort_engine_rows"][0]))
 def test_diagnostic_relabel_rejected(self):self.rejected_matrix(lambda s:s["flat_cohort_engine_rows"][-1].update(analysis_role="primary"))
 def test_empty_quality_zero_rejected(self):self.rejected_matrix(lambda s:s["flat_cohort_engine_rows"][0].update(quality_R1=0))
 def test_underfilled_claim_rejected(self):self.rejected_matrix(lambda s:s["flat_cohort_engine_rows"][0].update(underfilled=False))
 def test_wrong_model_denominator_rejected(self):self.rejected_matrix(lambda s:s["flat_cohort_engine_rows"][0]["model_coverage"].update(expected=3))
 def test_nonfinite_quality_rejected(self):self.rejected_matrix(lambda s:s["flat_cohort_engine_rows"][0].update(n_selected=1,n_R1_complete=1,quality_R1=float("nan"),reason=None,model_coverage=dict(expected=3,valid=3)))
 def test_unfrozen_generation_seed_rejected(self):self.rejected_matrix(lambda s:s["flat_cohort_engine_rows"][0].update(seed=3))
 def test_null_missing_reason_rejected(self):self.rejected_matrix(lambda s:s["flat_cohort_engine_rows"][0].update(n_selected=1,n_R1_complete=0,reason="EMPTY_COHORT",model_coverage=dict(expected=3,valid=0)))
 def test_four_comparison_axes_retained(self):self.assertEqual(len(m.comparison_rules(comparisons())),4)
 def test_partial_pair_macro_not_zero(self):
  s=comparisons();s["comparisons"][0]["paired_macro_mean_RF_minus_BindCraft"]=0
  with self.assertRaises(ValueError):m.comparison_rules(s)
 def test_dropped_sixth_target_rejected(self):
  s=comparisons();s["comparisons"][0]["pairs"].pop()
  with self.assertRaises(ValueError):m.comparison_rules(s)
 def test_p_value_invention_rejected(self):
  s=comparisons();s["comparisons"][0]["inferential_p_value"]=.04
  with self.assertRaises(ValueError):m.comparison_rules(s)
 def test_direction_swap_rejected(self):
  s=comparisons();r=s["comparisons"][0];r["pairs"][0].update(rf_quality_R1=.8,bindcraft_quality_R1=.2,RF_minus_BindCraft=-.6);r["n_paired_available"]=1
  with self.assertRaises(ValueError):m.comparison_rules(s)
 def test_all_primary28_actual_costs(self):
  c,t,p=costfixture();primary,rows=m.costs(c,t,p);self.assertEqual(len(primary),28);self.assertEqual(sum(r["actual_GPU_seconds"]for r in rows),100800)
 def test_failure_before_manifest_positive_cost_retained(self):
  c,t,p=costfixture();t["rows"][0]["state"]="FAILED";c["allocated_failure_GPU_seconds"]=t["allocated_failure_GPU_seconds"]=3600
  self.assertEqual(m.costs(c,t,p)[0][0]["actual_GPU_seconds"],3600)
 def test_omitted_failure_cost_rejected(self):
  c,t,p=costfixture();t["rows"][0]["state"]="FAILED"
  with self.assertRaises(ValueError):m.costs(c,t,p)
 def test_duplicate_raw_allocation_rejected(self):
  c,t,p=costfixture();t["rows"][1]["raw_id"]=t["rows"][0]["raw_id"]
  with self.assertRaises(ValueError):m.costs(c,t,p)
 def test_gpu_missing_not_zero(self):
  c,t,p=costfixture();t["rows"][0]["GPU_count"]=None
  with self.assertRaises(ValueError):m.costs(c,t,p)
 def test_zero_cancel_kept_separate(self):
  c,t,p=costfixture();t["rows"][0].update(GPU_count=0,elapsed_seconds=0,actual_GPU_seconds=0,state="CANCELLED",allocation_kind="ZERO_UNALLOCATED_CANCEL");c["actual_GPU_seconds"]=t["actual_GPU_seconds"]=97200
  self.assertEqual(m.costs(c,t,p)[0][0]["actual_GPU_seconds"],0)
 def test_whole_historical_cost_claim_rejected(self):
  c,t,p=costfixture();c["whole_historical_project_cost_claim"]=True
  with self.assertRaises(ValueError):m.costs(c,t,p)
 def test_raw_id_equal_array_master_leaf_retained(self):
  c,t,p=costfixture();t["rows"][-1]["raw_id"]="13260";self.assertEqual(len(m.costs(c,t,p)[1]),28)
 def test_native20_74_missing_slots_retained(self):
  rows=m.structure_rows(*structures());self.assertEqual(len(rows),74);self.assertTrue(all(r["raw_PDB"]is None and r["R1"]is None for r in rows))
 def test_native14_includes_unresolved_models(self):
  s,i,a,mem,p=structures();b=dict(structures=m.structure_rows(s,i,a,mem,p),membership=mem,request=dict(common_successor={}))
  rows=m.native_rows(b);self.assertEqual(len(rows),14);self.assertTrue(all(r["R1_median"]is None for r in rows))
 def test_lost_physical_slot_rejected(self):
  s,i,a,mem,p=structures();p["rows"].pop()
  with self.assertRaises(ValueError):m.structure_rows(s,i,a,mem,p)
 def test_duplicate_score_slot_rejected(self):
  s,i,a,mem,p=structures();s["results"][0]["models"][1]=s["results"][0]["models"][0]
  with self.assertRaises(ValueError):m.structure_rows(s,i,a,mem,p)
 def test_unqualified_valid_confidence_rejected(self):
  s,i,a,mem,p=structures();s["results"][0]["models"][0]["status"]="VALID";p["rows"][0].update(source_qualification="UNRESOLVED_WORKER_LINEAGE_COORDINATES_ONLY",confidence_content_status="VALID")
  with self.assertRaises(ValueError):m.structure_rows(s,i,a,mem,p)
 def test_boundary_1p5_not_severe(self):
  s,i,a,mem,p=structures();p["rows"][0].update(minimum_distance_A=1.5,severe_lt_1p5_A=False);self.assertFalse(m.structure_rows(s,i,a,mem,p)[0]["severe_lt_1p5_A"])
 def test_strict_distance_flag_mismatch_rejected(self):
  s,i,a,mem,p=structures();p["rows"][0].update(minimum_distance_A=1.49,severe_lt_1p5_A=False)
  with self.assertRaises(ValueError):m.structure_rows(s,i,a,mem,p)
 def test_changed_physical_cutoff_rejected(self):
  s,i,a,mem,p=structures();p["policy"]["severe_flag_cutoff_A"]=2.5
  with self.assertRaises(ValueError):m.structure_rows(s,i,a,mem,p)
 def test_complete_median_missing_stays_null(self):self.assertIsNone(m.median_complete([.8,None,.7],3))
 def test_tsv_null_zero_distinct(self):self.assertEqual(m.tsv([dict(a=None,b=0,c=False)],("a","b","c")),"a\tb\tc\nNULL\t0\tfalse\n")
 def test_actual_old_new_cpu_records(self):
  base="JobId=19000 JobState=RUNNING UserId=u21111210118(1) Account=u21111210118 Partition=organ NumCPUs=2 "
  for tres in("TRES=cpu=2,node=1","AllocTRES=cpu=2,node=1"):self.assertEqual(m.cpu_record(base+tres,"19000")["allocated_GPUs"],0)
 def test_cpu_gpu_missing_tres_rejected(self):
  base="JobId=19000 JobState=RUNNING UserId=u21111210118(1) Account=u21111210118 Partition=organ NumCPUs=2 "
  for tres in("","TRES=","TRES=cpu=2,gres/gpu=1","TRES=cpu=3","TRES=cpu=2,node=1 AllocTRES=cpu=2,node=2"):
   with self.assertRaises(ValueError):m.cpu_record(base+tres,"19000")
 def test_real_receipt_drift_symlink_readonly(self):
  parent=m.R/"steps/24_benchmark_delivery/tmp";parent.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(dir=parent,prefix="final-report-contract-")as d:
   p=Path(d)/"e.json";p.write_bytes(b"fixture");p.chmod(0o444);r=m.rec(p);self.assertEqual(m.verify(r,True),p);p.chmod(0o644)
   with self.assertRaises(ValueError):m.verify(r,True)
   p.write_bytes(b"changed");p.chmod(0o444)
   with self.assertRaises(ValueError):m.verify(r)
   link=Path(d)/"link.json";link.symlink_to(p)
   with self.assertRaises(ValueError):m.rec(link)
def bundle_fixture():
 stats,plan=matrix();s,i,a,mem,p=structures();cost,terminal,_=costfixture()
 plan["protocol"].update(budget_gpu_seconds=3600,sampling=dict(uniform_n_per_replicate=3,native_top_k_per_replicate=2))
 stats.update(n_empty_cohort_engine_rows=112,n_missing_selected_outcome_rows=0,comparisons=comparisons()["comparisons"],rows=[dict(target_id=t["target_id"],analysis_role=t["analysis_role"],method_id=meth,engine=eng,cohort=coh,quality_R1=None,status="TARGET_QUALITY_NOT_ESTIMABLE")for t in plan["protocol"]["targets"]for meth in("rf_diffusion","bindcraft")for eng in m.ENGINES for coh in m.COHORTS])
 for r in stats["flat_cohort_engine_rows"]:r.update(candidate_R0_summary=None,candidate_R1_summary=None)
 receipt=dict(path=str(m.R/"synthetic-only.json"),bytes=0,sha256="a"*64)
 formal=formal_fixture(stats["flat_cohort_engine_rows"]);formalrows=m.formal_matrix_rows(formal,stats["flat_cohort_engine_rows"])
 return dict(formal=formal,formalrows=formalrows,stats=stats,flat=stats["flat_cohort_engine_rows"],plan=plan,analysis=a,membership=mem,structures=m.structure_rows(s,i,a,mem,p),cost=cost,costrows=terminal["rows"],primary_costs=m.costs(cost,terminal,plan)[0],common=dict(statistics=receipt),request=dict(common_successor=receipt,root_gpu_cost=receipt),comparisons=m.comparison_rules(stats))
class AdditionalContracts(unittest.TestCase):
 def test_nonempty_complete_candidate_quality_accepted(self):
  s,p=matrix();s["flat_cohort_engine_rows"][0].update(n_selected=1,n_R1_complete=1,quality_R1=.7,reason=None,model_coverage=dict(expected=3,valid=3));self.assertEqual(m.fixed_matrix(s,p)[0]["quality_R1"],.7)
 def test_partial_selected_outcome_null_accepted(self):
  s,p=matrix();s["flat_cohort_engine_rows"][0].update(n_selected=2,n_R1_complete=1,quality_R1=None,reason="MISSING_PRESELECTED_CANDIDATE_OUTCOME",model_coverage=dict(expected=6,valid=3));self.assertIsNone(m.fixed_matrix(s,p)[0]["quality_R1"])
 def test_complete_six_pair_macro_accepted(self):
  s=comparisons()
  for r in s["comparisons"]:
   for pair in r["pairs"]:pair.update(rf_quality_R1=.8,bindcraft_quality_R1=.4,RF_minus_BindCraft=.4)
   r.update(n_paired_available=6,status="COMPLETE_SIX_TARGET_DESCRIPTIVE_COMPARISON",RF_target_median_R1=.8,BindCraft_target_median_R1=.4,paired_macro_mean_RF_minus_BindCraft=.4,paired_macro_median_RF_minus_BindCraft=.4)
  self.assertEqual(m.comparison_rules(s)[0]["n_paired_available"],6)
 def test_valid_PDB_confidence_source_mismatch_rejected(self):
  s,i,a,mem,p=structures();s["results"][0]["models"][0].update(status="VALID",raw_files=[dict(path="/scored.pdb")]);p["rows"][0].update(confidence_content_status="VALID",raw_PDB=dict(path="/different.pdb"))
  with self.assertRaises(ValueError):m.structure_rows(s,i,a,mem,p)
 def test_no_interface_null_R1_preserved(self):
  s,i,a,mem,p=structures();rr=dict(path="/no-interface.pdb")
  s["results"][0]["models"][0].update(status="NO_INTERFACE",raw_files=[rr]);p["rows"][0].update(confidence_content_status="NO_INTERFACE",raw_PDB=rr)
  r=m.structure_rows(s,i,a,mem,p)[0];self.assertEqual(r["confidence_status"],"NO_INTERFACE");self.assertIsNone(r["R1"])
 def test_changed_confidence_units_rejected(self):
  s,i,a,mem,p=structures();s["results"][0]["models"][0]["binder_plddt_fraction"]=80
  with self.assertRaises(ValueError):m.structure_rows(s,i,a,mem,p)
 def test_report_full56_native14_and_source_links(self):
  b=bundle_fixture();text=m.render_report(b,m.native_rows(b));self.assertIn("全部 112 行",text);self.assertEqual(len(b["stats"]["rows"]),56);self.assertEqual(len(m.native_rows(b)),14);self.assertIn(m.PLAN["path"],text);self.assertIn("新家族仍 UNVALIDATED",text);self.assertIn("实验结合或阻断验证：未完成",text)
 def test_report_positive_failure_cost_rendered(self):
  b=bundle_fixture();b["costrows"][0]["state"]="FAILED";b["cost"]["allocated_failure_GPU_seconds"]=3600
  text=m.render_report(b,m.native_rows(b));self.assertIn("formal_generation|primary|28|28|0|100800|3600",text)
 def artifacts(self):
  parent=m.R/"steps/24_benchmark_delivery/tmp";parent.mkdir(parents=True,exist_ok=True);t=tempfile.TemporaryDirectory(dir=parent,prefix="report-artifact-contract-");root=Path(t.name);b=bundle_fixture();texts,_=m.expected_artifacts(b)
  artifacts={n:m.write(root/n,v)for n,v in texts.items()};artifacts["structure_inventory.json"]=m.dump(root/"structure_inventory.json",dict(schema="all-fixed-structure-inventory.v1",rows=b["structures"],expected_models=74,experimental_binding_or_blockade=False))
  return t,root,b,texts,artifacts
 def test_actual_written_report_artifacts_pass(self):
  t,root,b,texts,artifacts=self.artifacts()
  try:self.assertTrue(m.verify_artifact_contents(artifacts,texts,b["structures"]))
  finally:t.cleanup()
 def test_changed_matrix_with_new_receipt_rejected(self):
  t,root,b,texts,artifacts=self.artifacts()
  try:
   p=root/"matrix112.tsv";p.chmod(0o644);p.write_text(texts["matrix112.tsv"].replace("NULL","0",1));p.chmod(0o444);artifacts["matrix112.tsv"]=m.rec(p)
   with self.assertRaises(ValueError):m.verify_artifact_contents(artifacts,texts,b["structures"])
  finally:t.cleanup()
 def test_lost_structure_slot_with_new_receipt_rejected(self):
  t,root,b,texts,artifacts=self.artifacts()
  try:
   p=root/"structure_inventory.json";p.chmod(0o644);p.unlink();artifacts[p.name]=m.dump(p,dict(schema="all-fixed-structure-inventory.v1",rows=b["structures"][:-1],expected_models=73,experimental_binding_or_blockade=False))
   with self.assertRaises(ValueError):m.verify_artifact_contents(artifacts,texts,b["structures"])
  finally:t.cleanup()
 def test_extra_unreviewed_artifact_rejected(self):
  t,root,b,texts,artifacts=self.artifacts()
  try:
   artifacts["unexpected.tsv"]=m.write(root/"unexpected.tsv","unexpected")
   with self.assertRaises(ValueError):m.verify_artifact_contents(artifacts,texts,b["structures"])
  finally:t.cleanup()

def formal_fixture(flat):
 rows=[dict(r,generation_status="ACCEPTED_FULL_BUDGET",n_unique_complete_pool=0,n_native_score_missing=0,n_R0_observed_pass=0,n_R0_unresolved=0,sample_R0_pass_fraction=None,observed_fixed_cohort_R0_per_GPU_hour=0,allocated_gpu_seconds=3600,operational_pass=None,experimental_probability=None)for r in flat]
 return dict(rows=rows,n_accepted_full_budget_tasks=28,complete_generation_matrix=True)
class FormalRowsContracts(unittest.TestCase):
 def test_actual_formal112_generation_status_join(self):
  s,p=matrix();f=formal_fixture(s["flat_cohort_engine_rows"]);self.assertEqual(len(m.formal_matrix_rows(f,s["flat_cohort_engine_rows"])),112)
 def test_failed_generation_is_typed_unresolved(self):
  s,p=matrix();f=formal_fixture(s["flat_cohort_engine_rows"])
  for r in f["rows"][:4]:r.update(generation_status="ENGINEERING_FAILED",reason="GENERATION_UNRESOLVED_NO_FULL_BUDGET",allocated_gpu_seconds=None)
  f.update(n_accepted_full_budget_tasks=27,complete_generation_matrix=False)
  self.assertEqual(len(m.formal_matrix_rows(f,s["flat_cohort_engine_rows"])),112)
 def test_full_budget_false_claim_rejected(self):
  s,p=matrix();f=formal_fixture(s["flat_cohort_engine_rows"]);f["n_accepted_full_budget_tasks"]=27
  with self.assertRaises(ValueError):m.formal_matrix_rows(f,s["flat_cohort_engine_rows"])
 def test_failed_generation_wrong_empty_reason_rejected(self):
  s,p=matrix();f=formal_fixture(s["flat_cohort_engine_rows"])
  for r in f["rows"][:4]:r.update(generation_status="ENGINEERING_FAILED",allocated_gpu_seconds=None)
  f.update(n_accepted_full_budget_tasks=27,complete_generation_matrix=False)
  with self.assertRaises(ValueError):m.formal_matrix_rows(f,s["flat_cohort_engine_rows"])

class UnresolvedLineageContracts(unittest.TestCase):
 def test_unqualified_missing_worker_retains_typed_nulls_and_coordinates(self):
  s,i,a,mem,p=structures();p["rows"][0].update(source_qualification="UNRESOLVED_WORKER_LINEAGE_COORDINATES_ONLY",minimum_distance_A=1.2,severe_lt_1p5_A=True,raw_PDB=dict(path="/unqualified.pdb"),status="INTRINSIC_HEAVY_ATOM_COORDINATE_DIAGNOSTIC_OBSERVED")
  r=m.structure_rows(s,i,a,mem,p)[0];self.assertEqual(r["confidence_status"],"MODEL_UNRESOLVED");self.assertIsNone(r["R0"]);self.assertIsNone(r["R1"]);self.assertEqual(r["minimum_distance_A"],1.2);self.assertFalse(r["experimental_binding_or_blockade"])
 def test_unqualified_no_interface_still_rejected(self):
  s,i,a,mem,p=structures();s["results"][0]["models"][0]["status"]="NO_INTERFACE";p["rows"][0].update(source_qualification="UNRESOLVED_WORKER_LINEAGE_COORDINATES_ONLY",confidence_content_status="NO_INTERFACE")
  with self.assertRaises(ValueError):m.structure_rows(s,i,a,mem,p)

if __name__=="__main__":unittest.main()
