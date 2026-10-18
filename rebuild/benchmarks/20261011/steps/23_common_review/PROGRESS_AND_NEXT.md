# Step 23 进度与下一步（2026-10-11）

当前已验收的是技术修复、原生 Boltz 3-model pilot、BBF 5-model pilot 和两条完整 CPU 验收入口。全量 native74、BBF110 和正式两法 benchmark 尚未完成内容验收；不能把准备完毕、任务退出或 pilot 成功写成全量科学结果。所有旧78控制均为 development，R1连续主报，operational_pass=null，无实验结合/阻断概率。

项目根目录：`/lustre/users/u21111210118/projects/test9`（下文 R）。
root 控制 GPU 提交和全局并发上限2；本 agent 未提交 GPU，也未改旧 frozen13051、旧模型、旧worker.json、旧live common或 ACTIVE。

|当前对象|权威入口 / receipt|已验收内容|
|---|---|---|
|未来候选共同复核 core v2|R/steps/23_common_review/frozen/common_core_v2_13130/code/benchmark_common_review_v2.py|62153B，SHA7d72314e0409fa1fb2a6ed86f593b198cf3e5c99f747c58d8cfa7d1fd0404d17；独立源码快照，不指向 mutable live source|
|v2 源码包|R/steps/23_common_review/frozen/common_core_v2_13130/source_bundle.json|SHA7743873fb5ec089c1edb14670823dc76c6f614dae9dec4baba19ca805cc7b804|
|core v2 CPU 验收|R/steps/23_common_review/runs/common_core_v2_validation_13130/acceptance.json|SHA442f6ffa91ea4bca7497ea429820a9c02e208c868453a114d19541b4e49f0bc5；14既有+3新合同、实际 prepare / score / verify 通过|
|原生 index19 技术修复|R/steps/23_common_review/runs/allocation_v2_13106/native_index19/native19_gpu.sbatch|SHA94294855970cc78df20a2747d0f4c13f4b1cb85c29240cce90a2311e4921b593；同 science / job_signature，新 raw root|
|index19 allocation wrapper|R/steps/23_common_review/runs/allocation_v2_13106/code/common_allocation_v2.py|3330B，SHAedfa4f2d99fa16df4db504612a185352adf3315d4ced061ba281abc75ca122fa；12合同，通过 rawID+arrayalias 选唯一行，保留 full raw，允许 RunTime 改变但拒绝 allocation identity / TRES 改变|
|BBF剩余21 GPU唯一入口|R/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/bbf_gpu_remaining.sbatch|1899B，SHA0bd097ddbf4ea7b7f9d7bf8d0cfff0003887f0ff70ce81b870bd90f6f0d1db40；array1-21%1，v4guard，删除旧 whole-text common 预检查|
|全量CPU下游登记|R/steps/23_common_review/runs/downstream_frozen_13119/readiness.json|SHA dc8976ea0795cbc4fab936e8e1cfe2a72d8c66c73f3a3bd76d0f23b4114588a0；真实 native3/BBF5 全链 readiness，8新合同+14/5既有测试通过|

core v2 修复两类技术问题：唯一 invoking Slurm 记录选择，以及 score 中 runtime_locks 循环变量覆盖 plan receipt。SETTINGS 完全相同；job_signature、units、geometry、one_score、blind_entities、a3m_rows、assert_mapping、seqcheck、transform_fit、find_raw 的 AST 未改变。实际重建20原生 jobs 的全部 job_signature 与13051相同，真实 pilot 科学分数逐字段相同。prepare/worker 必须在源码包中执行，且 plan.source 必须绑定实际 immutable v2 文件；未冻结 live source/rebuild 的 prepare/worker 会拒绝。

root 已提交的任务与输出：

|任务|状态角色 / 固定分母|输出 / 后继|
|---|---|---|
|native旧数组13059|原生0–18，旧19已 pending、0-cost取消并记录技术原因；原始科学 source13051 保留|R/steps/23_common_review/runs/native_controls_frozen_13051/raw|
|native修正GPU13107_19|afterany13059，承接原生GPU槽；只运行19，不重复0–18|R/steps/23_common_review/runs/allocation_v2_13106/native_index19/raw|
|BBF GPU13114|唯一 remaining1–21，使用13103入口；与已验收旧index0共22jobs/110models|R/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw|
|native CPU13124|afterany13107；固定20jobs/74models|R/steps/23_common_review/runs/downstream_frozen_13119/native74_review_13124|
|BBF CPU13125|afterany13114；固定22jobs/110models|R/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125|

上述 GPU/CPU 已提交；不要重复 submit，不启用未使用的13106 BBF alternative root。全量任务的 completed / failed 与内容验收由 root 继续监控。

