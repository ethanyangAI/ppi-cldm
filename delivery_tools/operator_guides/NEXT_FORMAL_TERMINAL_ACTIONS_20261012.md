# Formal13260 全部终止后的精确操作交接（2026-10-12）

这是只读源码/元数据形成的人工操作指南，不是执行回执。root 独占所有 Slurm 提交、GPU 调度、默认安装、Git/GitHub、正式归档和 ACTIVE。所有新增 hash、测试、解析评分、成本核算、打包与恢复验证均在实际 pureCPU Slurm allocation 内；登录节点不执行这些计算。每一步只消费显式、当前已接受的 exact path/bytes/SHA，不能用文件名、mtime、latest、exit0或布尔声明替代。

## 当前实际资格与仍未完成的部分

- SourceV10 job13316：COMPLETED0:0/123s CPU1 GPU0，software122/whole12/runner11，683 source/0issues，8源码身份12原父字段、四映射/588 archive成员全部 source 内容闭合。Status CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY；不是最终源码发布。
- MapperV4 job13319：COMPLETED13s CPU1 GPU0，201PASS/whole14/full17parent views，其中16个 Source closure generated observations；status EXACT_BBF6_RECOVERED5_NINE_ANNOTATIONS_ARCHIVE588_AND_EIGHT_SOURCE_ALIASES_MAPPER_CPU_ACCEPTED。
- Corrected LIB fixturefix1 job13322：实际53PASS、COMPLETED2s CPU1 GPU0，whole6。旧13320 FAILED2s/52PASS+1ERROR严格保留。当前软件源码为 pending/final_source_closure_v3_fixturefix1/，语义/schema/jobname V3不变。
- Integration13324：FAILED4s/83PASS+1ERROR，未安装默认源码。独立修复 pending/default_workflow_materialized_integration_v3_fixturefix1/ job13325已实际 COMPLETED0:0/4s CPU1GPU0、84PASS、owned4+acceptedLIB6完整软件绑定；严格 production main未改，原失败原包保留。软件接受不等于默认apply。
- Composer13321：FAILED6s/63PASS+3ERROR，原8 sealed保留。中间fixturefix1 job13323实际FAILED1:0/5s CPU1GPU0、66定义中2个JSONDecodeError（toy JSON被写为非JSON literal）；不是科学数据错误。当前 pending/final_delivery_composer_v4_fixturefix2/ exact8/66独立 STATIC_PASS，root新13326实际资格仍待真实终局回执；禁止沿用13321/13323。
- PostprocessV2 job13258 software37；native catalog13265 software24+20worker/74raw；CommonV5 job13269 software58；costV2 job13277 software76；reportV1 job13282 software54 均已有实际软件资格。不要重复软件任务；软件不能代替其未来真实生产内容。
- E2E设计13304、设计CPU13309、复核13311、finalCPU13312已真实闭合：candidate1×65aa/refolds3/passed0/REJECTED，status REFERENCE_FREE_E2E_COMPUTATIONAL_CHAIN_CONTENT_ACCEPTED。无有效blocker/实验阻断/优越性结论。
- Formal13260 原28组尚未全部终止。13264 afterany:13260 已唯一提交，不重复。formal release/throttle2 已实际完成，不重复解除hold。现在所有候选/score阅读与选择继续受 ALL28terminal 独立收集门控。
- 所有默认安装仍由 root 保守等 ALL28terminal；当前源码仍C3，不能提前 apply/stage olddefault覆盖新default。
- 最终 common112/raw/independent/statistics/current-GPU-cost/report build+QA/final-source/Git/publictree/package/isolatedrestore/ACTIVE 均需单独真实回执。

固定root：
R=/lustre/users/u21111210118/projects/test9
POST=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/formal_postprocess_v2_13258/code
COMMON=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/common_review_successor_v5_13269/code
COST=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/root_gpu_cost_v2_13277/code
REPORT=/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/final_scientific_report_v1_13282/code

下列命令是 exact CLI 模板；每个 *_SHA、NEW_*、ACTUAL_* 必须由root已接受的CPU输出填入。未填入的路径/参数不代表已存在或已接受，不自动选择目录或推断SHA。

