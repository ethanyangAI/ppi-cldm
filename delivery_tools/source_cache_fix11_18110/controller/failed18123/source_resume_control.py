#!/usr/bin/env python3
"""Resume preserved18095 Source closure; current StrictIndex only, never publisher replay."""
import os,sys,stat,re,json,hashlib,importlib.util,builtins,contextlib,io,subprocess
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/24_benchmark_delivery"
P=S/"pending/final_delivery_composer_v7_finite_source_context1_fix11_base_logical_cache"
CONTROLLER=S/"submissions/final_delivery_source_repair_18095_v1"
CODE_DEST="final_delivery_tools/source_cache_fix11_18110/code/"
CONTROL_DEST="final_delivery_tools/source_cache_fix11_18110/controller/"
MAX_CONTROL=20*1024*1024;MAX_OPERATIONAL=32*1024*1024;MAX_CLOSURE=100*1024*1024
META={"path","bytes","inode","mtime_ns","ctime_ns","mode","dev","nlink","uid","gid"}
RAW_OPEN=builtins.open;RAW_IO_OPEN=io.open;RAW_OS_OPEN=os.open
RAW_LSTAT=os.lstat;RAW_STAT=os.stat;RAW_READLINK=os.readlink;RAW_LISTDIR=os.listdir;RAW_SCANDIR=os.scandir
RAW_PATH_OPEN=Path.open;RAW_PATH_STAT=Path.stat;RAW_PATH_LSTAT=Path.lstat;RAW_PATH_RESOLVE=Path.resolve
RAW_PATH_READLINK=Path.readlink;RAW_ITERDIR=Path.iterdir

def need(v,message):
 if not v:raise ValueError(message)
def pairs(items):
 d={}
 for k,v in items:need(k not in d,"Duplicate JSON key");d[k]=v
 return d
def parse(raw):return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in()).throw(ValueError("Nonfinite JSON")))
def exact(a,b):return json.dumps(a,sort_keys=True,separators=(",",":"),allow_nan=False)==json.dumps(b,sort_keys=True,separators=(",",":"),allow_nan=False)
def lexical(p):
 text=os.fspath(p);need(type(text)is str and text.startswith("/")and all(x not in("",".","..")for x in text.split("/")[1:]),"Absolute lexical path required");return Path(text)
def md(p,fd=None):
 z=RAW_LSTAT(str(p))if fd is None else os.fstat(fd)
 return dict(path=str(p),bytes=z.st_size,inode=z.st_ino,mtime_ns=z.st_mtime_ns,ctime_ns=z.st_ctime_ns,mode=z.st_mode,dev=z.st_dev,nlink=z.st_nlink,uid=z.st_uid,gid=z.st_gid)
def shape(z):
 need(type(z)is dict and set(z)==META and all(type(z[k])is int for k in META-{"path"}),"Full Native10 required");lexical(z["path"]);return z
def rid(r):
 need(type(r)is dict and set(r)=={"path","bytes","sha256"}and type(r["bytes"])is int and r["bytes"]>=0 and re.fullmatch("[0-9a-f]{64}",r["sha256"]),"Whole receipt required");lexical(r["path"]);return(r["path"],r["bytes"],r["sha256"])
