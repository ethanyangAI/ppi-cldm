# Formal post-array CPU orchestration v1

Scope: receipt collection, scheduler cost joins, immutable API orchestration,
fixed cohort membership and common-review preparation. No method/inference,
settings, native filtering, candidate selection, thresholds or publication are
implemented or changed here. Root alone submits GPUs and promotes ACTIVE.

Authoritative source snapshot:
steps/24_benchmark_delivery/frozen/formal_postprocess_v1_13250/code/
source_snapshot.json SHA 7453aa9408b68411dec1e9ebbab085f295b95f00f08fdce2e2cc99187981ec5b.
CPU13250 passed 24 software contracts with GPU0. The mutable code directory is
an authoring location only. Use the readonly launcher from the snapshot.

## CLI, called by root after the actual formal array is terminal

Let S be the absolute readonly snapshot code directory and R the authority root.
The launcher selects organ/account u21111210118/qos normal, CPU2/RAM16G/4h,
no GPU GRES, empty CUDA, and chdir R/steps/22_matched_benchmark.

sbatch --dependency=afterany:ACTUAL_ARRAY_ID S/formal_postprocess_cpu_v1.sbatch \
  collect --plan ACTUAL_FROZEN28_PLAN --plan-sha256 EXACT_SHA \
  --array-job-id ACTUAL_ARRAY_ID --run-root ACTUAL_RUN_ROOT --out NEW_COLLECT_OUT

Every run is expected at RUN_ROOT/ARRAY_ID_INDEX/run_receipt.json. Array index
must exactly match the frozen28 order; only one physical allocation per slot is
accepted by this wrapper. A future explicitly amended technical rerun needs a
new reviewed orchestration contract, never retrospective choice among runs.

After acceptance.json is content-accepted and its hash is fixed:

sbatch S/formal_postprocess_cpu_v1.sbatch prepare-common \
  --collection NEW_COLLECT_OUT/acceptance.json \
  --collection-sha256 EXACT_COLLECTION_SHA --out NEW_COMMON_OUT

This creates inference_plan.json, membership.json, analysis_plan.json,
registry.json and root_dispatch.json; it does not submit or run model workers.
Root dispatch contains all fixed job indices, signatures and model counts.
No prior control cache is silently substituted; root may reuse only accepted
workers with exact signatures and preserve all required result slots.

## Fixed APIs and order

- v4 paired_budget_benchmark.py validates the plan and derives actual accounting.
- Every original attempt, including reject/NA/partial/boundary or engineering
  failure, invokes frozen13166 audit_native_confidence_v8.py on CPU.
- formal_contract_v2.native_output_closure independently rereads the full raw
  arrays, PDB/query identities and every native update before native ranking.
- Only then v4 cohorts executes its pre-existing fixed SHA/native policies.
- paired_budget_independent.py and formal_contract_v2.generation_matrix validate
  cost, full28 coverage and fixed selection independently.
- Immutable common_core_v2_13130 targets/prepare APIs derive the blind review.
  prepared7_chainfix13094 is required to equal formal input receipts. All common
  science fields must equal accepted registry7_bridge13010, except corrected
  input-manifest provenance. Existing MSA12983 is reused, with actual A3M/query
  checks performed by the frozen common prepare implementation.

The seven pins include the budget producer, independent auditor, formal64
contract, native9 collector, common core, MSA receipt and original registry.
Imports and artifacts are not rewritten; source snapshot files are readonly.

## Output contract

Accepted collect status:
FORMAL_ALLOCATION_NATIVE_AND_COHORT_CLOSURE_ACCEPTED

acceptance.json provides plan, source_snapshot, allocation, array_job_id,
run_root, sources, frozen_tasks=28, coverage_count=28, receipt_count,
full_budget_comparable_tasks, selected_members, actual_array_gpu_seconds,
no_new_predictions=true, no_gpu_submission=true, and files with exact
{path,bytes,sha256} receipts for:
fixed_generation_slots, run_receipts, allocation_joins, accounting,
native_audits, native_independent_closure, all_attempt_observation_inventory,
cohorts, independent_budget, generation_contract, scheduler_cost_inventory.

native_audits.json exact downstream schema:
{
  "schema": "formal_native_output_audit_bundle.v1",
  "plan": { "path": "...", "bytes": 0, "sha256": "..." },
  "collector_source": { "path": "...13166...", "bytes": 16372, "sha256": "eca561..." },
  "attempts": [
    {
      "run_receipt": { "path": "...", "bytes": 0, "sha256": "..." },
      "task_id": "...",
      "attempt_index": 0,
      "acceptance": { "path": "...acceptance.json", "bytes": 0, "sha256": "..." }
    }
  ]
}
The zeros above illustrate receipt keys only; production values are always
computed from real files. Zero-attempt initialization failures retain their run
and cost without invented attempts. This bundle feeds the already-frozen formal
CLI --native-audits; unchanged final common/scored/target-statistics inputs are
supplied after root's common model execution.

Accepted common preparation status:
FORMAL_BLIND_COMMON_REVIEW_PREPARED_NOT_INFERRED

root_dispatch.json status CPU_PREPARED_ROOT_GPU_SUBMISSION_REQUIRED, with
inference_plan, analysis_plan, membership, jobs[index/job_key/engine/variant/
expected_models/signature], job_count, frozen_model_slots and global cap2.

## Incomplete/empty semantics

Any nonterminal scheduler record, mismatched receipt or unjoined positive GPU
allocation stops downstream preparation, while raw sacct and cost-only evidence
remain on disk. A missing zero-cost/unsubmitted slot remains generation
unresolved in the fixed28 denominator. It is never a complete observed empty
sequence pool. Positive cost is counted by unique physical JobIDRaw; step and
array summaries are excluded by existing parsers. Engineering/control/
supplemental costs remain separate and are not added again to this array.

Native per-attempt audit errors are retained with stdout/stderr; other readable
attempts are still audited, and no cohort selection is accepted until all actual
attempts pass. Complete updates and partial tails are not imputed. Legitimate
scoreNA and scientific rejection remain distinct, including in uniform cohorts.

Failures produce typed_incomplete.json; outputs are never overwritten. Retry CPU
collection in a new directory only after the cause is resolved. Empty cohorts
and underfilled K3/K2 remain exactly as frozen APIs report; no method matching
by post-result equal candidate counts is introduced. Quality aggregation stays
in the existing 112-row final contract and is not reimplemented here.

No formal plan, GPU job or production collection has been created by this
subtask. Actual root-frozen plan/array/run-root remain required.

