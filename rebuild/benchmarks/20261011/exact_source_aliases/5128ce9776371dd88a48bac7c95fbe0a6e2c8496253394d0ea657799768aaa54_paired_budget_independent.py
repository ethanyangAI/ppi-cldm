#!/usr/bin/env python3
"""Independent bookkeeping audit. Does not import the production orchestrator."""
import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys

AA = set("ACDEFGHIKLMNPQRSTVWY")
TERMINAL = {"COMPLETED", "SCIENTIFIC_REJECT", "ENGINEERING_FAILURE", "TIMED_OUT_BOUNDARY", "INTERRUPTED"}

def canonical(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

def hash_object(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()

def rec(path):
    p = Path(path).resolve()
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return {"path": str(p), "bytes": p.stat().st_size, "sha256": h.hexdigest()}

def verify(r):
    actual = rec(r["path"])
    if any(actual[k] != r[k] for k in actual):
        raise ValueError("Independent receipt mismatch " + r["path"])
    return Path(r["path"])

def load(path):
    return json.loads(Path(path).read_text())

def jsonl(path):
    result = []
    for i, line in enumerate(Path(path).read_text().splitlines(keepends=True), 1):
        if not line.endswith("\n"):
            raise ValueError("Independent partial ledger line " + str(i))
        result.append(json.loads(line))
    return result

def scheduler_rows(text):
    rows, excluded = {}, []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split("|")
        if parts[-1] == "":
            parts.pop()
        if parts[0] == "JobIDRaw":
            continue
        if len(parts) == 8:
            jid, elapsed, tres, state, start, end, node, partition = parts
            alias = None
        elif len(parts) == 9:
            jid, alias, elapsed, tres, state, start, end, node, partition = parts
        else:
            raise ValueError("Unexpected scheduler format")
        if any("." in x or "[" in x for x in (jid, alias or "")):
            excluded.append(jid)
            continue
        if not re.fullmatch(r"\d+", jid) or (alias is not None and not re.fullmatch(r"\d+(?:_\d+)?", alias)):
            raise ValueError("Scheduler raw physical ID or logical alias is invalid")
        if jid in rows:
            raise ValueError("Duplicate physical scheduler allocation")
        specific = [int(n) for key, n in re.findall(r"(gres/gpu(?::[^,=]+)?)=(\d+)", tres) if key != "gres/gpu"]
        generic = re.search(r"(?:^|,)gres/gpu=(\d+)(?:,|$)", tres)
        ngpu = int(generic[1]) if generic else sum(specific)
        if generic and specific and sum(specific) != ngpu:
            raise ValueError("Typed/generic GPU TRES disagree")
        if int(elapsed) < 0:
            raise ValueError("Negative physical allocation elapsed")
        rows[jid] = {"seconds": int(elapsed), "ngpu": ngpu, "state": state.split()[0], "node": node,
            "job_id_alias": alias, "partition": partition, "start": start, "end": end}
    return rows, excluded

def selected_scheduler_record(run, text):
    selected = []
    for line in text.splitlines():
        if not line.strip():
            continue
        ids = re.findall(r"\bJobId=(\S+)", line)
        masters = re.findall(r"\bArrayJobId=(\S+)", line)
        indexes = re.findall(r"\bArrayTaskId=(\S+)", line)
        if len(ids) != 1 or not ids[0].isdigit() or len(masters) > 1 or len(indexes) > 1:
            raise ValueError("Invalid individual scheduler record identity")
        logical = masters[0] + "_" + indexes[0] if masters and indexes else ids[0]
        if logical == run["allocation_key"]:
            selected.append(line.strip() + "\n")
    if len(selected) != 1:
        raise ValueError("Original scheduler output has no unique logical allocation match")
    if "scheduler_selected_record" in run and run["scheduler_selected_record"] != selected[0]:
        raise ValueError("Declared selected scheduler record differs from original output")
    return selected[0]

def allocation_identity(run):
    """Independent original-scontrol physical identity reconstruction."""
    if not run.get("scheduler_start"):
        raise ValueError("Preserved original scheduler_start receipt required")
    text = selected_scheduler_record(run, Path(verify(run["scheduler_start"])).read_text())
    values = {}
    for field in ("JobId", "ArrayJobId", "ArrayTaskId"):
        tokens = re.findall(r"\b" + field + r"=(\S+)", text)
        if len(tokens) > 1:
            raise ValueError("Repeated physical allocation identity field")
        values[field] = tokens[0] if tokens else None
    jid, master, index = values["JobId"], values["ArrayJobId"], values["ArrayTaskId"]
    if not jid or not re.fullmatch(r"\d+", jid):
        raise ValueError("Original JobId is not a numeric physical allocation")
    if bool(master) != bool(index) or (master and (not master.isdigit() or not index.isdigit())):
        raise ValueError("Original array allocation identity is incomplete")
    logical = master + "_" + index if master else jid
    expected = {"raw_allocation_id": jid, "logical_allocation_key": logical,
                "array_job_id": master, "array_task_id": index}
    if run["allocation_key"] != logical:
        raise ValueError("Run logical alias contradicts original scheduler")
    for field in ("raw_allocation_id", "logical_allocation_key"):
        if field in run and run[field] != expected[field]:
            raise ValueError("Run allocation ID contradicts original scheduler")
    if "allocation_identity" in run and run["allocation_identity"] != expected:
        raise ValueError("Stored allocation identity contradicts original scheduler")
    return expected

def expected_tasks(protocol):
    tasks = []
    for target in protocol["targets"]:
        for seed in protocol["replicate_seeds"]:
            pair = {"protocol_id": protocol["protocol_id"], "target_id": target["target_id"], "seed": seed}
            for method in protocol["methods"]:
                key = dict(pair, method_id=method["method_id"])
                tasks.append(dict(key, task_id=hash_object(key)[:24], pair_id=hash_object(pair)[:24],
                    budget_gpu_seconds=target.get("budget_gpu_seconds", protocol["budget_gpu_seconds"]),
                    array_index=len(tasks)))
    return tasks

def selected_ids(plan, inventory, primary):
    p = plan["protocol"]
    expected, coverage = [], {}
    for task in plan["tasks"]:
        tid = task["task_id"]
        run = primary.get(tid)
        candidates = [] if run is None else [x for x in inventory.values() if x["task_id"] == tid and
            any(y["eligible"] and y["run_receipt"] == run for y in x["occurrences"])]
        method = next(x for x in p["methods"] if x["method_id"] == task["method_id"])
        def uniform_key(x):
            return hashlib.sha256(canonical([p["sampling"]["salt"], task["target_id"], task["seed"],
                                            x["sequence_sha256"]]).encode()).hexdigest()
        uniform = sorted(candidates, key=uniform_key)
        native = []
        for candidate in candidates:
            scores = [x["native_score"] for x in candidate["occurrences"] if x["eligible"] and
                x["run_receipt"] == run and x["native_score"] is not None and
                x["native_score_name"] == method["native_score_name"]]
            if scores:
                best = max(scores) if method["native_score_direction"] == "higher" else min(scores)
                native.append((candidate, best))
        native.sort(key=lambda pair: ((-1 if method["native_score_direction"] == "higher" else 1) *
                                     pair[1], pair[0]["sequence_sha256"]))
        limits = p["sampling"]
        coverage[tid] = {"n_unique_complete": len(candidates), "n_native_score_available": len(native),
                         "n_native_score_missing": len(candidates) - len(native)}
        for name, rows, limit in [
            ("uniform_all_complete", [(x, None) for x in uniform], limits["uniform_n_per_replicate"]),
            ("native_fixed_top_k", native, limits["native_top_k_per_replicate"])]:
            coverage[tid][name] = {"requested": limit, "selected": min(len(rows), limit),
                                  "underfilled": len(rows) < limit}
            for candidate, score in rows[:limit]:
                key = {"task_id": tid, "cohort": name, "sequence_sha256": candidate["sequence_sha256"],
                       "primary_run_receipt": run}
                expected.append({"cohort_record_id": hash_object(key), "task_id": tid, "cohort": name,
                                 "sequence_sha256": candidate["sequence_sha256"],
                                 "sequence": candidate["sequence"], "sampling_key": uniform_key(candidate),
                                 "native_score": score, "primary_run_receipt": run})
    return expected, coverage



def audit_raw_streams(attempt, seqs, updates):
    """Every newline-complete original record is ledgered or a typed raw error."""
    for key,name,events in [("raw_sequence_stream","sequence",seqs),
                             ("raw_native_screening_stream","native_screening",updates)]:
        receipt=attempt.get(key)
        if receipt is None:
            if events: raise ValueError("Original stream receipt missing")
            continue
        data=verify(receipt).read_bytes()
        lines=data.splitlines(keepends=True)
        complete=[(i,line) for i,line in enumerate(lines,1) if line.endswith(b"\n")]
        tails=[line for line in lines if not line.endswith(b"\n")]
        expected_tail=None if not tails else {"bytes":len(tails[-1]),"sha256":hashlib.sha256(tails[-1]).hexdigest()}
        declared=(attempt.get("partial_sequence_tail") or {}).get(name)
        if declared!=expected_tail: raise ValueError("Original partial stream tail differs from receipt")
        byline={event["source_line_number"]:event for event in events}
        errors={error["line_number"]:error for error in attempt.get("stream_errors",[]) if error.get("stream")==name}
        if len(byline)!=len(events): raise ValueError("Duplicate source stream line")
        for number,line in complete:
            if number in errors:
                if hashlib.sha256(line).hexdigest()!=errors[number]["raw_sha256"]:
                    raise ValueError("Raw stream error hash mismatch")
                continue
            if number not in byline: raise ValueError("Complete original stream record omitted from ledger")
            original=json.loads(line); event=byline[number]
            if name=="sequence":
                rawseq="".join(original["sequence"].split()).upper()
                if event["sequence"]!=rawseq: raise ValueError("Original sequence differs from ledger")
                rawid=original.get("sequence_record_id",original["lineage_id"])
                if event["sequence_record_id"]!=rawid: raise ValueError("Original sequence identity differs")
                fields=["lineage_id","internal_acceptance","native_score","native_score_name","completed_at_epoch"]
            else:
                fields=["sequence_record_id","internal_acceptance","native_score","native_score_name","completed_at_epoch"]
            if any(event.get(field)!=original.get(field) for field in fields):
                raise ValueError("Original stream field differs from immutable ledger")
        if any(number not in dict(complete) for number in byline):
            raise ValueError("Ledger event has no original newline-complete source")


def plan_chain(plan, plan_path):
    """Engineering repairs preserve immutable previous plans and comparison fields."""
    result={rec(plan_path)["sha256"]:plan}
    current=plan
    while current["protocol"].get("technical_amendment"):
        amendment=current["protocol"]["technical_amendment"]
        if not isinstance(amendment,dict) or not amendment.get("reason"):
            raise ValueError("Missing explicit amendment reason")
        receipt=amendment["previous_plan_receipt"]
        previous=load(verify(receipt))
        if receipt["sha256"] in result: raise ValueError("Cyclic amendment plans")
        if previous.get("status")!="FROZEN_BEFORE_GENERATION" or canonical(load(verify(previous["protocol_receipt"])))!=canonical(previous["protocol"]):
            raise ValueError("Prior immutable plan changed")
        verify(previous["orchestrator"])
        for target in previous["protocol"]["targets"]:verify(target["input_manifest"])
        for method in previous["protocol"]["methods"]:
            verify(method["config_receipt"])
            for adapter in method["adapter_receipts"]:verify(adapter)
        if canonical(previous["tasks"])!=canonical(current["tasks"]):
            raise ValueError("Amendment changes paired task matrix")
        for key in ["protocol_id","scientific_scope","execution_mode","targets","replicate_seeds","gpu_count","budget_gpu_seconds","shutdown_reserve_seconds","hardware","sampling","inference"]:
            if canonical(previous["protocol"].get(key))!=canonical(current["protocol"].get(key)):
                raise ValueError("Amendment changes scientific comparison field")
        for old,new in zip(previous["protocol"]["methods"],current["protocol"]["methods"]):
            if any(old.get(key)!=new.get(key) for key in ["method_id","native_score_name","native_score_direction"]):
                raise ValueError("Amendment changes native ranking identity")
        result[receipt["sha256"]]=previous;current=previous
    return result


def audit_gpu_ownership(run, protocol):
    """Independent RUNNING/TRES/proc-minor/NVML-UUID/child-visibility reconstruction."""
    initial=load(verify(run["initial_receipt"]))
    for key in ["hardware","scheduler_start","scheduler_alloc_tres","child_cuda_visible_devices","gpu_ownership_status"]:
        if initial[key]!=run[key]:raise ValueError("Initial GPU assignment differs from final receipt")
    scheduler=selected_scheduler_record(run,verify(run["scheduler_start"]).read_text())
    state=re.search(r"\bJobState=(\S+)",scheduler)
    tres=re.search(r"\b(?:AllocTRES|TRES)=(\S+)",scheduler)
    if not state or state[1]!="RUNNING" or not tres or tres[1]!=run["scheduler_alloc_tres"]:
        raise ValueError("Initial allocation was not verified RUNNING")
    count=re.search(r"(?:^|,)gres/gpu=(\d+)(?:,|$)",tres[1])
    typed=[int(x) for x in re.findall(r"(?:^|,)gres/gpu:[^,=]+=(\d+)",tres[1])]
    ngpu=int(count[1]) if count else sum(typed)
    if ngpu!=protocol["gpu_count"] or (count and typed and sum(typed)!=ngpu):
        raise ValueError("Initial allocated GPU count differs from frozen protocol")
    hardware=run["hardware"]
    parsed=[]
    for line in hardware["stdout"].strip().splitlines():
        cells=[x.strip() for x in line.split(",")]
        if len(cells)!=4:raise ValueError("Invalid raw NVML hardware record")
        parsed.append({"index":int(cells[0]),"name":cells[1],"memory_total_mib":int(cells[2]),"uuid":cells[3]})
    if parsed!=hardware["nvml_inventory"] or len({x["uuid"] for x in parsed})!=len(parsed):
        raise ValueError("Raw NVML physical inventory mismatch")
    physical={}
    for row in hardware["physical_inventory"]:
        raw=row["information"]
        minor=re.search(r"^Device Minor:\s*(\d+)\s*$",raw,re.MULTILINE)
        uuid=re.search(r"^GPU UUID:\s*(GPU-\S+)\s*$",raw,re.MULTILINE)
        model=re.search(r"^Model:\s*(.+?)\s*$",raw,re.MULTILINE)
        if not minor or not uuid or not model or (int(minor[1]),uuid[1],model[1])!=(row["device_minor"],row["uuid"],row["name"]):
            raise ValueError("Proc-driver physical identity differs from parsed record")
        if row["device_minor"] in physical or any(x["uuid"]==row["uuid"] for x in physical.values()):
            raise ValueError("Duplicate proc-driver physical GPU identity")
        physical[row["device_minor"]]=row
    if not physical:raise ValueError("Missing physical Device Minor to UUID map")
    byuuid={x["uuid"]:x for x in physical.values()}
    assignment=hardware["assignment_environment"];selections={}
    for key in ["SLURM_JOB_GPUS","SLURM_STEP_GPUS"]:
        if not assignment.get(key):continue
        identifiers=[]
        for token in assignment[key].split(","):
            token=token.strip()
            if re.fullmatch(r"\d+-\d+",token):
                low,high=map(int,token.split("-"))
                if high<low:raise ValueError("Invalid owned GPU range")
                identifiers.extend(str(i)for i in range(low,high+1))
            else:identifiers.append(token)
        if len(identifiers)!=ngpu or len(set(identifiers))!=ngpu:
            raise ValueError("Slurm owned GPU count mismatch")
        try:owned=[physical[int(token)] if token.isdigit() else byuuid[token] for token in identifiers]
        except KeyError:raise ValueError("Owned device is absent from proc-driver map")from None
        uuids={x["uuid"]for x in owned}
        if len(uuids)!=ngpu:raise ValueError("Slurm aliases resolve to duplicate physical devices")
        selections[key]=uuids
    if not selections or (len(selections)==2 and selections["SLURM_JOB_GPUS"]!=selections["SLURM_STEP_GPUS"]):
        raise ValueError("GPU assignment lacks consistent Slurm ownership")
    basis="SLURM_STEP_GPUS" if "SLURM_STEP_GPUS" in selections else "SLURM_JOB_GPUS"
    uuids=selections[basis]
    selected=[dict(x,device_minor=byuuid[x["uuid"]]["device_minor"])for x in parsed if x["uuid"]in uuids]
    if len(selected)!=ngpu or selected!=hardware["gpus"] or hardware["selection_basis"]!=basis:
        raise ValueError("Assigned physical UUID differs from selected NVML hardware")
    if any(x["name"]!=byuuid[x["uuid"]]["name"] or x["name"]!=protocol["hardware"]["gpu_name"]for x in selected):
        raise ValueError("Assigned GPU model is not the frozen physical model")
    owned_list=[x["uuid"]for x in selected]
    original=assignment.get("CUDA_VISIBLE_DEVICES")
    tokens=[] if original is None or not original.strip() else [x.strip()for x in original.split(",")]
    if not tokens:interpretation="UNSET_DERIVED_FROM_SLURM_OWNERSHIP"
    elif len(tokens)!=ngpu or len(set(tokens))!=ngpu:raise ValueError("Multiple original CUDA devices")
    elif all(x.startswith("GPU-")for x in tokens):
        if set(tokens)!=set(owned_list):raise ValueError("Unowned original CUDA UUID")
        interpretation="MATCHED_OWNED_UUID"
    elif all(re.fullmatch(r"\d+",x)for x in tokens):
        if set(tokens)=={str(x["device_minor"])for x in selected}:interpretation="MATCHED_SLURM_GLOBAL_INDICES"
        elif tokens==[str(i)for i in range(ngpu)]:interpretation="LOCAL_INDICES_REMAPPED_TO_OWNED_UUID"
        else:raise ValueError("Wrong original numeric CUDA device")
    else:raise ValueError("Invalid original CUDA mask")
    derived=",".join(owned_list)
    expected={"original_cuda_visible_devices":original,"interpretation":interpretation,
              "owned_gpu_uuids":owned_list,"derived_child_cuda_visible_devices":derived}
    if hardware["cuda_visibility_remapping"]!=expected or hardware["owned_gpu_uuids"]!=owned_list or (
        hardware["child_cuda_visible_devices"]!=derived or run["child_cuda_visible_devices"]!=derived):
        raise ValueError("Derived child CUDA visibility differs from owned physical UUID")
    if run["gpu_ownership_status"]!="RUNNING_SLURM_GPU_OWNERSHIP_VERIFIED":
        raise ValueError("Initial ownership acceptance marker missing")


def audit_session(run, plan, plan_path, attempts, allowed_plans):
    """Recompute owned persistent lifecycle and immutable request/response identity."""
    p, task = plan["protocol"], run["task"]
    full = run["status"] == "BUDGET_EXHAUSTED_WITH_EXPLICIT_BOUNDARY_CENSORING"
    session = run.get("session")
    run_plan_sha=run["plan"]["sha256"]
    if run_plan_sha not in allowed_plans:
        raise ValueError("Run plan hash is absent from immutable source amendment chain")
    if run_plan_sha != rec(plan_path)["sha256"]:
        if run["status"] not in {"EARLY_ENGINEERING_FAILURE","ENGINEERING_INTERRUPTION","ALLOCATION_EXPIRED_BEFORE_GENERATION"}:
            raise ValueError("Previous amended run was not an engineering failure")
        plan=allowed_plans[run_plan_sha];p=plan["protocol"]
    verify(run["plan"])
    if session is None:
        if full or attempts:
            raise ValueError("Persistent session provenance missing")
        return
    if run.get("execution_mode") != "persistent_session" or p.get("execution_mode") != "persistent_session":
        raise ValueError("Nonpersistent formal execution")
    audit_gpu_ownership(run,p)
    method = next(x for x in p["methods"] if x["method_id"] == task["method_id"])
    target = next(x for x in p["targets"] if x["target_id"] == task["target_id"])
    expected = {"protocol_sha256": plan["protocol_receipt"]["sha256"],
        "plan_sha256": run_plan_sha, "method_config_sha256": method["config_receipt"]["sha256"],
        "method_definition_sha256": hash_object(method), "target_manifest_sha256": target["input_manifest"]["sha256"]}
    for field in ("stdout", "stderr"):
        verify(session[field])
    if full and session["ended_at_epoch"] < run["generation_cutoff_epoch"] - .01:
        raise ValueError("Full-budget persistent session stopped before generation cutoff")
    if attempts:
        ready = load(verify(session["ready"]))
        if ready.get("schema") != "paired-budget-session-v1" or ready.get("status") != "READY":
            raise ValueError("Independent READY schema mismatch")
        if any(ready.get(k) != v for k,v in expected.items() if k != "method_definition_sha256"):
            raise ValueError("Independent READY config/source mismatch")
        if ready.get("pid") is not None and ready["pid"] != session["pid"]:
            raise ValueError("READY session PID mismatch")
    elif full and not run.get("session_initialization_boundary_censored"):
        raise ValueError("Zero-attempt full budget lacks initialization censoring")
    fields = dict(expected, session_dir=str(Path(session["stdout"]["path"]).parent),
        target_manifest=target["input_manifest"]["path"],target_id=task["target_id"],
        method_id=task["method_id"],task_id=task["task_id"],protocol_id=p["protocol_id"],
        generation_deadline_epoch=str(run["generation_cutoff_epoch"]),
        allocation_deadline_epoch=str(run["allocation_deadline_epoch"]),
        method_config=method["config_receipt"]["path"])
    if session["argv"] != [arg.format_map(fields) for arg in method["session_start"]]:
        raise ValueError("Independent session adapter argv mismatch")
    for attempt in attempts:
        index, exe = attempt["attempt_index"], attempt["execution"]
        if exe["transport"] != "persistent_session_rpc" or exe["session_pid"] != session["pid"]:
            raise ValueError("Attempt escaped persistent task lifecycle")
        request = load(verify(exe["request"]))
        identity = dict(expected, task_id=task["task_id"],protocol_id=p["protocol_id"],
            request_id="%06d"%index,attempt_index=index,replicate_seed=task["seed"],
            seed=int(hash_object({"protocol_id":task["protocol_id"],"target_id":task["target_id"],
                 "replicate_seed":task["seed"],"attempt_index":index})[:8],16))
        if any(request.get(k) != v for k,v in identity.items()):
            raise ValueError("Immutable RPC request identity/config mismatch")
        if request.get("schema") != "paired-budget-session-v1" or request.get("action") != "method-attempt":
            raise ValueError("Independent RPC request contract mismatch")
        if any(abs(request[field] - run[source]) > .01 for field,source in [
            ("generation_deadline_epoch","generation_cutoff_epoch"),("deadline_epoch","generation_cutoff_epoch"),
            ("allocation_deadline_epoch","allocation_deadline_epoch")]):
            raise ValueError("RPC cutoff differs from frozen task cutoff")
        if exe["response"] is not None:
            response = load(verify(exe["response"]))
            if response.get("schema") != "paired-budget-session-v1" or response.get("status") != "COMPLETE" or (
                response.get("request_id") != request["request_id"]):
                raise ValueError("Independent RPC response mismatch")
            result = verify(response["attempt_result"])
            if result.resolve() != (Path(request["attempt_dir"])/"attempt_result.json").resolve():
                raise ValueError("RPC response result outside attempt")
            if response["attempt_result"] != attempt["adapter_result"]:
                raise ValueError("Terminal attempt result receipt mismatch")
        elif attempt["status"] not in {"TIMED_OUT_BOUNDARY","ENGINEERING_FAILURE","INTERRUPTED"}:
            raise ValueError("Completed scientific attempt lacks terminal RPC response")
        for field,logfield in [("session_stdout_offsets","stdout"),("session_stderr_offsets","stderr")]:
            low,high=exe[field]
            if type(low) is not int or type(high) is not int or not 0 <= low <= high <= session[logfield]["bytes"]:
                raise ValueError("Attempt task log offsets invalid")
        for field in ("stdout","stderr"):
            verify(exe[field])

def audit(plan_path, receipts_path, sacct_path, producer_account_path, producer_cohort_path):
    plan, receipts = load(plan_path), load(receipts_path)
    p = plan["protocol"]
    if plan["status"] != "FROZEN_BEFORE_GENERATION" or canonical(load(verify(plan["protocol_receipt"]))) != canonical(p):
        raise ValueError("Protocol freeze mismatch")
    if canonical(plan["tasks"]) != canonical(expected_tasks(p)):
        raise ValueError("Independent task matrix differs")
    verify(plan["orchestrator"])
    for target in p["targets"]:
        verify(target["input_manifest"])
    for method in p["methods"]:
        verify(method["config_receipt"])
        for source in method["adapter_receipts"]:
            verify(source)
    sched, excluded = scheduler_rows(Path(sacct_path).read_text())
    producer, cohort = load(producer_account_path), load(producer_cohort_path)
    allowed_plans=plan_chain(plan,plan_path)
    inventory, primary, used = {}, {}, set()
    task_rows = {}
    all_seconds, all_attempts, native_updates, source_events = 0, 0, 0, 0
    for rr in receipts:
        run = load(verify(rr))
        identity = allocation_identity(run)
        tid, jid = run["task"]["task_id"], identity["raw_allocation_id"]
        task = next(x for x in plan["tasks"] if x["task_id"] == tid)
        if run["task"] != task or jid in used:
            raise ValueError("Unfrozen task or double-counted allocation")
        used.add(jid)
        if jid not in sched:
            raise ValueError("Missing original physical allocation row: " + jid)
        sr = sched[jid]
        if sr["job_id_alias"] is not None and sr["job_id_alias"] != identity["logical_allocation_key"]:
            raise ValueError("sacct logical alias contradicts original scheduler")
        if sr["ngpu"] != p["gpu_count"]:
            raise ValueError("Scheduler GPU count mismatch")
        seconds = sr["seconds"] * sr["ngpu"]
        all_seconds += seconds
        attempts = jsonl(verify(run["attempt_ledger"]))
        seqs = jsonl(verify(run["sequence_ledger"]))
        updates = [] if not run.get("native_screening_ledger") else jsonl(verify(run["native_screening_ledger"]))
        audit_session(run, plan, plan_path, attempts, allowed_plans)
        for attempt in attempts:
            index=attempt["attempt_index"]
            audit_raw_streams(attempt,[x for x in seqs if x["attempt_index"]==index],
                             [x for x in updates if x["attempt_index"]==index])
        all_attempts += len(attempts)
        native_updates += len(updates)
        source_events += len(seqs)
        if [x["attempt_index"] for x in attempts] != list(range(len(attempts))) or run["attempt_count"] != len(attempts):
            raise ValueError("Attempt ledger denominator mismatch")
        if any(x["status"] not in TERMINAL for x in attempts):
            raise ValueError("Nonterminal attempt omitted from final accounting")
        events_by_attempt = {i: [] for i in range(len(attempts))}
        keys = {(x["attempt_index"], x["sequence_record_id"]) for x in seqs}
        if len(keys) != len(seqs):
            raise ValueError("Repeated original sequence ID")
        for update in updates:
            if (update["attempt_index"], update["sequence_record_id"]) not in keys or update["task_id"] != tid:
                raise ValueError("Native update does not join sequence lineage")
            if update["internal_acceptance"] is not None and type(update["internal_acceptance"]) is not bool:
                raise ValueError("Invalid native acceptance bool")
            if update["native_score"] is not None and not math.isfinite(update["native_score"]):
                raise ValueError("Invalid native score")
            if update["observed_before_generation_cutoff"] and update["observed_at_epoch"] > run["generation_cutoff_epoch"] + 0.01:
                raise ValueError("Postcutoff native score entered selection")
        for original in seqs:
            event = dict(original)
            if event["task_id"] != tid or event["attempt_index"] not in events_by_attempt:
                raise ValueError("Sequence without original attempt")
            seq = "".join(event["sequence"].split()).upper()
            if not seq or not set(seq) <= AA or hashlib.sha256(seq.encode()).hexdigest() != event["sequence_sha256"]:
                raise ValueError("Complete sequence SHA/identity mismatch")
            if event["observed_before_generation_cutoff"] and event["observed_at_epoch"] > run["generation_cutoff_epoch"] + 0.01:
                raise ValueError("Postcutoff sequence entered primary cohort")
            relevant = sorted([u for u in updates if u["attempt_index"] == event["attempt_index"] and
                               u["sequence_record_id"] == event["sequence_record_id"]], key=lambda x: x["source_line_number"])
            for update in relevant:
                if update["observed_before_generation_cutoff"]:
                    for field in ("internal_acceptance", "native_score", "native_score_name"):
                        if update.get(field) is not None:
                            event[field] = update[field]
            events_by_attempt[event["attempt_index"]].append(event)
            key = (tid, event["sequence_sha256"])
            inventory.setdefault(key, {"task_id": tid, "sequence": seq, "sequence_sha256": event["sequence_sha256"],
                                      "occurrences": []})
            inventory[key]["occurrences"].append({"eligible": event["observed_before_generation_cutoff"],
                "run_receipt": rr, "native_score": event["native_score"], "native_score_name": event["native_score_name"],
                "internal_acceptance": event["internal_acceptance"]})
        for a in attempts:
            ev = events_by_attempt[a["attempt_index"]]
            upd = [x for x in updates if x["attempt_index"] == a["attempt_index"]]
            if a["complete_sequence_records"] != len(ev) or a["precutoff_sequence_records"] != sum(
                x["observed_before_generation_cutoff"] for x in ev):
                raise ValueError("Attempt complete-sequence counts differ")
            if a.get("screening_update_records", 0) != len(upd) or a.get("precutoff_screening_update_records", 0) != sum(
                x["observed_before_generation_cutoff"] for x in upd):
                raise ValueError("Attempt native-update counts differ")
        full = run["status"] == "BUDGET_EXHAUSTED_WITH_EXPLICIT_BOUNDARY_CENSORING"
        if full:
            start = datetime.datetime.fromisoformat(sr["start"])
            if start.tzinfo is None:
                start = start.astimezone()
            anchor = start.timestamp()
            if abs(run["allocation_started_at_epoch"] - anchor) > 1:
                raise ValueError("GPU deadline anchor differs from scheduler StartTime")
            allocation_deadline = anchor + task["budget_gpu_seconds"] / p["gpu_count"]
            if abs(run["generation_cutoff_epoch"] - (allocation_deadline - p["shutdown_reserve_seconds"])) > 0.01:
                raise ValueError("Reserved cleanup deadline differs from frozen protocol")
            if abs(run["allocation_deadline_epoch"] - allocation_deadline) > 0.01:
                raise ValueError("Allocation hard deadline differs from frozen budget")
        hardware = len(run["hardware"]["gpus"]) == p["gpu_count"] and all(
            x["name"] == p["hardware"]["gpu_name"] for x in run["hardware"]["gpus"])
        delta = seconds - task["budget_gpu_seconds"]
        accepted = full and hardware and sr["state"] in {"COMPLETED", "TIMEOUT"} and abs(delta) <= (
            p.get("accounting_tolerance_seconds", 0) * p["gpu_count"])
        if accepted:
            if tid in primary:
                raise ValueError("Post-result duplicate full-budget run selection")
            primary[tid] = rr
        expected = {"raw_allocation_id": jid, "logical_allocation_key": identity["logical_allocation_key"],
                    "allocation_identity": identity,
                    "attempt_count": len(attempts), "allocated_gpu_seconds": seconds,
                    "allocated_gpu_seconds_minus_budget": delta, "comparable_full_budget": accepted,
                    "sequence_record_count": len(seqs),
                    "precutoff_sequence_record_count": sum(x["observed_before_generation_cutoff"] for x in seqs),
                    "native_accepted_attempts": sum(any(x["internal_acceptance"] is True for x in ev)
                                                  for ev in events_by_attempt.values()),
                    "attempt_status_counts": {st: sum(x["status"] == st for x in attempts) for st in sorted(TERMINAL)}}
        task_rows[jid] = expected
    if any(sched[x]["seconds"] * sched[x]["ngpu"] > 0 for x in set(sched) - used):
        raise ValueError("Unaccounted positive GPU allocation")
    if producer["all_attempt_count"] != all_attempts or producer["allocated_gpu_seconds_all_attempts"] != all_seconds:
        raise ValueError("Producer aggregate totals differ from raw data")
    if len(producer["tasks"]) != len(task_rows):
        raise ValueError("Producer task denominator differs")
    for row in producer["tasks"]:
        for key, value in task_rows[row["raw_allocation_id"]].items():
            if row[key] != value:
                raise ValueError("Producer accounting mismatch " + key)
    expected_selected, expected_coverage = selected_ids(plan, inventory, primary)
    if len(cohort["selected"]) != len(expected_selected):
        raise ValueError("Cohort denominator differs")
    actual_ids = {x["cohort_record_id"]: x for x in cohort["selected"]}
    if len(actual_ids) != len(cohort["selected"]):
        raise ValueError("Duplicate cohort record")
    for row in expected_selected:
        actual = actual_ids[row["cohort_record_id"]]
        for key, value in row.items():
            if actual[key] != value:
                raise ValueError("Independent uniform/native selection mismatch " + key)
    if len(cohort["coverage"]) != len(plan["tasks"]):
        raise ValueError("Cohort task matrix incomplete")
    for row in cohort["coverage"]:
        for key, value in expected_coverage[row["task"]["task_id"]].items():
            if row[key] != value:
                raise ValueError("Independent cohort coverage mismatch " + key)
    return {"status": "INDEPENDENT_BUDGET_LEDGER_AND_COHORT_AUDIT_PASS",
            "scope": "No production orchestrator imports; persistent RPC/source identity, raw ledger, scheduler GPU seconds and SHA/native selection recomputed",
            "independent_auditor": rec(Path(__file__)),
            "plan": rec(plan_path), "run_receipts_input": rec(receipts_path), "raw_sacct": rec(sacct_path),
            "producer_accounting": rec(producer_account_path), "producer_cohort": rec(producer_cohort_path),
            "allocation_count": len(used), "full_budget_comparable_tasks": len(primary),
            "expected_tasks": len(plan["tasks"]), "all_attempt_count": all_attempts,
            "source_sequence_records": source_events, "native_update_records": native_updates,
            "unique_task_sequence_identities": len(inventory), "all_allocated_gpu_seconds": all_seconds,
            "uniform_and_native_selected_records": len(expected_selected), "excluded_scheduler_step_rows": excluded,
            "complete_generation_matrix": len(primary) == len(plan["tasks"]),
            "scientific_scope": "COMPUTATIONAL_ONLY"}

def main():
    parser = argparse.ArgumentParser()
    for name in ["plan", "run-receipts", "sacct", "producer-accounting", "producer-cohort", "output"]:
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    if not os.environ.get("SLURM_JOB_ID"):
        raise RuntimeError("Slurm CPU required for audit")
    result = audit(args.plan, args.run_receipts, args.sacct, args.producer_accounting, args.producer_cohort)
    result["slurm_job_id"] = os.environ["SLURM_JOB_ID"]
    output = Path(args.output)
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"])

if __name__ == "__main__":
    main()