## 1. 唯一 terminal collector13264，而非再提交collect

既有提交是：
sbatch --parsable --dependency=afterany:13260 /lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/code/formal13260_terminal_v3/formal13260_terminal_cpu.sbatch collect --collection-out /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/formal_collection_13260

root 先读取 actual squeue/sacct，确认13260所有28slot终止、13264实际终止。13264内 wrapper会再核ALL28无active、first actual allocation/resource/native/34软件/source/submission seal，并调用 frozen postprocessV2 collect。Missing/nonterminal/failed gate保存 typed_incomplete，禁止cohort/preparation。不要把 afterany/COMPLETED本身视为content验收。

外层：/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/formal_terminal13260_cpu13264/acceptance.json
必须 status FORMAL13260_TERMINAL_V2_COLLECTION_CPU_ACCEPTED_ROOT_COMMON_PREPARATION_PENDING。
内层：/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/formal_collection_13260/acceptance.json
必须 schema formal_postprocess_collection.v2 / status FORMAL_ALLOCATION_NATIVE_AND_COHORT_CLOSURE_ACCEPTED。
包含28完整coverage/所有allocation、native每attempt、独立budget/cohort、raw更新/轨迹/失败与cost；固定65aa canonical MPNN proposals仍主池，hard/pseudo/backbone不能混入。typed missing不是生物学阴性。Source/postprocess本身37资格13258已接受，不再跑一次替代collector。

唯一wrapper捕获的 collect_v2.command.json/.stdout/.stderr 是实际argv权威。其 underlying CLI语法为：
sbatch "$POST/formal_postprocess_cpu_v2.sbatch" collect --plan ACTUAL_FROZEN_PLAN --plan-sha256 ACTUAL_PLAN_SHA --array-job-id 13260 --run-root "/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/formal_runs" --resource-policy ACTUAL_POLICY --policy-sha256 ACTUAL_POLICY_SHA --submit-receipts ACTUAL_SEALED_RECEIPT_LIST --submit-receipts-sha256 ACTUAL_LIST_SHA --out NEW_COLLECTION_DIR
本命令只解释已提交collector，不授权重复收集或其他primaryarray合并。

## 2. frozen postprocess37 prepare-common

真实inner collectionaccepted后：
sbatch --parsable "$POST/formal_postprocess_cpu_v2.sbatch" prepare-common --collection "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/formal_collection_13260/acceptance.json" --collection-sha256 ACTUAL_COLLECTION_SHA --out "$NEW_COMMON_PREPARATION_DIR"

必须 status FORMAL_BLIND_COMMON_REVIEW_PREPARED_NOT_INFERRED，固定7targets/28arms、uniformK3/nativeK2、空池与underfill显式保留。Inference plan仅blind target+sequence dedup，没有origin/native ranking向评分泄露。固定MSA、所有modelseed/query/source均不改。root_dispatch只是待提交列表，不是推断完成。

## 3. native catalog24/13265只做新exact binding

已有 /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/native74_cache_catalog_13265/acceptance.json：
CPU_CACHE_GUARD_CATALOG_COMPLETE；catalog NATIVE74_RAW_CACHE_CATALOG_VERIFIED_FUTURE_FORMAL_BINDING_PENDING。
实际catalog4061/ed9973988c8a20c2182c71b821bacc4b781fccfcb7f2fe5766bd04c663dca7d0。20workers/74raw接受不自动授权新plan复用。

新的root CPU：
sbatch --parsable "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/code/native74_cache_guard_v1/native74_cache_cpu.sbatch" bind --catalog "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/native74_cache_catalog_13265/acceptance.json" --catalog-sha256 ACTUAL_CATALOG_SHA --preparation "$NEW_COMMON_PREPARATION_DIR/acceptance.json" --preparation-sha256 ACTUAL_PREPARATION_SHA

必须 CPU_CACHE_GUARD_BIND_COMPLETE；binding可为ALL20_REUSABLE或WITH_TYPED_NONREUSABLE_JOBS。每worker完整query/input/MSA/modelseed/sourceAST/weights/runtime/referencegeometry exact。仅external map绑定新plan，旧worker/source/allocation原字节不变；不能转移旧分数或重计historical native GPU成本。global typed_incomplete不授权复用。

