#!/usr/bin/env python3
"""Receipt-bound Chinese report writer and separate CPU filesystem QA. No models."""
import argparse,csv,hashlib,importlib.util,io,json,math,os,re,shutil,subprocess,sys,unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
D=Path(__file__).resolve().parent
FILES=("final_scientific_report.py","test_final_scientific_report.py","final_scientific_report_cpu.sbatch","HANDOFF.md")
SOFTWARE="FINAL_CHINESE_REPORT_TOOL_SOFTWARE_CPU_ACCEPTED"
ACCEPTED="FORMAL13260_FINAL_CHINESE_REPORT_AND_MATRIX_CPU_ACCEPTED"
COMMON="FORMAL_COMMON_RAW_CONTENT_INDEPENDENT_AND112_ACCEPTED_COMPUTATIONAL_ONLY"
COST="ROOT_CURRENT_GPU_SUBMISSION_UNIVERSE_AND_TERMINAL_COST_CPU_ACCEPTED"
PLAN=dict(path=str(R/"steps/22_matched_benchmark/formal_freeze_13257/plan/frozen_plan.json"),bytes=20295,sha256="e913d1bbccd531bf88a73f6ba60e8a0de85bb03ad8bcd3455d8952ca4effe0b6")
STATLIB=dict(path=str(R/"steps/24_benchmark_delivery/frozen/history_policy_13223/code/target_statistics_v2.py"),bytes=8723,sha256="cdad0d2dfb2005c2704178a641c48b40a5268b464cab9587d72ddcdc89f4bf73")
NATIVE=dict(path=str(R/"steps/24_benchmark_delivery/runs/native74_final_v2_13211/native74/acceptance.json"),bytes=9602,sha256="9effb60abceb03ca8c47b8e786f6613486bec96c90dec6aec517a1bd415fcff9")
ENGINES=("boltz","af2")
COHORTS=("uniform_all_complete","native_fixed_top_k")
QUALIFIED={"PASSED_CURRENT_WORKER_SOURCE_OWNERSHIP_AND_SLOT_LINEAGE","PASSED_EXACT_CPU_NATIVE_CACHE_SOURCE_AND_SLOT_BINDING"}
def need(value,message):
 if not value:raise ValueError(message)
def canon(obj):return json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False)
def path(p):
 p=Path(p);need(p.is_absolute()and p.is_relative_to(R)and p.resolve()==p and not p.is_symlink(),"Exact authority path required");return p
def rec(p):
 p=path(p);h=hashlib.sha256()
 with p.open("rb")as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return dict(path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest())
def verify(r,readonly=False):
 need(isinstance(r,dict)and set(r)=={"path","bytes","sha256"}and type(r["bytes"])is int and r["bytes"]>=0 and re.fullmatch("[0-9a-f]{64}",r["sha256"]),"Exact receipt shape required")
 p=path(r["path"]);need(p.is_file()and rec(p)==r,"Receipt byte identity differs: "+str(p))
 need(not readonly or not(p.stat().st_mode&0o222),"Readonly receipt required");return p
def read(p):return json.loads(Path(p).read_text())
def dump(p,obj):
 p=path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("x")as f:json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
 p.chmod(0o444);return rec(p)
def write(p,text):
 p=path(p)
 with p.open("x")as f:f.write(text)
 p.chmod(0o444);return rec(p)
def cli_receipt(p,sha):
 r=rec(p);need(r["sha256"]==sha,"CLI identity mismatch");verify(r,True);return r
def cpu_record(text,jid):
 rows=[s for s in text.splitlines()if re.search(r"\bJobId="+re.escape(jid)+r"(?:\s|$)",s)]
 need(len(rows)==1,"Unique actual CPU record required");f=dict(re.findall(r"(\w+)=(\S*)",rows[0]))
 need(f.get("JobState")=="RUNNING"and f.get("UserId","").startswith("u21111210118(")and f.get("Account")=="u21111210118"and f.get("Partition")=="organ","Actual owned RUNNING organ CPU required")
 need(f.get("NumCPUs","").isdigit()and int(f["NumCPUs"])>=1,"Actual CPU count unavailable")
 reps=[]
 for name in ("TRES","AllocTRES"):
  if name not in f:continue
  need(f[name],"Empty live CPU TRES")
  vals={}
  for token in f[name].split(","):
   need("="in token,"Malformed live CPU TRES");k,v=token.split("=",1);need(k not in vals,"Duplicate live CPU TRES");vals[k]=v
  need(vals.get("cpu","").isdigit()and int(vals["cpu"])==int(f["NumCPUs"]),"Allocated CPU mismatch")
  need(all(v.isdigit()and int(v)==0 for k,v in vals.items()if k.startswith("gres/gpu")),"Actual CPU helper allocated GPU")
  reps.append(vals)
 need(reps and all(v==reps[0]for v in reps),"Missing or inconsistent live CPU TRES")
 return dict(job_id=jid,allocated_GPUs=0,allocated_CPUs=int(f["NumCPUs"]),selected_scheduler_record=rows[0])
def cpu():
 need(os.environ.get("SLURM_JOB_ID","").isdigit(),"Actual Slurm allocation required")
 need(os.environ.get("CUDA_VISIBLE_DEVICES")==""and os.environ.get("JAX_PLATFORMS")=="cpu"and os.environ.get("PYTHONNOUSERSITE")=="1"and os.environ.get("PYTHONDONTWRITEBYTECODE")=="1"and "PYTHONPATH"not in os.environ and os.environ.get("OPENBLAS_NUM_THREADS")=="1","PureCPU import/thread isolation required")
 jid=os.environ["SLURM_JOB_ID"];return cpu_record(subprocess.check_output(["scontrol","show","job",jid,"-o"],text=True),jid)
