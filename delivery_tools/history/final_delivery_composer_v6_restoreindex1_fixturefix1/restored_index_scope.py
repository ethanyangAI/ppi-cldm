#!/usr/bin/env python3
"""Explicit package-index input scope for unchanged independent recomputation.
Only tagged new outputs, exact controls, owned executors and qualified CPU runtimes
have distinct permissions. No bare prefix is an input-read exemption.
"""
import argparse,contextlib,fnmatch,hashlib,importlib.util,json,os,re,subprocess,sys,types
from pathlib import Path
SCHEMA="strict-restored-package-index-scope.v1"
STATUS="ALL_ORIGINAL_RECOMPUTATION_INPUTS_EXACT_INDEXED_AND_RECOMPUTED_OUTPUTS_SCOPED"
MSA_CODE="import json,sys; sys.path.insert(0,sys.argv[1]); from control_msa_check import verify_roundtrip; print(json.dumps(verify_roundtrip(*sys.argv[2:]),sort_keys=True))"
RUNTIME_SCHEMA="conditional-installed-CPU-runtime-byte-qualification.v1"
def need(v,msg):
 if not v:raise ValueError(msg)
def rid(r):return(r["path"],r["bytes"],r["sha256"])
def lexical(p):
 raw=os.fspath(p);need(isinstance(raw,str)and raw.startswith("/")and(raw=="/"or all(x not in("","..",".")for x in raw.split("/")[1:])),"Absolute raw lexical scope path required");p=Path(raw);return p
def receipt(r):
 need(isinstance(r,dict)and isinstance(r.get("path"),str)and isinstance(r.get("bytes"),int)and not isinstance(r["bytes"],bool)and r["bytes"]>=0 and re.fullmatch("[0-9a-f]{64}",r.get("sha256","")),"Exact indexed receipt required");lexical(r["path"]);return r
def checksum(p):
 h=hashlib.sha256();n=0
 with Path(p).open("rb")as f:
  for b in iter(lambda:f.read(1048576),b""):n+=len(b);h.update(b)
 return dict(path=str(p),bytes=n,sha256=h.hexdigest())
def exact_file(p,r,root=None,readonly=True):
 p=lexical(p);need(p.is_file()and not p.is_symlink()and p.resolve()==p,"Regular nonsymlink exact input required")
 if root is not None:need(p.is_relative_to(root),"Indexed input outside restored boundary")
 if readonly:need(not(p.stat().st_mode&0o222),"Indexed original input must be readonly")
 a=checksum(p);need((a["bytes"],a["sha256"])==(r["bytes"],r["sha256"]),"Exact indexed input bytes differ");return p
def runtime_descriptor(logical):
 logical=lexical(logical);real=logical.resolve(strict=True);need(real.is_file()and not real.is_symlink(),"Resolved conditional CPU executable must be regular")
 link=os.readlink(logical)if logical.is_symlink()else None
 a=checksum(real)
 return dict(logical_executable=str(logical),logical_link_text=link,resolved_executable_path=str(real),resolved_bytes=a["bytes"],resolved_sha256=a["sha256"],scope="QUALIFIED_CONDITIONAL_INSTALLED_CPU_RUNTIME_ONLY",included_in_package=False)
def verify_runtime(record):
 need(record.get("scope")=="QUALIFIED_CONDITIONAL_INSTALLED_CPU_RUNTIME_ONLY"and record.get("included_in_package")is False,"Installed CPU runtime is explicit conditional scope only")
 need(runtime_descriptor(record["logical_executable"])==record,"Installed conditional CPU executable/link bytes drifted")
 return record["logical_executable"]
def qualify_runtime(common_config,common_config_receipt,common_receipt,common_content,runtime_receipt,out,source,allocation,dump):
 # Executable identity comes from the actual accepted common config, not basename inference.
 py=common_config["colabfold_cpu_python"];need(isinstance(py,str)and Path(py).is_absolute(),"Actual common CPU interpreter required")
 records=dict(core=runtime_descriptor(sys.executable),msa=runtime_descriptor(py))
 q=dict(schema=RUNTIME_SCHEMA,status="ACTUAL_COMMON_AND_RUNTIME_LINKED_CONDITIONAL_CPU_EXECUTABLE_BYTES_QUALIFIED",accepted_common_config=common_config_receipt,accepted_common_successor=common_receipt,accepted_common_content=common_content,accepted_runtime=runtime_receipt,actual_common_cpu_python=py,runtimes=records,source=source,allocation=allocation,no_binary_or_packages_redistributed=True,scientific_evidence_input_exception=False)
 for r in records.values():verify_runtime(r)
 return dump(Path(out)/"conditional_restore_CPU_runtime.json",q)
