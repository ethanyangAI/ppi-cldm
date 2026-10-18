#!/usr/bin/env python3
"""Frozen equal-GPU-budget orchestration; generic commands, no sequence design.

Production CLI requires Slurm. Commands are argv adapters, never shell strings.
Adapter contract is documented in PAIRED_BUDGET_API.md. All scientific rejects,
engineering failures and boundary-censored attempts remain in durable ledgers.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import statistics
import subprocess
import sys
import threading
import time

SCHEMA = "paired-budget-v1"
AA = set("ACDEFGHIKLMNPQRSTVWY")
TERMINAL = {"COMPLETED", "SCIENTIFIC_REJECT", "ENGINEERING_FAILURE", "TIMED_OUT_BOUNDARY", "INTERRUPTED"}
PROTECTED_ENV = {"CUDA_VISIBLE_DEVICES", "SLURM_JOB_ID", "SLURM_ARRAY_JOB_ID", "SLURM_ARRAY_TASK_ID"}
SELF = Path(__file__).resolve()

def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def record(path):
    p = Path(path).resolve()
    return {"path": str(p), "bytes": p.stat().st_size, "sha256": sha_file(p)}

def verified(rec):
    if not isinstance(rec, dict) or not {"path", "bytes", "sha256"} <= rec.keys():
        raise ValueError("Expected immutable file receipt")
    actual = record(rec["path"])
    if actual != {k: rec[k] for k in actual}:
        raise ValueError("File receipt mismatch: " + str(rec["path"]))
    return Path(actual["path"])

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text())

def write_exclusive(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        raise FileExistsError(str(p))
    partial = p.with_name(p.name + ".partial")
    with partial.open("x") as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    partial.replace(p)
    return record(p)

def append_durable(path, value):
    with Path(path).open("a") as f:
        f.write(canonical(value) + "\n")
        f.flush()
        os.fsync(f.fileno())

def rows_jsonl(path):
    out = []
    with Path(path).open() as f:
        for n, line in enumerate(f, 1):
            if not line.endswith("\n"):
                raise ValueError("Incomplete JSONL line " + str(n))
            out.append(json.loads(line))
    return out

def utc(epoch=None):
    return dt.datetime.fromtimestamp(time.time() if epoch is None else epoch, dt.timezone.utc).isoformat()

def positive_int(value, name):
    if type(value) is not int or value <= 0:
        raise ValueError(name + " must be a positive integer")
    return value

def validate_protocol(p, check_files=True):
    if p.get("schema") != SCHEMA or not p.get("protocol_id"):
        raise ValueError("Protocol schema/id missing")
    if p.get("execution_mode") != "persistent_session":
        raise ValueError("Formal paired benchmark requires persistent_session lifecycle")
    if p.get("scientific_scope") != "COMPUTATIONAL_ONLY":
        raise ValueError("Explicit COMPUTATIONAL_ONLY scope required")
    methods = p.get("methods", [])
    if len(methods) != 2 or len({x.get("method_id") for x in methods}) != 2:
        raise ValueError("Exactly two distinct methods required")
    targets = p.get("targets", [])
    if not targets or len({x.get("target_id") for x in targets}) != len(targets):
        raise ValueError("Distinct nonempty target matrix required")
    seeds = p.get("replicate_seeds", [])
    if not seeds or any(type(x) is not int for x in seeds) or len(set(seeds)) != len(seeds):
        raise ValueError("Distinct integer replicate seeds required")
    ngpu = positive_int(p.get("gpu_count"), "gpu_count")
    positive_int(p.get("budget_gpu_seconds"), "budget_gpu_seconds")
    reserve = positive_int(p.get("shutdown_reserve_seconds"), "shutdown_reserve_seconds")
    tolerance = p.get("accounting_tolerance_seconds", 0)
    if type(tolerance) is not int or tolerance < 0:
        raise ValueError("Nonnegative accounting tolerance required")
    if not p.get("hardware", {}).get("gpu_name"):
        raise ValueError("Frozen GPU hardware identity required")
    sampling = p.get("sampling", {})
    if not sampling.get("salt"):
        raise ValueError("Frozen sampling salt required")
    for k in ("uniform_n_per_replicate", "native_top_k_per_replicate"):
        positive_int(sampling.get(k), k)
    inference = p.get("inference", {})
    if inference.get("mode", "descriptive_only") not in {"descriptive_only", "target_bootstrap"}:
        raise ValueError("Frozen inference mode required")
    if inference.get("minimum_targets", 6) < 6:
        raise ValueError("At least six targets required for target bootstrap")
    positive_int(inference.get("bootstrap_replicates", 2000), "bootstrap_replicates")
    if type(inference.get("bootstrap_seed", 4142)) is not int:
        raise ValueError("Frozen bootstrap seed required")
    amendment = p.get("technical_amendment")
    if amendment is not None:
        if not isinstance(amendment, dict) or not isinstance(amendment.get("reason"), str) or not amendment["reason"].strip():
            raise ValueError("Technical amendment requires an explicit reason")
        if not amendment.get("previous_plan_receipt"):
            raise ValueError("Technical amendment requires immutable previous_plan_receipt")
        if check_files:
            verified(amendment["previous_plan_receipt"])
    for target in targets:
        if not target.get("target_id") or not re.fullmatch(r"[A-Za-z0-9_.-]+", target["target_id"]):
            raise ValueError("Unsafe target_id")
        budget = positive_int(target.get("budget_gpu_seconds", p["budget_gpu_seconds"]), "target budget")
        if budget % ngpu or budget // ngpu <= reserve + 1:
            raise ValueError("GPU budget must have integer wall seconds greater than reserve")
        if target.get("analysis_role", "primary") not in {"primary", "diagnostic"}:
            raise ValueError("Target analysis_role must be primary or diagnostic")
        if check_files:
            verified(target["input_manifest"])
    for method in methods:
        if not method.get("method_id") or not re.fullmatch(r"[A-Za-z0-9_.-]+", method["method_id"]):
            raise ValueError("Unsafe method_id")
        argv = method.get("session_start")
        if not isinstance(argv, list) or not argv or any(not isinstance(x, str) for x in argv):
            raise ValueError("Persistent session_start must be a nonempty argv array")
        if not method.get("adapter_receipts"):
            raise ValueError("Pinned adapter source receipt required")
        if not method.get("config_receipt"):
            raise ValueError("Pinned per-method config receipt required")
        if method.get("native_score_direction") not in {"higher", "lower"}:
            raise ValueError("Native score direction must be frozen")
        if not method.get("native_score_name"):
            raise ValueError("Native score name must be frozen")
        if PROTECTED_ENV & set(method.get("env", {})):
            raise ValueError("Adapter cannot override GPU/scheduler assignment")
        if check_files:
            verified(method["config_receipt"])
            for rec in method["adapter_receipts"]:
                verified(rec)
    return p

def make_tasks(p):
    validate_protocol(p, False)
    tasks = []
    for target in p["targets"]:
        for seed in p["replicate_seeds"]:
            pair_key = {"protocol_id": p["protocol_id"], "target_id": target["target_id"], "seed": seed}
            pair_id = digest(pair_key)[:24]
            for method in p["methods"]:
                key = dict(pair_key, method_id=method["method_id"])
                tasks.append(dict(key, task_id=digest(key)[:24], pair_id=pair_id,
                                  budget_gpu_seconds=target.get("budget_gpu_seconds", p["budget_gpu_seconds"])))
    for i, task in enumerate(tasks):
        task["array_index"] = i
    return tasks

def freeze_protocol(protocol_path, output):
    p = validate_protocol(read_json(protocol_path))
    plan = {"schema": SCHEMA, "status": "FROZEN_BEFORE_GENERATION",
            "protocol": p, "protocol_receipt": record(protocol_path),
            "orchestrator": record(SELF), "tasks": make_tasks(p), "created_at_utc": utc(),
            "sampling_scope": "All unique complete sequences observed before cutoff, including internally rejected sequences",
            "statistical_unit": "target; replicates are repeated computational runs"}
    write_exclusive(output, plan)
    return plan



def previous_amended_plan(current):
    amendment = current["protocol"].get("technical_amendment")
    if not amendment:
        return None
    previous = read_json(verified(amendment["previous_plan_receipt"]))
    if previous.get("status") != "FROZEN_BEFORE_GENERATION":
        raise ValueError("Previous source amendment plan was not frozen")
    if canonical(read_json(verified(previous["protocol_receipt"]))) != canonical(previous["protocol"]):
        raise ValueError("Previous plan protocol was changed")
    validate_protocol(previous["protocol"])
    verified(previous["orchestrator"])
    if canonical(previous["tasks"]) != canonical(current["tasks"]):
        raise ValueError("Technical amendment cannot change matched target/seed/budget tasks")
    old, new = previous["protocol"], current["protocol"]
    for field in ["protocol_id", "scientific_scope", "execution_mode", "targets", "replicate_seeds",
                  "gpu_count", "budget_gpu_seconds", "shutdown_reserve_seconds", "hardware", "sampling", "inference"]:
        if canonical(old.get(field)) != canonical(new.get(field)):
            raise ValueError("Technical amendment changes a frozen scientific comparison field: " + field)
    for before, after in zip(old["methods"], new["methods"]):
        if any(before.get(k) != after.get(k) for k in ["method_id", "native_score_name", "native_score_direction"]):
            raise ValueError("Technical amendment changes method/native-ranking identity")
    return previous


def validate_frozen_plan(plan_path, expected_sha256=None, require_expected=False):
    actual = record(plan_path)
    if require_expected and not expected_sha256:
        raise ValueError("Generation requires launcher-pinned --plan-sha256")
    if expected_sha256 is not None and actual["sha256"] != expected_sha256:
        raise ValueError("Frozen plan SHA differs from launcher")
    plan = read_json(plan_path)
    if plan.get("schema") != SCHEMA or plan.get("status") != "FROZEN_BEFORE_GENERATION":
        raise ValueError("Unfrozen plan")
    original = read_json(verified(plan["protocol_receipt"]))
    if canonical(original) != canonical(plan["protocol"]):
        raise ValueError("Embedded protocol differs from immutable original")
    validate_protocol(original)
    if canonical(plan["tasks"]) != canonical(make_tasks(original)):
        raise ValueError("Task matrix differs from frozen protocol")
    previous_amended_plan(plan)
    if record(SELF) != plan["orchestrator"]:
        raise ValueError("Orchestrator changed after freeze")
    return plan

def task_by_id(plan, task_id):
    found = [x for x in plan["tasks"] if x["task_id"] == task_id]
    if len(found) != 1:
        raise ValueError("Unknown/nonunique task_id")
    return found[0]

def attempt_seed(task, index):
    return int(digest({"protocol_id": task["protocol_id"], "target_id": task["target_id"],
                       "replicate_seed": task["seed"], "attempt_index": index})[:8], 16)

def allocation_key(env):
    if env.get("SLURM_ARRAY_JOB_ID") and env.get("SLURM_ARRAY_TASK_ID"):
        return env["SLURM_ARRAY_JOB_ID"] + "_" + env["SLURM_ARRAY_TASK_ID"]
    if env.get("SLURM_JOB_ID"):
        return env["SLURM_JOB_ID"]
    raise RuntimeError("Slurm allocation required")

def allocation_anchor(scontrol_text):
    match = re.search(r"\bStartTime=(\S+)", scontrol_text)
    if not match or match[1] in {"Unknown", "N/A", "None"}:
        raise ValueError("Scheduler StartTime unavailable")
    when = dt.datetime.fromisoformat(match[1])
    if when.tzinfo is None:
        when = when.astimezone()
    return when.timestamp()


def validate_scheduler_gpu_allocation(scontrol_text, expected_gpu_count):
    match = re.search(r"\b(?:AllocTRES|TRES)=(\S+)", scontrol_text)
    if not match:
        raise ValueError("Scheduler allocation TRES unavailable")
    actual = parse_alloc_tres_gpu(match[1])
    if actual != expected_gpu_count:
        raise ValueError("Actual Slurm GPU allocation differs from frozen gpu_count")
    return match[1]

def budget_deadlines(allocation_start_epoch, now_epoch, now_monotonic, gpu_seconds, ngpu, reserve):
    wall = gpu_seconds / ngpu
    absolute = allocation_start_epoch + wall
    allocation_deadline = now_monotonic + (absolute - now_epoch)
    return allocation_deadline - reserve, allocation_deadline

def select_assigned_gpus(inventory, env, expected_count):
    """NVML may expose all node GPUs; Slurm global device IDs define ownership."""
    assignment = {key: env.get(key) for key in
                  ["CUDA_VISIBLE_DEVICES", "SLURM_JOB_GPUS", "SLURM_STEP_GPUS"]}
    basis = next((key for key in ["SLURM_STEP_GPUS", "SLURM_JOB_GPUS"] if assignment[key]), None)
    if basis is None and assignment["CUDA_VISIBLE_DEVICES"] and any(
            x.startswith("GPU-") for x in assignment["CUDA_VISIBLE_DEVICES"].split(",")):
        basis = "CUDA_VISIBLE_DEVICES"
    if basis:
        identifiers = []
        for token in assignment[basis].split(","):
            token = token.strip()
            if re.fullmatch(r"\d+-\d+", token):
                low, high = map(int, token.split("-"))
                if high < low: raise ValueError("Invalid assigned GPU range")
                identifiers.extend(str(x) for x in range(low, high + 1))
            else:
                identifiers.append(token)
        if len(set(identifiers)) != len(identifiers) or len(identifiers) != expected_count:
            raise ValueError("Slurm device IDs disagree with allocated GPU count")
        selected = [x for x in inventory if str(x["index"]) in identifiers or x["uuid"] in identifiers]
        if len(selected) != expected_count:
            raise ValueError("Allocated physical GPU IDs absent from NVML inventory")
    else:
        if len(inventory) != expected_count:
            raise ValueError("NVML exposes unassigned devices without Slurm global IDs")
        selected, basis = inventory, "Slurm AllocTRES plus cgroup-visible NVML inventory"
    return selected, assignment, basis

def gpu_probe(expected_count):
    argv = ["nvidia-smi", "--query-gpu=index,name,memory.total,uuid", "--format=csv,noheader,nounits"]
    proc = subprocess.run(argv, text=True, capture_output=True, check=True)
    inventory = []
    for line in proc.stdout.strip().splitlines():
        cells = [x.strip() for x in line.split(",")]
        if len(cells) != 4:
            raise ValueError("Unexpected nvidia-smi output")
        inventory.append({"index": int(cells[0]), "name": cells[1],
                          "memory_total_mib": int(cells[2]), "uuid": cells[3]})
    gpus, assignment, basis = select_assigned_gpus(inventory, os.environ, expected_count)
    return {"argv": argv, "stdout": proc.stdout, "stderr": proc.stderr, "gpus": gpus,
            "nvml_inventory": inventory, "assignment_environment": assignment,
            "selection_basis": basis}

def normalize_sequence(sequence):
    if not isinstance(sequence, str):
        raise ValueError("Complete sequence must be a string")
    seq = "".join(sequence.split()).upper()
    if not seq or not set(seq) <= AA:
        raise ValueError("Only complete canonical amino-acid sequences may enter inventory")
    return seq

def normalize_sequence_record(raw, task, index, line_number, observed_epoch, before_cutoff):
    seq = normalize_sequence(raw.get("sequence"))
    if not isinstance(raw.get("lineage_id"), str) or not raw["lineage_id"]:
        raise ValueError("Complete sequence lineage_id required")
    acceptance = raw.get("internal_acceptance")
    if acceptance is not None and type(acceptance) is not bool:
        raise ValueError("internal_acceptance must be bool or null")
    score = raw.get("native_score")
    if score is not None and (type(score) not in {float, int} or not math.isfinite(score)):
        raise ValueError("native_score must be finite or null")
    completed = raw.get("completed_at_epoch")
    if type(completed) not in {float, int} or not math.isfinite(completed) or completed > observed_epoch + 0.01:
        raise ValueError("Finite, nonfuture completion timestamp required")
    receipts = raw.get("artifact_receipts", [])
    if not isinstance(receipts, list):
        raise ValueError("artifact_receipts must be an array")
    return {"task_id": task["task_id"], "target_id": task["target_id"], "method_id": task["method_id"],
            "seed": task["seed"], "attempt_index": index, "source_line_number": line_number,
            "sequence_record_id": raw.get("sequence_record_id", raw["lineage_id"]),
            "sequence": seq, "sequence_sha256": hashlib.sha256(seq.encode()).hexdigest(),
            "lineage_id": raw["lineage_id"], "internal_acceptance": acceptance,
            "native_score": score, "native_score_name": raw.get("native_score_name"),
            "completed_at_epoch": completed, "observed_at_epoch": observed_epoch,
            "observed_at_utc": utc(observed_epoch), "observed_before_generation_cutoff": bool(before_cutoff),
            "artifact_receipts": receipts}


def normalize_screening_record(raw, task, index, line_number, observed_epoch, before_cutoff):
    rid = raw.get("sequence_record_id")
    if not isinstance(rid, str) or not rid:
        raise ValueError("Native screening update requires sequence_record_id")
    accepted, score = raw.get("internal_acceptance"), raw.get("native_score")
    if accepted is not None and type(accepted) is not bool:
        raise ValueError("Native acceptance update must be bool/null")
    if score is not None and (type(score) not in {int, float} or not math.isfinite(score)):
        raise ValueError("Native score update must be finite/null")
    completed = raw.get("completed_at_epoch")
    if type(completed) not in {int, float} or not math.isfinite(completed) or completed > observed_epoch + 0.01:
        raise ValueError("Native screening completion timestamp required")
    return {"task_id": task["task_id"], "attempt_index": index, "source_line_number": line_number,
            "sequence_record_id": rid, "internal_acceptance": accepted, "native_score": score,
            "native_score_name": raw.get("native_score_name"), "completed_at_epoch": completed,
            "observed_at_epoch": observed_epoch, "observed_before_generation_cutoff": bool(before_cutoff)}

class SequenceStream:
    """Reads only newline-complete records; final partial lines never become candidates."""
    def __init__(self, path, output, task, attempt_index):
        self.path, self.output = Path(path), Path(output)
        self.task, self.index = task, attempt_index
        self.offset, self.line_number = 0, 0
        self.events, self.errors = [], []
        self.live_cutoff_epoch = None

    normalize = staticmethod(normalize_sequence_record)

    def scan(self, observed_epoch, before_cutoff):
        if not self.path.exists():
            return
        with self.path.open("rb") as f:
            f.seek(self.offset)
            snapshot_size = os.fstat(f.fileno()).st_size
            while f.tell() < snapshot_size:
                line = f.readline()
                if not line or not line.endswith(b"\n"):
                    break
                self.offset = f.tell()
                self.line_number += 1
                try:
                    raw = json.loads(line)
                    seen = time.time() if self.live_cutoff_epoch is not None else observed_epoch
                    eligible = before_cutoff and (self.live_cutoff_epoch is None or seen <= self.live_cutoff_epoch)
                    event = self.normalize(raw, self.task, self.index, self.line_number,
                                           seen, eligible)
                    self.events.append(event)
                    append_durable(self.output, event)
                except Exception as exc:
                    self.errors.append({"line_number": self.line_number, "error": str(exc),
                                        "raw_sha256": hashlib.sha256(line).hexdigest()})

    def partial_tail(self):
        if not self.path.exists():
            return None
        with self.path.open("rb") as f:
            f.seek(self.offset)
            tail = f.read()
        return None if not tail else {"bytes": len(tail), "sha256": hashlib.sha256(tail).hexdigest()}


class NativeScreeningStream(SequenceStream):
    normalize = staticmethod(normalize_screening_record)

class AttemptStreams:
    def __init__(self, attempt_dir, sequences_output, screening_output, task, index, live_cutoff_epoch=None):
        self.sequence = SequenceStream(Path(attempt_dir) / "sequences.jsonl", sequences_output, task, index)
        self.screening = NativeScreeningStream(Path(attempt_dir) / "native_screening.jsonl", screening_output, task, index)
        self.sequence.live_cutoff_epoch = live_cutoff_epoch
        self.screening.live_cutoff_epoch = live_cutoff_epoch

    def scan(self, observed_epoch, before_cutoff):
        self.sequence.scan(observed_epoch, before_cutoff)
        self.screening.scan(observed_epoch, before_cutoff)

    @property
    def events(self):
        return self.sequence.events

    @property
    def errors(self):
        return ([dict(x, stream="sequence") for x in self.sequence.errors] +
                [dict(x, stream="native_screening") for x in self.screening.errors])

    def partial_tail(self):
        tails = {k: stream.partial_tail() for k, stream in
                 [("sequence", self.sequence), ("native_screening", self.screening)] if stream.partial_tail()}
        return tails or None

    def contract_errors(self):
        ids = [x["sequence_record_id"] for x in self.sequence.events]
        errors = []
        if len(set(ids)) != len(ids):
            errors.append({"stream": "sequence", "error": "Duplicate sequence_record_id within attempt"})
        if any(x["sequence_record_id"] not in ids for x in self.screening.events):
            errors.append({"stream": "native_screening", "error": "Update does not join any complete sequence"})
        return errors

def expanded_argv(method, fields):
    return [arg.format_map(fields) for arg in method["argv"]]

def kill_group(proc):
    # The leader may have exited while child GPU workers still own its group.
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    proc.wait()

def execute_attempt(argv, env, attempt_dir, stream, generation_deadline, poll_seconds=0.1):
    """Hard process-group cutoff; no retry, sleep, or acceptance filtering."""
    start_mono, start_epoch = time.monotonic(), time.time()
    stdout, stderr = Path(attempt_dir) / "stdout.log", Path(attempt_dir) / "stderr.log"
    boundary, interrupted, launch_error = False, None, None
    proc = None
    with stdout.open("xb") as out, stderr.open("xb") as err:
        try:
            proc = subprocess.Popen(argv, cwd=attempt_dir, env=env, stdout=out, stderr=err,
                                    start_new_session=True)
            while proc.poll() is None:
                mono, epoch = time.monotonic(), time.time()
                if mono >= generation_deadline:
                    boundary = True
                    kill_group(proc)
                    break
                stream.scan(epoch, True)
                time.sleep(min(poll_seconds, max(0, generation_deadline - mono)))
        except BaseException as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                interrupted = repr(exc)
            else:
                launch_error = repr(exc)
            if proc is not None:
                kill_group(proc)
    end_mono, end_epoch = time.monotonic(), time.time()
    stream.scan(end_epoch, end_mono <= generation_deadline)
    return {"started_at_epoch": start_epoch, "ended_at_epoch": end_epoch,
            "elapsed_seconds": end_mono - start_mono, "returncode": None if proc is None else proc.returncode,
            "boundary_censored": boundary, "interrupted": interrupted, "launch_error": launch_error,
            "stdout": record(stdout), "stderr": record(stderr)}

def classify_attempt(execution, adapter_result, sequence_events, stream_errors, partial_tail):
    if execution.get("boundary_censored"):
        if stream_errors:
            return "ENGINEERING_FAILURE", "Invalid sequence contract at budget boundary"
        return "TIMED_OUT_BOUNDARY", "Budget boundary reached"
    if execution.get("interrupted"):
        return "INTERRUPTED", execution["interrupted"]
    if execution.get("launch_error"):
        return "ENGINEERING_FAILURE", execution["launch_error"]
    if execution.get("returncode") != 0:
        return "ENGINEERING_FAILURE", "Adapter process returned nonzero"
    if stream_errors or partial_tail:
        return "ENGINEERING_FAILURE", "Invalid/truncated adapter sequence stream"
    if not isinstance(adapter_result, dict):
        return "ENGINEERING_FAILURE", "Missing adapter terminal result"
    status = adapter_result.get("status")
    if status not in {"COMPLETED", "SCIENTIFIC_REJECT", "ENGINEERING_FAILURE"}:
        return "ENGINEERING_FAILURE", "Invalid adapter terminal status"
    if status == "COMPLETED" and not sequence_events:
        return "ENGINEERING_FAILURE", "COMPLETED adapter emitted no complete sequence"
    return status, adapter_result.get("reason")


class PersistentSession:
    """One task-level private interpreter; filesystem RPC leaves library stdout free."""
    def __init__(self, argv, env, session_dir, generation_deadline, expected_ready):
        self.path = Path(session_dir)
        self.path.mkdir(parents=True, exist_ok=False)
        (self.path / "requests").mkdir()
        (self.path / "responses").mkdir()
        self.stdout_path, self.stderr_path = self.path / "stdout.log", self.path / "stderr.log"
        self.stdout_handle, self.stderr_handle = self.stdout_path.open("xb"), self.stderr_path.open("xb")
        self.argv, self.expected_ready = argv, expected_ready
        self.started_at_epoch = time.time()
        self.generation_deadline = generation_deadline
        self.deadline_reached = threading.Event()
        try:
            self.proc = subprocess.Popen(argv, cwd=self.path, env=env, stdout=self.stdout_handle,
                                         stderr=self.stderr_handle, start_new_session=True)
        except BaseException:
            self.stdout_handle.close()
            self.stderr_handle.close()
            raise
        self.timer = threading.Timer(max(0, generation_deadline - time.monotonic()), self.hard_deadline)
        self.timer.daemon = True
        self.timer.start()
        self.ready_receipt = None

    def hard_deadline(self):
        self.deadline_reached.set()
        kill_group(self.proc)

    def wait_ready(self, poll_seconds=0.05):
        ready_path = self.path / "READY.json"
        while not self.deadline_reached.is_set() and time.monotonic() < self.generation_deadline:
            if self.proc.poll() is not None:
                raise RuntimeError("Persistent session exited before READY: " + str(self.proc.returncode))
            if ready_path.exists():
                ready = read_json(ready_path)
                if ready.get("schema") != "paired-budget-session-v1" or ready.get("status") != "READY":
                    raise ValueError("Invalid session READY contract")
                if any(ready.get(k) != v for k, v in self.expected_ready.items()):
                    raise ValueError("Session READY source/config hash differs from frozen launcher")
                if ready.get("pid") is not None and ready["pid"] != self.proc.pid:
                    raise ValueError("Session READY PID does not match owned process")
                self.ready_receipt = record(ready_path)
                return True
            time.sleep(min(poll_seconds, max(0, self.generation_deadline - time.monotonic())))
        self.hard_deadline()
        return False

    def attempt(self, request, attempt_dir, stream, poll_seconds=0.05):
        start_mono, start_epoch = time.monotonic(), time.time()
        request_path = self.path / "requests" / (request["request_id"] + ".json")
        request_receipt = write_exclusive(request_path, request)
        response_path = self.path / "responses" / (request["request_id"] + ".json")
        stdout_start, stderr_start = self.stdout_path.stat().st_size, self.stderr_path.stat().st_size
        boundary, interrupted, error, response_receipt = False, None, None, None
        try:
            while True:
                mono, epoch = time.monotonic(), time.time()
                if self.deadline_reached.is_set() or mono >= self.generation_deadline:
                    boundary = True
                    self.hard_deadline()
                    break
                stream.scan(epoch, True)
                if stream.errors or stream.contract_errors():
                    raise ValueError("Invalid original sequence/native-screening contract")
                if response_path.exists():
                    response = read_json(response_path)
                    if response.get("schema") != "paired-budget-session-v1" or response.get("status") != "COMPLETE":
                        raise ValueError("Invalid RPC response contract")
                    if response.get("request_id") != request["request_id"]:
                        raise ValueError("RPC response does not match outstanding attempt")
                    result_path = verified(response["attempt_result"])
                    if result_path.resolve() != (Path(attempt_dir) / "attempt_result.json").resolve():
                        raise ValueError("RPC terminal result points outside attempt directory")
                    response_receipt = record(response_path)
                    break
                if self.proc.poll() is not None:
                    raise RuntimeError("Persistent session exited during attempt: " + str(self.proc.returncode))
                time.sleep(min(poll_seconds, max(0, self.generation_deadline - mono)))
        except BaseException as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                interrupted = repr(exc)
            else:
                error = repr(exc)
            self.stop()
        end_mono, end_epoch = time.monotonic(), time.time()
        stream.scan(end_epoch, end_mono <= self.generation_deadline)
        # Libraries may write task-level stdout. Frozen offsets bind each attempt
        # to the final task log; optional attempt-level files are independently pinned.
        out, err = Path(attempt_dir) / "stdout.log", Path(attempt_dir) / "stderr.log"
        out.touch(exist_ok=True); err.touch(exist_ok=True)
        return {"started_at_epoch": start_epoch, "ended_at_epoch": end_epoch,
                "elapsed_seconds": end_mono - start_mono, "transport": "persistent_session_rpc",
                "session_pid": self.proc.pid, "request": request_receipt, "response": response_receipt,
                "returncode": 0 if response_receipt else self.proc.returncode,
                "boundary_censored": boundary, "interrupted": interrupted, "launch_error": error,
                "stdout": record(out), "stderr": record(err),
                "session_stdout_offsets": [stdout_start, self.stdout_path.stat().st_size],
                "session_stderr_offsets": [stderr_start, self.stderr_path.stat().st_size]}

    def stop(self):
        self.timer.cancel()
        kill_group(self.proc)

    def final_record(self):
        self.stop()
        self.stdout_handle.close()
        self.stderr_handle.close()
        return {"schema": "paired-budget-session-v1", "argv": self.argv, "pid": self.proc.pid,
                "started_at_epoch": self.started_at_epoch, "ended_at_epoch": time.time(),
                "ready": self.ready_receipt, "deadline_reached": self.deadline_reached.is_set(),
                "returncode": self.proc.returncode, "stdout": record(self.stdout_path),
                "stderr": record(self.stderr_path)}

def _run_task(plan_path, task_id, output_dir, technical_rerun_of=None, expected_plan_sha256=None):
    if not os.environ.get("SLURM_JOB_ID"):
        raise RuntimeError("GPU task requires Slurm")
    plan = validate_frozen_plan(plan_path, expected_plan_sha256, require_expected=True)
    p = validate_protocol(plan["protocol"])
    task = task_by_id(plan, task_id)
    target = next(x for x in p["targets"] if x["target_id"] == task["target_id"])
    method = next(x for x in p["methods"] if x["method_id"] == task["method_id"])
    out = Path(output_dir)
    if out.exists():
        raise FileExistsError("Each allocation needs a new output directory")
    out.mkdir(parents=True)
    ledger, sequences = out / "attempts.jsonl", out / "sequences.jsonl"
    screening = out / "screening_updates.jsonl"
    ledger.touch(exist_ok=False)
    sequences.touch(exist_ok=False)
    screening.touch(exist_ok=False)
    rerun = None
    if technical_rerun_of:
        previous = read_json(technical_rerun_of)
        if previous["task"]["task_id"] != task_id or previous["status"] not in {
                "EARLY_ENGINEERING_FAILURE", "ENGINEERING_INTERRUPTION", "ALLOCATION_EXPIRED_BEFORE_GENERATION"}:
            raise ValueError("Technical rerun requires matching failed task, never scientific rejection")
        if not p.get("technical_amendment"):
            raise ValueError("Technical rerun requires an explicit frozen source amendment")
        if previous.get("plan") != p["technical_amendment"]["previous_plan_receipt"]:
            raise ValueError("Technical rerun old receipt differs from declared previous source plan")
        verified(previous["plan"])
        rerun = record(technical_rerun_of)
    key = allocation_key(os.environ)
    scontrol = subprocess.run(["scontrol", "show", "job", os.environ["SLURM_JOB_ID"], "-o"],
                              capture_output=True, text=True, check=True)
    scheduler = out / "scontrol_start.txt"
    scheduler.write_text(scontrol.stdout)
    allocation_start = allocation_anchor(scontrol.stdout)
    scheduler_alloc_tres = validate_scheduler_gpu_allocation(scontrol.stdout, p["gpu_count"])
    gen_deadline, alloc_deadline = budget_deadlines(allocation_start, time.time(), time.monotonic(),
        task["budget_gpu_seconds"], p["gpu_count"], p["shutdown_reserve_seconds"])
    hardware = gpu_probe(p["gpu_count"])
    if len(hardware["gpus"]) != p["gpu_count"] or any(x["name"] != p["hardware"]["gpu_name"]
                                                     for x in hardware["gpus"]):
        raise ValueError("Visible GPU hardware/count differs from frozen comparison")
    if "minimum_memory_mib" in p["hardware"] and any(
        x["memory_total_mib"] < p["hardware"]["minimum_memory_mib"] for x in hardware["gpus"]):
        raise ValueError("Visible GPU memory below frozen minimum")
    initial = {"schema": SCHEMA, "task": task, "plan": record(plan_path), "hardware": hardware,
               "allocation_key": key, "allocation_started_at_epoch": allocation_start,
               "scheduler_start": record(scheduler), "scheduler_alloc_tres": scheduler_alloc_tres,
               "launcher_plan_sha256": expected_plan_sha256, "technical_rerun_of": rerun,
               "runner_started_at_utc": utc(), "source_amendment": p.get("technical_amendment")}
    write_exclusive(out / "initial.json", initial)

    attempts, engineering_stop = [], False
    max_attempts = p.get("max_attempts_safety_limit", 1000000)
    if type(max_attempts) is not int or max_attempts <= 0:
        raise ValueError("Invalid safety limit")
    generation_cutoff_epoch = allocation_start + task["budget_gpu_seconds"] / p["gpu_count"] - p["shutdown_reserve_seconds"]
    allocation_deadline_epoch = allocation_start + task["budget_gpu_seconds"] / p["gpu_count"]
    session_dir = out / "session"
    base_fields = {"session_dir": str(session_dir), "target_manifest": target["input_manifest"]["path"],
        "target_id": task["target_id"], "method_id": task["method_id"], "task_id": task_id,
        "protocol_id": p["protocol_id"], "generation_deadline_epoch": str(generation_cutoff_epoch),
        "allocation_deadline_epoch": str(allocation_deadline_epoch),
        "protocol_sha256": plan["protocol_receipt"]["sha256"], "plan_sha256": initial["plan"]["sha256"],
        "method_config": method["config_receipt"]["path"], "method_config_sha256": method["config_receipt"]["sha256"],
        "method_definition_sha256": digest(method), "target_manifest_sha256": target["input_manifest"]["sha256"]}
    session_argv = [arg.format_map(base_fields) for arg in method["session_start"]]
    env = dict(os.environ, PYTHONNOUSERSITE="1", OPENBLAS_NUM_THREADS="1")
    env.pop("PYTHONPATH", None)
    env.update({str(k): str(v) for k, v in method.get("env", {}).items()})
    env.update({"BENCHMARK_TASK_ID": task_id, "BENCHMARK_PROTOCOL_ID": p["protocol_id"],
        "BENCHMARK_GENERATION_DEADLINE_EPOCH": str(generation_cutoff_epoch),
        "BENCHMARK_ALLOCATION_DEADLINE_EPOCH": str(allocation_deadline_epoch),
        "BENCHMARK_PROTOCOL_SHA256": base_fields["protocol_sha256"],
        "BENCHMARK_PLAN_SHA256": base_fields["plan_sha256"],
        "BENCHMARK_METHOD_CONFIG_SHA256": base_fields["method_config_sha256"],
        "BENCHMARK_METHOD_DEFINITION_SHA256": base_fields["method_definition_sha256"],
        "BENCHMARK_TARGET_MANIFEST_SHA256": base_fields["target_manifest_sha256"]})
    expected_ready = {k: base_fields[k] for k in ["protocol_sha256", "plan_sha256",
                       "method_config_sha256", "target_manifest_sha256"]}
    session, session_error, ready, session_receipt = None, None, False, None
    try:
        session = PersistentSession(session_argv, env, session_dir, gen_deadline, expected_ready)
        ready = session.wait_ready()
        while ready and time.monotonic() < gen_deadline and len(attempts) < max_attempts:
            index = len(attempts)
            attempt_dir = out / "attempts" / ("%06d" % index)
            attempt_dir.mkdir(parents=True)
            remaining = max(0.0, gen_deadline - time.monotonic())
            request = dict(base_fields, schema="paired-budget-session-v1", action="method-attempt",
                request_id="%06d" % index, attempt_index=index, attempt_dir=str(attempt_dir),
                seed=attempt_seed(task, index), replicate_seed=task["seed"], remaining_seconds=remaining,
                generation_deadline_epoch=generation_cutoff_epoch, deadline_epoch=generation_cutoff_epoch,
                allocation_deadline_epoch=allocation_deadline_epoch)
            stream = AttemptStreams(attempt_dir, sequences, screening, task, index, generation_cutoff_epoch)
            execution = session.attempt(request, attempt_dir, stream)
            result_path = attempt_dir / "attempt_result.json"
            adapter, result_error = None, None
            if result_path.exists():
                try:
                    adapter = read_json(result_path)
                except Exception as exc:
                    result_error = repr(exc)
            status, reason = classify_attempt(execution, adapter, stream.events,
                stream.errors + stream.contract_errors(), stream.partial_tail())
            entry = {"task_id": task_id, "attempt_index": index, "attempt_seed": request["seed"],
                "argv": session_argv, "status": status, "reason": reason, "execution": execution,
                "adapter_result": None if not result_path.exists() else record(result_path),
                "adapter_result_parse_error": result_error,
                "adapter_declared_status": None if adapter is None else adapter.get("status"),
                "raw_sequence_stream": record(stream.sequence.path) if stream.sequence.path.exists() else None,
                "raw_native_screening_stream": record(stream.screening.path) if stream.screening.path.exists() else None,
                "complete_sequence_records": len(stream.events),
                "precutoff_sequence_records": sum(x["observed_before_generation_cutoff"] for x in stream.events),
                "screening_update_records": len(stream.screening.events),
                "precutoff_screening_update_records": sum(x["observed_before_generation_cutoff"] for x in stream.screening.events),
                "stream_errors": stream.errors + stream.contract_errors(), "partial_sequence_tail": stream.partial_tail()}
            append_durable(ledger, entry)
            attempts.append(entry)
            if status in {"ENGINEERING_FAILURE", "INTERRUPTED"}:
                engineering_stop = True
                break
            if status == "TIMED_OUT_BOUNDARY":
                break
    except BaseException as exc:
        session_error = repr(exc)
        engineering_stop = True
    finally:
        if session is not None:
            session_receipt = session.final_record()

    if engineering_stop:
        status = "ENGINEERING_INTERRUPTION" if attempts and attempts[-1]["status"] == "INTERRUPTED" else "EARLY_ENGINEERING_FAILURE"
    elif not attempts and not (session is not None and session.deadline_reached.is_set()):
        status = "ALLOCATION_EXPIRED_BEFORE_GENERATION"
    elif len(attempts) >= max_attempts and time.monotonic() < gen_deadline:
        status = "EARLY_ENGINEERING_FAILURE"
    else:
        status = "BUDGET_EXHAUSTED_WITH_EXPLICIT_BOUNDARY_CENSORING"
    result = dict(initial, status=status, attempt_ledger=record(ledger), sequence_ledger=record(sequences),
                  native_screening_ledger=record(screening), session=session_receipt,
                  session_error=session_error, session_initialization_boundary_censored=not ready and not engineering_stop,
                  execution_mode="persistent_session", attempt_count=len(attempts), generation_finished_at_utc=utc(),
                  generation_cutoff_epoch=allocation_start + task["budget_gpu_seconds"] / p["gpu_count"] - p["shutdown_reserve_seconds"],
                  allocation_deadline_epoch=allocation_start + task["budget_gpu_seconds"] / p["gpu_count"],
                  accounting_status="PENDING_INDEPENDENT_SACCT_ACCOUNTING",
                  comparable_full_budget=status == "BUDGET_EXHAUSTED_WITH_EXPLICIT_BOUNDARY_CENSORING",
                  engineering_safety_limit_reached=len(attempts) >= max_attempts and time.monotonic() < gen_deadline)
    receipt = write_exclusive(out / "run_receipt.json", result)
    # Normal budget exhaustion may finalize within the identical reserved tail.
    # Engineering stops release the GPU immediately; no artificial budget fill.
    if result["comparable_full_budget"]:
        while time.monotonic() < alloc_deadline:
            time.sleep(min(0.1, alloc_deadline - time.monotonic()))
    print(canonical({"receipt": receipt, "status": status}))
    return result


def run_task(plan_path, task_id, output_dir, technical_rerun_of=None, expected_plan_sha256=None):
    """Preserve an engineering receipt even when GPU preflight fails."""
    try:
        return _run_task(plan_path, task_id, output_dir, technical_rerun_of, expected_plan_sha256)
    except BaseException as exc:
        out = Path(output_dir)
        if (out / "run_receipt.json").exists():
            # The normal receipt is durable before the fixed finalization tail.
            return read_json(out / "run_receipt.json")
        if not os.environ.get("SLURM_JOB_ID"):
            raise
        plan = read_json(plan_path)
        task = task_by_id(plan, task_id)
        out.mkdir(parents=True, exist_ok=True)
        ledger, sequences = out / "attempts.jsonl", out / "sequences.jsonl"
        screening = out / "screening_updates.jsonl"
        ledger.touch(exist_ok=True)
        sequences.touch(exist_ok=True)
        screening.touch(exist_ok=True)
        initial = read_json(out / "initial.json") if (out / "initial.json").exists() else {}
        sched = out / "scontrol_start.txt"
        anchor = None
        if sched.exists():
            try:
                anchor = allocation_anchor(sched.read_text())
            except Exception:
                pass
        result = dict(initial, schema=SCHEMA, task=task, plan=record(plan_path),
                      allocation_key=allocation_key(os.environ),
                      hardware=initial.get("hardware", {"gpus": []}),
                      status="EARLY_ENGINEERING_FAILURE", attempt_count=len(rows_jsonl(ledger)),
                      attempt_ledger=record(ledger), sequence_ledger=record(sequences),
                      native_screening_ledger=record(screening),
                      generation_cutoff_epoch=None if anchor is None else anchor +
                          task["budget_gpu_seconds"] / plan["protocol"]["gpu_count"] -
                          plan["protocol"]["shutdown_reserve_seconds"],
                      accounting_status="PENDING_INDEPENDENT_SACCT_ACCOUNTING",
                      comparable_full_budget=False, fatal_error=repr(exc),
                      fatal_error_at_utc=utc(), technical_rerun_of=None if not technical_rerun_of else record(technical_rerun_of))
        write_exclusive(out / "run_receipt.json", result)
        print(canonical({"status": result["status"], "fatal_error": result["fatal_error"]}))
        return result

def inventory_from_ledgers(run_receipts):
    inventory, task_rows = {}, []
    for receipt in run_receipts:
        run = read_json(verified(receipt))
        attempts = rows_jsonl(verified(run["attempt_ledger"]))
        events = rows_jsonl(verified(run["sequence_ledger"]))

        updates = [] if not run.get("native_screening_ledger") else rows_jsonl(verified(run["native_screening_ledger"]))
        sequence_ids = {(x["attempt_index"], x["sequence_record_id"]) for x in events}
        if len(sequence_ids) != len(events):
            raise ValueError("Duplicate sequence_record_id within an attempt")
        for update in updates:
            if update["task_id"] != run["task"]["task_id"] or (update["attempt_index"], update["sequence_record_id"]) not in sequence_ids:
                raise ValueError("Native screening update does not join original sequence")
            if update["observed_before_generation_cutoff"] and update["observed_at_epoch"] > run["generation_cutoff_epoch"] + 0.01:
                raise ValueError("Postcutoff native update marked eligible")
            normalize_screening_record(update, run["task"], update["attempt_index"],
                                       update["source_line_number"], update["observed_at_epoch"],
                                       update["observed_before_generation_cutoff"])
        for event in events:
            event["raw_internal_acceptance"] = event["internal_acceptance"]
            event["raw_native_score"] = event["native_score"]
            relevant = [u for u in updates if u["attempt_index"] == event["attempt_index"]
                        and u["sequence_record_id"] == event["sequence_record_id"]]
            event["native_screening_updates"] = relevant
            for update in sorted(relevant, key=lambda x: x["source_line_number"]):
                if not update["observed_before_generation_cutoff"]:
                    continue
                for field in ("internal_acceptance", "native_score", "native_score_name"):
                    if update.get(field) is not None:
                        event[field] = update[field]

        indices = [x["attempt_index"] for x in attempts]
        if indices != list(range(len(attempts))) or any(x["status"] not in TERMINAL for x in attempts):
            raise ValueError("Attempt ledger is not a complete contiguous terminal ledger")
        if run["attempt_count"] != len(attempts):
            raise ValueError("Run attempt count differs from raw ledger")
        counts = {status: sum(x["status"] == status for x in attempts) for status in sorted(TERMINAL)}
        by_attempt = {i: [] for i in indices}
        for event in events:
            if event["task_id"] != run["task"]["task_id"] or event["attempt_index"] not in by_attempt:
                raise ValueError("Sequence lineage does not join attempt ledger")
            sequence = normalize_sequence(event["sequence"])
            if hashlib.sha256(sequence.encode()).hexdigest() != event["sequence_sha256"]:
                raise ValueError("Sequence SHA mismatch")
            if event["observed_before_generation_cutoff"] and event["observed_at_epoch"] > run["generation_cutoff_epoch"] + 0.01:
                raise ValueError("Candidate observed after cutoff was marked eligible")
            by_attempt[event["attempt_index"]].append(event)
            key = (event["task_id"], event["sequence_sha256"])
            if key not in inventory:
                inventory[key] = {"task_id": event["task_id"], "target_id": event["target_id"],
                                  "method_id": event["method_id"], "seed": event["seed"],
                                  "sequence": sequence, "sequence_sha256": event["sequence_sha256"], "occurrences": []}
            inventory[key]["occurrences"].append(dict(event, run_receipt=receipt))
        for attempt in attempts:
            ev = by_attempt[attempt["attempt_index"]]
            if attempt["complete_sequence_records"] != len(ev):
                raise ValueError("Attempt sequence count differs from raw stream")
            if attempt["precutoff_sequence_records"] != sum(x["observed_before_generation_cutoff"] for x in ev):
                raise ValueError("Attempt precutoff sequence count differs from raw stream")
            upd = [x for x in updates if x["attempt_index"] == attempt["attempt_index"]]
            if attempt.get("screening_update_records", 0) != len(upd):
                raise ValueError("Native screening update count differs from raw stream")
            if attempt.get("precutoff_screening_update_records", 0) != sum(x["observed_before_generation_cutoff"] for x in upd):
                raise ValueError("Precutoff native screening count differs from raw stream")
        task_rows.append({"task": run["task"], "run_receipt": receipt, "allocation_key": run["allocation_key"],
                          "hardware": run["hardware"], "status": run["status"],
                          "technical_rerun_of": run.get("technical_rerun_of"), "attempt_count": len(attempts),
                          "attempt_status_counts": counts, "sequence_record_count": len(events),
                          "precutoff_sequence_record_count": sum(x["observed_before_generation_cutoff"] for x in events),
                          "native_accepted_attempts": sum(any(e["internal_acceptance"] is True for e in ev) for ev in by_attempt.values()),
                          "boundary_observed_sequences": sum(not x["observed_before_generation_cutoff"] for x in events)})
    result = []
    for key in sorted(inventory):
        entry = inventory[key]
        entry["eligible_uniform"] = any(x["observed_before_generation_cutoff"] for x in entry["occurrences"])
        entry["lineage_ids"] = sorted({x["lineage_id"] for x in entry["occurrences"]})
        result.append(entry)
    return result, task_rows

def parse_alloc_tres_gpu(text):
    tokens = text.split(",")
    specific, generic = [], None
    for token in tokens:
        key, sep, value = token.partition("=")
        if not sep or not key.startswith("gres/gpu"):
            continue
        n = int(value)
        if n < 0:
            raise ValueError("Negative GPU allocation")
        if key == "gres/gpu":
            generic = n
        elif key.startswith("gres/gpu:"):
            specific.append(n)
    if generic is not None:
        if specific and sum(specific) != generic:
            raise ValueError("Generic and typed GPU counts disagree")
        return generic
    return sum(specific)

def parse_sacct(text):
    """Accept headers or headerless JobIDRaw|ElapsedRaw|AllocTRES|State|Start|End|NodeList|Partition."""
    allocations, excluded = {}, []
    for line in text.splitlines():
        if not line.strip():
            continue
        cells = next(csv.reader([line], delimiter="|"))
        if cells and cells[-1] == "":
            cells.pop()
        if cells[0] == "JobIDRaw":
            continue
        if len(cells) != 8:
            raise ValueError("Unexpected sacct field count")
        job, elapsed, tres, state, start, end, node, partition = cells
        if "." in job or "[" in job:
            excluded.append({"job_id": job, "reason": "job step or array summary"})
            continue
        if job in allocations:
            raise ValueError("Duplicate allocation row: " + job)
        if not re.fullmatch(r"\d+(?:_\d+)?", job):
            raise ValueError("Unexpected allocation job ID")
        seconds = int(elapsed)
        if seconds < 0:
            raise ValueError("Negative elapsed")
        allocations[job] = {"job_id": job, "elapsed_seconds": seconds,
            "gpu_count": parse_alloc_tres_gpu(tres), "alloc_tres": tres, "state": state.split()[0],
            "start": start, "end": end, "node": node, "partition": partition}
    return allocations, excluded

def independent_accounting(plan, run_receipts, sacct_text):
    inventory, task_rows = inventory_from_ledgers(run_receipts)
    allocations, excluded = parse_sacct(sacct_text)
    p = plan["protocol"]
    results, used = [], set()
    for row in task_rows:
        key = row["allocation_key"]
        if key in used:
            raise ValueError("Same allocation counted twice")
        used.add(key)
        if key not in allocations:
            raise ValueError("Missing raw scheduler allocation: " + key)
        actual = allocations[key]
        task = task_by_id(plan, row["task"]["task_id"])
        if row["task"] != task:
            raise ValueError("Task differs from frozen plan")
        if actual["gpu_count"] != p["gpu_count"]:
            raise ValueError("Scheduler GPU count differs from frozen protocol")
        actual_gpu_seconds = actual["elapsed_seconds"] * actual["gpu_count"]
        budget = task["budget_gpu_seconds"]
        delta = actual_gpu_seconds - budget
        tolerance = p.get("accounting_tolerance_seconds", 0) * p["gpu_count"]
        complete = row["status"] == "BUDGET_EXHAUSTED_WITH_EXPLICIT_BOUNDARY_CENSORING"
        hardware_match = len(row["hardware"]["gpus"]) == p["gpu_count"] and all(
            x["name"] == p["hardware"]["gpu_name"] for x in row["hardware"]["gpus"])
        terminal = actual["state"] in {"COMPLETED", "TIMEOUT"}
        comparable = complete and hardware_match and terminal and abs(delta) <= tolerance
        row.update({"scheduler_allocation": actual, "allocated_gpu_seconds": actual_gpu_seconds,
                    "nominal_gpu_seconds": budget, "allocated_gpu_seconds_minus_budget": delta,
                    "comparable_full_budget": comparable,
                    "comparison_exclusions": ([] if comparable else [
                        reason for flag, reason in [(not complete, "Engineering/early stop"),
                        (not hardware_match, "Hardware mismatch"), (not terminal, "Nonaccepted scheduler state"),
                        (abs(delta) > tolerance, "Realized allocation differs beyond frozen tolerance")] if flag])})
        results.append(row)
    omitted = sorted(set(allocations) - used)
    if any(allocations[k]["gpu_count"] > 0 and allocations[k]["elapsed_seconds"] > 0 for k in omitted):
        raise ValueError("Positive GPU allocation has no preserved run receipt: " + ",".join(omitted))
    return {"schema": SCHEMA, "status": "RAW_LEDGER_AND_SCHEDULER_ACCOUNTING_COMPLETE",
            "tasks": results, "inventory": inventory, "excluded_sacct_rows": excluded,
            "unjoined_allocation_rows": omitted, "allocated_gpu_seconds_all_attempts": sum(
                x["allocated_gpu_seconds"] for x in results),
            "all_attempt_count": sum(x["attempt_count"] for x in results),
            "all_run_receipts": run_receipts,
            "warning": "Engineering reruns count toward all resource use; only one accepted full-budget allocation per frozen task can define the primary comparison"}

def sampling_key(salt, target_id, seed, seq_sha):
    return hashlib.sha256(canonical([salt, target_id, seed, seq_sha]).encode()).hexdigest()

def cohorts(plan, inventory, task_rows):
    p = plan["protocol"]
    primary_rows = {}
    for row in task_rows:
        if row["comparable_full_budget"]:
            task_id = row["task"]["task_id"]
            if task_id in primary_rows:
                raise ValueError("Multiple accepted allocations for a frozen task; no post-result run selection allowed")
            primary_rows[task_id] = row
    selected, coverage = [], []
    for task in plan["tasks"]:
        task_id = task["task_id"]
        primary = primary_rows.get(task_id)
        eligible = [] if primary is None else [
            x for x in inventory if x["task_id"] == task_id and x["eligible_uniform"] and any(
                y["observed_before_generation_cutoff"] and y["run_receipt"] == primary["run_receipt"] for y in x["occurrences"])]
        method = next(x for x in p["methods"] if x["method_id"] == task["method_id"])
        salt = p["sampling"]["salt"]
        uniform = sorted(eligible, key=lambda x: sampling_key(salt, task["target_id"], task["seed"], x["sequence_sha256"]))
        native = []
        for x in eligible:
            scores = [y["native_score"] for y in x["occurrences"]
                      if y["observed_before_generation_cutoff"] and y["native_score"] is not None
                      and y["native_score_name"] == method["native_score_name"]
                      and y["run_receipt"] == primary["run_receipt"]]
            if scores:
                x = dict(x, selected_native_score=max(scores) if method["native_score_direction"] == "higher" else min(scores))
                native.append(x)
        sign = -1 if method["native_score_direction"] == "higher" else 1
        native.sort(key=lambda x: (sign * x["selected_native_score"], x["sequence_sha256"]))
        group = {"task": task, "primary_run_receipt": None if primary is None else primary["run_receipt"],
                 "comparison_status": "ACCEPTED_FULL_BUDGET" if primary else "UNRESOLVED_NO_ACCEPTED_FULL_BUDGET",
                 "n_unique_complete": len(eligible), "n_native_score_available": len(native),
                 "n_native_score_missing": len(eligible) - len(native)}
        for name, candidates, limit in [
            ("uniform_all_complete", uniform, p["sampling"]["uniform_n_per_replicate"]),
            ("native_fixed_top_k", native, p["sampling"]["native_top_k_per_replicate"])]:
            group[name] = {"requested": limit, "selected": min(len(candidates), limit),
                           "underfilled": len(candidates) < limit}
            for x in candidates[:limit]:
                item = {"task_id": task_id, "target_id": task["target_id"], "method_id": task["method_id"],
                        "seed": task["seed"], "cohort": name, "sequence": x["sequence"],
                        "sequence_sha256": x["sequence_sha256"], "lineage_ids": x["lineage_ids"],
                        "sampling_key": sampling_key(salt, task["target_id"], task["seed"], x["sequence_sha256"]),
                        "primary_run_receipt": primary["run_receipt"],
                        "internal_acceptance_values": sorted({str(y["internal_acceptance"]) for y in x["occurrences"]}),
                        "native_score": x.get("selected_native_score")}
                item["cohort_record_id"] = digest({k: item[k] for k in [
                    "task_id", "cohort", "sequence_sha256", "primary_run_receipt"]})
                selected.append(item)
        coverage.append(group)
    return {"schema": SCHEMA, "status": "PREDECLARED_COHORTS_SELECTED_FROM_ALL_COMPLETE_SEQUENCES",
            "plan": plan["protocol_receipt"], "coverage": coverage, "selected": selected,
            "uniform_selection_ignores_native_score_and_internal_acceptance": True,
            "native_top_k_scope": "Native scalar score across all complete unique sequences; separate from primary uniform cohort"}

def evaluator_rates(selected, outcomes):
    ids = {x["cohort_record_id"] for x in selected}
    mapped = {}
    for outcome in outcomes:
        rid = outcome["cohort_record_id"]
        if rid in mapped or rid not in ids:
            raise ValueError("Duplicate or unknown evaluator outcome")
        passed, evaluable = outcome.get("pass"), outcome.get("evaluable")
        if type(evaluable) is not bool or (evaluable and type(passed) is not bool) or (not evaluable and passed is not None):
            raise ValueError("Missing/failed evaluation must remain null, never a negative")
        mapped[rid] = outcome
    evaluated = [mapped[x["cohort_record_id"]] for x in selected
                 if x["cohort_record_id"] in mapped and mapped[x["cohort_record_id"]]["evaluable"]]
    npass = sum(x["pass"] for x in evaluated)
    n = len(selected)
    missing = n - len(evaluated)
    return {"n_selected": n, "n_evaluable": len(evaluated), "n_pass": npass,
            "n_fail": len(evaluated) - npass, "n_missing": missing,
            "complete_case_pass_rate": None if not evaluated else npass / len(evaluated),
            "all_selected_pass_rate": None if n == 0 or missing else npass / n,
            "all_selected_pass_rate_bounds": None if n == 0 else [npass / n, (npass + missing) / n]}

def target_bootstrap(effects, minimum_targets, replicates, seed):
    # Target is the resampling unit; model seeds never increase n.
    if len(effects) < minimum_targets:
        return {"status": "DESCRIPTIVE_ONLY_INSUFFICIENT_TARGETS", "n_targets": len(effects), "interval_95": None}
    import random
    rng = random.Random(seed)
    values = sorted(statistics.mean(rng.choices(effects, k=len(effects))) for _ in range(replicates))
    def quantile(q):
        pos = q * (len(values) - 1)
        a, b = math.floor(pos), math.ceil(pos)
        return values[a] + (values[b] - values[a]) * (pos - a)
    return {"status": "PREDECLARED_TARGET_BOOTSTRAP", "n_targets": len(effects),
            "replicates": replicates, "seed": seed, "interval_95": [quantile(0.025), quantile(0.975)],
            "scope": "Target-resampled descriptive uncertainty; no automatic significance or superiority claim"}

def summarize(plan, accounting, cohort_data, outcomes):
    # Outcome IDs are validated jointly before groupwise summaries.
    evaluator_rates(cohort_data["selected"], outcomes)
    p = plan["protocol"]
    raw = []
    task_account = {x["task"]["task_id"]: x for x in accounting["tasks"] if x["comparable_full_budget"]}
    for coverage in cohort_data["coverage"]:
        task = coverage["task"]
        row = task_account.get(task["task_id"])
        data = dict(coverage)
        for name in ("uniform_all_complete", "native_fixed_top_k"):
            selected = [x for x in cohort_data["selected"] if x["task_id"] == task["task_id"] and x["cohort"] == name]
            ids = {x["cohort_record_id"] for x in selected}
            rates = evaluator_rates(selected, [x for x in outcomes if x["cohort_record_id"] in ids])
            rates["observed_uniform_passes_per_allocated_gpu_hour"] = None if name != "uniform_all_complete" or row is None else (
                rates["n_pass"] * 3600 / row["allocated_gpu_seconds"])
            rates["fully_observed_uniform_passes_per_allocated_gpu_hour"] = None if (
                name != "uniform_all_complete" or row is None or rates["n_missing"]) else (
                rates["n_pass"] * 3600 / row["allocated_gpu_seconds"])
            data[name] = dict(coverage[name], evaluation=rates)
        if row:
            data["all_attempt_denominator"] = row["attempt_count"]
            data["native_accepted_attempt_fraction"] = None if not row["attempt_count"] else (
                row["native_accepted_attempts"] / row["attempt_count"])
            data["attempt_status_counts"] = row["attempt_status_counts"]
            data["allocated_gpu_seconds"] = row["allocated_gpu_seconds"]
        else:
            data["all_attempt_denominator"] = None
            data["native_accepted_attempt_fraction"] = None
        raw.append(data)
    paired = []
    method_ids = [x["method_id"] for x in p["methods"]]
    for target in p["targets"]:
        fields = {}
        complete = True
        for method in method_ids:
            reps = [x for x in raw if x["task"]["target_id"] == target["target_id"] and x["task"]["method_id"] == method]
            ys = [x["uniform_all_complete"]["evaluation"]["fully_observed_uniform_passes_per_allocated_gpu_hour"] for x in reps]
            if len(reps) != len(p["replicate_seeds"]) or any(x is None for x in ys):
                fields[method] = None
                complete = False
            else:
                fields[method] = statistics.mean(ys)
        paired.append({"target_id": target["target_id"], "analysis_role": target.get("analysis_role", "primary"),
                       "per_method_mean_uniform_passes_per_gpu_hour": fields,
                       "effect_first_minus_second": fields[method_ids[0]] - fields[method_ids[1]] if complete else None,
                       "status": "COMPLETE_PAIRED_TARGET" if complete else "UNRESOLVED_MISSING_REPLICATE_OR_EVALUATION"})
    effects = [x["effect_first_minus_second"] for x in paired
               if x["analysis_role"] == "primary" and x["effect_first_minus_second"] is not None]
    # A complete predeclared target matrix is required; no dropping difficult targets for inference.
    inf = p.get("inference", {})
    if len(effects) != sum(x.get("analysis_role", "primary") == "primary" for x in p["targets"]):
        inference = {"status": "DESCRIPTIVE_ONLY_INCOMPLETE_FROZEN_TARGET_MATRIX", "n_targets": len(effects), "interval_95": None}
    elif inf.get("mode", "descriptive_only") == "descriptive_only":
        inference = {"status": "PREDECLARED_DESCRIPTIVE_ONLY", "n_targets": len(effects), "interval_95": None}
    else:
        inference = target_bootstrap(effects, inf.get("minimum_targets", 6),
            inf.get("bootstrap_replicates", 2000), inf.get("bootstrap_seed", 4142))
    return {"schema": SCHEMA, "status": "PAIRED_COMPUTATIONAL_BENCHMARK_SUMMARIZED_WITH_EXPLICIT_MISSINGNESS",
            "method_order": method_ids, "statistical_unit": "target",
            "n_frozen_primary_targets": sum(x.get("analysis_role", "primary") == "primary" for x in p["targets"]),
            "n_frozen_diagnostic_targets": sum(x.get("analysis_role", "primary") == "diagnostic" for x in p["targets"]),
            "per_replicate_raw": raw,
            "paired_target_effects": paired, "target_effect_mean": None if not effects else statistics.mean(effects),
            "inference": inference, "all_attempt_count": accounting["all_attempt_count"],
            "all_allocated_gpu_seconds": accounting["allocated_gpu_seconds_all_attempts"],
            "scientific_scope": "Common external evaluator computational pass yield; no experimental binding/blockade or general workflow superiority proof"}

def require_slurm():
    if not os.environ.get("SLURM_JOB_ID"):
        raise RuntimeError("Production data operations require Slurm")

def main():
    def interrupted_by_scheduler(signum, frame):
        raise KeyboardInterrupt("scheduler signal " + str(signum))
    signal.signal(signal.SIGTERM, interrupted_by_scheduler)
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("freeze")
    p.add_argument("--protocol", required=True); p.add_argument("--output", required=True)
    p = sub.add_parser("run-task")
    p.add_argument("--plan", required=True); p.add_argument("--task-id", required=True); p.add_argument("--output-dir", required=True)
    p.add_argument("--technical-rerun-of"); p.add_argument("--plan-sha256", required=True)
    p = sub.add_parser("account")
    p.add_argument("--plan", required=True); p.add_argument("--run-receipts", required=True)
    p.add_argument("--sacct", required=True); p.add_argument("--output", required=True)
    p = sub.add_parser("cohort")
    p.add_argument("--plan", required=True); p.add_argument("--accounting", required=True); p.add_argument("--output", required=True)
    p = sub.add_parser("summarize")
    p.add_argument("--plan", required=True); p.add_argument("--accounting", required=True)
    p.add_argument("--cohort", required=True); p.add_argument("--outcomes", required=True); p.add_argument("--output", required=True)
    args = parser.parse_args()
    require_slurm()
    if args.command == "freeze":
        freeze_protocol(args.protocol, args.output)
    elif args.command == "run-task":
        result = run_task(args.plan, args.task_id, args.output_dir, args.technical_rerun_of, args.plan_sha256)
        if not result["comparable_full_budget"]:
            sys.exit(2)
    elif args.command == "account":
        plan = validate_frozen_plan(args.plan)
        out = independent_accounting(plan, read_json(args.run_receipts), Path(args.sacct).read_text())
        out.update({"plan": record(args.plan), "raw_sacct": record(args.sacct)})
        write_exclusive(args.output, out)
    elif args.command == "cohort":
        plan, accounting = validate_frozen_plan(args.plan), read_json(args.accounting)
        out = cohorts(plan, accounting["inventory"], accounting["tasks"])
        out.update({"frozen_plan": record(args.plan), "accounting": record(args.accounting)})
        write_exclusive(args.output, out)
    else:
        plan, accounting, cohort_data = validate_frozen_plan(args.plan), read_json(args.accounting), read_json(args.cohort)
        out = summarize(plan, accounting, cohort_data, read_json(args.outcomes))
        out.update({"frozen_plan": record(args.plan), "accounting": record(args.accounting),
                    "cohort": record(args.cohort), "outcomes": record(args.outcomes)})
        write_exclusive(args.output, out)
    print("COMPLETE", args.command)

if __name__ == "__main__":
    main()