def unique(rows,key,label):
 result={}
 for row in rows:
  k=key(row);need(k not in result,"Duplicate "+label);result[k]=row
 return result
def finite(x):return type(x)in(int,float)and math.isfinite(x)
def metric(x,low=None,high=None):
 need(x is None or(finite(x)and(low is None or x>=low)and(high is None or x<=high)),"Nonfinite or wrong-unit metric");return x
def slotkey(job,slot):return(job,slot["seed"],slot["model"])
def fixed_matrix(stats,plan):
 p=plan["protocol"];need(plan["status"]=="FROZEN_BEFORE_GENERATION"and p["scientific_scope"]=="COMPUTATIONAL_ONLY","Frozen computational plan required")
 targets=unique(p["targets"],lambda t:t["target_id"],"target")
 need(len(targets)==7 and sum(t["analysis_role"]=="primary"for t in targets.values())==6 and sum(t["analysis_role"]=="diagnostic"for t in targets.values())==1,"Six primary plus one diagnostic required")
 need({m["method_id"]for m in p["methods"]}=={"rf_diffusion","bindcraft"}and len(p["replicate_seeds"])==2 and len(set(p["replicate_seeds"]))==2,"Exact two methods/two seeds")
 tasks=unique(plan["tasks"],lambda t:t["task_id"],"frozen task");need(len(tasks)==28,"All28 arms required")
 expected={(t["target_id"],t["method_id"],t["seed"],coh,eng):t for t in tasks.values()for coh in COHORTS for eng in ENGINES}
 flat=stats["flat_cohort_engine_rows"];actual=unique(flat,lambda r:(r["target_id"],r["method_id"],r["seed"],r["cohort"],r["engine"]),"matrix row")
 need(set(actual)==set(expected)and len(flat)==112,"Complete fixed112 matrix required")
 need(stats["schema"]=="paired-target-statistics.v2"and stats["status"]=="FROZEN_COMPLETE_DENOMINATOR_DESCRIPTIVE_STATISTICS_RECOMPUTED"and stats["n_cohort_engine_rows"]==112 and len(stats["rows"])==56 and stats["n_primary_targets"]==6 and stats["complete_matrix_macro_requires_all_six_pairs"]is True and stats["missing_quality"]=="NULL_NEVER_ZERO"and stats["scientific_scope"]=="COMPUTATIONAL_ONLY"and stats["inference_mode"]=="descriptive_only"and stats["posthoc_target_dropping"]is False,"Accepted fixed descriptive statistics required")
 for key,r in actual.items():
  t=expected[key];need(r["task_id"]==t["task_id"]and r["array_index"]==t["array_index"]and r["analysis_role"]==targets[t["target_id"]]["analysis_role"],"Matrix frozen identity differs")
  n=r["n_selected"];v=r["n_R1_complete"];requested=r["n_requested"];mc=r["model_coverage"]
  need(all(type(x)is int for x in(n,v,requested))and 0<=v<=n<=requested and r["underfilled"]is(n<requested),"Matrix selection denominator differs")
  need(mc["expected"]==n*(3 if r["engine"]=="boltz"else 5)and type(mc["valid"])is int and 0<=mc["valid"]<=mc["expected"],"Matrix fixed model denominator differs")
  quality=metric(r["quality_R1"],0,1)
  need((quality is not None)==(n>0 and v==n),"NULL outcome completeness differs")
  need(r["reason"]==("EMPTY_COHORT"if n==0 else None if quality is not None else"MISSING_PRESELECTED_CANDIDATE_OUTCOME"),"Typed matrix reason differs")
 return flat
def comparison_rules(stats):
 rows=unique(stats["comparisons"],lambda r:(r["engine"],r["cohort"]),"comparison")
 need(set(rows)=={(e,c)for e in ENGINES for c in COHORTS},"Four separate comparison axes required")
 for r in rows.values():
  pairs=unique(r["pairs"],lambda x:x["target_id"],"comparison target")
  need(len(pairs)==6 and r["n_primary_targets"]==6,"All six paired targets required")
  count=sum(v["RF_minus_BindCraft"]is not None for v in pairs.values());complete=count==6
  need(r["n_paired_available"]==count and r["status"]==("COMPLETE_SIX_TARGET_DESCRIPTIVE_COMPARISON"if complete else"FULL_MATRIX_COMPARISON_UNRESOLVED"),"Complete-pair status differs")
  for v in pairs.values():
   a=metric(v["rf_quality_R1"],0,1);b=metric(v["bindcraft_quality_R1"],0,1)
   need(v["RF_minus_BindCraft"]==(a-b if a is not None and b is not None else None),"Paired direction differs")
  for key in("RF_target_median_R1","BindCraft_target_median_R1","paired_macro_mean_RF_minus_BindCraft","paired_macro_median_RF_minus_BindCraft"):
   metric(r[key]);need(complete or r[key]is None,"Incomplete six-target macro must remain NULL")
  need(r["inferential_p_value"]is None and r["inferential_confidence_interval"]is None and r["experimental_probability"]is None,"Unsupported inferential or experimental claim")
 return list(rows.values())
