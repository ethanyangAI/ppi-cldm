"""Meaningful software boundary fixtures. No generated formal sequences or model calls."""
import copy,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import common_review_successor as m
def fixture():
 targets=[dict(target_id="T"+str(i),synthetic=i==6)for i in range(7)]
 entities=[dict(blind_id="N"+str(i),target_id="T"+str(i))for i in range(7)]
 controls=[dict(blind_id=e["blind_id"],target_id=e["target_id"])for e in entities]
 jobs=[]
 for e in entities:
  for engine in("boltz","af2"):
   jobs.append(dict(blind_id=e["blind_id"],target_id=e["target_id"],engine=engine,variant="primary",expected_models=3 if engine=="boltz"else 5,slots=[dict(seed=s,model=0)for s in(31011,31012,31013)]if engine=="boltz"else[dict(seed=31021,model=i)for i in(1,2,3,4,5)]))
  if e["target_id"]!="T6":jobs.append(dict(blind_id=e["blind_id"],target_id=e["target_id"],engine="boltz",variant="single_sensitivity",expected_models=3,slots=[dict(seed=s,model=0)for s in(31011,31012,31013)]))
 for i,j in enumerate(jobs):j["job_key"]="J"+str(i)
 return dict(entities=entities,jobs=jobs),dict(targets=targets),dict(controls=controls,members=[])
def allocation():
 return dict(selected_scheduler_record="JobId=88 ArrayJobId=70 ArrayTaskId=1 JobState=RUNNING NumCPUs=3 MinMemoryNode=64G Command=/fake\n",owned_gpu_guard=dict(status="RUNNING_SLURM_GPU_OWNERSHIP_VERIFIED",owned_gpu_uuids=["GPU-3"],child_cuda_visible_devices="GPU-3",hardware=dict(gpus=[dict(name="NVIDIA A100-PCIE-40GB",memory_total_mib=40960)])))
def sourcepre():
 return dict(status="COMMON_SUCCESSOR_CPU_PREFLIGHT_ACCEPTED_ROOT_PENDING_ONLY_GPU_SUBMISSION_REQUIRED",source=dict(successor=[dict(path=str(m.SELF),bytes=1,sha256="a"),dict(path="/frozen/common_review_gpu.sbatch",bytes=1,sha256="b")]),root_pending_job_indices=[2,4])
def submission():
 pre=sourcepre();pr=dict(path="/preflight.json",bytes=1,sha256="c");sub=dict(schema="formal_common_root_submission.v1",preflight=pr,indices=[2,4],concurrency_cap=2,array_job_id="777",launcher=pre["source"]["successor"][1],entry=pre["source"]["successor"][0],submit_argv=["sbatch","--parsable","--export=ALL,COMMON_SUCCESSOR_ENTRY="+str(m.SELF),"--array=2,4%2","/frozen/common_review_gpu.sbatch","/preflight.json"]);return sub,pr,pre
