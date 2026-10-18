#!/usr/bin/env python3
"""Only two exact historical tar namespaces; no extraction or current file aliases."""
import copy,hashlib,json,tarfile
from pathlib import Path,PurePosixPath
import exact_relative_bbf_context as b
import historical_annotation_context as h
R=b.R
ARCHIVES=[
 {"parent_manifest":{"path":str(R/"archive/reconstruction_completed_modules_20261002.members.json"),"bytes":45243,"sha256":"dae90d5f02faedeef24d887e6edf414b86fc63d268e54e58a6a0d558c08d3d6e"},"archive_receipt":{"path":str(R/"archive/reconstruction_completed_modules_20261002.tar.gz"),"bytes":5956754,"sha256":"5cb2577dc3d089fbb69d6039cd6d8948968df7a65b1a7a5cef0311504fb6e9a5"},"member_count":193},
 {"parent_manifest":{"path":str(R/"archive/reconstruction_data_20261002.members.json"),"bytes":98587,"sha256":"20d567dad8b3ae4ec8daf2bf4077f48ba982a746b2a750e0537ab07604ad6e70"},"archive_receipt":{"path":str(R/"archive/reconstruction_data_20261002.tar.gz"),"bytes":23260269,"sha256":"2172e7bb68dcb82e7efc588369d934dbef095fb8680cbea36250cc93d34a9a79"},"member_count":395}]
SCHEMA="exact-historical-archive-member-context.v1"
STATUS="EXACT_TWO_HISTORICAL_ARCHIVES_AND588_MEMBER_BYTES_CPU_VERIFIED_ORIGINAL_INDEX_JSON_UNCHANGED"
PROOF_SCHEMA="historical-archive-member-byte-verification.v1"
PROOF_STATUS="EXACT_TWO_HISTORICAL_ARCHIVE_BYTES_AND588_MEMBER_BYTES_VERIFIED_NO_EXTRACTION_OR_NEW_SCIENCE"
ROLE="HISTORICAL_TAR_MEMBER_METADATA_NOT_CURRENT_FILE_OR_NEW_SCIENCE"
def need(v,message):
 if not v:raise ValueError(message)
def total():return sum(x["member_count"]for x in ARCHIVES)
def safe_member_name(name):
 need(isinstance(name,str)and bool(name)and "\x00"not in name and "\\"not in name,"Invalid archive member name")
 p=PurePosixPath(name)
 need(not p.is_absolute()and p.parts and name==p.as_posix()and "."not in p.parts and ".."not in p.parts,"Unsafe archive member namespace")
 need(p.suffix.lower()not in {".py",".sh",".sbatch"},"Historical archive source member is outside this exact no-source scope")
 return name
def parent_rows(parent,obj):
 matches=[x for x in ARCHIVES if x["parent_manifest"]==parent]
 need(len(matches)==1,"Unknown historical archive parent forbidden");spec=matches[0];arc=spec["archive_receipt"]
 need(isinstance(obj,dict)and obj.get("archive")==arc["path"]and obj.get("archive_bytes")==arc["bytes"]and obj.get("archive_sha256")==arc["sha256"]and obj.get("member_count")==spec["member_count"],"Exact original archive inventory header differs")
 rows=obj.get("members");need(isinstance(rows,list)and len(rows)==spec["member_count"],"Whole exact original archive member table required")
 seen=set();verified=[]
 for r in rows:
  rr=b.receipt(r,False);need(set(r)=={"path","bytes","sha256"},"Unexpected original member fields")
  name=safe_member_name(rr["path"]);need(name not in seen,"Duplicate archive inventory member");seen.add(name);verified.append(rr)
 return spec,verified
def entry(spec,i,r):
 return dict(source_parent=copy.deepcopy(spec["parent_manifest"]),source_field=["members",str(i)],original_member_path=r["path"],expected_bytes=r["bytes"],expected_sha256=r["sha256"],canonical_receipt=None,current_execution_allowed=False,current_file_restored=False,raw_member_bytes_verified_in_archive=True)
def scalar(e):
 return {**{k:e[k]for k in ("source_parent","source_field","original_member_path","expected_bytes","expected_sha256","canonical_receipt","current_execution_allowed","current_file_restored","raw_member_bytes_verified_in_archive")},"role":ROLE}
