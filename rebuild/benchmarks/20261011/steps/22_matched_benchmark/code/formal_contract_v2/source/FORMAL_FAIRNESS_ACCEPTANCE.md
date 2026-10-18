# 正式配对 benchmark 的独立公平性验收合同 v2

本合同只审查软件、资源计费、完整分母和描述统计。真实运行、候选与模型结果必须由各自冻结来源和内容验收支持；合同单元测试不是科学结果。

## 冻结字段

| 项目 | 固定值 |
| --- | --- |
| 任务单位 | 7靶标 × 2方法 × 2重复，共28任务 |
| 主靶标 | MDM2_1YCR、KEAP1_2FLU、EGFR_DIII_1IVO、BCLXL_2M04、HRAS_4G0N、CRK_SH3_1CKA |
| 诊断靶标 | BBF111_9HAG，始终不进入六靶标宏汇总 |
| 方法 / 效应方向 | rf_diffusion、bindcraft；RF minus BindCraft |
| 长度 / 种子 | 所有完整原始候选固定65aa；21011、21012 |
| 生成资源 | 每任务实际单张 NVIDIA A100-PCIE-40GB，显存至少40000MiB，名义3600 GPU秒 |
| 截止 | Slurm StartTime 起计；科学生成3590秒；共同10秒用于清理和持久记录 |
| 可比较状态 | 完整持久receipt和原始账本；COMPLETED或TIMEOUT；实际3600±2 GPU秒；无工程失败 |
| uniform | 所有截止前首次观察到的完整唯一序列，包括native拒绝及native分数NA；固定SHA盐；最多3 |
| native | 分开的方法原生标量排名top2；分数NA保留缺失数量；不足2不补造 |
| SHA盐 | PPI-PAIRED-20261011-FIXED-BEFORE-GENERATION |
| 共同主引擎 | Boltz，31011/31012/31013，完整3模型；R1 official ipSAE 10Å max连续值 |
| 次引擎 | AF2，seed31021，模型1–5，完整5模型；与Boltz分开 |
| 二元诊断 | R0≥1，全部规定模型的中位数；COMPUTATIONAL_ONLY |
| 统计 | complete_selected_candidate_median_then_both_replicate_mean；六靶标全配对描述汇总；无显著性或推断CI |

正式吞吐不允许工程pilot的max_attempts=1。persistent session初次环境启动/import/JIT、失败设计、MPNN、方法内AF2和native拒绝均计入统一生成预算。方法原生AF2可使用冻结的相应原生模板/initial guess；共同盲评不读取设计pose、模板或initial guess。

## 调度、所有权和实际费用

初始唯一调度记录必须是本任务真实RUNNING且allocated GPU1。Slurm JOB/STEP全局GPU编号通过driver Device Minor→UUID映射与NVML UUID核对，子进程固定为所拥有的唯一UUID。裸CUDA可见UUID不是分配所有权。

逻辑数组标识master_index与物理数字JobId分别保留。sacct计费按唯一物理JobIDRaw；step、数组汇总不重复计费，正GPU费用且缺run receipt的分配必须报错。历史13069两次失败仍计183+17=200 GPU秒。

3600秒的Slurm TIMEOUT本身不是工程失败，也不是内容成功。v4 runner在3590秒终止GPU进程组，先持久保存完整run receipt，再等待相同10秒尾部。仅具备完整receipt/原始账本/截止时间/硬件与所有权证明、实际费用在预定容差、且没有工程中断时才可比较。文件系统或终止异常造成receipt缺失，必须列为工程未解决，费用仍统计。工程早停立即释放，禁止空占凑满预算。

## 原始序列与分母

独立合同检查每条完整原始序列的65aa、canonical残基、SHA、task/target/method/seed、原始attempt ID和观察截止标记。native拒绝、native分数NA、同序列不同lineage及边界后完整记录都必须审查；不能只验证接受子集。边界后记录不进入选择池，但完整记录不免除长度合同。

attempt索引连续，所有attempt有终态；原始完整序列数、截止前序列数、native更新数逐attempt闭合。序列重复允许存在于原始账本；仅同task的唯一序列身份去重，lineage保留。相同attempt重复sequence_record_id或更新丢失原始序列应报错。无效完整序列为工程合同问题，不能被过滤后当作正常科学阴性。

## 112行及缺失语义

报告固定输出28任务 × uniform/native两cohort × Boltz/AF2两引擎，共112逐重复行。覆盖登记必须包含全部28任务，即使失败或无候选。

- 真正完整预算、完整观察的空池：n_selected=0，R1质量null；固定观察到的回收数量可为0，样本比例0/0仍null。
- 工程早停、未提交或无可比完整预算：质量及单位GPU小时回收值为null，原因明确为GENERATION_UNRESOLVED_NO_FULL_BUDGET。
- 选择池不足K：保留n_requested=3/2、真实n_selected及underfilled，不能按方法事后挑相同设计数量。
- 已选择的非空cohort缺summary或模型结果：保留选择分母，质量null；不得标成空池或补0。
- native分数不可得与native科学拒绝独立记录；uniform不依赖两者。
- 重复cohort summary、重复结果ID或重复模型slot应报错，禁止字典覆盖或set比较隐匿重复。

单位GPU小时的观察回收数使用实际分配秒数作分母，而不是固定名义一小时。该数只描述规定共同评估样本，不估计全部生成候选的真实通过率。

共同模型按exact target query+sequence去重缓存；原方法/重复/cohort归属及全部选择分母保留。native reference controls的partner长度不受候选65aa合同影响。

## 独立聚合

先检查每个预选候选的全部冻结模型slot；候选R1仅在规定3/5模型全可用时取中位数。再从blind score结果及membership独立重算cohort候选中位数、完整数量和模型覆盖；不只信任已解除盲态的summary。cohort质量要求全部真实选中候选均完整、且非空。

