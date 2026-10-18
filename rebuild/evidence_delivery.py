#!/usr/bin/env python3
"""Freeze, validate, package, and independently restore the PPI evidence delivery.

All commands that read/hash/analyse artifacts run in a Slurm CPU job. This is a
selective evidence closure, not an offline image of environments/model weights.
No mutation of earlier archives, the reconstruction registry, or source commits.
"""
import argparse
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import tempfile
import unittest

REQUIRED_ROLES = {
    "qualification_rfd60", "qualification_rfd60_independent",
    "qualification_bindcraft18", "qualification_bindcraft18_independent",
    "specificity_review", "evidence_axes", "evidence_axes_independent",
    "controls_technical", "controls_scoring", "calibration",
}
FORBIDDEN_PARTS = {".git", "__pycache__"}
BOUNDARIES = {
    "offsite_backup": False, "fully_offline_runtime_image": False,
    "old_original_backbones_restored": False, "old_MD_restored": False,
    "experimental_blockade_demonstrated": False, "workflow_superiority_demonstrated": False,
}
def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for data in iter(lambda: f.read(8 * 1024 * 1024), b""): h.update(data)
    return h.hexdigest()

def record(path):
    p = Path(path)
    return {"path": str(p), "sha256": sha(p), "bytes": p.stat().st_size}

def write_new(path, value):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("x") as f: json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False); f.write("\n")

def read(path):
    return json.loads(Path(path).read_text())

def slurm():
    if not os.environ.get("SLURM_JOB_ID"): raise RuntimeError("Run via a CPU Slurm allocation")
    if os.environ.get("SLURM_JOB_GPUS"): raise RuntimeError("Delivery does not need a GPU")
    return os.environ["SLURM_JOB_ID"]

def git(source, *args):
    return subprocess.check_output(["git", *args], cwd=source, text=True).strip()

def resolve_inside(root, path):
    p = Path(path)
    if not p.is_absolute(): p = root / p
    # Reject symlinks instead of following them outside an evidence package.
    if p.is_symlink(): raise ValueError("Symlink artifact rejected: " + str(p))
    p = p.absolute()
    if ".." in p.parts: raise ValueError("Traversal in artifact path: " + str(p))
    p.relative_to(root)
    return p

def verify_record(rec, root=None):
    p = Path(rec["path"])
    if root is not None: p = resolve_inside(root, p)
    if not p.is_file(): raise FileNotFoundError(p)
    if rec.get("bytes") is not None and p.stat().st_size != rec["bytes"]:
        raise ValueError("Size mismatch: " + str(p))
    if not re.fullmatch(r"[0-9a-f]{64}", rec.get("sha256", "")):
        raise ValueError("Missing/invalid SHA-256: " + str(p))
    if sha(p) != rec["sha256"]: raise ValueError("SHA-256 mismatch: " + str(p))
    return p

def values(obj, pointer):
    """Dot paths with wildcard: accepted_conditions.*.models."""
    cur = [obj]
    for key in pointer.split(".") if pointer else []:
        nxt = []
        for item in cur:
            if key == "*":
                if isinstance(item, dict): nxt.extend(item.values())
                elif isinstance(item, list): nxt.extend(item)
                else: raise ValueError("Wildcard on scalar: " + pointer)
            elif isinstance(item, dict) and key in item: nxt.append(item[key])
            elif isinstance(item, list) and key.isdigit(): nxt.append(item[int(key)])
            else: raise ValueError("Missing assertion field: " + pointer)
        cur = nxt
    return cur

def assert_content(obj, spec):
    vals = values(obj, spec.get("pointer", ""))
    op = spec["op"]
    if op == "equals":
        actual = vals[0] if len(vals) == 1 else vals
    elif op == "length":
        if len(vals) != 1: raise ValueError("length requires one collection")
        actual = len(vals[0])
    elif op == "sum_lengths": actual = sum(len(v) for v in vals)
    elif op == "all_equals":
        if not vals: raise ValueError("No values for all_equals")
        actual = all(v == spec["expected"] for v in vals)
        if not actual: raise ValueError("all_equals failed: " + str(spec))
        return {"assertion": spec, "actual_count": len(vals), "passed": True}
    else: raise ValueError("Unknown assertion operator: " + op)
    if actual != spec["expected"]: raise ValueError("Content assertion failed: " + str((spec, actual)))
    return {"assertion": spec, "actual": actual, "passed": True}

