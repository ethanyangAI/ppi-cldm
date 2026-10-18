#!/usr/bin/env python3
"""Independent CPU audit of engineering plan_v4 and all7 metadata-only chain bridge."""
import ast,hashlib,json,os,re,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");CODE=R/"steps/22_matched_benchmark/code";PILOT=R/"steps/22_matched_benchmark/engineering_pilot"
seen={};checks=[]
def rec(p):
 p=Path(p);h=hashlib.sha256()
 with p.open("rb")as f:
  for block in iter(lambda:f.read(8*1024*1024),b""):h.update(block)
 return {"path":str(p.resolve()),"bytes":p.stat().st_size,"sha256":h.hexdigest()}
def verify(r):
 actual=rec(r["path"])
 if actual!=r:raise ValueError("Receipt mismatch: "+r["path"])
 return Path(r["path"])
def read(p):return json.loads(Path(p).read_text())
def check(value,label):
 if not value:raise ValueError(label)
 checks.append(label)
def walk(obj):
 if isinstance(obj,dict):
  if {"path","bytes","sha256"}<=set(obj):
   key=(obj["path"],obj["sha256"])
   if key not in seen:
    path=verify({k:obj[k]for k in ["path","bytes","sha256"]})
    seen[key]=rec(path)
    if path.suffix==".json" and obj["bytes"]<4_000_000:
     try:walk(read(path))
     except json.JSONDecodeError:pass
  else:
   for v in obj.values():walk(v)
 elif isinstance(obj,list):
  for v in obj:walk(v)
jid=os.environ["SLURM_JOB_ID"]
cpu=subprocess.run(["scontrol","show","job",jid,"-o"],check=True,capture_output=True,text=True).stdout
check(re.search(r"\bJobState=(\S+)",cpu)[1]=="RUNNING","Auditor actual RUNNING CPU allocation")
tres=re.search(r"\b(?:AllocTRES|TRES)=(\S+)",cpu)[1]
check(not any(int(v)>0 for v in re.findall(r"(?:^|,)gres/gpu(?::[^,=]+)?=(\d+)",tres)),"Auditor actual GPU0")
dest=CODE/("engineering_plan_v3_audit_"+jid);dest.mkdir()
planpath=PILOT/"plan_v3/frozen_plan.json";plan=read(planpath);p=plan["protocol"]
freeze=read(PILOT/"plan_v3/freeze_receipt.json")
for field in ["plan","protocol","launcher"]:verify(freeze[field])
check(freeze["plan"]==rec(planpath) and freeze["status"]=="FROZEN_ENGINEERING_ONLY_NOT_PRODUCTION","Root exact engineering-only freeze receipt")
check(read(verify(plan["protocol_receipt"]))==p,"Embedded protocol equals original bytes")
expectedsource=R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py"
check(plan["orchestrator"]==rec(expectedsource) and plan["orchestrator"]["sha256"]=="b37227bd862ee1425a59f5308be1ee3f4824042dea5d71c1269ad0f406b318f9","Exact immutable budget v4 source")
check(p["protocol_id"]=="PPI-ENGINEERING-REPAIR-20261011" and p["scientific_scope"]=="COMPUTATIONAL_ONLY","Explicit new engineering protocol identity")
check(p["execution_mode"]=="persistent_session" and p["max_attempts_safety_limit"]==1,"One persistent attempt; no formal throughput comparison")
check(p["gpu_count"]==1 and p["budget_gpu_seconds"]==3600 and p["shutdown_reserve_seconds"]==10 and p["accounting_tolerance_seconds"]==2,"Unchanged predeclared integer budget/reserve/tolerance")
check(p["hardware"]=={"gpu_name":"NVIDIA A100-PCIE-40GB","minimum_memory_mib":40000},"Exact A100 hardware requirement")
check(p["replicate_seeds"]==[20901] and p["sampling"]=={"salt":"PPI-ENGINEERING-20261011-LOCKED","uniform_n_per_replicate":3,"native_top_k_per_replicate":2},"Engineering seed and independent sampling unchanged")
check(p["inference"]["mode"]=="descriptive_only" and p["concurrency_cap"]==2,"No engineering significance; concurrency cap")
check("technical_amendment"not in p and "engineering_history"in p,"Explicit engineering history separate from current dependency graph")
history=p["engineering_history"]
check(history["classification"]=="ENGINEERING_HISTORY_NOT_CURRENT_RUNTIME_DEPENDENCY","Old plan is engineering history only")
oldpath=Path(history["previous_plan_logical_path"])
check(oldpath==PILOT/"plan_v3/frozen_plan.json" and rec(oldpath)["sha256"]==history["previous_plan_sha256"],"Historical unexecuted plan-v3 exact hash preserved")
oldplan=read(oldpath);oldp=oldplan["protocol"]
check(history["previous_plan_had_no_gpu_execution"]is True and not (PILOT/"runs_v3").exists(),"Previous plan-v3 never launched; no post-result task source selection")
check(history["historical_unarchived_cpu_probe_source_sha256"]=="b47e302116b923e683aee567fe0c1b6721a56d6c410de9cd2cdd9dcfd79fecfd","Old unrecoverable development source remains explicitly historical")
history_note={"classification":"HISTORICAL_UNRESOLVED_PROVENANCE","previous_plan":rec(oldpath),"logical_development_path":str(R/"source/rebuild/benchmark_runtime.py"),
 "historical_bytes":33676,"historical_sha256":history["historical_unarchived_cpu_probe_source_sha256"],"current_authority_depends_on_this_source":False,
 "reason":"Legacy12980 obsolete CPU development probe has no exact archived source; removed from current-v7 dependency graph, never treated as current path hash."}
