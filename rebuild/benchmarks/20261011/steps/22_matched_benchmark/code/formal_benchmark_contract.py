#!/usr/bin/env python3
"""Independent formal 28-task/112-row fairness contracts; CPU only, no generation.
No imports from production orchestration or common scorer. Synthetic unit fixtures are software tests.
"""
import argparse,hashlib,json,math,os,re,statistics,subprocess
from collections import Counter
from pathlib import Path
AA=set("ACDEFGHIKLMNPQRSTVWY")
POLICY="complete_selected_candidate_median_then_both_replicate_mean"
PRIMARY={"MDM2_1YCR","KEAP1_2FLU","EGFR_DIII_1IVO","BCLXL_2M04","HRAS_4G0N","CRK_SH3_1CKA"}
DIAGNOSTIC={"BBF111_9HAG"}
COHORTS=("uniform_all_complete","native_fixed_top_k")
ENGINES={"boltz":3,"af2":5}
TERMINAL={"COMPLETED","SCIENTIFIC_REJECT","ENGINEERING_FAILURE","TIMED_OUT_BOUNDARY","INTERRUPTED"}
METHODS=("rf_diffusion","bindcraft")
def need(ok,message):
    if not ok:raise ValueError(message)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def finite(x):return type(x)in(int,float)and math.isfinite(x)
def unique(rows,key,label):
    result={}
    for row in rows:
        k=key(row);need(k not in result,"Duplicate "+label+": "+str(k));result[k]=row
    return result
def formal_protocol(p):
    exact={"schema":"paired-budget-v1","protocol_id":"PPI-PAIRED-BENCHMARK-20261011","scientific_scope":"COMPUTATIONAL_ONLY",
      "execution_mode":"persistent_session","replicate_seeds":[21011,21012],"binder_length":65,
      "gpu_count":1,"budget_gpu_seconds":3600,"shutdown_reserve_seconds":10,"accounting_tolerance_seconds":2,
      "hardware":{"gpu_name":"NVIDIA A100-PCIE-40GB","minimum_memory_mib":40000},
      "sampling":{"salt":"PPI-PAIRED-20261011-FIXED-BEFORE-GENERATION","uniform_n_per_replicate":3,"native_top_k_per_replicate":2},
      "aggregation_policy":POLICY,
      "completion_policy":{"allowed_scheduler_states":["COMPLETED","TIMEOUT"],"requires_durable_receipt_and_complete_raw_ledger":True,"generation_cutoff_wall_seconds":3590,"all_gpu_children_terminated_before_receipt":True,"actual_gpu_seconds":3600,"tolerance_seconds":2,"engineering_failure_is_comparable":False},
      "common_review_gate":{"score":"R0","threshold":1.0,"operator":">=","aggregation":"all_required_models_median","scope":"COMPUTATIONAL_ONLY"},
      "common_review_primary":{"engine":"boltz","models":3,"seeds":[31011,31012,31013],"endpoint":"R1_official_ipSAE_10A_max_continuous","operational_pass":None},
      "common_review_secondary":{"engine":"af2","models":5,"seed":31021,"model_order":[1,2,3,4,5],"endpoint":"separate_R1_R0","pooled_with_primary":False}}
    for key,value in exact.items():need(p.get(key)==value,"Frozen formal field differs: "+key)
    need("max_attempts_safety_limit"not in p,"Formal scientific throughput cannot stop at engineering max-attempt count")
    need(p["inference"]["mode"]=="descriptive_only","Six-target evidence is descriptive only")
    ts=unique(p["targets"],lambda t:t["target_id"],"target")
    need(set(ts)==PRIMARY|DIAGNOSTIC,"Exact seven target identities required")
    need(all(ts[t]["analysis_role"]=="primary"for t in PRIMARY)and all(ts[t]["analysis_role"]=="diagnostic"for t in DIAGNOSTIC),"Exact target role mapping required")
    need([m["method_id"]for m in p["methods"]]==list(METHODS),"Exact two method arms/effect direction")
    return p