def fingerprint(r):rid(r);return(r["bytes"],r["sha256"])
def receipt(path,raw):return dict(path=str(path),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def regular(z,readonly=True):need(stat.S_ISREG(z["mode"])and z["nlink"]==1 and(not readonly or not(z["mode"]&0o222)),"Regular singlelink, readonly except exact Core executable")
KNOWN={};READS={};CREATED={};DIRS={};MODE_EVENTS=[]
def admit(z):
 shape(z);need(z["path"]not in KNOWN or KNOWN[z["path"]]==z,"No conflicting historical/current Native");KNOWN[z["path"]]=z

def read_raw(path,limit,expected=None,own_first_pin=False):
 p=lexical(path);need(p.is_relative_to(R),"Fixed authority containment")
 for parent in p.parents:
  if parent==R.parent:break
  need(stat.S_ISDIR(RAW_LSTAT(str(parent)).st_mode),"Nonsymlink ancestors required")
 before=md(p);original_common=("SPEC"in globals()and expected==SPEC["Common_original_metadata"]and str(p)==expected["path"])
 regular(before,p!=R/"env/core/bin/python3.11"and not original_common)
 if expected is not None:admit(expected);need(before==expected,"Authenticated Native before payload")
 elif str(p)in CREATED:need(before==CREATED[str(p)],"Created custody")
 else:need(own_first_pin and(p==Path(__file__)or p==REQUEST_PATH),"No implicit original Native enrollment");admit(before)
 need(before["bytes"]<=limit,"Declared byte bound")
 fd=RAW_OS_OPEN(str(p),os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,"rb")as stream:
  need(md(p,stream.fileno())==md(p)==before,"Full fd/path before read")
  raw=stream.read(limit+1)
  need(md(p,stream.fileno())==md(p)==before,"Full fd/path after read")
 need(len(raw)==before["bytes"],"Whole exact bytes");r=receipt(p,raw)
 need(str(p)not in READS or READS[str(p)][0]==r,"Input bytes never refresh")
 READS[str(p)]=(r,before);return r,raw

def read_receipt(r,limit=MAX_CONTROL):
 rid(r);z=KNOWN.get(r["path"],CREATED.get(r["path"]))
 need(z is not None,"Exact saved Native before any original payload")
 actual,raw=read_raw(r["path"],limit,z)
 need(actual==r,"CPU whole bytes differ from declared tuple");return raw

def control(entry,limit=MAX_CONTROL):
 need(type(entry)is dict and set(entry)in({"receipt","metadata"},{"metadata"}),"Closed genuine own-control input")
 z=entry["metadata"];admit(z);r,raw=read_raw(z["path"],limit,z)
 if "receipt"in entry:need(r==entry["receipt"],"Known CPU control tuple changed")
 return parse(raw),r

def mkdir(p):
 p=lexical(p);need(p.is_relative_to(OUT),"Only new resume output directories")
 if str(p)in DIRS:return p
 if p!=OUT:mkdir(p.parent)
 need(not p.exists(),"Exclusive new output directory")
 os.mkdir(p,0o700);DIRS[str(p)]=md(p);need(DIRS[str(p)]["nlink"]==2 and not RAW_LISTDIR(p),"Initial empty own directory")
 fd=RAW_OS_OPEN(str(p),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:need(md(p,fd)==md(p)==DIRS[str(p)],"New directory fd/path");os.fsync(fd)
 finally:os.close(fd)
 parentfd=RAW_OS_OPEN(str(p.parent),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(parentfd)
 finally:os.close(parentfd)
 return p

def durable(p,raw):
 p=lexical(p);need(p.is_relative_to(OUT),"Only new resume outputs")
 mkdir(p.parent);need(not p.exists(),"No output overwrite")
 parentfd=RAW_OS_OPEN(str(p.parent),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  fd=os.open(p.name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=parentfd)
  with os.fdopen(fd,"wb")as stream:
   empty=md(p,stream.fileno());need(empty==md(p)and empty["bytes"]==0 and empty["nlink"]==1,"Exclusive empty fd/path")
   stream.write(raw);stream.flush();os.fsync(stream.fileno());os.fchmod(stream.fileno(),0o444);os.fsync(stream.fileno())
   filled=md(p,stream.fileno());need(filled==md(p)and filled["bytes"]==len(raw),"Filled readonly fd/path")
  os.fsync(parentfd)
 finally:os.close(parentfd)
 CREATED[str(p)]=filled
 r,repeated=read_raw(p,max(len(raw),1),filled);need(repeated==raw,"Durable full readback");return r

def dump(p,obj,limit=MAX_CONTROL):
 raw=(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode();need(len(raw)<=limit,"Bound before exclusive write");return durable(p,raw)

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def cpu_guard():
 jid=os.environ.get("SLURM_JOB_ID","");need(jid.isdigit(),"Owned CPU allocation required")
 need(os.environ.get("CUDA_VISIBLE_DEVICES")==""and os.environ.get("JAX_PLATFORMS")=="cpu"and os.environ.get("PYTHONNOUSERSITE")=="1"and os.environ.get("PYTHONDONTWRITEBYTECODE")=="1"and "PYTHONPATH"not in os.environ,"CPU isolated environment")
 need(all(os.environ.get(k)=="1"for k in("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS")),"Single CPU thread environment")
 run=subprocess.run(["scontrol","show","job","-o",jid],capture_output=True,text=True,timeout=30)
 need(run.returncode==0 and run.stderr=="","Whole live allocation command")
 fields=dict(re.findall(r"(\w+)=(\S+)",run.stdout))
 need(fields.get("JobId")==jid and fields.get("JobState")=="RUNNING"and fields.get("NumCPUs")=="1"and fields.get("Account")=="u21111210118"and fields.get("Partition")=="organ"and fields.get("UserId","").split("(")[0]=="u21111210118","Owned running CPU1 allocation")
 resources=[]
 for name in("TRES","AllocTRES"):
  if name not in fields:continue
  row=dict(token.split("=",1)for token in fields[name].split(","));need(row.get("cpu")=="1","Exact allocated CPU1")
  need(all(v.isdigit()and int(v)==0 for k,v in row.items()if k.startswith("gres/gpu")),"No allocated GPU")
  resources.append(row)
 need(resources and all(v==resources[0]for v in resources),"Consistent allocated TRES")
 return dict(job_id=jid,allocated_CPUs=1,allocated_gpus=0,scheduler_record=run.stdout)

REQUEST_PATH=lexical(sys.argv[1]);ALLOCATION=cpu_guard();JID=ALLOCATION["job_id"]
self_r,self_raw=read_raw(Path(__file__),MAX_CONTROL,own_first_pin=True)
request_r,request_raw=read_raw(REQUEST_PATH,MAX_CONTROL,own_first_pin=True);q=parse(request_raw)
REQUEST_KEYS={"schema","software_acceptance","software_Root_control","software_evidence","input_metadata","publisher_SPEC","publisher_request","preserved_controls","existing_control_copies","operational_directories","software_controller_metadata","additional_executed_sources"}
need(type(q)is dict and set(q)==REQUEST_KEYS and q["schema"]=="root-preserved18095-fix11-resume-request.v1","Closed Root resume request")
for z in q["input_metadata"]:admit(z)
SPEC=q["publisher_SPEC"];need(SPEC["publication_namespace"]=="final_source_late_publication_v8_","Actual preserved P8 profile")
need(len(q["existing_control_copies"])==95,"Exactly preserved95 control transports")
for z in q["existing_control_copies"]:admit(z)
for z in q["software_controller_metadata"]:admit(z)
SW,sw_r=control(q["software_acceptance"]);CO,co_r=control(q["software_Root_control"])
need(SW["actual_CPU_job_id"]==CO["actual_job_id"]=="18110"and CO["actual_producer_acceptance"]==sw_r,"Actual fix11 software18110 pair")
need(SW["schema"]=="final-composer-software.v7"and SW["status"]=="FINAL_DELIVERY_COMPOSER_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_ARCHIVE_ACCEPTANCE","Actual software only")
SOURCE44=[r for rows in SW["source"].values()for r in rows]
need(len(SOURCE44)==44 and len({r["path"]for r in SOURCE44})==44,"Whole executing Source44")
need(CO["actual_frozen_source_groups"]==SW["source"]and CO["zero_failure_error_skip"]is True and CO["actual_test_count"]==237,"Root237 software control")
for r in SOURCE44:read_receipt(r,1024*1024)
for z in SPEC["conditional_core_metadata"]:
 shape(z);need(md(z["path"])==z,"Original Core Native unchanged")
common_z=SPEC["Common_original_metadata"];read_raw(common_z["path"],1024*1024,common_z)
core_z=next(z for z in SPEC["conditional_core_metadata"]if z["path"]==str(R/"env/core/bin/python3.11"))
core_r,core_raw=read_raw(core_z["path"],25916456,core_z)
need(core_r["bytes"]==25916456 and core_r["sha256"]=="76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a","Original Core whole bytes")
OWN=Path(SW["source"]["composer"][0]["path"]).parent
need([Path(r["path"]).name for r in SW["source"]["composer"]]==["final_delivery_composer.py","test_final_delivery_composer.py","composer_bootstrap.py","composer_cpu.sbatch","composer_contracts_cpu.sbatch","HANDOFF.md","composer_context_api.py","relative_archive_restore.py","github_export_context.py","test_github_export_context.py","restored_index_scope.py","test_restored_index_scope.py","finite_source_delivery_context.py","test_finite_source_delivery_context.py","qualified_source_semantics.py"],"Qualified whole OWN15")
m=load("resume_fix11_qualified_composer",OWN/"final_delivery_composer.py")
need(m.sources()==SW["source"],"Exact executing qualified Source44");m.cpu()
helper=m.finite_source_api();api=m.restore_index_api()
need(helper.PARTIAL_CACHE_ORIGINAL_SOURCE_P==P and helper.PARTIAL_CACHE_REQUIRED_SOFTWARE_TESTS==m.SOFTWARE_TESTS==237,"Distinct qualified fix11 helper")
CT=parse(read_receipt(SW["contracts"]));need(CT["status"]=="PASS"and CT["tests_run"]==237 and CT["errors"]==CT["failures"]==0 and CT["tested_source"]==SW["source"],"Real existing237 contracts; never rerun")
OUT=S/"runs"/("final_source_resume_fix11_"+JID);mkdir(OUT)

try:

 REQUEST,request_original_r=control(q["publisher_request"])
 need(type(REQUEST)is dict and len(REQUEST)==13 and REQUEST["schema"]=="root-finite-late-source-publisher-primary-request.v1","Whole original R13 required")
 need(len(REQUEST["source_candidates"])==817 and len(REQUEST["i_source_route_choices"])==2002,"Original P8 request817 and I2002 routes")
 PRES=q["preserved_controls"];need(set(PRES)=={"I","manifest","operational","installation"},"Fixed four preserved controls")
 I,i_r=control(PRES["I"]);old_late,old_late_r=control(PRES["manifest"])
 OP,op_r=control(PRES["operational"],MAX_OPERATIONAL);INSTALL,installation_r=control(PRES["installation"])
 producer=SPEC["producer_receipts"];need(producer["source_inclusion"]==i_r and old_late["source_inclusion"]==OP["source_inclusion"]==INSTALL["source_inclusion"]==i_r,"Same immutable I")
 need(len(I["files"])==1429 and len(old_late["files"])==825 and len(OP["cache_history"]["members"])==13060,"Preserved18095 finite denominators")
 need(OP["allocation"]["job_id"]==INSTALL["allocation"]["job_id"]=="18095"and OP["stage_acceptance"]==INSTALL["stage_acceptance"]==old_late["stage_acceptance"]==SPEC["stage_acceptance_receipt"],"Failed18095 recorded history is not new success")
 need(INSTALL["status"]=="ALL_EXPLICIT_I_AND_LATE_DESTINATIONS_FULL_BYTES_READ_BACK_NOT_GIT_STAGED"and INSTALL["existing_targets_overwritten"]is False and INSTALL["installed_permissions_changed"]is False,"Original installation preserved")
 # Old controls and copies stay immutable. Only these three owned OP directories may change mode.
 OPROOT=S/"submissions/root_operational_source_provenance_from17809_18095"
 expected_op_names={str(OPROOT):["operational_evidence","operational_shell_sources","operational_source_provenance.json"],
  str(OPROOT/"operational_evidence"):sorted(x["evidence_copy"]["path"].split("/")[-1]for x in OP["new_four"]+OP["legacy_two"]["entries"]+OP["cache_history"]["members"]),
  str(OPROOT/"operational_shell_sources"):sorted(Path(x["eligible_source"]["path"]).name for x in OP["new_four"])}
 need(type(q["operational_directories"])is list and len(q["operational_directories"])==3 and {z["path"]for z in q["operational_directories"]}==set(expected_op_names),"Only exact owned OP3 mode targets")
 for z in sorted(q["operational_directories"],key=lambda x:len(Path(x["path"]).parts),reverse=True):
  shape(z);p=Path(z["path"]);need(md(p)==z and stat.S_ISDIR(z["mode"])and stat.S_IMODE(z["mode"])==0o775,"Actual preserved OP775 before seal")
  need(sorted(RAW_LISTDIR(p))==expected_op_names[str(p)],"Exact derived OP directory names")
  fd=RAW_OS_OPEN(str(p),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:
   need(md(p,fd)==md(p)==z,"Owned OP fd/path before mode event")
   os.fchmod(fd,0o555);os.fsync(fd);after=md(p,fd)
   need(after==md(p)and all(after[k]==z[k]for k in META-{"mode","ctime_ns"})and stat.S_IMODE(after["mode"])==0o555,"Only OP mode and ctime change")
  finally:os.close(fd)
  MODE_EVENTS.append(dict(path=str(p),before=z,after=after,names=expected_op_names[str(p)]))
 # Every installed old target keeps its saved full Native and its exact original CPU tuple.
 installed_md={z["path"]:z for z in INSTALL["all_target_metadata_after"]}
 installed_r={r["path"]:r for r in INSTALL["all_target_CPU_receipts"]}
 need(len(installed_md)==len(installed_r)==2254 and set(installed_md)==set(installed_r),"Preserved2254 target custody")
 old_rows=list(I["files"])+[dict(original_source=x["logical_receipt"],source=x["physical_receipt"],repository_relative=x["repository_relative"],kind=x["kind"],roles=x["roles"],logical_receipts=x.get("logical_receipts",[]))for x in old_late["files"]]
 expected_targets={str(R/"source"/x["repository_relative"]):dict(x["source"],path=str(R/"source"/x["repository_relative"]))for x in old_rows}
 need(expected_targets==installed_r,"All exact I+old825 installed CPU tuples")
 for p,z in installed_md.items():
  shape(z);need(md(p)==z,"Preserved installed full Native unchanged")
  fd=RAW_OS_OPEN(p,os.O_RDONLY|os.O_NOFOLLOW)
  with os.fdopen(fd,"rb")as stream:
   need(md(p,stream.fileno())==md(p)==z,"Installed fd/path before bytes")
   h=hashlib.sha256();size=0
   for chunk in iter(lambda:stream.read(1048576),b""):size+=len(chunk);h.update(chunk)
   need(md(p,stream.fileno())==md(p)==z,"Installed fd/path after bytes")
  need((size,h.hexdigest())==fingerprint(installed_r[p]),"Preserved installed whole bytes")
 # The actual new software's Source15 pairs and the three actual Root controller sources become new late rows.
 source_delta=[]
 for original,physical in zip(CO["actual_source_groups_original"]["composer"],SW["source"]["composer"]):
  need(Path(original["path"]).parent==P and Path(original["path"]).name==Path(physical["path"]).name and fingerprint(original)==fingerprint(physical),"New actual original/frozen OWN15 pairs")
  source_delta.append((original,physical,CODE_DEST+Path(original["path"]).name))
 controller_names=("software_control.py","software_cpu.sbatch","request.json")
 need(len(q["software_controller_metadata"])==3 and {z["path"]for z in q["software_controller_metadata"]}=={str(CONTROLLER/n)for n in controller_names},"Exact actual software controller3")
 for name in controller_names:
  z=next(z for z in q["software_controller_metadata"]if z["path"]==str(CONTROLLER/name));r,raw=read_raw(z["path"],MAX_CONTROL,z)
  source_delta.append((r,r,CONTROL_DEST+name))
 source_delta.append((self_r,self_r,CONTROL_DEST+"resume_controller.py"))
 need(type(q["additional_executed_sources"])is list and 1<=len(q["additional_executed_sources"])<=9,"Explicit finite launcher/privateGit/final-assembler Source rows")
 for entry in q["additional_executed_sources"]:
  need(type(entry)is dict and set(entry)in({"metadata","repository_relative"},{"receipt","metadata","repository_relative"}),"Closed actual extra executed Source")
  need(entry["repository_relative"].startswith(CONTROL_DEST)and ".."not in Path(entry["repository_relative"]).parts,"Only explicit repair controller public destinations")
  need(Path(entry["metadata"]["path"]).parent==Path(__file__).parent or (Path(entry["metadata"]["path"]).parent==S/"submissions/final_delivery_complete_from18110_v1"and entry["repository_relative"].startswith(CONTROL_DEST+"failed18116/")),"Current execution or exact preserved failed18116 Source directory")
  actual,raw=read_raw(entry["metadata"]["path"],MAX_CONTROL,entry["metadata"])
  if "receipt"in entry:need(actual==entry["receipt"],"Known additional code full tuple")
  source_delta.append((actual,actual,entry["repository_relative"]))
 NEW_SOURCE_N=len(source_delta)
 need(len({dest for a,b,dest in source_delta})==NEW_SOURCE_N and len({rid(a)for a,b,dest in source_delta})==NEW_SOURCE_N,"Distinct actual repair Source identities/destinations; no own output result")
 semantic_receipt=SW["source"]["composer"][14];g=helper._load_semantics_bytes(read_receipt(semantic_receipt),semantic_receipt)
 new_rows=[]
 for n,(original,physical,dest)in enumerate(source_delta):
  need(dest not in {x["repository_relative"]for x in old_rows},"No old Source destination replacement")
  raw=self_raw if physical==self_r else request_raw if physical==request_r else read_receipt(physical)
  copied=durable(OUT/"source_bytes"/("%02d"%n)/Path(physical["path"]).name,raw)
  need(fingerprint(copied)==fingerprint(original),"Real Source bytecopy")
  new_rows.append(dict(logical_receipt=original,physical_receipt=copied,repository_relative=dest,kind=g.kind(original["path"]),roles=["final_delivery_tools"]))
 late=dict(old_late,files=list(old_late["files"])+new_rows)
 helper.late_publication_shape(late,i_r,SPEC["stage_acceptance_receipt"],g)
 late_r=dump(OUT/"late_source_manifest_fix11.json",late)
 rows=list(old_rows)+[dict(original_source=x["logical_receipt"],source=x["physical_receipt"],repository_relative=x["repository_relative"],kind=x["kind"],roles=x["roles"],logical_receipts=x.get("logical_receipts",[]))for x in new_rows]
 identities=helper.identity_multimap(rows)[0];routes={}
 for choice in REQUEST["i_source_route_choices"]:
  k=rid(choice["original"]);need(k not in routes,"Original I route unique");routes[k]=dict(choice)
 selected_destinations={d["literal_path"]:d["selected_destination"]for d in REQUEST["source_candidates"]}
 selected_destinations.update({a["path"]:dest for a,b,dest in source_delta})
 for k,candidates in identities.items():
  if k in routes:continue
  choices={(rid(helper.subset(x["source"])),x["repository_relative"])for x in candidates}
  if k[0]in selected_destinations:choices={item for item in choices if item[1]==selected_destinations[k[0]]}
  need(len(choices)==1,"Full Source tuple has no unique explicitly declared physical/destination route")
  physical_key,dest=next(iter(choices));routes[k]=dict(original=dict(path=k[0],bytes=k[1],sha256=k[2]),selected_physical=dict(path=physical_key[0],bytes=physical_key[1],sha256=physical_key[2]),repository_relative=dest)
 helper._source_route_table(rows,list(routes.values()))
 # Reconstruct the ORIGINAL ordered transport loop; every old copied file is reused and byte-validated.
 A=parse(read_receipt(producer["acceptance"]));proofs=[parse(read_receipt(A[p]))for p,k in helper.PAIRS]
 required={}
 def require(r):rid(r);required.setdefault(rid(r),r)
 for r in producer.values():require(r)
 for r in helper._proof_receipts(A):require(r)
 for r in list(g._catalog_msa_controls())+[g._WORKER_BASE,g._WORKER_CLOSURE]+[r for p in proofs[2:]for r in p["authority_receipts"]]:require(r)
 bridge=old_late["source_text_provenance_bridges"][0]
 for r in REQUEST["source_control_receipts"]+[SPEC["stage_acceptance_receipt"],old_late_r,bridge["byte_identity_proof"],op_r,OP["stage_terminal_metadata"],OP["legacy_capture"]]:require(r)
 oldSW=SPEC["successor_software"];oldA=parse(read_receipt(oldSW["software_acceptance"]))
 partial_pin=helper._partial_cache_authority_record(OP)["control_receipt"]
 for r in [oldSW["software_acceptance"],oldSW["Root_execution_control"],oldA["contracts"],partial_pin]:require(r)
 semantic_targets=dict(required)
 derived=helper._derived_receipts(A,I,proofs,g)
 i_physical={rid(helper.subset(x["source"])):helper.subset(x["source"])for x in I["files"]}
 for r in derived+list(i_physical.values())+[x["physical_receipt"]for x in old_late["files"]]+[x["evidence_copy"]for x in OP["cache_history"]["members"]+OP["new_four"]+OP["legacy_two"]["entries"]]+[x["eligible_source"]for x in OP["legacy_two"]["entries"]]+[bridge["eligible_copy"],SPEC["source44_receipts"][14]]:semantic_targets[rid(r)]=r
 old_json_sources={rid(x["source"])for x in old_rows};transport_rows=[]
 OLDPUB=S/"runs/final_source_late_publication_v8_18095";old_copies={z["path"]:z for z in q["existing_control_copies"]}
 for key,r in semantic_targets.items():
  if key in required or Path(r["path"]).suffix==".json"and key in old_json_sources:
   path=OLDPUB/"control_bytes"/("%05d_%s.OPAQUE.txt"%(len(transport_rows),Path(r["path"]).stem))
   need(str(path)in old_copies,"Exact preserved original transport filename/ordinal")
   archived,raw=read_raw(path,MAX_CLOSURE if r==producer["source_closure"]else MAX_OPERATIONAL if r==op_r else MAX_CONTROL,old_copies[str(path)])
   need(fingerprint(archived)==fingerprint(r),"Preserved transport whole bytes exactly match original receipt")
   transport_rows.append(dict(original=r,archived=archived,status="READONLY_BYTE_IDENTICAL_ALIAS",role="FINITE_SOURCE_CONTROL_BYTES"if key in required else"FINITE_SOURCE_JSON_BYTES"))
 prior_path=OLDPUB/"control_bytes/prior_failed18082_installation.OPAQUE.txt"
 need(len(transport_rows)==94 and str(prior_path)in old_copies,"Original94 plus fixed prior-installation TXT")
 prior_original_path=str(S/"submissions/root_final_source_late_publication_v7_execution_control_18082/installation_readback.json")
 prior_md=KNOWN.get(prior_original_path);need(prior_md is not None,"Preserved original18082 installation Native")
 prior_r,prior_raw=read_raw(prior_original_path,4*1024*1024,prior_md)
 prior_copy,copied_raw=read_raw(prior_path,4*1024*1024,old_copies[str(prior_path)])
 need(copied_raw==prior_raw,"Original whole prior-installation archive copy byte equality")
 transport_rows.append(dict(original=prior_r,archived=prior_copy,status="READONLY_BYTE_IDENTICAL_ALIAS",role="FINITE_SOURCE_CONTROL_BYTES"))
 # New control aliases are the only new metadata copies; never rewrite/re-copy old13060 evidence.
 new_controls=[sw_r,co_r,SW["contracts"],late_r,request_r]
 need(type(q["software_evidence"])is list and len(q["software_evidence"])==2,"Actual named237 log and actual terminal control")
 terminal_path=str(S/"submissions/final_delivery_source_repair18110_terminal/receipt.json")
 need({entry["metadata"]["path"]for entry in q["software_evidence"]}=={CO["actual_contract_log"]["path"],terminal_path},"Only exact known237 log and fixed18110 terminal")
 for entry in q["software_evidence"]:
  if entry["metadata"]["path"]==terminal_path:
   terminal_obj,r=control(entry)
   need(terminal_obj["actual_job_id"]=="18110"and terminal_obj["rc"]==0 and terminal_obj["tests_run"]==237 and terminal_obj["errors"]==terminal_obj["failures"]==terminal_obj["skips"]==0,"Actual completed18110 terminal whole control")
  else:
   need(type(entry)is dict and set(entry)=={"receipt","metadata"}and entry["receipt"]==CO["actual_contract_log"],"Known actual full237 named log tuple/Native")
   r,raw=read_raw(entry["metadata"]["path"],MAX_CONTROL,entry["metadata"]);need(r==entry["receipt"],"Actual named237 log whole bytes")
  new_controls.append(r)
 new_transports=[]
 for r in new_controls+[x["physical_receipt"]for x in new_rows if Path(x["physical_receipt"]["path"]).suffix==".json"]:
  if rid(r)in {rid(x["original"])for x in transport_rows+new_transports}:continue
  raw=read_receipt(r)if r["path"]not in CREATED else read_raw(r["path"],MAX_CONTROL,CREATED[r["path"]])[1]
  alias=durable(OUT/"control_bytes"/("%03d_%s.OPAQUE.txt"%(len(new_transports),Path(r["path"]).stem)),raw)
  new_transports.append(dict(original=r,archived=alias,status="READONLY_BYTE_IDENTICAL_ALIAS",role="FINITE_SOURCE_CONTROL_BYTES"if r in new_controls else"FINITE_SOURCE_JSON_BYTES"))
 binding=dict(schema=helper.SCHEMA,root_owned=True,producer=producer,semantics_source=semantic_receipt,stage_acceptance=SPEC["stage_acceptance_receipt"],late_source_publication=late_r,transport_aliases=transport_rows+new_transports,additional_control_receipts=REQUEST["source_control_receipts"][19:],source_routes=list(routes.values()),operational_source_provenance=op_r,partial_cache_software_authority=dict(software_acceptance=sw_r,Root_execution_control=co_r))
 helper._binding_shape(binding)
 current=helper.load_current(binding);projection=current.projection
 need(projection.i==I and len(projection.source_rows)==1429+825+NEW_SOURCE_N,"Original I and old825 preserved plus exact declared Source delta")
 expected_proof=projection.proof();binding_r=dump(OUT/"source_context_binding.json",binding)

 # The exact V3 physical/alias planner is reused; CURRENT_ROOT is never called an isolated restore.
 transports=helper._binding_shape(binding);partial_software=projection.partial_cache_software
 plan_receipts={rid(r):r for r in projection.terminal_source_receipts()+projection.semantic_control_receipts()}
 for row in binding["transport_aliases"]:plan_receipts[rid(row["archived"])]=row["archived"]
 source_keys={rid(r)for r in projection.terminal_source_receipts()};evidence_keys={rid(r)for r in projection.operational["evidence"]}
 alias_targets={}
 for row in projection.selected_source_aliases()+projection.aliases():
  projection.check_source_text_alias(row)
  chosen=row if projection.operational_alias(row)else projection.project_source_alias(row)or row
  target=chosen["archived"]if projection.operational_alias(row)else projection._transport_target(chosen["archived"])
  key=rid(chosen["original"]);value=rid(target)
  need(value in plan_receipts and(key not in alias_targets or alias_targets[key]==value),"Full exact alias/physical closure");alias_targets[key]=value
 aliases=[dict(original=dict(path=k[0],bytes=k[1],sha256=k[2]),archived=plan_receipts[target],status="READONLY_BYTE_IDENTICAL_ALIAS")for k,target in sorted(alias_targets.items())]
 for key,target in alias_targets.items():
  if key in plan_receipts and key!=target:
   need(key not in source_keys and key not in evidence_keys,"Physical Source/evidence retains self route");del plan_receipts[key]
 for target in alias_targets.values():need(target in plan_receipts,"Onehop physical target retained")
 manifest=[dict(receipt=r,relative=Path(r["path"]).relative_to(R).as_posix(),role="OPERATIONAL_EVIDENCE"if k in evidence_keys else"SOURCE"if k in source_keys else"SEMANTIC_CONTROL")for k,r in sorted(plan_receipts.items())]
 need(len({x["receipt"]["path"]for x in manifest})==len(manifest),"Distinct actual physical entries")
 # This status is required by the unchanged StrictIndex constructor; the fixture flags prohibit delivery claims.
 pkg=dict(schema="benchmark-delivery-package.v1",status="PACKAGED_AWAITING_INDEPENDENT_RESTORE",authority_root=str(R),manifest=manifest,
  current_index_interface_fixture_only=True,archive_created=False,isolated_root=False,production_package_accepted=False,scientific_restore_accepted=False)
 alias_obj=dict(aliases=aliases);pkg_r=dump(OUT/"current_index_interface_manifest.json",pkg);alias_r=dump(OUT/"current_index_aliases.json",alias_obj)
 ROOT=R;index_out=OUT/"current_index_output";traps=[];expected_traps=[];cases=[]
 source_exec={r["path"]for r in SOURCE44};physical_paths={r["path"]for r in plan_receipts.values()};ancestors=set()
 for p in [ROOT,OUT,index_out]+[Path(x)for x in source_exec|physical_paths]:ancestors.update(str(x)for x in p.parents)

 poison_fds=set()
 def permitted(p,operation,writing=False):
  if isinstance(p,int):return p in poison_fds
  path=lexical(p);s=str(path)
  if writing:return path.is_relative_to(OUT)
  if s in physical_paths or s in source_exec:return True
  if operation in("stat","lstat","resolve","readlink")and(s in ancestors or path.is_relative_to(OUT)):return True
  return False
 def deny(p,operation,writing=False):
  if not permitted(p,operation,writing):
   traps.append(dict(path=str(p),operation=operation));raise AssertionError("Original filesystem denied in SOURCE-only INDEX: "+str(p))
 @contextlib.contextmanager
 def poison():
  saved=[]
  def patch(obj,name,value):
   saved.append((obj,name,getattr(obj,name)));setattr(obj,name,value)
  def po(p,*a,**k):
   mode=a[0]if a else k.get("mode","r");deny(p,"open",any(x in mode for x in("w","a","x","+")));return RAW_PATH_OPEN(p,*a,**k)
  def bo(p,*a,**k):
   mode=a[0]if a else k.get("mode","r");deny(p,"open",any(x in mode for x in("w","a","x","+")));return RAW_OPEN(p,*a,**k)
  def io_open(p,*a,**k):
   mode=a[0]if a else k.get("mode","r");deny(p,"io.open",any(x in mode for x in("w","a","x","+")));return RAW_IO_OPEN(p,*a,**k)
  def oo(p,flags,*a,**k):
   deny(p,"os.open",bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
   fd=RAW_OS_OPEN(p,flags,*a,**k);poison_fds.add(fd);return fd
  def list_directory(p="."):deny(p,"os.listdir");return RAW_LISTDIR(p)
  def scan_directory(p="."):deny(p,"os.scandir");return RAW_SCANDIR(p)
  def iterate_directory(p):deny(p,"Path.iterdir");return RAW_ITERDIR(p)
  def st(p,*a,**k):deny(p,"stat");return RAW_STAT(p,*a,**k)
  def ls(p,*a,**k):deny(p,"lstat");return RAW_LSTAT(p,*a,**k)
  def rl(p,*a,**k):deny(p,"readlink");return RAW_READLINK(p,*a,**k)
  def pst(p,*a,**k):deny(p,"stat");return RAW_PATH_STAT(p,*a,**k)
  def pls(p,*a,**k):deny(p,"lstat");return RAW_PATH_LSTAT(p,*a,**k)
  def prs(p,*a,**k):deny(p,"resolve");return RAW_PATH_RESOLVE(p,*a,**k)
  def prl(p,*a,**k):deny(p,"readlink");return RAW_PATH_READLINK(p,*a,**k)
  try:
   for obj,name,value in[(builtins,"open",bo),(io,"open",io_open),(os,"open",oo),(os,"listdir",list_directory),
    (os,"scandir",scan_directory),(os,"stat",st),(os,"lstat",ls),(os,"readlink",rl),(Path,"iterdir",iterate_directory),
    (Path,"open",po),(Path,"stat",pst),(Path,"lstat",pls),(Path,"resolve",prs),(Path,"readlink",prl)]:patch(obj,name,value)
   yield
  finally:
   for obj,name,value in reversed(saved):setattr(obj,name,value)

 with poison():
  index=api.StrictIndex(pkg,ROOT,index_out,alias_obj)
  replay,baseline=helper.indexed_payloads(binding,pkg,index)
  need(exact(replay.proof(),expected_proof),"Full current/real-INDEX projection equality")
  need(not traps,"Positive current INDEX used an unindexed/original fallback")
  for path,z in baseline.items():
   expected=current.inputs.original.get(path,CREATED.get(path));need(expected==z,"First INDEX Native equals prior current/creation custody")
  projection=replay
  def selected_physical(r):
   key=rid(r);target=index.aliases.get(key,key)
   need(target in index.rows,"Authenticated complete real INDEX physical target")
   return index.rows[target][0]
  def omitted(label,r):
   target=rid(selected_physical(r))
   reduced=dict(pkg,manifest=[row for row in pkg["manifest"]if rid(row["receipt"])!=target])
   reduced_aliases=dict(aliases=[e for e in aliases if rid(e["archived"])!=target])
   neg=api.StrictIndex(reduced,ROOT,OUT/("negative_"+label),reduced_aliases)
   before=len(traps)
   try:helper._indexed_source_bytes(reduced,neg,r,transports,{})
   except ValueError as e:cases.append(dict(case=label,status="EXPECTED_VALUEERROR",required_receipt=r,physical_target=index.rows[target][0],error=str(e)))
   else:raise ValueError("Real INDEX omission was accepted: "+label)
   need(len(traps)==before,"Omission denial attempted original fallback")
  alternatives=[]
  for key,candidate_rows in sorted(projection.identities.items()):
   if key in projection.source_copies:continue
   candidate_physical={rid(projection._transport_target(row["source"])):projection._transport_target(row["source"])for row in candidate_rows}
   chosen=projection._transport_target(projection.source_physical[key])
   for candidate in candidate_physical.values():
    if rid(candidate)!=rid(chosen):
     alternatives.append((dict(path=key[0],bytes=key[1],sha256=key[2]),chosen,candidate))
  need(alternatives,"Actual full logical Source identity must have a genuinely unselected declared copy")
  selected_original,selected_copy,unselected_copy=alternatives[0]
  omitted("unselected_declared_Source_copy",unselected_copy)
  known_cache=[];unknown_cache=[]
  for original,copy,field in projection.operational["caches"]:
   route=projection.operational_routes[rid(original)]
   (unknown_cache if route["role"]=="INDEPENDENT_CACHE_EVIDENCE"else known_cache).append(copy)
  need(known_cache and unknown_cache,"Both admitted and non-Source cache evidence classes are required")
  omitted("known_Source_cache_independent_EVIDENCE",known_cache[0])
  omitted("unknown_cache_independent_EVIDENCE",unknown_cache[0])
  omitted("new_four_eligible_shell_Source",OP["new_four"][0]["eligible_source"])
  omitted("legacy_two_existing_shell_Source",OP["legacy_two"]["entries"][0]["eligible_source"])
  omitted("new_four_independent_raw_OPAQUE",OP["new_four"][0]["evidence_copy"])
  omitted("legacy_two_independent_raw_OPAQUE",OP["legacy_two"]["entries"][0]["evidence_copy"])
  bridge_inputs=helper._late_bridge_receipts(late)
  omitted("sole_bridge_eligible_python_Source",bridge_inputs[1])
  omitted("sole_bridge_byte_identity_proof",bridge_inputs[0])
  required_controls=set(projection.control_receipts)
  control_transports=[row for row in binding["transport_aliases"]if rid(row["original"])in required_controls]
  need(control_transports,"Actual authenticated control transport is required")
  omitted("declared_semantic_JSON_OPAQUE_transport",control_transports[0]["original"])
  for label,r in [("actual237_software_acceptance",sw_r),
   ("actual237_Root_execution_control",co_r),
   ("actual237_derived_contracts",SW["contracts"]),
   ("fixed_prior_failed17837_name_authority",partial_software["control_receipt"])]:
   need(rid(r)in required_controls,"Whole current authority control must be a mandatory semantic CONTROL_BYTES row")
   omitted(label,r)
  wrong_source_aliases=[dict(e)for e in aliases];found=0
  for e in wrong_source_aliases:
   if rid(e["original"])==rid(selected_original):e["archived"]=unselected_copy;found+=1
  need(found==1 and fingerprint(selected_copy)==fingerprint(unselected_copy),"Exact conditional same-FP Source alias negative")
  wrong_source=api.StrictIndex(pkg,ROOT,OUT/"negative_wrong_selected_Source_alias",dict(aliases=wrong_source_aliases))
  before=len(traps)
  try:helper.indexed_payloads(binding,pkg,wrong_source)
  except ValueError as e:cases.append(dict(case="selected_Source_alias_redirected_to_other_declared_copy",status="EXPECTED_VALUEERROR",original=selected_original,selected=selected_copy,wrong=unselected_copy,error=str(e)))
  else:raise ValueError("Wrong selected Source alias was accepted")
  need(len(traps)==before,"Selected Source alias denial attempted original fallback")
  raw_receipt=OP["new_four"][0]["original_text"]
  bad=dict(pkg,manifest=list(pkg["manifest"])+[dict(receipt=raw_receipt,relative=Path(raw_receipt["path"]).relative_to(R).as_posix(),role="INVALID_RAW_ORIGINAL")])
  bad_aliases=dict(aliases=[e for e in aliases if rid(e["original"])!=rid(raw_receipt)])
  bad_index=api.StrictIndex(bad,ROOT,OUT/"negative_raw_original",bad_aliases)
  before=len(traps)
  try:helper.indexed_payloads(binding,bad,bad_index)
  except ValueError as e:cases.append(dict(case="raw_original_INDEX_row",status="EXPECTED_VALUEERROR",error=str(e)))
  else:raise ValueError("Raw documentary original INDEX row was accepted")
  need(len(traps)==before,"Raw original was read before denial")
  wrong_aliases=[dict(e)for e in aliases];raw_key=rid(raw_receipt);found=0
  for e in wrong_aliases:
   if rid(e["original"])==raw_key:e["archived"]=selected_physical(OP["new_four"][0]["eligible_source"]);found+=1
  need(found==1,"Actual exact raw-evidence alias is required")
  wrong=api.StrictIndex(pkg,ROOT,OUT/"negative_wrong_raw_alias",dict(aliases=wrong_aliases))
  before=len(traps)
  try:helper.operational_index_alias_shape(projection,wrong)
  except ValueError as e:cases.append(dict(case="raw_opaque_alias_redirected_to_same_FP_shell_Source",status="EXPECTED_VALUEERROR",error=str(e)))
  else:raise ValueError("Wrong operational raw alias was accepted")
  need(len(traps)==before,"Raw alias denial attempted original IO")
  text_receipt=projection.source_bridge["original_text"]
  text_bad=dict(pkg,manifest=list(pkg["manifest"])+[dict(receipt=text_receipt,relative=Path(text_receipt["path"]).relative_to(R).as_posix(),role="INVALID_64944_ORIGINAL_TXT")])
  text_index=api.StrictIndex(text_bad,ROOT,OUT/"negative_64944_original_row",alias_obj)
  before=len(traps)
  try:helper.indexed_payloads(binding,text_bad,text_index)
  except ValueError as e:cases.append(dict(case="64944_original_TXT_INDEX_row",status="EXPECTED_VALUEERROR",error=str(e)))
  else:raise ValueError("64944 original TXT INDEX row was accepted")
  need(len(traps)==before,"64944 row denial attempted original IO")
  text_aliases=list(aliases)+[dict(original=text_receipt,archived=selected_physical(bridge_inputs[1]),status="READONLY_BYTE_IDENTICAL_ALIAS")]
  text_alias_index=api.StrictIndex(pkg,ROOT,OUT/"negative_64944_original_alias",dict(aliases=text_aliases))
  before=len(traps)
  try:helper.indexed_payloads(binding,pkg,text_alias_index)
  except ValueError as e:cases.append(dict(case="64944_original_TXT_INDEX_alias",status="EXPECTED_VALUEERROR",error=str(e)))
  else:raise ValueError("64944 original TXT alias was accepted")
  need(len(traps)==before,"64944 alias denial attempted original IO")
  for original in [OP["new_four"][0]["original_text"],projection.source_bridge["original_text"]]:
   p=Path(original["path"])
   for operation in [lambda: p.read_bytes(),lambda: builtins.open(p,"rb"),lambda: io.open(p,"rb"),
    lambda: os.open(str(p),os.O_RDONLY),lambda: os.stat(str(p)),lambda: os.lstat(str(p)),lambda: p.resolve(),lambda: os.readlink(str(p))]:
    start=len(traps)
    try:operation()
    except AssertionError:expected_traps.extend(traps[start:]);del traps[start:]
    else:raise ValueError("Original-FS open/stat/lstat/resolve/readlink poison is not active")
  original_cache=Path(helper.CACHE_ROOTS[-1])
  for operation in [lambda: list(original_cache.iterdir()),lambda: os.listdir(str(original_cache)),lambda: list(os.scandir(str(original_cache)))]:
   start=len(traps)
   try:operation()
   except AssertionError:expected_traps.extend(traps[start:]);del traps[start:]
   else:raise ValueError("Original cache directory-listing poison is not active")
  need(not traps,"Unexpected original filesystem attempt")
  helper.operational_index_alias_shape(projection,index)
  index.after()
  helper.operational_index_native_end(index,baseline)
 # No original payload is opened in final metadata custody. Code and approved controls are separate outer scope.
  # The new software/source/control inputs must also be required physical INDEX rows.
  omitted("new_fix11_helper_Source",new_rows[12]["physical_receipt"])
  omitted("Root_software_controller_JSON_Source",new_rows[17]["physical_receipt"])
  omitted("resume_executing_Source",new_rows[18]["physical_receipt"])
  omitted("runtime_request_control",request_r)
 # Changed logical admission is checked against the real original-I data without any leaf IO.
 selected_cache_paths={e["original_receipt"]["path"]for e in OP["cache_history"]["members"]}
 additional=projection.operational["partial_cache_name_authority"]["observation"]["additional_current_child_names"]
 extra_occurrences=[]
 for row in I["files"]:
  for r in [row["original_source"]]+row.get("logical_receipts",[]):
   if r["path"]not in selected_cache_paths and r["path"]==str(Path(helper.PARTIAL_CACHE_ROOT)/Path(r["path"]).name):extra_occurrences.append((row,r))
 need(len(extra_occurrences)==644 and len({r["path"]for row,r in extra_occurrences})==542,"Actual18095 base-I logical-only occurrence denominator")
 row,logical=extra_occurrences[0]
 need(helper.operational_cache_Source_admission(I["files"],[row],OP["cache_history"]["members"],additional),"Real base-I additional-name admission")
 for label,changed in[("altered_base_logical_destination",dict(row,repository_relative="invented/source.py")),("altered_base_logical_role",dict(row,roles=["UNDECLARED_ROLE"]))]:
  try:helper.operational_cache_Source_admission(I["files"],[changed],OP["cache_history"]["members"],additional)
  except ValueError as exc:cases.append(dict(case=label,status="EXPECTED_VALUEERROR",error=str(exc)))
  else:raise ValueError("Altered original-I logical association accepted")
 # Public repair destinations are new, exact and never overwrite one of the old2254 installed targets.
 install_prefix=R/"source/final_delivery_tools/source_cache_fix11_18110"
 need(all((R/"source"/r["repository_relative"]).is_relative_to(install_prefix)for r in new_rows),"Only selected new repair public subtree")
 parent=install_prefix.parent;parent_events={e["path"]:e for e in INSTALL["parent_child_addition_events"]}
 need(str(parent)in parent_events,"Existing installation declares repair parent")
 old_parent=parent_events[str(parent)]
 need(md(parent)==old_parent["after"]and sorted(RAW_LISTDIR(parent))==sorted(old_parent["names_after"]),"Existing parent starts at actual18095 installation.after")
 need(not install_prefix.exists(),"Distinct repair Source subtree absent; never replay/overwrite")
 source_dirs={};source_files={}
 def source_mkdir(path):
  if str(path)in source_dirs:return
  if path!=install_prefix:source_mkdir(path.parent)
  need(path.is_relative_to(install_prefix),"Only fixed repair source subtree")
  parentfd=RAW_OS_OPEN(str(path.parent),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:os.mkdir(path.name,0o775,dir_fd=parentfd);os.fsync(parentfd)
  finally:os.close(parentfd)
  source_dirs[str(path)]=md(path)
 for row in new_rows:
  dest=R/"source"/row["repository_relative"];source_mkdir(dest.parent)
  need(not dest.exists(),"No installed file overwrite")
  raw=read_receipt(row["physical_receipt"])
  parentfd=RAW_OS_OPEN(str(dest.parent),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:
   fd=os.open(dest.name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=parentfd)
   with os.fdopen(fd,"wb")as stream:
    empty=md(dest,stream.fileno());need(empty==md(dest)and empty["bytes"]==0 and empty["nlink"]==1,"New Source empty fd/path")
    stream.write(raw);stream.flush();os.fsync(stream.fileno());os.fchmod(stream.fileno(),0o664);os.fsync(stream.fileno())
    z=md(dest,stream.fileno());need(z==md(dest)and z["bytes"]==len(raw),"Installed repair fd/path")
   os.fsync(parentfd)
  finally:os.close(parentfd)
  fd=RAW_OS_OPEN(str(dest),os.O_RDONLY|os.O_NOFOLLOW)
  with os.fdopen(fd,"rb")as stream:
   need(md(dest,stream.fileno())==z,"Installed readback fd");again=stream.read(len(raw)+1);need(md(dest,stream.fileno())==md(dest)==z,"Installed readback Native")
  need(again==raw,"New public repair fullbyte equality");source_files[str(dest)]=dict(metadata=z,receipt=dict(row["physical_receipt"],path=str(dest)))
 parent_after=md(parent);need(all(parent_after[k]==old_parent["after"][k]for k in META-{"bytes","mtime_ns","ctime_ns","nlink"})and parent_after["nlink"]==old_parent["after"]["nlink"]+1,"Only exact new public subtree parent event")
 need(sorted(RAW_LISTDIR(parent))==sorted(set(old_parent["names_after"])|{install_prefix.name}),"One declared Source parent child")
 source_events=[dict(path=str(parent),before=old_parent["after"],after=parent_after,names_before=old_parent["names_after"],declared_added_children=[install_prefix.name],names_after=sorted(set(old_parent["names_after"])|{install_prefix.name}),created=False,permission_unchanged=True)]
 for p,initial in source_dirs.items():
  after=md(p);names=sorted({Path(x).name for x in list(source_dirs)+list(source_files)if str(Path(x).parent)==p})
  need(all(after[k]==initial[k]for k in META-{"bytes","mtime_ns","ctime_ns","nlink"})and after["nlink"]==initial["nlink"]+sum(str(Path(x).parent)==p for x in source_dirs),"New Source finite fill event")
  need(sorted(RAW_LISTDIR(p))==names,"Exact new Source subtree universe")
  source_events.append(dict(path=p,before=initial,after=after,names_before=[],declared_added_children=names,names_after=names,created=True,permission_unchanged=True))

 def index_end():
  with poison():
   repeated,again=helper.indexed_payloads(binding,pkg,index)
   need(exact(repeated.proof(),expected_proof)and all(path in baseline and baseline[path]==z for path,z in again.items()),"Full repeated current-index proof and fixed baseline")
   index.after();helper.operational_index_native_end(index,baseline)
  need(not traps,"No original/unindexed fallback")
 def original_end():
  current.end()
  for r,z in READS.values():
   actual,raw=read_raw(r["path"],max(r["bytes"],1),z);need(actual==r,"Closed own input bytes unchanged")
  for p,z in installed_md.items():need(md(p)==z,"All old2254 installed file Native unchanged")
  for event in source_events:need(sorted(RAW_LISTDIR(event["path"]))==event["names_after"]and md(event["path"])==event["after"],"Exact new Source parent event remains current")
  for event in MODE_EVENTS:need(sorted(RAW_LISTDIR(event["path"]))==event["names"]and md(event["path"])==event["after"],"Only owned OP3 mode event stays current")
  need(m.sources()==SW["source"],"All executing Source44 unchanged")
 index_end();original_end()
 proof_r=dump(OUT/"current_index_projection.json",expected_proof)
 source_rows_r=dump(OUT/"source_rows.json",projection.source_rows)
 source_r=dump(OUT/"repair_source_installation.json",dict(old_installation=installation_r,old_targets=2254,original_I=i_r,original_manifest=old_late_r,new_manifest=late_r,new_Source_delta=new_rows,new_installed=list(source_files.values()),new_parent_events=source_events,old_target_files_overwritten=False,old_I_or_manifest_changed=False))
 result=dict(schema="root-preserved18095-fix11-current-index-compatibility.v1",status="ACTUAL_CURRENT_SOURCE_AND_REAL_STRICT_INDEX_COMPATIBLE_ARCHIVE_PUBLICATION_ISOLATED_RESTORE_PENDING",allocation=ALLOCATION,
  source_context=binding,source_context_binding=binding_r,source_rows=source_rows_r,finite_projection=proof_r,current_index_manifest=pkg_r,current_index_aliases=alias_r,
  qualified_software=sw_r,qualified_Root_software_control=co_r,contracts=SW["contracts"],original_I=i_r,preserved_manifest=old_late_r,preserved_operational=op_r,preserved_installation=installation_r,
  resumed_manifest=late_r,new_repair_Source_installation=source_r,old_targets_preserved=2254,new_installed_Source=NEW_SOURCE_N,old_cache_evidence_reused=13060,old_cache_evidence_recopied=0,
  mode_events=MODE_EVENTS,current_index_physical_entries=len(index.rows),current_index_alias_count=len(index.aliases),StrictIndex_proof=index.proof(),expected_negative_cases=cases,deliberate_poison_selfchecks=expected_traps,unexpected_original_filesystem_attempts=traps,
  current_root_is_authority_R=True,isolated_restore_performed=False,archive_created=False,production_package_accepted=False,Git_changed=False,published=False,ACTIVE_changed=False,
  publisher18095_remains_failed=True,publisher_replayed=False,no_scientific_recomputation=True,old_Source17_permissions_changed=False)
 result_r=dump(OUT/"acceptance.json",result)
 # Repeats precede a final Native-only fence. New output directories alone become readonly.
 index_end();original_end()
 for p,initial in sorted(DIRS.items(),key=lambda x:len(Path(x[0]).parts),reverse=True):
  before=md(p);names=sorted({Path(x).name for x in list(CREATED)+list(DIRS)if str(Path(x).parent)==p})
  need(sorted(RAW_LISTDIR(p))==names,"Own exact final output universe")
  need(all(before[k]==initial[k]for k in META-{"bytes","mtime_ns","ctime_ns","nlink"})and before["nlink"]==initial["nlink"]+sum(str(Path(x).parent)==p for x in DIRS),"Only declared own output fill")
  fd=RAW_OS_OPEN(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:need(md(p,fd)==before,"Final own directory fd");os.fchmod(fd,0o555);os.fsync(fd);after=md(p,fd);need(after==md(p),"Final own directory fd/path")
  finally:os.close(fd)
  DIRS[p]=after
 for r,z in READS.values():need(md(r["path"])==z,"True-last fixed own/control/Core/Common Native")
 for z in SPEC["conditional_core_metadata"]:need(md(z["path"])==z,"True-last Core2 Native")
 for path,z in baseline.items():need(md(path)==z,"True-last indexed Native")
 for path,z in current.inputs.original.items():need(md(path)==z,"True-last current Native")
 for path,z in installed_md.items():need(md(path)==z,"True-last preserved installed Native")
 for path,item in source_files.items():need(md(path)==item["metadata"],"True-last new Source Native")
 for path,z in CREATED.items():need(md(path)==z,"True-last new output file Native")
 for path,z in DIRS.items():need(md(path)==z,"True-last new output directory Native")
 print(json.dumps(dict(status=result["status"],actual_job_id=JID,acceptance=result_r,source_context_binding=binding_r,source_rows=source_rows_r,resumed_manifest=late_r,new_repair_Source_installation=source_r,current_root_index_only=True,isolated_restore_accepted=False,Git_changed=False,published=False,ACTIVE_changed=False),sort_keys=True,allow_nan=False))

except BaseException as primary:
 failure=dict(schema="root-preserved18095-fix11-resume-incomplete.v1",status="INCOMPLETE_NO_CURRENT_INDEX_OR_DELIVERY_ACCEPTANCE",actual_job_id=JID,error_type=type(primary).__name__,error=str(primary),
  exact_OP_mode_events=MODE_EVENTS,created_output_files=list(CREATED.values()),created_output_directories_initial=list(DIRS.values()),new_Source_files=list(globals().get("source_files",{}).values()),new_Source_directories_initial=list(globals().get("source_dirs",{}).values()),publisher_replayed=False,archive_created=False,published=False,ACTIVE_changed=False)
 try:dump(OUT/"typed_incomplete.json",failure)
 except BaseException as secondary:
  print(json.dumps(dict(status="INCOMPLETE_PRESERVATION_ERROR_OR_SEALED_OUTPUT",primary_error_type=type(primary).__name__,primary_error=str(primary),preservation_error_type=type(secondary).__name__,preservation_error=str(secondary),actual_OP_mode_events=MODE_EVENTS),sort_keys=True,allow_nan=False),file=sys.stderr)
 raise
