import os,sys,json,importlib.util,traceback,inspect
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
D=R/'steps/24_benchmark_delivery/frozen/source_refresh_relative_v4_13279/code'
sys.path.insert(0,str(D))
spec=importlib.util.spec_from_file_location('actual_source_v4_parent_diagnostic',D/'source_delivery_refresh_v4.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
allocation=m.cpu()
O=R/'steps/24_benchmark_delivery/runs'/('source_receipt_parent_diagnostic_'+os.environ['SLURM_JOB_ID']);O.mkdir(exist_ok=False)
original=m.exact;calls=0;failure_context=None
def diagnostic_exact(p,receipt):
 global calls,failure_context
 calls+=1
 try:return original(p,receipt)
 except Exception as error:
  frame=inspect.currentframe().f_back
  while frame is not None and frame.f_code.co_name!='_audit':frame=frame.f_back
  context={}
  if frame is not None:
   v=frame.f_locals;parent=v.get('parent');trail=v.get('trail',())
   parents=[e for e in v.get('edges',[]) if e.get('receipt',{}).get('path')==parent]
   row=parents[-1] if parents else None
   candidates=v.get('candidates',{}).get(Path(receipt['path']).name,[])
   context=dict(parent_original_logical_path=parent,source_field=list(trail),previous_verified_parent_edge=row,declared_basename_candidates=[str(x) for x in candidates],declared_same_size_candidates=[dict(path=str(x['path']),bytes=x['path'].stat().st_size)for x in v.get('original_rows',{}).values()if x['path'].is_file()and x['path'].stat().st_size==receipt['bytes']],exact_declared_alias_hit=(receipt['path'],receipt['sha256'])in v.get('aliases',{}))
  failure_context=dict(diagnostic_only=True,source_V4_guard_unchanged=True,external_original_not_read=True,attempted_receipt=receipt,original_error_type=type(error).__name__,original_error=str(error),context=context)
  raise ValueError(json.dumps(failure_context,ensure_ascii=False))from error
m.exact=diagnostic_exact
result=dict(schema='source-closure-exact-parent-diagnostic.v1',status='DIAGNOSTIC_ONLY_NOT_SOURCE_ACCEPTANCE',allocation=allocation,source=m.rec(Path(__file__)),original_sealed_V4_source=m.rec(D/'source_delivery_refresh_v4.py'),actual13279_and13285_history_preserved=True,strict_authority_guard_weakened=False,default_or_scientific_inputs_changed=False,GPU_allocated=0)
try:
 m.audit(O/'replay',R/'steps/24_benchmark_delivery/runs/source_relative_contracts_13279/acceptance.json');result.update(replay_unexpectedly_completed=True,exact_calls=calls)
except Exception as error:
 result.update(replay_unexpectedly_completed=False,exact_calls=calls,failure_context=failure_context,error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc())
p=O/'diagnostic.json';m.dump(p,result);p.chmod(0o444);print(json.dumps(m.rec(p)),flush=True)
