#!/usr/bin/env python3
"""Prepared substantive contracts; executed only in reviewed organ pureCPU barrier."""
import copy,json,os,tempfile,unittest
from pathlib import Path
import science13263_content_barrier as a
def report():
 lines=[" ".join(a.LABELS)]
 source=scores();pairs={(x["target_id"],x["engine"]):x for x in source["results"]}
 for target,label in a.TABLE_LABELS.items():
  b=pairs[(target,"boltz")];f=pairs[(target,"af2")];d1=b["models"][0]["geometry"]["known_partner_target_aligned_CA_RMSD_A"];d2=f["models"][0]["geometry"]["known_partner_target_aligned_CA_RMSD_A"]
  counts="3/3；5/5"if target in a.PASS_TARGETS else"0/3；0/5"
  lines.append("| "+label+" | "+f'{b["models"][0]["R1"]:.3f}'+" | "+f'{f["models"][0]["R1"]:.3f}'+" | "+f'{d1:.3f}'+" | "+f'{d2:.3f}'+" | "+counts+" |")
 return "\n".join(lines)
def scores():
 rows=[]
 for ix,t in enumerate(sorted(a.TARGETS)):
  for e in ("boltz","af2"):
   n=3 if e=="boltz"else 5;d=(1.0 if t in a.PASS_TARGETS else 10.0+ix)+(0.1 if e=="af2"else 0.0);r1=0.2+ix*.07+(.001 if e=="af2"else 0)
   rows.append({"target_id":t,"engine":e,"variant":"primary","models":[{"status":"VALID","R1":r1,"geometry":{"known_partner_target_aligned_CA_RMSD_A":d,"contact_target_residue_F1":.6}}for _ in range(n)]})
 return {"results":rows}
def batch(receipts=None):
 return "#!/bin/sh\n# This script was created by sbatch --wrap.\n\npython - <<'SCIENCE_CPU_QA'\nimport os\nassert not os.environ.get(\"CUDA_VISIBLE_DEVICES\")\nreceipts="+repr(a.RECEIPTS if receipts is None else receipts)+"\nprint(\"SCIENCE_REPORT_QA_AND_ENGINEERING_E2E_INPUT_PREFLIGHT_PASS_NOT_GPU_EXECUTED\")\n\nSCIENCE_CPU_QA\n"
def stdout(rows=None):
 rows=rows or a.native_rows(scores(),report())
 s=["CURRENT_RECEIPT_SHA_PASS "+rel+" 11 "+sha for rel,sha in a.RECEIPTS.items()]
 s+=["REPORT_NATIVE_NUMERIC_PASS "+r["target_id"]+" "+r["engine"]+" "+str(r["R1_median"])+" "+str(r["partner_CA_RMSD_median_A"])+" "+str(r["strict_count"])+" "+str(r["model_count"])for r in rows]
 s+=["REPORT_RECEIPT "+str(a.R/a.REPORT)+" 22 "+"b"*64,"EXACT_OLD_PREDICTED_INPUT_AND_NATIVE_MODEL0_CHAIN_PASS /exact/model0.pdb","CURRENT_GENERIC_SOURCE "+json.dumps({"python_source_sha256":a.BASE})]
 s+=["CURRENT_RUNTIME_LOCK_PASS "+c for c in ("core","rfd","boltz")]
 s+=["SCIENCE_REPORT_QA_AND_ENGINEERING_E2E_INPUT_PREFLIGHT_PASS_NOT_GPU_EXECUTED"]
 return "\n".join(s)
def accounting(state="COMPLETED",exitcode="0:0",tres="cpu=1,mem=4G,node=1,billing=1",jid="13263",user="u21111210118",name="test9_science_report_preflight",partition="organ"):
 return "|".join((jid,state,exitcode,"12",tres,user,"u21111210118",name,partition))+"|\n"
def config():
 return {"structure":{"mode":"predict_only"},"design":{"backbones":1,"sequences_per_backbone":1,"binder_length":65,"seed":42,"temperature":.1},"refold":{"seed":1042,"samples":3}}
