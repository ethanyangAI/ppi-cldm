#!/usr/bin/env python3
"""First actual pureCPU source seal/contracts; independent from final science/archive gates."""
import importlib.util,json,os,shutil,sys,subprocess,unittest
from pathlib import Path
SOURCE=Path(__file__).resolve().parent
sys.path.insert(0,str(SOURCE))
import final_delivery_composer as original
def main():
    allocation=original.cpu();jid=os.environ["SLURM_JOB_ID"]
    out=original.R/"steps/24_benchmark_delivery/runs"/("final_composer_contracts_"+jid);out.mkdir(parents=True,exist_ok=False)
    snap=original.R/"steps/24_benchmark_delivery/frozen"/("final_delivery_composer_v4_"+jid)/"code";snap.mkdir(parents=True,exist_ok=False)
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
    source=m.sources()
    for p in [snap/name for name in m.FILES]+[dependency/name for name in api.NAMES]:
        if p.suffix==".py":compile(p.read_bytes(),str(p),"exec",dont_inherit=True)
        if p.suffix==".sbatch":
            pr=subprocess.run(["bash","-n",str(p)],capture_output=True,text=True);m.need(pr.returncode==0,"CPU launcher parse failed: "+pr.stderr)
    sys.modules["final_delivery_composer"]=m
    ts=importlib.util.spec_from_file_location("sealed_final_composer_tests",snap/"test_final_delivery_composer.py");tests=importlib.util.module_from_spec(ts);ts.loader.exec_module(tests)
    with(out/"contracts.txt").open("x")as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
    (out/"contracts.txt").chmod(0o444)
    tr=m.dump(out/"contracts.json",dict(status="PASS"if result.wasSuccessful()else"FAIL",tests_run=result.testsRun,errors=len(result.errors),failures=len(result.failures),log=m.rec(out/"contracts.txt"),tested_source=source,all_owned_and_context_python_compile_PASS=True,all_launchers_bash_syntax_PASS=True))
    m.need(result.wasSuccessful()and result.testsRun==m.SOFTWARE_TESTS,"Actual66 composer software contracts failed")
    m.need(m.sources()==source,"Whole executing composer and frozen dependencies changed after software contracts")
    receipt=m.dump(out/"acceptance.json",dict(schema="final-composer-software.v4",status=m.SOFTWARE_STATUS,source=source,contracts=tr,allocation=allocation,entry=m.rec(snap/"final_delivery_composer.py"),CPU_launcher=m.rec(snap/"composer_cpu.sbatch"),actual_CPU_job_id=jid,scientific_scope="SOFTWARE_FIXTURES_ONLY",production_science_accepted=False,archive_or_restore_complete=False,ACTIVE_changed=False,no_GPU_submission=True))
    print(json.dumps(receipt))
if __name__=="__main__":main()
