#!/usr/bin/env python3
"""Exact successor source closure; CPU only, no model calls or release promotion.

Consume an accepted immutable base inclusion plus explicit accepted new modules.
Never enumerate live source directories, infer "latest", or copy inference assets.
"""
import argparse,collections,hashlib,json,os,re,shutil,subprocess,sys,unittest
from pathlib import Path

R=Path("/lustre/users/u21111210118/projects/test9")
SOURCE_EXT={".py",".sh",".sbatch"}
PUBLIC_TEXT_EXT=SOURCE_EXT|{".md",".json",".yaml",".yml",".toml"}
RECEIPT_TEXT_EXT=PUBLIC_TEXT_EXT|{".txt"}
REQUIRED_MODULES={
 "formal13260_terminal_v3","native74_cache_catalog","native74_cache_binding",
 "reference_free_e2e","formal_common_review","independent_statistics",
 "scientific_report","final_delivery_tools","default_workflow_integration",
}
MODULE_GATE_STATUS={
 "formal13260_terminal_v3":{"FORMAL13260_TERMINAL_V2_COLLECTION_CPU_ACCEPTED_ROOT_COMMON_PREPARATION_PENDING"},
 "native74_cache_catalog":{"CPU_CACHE_GUARD_CATALOG_COMPLETE"},
 "native74_cache_binding":{"CPU_CACHE_GUARD_BIND_COMPLETE"},
 "default_workflow_integration":{"DEFAULT_GENERIC_PHYSICAL_GATE_AND_MATERIALIZED_RUNTIME_INTEGRATION_CPU_VERIFIED_NOT_PUBLISHED"},
 "formal_common_review":{"FORMAL_COMMON_RAW_CONTENT_INDEPENDENT_AND112_ACCEPTED_COMPUTATIONAL_ONLY"},
 "independent_statistics":{"INDEPENDENT_FORMAL112_FAIRNESS_AND_STATISTICS_AUDIT_PASS"},
 "scientific_report":{"FORMAL13260_FINAL_CHINESE_REPORT_AND_MATRIX_CPU_ACCEPTED"},
 "final_delivery_tools":{"FINAL_DELIVERY_COMPOSER_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_ARCHIVE_ACCEPTANCE"},
 "reference_free_e2e":{"CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED","REFERENCE_FREE_E2E_COMPUTATIONAL_CHAIN_CONTENT_ACCEPTED"},
}
# Final source closure does not independently certify scientific endpoints.
SECRET_RE=re.compile(r"(?im)(?:password|access_token|secret_key|api_key|private_key)\s*[:=]\s*[\"']?(?!None\b|null\b|os\.|env\b|\$\{|<|YOUR_|getenv\b)[A-Za-z0-9+/=_-]{12,}")
METADATA_ONLY={"exact-resource-aliases.v2","native-resource-closure.v2","benchmark-source-receipt-closure.v1"}
PACKAGE_NAMES=("final_source_closure.py","test_final_source_closure.py","final_source_cpu.sbatch","HANDOFF.md","FINAL_SOURCE_CHECKLIST.md","final_source_context_adapter.py")
SOURCE_CONTRACTS=53
REGRESSION_NAMES={"test_development_regressions.py","test_audit_regressions.py","test_benchmark.py","test_construct_contract.py","test_scientific_contracts.py","test_runtime_registration.py","test_af2_review.py"}
REGRESSION7=REGRESSION_NAMES
INTEGRATION_NAMES={"integrate_default_workflow_v3.py","test_integrate_default_workflow_v3.py","default_integration_cpu_v3.sbatch","HANDOFF.md"}
SOFTWARE_STATUS="FINAL_SOURCE_MATERIALIZED_ARCHIVE_CONTEXT_AND_DERIVED_V2_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_INTEGRATION"
def need(v,msg):
 if not v:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text())
def metadata_only(obj):
 marker=obj.get("schema")if isinstance(obj,dict)else None
 return isinstance(marker,str)and marker in METADATA_ONLY
def key(r):return r["path"],r["sha256"],r["bytes"]
def fp(r):return r["bytes"],r["sha256"]
def receipt_shape(r):
 need(isinstance(r,dict)and {"path","sha256","bytes"}<=r.keys(),"Exact path/bytes/SHA receipt required")
 need(isinstance(r["path"],str)and Path(r["path"]).is_absolute(),"Absolute receipt path required")
 need(isinstance(r["bytes"],int)and not isinstance(r["bytes"],bool)and r["bytes"]>=0,"Integer nonnegative byte count required")
 need(isinstance(r["sha256"],str)and re.fullmatch("[0-9a-f]{64}",r["sha256"])is not None,"Exact SHA256 required")
 return r
def rec(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open("rb")as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b);n+=len(b)
 return dict(path=str(p),bytes=n,sha256=h.hexdigest())
def safe_path(p):
 p=Path(p);need(p.is_absolute()and p.is_relative_to(R),"Receipt outside authority")
 need(not p.is_symlink()and p.resolve()==p,"Symlink components forbidden")
 return p
def verify(r,readonly=False):
 receipt_shape(r);p=safe_path(r["path"])
 need(p.is_file(),"Required exact bytes unavailable: "+str(p))
 need(fp(rec(p))==fp(r),"Required exact bytes changed: "+str(p))
 need(not readonly or not(p.stat().st_mode&0o222),"Readonly frozen source required")
 return p
