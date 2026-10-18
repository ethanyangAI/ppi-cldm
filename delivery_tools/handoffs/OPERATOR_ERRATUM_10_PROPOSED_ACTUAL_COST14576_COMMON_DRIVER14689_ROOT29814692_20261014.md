# PROPOSED operator erratum 10 — actual Cost14576, Common driver14689, restored ROOT298 checker14692

This is a separate HUMAN proposal prepared on 2026-10-14. It is not installed authority, a source plan, an audit, a submission, a scientific acceptance or a real restoration proof. Main guide and installed ERRATUM1–9 remain unchanged. Root alone may install an independently reviewed copy. This proposal records the accepted new software and Cost interfaces and the remaining procedure; it introduces no algorithm, model parameter, GPU rerun, queue action, source edit, guard waiver or automatic retry.

R = /lustre/users/u21111210118/projects/test9
S = R/steps/24_benchmark_delivery
All paths below beginning S/ or R/ are exact expansions of those roots. Full receipt identities must come from actual allocated-CPU outputs and readonly evidence. Seal ownSHA values not yet captured by an owned CPU are deliberately not supplied here.

## 1. Actual accepted evidence and limits

| Evidence | Actual result | Exact acceptance and CPU-emitted identity |
|---|---|---|
| V3 Cost software14565 | COMPLETED0:0,20s,CPU1/GPU0;88 PASS,0 failures/errors/skips; source4 | S/runs/root_gpu_cost_contracts_14565/acceptance.json;7539 bytes; b46e1f1f7e8dd9ea30a2c8109843a62ee2ff83c0ecd9da779b5bd9d6718a24c6 |
| Full V3 Cost14576 | COMPLETED0:0,13s,CPU1/GPU0; complete current ROOT298 accounting | S/runs/root_gpu_cost_audit_14576/acceptance.json;15252 bytes; ca6bac7a46bad01841a52804c2793b875934cf2cc7672d9ceb24de62a3c25ebd |
| Common owner-queue driver software14689 | COMPLETED0:0,10s,CPU1/GPU0;32 PASS,0 failures/errors/skips; source4 | S/runs/common_v5_owner_queue_driver_contracts_14689/acceptance.json;77184 bytes;6a721a952d387602271965766b9166c876ecaedb459a56e72b3d8050d3b6074f |
| Restored ROOT298 REV1 software14692 | COMPLETED0:0,7s,CPU1/GPU0;24 PASS,0 failures/errors/skips; source4 | S/runs/restored_root298_cost_software_14692/acceptance.json;12577 bytes;2c73a47c7696fa78138a7d5fe810c13b5ac7b37e8ca74f9098958198c759f9dd |

These identities were emitted by the actual CPU producers or preserved in root's actual terminal capture. This human preparation does not calculate hashes. The RUNNING records embedded in each software acceptance are the producer's allocation-time observations; separate readonly terminal metadata records the actual COMPLETED terminal. No historical missing terminal GPU field is silently converted to zero; the software allocations have their own strict live CPU/GPU0 guards.

Cost14576 status is ROOT_CURRENT_GPU_SUBMISSION_UNIVERSE_AND_TERMINAL_COST_CPU_ACCEPTED; schema root_current_gpu_cost_closure.v1. Its actual saved current scope contains four root submissions and298 GPU allocations,143583 GPU seconds,312 failed-allocation GPU seconds and maximum simultaneous owned GPUs2. It covers the fixed Oct11T14:25:00Z→Oct12T16:39:19Z window. It is current-root accounting, not whole historical project cost, a score, scientific evidence or publication acceptance.

14689 status is COMMON_V5_OWNER_QUEUE_FINISH_DRIVER_SOFTWARE_CPU_ACCEPTED_NOT_SCIENCE; schema common-v5-owner-queue-driver-software.v1. scientific_finish_executed:false. Its actual32 metadata/source fixtures do not establish the future Common/raw/stat112 scientific gate.