def refs_and_paths(obj):
    """Recognise manifest records plus *_path/*_sha256 pairs; collect local paths."""
    refs, paths = [], []
    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("path"), str) and isinstance(x.get("sha256"), str):
                refs.append({k: x[k] for k in ("path", "sha256", "bytes") if k in x})
            for k, v in x.items():
                if k.endswith("_path") and isinstance(v, str):
                    hk = k[:-5] + "_sha256"
                    if isinstance(x.get(hk), str): refs.append({"path": v, "sha256": x[hk]})
                walk(v)
        elif isinstance(x, list):
            for item in x: walk(item)
        elif isinstance(x, str) and x.startswith("/"):
            # Prose or shell commands containing absolute paths are not artifact records.
            if "\n" not in x and "\x00" not in x: paths.append(x)
    walk(obj)
    return refs, paths

def excluded(root, p, config):
    rel = p.relative_to(root).as_posix()
    for rule in config.get("exclusions", []):
        prefix = rule["prefix"].rstrip("/")
        if rel == prefix or rel.startswith(prefix + "/"): return rule
    return None

def closure(config):
    root = Path(config["root"]).absolute()
    queue = collections.deque(Path(r["path"]) for r in config["seeds"])
    queue.extend(root / p for p in config.get("include_files", []))
    seen, inventory, refs, external, ignored, missing = set(), {}, {}, {}, set(), set()
    missing_sources = collections.defaultdict(set)
    for g in config["gates"]: queue.append(Path(g["file"]["path"]))
    while queue:
        p = resolve_inside(root, queue.popleft())
        rel = p.relative_to(root).as_posix()
        if rel in seen: continue
        seen.add(rel)
        if any(part in FORBIDDEN_PARTS for part in p.parts): raise ValueError("Forbidden artifact: " + rel)
        rule = excluded(root, p, config)
        if rule:
            external.setdefault(rel, {"path": str(p), "classification": rule["classification"],
                             "reason": rule["reason"], "rule": rule["prefix"]})
            continue
        if not p.is_file():
            if p.is_dir(): ignored.add(rel)
            else: missing.add(rel)
            continue
        inventory[rel] = record(p)
        if p.suffix.lower() != ".json": continue
        # Score matrices are evidence data, not manifests, and need no recursive parse.
        if "_scores_" in p.name: continue
        try: doc = read(p)
        except (UnicodeDecodeError, json.JSONDecodeError): raise ValueError("Invalid JSON: " + str(p))
        rlist, plist = refs_and_paths(doc)
        for r in rlist:
            try:
                rp = resolve_inside(root, r["path"])
                if not Path(r["path"]).is_absolute() and not rp.is_file():
                    near = resolve_inside(root, p.parent / r["path"])
                    if near.is_file(): rp = near
                r = dict(r, path=str(rp))
            except ValueError:
                rules = config.get("allowed_external_historical_roots", [])
                matching = [x for x in rules if str(r["path"]).startswith(x["prefix"].rstrip("/")+"/") and x.get("reason")]
                if len(matching) != 1: raise ValueError("Unadjudicated outside-project artifact: " + str(r["path"]))
                external[str(r["path"])] = dict(r, classification="unrecovered_historical_reference",
                                               reason=matching[0]["reason"])
                continue
            rr = rp.relative_to(root).as_posix()
            old = refs.get(rr)
            if old and old["sha256"] != r["sha256"]:
                raise ValueError("Conflicting frozen hashes for " + rr)
            refs[rr] = r
            rule = excluded(root, rp, config)
            if rule:
                external[rr] = dict(r, classification=rule["classification"], reason=rule["reason"], rule=rule["prefix"])
                continue
            if not rp.is_file(): raise FileNotFoundError("Missing hashed artifact " + str(rp) + " referenced by " + str(p))
            queue.append(rp)
        for candidate in plist:
            try: cp = resolve_inside(root, candidate)
            except ValueError: continue
            if cp.is_file(): queue.append(cp)
            elif cp.is_dir(): ignored.add(cp.relative_to(root).as_posix())
            else:
                missing_rel = cp.relative_to(root).as_posix()
                missing.add(missing_rel); missing_sources[missing_rel].add(rel)
    omissions = config.get("allowed_nonfile_references", []) + config.get("allowed_historical_missing_paths", [])
    if any(not x.get("reason") for x in omissions): raise ValueError("Historical omission requires reason")
    allowed = {x["relative_path"] for x in omissions}
    unexpected_missing = sorted(missing - allowed)
    # Existing output roots and directories do not imply recursive bulk inclusion.
    # Any absent path-only reference must be explicitly adjudicated, never silently omitted.
    if unexpected_missing: raise ValueError("Unadjudicated missing path-only references: " + repr({k: sorted(missing_sources[k]) for k in unexpected_missing}))
    for rel, expected in refs.items():
        if rel in inventory:
            if inventory[rel]["sha256"] != expected["sha256"] or (expected.get("bytes") is not None and inventory[rel]["bytes"] != expected["bytes"]):
                raise ValueError("Artifact hash/size mismatch while closing graph: " + rel)
    return {
        "files": [{"relative_path": k, **inventory[k]} for k in sorted(inventory)],
        "external_reproducible_dependencies": [external[k] for k in sorted(external) if external[k]["classification"] == "external_reproducible_dependency"],
        "historical_archive_dependencies": [external[k] for k in sorted(external) if external[k]["classification"] == "historical_archive_dependency"],
        "unrecovered_historical_references": [external[k] for k in sorted(external) if external[k]["classification"] == "unrecovered_historical_reference"],
        "directory_references_not_recursively_copied": sorted(ignored),
        "adjudicated_nonfile_references": [dict(x, referenced_by=sorted(missing_sources[x["relative_path"]])) for x in omissions if x["relative_path"] in missing],
    }