class Contracts(unittest.TestCase):
 def test_native_full20_74(self):
  p,a,v=fixture();r=m.expected_sensitivity(p,a,v);self.assertEqual((r["n_jobs"],r["n_models"],r["n_sensitivity_jobs"]),(20,74,6))
 def test_missing_native_sensitivity_rejected(self):
  p,a,v=fixture();p["jobs"]=[j for j in p["jobs"]if j["job_key"]!="J2"]
  with self.assertRaises(ValueError):m.expected_sensitivity(p,a,v)
 def test_duplicate_fixed_job_rejected(self):
  p,a,v=fixture();p["jobs"].append(copy.deepcopy(p["jobs"][0]))
  with self.assertRaises(ValueError):m.expected_sensitivity(p,a,v)
 def test_AF2_model_duplicate_rejected(self):
  p,a,v=fixture();j=next(j for j in p["jobs"]if j["engine"]=="af2");j["slots"][-1]=j["slots"][0]
  with self.assertRaises(ValueError):m.expected_sensitivity(p,a,v)
 def test_boltz_seed_changed_rejected(self):
  p,a,v=fixture();p["jobs"][0]["slots"][0]["seed"]=31014
  with self.assertRaises(ValueError):m.expected_sensitivity(p,a,v)
 def test_new_synthetic_sensitivity_forbidden(self):
  p,a,v=fixture();j=copy.deepcopy(p["jobs"][-2]);j.update(blind_id="N6",target_id="T6",engine="boltz",variant="single_sensitivity")
  with self.assertRaises(ValueError):m.expected_sensitivity(dict(p,jobs=p["jobs"]+[j]),a,v)
 def test_seven_controls_required(self):
  p,a,v=fixture();v["controls"].pop()
  with self.assertRaises(ValueError):m.expected_sensitivity(p,a,v)
 def test_uniform_minimum_hash_sensitive(self):
  p,a,v=fixture();p["entities"].append(dict(blind_id="D0",target_id="T0"))
  v["members"]=[dict(blind_id="D0",cohort="uniform_all_complete",task_id="t",sampling_key="00",sequence_sha256="aa")]
  for engine in("boltz","af2"):
   j=copy.deepcopy(next(j for j in p["jobs"]if j["engine"]==engine and j["variant"]=="primary"));j.update(blind_id="D0",job_key="D0_"+engine);p["jobs"].append(j)
  j=copy.deepcopy(p["jobs"][2]);j.update(blind_id="D0",job_key="D0_single");p["jobs"].append(j)
  self.assertIn("D0",m.expected_sensitivity(p,a,v)["sensitive_blind_ids"])
 def test_uniform_missing_sensitivity_rejected(self):
  p,a,v=fixture();p["entities"].append(dict(blind_id="D0",target_id="T0"));v["members"]=[dict(blind_id="D0",cohort="uniform_all_complete",task_id="t",sampling_key="00",sequence_sha256="aa")]
  for engine in("boltz","af2"):
   j=copy.deepcopy(next(j for j in p["jobs"]if j["engine"]==engine and j["variant"]=="primary"));j.update(blind_id="D0",job_key="D0_"+engine);p["jobs"].append(j)
  with self.assertRaises(ValueError):m.expected_sensitivity(p,a,v)
 def test_native_top_rank_alone_not_sensitive(self):
  p,a,v=fixture();p["entities"].append(dict(blind_id="D0",target_id="T0"));v["members"]=[dict(blind_id="D0",cohort="native_fixed_top_k",task_id="t",sampling_key="00",sequence_sha256="aa")]
  for engine in("boltz","af2"):
   j=copy.deepcopy(next(j for j in p["jobs"]if j["engine"]==engine and j["variant"]=="primary"));j.update(blind_id="D0",job_key="D0_"+engine);p["jobs"].append(j)
  self.assertNotIn("D0",m.expected_sensitivity(p,a,v)["sensitive_blind_ids"])
 def test_relative_file_allowed(self):self.assertEqual(m.safe_relative("af2/complex.a3m"),Path("af2/complex.a3m"))
 def test_relative_parent_forbidden(self):
  with self.assertRaises(ValueError):m.safe_relative("../outside")
 def test_absolute_file_forbidden(self):
  with self.assertRaises(ValueError):m.safe_relative("/outside")
 def test_actual_shared_gpu3_policy(self):
  with patch.dict(os.environ,dict(OMP_NUM_THREADS="4",CUDA_VISIBLE_DEVICES="GPU-3")):self.assertEqual(m.gpu_resources(allocation())["owned_gpu_guard"]["owned_gpu_uuids"],["GPU-3"])
 def test_cpu4_rejected(self):
  a=allocation();a["selected_scheduler_record"]=a["selected_scheduler_record"].replace("NumCPUs=3","NumCPUs=4")
  with patch.dict(os.environ,dict(OMP_NUM_THREADS="4",CUDA_VISIBLE_DEVICES="GPU-3")):
   with self.assertRaises(ValueError):m.gpu_resources(a)
 def test_nonrunning_rejected(self):
  a=allocation();a["selected_scheduler_record"]=a["selected_scheduler_record"].replace("RUNNING","PENDING")
  with patch.dict(os.environ,dict(OMP_NUM_THREADS="4",CUDA_VISIBLE_DEVICES="GPU-3")):
   with self.assertRaises(ValueError):m.gpu_resources(a)
 def test_memory_not_declared_zero(self):
  a=allocation();a["selected_scheduler_record"]=a["selected_scheduler_record"].replace("MinMemoryNode=64G","MinMemoryNode=32G")
  with patch.dict(os.environ,dict(OMP_NUM_THREADS="4",CUDA_VISIBLE_DEVICES="GPU-3")):
   with self.assertRaises(ValueError):m.gpu_resources(a)
 def test_UUID_remap_required(self):
  with patch.dict(os.environ,dict(OMP_NUM_THREADS="4",CUDA_VISIBLE_DEVICES="0")):
   with self.assertRaises(ValueError):m.gpu_resources(allocation())
 def test_hardware_memory_exact(self):
  a=allocation();a["owned_gpu_guard"]["hardware"]["gpus"][0]["memory_total_mib"]=81920
  with patch.dict(os.environ,dict(OMP_NUM_THREADS="4",CUDA_VISIBLE_DEVICES="GPU-3")):
   with self.assertRaises(ValueError):m.gpu_resources(a)
 def test_OMP_literal4_required(self):
  with patch.dict(os.environ,dict(OMP_NUM_THREADS="3",CUDA_VISIBLE_DEVICES="GPU-3")):
   with self.assertRaises(ValueError):m.gpu_resources(allocation())
 def test_sacct_steps_ignored_full_failed_cost(self):
  text="777|777|COMPLETED|0||a|b|c\n777_2|778|FAILED|15|cpu=3,gres/gpu=1|a|b|n\n777_2.batch|778.batch|FAILED|15|cpu=3|a|b|n\n777_4|777|COMPLETED|20|cpu=3,gres/gpu=1|a|b|n\n"
  r=m.scheduler_rows(text,"777",[2,4]);self.assertEqual(sum(x["actual_GPU_seconds"]for x in r),35)
 def test_sacct_pending_zero_cancel(self):
  r=m.scheduler_rows("777_2|778|CANCELLED|0||Unknown|Unknown|None\n","777",[2]);self.assertEqual(r[0]["actual_GPU_seconds"],0)
 def test_sacct_nonterminal_rejected(self):
  with self.assertRaises(ValueError):m.scheduler_rows("777_2|778|RUNNING|3|cpu=3,gres/gpu=1|a|b|n\n","777",[2])
 def test_sacct_duplicate_physical_cost_rejected(self):
  with self.assertRaises(ValueError):m.scheduler_rows("777_2|778|COMPLETED|3|cpu=3,gres/gpu=1|a|b|n\n777_4|778|COMPLETED|3|cpu=3,gres/gpu=1|a|b|n\n","777",[2,4])
 def test_sacct_missing_slot_rejected(self):
  with self.assertRaises(ValueError):m.scheduler_rows("777_2|778|FAILED|3|cpu=3,gres/gpu=1|a|b|n\n","777",[2,4])
 def test_sacct_extra_allocated_slot_rejected(self):
  with self.assertRaises(ValueError):m.scheduler_rows("777_3|778|FAILED|3|cpu=3,gres/gpu=1|a|b|n\n","777",[2])
 def test_sacct_nonshared_cpu_rejected(self):
  with self.assertRaises(ValueError):m.scheduler_rows("777_2|778|FAILED|3|cpu=4,gres/gpu=1|a|b|n\n","777",[2])
 def test_submission_exact_pending_array(self):
  s,r,p=submission();self.assertEqual(m.submission_contract(s,r,p)[0],"777")
 def test_submission_cache_index_not_rerun(self):
  s,r,p=submission();s["indices"].append(0)
  with self.assertRaises(ValueError):m.submission_contract(s,r,p)
 def test_submission_cap3_forbidden(self):
  s,r,p=submission();s["submit_argv"][3]="--array=2,4%3"
  with self.assertRaises(ValueError):m.submission_contract(s,r,p)
 def test_submission_wrong_entry_forbidden(self):
  s,r,p=submission();s["entry"]=dict(path="/mutable.py",bytes=1,sha256="bad")
  with self.assertRaises(ValueError):m.submission_contract(s,r,p)
 def test_GPU_cached_index_forbidden_before_model(self):
  with self.assertRaises(ValueError):m.gpu_plan(sourcepre(),0)
 def test_unique_receipts_contract(self):
  with self.assertRaises(ValueError):m.by([{"key":"x"},{"key":"x"}],lambda x:x["key"])

