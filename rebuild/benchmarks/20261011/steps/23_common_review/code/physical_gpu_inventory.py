import os,sys,subprocess,json
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
sys.path.insert(0,str(R/"source/rebuild"))
from benchmark_common_review import cpu,allocation
from screening_transfer import dump,rec
cpu()
cmd=["nvidia-smi","--query-gpu=index,name,memory.total,uuid,driver_version","--format=csv,noheader,nounits"]
p=subprocess.run(cmd,capture_output=True,text=True)
g=[]
if p.returncode==0:
    for line in p.stdout.strip().splitlines():
        v=[s.strip() for s in line.split(",")]
        if len(v)!=5:raise ValueError("Malformed physical inventory")
        g.append(dict(index=int(v[0]),name=v[1],memory_total_mib=int(v[2]),uuid=v[3],driver_version=v[4]))
out=R/"steps/23_common_review/inputs"/("physical_gpu_inventory_"+os.environ["SLURM_JOB_ID"]+".json")
dump(out,dict(status="CPU0_ALLOCATION_READ_ONLY_NVML_PHYSICAL_INVENTORY" if g else "CPU0_NVML_PHYSICAL_INVENTORY_UNAVAILABLE",allocation=allocation(0),argv=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,physical_gpus=g,source=rec(__file__),GPU_inference_performed=False))
print(json.dumps(dict(receipt=rec(out),gpus=g,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr),indent=2),flush=True)

