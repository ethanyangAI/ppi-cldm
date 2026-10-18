#!/usr/bin/env python3
"""Independent corrected supplemental seed/resource/content gate; CPU only."""
import argparse,importlib.util,json,math,os,random,subprocess
from pathlib import Path
import independent_resource_policy as res
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime"
BASE={"path":str(R/"steps/22_matched_benchmark/code/resource_contract_v1/source/audit_supplemental_engineering.py"),"bytes":16109,"sha256":"467ef3ac8903d672430305c742c906a581deaafcb729f9a82351bce361b5c39d"}
CONFIG={"path":str(S/"runs/supplemental_stage_prepare_13239/outputs/config.json"),"bytes":7020,"sha256":"e26c63af40a729a07cc7ce0dc1675babd74589ef43d1eee3cf93a4b30c427970"}
LAUNCHER={"path":str(S/"frozen/supplemental_launcher_13241/gpu_launcher.sh"),"bytes":2225,"sha256":"d602956154fb396fd14d7737c360d7d35144b4e6ca6c3d1c51eb6dc401e42615"}
COLLECTOR={"path":str(S/"frozen/supplemental_content_collector_13244/audit_supplemental_bindcraft_v1.py"),"bytes":14040,"sha256":"2e830b391503abfc3e36585304ed584106fd2ea528cda3982306a5ce3c51d776"}
SCOPE="ENGINEERING_STAGE_COVERAGE_ONLY_NOT_NATIVE_ACCEPTED_NOT_FORMAL"
need=res.need;rec=res.rec;verify=res.verify;read=res.read
def base():
 p=verify(BASE,True);sp=importlib.util.spec_from_file_location("supplemental_v1_independent",p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 m.CONFIG=CONFIG;m.LAUNCHER=LAUNCHER
 return m
def rng_events(events,root_seed):
    need(root_seed==791205,"Predetermined root seed differs")
    seeded=[(i,x)for i,x in enumerate(events)if x["stage"]=="python_rng_seeded_before_official_constructors"]
    need(len(seeded)==1 and seeded[0][1]["root_seed"]==root_seed and seeded[0][1]["additional_draws"]==0,"Unique preconstructor Python seed proof required")
    start=seeded[0][0];python=random.Random(root_seed);draws=[];constructors=[];numpy_values=[]
    last_epoch=None
    for i,row in enumerate(events):
        need(row["scientific_scope"]==SCOPE and type(row["completed_at_epoch"])in(int,float)and math.isfinite(row["completed_at_epoch"]),"Event scope/timestamp differs")
        need(last_epoch is None or row["completed_at_epoch"]>=last_epoch,"Actual seed/model events not ordered");last_epoch=row["completed_at_epoch"]
        stage=row["stage"]
        if stage=="python_random_randint_observed":
            need(i>start and all(type(row[k])is int for k in("lower","upper","value")),"Python RNG event precedes fixed seed/invalid interval")
            need(row["lower"]<=row["upper"]and python.randint(row["lower"],row["upper"])==row["value"],"Actual original Python randint differs from independent replay")
            draws.append(row)
        elif stage=="actual_mpnn_constructor_key_seed_observed":
            need(i>start and len(draws)==1 and row["seed"]==draws[0]["value"]and row["additional_draws"]==0,"Actual original MPNN Keyseed differs from first Python draw")
            constructors.append(row)
        elif stage=="deterministic_entropy_seed":
            need(i>start and type(row["seed"])is int and 0<=row["seed"]<2**31-1,"NumPy entropy seed invalid");numpy_values.append(row["seed"])
    need(len(constructors)==1 and draws,"Actual original MPNN constructor seed proof required")
    import numpy as np
    numpy=np.random.default_rng(root_seed);expected=[int(numpy.integers(0,2**31-1))for _ in numpy_values]
    need(expected==numpy_values,"Actual numpy fallback differs from independent PCG64 replay")
    return {"status":"ALL_ACTUAL_PYTHON_RANDINT_AND_NUMPY_ENTROPY_SEEDS_INDEPENDENTLY_REPLAYED","root_seed":root_seed,
      "python_randint_count":len(draws),"numpy_fallback_count":len(numpy_values),"actual_mpnn_key_seed":constructors[0]["seed"],
      "python_stream":"random.Random(root_seed).randint(actual_lower,actual_upper)","numpy_stream":"default_rng(root_seed).integers(0,2**31-1)",
      "additional_gpu_model_rng_draws":0}
def audit(actual_job,content_acceptance,rng_acceptance,history_audit,report_dir):
    allocation=res.cpu_guard();D=Path(report_dir);need(not D.exists(),"Never overwrite evidence");D.mkdir(parents=True)
    m=base();verify(CONFIG,True);verify(LAUNCHER,True);verify(COLLECTOR,True);cfg=read(CONFIG["path"])
    graph=m.receipt_graph(cfg);fixed=read(verify(cfg["fixed_pose"],True));m.receipt_graph(fixed)
    need(fixed["scope"]==SCOPE and fixed["selection_rule"]=="First and only actual trajectory; no quality-based pose or seed selection"and fixed["trajectory"]["native_termination"]=="Clashing","Predetermined real rejected pose changed")
    need(cfg["repair_of_supplemental_gpu_job"].startswith("13234 PythonKey seed not reconstructable"),"Deterministic replay lacks explicit unresolved history provenance")
    out=S/("runs/bindcraft_supplemental_gpu_"+str(actual_job))/"outputs"
    argv=["sacct","-X","-P","-n","-j",str(actual_job),"--format=JobIDRaw,ElapsedRaw,AllocTRES,State,Start,End,NodeList,Partition"]
    raw=subprocess.check_output(argv,text=True);(D/"sacct_raw.txt").write_text(raw);rows,excluded=res.accounting_rows(raw)
    need(set(rows)=={str(actual_job)}and str(actual_job)not in("13234","13175","13181","13069","13070"),"Exactly one new physical supplementary allocation")
    final=res.terminal_allocation(rows[str(actual_job)],actual_job,2,1)
    guard=read(out/"gpu_allocation.json");need(str(guard["job_id"])==str(actual_job),"Guard allocation differs")
    ownership=m.independent_ownership(guard,D/"ownership")
    _,fields,_=res.selected(guard["scheduler_record"],actual_job);need(fields["Command"]==LAUNCHER["path"],"Unfrozen supplemental launcher command")
    start=int(__import__("datetime").datetime.fromisoformat(fields["StartTime"]).timestamp())
    timing=m.timing_contract((out.parent/"launcher_budget.txt").read_text(),(out.parent/"scheduler_at_launch.txt").read_text(),guard,actual_job,start)
    need(timing["start"]==final["start"]and timing["node"]==final["node"]and final["partition"]=="organ","Initial/terminal allocation differs")
    m.worker_contract(read(out/"worker_result.json"),actual_job)
    pool=m.raw_pool_contract(read(out/"mpnn_pool.json"),m.jsonl_complete(out/"supplemental_sequences.jsonl"))
    need(not(out/"sequences.jsonl").exists()and not(out/"native_screening.jsonl").exists(),"Supplemental leaked into formal native inventory")
    acceptance=read(verify(rec(content_acceptance)));m.content_contract(acceptance,out,cfg,actual_job);native=m.native_content(acceptance,out,cfg,actual_job)
    events=m.jsonl_complete(out/"supplemental_events.jsonl");rng=rng_events(events,cfg["seed"])
    rng_doc=read(verify(rec(rng_acceptance)));need(rng_doc["status"]=="ACTUAL_OFFICIAL_PYTHON_KEY_SEEDS_AND_NUMPY_ENTROPY_RECOMPUTED_FROM_PREDECLARED_ROOT_SEED"and rng_doc["root_seed"]==cfg["seed"],"Independent content collector actual seed status/root differs")
    need(rng_doc["events"]==rec(out/"supplemental_events.jsonl")and rng_doc["additional_model_rng_draws"]==0,"Collector RNG proof did not join exact original event universe")
    need(rng_doc["official_python_key_sources"]==cfg["python_key_sources"],"Official installed/vendor Key source proof differs")
    for row in acceptance["actual_native_predictions"]:
        doc=read(verify(row["archive"]));need(doc["actual_model_rng_seed"]==791205,"Actual explicit native AF2 model seed differs")
        key=doc["actual_model_rng_key_after_predict"];need(type(key)is list and len(key)==2 and all(type(x)is int and 0<=x<=2**32-1 for x in key),"Actual native AF2 key-after-predict missing")
    main=read(verify(m.MAIN,True));need(main["all_allocated_gpu_seconds"]==591 and main["allocation_count"]==main["expected_tasks"]==2,"Main exact2/591 altered")
    historical=read(verify(rec(history_audit),True));need(historical["allocated_gpu_seconds"]==381 and historical["accounting"]["actual"]["raw_allocation_id"]=="13234","Old unseeded supplemental cost authority differs")
    report={"schema":"independent_seeded_supplemental_engineering.v1","status":"INDEPENDENT_CURRENT_SEEDED_SUPPLEMENTAL_BUDGET_OWNERSHIP_RAW_CONTENT_AND_RNG_AUDIT_PASS",
      "scientific_scope":SCOPE,"coverage_mode":"supplemental_api_coverage","full_budget_comparable":False,"formal_sequences":0,"native_accepted_sequences":0,
      "source":rec(__file__),"resource_source":rec(res.__file__),"historical_audit_library":BASE,"collector_source":COLLECTOR,"cpu_allocation":allocation,
      "config":CONFIG,"launcher":LAUNCHER,"content_acceptance":rec(content_acceptance),"rng_acceptance":rec(rng_acceptance),"sacct_argv":argv,"sacct_raw":rec(D/"sacct_raw.txt"),
      "actual_allocation":final,"allocated_gpu_seconds":final["allocated_gpu_seconds"],"actual_allocated_cpu_count":2,"ownership":ownership,
      "launcher_timing":timing,"pool":pool,"raw_sequence_stream":rec(out/"supplemental_sequences.jsonl"),"native_content":native,"rng":rng,"rng_events":rec(out/"supplemental_events.jsonl"),
      "config_graph_receipt_count":len(graph),"main_accounting_unchanged":m.MAIN,"main_gpu_seconds_excluded":591,
      "unseeded_supplemental_history":rec(history_audit),"unseeded_history_gpu_seconds_excluded":381,"cancelled_prior13229_gpu_seconds":0,
      "interpretation":"Current deterministic later API coverage on first fixed scientifically rejected trajectory; all20 supplemental sequences excluded from formal/native accepted candidate universe"}
    (D/"acceptance.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps(report));return report
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--actual-job",required=True);ap.add_argument("--content-acceptance",required=True);ap.add_argument("--rng-acceptance",required=True);ap.add_argument("--history-audit",required=True);ap.add_argument("--report-dir",required=True);a=ap.parse_args()
 audit(a.actual_job,a.content_acceptance,a.rng_acceptance,a.history_audit,a.report_dir)
if __name__=="__main__":main()

