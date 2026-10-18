# Mandatory OPERATOR ERRATUM9 — actual13558 Common13460/J6 indexed metadata verifier

INSTALLED / MANDATORY HUMAN GUIDANCE ONLY / 2026-10-12T12:30:33.439776+00:00。Root在完整原文读回与common_review_readiness独立HUMAN_READBACK_PASS后安装本指南；原17070B提案及主指南/ERRATUM1–8保持原文。安装不修改代码、收据、源文件、GPU设置、队列、Git或ACTIVE，不运行哈希/编译/测试/作业。实际Common13423仍未全268终态；科学交付、成本、公共发布与真实恢复仍待其实际门。

本提案只补充已实际通过的新软件工具及其以后真实恢复的路由。所有 SHA 均引用已有实际 CPU stdout/保存收据；本提案没有计算哈希、导入项目模块、编译、测试、提交作业或创建验收。

## 1. 已实际闭合的范围

唯一新软件作业13558：organ，owner/account u21111210118，CPU1/GPU0，原始10分钟、8G，无调度覆盖。实际 COMPLETED0:0，26秒；32测试 PASS，failures/errors/skipped 全0。合同日志逐项32个OK；编译 owned Python 与 bash -n 真正通过。原始与冻结 OWN4 同字节，执行前后读回通过。CORE 条件解释器在该实际软件分支前后被原代码验证；没有重跑已有130/20/76/58软件套件。

实际软件验收：

```text
/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/restored_common13460_metadata_software_13558/acceptance.json
bytes=19295
sha256=46961d96044333116e7dd829d364533be1d5815c147fa0df7819ffcd3baee5d7
schema=restored-common13460-metadata-software.v1
status=RESTORED_COMMON13460_METADATA_VERIFIER_SOFTWARE_CPU_ACCEPTED_NOT_REAL_RESTORE
```

该 own tuple 来自实际 CPU stdout349B；stderr0B。它明确 production_restore_verified=false、science_accepted=false、no_GPU_submission=true、ACTIVE_changed=false。通过软件 fixture 不等于已经对真实归档执行元数据验收，更不等于完整RAW恢复、科学有效阻断、实验验证、成本闭合或发布。

同一实际输出目录内，均0444：

| 文件 | 实际 bytes | 已保存的 CPU SHA-256 |
| --- | ---: | --- |
| contracts.json | 2756 | ea477b592115a98e9685add84936d75b30c14724692b4393a59da4af1ea9eea3 |
| contracts.txt | 4726 | a5dfa9b736c3f248b57175d194ed9b3c90103a5d3a2156cf09e8d25366197deb |
| source_snapshot.json | 4235 | 73535f5077469fad876142512e71346e6f6cf0d475f496cbdcc64a9f75e75a6f |

A、contracts.source_files/tested_source_files、snapshot.frozen_source_files 同一精确四条；snapshot.original_executing_sources 与 A.original_executing_sources 同一四条；allocation 同一实际13558。上述 tuple 是既有实际 CPU 证据，并非人工文件的重新计算。

## 2. 精确冻结源码与实际提交历史

实际执行后冻结目录：

```text
/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/restored_common13460_metadata_verifier_v1_13558/code/
```

目录0555，恰四个0444文件；原 pending 同名四文件亦0444/目录0555，保存原入口历史。

| OWN4 文件 | 实际 bytes | 实际原始/冻结共用 SHA-256 |
| --- | ---: | --- |
| checker.py | 36011 | f7e97735915b5457f4da8534a5d0522014fcaff8ec0fbd5c74833bbcdbf78acf |
| test_checker.py | 24595 | f8c65f1b2f2b392fadac895bfc1728de6dc597942fd9200e8a35adfd4ad730fb |
| checker_cpu.sbatch | 1536 | 951327df022cfeffa27cb9c53d4c32e187ace885e36b8e6ad0db87f6f2466587 |
| HANDOFF.md | 15525 | ab460c5ea0ba16fdf72e80f011f8186d242a99aeadcfef3c99be697e29626161 |

实际 root claim 全部保留：

```text
/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_common13460_metadata_verifier_v1_primary_claim/
request.json                    1379 B
metadata_readonly_seal.json      3272 B
submission_in_progress.json       469 B
submit_receipt.json                790 B
```

source seal 只将模式改为0444/0555，原 bytes/inode/mtime 不变。submit_receipt 原始 argv 是 pending launcher contracts，raw_stdout="13558\n"、raw_stderr=""、rc0。request 的 tests_unexecuted=32 与 submit 的 software_accepted=false 是提交当时的原始事实；不得回写这些历史文件来伪造提交时已通过。后来的实际 A 与终态封存证明软件已通过。没有再次提交13558，也不应为已通过的软件重跑 contracts。