def validate_mapping(m):
 need(isinstance(m,dict)and m.get("schema")==SCHEMA and m.get("status")==STATUS,"Exact historical archive-member map required")
 need(m.get("current_declared_graph_only")is True,"Current declared source graph-only archive scope required")
 need(m.get("historical_archive_context_parent_n")==len(ARCHIVES)and m.get("archive_member_n")==total(),"Exact archive namespace counts required")
 for key,v in dict(all588_declared_member_edges_observed=True,all588_member_bytes_independently_verified_in_archives=True,original_index_JSON_bytes_unchanged=True,archive_extracted=False,archived_JSON_payload_parsed=False,current_file_restored=False,current_execution_authorized=False,new_scientific_inference=False,unknown_relative_edges_allowed=False,external_files_read=False).items():need(m.get(key)is v,"Actual finite archive map policy differs: "+key)
 b.receipt(m["archive_member_verification"])
 rows=m.get("archives");need(isinstance(rows,list)and len(rows)==len(ARCHIVES),"Exactly two declared archive contexts required")
 by={}
 for row in rows:
  matching=[x for x in ARCHIVES if x["parent_manifest"]==row.get("parent_manifest")]
  need(len(matching)==1,"Unknown archive namespace parent");spec=matching[0];key=tuple(spec["parent_manifest"][k]for k in ("path","bytes","sha256"))
  need(key not in by and row.get("archive_receipt")==spec["archive_receipt"]and row.get("member_count")==spec["member_count"],"Duplicate/forked archive context")
  entries=row.get("entries");need(isinstance(entries,list)and len(entries)==spec["member_count"],"All archive member fields required")
  fields=set();names=set()
  for e in entries:
   trail=e.get("source_field");need(isinstance(trail,list)and len(trail)==2 and trail[0]=="members"and isinstance(trail[1],str)and trail[1].isdigit()and str(int(trail[1]))==trail[1]and int(trail[1])<spec["member_count"],"Unknown archive member field")
   need(tuple(trail)not in fields,"Duplicate archive member field");fields.add(tuple(trail))
   r=b.receipt(dict(path=e["original_member_path"],bytes=e["expected_bytes"],sha256=e["expected_sha256"]),False);safe_member_name(r["path"]);need(r["path"]not in names,"Duplicate mapped archive member name");names.add(r["path"])
   expected=entry(spec,int(trail[1]),r);need(set(e)==set(expected)and all(e.get(k)==v for k,v in expected.items()),"Archive member parent/null/noncurrent role differs")
  need(fields=={("members",str(i))for i in range(spec["member_count"])},"Incomplete exact archive fields");by[key]=row
 lineage=m.get("accepted_lineage_receipts");need(isinstance(lineage,list)and len(lineage)>=4 and len({h.key(b.receipt(r))for r in lineage})==len(lineage),"Unique actual archive producer lineage required")
 for key in ("producer_executed_source","producer_actual_software_gate","source_graph_selector","prior_accepted_inclusion"):b.receipt(m[key])
 need(m["producer_executed_source"]in lineage and m["producer_actual_software_gate"]in lineage,"Archive producer source/software lineage missing")
 return by
def exact_manifest_view(parent,obj,m):
 by=validate_mapping(m);spec,rows=parent_rows(parent,obj);row=by[h.key(parent)]
 entries=sorted(row["entries"],key=lambda e:int(e["source_field"][1]))
 need(entries==[entry(spec,i,r)for i,r in enumerate(rows)],"Archive map differs from exact original member table")
 view=copy.deepcopy(obj);contexts=[scalar(e)for e in entries];view["members"]=contexts
 return view,contexts
def normalise_edge(r,parent,trail,m):
 by=validate_mapping(m);need(h.key(b.receipt(parent))in by,"Unknown archive-member parent forbidden before dedup")
 need(isinstance(trail,(tuple,list))and len(trail)==2 and all(isinstance(t,str)for t in trail)and trail[0]=="members"and trail[1].isdigit()and str(int(trail[1]))==trail[1],"Unknown archive-member field forbidden before dedup")
 row=by[h.key(parent)];matching=[e for e in row["entries"]if e["source_field"]==list(trail)]
 need(len(matching)==1,"Unknown archive-member field forbidden before dedup");e=matching[0]
 need(b.receipt(r,False)==dict(path=e["original_member_path"],bytes=e["expected_bytes"],sha256=e["expected_sha256"]),"Unknown archive-member original identity")
 return None,scalar(e)
