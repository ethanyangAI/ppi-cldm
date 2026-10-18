# Independent static terminal-wrapper review — 2026-10-11

Scope: source/read-only scheduler metadata review only. No source hashes, compilation, tests or scientific analysis ran on the login node. CPU validation remains pending in actual terminal job13264, afterany formal array13260.

Reviewed terminal wrapper V1 and narrow V3 correction under:
/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal13260_terminal_v3/

Finding in V1: checks_and_seal applied readonly=True to all accepted postprocess snapshot source_pins. Actual MSA12983/msa.json and registry7_bridge13010.json have mode0664. Accepted formal_postprocess V2 pins them by exact bytes/SHA and does not require readonly file mode; V1 would have rejected valid accepted inputs before collection.

V3 correction statically accepted: only keys msa and previous_registry use readonly=False, still exact bytes/SHA. All snapshot source files and all other known/unknown source pins require readonly. No scientific file is chmodded or changed. Two additional contracts cover this boundary; suite requires34. A remaining documentation occurrence of32 was reported to author for correction before submission; operative test count is34.

Independent static checks:
- V2 collect CLI arguments exactly match immutable formal_postprocess_v2_13258: plan/hash, array ID, run root, resource policy/hash, submit-receipt-list/hash, output.
- Source schema formal_postprocess_source.v2 and collection accepted status match.
- first_initial uses existing accepted independent v4 audit_gpu_ownership(run, protocol) and allocation_identity(run) correctly, binding initial as its own preserved receipt; actual initial fields agree with exact logical13260_0/raw13261/start-policy ordering.
- Existing root submit receipt fields match launcher/plan/policy/pre-generation/current-seeded gates and raw scheduler ID assertions.
- afterany root submission plus fresh squeue-empty and terminal sacct state gate precedes immutable V2 execution; failures/timeouts remain inspectable.
- No early cohort selection, score computation, model execution, GPU submission, eligibility change or publication is introduced.
- Output uses create-exclusive semantics, preserves typed failures, and does not overwrite prior collections.

Conclusion: V3 STATIC REVIEW PASS with actual CPU source hash/34 software contracts/receipt sealing pending. This is not pre-submission CPU acceptance or formal benchmark completion. Root submitted unique CPU terminal job13264; do not submit V1/V2 or a duplicate terminal job.