## 4. CommonV5软件58的真实CPU preflight

固定accepted ENTRY=$COMMON/common_review_successor.py，CPU=$COMMON/common_review_cpu.sbatch，GPU=$COMMON/common_review_gpu.sbatch；software路径 /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/common_successor_contracts_13269/acceptance.json。
sbatch --parsable --export=ALL,COMMON_SUCCESSOR_ENTRY="$ENTRY" "$CPU" preflight --software-acceptance "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/common_successor_contracts_13269/acceptance.json" --software-acceptance-sha256 ACTUAL_COMMON_SOFTWARE_SHA --preparation "$NEW_COMMON_PREPARATION_DIR/acceptance.json" --preparation-sha256 ACTUAL_PREPARATION_SHA --binding "$ACTUAL_BIND_RUN/acceptance.json" --binding-sha256 ACTUAL_BIND_SHA --out "$NEW_COMMON_PREFLIGHT_DIR"

必须 COMMON_SUCCESSOR_CPU_PREFLIGHT_ACCEPTED_ROOT_PENDING_ONLY_GPU_SUBMISSION_REQUIRED。source/library、collection/preparation/binding/20native74、六天然native单MSA sensitivity、uniform最低hash sensitivity、cache approved rawroot和pendingindices全部真实闭合。三Boltz seeds31011/12/13，五AF2 Multimerv3 models seed31021，ipSAE10/15与geometry4/8不改。
原core无intrinsic severe-clash资格门，V5输出全fixedslots独立 min heavy protein interchain distance/<1.5Å诊断，不能改 lockedscore/filter/rank或称实验结构资格。

## 5. root只提交exact pending common GPU array，globalcap2

若真实 root_pending_job_indices为空，不提交GPU。否则root先检查当前所有formal/E2E/common/technical-rerun的GPU lane，globalcap2不是array%2本身保证。E2E已terminal，formal必须ALL28terminal才能到此preflight。保持 CPU3/GPU1/mem64G/OMP4/A10040GB/3600sec与原models/settings。

sbatch --parsable --export=ALL,COMMON_SUCCESSOR_ENTRY="$ENTRY" --array=EXACT_COMMA_SEPARATED_PENDING_INDICES%2 "$GPU" "$NEW_COMMON_PREFLIGHT_DIR/preflight.json"

可有明确root已审dependency，其exactargv必须按accepted接口位置记录。提交只一次，每pendingindex唯一claim，不允许cacheindex或已有rawslot再跑。root立即保存readonly formal_common_root_submission.v1：actualarrayid/实际stdoutstderr/exactargv/entrylauncherreceipts/actualpreflight/indexlist/cap2；append新explicit GPUjournal版本，priorentries完全不变。不要猜未来costreceipt或读凭据。Allocated stagefailure即使没有worker/stage_result也保留positivecost，不自动换seed/rescue。

## 6. CommonGPU terminal后CPU finish：先cost，再raw/score/independent112

新array实际terminal后：
sbatch --parsable --dependency=afterany:ACTUAL_COMMON_ARRAY --export=ALL,COMMON_SUCCESSOR_ENTRY="$ENTRY" "$CPU" finish --preflight "$NEW_COMMON_PREFLIGHT_DIR/preflight.json" --preflight-sha256 ACTUAL_PREFLIGHT_SHA --submission "$ACTUAL_COMMON_ROOT_SUBMISSION_JSON" --submission-sha256 ACTUAL_SUBMISSION_SHA --out "$NEW_COMMON_RESULT_DIR"

如果pendingempty，省dependency/submission参数。finish先保存terminal numericreview_allocations，任何丢失worker/改变slot/source/start/hardware也不能抹成本。失败或缺model固定MODEL_UNRESOLVED，不作negativebiology。strict partial AF2 protocol阻断independent acceptance；保留112/null、physicalobservations与cost，technicalrepair须新identity，不能编辑worker伪PASS。

