# Paired computational budget orchestration API

Status: software contract; production target/budget/method settings must be frozen by the root controller before GPU generation. These files contain no generated biological candidates or benchmark outcomes.

Authority root: /lustre/users/u21111210118/projects/test9
Module: source/rebuild/paired_budget_benchmark.py
CPU tests: steps/22_matched_benchmark/code/test_paired_budget_benchmark.py

## Frozen protocol (paired-budget-v1)

Required top-level fields:

- schema: paired-budget-v1
- protocol_id: a stable identifier
- scientific_scope: COMPUTATIONAL_ONLY
- execution_mode: persistent_session (required). One interpreter lifecycle per task; both methods follow this lifecycle.
- targets: nonempty array; each has target_id, input_manifest file receipt, analysis_role primary or diagnostic, and optionally budget_gpu_seconds. A per-target budget applies equally to both methods and every replicate.
- methods: exactly two distinct method_id records, each with session_start (an argument array), adapter_receipts (all adapter source files), config_receipt, native_score_name, native_score_direction (higher/lower), and optionally env. File receipts contain absolute path, bytes and SHA-256.
- replicate_seeds: distinct integers.
- gpu_count: positive integer, fixed for all arms.
- budget_gpu_seconds: positive integer, divisible by gpu_count.
- shutdown_reserve_seconds: identical positive integer for all arms.
- accounting_tolerance_seconds: predeclared nonnegative integer for scheduler integer-second resolution; actual deviations are always reported.
- hardware: exact gpu_name, optional minimum_memory_mib.
- sampling: frozen salt, uniform_n_per_replicate, native_top_k_per_replicate, both positive integers.
- inference: mode=descriptive_only (recommended for this benchmark), minimum_targets>=6, bootstrap_replicates, bootstrap_seed. Optional target_bootstrap mode only resamples the complete frozen primary target matrix.
- optional technical_amendment: an object with reason (nonempty string) and previous_plan_receipt for an explicit engineering repair. All previous plan/source/config bytes are preserved; target matrix, seeds, budgets, hardware, sampling and score identity cannot change.
- optional max_attempts_safety_limit: terminating this bound before time expires is an engineering early stop, not a full-budget method result.

Freeze:
    python paired_budget_benchmark.py freeze --protocol <protocol.json> --output <frozen_plan.json>

Before freeze, save versioned immutable source/config snapshots and invoke freeze/run/account with that orchestrator snapshot; the plan pins its exact path and bytes. The immutable plan contains all tasks, source fingerprint and original protocol receipt. The launcher must pin the plan SHA. Both the embedded protocol and task matrix are recomputed and checked before generation; method config and adapter source hashes are verified again. No result-based target, seed, budget, sequence-count or threshold selection is permitted.

## One persistent method session per task

Formal runner:
    python paired_budget_benchmark.py run-task --plan <frozen_plan.json> --plan-sha256 <SHA> --task-id <id> --output-dir <new-directory>

An explicit technical rerun also passes --technical-rerun-of <old engineering run_receipt.json>. The frozen protocol must include technical_amendment. Scientific rejection does not authorize a rerun/replacement. Every allocation uses a new output directory.

Method session_start supports:
{session_dir}, {target_manifest}, {target_manifest_sha256},
{target_id}, {method_id}, {task_id}, {protocol_id},
{generation_deadline_epoch}, {allocation_deadline_epoch},
{protocol_sha256}, {plan_sha256},
{method_config}, {method_config_sha256}, {method_definition_sha256}.

No shell evaluation occurs. Protected scheduler/GPU assignment environment variables cannot be overridden.

Corresponding environment:
BENCHMARK_TASK_ID, BENCHMARK_PROTOCOL_ID,
BENCHMARK_GENERATION_DEADLINE_EPOCH, BENCHMARK_ALLOCATION_DEADLINE_EPOCH,
BENCHMARK_PROTOCOL_SHA256, BENCHMARK_PLAN_SHA256,
BENCHMARK_METHOD_CONFIG_SHA256, BENCHMARK_METHOD_DEFINITION_SHA256,
BENCHMARK_TARGET_MANIFEST_SHA256.

Runtime integration:
    <private_python> benchmark_runtime.py method-session
        --method <method>
        --session-dir {session_dir}
        --target-manifest {target_manifest}
        --config {method_config}
        --config-sha256 {method_config_sha256}

The runner owns one process group and one independent hard-cutoff watchdog. Child prediction workers must inherit this group; they cannot daemonize or create another process session. Imports, model initialization and trajectory processing remain inside this counted persistent lifecycle. The watchdog kills the entire group even while the main controller is reading streams, and cleans up children even if their parent exits first. Initializing past the cutoff is explicitly session_initialization_boundary_censored, with zero invented attempts/candidates.

