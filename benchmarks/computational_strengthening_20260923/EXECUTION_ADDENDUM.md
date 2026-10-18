# 执行补充与冻结的比较规则

任务：全部执行六类计算加强及多重复短程MD。权威目录：fudan:/lustre/users/u21111210118/projects/test9。
原协议 protocol.json 保持哈希不变；本补充不按新结果调参。

- 校准固定比较三组特征：置信度；置信度+双向ipSAE最小值；再加入游离折叠支持比例、界面能量/面积、形状互补、未满足极性基团/面积。每组取训练集经验百分位的最小值，训练集FPR≤0.20下最大化召回，按靶标家族留出；同源binder≥80%全长一致性跨折时移除训练近邻。只做回顾性诊断。竞争阻断不是这78条结合标签的实测终点，不用其伪造阻断性能。
- Rosetta固定ref2015、3随机种子、每次FastRelax一轮/max_iter200、限制整体链移动、分离后重排。DAlphaBall smoke失败，改用Rosetta自带VSASA/default SASA路径计算BuriedUnsatHbonds，保存失败记录，不能套用DAlphaBall阈值。
- 原113个扩展预测（81游离单体、16原生/消融、15特异性/全长/自缔合、1个KLHL3原生对照）不变。补入6TTK的KLHL12–DVL1原生阳性对照，验证同源靶标预测敏感性，共114项。
- 物理检查覆盖81原始条目以及33新增复合物，每项3次；与不同长度原生肽比较时能量不是亲和力。
- MD为两个优先候选及原生NRF2复合物，各3种子，CPU隐式GBn2/Amber14，100ps平衡、1ns无约束生产。短程不解离不等于高亲和力；保留全部轨迹和异常。

方法依据：
- https://docs.rosettacommons.org/docs/latest/application_documentation/analysis/interface-analyzer
- https://docs.rosettacommons.org/docs/latest/scripting_documentation/RosettaScripts/Filters/filter_pages/BuriedUnsatHbondsFilter
- https://docs.openmm.org/latest/userguide/application/02_running_sims.html
- https://www.rcsb.org/structure/4CH9
- https://www.rcsb.org/structure/6TTK


补充：为区分界面损伤与整体折叠损伤，增加全部15条消融序列的游离单体预测（相同5权重×3种子）。总扩展预测为129项，其中96单体、33复合物；物理检查仍114项，MD仍9条。突变复合物分数下降但游离折叠同时恶化时，不归因于特异界面贡献。

轨迹验收补充：所有MD几何从保存的DCD独立重算，统一相对生产阶段第一个保存帧（10ps）报告；原始在线相对平衡末帧的trace原样保留。验证100帧、原子数、有限坐标，末DCD帧与final.pdb全原子RMSD须<0.002Å。独立读取器使用实际OpenMM写出的已知坐标做单位/帧序与截断拒绝验收。

CPU运行修复：原4线程MD数组186615因短程基准预计每条180小时、超过12小时worker限制而停止，未产生验收轨迹。8线程×9并发基准预计每条83–90小时，改为8线程、6天Slurm时限、143小时worker时限。基准仅20个计时步，不是精确完成日期；正式进度每500步记录。100ps平衡、1ns生产、2fs步长、力场和种子全部保持原定值。每500步保存检查点，另保存平衡末参考坐标；不自动把中断片段拼成合格轨迹。检查点回读坐标、速度和步数通过；多线程随机动力学不承诺逐位相同的后续轨迹。原有127项测试仍通过。
