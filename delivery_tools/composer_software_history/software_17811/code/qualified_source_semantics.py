#!/usr/bin/env python3
"""Exact successor source closure; CPU only, no model calls or release promotion.

Consume an accepted immutable base inclusion plus explicit accepted new modules.
Never enumerate live source directories, infer "latest", or copy inference assets.
"""
import argparse,collections,hashlib,json,os,re,shutil,stat,subprocess,sys,unittest
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
SOURCE_CONTRACTS=356
REGRESSION_NAMES={"test_development_regressions.py","test_audit_regressions.py","test_benchmark.py","test_construct_contract.py","test_scientific_contracts.py","test_runtime_registration.py","test_af2_review.py"}
REGRESSION7=REGRESSION_NAMES
INTEGRATION_NAMES={"integrate_default_workflow_v3.py","test_integrate_default_workflow_v3.py","default_integration_cpu_v3.sbatch","HANDOFF.md"}
SOFTWARE_STATUS="FINAL_SOURCE_MATERIALIZED_FINITE_WORKER_AND_CATALOG_MSA_CONTEXTS_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_INTEGRATION"
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

CORE_LOGICAL=Path("/lustre/users/u21111210118/projects/test9/env/core/bin/python")
CORE_REAL=Path("/lustre/users/u21111210118/projects/test9/env/core/bin/python3.11")
CORE_BYTES=25916456
CORE_SHA="76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a"
SOFTWARE_JOB_NAME="test9_final_source_catalog_msa_gap_contracts_v3"
def stable_metadata(p):
 p=Path(p);s=p.lstat()
 return dict(path=str(p),bytes=s.st_size,inode=s.st_ino,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,mode=s.st_mode,dev=s.st_dev,nlink=s.st_nlink,uid=s.st_uid,gid=s.st_gid)
def owned_source_bundle(directory):
 directory=safe_path(directory);need(directory.is_dir()and not(directory.stat().st_mode&0o222)and {x.name for x in directory.iterdir()}==set(PACKAGE_NAMES),"Exact readonly own6 source universe required")
 rows=[]
 for name in PACKAGE_NAMES:
  p=safe_path(directory/name);need(p.is_file()and not(p.stat().st_mode&0o222),"Readonly regular owned source required");rows.append(rec(p))
 return rows,[stable_metadata(x["path"])for x in rows]
def owned_source_readback(original,frozen,before_original,before_frozen):
 need(len(original)==len(frozen)==6 and {Path(x["path"]).name for x in original}=={Path(x["path"]).name for x in frozen}==set(PACKAGE_NAMES),"Whole6 original/frozen sources required")
 for rows,before in ((original,before_original),(frozen,before_frozen)):
  need(len(before)==6 and [stable_metadata(verify(x,True))for x in rows]==before,"Owned source bytes/metadata changed after execution")
 left={Path(x["path"]).name:fp(x)for x in original};right={Path(x["path"]).name:fp(x)for x in frozen}
 need(left==right,"Original and actually tested frozen own6 bytes differ")
 return True
def core_runtime_shape(value):
 need(isinstance(value,dict)and value.get("schema")=="conditional-core-interpreter-byte-identity.v1"and value.get("logical_executable")==str(CORE_LOGICAL)and value.get("link_text")=="python3.11"and value.get("resolved_binary_identity")==dict(logical_path=str(CORE_REAL),bytes_as_scalar=CORE_BYTES,sha256_as_scalar=CORE_SHA)and value.get("conditional_excluded_not_archived")is True,"Exact conditional CORE interpreter identity required")
 return value
def conditional_core_runtime():
 need(Path(sys.executable)==CORE_LOGICAL,"Exact approved CORE logical interpreter required")
 a=stable_metadata(CORE_LOGICAL);b=stable_metadata(CORE_REAL)
 need(CORE_LOGICAL.is_symlink()and os.readlink(CORE_LOGICAL)=="python3.11"and CORE_LOGICAL.resolve()==CORE_REAL and CORE_REAL.is_file()and not CORE_REAL.is_symlink(),"Exact CORE link/resolved regular executable required")
 digest=rec(CORE_REAL)
 need(digest["bytes"]==CORE_BYTES and digest["sha256"]==CORE_SHA,"Conditional CORE whole-byte identity changed")
 need(stable_metadata(CORE_LOGICAL)==a and stable_metadata(CORE_REAL)==b,"Conditional CORE stable metadata changed while reading")
 return core_runtime_shape(dict(schema="conditional-core-interpreter-byte-identity.v1",logical_executable=str(CORE_LOGICAL),link_text="python3.11",resolved_binary_identity=dict(logical_path=str(CORE_REAL),bytes_as_scalar=CORE_BYTES,sha256_as_scalar=CORE_SHA),logical_metadata=a,resolved_metadata=b,conditional_excluded_not_archived=True,atime_excluded_from_stable_identity=True))
def software_snapshot_shape(obj,snapshot):
 need(snapshot.get("schema")=="final-source-owned-six-byte-snapshot.v1"and snapshot.get("original_executing_sources")==obj["original_executing_sources"]and snapshot.get("source_files")==obj["source_files"]and snapshot.get("source_entry")==obj["source_entry"]and snapshot.get("conditional_core_runtime")==obj["conditional_core_runtime"],"Accepted software snapshot/source/runtime fork")
 for prefix,receipts in (("original",obj["original_executing_sources"]),("frozen",obj["source_files"])):
  before=snapshot.get(prefix+"_metadata_before");after=snapshot.get(prefix+"_metadata_after")
  need(isinstance(before,list)and len(before)==6 and exact_json(before,after),"Whole6 stable metadata before/end table required")
  expected={r["path"]:r["bytes"]for r in receipts};need({x.get("path")for x in before}==set(expected),"Metadata/source path universe differs")
  fields={"path","bytes","inode","mtime_ns","ctime_ns","mode","dev","nlink","uid","gid"}
  for value in before:
   need(set(value)==fields and all(type(value[k])is int and value[k]>=0 for k in fields-{"path"})and value["bytes"]==expected[value["path"]]and stat.S_ISREG(value["mode"])and not(value["mode"]&0o222),"Exact readonly regular source metadata integers required")
 need(snapshot.get("whole6_source_prepost_PASS")is True and snapshot.get("original_and_frozen_owned_bytes_identical")is True and snapshot.get("conditional_runtime_prepost_PASS")is True,"Actual original/frozen six pre/end byte metadata/runtime proof required")
 return snapshot

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

# Only four already accepted SOURCE rows may have an extensionless public name.
# These are script bytes, not copied environments, executables, packages or weights.
INHERITED_ENTRYPOINT_BASE = json.loads(r'''{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/acceptance.json","bytes":10963,"sha256":"fcaeb34bb139bc2c4a271e44dd72f23260592af23c872c4ae2bb7a8f67c47e58"}''')
INHERITED_ENTRYPOINT_INCLUSION = json.loads(r'''{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/source_inclusion_v3.json","bytes":784715,"sha256":"8909e49a5a5396827135e9492af393bdc369e2a28d766cc8767ff24f03914f6a"}''')
INHERITED_ENTRYPOINT_CONTEXTS = json.loads(r'''[{"index":561,"row":{"source":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/readonly_source_bytes/602fbcae9af76fe89e509df8ac42bf72c9b0e551fbbc4ea3ec815fa00801ca9d_boltz","bytes":201,"sha256":"602fbcae9af76fe89e509df8ac42bf72c9b0e551fbbc4ea3ec815fa00801ca9d"},"original_source":{"path":"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/common_core_v2_13130/code/runtime_entries/boltz","bytes":201,"sha256":"602fbcae9af76fe89e509df8ac42bf72c9b0e551fbbc4ea3ec815fa00801ca9d"},"repository_relative":"rebuild/benchmarks/20261011/steps/23_common_review/frozen/common_core_v2_13130/code/runtime_entries/boltz","role":"CURRENT_CORRECTED_COMMON_CORE_V2","roles":["CURRENT_CORRECTED_COMMON_CORE_V2"],"kind":"IMPLEMENTATION","logical_receipts":[],"cluster_specific":true}},{"index":562,"row":{"source":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/readonly_source_bytes/2bdee1ae29c1137de4c8b982fec72f595b28a3ca2f17ca9828ce2522af5839c6_colabfold_batch","bytes":212,"sha256":"2bdee1ae29c1137de4c8b982fec72f595b28a3ca2f17ca9828ce2522af5839c6"},"original_source":{"path":"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/common_core_v2_13130/code/runtime_entries/colabfold_batch","bytes":212,"sha256":"2bdee1ae29c1137de4c8b982fec72f595b28a3ca2f17ca9828ce2522af5839c6"},"repository_relative":"rebuild/benchmarks/20261011/steps/23_common_review/frozen/common_core_v2_13130/code/runtime_entries/colabfold_batch","role":"CURRENT_CORRECTED_COMMON_CORE_V2","roles":["CURRENT_CORRECTED_COMMON_CORE_V2"],"kind":"IMPLEMENTATION","logical_receipts":[],"cluster_specific":true}},{"index":580,"row":{"source":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/readonly_source_bytes/602fbcae9af76fe89e509df8ac42bf72c9b0e551fbbc4ea3ec815fa00801ca9d_boltz","bytes":201,"sha256":"602fbcae9af76fe89e509df8ac42bf72c9b0e551fbbc4ea3ec815fa00801ca9d"},"original_source":{"path":"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/native_common_13051/code/runtime_entries/boltz","bytes":201,"sha256":"602fbcae9af76fe89e509df8ac42bf72c9b0e551fbbc4ea3ec815fa00801ca9d"},"repository_relative":"rebuild/benchmarks/20261011/steps/23_common_review/frozen/native_common_13051/code/runtime_entries/boltz","role":"HISTORICAL_NATIVE_SCIENTIFIC_SOURCE_13051","roles":["HISTORICAL_NATIVE_SCIENTIFIC_SOURCE_13051"],"kind":"IMPLEMENTATION","logical_receipts":[],"cluster_specific":true}},{"index":581,"row":{"source":{"path":"/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/readonly_source_bytes/2bdee1ae29c1137de4c8b982fec72f595b28a3ca2f17ca9828ce2522af5839c6_colabfold_batch","bytes":212,"sha256":"2bdee1ae29c1137de4c8b982fec72f595b28a3ca2f17ca9828ce2522af5839c6"},"original_source":{"path":"/lustre/users/u21111210118/projects/test9/steps/23_common_review/frozen/native_common_13051/code/runtime_entries/colabfold_batch","bytes":212,"sha256":"2bdee1ae29c1137de4c8b982fec72f595b28a3ca2f17ca9828ce2522af5839c6"},"repository_relative":"rebuild/benchmarks/20261011/steps/23_common_review/frozen/native_common_13051/code/runtime_entries/colabfold_batch","role":"HISTORICAL_NATIVE_SCIENTIFIC_SOURCE_13051","roles":["HISTORICAL_NATIVE_SCIENTIFIC_SOURCE_13051"],"kind":"IMPLEMENTATION","logical_receipts":[],"cluster_specific":true}}]''')
INHERITED_ENTRYPOINT_BASE_N = 683
def exact_json(left,right):
 if type(left)is not type(right):return False
 if isinstance(left,dict):return set(left)==set(right)and all(exact_json(left[k],right[k])for k in left)
 if isinstance(left,list):return len(left)==len(right)and all(exact_json(a,b)for a,b in zip(left,right))
 return left==right
class InheritedEntryPointScope:
 def __init__(self,base_receipt,inclusion_receipt,files):
  receipt_shape(base_receipt);receipt_shape(inclusion_receipt);need(isinstance(files,list),"Inherited source rows must be a list")
  named=base_receipt["path"]==INHERITED_ENTRYPOINT_BASE["path"]or inclusion_receipt["path"]==INHERITED_ENTRYPOINT_INCLUSION["path"]
  self.actual_base=named
  if named:
   need(exact_json(base_receipt,INHERITED_ENTRYPOINT_BASE)and exact_json(inclusion_receipt,INHERITED_ENTRYPOINT_INCLUSION),"Exact accepted Source13316 base/inclusion authority required")
   need(len(files)==INHERITED_ENTRYPOINT_BASE_N,"All683 accepted inherited source rows required")
  self.expected_n=len(files);self.original_keys=[key(receipt_shape(x["source"]))for x in files]
  self.contexts={x["index"]:x["row"]for x in INHERITED_ENTRYPOINT_CONTEXTS};self.observed=set();self.considered=set();self.retained=set()
 def permission(self,index,row,r,d,roles):
  need(type(index)is int and 0<=index<self.expected_n and index not in self.considered,"Inherited row must be observed once before source identity dedup")
  need(exact_json(row.get("source"),r)and key(r)==self.original_keys[index],"Inherited row source identity fork")
  self.considered.add(index)
  candidate=index in self.contexts if self.actual_base else False
  original=row.get("original_source");original_path=original.get("path")if isinstance(original,dict)else None
  protected=any(row.get("repository_relative")==x["row"]["repository_relative"]or original_path==x["row"]["original_source"]["path"]or r["path"]==x["row"]["source"]["path"]for x in INHERITED_ENTRYPOINT_CONTEXTS)
  if candidate or protected or Path(r["path"]).suffix=="":
   need(self.actual_base and candidate and exact_json(row,self.contexts[index]),"Only four exact accepted inherited entrypoint contexts may authorize extensionless text")
   need(d==row["repository_relative"]and exact_json(roles,row["roles"]),"Inherited entrypoint destination or role fork")
   need(index not in self.observed,"Duplicate inherited entrypoint context")
   self.observed.add(index)
   d=destination(d);p=Path(r["path"])
   need(not conditional(p),"Conditional inference asset is not public source")
   need(not any(x in p.parts for x in (".git","site-packages","weights","params")),"Private/runtime tree is not public source")
   need(not any(x in p.name.lower()for x in ("id_ed25519","credential")),"Credential/licensed software asset excluded")
   return d,"IMPLEMENTATION"
  return eligible_public(r,d),None
 def mark_retained(self,index,row):
  need(index in self.considered and index not in self.retained and key(row["source"])==self.original_keys[index],"Inherited row was not independently added exactly once")
  self.retained.add(index)
 def require_complete(self):
  need(self.considered==self.retained==set(range(self.expected_n)),"Every inherited source row must be retained before dedup")
  if self.actual_base:need(self.expected_n==683 and self.observed==set(self.contexts),"All683 rows and all four exact inherited entrypoint observations required")
  else:need(not self.observed,"No extensionless permission outside the exact accepted base")
 def proof(self):
  self.require_complete()
  return dict(schema="exact-accepted-inherited-entrypoint-source-scope.v1",status="EXACT_SOURCE13316_FOUR_ENTRYPOINT_CONTEXTS_ALL683_RETAINED"if self.actual_base else"ORDINARY_PUBLIC_POLICY_ONLY_NO_EXTENSIONLESS_PERMISSION",
   accepted_base=INHERITED_ENTRYPOINT_BASE if self.actual_base else None,accepted_inclusion=INHERITED_ENTRYPOINT_INCLUSION if self.actual_base else None,
   inherited_source_row_n=self.expected_n,retained_inherited_source_row_n=len(self.retained),authorized_context_n=len(self.observed),
   authorized_contexts=[dict(index=i,row=self.contexts[i])for i in sorted(self.observed)],every_inherited_row_retained=True,
   generic_public_text_policy_changed=False,basename_or_extensionless_permission_granted=False,raw_source_JSON_rewritten=False,
   installed_runtime_or_binary_or_weights_copied=False,new_receipt_parent_permission_granted=False)


# One documented vendor demonstration stream, never a receipt/configuration SOURCE.
# These private literal pins are not arguments, environment options or Plan scopes.
_VENDOR_EXAMPLE_PARENT = {
    "path": "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/runtime_drift_diagnostic_13275/vendor_dllogger_files.json",
    "bytes": 3700,
    "sha256": "db80ec35cdabb7e66a846df974cafe57e8b1ac1a121fc582b5d0a751d06bf239",
}
_VENDOR_EXAMPLE_LEAF = {
    "path": "/lustre/users/u21111210118/projects/test9/vendor/dllogger/examples/example_resnet_log.json",
    "bytes": 12874,
    "sha256": "ac323732e3b9cfead3f394467b08a03e7a8f30af2178335531129955f4594df4",
}
_VENDOR_EXAMPLE_MODULE = "default_workflow_integration"
_VENDOR_EXAMPLE_ROLE = "EXACT_FINITE_OPAQUE_VENDOR_EXAMPLE_DATA_NOT_RECEIPT_OR_SOURCE"


def _strict_vendor_json(raw):
    def pairs(items):
        result = {}
        for name, value in items:
            need(name not in result, "Duplicate key in finite vendor format")
            result[name] = value
        return result

    def constant(value):
        raise ValueError("Nonfinite number in finite vendor format: " + value)

    def number(value):
        result = float(value)
        need(result == result and abs(result) != float("inf"),
             "Nonfinite exponent in finite vendor format")
        return result

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant, parse_float=number)


def _vendor_example_matches(receipt):
    receipt_shape(receipt)
    return receipt["path"] == _VENDOR_EXAMPLE_LEAF["path"] or fp(receipt) == fp(_VENDOR_EXAMPLE_LEAF)


def reject_vendor_example_declaration(receipt):
    need(not _vendor_example_matches(receipt),
         "Finite opaque vendor DATA cannot be a direct SOURCE, seed, gate, context or Plan alias")


class VendorExampleOpaqueLeaf:
    """Authorize this one raw DATA edge before any graph identity deduplication."""

    def __init__(self, out):
        self.out = safe_path(out)
        self.observed = 0
        self.parent_before = None
        self.leaf_before = None
        self.copy_receipt = None
        self.copy_before = None
        self.record_types = None

    @staticmethod
    def _regular(path, readonly):
        path = safe_path(path)
        value = stable_metadata(path)
        need(stat.S_ISREG(value["mode"]) and value["nlink"] == 1,
             "Finite vendor input must be a nonsymlink single-link regular file")
        need(not readonly or not (value["mode"] & 0o222),
             "Finite vendor parent/copy must be readonly")
        return path, value

    def _inputs(self):
        parent, parent_before = self._regular(_VENDOR_EXAMPLE_PARENT["path"], True)
        leaf, leaf_before = self._regular(_VENDOR_EXAMPLE_LEAF["path"], False)
        need(leaf_before["mode"] & 0o777 == 0o664,
             "Original vendor demonstration permission must remain0664")
        parent_bytes = parent.read_bytes()
        leaf_bytes = leaf.read_bytes()
        need((len(parent_bytes), hashlib.sha256(parent_bytes).hexdigest()) == fp(_VENDOR_EXAMPLE_PARENT),
             "Exact finite vendor parent bytes changed")
        need((len(leaf_bytes), hashlib.sha256(leaf_bytes).hexdigest()) == fp(_VENDOR_EXAMPLE_LEAF),
             "Exact finite vendor example bytes changed")
        need(stable_metadata(parent) == parent_before and stable_metadata(leaf) == leaf_before,
             "Finite vendor inputs drifted during read")
        rows = _strict_vendor_json(parent_bytes)
        need(isinstance(rows, list) and len(rows) == 18,
             "Exact finite vendor parent must contain18 rows")
        identities = set()
        paths = set()
        for row in rows:
            need(isinstance(row, dict) and set(row) == {"path", "bytes", "sha256"},
                 "Finite vendor parent row shape changed")
            receipt_shape(row)
            safe_path(row["path"])
            need(key(row) not in identities and row["path"] not in paths,
                 "Duplicate or forked vendor inventory path")
            identities.add(key(row))
            paths.add(row["path"])
        need(rows[15] == _VENDOR_EXAMPLE_LEAF, "Exact vendor inventory row15 changed")
        text = leaf_bytes.decode("utf-8")
        need(not SECRET_RE.search(text) and "-----BEGIN " + "OPENSSH PRIVATE KEY-----" not in text,
             "Potential credential in finite vendor example")
        lines = text.splitlines()
        need(len(lines) == 52 and all(line.startswith("DLLL ") for line in lines),
             "Exact vendor example requires52 DLLL records")
        types = collections.Counter()
        for line in lines:
            record = _strict_vendor_json(line[5:])
            need(isinstance(record, dict) and isinstance(record.get("type"), str) and record["type"] in {"LOG", "METADATA"},
                 "Unknown finite vendor demonstration record")
            types[record["type"]] += 1
        need(set(types) == {"LOG", "METADATA"}, "Both documented vendor record kinds required")
        need(stable_metadata(parent) == parent_before and stable_metadata(leaf) == leaf_before,
             "Finite vendor inputs drifted during format verification")
        return parent_before, leaf_before, leaf_bytes, dict(sorted(types.items()))

    def _copy(self, content):
        directory = self.out / "opaque_vendor_example_bytes"
        directory.mkdir(exist_ok=False)
        path = directory / (_VENDOR_EXAMPLE_LEAF["sha256"] + "_example_resnet_log.OPAQUE.txt")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o444)
            os.fsync(stream.fileno())
        descriptor = rec(path)
        need(fp(descriptor) == fp(_VENDOR_EXAMPLE_LEAF) and path.read_bytes() == content,
             "Finite vendor opaque preservation differs from original bytes")
        self._regular(path, True)
        directory.chmod(0o555)
        parent_fd = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
        self.copy_receipt = descriptor
        self.copy_before = stable_metadata(path)

    def edge(self, receipt, parent, trail, module):
        if not _vendor_example_matches(receipt):
            return None
        need(receipt == _VENDOR_EXAMPLE_LEAF and parent == _VENDOR_EXAMPLE_PARENT["path"]
             and type(trail) is tuple and trail == ("15",)
             and module == _VENDOR_EXAMPLE_MODULE,
             "Opaque vendor DATA requires its exact parent/field/module/child identity")
        parent_before, leaf_before, content, types = self._inputs()
        if self.observed == 0:
            self.parent_before = parent_before
            self.leaf_before = leaf_before
            self.record_types = types
            self._copy(content)
        else:
            need(parent_before == self.parent_before and leaf_before == self.leaf_before
                 and types == self.record_types, "Repeated finite vendor edge drifted")
        self.observed += 1
        self.readback()
        return dict(receipt=dict(_VENDOR_EXAMPLE_LEAF), parent=parent,
                    field=list(trail), module=module, physical=self.copy_receipt,
                    resolution_basis="EXACT_READONLY_OPAQUE_DATA_BYTECOPY",
                    role=_VENDOR_EXAMPLE_ROLE,
                    raw_bytes_preserved=True, receipt_children_interpreted=False,
                    source_or_configuration_promotion=False)

    def readback(self):
        need(self.observed > 0 and self.copy_receipt is not None,
             "Finite vendor preservation has not occurred")
        parent_before, leaf_before, content, types = self._inputs()
        need(parent_before == self.parent_before and leaf_before == self.leaf_before
             and types == self.record_types, "Finite vendor original bytes/metadata drifted")
        copy_path, copy_metadata = self._regular(self.copy_receipt["path"], True)
        need(copy_metadata == self.copy_before and rec(copy_path) == self.copy_receipt
             and copy_path.read_bytes() == content,
             "Finite vendor readonly opaque copy changed")
        need(stable_metadata(copy_path) == self.copy_before,
             "Finite vendor opaque copy drifted during readback")
        return True

    def require_complete(self, actual_base):
        if actual_base:
            need(self.observed > 0, "Actual source graph must observe exact finite vendor DATA edge")
        if self.observed:
            self.readback()
        return self.observed > 0

    def alias_index(self):
        self.readback()
        return dict(schema="exact-resource-aliases.v2",
                    status="EXACT_VENDOR_EXAMPLE_OPAQUE_DATA_BYTE_ALIAS_CPU_VERIFIED",
                    aliases=[dict(original=dict(_VENDOR_EXAMPLE_LEAF),
                                  archived=self.copy_receipt,
                                  status="READONLY_BYTE_IDENTICAL_ALIAS",
                                  role=_VENDOR_EXAMPLE_ROLE)],
                    historical_unresolved=[],
                    separate_original_JSON_physical_package_entry_forbidden=True,
                    scientific_or_source_acceptance=False)

    def proof(self):
        self.readback()
        return dict(schema="exact-vendor-example-opaque-data-leaf.v1",
                    status="EXACT_PARENT18_FIELD15_VENDOR_DLLL52_DATA_BYTES_PRESERVED_CPU_VERIFIED",
                    parent_manifest=dict(_VENDOR_EXAMPLE_PARENT),
                    original_data_leaf=dict(_VENDOR_EXAMPLE_LEAF),
                    source_field=["15"], module=_VENDOR_EXAMPLE_MODULE,
                    role=_VENDOR_EXAMPLE_ROLE,
                    archived_opaque_data=self.copy_receipt,
                    parent_metadata_before=self.parent_before,
                    parent_metadata_after=stable_metadata(_VENDOR_EXAMPLE_PARENT["path"]),
                    original_metadata_before=self.leaf_before,
                    original_metadata_after=stable_metadata(_VENDOR_EXAMPLE_LEAF["path"]),
                    preserved_metadata=self.copy_before,
                    authorized_observation_n=self.observed,
                    vendor_inventory_row_n=18, vendor_stream_record_n=52,
                    vendor_stream_record_types=self.record_types,
                    original_bytes_and_metadata_unchanged=True,
                    original_permission_unchanged=True,
                    preserved_copy_readonly_fsynced_and_byte_identical=True,
                    original_JSON_or_parent_rewritten=False,
                    receipt_children_interpreted=False,
                    public_source_or_configuration_promoted=False,
                    scientific_content_accepted=False,
                    generic_JSON_parser_or_context_permissions_changed=False,
                    future_package_index_and_isolated_restore_acceptance=False)



def verify_vendor_example_preservation(saved, alias_index, allocation):
    """Current CPU saved-proof readback; no restored/live fallback API is added."""
    need(isinstance(saved, dict) and isinstance(alias_index, dict),
         "Actual finite vendor proof and alias index required")
    copy_receipt = receipt_shape(saved["archived_opaque_data"])
    path = safe_path(copy_receipt["path"])
    need(path.name == _VENDOR_EXAMPLE_LEAF["sha256"] + "_example_resnet_log.OPAQUE.txt"
         and path.parent.name == "opaque_vendor_example_bytes",
         "Exact finite vendor preservation destination required")
    scope = VendorExampleOpaqueLeaf(path.parent.parent)
    need(saved["exact_alias_index"]["path"] == str(scope.out / "vendor_example_opaque_aliases.json"),
         "Exact finite vendor alias control destination required")
    parent_before, leaf_before, unused, types = scope._inputs()
    need(type(saved.get("authorized_observation_n")) is int
         and saved["authorized_observation_n"] >= 1,
         "Actual authorized finite vendor observations required")
    scope.parent_before = parent_before
    scope.leaf_before = leaf_before
    scope.copy_receipt = copy_receipt
    scope.copy_before = stable_metadata(verify(copy_receipt, True))
    scope.record_types = types
    scope.observed = saved["authorized_observation_n"]
    expected = dict(scope.proof(), allocation=allocation,
                    exact_alias_index=receipt_shape(saved["exact_alias_index"]))
    need(exact_json(saved, expected), "Saved finite vendor proof differs from current complete content")
    need(exact_json(alias_index, scope.alias_index()), "Saved finite vendor alias index differs")
    need(rec(verify(saved["exact_alias_index"], True)) == saved["exact_alias_index"],
         "Saved finite vendor alias index bytes changed")
    return True






# Four exact inherited history authorities; no Cartesian or generic permission.
_FIXED_HISTORY_MAPPING_PARENTS = (
    dict(base_field="external_historical_receipt_context_mapping",
         receipt=dict(path=str(R / "steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/external_historical_receipt_context_mapping.json"),
                      bytes=27119, sha256="c01e18d92dd84f3e8cf44a1a4377677bddc0ee3a512d9a61ecaeda05a6f3da24"),
         schema="exact-unrecovered-historical-annotations.v1",
         status="EXACT_NINE_NONOPERATIVE_HISTORICAL_ANNOTATIONS_CPU_CLASSIFIED_ORIGINAL_JSON_UNCHANGED"),
    dict(base_field="current_recovered_relative_receipt_context_mapping",
         receipt=dict(path=str(R / "steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/current_recovered_relative_receipt_context_mapping.json"),
                      bytes=16545, sha256="ddf785a624b01bb16ff91a12d4f1a7bba29a97a216b70f88744f83d305c40c70"),
         schema="exact-current-recovered-five-relative-context.v1",
         status="EXACT_FIVE_CURRENT_RECOVERED_EVIDENCE_CPU_BYTE_ACCEPTED_ORIGINAL_JSON_UNCHANGED"),
    dict(base_field="archive_member_receipt_context_mapping",
         receipt=dict(path=str(R / "steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/archive_member_receipt_context_mapping.json"),
                      bytes=502724, sha256="22aa7c0f30d2b97e7b5ec090a8a0fda9c1ea2d63bf3f056b4e111e737354329d"),
         schema="exact-historical-archive-member-context.v1",
         status="EXACT_TWO_HISTORICAL_ARCHIVES_AND588_MEMBER_BYTES_CPU_VERIFIED_ORIGINAL_INDEX_JSON_UNCHANGED"))
_FIXED_HISTORY_MAPPING_PROVENANCE = dict(
    producer_executed_source=dict(path=str(R / "steps/24_benchmark_delivery/frozen/source_refresh_relative_v10_13316/code/source_delivery_refresh_v10.py"),
                                 bytes=119405, sha256="576a9b04b9bcaeb7578ad979a972c8d448af546c7f54c10180e4ec22ed08564e"),
    producer_actual_software_gate=dict(path=str(R / "steps/24_benchmark_delivery/runs/source_relative_contracts_13316/acceptance.json"),
                                      bytes=2519, sha256="09eb3de1cc420179b98e54becb2c01c2f462a501aeeef639d33460012096d5c2"),
    source_graph_selector=dict(path=str(R / "steps/24_benchmark_delivery/frozen/source_refresh_relative_v10_13316/code/delivery_graph_v2.py"),
                               bytes=8774, sha256="e14b12e01c8e2b9a70ecb30d70d2194bbe89147c01eb02dd305be4075276f98d"))
_FIXED_HISTORY_LINEAGE_SLOTS = {
    "inventory13299": (2, 3), "archive13298": (2, 2),
    "relative13295": (1, 2), "parent13290": (0, 6)}


def _fixed_history_definition(family):
    prefixes = {"inventory13299": ("_HISTORY", "history"),
                "archive13298": ("_ARCHIVE_PARENT_HISTORY", "archive_parent_history"),
                "relative13295": ("_RELATIVE_DIAGNOSTIC_HISTORY", "relative_diagnostic_history"),
                "parent13290": ("_PARENT_DIAGNOSTIC_HISTORY", "parent_diagnostic_history")}
    need(type(family) is str and family in prefixes, "Unknown fixed inherited history family")
    prefix, stem = prefixes[family]
    return dict(base=globals()[prefix + "_BASE"], leaf=globals()[prefix + "_LEAF"],
                field=globals()[prefix + "_FIELD"], modules=globals()[prefix + "_MODULES"],
                metadata_shape=globals()["_" + stem + "_metadata_shape"])


def _fixed_history_contexts(family):
    definition = _fixed_history_definition(family)
    rows = [dict(parent_manifest=dict(definition["base"]), field=list(definition["field"]),
                 receipt=dict(definition["leaf"]))]
    rows.extend(dict(parent_manifest=dict(entry["receipt"]), field=list(definition["field"]),
                     receipt=dict(definition["leaf"])) for entry in _FIXED_HISTORY_MAPPING_PARENTS)
    slot, index = _FIXED_HISTORY_LINEAGE_SLOTS[family]
    rows.append(dict(parent_manifest=dict(_FIXED_HISTORY_MAPPING_PARENTS[slot]["receipt"]),
                     field=["accepted_lineage_receipts", str(index)], receipt=dict(definition["leaf"])))
    need(len(rows) == 5 and len({(r["parent_manifest"]["path"], tuple(r["field"])) for r in rows}) == 5,
         "Exactly five distinct fixed parent/field rows required")
    return rows


def _fixed_history_context(family, parent, trail, module):
    definition = _fixed_history_definition(family)
    need(type(parent) is str and type(trail) is tuple and module in definition["modules"],
         "Fixed inherited history requires exact parent/field/two-module/fulltuple context")
    rows = [row for row in _fixed_history_contexts(family)
            if row["parent_manifest"]["path"] == parent and tuple(row["field"]) == trail]
    need(len(rows) == 1, "Fixed inherited history requires exact parent/field/two-module/fulltuple context")
    return rows[0]


def _fixed_history_observation_context(family, observation):
    need(type(observation) is dict and type(observation.get("field")) is list
         and all(type(x) is str for x in observation["field"])
         and type(observation.get("parent_manifest")) is dict,
         "Full selected inherited history parent/field required")
    row = _fixed_history_context(family, observation["parent_manifest"].get("path"),
                                 tuple(observation["field"]), observation.get("module"))
    need(exact_json(observation["parent_manifest"], row["parent_manifest"])
         and exact_json(observation.get("receipt"), row["receipt"]),
         "Fixed inherited history selected full parent/leaf receipt changed")
    return row


def _fixed_history_authority_projection(family, metadata):
    definition = _fixed_history_definition(family)
    receipts = [dict(definition["base"])] + [dict(x["receipt"]) for x in _FIXED_HISTORY_MAPPING_PARENTS]
    need(type(metadata) is list and len(metadata) == 4, "Closed four-authority native metadata table required")
    checked = [definition["metadata_shape"](value, receipt["path"], receipt["bytes"])
               for value, receipt in zip(metadata, receipts)]
    return dict(authority_receipts=receipts,
                authority_metadata_before=[dict(x) for x in checked],
                authority_metadata_after=[dict(x) for x in checked],
                authorized_parent_field_rows=_fixed_history_contexts(family),
                authority_policy="FOUR_FULL_PINNED_AUTHORITIES_FIVE_EXACT_ROWS_NOT_PARENT_FIELD_CARTESIAN_PRODUCT",
                prospective_rows_require_actual_runtime_authentication=True,
                relative_BBF_mapping_parent_authorized=False,
                generic_parent_or_module_permission_added=False)


