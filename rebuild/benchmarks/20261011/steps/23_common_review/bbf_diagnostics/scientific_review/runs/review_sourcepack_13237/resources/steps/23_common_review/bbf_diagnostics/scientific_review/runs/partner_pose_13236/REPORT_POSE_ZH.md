# 已知伙伴pose几何补充审读（source-preserving）

原字段known_partner_structural_recovery实际以target CA RMSD≤2 Å与target接口F1≥0.5判断，明确保留并改称target/interface proxy。下列伙伴pose端点另以target配准后的partner CA RMSD≤2 Å且target interface F1≥0.5判断；两门均含等号，不依赖R0/R1、不拟合阈值。此为计算结构比较，不表示实验结合或功能验证。

原74模型评分、源码、GPU推断均保持原字节/hash。完整20job/74模型及BBF110中b4两臂10模型有真实有限几何值，无missing当negative或补0。统计单位仍是模型技术重复；不同engine/variant分列，不混成实验样本。

端点登记/解释时序：RETROSPECTIVE_CONTROL_GEOMETRY_DIAGNOSTIC; native74/BBF development; no cutoff fitting, no pre-native preregistration claim。所绑定protocol见JSON receipt；凡旧文本明定target RMSD，不能称其早已定义partner门。

|target|engine|variant|有效/预定|伙伴RMSD median [Q25,Q75] Å|target F1 median|伙伴pose计数|旧target/interface proxy计数|
|---|---|---|---:|---:|---:|---:|---:|
|MDM2_1YCR|boltz|primary|3/3|1.735 [1.641,1.768]|0.909|3/3|3/3|
|MDM2_1YCR|af2|primary|5/5|1.746 [1.632,1.768]|0.857|5/5|5/5|
|MDM2_1YCR|boltz|single_sensitivity|3/3|2.060 [2.034,2.110]|0.884|0/3|3/3|
|KEAP1_2FLU|boltz|primary|3/3|3.755 [3.353,3.880]|0.950|0/3|3/3|
|KEAP1_2FLU|af2|primary|5/5|3.423 [3.194,3.842]|0.895|0/5|5/5|
|KEAP1_2FLU|boltz|single_sensitivity|3/3|4.953 [4.947,5.764]|0.974|0/3|3/3|
|BCLXL_2M04|boltz|primary|3/3|5.724 [5.564,5.742]|0.711|0/3|0/3|
|BCLXL_2M04|af2|primary|5/5|5.047 [4.918,5.087]|0.693|0/5|0/5|
|BCLXL_2M04|boltz|single_sensitivity|3/3|5.253 [4.821,5.514]|0.685|0/3|0/3|
|EGFR_DIII_1IVO|boltz|primary|3/3|3.924 [3.870,11.500]|0.958|0/3|2/3|
|EGFR_DIII_1IVO|af2|primary|5/5|17.073 [16.777,17.642]|0.759|0/5|5/5|
|EGFR_DIII_1IVO|boltz|single_sensitivity|3/3|4.411 [4.360,4.543]|0.939|0/3|3/3|
|HRAS_4G0N|boltz|primary|3/3|5.861 [5.788,5.903]|0.788|0/3|3/3|
|HRAS_4G0N|af2|primary|5/5|11.182 [11.168,16.637]|0.565|0/5|5/5|
|HRAS_4G0N|boltz|single_sensitivity|3/3|20.813 [20.561,21.129]|0.485|0/3|1/3|
|CRK_SH3_1CKA|boltz|primary|3/3|0.415 [0.403,0.428]|0.903|3/3|3/3|
|CRK_SH3_1CKA|af2|primary|5/5|0.987 [0.900,0.996]|0.897|5/5|5/5|
|CRK_SH3_1CKA|boltz|single_sensitivity|3/3|0.511 [0.476,0.524]|0.903|3/3|3/3|
|BBF111_9HAG|boltz|primary|3/3|6.204 [5.700,6.232]|0.769|0/3|0/3|
|BBF111_9HAG|af2|primary|5/5|45.914 [21.563,48.440]|0.100|0/5|0/5|

## BBF b4开发输入诊断单列

|arm|伙伴RMSD median [Q25,Q75] Å|target F1 median|伙伴pose/5|旧target/interface proxy/5|
|---|---:|---:|---:|---:|
|single_no_template|16.160 [11.318,44.053]|0.595|0/5|0/5|
|single_target_only_9HAG_template|2.346 [2.225,2.361]|0.971|0/5|5/5|

BBF110的target112/seed31031/ColabDesign backend与native74的target111/Boltz3seed或AF2seed31021不同，不能合并为配对第三臂。旧5/5 target/interface检查不能写成5/5完整伙伴pose恢复；全部逐模型target RMSD、partner RMSD及F1见JSON。BBF仍为开发数据，无天然PPI/blockade标签。

本补充对6个天然target与1个BBF诊断均完整列出固定模型分母；主R1 endpoint、MSA/模板规则、候选采样与方法比较未调整。它只修正几何语义，不证明workflow优越或未见家族泛化。
