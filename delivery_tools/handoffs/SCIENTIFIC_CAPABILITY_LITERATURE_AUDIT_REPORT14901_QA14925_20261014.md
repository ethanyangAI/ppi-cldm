# 正式计算报告14901／独立QA14925的人工科学、能力与文献审查

本文件为人工解释审查与交付边界备忘录，不是新的软件、科学计算、成本或归档验收。审查读取了正式中文报告全文、已生成的主验收、独立112槽位与报告QA凭据，并核对一手方法文档；没有读取模型RAW内容、重新计算分数／统计、运行神经推理、改写冻结报告或源码。根审查与独立人工审读均未发现需要更改当前报告的实质性越界。

报告：[REPORT_ZH.md](/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_scientific_report_build_14901/REPORT_ZH.md)，13308 bytes，实际CPU SHA256769bf92c23119cbe946d92b33a26da7587b73f6a9d994a143b9410c8968f2fd4。独立QA：[acceptance.json](/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/final_scientific_report_qa_14925/acceptance.json)，6663 bytes，实际CPU SHA256809eb53f2bacc49d9b3a309d48f4c4784179af5a6a2d9b1762fa6f27478ca5c3，状态FORMAL13260_FINAL_CHINESE_REPORT_AND_MATRIX_CPU_ACCEPTED。构建14901为COMPLETED0:0／180秒，独立QA14925为COMPLETED0:0／16秒；CPU1／GPU0来自各自真实owned CPU guard。二者不是完整项目发布或恢复的替代门。

## 分母、失败和比较解释

固定28个生成arms保留，26个达到完整预算可比门；CRK的两个RFD早期工程失败保留，完整生成矩阵为false。全112个cohort-engine槽位与1124个结构模型分母保留。空cohort／工程失败与真正的数值零不同，不把不可估计写成阴性生物学。123是所选成员数，不是已验证结合者数。

均匀主cohort每arm最多K3、原生分数次cohort最多K2，两者的选择机制不同，分开呈现；两固定生成seed、不同复核引擎和诊断靶标边界保持冻结。主Boltz与次AF2均只有5／6主靶标完整配对，原生选择次cohort为3／6；总体macro需要全部六对，因此均值／中位数／推断性p值与区间保持NULL。逐靶标描述结果可以读取；不将可用子集外推为固定六目标总体优势，也不通过删除靶标或补零改变比较。BBF111仅为诊断，不混入主macro。

正式native14双引擎主控制、20 jobs／74 models的全部native变体、历史native74与development筛选分别注明。target recovery／接触几何flag、伙伴target-aligned RMSD和target-binder intrinsic最小距离是不同端点。报告已说明结构恢复flag不等于原生伙伴整体姿势恢复，未观察loop不填充；intrinsic <1.5 Å诊断不改变冻结R1、排序或筛选。

## 方法与文献边界

BindCraft官方实现使用AF2反向传播参与设计。因此，本轮AF2次引擎复核不能被宣传为完全外部、与BindCraft设计oracle无关的第二个验证器；这是从方法依赖关系得到的解释限制。当前报告将Boltz作为主引擎、AF2单独作为次引擎，未宣称两个完全独立外部验证器。[BindCraft官方方法说明](https://github.com/martinpacesa/BindCraft)

ipSAE是由预测PAE和长度／接触定义构成的链间计算评分，max取非对称方向值中的最大值。它是固定计算端点，不能直接解释成实测Kd、实验结合阈值或竞争阻断；R0≥1亦不是实验阈值。[ipSAE官方定义](https://github.com/DunbrackLab/IPSAE)

Boltz的结构／置信输出与affinity模块是不同输出；官方文档所述affinity模块针对小分子与蛋白靶标，不能从本轮蛋白binder的置信或ipSAE结果推定binder-target亲和力。[Boltz官方预测文档](https://github.com/jwohlwend/boltz/blob/main/docs/prediction.md)

RFdiffusion原方法的论文结果属于其研究设置。方法论文已展示的实验成绩不能替代本轮固定65-aa、一小时预算、所选域／种子协议的实验验证，也不能建立任意蛋白对或新家族可靠性。[RFdiffusion原论文](https://www.nature.com/articles/s41586-023-06415-8)

根审查浏览BindCraft Nature页面时遇到不可访问的认证重定向；随后核对可访问的作者官方实现文档。该网页访问事件不属于Slurm／Source／报告验收失败，不把无法访问页面当作已直接读到的文献内容。没有下载论文文件、模型、数据或创建本地科研源码镜像。

## 成本、能力与尚待完成的交付

本轮root universe的143583 GPU秒、312已分配失败秒与最大2并行GPU已由独立完整成本验收14576接受；报告保留这些边界并排除历史native重复收费。生成arm成本按共享arm计，不按112行重复相加；总额不是整个历史项目成本。

参考自由E2E现有结果是工程性、新家族仍UNVALIDATED；默认工作流集成实际技术接受由独立13420门提供。正式计算benchmark、E2E／默认技术可运行性、实验结合／竞争阻断、临床效用与跨家族泛化不是同一种证据。报告没有把上述技术接受推广为任意蛋白对可靠或方法全面优越。

本审查结论为：在COMPUTATIONAL_ONLY范围内，报告和独立QA可继续作为九角色来源闭包输入；没有要求改写冻结报告／统计／源码或重复54软件测试。完整source audit／stage、私有历史与bundle、真实GitHub发布及CPU API读回、包装／显式CORE extract、仅 restored index的全RAW科学重算、13460元数据关系与ROOT298完整成本回放、最后ACTIVE提升仍必须逐门实际通过。当前不是最终完整交付。

本文件及其元数据安装／读回记录须作为scientific_report与final_delivery_tools的显式补充文档来源／evidence seed保留；它不增添第十角色、不替换Report QA6663或Composer13377／130，不作为自身归档之后恢复门的循环先决条件。
