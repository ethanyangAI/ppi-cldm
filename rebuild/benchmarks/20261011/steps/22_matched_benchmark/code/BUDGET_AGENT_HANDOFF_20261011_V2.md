# Budget / fairness agent handoff — 2026-10-11

This is a completed subtask handoff. Root is still pursuing the user's full workflow and benchmark delivery; this handoff does not declare the scientific project complete. Root has the current-thread 30-minute heartbeat ppi-blocker-benchmark, not a new thread. Do not create a duplicate automation, GPU array, or formal plan.

## Execution constraints and ownership

Remote R=/lustre/users/u21111210118/projects/test9. SSH private key /Users/yangzijian/.ssh/id_ed25519, UseKeychain=yes, IdentitiesOnly=yes, BatchMode=yes, port22560 u21111210118@192.168.81.6.
Only CPU organ / account u21111210118 / qos normal, no GRES, exact --chdir=R/steps/22_matched_benchmark, actual RUNNING GPU0, private core Python, empty/NoDevFiles/-1 CUDA mask, PS1 guard, PYTHONNOUSERSITE=1, OPENBLAS_NUM_THREADS=1, PYTHONDONTWRITEBYTECODE=1, unset PYTHONPATH.
No local code/data, no GPU submission, no ACTIVE/GitHub/commit work by this agent.
Budget agent owns source/rebuild/paired_budget_benchmark.py and step22/code. Do not mutate accepted/frozen source, plans, runtime config, inputs or original evidence.

## Accepted generic allocation / deadline source (unchanged)

R/steps/22_matched_benchmark/settings/pilot_budget_v4/source/
- paired_budget_benchmark.py 84446 bytes SHA b37227bd862ee1425a59f5308be1ee3f4824042dea5d71c1269ad0f406b318f9
- paired_budget_independent.py 37640 bytes SHA 5128ce9776371dd88a48bac7c95fbe0a6e2c8496253394d0ea657799768aaa54
- 74 CPU contracts, CPU13088 GPU0; source snapshot all0444, directories0555.

Actual unique RUNNING scheduler record + allocatedGPU1; raw numeric JobId and logical array master_index both preserved. Owned Slurm global JOB/STEP GPU IDs resolve via Device Minor→UUID and match NVML UUID; cgroup-local NVML index0 can represent global minor3. Child CUDA_VISIBLE_DEVICES is the exact owned UUID. Bare CUDA UUID is not ownership.
Slurm StartTime is budget origin. Generation cutoff3590s, identical10s shutdown reserve, total3600±2 actualGPU seconds. Hard kill entire persistent method process group, including children. Receipt and complete raw ledgers must be durable. COMPLETED/TIMEOUT only with full source/ownership/hardware/ledger proof; engineering short exit releases immediately and remains incomparable.
sacct -X standard8 columns supported; physical numeric JobIDRaw, not logical array alias, is the unique counting key. Do not count steps/master summaries twice. A positive unjoined GPU allocation fails closed.
Raw all-complete sequence pool includes native rejection and scoreNA, unique sequence identities retain every lineage. Uniform SHA selection K3, native separate K2; no post-result equal-count selection.

## Current engineering plan_v5 / runtime_v8 preGPU proof

R/steps/22_matched_benchmark/engineering_pilot/plan_v5/frozen_plan.json:
8182 bytes SHA 8b47944f5ba5662c2e382b2f6b52553760d95a0ed678ea4a4c9d44396cb038bb.
Runtime pilot_v8/source/benchmark_runtime.py:
51064 bytes SHA 51b516a692d369f4d9a6ae9e3c39c0294da219c4d065420bbf9538a4af4b6562.

CPU13167 COMPLETED34s, GPU0, independent preGPU PASS351 exact current-operative receipts +161 checks:
R/steps/22_matched_benchmark/code/engineering_plan_v5_audit_v3_13167/acceptance.json
111740 bytes SHA 2378283d96fd16100dcc92e8169026bc62276baf583c9310ca1b3aa653c24be5.
Source audit_engineering_plan_v5_v3.py is readonly.
All7 chainfix13094 target geometry/query/hotspots/reference maps unchanged; only original incorrect RFD chain metadata corrected. Exact v7→v8 scientific configs unchanged. AST/diff: only after-return raw confidence/same-aux official PDB archival and observational RPC identity metadata; no extra model calls or RNG draws. Archive work remains inside allocated deadline.