def audit_closure(args):
    job = slurm(); cfg = read(args.config); graph = closure(cfg)
    out = {"status": "DRAFT_CLOSURE_AUDITED_NOT_DELIVERY_ACCEPTANCE", "job_id": job,
           "config": record(args.config), "artifact_closure": graph, "boundaries": BOUNDARIES}
    write_new(args.output, out)
    print(json.dumps({"audit": record(args.output), "files": len(graph["files"]),
                      "bytes": sum(x["bytes"] for x in graph["files"])}))

def freeze(args):
    job = slurm(); cfg = read(args.config); root = Path(cfg["root"]).absolute()
    roles = [g["role"] for g in cfg["gates"]]
    if len(roles) != len(set(roles)): raise ValueError("Duplicate gate roles")
    if not REQUIRED_ROLES.issubset(roles): raise ValueError("Missing terminal gates: " + repr(REQUIRED_ROLES - set(roles)))
    for rule in cfg.get("exclusions", []):
        if rule["classification"] not in {"external_reproducible_dependency", "historical_archive_dependency"}:
            raise ValueError("Unsupported exclusion class")
        if not rule.get("reason") or not rule.get("recipe_files"): raise ValueError("Excluded artifacts need reasons/recipes")
        for p in rule["recipe_files"]:
            if not resolve_inside(root, p).is_file(): raise ValueError("Missing dependency recipe: " + p)
            cfg.setdefault("include_files", []).append(p)
    source = root / "source"
    if git(source, "status", "--porcelain"): raise ValueError("Source working tree must be committed and clean")
    commit = git(source, "rev-parse", args.source_commit + "^{commit}")
    if git(source, "rev-parse", "HEAD") != commit: raise ValueError("Requested commit must equal checked-out HEAD")
    cfg["source_commit"] = commit
    if not cfg.get("report"): raise ValueError("Final comprehensive report required")
    cfg.setdefault("include_files", []).append(cfg["report"])
    for r in cfg["seeds"]: verify_record(r, root)
    checked = []
    for g in cfg["gates"]:
        p = verify_record(g["file"], root); doc = read(p)
        if doc.get("status") not in g["accepted_statuses"]: raise ValueError("Unaccepted gate status: " + g["role"])
        if not g.get("assertions"): raise ValueError("Gate needs explicit content assertions: " + g["role"])
        checked.append({"role": g["role"], "file": g["file"], "status": doc["status"],
                        "assertions": [assert_content(doc, a) for a in g["assertions"]]})
    graph = closure(cfg)
    names = git(source, "ls-files", "-z").split("\0")
    source_files = [{"relative_path": n, **record(source / n)} for n in names if n]
    plan = {"schema_version": 1, "status": "FROZEN_AND_VALIDATED_FOR_PACKAGING", "job_id": job,
            "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "config": cfg, "terminal_gates": checked, "artifact_closure": graph,
            "source_files": source_files, "source_commit": commit,
            "boundaries": BOUNDARIES, "packed_file_count": len(graph["files"]),
            "packed_bytes": sum(r["bytes"] for r in graph["files"]),
            "source_branch": git(source, "branch", "--show-current")}
    write_new(args.plan, plan)
    print(json.dumps({"plan": record(args.plan), "files": plan["packed_file_count"], "bytes": plan["packed_bytes"]}))

