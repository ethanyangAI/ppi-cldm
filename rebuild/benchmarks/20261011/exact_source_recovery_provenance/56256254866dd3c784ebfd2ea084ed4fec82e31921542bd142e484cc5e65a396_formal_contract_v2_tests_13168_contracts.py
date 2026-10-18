#!/usr/bin/env python3
"""Meaningful CPU contracts for fixed denominators, missingness, and raw all-sequence closure."""
import ast,copy,hashlib,importlib.util,json,os,sys,tempfile,unittest
from unittest import mock
from pathlib import Path
import formal_benchmark_contract as f
def protocol():
 return {"schema":"paired-budget-v1","protocol_id":"PPI-PAIRED-BENCHMARK-20261011","scientific_scope":"COMPUTATIONAL_ONLY",
 "execution_mode":"persistent_session","replicate_seeds":[21011,21012],"binder_length":65,"gpu_count":1,"budget_gpu_seconds":3600,
 "shutdown_reserve_seconds":10,"accounting_tolerance_seconds":2,"hardware":{"gpu_name":"NVIDIA A100-PCIE-40GB","minimum_memory_mib":40000},
 "sampling":{"salt":"PPI-PAIRED-20261011-FIXED-BEFORE-GENERATION","uniform_n_per_replicate":3,"native_top_k_per_replicate":2},
 "aggregation_policy":f.POLICY,"completion_policy":{"allowed_scheduler_states":["COMPLETED","TIMEOUT"],"requires_durable_receipt_and_complete_raw_ledger":True,"generation_cutoff_wall_seconds":3590,"all_gpu_children_terminated_before_receipt":True,"actual_gpu_seconds":3600,"tolerance_seconds":2,"engineering_failure_is_comparable":False},"inference":{"mode":"descriptive_only","minimum_targets":6},
 "common_review_gate":{"score":"R0","threshold":1.0,"operator":">=","aggregation":"all_required_models_median","scope":"COMPUTATIONAL_ONLY"},
 "common_review_primary":{"engine":"boltz","models":3,"seeds":[31011,31012,31013],"endpoint":"R1_official_ipSAE_10A_max_continuous","operational_pass":None},
 "common_review_secondary":{"engine":"af2","models":5,"seed":31021,"model_order":[1,2,3,4,5],"endpoint":"separate_R1_R0","pooled_with_primary":False},
 "targets":[{"target_id":tid,"analysis_role":"primary"if tid in f.PRIMARY else"diagnostic"}for tid in sorted(f.PRIMARY|f.DIAGNOSTIC)],
 "methods":[{"method_id":m}for m in f.METHODS]}
def fixture():
 p=protocol();tasks=f.task_matrix(p);plan={"protocol":p,"tasks":tasks};alloc=[];coverage=[]
 for i,t in enumerate(tasks):
  rr={"path":"/software_fixture/"+str(i),"bytes":1,"sha256":str(i)}
  row={"task":t,"raw_allocation_id":str(50001+i),"run_receipt":rr,"scheduler_allocation":{"raw_allocation_id":str(50001+i),"gpu_count":1,"elapsed_seconds":3600,"state":"COMPLETED"},
    "allocated_gpu_seconds":3600,"status":"BUDGET_EXHAUSTED_WITH_EXPLICIT_BOUNDARY_CENSORING","comparable_full_budget":True,
    "hardware":{"gpus":[{"name":"NVIDIA A100-PCIE-40GB","memory_total_mib":40960}]},"attempt_status_counts":{"COMPLETED":0,"SCIENTIFIC_REJECT":1,"ENGINEERING_FAILURE":0,"INTERRUPTED":0}}
  alloc.append(row);coverage.append({"task":t,"primary_run_receipt":rr,"comparison_status":"ACCEPTED_FULL_BUDGET","n_unique_complete":0,"n_native_score_available":0,"n_native_score_missing":0,
   "uniform_all_complete":{"requested":3,"selected":0,"underfilled":True},"native_fixed_top_k":{"requested":2,"selected":0,"underfilled":True}})
 account={"tasks":alloc,"allocated_gpu_seconds_all_attempts":100800};cohorts={"coverage":coverage,"selected":[]}
 independent={"status":"INDEPENDENT_BUDGET_LEDGER_AND_COHORT_AUDIT_PASS","expected_tasks":28,"full_budget_comparable_tasks":28,"complete_generation_matrix":True,"all_allocated_gpu_seconds":100800}
 common={"cohort_summaries":[],"outcomes":{"boltz":[],"af2":[]}}
 return p,plan,account,cohorts,independent,common