def verify_tar(path,spec,rows):
 # No extraction or member JSON parsing: stream and compare every regular member byte.
 declared={r["path"]:r for r in rows};seen=set();proof=[];directories=[]
 ancestors={p.as_posix()for name in declared for p in PurePosixPath(name).parents if p.as_posix()!="."}
 with tarfile.open(path,mode="r|gz")as archive:
  for info in archive:
   if info.isdir():
    name=safe_member_name(info.name.rstrip("/"))
    need(name in ancestors and name not in directories and name not in declared,"Unexpected/duplicate/colliding archive directory")
    directories.append(name);continue
   name=safe_member_name(info.name)
   need(info.type in (tarfile.REGTYPE,tarfile.AREGTYPE)and info.isfile()and not info.issym()and not info.islnk()and not info.sparse,"Only actual regular nonsparse archive members allowed")
   need(name not in seen,"Duplicate actual archive member");seen.add(name)
   need(name in declared,"Extra undeclared actual archive member");r=declared[name]
   need(type(info.size)is int and info.size==r["bytes"],"Actual archive member size differs")
   stream=archive.extractfile(info);need(stream is not None,"Actual regular member bytes unavailable")
   sha=hashlib.sha256();n=0
   with stream:
    for chunk in iter(lambda:stream.read(1048576),b""):sha.update(chunk);n+=len(chunk)
   need(n==r["bytes"]and sha.hexdigest()==r["sha256"],"Actual archive member SHA/bytes differ")
   proof.append(dict(original_member_path=name,expected_bytes=r["bytes"],expected_sha256=r["sha256"],actual_bytes=n,actual_sha256=sha.hexdigest(),regular_file=True,current_file_restored=False))
 need(seen==set(declared)and len(proof)==spec["member_count"],"Missing/extra actual archive member universe")
 return dict(parent_manifest=spec["parent_manifest"],archive_receipt=spec["archive_receipt"],member_count=spec["member_count"],members=proof,directory_n=len(directories),directory_names=directories,all_member_bytes_verified=True,current_files_restored=False,member_JSON_payload_parsed=False)
def saved_producer_proof(m,read_exact):
 proof=json.loads(read_exact(m["archive_member_verification"]).read_text())
 need(proof.get("schema")==PROOF_SCHEMA and proof.get("status")==PROOF_STATUS,"Actual producer archive byte proof required")
 need(proof.get("historical_archive_context_parent_n")==len(ARCHIVES)and proof.get("archive_member_n")==total(),"Actual producer archive/member counts differ")
 for key,v in dict(all_regular_members_exactly_verified=True,original_index_JSON_bytes_unchanged=True,archive_extracted=False,archived_JSON_payload_parsed=False,current_file_restored=False,current_execution_authorized=False,new_scientific_inference=False).items():need(proof.get(key)is v,"Actual producer archive proof policy differs: "+key)
 archives=proof.get("archives");need(isinstance(archives,list)and len(archives)==len(ARCHIVES),"Actual producer whole two-archive proof required")
 by=validate_mapping(m)
 for spec in ARCHIVES:
  rows=[r for r in archives if r.get("parent_manifest")==spec["parent_manifest"]];need(len(rows)==1,"Missing/duplicate/forked producer archive parent")
  row=rows[0];entries=sorted(by[h.key(spec["parent_manifest"])]["entries"],key=lambda e:int(e["source_field"][1]))
  expected=[{k:v for k,v in e.items()if k!="source_parent"}for e in entries]
  need(row.get("archive_receipt")==spec["archive_receipt"]and row.get("member_count")==spec["member_count"]and row.get("regular_members")==expected,"Producer tar/member table differs from exact mapping")
  need(type(row.get("directory_n"))is int and row["directory_n"]>=0 and row.get("archive_bytes_verified_before_and_after")is True and row.get("extracted")is False and row.get("archived_JSON_payload_parsed")is False,"Producer archive proof before/after/no-extraction differs")
 return proof