def validate_plan(plan):
    if plan["status"] != "FROZEN_AND_VALIDATED_FOR_PACKAGING": raise ValueError("Invalid plan state")
    root = Path(plan["config"]["root"])
    for row in plan["artifact_closure"]["files"]: verify_record(row, root)
    for row in plan["source_files"]: verify_record(row, root)
    if git(root / "source", "rev-parse", "HEAD") != plan["source_commit"]: raise ValueError("Source HEAD drifted")
    if git(root / "source", "status", "--porcelain"): raise ValueError("Source became dirty")
    return root

def package(args):
    job = slurm(); plan = read(args.plan); root = validate_plan(plan)
    out = resolve_inside(root, args.output_dir)
    out.mkdir(parents=True, exist_ok=False)
    limit = int(args.part_mib * 1024 * 1024)
    if limit < 1024 * 1024: raise ValueError("Part size too small")
    bundle = out / "source.bundle"
    subprocess.run(["git", "bundle", "create", str(bundle), "--all"], cwd=root / "source", check=True)
    subprocess.run(["git", "bundle", "verify", str(bundle)], cwd=root / "source", check=True)
    chunks, part, size = [], [], 0
    for row in plan["artifact_closure"]["files"]:
        if part and size + row["bytes"] > limit: chunks.append(part); part, size = [], 0
        part.append(row); size += row["bytes"]
    if part: chunks.append(part)
    parts = []
    for i, rows in enumerate(chunks):
        dest = out / ("evidence.part%03d.tar.gz" % (i + 1))
        with tarfile.open(dest, "x:gz", compresslevel=1) as tf:
            for row in rows:
                verify_record(row, root)
                tf.add(row["path"], arcname=row["relative_path"], recursive=False)
        parts.append({"archive": record(dest), "member_count": len(rows),
                      "members": [r["relative_path"] for r in rows]})
    shutil.copyfile(args.plan, out / "frozen_plan.json")
    receipt = {"schema_version": 1, "status": "PACKAGED_AWAITING_INDEPENDENT_RESTORE", "job_id": job,
               "plan": record(out / "frozen_plan.json"), "source_bundle": record(bundle), "parts": parts,
               "source_commit": plan["source_commit"], "boundaries": BOUNDARIES}
    write_new(out / "packaging_receipt.json", receipt)
    print(json.dumps({"receipt": record(out / "packaging_receipt.json"), "parts": len(parts)}))

def safe_name(name):
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or not name or "\\" in name:
        raise ValueError("Unsafe archive member: " + name)
    return p

