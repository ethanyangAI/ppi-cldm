#!/usr/bin/env python3
"""Root-only reviewed three-path integration; actual tested library and scientific gates required."""
import argparse,hashlib,importlib.util,json,os,re,shutil,subprocess,sys,traceback,unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
BASE="c3d528bb6801a7a571cdd20bfd90652e397a8540a136e1f0510ef0ccc5488dde"
PATHS=("src/ppiblocker/pipeline.py","src/ppiblocker/pose_physical_gate.py","environment/runtime-lock-rfd.json")
OWN=("integrate_default_workflow_v3.py","test_integrate_default_workflow_v3.py","default_integration_cpu_v3.sbatch","HANDOFF.md")
LIB=("final_source_closure.py","test_final_source_closure.py","final_source_cpu.sbatch","HANDOFF.md","FINAL_SOURCE_CHECKLIST.md","final_source_context_adapter.py")
LIB_TESTS=53
TESTS=84
STATUS="DEFAULT_GENERIC_PHYSICAL_GATE_AND_MATERIALIZED_RUNTIME_INTEGRATION_CPU_VERIFIED_NOT_PUBLISHED"
SOFTWARE_STATUS="DEFAULT_MATERIALIZED_INTEGRATION_SOFTWARE_CPU_ACCEPTED_NO_DEFAULT_WRITE"
GATES={"source_refresh_current","generic_materialized_repair_current","physical_preflight_v3_current","materialization13281"}
GATE_JOBNAMES={"source_refresh_current":"test9_source_relative_v10","generic_materialized_repair_current":"test9_generic_materialized_repair_v3","physical_preflight_v3_current":"test9_native_physical_preflight_v3","materialization13281":"test9_rfd_cache_materialization_cpu"}
REGRESSIONS={"test_development_regressions.py","test_audit_regressions.py","test_benchmark.py","test_construct_contract.py","test_scientific_contracts.py","test_runtime_registration.py","test_af2_review.py"}
PHYSICAL={"test_pose_physical_gate.py","test_e2e_resource_policy.py","test_e2e_design_contracts.py"}
def need(value,message):
 if not value:raise ValueError(message)
def raw_rec(p):
 p=Path(p);return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def boot_path(p,readonly=True):
 p=Path(p)
 need(p.is_absolute()and p.is_relative_to(R)and p.resolve()==p and not p.is_symlink()and p.is_file(),"Exact authority-local file required")
 need(not readonly or not(p.stat().st_mode&0o222),"Readonly accepted source required")
 return p
def boot_verify(r):
 p=boot_path(r["path"]);need(raw_rec(p)==r,"Actual accepted software/source bytes differ");return p
def terminal(jid,state="COMPLETED",jobname=None):
 need(str(jid).isdigit(),"Numeric actual CPU job required")
 raw=subprocess.check_output(["sacct","-X","-j",str(jid),"--noheader","--parsable2","--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocTRES,User%64,Account%64,JobName%100,Partition%64"],text=True)
 rows=[x.split("|")for x in raw.splitlines()if x.split("|",1)[0]==str(jid)];need(len(rows)==1,"Unique actual accounting row required")
 row=rows[0];need(len(row)>=9 and re.fullmatch("[0-9]+",row[3])is not None,"Complete numeric actual terminal accounting required")
 if state=="CANCELLED"and row[3]=="0"and row[4]=="":cpus,gpu,vals=0,0,{}
 else:cpus,gpu,vals=allocated_cpu_tres({"AllocTRES":row[4]})
 need(row[1].split()[0]==state and gpu==0 and row[5:7]==["u21111210118","u21111210118"]and row[8]=="organ","Wrong terminal ownership/state/GPU")
 if state=="COMPLETED":need(row[2]=="0:0"and cpus>=1,"Actual successful pureCPU allocation required")
 if jobname:need(row[7]==jobname,"Wrong actual software/science job source")
 return dict(job_id=str(jid),state=row[1],exit_code=row[2],elapsed_seconds=int(row[3]),allocated_TRES=row[4],allocated_CPUs=cpus,allocated_GPUs=gpu,raw_sacct=raw)
def bind_library(acceptance):
 p=boot_path(acceptance);before=raw_rec(p);sw=json.loads(p.read_text());need(raw_rec(p)==before,"Library acceptance changed during read")
 need(sw.get("schema")=="final-source-materialized-software-acceptance.v3"and sw.get("status")=="FINAL_SOURCE_MATERIALIZED_ARCHIVE_CONTEXT_AND_DERIVED_V2_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_INTEGRATION","Actual final-source library software-only gate required")
 rows=sw["source_files"];need(len(rows)==6 and {Path(x["path"]).name for x in rows}==set(LIB),"Exactly six accepted library files required")
 parent={str(Path(x["path"]).parent)for x in rows};need(len(parent)==1,"One exact tested library package required")
 for r in rows:boot_verify(r)
 contracts=json.loads(boot_verify(sw["contracts"]).read_text())
 need(contracts.get("status")=="PASS"and contracts.get("tests")==LIB_TESTS and contracts.get("failures")==0 and contracts.get("errors")==0,"Actual exact library contract counts required")
 need(contracts.get("tested_source_files")==rows and contracts.get("owned_python_compile_PASS")is True and contracts.get("bash_syntax_PASS")is True,"Actual library tested source and compile flags required")
 boot_verify(contracts["log"])
 accounting=terminal(sw["allocation"]["job_id"],jobname="test9_final_source_materialized_v3")
 here=Path(__file__).resolve().parent;copied=[]
 for r in rows:
  q=boot_path(here/"library"/Path(r["path"]).name)
  need((raw_rec(q)["sha256"],q.stat().st_size)==(r["sha256"],r["bytes"]),"Executing copied library differs from tested library")
  copied.append(dict(tested=r,executing=raw_rec(q)))
 sys.path.insert(0,str(here/"library"))
 spec=importlib.util.spec_from_file_location("accepted_final_source_library",here/"library/final_source_closure.py")
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 for name in ("rec","fp","read","verify","dump","cpu","safe_path","receipt_shape"):
  globals()[name]=getattr(module,name)
 need(module.R==R and module.SOURCE_CONTRACTS==LIB_TESTS,"Accepted library authority/count mismatch")
 globals()["library_module"]=module
 return dict(receipt=before,source_files=rows,executing_copies=copied,actual_CPU_accounting=accounting)
def tree_sha(source):
 return hashlib.sha256("".join(str(p.relative_to(source))+rec(p)["sha256"]for p in sorted((Path(source)/"src").rglob("*.py"))).encode()).hexdigest()
def source_bindings():
 here=Path(__file__).resolve().parent
 return [rec(boot_path(here/n))for n in OWN]+[rec(boot_path(here/"library"/n))for n in LIB]
