from pathlib import Path
from collections import Counter
import shutil
from ppiblocker.common import *
root=Path("/lustre/users/u21111210118/projects/test9");run=Run(root,"71_roundA_completeness",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 rows=[];sources=[];cells=set()
 for p in sorted((root/"steps/43_development_refold/runs").glob("*/manifest.json")):
  m=read_json(p)
  require(m["status"]=="DEVELOPMENT_REFOLD_COMPLETE","UNFINISHED_REFOLD",str(p))
  require(m["cell_index"] not in cells,"DUPLICATE_CELL",str(p));cells.add(m["cell_index"])
  ep=verify_file(m["outputs"]["evaluation_manifest"]);e=read_json(ep)
  require(e["status"]=="EVALUATION_COMPLETE","INCOMPLETE_EVALUATION",str(ep))
  v=read_json(verify_file(e["outputs"]["evaluation"]));c=v["candidates"]
  require(len(c)==16,"COUNT",str(ep));sources.extend([record_file(p),record_file(ep)])
  rows.append(dict(cell=m["cell_index"],target=m["case"],condition=m["condition"],seed=m["seed"],total=len(c),status_counts=dict(Counter(x["status"] for x in c)),sample_count=sum(len(x["models"]) for x in c),evaluation=record_file(ep)))
 require(cells==set(range(16)),"CELL_COVERAGE",str(cells))
 run.manifest["inputs"]=sources;run.save()
 atomic_json(run.path/"outputs/summary.json",rows);run.output("summary",run.path/"outputs/summary.json")
 lines=["# 第一轮生成与回折完整性核验","","256 条候选、16 个批次全部完成；沿用原定门槛，未根据结果调整。通过计算门槛不等于实验阻断。","","|靶标|条件|种子|候选数|计算门槛通过|技术失败|","|---|---|---|---|---|---|"]
 for x in sorted(rows,key=lambda x:x["cell"]):lines.append(f'|{x["target"]}|{x["condition"]}|{x["seed"]}|{x["total"]}|{x["status_counts"].get("COMPUTATIONAL_COMPETITION_CANDIDATE",0)}|{x["status_counts"].get("EVALUATION_FAILED",0)}|')
 p=run.path/"outputs/report.md";p.write_text("\n".join(lines)+"\n");run.output("report",p)
 print(run.finish("ROUND_A_ALL_256_REFOLDS_VERIFIED","computational_only",dict(candidates=256,models=sum(x["sample_count"] for x in rows),passing_candidates=sum(x["status_counts"].get("COMPUTATIONAL_COMPETITION_CANDIDATE",0) for x in rows))),flush=True)
except Exception as e:run.fail(e);raise