def _fixed_history_saved_authorities(family, saved):
    projection = _fixed_history_authority_projection(family, saved.get("authority_metadata_before"))
    need(exact_json(saved.get("authority_metadata_after"), projection["authority_metadata_after"])
         and exact_json(saved.get("parent_metadata_before"), projection["authority_metadata_before"][0])
         and exact_json(saved.get("parent_metadata_after"), projection["authority_metadata_before"][0]),
         "Full inherited history authority metadata binding changed")
    return projection



def _fixed_history_authority_fence(family, original_metadata):
    """Closed no-JSON final guard: original full receipts/native, never a ratchet."""
    projection = _fixed_history_authority_projection(family, original_metadata)
    receipts = projection["authority_receipts"]
    baseline = projection["authority_metadata_before"]
    for receipt, expected in zip(receipts, baseline):
        path = safe_path(receipt["path"])
        need(exact_json(stable_metadata(path), expected) and rec(path) == receipt
             and exact_json(stable_metadata(path), expected),
             "Fixed inherited history authority changed after final control read")
    # A later own-byte read must not change an earlier authority's native state.
    for receipt, expected in zip(receipts, baseline):
        need(exact_json(stable_metadata(safe_path(receipt["path"])), expected),
             "Fixed inherited history authority changed after final control read")
    return True



def _fixed_history_native_union_sweep(original_records):
    """True last operation: native-only, no JSON/hash/read or baseline refresh."""
    need(type(original_records) is list and bool(original_records),
         "Original finite native union required")
    union = {}
    for record in original_records:
        need(type(record) is dict and set(record) == _HISTORY_META_KEYS
             and type(record.get("path")) is str
             and all(type(record[name]) is int and record[name] >= 0 for name in _HISTORY_META_KEYS - {"path"}),
             "Exact original finite native record required")
        path = record["path"]
        need(path not in union or union[path] == record,
             "Conflicting original native baselines for the same finite path")
        union[path] = record
    for path, expected in union.items():
        # These exact two paths are the already authenticated conditional CORE.
        # This last sweep checks only their original native records, not bytes.
        if path == str(CORE_LOGICAL):
            current = stable_metadata(Path(path))
            need(stat.S_ISLNK(current["mode"]) and current["bytes"] == 10 and current["nlink"] == 1,
                 "Exact conditional CORE logical native type required")
        elif path == str(CORE_REAL):
            current = stable_metadata(Path(path))
            need(stat.S_ISREG(current["mode"]) and current["bytes"] == CORE_BYTES and current["nlink"] == 1,
                 "Exact conditional CORE resolved native type required")
        else:
            current = stable_metadata(safe_path(path))
        need(current == expected,
             "Fixed history final native union drifted")
    return True


def _fixed_history_saved_native_records(saved):
    """Projection of existing producer baselines; never captures current metadata."""
    need(type(saved) is dict and type(saved.get("authority_metadata_before")) is list,
         "Saved finite authority native table required")
    return list(saved["authority_metadata_before"]) + [
        saved["original_metadata_before"], saved["preserved_metadata"], saved["copy_directory_metadata"]]


def _fixed_history_mapping_inputs(family, base, base_before):
    definition = _fixed_history_definition(family)
    history = base.get("original_failure_history")
    need(type(history) is dict, "Exact BaseA inherited history object required")
    receipts = [definition["base"]] + [entry["receipt"] for entry in _FIXED_HISTORY_MAPPING_PARENTS]
    metadata = [base_before]
    for slot, entry in enumerate(_FIXED_HISTORY_MAPPING_PARENTS):
        receipt = entry["receipt"]
        need(exact_json(base.get(entry["base_field"]), receipt), "Exact BaseA mapping descriptor changed")
        path = safe_path(receipt["path"])
        before = stable_metadata(path)
        definition["metadata_shape"](before, receipt["path"], receipt["bytes"])
        need(rec(path) == receipt, "Fixed inherited mapping own bytes changed")
        text = path.read_bytes().decode("utf-8")
        need(not SECRET_RE.search(text) and "-----BEGIN " + "OPENSSH PRIVATE KEY-----" not in text,
             "Potential credential in fixed inherited mapping")
        obj = _strict_history_json(text)
        need(type(obj) is dict and obj.get("schema") == entry["schema"] and obj.get("status") == entry["status"]
             and exact_json(obj.get("original_failure_history"), history)
             and all(exact_json(obj.get(name), value) for name, value in _FIXED_HISTORY_MAPPING_PROVENANCE.items()),
             "Fixed inherited mapping schema/history/producer provenance changed")
        chosen_slot, index = _FIXED_HISTORY_LINEAGE_SLOTS[family]
        if chosen_slot == slot:
            lineage = obj.get("accepted_lineage_receipts")
            need(type(lineage) is list and len(lineage) > index
                 and exact_json(lineage[index], definition["leaf"]),
                 "Exact inherited mapping lineage slot changed")
        need(rec(path) == receipt and exact_json(stable_metadata(path), before),
             "Fixed inherited mapping changed during strict own JSON readback")
        metadata.append(before)
    for receipt, before in zip(receipts, metadata):
        need(rec(safe_path(receipt["path"])) == receipt
             and exact_json(stable_metadata(safe_path(receipt["path"])), before),
             "Fixed inherited history authority changed after the last mapping JSON read")
    _fixed_history_authority_projection(family, metadata)
    return metadata


# One immutable diagnostic history DATA object; embedded member records are not inputs.
_HISTORY_BASE = dict(INHERITED_ENTRYPOINT_BASE)
_HISTORY_AUTHORITY = "/lustre/users/u21111210118/projects/test9"
_HISTORY_LEAF = {
    "path": str(R / "steps/24_benchmark_delivery/runs/source_unknown_relative_inventory_13299/diagnostic.json"),
    "bytes": 590526,
    "sha256": "8bc7232449d5469cc621e6e34b26716c3d8ff65fc4a52e10d04b3977d9229313",
}
_HISTORY_FIELD = ("original_failure_history", "actual13299_complete_accessible_finite_inventory_diagnostic_only")
_HISTORY_MODULES = ("default_workflow_integration", "final_delivery_tools")
_HISTORY_ROLE = "EXACT13299_DIAGNOSTIC_HISTORY_DATA_NOT_RECEIPT_SOURCE_OR_ARCHIVE_AUTHORIZATION"
_HISTORY_PRODUCER = {
    "path": str(R / "steps/24_benchmark_delivery/frozen/source_refresh_relative_v7_13297/code/source_delivery_refresh_v7.py"),
    "bytes": 42275,
    "sha256": "c2e9bd2502edc353055b038d50bce79ae70ee92685df095d88cfb74fabe260b1",
}
_HISTORY_SOFTWARE = {
    "path": str(R / "steps/24_benchmark_delivery/runs/source_relative_contracts_13297/acceptance.json"),
    "bytes": 2513,
    "sha256": "cd7c356bc2736b76d593426cade0438bcd404b3a5addc80da10aff8716d6b4f1",
}
_HISTORY_MANIFESTS = (
    ({"path": str(R / "archive/reconstruction_completed_modules_20261002.members.json"),
      "bytes": 45243, "sha256": "dae90d5f02faedeef24d887e6edf414b86fc63d268e54e58a6a0d558c08d3d6e"}, 193),
    ({"path": str(R / "archive/reconstruction_data_20261002.members.json"),
      "bytes": 98587, "sha256": "20d567dad8b3ae4ec8daf2bf4077f48ba982a746b2a750e0537ab07604ad6e70"}, 395),
)
_HISTORY_FALSE_FLAGS = (
    "default_changed", "source_staged", "formal_outputs_read", "model_inference",
    "archive_bytes_read", "all_unknown_nested_contexts_claimed", "scientific_acceptance",
)
_HISTORY_TRUE_FLAGS = (
    "guard_modified_only_in_diagnostic_process", "production_source_bytes_unchanged",
    "unrecognized_children_not_recursively_read",
)
_HISTORY_PROOF_SCHEMA = "exact13299-inventory-diagnostic-history-data-leaf.v2"
_HISTORY_PROOF_STATUS = "EXACT_BASEA_HISTORY_CONTEXTS_AND13299_DIAGNOSTIC_DATA_BYTES_PRESERVED_CPU_VERIFIED"
_HISTORY_ALIAS_STATUS = "EXACT13299_DIAGNOSTIC_HISTORY_DATA_BYTE_ALIAS_CPU_VERIFIED"
_HISTORY_META_KEYS = {"path", "bytes", "inode", "mtime_ns", "ctime_ns", "mode", "dev", "nlink", "uid", "gid"}


def _strict_history_json(raw):
    def pairs(items):
        result = {}
        for name, value in items:
            need(name not in result, "Duplicate key in fixed inventory history JSON")
            result[name] = value
        return result

    def constant(value):
        raise ValueError("Nonfinite fixed inventory history JSON number: " + value)

    def number(value):
        result = float(value)
        need(result == result and abs(result) != float("inf"),
             "Nonfinite fixed inventory history JSON exponent")
        return result

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant, parse_float=number)


def _inventory_history_matches(receipt):
    receipt_shape(receipt)
    return receipt["path"] == _HISTORY_LEAF["path"] or fp(receipt) == fp(_HISTORY_LEAF)


def reject_inventory_history_declaration(receipt):
    need(not _inventory_history_matches(receipt),
         "Fixed13299 diagnostic DATA cannot be direct SOURCE/gate/seed/context/Plan alias")


def inventory_history_document_shape(obj):
    """Pure object validation: no member path is normalized, resolved, statted or opened."""
    need(isinstance(obj, dict)
         and obj.get("schema") == "source-unknown-relative-finite-inventory-diagnostic-only.v1"
         and obj.get("status") == "FINITE_UNKNOWN_RELATIVE_EDGES_COLLECTED_NO_SOURCE_ACCEPTANCE_NO_AUTHORIZATION",
         "Exact nonauthorizing13299 diagnostic schema/status required")
    need(obj.get("job_id") == "13299" and obj.get("failed_source_job") == "13297"
         and type(obj.get("CPU")) is int and obj["CPU"] == 1
         and type(obj.get("GPU")) is int and obj["GPU"] == 0,
         "Fixed13299 diagnostic identity/CPU-only declaration changed")
    need(all(obj.get(k) is False for k in _HISTORY_FALSE_FLAGS)
         and all(obj.get(k) is True for k in _HISTORY_TRUE_FLAGS),
         "Fixed inventory diagnostic must remain nonauthorizing history")
    need(obj.get("source_producer") == _HISTORY_PRODUCER
         and obj.get("software_only_gate") == _HISTORY_SOFTWARE,
         "Fixed13299 producer/software observations changed")
    need(type(obj.get("parent_count")) is int and obj["parent_count"] == 2
         and type(obj.get("edge_count")) is int and obj["edge_count"] == 588,
         "Diagnostic metadata requires exactly2 parents/588 observations")
    parents = obj.get("parents")
    need(isinstance(parents, list) and len(parents) == 2,
         "Fixed diagnostic parent metadata shape changed")
    expected_edges = []
    for entry, (manifest, count) in zip(parents, _HISTORY_MANIFESTS):
        need(isinstance(entry, dict) and set(entry) == {"parent", "physical_parent", "parent_JSON"}
             and entry["parent"] == manifest and entry["physical_parent"] == manifest,
             "Fixed diagnostic embedded manifest identity changed")
        declared = entry["parent_JSON"]
        need(isinstance(declared, dict) and type(declared.get("member_count")) is int
             and declared["member_count"] == count
             and isinstance(declared.get("members"), list) and len(declared["members"]) == count,
             "Fixed diagnostic193/395 member metadata shape changed")
        # These are scalar historical namespace observations. Never receipt_shape(member).
        for member in declared["members"]:
            need(isinstance(member, dict) and set(member) == {"path", "bytes", "sha256"}
                 and isinstance(member["path"], str) and bool(member["path"])
                 and type(member["bytes"]) is int and member["bytes"] >= 0
                 and isinstance(member["sha256"], str)
                 and re.fullmatch("[0-9a-f]{64}", member["sha256"]) is not None,
                 "Fixed diagnostic member observation shape changed")
        for index in reversed(range(count)):
            expected_edges.append(dict(parent=manifest, field=["members", str(index)],
                                       original_relative_receipt=declared["members"][index],
                                       diagnostic_only_edge_skipped=True,
                                       authorization_granted=False, current_canonical_child=None))
    need(exact_json(obj.get("edges"), expected_edges),
         "All588 ordered diagnostic observations must remain nonauthorizing and unchanged")
    return True


def _history_metadata_shape(value, expected_path, size=None, directory=False):
    """Pure metadata shape validation; independently enforce444 files or555 directory."""
    need(isinstance(value, dict) and set(value) == _HISTORY_META_KEYS
         and value.get("path") == expected_path
         and all(type(value[k]) is int and value[k] >= 0 for k in _HISTORY_META_KEYS - {"path"}),
         "Exact integer fixed inventory history metadata required")
    if directory:
        need(stat.S_ISDIR(value["mode"]) and stat.S_IMODE(value["mode"]) == 0o555
             and value["nlink"] == 2,
             "Fixed history copy directory must independently be readonly0555")
    else:
        need(stat.S_ISREG(value["mode"]) and stat.S_IMODE(value["mode"]) == 0o444
             and value["nlink"] == 1 and value["bytes"] == size,
             "Fixed history input/copy must be readonly0444 single-link regular")
    return value


def _history_copy_structure(receipt):
    receipt_shape(receipt)
    need(set(receipt) == {"path", "bytes", "sha256"} and fp(receipt) == fp(_HISTORY_LEAF),
         "Fixed history copy must preserve the exact full byte identity")
    raw = receipt["path"]
    path = Path(raw)
    need(path.is_absolute() and path.is_relative_to(Path(_HISTORY_AUTHORITY))
         and all(part not in ("", ".", "..") for part in raw.split("/")[1:])
         and path.name == _HISTORY_LEAF["sha256"] + "_13299_diagnostic.OPAQUE.txt"
         and path.parent.name == "opaque_inventory_history_bytes",
         "Exact fixed history preservation path required")
    return path


def inventory_history_proof_shape(saved, alias_index, allocation):
    """Pure strict validator for later INDEX-only replay; performs no filesystem calls."""
    need(isinstance(saved, dict) and isinstance(alias_index, dict) and isinstance(allocation, dict),
         "Full fixed history proof/index/allocation objects required")
    copy_receipt = saved.get("preserved_opaque_data")
    path = _history_copy_structure(copy_receipt)
    out = path.parent.parent
    pointer = receipt_shape(saved.get("exact_alias_index"))
    need(set(pointer) == {"path", "bytes", "sha256"}
         and pointer["path"] == str(out / "inventory_history_opaque_aliases.json"),
         "Fixed history proof/index pointer changed")
    need(isinstance(allocation.get("job_id"), str) and allocation["job_id"].isdigit()
         and type(allocation.get("allocated_CPUs")) is int and allocation["allocated_CPUs"] >= 1
         and type(allocation.get("allocated_gpus")) is int and allocation["allocated_gpus"] == 0,
         "Actual CPU allocation object required for fixed history proof")
    observations = saved.get("observations")
    need(isinstance(observations, list) and observations, "Actual ordered history observations required")
    expected_observations = []
    for index, observation in enumerate(observations):
        need(isinstance(observation, dict) and observation.get("module") in _HISTORY_MODULES,
             "Unknown fixed history observation module")
        selected = _fixed_history_observation_context("inventory13299", observation)
        expected_observations.append(dict(
            ordinal=index, receipt=dict(_HISTORY_LEAF), parent_manifest=dict(selected["parent_manifest"]),
            field=list(selected["field"]), module=observation["module"], physical=copy_receipt,
            resolution_basis="EXACT_READONLY13299_DIAGNOSTIC_HISTORY_DATA_BYTECOPY", role=_HISTORY_ROLE))
    need(exact_json(observations, expected_observations),
         "Full ordered fixed history observation context changed")
    actual_default = sum(x["module"] == "default_workflow_integration" for x in observations)
    actual_prospective = sum(x["module"] == "final_delivery_tools" for x in observations)
    need(actual_default >= 1, "At least one actual default history edge must be observed")
    parent_meta = _history_metadata_shape(saved.get("parent_metadata_before"), _HISTORY_BASE["path"],
                                          _HISTORY_BASE["bytes"])
    leaf_meta = _history_metadata_shape(saved.get("original_metadata_before"), _HISTORY_LEAF["path"],
                                        _HISTORY_LEAF["bytes"])
    copy_meta = _history_metadata_shape(saved.get("preserved_metadata"), str(path), copy_receipt["bytes"])
    directory_meta = _history_metadata_shape(saved.get("copy_directory_metadata"), str(path.parent),
                                             directory=True)
    expected = dict(
        schema=_HISTORY_PROOF_SCHEMA, status=_HISTORY_PROOF_STATUS,
        parent_manifest=dict(_HISTORY_BASE), original_diagnostic_data=dict(_HISTORY_LEAF),
        source_field=list(_HISTORY_FIELD), role=_HISTORY_ROLE,
        allowed_modules=list(_HISTORY_MODULES),
        module_policy=dict(default_workflow_integration="FINITE_FIVE_ROWS_ACTUAL_RUNTIME_PARENT_FIELD_AUTHENTICATION_REQUIRED",
                           final_delivery_tools="PROSPECTIVE_SAME_FIVE_ROWS_NOT_REQUIRED"),
        preserved_opaque_data=copy_receipt, exact_alias_index=pointer, allocation=allocation,
        parent_metadata_before=parent_meta, parent_metadata_after=parent_meta,
        original_metadata_before=leaf_meta, original_metadata_after=leaf_meta,
        preserved_metadata=copy_meta, copy_directory_metadata=directory_meta,
        observations=expected_observations, authorized_observation_n=len(observations),
        actual_default_observation_n=actual_default, actual_finaltools_observation_n=actual_prospective,
        embedded_parent_n=2, embedded_member_counts=[193, 395], embedded_observation_n=588,
        independent_source_producer=dict(_HISTORY_PRODUCER),
        independent_software_only_gate=dict(_HISTORY_SOFTWARE),
        independent_BaseA_history_fields_retained=True,
        original_bytes_and_metadata_unchanged=True, original_permission_unchanged=True,
        preserved_copy_readonly_fsynced_and_byte_identical=True,
        embedded_relative_targets_interpreted=False, member_paths_statted_or_opened=False,
        source_or_configuration_promotion=False, archive_or_scientific_acceptance=False,
        original_JSON_or_parent_rewritten=False, generic_reader_or17_parent_scope_changed=False,
        separate_original_JSON_physical_package_entry_forbidden=True,
        future_package_index_and_isolated_restore_acceptance=False)
    expected.update(_fixed_history_saved_authorities("inventory13299", saved))
    need(exact_json(saved, expected), "Full saved fixed inventory history proof changed")
    expected_alias = dict(
        schema="exact-resource-aliases.v2", status=_HISTORY_ALIAS_STATUS,
        aliases=[dict(original=dict(_HISTORY_LEAF), archived=copy_receipt,
                      status="READONLY_BYTE_IDENTICAL_ALIAS", role=_HISTORY_ROLE)],
        historical_unresolved=[], separate_original_JSON_physical_package_entry_forbidden=True,
        scientific_or_source_or_archive_authorization=False)
    need(exact_json(alias_index, expected_alias), "Full fixed history byte alias index changed")
    return True


class InventoryHistoryOpaqueLeaf:
    """One fixed history DATA edge, authorized afresh before seen or any resolver."""

    def __init__(self, out, accepted_base):
        self.out = safe_path(out)
        self.active = accepted_base == _HISTORY_BASE
        self.directory = self.out / "opaque_inventory_history_bytes"
        self.observations = []
        self.parent_before = None
        self.authorities_before = None
        self.leaf_before = None
        self.copy_receipt = None
        self.copy_before = None
        self.directory_before = None

    @staticmethod
    def _regular(path):
        path = safe_path(path)
        metadata = stable_metadata(path)
        _history_metadata_shape(metadata, str(path), metadata["bytes"])
        return path, metadata

    def _inputs(self):
        need(self.active, "Fixed history leaf requires the exact accepted BaseA")
        parent, parent_before = self._regular(_HISTORY_BASE["path"])
        leaf, leaf_before = self._regular(_HISTORY_LEAF["path"])
        need(rec(parent) == _HISTORY_BASE and rec(leaf) == _HISTORY_LEAF,
             "Fixed history parent/original bytes changed")
        parent_bytes = parent.read_bytes()
        content = leaf.read_bytes()
        base = _strict_history_json(parent_bytes.decode("utf-8"))
        need(isinstance(base, dict) and base.get("schema") == "source-delivery-refresh.v3"
             and base.get("status") == "CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY"
             and type(base.get("source_issues")) is int and base["source_issues"] == 0
             and base.get("source_staged") is False,
             "Exact accepted BaseA history authority required")
        history = base.get("original_failure_history", {})
        need(history.get(_HISTORY_FIELD[1]) == _HISTORY_LEAF
             and history.get("original13297_failed_executing_source") == _HISTORY_PRODUCER
             and history.get("actual13297_software58_only") == _HISTORY_SOFTWARE,
             "Exact BaseA field and independent producer/software edges required")
        text = content.decode("utf-8")
        need(not SECRET_RE.search(text) and "-----BEGIN " + "OPENSSH PRIVATE KEY-----" not in text,
             "Potential credential in fixed diagnostic history DATA")
        inventory_history_document_shape(_strict_history_json(text))
        need(rec(parent) == _HISTORY_BASE and rec(leaf) == _HISTORY_LEAF
             and stable_metadata(parent) == parent_before and stable_metadata(leaf) == leaf_before,
             "Fixed history inputs changed during own-byte/shape readback")
        self._current_authorities = _fixed_history_mapping_inputs("inventory13299", base, parent_before)
        need(rec(parent) == _HISTORY_BASE and rec(leaf) == _HISTORY_LEAF
             and stable_metadata(parent) == parent_before and stable_metadata(leaf) == leaf_before,
             "Fixed history parent/leaf changed after the last mapping JSON read")
        return parent_before, leaf_before, content

    def _copy(self, content):
        self.directory.mkdir(mode=0o700, exist_ok=False)
        target = self.directory / (_HISTORY_LEAF["sha256"] + "_13299_diagnostic.OPAQUE.txt")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(target, flags, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o444)
            os.fsync(stream.fileno())
        self.copy_receipt = rec(target)
        need(fp(self.copy_receipt) == fp(_HISTORY_LEAF) and target.read_bytes() == content,
             "Fixed history opaque preservation changed bytes")
        unused, self.copy_before = self._regular(target)
        self.directory.chmod(0o555)
        fd = os.open(self.directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        self.directory_before = stable_metadata(self.directory)

    def edge(self, receipt, parent, trail, module):
        if not _inventory_history_matches(receipt):
            return None
        need(receipt == _HISTORY_LEAF, "Fixed inherited history requires exact leaf fulltuple")
        selected = _fixed_history_context("inventory13299", parent, trail, module)
        parent_before, leaf_before, content = self._inputs()
        if self.copy_receipt is None:
            self.parent_before, self.leaf_before = parent_before, leaf_before
            self.authorities_before = self._current_authorities
            self._copy(content)
        else:
            need(parent_before == self.parent_before and leaf_before == self.leaf_before,
                 "Repeated fixed history observation changed original metadata")
        self.readback()
        observation = dict(
            ordinal=len(self.observations), receipt=dict(_HISTORY_LEAF),
            parent_manifest=dict(selected["parent_manifest"]), field=list(trail), module=module,
            physical=self.copy_receipt,
            resolution_basis="EXACT_READONLY13299_DIAGNOSTIC_HISTORY_DATA_BYTECOPY", role=_HISTORY_ROLE)
        self.observations.append(observation)
        return dict(receipt=dict(_HISTORY_LEAF), parent=parent, field=list(trail), module=module,
                    physical=self.copy_receipt, resolution_basis=observation["resolution_basis"],
                    role=_HISTORY_ROLE, raw_bytes_preserved=True,
                    receipt_children_interpreted=False, source_or_configuration_promotion=False)

    def readback(self):
        need(self.copy_receipt is not None, "Fixed history DATA preservation has not occurred")
        parent_meta, leaf_meta, content = self._inputs()
        need(exact_json(self._current_authorities, self.authorities_before),
             "Fixed inherited history four-authority native metadata drifted")
        need(parent_meta == self.parent_before and leaf_meta == self.leaf_before,
             "Fixed history original/parent stable metadata drifted")
        copy_path, copy_meta = self._regular(self.copy_receipt["path"])
        need(_history_copy_structure(self.copy_receipt) == copy_path
             and copy_meta == self.copy_before and rec(copy_path) == self.copy_receipt
             and copy_path.read_bytes() == content and stable_metadata(copy_path) == self.copy_before,
             "Fixed history readonly copy bytes/metadata drifted")
        directory = safe_path(self.directory)
        directory_meta = stable_metadata(directory)
        _history_metadata_shape(directory_meta, str(directory), directory=True)
        need(directory_meta == self.directory_before
             and {p.name for p in directory.iterdir()} == {copy_path.name},
             "Fixed history555 directory metadata or exact one-file universe changed")
        return True

    def require_complete(self):
        if self.active:
            need(any(x["module"] == "default_workflow_integration" for x in self.observations),
                 "Actual source graph must observe the fixed default history edge")
            self.readback()
        else:
            need(not self.observations and self.copy_receipt is None,
                 "No inventory history exception outside exact BaseA")
        return self.active

    def alias_index(self):
        self.readback()
        return dict(
            schema="exact-resource-aliases.v2", status=_HISTORY_ALIAS_STATUS,
            aliases=[dict(original=dict(_HISTORY_LEAF), archived=self.copy_receipt,
                          status="READONLY_BYTE_IDENTICAL_ALIAS", role=_HISTORY_ROLE)],
            historical_unresolved=[], separate_original_JSON_physical_package_entry_forbidden=True,
            scientific_or_source_or_archive_authorization=False)

    def proof(self):
        need(self.require_complete(), "Actual fixed inventory history observations required")
        return dict(
            schema=_HISTORY_PROOF_SCHEMA, status=_HISTORY_PROOF_STATUS,
            parent_manifest=dict(_HISTORY_BASE), original_diagnostic_data=dict(_HISTORY_LEAF),
            source_field=list(_HISTORY_FIELD), role=_HISTORY_ROLE, allowed_modules=list(_HISTORY_MODULES),
            module_policy=dict(default_workflow_integration="FINITE_FIVE_ROWS_ACTUAL_RUNTIME_PARENT_FIELD_AUTHENTICATION_REQUIRED",
                               final_delivery_tools="PROSPECTIVE_SAME_FIVE_ROWS_NOT_REQUIRED"),
            preserved_opaque_data=self.copy_receipt,
            parent_metadata_before=self.parent_before,
            parent_metadata_after=stable_metadata(_HISTORY_BASE["path"]),
            original_metadata_before=self.leaf_before,
            original_metadata_after=stable_metadata(_HISTORY_LEAF["path"]),
            preserved_metadata=self.copy_before, copy_directory_metadata=self.directory_before,
            observations=list(self.observations), authorized_observation_n=len(self.observations),
            actual_default_observation_n=sum(x["module"] == "default_workflow_integration" for x in self.observations),
            actual_finaltools_observation_n=sum(x["module"] == "final_delivery_tools" for x in self.observations),
            embedded_parent_n=2, embedded_member_counts=[193, 395], embedded_observation_n=588,
            independent_source_producer=dict(_HISTORY_PRODUCER),
            independent_software_only_gate=dict(_HISTORY_SOFTWARE),
            independent_BaseA_history_fields_retained=True, original_bytes_and_metadata_unchanged=True,
            original_permission_unchanged=True, preserved_copy_readonly_fsynced_and_byte_identical=True,
            embedded_relative_targets_interpreted=False, member_paths_statted_or_opened=False,
            source_or_configuration_promotion=False, archive_or_scientific_acceptance=False,
            original_JSON_or_parent_rewritten=False, generic_reader_or17_parent_scope_changed=False,
            separate_original_JSON_physical_package_entry_forbidden=True,
            future_package_index_and_isolated_restore_acceptance=False,
            **_fixed_history_authority_projection("inventory13299", self.authorities_before))


def verify_inventory_history_preservation(saved, alias_index, allocation):
    """Current CPU live readback plus the pure validator; no generic reader callback."""
    inventory_history_proof_shape(saved, alias_index, allocation)
    copy_receipt = saved["preserved_opaque_data"]
    path = _history_copy_structure(copy_receipt)
    scope = InventoryHistoryOpaqueLeaf(path.parent.parent, _HISTORY_BASE)
    scope.parent_before = saved["parent_metadata_before"]
    scope.authorities_before = saved["authority_metadata_before"]
    scope.leaf_before = saved["original_metadata_before"]
    scope.copy_receipt = copy_receipt
    scope.copy_before = saved["preserved_metadata"]
    scope.directory_before = saved["copy_directory_metadata"]
    scope.observations = saved["observations"]
    scope.require_complete()
    pointer = saved["exact_alias_index"]
    index_path = verify(pointer, True)
    index_before = stable_metadata(index_path)
    need(rec(index_path) == pointer
         and exact_json(_strict_history_json(index_path.read_text()), alias_index),
         "Saved fixed inventory history alias bytes changed")
    expected = dict(scope.proof(), exact_alias_index=pointer, allocation=allocation)
    need(exact_json(saved, expected), "Current complete fixed inventory history proof differs")
    _fixed_history_authority_fence("inventory13299", scope.authorities_before)
    _fixed_history_native_union_sweep(_fixed_history_saved_native_records(saved) + [index_before])
    return True


# One immutable diagnostic history DATA object; embedded member records are not inputs.
_ARCHIVE_PARENT_HISTORY_BASE = dict(INHERITED_ENTRYPOINT_BASE)
_ARCHIVE_PARENT_HISTORY_AUTHORITY = "/lustre/users/u21111210118/projects/test9"
_ARCHIVE_PARENT_HISTORY_LEAF = {
    "path": str(R / "steps/24_benchmark_delivery/runs/source_v7_relative_context_diagnostic_13298/diagnostic.json"),
    "bytes": 50849,
    "sha256": "d680badfc6f11aefdbb88f673f3ac611766e87be7e3b2c5be7633ba886ff2a07",
}
_ARCHIVE_PARENT_HISTORY_FIELD = ("original_failure_history", "actual13298_archive_parent_diagnostic_only")
_ARCHIVE_PARENT_HISTORY_MODULES = ("default_workflow_integration", "final_delivery_tools")
_ARCHIVE_PARENT_HISTORY_ROLE = "EXACT13298_DIAGNOSTIC_ARCHIVE_PARENT_HISTORY_DATA_NOT_RECEIPT_SOURCE_OR_ARCHIVE_AUTHORIZATION"
_ARCHIVE_PARENT_HISTORY_PRODUCER = {
    "path": str(R / "steps/24_benchmark_delivery/frozen/source_refresh_relative_v7_13297/code/source_delivery_refresh_v7.py"),
    "bytes": 42275,
    "sha256": "c2e9bd2502edc353055b038d50bce79ae70ee92685df095d88cfb74fabe260b1",
}
_ARCHIVE_PARENT_HISTORY_SOFTWARE = {
    "path": str(R / "steps/24_benchmark_delivery/runs/source_relative_contracts_13297/acceptance.json"),
    "bytes": 2513,
    "sha256": "cd7c356bc2736b76d593426cade0438bcd404b3a5addc80da10aff8716d6b4f1",
}
_ARCHIVE_PARENT_HISTORY_MANIFEST = {
    "path": str(R / "archive/reconstruction_completed_modules_20261002.members.json"),
    "bytes": 45243,
    "sha256": "dae90d5f02faedeef24d887e6edf414b86fc63d268e54e58a6a0d558c08d3d6e",
}
_ARCHIVE_PARENT_HISTORY_FALSE_FLAGS = (
    "external_files_read", "source_staged", "default_changed", "formal_outputs_read",
)
_ARCHIVE_PARENT_HISTORY_TRUE_FLAGS = ()
_ARCHIVE_PARENT_HISTORY_TOP_KEYS = {
    "schema", "status", "slurm_job_id", "CPUs", "GPUs", "failed_source_job",
    "source_producer", "original_software_only_acceptance", "diagnostic",
    "external_files_read", "source_staged", "default_changed", "formal_outputs_read",
}
_ARCHIVE_PARENT_HISTORY_DIAGNOSTIC_KEYS = {
    "parent", "parent_relative_to_authority", "source_field", "offending_receipt",
    "parent_JSON", "error_type", "error",
}
_ARCHIVE_PARENT_HISTORY_PROOF_SCHEMA = "exact13298-archive-parent-diagnostic-history-data-leaf.v2"
_ARCHIVE_PARENT_HISTORY_PROOF_STATUS = "EXACT_BASEA_ARCHIVE_PARENT_HISTORY_CONTEXTS_AND13298_DIAGNOSTIC_DATA_BYTES_PRESERVED_CPU_VERIFIED"
_ARCHIVE_PARENT_HISTORY_ALIAS_STATUS = "EXACT13298_DIAGNOSTIC_ARCHIVE_PARENT_HISTORY_DATA_BYTE_ALIAS_CPU_VERIFIED"
_ARCHIVE_PARENT_HISTORY_META_KEYS = {"path", "bytes", "inode", "mtime_ns", "ctime_ns", "mode", "dev", "nlink", "uid", "gid"}


def _strict_archive_parent_history_json(raw):
    def pairs(items):
        result = {}
        for name, value in items:
            need(name not in result, "Duplicate key in fixed inventory history JSON")
            result[name] = value
        return result

    def constant(value):
        raise ValueError("Nonfinite fixed inventory history JSON number: " + value)

    def number(value):
        result = float(value)
        need(result == result and abs(result) != float("inf"),
             "Nonfinite fixed inventory history JSON exponent")
        return result

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant, parse_float=number)