Historical plan_v4 / pilot_v7 were audited but never GPU-executed:
code/engineering_plan_v4_audit_13141/EXECUTION_STATUS.json 2766 bytes SHA238fb2f59694c8b1ee0b091b1530b258d2d3fb9f24ad07b546e2cc2cacce6d19.
Old b47e302... development source33676B from readiness12980 has no exact archive, retained HISTORICAL_UNRESOLVED_PROVENANCE and excluded from current readiness. Final13092/v6-v7 source43050B SHA1325556... did not drift. Failed13161/13164 arose from over-recursing prior historical preflight comparison.old_config→legacy12980, not current v8 source/config failure. Current operative graph351 closes. Prior status/preflight original hashes are directly checked; historical old_config branches are not current dependencies.

## Actual engineering13175 independent accounting — COMPLETE

Array13175 engineering plan5, two tasks, maxattempt1:
RF logical13175_0→raw physical13181,202GPU seconds, one COMPLETED attempt,8 complete canonical65aa unique records,8 native updates.
BC logical13175_1→raw physical13175,389GPU seconds, one SCIENTIFIC_REJECT attempt before MPNN,0 complete sequences/updates.
Both outer runs EARLY_ENGINEERING_FAILURE because deliberate maxattempt1 cap; scheduler FAILED exit2 expected in this engineering protocol. No formal full-budget comparability; native content acceptance is separate. Scientific rejection does not prove unexecuted later API stages.

CPU13209 COMPLETED1s GPU0:
R/steps/22_matched_benchmark/code/engineering13175_accounting_13209/independent_acceptance.json
2235 bytes SHA143050799e9c9f75f964541c8d583b54edba5309c8b5c41d525708dc9fac33a2.
Status INDEPENDENT_BUDGET_LEDGER_AND_COHORT_AUDIT_PASS; allocation_count2, expected_tasks2, all_attempt_count2, all_allocated_gpu_seconds591, raw8, native8, full_budget_comparable_tasks0, selected0.
REPORT.json 5446 bytes SHA3adb7181ca1f48fd7159a66a7b7c53d895f11cf53b6f88ed2418f9190769d490.
All files0444, directory0555.
run_receipts.json 493 bytes SHA26f59b85be4d9fc05904a990d31a3736bdb1648908d7486ad8ce6fbc04591e0f.
Actual wrapper source code/audit_engineering_actual_array.py 4873 SHA7fa2daad5778a56a536ab14b20d22bc97401a3b772932a91ef9be276d4f693f8.

Historical failed array13069 independently retained183+17=200GPU seconds:
code/pilot13069_array_accounting_13090/report.json 9449 SHA09ed8a3d5d0493db99ac75eb262fdeefd0f291feff9b70310570d974752ce93f.
Only these two engineering batches sum791. This is NOT total project GPU cost. Native controls, BBF diagnostic, other development and forthcoming BC supplemental allocations need their own registry/accounting. Supplemental allocation must never be merged into main exact2 run set or formal candidates.

## Final formal fairness/native source snapshot — COMPLETE

CPU13210 COMPLETED8s GPU0,64 tests PASS; no formal freeze or GPU submission:
R/steps/22_matched_benchmark/code/formal_contract_v2/manifest.json
11279 bytes SHA43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47.
source/formal_benchmark_contract.py 46984 bytes SHA768c0ca8fbdf942638688ed6a12ea1e88a42b50d7c219b902bbc3d945ddeb4bc.
source/test_formal_benchmark_contract.py 38371 bytes SHA792a805d12d6c48cd75b847c3a400eee6ab1b704793c75176bcd267019571ce4.
source/FORMAL_FAIRNESS_ACCEPTANCE.md has exact API/checklist; all snapshot files0444 directories0555.