class StrictIndex:
 def __init__(self,pkg,root,out,aliases=None,controls=(),owned=(),runtime=None,allow_existing_output=False):
  need(pkg.get("schema")=="benchmark-delivery-package.v1"and pkg.get("status")=="PACKAGED_AWAITING_INDEPENDENT_RESTORE","Exact authority package required")
  self.pkg=pkg;self.authority=lexical(pkg["authority_root"]);self.root=lexical(root);self.out=lexical(out)
  need(self.root.resolve()==self.root and self.root.is_dir()and self.out.is_relative_to(self.root)and self.out!=self.root and self.out.resolve()==self.out,"Isolated root/new-output containment required")
  need(allow_existing_output or not self.out.exists(),"Trusted recomputation output must initially be absent")
  self.rows={};self.paths={};self.aliases={};self.controls={};self.owned={};self.reads=set();self.outputs=set();self.processes=[];self.loaded=[]
  for row in pkg["manifest"]:
   r=receipt(row["receipt"]);rel=row["relative"]
   need(Path(r["path"]).is_relative_to(self.authority)and Path(r["path"]).relative_to(self.authority).as_posix()==rel and rel and all(x not in("","..",".")for x in rel.split("/")),"Index logical path/relative differs")
   p=self.root/rel;need(not p.is_relative_to(self.out),"Original package input cannot overlap new output scope")
   need(r["path"]not in self.paths and rid(r)not in self.rows,"Duplicate/conflicting package index path")
   self.rows[rid(r)]=(r,p);self.paths[r["path"]]=[rid(r)]
  for e in(aliases or{}).get("aliases",[]):
   a=receipt(e["original"]);b=receipt(e["archived"])
   need(e.get("status")=="READONLY_BYTE_IDENTICAL_ALIAS"and(a["bytes"],a["sha256"])==(b["bytes"],b["sha256"])and rid(b)in self.rows,"Alias must be byte-identical to an indexed file")
   k=rid(a);need(k not in self.aliases,"Duplicate alias identity")
   need(k not in self.rows or self.rows[k][1]==self.rows[rid(b)][1],"Alias conflicts with indexed original")
   self.aliases[k]=rid(b);self.paths.setdefault(a["path"],[])
   if k not in self.paths[a["path"]]:self.paths[a["path"]].append(k)
  for r in controls:
   receipt(r);need(r["path"]not in self.controls,"Duplicate control receipt");self.controls[r["path"]]=r
  for r in owned:
   receipt(r);need(r["path"]not in self.owned,"Duplicate owned executor");self.owned[r["path"]]=r
  self.runtime=runtime
  self.directories={self.root}
  for r,p in self.rows.values():
   self.directories.update(x for x in p.parents if x.is_relative_to(self.root))
  self.control_directories={Path(r["path"]).parent for r in self.controls.values()}
 def _logical(self,p):
  p=lexical(p)
  if p.is_relative_to(self.root):return self.authority/p.relative_to(self.root)
  return p
 def select(self,path,sha=None):
  logical=str(self._logical(path));keys=[k for k in self.paths.get(logical,[])if sha is None or k[2]==sha]
  need(len(keys)==1,"Original scientific/source path requires one exact index/alias identity: "+logical)
  key=keys[0];target=self.aliases.get(key,key);r,p=self.rows[target]
  exact_file(p,r,self.root);self.reads.add(key);return r,p,key
 def input(self,*parts,expected_sha=None):
  if len(parts)==1 and isinstance(parts[0],IndexedPath):
   v=parts[0];need(v.owner is self and v.scope=="INPUT","An output/control cannot satisfy an original input");return IndexedPath(self,v.logical,"INPUT",expected_sha or v.sha,v.physical_view)
  texts=[str(x)for x in parts];need(texts and all(all(c not in("","..",".")for c in(t.split("/")[1:]if t.startswith("/")else t.split("/")))for t in texts)and all(not t.startswith("/")for t in texts[1:]),"Raw original-input traversal/empty component forbidden")
  p=Path(*texts);p=lexical(p);return IndexedPath(self,p,"INPUT",expected_sha)
 def structural(self,p):
  if isinstance(p,IndexedPath):need(p.owner is self,"Cross-scope path owner");return p
  p=lexical(p)
  if p==self.out:return IndexedPath(self,p,"OUTPUT")
  if str(p)in self.controls:return IndexedPath(self,p,"CONTROL")
  if p==self.root:return IndexedPath(self,p,"DIRECTORY")
  return self.input(p)
 def common_path(self,p):
  if isinstance(p,IndexedPath):need(p.owner is self,"Cross-scope path owner");return p
  return self.input(p)
 def output(self,p):return IndexedPath(self,lexical(p),"OUTPUT")
 def physical(self,v,operation="read"):
  if v.scope=="INPUT":
   p=lexical(v.logical);mapped=self.root/p.relative_to(self.authority)if p.is_relative_to(self.authority)else p
   if mapped in self.directories and not mapped.is_file():
    need(operation in("directory","stat"),"Input directory cannot become a file-read exemption")
    need(mapped.resolve()==mapped and not mapped.is_symlink(),"Indexed virtual directory changed");return mapped
   return self.select(p,v.sha)[1]
  if v.scope=="CONTROL":
   need(operation!="write","Immutable control cannot be overwritten");return exact_file(v.logical,self.controls[str(v.logical)])
  if v.scope=="DIRECTORY":
   need(v.logical==self.root and operation in("directory","stat"),"Root directory is structural only");return self.root
  need(v.scope=="OUTPUT"and v.logical.is_relative_to(self.out),"Explicit trusted output tag required")
  p=lexical(v.logical);need(p.resolve()==p and not p.is_symlink(),"New output symlink/outside scope")
  if operation=="read":need(p.is_file(),"Fresh output file missing")
  return p
 def read_json(self,p):
  v=self.structural(p)if not isinstance(p,IndexedPath)else p
  return json.loads(v.read_text())
 def rec(self,p):
  v=self.structural(p)if not isinstance(p,IndexedPath)else p;actual=checksum(self.physical(v,"read"))
  actual["path"]=str(v);return actual
 def dump(self,p,obj):
  v=p if isinstance(p,IndexedPath)else self.structural(p);need(v.scope=="OUTPUT","Only new outputs can be dumped")
  v.parent.mkdir(parents=True,exist_ok=True)
  with v.open("x")as f:json.dump(obj,f,indent=2,allow_nan=False);f.write("\n")
  return self.rec(v)
 def verify(self,r,*unused):
  v=self.input(r["path"],expected_sha=r["sha256"]);a=self.rec(v)
  need((a["bytes"],a["sha256"])==(r["bytes"],r["sha256"]),"Declared indexed receipt differs")
  return v
 def after(self,touched_only=False):
  targets={self.aliases.get(k,k)for k in self.reads}if touched_only else set(self.rows)
  for key in targets:
   r,p=self.rows[key];exact_file(p,r,self.root)
  for r in self.controls.values():exact_file(r["path"],r)
  for r in self.owned.values():exact_file(r["path"],r)
  if self.runtime:
   for r in self.runtime["runtimes"].values():verify_runtime(r)
 def proof(self):
  return dict(schema=SCHEMA,status=STATUS,indexed_file_n=len(self.rows),indexed_original_identities_read=[dict(logical_path=k[0],bytes=k[1],sha256=k[2])for k in sorted(self.reads)],fresh_output_paths=sorted(self.outputs),subprocesses=self.processes,live_scientific_fallback=False,unindexed_original_input_allowed=False,source_JSON_rewritten=False,conditional_runtime_not_archived=True)