## 3. 已实际安装的索引输入终态封存

新工具的历史软件终态证据已经由 root 实际保存并封存：

```text
/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/submissions/restored_common13460_metadata_software_13558_actual_terminal_seal/receipt.json
bytes=8149, mode=0444
schema=restored-common13460-metadata-software-terminal-seal.v1
status=ACTUAL_TERMINAL_SOFTWARE_METADATA_READBACK_PASS_NOT_REAL_RESTORE
```

它绑定实际19295/46961...的软件 A、精确 frozen OWN4、原始 OWN4、contracts、snapshot 与 metadata_only=true。原始保存的固定查询是：

```text
["sacct","-X","-n","-P","-j","13558",
 "--format=JobID,JobName%128,User%64,Account%64,Partition%64,State,ExitCode,ElapsedRaw,AllocTRES"]
```

rc0、stderr为空，唯一实际行：

```text
13558|test9_restored_common13460_metadata|u21111210118|u21111210118|organ|COMPLETED|0:0|26|billing=1,cpu=1,node=1
```

封存实际6文件/1目录：A、contracts.json、contracts.txt、source_snapshot.json、Slurm stdout349/err0 全0444；输出目录0555。before/after bytes/inode/mtime 均未改变，只有原Slurm日志0664→0444及目录0775→0555。只读元数据再次核对一致。本文件自身8149B receipt 的 ownSHA尚未在本提案中提供；未来打包必须使用实际拥有CPU产生的完整索引身份，禁止猜 SHA、按mtime选择或只用basename。

真实生产 checker 将只通过包索引读取这个 saved seal 与软件证据，**不再查询历史13558 sacct**。唯一 live scheduler 查询是它自己当前、实际 RUNNING 的纯CPU allocation guard；不能将 PENDING、缺失CPU、owner/account/partition错误或GPU记录当作验收。

## 4. 九角色最终 SOURCE / metadata 覆盖

既有九角色及主 gate 保持原语义：

```text
formal13260_terminal_v3
native74_cache_catalog
native74_cache_binding
reference_free_e2e
formal_common_review
independent_statistics
scientific_report
final_delivery_tools
default_workflow_integration
```

final_delivery_tools 的主 gate 仍是已有实际 Composer130：
FINAL_DELIVERY_COMPOSER_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_ARCHIVE_ACCEPTANCE。
新32的独立状态不能替换这个主 gate，不能新增第十个角色或声称它实现了既有科学 gate。

root 最终源计划必须为本工具显式写入四个 sources：checker.py、test_checker.py、checker_cpu.sbatch、HANDOFF.md，使用实际13558冻结 full receipts，在独立的公开包目录保留完整同包布局。不要只给 seeds 而漏掉测试、launcher 或 HANDOFF，也不要按basename压平与其他工具的 HANDOFF/launcher。原始 pending 与实际冻结 source 对照仍作为可追溯证据。

在同一 final_delivery_tools 的精确 seeds / 最终全包索引中，覆盖实际新SW A、contracts、log、snapshot、上述8149终态 seal、claim四文件、原/frozen四源、两个Slurm日志及它们引用的既有 SOURCE/qualification。源/索引条目须按 full(path,bytes,SHA)闭合；不能仅引用文件路径或声明布尔PASS。保留主指南/ERR1–8、此提案与以后安装的人工指南作为实际明确的文档源条目；本提案不自动安装、登记或发布它们。

执行代码范围与归档 SOURCE 证据不同：当前实际 executing frozen OWN4、pinned StrictIndex 是允许的执行 CODE；这些文件及其他来源还必须有对应的 indexed archived SOURCE副本。CODE在live路径存在不能救回缺失的 indexed SOURCE。A13377/130 contracts/log 与完整 source12+API15+mapper14（41条）都属于生产必读的索引证据；不运行原130来“补资格”。

CORE 是单独的条件CPU执行环境，实际13558保存逻辑路径 R/env/core/bin/python、link text python3.11、resolved regular binary25916456B及其实际CPU SHA。软件前后及真实checker生产前后验证同一记录；二进制、site-packages、权重、参数不进入源码/归档重新分发。nested resolved_* 字段是 scalar conditional provenance，不能变成任意科学输入的live读取例外。

已执行的其他 capture/helper、默认运行manifest与旧字节归档别名仍按ERR7/8显式覆盖，保持各自独立公开目录和真实身份，不合并、不覆盖、不因加入本OWN4而漏掉先前 late provenance。