def task_matrix(p):
    rows=[]
    for t in p["targets"]:
        for seed in p["replicate_seeds"]:
            pair={"protocol_id":p["protocol_id"],"target_id":t["target_id"],"seed":seed}
            for m in p["methods"]:
                base=dict(pair,method_id=m["method_id"])
                rows.append(dict(base,task_id=digest(base)[:24],pair_id=digest(pair)[:24],budget_gpu_seconds=3600,array_index=len(rows)))
    return rows
def raw_closure(run,attempts,events,updates,binder_length=65):
    """Checks every complete record, including rejected, score-NA and boundary-observed records."""
    tid=run["task"]["task_id"];need(run["attempt_count"]==len(attempts),"Attempt denominator differs")
    need([a["attempt_index"]for a in attempts]==list(range(len(attempts))),"Contiguous terminal attempt ledger required")
    need(all(a["status"]in TERMINAL for a in attempts),"Unrecorded terminal attempt outcome")
    ids=unique(events,lambda e:(e["attempt_index"],e["sequence_record_id"]),"original sequence ID")
    counts=Counter();before=Counter();uniq=set();native=Counter();native_before=Counter()
    for e in events:
        need(e["task_id"]==tid and e["attempt_index"]in range(len(attempts)),"Sequence does not join raw attempt")
        for key in ("target_id","method_id","seed"):need(e[key]==run["task"][key],"Sequence identity differs: "+key)
        seq=e["sequence"];need(isinstance(seq,str)and len(seq)==binder_length and set(seq)<=AA,"ALL complete raw sequences must be canonical fixed65aa; no accepted-only length filtering")
        need(hashlib.sha256(seq.encode()).hexdigest()==e["sequence_sha256"],"Raw sequence SHA mismatch")
        need(type(e["observed_before_generation_cutoff"])is bool,"Cutoff eligibility must be explicit bool")
        need(finite(e["observed_at_epoch"]),"Observed timestamp invalid")
        need(not e["observed_before_generation_cutoff"]or e["observed_at_epoch"]<=run["generation_cutoff_epoch"]+.01,"Post-cutoff sequence marked eligible")
        need(e["internal_acceptance"]is None or type(e["internal_acceptance"])is bool,"Native acceptance type invalid")
        need(e["native_score"]is None or finite(e["native_score"]),"Native score invalid")
        counts[e["attempt_index"]]+=1;before[e["attempt_index"]]+=e["observed_before_generation_cutoff"];uniq.add(e["sequence_sha256"])
    source_updates=unique(updates,lambda u:(u["attempt_index"],u["source_line_number"]),"native update source line")
    for u in source_updates.values():
        key=(u["attempt_index"],u["sequence_record_id"]);need(key in ids and u["task_id"]==tid,"Native update lost original complete sequence")
        need(type(u["observed_before_generation_cutoff"])is bool and finite(u["observed_at_epoch"]),"Native update eligibility invalid")
        need(not u["observed_before_generation_cutoff"]or u["observed_at_epoch"]<=run["generation_cutoff_epoch"]+.01,"Post-cutoff native score marked eligible")
        need(u["internal_acceptance"]is None or type(u["internal_acceptance"])is bool,"Updated native acceptance type invalid")
        need(u["native_score"]is None or finite(u["native_score"]),"Updated native score invalid")
        native[u["attempt_index"]]+=1;native_before[u["attempt_index"]]+=u["observed_before_generation_cutoff"]
    for a in attempts:
        i=a["attempt_index"]
        need(a["complete_sequence_records"]==counts[i]and a["precutoff_sequence_records"]==before[i],"All-attempt raw sequence denominator differs")
        need(a.get("screening_update_records",0)==native[i]and a.get("precutoff_screening_update_records",0)==native_before[i],"Native dual-stream denominator differs")
    return {"n_attempts":len(attempts),"n_complete_raw_records":len(events),"n_unique_sequence_identities":len(uniq),
            "n_pre_cutoff_raw_records":sum(before.values()),"n_native_updates":len(updates),"all_complete_length":binder_length}