def restore(args):
    job = slurm(); packed = read(args.receipt)
    if job == packed["job_id"]: raise ValueError("Restore must run in an independent Slurm job")
    if packed["status"] != "PACKAGED_AWAITING_INDEPENDENT_RESTORE": raise ValueError("Invalid package status")
    plan = read(verify_record(packed["plan"]))
    bundle = verify_record(packed["source_bundle"])
    dest = Path(args.restore_dir).absolute()
    dest.mkdir(parents=True, exist_ok=False)
    data = dest / "data"; data.mkdir()
    expected = {r["relative_path"]: r for r in plan["artifact_closure"]["files"]}
    seen = set()
    for part in packed["parts"]:
        archive = verify_record(part["archive"]); members = []
        with tarfile.open(archive, "r:gz") as tf:
            for item in tf:
                safe_name(item.name)
                if not item.isfile(): raise ValueError("Only regular files allowed: " + item.name)
                if item.name in seen or item.name not in expected: raise ValueError("Unexpected/duplicate archive member: " + item.name)
                if item.size != expected[item.name]["bytes"]: raise ValueError("Archive size mismatch")
                target = data / item.name; target.parent.mkdir(parents=True, exist_ok=True)
                with tf.extractfile(item) as src, target.open("xb") as dst: shutil.copyfileobj(src, dst)
                if sha(target) != expected[item.name]["sha256"]: raise ValueError("Restored hash mismatch: " + item.name)
                seen.add(item.name); members.append(item.name)
        if members != part["members"] or len(members) != part["member_count"]: raise ValueError("Part member inventory mismatch")
    if seen != set(expected): raise ValueError("Incomplete restored artifact closure")
    clone = dest / "source"
    subprocess.run(["git", "clone", "--no-checkout", str(bundle), str(clone)], check=True)
    subprocess.run(["git", "checkout", "--detach", plan["source_commit"]], cwd=clone, check=True)
    if git(clone, "rev-parse", "HEAD") != plan["source_commit"]: raise ValueError("Restored source commit mismatch")
    source_expected = {r["relative_path"]: r for r in plan["source_files"]}
    if set(git(clone, "ls-files", "-z").split("\0")) - {""} != set(source_expected): raise ValueError("Source inventory mismatch")
    for rel, row in source_expected.items():
        if sha(clone / rel) != row["sha256"]: raise ValueError("Restored source mismatch: " + rel)
    tests = {"status": "NOT_RUN"}
    if args.python:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(clone / "src"); env["PYTHONNOUSERSITE"] = "1"; env["OPENBLAS_NUM_THREADS"] = "1"
        with (dest / "restored_pytest.log").open("x") as f:
            proc = subprocess.run([args.python, "-m", "pytest", "-q"], cwd=clone, env=env, stdout=f, stderr=subprocess.STDOUT)
        tests = {"status": "PASSED" if proc.returncode == 0 else "FAILED",
                 "exit_code": proc.returncode, "log": record(dest / "restored_pytest.log")}
        if proc.returncode: raise RuntimeError("Restored source tests failed; inspect " + str(dest))
    if tests["status"] != "PASSED": raise ValueError("Final acceptance requires restored-source tests (--python)")
    result = {"status": "EVIDENCE_DELIVERY_INDEPENDENTLY_RESTORED_AND_VERIFIED", "job_id": job,
              "packaging_receipt": record(args.receipt), "source_commit": plan["source_commit"],
              "restored_files": len(seen), "restored_source_files": len(source_expected),
              "restored_bytes": sum(r["bytes"] for r in expected.values()), "source_tests": tests,
              "restore_path": str(dest), "boundaries": BOUNDARIES}
    write_new(args.acceptance, result)
    print(json.dumps(result, ensure_ascii=False))

