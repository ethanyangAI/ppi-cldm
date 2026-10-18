#!/usr/bin/env python3
"""Meaningful byte/mode/graph, refusal and independent-verification contracts."""
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
import github_source_export as exporter
import github_export_verify as verifier

class GitHubExportContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.write("keep.txt", b"unchanged\n")
        self.write("mode.sh", b"#!/bin/sh\nexit 0\n")
        self.write("delete.txt", b"remove me\n")
        self.write("swap", b"file becomes directory\n")
        self.write("reverse/old.txt", b"directory becomes file\n")
        self.write("text.txt", b"old\r\ntext\r\n")
        self.write("a.c", b"Git tree sorting fixture\n")
        self.write("a/old.txt", b"nested\n")
        self.baseline = self.commit("baseline")
        self.write("mode.sh", b"#!/bin/sh\nexit 0\n")
        (self.repo / "mode.sh").chmod(0o755)
        (self.repo / "delete.txt").unlink()
        (self.repo / "swap").unlink()
        self.write("swap/child.txt", b"new nested tree\n")
        shutil.rmtree(self.repo / "reverse")
        self.write("reverse", b"directory replaced by file\n")
        self.write("text.txt", b"new\ntext\n")
        self.write("binary.dat", bytes((0, 255, 128, 10, 13, 0)))
        self.write("duplicates/one.txt", b"deduplicated contents\n")
        self.write("duplicates/two.txt", b"deduplicated contents\n")
        self.write("unicode/\u7814\u7a76\tfile\nname.txt", b"UTF-8 unusual pathname\n")
        (self.repo / "link").symlink_to("keep.txt")
        self.head = self.commit("final")
        self.output = self.root / "export"

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    def write(self, path, data):
        file = self.repo / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD").decode().strip()

    def export(self, **kwargs):
        return exporter.export(self.repo, self.baseline, self.head, self.output, "fixture/repo", **kwargs)

    def forge_payload(self, receipt, value, manifest):
        path = self.output / receipt["path"]
        path.chmod(0o644)
        data = exporter.canonical(value)
        path.write_bytes(data)
        path.chmod(0o444)
        receipt["bytes"] = len(data)
        receipt["sha256"] = hashlib.sha256(data).hexdigest()
        mf = self.output / "export_manifest.json"
        mf.chmod(0o644)
        mf.write_bytes(exporter.canonical(manifest))
        mf.chmod(0o444)

    def test_exact_tree_binary_modes_symlink_deletions_and_path_replacements(self):
        manifest = self.export()
        result = verifier.verify(self.output, self.repo)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["final_tree_sha"], self.git("rev-parse", "HEAD^{tree}").decode().strip())
        inventory = json.loads((self.output / "source_inventory.json").read_text())["entries"]
        by_path = {item["path"]: item for item in inventory}
        self.assertEqual(by_path["mode.sh"]["mode"], "100755")
        self.assertEqual(by_path["link"]["mode"], "120000")
        binary_sha = by_path["binary.dat"]["sha"]
        blob = json.loads((self.output / ("blobs/" + binary_sha + ".json")).read_text())
        self.assertEqual(base64.b64decode(blob["content"]), bytes((0, 255, 128, 10, 13, 0)))
        delta = json.loads((self.output / "delta_tree_payload.json").read_text())["tree_elements"]
        by_delta = {item["path"]: item for item in delta}
        self.assertIsNone(by_delta["delete.txt"]["sha"])
        self.assertIsNone(by_delta["swap"]["sha"])
        self.assertIsNone(by_delta["reverse/old.txt"]["sha"])
        self.assertIn("swap/child.txt", by_delta)
        self.assertIn("reverse", by_delta)
        self.assertTrue(all(path.stat().st_mode & 0o777 == 0o444 for path in self.output.rglob("*") if path.is_file()))
        self.assertEqual(manifest["source_file_count"], len(by_path))

    def test_blob_deduplication_and_baseline_object_reuse(self):
        manifest = self.export()
        plan = json.loads((self.output / "api_handoff_plan.json").read_text())
        shared_sha = exporter.git_object("blob", b"deduplicated contents\n")
        self.assertEqual(sum(call["expected_sha"] == shared_sha for call in plan["blob_calls"]), 1)
        baseline_sha = exporter.git_object("blob", b"unchanged\n")
        self.assertNotIn(baseline_sha, [call["expected_sha"] for call in plan["blob_calls"]])
        self.assertLess(manifest["new_blob_object_count"], manifest["source_file_count"])

    def test_no_change_reuses_entire_public_baseline_tree(self):
        self.head = self.baseline
        self.git("reset", "--hard", self.baseline)
        manifest = self.export()
        self.assertEqual(manifest["new_blob_object_count"], 0)
        self.assertEqual(manifest["new_tree_object_count"], 0)
        self.assertEqual(manifest["changed_path_count"], 0)
        self.assertEqual(verifier.verify(self.output, self.repo)["status"], "PASS")

    def test_untracked_and_staged_source_are_refused(self):
        self.write("untracked.txt", b"not committed\n")
        with self.assertRaisesRegex(exporter.ExportError, "not clean"):
            self.export()
        self.git("add", "untracked.txt")
        with self.assertRaisesRegex(exporter.ExportError, "not clean"):
            self.export()
        self.assertFalse(self.output.exists())

    def test_explicit_head_mismatch_is_refused(self):
        self.head = self.baseline
        with self.assertRaisesRegex(exporter.ExportError, "HEAD differs"):
            self.export()

    def test_nonancestor_baseline_is_refused(self):
        self.git("checkout", "--orphan", "other")
        self.git("rm", "-rf", ".")
        self.write("other.txt", b"different history\n")
        self.head = self.commit("orphan")
        with self.assertRaises(subprocess.CalledProcessError):
            self.export()

    def test_existing_export_is_not_overwritten(self):
        self.export()
        with self.assertRaisesRegex(exporter.ExportError, "new immutable"):
            self.export()

    def test_private_key_and_access_token_refusal_no_values_in_error(self):
        key = b"-----BEGIN " + b"RSA PRIVATE KEY-----\n" + b"private-material\n"
        self.write("unsafe.txt", key)
        self.head = self.commit("unsafe fixture")
        with self.assertRaisesRegex(exporter.ExportError, "private_key_content") as caught:
            self.export()
        self.assertNotIn("private-material", str(caught.exception))
        (self.repo / "unsafe.txt").unlink()
        token = ("gh" + "p_" + "a" * 40).encode()
        self.write("unsafe.txt", token)
        self.head = self.commit("token fixture")
        with self.assertRaisesRegex(exporter.ExportError, "access_token") as caught:
            self.export()
        self.assertNotIn(token.decode(), str(caught.exception))
        self.assertFalse(self.output.exists())

    def test_credential_and_licensed_runtime_paths_refused(self):
        for path in (".env", ".ssh/private.txt", "licensed.whl", "model.ckpt"):
            with self.subTest(path=path):
                self.write(path, b"fixture\n")
                self.head = self.commit("blocked path")
                with self.assertRaises(exporter.ExportError):
                    self.export()
                (self.repo / path).unlink()
                self.head = self.commit("remove blocked path")

    def test_literal_environment_credential_refused_but_placeholder_allowed(self):
        self.write("config.txt", ("TOKEN" + "=private-value-123456\n").encode())
        self.head = self.commit("environment credential")
        with self.assertRaisesRegex(exporter.ExportError, "literal_environment"):
            self.export()
        self.write("config.txt", ("TOKEN" + "=your_placeholder_value\n").encode())
        self.head = self.commit("placeholder")
        self.assertEqual(self.export()["publication_scan"]["status"], "PASS")

    def test_unsafe_symlink_does_not_read_link_target(self):
        for target in ("/etc/passwd", "../outside.txt"):
            with self.subTest(target=target):
                link = self.repo / "unsafe_link"
                if link.is_symlink():
                    link.unlink()
                link.symlink_to(target)
                self.head = self.commit("unsafe symlink")
                with self.assertRaises(exporter.ExportError):
                    self.export()

    def test_new_gitlink_requires_public_object_review(self):
        subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(self.repo), str(self.repo / "submodule")], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["git", "-C", str(self.repo / "submodule"), "checkout", "-q", self.baseline], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.git("update-index", "--add", "--cacheinfo", "160000," + self.baseline + ",submodule")
        self.git("commit", "-q", "-m", "new gitlink")
        self.head = self.git("rev-parse", "HEAD").decode().strip()
        with self.assertRaisesRegex(exporter.ExportError, "gitlink"):
            self.export()

    def test_handoff_size_policy_refuses_before_any_output(self):
        with self.assertRaisesRegex(exporter.ExportError, "handoff_size"):
            self.export(max_blob_bytes=1)
        self.assertFalse(self.output.exists())

    def test_payload_corruption_is_rejected_even_with_forged_sha256_receipt(self):
        manifest = self.export()
        receipt = next(item for item in manifest["object_payloads"] if item["path"].startswith("blobs/"))
        value = json.loads((self.output / receipt["path"]).read_text())
        value["content"] = base64.b64encode(b"wrong bytes").decode()
        self.forge_payload(receipt, value, manifest)
        with self.assertRaisesRegex(verifier.VerificationError, "intended Git object"):
            verifier.verify(self.output, self.repo)

    def test_api_returned_object_sha_must_match_every_expected_id(self):
        self.export()
        plan = json.loads((self.output / "api_handoff_plan.json").read_text())
        responses = {"blobs": {item["expected_sha"]: item["expected_sha"] for item in plan["blob_calls"]}, "trees": {item["expected_sha"]: item["expected_sha"] for item in plan["tree_calls"]}}
        self.assertTrue(verifier.verify(self.output, self.repo, responses)["api_responses_verified"])
        first = next(iter(responses["blobs"]))
        responses["blobs"][first] = "0" * 40
        with self.assertRaisesRegex(verifier.VerificationError, "returned a different"):
            verifier.verify(self.output, self.repo, responses)

    def test_inventory_cannot_omit_unchanged_source(self):
        manifest = self.export()
        receipt = manifest["source_inventory"]
        inventory = json.loads((self.output / receipt["path"]).read_text())
        inventory["entries"] = [item for item in inventory["entries"] if item["path"] != "keep.txt"]
        self.forge_payload(receipt, inventory, manifest)
        with self.assertRaisesRegex(verifier.VerificationError, "entire committed"):
            verifier.verify(self.output, self.repo)

    def test_dependency_order_is_verified_independently(self):
        manifest = self.export()
        receipt = manifest["handoff_plan"]
        plan = json.loads((self.output / receipt["path"]).read_text())
        plan["tree_calls"] = list(reversed(plan["tree_calls"]))
        self.forge_payload(receipt, plan, manifest)
        with self.assertRaisesRegex(verifier.VerificationError, "dependency order"):
            verifier.verify(self.output, self.repo)

    def test_non_utf8_git_path_refused(self):
        rawpath = os.fsencode(str(self.repo)) + b"/invalid_\xff"
        fd = os.open(rawpath, os.O_WRONLY | os.O_CREAT, 0o644)
        os.write(fd, b"path fixture\n")
        os.close(fd)
        self.head = self.commit("non UTF-8")
        with self.assertRaisesRegex(exporter.ExportError, "valid UTF-8"):
            self.export()

    def test_new_public_commit_can_have_same_tree_and_different_identity(self):
        self.export()
        tree = self.git("rev-parse", "HEAD^{tree}").decode().strip()
        public_commit = subprocess.run(["git", "-C", str(self.repo), "commit-tree", tree, "-p", self.baseline], input=b"fixture public delivery\n", check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
        self.assertNotEqual(public_commit, self.head)
        self.assertEqual(verifier.verify(self.output, self.repo, published_ref=public_commit)["published_ref_verified"], public_commit)
        wrong_parent = subprocess.run(["git", "-C", str(self.repo), "commit-tree", tree, "-p", self.head], input=b"fixture wrong parent\n", check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
        with self.assertRaisesRegex(verifier.VerificationError, "unexpected parent"):
            verifier.verify(self.output, self.repo, published_ref=wrong_parent)

    def test_python_token_variables_and_expressions_are_not_credentials(self):
        self.write("code.py", b'tokens = some_value_function()\nMAX_TOKENS = 4096\nTOKEN = os.getenv("TOKEN")\n')
        self.head = self.commit("ordinary Python source")
        self.assertEqual(self.export()["publication_scan"]["status"], "PASS")

    def test_cpu_slurm_controller_tres_fallback_and_unknown_tres_refusal(self):
        response = subprocess.CompletedProcess([], 0, b"JobState=RUNNING TRES=cpu=1,node=1,billing=1 Partition=organ NodeList=gpu1\n")
        with mock.patch.dict(os.environ, {"SLURM_JOB_ID": "999", "CUDA_VISIBLE_DEVICES": "", "SLURM_JOB_GPUS": "", "SLURM_STEP_GPUS": ""}), mock.patch.object(exporter.subprocess, "run", return_value=response):
            receipt = exporter.require_cpu_slurm()
            self.assertEqual(receipt["alloc_tres"], "cpu=1,node=1,billing=1")
            self.assertEqual(receipt["allocated_tres_field"], "TRES")
        response = subprocess.CompletedProcess([], 0, b"JobState=RUNNING Partition=organ NodeList=gpu1\n")
        with mock.patch.dict(os.environ, {"SLURM_JOB_ID": "999", "CUDA_VISIBLE_DEVICES": ""}), mock.patch.object(exporter.subprocess, "run", return_value=response):
            with self.assertRaisesRegex(exporter.ExportError, "CPU TRES"):
                exporter.require_cpu_slurm()

    def test_cpu_slurm_gate_rejects_missing_allocation_and_gpu_tres(self):
        with mock.patch.dict(os.environ, {"SLURM_JOB_ID": "", "CUDA_VISIBLE_DEVICES": ""}):
            with self.assertRaisesRegex(exporter.ExportError, "Slurm CPU"):
                exporter.require_cpu_slurm()
        response = subprocess.CompletedProcess([], 0, b"JobState=RUNNING AllocTRES=cpu=1,gres/gpu=1 Partition=organ NodeList=gpu1\n")
        with mock.patch.dict(os.environ, {"SLURM_JOB_ID": "999", "CUDA_VISIBLE_DEVICES": ""}), mock.patch.object(exporter.subprocess, "run", return_value=response):
            with self.assertRaisesRegex(exporter.ExportError, "GPU TRES"):
                exporter.require_cpu_slurm()

if __name__ == "__main__":
    unittest.main(verbosity=2)