def generation_matrix(plan,accounting,cohorts,independent):
    p=formal_protocol(plan["protocol"]);expected=task_matrix(p);need(plan["tasks"]==expected,"Exact frozen28 task matrix differs")
    need(independent["status"]=="INDEPENDENT_BUDGET_LEDGER_AND_COHORT_AUDIT_PASS","Independent raw accounting required")
    need(independent["expected_tasks"]==28,"Independent full denominator differs")
    tasks={x["task_id"]:x for x in expected}
    allocations=unique(accounting["tasks"],lambda r:r["raw_allocation_id"],"physical allocation")
    accepted={};cost=0
    for row in allocations.values():
        t=row["task"];need(t["task_id"]in tasks and t==tasks[t["task_id"]],"Unfrozen allocated task")
        a=row["scheduler_allocation"];need(a["raw_allocation_id"]==row["raw_allocation_id"],"Raw allocation ID differs")
        need(a["gpu_count"]==1 and row["allocated_gpu_seconds"]==a["elapsed_seconds"],"Actual AllocTRES GPU accounting differs")
        cost+=row["allocated_gpu_seconds"]
        hardware=row["hardware"]["gpus"]
        hmatch=len(hardware)==1 and hardware[0]["name"]==p["hardware"]["gpu_name"]and hardware[0]["memory_total_mib"]>=40000
        engineering=sum(row["attempt_status_counts"].get(st,0)for st in ("ENGINEERING_FAILURE","INTERRUPTED"))>0
        full=row["status"]=="BUDGET_EXHAUSTED_WITH_EXPLICIT_BOUNDARY_CENSORING"
        comparable=full and not engineering and hmatch and a["state"]in("COMPLETED","TIMEOUT")and abs(row["allocated_gpu_seconds"]-3600)<=2
        need(row["comparable_full_budget"]==comparable,"Full-budget engineering/hardware/TRES gate differs")
        if comparable:
            need(t["task_id"]not in accepted,"Post-result choice among duplicate full-budget allocations")
            accepted[t["task_id"]]=row
    need(cost==accounting["allocated_gpu_seconds_all_attempts"]==independent["all_allocated_gpu_seconds"],"All attempts GPU cost differs")
    need(independent["full_budget_comparable_tasks"]==len(accepted)and independent["complete_generation_matrix"]==(len(accepted)==28),"Independent full-matrix gate differs")
    coverage=unique(cohorts["coverage"],lambda c:c["task"]["task_id"],"coverage task")
    need(set(coverage)==set(tasks),"Coverage must retain every frozen28 task")
    selected=unique(cohorts["selected"],lambda c:c["cohort_record_id"],"selected cohort member")
    group=Counter();seqs={}
    for c in selected.values():
        tid=c["task_id"];need(tid in tasks and c["cohort"]in COHORTS,"Unknown selected cohort/task")
        for field in("target_id","method_id","seed"):need(c[field]==tasks[tid][field],"Selected target/method/replicate differs")
        need(len(c["sequence"])==65 and set(c["sequence"])<=AA and hashlib.sha256(c["sequence"].encode()).hexdigest()==c["sequence_sha256"],"Selected sequence identity/65aa differs")
        key=(tid,c["cohort"],c["sequence_sha256"]);need(key not in seqs,"Duplicate sequence within task/cohort");seqs[key]=c
        need(tid in accepted and c["primary_run_receipt"]==accepted[tid]["run_receipt"],"Engineering-failed/alternate allocation entered cohort")
        group[(tid,c["cohort"])]+=1
    for tid,c in coverage.items():
        need(c["task"]==tasks[tid],"Coverage task definition differs")
        need((c["comparison_status"]=="ACCEPTED_FULL_BUDGET")==(tid in accepted),"Coverage full-budget status differs")
        need(c["primary_run_receipt"]==(accepted[tid]["run_receipt"]if tid in accepted else None),"Coverage allocation routing differs")
        for cohort,k in zip(COHORTS,(3,2)):
            n=group[(tid,cohort)];v=c[cohort]
            need(v=={"requested":k,"selected":n,"underfilled":n<k}and 0<=n<=k,"Fixed requested/selected/underfill denominator differs")
        need(c[COHORTS[0]]["selected"]==min(c["n_unique_complete"],3),"Uniform pool selection silently lost complete identities")
        need(c[COHORTS[1]]["selected"]==min(c["n_native_score_available"],2),"Native fixed top-k denominator differs")
        need(c["n_native_score_missing"]==c["n_unique_complete"]-c["n_native_score_available"],"Missing native score denominator differs")
        if tid not in accepted:need(c["n_unique_complete"]==0,"Unaccepted generation cannot define primary cohort")
    return {"tasks":tasks,"coverage":coverage,"accepted":accepted,"selected":selected,"all_gpu_seconds":cost}