14692 status is RESTORED_ROOT298_COST_VERIFIER_SOFTWARE_CPU_ACCEPTED_NOT_REAL_RESTORE; schema restored-root298-cost-software.v1. production_restore_verified:false and science_accepted:false. Its actual24 synthetic accounting/core package-extract fixtures do not establish a real archived ROOT298 replay.

At preparation, no new Common scientific finish acceptance or new ROOT298 postarchive content acceptance is asserted or assigned a future SHA/output/job ID.

## 2. New actual terminal seals and fixed current sources

Readonly root terminal seals now exist:

- S/submissions/root_gpu_cost_v3_software14565_actual_metadata_terminal_seal/receipt.json14649; source4, actual88/software-only producer binding.
- S/submissions/root_gpu_cost_v3_audit14576_actual_full_cost_metadata_terminal_seal/receipt.json24087; actual full Cost18-file terminal evidence.
- S/submissions/common_ownerqueue_driver_software14689_actual_terminal_metadata_seal/receipt.json8123; schema common-ownerqueue-driver-software-terminal-metadata-only.v1; status ACTUAL_SOFTWARE_TERMINAL_METADATA_READBACK_PASS_NOT_COMMON_SCIENCE; actual9-column COMPLETED0:0/10s named CPU1 row, raw113/0,5files/1dir.
- S/submissions/restored_root298_cost_software_14692_actual_terminal_seal/receipt.json8732; schema restored-root298-cost-software-terminal-seal.v1; status ACTUAL_SOFTWARE_TERMINAL_METADATA_READBACK_PASS_NOT_REAL_COST_RESTORE; actual9-column COMPLETED0:0/7s named CPU1 row, raw105/0,6files/1dir.

These metadata-only seals preserve source/evidence bytes/inodes/mtime and readonly state. Unknown ownSHA of a seal must later be obtained in the owned CPU or selected from one exact actual package-index row as the qualified checker requires. A human byte count is not an accepted full receipt.

Current source packages, all including their own HANDOFF:

| Package | Original reviewed directory | Actual executing frozen directory | Owned file names / byte counts |
|---|---|---|---|
| V3 Cost | S/pending/root_gpu_cost_v3_running_window_v1/ | S/frozen/root_gpu_cost_v3_running_window_v1_14565/code/ | root_gpu_cost_audit.py42022;test_root_gpu_cost_audit.py25307;root_gpu_cost_cpu.sbatch1377;HANDOFF.md13694 |
| Common driver | S/pending/common_v5_owner_queue_finish_driver_v1/ | S/frozen/common_v5_owner_queue_finish_driver_v1_14689/code/ | driver.py31670;test_driver.py18718;driver_cpu.sbatch1445;HANDOFF.md12885 |
| ROOT298 REV1 checker | S/pending/restored_root298_cost_verifier_v1_rev1/ | S/frozen/restored_root298_cost_verifier_v1_rev1_14692/code/ | checker.py39239;test_checker.py21586;checker_cpu.sbatch1492;HANDOFF.md17808 |

Original and frozen counterpart tuples, before/end source metadata, real compiler/Bash results and tested-source sets are already saved in the actual software acceptances. They remain separate full identities. No old software suite76/58/130/32 is repeated to accept these packages. The observed new counts are88,32 and24 respectively.

Explicit software seeds:

- Cost14565 contracts.json1484/28c8177951c052b153edc06e487902833ec5962ef7724698386221b2e5905d13 and contracts.txt10700/40f3efb54257ea895cb613f993e3d39085a04c591ee7e37bf974c77f0cfc3b40.
- Common14689 contracts.json1481/40ea8503a96cb607eb0517c72a9fc0f396d45f7a55e1d97ada3fa6ca4f9dec04 and contracts.txt5221/50d70fc0052de5d78838780e6eda666f18e126a01f92a30b613f569006a01854. The complete source/control snapshot is embedded in its acceptance; do not invent a separate Common source_snapshot.json.
- ROOT29814692 contracts.json2735/912b663910dc60844399293956991c312202daa9680e9807cfececd748eef273;contracts.txt3995/829880e28b419a81a61bd19c1be57094e72841f99e2af28f59e1ad60025c0c88;source_snapshot.json5313/c65e8f8a38638890ee690f17bb868ca2d6d4ca82334e77e8187b96ef960a12a7.
- Conditional installed core interpreter observations belong to these acceptances and remain conditional execution facts, not a binary archive SOURCE/redistribution requirement.