## 5. 真实恢复元数据验收需要的索引输入

完整最小关系图沿实际 A/proof 指针读取；需全部进入真实包的精确索引，并以恢复根内只读 nonsymlink bytes为权威：

- 新工具实际软件 A19295、32合同2756/日志4726、snapshot4235、原/frozen OWN4以及8149 named terminal seal。
- 已接受 Composer13377软件 A19236、130 contracts/log、精确41 SOURCE 文件及 pinned StrictIndex34228/core21981。生产仅执行当前4+StrictIndex；core package/extract只在新32合成fixtures被调用，生产checker不调用scorer、writer或科学重算入口。
- Common13460 metadata A17771、diff、transaction、readonly OLD5096 archive、NEW5157 canonical、byte-identical5157 candidate、实际 factual submit1598、accepted Cost4/Common7 software/source/log、原/frozen amendment OWN4、compile/snapshot及保存的13277/13269 CPU终态证据。
- 真实 preflight13422、未改claim三文件、其余GPU controller三文件、J5、J6及仍独立的13315修正 A；实际13460 terminal metadata seal10023及它保存的13个sealed files/raw logs。J6的四个entry与前驱0005完全相同，旧13315资格list保持，唯一新增为 separate13460资格。
- 包的config与显式resource aliases也必读indexed bytes。只有 exact newSW execution control、exact packaging_receipt、exact restore-root/RESTORE_HASH_ACCEPTANCE 是明确的数据CONTROL，另有执行CODE和条件解释器范围。newSW外部CONTROL还必须与它的indexed归档副本相同；CONTROL不能替代原INPUT。

OLD canonical5096只保留 scalar logical identity，并以实际旧archive receipt读回；NEWcanonical5157与candidate是各自实际full receipts。若其他原JSON仍含OLDcanonical receipt-shaped observation，必须使用既有精确 READONLY_BYTE_IDENTICAL_ALIAS 到 indexed旧archive；不能选择同路径的NEW5157来冒充OLD，不能引入任意“历史父”豁免或扩大已接受的有限SOURCE上下文。

J6及terminal seal自己的SHA未知时，checker只接受其准确logical path在明确manifest中**唯一**完整索引项；缺失、第二种SHA或冲突alias必须失败。它不读取live R的metadata writer/root controller/原JSON来补缺，更不会执行amendment.py或修改controller/J6。

Independent semantics：ONLY两个raw_sbatch aliases逐值等于原始raw_stdout/raw_stderr，原所有字段、value types、list order、full argv、268 indices/cap2/真实13423宇宙不变；OLDarchive与NEWcanonical/candidate独立实际bytes；metadata transaction/parent555的历史事实与accepted proof一致；恢复copy不要求同历史inode。13315的实际字段是 actual_job_id="13311"，allocation.slurm_job_id="13315"/CPU1/GPU0，不能把评估作业13311与CPU修正作业13315混同。

本元数据checker不建立成本PASS、不重算分数、不提交神经推断/GPU、不修改SOURCE。ERR8要求的全索引 frozen RAW科学重算仍由既有生产恢复步骤在拥有的CPU allocation执行。

## 6. 固定真实生产顺序与可执行 CLI

当前13558软件已通过。**下面的生产命令尚未执行，不是新的接受，也不能现在为非终态Common启动真实final package。**

所有既有报告/成本/Common/statistics/source/public/bundle/compose/package门按主指南及ERR1–8闭合，Common所有268实际terminal后仍先COST76 actual完整seal-ledger+audit，再finish；使用J6与已实际修正NEWcanonical5157/a5bb...，保留缺manifest正GPU allocation的成本。这个新工具不绕过上述门、不替代all9角色、不要求重跑已接受软件。

真实 archive流程：
1. final9role source及所有必需late SOURCE/proofs完整索引，报告QA/成本与正式Common/statistics取得实际资格，公共sole-baseline-parent/full tree/private bundle与读回资格通过。
2. actual composition与package通过既有严格API。保留实际packaging_receipt完整tuple及其SHA。
3. 执行 unchanged core.extract 到一个新的、隔离恢复根。其marker status仍为 RESTORED_HASHES_VERIFIED_CONTENT_RECOMPUTATION_PENDING；hash-only不是科学恢复PASS。
4. 运行已有实际Composer13377/130源码的wrapper.restore：完整indexed RAW budget/Common/statistics重算与输入readonly seal，取得实际内容+终态资格。软件A13377本身不是这一步真实接受。
5. **只有上述真实full restored科学验收通过后**，root从13558实际 frozen launcher分配新的 organ纯CPU1/GPU0 metadata job，指向同一exactpackage和restore root，输出一个此前不存在的恢复根内目录。