class IndexedPath:
 def __init__(self,owner,logical,scope,sha=None,physical_view=False):self.owner=owner;self.logical=lexical(logical);self.scope=scope;self.sha=sha;self.physical_view=physical_view
 def physical(self):
  self.owner.physical(self,"directory"if self._directory()else"read")
  return IndexedPath(self.owner,self.logical,self.scope,self.sha,True)
 def _directory(self):
  if self.scope in("DIRECTORY",):return True
  if self.scope=="OUTPUT":return self.logical.is_dir()or not self.logical.suffix
  p=self.logical;physical=self.owner.root/p.relative_to(self.owner.authority)if p.is_relative_to(self.owner.authority)else p
  return physical in self.owner.directories and not physical.is_file()
 def __str__(self):
  return str(self.owner.physical(self,"directory"if self._directory()else"read"))if self.physical_view else str(self.logical)
 def __fspath__(self):return str(self.owner.physical(self,"directory"if self._directory()else"read"))
 def __repr__(self):return "IndexedPath("+repr(str(self.logical))+","+self.scope+")"
 def __hash__(self):return hash((str(self.logical),self.scope))
 def __eq__(self,o):
  try:return self.logical==(o.logical if isinstance(o,IndexedPath)else Path(o))
  except TypeError:return False
 def __truediv__(self,p):
  need(not Path(str(p)).is_absolute()and all(x not in("","..",".")for x in str(p).split("/")),"Raw derived path traversal/empty component forbidden")
  scope=self.scope
  dest=self.logical/str(p)
  if scope=="DIRECTORY":scope="CONTROL"if str(dest)in self.owner.controls else"INPUT"
  return IndexedPath(self.owner,dest,scope,None,self.physical_view)
 @property
 def parent(self):
  scope="INPUT"if self.scope=="CONTROL"else self.scope
  logical=self.owner.physical(self,"directory"if self._directory()else"read").parent if self.physical_view else self.logical.parent
  return IndexedPath(self.owner,logical,scope,None,self.physical_view)
 @property
 def name(self):return self.logical.name
 @property
 def suffix(self):return self.logical.suffix
 @property
 def stem(self):return self.logical.stem
 @property
 def parts(self):return self.logical.parts
 def resolve(self,*a,**k):self.owner.physical(self,"directory"if self._directory()else"read");return self
 def absolute(self):return self
 def relative_to(self,p):return self.logical.relative_to(p.logical if isinstance(p,IndexedPath)else p)
 def is_relative_to(self,p):return self.logical.is_relative_to(p.logical if isinstance(p,IndexedPath)else p)
 def with_name(self,p):return self.parent/p
 def with_suffix(self,p):return self.parent/(self.logical.stem+p)
 def open(self,mode="r",*a,**kw):
  writing=any(c in mode for c in("w","a","x","+"));need(not writing or self.scope=="OUTPUT","Original indexed inputs are immutable")
  p=self.owner.physical(self,"write"if writing else"read")
  if writing:self.owner.outputs.add(str(p))
  return p.open(mode,*a,**kw)
 def read_text(self,*a,**k):return self.owner.physical(self,"read").read_text(*a,**k)
 def read_bytes(self):return self.owner.physical(self,"read").read_bytes()
 def write_text(self,s,*a,**k):
  need(self.scope=="OUTPUT","Input write forbidden");p=self.owner.physical(self,"write");self.owner.outputs.add(str(p));return p.write_text(s,*a,**k)
 def write_bytes(self,s):
  need(self.scope=="OUTPUT","Input write forbidden");p=self.owner.physical(self,"write");self.owner.outputs.add(str(p));return p.write_bytes(s)
 def mkdir(self,*a,**k):need(self.scope=="OUTPUT","Only new outputs may create directories");return self.owner.physical(self,"write").mkdir(*a,**k)
 def exists(self):
  try:return self.owner.physical(self,"stat"if self._directory()else"read").exists()
  except FileNotFoundError:return False
 def is_file(self):return self.owner.physical(self,"stat"if self._directory()else"read").is_file()
 def is_dir(self):return self.owner.physical(self,"stat"if self._directory()else"read").is_dir()
 def stat(self):return self.owner.physical(self,"stat"if self._directory()else"read").stat()
 def glob(self,pattern):
  need(self.scope=="INPUT"and ".."not in pattern.split("/")and not pattern.startswith("/"),"Only indexed directory glob is allowed")
  directory=self.owner.physical(self,"directory");observed=list(directory.glob(pattern))
  for p in observed:
   if p.is_dir():need(p in self.owner.directories and p.resolve()==p,"Unindexed/symbolic glob directory");continue
   self.owner.select(p);yield IndexedPath(self.owner,p,"INPUT",physical_view=True)
 def iterdir(self):return self.glob("*")