def explicit_evaluation_rows(protocol,coverage,selected,common,allocated_gpu_seconds_by_task=None):
    """Always returns28x2cohortx2engine=112 rows; empty quality remains null."""
    p=formal_protocol(protocol);allocated_gpu_seconds_by_task=allocated_gpu_seconds_by_task or {};tasks={t["task_id"]:t for t in task_matrix(p)}
    cv=unique(coverage,lambda x:x["task"]["task_id"],"coverage")
    need(set(cv)==set(tasks),"Evaluation full task denominator differs")
    members=unique(selected,lambda x:x["cohort_record_id"],"cohort member")
    groups={};known_keys=set()
    for x in members.values():
        need(x["task_id"]in tasks and x["cohort"]in COHORTS,"Evaluation unknown task/cohort")
        groups.setdefault((x["task_id"],x["cohort"]),[]).append(x)
    def key(x):return(x["target_id"],x["method_id"],x["seed"],x["cohort"],x["engine"])
    summaries=unique(common["cohort_summaries"],key,"common cohort summary")
    outcomes={}
    for engine in ENGINES:
        outcomes[engine]=unique(common["outcomes"][engine],lambda x:x["cohort_record_id"],"common outcome "+engine)
        need(set(outcomes[engine])<=set(members),"Unknown evaluator member")
        for out in outcomes[engine].values():
            need(type(out["evaluable"])is bool,"Evaluator evaluability must be bool")
            need((type(out["pass"])is bool)if out["evaluable"]else out["pass"]is None,"Unresolved outcome must remain null")
    rows=[]
    for task in tasks.values():
        cov=cv[task["task_id"]];accepted=cov["comparison_status"]=="ACCEPTED_FULL_BUDGET"
        for cohort,k in zip(COHORTS,(3,2)):
            selected_group=groups.get((task["task_id"],cohort),[]);n=len(selected_group)
            need(cov[cohort]["selected"]==n and cov[cohort]["requested"]==k,"Selected vs coverage denominator differs")
            for engine,nmodels in ENGINES.items():
                skey=(task["target_id"],task["method_id"],task["seed"],cohort,engine);known_keys.add(skey)
                s=summaries.get(skey);quality=None;reason=None
                if not accepted:
                    need(n==0,"Unaccepted generation has selected candidates");reason="GENERATION_UNRESOLVED_NO_FULL_BUDGET"
                elif n==0:reason="EMPTY_COHORT"
                elif s is None:reason="MISSING_PRESELECTED_COHORT_SUMMARY"
                else:
                    need(s["n_selected"]==n,"Common summary lost selected candidate")
                    need(s.get("operational_pass")is None,"No operational family transfer claim")
                    v=s["R1_candidates"];need(v["n_expected"]==n and v["n_valid"]==s["n_R1_complete"],"R1 candidate denominator differs")
                    need(0<=s["n_R1_complete"]<=n,"Impossible complete-candidate count")
                    mc=s["model_coverage"];need(mc["expected"]==n*nmodels and 0<=mc["valid"]<=mc["expected"],"Frozen common model denominator differs")
                    complete=s["n_R1_complete"]==n and mc["valid"]==mc["expected"]
                    need((finite(v["median"]))if complete else v["median"]is None,"Missing selected/model quality must remain null")
                    quality=v["median"]if complete else None;reason=None if complete else "MISSING_PRESELECTED_CANDIDATE_OUTCOME"
                if n==0 and s is not None:
                    need(s["n_selected"]==0 and s["n_R1_complete"]==0 and s["R1_candidates"]["median"]is None,"Empty cohort fabricated quality")
                outs=[outcomes[engine].get(m["cohort_record_id"])for m in selected_group]
                r0complete=all(o is not None and o["evaluable"]for o in outs)
                missing=sum(o is None or not o["evaluable"]for o in outs);npass=sum(o is not None and o["evaluable"]and o["pass"]for o in outs)
                if missing and quality is not None:
                    # R0 and R1 have separate evaluability; only absence of the entire member invalidates R1.
                    need(all(o is not None for o in outs),"Complete R1 claimed for entirely missing preselected member outcome")
                rows.append(dict(task_id=task["task_id"],target_id=task["target_id"],method_id=task["method_id"],seed=task["seed"],
                    analysis_role=next(t["analysis_role"]for t in p["targets"]if t["target_id"]==task["target_id"]),cohort=cohort,engine=engine,
                    generation_status=cov["comparison_status"],n_requested=k,n_selected=n,underfilled=n<k,
                    n_unique_complete_pool=cov["n_unique_complete"],n_native_score_missing=cov["n_native_score_missing"],
                    n_R1_complete=0 if s is None else s["n_R1_complete"],quality_R1=quality,reason=reason,
                    n_R0_observed_pass=npass,n_R0_unresolved=missing,sample_R0_pass_fraction=npass/n if n>0 and r0complete else None,
                    observed_fixed_cohort_R0_per_GPU_hour=npass/(allocated_gpu_seconds_by_task.get(task["task_id"],3600)/3600)if accepted and r0complete else None,
                    allocated_gpu_seconds=allocated_gpu_seconds_by_task.get(task["task_id"])if accepted else None,
                    operational_pass=None,experimental_probability=None))
    need(set(summaries)<=known_keys,"Unknown target/method/seed/cohort/engine summary")
    need(len(rows)==112,"Explicit112 row denominator differs")
    return rows
