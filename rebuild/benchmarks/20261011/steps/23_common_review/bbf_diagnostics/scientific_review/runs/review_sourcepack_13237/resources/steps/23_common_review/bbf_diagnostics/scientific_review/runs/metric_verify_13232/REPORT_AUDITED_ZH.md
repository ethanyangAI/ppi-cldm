# BBF输入条件开发诊断：独立审读

本轮110/110模型完成且通过独立内容复核。统计单位是11个既有设计（原资格化6个SPR检出、5个未检出），每个设计每臂5个AF2权重模型为技术重复。以下结果只解释已知BBF控制的输入敏感性。

原表标签、完整binder query、末端构建范围、main/sensitivity资格与冻结eligibility78逐条一致；无改标签、无删除案例、无模型择优、无重调cutoff。两臂都single target/binder MSA，5multimer_v3×seed31031×3recycles，仅target模板有无不同。

|输入臂|R0 AUC|R1 AUC|旧R0≥1 TP/FN|FP/TN|TPR|FPR|
|---|---:|---:|---:|---:|---:|---:|
|single_no_template|0.3667|0.3333|1/5|2/3|0.167|0.400|
|single_target_only_9HAG_template|0.6667|0.6667|2/4|1/4|0.333|0.200|

AUC由正负案例所有30对的胜负（并列计半）与独立秩和公式交叉验证。病例汇总固定五模型中位数；原R0≥1仅作既定计算回收门诊断。R1始终连续，未创建实验检出概率或新阈值。

|原案例|原SPR标签|R0 single→target template|R1 single→target template|target RMSD Å single→template|
|---|---:|---:|---:|---:|
|bc_BBF_b10|0|1.039→0.288|0.609→0.010|2.76→1.22|
|bc_BBF_b11|0|1.020→0.291|0.545→0.000|2.66→1.21|
|bc_BBF_b12|1|1.092→0.446|0.617→0.010|2.65→1.21|
|bc_BBF_b13|0|0.935→0.203|0.460→0.000|2.55→1.20|
|bc_BBF_b2|1|0.190→0.208|0.000→0.000|2.72→1.21|
|bc_BBF_b3|1|0.225→1.109|0.000→0.666|2.46→1.20|
|bc_BBF_b4|1|0.151→1.082|0.000→0.621|2.44→1.27|
|bc_BBF_b5|0|0.160→1.070|0.000→0.655|2.49→1.21|
|bc_BBF_b6|1|0.150→0.973|0.000→0.470|2.56→1.22|
|bc_BBF_b7|0|0.170→0.996|0.000→0.505|2.45→1.19|
|bc_BBF_b8|1|0.218→0.984|0.000→0.578|2.48→1.23|

单序列无模板时，评分排序对作者SPR标签的AUC低于0.5；加入实验unbound target-only模板后，连续排序在这11例内改善。固定旧R0门可能仍漏掉连续分数较高的阳性，阳性b2/b12仍低分，阴性b5/b7仍呈高R1；AUC=0.667属于不完整区分，不能写成全部回收，或从结果选择新门。11个病例不足以证明跨家族适用；未检出标签受原作者SPR条件、表达/纯度、构建与未知重复数限制，不表示所有条件下无亲和力。

## 结构解释与泄漏审查

9HAG unbound核心与9HAC bound target为相同111残基；独立CA配准RMSD=1.3003 Å。模板每个原子坐标与原始9HAG CIF交叉匹配，未替换为9HAC bound复合体。
- 已知b4，single_no_template：target RMSD中位数2.444 Å；target配准后已观测binder CA RMSD中位数16.160 Å；固定target backbone+interface几何检查满足0/5。
- 已知b4，single_target_only_9HAG_template：target RMSD中位数1.267 Å；target配准后已观测binder CA RMSD中位数2.346 Å；固定target backbone+interface几何检查满足5/5。

固定native74中的BBF已知b4控制作为单列上下文（未用于本轮AUC/阈值）：

|引擎|固定有效模型|R0 median|R1 median|伙伴CA RMSD median Å|固定target+interface检查|
|---|---:|---:|---:|---:|---:|
|boltz|3|0.859|0.270|6.204|0/3|
|af2|5|0.160|0.000|45.914|0/5|

逐模型native target RMSD、interface F1和伙伴CA RMSD见metrics.json/native_control_context.models。native target111与旧b4 target112（初始M）不同，且backend/seed不同，因此该上下文不能作为本轮第三个配对arm。原known_partner_structural_recovery字段实际按target RMSD≤2 Å且interface F1≥0.5，伙伴RMSD另报；置信度、R1与伙伴RMSD不能互相替代。

b4推理输入为作者完整140残基核心，晶体147残基的末端GSHHHHH单列；reference缺失的内部残基不从query删除，几何仅使用明确映射的观测CA。所有22个实际特征文件逐个重读：forward query与原表完整序列一致、single-row MSA一致；raw batch/effective template坐标只来自9HAG target，binder mask/position/pseudo-beta全零、prev_pos全零；无模板臂target mask/position/pseudo-beta也全零。所有GPU worker与同一immutable backend、该CPU feature hash及自身raw PDB/confidence绑定；GPU时未另行抓取每层中间张量，证明范围是固定源码/输入生成路径与CPU实际forward feature捕获的复用。9HAC/b4只用于事后结构比较，不在模板或initial guess输入内。

