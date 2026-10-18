"""PureCPU contract fixtures: no scheduler submission or model invocation."""
import copy,datetime,unittest
import root_gpu_cost_audit as m
def receipt(name):
 return dict(path=str(m.R/"steps/24_benchmark_delivery/frozen"/"cost_fixture"/name),bytes=1,sha256="a"*64)
def stamp(seconds):
 return datetime.datetime.fromtimestamp(m.utc(m.PRIMARY_START)+seconds,datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
def line(jid="800_0",raw="801",name="test9_fixture",state="FAILED",elapsed=10,tres="cpu=3,gres/gpu=1",start=10,**kw):
 vals=dict(logical_id=jid,raw_id=raw,job_name=name,user=m.USER,account=m.USER,state=state,elapsed_seconds=elapsed,AllocTRES=tres,Submit=stamp(0),Start=stamp(start+0),End=stamp(start+int(elapsed))if str(elapsed).isdigit()else stamp(start+10),node="organ01",partition="organ",WorkDir=str(m.R));vals.update(kw)
 return "|".join(str(vals[k])for k in ("logical_id","raw_id","job_name","user","account","state","elapsed_seconds","AllocTRES","Submit","Start","End","node","partition","WorkDir"))+"\n"
def dispatch(job="800",ix=None):
 return dict(submission_id="fixture_"+job,phase="formal_generation",kind="primary",job_id=job,indices=[0]if ix is None else ix,stage=None,preflight=None,launcher=receipt("launcher.sbatch"),job_name="test9_fixture",WorkDir=str(m.R),expected_allocation_count=1,rerun_of=None)
def close(text=None,universe=None,ds=None):
 text=line()if text is None else text
 return m.close_rows([dispatch()]if ds is None else ds,text,text if universe is None else universe,m.utc(m.PRIMARY_START)+120)
def launcher(e2e=False):
 rows=["#SBATCH --job-name=test9_fixture","#SBATCH --gres=gpu:1","#SBATCH --cpus-per-task=3","#SBATCH --mem=64G","export OMP_NUM_THREADS=4"]
 if not e2e:rows.append("#SBATCH --chdir="+str(m.R))
 return "\n".join(rows)
def formal():
 ent=dict(submission_id="formal13260",phase="formal_generation",kind="primary",receipt=dict(path=str(m.FORMAL_SUB),bytes=1,sha256="a"*64))
 ln=receipt("formal.sbatch")
 c=dict(schema="paired_formal_resource_submission.v1",job_id="13260",launcher=ln,plan=m.FORMAL_PLAN,resource_policy=m.POLICY,submit_argv=["sbatch","--parsable",ln["path"]],raw_sbatch_stdout="13260\n",raw_sbatch_stderr="")
 return ent,c,lambda r:dict(status="FROZEN_BEFORE_GENERATION",tasks=[dict(index=i)for i in range(28)])
def common():
 ent=dict(submission_id="common14000",phase="common_review",kind="primary",receipt=receipt("common_submission.json"))
 pr=receipt("common_preflight.json");entry=receipt("common_review_successor.py");ln=receipt("common_review_gpu.sbatch")
 pre=dict(status="COMMON_SUCCESSOR_CPU_PREFLIGHT_ACCEPTED_ROOT_PENDING_ONLY_GPU_SUBMISSION_REQUIRED",no_inference=True,root_submission_performed=False,root_pending_job_indices=[2,4],source=dict(successor=[entry,ln]))
 c=dict(schema="formal_common_root_submission.v1",array_job_id="14000",preflight=pr,indices=[2,4],concurrency_cap=2,entry=entry,launcher=ln,submit_argv=["sbatch","--parsable","--export=ALL,COMMON_SUCCESSOR_ENTRY="+entry["path"],"--array=2,4%2",ln["path"],pr["path"]],raw_sbatch_stdout="14000\n",raw_sbatch_stderr="")
 return ent,c,lambda r:pre
def e2e(stage="design"):
 ent=dict(submission_id="e2e15000",phase="reference_free_e2e",kind="primary",receipt=receipt("e2e_submission.json"))
 pr=receipt("physical_acceptance.json");source=receipt("physical_source.json");ln=receipt("e2e_gpu_stage.sbatch");entry=receipt("e2e_model_stage.py");pose=receipt("qualified_pose.json")
 pre=dict(status="CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED",GPU_allocated=0,source_manifest=source,qualified_prediction=dict(status="POSE_ACCEPTED",manifest=pose))
 docs={pr["path"]:pre,source["path"]:dict(files=[ln,entry])}
 c=dict(schema="reference_free_root_model_submission.v1",job_id="15000",preflight_acceptance=pr,source_manifest=source,stage=stage,submission_workdir=str(m.R),launcher=ln,entry=entry,upstream=pose,result_dir=str(m.R/"steps/25_reference_free_e2e/runs/fixture"),raw_sbatch_stdout="15000\n",raw_sbatch_stderr="")
 if stage=="evaluate":
  c["upstream"]=receipt("actual_design.json");c["design_stage_result"]=receipt("design_stage_result.json");c["design_audit_acceptance"]=receipt("design_cpu_acceptance.json")
  docs[c["design_stage_result"]["path"]]=dict(stage="design",status="ACTUAL_MODEL_STAGE_COMPLETE",result_manifest=c["upstream"])
  docs[c["design_audit_acceptance"]["path"]]=dict(status="REFERENCE_FREE_E2E_ACTUAL_DESIGN_CPU_CONTENT_ACCEPTED",actual_design_manifest=c["upstream"],actual_design_stage_result=c["design_stage_result"])
 c["submit_argv"]=["sbatch","--parsable","--chdir="+str(m.R),ln["path"],stage,pr["path"],c["upstream"]["path"],c["result_dir"]]
 if stage=="evaluate":c["submit_argv"] +=[c["design_stage_result"]["path"],c["design_audit_acceptance"]["path"]]
 return ent,c,lambda r:docs[r["path"]],docs
def ledger():
 e,_,_=formal()
 return dict(schema="root-current-gpu-submission-universe.v1",authority_root=str(m.R),scope_start_utc=m.PRIMARY_START,scope_end_utc=stamp(120)+"Z",formal_array_job_id="13260",global_current_scope_gpu_cap=2,entries=[e],common_preflight=receipt("common_preflight.json"),physical_preflight=receipt("physical_acceptance.json"),e2e_disposition="upstream_rejected")
class Costs(unittest.TestCase):
 def test_failed_missing_manifest_keeps_cost(self):
  r=close();self.assertEqual((r["actual_GPU_seconds"],r["allocated_failure_GPU_seconds"]),(10,10));self.assertFalse(r["result_manifests_read_for_cost"])
 def test_completed_keeps_actual_cost(self):self.assertEqual(close(line(state="COMPLETED"))["actual_GPU_seconds"],10)
 def test_timeout_keeps_full_cost(self):self.assertEqual(close(line(state="TIMEOUT"))["allocated_failure_GPU_seconds"],10)
 def test_oom_keeps_full_cost(self):self.assertEqual(close(line(state="OUT_OF_MEMORY"))["actual_GPU_seconds"],10)
 def test_allocated_cancel_keeps_full_cost(self):self.assertEqual(close(line(state="CANCELLED by 12"))["allocated_failure_GPU_seconds"],10)
 def test_step_excluded_not_doublecharged(self):
  r=close(line()+line(jid="800_0.batch",raw="801.batch"));self.assertEqual(r["actual_GPU_seconds"],10);self.assertEqual(len(r["excluded_job_steps"]),1)
 def test_zero_unallocated_cancel_separate(self):
  r=close(line(state="CANCELLED",elapsed=0,tres="",Start="Unknown",End="Unknown"));self.assertEqual((r["zero_unallocated_cancels"],r["allocated_GPU_jobs"]),(1,0))
 def test_allocated_zero_seconds_not_unallocated(self):
  r=close(line(elapsed=0));self.assertEqual((r["zero_unallocated_cancels"],r["allocated_GPU_jobs"]),(0,1))
 def test_unknown_elapsed_not_zero(self):
  with self.assertRaises(ValueError):close(line(elapsed="Unknown"))
 def test_nonterminal_rejected(self):
  with self.assertRaises(ValueError):close(line(state="RUNNING"))
 def test_unknown_state_rejected(self):
  with self.assertRaises(ValueError):close(line(state="MYSTERY"))
 def test_missing_submitted_slot_rejected(self):
  with self.assertRaises(ValueError):close("",ds=[dispatch(ix=[0,1])])
 def test_duplicate_logical_rejected(self):
  with self.assertRaises(ValueError):close(line()+line())
 def test_duplicate_raw_allocation_rejected(self):
  with self.assertRaises(ValueError):close(line()+line(jid="800_1"),ds=[dispatch(ix=[0,1])])
 def test_unmapped_positive_job_rejected(self):
  with self.assertRaises(ValueError):close(universe=line()+line(jid="900",raw="900"))
 def test_time_universe_coverage_required(self):
  with self.assertRaises(ValueError):close(universe="")
 def test_duplicate_universe_positive_rejected(self):
  with self.assertRaises(ValueError):close(universe=line()+line())
 def test_unrelated_name_does_not_expand_scope(self):self.assertEqual(close(universe=line()+line(jid="900",raw="900",name="unrelated_other_project"))["actual_GPU_seconds"],10)
 def test_cpu4_rejected(self):
  with self.assertRaises(ValueError):close(line(tres="cpu=4,gres/gpu=1"))
 def test_gpu2_rejected(self):
  with self.assertRaises(ValueError):close(line(tres="cpu=3,gres/gpu=2"))
 def test_typed_generic_gpu_consistent(self):self.assertEqual(close(line(tres="cpu=3,gres/gpu=1,gres/gpu:a100=1"))["actual_GPU_seconds"],10)
 def test_typed_generic_disagreement_rejected(self):
  with self.assertRaises(ValueError):close(line(tres="cpu=3,gres/gpu=1,gres/gpu:a100=2"))
 def test_missing_memory_is_unavailable(self):self.assertEqual(close()["rows"][0]["actual_memory_AllocTRES"],"UNAVAILABLE_NOT_ZERO")
 def test_actual_wrong_memory_rejected(self):
  with self.assertRaises(ValueError):close(line(tres="cpu=3,mem=32G,gres/gpu=1"))
 def test_wrong_account_rejected(self):
  with self.assertRaises(ValueError):close(line(account="other"))
 def test_wrong_jobname_rejected(self):
  with self.assertRaises(ValueError):close(line(name="test9_different"))
 def test_elapsed_interval_mismatch_rejected(self):
  with self.assertRaises(ValueError):close(line(End=stamp(35)))
 def test_allocated_interval_before_scope_rejected(self):
  with self.assertRaises(ValueError):close(line(start=-1))
 def test_compressed_cancel_expand_exact(self):
  t=line(jid="800_[0-1%2]",raw="800",state="CANCELLED",elapsed=0,tres="",Start="Unknown",End="Unknown")
  r=close(t,ds=[dispatch(ix=[0,1])]);self.assertEqual((r["expected_submitted_allocation_slots"],r["zero_unallocated_cancels"]),(2,2))
 def test_compressed_positive_is_ambiguous(self):
  with self.assertRaises(ValueError):close(line(jid="800_[0-1]"),ds=[dispatch(ix=[0,1])])
 def test_zero_parent_not_extra_task(self):
  r=close(line()+line(jid="800",raw="800",state="CANCELLED",elapsed=0,tres="",Start="Unknown",End="Unknown"));self.assertEqual(r["expected_submitted_allocation_slots"],1)
 def test_global_three_gpu_intervals_rejected(self):
  t=line()+line(jid="800_1",raw="802")+line(jid="800_2",raw="803")
  with self.assertRaises(ValueError):close(t,ds=[dispatch(ix=[0,1,2])])
 def test_equal_end_start_not_third_gpu(self):
  t=line()+line(jid="800_1",raw="802")+line(jid="800_2",raw="803",start=20)
  self.assertEqual(close(t,ds=[dispatch(ix=[0,1,2])])["actual_maximum_current_scope_concurrent_GPUs"],2)
 def test_missing_actual_gpu_TRES_not_zero(self):
  with self.assertRaises(ValueError):close(line(tres="cpu=3,mem=64G"))
  with self.assertRaises(ValueError):close(line(state="CANCELLED",elapsed=0,tres=""))
 def test_raw_array_task_id_equal_master_still_charged(self):
  self.assertEqual(close(line(raw="800"))["actual_GPU_seconds"],10)
 def test_actual_workdir_mismatch_rejected(self):
  with self.assertRaises(ValueError):close(line(WorkDir="/another"))
class SubmissionContracts(unittest.TestCase):
 def check(self,t):return m.submission_contract(t[0],t[1],t[2],launcher(t[0]["phase"]=="reference_free_e2e"))
 def test_actual_formal_primary28(self):self.assertEqual(self.check(formal())["expected_allocation_count"],28)
 def test_formal_plan_mutation_rejected(self):
  e,c,f=formal();c["plan"]=receipt("other_plan.json")
  with self.assertRaises(ValueError):self.check((e,c,f))
 def test_primary_receipt_location_exact(self):
  e,c,f=formal();e["receipt"]=receipt("forged_primary.json")
  with self.assertRaises(ValueError):self.check((e,c,f))
 def test_formal_resource_override_rejected(self):
  e,c,f=formal();c["submit_argv"].insert(2,"--cpus-per-task=4")
  with self.assertRaises(ValueError):self.check((e,c,f))
 def test_raw_actual_submission_stdout_required(self):
  e,c,f=formal();del c["raw_sbatch_stdout"]
  with self.assertRaises(ValueError):self.check((e,c,f))
 def test_common_exact_pending_source_argv(self):self.assertEqual(self.check(common())["indices"],[2,4])
 def test_common_dependency_after_export(self):
  e,c,f=common();c["dependency"]="afterany:13260:14000_1";c["submit_argv"].insert(3,"--dependency="+c["dependency"])
  self.assertEqual(self.check((e,c,f))["expected_allocation_count"],2)
 def test_common_preflight_wrong_argument_rejected(self):
  e,c,f=common();c["submit_argv"][-1]=receipt("other.json")["path"]
  with self.assertRaises(ValueError):self.check((e,c,f))
 def test_common_unqualified_source_rejected(self):
  e,c,f=common();c["entry"]=receipt("different.py")
  with self.assertRaises(ValueError):self.check((e,c,f))
 def test_e2e_design_pose_exact(self):self.assertEqual(self.check(e2e()[:3])["stage"],"design")
 def test_e2e_evaluate_actual_cpu_gate(self):self.assertEqual(self.check(e2e("evaluate")[:3])["stage"],"evaluate")
 def test_e2e_rejected_pose_never_force_design(self):
  e,c,f,d=e2e();d[c["preflight_acceptance"]["path"]]["qualified_prediction"]["status"]="POSE_REJECTED"
  with self.assertRaises(ValueError):self.check((e,c,f))
 def test_e2e_missing_design_gate_rejected(self):
  e,c,f,d=e2e("evaluate");d[c["design_audit_acceptance"]["path"]]["status"]="PENDING"
  with self.assertRaises(ValueError):self.check((e,c,f))
 def test_e2e_wrong_upstream_argv_rejected(self):
  e,c,f,d=e2e();c["submit_argv"][6]=receipt("different_pose.json")["path"]
  with self.assertRaises(ValueError):self.check((e,c,f))
 def test_e2e_actual_root_workdir_required(self):
  e,c,f,d=e2e();del c["submission_workdir"]
  with self.assertRaises(ValueError):self.check((e,c,f))
 def test_e2e_root_chdir_argv_required(self):
  e,c,f,d=e2e();c["submit_argv"].pop(2)
  with self.assertRaises(ValueError):self.check((e,c,f))
 def test_numeric_failure_inventory_independent_of_manifest(self):
  r=m.preliminary_inventory(line(),line());self.assertEqual(r["positive_failure_rows"][0]["elapsed_seconds"],10);self.assertFalse(r["result_manifest_required"])
 def test_generic1_typed0_disagreement_rejected(self):
  with self.assertRaises(ValueError):close(line(tres="cpu=3,gres/gpu=1,gres/gpu:a100=0"))
class UniverseContracts(unittest.TestCase):
 def test_current_formal_ledger(self):self.assertEqual(len(m.ledger_contract(ledger())[0]),1)
 def test_duplicate_submission_identity_rejected(self):
  l=ledger();l["entries"]*=2
  with self.assertRaises(ValueError):m.ledger_contract(l)
 def test_scope_cannot_skip_first_submit(self):
  l=ledger();l["scope_start_utc"]=stamp(1)+"Z"
  with self.assertRaises(ValueError):m.ledger_contract(l)
 def test_rerun_separate_identity_parent(self):
  l=ledger();e=copy.deepcopy(l["entries"][0]);e.update(submission_id="formal_retry",kind="technical_rerun",rerun_of="formal13260",scientific_results_merged=False,receipt=receipt("retry.json"));l["entries"].append(e)
  self.assertEqual(len(m.ledger_contract(l)[0]),2)
 def test_rerun_silent_result_merge_rejected(self):
  l=ledger();e=copy.deepcopy(l["entries"][0]);e.update(submission_id="retry",kind="technical_rerun",rerun_of="formal13260",scientific_results_merged=True);l["entries"].append(e)
  with self.assertRaises(ValueError):m.ledger_contract(l)
 def test_missing_rerun_ancestor_rejected(self):
  l=ledger();e=copy.deepcopy(l["entries"][0]);e.update(submission_id="retry",kind="technical_rerun",rerun_of="missing",scientific_results_merged=False);l["entries"].append(e)
  with self.assertRaises(ValueError):m.ledger_contract(l)
 def test_root_bool_does_not_supply_universe(self):
  l=ledger();l.update(entries=[],complete_root_gpu_submission_universe=True)
  with self.assertRaises(ValueError):m.ledger_contract(l)
 def test_naive_scope_timestamp_rejected(self):
  with self.assertRaises(ValueError):m.utc(stamp(10))
 def test_descriptor_hash_not_placeholder(self):
  r=receipt("fixture");r["sha256"]="UNKNOWN"
  with self.assertRaises(ValueError):m.shape(r)


def journal():
 l=ledger();return dict(schema="root-current-gpu-submission-journal.v1",authority_root=str(m.R),scope_start_utc=m.PRIMARY_START,entries=[dict(submission_id=e["submission_id"],phase=e["phase"],kind=e["kind"],receipt_path=e["receipt"]["path"])for e in l["entries"]])
class JournalContracts(unittest.TestCase):
 def test_formal_only_journal_no_future_gates_needed(self):
  self.assertEqual(len(m.journal_contract(journal())),1)
 def test_journal_unique_receipt_path_required(self):
  j=journal();e=dict(j["entries"][0],submission_id="other");j["entries"].append(e)
  with self.assertRaises(ValueError):m.journal_contract(j)
 def test_journal_append_prefix_preserved(self):
  a=journal();b=copy.deepcopy(a);b["entries"].append(dict(submission_id="common_new",phase="common_review",kind="primary",receipt_path=receipt("new.json")["path"]))
  m.journal_prefix(a,b)
 def test_journal_prefix_drop_rejected(self):
  a=journal();a["entries"].append(dict(submission_id="common_new",phase="common_review",kind="primary",receipt_path=receipt("new.json")["path"]));b=journal()
  with self.assertRaises(ValueError):m.journal_prefix(a,b)
 def test_journal_metadata_no_source_hash_required(self):
  self.assertTrue(all("sha256"not in e and "receipt"not in e for e in m.journal_contract(journal())))

def CPUrecord(tres="TRES=cpu=2,node=1,billing=2",cpus="2"):
 return "JobId=17000 JobState=RUNNING NumCPUs="+cpus+" UserId="+m.USER+"(123) Account="+m.USER+" Partition=organ "+tres
class CPUAllocationContracts(unittest.TestCase):
 def test_actual_old_live_TRES_cpu2_accepted(self):
  self.assertEqual(m.select_cpu_record(CPUrecord(),"17000")["allocated_TRES_fields"],["TRES"])
 def test_actual_new_live_AllocTRES_cpu2_accepted(self):
  self.assertEqual(m.select_cpu_record(CPUrecord("AllocTRES=cpu=2,node=1,billing=2"),"17000")["allocated_CPUs"],2)
 def test_both_actual_CPU_representations_agree(self):
  self.assertEqual(m.select_cpu_record(CPUrecord("TRES=cpu=2,node=1 AllocTRES=node=1,cpu=2"),"17000")["allocated_TRES_fields"],["TRES","AllocTRES"])
 def test_both_actual_CPU_representations_disagree_rejected(self):
  with self.assertRaises(ValueError):m.select_cpu_record(CPUrecord("TRES=cpu=2,node=1 AllocTRES=cpu=2,node=2"),"17000")
 def test_missing_actual_CPU_TRES_rejected(self):
  with self.assertRaises(ValueError):m.select_cpu_record(CPUrecord(""),"17000")
 def test_empty_actual_CPU_TRES_rejected(self):
  for tres in ("TRES=","AllocTRES=","TRES= AllocTRES=cpu=2,node=1","TRES=cpu=2,node=1 AllocTRES="):
   with self.assertRaises(ValueError):m.select_cpu_record(CPUrecord(tres),"17000")
 def test_actual_CPU_helper_GPU1_rejected(self):
  with self.assertRaises(ValueError):m.select_cpu_record(CPUrecord("TRES=cpu=2,gres/gpu=1"),"17000")
 def test_actual_CPU_NumCPUs_discrepancy_rejected(self):
  with self.assertRaises(ValueError):m.select_cpu_record(CPUrecord(cpus="3"),"17000")
