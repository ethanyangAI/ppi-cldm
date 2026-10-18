# 共同盲化复核执行协议 v1.2

冻结前提：root 的生成协议先登记 common_review_gate={"score":"R0","threshold":1.0,"operator":">=","aggregation":"all_required_models_median","scope":"COMPUTATIONAL_ONLY"}。R1 continuous 为主终点，不预设通用二元阈值；operational_pass=null，原因 NEW_FAMILY_UNVALIDATED/UNVALIDATED_TRANSFER。原 published78 全部为 development。

primary Boltz2.2.1：seed31011/31012/31013，每seed1model，3recycles/200samplingsteps/no_kernels/1实际allocated GPU。6天然target使用CPU MMseqs2冻结 target-only unpaired MSA，query/binder每链完全相同、rowcount/unique count/deletion semantics/SHA保留；BBF.synthetic按靶标身份预先single。binder均single，无templates/hotspots/设计或复合体坐标/initial guess。天然单序列可能降低准确性，因此全single只作预定sensitivity：7 native controls +各arm uniform hash首1candidate；BBF与primary重叠复用。

secondary AF2：multimer_v3五模型各1seed31021、3recycles、early-stop .5、0relax，无template/initial guess；天然target复用primary MSA cap128:256，binder单行；BBF cap1:1。保存实际config和实际A3M，CPU精确roundtrip验证每链query/cardinality、paired/unpaired有序序列与deletion matrix。失败typed unresolved，不能偷偷fallback。

原生伙伴从冻结reference observed链B取得，明确是实验观测构建体；不把reference/knownbinder坐标输入推断。target internal missing修复并验收后使用完整query。query→experimental observed mapping逐残基exact一致；不臆造missing loop的实验坐标。

uniform每arm K3从截止前ALL completed unique MPNNN序列哈希抽样，保留生成器内部reject；native topK2独立用途。两个cohort交集按exacttarget+exactbinder只推断一次，原cohort分母与underfill均保留。inference/analysis无method origin/native score/cohort字段；membership仅CPU内容验收后unblind。

R0每模型使用global ipTM/.75、binderpLDDT/.8、unique界面pLDDT/.8、8Å/双向5Å重原子残基接触PAE的minimum。Boltz global ipTM与AF2 global ipTM并列；directional pair ipTM另外记录。R1官方6174cf9e71cb1bd660cc805856a18c4871a6dec3的ipSAE10-max；两方向/min10/max15/d0dom敏感性保留。每引擎必须全部预定模型有效才给主median/IQR；缺失/no-interface为null不补0，不删除分母。R0>=1只叫固定计算回收率；R1/geometry无事后硬AND门。

geometry连续proxy：mapped targetCA对齐后的native5Åtarget接口覆盖、candidate/nativepartner<2.5Å重原子clash pair数量和原伙伴重原子overlap fraction；4/8Å contact sensitivity。原生伙伴恢复预定逐模型 targetmappedCA RMSD<=2Å且reference contact-targetresidue F1>=.5，另报伙伴target-alignedCA RMSD/contact pair recall。该恢复判据用于复核器可恢复性，不是亲和/功能证据。

所有下载/hash/准备/测试/评分/报告在organ CPU且GRES0（用户本轮允许），GPU worker须scontrol AllocTRES/TRES实际gres/gpu=1，root冻结后统一提交，整体最多2并发。raw worker exit0仅状态，CPU hash、链身份/units/配置/MSA/官方score/模型分母验收后才计完成。

CLI：
- targets --input FROZEN_TARGET_LIST --out registry.json
- msa --input registry.json --out msa.json
- prepare --registry registry.json --msa msa.json --cohorts selected.json --gate-protocol ROOT_GENERATION_PROTOCOL --out inference_plan.json
- worker --plan inference_plan.json --index INDEX --out RAW_SHARED_CACHE (GPU由root)
- score --plan inference_plan.json --analysis analysis_plan.json --worker RAW_SHARED_CACHE --out score.json (CPU，不读取membership)
- verify --input score.json --membership membership.json --out acceptance.json (CPU，独立重算summary/hash后unblind)

准确结构/实验blockade/亲和力/新家族泛化均不能由计算score宣称。具体优势须根据新benchmark实际target/method/rep/cohort分布、缺失与计算预算比较；无显著或反向结果也完整交付。