def isolated_subprocess(scope,config,owned_entry,original_run):
 def run(argv,*args,**kwargs):
  need(not args and isinstance(argv,list)and kwargs.get("shell",False)is False,"Only exact registered common subprocess forms")
  ip=scope.verify(config["official_ipsae"]).physical();msa=scope.verify(config["msa_roundtrip_source"]).physical()
  if len(argv)==6 and argv[0]==scope.runtime["runtimes"]["core"]["logical_executable"]:
   need(argv[1]==str(ip)and argv[4]in("10","15")and argv[5]=="15","Exact indexed official ipSAE/source/cutoff argv required")
   paths=[lexical(p)for p in argv[2:4]];need(paths[0].name=="scores.json"and paths[1].name=="model.pdb"and paths[0].parent==paths[1].parent and all(str(p)in scope.outputs and p.is_relative_to(scope.out)for p in paths),"Only previously created tagged common outputs may enter ipSAE")
   for p in paths:need(p.is_file()and not p.is_symlink()and p.resolve()==p,"Fresh ipSAE inputs unavailable")
   verify_runtime(scope.runtime["runtimes"]["core"]);exact_file(owned_entry["path"],owned_entry)
   childdir=scope.out/"strict_subprocess_inputs";childdir.mkdir(exist_ok=True);path=childdir/("ipsae_"+str(len(scope.processes))+".json")
   contract=dict(schema="indexed-IPSAE-subprocess-contract.v1",package=scope.pkg,package_control=next(r for r in scope.controls.values()if r["path"]!=str(scope.root/"RESTORE_HASH_ACCEPTANCE.json")),restore_root=str(scope.root),new_output_root=str(scope.out),aliases=dict(aliases=[dict(original=dict(path=k[0],bytes=k[1],sha256=k[2]),archived=scope.rows[v][0],status="READONLY_BYTE_IDENTICAL_ALIAS")for k,v in scope.aliases.items()]),owned_entry=owned_entry,runtime=scope.runtime,source=config["official_ipsae"],generated_inputs=[checksum(p)for p in paths],cutoff=argv[4])
   data=json.dumps(contract,sort_keys=True).encode();path.write_bytes(data);path.chmod(0o444)
   command=[argv[0],owned_entry["path"],"child-ipsae","--contract",str(path),"--contract-sha256",hashlib.sha256(data).hexdigest()]
   life=paths[0].parent/("strict_ipsae_IO_"+argv[4]+".json");life_tag=scope.output(life);scope.physical(life_tag,"write");scope.outputs.add(str(life))
   result=original_run(command,**kwargs)
   actual_life=scope.physical(life_tag,"read")if life.is_file()else None
   lifecycle=checksum(actual_life)if actual_life is not None and not(actual_life.stat().st_mode&0o222)else None
   if result.returncode==0:
    need(lifecycle is not None,"Actual child official OUTPUT lifecycle proof required")
    record=json.loads(scope.physical(life_tag,"read").read_bytes());need(record.get("schema")=="finite-official-IPSAE-output-lifecycle.v1"and record.get("status")=="EXACT_THREE_OFFICIAL_OUTPUT_WRITERS_CLOSED"and record.get("required_all_three")is True and record.get("cleanup_errors")==[]and record.get("original_official_source_changed")is False and {r["writer"]for r in record["writers"]}=={"OUT","PML","OUT2"}and len(record["writers"])==3 and all(r.get("status")in("FLUSHED_AND_CLOSED","ALREADY_CLOSED")for r in record["writers"]),"Actual child finite official writer closure failed")
   scope.processes.append(dict(kind="EXPLICIT_INDEXED_OFFICIAL_IPSAE_SOURCE_LOADER",indexed_source=str(ip.logical),fresh_output_inputs=list(map(str,paths)),child_contract=checksum(path),official_output_lifecycle=lifecycle,returncode=result.returncode));scope.after(touched_only=True);return result
  need(len(argv)==8 and argv[0]==scope.runtime["runtimes"]["msa"]["logical_executable"]and argv[1]=="-c"and argv[2]==MSA_CODE and argv[3]==str(msa.parent),"Exact indexed AF2 MSA subprocess contract required")
  inputs=[scope.input(p).physical()for p in argv[4:6]]
  need(all(re.fullmatch("[ACDEFGHIKLMNPQRSTVWY]+",s)for s in argv[6:]),"Exact protein query scalar args required")
  source=scope.verify(config["msa_roundtrip_source"]).physical();verify_runtime(scope.runtime["runtimes"]["msa"]);exact_file(owned_entry["path"],owned_entry)
  childdir=scope.out/"strict_subprocess_inputs";childdir.mkdir(exist_ok=True);path=childdir/("msa_"+str(len(scope.processes))+".json")
  contract=dict(schema="indexed-MSA-subprocess-contract.v1",package=scope.pkg,package_control=next(r for r in scope.controls.values()if r["path"]not in(str(scope.root/"RESTORE_HASH_ACCEPTANCE.json"),)),restore_root=str(scope.root),new_output_root=str(scope.out),aliases=dict(aliases=[dict(original=dict(path=k[0],bytes=k[1],sha256=k[2]),archived=scope.rows[v][0],status="READONLY_BYTE_IDENTICAL_ALIAS")for k,v in scope.aliases.items()]),owned_entry=owned_entry,runtime=scope.runtime,source=config["msa_roundtrip_source"],inputs=[scope.select(p.logical,p.sha)[0]for p in inputs],target=argv[6],binder=argv[7])
  data=json.dumps(contract,sort_keys=True).encode();path.write_bytes(data);path.chmod(0o444)
  command=[argv[0],owned_entry["path"],"child-msa","--contract",str(path),"--contract-sha256",hashlib.sha256(data).hexdigest()]
  result=original_run(command,**kwargs);scope.processes.append(dict(kind="EXPLICIT_INDEXED_MSA_SOURCE_LOADER",indexed_source=source.logical.as_posix(),indexed_inputs=[p.logical.as_posix()for p in inputs],child_contract=checksum(path),returncode=result.returncode));scope.after(touched_only=True);return result
 return run
