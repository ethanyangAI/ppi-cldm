#!/usr/bin/env python3
"""Meaningful negative/restore/statistical gates; all outputs are test fixtures."""
import copy,hashlib,io,json,os,shutil,tarfile,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import delivery_core as d
from restore_resolver import path_factory,load_budget_auditor
from common_review_independent import summary,compare,chain_data,geometry,recompute_model
from target_statistics import target_statistics,POLICY
R=Path("/lustre/users/u21111210118/projects/test9")
class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=os.environ["TMPDIR"]);self.base=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def test_receipt_tamper(self):
        p=self.base/"bytes";p.write_bytes(b"accepted");r=d.rec(p);p.write_bytes(b"corrupt!")
        with self.assertRaises(ValueError):d.verify(r)
    def test_symlink_evidence_rejected(self):
        p=self.base/"bytes";p.write_bytes(b"x");link=self.base/"link";link.symlink_to(p)
        with self.assertRaises(ValueError):d.verify(d.rec(link),self.base)
    def test_restore_reads_restored_bytes_not_original(self):
        original=self.base/"authority";restore=self.base/"restore";original.mkdir();restore.mkdir()
        (original/"a.json").write_text("ORIGINAL_CHANGED");(restore/"a.json").write_text("FROZEN_BYTES")
        P=path_factory(original,restore)
        self.assertEqual(P(original/"a.json").read_text(),"FROZEN_BYTES")
        self.assertEqual(str(P(original/"a.json").parent),str(original))
    def test_restore_outside_path_denied(self):
        restore=self.base/"restore";restore.mkdir();P=path_factory(self.base/"authority",restore)
        with self.assertRaises(PermissionError):P("/etc/passwd").read_text()
    def test_restore_symlink_escape_denied(self):
        authority=self.base/"authority";restore=self.base/"restore";restore.mkdir()
        (restore/"escape").symlink_to("/etc/passwd");P=path_factory(authority,restore)
        with self.assertRaises(PermissionError):P(authority/"escape").read_text()
    def test_restore_nested_root_not_double_remapped(self):
        authority=self.base/"authority";restore=authority/"restore";restore.mkdir(parents=True)
        (restore/"a").write_text("x");P=path_factory(authority,restore)
        self.assertEqual(P(restore/"a").read_text(),"x")
    def test_public_source_inventory_excludes_run_artifacts(self):
        rows=d.source_entries(R)
        self.assertTrue(any(p.name=="paired_budget_independent.py" for p,_,_ in rows))
        self.assertTrue(any(p.name=="cpu_readiness.py" for p,_,_ in rows))
        self.assertFalse(any(p.suffix in d.PROHIBITED_PUBLIC or "__pycache__" in p.parts or "/runs/" in str(p) for p,_,_ in rows))
        self.assertTrue(any(dest==Path("rebuild/benchmark_inputs.py") for _,dest,_ in rows))
    def test_packaging_restore_keeps_json_bytes(self):
        authority=self.base/"authority";authority.mkdir();p=authority/"plan.json";p.write_text('{"absolute":"/old/authority/a","state":"FIXTURE"}\n')
        config=authority/"config.json";config.write_text('{"scope":"TEST_FIXTURE"}\n')
        v=dict(status="FINAL_DELIVERY_CONFIG_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY",authority_root=str(authority),
               phase_id="FIXTURE_NOT_A_RELEASE",config=d.rec(config),files={"plan.json":dict(receipt=d.rec(p),classification="AUDIT")},
               conditional_inference_dependencies=[])
        validation=authority/"validation.json";d.dump(validation,v)
        with patch.object(d,"cpu",return_value={"allocated_gpus":0}):
            package=d.package(validation,self.base/"package",1)
            receipt=self.base/"package/packaging_receipt.json";result=d.extract(receipt,self.base/"restored")
        self.assertEqual((self.base/"restored/plan.json").read_bytes(),p.read_bytes())
        self.assertFalse(result["frozen_plan_bytes_changed"])
        self.assertEqual(result["status"],"RESTORED_HASHES_VERIFIED_CONTENT_RECOMPUTATION_PENDING")
    def test_unsafe_tar_member_rejected(self):
        data=self.base/"bad.tar"
        with tarfile.open(data,"w") as t:
            m=tarfile.TarInfo("../escape");m.size=1;t.addfile(m,io.BytesIO(b"x"))
        pkg=self.base/"pkg.json";r=d.rec(data)
        d.dump(pkg,dict(status="PACKAGED_AWAITING_INDEPENDENT_RESTORE",parts=[r],archive_sha256=r["sha256"],archive_bytes=r["bytes"],
                       manifest=[dict(relative="../escape",receipt=r,classification="AUDIT")]))
        with patch.object(d,"cpu",return_value={}):
            with self.assertRaises(ValueError):d.extract(pkg,self.base/"restore")
    def test_package_corruption_rejected_before_extraction(self):
        p=self.base/"part";p.write_bytes(b"abc");r=d.rec(p);p.write_bytes(b"def")
        pkg=self.base/"pkg.json";d.dump(pkg,dict(status="PACKAGED_AWAITING_INDEPENDENT_RESTORE",parts=[r],archive_sha256=r["sha256"],archive_bytes=3,manifest=[]))
        with patch.object(d,"cpu",return_value={}):
            with self.assertRaises(ValueError):d.extract(pkg,self.base/"restore")
    def validation_fixture(self):
        root=self.base/"fixture_authority";root.mkdir()
        old={}
        files=[]
        for name in ("phase","reconstruction","report"):
            path=root/(name+".json");path.write_text('{"scope":"OLD_TEST_FIXTURE"}\\n')
            old[{"phase":"current_phase","reconstruction":"reconstruction","report":"human_report"}[name]]=d.rec(path)
            files.append({"receipt":d.rec(path),"classification":"AUTHORITY_SNAPSHOT"})
        old["phase_id"]="OLD_FIXTURE";active=root/"ACTIVE.json";d.dump(active,old)
        files.append({"receipt":d.rec(active),"classification":"AUTHORITY_SNAPSHOT"})
        gates={}
        for name in d.GATES:
            obj={"status":"FIXTURE_ACCEPTED"}
            if name=="generation_accounting":obj.update(complete_generation_matrix=True,expected_tasks=28)
            if name=="common_review_content":obj.update(status="COMMON_REVIEW_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY",independent_experimental_validation=False)
            if name=="source_release":obj.update(commit="a"*40,working_tree_clean=True)
            path=root/(name+".json");d.dump(path,obj)
            gates[name]={"receipt":d.rec(path),"expect":{"status":obj["status"]}}
            files.append({"receipt":d.rec(path),"classification":"AUDIT"})
        config={"schema":d.SCHEMA,"scientific_scope":"COMPUTATIONAL_ONLY","authority_root":str(root),"phase_id":"NEW_FIXTURE",
                "previous_active":d.rec(active),"gates":gates,"files":files}
        return root,config
    def test_validation_rejects_missing_delivery_gate(self):
        root,config=self.validation_fixture();del config["gates"]["runtime_gpu_pilot"]
        path=root/"config.json";d.dump(path,config)
        with patch.object(d,"cpu",return_value={}):
            with self.assertRaisesRegex(ValueError,"gate omitted"):d.validate(path,root/"validation.json")
    def test_validation_rejects_incomplete_generation_matrix(self):
        root,config=self.validation_fixture();receipt=config["gates"]["generation_accounting"]["receipt"]
        path=Path(receipt["path"]);obj=d.read(path);obj["complete_generation_matrix"]=False;path.write_text(json.dumps(obj))
        config["gates"]["generation_accounting"]["receipt"]=d.rec(path)
        cp=root/"config.json";d.dump(cp,config)
        with patch.object(d,"cpu",return_value={}):
            with self.assertRaisesRegex(ValueError,"28 paired"):d.validate(cp,root/"validation.json")
    def test_validation_rejects_uncommitted_source_claim(self):
        root,config=self.validation_fixture();receipt=config["gates"]["source_release"]["receipt"]
        path=Path(receipt["path"]);obj=d.read(path);obj["working_tree_clean"]=False;path.write_text(json.dumps(obj))
        config["gates"]["source_release"]["receipt"]=d.rec(path);cp=root/"config.json";d.dump(cp,config)
        with patch.object(d,"cpu",return_value={}):
            with self.assertRaisesRegex(ValueError,"clean source"):d.validate(cp,root/"validation.json")
    def test_missing_outcome_never_becomes_zero(self):
        v=summary([.9,None,.7],3)
        self.assertIsNone(v["median"]);self.assertEqual(v["n_missing"],1);self.assertAlmostEqual(v["observed_only_median"],.8)
    def protocol(self):
        return dict(targets=[dict(target_id="t"+str(i),analysis_role="primary") for i in range(6)]+[dict(target_id="b",analysis_role="diagnostic")],
            methods=[dict(method_id="rf_diffusion"),dict(method_id="bindcraft")],replicate_seeds=[1,2],
            sampling=dict(uniform_n_per_replicate=3,native_top_k_per_replicate=2))
    def summaries(self):
        rows=[]
        for target in self.protocol()["targets"]:
            for method in ("rf_diffusion","bindcraft"):
                for engine in ("boltz","af2"):
                    for cohort in ("uniform_all_complete","native_fixed_top_k"):
                        for seed in (1,2):
                            quality=.6 if method=="rf_diffusion" else .5
                            rows.append(dict(target_id=target["target_id"],method_id=method,engine=engine,cohort=cohort,seed=seed,
                                n_selected=1,n_R1_complete=1,R1_candidates=summary([quality],1),R0_candidates=summary([1.1],1),model_coverage=dict(expected=3,valid=3)))
        return rows
    def test_primary_target_n_excludes_diagnostic_and_allows_underfill(self):
        out=target_statistics({"cohort_summaries":self.summaries()},self.protocol(),"rf_diffusion","bindcraft")
        p=out["comparisons"][0];self.assertEqual(p["n_primary_targets"],6);self.assertEqual(p["n_paired_available"],6)
        self.assertAlmostEqual(p["paired_macro_mean_RF_minus_BindCraft"],.1)
        self.assertTrue(out["rows"][0]["replicates"][0]["underfilled"])
        self.assertIsNone(p["inferential_p_value"]);self.assertIsNone(p["inferential_confidence_interval"])
    def test_one_missing_primary_replicate_blocks_full_macro(self):
        rows=self.summaries();rows=[r for r in rows if not(r["target_id"]=="t0" and r["method_id"]=="rf_diffusion" and r["engine"]=="boltz" and r["cohort"]=="uniform_all_complete" and r["seed"]==2)]
        out=target_statistics({"cohort_summaries":rows},self.protocol(),"rf_diffusion","bindcraft")
        p=out["comparisons"][0];self.assertEqual(p["n_primary_targets"],6);self.assertEqual(p["n_paired_available"],5)
        self.assertIsNone(p["paired_macro_mean_RF_minus_BindCraft"]);self.assertEqual(p["status"],"FULL_MATRIX_COMPARISON_UNRESOLVED")
    def test_missing_diagnostic_does_not_change_primary_macro(self):
        rows=[r for r in self.summaries() if r["target_id"]!="b"]
        out=target_statistics({"cohort_summaries":rows},self.protocol(),"rf_diffusion","bindcraft")
        self.assertEqual(out["comparisons"][0]["n_paired_available"],6)
        self.assertTrue(all(r["quality_R1"] is None for r in out["rows"] if r["target_id"]=="b"))
    def test_numerical_mismatch_is_not_accepted(self):
        with self.assertRaises(ValueError):compare({"R1":.7},{"R1":.8})
    def test_perfect_geometry_and_missing_reference_mapping(self):
        a=dict(sequence="AAA",ca=__import__("numpy").array([[0,0,0],[4,0,0],[0,4,0]],float),
               heavy=[__import__("numpy").array([[0,0,0]],float),__import__("numpy").array([[4,0,0]],float),__import__("numpy").array([[0,4,0]],float)])
        b=dict(sequence="AA",ca=__import__("numpy").array([[0,0,3],[4,0,3]],float),
               heavy=[__import__("numpy").array([[0,0,3]],float),__import__("numpy").array([[4,0,3]],float)])
        g=geometry(a,b,a,b,{1:1,2:2,3:3},False,{})
        self.assertAlmostEqual(g["target_recovery_RMSD_A"],0,places=10);self.assertEqual(g["native_interface_coverage"],1)
        with self.assertRaises(ValueError):geometry(a,b,dict(a,sequence="CAA"),b,{1:1,2:2,3:3},False,{})
    def test_public_secret_scanner(self):
        secret="pass"+"word = 'A1B2C3D4E5F6G7H8'"
        self.assertIsNotNone(d.SECRET_RE.search(secret))
        self.assertIsNone(d.SECRET_RE.search("password = os.environ.get('TOKEN')"))
    def test_independent_budget_import_uses_restored_source(self):
        original=self.base/"authority";restore=self.base/"restore";original.mkdir();restore.mkdir()
        source=restore/"audit.py";source.write_text("from pathlib import Path\n\ndef read(path): return Path(path).read_text()\n")
        receipt=d.rec(source);receipt["path"]=str(original/"audit.py")
        (restore/"raw").write_text("restored");(original/"raw").write_text("changed")
        m=load_budget_auditor(receipt,original,restore)
        self.assertEqual(m.read(str(original/"raw")),"restored")
    def test_real_boltz_independent_raw_scores_and_geometry(self):
        fixture=d.read(R/"steps/23_common_review/runs/integration_12969/acceptance.json")
        row=fixture["boltz"];original_root=R;restore=self.base/"restore";restore.mkdir()
        ident=d.read(R/"steps/22_matched_benchmark/input_preparation/runs/12956/targets/MDM2_1YCR/identity.json")
        ipsae=R/"vendor/IPSAE_6174cf9e71cb/ipsae.py"
        records=row["raw_files"]+[ident["reference_complex"],d.rec(ipsae)]
        for r in records:
            p=Path(r["path"]);dest=restore/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
        P=path_factory(R,restore);chains=chain_data(P(row["raw_files"][0]["path"]).physical());refs=chain_data(P(ident["reference_complex"]["path"]).physical())
        e=dict(target_sequence=chains[0]["sequence"],binder_sequence=chains[1]["sequence"])
        target=dict(reference_complex=ident["reference_complex"],query_to_reference_indices=ident["design_to_reference_indices"],
                   native_partner_query_to_reference_indices={str(i):i for i in range(1,len(refs[1]["sequence"])+1)})
        actual=recompute_model("boltz",row,e,target,True,P(ipsae).physical(),P,restore/"recomputed")
        for name,value in actual.items():compare(value,row[name],"real_boltz."+name)
        self.assertAlmostEqual(actual["R0"],row["R0"],places=12)
        self.assertEqual(actual["R1"],row["R1"])
    def test_real_af2_independent_R0_units(self):
        fixture=d.read(R/"steps/23_common_review/runs/integration_12969/acceptance.json")
        row={"raw_files":fixture["af2"]["raw_files"]};restore=self.base/"restore";restore.mkdir()
        ident=d.read(R/"steps/22_matched_benchmark/input_preparation/runs/12956/targets/MDM2_1YCR/identity.json")
        ipsae=R/"vendor/IPSAE_6174cf9e71cb/ipsae.py"
        for r in row["raw_files"]+[ident["reference_complex"],d.rec(ipsae)]:
            p=Path(r["path"]);dest=restore/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
        P=path_factory(R,restore);chains=chain_data(P(row["raw_files"][0]["path"]).physical())
        e=dict(target_sequence=chains[0]["sequence"],binder_sequence=chains[1]["sequence"])
        target=dict(reference_complex=ident["reference_complex"],query_to_reference_indices=ident["design_to_reference_indices"])
        actual=recompute_model("af2",row,e,target,False,P(ipsae).physical(),P,restore/"recomputed")
        self.assertAlmostEqual(actual["R0"],fixture["af2"]["accepted_R0"],places=12)
def main():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests);result=unittest.TextTestRunner(verbosity=2).run(suite)
    out=R/"steps/24_benchmark_delivery/runs"/("contracts_"+os.environ["SLURM_JOB_ID"]);out.mkdir(parents=True,exist_ok=False)
    sources={p.name:d.rec(p) for p in sorted(Path(__file__).parent.iterdir()) if p.is_file() and p.suffix==".py"}
    d.dump(out/"acceptance.json",dict(status="DELIVERY_HELPERS_CPU_CONTRACTS_ACCEPTED" if result.wasSuccessful() else "DELIVERY_HELPERS_CONTRACTS_FAILED",
        tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),source_receipts=sources,
        scientific_scope="ENGINEERING_TEST_FIXTURES_ONLY",production_benchmark_completed=False,ACTIVE_changed=False))
    if not result.wasSuccessful():raise SystemExit(1)
if __name__=="__main__":main()