The runner verifies current scontrol AllocTRES/TRES GPU count before invoking any adapter; NVML visibility on a CPU allocation cannot authorize inference. Slurm StartTime is the allocation anchor. Environment startup, JIT, generation, internal predictions, filters, scientific rejections and engineering attempts consume the allocation budget. Requests continue sequentially until the shared generation cutoff (allocation start + budget_gpu_seconds/gpu_count - reserve), when the process group is hard-killed and a durable receipt is written within the common reserved tail. Normal runs retain the allocation only until the frozen allocation deadline. Engineering failures release it immediately; no idle fill disguises short use. A Slurm TimeLimit matching the whole-minute nominal budget provides an additional allocation boundary. GPU jobs must use one common frozen hardware type and the root controller's concurrency cap.

## Immutable filesystem RPC (paired-budget-session-v1)

Library stdout goes to task-level session logs. Control records are written atomically through a temporary file followed by rename. Only one outstanding request is permitted.

READY.json at session_dir:
    {"schema":"paired-budget-session-v1", "status":"READY",
     "pid":<owned process id>,
     "protocol_sha256":"...", "plan_sha256":"...",
     "method_config_sha256":"...", "target_manifest_sha256":"..."}

Request session_dir/requests/000000.json:
    {"schema":"paired-budget-session-v1", "action":"method-attempt",
     "request_id":"000000", "attempt_index":0, "attempt_dir":"<absolute>",
     "task_id":"...", "protocol_id":"...", "target_manifest":"<absolute>",
     "target_id":"...", "method_id":"...", "seed":<derived int>,
     "replicate_seed":<frozen int>, "remaining_seconds":<number>,
     "generation_deadline_epoch":<absolute cutoff>,
     "deadline_epoch":<same generation cutoff>,
     "allocation_deadline_epoch":<later shared cleanup endpoint>,
     "protocol_sha256":"...", "plan_sha256":"...",
     "method_config_sha256":"...", "method_definition_sha256":"...",
     "target_manifest_sha256":"..."}

The allocation_deadline_epoch includes the common cleanup reserve; generation stops at generation_deadline_epoch. Runtime must not use allocation_deadline_epoch to start a new model stage. The controller remains the sole termination authority.

Response session_dir/responses/000000.json:
    {"schema":"paired-budget-session-v1", "status":"COMPLETE",
     "request_id":"000000",
     "attempt_result":{"path":"<attempt_dir>/attempt_result.json",
                       "bytes":<int>, "sha256":"..."}}

READY/request/response identity and source/config hashes are checked. A truncated or mismatched control record, missing terminal result or exited session is an engineering failure. Attempts preserve immutable request/response receipts, original sequences and optional native updates. Every attempt pins its original sequences.jsonl and native_screening.jsonl file hashes, as well as normalized append-only ledger records. The independent checker requires every original complete line to appear in the ledger or an explicitly typed raw contract error; exact partial tail hashes are verified. Invalid stream contracts stop the session immediately as engineering failures. Every attempt records the same owned session PID plus byte ranges of the final session stdout/stderr, whose hashes are pinned after process cleanup. A hard boundary can have no response; complete sequences observed before cutoff remain eligible and partial lines are preserved as receipts.

## Incremental sequence and native-screening streams

The adapter immediately emits every complete sequence once to attempt_dir/sequences.jsonl, with a trailing newline per JSON record. This includes sequences subsequently rejected by native filters and sequences whose internal predictions are unfinished at cutoff.

Required sequence record:
    {
      "sequence_record_id": "unique-within-this-attempt",
      "sequence": "<complete canonical amino-acid string>",
      "lineage_id": "<parent design/trajectory identity>",
      "internal_acceptance": null,
      "native_score": null,
      "native_score_name": "<frozen native score name or null>",
      "completed_at_epoch": <time.time()>,
      "artifact_receipts": []
    }

Optional later updates go to attempt_dir/native_screening.jsonl:
    {
      "sequence_record_id": "<same original id>",
      "internal_acceptance": true|false|null,
      "native_score": <finite number or null>,
      "native_score_name": "<frozen native score name>",
      "completed_at_epoch": <time.time()>
    }

The original sequence event is never overwritten. The runner captures both streams with first-observed timestamps. CPU inventory merges nonnull updates observed before cutoff. Updates after cutoff remain auditable and cannot improve native top-k selection. An update without its original sequence, repeated original sequence ID, invalid sequence, invalid bool/score or incomplete terminal stream is an engineering contract error. A partial line at an actual hard boundary is retained as a tail receipt and never becomes a complete candidate.