实际finish调用：
core13130.score → score.json；
core13130.verify_result → common_acceptance.json；
isolated scientific raw bytecopy + independent13223.audit_common → independent recomputed acceptance；
target_statistics_v2.statistics → target_statistics.json；
formal_contract_v2 exactfixed CLI → formal112_acceptance.json。

终局 status FORMAL_COMMON_RAW_CONTENT_INDEPENDENT_AND112_ACCEPTED_COMPUTATIONAL_ONLY。
formal112 status INDEPENDENT_FORMAL112_FAIRNESS_AND_STATISTICS_AUDIT_PASS。
必须112cohort-engine固定row/56targetrow/6primary+1BBFdiagnostic，两个replicate candidate模型全requiredmedian→candidateallmedian→replicate均值；empty/missing为NULL，不能0impute/丢target。全6paired齐才macro，不能强制significance/优越。
检查qualified vs source-unqualified coordinate observations、native14primary/all74 context、Boltz/AF2一致性与置信差异。实际structured gate审完才是common112内容资格；不是实验binding/blockade。

## 7. 当前root完整GPU universe/terminal cost76：seal-ledger与audit均为CPU

Cost软件13277已有76PASS，不再跑contracts。ENTRY=$COST/root_gpu_cost_audit.py。
新common提交应append在实际journal004之后，preserveformal/design/evaluate三oldentry、13315顶层amendment资格与originalentries。使用最后显式final journalpath，不扫描latest。
sbatch --parsable --export=ALL,ROOT_GPU_COST_ENTRY="$COST/root_gpu_cost_audit.py" "$COST/root_gpu_cost_cpu.sbatch" seal-ledger --software-acceptance "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/root_gpu_cost_contracts_13277/acceptance.json" --software-sha256 ACTUAL_COST_SOFTWARE_SHA --journal "$FINAL_EXPLICIT_JOURNAL_PATH" --common-preflight "$NEW_COMMON_PREFLIGHT_DIR/preflight.json" --physical-preflight "/lustre/users/u21111210118/projects/test9/steps/25_reference_free_e2e/runs/physical_preflight_13294/acceptance.json" --scope-end-utc ACTUAL_TERMINAL_SCOPE_END_UTC --e2e-disposition attempted

必须 ROOT_GPU_SUBMISSION_JOURNAL_LEDGER_CPU_SEALED，只封实际journal/controller完整前驱，不是costaccepted。
sbatch --parsable --export=ALL,ROOT_GPU_COST_ENTRY="$COST/root_gpu_cost_audit.py" "$COST/root_gpu_cost_cpu.sbatch" audit --software-acceptance "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/root_gpu_cost_contracts_13277/acceptance.json" --software-sha256 ACTUAL_COST_SOFTWARE_SHA --ledger "$ACTUAL_SEALED_LEDGER_PATH" --ledger-sha256 ACTUAL_LEDGER_SHA

必须 ROOT_CURRENT_GPU_SUBMISSION_UNIVERSE_AND_TERMINAL_COST_CPU_ACCEPTED，complete_root_gpu_submission_universe/allocated_failure_before_manifest_cost_retained、root_gpu_submission_receipts、terminal_numeric_accounting_receipts。
查询boundeduser/time/name+所有显式slot independentlyjoin，rawid一次/steps排除、StartEndintervalcap2、CPU3GPU1/memorymissingUNAVAILABLE_NOT_ZERO、所有allocatedfailed/timeout成本positive保留。Historicalnative20/74不重计。Scope开始2026-10-11T14:25:00Z，不声称全历史projectcost。
完整controller13315独立内容由Composer显式核验，cost只hashjournal004不能代替其Only-addition资格。

## 8. default integration84与最终报告54