def member(t):
 seq="A"*65
 return dict(task_id=t["task_id"],target_id=t["target_id"],method_id=t["method_id"],seed=t["seed"],cohort=f.COHORTS[0],sequence=seq,sequence_sha256=hashlib.sha256(seq.encode()).hexdigest(),cohort_record_id="software_member_1")
def one_selected():
 p,plan,ac,co,ind,common=fixture();m=member(plan["tasks"][0]);m["primary_run_receipt"]=co["coverage"][0]["primary_run_receipt"];co["selected"].append(m)
 cov=co["coverage"][0];cov.update(n_unique_complete=1,n_native_score_missing=1);cov[f.COHORTS[0]]={"requested":3,"selected":1,"underfilled":True}
 for eng,n in f.ENGINES.items():
  common["cohort_summaries"].append(dict(target_id=m["target_id"],method_id=m["method_id"],seed=m["seed"],cohort=m["cohort"],engine=eng,
   n_selected=1,n_R1_complete=1,R1_candidates=dict(n_expected=1,n_valid=1,median=.3),R0_candidates=dict(n_expected=1,n_valid=1,median=1.1),
   model_coverage=dict(expected=n,valid=n),operational_pass=None))
  common["outcomes"][eng].append(dict(cohort_record_id=m["cohort_record_id"],evaluable=True,**{"pass":True}))
 return p,plan,ac,co,ind,common
def raw_fixture():
 t=f.task_matrix(protocol())[0];run={"task":t,"attempt_count":1,"generation_cutoff_epoch":100.}
 a={"attempt_index":0,"status":"SCIENTIFIC_REJECT","complete_sequence_records":2,"precutoff_sequence_records":2,"screening_update_records":1,"precutoff_screening_update_records":1}
 seq="A"*65;ev=[]
 for i in range(2):ev.append(dict(task_id=t["task_id"],target_id=t["target_id"],method_id=t["method_id"],seed=t["seed"],attempt_index=0,sequence_record_id=str(i),sequence=seq,
 sequence_sha256=hashlib.sha256(seq.encode()).hexdigest(),observed_before_generation_cutoff=True,observed_at_epoch=90.,internal_acceptance=False if i==0 else None,native_score=None))
 upd=[dict(task_id=t["task_id"],attempt_index=0,sequence_record_id="0",source_line_number=1,observed_before_generation_cutoff=True,observed_at_epoch=95.,internal_acceptance=False,native_score=.8)]
 return run,[a],ev,upd