historical_accounting=CODE/"pilot13069_array_accounting_13090/report.json"
check(rec(historical_accounting)["sha256"]=="09ed8a3d5d0493db99ac75eb262fdeefd0f291feff9b70310570d974752ce93f","Historical 200 GPU seconds preserved")
readiness=read(verify(p["current_readiness_dependency"]))
check(readiness["status"]=="CURRENT_READONLY_PRIVATE_METHOD_DEPENDENCIES_CPU_ACCEPTED_GPU_PENDING"and readiness["legacy_12980_dev_adapter_proof_currently_excluded"]is True,"Fresh current readiness excludes obsolete source proof")
check(readiness["runtime_source"]["sha256"]=="1325556ccac5936bbae456344f040257b5041815190af5b48425cf016bc38e17","Runtime unchanged exact native-v6 bytes")
for key in ["budget_gpu_seconds","gpu_count","shutdown_reserve_seconds","accounting_tolerance_seconds","replicate_seeds","hardware","sampling","inference","max_attempts_safety_limit"]:
 check(oldp[key]==p[key],"Unchanged protocol setting "+key)
check(len(p["targets"])==1 and p["targets"][0]["target_id"]=="KEAP1_2FLU" and p["targets"][0]["analysis_role"]=="diagnostic","Largest target engineering diagnostic only")
check([m["method_id"]for m in p["methods"]]==["rf_diffusion","bindcraft"],"Both method arms")
# Independently reconstruct task IDs/matrix without importing the orchestrator.
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
expected=[]
for target in p["targets"]:
 for seed in p["replicate_seeds"]:
  pair={"protocol_id":p["protocol_id"],"target_id":target["target_id"],"seed":seed}
  for method in p["methods"]:
   base=dict(pair,method_id=method["method_id"])
   expected.append(dict(base,task_id=digest(base)[:24],pair_id=digest(pair)[:24],budget_gpu_seconds=3600,array_index=len(expected)))