def operation_plan(q):
 need(q.get("schema")=="default-generic-materialized-integration-request.v2"and q.get("root_approved")is True,"Explicit distinct three-path root request required")
 need(q.get("formal_array_job_id")=="13260"and q.get("formal_sources_changed")is False,"Frozen formal sources required")
 need(q.get("expected_old_tree_sha256")==BASE,"Exact original C3 tree required")
 need(set(q.get("gates",{}))==GATES,"Four actual source/generic/physical/materialization gates required")
 ops=q.get("operations");need(isinstance(ops,list)and len(ops)==3 and {x.get("repository_relative")for x in ops}==set(PATHS),"Exactly three authorized path operations required")
 by={x["repository_relative"]:x for x in ops}
 need(by[PATHS[0]].get("old")is not None and by[PATHS[1]].get("old")is None and by[PATHS[2]].get("old")is not None,"Only original pipeline/RFD replacement and absent helper creation")
 for o in ops:
  receipt_shape(o["new"])
  if o["old"]is not None:receipt_shape(o["old"])
 receipt_shape(q["staged_selector_test"])
 need(Path(q["staged_selector_test"]["path"]).name=="test_common_runtime_selector.py","Same accepted selector15 contracts required")
 need(q.get("runtime_lock_policy")=="EXACT_REVIEWED_FULL226_RFD_ONLY_CORE_BOLTZ_UNCHANGED","Only accepted full materialized RFD lock may replace old lock")
 for key,names in (("regression_tests",REGRESSIONS),("physical_tests",PHYSICAL)):
  rows=q.get(key,[]);need(len(rows)==len(names)and{Path(x["path"]).name for x in rows}==names,"All exact "+key+" files required")
  for r in rows:receipt_shape(r)
 need(set(q.get("original_runtime_locks",{}))=={"core","rfd","boltz"},"Three old lock identities required")
 for c,r in q["original_runtime_locks"].items():
  receipt_shape(r);need(r["path"]==str(R/"source/environment"/("runtime-lock-"+c+".json")),"Wrong original default lock path")
 for r in q["regression_tests"]:need(r["path"]==str(R/"source/tests"/Path(r["path"]).name),"Original same seven generic regression paths required")
 receipt_shape(q["context_mapper_acceptance"])
 return by
def history():
 out={}
 for jid,state in (("13262","FAILED"),("13263","FAILED"),("13279","FAILED"),("13293","FAILED"),("13297","FAILED"),("13305","FAILED"),("13307","FAILED"),("13303","FAILED"),("13267","CANCELLED")):
  row=terminal(jid,state)
  if jid=="13267":need(row["elapsed_seconds"]==0 and row["allocated_CPUs"]==0 and row["allocated_TRES"]=="","Old physical V2 cancellation must remain explicit unallocated zero-cost history")
  out[jid]=row
 return out
def gate(g,jobname):
 obj=read(verify(g["receipt"],True));account=terminal(g["cpu_job_id"],jobname=jobname)
 return obj,dict(receipt=g["receipt"],actual_CPU_accounting=account)
def prerequisites(q,ops,out):
 objects={};gates={}
 for role,g in q["gates"].items():objects[role],gates[role]=gate(g,GATE_JOBNAMES[role])
 source=objects["source_refresh_current"]
 need(source.get("schema")=="source-delivery-refresh.v3"and source.get("status")=="CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY"and source.get("current_recovered_evidence_file_n")==5 and source.get("historical_provenance_annotation_n")==9 and source.get("historical_archive_context_parent_n")==2 and source.get("archive_member_n")==588 and source.get("external_files_read")is False and source.get("source_issues")==0,"Actual source V10 gate required")
 inclusion=read(verify(source["source_inclusion"],True))
 need(str(inclusion["allocation"]["job_id"])==str(q["gates"]["source_refresh_current"]["cpu_job_id"]),"Actual current source CPU allocation differs")
 need(str(q["gates"]["source_refresh_current"]["cpu_job_id"])not in{"13262","13279","13293","13297","13305","13307"},"Failed old source jobs cannot satisfy gate")
 runner=inclusion["runner_source_snapshot"];need(any(Path(r["path"]).name=="source_delivery_refresh_v10.py"for r in runner),"Actual V10 source identity required")
 source_software(source,runner,q["gates"]["source_refresh_current"]["cpu_job_id"])
 gates["context_mapper"]=context_mapper_gate(q,source,out)
 for r in runner:verify(r,True)
 generic=objects["generic_materialized_repair_current"]
 need(generic.get("schema")=="generic-report-materialized-runtime-repair-acceptance.v3"and generic.get("status")=="GENERIC_REPORT_CONTENT_AND_MATERIALIZED_RUNTIME_V3_CPU_REPAIR_ACCEPTED_FAILED13263_13286_13287_PRESERVED"and generic.get("original13263_failure_preserved")is True and generic.get("failed13286_13287_preserved")is True,"Actual new generic repair required; old failures preserved")
 need(str(generic["slurm_job_id"])==str(q["gates"]["generic_materialized_repair_current"]["cpu_job_id"]),"Generic accepted allocation differs")
 saved_contracts(generic["contracts"],105,generic["source_files"],9)
 need(pre_status_gate(generic),"Generic CPU source/software compilation required")
 pre=objects["physical_preflight_v3_current"]
 need(pre.get("schema")=="REFERENCE_FREE_E2E_PHYSICAL_GATE_PREFLIGHT_AND_CPU_REQUALIFICATION_V3"and pre.get("status")=="CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED"and pre.get("contracts_count")==57,"Actual PhysicalV3 gate required")
 need(str(pre["slurm_job_id"])==str(q["gates"]["physical_preflight_v3_current"]["cpu_job_id"]),"Physical accepted allocation differs")
 need(pre.get("qualified_prediction",{}).get("status")in{"POSE_ACCEPTED","POSE_REJECTED"}and pre.get("native_inference_performed")is False,"Honest complete physical requalification required")
 need(pre["source_manifest"]==q["source_manifest"],"Exact accepted physical source manifest required")
 physical_contracts(pre)
 need(pre["generic_report_repair_acceptance"]==q["gates"]["generic_materialized_repair_current"]["receipt"],"Physical qualification must consume exact generic repair")
 override_receipt=q["reviewed_runtime_override_acceptance"];override=read(verify(override_receipt,True))
 need(generic["reviewed_runtime_override_acceptance"]==pre["reviewed_runtime_override_acceptance"]==override_receipt,"Same actual accepted runtime override required")
 need(override.get("schema")=="reviewed-runtime-override-acceptance.v1"and override.get("status")=="REVIEWED_FULL_MATERIALIZED_RFD_RUNTIME_OVERRIDE_CPU_ACCEPTED_DEFAULT_UNCHANGED"and override.get("cache_excluded_from_new_lock")is False and override.get("default_runtime_locks_unchanged")is True,"Full cache included reviewed runtime required")
 need(override["original_default_locks"]==pre["default_runtime_locks_unchanged"]==q["original_runtime_locks"],"Exact old default three locks differ")
 materialization=objects["materialization13281"]
 need(q["gates"]["materialization13281"]["cpu_job_id"]=="13281"and materialization.get("job_id")=="13281"and materialization.get("schema")=="rfd-cache-materialization.v1"and materialization.get("status")=="RFD_MATERIALIZED_IGSO3_RUNTIME_CPU_QUALIFIED_DEFAULT_LOCK_UNCHANGED","Actual13281 full cache materialization gate required")
 need(generic["materialization_acceptance"]==pre["materialization_acceptance"]==override["materialization_acceptance"]==q["gates"]["materialization13281"]["receipt"],"Same materialization source lineage required")
 need(set(override["runtime_locks"])=={"core","rfd","boltz"},"All reviewed runtime locks required")
 for c,r in override["runtime_locks"].items():
  verify(r,True)
  if c!="rfd":need(fp(r)==fp(q["original_runtime_locks"][c]),"Core/Boltz default lock bytes must remain unchanged")
 need(ops[PATHS[2]]["new"]==override["runtime_locks"]["rfd"]and ops[PATHS[2]]["old"]==q["original_runtime_locks"]["rfd"],"Only exact accepted full RFD lock can replace old RFD")
 snapshot=read(verify(q["source_manifest"],True));base=Path(q["source_manifest"]["path"]).parent
 need(snapshot.get("schema")=="physical_gate_source_snapshot.v1"and snapshot["base_python_source_sha256"]==BASE and snapshot.get("default_common_selector_is_original")is True,"Actual staged/base source identity required")
 target=snapshot["default_python_source_sha256_without_staged_runtime_selector"]
 need(target!=snapshot["patched_python_source_sha256"],"Staged/default distinct full Python identities required")
 promotions=snapshot["default_promotion_files"];need(len(promotions)==2 and {x["repository_relative"]for x in promotions}==set(PATHS[:2]),"Only two accepted promotion Python files")
 for row in promotions:
  if row["repository_relative"]!=PATHS[0] or not q.get("derived_pipeline_qualification"):need(ops[row["repository_relative"]]["new"]==row["source"],"Default Python promotion differs from accepted staged patch")
 records={r["path"]:r for r in snapshot["files"]};need(len(records)==len(snapshot["files"]),"Duplicate physical source inventory")
 need(ops[PATHS[0]]["old"]==records[str(base/"base_source"/PATHS[0])],"Exact original pipeline snapshot required")
 selector=snapshot["staged_runtime_selector"];need(selector["original_common"]==records[str(base/"base_source/src/ppiblocker/common.py")],"Original C3 common selector source differs")
 need(fp(selector["default_common_unchanged"])==fp(selector["original_common"])and selector["default_common_unchanged"]["path"]==str(R/"source/src/ppiblocker/common.py"),"Default common must remain original C3 bytes")
 need(fp(selector["staged_common"])!=fp(selector["original_common"]),"Staged runtime selector must never be promoted")
 for r in snapshot["files"]:verify(r,True)
 for r in q["physical_tests"]:
  need(r["path"]==str(base/Path(r["path"]).name)and records[r["path"]]==r,"Same accepted physical42 suite files required")
 need(records.get(q["staged_selector_test"]["path"])==q["staged_selector_test"]and q["staged_selector_test"]["path"]==str(base/"test_common_runtime_selector.py"),"Exact accepted selector15 source binding required")
 need(q.get("derived_pipeline_qualification")is not None,"Final production integration requires actual derivedV2 qualification")
 target,proof=derived_pipeline_gate(q,ops,snapshot,pre);gates["derived_pipeline_qualification"]=proof
 need(q["expected_new_tree_sha256"]==target,"Explicit accepted default source identity required")
 for r in q["regression_tests"]:verify(r,False)
 return objects,gates,override,snapshot,base,records