这支持一种解释：synthetic BBF缺少天然同源MSA，独立序列推断的target局部几何偏差可影响置信度排序；提供近似bound折叠的实验unbound target帮助恢复正确target先验及已知b4姿态。此为与观察一致的计算解释，不能单凭相关性确定因果，也不能证明其他BBF阳性的真实界面或功能。模板来自原设计同靶标结构，因此该臂是target-conditioned recovery，而不是完全sequence-only评估。

## 证据范围

旧15模型MSA/no-template结果仍保留为不同seed/模型预算的历史参考，不与本轮两臂混为第三个配对处理；本报告未改正式共同复核primary/secondary、目标MSA规则或候选采样方案。R0门只诊断历史计算回收，几何coverage/clash仍是proxy；BBF无已确立天然PPI伙伴或实验blockade标签。不能据此宣称RFdiffusion或BindCraft方法优越、跨家族泛化成功、亲和力或实验阻断。

既有query构建范围也与分数分组相关：b3–b8为112残基query（初始M没有模板坐标），其原标签是4阳性/2阴性；b2及b10–b13为111残基，是2阳性/3阴性。模板臂112组全部R1较高，111组全部R1较低，因而不能把这一结构分组误认成SPR阳性/阴性。两组binder序列/长度/设计拓扑也不同，本轮无法把初始M效应与这些因素拆开；两臂在同一案例内query完全一致。后续若做构建输入因果诊断，应另行预定全部11案例的query范围交叉敏感性，不能按结果修改本轮或正式benchmark。

target模板使阳性和阴性的target RMSD均下降，target几何恢复本身不能验证结合。只有b4有已知实验复合体可直接核查姿态；其余案例不能从5 Å覆盖或R1置信度获得实验pose/阻断真值。

原子来源检查853个9HAG核心原子；独立raw R0/固定官方R1/target RMSD/interface F1检查110模型；7项meaningful contracts通过。完整分数、秩、paired delta、原标签与hash见同目录JSON/TSV。

依据：[BindCraft原论文](https://www.nature.com/articles/s41586-025-09429-6)说明BBF无天然同源、11个纯化设计6个检出，9HAG用于设计靶标及9HAC为b4晶体；[9HAG](https://www.rcsb.org/structure/9HAG)为1.86 Å monomer实验结构，[9HAC](https://www.rcsb.org/structure/9HAC)为3.10 Å复合体；[ipSAE固定官方revision](https://github.com/DunbrackLab/IPSAE/tree/6174cf9e71cb1bd660cc805856a18c4871a6dec3)作为既定连续置信度来源。

## 已知b4逐模型几何核验：明确区别target与partner

冻结门为target CA RMSD≤2 Å且target interface F1≥0.5；它没有partner CA RMSD门。因此BBF110模板臂5/5仅指target+interface几何检查，不能写为完整binder姿态达到≤2 Å。伙伴CA RMSD按target配准后独立计算、连续报告，未新增rescue cutoff或筛选规则。

|上下文|model|seed|target CA RMSD Å|target interface F1|partner CA RMSD Å|原target+interface检查|
|---|---:|---:|---:|---:|---:|---:|
|BBF110:single_no_template|1|31031|2.6486|0.0000|44.0533|0|
|BBF110:single_no_template|2|31031|2.5643|0.0000|49.2282|0|
|BBF110:single_no_template|3|31031|2.0988|0.5946|16.1595|0|
|BBF110:single_no_template|4|31031|2.4439|0.7027|11.3180|0|
|BBF110:single_no_template|5|31031|2.4325|0.6061|10.5984|0|
|BBF110:single_target_only_9HAG_template|1|31031|1.2537|0.9714|2.1612|1|
|BBF110:single_target_only_9HAG_template|2|31031|1.2084|0.8889|25.4243|1|
|BBF110:single_target_only_9HAG_template|3|31031|1.2674|0.9714|2.3456|1|
|BBF110:single_target_only_9HAG_template|4|31031|1.2724|0.9714|2.2250|1|
|BBF110:single_target_only_9HAG_template|5|31031|1.2715|0.9714|2.3608|1|
|native74:boltz|0|31011|2.7312|0.7027|6.2035|0|
|native74:boltz|0|31012|2.7052|0.7778|6.2602|0|
|native74:boltz|0|31013|2.7171|0.7692|5.1974|0|
|native74:af2|1|31021|2.6717|0.0000|48.4404|0|
|native74:af2|2|31021|2.6599|0.0000|48.5645|0|
|native74:af2|3|31021|2.7338|0.1000|45.9135|0|
|native74:af2|4|31021|2.5059|0.5143|20.9125|0|
|native74:af2|5|31021|2.3905|0.4615|21.5629|0|

独立stdlib verifier从110模型重建22个case中位数，另用排序并列平均秩重算AUC、重算固定R0混淆矩阵，逐文件hash核对，5项额外合同通过。早期13221 checker列顺序假设错误已保留原失败日志；没有改动原始推断、标签或分数。13226为中间审读，13230为数值/解释修订结果，当前审读入口由本acceptance明确绑定。