每靶标/方法由两个固定重复的cohort质量取等权平均，不能把更多候选或模型的重复加权。RF–BindCraft逐靶标差值必须保留全部六主靶标；宏平均/中位数仅在全部六个配对效应可估计时输出。BBF诊断不填补缺失主靶标。Boltz主端点、AF2次端点及native次cohort各自报告，无混合评分、p值或推断置信区间。

step24现有target_statistics.py已通过独立空矩阵及基本聚合验证；最终必须先通过本合同的重复、长度、实际费用和scored→summary闭合验收，再读取其56行×两重复及全六靶标汇总。

## 来源冻结与历史别名

冻结plan/config/adapter/target/输入来源按(path, SHA)作为身份键，而不能仅按路径。旧证据引用开发脚本时，仅能解析到SHA和字节数完全相同的只读历史快照，报告原指针、当前指针及精确快照别名；不得将旧SHA声称为当前开发路径的SHA。

CPU13113定位旧readiness_12980的adapter_source：33676bytes，b47e302116b923e683aee567fe0c1b6721a56d6c410de9cd2cdd9dcfd79fecfd，尚无对应归档。它与最终13092/v6的43050bytes SHA1325556ccac5936bbae456344f040257b5041815190af5b48425cf016bc38e17不同。新current_v7与observation_v8只读dependency/config已替代该旧input proof。CPU13167已验证plan_v5的351个当前exact凭据与161项合同；旧v4未执行记录直接验证原始receipt，旧报告内old_config比较分支属于ENGINEERING_HISTORY，不递归冒充当前依赖。旧b47缺口仍明确保留，当前v8权威不依赖它。

工程GPU内容验收必须绑定确切工程plan、runtime、orchestrator、config、target和两次真实run receipt，并有独立计费验收。科学拒绝不要求转为接受；但早期trajectory拒绝本身不能证明未执行的MPNN/AF2阶段。补充API工程覆盖需明确coverage_mode、单独计费并保留证据，不可混入正式候选。


## 全部原生分数与置信度原始文件

当前方法runtime为readonly pilot_v8，51064bytes、SHA51b516a692d369f4d9a6ae9e3c39c0294da219c4d065420bbf9538a4af4b6562。v7→v8仅新增after-return置信度/同aux官方PDB序列化和task/attempt/replicate观察元数据；GPU模型调用参数、随机抽样、模型调用数量和排序未变。该复制/序列化开销仍计入相同GPU分配截止。

冻结CPU collector是native_collector_contracts_13166/source/audit_native_confidence_v8.py，16372bytes、SHAeca561182d06eca52bde005b45f02dd261d57b916d70ea5e34e99e86a79830b5。它对每个实际attempt运行，包含原生拒绝、分数NA和预算边界。原报告的ENGINEERING_ONLY表示技术内容审计不自称科学成功；它不赋予正式候选新的可比较性。

独立v2合同读取全部attempt的collector receipt，原生update数量必须与完整原始流和first-observation标准化账本完全一致；source_line_number=原native_update_index+1，禁止blankline改变索引。每个更新包括scoreNA都必须有一条审计结果，不能只审top2或接受序列。

模块以stdlib解析五个primitive NPZ数组，直接检查aatype full query、PAEÅ、pLDDT fraction、global iPTM及same-aux PDB的A/B链序列和CA pLDDT。RF排序值从两个方向的target–binder PAE均值独立回算，必须只有model_1_ptm；BC有分数时必须恰好model_1_ptm+model_2_ptm，按照官方先逐模型round2、再mean/round2回算。默认native过滤和RF坐标criteria需冻结collector的全部原始证据；合同同时核其raw数组指标与完整rank流，任何分数NA不得填补。

durable JSON是观察完成标记。完整但尚未写入index的sidecar保留并核验；partial数组/PDB文件保留作为未完成物，不补成预测或排名分数。所有观察的task/attempt/replicate/plan/protocol/config/target身份都严格匹配。完整档案存在不使截止后观察自动进入池；冻结runner的首次观察截止标记始终决定资格。

native-audits JSON形状：
{schema:"formal_native_output_audit_bundle.v1", plan:exact_plan_receipt, collector_source:exact13166_receipt, attempts:[{run_receipt,task_id,attempt_index,acceptance:exact_per_attempt_collector_receipt}]}
所有run_receipts中的全部attempt都需要独立项，包括工程失败。零attempt的初始化失败保留run/费用，不伪造attempt。正式所有receipt来自真实结果，不使用合同测试的synthetic数组。

工程组合器只验证确切两次主工程运行；单列补充API阶段覆盖及其额外GPU费用不能混入该两次主run集合。v2测试覆盖源码/config/task/run集合不一致、缺native阶段、工程失败状态与错误GPU数量的拒绝。

## 执行API

独立只读模块：steps/22_matched_benchmark/code/formal_contract_v2/source/formal_benchmark_contract.py
测试：steps/22_matched_benchmark/code/formal_contract_v2/source/test_formal_benchmark_contract.py
旧formal_contract_v1/40测试和CPU13168/50测试凭据保持原字节。

最终CPU审查入口接受：
--plan --accounting --cohorts --independent-budget --run-receipts
--common --membership --inference --scored --target-statistics --native-audits --output

模块会验证上述输入receipt闭合、raw65aa与双流、全部原生置信度/排名值、独立GPU账本、全部112行、所有共同模型slot（包括controls/sensitivity）、blind→cohort聚合，以及与step24交付统计一致。输出为新的独立验收JSON，不修改接受的v4、共同评分、输入或正式计划。运行必须使用真实RUNNING CPU0 Slurm allocation。