Terminal attempt_dir/attempt_result.json:
    {"status":"COMPLETED"|"SCIENTIFIC_REJECT"|"ENGINEERING_FAILURE","reason":"..."}
COMPLETED must have emitted at least one complete sequence. Nonzero process exits are engineering failures. A forced budget stop is TIMED_OUT_BOUNDARY even if an adapter later declares a scientific status.

## Independent accounting and common evaluator cohorts

CPU accounting accepts an array of immutable run_receipt file receipts. Preserve all production engineering allocations and any explicitly amended reruns.

Raw scheduler command:
    sacct -X -j <allocation IDs> --noheader --parsable2 \
      --format=JobIDRaw,ElapsedRaw,AllocTRES,State,Start,End,NodeList,Partition

CPU commands:
    python paired_budget_benchmark.py account --plan <plan> --run-receipts <receipts.json> --sacct <raw.txt> --output <accounting.json>
    python paired_budget_benchmark.py cohort --plan <plan> --accounting <accounting.json> --output <cohorts.json>

The accountant independently rereads all sequence/attempt/update ledgers, verifies their receipts, recomputes denominators and joins unique scheduler allocation rows. Job steps and array summary rows do not double-count GPU seconds. Generic and typed GPU TRES must agree. Each counted allocation is gpu_count × ElapsedRaw. A positive GPU allocation without its run receipt fails accounting. Hardware, scheduler terminal state and realized budget must pass the frozen gate. Early engineering stops count in all resource totals but cannot define a fair full-budget method comparison. Multiple full-budget runs for the same frozen task are rejected; there is no post-result selection of a better run.

Primary uniform cohort: among all unique complete sequences observed before cutoff, choose the smallest SHA256(canonical([salt,target_id,replicate_seed,sequence_sha])). The method ID, native score and native acceptance flag do not enter this key. Sequence order, rank and acceptance flags cannot affect inclusion. Deduplication preserves every lineage and occurrence.

Secondary native cohort: predeclared fixed top-k by each method's own frozen scalar score, over all complete unique sequences with that score available. Score-missing sequences and underfilled cohorts are explicitly counted. This separately measures native ranking and does not replace the uniform cohort.

The common external evaluator must consume these cohort IDs and exact sequences, applying the same model/settings/thresholds with labels and method identity concealed from threshold development. Generation GPUs and common external evaluation cost are separate predeclared accounting scopes.

Evaluator outcomes file is a JSON array:
    {"cohort_record_id":"...", "evaluable":true, "pass":true}
    {"cohort_record_id":"...", "evaluable":false, "pass":null}
Absent outcome records are unresolved. They are never negative biology. Duplicate/unknown IDs and unevaluable false-pass records are errors.

CPU summary:
    python paired_budget_benchmark.py summarize --plan <plan> --accounting <accounting.json> --cohort <cohorts.json> --outcomes <outcomes.json> --output <summary.json>

Summaries include every replicate's all-attempt denominator, scientific reject/engineering/censored counts, complete unique sequence inventory, native accepted-attempt fraction, uniform and native evaluator coverage/pass-rate bounds, actual GPU use, and target-level paired effects. The yield is explicitly the observed common-uniform-sample pass count per allocated GPU hour; it is not an estimate of all unevaluated generated candidates. Empty sequence cohorts have unavailable quality rates; a fully observed full-budget task can have zero computational pass yield. Replicates/seeds do not increase biological target n. Diagnostic targets remain visible and do not enter the main primary target mean/inference. A missing frozen primary target disables inference rather than silently dropping a difficult case.

All outputs remain computational evidence. Experimental affinity, competition blockade and broad superiority require their own evidence.


## Separate independent implementation

steps/22_matched_benchmark/code/paired_budget_independent.py imports no production orchestration module. It independently reconstructs task identities, verifies the persistent session PID and READY/RPC/source/config identity, joins original sequence/native update streams, verifies Slurm StartTime and the shared cleanup cutoff, recounts every attempt and actual GPU second, then recomputes uniform SHA sampling and separate native top-k.

    python paired_budget_independent.py \
      --plan <frozen_plan.json> --run-receipts <receipts.json> \
      --sacct <raw_sacct.txt> --producer-accounting <accounting.json> \
      --producer-cohort <cohorts.json> --output <independent_acceptance.json>

A PASS on a partial fixture/partial matrix is structural acceptance only. Formal benchmark delivery must additionally require complete_generation_matrix=true and expected_tasks matching the complete frozen matrix, and independently verify every selected common-evaluator outcome. Source/config inputs referenced by frozen plans must retain their original bytes; use new filenames/source snapshots for technical amendments.

