#!/usr/bin/env python3
"""Freeze all 28 matched-budget tasks after root accepts complete GPU engineering."""
import importlib.util,json,hashlib,os,argparse
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
def receipt(p):
 p=Path(p).resolve();return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--engineering-acceptance",required=True);ap.add_argument("--out",required=True)
 a=ap.parse_args()
 ep=Path(a.engineering_acceptance).resolve();engineering=json.loads(ep.read_text())
 if engineering.get("status")!="BOTH_NATIVE_GPU_METHOD_WORKFLOWS_CONTENT_ACCEPTED_ENGINEERING_ONLY":raise ValueError("Complete actual GPU engineering acceptance required")
 P=R/"steps/22_matched_benchmark/settings/pilot_v6"
 B=R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source"
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
 if sum(t["analysis_role"]=="primary" for t in targets)!=6 or sum(t["analysis_role"]=="diagnostic" for t in targets)!=1:raise ValueError("Exactly six primary and one diagnostic")
 protocol={"schema":"paired-budget-v1","protocol_id":"PPI-PAIRED-BENCHMARK-20261011",
 "scientific_scope":"COMPUTATIONAL_ONLY","execution_mode":"persistent_session",
 "purpose":"Controlled same-target same-GPU-budget computational comparison; all six primary target pairs retained",
 "targets":targets,"methods":methods,"replicate_seeds":[21011,21012],"binder_length":65,
 "gpu_count":1,"budget_gpu_seconds":3600,"shutdown_reserve_seconds":10,"accounting_tolerance_seconds":2,
 "hardware":{"gpu_name":"NVIDIA A100-PCIE-40GB","minimum_memory_mib":40000},
 "sampling":{"salt":"PPI-PAIRED-20261011-FIXED-BEFORE-GENERATION","uniform_n_per_replicate":3,"native_top_k_per_replicate":2},
 "inference":{"mode":"descriptive_only","minimum_targets":6,"bootstrap_replicates":2000,"bootstrap_seed":4142},
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
 (D/"freeze_receipt.json").write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
 print(json.dumps(output))
if __name__=="__main__":main()