check(plan["tasks"]==expected and freeze["expected_tasks"]==2,"Independent exact two-task matrix")
scientific_comparison=[]
for method in p["methods"]:
 mid=method["method_id"];oldmethod=next(x for x in oldp["methods"]if x["method_id"]==mid)
 check(method["native_score_name"]==oldmethod["native_score_name"]and method["native_score_direction"]==oldmethod["native_score_direction"],mid+" native score identity unchanged")
 newcfg=read(verify(method["config_receipt"]));oldcfg=read(verify(oldmethod["config_receipt"]))
 def science(cfg):
  obj=json.loads(json.dumps(cfg));obj.pop("input_receipts",None);obj.pop("engineering_revision",None)
  env=obj.get("native_af2",{}).get("environment_script")
  if env:obj["native_af2"]["environment_script"]={k:env[k]for k in ["bytes","sha256"]}
  return obj
 check(science(newcfg)==science(oldcfg),mid+" exact native scientific settings unchanged")
 check(newcfg["binder_length"]==65 and newcfg["execution_mode"]=="persistent_session",mid+" fixed65aa persistent")
 check("/settings/pilot_v7/"in method["config_receipt"]["path"],mid+" exact immutable runtime-v7 config")
 for r in method["adapter_receipts"]:check("/settings/pilot_v7/source/"in r["path"],mid+" immutable-v7 adapter path")
 argv=method["session_start"]
 check(argv[:2]==["bash","-c"] and "; exec python "in argv[2] and "/settings/pilot_v7/source/benchmark_runtime.py"in argv[2],mid+" persistent exec launcher")
 check("--method "+mid+" "in argv[2]and argv[-4:]==["{session_dir}","{target_manifest}","{method_config}","{method_config_sha256}"],mid+" explicit frozen method/config/session routing")
 scientific_comparison.append({"method_id":mid,"old_config":oldmethod["config_receipt"],"new_config":method["config_receipt"],"science_equal_except_identical_env_path":True})