class ContentContracts(unittest.TestCase):
 def test_full_native14_accepts(self):self.assertEqual(len(a.native_rows(scores(),report())),14)
 def test_missing_native_slot_rejected(self):
  x=scores();x["results"].pop()
  with self.assertRaises(ValueError):a.native_rows(x,report())
 def test_duplicate_native_slot_rejected(self):
  x=scores();x["results"][-1]=copy.deepcopy(x["results"][0])
  with self.assertRaises(ValueError):a.native_rows(x,report())
 def test_unknown_engine_rejected(self):
  x=scores();x["results"][0]["engine"]="third"
  with self.assertRaises(ValueError):a.native_rows(x,report())
 def test_unknown_target_rejected(self):
  x=scores();x["results"][0]["target_id"]="OTHER"
  with self.assertRaises(ValueError):a.native_rows(x,report())
 def test_three_boltz_models_required(self):
  x=scores();x["results"][0]["models"].pop()
  with self.assertRaises(ValueError):a.native_rows(x,report())
 def test_five_af2_models_required(self):
  x=scores();x["results"][1]["models"].pop()
  with self.assertRaises(ValueError):a.native_rows(x,report())
 def test_nonvalid_model_rejected(self):
  x=scores();x["results"][0]["models"][0]["status"]="UNRESOLVED"
  with self.assertRaises(ValueError):a.native_rows(x,report())
 def test_nonfinite_r1_rejected(self):
  x=scores();x["results"][0]["models"][0]["R1"]=float("nan")
  with self.assertRaises(ValueError):a.native_rows(x,report())
 def test_invalid_f1_rejected(self):
  x=scores();x["results"][0]["models"][0]["geometry"]["contact_target_residue_F1"]=1.1
  with self.assertRaises(ValueError):a.native_rows(x,report())
 def test_fixed_strict_failure_target_rejected(self):
  x=scores();row=next(r for r in x["results"]if r["target_id"]=="KEAP1_2FLU")
  row["models"][0]["geometry"]["known_partner_target_aligned_CA_RMSD_A"]=1.5
  with self.assertRaises(ValueError):a.native_rows(x,report())
 def test_fixed_strict_success_target_rejected(self):
  x=scores();row=next(r for r in x["results"]if r["target_id"]=="MDM2_1YCR")
  row["models"][0]["geometry"]["contact_target_residue_F1"]=.4
  with self.assertRaises(ValueError):a.native_rows(x,report())
 def test_report_labels_required(self):
  with self.assertRaises(ValueError):a.native_rows(scores(),report().replace("MPNN proposals",""))
 def test_report_formatted_numbers_required(self):
  with self.assertRaises(ValueError):a.native_rows(scores(),report().replace("10.000",""))
 def test_original_receipts_ast_accepts(self):self.assertIn("receipts",a.embedded_receipts(batch()))
 def test_original_thirteen_ast_wrong_pin_rejected(self):
  x=dict(a.RECEIPTS);x[a.PRED]="a"*64
  with self.assertRaises(ValueError):a.embedded_receipts(batch(x))
 def test_original_thirteen_ast_missing_rejected(self):
  x=dict(a.RECEIPTS);x.pop(a.PRED)
  with self.assertRaises(ValueError):a.embedded_receipts(batch(x))
 def test_original_wrap_header_required(self):
  with self.assertRaises(ValueError):a.embedded_receipts(batch().replace("#!/bin/sh","#!/bin/bash"))
 def test_original_log_full_content_accepts(self):
  self.assertTrue(a.original_stdout(stdout(),a.native_rows(scores(),report()))["full_check_evidence"])
 def test_marker_only_log_rejected(self):
  with self.assertRaises(ValueError):a.original_stdout("SCIENCE_REPORT_QA_AND_ENGINEERING_E2E_INPUT_PREFLIGHT_PASS_NOT_GPU_EXECUTED",[])
 def test_original_log_missing_receipt_rejected(self):
  with self.assertRaises(ValueError):a.original_stdout("\n".join(stdout().splitlines()[1:]),a.native_rows(scores(),report()))
 def test_original_log_duplicate_receipt_rejected(self):
  with self.assertRaises(ValueError):a.original_stdout(stdout()+"\n"+stdout().splitlines()[0],a.native_rows(scores(),report()))
 def test_original_log_numeric_drift_rejected(self):
  lines=stdout().splitlines();index=next(i for i,x in enumerate(lines)if x.startswith("REPORT_NATIVE_NUMERIC_PASS "));cells=lines[index].split();cells[3]="9.99";lines[index]=" ".join(cells)
  with self.assertRaises(ValueError):a.original_stdout("\n".join(lines),a.native_rows(scores(),report()))
 def test_original_log_runtime_three_required(self):
  with self.assertRaises(ValueError):a.original_stdout(stdout().replace("CURRENT_RUNTIME_LOCK_PASS rfd",""),a.native_rows(scores(),report()))
 def test_original_log_generic_c3_required(self):
  with self.assertRaises(ValueError):a.original_stdout(stdout().replace(a.BASE,"e"*64),a.native_rows(scores(),report()))
 def test_original_report_identity_path_required(self):
  with self.assertRaises(ValueError):a.original_stdout(stdout().replace(str(a.R/a.REPORT),"/other.md"),a.native_rows(scores(),report()))
 def test_original_terminal_cpu_accepts(self):self.assertEqual(a.parse_accounting(accounting(),"13263")["allocated_GPUs"],0)
 def test_original_pending_rejected(self):
  with self.assertRaises(ValueError):a.parse_accounting(accounting("PENDING"),"13263")
 def test_original_exit_zero_without_cpu_rejected(self):
  with self.assertRaises(ValueError):a.parse_accounting(accounting(tres="mem=4G"),"13263")
 def test_original_gpu_allocation_rejected(self):
  with self.assertRaises(ValueError):a.parse_accounting(accounting(tres="cpu=1,gres/gpu:a100=1"),"13263")
 def test_duplicate_sacct_row_rejected(self):
  with self.assertRaises(ValueError):a.parse_accounting(accounting()*2,"13263")
 def test_step_row_cannot_replace_allocation(self):
  with self.assertRaises(ValueError):a.parse_accounting(accounting(jid="13263.batch"),"13263")
 def test_wrong_owner_rejected(self):
  with self.assertRaises(ValueError):a.parse_accounting(accounting(user="other"),"13263")
 def test_nonnumeric_tres_rejected(self):
  with self.assertRaises(ValueError):a.parse_accounting(accounting(tres="cpu=x"),"13263")
 def test_old_fixed_model0_contract_accepts(self):a.old_config(config(),{"source":{"kind":"boltz2_predicted","model":0}})
 def test_old_alternate_model_rejected(self):
  with self.assertRaises(ValueError):a.old_config(config(),{"source":{"kind":"boltz2_predicted","model":1}})
 def test_old_seed_change_rejected(self):
  x=config();x["design"]["seed"]=43
  with self.assertRaises(ValueError):a.old_config(x,{"source":{"kind":"boltz2_predicted","model":0}})
 def test_old_budget_change_rejected(self):
  x=config();x["design"]["backbones"]=2
  with self.assertRaises(ValueError):a.old_config(x,{"source":{"kind":"boltz2_predicted","model":0}})
 def test_old_refold_change_rejected(self):
  x=config();x["refold"]["samples"]=5
  with self.assertRaises(ValueError):a.old_config(x,{"source":{"kind":"boltz2_predicted","model":0}})
 def test_runtime_lock_drift_rejected(self):
  with self.assertRaises(ValueError):a.exact_runtime({"sha":"a"},{"sha":"b"},"core")
 def test_runtime_lock_exact_accepts(self):a.exact_runtime({"sha":"a"},{"sha":"a"},"core")
 def test_real_frozen_identity_copy(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/"source.py";p.write_text("original");dst=Path(d)/"freeze"/"source.py"
   r=a.freeze(p,dst);self.assertEqual(r["original"]["sha256"],r["frozen"]["sha256"]);self.assertFalse(dst.stat().st_mode&0o222)
 def test_real_existing_freeze_not_overwritten(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/"p";p.write_text("old");q=Path(d)/"q";q.write_text("preserved")
   with self.assertRaises(ValueError):a.freeze(p,q)
   self.assertEqual(q.read_text(),"preserved")
 def test_missing_original_bytes_not_waived(self):
  with tempfile.TemporaryDirectory()as d:
   with self.assertRaises(ValueError):a.freeze(Path(d)/"absent",Path(d)/"freeze")
 def test_changed_report_identity_not_waived(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/"report";p.write_text("newreport")
   with self.assertRaises(ValueError):a.freeze(p,Path(d)/"frozen","b"*64,22)
 def test_historical_core_parent_exact(self):
  a.lock_parent_contract("core",{"source":{"python_source_sha256":a.BASE},"status":"POSE_ACCEPTED","execution":{"slurm_job_id":"11801"},"runtime":{"core":{"lock":a.HISTORICAL_LOCKS["core"]}}})
 def test_historical_boltz_parent_exact(self):
  a.lock_parent_contract("boltz",{"source":{"python_source_sha256":a.BASE},"status":"POSE_ACCEPTED","execution":{"slurm_job_id":"11801"},"runtime":{"boltz":{"lock":a.HISTORICAL_LOCKS["boltz"]}}})
 def test_historical_rfd_parent_exact(self):
  a.lock_parent_contract("rfd",{"source":{"python_source_sha256":a.BASE},"status":"DESIGNS_GENERATED","execution":{"slurm_job_id":"11728"},"runtime":{"rfd":{"lock":a.HISTORICAL_LOCKS["rfd"]}}})
 def test_historical_lock_parent_sha_drift_rejected(self):
  p={"source":{"python_source_sha256":a.BASE},"status":"DESIGNS_GENERATED","execution":{"slurm_job_id":"11728"},"runtime":{"rfd":{"lock":{**a.HISTORICAL_LOCKS["rfd"],"sha256":"a"*64}}}}
  with self.assertRaises(ValueError):a.lock_parent_contract("rfd",p)
 def test_historical_lock_origin_job_drift_rejected(self):
  p={"source":{"python_source_sha256":a.BASE},"status":"DESIGNS_GENERATED","execution":{"slurm_job_id":"999"},"runtime":{"rfd":{"lock":a.HISTORICAL_LOCKS["rfd"]}}}
  with self.assertRaises(ValueError):a.lock_parent_contract("rfd",p)
 def test_historical_lock_source_drift_rejected(self):
  p={"source":{"python_source_sha256":"e"*64},"status":"DESIGNS_GENERATED","execution":{"slurm_job_id":"11728"},"runtime":{"rfd":{"lock":a.HISTORICAL_LOCKS["rfd"]}}}
  with self.assertRaises(ValueError):a.lock_parent_contract("rfd",p)
 def test_structured_receipt_becomes_readonly(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/"receipt.json";a.dump(p,{"unit_fixture":True});self.assertFalse(p.stat().st_mode&0o222)
 def test_structured_receipt_not_overwritten(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/"receipt.json";a.dump(p,{"unit_fixture":"preserved"})
   with self.assertRaises(FileExistsError):a.dump(p,{"unit_fixture":"replacement"})
   self.assertEqual(json.loads(p.read_text())["unit_fixture"],"preserved")
 def test_explicit_invalid_job_id_allows_purge_classification(self):self.assertTrue(a.explicit_purge("slurm_load_jobs error: Invalid job id specified"))
 def test_explicit_purged_job_allows_classification(self):self.assertTrue(a.explicit_purge("Job13263 has been purged"))
 def test_permission_error_not_purge(self):self.assertFalse(a.explicit_purge("Access/permission denied"))
 def test_network_error_not_purge(self):self.assertFalse(a.explicit_purge("Unable to contact slurm controller"))
 def test_unknown_scheduler_error_not_purge(self):self.assertFalse(a.explicit_purge("Unspecified failure"))
 def test_actual_wrong_partition_rejected(self):
  with self.assertRaises(ValueError):a.parse_accounting(accounting(partition="gpu"),"13263")
 def test_prepared_scheduler_metadata_pins_accept(self):
  text="JobId=13263 JobName=test9_science_report_preflight UserId=u21111210118(6263900) Account=u21111210118 Partition=organ NumCPUs=1 CPUs/Task=1 JobState=PENDING WorkDir="+str(a.R)+" StdOut="+str(a.R/"logs/science_report_preflight_13263.out")+" StdErr="+str(a.R/"logs/science_report_preflight_13263.err")
  a.scheduler_metadata(text,False)
 def test_prepared_scheduler_metadata_resources_required(self):
  text="JobId=13263 JobName=test9_science_report_preflight UserId=u21111210118(6263900) Account=u21111210118 Partition=organ NumCPUs=2 CPUs/Task=2 JobState=PENDING WorkDir="+str(a.R)+" StdOut="+str(a.R/"logs/science_report_preflight_13263.out")+" StdErr="+str(a.R/"logs/science_report_preflight_13263.err")
  with self.assertRaises(ValueError):a.scheduler_metadata(text,False)
 def test_prepared_scheduler_state_cannot_replace_terminal_state(self):
  text="JobId=13263 JobName=test9_science_report_preflight UserId=u21111210118(6263900) Account=u21111210118 Partition=organ NumCPUs=1 CPUs/Task=1 JobState=PENDING WorkDir="+str(a.R)+" StdOut="+str(a.R/"logs/science_report_preflight_13263.out")+" StdErr="+str(a.R/"logs/science_report_preflight_13263.err")
  with self.assertRaises(ValueError):a.scheduler_metadata(text,True)
 def test_report_target_row_swap_rejected(self):
  text=report().replace("MDM2–p53","TMP").replace("KEAP1–NRF2","MDM2–p53").replace("TMP","KEAP1–NRF2")
  with self.assertRaises(ValueError):a.native_rows(scores(),text)
 def test_report_target_mislabel_rejected(self):
  with self.assertRaises(ValueError):a.native_rows(scores(),report().replace("MDM2–p53","wrong target"))
 def test_report_target_duplicate_rejected(self):
  text=report()+"\n"+next(x for x in report().splitlines()if x.startswith("| MDM2–p53 |"))
  with self.assertRaises(ValueError):a.native_rows(scores(),text)
 def test_report_target_engine_cells_swapped_rejected(self):
  lines=report().splitlines();index=next(i for i,x in enumerate(lines)if x.startswith("| MDM2–p53 |"));cells=lines[index].split("|");cells[2],cells[3]=cells[3],cells[2];lines[index]="|".join(cells)
  with self.assertRaises(ValueError):a.native_rows(scores(),"\n".join(lines))
 def test_report_target_strict_count_wrong_rejected(self):
  with self.assertRaises(ValueError):a.native_rows(scores(),report().replace("3/3；5/5","2/3；5/5",1))
 def test_report_numeric_global_occurrence_cannot_rescue_wrong_row(self):
  lines=report().splitlines();index=next(i for i,x in enumerate(lines)if x.startswith("| MDM2–p53 |"));cells=lines[index].split("|");old=cells[2].strip();cells[2]=" 0.999 ";lines[index]="|".join(cells);lines.append("Historical numeric occurrence outside target table: "+old)
  with self.assertRaises(ValueError):a.native_rows(scores(),"\n".join(lines))
 def test_prepared_actual_failed_state_is_history_only(self):
  text="JobId=13263 JobName=test9_science_report_preflight UserId=u21111210118(6263900) Account=u21111210118 Partition=organ NumCPUs=1 CPUs/Task=1 JobState=FAILED WorkDir="+str(a.R)+" StdOut="+str(a.R/"logs/science_report_preflight_13263.out")+" StdErr="+str(a.R/"logs/science_report_preflight_13263.err")
  a.scheduler_metadata(text,False,"FAILED")
  with self.assertRaises(ValueError):a.scheduler_metadata(text,True,"FAILED")

def failed_stdout():
 return "\n".join(x for x in stdout().splitlines()if x not in {"CURRENT_RUNTIME_LOCK_PASS rfd","CURRENT_RUNTIME_LOCK_PASS boltz","SCIENCE_REPORT_QA_AND_ENGINEERING_E2E_INPUT_PREFLIGHT_PASS_NOT_GPU_EXECUTED"})
def materialization():
 lock={"path":str(a.R/"steps/24_benchmark_delivery/runs/rfd_cache_materialization_13281/runtime-lock-rfd-materialized.json"),"bytes":1,"sha256":"e"*64}
 spec={"T":50,"min_sigma":.02,"max_sigma":1.5,"min_b":1.5,"max_b":2.5,"num_omega":1000,"schedule":"linear","L":2000,"cache_dir":str(a.R/"steps/24_benchmark_delivery/runs/rfd_cache_materialization_13281/independent_regenerated_schedule")}
 return {"schema":"rfd-cache-materialization.v1","status":a.MAT_STATUS,"job_id":"13281","default_lock_updated":False,"application_to_default_runtime_performed":False,"model_inference_performed":False,"GPU_allocated":0,"cause_diagnostic":a.DIAG,"single_cache_diagnostic":a.CACHE_DIAG,"original_cache":a.CACHE,"fixed_numeric_equivalence":{"rtol":1e-8,"atol":1e-8},"official_constructor_arguments":spec,"array_crosschecks":[{"key":k,"shape":[1],"dtype":"float64","max_absolute_difference":0.0,"fixed_numeric_equivalent":True}for k in ("cdf","score_norm","exp_score_norms","discrete_omega","discrete_sigma")],"original_default_lock":a.HISTORICAL_LOCKS["rfd"],"old_pre_materialization_lock_preserved":True,"baseline_vendor225_bytes_unchanged":True,"all_other_RFD_runtime_fields_unchanged":True,"core_and_boltz_captured_match_historical":True,"scientific_generation_or_selection_settings_changed":False,"source_records":[{"path":"/fixture/"+n,"bytes":1,"sha256":"a"*64}for n in ("materialization.py","diffusion.py","igso3.py","base.yaml","common.py")],"materialized_runtime_lock":lock}
def runtime_pair():
 old={"component":"rfd","environment":{"same":True},"assets":{"checkpoint":"same"},"vendor_files":{"RFdiffusion":{"path_root":"/fixture/RFdiffusion","file_count":225,"bytes":100,"tree_sha256":"a"*64},"ProteinMPNN":{"same":True},"dllogger":{"same":True}}}
 new=copy.deepcopy(old);new["vendor_files"]["RFdiffusion"].update(file_count=226,bytes=100+a.CACHE["bytes"],tree_sha256="b"*64)
 return old,new
class MaterializedRepairContracts(unittest.TestCase):
 def test_original_failed_partial_content_is_preserved(self):
  x=a.failed_original_stdout(failed_stdout(),a.native_rows(scores(),report()))
  self.assertFalse(x["full_check_evidence"]);self.assertTrue(x["original_failure_preserved"])
 def test_original_completed_stdout_cannot_claim_failed_history(self):
  with self.assertRaises(ValueError):a.failed_original_stdout(stdout(),a.native_rows(scores(),report()))
 def test_failed_history_missing_native_row_rejected(self):
  s=failed_stdout();line=next(x for x in s.splitlines()if x.startswith("REPORT_NATIVE_NUMERIC_PASS "))
  with self.assertRaises(ValueError):a.failed_original_stdout(s.replace(line,""),a.native_rows(scores(),report()))
 def test_failed_original_terminal_gpu0_accepts(self):
  x=a.terminal_repair_accounting(accounting(state="FAILED",exitcode="1:0"),"13263");self.assertEqual(x["state"],"FAILED")
 def test_original_failed_cannot_be_upgraded_to_completed(self):
  with self.assertRaises(ValueError):a.terminal_repair_accounting(accounting(),"13263")
 def test_original_failed_gpu_allocation_rejected(self):
  with self.assertRaises(ValueError):a.terminal_repair_accounting(accounting(state="FAILED",exitcode="1:0",tres="cpu=1,gres/gpu=1"),"13263")
 def test_future_materialization_pending_rejected(self):
  m=materialization();m["status"]="PENDING"
  with self.assertRaises(ValueError):a.materialization_contract(m)
 def test_actual_materialization_exact_contract_accepts(self):self.assertEqual(a.materialization_contract(materialization()),materialization()["materialized_runtime_lock"])
 def test_materialization_wrong_cache_identity_rejected(self):
  m=materialization();m["original_cache"]={**a.CACHE,"sha256":"e"*64}
  with self.assertRaises(ValueError):a.materialization_contract(m)
 def test_materialization_tolerance_relaxation_rejected(self):
  m=materialization();m["fixed_numeric_equivalence"]["atol"]=1e-2
  with self.assertRaises(ValueError):a.materialization_contract(m)
 def test_materialization_constructor_change_rejected(self):
  m=materialization();m["official_constructor_arguments"]["T"]=100
  with self.assertRaises(ValueError):a.materialization_contract(m)
 def test_materialization_missing_array_rejected(self):
  m=materialization();m["array_crosschecks"].pop()
  with self.assertRaises(ValueError):a.materialization_contract(m)
 def test_materialization_nonfinite_delta_rejected(self):
  m=materialization();m["array_crosschecks"][0]["max_absolute_difference"]=float("nan")
  with self.assertRaises(ValueError):a.materialization_contract(m)
 def test_materialization_default_lock_change_rejected(self):
  m=materialization();m["default_lock_updated"]=True
  with self.assertRaises(ValueError):a.materialization_contract(m)
 def test_only_cache_full226_fingerprint_delta_accepts(self):
  old,new=runtime_pair();self.assertTrue(a.rfd_full_delta_contract(old,new)["cache_included_not_excluded"])
 def test_cache_exclusion_from_new_lock_rejected(self):
  old,new=runtime_pair();new["vendor_files"]["RFdiffusion"]=copy.deepcopy(old["vendor_files"]["RFdiffusion"])
  with self.assertRaises(ValueError):a.rfd_full_delta_contract(old,new)
 def test_additional_unreviewed_vendor_file_rejected(self):
  old,new=runtime_pair();new["vendor_files"]["RFdiffusion"]["file_count"]=227
  with self.assertRaises(ValueError):a.rfd_full_delta_contract(old,new)
 def test_unrelated_model_checkpoint_drift_rejected(self):
  old,new=runtime_pair();new["assets"]["checkpoint"]="different"
  with self.assertRaises(ValueError):a.rfd_full_delta_contract(old,new)


class ActualArrayRepeatContracts(unittest.TestCase):
 def fixture(self):
  import numpy as np
  x={k:np.asarray([1.0,2.0],dtype="float64")for k in ("cdf","score_norm","exp_score_norms","discrete_omega","discrete_sigma")}
  rows=[{"key":k,"shape":[2],"dtype":"float64","exact_array_equal":True,"max_absolute_difference":0.0,"fixed_numeric_equivalent":True}for k in sorted(x)]
  return x,{"array_crosschecks":rows}
 def test_actual_five_numeric_arrays_and_saved_rows_accept(self):
  x,m=self.fixture();self.assertEqual(len(a.cache_arrays_contract(x,copy.deepcopy(x),m)),5)
 def test_actual_array_numerical_difference_rejected(self):
  x,m=self.fixture();y=copy.deepcopy(x);y["cdf"][0]=2.0
  with self.assertRaises(ValueError):a.cache_arrays_contract(x,y,m)
 def test_actual_nonfinite_array_rejected(self):
  x,m=self.fixture();x["cdf"][0]=float("nan")
  with self.assertRaises(ValueError):a.cache_arrays_contract(x,x,m)
 def test_saved_array_diagnostics_cannot_hide_real_dtype(self):
  x,m=self.fixture();m["array_crosschecks"][0]["dtype"]="float32"
  with self.assertRaises(ValueError):a.cache_arrays_contract(x,copy.deepcopy(x),m)


class MaterializationLineageFileContracts(unittest.TestCase):
 def fixture(self,root):
  pending=root/"steps/24_benchmark_delivery/pending/rfd_cache_materialization_v2";executed=root/"steps/24_benchmark_delivery/frozen/rfd_cache_materialization_v2_13281/code"
  pending.mkdir(parents=True);executed.mkdir(parents=True)
  for name in ("materialization.py","materialization_cpu.sbatch"):
   for directory in (pending,executed):(directory/name).write_text("toy-reviewed-source\n");(directory/name).chmod(0o444)
  submit=root/"steps/24_benchmark_delivery/submissions/rfd_cache_materialization_v2_primary_claim/submission_receipt.json";submit.parent.mkdir(parents=True)
  q={"schema":"root-pure-cpu-cache-requalification-submission.v1","job_id":"13281","argv":["sbatch","--parsable",str(pending/"materialization_cpu.sbatch")],"raw_stdout":"13281\n","raw_stderr":"","returncode":0,"requests_gpu":False,"defaultlock_changes":False,"fixed_comparison":{"rtol":1e-8,"atol":1e-8}}
  submit.write_text(json.dumps(q));submit.chmod(0o444)
  out=root/"toy_new_successor";out.mkdir()
  return pending,executed,submit,q,out,{"source_records":[a.rec(executed/"materialization.py")]}
 def test_actual_toy_two_files_submission_and_self_lineage_accepts(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory()as d,patch.object(a,"R",Path(d)):
   _,_,_,_,out,m=self.fixture(Path(d));proof=a.materialization_source_lineage(out,m)
   self.assertTrue(Path(proof["path"]).is_file())
 def test_actual_toy_executed_source_byte_drift_rejected(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory()as d,patch.object(a,"R",Path(d)):
   _,executed,_,_,out,m=self.fixture(Path(d));p=executed/"materialization.py";p.chmod(0o644);p.write_text("different\n");p.chmod(0o444)
   with self.assertRaises(ValueError):a.materialization_source_lineage(out,m)
 def test_actual_toy_root_job_argv_or_self_entry_mismatch_rejected(self):
  from unittest.mock import patch
  for mode in ("job","argv","self"):
   with self.subTest(mode=mode),tempfile.TemporaryDirectory()as d,patch.object(a,"R",Path(d)):
    _,_,submit,q,out,m=self.fixture(Path(d))
    if mode=="self":m["source_records"][0]["sha256"]="e"*64
    else:
     if mode=="job":q["job_id"]="13280"
     else:q["argv"][-1]="/wrong/script"
     submit.chmod(0o644);submit.write_text(json.dumps(q));submit.chmod(0o444)
    with self.assertRaises(ValueError):a.materialization_source_lineage(out,m)

class ZeroExitPurgeContracts(unittest.TestCase):
 def test_actual_rc0_empty_stdout_explicit_purge(self):self.assertEqual(a.scheduler_source_action(0,"","job script retrieval failed: Invalid job id specified\n",True),"SOURCE_FROM_REVIEWED_DIRECT_SCHEDULER_CAPTURE")
 def test_rc1_explicit_purge_preserves_same_policy(self):self.assertEqual(a.scheduler_source_action(1,"","slurm_load_jobs error: Invalid job id specified\n",True),"SOURCE_FROM_REVIEWED_DIRECT_SCHEDULER_CAPTURE")
 def test_fresh_exact_source_still_allowed(self):
  c={"source_status":a.scheduler_source_action(0,"same-script","",True)};a.exact_fresh_batch("same-script","same-script",c)
 def test_fresh_changed_source_rejected(self):
  with self.assertRaises(ValueError):a.exact_fresh_batch("changed","original",{"source_status":"SOURCE_FROM_CURRENT_QUERY"})
 def test_mixed_purge_and_script_rejected(self):
  with self.assertRaises(ValueError):a.scheduler_source_action(0,"#!/bin/sh\n","Invalid job id specified",True)
 def test_permission_error_no_fallback(self):
  with self.assertRaises(ValueError):a.scheduler_source_action(1,"","Permission denied",True)
 def test_zero_exit_unknown_empty_source_rejected(self):
  with self.assertRaises(ValueError):a.scheduler_source_action(0,"","Unspecified failure",True)
 def test_zero_exit_silent_empty_source_rejected(self):
  with self.assertRaises(ValueError):a.scheduler_source_action(0,"","",True)
class FailedPredecessorContracts(unittest.TestCase):
 def row(self,jid="13286",state="FAILED",tres="cpu=1",code="1:0"):
  name="test9_generic_materialized_repair"if jid=="13286"else"test9_root_receipt_capture"
  return "|".join((jid,state,code,"2",tres,"u21111210118","u21111210118",name,"organ",""))
 def test_both_actual_failed_purecpu_histories_supported(self):
  for jid in ("13286","13287"):self.assertEqual(a.failed_predecessor_accounting(self.row(jid),jid)["state"],"FAILED")
 def test_completed_cannot_upgrade_failed_predecessor(self):
  with self.assertRaises(ValueError):a.failed_predecessor_accounting(self.row(state="COMPLETED",code="0:0"),"13286")
 def test_positive_gpu_cannot_be_hidden_as_cpu_failure(self):
  with self.assertRaises(ValueError):a.failed_predecessor_accounting(self.row(tres="cpu=1,gres/gpu=1"),"13286")
if __name__=="__main__":unittest.main()