Corrected Integration84实际softwareaccepted后，root在ALL28terminal fence与所有current prerequisites满足时使用：
sbatch "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/default_workflow_materialized_integration_v3_fixturefix1/default_integration_cpu_v3.sbatch" apply "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_source_materialized_software_13322/acceptance.json" "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/default_materialized_integration_root_request_v3/request.json" "$ACTUAL_CORRECTED_INTEGRATION84_ACCEPTANCE_PATH"
schema.v2 threepaths、actualDerived13306newpipeline、Physical13294helper、materializedRFDfull226 adopted，originalcommon及core/Boltz unchanged；actualbefore/postruntime+samegeneric7/physical42/selector15，oldpipeline+oldRFDreadonlyarchive/rollback/concurrentbyte guards全部严格。实际status DEFAULT_GENERIC_PHYSICAL_GATE_AND_MATERIALIZED_RUNTIME_INTEGRATION_CPU_VERIFIED_NOT_PUBLISHED后才算默认workflow修复。Source/publication仍独立。

报告工具54软件13282已接受。root readonlyrequest schema final-scientific-report-request.v1绑定actualsoftware/common_successor/currentrootcost与COMPUTATIONAL_ONLY/experimental_binding_or_blockadefalse。仅使用真实common112/native/physical/cost图：
sbatch --parsable --export=ALL,FINAL_SCIENTIFIC_REPORT_ENTRY="$REPORT/final_scientific_report.py" "$REPORT/final_scientific_report_cpu.sbatch" build --request "$ACTUAL_REPORT_REQUEST_PATH" --request-sha256 ACTUAL_REQUEST_SHA
后另一个CPU job：
sbatch --parsable --export=ALL,FINAL_SCIENTIFIC_REPORT_ENTRY="$REPORT/final_scientific_report.py" "$REPORT/final_scientific_report_cpu.sbatch" qa --manifest "$ACTUAL_BUILD_DIR/report_manifest.json" --manifest-sha256 ACTUAL_MANIFEST_SHA

必须 FORMAL13260_FINAL_CHINESE_REPORT_AND_MATRIX_CPU_ACCEPTED，绑定report/common_successor/statistics/root_gpu_cost/112/6/COMPUTATIONAL_ONLY。REPORT_ZH/matrix112/structure_inventory/native14/actual_allocations inputs+allcurrentbytes+rerunfrozenstats deterministic重建通过，不能用build exit0或软件54替代QA。诚实报告negative/NULL/underfill/failedgeneration、BBF跨家族局限、E2Eaccepted0，无forestplots/强制优越/实验结论。

## 9. Finalsource root explicit九roles+完整lateprovenance

实际correctedLIB6/53，Integration4/84，Mapper14/201与Composercorrected8/66接入finalsource plan schema final-source-closure-plan.v3；root_owned true/formal13260/public_source_only/no_settings_change/root_integration_review明确。
九roles必须一一出现，每个gate真实status+receipt，每个sources非空且exactrepository_relative，每个seeds完整source/freeze/test/launcher/doc/proof/submit/accounting：
formal13260_terminal_v3；
native74_cache_catalog；
native74_cache_binding；
reference_free_e2e；
formal_common_review；
independent_statistics（actualformal112acceptance）；
scientific_report（actualQA）；
final_delivery_tools（actualcorrectedComposer软件66，无archive-cycle）；
default_workflow_integration（actual3path/default installed）。

base接受Source13316exactreceipt；fourmaps/3aliasartifacts/8ID12fields/588members完全保留。context parent seeds必须acceptedmapper17 exactrawparents，包括generatedclosure16；不知道的parent/path不能泛alias。实际integrationarchives路由oldpipeline/RFDhistory，只接受exactoldbytes，新defaultdest不冲突。禁止SourceV10旧defaultstaging再次覆盖currentnewdefault。

Adapterrequest schema final-source-materialized-context-read-view-request.v3，绑定actualLIB53、Mapper13319、final_source_plan，raw_JSON_rewrite_allowed/genericrelative/genericexternal全false。rootCPU audit：
sbatch "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/final_source_closure_v3_fixturefix1/final_source_cpu.sbatch" audit "$ACTUAL_FINAL_SOURCE_ADAPTER_REQUEST_PATH"
必须内 FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED 及外 FINAL_CURRENT_SOURCE_MATERIALIZED_FIVE_PARENT_CONTEXT_AND_DERIVED_V2_CPU_ACCEPTED_NOT_STAGED_NOT_PUBLISHED；实际newscope包含allowned/executed/dependent源码。