import intrinsic_clearance as physical
def atom(serial,chain,residue,x,name="CA",element="C",alt="",resnum=1):
 return f"ATOM  {serial:5d} {name:>4s}{alt:1s}{residue:>3s} {chain}{resnum:4d}    {x:8.3f}{0.:8.3f}{0.:8.3f}{1.:6.2f}{90.:6.2f}          {element:>2s}\n"
def pdb(distance):
 return atom(1,"A","ALA",0.)+atom(2,"B","GLY",distance)
def stat_fixture():
 lib=m.load("successor_statistics_fixture",m.PINS["statistics"])
 p=dict(protocol_id="SOFTWARE_FIXTURE",targets=[dict(target_id="T"+str(i),analysis_role="primary"if i<6 else"diagnostic")for i in range(7)],methods=[dict(method_id="rf_diffusion"),dict(method_id="bindcraft")],replicate_seeds=[21011,21012],budget_gpu_seconds=3600,sampling=dict(uniform_n_per_replicate=3,native_top_k_per_replicate=2))
 tasks=lib.expected_tasks(p);plan=dict(status="FROZEN_BEFORE_GENERATION",protocol=p,tasks=tasks)
 cov=[dict(task=t,uniform_all_complete=dict(requested=3,selected=0,underfilled=True),native_fixed_top_k=dict(requested=2,selected=0,underfilled=True))for t in tasks]
 return lib,plan,dict(coverage=cov,selected=[]),dict(cohort_summaries=[])