def strict_primary_slots(inference,scored,membership,selected):
    members=unique(membership["members"],lambda m:m["cohort_record_id"],"blind membership")
    selected_by=unique(selected,lambda m:m["cohort_record_id"],"selected record")
    need(set(members)==set(selected_by),"Membership lost preselected member")
    for rid,m in members.items():
        for k,v in selected_by[rid].items():need(m.get(k)==v,"Blind membership changed cohort identity: "+k)
    jobs=unique(inference["jobs"],lambda j:j["job_key"],"inference job");scores=unique(scored["results"],lambda j:j["job_key"],"scored job")
    need(set(jobs)==set(scores),"Missing fixed common job")
    primary=unique([j for j in jobs.values()if j["variant"]=="primary"],lambda j:(j["blind_id"],j["engine"]),"primary blind engine")
    for m in members.values():
        for engine in ENGINES:need((m["blind_id"],engine)in primary,"Preselected member lacks common engine")
    for j in jobs.values():
            engine=j["engine"];need(engine in ENGINES,"Unknown common engine");n=ENGINES[engine];s=scores[j["job_key"]]
            need(j["variant"]=="primary"or(j["variant"]=="single_sensitivity"and engine=="boltz"),"Unknown common MSA sensitivity job")
            slots=[{"seed":seed,"model":0}for seed in(31011,31012,31013)]if engine=="boltz"else[{"seed":31021,"model":i}for i in(1,2,3,4,5)]
            need(j["expected_models"]==n and j["slots"]==slots,"Frozen required model slots differ")
            got=unique(s["models"],lambda v:canonical(v["slot"]),"scored model slot")
            need(set(got)=={canonical(x)for x in slots}and len(s["models"])==n,"Duplicate/missing exact common model slot")
            for v in s["models"]:
                need(v["R1"]is None or finite(v["R1"]),"Nonfinite R1 model")
                need(v["R0"]is None or finite(v["R0"]),"Nonfinite R0 model")
            for axis in("R0","R1"):
                vals=[v[axis]for v in s["models"]];complete=all(v is not None for v in vals)
                need(s[axis]["n_expected"]==n and s[axis]["n_valid"]==sum(v is not None for v in vals),"Common model summary denominator differs")
                need(s[axis]["median"]==(statistics.median(vals)if complete else None),"All required model median differs")
            need(s.get("operational_pass")is None and s.get("experimental_probability")is None and s.get("experimental_blockade")is False,"Unsupported experimental/operational claim")
    return {"selected_members":len(members),"primary_blind_engine_jobs":len(primary),"fixed_slots_validated":True}