def dump(p,o):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("x")as f:json.dump(o,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
 p.chmod(0o444);return rec(p)
def cpu():
 need(os.environ.get("SLURM_JOB_ID","").isdigit()and os.environ.get("CUDA_VISIBLE_DEVICES")=="","Actual pureCPU Slurm allocation/empty CUDA mask required")
 need(os.environ.get("JAX_PLATFORMS")=="cpu"and os.environ.get("PYTHONNOUSERSITE")=="1"and os.environ.get("PYTHONDONTWRITEBYTECODE")=="1"and "PYTHONPATH"not in os.environ and os.environ.get("OPENBLAS_NUM_THREADS")=="1","Readonly/import/CPU thread isolation required")
 jid=os.environ["SLURM_JOB_ID"]
 raw=subprocess.check_output(["sacct","-X","-j",jid,"--noheader","--parsable2","--format=JobIDRaw,State,AllocTRES,User%64,Account%64,Partition%64"],text=True)
 rows=[x.split("|")for x in raw.splitlines()if x.split("|",1)[0]==jid]
 need(len(rows)==1 and len(rows[0])>=6 and rows[0][1]=="RUNNING"and rows[0][3:6]==["u21111210118","u21111210118","organ"],"Unique actual CPU owner/account/partition required")
 vals=dict(t.split("=",1)for t in rows[0][2].split(",")if "="in t)
 def n(k):
  v=vals.get(k,"0");need(re.fullmatch("[0-9]+",v),"Numeric actual allocated CPU TRES required");return int(v)
 need(n("cpu")>=1 and max(n("gres/gpu"),sum(n(k)for k in vals if k.startswith("gres/gpu:")))==0,"Actual CPU>=1/GPU0 required")
 return dict(job_id=jid,scheduler_record=raw,numeric_sacct_row=rows[0],allocated_CPUs=n("cpu"),allocated_gpus=0)
def terminal_cpu(jid,expected_name,expected_state="COMPLETED",expected_exit="0:0"):
 need(isinstance(jid,str)and jid.isdigit(),"Exact prerequisite CPU job identity required")
 raw=subprocess.check_output(["sacct","-X","-j",jid,"--noheader","--parsable2","--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocTRES,User%64,Account%64,JobName%100,Partition%64"],text=True)
 rows=[x.split("|")for x in raw.splitlines()if x.split("|",1)[0]==jid]
 need(len(rows)==1 and len(rows[0])>=9,"Unique terminal CPU prerequisite required")
 job,state,exitcode,elapsed,tres,user,account,name,partition=rows[0][:9];vals=dict(t.split("=",1)for t in tres.split(",")if "="in t)
 def n(k):
  v=vals.get(k,"0");need(re.fullmatch("[0-9]+",v),"Numeric terminal CPU TRES required");return int(v)
 need(state==expected_state and exitcode==expected_exit and elapsed.isdigit()and user==account=="u21111210118"and name==expected_name and partition=="organ"and n("cpu")>=1 and max(n("gres/gpu"),sum(n(k)for k in vals if k.startswith("gres/gpu:")))==0,"Actual terminal COMPLETED0 CPU/GPU0 owner/name required")
 return dict(raw=raw,row=rows[0],job_id=jid,state=state,exit_code=exitcode,allocated_CPUs=n("cpu"),allocated_GPUs=0,elapsed_seconds=int(elapsed))
def tree_sha(source):
 files=sorted((Path(source)/"src").rglob("*.py"))
 return hashlib.sha256("".join(str(p.relative_to(source))+rec(p)["sha256"]for p in files).encode()).hexdigest()
def collect(source,locks,old_manifest):
 sys.path.insert(0,str(Path(source)/"src"))
 from ppiblocker import common
 old=common.load_run(old_manifest,{"POSE_ACCEPTED"})
 for component,r in locks.items():
  verify(r);need(common.collect_runtime(R,component)==read(r["path"]),"Actual reviewed runtime drift: "+component)
 return dict(old_prediction_manifest=rec(old_manifest),runtime_locks=locks,old_source_sha256=old["source"]["python_source_sha256"])
def receipt_edges(o,trail=()):
 if isinstance(o,dict):
  if {"path","sha256","bytes"}<=o.keys()and isinstance(o["path"],str):
   yield receipt_shape(o),trail
  for k,v in o.items():yield from receipt_edges(v,trail+(str(k),))
 elif isinstance(o,list):
  for i,v in enumerate(o):yield from receipt_edges(v,trail+(str(i),))
def conditional(p):
 parts=Path(p).parts
 return "env"in parts or any(x in parts for x in ("colabfold","boltz","mmseqs","rfdiffusion","bindcraft"))and "assets"in parts
def destination(d):
 p=Path(d)
 need(not p.is_absolute()and str(p)not in ("",".")and ".."not in p.parts and ".git"not in p.parts,"Unsafe repository destination")
 return p.as_posix()
def kind(p):
 p=Path(p)
 return "TEST"if p.name.startswith("test_")else "IMPLEMENTATION"if p.suffix==".py"else "CONFIGURATION_OR_LAUNCHER"if p.suffix in {".json",".yaml",".yml",".toml",".sh",".sbatch"}else "DOCUMENT"
def eligible_public(r,d):
 receipt_shape(r);d=destination(d);p=Path(r["path"])
 need(p.suffix in PUBLIC_TEXT_EXT,"Only declared public text sources/config/documents allowed")
 need(not conditional(p),"Conditional inference asset is not public source")
 need(not any(x in p.parts for x in (".git","site-packages","weights","params")),"Private/runtime tree is not public source")
 need(not any(x in p.name.lower()for x in ("id_ed25519","credential")),"Credential/licensed software asset excluded")
 return d
def module_plan(plan):
 need(plan.get("schema")=="final-source-closure-plan.v3","Wrong explicit closure plan schema")
 need(plan.get("root_owned")is True and plan.get("formal_array_job_id")=="13260","Root plan must bind actual13260")
 modules=plan.get("modules");need(isinstance(modules,list),"Explicit accepted modules required")
 roles=[m.get("role")for m in modules]
 need(len(roles)==len(set(roles))and set(roles)==REQUIRED_MODULES,"All nine exact final module roles required")
 need(plan.get("public_source_only")is True and plan.get("no_scientific_settings_change")is True,"Source-only scope required")
 need(plan.get("root_integration_review",{}).get("new_generic_source_promotion_reviewed")is True,
      "Root must explicitly review integration of corrected generic source; isolated version alone is not product integration")
 for m in modules:
  need(isinstance(m.get("gate"),dict)and isinstance(m["gate"].get("expected_status"),str)and m["gate"]["expected_status"],"Explicit module terminal status required")
  receipt_shape(m["gate"]["receipt"])
  if m["role"]in MODULE_GATE_STATUS:
   need(m["gate"]["expected_status"]in MODULE_GATE_STATUS[m["role"]],"Unexpected current module terminal status")
  need(isinstance(m.get("sources"),list)and len(m["sources"])>0,"Every operative module needs exact source entries, including reused source")
  need(isinstance(m.get("seeds",[]),list),"Explicit source snapshot/receipt seeds required")
  for s in m["sources"]:eligible_public(s["receipt"],s["repository_relative"])
  if m["role"]=="default_workflow_integration":
   ds={s["repository_relative"]for s in m["sources"]}
   need({"src/ppiblocker/pipeline.py","src/ppiblocker/pose_physical_gate.py","environment/runtime-lock-rfd.json"}<=ds,"Default CLI must publish both exact integrated physical-gate paths")
 return modules
DERIVED_NAMES={"patch_generic_design.py","test_generic_design.py","qualify_generic_design_cpu.py","generic_design_cpu.sbatch","HANDOFF.md"}
def derived_dependency_shape(d,c,m):
 rows=d.get("source_dependencies")
 need(isinstance(rows,list)and len(rows)==1 and c.get("source_dependencies")==rows and m.get("source_dependencies")==rows,"Actual same named regression dependency must bind qualification/contracts/manifest")
 dep=rows[0];need(dep.get("relative_path")=="scripts/register_runtime_locks.py"and dep.get("role")=="UNCHANGED_GENERIC_RUNTIME_REGISTRATION_TEST_IMPORT_DEPENDENCY","Unknown derived regression dependency")
 for key in ("original","frozen"):receipt_shape(dep[key])
 need(dep["original"]["path"]==str(R/"source/scripts/register_runtime_locks.py")and fp(dep["original"])==fp(dep["frozen"]),"Derived dependency original path/byte identity differs")
 need(dep["frozen"]["path"]==str(Path(d["derived_source_manifest"]["path"]).parent/"scripts/register_runtime_locks.py"),"Derived dependency exact tested sibling path differs")
 old=d.get("failed_predecessor");need(old==m.get("failed_predecessor")and isinstance(old,dict)and old.get("schema")=="generic-design-qualification-failed-v1-history.v1"and old.get("status")=="ACTUAL_FAILED13303_V1_PRESERVED_NOT_QUALIFIED"and old.get("repair_identity_is_distinct")is True and old.get("old_acceptance_used")is False,"Actual failed13303 V1 history must remain distinct")
 receipt_shape(old["incomplete"]);numeric=old.get("terminal_numeric_accounting",{})
 need(numeric.get("job_id")=="13303"and numeric.get("state")=="FAILED"and numeric.get("exit_code")=="1:0"and type(numeric.get("allocated_CPUs"))is int and numeric["allocated_CPUs"]>=1 and type(numeric.get("allocated_GPUs"))is int and numeric["allocated_GPUs"]==0,"Actual failed13303 numeric CPU/GPU0 history required")
 return dep
def derived_contract_shape(d,c,m,request,ops,snapshot):
 need(d.get("schema")=="generic-design-input-empty-pool-qualification.v2"and d.get("status")=="GENERIC_DESIGN_INPUT_AND_NONEMPTY_POOL_WITH_REGRESSION_DEPENDENCY_V2_CPU_ACCEPTED","Actual mandatory derived input/pool pipeline qualification required")
 need(request.get("derived_pipeline_qualification")is not None,"Final workflow requires actually qualified input/pool repair")
 need(d.get("parent_source_manifest")==request.get("source_manifest")and d.get("parent_physical_preflight")==request.get("gates",{}).get("physical_preflight_v3_current",{}).get("receipt"),"Derived exact physical parent chain differs")
 original=next(x["source"]for x in snapshot["default_promotion_files"]if x["repository_relative"]=="src/ppiblocker/pipeline.py")
 helper=next(x["source"]for x in snapshot["default_promotion_files"]if x["repository_relative"]=="src/ppiblocker/pose_physical_gate.py")
 need(d.get("original_physical_pipeline")==original and d.get("derived_pipeline")==ops["src/ppiblocker/pipeline.py"]["new"]and d.get("physical_helper_unchanged")==helper,"Only exact derived pipeline may supersede physical promotion")
 need(ops["src/ppiblocker/pose_physical_gate.py"]["new"]==helper and d.get("default_common_original")==snapshot["staged_runtime_selector"]["original_common"]and fp(d["staged_common_unchanged"])==fp(snapshot["staged_runtime_selector"]["staged_common"]),"Original common and physical helper identities must remain exact")
 need(d.get("default_python_source_sha256_without_staged_runtime_selector")==request.get("expected_new_tree_sha256")and d.get("staged_python_source_sha256")!=request.get("expected_new_tree_sha256"),"Accepted derived staged/default tree identities differ")
 need(d.get("default_source_unchanged")is True and d.get("model_inference_performed")is False and d.get("formal_benchmark_mutated")is False and d.get("experimental_binding")is False and d.get("experimental_blockade")is False and d.get("source_staged")is False,"Derived qualification has only software scope")
 sources=d.get("source_files",[])
 need(len(sources)==5 and {Path(r["path"]).name for r in sources}==DERIVED_NAMES and len({r["path"]for r in sources})==5,"Exact whole derived qualification source5 required")
 need(c.get("status")=="PASS"and c.get("source_files")==sources and c.get("derived_source_manifest")==d.get("derived_source_manifest")and c.get("owned_tests")==50 and c.get("owned_dependency_tests")==12 and c.get("source_dependency_count")==1 and c.get("compiled_named_regression_dependencies")is True and c.get("source_dependencies_readback_before_and_after_tests")is True and c.get("generic_regression_file_count")==7 and c.get("staged_physical_suite_tests")==57 and c.get("default_physical_suite_tests")==25 and c.get("models_called")is False and c.get("compiled_owned_and_derived")is True and c.get("bash_syntax")is True,"Saved actual eight-suite design qualification contract required")
 suites=c.get("suites",[]);expected={"owned_design_validation":50,"owned_source_dependencies":12,"generic_seven":None,"staged_physical":25,"staged_resource":9,"staged_design":8,"staged_selector":15,"default_physical":25}
 need(len(suites)==8 and {x.get("suite")for x in suites}==set(expected),"Eight exact distinct derived suite rows required")
 for row in suites:
  count=row.get("tests");need(type(count)is int and count>0 and (expected[row["suite"]]is None or count==expected[row["suite"]])and row.get("returncode")==0 and row.get("failures")==row.get("errors")==row.get("skipped")==0,"Actual derived suite failed/empty/count differs")
  receipt_shape(row["stdout"]);receipt_shape(row["stderr"])
  need(isinstance(row.get("argv"),list)and row["argv"],"Exact executed suite argv required")
  if row["suite"]in {"owned_design_validation","owned_source_dependencies","generic_seven"}:receipt_shape(row["junit"])
 need(m.get("schema")=="generic-design-derived-source.v2"and all(m.get(k)==d.get(k)for k in ("parent_physical_preflight","parent_source_manifest","original_physical_pipeline","derived_pipeline","source_files","staged_python_source_sha256","default_python_source_sha256_without_staged_runtime_selector","physical_helper_unchanged","default_common_original"))and m.get("staged_common")==d.get("staged_common_unchanged")and m.get("formal28_112_empty_null_semantics_changed")is False,"Actual qualified derived manifest identity differs")
 derived_dependency_shape(d,c,m)
 need(len(m.get("generic_regression_sources",[]))==7 and {Path(x["original"]["path"]).name for x in m["generic_regression_sources"]}==set(REGRESSION7),"Same seven actual generic regression identities required")
 for key in ("staged_source_files","default_candidate_source_files"):
  rows=m.get(key,[]);need(rows and len({r["path"]for r in rows})==len(rows),"Full derived staged/default source inventory required")
  pipeline=next((r for r in rows if r["path"].endswith("/src/ppiblocker/pipeline.py")),None)
  common=next((r for r in rows if r["path"].endswith("/src/ppiblocker/common.py")),None)
  helper_row=next((r for r in rows if r["path"].endswith("/src/ppiblocker/pose_physical_gate.py")),None)
  need(pipeline is not None and common is not None and helper_row is not None and fp(pipeline)==fp(d["derived_pipeline"])and fp(helper_row)==fp(helper),"Full derived source inventory differs from qualified promotion")
  expected_common=d["staged_common_unchanged"]if key=="staged_source_files"else d["default_common_original"]
  need(fp(common)==fp(expected_common),"Derived common selector identity differs")
 return suites
def derived_qualification_binding(obj,request,ops):
 ar=request.get("derived_pipeline_qualification");need(ar is not None and obj.get("derived_pipeline_qualification")==ar,"Final integration must retain mandatory actual derived qualification")
 d=read(verify(ar,True));c=read(verify(d["contracts"],True));m=read(verify(d["derived_source_manifest"],True));snapshot=read(verify(request["source_manifest"],True))
 suites=derived_contract_shape(d,c,m,request,ops,snapshot)
 need(d["allocation"]["job_id"]==d["slurm_job_id"],"Derived actual CPU allocation fork")
 accounting=terminal_cpu(d["slurm_job_id"],"test9_generic_design_guard_v2")
 for key in ("source_files","staged_source_files","default_candidate_source_files"):
  for rr in (d["source_files"]if key=="source_files"else m[key]):verify(rr,True)
 for rr in (d["physical_helper_unchanged"],d["default_common_original"],d["staged_common_unchanged"],d["derived_pipeline"]):verify(rr,True)
 for pair in m["generic_regression_sources"]:verify(pair["original"]);verify(pair["frozen"],True)
 dependency=derived_dependency_shape(d,c,m);verify(dependency["original"]);verify(dependency["frozen"],True)
 named=Path(dependency["frozen"]["path"]).parent;need(not(named.stat().st_mode&0o222)and {p.name for p in named.iterdir()}=={"register_runtime_locks.py"},"Actual readonly one-helper dependency universe differs")
 verify(d["failed_predecessor"]["incomplete"],True)
 actual_failed=terminal_cpu("13303","test9_generic_design_guard_v1","FAILED","1:0")
 numeric=d["failed_predecessor"]["terminal_numeric_accounting"];need(numeric.get("row")==actual_failed["row"]and numeric.get("raw")==actual_failed["raw"],"Failed13303 saved actual terminal accounting fork")
 failed=read(d["failed_predecessor"]["incomplete"]["path"]);need(failed.get("schema")=="generic-design-input-empty-pool-incomplete.v1"and failed.get("status")=="GENERIC_DESIGN_DERIVED_PIPELINE_NOT_QUALIFIED"and failed.get("allocation",{}).get("job_id")=="13303"and failed.get("model_inference_performed")is False and failed.get("default_mutated")is False and failed.get("formal_benchmark_mutated")is False and failed.get("failed_stage")=="actual_50_owned_generic7_and_physical_suites","Actual failed13303 incomplete bytes differ")
 compile(verify(dependency["frozen"],True).read_bytes(),dependency["frozen"]["path"],"exec",dont_inherit=True)
 for row in suites:
  for key in ("stdout","stderr"):verify(row[key],True)
  if row["suite"]in {"owned_design_validation","owned_source_dependencies","generic_seven"}:
   import xml.etree.ElementTree as ET
   root=ET.parse(verify(row["junit"],True)).getroot();actual=list(root.iter("testsuite"))
   need(len(actual)==1 and all(int(actual[0].attrib.get(k,"0"))==row[k]for k in ("tests","failures","errors","skipped")),"Actual saved JUnit counts differ")
  else:
   raw=Path(row["stdout"]["path"]).read_text()+"\n"+Path(row["stderr"]["path"]).read_text()
   need(re.findall(r"(?:^|\n)Ran ([0-9]+) tests?\b",raw)==[str(row["tests"])],"Actual saved unittest count differs")
 return dict(acceptance=ar,contracts=d["contracts"],derived_source_manifest=d["derived_source_manifest"],derived_source_files=d["source_files"],actual_terminal_accounting=accounting,derived_pipeline=d["derived_pipeline"],default_tree_sha256=d["default_python_source_sha256_without_staged_runtime_selector"],all_eight_actual_suite_rows_verified=True,source_dependencies=d["source_dependencies"],failed_predecessor=d["failed_predecessor"])

def replacement_binding(obj,request,sources):
 need(obj.get("schema")=="default-materialized-generic-integration-acceptance.v2"and obj.get("status")=="DEFAULT_GENERIC_PHYSICAL_GATE_AND_MATERIALIZED_RUNTIME_INTEGRATION_CPU_VERIFIED_NOT_PUBLISHED","Actual distinct three-path default integration required")
 need(request.get("schema")=="default-generic-materialized-integration-request.v2"and request.get("root_approved")is True,"Root reviewed explicit three-path integration request required")
 paths={"src/ppiblocker/pipeline.py","src/ppiblocker/pose_physical_gate.py","environment/runtime-lock-rfd.json"}
 ops=request.get("operations",[]);need(len(ops)==3 and {o.get("repository_relative")for o in ops}==paths,"Exactly three accepted replacement paths required")
 by={o["repository_relative"]:o for o in ops}
 need(by["src/ppiblocker/pipeline.py"].get("old")is not None and by["src/ppiblocker/pose_physical_gate.py"].get("old")is None and by["environment/runtime-lock-rfd.json"].get("old")is not None,"Old pipeline/RFD lock and absent helper contract differs")
 for o in ops:receipt_shape(o["new"])
 need(obj.get("source_manifest")==request.get("source_manifest")and obj.get("old_tree_sha256")==request.get("expected_old_tree_sha256")and obj.get("new_tree_sha256")==request.get("expected_new_tree_sha256"),"Actual whole Python-tree/source manifest binding differs")
 replacement=obj.get("replacement",{})
 need(len(replacement.get("replaced_paths",[]))==3 and set(replacement["replaced_paths"])==paths,"Actual accepted replaced paths differ")
 records=replacement.get("new_default_files",[]);need(len(records)==3,"Exact three actual new default descriptors required")
 actual={Path(r["path"]).relative_to(R/"source").as_posix():r for r in records}
 declared={s["repository_relative"]:s["receipt"]for s in sources if s["repository_relative"]in paths}
 need(set(actual)==paths and set(declared)==paths,"Actual and explicitly declared default three files required")
 for p in paths:need(fp(actual[p])==fp(by[p]["new"])==fp(declared[p]),"Actual new file differs from exact accepted replacement: "+p)
 need(fp(replacement["old_pipeline_archive"])==fp(by["src/ppiblocker/pipeline.py"]["old"])and fp(replacement["old_rfd_lock_archive"])==fp(by["environment/runtime-lock-rfd.json"]["old"]),"Exact old pipeline/RFD lock archives required")
 return by
def inherited_source_route(row,ops):
 d=row["repository_relative"]
 if d in {"src/ppiblocker/pipeline.py","environment/runtime-lock-rfd.json"}:
  need(fp(row["source"])==fp(ops[d]["old"]),"Inherited current source differs from integration exact old bytes")
  name="pipeline.py"if d.endswith("pipeline.py")else"runtime-lock-rfd.json"
  role="SUPERSEDED_DEFAULT_GENERIC_EXACT_HISTORY"if name=="pipeline.py"else"SUPERSEDED_DEFAULT_RFD_LOCK_EXACT_HISTORY"
  return "rebuild/benchmarks/20261011/exact_source_aliases/"+row["source"]["sha256"]+"_"+name,[role]
 if d=="src/ppiblocker/pose_physical_gate.py":raise ValueError("Inherited helper contradicts exact originally absent helper")
 return d,row.get("roles",[row.get("role","INHERITED_ACCEPTED_SOURCE")])
def software_shape(obj,contracts):
 need(obj.get("schema")=="final-source-materialized-software-acceptance.v3"and obj.get("status")==SOFTWARE_STATUS,"Actual distinct library software qualification required")
 sources=obj.get("source_files");need(isinstance(sources,list)and len(sources)==6 and {Path(r["path"]).name for r in sources}==set(PACKAGE_NAMES),"Exact six qualified library source files required")
 need(contracts.get("status")=="PASS"and contracts.get("tests")==SOURCE_CONTRACTS and contracts.get("failures")==0 and contracts.get("errors")==0 and contracts.get("tested_source_files")==sources and contracts.get("owned_python_compile_PASS")is True and contracts.get("bash_syntax_PASS")is True,"Actual saved53/count/source/syntax library contracts required")
 return sources

def require_context_reader(plan,reader,complete=False):
 accepted=getattr(reader,"accepted",None);qualification=getattr(reader,"qualification",None)
 need(isinstance(accepted,dict)and accepted.get("schema")=="exact-current-context-mapper-acceptance.v4"and accepted.get("status")=="EXACT_BBF6_RECOVERED5_NINE_ANNOTATIONS_ARCHIVE588_AND_EIGHT_SOURCE_ALIASES_MAPPER_CPU_ACCEPTED"and isinstance(qualification,dict),"Production audit requires actual qualified four-map/five-parent reader")
 need(qualification.get("mapper_acceptance")==plan.get("mapper_software_acceptance")and accepted.get("base_acceptance")==plan.get("base_acceptance")and accepted.get("relative_receipt_context_mapping")==plan.get("relative_receipt_context_mapping")and accepted.get("external_historical_receipt_context_mapping")==plan.get("external_historical_receipt_context_mapping")and accepted.get("current_recovered_relative_receipt_context_mapping")==plan.get("current_recovered_relative_receipt_context_mapping")and accepted.get("archive_member_receipt_context_mapping")==plan.get("archive_member_receipt_context_mapping"),"Actual mapper reader differs from explicit base/maps/qualification")
 finite=getattr(reader,"finite",None);verification=getattr(finite,"verification",None)
 need(isinstance(verification,dict)and verification.get("schema")=="independent-source-alias-and-provenance-verification.v1"and verification.get("status")=="EXACT_V10_SELECTED8_ORIGINAL12_AND_FIVE_PROOF_PARENTS_INDEPENDENTLY_CPU_VERIFIED","Actual full SourceV10 finite qualification required")
 need(accepted.get("exact_recovered_source_identity_n")==8 and accepted.get("exact_original_source_edge_n")==12 and all(accepted.get(name)==verification.get("artifacts",{}).get(name)and isinstance(accepted.get(name),dict)for name in ("finite_source_recovery_inputs_qualification","finite_source_alias_verification","finite_exact_source_alias_index")),"Actual exact three SourceV10 artifact pointers required")
 if complete:reader.require_both_used()
 return reader.proof()
def inherited_archive_edge(e,reader):
 mapping=getattr(getattr(reader,"archives",None),"mapping",None)
 need(isinstance(mapping,dict),"Accepted actual archive map required for inherited scalar member")
 item=e.get("historical_archive_member");role="HISTORICAL_ARCHIVE_NAMESPACE_MEMBER_BYTE_VERIFIED_NOT_CURRENT_FILE_OR_NEW_SCIENCE"
 need(isinstance(item,dict)and e.get("role")==role,"Unknown inherited scalar archive role")
 matches=[a for a in mapping.get("archives",[])if a.get("parent_manifest")==item.get("source_parent")];need(len(matches)==1,"Unknown inherited archive parent")
 archive=matches[0];fields=item.get("source_field");matches=[x for x in archive.get("entries",[])if x.get("source_field")==fields]
 need(len(matches)==1,"Unknown inherited archive member field")
 expected={**matches[0],"archive_receipt":archive["archive_receipt"],"role":role}
 need(item==expected and e.get("field")==fields and expected.get("canonical_receipt")is None and expected.get("current_execution_allowed")is False and expected.get("current_file_restored")is False and expected.get("raw_member_bytes_verified_in_archive")is True,"Inherited archive member descriptor/policy fork")
 return e
def freeze_runner(out):
 here=Path(__file__).resolve().parent;need(not(here.stat().st_mode&0o222),"Reviewed package must be readonly before CPU execution")
 target=out/"runner";target.mkdir()
 for name in PACKAGE_NAMES:
  p=here/name;need(p.is_file()and not p.is_symlink()and not(p.stat().st_mode&0o222),"Readonly reviewed runner package required")
  shutil.copyfile(p,target/name);(target/name).chmod(0o444)
 target.chmod(0o555)
 return [rec(target/n)for n in PACKAGE_NAMES]
def contracts(out):
 spec=__import__("importlib.util",fromlist=["util"])
 path=out/"runner/test_final_source_closure.py"
 ss=spec.spec_from_file_location("final_source_tests",path);mm=spec.module_from_spec(ss);ss.loader.exec_module(mm)
 suite=unittest.defaultTestLoader.loadTestsFromModule(mm)
 need(suite.countTestCases()==SOURCE_CONTRACTS,"Expected53 source-boundary contracts")
 with(out/"contracts.txt").open("x")as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
 (out/"contracts.txt").chmod(0o444)
 rr=dump(out/"contracts.json",dict(status="PASS"if result.wasSuccessful()else"FAIL",tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),log=rec(out/"contracts.txt"),tested_source_files=[rec(out/"runner"/n)for n in PACKAGE_NAMES],owned_python_compile_PASS=True,bash_syntax_PASS=True))
 need(result.wasSuccessful(),"Source closure software contracts failed")
 return rr
