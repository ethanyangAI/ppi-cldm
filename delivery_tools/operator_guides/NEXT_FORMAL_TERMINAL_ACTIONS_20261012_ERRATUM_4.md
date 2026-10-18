# Operator guide erratum 4 — exact entry points and public qualification order

This mandatory correction supersedes only the two operator-routing errors in ERRATUM_3. Preserve ERRATUM_3 as immutable history, together with the main guide and ERRATUM_1/2. No source modification, test retry, production job or GitHub write resulted from the human routing errors. Actual13328/98 software qualification remains accepted.

Exact frozen directory F:
/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_delivery_composer_v5_exportcontext1_13328/code

Use its composer_cpu.sbatch with FINAL_COMPOSER_ENTRY explicitly set for each mode:
- inventory / compose: F/final_delivery_composer.py.
- package / restore: F/relative_archive_restore.py.
- readback / standalone qualify: F/github_export_context.py.
The main Composer CLI offers inventory and compose only. Do not send package or restore to it. The wrapper package CLI requires actual --validation and --validation-sha256 plus --out; the wrapper restore CLI requires actual --package and --package-sha256, --restore-root and separate new --out under the extracted root.

Between wrapper package and wrapper restore, explicitly run unchanged frozen history_policy_13223/code/delivery_core_v2.py extract --package ACTUAL_PACKAGING_RECEIPT --restore-root NEW_ISOLATED_ROOT inside an actual owned CPU allocation. Verify its actual RESTORE_HASH_ACCEPTANCE before wrapper restore. Do not omit extraction or substitute a live-file fallback. All shell example labels are unexecuted placeholders; future arguments must use actual emitted descriptors.

Correct chronological order:
1. Actual scientific common112/statistics/cost and report QA, default integration, final-source audit and stage, clean private commit and qualified private bundle.
2. Run the pinned frozen exporter to PREPARE exact export manifest/inventory/payloads/handoff. This exporter preparation precedes public writes and is not public readback or export-context qualification.
3. Root creates actual public blobs/trees, the same-final-tree commit with the pinned baseline sole parent, new reversible branch and draft PR; retain actual raw connector responses and request captures, attach PR.
4. Actual V5 CPU readback obtains public REST GET/fetch/raw commit/full nontruncated tree/parity; its job must be terminal and freshly CPU1/GPU0-qualified.
5. Actual export-context qualification runs AFTER the public verifier PASS and real readback terminal, either via standalone helper qualify or lazily in compose.
6. Actual Composer inventory/compose; wrapper package; explicit unchanged-core extract; wrapper restored-index-only independent verification/recomputation; ACTIVE only after every actual required gate passes.

The accepted frozen HANDOFF.md and CLI source confirm this sequence. Previously named prepublication "export qualification" in ERRATUM_3 means exporter preparation only and must not be executed as helper qualify before publication. Raw export JSON remains unchanged. No software retest is warranted for this documentation correction.