def costs(cost,terminal,plan):
 need(cost["status"]==COST and cost["complete_root_gpu_submission_universe"]is True and cost["allocated_failure_before_manifest_cost_retained"]is True and cost["result_manifests_required_for_cost"]is False and cost["whole_historical_project_cost_claim"]is False,"Actual current allocation closure required")
 rows=terminal["rows"];unique(rows,lambda r:r["logical_id"],"cost logical ID");positive=[]
 for r in rows:
  need(r["phase"]in{"formal_generation","common_review","reference_free_e2e"}and r["submission_kind"]in{"primary","technical_rerun"},"Unbounded cost phase/identity")
  need(type(r["GPU_count"])is int and r["GPU_count"]in{0,1}and type(r["elapsed_seconds"])is int and r["elapsed_seconds"]>=0 and r["actual_GPU_seconds"]==r["GPU_count"]*r["elapsed_seconds"],"Actual GPU numeric cost differs")
  if r["GPU_count"]:positive.append(r)
  else:need(r["allocation_kind"]=="ZERO_UNALLOCATED_CANCEL"and r["state"]=="CANCELLED"and r["elapsed_seconds"]==0,"Zero cost lacks unallocated cancellation")
  need(r["result_manifest_required_for_cost"]is False,"Manifest-based cost exclusion forbidden")
 unique(positive,lambda r:r["raw_id"],"physical allocation ID")
 need(cost["actual_GPU_seconds"]==terminal["actual_GPU_seconds"]==sum(r["actual_GPU_seconds"]for r in rows),"All actual costs differ")
 failure=sum(r["actual_GPU_seconds"]for r in rows if r["state"]!="COMPLETED")
 need(cost["allocated_failure_GPU_seconds"]==terminal["allocated_failure_GPU_seconds"]==failure,"Failure/cancel cost omitted")
 primary={int(r["logical_id"].split("_")[1]):r for r in rows if r["phase"]=="formal_generation"and r["submission_kind"]=="primary"and r["logical_id"].startswith("13260_")}
 need(len(primary)==28 and set(primary)=={t["array_index"]for t in plan["tasks"]},"Actual formal13260 28 allocation costs required")
 return primary,rows
def structure_rows(score,inference,analysis,membership,physical):
 jobs=unique(inference["jobs"],lambda r:r["job_key"],"inference job");targets=unique(analysis["targets"],lambda r:r["target_id"],"analysis target")
 outcomes=unique(score["results"],lambda r:r["job_key"],"scored job");need(set(jobs)==set(outcomes),"Score fixed job universe differs")
 diagnostics=unique(physical["rows"],lambda r:slotkey(r["job_key"],r["slot"]),"physical slot")
 expected={slotkey(j["job_key"],s)for j in jobs.values()for s in j["slots"]}
 need(set(diagnostics)==expected and physical["expected_models"]==score["models_expected"]==len(expected)and physical["status"]=="ALL_FIXED_COMMON_MODEL_INTRINSIC_DIAGNOSTICS_RECORDED"and physical["experimental_binding_or_blockade"]is False,"All fixed physical/score slots required")
 need(physical["policy"]["severe_flag_cutoff_A"]==1.5 and physical["policy"]["severe_flag_operator"]=="<"and physical["policy"]["ranking_or_filter_changes"]is False and physical["policy"]["formal_primary_R1_changes"]is False,"Predeclared separate physical diagnostic required")
 controls=unique(membership["controls"],lambda r:r["blind_id"],"native control")
 need(len(controls)==7,"All seven native controls required")
 members={}
 for m in membership["members"]:members.setdefault(m["blind_id"],[]).append(m)
 result=[]
 for j in jobs.values():
  scored=outcomes[j["job_key"]];models=unique(scored["models"],lambda m:slotkey(j["job_key"],m["slot"]),"score slot")
  need(set(models)=={slotkey(j["job_key"],s)for s in j["slots"]},"Fixed score model slots differ")
  t=targets[j["target_id"]]
  for s in j["slots"]:
   key=slotkey(j["job_key"],s);m=models[key];d=diagnostics[key]
   need(d["confidence_content_status"]==m["status"]and m["status"]in{"VALID","NO_INTERFACE","MODEL_UNRESOLVED"},"Model confidence status differs")
   qualification=d["source_qualification"];need(qualification in QUALIFIED or(qualification=="UNRESOLVED_WORKER_LINEAGE_COORDINATES_ONLY"and m["status"]=="MODEL_UNRESOLVED"and m["R0"]is None and m["R1"]is None),"Unqualified usable confidence/score forbidden")
   distance=metric(d["minimum_distance_A"],0)
   need(d["severe_lt_1p5_A"]==(distance<1.5 if distance is not None else None),"Separate strict physical flag differs")
   raw=[r for r in m.get("raw_files",[])if Path(r["path"]).suffix.lower()==".pdb"]
   need(len(raw)<=1,"Ambiguous scored PDB")
   if m["status"]in{"VALID","NO_INTERFACE"}:need(len(raw)==1 and raw[0]==d["raw_PDB"],"Confidence and coordinate source differ")
   geo=m.get("geometry",{})
   result.append(dict(job_key=j["job_key"],blind_id=j["blind_id"],target_id=j["target_id"],family=t["family"],synthetic=t["synthetic"],engine=j["engine"],variant=j["variant"],seed=s["seed"],model=s["model"],role="NATIVE_PARTNER_CONTROL"if j["blind_id"]in controls else"CANDIDATE",memberships=[dict(task_id=v["task_id"],method_id=v["method_id"],generation_seed=v["seed"],cohort=v["cohort"],cohort_record_id=v["cohort_record_id"])for v in members.get(j["blind_id"],[])],confidence_status=m["status"],reason=m.get("reason"),source_qualification=d["source_qualification"],R0=metric(m["R0"]),R1=metric(m["R1"],0,1),raw_PDB=d["raw_PDB"],reference_complex=t["reference_complex"],global_iptm=metric(m.get("global_iptm"),0,1),binder_plddt_fraction=metric(m.get("binder_plddt_fraction"),0,1),interface_plddt_fraction=metric(m.get("interface_plddt_fraction"),0,1),bidirectional_contact_PAE_A=metric(m.get("bidirectional_contact_PAE_A"),0),geometry=geo,intrinsic_status=d["status"],intrinsic_reason=d.get("reason"),minimum_distance_A=distance,severe_lt_1p5_A=d["severe_lt_1p5_A"],experimental_binding_or_blockade=False))
 need(len(result)==len(expected),"Structure inventory denominator differs")
 native=[r for r in result if r["role"]=="NATIVE_PARTNER_CONTROL"]
 need(len({r["job_key"]for r in native})==20 and len(native)==74,"All native20/74 primary+sensitivity models required")
 return result