Contract receipts are stored in code/tests_<SlurmJobID>/receipt.json. Require a PASS, source_unchanged_during_tests=true and a source hash matching the frozen plan. Tests use synthetic bookkeeping and CPU processes; they do not validate model GPU execution or establish scientific outcomes.

Latest verified CPU contract: job 13088, 74 tests PASS, actual sacct AllocTRES billing=1,cpu=1,node=1 (gpu0). Production orchestrator SHA b37227bd862ee1425a59f5308be1ee3f4824042dea5d71c1269ad0f406b318f9; independent auditor SHA 5128ce9776371dd88a48bac7c95fbe0a6e2c8496253394d0ea657799768aaa54. No GPU/model inference or scientific outcomes were generated by these tests. The previous pilot_v1 snapshot and job 13006 / 57-test receipt remain preserved.

## Scheduler ownership and descendant GPU visibility (pilot_budget_v2)

Generation requires the invoking Slurm JobId to match a fresh scontrol record with JobState=RUNNING and exactly the frozen GPU count in its actual allocation TRES. This cluster's older scontrol exposes allocated TRES under TRES=; AllocTRES= is used when available. ReqTRES/ReqGRES never proves allocation. Final accounting uses sacct AllocTRES independently.

Ownership must come from SLURM_STEP_GPUS and/or SLURM_JOB_GPUS. A bare CUDA_VISIBLE_DEVICES UUID or a single device in cgroup-restricted NVML is insufficient. If both Slurm assignment variables are present, their physical UUID sets must match and each must have the required count.

