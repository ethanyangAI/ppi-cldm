#!/usr/bin/env python3
"""Freeze all 28 matched-budget tasks after root accepts complete GPU engineering."""
import importlib.util,json,hashlib,os,argparse,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
def receipt(p):
 p=Path(p).resolve();return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--engineering-acceptance",required=True);ap.add_argument("--out",required=True)
 a=ap.parse_args()
 ep=Path(a.engineering_acceptance).resolve();engineering=json.loads(ep.read_text())
 P=R/"steps/22_matched_benchmark/settings/pilot_v8"
 B=R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source"
 sp=importlib.util.spec_from_file_location("frozen_budget",B/"paired_budget_benchmark.py")
 mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
 raw=subprocess.check_output(["scontrol","show","job",os.environ.get("SLURM_JOB_ID","INVALID"),"-o"],text=True)
 selected=mod.select_scheduler_record(raw,raw_job_id=os.environ.get("SLURM_JOB_ID"),logical_key=mod.allocation_key(os.environ))
 tres=mod.validate_scheduler_gpu_allocation(selected,0)
 if os.environ.get("CUDA_VISIBLE_DEVICES","") not in ("","NoDevFiles","-1"):raise ValueError("CPU-only freeze must disable CUDA")
 if engineering.get("status")!="BOTH_NATIVE_GPU_METHOD_WORKFLOWS_CONTENT_ACCEPTED_ENGINEERING_ONLY":raise ValueError("Complete actual GPU engineering acceptance required")
 pins={"plan":receipt(R/"steps/22_matched_benchmark/engineering_pilot/plan_v5/frozen_plan.json"),
       "runtime_source":receipt(P/"source/benchmark_runtime.py"),
       "orchestrator_source":receipt(B/"paired_budget_benchmark.py"),
       "input_bridge":receipt(R/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/prepared_inputs.json")}
 for key,r in pins.items():
  if engineering.get(key)!=r:raise ValueError("Engineering authority pin mismatch: "+key)
 rows=engineering.get("method_acceptances",[])
 if len(rows)!=2 or {row.get("method_id") for row in rows}!={"rf_diffusion","bindcraft"}:raise ValueError("Two actual GPU method acceptance records required")
 engineering_plan=mod.read_json(mod.verified(pins["plan"]))
 tasks={t["method_id"]:t for t in engineering_plan["tasks"]}
 method_specs={m["method_id"]:m for m in engineering_plan["protocol"]["methods"]}
 stages={"rf_diffusion":{"rf_diffusion_backbone","original_proteinmpnn","native_af2_ptm1"},"bindcraft":{"native_bindcraft_trajectory","soluble_proteinmpnn","native_af2_ptm1_and_2","native_filters"}}
 run_records=[]
 for row in rows:
  apath=mod.verified(row["acceptance"]);accept=json.loads(Path(apath).read_text())
  if accept.get("status")!="NATIVE_GPU_METHOD_WORKFLOW_CONTENT_ACCEPTED_ENGINEERING_ONLY" or accept.get("method_id")!=row["method_id"]:raise ValueError("Method GPU content status mismatch")
  if accept.get("plan")!=pins["plan"] or accept.get("runtime_source")!=pins["runtime_source"]:raise ValueError("Method GPU source/plan not exact engineering authority")
  mid=row["method_id"]
  if accept.get("actual_assigned_gpu_count")!=1 or accept.get("scientific_scope")!="ENGINEERING_ONLY":raise ValueError("Actual single-GPU native stage proof required")
  if accept.get("native_stage_status")!={stage:"PASS" for stage in stages[mid]}:raise ValueError("Exact native stage proof required")
  if accept.get("task_id")!=tasks[mid]["task_id"] or accept.get("config_receipt")!=method_specs[mid]["config_receipt"] or accept.get("target_manifest")!=engineering_plan["protocol"]["targets"][0]["input_manifest"]:raise ValueError("Method GPU task/config/target identity mismatch")
  if set(accept.get("stage_evidence",{}))!=stages[mid]:raise ValueError("Exact stage evidence receipts required")
  for proof in accept["stage_evidence"].values():mod.verified(proof)
  run=mod.read_json(mod.verified(accept["run_receipt"]))
  if run["plan"]!=pins["plan"] or run["task"]!=tasks[mid]:raise ValueError("Engineering run receipt is from another task/plan")
  run_records.append(accept["run_receipt"])
 mod.verified(engineering["independent_budget_acceptance"])
 independent=json.loads(Path(engineering["independent_budget_acceptance"]["path"]).read_text())
 if independent.get("status")!="INDEPENDENT_BUDGET_LEDGER_AND_COHORT_AUDIT_PASS" or independent.get("plan")!=pins["plan"] or independent.get("independent_auditor")!=receipt(B/"paired_budget_independent.py") or independent.get("allocation_count")!=2 or independent.get("expected_tasks")!=2:raise ValueError("Exact two-task independent engineering budget audit required")
 audited_runs=mod.read_json(mod.verified(independent["run_receipts_input"]))
 if sorted(audited_runs,key=lambda r:r["path"])!=sorted(run_records,key=lambda r:r["path"]):raise ValueError("Independent budget audit belongs to another run set")
 previous=R/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/prepared_inputs.json"
 prepared=json.loads(previous.read_text())
 if prepared["status"]!="ALL_TARGET_INPUTS_ACCEPTED" or len(prepared["prepared"])!=7:raise ValueError("Complete final seven inputs required")
 methods=[]
 for mid,envname,score,direction in [
 ("rf_diffusion","rfd_env.sh","native_single_AF2_PTM_pae_interaction","lower"),
 ("bindcraft","bindcraft_env.sh","native_BindCraft_average_AF2_iptm","higher")]:
  env=P/"source"/envname
  methods.append({"method_id":mid,
  "session_start":["bash","-c",'source '+str(env)+'; exec python '+str(P/"source/benchmark_runtime.py")+' method-session --method '+mid+' --session-dir "$1" --target-manifest "$2" --config "$3" --config-sha256 "$4"',"method-session","{session_dir}","{target_manifest}","{method_config}","{method_config_sha256}"],
  "adapter_receipts":[receipt(P/"source/benchmark_runtime.py"),receipt(env)],
  "config_receipt":receipt(P/(mid+".json")),"native_score_name":score,"native_score_direction":direction})
 targets=[{k:e[k] for k in ("target_id","input_manifest","analysis_role")} for e in prepared["prepared"]]
 expected_roles={k:"primary" for k in ("MDM2_1YCR","KEAP1_2FLU","EGFR_DIII_1IVO","BCLXL_2M04","HRAS_4G0N","CRK_SH3_1CKA")}
 expected_roles["BBF111_9HAG"]="diagnostic"
 if len(targets)!=7 or {t["target_id"]:t["analysis_role"] for t in targets}!=expected_roles:raise ValueError("Exact seven identities and roles required")
 protocol={"schema":"paired-budget-v1","protocol_id":"PPI-PAIRED-BENCHMARK-20261011",
 "scientific_scope":"COMPUTATIONAL_ONLY","execution_mode":"persistent_session",
 "purpose":"Controlled same-target same-GPU-budget computational comparison; all six primary target pairs retained",
 "targets":targets,"methods":methods,"replicate_seeds":[21011,21012],"binder_length":65,
 "gpu_count":1,"budget_gpu_seconds":3600,"shutdown_reserve_seconds":10,"accounting_tolerance_seconds":2,
 "hardware":{"gpu_name":"NVIDIA A100-PCIE-40GB","minimum_memory_mib":40000},
 "sampling":{"salt":"PPI-PAIRED-20261011-FIXED-BEFORE-GENERATION","uniform_n_per_replicate":3,"native_top_k_per_replicate":2},
 "inference":{"mode":"descriptive_only","minimum_targets":6,"bootstrap_replicates":2000,"bootstrap_seed":4142},
 "completion_policy":{"allowed_scheduler_states":["COMPLETED","TIMEOUT"],"requires_durable_receipt_and_complete_raw_ledger":True,"generation_cutoff_wall_seconds":3590,"all_gpu_children_terminated_before_receipt":True,"actual_gpu_seconds":3600,"tolerance_seconds":2,"engineering_failure_is_comparable":False},
 "concurrency_cap":2,"common_review_gate":{"score":"R0","threshold":1.0,"operator":">=","aggregation":"all_required_models_median","scope":"COMPUTATIONAL_ONLY"},
 "common_review_primary":{"engine":"boltz","models":3,"seeds":[31011,31012,31013],"endpoint":"R1_official_ipSAE_10A_max_continuous","operational_pass":None},
 "common_review_secondary":{"engine":"af2","models":5,"seed":31021,"model_order":[1,2,3,4,5],"endpoint":"separate_R1_R0","pooled_with_primary":False},
 "aggregation_policy":"complete_selected_candidate_median_then_both_replicate_mean",
 "quality_rule":"Candidate median requires every frozen engine model; task median requires nonempty selected cohort and every selected candidate; target mean requires both fixed replicates; macro requires all six paired targets.",
 "missing_rule":"Typed unresolved remains in fixed denominator. Empty cohort quality is null; fully observed empty sequence pool may have observed fixed-cohort recovery yield zero.",
 "uniform_pool":"All canonical complete 65aa sequences first observed before the generation cutoff, including native rejected and native score unavailable. Sequence unique within task.",
 "native_cohort":"Independent secondary cohort, method-native fixed score top2 with unavailable score excluded and underfill retained.",
 "sensitivity_rule":"All native controls plus the minimum fixed uniform sampling hash candidate from each arm; natural target single-MSA Boltz sensitivity; BBF primary single MSA.",
 "engineering_acceptance":receipt(ep),"input_bridge":receipt(previous),
 "physical_hardware_inventory":receipt(R/"steps/23_common_review/inputs/proc_gpu_inventory_13044.json"),
 "source_entry":receipt(__file__)}
 D=Path(a.out).resolve()
 if D.exists():raise FileExistsError(D)
 D.mkdir(parents=True)
 pp=D/"protocol.json";pp.write_text(json.dumps(protocol,indent=2,sort_keys=True)+"\n")
 sp=importlib.util.spec_from_file_location("frozen_budget",B/"paired_budget_benchmark.py")
 mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
 plan=D/"frozen_plan.json";mod.freeze_protocol(pp,plan);sha=receipt(plan)["sha256"]
 launcher=D/"formal_generation.sbatch"
 text="""#!/bin/bash
#SBATCH --job-name=test9_paired_formal_generation
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --array=0-27%2
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark
#SBATCH --output=/lustre/users/u21111210118/projects/test9/logs/formal-generation-%A_%a.out
set -euo pipefail
export PS1="${PS1:-}" PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4
unset PYTHONPATH
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/tmp/formal-${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
TASK_ID=$(/lustre/users/u21111210118/projects/test9/env/core/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1]))["tasks"][int(sys.argv[2])]["task_id"])' PLAN_PATH "$SLURM_ARRAY_TASK_ID")
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py run-task --plan PLAN_PATH --plan-sha256 PLAN_SHA --task-id "$TASK_ID" --output-dir /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/formal_runs/${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}
"""
 launcher.write_text(text.replace("PLAN_PATH",str(plan)).replace("PLAN_SHA",sha))
 for p in (pp,plan,launcher):p.chmod(0o444)
 output={"status":"FROZEN_FULL28_FORMAL_BEFORE_GENERATION","plan":receipt(plan),"protocol":receipt(pp),"launcher":receipt(launcher),"engineering":receipt(ep),"expected_tasks":28,"scientific_scope":"COMPUTATIONAL_ONLY"}
 output["CPU_allocation"]={"scheduler_record_full":raw,"selected_scheduler_record":selected,"allocated_tres":tres,"allocated_gpu_count":0}
 (D/"freeze_receipt.json").write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
 (D/"freeze_receipt.json").chmod(0o444)
 D.chmod(0o555)
 print(json.dumps(output))
if __name__=="__main__":main()

