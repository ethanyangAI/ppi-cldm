import os,sys,json,importlib.util,traceback,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
D=R/'steps/24_benchmark_delivery/frozen/source_refresh_relative_v4_13279/code'
sys.path.insert(0,str(D))
spec=importlib.util.spec_from_file_location('actual_source_v4_diagnostic',D/'source_delivery_refresh_v4.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
allocation=m.cpu()
O=R/'steps/24_benchmark_delivery/runs'/('source_receipt_path_diagnostic_'+os.environ['SLURM_JOB_ID']);O.mkdir(exist_ok=False)
def rec(p):
 return m.rec(p)
original=m.exact
calls=0
def diagnostic_exact(p,receipt):
 global calls
 calls+=1
 try:return original(p,receipt)
 except Exception as error:
  raise ValueError(json.dumps(dict(diagnostic_only=True,source_V4_guard_unchanged=True,attempted_path=str(p),attempted_receipt=receipt,original_error_type=type(error).__name__,original_error=str(error)),ensure_ascii=False)) from error
m.exact=diagnostic_exact
result=dict(schema='source-closure-exact-path-diagnostic.v1',status='DIAGNOSTIC_ONLY_NOT_SOURCE_ACCEPTANCE',allocation=allocation,source=rec(Path(__file__)),original_sealed_V4_source=rec(D/'source_delivery_refresh_v4.py'),actual_13279_failure_history_preserved=True,strict_authority_guard_weakened=False,default_or_scientific_inputs_changed=False,GPU_allocated=0)
try:
 m.audit(O/'replay',R/'steps/24_benchmark_delivery/runs/source_relative_contracts_13279/acceptance.json')
 result.update(replay_unexpectedly_completed=True,exact_calls=calls)
except Exception as error:
 result.update(replay_unexpectedly_completed=False,exact_calls=calls,error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc())
p=O/'diagnostic.json';m.dump(p,result);p.chmod(0o444);print(json.dumps(rec(p)),flush=True)
