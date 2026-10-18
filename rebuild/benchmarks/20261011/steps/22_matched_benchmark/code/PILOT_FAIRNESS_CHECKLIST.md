# Matched benchmark acceptance checklist

This checklist evaluates software accounting and computational endpoints. It does not certify experimentally measured affinity or competition blockade.

## Freeze before formal generation

- Immutable input-preparation source, method runtime, method settings/environment scripts, orchestrator, independent verifier, target manifest and all transitive input-file receipts. Source snapshots retain their bytes after engineering repairs.
- Exact sequence and coordinate identity, species/construct, PDB model/biological state, target fragment and reference mapping for every target. Repaired loops remain labeled modeled; input and hotspots are identical in both methods.
- The actual RF output PDB must demonstrate receptor/binder chain identities and a 65-residue complete binder. Common external inference normalizes target A/binder B independently.
- Complete fixed target matrix with role primary/diagnostic, method identities, replicate seeds, one GPU model/count, allocation GPU seconds, common shutdown reserve, scheduler resolution tolerance, all-complete uniform sampling salt/n, native fixed top-k and external score/model/gate definitions.
- Persistent session per task for both methods; environment activation/import/model/JIT initialization begins inside the Slurm StartTime allocation budget. Internal predictions and all rejected attempts remain inside that same budget.
- Engineering pilots are a separate scope. Their complete-chain timing may uniformly revise the formal budget before freeze; candidate scores or native success may not select settings, families or budgets.

## Formal generation / ledger acceptance

- Each launcher pins plan SHA; exact source/config/input identities are checked at process startup. Actual scontrol AllocTRES must allocate the frozen GPU count and the assigned physical hardware must match the frozen model.
- One owned persistent session PID/process group, atomic READY and sequential immutable RPC requests/responses, independent watchdog at scientific cutoff, common final cleanup endpoint.
- Every complete emitted sequence is recorded immediately, including internally rejected sequences and sequences awaiting internal validation. Optional native updates are a separate immutable stream.
- Raw sequence/update files, normalized sequence/update/attempt ledgers, terminal responses, partial-tail hashes, session logs and attempt log byte ranges retain receipts. Missing/truncated control records and invalid complete stream records are engineering failures.
- Hard-boundary attempts and initializations remain explicitly censored. Early engineering failures release the allocation immediately and cannot be passed off as a full-budget comparable arm.
- Technical fixes use a new immutable plan/config/source amendment linked to previous_plan_receipt and the old engineering run. Budgets, targets, seeds, hardware, sampling and native score identity remain fixed; old failures still contribute to gross resource totals.

## Independent comparison acceptance

- Raw sacct allocation rows are joined one-to-one with all run receipts. Job steps/array summaries do not double count. Actual ElapsedRaw × GPU count, scheduler state, hardware and budget deviation are reported.
- Exactly one comparable full-budget allocation per frozen task. No post-result choice among completed reruns; no equal-design-count subsampling chosen after output.
- Unique complete sequence and lineage inventories include every complete original sequence. Uniform SHA selection excludes method, score and internal acceptance. Native top-k is separately fixed and all missing/underfilled cohorts are reported.
- Common external evaluator is method blind and uses the same target/binder identity, MSA/model settings and fixed computational gate. Its GPU cost is separate from generation cost.
- Missing/failed common predictions remain unresolved with coverage and bounds; they are not false experimental biology.
- Every seed's raw denominators/rates and every primary target's paired method difference are reported. Seeds do not increase target n; diagnostic BBF does not enter the primary target mean.
- A separate implementation rechecks source/RPC/ledger/budget/sampling. Structural PASS alone is insufficient: complete_generation_matrix must be true for the entire frozen formal matrix and every selected external outcome must be verified.
- Overall performance statements stay descriptive under the frozen six-primary-target design. Workflow superiority is an empirical comparison to assess, not an acceptance criterion to manufacture.

Software source snapshot: settings/pilot_v1/source/snapshot_manifest.json
Latest production contract: 57 CPU tests PASS, job 13006, orchestrator SHA 858aa2c994dbe168caecd55e589ef901e987406eeefca20051197b150788d7e2.

