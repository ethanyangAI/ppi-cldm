"""Benchmark selection over a shared immutable candidate pool (no experimental claims)."""
from __future__ import annotations
import argparse,hashlib,json,math,statistics
from pathlib import Path
from .common import Run,load_run,read_json,record_file,atomic_json,require,EvidenceError
from .backends import confidence_reasons

COMPETITION_REASONS={"INSUFFICIENT_NATIVE_INTERFACE_OVERLAP","NO_STERIC_COMPETITION_SUPPORT"}
def valid_number(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)

def rank_pool(rows,k=8,gates=None):
    require(type(k) is int and k>0,"INVALID_K","K must be positive")
    gates=gates or {}
    require(len({r["id"] for r in rows})==len(rows),"DUPLICATE_CANDIDATE_ID","Candidate IDs must be unique")
    diagnostics=[]
    for row in rows:
        item=dict(id=row["id"],sequence=row["sequence"],s0_pass=False,s1_pass=False,
                  binding_score=None,competition_score=None,reason=None)
        models=row.get("models",[])
        requested=row.get("requested_samples")
        if row.get("status")=="EVALUATION_FAILED" or not models or type(requested) is not int or len(models)!=requested or requested<3:
            item["reason"]="INCOMPLETE_OR_FAILED_EVALUATION";diagnostics.append(item);continue
        if any(m.get("status")=="MODEL_EVALUATION_FAILED" or "metrics" not in m or "geometry" not in m for m in models):
            item["reason"]="INVALID_MODEL";diagnostics.append(item);continue
        s0=[];s1=[];scores=[];coverages=[]
        for model in models:
            metrics=model["metrics"];geom=model["geometry"]
            numbers=[metrics.get("pair_iptm"),geom.get("binder_ca_rmsd_after_target_alignment"),
                     geom.get("target_ca_rmsd"),geom.get("native_interface_coverage"),
                     geom.get("partner_overlap_atom_count_2A"),geom.get("predicted_complex_interface",{}).get("minimum_distance")]
            finite_metrics=[v for v in metrics.values() if v is not None and not isinstance(v,bool)]
            if not all(valid_number(x) for x in numbers+finite_metrics):
                item["reason"]="INVALID_METRIC";break
            # Recompute base gates from the frozen metrics, not from S1's pass/fail label.
            try: reasons=confidence_reasons(metrics,gates)
            except (KeyError,TypeError,ValueError):item["reason"]="INVALID_METRIC";break
            if numbers[1]>gates.get("max_binder_rmsd",2):reasons.append("DESIGNED_POSE_NOT_RECOVERED")
            if numbers[2]>gates.get("max_target_rmsd",2):reasons.append("TARGET_DISTORTED")
            if numbers[5]<1.5:reasons.append("SEVERE_TARGET_BINDER_CLASH")
            base=not reasons
            competition=base and numbers[3]>=gates.get("min_interface_overlap",.5) and numbers[4]>=gates.get("min_partner_overlap_atoms",5)
            s0.append(base);s1.append(competition);scores.append(numbers[0]);coverages.append(numbers[3])
        if item["reason"]:
            diagnostics.append(item);continue
        needed=max(2,math.ceil(.6*requested))
        item.update(s0_pass=sum(s0)>=needed,s1_pass=sum(s1)>=needed,
                    s0_samples=sum(s0),s1_samples=sum(s1),
                    binding_score=statistics.median(scores),competition_score=statistics.median(coverages))
        diagnostics.append(item)
    arms={}
    for arm in ("s0","s1"):
        eligible=[r for r in diagnostics if r[arm+"_pass"]]
        # S1 tests added competition gates; rank both by identical binding confidence.
        eligible.sort(key=lambda r:(-r["binding_score"],r["id"]))
        seen=set();selected=[];duplicates=[]
        for row in eligible:
            if row["sequence"] in seen:duplicates.append(row["id"]);continue
            seen.add(row["sequence"]);selected.append(row["id"])
            if len(selected)==k:break
        arms[arm]=dict(selected=selected,allocated_slots=k,unfilled_slots=k-len(selected),
                       eligible_count=len(eligible),duplicate_ids=duplicates,
                       experimental_blockade=None)
    return dict(arms=arms,candidates=diagnostics,pool_count=len(rows),
                pool_sequence_sha256=hashlib.sha256(json.dumps([(r["id"],r["sequence"]) for r in rows],separators=(",",":")).encode()).hexdigest(),
                rule_version="shared_pool_v1",ranking="median pair ipTM descending; ID tie-break; identical across arms",
                deduplication="exact sequence only; structural clustering not yet implemented",
                experimental_results_available=False)