Root claim folders are explicit provenance, not alternative executions:

- S/submissions/root_gpu_cost_v3_running_window_v1_primary_claim/
- S/submissions/root_gpu_cost_v3_audit_from13782_14565_primary_claim/
- S/submissions/common_v5_owner_queue_finish_driver_v1_primary_claim/ — request.json,in_progress.json,submit.json;actual submit14689 used CPU1/8G/10min software-only overrides.
- S/submissions/restored_root298_cost_verifier_v1_rev1_primary_claim/ — request.json,in_progress.json,submit.json;actual submit14692 used the originalCPU1/8G/10min launcher.

Also include the named actual scheduler captures software14565_20261014T041441Z, fullCost14576_20261014T041938Z, Common14689_20261014T053441Z and ROOT29814692_20261014T053441Z under their exact S/submissions folders, all root metadata/source seals and actual Slurm software logs. Their original submission-time no_acceptance_yet fields remain historical timepoint facts; do not rewrite them after acceptance.

## 3. Preserve failed Cost coverage and diagnostic provenance

Old13277/76 software/source and old14178 remain immutable history. Cost14178 actually FAILED1:0/38s; the strict covered==allocated closure rejected the independent time-universe coverage. Its typed status ROOT_GPU_COST_UNIVERSE_TYPED_INCOMPLETE and preserved raw queries are not Cost acceptance, OOM or a timeout attribution.

Explicit failure seed set: S/runs/root_gpu_cost_audit_14178/ and S/submissions/root_gpu_cost_audit14178_actual_failed_typed_metadata_terminal_seal/receipt.json, original root claim/queue-context/scheduler captures and actual logs. Preserve the original fixed window, argv/raw command evidence and missing-slot failure. Do not retrospectively alter it to match V3.

Actual diagnostic14448 was DIAGNOSTIC_ONLY, with report S/runs/root_cost_universe_diagnostic_14448/diagnostic.json34633/0c4542e66f42e8399f43f13aac09920f27d14f3f41dca822177431db379997f4 and the named actual metadata seal S/submissions/root_cost_universe_diagnostic14448_actual_metadata_terminal_seal/receipt.json. Its actual source3 are the three named files diagnostic.py12510,diagnostic_cpu.sbatch1060,HANDOFF.md3126 in S/pending/root_cost_time_universe_diagnostic_v1_rev2_14178/. Preserve its claim S/submissions/root_cost_time_universe_diagnostic_from14178_rev2_primary_claim/ and each saved actual query/control/raw output.

Actual probe14513 was DIAGNOSTIC_ONLY_FIXED_TIME_QUERY_VARIANTS_OBSERVED_NOT_COST_OR_SCIENCE_ACCEPTANCE. Its report is S/runs/root_cost_time_query_probe_14513/diagnostic.json63724/7e586fc784f6e233e0e9d2b6318907f3a5568999704314a1fb3ffd38114ab313. Its actual source3 are diagnostic.py26418,diagnostic_cpu.sbatch1086,HANDOFF.md9616 in S/pending/root_cost_time_query_probe_v1_rev1_14448/. Preserve claim S/submissions/root_cost_time_query_probe_from14448_rev1_primary_claim/, all saved baseline/duplicates/RUNNING/-X/unsupported-array/eligible/helpformat query controls/raw, scheduler capture and S/submissions/root_cost_time_query_probe14513_actual_metadata_terminal_seal_retry1/receipt.json. The first root metadata-preparation TypeError happened before its mkdir/chmod; retain that distinct history rather than mislabel it as the diagnostic's Slurm failure.

