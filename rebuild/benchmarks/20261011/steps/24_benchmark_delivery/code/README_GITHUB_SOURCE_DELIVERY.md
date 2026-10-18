# GitHub source delivery fallback

These helpers prepare an auditable connector handoff without reading credentials or changing the source checkout, commits, branches, GitHub, or project authority. Run source inspection and tests only inside a Slurm CPU allocation. The temporary organ CPU exception applies; request no GPU and clear CUDA_VISIBLE_DEVICES.

## Publication strategy

The GitHub connector can create blobs, trees and commits but its exposed create_commit arguments do not include local author/committer metadata. A commit created by this connector will have a new identity. Do not claim it reproduces the unpublished local commit history.

The supported fallback preserves exact source bytes and modes by publishing a new commit whose sole parent is the verified public baseline e2984a94674ffcb75b280680038df5e9f39d684d and whose root tree is identical to the final approved local commit. Keep the local branch, its final commit ID and a verified private source.bundle containing that commit and history. Do not rewrite or discard that history.

The exporter checks a clean checkout, an explicitly provided final commit, baseline ancestry, every final tracked blob, file modes, symlink safety, and high-confidence publication exclusions. It reconstructs the Git root tree independently and requires equality with Git. Payloads use base64 for exact byte preservation, including binary files and line endings. Model checkpoints, runtime wheels/shared libraries, credentials and opaque data archives are refused; they belong in the private evidence package, not the public source tree. Gitlinks added or changed since the baseline require separate public-object review.

Every new blob receives one immutable payload. Complete tree payloads are ordered from children to parents. Existing baseline objects are reused. This avoids ambiguous nested changes when a file becomes a directory or a directory becomes a file. The separate delta payload records additions, removals and mode changes for review; it is not the default publication path.

GitHub documents base64 blob creation, valid file modes and null-SHA deletion entries in its [blob API](https://docs.github.com/en/rest/git/blobs#create-a-blob) and [tree API](https://docs.github.com/en/rest/git/trees#create-a-tree). A published tree must be committed and a branch updated separately. The connector supplies narrower [commit API](https://docs.github.com/en/rest/git/commits#create-a-commit) fields than the complete REST interface.

## Run after the final source integration and commit

Set R to the authoritative test9 root. Replace FINAL_COMMIT_SHA with the actual approved clean source commit. Invoke the immutable helper snapshot in the final Slurm CPU job:

    python github_source_export.py \
      --repo "$R/source" \
      --baseline e2984a94674ffcb75b280680038df5e9f39d684d \
      --expected-head FINAL_COMMIT_SHA \
      --repository ethanyangAI/ppi-cldm \
      --output-dir "$R/steps/24_benchmark_delivery/runs/github_export_${SLURM_JOB_ID}"

    python github_export_verify.py \
      --repo "$R/source" \
      --export-dir "$R/steps/24_benchmark_delivery/runs/github_export_${SLURM_JOB_ID}" \
      --output "$R/steps/24_benchmark_delivery/runs/github_verify_${SLURM_JOB_ID}.json"

The independent verifier imports no exporter code and uses official git hash-object to verify Git object IDs. It verifies the complete committed file denominator, baseline reuse, all payload bytes, child-first tree dependencies, and the exact changes including deletions. It also supports API-returned SHA receipts and a subsequently fetched public ref.

## Root-agent connector handoff

1. Verify the public baseline still exists and resolves to the export's baseline tree. A changed public master requires a documented resolution, not silently substituting its SHA.
2. Read the immutable manifest and its receipt-matched plan from the remote allocation artifacts into connector memory only. Do not create a local source/data mirror.
3. Call each named create_blob tool with its corresponding payload. Check the returned SHA equals expected_sha before proceeding.
4. Call create_tree in the exact ordered plan. Every returned SHA must equal expected_sha. Stop before a commit if any mismatch occurs.
5. Create a new public commit with the specified baseline parent, exact final tree and a root-approved descriptive message. Record its new SHA, parent and tree. Create/update only the intended new branch; root owns GitHub writes.
6. Preserve the old local branch and verify source.bundle contains the local final commit before changing the checkout. Fetch the new public branch through unauthenticated public HTTPS with credential helpers disabled. Fetch does not need public-repository credentials.
7. Inside Slurm CPU, run the independent verifier with --api-responses and --published-ref. Confirm clean source status and exact old/new tree equality. Root may then switch to the public branch using a normal non-destructive checkout. Preserve the old branch and bundle. Do not use reset --hard, force push, or delete local history.
8. Only after delivery-wide content and restore acceptance may root register the new authoritative source HEAD. Changing branch alone is not project acceptance.

If authenticated Git push later becomes available through the user's existing supported connection without credential extraction, preserving exact original history would be preferable. This helper does not search for tokens, print credential helpers, transport secrets through SSH, or add credentials to an unauthenticated CLI.

The publication scanner is a high-confidence exclusion gate plus explicit path policy, not proof that every possible secret is detectable. Root must review the source inclusion audit, including newly frozen guard and controller helpers, before export. Final source and package inclusion audits must be rerun after all agent files have stabilized.

## Meaningful contracts

test_github_source_export.py covers exact tree reconstruction, non-UTF-8 refusal, executable/symlink modes, binary bytes, duplicate-content blobs, baseline object reuse, unchanged source completeness, file/directory replacement, deletions, dirty source and wrong-head refusal, ancestry, forbidden credentials/runtime binaries, unsafe links, size policy, atomic refusal, tampering despite forged SHA-256 receipts, child-first dependencies, returned-object ID mismatch, and CPU-only allocation enforcement. These tests use isolated temporary Git repositories under the allocation's TMPDIR. They do not publish test fixtures.

