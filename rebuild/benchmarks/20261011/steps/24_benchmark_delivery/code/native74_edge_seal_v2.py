#!/usr/bin/env python3
"""Read-only supplement: independently verify all current edges and record final receipts."""
import collections,json,os
from pathlib import Path
import native_resource_closure_v2 as n
from provenance_aliases_v2 import ReceiptResolver
R=n.R;run=R/"steps/24_benchmark_delivery/runs/native74_final_v2_13211/native74"
out=Path(os.environ["NATIVE_CLOSURE_TEST_OUTPUT"]);out.mkdir(parents=True,exist_ok=True)
accepted=n.read(run/"acceptance.json")
if accepted["status"]!="NATIVE74_FULL_RAW_AND_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY":raise ValueError("Full74 content acceptance absent")
science=run/"scored";closed=run/"closure";supp=n.read(closed/"acceptance.json")
closure=n.read(closed/"resource_closure.json");index=n.read(closed/"resource_aliases.json")
resolver=ReceiptResolver(R,index=index)
policy_path=R/"steps/24_benchmark_delivery/frozen/native74_final_v2_13211/code/native_msa_history_policy.json"
def archived_receipt(path):
    matches=[entry["original"] for entry in index["aliases"] if entry["original"]["path"]==str(path)]
    if len(matches)!=1:raise ValueError("Exact SHA required for ambiguous archive path "+str(path))
    return matches[0]
policy=n.read(resolver.verify(archived_receipt(policy_path)))
names=("manifest.json","assembly.json","score.json","raw_audit.json","score_acceptance.json","score_engine_original.json","score_metadata_repair.json","REPORT.md")
manifest=n.read(resolver.verify(supp["immutable_prior_evidence"]["manifest.json"]))
seeds=list(supp["immutable_prior_evidence"].values())+[manifest[k] for k in ("source","inference_plan","analysis_plan","membership")]
seeds+=[archived_receipt(R/"steps/23_common_review/frozen/native_common_13051/source_bundle.json"),
        archived_receipt(R/"steps/23_common_review/runs/downstream_frozen_13119/code/native_review_pipeline_v2.py"),
        archived_receipt(R/"steps/24_benchmark_delivery/frozen/native74_final_v2_13211/code/native_resource_closure_v2.py"),
        archived_receipt(R/"steps/24_benchmark_delivery/frozen/native74_final_v2_13211/code/provenance_aliases_v2.py"),
        archived_receipt(R/"steps/24_benchmark_delivery/frozen/native74_final_v2_13211/code/test_native_resource_closure_v2.py"),
        archived_receipt(policy_path),archived_receipt(R/"steps/24_benchmark_delivery/frozen/native74_final_v2_13211/code/native_full74_collection_v2.py"),
        archived_receipt(science/"independent_current_msa_audit.json")]
result=n.verify_closure(R,closed,closure,index,seeds,policy)
assembly=n.read(resolver.verify(supp["immutable_prior_evidence"]["assembly.json"]))
score=n.read(resolver.verify(supp["immutable_prior_evidence"]["score.json"]))
a=n.read(resolver.verify(supp["immutable_prior_evidence"]["score_acceptance.json"]))
raw=n.read(resolver.verify(supp["immutable_prior_evidence"]["raw_audit.json"]))
counts=n.validate_native_matrix(assembly,score,a,raw)
if assembly["n_jobs_copied"]!=20 or raw["n_raw_confidence_accepted"]!=74:raise ValueError("Final all74 worker/confidence gate missing")
msa=n.read(resolver.verify(archived_receipt(science/"independent_current_msa_audit.json")))
if msa["n_jobs_expected"]!=msa["n_jobs_accepted"] or msa["old_MSA_derivation_sources_executed"]:raise ValueError("Current independent MSA query verification missing")
native_rows=[]
for row in a["native_recovery_controls"]:
    native_rows.append({k:row.get(k) for k in ("target_id","blind_id","control_type","engines")})
result=dict(result,status="NATIVE74_CURRENT_OPERATIVE_CLOSURE_ALL_EDGE_ROLES_AND_DENOMINATORS_ACCEPTED_WITH_TWO_TYPED_MSA_HISTORY_GAPS",
            CPU_allocation=n.cpu_allocation(),source=n.checksum(__file__),hardened_closure_source=n.checksum(n.__file__),
            prior_final_native_acceptance=n.checksum(run/"acceptance.json"),prior_final_closure_acceptance=n.checksum(closed/"acceptance.json"),
            raw_model_outcomes=counts,native_recovery_controls=native_rows,current_MSA_features_accepted=msa["n_jobs_accepted"],
            historical_MSA_gaps=[dict(original=h["original"],subtype=h["subtype"],role=h["role"],parent=h["parent"],trail=h["trail"],shortest_receipt_chain=h["shortest_receipt_chain"]) for h in index["historical_unresolved"]],
            full_historical_source_closure=False,offline_GPU_recompute_guaranteed=False,scientific_scores_changed=False,original_sources_modified=False,
            new_GPU_inference=False,formal28arm_benchmark_complete=False,ACTIVE_changed=False,contract_tests=n.checksum(out/"tests.json"))
n.dump(out/"acceptance.json",result)
for path in (R/"steps/24_benchmark_delivery/runs/contracts_v2_13156/acceptance.json",
             R/"steps/24_benchmark_delivery/runs/source_audit_v8_13212/source_inclusion_v2.json",run/"acceptance.json",
             closed/"acceptance.json",closed/"resource_closure.json",closed/"resource_aliases.json",science/"score.json",science/"raw_audit.json",science/"independent_current_msa_audit.json",out/"acceptance.json"):
    print(json.dumps(n.checksum(path)),flush=True)

