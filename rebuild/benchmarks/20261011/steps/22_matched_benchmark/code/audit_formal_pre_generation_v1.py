#!/usr/bin/env python3
"""Independent CPU pre-generation closure for formalplan13257 and sharedCPU3 policy."""
import ast,hashlib,importlib.util,json,os,subprocess,sys
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");CODE=R/"steps/22_matched_benchmark/code";P=R/"steps/22_matched_benchmark/formal_freeze_13257/plan"
RESOURCE=CODE/"resource_contract_v3/source"
sys.path.insert(0,str(RESOURCE));import independent_resource_policy as res
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
cpu=res.cpu_guard();D=CODE/("formal_pre_generation_"+os.environ["SLURM_JOB_ID"]);D.mkdir()
F=module("formal64",CODE/"formal_contract_v2/source/formal_benchmark_contract.py")
# Reuse only independent receipt/graph functions from the accepted v5 preflight, never its top-level audit.
old_source=CODE/"audit_engineering_plan_v5_v3.py";tree=ast.parse(old_source.read_text())
defs=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in("rec","verify","read","check","walk")]
context={"Path":Path,"R":R,"hashlib":hashlib,"json":json,"seen":{},"checks":[],"canonical_aliases":[]}
exec(compile(ast.Module(body=defs,type_ignores=[]),str(old_source),"exec"),context)
verify=context["verify"];read=context["read"];walk=context["walk"];check=context["check"]
freeze=read(P/"freeze_receipt.json");plan=read(P/"frozen_plan.json")
for key in("plan","protocol","launcher","engineering"):verify(freeze[key])
check(freeze["plan"]==res.rec(P/"frozen_plan.json")and freeze["status"]=="FROZEN_FULL28_FORMAL_BEFORE_GENERATION","Actual readonly formal13257 freeze")
check(plan["protocol_receipt"]==freeze["protocol"]and read(verify(plan["protocol_receipt"]))==plan["protocol"],"Embedded/direct protocol exact")
check(plan["status"]=="FROZEN_BEFORE_GENERATION"and plan["orchestrator"]==res.rec(R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py"),"Exact current formal authority andv4 runner")
F.formal_protocol(plan["protocol"]);check(plan["tasks"]==F.task_matrix(plan["protocol"])and len(plan["tasks"])==28,"Independent exact full28 formal matrix/roles/budget/salt/65aa/model/aggregation")
for method in plan["protocol"]["methods"]:
 check(method["config_receipt"]==res.rec(R/("steps/22_matched_benchmark/settings/pilot_v8/"+method["method_id"]+".json")),"Same accepted immutable native science configuration:"+method["method_id"])
 for receipt in method["adapter_receipts"]+[method["config_receipt"]]:
  verify(receipt);check(not Path(receipt["path"]).stat().st_mode&0o222,"Readonly source/config")
 check(method["session_start"][:2]==["bash","-c"]and "; exec python "in method["session_start"][2],"Persistent method session PID/deadline authority")
combined=read(verify(plan["protocol"]["engineering_acceptance"]))
check(combined["status"]=="BOTH_NATIVE_GPU_METHOD_WORKFLOWS_CONTENT_ACCEPTED_ENGINEERING_ONLY","Both method engineer proof typed separate from formal scientific results")
check(combined["independent_budget_acceptance"]==res.rec(CODE/"engineering13175_accounting_13209/independent_acceptance.json"),"Exact2main591 independent accounting")
methods={x["method_id"]:x["acceptance"]for x in combined["method_acceptances"]}
BC=read(verify(methods["bindcraft"]));check(BC["run_receipt"]["path"].endswith("runs_v5/13175_1/run_receipt.json")and BC["main_workflow_terminal"]=="SCIENTIFIC_REJECT_BEFORE_MPNN"and BC["main_workflow_full_native_chain_completed"]is False,"MainBC scientifically rejected trajectory; later APIs supplemental only")
check(methods["bindcraft"]["path"]==str(R/"steps/21_method_runtime/runs/supplemental_actual_current_13247/outputs/acceptance.json")and BC["supplemental_formal_eligible_sequences"]==0,"Current deterministic supplemental gate bound, no primarypool")
current=CODE/"seeded_supplemental13246_audit_13254/acceptance.json";CUR=read(current)
check(CUR["status"]=="INDEPENDENT_CURRENT_SEEDED_SUPPLEMENTAL_BUDGET_OWNERSHIP_RAW_CONTENT_AND_RNG_AUDIT_PASS"and CUR["allocated_gpu_seconds"]==359 and CUR["formal_sequences"]==0,"Additional independent current359-cost andfullrawRNG acceptance")
check(CUR["content_acceptance"]==res.rec(R/"steps/21_method_runtime/runs/supplemental_actual_current_13247/outputs/supplemental_base_audit/acceptance.json")and CUR["rng_acceptance"]==res.rec(R/"steps/21_method_runtime/runs/supplemental_actual_current_13247/outputs/deterministic_rng.json"),"Same base/fullrawseededcontent and all originalseed events")
policy_dir=R/("steps/22_matched_benchmark/formal_launchpolicy_"+os.environ["SLURM_JOB_ID"])
resource_freeze=res.freeze_resource_policy(P/"frozen_plan.json",verify(freeze["launcher"]),policy_dir)
policy=read(policy_dir/"resource_policy.json");res.formal_policy(policy)
check(policy["plan"]==freeze["plan"]and policy["protocol"]==freeze["protocol"],"CPU3 policy exact formal authority binding")
check(policy["sequence_universe"]==res.sequence_universe(plan["protocol"]),"Before-generation MPNN-only primarypool scope andseparate intermediate lineage")
old_shell=verify(freeze["launcher"]).read_text();new_shell=verify(policy["launcher"]).read_text()
check(new_shell==old_shell.replace("#SBATCH --cpus-per-task=4","#SBATCH --cpus-per-task=3",1),"Exact original/newlauncher only4->3")
for literal in("#SBATCH --gres=gpu:1","#SBATCH --mem=64G","#SBATCH --time=01:00:00","#SBATCH --array=0-27%2","OMP_NUM_THREADS=4","OPENBLAS_NUM_THREADS=1",str(P/"frozen_plan.json"),freeze["plan"]["sha256"]):
 check(literal in new_shell,"Shared all28 frozen launch resource:"+literal)
subprocess.run(["bash","-n",policy["launcher"]["path"]],check=True)
# Current operative graph includes model/environment/target/reference/source proofs. Historical source aliases resolve exact archived bytes.
walk(plan);walk(freeze);walk(policy);walk(CUR)
check(not any(x["sha256"]=="b47e302116b923e683aee567fe0c1b6721a56d6c410de9cd2cdd9dcfd79fecfd"for x in context["seen"].values()),"No unresolved obsolete development source in currentauthority")
root_sacct=subprocess.check_output(["sacct","-X","-P","-n","-j","13257","--format=JobIDRaw,ElapsedRaw,AllocTRES,State"],text=True)
check(root_sacct.strip().endswith("|COMPLETED")and "gres/gpu"not in root_sacct,"Root formal freeze13257 actualcompletedGPU0")
report={"status":"INDEPENDENT_FORMAL28_READONLY_AUTHORITY_CURRENT_SEEDED_GATE_AND_SHARED_CPU3_PRE_GENERATION_AUDIT_PASS",
 "scope":"BEFORE_GENERATION_NOT_SCIENTIFIC_RESULT_ACCEPTANCE","source":res.rec(__file__),"cpu_allocation":cpu,
 "plan":freeze["plan"],"protocol":freeze["protocol"],"root_freeze_receipt":res.rec(P/"freeze_receipt.json"),"root_freeze_sacct_raw":root_sacct,
 "resource_policy":res.rec(policy_dir/"resource_policy.json"),"resource_freeze":res.rec(policy_dir/"freeze_receipt.json"),"ready_launcher":policy["launcher"],
 "original_cpu4_launcher":freeze["launcher"],"original_cpu4_execution_status":"AUDITED_NOT_EXECUTED","shared_cpu_count":3,"gpu_count":1,"requested_memory_gib":64,"omp_threads_literal":4,
 "cgroup_cpu_isolation_status":"UNOBSERVED","possible_cpu_bottleneck":True,"expected_task_count":28,"expected_frozen_generation_gpu_seconds":100800,
 "sequence_scope_clarification":policy["sequence_universe"],"main_two_allocation_accounting":combined["independent_budget_acceptance"],
 "current_supplemental_independent_gate":res.rec(current),"current_supplemental_gpu_seconds_separate":359,
 "unseeded_supplemental_history_gpu_seconds_separate":381,"earlier_failed_engineering_gpu_seconds_separate":200,"main_engineering_gpu_seconds_separate":591,
 "recursive_verified_receipt_count":len(context["seen"]),"verified_receipts":list(context["seen"].values()),
 "canonical_exact_byte_aliases":context["canonical_aliases"],"checks":context["checks"],
 "formal64_contracts":res.rec(CODE/"formal_contract_v2/manifest.json"),"resource54_contracts":res.rec(CODE/"resource_contract_v3/manifest.json"),
 "GPU_submitted_by_auditor":False,"reporting_rule":"Sixprimary targets descriptive paired effects; preserve engineering failures, emptyMPNN pools andallmodelmissingness; intermediate complete trajectory sequences counted separately; no experimentalblockade or workflow superiority established"}
path=D/"acceptance.json";path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
for p in D.rglob("*"):
 if p.is_file():p.chmod(0o444)
D.chmod(0o555);Path(__file__).chmod(0o444)
print(json.dumps({"status":report["status"],"receipt":res.rec(path),"policy":report["resource_policy"],"launcher":report["ready_launcher"],"recursive_receipts":report["recursive_verified_receipt_count"]}))

