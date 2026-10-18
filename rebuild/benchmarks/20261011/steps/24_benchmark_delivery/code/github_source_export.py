#!/usr/bin/env python3
"""Read-only, Slurm-CPU exporter for a committed Git tree to GitHub Git-data payloads."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

SCHEMA = "github_exact_tree_export.v1"
FORBIDDEN_SUFFIXES = {
    ".pem", ".p12", ".pfx", ".key", ".whl", ".so", ".dylib", ".dll", ".exe",
    ".pt", ".pth", ".ckpt", ".safetensors", ".onnx", ".h5", ".hdf5", ".npz",
    ".npy", ".pkl", ".pickle", ".joblib", ".tar", ".tgz", ".zip", ".7z", ".rar",
}
FORBIDDEN_BASENAMES = {".netrc", ".git-credentials", "credentials", "id_rsa", "id_ed25519", "id_dsa", "id_ecdsa"}
TOKEN_RE = re.compile(rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{20,})")
KEY_RE = re.compile(rb"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")
ENV_SECRET_RE = re.compile(rb"(?m)^\s*(?:export\s+)?[A-Z0-9_]*(?:TOKEN|PASSWORD|SECRET|API_KEY|ACCESS_KEY)\s*=\s*(?:\"([^\"\r\n]{8,})\"|'([^'\r\n]{8,})'|([A-Za-z0-9+/=._-]{8,}))\s*(?:#.*)?$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

class ExportError(RuntimeError):
    pass

def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def git(repo, *args, input=None):
    return subprocess.run(["git", "-C", str(repo), *args], input=input, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

def git_object(kind, data):
    return hashlib.sha1(kind.encode("ascii") + b" " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def require_cpu_slurm():
    jobid = os.environ.get("SLURM_JOB_ID", "")
    if not re.fullmatch(r"\d+", jobid):
        raise ExportError("A Slurm CPU allocation is required.")
    if os.environ.get("CUDA_VISIBLE_DEVICES", ""):
        raise ExportError("CUDA_VISIBLE_DEVICES must be empty.")
    raw = subprocess.run(["scontrol", "show", "job", "-o", jobid], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode()
    fields = dict(item.split("=", 1) for item in raw.split() if "=" in item)
    if fields.get("JobState") != "RUNNING":
        raise ExportError("The source-processing allocation must be RUNNING.")
    tres = fields.get("AllocTRES") or fields.get("TRES", "")
    if not tres or not any(re.fullmatch(r"cpu=[1-9]\d*", value) for value in tres.split(",")):
        raise ExportError("Allocated CPU TRES must be explicitly available.")
    for name in ("AllocTRES", "TRES", "TresPerNode", "TresPerTask", "TresPerJob"):
        for value in fields.get(name, "").split(","):
            if "gpu" in value.lower() and not value.endswith("=0"):
                raise ExportError("GPU TRES are forbidden for source processing.")
    if os.environ.get("SLURM_JOB_GPUS", "") or os.environ.get("SLURM_STEP_GPUS", ""):
        raise ExportError("Allocated GPU identifiers are forbidden for source processing.")
    return {"job_id": jobid, "state": fields.get("JobState"), "alloc_tres": tres, "allocated_tres_field": "AllocTRES" if fields.get("AllocTRES") else "TRES", "partition": fields.get("Partition"), "node_list": fields.get("NodeList"), "cuda_visible_devices": ""}

def resolve_commit(repo, ref):
    result = git(repo, "rev-parse", "--verify", ref + "^{commit}").decode().strip()
    if not SHA_RE.fullmatch(result):
        raise ExportError("Only SHA-1 Git repositories are supported by this GitHub payload.")
    return result

def clean_guard(repo, expected_head):
    if git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all"):
        raise ExportError("Source checkout is not clean, including untracked files.")
    if resolve_commit(repo, "HEAD") != expected_head:
        raise ExportError("HEAD differs from the explicitly approved commit.")

def entries(repo, ref):
    result = {}
    for record in git(repo, "ls-tree", "-r", "-z", "--full-tree", ref).split(b"\0"):
        if not record:
            continue
        meta, rawpath = record.split(b"\t", 1)
        mode, kind, sha = meta.decode("ascii").split()
        try:
            path = rawpath.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ExportError("GitHub JSON paths require valid UTF-8.") from exc
        if not path or path.startswith("/") or any(p in ("", ".", "..", ".git") for p in path.split("/")):
            raise ExportError("Unsafe Git path in committed tree.")
        if mode not in ("100644", "100755", "120000", "160000"):
            raise ExportError("Unsupported Git leaf mode.")
        if (mode == "160000") != (kind == "commit"):
            raise ExportError("Git leaf mode/type inconsistency.")
        result[path] = {"path": path, "mode": mode, "type": kind, "sha": sha}
    return result

def forbidden(path, data, mode):
    pure = Path(path)
    lowered_parts = [part.lower() for part in pure.parts]
    name = pure.name.lower()
    if any(part in (".git", ".ssh", ".aws", ".azure", ".kube") for part in lowered_parts):
        return "private_configuration_directory"
    if name in FORBIDDEN_BASENAMES or name == ".env" or (name.startswith(".env.") and name not in (".env.example", ".env.sample", ".env.template")):
        return "credential_filename"
    if pure.suffix.lower() in FORBIDDEN_SUFFIXES:
        return "runtime_model_binary_or_archive"
    if KEY_RE.search(data):
        return "private_key_content"
    if TOKEN_RE.search(data):
        return "high_confidence_access_token"
    for found in ENV_SECRET_RE.finditer(data):
        value = next(group for group in found.groups() if group is not None).strip()
        lower = value.lower()
        if value[:1] not in (b"$", b"<", b"{") and not any(marker in lower for marker in (b"example", b"placeholder", b"changeme", b"your_", b"redacted")):
            return "literal_environment_credential"
    if mode == "120000":
        try:
            target = data.decode("utf-8")
        except UnicodeDecodeError:
            return "non_utf8_symlink"
        if target.startswith("/") or "\0" in target:
            return "unsafe_symlink_target"
        joined = (Path(path).parent / target).as_posix()
        depth = 0
        for part in joined.split("/"):
            if part == "..":
                depth -= 1
            elif part not in ("", "."):
                depth += 1
            if depth < 0:
                return "symlink_escapes_repository"
    return None

def build_trees(leaves):
    """Reconstruct every Git tree from leaf modes and IDs, independently of rev-parse."""
    directories = {"": {}}
    for path, item in leaves.items():
        parts = path.split("/")
        for index in range(len(parts) - 1):
            parent = "/".join(parts[:index])
            child = "/".join(parts[:index + 1])
            existing = directories[parent].get(parts[index])
            if existing and existing["type"] != "tree":
                raise ExportError("File/directory path collision.")
            directories[parent][parts[index]] = {"path": parts[index], "mode": "040000", "type": "tree", "directory": child}
            directories.setdefault(child, {})
        parent = "/".join(parts[:-1])
        if parts[-1] in directories[parent]:
            raise ExportError("Duplicate tree entry.")
        directories[parent][parts[-1]] = {"path": parts[-1], "mode": item["mode"], "type": item["type"], "sha": item["sha"]}
    built = {}
    order = sorted(directories, key=lambda path: (-len(path.split("/")) if path else 0, path))
    for directory in order:
        items = []
        for value in directories[directory].values():
            item = dict(value)
            if item["type"] == "tree":
                item["sha"] = built[item.pop("directory")]["sha"]
            items.append(item)
        items.sort(key=lambda item: item["path"].encode("utf-8") + (b"/" if item["type"] == "tree" else b""))
        raw = b"".join((item["mode"].lstrip("0") + " ").encode("ascii") + item["path"].encode("utf-8") + b"\0" + bytes.fromhex(item["sha"]) for item in items)
        built[directory] = {"sha": git_object("tree", raw), "entries": items, "bytes": len(raw)}
    return built

def write_payload(folder, relative, payload):
    data = canonical(payload)
    file = folder / relative
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_bytes(data)
    return {"path": relative, "bytes": len(data), "sha256": digest(data)}

def export(repo, baseline, expected_head, output, repository, max_blob_bytes=2 * 1024 * 1024, allocation=None):
    repo = Path(repo).resolve()
    output = Path(output).absolute()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ExportError("Invalid repository full name.")
    baseline = resolve_commit(repo, baseline)
    expected_head = resolve_commit(repo, expected_head)
    clean_guard(repo, expected_head)
    if output.exists():
        raise ExportError("Output must be a new immutable export directory.")
    subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", baseline, expected_head], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    base = entries(repo, baseline)
    final = entries(repo, expected_head)
    base_trees, final_trees = build_trees(base), build_trees(final)
    expected_tree = git(repo, "rev-parse", expected_head + "^{tree}").decode().strip()
    baseline_tree = git(repo, "rev-parse", baseline + "^{tree}").decode().strip()
    if final_trees[""]["sha"] != expected_tree or base_trees[""]["sha"] != baseline_tree:
        raise ExportError("Independent Git tree reconstruction differs from Git.")
    inventory, contents, violations = [], {}, []
    base_blob_ids = {item["sha"] for item in base.values() if item["type"] == "blob"}
    base_tree_ids = {item["sha"] for item in base_trees.values()}
    for path, item in sorted(final.items()):
        receipt = dict(item)
        if item["type"] == "blob":
            data = git(repo, "cat-file", "blob", item["sha"])
            if git_object("blob", data) != item["sha"]:
                raise ExportError("Committed blob object ID mismatch.")
            reason = forbidden(path, data, item["mode"])
            if reason:
                violations.append({"path": path, "reason": reason})
            if len(data) > max_blob_bytes:
                violations.append({"path": path, "reason": "blob_exceeds_configured_handoff_size"})
            receipt.update({"bytes": len(data), "sha256": digest(data)})
            contents[item["sha"]] = data
        elif base.get(path) != item:
            violations.append({"path": path, "reason": "new_or_modified_gitlink_requires_separate_public_object_review"})
        inventory.append(receipt)
    if violations:
        # Reasons and paths only: never put matching credentials into logs.
        raise ExportError("Publication exclusions failed: " + json.dumps(violations, ensure_ascii=False))
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=output.name + ".pending-", dir=output.parent))
    try:
        payload_receipts, blob_calls, tree_calls = [], [], []
        for sha in sorted(set(contents) - base_blob_ids):
            relative = "blobs/" + sha + ".json"
            payload = {"repository_full_name": repository, "encoding": "base64", "content": base64.b64encode(contents[sha]).decode("ascii")}
            receipt = write_payload(temporary, relative, payload)
            receipt["expected_git_sha"] = sha
            payload_receipts.append(receipt)
            blob_calls.append({"tool": "mcp__codex_apps__github_create_blob", "payload": relative, "expected_sha": sha})
        seen = set(base_tree_ids)
        for directory, tree in final_trees.items():
            sha = tree["sha"]
            if sha in seen:
                continue
            relative = "trees/" + sha + ".json"
            payload = {"repository_full_name": repository, "base_tree_sha": None, "tree_elements": tree["entries"]}
            receipt = write_payload(temporary, relative, payload)
            receipt["expected_git_sha"] = sha
            payload_receipts.append(receipt)
            tree_calls.append({"tool": "mcp__codex_apps__github_create_tree", "payload": relative, "expected_sha": sha, "directory": directory})
            seen.add(sha)
        delta = []
        for path in sorted(set(base) | set(final)):
            old, new = base.get(path), final.get(path)
            if old == new:
                continue
            if new is None:
                delta.append(dict(old, sha=None))
            else:
                delta.append(dict(new))
        delta_receipt = write_payload(temporary, "delta_tree_payload.json", {"repository_full_name": repository, "base_tree_sha": baseline_tree, "tree_elements": delta})
        inventory_receipt = write_payload(temporary, "source_inventory.json", {"schema": "github_source_inventory.v1", "entries": inventory})
        plan_receipt = write_payload(temporary, "api_handoff_plan.json", {
            "schema": "github_exact_tree_handoff.v1", "repository_full_name": repository,
            "strategy": "base64_blobs_then_dependency_ordered_full_trees_then_new_commit",
            "expected_final_tree_sha": expected_tree, "public_parent_commit_sha": baseline,
            "blob_calls": blob_calls, "tree_calls": tree_calls,
            "create_commit_template": {"repository_full_name": repository, "parent_sha": baseline, "tree_sha": expected_tree, "message": None},
            "publication_authorization": "ROOT_AGENT_ONLY_NO_WRITES_BY_EXPORTER",
            "commit_identity": "NEW_PUBLIC_COMMIT_WITH_EXACT_LOCAL_TREE_NOT_IDENTICAL_LOCAL_COMMIT",
            "root_tree_must_match_before_commit": True,
            "branch_update_is_separate": True,
            "delta_tree_is_review_artifact_only": True,
        })
        manifest = {
            "schema": SCHEMA, "status": "READY_FOR_ROOT_REVIEW_NO_PUBLICATION_PERFORMED",
            "repository_full_name": repository, "source_checkout": str(repo),
            "baseline_commit_sha": baseline, "baseline_tree_sha": baseline_tree,
            "local_commit_sha": expected_head, "final_tree_sha": expected_tree,
            "source_clean_before_and_after": True,
            "source_inventory": inventory_receipt, "handoff_plan": plan_receipt,
            "delta_tree_payload": delta_receipt, "object_payloads": payload_receipts,
            "source_file_count": len(final), "changed_path_count": len(delta),
            "new_blob_object_count": len(blob_calls), "new_tree_object_count": len(tree_calls),
            "total_blob_bytes": sum(item.get("bytes", 0) for item in inventory),
            "max_blob_bytes_policy": max_blob_bytes,
            "allocation": allocation,
            "exporter": {"path": str(Path(__file__).resolve()), "sha256": digest(Path(__file__).read_bytes())},
            "python_version": sys.version.split()[0], "git_version": git(repo, "--version").decode().strip(),
            "publication_scan": {"status": "PASS", "scope": "all_final_tracked_blob_bytes_and_paths", "limitations": "High-confidence exclusion gate plus root source review, not a proof that every possible secret is detectable."},
            "history_preservation_required": {"local_commit_sha": expected_head, "public_commit_metadata_will_differ": True, "archive_local_branch_and_verified_source_bundle_before_switch": True},
        }
        clean_guard(repo, expected_head)
        if git(repo, "rev-parse", expected_head + "^{tree}").decode().strip() != expected_tree:
            raise ExportError("Committed source identity changed during export.")
        write_payload(temporary, "export_manifest.json", manifest)
        for file in temporary.rglob("*"):
            if file.is_file():
                file.chmod(0o444)
        temporary.rename(output)
        return manifest
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--max-blob-bytes", type=int, default=2 * 1024 * 1024)
    args = parser.parse_args()
    try:
        allocation = require_cpu_slurm()
        if args.max_blob_bytes <= 0:
            raise ExportError("max-blob-bytes must be positive.")
        manifest = export(args.repo, args.baseline, args.expected_head, args.output_dir, args.repository, args.max_blob_bytes, allocation)
        print(json.dumps({"status": manifest["status"], "output_dir": args.output_dir, "local_commit_sha": manifest["local_commit_sha"], "final_tree_sha": manifest["final_tree_sha"], "source_file_count": manifest["source_file_count"], "changed_path_count": manifest["changed_path_count"], "new_blob_object_count": manifest["new_blob_object_count"], "new_tree_object_count": manifest["new_tree_object_count"]}, sort_keys=True))
    except (ExportError, subprocess.CalledProcessError) as exc:
        print("EXPORT_REFUSED: " + str(exc), file=sys.stderr)
        raise SystemExit(2)

if __name__ == "__main__":
    main()

