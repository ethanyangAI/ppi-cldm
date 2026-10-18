#!/usr/bin/env python3
import hashlib,importlib.util,json,os,shutil,sys,unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");C=R/"steps/22_matched_benchmark/code";P=C/"formal_contract_v2_preparation"
sys.path.insert(0,str(P));import formal_benchmark_contract as preparation
allocation=preparation.cpu_guard()
if os.environ.get("CUDA_VISIBLE_DEVICES","")not in("","NoDevFiles","-1"):raise ValueError("CPU0 snapshot only")
D=C/"formal_contract_v2";D.mkdir();S=D/"source";S.mkdir();H=D/"history_exact_bytes";H.mkdir()
rec=preparation.receipt
for name in("formal_benchmark_contract.py","test_formal_benchmark_contract.py","FORMAL_FAIRNESS_ACCEPTANCE.md"):
 shutil.copyfile(P/name,S/name);(S/name).chmod(0o444)
for original,name in((C/"freeze_engineering_pilot_v5.py","root_freeze_engineering_pilot_v5.py"),(C/"freeze_formal_benchmark_v3.py","root_freeze_formal_benchmark_v3.py"),(C/"combine_engineering_acceptance_v1.py","root_combine_engineering_acceptance_v1.py"),(Path(__file__),"snapshot_driver.py")):
 shutil.copyfile(original,S/name);(S/name).chmod(0o444)
aliases=[];candidate=C/"formal_contract_history_candidates"
historical=[(C/"formal_contract_v2_tests_13168/acceptance.json",{"source":candidate/"source_50.py","contracts":candidate/"tests_50.py","reviewed_root_formal_helper":candidate/"root_formal_v3_old.py"}),
 (C/"formal_contract_v2_tests_13180/acceptance.json",{"source":candidate/"source_64.py","contracts":P/"test_formal_benchmark_contract.py"})]
for reportpath,mapping in historical:
 report=json.loads(reportpath.read_text())
 for key,path in mapping.items():
  expected=report[key];body=path.read_bytes().rstrip(b"\n");found=None
  for n in range(11):
   data=body+b"\n"*n
   if len(data)==expected["bytes"]and hashlib.sha256(data).hexdigest()==expected["sha256"]:found=data;break
  if found is None:raise ValueError("Cannot resolve exact historical source "+str(reportpath)+" "+key+" "+expected["sha256"])
  destination=H/(reportpath.parent.name+"_"+key+".py");destination.write_bytes(found);destination.chmod(0o444)
  aliases.append({"historical_report":rec(reportpath),"logical_receipt":expected,"resolved_readonly_exact_byte_receipt":rec(destination),"original_mutable_path_hash_claimed_equal":False})
(S/"formal_benchmark_contract.py").chmod(0o444)
sys.path.pop(0);sys.path.insert(0,str(S));sys.modules.pop("formal_benchmark_contract",None)
import formal_benchmark_contract as f
spec=importlib.util.spec_from_file_location("frozen_formal2_tests",S/"test_formal_benchmark_contract.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
report={"status":"INDEPENDENT_FORMAL_V2_ALL_NATIVE_OUTPUTS_AND112_FAIRNESS_READONLY_SOURCE_SNAPSHOT_PASS"if result.wasSuccessful()else"CONTRACT_FAILURE",
 "cpu_job_id":os.environ["SLURM_JOB_ID"],"allocation":allocation,"n_tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),
 "files":[rec(x)for x in sorted(S.iterdir())],"historical_exact_byte_aliases":aliases,
 "source":rec(S/"formal_benchmark_contract.py"),"contracts":rec(S/"test_formal_benchmark_contract.py"),"API":rec(S/"FORMAL_FAIRNESS_ACCEPTANCE.md"),
 "reviewed_root_formal_helper":rec(C/"freeze_formal_benchmark_v3.py"),"reviewed_root_builder":rec(C/"combine_engineering_acceptance_v1.py"),
 "reviewed_engineering_plan":rec(R/"steps/22_matched_benchmark/engineering_pilot/plan_v5/frozen_plan.json"),
 "independent_engineering_preflight":rec(C/"engineering_plan_v5_audit_v3_13167/acceptance.json"),
 "collector_source":f.NATIVE_COLLECTOR_RECEIPT,"runtime_source":rec(R/"steps/22_matched_benchmark/settings/pilot_v8/source/benchmark_runtime.py"),
 "no_formal_freeze":True,"no_gpu_submission":True,"no_accepted_v4_mutation":True,"no_scientific_results":"All unit input arrays/sequences/PDB/receipt objects are explicit software fixtures."}
output=D/"manifest.json";output.write_text(json.dumps(report,indent=2)+"\n");output.chmod(0o444);S.chmod(0o555);H.chmod(0o555);D.chmod(0o555)
print(json.dumps({"status":report["status"],"n_tests":result.testsRun,"source":report["source"],"contracts":report["contracts"],"manifest":rec(output)},indent=2))
raise SystemExit(0 if result.wasSuccessful()else 1)