class FormalContracts(unittest.TestCase):
 def test_exact_protocol28_matrix(self):
  p,pl,*_=fixture();f.formal_protocol(p);self.assertEqual(len(pl["tasks"]),28);self.assertEqual(len({x["task_id"]for x in pl["tasks"]}),28)
 def test_early_engineering_count_cap_forbidden(self):
  p=protocol();p["max_attempts_safety_limit"]=1
  with self.assertRaisesRegex(ValueError,"max-attempt"):f.formal_protocol(p)
 def test_duplicate_target_ids_even_correct_role_counts_rejected(self):
  p=protocol();p["targets"][1]["target_id"]=p["targets"][0]["target_id"]
  with self.assertRaisesRegex(ValueError,"Duplicate target"):f.formal_protocol(p)
 def test_primary_diagnostic_exact_identity(self):
  p=protocol();p["targets"][0]["analysis_role"]="primary"
  with self.assertRaisesRegex(ValueError,"role"):f.formal_protocol(p)
 def test_wrong_budget_or_seed_salt_rejected(self):
  for k,v in (("budget_gpu_seconds",3590),("replicate_seeds",[21011,21013]),("binder_length",64)):
   p=protocol();p[k]=v
   with self.assertRaises(ValueError):f.formal_protocol(p)
 def test_empty28_tasks112_rows_null_quality_observed_zero(self):
  p,pl,a,c,i,cm=fixture();f.generation_matrix(pl,a,c,i);rows=f.explicit_evaluation_rows(p,c["coverage"],c["selected"],cm)
  self.assertEqual(len(rows),112);self.assertTrue(all(r["quality_R1"]is None and r["reason"]=="EMPTY_COHORT"and r["observed_fixed_cohort_R0_per_GPU_hour"]==0 for r in rows))
  self.assertTrue(all(x["paired_macro_mean_RF_minus_BindCraft"]is None for x in f.independent_target_aggregation(rows)))
 def test_engineering_short_use_not_comparable_preserves_cost(self):
  p,pl,a,c,i,cm=fixture();r=a["tasks"][0];r.update(status="EARLY_ENGINEERING_FAILURE",allocated_gpu_seconds=17,comparable_full_budget=False)
  r["scheduler_allocation"].update(elapsed_seconds=17,state="FAILED");r["attempt_status_counts"]["ENGINEERING_FAILURE"]=1
  cov=c["coverage"][0];cov.update(primary_run_receipt=None,comparison_status="UNRESOLVED_NO_ACCEPTED_FULL_BUDGET")
  a["allocated_gpu_seconds_all_attempts"]-=3583;i.update(all_allocated_gpu_seconds=a["allocated_gpu_seconds_all_attempts"],full_budget_comparable_tasks=27,complete_generation_matrix=False)
  result=f.generation_matrix(pl,a,c,i);self.assertEqual(result["all_gpu_seconds"],100800-3583)
  rows=f.explicit_evaluation_rows(p,c["coverage"],[],cm);rr=[x for x in rows if x["task_id"]==r["task"]["task_id"]]
  self.assertTrue(all(x["reason"]=="GENERATION_UNRESOLVED_NO_FULL_BUDGET"and x["observed_fixed_cohort_R0_per_GPU_hour"]is None for x in rr))
 def test_full_time_with_engineering_failure_rejected(self):
  p,pl,a,c,i,_=fixture();a["tasks"][0]["attempt_status_counts"]["ENGINEERING_FAILURE"]=1
  with self.assertRaisesRegex(ValueError,"engineering"):f.generation_matrix(pl,a,c,i)
 def test_timeout_requires_full_receipt_actual_budget(self):
  p,pl,a,c,i,_=fixture();a["tasks"][0]["scheduler_allocation"]["state"]="TIMEOUT";f.generation_matrix(pl,a,c,i)
  a["tasks"][0]["status"]="ENGINEERING_INTERRUPTION"
  with self.assertRaises(ValueError):f.generation_matrix(pl,a,c,i)
 def test_wrong_actual_tres_count_rejected(self):
  p,pl,a,c,i,_=fixture();a["tasks"][0]["scheduler_allocation"]["gpu_count"]=2
  with self.assertRaisesRegex(ValueError,"AllocTRES"):f.generation_matrix(pl,a,c,i)
 def test_duplicate_actual_allocation_rejected(self):
  p,pl,a,c,i,_=fixture();a["tasks"][1]["raw_allocation_id"]=a["tasks"][0]["raw_allocation_id"]
  with self.assertRaisesRegex(ValueError,"physical allocation"):f.generation_matrix(pl,a,c,i)
 def test_duplicate_full_task_postresult_selection_rejected(self):
  p,pl,a,c,i,_=fixture();r=copy.deepcopy(a["tasks"][0]);r["raw_allocation_id"]="80000";r["scheduler_allocation"]["raw_allocation_id"]="80000";a["tasks"].append(r)
  with self.assertRaisesRegex(ValueError,"Post-result"):f.generation_matrix(pl,a,c,i)
 def test_hardware_memory_contract_is_independent(self):
  p,pl,a,c,i,_=fixture();a["tasks"][0]["hardware"]["gpus"][0]["memory_total_mib"]=20000
  with self.assertRaises(ValueError):f.generation_matrix(pl,a,c,i)
 def test_accepted_only_sampling_prohibited_by_pool_closure(self):
  p,pl,a,c,i,cm=one_selected();c["coverage"][0]["n_unique_complete"]=5;c["coverage"][0]["n_native_score_missing"]=5
  with self.assertRaisesRegex(ValueError,"Uniform pool"):f.generation_matrix(pl,a,c,i)
 def test_underfill_one_selected_retains_requested3_quality(self):
  p,pl,a,c,i,cm=one_selected();f.generation_matrix(pl,a,c,i);rows=f.explicit_evaluation_rows(p,c["coverage"],c["selected"],cm)
  r=next(x for x in rows if x["task_id"]==c["selected"][0]["task_id"]and x["cohort"]==f.COHORTS[0]and x["engine"]=="boltz")
  self.assertEqual((r["n_requested"],r["n_selected"],r["underfilled"],r["quality_R1"]),(3,1,True,.3))
 def test_missing_nonempty_common_summary_keeps_selected_denominator(self):
  p,pl,a,c,i,cm=one_selected();cm["cohort_summaries"]=[]
  rows=f.explicit_evaluation_rows(p,c["coverage"],c["selected"],cm);r=next(x for x in rows if x["n_selected"])
  self.assertEqual(r["n_selected"],1);self.assertEqual(r["reason"],"MISSING_PRESELECTED_COHORT_SUMMARY");self.assertIsNone(r["quality_R1"])
 def test_duplicate_summary_silent_overwrite_rejected(self):
  p,pl,a,c,i,cm=one_selected();cm["cohort_summaries"].append(copy.deepcopy(cm["cohort_summaries"][0]))
  with self.assertRaisesRegex(ValueError,"Duplicate common cohort"):f.explicit_evaluation_rows(p,c["coverage"],c["selected"],cm)
 def test_missing_preselected_outcome_cannot_claim_R1_complete(self):
  p,pl,a,c,i,cm=one_selected();cm["outcomes"]["boltz"]=[]
  with self.assertRaisesRegex(ValueError,"entirely missing"):f.explicit_evaluation_rows(p,c["coverage"],c["selected"],cm)
 def test_nonfinite_summary_rejected(self):
  p,pl,a,c,i,cm=one_selected();cm["cohort_summaries"][0]["R1_candidates"]["median"]=float("nan")
  with self.assertRaisesRegex(ValueError,"quality"):f.explicit_evaluation_rows(p,c["coverage"],c["selected"],cm)
 def test_r1_missing_model_null_not_zero(self):
  p,pl,a,c,i,cm=one_selected();s=cm["cohort_summaries"][0];s.update(n_R1_complete=0);s["R1_candidates"].update(n_valid=0,median=None);s["model_coverage"]["valid"]=2
  rows=f.explicit_evaluation_rows(p,c["coverage"],c["selected"],cm);r=next(x for x in rows if x["n_selected"]and x["engine"]=="boltz")
  self.assertIsNone(r["quality_R1"]);self.assertEqual(r["n_selected"],1)
 def test_complete_raw_native_reject_and_na_are_both_counted(self):
  r,a,e,u=raw_fixture();out=f.raw_closure(r,a,e,u);self.assertEqual(out["n_complete_raw_records"],2);self.assertEqual(out["n_unique_sequence_identities"],1)
 def test_rejected_wrong_length_cannot_be_filtered_away(self):
  r,a,e,u=raw_fixture();e[0]["sequence"]="A"*64;e[0]["sequence_sha256"]=hashlib.sha256(e[0]["sequence"].encode()).hexdigest()
  with self.assertRaisesRegex(ValueError,"ALL complete"):f.raw_closure(r,a,e,u)
 def test_boundary_complete_wrong_length_still_contract_failure(self):
  r,a,e,u=raw_fixture();e[1].update(sequence="A"*66,observed_before_generation_cutoff=False,observed_at_epoch=101.)
  e[1]["sequence_sha256"]=hashlib.sha256(e[1]["sequence"].encode()).hexdigest();a[0]["precutoff_sequence_records"]=1
  with self.assertRaisesRegex(ValueError,"ALL complete"):f.raw_closure(r,a,e,u)
 def test_duplicate_sequence_record_not_unique_sequence_repetition(self):
  r,a,e,u=raw_fixture();e[1]["sequence_record_id"]="0"
  with self.assertRaisesRegex(ValueError,"Duplicate original"):f.raw_closure(r,a,e,u)
 def test_all_attempt_sequence_count_must_close(self):
  r,a,e,u=raw_fixture();a[0]["complete_sequence_records"]=1
  with self.assertRaisesRegex(ValueError,"raw sequence denominator"):f.raw_closure(r,a,e,u)
 def test_postcutoff_marked_pre_cutoff_is_rejected(self):
  r,a,e,u=raw_fixture();e[0]["observed_at_epoch"]=101.
  with self.assertRaisesRegex(ValueError,"Post-cutoff"):f.raw_closure(r,a,e,u)
 def test_native_update_missing_original_sequence_rejected(self):
  r,a,e,u=raw_fixture();u[0]["sequence_record_id"]="99"
  with self.assertRaisesRegex(ValueError,"lost original"):f.raw_closure(r,a,e,u)
 def test_fixed_both_rep_mean_all6_and_diagnostic_exclusion(self):
  p,pl,a,c,i,cm=fixture();rows=f.explicit_evaluation_rows(p,c["coverage"],[],cm)
  for r in rows:r["quality_R1"]=999. if r["analysis_role"]=="diagnostic"else(.8 if r["method_id"]=="rf_diffusion"else.2)+(0 if r["seed"]==21011 else.2)
  comp=f.independent_target_aggregation(rows)
  self.assertTrue(all(abs(x["paired_macro_mean_RF_minus_BindCraft"]-.6)<1e-12 for x in comp))
  self.assertTrue(all(x["inferential_p_value"]is None for x in comp))
  rows[4]["quality_R1"]=None # first primary cell after BBF four cohorts/engines? identity below is more robust.
  first=next(r for r in rows if r["analysis_role"]=="primary"and r["cohort"]==f.COHORTS[0]and r["engine"]=="boltz");first["quality_R1"]=None
  comp=f.independent_target_aggregation(rows);x=next(v for v in comp if v["engine"]=="boltz"and v["cohort"]==f.COHORTS[0])
  self.assertIsNone(x["paired_macro_mean_RF_minus_BindCraft"]);self.assertLess(x["n_paired_available"],6)
 def test_duplicate_112_row_rejected(self):
  p,pl,a,c,i,cm=fixture();rows=f.explicit_evaluation_rows(p,c["coverage"],[],cm);rows[-1]=copy.deepcopy(rows[0])
  with self.assertRaisesRegex(ValueError,"Duplicate 112"):f.independent_target_aggregation(rows)
 def test_current_delivery_empty_matrix_has56rows112replicates(self):
  root=Path("/lustre/users/u21111210118/projects/test9");sys.path.insert(0,str(root/"source/rebuild"));sys.path.insert(0,str(root/"steps/24_benchmark_delivery/code"))
  spec=importlib.util.spec_from_file_location("current_target_statistics",root/"steps/24_benchmark_delivery/code/target_statistics.py")
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  p,pl,a,c,i,cm=fixture();rows=f.explicit_evaluation_rows(p,c["coverage"],[],cm);out=module.target_statistics(cm,p,*f.METHODS)
  self.assertEqual(len(out["rows"]),56);self.assertEqual(sum(len(r["replicates"])for r in out["rows"]),112);f.compare_delivery_statistics(rows,out)
 def test_compile_root_freeze_helpers_without_execution(self):
  for name in("freeze_engineering_pilot_v5.py","freeze_formal_benchmark_v3.py","combine_engineering_acceptance_v1.py"):
   p=Path("/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code")/name;compile(p.read_text(),str(p),"exec")
 def test_root_formal_v3_literal_fields_match_independent_contract(self):
  path=Path("/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/freeze_formal_benchmark_v3.py")
  tree=ast.parse(path.read_text());assignment=next(n for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=="protocol"for t in n.targets))
  keys=[ast.literal_eval(k)for k in assignment.value.keys];self.assertNotIn("max_attempts_safety_limit",keys)
  p=protocol()
  for k,n in zip(keys,assignment.value.values):
   try:value=ast.literal_eval(n)
   except(ValueError,TypeError):continue
   if k in p:p[k]=value
  f.formal_protocol(p)
 def test_actual_gpu_seconds_rate_denominator_not_nominal_hours(self):
  p,pl,a,c,i,cm=one_selected();rows=f.explicit_evaluation_rows(p,c["coverage"],c["selected"],cm,{c["selected"][0]["task_id"]:3602})
  r=next(x for x in rows if x["n_selected"]and x["engine"]=="boltz")
  self.assertAlmostEqual(r["observed_fixed_cohort_R0_per_GPU_hour"],3600/3602)
 def test_common_primary_not_pooled_with_af2(self):
  p,pl,a,c,i,cm=fixture();rows=f.explicit_evaluation_rows(p,c["coverage"],[],cm)
  for r in rows:r["quality_R1"]=(.8 if r["method_id"]=="rf_diffusion"else.2)if r["engine"]=="boltz"else(.1 if r["method_id"]=="rf_diffusion"else.9)
  comparisons=f.independent_target_aggregation(rows)
  b=next(x for x in comparisons if x["engine"]=="boltz");af=next(x for x in comparisons if x["engine"]=="af2")
  self.assertAlmostEqual(b["paired_macro_mean_RF_minus_BindCraft"],.6);self.assertAlmostEqual(af["paired_macro_mean_RF_minus_BindCraft"],-.8)
 def test_common_candidate_median_cannot_be_fabricated_after_unblinding(self):
  fx=FixedCommonSlots();inference,scored,membership,selected=fx.fixtures()
  for s in scored["results"]:
   for axis in("R0","R1"):s[axis]=f.continuous_summary([v[axis]for v in s["models"]],s["expected_models"])
  m=membership["members"][0];summaries=[]
  for s in scored["results"]:
   summaries.append(dict(target_id=m["target_id"],method_id=m["method_id"],seed=m["seed"],cohort=m["cohort"],engine=s["engine"],
      n_selected=1,n_R1_complete=1,R0_candidates=f.continuous_summary([s["R0"]["median"]],1),R1_candidates=f.continuous_summary([s["R1"]["median"]],1),
      model_coverage=dict(expected=s["expected_models"],valid=s["expected_models"])))
  common={"cohort_summaries":summaries};f.common_candidate_summaries(scored,membership,common)
  common["cohort_summaries"][0]["R1_candidates"]["median"]+=.1
  with self.assertRaisesRegex(ValueError,"Scored-to-cohort"):f.common_candidate_summaries(scored,membership,common)