def software(out):
 allocation=cpu();out=safe_path(out);out.mkdir(parents=True,exist_ok=False);stage="owned_source_freeze"
 try:
  runners=freeze_runner(out)
  need(fp(rec(Path(__file__).resolve()))==fp(next(r for r in runners if Path(r["path"]).name=="final_source_closure.py")),"Executing owned source differs from frozen library")
  for r in runners:
   if Path(r["path"]).suffix==".py":compile(Path(r["path"]).read_bytes(),r["path"],"exec",dont_inherit=True)
  need(subprocess.run(["bash","-n",str(out/"runner/final_source_cpu.sbatch")],capture_output=True,text=True).returncode==0,"Exact library launcher syntax failed")
  stage="software53";cr=contracts(out);co=read(verify(cr,True));obj=dict(schema="final-source-materialized-software-acceptance.v3",status=SOFTWARE_STATUS,source_files=runners,contracts=cr,allocation=allocation,no_model_calls=True,no_GPU_submission=True,science_or_integration_accepted=False,source_staged=False,published=False,ACTIVE_changed=False)
  software_shape(obj,co);descriptor=dump(out/"acceptance.json",obj)
  print(json.dumps(dict(status=SOFTWARE_STATUS,acceptance=descriptor),sort_keys=True),flush=True)
 except Exception as e:
  dump(out/"typed_incomplete.json",dict(status="FINAL_SOURCE_MATERIALIZED_SOFTWARE_TYPED_INCOMPLETE",failed_stage=stage,reason_type=type(e).__name__,reason=str(e),allocation=allocation,source_staged=False,ACTIVE_changed=False));raise