def val(x):
 if x is None:return"NULL"
 if type(x)is bool:return"true"if x else"false"
 if isinstance(x,(dict,list)):return canon(x)
 return str(x)
def tsv(rows,fields):
 f=io.StringIO(newline="");w=csv.writer(f,delimiter="\t",lineterminator="\n");w.writerow(fields)
 for r in rows:w.writerow([val(r.get(k))for k in fields])
 return f.getvalue()
def formal_matrix_rows(formal,flat):
 key=lambda r:(r["target_id"],r["method_id"],r["seed"],r["cohort"],r["engine"])
 rows=unique(formal["rows"],key,"formal112 row");need(len(rows)==112 and set(rows)=={key(r)for r in flat},"All formal112 rows must join statistics")
 tasks={}
 for r in flat:
  f=rows[key(r)]
  need(all(f[k]==r[k]for k in("task_id","analysis_role","n_requested","n_selected","underfilled","n_R1_complete","quality_R1")),"Formal112/statistics identity or outcome differs")
  tasks.setdefault(f["task_id"],set()).add(f["generation_status"])
  if f["generation_status"]!="ACCEPTED_FULL_BUDGET":
   need(f["n_selected"]==0 and f["quality_R1"]is None and f["reason"]=="GENERATION_UNRESOLVED_NO_FULL_BUDGET"and f["allocated_gpu_seconds"]is None,"Unqualified generation must retain typed reason/NULL")
  need(f["operational_pass"]is None and f["experimental_probability"]is None,"Formal row experimental/operational claim forbidden")
 need(len(tasks)==28 and all(len(v)==1 for v in tasks.values()),"All28 generation status identities required")
 n=sum(v=={"ACCEPTED_FULL_BUDGET"}for v in tasks.values())
 need(formal["n_accepted_full_budget_tasks"]==n and formal["complete_generation_matrix"]is(n==28),"Actual accepted full-budget count differs")
 return rows
class Evidence:
 def __init__(self):self.rows={}
 def load(self,r,ro=False):
  p=verify(r,ro);obj=read(p);verify(r,ro);self.rows[canon(r)]=r;return obj
 def file(self,r,ro=False):verify(r,ro);self.rows[canon(r)]=r
def load_bundle(request):
 need(request["schema"]=="final-scientific-report-request.v1"and request["scientific_scope"]=="COMPUTATIONAL_ONLY"and request["experimental_binding_or_blockade"]is False,"Explicit computational report request required")
 e=Evidence();c=e.load(request["common_successor"],True);cost=e.load(request["root_gpu_cost"],True)
 need(c["status"]==COMMON and c["n_fixed_cohort_engine_rows"]==112 and c["n_primary_targets"]==6 and c["n_diagnostic_targets"]==1 and c["experimental_binding_or_blockade"]is False and c["workflow_superiority"]is False,"Actual final common112 accepted receipt required")
 producer=e.load(c["common_acceptance"]);stats=e.load(c["statistics"]);physical=e.load(c["intrinsic_target_binder_physical_clearance"]);formal=e.load(c["formal112"]);ind=e.load(c["independent_common"])
 need(producer["status"]=="COMMON_REVIEW_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY"and formal["status"]=="INDEPENDENT_FORMAL112_FAIRNESS_AND_STATISTICS_AUDIT_PASS"and ind["status"]=="RESTORED_RAW_COMMON_SCORES_AND_COHORT_STATISTICS_RECOMPUTED","Actual content/independent formal gates required")
 score=e.load(producer["result"]);membership=e.load(producer["membership"]);inference=e.load(score["plan"]);analysis=e.load(score["analysis_plan"]);pre=e.load(c["preflight"]);prepared=e.load(pre["preparation"]);collection=e.load(prepared["collection"]);cohorts=e.load(collection["files"]["cohorts"]);plan=e.load(PLAN,False)
 need(formal["plan"]==prepared["plan"]==PLAN and prepared["outputs"]["inference_plan"]==score["plan"]==membership["inference_plan"]and prepared["outputs"]["membership"]==producer["membership"]and prepared["outputs"]["analysis_plan"]==score["analysis_plan"],"Operative report input graph differs")
 need(formal["n_explicit_replicate_cohort_engine_rows"]==112 and collection["status"]=="FORMAL_ALLOCATION_NATIVE_AND_COHORT_CLOSURE_ACCEPTED","Actual collection/full112 gate required")
 library=verify(STATLIB,True);e.file(STATLIB,True)
 spec=importlib.util.spec_from_file_location("report_locked_statistics",library);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 need(stats==module.statistics(producer,plan,cohorts,"rf_diffusion","bindcraft"),"Actual frozen descriptive statistics differ")
 terminal=e.load(cost["terminal_costs"]);native=e.load(NATIVE)
 need(native["status"]=="NATIVE74_FULL_RAW_AND_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY"and native["expected_jobs"]==20 and native["expected_models"]==74,"Historical native calibration context differs")
 for key in("formal112","statistics","raw_union","review_allocations"):e.file(c[key],True)
 for r in cost["root_gpu_submission_receipts"]+cost["terminal_numeric_accounting_receipts"]:e.file(r,True)
 e.file(cost["journal_closure"],True);e.file(cost["ledger"],True)
 flat=fixed_matrix(stats,plan);formalrows=formal_matrix_rows(formal,flat);comparisons=comparison_rules(stats);primary,costrows=costs(cost,terminal,plan)
 structures=structure_rows(score,inference,analysis,membership,physical)
 for r in structures:
  if r["raw_PDB"]:e.file(r["raw_PDB"])
  e.file(r["reference_complex"])
 for j in score["results"]:
  for r in j.get("protocol_files",[]):e.file(r)
  for m in j["models"]:
   for r in m.get("raw_files",[])+m.get("derived_files",[]):e.file(r)
 return dict(request=request,common=c,producer=producer,score=score,inference=inference,analysis=analysis,membership=membership,plan=plan,stats=stats,formal=formal,formalrows=formalrows,physical=physical,cost=cost,costrows=costrows,primary_costs=primary,flat=flat,comparisons=comparisons,structures=structures,historical_native=native,evidence=list(e.rows.values()))
