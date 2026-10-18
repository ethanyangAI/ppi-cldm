# 同靶标、同预算计算 benchmark：执行协议草案
修订日期：2026-10-11。状态：七靶标输入、74 个原生对照复核模型与 RF 工程流程已验收；BindCraft 首个轨迹被官方筛选拒绝，正在单独验证后续阶段；28 个正式任务尚未冻结。本文为执行协议及阶段进度，不是正式比较结果报告。

权威计算目录：/lustre/users/u21111210118/projects/test9。所有新计算、安装、下载、评分和验证均在 Slurm 作业中执行。本地仅保留人类可读报告。已获授权临时使用 organ 的 CPU 核执行准备和诊断，CPU 作业不申请 GPU。

## 科学问题和解释范围
在相同靶标结构、预定互作表位、65 aa 设计长度、物理 GPU 型号和计时预算下，比较 RFdiffusion + 原版 ProteinMPNN + 原生 AF2 复核与官方 BindCraft 完整原生流程。统计单位是靶标；重复种子不增加生物学样本量。交付允许得到不支持优越性的结果。

当前 78 个历史对照全部属于方法开发资料。新比较不是把这些对照重新包装成独立验证。共同复核的结构置信度、pose 恢复、参考界面覆盖及空间遮挡分别报告；它们不等同于实验结合、KD、PPI 阻断或临床疗效。

## 输入矩阵
| 角色 | 靶标与解析复合物 | 明确构建体 / 状态 | 靶标长度 | 覆盖的主要类型 |
|---|---|---|---:|---|
| 主比较 | 人 MDM2，1YCR A/B | 连续观测核心；末端未观测部分不设计 | 85 | 短螺旋肽结合槽 |
| 主比较 | 人 KEAP1，2FLU X/P | Kelch 核心与 NRF2 肽；去掉末端标签区 | 285 | β-propeller 与酸性线性 motif |
| 主比较 | 人 EGFR，1IVO A/C | DIII，作者编号 310–481；不代表完整受体 | 172 | 胞外受体与蛋白配体界面 |
| 主比较 | 人 BCL-xL，2M04 A/B | PUMA 复合物；固定 NMR model 1 | 174 | 螺旋蛋白与 BH3 肽结合槽 |
| 主比较 | 人野生型 H-Ras，4G0N A/B | GNP 状态实验坐标，protein-only 输入；不是 KRAS | 166 | 核苷酸依赖的效应蛋白界面 |
| 主比较 | 小鼠 c-Crk，1CKA A/B | SH3 核心，与 C3G 肽 | 57 | 浅表面、富脯氨酸 motif |
| 独立诊断 | 合成 BBF111，9HAG 与 9HAC | 非天然 PPI；b4 原生对照保留作者 140 aa 完整 query | 111 | 合成折叠与跨家族失效诊断 |

所有输入均已核验 RCSB / UniProt / 作者链身份、序列、链号、参考索引和三个热点。H-Ras 的 Y64/S65 为最小补建：固定随机种子，仅补建缺口重原子松弛，全部 1,283 个原有实验重原子位移为 0 Å；这两位不冒充实验观测坐标。EGFR 的糖基及完整受体环境未纳入两种设计方法，必须作为共同限制报告。

最终输入：steps/22_matched_benchmark/input_preparation/prepared_7_chainfix_13094/。该版本只修正 target=A / binder=B 的链元数据，坐标、query、热点与参考映射沿用 13010 的验收字节。独立 CPU 验收 13019：75 项递归 receipt 一致，7 个靶标的序列、编号、热点和参考映射通过；provenance_final7_13019.json SHA-256 为 4d6c339ffda336254cb445e12505ff7cfdabc159dc94c43961b6d522dbd2845e。

