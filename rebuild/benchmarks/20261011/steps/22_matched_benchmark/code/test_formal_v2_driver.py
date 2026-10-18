#!/usr/bin/env python3
import importlib.util,json,os,sys,unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");C=R/"steps/22_matched_benchmark/code"
S=C/"formal_contract_v2_preparation";sys.path.insert(0,str(S))
import formal_benchmark_contract as f
allocation=f.cpu_guard()
if os.environ.get("CUDA_VISIBLE_DEVICES","")not in("","NoDevFiles","-1"):raise ValueError("CPU0 contracts only")
D=C/("formal_contract_v2_tests_"+os.environ["SLURM_JOB_ID"]);D.mkdir()
spec=importlib.util.spec_from_file_location("formal2tests",S/"test_formal_benchmark_contract.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
report={"status":"INDEPENDENT_FORMAL_V2_METADATA_COMBINATION_CONTRACTS_PASS"if result.wasSuccessful()else"CONTRACT_FAILURE",
"allocation":allocation,"tests_run":result.testsRun,"errors":len(result.errors),"failures":len(result.failures),
"source":f.receipt(S/"formal_benchmark_contract.py"),"contracts":f.receipt(S/"test_formal_benchmark_contract.py"),
"reviewed_root_builder":f.receipt(C/"combine_engineering_acceptance_v1.py"),"reviewed_root_engineering_helper":f.receipt(C/"freeze_engineering_pilot_v5.py"),
"reviewed_root_formal_helper":f.receipt(C/"freeze_formal_benchmark_v3.py"),"no_gpu_submission":True,"no_formal_freeze":True,
"scope":"Software-only synthetic receipt fixtures; no generation or scientific acceptance."}
out=D/"acceptance.json";out.write_text(json.dumps(report,indent=2)+"\n");out.chmod(0o444);D.chmod(0o555)
print(json.dumps({"status":report["status"],"tests":result.testsRun,"receipt":f.receipt(out)},indent=2))
raise SystemExit(0 if result.wasSuccessful()else 1)

