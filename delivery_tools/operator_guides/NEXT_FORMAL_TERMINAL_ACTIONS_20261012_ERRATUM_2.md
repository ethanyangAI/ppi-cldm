# Operator guide erratum 2 — 2026-10-12

Applies to /lustre/users/u21111210118/projects/test9/00_admin/NEXT_FORMAL_TERMINAL_ACTIONS_20261012.md §10, in addition to mandatory ERRATUM_1. This is a bounded source/metadata review and human operator correction, not software, publication, archive, or restore acceptance. The original readonly guides and accepted Composer13326 remain unchanged.

## Separate private history from the exact public commit graph

Pinned github_export_verify.py requires the fetched published commit to have exactly one parent, baseline e2984a94674ffcb75b280680038df5e9f39d684d. The preserved local history has HEAD29dac0fb3e7312b3aaf65ab3d2579d399a3220fa and parent9b6bc2df87e05a3549b018f37cba678a33b7789c. Consequently normal push of the future private-history final HEAD cannot satisfy this existing public verifier.

Keep the private branch, final clean commit, and qualified private source.bundle with their full history. Produce a distinct public commit using the independently qualified export's exact final tree and the pinned baseline as its sole parent. Its commit SHA may differ from the private final commit; complete tree/blob equality is mandatory. After actual science/report QA/default installation/finalsource audit/staging/clean commit/private bundle acceptance, root may use exact GitHub blob/tree/commit tools, create a new reversible branch from the actual public commit, create a draft PR and attach it. No private history rewrite, reset, force push, or master update.

Save actual API responses, root request/argv and expected-to-returned object mappings. Fetch the actual remote ref/commit/tree and complete nontruncated recursive tree in a real CPU allocation, preserve response provenance, and fetch the remote public ref into the local repository without moving its private final HEAD. A local ref alias does not prove remote origin. Reverify the live base at execution. Draft publication still precedes Composer because Composer requires actual published_ref and api_responses; ACTIVE remains last.

## Newly identified exact export-context production blocker

Static review found a real input-format mismatch beyond the existing66 software fixtures. The export manifest contains relative path/bytes/SHA256 children for source_inventory, handoff_plan, delta_tree_payload and object_payloads. The source_inventory entries themselves contain repository-relative blob path/bytes/SHA256 fields. Composer's recursive closure and unchanged core validation currently recognize only the accepted historical exact-parent namespaces and reject these new export parents. The pinned GitHub verifier requires the raw export manifest paths to remain relative.

Do not edit raw export JSON, make it absolute, add a generic relative waiver, or modify frozen Composer13326. A distinct production successor must narrowly qualify the actual independently verified export manifest and inventory with exact parent descriptors and schema-defined fields; verify the complete actual source tree and blob bytes; preserve Git symlink mode120000 as blob text without reading a symlink target; archive all actual payloads, raw parents, private source bundle, source-object byte evidence and qualification proofs. Compose traversal, module-local unchanged-core validation, package fresh checks and isolated restored-index-only verification must consume the same strict view. No live checkout/export fallback during restore. Old duplicate, missing-file, source identity, exact-parent and restored-index gates remain strict.

Two agents are implementing/reviewing this successor; the other agent independently checks nested scope and negative cases. No new successor source or tests are accepted yet. Existing SourceV10/Mapper201/LIB53/Integration84 qualifications remain valid for their own unchanged scope; the new Composer software count and source identity must be actual, never represented as the old66 acceptance.

Independent interface audit:
/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/GITHUB_EXPORT_CONTEXT_INTERFACE_AUDIT_20261012.md

Read-only GitHub readiness responses saved at:
/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/github_prepublication_readiness_20261012/metadata_api_responses.json
At2026-10-11T19:59:21Z repo metadata reported public, not archived, default master, connector permissions admin/push/pull true. Actual fetch_commit(master) still returned e2984a94674ffcb75b280680038df5e9f39d684d. An extra collaborator-permission endpoint returned403 Resource not accessible by integration; this does not establish a failed Git write. These are readiness metadata, not future publication/parity evidence.

Include this erratum, the readiness response, interface audit, all successor sources/software/actual failures/submission/seals and qualification proofs in final late provenance. Hashing and testing only occur in actual owned CPU allocations. Formal13260 remains frozen and unread before ALL28terminal; default apply remains held until then. Cost seal-ledger and numeric audit remain BEFORE CommonV5 finish. No new GPU submission, default write, Git write, candidate read, or ACTIVE change was made for this review.