## 原生方法
RF 使用官方复合物模型、默认 50 步扩散，每个 backbone 生成 8 条原版 ProteinMPNN 序列，温度 0.0001；固定 target，仅设计 binder，长度 65。原生 AF2 使用 model_1_ptm、single MSA、3 次 recycle、target-only template，并从生成的完整 backbone 提供 initial guess。新设计 nongly 的 Cβ 由官方几何构造；gly 使用 Cα。binder 的 template atom / pseudo-beta 坐标及 mask 全部清零。这个 ColabDesign 实现按作者方法语义复现，不能称为原始 dl_binder_design 程序逐字执行。

RF 原生排序使用双方向 cross-block PAE 的平均值，单位 Å，越低越好。预定内部筛选为 binder pLDDT ≥ 0.80、平均 cross PAE ≤ 10 Å、按 target 对齐后的 binder Cα RMSD ≤ 1 Å；没有声称重现论文每个 campaign 的全部人工、Rosetta 或实验筛选。

BindCraft 使用固定官方 commit 7713aa0d0d351e4117a8befeb8541f3a8ebd3368 与 default_4stage_multimer / default_filters：原生四阶段优化、soluble ProteinMPNN 20 序列、原生 PTM model 1/2 复核和官方过滤。原生排序为 Average_i_pTM，越高越好。固定随机种子，保留被内部拒绝的完整 MPNN 序列。default initial_guess / bigbang 均为 false；CPU 已直接截获官方模型实际输入，确认 padded binder template 全零。

同一任务保持一个持久方法会话。环境启动、模型读取、JIT、生成、内部筛选与科学拒绝均消耗计时预算。方法原生分数的单位不同，不能直接跨方法比较。

## 计时与抽样（正式冻结前的预定方案）
预计 7 靶标 × 2 方法 × 2 重复，共 28 个生成任务，每任务 1 张 A100-PCIE-40GB、3,600 秒 GPU 预算，重复种子 21011 / 21012。全局最多 2 张 GPU。共同复核额外计费，不计入设计预算。

已对最大 KEAP1 靶标开展两种方法各一个原生 attempt 的工程试运行，主批次独立计费 591 GPU 秒。RF 完成 1 个骨架、8 条原版 MPNN 序列和 8 次原生 AF2；BindCraft 首个轨迹在进入 MPNN 前被官方 Clashing 筛选拒绝。一次尝试上限导致外层任务退出，不将这个科学拒绝记成技术异常。BindCraft 后续 API 以固定的真实拒绝轨迹开展独立 ENGINEERING_STAGE_COVERAGE，保留拒绝结论、单独计费、排除正式候选池；不能将其写成主 attempt 完整通过。只有当前原生阶段、链身份、CUDA、随机种子、计时边界、增量记录及单独覆盖的内容/开销核验后，才冻结正式任务。不因为结果不好更换靶标、种子、内部默认筛选或比较指标。

正式计时锚点为 Slurm StartTime；3,590 秒停止新生成及所有子进程，预留 10 秒记录尾部。边界截断保留完整序列和部分尾行的明确状态。无法提前结束一个失败任务后闲置 GPU 来冒充完整预算。

主分析从全部完整、去重且截止前观测到的 MPNN 序列中按固定 SHA 盐、靶标、重复种子和序列 hash 选 3 条；抽样键不含方法名称、原生分数或是否内部通过。次分析分别按各方法原生分数选固定 top 2，不能替代主分析。空池、欠填、原生分数缺失、边界截断和工程失败均保留。

## 共同复核
主评估 Boltz2.2.1：3 个固定种子 31011/31012/31013，每种子 1 个模型、3 次 recycle、200 步 diffusion。天然靶标使用 target-only unpaired MSA；binder single。合成 BBF 预定 single sequence。所有共同复核不输入设计坐标、template、initial guess、热点或势能。

次评估 AF2-Multimer-v3 的 5 个模型，种子 31021，3 次 recycle。天然 target MSA cap 128:256，binder single；BBF cap 1:1。另对所有天然原生对照及每个设计 arm 的固定 hash-first uniform 候选开展 single-sequence 敏感性。方法标签与 cohort 来源在评分阶段隐藏。