def expected_default(q,ops,snapshot,base,out,override):
 source=out/"expected_default/source";source.mkdir(parents=True)
 prefix=base/"base_source"
 rows=[r for r in snapshot["files"]if Path(r["path"]).is_relative_to(prefix)and Path(r["path"]).suffix==".py"]
 need(rows,"Explicit original Python source inventory required")
 for r in rows:
  relative=Path(r["path"]).relative_to(prefix);need(relative.parts[0]=="src","Only original Python source tree expected")
  target=source/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(verify(r,True),target)
 for n in PATHS[:2]:
  target=source/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(verify(ops[n]["new"],True),target)
 for c,r in override["runtime_locks"].items():
  target=source/"environment"/("runtime-lock-"+c+".json");target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(verify(r,True),target)
 need(tree_sha(source)==q["expected_new_tree_sha256"],"Explicit default clone differs from accepted default identity")
 common=source/"src/ppiblocker/common.py"
 need(fp(rec(common))==fp(snapshot["staged_runtime_selector"]["original_common"]),"Staged common must not enter expected default")
 files=[rec(p)for p in sorted(source.rglob("*"))if p.is_file()]
 for p in source.rglob("*"):
  if p.is_file():p.chmod(0o444)
 for p in sorted([p for p in source.rglob("*")if p.is_dir()],key=lambda p:len(p.parts),reverse=True):p.chmod(0o555)
 source.chmod(0o555)
 return source,dump(out/"expected_default_manifest.json",dict(schema="expected-default-materialized-source.v2",files=files,python_source_sha256=tree_sha(source),default_common_unchanged=rec(common),staged_common_not_installed=True))
def command(argv,cwd,env,prefix):
 result=subprocess.run(argv,cwd=cwd,env=env,capture_output=True,text=True)
 Path(str(prefix)+".stdout").write_text(result.stdout);Path(str(prefix)+".stderr").write_text(result.stderr)
 row=dict(argv=list(argv),cwd=str(cwd),returncode=result.returncode,stdout=rec(str(prefix)+".stdout"),stderr=rec(str(prefix)+".stderr"))
 dump(str(prefix)+".command.json",row);need(result.returncode==0,"Actual default regression/physical/runtime check failed")
 return row,result.stdout+"\n"+result.stderr
