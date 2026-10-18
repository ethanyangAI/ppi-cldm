"""Staged-only exact common.py runtime-lock selector; no default path write."""
import json,os,re,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
OLD="        lock=Path(root)/'source/environment'/f'runtime-lock-{component}.json'"
def need(v,message):
 if not v:raise ValueError(message)
def patch(text,directory):
 p=Path(directory)
 need(p.is_absolute()and p.is_relative_to(R/"steps/24_benchmark_delivery/runs")and p.name=="runtime_override"and p.parent.name=="frozen"and p.parent.parent.name.startswith("generic_runtime_repair_"),"Only explicit accepted generic-repair override directory allowed")
 need(text.count(OLD)==1,"Exactly one original common lock selector required")
 new="        lock=Path("+repr(str(p))+")/f'runtime-lock-{component}.json'"
 return text.replace(OLD,new),{"old_selector":OLD,"new_selector":new,"directory":str(p),"source_write_scope":"STAGED_COMMON_ONLY"}
def accounting(text,jid,canceled=False,expected_state="RUNNING"):
 rows=[x.split("|")for x in text.splitlines()if x.split("|",1)[0]==str(jid)]
 need(len(rows)==1 and len(rows[0])>=9,"One exact scheduler accounting row required")
 job,state,exitcode,elapsed,tres,user,account,name,partition=rows[0][:9]
 need(user=="u21111210118"and account=="u21111210118"and partition=="organ"and elapsed.isdigit(),"Exact CPU ownership/account/partition required")
 if canceled:
  need(str(jid)=="13267"and name=="test9_native_physical_preflight_v2"and state.startswith("CANCELLED")and int(elapsed)==0 and not tres,"Old13267 must be canceled before allocation, never passed")
  return {"job_id":job,"state":state,"exit_code":exitcode,"elapsed_seconds":0,"allocated_CPUs":0,"allocated_GPUs":0,"allocated_TRES":tres,"row":rows[0]}
 vals={}
 for token in tres.split(","):
  need("="in token,"Actual allocation TRES required");k,v=token.split("=",1);need(k not in vals,"Duplicate allocation TRES");vals[k]=v
 def n(k):
  x=vals.get(k,"0");need(re.fullmatch(r"[0-9]+",x),"Numeric allocated TRES required");return int(x)
 need(expected_state in {"RUNNING","COMPLETED"}and state==expected_state and (expected_state!="COMPLETED"or exitcode=="0:0")and n("cpu")>=1 and max(n("gres/gpu"),sum(n(k)for k in vals if k.startswith("gres/gpu:")))==0,"Actual current pureCPU allocation required")
 return {"job_id":job,"state":state,"elapsed_seconds":int(elapsed),"allocated_CPUs":n("cpu"),"allocated_GPUs":0,"allocated_TRES":tres,"row":rows[0]}
def current_cpu_guard(jid):
 need(str(jid).isdigit()and os.environ.get("CUDA_VISIBLE_DEVICES")==""and os.environ.get("JAX_PLATFORMS")=="cpu"and os.environ.get("PYTHONNOUSERSITE")=="1"and not os.environ.get("PYTHONPATH"),"Actual isolated CPU job required")
 raw=subprocess.check_output(["sacct","-X","-j",str(jid),"--noheader","--parsable2","--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocTRES,User%64,Account%64,JobName%100,Partition%64"],text=True)
 return {"numeric":accounting(raw,jid),"raw":raw}

def qualification_contract(pre,snapshot,contracts,inputs):
 need(pre.get("schema")=="REFERENCE_FREE_E2E_PHYSICAL_GATE_PREFLIGHT_AND_CPU_REQUALIFICATION_V3"and pre.get("status")=="CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED"and pre.get("GPU_allocated")==0 and pre.get("native_inference_performed")is False,"Actual V3 pureCPU qualification required")
 need(pre.get("contracts_count")==57 and contracts.get("status")=="PASS"and contracts.get("tests")==57 and contracts.get("compiled_source")is True and contracts.get("bash_syntax")is True and contracts.get("source_manifest")==pre["source_manifest"],"Actual57 tested exact physicalV3 source required")
 suites=contracts.get("suites",[])
 need(len(suites)==4 and {x.get("suite")for x in suites}=={"physical","resource","design","staged_selector"}and all(x.get("returncode")==0 and isinstance(x.get("tests"),int)and x["tests"]>0 for x in suites)and sum(x["tests"]for x in suites)==57 and next(x["tests"]for x in suites if x["suite"]=="staged_selector")==15,"Actual four software suite count/exit closure required")
 need(snapshot.get("schema")=="physical_gate_source_snapshot.v1"and snapshot.get("base_python_source_sha256")=="c3d528bb6801a7a571cdd20bfd90652e397a8540a136e1f0510ef0ccc5488dde"and snapshot.get("default_common_selector_is_original")is True and pre.get("default_python_source_sha256_without_staged_runtime_selector")==snapshot.get("default_python_source_sha256_without_staged_runtime_selector")and pre.get("staged_runtime_selector")==snapshot.get("staged_runtime_selector"),"Distinct staged/default source identities required")
 need(pre.get("runtime_override_inputs")==snapshot.get("runtime_override_inputs")and pre.get("reviewed_runtime_override_acceptance")==snapshot.get("reviewed_runtime_override_acceptance")==inputs.get("runtime_override_acceptance")and pre.get("generic_report_repair_acceptance")==inputs.get("generic_repair_acceptance")and pre.get("materialization_acceptance")==inputs.get("materialization_acceptance"),"One exact actual generic/materialization/override input chain required")
 selector=snapshot["staged_runtime_selector"];directory=Path(selector["directory"])
 patch(OLD,str(directory))
 need(selector.get("old_selector")==OLD and selector.get("new_selector")=="        lock=Path("+repr(str(directory))+")/f'runtime-lock-{component}.json'"and selector.get("source_write_scope")=="STAGED_COMMON_ONLY","Only exact reviewed staged selector permitted")
 need(isinstance(pre.get("failed13286_13287_history"),dict)and pre["failed13286_13287_history"]==snapshot.get("failed13286_13287_history")==inputs.get("failed13286_13287_history"),"One exact preserved failed predecessor history chain required")
 need(pre.get("qualified_prediction",{}).get("status")in {"POSE_ACCEPTED","POSE_REJECTED"},"Incomplete requalification cannot become a terminal scientific outcome")
 return True