@contextlib.contextmanager
def patched_core(api,scope,config,owned_entry):
 import restore_resolver_v2 as resolver
 import common_review_independent_v2 as common
 saved=[];budget_modules=[]
 def patch(module,name,value):
  saved.append((module,name,getattr(module,name)));setattr(module,name,value)
 def factory(authority,restore,aliases=None):
  need(Path(authority)==scope.authority and Path(restore)==scope.root,"Core resolver authority/root differs")
  return scope.input
 old_loader=resolver.load_budget_auditor
 def loader(r,authority,restore,aliases=None):
  need(Path(authority)==scope.authority and Path(restore)==scope.root,"Budget source loader authority/root differs")
  source=scope.verify(r).physical();module=types.ModuleType("independent_indexed_budget_auditor");module.__file__=os.fspath(source)
  # Compile the exact indexed source bytes; never import a directory or unindexed pycache.
  exec(compile(source.read_bytes(),module.__file__,"exec",dont_inherit=True),module.__dict__)
  budget_modules.append((module,module.Path,module.verify));module.Path=scope.input;module.verify=scope.verify;return module
 original_run=common.subprocess.run
 class Proxy:
  def __getattr__(self,name):return getattr(subprocess,name)
  run=staticmethod(isolated_subprocess(scope,config,owned_entry,original_run))
 try:
  patch(resolver,"path_factory",factory);patch(resolver,"load_budget_auditor",loader)
  patch(api,"path_factory",factory);patch(api,"Path",scope.structural);patch(api,"read",scope.read_json);patch(api,"rec",scope.rec);patch(api,"dump",scope.dump);patch(api,"verify",scope.verify)
  patch(common,"path_factory",factory);patch(common,"Path",scope.common_path);patch(common,"subprocess",Proxy())
  yield
 finally:
  for module,old_path,old_verify in reversed(budget_modules):module.Path=old_path;module.verify=old_verify
  for module,name,value in reversed(saved):setattr(module,name,value)