def continuous_summary(values,expected):
    valid=sorted(float(x)for x in values if finite(x));complete=len(values)==expected and len(valid)==expected
    def quantile(q):
        z=(len(valid)-1)*q;lo=math.floor(z);hi=math.ceil(z)
        return valid[lo]+(valid[hi]-valid[lo])*(z-lo)
    q25=quantile(.25)if complete else None;q75=quantile(.75)if complete else None
    return dict(n_expected=expected,n_observed=len(values),n_valid=len(valid),n_missing=max(expected-len(valid),0),
        median=statistics.median(valid)if complete else None,observed_only_median=statistics.median(valid)if valid else None,
        q25=q25,q75=q75,IQR=q75-q25 if complete else None,min=min(valid)if valid else None,max=max(valid)if valid else None)
def scalar_equal(x,y):
    return math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-12)if finite(x)and finite(y)else x==y
def common_candidate_summaries(scored,membership,common):
    scores=unique([s for s in scored["results"]if s["variant"]=="primary"],lambda s:(s["blind_id"],s["engine"]),"common primary summary")
    groups={}
    for member in membership["members"]:
        for engine in ENGINES:
            key=(member["target_id"],member["method_id"],member["seed"],member["cohort"],engine)
            need((member["blind_id"],engine)in scores,"Membership missing blind primary score")
            groups.setdefault(key,[]).append(scores[(member["blind_id"],engine)])
    actual=unique(common["cohort_summaries"],lambda s:(s["target_id"],s["method_id"],s["seed"],s["cohort"],s["engine"]),"unblinded common summary")
    need({k for k,v in actual.items()if v["n_selected"]>0}==set(groups),"Nonempty selected cohort summary denominator differs")
    for key,candidates in groups.items():
        a=actual[key];need(a["n_selected"]==len(candidates),"Candidate denominator differs from membership")
        for axis in("R0","R1"):
            vals=[c[axis]["median"]for c in candidates];summary=continuous_summary(vals,len(candidates))
            for field,value in a[axis+"_candidates"].items():
                need(field in summary and scalar_equal(value,summary[field]),"Scored-to-cohort "+axis+" summary differs: "+field)
            if axis=="R1":
                need(a["n_R1_complete"]==summary["n_valid"],"Candidate R1 completeness differs from scored outputs")
                need(a["model_coverage"]==dict(expected=sum(c[axis]["n_expected"]for c in candidates),valid=sum(c[axis]["n_valid"]for c in candidates)),"Model coverage differs from scored outputs")
    return {"nonempty_cohort_engine_summaries":len(groups),"raw_scored_to_cohort_summaries_recomputed":True}
