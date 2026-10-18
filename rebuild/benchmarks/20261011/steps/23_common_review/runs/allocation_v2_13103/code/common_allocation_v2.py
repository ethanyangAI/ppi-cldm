#!/usr/bin/env python3
"""Technical-only allocation correction for immutable common-review science."""
import importlib.util,json,os,re,subprocess,sys
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
COMMON=R/"steps/23_common_review/frozen/native_common_13051/code/benchmark_common_review.py"
GUARD=R/"steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py"
def guard_module():
    spec=importlib.util.spec_from_file_location("common_scheduler_guard_v4",GUARD)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def scheduler_receipt(text,expected_gpu,environment):
    g=guard_module();job=environment.get("SLURM_JOB_ID")
    if not job:raise RuntimeError("Production common review requires actual Slurm allocation")
    logical=None
    if environment.get("SLURM_ARRAY_JOB_ID") is not None or environment.get("SLURM_ARRAY_TASK_ID") is not None:
        if not environment.get("SLURM_ARRAY_JOB_ID") or environment.get("SLURM_ARRAY_TASK_ID") is None:raise ValueError("Incomplete invoking array identity")
        logical=environment["SLURM_ARRAY_JOB_ID"]+"_"+environment["SLURM_ARRAY_TASK_ID"]
    selected=g.select_scheduler_record(text,raw_job_id=job,logical_key=logical)
    identity=g.scheduler_allocation_identity(selected,logical_key=logical,env=environment)
    tres=g.validate_scheduler_gpu_allocation(selected,expected_gpu)
    return dict(job_id=job,expected_gpu=expected_gpu,allocated_gpu_count=expected_gpu,
                scheduler_record=selected,scheduler_record_full=text,selected_scheduler_record=selected,
                scheduler_alloc_tres=tres,raw_allocation_identity=identity,
                technical_scope="UNIQUE_INVOKING_SCHEDULER_RECORD_ONLY_SCIENTIFIC_SETTINGS_UNCHANGED")
def allocation(expected_gpu):
    env=dict(os.environ);job=env.get("SLURM_JOB_ID")
    if not job:raise RuntimeError("Production common review requires actual Slurm allocation")
    pr=subprocess.run(["scontrol","show","job",job,"-o"],capture_output=True,text=True,check=True)
    result=scheduler_receipt(pr.stdout,expected_gpu,env)
    if expected_gpu==1:
        owned=guard_module().gpu_ownership_guard(expected_count=1,expected_gpu_name="NVIDIA A100-PCIE-40GB",env=env)
        if owned["selected_scheduler_record"].strip()!=result["selected_scheduler_record"].strip():raise ValueError("Independent scheduler/ownership selection mismatch")
        os.environ["CUDA_VISIBLE_DEVICES"]=owned["child_cuda_visible_devices"]
        result["owned_gpu_guard"]=owned
    context=Path(__file__).with_name("wrapper_receipts.json")
    if context.exists():result["technical_reference_receipts"]=json.loads(context.read_text())
    return result
def main():
    sys.path.insert(0,str(COMMON.parent))
    import benchmark_common_review as scientific
    scientific.allocation=allocation
    # Every scientific function, SETTINGS and job_signature is the immutable original.
    scientific.main()
if __name__=="__main__":main()