The actual baseline and duplicates variants covered297/298 and independently queried --state=RUNNING covered298/298. The unsupported --array query failed for actualSlurm22.05.8. These are diagnostic observations, not coverage filling or a broad query waiver. Eligible Unknown does not establish DB EligibleTime=0 or the exact actual failure cause. V3 changed only the independent user/time query by adding --state=RUNNING; original window/FIELDS/no -j-fill/strict duplicate/identity/coverage equality/cap2/failure-cost checks remain. Only actual14576 establishes the new full accounting acceptance.

## 4. Next Common finish uses accepted driver14689, unchanged original scientific source7

Current upstream identities stay exact:

- Old Common software13269: S/runs/common_successor_contracts_13269/acceptance.json6429/da595226c4a6db5b0fd6ebcfdce9d29e92362fb76d849e15941d0ca5c4a8886d;58 metadata acceptance remains unchanged.
- Old scientific entry: S/frozen/common_review_successor_v5_13269/code/common_review_successor.py, actual __file__/SELF/D/source7/PINS retained.
- Actual preflight13422: S/runs/formal_common_preflight_13407_13409/preflight.json889318/e30b4e61c45d8de80701d82199fda1d6c79176e9092d2a0f91c40e05598589e0.
- Current canonical Common13423 controller: S/submissions/formal_common_pending_from13422_primary_claim/root_submission.json5157/a5bb7cf6bc20fca0d7e05127065dad7f6b5b1f6cff9b8b192a109318aa7f2a22.
- Historical native13211 input: S/runs/native74_final_v2_13211/native74/acceptance.json9602/9effb60abceb03ca8c47b8e786f6613486bec96c90dec6aec517a1bd415fcff9;metadata-only readonly seal S/submissions/common_ownerqueue_driver_native13211_input_metadata_readonly_seal/receipt.json1455 changed only0664→0444, preserving bytes/inode/mtime.
- Ledger13782: S/runs/root_gpu_cost_seal-ledger_13782/root_gpu_submission_ledger.json2782/b4601b7acabf198d22bc949985fcb2f707df9b82049f24886d01449944adf998, J6/current amended controller as already qualified by actual14576.

Failure14600 stays FAILED1:0/144s with typed280/out0/err1308 and no scientific acceptance. Its original failed target-query stdout/stderr were not recorded; actual cause remains UNPROVEN. Preserve S/submissions/formal_common_finish14600_actual_failed_typed_metadata_terminal_seal/receipt.json5554 plus the separate later S/submissions/common13423_completed_controller_queue_diagnostic_metadata_20261014T043818Z/receipt.json2267/raw6. The later Invalid-job reply is not the original failed reply. Do not charge or claim a GPU rerun.

Root may uniquely submit a NEW owned CPU scientific finish using the accepted frozen driver only, after its actual software qualification and FULL Cost14576. This proposal itself performs no submission and names no future job/output:

    sbatch --parsable --export=ALL,COMMON_FINISH_DRIVER_ENTRY=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/common_v5_owner_queue_finish_driver_v1_14689/code/driver.py /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/common_v5_owner_queue_finish_driver_v1_14689/code/driver_cpu.sbatch finish --software-acceptance /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/common_v5_owner_queue_driver_contracts_14689/acceptance.json --software-sha256 6a721a952d387602271965766b9166c876ecaedb459a56e72b3d8050d3b6074f --out <ROOT_CHOSEN_NEW_ABSENT_MANUAL_COMMON_OUTPUT>

Production launcher/guard requires actualCPU2/16G/4h, named test9_common_ownerqueue_finish_cpu,organ/accountu21111210118,GPU0 and CPU isolation. Manual --out must be absent; never reuse14600's output or requeue its job. Do not apply the software-onlyCPU1/8G/10min override to scientific finish.

