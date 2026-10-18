# Generic design input and empty pool qualification V2

Prepared isolated five-file source package only. No hash, compilation, fixture execution, model call, Slurm submission, C3/default/PhysicalV3/formal mutation or lock adoption during preparation. Root submits every job. Common/root are independent static reviewers; this author is not its own independent reviewer.

## Exact bug and narrow correction

The original generic backend coerces binder_length/backbones/sequences_per_backbone with int(). sequences_per_backbone=0 may produce no generated records, while pipeline.design still emits DESIGNS_GENERATED count0 and evaluate skips its loop then emits EVALUATION_COMPLETE total0. This package changes only pipeline.py derived from actual accepted PhysicalV3.

validate_config requires strict positive non-boolean integer design.backbones, design.sequences_per_backbone and design.binder_length. Existing backend range limits backbones1–1000/binder_length30–200 are enforced before any generator/runtime call; defaults4/4/65 and configuration bytes/values are not rewritten. No new maximum sequences_per_backbone or seed/anchor rule is introduced.

One finite positive numeric design.temperature is required. This follows actual unchanged ProteinMPNN run.py line62 (single float parsing per supplied token) and utils.py1165–1166 (division by temperature), plus this generic adapter's count+1 FASTA-record contract which does not support multiple-temperature strings. Default0.1 is unchanged. There is no new upper bound or scientific temperature choice. Nonfinite/zero/negative/bool/multiple-string/float-overflow values fail with typed INVALID_DESIGN_TEMPERATURE.

pipeline.design rejects a non-list or empty backend pool before writing candidates/config/fasta or accepting DESIGNS_GENERATED. pipeline.evaluate rejects imported empty or non-list DESIGNS_GENERATED pools before runtime capture/native parsing/replay/refold and before successful evaluation. Typed errors INVALID_DESIGN_POOL/EMPTY_DESIGN_POOL preserve an actual FAILED run. A nonempty pool whose valid candidates are all rejected remains EVALUATION_COMPLETE accepted_count0/total_count>0; this is a real computational negative and is covered by a positive fixture.

Formal28/112 complete-denominator empty/null/generation failure accounting is independent frozen scientific code and remains unchanged. No design-count, temperature, score, budget or selected candidate changes occur in the formal benchmark.

## Actual root CPU inputs, no future receipt fabrication

Root creates a readonly nonsymlink JSON request under R:
schema: generic-design-input-empty-pool-request.v2
root_owned: true
default_write_allowed: false
scientific_settings_change_allowed: false
parent_physical_preflight: exact path/bytes/SHA of actually accepted PhysicalV3 preflight
parent_source_manifest: exact path/bytes/SHA named by that acceptance
failed_predecessor_incomplete: exact actual readonly runs/generic_design_qualification_13303/typed_incomplete.json receipt. Its actual FAILED1:0/CPU>=1/GPU0/owner/account/organ/jobname is queried fresh and retained; no old acceptance is consumed.

No pending job ID, status-only source, future SHA, old V2 physical gate, rejected predecessor or boolean substitutes for actual content. Parent must bind actual structured57 software receipts, owner/account/organ/COMPLETED0/CPU>=1/GPU0 and exact full frozen source universe/current bytes. Requalification may honestly be POSE_ACCEPTED or POSE_REJECTED; the derived input bug fix does not change or re-run that scientific outcome. The parent's failed13286/13287 and cancelled13267 history is preserved through its exact accepted receipt graph.

Root command after actual parent completion and independent static seal:
sbatch /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/generic_design_qualification_v2/generic_design_cpu.sbatch EXACT_READONLY_REQUEST

CPU1/8G/30min/noGPU, BLAS/OMP/MKL1, job-specific TMPDIR. Current numeric CPU ownership and environment guard precedes hashing. First freeze own five readonly files and compile/bash-n. Then independently verify actual parent qualification; derive two exact clones without writing any live source.

## Separate staged and default candidate trees

derived_source/src preserves the parent's staged common.py exact runtime selector and all other modules; only pipeline.py changes. default_candidate_source/src has the same derived pipeline/helper but substitutes the accepted immutable base original common.py. This corresponds exactly to the later three-path default transaction; the staged common selector is never installed.

Both tree digests use the original generic/PhysicalV3 sorted-relative Python source identity algorithm. Parent source files and default C3/three runtime-lock bytes are independently checked before and after testing. The new helper pose_physical_gate.py is unchanged.

The seven exact pre-existing source/tests filenames and their one actual named import dependency are frozen under actual CPU, before execution, with original and immutable copied byte receipts. Originals are reverified after all checks. They are regression software, not model data or scientific endpoints. No mtime/latest discovery or modified test source is substituted.

Actual tests (eight independently counted suite rows):
- 50 owned pytest cases: strict counts/type/ranges, temperature domain/default preservation, backend empty/non-list dispatch, imported empty/non-list and replay rejection, valid nonempty design, valid nonempty all-rejected evaluation, patch collision/unknown anchor.
- 12 added owned source dependency fixtures in a separately selected pytest suite: valid exact sibling copy/readback, absent helper, symlink helper, wrong source root, actual original/frozen byte drift, original/frozen path forks, unknown role, extra/missing declaration and writable frozen helper. No case calls a model or changes a live runtime lock.
- all seven generic regression files on the default candidate clone with original common selector; actual test counts and zero failures/errors/skips saved from JUnit XML.
- PhysicalV3 physical25/resource9/design8/staged-selector15 on the staged derived tree: total57.
- physical25 repeated on the default candidate tree.
- all owned/derived Python source and exact named frozen regression helper compile, plus owned launcher bash-n.