def audit(plan_path,out):
 allocation=cpu();out=safe_path(out);out.mkdir(parents=True,exist_ok=False);stage="bootstrap"
 try:
  runners=freeze_runner(out)
  for r in runners:
   if Path(r["path"]).suffix==".py":compile(Path(r["path"]).read_bytes(),r["path"],"exec",dont_inherit=True)
  syntax=subprocess.run(["bash","-n",str(out/"runner/final_source_cpu.sbatch")],capture_output=True,text=True);need(syntax.returncode==0,"Frozen library launcher syntax failed")
  need(fp(rec(Path(__file__).resolve()))==fp(next(r for r in runners if Path(r["path"]).name=="final_source_closure.py")),"Executing owned library differs from frozen source")
  test_receipt=contracts(out);stage="explicit_plan"
  p=safe_path(plan_path);need(not(p.stat().st_mode&0o222),"Explicit reviewed plan must be readonly")
  plan=read(p);modules=module_plan(plan);require_context_reader(plan,read)
  stage="base_readback";accepted=read(verify(plan["base_acceptance"]))
  need(accepted.get("status")=="CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY"and accepted.get("source_issues")==0 and accepted.get("source_staged")is False,"Actual accepted repaired V10 sourcebase required")
  base=read(verify(accepted["source_inclusion"]));closure=read(verify(accepted["source_closure"]))
  need(base.get("status")=="SOURCE_INCLUSION_AUDIT_PASS"and base.get("applied")is False and not base.get("issues"),"Exact nonstaging accepted base inclusion required")
  need(base.get("formal_array_job_id")=="13260","Base source binds different formal array")
  need(base.get("source_receipt_closure")==accepted["source_closure"],"Accepted base closure pointer differs")
  integrated=next(m for m in modules if m["role"]=="default_workflow_integration")
  integration_obj=read(verify(integrated["gate"]["receipt"]))
  need(integration_obj.get("status")==integrated["gate"]["expected_status"],"Default integration is not actually accepted")
  integration_request=read(verify(integration_obj["request"]))
  replacement_ops=replacement_binding(integration_obj,integration_request,integrated["sources"])
  derived_qualification_proof=derived_qualification_binding(integration_obj,integration_request,replacement_ops)
  verify(integration_obj["replacement"]["old_pipeline_archive"],True);verify(integration_obj["replacement"]["old_rfd_lock_archive"],True)
  integration_sources=integration_obj.get("source_files",[]);need(len(integration_sources)==4 and {Path(r["path"]).name for r in integration_sources}==INTEGRATION_NAMES,"Whole actual qualified external integration source4 required")
  for rr in integration_sources:
   verify(rr,True);need(any(fp(rr)==fp(ss["receipt"])for ss in integrated["sources"]),"Executed integration source omitted from final source scope")
  for rr in integration_obj["replacement"]["new_default_files"]:verify(rr)
  rows={};aliases={};inherited_edges={};history={};all_edges=[];sources={};deps={};data=set();gate_records=[];seen=set()
  def alias(logical,physical):
   receipt_shape(logical);receipt_shape(physical);need(fp(logical)==fp(physical),"Source alias changes bytes")
   k=key(logical)
   if k in aliases:need(fp(aliases[k])==fp(physical),"Conflicting alias")
   aliases[k]=physical
  for row in base["files"]:
   verify(row["source"],True);alias(row["original_source"],row["source"])
  for e in closure["edges"]:
   if "receipt"not in e:
    if e.get("role")=="HISTORICAL_ARCHIVE_NAMESPACE_MEMBER_BYTE_VERIFIED_NOT_CURRENT_FILE_OR_NEW_SCIENCE":inherited_archive_edge(e,read)
    else:need(e.get("role")=="HISTORICAL_PROVENANCE_ANNOTATION_UNRECOVERED_NOT_BYTE_ACCEPTED"and isinstance(e.get("historical_annotation"),dict),"Unknown scalar inherited edge denied")
    all_edges.append(e);continue
   ek=(key(e["receipt"]),e.get("parent"),tuple(e.get("field",[])))
   inherited_edges[ek]=e
   if e.get("role")=="TYPED_NONOPERATIVE_HISTORICAL_GAP":history[ek]=e
   elif "physical"in e:alias(e["receipt"],e["physical"])
  alias(replacement_ops["src/ppiblocker/pipeline.py"]["old"],integration_obj["replacement"]["old_pipeline_archive"])
  alias(replacement_ops["environment/runtime-lock-rfd.json"]["old"],integration_obj["replacement"]["old_rfd_lock_archive"])
  for a in plan.get("aliases",[]):alias(a["logical"],a["physical"]);verify(a["physical"])
  def resolve(r):
   receipt_shape(r)
   if key(r)in aliases:return verify(aliases[key(r)]),"EXPLICIT_EXACT_BYTE_ALIAS"
   return verify(r),"EXACT_ORIGINAL"
  frozen=out/"readonly_source_bytes";frozen.mkdir()
  def add(r,d,roles,logical=None):
   d=eligible_public(r,d);physical,basis=resolve(r);b=physical.read_bytes()
   need(fp(rec(physical))==fp(r),"Source changed during CPU readback")
   b.decode("utf-8")
   need(not SECRET_RE.search(b.decode("utf-8"))and "-----BEGIN "+"OPENSSH PRIVATE KEY-----"not in b.decode("utf-8"),"Potential credential in selected public source; root review required")
   c=frozen/(r["sha256"]+"_"+physical.name)
   if c.exists():need(c.read_bytes()==b,"Frozen source collision")
   else:c.write_bytes(b);c.chmod(0o444)
   if d in rows:need(fp(rows[d]["source"])==fp(r),"Different sources target same repository destination")
   else:rows[d]=dict(source=rec(c),original_source=r,repository_relative=d,roles=[],logical_receipts=[],kind=kind(physical),cluster_specific=b"/lustre/users/"in b or b"#SBATCH"in b)
   rows[d]["roles"]=sorted(set(rows[d]["roles"])|set(roles));rows[d]["role"]=";".join(rows[d]["roles"])
   if logical and logical not in rows[d]["logical_receipts"]:rows[d]["logical_receipts"].append(logical)
  for row in base["files"]:
   inherited_destination,inherited_roles=inherited_source_route(row,replacement_ops)
   add(row["source"],inherited_destination,inherited_roles,row.get("original_source"))
  for rr in runners:add(rr,"rebuild/benchmarks/20261011/steps/24_benchmark_delivery/code/final_source_closure_v3/"+Path(rr["path"]).name,["FINAL_SOURCE_MATERIALIZED_CONTEXT_RUNNER"])
  queue=[(receipt_shape(r),None,(),"EXACT_ACCEPTED_CONTEXT_PARENT")for r in plan.get("context_parent_seeds",[])]
  for m in modules:
   g=m["gate"];obj=read(verify(g["receipt"]))
   need(obj.get("status")==g["expected_status"],"Module terminal acceptance not exact: "+m["role"])
   if m["role"]=="reference_free_e2e"and g["expected_status"]=="CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED":
    need(obj.get("qualified_prediction",{}).get("status")=="POSE_REJECTED","Accepted pose requires actual design/refold/final audit, not preflight-only completion")
    terminal=m.get("root_terminal_rejection_gate");need(isinstance(terminal,dict),"Root CPU terminal rejection receipt required")
    tr=read(verify(terminal["receipt"]));need(tr.get("status")==terminal["expected_status"]and tr.get("preflight")==g["receipt"],"Terminal rejection does not bind actual preflight")
    need(tr.get("new_inference_GPU_seconds")==0 and tr.get("new_design_performed")is False and tr.get("new_refold_performed")is False,"Rejected native pose must not force model continuation")
    queue.append((terminal["receipt"],None,(),m["role"]))
   for s in m["sources"]:add(s["receipt"],s["repository_relative"],[m["role"]])
   if m["role"]in {"reference_free_e2e","formal_common_review"}:
    ac=m.get("allocation_closure_gate");need(isinstance(ac,dict),"Root complete GPU submission/allocation cost closure gate required")
    ao=read(verify(ac["receipt"]));need(ac["expected_status"]=="ROOT_CURRENT_GPU_SUBMISSION_UNIVERSE_AND_TERMINAL_COST_CPU_ACCEPTED"and ao.get("status")==ac["expected_status"],"Exact independent root allocation closure is not actually accepted")
    need(ao.get("complete_root_gpu_submission_universe")is True and ao.get("allocated_failure_before_manifest_cost_retained")is True,"Missing-result GPU allocation costs cannot be omitted")
    need(isinstance(ao.get("root_gpu_submission_receipts"),list)and isinstance(ao.get("terminal_numeric_accounting_receipts"),list),"Actual root submissions and terminal numeric accounting must be preserved")
    queue.append((ac["receipt"],None,(),m["role"]))
   gate_records.append(dict(role=m["role"],gate=g))
   for r in [g["receipt"]]+m.get("seeds",[]):receipt_shape(r);queue.append((r,None,(),m["role"]))
  stage="recursive_exact_new_dependencies"
  while queue:
   r,parent,trail,module=queue.pop();ek=(key(r),parent,trail)
   # Permission is an exact historical edge of the accepted base, checked before dedup.
   if ek in history:
    all_edges.append(dict(receipt=r,parent=parent,field=list(trail),module=module,role="INHERITED_EXACT_NONOPERATIVE_HISTORICAL_EDGE_NOT_CURRENT_BYTE_ACCEPTANCE"));continue
   if conditional(r["path"]):
    deps[key(r)]=r;all_edges.append(dict(receipt=r,parent=parent,field=list(trail),module=module,role="CONDITIONAL_INFERENCE_DEPENDENCY_EXCLUDED_FROM_PUBLIC_SOURCE"));continue
   if key(r)in seen:continue
   seen.add(key(r));suffix=Path(r["path"]).suffix
   if suffix not in RECEIPT_TEXT_EXT:
    data.add(key(r));all_edges.append(dict(receipt=r,parent=parent,field=list(trail),module=module,role="DATA_RECEIPT_RETAINED_NOT_RAW_REAUDITED"));continue
   physical,basis=resolve(r)
   all_edges.append(dict(receipt=r,parent=parent,field=list(trail),module=module,physical=rec(physical),resolution_basis=basis,role="EXACT_NEW_TEXT_RECEIPT_READBACK"))
   if suffix in SOURCE_EXT:
    sources[key(r)]=r
    if not any(fp(row["source"])==fp(r)for row in rows.values()):
     add(r,"rebuild/benchmarks/20261011/exact_source_aliases/"+r["sha256"]+"_"+Path(r["path"]).name,[module,"RECURSIVE_OPERATIVE_SOURCE"],r)
   if suffix==".json":
    obj=read(physical)
    if metadata_only(obj):continue
    # Accepted edge-seal annotations are coverage metadata, not invented source edges.
    if isinstance(obj,dict)and "historical_MSA_gaps"in obj:
     recorded={(key(x["original"]),x["parent"],tuple(x["trail"]))for x in obj["historical_MSA_gaps"]}
     need(len(recorded)==2 and recorded<=set(history),"Historical annotation set differs from inherited exact accepted edges")
     obj={k:v for k,v in obj.items()if k!="historical_MSA_gaps"}
    queue.extend((n,r["path"],t,module)for n,t in receipt_edges(obj))
  frozen.chmod(0o555)
  context_proof=dump(out/"exact_five_parent_context_reader_proof.json",require_context_reader(plan,read,True))
  closed=dump(out/"source_receipt_closure_final.json",dict(schema="final-source-receipt-closure.v2",status="EXACT_NEW_SOURCE_DEPENDENCIES_WITH_INHERITED_TYPED_HISTORY",base_closure=accepted["source_closure"],module_gates=gate_records,edges=all_edges,source_receipts=list(sources.values()),conditional_dependencies=list(deps.values()),data_receipts_retained_not_reaudited_n=len(data),no_new_historical_waivers=True,raw_content_reaudited=False))
  stage="inclusion"
  inclusion=dump(out/"source_inclusion_final.json",dict(schema="benchmark-source-inclusion.v3",status="SOURCE_INCLUSION_AUDIT_PASS",authority_root=str(R),files=sorted(rows.values(),key=lambda x:x["repository_relative"]),issues=[],applied=False,runner_source_snapshot=runners,allocation=allocation,base_inclusion=accepted["source_inclusion"],source_receipt_closure=closed,explicit_plan=rec(p),module_gates=gate_records,entry_kind_counts=dict(collections.Counter(x["kind"]for x in rows.values())),formal_array_job_id="13260",source_staged=False,source_published=False,ACTIVE_changed=False,scientific_endpoint_acceptance_performed=False,scope="Exact final public source coverage only; root scientific content/publication/archive/promotion remain separate required gates"))
  result=dict(schema="final-source-closure-acceptance.v3",status="FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED",source_inclusion=inclusion,source_closure=closed,exact_five_parent_context_reader_proof=context_proof,mandatory_derived_pipeline_qualification=derived_qualification_proof,explicit_plan=rec(p),contracts=test_receipt,source_entries=len(rows),source_issues=0,required_modules=sorted(REQUIRED_MODULES),module_gates=gate_records,allocation=allocation,source_staged=False,source_published=False,ACTIVE_changed=False,no_model_calls=True,no_GPU_submission=True)
  descriptor=dump(out/"acceptance.json",result)
  print(json.dumps({"acceptance":descriptor},sort_keys=True),flush=True)
  for x in out.glob("*.json"):x.chmod(0o444)
  print(result["status"])
 except Exception as e:
  dump(out/"typed_incomplete.json",dict(status="FINAL_SOURCE_CLOSURE_TYPED_INCOMPLETE_NO_STAGING",failed_stage=stage,reason_type=type(e).__name__,reason=str(e),allocation=allocation,partial_bytes_retained=True,source_staged=False,ACTIVE_changed=False));raise