新late元数据必须加入 final_delivery_tools/history exactseeds与最终privatepackage，不靠此文presencePASS：
/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/handoffs/final_source_late_receipt_guide_20261012.md
/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/consumer_v4_v3_v3_metadata_readonly_seal/receipt.json
exact_context_mapper_v4_primary_claim/request.json与submit_receipt.json；
final_source_closure_v3_software_primary_claim/submit_receipt.json；
consumer13319_13320_cpu_backfill_timelimits/receipt.json；
原LIB13320 contracts/log/typed_incomplete/frozen6/submit与correctedLIB13322actual6/53/submit；
原Composer13321及13323 contracts/log/typedfailure/frozen8/submit与correctedactual8/66/submit；
原Integration13324 failurecontracts/log/frozen4/submit与correctedIntegration13325 actual4/84/submit；
source_e2e_descriptor_capture_primary_claim/submit_receipt.json（13317failed）；
source_e2e_descriptor_capture_retry_after13317_RO_fix/submit_receipt.json（13318accepted）；
sourcecapture2/failure13317logs/noresultmanifest事实、13318descriptor_capture.json及final13312_actual_metadata_readonly_seal/receipt.json；
controller13315实际3901资格/amendment1796/oldarchive3343/newcontroller3626/source2/actualCPUproof/journals003+004；
所有source13262/13263/13279/13293/13297/13305/13307、13303、13286/87等原失败source/accounting、13267zeroCPU取消；后续rootmetadata-onlyseal/CPUbackfill/technicalrerunreceipts。
每项fullpath以root已声明metadata为准，新source资格只在CPU生成；本文无未来hash填造。

## 10. source staging/cleancommit/privatebundle/GitHub readback，再Composer+isolatedrestore

Actualsource audit通过后root使用acceptedlibrary stage exact新auditedentries，原absent-only/differing-file拒绝不放松。Actualthreepath已由integration安装，stage不得代替事务。stage函数CLI：
ACTUAL_ACCEPTED_LIBRARY_ENTRY stage --audit ACTUAL_AUDITED_FINAL_SOURCE_ACCEPTANCE_PATH --audit-sha256 ACTUAL_SHA --out NEW_STAGE_DIR
在root-owned pureCPU job内调用；只能使用qualified exactentry，不能直接login执行。

root复核publicsource范围/READMEfixedprotocol+evidenceboundaries、排除licensedwheels/weights/privatecredential，然后正常git add/commit。保留originalbranch/localhistory，生成并CPUverify private source.bundle。禁止reset --hard/forcepush/丢历史。实际repo ethanyangAI/ppi-cldm、baseline e2984a94674ffcb75b280680038df5e9f39d684d。

现有Composer.compose实际要求source_release.github.published_ref和api_responses并 independently验证actualpublictree。故GitHub draftbranch/tree readback在compose之前是现有接口依赖；正式project ACTIVE仍最后。root可正常push或用已qualified github_source_export.py精确blob/tree/commit connectorfallback，所有export/hash/verify在CPU：
github_source_export.py --repo "$R/source" --baseline e2984a94674ffcb75b280680038df5e9f39d684d --expected-head ACTUAL_FINAL_COMMIT --repository ethanyangAI/ppi-cldm --output-dir NEW_EXPORT_DIR
github_export_verify.py --repo "$R/source" --export-dir ACTUAL_EXPORT_DIR --output NEW_VERIFY_JSON
APIreturnedSHAs逐一匹配expectedtree，再CPUreadback --api-responses ACTUAL_RESPONSE_JSON --published-ref ACTUAL_FETCHED_REF，clean committed tree/sourceinclusion/privatebundle全部一致；new connectorcommit如与localSHA不同，解释exacttree等价且privatehistorybundle保留。创建任何PR后root必须attach_artifact。