class FixedCommonSlots(unittest.TestCase):
 def fixtures(self):
  p,pl,a,c,i,cm=one_selected();m=dict(c["selected"][0],blind_id="blind_software");membership={"members":[m]};jobs=[];scored=[]
  for eng,n in f.ENGINES.items():
   slots=[{"seed":s,"model":0}for s in(31011,31012,31013)]if eng=="boltz"else[{"seed":31021,"model":i}for i in(1,2,3,4,5)]
   j=dict(job_key="software_"+eng,blind_id=m["blind_id"],engine=eng,variant="primary",expected_models=n,slots=slots);jobs.append(j)
   vals=[.1+i*.1 for i in range(n)]
   models=[dict(slot=s,R0=v,R1=v)for s,v in zip(slots,vals)]
   median=sorted(vals)[n//2]
   scored.append(dict(j,models=models,R0=dict(n_expected=n,n_valid=n,median=median),R1=dict(n_expected=n,n_valid=n,median=median),operational_pass=None,experimental_probability=None,experimental_blockade=False))
  return {"jobs":jobs},{"results":scored},membership,c["selected"]
 def test_exact_primary3_and_secondary5_slots(self):f.strict_primary_slots(*self.fixtures())
 def test_duplicate_slot_cannot_pass_set_equality(self):
  i,s,m,c=self.fixtures();s["results"][0]["models"].append(copy.deepcopy(s["results"][0]["models"][0]))
  with self.assertRaisesRegex(ValueError,"Duplicate scored model"):f.strict_primary_slots(i,s,m,c)
 def test_control_and_sensitivity_models_also_require_unique_slots(self):
  i,s,m,c=self.fixtures();control=copy.deepcopy(i["jobs"][0]);control.update(job_key="control",blind_id="native_control");i["jobs"].append(control)
  output=copy.deepcopy(s["results"][0]);output.update(job_key="control",blind_id="native_control");output["models"].append(copy.deepcopy(output["models"][0]));s["results"].append(output)
  with self.assertRaisesRegex(ValueError,"Duplicate scored model"):f.strict_primary_slots(i,s,m,c)
 def test_wrong_secondary_model_order_rejected(self):
  i,s,m,c=self.fixtures();i["jobs"][1]["slots"].reverse()
  with self.assertRaisesRegex(ValueError,"required model slots"):f.strict_primary_slots(i,s,m,c)
 def test_missing_model_retained_as_typed_null(self):
  i,s,m,c=self.fixtures();r=s["results"][0];r["models"][0]["R1"]=None;r["R1"].update(n_valid=2,median=None);f.strict_primary_slots(i,s,m,c)
  r["R1"]["median"]=0
  with self.assertRaisesRegex(ValueError,"model median"):f.strict_primary_slots(i,s,m,c)

class EngineeringCombinationContracts(unittest.TestCase):
 """Temporary software-only receipts test the root metadata combiner; no scientific outputs."""
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix="software_combine_",dir="/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code")
  self.root=Path(self.temp.name);self.code=Path("/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code")
  spec=importlib.util.spec_from_file_location("engineering_combiner_contract",self.code/"combine_engineering_acceptance_v1.py")
  self.builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.builder)
  self.builder.R=self.root;self.builder.P=self.root/"steps/22_matched_benchmark/settings/pilot_v8"
  self.stage_sets={"rf_diffusion":{"rf_diffusion_backbone","original_proteinmpnn","native_af2_ptm1"},"bindcraft":{"native_bindcraft_trajectory","soluble_proteinmpnn","native_af2_ptm1_and_2","native_filters"}}
  self.save(self.builder.P/"source/benchmark_runtime.py","software fixture source; not executable")
  bridge=self.root/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/prepared_inputs.json"
  self.save(bridge,{"software_fixture":True})
  self.manifest=self.save(self.root/"target_manifest.json",{"software_fixture":True})
  self.tasks=[{"method_id":m,"task_id":"software_task_"+m}for m in f.METHODS]
  self.methods=[{"method_id":m,"config_receipt":self.save(self.root/(m+"_cfg.json"),{"software_fixture":True})}for m in f.METHODS]
  self.plan={"tasks":self.tasks,"protocol":{"methods":self.methods,"targets":[{"input_manifest":self.manifest}]}}
  pp=self.root/"steps/22_matched_benchmark/engineering_pilot/plan_v5/frozen_plan.json";self.planreceipt=self.save(pp,self.plan)
  self.accpaths={};self.runs=[]
  for task,method in zip(self.tasks,self.methods):
   mid=task["method_id"];run=self.save(self.root/(mid+"_run.json"),{"plan":self.planreceipt,"task":task});self.runs.append(run)
   stage={s:self.save(self.root/(mid+"_"+s+".json"),{"software_fixture":True,"status":"PASS"})for s in self.stage_sets[mid]}
   obj={"status":"NATIVE_GPU_METHOD_WORKFLOW_CONTENT_ACCEPTED_ENGINEERING_ONLY","method_id":mid,"plan":self.planreceipt,
    "runtime_source":self.builder.receipt(self.builder.P/"source/benchmark_runtime.py"),"task_id":task["task_id"],"actual_assigned_gpu_count":1,"scientific_scope":"ENGINEERING_ONLY",
    "native_stage_status":{s:"PASS"for s in self.stage_sets[mid]},"stage_evidence":stage,"config_receipt":method["config_receipt"],"target_manifest":self.manifest,"run_receipt":run}
   path=self.root/(mid+"_acceptance.json");self.save(path,obj);self.accpaths[mid]=path
  runset=self.save(self.root/"run_set.json",self.runs)
  self.accountingpath=self.root/"accounting.json"
  self.save(self.accountingpath,{"status":"INDEPENDENT_BUDGET_LEDGER_AND_COHORT_AUDIT_PASS","plan":self.planreceipt,
   "independent_auditor":self.builder.receipt(self.builder.B/"paired_budget_independent.py"),"allocation_count":2,"expected_tasks":2,"run_receipts_input":runset})
  self.out=self.root/"combined.json"
 def tearDown(self):self.temp.cleanup()
 def save(self,path,obj):
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text(obj if isinstance(obj,str)else json.dumps(obj));return f.receipt(path)
 def mutate(self,path,operation):
  obj=f.read(path);operation(obj);self.save(path,obj)
 def invoke(self,cpu="JobId=99001 JobState=RUNNING TRES=cpu=1,node=1,billing=1"):
  argv=["combine","--rf",str(self.accpaths["rf_diffusion"]),"--bc",str(self.accpaths["bindcraft"]),"--accounting",str(self.accountingpath),"--out",str(self.out)]
  with mock.patch.object(sys,"argv",argv),mock.patch.dict(os.environ,{"SLURM_JOB_ID":"99001","CUDA_VISIBLE_DEVICES":""}),mock.patch.object(self.builder.subprocess,"check_output",return_value=cpu):
   self.builder.main()
  return f.read(self.out)
 def test_combiner_complete_exact2_pins_and_stages_accept(self):
  result=self.invoke();self.assertEqual(result["status"],"BOTH_NATIVE_GPU_METHOD_WORKFLOWS_CONTENT_ACCEPTED_ENGINEERING_ONLY")
  self.assertEqual(result["plan"],self.planreceipt);self.assertEqual({x["method_id"]for x in result["method_acceptances"]},set(f.METHODS))
 def test_combiner_wrong_actual_runtime_source_rejected(self):
  self.mutate(self.accpaths["rf_diffusion"],lambda o:o["runtime_source"].update(sha256="0"*64))
  with self.assertRaisesRegex(ValueError,"source/plan/task"):self.invoke()
 def test_combiner_wrong_native_config_rejected(self):
  self.mutate(self.accpaths["bindcraft"],lambda o:o["config_receipt"].update(sha256="0"*64))
  with self.assertRaisesRegex(ValueError,"config/target"):self.invoke()
 def test_combiner_wrong_task_rejected(self):
  self.mutate(self.accpaths["rf_diffusion"],lambda o:o.update(task_id="wrong_task"))
  with self.assertRaisesRegex(ValueError,"source/plan/task"):self.invoke()
 def test_combiner_missing_native_af2_stage_rejected(self):
  self.mutate(self.accpaths["bindcraft"],lambda o:o["stage_evidence"].pop("native_af2_ptm1_and_2"))
  with self.assertRaisesRegex(ValueError,"workflow stage"):self.invoke()
 def test_combiner_engineering_failure_cannot_pass_status(self):
  self.mutate(self.accpaths["rf_diffusion"],lambda o:o.update(status="ENGINEERING_FAILURE"))
  with self.assertRaisesRegex(ValueError,"engineering acceptance"):self.invoke()
 def test_combiner_supplemental_allocation_not_merged_as_main_run(self):
  obj=f.read(self.accountingpath);runset=Path(obj["run_receipts_input"]["path"]);self.save(runset,self.runs+[self.runs[0]])
  obj["run_receipts_input"]=f.receipt(runset);self.save(self.accountingpath,obj)
  with self.assertRaisesRegex(ValueError,"run set differs"):self.invoke()
 def test_combiner_same_count_but_wrong_audited_run_rejected(self):
  obj=f.read(self.accountingpath);extra=self.save(self.root/"other_run.json",{"software_fixture":True})
  runset=Path(obj["run_receipts_input"]["path"]);self.save(runset,[self.runs[0],extra]);obj["run_receipts_input"]=f.receipt(runset);self.save(self.accountingpath,obj)
  with self.assertRaisesRegex(ValueError,"run set differs"):self.invoke()
 def test_combiner_real_run_task_receipt_drift_rejected(self):
  obj=f.read(self.accpaths["rf_diffusion"]);rp=Path(obj["run_receipt"]["path"]);run=f.read(rp);run["task"]["task_id"]="wrong"
  self.save(rp,run);obj["run_receipt"]=f.receipt(rp);self.save(self.accpaths["rf_diffusion"],obj)
  with self.assertRaisesRegex(ValueError,"Run receipt differs"):self.invoke()
 def test_combiner_wrong_actual_assigned_gpu_count_rejected(self):
  self.mutate(self.accpaths["bindcraft"],lambda o:o.update(actual_assigned_gpu_count=2))
  with self.assertRaisesRegex(ValueError,"actual GPU"):self.invoke()

if __name__=="__main__":unittest.main(verbosity=2)