class V2Contracts(unittest.TestCase):
 def test_exact_preflight_argument_required(self):
  s,r,p=submission();s["submit_argv"][-1]="/different.json"
  with self.assertRaises(ValueError):m.submission_contract(s,r,p)
 def test_resource_override_forbidden(self):
  s,r,p=submission();s["submit_argv"].insert(2,"--cpus-per-task=4")
  with self.assertRaises(ValueError):m.submission_contract(s,r,p)
 def test_duplicate_array_override_forbidden(self):
  s,r,p=submission();s["submit_argv"].insert(2,"--array=2%1")
  with self.assertRaises(ValueError):m.submission_contract(s,r,p)
 def test_dependency_declared_exact(self):
  s,r,p=submission();s["dependency"]="afterany:12:13_2";s["submit_argv"].insert(3,"--dependency=afterany:12:13_2")
  self.assertEqual(m.submission_contract(s,r,p)[0],"777")
 def test_start_preflight_pointer_exact(self):
  pre=sourcepre();pr=dict(path="/preflight.json",bytes=1,sha256="c");job={"job_key":"x"}
  start=dict(index=2,job=job,preflight_path="/different.json",successor_entry_path=str(m.SELF),source_receipts=pre["source"],neural_worker_source=m.PINS["common"])
  with self.assertRaises(ValueError):m.start_contract(start,2,pr,pre,job)
 def test_start_source_exact(self):
  pre=sourcepre();pr=dict(path="/preflight.json",bytes=1,sha256="c");job={"job_key":"x"}
  start=dict(index=2,job=job,preflight_path=pr["path"],successor_entry_path="/mutable.py",source_receipts=pre["source"],neural_worker_source=m.PINS["common"])
  with self.assertRaises(ValueError):m.start_contract(start,2,pr,pre,job)
 def test_bad_resource_numeric_cost_still_parseable(self):
  r=m.scheduler_rows("777_2|778|FAILED|7|cpu=4,gres/gpu=2|a|b|n\n","777",[2],resource_strict=False)
  self.assertEqual(r[0]["actual_GPU_seconds"],14)
 def test_physical_2A_continuous(self):
  r=physical.observe(pdb(2.),"A","G");self.assertEqual(r["minimum_distance_A"],2.);self.assertFalse(r["severe_lt_1p5_A"])
 def test_physical_strict_boundary_not_severe(self):self.assertFalse(physical.observe(pdb(1.5),"A","G")["severe_lt_1p5_A"])
 def test_physical_below_boundary_severe(self):self.assertTrue(physical.observe(pdb(1.499),"A","G")["severe_lt_1p5_A"])
 def test_physical_coincident_zero_not_missing(self):self.assertEqual(physical.observe(pdb(0.),"A","G")["minimum_distance_A"],0.)
 def test_physical_H_D_exclusion(self):
  r=physical.observe(pdb(2.)+atom(3,"B","GLY",0.1,name="H",element="H")+atom(4,"B","GLY",0.2,name="D",element="D"),"A","G")
  self.assertEqual((r["minimum_distance_A"],r["excluded_H_D_atoms"]),(2.,2))
 def test_physical_altloc_ambiguity_rejected(self):
  with self.assertRaises(ValueError):physical.observe(atom(1,"A","ALA",0.,alt="A")+atom(2,"B","GLY",2.),"A","G")
 def test_physical_duplicate_atom_rejected(self):
  with self.assertRaises(ValueError):physical.observe(pdb(2.)+atom(3,"B","GLY",3.),"A","G")
 def test_physical_multi_MODEL_rejected(self):
  with self.assertRaises(ValueError):physical.observe("MODEL        1\n"+pdb(2.)+"ENDMDL\nMODEL        2\n"+pdb(2.)+"ENDMDL\n","A","G")
 def test_physical_nonfinite_rejected(self):
  with self.assertRaises(ValueError):physical.observe(pdb(float("nan")),"A","G")
 def test_physical_full_query_mismatch_rejected(self):
  with self.assertRaises(ValueError):physical.observe(pdb(2.),"G","G")
 def test_physical_empty_chain_rejected(self):
  with self.assertRaises(ValueError):physical.observe(atom(1,"A","ALA",0.),"A","G")
 def test_physical_missing_CA_rejected(self):
  with self.assertRaises(ValueError):physical.observe(atom(1,"A","ALA",0.,name="N",element="N")+atom(2,"B","GLY",2.),"A","G")
 def test_physical_fixed_unresolved_denominator(self):
  plan=dict(entities=[dict(blind_id="b",target_sequence="A",binder_sequence="G")],jobs=[dict(job_key="j",blind_id="b",engine="boltz",variant="primary",expected_models=3,slots=[dict(seed=s,model=0)for s in(1,2,3)])])
  def missing(*args):raise FileNotFoundError("Fixture missing PDB")
  with tempfile.TemporaryDirectory()as td:
   r=physical.diagnose(plan,None,td,missing,lambda p:None,lambda r:None,Path(td)/"physical.json",{"path":"/software_fixture.py"})
  self.assertEqual((len(r["rows"]),r["n_typed_unresolved"]),(3,3));self.assertTrue(all(x["minimum_distance_A"]is None and x["severe_lt_1p5_A"]is None for x in r["rows"]))
 def test_existing_statistics_all112_empty_null(self):
  lib,plan,cohorts,common=stat_fixture();r=lib.statistics(common,plan,cohorts,"rf_diffusion","bindcraft")
  self.assertEqual((r["n_cohort_engine_rows"],r["n_empty_cohort_engine_rows"]),(112,112))
  self.assertTrue(all(x["quality_R1"]is None for x in r["flat_cohort_engine_rows"]));self.assertTrue(all(x["paired_macro_mean_RF_minus_BindCraft"]is None for x in r["comparisons"]))
 def test_existing_statistics_partial_outcome_null(self):
  lib,plan,cohorts,common=stat_fixture();t=plan["tasks"][0];cohorts["coverage"][0]["uniform_all_complete"].update(selected=1);cohorts["selected"]=[dict(task_id=t["task_id"],cohort="uniform_all_complete",cohort_record_id="fixture1")]
  for engine,nmodel in(("boltz",3),("af2",5)):
   summary=dict(n_expected=1,n_observed=1,n_valid=0,n_missing=1,median=None)
   common["cohort_summaries"].append(dict(target_id=t["target_id"],method_id=t["method_id"],seed=t["seed"],cohort="uniform_all_complete",engine=engine,n_selected=1,n_R1_complete=0,R1_candidates=summary,R0_candidates=summary,model_coverage=dict(expected=nmodel,valid=0)))
  r=lib.statistics(common,plan,cohorts,"rf_diffusion","bindcraft")
  self.assertEqual(r["n_cohort_engine_rows"],112);self.assertEqual(r["n_missing_selected_outcome_rows"],2)
  self.assertTrue(all(x["paired_macro_mean_RF_minus_BindCraft"]is None for x in r["comparisons"]))
 def test_existing_independent_AF2_partial_config_blocks(self):
  # Real accepted independent API; explicit authority containment does not rely on TMPDIR.
  with tempfile.TemporaryDirectory(dir=m.R/"steps/24_benchmark_delivery/tmp",prefix="successor_AF2_fixture_")as td:
   base=Path(td);logical=base/"logical";logical.mkdir()
   def put(name,obj):
    p=logical/name;p.write_text(json.dumps(obj));return m.rec(p)
   inputp=logical/"complex.a3m";inputp.write_text(">query\nA:G\n")
   ref=logical/"reference.pdb";ref.write_text(pdb(2.))
   slots=[dict(seed=31021,model=i)for i in(1,2,3,4,5)]
   job=dict(job_key="fixture_AF2",blind_id="b",target_id="T",engine="af2",variant="primary",expected_models=5,slots=slots,input=m.rec(inputp))
   plan=dict(settings={},jobs=[job],entities=[dict(blind_id="b",target_id="T",target_sequence="A",binder_sequence="G")])
   pr=put("plan.json",plan);ar=put("analysis.json",dict(inference_plan=pr,targets=[dict(target_id="T",reference_complex=m.rec(ref))],native_recovery_controls=[]))
   mr=put("membership.json",dict(inference_plan=pr,members=[]))
   wr=put("worker.json",dict(settings={}))
   scored=dict(plan=pr,analysis_plan=ar,results=[dict(job_key="fixture_AF2",worker_record=wr,protocol_files=[],models=[dict(slot=s,status="MODEL_UNRESOLVED",R0=None,R1=None,reason="Fixture missing config")for s in slots])])
   sr=put("score.json",scored);cr=put("accepted.json",dict(cohort_summaries=[]))
   cfg=dict(result=sr["path"],analysis_plan=ar["path"],membership=mr["path"],producer_acceptance=cr["path"],official_ipsae=m.rec(Path(m.PINS["common"]["path"]).parent/"vendor/ipsae.py"),msa_roundtrip_source=m.rec(Path(m.PINS["common"]["path"]).parent/"control_msa_check.py"),colabfold_cpu_python=str(m.R/"env/colabfold/bin/python"))
   tree=base/"restore";m.independent_copy_tree(cfg,plan,json.loads(Path(ar["path"]).read_text()),scored,tree)
   lib=m.load("successor_partial_independent_fixture",m.PINS["independent"])
   with self.assertRaises(FileNotFoundError):lib.audit_common(cfg,str(m.R),str(tree),tree/"recomputed",None)