CorrectedComposer66software实际接受后，用其 exact frozen ENTRY/CPUlauncher及source/lib11/mapper14执行绑定，显式rootinventoryrequest限定全部terminaldirs/terminalgate/root_binding，不从latest猜范围。inventoryCLI：
ACTUAL_COMPOSER_ENTRY inventory --request ROOT_INVENTORY_REQUEST --request-sha256 ACTUAL_SHA --software ACTUAL_COMPOSER_SOFTWARE_ACCEPTANCE --software-sha256 ACTUAL_SHA --out NEW_INVENTORY_DIR
composeCLI：
ACTUAL_COMPOSER_ENTRY compose --request ROOT_COMPOSE_REQUEST --request-sha256 ACTUAL_SHA --software ACTUAL_COMPOSER_SOFTWARE_ACCEPTANCE --software-sha256 ACTUAL_SHA --out NEW_COMPOSE_DIR
均通过acceptedpureCPUlauncher FINAL_COMPOSER_ENTRY调用。

Compose要实际common112/innerraw/independent/112stats/cost/reportQA/sourceinclusion+newdefault/cleancommit/GitHubparity、historicalpolicy2、full allfiles universe 与licensedconditionaldeps分离。Controller amendment binding=actual13315qualification+actualjournal004descriptor，independentfreshterminal13315/13309、Only design_audit_acceptance addition/source2/oldnewbytes/unchangedGPUuniverse，不只pointerhash。
原JSONrawbytes不改；17parentview先于traverse/dedup，allsource/provenance fullscope及588tar/full5TXT+JSON明确packaged。

compose status FINAL_DELIVERY_CONFIG_AND_UNIVERSE_CPU_VALIDATED_ARCHIVE_RESTORE_PUBLICATION_PENDING不是fullarchive。
用同acceptedComposer relative_archive_restore.py wrapper的actualpureCPU：
relative_archive_restore.py package --validation ACTUAL_COMPOSE/delivery_validation.json --validation-sha256 ACTUAL_SHA --out NEW_PACKAGE_DIR --part-mib 512
先用相同 Composer实际依赖绑定的 unchanged delivery_core_v2.py extract --package ACTUAL_PACKAGE/packaging_receipt.json --restore-root NEW_ISOLATED_RESTORE_ROOT，在 pureCPU 独立目录安全提取并产生 RESTORE_HASH_ACCEPTANCE.json；未提取/未hashverified的空目录不能直接调用restore。
relative_archive_restore.py restore --package ACTUAL_PACKAGE/packaging_receipt.json --package-sha256 ACTUAL_SHA --restore-root NEW_ISOLATED_RESTORE_ROOT --out NEW_ISOLATED_RESTORE_ROOT/NEW_RECOMPUTATION_SUBDIR
restore要求root已经存在、out新建且严格位于该restoredtree内；package和extract都读取实际packaging_receipt而非尚未生成的猜测result。

实际wrapper先核完整上下文/source/currentbytes，再调用unchangedfrozen core.package/restore.run；restore authority仅explicitrestoredindex/acceptedaliases，无liverawfallback；完整588tarbytes/5recoveryfiles/8sourcecopies/provenanceinputs/17rawparents/oldJSON+newscalarproof/allsource14/metadataamendment图、fixedbudget/native/rawcommon/112stats独立重算。只同Lustre隔离restore不是offsite或offlineGPUimage；licensedsoftware/weights是explicitdependency。
任何missing/different/unavailable/scheduler/resource/contentfailure保存typedunresolved，先修新identity不能自动publish。Final scientificoutcome可以accepted0/null，并不要求positiveblocker。

## 11. 最后root发布/原子ACTIVE

仅actualallgates/sourcepublictree/完整package+isolatedrestore内容接受后，root写新的phase/report/manifest和可追溯source/code/licensedparameter/dependency pointers，按现有immutable publish API用config+restore receipt校验后原子更新 /lustre/users/u21111210118/projects/test9/00_admin/ACTIVE.json。保持旧ACTIVE/phase/manifests/sourcebundles/archive可追溯。最终README/中文审计报告链接权威位置与benchmark矩阵；PR attach/readback都已真实完成。然后root关闭/更新heartbeat为complete。

不能用E2E工程成功、软件fixtures、源图PASS、GPU退出0、部分native恢复或部分formal组推断overall完成。交付说明必须区分技术闭合/计算证据/阴性或不可估计/实验缺口，诚实回答workflow是否达到给任意两蛋白推断pose再生成blocker的目标及目前覆盖边界。
