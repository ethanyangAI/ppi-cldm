# 两蛋白到定向 blocker：用户入口能力静态审计

日期：2026-10-12。证据层级：COMPUTATIONAL_ONLY / STATIC_SOURCE_READBACK。审阅者未执行哈希、测试、科学计算、Slurm 提交或模型推断，未读取 formal13260 候选及结果。本报告是独立人类审计说明，不修改旧 DRAFT、默认代码或数据。

当前代码具有完整的“身份解析 → 实验复合物获取或 Boltz-2 pose 推断 → 原生界面定向 RFdiffusion+ProteinMPNN → 无复合物模板的复折叠与竞争几何复核”编排。它支持有身份与构件约束的可溶性两蛋白体系；不能解释为任意输入两蛋白都存在互作，或任意 pose 都能产生有效 blocker。

默认 CLI、正式 benchmark 控制器、prepared PhysicalV3 是不同执行身份。PhysicalV3 的源码静态审查通过不表示实际 CPU 资格、默认安装或新模型结果已完成。最终科学结论须消费正式共同复核、统计、完整提交成本与独立报告 QA 的实际接受凭据；不能依据本报告或软件测试 PASS 宣称优越性。

## 逐环节能力与限制

| 环节 | 代码中实际存在的行为 | 必要拒判或未闭合范围 | 主要源码证据 |
| --- | --- | --- | --- |
| 两蛋白输入 | 恰好两个有顺序的对象：A 为被设计 binder 靶向的目标，B 为原生伙伴。支持 UniProt、精确 gene+taxon，或单条标准氨基酸序列；支持显式残基范围。 | 裸基因名、多个 FASTA、模糊氨基酸、冲突身份、错误物种及过短构件拒绝。用户须明确方向；不会自动双向设计。 | source/src/ppiblocker/pipeline.py:16–53；identity.py:62–115 |
| 实验结构搜索 | 对两个 UniProt accession 搜索 RCSB experimental entry，再下载 biological assembly，检查物种、entity accession、序列/构件和真实接触。保留获取与拒判记录。 | sequence-only 不会自动按序列反查 PDB；需显式结构或预测。最多搜索20条，第一份合格接触装配被采用；不保证全库最优或不存在别的结构。 | identity.py:117–137；pipeline.py:62–139 |
| 已知或本地结构 | 可指定 PDB/assembly/chains；本地结构需 provenance 且 experimental=true。规范化为 A/B 并保留原装配。 | 本地来源由调用者提供，不是自动实验来源核验。明确指定的 PDB 不合格时返回拒判，不悄悄切换。精确构件缺失、变异或截短不能靠相似序列替代；需显式构件决定。 | pipeline.py:98–138；structure.py:72–111 |
| 没有合格复合物 | 未找到合格结构时返回 NEEDS_PREDICTION；predict_only 明确禁止复合物模板和接触约束。CLI run 在需要时调用 predict。 | 网络/检索错误是不可用，不能当作“无结构”。身份或上下文不足不会用预测结果补成生物学证明。 | pipeline.py:29–35、91–96、139–140、318–323；identity.py:128–131 |
| 原生互作 pose 推断 | 默认为 Boltz-2，至少3个样本；要求精确 A/B 序列、pair-specific ipTM、界面 PAE/pLDDT、接触及目标对齐后的伙伴 pose 一致性。至少2且≥60%全部模型支持。 | 固定 backend，没有通用 docking/AF2 native-pose 替代选择。任一样本读取/结构评估错误使 PREDICTION_INCOMPLETE；不接触或不收敛为 POSE_REJECTED。分数不是互作概率。 | pipeline.py:144–209；backends.py:28–104 |
| 原生 pose 的物理门槛 | 当前默认 evaluate 已检查 target–binder 最小重原子距离<1.5Å；prepared PhysicalV3 将同一门槛前移至 native prediction 和 design 入口。 | 当前 default predict/validate_design_pose 尚无这道前移门槛；必须完成真实 PhysicalV3 资格与后续明确默认集成，不能把 prepared 版本当作已安装。 | pipeline.py:175–208、211–227、289；steps/25_reference_free_e2e/pending/physical_gate_v3/patch_pipeline.py:10–49；pose_physical_gate.py:6–32 |
| 生物学与装配上下文 | 所有设计器入口要求 native_interaction_supported、非空 interaction_evidence、soluble_construct、no_required_unmodelled_context；不允许丢弃额外链或非蛋白组分。 | 这些是显式人工审核字段，不是自动文献/原生互作真实性检验。膜、必需糖链/辅因子、多亚基体系等需另行受审扩展。prepare 的 POSE_ACCEPTED 仅表示观察到界面，仍可能在 design 被上下文拒绝。 | pipeline.py:211–226；structure.py:11–38 |
| RFdiffusion 定向生成 | 从原生界面接触中取几何锚点；固定目标 A，生成30–200 aa binder；检查目标序列和连续 CA 骨架。 | 默认前三个接触密集残基是几何锚点，不是实测能量 hotspot。目标骨架缺口拒绝；不会自动修补缺口、选择结构域或处理膜/糖链。 | backends.py:106–148 |
| ProteinMPNN | 只设计 B 链，保留目标序列；记录 backbone、FASTA、序列、锚点及来源。 | 输出状态是 DESIGNS_GENERATED / unvalidated_sequences；MPNN 评分与成功运行不证明结合、阻断或稳定表达。 | backends.py:149–166；pipeline.py:229–242 |
| 设计后复核 | 目标加新 binder 的 Boltz-2 无复合物模板复折叠；分别记录置信度、真实预测界面物理碰撞、binder pose 恢复、目标变形、原生界面覆盖及原伙伴空间不相容。 | ≥60%且至少2个通过样本才给 COMPUTATIONAL_COMPETITION_CANDIDATE；任何评估错误使整体 EVALUATION_INCOMPLETE。这些是空间竞争假说，不是实测 blockade。 | pipeline.py:250–315；structure.py:144–174 |
| AF2 正交复核 | 独立 AF2/ColabFold 和共同复核源码存在，分别保留模型、MSA、配置、几何及置信度证据；正式共同复核有固定 protocol 与全模型分母。 | 通用 ppiblocker CLI 的 evaluate/run 没有自动 AF2 分支。不能把 README 中历史5模型×3seed协议、通用 Boltz 流程与本轮固定共同复核协议当成一个已经执行的通用入口。 | cli.py:5、11–18；pipeline.py:275；rebuild/benchmark_common_review.py:17、271–284、403–449；src/ppiblocker/af2_review.py:1–39 |
| 跨方法 benchmark | 方法 interchange 导出 BindCraft/BoltzGen 配置并能导入有来源的候选池；本轮同靶标同预算执行与共同复核由独立 root 控制器管理。 | 输入导出明确是 INPUTS_EXPORTED_NOT_EXECUTED；BindCraft accepted-design stopping criterion 不等同 RF raw-candidate budget。默认 CLI 无 BindCraft 一键生成分支。未完成实际全分母共同复核前不能宣称 workflow 优越。 | benchmark_adapters.py:9–38、41–75；cli.py:11–18 |
| 操作与审计 | 每一步使用显式上游 manifest、文件身份和独立 run；reevaluate 仅重算已验证旧结果，保留原推断来源。 | 当前 submit_public.sh/docs 仍列 CPU2 / GPU4CPU 的通用 wrapper，不等同本轮 sharedCPU3/GPU1/64G/OMP4、真实 UUID ownership、root统一 journal/cost 机制；不能用旧 wrapper 绕过本轮单一提交权。 | scripts/submit_public.sh:4–28；docs/WORKFLOW.md:23–37；pipeline.py:245–263 |