实际冻结入口已存在，生产路由如下；只替换尚不存在的package/root/output占位符与实际package SHA，不能猜未来hash或复用已存在输出：

```sh
sbatch --parsable \
  /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/restored_common13460_metadata_verifier_v1_13558/code/checker_cpu.sbatch \
  verify \
  /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/restored_common13460_metadata_verifier_v1_13558/code/checker.py \
  --software /lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/restored_common13460_metadata_software_13558/acceptance.json \
  --software-sha 46961d96044333116e7dd829d364533be1d5815c147fa0df7819ffcd3baee5d7 \
  --package ACTUAL_PACKAGING_RECEIPT_ABSOLUTE_PATH \
  --package-sha ACTUAL_OWNED_CPU_PACKAGE_SHA \
  --restore-root ACTUAL_READONLY_FULL_RAW_VERIFIED_RESTORE_ROOT \
  --out ACTUAL_RESTORE_ROOT/NEW_ABSENT_METADATA_OUTPUT
```

此source-qualified launcher用明确 CORE interpreter调用0444 .py，不直接exec该 .py。jobname精确 test9_restored_common13460_metadata，organ/account u21111210118/qosnormal，CPU1/8G/GPU0/原10min；emptyCUDA/JAXcpu、PYTHONNOUSERSITE、PYTHONDONTWRITEBYTECODE、BLAS/OMP/MKL1、unsetPYTHONPATH。contracts-only分支才创建live TMPDIR；verify仅调用实际qualified frozen entry，不bootstrap pending、不写live S/frozen/S/runs/S/tmp。Slurm固定stdout/stderr是当前allocation stream metadata，不能成为INPUT读回例外。仅当前cpu()读取live scheduler；所有历史软件/13460终态从已indexed saved evidence读回。

真实proof输出仅经 StrictIndex OUTPUT mkdir/open/rec：指定root的absent contained descendant，acceptance target先注册再保存fresh_output_paths，close时flush/fsync/0444；绝不提升OUTPUT为INPUT。执行前后验证conditional CORE；末尾重读所读全部metadata/source索引与controls/executors，权限或bytes drift须失败。缺任何index证据时不得用live root rescue。

## 7. 真实checker结果与 ACTIVE fence

尚无真实checker生产内容receipt。本提案不能创建或宣称它。

未来真正成功的schema/status应为：
restored-common13460-metadata-content.v1 /
RESTORED_COMMON13460_AND_J6_EXACT_INDEX_METADATA_CONTENT_ACCEPTED_NOT_SCIENCE。

实际receipt将记录生产CPU job/allocation、13558 software execution control、indexed saved software terminal、package/extraction control、conditionalCORE、required indexed INPUT read proof与registered OUTPUT路径、13460/J6/OLD/NEW/CAND独立关系。root必须读实际CPU stdout打印的own tuple及完整内容、fresh actual terminal，不能只看exit0或布尔字段。scope始终 RESTORED_METADATA_ONLY_NOT_SCIENCE_COST_PUBLICATION_OR_ACTIVE；production_restore_verified只指本checker的真实metadata内容通过，不表示scientific_recomputation_performed=true。

该content receipt是 LATE POSTARCHIVE 输出。保留到最终交付的独立实际证据/ACTIVE fence；**不能把它回填为创建同一个source/report/包的前置输入，不能为了把它包含在已验收包里再覆盖原manifest或制造接受循环。** root最终 ACTIVE-last须同时拥有真实完整科学恢复及此新独立元数据内容验收；既有source/Git/public/private/cost门全部保持。

## 8. 本提案的权限与安装

Root在2026-10-12T12:30:33.439776+00:00将本独立mandatory ERRATUM9安装为只读人工指南，依据root全文读回与common_review_readiness独立HUMAN_READBACK_PASS。原17070B提案保留；主指南/ERR1–8及所有history原文保持。安装元数据见steps/24_benchmark_delivery/submissions/operator_erratum9_actual13558_root_install_metadata/receipt.json。人工指南不替代软件、真实恢复或科学接受，不发布source、不更新ACTIVE、不提交作业。

Common13423仍非全268终态；整链继续INCOMPLETE。此时有用的实际进展是13558新软件与8149 terminal seal已闭合，可成为后续final tools SOURCE/index输入；真实metadata restore、RAW scientific restore、COST/Common finish/report/publication等只可按各自实际门与未来CPU内容记录判定。