The driver records a fresh actual owner-wide squeue -h -u USER -o %i|%T command/raw with rc0 before calling old finish. ANY exact13423 parent/task/compressed range in ANY state blocks. Malformed/duplicates/nonzero/timeout/spawn failure blocks; no invalid-j-rc1→empty acceptance. A module-local proxy intercepts only the old exact LIST target call and three True kwargs once, delegates all other subprocess calls unchanged and restores the module binding in finally. It labels the result DERIVED_TARGET_ONLY and original target query INTERCEPTED_NOT_EXECUTED; original raw is never fabricated. Old sacct, worker lineage, scoring, official ipSAE/MSA, independent RAW and statistics/formal112 run unchanged in the owned CPU.

Successful production must emit BOTH:

1. NEW_MANUAL_COMMON_OUTPUT/acceptance.json — original schema formal_common_successor_acceptance.v1/status FORMAL_COMMON_RAW_CONTENT_INDEPENDENT_AND112_ACCEPTED_COMPUTATIONAL_ONLY, original source7, actual preflight/controller and raw/stat/formal112 graph. This remains the primary formal_common_review scientific gate.
2. NEW_MANUAL_COMMON_OUTPUT/owner_queue_driver_control/driver_execution_acceptance.json — distinct driver source/software/actual query/proof/source-control-runtime-end evidence; status COMMON_V5_UNCHANGED_FINISH_DRIVER_CPU_COMPLETE_SEPARATE_PROOF.

Also retain the exact actual command/stdout/stderr/target_queue_proof.json and the old output's derived-only squeue.txt with its explicit role. A primary file alone is insufficient if driver postflight fails; root must read actual content/fresh terminal and both proofs. Partial/typed failure remains unresolved and does not promote a report.

The report's existing request.common_successor must point to that future actual ORIGINAL primary Common acceptance, not to software14689 or driver_execution_acceptance. request.root_gpu_cost points to actualCost14576. Report load_bundle derives statistics/formal112 from the Common graph; do not manufacture a separate substitute statistics object or a future hash. Use the accepted report13282/54 build and separateQA routes only after the actual required upstream graph passes.

## 5. Actual Aux14692 is software only; ROOT298 content becomes a separate postarchive ACTIVE fence

Do not rerun the failed original standalone source14668. It FAILED1:0/0s with SyntaxError at else18 before main/CPUguard/hashes/compile/freeze/Out and any24 fixtures; no A/contracts/output exists. Preserve original S/pending/restored_root298_cost_verifier_v1/ OWN4, source proposal/claim, err489/out0, scheduler metadata4763 and S/submissions/restored_root298_cost_software14668_actual_failed_parse_metadata_terminal_seal/receipt.json3070. REV1 changes only syntax spacing and separate pending/frozen paths, not cost/scientific semantics.

The actual14692 frozen REV1 is the current checker. Its implementation reads historical software/Cost/journals/controller/source4+original4/raw/terminal evidence through the exact restored package index. Executable CODE is limited to accepted OWN4, fixed reader34228/9dec8043bcd8b44394869791f8046aff3f2787a491d8a285fcbc56a4c5e62fac and the exact Cost main9db3aec7c9c09f2c91ce36d93255350be74a4d2a2a3f6afc73d88292af7d14ed compiled from INDEXED bytes for unchanged pure APIs. The reader's archived SOURCE counterpart is separately indexed. CORE delivery_core_v2.py21981 executes only the software fixture package/extract; production checker never invokes its package/extract or live Cost main/writer/query.

Before source stage, include current OWN4/software snapshot/contracts/log/dependencies/runtime scalar observations and the mandatory new software terminal8732 in final_delivery_tools explicit SOURCES and evidence_seeds. Its real postarchive content A is LATE output and must NOT become a prerequisite for its own source audit, report, private bundle, package or extract.

Required order after actual source/report/public/private/package gates:

1. Existing13377/130 wrapper package; unchanged core.extract produces exact hash marker.
2. Existing13377 actual full indexed RAW scientific recomputation and readonly input seal, all indexed inputs only. Software130 alone is not this result.
3. ExistingG13558 actual indexed common13460 metadata proof, same package/root. Software32 alone is not this result.
4. Then new14692 ROOT298 real indexed accounting replay, same package/root and a fresh absent restored-root output child.
5. Independently read all actual late content/terminal proofs before ACTIVE. The new accounting gate is additional, never a replacement for the mandatory full RAW recomputation,13460 proof or primary nine-role gates.