## 本次科学闭环必须完成的内容

1. 对 prepared PhysicalV3 进行实际纯 CPU 软件、原始三模型物理重算、完整缓存 runtime 和来源资格验证；诚实的 POSE_REJECTED 是终态，不能强行生成或换模型0。
2. 用实际合格 staged pipeline/helper 加原始 common.py 构造不同的 default Python 身份。后续显式三路径事务只推广 pipeline.py、pose_physical_gate.py 和 reviewed materialized RFD lock；归档旧 pipeline/旧锁。staged 硬编码 selector 不安装到 default。
3. 当前已观察的旧 RFD 锁与新增派生缓存差异须通过已审方法独立资格和显式 adoption 闭合；此前实际13263 FAILED 不可升级为接受，也不能自动刷新锁。
4. 根据实际13290诊断，完成 distinct sourcebaseV6 的受审源码闭包及 mapperV2：只有 exact4665-byte recovered_three_candidates.json 的预先标明未恢复 marker 和9个 native/backbone/design_manifest 字段能转成非操作性历史注释；canonical=null、not byte accepted，原 JSON 字节不改、不声称恢复结构。未知父/字段/身份、当前操作边或原始数据不可借此绕过验收。source-only readiness 不能替代 archive/restore 和当前数据闭包。
5. 正式28-task benchmark 的实际输出、固定112 cohort–engine 分母、全部6 primary targets 的统计、全部 root GPU 提交和分配成本、最终报告/matrix/结构来源 QA 均需实际凭据。全6不可估计或缺失时保留 null，不截取有利子集。
6. 默认文档应在实际集成后清楚标识通用入口、正式 benchmark、独立 AF2 review 与工程 E2E 的协议/提交机制差异；无需把实现细节塞进科学结论。

上述条目是当前闭环要求，不表示已得到任何新的 binder 或 benchmark 科学结果。软件资格、源码资格、执行完成、计算候选、实验结合及功能阻断是不同证据层级。


实际13290 的父字段诊断明确：旧三条 KEAP1 development 记录仅恢复精确序列，标记为 EXACT_SEQUENCE_FROM_HISTORICAL_OUTPUT_STRUCTURES_NOT_RECOVERED，missing_files 已列出 native/backbone/design_manifest。九个结构/manifest 描述是既有历史来源注释，不是当前已恢复输入。V5 的通用恢复尝试保留为只读未执行历史；V6/mapperV2 的有限视图尚待独立静审及实际 CPU 接受。纠正注释分类不能扩展为缺失当前输入的豁免。

## 仍属于受审扩展或实验验证的范围

完全未知任意蛋白对的相互作用真实性、无身份序列的自动全库结构检索、膜/糖基化/辅因子/多亚基建模、allosteric blockade、小分子阻断、未知家族的自动可靠门槛、off-target selectivity、表达/溶解性/稳定性、实测亲和力、功能竞争及安全性，没有被当前通用流程自动证明。拒判或无法估计不能解释为没有生物学作用；计算竞争候选也不能解释为功能 blocker。

建议最终用户交付措辞：**“给定两个身份与构件明确、具有受审原生互作证据的蛋白，获取合格实验复合物或推断并拒判不可靠 pose，在支持的两蛋白可溶体系上产生界面定向蛋白 binder，并给出独立计算复核与完整失败/成本记录。”** 更宽范围应以新增受审任务及实际验证单独交付。