def independent_target_aggregation(rows):
    need(len(rows)==112,"Full112 rows required")
    keyed=unique(rows,lambda r:(r["target_id"],r["method_id"],r["seed"],r["cohort"],r["engine"]),"112 evaluation row")
    output=[]
    for engine in ENGINES:
        for cohort in COHORTS:
            pairs=[]
            for tid in sorted(PRIMARY):
                quality={}
                for method in METHODS:
                    v=[keyed[(tid,method,seed,cohort,engine)]["quality_R1"]for seed in(21011,21012)]
                    quality[method]=statistics.mean(v)if all(x is not None for x in v)else None
                rf,bc=(quality[m]for m in METHODS)
                pairs.append(dict(target_id=tid,rf_quality_R1=rf,bindcraft_quality_R1=bc,RF_minus_BindCraft=rf-bc if rf is not None and bc is not None else None))
            complete=all(x["RF_minus_BindCraft"]is not None for x in pairs)
            output.append(dict(engine=engine,cohort=cohort,n_primary_targets=6,n_paired_available=sum(x["RF_minus_BindCraft"]is not None for x in pairs),
                pairs=pairs,paired_macro_mean_RF_minus_BindCraft=statistics.mean(x["RF_minus_BindCraft"]for x in pairs)if complete else None,
                paired_macro_median_RF_minus_BindCraft=statistics.median(x["RF_minus_BindCraft"]for x in pairs)if complete else None,
                inferential_p_value=None,inferential_confidence_interval=None))
    return output
def compare_delivery_statistics(rows,actual):
    need(actual["aggregation_policy"]==POLICY and actual["n_primary_targets"]==6 and actual["n_diagnostic_targets"]==1,"Delivery aggregation identity differs")
    by=unique(actual["rows"],lambda r:(r["target_id"],r["method_id"],r["cohort"],r["engine"]),"delivery target row")
    need(len(by)==56,"Delivery56 target/cohort/engine rows required")
    for r in rows:
        k=(r["target_id"],r["method_id"],r["cohort"],r["engine"]);need(k in by,"Delivery lost fixed target row")
        reps=unique(by[k]["replicates"],lambda v:v["seed"],"delivery replicate")
        need(set(reps)=={21011,21012},"Delivery lost fixed replicate")
        v=reps[r["seed"]]
        for field in("n_selected","n_requested","underfilled","n_R1_complete","quality_R1"):need(v[field]==r[field],"Delivery replicate differs: "+field)
        if r["n_selected"]>0:need(v["reason"]==r["reason"],"Missing nonempty cohort mislabeled empty")
    comparisons=unique(actual["comparisons"],lambda v:(v["engine"],v["cohort"]),"delivery comparison")
    expected=independent_target_aggregation(rows);need(set(comparisons)=={(v["engine"],v["cohort"])for v in expected},"Both engines/cohorts must remain separate")
    for v in expected:
        a=comparisons[(v["engine"],v["cohort"])]
        need(a["n_paired_available"]==v["n_paired_available"],"Paired-target denominator differs")
        apairs=unique(a["pairs"],lambda x:x["target_id"],"delivery primary pair")
        need(set(apairs)=={x["target_id"]for x in v["pairs"]},"Paired target denominator differs")
        for pair in v["pairs"]:
            for k,value in pair.items():
                got=apairs[pair["target_id"]][k]
                need(math.isclose(got,value,rel_tol=1e-12,abs_tol=1e-12)if finite(value)and finite(got)else got==value,"Paired target effects differ: "+k)
        for field in("paired_macro_mean_RF_minus_BindCraft","paired_macro_median_RF_minus_BindCraft","inferential_p_value","inferential_confidence_interval"):
            need(math.isclose(a[field],v[field],rel_tol=1e-12,abs_tol=1e-12)if finite(a[field])and finite(v[field])else a[field]==v[field],"Delivery descriptive aggregate differs: "+field)
    return expected
def receipt(path):
    p=Path(path).resolve();h=hashlib.sha256()
    with p.open("rb")as f:
        for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
    return {"path":str(p),"bytes":p.stat().st_size,"sha256":h.hexdigest()}
def verify(r):
    need(receipt(r["path"])==r,"Receipt mismatch: "+r["path"]);return Path(r["path"])
