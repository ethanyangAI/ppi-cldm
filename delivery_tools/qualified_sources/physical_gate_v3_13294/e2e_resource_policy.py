"""Independent engineering resource contract; reuses accepted budget-v4 ownership."""
import importlib.util, json, math, os, re, subprocess
from pathlib import Path
BUDGET=dict(path="/lustre/users/u21111210118/projects/test9/steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py",
            bytes=84446,sha256="b37227bd862ee1425a59f5308be1ee3f4824042dea5d71c1269ad0f406b318f9")
POLICY=dict(schema="reference_free_e2e_resources.v1",scheduler_CPUs=3,GPU_count=1,
            requested_memory_GiB=64,OMP_NUM_THREADS=4,GPU_name="NVIDIA A100-PCIE-40GB",GPU_memory_MiB=40960,
            all_wall_costs_outside_formal_benchmark=True,cpu_cgroup_isolation="UNOBSERVED",
            actual_memory_when_omitted_from_AllocTRES="UNAVAILABLE_NOT_ZERO")

def load_guard():
    spec=importlib.util.spec_from_file_location("e2e_reused_accepted_budget_v4",BUDGET["path"])
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def validate_owned_record(owned,environment,created_epoch):
    g=load_guard()
    env=dict(environment)
    sched=g.select_scheduler_record(owned["scheduler_record"],raw_job_id=env["SLURM_JOB_ID"])
    if sched!=owned["selected_scheduler_record"]:raise ValueError("Guard selected scheduler record changed")
    identity=g.scheduler_allocation_identity(sched,env=env)
    tres=g.validate_scheduler_gpu_allocation(sched,1)
    if tres!=owned["scheduler_alloc_tres"]:raise ValueError("Owned allocated TRES differs")
    num=re.findall(r"\bNumCPUs=(\S+)",sched)
    entries=dict(x.split("=",1) for x in tres.split(",") if "=" in x)
    if num!=["3"] or entries.get("cpu")!="3" or env.get("SLURM_CPUS_PER_TASK")!="3":
        raise ValueError("Actual CPU allocation must be 3, not only a request")
    requested=re.findall(r"\bMinMemoryNode=(\S+)",sched)
    if requested not in [["64G"],["65536M"],["65536"]]:raise ValueError("Frozen engineering request memory must be 64GiB")
    if env.get("OMP_NUM_THREADS")!="4":raise ValueError("Frozen engineering OMP literal must remain 4")
    if g.allocation_anchor(sched)<math.floor(created_epoch):raise ValueError("Allocation started before engineering policy freeze")
    hw=owned["hardware"];selected=hw["gpus"]
    if len(selected)!=1 or selected[0]["name"]!=POLICY["GPU_name"] or selected[0]["memory_total_mib"]!=40960:
        raise ValueError("Actual owned engineering GPU hardware differs")
    if owned["child_cuda_visible_devices"]!=selected[0]["uuid"] or owned["owned_gpu_uuids"]!=[selected[0]["uuid"]]:
        raise ValueError("Child GPU identity not exact owned physical UUID")
    derived,remapping=g.derive_child_gpu_visibility(selected,hw["assignment_environment"])
    if derived!=owned["child_cuda_visible_devices"]:raise ValueError("Original assignment and child CUDA UUID disagree")
    return dict(policy=POLICY,actual_allocation_identity=identity,selected_scheduler_record=sched,
                allocated_CPU_count=3,allocated_GPU_count=1,scheduler_AllocTRES=tres,
                actual_memory_AllocTRES=entries.get("mem","UNAVAILABLE_NOT_ZERO"),
                requested_MinMemoryNode=requested[0],allocation_start_epoch=g.allocation_anchor(sched),
                owned_GPU_UUID=selected[0]["uuid"],owned_GPU_physical_minor=selected[0]["device_minor"],
                GPU_name=selected[0]["name"],GPU_memory_MiB=selected[0]["memory_total_mib"],
                canonical_child_CUDA_VISIBLE_DEVICES=derived,cuda_remapping=remapping,
                CPU_cgroup_isolation="UNOBSERVED")

def child_backend_environment(original):
    return {**original,"OMP_NUM_THREADS":"4"}

def model_guard(component,root,backend_environment,created_epoch):
    owned=load_guard().gpu_ownership_guard(expected_count=1,expected_gpu_name=POLICY["GPU_name"],env=dict(os.environ))
    evidence=validate_owned_record(owned,dict(os.environ),created_epoch)
    os.environ["CUDA_VISIBLE_DEVICES"]=owned["child_cuda_visible_devices"]
    env=backend_environment(root,component)
    if env.get("CUDA_VISIBLE_DEVICES")!=owned["child_cuda_visible_devices"] or env.get("OMP_NUM_THREADS")!="4":
        raise ValueError("Backend child resource or GPU identity override")
    script='import json,torch; n=torch.cuda.device_count(); assert n==1,("actual child visible count",n); p=torch.cuda.get_device_properties(0); assert p.name=="NVIDIA A100-PCIE-40GB",p.name; print(json.dumps(dict(actual_visible_GPU_count=n,name=p.name,memory_MiB=p.total_memory//(1024*1024))))'
    result=subprocess.run([str(Path(root)/"env"/component/"bin/python"),"-c",script],
                          capture_output=True,text=True,env=env,timeout=180)
    if result.returncode:raise ValueError("Actual component single-GPU probe failed: "+result.stdout+result.stderr)
    evidence.update(reused_GPU_guard_source=BUDGET,owned_guard=owned,actual_component=component,
                    child_GPU_probe=json.loads(result.stdout.strip().splitlines()[-1]),
                    probe_stdout=result.stdout,probe_stderr=result.stderr)
    return evidence
