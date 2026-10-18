#!/usr/bin/env python3
"""Combine verified engineering evidence; does not accept a scientific benchmark."""
import argparse,importlib.util,json,hashlib,os,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
B=R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source"
P=R/"steps/22_matched_benchmark/settings/pilot_v8"
def receipt(path):
 p=Path(path).resolve();return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--rf",required=True);ap.add_argument("--bc",required=True);ap.add_argument("--accounting",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
 spec=importlib.util.spec_from_file_location("frozen_budget",B/"paired_budget_benchmark.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 raw=subprocess.check_output(["scontrol","show","job",os.environ.get("SLURM_JOB_ID","INVALID"),"-o"],text=True)
 selected=m.select_scheduler_record(raw,raw_job_id=os.environ.get("SLURM_JOB_ID"),logical_key=m.allocation_key(os.environ));m.validate_scheduler_gpu_allocation(selected,0)
 if os.environ.get("CUDA_VISIBLE_DEVICES","") not in ("","NoDevFiles","-1"):raise ValueError("CPU0 evidence combination required")
 pins={"plan":receipt(R/"steps/22_matched_benchmark/engineering_pilot/plan_v5/frozen_plan.json"),"runtime_source":receipt(P/"source/benchmark_runtime.py"),"orchestrator_source":receipt(B/"paired_budget_benchmark.py"),"input_bridge":receipt(R/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/prepared_inputs.json")}
 plan=m.read_json(m.verified(pins["plan"]));tasks={t["method_id"]:t for t in plan["tasks"]};methods={t["method_id"]:t for t in plan["protocol"]["methods"]}
 stages={"rf_diffusion":{"rf_diffusion_backbone","original_proteinmpnn","native_af2_ptm1"},"bindcraft":{"native_bindcraft_trajectory","soluble_proteinmpnn","native_af2_ptm1_and_2","native_filters"}}
 rows=[];runs=[]
 for mid,path in (("rf_diffusion",a.rf),("bindcraft",a.bc)):
  acc=receipt(path);obj=m.read_json(m.verified(acc))
  if obj.get("status")!="NATIVE_GPU_METHOD_WORKFLOW_CONTENT_ACCEPTED_ENGINEERING_ONLY" or obj.get("method_id")!=mid:raise ValueError("Native actual-GPU engineering acceptance absent")
  if obj.get("plan")!=pins["plan"] or obj.get("runtime_source")!=pins["runtime_source"] or obj.get("task_id")!=tasks[mid]["task_id"]:raise ValueError("Actual source/plan/task differs")
  if obj.get("actual_assigned_gpu_count")!=1 or obj.get("scientific_scope")!="ENGINEERING_ONLY":raise ValueError("One actual GPU proof required")
  if obj.get("native_stage_status")!={s:"PASS" for s in stages[mid]} or set(obj.get("stage_evidence",{}))!=stages[mid]:raise ValueError("Every native workflow stage required")
  if obj.get("config_receipt")!=methods[mid]["config_receipt"] or obj.get("target_manifest")!=plan["protocol"]["targets"][0]["input_manifest"]:raise ValueError("Method config/target differs")
  for evidence in obj["stage_evidence"].values():m.verified(evidence)
  run=m.read_json(m.verified(obj["run_receipt"]))
  if run["plan"]!=pins["plan"] or run["task"]!=tasks[mid]:raise ValueError("Run receipt differs")
  rows.append({"method_id":mid,"acceptance":acc});runs.append(obj["run_receipt"])
 accounting=receipt(a.accounting);independent=m.read_json(m.verified(accounting))
 if independent.get("status")!="INDEPENDENT_BUDGET_LEDGER_AND_COHORT_AUDIT_PASS" or independent.get("plan")!=pins["plan"] or independent.get("independent_auditor")!=receipt(B/"paired_budget_independent.py") or independent.get("allocation_count")!=2 or independent.get("expected_tasks")!=2:raise ValueError("Exact two-task accounting required")
 audited=m.read_json(m.verified(independent["run_receipts_input"]))
 if sorted(audited,key=lambda r:r["path"])!=sorted(runs,key=lambda r:r["path"]):raise ValueError("Audited run set differs")
 output={"status":"BOTH_NATIVE_GPU_METHOD_WORKFLOWS_CONTENT_ACCEPTED_ENGINEERING_ONLY",**pins,"method_acceptances":rows,"independent_budget_acceptance":accounting,"purpose":"Full native workflow engineering proof; not a full-budget scientific comparison","source_entry":receipt(__file__),"CPU0_scheduler_record":selected}
 out=Path(a.out).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 with out.open("x") as handle:json.dump(output,handle,indent=2,sort_keys=True);handle.write("\n");handle.flush();os.fsync(handle.fileno())
 out.chmod(0o444);print(json.dumps(receipt(out)))
if __name__=="__main__":main()

