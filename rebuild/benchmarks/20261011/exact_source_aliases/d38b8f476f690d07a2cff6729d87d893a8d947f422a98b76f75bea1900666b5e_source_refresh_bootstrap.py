#!/usr/bin/env python3
"""Actual pureCPU source seal and software fixtures; no science gate substitution."""
import argparse,hashlib,json,os,subprocess,sys,unittest
from pathlib import Path
from delivery_core import cpu,rec,dump
R=Path("/lustre/users/u21111210118/projects/test9")
FAILED=R/"steps/24_benchmark_delivery/frozen/source_refresh_v1_13262/code"
NAMES=("source_delivery_refresh_v7.py","relative_receipt_policy.py","test_relative_receipt_policy.py","source_refresh_bootstrap.py","source_refresh_cpu.sbatch","HANDOFF.md","delivery_core.py","delivery_graph_v2.py","provenance_aliases_v2.py","native_resource_closure_v2.py","reference_source_delivery_refresh_v1.py")
PINS={"delivery_core.py":(21656,"5e1e1f3f2e8a5f2c5771508b7e9433139ee36d58d5b2cc6514bf97333973ca4c"),"delivery_graph_v2.py":(8774,"e14b12e01c8e2b9a70ecb30d70d2194bbe89147c01eb02dd305be4075276f98d"),"provenance_aliases_v2.py":(5048,"1de9f0ba13cf8774f6de0fbe4410fd41b8dacf5e9e6d5f1f969b9842f1d8bd01"),"native_resource_closure_v2.py":(20444,"33a1a8103efbf5d467e9e8360b9bac2f04624e1f1a5929caaa3cc282c6a66c48")}
def need(value,message):
 if not value:raise ValueError(message)
def contracts(out):
 allocation=cpu();need(os.environ.get("PYTHONDONTWRITEBYTECODE")=="1"and "PYTHONPATH"not in os.environ,"Readonly import isolation required")
 here=Path(__file__).resolve().parent;need(not(here.stat().st_mode&0o222),"Source package must be readonly")
 out=Path(out);need(out.is_absolute()and out.is_relative_to(R)and out.resolve()==out,"CPU output outside authority")
 out.mkdir(parents=True,exist_ok=False)
 stage="source_seal"
 try:
  receipts=[]
  for name in NAMES:
   p=here/name;need(p.is_file()and not p.is_symlink()and not(p.stat().st_mode&0o222),"Readonly exact source absent: "+name)
   receipts.append(rec(p))
   if name in PINS:
    need((p.stat().st_size,rec(p)["sha256"])==PINS[name],"Frozen13262 dependency differs: "+name)
    original=FAILED/name
    need(original.is_file()and not(original.stat().st_mode&0o222)and not original.is_symlink(),"Failed13262 dependency unavailable")
    need((original.stat().st_size,rec(original)["sha256"])==PINS[name],"Original frozen13262 dependency differs: "+name)
   if name.endswith(".py"):compile(p.read_bytes(),str(p),"exec",dont_inherit=True)
   if name.endswith(".sbatch"):subprocess.run(["bash","-n",str(p)],check=True)
  old=FAILED/"source_delivery_refresh_v1.py"
  need(old.is_file()and not(old.stat().st_mode&0o222)and old.stat().st_size==17160,"Failed13262 source identity unavailable")
  need(rec(old)["sha256"]==rec(here/"reference_source_delivery_refresh_v1.py")["sha256"],"Copied failed13262 source differs")
  dump(out/"source_snapshot.json",{"schema":"source-refresh-relative-software-source.v7","source_receipts":receipts,"failed13262_reference":rec(old),"frozen_dependency_receipts":[rec(FAILED/n)for n in PINS],"allocation":allocation})
  stage="software_contracts"
  import test_relative_receipt_policy as fixture
  suite=unittest.defaultTestLoader.loadTestsFromModule(fixture)
  need(suite.countTestCases()==58,"Expected58 relative edge contracts")
  with(out/"contracts.txt").open("x")as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
  tests=dump(out/"contracts.json",{"status":"PASS"if result.wasSuccessful()else"FAIL","tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"log":rec(out/"contracts.txt")})
  need(result.wasSuccessful(),"Software relative context contracts failed")
  accepted={"schema":"source-refresh-relative-software-acceptance.v7","status":"SOURCE_REFRESH_RELATIVE_SOFTWARE_CPU_ACCEPTED_ACTUAL_SOURCE_AUDIT_PENDING","source_snapshot":rec(out/"source_snapshot.json"),"contracts":tests,"allocation":allocation,"compiled_all_python":True,"bash_syntax_checked":True,"tests_expected":58,"scientific_settings_changed":False,"models_recomputed":False,"GPU_submitted":False,"source_staged":False,"ACTIVE_changed":False}
  dump(out/"acceptance.json",accepted)
  for p in out.iterdir():p.chmod(0o444)
  out.chmod(0o555)
  return accepted
 except Exception as error:
  dump(out/"typed_incomplete.json",{"schema":"source-refresh-relative-software-incomplete.v7","status":"SOURCE_REFRESH_RELATIVE_SOFTWARE_INCOMPLETE","failed_stage":stage,"error_type":type(error).__name__,"error":str(error),"GPU_submitted":False,"source_staged":False,"ACTIVE_changed":False})
  raise
def main():
 parser=argparse.ArgumentParser();parser.add_argument("--out",required=True);args=parser.parse_args()
 print(json.dumps(contracts(args.out),ensure_ascii=False))
if __name__=="__main__":main()
