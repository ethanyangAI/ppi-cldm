#!/usr/bin/env python3
"""34 terminal-wrapper contracts. Stdlib, CPU only, no project input reading."""
import copy,importlib.util,unittest
from pathlib import Path
sp=importlib.util.spec_from_file_location("terminal_wrapper_under_test",Path(__file__).with_name("formal13260_terminal.py"))
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class Contracts(unittest.TestCase):
 def env(self):
  return dict(CUDA_VISIBLE_DEVICES="",PYTHONDONTWRITEBYTECODE="1",PYTHONNOUSERSITE="1",OPENBLAS_NUM_THREADS="1",JAX_PLATFORMS="cpu",SLURM_JOB_ID="9001")
 def submit(self):
  return dict(schema="paired_formal_resource_submission.v1",job_id="13260",
   submit_argv=["sbatch","--parsable",m.PINS["launcher"]["path"]],launcher=m.PINS["launcher"],resource_policy=m.PINS["policy"],plan=m.PINS["plan"],
   pre_generation_independent_gate=m.PINS["pregeneration"],current_seeded_supplemental_independent_gate=m.PINS["seeded"],
   submitted_at_epoch=101.1,root_owned_primary_array=True,global_project_gpu_concurrency_cap=2,source_settings_unchanged=True,
   raw_sbatch_stdout="13260\n",raw_sbatch_stderr="",cpu_cgroup_isolation_status="UNOBSERVED")
 def badenv(self,k,v):
  e=self.env();e[k]=v
  with self.assertRaises(ValueError):m.check_env(e,m.R/"steps/22_matched_benchmark")
 def badsubmit(self,k,v):
  s=copy.deepcopy(self.submit());s[k]=v
  with self.assertRaises(ValueError):m.check_submit(s,100.2)
 def test_01_valid_cpu_environment(self):m.check_env(self.env(),m.R/"steps/22_matched_benchmark")
 def test_02_cuda_gpu_rejected(self):self.badenv("CUDA_VISIBLE_DEVICES","0")
 def test_03_bytecode_mutation_rejected(self):self.badenv("PYTHONDONTWRITEBYTECODE","0")
 def test_04_user_site_rejected(self):self.badenv("PYTHONNOUSERSITE","0")
 def test_05_cpu_oversubscription_rejected(self):self.badenv("OPENBLAS_NUM_THREADS","4")
 def test_06_jax_gpu_backend_rejected(self):self.badenv("JAX_PLATFORMS","cuda")
 def test_07_injected_pythonpath_rejected(self):self.badenv("PYTHONPATH","/tmp/untrusted")
 def test_08_no_slurm_allocation_rejected(self):self.badenv("SLURM_JOB_ID","")
 def test_09_wrong_working_directory_rejected(self):
  with self.assertRaises(ValueError):m.check_env(self.env(),m.R)
 def test_10_valid_exact_submission(self):self.assertTrue(m.check_submit(self.submit(),100.2))
 def test_11_wrong_schema_rejected(self):self.badsubmit("schema","legacy")
 def test_12_wrong_master_rejected(self):self.badsubmit("job_id","13261")
 def test_13_any_cli_resource_override_rejected(self):
  self.badsubmit("submit_argv",["sbatch","--parsable","--cpus-per-task=4",m.PINS["launcher"]["path"]])
 def test_14_launcher_identity_rejected(self):self.badsubmit("launcher",{**m.PINS["launcher"],"sha256":"0"*64})
 def test_15_policy_identity_rejected(self):self.badsubmit("resource_policy",m.PINS["original_launcher"])
 def test_16_plan_identity_rejected(self):self.badsubmit("plan",m.PINS["protocol"])
 def test_17_pregeneration_gate_identity_rejected(self):self.badsubmit("pre_generation_independent_gate",m.PINS["seeded"])
 def test_18_corrected_seeded_gate_identity_rejected(self):self.badsubmit("current_seeded_supplemental_independent_gate",m.PINS["pregeneration"])
 def test_19_submission_timestamp_missing_rejected(self):self.badsubmit("submitted_at_epoch",None)
 def test_20_submission_before_policy_rejected(self):self.badsubmit("submitted_at_epoch",99.9)
 def test_21_root_ownership_required(self):self.badsubmit("root_owned_primary_array",False)
 def test_22_concurrency_cap_required(self):self.badsubmit("global_project_gpu_concurrency_cap",3)
 def test_23_source_settings_assertion_required(self):self.badsubmit("source_settings_unchanged",False)
 def test_24_raw_submission_id_required(self):self.badsubmit("raw_sbatch_stdout","13261\n")
 def test_25_submission_stderr_requires_review(self):self.badsubmit("raw_sbatch_stderr","scheduler error")
 def test_26_cgroup_observation_not_invented(self):self.badsubmit("cpu_cgroup_isolation_status","VERIFIED")
 def test_27_terminal_failure_is_still_collectable(self):m.check_terminal({"13261":{"state":"FAILED"}},"")
 def test_28_queued_array_blocks_collection(self):
  with self.assertRaises(ValueError):m.check_terminal({"13261":{"state":"COMPLETED"}},"13260_1|PENDING")
 def test_29_missing_scheduler_rows_blocks_collection(self):
  with self.assertRaises(ValueError):m.check_terminal({},"")
 def test_30_running_accounting_blocks_collection(self):
  with self.assertRaises(ValueError):m.check_terminal({"13261":{"state":"RUNNING"}},"")
 def test_31_pending_accounting_blocks_collection(self):
  with self.assertRaises(ValueError):m.check_terminal({"13261":{"state":"PENDING"}},"")
 def test_32_timeout_and_zero_cost_cancellation_preserved(self):
  m.check_terminal({"13261":{"state":"TIMEOUT"},"13260":{"state":"CANCELLED"}},"")
 def test_33_existing_scientific_inputs_exact_hash_not_new_readonly_rule(self):
  self.assertFalse(m.snapshot_pin_readonly("msa"));self.assertFalse(m.snapshot_pin_readonly("previous_registry"))
 def test_34_all_source_pins_remain_readonly(self):
  for key in ["resource","budget","independent","formal","native","common","unrecognized_new_pin"]:
   with self.subTest(key=key):self.assertTrue(m.snapshot_pin_readonly(key))
if __name__=="__main__":unittest.main()