class DeliveryTests(unittest.TestCase):
    def test_traversal_and_unsafe_members(self):
        for x in ["../x", "/x", "a/../../x", "a\\b", ""]:
            with self.assertRaises(ValueError): safe_name(x)
        self.assertEqual(str(safe_name("steps/15/result.json")), "steps/15/result.json")
    def test_missing_assertion_does_not_pass(self):
        with self.assertRaises(ValueError): assert_content({"status": "PASS"}, {"pointer": "count", "op": "equals", "expected": 0})
        with self.assertRaises(ValueError): assert_content({"x": []}, {"pointer": "x.*", "op": "all_equals", "expected": True})
    def test_model_counts_are_real_counts(self):
        x = {"rows": [{"models": [1,2]}, {"models": [3]}]}
        self.assertTrue(assert_content(x, {"pointer": "rows.*.models", "op": "sum_lengths", "expected": 3})["passed"])
        with self.assertRaises(ValueError): assert_content(x, {"pointer": "rows.*.models", "op": "sum_lengths", "expected": 4})
    def test_manifest_ref_pair(self):
        rs, _ = refs_and_paths({"manifest_path": "/a.json", "manifest_sha256": "c"*64,
                              "f": {"path": "/b.pdb", "sha256": "d"*64}})
        self.assertEqual({r["path"] for r in rs}, {"/a.json", "/b.pdb"})
    def test_changed_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"x"; p.write_text("original"); r=record(p); p.write_text("modified")
            with self.assertRaises(ValueError): verify_record(r)
    def test_closure_relative_and_excluded_dependency(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"inputs").mkdir(); (root/"assets").mkdir()
            data=root/"inputs/data.bin"; data.write_bytes(b"evidence")
            weight=root/"assets/model.bin"; weight.write_bytes(b"weight")
            rec=record(data); rec["path"]="data.bin"
            seed=root/"inputs/manifest.json"
            seed.write_text(json.dumps({"input":rec,"weight":record(weight)}))
            cfg={"root":str(root),"seeds":[record(seed)],"gates":[],
                 "exclusions":[{"prefix":"assets","classification":"external_reproducible_dependency","reason":"reacquire"}]}
            out=closure(cfg)
            self.assertEqual({x["relative_path"] for x in out["files"]},{"inputs/manifest.json","inputs/data.bin"})
            self.assertEqual(out["external_reproducible_dependencies"][0]["sha256"],sha(weight))
            data.write_bytes(b"changed!")
            with self.assertRaises(ValueError): closure(cfg)
    def test_missing_hashed_artifact_cannot_be_waived(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); seed=root/"manifest.json"
            seed.write_text(json.dumps({"input":{"path":str(root/"lost"),"sha256":"a"*64}}))
            cfg={"root":str(root),"seeds":[record(seed)],"gates":[],
                 "allowed_historical_missing_paths":[{"relative_path":"lost","reason":"historical"}]}
            with self.assertRaises(FileNotFoundError): closure(cfg)
    def test_conflicting_frozen_references(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); data=root/"x"; data.write_text("x")
            rec=record(data); rec2=dict(rec,sha256="a"*64)
            seed=root/"manifest.json"; seed.write_text(json.dumps([rec,rec2]))
            with self.assertRaises(ValueError):
                closure({"root":str(root),"seeds":[record(seed)],"gates":[]})
    def test_outside_project_artifact_needs_explicit_historical_classification(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); seed=root/"manifest.json"
            seed.write_text(json.dumps({"lost":{"path":"/unavailable/old/x.pdb","sha256":"a"*64}}))
            cfg={"root":str(root),"seeds":[record(seed)],"gates":[]}
            with self.assertRaises(ValueError): closure(cfg)
            cfg["allowed_external_historical_roots"]=[{"prefix":"/unavailable/old","reason":"Lost historical backbone; not restored"}]
            out=closure(cfg)
            self.assertEqual(len(out["unrecovered_historical_references"]),1)
            self.assertEqual(len(out["external_reproducible_dependencies"]),0)
    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"x").write_text("x"); (root/"link").symlink_to(root/"x")
            with self.assertRaises(ValueError): resolve_inside(root, root/"link")

def main():
    p = argparse.ArgumentParser(description=__doc__); s=p.add_subparsers(dest="command", required=True)
    a=s.add_parser("freeze"); a.add_argument("--config",required=True); a.add_argument("--source-commit",required=True); a.add_argument("--plan",required=True)
    a=s.add_parser("package"); a.add_argument("--plan",required=True); a.add_argument("--output-dir",required=True); a.add_argument("--part-mib",type=int,default=512)
    a=s.add_parser("restore"); a.add_argument("--receipt",required=True); a.add_argument("--restore-dir",required=True); a.add_argument("--acceptance",required=True); a.add_argument("--python",required=True)
    a=s.add_parser("audit_closure"); a.add_argument("--config",required=True); a.add_argument("--output",required=True)
    s.add_parser("selftest")
    a=p.parse_args()
    if a.command=="selftest":
        slurm()
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DeliveryTests))
        if not result.wasSuccessful(): raise SystemExit(1)
    else: globals()[a.command](a)
if __name__=="__main__": main()

