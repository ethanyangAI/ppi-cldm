#!/usr/bin/env python3
import datetime, hashlib, importlib.util, json, os, pathlib, sys, unittest
STEP=pathlib.Path("/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code")
def rec(p):
 return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
if not os.environ.get("SLURM_JOB_ID"):raise RuntimeError("Slurm CPU required")
source_path=pathlib.Path("/lustre/users/u21111210118/projects/test9/source/rebuild/paired_budget_benchmark.py")
source_before=rec(source_path)
independent_path=STEP/"paired_budget_independent.py"
independent_before=rec(independent_path)
spec=importlib.util.spec_from_file_location("paired_budget_contract_tests",STEP/"test_paired_budget_benchmark.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
tests=unittest.defaultTestLoader.loadTestsFromModule(module)
result=unittest.TextTestRunner(verbosity=2).run(tests)
source_after=rec(source_path)
independent_after=rec(independent_path)
source_unchanged=source_before==source_after and independent_before==independent_after
receipt={"status":"PAIRED_BUDGET_CPU_CONTRACT_TESTS_PASS" if result.wasSuccessful() and source_unchanged else "PAIRED_BUDGET_CPU_CONTRACT_TESTS_FAIL",
 "job_id":os.environ["SLURM_JOB_ID"],"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "n_tests":result.testsRun,"n_failures":len(result.failures),"n_errors":len(result.errors),
 "source":source_before,"source_after":source_after,"source_unchanged_during_tests":source_unchanged,
 "independent_verifier":independent_before,"independent_verifier_after":independent_after,
 "tests":rec(STEP/"test_paired_budget_benchmark.py"),"python":sys.executable,
 "scope":"Synthetic bookkeeping/process fixtures only; no GPU/model inference or scientific outcomes"}
path=STEP/("tests_"+os.environ["SLURM_JOB_ID"])/"receipt.json";path.parent.mkdir(exist_ok=True)
if path.exists():raise FileExistsError(path)
path.write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
sys.exit(0 if result.wasSuccessful() and source_unchanged else 1)

