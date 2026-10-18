# Independent resource and supplemental contracts v3

Software/CPU only; no GPU submission or scientific design. Source files and meaningful fixtures are frozen after CPU54-contract run13252. Accepted budgetv4 and formal_contract_v3 remain unchanged.

Supplemental audit:
python source/audit_supplemental_engineering.py --actual-job 13234 --cancelled-job 13229 --amendment <immutable amendment.json> --output-dir <actual outputs> --content-acceptance <supplemental_base_audit/acceptance.json> --report-dir <NEW independent output>
Counts only the positive supplemental allocation and the cancelled request's zero cost. Requires actual CPU2/GPU1, RUNNING ownership, physical DeviceMinor/UUID/CVD proof, hard3600+2 accounting,20 complete65aa lineages, fixed rawindex0, both actual complex model confidence/query/PDB recomputation, default late API receipts and no formal ledgers/native acceptance. It keeps main591 unchanged.

Future formal policy freeze (root only, CPU Slurm):
python source/independent_resource_policy.py freeze --plan <immutable formal_v3 plan> --original-launcher <immutable CPU4 launcher> --output-dir <NEW immutable policy dir>
Produces resource_policy.json, formal_generation_cpu3.sbatch and freeze_receipt.json. Only one literal SBATCH CPUs4->3 changes. Exact original/new launcher, plan, protocol and source receipts are pinned. CPU3/GPU1/64GiB/OMP4/OpenBLAS1 apply identically to all28 and every technical rerun. This freezes additional resource metadata and does not edit scientific plan/protocol/old launcher.

Before GPU submit, root records readonly submit receipt:
{"job_id":"<array master>","submit_argv":["sbatch","--parsable","<policy new launcher path>"],"launcher":<policy launcher receipt>,"resource_policy":<policy receipt>,"plan":<policy plan receipt>}
Optional array/dependency overrides allowed; CPU/GPU/memory/partition/QOS/account/time overrides rejected. Each rerun has its own immutable submit receipt. Preserve original CPU4 launcher as AUDITED_NOT_EXECUTED.

Final independent CPU resource gate:
python source/independent_resource_policy.py audit --policy <policy.json> --run-receipts <JSON array exact run receipts> --sacct <all actual master/attempt rows standard8/9fields> --submit-receipts <JSON array submit receipts> --output-dir <NEW output>
Requires all28 frozen task IDs, includes every physical positive allocation/rerun, rejects missing/unrecorded/duplicate allocations, CPU3/GPU1 raw RUNNING and terminal TRES, actual A10040GB, exact scheduler command/source launcher, StartTime after policy freeze and memory64GiB. Missing mem AllocTRES is UNAVAILABLE_NOT_ZERO. Full scientific comparability remains separately governed by accepted independent budget and64formal contracts: resource PASS alone is not scientific success or full-budget acceptance. Cgroup CPU isolation/affinity are UNOBSERVED in existing runtime receipts; scheduler allocated CPUs are confirmed, OMP4 may cause CPU contention. Engineering supplemental CPU2 is excluded from all28.

No threshold/model/seed/native ranking changes. Supplemental sequences cannot enter formal candidate counts or comparative scientific outcomes.

Corrected current supplemental independent audit:
python source/audit_seeded_supplemental.py --actual-job 13246 --content-acceptance <current collector supplemental_base_audit/acceptance.json> --rng-acceptance <deterministic_rng.json> --history-audit <immutable old13234 independent audit receipt JSON> --report-dir <NEW output>
Pins corrected13239 config/source and13241 directCPU2 launcher. Independently replays ALL observed Python randint returns and ALL NumPy PCG64 fallback seed values; exact MPNN constructorseed equals first Python draw; actual AF2 ownerseed791205 and uint32 key-after-predict retained. Python/NumPy distinct streams remain separate. Original13234/13235 cost381 is reproducibility-unresolved engineering history, excluded from current deterministic gate. All20 supplemental sequences excludedformal pool.

Pre-generation sequence scopeclarification is embedded in resource_policy.json and binds the immutable formal plan, original protocol and exactv8 source: primary candidates are complete original MPNN proposals (native rejects and unavailable scores included). Complete optimized trajectory hard/pseudo sequences and RF backbone intermediates have separate inventories and phase/rejection denominators. Zero MPNN proposals must never be described as zero total complete optimized sequences. No post-engineering eligibility expansion, calls, filters, seeds, sampling salt or cutoff change.