Pins final root freeze_formal_benchmark_v3.py11994 bytes SHAe23f09c1f01f1459fe1281f2648dd1e3c0d7d0e9704b9024acdaf732b7c3b3d8 plus copied readonly root helper/combiner/engineering helper. Contract does not freeze the formal plan.
Root combine_engineering_acceptance_v1.py4538B SHA0cb377a068ce893b08637ae50142dd5ac7a48f735279b74fecdde2ab2f37dd49;10 tests cover success, bad source/config/task, missing native AF2 stage, engineering failure, same-count wrong run set, supplemental extra run, run receipt task drift, wrong assignedGPU count.

40 original fixed-matrix/statistics contracts retained plus native64 coverage. CPU13168/50PASS receipt preserved; CPU13180/64PASS preserved. Exact historical50/64 source and old root helper bytes recovered into snapshot history_exact_bytes with logical receipt→readonly same-SHA/bytes aliases. Original receipts unchanged; never claim current mutable prep path has old SHA.
Failed13208 incomplete snapshot retained under code/formal_contract_v2_failed_13208; successful authoritative v2 is the fixed path above.

Fixed formal28=7targets×2methods×seeds21011/21012,65aa,1GPU A100-PCIE40GB min40000MiB,3600s/reserve10/tol2, no maxattempt cap. Six primary targets MDM2/KEAP1/EGFR/BCLXL/HRAS/CRK; BBF111 diagnostic excludes macro. Uniform3/native2 same pre-generation SHA salt. Boltz3 seed31011/12/13 primary R1 officialipSAE10max continuous; AF2models1..5 seed31021 separate; R0>=1 diagnostic only. Fixed112 replicate×cohort×engine rows; empty complete-budget pool has qualitynull/observed count0, unaccepted generation null; all selected/model slots required, both replicates equal mean, all six paired targets for macro; no p/CI.

Native collector exact frozen source:
R/steps/21_method_runtime/runs/native_collector_contracts_13166/source/audit_native_confidence_v8.py
16372 bytes SHAeca561182d06eca52bde005b45f02dd261d57b916d70ea5e34e99e86a79830b5.
Must audit every actual attempt, every native update including reject/NA/partial/boundary, never pilot/top2-only.
Bundle:
{schema:"formal_native_output_audit_bundle.v1",plan:exact_plan_receipt,collector_source:exact13166,attempts:[{run_receipt,task_id,attempt_index,acceptance:exact_per_attempt_collector_receipt}]}
Source_line_number=native_update_index+1. Raw stream hash/full lines/partial tail and all first-observation normalized updates exactly join. Every observation binds task,attempt,replicate,plan,protocol,config,target,fullquery.
Independent contract stdlib NPZ parser recomputes primitive arrays/query/PDBCApLDDT/RFbidirectionalcrossPAE/BCofficial per-modelround2 then mean/round2 score. Scored BC requires exactly models1/2, RFexactmodel1; NA remains NA. Durable complete unindexed sidecars retained, partial artifacts not imputed, formal cutoff eligibility remains frozen runner first observation. CPU collector actual native filters/RMSD proof is retained; raw scalar recomputation does not import its numpy score values.
CLI:
python immutable_formal_contract_v2/source/formal_benchmark_contract.py
--plan --accounting --cohorts --independent-budget --run-receipts
--common --membership --inference --scored --target-statistics --native-audits --output

## Next root / followup work

Root/runtime collect main RF native8 content and BC completed-trajectory rejection proof. BC later API supplemental stage coverage separately frozen/source/config/plan/coverage_mode and GPU accounting; not formal candidates. Combined engineering main independent budget must remain exact2 original runs.
Root needs common-agent independent audit of complete110 BBF diagnostic, fixed labels and no threshold tuning; this agent releases concurrency slot for that work.
When real formal plan is frozen, independently verify exact plan/helper/source/policies and all28task matrix before root launch. After terminal actual runs, frozen v4 ledger/sacct audit and v2 every-attempt native bundle, blind score/membership/112rows/target statistics audits. Preserve every engineering/failure cost and all missing outcomes.
No claim of workflow superiority, structural affinity, binding/blockade or completed formal benchmark exists yet in this subtask.