class V3Contracts(unittest.TestCase):
 def test_missing_worker_physical_not_qualified(self):
  plan=dict(entities=[dict(blind_id="b",target_sequence="A",binder_sequence="G")],jobs=[dict(job_key="j",blind_id="b",engine="boltz",variant="primary",expected_models=1,slots=[dict(seed=1,model=0)])])
  def missing(*a):raise FileNotFoundError("Fixture missing")
  with tempfile.TemporaryDirectory()as td:r=physical.diagnose(plan,None,td,missing,lambda p:None,lambda r:None,Path(td)/"p.json",{"path":"/fixture"},None)
  self.assertEqual(r["rows"][0]["source_qualification"],"UNRESOLVED_WORKER_LINEAGE_COORDINATES_ONLY")
 def test_physical_qualified_map_explicit(self):
  plan=dict(entities=[dict(blind_id="b",target_sequence="A",binder_sequence="G")],jobs=[dict(job_key="j",blind_id="b",engine="boltz",variant="primary",expected_models=1,slots=[dict(seed=1,model=0)])])
  def missing(*a):raise FileNotFoundError("Fixture missing")
  with tempfile.TemporaryDirectory()as td:r=physical.diagnose(plan,None,td,missing,lambda p:None,lambda r:None,Path(td)/"p.json",{"path":"/fixture"},{"j":"PASSED_EXACT_CPU_NATIVE_CACHE_SOURCE_AND_SLOT_BINDING"})
  self.assertEqual(r["rows"][0]["source_qualification"],"PASSED_EXACT_CPU_NATIVE_CACHE_SOURCE_AND_SLOT_BINDING")
  self.assertIsNone(r["rows"][0]["minimum_distance_A"])
