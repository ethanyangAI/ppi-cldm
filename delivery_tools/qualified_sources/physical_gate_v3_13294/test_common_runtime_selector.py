import unittest
import patch_common_runtime_selector as a
P=str(a.R/"steps/24_benchmark_delivery/runs/generic_runtime_repair_13300/frozen/runtime_override")
class SelectorContracts(unittest.TestCase):
 def test_only_selector_changes(self):
  text="unchanged\n"+a.OLD+"\nunchanged-after\n";new,p=a.patch(text,P)
  self.assertEqual(new.replace(p["new_selector"],a.OLD),text)
 def test_duplicate_original_selector_rejected(self):
  with self.assertRaises(ValueError):a.patch(a.OLD+"\n"+a.OLD,P)
 def test_unknown_original_selector_rejected(self):
  with self.assertRaises(ValueError):a.patch("lock=unknown",P)
 def test_default_runtime_directory_rejected(self):
  with self.assertRaises(ValueError):a.patch(a.OLD,str(a.R/"source/environment"))
 def test_unrelated_runtime_alias_rejected(self):
  with self.assertRaises(ValueError):a.patch(a.OLD,str(a.R/"steps/24_benchmark_delivery/runs/other/frozen/runtime_override"))
 def test_real_cancelled_unallocated_history_accepts(self):
  row="13267|CANCELLED|0:0|0||u21111210118|u21111210118|test9_native_physical_preflight_v2|organ|"
  self.assertEqual(a.accounting(row,"13267",True)["allocated_GPUs"],0)
 def test_allocated_cancellation_cannot_be_zero_cost(self):
  row="13267|CANCELLED|0:0|20|cpu=1|u21111210118|u21111210118|test9_native_physical_preflight_v2|organ|"
  with self.assertRaises(ValueError):a.accounting(row,"13267",True)
 def test_completed_cpu_prerequisite_accepts_actual_state(self):
  row="13300|COMPLETED|0:0|10|cpu=1|u21111210118|u21111210118|test9_generic_materialized_repair|organ|"
  self.assertEqual(a.accounting(row,"13300",expected_state="COMPLETED")["state"],"COMPLETED")
 def test_wrong_cpu_owner_rejected(self):
  row="13300|RUNNING|0:0|1|cpu=1|other|u21111210118|test9_native_physical_preflight_v3|organ|"
  with self.assertRaises(ValueError):a.accounting(row,"13300")
class QualificationContracts(unittest.TestCase):
 def case(self):
  pointer={"path":"/synthetic/manifest","bytes":1,"sha256":"a"*64}
  _,selector=a.patch(a.OLD,P)
  snapshot=dict(failed13286_13287_history=pointer,schema="physical_gate_source_snapshot.v1",base_python_source_sha256="c3d528bb6801a7a571cdd20bfd90652e397a8540a136e1f0510ef0ccc5488dde",default_common_selector_is_original=True,default_python_source_sha256_without_staged_runtime_selector="b"*64,staged_runtime_selector=selector,runtime_override_inputs=pointer,reviewed_runtime_override_acceptance=pointer)
  pre=dict(failed13286_13287_history=pointer,schema="REFERENCE_FREE_E2E_PHYSICAL_GATE_PREFLIGHT_AND_CPU_REQUALIFICATION_V3",status="CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED",GPU_allocated=0,native_inference_performed=False,contracts_count=57,source_manifest=pointer,default_python_source_sha256_without_staged_runtime_selector="b"*64,staged_runtime_selector=selector,runtime_override_inputs=pointer,reviewed_runtime_override_acceptance=pointer,generic_report_repair_acceptance=pointer,materialization_acceptance=pointer,qualified_prediction={"status":"POSE_ACCEPTED"})
  contracts=dict(status="PASS",tests=57,compiled_source=True,bash_syntax=True,source_manifest=pointer,suites=[dict(suite=n,tests=k,returncode=0)for n,k in (("physical",25),("resource",9),("design",8),("staged_selector",15))])
  inputs=dict(failed13286_13287_history=pointer,runtime_override_acceptance=pointer,generic_repair_acceptance=pointer,materialization_acceptance=pointer)
  return pre,snapshot,contracts,inputs
 def test_exact_v3_source_contract_accepts(self):self.assertTrue(a.qualification_contract(*self.case()))
 def test_legacy_status_only_cannot_qualify(self):
  pre,s,c,i=self.case();pre["schema"]="V2"
  with self.assertRaises(ValueError):a.qualification_contract(pre,s,c,i)
 def test_contract_count_and_exit_are_required(self):
  pre,s,c,i=self.case();c["suites"][0]["returncode"]=1
  with self.assertRaises(ValueError):a.qualification_contract(pre,s,c,i)
 def test_staged_default_identity_mismatch_rejected(self):
  pre,s,c,i=self.case();pre["default_python_source_sha256_without_staged_runtime_selector"]="c"*64
  with self.assertRaises(ValueError):a.qualification_contract(pre,s,c,i)
 def test_runtime_receipt_fork_rejected(self):
  for field in ("runtime_override_acceptance","failed13286_13287_history"):
   with self.subTest(field=field):
    pre,s,c,i=self.case();i[field]={"path":"/synthetic/other","bytes":1,"sha256":"a"*64}
    with self.assertRaises(ValueError):a.qualification_contract(pre,s,c,i)
  pre,s,c,i=self.case();pre.pop("failed13286_13287_history")
  with self.assertRaises(ValueError):a.qualification_contract(pre,s,c,i)
 def test_incomplete_pose_cannot_be_terminal(self):
  pre,s,c,i=self.case();pre["qualified_prediction"]["status"]="UNRESOLVED"
  with self.assertRaises(ValueError):a.qualification_contract(pre,s,c,i)
if __name__=="__main__":unittest.main()
