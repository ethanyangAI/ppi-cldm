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

def fixture_run(root, task, events=None, statuses=None, job="123_0", status=None):
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
           "hardware": {"gpus": [{"name": "FAKE_GPU_CPU_UNIT_TEST"}]},
           "attempt_ledger": m.record(attempt_path), "sequence_ledger": m.record(sequence_path),
           "allocation_started_at_epoch": 1000, "generation_cutoff_epoch": 4590,
           "allocation_deadline_epoch": 4600, "technical_rerun_of": None}
    return dump(out / "run_receipt.json", run)

def event(task, seq="ACD", index=0, acceptance=False, score=0.8, before=True):
    return m.normalize_sequence_record({"sequence": seq, "lineage_id": "lineage-" + str(index),
        "internal_acceptance": acceptance, "native_score": score, "native_score_name": "native",
        "completed_at_epoch": 1000}, task, index, 1, 1001, before)

def sacct(job="123_0", elapsed=3600, gpu="gres/gpu=1", state="COMPLETED"):
    return "|".join([job, str(elapsed), gpu, state, "1970-01-01T00:16:40+00:00", "1970-01-01T01:16:40+00:00", "node", "organ"]) + "\n"


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
        inventory=[{"index":i,"uuid":"GPU-"+str(i),"name":"A100","memory_total_mib":81920} for i in range(4)]
        selected,assignment,basis=m.select_assigned_gpus(inventory,{"SLURM_JOB_GPUS":"2","CUDA_VISIBLE_DEVICES":"0"},1)
        self.assertEqual([x["index"] for x in selected],[2])
        self.assertEqual(basis,"SLURM_JOB_GPUS")
        self.assertEqual(assignment["CUDA_VISIBLE_DEVICES"],"0")
        with self.assertRaises(ValueError): m.select_assigned_gpus(inventory,{"CUDA_VISIBLE_DEVICES":"0"},1)

    def test_assigned_gpu_uuid_and_device_count_are_checked(self):
        inventory=[{"index":i,"uuid":"GPU-"+str(i)} for i in range(4)]
        selected,_,_=m.select_assigned_gpus(inventory,{"CUDA_VISIBLE_DEVICES":"GPU-3"},1)
        self.assertEqual(selected[0]["index"],3)
        with self.assertRaises(ValueError): m.select_assigned_gpus(inventory,{"SLURM_JOB_GPUS":"0,1"},1)
        with self.assertRaises(ValueError): m.select_assigned_gpus(inventory,{"SLURM_JOB_GPUS":"9"},1)
        with self.assertRaises(ValueError): m.select_assigned_gpus(inventory,{"SLURM_JOB_GPUS":"0,0"},2)

    def test_step_gpu_assignment_is_preferred_and_visible_cgroup_fallback(self):
        inventory=[{"index":i,"uuid":"GPU-"+str(i)} for i in range(4)]
        selected,_,_=m.select_assigned_gpus(inventory,{"SLURM_JOB_GPUS":"0,1","SLURM_STEP_GPUS":"1"},1)
        self.assertEqual(selected[0]["index"],1)
        selected,_,basis=m.select_assigned_gpus([inventory[2]],{"CUDA_VISIBLE_DEVICES":"0"},1)
        self.assertEqual(selected[0]["index"],2)
        self.assertIn("cgroup-visible",basis)

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
            m.validate_scheduler_gpu_allocation("JobId=123 AllocTRES=cpu=1,node=1", 1)
        with self.assertRaises(ValueError):
            m.validate_scheduler_gpu_allocation("JobId=123 AllocTRES=cpu=1,gres/gpu=0", 1)
        with self.assertRaises(ValueError):
            m.validate_scheduler_gpu_allocation("JobId=123 AllocTRES=cpu=4,gres/gpu=2", 1)

    def test_scheduler_allocation_tres_and_legacy_tres_are_both_validated(self):
        text = "JobId=123 AllocTRES=cpu=4,gres/gpu=1,gres/gpu:a100=1"
        self.assertEqual(m.validate_scheduler_gpu_allocation(text, 1), "cpu=4,gres/gpu=1,gres/gpu:a100=1")
        self.assertEqual(m.validate_scheduler_gpu_allocation("JobId=123 TRES=cpu=4,gres/gpu=1", 1),
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
        scheduler="JobId=123 StartTime="+timestamp+" AllocTRES=cpu=1,gres/gpu=1"
        gpu={"gpus":[{"name":"FAKE_GPU_CPU_UNIT_TEST","memory_total_mib":1,"uuid":"SYNTHETIC_NO_GPU"}]}
        with mock.patch.dict(os.environ,{"SLURM_JOB_ID":"123","SLURM_ARRAY_JOB_ID":"","SLURM_ARRAY_TASK_ID":""}), \
             mock.patch.object(m.subprocess,"run",return_value=m.subprocess.CompletedProcess([],0,scheduler,"")), \
             mock.patch.object(m,"gpu_probe",return_value=gpu):
            result=m.run_task(plan_path,task["task_id"],self.root/"run",expected_plan_sha256=m.sha_file(plan_path))
        self.assertEqual(result["status"],"BUDGET_EXHAUSTED_WITH_EXPLICIT_BOUNDARY_CENSORING")
        self.assertEqual(result["attempt_count"],3)
        attempts=m.rows_jsonl(result["attempt_ledger"]["path"])
        self.assertEqual([x["status"] for x in attempts],["SCIENTIFIC_REJECT","SCIENTIFIC_REJECT","TIMED_OUT_BOUNDARY"])
        self.assertEqual(len({x["execution"]["session_pid"] for x in attempts}),1)
        run_receipt=m.record(self.root/"run"/"run_receipt.json")
        end=m.dt.datetime.fromtimestamp(anchor+3,m.dt.timezone.utc).isoformat()
        raw="|".join(["123","3","gres/gpu=1","COMPLETED",timestamp,end,"cpu-fixture","organ"])+"\n"
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