def verify_content(m,read_exact):
 validate_mapping(m)
 for r in m["accepted_lineage_receipts"]+[m["source_graph_selector"],m["prior_accepted_inclusion"]]:read_exact(r)
 saved=saved_producer_proof(m,read_exact);actual=[];contexts=[]
 for spec in ARCHIVES:
  parent=spec["parent_manifest"];obj=json.loads(read_exact(parent).read_text());_,rows=parent_rows(parent,obj)
  _,view=exact_manifest_view(parent,obj,m);contexts.extend(view)
  path=read_exact(spec["archive_receipt"]);one=verify_tar(path,spec,rows)
  savedone=next(r for r in saved["archives"]if r["parent_manifest"]==parent);need(savedone["directory_n"]==one["directory_n"],"Producer directory accounting differs from actual tar")
  read_exact(spec["archive_receipt"]);read_exact(parent);actual.append(one)
 return dict(schema="independent-historical-archive-member-verification.v1",mapping_receipt=None,parent_manifests=[s["parent_manifest"]for s in ARCHIVES],archive_receipts=[s["archive_receipt"]for s in ARCHIVES],archive_member_verification=m["archive_member_verification"],archives=actual,archive_parent_n=len(ARCHIVES),member_n=total(),all_member_bytes_verified=True,all_exact_parent_fields_verified=True,contexts=contexts,original_json_unchanged=True,archive_bytes_unchanged=True,no_extraction=True,current_files_restored=False,member_JSON_payload_parsed=False,new_scientific_inference=False,saved_producer_proof_schema=saved["schema"])
def verify_mapping_receipt(receipt):
 allocation=b.cpu_guard();m=json.loads(b.verify_bytes(receipt,True).read_text());proof=verify_content(m,lambda r:b.verify_bytes(r,True));proof.update(mapping_receipt=b.receipt(receipt),allocation=allocation);return m,proof
class VerifiedArchiveMemberReader:
 def __init__(self,mapping_receipt,reader,parent_aliases=()):
  self.mapping_receipt=b.receipt(mapping_receipt);self.mapping,self.verification=verify_mapping_receipt(mapping_receipt);self.reader=reader;self.used=[]
  self.parents={s["parent_manifest"]["path"]:(s["parent_manifest"],s["parent_manifest"])for s in ARCHIVES}
  for row in parent_aliases:
   need(isinstance(row,dict)and set(row)=={"logical","physical"},"Exact archive parent alias shape required")
   logical=b.receipt(row["logical"]);need(any(logical==s["parent_manifest"]for s in ARCHIVES),"Unknown archive parent alias")
   physical=b.receipt(row["physical"]);need((physical["bytes"],physical["sha256"])==(logical["bytes"],logical["sha256"])and physical["path"]not in self.parents,"Archive parent alias byte/duplicate mismatch")
   b.verify_bytes(physical,True);self.parents[physical["path"]]=(logical,physical)
 def __call__(self,path):
  p=Path(path);need(p.is_absolute()and p.is_relative_to(R)and p.resolve()==p,"External archive metadata reads forbidden")
  if str(p)not in self.parents:return self.reader(path)
  logical,physical=self.parents[str(p)];b.verify_bytes(physical,True);obj=self.reader(path);view,contexts=exact_manifest_view(logical,obj,self.mapping);b.verify_bytes(physical,True)
  self.used.append(dict(physical_parent=physical,logical_parent=logical,contexts=contexts,raw_JSON_changed=False));return view
 def proof(self):return dict(mapping_receipt=self.mapping_receipt,verification=self.verification,read_views_used=self.used,scope="EXACT_TWO_ARCHIVE_MEMBER_SCALAR_NAMESPACES_NO_EXTRACTION",raw_JSON_changed=False,module_local_reader_only=True,current_files_restored=False,member_JSON_payload_parsed=False)
