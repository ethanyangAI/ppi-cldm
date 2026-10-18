#!/usr/bin/env python3
"""Read-only audit of historical pilot13069; CPU-only independent accounting."""
import importlib.util,json,os,re,subprocess,sys,hashlib
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");CODE=R/"steps/22_matched_benchmark/code"
SOURCE=R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source"
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec)
 sys.modules[name]=m;spec.loader.exec_module(m);return m
m=module("pilot_v4_accounting",SOURCE/"paired_budget_benchmark.py")
ind=module("pilot_v4_independent",SOURCE/"paired_budget_independent.py")
jid=os.environ["SLURM_JOB_ID"]
cpu=subprocess.run(["scontrol","show","job",jid,"-o"],check=True,capture_output=True,text=True).stdout
tres=re.search(r"\b(?:AllocTRES|TRES)=(\S+)",cpu)[1]
if re.search(r"\bJobState=(\S+)",cpu)[1]!="RUNNING" or m.parse_alloc_tres_gpu(tres)!=0:
 raise RuntimeError("CPU-only running job required")
dest=CODE/("pilot13069_array_accounting_"+jid);dest.mkdir()
pilot=R/"steps/22_matched_benchmark/engineering_pilot"
planpath=pilot/"plan_v2/frozen_plan.json"
receipts=[m.record(pilot/"runs"/alias/"run_receipt.json") for alias in ["13069_0","13069_1"]]
before={str(p):m.record(p) for alias in ["13069_0","13069_1"]
        for p in sorted((pilot/"runs"/alias).rglob("*")) if p.is_file()}
receiptpath=dest/"run_receipts.json";m.write_exclusive(receiptpath,receipts)
plan=m.validate_frozen_plan(planpath,require_current_orchestrator=False)
reports=[]
for n,fields in [(8,"JobIDRaw,ElapsedRaw,AllocTRES,State,Start,End,NodeList,Partition"),
                 (9,"JobIDRaw,JobID,ElapsedRaw,AllocTRES,State,Start,End,NodeList,Partition")]:
 argv=["sacct","-X","-j","13069","-n","-P","--format="+fields]
 result=subprocess.run(argv,check=True,capture_output=True,text=True)
 raw=dest/("sacct_"+str(n)+"fields.txt");raw.write_text(result.stdout)
 accounting=m.independent_accounting(plan,receipts,result.stdout)
 accounting.update(plan=m.record(planpath),raw_sacct=m.record(raw))
 accountpath=dest/("accounting_"+str(n)+".json");m.write_exclusive(accountpath,accounting)
 cohort=m.cohorts(plan,accounting["inventory"],accounting["tasks"])
 cohort.update(frozen_plan=m.record(planpath),accounting=m.record(accountpath))
 cohortpath=dest/("cohort_"+str(n)+".json");m.write_exclusive(cohortpath,cohort)
 audit=ind.audit(planpath,receiptpath,raw,accountpath,cohortpath)
 auditpath=dest/("independent_"+str(n)+".json");m.write_exclusive(auditpath,audit)
 if accounting["allocated_gpu_seconds_all_attempts"]!=200 or audit["all_allocated_gpu_seconds"]!=200:
  raise RuntimeError("Historical pilot actual resource totals differ from 200 GPU seconds")
 if audit["allocation_count"]!=2 or audit["full_budget_comparable_tasks"]!=0 or audit["complete_generation_matrix"]:
  raise RuntimeError("Historical engineering pilot falsely treated as full scientific matrix")
 rows=[{"method_id":x["task"]["method_id"],"logical_allocation_key":x["logical_allocation_key"],
        "raw_allocation_id":x["raw_allocation_id"],"gpu_count":x["scheduler_allocation"]["gpu_count"],
        "elapsed_seconds":x["scheduler_allocation"]["elapsed_seconds"],"allocated_gpu_seconds":x["allocated_gpu_seconds"],
        "run_status":x["status"],"comparable_full_budget":x["comparable_full_budget"],
        "comparison_exclusions":x["comparison_exclusions"],"attempt_count":x["attempt_count"],
        "attempt_status_counts":x["attempt_status_counts"],"complete_sequence_records":x["sequence_record_count"]}
       for x in accounting["tasks"]]
 reports.append({"fields":n,"argv":argv,"raw_sacct":m.record(raw),"accounting":m.record(accountpath),
                 "cohort":m.record(cohortpath),"independent_acceptance":m.record(auditpath),
                 "all_gpu_seconds":audit["all_allocated_gpu_seconds"],"allocations":rows})
after={str(p):m.record(p) for alias in ["13069_0","13069_1"]
       for p in sorted((pilot/"runs"/alias).rglob("*")) if p.is_file()}
if before!=after:raise RuntimeError("Historical pilot files changed during read-only audit")
report={"status":"HISTORICAL_ENGINEERING_PILOT_PHYSICAL_GPU_ACCOUNTING_AUDIT_PASS",
 "scope":"ENGINEERING_PILOT_ONLY; no full-budget scientific result, no biological superiority claim",
 "cpu_job_id":jid,"cpu_scheduler":cpu,"cpu_alloc_tres":tres,
 "accounting_source":m.record(SOURCE/"paired_budget_benchmark.py"),
 "independent_source":m.record(SOURCE/"paired_budget_independent.py"),
 "plan":m.record(planpath),"run_receipts":receipts,"historical_all_files_unchanged":True,
 "historical_file_count":len(before),"total_actual_gpu_seconds":200,"full_budget_comparable_tasks":0,
 "complete_generation_matrix":False,"exports":reports}
out=dest/"report.json";m.write_exclusive(out,report)
text=["# Pilot 13069 physical GPU accounting audit","",
 "Both methods stopped with engineering failures. Actual GPU cost remains in the ledger: 200 GPU seconds (0.055556 GPU hours). No arm is a comparable full-budget scientific result.",
 "","| Method | Logical task | Physical JobIDRaw | Elapsed s | GPU count | GPU s | Comparable |",
 "|---|---|---:|---:|---:|---:|---|"]
for row in reports[0]["allocations"]:
 text.append("| {method_id} | {logical_allocation_key} | {raw_allocation_id} | {elapsed_seconds} | {gpu_count} | {allocated_gpu_seconds} | False |".format(**row))
text.extend(["","Independent audits passed for the original eight-field export and the optional nine-field diagnostic export. Both derive array aliases from the original hashed scontrol records and count each numeric physical allocation once.",
 "",str(len(before))+" original pilot files were read and remained byte-identical. Old generation sources, receipts and settings were not altered.",
 "","The numeric array master 13069 is the physical allocation ID of task 13069_1; it is not an extra allocation to add.",
 "", "Full report: "+str(out),""])
note=dest/"REPORT.md";note.write_text("\n".join(text))
print(json.dumps({"status":report["status"],"report":m.record(out),"readable_report":m.record(note),
 "total_gpu_seconds":200,"full_budget_comparable_tasks":0,"historical_files_unchanged":len(before)},indent=2))


