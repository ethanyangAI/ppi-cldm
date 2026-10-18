# Operator guide erratum 1 — 2026-10-12

Applies to /lustre/users/u21111210118/projects/test9/00_admin/NEXT_FORMAL_TERMINAL_ACTIONS_20261012.md §10. The original readonly guide is preserved. No code, manifest, source settings, Slurm submission, hash or test execution changed.

The stage --audit argument is the exact accepted source_inclusion_final.json descriptor pointed to by actual final source acceptance['source_inclusion']. It is not the final source acceptance.json. Actual stage requires status SOURCE_INCLUSION_AUDIT_PASS and applied false before checking/installing the audited exact source entries.

Correct root-owned pureCPU command template:
ACTUAL_ACCEPTED_LIBRARY_ENTRY stage --audit ACTUAL_ACCEPTED_SOURCE_INCLUSION_FINAL_JSON_PATH --audit-sha256 ACTUAL_SOURCE_INCLUSION_SHA --out NEW_STAGE_DIR

Resolve that path/SHA from the actual accepted finalsource output receipt; do not guess future bytes, reuse oldbase inclusion, or compute it on login. Root's three-path integration is a separate accepted operation; absent-only stage/differing-source guard is unchanged and cannot replace that transaction.

Current software metadata update: corrected Composer fixturefix2 actual job13326 has independent READBACK_PASS,66 actual tests PASS, CPU1/GPU0, no science/archive/ACTIVE acceptance. Original13321 and13323 failures remain immutable. Use actual13326 qualified source8/software receipt and accepted launcher thereafter. This software status does not remove all28terminal/source/common112/report/cost/archive/restore gates.

The prior bounded guide review confirmed CommonV5 preflight/finish, report build/QA, actual GitHub source readback before compose, then package→exact extraction/hash closure→isolated restore→finalACTIVE order. Exact stage correction above takes precedence over its earlier §10 template.