共同主分数为连续 R1（官方 ipSAE，预定阈值/方向的精确实现），每候选要求 3 个主 Boltz seed 完整后取中位数。没有为新家族引入通用 ipSAE 合格阈值。R0 ≥ 1 仅为已固定的计算诊断门。几何评估包括参考靶标界面覆盖、与参考 partner 的 <2.5 Å 重原子冲突，以及 4/8 Å 接触敏感性。原冻结共同评分的 known_partner_structural_recovery 字段实际使用 target 主链 RMSD ≤2 Å 且靶标接触残基 F1 ≥0.5；它是靶标结构/界面代理，不能称为完整伙伴 pose 恢复。partner 的 target-aligned Cα RMSD 连续单列。此前草案将该字段描述成 partner RMSD 门，现纠正语义，原数值与冻结推断不变。另追加 partner RMSD ≤2 Å 且靶标接触 F1 ≥0.5 的严格伙伴几何诊断，原生对照/BBF 中明确标记为回顾性诊断，不声称它在原生推断前已冻结；不调整主 R1 或固定 R0 门。

7 个原生互作对照、20 个复核作业、74 个模型全部完成原始输出与评分内容验收（CPU13211；独立逐边读取核验13214）。74/74 内容有效表示输出齐全可核验，不能写成原生 pose 全部恢复。AF2 对 EGFR、H-Ras、BBF 的参考 pose 恢复弱，Boltz 对 H-Ras 和 BBF 也有限；这些失败保留在矩阵中，限制相应新候选的解释。具体资格、R0/R1、参考界面与 RMSD 按引擎分别报告。若原生对照未恢复，specificity / blockade 推断保持不可确认。

## 跨家族失效诊断
已对历史 78 个对照、1,170 个模型完成 R0 精确重现与官方 ipSAE 重评分。BBF 阳性恢复仍为 0/6；Mdm2 假阳性仍过高，因此不能宣称换分数已经解决跨家族筛选。

已完成 BBF 11 个已知对照的 110/110 模型内容验收（CPU13125）；正在按既定 SPR 资格标签独立解释连续分数与固定诊断门，不将此开发资料称为新家族外部验证。诊断设置：single sequence / target-only 9HAG 实验 template 两个 arm，5 个 Multimer-v3 模型、种子 31031、3 次 recycle。只输入实验 target 单链 template，完整作者 binder query 保留，binder template / initial guess 全零。完整矩阵终态、实际输入数组及所有分数都要交付，不用专门为 BBF 调阈值来救结果。

## 聚合、验收与交付
每个重复以所有已选 uniform 候选主 R1 中位数表示质量，要求所有已选候选均有完整结果且 cohort 非空；欠填必须展示实际数量。靶标值为两个重复中位数的平均，任何一个重复缺失则为 null。只在两个方法都有效时给出 RF−BindCraft 差值；只有 6 个天然靶标的全部配对有效时报告完整矩阵宏平均，否则完整比较为不可估计，不能剔除难靶标。native-top 单独分析。仅作描述性比较，不报告 p 值或推断置信区间。

最终必须完成：全部正式任务与复核矩阵终态、原始 sacct GPU 秒核对、独立 ledger / cohort / 原始结构 / 分数重算、完整源码提交与 GitHub 交付、哈希闭包分卷备份、同一 Lustre 上独立恢复再计算、唯一 ACTIVE 原子更新，以及本地人类可读审计报告。许可证软件和大模型权重保留条件依赖，不公开重分发；同文件系统恢复不称为异地备份或离线 GPU 镜像。

方法依据：[RFdiffusion 官方仓库](https://github.com/RosettaCommons/RFdiffusion)、[作者 AF2 initial-guess 验证流程](https://github.com/nrbennet/dl_binder_design)、[BindCraft 官方仓库](https://github.com/martinpacesa/BindCraft)、[Boltz 推理文档](https://github.com/jwohlwend/boltz/blob/main/docs/prediction.md)、[官方 ipSAE](https://github.com/DunbrackLab/IPSAE)。

