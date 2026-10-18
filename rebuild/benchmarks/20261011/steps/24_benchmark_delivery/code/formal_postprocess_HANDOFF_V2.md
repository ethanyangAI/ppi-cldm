# Formal post-array CPU orchestration — V2 handoff (2026-10-11)

Scope: remote-only CPU receipt orchestration. No new predictions, no generation/review GPU submissions, no ACTIVE publication, and no scientific settings, filters, thresholds, candidate eligibility or cohort rules change. Root owns formal generation/review launch and publication. V1 remains immutable history.

## Accepted entry and verification

- Readonly source: `/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/formal_postprocess_v2_13258/code/`
- Entry `formal_postprocess_v2.py`: 35372 bytes, SHA b04fc8e8c01b7b5a646a854e031aba519081ba4dc2c13c38d83870146b1727a2.
- `source_snapshot.json`: 5627 bytes, SHA 87969e3ec3177405a79039c37671eba159ac4bd0bc49b8e2e517406628265317.
- CPU13258: COMPLETED, 2 seconds, GPU0; 37 software contracts PASS, no failures/errors.
- Receipt: `/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/formal_postprocess_contracts_13258/acceptance.json`.
- Real engineering phase readback: same run directory `engineering_phase_readback.json`, 144456 bytes, SHA 9e851c7f6bab8a9c4bfd2a4f6456df5a686d42cf3543c61dd86064a1a1e19d3e.
- CPU13251 actual common target/MSA input readback PASS: `/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/formal_postprocess_inputcheck_13251/acceptance.json`, 8315 bytes, SHA 0e380b9c51fb65d496a37ff5a019b815c3795c90d43621b5e5243fdf634a7237.
- Formal collection has not run. No formal array or plan is created by this package.

## Exact CLI

Define SNAPSHOT as the immutable source directory above. Source launcher pins the absolute readonly entry (it does not use Slurm spool dirname). All placeholders below are required inputs from root, not guessed IDs.

```text
sbatch SNAPSHOT/formal_postprocess_cpu_v2.sbatch collect
 --plan REAL_FROZEN_28_PLAN --plan-sha256 EXACT_PLAN_SHA
 --array-job-id REAL_FORMAL_ARRAY_ID --run-root REAL_FORMAL_RUN_ROOT
 --resource-policy ACTUAL_PREGNERATION_RESOURCE_POLICY --policy-sha256 EXACT_POLICY_SHA
 --submit-receipts JSON_LIST_OF_EXACT_SUBMISSION_RECEIPTS --submit-receipts-sha256 EXACT_LIST_SHA
 --out NEW_COLLECTION_DIRECTORY
```

Submission list JSON is `[{path,bytes,sha256}, ...]`; each entry points to the root's immutable submission document required by resource_contract_v3 (plan, launcher, resource_policy, submit_argv, job_id). This version supports the exact original 28 array slots at `RUN_ROOT/ARRAYID_INDEX/run_receipt.json`. It does not silently choose among technical reruns or merge other arrays. Any future rerun must receive a separately reviewed orchestration contract.

After collection acceptance:
```text
sbatch SNAPSHOT/formal_postprocess_cpu_v2.sbatch prepare-common
 --collection COLLECTION_DIRECTORY/acceptance.json
 --collection-sha256 EXACT_ACCEPTANCE_SHA --out NEW_COMMON_DIRECTORY
```

Only the root submits review GPU jobs from the resulting root_dispatch; no inference occurs in either command.

## Frozen sources and gates

Snapshot pins exact bytes/hash of budget_v4 producer, independent budget_v4, formal_contract_v2, native collector13166, common_core_v2_13130, resource_contract_v3, MSA12983 and accepted legacy common registry. Policy scope must equal resource_contract_v3's sequence_universe bound to the exact formal plan/protocol and runtime_v8. Canonical 65aa MPNN proposals remain primary; native rejects and score-NA remain in the original pool. Hard/pseudo trajectory and RF backbone intermediates are inventoried separately and never appended to the cohort universe.

