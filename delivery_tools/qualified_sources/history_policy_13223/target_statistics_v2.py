#!/usr/bin/env python3
"""All 28 arms and 112 cohort-engine rows, including empty denominators."""
import hashlib,json,math
import numpy as np
POLICY="complete_selected_candidate_median_then_both_replicate_mean"
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
def expected_tasks(p):
    tasks=[]
    for target in p["targets"]:
        for seed in p["replicate_seeds"]:
            pair=dict(protocol_id=p["protocol_id"],target_id=target["target_id"],seed=seed)
            for method in p["methods"]:
                key=dict(pair,method_id=method["method_id"])
                tasks.append(dict(key,task_id=hashlib.sha256(canonical(key).encode()).hexdigest()[:24],
                   pair_id=hashlib.sha256(canonical(pair).encode()).hexdigest()[:24],
                   budget_gpu_seconds=target.get("budget_gpu_seconds",p["budget_gpu_seconds"]),array_index=len(tasks)))
    return tasks
def statistics(common,plan,cohort,rf_method,bc_method):
    p=plan["protocol"];tasks=expected_tasks(p)
    if plan.get("status")!="FROZEN_BEFORE_GENERATION" or plan["tasks"]!=tasks or len(tasks)!=28:raise ValueError("Frozen 28-arm matrix required")
    seeds=p["replicate_seeds"]
    if len(seeds)!=2 or len(set(seeds))!=2 or {m["method_id"] for m in p["methods"]}!={rf_method,bc_method}:raise ValueError("Frozen two-method/two-replicate identity differs")
    primary=[t for t in p["targets"] if t["analysis_role"]=="primary"];diagnostic=[t for t in p["targets"] if t["analysis_role"]=="diagnostic"]
    if len(primary)!=6 or len(diagnostic)!=1:raise ValueError("Primary six plus diagnostic one required")
    roles={t["target_id"]:t["analysis_role"] for t in p["targets"]}
    coverage={r["task"]["task_id"]:r for r in cohort["coverage"]}
    if len(coverage)!=28 or set(coverage)!={t["task_id"] for t in tasks}:raise ValueError("Every arm coverage record required, even empty")
    summaries={}
    for row in common["cohort_summaries"]:
        key=(row["target_id"],row["method_id"],row["seed"],row["cohort"],row["engine"])
        if key in summaries:raise ValueError("Duplicate cohort-engine summary")
        summaries[key]=row
    allowed=set();flat=[];chosen_ids={c["cohort_record_id"] for c in cohort["selected"]}
    if len(chosen_ids)!=len(cohort["selected"]):raise ValueError("Duplicate selected cohort IDs")
    selected_counts={}
    for row in cohort["selected"]:
        key=(row["task_id"],row["cohort"]);selected_counts[key]=selected_counts.get(key,0)+1
    for task in tasks:
        if coverage[task["task_id"]]["task"]!=task:raise ValueError("Coverage task differs from freeze")
        for name,limitfield in (("uniform_all_complete","uniform_n_per_replicate"),("native_fixed_top_k","native_top_k_per_replicate")):
            requested=p["sampling"][limitfield];cov=coverage[task["task_id"]][name]
            selected=selected_counts.get((task["task_id"],name),0)
            if cov["requested"]!=requested or cov["selected"]!=selected or cov["underfilled"]!=(selected<requested) or selected>requested:
                raise ValueError("Selected/empty/underfilled denominator differs")
            for engine,nmodel in (("boltz",3),("af2",5)):
                key=(task["target_id"],task["method_id"],task["seed"],name,engine);allowed.add(key);row=summaries.get(key)
                if selected==0:
                    if row is not None and (row["n_selected"]!=0 or row["n_R1_complete"]!=0 or row["R1_candidates"]["median"] is not None):
                        raise ValueError("Empty cohort invented quality")
                    rep=dict(n_selected=0,n_R1_complete=0,quality_R1=None,reason="EMPTY_COHORT",
                         candidate_R1_summary=None,candidate_R0_summary=None,model_coverage=dict(expected=0,valid=0))
                else:
                    if row is None or row["n_selected"]!=selected:raise ValueError("Nonempty cohort-engine outcome row omitted")
                    mc=row["model_coverage"]
                    if mc["expected"]!=selected*nmodel or not 0<=mc["valid"]<=mc["expected"]:raise ValueError("Fixed model denominator differs")
                    nvalid=row["n_R1_complete"];s=row["R1_candidates"]
                    if s["n_expected"]!=selected or s["n_observed"]!=selected or s["n_valid"]!=nvalid or s["n_missing"]!=selected-nvalid:
                        raise ValueError("Candidate denominator differs")
                    if not 0<=nvalid<=selected or (s["median"] is not None)!=(nvalid==selected):raise ValueError("Missing outcome filled or omitted")
                    quality=s["median"]
                    if quality is not None and (not math.isfinite(quality) or not 0<=quality<=1):raise ValueError("R1 quality units/range")
                    rep=dict(n_selected=selected,n_R1_complete=nvalid,quality_R1=quality,
                         reason=None if quality is not None else "MISSING_PRESELECTED_CANDIDATE_OUTCOME",
                         candidate_R1_summary=s,candidate_R0_summary=row["R0_candidates"],model_coverage=mc)
                flat.append(dict(task_id=task["task_id"],array_index=task["array_index"],target_id=task["target_id"],
                     analysis_role=roles[task["target_id"]],method_id=task["method_id"],seed=task["seed"],cohort=name,engine=engine,
                     n_requested=requested,underfilled=selected<requested,**rep))
    if set(summaries)-allowed:raise ValueError("Unfrozen cohort-engine summary")
    if len(flat)!=112:raise ValueError("Complete 112 cohort-engine denominator required")
    lookup={(r["target_id"],r["method_id"],r["seed"],r["cohort"],r["engine"]):r for r in flat};rows=[]
    for target in p["targets"]:
        for method in (rf_method,bc_method):
            for engine in ("boltz","af2"):
                for name in ("uniform_all_complete","native_fixed_top_k"):
                    reps=[lookup[(target["target_id"],method,seed,name,engine)] for seed in seeds]
                    complete=all(r["quality_R1"] is not None for r in reps)
                    rows.append(dict(target_id=target["target_id"],analysis_role=target["analysis_role"],method_id=method,engine=engine,cohort=name,
                         replicates=reps,quality_R1=float(np.mean([r["quality_R1"] for r in reps])) if complete else None,
                         status="BOTH_REPLICATES_COMPLETE" if complete else "TARGET_QUALITY_NOT_ESTIMABLE"))
    index={(r["target_id"],r["method_id"],r["cohort"],r["engine"]):r for r in rows};comparisons=[]
    for engine in ("boltz","af2"):
        for name in ("uniform_all_complete","native_fixed_top_k"):
            pairs=[]
            for target in primary:
                a=index[(target["target_id"],rf_method,name,engine)]["quality_R1"];b=index[(target["target_id"],bc_method,name,engine)]["quality_R1"]
                pairs.append(dict(target_id=target["target_id"],rf_quality_R1=a,bindcraft_quality_R1=b,RF_minus_BindCraft=a-b if a is not None and b is not None else None))
            complete=all(r["RF_minus_BindCraft"] is not None for r in pairs)
            comparisons.append(dict(engine=engine,cohort=name,n_primary_targets=6,n_paired_available=sum(r["RF_minus_BindCraft"] is not None for r in pairs),
              status="COMPLETE_SIX_TARGET_DESCRIPTIVE_COMPARISON" if complete else "FULL_MATRIX_COMPARISON_UNRESOLVED",pairs=pairs,
              RF_target_median_R1=float(np.median([r["rf_quality_R1"] for r in pairs])) if complete else None,
              BindCraft_target_median_R1=float(np.median([r["bindcraft_quality_R1"] for r in pairs])) if complete else None,
              paired_macro_mean_RF_minus_BindCraft=float(np.mean([r["RF_minus_BindCraft"] for r in pairs])) if complete else None,
              paired_macro_median_RF_minus_BindCraft=float(np.median([r["RF_minus_BindCraft"] for r in pairs])) if complete else None,
              inferential_p_value=None,inferential_confidence_interval=None,experimental_probability=None))
    return dict(schema="paired-target-statistics.v2",status="FROZEN_COMPLETE_DENOMINATOR_DESCRIPTIVE_STATISTICS_RECOMPUTED",
      aggregation_policy=POLICY,n_arms=28,n_cohort_engine_rows=112,n_primary_targets=6,n_diagnostic_targets=1,
      primary_engine="boltz",primary_cohort="uniform_all_complete",flat_cohort_engine_rows=flat,rows=rows,comparisons=comparisons,
      n_empty_cohort_engine_rows=sum(r["n_selected"]==0 for r in flat),n_missing_selected_outcome_rows=sum(r["reason"]=="MISSING_PRESELECTED_CANDIDATE_OUTCOME" for r in flat),
      inference_mode="descriptive_only",scientific_scope="COMPUTATIONAL_ONLY",missing_quality="NULL_NEVER_ZERO",
      complete_matrix_macro_requires_all_six_pairs=True,posthoc_target_dropping=False)

