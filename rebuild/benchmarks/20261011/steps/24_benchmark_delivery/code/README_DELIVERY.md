# Benchmark delivery support — candidate only

Authority: /lustre/users/u21111210118/projects/test9
Current accepted phase remains PPI-EVIDENCE-REPAIR-20261004. This directory does not
declare the new benchmark complete and must not be registered as current yet.

## Complete source inclusion

Run code/delivery_core.py source-audit on a Slurm CPU allocation. The resulting
manifest gives exact source paths, SHA-256 and repository destinations for all
seven new core modules and top-level step 20–24 Python/shell/Slurm/documentation
helpers. It includes environment installation/repair/readiness helpers, independent
budget auditor, provenance checker, contract tests, query/MSA/native-control
preparation and delivery support. Run outputs, caches, weights and licensed wheels
are excluded. After scientific execution is finished, root reruns this audit,
stages exact bytes (--apply is available), commits the complete source, and records
clean working tree, commit, source inclusion receipt and source tests. The delivery
validator checks every proposed file against the committed Git object.

A source audit before the final runtime/scientific freeze is an inventory, not a
final immutable release. Generated formal protocol/configuration documents and
upstream source/model/license receipts must be archived and linked from the final
source README. Cluster scripts declare the project's authority path/account and
must be adapted for a different Slurm site. The implementation is not represented
as a machine-independent, offline GPU runtime.

## Terminal acceptance gates

1. Screening: all 78 identities and 1,170 existing models are content verified;
   all 78 remain development. R0 identity and official ipSAE directions are pinned.
2. BBF input sensitivity: every predeclared model/arm has a terminal, content
   verified state. Improved scoring is not called successful solely because
   software runs; current step 20 has not solved BBF positive recovery.
3. Seven input constructs: exact sequence/structure/mapping/hotspot identity.
   HRAS 64/65 are modeled, with all observed atoms unchanged. BBF reference binder
   retains the author full query despite missing experimental coordinates.
4. Real GPU engineering pilot: each full native workflow, persistent session,
   actual physical GPU assignment, output chain identity, seed/parameters,
   startup/JIT/native filtering timing and all completed MPNN sequences verified.
5. Formal generation: all 28 frozen same-target, same-budget tasks are terminal.
   All allocated GPU seconds, including failed engineering allocations, are
   reconciled to raw sacct. Deadlines include startup and have explicit boundary
   censoring; no score-driven restart or cohort selection.
6. Common review: original method/cohort remains hidden during scoring, all fixed
   Boltz/AF2/MSA sensitivity slots are retained, native controls are evaluated,
   raw query/chain/unit/config/MSA/features/hashes pass. Null remains null.
7. Independent content: raw ledger and sacct accounting, uniform/native cohort
   selection, raw PDB/JSON/NPZ contacts/R0/geometry and official ipSAE are recomputed.
8. Statistics/report: primary n = 6 targets, BBF diagnostic separate, both
   replicate estimates required. Each nonempty selected cohort requires every
   selected outcome; underfill is reported. Full macro comparison is null unless
   all six paired target estimates are available. No p-values or inferential CIs.
9. Source release: complete code/helpers/tests plus environment/source/model/
   license receipts and installation order. No proprietary wheel, credentials,
   full weight redistribution or experimental claim is embedded in public source.
10. Package/restore/publication: all required evidence is archived with byte/hash
    closure, safely restored on the same Lustre filesystem and independently
    recomputed before single ACTIVE publication. Prior accepted metadata/report
    remain recoverable; failures and provenance repairs remain visible.

A scientific negative or no-interface result can be accepted as faithfully
computed evidence. A missing/failed model is typed unresolved and stays in the
denominator; it does not become a negative binding or blocking experiment.

## Helper APIs

All helper work requires an actual Slurm CPU allocation with zero GPU TRES and
CUDA_VISIBLE_DEVICES empty. User approved temporary organ CPU use for this phase.

- delivery_core.py source-audit --root R --out SOURCE_AUDIT.json [--apply]
- delivery_core.py validate --config DELIVERY_CONFIG.json --out VALIDATION.json
- delivery_core.py package --validation VALIDATION.json --out NEW_ARCHIVE_DIR
  --part-mib 512
- delivery_core.py extract --package PACKAGING_RECEIPT.json --restore-root NEW_DIR
- restore_verify.py --package PACKAGING_RECEIPT.json --restore-root NEW_DIR
  --out NEW_DIR/recomputed
- delivery_core.py publish --validation VALIDATION.json
  --restore-acceptance RESTORE_ACCEPTANCE.json --phase NEW_PHASE.json
  --active R/00_admin/ACTIVE.json

The publish operation is intentionally separate and is not run by these tests.
It requires terminal validation, raw-content independent restore, exact matching
phase/package/report/source receipts and unchanged previous ACTIVE. It archives
old ACTIVE, old phase/reconstruction/report bytes and updates ACTIVE atomically,
rolling back on post-publication integrity failure.

## Delivery config contract

schema: benchmark-delivery.v1; scientific_scope: COMPUTATIONAL_ONLY.
Config requires authority_root, phase_id, previous_active receipt, exactly the
nine named gates in delivery_core.GATES with explicit status/content expectations,
and a files list with receipt + classification. Classes: SOURCE, EVIDENCE, AUDIT,
HUMAN_REPORT, AUTHORITY_SNAPSHOT, ENGINEERING_HISTORY. Failed historical reports
may contain claims of mismatched/obsolete receipts; ENGINEERING_HISTORY preserves
their bytes without treating those failed claims as current validated evidence.

Every receipt embedded in current packaged JSON must be included or declared in
conditional_inference_dependencies with included_in_package:false and the reason.
Original source/model/parameter hashes and license/installation records are kept;
large inference weights and licensed wheels may remain conditional. Archive and
validator/config bytes are automatically added to the package manifest.

recomputation.generation: auditor_source receipt, plan, run_receipts, sacct,
producer_accounting, producer_cohort.
recomputation.common: result, analysis_plan, membership, producer_acceptance,
official_ipsae receipt, msa_roundtrip_source receipt, colabfold_cpu_python.
recomputation.statistics: aggregation_policy
complete_selected_candidate_median_then_both_replicate_mean, rf_method_id,
bindcraft_method_id, producer_summary.

Frozen plans/sources retain their original bytes and authority strings. The
restore resolver translates file I/O to the independent restore tree, rejects
outside/symlink reads, preserves logical path strings for exact RPC checks, and
does not read original scientific evidence. Recomputing AF2 MSA features uses the
private installed CPU Python runtime and the restored helper/input/A3M bytes;
this is an explicit conditional software dependency, not an offline runtime image.

## Evidence limits

Results support a controlled computational comparison on this matrix. They do
not establish experimental binding, functional PPI blockade, affinity/KD,
arbitrary-family generalization or clinical efficacy. Pose recovery, interface
confidence, clash/occlusion and native internal acceptance are distinct endpoints.
Uniform and native-top cohorts remain separate. An unfavorable comparison is
delivered without selecting a different target set or endpoint.

The real-format fixture tests reuse historical predictions only to test parsing,
units, contacts, geometry and independent official-score execution. They are not
new frozen-protocol benchmark predictions.

