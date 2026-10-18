import os,sys,json
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
sys.path.insert(0,str(R/"source/rebuild"))
from benchmark_common_review import cpu,allocation
from screening_transfer import dump,rec
cpu();rows=[]
for p in sorted(Path("/proc/driver/nvidia/gpus").glob("*/information")):
    try:rows.append(dict(path=str(p),status="READABLE_DRIVER_PHYSICAL_INFORMATION",text=p.read_text()))
    except (PermissionError,OSError) as e:rows.append(dict(path=str(p),status="INFORMATION_UNAVAILABLE",reason=str(e)))
out=R/"steps/23_common_review/inputs"/("proc_gpu_inventory_"+os.environ["SLURM_JOB_ID"]+".json")
dump(out,dict(status="CPU0_PROC_DRIVER_PHYSICAL_INFORMATION" if rows else "CPU0_PROC_DRIVER_INFORMATION_UNAVAILABLE",allocation=allocation(0),rows=rows,source=rec(__file__),GPU_inference_performed=False))
print(json.dumps(dict(receipt=rec(out),rows=rows),indent=2),flush=True)