def matrix_rows(b):
 targets={r["target_id"]:r for r in b["analysis"]["targets"]}
 out=[]
 for r in b["flat"]:
  t=targets[r["target_id"]];a=b["primary_costs"][r["array_index"]];f=b["formalrows"][(r["target_id"],r["method_id"],r["seed"],r["cohort"],r["engine"])]
  out.append(dict(r,generation_status=f["generation_status"],formal_reason=f["reason"],n_unique_complete_pool=f["n_unique_complete_pool"],n_native_score_missing=f["n_native_score_missing"],n_R0_observed_pass=f["n_R0_observed_pass"],n_R0_unresolved=f["n_R0_unresolved"],sample_R0_pass_fraction=f["sample_R0_pass_fraction"],observed_fixed_cohort_R0_per_GPU_hour=f["observed_fixed_cohort_R0_per_GPU_hour"],comparable_generation_GPU_seconds=f["allocated_gpu_seconds"],family=t["family"],synthetic=t["synthetic"],budget_GPU_seconds=b["plan"]["protocol"]["budget_gpu_seconds"],generation_allocation=a["logical_id"],generation_primary_actual_GPU_seconds=a["actual_GPU_seconds"],generation_terminal_state=a["state"],quality_R0=r["candidate_R0_summary"]["median"]if r["candidate_R0_summary"]else None,statistics_source=b["common"]["statistics"],formal_plan_source=PLAN,root_GPU_cost_source=b["request"]["root_gpu_cost"],scientific_scope="COMPUTATIONAL_ONLY",experimental_binding_or_blockade=False))
 return out