Root-only FUTURE production command, using real preceding package/F/G full tuples and absent output; angle fields are deliberately unresolved and not literal shell commands:

    sbatch --parsable --export=ALL,ROOT298_CHECKER_ENTRY=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/restored_root298_cost_verifier_v1_rev1_14692/code/checker.py /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/restored_root298_cost_verifier_v1_rev1_14692/code/checker_cpu.sbatch verify --software /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/restored_root298_cost_software_14692/acceptance.json --software-sha 2c73a47c7696fa78138a7d5fe810c13b5ac7b37e8ca74f9098958198c759f9dd --package <ACTUAL_PACKAGE_RECEIPT> --package-sha <ACTUAL_CPU_SHA> --restore-root <ACTUAL_ISOLATED_ROOT> --out <NEW_ABSENT_CHILD> --raw-restore <ACTUAL_F_CONTEXT_RESTORE_ACCEPTANCE> --raw-restore-sha <ACTUAL_CPU_SHA> --metadata-restore <ACTUAL_G_ACCEPTANCE> --metadata-restore-sha <ACTUAL_CPU_SHA>

Actual production must requireCPU1/8G/10min/organ/named test9_restored_root298_cost,GPU0/isolatedconditional core. The exact current installed core executable link/resolved binary is a conditional runtime dependency checked before/end, not archive payload or generic live-root permission. Production creates no live S/tmp/frozen/runs; only typed fresh OUTPUT inside the restored root. Only current own CPU guard queries current scontrol. Historical software terminals are indexed saved evidence. Missing/ambiguous/writable/symbolic input refuses; no live original path rescue or explicit stream fill.

The checker rederives all four dispatches from indexed current controllers/launchers/phase roots and revalidates complete append-only journal/ledger identity. Its finite adapter permits only the TWO exact scalar E2E result_dir values; no read/open permission. It independently replays both exact saved query protocols, compares the WHOLE saved closure JSON (types/order/steps/identity/failure/interval flags), preliminary inventory and298/143583/312/cap2. No new Slurm accounting or neural inference is submitted during the replay.

Real future outputs are recomputed_root_gpu_cost.json and acceptance.json; schema restored-root298-cost-content.v1/status RESTORED_ROOT298_GPU_COST_INDEPENDENT_RECOMPUTATION_ACCEPTED_NOT_SCIENCE. Until actual content+terminal readback, no such proof is accepted. A complete indexed accounting result is still not a scientific/publication/ACTIVE acceptance by itself.

## 6. Explicit late SOURCES, seeds and public package boundaries

All nine roles must be the exact existing names:

- formal13260_terminal_v3
- native74_cache_catalog
- native74_cache_binding
- reference_free_e2e
- formal_common_review
- independent_statistics
- scientific_report
- final_delivery_tools
- default_workflow_integration

Do not introduce root_gpu_cost_source, Common-driver or ROOT298 as a tenth role. final_delivery_tools primary software gate stays actualComposer13377/130, source12/API15/Mapper14; current LIB13322/53, Integration13325/84, Mapper13319/201 and all accepted upstream source qualifiers remain unchanged. Aux14692/24 and driver14689/32 are additional source/evidence seeds. The future actual old Common primary gate and formal112/statistics/report actual results must still satisfy the original scientific roles; present software success cannot fill them.

Each CURRENT new OWN4 row must appear explicitly in module.sources/public_source_destinations, including HANDOFF.md and tests/launcher; one evidence seed is not a substitute for SOURCES. Preserve original/frozen counterparts by full identity and put each package in a DISTINCT public folder, with receipt aliases declared explicitly and no basename flattening:

