#!/usr/bin/env python3
"""First source sealing and software tests, pureCPU. No GPU dispatch."""
import importlib.util,json,os,shutil,subprocess,sys,unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
SOURCE=Path(__file__).resolve().parent
sys.path.insert(0,str(SOURCE))
import common_review_successor as authority
def main():
 authority.cpu()
 jid=os.environ["SLURM_JOB_ID"]
 out=R/"steps/24_benchmark_delivery/runs"/("common_successor_contracts_"+jid)
 out.mkdir(parents=True,exist_ok=False)
 snapshot=R/"steps/24_benchmark_delivery/frozen"/("common_review_successor_v5_"+jid)/"code"
 snapshot.mkdir(parents=True,exist_ok=False)
 for name in authority.FILES:
  p=SOURCE/name
  authority.need(not p.is_symlink()and not(p.stat().st_mode&0o222),"Reviewed readonly source required")
  shutil.copyfile(p,snapshot/name);(snapshot/name).chmod(0o444)
 snapshot.chmod(0o555)
 sys.path.insert(0,str(snapshot))
 spec=importlib.util.spec_from_file_location("sealed_successor",snapshot/"common_review_successor.py")
 sealed=importlib.util.module_from_spec(spec);spec.loader.exec_module(sealed)
 source=sealed.sources()
 for name in authority.FILES:
  p=snapshot/name
  if p.suffix==".py":compile(p.read_bytes(),str(p),"exec",dont_inherit=True)
  if p.suffix==".sbatch":
   proc=subprocess.run(["bash","-n",str(p)],capture_output=True,text=True);sealed.need(proc.returncode==0,"Bash source parse failed: "+proc.stderr)
 sys.modules["common_review_successor"]=sealed
 test_spec=importlib.util.spec_from_file_location("sealed_successor_tests",snapshot/"test_common_review_successor.py");tests=importlib.util.module_from_spec(test_spec);test_spec.loader.exec_module(tests)
 with(out/"contracts.txt").open("x")as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
 rr=sealed.dump(out/"contracts.json",dict(status="PASS"if result.wasSuccessful()else"FAIL",tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),log=sealed.rec(out/"contracts.txt")))
 sealed.need(result.wasSuccessful()and result.testsRun==58,"Successor boundary contracts failed or missing")
 receipt=sealed.dump(out/"acceptance.json",dict(status="COMMON_SUCCESSOR_SOFTWARE_SOURCE_CPU_ACCEPTED_FUTURE_FORMAL_PREPARATION_PENDING",source=source,contracts=rr,entry=sealed.rec(snapshot/"common_review_successor.py"),CPU_launcher=sealed.rec(snapshot/"common_review_cpu.sbatch"),GPU_launcher=sealed.rec(snapshot/"common_review_gpu.sbatch"),no_inference=True,no_GPU_submission=True,actual_CPU_job_id=jid,future_formal_binding=False))
 print(json.dumps(receipt))
if __name__=="__main__":main()
