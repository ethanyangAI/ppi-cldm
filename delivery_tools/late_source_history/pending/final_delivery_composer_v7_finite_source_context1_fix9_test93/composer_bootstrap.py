#!/usr/bin/env python3
"""First actual pureCPU source seal/contracts; independent from final science/archive gates."""
import importlib.util,json,os,shutil,sys,subprocess,unittest
from pathlib import Path
SOURCE=Path(__file__).resolve().parent
sys.path.insert(0,str(SOURCE))
import final_delivery_composer as original
def main():
    allocation=original.cpu();jid=os.environ["SLURM_JOB_ID"]
    original_sources=[original.rec(original.verify(original.rec(SOURCE/n),True))for n in original.FILES]
    out=original.R/"steps/24_benchmark_delivery/runs"/("final_composer_operational_provenance_contracts_"+jid);out.mkdir(parents=True,exist_ok=False)
    snap=original.R/"steps/24_benchmark_delivery/frozen"/("final_delivery_composer_v7_operational_source_provenance_"+jid)/"code";snap.mkdir(parents=True,exist_ok=False)
    for name in original.FILES:
        p=SOURCE/name;original.need(p.is_file()and not p.is_symlink()and not(p.stat().st_mode&0o222),"Reviewed readonly source required")
        shutil.copyfile(p,snap/name);(snap/name).chmod(0o444)
    dependency=snap.parent/"context_mapper_v4";dependency.mkdir()
    prepared=original.R/"steps/24_benchmark_delivery/pending/exact_context_mapper_v4"
    api=original.load("prepared_context_dependency_guard",SOURCE/"composer_context_api.py")
    for name in api.NAMES:
        p=prepared/name;original.need(p.is_file()and p.resolve()==p and not(p.stat().st_mode&0o222),"Reviewed readonly exact mapper14 dependency required")
        shutil.copyfile(p,dependency/name);(dependency/name).chmod(0o444)
        original.need(original.identity(original.rec(p))==original.identity(original.rec(dependency/name)),"Exact mapper dependency copy byte mismatch")
    dependency.chmod(0o555);snap.chmod(0o555);sys.path.insert(0,str(snap))
    spec=importlib.util.spec_from_file_location("sealed_final_composer",snap/"final_delivery_composer.py");m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    source=m.sources();m.original_source_readback(original_sources,source["composer"])
    for p in [snap/name for name in m.FILES]+[dependency/name for name in api.NAMES]:
        if p.suffix==".py":compile(p.read_bytes(),str(p),"exec",dont_inherit=True)
        if p.suffix==".sbatch":
            pr=subprocess.run(["bash","-n",str(p)],capture_output=True,text=True);m.need(pr.returncode==0,"CPU launcher parse failed: "+pr.stderr)
    sys.modules["final_delivery_composer"]=m
    ts=importlib.util.spec_from_file_location("sealed_final_composer_tests",snap/"test_final_delivery_composer.py");tests=importlib.util.module_from_spec(ts);ts.loader.exec_module(tests)
    hs=importlib.util.spec_from_file_location("sealed_export_context_tests",snap/"test_github_export_context.py");ht=importlib.util.module_from_spec(hs);hs.loader.exec_module(ht)
    rs=importlib.util.spec_from_file_location("sealed_restore_index_tests",snap/"test_restored_index_scope.py");rt=importlib.util.module_from_spec(rs);rs.loader.exec_module(rt)
    fs=importlib.util.spec_from_file_location("sealed_finite_source_context_tests",snap/"test_finite_source_delivery_context.py");ft=importlib.util.module_from_spec(fs);fs.loader.exec_module(ft)
    finite=m.finite_source_api()
    semantic_r=next(r for r in source["composer"]if Path(r["path"]).name==finite.SEMANTICS_NAME)
    semantic=finite._load_semantics_bytes(Path(semantic_r["path"]).read_bytes(),semantic_r)
    fixture_inputs=finite.CurrentInputs()
    fixture_receipts=[getattr(semantic,prefix+"_LEAF")for family,prefix,doc,proof in finite._history_definitions(semantic)]
    for r in fixture_receipts:fixture_inputs.read(r)
    ft.DATA_FIXTURE_BYTES=dict(fixture_inputs.payloads)
    fixture_inputs.end()
    operational_fixtures=finite.SoftwareOperationalByteFixtures()
    ft.OPERATIONAL_FIXTURE_BYTES=dict(operational_fixtures.raw)
    ft.OPERATIONAL_CONTROL_FIXTURE_BYTES={k[0]:v for k,v in operational_fixtures.inputs.payloads.items()}
    operational_fixtures.end()
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(tests),unittest.defaultTestLoader.loadTestsFromModule(ht),unittest.defaultTestLoader.loadTestsFromModule(rt),unittest.defaultTestLoader.loadTestsFromModule(ft)])
    with(out/"contracts.txt").open("x")as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
    (out/"contracts.txt").chmod(0o444)
    tr=m.dump(out/"contracts.json",dict(status="PASS"if result.wasSuccessful()else"FAIL",tests_run=result.testsRun,errors=len(result.errors),failures=len(result.failures),log=m.rec(out/"contracts.txt"),software_fixture_inputs=fixture_receipts,software_operational_source_provenance_byte_fixture_receipts=operational_fixtures.receipts,software_operational_source_provenance_byte_fixture_metadata=list(operational_fixtures.original.values()),software_operational_control_fixture_receipts=list(operational_fixtures.inputs.receipts.values()),software_operational_fixture_scope="EXACT_SIX_RAW_OPERATIONAL_TXT_OWN_BYTES_NOT_EXECUTED_NO_CHILD_IO_NOT_CODE44",software_fixture_input_native_before=list(fixture_inputs.original.values()),tested_source=source,all_owned_and_context_python_compile_PASS=True,all_launchers_bash_syntax_PASS=True))
    m.need(result.wasSuccessful()and result.testsRun==m.SOFTWARE_TESTS,"Actual finite Source composer software contracts failed")
    m.need(m.sources()==source,"Whole executing composer and frozen dependencies changed after software contracts")
    m.original_source_readback(original_sources,source["composer"])
    receipt=m.dump(out/"acceptance.json",dict(schema="final-composer-software.v7",status=m.SOFTWARE_STATUS,source=source,contracts=tr,allocation=allocation,entry=m.rec(snap/"final_delivery_composer.py"),CPU_launcher=m.rec(snap/"composer_cpu.sbatch"),software_fixture_inputs=fixture_receipts,software_operational_source_provenance_byte_fixture_receipts=operational_fixtures.receipts,software_operational_source_provenance_byte_fixture_metadata=list(operational_fixtures.original.values()),software_operational_control_fixture_receipts=list(operational_fixtures.inputs.receipts.values()),software_operational_fixture_scope="EXACT_SIX_RAW_OPERATIONAL_TXT_OWN_BYTES_NOT_EXECUTED_NO_CHILD_IO_NOT_CODE44",software_fixture_input_native_before=list(fixture_inputs.original.values()),software_fixture_input_native_after=list(fixture_inputs.original.values()),software_fixture_scope="EXACT_FOUR_DIAGNOSTIC_DOCUMENT_OWN_BYTES_DATA_NO_CHILD_TARGET_IO",original_executing_sources=original_sources,original_source_entry=original.rec(SOURCE/"composer_bootstrap.py"),original_owned_pre_and_post_byte_readback_PASS=True,actual_CPU_job_id=jid,scientific_scope="SOFTWARE_FIXTURES_ONLY",production_science_accepted=False,archive_or_restore_complete=False,ACTIVE_changed=False,no_GPU_submission=True))
    fixture_inputs.end();operational_fixtures.end();m.need(m.sources()==source,"Source44 changed after final software output")
    fixture_inputs.native_end();operational_fixtures.native_end();print(json.dumps(receipt))
if __name__=="__main__":main()
