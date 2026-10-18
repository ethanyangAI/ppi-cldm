#!/usr/bin/env python3
"""Independent read-only verifier of GitHub exact-tree export artifacts."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys

class VerificationError(RuntimeError):
    pass

def run_git(repo, *args, input=None):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def read_receipt(root, receipt):
    relative = PurePosixPath(receipt["path"])
    if relative.is_absolute() or any(part in ("", ".", "..") for part in relative.parts):
        raise VerificationError("Unsafe export receipt path.")
    file = root.joinpath(*relative.parts)
    if not file.is_file() or file.is_symlink():
        raise VerificationError("Missing or symbolic export payload.")
    data = file.read_bytes()
    if len(data) != receipt["bytes"] or hashlib.sha256(data).hexdigest() != receipt["sha256"]:
        raise VerificationError("Export receipt mismatch: " + str(relative))
    if stat.S_IMODE(file.stat().st_mode) != 0o444:
        raise VerificationError("Export payload is not immutable.")
    return json.loads(data.decode("utf-8"))

def object_sha(repo, kind, data):
    # Official git object encoder, not the exporter's hashing implementation.
    return run_git(repo, "hash-object", "-t", kind, "--stdin", input=data).decode().strip()

def source_leaves(repo, ref):
    leaves = {}
    for record in run_git(repo, "ls-tree", "-r", "-z", ref).split(b"\0"):
        if record:
            metadata, path = record.split(b"\t", 1)
            mode, kind, sha = metadata.decode().split()
            leaves[path.decode("utf-8")] = (mode, kind, sha)
    return leaves

def verify(root, repo, responses=None, published_ref=None):
    root, repo = Path(root).resolve(), Path(repo).resolve()
    manifest_file = root / "export_manifest.json"
    if manifest_file.is_symlink() or stat.S_IMODE(manifest_file.stat().st_mode) != 0o444:
        raise VerificationError("Export manifest is not an immutable ordinary file.")
    manifest = load_json(manifest_file)
    if manifest.get("schema") != "github_exact_tree_export.v1":
        raise VerificationError("Unknown export schema.")
    expected_tree = manifest["final_tree_sha"]
    local_commit = manifest["local_commit_sha"]
    baseline_commit = manifest["baseline_commit_sha"]
    if run_git(repo, "rev-parse", local_commit + "^{tree}").decode().strip() != expected_tree:
        raise VerificationError("Source commit tree differs from export.")
    if run_git(repo, "rev-parse", baseline_commit + "^{tree}").decode().strip() != manifest["baseline_tree_sha"]:
        raise VerificationError("Baseline source tree differs from export.")
    final = source_leaves(repo, local_commit)
    base = source_leaves(repo, baseline_commit)
    inventory = read_receipt(root, manifest["source_inventory"])
    if inventory.get("schema") != "github_source_inventory.v1":
        raise VerificationError("Unknown inventory schema.")
    exported = {}
    for item in inventory["entries"]:
        path = item["path"]
        if path in exported:
            raise VerificationError("Duplicate exported path.")
        exported[path] = (item["mode"], item["type"], item["sha"])
        if item["type"] == "blob":
            raw = run_git(repo, "cat-file", "blob", item["sha"])
            if object_sha(repo, "blob", raw) != item["sha"] or len(raw) != item["bytes"] or hashlib.sha256(raw).hexdigest() != item["sha256"]:
                raise VerificationError("Committed source blob receipt mismatch: " + path)
    if exported != final:
        raise VerificationError("Exported inventory is not the entire committed source tree.")
    if manifest["source_file_count"] != len(final):
        raise VerificationError("Source file denominator mismatch.")
    objects = {}
    for receipt in manifest["object_payloads"]:
        payload = read_receipt(root, receipt)
        sha = receipt["expected_git_sha"]
        if sha in objects:
            raise VerificationError("Duplicate exported object.")
        if payload.get("repository_full_name") != manifest["repository_full_name"]:
            raise VerificationError("Payload repository mismatch.")
        objects[sha] = (payload, receipt["path"])
    plan = read_receipt(root, manifest["handoff_plan"])
    if plan["expected_final_tree_sha"] != expected_tree or plan["public_parent_commit_sha"] != baseline_commit:
        raise VerificationError("Handoff graph authority mismatch.")
    known_blobs = {record[2] for record in base.values() if record[1] == "blob"}
    known_trees = {manifest["baseline_tree_sha"]}
    for record in run_git(repo, "ls-tree", "-r", "-t", "-z", baseline_commit).split(b"\0"):
        if record:
            meta = record.split(b"\t", 1)[0].decode().split()
            if meta[1] == "tree":
                known_trees.add(meta[2])
    required_blobs = {record[2] for record in final.values() if record[1] == "blob"} - known_blobs
    observed_blob_calls = set()
    observed_tree_calls = set()
    for call in plan["blob_calls"]:
        sha = call["expected_sha"]
        if sha in observed_blob_calls:
            raise VerificationError("Duplicate blob API call.")
        observed_blob_calls.add(sha)
        payload, relative = objects[sha]
        if relative != call["payload"] or call["tool"] != "mcp__codex_apps__github_create_blob" or payload["encoding"] != "base64":
            raise VerificationError("Unexpected blob call contract.")
        raw = base64.b64decode(payload["content"], validate=True)
        if object_sha(repo, "blob", raw) != sha:
            raise VerificationError("Blob payload bytes differ from intended Git object.")
        known_blobs.add(sha)
    if observed_blob_calls != required_blobs or len(observed_blob_calls) != manifest["new_blob_object_count"]:
        raise VerificationError("Exported blob API call set is incomplete or extra.")
    last_tree = None
    for call in plan["tree_calls"]:
        sha = call["expected_sha"]
        if sha in observed_tree_calls:
            raise VerificationError("Duplicate tree API call.")
        observed_tree_calls.add(sha)
        payload, relative = objects[sha]
        if relative != call["payload"] or call["tool"] != "mcp__codex_apps__github_create_tree" or payload["base_tree_sha"] is not None:
            raise VerificationError("Unexpected complete-tree call contract.")
        elements = payload["tree_elements"]
        names = set()
        raw_parts = []
        for item in sorted(elements, key=lambda value: value["path"].encode("utf-8") + (b"/" if value["type"] == "tree" else b"")):
            name = item["path"]
            if "/" in name or name in ("", ".", "..") or name in names:
                raise VerificationError("Tree payload has unsafe or duplicate immediate entry.")
            names.add(name)
            mode, kind, item_sha = item["mode"], item["type"], item["sha"]
            if (mode, kind) not in (("100644", "blob"), ("100755", "blob"), ("120000", "blob"), ("040000", "tree"), ("160000", "commit")):
                raise VerificationError("Git file mode/type was not preserved.")
            if kind == "blob" and item_sha not in known_blobs:
                raise VerificationError("Tree references an unpublished blob.")
            if kind == "tree" and item_sha not in known_trees:
                raise VerificationError("Tree API calls are not in dependency order.")
            raw_parts.append((mode.lstrip("0") + " ").encode() + name.encode("utf-8") + b"\0" + bytes.fromhex(item_sha))
        if object_sha(repo, "tree", b"".join(raw_parts)) != sha:
            raise VerificationError("Tree payload differs from intended Git object.")
        known_trees.add(sha)
        last_tree = sha
    if len(observed_tree_calls) != manifest["new_tree_object_count"] or set(objects) != observed_blob_calls | observed_tree_calls:
        raise VerificationError("Object call denominator mismatch.")
    if expected_tree not in known_trees or (plan["tree_calls"] and last_tree != expected_tree):
        raise VerificationError("Complete tree plan does not end at the approved final tree.")
    delta = read_receipt(root, manifest["delta_tree_payload"])
    expected_delta = {}
    for path in set(base) | set(final):
        if base.get(path) != final.get(path):
            record = final.get(path) or base[path]
            expected_delta[path] = {"path": path, "mode": record[0], "type": record[1], "sha": record[2] if path in final else None}
    observed_delta = {item["path"]: item for item in delta["tree_elements"]}
    if len(observed_delta) != len(delta["tree_elements"]) or observed_delta != expected_delta or len(expected_delta) != manifest["changed_path_count"]:
        raise VerificationError("Delta modes, IDs, additions or deletions are wrong.")
    if delta["base_tree_sha"] != manifest["baseline_tree_sha"]:
        raise VerificationError("Delta baseline mismatch.")
    if responses is not None:
        for kind, calls in (("blobs", plan["blob_calls"]), ("trees", plan["tree_calls"])):
            mapping = responses.get(kind, {})
            if set(mapping) != {call["expected_sha"] for call in calls}:
                raise VerificationError("API response denominator mismatch.")
            if any(mapping[sha] != sha for sha in mapping):
                raise VerificationError("GitHub returned a different Git object SHA.")
        commit = responses.get("commit")
        if commit and (commit.get("tree_sha") != expected_tree or commit.get("parent_shas") != [baseline_commit]):
            raise VerificationError("Published commit graph differs from the approved tree/parent.")
    if published_ref:
        if run_git(repo, "rev-parse", published_ref + "^{tree}").decode().strip() != expected_tree:
            raise VerificationError("Fetched public commit does not have identical tree.")
        parents = run_git(repo, "show", "-s", "--format=%P", published_ref).decode().strip().split()
        if parents != [baseline_commit]:
            raise VerificationError("Fetched public commit has unexpected parent(s).")
    return {"schema": "github_exact_tree_independent_verification.v1", "status": "PASS", "local_commit_sha": local_commit, "final_tree_sha": expected_tree, "source_file_count": len(final), "changed_path_count": len(expected_delta), "new_blob_object_count": len(observed_blob_calls), "new_tree_object_count": len(observed_tree_calls), "api_responses_verified": responses is not None, "published_ref_verified": published_ref}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-dir", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--api-responses")
    parser.add_argument("--published-ref")
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        result = verify(args.export_dir, args.repo, load_json(args.api_responses) if args.api_responses else None, args.published_ref)
        data = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output:
            file = Path(args.output)
            if file.exists():
                raise VerificationError("Verification output must be new.")
            file.write_text(data)
        print(data.strip())
    except (VerificationError, subprocess.CalledProcessError, ValueError, KeyError) as exc:
        print("VERIFICATION_REFUSED: " + str(exc), file=sys.stderr)
        raise SystemExit(2)

if __name__ == "__main__":
    main()

