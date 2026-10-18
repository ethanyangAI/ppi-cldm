import copy, tempfile, unittest
from pathlib import Path
import e2e_resource_policy as r
class Resources(unittest.TestCase):
    def fixture(self):
        env=dict(SLURM_JOB_ID="900",SLURM_CPUS_PER_TASK="3",OMP_NUM_THREADS="4",SLURM_JOB_GPUS="3",CUDA_VISIBLE_DEVICES="0")
        sched="JobId=900 JobState=RUNNING StartTime=2026-10-11T22:00:00 NumCPUs=3 MinMemoryNode=64G AllocTRES=cpu=3,node=1,gres/gpu=1\n"
        gpu=dict(index=0,device_minor=3,uuid="GPU-owned",name="NVIDIA A100-PCIE-40GB",memory_total_mib=40960)
        owned=dict(scheduler_record=sched,selected_scheduler_record=sched,scheduler_alloc_tres="cpu=3,node=1,gres/gpu=1",
          hardware=dict(gpus=[gpu],assignment_environment=env),owned_gpu_uuids=["GPU-owned"],child_cuda_visible_devices="GPU-owned")
        return owned,env
    def test_cpu3_minor3_local0_passes(self):
        owned,env=self.fixture();x=r.validate_owned_record(owned,env,0);self.assertEqual(x["canonical_child_CUDA_VISIBLE_DEVICES"],"GPU-owned")
    def test_CPU4_actual_rejects(self):
        owned,env=self.fixture();owned["scheduler_record"]=owned["selected_scheduler_record"]=owned["scheduler_record"].replace("NumCPUs=3","NumCPUs=4")
        with self.assertRaises(ValueError):r.validate_owned_record(owned,env,0)
    def test_GPU0_not_a_minor3_authority(self):
        owned,env=self.fixture();owned["child_cuda_visible_devices"]="GPU-other"
        with self.assertRaises(ValueError):r.validate_owned_record(owned,env,0)
    def test_pending_request_not_actual_allocation(self):
        owned,env=self.fixture();owned["scheduler_record"]=owned["selected_scheduler_record"]=owned["scheduler_record"].replace("RUNNING","PENDING")
        with self.assertRaises(ValueError):r.validate_owned_record(owned,env,0)
    def test_memory_omission_is_not_zero(self):
        owned,env=self.fixture();x=r.validate_owned_record(owned,env,0);self.assertEqual(x["actual_memory_AllocTRES"],"UNAVAILABLE_NOT_ZERO")
    def test_memory_request_changed_rejects(self):
        owned,env=self.fixture();owned["scheduler_record"]=owned["selected_scheduler_record"]=owned["scheduler_record"].replace("64G","16G")
        with self.assertRaises(ValueError):r.validate_owned_record(owned,env,0)
    def test_OMP4_retained_without_GPU_override(self):
        old=dict(OMP_NUM_THREADS="3",CUDA_VISIBLE_DEVICES="GPU-owned",SLURM_JOB_ID="900")
        new=r.child_backend_environment(old);self.assertEqual(new["OMP_NUM_THREADS"],"4");self.assertEqual(new["CUDA_VISIBLE_DEVICES"],old["CUDA_VISIBLE_DEVICES"])
    def test_old_policy_start_rejects(self):
        owned,env=self.fixture()
        with self.assertRaises(ValueError):r.validate_owned_record(owned,env,99999999999)
    def test_multi_record_SELECT_does_not_use_first(self):
        owned,env=self.fixture();owned["scheduler_record"]="JobId=901 JobState=PENDING NumCPUs=3 AllocTRES=cpu=3,gres/gpu=1\n"+owned["scheduler_record"]
        self.assertEqual(r.validate_owned_record(owned,env,0)["actual_allocation_identity"]["raw_allocation_id"],"900")
if __name__=="__main__":unittest.main()