def stage(audit_path,audit_sha,out):
 allocation=cpu();r=rec(safe_path(audit_path));need(r["sha256"]==audit_sha,"Explicit accepted inclusion SHA required")
 obj=read(verify(r));need(obj.get("status")=="SOURCE_INCLUSION_AUDIT_PASS"and obj.get("applied")is False and not obj.get("issues"),"Nonstaging accepted source inclusion required")
 need(obj.get("schema")=="benchmark-source-inclusion.v3"and obj.get("formal_array_job_id")=="13260","Wrong exact source inclusion identity")
 for rr in obj["runner_source_snapshot"]:verify(rr,True)
 expected=next(rr for rr in obj["runner_source_snapshot"]if Path(rr["path"]).name=="final_source_closure.py")
 need(rec(Path(__file__).resolve())==expected,"Execute exact accepted frozen stage runner")
 checked=[]
 for row in obj["files"]:
  original=verify(row["source"],True);d=R/"source"/destination(row["repository_relative"]);safe_path(d)
  need(not d.exists()or d.is_file(),"Repository destination is not regular file")
  if d.exists():need(fp(rec(d))==fp(row["source"]),"Different existing destination requires root integration review: "+str(d))
  checked.append((original,d,row))
 out=safe_path(out);out.mkdir(parents=True,exist_ok=False);created=[]
 for original,d,row in checked:
  d.parent.mkdir(parents=True,exist_ok=True)
  if not d.exists():shutil.copyfile(original,d);created.append(str(d))
  need(fp(rec(d))==fp(row["source"]),"Source installation CPU readback mismatch")
 dump(out/"acceptance.json",dict(status="EXACT_AUDITED_FROZEN_SOURCE_SET_INSTALLED_NOT_GIT_STAGED",source_inclusion=r,allocation=allocation,entry_n=len(checked),created_files=created,working_tree_commit_or_stage_performed=False,ACTIVE_changed=False,GPU_submitted=False))
def main():
 ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest="command",required=True)
 w=sub.add_parser("software");w.add_argument("--out",required=True)
 a=sub.add_parser("audit");a.add_argument("--plan",required=True);a.add_argument("--out",required=True)
 s=sub.add_parser("stage");s.add_argument("--audit",required=True);s.add_argument("--audit-sha256",required=True);s.add_argument("--out",required=True)
 a=ap.parse_args()
 if a.command=="software":software(a.out)
 elif a.command=="audit":audit(a.plan,a.out)
 else:stage(a.audit,a.audit_sha256,a.out)
if __name__=="__main__":main()