def run_indexed_core(api,pkg_receipt,pkg,root,out,aliases,owned,runtime,m):
 executing_sources=m.sources();need(executing_sources["composer"]==owned,"Actual owned executing source universe differs");marker=checksum(Path(root)/"RESTORE_HASH_ACCEPTANCE.json");scope=StrictIndex(pkg,root,out,aliases,controls=[pkg_receipt,marker],owned=owned,runtime=runtime)
 entry=next(r for r in owned if Path(r["path"]).name=="restored_index_scope.py")
 config=json.loads(scope.input(pkg["config"]["path"],expected_sha=pkg["config"]["sha256"]).read_text());need(config["recomputation"]["common"]["colabfold_cpu_python"]==runtime["actual_common_cpu_python"],"Actual restored common/runtime executable pointer differs")
 scope.after()
 with patched_core(api,scope,config["recomputation"]["common"],entry):result=api.run(pkg_receipt["path"],str(root),str(out))
 scope.after();need(m.sources()==executing_sources,"Whole executing owned/dependency/context source bytes changed during full restore");proof=m.dump(Path(out)/"strict_package_index_recomputation.json",dict(scope.proof(),executing_sources=executing_sources,whole_executing_source_pre_and_post_byte_readback_PASS=True));return result,proof
def seal_restored_metadata(pkg,root):
 # Root-authorized actual CPU metadata-only seal of a new extracted tree, never original authority.
 root=lexical(root);need(root.resolve()==root,"Readonly metadata seal restore root")
 changes=[]
 for row in pkg["manifest"]:
  p=root/row["relative"];r=receipt(row["receipt"]);exact_file(p,r,root,readonly=False);old=p.stat().st_mode&0o777;p.chmod(old&~0o222);changes.append(dict(logical_path=r["path"],previous_mode=old,new_mode=p.stat().st_mode&0o777));exact_file(p,r,root)
 marker=root/"RESTORE_HASH_ACCEPTANCE.json";need(marker.is_file()and marker.resolve()==marker and not marker.is_symlink(),"Exact extraction marker");marker.chmod(0o444)
 return dict(status="RESTORED_INDEX_INPUT_METADATA_READONLY_SEALED_BYTES_UNCHANGED",rows=changes)
def child_allocation_shape(f,jid):
 need(f.get("JobId")==jid and f.get("JobState")=="RUNNING"and f.get("NumCPUs")=="1"and f.get("UserId","").split("(")[0]=="u21111210118"and f.get("Account")=="u21111210118"and f.get("Partition")=="organ","Owned actual CPU1 child allocation required")
 values=[]
 for field in("AllocTRES","TRES"):
  tres=f.get(field)
  if not tres:continue
  vals={}
  for token in tres.split(","):
   need("="in token,"Malformed child TRES");k,v=token.split("=",1);need(k and v and k not in vals,"Duplicate/empty child TRES");vals[k]=v
  need(vals.get("cpu")=="1","Actual child CPU1 TRES")
  for k,v in vals.items():
   if k.startswith("gres/gpu"):need(v.isdecimal()and int(v)==0,"CPU child must allocate no GPU")
  values.append(vals)
 need(values and all(v==values[0]for v in values),"Child live AllocTRES/TRES missing or inconsistent");return values[0]
def child_cpu_guard():
 need(os.environ.get("SLURM_JOB_ID","").isdecimal()and os.environ.get("CUDA_VISIBLE_DEVICES")==""and os.environ.get("JAX_PLATFORMS")=="cpu"and os.environ.get("PYTHONNOUSERSITE")=="1"and os.environ.get("PYTHONDONTWRITEBYTECODE")=="1"and "PYTHONPATH"not in os.environ and os.environ.get("OPENBLAS_NUM_THREADS")=="1","Actual isolated Slurm CPU child required")
 raw=subprocess.check_output(["scontrol","show","job",os.environ["SLURM_JOB_ID"],"-o"],text=True);f=dict(re.findall(r"(\w+)=(\S+)",raw));child_allocation_shape(f,os.environ["SLURM_JOB_ID"])
