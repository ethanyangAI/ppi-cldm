# Delivery integration v2 — pending production evidence

This is delivery/support engineering. No formal 28-arm benchmark result, ACTIVE promotion or GitHub publication is
claimed here. Native74 current operative content was accepted byCPU13211 and
hardened independent edge verifier13214; BBF110 is separately root-owned. Source, source staging/commit, ACTIVE and GitHub remain root-owned.

## Declared graph

delivery_graph_v2.py uses explicit graph nodes, not modification times:
- nine core modules, including benchmark_inputs_v2.py and benchmark_common_review_v2.py;
- immutable budget v4 (settings/pilot_budget_v4/source);
- corrected common source bundle common_core_v2_13130;
- declared runtime configuration is selected explicitly; current accepted v8
  must be audited with --runtime-settings pilot_v8;
- old native_common_13051 source remains the source of native evidence;
- selected native19 entry allocation_v2_13106 and selected BBF remaining entry
  allocation_v2_13103; unused alternative/transition roots do not replace them;
- downstream_frozen_13119 helpers/launchers, BBF backend v2, step 20–24 current
  controllers/tests/docs and GitHub exporter/verifier support.

This audit proposes exact repository paths and checks bytes/credentials. It does
not stage source unless root explicitly uses --stage. The final audit must be
rerun after all runtime/protocol/helper changes are finished. Root should publish
README_MATCHED_BENCHMARK_20261011 with the corrected v2 CLI, install order,
scientific limits and frozen protocol/config/source/license/parameter pointers.

## Exact provenance aliases

provenance_aliases_v2.py accepts only exact (original absolute path, SHA-256)
keys and readonly byte-identical archives. Multiple revisions at one original
mutable path require a SHA; no nearest revision, reconstructed source or edited
receipt can substitute. Existing frozen bytes/JSON/source plans are not changed.

Known recoverable old runtime revisions are pinned by pilot_v3 (f3726…) and
pilot_v5 (773dc1…) and copied to this step's readonly alias archive. The
readiness_12980 receipt b47e302… has no retained exact adapter bytes. It is typed
HISTORICAL_UNRESOLVED_PROVENANCE, allowed only as engineering history and never
as current PASS. Fresh v7/current readiness excludes that old dependency.

Native resource_closure.json supplies original→hash-identical copy mappings for
scientific source, inputs, reference geometry, confidence arrays and raw outputs.
Ingest its complete resources, not just score/summary files. Engine/environment/
parameter dependencies remain separately declared. During independent restore,
resolve logical authority paths to restored bytes or exact aliases; reject outside
reads and aliases with incorrect hashes or writable archive mode. Tar extraction
preserves readonly modes. Same-Lustre restore is not an offsite backup or an
offline GPU image.

## Complete statistics contract

target_statistics_v2.py verifies the frozen task matrix (7 targets × 2 methods ×
2 replicates = 28 arms) and all generation coverage records before aggregation.
It returns 112 explicit cohort–engine rows (28 × uniform/native × Boltz/AF2),
including zero-selected cohorts, plus 56 target-method-cohort-engine rows.

Per replicate: complete all-required model median per candidate, then median of
all selected candidate R1 values. Cohort must be nonempty; underfill is retained
and does not invalidate otherwise complete outcomes. Every selected outcome is
required. Empty/missing → quality null, never zero. Per target: mean of both
replicate medians; a missing replicate keeps target quality null. Primary target
denominator stays six; synthetic BBF is diagnostic. Macro method medians and
paired RF-minus-BindCraft means/medians are reported only when all six pairs are
available. No posthoc easy-case dropping, p-values or inferential CIs.

R0 observed uniform recovery/GPU-hour is a separate fixed-cohort endpoint and is
not an estimate of the entire generated candidate pool. A full-budget empty pool
can have observed zero recovery only after accounting/completeness is verified.
Missing structural outcomes remain unresolved and cannot be biological negatives.

## Final packaging inputs (required, not yet all available)

1. Previous ACTIVE, its registered phase/reconstruction/report, old accepted
   package/restore references, and prior source release proof.