- final_delivery_tools/root_gpu_cost_v3_running_window_v1/ — current four Cost files.
- final_delivery_tools/common_v5_owner_queue_finish_driver_v1/ — current four driver files.
- final_delivery_tools/restored_root298_cost_verifier_v1_rev1/ — current four checker files.
- Separate HISTORY source folder for failed original restored_root298_cost_verifier_v1/OWN4, never selected as executing current code.
- Separate diagnostic folders for root_cost_time_universe_diagnostic_v1_rev2_14178/OWN3 and root_cost_time_query_probe_v1_rev1_14448/OWN3.
- Retain fixed oldCost13277/source4 and G13558/source4 as separate historical/current-proof dependencies. G's fixed oldCost76 software binding qualifies the13460 metadata history; never replace that binding with newV3/88 or expand its executable CODE permission.

Explicit evidence_seeds additionally include ALL current SWAs, actual original/frozen tuples and compiler/Bash/source snapshots (Common snapshot embedded in A), contracts/logs, conditional runtime scalar metadata, actual terminal seals/raw, root claims/request/in-progress/submission results/source metadata seals and actual Slurm logs. Retain fullCost14576 ledger/journal closure/numeric command+raw stream/inventory/closure/active-query/unallocated13266 graph and associated original root journals J5/J6/current5157 controller, old5096 archive/candidate/transaction/13460 actual qualification, plus the separate unchanged13315 amendment. Use existing exact archive aliases if old canonical receipt-shaped observations persist; do not broaden the17-parent source contexts or rescue by basename.

Future Common completion adds BOTH original primary science A and separate driver execution graph, owner command/raw/proof/derived-only file, actual terminal and root claim/seal. Future ROOT298 content A and typed output proof are late postarchive records, collected after accepted assembly/restore; they are not prearchive seeds and cannot create a circular prerequisite.

Preserve all previously required late tools rather than replacing the source list with these three packages: captures13318,13421,13433 and native13288 OWN2 in distinct folders; atom13410 OWN2/actual diagnostic/claim/seal/execution copy; scheduler bootstrapOWN5/software13412/apply13420/default runtime manifest2823/qc6/old2archives/capture13433;13460 amendmentOWN4/J6/old/new/candidate/transaction/full13-file terminal evidence;G13558OWN4/HANDOFF/SWA/8149 terminal; all mandatory main/ERR1–9 and human readiness notes and earlier actual source/mapper/composer/default failure histories. Installed guides remain intact; this proposal joins late HUMAN evidence only if root installs or includes it explicitly.

## 7. Final gates and stopping boundaries remain

Actual CostFIRST is satisfied by14576. Remaining scientific Common/raw112/statistics/report build+separateQA must pass their actual complete graphs before all-nine source audit or staging. No scientific scores, pools or future hashes were inferred during this human preparation. Full28/268 denominator, actual failure costs, null/unresolved fields, no forced reruns/no superiority/experimental claims and global owned-GPU cap2 remain.

Use the accepted current LIB53 actual audit runner, correct stage inclusion receipt and CORE -B invocation established by installedERR7; do not pass acceptance.json to stage --audit or execute a0444 Python source directly. Stage only the actual source_inclusion_final.json pointer/SHA from the future accepted audit. Current source13316/V10 plus explicit old/default archive aliases remain authority; do not overwrite old reviewed JSON or relax finite contexts.

Report13282/54 build and independentQA remain required. ExistingERR6 public sequence remains: approved sole-baseline full Git tree/private history bundle, complete actual tool results and genuine metadata/IDs, owned-CPU fresh public readback+verifierPASS before export qualification, qualified inventory/compose, package, unchangedcore.extract, full EACH-input indexed RAW restore, G metadata restore, NEW ROOT298 replay, actual late proof readback, ACTIVE last. No software qualifier alone, a pointer hash alone or an exit0 job alone completes the project.

This proposal supplies no new receipt, journal, source policy, accepted scientific object, queue change or installation. Root must independently review it and any actual subsequent outputs. Main+ERR1–9 and all old readonly proposals, source packages and failure evidence remain unchanged.

