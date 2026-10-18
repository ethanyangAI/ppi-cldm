# AF2 复核 v2：文献依据与执行边界

## 改动
- 主复核仍为无模板、无设计结构初始猜测的 AF2-Multimer v3。
- 从单权重 × 三种子扩大为五权重 × 三种子；recycle 上限由 3 增至 12，显式 early-stop tolerance=0.5。
- 12 是本轮预先限定的计算预算，不是声称优于 ColabFold 的默认上限 20；报告每模型实际 recycle 和触顶情况。
- 旧 model1、同三个种子的结果保留作配对比较；其余权重用于结构稳定性诊断，15 次预测不能视为15个独立实验。
- CPU Amber 松弛保留 raw/relaxed 两套坐标、原置信度文件及坐标位移。网络置信度不因松弛而重新生成；新接口上的均值属于原分数的重新汇总。
- 将自身折叠、target-aligned pose、原生接口覆盖、主链碰撞、侧链碰撞、松弛位移分别报告。不把全局 ipTM 当作方向性 pair-ipTM。
- 官方 ipSAE 源码按提交固定；PAE cutoffs 10/15 Å、distance cutoff 15 Å；报告双方向结果，无新通过阈值。
- 本轮包含全部三条已筛出的 KEAP1 候选，以及按 ID 哈希选出的每靶标1阳性/1阴性，共5靶标10对照。仅为小规模方法诊断，不足以校准概率或精确成功率。

## 方法依据
1. [BindCraft](https://doi.org/10.1038/s41586-025-09429-6)：区分生成与重新预测，并加入能量松弛和物理接口检查。论文复核采用 AF2 monomer 的两种模板模型、三轮 recycle 和 Rosetta FastRelax；本轮 AF2-Multimer + Amber 不是该方案的原样复现，不能照搬其通过率或归一化阈值。
2. [ColabFold 官方版本说明](https://github.com/sokrypton/ColabFold/wiki/v1.5.0/702284308448d74c2a49b85036283631f8781484)：支持模型/种子采样、recycle 与提前收敛，以及独立松弛。
3. [DunbrackLab ipSAE](https://github.com/DunbrackLab/IPSAE)：提供面向链间接口的辅助分数。本轮源代码版本和文件哈希在 setup manifest 中固定。
4. [OpenMM API](https://docs.openmm.org/latest/api-python/generated/openmm.app.simulation.Simulation.html)：当前最小化容差使用力单位。[AlphaFold issue 923](https://github.com/google-deepmind/alphafold/issues/923)记录旧版本的单位不兼容。

## OpenMM 兼容补充
旧 AF2 的 2.39 kcal/mol 参数在旧 API 中对应约10的数值容差；OpenMM 8要求 kJ/(mol·nm)。独立 worker 显式转换为 9.99976 kJ/(mol·nm)，保存日志和版本；不改安装目录。2000 iterations、3 outer iterations、10 kcal/(mol·Å²)重原子约束保持固定。兼容补充不改变 GPU 预测协议。
失败松弛保留为失败，不自动补成成功；松弛后碰撞减少不能单独证明结合，更不能证明阻断。

## 完成标准
13项完整推断与逐模型后处理，包含缺失的 bb145_seq0 历史基线；输出3×13个旧模型和15×13个新模型的记录、paired model1比较、全部权重的分布、公开对照结果和失败清单。任何新增阈值或扩大到全78对照，应另行预先登记，不能凭本轮候选结果调整门槛。


公开设计可能已在原研究中经过 AF2 设计或筛选，因此存在生成方法与评估器的关联；本轮对照不构成完全独立验证集。复合物中的自身对齐 RMSD 是设计骨架恢复指标，不代表游离状态折叠稳定性或结合亲和力。
