import shutil
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,atomic_json
root=Path("/lustre/users/u21111210118/projects/test9")
summary=root/"steps/23_benchmark_report/runs/20260922T052344Z_6cb1d7733a0a/outputs/summary.json"
run=Run(root,"23_benchmark_report",[record_file(summary)]);shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 rows=[]
 for row in read_json(summary)["pools"]:
  dm=Path(row["design_manifest"]["path"]);m=read_json(dm)
  source=dm.parent if len(m["inputs"])==1 else Path(m["inputs"][1]["path"]).parent.parent
  gen=list((source/"logs").glob("*.resources.json"))
  reuse=source/"qc/reused_rfd.json"
  if reuse.exists():gen.append(Path(read_json(reuse)["source_manifest"]["path"]).parent/"logs/rfd.resources.json")
  refs=list((Path(row["evaluation_manifest"]["path"]).parent/"logs").glob("*.resources.json"))
  def seconds(paths):return sum(read_json(p)["wall_seconds"] for p in paths if read_json(p)["status"]=="COMPLETE")
  rows.append(dict(case=row["case"],method=row["method"],generation_seconds=seconds(gen),refold_seconds=seconds(refs),
    generation_receipts=[record_file(p) for p in gen],refold_receipts=[record_file(p) for p in refs],
    semantics="Successful backend command wall time; one allocated GPU per job. Startup/provenance IO, scheduler wait, native-pose inference and failed retries excluded. No isolated GPU utilization or peak VRAM measurement."))
 out=run.path/"outputs/costs.json";atomic_json(out,rows);run.output("costs",out)
 print([(x["case"],x["method"],round(x["generation_seconds"]),round(x["refold_seconds"])) for x in rows],flush=True)
 print(run.finish("MODEL_COMMAND_COSTS_COMPLETE","resource_measurement"),flush=True)
except Exception as e:run.fail(e);raise