def checks(source,q,override,out,prefix,installed):
 core=str(R/"env/core/bin/python");env={**os.environ,"PYTHONPATH":str(source/"src"),"PYTHONDONTWRITEBYTECODE":"1"}
 generic_xml=out/(prefix+"_generic7.xml")
 generic_script="import sys;from pathlib import Path;from ppiblocker import pipeline,common;assert Path(pipeline.__file__)==Path(sys.argv[1]);assert pipeline.runtime_provenance is common.runtime_provenance;import pytest;raise SystemExit(pytest.main(sys.argv[2:]))"
 env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"]="1"
 generic,_=command([core,"-B","-c",generic_script,str(source/"src/ppiblocker/pipeline.py"),"-q","-p","no:cacheprovider","--junitxml="+str(generic_xml)]+[r["path"]for r in q["regression_tests"]],R/"source",env,out/(prefix+"_generic7"))
 import xml.etree.ElementTree as ET
 ss=list(ET.parse(generic_xml).getroot().iter("testsuite"));need(len(ss)==1,"Unique actual generic suite accounting required")
 counts={k:int(ss[0].attrib.get(k,"0"))for k in ("tests","failures","errors","skipped")}
 need(counts["tests"]>0 and all(counts[k]==0 for k in ("failures","errors","skipped")),"Actual generic7 tests must complete without skips/errors")
 generic.update(junit=rec(generic_xml),**counts)
 physical=[];count=0
 for r in q["physical_tests"]:
  row,log=command([core,"-B",r["path"]],R/"source",env,out/(prefix+"_"+Path(r["path"]).stem))
  matches=re.findall(r"(?:^|\n)Ran ([0-9]+) tests?\b",log);need(len(matches)==1,"Actual physical suite count required")
  row["tests"]=int(matches[0]);count+=row["tests"];physical.append(row)
 need(count==42,"Same actual physical42 suite required")
 # Collector executes real env/vendor/assets at R; no shadow environment or mocked runtime.
 script="import json,sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from ppiblocker import common,pipeline;from ppiblocker.pose_physical_gate import physical_pose_reasons;root=Path(sys.argv[2]);locks=json.loads(sys.argv[3]);assert pipeline.physical_pose_reasons is physical_pose_reasons;assert pipeline.runtime_provenance is common.runtime_provenance;results={c:common.collect_runtime(root,c) for c in ('core','rfd','boltz')};assert all(results[c]==common.read_json(locks[c]['path']) for c in results);out=Path(sys.argv[4]);common.atomic_json(out,results);"
 if installed:script+="run=common.Run(root,'default_runtime_integration_recheck',{});common.runtime_provenance(run,root,['rfd','boltz']);print(json.dumps({'runtime_manifest':str(run.path/'manifest.json'),'components':list(run.manifest['runtime'])}));"
 else:script+="print('EXPECTED_DEFAULT_SOURCE_REAL_THREE_RUNTIME_COLLECTORS_PASS');"
 runtime,_=command([core,"-B","-c",script,str(source/"src"),str(R),json.dumps(override["runtime_locks"],separators=(",",":")),str(out/(prefix+"_actual_runtime3.json"))],R/"source",env,out/(prefix+"_runtime3"))
 for r in q["regression_tests"]:verify(r,False)
 for r in override["runtime_locks"].values():verify(r,True)
 selector,selectorlog=command([core,"-B",q["staged_selector_test"]["path"]],R/"source",env,out/(prefix+"_staged_selector15"))
 need(re.findall(r"(?:^|\n)Ran ([0-9]+) tests?\b",selectorlog)==["15"],"Same actual staged-selector15 contracts required")
 return dict(generic_regression=generic,physical_suites=physical,physical_tests=42,staged_selector_suite=selector,staged_selector_tests=15,all_relevant_physical_contracts=57,staged_selector_suite_is_not_default_common=True,current_runtime=runtime,actual_runtime3=rec(out/(prefix+"_actual_runtime3.json")),runtime_collectors_used_actual_R=True,staged_runtime_selector_not_used=True)

def saved_contracts(r,count,sources=None,source_count=None):
 c=read(verify(r,True));need(c.get("status")=="PASS"and c.get("tests")==count and c.get("failures")==0 and c.get("errors")==0,"Exact saved software counts required")
 verify(c["log"],True)
 if sources is not None:
  need(c.get("source_files")==sources and len(sources)==source_count and len({x["path"]for x in sources})==source_count,"Whole tested source universe required")
  for x in sources:verify(x,True)
 return c
def pre_status_gate(generic):
 c=read(verify(generic["contracts"],True))
 return c.get("owned_python_compile_PASS")is True and c.get("bash_syntax_PASS")is True
SOURCE_NAMES={"source_delivery_refresh_v10.py","relative_receipt_policy.py","test_relative_receipt_policy.py","source_refresh_bootstrap.py","source_refresh_cpu.sbatch","HANDOFF.md","delivery_core.py","delivery_graph_v2.py","provenance_aliases_v2.py","native_resource_closure_v2.py","reference_source_delivery_refresh_v1.py","historical_archive_member_context.py"}
MAP_FIELDS=("relative_receipt_context_mapping","external_historical_receipt_context_mapping","current_recovered_relative_receipt_context_mapping","archive_member_receipt_context_mapping")
def source_contract_shape(source,runner,s,c,p,jid):
 need(s.get("schema")=="source-refresh-relative-software-acceptance.v10"and s.get("status")=="SOURCE_REFRESH_RELATIVE_SOFTWARE_CPU_ACCEPTED_ACTUAL_SOURCE_AUDIT_PENDING"and s.get("tests_expected")==122 and str(s.get("allocation",{}).get("job_id"))==str(jid),"Actual V10 software122 same-job identity required")
 need(c.get("status")=="PASS"and c.get("tests")==122 and c.get("failures")==c.get("errors")==0,"Actual saved V10 software122 PASS required")
 rows=p.get("source_receipts",[]);need(len(rows)==12 and {Path(x["path"]).name for x in rows}==SOURCE_NAMES and len({x["path"]for x in rows})==12 and len({str(Path(x["path"]).parent)for x in rows})==1,"Whole12 V10 tested source required")
 need(runner==sorted([x for x in rows if Path(x["path"]).suffix in {".py",".sbatch"}],key=lambda x:x["path"])and len(runner)==11,"Actual executing11 must equal tested12 minus document")
 need(s.get("compiled_all_python")is True and s.get("bash_syntax_checked")is True,"Actual V10 compilation required")
 need(source.get("historical_archive_context_parent_n")==2 and source.get("archive_member_n")==588 and source.get("current_recovered_evidence_file_n")==5 and source.get("historical_provenance_annotation_n")==9,"Four finite current/historical contexts required")
 for key in (*MAP_FIELDS,"archive_member_verification"):receipt_shape(source[key])
 return rows
def source_software(source,runner,jid):
 b=read(verify(source["software_gate_binding"],True));need(b.get("status")=="ACTUAL_SOFTWARE_GATE_BOUND_TO_SOURCE_REFRESH_V10","Actual source V10 software binding required")
 s=read(verify(b["software_acceptance"],True));c=saved_contracts(s["contracts"],122);p=read(verify(s["source_snapshot"],True))
 rows=source_contract_shape(source,runner,s,c,p,jid)
 for x in rows:verify(x,True)
 return dict(software_acceptance=b["software_acceptance"],source_files=rows)
