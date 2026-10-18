import shutil
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,atomic_json
root=Path("/lustre/users/u21111210118/projects/test9")
extended=root/"steps/12_extended_qualification/runs/20260922T040335Z_5b613065df6e/outputs/qualification.json"
context=root/"steps/16_context_inventory/runs/20260922T043634Z_f52393777f19/outputs/qualification.json"
run=Run(root,"23_benchmark_report",[record_file(extended),record_file(context)])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 cases=read_json(extended)["cases"];cx={x["case_id"]:x for x in read_json(context)["cases"]}
 assert len(cases)==50 and len(cx)==32
 lines=["# 50 项测试矩阵执行与适用范围裁决","","48 个候选蛋白对与 2 个身份哨兵逐项保留。此处的未通过表示当前入口/背景支持不满足，不代表生物学上不互作。","",
 "C0/C1 进行了扩大上限的有界结构检索；C2 另外实际检查了候选坐标，仍非所有 PDB 的穷尽审查。P06/P09 是开发集的孤立结构域-短肽构建体，不能作为跨类型留出验证。",
 "","|ID|蛋白对|原矩阵类型|扩大检索状态|背景坐标复查|当前裁决|","|---|---|---|---|---|---|"]
 rows=[]
 for c in cases:
  cid=c["case_id"]
  final=("开发回归，非新增独立测试" if cid=="P01" else
   "开发构建体：RF/BoltzGen/motif已执行" if cid in ["P06","P09"] else
   "排除主比较：S63T序列差异+NMR约束对接；保留历史挑战结果" if cid=="P32" else
   "未放行：结构性Zn不可因坐标缺失而忽略" if cid=="P14" else
   "身份拒绝哨兵" if cid.startswith("Q") else "当前未合格；需构建体或背景支持")
  state=cx[cid]["status"] if cid in cx else "不适用此轮C2复查"
  rows.append(dict(case_id=cid,reference_gate=c["status"],context_gate=state,adjudication=final,background=c["background"]))
  lines.append(f"|{cid}|{c['target']}–{c['partner']}|{c['background']}|{c['status']}|{state}|{final}|")
 lines+=["","原定 6 靶标 × 4 生成器 × 2 种子 × 64 候选仍未达到资格门槛，不能用32条开发/挑战序列替代该主 benchmark。",
 "未完成的适用范围包括必需金属/辅因子、翻译后修饰、多蛋白背景、膜与糖链、核酸背景和生理多价性。未使用删掉背景组分、放松物种或替代成近亲序列的方法补足样本数。"]
 md=run.path/"outputs/50项测试矩阵执行状态.md";md.write_text("\n".join(lines)+"\n");run.output("report",md)
 js=run.path/"outputs/adjudication.json";atomic_json(js,rows);run.output("adjudication",js)
 print(run.finish("FULL_MATRIX_ADJUDICATED","scope_audit"),flush=True)
except Exception as e:run.fail(e);raise