native CPU入口：
`R/steps/23_common_review/runs/downstream_frozen_13119/native74_review_cpu.sbatch`
1439B，SHA bbfecf089a61fdf222305d7fa98c909b5a05a1b4f10b1a24a5c24a47ba36dc04。
helper 同目录 code/native_review_pipeline_v2.py，17474B，SHA56648b7f905abfc393526fcba04dcd5e7ecc9cb4437db796b3b58047292b77fa。
它将两原始root中的全部 regular raw 文件真实 bytecopy，记录 original / copy receipts，不用 symlink、不改原worker字节；原source13051 score→独立实际GPU归属/full query/units audit→verify→resource_closure。原 engine score 保存为 score_engine_original.json；只纠正 plan receipt 的 canonical score 与 score_metadata_repair.json 绑定，所有其它字段/分数相同。resource_closure.json 给出科学证据的 original→hash-identical copy 映射，evidence_resources/ 包含所需源码、输入、几何参考等；engineweights/env 单列 recompute dependencies，不宣称离线GPU重推已保证。

BBF CPU入口：
`R/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_cpu.sbatch`
1219B，SHA cb55b9b68ae7255d6f60b8697c889eb4a875f21fa571ebd7cbe3e6b83e98e043。
helper 同目录 code/audit_bbf_workers_v2.py，9831B，SHA5d56d2a91a1acf0215283aca78180c37398f71d8bcf3f45add02d83d8b0cdde5。
它只合并旧13067 index0和 chosen13103 remaining root，拒绝重复worker；核验实际 allocation rawID、minor→UUID→NVML、source/feature/reference receipts、Slurm Command、full query、pLDDT / PAE units、固定5slots，再用 frozen13061 collect→R0/R1 score→verify。110 分母保留；missing / no-interface 不填零，失败不可写成生物阴性。

源码审计必须纳入的模块和依赖：

- R/source/rebuild/benchmark_common_review_v2.py 与 frozen/common_core_v2_13130 全源码包；old live benchmark_common_review.py 仍是历史原字节，最终 public CLI / future candidate SOURCE 以 corrected v2 为准。
- R/steps/23_common_review/code/build_common_core_v2.py、code/freeze_downstream_v2.py；runs/common_core_v2_validation_13130 与 runs/downstream_frozen_13119 的 acceptance/readiness。
- R/steps/23_common_review/runs/allocation_v2_13106/code/common_allocation_v2.py 及 wrapper_receipts.json；code/freeze_review_technical_v2_1.py。
- R/steps/23_common_review/runs/downstream_frozen_13119/code/native_review_pipeline_v2.py、code/audit_bbf_workers_v2.py；两CPU launcher。
- R/steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py（84446B，SHA b37227bd862ee1425a59f5308be1ee3f4824042dea5d71c1269ad0f406b318f9）及 snapshot_manifest / 74合同receipt；这是实际 GPU ownership guard 依赖。
- R/steps/21_method_runtime/frozen/bbf_backend_v2/bbf_feature_backend.py（15084B，SHAea568fb4fa1905d54c304a60d7f6b78af4a01a80941d5cf0c0152c1254d361b3）及 bindcraft_env.sh、CPU13057 literal110 features。
- R/steps/23_common_review/frozen/native_common_13051 与 native_controls_frozen_13051 inference/analysis/membership；这是现有 native evidence 的原科学source，不能被 v2 覆写或伪装成 v2 worker。
- R/steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061 plan/sourcebundle/features/feature_acceptance，以及旧13067 index0worker和 worker_validation_13096/acceptance。
- 原生全量产出的 assembly / raw_audit / 原score与metadata修复 / canonical score / score_acceptance / resource_closure 和所有 hash-identical copies，delivery resolver 必须采用完整资源映射，不能只收 summary 或 symlink。

技术历史角色：13103 native wrapper 因双 scontrol 全文 RunTime 比较问题未用于GPU；13105是过渡 freeze，不是权威；13106为实际 native19技术入口。13116 downstream v1在发现 score plan receipt bug 时失败，保持历史；13119为已实际跑通并已提交依赖的CPU下游入口。13130 rebased_native_plan 仅用于验证新source绑定，不重推旧native；未来正式candidate应由root使用 corrected v2 再准备其自己的新 plan。

下一步由 root 确认13124/13125终态和顶层acceptance，再审读各目标/引擎结构恢复、R1连续分布、typed missing及BBF成对输入差异；原生恢复失败会限制相应靶标的解释。正式两法候选的共同复核使用 corrected v2 冻结plan/SOURCE，随后进行独立评分、预定统计和完整 delivery/restore 验收。现有pilot或开发诊断都不证明workflow普适优越或实验blockade。