Generic runtime fixtures deliberately use original common.py because they create synthetic local runtime locks. Running those fixtures against the staged hardcoded accepted override selector would test a different contract. Both clones are explicit; staged selector15 is independently repeated, and the staged source is unchanged.

Synthetic backend/refold call sites are mocked. No actual RFdiffusion, ProteinMPNN, Boltz/AF2 inference, scientific raw scoring or new physical native requalification runs in this package.

## Accepted interface for integration/final source

schema generic-design-input-empty-pool-qualification.v2
status GENERIC_DESIGN_INPUT_AND_NONEMPTY_POOL_WITH_REGRESSION_DEPENDENCY_V2_CPU_ACCEPTED

Fields:
parent_physical_preflight / parent_source_manifest: exact accepted actual parent receipts.
parent_terminal_accounting: actual fresh CPU scheduler raw/row.
original_physical_pipeline: parent tested pipeline receipt.
derived_pipeline: tested default_candidate_source/src/ppiblocker/pipeline.py exact receipt.
derived_source_manifest: full owned, staged/default module, seven test-source identities, one named regression source dependency, preserved failed V1 identity and exact edit scope (schema generic-design-derived-source.v2).
source_files: five owned frozen files, including this HANDOFF.
source_dependencies: one exact named original/frozen register_runtime_locks.py source receipt pair, matching derived_source_manifest and contracts.
failed_predecessor: exact typed13303 V1 failure receipt and fresh numeric terminal allocation. Distinct V2 has a separate job/source/request identity.
contracts: actual policy50/dependency12/generic7/staged57/default25 source-bound logs/JUnit/counts/zero errors, compiled_named_regression_dependencies and pre/post exact source dependency readback. There is no fabricated aggregate test total.
allocation/slurm_job_id: actual current CPU job, terminal verification required by later consumer.
staged_python_source_sha256 and default_python_source_sha256_without_staged_runtime_selector.
physical_helper_unchanged/default_common_original/staged_common_unchanged.
default_source_unchanged/default_runtime_locks_unchanged.
scientific_scope COMPUTATIONAL_ONLY; experimental binding/blockade false; model inference false; source_staged false.

Future integration request's top-level derived_pipeline_qualification exact actual receipt is an extra prerequisite, not a waiver of original physical/runtime/source gates. Its operations3 pipeline.new must equal derived_pipeline; expected new default tree must equal this accepted default tree identity. Helper stays the parent PhysicalV3 exact promotion and third RFDlock adoption stays explicitly accepted. No fourth destination. Final source audit must bind this acceptance/source/contracts and preserve parent source/history.

Only success after all real CPU checks prints accepted descriptor/new pipeline/default identity. A failure prints fresh typed_incomplete with actual stage/allocation; it never becomes source readiness by exit0 or software-only PASS. Actual gates remain pending until root reads terminal sacct plus all receipts.


## V2 narrow operational repair and exact downstream qualification

Actual V1 job13303 failed after the unchanged owned50 policy suite passed, before generic7 collection completed. The old generic test_runtime_registration.py imports Path(__file__).resolve().parents[1]/scripts/register_runtime_locks.py. Relocating only seven tests omitted that source dependency. V1 source and actual failure remain immutable history and are not qualified.

V2 freezes only /lustre/users/u21111210118/projects/test9/source/scripts/register_runtime_locks.py, preserving its original bytes, to the exact actual output-directory sibling scripts/register_runtime_locks.py required by the unchanged generic test. No import rewrite, test skip, live registration invocation or science/settings/default change is introduced. The scripts directory is readonly with an exact one-file universe. The original helper may have ordinary source permissions; its exact original SHA/bytes are measured on actual Slurm CPU, its copied helper is readonly, and both are verified before and after the entire test sequence. All seven original tests are separately verified before and after as before.

The original policy50 test definitions and patch_generic_design.py are byte-preserved from V1. The same owned test source adds12 source-dependency cases, selected as their own suite via -k regression_dependency; policy50 uses -k "not regression_dependency". These are explicit disjoint suites with JUnit actual counts and no skipped tests. generic7 is run in full without filtering or altered source. Eight rows:
owned_design_validation50, owned_source_dependencies12, generic_seven actual positive count,
staged_physical25, staged_resource9, staged_design8, staged_selector15, default_physical25.
Every row has actual argv/returncode/stdout/stderr/counts, and pytest rows have JUnit receipts.

Consumers must require qualification schema .v2 and status GENERIC_DESIGN_INPUT_AND_NONEMPTY_POOL_WITH_REGRESSION_DEPENDENCY_V2_CPU_ACCEPTED, actual terminal jobname test9_generic_design_guard_v2, whole five owned sources, eight suite rows with exact fixed counts, unchanged parent PhysicalV3 receipt/source identities, and source_dependencies equality across acceptance/derived_source_manifest/contracts. They must verify both named dependency receipts at their exact original/frozen paths, the actual freeze/compile/readback flags, and the original13303 typed failure plus terminal allocation. V1 literal/status is not a fallback.

The added helper is software evidence for regression qualification and must enter final source/archive/restore closure through its explicit source_dependencies receipts. It is never a fourth default destination. The later default transaction remains pipeline.py / pose_physical_gate.py / environment/runtime-lock-rfd.json, with default common.py original C3 bytes.