Slurm numeric global IDs resolve through Device Minor -> GPU UUID in /proc/driver/nvidia/gpus/*/information. They never index directly into nvidia-smi / NVML, whose device indexes can be remapped by cgroup visibility. The selected UUID must be in both the physical /proc map and NVML inventory, and the model names must agree with the exact frozen hardware name. For example Slurm global ID 3, physical Device Minor 3 -> GPU-3, and visible NVML index 0 -> GPU-3 is valid.

An incoming CUDA_VISIBLE_DEVICES UUID must identify exactly the owned physical device set. A numeric mask is accepted only as the owned global minor IDs or as ordered local indexes 0..N-1; the receipt records which interpretation applies. In either case, the runner sets its method-session child's CUDA_VISIBLE_DEVICES to the full owned UUID(s) before any method interpreter is launched. For a single owned global device 3, an incoming local mask 0 becomes that device's physical UUID; a mask 1/2 or an unowned UUID is rejected. Missing ownership, duplicate/multiple devices, mixed masks and inconsistent Slurm assignments are errors.

initial.json retains the raw scontrol receipt, raw NVML output, raw /proc device-information texts, parsed ownership map, initial assignment environment, remapping interpretation and exact derived child mask. The final receipt pins initial.json. The independent auditor re-parses each raw source, reconstructs ownership and verifies the child mask without importing the production module. CPU fixtures exercise global-minor/NVML reindexing, wrong masks, non-RUNNING state and actual child inheritance; actual model/GPU execution still requires the engineering pilot.

Method env cannot override any SLURM_* or BENCHMARK_* variable or protected CUDA/NVIDIA/other GPU visibility variables. This includes SLURM_STEP_GPUS and SLURM_JOB_GPUS.

Reusable helper for independently launched GPU workers:

    import importlib.util, os, sys
    path = "/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py"
    spec = importlib.util.spec_from_file_location("frozen_gpu_budget", path)
    guard_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = guard_module
    spec.loader.exec_module(guard_module)
    receipt = guard_module.gpu_ownership_guard(
        expected_count=1, expected_gpu_name="NVIDIA A100-PCIE-40GB")
    os.environ["CUDA_VISIBLE_DEVICES"] = receipt["child_cuda_visible_devices"]

Execute the helper and set the returned mask before importing torch/JAX or creating any CUDA context. The helper returns scheduler_record, scheduler_alloc_tres, hardware, owned_gpu_uuids and child_cuda_visible_devices; the worker must preserve this JSON receipt. Supplying env is supported for CPU test fixtures, not for inventing production assignments.

Fresh CPU-only hardware inventory is steps/23_common_review/inputs/proc_gpu_inventory_13044.json, SHA eb4a7eb9d026b85d228a2983e85c60a883a117c6438babadecbcbe106e1a29e7. It confirms the node's physical model map, not job ownership. Every GPU worker independently verifies its own RUNNING allocation.


## Physical allocation IDs and arrays (pilot_budget_v3)

SLURM_ARRAY_JOB_ID + "_" + SLURM_ARRAY_TASK_ID is a logical task alias. It is not JobIDRaw. The runner records both allocation_key (the preserved logical alias) and raw_allocation_id, with a structured allocation_identity. The unique physical allocation ID is the numeric JobId in the original scontrol_start receipt; ArrayJobId and ArrayTaskId reconstruct the alias. Every declared alias, ID and invoking Slurm environment must agree. Example: JobId=13070 ArrayJobId=13069 ArrayTaskId=0 means logical 13069_0 but raw allocation 13070; JobId=13069 ArrayJobId=13069 ArrayTaskId=1 means logical 13069_1 and raw allocation 13069. The number equal to an array master ID can be a real task's physical ID.

The standard export remains:

    sacct -X -j <jobs> -n -P --format=JobIDRaw,ElapsedRaw,AllocTRES,State,Start,End,NodeList,Partition

Eight headerless fields are supported unchanged. An optional nine-field diagnostic export adds JobID immediately after JobIDRaw:

    sacct -X -j <jobs> -n -P --format=JobIDRaw,JobID,ElapsedRaw,AllocTRES,State,Start,End,NodeList,Partition

The nine-field JobID alias must match the original scontrol identity. In eight-field input the alias is independently derived from scontrol; it is never guessed from a numeric master ID or array order. Job steps and explicit bracketed array summaries are excluded. Duplicate physical IDs, including an extra master/summary row with the same numeric ID as a real task, are rejected. Positive GPU resource rows with no unique preserved run receipt are errors.

GPU seconds are elapsed seconds times actual GPU count for each distinct physical allocation. Both failed engineering arms and technical reruns remain in all resource totals. Early failures remain noncomparable, with their shorter observed usage; they are not filled or replaced to create full-budget scientific results.

Historical run receipts lacking the new fields are read without mutation: both producer and separate independent auditor derive physical identity from the verified original scheduler_start receipt and check the old allocation_key. Missing original evidence or contradictory identity fails closed. Completed 13069 receipts, pilot_budget_v2 snapshots and prior test receipts remain unchanged.

A new accounting implementation can audit an older plan: account/cohort/summarize verify the historical plan's pinned generation orchestrator bytes, configs and sources, and record the separate current accounting_orchestrator identity. Generation still requires the executing immutable orchestrator to equal the frozen plan exactly. No old generation source or receipt is edited to repair post-run accounting.

The 74-test CPU contract includes the actual 13069/13070 alias case, the master numeric collision, both export formats, logical/raw forgery, missing positive allocations, duplicate master rows, step exclusion, unchanged historical receipt bytes and a real persistent CPU child running under mocked array scheduler metadata. These are software/accounting validations, not biological benchmark results.

## Multi-record scontrol array-master output (pilot_budget_v4)

On this cluster, scontrol show job <numeric array master> -o can return several task records. The pilot13069_1 original receipt contains its own JobId=13069 / ArrayTaskId=1 RUNNING record and a JobId=13070 / ArrayTaskId=0 FAILED sibling record. Their StartTime and TRES differ. Using the first JobState, StartTime or TRES in the entire output is invalid.

select_scheduler_record(scontrol_text, raw_job_id=None, logical_key=None) requires exactly one matching individual record. Generation supplies both invoking SLURM_JOB_ID and its logical alias; the reusable GPU helper supplies the invoking physical ID and then validates array environment identity. Old-run accounting and independent audit reconstruct the alias from each original record and match the preserved allocation_key. Multiple matches, missing matches, repeated IDs within a record and contradictory raw/alias combinations are rejected.

All state, actual allocation TRES and deadline anchoring use that selected individual record. Full original scontrol text remains preserved. The GPU helper returns selected_scheduler_record along with full scheduler_record; generation receipts contain scheduler_selected_record alongside the original scheduler_start file receipt. The independent auditor reselects the record from the original raw evidence and checks any declared selected record.

The 74-test contract exercises both sibling orders, a failed selected task with a RUNNING sibling, incorrect sibling GPU counts/StartTime, ambiguity, wrong aliases, old receipts without newly introduced fields, and a real persistent CPU child with a FAILED/TRES0 sibling first. Source and independent auditor hashes remained unchanged throughout the tests.

pilot_budget_v3 is preserved as an unused engineering snapshot: its strict single-record parsing correctly refused the historical multi-record evidence. CPU13083 failed that audit before acceptance; neither its receipt nor old pilot files were altered. Use v4 for the next engineering freeze and post-run accounting.