def verify_restored_mapping(mapping_receipt,restore_root,index):
 allocation=b.cpu_guard();root,lookup=b.restored_index(index,restore_root);read_paths=[]
 def exact(r):
  p=b.restored_bytes(r,root,lookup);need(not(p.stat().st_mode&0o222),"Readonly restored archive metadata/tars/source required");read_paths.append(str(p));return p
 m=json.loads(exact(mapping_receipt).read_text());proof=verify_content(m,exact)
 proof.update(mapping_receipt=b.receipt(mapping_receipt),allocation=allocation,restored_root=str(root),read_paths=read_paths,all_read_paths_under_restored_root=True,no_live_root_fallback=True);return m,proof
def verify_saved_verification(accepted,read_exact):
 saved=json.loads(read_exact(accepted["archive_member_verification"]).read_text())
 mapping_receipt=accepted.get("archive_member_receipt_context_mapping");m=json.loads(read_exact(mapping_receipt).read_text());by=validate_mapping(m)
 need(saved.get("schema")=="independent-historical-archive-member-verification.v1"and saved.get("mapping_receipt")==mapping_receipt,"Actual saved independent archive proof schema/identity differs")
 need(saved.get("parent_manifests")==[x["parent_manifest"]for x in ARCHIVES]and saved.get("archive_receipts")==[x["archive_receipt"]for x in ARCHIVES]and saved.get("archive_member_verification")==m["archive_member_verification"]and saved.get("archive_parent_n")==len(ARCHIVES)and saved.get("member_n")==total(),"Actual saved independent full archive universe differs")
 for key,value in dict(all_member_bytes_verified=True,all_exact_parent_fields_verified=True,original_json_unchanged=True,archive_bytes_unchanged=True,no_extraction=True,current_files_restored=False,member_JSON_payload_parsed=False,new_scientific_inference=False).items():need(saved.get(key)is value,"Actual saved archive proof policy differs: "+key)
 need(saved.get("saved_producer_proof_schema")==PROOF_SCHEMA,"Actual saved producer proof schema binding missing")
 archives=saved.get("archives");need(isinstance(archives,list)and len(archives)==len(ARCHIVES),"Saved independent actual two-archive member tables missing")
 all_contexts=[]
 for spec in ARCHIVES:
  entries=sorted(by[h.key(spec["parent_manifest"])]["entries"],key=lambda e:int(e["source_field"][1]));all_contexts.extend(scalar(e)for e in entries)
  matches=[row for row in archives if row.get("parent_manifest")==spec["parent_manifest"]];need(len(matches)==1,"Saved independent archive parent missing/duplicate")
  row=matches[0];need(row.get("archive_receipt")==spec["archive_receipt"]and row.get("member_count")==spec["member_count"]and row.get("all_member_bytes_verified")is True and row.get("current_files_restored")is False and row.get("member_JSON_payload_parsed")is False,"Saved actual archive descriptor/policy differs")
  members=row.get("members");need(isinstance(members,list)and len(members)==spec["member_count"],"Saved independent complete member rows missing")
  expected={e["original_member_path"]:dict(original_member_path=e["original_member_path"],expected_bytes=e["expected_bytes"],expected_sha256=e["expected_sha256"],actual_bytes=e["expected_bytes"],actual_sha256=e["expected_sha256"],regular_file=True,current_file_restored=False)for e in entries};seen=set()
  for member in members:
   need(isinstance(member,dict),"Saved actual regular member row required");name=safe_member_name(member.get("original_member_path"))
   need(name in expected and name not in seen and member==expected[name],"Saved actual member bytes/SHA/null/current role differs");seen.add(name)
  need(seen==set(expected),"Saved independent member universe is incomplete")
  dirs=row.get("directory_names");need(isinstance(dirs,list)and type(row.get("directory_n"))is int and row["directory_n"]==len(dirs)and len(set(dirs))==len(dirs),"Saved directory count/unique table differs")
  ancestors={p.as_posix()for name in expected for p in PurePosixPath(name).parents if p.as_posix()!="."}
  for name in dirs:need(safe_member_name(name)in ancestors and name not in expected,"Saved unsafe/extra/colliding archive directory")
 need(saved.get("contexts")==all_contexts,"Saved exact all588 scalar parent/field contexts missing/forked")
 saved_producer_proof(m,read_exact)
 if accepted.get("allocation")is not None:need(saved.get("allocation",{}).get("job_id")==accepted["allocation"].get("job_id"),"Saved actual mapper CPU proof allocation differs")
 return saved