def select(root,manifest,k):
    upstream=load_run(manifest,{"EVALUATION_COMPLETE","EVALUATION_INCOMPLETE"})
    require(upstream["step"]=="04_evaluate","WRONG_STAGE","Expected evaluation manifest")
    run=Run(root,"07_benchmark_selection",[record_file(manifest)])
    try:
        data=read_json(upstream["outputs"]["evaluation"]["path"])
        result=rank_pool(data["candidates"],k,data.get("gates",{}))
        result["upstream_evaluation"]=record_file(manifest)
        atomic_json(run.path/"outputs/selection.json",result);run.output("selection",run.path/"outputs/selection.json")
        lines=["# Shared-pool selector comparison","",
               "Computational gate comparison only. No experimental outcome has been measured.","",
               "|Selector|Pool|Allocated slots|Selected|Unfilled|","|---|---:|---:|---:|---:|"]
        for arm,row in result["arms"].items():
            lines.append(f"|{arm}|{result['pool_count']}|{k}|{len(row['selected'])}|{row['unfilled_slots']}|")
        report=run.path/"outputs/report.md";report.write_text("\n".join(lines)+"\n");run.output("report",report)
        return run.finish("SELECTION_COMPLETE","computational_selection_only")
    except Exception as error:run.fail(error);raise

def validate_registry(cases):
    require(bool(cases),"EMPTY_REGISTRY","No cases")
    require(len({c["case_id"] for c in cases})==len(cases),"DUPLICATE_CASE_ID","Case IDs must be unique")
    families={}
    for case in cases:
        require(case.get("split") in {"DEVELOPMENT","TEST","CHALLENGE"},"SPLIT_UNRESOLVED",case["case_id"])
        family=case.get("family_group")
        require(bool(family),"FAMILY_UNRESOLVED",case["case_id"])
        if case["split"]!="CHALLENGE":
            require(family not in families or families[family]==case["split"],"FAMILY_LEAKAGE",family)
            families[family]=case["split"]
        if case["split"]=="TEST":
            require(case.get("homology_review_complete") is True,"HOMOLOGY_REVIEW_REQUIRED",case["case_id"])
            require(case.get("used_for_development") is False,"DEVELOPMENT_LEAKAGE",case["case_id"])
        require(case.get("qualification_status") in {"ACCEPTED_CONSTRUCT","REJECT_EXPECTED","PENDING_REVIEW"},"INVALID_QUALIFICATION",case["case_id"])
        if case["qualification_status"]=="ACCEPTED_CONSTRUCT":
            require(case.get("context_review_complete") is True and case.get("structure_record"),"CONTEXT_REVIEW_REQUIRED",case["case_id"])
            from .common import verify_file
            verify_file(case["structure_record"])
    return True

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True)
    sub=p.add_subparsers(dest="command",required=True)
    s=sub.add_parser("select");s.add_argument("manifest");s.add_argument("--k",type=int,default=8)
    s=sub.add_parser("validate-registry");s.add_argument("registry")
    args=p.parse_args()
    if args.command=="select":print(select(args.root,args.manifest,args.k))
    else:
        validate_registry(read_json(args.registry)["cases"]);print("REGISTRY_VALID")
if __name__=="__main__":main()