MAPPER_NAMES={"finite_source_context.py","test_finite_source_context.py","exact_relative_bbf_context.py","test_exact_relative_bbf_context.py","context_mapper_audit_cpu.py","context_mapper_cpu.sbatch","context_consumer.py","HANDOFF.md","historical_annotation_context.py","test_historical_annotation_context.py","recovered_five_context.py","test_recovered_five_context.py","archive_member_context.py","test_archive_member_context.py"}
def source_alias_pointer_shape(source,mapper):
 fields=("finite_source_recovery_inputs_qualification","finite_source_alias_verification","finite_exact_source_alias_index")
 for name in fields:
  receipt_shape(source.get(name));need(mapper.get(name)==source[name],"Actual SourceV10/mapper finite artifact differs")
 need(source.get("exact_recovered_source_identity_n")==mapper.get("exact_recovered_source_identity_n")==8 and source.get("exact_original_source_edge_n")==mapper.get("exact_original_source_edge_n")==12,"Actual SourceV10/mapper8/12 scope required")
 return True

def mapper_binding_shape(ma,source,base,contracts):
 source_alias_pointer_shape(source,ma)
 need(ma.get("schema")=="exact-current-context-mapper-acceptance.v4"and ma.get("status")=="EXACT_BBF6_RECOVERED5_NINE_ANNOTATIONS_ARCHIVE588_AND_EIGHT_SOURCE_ALIASES_MAPPER_CPU_ACCEPTED","Actual MapperV4 content gate required")
 rows=ma.get("source_files",[]);need(len(rows)==14 and {Path(x["path"]).name for x in rows}==MAPPER_NAMES and len({x["path"]for x in rows})==14,"Actual whole14 mapper source required")
 need(contracts.get("status")=="PASS"and contracts.get("tests")==201 and contracts.get("failures")==contracts.get("errors")==0 and contracts.get("tested_source_files")==rows and contracts.get("owned_python_compile_PASS")is True and contracts.get("bash_syntax_PASS")is True,"Saved actual MapperV4 software201/source/syntax required")
 need(ma.get("base_acceptance")==base and ma.get("source_closure")==source.get("source_closure")and all(ma.get(k)==source.get(k)for k in MAP_FIELDS),"MapperV4 actual source/four-map/closure binding differs")
 return rows
def context_mapper_gate(q,source,out):
 ar=q["context_mapper_acceptance"];ma=read(verify(ar,True));contracts=read(verify(ma["contracts"],True));rows=mapper_binding_shape(ma,source,q["gates"]["source_refresh_current"]["receipt"],contracts)
 verify(contracts["log"],True);terminal(ma["allocation"]["job_id"],jobname="test9_exact_context_v4")
 copied=out/"qualified_context_mapper";copied.mkdir(exist_ok=False)
 for r in rows:
  target=copied/Path(r["path"]).name;shutil.copyfile(verify(r,True),target);target.chmod(0o444);need(fp(rec(target))==fp(r),"Qualified MapperV4 copy bytes differ")
 copied.chmod(0o555);sys.path.insert(0,str(copied))
 for name in ("exact_relative_bbf_context","historical_annotation_context","recovered_five_context","archive_member_context","finite_source_context","context_consumer"):
  spec=importlib.util.spec_from_file_location(name,copied/(name+".py"));mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
 b=sys.modules["exact_relative_bbf_context"];accepted,proof=b.verify_mapper_acceptance(ar,source[MAP_FIELDS[0]],q["gates"]["source_refresh_current"]["receipt"],source[MAP_FIELDS[1]],source[MAP_FIELDS[2]],source[MAP_FIELDS[3]])
 need(accepted==ma,"Fresh actual mapper acceptance content differs")
 for r in rows:verify(r,True)
 return dict(receipt=ar,source_files=rows,executing_copies=[rec(copied/Path(r["path"]).name)for r in rows],current_full_mapper_qualification=proof,all588_archive_bytes_reverified=True)
def physical_contracts(pre):
 c=read(verify(pre["software_contracts"],True))
 need(c.get("status")=="PASS"and c.get("tests")==57 and c.get("compiled_source")is True and c.get("bash_syntax")is True and c.get("source_manifest")==pre["source_manifest"],"Actual accepted physical57 source contracts required")
 suites=c["suites"]
 need(len(suites)==4 and {x["suite"]:x["tests"]for x in suites}=={"physical":25,"resource":9,"design":8,"staged_selector":15}and all(x["returncode"]==0 for x in suites),"Exact physical suite counts/exit required")
 for x in suites:
  verify(x["stdout"],True);verify(x["stderr"],True)
def derived_contracts(r,sources,manifest):
 c=read(verify(r,True))
 need(c.get("status")=="PASS"and c.get("owned_tests")==50 and c.get("owned_dependency_tests")==12 and c.get("source_dependency_count")==1 and c.get("compiled_named_regression_dependencies")is True and c.get("source_dependencies_readback_before_and_after_tests")is True and c.get("generic_regression_file_count")==7 and c.get("staged_physical_suite_tests")==57 and c.get("default_physical_suite_tests")==25 and c.get("models_called")is False and c.get("compiled_owned_and_derived")is True and c.get("bash_syntax")is True,"Actual structured derived50/generic7/physical57+25 contracts required")
 names={"patch_generic_design.py","test_generic_design.py","qualify_generic_design_cpu.py","generic_design_cpu.sbatch","HANDOFF.md"}
 need(len(sources)==5 and {Path(x["path"]).name for x in sources}==names and len({str(Path(x["path"]).parent)for x in sources})==1 and c.get("source_files")==sources and c.get("derived_source_manifest")==manifest,"Whole five derived source and manifest binding required")
 for x in sources:verify(x,True)
 suites=c["suites"];expected={"owned_design_validation":50,"owned_source_dependencies":12,"generic_seven":None,"staged_physical":25,"staged_resource":9,"staged_design":8,"staged_selector":15,"default_physical":25}
 need(len(suites)==8 and {x["suite"]for x in suites}==set(expected),"All exact eight derived suite rows required")
 import xml.etree.ElementTree as ET
 for x in suites:
  need(x.get("returncode")==0 and type(x.get("tests"))is int and x["tests"]>0 and all(x.get(k)==0 for k in ("failures","errors","skipped")),"Actual complete successful suite counts required")
  if expected[x["suite"]]is not None:need(x["tests"]==expected[x["suite"]],"Derived suite count differs")
  stdout=verify(x["stdout"],True);stderr=verify(x["stderr"],True)
  if x["suite"]in {"owned_design_validation","owned_source_dependencies","generic_seven"}:
   root=ET.parse(verify(x["junit"],True)).getroot();ss=list(root.iter("testsuite"))
   need(len(ss)==1 and all(int(ss[0].attrib.get(k,"0"))==x[k]for k in ("tests","failures","errors","skipped")),"Actual JUnit counts disagree with accepted suite")
  else:need(re.findall(r"(?:^|\n)Ran ([0-9]+) tests?\b",stdout.read_text()+"\n"+stderr.read_text())==[str(x["tests"])],"Actual unittest log/count mismatch")
 return c