def _archive_parent_history_matches(receipt):
    receipt_shape(receipt)
    return receipt["path"] == _ARCHIVE_PARENT_HISTORY_LEAF["path"] or fp(receipt) == fp(_ARCHIVE_PARENT_HISTORY_LEAF)


def reject_archive_parent_history_declaration(receipt):
    need(not _archive_parent_history_matches(receipt),
         "Fixed13298 diagnostic DATA cannot be direct SOURCE/gate/seed/context/Plan alias")


def archive_parent_history_document_shape(obj):
    """Pure DATA validation; embedded namespace strings never become file receipts."""
    need(isinstance(obj, dict) and set(obj) == _ARCHIVE_PARENT_HISTORY_TOP_KEYS
         and obj["schema"] == "source-v7-relative-context-diagnostic-only.v1"
         and obj["status"] == "EXACT_RELATIVE_PARENT_DIAGNOSED_STRICT_GUARD_UNCHANGED_NOT_SOURCE_ACCEPTANCE",
         "Exact nonauthorizing13298 diagnostic schema/status/thirteen keys required")
    need(obj["slurm_job_id"] == "13298" and obj["failed_source_job"] == "13297"
         and type(obj["CPUs"]) is int and obj["CPUs"] == 1
         and type(obj["GPUs"]) is int and obj["GPUs"] == 0,
         "Fixed13298 diagnostic identity/CPU-only declaration changed")
    need(all(obj[k] is False for k in _ARCHIVE_PARENT_HISTORY_FALSE_FLAGS),
         "Fixed archive-parent diagnostic must remain nonauthorizing history")
    need(obj["source_producer"] == _ARCHIVE_PARENT_HISTORY_PRODUCER
         and obj["original_software_only_acceptance"] == _ARCHIVE_PARENT_HISTORY_SOFTWARE,
         "Fixed13298 producer/software observations changed")
    diagnostic = obj["diagnostic"]
    need(isinstance(diagnostic, dict)
         and set(diagnostic) == _ARCHIVE_PARENT_HISTORY_DIAGNOSTIC_KEYS
         and diagnostic["parent"] == _ARCHIVE_PARENT_HISTORY_MANIFEST
         and diagnostic["parent_relative_to_authority"] == "archive/reconstruction_completed_modules_20261002.members.json"
         and diagnostic["source_field"] == ["members", "192"]
         and diagnostic["error_type"] == "ValueError"
         and diagnostic["error"] == "Unknown relative receipt parent",
         "Exact documentary13298 archive-parent/error context required")
    declared = diagnostic["parent_JSON"]
    need(isinstance(declared, dict)
         and set(declared) == {"archive", "archive_bytes", "archive_sha256", "member_count", "members",
                               "validation_run", "scope_counts", "base_package", "excluded_ongoing_modules"}
         and type(declared["member_count"]) is int and declared["member_count"] == 193
         and isinstance(declared["members"], list) and len(declared["members"]) == 193,
         "Fixed193-member diagnostic metadata snapshot changed")
    need(isinstance(declared["archive"], str) and bool(declared["archive"])
         and type(declared["archive_bytes"]) is int and declared["archive_bytes"] >= 0
         and isinstance(declared["archive_sha256"], str)
         and re.fullmatch("[0-9a-f]{64}", declared["archive_sha256"]) is not None
         and isinstance(declared["validation_run"], str) and bool(declared["validation_run"])
         and isinstance(declared["scope_counts"], dict)
         and all(isinstance(k, str) and type(v) is int and v >= 0
                 for k, v in declared["scope_counts"].items())
         and isinstance(declared["base_package"], dict)
         and set(declared["base_package"]) == {"archive", "sha256", "members_index", "members_index_sha256",
                                             "restore_receipt", "restore_receipt_sha256"}
         and all(isinstance(v, str) and bool(v) for v in declared["base_package"].values())
         and declared["excluded_ongoing_modules"] == [],
         "Fixed archive snapshot scalar provenance shape changed")
    # Do not call receipt_shape, Path, safe_path, normalize_edge or any filesystem API here.
    paths = []
    for member in declared["members"]:
        need(isinstance(member, dict) and set(member) == {"path", "bytes", "sha256"}
             and isinstance(member["path"], str) and bool(member["path"])
             and type(member["bytes"]) is int and member["bytes"] >= 0
             and isinstance(member["sha256"], str)
             and re.fullmatch("[0-9a-f]{64}", member["sha256"]) is not None,
             "Fixed diagnostic member scalar metadata shape changed")
        paths.append(member["path"])
    need(len(set(paths)) == 193
         and exact_json(diagnostic["offending_receipt"], declared["members"][192]),
         "Fixed member192 documentary observation changed")
    return True


def _archive_parent_history_metadata_shape(value, expected_path, size=None, directory=False):
    """Pure metadata shape validation; independently enforce444 files or555 directory."""
    need(isinstance(value, dict) and set(value) == _ARCHIVE_PARENT_HISTORY_META_KEYS
         and value.get("path") == expected_path
         and all(type(value[k]) is int and value[k] >= 0 for k in _ARCHIVE_PARENT_HISTORY_META_KEYS - {"path"}),
         "Exact integer fixed inventory history metadata required")
    if directory:
        need(stat.S_ISDIR(value["mode"]) and stat.S_IMODE(value["mode"]) == 0o555
             and value["nlink"] == 2,
             "Fixed history copy directory must independently be readonly0555")
    else:
        need(stat.S_ISREG(value["mode"]) and stat.S_IMODE(value["mode"]) == 0o444
             and value["nlink"] == 1 and value["bytes"] == size,
             "Fixed history input/copy must be readonly0444 single-link regular")
    return value


def _archive_parent_history_copy_structure(receipt):
    receipt_shape(receipt)
    need(set(receipt) == {"path", "bytes", "sha256"} and fp(receipt) == fp(_ARCHIVE_PARENT_HISTORY_LEAF),
         "Fixed history copy must preserve the exact full byte identity")
    raw = receipt["path"]
    path = Path(raw)
    need(path.is_absolute() and path.is_relative_to(Path(_ARCHIVE_PARENT_HISTORY_AUTHORITY))
         and all(part not in ("", ".", "..") for part in raw.split("/")[1:])
         and path.name == _ARCHIVE_PARENT_HISTORY_LEAF["sha256"] + "_13298_diagnostic.OPAQUE.txt"
         and path.parent.name == "opaque_archive_parent_history_bytes",
         "Exact fixed history preservation path required")
    return path


def _archive_parent_history_control_metadata(path):
    path = safe_path(path)
    need(path.name in {"archive_parent_history_opaque_aliases.json",
                       "archive_parent_history_opaque_leaf_proof.json"},
         "Only the two fixed13298 output controls are permitted")
    metadata = stable_metadata(path)
    _archive_parent_history_metadata_shape(metadata, str(path), metadata["bytes"])
    return metadata


def _archive_parent_history_control_readback(receipt, expected_metadata=None):
    receipt_shape(receipt)
    path = safe_path(receipt["path"])
    before = _archive_parent_history_control_metadata(path)
    if expected_metadata is not None:
        need(exact_json(before, expected_metadata), "Fixed13298 control native metadata drifted")
    need(rec(path) == receipt, "Fixed13298 control whole bytes changed")
    content = path.read_bytes()
    obj = _strict_archive_parent_history_json(content.decode("utf-8"))
    # This full readback is intentionally AFTER the final own JSON read/parse.
    need(rec(path) == receipt and stable_metadata(path) == before,
         "Fixed13298 control changed during own JSON readback")
    _archive_parent_history_control_metadata(path)
    return obj, before


