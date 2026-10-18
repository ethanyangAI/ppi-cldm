#!/usr/bin/env python3
"""Contracts for the two limited MSA dispositions in generic delivery validation."""
import copy,json,os,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import native_resource_closure_v2 as n
from provenance_aliases_v2 import ReceiptResolver,checksum
from historical_scope_v2 import HistoricalScopeVerifier
R=n.R;run=R/"steps/24_benchmark_delivery/runs/native74_final_v2_13211/native74/closure"
INDEX=n.read(run/"resource_aliases.json");POLICY=n.read(R/"steps/24_benchmark_delivery/frozen/native74_final_v2_13211/code/native_msa_history_policy.json")
class HistoryContracts(unittest.TestCase):
    def setUp(self):self.resolver=ReceiptResolver(R,index=INDEX);self.scope=HistoricalScopeVerifier(self.resolver,POLICY)
    def test_both_exact_history_metadata_contexts_accepted(self):
        self.assertEqual(len(INDEX["historical_unresolved"]),2)
        for h in INDEX["historical_unresolved"]:self.assertTrue(self.scope.metadata(h))
    def test_actual_parent_fields_accepted_but_current_source_fields_fail(self):
        for h in INDEX["historical_unresolved"]:
            self.assertTrue(self.scope.edge(h["original"],h["parent"],h["trail"]))
            self.assertFalse(self.scope.edge(h["original"],str(R/"steps/current/worker.json"),["source"]))
            self.assertFalse(self.scope.edge(h["original"],h["parent"],["worker_source"]))
    def test_no_policy_cannot_exempt_MSA_source(self):
        scope=HistoricalScopeVerifier(self.resolver)
        for h in INDEX["historical_unresolved"]:
            with self.assertRaises(ValueError):scope.metadata(h)
            self.assertFalse(scope.edge(h["original"],h["parent"],h["trail"]))
    def test_extra_or_changed_policy_entry_rejected(self):
        altered=copy.deepcopy(POLICY);altered["entries"].append(copy.deepcopy(altered["entries"][0]))
        with self.assertRaises(ValueError):HistoricalScopeVerifier(self.resolver,altered)
        altered=copy.deepcopy(POLICY);altered["entries"][0]["expected_sha256"]="a"*64
        with self.assertRaises(ValueError):HistoricalScopeVerifier(self.resolver,altered)
    def test_policy_cannot_enable_current_execution(self):
        altered=copy.deepcopy(POLICY);altered["entries"][0]["current_execution_allowed"]=True
        with self.assertRaises(ValueError):HistoricalScopeVerifier(self.resolver,altered)
    def test_forged_historical_metadata_rejected(self):
        forged=copy.deepcopy(INDEX["historical_unresolved"][0]);forged["original"]["sha256"]="b"*64
        with self.assertRaises(ValueError):self.scope.metadata(forged)
        forged=copy.deepcopy(INDEX["historical_unresolved"][0]);forged["current_PASS_allowed"]=True
        with self.assertRaises(ValueError):self.scope.metadata(forged)
    def test_archived_JSON_parent_recovers_only_explicit_logical_receipts(self):
        for h in INDEX["historical_unresolved"]:
            entry=next(x for x in INDEX["aliases"] if x["original"]["path"]==h["parent"])
            p=self.resolver.verify(entry["original"])
            self.assertIn(h["parent"],self.scope.logical_parents(p,entry["archived"]["sha256"]))
    def test_same_Lustre_independent_restore_policy_reads_only_restored_bytes(self):
        with tempfile.TemporaryDirectory(dir=os.environ["TMPDIR"]) as tmp:
            restore=Path(tmp);aliases=[]
            wanted={e["parent_path"] for e in POLICY["entries"]}|{e["actual_operative_scientific_source"]["path"] for e in POLICY["entries"]}
            for entry in INDEX["aliases"]:
                if entry["original"]["path"] not in wanted:continue
                p=self.resolver.verify(entry["original"]);dest=restore/Path(entry["archived"]["path"]).relative_to(R)
                dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);dest.chmod(0o444);aliases.append(entry)
            resolver=ReceiptResolver(R,restore,index={"aliases":aliases,"historical_unresolved":INDEX["historical_unresolved"]})
            scope=HistoricalScopeVerifier(resolver,POLICY)
            def restored_only(p):
                if not Path(p).is_relative_to(restore):raise AssertionError("Original scientific evidence read during independent restore")
                return checksum(p)
            with patch.object(n,"checksum",restored_only):
                for h in INDEX["historical_unresolved"]:self.assertTrue(scope.metadata(h))
    def test_12980_metadata_is_noncurrent_and_not_operational_source(self):
        r={"path":str(R/"source/rebuild/benchmark_runtime.py"),"sha256":"b47e302116b923e683aee567fe0c1b6721a56d6c410de9cd2cdd9dcfd79fecfd","bytes":33676}
        h={"original":r,"status":"HISTORICAL_UNRESOLVED_PROVENANCE","current_PASS_allowed":False}
        scope=HistoricalScopeVerifier(ReceiptResolver(R,index={"historical_unresolved":[h]}))
        self.assertTrue(scope.metadata(h))
        self.assertFalse(scope.edge(r,str(R/"steps/current/worker.json"),["source"]))
if __name__=="__main__":
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(HistoryContracts))
    out=Path(os.environ["HISTORY_POLICY_TEST_OUTPUT"]);out.mkdir(parents=True,exist_ok=True)
    n.dump(out/"acceptance.json",dict(status="EXACT_HISTORICAL_MSA_POLICY_GENERIC_DELIVERY_CONTRACTS_ACCEPTED" if result.wasSuccessful() else "FAILED",
        tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),sources=[checksum(__file__),checksum(n.__file__),checksum(Path(__file__).with_name("historical_scope_v2.py")),checksum(Path(__file__).with_name("delivery_core_v2.py"))],
        formal28_benchmark_complete=False,ACTIVE_changed=False,source_staged=False,only_two_exact_MSA_derivation_exceptions=True,current_source_missing_allowed=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)