def derived_pipeline_gate(q,ops,snapshot,pre):
 r=q["derived_pipeline_qualification"]
 # Exact qualified library V3 independently verifies real V2 eight rows, logs, named dependency and failed13303 bytes/accounting.
 proof=library_module.derived_qualification_binding({"derived_pipeline_qualification":r},q,ops)
 d=read(verify(r,True));need(d["default_runtime_locks_unchanged"]==q["original_runtime_locks"],"Derived default lock receipts differ")
 manifest=read(verify(d["derived_source_manifest"],True));generic=manifest["generic_regression_sources"]
 need(sorted([x["original"]for x in generic],key=lambda x:x["path"])==sorted(q["regression_tests"],key=lambda x:x["path"]),"Derived original same seven regression receipts differ")
 derived_contracts(d["contracts"],d["source_files"],d["derived_source_manifest"])
 return d["default_python_source_sha256_without_staged_runtime_selector"],dict(receipt=r,current_full_derived_qualification=proof,source_dependencies=d["source_dependencies"],failed_predecessor=d["failed_predecessor"],actual_CPU_accounting=terminal(d["slurm_job_id"],jobname="test9_generic_design_guard_v2"))
def allocated_cpu_tres(fields):
 tables=[]
 for key in ("AllocTRES","TRES"):
  if fields.get(key):
   vals={}
   for token in fields[key].split(","):
    need("="in token,"Malformed actual allocation TRES")
    k,v=token.split("=",1);need(k and k not in vals,"Duplicate actual allocation TRES")
    vals[k]=v
   tables.append(vals)
 need(tables,"Actual allocation TRES missing")
 need(all(x==tables[0]for x in tables),"Conflicting actual allocation TRES fields")
 vals=tables[0]
 def number(key,required=False):
  need(not required or key in vals,"Allocated CPU count absent")
  v=vals.get(key,"0");need(re.fullmatch("[0-9]+",v)is not None,"Numeric allocated CPU/GPU required")
  return int(v)
 cpus=number("cpu",True);need(cpus>=1,"Actual allocated CPU count must be positive")
 gpu=max(number("gres/gpu"),sum(number(k)for k in vals if k.startswith("gres/gpu:")))
 return cpus,gpu,vals