def _archive_parent_history_write_control(path, obj):
    path = safe_path(path)
    need(path.name in {"archive_parent_history_opaque_aliases.json",
                       "archive_parent_history_opaque_leaf_proof.json"},
         "Only the two fixed13298 output controls are permitted")
    content = (json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
        os.fchmod(stream.fileno(), 0o444)
        os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    receipt = rec(path)
    metadata = _archive_parent_history_control_metadata(path)
    actual, unused = _archive_parent_history_control_readback(receipt, metadata)
    need(exact_json(actual, obj) and path.read_bytes() == content
         and stable_metadata(path) == metadata,
         "Fixed13298 control exclusive fsync publication changed")
    return receipt, metadata


def archive_parent_history_proof_shape(saved, alias_index, allocation):
    """Pure strict validator for later INDEX-only replay; performs no filesystem calls."""
    need(isinstance(saved, dict) and isinstance(alias_index, dict) and isinstance(allocation, dict),
         "Full fixed history proof/index/allocation objects required")
    copy_receipt = saved.get("preserved_opaque_data")
    path = _archive_parent_history_copy_structure(copy_receipt)
    out = path.parent.parent
    pointer = receipt_shape(saved.get("exact_alias_index"))
    need(set(pointer) == {"path", "bytes", "sha256"}
         and pointer["path"] == str(out / "archive_parent_history_opaque_aliases.json"),
         "Fixed history proof/index pointer changed")
    need(isinstance(allocation.get("job_id"), str) and allocation["job_id"].isdigit()
         and type(allocation.get("allocated_CPUs")) is int and allocation["allocated_CPUs"] >= 1
         and type(allocation.get("allocated_gpus")) is int and allocation["allocated_gpus"] == 0,
         "Actual CPU allocation object required for fixed history proof")
    observations = saved.get("observations")
    need(isinstance(observations, list) and observations, "Actual ordered history observations required")
    expected_observations = []
    for index, observation in enumerate(observations):
        need(isinstance(observation, dict) and observation.get("module") in _ARCHIVE_PARENT_HISTORY_MODULES,
             "Unknown fixed history observation module")
        selected = _fixed_history_observation_context("archive13298", observation)
        expected_observations.append(dict(
            ordinal=index, receipt=dict(_ARCHIVE_PARENT_HISTORY_LEAF), parent_manifest=dict(selected["parent_manifest"]),
            field=list(selected["field"]), module=observation["module"], physical=copy_receipt,
            resolution_basis="EXACT_READONLY13298_DIAGNOSTIC_ARCHIVE_PARENT_HISTORY_DATA_BYTECOPY", role=_ARCHIVE_PARENT_HISTORY_ROLE))
    need(exact_json(observations, expected_observations),
         "Full ordered fixed history observation context changed")
    actual_default = sum(x["module"] == "default_workflow_integration" for x in observations)
    actual_prospective = sum(x["module"] == "final_delivery_tools" for x in observations)
    need(actual_default >= 1, "At least one actual default history edge must be observed")
    parent_meta = _archive_parent_history_metadata_shape(saved.get("parent_metadata_before"), _ARCHIVE_PARENT_HISTORY_BASE["path"],
                                          _ARCHIVE_PARENT_HISTORY_BASE["bytes"])
    leaf_meta = _archive_parent_history_metadata_shape(saved.get("original_metadata_before"), _ARCHIVE_PARENT_HISTORY_LEAF["path"],
                                        _ARCHIVE_PARENT_HISTORY_LEAF["bytes"])
    copy_meta = _archive_parent_history_metadata_shape(saved.get("preserved_metadata"), str(path), copy_receipt["bytes"])
    directory_meta = _archive_parent_history_metadata_shape(saved.get("copy_directory_metadata"), str(path.parent),
                                             directory=True)
    expected = dict(
        schema=_ARCHIVE_PARENT_HISTORY_PROOF_SCHEMA, status=_ARCHIVE_PARENT_HISTORY_PROOF_STATUS,
        parent_manifest=dict(_ARCHIVE_PARENT_HISTORY_BASE), original_diagnostic_data=dict(_ARCHIVE_PARENT_HISTORY_LEAF),
        source_field=list(_ARCHIVE_PARENT_HISTORY_FIELD), role=_ARCHIVE_PARENT_HISTORY_ROLE,
        allowed_modules=list(_ARCHIVE_PARENT_HISTORY_MODULES),
        module_policy=dict(default_workflow_integration="FINITE_FIVE_ROWS_ACTUAL_RUNTIME_PARENT_FIELD_AUTHENTICATION_REQUIRED",
                           final_delivery_tools="PROSPECTIVE_SAME_FIVE_ROWS_NOT_REQUIRED"),
        preserved_opaque_data=copy_receipt, exact_alias_index=pointer, allocation=allocation,
        parent_metadata_before=parent_meta, parent_metadata_after=parent_meta,
        original_metadata_before=leaf_meta, original_metadata_after=leaf_meta,
        preserved_metadata=copy_meta, copy_directory_metadata=directory_meta,
        observations=expected_observations, authorized_observation_n=len(observations),
        actual_default_observation_n=actual_default, actual_finaltools_observation_n=actual_prospective,
        embedded_parent_n=1, embedded_member_counts=[193], embedded_observation_n=193,
        independent_source_producer=dict(_ARCHIVE_PARENT_HISTORY_PRODUCER),
        independent_software_only_gate=dict(_ARCHIVE_PARENT_HISTORY_SOFTWARE),
        independent_BaseA_history_fields_retained=True,
        original_bytes_and_metadata_unchanged=True, original_permission_unchanged=True,
        preserved_copy_readonly_fsynced_and_byte_identical=True,
        embedded_relative_targets_interpreted=False, member_paths_statted_or_opened=False,
        source_or_configuration_promotion=False, archive_or_scientific_acceptance=False,
        original_JSON_or_parent_rewritten=False, generic_reader_or17_parent_scope_changed=False,
        separate_original_JSON_physical_package_entry_forbidden=True,
        future_package_index_and_isolated_restore_acceptance=False)
    expected.update(_fixed_history_saved_authorities("archive13298", saved))
    need(exact_json(saved, expected), "Full saved fixed inventory history proof changed")
    expected_alias = dict(
        schema="exact-resource-aliases.v2", status=_ARCHIVE_PARENT_HISTORY_ALIAS_STATUS,
        aliases=[dict(original=dict(_ARCHIVE_PARENT_HISTORY_LEAF), archived=copy_receipt,
                      status="READONLY_BYTE_IDENTICAL_ALIAS", role=_ARCHIVE_PARENT_HISTORY_ROLE)],
        historical_unresolved=[], separate_original_JSON_physical_package_entry_forbidden=True,
        scientific_or_source_or_archive_authorization=False)
    need(exact_json(alias_index, expected_alias), "Full fixed history byte alias index changed")
    return True


class ArchiveParentHistoryOpaqueLeaf:
    """One fixed history DATA edge, authorized afresh before seen or any resolver."""

    def __init__(self, out, accepted_base):
        self.out = safe_path(out)
        self.active = accepted_base == _ARCHIVE_PARENT_HISTORY_BASE
        self.directory = self.out / "opaque_archive_parent_history_bytes"
        self.observations = []
        self.parent_before = None
        self.authorities_before = None
        self.leaf_before = None
        self.copy_receipt = None
        self.copy_before = None
        self.directory_before = None

    @staticmethod
    def _regular(path):
        path = safe_path(path)
        metadata = stable_metadata(path)
        _archive_parent_history_metadata_shape(metadata, str(path), metadata["bytes"])
        return path, metadata

    def _inputs(self):
        need(self.active, "Fixed history leaf requires the exact accepted BaseA")
        parent, parent_before = self._regular(_ARCHIVE_PARENT_HISTORY_BASE["path"])
        leaf, leaf_before = self._regular(_ARCHIVE_PARENT_HISTORY_LEAF["path"])
        need(rec(parent) == _ARCHIVE_PARENT_HISTORY_BASE and rec(leaf) == _ARCHIVE_PARENT_HISTORY_LEAF,
             "Fixed history parent/original bytes changed")
        parent_bytes = parent.read_bytes()
        content = leaf.read_bytes()
        base = _strict_archive_parent_history_json(parent_bytes.decode("utf-8"))
        need(isinstance(base, dict) and base.get("schema") == "source-delivery-refresh.v3"
             and base.get("status") == "CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY"
             and type(base.get("source_issues")) is int and base["source_issues"] == 0
             and base.get("source_staged") is False,
             "Exact accepted BaseA history authority required")
        history = base.get("original_failure_history", {})
        need(history.get(_ARCHIVE_PARENT_HISTORY_FIELD[1]) == _ARCHIVE_PARENT_HISTORY_LEAF
             and history.get("original13297_failed_executing_source") == _ARCHIVE_PARENT_HISTORY_PRODUCER
             and history.get("actual13297_software58_only") == _ARCHIVE_PARENT_HISTORY_SOFTWARE,
             "Exact BaseA field and independent producer/software edges required")
        text = content.decode("utf-8")
        need(not SECRET_RE.search(text) and "-----BEGIN " + "OPENSSH PRIVATE KEY-----" not in text,
             "Potential credential in fixed diagnostic history DATA")
        archive_parent_history_document_shape(_strict_archive_parent_history_json(text))
        need(rec(parent) == _ARCHIVE_PARENT_HISTORY_BASE and rec(leaf) == _ARCHIVE_PARENT_HISTORY_LEAF
             and stable_metadata(parent) == parent_before and stable_metadata(leaf) == leaf_before,
             "Fixed history inputs changed during own-byte/shape readback")
        self._current_authorities = _fixed_history_mapping_inputs("archive13298", base, parent_before)
        need(rec(parent) == _ARCHIVE_PARENT_HISTORY_BASE and rec(leaf) == _ARCHIVE_PARENT_HISTORY_LEAF
             and stable_metadata(parent) == parent_before and stable_metadata(leaf) == leaf_before,
             "Fixed history parent/leaf changed after the last mapping JSON read")
        return parent_before, leaf_before, content

    def _copy(self, content):
        self.directory.mkdir(mode=0o700, exist_ok=False)
        target = self.directory / (_ARCHIVE_PARENT_HISTORY_LEAF["sha256"] + "_13298_diagnostic.OPAQUE.txt")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(target, flags, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o444)
            os.fsync(stream.fileno())
        self.copy_receipt = rec(target)
        need(fp(self.copy_receipt) == fp(_ARCHIVE_PARENT_HISTORY_LEAF) and target.read_bytes() == content,
             "Fixed history opaque preservation changed bytes")
        unused, self.copy_before = self._regular(target)
        self.directory.chmod(0o555)
        fd = os.open(self.directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        self.directory_before = stable_metadata(self.directory)

    def edge(self, receipt, parent, trail, module):
        if not _archive_parent_history_matches(receipt):
            return None
        need(receipt == _ARCHIVE_PARENT_HISTORY_LEAF, "Fixed inherited history requires exact leaf fulltuple")
        selected = _fixed_history_context("archive13298", parent, trail, module)
        parent_before, leaf_before, content = self._inputs()
        if self.copy_receipt is None:
            self.parent_before, self.leaf_before = parent_before, leaf_before
            self.authorities_before = self._current_authorities
            self._copy(content)
        else:
            need(parent_before == self.parent_before and leaf_before == self.leaf_before,
                 "Repeated fixed history observation changed original metadata")
        self.readback()
        observation = dict(
            ordinal=len(self.observations), receipt=dict(_ARCHIVE_PARENT_HISTORY_LEAF),
            parent_manifest=dict(selected["parent_manifest"]), field=list(trail), module=module,
            physical=self.copy_receipt,
            resolution_basis="EXACT_READONLY13298_DIAGNOSTIC_ARCHIVE_PARENT_HISTORY_DATA_BYTECOPY", role=_ARCHIVE_PARENT_HISTORY_ROLE)
        self.observations.append(observation)
        return dict(receipt=dict(_ARCHIVE_PARENT_HISTORY_LEAF), parent=parent, field=list(trail), module=module,
                    physical=self.copy_receipt, resolution_basis=observation["resolution_basis"],
                    role=_ARCHIVE_PARENT_HISTORY_ROLE, raw_bytes_preserved=True,
                    receipt_children_interpreted=False, source_or_configuration_promotion=False)

    def readback(self):
        need(self.copy_receipt is not None, "Fixed history DATA preservation has not occurred")
        parent_meta, leaf_meta, content = self._inputs()
        need(exact_json(self._current_authorities, self.authorities_before),
             "Fixed inherited history four-authority native metadata drifted")
        need(parent_meta == self.parent_before and leaf_meta == self.leaf_before,
             "Fixed history original/parent stable metadata drifted")
        copy_path, copy_meta = self._regular(self.copy_receipt["path"])
        need(_archive_parent_history_copy_structure(self.copy_receipt) == copy_path
             and copy_meta == self.copy_before and rec(copy_path) == self.copy_receipt
             and copy_path.read_bytes() == content and stable_metadata(copy_path) == self.copy_before,
             "Fixed history readonly copy bytes/metadata drifted")
        directory = safe_path(self.directory)
        directory_meta = stable_metadata(directory)
        _archive_parent_history_metadata_shape(directory_meta, str(directory), directory=True)
        need(directory_meta == self.directory_before
             and {p.name for p in directory.iterdir()} == {copy_path.name},
             "Fixed history555 directory metadata or exact one-file universe changed")
        return True

    def require_complete(self):
        if self.active:
            need(any(x["module"] == "default_workflow_integration" for x in self.observations),
                 "Actual source graph must observe the fixed default history edge")
            self.readback()
        else:
            need(not self.observations and self.copy_receipt is None,
                 "No inventory history exception outside exact BaseA")
        return self.active

    def alias_index(self):
        self.readback()
        return dict(
            schema="exact-resource-aliases.v2", status=_ARCHIVE_PARENT_HISTORY_ALIAS_STATUS,
            aliases=[dict(original=dict(_ARCHIVE_PARENT_HISTORY_LEAF), archived=self.copy_receipt,
                          status="READONLY_BYTE_IDENTICAL_ALIAS", role=_ARCHIVE_PARENT_HISTORY_ROLE)],
            historical_unresolved=[], separate_original_JSON_physical_package_entry_forbidden=True,
            scientific_or_source_or_archive_authorization=False)

    def proof(self):
        need(self.require_complete(), "Actual fixed inventory history observations required")
        return dict(
            schema=_ARCHIVE_PARENT_HISTORY_PROOF_SCHEMA, status=_ARCHIVE_PARENT_HISTORY_PROOF_STATUS,
            parent_manifest=dict(_ARCHIVE_PARENT_HISTORY_BASE), original_diagnostic_data=dict(_ARCHIVE_PARENT_HISTORY_LEAF),
            source_field=list(_ARCHIVE_PARENT_HISTORY_FIELD), role=_ARCHIVE_PARENT_HISTORY_ROLE, allowed_modules=list(_ARCHIVE_PARENT_HISTORY_MODULES),
            module_policy=dict(default_workflow_integration="FINITE_FIVE_ROWS_ACTUAL_RUNTIME_PARENT_FIELD_AUTHENTICATION_REQUIRED",
                               final_delivery_tools="PROSPECTIVE_SAME_FIVE_ROWS_NOT_REQUIRED"),
            preserved_opaque_data=self.copy_receipt,
            parent_metadata_before=self.parent_before,
            parent_metadata_after=stable_metadata(_ARCHIVE_PARENT_HISTORY_BASE["path"]),
            original_metadata_before=self.leaf_before,
            original_metadata_after=stable_metadata(_ARCHIVE_PARENT_HISTORY_LEAF["path"]),
            preserved_metadata=self.copy_before, copy_directory_metadata=self.directory_before,
            observations=list(self.observations), authorized_observation_n=len(self.observations),
            actual_default_observation_n=sum(x["module"] == "default_workflow_integration" for x in self.observations),
            actual_finaltools_observation_n=sum(x["module"] == "final_delivery_tools" for x in self.observations),
            embedded_parent_n=1, embedded_member_counts=[193], embedded_observation_n=193,
            independent_source_producer=dict(_ARCHIVE_PARENT_HISTORY_PRODUCER),
            independent_software_only_gate=dict(_ARCHIVE_PARENT_HISTORY_SOFTWARE),
            independent_BaseA_history_fields_retained=True, original_bytes_and_metadata_unchanged=True,
            original_permission_unchanged=True, preserved_copy_readonly_fsynced_and_byte_identical=True,
            embedded_relative_targets_interpreted=False, member_paths_statted_or_opened=False,
            source_or_configuration_promotion=False, archive_or_scientific_acceptance=False,
            original_JSON_or_parent_rewritten=False, generic_reader_or17_parent_scope_changed=False,
            separate_original_JSON_physical_package_entry_forbidden=True,
            future_package_index_and_isolated_restore_acceptance=False,
            **_fixed_history_authority_projection("archive13298", self.authorities_before))


def verify_archive_parent_history_preservation(saved, alias_index, allocation):
    """Current owned-CPU object verifier; pure validator remains separately usable."""
    archive_parent_history_proof_shape(saved, alias_index, allocation)
    pointer = saved["exact_alias_index"]
    actual_index, index_before = _archive_parent_history_control_readback(pointer)
    need(exact_json(actual_index, alias_index), "Saved fixed archive-parent alias object differs")
    copy_receipt = saved["preserved_opaque_data"]
    path = _archive_parent_history_copy_structure(copy_receipt)
    scope = ArchiveParentHistoryOpaqueLeaf(path.parent.parent, _ARCHIVE_PARENT_HISTORY_BASE)
    scope.parent_before = saved["parent_metadata_before"]
    scope.authorities_before = saved["authority_metadata_before"]
    scope.leaf_before = saved["original_metadata_before"]
    scope.copy_receipt = copy_receipt
    scope.copy_before = saved["preserved_metadata"]
    scope.directory_before = saved["copy_directory_metadata"]
    scope.observations = saved["observations"]
    scope.require_complete()
    expected = dict(scope.proof(), exact_alias_index=pointer, allocation=allocation)
    need(exact_json(saved, expected), "Current complete fixed archive-parent history proof differs")
    final_index, unused = _archive_parent_history_control_readback(pointer, index_before)
    need(exact_json(final_index, alias_index), "Saved fixed archive-parent alias changed after inputs")
    _fixed_history_authority_fence("archive13298", scope.authorities_before)
    _fixed_history_native_union_sweep(_fixed_history_saved_native_records(saved) + [index_before])
    return True


# One immutable diagnostic history DATA object; embedded member records are not inputs.
_RELATIVE_DIAGNOSTIC_HISTORY_BASE = dict(INHERITED_ENTRYPOINT_BASE)
_RELATIVE_DIAGNOSTIC_HISTORY_AUTHORITY = "/lustre/users/u21111210118/projects/test9"
_RELATIVE_DIAGNOSTIC_HISTORY_LEAF = {
    "path": str(R / "steps/24_benchmark_delivery/runs/source_v6_relative_context_diagnostic_13295/diagnostic.json"),
    "bytes": 4407,
    "sha256": "e1a3efe660dab843d37c8d216df927927d79ec8e5186cf9249a742ec328812be",
}
_RELATIVE_DIAGNOSTIC_HISTORY_FIELD = ("original_failure_history", "actual13295_relative_diagnostic_only")
_RELATIVE_DIAGNOSTIC_HISTORY_MODULES = ("default_workflow_integration", "final_delivery_tools")
_RELATIVE_DIAGNOSTIC_HISTORY_ROLE = "EXACT13295_RELATIVE_DIAGNOSTIC_HISTORY_DATA_NOT_RECEIPT_SOURCE_OR_RECOVERY_AUTHORIZATION"
_RELATIVE_DIAGNOSTIC_HISTORY_PRODUCER = {
    "path": str(R / "steps/24_benchmark_delivery/frozen/source_refresh_relative_v6_13293/code/source_delivery_refresh_v6.py"),
    "bytes": 33958,
    "sha256": "0538c38223bafa65949b33f8d33961e0fb66fc09d83f904a805d0ec742b4633d",
}
_RELATIVE_DIAGNOSTIC_HISTORY_SOFTWARE = {
    "path": str(R / "steps/24_benchmark_delivery/runs/source_relative_contracts_13293/acceptance.json"),
    "bytes": 2513,
    "sha256": "81871930a6f6b356c5901e66ab18de99f6e012c7233cc96cec22413cca1e4a48",
}
_RELATIVE_DIAGNOSTIC_HISTORY_RECOVERED_PARENT = {
    "path": str(R / "01_raw/recovered_inputs/candidate_recovery_receipt.json"),
    "bytes": 2528,
    "sha256": "6398ad0dfafeb272c4bdfef6ce0a01ed14ebe526f1a2765ffbdd46dfe9b4e66c",
}
_RELATIVE_DIAGNOSTIC_HISTORY_FILE_NAMES = (
    "session_record_6378_stdout.txt", "session_record_7006_stdout.txt",
    "session_record_7013_partial_control_stdout.txt", "recovered_three_candidates.json",
    "public_source_inventory_5001.json",
)
_RELATIVE_DIAGNOSTIC_HISTORY_RECORD_NUMBERS = (6378, 7006, 7013)
_RELATIVE_DIAGNOSTIC_HISTORY_FALSE_FLAGS = (
    "external_files_read", "source_staged", "default_changed", "formal_outputs_read",
)
_RELATIVE_DIAGNOSTIC_HISTORY_TRUE_FLAGS = ()
_RELATIVE_DIAGNOSTIC_HISTORY_TOP_KEYS = {
    "schema", "status", "slurm_job_id", "CPUs", "GPUs", "failed_source_job",
    "source_producer", "original_software_only_acceptance", "diagnostic",
    "external_files_read", "source_staged", "default_changed", "formal_outputs_read",
}
_RELATIVE_DIAGNOSTIC_HISTORY_DIAGNOSTIC_KEYS = {
    "parent", "parent_relative_to_authority", "source_field", "offending_receipt",
    "parent_JSON", "error_type", "error",
}
_RELATIVE_DIAGNOSTIC_HISTORY_PROOF_SCHEMA = "exact13295-relative-diagnostic-history-data-leaf.v2"
_RELATIVE_DIAGNOSTIC_HISTORY_PROOF_STATUS = "EXACT_BASEA_RELATIVE_DIAGNOSTIC_HISTORY_CONTEXTS_AND13295_DATA_BYTES_PRESERVED_CPU_VERIFIED"
_RELATIVE_DIAGNOSTIC_HISTORY_ALIAS_STATUS = "EXACT13295_RELATIVE_DIAGNOSTIC_HISTORY_DATA_BYTE_ALIAS_CPU_VERIFIED"
_RELATIVE_DIAGNOSTIC_HISTORY_META_KEYS = {"path", "bytes", "inode", "mtime_ns", "ctime_ns", "mode", "dev", "nlink", "uid", "gid"}


def _strict_relative_diagnostic_history_json(raw):
    def pairs(items):
        result = {}
        for name, value in items:
            need(name not in result, "Duplicate key in fixed inventory history JSON")
            result[name] = value
        return result

    def constant(value):
        raise ValueError("Nonfinite fixed inventory history JSON number: " + value)

    def number(value):
        result = float(value)
        need(result == result and abs(result) != float("inf"),
             "Nonfinite fixed inventory history JSON exponent")
        return result

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant, parse_float=number)


def _relative_diagnostic_history_matches(receipt):
    receipt_shape(receipt)
    return receipt["path"] == _RELATIVE_DIAGNOSTIC_HISTORY_LEAF["path"] or fp(receipt) == fp(_RELATIVE_DIAGNOSTIC_HISTORY_LEAF)


def reject_relative_diagnostic_history_declaration(receipt):
    need(not _relative_diagnostic_history_matches(receipt),
         "Fixed13295 diagnostic DATA cannot be direct SOURCE/gate/seed/context/Plan alias")


def relative_diagnostic_history_document_shape(obj):
    """Pure own-DATA shape: embedded file/session strings never become target receipts."""
    need(isinstance(obj, dict) and set(obj) == _RELATIVE_DIAGNOSTIC_HISTORY_TOP_KEYS
         and obj["schema"] == "source-v6-relative-context-diagnostic-only.v1"
         and obj["status"] == "EXACT_RELATIVE_PARENT_DIAGNOSED_STRICT_GUARD_UNCHANGED_NOT_SOURCE_ACCEPTANCE",
         "Exact nonauthorizing13295 diagnostic schema/status/thirteen keys required")
    need(obj["slurm_job_id"] == "13295" and obj["failed_source_job"] == "13293"
         and type(obj["CPUs"]) is int and obj["CPUs"] == 1
         and type(obj["GPUs"]) is int and obj["GPUs"] == 0,
         "Fixed13295 diagnostic identity/CPU-only declaration changed")
    need(all(obj[k] is False for k in _RELATIVE_DIAGNOSTIC_HISTORY_FALSE_FLAGS),
         "Fixed relative diagnostic must remain nonauthorizing history")
    need(obj["source_producer"] == _RELATIVE_DIAGNOSTIC_HISTORY_PRODUCER
         and obj["original_software_only_acceptance"] == _RELATIVE_DIAGNOSTIC_HISTORY_SOFTWARE,
         "Fixed13295 producer/software observations changed")
    diagnostic = obj["diagnostic"]
    need(isinstance(diagnostic, dict) and set(diagnostic) == _RELATIVE_DIAGNOSTIC_HISTORY_DIAGNOSTIC_KEYS
         and diagnostic["parent"] == _RELATIVE_DIAGNOSTIC_HISTORY_RECOVERED_PARENT
         and diagnostic["parent_relative_to_authority"] == "01_raw/recovered_inputs/candidate_recovery_receipt.json"
         and diagnostic["source_field"] == ["files", "4"]
         and diagnostic["error_type"] == "ValueError"
         and diagnostic["error"] == "Unknown relative receipt parent",
         "Exact documentary13295 recovered-parent/error context required")
    declared = diagnostic["parent_JSON"]
    need(isinstance(declared, dict) and set(declared) == {
             "schema_version", "session_id", "source_session_file", "recovery_type", "records", "files"}
         and type(declared["schema_version"]) is int and declared["schema_version"] == 1
         and declared["session_id"] == "01a0bdc5-988d-70c1-8346-f463d4989fa2"
         and declared["source_session_file"] == "/Users/yangzijian/.codex/sessions/2026/09/20/rollout-2026-09-20T15-43-58-01a0bdc5-988d-70c1-8346-f463d4989fa2.jsonl"
         and declared["recovery_type"] == "byte_preserving_evidence_extraction_no_new_scientific_inference"
         and isinstance(declared["records"], list) and len(declared["records"]) == 3
         and isinstance(declared["files"], list) and len(declared["files"]) == 5,
         "Fixed three-record/five-file diagnostic metadata snapshot changed")
    # These scalar observations are NEVER passed to receipt_shape, Path or any I/O API.
    paths = []
    for value in declared["files"]:
        need(isinstance(value, dict) and set(value) == {"path", "bytes", "sha256"}
             and isinstance(value["path"], str) and bool(value["path"])
             and type(value["bytes"]) is int and value["bytes"] >= 0
             and isinstance(value["sha256"], str)
             and re.fullmatch("[0-9a-f]{64}", value["sha256"]) is not None,
             "Fixed diagnostic file scalar metadata shape changed")
        paths.append(value["path"])
    need(tuple(paths) == _RELATIVE_DIAGNOSTIC_HISTORY_FILE_NAMES and len(set(paths)) == 5,
         "Exactly five fixed documentary relative names required")
    record_keys = {"record_number", "ordinal", "timestamp", "original_jsonl_line_sha256",
                   "output_file", "output_sha256", "extraction"}
    for i, value in enumerate(declared["records"]):
        number = _RELATIVE_DIAGNOSTIC_HISTORY_RECORD_NUMBERS[i]
        need(isinstance(value, dict) and set(value) == record_keys
             and type(value["record_number"]) is int and value["record_number"] == number
             and type(value["ordinal"]) is int and value["ordinal"] == number - 1
             and isinstance(value["timestamp"], str)
             and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z", value["timestamp"]) is not None
             and isinstance(value["original_jsonl_line_sha256"], str)
             and re.fullmatch("[0-9a-f]{64}", value["original_jsonl_line_sha256"]) is not None
             and value["output_file"] == declared["files"][i]["path"]
             and value["output_sha256"] == declared["files"][i]["sha256"]
             and isinstance(value["extraction"], str) and bool(value["extraction"]),
             "Fixed three-record documentary linkage/types changed")
    need(exact_json(diagnostic["offending_receipt"], declared["files"][4]),
         "Fixed files4 documentary observation changed")
    return True


def _relative_diagnostic_history_metadata_shape(value, expected_path, size=None, directory=False):
    """Pure metadata shape validation; independently enforce444 files or555 directory."""
    need(isinstance(value, dict) and set(value) == _RELATIVE_DIAGNOSTIC_HISTORY_META_KEYS
         and value.get("path") == expected_path
         and all(type(value[k]) is int and value[k] >= 0 for k in _RELATIVE_DIAGNOSTIC_HISTORY_META_KEYS - {"path"}),
         "Exact integer fixed inventory history metadata required")
    if directory:
        need(stat.S_ISDIR(value["mode"]) and stat.S_IMODE(value["mode"]) == 0o555
             and value["nlink"] == 2,
             "Fixed history copy directory must independently be readonly0555")
    else:
        need(stat.S_ISREG(value["mode"]) and stat.S_IMODE(value["mode"]) == 0o444
             and value["nlink"] == 1 and value["bytes"] == size,
             "Fixed history input/copy must be readonly0444 single-link regular")
    return value


def _relative_diagnostic_history_copy_structure(receipt):
    receipt_shape(receipt)
    need(set(receipt) == {"path", "bytes", "sha256"} and fp(receipt) == fp(_RELATIVE_DIAGNOSTIC_HISTORY_LEAF),
         "Fixed history copy must preserve the exact full byte identity")
    raw = receipt["path"]
    path = Path(raw)
    need(path.is_absolute() and path.is_relative_to(Path(_RELATIVE_DIAGNOSTIC_HISTORY_AUTHORITY))
         and all(part not in ("", ".", "..") for part in raw.split("/")[1:])
         and path.name == _RELATIVE_DIAGNOSTIC_HISTORY_LEAF["sha256"] + "_13295_diagnostic.OPAQUE.txt"
         and path.parent.name == "opaque_relative_diagnostic_history_bytes",
         "Exact fixed history preservation path required")
    return path


def _relative_diagnostic_history_control_metadata(path):
    path = safe_path(path)
    need(path.name in {"relative_diagnostic_history_opaque_aliases.json",
                       "relative_diagnostic_history_opaque_leaf_proof.json"},
         "Only the two fixed13295 output controls are permitted")
    metadata = stable_metadata(path)
    _relative_diagnostic_history_metadata_shape(metadata, str(path), metadata["bytes"])
    return metadata


def _relative_diagnostic_history_control_readback(receipt, expected_metadata=None):
    receipt_shape(receipt)
    path = safe_path(receipt["path"])
    before = _relative_diagnostic_history_control_metadata(path)
    if expected_metadata is not None:
        need(exact_json(before, expected_metadata), "Fixed13295 control native metadata drifted")
    need(rec(path) == receipt, "Fixed13295 control whole bytes changed")
    content = path.read_bytes()
    obj = _strict_relative_diagnostic_history_json(content.decode("utf-8"))
    # This full readback is intentionally AFTER the final own JSON read/parse.
    need(rec(path) == receipt and stable_metadata(path) == before,
         "Fixed13295 control changed during own JSON readback")
    _relative_diagnostic_history_control_metadata(path)
    return obj, before


def _relative_diagnostic_history_write_control(path, obj):
    path = safe_path(path)
    need(path.name in {"relative_diagnostic_history_opaque_aliases.json",
                       "relative_diagnostic_history_opaque_leaf_proof.json"},
         "Only the two fixed13295 output controls are permitted")
    content = (json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
        os.fchmod(stream.fileno(), 0o444)
        os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    receipt = rec(path)
    metadata = _relative_diagnostic_history_control_metadata(path)
    actual, unused = _relative_diagnostic_history_control_readback(receipt, metadata)
    need(exact_json(actual, obj) and path.read_bytes() == content
         and stable_metadata(path) == metadata,
         "Fixed13295 control exclusive fsync publication changed")
    return receipt, metadata


def relative_diagnostic_history_proof_shape(saved, alias_index, allocation):
    """Pure strict validator for later INDEX-only replay; performs no filesystem calls."""
    need(isinstance(saved, dict) and isinstance(alias_index, dict) and isinstance(allocation, dict),
         "Full fixed history proof/index/allocation objects required")
    copy_receipt = saved.get("preserved_opaque_data")
    path = _relative_diagnostic_history_copy_structure(copy_receipt)
    out = path.parent.parent
    pointer = receipt_shape(saved.get("exact_alias_index"))
    need(set(pointer) == {"path", "bytes", "sha256"}
         and pointer["path"] == str(out / "relative_diagnostic_history_opaque_aliases.json"),
         "Fixed history proof/index pointer changed")
    need(isinstance(allocation.get("job_id"), str) and allocation["job_id"].isdigit()
         and type(allocation.get("allocated_CPUs")) is int and allocation["allocated_CPUs"] >= 1
         and type(allocation.get("allocated_gpus")) is int and allocation["allocated_gpus"] == 0,
         "Actual CPU allocation object required for fixed history proof")
    observations = saved.get("observations")
    need(isinstance(observations, list) and observations, "Actual ordered history observations required")
    expected_observations = []
    for index, observation in enumerate(observations):
        need(isinstance(observation, dict) and observation.get("module") in _RELATIVE_DIAGNOSTIC_HISTORY_MODULES,
             "Unknown fixed history observation module")
        selected = _fixed_history_observation_context("relative13295", observation)
        expected_observations.append(dict(
            ordinal=index, receipt=dict(_RELATIVE_DIAGNOSTIC_HISTORY_LEAF), parent_manifest=dict(selected["parent_manifest"]),
            field=list(selected["field"]), module=observation["module"], physical=copy_receipt,
            resolution_basis="EXACT_READONLY13295_RELATIVE_DIAGNOSTIC_HISTORY_DATA_BYTECOPY", role=_RELATIVE_DIAGNOSTIC_HISTORY_ROLE))
    need(exact_json(observations, expected_observations),
         "Full ordered fixed history observation context changed")
    actual_default = sum(x["module"] == "default_workflow_integration" for x in observations)
    actual_prospective = sum(x["module"] == "final_delivery_tools" for x in observations)
    need(actual_default >= 1, "At least one actual default history edge must be observed")
    parent_meta = _relative_diagnostic_history_metadata_shape(saved.get("parent_metadata_before"), _RELATIVE_DIAGNOSTIC_HISTORY_BASE["path"],
                                          _RELATIVE_DIAGNOSTIC_HISTORY_BASE["bytes"])
    leaf_meta = _relative_diagnostic_history_metadata_shape(saved.get("original_metadata_before"), _RELATIVE_DIAGNOSTIC_HISTORY_LEAF["path"],
                                        _RELATIVE_DIAGNOSTIC_HISTORY_LEAF["bytes"])
    copy_meta = _relative_diagnostic_history_metadata_shape(saved.get("preserved_metadata"), str(path), copy_receipt["bytes"])
    directory_meta = _relative_diagnostic_history_metadata_shape(saved.get("copy_directory_metadata"), str(path.parent),
                                             directory=True)
    expected = dict(
        schema=_RELATIVE_DIAGNOSTIC_HISTORY_PROOF_SCHEMA, status=_RELATIVE_DIAGNOSTIC_HISTORY_PROOF_STATUS,
        parent_manifest=dict(_RELATIVE_DIAGNOSTIC_HISTORY_BASE), original_diagnostic_data=dict(_RELATIVE_DIAGNOSTIC_HISTORY_LEAF),
        source_field=list(_RELATIVE_DIAGNOSTIC_HISTORY_FIELD), role=_RELATIVE_DIAGNOSTIC_HISTORY_ROLE,
        allowed_modules=list(_RELATIVE_DIAGNOSTIC_HISTORY_MODULES),
        module_policy=dict(default_workflow_integration="FINITE_FIVE_ROWS_ACTUAL_RUNTIME_PARENT_FIELD_AUTHENTICATION_REQUIRED",
                           final_delivery_tools="PROSPECTIVE_SAME_FIVE_ROWS_NOT_REQUIRED"),
        preserved_opaque_data=copy_receipt, exact_alias_index=pointer, allocation=allocation,
        parent_metadata_before=parent_meta, parent_metadata_after=parent_meta,
        original_metadata_before=leaf_meta, original_metadata_after=leaf_meta,
        preserved_metadata=copy_meta, copy_directory_metadata=directory_meta,
        observations=expected_observations, authorized_observation_n=len(observations),
        actual_default_observation_n=actual_default, actual_finaltools_observation_n=actual_prospective,
        embedded_parent_n=1, embedded_record_n=3, embedded_file_n=5,
        embedded_receipt_occurrence_n=6, embedded_unique_relative_path_n=5,
        independent_source_producer=dict(_RELATIVE_DIAGNOSTIC_HISTORY_PRODUCER),
        independent_software_only_gate=dict(_RELATIVE_DIAGNOSTIC_HISTORY_SOFTWARE),
        independent_BaseA_history_fields_retained=True,
        original_bytes_and_metadata_unchanged=True, original_permission_unchanged=True,
        preserved_copy_readonly_fsynced_and_byte_identical=True,
        embedded_relative_targets_interpreted=False, embedded_targets_statted_or_opened=False,
        source_or_configuration_promotion=False, archive_or_scientific_acceptance=False,
        original_JSON_or_parent_rewritten=False, generic_reader_or17_parent_scope_changed=False,
        separate_original_JSON_physical_package_entry_forbidden=True,
        future_package_index_and_isolated_restore_acceptance=False)
    expected.update(_fixed_history_saved_authorities("relative13295", saved))
    need(exact_json(saved, expected), "Full saved fixed inventory history proof changed")
    expected_alias = dict(
        schema="exact-resource-aliases.v2", status=_RELATIVE_DIAGNOSTIC_HISTORY_ALIAS_STATUS,
        aliases=[dict(original=dict(_RELATIVE_DIAGNOSTIC_HISTORY_LEAF), archived=copy_receipt,
                      status="READONLY_BYTE_IDENTICAL_ALIAS", role=_RELATIVE_DIAGNOSTIC_HISTORY_ROLE)],
        historical_unresolved=[], separate_original_JSON_physical_package_entry_forbidden=True,
        scientific_or_source_or_archive_authorization=False)
    need(exact_json(alias_index, expected_alias), "Full fixed history byte alias index changed")
    return True


class RelativeDiagnosticHistoryOpaqueLeaf:
    """One fixed history DATA edge, authorized afresh before seen or any resolver."""

    def __init__(self, out, accepted_base):
        self.out = safe_path(out)
        self.active = accepted_base == _RELATIVE_DIAGNOSTIC_HISTORY_BASE
        self.directory = self.out / "opaque_relative_diagnostic_history_bytes"
        self.observations = []
        self.parent_before = None
        self.authorities_before = None
        self.leaf_before = None
        self.copy_receipt = None
        self.copy_before = None
        self.directory_before = None

    @staticmethod
    def _regular(path):
        path = safe_path(path)
        metadata = stable_metadata(path)
        _relative_diagnostic_history_metadata_shape(metadata, str(path), metadata["bytes"])
        return path, metadata

    def _inputs(self):
        need(self.active, "Fixed history leaf requires the exact accepted BaseA")
        parent, parent_before = self._regular(_RELATIVE_DIAGNOSTIC_HISTORY_BASE["path"])
        leaf, leaf_before = self._regular(_RELATIVE_DIAGNOSTIC_HISTORY_LEAF["path"])
        need(rec(parent) == _RELATIVE_DIAGNOSTIC_HISTORY_BASE and rec(leaf) == _RELATIVE_DIAGNOSTIC_HISTORY_LEAF,
             "Fixed history parent/original bytes changed")
        parent_bytes = parent.read_bytes()
        content = leaf.read_bytes()
        base = _strict_relative_diagnostic_history_json(parent_bytes.decode("utf-8"))
        need(isinstance(base, dict) and base.get("schema") == "source-delivery-refresh.v3"
             and base.get("status") == "CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY"
             and type(base.get("source_issues")) is int and base["source_issues"] == 0
             and base.get("source_staged") is False,
             "Exact accepted BaseA history authority required")
        history = base.get("original_failure_history", {})
        need(history.get(_RELATIVE_DIAGNOSTIC_HISTORY_FIELD[1]) == _RELATIVE_DIAGNOSTIC_HISTORY_LEAF
             and history.get("original13293_executing_source") == _RELATIVE_DIAGNOSTIC_HISTORY_PRODUCER
             and history.get("original13293_software_only_acceptance") == _RELATIVE_DIAGNOSTIC_HISTORY_SOFTWARE,
             "Exact BaseA field and independent producer/software edges required")
        text = content.decode("utf-8")
        need(not SECRET_RE.search(text) and "-----BEGIN " + "OPENSSH PRIVATE KEY-----" not in text,
             "Potential credential in fixed diagnostic history DATA")
        relative_diagnostic_history_document_shape(_strict_relative_diagnostic_history_json(text))
        need(rec(parent) == _RELATIVE_DIAGNOSTIC_HISTORY_BASE and rec(leaf) == _RELATIVE_DIAGNOSTIC_HISTORY_LEAF
             and stable_metadata(parent) == parent_before and stable_metadata(leaf) == leaf_before,
             "Fixed history inputs changed during own-byte/shape readback")
        self._current_authorities = _fixed_history_mapping_inputs("relative13295", base, parent_before)
        need(rec(parent) == _RELATIVE_DIAGNOSTIC_HISTORY_BASE and rec(leaf) == _RELATIVE_DIAGNOSTIC_HISTORY_LEAF
             and stable_metadata(parent) == parent_before and stable_metadata(leaf) == leaf_before,
             "Fixed history parent/leaf changed after the last mapping JSON read")
        return parent_before, leaf_before, content

    def _copy(self, content):
        self.directory.mkdir(mode=0o700, exist_ok=False)
        target = self.directory / (_RELATIVE_DIAGNOSTIC_HISTORY_LEAF["sha256"] + "_13295_diagnostic.OPAQUE.txt")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(target, flags, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o444)
            os.fsync(stream.fileno())
        self.copy_receipt = rec(target)
        need(fp(self.copy_receipt) == fp(_RELATIVE_DIAGNOSTIC_HISTORY_LEAF) and target.read_bytes() == content,
             "Fixed history opaque preservation changed bytes")
        unused, self.copy_before = self._regular(target)
        self.directory.chmod(0o555)
        fd = os.open(self.directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        self.directory_before = stable_metadata(self.directory)

    def edge(self, receipt, parent, trail, module):
        if not _relative_diagnostic_history_matches(receipt):
            return None
        need(receipt == _RELATIVE_DIAGNOSTIC_HISTORY_LEAF, "Fixed inherited history requires exact leaf fulltuple")
        selected = _fixed_history_context("relative13295", parent, trail, module)
        parent_before, leaf_before, content = self._inputs()
        if self.copy_receipt is None:
            self.parent_before, self.leaf_before = parent_before, leaf_before
            self.authorities_before = self._current_authorities
            self._copy(content)
        else:
            need(parent_before == self.parent_before and leaf_before == self.leaf_before,
                 "Repeated fixed history observation changed original metadata")
        self.readback()
        observation = dict(
            ordinal=len(self.observations), receipt=dict(_RELATIVE_DIAGNOSTIC_HISTORY_LEAF),
            parent_manifest=dict(selected["parent_manifest"]), field=list(trail), module=module,
            physical=self.copy_receipt,
            resolution_basis="EXACT_READONLY13295_RELATIVE_DIAGNOSTIC_HISTORY_DATA_BYTECOPY", role=_RELATIVE_DIAGNOSTIC_HISTORY_ROLE)
        self.observations.append(observation)
        return dict(receipt=dict(_RELATIVE_DIAGNOSTIC_HISTORY_LEAF), parent=parent, field=list(trail), module=module,
                    physical=self.copy_receipt, resolution_basis=observation["resolution_basis"],
                    role=_RELATIVE_DIAGNOSTIC_HISTORY_ROLE, raw_bytes_preserved=True,
                    receipt_children_interpreted=False, source_or_configuration_promotion=False)

    def readback(self):
        need(self.copy_receipt is not None, "Fixed history DATA preservation has not occurred")
        parent_meta, leaf_meta, content = self._inputs()
        need(exact_json(self._current_authorities, self.authorities_before),
             "Fixed inherited history four-authority native metadata drifted")
        need(parent_meta == self.parent_before and leaf_meta == self.leaf_before,
             "Fixed history original/parent stable metadata drifted")
        copy_path, copy_meta = self._regular(self.copy_receipt["path"])
        need(_relative_diagnostic_history_copy_structure(self.copy_receipt) == copy_path
             and copy_meta == self.copy_before and rec(copy_path) == self.copy_receipt
             and copy_path.read_bytes() == content and stable_metadata(copy_path) == self.copy_before,
             "Fixed history readonly copy bytes/metadata drifted")
        directory = safe_path(self.directory)
        directory_meta = stable_metadata(directory)
        _relative_diagnostic_history_metadata_shape(directory_meta, str(directory), directory=True)
        need(directory_meta == self.directory_before
             and {p.name for p in directory.iterdir()} == {copy_path.name},
             "Fixed history555 directory metadata or exact one-file universe changed")
        return True

    def require_complete(self):
        if self.active:
            need(any(x["module"] == "default_workflow_integration" for x in self.observations),
                 "Actual source graph must observe the fixed default history edge")
            self.readback()
        else:
            need(not self.observations and self.copy_receipt is None,
                 "No inventory history exception outside exact BaseA")
        return self.active

    def alias_index(self):
        self.readback()
        return dict(
            schema="exact-resource-aliases.v2", status=_RELATIVE_DIAGNOSTIC_HISTORY_ALIAS_STATUS,
            aliases=[dict(original=dict(_RELATIVE_DIAGNOSTIC_HISTORY_LEAF), archived=self.copy_receipt,
                          status="READONLY_BYTE_IDENTICAL_ALIAS", role=_RELATIVE_DIAGNOSTIC_HISTORY_ROLE)],
            historical_unresolved=[], separate_original_JSON_physical_package_entry_forbidden=True,
            scientific_or_source_or_archive_authorization=False)

    def proof(self):
        need(self.require_complete(), "Actual fixed inventory history observations required")
        return dict(
            schema=_RELATIVE_DIAGNOSTIC_HISTORY_PROOF_SCHEMA, status=_RELATIVE_DIAGNOSTIC_HISTORY_PROOF_STATUS,
            parent_manifest=dict(_RELATIVE_DIAGNOSTIC_HISTORY_BASE), original_diagnostic_data=dict(_RELATIVE_DIAGNOSTIC_HISTORY_LEAF),
            source_field=list(_RELATIVE_DIAGNOSTIC_HISTORY_FIELD), role=_RELATIVE_DIAGNOSTIC_HISTORY_ROLE, allowed_modules=list(_RELATIVE_DIAGNOSTIC_HISTORY_MODULES),
            module_policy=dict(default_workflow_integration="FINITE_FIVE_ROWS_ACTUAL_RUNTIME_PARENT_FIELD_AUTHENTICATION_REQUIRED",
                               final_delivery_tools="PROSPECTIVE_SAME_FIVE_ROWS_NOT_REQUIRED"),
            preserved_opaque_data=self.copy_receipt,
            parent_metadata_before=self.parent_before,
            parent_metadata_after=stable_metadata(_RELATIVE_DIAGNOSTIC_HISTORY_BASE["path"]),
            original_metadata_before=self.leaf_before,
            original_metadata_after=stable_metadata(_RELATIVE_DIAGNOSTIC_HISTORY_LEAF["path"]),
            preserved_metadata=self.copy_before, copy_directory_metadata=self.directory_before,
            observations=list(self.observations), authorized_observation_n=len(self.observations),
            actual_default_observation_n=sum(x["module"] == "default_workflow_integration" for x in self.observations),
            actual_finaltools_observation_n=sum(x["module"] == "final_delivery_tools" for x in self.observations),
            embedded_parent_n=1, embedded_record_n=3, embedded_file_n=5,
            embedded_receipt_occurrence_n=6, embedded_unique_relative_path_n=5,
            independent_source_producer=dict(_RELATIVE_DIAGNOSTIC_HISTORY_PRODUCER),
            independent_software_only_gate=dict(_RELATIVE_DIAGNOSTIC_HISTORY_SOFTWARE),
            independent_BaseA_history_fields_retained=True, original_bytes_and_metadata_unchanged=True,
            original_permission_unchanged=True, preserved_copy_readonly_fsynced_and_byte_identical=True,
            embedded_relative_targets_interpreted=False, embedded_targets_statted_or_opened=False,
            source_or_configuration_promotion=False, archive_or_scientific_acceptance=False,
            original_JSON_or_parent_rewritten=False, generic_reader_or17_parent_scope_changed=False,
            separate_original_JSON_physical_package_entry_forbidden=True,
            future_package_index_and_isolated_restore_acceptance=False,
            **_fixed_history_authority_projection("relative13295", self.authorities_before))


def verify_relative_diagnostic_history_preservation(saved, alias_index, allocation):
    """Current owned-CPU object verifier; pure validator remains separately usable."""
    relative_diagnostic_history_proof_shape(saved, alias_index, allocation)
    pointer = saved["exact_alias_index"]
    actual_index, index_before = _relative_diagnostic_history_control_readback(pointer)
    need(exact_json(actual_index, alias_index), "Saved fixed relative-diagnostic alias object differs")
    copy_receipt = saved["preserved_opaque_data"]
    path = _relative_diagnostic_history_copy_structure(copy_receipt)
    scope = RelativeDiagnosticHistoryOpaqueLeaf(path.parent.parent, _RELATIVE_DIAGNOSTIC_HISTORY_BASE)
    scope.parent_before = saved["parent_metadata_before"]
    scope.authorities_before = saved["authority_metadata_before"]
    scope.leaf_before = saved["original_metadata_before"]
    scope.copy_receipt = copy_receipt
    scope.copy_before = saved["preserved_metadata"]
    scope.directory_before = saved["copy_directory_metadata"]
    scope.observations = saved["observations"]
    scope.require_complete()
    expected = dict(scope.proof(), exact_alias_index=pointer, allocation=allocation)
    need(exact_json(saved, expected), "Current complete fixed relative-diagnostic history proof differs")
    final_index, unused = _relative_diagnostic_history_control_readback(pointer, index_before)
    need(exact_json(final_index, alias_index), "Saved fixed relative-diagnostic alias changed after inputs")
    _fixed_history_authority_fence("relative13295", scope.authorities_before)
    _fixed_history_native_union_sweep(_fixed_history_saved_native_records(saved) + [index_before])
    return True


# One immutable diagnostic history DATA object; embedded member records are not inputs.
_PARENT_DIAGNOSTIC_HISTORY_BASE = dict(INHERITED_ENTRYPOINT_BASE)
_PARENT_DIAGNOSTIC_HISTORY_AUTHORITY = "/lustre/users/u21111210118/projects/test9"
_PARENT_DIAGNOSTIC_HISTORY_LEAF = json.loads(r'''{
  "path": "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_receipt_parent_diagnostic_13290/diagnostic.json",
  "bytes": 9679,
  "sha256": "bd46f9afe0cd0b64003fa7d77c5d5ef2b66235942a16376ab4a15a674267567f"
}''')
_PARENT_DIAGNOSTIC_HISTORY_FIELD = ("original_failure_history", "actual13290_parent_diagnostic_only")
_PARENT_DIAGNOSTIC_HISTORY_MODULES = ("default_workflow_integration", "final_delivery_tools")
_PARENT_DIAGNOSTIC_HISTORY_ROLE = "EXACT13290_PARENT_DIAGNOSTIC_HISTORY_DATA_NOT_EXTERNAL_RECEIPT_SOURCE_OR_RECOVERY_AUTHORIZATION"
_PARENT_DIAGNOSTIC_HISTORY_PRODUCER = json.loads(r'''{
  "path": "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/pending/source_receipt_parent_diagnostic_v1/diagnostic.py",
  "bytes": 2787,
  "sha256": "3e3263606831e4c35dd29ac40f043e1c44cb6b8db9ee01f2b5acf139fd9ba265"
}''')
_PARENT_DIAGNOSTIC_HISTORY_V4_SOURCE = json.loads(r'''{
  "path": "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/frozen/source_refresh_relative_v4_13279/code/source_delivery_refresh_v4.py",
  "bytes": 21113,
  "sha256": "e3b6a5965dae04d95b470c124e4b39d6569a689ac1a4ff5e9775060b981ef794"
}''')
_PARENT_DIAGNOSTIC_HISTORY_RECOVERED_PARENT = json.loads(r'''{
  "path": "/lustre/users/u21111210118/projects/test9/01_raw/recovered_inputs/recovered_three_candidates.json",
  "bytes": 4665,
  "sha256": "04a73810c339e4594e8dc989e2c89aa3ba90542f89d5644c92f9df2b755c482c"
}''')
_PARENT_DIAGNOSTIC_HISTORY_PREVIOUS_EDGE_PARENT = '/lustre/users/u21111210118/projects/test9/steps/03_af2_restore/target_msa/receipt.json'
# Documentary scalar only, never a filesystem target.
_PARENT_DIAGNOSTIC_HISTORY_ATTEMPT = json.loads(r'''{
  "path": "/work/home/lvying/lvying20260610/project-1/test9/steps/03_design/runs/20260922T113858Z_149ef033124f/manifest.json",
  "sha256": "47bfbe1852aede63e479b88a1456a06aafc0797730453d003551091ff5251262",
  "bytes": 12402
}''')
_PARENT_DIAGNOSTIC_HISTORY_FALSE_FLAGS = ("strict_authority_guard_weakened", "default_or_scientific_inputs_changed", "replay_unexpectedly_completed")
_PARENT_DIAGNOSTIC_HISTORY_TRUE_FLAGS = ("actual13279_and13285_history_preserved",)
_PARENT_DIAGNOSTIC_HISTORY_TOP_KEYS = set(('schema', 'status', 'allocation', 'source', 'original_sealed_V4_source', 'actual13279_and13285_history_preserved', 'strict_authority_guard_weakened', 'default_or_scientific_inputs_changed', 'GPU_allocated', 'replay_unexpectedly_completed', 'exact_calls', 'failure_context', 'error_type', 'error', 'traceback'))
_PARENT_DIAGNOSTIC_HISTORY_PROOF_SCHEMA = "exact13290-parent-diagnostic-history-data-leaf.v2"
_PARENT_DIAGNOSTIC_HISTORY_PROOF_STATUS = "EXACT_BASEA_PARENT_DIAGNOSTIC_HISTORY_CONTEXTS_AND13290_DATA_BYTES_PRESERVED_CPU_VERIFIED"
_PARENT_DIAGNOSTIC_HISTORY_ALIAS_STATUS = "EXACT13290_PARENT_DIAGNOSTIC_HISTORY_DATA_BYTE_ALIAS_CPU_VERIFIED"
_PARENT_DIAGNOSTIC_HISTORY_META_KEYS = {"path", "bytes", "inode", "mtime_ns", "ctime_ns", "mode", "dev", "nlink", "uid", "gid"}


def _strict_parent_diagnostic_history_json(raw):
    def pairs(items):
        result = {}
        for name, value in items:
            need(name not in result, "Duplicate key in fixed exact-parent diagnostic history JSON")
            result[name] = value
        return result

    def constant(value):
        raise ValueError("Nonfinite fixed exact-parent diagnostic history JSON number: " + value)

    def number(value):
        result = float(value)
        need(result == result and abs(result) != float("inf"),
             "Nonfinite fixed exact-parent diagnostic history JSON exponent")
        return result

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant, parse_float=number)


def _parent_diagnostic_history_matches(receipt):
    receipt_shape(receipt)
    return receipt["path"] == _PARENT_DIAGNOSTIC_HISTORY_LEAF["path"] or fp(receipt) == fp(_PARENT_DIAGNOSTIC_HISTORY_LEAF)


def reject_parent_diagnostic_history_declaration(receipt):
    need(not _parent_diagnostic_history_matches(receipt),
         "Fixed13290 diagnostic DATA cannot be direct SOURCE/gate/seed/context/Plan alias")


def parent_diagnostic_history_document_shape(obj):
    """Pure whole own-DATA shape; no documentary target becomes an input."""
    need(type(obj) is dict and set(obj) == _PARENT_DIAGNOSTIC_HISTORY_TOP_KEYS
         and obj["schema"] == "source-closure-exact-parent-diagnostic.v1"
         and obj["status"] == "DIAGNOSTIC_ONLY_NOT_SOURCE_ACCEPTANCE",
         "Exact13290 nonauthorizing schema/status/fifteen keys required")
    need(all(obj[k] is False for k in _PARENT_DIAGNOSTIC_HISTORY_FALSE_FLAGS)
         and all(obj[k] is True for k in _PARENT_DIAGNOSTIC_HISTORY_TRUE_FLAGS)
         and type(obj["GPU_allocated"]) is int and obj["GPU_allocated"] == 0
         and type(obj["exact_calls"]) is int and obj["exact_calls"] == 1660,
         "Fixed13290 history flags and exact integer counters changed")
    allocation = obj["allocation"]
    need(type(allocation) is dict and set(allocation) == {"job_id", "scheduler_record", "allocated_gpus"}
         and allocation["job_id"] == "13290" and type(allocation["allocated_gpus"]) is int
         and allocation["allocated_gpus"] == 0 and type(allocation["scheduler_record"]) is str
         and "JobId=13290 " in allocation["scheduler_record"] and "NumCPUs=1 " in allocation["scheduler_record"],
         "Fixed historical CPU declaration changed; no live scheduler permission")
    need(exact_json(obj["source"], _PARENT_DIAGNOSTIC_HISTORY_PRODUCER)
         and exact_json(obj["original_sealed_V4_source"], _PARENT_DIAGNOSTIC_HISTORY_V4_SOURCE),
         "Both fixed ordinary Source child identities must remain intact")
    failure = obj["failure_context"]
    need(type(failure) is dict and set(failure) == {
             "diagnostic_only", "source_V4_guard_unchanged", "external_original_not_read",
             "attempted_receipt", "original_error_type", "original_error", "context"}
         and all(failure[k] is True for k in ("diagnostic_only", "source_V4_guard_unchanged", "external_original_not_read"))
         and exact_json(failure["attempted_receipt"], _PARENT_DIAGNOSTIC_HISTORY_ATTEMPT)
         and failure["original_error_type"] == "ValueError" and failure["original_error"] == "Source receipt escapes authority",
         "Fixed external attempt is documentary, not read or byte accepted")
    context = failure["context"]
    need(type(context) is dict and set(context) == {
             "parent_original_logical_path", "source_field", "previous_verified_parent_edge",
             "declared_basename_candidates", "declared_same_size_candidates", "exact_declared_alias_hit"}
         and context["parent_original_logical_path"] == _PARENT_DIAGNOSTIC_HISTORY_RECOVERED_PARENT["path"]
         and context["source_field"] == ["entries", "2", "design_manifest"]
         and context["declared_basename_candidates"] == [] and context["declared_same_size_candidates"] == []
         and context["exact_declared_alias_hit"] is False,
         "Complete fixed historical context changed")
    previous = context["previous_verified_parent_edge"]
    need(type(previous) is dict and set(previous) == {
             "receipt", "parent", "field", "physical", "resolution_basis", "relative_context", "role"}
         and exact_json(previous["receipt"], _PARENT_DIAGNOSTIC_HISTORY_RECOVERED_PARENT)
         and exact_json(previous["physical"], _PARENT_DIAGNOSTIC_HISTORY_RECOVERED_PARENT)
         and previous["parent"] == _PARENT_DIAGNOSTIC_HISTORY_PREVIOUS_EDGE_PARENT
         and previous["field"] == ["inputs"] and previous["resolution_basis"] == "EXACT_ORIGINAL"
         and previous["relative_context"] is None and previous["role"] == "EXACT_TEXT_RECEIPT_READBACK",
         "Previous-parent documentary receipt/physical cannot grant a new parent")
    need(obj["error_type"] == "ValueError" and type(obj["error"]) is str
         and exact_json(_strict_parent_diagnostic_history_json(obj["error"]), failure)
         and type(obj["traceback"]) is str and "ValueError" in obj["traceback"],
         "Own duplicate error JSON string and traceback must remain documentary")
    return True


def parent_diagnostic_history_source_children():
    """Pure ordinary Source obligations, not interpretation of attempted targets."""
    return [dict(receipt=dict(_PARENT_DIAGNOSTIC_HISTORY_PRODUCER), field=["source"]),
            dict(receipt=dict(_PARENT_DIAGNOSTIC_HISTORY_V4_SOURCE), field=["original_sealed_V4_source"])]


def parent_diagnostic_history_source_coverage(saved, closure, inclusion):
    """Pure actual C/I coverage: DATA obligation flags alone are not acceptance."""
    need(type(saved) is dict and type(closure) is dict and type(inclusion) is dict
         and type(saved.get("observations")) is list and bool(saved["observations"])
         and type(closure.get("edges")) is list and type(inclusion.get("files")) is list,
         "Full proof/actual closure/actual inclusion objects required")
    expected_index = dict(schema="exact-resource-aliases.v2", status=_PARENT_DIAGNOSTIC_HISTORY_ALIAS_STATUS,
                          aliases=[dict(original=dict(_PARENT_DIAGNOSTIC_HISTORY_LEAF), archived=saved.get("preserved_opaque_data"),
                                        status="READONLY_BYTE_IDENTICAL_ALIAS", role=_PARENT_DIAGNOSTIC_HISTORY_ROLE)],
                          historical_unresolved=[], separate_original_JSON_physical_package_entry_forbidden=True,
                          scientific_or_source_or_archive_authorization=False)
    parent_diagnostic_history_proof_shape(saved, expected_index, saved.get("allocation"))
    actual_data = [edge for edge in closure["edges"] if edge.get("receipt") == _PARENT_DIAGNOSTIC_HISTORY_LEAF]
    expected_data = [dict(receipt=dict(_PARENT_DIAGNOSTIC_HISTORY_LEAF), parent=observation["parent_manifest"]["path"],
                          field=list(observation["field"]), module=observation["module"],
                          physical=saved["preserved_opaque_data"], resolution_basis=observation["resolution_basis"],
                          role=_PARENT_DIAGNOSTIC_HISTORY_ROLE, raw_bytes_preserved=True,
                          documentary_receipt_children_interpreted=False, ordinary_Source_children_explicitly_enqueued=True,
                          source_or_configuration_promotion=False) for observation in saved["observations"]]
    need(exact_json(actual_data, expected_data), "Actual ordered DATA graph edges differ from the full saved proof")
    obligations = parent_diagnostic_history_source_children()
    need(exact_json(saved.get("ordinary_source_children"), obligations)
         and saved.get("ordinary_source_children_are_separate_graph_obligations") is True,
         "Source2 obligations must be explicit, never DATA byte acceptance")
    expected = []
    for observation in saved["observations"]:
        need(observation.get("module") in _PARENT_DIAGNOSTIC_HISTORY_MODULES
             and observation.get("receipt") == _PARENT_DIAGNOSTIC_HISTORY_LEAF
             and _fixed_history_observation_context("parent13290", observation),
             "Source obligations require each exact authorized DATA observation")
        for child in reversed(obligations):
            expected.append((child["receipt"], child["field"], observation["module"]))
    selected = [edge for edge in closure["edges"] if edge.get("parent") == _PARENT_DIAGNOSTIC_HISTORY_LEAF["path"]]
    need(len(selected) == len(expected), "Every ordered13290 Source2 edge must be retained")
    for edge, (receipt, field, module) in zip(selected, expected):
        need(edge.get("receipt") == receipt and edge.get("field") == field and edge.get("module") == module
             and edge.get("role") == "EXACT_NEW_TEXT_RECEIPT_READBACK"
             and edge.get("resolution_basis") in {"EXACT_ORIGINAL", "EXPLICIT_EXACT_BYTE_ALIAS"},
             "Source2 original parent/field/module/ordinary verification changed")
        physical = receipt_shape(edge.get("physical"))
        need(fp(physical) == fp(receipt), "Ordinary Source2 physical bytes forked")
        matches = [row for row in inclusion["files"] if fp(row["source"]) == fp(receipt)]
        need(matches and any(row.get("kind") == "IMPLEMENTATION" and module in row.get("roles", [])
                            and (row.get("original_source") == receipt or receipt in row.get("logical_receipts", [])) for row in matches),
             "Both Source2 identities require actual IMPLEMENTATION inclusion rows")
    return True


def _parent_diagnostic_history_metadata_shape(value, expected_path, size=None, directory=False):
    """Pure metadata shape validation; independently enforce444 files or555 directory."""
    need(isinstance(value, dict) and set(value) == _PARENT_DIAGNOSTIC_HISTORY_META_KEYS
         and value.get("path") == expected_path
         and all(type(value[k]) is int and value[k] >= 0 for k in _PARENT_DIAGNOSTIC_HISTORY_META_KEYS - {"path"}),
         "Exact integer fixed exact-parent diagnostic history metadata required")
    if directory:
        need(stat.S_ISDIR(value["mode"]) and stat.S_IMODE(value["mode"]) == 0o555
             and value["nlink"] == 2,
             "Fixed history copy directory must independently be readonly0555")
    else:
        need(stat.S_ISREG(value["mode"]) and stat.S_IMODE(value["mode"]) == 0o444
             and value["nlink"] == 1 and value["bytes"] == size,
             "Fixed history input/copy must be readonly0444 single-link regular")
    return value


def _parent_diagnostic_history_copy_structure(receipt):
    receipt_shape(receipt)
    need(set(receipt) == {"path", "bytes", "sha256"} and fp(receipt) == fp(_PARENT_DIAGNOSTIC_HISTORY_LEAF),
         "Fixed history copy must preserve the exact full byte identity")
    raw = receipt["path"]
    path = Path(raw)
    need(path.is_absolute() and path.is_relative_to(Path(_PARENT_DIAGNOSTIC_HISTORY_AUTHORITY))
         and all(part not in ("", ".", "..") for part in raw.split("/")[1:])
         and path.name == _PARENT_DIAGNOSTIC_HISTORY_LEAF["sha256"] + "_13290_diagnostic.OPAQUE.txt"
         and path.parent.name == "opaque_parent_diagnostic_history_bytes",
         "Exact fixed history preservation path required")
    return path


def _parent_diagnostic_history_control_metadata(path):
    path = safe_path(path)
    need(path.name in {"parent_diagnostic_history_opaque_aliases.json",
                       "parent_diagnostic_history_opaque_leaf_proof.json"},
         "Only the two fixed13290 output controls are permitted")
    metadata = stable_metadata(path)
    _parent_diagnostic_history_metadata_shape(metadata, str(path), metadata["bytes"])
    return metadata


def _parent_diagnostic_history_control_readback(receipt, expected_metadata=None):
    receipt_shape(receipt)
    path = safe_path(receipt["path"])
    before = _parent_diagnostic_history_control_metadata(path)
    if expected_metadata is not None:
        need(exact_json(before, expected_metadata), "Fixed13290 control native metadata drifted")
    need(rec(path) == receipt, "Fixed13290 control whole bytes changed")
    content = path.read_bytes()
    obj = _strict_parent_diagnostic_history_json(content.decode("utf-8"))
    # This full readback is intentionally AFTER the final own JSON read/parse.
    need(rec(path) == receipt and stable_metadata(path) == before,
         "Fixed13290 control changed during own JSON readback")
    _parent_diagnostic_history_control_metadata(path)
    return obj, before


def _parent_diagnostic_history_write_control(path, obj):
    path = safe_path(path)
    need(path.name in {"parent_diagnostic_history_opaque_aliases.json",
                       "parent_diagnostic_history_opaque_leaf_proof.json"},
         "Only the two fixed13290 output controls are permitted")
    content = (json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
        os.fchmod(stream.fileno(), 0o444)
        os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    receipt = rec(path)
    metadata = _parent_diagnostic_history_control_metadata(path)
    actual, unused = _parent_diagnostic_history_control_readback(receipt, metadata)
    need(exact_json(actual, obj) and path.read_bytes() == content
         and stable_metadata(path) == metadata,
         "Fixed13290 control exclusive fsync publication changed")
    return receipt, metadata


def parent_diagnostic_history_proof_shape(saved, alias_index, allocation):
    """Pure strict validator for later INDEX-only replay; performs no filesystem calls."""
    need(isinstance(saved, dict) and isinstance(alias_index, dict) and isinstance(allocation, dict),
         "Full fixed history proof/index/allocation objects required")
    copy_receipt = saved.get("preserved_opaque_data")
    path = _parent_diagnostic_history_copy_structure(copy_receipt)
    out = path.parent.parent
    pointer = receipt_shape(saved.get("exact_alias_index"))
    need(set(pointer) == {"path", "bytes", "sha256"}
         and pointer["path"] == str(out / "parent_diagnostic_history_opaque_aliases.json"),
         "Fixed history proof/index pointer changed")
    need(isinstance(allocation.get("job_id"), str) and allocation["job_id"].isdigit()
         and type(allocation.get("allocated_CPUs")) is int and allocation["allocated_CPUs"] >= 1
         and type(allocation.get("allocated_gpus")) is int and allocation["allocated_gpus"] == 0,
         "Actual CPU allocation object required for fixed history proof")
    observations = saved.get("observations")
    need(isinstance(observations, list) and observations, "Actual ordered history observations required")
    expected_observations = []
    for index, observation in enumerate(observations):
        need(isinstance(observation, dict) and observation.get("module") in _PARENT_DIAGNOSTIC_HISTORY_MODULES,
             "Unknown fixed history observation module")
        selected = _fixed_history_observation_context("parent13290", observation)
        expected_observations.append(dict(
            ordinal=index, receipt=dict(_PARENT_DIAGNOSTIC_HISTORY_LEAF), parent_manifest=dict(selected["parent_manifest"]),
            field=list(selected["field"]), module=observation["module"], physical=copy_receipt,
            resolution_basis="EXACT_READONLY13290_PARENT_DIAGNOSTIC_HISTORY_DATA_BYTECOPY", role=_PARENT_DIAGNOSTIC_HISTORY_ROLE))
    need(exact_json(observations, expected_observations),
         "Full ordered fixed history observation context changed")
    actual_default = sum(x["module"] == "default_workflow_integration" for x in observations)
    actual_prospective = sum(x["module"] == "final_delivery_tools" for x in observations)
    need(actual_default >= 1, "At least one actual default history edge must be observed")
    parent_meta = _parent_diagnostic_history_metadata_shape(saved.get("parent_metadata_before"), _PARENT_DIAGNOSTIC_HISTORY_BASE["path"],
                                          _PARENT_DIAGNOSTIC_HISTORY_BASE["bytes"])
    leaf_meta = _parent_diagnostic_history_metadata_shape(saved.get("original_metadata_before"), _PARENT_DIAGNOSTIC_HISTORY_LEAF["path"],
                                        _PARENT_DIAGNOSTIC_HISTORY_LEAF["bytes"])
    copy_meta = _parent_diagnostic_history_metadata_shape(saved.get("preserved_metadata"), str(path), copy_receipt["bytes"])
    directory_meta = _parent_diagnostic_history_metadata_shape(saved.get("copy_directory_metadata"), str(path.parent),
                                             directory=True)
    expected = dict(
        schema=_PARENT_DIAGNOSTIC_HISTORY_PROOF_SCHEMA, status=_PARENT_DIAGNOSTIC_HISTORY_PROOF_STATUS,
        parent_manifest=dict(_PARENT_DIAGNOSTIC_HISTORY_BASE), original_diagnostic_data=dict(_PARENT_DIAGNOSTIC_HISTORY_LEAF),
        source_field=list(_PARENT_DIAGNOSTIC_HISTORY_FIELD), role=_PARENT_DIAGNOSTIC_HISTORY_ROLE,
        allowed_modules=list(_PARENT_DIAGNOSTIC_HISTORY_MODULES),
        module_policy=dict(default_workflow_integration="FINITE_FIVE_ROWS_ACTUAL_RUNTIME_PARENT_FIELD_AUTHENTICATION_REQUIRED",
                           final_delivery_tools="PROSPECTIVE_SAME_FIVE_ROWS_NOT_REQUIRED"),
        preserved_opaque_data=copy_receipt, exact_alias_index=pointer, allocation=allocation,
        parent_metadata_before=parent_meta, parent_metadata_after=parent_meta,
        original_metadata_before=leaf_meta, original_metadata_after=leaf_meta,
        preserved_metadata=copy_meta, copy_directory_metadata=directory_meta,
        observations=expected_observations, authorized_observation_n=len(observations),
        actual_default_observation_n=actual_default, actual_finaltools_observation_n=actual_prospective,
        embedded_receipt_occurrence_n=5, embedded_unique_fingerprint_n=4,
        ordinary_source_children=parent_diagnostic_history_source_children(),
        ordinary_source_children_are_separate_graph_obligations=True,
        independent_BaseA_history_fields_retained=True,
        original_bytes_and_metadata_unchanged=True, original_permission_unchanged=True,
        preserved_copy_readonly_fsynced_and_byte_identical=True,
        documentary_external_or_previous_targets_interpreted=False, documentary_targets_statted_or_opened=False,
        source_or_configuration_promotion=False, archive_or_scientific_acceptance=False,
        original_JSON_or_parent_rewritten=False, generic_reader_or17_parent_scope_changed=False,
        separate_original_JSON_physical_package_entry_forbidden=True,
        future_package_index_and_isolated_restore_acceptance=False)
    expected.update(_fixed_history_saved_authorities("parent13290", saved))
    need(exact_json(saved, expected), "Full saved fixed exact-parent diagnostic history proof changed")
    expected_alias = dict(
        schema="exact-resource-aliases.v2", status=_PARENT_DIAGNOSTIC_HISTORY_ALIAS_STATUS,
        aliases=[dict(original=dict(_PARENT_DIAGNOSTIC_HISTORY_LEAF), archived=copy_receipt,
                      status="READONLY_BYTE_IDENTICAL_ALIAS", role=_PARENT_DIAGNOSTIC_HISTORY_ROLE)],
        historical_unresolved=[], separate_original_JSON_physical_package_entry_forbidden=True,
        scientific_or_source_or_archive_authorization=False)
    need(exact_json(alias_index, expected_alias), "Full fixed history byte alias index changed")
    return True


class ParentDiagnosticHistoryOpaqueLeaf:
    """One fixed history DATA edge, authorized afresh before seen or any resolver."""

    def __init__(self, out, accepted_base):
        self.out = safe_path(out)
        self.active = accepted_base == _PARENT_DIAGNOSTIC_HISTORY_BASE
        self.directory = self.out / "opaque_parent_diagnostic_history_bytes"
        self.observations = []
        self.parent_before = None
        self.authorities_before = None
        self.leaf_before = None
        self.copy_receipt = None
        self.copy_before = None
        self.directory_before = None

    @staticmethod
    def _regular(path):
        path = safe_path(path)
        metadata = stable_metadata(path)
        _parent_diagnostic_history_metadata_shape(metadata, str(path), metadata["bytes"])
        return path, metadata

    def _inputs(self):
        need(self.active, "Fixed history leaf requires the exact accepted BaseA")
        parent, parent_before = self._regular(_PARENT_DIAGNOSTIC_HISTORY_BASE["path"])
        leaf, leaf_before = self._regular(_PARENT_DIAGNOSTIC_HISTORY_LEAF["path"])
        need(rec(parent) == _PARENT_DIAGNOSTIC_HISTORY_BASE and rec(leaf) == _PARENT_DIAGNOSTIC_HISTORY_LEAF,
             "Fixed history parent/original bytes changed")
        parent_bytes = parent.read_bytes()
        content = leaf.read_bytes()
        base = _strict_parent_diagnostic_history_json(parent_bytes.decode("utf-8"))
        need(isinstance(base, dict) and base.get("schema") == "source-delivery-refresh.v3"
             and base.get("status") == "CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY"
             and type(base.get("source_issues")) is int and base["source_issues"] == 0
             and base.get("source_staged") is False,
             "Exact accepted BaseA history authority required")
        history = base.get("original_failure_history", {})
        need(history.get(_PARENT_DIAGNOSTIC_HISTORY_FIELD[1]) == _PARENT_DIAGNOSTIC_HISTORY_LEAF
             and history.get("original13279_failed_executing_source") == _PARENT_DIAGNOSTIC_HISTORY_V4_SOURCE,
             "Exact BaseA field and independent producer/software edges required")
        text = content.decode("utf-8")
        need(not SECRET_RE.search(text) and "-----BEGIN " + "OPENSSH PRIVATE KEY-----" not in text,
             "Potential credential in fixed diagnostic history DATA")
        parent_diagnostic_history_document_shape(_strict_parent_diagnostic_history_json(text))
        need(rec(parent) == _PARENT_DIAGNOSTIC_HISTORY_BASE and rec(leaf) == _PARENT_DIAGNOSTIC_HISTORY_LEAF
             and stable_metadata(parent) == parent_before and stable_metadata(leaf) == leaf_before,
             "Fixed history inputs changed during own-byte/shape readback")
        self._current_authorities = _fixed_history_mapping_inputs("parent13290", base, parent_before)
        need(rec(parent) == _PARENT_DIAGNOSTIC_HISTORY_BASE and rec(leaf) == _PARENT_DIAGNOSTIC_HISTORY_LEAF
             and stable_metadata(parent) == parent_before and stable_metadata(leaf) == leaf_before,
             "Fixed history parent/leaf changed after the last mapping JSON read")
        return parent_before, leaf_before, content

    def _copy(self, content):
        self.directory.mkdir(mode=0o700, exist_ok=False)
        target = self.directory / (_PARENT_DIAGNOSTIC_HISTORY_LEAF["sha256"] + "_13290_diagnostic.OPAQUE.txt")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(target, flags, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o444)
            os.fsync(stream.fileno())
        self.copy_receipt = rec(target)
        need(fp(self.copy_receipt) == fp(_PARENT_DIAGNOSTIC_HISTORY_LEAF) and target.read_bytes() == content,
             "Fixed history opaque preservation changed bytes")
        unused, self.copy_before = self._regular(target)
        self.directory.chmod(0o555)
        fd = os.open(self.directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        self.directory_before = stable_metadata(self.directory)

    def edge(self, receipt, parent, trail, module):
        if not _parent_diagnostic_history_matches(receipt):
            return None
        need(receipt == _PARENT_DIAGNOSTIC_HISTORY_LEAF, "Fixed inherited history requires exact leaf fulltuple")
        selected = _fixed_history_context("parent13290", parent, trail, module)
        parent_before, leaf_before, content = self._inputs()
        if self.copy_receipt is None:
            self.parent_before, self.leaf_before = parent_before, leaf_before
            self.authorities_before = self._current_authorities
            self._copy(content)
        else:
            need(parent_before == self.parent_before and leaf_before == self.leaf_before,
                 "Repeated fixed history observation changed original metadata")
        self.readback()
        observation = dict(
            ordinal=len(self.observations), receipt=dict(_PARENT_DIAGNOSTIC_HISTORY_LEAF),
            parent_manifest=dict(selected["parent_manifest"]), field=list(trail), module=module,
            physical=self.copy_receipt,
            resolution_basis="EXACT_READONLY13290_PARENT_DIAGNOSTIC_HISTORY_DATA_BYTECOPY", role=_PARENT_DIAGNOSTIC_HISTORY_ROLE)
        self.observations.append(observation)
        return dict(receipt=dict(_PARENT_DIAGNOSTIC_HISTORY_LEAF), parent=parent, field=list(trail), module=module,
                    physical=self.copy_receipt, resolution_basis=observation["resolution_basis"],
                    role=_PARENT_DIAGNOSTIC_HISTORY_ROLE, raw_bytes_preserved=True,
                    documentary_receipt_children_interpreted=False, ordinary_Source_children_explicitly_enqueued=True,
                    source_or_configuration_promotion=False)

    def source_child_context(self, receipt, parent, trail, module):
        if parent != _PARENT_DIAGNOSTIC_HISTORY_LEAF["path"]:
            return False
        need(any(x["module"] == module for x in self.observations)
             and module in _PARENT_DIAGNOSTIC_HISTORY_MODULES and type(trail) is tuple,
             "Source2 context requires a prior exact authorized13290 DATA observation")
        need(any(receipt == child["receipt"] and trail == tuple(child["field"])
                 for child in parent_diagnostic_history_source_children()),
             "Only the two unchanged fixed ordinary Source child contexts are generated")
        return True

    def readback(self):
        need(self.copy_receipt is not None, "Fixed history DATA preservation has not occurred")
        parent_meta, leaf_meta, content = self._inputs()
        need(exact_json(self._current_authorities, self.authorities_before),
             "Fixed inherited history four-authority native metadata drifted")
        need(parent_meta == self.parent_before and leaf_meta == self.leaf_before,
             "Fixed history original/parent stable metadata drifted")
        copy_path, copy_meta = self._regular(self.copy_receipt["path"])
        need(_parent_diagnostic_history_copy_structure(self.copy_receipt) == copy_path
             and copy_meta == self.copy_before and rec(copy_path) == self.copy_receipt
             and copy_path.read_bytes() == content and stable_metadata(copy_path) == self.copy_before,
             "Fixed history readonly copy bytes/metadata drifted")
        directory = safe_path(self.directory)
        directory_meta = stable_metadata(directory)
        _parent_diagnostic_history_metadata_shape(directory_meta, str(directory), directory=True)
        need(directory_meta == self.directory_before
             and {p.name for p in directory.iterdir()} == {copy_path.name},
             "Fixed history555 directory metadata or exact one-file universe changed")
        return True

    def require_complete(self):
        if self.active:
            need(any(x["module"] == "default_workflow_integration" for x in self.observations),
                 "Actual source graph must observe the fixed default history edge")
            self.readback()
        else:
            need(not self.observations and self.copy_receipt is None,
                 "No inventory history exception outside exact BaseA")
        return self.active

    def alias_index(self):
        self.readback()
        return dict(
            schema="exact-resource-aliases.v2", status=_PARENT_DIAGNOSTIC_HISTORY_ALIAS_STATUS,
            aliases=[dict(original=dict(_PARENT_DIAGNOSTIC_HISTORY_LEAF), archived=self.copy_receipt,
                          status="READONLY_BYTE_IDENTICAL_ALIAS", role=_PARENT_DIAGNOSTIC_HISTORY_ROLE)],
            historical_unresolved=[], separate_original_JSON_physical_package_entry_forbidden=True,
            scientific_or_source_or_archive_authorization=False)

    def proof(self):
        need(self.require_complete(), "Actual fixed exact-parent diagnostic history observations required")
        return dict(
            schema=_PARENT_DIAGNOSTIC_HISTORY_PROOF_SCHEMA, status=_PARENT_DIAGNOSTIC_HISTORY_PROOF_STATUS,
            parent_manifest=dict(_PARENT_DIAGNOSTIC_HISTORY_BASE), original_diagnostic_data=dict(_PARENT_DIAGNOSTIC_HISTORY_LEAF),
            source_field=list(_PARENT_DIAGNOSTIC_HISTORY_FIELD), role=_PARENT_DIAGNOSTIC_HISTORY_ROLE, allowed_modules=list(_PARENT_DIAGNOSTIC_HISTORY_MODULES),
            module_policy=dict(default_workflow_integration="FINITE_FIVE_ROWS_ACTUAL_RUNTIME_PARENT_FIELD_AUTHENTICATION_REQUIRED",
                               final_delivery_tools="PROSPECTIVE_SAME_FIVE_ROWS_NOT_REQUIRED"),
            preserved_opaque_data=self.copy_receipt,
            parent_metadata_before=self.parent_before,
            parent_metadata_after=stable_metadata(_PARENT_DIAGNOSTIC_HISTORY_BASE["path"]),
            original_metadata_before=self.leaf_before,
            original_metadata_after=stable_metadata(_PARENT_DIAGNOSTIC_HISTORY_LEAF["path"]),
            preserved_metadata=self.copy_before, copy_directory_metadata=self.directory_before,
            observations=list(self.observations), authorized_observation_n=len(self.observations),
            actual_default_observation_n=sum(x["module"] == "default_workflow_integration" for x in self.observations),
            actual_finaltools_observation_n=sum(x["module"] == "final_delivery_tools" for x in self.observations),
            embedded_receipt_occurrence_n=5, embedded_unique_fingerprint_n=4,
            ordinary_source_children=parent_diagnostic_history_source_children(),
            ordinary_source_children_are_separate_graph_obligations=True,
            independent_BaseA_history_fields_retained=True, original_bytes_and_metadata_unchanged=True,
            original_permission_unchanged=True, preserved_copy_readonly_fsynced_and_byte_identical=True,
            documentary_external_or_previous_targets_interpreted=False, documentary_targets_statted_or_opened=False,
            source_or_configuration_promotion=False, archive_or_scientific_acceptance=False,
            original_JSON_or_parent_rewritten=False, generic_reader_or17_parent_scope_changed=False,
            separate_original_JSON_physical_package_entry_forbidden=True,
            future_package_index_and_isolated_restore_acceptance=False,
            **_fixed_history_authority_projection("parent13290", self.authorities_before))


def verify_parent_diagnostic_history_preservation(saved, alias_index, allocation):
    """Current owned-CPU object verifier; pure validator remains separately usable."""
    parent_diagnostic_history_proof_shape(saved, alias_index, allocation)
    pointer = saved["exact_alias_index"]
    actual_index, index_before = _parent_diagnostic_history_control_readback(pointer)
    need(exact_json(actual_index, alias_index), "Saved fixed parent-diagnostic alias object differs")
    copy_receipt = saved["preserved_opaque_data"]
    path = _parent_diagnostic_history_copy_structure(copy_receipt)
    scope = ParentDiagnosticHistoryOpaqueLeaf(path.parent.parent, _PARENT_DIAGNOSTIC_HISTORY_BASE)
    scope.parent_before = saved["parent_metadata_before"]
    scope.authorities_before = saved["authority_metadata_before"]
    scope.leaf_before = saved["original_metadata_before"]
    scope.copy_receipt = copy_receipt
    scope.copy_before = saved["preserved_metadata"]
    scope.directory_before = saved["copy_directory_metadata"]
    scope.observations = saved["observations"]
    scope.require_complete()
    expected = dict(scope.proof(), exact_alias_index=pointer, allocation=allocation)
    need(exact_json(saved, expected), "Current complete fixed parent-diagnostic history proof differs")
    final_index, unused = _parent_diagnostic_history_control_readback(pointer, index_before)
    need(exact_json(final_index, alias_index), "Saved fixed parent-diagnostic alias changed after inputs")
    _fixed_history_authority_fence("parent13290", scope.authorities_before)
    _fixed_history_native_union_sweep(_fixed_history_saved_native_records(saved) + [index_before])
    return True


# Fixed historical worker CONTROL compatibility; no generic symlink or JSON waiver.
_WORKER_MODULE = "default_workflow_integration"
_WORKER_ROLE = "EXACT_FINITE_WORKER_CONTROL_RECEIPT_READBACK"
_WORKER_BASE = INHERITED_ENTRYPOINT_BASE
_WORKER_CLOSURE = json.loads(r'''{
  "path": "/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/source_receipt_closure.json",
  "bytes": 14961330,
  "sha256": "7e32c2b8196a873874d12747caf4b1b4b829808537e8770c83b3124595f138ff"
}''')
_WORKER_PARENTS = json.loads(r'''[
  {
    "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/runs/worker_validation_13096/raw.json",
    "sha256": "53c53984a5cc0e223b653755d0293688208bcfcae46b3f7f7a3e037df387d868",
    "bytes": 8452
  },
  {
    "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
    "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
    "bytes": 103116
  }
]''')
_WORKER_TABLE = json.loads(r'''[
  {
    "index": 17573,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/runs/worker_validation_13096/raw_view/bc_BBF_b10_single_no_template/worker.json",
      "sha256": "b5a9382777fe2376172c52042f7fcde745ecf580ecd42a0384db8e175d78ebef",
      "bytes": 9487
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/runs/bbf_launch_13067/raw/bc_BBF_b10_single_no_template/worker.json",
      "sha256": "b5a9382777fe2376172c52042f7fcde745ecf580ecd42a0384db8e175d78ebef",
      "bytes": 9487
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/runs/worker_validation_13096/raw.json",
      "sha256": "53c53984a5cc0e223b653755d0293688208bcfcae46b3f7f7a3e037df387d868",
      "bytes": 8452
    },
    "field": [
      "jobs",
      "0",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/runs/worker_validation_13096/raw_view/bc_BBF_b10_single_no_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/runs/bbf_launch_13067/raw/bc_BBF_b10_single_no_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/runs/worker_validation_13096/raw_view/bc_BBF_b10_single_no_template/worker.json",
        "sha256": "b5a9382777fe2376172c52042f7fcde745ecf580ecd42a0384db8e175d78ebef",
        "bytes": 9487
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/runs/worker_validation_13096/raw.json",
      "field": [
        "jobs",
        "0",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/runs/worker_validation_13096/raw_view/bc_BBF_b10_single_no_template/worker.json",
        "bytes": 9487,
        "sha256": "b5a9382777fe2376172c52042f7fcde745ecf580ecd42a0384db8e175d78ebef"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18724,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b8_single_target_only_9HAG_template/worker.json",
      "sha256": "3e0a866425f255270ac350d5eb4d78dbe328951afeca44138bd32e7cab278018",
      "bytes": 16178
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b8_single_target_only_9HAG_template/worker.json",
      "sha256": "3e0a866425f255270ac350d5eb4d78dbe328951afeca44138bd32e7cab278018",
      "bytes": 16178
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "21",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b8_single_target_only_9HAG_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b8_single_target_only_9HAG_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b8_single_target_only_9HAG_template/worker.json",
        "sha256": "3e0a866425f255270ac350d5eb4d78dbe328951afeca44138bd32e7cab278018",
        "bytes": 16178
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "21",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b8_single_target_only_9HAG_template/worker.json",
        "bytes": 16178,
        "sha256": "3e0a866425f255270ac350d5eb4d78dbe328951afeca44138bd32e7cab278018"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18725,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b8_single_no_template/worker.json",
      "sha256": "c137e81756a8adf94a7ad9cff04abad68d741f575fb0d9bfc0d44fa146cf13b8",
      "bytes": 11155
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b8_single_no_template/worker.json",
      "sha256": "c137e81756a8adf94a7ad9cff04abad68d741f575fb0d9bfc0d44fa146cf13b8",
      "bytes": 11155
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "20",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b8_single_no_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b8_single_no_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b8_single_no_template/worker.json",
        "sha256": "c137e81756a8adf94a7ad9cff04abad68d741f575fb0d9bfc0d44fa146cf13b8",
        "bytes": 11155
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "20",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b8_single_no_template/worker.json",
        "bytes": 11155,
        "sha256": "c137e81756a8adf94a7ad9cff04abad68d741f575fb0d9bfc0d44fa146cf13b8"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18726,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b7_single_target_only_9HAG_template/worker.json",
      "sha256": "28b8cdc7860380f952493ec2f23ede68108fe904c0005484a842d470ef46e4bb",
      "bytes": 11323
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b7_single_target_only_9HAG_template/worker.json",
      "sha256": "28b8cdc7860380f952493ec2f23ede68108fe904c0005484a842d470ef46e4bb",
      "bytes": 11323
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "19",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b7_single_target_only_9HAG_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b7_single_target_only_9HAG_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b7_single_target_only_9HAG_template/worker.json",
        "sha256": "28b8cdc7860380f952493ec2f23ede68108fe904c0005484a842d470ef46e4bb",
        "bytes": 11323
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "19",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b7_single_target_only_9HAG_template/worker.json",
        "bytes": 11323,
        "sha256": "28b8cdc7860380f952493ec2f23ede68108fe904c0005484a842d470ef46e4bb"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18727,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b7_single_no_template/worker.json",
      "sha256": "59ea3ac3e59b7b20fc5af1acfb752bbd688016f1e5b322903bc187a44d2f40c5",
      "bytes": 11155
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b7_single_no_template/worker.json",
      "sha256": "59ea3ac3e59b7b20fc5af1acfb752bbd688016f1e5b322903bc187a44d2f40c5",
      "bytes": 11155
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "18",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b7_single_no_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b7_single_no_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b7_single_no_template/worker.json",
        "sha256": "59ea3ac3e59b7b20fc5af1acfb752bbd688016f1e5b322903bc187a44d2f40c5",
        "bytes": 11155
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "18",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b7_single_no_template/worker.json",
        "bytes": 11155,
        "sha256": "59ea3ac3e59b7b20fc5af1acfb752bbd688016f1e5b322903bc187a44d2f40c5"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18728,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b6_single_target_only_9HAG_template/worker.json",
      "sha256": "e06899c2abf5df5d51a98648aa81e24c7931595c50461fa4f3ea4cae2a711455",
      "bytes": 11324
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b6_single_target_only_9HAG_template/worker.json",
      "sha256": "e06899c2abf5df5d51a98648aa81e24c7931595c50461fa4f3ea4cae2a711455",
      "bytes": 11324
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "17",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b6_single_target_only_9HAG_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b6_single_target_only_9HAG_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b6_single_target_only_9HAG_template/worker.json",
        "sha256": "e06899c2abf5df5d51a98648aa81e24c7931595c50461fa4f3ea4cae2a711455",
        "bytes": 11324
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "17",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b6_single_target_only_9HAG_template/worker.json",
        "bytes": 11324,
        "sha256": "e06899c2abf5df5d51a98648aa81e24c7931595c50461fa4f3ea4cae2a711455"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18729,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b6_single_no_template/worker.json",
      "sha256": "86f5735b1b36be6cc58763bec33bd449da08bf0c10eb57d83394d0f06e1eea6e",
      "bytes": 11156
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b6_single_no_template/worker.json",
      "sha256": "86f5735b1b36be6cc58763bec33bd449da08bf0c10eb57d83394d0f06e1eea6e",
      "bytes": 11156
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "16",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b6_single_no_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b6_single_no_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b6_single_no_template/worker.json",
        "sha256": "86f5735b1b36be6cc58763bec33bd449da08bf0c10eb57d83394d0f06e1eea6e",
        "bytes": 11156
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "16",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b6_single_no_template/worker.json",
        "bytes": 11156,
        "sha256": "86f5735b1b36be6cc58763bec33bd449da08bf0c10eb57d83394d0f06e1eea6e"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18730,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b5_single_target_only_9HAG_template/worker.json",
      "sha256": "ccd50bee43850015e20c40055b6a0c11e93e1de407157427a77259990ebe9ca7",
      "bytes": 11321
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b5_single_target_only_9HAG_template/worker.json",
      "sha256": "ccd50bee43850015e20c40055b6a0c11e93e1de407157427a77259990ebe9ca7",
      "bytes": 11321
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "15",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b5_single_target_only_9HAG_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b5_single_target_only_9HAG_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b5_single_target_only_9HAG_template/worker.json",
        "sha256": "ccd50bee43850015e20c40055b6a0c11e93e1de407157427a77259990ebe9ca7",
        "bytes": 11321
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "15",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b5_single_target_only_9HAG_template/worker.json",
        "bytes": 11321,
        "sha256": "ccd50bee43850015e20c40055b6a0c11e93e1de407157427a77259990ebe9ca7"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18731,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b5_single_no_template/worker.json",
      "sha256": "40043cc1cd218ec82f3da1f53b826064e21028af8c96269aec0e7dd33fbe04ce",
      "bytes": 11153
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b5_single_no_template/worker.json",
      "sha256": "40043cc1cd218ec82f3da1f53b826064e21028af8c96269aec0e7dd33fbe04ce",
      "bytes": 11153
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "14",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b5_single_no_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b5_single_no_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b5_single_no_template/worker.json",
        "sha256": "40043cc1cd218ec82f3da1f53b826064e21028af8c96269aec0e7dd33fbe04ce",
        "bytes": 11153
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "14",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b5_single_no_template/worker.json",
        "bytes": 11153,
        "sha256": "40043cc1cd218ec82f3da1f53b826064e21028af8c96269aec0e7dd33fbe04ce"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18732,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b4_single_target_only_9HAG_template/worker.json",
      "sha256": "7f35bdf056eb87f40441c866248458db1f152af21c0fcdc3b3e28dfa662a17f3",
      "bytes": 11321
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b4_single_target_only_9HAG_template/worker.json",
      "sha256": "7f35bdf056eb87f40441c866248458db1f152af21c0fcdc3b3e28dfa662a17f3",
      "bytes": 11321
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "13",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b4_single_target_only_9HAG_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b4_single_target_only_9HAG_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b4_single_target_only_9HAG_template/worker.json",
        "sha256": "7f35bdf056eb87f40441c866248458db1f152af21c0fcdc3b3e28dfa662a17f3",
        "bytes": 11321
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "13",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b4_single_target_only_9HAG_template/worker.json",
        "bytes": 11321,
        "sha256": "7f35bdf056eb87f40441c866248458db1f152af21c0fcdc3b3e28dfa662a17f3"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18733,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b4_single_no_template/worker.json",
      "sha256": "d61297dc08a5c82d6c970341d2dc4a319340c0a37e572ee0749b8f14ba7190d2",
      "bytes": 11155
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b4_single_no_template/worker.json",
      "sha256": "d61297dc08a5c82d6c970341d2dc4a319340c0a37e572ee0749b8f14ba7190d2",
      "bytes": 11155
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "12",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b4_single_no_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b4_single_no_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b4_single_no_template/worker.json",
        "sha256": "d61297dc08a5c82d6c970341d2dc4a319340c0a37e572ee0749b8f14ba7190d2",
        "bytes": 11155
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "12",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b4_single_no_template/worker.json",
        "bytes": 11155,
        "sha256": "d61297dc08a5c82d6c970341d2dc4a319340c0a37e572ee0749b8f14ba7190d2"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18734,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b3_single_target_only_9HAG_template/worker.json",
      "sha256": "f92e149fa35a6835701f4e3f86f1e1c9bd73428c3df262458a42d06f4680ffc3",
      "bytes": 11331
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b3_single_target_only_9HAG_template/worker.json",
      "sha256": "f92e149fa35a6835701f4e3f86f1e1c9bd73428c3df262458a42d06f4680ffc3",
      "bytes": 11331
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "11",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b3_single_target_only_9HAG_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b3_single_target_only_9HAG_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b3_single_target_only_9HAG_template/worker.json",
        "sha256": "f92e149fa35a6835701f4e3f86f1e1c9bd73428c3df262458a42d06f4680ffc3",
        "bytes": 11331
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "11",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b3_single_target_only_9HAG_template/worker.json",
        "bytes": 11331,
        "sha256": "f92e149fa35a6835701f4e3f86f1e1c9bd73428c3df262458a42d06f4680ffc3"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18735,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b3_single_no_template/worker.json",
      "sha256": "a51d9ed02c273a091e2cce2855fdb5f77bae7cad227f7c67b7f2a1393a8623f6",
      "bytes": 11162
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b3_single_no_template/worker.json",
      "sha256": "a51d9ed02c273a091e2cce2855fdb5f77bae7cad227f7c67b7f2a1393a8623f6",
      "bytes": 11162
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "10",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b3_single_no_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b3_single_no_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b3_single_no_template/worker.json",
        "sha256": "a51d9ed02c273a091e2cce2855fdb5f77bae7cad227f7c67b7f2a1393a8623f6",
        "bytes": 11162
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "10",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b3_single_no_template/worker.json",
        "bytes": 11162,
        "sha256": "a51d9ed02c273a091e2cce2855fdb5f77bae7cad227f7c67b7f2a1393a8623f6"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18736,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b2_single_target_only_9HAG_template/worker.json",
      "sha256": "3ee66d61fb8309f97e3ce9636d5c59f0d343ea67df391de1d85a37147f10994c",
      "bytes": 11326
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b2_single_target_only_9HAG_template/worker.json",
      "sha256": "3ee66d61fb8309f97e3ce9636d5c59f0d343ea67df391de1d85a37147f10994c",
      "bytes": 11326
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "9",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b2_single_target_only_9HAG_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b2_single_target_only_9HAG_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b2_single_target_only_9HAG_template/worker.json",
        "sha256": "3ee66d61fb8309f97e3ce9636d5c59f0d343ea67df391de1d85a37147f10994c",
        "bytes": 11326
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "9",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b2_single_target_only_9HAG_template/worker.json",
        "bytes": 11326,
        "sha256": "3ee66d61fb8309f97e3ce9636d5c59f0d343ea67df391de1d85a37147f10994c"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18737,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b2_single_no_template/worker.json",
      "sha256": "c010fd6555e126b165e8c8cff55d237ab8f8b793e0295b525c9b670fde0bb241",
      "bytes": 11157
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b2_single_no_template/worker.json",
      "sha256": "c010fd6555e126b165e8c8cff55d237ab8f8b793e0295b525c9b670fde0bb241",
      "bytes": 11157
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "8",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b2_single_no_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b2_single_no_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b2_single_no_template/worker.json",
        "sha256": "c010fd6555e126b165e8c8cff55d237ab8f8b793e0295b525c9b670fde0bb241",
        "bytes": 11157
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "8",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b2_single_no_template/worker.json",
        "bytes": 11157,
        "sha256": "c010fd6555e126b165e8c8cff55d237ab8f8b793e0295b525c9b670fde0bb241"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18738,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b13_single_target_only_9HAG_template/worker.json",
      "sha256": "1a1fd0269d60434794ddb5625017c8a6767964dee92371420d3fbc066c2c9110",
      "bytes": 11335
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b13_single_target_only_9HAG_template/worker.json",
      "sha256": "1a1fd0269d60434794ddb5625017c8a6767964dee92371420d3fbc066c2c9110",
      "bytes": 11335
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "7",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b13_single_target_only_9HAG_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b13_single_target_only_9HAG_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b13_single_target_only_9HAG_template/worker.json",
        "sha256": "1a1fd0269d60434794ddb5625017c8a6767964dee92371420d3fbc066c2c9110",
        "bytes": 11335
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "7",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b13_single_target_only_9HAG_template/worker.json",
        "bytes": 11335,
        "sha256": "1a1fd0269d60434794ddb5625017c8a6767964dee92371420d3fbc066c2c9110"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18739,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b13_single_no_template/worker.json",
      "sha256": "0362c375ecb5b180ae7808ad08fb56db85b2ed396c3038ad965d7c878cf0e54e",
      "bytes": 11146
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b13_single_no_template/worker.json",
      "sha256": "0362c375ecb5b180ae7808ad08fb56db85b2ed396c3038ad965d7c878cf0e54e",
      "bytes": 11146
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "6",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b13_single_no_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b13_single_no_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b13_single_no_template/worker.json",
        "sha256": "0362c375ecb5b180ae7808ad08fb56db85b2ed396c3038ad965d7c878cf0e54e",
        "bytes": 11146
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "6",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b13_single_no_template/worker.json",
        "bytes": 11146,
        "sha256": "0362c375ecb5b180ae7808ad08fb56db85b2ed396c3038ad965d7c878cf0e54e"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18740,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b12_single_target_only_9HAG_template/worker.json",
      "sha256": "d170561b7499bc4fa8176159b8aec1bc2c508fcb7ee69380752fe4d35df0c747",
      "bytes": 11313
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b12_single_target_only_9HAG_template/worker.json",
      "sha256": "d170561b7499bc4fa8176159b8aec1bc2c508fcb7ee69380752fe4d35df0c747",
      "bytes": 11313
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "5",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b12_single_target_only_9HAG_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b12_single_target_only_9HAG_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b12_single_target_only_9HAG_template/worker.json",
        "sha256": "d170561b7499bc4fa8176159b8aec1bc2c508fcb7ee69380752fe4d35df0c747",
        "bytes": 11313
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "5",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b12_single_target_only_9HAG_template/worker.json",
        "bytes": 11313,
        "sha256": "d170561b7499bc4fa8176159b8aec1bc2c508fcb7ee69380752fe4d35df0c747"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18741,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b12_single_no_template/worker.json",
      "sha256": "05f38d5268b7f68a4723d3f639e59ec46f6bb85cdde54267e289bc68dde71ce2",
      "bytes": 11145
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b12_single_no_template/worker.json",
      "sha256": "05f38d5268b7f68a4723d3f639e59ec46f6bb85cdde54267e289bc68dde71ce2",
      "bytes": 11145
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "4",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b12_single_no_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b12_single_no_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b12_single_no_template/worker.json",
        "sha256": "05f38d5268b7f68a4723d3f639e59ec46f6bb85cdde54267e289bc68dde71ce2",
        "bytes": 11145
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "4",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b12_single_no_template/worker.json",
        "bytes": 11145,
        "sha256": "05f38d5268b7f68a4723d3f639e59ec46f6bb85cdde54267e289bc68dde71ce2"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18742,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b11_single_target_only_9HAG_template/worker.json",
      "sha256": "6482f965378ee1cc092160a66f9b8873f0ce7a392df27cecaf3de1c9e9547208",
      "bytes": 11314
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b11_single_target_only_9HAG_template/worker.json",
      "sha256": "6482f965378ee1cc092160a66f9b8873f0ce7a392df27cecaf3de1c9e9547208",
      "bytes": 11314
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "3",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b11_single_target_only_9HAG_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b11_single_target_only_9HAG_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b11_single_target_only_9HAG_template/worker.json",
        "sha256": "6482f965378ee1cc092160a66f9b8873f0ce7a392df27cecaf3de1c9e9547208",
        "bytes": 11314
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "3",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b11_single_target_only_9HAG_template/worker.json",
        "bytes": 11314,
        "sha256": "6482f965378ee1cc092160a66f9b8873f0ce7a392df27cecaf3de1c9e9547208"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18743,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b11_single_no_template/worker.json",
      "sha256": "d097f3d8dbf421ec863108f1e1955e0630ad7fa4c6f55c427ce0bb80df10607e",
      "bytes": 11146
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b11_single_no_template/worker.json",
      "sha256": "d097f3d8dbf421ec863108f1e1955e0630ad7fa4c6f55c427ce0bb80df10607e",
      "bytes": 11146
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "2",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b11_single_no_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b11_single_no_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b11_single_no_template/worker.json",
        "sha256": "d097f3d8dbf421ec863108f1e1955e0630ad7fa4c6f55c427ce0bb80df10607e",
        "bytes": 11146
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "2",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b11_single_no_template/worker.json",
        "bytes": 11146,
        "sha256": "d097f3d8dbf421ec863108f1e1955e0630ad7fa4c6f55c427ce0bb80df10607e"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18744,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b10_single_target_only_9HAG_template/worker.json",
      "sha256": "5c19b0056464ed985437e2d99f3aa2e5d5c16588de4df3aadc4b1008095831ef",
      "bytes": 11320
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b10_single_target_only_9HAG_template/worker.json",
      "sha256": "5c19b0056464ed985437e2d99f3aa2e5d5c16588de4df3aadc4b1008095831ef",
      "bytes": 11320
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "1",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b10_single_target_only_9HAG_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/allocation_v2_13103/bbf_remaining/raw/bc_BBF_b10_single_target_only_9HAG_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b10_single_target_only_9HAG_template/worker.json",
        "sha256": "5c19b0056464ed985437e2d99f3aa2e5d5c16588de4df3aadc4b1008095831ef",
        "bytes": 11320
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "1",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b10_single_target_only_9HAG_template/worker.json",
        "bytes": 11320,
        "sha256": "5c19b0056464ed985437e2d99f3aa2e5d5c16588de4df3aadc4b1008095831ef"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  },
  {
    "index": 18745,
    "logical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b10_single_no_template/worker.json",
      "sha256": "b5a9382777fe2376172c52042f7fcde745ecf580ecd42a0384db8e175d78ebef",
      "bytes": 9487
    },
    "canonical": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/runs/bbf_launch_13067/raw/bc_BBF_b10_single_no_template/worker.json",
      "sha256": "b5a9382777fe2376172c52042f7fcde745ecf580ecd42a0384db8e175d78ebef",
      "bytes": 9487
    },
    "parent": {
      "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "sha256": "bec1aa4a6eba60da9c9e2d465ea27e71d7bddb2a740e535c793a2e946058aca7",
      "bytes": 103116
    },
    "field": [
      "jobs",
      "0",
      "worker"
    ],
    "link_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b10_single_no_template",
    "link_text": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/runs/bbf_launch_13067/raw/bc_BBF_b10_single_no_template",
    "base_edge": {
      "receipt": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b10_single_no_template/worker.json",
        "sha256": "b5a9382777fe2376172c52042f7fcde745ecf580ecd42a0384db8e175d78ebef",
        "bytes": 9487
      },
      "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw.json",
      "field": [
        "jobs",
        "0",
        "worker"
      ],
      "physical": {
        "path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/raw_view/bc_BBF_b10_single_no_template/worker.json",
        "bytes": 9487,
        "sha256": "b5a9382777fe2376172c52042f7fcde745ecf580ecd42a0384db8e175d78ebef"
      },
      "resolution_basis": "EXACT_ORIGINAL",
      "relative_context": null,
      "current_recovered_relative_context": null,
      "finite_exact_source_alias_context": null,
      "role": "EXACT_TEXT_RECEIPT_READBACK"
    }
  }
]''')


def _worker_related(receipt):
    receipt_shape(receipt)
    canonical = {row["canonical"]["path"]: row["canonical"] for row in _WORKER_TABLE}
    if receipt["path"] in canonical:
        need(receipt == canonical[receipt["path"]],
             "Known ordinary canonical worker full tuple changed")
        return False
    return (receipt["path"] in {row["logical"]["path"] for row in _WORKER_TABLE}
            or fp(receipt) in {fp(row["logical"]) for row in _WORKER_TABLE})


def reject_worker_declaration(receipt):
    receipt_shape(receipt)
    need(receipt["path"] not in {row["logical"]["path"] for row in _WORKER_TABLE}
         and fp(receipt) not in {fp(row["logical"]) for row in _WORKER_TABLE},
         "Fixed worker CONTROL requires exact original parent/field/module, never direct declarations")


def _worker_clone(value):
    return json.loads(json.dumps(value, allow_nan=False))


def _worker_regular(path, readonly):
    path = safe_path(path)
    metadata = stable_metadata(path)
    need(stat.S_ISREG(metadata["mode"]) and metadata["nlink"] == 1,
         "Finite worker input must be a nonsymlink single-link regular file")
    if readonly:
        need(stat.S_IMODE(metadata["mode"]) == 0o444,
             "Finite worker authority/copy must remain0444")
    return path, metadata


def _worker_exact_bytes(receipt, readonly):
    receipt_shape(receipt)
    path, before = _worker_regular(receipt["path"], readonly)
    content = path.read_bytes()
    need((len(content), hashlib.sha256(content).hexdigest()) == fp(receipt),
         "Finite worker exact authority/control bytes changed")
    need(stable_metadata(path) == before, "Finite worker byte read metadata drift")
    return content, before


def _worker_field(value, trail):
    for token in trail:
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def _worker_authority():
    need(len(_WORKER_TABLE) == 23 and len({row["index"] for row in _WORKER_TABLE}) == 23,
         "Exactly23 fixed worker context slots required")
    targets = {key(row["canonical"]) for row in _WORKER_TABLE}
    need(len(targets) == 22 and len(_WORKER_PARENTS) == 2,
         "Exactly22 canonical worker targets and two raw parents required")
    base_bytes, base_metadata = _worker_exact_bytes(_WORKER_BASE, True)
    closure_bytes, closure_metadata = _worker_exact_bytes(_WORKER_CLOSURE, True)
    base = _strict_vendor_json(base_bytes)
    closure = _strict_vendor_json(closure_bytes)
    need(base.get("source_closure") == _WORKER_CLOSURE
         and closure.get("schema") == "benchmark-source-receipt-closure.v1",
         "Fixed accepted Base/C worker authority differs")
    parents = {}
    metadata = {"base": base_metadata, "closure": closure_metadata, "parents": []}
    for parent in _WORKER_PARENTS:
        content, before = _worker_exact_bytes(parent, False)
        need(stat.S_IMODE(before["mode"]) == 0o664,
             "Original worker parent permission must remain0664")
        parents[parent["path"]] = _strict_vendor_json(content)
        metadata["parents"].append(before)
    for row in _WORKER_TABLE:
        need(closure["edges"][row["index"]] == row["base_edge"],
             "Fixed accepted BaseC worker edge changed")
        need(row["base_edge"]["receipt"] == row["logical"]
             and row["base_edge"]["physical"] == row["logical"]
             and row["base_edge"]["parent"] == row["parent"]["path"]
             and row["base_edge"]["field"] == row["field"]
             and row["base_edge"]["role"] == "EXACT_TEXT_RECEIPT_READBACK"
             and row["parent"] in _WORKER_PARENTS,
             "Fixed worker table is not the exact accepted context")
        need(_worker_field(parents[row["parent"]["path"]], row["field"]) == row["logical"],
             "Exact raw parent worker field forked")
    return metadata


def _worker_source(row):
    logical = Path(row["logical"]["path"])
    canonical = Path(row["canonical"]["path"])
    link = Path(row["link_path"])
    need(logical.is_absolute() and logical.is_relative_to(R)
         and canonical.is_absolute() and canonical.is_relative_to(R),
         "Fixed worker paths must remain inside authority")
    need(logical.parent == link and canonical.parent == Path(row["link_text"]),
         "Fixed worker logical/link/canonical layout differs")
    # The sole permitted link is checked literally. All canonical components
    # still go through unchanged safe_path; no generic resolve is a byte reader.
    safe_path(link.parent)
    link_before = stable_metadata(link)
    need(stat.S_ISLNK(link_before["mode"]) and link_before["nlink"] == 1
         and stat.S_IMODE(link_before["mode"]) == 0o777
         and os.readlink(link) == row["link_text"],
         "Exact single-link worker raw_view target changed")
    canonical_path, canonical_before = _worker_regular(canonical, False)
    need(logical.resolve() == canonical,
         "Fixed worker logical path resolves to a different canonical target")
    for node in [logical] + list(logical.parents):
        if node == R.parent:
            break
        if node != link:
            need(not stat.S_ISLNK(node.lstat().st_mode),
                 "Unknown worker symlink component forbidden")
    logical_before = stable_metadata(logical)
    need(stat.S_ISREG(logical_before["mode"]) and logical_before["nlink"] == 1
         and stat.S_IMODE(logical_before["mode"]) == 0o664
         and stat.S_IMODE(canonical_before["mode"]) == 0o664,
         "Original worker single-link permission must remain0664")
    need({k: v for k, v in logical_before.items() if k != "path"}
         == {k: v for k, v in canonical_before.items() if k != "path"},
         "Fixed logical worker and canonical input are not the same file identity")
    content = canonical_path.read_bytes()
    need((len(content), hashlib.sha256(content).hexdigest()) == fp(row["canonical"])
         == fp(row["logical"]), "Exact canonical worker bytes changed")
    obj = _strict_vendor_json(content)
    need(isinstance(obj, (dict, list)), "Worker CONTROL must remain complete structured JSON")
    need(stable_metadata(link) == link_before and os.readlink(link) == row["link_text"]
         and logical.resolve() == canonical
         and stable_metadata(logical) == logical_before
         and stable_metadata(canonical_path) == canonical_before,
         "Worker canonical/link metadata drifted during read")
    return content, obj, dict(logical=logical_before, canonical=canonical_before,
                              link=link_before, link_text=row["link_text"])


class FiniteWorkerControlAliases:
    """Fixed23 prospective historical-default contexts, checked before dedup."""

    def __init__(self, out, base_receipt, closure_receipt):
        self.out = safe_path(out)
        self.enabled = base_receipt == _WORKER_BASE
        if self.enabled:
            need(closure_receipt == _WORKER_CLOSURE,
                 "Actual worker scope requires exact accepted BaseC descriptor")
        self.authority_before = None
        self.source_before = {}
        self.copies = {}
        self.copy_before = {}
        self.children = {}
        self.observations = []
        self.seen_indices = set()
        self.directory = self.out / "finite_worker_control_bytes"
        self.directory_before = None
        self.finalized = False
        self.target_keys = sorted({key(row["canonical"]) for row in _WORKER_TABLE})

    def begin(self):
        if not self.enabled:
            return False
        authority = _worker_authority()
        source_metadata = {}
        for row in _WORKER_TABLE:
            content, obj, metadata = _worker_source(row)
            source_metadata[row["index"]] = metadata
        if self.authority_before is None:
            self.authority_before = authority
            self.source_before = source_metadata
        need(authority == self.authority_before
             and source_metadata == self.source_before,
             "Whole fixed worker authority/input metadata drifted before traversal")
        return True

    def _context(self, receipt, parent, trail, module):
        if not _worker_related(receipt):
            return None
        need(self.enabled, "Fixed worker CONTROL cannot enter an unrelated base")
        matches = [row for row in _WORKER_TABLE if row["logical"] == receipt]
        need(len(matches) == 1 and parent == matches[0]["parent"]["path"]
             and type(trail) is tuple and list(trail) == matches[0]["field"]
             and module == _WORKER_MODULE,
             "Worker CONTROL requires its exact full receipt/parent/field/default module")
        return matches[0]

    def _copy_name(self, row):
        slot = self.target_keys.index(key(row["canonical"]))
        return "%03d_%s_worker.json" % (slot, row["canonical"]["sha256"])

    def _copy(self, row, content):
        target_key = key(row["canonical"])
        if target_key in self.copies:
            path, metadata = _worker_regular(self.copies[target_key]["path"], True)
            need(metadata == self.copy_before[target_key]
                 and path.read_bytes() == content
                 and rec(path) == self.copies[target_key],
                 "Previously owned canonical worker copy changed")
            return
        need(not self.finalized, "No worker copy may be added after finalization")
        if not self.copies:
            self.directory.mkdir(exist_ok=False)
        path = self.directory / self._copy_name(row)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o444)
            os.fsync(stream.fileno())
        descriptor = rec(path)
        path, metadata = _worker_regular(path, True)
        need(fp(descriptor) == fp(row["canonical"]) and path.read_bytes() == content
             and stable_metadata(path) == metadata,
             "Exclusive readonly worker CONTROL copy differs")
        self.copies[target_key] = descriptor
        self.copy_before[target_key] = metadata

    def edge(self, receipt, parent, trail, module):
        row = self._context(receipt, parent, trail, module)
        if row is None:
            return None
        self.begin()
        authority = _worker_authority()
        content, obj, source_metadata = _worker_source(row)
        need(authority == self.authority_before, "Fixed worker authority metadata drifted")
        if row["index"] in self.source_before:
            need(source_metadata == self.source_before[row["index"]],
                 "Repeated worker occurrence source/link drifted")
        else:
            self.source_before[row["index"]] = source_metadata
        self._copy(row, content)
        target_key = key(row["canonical"])
        child_rows = [dict(receipt=_worker_clone(child), field=list(field))
                      for child, field in receipt_edges(obj)]
        if target_key in self.children:
            need(self.children[target_key] == child_rows, "Normal worker JSON children changed")
        else:
            self.children[target_key] = child_rows
        physical = self.copies[target_key]
        observed = dict(index=row["index"], receipt=_worker_clone(receipt), parent=parent,
                        field=list(trail), module=module, physical=_worker_clone(physical))
        self.observations.append(observed)
        self.seen_indices.add(row["index"])
        self.readback()
        return dict(observed, role=_WORKER_ROLE,
                    resolution_basis="EXACT_FINITE_READONLY_WORKER_CONTROL_BYTECOPY",
                    raw_bytes_preserved=True, receipt_children_interpreted=True,
                    child_parent_is_original_logical_worker=True,
                    source_or_scientific_promotion=False)

    def parse(self, receipt, edge):
        # This is the only internal CONTROL parser. No caller supplies a scope,
        # reader, parent alias or arbitrary path; both edge and owned copy bind.
        need(edge.get("role") == _WORKER_ROLE and edge.get("receipt") == receipt
             and edge in [dict(x, role=_WORKER_ROLE,
                              resolution_basis="EXACT_FINITE_READONLY_WORKER_CONTROL_BYTECOPY",
                              raw_bytes_preserved=True, receipt_children_interpreted=True,
                              child_parent_is_original_logical_worker=True,
                              source_or_scientific_promotion=False) for x in self.observations],
             "Only an actually authorized worker occurrence may be parsed")
        row = next(row for row in _WORKER_TABLE if row["logical"] == receipt)
        path = verify(edge["physical"], True)
        need(edge["physical"] == self.copies[key(row["canonical"])],
             "Unknown worker copy parser target")
        content = path.read_bytes()
        need((len(content), hashlib.sha256(content).hexdigest()) == fp(receipt),
             "Owned worker normal JSON bytes changed before child traversal")
        obj = _strict_vendor_json(content)
        need([dict(receipt=_worker_clone(child), field=list(field))
              for child, field in receipt_edges(obj)] == self.children[key(row["canonical"])],
             "Worker parser must retain every normal receipt child")
        self.readback()
        return obj

    def readback(self):
        need(self.observations and self.authority_before is not None,
             "No actual worker observation to verify")
        need(_worker_authority() == self.authority_before,
             "Worker BaseC/two-parent authority bytes or metadata drifted")
        for row in _WORKER_TABLE:
            if row["index"] not in self.source_before:
                continue
            content, obj, source_metadata = _worker_source(row)
            need(source_metadata == self.source_before[row["index"]],
                 "Original worker/link metadata changed")
            target_key = key(row["canonical"])
            if target_key not in self.copies:
                continue
            path, metadata = _worker_regular(self.copies[target_key]["path"], True)
            need(metadata == self.copy_before[target_key]
                 and rec(path) == self.copies[target_key]
                 and path.read_bytes() == content
                 and stable_metadata(path) == metadata,
                 "Readonly worker copy changed after observation/output")
            need([dict(receipt=_worker_clone(child), field=list(field))
                  for child, field in receipt_edges(obj)] == self.children[target_key],
                 "Worker child receipt coverage drifted")
        if self.finalized:
            directory = safe_path(self.directory)
            directory_metadata = stable_metadata(directory)
            need(stat.S_ISDIR(directory_metadata["mode"])
                 and not directory.is_symlink()
                 and stat.S_IMODE(directory_metadata["mode"]) == 0o555,
                 "Finite worker copy directory must be a nonsymlink readonly0555 directory")
            need(directory_metadata == self.directory_before
                 and {p.name for p in directory.iterdir()}
                 == {Path(r["path"]).name for r in self.copies.values()},
                 "Worker preservation directory universe or metadata changed")
        return True

    def require_complete(self):
        if not self.enabled:
            need(not self.observations, "Unrelated base received a finite worker observation")
            return False
        need(self.seen_indices == {row["index"] for row in _WORKER_TABLE}
             and len(self.copies) == len(self.target_keys) == 22,
             "All23 actual worker context slots and22 canonical copies required")
        self.readback()
        if not self.finalized:
            self.directory.chmod(0o555)
            fd = os.open(self.directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
            self.directory_before = stable_metadata(self.directory)
            self.finalized = True
        self.readback()
        return True

    def alias_index(self):
        need(self.require_complete(), "Actual complete fixed worker scope required")
        return dict(schema="exact-resource-aliases.v2",
                    status="EXACT_FIXED23_WORKER_CONTROL_ALIASES_CPU_VERIFIED",
                    aliases=[dict(original=_worker_clone(row["logical"]),
                                  archived=self.copies[key(row["canonical"])],
                                  status="READONLY_BYTE_IDENTICAL_ALIAS", role=_WORKER_ROLE)
                             for row in _WORKER_TABLE],
                    historical_unresolved=[], canonical_target_n=22,
                    separate_original_symlink_physical_package_entry_forbidden=True,
                    normal_JSON_receipt_children_retained=True,
                    scientific_or_source_acceptance=False)

    def proof(self):
        need(self.require_complete(), "Actual complete fixed worker scope required")
        scope = [dict(index=row["index"], original=_worker_clone(row["logical"]),
                      parent_manifest=_worker_clone(row["parent"]), source_field=list(row["field"]),
                      module=_WORKER_MODULE,
                      canonical_path_as_scalar=row["canonical"]["path"],
                      canonical_bytes_as_scalar=row["canonical"]["bytes"],
                      canonical_sha256_as_scalar=row["canonical"]["sha256"],
                      exact_link_path_as_scalar=row["link_path"],
                      exact_link_text_as_scalar=row["link_text"])
                 for row in _WORKER_TABLE]
        targets = []
        for target_key in self.target_keys:
            row = next(row for row in _WORKER_TABLE if key(row["canonical"]) == target_key)
            targets.append(dict(canonical_path_as_scalar=row["canonical"]["path"],
                                bytes_as_scalar=row["canonical"]["bytes"],
                                sha256_as_scalar=row["canonical"]["sha256"],
                                preserved=self.copies[target_key],
                                preserved_metadata=self.copy_before[target_key],
                                child_receipts=self.children[target_key]))
        return dict(schema="exact-finite-worker-control-alias-preservation.v1",
                    status="EXACT_BASE23_CONTEXTS_22_NORMAL_JSON_CONTROL_COPIES_CPU_VERIFIED",
                    accepted_base=_worker_clone(_WORKER_BASE),
                    accepted_base_closure=_worker_clone(_WORKER_CLOSURE),
                    raw_parent_manifests=_worker_clone(_WORKER_PARENTS),
                    fixed_scope=scope, fixed_context_n=23, canonical_target_n=22,
                    unique_expected_fingerprint_n=len({fp(row["canonical"]) for row in _WORKER_TABLE}),
                    observed_context_slots=sorted(self.seen_indices),
                    authorized_observation_n=len(self.observations),
                    observations=_worker_clone(self.observations),
                    output_root_as_scalar=str(self.out),
                    authority_metadata_before=_worker_clone(self.authority_before),
                    authority_metadata_after=_worker_clone(self.authority_before),
                    source_metadata_before=[dict(index=k, metadata=self.source_before[k])
                                            for k in sorted(self.source_before)],
                    source_metadata_after=[dict(index=k, metadata=self.source_before[k])
                                           for k in sorted(self.source_before)],
                    canonical_targets=targets, copy_directory_metadata=self.directory_before,
                    original_worker_modes_unchanged_0664=True,
                    all_inputs_copies_readlinks_pre_end_afteroutput_bound=True,
                    every_occurrence_authorized_before_seen=True,
                    normal_JSON_receipt_children_retained=True,
                    child_parent_is_original_logical_worker=True,
                    generic_reader_or_17_parent_permission_changed=False,
                    source_or_scientific_promotion=False)


def _worker_saved_metadata(value):
    fields = {"path", "bytes", "inode", "mtime_ns", "ctime_ns", "mode",
              "dev", "nlink", "uid", "gid"}
    need(type(value) is dict and set(value) == fields and type(value["path"]) is str
         and all(type(value[k]) is int and value[k] >= 0 for k in fields - {"path"}),
         "Saved worker stable metadata requires exact integer fields")
    return value


def verify_finite_worker_preservation(proof, aliases, allocation):
    need(isinstance(proof, dict) and proof.get("allocation") == allocation,
         "Actual finite worker saved allocation differs")
    need(type(allocation) is dict and type(allocation.get("job_id")) is str
         and allocation["job_id"].isdigit()
         and type(allocation.get("allocated_CPUs")) is int
         and allocation["allocated_CPUs"] >= 1
         and type(allocation.get("allocated_gpus")) is int
         and allocation["allocated_gpus"] == 0,
         "Actual finite worker producer requires a numeric CPU allocation/GPU0")
    out = safe_path(proof.get("output_root_as_scalar", ""))
    index_receipt = receipt_shape(proof.get("exact_alias_index"))
    need(index_receipt["path"] == str(out / "finite_worker_control_aliases.json"),
         "Fixed worker alias index must be its actual owned output")
    index_bytes, index_metadata = _worker_exact_bytes(index_receipt, True)
    need(exact_json(_strict_vendor_json(index_bytes), aliases),
         "Saved worker alias index payload differs from its actual bytes")
    scope = FiniteWorkerControlAliases(out, _WORKER_BASE, _WORKER_CLOSURE)
    need(type(proof.get("authorized_observation_n")) is int
         and type(proof.get("fixed_context_n")) is int
         and type(proof.get("canonical_target_n")) is int,
         "Finite worker saved counts require exact integers")
    need(proof.get("fixed_context_n") == 23 and proof.get("canonical_target_n") == 22,
         "Finite worker complete saved denominator differs")
    scope.authority_before = _worker_authority()
    sources = proof.get("source_metadata_before")
    need(isinstance(sources, list) and len(sources) == 23
         and [x.get("index") for x in sources] == sorted(row["index"] for row in _WORKER_TABLE),
         "All23 saved worker source/link metadata rows required")
    for source in sources:
        need(type(source["index"]) is int and type(source["metadata"]) is dict
             and set(source["metadata"]) == {"logical", "canonical", "link", "link_text"}
             and type(source["metadata"]["link_text"]) is str,
             "Saved worker source/link row types differ")
        for name in ("logical", "canonical", "link"):
            _worker_saved_metadata(source["metadata"][name])
    scope.source_before = {x["index"]: x["metadata"] for x in sources}
    targets = proof.get("canonical_targets")
    need(isinstance(targets, list) and len(targets) == 22, "All22 saved canonical targets required")
    for target_key, target in zip(scope.target_keys, targets):
        row = next(row for row in _WORKER_TABLE if key(row["canonical"]) == target_key)
        receipt = receipt_shape(target["preserved"])
        need(receipt["path"] == str(scope.directory / scope._copy_name(row))
             and fp(receipt) == fp(row["canonical"]),
             "Saved worker copy target/full mapping differs")
        scope.copies[target_key] = receipt
        scope.copy_before[target_key] = _worker_saved_metadata(target["preserved_metadata"])
        scope.children[target_key] = target["child_receipts"]
    observations = proof.get("observations")
    need(isinstance(observations, list) and len(observations) == proof["authorized_observation_n"],
         "Saved worker observation count differs")
    for observed in observations:
        need(isinstance(observed, dict) and set(observed) == {"index", "receipt", "parent", "field", "module", "physical"},
             "Saved finite worker observation shape differs")
        need(type(observed["index"]) is int and type(observed["field"]) is list
             and all(type(token) is str for token in observed["field"]),
             "Saved worker observed index/field exact types required")
        row = scope._context(observed["receipt"], observed["parent"],
                             tuple(observed["field"]), observed["module"])
        need(row is not None and row["index"] == observed["index"]
             and observed["physical"] == scope.copies[key(row["canonical"])],
             "Saved worker context/full copy mapping differs")
        scope.seen_indices.add(row["index"])
    scope.observations = _worker_clone(observations)
    scope.finalized = True
    scope.directory_before = _worker_saved_metadata(proof.get("copy_directory_metadata"))
    scope.readback()
    expected_aliases = scope.alias_index()
    expected_proof = dict(scope.proof(), allocation=allocation,
                          exact_alias_index=proof.get("exact_alias_index"))
    need(exact_json(aliases, expected_aliases) and exact_json(proof, expected_proof),
         "Complete saved finite worker proof or alias index forked")
    final_index_bytes, final_index_metadata = _worker_exact_bytes(index_receipt, True)
    need(final_index_bytes == index_bytes and final_index_metadata == index_metadata,
         "Saved worker alias index changed during full content verification")
    return True



# Exact catalog annotations retain accepted unresolved provenance, never old bytes.
_CATALOG_MSA_CATALOG = dict(path="/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/native74_cache_catalog_13265/catalog.json", bytes=1154029, sha256="4eb474dc45c1a0ac20e152703b1fc50418096732da5083690c6a78262241e19e")
_CATALOG_MSA_ACCEPTANCE = dict(path="/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/native74_cache_catalog_13265/acceptance.json", bytes=4061, sha256="ed9973988c8a20c2182c71b821bacc4b781fccfcb7f2fe5766bd04c663dca7d0")
_CATALOG_MSA_BASE_C = dict(path="/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/source_refresh_relative_v10_13316/source_receipt_closure.json", bytes=14961330, sha256="7e32c2b8196a873874d12747caf4b1b4b829808537e8770c83b3124595f138ff")
_CATALOG_MSA_EDGE_SEAL = dict(path="/lustre/users/u21111210118/projects/test9/steps/24_benchmark_delivery/runs/native74_edge_seal_13214/acceptance.json", bytes=772271, sha256="aa350763e14103e2cde432652b83fd6c5e95fd11569d663364e9c4ecb82bd45c")
_CATALOG_MSA_DEFINITIONS = [
  {
    "original": {
      "path": "/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_common_review.py",
      "sha256": "e52a1598f3736e4c83512811e7a84037206a9cb1c13066981492345554b42d08",
      "bytes": 46094
    },
    "subtype": "HISTORICAL_UNRESOLVED_MSA_DERIVATION",
    "role": "OLD_MSA_DOWNLOAD_GENERATOR_LINEAGE",
    "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/msa_12975/msa.json",
    "trail": [
      "source"
    ],
    "shortest_receipt_chain": [
      {
        "parent_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/native_controls_frozen_13051/inference_plan.json",
        "parent_sha256": "9c90d720d39f306e9c601a8281afaca0d29ac986872805dd6b913eb8f2e9373b",
        "field": [
          "msa"
        ]
      },
      {
        "parent_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/msa_content_12983/msa.json",
        "parent_sha256": "edfd913d745b84e8412bcb13a46dd2862f63fc9757d8e9c69c7e7ff153b9e61f",
        "field": [
          "original_download_results"
        ]
      },
      {
        "parent_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/msa_12975/msa.json",
        "parent_sha256": "7084743586acf57dceef5260060949962b25ebb11d2e311650b9586208734d00",
        "field": [
          "source"
        ]
      }
    ]
  },
  {
    "original": {
      "path": "/lustre/users/u21111210118/projects/test9/source/rebuild/benchmark_common_review.py",
      "sha256": "74915aaf1ae3f21b5c2d7169ff53f1fd5d776772e0c89ea778f4572db831df9e",
      "bytes": 46425
    },
    "subtype": "HISTORICAL_UNRESOLVED_MSA_DERIVATION",
    "role": "OLD_MSA_CONTENT_VALIDATOR_GENERATOR_LINEAGE",
    "parent": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/msa_content_12983/msa.json",
    "trail": [
      "source"
    ],
    "shortest_receipt_chain": [
      {
        "parent_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/native_controls_frozen_13051/inference_plan.json",
        "parent_sha256": "9c90d720d39f306e9c601a8281afaca0d29ac986872805dd6b913eb8f2e9373b",
        "field": [
          "msa"
        ]
      },
      {
        "parent_path": "/lustre/users/u21111210118/projects/test9/steps/23_common_review/runs/msa_content_12983/msa.json",
        "parent_sha256": "edfd913d745b84e8412bcb13a46dd2862f63fc9757d8e9c69c7e7ff153b9e61f",
        "field": [
          "source"
        ]
      }
    ]
  }
]
_CATALOG_MSA_FIELD = "historical_MSA_derivation_gaps_preserved"
_CATALOG_MSA_MODULES = ("native74_cache_catalog", "final_delivery_tools")
_CATALOG_MSA_ROLE = "CATALOG_DECLARATION_OF_INHERITED_NONOPERATIVE_MSA_GAP_NOT_CURRENT_BYTE_ACCEPTANCE"
_CATALOG_MSA_ROOT_DECISION = "Exact root authorization received2026-10-11; retain unresolved source only as historical MSA derivation. Operative current science uses accepted frozen native876d source and exact actual A3M/query/features."
_CATALOG_MSA_KEYS = {"schema","status","native_acceptance","independent_edge_seal","old_plan","old_source","new_source","new_source_bundle","source_compatibility","rows","workers","raw_models","source_roots","split_recovery_index18_retained","historical_MSA_derivation_gaps_preserved","historical_missing_exemption_for_current_inputs","old_runtime_locks","old_af2_parameter_receipts","no_new_predictions","no_scores_transferred","new_inference_GPU_seconds","old_GPU_cost_not_recharged","future_formal_binding"}

def _catalog_msa_controls():
    return [_CATALOG_MSA_CATALOG, _CATALOG_MSA_ACCEPTANCE, _CATALOG_MSA_BASE_C]

def _catalog_msa_old_fingerprint(r):
    return isinstance(r,dict) and any(r.get("bytes")==d["original"]["bytes"] and r.get("sha256")==d["original"]["sha256"] for d in _CATALOG_MSA_DEFINITIONS)

def reject_catalog_msa_gap_declaration(r):
    need(not _catalog_msa_old_fingerprint(r),
         "Catalog MSA historical declaration cannot authorize operative Source, seed, gate, alias, add or resolve")

def _catalog_msa_json(text):
    def pairs(items):
        result={}
        for k,v in items:
            need(k not in result,"Duplicate catalog MSA JSON key")
            result[k]=v
        return result
    def invalid(value):
        raise ValueError("Nonfinite catalog MSA JSON forbidden")
    def number(value):
        result=float(value)
        need(result==result and abs(result)!=float("inf"),"Nonfinite catalog MSA JSON forbidden")
        return result
    return json.loads(text,object_pairs_hook=pairs,parse_constant=invalid,parse_float=number)

def _catalog_msa_definition_shape(catalog,catalog_A,accepted_BaseC):
    need(type(catalog)is dict and set(catalog)==_CATALOG_MSA_KEYS
         and catalog.get("schema")=="native74_cache_catalog.v1"
         and catalog.get("status")=="NATIVE74_RAW_CACHE_CATALOG_VERIFIED_FUTURE_FORMAL_BINDING_PENDING",
         "Exact catalog MSA schema/status/23-key declaration required")
    need(type(catalog_A)is dict and catalog_A.get("status")=="CPU_CACHE_GUARD_CATALOG_COMPLETE"
         and exact_json(catalog_A.get("result"),_CATALOG_MSA_CATALOG)
         and catalog_A.get("no_inference")is True and catalog_A.get("no_GPU_submission")is True
         and catalog_A.get("formal_binding")is False,"Accepted catalog A/result binding changed")
    need(exact_json(catalog.get(_CATALOG_MSA_FIELD),_CATALOG_MSA_DEFINITIONS)
         and catalog.get("historical_missing_exemption_for_current_inputs")is False
         and exact_json(catalog.get("independent_edge_seal"),_CATALOG_MSA_EDGE_SEAL)
         and type(catalog.get("workers"))is int and catalog["workers"]==20
         and type(catalog.get("raw_models"))is int and catalog["raw_models"]==74
         and catalog.get("split_recovery_index18_retained")is True
         and catalog.get("no_new_predictions")is True and catalog.get("no_scores_transferred")is True
         and type(catalog.get("new_inference_GPU_seconds"))is int and catalog["new_inference_GPU_seconds"]==0
         and catalog.get("old_GPU_cost_not_recharged")is True and catalog.get("future_formal_binding")is False,
         "Exact ordered two catalog MSA declarations/current-exemption policy changed")
    need(type(accepted_BaseC)is dict and type(accepted_BaseC.get("historical_gaps"))is list
         and len(accepted_BaseC["historical_gaps"])==3
         and accepted_BaseC.get("source_missing_allowed_only_exact_historical_edges")is True,
         "Original three accepted typed historical gaps required")
    for slot,definition in enumerate(_CATALOG_MSA_DEFINITIONS):
        historical=accepted_BaseC["historical_gaps"][slot+1]
        need(type(historical)is dict,"Typed accepted MSA historical definition required")
        projected=dict(original=historical.get("receipt"),subtype=historical.get("subtype"),
                       role=historical.get("role"),parent=historical.get("parent"),
                       trail=historical.get("field"),shortest_receipt_chain=historical.get("shortest_receipt_chain"))
        need(exact_json(projected,definition)
             and historical.get("root_decision")==_CATALOG_MSA_ROOT_DECISION
             and historical.get("parent_sha256")==definition["shortest_receipt_chain"][-1]["parent_sha256"]
             and exact_json(historical.get("actual_operative_scientific_source"),catalog.get("old_source")),
             "Full accepted catalog MSA history/root decision/operative-source binding changed")
        edges=[e for e in accepted_BaseC.get("edges",[]) if exact_json(e.get("receipt"),definition["original"])
               and e.get("parent")==definition["parent"] and e.get("field")==definition["trail"]]
        need(len(edges)==1 and edges[0].get("role")=="TYPED_NONOPERATIVE_HISTORICAL_GAP",
             "Unique original exact typed MSA edge required")
    return True

def _catalog_msa_native_shape(records):
    need(type(records)is list and len(records)==3,"Closed original catalog/A/BaseC native table required")
    for value,receipt in zip(records,_catalog_msa_controls()):
        need(type(value)is dict and set(value)==_HISTORY_META_KEYS
             and value.get("path")==receipt["path"] and value.get("bytes")==receipt["bytes"]
             and all(type(value[k])is int and value[k]>=0 for k in _HISTORY_META_KEYS-{"path"})
             and stat.S_ISREG(value["mode"]) and stat.S_IMODE(value["mode"])==0o444 and value["nlink"]==1,
             "Exact catalog/A/BaseC readonly single-link native record required")
    return records

def _catalog_msa_projection(slot,original_metadata):
    _catalog_msa_native_shape(original_metadata)
    return dict(schema="exact-catalog-msa-gap-declaration-projection.v1",slot=slot,
                catalog=_CATALOG_MSA_CATALOG,catalog_acceptance=_CATALOG_MSA_ACCEPTANCE,
                accepted_base_closure=_CATALOG_MSA_BASE_C,inherited_historical_gap_index=slot+1,
                declaration=json.loads(json.dumps(_CATALOG_MSA_DEFINITIONS[slot])),
                original_metadata_before=[dict(x)for x in original_metadata],original_metadata_after=[dict(x)for x in original_metadata],
                old_source_bytes_verified=False,old_source_restored=False,
                current_input_exemption=False,physical_alias_authorized=False,
                new_Source_identity_created=False)

def catalog_msa_gap_projection_native(actual_C):
    """Pure extraction of ORIGINAL producer records; no current metadata/FS."""
    need(type(actual_C)is dict and type(actual_C.get("edges"))is list,"Actual Source C object required")
    edges=[e for e in actual_C["edges"] if e.get("role")==_CATALOG_MSA_ROLE]
    if not edges:return []
    first=edges[0].get("catalog_msa_gap_projection",{})
    records=first.get("original_metadata_before")
    _catalog_msa_native_shape(records)
    for e in edges:
        projection=e.get("catalog_msa_gap_projection",{})
        slot=projection.get("slot")
        need(type(slot)is int and 0<=slot<2
             and exact_json(projection,_catalog_msa_projection(slot,records)),
             "Closed catalog MSA projection/original native binding changed")
    return records

def catalog_msa_gap_projection_shape(catalog,catalog_A,accepted_BaseC,actual_C):
    """INDEX-object-only semantic replay. Caller authenticates whole input bytes."""
    _catalog_msa_definition_shape(catalog,catalog_A,accepted_BaseC)
    records=catalog_msa_gap_projection_native(actual_C)
    need(bool(records),"Actual catalog MSA annotation observations required")
    need(exact_json(actual_C.get("base_closure"),_CATALOG_MSA_BASE_C),
         "Actual C accepted BaseC pointer changed")
    observations=[(i,e) for i,e in enumerate(actual_C["edges"]) if e.get("role")==_CATALOG_MSA_ROLE]
    for e in actual_C["edges"]:
        if _catalog_msa_old_fingerprint(e.get("receipt")) and e.get("role")!=_CATALOG_MSA_ROLE:
            original=[d for d in _CATALOG_MSA_DEFINITIONS if exact_json(e.get("receipt"),d["original"])
                      and e.get("parent")==d["parent"] and e.get("field")==d["trail"]]
            need(len(original)==1 and e.get("role")in {"TYPED_NONOPERATIVE_HISTORICAL_GAP","INHERITED_EXACT_NONOPERATIVE_HISTORICAL_EDGE_NOT_CURRENT_BYTE_ACCEPTANCE"},
                 "Old MSA fingerprint cannot be an operative or unrelated actual C edge")
    expected=[]
    for i,e in enumerate(actual_C["edges"]):
        if exact_json(e.get("receipt"),_CATALOG_MSA_CATALOG) and e.get("role")=="EXACT_NEW_TEXT_RECEIPT_READBACK":
            need(e.get("module")in _CATALOG_MSA_MODULES and type(e.get("physical"))is dict
                 and fp(e["physical"])==fp(_CATALOG_MSA_CATALOG),
                 "Catalog actual ordinary readback/module/full-fingerprint required")
            expected.extend([(i,e["module"],slot)for slot in (1,0)])
    need(len(expected)==len(observations) and bool(expected),"Exactly both declarations per actual catalog parse required")
    for (parsed,module,slot),(index,e) in zip(expected,observations):
        need(index>parsed and type(e)is dict
             and set(e)=={"receipt","parent","field","module","role","catalog_msa_gap_projection"}
             and exact_json(e["receipt"],_CATALOG_MSA_DEFINITIONS[slot]["original"])
             and e["parent"]==_CATALOG_MSA_CATALOG["path"]
             and e["field"]==[_CATALOG_MSA_FIELD,str(slot),"original"] and e["module"]==module
             and exact_json(e["catalog_msa_gap_projection"],_catalog_msa_projection(slot,records)),
             "Catalog MSA annotation is not the exact ordered coupled declaration context")
    return True

class CatalogMSAGapContexts:
    """Two documentary projections. No target-path payload/stat/alias/Source IO."""
    def __init__(self,base_closure_receipt):
        self.bound=exact_json(base_closure_receipt,_CATALOG_MSA_BASE_C)
        self.active=False;self.original_metadata=[];self.base=None;self.catalog=None;self.acceptance=None
        self.parses=[];self.observations=[];self.pending=[]
        if self.bound:
            # All three baselines precede the first inherited BaseC/gate/catalog read.
            self.original_metadata=[stable_metadata(safe_path(r["path"]))for r in _catalog_msa_controls()]
            _catalog_msa_native_shape(self.original_metadata)
    def bind_base(self,obj):
        self.base=obj
    def fence(self):
        if not self.bound:return True
        _catalog_msa_native_shape(self.original_metadata)
        for receipt,metadata in zip(_catalog_msa_controls(),self.original_metadata):
            path=safe_path(receipt["path"])
            need(exact_json(stable_metadata(path),metadata) and rec(path)==receipt
                 and exact_json(stable_metadata(path),metadata),"Catalog MSA fixed input own bytes/native changed")
        _fixed_history_native_union_sweep(self.original_metadata)
        return True
    def native_fence(self):
        if self.bound:_fixed_history_native_union_sweep(self.original_metadata)
        return True
    def catalog_candidate(self,r):
        return isinstance(r,dict) and (r.get("path")==_CATALOG_MSA_CATALOG["path"]
                                       or fp(r)==fp(_CATALOG_MSA_CATALOG))
    def incoming(self,r,module):
        if self.catalog_candidate(r):
            need(self.bound and exact_json(r,_CATALOG_MSA_CATALOG) and module in _CATALOG_MSA_MODULES,
                 "Exact accepted catalog identity/two-module context required")
        return True
    def opened(self,r,physical,obj,module):
        if not self.catalog_candidate(r):return obj
        self.incoming(r,module);self.fence()
        catalog=_catalog_msa_json(Path(physical).read_text(encoding="utf-8"))
        need(exact_json(catalog,obj),"Catalog ordinary reader object differs from exact own JSON")
        acceptance=_catalog_msa_json(verify(_CATALOG_MSA_ACCEPTANCE,True).read_text(encoding="utf-8"))
        _catalog_msa_definition_shape(catalog,acceptance,self.base)
        self.fence()
        self.catalog=catalog;self.acceptance=acceptance;self.active=True
        self.parses.append(module);self.pending.extend([(module,1),(module,0)])
        return obj
    def edge(self,r,parent,trail,module,history):
        # Original exact accepted historical contexts keep their unchanged branch.
        if (key(r),parent,trail)in history:return None
        candidate=parent==_CATALOG_MSA_CATALOG["path"] and tuple(trail[:1])==(_CATALOG_MSA_FIELD,)
        if candidate:
            need(self.active and module in _CATALOG_MSA_MODULES and bool(self.pending),
                 "Authenticated exact catalog parse required for MSA declaration")
            expected_module,slot=self.pending[0]
            need(module==expected_module and trail==(_CATALOG_MSA_FIELD,str(slot),"original")
                 and exact_json(r,_CATALOG_MSA_DEFINITIONS[slot]["original"]),
                 "Exact ordered catalog MSA parent/slot/receipt/module context required")
            self.fence();self.pending.pop(0)
            e=dict(receipt=r,parent=parent,field=list(trail),module=module,role=_CATALOG_MSA_ROLE,
                   catalog_msa_gap_projection=_catalog_msa_projection(slot,self.original_metadata))
            self.observations.append(e)
            return e
        reject_catalog_msa_gap_declaration(r)
        return None
    def require_complete(self):
        if self.bound:
            need(self.active and len(self.observations)==2*len(self.parses) and not self.pending,
                 "Both exact catalog MSA declarations must complete every actual parse")
            self.fence()
        return self.active
    def validate_graph(self,actual_C):
        if self.active:
            catalog_msa_gap_projection_shape(self.catalog,self.acceptance,self.base,actual_C)
            self.fence()
        return True

def catalog_msa_gap_saved_inputs(actual_C):
    """Current adapter check from saved producer baselines, never adopts new MD."""
    records=catalog_msa_gap_projection_native(actual_C)
    if not records:return None
    _fixed_history_native_union_sweep(records)
    objects=[]
    for receipt,metadata in zip(_catalog_msa_controls(),records):
        path=safe_path(receipt["path"])
        need(stable_metadata(path)==metadata and rec(path)==receipt,"Catalog MSA saved input own bytes/native changed")
        objects.append(_catalog_msa_json(path.read_text(encoding="utf-8")))
    catalog_msa_gap_projection_shape(objects[0],objects[1],objects[2],actual_C)
    catalog_msa_gap_saved_fence(records)
    return objects

def catalog_msa_gap_saved_fence(records):
    if not records:return True
    _catalog_msa_native_shape(records)
    for receipt,metadata in zip(_catalog_msa_controls(),records):
        path=safe_path(receipt["path"])
        need(stable_metadata(path)==metadata and rec(path)==receipt and stable_metadata(path)==metadata,
             "Catalog MSA saved input own bytes/native changed")
    _fixed_history_native_union_sweep(records)
    return True


def catalog_msa_gap_graph_readback(controls):
    """Closed A/C/I[/CA] current own-control check, never a child reader."""
    need(type(controls)is dict and set(controls)in ({"acceptance","source_closure","source_inclusion"},
                                                   {"acceptance","source_closure","source_inclusion","context_adapter_acceptance"}),
         "Closed catalog MSA Source A/C/I/CA graph controls required")
    objects={};catalog_inputs=None
    for name,(receipt,metadata)in controls.items():
        need(type(metadata)is dict and set(metadata)==_HISTORY_META_KEYS
             and metadata.get("path")==receipt["path"] and metadata.get("bytes")==receipt["bytes"]
             and stat.S_ISREG(metadata["mode"]) and stat.S_IMODE(metadata["mode"])==0o444 and metadata["nlink"]==1,
             "Original catalog MSA graph readonly single-link native table required")
        path=safe_path(receipt["path"])
        need(rec(path)==receipt and stable_metadata(path)==metadata,"Catalog MSA graph changed before JSON")
        objects[name]=_catalog_msa_json(path.read_text(encoding="utf-8"))
        need(rec(path)==receipt and stable_metadata(path)==metadata,"Catalog MSA graph changed during JSON")
    C=controls["source_closure"][0];I=controls["source_inclusion"][0];A=controls["acceptance"][0]
    need(objects["acceptance"].get("schema")=="final-source-closure-acceptance.v3"
         and objects["acceptance"].get("status")=="FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED"
         and objects["acceptance"].get("source_closure")==C and objects["acceptance"].get("source_inclusion")==I
         and objects["source_inclusion"].get("source_receipt_closure")==C,
         "Catalog MSA actual A/I/C object pointer fork")
    if "context_adapter_acceptance"in objects:
        CA=objects["context_adapter_acceptance"]
        need(CA.get("schema")=="final-source-materialized-context-read-view-acceptance.v3"
             and CA.get("status")=="FINAL_CURRENT_SOURCE_MATERIALIZED_FIVE_PARENT_CONTEXT_AND_DERIVED_V2_CPU_ACCEPTED_NOT_STAGED_NOT_PUBLISHED"
             and CA.get("actual_new_library_acceptance")==A and CA.get("source_closure")==C and CA.get("source_inclusion")==I,
             "Catalog MSA actual CA/A/I/C object pointer fork")
    catalog_inputs=catalog_msa_gap_saved_inputs(objects["source_closure"])
    need(catalog_inputs is not None,"Actual catalog MSA C projection required")
    records=catalog_msa_gap_projection_native(objects["source_closure"])
    for receipt,metadata in controls.values():
        need(rec(receipt["path"])==receipt and stable_metadata(receipt["path"])==metadata,
             "Catalog MSA graph changed after all final JSON")
    # TRUE last native-only sweep includes controls read before later graph hashes.
    _fixed_history_native_union_sweep(records+[metadata for receipt,metadata in controls.values()])
    return records

def module_plan(plan):
 need(plan.get("schema")=="final-source-closure-plan.v3","Wrong explicit closure plan schema")
 for name in ("base_acceptance","library_software_acceptance","mapper_software_acceptance"):
  if name in plan:reject_parent_diagnostic_history_declaration(plan[name]);reject_relative_diagnostic_history_declaration(plan[name]);reject_archive_parent_history_declaration(plan[name]);reject_catalog_msa_gap_declaration(plan[name]);reject_inventory_history_declaration(plan[name])
 need(plan.get("root_owned")is True and plan.get("formal_array_job_id")=="13260","Root plan must bind actual13260")
 for context_seed in plan.get("context_parent_seeds",[]):reject_parent_diagnostic_history_declaration(context_seed);reject_relative_diagnostic_history_declaration(context_seed);reject_archive_parent_history_declaration(context_seed);reject_catalog_msa_gap_declaration(context_seed);reject_inventory_history_declaration(context_seed);reject_vendor_example_declaration(context_seed);reject_worker_declaration(context_seed)
 for entry in plan.get("aliases",[]):
  reject_parent_diagnostic_history_declaration(entry["logical"]);reject_relative_diagnostic_history_declaration(entry["logical"]);reject_archive_parent_history_declaration(entry["logical"]);reject_catalog_msa_gap_declaration(entry["logical"]);reject_inventory_history_declaration(entry["logical"]);reject_parent_diagnostic_history_declaration(entry["physical"]);reject_relative_diagnostic_history_declaration(entry["physical"]);reject_archive_parent_history_declaration(entry["physical"]);reject_catalog_msa_gap_declaration(entry["physical"]);reject_inventory_history_declaration(entry["physical"])
  reject_vendor_example_declaration(entry["logical"]);reject_vendor_example_declaration(entry["physical"]);reject_worker_declaration(entry["logical"]);reject_worker_declaration(entry["physical"])
 modules=plan.get("modules");need(isinstance(modules,list),"Explicit accepted modules required")
 roles=[m.get("role")for m in modules]
 need(len(roles)==len(set(roles))and set(roles)==REQUIRED_MODULES,"All nine exact final module roles required")
 need(plan.get("public_source_only")is True and plan.get("no_scientific_settings_change")is True,"Source-only scope required")
 need(plan.get("root_integration_review",{}).get("new_generic_source_promotion_reviewed")is True,
      "Root must explicitly review integration of corrected generic source; isolated version alone is not product integration")
 for m in modules:
  need(isinstance(m.get("gate"),dict)and isinstance(m["gate"].get("expected_status"),str)and m["gate"]["expected_status"],"Explicit module terminal status required")
  receipt_shape(m["gate"]["receipt"])
  for gate_name in ("allocation_closure_gate","root_terminal_rejection_gate"):
   if gate_name in m:reject_parent_diagnostic_history_declaration(m[gate_name]["receipt"]);reject_relative_diagnostic_history_declaration(m[gate_name]["receipt"]);reject_archive_parent_history_declaration(m[gate_name]["receipt"]);reject_catalog_msa_gap_declaration(m[gate_name]["receipt"]);reject_inventory_history_declaration(m[gate_name]["receipt"])
  if m["role"]in MODULE_GATE_STATUS:
   need(m["gate"]["expected_status"]in MODULE_GATE_STATUS[m["role"]],"Unexpected current module terminal status")
  need(isinstance(m.get("sources"),list)and len(m["sources"])>0,"Every operative module needs exact source entries, including reused source")
  need(isinstance(m.get("seeds",[]),list),"Explicit source snapshot/receipt seeds required")
  reject_parent_diagnostic_history_declaration(m["gate"]["receipt"]);reject_relative_diagnostic_history_declaration(m["gate"]["receipt"]);reject_archive_parent_history_declaration(m["gate"]["receipt"]);reject_catalog_msa_gap_declaration(m["gate"]["receipt"]);reject_inventory_history_declaration(m["gate"]["receipt"]);reject_vendor_example_declaration(m["gate"]["receipt"]);reject_worker_declaration(m["gate"]["receipt"])
  for seed in m.get("seeds",[]):reject_parent_diagnostic_history_declaration(seed);reject_relative_diagnostic_history_declaration(seed);reject_archive_parent_history_declaration(seed);reject_catalog_msa_gap_declaration(seed);reject_inventory_history_declaration(seed);reject_vendor_example_declaration(seed);reject_worker_declaration(seed)
  for s in m["sources"]:
   reject_parent_diagnostic_history_declaration(s["receipt"]);reject_relative_diagnostic_history_declaration(s["receipt"]);reject_archive_parent_history_declaration(s["receipt"]);reject_catalog_msa_gap_declaration(s["receipt"]);reject_inventory_history_declaration(s["receipt"]);reject_vendor_example_declaration(s["receipt"]);reject_worker_declaration(s["receipt"]);eligible_public(s["receipt"],s["repository_relative"])
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
 need(contracts.get("status")=="PASS"and type(contracts.get("tests"))is int and contracts["tests"]==SOURCE_CONTRACTS and type(contracts.get("failures"))is int and contracts["failures"]==0 and type(contracts.get("errors"))is int and contracts["errors"]==0 and contracts.get("tested_source_files")==sources and contracts.get("owned_python_compile_PASS")is True and contracts.get("bash_syntax_PASS")is True,"Actual saved356/count/source/syntax library contracts required")
 original=obj.get("original_executing_sources");need(isinstance(original,list)and len(original)==6 and {Path(r["path"]).name for r in original}==set(PACKAGE_NAMES),"Whole original executed source6 required")
 need({Path(r["path"]).name:fp(receipt_shape(r))for r in original}=={Path(r["path"]).name:fp(receipt_shape(r))for r in sources},"Original and tested frozen software source identities differ")
 need(obj.get("source_entry")==next(r for r in original if Path(r["path"]).name=="final_source_closure.py"),"Software executing entry differs from original source6")
 receipt_shape(obj["source_snapshot"]);core_runtime_shape(obj["conditional_core_runtime"])
 need(obj.get("whole6_source_prepost_PASS")is True and obj.get("original_and_frozen_owned_bytes_identical")is True and obj.get("conditional_runtime_prepost_PASS")is True,"Actual whole6/runtime before-end software qualification required")
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
 need(suite.countTestCases()==SOURCE_CONTRACTS,"Expected356 source-boundary contracts: retained321 plus35 catalog MSA declaration context boundaries")
 with(out/"contracts.txt").open("x")as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
 (out/"contracts.txt").chmod(0o444)
 rr=dump(out/"contracts.json",dict(status="PASS"if result.wasSuccessful()else"FAIL",tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),log=rec(out/"contracts.txt"),tested_source_files=[rec(out/"runner"/n)for n in PACKAGE_NAMES],owned_python_compile_PASS=True,bash_syntax_PASS=True))
 need(result.wasSuccessful(),"Source closure software contracts failed")
 return rr
def software(out):
 allocation=cpu();runtime=conditional_core_runtime();out=safe_path(out);out.mkdir(parents=True,exist_ok=False);stage="owned_source_freeze"
 try:
  original,original_before=owned_source_bundle(Path(__file__).resolve().parent);source_entry=rec(Path(__file__).resolve())
  runners=freeze_runner(out);frozen_before=[stable_metadata(r["path"])for r in runners]
  owned_source_readback(original,runners,original_before,frozen_before)
  need(source_entry==next(r for r in original if Path(r["path"]).name=="final_source_closure.py"),"Actual original software entry is not in source6")
  for r in runners:
   if Path(r["path"]).suffix==".py":compile(Path(r["path"]).read_bytes(),r["path"],"exec",dont_inherit=True)
  need(subprocess.run(["bash","-n",str(out/"runner/final_source_cpu.sbatch")],capture_output=True,text=True).returncode==0,"Exact library launcher syntax failed")
  stage="software356";cr=contracts(out);co=read(verify(cr,True))
  owned_source_readback(original,runners,original_before,frozen_before);need(conditional_core_runtime()==runtime,"Conditional CORE runtime changed during software")
  snapshot=dump(out/"source_snapshot.json",dict(schema="final-source-owned-six-byte-snapshot.v1",source_entry=source_entry,original_executing_sources=original,source_files=runners,
   original_metadata_before=original_before,original_metadata_after=[stable_metadata(r["path"])for r in original],frozen_metadata_before=frozen_before,frozen_metadata_after=[stable_metadata(r["path"])for r in runners],
   conditional_core_runtime=runtime,whole6_source_prepost_PASS=True,original_and_frozen_owned_bytes_identical=True,conditional_runtime_prepost_PASS=True))
  obj=dict(schema="final-source-materialized-software-acceptance.v3",status=SOFTWARE_STATUS,source_files=runners,original_executing_sources=original,source_entry=source_entry,source_snapshot=snapshot,
   conditional_core_runtime=runtime,whole6_source_prepost_PASS=True,original_and_frozen_owned_bytes_identical=True,conditional_runtime_prepost_PASS=True,contracts=cr,allocation=allocation,
   no_model_calls=True,no_GPU_submission=True,science_or_integration_accepted=False,source_staged=False,published=False,ACTIVE_changed=False)
  software_shape(obj,co);software_snapshot_shape(obj,read(verify(snapshot,True)))
  owned_source_readback(original,runners,original_before,frozen_before);need(conditional_core_runtime()==runtime,"Conditional CORE runtime changed before software acceptance")
  descriptor=dump(out/"acceptance.json",obj)
  owned_source_readback(original,runners,original_before,frozen_before);need(conditional_core_runtime()==runtime,"Conditional CORE runtime changed after software output")
  verify(snapshot,True);verify(cr,True);verify(co["log"],True);verify(descriptor,True)
  print(json.dumps(dict(status=SOFTWARE_STATUS,acceptance=descriptor),sort_keys=True),flush=True)
 except Exception as e:
  dump(out/"typed_incomplete.json",dict(status="FINAL_SOURCE_MATERIALIZED_SOFTWARE_TYPED_INCOMPLETE",failed_stage=stage,reason_type=type(e).__name__,reason=str(e),allocation=allocation,source_staged=False,ACTIVE_changed=False));raise

def audit(plan_path,out):
 allocation=cpu();runtime=conditional_core_runtime();out=safe_path(out);out.mkdir(parents=True,exist_ok=False);stage="bootstrap"
 try:
  original,original_before=owned_source_bundle(Path(__file__).resolve().parent)
  runners=freeze_runner(out);frozen_before=[stable_metadata(r["path"])for r in runners]
  owned_source_readback(original,runners,original_before,frozen_before)
  for r in runners:
   if Path(r["path"]).suffix==".py":compile(Path(r["path"]).read_bytes(),r["path"],"exec",dont_inherit=True)
  syntax=subprocess.run(["bash","-n",str(out/"runner/final_source_cpu.sbatch")],capture_output=True,text=True);need(syntax.returncode==0,"Frozen library launcher syntax failed")
  need(fp(rec(Path(__file__).resolve()))==fp(next(r for r in runners if Path(r["path"]).name=="final_source_closure.py")),"Executing owned library differs from frozen source")
  test_receipt=contracts(out);stage="explicit_plan"
  p=safe_path(plan_path);need(not(p.stat().st_mode&0o222),"Explicit reviewed plan must be readonly")
  plan=read(p);modules=module_plan(plan);require_context_reader(plan,read)
  stage="base_readback";accepted=read(verify(plan["base_acceptance"]))
  need(accepted.get("status")=="CURRENT_SOURCE_REFRESH_READY_NOT_STAGED_NOT_FULL_DELIVERY"and accepted.get("source_issues")==0 and accepted.get("source_staged")is False,"Actual accepted repaired V10 sourcebase required")
  catalog_msa=CatalogMSAGapContexts(accepted["source_closure"])
  base=read(verify(accepted["source_inclusion"]));closure=read(verify(accepted["source_closure"]))
  catalog_msa.bind_base(closure)
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
  inherited_entrypoints=InheritedEntryPointScope(plan["base_acceptance"],accepted["source_inclusion"],base["files"])
  opaque_vendor=VendorExampleOpaqueLeaf(out)
  inventory_history=InventoryHistoryOpaqueLeaf(out,plan["base_acceptance"])
  archive_parent_history=ArchiveParentHistoryOpaqueLeaf(out,plan["base_acceptance"])
  relative_diagnostic_history=RelativeDiagnosticHistoryOpaqueLeaf(out,plan["base_acceptance"])
  parent_diagnostic_history=ParentDiagnosticHistoryOpaqueLeaf(out,plan["base_acceptance"])
  worker_controls=FiniteWorkerControlAliases(out,plan["base_acceptance"],accepted["source_closure"])
  worker_controls.begin()
  rows={};aliases={};inherited_edges={};history={};all_edges=[];sources={};deps={};data=set();gate_records=[];seen=set()
  def alias(logical,physical):
   reject_parent_diagnostic_history_declaration(logical);reject_relative_diagnostic_history_declaration(logical);reject_archive_parent_history_declaration(logical);reject_catalog_msa_gap_declaration(logical);reject_inventory_history_declaration(logical);reject_parent_diagnostic_history_declaration(physical);reject_relative_diagnostic_history_declaration(physical);reject_archive_parent_history_declaration(physical);reject_catalog_msa_gap_declaration(physical);reject_inventory_history_declaration(physical)
   reject_vendor_example_declaration(logical);reject_vendor_example_declaration(physical)
   receipt_shape(logical);receipt_shape(physical);need(fp(logical)==fp(physical),"Source alias changes bytes")
   k=key(logical)
   if k in aliases:need(fp(aliases[k])==fp(physical),"Conflicting alias")
   aliases[k]=physical
  for row in base["files"]:
   reject_catalog_msa_gap_declaration(row["source"]);verify(row["source"],True);alias(row["original_source"],row["source"])
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
   reject_parent_diagnostic_history_declaration(r);reject_relative_diagnostic_history_declaration(r);reject_archive_parent_history_declaration(r);reject_catalog_msa_gap_declaration(r);reject_inventory_history_declaration(r)
   receipt_shape(r);need(not _worker_related(r),"Exceptional worker alias requires its before-seen context route")
   if key(r)in aliases:return verify(aliases[key(r)]),"EXPLICIT_EXACT_BYTE_ALIAS"
   return verify(r),"EXACT_ORIGINAL"
  frozen=out/"readonly_source_bytes";frozen.mkdir()
  def add(r,d,roles,logical=None,inherited_row=None,inherited_index=None):
   reject_parent_diagnostic_history_declaration(r);reject_relative_diagnostic_history_declaration(r);reject_archive_parent_history_declaration(r);reject_catalog_msa_gap_declaration(r);reject_inventory_history_declaration(r)
   if logical is not None:reject_parent_diagnostic_history_declaration(logical);reject_relative_diagnostic_history_declaration(logical);reject_archive_parent_history_declaration(logical);reject_catalog_msa_gap_declaration(logical);reject_inventory_history_declaration(logical)
   reject_worker_declaration(r)
   reject_vendor_example_declaration(r)
   if logical is not None:reject_vendor_example_declaration(logical)
   inherited_kind=None
   if inherited_row is None:d=eligible_public(r,d)
   else:d,inherited_kind=inherited_entrypoints.permission(inherited_index,inherited_row,r,d,roles)
   physical,basis=resolve(r)
   if inherited_kind is not None:
    need(not(physical.stat().st_mode&0o222)and not conditional(physical)and not any(x in physical.parts for x in (".git","site-packages","weights","params")),"Finite inherited entrypoint bytes must remain readonly nonruntime SOURCE")
   b=physical.read_bytes()
   need(fp(rec(physical))==fp(r),"Source changed during CPU readback")
   b.decode("utf-8")
   need(not SECRET_RE.search(b.decode("utf-8"))and "-----BEGIN "+"OPENSSH PRIVATE KEY-----"not in b.decode("utf-8"),"Potential credential in selected public source; root review required")
   c=frozen/(r["sha256"]+"_"+physical.name)
   if c.exists():need(c.read_bytes()==b,"Frozen source collision")
   else:c.write_bytes(b);c.chmod(0o444)
   if d in rows:need(fp(rows[d]["source"])==fp(r),"Different sources target same repository destination")
   else:rows[d]=dict(source=rec(c),original_source=r,repository_relative=d,roles=[],logical_receipts=[],kind=inherited_kind or kind(physical),cluster_specific=b"/lustre/users/"in b or b"#SBATCH"in b)
   rows[d]["roles"]=sorted(set(rows[d]["roles"])|set(roles));rows[d]["role"]=";".join(rows[d]["roles"])
   if logical and logical not in rows[d]["logical_receipts"]:rows[d]["logical_receipts"].append(logical)
  for inherited_index,row in enumerate(base["files"]):
   inherited_destination,inherited_roles=inherited_source_route(row,replacement_ops)
   add(row["source"],inherited_destination,inherited_roles,row.get("original_source"),row,inherited_index)
   inherited_entrypoints.mark_retained(inherited_index,row)
  inherited_entrypoints.require_complete()
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
   catalog_msa.incoming(r,module)
   catalog_annotation=catalog_msa.edge(r,parent,trail,module,history)
   if catalog_annotation is not None:
    all_edges.append(catalog_annotation);continue
   parent_diagnostic_edge=parent_diagnostic_history.edge(r,parent,trail,module)
   if parent_diagnostic_edge is not None:
    data.add(key(r));all_edges.append(parent_diagnostic_edge)
    queue.extend((child["receipt"],r["path"],tuple(child["field"]),module)for child in parent_diagnostic_history_source_children())
    continue
   parent_diagnostic_source_child=parent_diagnostic_history.source_child_context(r,parent,trail,module)
   if parent_diagnostic_source_child:need(ek not in history and not conditional(r["path"]),"Fixed Source2 children must use ordinary current Source verification")
   relative_diagnostic_edge=relative_diagnostic_history.edge(r,parent,trail,module)
   if relative_diagnostic_edge is not None:
    data.add(key(r));all_edges.append(relative_diagnostic_edge);continue
   archive_parent_edge=archive_parent_history.edge(r,parent,trail,module)
   if archive_parent_edge is not None:
    data.add(key(r));all_edges.append(archive_parent_edge);continue
   inventory_edge=inventory_history.edge(r,parent,trail,module)
   if inventory_edge is not None:
    data.add(key(r));all_edges.append(inventory_edge);continue
   worker_edge=worker_controls.edge(r,parent,trail,module)
   opaque_edge=opaque_vendor.edge(r,parent,trail,module)
   if opaque_edge is not None:
    data.add(key(r));all_edges.append(opaque_edge);continue
   # Permission is an exact historical edge of the accepted base, checked before dedup.
   if ek in history:
    all_edges.append(dict(receipt=r,parent=parent,field=list(trail),module=module,role="INHERITED_EXACT_NONOPERATIVE_HISTORICAL_EDGE_NOT_CURRENT_BYTE_ACCEPTANCE"));continue
   if conditional(r["path"]):
    deps[key(r)]=r;all_edges.append(dict(receipt=r,parent=parent,field=list(trail),module=module,role="CONDITIONAL_INFERENCE_DEPENDENCY_EXCLUDED_FROM_PUBLIC_SOURCE"));continue
   if key(r)in seen and not parent_diagnostic_source_child:
    if worker_edge is not None:all_edges.append(worker_edge)
    continue
   seen.add(key(r))
   if worker_edge is not None:
    all_edges.append(worker_edge)
    worker_obj=worker_controls.parse(r,worker_edge)
    queue.extend((n,r["path"],t,module)for n,t in receipt_edges(worker_obj))
    continue
   suffix=Path(r["path"]).suffix
   if suffix not in RECEIPT_TEXT_EXT:
    data.add(key(r));all_edges.append(dict(receipt=r,parent=parent,field=list(trail),module=module,role="DATA_RECEIPT_RETAINED_NOT_RAW_REAUDITED"));continue
   physical,basis=resolve(r)
   all_edges.append(dict(receipt=r,parent=parent,field=list(trail),module=module,physical=rec(physical),resolution_basis=basis,role="EXACT_NEW_TEXT_RECEIPT_READBACK"))
   if suffix in SOURCE_EXT:
    sources[key(r)]=r
    if parent_diagnostic_source_child and any(fp(row["source"])==fp(r)for row in rows.values()):
     existing=[row for row in rows.values()if fp(row["source"])==fp(r)]
     need(len(existing)==1,"Fixed Source2 existing fingerprint has ambiguous public destinations")
     row=existing[0];existing_destination=row.get("repository_relative")
     need(row.get("kind")=="IMPLEMENTATION" and type(row.get("roles"))is list and bool(row["roles"])
          and all(type(role)is str for role in row["roles"]) and len(set(row["roles"]))==len(row["roles"])
          and set(row["roles"])<=REQUIRED_MODULES|{"RECURSIVE_OPERATIVE_SOURCE"}
          and (row.get("original_source")==r or r in row.get("logical_receipts",[])),
          "Fixed Source2 existing public identity/kind/roles are incompatible")
     preserved={name:row[name]for name in ("source","original_source","repository_relative","kind","cluster_specific")}
     need(eligible_public(r,existing_destination)==existing_destination,"Fixed Source2 existing public destination is incompatible")
     add(r,existing_destination,[module,"RECURSIVE_OPERATIVE_SOURCE"],r)
     need(all(exact_json(rows[existing_destination][name],value)for name,value in preserved.items()),
          "Fixed Source2 ordinary add changed existing identity/kind/destination")
    elif not any(fp(row["source"])==fp(r)for row in rows.values()):
     add(r,"rebuild/benchmarks/20261011/exact_source_aliases/"+r["sha256"]+"_"+Path(r["path"]).name,[module,"RECURSIVE_OPERATIVE_SOURCE"],r)
   if suffix==".json":
    obj=read(physical)
    catalog_msa.opened(r,physical,obj,module)
    if metadata_only(obj):continue
    # Accepted edge-seal annotations are coverage metadata, not invented source edges.
    if isinstance(obj,dict)and "historical_MSA_gaps"in obj:
     recorded={(key(x["original"]),x["parent"],tuple(x["trail"]))for x in obj["historical_MSA_gaps"]}
     need(len(recorded)==2 and recorded<=set(history),"Historical annotation set differs from inherited exact accepted edges")
     obj={k:v for k,v in obj.items()if k!="historical_MSA_gaps"}
    queue.extend((n,r["path"],t,module)for n,t in receipt_edges(obj))
  catalog_msa_active=catalog_msa.require_complete()
  parent_diagnostic_history_active=parent_diagnostic_history.require_complete()
  parent_diagnostic_history_proof=None;parent_diagnostic_history_aliases=None
  parent_diagnostic_graph_controls={}
  final_history_graph_controls={}
  final_history_active=catalog_msa_active or any(scope.active for scope in (inventory_history,archive_parent_history,relative_diagnostic_history,parent_diagnostic_history))
  history_control_native=[]
  def history_final_native_sweep():
   records=list(original_before)+list(frozen_before)+[runtime["logical_metadata"],runtime["resolved_metadata"]]
   for scope in (inventory_history,archive_parent_history,relative_diagnostic_history,parent_diagnostic_history):
    if scope.copy_receipt is not None:
     records.extend(scope.authorities_before)
     records.extend([scope.leaf_before,scope.copy_before,scope.directory_before])
   records.extend(catalog_msa.original_metadata)
   records.extend(history_control_native)
   records.extend(metadata for receipt,metadata in final_history_graph_controls.values())
   return _fixed_history_native_union_sweep(records)
  def catalog_msa_output_readback():
   if catalog_msa_active:
    complete={"source_receipt_closure_final.json","source_inclusion_final.json","acceptance.json"}
    if complete<=set(final_history_graph_controls):
     names={"acceptance.json":"acceptance","source_receipt_closure_final.json":"source_closure","source_inclusion_final.json":"source_inclusion"}
     catalog_msa_gap_graph_readback({names[name]:value for name,value in final_history_graph_controls.items()})
    else:
     actual_C=dict(base_closure=accepted["source_closure"],edges=all_edges)
     for name,(receipt,metadata)in final_history_graph_controls.items():
      path=verify(receipt,True)
      need(stable_metadata(path)==metadata,"Catalog MSA graph native changed before JSON")
      produced=read(path)
      need(rec(path)==receipt and stable_metadata(path)==metadata,"Catalog MSA graph changed during JSON")
      if name=="source_receipt_closure_final.json":actual_C=produced
      if name=="source_inclusion_final.json":need(produced.get("source_receipt_closure")==closed,"Catalog MSA I/C pointer fork")
     catalog_msa.validate_graph(actual_C)
     for receipt,metadata in final_history_graph_controls.values():
      need(rec(receipt["path"])==receipt and stable_metadata(receipt["path"])==metadata,
           "Catalog MSA graph changed after all final JSON")
    history_final_native_sweep()
  catalog_msa_output_readback()
  if parent_diagnostic_history_active:
   parent_diagnostic_history_aliases,parent_diagnostic_alias_metadata=_parent_diagnostic_history_write_control(out/"parent_diagnostic_history_opaque_aliases.json",parent_diagnostic_history.alias_index())
   parent_diagnostic_history_proof,parent_diagnostic_proof_metadata=_parent_diagnostic_history_write_control(out/"parent_diagnostic_history_opaque_leaf_proof.json",dict(parent_diagnostic_history.proof(),allocation=allocation,exact_alias_index=parent_diagnostic_history_aliases))
   history_control_native.extend([parent_diagnostic_proof_metadata,parent_diagnostic_alias_metadata])
  def parent_diagnostic_history_output_readback():
   if parent_diagnostic_history_active:
    parent_diagnostic_history.readback()
    saved,unused=_parent_diagnostic_history_control_readback(parent_diagnostic_history_proof,parent_diagnostic_proof_metadata)
    index,unused=_parent_diagnostic_history_control_readback(parent_diagnostic_history_aliases,parent_diagnostic_alias_metadata)
    verify_parent_diagnostic_history_preservation(saved,index,allocation)
    graph={"edges":all_edges};included={"files":list(rows.values())}
    for name,(receipt,expected_metadata)in parent_diagnostic_graph_controls.items():
     path=verify(receipt,True);before=stable_metadata(path)
     _parent_diagnostic_history_metadata_shape(before,str(path),receipt["bytes"])
     need(exact_json(before,expected_metadata),"Actual13290 graph control native metadata drifted")
     produced=read(path)
     need(produced.get("parent_diagnostic_history_opaque_leaf_proof")==parent_diagnostic_history_proof and produced.get("parent_diagnostic_history_opaque_aliases")==parent_diagnostic_history_aliases,"Actual A/I/C parent-diagnostic proof/index pointers differ")
     need(rec(path)==receipt and stable_metadata(path)==before,"Actual13290 graph control changed during final JSON read")
     if name=="source_receipt_closure_final.json":graph=produced
     if name=="source_inclusion_final.json":included=produced
    parent_diagnostic_history_source_coverage(saved,graph,included)
    for receipt,expected_metadata in parent_diagnostic_graph_controls.values():
     need(rec(receipt["path"])==receipt and stable_metadata(receipt["path"])==expected_metadata,
          "Actual13290 graph control changed after all final JSON and coverage reads")
    _parent_diagnostic_history_control_readback(parent_diagnostic_history_proof,parent_diagnostic_proof_metadata)
    _parent_diagnostic_history_control_readback(parent_diagnostic_history_aliases,parent_diagnostic_alias_metadata)
    _fixed_history_authority_fence("parent13290", parent_diagnostic_history.authorities_before)
    for receipt,expected_metadata in parent_diagnostic_graph_controls.values():
     need(rec(receipt["path"])==receipt and stable_metadata(receipt["path"])==expected_metadata,
          "Actual13290 graph control changed after final proof/index readback")
    history_final_native_sweep()
  parent_diagnostic_history_output_readback()
  catalog_msa_output_readback()
  relative_diagnostic_history_active=relative_diagnostic_history.require_complete()
  relative_diagnostic_history_proof=None;relative_diagnostic_history_aliases=None
  if relative_diagnostic_history_active:
   relative_diagnostic_history_aliases,relative_diagnostic_alias_metadata=_relative_diagnostic_history_write_control(out/"relative_diagnostic_history_opaque_aliases.json",relative_diagnostic_history.alias_index())
   relative_diagnostic_history_proof,relative_diagnostic_proof_metadata=_relative_diagnostic_history_write_control(out/"relative_diagnostic_history_opaque_leaf_proof.json",dict(relative_diagnostic_history.proof(),allocation=allocation,exact_alias_index=relative_diagnostic_history_aliases))
   history_control_native.extend([relative_diagnostic_proof_metadata,relative_diagnostic_alias_metadata])
  def relative_diagnostic_history_output_readback():
   if relative_diagnostic_history_active:
    relative_diagnostic_history.readback()
    saved,unused=_relative_diagnostic_history_control_readback(relative_diagnostic_history_proof,relative_diagnostic_proof_metadata)
    index,unused=_relative_diagnostic_history_control_readback(relative_diagnostic_history_aliases,relative_diagnostic_alias_metadata)
    verify_relative_diagnostic_history_preservation(saved,index,allocation)
    _relative_diagnostic_history_control_readback(relative_diagnostic_history_proof,relative_diagnostic_proof_metadata)
    _relative_diagnostic_history_control_readback(relative_diagnostic_history_aliases,relative_diagnostic_alias_metadata)
    _fixed_history_authority_fence("relative13295", relative_diagnostic_history.authorities_before)
    history_final_native_sweep()
  relative_diagnostic_history_output_readback()
  parent_diagnostic_history_output_readback()
  catalog_msa_output_readback()
  archive_parent_history_active=archive_parent_history.require_complete()
  archive_parent_history_proof=None;archive_parent_history_aliases=None
  if archive_parent_history_active:
   archive_parent_history_aliases,archive_parent_alias_metadata=_archive_parent_history_write_control(out/"archive_parent_history_opaque_aliases.json",archive_parent_history.alias_index())
   archive_parent_history_proof,archive_parent_proof_metadata=_archive_parent_history_write_control(out/"archive_parent_history_opaque_leaf_proof.json",dict(archive_parent_history.proof(),allocation=allocation,exact_alias_index=archive_parent_history_aliases))
   history_control_native.extend([archive_parent_proof_metadata,archive_parent_alias_metadata])
  def archive_parent_history_output_readback():
   if archive_parent_history_active:
    archive_parent_history.readback()
    saved,unused=_archive_parent_history_control_readback(archive_parent_history_proof,archive_parent_proof_metadata)
    index,unused=_archive_parent_history_control_readback(archive_parent_history_aliases,archive_parent_alias_metadata)
    verify_archive_parent_history_preservation(saved,index,allocation)
    _archive_parent_history_control_readback(archive_parent_history_proof,archive_parent_proof_metadata)
    _archive_parent_history_control_readback(archive_parent_history_aliases,archive_parent_alias_metadata)
    _fixed_history_authority_fence("archive13298", archive_parent_history.authorities_before)
    history_final_native_sweep()
  archive_parent_history_output_readback()
  relative_diagnostic_history_output_readback()
  parent_diagnostic_history_output_readback()
  catalog_msa_output_readback()
  inventory_history_active=inventory_history.require_complete()
  inventory_history_proof=None;inventory_history_aliases=None
  if inventory_history_active:
   inventory_history_aliases=dump(out/"inventory_history_opaque_aliases.json",inventory_history.alias_index())
   inventory_history_proof=dump(out/"inventory_history_opaque_leaf_proof.json",dict(inventory_history.proof(),allocation=allocation,exact_alias_index=inventory_history_aliases))
   history_control_native.extend([stable_metadata(inventory_history_proof["path"]),stable_metadata(inventory_history_aliases["path"])])
  def inventory_history_output_readback():
   if inventory_history_active:
    inventory_history.readback();verify(inventory_history_aliases,True);verify(inventory_history_proof,True)
    verify_inventory_history_preservation(read(inventory_history_proof["path"]),read(inventory_history_aliases["path"]),allocation)
    _fixed_history_authority_fence("inventory13299", inventory_history.authorities_before)
    history_final_native_sweep()
  inventory_history_output_readback()
  archive_parent_history_output_readback()
  relative_diagnostic_history_output_readback()
  parent_diagnostic_history_output_readback()
  catalog_msa_output_readback()
  worker_active=worker_controls.require_complete()
  worker_proof=None;worker_aliases=None
  if worker_active:
   worker_aliases=dump(out/"finite_worker_control_aliases.json",worker_controls.alias_index())
   worker_proof=dump(out/"finite_worker_control_proof.json",dict(worker_controls.proof(),allocation=allocation,exact_alias_index=worker_aliases))
  def worker_output_readback():
   if worker_active:
    worker_controls.readback();verify(worker_aliases,True);verify(worker_proof,True)
    verify_finite_worker_preservation(read(worker_proof["path"]),read(worker_aliases["path"]),allocation)
  worker_output_readback()
  inventory_history_output_readback()
  archive_parent_history_output_readback()
  relative_diagnostic_history_output_readback()
  parent_diagnostic_history_output_readback()
  catalog_msa_output_readback()
  opaque_vendor_active=opaque_vendor.require_complete(inherited_entrypoints.actual_base)
  opaque_aliases=None;opaque_proof=None
  if opaque_vendor_active:
   opaque_aliases=dump(out/"vendor_example_opaque_aliases.json",opaque_vendor.alias_index())
   opaque_proof=dump(out/"vendor_example_opaque_leaf_proof.json",dict(opaque_vendor.proof(),allocation=allocation,exact_alias_index=opaque_aliases))
   opaque_vendor.readback()
  frozen.chmod(0o555)
  inherited_entrypoint_proof=dump(out/"inherited_entrypoint_source_scope.json",inherited_entrypoints.proof())
  owned_source_readback(original,runners,original_before,frozen_before);need(conditional_core_runtime()==runtime,"Owned source/runtime drift after source graph")
  context_proof=dump(out/"exact_five_parent_context_reader_proof.json",require_context_reader(plan,read,True))
  closed=dump(out/"source_receipt_closure_final.json",dict(schema="final-source-receipt-closure.v2",status="EXACT_NEW_SOURCE_DEPENDENCIES_WITH_INHERITED_TYPED_HISTORY",base_closure=accepted["source_closure"],inherited_entrypoint_source_scope=inherited_entrypoint_proof,vendor_example_opaque_leaf_proof=opaque_proof,vendor_example_opaque_aliases=opaque_aliases,finite_worker_control_proof=worker_proof,finite_worker_control_aliases=worker_aliases,inventory_history_opaque_leaf_proof=inventory_history_proof,inventory_history_opaque_aliases=inventory_history_aliases,archive_parent_history_opaque_leaf_proof=archive_parent_history_proof,archive_parent_history_opaque_aliases=archive_parent_history_aliases,relative_diagnostic_history_opaque_leaf_proof=relative_diagnostic_history_proof,relative_diagnostic_history_opaque_aliases=relative_diagnostic_history_aliases,parent_diagnostic_history_opaque_leaf_proof=parent_diagnostic_history_proof,parent_diagnostic_history_opaque_aliases=parent_diagnostic_history_aliases,module_gates=gate_records,edges=all_edges,source_receipts=list(sources.values()),conditional_dependencies=list(deps.values()),data_receipts_retained_not_reaudited_n=len(data),no_new_historical_waivers=True,raw_content_reaudited=False))
  if parent_diagnostic_history_active:parent_diagnostic_graph_controls["source_receipt_closure_final.json"]=(closed,stable_metadata(closed["path"]))
  if final_history_active:final_history_graph_controls["source_receipt_closure_final.json"]=(closed,stable_metadata(closed["path"]))
  worker_output_readback()
  inventory_history_output_readback()
  archive_parent_history_output_readback()
  relative_diagnostic_history_output_readback()
  parent_diagnostic_history_output_readback()
  catalog_msa_output_readback()
  stage="inclusion"
  inclusion=dump(out/"source_inclusion_final.json",dict(schema="benchmark-source-inclusion.v3",status="SOURCE_INCLUSION_AUDIT_PASS",authority_root=str(R),files=sorted(rows.values(),key=lambda x:x["repository_relative"]),issues=[],applied=False,runner_source_snapshot=runners,allocation=allocation,base_inclusion=accepted["source_inclusion"],inherited_entrypoint_source_scope=inherited_entrypoint_proof,vendor_example_opaque_leaf_proof=opaque_proof,vendor_example_opaque_aliases=opaque_aliases,finite_worker_control_proof=worker_proof,finite_worker_control_aliases=worker_aliases,inventory_history_opaque_leaf_proof=inventory_history_proof,inventory_history_opaque_aliases=inventory_history_aliases,archive_parent_history_opaque_leaf_proof=archive_parent_history_proof,archive_parent_history_opaque_aliases=archive_parent_history_aliases,relative_diagnostic_history_opaque_leaf_proof=relative_diagnostic_history_proof,relative_diagnostic_history_opaque_aliases=relative_diagnostic_history_aliases,parent_diagnostic_history_opaque_leaf_proof=parent_diagnostic_history_proof,parent_diagnostic_history_opaque_aliases=parent_diagnostic_history_aliases,source_receipt_closure=closed,explicit_plan=rec(p),module_gates=gate_records,entry_kind_counts=dict(collections.Counter(x["kind"]for x in rows.values())),formal_array_job_id="13260",source_staged=False,source_published=False,ACTIVE_changed=False,scientific_endpoint_acceptance_performed=False,scope="Exact final public source coverage only; root scientific content/publication/archive/promotion remain separate required gates"))
  if parent_diagnostic_history_active:parent_diagnostic_graph_controls["source_inclusion_final.json"]=(inclusion,stable_metadata(inclusion["path"]))
  if final_history_active:final_history_graph_controls["source_inclusion_final.json"]=(inclusion,stable_metadata(inclusion["path"]))
  worker_output_readback()
  inventory_history_output_readback()
  archive_parent_history_output_readback()
  relative_diagnostic_history_output_readback()
  parent_diagnostic_history_output_readback()
  catalog_msa_output_readback()
  result=dict(schema="final-source-closure-acceptance.v3",status="FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED",source_inclusion=inclusion,source_closure=closed,inherited_entrypoint_source_scope=inherited_entrypoint_proof,vendor_example_opaque_leaf_proof=opaque_proof,vendor_example_opaque_aliases=opaque_aliases,finite_worker_control_proof=worker_proof,finite_worker_control_aliases=worker_aliases,inventory_history_opaque_leaf_proof=inventory_history_proof,inventory_history_opaque_aliases=inventory_history_aliases,archive_parent_history_opaque_leaf_proof=archive_parent_history_proof,archive_parent_history_opaque_aliases=archive_parent_history_aliases,relative_diagnostic_history_opaque_leaf_proof=relative_diagnostic_history_proof,relative_diagnostic_history_opaque_aliases=relative_diagnostic_history_aliases,parent_diagnostic_history_opaque_leaf_proof=parent_diagnostic_history_proof,parent_diagnostic_history_opaque_aliases=parent_diagnostic_history_aliases,original_executing_sources=original,conditional_core_runtime=runtime,whole6_source_prepost_PASS=True,original_and_frozen_owned_bytes_identical=True,conditional_runtime_prepost_PASS=True,exact_five_parent_context_reader_proof=context_proof,mandatory_derived_pipeline_qualification=derived_qualification_proof,explicit_plan=rec(p),contracts=test_receipt,source_entries=len(rows),source_issues=0,required_modules=sorted(REQUIRED_MODULES),module_gates=gate_records,allocation=allocation,source_staged=False,source_published=False,ACTIVE_changed=False,no_model_calls=True,no_GPU_submission=True)
  owned_source_readback(original,runners,original_before,frozen_before);need(conditional_core_runtime()==runtime,"Owned source/runtime drift before source audit acceptance")
  if opaque_vendor_active:opaque_vendor.readback();verify(opaque_aliases,True);verify(opaque_proof,True)
  worker_output_readback()
  inventory_history_output_readback()
  archive_parent_history_output_readback()
  relative_diagnostic_history_output_readback()
  parent_diagnostic_history_output_readback()
  catalog_msa_output_readback()
  descriptor=dump(out/"acceptance.json",result)
  if parent_diagnostic_history_active:parent_diagnostic_graph_controls["acceptance.json"]=(descriptor,stable_metadata(descriptor["path"]))
  if final_history_active:final_history_graph_controls["acceptance.json"]=(descriptor,stable_metadata(descriptor["path"]))
  worker_output_readback()
  inventory_history_output_readback()
  archive_parent_history_output_readback()
  relative_diagnostic_history_output_readback()
  parent_diagnostic_history_output_readback()
  catalog_msa_output_readback()
  if opaque_vendor_active:opaque_vendor.readback();verify(opaque_aliases,True);verify(opaque_proof,True)
  owned_source_readback(original,runners,original_before,frozen_before);need(conditional_core_runtime()==runtime,"Owned source/runtime drift after source audit output")
  print(json.dumps({"acceptance":descriptor},sort_keys=True),flush=True)
  for x in out.glob("*.json"):
   final_mode=x.lstat().st_mode
   if not(stat.S_ISREG(final_mode)and stat.S_IMODE(final_mode)==0o444):
    x.chmod(0o444)
  inventory_history_output_readback()
  archive_parent_history_output_readback()
  relative_diagnostic_history_output_readback()
  parent_diagnostic_history_output_readback()
  catalog_msa_output_readback()
  owned_source_readback(original,runners,original_before,frozen_before);need(conditional_core_runtime()==runtime,"Owned source/runtime drift after final history proof and readonly outputs")
  for family,active,scope in (("inventory13299",inventory_history_active,inventory_history),
                             ("archive13298",archive_parent_history_active,archive_parent_history),
                             ("relative13295",relative_diagnostic_history_active,relative_diagnostic_history),
                             ("parent13290",parent_diagnostic_history_active,parent_diagnostic_history)):
   if active:_fixed_history_authority_fence(family,scope.authorities_before)
  catalog_msa.fence()
  for receipt,expected_metadata in final_history_graph_controls.values():
   need(rec(receipt["path"])==receipt and stable_metadata(receipt["path"])==expected_metadata,
        "Actual finite history final graph bytes/native metadata changed before final status")
  if final_history_active:history_final_native_sweep()
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