def read(p):return json.loads(Path(p).read_text())
def jsonl(p):return[json.loads(x)for x in Path(p).read_text().splitlines()if x.strip()]
def cpu_guard():
    jid=os.environ.get("SLURM_JOB_ID");need(jid is not None,"Audit requires Slurm CPU0")
    raw=subprocess.check_output(["scontrol","show","job",jid,"-o"],text=True)
    lines=[x for x in raw.splitlines()if re.search(r"(?:^|\s)JobId="+re.escape(jid)+r"(?:\s|$)",x)]
    need(len(lines)==1 and "JobState=RUNNING"in lines[0],"Unique RUNNING audit allocation required")
    tres=re.search(r"(?:^|\s)(?:AllocTRES|TRES)=(\S+)",lines[0])
    need(tres is not None and not re.search(r"(?:^|,)gres/gpu(?::[^,=]+)?=[1-9]",tres[1]),"Audit must allocate GPU0")
    return {"job_id":jid,"scheduler_record":raw,"allocated_tres":tres[1]}
def main():
    ap=argparse.ArgumentParser()
    for x in("plan","accounting","cohorts","independent_budget","run_receipts","common","membership","inference","scored","target_statistics","output"):ap.add_argument("--"+x.replace("_","-"),required=True)
    a=ap.parse_args();allocation=cpu_guard();plan=read(a.plan);account=read(a.accounting);cohorts=read(a.cohorts);ind=read(a.independent_budget)
    for field,path in(("plan",a.plan),("producer_accounting",a.accounting),("producer_cohort",a.cohorts),("run_receipts_input",a.run_receipts)):need(ind[field]==receipt(path),"Independent auditor input receipt differs: "+field)
    g=generation_matrix(plan,account,cohorts,ind);lengths=[]
    for rr in read(a.run_receipts):
        run=read(verify(rr));lengths.append(dict(run_receipt=rr,**raw_closure(run,jsonl(verify(run["attempt_ledger"])),jsonl(verify(run["sequence_ledger"])),jsonl(verify(run["native_screening_ledger"]))if run.get("native_screening_ledger")else[])))
    common=read(a.common);membership=read(a.membership);inference=read(a.inference);scored=read(a.scored)
    need(common["status"]=="COMMON_REVIEW_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY","Common content acceptance required")
    need(common["result"]==receipt(a.scored)and common["membership"]==receipt(a.membership),"Common content receipt differs")
    need(scored["plan"]==receipt(a.inference)and membership["inference_plan"]==receipt(a.inference)and membership["cohorts"]==receipt(a.cohorts),"Common inference/membership receipt differs")
    need(common["coverage"]==cohorts["coverage"]==membership["coverage"],"Common coverage lost generation denominator")
    slots=strict_primary_slots(inference,scored,membership,cohorts["selected"])
    summary_closure=common_candidate_summaries(scored,membership,common)
    rows=explicit_evaluation_rows(plan["protocol"],cohorts["coverage"],cohorts["selected"],common,{tid:r["allocated_gpu_seconds"]for tid,r in g["accepted"].items()})
    comparisons=compare_delivery_statistics(rows,read(a.target_statistics))
    report={"status":"INDEPENDENT_FORMAL112_FAIRNESS_AND_STATISTICS_AUDIT_PASS","scientific_scope":"COMPUTATIONAL_ONLY",
        "source":receipt(__file__),"allocation":allocation,"plan":receipt(a.plan),"independent_budget":receipt(a.independent_budget),
        "n_frozen_tasks":28,"n_explicit_replicate_cohort_engine_rows":112,"complete_generation_matrix":len(g["accepted"])==28,
        "n_accepted_full_budget_tasks":len(g["accepted"]),"all_allocated_gpu_seconds":g["all_gpu_seconds"],
        "all_raw_sequence_length_closure":lengths,"common_slots":slots,"scored_candidate_summary_closure":summary_closure,"rows":rows,"comparisons":comparisons,
        "primary_engine":"boltz","primary_cohort":"uniform_all_complete","diagnostic_excluded_from_macro":True,
        "evidence_limit":"Computational descriptive result only. No experimental binding/blockade, affinity or significance claim."}
    out=Path(a.output);need(not out.exists(),"Audit output must be new");out.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps(receipt(out)))
if __name__=="__main__":main()