def current_cpu():
 need(os.environ.get("SLURM_JOB_ID","").isdigit(),"Actual CPU allocation required")
 need(os.environ.get("CUDA_VISIBLE_DEVICES")==""and os.environ.get("JAX_PLATFORMS")=="cpu"and os.environ.get("PYTHONDONTWRITEBYTECODE")=="1"and os.environ.get("PYTHONNOUSERSITE")=="1"and "PYTHONPATH"not in os.environ,"PureCPU import isolation required")
 need(all(os.environ.get(x)=="1"for x in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS")),"Serial CPU bounds required")
 jid=os.environ["SLURM_JOB_ID"];raw=subprocess.check_output(["scontrol","show","job",jid,"-o"],text=True)
 rows=[x for x in raw.splitlines()if re.search(r"\bJobId="+jid+r"(?:\s|$)",x)];need(len(rows)==1,"Unique actual allocation required")
 f=dict(re.findall(r"(\w+)=(\S+)",rows[0]));allocated_cpus,gpu,vals=allocated_cpu_tres(f)
 need(f.get("JobState")=="RUNNING"and f.get("JobName")=="test9_default_materialized_integration_v3"and f.get("UserId","").split("(")[0]=="u21111210118"and f.get("Account")=="u21111210118"and f.get("Partition")=="organ"and allocated_cpus>=1 and gpu==0,"Actual root pureCPU running allocation required")
 return dict(job_id=jid,scheduler_record=rows[0],allocated_cpus=allocated_cpus,allocated_tres=vals,allocated_gpus=0)
def full_source_guard(s):
 need(s["status"]==SOFTWARE_STATUS and s.get("tests_expected")==TESTS and s.get("compiled_all_python")is True and s.get("bash_syntax_checked")is True,"Actual integration software acceptance required")
 rows=s["source_files"];here=Path(__file__).resolve().parent;expected={str(here/n)for n in OWN}|{str(here/"library"/n)for n in LIB}
 need(len(rows)==10 and {x["path"]for x in rows}==expected,"Whole executing4+library6 source binding required")
 for x in rows:verify(x,True)
 contracts=saved_contracts(s["contracts"],TESTS)
 need(contracts.get("source_files")==rows,"Actual integration contracts must bind whole executing source10")
 return rows

def destination_path(source,name):
 need(name in PATHS,"Only exact three default destinations")
 source=Path(source);need(source.is_absolute()and source.is_relative_to(R)and source.resolve()==source and source.is_dir(),"Exact authority-local source directory required")
 p=source/name;need(p.parent.resolve()==p.parent and not p.is_symlink(),"Default destination symlink forbidden")
 return p
def current_old(source,ops):
 for name in PATHS:
  p=destination_path(source,name);old=ops[name]["old"]
  if old is None:need(not p.exists(),"Previously absent physical helper is no longer absent")
  else:need(p.is_file()and fp(rec(p))==fp(old),"Default destination no longer exact old bytes: "+name)
def atomic_bytes(p,data,mode):
 p=Path(p);temp=p.with_name(p.name+".integration-"+os.environ.get("SLURM_JOB_ID","fixture")+".tmp")
 with temp.open("xb")as f:
  f.write(data);f.flush();os.fsync(f.fileno())
 temp.chmod(mode)
 try:os.replace(temp,p)
 finally:
  if temp.exists():temp.unlink()
def archive_old(source,ops,out):
 current_old(source,ops);archives={};modes={}
 for name in PATHS:
  p=destination_path(source,name);modes[name]=(p.stat().st_mode&0o777)if p.exists()else 0o644
  if ops[name]["old"]is not None:
   dest=out/"old_default_exact_history"/name;dest.parent.mkdir(parents=True,exist_ok=True)
   with dest.open("xb")as f:f.write(p.read_bytes())
   need(fp(rec(dest))==fp(ops[name]["old"]),"Archived old bytes differ");dest.chmod(0o444);archives[name]=rec(dest)
 return archives,modes
def rollback(source,ops,archives,modes,out,reason):
 restored=[];blocked=[]
 for name in reversed((PATHS[1],PATHS[2],PATHS[0])):
  p=destination_path(source,name);old=ops[name]["old"]
  if not p.exists():
   if old is None:continue
   blocked.append(dict(repository_relative=name,reason="MISSING_UNEXPECTED_OLD_DESTINATION"));continue
  actual=rec(p)
  if old is not None and fp(actual)==fp(old):continue
  if fp(actual)!=fp(ops[name]["new"]):
   blocked.append(dict(repository_relative=name,reason="UNKNOWN_CONCURRENT_BYTES_RETAINED",current=actual));continue
  if old is None:p.unlink()
  else:
   archive=verify(archives[name],True)
   atomic_bytes(p,archive.read_bytes(),modes[name])
   need(fp(rec(p))==fp(old),"Rollback old exact bytes failed")
  restored.append(name)
 receipt=dump(out/"rollback.json",dict(schema="default-materialized-rollback.v2",status="EXACT_OWNED_BYTES_ROLLED_BACK"if not blocked else"ROLLBACK_INCOMPLETE_UNKNOWN_BYTES_NOT_OVERWRITTEN",reason=reason,restored_paths=restored,blocked=blocked))
 need(not blocked,"Rollback incomplete: unknown concurrent bytes retained")
 current_old(source,ops)
 return receipt
def install(source,ops,out,after=None,finalize=None):
 archives,modes=archive_old(source,ops,out)
 journal=dump(out/"transaction_journal.json",dict(schema="default-materialized-three-path-transaction.v2",paths=list(PATHS),operations=[ops[n]for n in PATHS],archives=archives,old_modes=modes,install_order=[PATHS[1],PATHS[2],PATHS[0]],rollback_on_postcheck_failure=True))
 installed=[]
 try:
  for name in (PATHS[1],PATHS[2],PATHS[0]):
   p=destination_path(source,name);old=ops[name]["old"]
   if old is None:need(not p.exists(),"Unexpected concurrent helper creation")
   else:need(p.is_file()and fp(rec(p))==fp(old),"Concurrent default change before replacement")
   new=verify(ops[name]["new"],True)
   atomic_bytes(p,new.read_bytes(),modes[name])
   need(fp(rec(p))==fp(ops[name]["new"]),"Exact replacement readback differs")
   installed.append(name)
  post=after()if after is not None else{}
  result=dict(old_pipeline_archive=archives[PATHS[0]],old_rfd_lock_archive=archives[PATHS[2]],new_default_files=[rec(destination_path(source,n))for n in PATHS],replaced_paths=list(PATHS),transaction_journal=journal,postchecks=post,old_modes=modes)
  if finalize is not None:finalize(result)
  return result
 except Exception as error:
  try:rollback_receipt=rollback(source,ops,archives,modes,out,str(error))
  except Exception as failure:
   dump(out/"rollback_failure.json",dict(status="ROLLBACK_FAILED_OR_INCOMPLETE",original_error=str(error),rollback_error=str(failure),installed_paths=installed))
   raise RuntimeError("Transaction/postcheck failed; rollback incomplete, see durable rollback receipts")from error
  dump(out/"transaction_failure.json",dict(status="TRANSACTION_FAILED_EXACT_OLD_BYTES_RESTORED",error=str(error),installed_paths=installed,rollback=rollback_receipt))
  raise
def unchanged_nonoperations(q,snapshot):
 verify(snapshot["staged_runtime_selector"]["default_common_unchanged"],False)
 for c in ("core","boltz"):verify(q["original_runtime_locks"][c],False)
 for r in q["regression_tests"]:verify(r,False)
def software(library_path,out,freeze):
 allocation=current_cpu();here=Path(__file__).resolve().parent
 need(not(here.stat().st_mode&0o222),"Prepared reviewed source must be readonly")
 own=[raw_rec(boot_path(here/n))for n in OWN]
 libp=boot_path(library_path);librec=raw_rec(libp);libobj=json.loads(libp.read_text());need(raw_rec(libp)==librec,"Library gate drift")
 need(libobj.get("status")=="FINAL_SOURCE_MATERIALIZED_ARCHIVE_CONTEXT_AND_DERIVED_V2_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_INTEGRATION","Actual standalone library CPU acceptance required")
 librows=libobj["source_files"];need(len(librows)==6 and{Path(x["path"]).name for x in librows}==set(LIB),"Actual whole library6 required")
 for r in librows:boot_verify(r)
 frozen=Path(freeze);need(frozen.is_absolute()and frozen.is_relative_to(R)and frozen.resolve()==frozen and not frozen.exists(),"Fresh exact software snapshot required")
 frozen.mkdir(parents=True)
 for r in own:shutil.copyfile(boot_verify(r),frozen/Path(r["path"]).name)
 (frozen/"library").mkdir()
 for r in librows:shutil.copyfile(boot_verify(r),frozen/"library"/Path(r["path"]).name)
 for p in frozen.rglob("*"):
  if p.is_file():p.chmod(0o444)
 (frozen/"library").chmod(0o555);frozen.chmod(0o555)
 # Execute the byte-identical accepted-copy entry, not prepared source, for all software contracts.
 argv=[str(R/"env/core/bin/python"),"-B",str(frozen/OWN[0]),"software_frozen","--library-acceptance",str(libp),"--out",str(out)]
 env={**os.environ,"DEFAULT_INTEGRATION_ORIGINAL_SOURCE_JSON":json.dumps(own,separators=(",",":"))}
 result=subprocess.run(argv,env=env)
 need(result.returncode==0,"Frozen integration software CPU failed")
def software_frozen(library_path,out):
 allocation=current_cpu();lib=bind_library(library_path);cpu()
 out=safe_path(out);out.mkdir(parents=True,exist_ok=False);sources=source_bindings()
 originals=json.loads(os.environ["DEFAULT_INTEGRATION_ORIGINAL_SOURCE_JSON"])
 need(len(originals)==4 and{Path(x["path"]).name for x in originals}==set(OWN),"Exact prepared reviewed source receipts required")
 for r in originals:
  boot_verify(r);copy=next(x for x in sources if Path(x["path"]).name==Path(r["path"]).name and Path(x["path"]).parent==Path(__file__).resolve().parent)
  need(fp(copy)==fp(r),"Prepared/frozen integration source byte drift")
 for r in sources:
  p=Path(r["path"])
  if p.suffix==".py":compile(p.read_bytes(),str(p),"exec",dont_inherit=True)
  if p.suffix==".sbatch":subprocess.run(["bash","-n",str(p)],check=True)
 import test_integrate_default_workflow_v3 as fixtures
 fixtures.m=sys.modules[__name__]
 suite=unittest.defaultTestLoader.loadTestsFromModule(fixtures);need(suite.countTestCases()==TESTS,"Exact declared integration fixture count required")
 with(out/"contracts.txt").open("x")as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
 contracts=dump(out/"contracts.json",dict(status="PASS"if result.wasSuccessful()else"FAIL",tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),log=rec(out/"contracts.txt"),source_files=sources))
 need(result.wasSuccessful(),"Three-path integration software contracts failed")
 result=dict(schema="default-materialized-integration-software-acceptance.v2",status=SOFTWARE_STATUS,source_files=sources,original_source_files=originals,library_software_binding=lib,contracts=contracts,allocation=allocation,tests_expected=TESTS,compiled_all_python=True,bash_syntax_checked=True,default_written=False,science_accepted=False,models_recomputed=False,GPU_submitted=False,ACTIVE_changed=False)
 dump(out/"acceptance.json",result)
 for p in out.iterdir():p.chmod(0o444)
 out.chmod(0o555)
 print(result["status"])
def release_lock(path,content,created):
 if created and path is not None and path.exists()and path.read_bytes()==content:path.unlink()
def apply(request_path,software_path,library_path,out):
 allocation=current_cpu();lib=bind_library(library_path);cpu()
 s=read(boot_path(software_path));srec=rec(software_path);sources=full_source_guard(s)
 terminal(s["allocation"]["job_id"],jobname="test9_default_materialized_integration_v3")
 need(s["library_software_binding"]["receipt"]==rec(library_path)and s["library_software_binding"]["source_files"]==lib["source_files"],"Actual tested library prerequisite changed")
 request_receipt=rec(boot_path(request_path));q=read(request_path)
 need(rec(request_path)==request_receipt,"Root request changed during read")
 ops=operation_plan(q);source=R/"source";out=safe_path(out);out.mkdir(parents=True,exist_ok=False)
 stage="prerequisites";lock=None;lock_bytes=None;lock_created=False
 try:
  old_history=history();objects,gates,override,snapshot,base,records=prerequisites(q,ops,out)
  need(tree_sha(source)==BASE,"Current C3 tree changed")
  current_old(source,ops);unchanged_nonoperations(q,snapshot)
  for r in sources:verify(r,True)
  clone,clone_manifest=expected_default(q,ops,snapshot,base,out,override)
  stage="isolated_expected_default_full_checks"
  prechecks=checks(clone,q,override,out,"expected_default",False)
  need(tree_sha(clone)==q["expected_new_tree_sha256"],"Expected default clone changed during qualification")
  need(tree_sha(source)==BASE,"Default C3 changed during isolated qualification")
  current_old(source,ops);unchanged_nonoperations(q,snapshot)
  # One fixed controller lock, outside default source. No stale lock is silently removed.
  lock=R/"steps/24_benchmark_delivery/runs/default_materialized_integration_exclusive.lock"
  lock_bytes=json.dumps(dict(job_id=allocation["job_id"],request=request_receipt)).encode()
  with lock.open("xb")as f:f.write(lock_bytes);f.flush();os.fsync(f.fileno())
  lock_created=True
  stage="exact_three_path_install_and_postchecks"
  def postcheck():
   need(tree_sha(source)==q["expected_new_tree_sha256"],"Installed full default tree identity differs")
   unchanged_nonoperations(q,snapshot)
   result=checks(source,q,override,out,"installed_default",True)
   need(tree_sha(source)==q["expected_new_tree_sha256"],"Installed source drifted during checks")
   unchanged_nonoperations(q,snapshot)
   for r in sources:verify(r,True)
   need(rec(request_path)==request_receipt,"Root request drifted")
   return result
  def finalize(replacement):
   result=dict(schema="default-materialized-generic-integration-acceptance.v2",status=STATUS,request=request_receipt,source_manifest=q["source_manifest"],software_acceptance=srec,library_software_binding=lib,source_files=[r for r in sources if Path(r["path"]).parent==Path(__file__).resolve().parent],executed_library_sources=[r for r in sources if Path(r["path"]).parent==Path(__file__).resolve().parent/"library"],allocation=allocation,slurm_job_id=allocation["job_id"],old_tree_sha256=BASE,new_tree_sha256=tree_sha(source),expected_default_manifest=clone_manifest,expected_default_checks=prechecks,replacement=replacement,accepted_prerequisites=gates,original_failure_history=old_history,derived_pipeline_qualification=q.get("derived_pipeline_qualification"),original_common_preserved=snapshot["staged_runtime_selector"]["default_common_unchanged"],installed_runtime_locks={c:rec(source/"environment"/("runtime-lock-"+c+".json"))for c in ("core","rfd","boltz")},staged_common_never_installed=True,three_actual_runtime_components_verified=True,formal_sources_changed=False,models_recomputed=False,GPU_submitted=False,Git_changed=False,ACTIVE_changed=False,experimental_binding=False,experimental_blockade=False)
   for p in out.iterdir():
    if p.is_file():p.chmod(0o444)
   dump(out/"acceptance.json",result);(out/"acceptance.json").chmod(0o444)
  replacement=install(source,ops,out,postcheck,finalize)
  print(STATUS)
 except Exception as error:
  dump(out/"typed_incomplete.json",dict(schema="default-materialized-integration-incomplete.v2",status="DEFAULT_MATERIALIZED_INTEGRATION_INCOMPLETE_NOT_PUBLISHED",failed_stage=stage,error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc(),request=request_receipt,software_acceptance=srec,allocation=allocation,default_may_have_changed=stage=="exact_three_path_install_and_postchecks",rollback_receipt=(rec(out/"rollback.json")if(out/"rollback.json").exists()else None),rollback_failed=(out/"rollback_failure.json").exists(),Git_changed=False,ACTIVE_changed=False,GPU_submitted=False))
  raise
 finally:
  release_lock(lock,lock_bytes,lock_created)
def dispatch(software_path,request_path,library_path,out):
 current_cpu();s=json.loads(boot_path(software_path).read_text());need(s.get("status")==SOFTWARE_STATUS,"Actual integration software gate required")
 rows=s["source_files"];entry=[x for x in rows if Path(x["path"]).name==OWN[0]]
 need(len(entry)==1,"One accepted frozen integration entry required");boot_verify(entry[0])
 originals=s["original_source_files"];need(len(originals)==4,"Original dispatcher source receipt absent")
 for r in originals:boot_verify(r)
 own_entry=next(x for x in originals if Path(x["path"]).name==OWN[0])
 need(own_entry==raw_rec(Path(__file__).resolve()),"Executing dispatcher differs from tested original")
 os.execv(str(R/"env/core/bin/python"),[str(R/"env/core/bin/python"),"-B",entry[0]["path"],"apply","--request",str(request_path),"--software-acceptance",str(software_path),"--library-acceptance",str(library_path),"--out",str(out)])
def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest="mode",required=True)
 for name in ("software","software_frozen","apply","dispatch"):
  x=sub.add_parser(name);x.add_argument("--library-acceptance",required=True);x.add_argument("--out",required=True)
  if name=="software":x.add_argument("--freeze",required=True)
  if name in {"apply","dispatch"}:x.add_argument("--request",required=True);x.add_argument("--software-acceptance",required=True)
 a=p.parse_args()
 if a.mode=="software":software(a.library_acceptance,a.out,a.freeze)
 elif a.mode=="software_frozen":software_frozen(a.library_acceptance,a.out)
 elif a.mode=="dispatch":dispatch(a.software_acceptance,a.request,a.library_acceptance,a.out)
 else:apply(a.request,a.software_acceptance,a.library_acceptance,a.out)
if __name__=="__main__":main()
