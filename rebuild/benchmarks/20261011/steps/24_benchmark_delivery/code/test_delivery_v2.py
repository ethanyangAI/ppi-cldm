#!/usr/bin/env python3
"""Delivery v2 engineering contracts; never accepts production benchmark results."""
import copy,hashlib,json,os,shutil,unittest
from pathlib import Path
from unittest.mock import patch
import test_delivery as v1
import delivery_core_v2 as d
from delivery_graph_v2 import source_entries
from provenance_aliases_v2 import ReceiptResolver,archive_alias,HistoricalUnresolvedProvenance,AmbiguousReceiptPath,aliases_from_closure
from restore_resolver_v2 import path_factory,load_budget_auditor
from target_statistics_v2 import expected_tasks,statistics,POLICY
from common_review_independent import summary
R=v1.R
class Tests(v1.Tests):
    def alias_fixture(self,extra=False):
        authority=self.base/"authority";authority.mkdir()
        logical=authority/"mutable.py";logical.write_text("original version\n");old=d.rec(logical)
        snapshot=authority/"snapshot.py";snapshot.write_bytes(logical.read_bytes())
        archive=archive_alias(old,snapshot,authority/"aliases","HISTORICAL_EXACT_SOURCE_BYTES")
        logical.write_text("current changed version\n")
        index={"aliases":[archive],"historical_unresolved":[]}
        if extra:
            second=d.rec(logical);s2=authority/"snapshot2.py";s2.write_bytes(logical.read_bytes())
            index["aliases"].append(archive_alias(second,s2,authority/"aliases","HISTORICAL_EXACT_SOURCE_BYTES"))
        return authority,old,index
    def test_alias_reads_exact_old_bytes_after_live_changes(self):
        root,old,index=self.alias_fixture()
        resolver=ReceiptResolver(root,index=index)
        self.assertEqual(resolver.verify(old).read_text(),"original version\n")
        self.assertEqual(Path(old["path"]).read_text(),"current changed version\n")
    def test_alias_wrong_sha_has_no_nearest_fallback(self):
        root,old,index=self.alias_fixture();r=dict(old,sha256="f"*64)
        with self.assertRaises(ValueError):ReceiptResolver(root,index=index).verify(r)
    def test_two_versions_same_path_require_exact_sha(self):
        root,old,index=self.alias_fixture(extra=True);resolver=ReceiptResolver(root,index=index)
        with self.assertRaises(AmbiguousReceiptPath):resolver.resolve(old["path"])
        self.assertEqual(resolver.verify(old).read_text(),"original version\n")
    def test_writable_alias_cannot_satisfy_receipt(self):
        root,old,index=self.alias_fixture();Path(index["aliases"][0]["archived"]["path"]).chmod(0o644)
        with self.assertRaisesRegex(ValueError,"readonly"):ReceiptResolver(root,index=index).verify(old)
    def test_unrecoverable_history_never_current_pass(self):
        root=self.base/"authority";root.mkdir();r={"path":str(root/"missing"),"sha256":"a"*64,"bytes":1}
        index={"aliases":[],"historical_unresolved":[{"original":r,"status":"HISTORICAL_UNRESOLVED_PROVENANCE","current_PASS_allowed":False}]}
        resolver=ReceiptResolver(root,index=index)
        with self.assertRaises(HistoricalUnresolvedProvenance):resolver.verify(r)
        self.assertIsNone(resolver.verify(r,scope="HISTORICAL"))
    def test_restore_alias_keeps_frozen_source_bytes_and_logical_path(self):
        root,old,index=self.alias_fixture();restore=self.base/"restore";restore.mkdir()
        for row in index["aliases"]:
            p=Path(row["archived"]["path"]);dest=restore/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(p,dest);dest.chmod(0o444)
        P=path_factory(root,restore,index);p=P(old["path"],expected_sha=old["sha256"])
        self.assertEqual(str(p),old["path"]);self.assertEqual(p.read_text(),"original version\n")
        self.assertEqual(str(p.resolve()),old["path"])
        self.assertEqual(P(p).expected_sha,old["sha256"])
    def test_independent_auditor_verifies_alias_without_original_evidence(self):
        root=self.base/"authority";root.mkdir();restore=self.base/"restore";restore.mkdir()
        script=root/"auditor.py";script.write_text("from pathlib import Path\nimport hashlib\n\ndef rec(p):\n p=Path(p).resolve(); b=p.read_bytes(); return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))\n")
        sr=d.rec(script);dest=restore/"auditor.py";shutil.copyfile(script,dest)
        data=root/"mutable.py";data.write_text("old");old=d.rec(data);snapshot=root/"old.py";snapshot.write_text("old")
        entry=archive_alias(old,snapshot,root/"aliases","HISTORICAL_EXACT_SOURCE_BYTES")
        a=Path(entry["archived"]["path"]);copied=restore/a.relative_to(root);copied.parent.mkdir(parents=True);shutil.copyfile(a,copied);copied.chmod(0o444)
        data.unlink();script.unlink()
        m=load_budget_auditor(sr,root,restore,{"aliases":[entry]})
        p=m.verify(old);self.assertEqual(p.read_text(),"old");self.assertEqual(m.rec(p)["path"],old["path"])
    def test_resource_closure_preserves_exact_references_and_excludes_engine_dependency(self):
        root=self.base/"authority";root.mkdir();p=root/"reference";p.write_text("reference");r=d.rec(p)
        c={"resources":[{"original":r,"copy":r,"copied":True,"scope":"SCIENTIFIC_SOURCE_INPUT_REFERENCE_OR_RAW_EVIDENCE"},
                        {"original":r,"copy":r,"copied":False,"scope":"RECOMPUTE_DEPENDENCY"}]}
        aliases=aliases_from_closure(c,root/"archive")
        self.assertEqual(len(aliases),1);self.assertEqual(aliases[0]["original"],r)
    def test_source_inclusion_has_v2_and_chosen_frozen_graph(self):
        rows=source_entries(R,"pilot_v7");paths={str(p) for p,_,_ in rows}
        for relative in ("source/rebuild/benchmark_inputs_v2.py","source/rebuild/benchmark_common_review_v2.py",
           "steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py",
           "steps/23_common_review/frozen/common_core_v2_13130/code/benchmark_common_review_v2.py",
           "steps/23_common_review/runs/downstream_frozen_13119/code/native_review_pipeline_v2.py",
           "steps/24_benchmark_delivery/code/github_export_verify.py"):
            self.assertIn(str(R/relative),paths)
    def v2_fixture(self,empty=False):
        p=self.protocol();p.update(protocol_id="TEST_FIXTURE_NO_SCIENCE",budget_gpu_seconds=3600)
        tasks=expected_tasks(p);plan={"status":"FROZEN_BEFORE_GENERATION","protocol":p,"tasks":tasks}
        cohort={"coverage":[],"selected":[]};rows=[]
        for task in tasks:
            cov={"task":task}
            for name,nreq in (("uniform_all_complete",3),("native_fixed_top_k",2)):
                n=0 if empty else 1
                cov[name]={"requested":nreq,"selected":n,"underfilled":n<nreq}
                if n:
                    cohort["selected"].append({"task_id":task["task_id"],"cohort":name,"cohort_record_id":task["task_id"]+"_"+name})
                    for engine,nmodel in (("boltz",3),("af2",5)):
                        value=.6 if task["method_id"]=="rf_diffusion" else .5
                        rows.append(dict(target_id=task["target_id"],method_id=task["method_id"],seed=task["seed"],cohort=name,engine=engine,
                          n_selected=1,n_R1_complete=1,R1_candidates=summary([value],1),R0_candidates=summary([1.1],1),
                          model_coverage={"expected":nmodel,"valid":nmodel}))
            cohort["coverage"].append(cov)
        return {"cohort_summaries":rows},plan,cohort
    def test_all_empty_28_arms_retain_112_cohort_engine_rows(self):
        common,plan,cohort=self.v2_fixture(empty=True)
        out=statistics(common,plan,cohort,"rf_diffusion","bindcraft")
        self.assertEqual(out["n_arms"],28);self.assertEqual(len(out["flat_cohort_engine_rows"]),112)
        self.assertEqual(out["n_empty_cohort_engine_rows"],112);self.assertEqual(len(out["rows"]),56)
        for row in out["comparisons"]:
            self.assertEqual(row["n_primary_targets"],6);self.assertEqual(row["n_paired_available"],0)
            self.assertIsNone(row["paired_macro_mean_RF_minus_BindCraft"])
    def test_all_underfilled_complete_outcomes_keep_valid_six_target_macro(self):
        common,plan,cohort=self.v2_fixture()
        out=statistics(common,plan,cohort,"rf_diffusion","bindcraft")
        self.assertTrue(all(r["underfilled"] for r in out["flat_cohort_engine_rows"]))
        self.assertEqual(out["comparisons"][0]["n_paired_available"],6)
        self.assertAlmostEqual(out["comparisons"][0]["paired_macro_mean_RF_minus_BindCraft"],.1)
    def test_one_empty_primary_arm_blocks_macro_without_dropping_target(self):
        common,plan,cohort=self.v2_fixture();task=plan["tasks"][0];tid=task["task_id"]
        cohort["selected"]=[r for r in cohort["selected"] if not(r["task_id"]==tid and r["cohort"]=="uniform_all_complete")]
        cov=next(r for r in cohort["coverage"] if r["task"]["task_id"]==tid);cov["uniform_all_complete"]["selected"]=0
        common["cohort_summaries"]=[r for r in common["cohort_summaries"] if not(r["target_id"]==task["target_id"] and r["method_id"]==task["method_id"] and r["seed"]==task["seed"] and r["cohort"]=="uniform_all_complete")]
        out=statistics(common,plan,cohort,"rf_diffusion","bindcraft")
        self.assertEqual(out["n_cohort_engine_rows"],112);self.assertEqual(out["comparisons"][0]["n_paired_available"],5)
        self.assertIsNone(out["comparisons"][0]["paired_macro_mean_RF_minus_BindCraft"])
        self.assertEqual(out["comparisons"][1]["n_paired_available"],6)
    def test_missing_selected_model_not_quality_zero(self):
        common,plan,cohort=self.v2_fixture();row=common["cohort_summaries"][0]
        row["n_R1_complete"]=0;row["R1_candidates"]=summary([None],1);row["model_coverage"]["valid"]=2
        out=statistics(common,plan,cohort,"rf_diffusion","bindcraft")
        self.assertEqual(out["n_missing_selected_outcome_rows"],1);self.assertIsNone(out["comparisons"][0]["paired_macro_mean_RF_minus_BindCraft"])
    def test_missing_arm_coverage_is_rejected(self):
        common,plan,cohort=self.v2_fixture();cohort["coverage"].pop()
        with self.assertRaisesRegex(ValueError,"Every arm"):statistics(common,plan,cohort,"rf_diffusion","bindcraft")
    def test_nonempty_missing_engine_summary_is_rejected(self):
        common,plan,cohort=self.v2_fixture();common["cohort_summaries"].pop()
        with self.assertRaisesRegex(ValueError,"outcome row omitted"):statistics(common,plan,cohort,"rf_diffusion","bindcraft")
    def test_duplicate_summary_is_rejected(self):
        common,plan,cohort=self.v2_fixture();common["cohort_summaries"].append(copy.deepcopy(common["cohort_summaries"][0]))
        with self.assertRaisesRegex(ValueError,"Duplicate"):statistics(common,plan,cohort,"rf_diffusion","bindcraft")
    def test_frozen_task_identity_mismatch_is_rejected(self):
        common,plan,cohort=self.v2_fixture();plan["tasks"][0]["seed"]=99
        with self.assertRaisesRegex(ValueError,"28-arm"):statistics(common,plan,cohort,"rf_diffusion","bindcraft")
    def test_model_slot_denominator_mismatch_is_rejected(self):
        common,plan,cohort=self.v2_fixture();common["cohort_summaries"][0]["model_coverage"]["expected"]=2
        with self.assertRaisesRegex(ValueError,"Fixed model"):statistics(common,plan,cohort,"rf_diffusion","bindcraft")
    def test_restore_readonly_archive_modes_preserved(self):
        root=self.base/"authority";root.mkdir();p=root/"alias.py";p.write_text("frozen");p.chmod(0o444)
        cp=root/"config.json";cp.write_text('{"scope":"TEST_FIXTURE"}\n')
        vp=root/"validation.json";d.dump(vp,dict(status="FINAL_DELIVERY_CONFIG_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY",authority_root=str(root),
           phase_id="FIXTURE_NO_RELEASE",config=d.rec(cp),files={"alias.py":{"receipt":d.rec(p),"classification":"AUDIT"}},conditional_inference_dependencies=[]))
        with patch.object(d,"cpu",return_value={}):
            d.package(vp,self.base/"package",1);d.extract(self.base/"package/packaging_receipt.json",self.base/"restore")
        self.assertEqual((self.base/"restore/alias.py").stat().st_mode & 0o222,0)
def main():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests);result=unittest.TextTestRunner(verbosity=2).run(suite)
    output=Path(os.environ["DELIVERY_V2_OUTPUT"]);output.mkdir(parents=True,exist_ok=False)
    sources={p.name:d.rec(p) for p in sorted(Path(__file__).parent.iterdir()) if p.is_file() and p.suffix==".py"}
    d.dump(output/"acceptance.json",dict(status="DELIVERY_V2_CPU_CONTRACTS_ACCEPTED" if result.wasSuccessful() else "DELIVERY_V2_CPU_CONTRACTS_FAILED",
        tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),sources=sources,
        scientific_scope="ENGINEERING_FIXTURES_ONLY",production_benchmark_completed=False,ACTIVE_changed=False,source_staged=False))
    if not result.wasSuccessful():raise SystemExit(1)
if __name__=="__main__":main()