2. Step20 complete78/1170 acceptance, manifest, raw references and R0/R1 diagnostics.
3. Full native20job/74model and BBF22job/110model terminal acceptance, all raw
   workers/models, allocations, fixed feature queries, old/new technical roots,
   assembly, original engine score, metadata-repair proof, canonical score,
   independent raw audit, score acceptance and complete resource_closure.
4. Prepared7 chain-fixed inputs, exact declared/observed sequences/mappings,
   target-only HRAS repair proof, author full BBF query and sources.
5. Final GPU engineering pilot acceptances and immutable runtime/native settings,
   source/weight/license/readiness records. No readiness/pilot shortcut.
6. Formal frozen generation plan/protocol, all 28 tasks' raw attempt/sequence/
   native-update streams and ledgers, persistent session/RPC files, failures,
   stdout/stderr, hardware/allocation receipts, raw sacct and independent complete
   budget/cohort audit. All failed allocations stay accounted.
7. Future candidates' corrected common_core_v2_13130 frozen query/analysis/
   membership/runtime/MSA plans, all common Boltz/AF2/sensitivity raw results and
   fixed slots, blind score and independent raw-score/content verification.
8. Full 112-row denominator/statistics output, n=6 paired target comparisons,
   native recoverability diagnostics, uncertainty/missing/underfill reports,
   geometry proxies, final human report and source inclusion/commit/test receipt.
9. Exact resource alias index and archived alias bytes; all current receipt
   closure, explicit historical unresolved dispositions and conditional inference
   dependencies. Failed historical reports use ENGINEERING_HISTORY, preserving
   their bytes without treating their mismatched claims as current evidence.
10. Deterministic package manifest/parts, safe independent extraction, raw ledger/
    sacct/cohort/score/statistics recomputation and hash-verified source release.
    Only then may root separately publish a new phase and ACTIVE.

Current gaps: formal28-arm generation/cohort/common review/statistics are
pending. Current v8 and the full native74 operative collection are accepted;
RF/BindCraft engineering acceptance and BBF110 are separately root-owned.
Final packaging must carry the2 exact HISTORICAL_UNRESOLVED_MSA_DERIVATION
entries as historical edges, preserving current operative strict closure.
Generic delivery_core_v2 now binds the2 exact parent/field exceptions only when
config.historical_provenance_policy is the hash-verified frozen13211 policy
receipt. CPU13223 accepted42 base+9 exact-policy contracts, including a same-Lustre
restore that reads only restored parent/source bytes. All current missing source
edges still fail. Classifying the entire scientific closure/alias index as history
is forbidden. The generic delivery validator therefore cannot accept or
publish this phase yet.

## v2 execution

- delivery_graph_v2.py source-audit --root R --out SOURCE_INCLUSION.json
  --runtime-settings pilot_v7
- delivery_graph_v2.py historical-aliases --root R --out NEW_ALIAS_DIRECTORY
- delivery_core_v2.py validate/package/extract/publish (v1 command arguments);
  config schema benchmark-delivery.v2 and resource_aliases receipt are required.
- restore_verify_v2.py --package ... --restore-root ... --out ...
  It recomputes budget/cohort from restored raw evidence and all 112 statistics
  rows. Re-run independent common scores and actual AF2 MSA feature roundtrips
  using restored scientific inputs and declared private CPU software dependency.

CPU contract tests run from readonly source snapshots on organ without GPU TRES.
Contracts and fixture results are engineering evidence only; formal delivery
acceptance and promotion remain separate and require real completed evidence.


## Approved limited history-policy config

For this native graph, set historical_provenance_policy to the exact receipt of
R/steps/24_benchmark_delivery/frozen/native74_final_v2_13211/code/native_msa_history_policy.json
(SHAec3e16d3764f4620f0adebfb26194cd14bd11bb21dde6abee9e65e4d479b9315,4377B).
Include its actual bytes in the package/source graph. historical_scope_v2.py
requires exactly2 approved entries, original parent SHA/field/hash/size, and
current_execution_allowed=false. Native876d operative code must remain available
through exact aliases; every duplicate/current edge is independently checked.

Current contract receipts: history_contracts_13223/base/acceptance.json(42) and
history_contracts_13223/acceptance.json(9). These are preparation contracts;
formal28-arm production, clean source release, packaging and actual full restore
remain required before final phase acceptance.
