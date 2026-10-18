#!/usr/bin/env python3
"""Freeze a one-attempt engineering pilot; never a fair scientific comparison."""
import importlib.util,json,hashlib,os
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
P=R/"steps/22_matched_benchmark/settings/pilot_v7"
B=R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source"
D=R/"steps/22_matched_benchmark/engineering_pilot/plan_v4"
D.mkdir(parents=True,exist_ok=True)
def receipt(p):
 p=Path(p); return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
methods=[]
for mid,envname,score,direction in [
 ("rf_diffusion","rfd_env.sh","native_single_AF2_PTM_pae_interaction","lower"),
 ("bindcraft","bindcraft_env.sh","native_BindCraft_average_AF2_iptm","higher")]:
 env=P/"source"/envname
 methods.append({"method_id":mid,
 "session_start":["bash","-c",'source '+str(env)+'; exec python '+str(P/"source/benchmark_runtime.py")+' method-session --method '+mid+' --session-dir "$1" --target-manifest "$2" --config "$3" --config-sha256 "$4"',"method-session","{session_dir}","{target_manifest}","{method_config}","{method_config_sha256}"],
 "adapter_receipts":[receipt(P/"source/benchmark_runtime.py"),receipt(env)],
 "config_receipt":receipt(P/(mid+".json")),"native_score_name":score,"native_score_direction":direction})
protocol={"schema":"paired-budget-v1","protocol_id":"PPI-ENGINEERING-REPAIR-20261011",
 "scientific_scope":"COMPUTATIONAL_ONLY","execution_mode":"persistent_session",
 "purpose":"GPU engineering: one complete method attempt on the largest target; all allocated cost retained; not a fair full-budget scientific comparison",
 "targets":[{"target_id":"KEAP1_2FLU","input_manifest":receipt(R/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/KEAP1_2FLU/input_manifest.json"),"analysis_role":"diagnostic"}],
 "methods":methods,"replicate_seeds":[20901],"gpu_count":1,"budget_gpu_seconds":3600,
 "shutdown_reserve_seconds":10,"accounting_tolerance_seconds":2,
 "hardware":{"gpu_name":"NVIDIA A100-PCIE-40GB","minimum_memory_mib":40000},
 "sampling":{"salt":"PPI-ENGINEERING-20261011-LOCKED","uniform_n_per_replicate":3,"native_top_k_per_replicate":2},
 "inference":{"mode":"descriptive_only","minimum_targets":6,"bootstrap_replicates":2000,"bootstrap_seed":4142},
 "max_attempts_safety_limit":1,"concurrency_cap":2}
protocol["engineering_history"]={"classification":"ENGINEERING_HISTORY_NOT_CURRENT_RUNTIME_DEPENDENCY","previous_plan_logical_path":str(R/"steps/22_matched_benchmark/engineering_pilot/plan_v3/frozen_plan.json"),"previous_plan_sha256":receipt(R/"steps/22_matched_benchmark/engineering_pilot/plan_v3/frozen_plan.json")["sha256"],"previous_plan_had_no_gpu_execution":True,"historical_unarchived_cpu_probe_source_sha256":"b47e302116b923e683aee567fe0c1b6721a56d6c410de9cd2cdd9dcfd79fecfd","reason":"Fresh current CPU readiness and dependency closure replaces obsolete development proof; exact runtime bytes and all scientific settings unchanged","target_geometry_query_hotspots_reference_maps_unchanged":True,"method_native_scientific_settings_unchanged":True,"budget_unchanged":True}
protocol["current_readiness_dependency"]=receipt(R/"steps/21_method_runtime/runs/current_v7_delivery_13133/outputs/current_readiness_dependency.json")
protocol["physical_hardware_inventory"]=receipt(R/"steps/23_common_review/inputs/proc_gpu_inventory_13044.json")
pp=D/"protocol.json"
with pp.open("x") as f: json.dump(protocol,f,indent=2); f.write("\n")
sp=importlib.util.spec_from_file_location("frozen_budget",B/"paired_budget_benchmark.py")
m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
plan=D/"frozen_plan.json"; m.freeze_protocol(pp,plan)
sha=receipt(plan)["sha256"]
launcher=D/"engineering_pilot.sbatch"
text='''#!/bin/bash
#SBATCH --job-name=t9-engineering-pilot
#SBATCH --partition=organ
#SBATCH --account=u21111210118
#SBATCH --qos=normal
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --array=0-1%1
#SBATCH --chdir=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark
#SBATCH --output=/lustre/users/u21111210118/projects/test9/logs/engineering-pilot-v4-%A_%a.out
set -euo pipefail
export PS1="${PS1:-}"
export PYTHONNOUSERSITE=1
unset PYTHONPATH
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=4
export TMPDIR=/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/tmp/pilot-${SLURM_JOB_ID}
mkdir -p "$TMPDIR"
TASK_ID=$(/lustre/users/u21111210118/projects/test9/env/core/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1]))["tasks"][int(sys.argv[2])]["task_id"])' PLAN_PATH "$SLURM_ARRAY_TASK_ID")
exec /lustre/users/u21111210118/projects/test9/env/core/bin/python /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py run-task --plan PLAN_PATH --plan-sha256 PLAN_SHA --task-id "$TASK_ID" --output-dir /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/engineering_pilot/runs_v4/${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}
'''
launcher.write_text(text.replace("PLAN_PATH",str(plan)).replace("PLAN_SHA",sha))
for p in (pp,plan,launcher): p.chmod(0o444)
out={"status":"FROZEN_ENGINEERING_ONLY_NOT_PRODUCTION","plan":receipt(plan),"protocol":receipt(pp),"launcher":receipt(launcher),"expected_tasks":2,"production_gpu_jobs_submitted":False}
(D/"freeze_receipt.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out))

