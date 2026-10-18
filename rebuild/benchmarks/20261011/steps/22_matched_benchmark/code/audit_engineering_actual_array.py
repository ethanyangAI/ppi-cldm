#!/usr/bin/env python3
"""Root-invoked CPU posthoc independent accounting of a two-task engineering array.
No GPU submission and no generation. Preserves old/new costs and all raw length records.
"""
import argparse,hashlib,importlib.util,json,os,re,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");B=R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source"
CONTRACT=R/"steps/22_matched_benchmark/code/formal_contract_v1/source/formal_benchmark_contract.py"
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--plan",required=True);ap.add_argument("--run-root",required=True);ap.add_argument("--array-job-id",required=True);ap.add_argument("--out",required=True)
 a=ap.parse_args();contract=module("independent_formal_contract",CONTRACT);cpu=contract.cpu_guard()
 producer=module("frozen_budget",B/"paired_budget_benchmark.py");auditor=module("independent_budget",B/"paired_budget_independent.py")
 planpath=Path(a.plan).resolve();plan=producer.read_json(planpath)
 if len(plan["tasks"])!=2 or plan["protocol"].get("max_attempts_safety_limit")!=1:raise ValueError("This wrapper is for the exact two-task engineering pilot only")
 if not re.fullmatch(r"\d+",a.array_job_id):raise ValueError("Numeric Slurm master ID required")
 out=Path(a.out).resolve()
 if out.exists():raise FileExistsError(out)
 runroot=Path(a.run_root).resolve();receipts=[];lengths=[]
 for index in range(2):
  p=runroot/(a.array_job_id+"_"+str(index))/"run_receipt.json"
  run=producer.read_json(p)
  if run["plan"]!=producer.record(planpath) or run["task"]!=plan["tasks"][index]:raise ValueError("Exact array index/task/plan receipt differs")
  receipts.append(producer.record(p))
  lengths.append(dict(run_receipt=receipts[-1],**contract.raw_closure(run,producer.rows_jsonl(producer.verified(run["attempt_ledger"])),
     producer.rows_jsonl(producer.verified(run["sequence_ledger"])),
     producer.rows_jsonl(producer.verified(run["native_screening_ledger"]))if run.get("native_screening_ledger")else[],65)))
 fmt="JobIDRaw,ElapsedRaw,AllocTRES,State,Start,End,NodeList,Partition"
 raw=subprocess.check_output(["sacct","-X","-j",a.array_job_id,"--noheader","--parsable2","--format="+fmt],text=True)
 parsed,_=producer.parse_sacct(raw)
 if any(x["state"]in {"RUNNING","PENDING","COMPLETING","CONFIGURING"}for x in parsed.values()):raise ValueError("Audit only after both actual allocations are terminal")
 account=producer.independent_accounting(plan,receipts,raw)
 cohorts=producer.cohorts(plan,account["inventory"],account["tasks"])
 out.mkdir(parents=True)
 def save(name,value):
  p=out/name;p.write_text(json.dumps(value,indent=2,allow_nan=False)+"\n");return p
 rp=save("run_receipts.json",receipts);sp=out/"sacct_8.txt";sp.write_text(raw)
 acp=save("producer_accounting.json",account);cp=save("producer_cohorts.json",cohorts)
 independent=auditor.audit(planpath,rp,sp,acp,cp);ip=save("independent_acceptance.json",independent)
 previous=R/"steps/22_matched_benchmark/code/pilot13069_array_accounting_13090/report.json"
 old=contract.receipt(previous)
 if old["sha256"]!="09ed8a3d5d0493db99ac75eb262fdeefd0f291feff9b70310570d974752ce93f":raise ValueError("Historical failed cost receipt changed")
 report=dict(status="INDEPENDENT_ENGINEERING_ALLOCATIONS_RAW_LEDGER_ACCOUNTING_PASS",scope="ENGINEERING_ONLY_NOT_FORMAL_OR_SCIENTIFIC_ACCEPTANCE",
    source=contract.receipt(__file__),allocation=cpu,plan=contract.receipt(planpath),
    independent_budget_acceptance=contract.receipt(ip),accounting=contract.receipt(acp),cohorts=contract.receipt(cp),
    run_receipts_input=contract.receipt(rp),raw_sacct=contract.receipt(sp),all_complete_65aa_raw_closure=lengths,
    historical_failed13069_receipt=old,historical_failed_gpu_seconds=200,
    current_gpu_seconds_all_attempts=independent["all_allocated_gpu_seconds"],
    historical_plus_current_engineering_gpu_seconds=200+independent["all_allocated_gpu_seconds"],
    cost_scope="Only preserved array13069 and this engineering array; all other development, supplemental API and common evaluation GPU allocations require separate registry accounting.",
    note="One-attempt safety limit intentionally yields early-stop noncomparable receipts. Native content/stages require separate content acceptance; all actual resource use retained.",
    no_gpu_submission=True)
 final=save("REPORT.json",report)
 print(json.dumps(dict(report=contract.receipt(final),independent_budget_acceptance=contract.receipt(ip),
   allocated_gpu_seconds=independent["all_allocated_gpu_seconds"],all_attempts=independent["all_attempt_count"],
   all_complete_sequence_records=independent["source_sequence_records"]),indent=2))
if __name__=="__main__":main()
