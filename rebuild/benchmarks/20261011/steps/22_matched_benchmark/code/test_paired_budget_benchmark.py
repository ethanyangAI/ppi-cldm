#!/usr/bin/env python3
"""CPU contract tests using synthetic bookkeeping fixtures, no model inference."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path("/lustre/users/u21111210118/projects/test9")
spec = importlib.util.spec_from_file_location("paired_budget", ROOT / "source/rebuild/paired_budget_benchmark.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def dump(path, value):
    Path(path).write_text(json.dumps(value) + "\n")
    return m.record(path)

def protocol(root, targets=1):
    input_receipt = dump(root / "input.json", {"fixture": True})
    adapter_receipt = dump(root / "adapter.json", {"fixture": True})
    return {"schema": m.SCHEMA, "protocol_id": "engineering-fixture",
        "scientific_scope": "COMPUTATIONAL_ONLY", "execution_mode": "persistent_session",
        "targets": [{"target_id": "target" + str(i), "input_manifest": input_receipt,
                     "analysis_role": "primary"} for i in range(targets)],
        "methods": [{"method_id": method, "argv": [sys.executable, "{attempt_dir}/adapter.py"],
                     "session_start": [sys.executable, "{session_dir}/adapter.py"],
                     "adapter_receipts": [adapter_receipt], "config_receipt": adapter_receipt, "native_score_name": "native",
                     "native_score_direction": "higher"} for method in ("methodA", "methodB")],
        "replicate_seeds": [17, 29], "gpu_count": 1, "budget_gpu_seconds": 3600,
        "shutdown_reserve_seconds": 10, "accounting_tolerance_seconds": 2,
        "hardware": {"gpu_name": "FAKE_GPU_CPU_UNIT_TEST"},
        "sampling": {"salt": "frozen-before-fixture-results", "uniform_n_per_replicate": 2,
                     "native_top_k_per_replicate": 1},
        "inference": {"minimum_targets": 6, "bootstrap_replicates": 2000, "bootstrap_seed": 4142}}

def plan(root, targets=1):
    p = protocol(root, targets)
    return {"schema": m.SCHEMA, "status": "FROZEN_BEFORE_GENERATION", "protocol": p,
            "protocol_receipt": dump(root / "protocol.json", p), "orchestrator": m.record(m.SELF),
            "tasks": m.make_tasks(p)}


def hardware_fixture():
    inventory=[{"index":i,"uuid":"GPU-"+str(i),"name":"FAKE_GPU_CPU_UNIT_TEST","memory_total_mib":1} for i in range(4)]
    physical=[{"device_minor":i,"uuid":"GPU-"+str(i),"name":"FAKE_GPU_CPU_UNIT_TEST",
               "path":"/proc/driver/nvidia/gpus/fixture"+str(i)+"/information",
               "information":"Model: FAKE_GPU_CPU_UNIT_TEST\nGPU UUID: GPU-"+str(i)+"\nDevice Minor: "+str(i)+"\n"} for i in range(4)]
    return {"gpus":[dict(inventory[3],device_minor=3)],"nvml_inventory":inventory,"physical_inventory":physical,
        "stdout":"".join(str(i)+", FAKE_GPU_CPU_UNIT_TEST, 1, GPU-"+str(i)+"\n" for i in range(4)),
        "assignment_environment":{"SLURM_JOB_GPUS":"3","SLURM_STEP_GPUS":None,"CUDA_VISIBLE_DEVICES":"0"},
        "selection_basis":"SLURM_JOB_GPUS","owned_gpu_uuids":["GPU-3"],"child_cuda_visible_devices":"GPU-3",
        "cuda_visibility_remapping":{"original_cuda_visible_devices":"0","interpretation":"LOCAL_INDICES_REMAPPED_TO_OWNED_UUID",
            "owned_gpu_uuids":["GPU-3"],"derived_child_cuda_visible_devices":"GPU-3"}}

def fixture_run(root, task, events=None, statuses=None, job="123_0", status=None, raw_id=None):
    out = root / job
    out.mkdir()
    events = [] if events is None else events
    statuses = ["SCIENTIFIC_REJECT"] if statuses is None else statuses
    attempts = [{"task_id": task["task_id"], "attempt_index": i, "status": value,
                 "complete_sequence_records": sum(x["attempt_index"] == i for x in events),
                 "precutoff_sequence_records": sum(x["attempt_index"] == i and x["observed_before_generation_cutoff"] for x in events)}
                for i, value in enumerate(statuses)]
    attempt_path, sequence_path = out / "attempts.jsonl", out / "sequences.jsonl"
    for pth, rows in ((attempt_path, attempts), (sequence_path, events)):
        pth.write_text("".join(json.dumps(row) + "\n" for row in rows))
    run = {"task": task, "allocation_key": job, "attempt_count": len(attempts),
           "status": status or "BUDGET_EXHAUSTED_WITH_EXPLICIT_BOUNDARY_CENSORING",
           "hardware": hardware_fixture(),
           "attempt_ledger": m.record(attempt_path), "sequence_ledger": m.record(sequence_path),
           "allocation_started_at_epoch": 1000, "generation_cutoff_epoch": 4590,
           "allocation_deadline_epoch": 4600, "technical_rerun_of": None}
    run["child_cuda_visible_devices"]="GPU-3"
    run["gpu_ownership_status"]="RUNNING_SLURM_GPU_OWNERSHIP_VERIFIED"
    run["scheduler_alloc_tres"]="cpu=1,gres/gpu=1"
    run["scheduler_start"]=dump(out/"scheduler.json",{"fixture":True})
    actual_id = str(raw_id) if raw_id is not None else fixture_physical_id(job)
    array = "" if "_" not in job else " ArrayJobId="+job.split("_")[0]+" ArrayTaskId="+job.split("_")[1]
    Path(run["scheduler_start"]["path"]).write_text("JobId="+actual_id+array+" JobState=RUNNING StartTime=1970-01-01T00:16:40+00:00 AllocTRES=cpu=1,gres/gpu=1\n")
    run["scheduler_start"]=m.record(run["scheduler_start"]["path"])
    run["initial_receipt"]=dump(out/"initial.json",{k:run[k] for k in ["hardware","child_cuda_visible_devices","gpu_ownership_status","scheduler_alloc_tres","scheduler_start"]})
    return dump(out / "run_receipt.json", run)

def event(task, seq="ACD", index=0, acceptance=False, score=0.8, before=True):
    return m.normalize_sequence_record({"sequence": seq, "lineage_id": "lineage-" + str(index),
        "internal_acceptance": acceptance, "native_score": score, "native_score_name": "native",
        "completed_at_epoch": 1000}, task, index, 1, 1001, before)

def fixture_physical_id(job):
    logical, dot, step = job.partition(".")
    if "_" in logical:
        master, index = logical.split("_")
        actual = str(int(master) * 1000 + int(index) + 1)
    else:
        actual = logical
    return actual + (dot + step if dot else "")

def sacct(job="123_0", elapsed=3600, gpu="gres/gpu=1", state="COMPLETED", raw_id=None, include_alias=True):
    raw = fixture_physical_id(job) if raw_id is None else str(raw_id)
    fields=[raw]
    if include_alias:fields.append(job)
    fields.extend([str(elapsed), gpu, state, "1970-01-01T00:16:40+00:00", "1970-01-01T01:16:40+00:00", "node", "organ"])
    return "|".join(fields) + "\n"


def fixture_session(run_receipt, frozen_plan_path, frozen_plan):
    """Synthetic immutable RPC provenance for the independent audit fixture."""
    run=m.read_json(run_receipt["path"]); p=frozen_plan["protocol"]; task=run["task"]
    method=next(x for x in p["methods"] if x["method_id"]==task["method_id"])
    target=next(x for x in p["targets"] if x["target_id"]==task["target_id"])
    session_dir=Path(run_receipt["path"]).parent/"session"; session_dir.mkdir()
    stdout,stderr=session_dir/"stdout.log",session_dir/"stderr.log"; stdout.touch(); stderr.touch()
    expected={"protocol_sha256":frozen_plan["protocol_receipt"]["sha256"],"plan_sha256":m.sha_file(frozen_plan_path),
        "method_config_sha256":method["config_receipt"]["sha256"],"method_definition_sha256":m.digest(method),
        "target_manifest_sha256":target["input_manifest"]["sha256"]}
    fields=dict(expected,session_dir=str(session_dir),target_manifest=target["input_manifest"]["path"],
        target_id=task["target_id"],method_id=task["method_id"],task_id=task["task_id"],protocol_id=p["protocol_id"],
        generation_deadline_epoch=str(run["generation_cutoff_epoch"]),allocation_deadline_epoch=str(run["allocation_deadline_epoch"]),
        method_config=method["config_receipt"]["path"])
    run["plan"]=m.record(frozen_plan_path); run["execution_mode"]="persistent_session"
    run["session"]={"schema":"paired-budget-session-v1","pid":43210,"argv":[x.format_map(fields) for x in method["session_start"]],
        "started_at_epoch":1000,"ended_at_epoch":4590,"stdout":m.record(stdout),"stderr":m.record(stderr),
        "ready":dump(session_dir/"READY.json",dict(expected,schema="paired-budget-session-v1",status="READY",pid=43210))}
    attempts=m.rows_jsonl(run["attempt_ledger"]["path"])
    for attempt in attempts:
        index=attempt["attempt_index"]; out=session_dir/("attempt%06d"%index);out.mkdir()
        request=dict(fields,schema="paired-budget-session-v1",action="method-attempt",request_id="%06d"%index,
            attempt_index=index,attempt_dir=str(out),seed=m.attempt_seed(task,index),replicate_seed=task["seed"],
            generation_deadline_epoch=run["generation_cutoff_epoch"],deadline_epoch=run["generation_cutoff_epoch"],
            allocation_deadline_epoch=run["allocation_deadline_epoch"])
        terminal=dump(out/"attempt_result.json",{"status":attempt["status"]})
        response=dump(out/"response.json",dict(schema="paired-budget-session-v1",status="COMPLETE",
            request_id=request["request_id"],attempt_result=terminal))
        for name in ("stdout","stderr"): (out/(name+".log")).touch()
        original_events=m.rows_jsonl(run["sequence_ledger"]["path"])
        raw_events=[x for x in original_events if x["attempt_index"]==index]
        raw_path=out/"sequences.jsonl"
        raw_path.write_text("".join(json.dumps(x)+"\n" for x in raw_events))
        attempt["raw_sequence_stream"]=m.record(raw_path)
        attempt["raw_native_screening_stream"]=None
        attempt["adapter_result"]=terminal
        attempt["execution"]={"transport":"persistent_session_rpc","session_pid":43210,
            "request":dump(out/"request.json",request),"response":response,
            "stdout":m.record(out/"stdout.log"),"stderr":m.record(out/"stderr.log"),
            "session_stdout_offsets":[0,0],"session_stderr_offsets":[0,0]}
    Path(run["attempt_ledger"]["path"]).write_text("".join(json.dumps(x)+"\n" for x in attempts))
    run["attempt_ledger"]=m.record(run["attempt_ledger"]["path"])
    return dump(run_receipt["path"],run)

class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.plan = plan(self.root)
        self.task = self.plan["tasks"][0]

    def tearDown(self):
        self.tmp.cleanup()

    def test_integer_gpu_seconds_budget_and_startup_are_counted(self):
        gen, alloc = m.budget_deadlines(1000, 1200, 50, 3600, 1, 10)
        self.assertEqual((gen, alloc), (3440, 3450))
        gen, alloc = m.budget_deadlines(1000, 1200, 50, 7200, 2, 10)
        self.assertEqual((gen, alloc), (3440, 3450))

    def test_protocol_rejects_fractional_budget_and_env_override(self):
        p = self.plan["protocol"]
        p["gpu_count"] = 2
        p["budget_gpu_seconds"] = 3599
        with self.assertRaises(ValueError):
            m.validate_protocol(p, False)
        p["budget_gpu_seconds"] = 3600
        p["methods"][0]["env"] = {"CUDA_VISIBLE_DEVICES": "9"}
        with self.assertRaises(ValueError):
            m.validate_protocol(p, False)

    def test_matched_methods_share_attempt_seed(self):
        tasks = self.plan["tasks"]
        self.assertEqual(tasks[0]["pair_id"], tasks[1]["pair_id"])
        self.assertEqual(m.attempt_seed(tasks[0], 3), m.attempt_seed(tasks[1], 3))
        self.assertNotEqual(m.attempt_seed(tasks[0], 3), m.attempt_seed(tasks[0], 4))

    def test_process_group_hard_timeout(self):
        out = self.root / "process"
        out.mkdir()
        sequence_ledger = self.root / "events.jsonl"
        sequence_ledger.touch()
        stream = m.SequenceStream(out / "sequences.jsonl", sequence_ledger, self.task, 0)
        start = time.monotonic()
        execution = m.execute_attempt([sys.executable, "-c", "import time; time.sleep(10)"],
                                       dict(os.environ), out, stream, start + 0.18, 0.01)
        self.assertTrue(execution["boundary_censored"])
        self.assertLess(time.monotonic() - start, 1.0)
        self.assertEqual(m.classify_attempt(execution, None, [], [], None)[0], "TIMED_OUT_BOUNDARY")

    def test_completed_rejected_sequence_survives_timeout(self):
        out = self.root / "process"
        out.mkdir()
        sequence_ledger = self.root / "events.jsonl"
        sequence_ledger.touch()
        raw = {"sequence": "ACD", "lineage_id": "rejected-complete", "internal_acceptance": False,
               "native_score": 0.4, "native_score_name": "native", "completed_at_epoch": time.time()}
        code = "import pathlib,time; pathlib.Path('sequences.jsonl').write_text(" + repr(json.dumps(raw) + "\n") + "); time.sleep(10)"
        stream = m.SequenceStream(out / "sequences.jsonl", sequence_ledger, self.task, 0)
        execution = m.execute_attempt([sys.executable, "-c", code], dict(os.environ), out, stream,
                                       time.monotonic() + 0.25, 0.01)
        self.assertTrue(execution["boundary_censored"])
        self.assertEqual(len(stream.events), 1)
        self.assertFalse(stream.events[0]["internal_acceptance"])
        self.assertTrue(stream.events[0]["observed_before_generation_cutoff"])

    def test_incomplete_jsonl_tail_is_preserved_and_not_candidate(self):
        input_path = self.root / "sequences.jsonl"
        output_path = self.root / "events.jsonl"
        output_path.touch()
        input_path.write_text('{"sequence":')
        stream = m.SequenceStream(input_path, output_path, self.task, 0)
        stream.scan(1001, True)
        self.assertEqual(stream.events, [])
        self.assertEqual(stream.partial_tail()["bytes"], 12)


    def test_invalid_contract_at_boundary_is_not_a_scientific_budget_result(self):
        execution={"boundary_censored":True,"returncode":-9}
        self.assertEqual(m.classify_attempt(execution,None,[],[{"error":"bad original"}],None)[0],"ENGINEERING_FAILURE")
        self.assertEqual(m.classify_attempt(execution,None,[],[],{"sequence":{"bytes":4}})[0],"TIMED_OUT_BOUNDARY")

    def test_engineering_and_scientific_rejects_remain_distinct(self):
        exe = {"returncode": 0, "boundary_censored": False}
        self.assertEqual(m.classify_attempt(exe, {"status": "SCIENTIFIC_REJECT"}, [], [], None)[0], "SCIENTIFIC_REJECT")
        self.assertEqual(m.classify_attempt(exe, {"status": "COMPLETED"}, [], [], None)[0], "ENGINEERING_FAILURE")
        self.assertEqual(m.classify_attempt(dict(exe, returncode=1), {"status": "SCIENTIFIC_REJECT"}, [], [], None)[0],
                         "ENGINEERING_FAILURE")

    def test_all_attempt_denominator_includes_engineering_and_boundary(self):
        ev = [event(self.task, acceptance=True)]
        rec = fixture_run(self.root, self.task, ev,
                          ["COMPLETED", "ENGINEERING_FAILURE", "TIMED_OUT_BOUNDARY"])
        inventory, tasks = m.inventory_from_ledgers([rec])
        self.assertEqual(tasks[0]["attempt_count"], 3)
        self.assertEqual(tasks[0]["native_accepted_attempts"], 1)
        self.assertEqual(tasks[0]["attempt_status_counts"]["ENGINEERING_FAILURE"], 1)
        self.assertEqual(tasks[0]["attempt_status_counts"]["TIMED_OUT_BOUNDARY"], 1)

    def test_sequence_duplicates_preserve_lineage_and_deduplicate_inventory(self):
        ev = [event(self.task, " acd ", 0), event(self.task, "ACD", 1, True), event(self.task, "ACE", 2)]
        rec = fixture_run(self.root, self.task, ev, ["COMPLETED"] * 3)
        inventory, _ = m.inventory_from_ledgers([rec])
        self.assertEqual(len(inventory), 2)
        duplicate = next(x for x in inventory if x["sequence"] == "ACD")
        self.assertEqual(len(duplicate["occurrences"]), 2)
        self.assertEqual(len(duplicate["lineage_ids"]), 2)

    def test_invalid_sequence_cannot_enter_complete_inventory(self):
        with self.assertRaises(ValueError):
            m.normalize_sequence("ACDX")
        raw = {"sequence": "ACD", "lineage_id": "x", "internal_acceptance": "False", "completed_at_epoch": 1000}
        with self.assertRaises(ValueError):
            m.normalize_sequence_record(raw, self.task, 0, 1, 1001, True)


    def test_nvml_all_node_devices_uses_slurm_assigned_physical_gpu(self):
        hw=hardware_fixture()
        selected,assignment,basis=m.select_assigned_gpus(hw["nvml_inventory"],hw["assignment_environment"],1,hw["physical_inventory"])
        self.assertEqual([x["device_minor"] for x in selected],[3])
        self.assertEqual(basis,"SLURM_JOB_GPUS")
        child,remap=m.derive_child_gpu_visibility(selected,assignment)
        self.assertEqual(child,"GPU-3")
        self.assertEqual(remap["interpretation"],"LOCAL_INDICES_REMAPPED_TO_OWNED_UUID")

    def test_bare_cuda_uuid_and_cgroup_visibility_never_prove_ownership(self):
        hw=hardware_fixture()
        for env in [{"CUDA_VISIBLE_DEVICES":"GPU-3"},{"CUDA_VISIBLE_DEVICES":"0"},{}]:
            with self.assertRaises(ValueError):m.select_assigned_gpus(hw["nvml_inventory"],env,1,hw["physical_inventory"])

    def test_global_minor_three_matches_nvml_reindexed_zero_by_uuid(self):
        hw=hardware_fixture()
        nvml=[dict(hw["nvml_inventory"][3],index=0)]
        selected,_,_=m.select_assigned_gpus(nvml,{"SLURM_JOB_GPUS":"3"},1,hw["physical_inventory"])
        self.assertEqual(selected[0]["index"],0)
        self.assertEqual(selected[0]["device_minor"],3)
        self.assertEqual(selected[0]["uuid"],"GPU-3")
        nvml[0]["uuid"]="GPU-2"
        with self.assertRaises(ValueError):m.select_assigned_gpus(nvml,{"SLURM_JOB_GPUS":"3"},1,hw["physical_inventory"])

    def test_owned_uuid_and_consistent_step_job_ids_pass(self):
        hw=hardware_fixture()
        env={"SLURM_JOB_GPUS":"GPU-3","SLURM_STEP_GPUS":"3","CUDA_VISIBLE_DEVICES":"GPU-3"}
        selected,assignment,basis=m.select_assigned_gpus(hw["nvml_inventory"],env,1,hw["physical_inventory"])
        self.assertEqual(basis,"SLURM_STEP_GPUS")
        self.assertEqual(m.derive_child_gpu_visibility(selected,assignment)[0],"GPU-3")
        env["SLURM_STEP_GPUS"]="2"
        with self.assertRaises(ValueError):m.select_assigned_gpus(hw["nvml_inventory"],env,1,hw["physical_inventory"])

    def test_wrong_cuda_numeric_uuid_multiple_and_mixed_masks_fail(self):
        selected=hardware_fixture()["gpus"]
        for cvd in ["1","2","GPU-2","GPU-2,GPU-3","0,0","0,GPU-3","-1","all"]:
            with self.assertRaises(ValueError):m.derive_child_gpu_visibility(selected,{"CUDA_VISIBLE_DEVICES":cvd})
        for cvd in ["0","3","GPU-3",None]:
            self.assertEqual(m.derive_child_gpu_visibility(selected,{"CUDA_VISIBLE_DEVICES":cvd})[0],"GPU-3")

    def test_owned_device_counts_and_duplicate_physical_map_fail(self):
        hw=hardware_fixture()
        for text in ["0,1","9","3,3","3-2"]:
            with self.assertRaises(ValueError):m.select_assigned_gpus(hw["nvml_inventory"],{"SLURM_JOB_GPUS":text},1,hw["physical_inventory"])
        physical=hw["physical_inventory"]+[hw["physical_inventory"][0]]
        with self.assertRaises(ValueError):m.select_assigned_gpus(hw["nvml_inventory"],{"SLURM_JOB_GPUS":"3"},1,physical)
        with self.assertRaises(ValueError):m.select_assigned_gpus(hw["nvml_inventory"],{"SLURM_JOB_GPUS":"3"},1,[])

    def test_gpu_guard_requires_running_job_and_exact_model_before_probe(self):
        env={"SLURM_JOB_ID":"123","SLURM_JOB_GPUS":"3","CUDA_VISIBLE_DEVICES":"0"}
        hw=hardware_fixture()
        good="JobId=123 JobState=RUNNING AllocTRES=cpu=1,gres/gpu=1"
        with mock.patch.object(m.subprocess,"run",return_value=m.subprocess.CompletedProcess([],0,good,"")),mock.patch.object(m,"gpu_probe",return_value=hw):
            guard=m.gpu_ownership_guard(1,"FAKE_GPU_CPU_UNIT_TEST",env)
            self.assertEqual(guard["child_cuda_visible_devices"],"GPU-3")
            with self.assertRaises(ValueError):m.gpu_ownership_guard(1,"WRONG_MODEL",env)
        for record in ["JobId=123 JobState=PENDING AllocTRES=gres/gpu=1","JobId=123 JobState=RUNNING AllocTRES=cpu=1","JobId=124 JobState=RUNNING AllocTRES=gres/gpu=1"]:
            with mock.patch.object(m.subprocess,"run",return_value=m.subprocess.CompletedProcess([],0,record,"")),mock.patch.object(m,"gpu_probe")as probe:
                with self.assertRaises(ValueError):m.gpu_ownership_guard(1,"FAKE_GPU_CPU_UNIT_TEST",env)
                probe.assert_not_called()


    def test_gpu_probe_uses_proc_minor_uuid_with_reindexed_nvml(self):
        hw=hardware_fixture();raw="0, FAKE_GPU_CPU_UNIT_TEST, 1, GPU-3\n"
        env={"SLURM_JOB_GPUS":"3","CUDA_VISIBLE_DEVICES":"0"}
        with mock.patch.object(m.subprocess,"run",return_value=m.subprocess.CompletedProcess([],0,raw,"")),mock.patch.object(m,"physical_gpu_inventory",return_value=hw["physical_inventory"]):
            probe=m.gpu_probe(1,env)
        self.assertEqual(probe["gpus"][0]["index"],0)
        self.assertEqual(probe["gpus"][0]["device_minor"],3)
        self.assertEqual(probe["child_cuda_visible_devices"],"GPU-3")

    def test_independent_gpu_assignment_rejects_forged_child_visibility_and_state(self):
        spec=importlib.util.spec_from_file_location("ownership_independent",
            ROOT/"steps/22_matched_benchmark/code/paired_budget_independent.py")
        independent=importlib.util.module_from_spec(spec);spec.loader.exec_module(independent)
        receipt=fixture_run(self.root,self.task)
        run=m.read_json(receipt["path"])
        independent.audit_gpu_ownership(run,self.plan["protocol"])
        forged=json.loads(json.dumps(run));forged["child_cuda_visible_devices"]="GPU-2"
        initial=m.read_json(forged["initial_receipt"]["path"]);initial["child_cuda_visible_devices"]="GPU-2"
        forged["initial_receipt"]=dump(self.root/"forged_initial.json",initial)
        with self.assertRaises(ValueError):independent.audit_gpu_ownership(forged,self.plan["protocol"])
        scheduler=Path(run["scheduler_start"]["path"])
        scheduler.write_text(scheduler.read_text().replace("RUNNING","PENDING"))
        run["scheduler_start"]=m.record(scheduler)
        initial=m.read_json(run["initial_receipt"]["path"]);initial["scheduler_start"]=run["scheduler_start"]
        run["initial_receipt"]=dump(self.root/"pending_initial.json",initial)
        with self.assertRaises(ValueError):independent.audit_gpu_ownership(run,self.plan["protocol"])

    def test_all_scheduler_gpu_and_generated_benchmark_env_overrides_rejected(self):
        p=protocol(self.root)
        for key in ["SLURM_JOB_GPUS","SLURM_STEP_GPUS","SLURM_JOB_ID","SLURM_JOB_STATE","CUDA_VISIBLE_DEVICES","NVIDIA_VISIBLE_DEVICES","CUDA_DEVICE_ORDER","GPU_DEVICE_ORDINAL","BENCHMARK_GENERATION_DEADLINE_EPOCH"]:
            p["methods"][0]["env"]={key:"unowned"}
            with self.assertRaises(ValueError):m.validate_protocol(p,False)

    def test_multirecord_array_master_scontrol_selects_unique_task_independent_of_order(self):
        mine="JobId=13069 ArrayJobId=13069 ArrayTaskId=1 JobState=RUNNING StartTime=1970-01-01T00:16:40+00:00 AllocTRES=gres/gpu=1\n"
        sibling="JobId=13070 ArrayJobId=13069 ArrayTaskId=0 JobState=FAILED StartTime=1970-01-01T00:00:00+00:00 AllocTRES=cpu=1\n"
        for raw in [mine+sibling,sibling+mine]:
            self.assertEqual(m.select_scheduler_record(raw,raw_job_id="13069",logical_key="13069_1"),mine)
            self.assertEqual(m.scheduler_allocation_identity(raw,"13069_1")["raw_allocation_id"],"13069")
            self.assertEqual(m.allocation_anchor(m.select_scheduler_record(raw,logical_key="13069_1")),1000)
            self.assertEqual(m.validate_scheduler_gpu_allocation(m.select_scheduler_record(raw,logical_key="13069_1"),1),"gres/gpu=1")

    def test_multirecord_scontrol_gpu_guard_uses_invoking_task_not_failed_sibling(self):
        mine="JobId=13069 ArrayJobId=13069 ArrayTaskId=1 JobState=RUNNING AllocTRES=gres/gpu=1\n"
        sibling="JobId=13070 ArrayJobId=13069 ArrayTaskId=0 JobState=FAILED AllocTRES=gres/gpu=7\n"
        env={"SLURM_JOB_ID":"13069","SLURM_ARRAY_JOB_ID":"13069","SLURM_ARRAY_TASK_ID":"1"}
        for raw in [mine+sibling,sibling+mine]:
            with mock.patch.object(m.subprocess,"run",return_value=m.subprocess.CompletedProcess([],0,raw,"")),mock.patch.object(m,"gpu_probe",return_value=hardware_fixture()):
                guard=m.gpu_ownership_guard(1,"FAKE_GPU_CPU_UNIT_TEST",env)
                self.assertEqual(guard["selected_scheduler_record"],mine)
                self.assertEqual(guard["scheduler_record"],raw)
                self.assertEqual(guard["scheduler_alloc_tres"],"gres/gpu=1")

    def test_multirecord_scontrol_ambiguity_wrong_alias_and_wrong_running_sibling_fail(self):
        own="JobId=13069 ArrayJobId=13069 ArrayTaskId=1 JobState=FAILED AllocTRES=gres/gpu=1\n"
        sibling="JobId=13070 ArrayJobId=13069 ArrayTaskId=0 JobState=RUNNING AllocTRES=gres/gpu=1\n"
        for raw in [own+own,own+sibling]:
            with self.assertRaises(ValueError):m.select_scheduler_record(raw)
        for raw in [own+own,own+sibling]:
            with mock.patch.object(m.subprocess,"run",return_value=m.subprocess.CompletedProcess([],0,raw,"")),mock.patch.object(m,"gpu_probe")as probe:
                with self.assertRaises(ValueError):m.gpu_ownership_guard(1,"FAKE_GPU_CPU_UNIT_TEST",{"SLURM_JOB_ID":"13069"})
                probe.assert_not_called()
        with self.assertRaises(ValueError):m.select_scheduler_record(own+sibling,raw_job_id="13069",logical_key="13069_0")

    def test_old_run_multirecord_scheduler_preserved_and_independently_selected(self):
        rr=fixture_run(self.root,self.task,job="13069_1",raw_id="13069")
        run=m.read_json(rr["path"]);p=Path(run["scheduler_start"]["path"])
        own=p.read_text();other=own.replace("JobId=13069 ","JobId=13070 ").replace("ArrayTaskId=1 ","ArrayTaskId=0 ").replace("JobState=RUNNING","JobState=FAILED")
        p.write_text(other+own);run["scheduler_start"]=m.record(p)
        initial=m.read_json(run["initial_receipt"]["path"]);initial["scheduler_start"]=run["scheduler_start"]
        run["initial_receipt"]=dump(run["initial_receipt"]["path"],initial);rr=dump(rr["path"],run)
        before=Path(rr["path"]).read_bytes()
        result=m.independent_accounting(self.plan,[rr],sacct("13069_1",raw_id="13069",include_alias=False))
        self.assertEqual(result["tasks"][0]["raw_allocation_id"],"13069")
        self.assertEqual(Path(rr["path"]).read_bytes(),before)
        spec=importlib.util.spec_from_file_location("independent_multirecord",ROOT/"steps/22_matched_benchmark/code/paired_budget_independent.py")
        ind=importlib.util.module_from_spec(spec);spec.loader.exec_module(ind)
        self.assertEqual(ind.allocation_identity(run)["raw_allocation_id"],"13069")
        ind.audit_gpu_ownership(run,self.plan["protocol"])
        run["scheduler_selected_record"]=other
        with self.assertRaises(ValueError):ind.allocation_identity(run)

    def test_original_scheduler_resolves_physical_array_id_and_environment(self):
        text="JobId=13070 ArrayJobId=13069 ArrayTaskId=0 JobState=RUNNING"
        expected={"raw_allocation_id":"13070","logical_allocation_key":"13069_0",
                  "array_job_id":"13069","array_task_id":"0"}
        self.assertEqual(m.scheduler_allocation_identity(text,"13069_0"),expected)
        self.assertEqual(m.scheduler_allocation_identity(text,"13069_0",{
            "SLURM_JOB_ID":"13070","SLURM_ARRAY_JOB_ID":"13069","SLURM_ARRAY_TASK_ID":"0"}),expected)
        for bad in ["JobId=13070 ArrayJobId=13069", "JobId=13070 ArrayTaskId=0",
                    "JobId=13069_0", "JobId=13070 JobId=13071", "JobId=13070 ArrayJobId=13069 ArrayTaskId=[0-1]"]:
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                m.scheduler_allocation_identity(bad)
        with self.assertRaises(ValueError):
            m.scheduler_allocation_identity(text,"13069_1")
        with self.assertRaises(ValueError):
            m.scheduler_allocation_identity(text,"13069_0",{"SLURM_JOB_ID":"13069"})
        with self.assertRaises(ValueError):
            m.scheduler_allocation_identity(text,"13069_0",{"SLURM_JOB_ID":"13070",
                "SLURM_ARRAY_JOB_ID":"13069","SLURM_ARRAY_TASK_ID":"1"})

    def test_array_raw_ids_differ_from_alias_and_master_is_real_task_id(self):
        first=fixture_run(self.root,self.task,[],["ENGINEERING_FAILURE"],"13069_0","EARLY_ENGINEERING_FAILURE","13070")
        second=fixture_run(self.root,self.plan["tasks"][1],[],["ENGINEERING_FAILURE"],"13069_1","EARLY_ENGINEERING_FAILURE","13069")
        originals=[Path(x["path"]).read_bytes() for x in [first,second]]
        for aliases in [True,False]:
            raw=sacct("13069_0",183,state="FAILED",raw_id="13070",include_alias=aliases)+sacct(
                "13069_1",17,state="FAILED",raw_id="13069",include_alias=aliases)
            out=m.independent_accounting(self.plan,[first,second],raw)
            self.assertEqual(out["allocated_gpu_seconds_all_attempts"],200)
            self.assertEqual(out["physical_allocation_count"],2)
            self.assertEqual([x["raw_allocation_id"] for x in out["tasks"]],["13070","13069"])
            self.assertEqual([x["logical_allocation_key"] for x in out["tasks"]],["13069_0","13069_1"])
            self.assertTrue(all(not x["comparable_full_budget"] for x in out["tasks"]))
        self.assertEqual([Path(x["path"]).read_bytes() for x in [first,second]],originals)

    def test_array_alias_steps_master_double_count_and_positive_missing_allocation(self):
        rec=fixture_run(self.root,self.task,job="13069_1",raw_id="13069")
        valid=sacct("13069_1",raw_id="13069")
        out=m.independent_accounting(self.plan,[rec],valid+sacct("13069_1.batch",raw_id="13069.batch"))
        self.assertEqual(out["allocated_gpu_seconds_all_attempts"],3600)
        self.assertEqual(len(out["excluded_sacct_rows"]),1)
        for raw in [valid+sacct("13069",raw_id="13069"),
                    sacct("13069",raw_id="13069"),
                    valid+sacct("13069_0",183,state="FAILED",raw_id="13070"),
                    sacct("13069_1",raw_id="13070")]:
            with self.subTest(raw=raw),self.assertRaises(ValueError):
                m.independent_accounting(self.plan,[rec],raw)

    def test_array_accounting_rejects_missing_or_contradictory_original_identity(self):
        rec=fixture_run(self.root,self.task)
        run=m.read_json(rec["path"])
        del run["scheduler_start"]
        missing=dump(rec["path"],run)
        with self.assertRaises(ValueError):
            m.independent_accounting(self.plan,[missing],sacct())
        run["scheduler_start"]=m.record(Path(rec["path"]).parent/"scheduler.json")
        for fields in [{"raw_allocation_id":"999"},{"logical_allocation_key":"124_0"},
                       {"allocation_identity":{"raw_allocation_id":"999"}}]:
            bad=dict(run,**fields)
            with self.subTest(fields=fields),self.assertRaises(ValueError):
                m.independent_accounting(self.plan,[dump(rec["path"],bad)],sacct())
        bad=dict(run,allocation_key="124_0")
        with self.assertRaises(ValueError):
            m.independent_accounting(self.plan,[dump(rec["path"],bad)],sacct())

    def test_independent_array_accounting_reconstructs_raw_ids_and_aliases(self):
        protocol_path,plan_path=self.root/"array_protocol.json",self.root/"array_plan.json"
        dump(protocol_path,protocol(self.root));frozen=m.freeze_protocol(protocol_path,plan_path)
        receipts=[]
        for task,alias,raw_id in [(frozen["tasks"][0],"13069_0","13070"),(frozen["tasks"][1],"13069_1","13069")]:
            rr=fixture_run(self.root,task,[],["ENGINEERING_FAILURE"],alias,"EARLY_ENGINEERING_FAILURE",raw_id)
            receipts.append(fixture_session(rr,plan_path,frozen))
        spec=importlib.util.spec_from_file_location("independent_array",ROOT/"steps/22_matched_benchmark/code/paired_budget_independent.py")
        auditor=importlib.util.module_from_spec(spec);spec.loader.exec_module(auditor)
        for include_alias in [True,False]:
            raw=sacct("13069_0",183,state="FAILED",raw_id="13070",include_alias=include_alias)+sacct(
                "13069_1",17,state="FAILED",raw_id="13069",include_alias=include_alias)
            accounting=m.independent_accounting(frozen,receipts,raw)
            cohort=m.cohorts(frozen,accounting["inventory"],accounting["tasks"])
            paths=[self.root/x for x in ["array_receipts.json","array_sacct.txt","array_accounting.json","array_cohort.json"]]
            dump(paths[0],receipts);paths[1].write_text(raw);dump(paths[2],accounting);dump(paths[3],cohort)
            result=auditor.audit(plan_path,paths[0],paths[1],paths[2],paths[3])
            self.assertEqual(result["all_allocated_gpu_seconds"],200)
            self.assertEqual(result["allocation_count"],2)
            self.assertFalse(result["complete_generation_matrix"])
            forged=json.loads(json.dumps(accounting));forged["tasks"][0]["raw_allocation_id"]="13069"
            dump(paths[2],forged)
            with self.assertRaises(ValueError):
                auditor.audit(plan_path,paths[0],paths[1],paths[2],paths[3])
        with self.assertRaises(ValueError):
            auditor.scheduler_rows(sacct("13069_1",raw_id="13069")+sacct("13069",raw_id="13069"))

    def test_offline_accounting_can_verify_old_source_but_generation_requires_current_source(self):
        protocol_path,plan_path=self.root/"offline_protocol.json",self.root/"offline_plan.json"
        dump(protocol_path,protocol(self.root));frozen=m.freeze_protocol(protocol_path,plan_path)
        old_source=self.root/"preserved_old_source.py";old_source.write_bytes(Path(m.SELF).read_bytes())
        frozen["orchestrator"]=m.record(old_source);dump(plan_path,frozen)
        with self.assertRaises(ValueError):
            m.validate_frozen_plan(plan_path)
        checked=m.validate_frozen_plan(plan_path,require_current_orchestrator=False)
        self.assertEqual(checked["orchestrator"],m.record(old_source))
        old_source.write_text("modified")
        with self.assertRaises(ValueError):
            m.validate_frozen_plan(plan_path,require_current_orchestrator=False)

    def test_scheduler_generic_and_typed_gpus_are_not_double_counted(self):
        self.assertEqual(m.parse_alloc_tres_gpu("cpu=8,gres/gpu=1,gres/gpu:a100=1"), 1)
        self.assertEqual(m.parse_alloc_tres_gpu("gres/gpu:a100=2"), 2)
        with self.assertRaises(ValueError):
            m.parse_alloc_tres_gpu("gres/gpu=1,gres/gpu:a100=2")

    def test_scheduler_steps_excluded_duplicate_allocations_rejected(self):
        allocations, excluded = m.parse_sacct(sacct() + sacct("123_0.batch", elapsed=3599))
        self.assertEqual(len(allocations), 1)
        self.assertEqual(len(excluded), 1)
        with self.assertRaises(ValueError):
            m.parse_sacct(sacct() + sacct())

    def test_short_engineering_allocation_counted_but_not_fair_method_result(self):
        rec = fixture_run(self.root, self.task, statuses=["ENGINEERING_FAILURE"], status="EARLY_ENGINEERING_FAILURE")
        out = m.independent_accounting(self.plan, [rec], sacct(elapsed=45, state="FAILED"))
        row = out["tasks"][0]
        self.assertEqual(out["allocated_gpu_seconds_all_attempts"], 45)
        self.assertFalse(row["comparable_full_budget"])
        self.assertEqual(out["all_attempt_count"], 1)

    def test_realized_budget_mismatch_and_unjoined_gpu_allocation_fail(self):
        rec = fixture_run(self.root, self.task)
        out = m.independent_accounting(self.plan, [rec], sacct(elapsed=3590))
        self.assertFalse(out["tasks"][0]["comparable_full_budget"])
        with self.assertRaises(ValueError):
            m.independent_accounting(self.plan, [rec], sacct() + sacct("124_0", elapsed=45, state="FAILED"))

    def test_same_allocation_cannot_be_counted_twice(self):
        rec = fixture_run(self.root, self.task)
        with self.assertRaises(ValueError):
            m.independent_accounting(self.plan, [rec, rec], sacct())

    def test_tampered_ledger_rejected(self):
        rec = fixture_run(self.root, self.task)
        run = m.read_json(rec["path"])
        Path(run["attempt_ledger"]["path"]).write_text("{}\n")
        with self.assertRaises(ValueError):
            m.inventory_from_ledgers([rec])

    def test_uniform_sampling_invariant_to_order_score_and_internal_acceptance(self):
        events = [event(self.task, seq, i, False, score) for i, (seq, score) in enumerate(
            [("ACD", 0.1), ("ACE", 0.8), ("ACF", 0.4), ("ACG", 0.9)])]
        rec = fixture_run(self.root, self.task, events, ["COMPLETED"] * 4)
        out = m.independent_accounting(self.plan, [rec], sacct())
        cohort_a = m.cohorts(self.plan, out["inventory"], out["tasks"])
        for item in out["inventory"]:
            for occurrence in item["occurrences"]:
                occurrence["native_score"] = 999 - occurrence["native_score"]
                occurrence["internal_acceptance"] = True
        cohort_b = m.cohorts(self.plan, list(reversed(out["inventory"])), out["tasks"])
        selected_a = [x["sequence_sha256"] for x in cohort_a["selected"] if x["cohort"] == "uniform_all_complete"]
        selected_b = [x["sequence_sha256"] for x in cohort_b["selected"] if x["cohort"] == "uniform_all_complete"]
        self.assertEqual(selected_a, selected_b)
        self.assertEqual(len(selected_a), 2)

    def test_uniform_selection_includes_internally_rejected_and_native_top_k_is_separate(self):
        events = [event(self.task, "ACD", 0, False, 0.9), event(self.task, "ACE", 1, True, 0.1)]
        rec = fixture_run(self.root, self.task, events, ["SCIENTIFIC_REJECT", "COMPLETED"])
        out = m.independent_accounting(self.plan, [rec], sacct())
        cohort = m.cohorts(self.plan, out["inventory"], out["tasks"])
        uniform = [x for x in cohort["selected"] if x["cohort"] == "uniform_all_complete"]
        native = [x for x in cohort["selected"] if x["cohort"] == "native_fixed_top_k"]
        self.assertEqual(len(uniform), 2)
        self.assertTrue(any(x["internal_acceptance_values"] == ["False"] for x in uniform))
        self.assertEqual(native[0]["sequence"], "ACD")

    def test_boundary_only_sequences_never_enter_primary_cohort(self):
        rec = fixture_run(self.root, self.task, [event(self.task, before=False)], ["TIMED_OUT_BOUNDARY"])
        out = m.independent_accounting(self.plan, [rec], sacct())
        cohort = m.cohorts(self.plan, out["inventory"], out["tasks"])
        self.assertEqual(cohort["selected"], [])
        self.assertEqual(len(out["inventory"]), 1)
        self.assertEqual(out["tasks"][0]["boundary_observed_sequences"], 1)

    def test_duplicate_full_budget_run_cannot_be_selected_post_result(self):
        a = fixture_run(self.root, self.task, job="123_0")
        b = fixture_run(self.root, self.task, job="124_0")
        out = m.independent_accounting(self.plan, [a, b], sacct() + sacct("124_0"))
        with self.assertRaises(ValueError):
            m.cohorts(self.plan, out["inventory"], out["tasks"])

    def test_missing_evaluator_outcomes_are_null_and_have_bounds(self):
        selected = [{"cohort_record_id": str(i)} for i in range(3)]
        outcomes = [{"cohort_record_id": "0", "evaluable": True, "pass": True},
                    {"cohort_record_id": "1", "evaluable": False, "pass": None}]
        rate = m.evaluator_rates(selected, outcomes)
        self.assertEqual(rate["n_missing"], 2)
        self.assertEqual(rate["complete_case_pass_rate"], 1)
        self.assertIsNone(rate["all_selected_pass_rate"])
        self.assertEqual(rate["all_selected_pass_rate_bounds"], [1 / 3, 1])
        with self.assertRaises(ValueError):
            m.evaluator_rates(selected, [{"cohort_record_id": "1", "evaluable": False, "pass": False}])

    def test_duplicate_unknown_evaluator_outcomes_rejected(self):
        selected = [{"cohort_record_id": "0"}]
        outcome = {"cohort_record_id": "0", "evaluable": True, "pass": False}
        with self.assertRaises(ValueError):
            m.evaluator_rates(selected, [outcome, outcome])
        with self.assertRaises(ValueError):
            m.evaluator_rates(selected, [dict(outcome, cohort_record_id="unknown")])

    def test_insufficient_targets_never_get_inferential_interval(self):
        result = m.target_bootstrap([1.0] * 5, 6, 2000, 4142)
        self.assertIsNone(result["interval_95"])
        self.assertEqual(result["n_targets"], 5)

    def test_target_bootstrap_is_seed_frozen_and_target_based(self):
        effects = [0, 1, 2, 3, 4, 5]
        a = m.target_bootstrap(effects, 6, 100, 4142)
        b = m.target_bootstrap(effects, 6, 100, 4142)
        self.assertEqual(a, b)
        self.assertEqual(a["n_targets"], 6)

    def test_zero_generated_sequences_quality_is_not_negative(self):
        rate = m.evaluator_rates([], [])
        self.assertIsNone(rate["all_selected_pass_rate"])
        self.assertIsNone(rate["complete_case_pass_rate"])
        self.assertIsNone(rate["all_selected_pass_rate_bounds"])

    def test_diagnostic_target_does_not_inflate_primary_target_n(self):
        self.plan["protocol"]["targets"][0]["analysis_role"] = "diagnostic"
        self.plan["protocol"]["targets"][0]["target_id"] = self.task["target_id"]
        raw_cohort = {"coverage": [], "selected": []}
        account = {"tasks": [], "all_attempt_count": 0, "allocated_gpu_seconds_all_attempts": 0}
        result = m.summarize(self.plan, account, raw_cohort, [])
        self.assertEqual(result["paired_target_effects"][0]["analysis_role"], "diagnostic")
        self.assertEqual(result["inference"]["n_targets"], 0)

    def test_generation_preflight_failure_has_durable_zero_attempt_receipt(self):
        plan_path = self.root / "plan.json"
        dump(plan_path, self.plan)
        output = self.root / "preflight"
        with mock.patch.dict(os.environ, {"SLURM_JOB_ID": "123"}, clear=False), mock.patch.object(
                m, "_run_task", side_effect=RuntimeError("preflight fixture failure")):
            result = m.run_task(plan_path, self.task["task_id"], output)
        self.assertEqual(result["status"], "EARLY_ENGINEERING_FAILURE")
        self.assertEqual(result["attempt_count"], 0)
        self.assertTrue((output / "run_receipt.json").exists())


    def test_source_amendment_cannot_change_budgets_targets_or_sampling(self):
        old_path=self.root/"old_plan.json";old=plan(self.root);dump(old_path,old)
        revised=json.loads(json.dumps(old))
        revised["protocol"]["technical_amendment"]={"reason":"Fix adapter engineering error",
            "previous_plan_receipt":m.record(old_path)}
        self.assertEqual(m.previous_amended_plan(revised)["tasks"],old["tasks"])
        revised["protocol"]["sampling"]["salt"]="changed-after-outcomes"
        with self.assertRaises(ValueError):m.previous_amended_plan(revised)

    def test_source_amendment_requires_pinned_previous_plan_and_reason(self):
        p=protocol(self.root);p["technical_amendment"]={"reason":"fix"}
        with self.assertRaises(ValueError):m.validate_protocol(p,False)
        p["technical_amendment"]={"previous_plan_receipt":{"path":"missing"}}
        with self.assertRaises(ValueError):m.validate_protocol(p,False)

    def test_changed_adapter_receipt_prevents_freeze(self):
        p = self.plan["protocol"]
        Path(p["methods"][0]["adapter_receipts"][0]["path"]).write_text("changed")
        with self.assertRaises(ValueError):
            m.validate_protocol(p, True)


    def test_native_update_merges_without_duplicating_original_sequence(self):
        original = event(self.task, "ACD", 0, None, None)
        rec = fixture_run(self.root, self.task, [original], ["COMPLETED"])
        run = m.read_json(rec["path"])
        update = m.normalize_screening_record({"sequence_record_id": original["sequence_record_id"],
            "internal_acceptance": True, "native_score": 0.9, "native_score_name": "native",
            "completed_at_epoch": 1002}, self.task, 0, 1, 1003, True)
        path = Path(rec["path"]).parent / "updates.jsonl"
        path.write_text(json.dumps(update) + "\n")
        run["native_screening_ledger"] = m.record(path)
        attempts_path = Path(run["attempt_ledger"]["path"])
        attempt = m.rows_jsonl(attempts_path)[0]
        attempt["screening_update_records"] = 1
        attempt["precutoff_screening_update_records"] = 1
        attempts_path.write_text(json.dumps(attempt) + "\n")
        run["attempt_ledger"] = m.record(attempts_path)
        rec = dump(rec["path"], run)
        inventory, tasks = m.inventory_from_ledgers([rec])
        self.assertEqual(len(inventory), 1)
        occurrence = inventory[0]["occurrences"][0]
        self.assertIsNone(occurrence["raw_native_score"])
        self.assertEqual(occurrence["native_score"], 0.9)
        self.assertTrue(occurrence["internal_acceptance"])
        self.assertEqual(tasks[0]["native_accepted_attempts"], 1)

    def test_postcutoff_native_update_is_retained_without_changing_top_k_score(self):
        original = event(self.task, "ACD", 0, None, None)
        rec = fixture_run(self.root, self.task, [original], ["TIMED_OUT_BOUNDARY"])
        run = m.read_json(rec["path"])
        update = m.normalize_screening_record({"sequence_record_id": original["sequence_record_id"],
            "internal_acceptance": True, "native_score": 0.9, "native_score_name": "native",
            "completed_at_epoch": 1002}, self.task, 0, 1, 1003, False)
        path = Path(rec["path"]).parent / "updates.jsonl"
        path.write_text(json.dumps(update) + "\n")
        run["native_screening_ledger"] = m.record(path)
        attempt_path = Path(run["attempt_ledger"]["path"])
        attempt = m.rows_jsonl(attempt_path)[0]
        attempt["screening_update_records"] = 1
        attempt["precutoff_screening_update_records"] = 0
        attempt_path.write_text(json.dumps(attempt) + "\n")
        run["attempt_ledger"] = m.record(attempt_path)
        rec = dump(rec["path"], run)
        inventory, _ = m.inventory_from_ledgers([rec])
        occurrence = inventory[0]["occurrences"][0]
        self.assertIsNone(occurrence["native_score"])
        self.assertIsNone(occurrence["internal_acceptance"])
        self.assertEqual(len(occurrence["native_screening_updates"]), 1)

    def test_update_without_original_sequence_is_engineering_contract_error(self):
        output = self.root / "streams"
        output.mkdir()
        seqlog, updateslog = self.root / "seqlog.jsonl", self.root / "updateslog.jsonl"
        seqlog.touch(); updateslog.touch()
        streams = m.AttemptStreams(output, seqlog, updateslog, self.task, 0)
        update = {"sequence_record_id": "unknown", "internal_acceptance": False, "native_score": 0.1,
                  "native_score_name": "native", "completed_at_epoch": 1000}
        (output / "native_screening.jsonl").write_text(json.dumps(update) + "\n")
        streams.scan(1001, True)
        self.assertEqual(len(streams.contract_errors()), 1)

    def test_changed_method_config_prevents_freeze(self):
        p = self.plan["protocol"]
        changed = self.root / "changed_config.json"
        p["methods"][0]["config_receipt"] = dump(changed, {"fixture": 1})
        changed.write_text('{"fixture":2}')
        with self.assertRaises(ValueError):
            m.validate_protocol(p, True)



    def test_embedded_protocol_and_task_mutation_cannot_start_generation(self):
        path = self.root / "frozen.json"
        dump(path, self.plan)
        self.assertEqual(m.validate_frozen_plan(path, m.sha_file(path), True)["tasks"], self.plan["tasks"])
        changed = json.loads(json.dumps(self.plan))
        changed["protocol"]["budget_gpu_seconds"] = 7200
        dump(path, changed)
        with self.assertRaises(ValueError):
            m.validate_frozen_plan(path, m.sha_file(path), True)
        changed = json.loads(json.dumps(self.plan))
        changed["tasks"][0]["budget_gpu_seconds"] = 7200
        dump(path, changed)
        with self.assertRaises(ValueError):
            m.validate_frozen_plan(path, m.sha_file(path), True)

    def test_plan_hash_is_required_for_production_generation(self):
        path = self.root / "frozen.json"
        dump(path, self.plan)
        with self.assertRaises(ValueError):
            m.validate_frozen_plan(path, require_expected=True)
        with self.assertRaises(ValueError):
            m.validate_frozen_plan(path, "0" * 64, True)
        m.validate_frozen_plan(path, m.sha_file(path), True)



    def test_independent_audit_recomputes_accounting_and_uniform_native_cohorts(self):
        independent_spec = importlib.util.spec_from_file_location("independent_budget",
            ROOT / "steps/22_matched_benchmark/code/paired_budget_independent.py")
        independent = importlib.util.module_from_spec(independent_spec)
        independent_spec.loader.exec_module(independent)
        ev = [event(self.task, "ACD", 0, False, 0.9), event(self.task, "ACE", 1, True, 0.1)]
        receipt = fixture_run(self.root, self.task, ev, ["SCIENTIFIC_REJECT", "COMPLETED"])
        plan_path = self.root / "plan.json"
        dump(plan_path, self.plan)
        receipt = fixture_session(receipt, plan_path, self.plan)
        accounting = m.independent_accounting(self.plan, [receipt], sacct())
        cohort = m.cohorts(self.plan, accounting["inventory"], accounting["tasks"])
        plan_path, receipts_path, sacct_path = self.root / "plan.json", self.root / "receipts.json", self.root / "sacct.txt"
        account_path, cohort_path = self.root / "accounting.json", self.root / "cohort.json"
        dump(plan_path, self.plan); dump(receipts_path, [receipt])
        sacct_path.write_text(sacct()); dump(account_path, accounting); dump(cohort_path, cohort)
        result = independent.audit(plan_path, receipts_path, sacct_path, account_path, cohort_path)
        self.assertEqual(result["status"], "INDEPENDENT_BUDGET_LEDGER_AND_COHORT_AUDIT_PASS")
        self.assertEqual(result["all_attempt_count"], 2)
        self.assertEqual(result["all_allocated_gpu_seconds"], 3600)
        self.assertEqual(result["full_budget_comparable_tasks"], 1)
        self.assertFalse(result["complete_generation_matrix"])
        accounting["all_attempt_count"] = 999
        dump(account_path, accounting)
        with self.assertRaises(ValueError):
            independent.audit(plan_path, receipts_path, sacct_path, account_path, cohort_path)

    def test_independent_audit_rejects_changed_cleanup_deadline(self):
        independent_spec = importlib.util.spec_from_file_location("independent_budget_deadline",
            ROOT / "steps/22_matched_benchmark/code/paired_budget_independent.py")
        independent = importlib.util.module_from_spec(independent_spec)
        independent_spec.loader.exec_module(independent)
        receipt = fixture_run(self.root, self.task)
        run = m.read_json(receipt["path"])
        run["generation_cutoff_epoch"] += 10
        receipt = dump(receipt["path"], run)
        plan_path = self.root / "plan.json"
        dump(plan_path, self.plan)
        receipt = fixture_session(receipt, plan_path, self.plan)
        accounting = m.independent_accounting(self.plan, [receipt], sacct())
        cohort = m.cohorts(self.plan, accounting["inventory"], accounting["tasks"])
        plan_path, receipts_path, sacct_path = self.root / "plan.json", self.root / "receipts.json", self.root / "sacct.txt"
        account_path, cohort_path = self.root / "accounting.json", self.root / "cohort.json"
        dump(plan_path, self.plan); dump(receipts_path, [receipt])
        sacct_path.write_text(sacct()); dump(account_path, accounting); dump(cohort_path, cohort)
        with self.assertRaises(ValueError):
            independent.audit(plan_path, receipts_path, sacct_path, account_path, cohort_path)




    def test_independent_amendment_counts_failed_old_plan_and_fixed_new_plan(self):
        spec=importlib.util.spec_from_file_location("amendment_independent",
            ROOT/"steps/22_matched_benchmark/code/paired_budget_independent.py")
        independent=importlib.util.module_from_spec(spec);spec.loader.exec_module(independent)
        old_path=self.root/"old_plan.json";dump(old_path,self.plan)
        old_run=fixture_run(self.root,self.task,[],["ENGINEERING_FAILURE"],"123_0","EARLY_ENGINEERING_FAILURE")
        old_run=fixture_session(old_run,old_path,self.plan)
        revised=json.loads(json.dumps(self.plan))
        revised["protocol"]["technical_amendment"]={"reason":"Fix loader; no scientific setting changes",
            "previous_plan_receipt":m.record(old_path)}
        revised["protocol"]["methods"][0]["config_receipt"]=dump(self.root/"fixed_config.json",{"loader_fix":True})
        revised["protocol_receipt"]=dump(self.root/"revised_protocol.json",revised["protocol"])
        new_path=self.root/"new_plan.json";dump(new_path,revised)
        new_run=fixture_run(self.root,self.task,[event(self.task)],["SCIENTIFIC_REJECT"],"124_0")
        new_run=fixture_session(new_run,new_path,revised)
        raw=sacct(elapsed=45,state="FAILED")+sacct("124_0")
        accounting=m.independent_accounting(revised,[old_run,new_run],raw)
        cohort=m.cohorts(revised,accounting["inventory"],accounting["tasks"])
        rp,ap,cp,sp=[self.root/x for x in ["receipts.json","accounting.json","cohort.json","raw_sacct.txt"]]
        dump(rp,[old_run,new_run]);dump(ap,accounting);dump(cp,cohort);sp.write_text(raw)
        result=independent.audit(new_path,rp,sp,ap,cp)
        self.assertEqual(result["all_allocated_gpu_seconds"],3645)
        self.assertEqual(result["full_budget_comparable_tasks"],1)
        # A scientific run from an obsolete plan cannot be retroactively reused.
        old_value=m.read_json(old_run["path"]);old_value["status"]="BUDGET_EXHAUSTED_WITH_EXPLICIT_BOUNDARY_CENSORING"
        old_run=dump(old_run["path"],old_value);dump(rp,[old_run,new_run])
        with self.assertRaises(ValueError):independent.audit(new_path,rp,sp,ap,cp)

    def test_independent_raw_stream_detects_omitted_or_changed_complete_sequence(self):
        spec=importlib.util.spec_from_file_location("raw_independent",
            ROOT/"steps/22_matched_benchmark/code/paired_budget_independent.py")
        independent=importlib.util.module_from_spec(spec);spec.loader.exec_module(independent)
        ev=event(self.task)
        raw=self.root/"raw_sequences.jsonl";raw.write_text(json.dumps(ev)+"\n")
        attempt={"raw_sequence_stream":m.record(raw),"raw_native_screening_stream":None}
        independent.audit_raw_streams(attempt,[ev],[])
        with self.assertRaises(ValueError):independent.audit_raw_streams(attempt,[],[])
        original=dict(ev,sequence="ACE");raw.write_text(json.dumps(original)+"\n")
        attempt["raw_sequence_stream"]=m.record(raw)
        with self.assertRaises(ValueError):independent.audit_raw_streams(attempt,[ev],[])

    def test_pure_cpu_allocation_cannot_launch_generation_even_if_nvml_visible(self):
        with self.assertRaises(ValueError):
            m.validate_scheduler_gpu_allocation("JobId=123 JobState=RUNNING AllocTRES=cpu=1,node=1", 1)
        with self.assertRaises(ValueError):
            m.validate_scheduler_gpu_allocation("JobId=123 JobState=RUNNING AllocTRES=cpu=1,gres/gpu=0", 1)
        with self.assertRaises(ValueError):
            m.validate_scheduler_gpu_allocation("JobId=123 JobState=RUNNING AllocTRES=cpu=4,gres/gpu=2", 1)

    def test_scheduler_allocation_tres_and_legacy_tres_are_both_validated(self):
        text = "JobId=123 JobState=RUNNING AllocTRES=cpu=4,gres/gpu=1,gres/gpu:a100=1"
        self.assertEqual(m.validate_scheduler_gpu_allocation(text, 1), "cpu=4,gres/gpu=1,gres/gpu:a100=1")
        self.assertEqual(m.validate_scheduler_gpu_allocation("JobId=123 JobState=RUNNING TRES=cpu=4,gres/gpu=1", 1),
                         "cpu=4,gres/gpu=1")


class PersistentSessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.plan = plan(self.root)
        self.task = self.plan["tasks"][0]
        self.sessions = []
        self.expected = {k: "frozen-" + k for k in
                         ["protocol_sha256", "plan_sha256", "method_config_sha256", "target_manifest_sha256"]}

    def tearDown(self):
        for session in self.sessions:
            session.final_record()
        self.tmp.cleanup()

    def daemon(self, mode="normal", seconds=1.5, ready_delay=0):
        # Pure bookkeeping daemon; each request emits one sequence then responds.
        code = r'''
import hashlib,json,os,pathlib,subprocess,sys,time
p=pathlib.Path.cwd()
expected=json.loads(os.environ["FIXTURE_READY"])
mode=os.environ["FIXTURE_MODE"]
def atomic(path,v):
    temp=path.with_suffix(".partial")
    temp.write_text(json.dumps(v)+"\n"); os.replace(temp,path)
def receipt(path):
    b=path.read_bytes(); return {"path":str(path.resolve()),"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
time.sleep(float(os.environ["FIXTURE_READY_DELAY"]))
if mode=="bad_ready": expected["plan_sha256"]="tampered"
atomic(p/"READY.json",dict(expected,schema="paired-budget-session-v1",status="READY",pid=os.getpid()))
(p/"initializations.txt").write_text("one\n")
for index in range(100):
    reqpath=p/"requests"/("%06d.json"%index)
    while not reqpath.exists(): time.sleep(.002)
    req=json.loads(reqpath.read_text()); out=pathlib.Path(req["attempt_dir"])
    print("attempt",index,"pid",os.getpid(),flush=True)
    seq={"sequence_record_id":"sequence-"+str(index),"sequence":"ACD","lineage_id":"lineage-"+str(index),
         "internal_acceptance":False,"native_score":.2,"native_score_name":"native","completed_at_epoch":time.time()}
    if mode=="bad_sequence": seq["sequence"]="ACDX"
    (out/"sequences.jsonl").write_text(json.dumps(seq)+"\n")
    if mode=="bad_sequence": time.sleep(10)
    if mode=="boundary":
        (out/"native_screening.jsonl").write_text('{"sequence_record_id":')
        time.sleep(10)
    if mode=="bad_rpc":
        (p/"responses"/("%06d.json"%index)).write_text('{"schema":')
    else:
        result=out/"attempt_result.json"
        atomic(result,{"status":"SCIENTIFIC_REJECT"})
        response=dict(schema="paired-budget-session-v1",status="COMPLETE",request_id=req["request_id"],attempt_result=receipt(result))
        if mode=="wrong_rpc": response["request_id"]="999999"
        atomic(p/"responses"/("%06d.json"%index),response)
        '''
        env=dict(os.environ,FIXTURE_READY=json.dumps(self.expected),FIXTURE_MODE=mode,
                 FIXTURE_READY_DELAY=str(ready_delay))
        session=m.PersistentSession([sys.executable,"-u","-c",code],env,self.root/("session"+str(len(self.sessions))),
                                    time.monotonic()+seconds,self.expected)
        self.sessions.append(session)
        return session

    def attempt(self, session,index):
        out=self.root/("attempt"+str(index)); out.mkdir()
        seq=self.root/"sequences.jsonl"; updates=self.root/"updates.jsonl"
        seq.touch(exist_ok=True); updates.touch(exist_ok=True)
        stream=m.AttemptStreams(out,seq,updates,self.task,index,time.time()+max(0,session.generation_deadline-time.monotonic()))
        request=dict(schema="paired-budget-session-v1",action="method-attempt",request_id="%06d"%index,
                     attempt_dir=str(out),attempt_index=index,seed=17)
        execution=session.attempt(request,out,stream,.003)
        result=m.read_json(out/"attempt_result.json") if (out/"attempt_result.json").exists() else None
        return execution,result,stream

    def test_one_persistent_pid_and_one_import_lifecycle_across_attempts(self):
        session=self.daemon()
        self.assertTrue(session.wait_ready(.003))
        first=self.attempt(session,0); second=self.attempt(session,1)
        self.assertEqual(first[0]["session_pid"],second[0]["session_pid"])
        self.assertEqual((session.path/"initializations.txt").read_text(),"one\n")
        self.assertEqual(len(first[2].events),1)
        self.assertEqual(m.classify_attempt(second[0],second[1],second[2].events,[],None)[0],"SCIENTIFIC_REJECT")
        self.assertLess(time.monotonic(),session.generation_deadline)

    def test_initialization_boundary_censored_hard_kill(self):
        session=self.daemon(seconds=.15,ready_delay=10)
        start=time.monotonic()
        self.assertFalse(session.wait_ready(.003))
        self.assertTrue(session.deadline_reached.is_set())
        self.assertIsNotNone(session.proc.poll())
        self.assertLess(time.monotonic()-start,.8)

    def test_boundary_keeps_complete_rejected_sequence_and_partial_update(self):
        session=self.daemon("boundary",seconds=.22)
        self.assertTrue(session.wait_ready(.003))
        execution,result,stream=self.attempt(session,0)
        self.assertTrue(execution["boundary_censored"])
        self.assertEqual(len(stream.events),1)
        self.assertFalse(stream.events[0]["internal_acceptance"])
        self.assertTrue(stream.events[0]["observed_before_generation_cutoff"])
        self.assertIn("native_screening",stream.partial_tail())
        self.assertEqual(m.classify_attempt(execution,result,stream.events,stream.errors,stream.partial_tail())[0],"TIMED_OUT_BOUNDARY")


    def test_invalid_sequence_stops_early_without_masking_as_budget_boundary(self):
        session=self.daemon("bad_sequence",seconds=2)
        self.assertTrue(session.wait_ready(.003))
        execution,result,stream=self.attempt(session,0)
        self.assertFalse(execution["boundary_censored"])
        self.assertIn("Invalid original",execution["launch_error"])
        self.assertTrue(stream.errors)
        self.assertIsNotNone(session.proc.poll())
        self.assertLess(time.monotonic(),session.generation_deadline-1)
        self.assertEqual(m.classify_attempt(execution,result,stream.events,stream.errors,None)[0],"ENGINEERING_FAILURE")

    def test_truncated_rpc_is_engineering_failure_and_session_stops_early(self):
        session=self.daemon("bad_rpc",seconds=2)
        self.assertTrue(session.wait_ready(.003))
        execution,result,stream=self.attempt(session,0)
        self.assertIn("JSONDecodeError",execution["launch_error"])
        self.assertIsNotNone(session.proc.poll())
        self.assertLess(time.monotonic(),session.generation_deadline-1)
        self.assertEqual(m.classify_attempt(execution,result,stream.events,[],None)[0],"ENGINEERING_FAILURE")

    def test_response_for_other_attempt_is_engineering_failure(self):
        session=self.daemon("wrong_rpc")
        self.assertTrue(session.wait_ready(.003))
        execution,result,stream=self.attempt(session,0)
        self.assertIn("does not match",execution["launch_error"])
        self.assertIsNotNone(session.proc.poll())

    def test_ready_hash_mismatch_refuses_requests(self):
        session=self.daemon("bad_ready")
        with self.assertRaises(ValueError):
            session.wait_ready(.003)
        self.assertEqual(list((session.path/"requests").iterdir()),[])

    def test_watchdog_kills_session_even_while_controller_not_polling(self):
        session=self.daemon(seconds=.16,ready_delay=10)
        # Controller deliberately does no reads/polls until after the deadline.
        time.sleep(.28)
        self.assertTrue(session.deadline_reached.is_set())
        self.assertIsNotNone(session.proc.poll())

    def test_group_cleanup_even_when_leader_exits_first(self):
        pidfile=self.root/"grandchild.txt"
        code="import subprocess,sys; p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(10)']); open("+repr(str(pidfile))+",'w').write(str(p.pid))"
        proc=m.subprocess.Popen([sys.executable,"-c",code],start_new_session=True)
        proc.wait()
        pid=int(pidfile.read_text())
        m.kill_group(proc)
        # A zombie is terminated; it cannot compute or hold GPU contexts.
        time.sleep(.03)
        stat=Path("/proc")/str(pid)/"stat"
        self.assertTrue(not stat.exists() or stat.read_text().split()[2]=="Z")


    def test_full_persistent_runner_ledgers_budget_and_independent_audit(self):
        # Real CPU child lifecycle; GPU ownership/probe are mocked, no inference.
        adapter=self.root/"cpu_adapter.py"
        adapter.write_text(r'''
import hashlib,json,os,pathlib,time
p=pathlib.Path.cwd()
def atomic(path,value):
    tmp=path.with_suffix(".partial");tmp.write_text(json.dumps(value)+"\n");os.replace(tmp,path)
def receipt(path):
    data=path.read_bytes();return {"path":str(path.resolve()),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}
(p/"child_cvd.txt").write_text(os.environ["CUDA_VISIBLE_DEVICES"])
ready={key:os.environ["BENCHMARK_"+key.upper()] for key in ["protocol_sha256","plan_sha256","method_config_sha256","target_manifest_sha256"]}
atomic(p/"READY.json",dict(ready,schema="paired-budget-session-v1",status="READY",pid=os.getpid()))
for index in range(10):
    request_path=p/"requests"/("%06d.json"%index)
    while not request_path.exists():time.sleep(.002)
    request=json.loads(request_path.read_text());out=pathlib.Path(request["attempt_dir"])
    raw={"sequence_record_id":"s"+str(index),"sequence":"ACD","lineage_id":"lineage"+str(index),
        "internal_acceptance":None,"native_score":None,"native_score_name":"native","completed_at_epoch":time.time()}
    (out/"sequences.jsonl").write_text(json.dumps(raw)+"\n")
    update={"sequence_record_id":raw["sequence_record_id"],"internal_acceptance":False,"native_score":.7,
        "native_score_name":"native","completed_at_epoch":time.time()}
    (out/"native_screening.jsonl").write_text(json.dumps(update)+"\n")
    if index==2:
        with (out/"native_screening.jsonl").open("a") as f:f.write('{"sequence_record_id":')
        time.sleep(10)
    result=out/"attempt_result.json";atomic(result,{"status":"SCIENTIFIC_REJECT"})
    atomic(p/"responses"/("%06d.json"%index),dict(schema="paired-budget-session-v1",status="COMPLETE",
        request_id=request["request_id"],attempt_result=receipt(result)))
''')
        p=protocol(self.root);p["budget_gpu_seconds"]=3;p["shutdown_reserve_seconds"]=1
        for method in p["methods"]:
            method["session_start"]=[sys.executable,"-u",str(adapter)]
            method["adapter_receipts"]=[m.record(adapter)]
        protocol_path,plan_path=self.root/"production_protocol.json",self.root/"frozen.json"
        dump(protocol_path,p);frozen=m.freeze_protocol(protocol_path,plan_path);task=frozen["tasks"][0]
        anchor=time.time()-.05
        timestamp=m.dt.datetime.fromtimestamp(anchor,m.dt.timezone.utc).isoformat()
        scheduler="JobId=13069 ArrayJobId=13069 ArrayTaskId=1 JobState=FAILED StartTime=1970-01-01T00:00:00+00:00 AllocTRES=cpu=1\n"+"JobId=13070 ArrayJobId=13069 ArrayTaskId=0 JobState=RUNNING StartTime="+timestamp+" AllocTRES=cpu=1,gres/gpu=1"
        gpu=hardware_fixture()
        with mock.patch.dict(os.environ,{"SLURM_JOB_ID":"13070","SLURM_ARRAY_JOB_ID":"13069","SLURM_ARRAY_TASK_ID":"0"}), \
             mock.patch.object(m.subprocess,"run",return_value=m.subprocess.CompletedProcess([],0,scheduler,"")), \
             mock.patch.object(m,"gpu_probe",return_value=gpu):
            result=m.run_task(plan_path,task["task_id"],self.root/"run",expected_plan_sha256=m.sha_file(plan_path))
        self.assertEqual(result["status"],"BUDGET_EXHAUSTED_WITH_EXPLICIT_BOUNDARY_CENSORING")
        self.assertEqual(result["attempt_count"],3)
        self.assertEqual(result["allocation_key"],"13069_0")
        self.assertEqual(result["raw_allocation_id"],"13070")
        self.assertEqual(result["logical_allocation_key"],"13069_0")
        self.assertTrue(result["scheduler_selected_record"].startswith("JobId=13070 "))
        self.assertEqual((self.root/"run"/"session"/"child_cvd.txt").read_text(),"GPU-3")
        attempts=m.rows_jsonl(result["attempt_ledger"]["path"])
        self.assertEqual([x["status"] for x in attempts],["SCIENTIFIC_REJECT","SCIENTIFIC_REJECT","TIMED_OUT_BOUNDARY"])
        self.assertEqual(len({x["execution"]["session_pid"] for x in attempts}),1)
        run_receipt=m.record(self.root/"run"/"run_receipt.json")
        end=m.dt.datetime.fromtimestamp(anchor+3,m.dt.timezone.utc).isoformat()
        raw="|".join(["13070","3","gres/gpu=1","COMPLETED",timestamp,end,"cpu-fixture","organ"])+"\n"
        accounting=m.independent_accounting(frozen,[run_receipt],raw)
        self.assertEqual(accounting["all_attempt_count"],3)
        self.assertTrue(accounting["tasks"][0]["comparable_full_budget"])
        self.assertEqual(len(accounting["inventory"]),1)
        cohort=m.cohorts(frozen,accounting["inventory"],accounting["tasks"])
        self.assertTrue(all(x["internal_acceptance_values"]==["False"] for x in cohort["selected"]))
        receiptspath,acctpath,cohortpath,sacctpath=[self.root/x for x in ["receipts.json","accounting.json","cohort.json","raw_sacct.txt"]]
        dump(receiptspath,[run_receipt]);dump(acctpath,accounting);dump(cohortpath,cohort);sacctpath.write_text(raw)
        spec=importlib.util.spec_from_file_location("end_to_end_independent",ROOT/"steps/22_matched_benchmark/code/paired_budget_independent.py")
        independent=importlib.util.module_from_spec(spec);spec.loader.exec_module(independent)
        acceptance=independent.audit(plan_path,receiptspath,sacctpath,acctpath,cohortpath)
        self.assertEqual(acceptance["all_attempt_count"],3)
        self.assertEqual(acceptance["source_sequence_records"],3)
        self.assertEqual(acceptance["full_budget_comparable_tasks"],1)
        self.assertFalse(acceptance["complete_generation_matrix"])

    def test_protocol_rejects_repeated_process_mode(self):
        p=protocol(self.root)
        p["execution_mode"]="per_attempt"
        with self.assertRaises(ValueError): m.validate_protocol(p,False)

if __name__ == "__main__":
    unittest.main(verbosity=2)