def installed_runtime_imports_only():
 # Source-directory/cwd/pycache imports are not a scientific input exception.
 prefixes={Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve(),Path(sys.exec_prefix).resolve(),Path(sys.base_exec_prefix).resolve()}
 sys.path[:]=[p for p in sys.path if p and any(Path(p).resolve().is_relative_to(root)for root in prefixes)]
def child_contract(path,expected,schema):
 child_cpu_guard();path=lexical(path);need(path.is_file()and path.resolve()==path and not(path.stat().st_mode&0o222),"Immutable child input contract")
 data=path.read_bytes();need(hashlib.sha256(data).hexdigest()==expected,"Actual child contract bytes differ");q=json.loads(data);need(q.get("schema")==schema,"Exact child source loader schema")
 exact_file(Path(__file__).resolve(),q["owned_entry"]);exact_file(q["package_control"]["path"],q["package_control"]);need(json.loads(Path(q["package_control"]["path"]).read_bytes())==q["package"],"Child actual package-control manifest differs")
 scope=StrictIndex(q["package"],q["restore_root"],q["new_output_root"],q["aliases"],owned=[q["owned_entry"]],runtime=q["runtime"],allow_existing_output=True);return path,data,q,scope
def declare_official_output_paths(scope,model_pdb,cutoff):
 model=lexical(model_pdb);need(model.name=="model.pdb"and cutoff in("10","15")and model.is_relative_to(scope.out),"Fixed official fresh model/cutoff OUTPUT scope")
 prefix=model.parent/("model_"+cutoff+"_15")
 paths=dict(OUT=Path(str(prefix)+".txt"),PML=Path(str(prefix)+".pml"),OUT2=Path(str(prefix)+"_byres.txt"))
 for p in paths.values():
  scope.physical(scope.output(p),"write");need(not p.exists(),"Official OUTPUT must initially be absent");scope.outputs.add(str(p))
 return paths
def finalize_official_output_streams(namespace,scope,paths,required,trace):
 import io
 need(set(paths)=={"OUT","PML","OUT2"},"Only exact three official writer keys")
 table=lexical(paths["OUT"]);need(re.fullmatch(r"model_(10|15)_15\.txt",table.name)and table.is_relative_to(scope.out),"Exact official declared table path")
 stem=table.with_suffix("");need(paths==dict(OUT=table,PML=Path(str(stem)+".pml"),OUT2=Path(str(stem)+"_byres.txt"))and all(str(p)in scope.outputs for p in paths.values()),"Only predeclared fixed-name official OUTPUTs")
 errors=[];rows=[]
 for key,p in paths.items():
  handle=namespace.get(key);row=dict(writer=key,expected_output_path=str(p));rows.append(row)
  if handle is None:
   row["status"]="MISSING_AFTER_SOURCE_EXCEPTION"if not required else"MISSING_REQUIRED_OFFICIAL_WRITER"
   if required:errors.append(key+": missing required writer")
   continue
  try:
   need(isinstance(handle,io.TextIOBase)and isinstance(handle.name,str)and handle.mode=="w","Exact text write-mode official writer required")
   need(lexical(handle.name)==p,"Official writer does not match its declared OUTPUT")
   scope.physical(scope.output(p),"write");need(p.is_file()and p.resolve()==p and not p.is_symlink(),"Official writer OUTPUT is not regular/nonsymlink")
   row["closed_before"]=handle.closed
   if handle.closed:row["status"]="ALREADY_CLOSED";continue
   fd=os.fstat(handle.fileno());stat=p.stat();need((fd.st_dev,fd.st_ino)==(stat.st_dev,stat.st_ino),"Official writer descriptor/output identity mismatch")
  except Exception as e:
   row.update(status="INVALID_WRITER_SCOPE_TYPE_OR_IDENTITY",error_type=type(e).__name__,error=str(e));errors.append(key+": "+str(e));continue
  failures=[]
  try:handle.flush()
  except Exception as e:failures.append("flush: "+type(e).__name__+": "+str(e))
  finally:
   try:handle.close()
   except Exception as e:failures.append("close: "+type(e).__name__+": "+str(e))
  row["closed_after"]=handle.closed
  if failures or not handle.closed:
   row.update(status="OFFICIAL_WRITER_CLEANUP_FAILED",errors=failures);errors.extend(key+": "+x for x in failures)
   if not handle.closed:errors.append(key+": still open")
  else:row["status"]="FLUSHED_AND_CLOSED"
 trace.update(schema="finite-official-IPSAE-output-lifecycle.v1",status="EXACT_THREE_OFFICIAL_OUTPUT_WRITERS_CLOSED"if not errors and required else"CLEANUP_AFTER_SOURCE_EXCEPTION"if not errors else"OFFICIAL_OUTPUT_LIFECYCLE_REJECTED",required_all_three=required,writers=rows,cleanup_errors=errors,original_official_source_changed=False)
 if errors:raise ValueError("Official output lifecycle rejected: "+"; ".join(errors))
 return trace
