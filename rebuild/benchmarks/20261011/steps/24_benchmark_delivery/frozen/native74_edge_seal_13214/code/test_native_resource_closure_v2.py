#!/usr/bin/env python3
"""Meaningful exact-closure contracts, including mutation/omission failures."""
import json,os,tempfile,unittest
from pathlib import Path
import native_resource_closure_v2 as n
from provenance_aliases_v2 import checksum,ReceiptResolver
class ClosureContracts(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"));self.root=Path(self.tmp.name)
        self.old=self.root/"steps/old";self.old.mkdir(parents=True);n.dump(self.old/"assembly.json",{"rows":[]})
        self.out=self.root/"new";self.out.mkdir()
    def tearDown(self):self.tmp.cleanup()
    def write(self,p,value):
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value);return checksum(p)
    def build(self,seed):
        b=n.ClosureBuilder(self.root,self.out,self.old);return b.build(seed)
    def test_mutable_doc_exact_retained_revision_and_frozen_json_bytes(self):
        frozen=self.root/"steps/frozen/api.md";old=self.write(frozen,"old-v1")
        logical=self.root/"steps/code/api.md";self.write(logical,"new-v2")
        old["path"]=str(logical)
        j=self.root/"steps/input.json";n.dump(j,{"api":old});before=j.read_bytes();seed=checksum(j)
        closure,index=self.build([seed]);result=n.verify_closure(self.root,self.out,closure,index,[seed])
        self.assertEqual(result["n_readonly_bytecopies"],2);self.assertEqual(j.read_bytes(),before)
        r=ReceiptResolver(self.root,index=index);self.assertEqual(r.verify(old).read_text(),"old-v1")
        self.assertEqual(logical.read_text(),"new-v2")
    def test_same_original_path_two_versions_not_collapsed(self):
        logical=self.root/"steps/code/api.md";a=self.write(self.root/"steps/v1/api.md","version-one");b=self.write(self.root/"steps/v2/api.md","version-two-longer")
        a["path"]=b["path"]=str(logical)
        closure,index=self.build([a,b])
        self.assertEqual(closure["evidence_copy_n"],2)
        self.assertEqual(n.verify_closure(self.root,self.out,closure,index,[a,b])["n_exact_resources"],2)
    def test_missing_current_document_never_passes(self):
        r={"path":str(self.root/"steps/code/api.md"),"bytes":4,"sha256":"0"*64}
        with self.assertRaises(FileNotFoundError):self.build([r])
    def test_prediction_never_restored_by_same_basename(self):
        r=self.write(self.root/"steps/unrelated/model.npz","fake")
        r["path"]=str(self.root/"steps/raw/model.npz")
        with self.assertRaises(FileNotFoundError):self.build([r])
    def test_assembled_raw_copy_is_verified(self):
        original=self.write(self.root/"steps/raw/data.npz","raw")
        copy=self.write(self.old/"assembled/data.npz","raw")
        n.dump(self.old/"assembly.json",{"rows":[{"files":[{"original":original,"copy":copy}]}]})
        Path(original["path"]).unlink()
        closure,index=self.build([original]);self.assertEqual(closure["resources"][0]["resolution_basis"],"ORIGINAL_RAW_TO_ACCEPTED_HASH_IDENTICAL_BYTECOPY")
        self.assertEqual(n.verify_closure(self.root,self.out,closure,index,[original])["n_readonly_bytecopies"],1)
    def test_original_raw_changed_rejects_even_good_assembled_copy(self):
        original=self.write(self.root/"steps/raw/data.npz","raw")
        copy=self.write(self.old/"assembled/data.npz","raw")
        n.dump(self.old/"assembly.json",{"rows":[{"files":[{"original":original,"copy":copy}]}]})
        Path(original["path"]).write_text("bad")
        with self.assertRaisesRegex(ValueError,"Original raw differs"):self.build([original])
    def test_mutated_readonly_archive_rejected(self):
        r=self.write(self.root/"steps/source.py","source")
        closure,index=self.build([r]);p=Path(index["aliases"][0]["archived"]["path"]);p.chmod(0o644);p.write_text("tamper");p.chmod(0o444)
        with self.assertRaises(ValueError):n.verify_closure(self.root,self.out,closure,index,[r])
    def test_writable_archive_rejected(self):
        r=self.write(self.root/"steps/source.py","source")
        closure,index=self.build([r]);Path(index["aliases"][0]["archived"]["path"]).chmod(0o644)
        with self.assertRaisesRegex(ValueError,"readonly"):n.verify_closure(self.root,self.out,closure,index,[r])
    def test_recursive_receipt_omission_rejected(self):
        r=self.write(self.root/"steps/source.py","source");j=self.root/"steps/plan.json";n.dump(j,{"source":r});seed=checksum(j)
        closure,index=self.build([seed]);closure["resources"]=[x for x in closure["resources"] if n.key(x["original"])!=n.key(r)]
        with self.assertRaisesRegex(ValueError,"omitted"):n.verify_closure(self.root,self.out,closure,index,[seed])
    def test_symlink_source_rejected(self):
        p=self.root/"steps/source.py";self.write(p,"source");s=self.root/"steps/linked.py";s.symlink_to(p);r=checksum(s)
        with self.assertRaisesRegex(ValueError,"escapes"):self.build([r])
    def test_engine_weights_are_conditional_not_faked_bytes(self):
        r={"path":str(self.root/"assets/boltz/weights.ckpt"),"bytes":1000000000,"sha256":"a"*64}
        closure,index=self.build([r]);self.assertEqual(closure["evidence_copy_n"],0);self.assertEqual(closure["engine_recompute_dependency_n"],1)
        self.assertFalse(closure["offline_GPU_recompute_guaranteed"])
        self.assertEqual(n.verify_closure(self.root,self.out,closure,index,[r])["n_engine_recompute_dependencies"],1)
    def test_historical_gap_allowed_only_exact_original_context(self):
        r={"path":str(n.R/"source/rebuild/benchmark_runtime.py"),"bytes":33676,"sha256":n.UNRECOVERABLE}
        parent=str(n.R/"steps/21_method_runtime/runs/readiness_12980/outputs/acceptance.json")
        self.assertTrue(n.historical_unavailable(r,parent,("adapter_source",)))
        self.assertFalse(n.historical_unavailable(r,parent,("worker_source",)))
        self.assertFalse(n.historical_unavailable(r,"actual_native_worker.json",("adapter_source",)))
    def test_unreachable_resource_rejected(self):
        r=self.write(self.root/"steps/source.py","source");s=self.write(self.root/"steps/unused.py","unused")
        closure,index=self.build([r,s])
        with self.assertRaisesRegex(ValueError,"Unreachable"):n.verify_closure(self.root,self.out,closure,index,[r])
    def matrix(self):
        assembly={"n_jobs_expected":20,"n_models_expected":74,"n_jobs_copied":19,"rows":[]}
        score={"models_expected":74,"results":[]};a={"n_jobs":20,"n_models_expected":74,"n_models_valid":71,"n_unresolved_or_no_interface":3}
        raw={"n_jobs_expected":20,"n_models_expected":74,"n_raw_confidence_accepted":71,"n_raw_unresolved":3,"rows":[]}
        for i in range(20):
            k="job"+str(i);nslots=3 if i<13 else 5;missing=i==0
            assembly["rows"].append({"job_key":k,"models_expected":nslots,"status":"WORKER_MISSING_OR_FAILED_SCHEDULER_LEDGER_REQUIRED" if missing else "ALL_REGULAR_RAW_FILES_BYTECOPIED"})
            score["results"].append({"job_key":k,"models":[{"status":"MODEL_UNRESOLVED" if missing else "VALID","R0":None if missing else 1.0,"R1":None if missing else 1.0} for _ in range(nslots)]})
            raw["rows"].append({"job_key":k,"status":"WORKER_MISSING_TYPED_UNRESOLVED" if missing else "NATIVE_ACTUAL_GPU_OWNERSHIP_AND_RAW_CONTENT_AUDITED","models":[] if missing else [{"status":"RAW_EXACT_QUERY_CONFIDENCE_UNITS_ACCEPTED"} for _ in range(nslots)]})
        return assembly,score,a,raw
    def test_full74_denominator_preserves_19worker_typed_missing(self):
        self.assertEqual(n.validate_native_matrix(*self.matrix()),{"MODEL_UNRESOLVED":3,"VALID":71})
    def test_missing_worker_cannot_become_no_interface(self):
        assembly,score,a,raw=self.matrix()
        score["results"][0]["models"][0]={"status":"NO_INTERFACE","R0":0.0,"R1":0.0}
        with self.assertRaisesRegex(ValueError,"scored biology"):n.validate_native_matrix(assembly,score,a,raw)
    def test_duplicate_arm_cannot_hide_dropped_denominator(self):
        assembly,score,a,raw=self.matrix();score["results"][-1]=score["results"][0]
        with self.assertRaisesRegex(ValueError,"matrix incomplete"):n.validate_native_matrix(assembly,score,a,raw)

    def test_full74_gate_requires_all_raw_confidence(self):
        import native_full74_collection_v2 as full
        self.assertEqual(full.final_native_status({"n_jobs_copied":20},{"n_raw_confidence_accepted":74,"n_raw_unresolved":0}),"NATIVE74_FULL_RAW_AND_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY")
        self.assertIn("NOT_FULL74_ACCEPTED",full.final_native_status({"n_jobs_copied":19},{"n_raw_confidence_accepted":71,"n_raw_unresolved":3}))
    def test_two_exact_MSA_history_fields_not_generalized(self):
        from unittest.mock import patch
        parent="/authority/old_msa.json";operative={"path":"/authority/current.py","sha256":"876d29f9b8a20cf3f8bbf526262de96b1071a30b47590b632e5d31f97c362391","bytes":59077}
        r={"path":"/authority/old.py","sha256":"e"*64,"bytes":46094}
        entry=dict(logical_path=r["path"],expected_sha256=r["sha256"],expected_bytes=r["bytes"],parent_path=parent,parent_sha256="a"*64,field=["source"],status="HISTORICAL_UNRESOLVED_MSA_DERIVATION",current_execution_allowed=False,actual_operative_scientific_source=operative,role="OLD_MSA_GENERATOR",root_decision="Exact context only")
        fake=lambda p: {"path":str(p),"sha256":"a"*64 if str(p)==parent else operative["sha256"],"bytes":1}
        with patch.object(n,"checksum",fake):
            self.assertEqual(n.historical_gap(r,parent,("source",),{"entries":[entry]})["subtype"],"HISTORICAL_UNRESOLVED_MSA_DERIVATION")
            self.assertIsNone(n.historical_gap(r,parent,("worker_source",),{"entries":[entry]}))
            self.assertIsNone(n.historical_gap(r,"/authority/current_worker.json",("source",),{"entries":[entry]}))
            wrong=dict(r,sha256="f"*64);self.assertIsNone(n.historical_gap(wrong,parent,("source",),{"entries":[entry]}))
    def test_history_policy_rejects_changed_parent_bytes(self):
        from unittest.mock import patch
        r={"path":"/authority/old.py","sha256":"e"*64,"bytes":46094}
        entry=dict(logical_path=r["path"],expected_sha256=r["sha256"],expected_bytes=r["bytes"],parent_path="/authority/msa.json",parent_sha256="a"*64,field=["source"],status="HISTORICAL_UNRESOLVED_MSA_DERIVATION",current_execution_allowed=False)
        with patch.object(n,"checksum",lambda p:{"sha256":"b"*64}):
            with self.assertRaisesRegex(ValueError,"parent bytes changed"):n.historical_gap(r,entry["parent_path"],("source",),{"entries":[entry]})

    def test_allowed_historical_SHA_cannot_cover_current_edge(self):
        from unittest.mock import patch
        r={"path":str(self.root/"steps/old.py"),"sha256":"e"*64,"bytes":4};j=self.root/"steps/plan.json"
        n.dump(j,{"operative_source":r,"history_source":r})
        allowed=lambda r,parent,trail,policy,resolver=None:({"subtype":"HISTORICAL_UNRESOLVED_MSA_DERIVATION","role":"OLD_MSA_GENERATOR"} if trail==("history_source",) else None)
        with patch.object(n,"historical_gap",allowed):
            with self.assertRaisesRegex(ValueError,"current operative receipt"):self.build([checksum(j)])
    def test_independent_verifier_checks_duplicate_historical_edges(self):
        from unittest.mock import patch
        r={"path":str(self.root/"steps/old.py"),"sha256":"e"*64,"bytes":4};j=self.root/"steps/plan.json"
        n.dump(j,{"operative_source":r,"history_source":r});seed=checksum(j)
        alias=n.archive_alias(seed,j,self.out/"evidence_resources","TEST_PLAN")
        h=dict(original=r,status="HISTORICAL_UNRESOLVED_PROVENANCE",current_PASS_allowed=False,parent=str(j),trail=["history_source"])
        closure={"resources":[{"original":seed,"copy":alias["archived"],"scope":"SCIENTIFIC_SOURCE_INPUT_REFERENCE_OR_RAW_EVIDENCE","copied":True},
                              {"original":r,"scope":"ENGINEERING_HISTORY","copied":False,"historical_unresolved":h}],
                 "evidence_copy_n":1,"engine_recompute_dependency_n":0,"historical_unresolved_n":1}
        index={"aliases":[alias],"historical_unresolved":[h]}
        allowed=lambda r,parent,trail,policy,resolver=None:({"subtype":"HISTORICAL_UNRESOLVED_MSA_DERIVATION","role":"OLD_MSA_GENERATOR"} if trail==("history_source",) else None)
        with patch.object(n,"historical_gap",allowed):
            with self.assertRaisesRegex(ValueError,"current evidence role"):n.verify_closure(self.root,self.out,closure,index,[seed])

if __name__=="__main__":
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ClosureContracts))
    out=Path(os.environ["NATIVE_CLOSURE_TEST_OUTPUT"]);out.mkdir(parents=True,exist_ok=True)
    n.dump(out/"tests.json",dict(status="PASSED" if result.wasSuccessful() else "FAILED",tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),
                               sources=[checksum(__file__),checksum(n.__file__),checksum(Path(__file__).with_name("provenance_aliases_v2.py"))]))
    raise SystemExit(0 if result.wasSuccessful() else 1)