MATRIX_FIELDS=("task_id","array_index","target_id","analysis_role","family","synthetic","method_id","seed","cohort","engine","budget_GPU_seconds","generation_allocation","generation_primary_actual_GPU_seconds","generation_terminal_state","generation_status","formal_reason","n_unique_complete_pool","n_native_score_missing","n_R0_observed_pass","n_R0_unresolved","sample_R0_pass_fraction","observed_fixed_cohort_R0_per_GPU_hour","comparable_generation_GPU_seconds","n_requested","n_selected","underfilled","n_R1_complete","quality_R1","quality_R0","reason","model_coverage","candidate_R1_summary","candidate_R0_summary","statistics_source","formal_plan_source","root_GPU_cost_source","scientific_scope","experimental_binding_or_blockade")
STRUCT_FIELDS=("job_key","blind_id","target_id","family","synthetic","engine","variant","seed","model","role","memberships","confidence_status","reason","source_qualification","R0","R1","raw_PDB","reference_complex","global_iptm","binder_plddt_fraction","interface_plddt_fraction","bidirectional_contact_PAE_A","geometry","intrinsic_status","intrinsic_reason","minimum_distance_A","severe_lt_1p5_A","experimental_binding_or_blockade")
COST_FIELDS=("logical_id","raw_id","submission_id","phase","submission_kind","stage","rerun_of","state","GPU_count","elapsed_seconds","actual_GPU_seconds","allocation_kind","Start","End","node","actual_memory_AllocTRES","result_manifest_required_for_cost")
def median_complete(values,n):
 need(len(values)==n,"Complete median denominator differs")
 if any(v is None for v in values):return None
 for v in values:metric(v)
 s=sorted(values);return(s[(n-1)//2]+s[n//2])/2
def native_rows(b):
 out=[]
 controls={r["blind_id"]:r for r in b["membership"]["controls"]}
 for blind,c in controls.items():
  for eng in ENGINES:
   rows=[r for r in b["structures"]if r["blind_id"]==blind and r["engine"]==eng and r["variant"]=="primary"];n=3 if eng=="boltz"else 5
   need(len(rows)==n,"Native primary model denominator differs")
   out.append(dict(target_id=c["target_id"],engine=eng,n_expected=n,n_contact_valid=sum(r["confidence_status"]=="VALID"for r in rows),n_no_interface=sum(r["confidence_status"]=="NO_INTERFACE"for r in rows),n_typed_unresolved=sum(r["confidence_status"]=="MODEL_UNRESOLVED"for r in rows),R0_median=median_complete([r["R0"]for r in rows],n),R1_median=median_complete([r["R1"]for r in rows],n),partner_target_aligned_CA_RMSD_A_median=median_complete([r["geometry"].get("known_partner_target_aligned_CA_RMSD_A")for r in rows],n),native_contact_recall_median=median_complete([r["geometry"].get("known_partner_native_contact_recall")for r in rows],n),structural_recovery_true=sum(r["geometry"].get("known_partner_structural_recovery")is True for r in rows),source=b["request"]["common_successor"],experimental_binding_or_blockade=False))
 need(len(out)==14,"All native14 rows required");return out
NATIVE_FIELDS=("target_id","engine","n_expected","n_contact_valid","n_no_interface","n_typed_unresolved","R0_median","R1_median","partner_target_aligned_CA_RMSD_A_median","native_contact_recall_median","structural_recovery_true","source","experimental_binding_or_blockade")
def fmt(x):return"不可估计"if x is None else f"{x:.4f}"if finite(x)else str(x)
def render_report(b,native):
 p=b["plan"]["protocol"];lines=["# PPI blocker 工作流正式计算 benchmark 报告","","证据等级：COMPUTATIONAL_ONLY。实验结合或阻断验证：未完成（false）；亲和力、机制、治疗效果与新家族泛化成功率均未由本计算比较确立。","","本报告按实际受验收的固定输入、原始模型复核、描述统计及根提交成本凭据生成。六个主靶标全部保留；人工靶标 BBF111 作为诊断项，单独呈现。结果允许零候选、无界面及不可估计，不预设任一 workflow 优越。","","## 预先冻结的比较与完整分母","",f"七靶标 × 两方法 × 两生成 seed = 28 arms；每 arm GPU 预算 {p['budget_gpu_seconds']} 秒、单 GPU；生成 seed：{p['replicate_seeds']}。方法：RFdiffusion+ProteinMPNN 与 BindCraft。两 cohort × 两复核引擎保留全部 112 行，方法内部原生分数不跨方法直接比较。",f"实际通过完整预算可比门禁 arms：{b['formal']['n_accepted_full_budget_tasks']}/28；完整生成矩阵：{b['formal']['complete_generation_matrix']}。工程失败/非完整预算的空 cohort 单列 generation status 和正式失败原因，不能解释为生物学阴性。",f"均匀 cohort 每次最多 {p['sampling']['uniform_n_per_replicate']} 条；原生分数 top-k 每次最多 {p['sampling']['native_top_k_per_replicate']} 条。均匀池含完整、canonical、冻结 cutoff 前首次出现的 65 aa 序列，包括方法原生拒绝和原生分数不可用项；序列在 task 内去重。","候选 R1 中位数需全部固定模型；arm 中位数需全部预选候选；target 均值需两个固定 seed；全矩阵 macro 需六个主靶标配对全部可估计。缺失值为 NULL，不补零、不事后删除靶标。","Boltz 主引擎：seed31011/31012/31013，3 模型；AF2 次引擎：seed31021，multimer-v3 model1–5，3 recycles、无 template、无 relax，5 模型，分开呈现。R1 为官方 ipSAE10-max 连续端点；计算 R0≥1 不是实验结合阈值。","天然靶点使用冻结 target-only unpaired MSA，binder single；BBF primary single。所有 native control 与各非空均匀 arm 预定 hash 最小项参与天然靶点 Boltz single-MSA 敏感性；BBF 不另设该敏感性。","",f"112 行中空 cohort-engine 行：{b['stats']['n_empty_cohort_engine_rows']}；预选候选结果缺失行：{b['stats']['n_missing_selected_outcome_rows']}。模型总分母：{len(b['structures'])}，所有 primary、sensitivity、native 和候选槽位均保留。","","## 六主靶标配对描述比较","","|引擎|cohort|可用配对/固定6|全矩阵 RF−BindCraft 均值|状态|","|---|---|---:|---:|---|"]
 for c in b["comparisons"]:lines.append(f"|{c['engine']}|{c['cohort']}|{c['n_paired_available']}/6|{fmt(c['paired_macro_mean_RF_minus_BindCraft'])}|{c['status']}|")
 lines+=["","差值方向为 RF−BindCraft；正值仅表示该计算端点更高，未定义实验优越性。若六对不齐，全矩阵 macro 为 NULL。所有比较为描述性；p 值、推断性置信区间和实验成功概率均为 NULL。","","|target|角色|方法|引擎|cohort|两个 seed 的 R1 均值|状态|","|---|---|---|---|---|---:|---|"]
 for r in b["stats"]["rows"]:lines.append(f"|{r['target_id']}|{r['analysis_role']}|{r['method_id']}|{r['engine']}|{r['cohort']}|{fmt(r['quality_R1'])}|{r['status']}|")
 lines+=["","## 原生伙伴恢复与结构证据","","|target|引擎|有效接触/预定|无界面|未解决|R0|R1|伙伴 RMSD Å|contact recall|结构恢复 true/预定|","|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
 for r in native:lines.append(f"|{r['target_id']}|{r['engine']}|{r['n_contact_valid']}/{r['n_expected']}|{r['n_no_interface']}|{r['n_typed_unresolved']}|{fmt(r['R0_median'])}|{fmt(r['R1_median'])}|{fmt(r['partner_target_aligned_CA_RMSD_A_median'])}|{fmt(r['native_contact_recall_median'])}|{r['structural_recovery_true']}/{r['n_expected']}|")
 rows=b["structures"];obs=sum(r["minimum_distance_A"]is not None for r in rows);severe=sum(r["severe_lt_1p5_A"]is True for r in rows);qualified_obs=sum(r["minimum_distance_A"]is not None and r["source_qualification"]in QUALIFIED for r in rows);unqualified_obs=obs-qualified_obs
 lines+=["",f"Intrinsic target–binder heavy-atom 最小距离独立诊断：观察到 {obs}/{len(rows)} 槽位，其中来源资格通过的观察 {qualified_obs}，来源未解决的 coordinate-only 观察 {unqualified_obs}（不成为有效置信结果）；严格 <1.5 Å flag {severe}，其余 {len(rows)-obs} 槽位 typed unresolved/NULL。该 flag 不参与冻结 R1、候选排序或筛选。","结构恢复 flag 沿用冻结 geometry 定义（target recovery RMSD≤2 Å、contact target F1≥0.5）；伙伴 target-aligned RMSD 单列，该 flag 不等于原生伙伴整体姿势已恢复。对齐到已观察实验残基后的原生界面覆盖、接触 F1、原伙伴 <2.5 Å 原子重叠、4/8 Å sensitivity 是刚性几何代理；与 target–binder 自身最小距离是不同轴。未观察 loop 不补作实验坐标；结构恢复失败限制相应靶标解释。","structure_inventory.tsv/json 保留每个固定槽位的 raw PDB 与 reference complex 收据、置信状态、R0/R1、几何代理、intrinsic flag、缺失原因、来源资格、method/cohort membership。共享 blind 候选只保留一次模型槽位，多 membership 单独列出。","历史 native74 CPU 验收仅提供原生控制校准的可追溯背景（20 jobs/74 models），不替代本轮正式 native14 双引擎主模型及全部敏感性；全78 screening/跨家族筛选属于 DEVELOPMENT_ONLY，新家族仍 UNVALIDATED。","","## 实际计算成本与技术失败","","|phase|identity kind|提交槽位|实际GPU分配|未分配取消|GPU秒|其中非COMPLETED成本|","|---|---|---:|---:|---:|---:|---:|"]
 for phase in("formal_generation","common_review","reference_free_e2e"):
  for kind in("primary","technical_rerun"):
   rr=[r for r in b["costrows"]if r["phase"]==phase and r["submission_kind"]==kind]
   lines.append(f"|{phase}|{kind}|{len(rr)}|{sum(r['GPU_count']>0 for r in rr)}|{sum(r['GPU_count']==0 for r in rr)}|{sum(r['actual_GPU_seconds']for r in rr)}|{sum(r['actual_GPU_seconds']for r in rr if r['state']!='COMPLETED')}|")
 lines +=["",f"本轮 root 提交 scope 的总实际 GPU 秒：{b['cost']['actual_GPU_seconds']}；非COMPLETED分配成本：{b['cost']['allocated_failure_GPU_seconds']}。GPU0 未分配取消项单列；已分配失败、超时、取消及 stage_result 尚未生成的成本全部保留。repair 使用新 identity，未与初始结果静默合并。历史 native 缓存不重复计费；这不是整个历史项目总成本。","112 matrix 中 generation cost 是共享 arm 成本，不能按112行重复求和；actual_allocations.tsv 是每次真实 allocation 一行的计费表。生成预算与共同复核/E2E成本分别呈现。","","## 解释边界与交付门禁","","同靶标、同预算与双引擎复核支持固定计算端点比较；任意两蛋白的姿势预测、实验阻断和跨新家族普适性仍需各自独立证据。参考自由 E2E、默认流程集成、完整 source/archive/restore 与 GitHub publication 是否完成，应读取最终交付各自真实门禁；本报告不以计算 benchmark 验收代替那些门禁。","","## 可追溯来源",""]
 for title,r in(("本轮 common112",b["request"]["common_successor"]),("描述统计",b["common"]["statistics"]),("全root GPU成本",b["request"]["root_gpu_cost"]),("正式冻结28计划",PLAN),("native74历史校准",NATIVE)):
  lines.append(f"- {title}：[receipt]({r['path']})；{r['bytes']} bytes；SHA256 {r['sha256']}")
 lines+=["","附件：matrix112.tsv；structure_inventory.tsv/json；native14.tsv；actual_allocations.tsv；report_inputs.json；report_manifest.json。",""]
 return"\n".join(lines)
def expected_artifacts(b):
 native=native_rows(b)
 return{"REPORT_ZH.md":render_report(b,native),"matrix112.tsv":tsv(matrix_rows(b),MATRIX_FIELDS),"structure_inventory.tsv":tsv(b["structures"],STRUCT_FIELDS),"native14.tsv":tsv(native,NATIVE_FIELDS),"actual_allocations.tsv":tsv(b["costrows"],COST_FIELDS)},native
def verify_artifact_contents(artifacts,texts,structures):
 need(set(artifacts)==set(texts)|{"structure_inventory.json"},"Exact report artifact universe required")
 for name,expected in texts.items():
  p=verify(artifacts[name],True);need(p.name==name and p.read_text()==expected,"Report or full matrix content differs: "+name)
 inventory=read(verify(artifacts["structure_inventory.json"],True))
 need(inventory==dict(schema="all-fixed-structure-inventory.v1",rows=structures,expected_models=len(structures),experimental_binding_or_blockade=False),"All fixed structure inventory differs")
 return True
def software_source():
 need(D.is_relative_to(R/"steps/24_benchmark_delivery/frozen")and not(D.stat().st_mode&0o222),"Execute readonly CPU-sealed source")
 return[rec(verify(rec(D/n),True))for n in FILES]
def software_acceptance(r):
 sw=read(verify(r,True));need(sw["status"]==SOFTWARE and sw["source"]==software_source(),"Actual tested report source required")
 tests=read(verify(sw["contracts"],True));need(tests["status"]=="PASS"and tests["tests_run"]==54 and tests["failures"]==0 and tests["errors"]==0,"Actual54 report tool contracts required");return sw
def build(request_receipt,out):
 allocation=cpu();request=read(verify(request_receipt,True));software_acceptance(request["software_acceptance"])
 b=load_bundle(request);texts,native=expected_artifacts(b);artifacts={n:write(out/n,s)for n,s in texts.items()}
 artifacts["structure_inventory.json"]=dump(out/"structure_inventory.json",dict(schema="all-fixed-structure-inventory.v1",rows=b["structures"],expected_models=len(b["structures"]),experimental_binding_or_blockade=False))
 inputs=dump(out/"report_inputs.json",dict(request=request_receipt,operative_receipts=b["evidence"],historical_native74_context=NATIVE))
 return dump(out/"report_manifest.json",dict(schema="final-scientific-report-build.v1",status="CHINESE_REPORT_AND_FULL_MATRIX_BUILT_CPU_QA_PENDING",request=request_receipt,inputs=inputs,artifacts=artifacts,source=software_source(),allocation=allocation,n_fixed_cohort_engine_rows=112,n_primary_targets=6,expected_structure_models=len(b["structures"]),scientific_scope="COMPUTATIONAL_ONLY",experimental_binding_or_blockade=False))
def qa(manifest_receipt,out):
 allocation=cpu();manifest=read(verify(manifest_receipt,True))
 need(manifest["schema"]=="final-scientific-report-build.v1"and manifest["status"]=="CHINESE_REPORT_AND_FULL_MATRIX_BUILT_CPU_QA_PENDING"and manifest["source"]==software_source(),"Actual immutable report build required")
 request=read(verify(manifest["request"],True));software_acceptance(request["software_acceptance"]);b=load_bundle(request);texts,native=expected_artifacts(b)
 verify_artifact_contents(manifest["artifacts"],texts,b["structures"])
 need(manifest["expected_structure_models"]==len(b["structures"])and manifest["n_fixed_cohort_engine_rows"]==112 and manifest["n_primary_targets"]==6 and manifest["scientific_scope"]=="COMPUTATIONAL_ONLY"and manifest["experimental_binding_or_blockade"]is False,"Report content scope/counts differ")
 inputs=read(verify(manifest["inputs"],True));need(inputs==dict(request=manifest["request"],operative_receipts=b["evidence"],historical_native74_context=NATIVE),"Report operative source receipts differ")
 return dump(out/"acceptance.json",dict(schema="final-scientific-report-content-acceptance.v1",status=ACCEPTED,report=manifest["artifacts"]["REPORT_ZH.md"],common_successor=request["common_successor"],statistics=b["common"]["statistics"],root_gpu_cost=request["root_gpu_cost"],matrix=manifest["artifacts"]["matrix112.tsv"],structure_inventory=manifest["artifacts"]["structure_inventory.json"],structure_matrix=manifest["artifacts"]["structure_inventory.tsv"],native14=manifest["artifacts"]["native14.tsv"],actual_allocations=manifest["artifacts"]["actual_allocations.tsv"],report_manifest=manifest_receipt,report_inputs=manifest["inputs"],n_fixed_cohort_engine_rows=112,n_primary_targets=6,n_native_primary_control_engine_rows=14,n_native_all_variant_jobs=20,n_native_all_variant_models=74,n_all_fixed_structure_models=len(b["structures"]),scientific_scope="COMPUTATIONAL_ONLY",experimental_binding_or_blockade=False,full_denominators_preserved=True,all_six_macro_missing_stays_null=True,allocated_failure_before_manifest_cost_retained=True,source=software_source(),allocation=allocation,publication_or_default_workflow_acceptance=False))
def contracts(out):
 allocation=cpu();frozen=R/"steps/24_benchmark_delivery/frozen"/("final_scientific_report_v1_"+os.environ["SLURM_JOB_ID"])/"code";frozen.mkdir(parents=True,exist_ok=False)
 need(not(D.stat().st_mode&0o222),"Reviewed readonly report package")
 for n in FILES:
  p=verify(rec(D/n),True);shutil.copyfile(p,frozen/n);(frozen/n).chmod(0o444)
 frozen.chmod(0o555)
 for n in FILES:
  if n.endswith(".py"):compile((frozen/n).read_bytes(),str(frozen/n),"exec",dont_inherit=True)
  if n.endswith(".sbatch"):subprocess.run(["bash","-n",str(frozen/n)],check=True)
 spec=importlib.util.spec_from_file_location("report_contracts",frozen/FILES[1]);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 with(out/"contracts.txt").open("x")as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
 (out/"contracts.txt").chmod(0o444);tests=dump(out/"contracts.json",dict(status="PASS"if result.wasSuccessful()else"FAIL",tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),log=rec(out/"contracts.txt")))
 need(result.wasSuccessful()and result.testsRun==54,"Meaningful report54 contracts failed")
 source=[rec(frozen/n)for n in FILES]
 return dump(out/"acceptance.json",dict(status=SOFTWARE,source=source,contracts=tests,allocation=allocation,entry=rec(frozen/FILES[0]),CPU_launcher=rec(frozen/FILES[2]),no_scientific_result_report_created=True,new_GPU_submission=False))
def main():
 p=argparse.ArgumentParser();sp=p.add_subparsers(dest="mode",required=True)
 a=sp.add_parser("contracts");a.add_argument("--out",required=True)
 for mode,key in(("build","request"),("qa","manifest")):
  a=sp.add_parser(mode);a.add_argument("--"+key,required=True);a.add_argument("--"+key+"-sha256",required=True);a.add_argument("--out",required=True)
 args=p.parse_args();cpu();out=path(args.out);out.mkdir(parents=True,exist_ok=False)
 try:
  if args.mode=="contracts":result=contracts(out)
  elif args.mode=="build":result=build(cli_receipt(args.request,args.request_sha256),out)
  else:result=qa(cli_receipt(args.manifest,args.manifest_sha256),out)
  print(json.dumps(result,ensure_ascii=False))
 except Exception as error:
  dump(out/"typed_incomplete.json",dict(status="FINAL_SCIENTIFIC_REPORT_TYPED_INCOMPLETE_NO_PROMOTION",error_type=type(error).__name__,error=str(error),mode=args.mode,new_GPU_submission=False,experimental_binding_or_blockade=False))
  raise
if __name__=="__main__":main()