def execute_indexed_official_source(source,scope,model_pdb,cutoff,namespace=None,trace=None):
 paths=declare_official_output_paths(scope,model_pdb,cutoff);namespace={}if namespace is None else namespace;trace={}if trace is None else trace
 namespace.setdefault("__name__","__main__");namespace.setdefault("__file__",os.fspath(source))
 primary=None;primary_tb=None;cleanup=None
 try:exec(compile(source.read_bytes(),os.fspath(source),"exec",dont_inherit=True),namespace)
 except BaseException as e:primary=e;primary_tb=e.__traceback__
 try:finalize_official_output_streams(namespace,scope,paths,primary is None,trace)
 except BaseException as e:cleanup=e
 if primary is not None:
  if cleanup is not None:
   # Preserve the actual original exception; cleanup errors are explicit metadata,
   # never a successful score or replacement exception.
   primary.strict_official_output_cleanup_errors=trace.get("cleanup_errors",[])
   if hasattr(primary,"add_note"):primary.add_note("Official output cleanup: "+str(cleanup))
  raise primary.with_traceback(primary_tb)
 if cleanup is not None:raise cleanup
 return trace
def write_official_output_lifecycle(scope,model_pdb,cutoff,lifecycle,primary=None):
 try:
  path=Path(model_pdb).parent/("strict_ipsae_IO_"+cutoff+".json");tag=scope.output(path);r=scope.dump(tag,lifecycle)
  actual=scope.physical(tag,"read");actual.chmod(actual.stat().st_mode&~0o222)
  need(checksum(actual)==r and not(actual.stat().st_mode&0o222),"Actual new official IO lifecycle metadata seal changed bytes")
  return r
 except BaseException as e:
  if primary is None:raise
  primary.strict_official_output_proof_write_error=dict(type=type(e).__name__,message=str(e))
  if hasattr(primary,"add_note"):primary.add_note("Official IO proof write: "+str(e))
  return None
def child_ipsae(contract_path,expected):
 path,data,q,scope=child_contract(contract_path,expected,"indexed-IPSAE-subprocess-contract.v1");verify_runtime(q["runtime"]["runtimes"]["core"])
 source=scope.verify(q["source"]);need(q["cutoff"]in("10","15"),"Fixed ipSAE cutoff")
 inputs=q["generated_inputs"];need(len(inputs)==2 and Path(inputs[0]["path"]).name=="scores.json"and Path(inputs[1]["path"]).name=="model.pdb"and Path(inputs[0]["path"]).parent==Path(inputs[1]["path"]).parent,"Fixed fresh IPSAE inputs")
 for r in inputs:exact_file(r["path"],r,scope.out,readonly=False)
 installed_runtime_imports_only();old=sys.argv;sys.argv=[os.fspath(source)]+[r["path"]for r in inputs]+[q["cutoff"],"15"];lifecycle={};primary=None;primary_tb=None
 try:execute_indexed_official_source(source,scope,inputs[1]["path"],q["cutoff"],trace=lifecycle)
 except BaseException as e:primary=e;primary_tb=e.__traceback__
 try:
  if lifecycle:write_official_output_lifecycle(scope,inputs[1]["path"],q["cutoff"],lifecycle,primary)
 finally:sys.argv=old
 if primary is not None:raise primary.with_traceback(primary_tb)
 for r in inputs:exact_file(r["path"],r,scope.out,readonly=False)
 scope.after(touched_only=True);need(path.read_bytes()==data,"IPSAE child input contract changed")
def child_msa(contract_path,expected):
 path,data,q,scope=child_contract(contract_path,expected,"indexed-MSA-subprocess-contract.v1")
 verify_runtime(q["runtime"]["runtimes"]["msa"]);source=scope.verify(q["source"]);inputs=[scope.verify(r)for r in q["inputs"]]
 installed_runtime_imports_only()
 namespace=dict(__name__="explicit_indexed_control_msa_check",__file__=os.fspath(source))
 exec(compile(source.read_bytes(),os.fspath(source),"exec",dont_inherit=True),namespace)
 namespace["Path"]=scope.input
 result=namespace["verify_roundtrip"](inputs[0],inputs[1],q["target"],q["binder"]);scope.after(touched_only=True);need(path.read_bytes()==data,"MSA child contract changed");print(json.dumps(result,sort_keys=True))
def main():
 p=argparse.ArgumentParser();p.add_argument("mode",choices=("child-msa","child-ipsae"));p.add_argument("--contract",required=True);p.add_argument("--contract-sha256",required=True);a=p.parse_args();(child_msa if a.mode=="child-msa"else child_ipsae)(a.contract,a.contract_sha256)
if __name__=="__main__":main()