Collect preserves all28 expected slots. Missing receipt is RUN_RECEIPT_UNAVAILABLE, not an observed empty pool. Terminal sacct raw physical IDs count once; Slurm steps/master summaries are excluded; positive unjoined allocation cost rejects. Root submission receipts plus actual start scheduler records verify shared CPU3/GPU1/memory64G/unchanged literal OMP4 hardware policy. All resources are read back from actual allocations; a missing memory TRES is unavailable, never zero.

After terminal state, independent accounting/resource, phase lineage and every-attempt native CPU gates are attempted even if another gate fails. Native collector13166 audits every actual attempt, including scientific reject, boundary and engineering failures. Formal64 stdlib independent raw-array closure verifies all native observations before native cohort ranking. If any preselection gate fails, typed incomplete artifacts are retained and no cohort/common promotion occurs.

Primary MPNN sequence first-observation/cutoff/deduplication and uniformK3/nativeK2 are delegated unchanged to budget_v4. Independent budget_v4 and formal_contract_v2 verify generation/cohort closure. Empty cohorts and typed missing coverage remain in fixed denominators.

## Output schemas

`formal_postprocess_collection.v2` acceptance status:
`FORMAL_ALLOCATION_NATIVE_AND_COHORT_CLOSURE_ACCEPTED`.
Fields: exact plan/source_snapshot/resource_policy/submit_receipts_list/allocation, array_job_id/run_root, sources, frozen_tasks=28, receipt_count, coverage_count=28, full_budget_comparable_tasks, selected_members, actual_array_gpu_seconds, no_new_predictions, no_gpu_submission; files map receipts to fixed_generation_slots, run_receipts, allocation_joins, accounting, independent_resources, preselection_gates, phase_lineage_inventory, all_attempt_observation_inventory, native_audits, native_independent_observation_inventory, native_independent_closure, cohorts, independent_budget, generation_contract, scheduler_cost_inventory.

Native bundle preserves the existing API exactly:
`{schema:"formal_native_output_audit_bundle.v1",plan:receipt,collector_source:receipt,attempts:[{run_receipt,task_id,attempt_index,acceptance:receipt}]}`.

`formal_phase_lineage_inventory.v1` stores plan/policy/source receipts, run coverage, every actual attempt entry, exact normalized proposal/update records, raw native events/stage timing/proposal/update streams (full file receipts + all full rows + tail byte count/hex/hash), all actual trajectory/backbone PDB receipts and first-model ATOM residue identities, each trajectory start/completion/source line/hard sequence/native termination, source-PDB-to-MPNN batch lineage, PDB-vs-hard identity differences, raw FASTA/identity/attempt-result receipts, phase counts and explicit issues. Unjoined or partial physical exports remain typed. Residue/length completeness does not establish structure or biological acceptance.

Actual engineering readback confirms RF1 physical backbone/8 original MPNN proposals/8 native updates; BC1 complete canonical65 trajectory/native Clashing/0 MPNN proposals. BC hard sequence position12=M and physical pseudo export position12=C are distinct identities retained without modification. The unchanged full target is verified. These are engineering-only inputs, not formal candidates.

`formal_common_preparation.v1` status:
`FORMAL_BLIND_COMMON_REVIEW_PREPARED_NOT_INFERRED`.
Outputs include exact registry, inference_plan, analysis_plan, membership and root_dispatch receipts. Prepared chainfix13094 target receipts must equal formal plan; full scientific fields must equal accepted common registry except corrected input-manifest pointer. Seven frozen MSA full queries and content were independently read back. Existing common_core generates settings/inputs unchanged. Membership is exact and includes empty/unresolved coverage, with no origin labels in inference plan.

`formal_common_review_dispatch.v1` status:
`CPU_PREPARED_ROOT_GPU_SUBMISSION_REQUIRED`; lists every index/job_key/engine/variant/expected_models/exact signature and fixed total model slots. No cache replacement is performed; root may use separately accepted matching receipts or run pending slots. Formal blind review remains pending until actual GPU workers and CPU scoring/independent acceptance finish.

## Evidence limits

CPU contracts and source/input/lineage readback are technical readiness. They are not a completed formal benchmark, workflow superiority, binding, blockade, or clinical evidence. No contribution from engineering/supplemental/control jobs is added to the formal generation cost here.

