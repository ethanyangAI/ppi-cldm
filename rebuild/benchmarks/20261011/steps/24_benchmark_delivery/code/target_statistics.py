#!/usr/bin/env python3
"""Frozen descriptive target-unit aggregation; no p-values or inferential CIs."""
import json,math
from pathlib import Path
import numpy as np
from restore_resolver import path_factory
POLICY="complete_selected_candidate_median_then_both_replicate_mean"
def target_statistics(common,protocol,rf_method,bindcraft_method):
    seeds=protocol["replicate_seeds"]
    if len(seeds)!=2 or len(set(seeds))!=2:raise ValueError("Exactly two frozen replicates required")
    methods={m["method_id"] for m in protocol["methods"]}
    if methods!={rf_method,bindcraft_method}:raise ValueError("Frozen methods/effect direction disagree")
    primary=[t for t in protocol["targets"] if t["analysis_role"]=="primary"]
    diagnostic=[t for t in protocol["targets"] if t["analysis_role"]=="diagnostic"]
    if len(primary)!=6 or len(diagnostic)!=1:raise ValueError("Primary n=6 plus diagnostic n=1 required")
    summaries={(x["target_id"],x["method_id"],x["seed"],x["cohort"],x["engine"]):x for x in common["cohort_summaries"]}
    rows=[]
    for target in protocol["targets"]:
        tid=target["target_id"]
        for engine in ("boltz","af2"):
            for cohort in ("uniform_all_complete","native_fixed_top_k"):
                for method in (rf_method,bindcraft_method):
                    reps=[]
                    requested=protocol["sampling"]["uniform_n_per_replicate" if cohort=="uniform_all_complete" else "native_top_k_per_replicate"]
                    for seed in seeds:
                        row=summaries.get((tid,method,seed,cohort,engine))
                        if row is None:
                            rep=dict(seed=seed,n_selected=0,n_requested=requested,underfilled=True,n_R1_complete=0,
                                     quality_R1=None,reason="EMPTY_COHORT",model_coverage=dict(expected=0,valid=0))
                        else:
                            n=row["n_selected"];complete=n>0 and row["n_R1_complete"]==n and row["R1_candidates"]["median"] is not None
                            rep=dict(seed=seed,n_selected=n,n_requested=requested,underfilled=n<requested,
                               n_R1_complete=row["n_R1_complete"],quality_R1=row["R1_candidates"]["median"] if complete else None,
                               reason=None if complete else ("EMPTY_COHORT" if n==0 else "MISSING_PRESELECTED_CANDIDATE_OUTCOME"),
                               candidate_R1_summary=row["R1_candidates"],candidate_R0_summary=row["R0_candidates"],
                               model_coverage=row["model_coverage"])
                        reps.append(rep)
                    valid=all(r["quality_R1"] is not None for r in reps)
                    rows.append(dict(target_id=tid,analysis_role=target["analysis_role"],method_id=method,engine=engine,cohort=cohort,
                       replicates=reps,quality_R1=float(np.mean([r["quality_R1"] for r in reps])) if valid else None,
                       status="BOTH_REPLICATES_COMPLETE" if valid else "TARGET_QUALITY_NOT_ESTIMABLE",
                       denominator_policy="Nonempty preselected cohort; all selected outcomes required; underfill retained; no missing-value zero fill."))
    index={(r["target_id"],r["method_id"],r["engine"],r["cohort"]):r for r in rows}
    comparisons=[]
    for engine in ("boltz","af2"):
        for cohort in ("uniform_all_complete","native_fixed_top_k"):
            pairs=[]
            for target in primary:
                rf=index[(target["target_id"],rf_method,engine,cohort)]["quality_R1"]
                bc=index[(target["target_id"],bindcraft_method,engine,cohort)]["quality_R1"]
                pairs.append(dict(target_id=target["target_id"],rf_quality_R1=rf,bindcraft_quality_R1=bc,
                   RF_minus_BindCraft=rf-bc if rf is not None and bc is not None else None))
            complete=all(p["RF_minus_BindCraft"] is not None for p in pairs)
            comparisons.append(dict(engine=engine,cohort=cohort,n_primary_targets=6,n_paired_available=sum(p["RF_minus_BindCraft"] is not None for p in pairs),
              status="COMPLETE_SIX_TARGET_DESCRIPTIVE_COMPARISON" if complete else "FULL_MATRIX_COMPARISON_UNRESOLVED",
              pairs=pairs,RF_target_median_R1=float(np.median([p["rf_quality_R1"] for p in pairs])) if complete else None,
              BindCraft_target_median_R1=float(np.median([p["bindcraft_quality_R1"] for p in pairs])) if complete else None,
              paired_macro_mean_RF_minus_BindCraft=float(np.mean([p["RF_minus_BindCraft"] for p in pairs])) if complete else None,
              paired_macro_median_RF_minus_BindCraft=float(np.median([p["RF_minus_BindCraft"] for p in pairs])) if complete else None,
              experimental_probability=None,inferential_p_value=None,inferential_confidence_interval=None))
    return dict(status="FROZEN_TARGET_UNIT_DESCRIPTIVE_STATISTICS_RECOMPUTED",aggregation_policy=POLICY,
       primary_engine="boltz",primary_cohort="uniform_all_complete",secondary_cohort="native_fixed_top_k",
       n_primary_targets=6,n_diagnostic_targets=1,rows=rows,comparisons=comparisons,
       scientific_scope="COMPUTATIONAL_ONLY",missing_quality="NULL_NEVER_ZERO",
       full_matrix_policy="All six paired target estimates required; no easy-case dropping.",
       inference_mode="descriptive_only",observed_uniform_R0_per_GPU_hour_scope="Observed fixed-cohort recovery only; not an estimate of all generated candidates.")

