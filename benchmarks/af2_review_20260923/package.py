import shutil,sys,re
from pathlib import Path
from ppiblocker.common import *
root=Path("/lustre/users/u21111210118/projects/test9");run=Run(root,"78_af2_review_delivery",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 p=Path(sys.argv[1]);m=read_json(p)
 require(m["status"]=="AF2_REVIEW_DIAGNOSTIC_COMPLETE","REPORT_STATUS",str(p))
 require(m["entries"]==13 and m["expanded_models"]==195 and m["baseline_models"]==39,"COMPLETENESS_COUNTS",str(p))
 report=verify_file(m["outputs"]["report"]);summary=verify_file(m["outputs"]["summary"])
 directory=root/"reports/af2_review_20260923";directory.mkdir(exist_ok=True)
 docs=[(report,"AF2_复核改进与结果.md"),(root/"source/benchmarks/af2_review_20260923/METHODS.md","方法与文献依据.md")]
 files=[]
 for src,name in docs:
  dest=directory/name;shutil.copy2(src,dest);require(digest(dest)==digest(src),"MIRROR_CHECK",str(dest));files.append(record_file(dest));run.output(name,dest)
 commit_file=root/"steps/78_af2_review_delivery/source_commit.txt"
 commit=commit_file.read_text().strip()
 require(re.fullmatch("[0-9a-f]{40}",commit) is not None,"COMMIT_RECEIPT",commit)
 lines=["# AF2 复核 v2：复现与验收索引","","执行ID：AF2-REVIEW-V2-20260923。版本：1.0。","",f"权威目录：fudan:{root}",f"交付时源码提交：{commit}；未推送GitHub。","",
 "121 项测试通过；日志 steps/73_af2_review_setup/mpnn_186358.log。","13/13 项推断完成；195 个扩展模型与39个旧方案模型，合计234个模型。",f'松弛技术失败：{m["relaxation_failures"]}。计算完成不等于所有模型通过几何/置信度判定。',"",
 f"报告 manifest：{p}",f"报告 manifest SHA-256：{digest(p)}",f"逐项统计：{summary}","",
 "输入与源码冻结：steps/73_af2_review_setup/runs/20260923T092849Z_a3695ac8dc12/manifest.json。",
 "输入身份、MSA 复用、ipSAE 提交及源码哈希均在该 manifest 和输出凭据中。",
 "OpenMM兼容和ipSAE验收：steps/76_af2_review_smoke/runs/20260923T093955Z_ff9c62d39b02/manifest.json。",
 "旧失败的smoke记录保留；重试解决了地址空间限制、OpenMM单位接口和MPNN前后序列对应问题。",
 "",
 "## 人类可读文件哈希",""]
 for item in files:lines.append(f'- {Path(item["path"]).name}: {item["sha256"]}')
 index=directory/"复现与验收索引.md";index.write_text("\n".join(lines)+"\n");run.output("index",index)
 run.manifest["inputs"]=[record_file(p),record_file(commit_file)];run.save()
 print(run.finish("AF2_REVIEW_DELIVERY_VERIFIED","computational_only"),flush=True)
except Exception as e:run.fail(e);raise