bridge=read(R/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/prepared_inputs.json")
metadata=read(R/"steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/metadata_acceptance.json")
rows=metadata["audits"];check(len(rows)==7 and len({x["target_id"]for x in rows})==7,"All7 chain bridge audited")
bridge_checks=[]
for row in rows:
 old=read(verify(row["previous_manifest"]));new=read(verify(row["new_manifest"]))
 check(old["rfd_output_target_chain"]=="B" and old["rfd_binder_chain"]=="A" and new["rfd_output_target_chain"]=="A"and new["rfd_binder_chain"]=="B",row["target_id"]+" corrected physical chain roles")
 oldcompare=dict(old);newcompare=dict(new)
 for key in ["rfd_output_target_chain","rfd_binder_chain"]:oldcompare.pop(key);newcompare.pop(key)
 correction=newcompare.pop("native_chain_metadata_correction")
 check(oldcompare==newcompare,row["target_id"]+" every other original field identical")
 check(correction["previous_manifest"]==row["previous_manifest"],row["target_id"]+" pinned original manifest")
 for key in ["target_pdb","reference_complex","target_sequence","hotspots","design_to_reference_indices","partner_to_reference_indices"]:
  check(old[key]==new[key],row["target_id"]+" geometry/query/hotspots/maps unchanged "+key)
 check(new["binder_length"]==65 and new["common_target_chain"]=="A"and new["common_binder_chain"]=="B",row["target_id"]+" consistent common identities/length")
 bridge_checks.append({"target_id":row["target_id"],"old":row["previous_manifest"],"new":row["new_manifest"],"other_fields_equal":True,"geometry_regenerated":False})
proof=read(verify(metadata["official_output_proof"]))
check(proof["status"]=="PASS"and proof["physical_target_chain"]=="A"and proof["physical_binder_chain"]=="B"and proof["target_count"]==285 and proof["binder_count"]==65,"Actual official RFD output physical identity proof")
check(all(proof["strict_trb_checks"].values()),"All exact TRB identity checks PASS")
# Re-parse actual preserved PDB chain/sequence; never generate or mutate coordinates.
AA={"ALA":"A","CYS":"C","ASP":"D","GLU":"E","PHE":"F","GLY":"G","HIS":"H","ILE":"I","LYS":"K","LEU":"L","MET":"M","ASN":"N","PRO":"P","GLN":"Q","ARG":"R","SER":"S","THR":"T","VAL":"V","TRP":"W","TYR":"Y"}
chains={}
for line in verify(proof["actual_official_output_pdb"]).read_text().splitlines():
 if line.startswith("ATOM")and line[12:16].strip()=="CA":
  chain=line[21];key=(int(line[22:26]),line[26]);chains.setdefault(chain,{})[key]=AA[line[17:20].strip()]
sequences={c:"".join(v[k]for k in sorted(v))for c,v in chains.items()}
check(set(sequences)=={"A","B"}and sequences["A"]==proof["target_sequence"]and len(sequences["B"])==65,"Independent actual preserved PDB CA identities")
check(proof["coordinate_audit_role"].startswith("diagnostic only"),"No posthoc coordinate quality selection")
launcher=verify(freeze["launcher"]);shell=launcher.read_text()
for string in ["#SBATCH --gres=gpu:1","#SBATCH --account=u21111210118","#SBATCH --qos=normal","#SBATCH --partition=organ","#SBATCH --time=01:00:00","#SBATCH --array=0-1%1",
 "#SBATCH --chdir="+str(R/"steps/22_matched_benchmark"),"--plan "+str(planpath),"--plan-sha256 "+freeze["plan"]["sha256"],str(expectedsource),"runs_v3/${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"]:
 check(string in shell,"Launcher pinned "+string)
check("runs/13069"not in shell and "runs_v3"in shell,"New output names preserve completed13069")
subprocess.run(["bash","-n",str(launcher)],check=True)
ast.parse((CODE/"freeze_engineering_pilot_v4.py").read_text())
for method in p["methods"]:
 for receipt in [method["config_receipt"]]+method["adapter_receipts"]:
  check(Path(receipt["path"]).stat().st_mode&0o222==0,"Readonly current-v7 source/config "+receipt["path"])
walk(plan);walk(freeze);walk(metadata)
check(not any(v["sha256"]=="b47e302116b923e683aee567fe0c1b6721a56d6c410de9cd2cdd9dcfd79fecfd"for v in seen.values()),"No obsolete unarchived source in current operative graph")
check(all(Path(x["path"]).stat().st_mode&0o222==0 for x in [freeze["plan"],freeze["protocol"],freeze["launcher"],plan["orchestrator"]]),"Plan/protocol/launcher/orchestrator readonly")
report={"status":"INDEPENDENT_ENGINEERING_PLAN_V4_CURRENT_OPERATIVE_GRAPH_PRE_GPU_AUDIT_PASS","scope":"ENGINEERING_ONLY_NOT_FORMAL_OR_SCIENTIFIC_ACCEPTANCE",
 "cpu_job_id":jid,"cpu_scheduler":cpu,"cpu_alloc_tres":tres,"audit_source":rec(Path(__file__)),
 "plan":rec(planpath),"freeze_helper":rec(CODE/"freeze_engineering_pilot_v3.py"),"freeze_receipt":rec(PILOT/"plan_v3/freeze_receipt.json"),
 "launcher":rec(launcher),"n_tasks":2,"max_attempts_safety_limit":1,"all7_metadata_only_checks":bridge_checks,
 "method_scientific_equivalence":scientific_comparison,"recursive_verified_receipt_count":len(seen),
 "verified_receipts":list(seen.values()),"historical_unresolved_provenance":history_note,"historical_cost_report":rec(historical_accounting),"fresh_readiness":p["current_readiness_dependency"],"checks":checks,
 "functional_pilot_acceptance_note":"After one completed/rejected native method attempt, max_attempts=1 intentionally stops early: job exit2/noncomparable is expected. Assess attempt_result and raw native identity/features/ledger closure; this is not a full-budget fair result.",
 "historical_cost_gpu_seconds":200,"gpu_jobs_submitted_by_auditor":False}
out=dest/"acceptance.json";out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"status":report["status"],"receipt":rec(out),"recursive_receipts":len(seen),"n_checks":len(checks),"n_targets_metadata_unchanged":7,"n_tasks":2},indent=2))


