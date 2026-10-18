#!/usr/bin/env python3
"""Two exact historical tar namespaces; no extraction or current-path authorization."""
import copy,hashlib,json,tarfile
from pathlib import Path,PurePosixPath
from delivery_core import cpu,rec
R=Path("/lustre/users/u21111210118/projects/test9")
SCHEMA="exact-historical-archive-member-context.v1"
STATUS="EXACT_TWO_HISTORICAL_ARCHIVES_AND588_MEMBER_BYTES_CPU_VERIFIED_ORIGINAL_INDEX_JSON_UNCHANGED"
ROLE="HISTORICAL_ARCHIVE_NAMESPACE_MEMBER_BYTE_VERIFIED_NOT_CURRENT_FILE_OR_NEW_SCIENCE"
EXPECTED_MEMBERS=588
PINS=(
 {"parent_manifest":{"path":str(R/"archive/reconstruction_completed_modules_20261002.members.json"),"bytes":45243,"sha256":"dae90d5f02faedeef24d887e6edf414b86fc63d268e54e58a6a0d558c08d3d6e"},"archive_receipt":{"path":str(R/"archive/reconstruction_completed_modules_20261002.tar.gz"),"bytes":5956754,"sha256":"5cb2577dc3d089fbb69d6039cd6d8948968df7a65b1a7a5cef0311504fb6e9a5"},"member_count":193},
 {"parent_manifest":{"path":str(R/"archive/reconstruction_data_20261002.members.json"),"bytes":98587,"sha256":"20d567dad8b3ae4ec8daf2bf4077f48ba982a746b2a750e0537ab07604ad6e70"},"archive_receipt":{"path":str(R/"archive/reconstruction_data_20261002.tar.gz"),"bytes":23260269,"sha256":"2172e7bb68dcb82e7efc588369d934dbef095fb8680cbea36250cc93d34a9a79"},"member_count":395},
)
def need(value,message):
 if not value:raise ValueError(message)
def shape(r):
 need(isinstance(r,dict)and set(r)=={"path","bytes","sha256"},"Exact archive/member identity required")
 need(isinstance(r["path"],str)and type(r["bytes"])is int and r["bytes"]>=0,"Exact archive/member path and nonnegative integer bytes required")
 need(isinstance(r["sha256"],str)and len(r["sha256"])==64 and all(x in "0123456789abcdef"for x in r["sha256"]),"Exact archive/member SHA required")
 return r
def exact_readonly(r):
 shape(r);p=Path(r["path"])
 need(p.is_absolute()and p.is_relative_to(R)and p.resolve()==p and not p.is_symlink()and p.is_file(),"Exact internal nonsymlink historical archive/index required")
 need(not(p.stat().st_mode&0o222),"Readonly historical archive/index required")
 need(rec(p)==r,"Historical archive/index bytes differ")
 return p
def member_name(name):
 need(isinstance(name,str)and name and "\\"not in name,"Archive namespace path required")
 p=PurePosixPath(name)
 need(not p.is_absolute()and p.as_posix()==name and not any(x in ("",".","..")for x in name.split("/")),"Unsafe or noncanonical archive namespace path")
 return name
def declared_members(parent,pin):
 need(isinstance(parent,dict)and parent.get("archive")==pin["archive_receipt"]["path"]and parent.get("archive_bytes")==pin["archive_receipt"]["bytes"]and parent.get("archive_sha256")==pin["archive_receipt"]["sha256"],"Historical archive/index declaration fork")
 rows=parent.get("members")
 need(parent.get("member_count")==pin["member_count"]and isinstance(rows,list)and len(rows)==pin["member_count"],"Exact historical member-count table required")
 by={}
 for i,r in enumerate(rows):
  shape(r);name=member_name(r["path"])
  need(Path(name).suffix not in {".py",".sh",".sbatch"},"This finite historical scope cannot introduce operative source")
  need(name not in by,"Duplicate historical member identity")
  by[name]=(i,r)
 return by
def verify_tar(archive_receipt,by):
 p=exact_readonly(archive_receipt);seen=set();verified=[];directory_n=0;directories=set()
 allowed_directories={"/".join(PurePosixPath(name).parts[:i])for name in by for i in range(1,len(PurePosixPath(name).parts))}
 with p.open("rb")as source:
  with tarfile.open(fileobj=source,mode="r|gz")as archive:
   for info in archive:
    if info.isdir():
     name=info.name[:-1]if info.name.endswith("/")else info.name;member_name(name)
     need(name in allowed_directories and name not in directories and name not in by,"Unexpected, duplicate or conflicting tar directory")
     directories.add(name);directory_n+=1;continue
    need(info.isreg(),"Historical tar symbolic/hardlink/special member forbidden")
    name=member_name(info.name);need(name in by and name not in seen,"Unexpected or duplicate tar member")
    i,r=by[name];need(info.size==r["bytes"],"Historical tar member byte-count differs")
    handle=archive.extractfile(info);need(handle is not None,"Historical tar member stream unavailable")
    digest=hashlib.sha256();n=0
    with handle:
     for block in iter(lambda:handle.read(1048576),b""):digest.update(block);n+=len(block)
    need(n==r["bytes"]and digest.hexdigest()==r["sha256"],"Historical tar member byte identity differs")
    seen.add(name);verified.append(dict(source_field=["members",str(i)],original_member_path=name,expected_bytes=n,expected_sha256=r["sha256"],canonical_receipt=None,current_execution_allowed=False,current_file_restored=False,raw_member_bytes_verified_in_archive=True))
 need(seen==set(by),"Missing historical tar member")
 exact_readonly(archive_receipt)
 return dict(archive_receipt=archive_receipt,member_count=len(verified),regular_members=sorted(verified,key=lambda r:int(r["source_field"][1])),directory_n=directory_n,archive_bytes_verified_before_and_after=True,extracted=False,archived_JSON_payload_parsed=False)
class ExactHistoricalArchiveMembers:
 def __init__(self,guard=cpu):
  self.allocation=guard()
  need(len(PINS)==2 and sum(x["member_count"]for x in PINS)==EXPECTED_MEMBERS,"Literal two historical archive scopes required")
  self.pins=copy.deepcopy(PINS);self.parents={};self.tables={};self.verified=[];self.observed=set()
  for pin in self.pins:
   r=pin["parent_manifest"];p=exact_readonly(r);obj=json.loads(p.read_text());exact_readonly(r)
   table=declared_members(obj,pin);proof=verify_tar(pin["archive_receipt"],table);exact_readonly(r)
   self.parents[r["path"]]=obj;self.tables[r["path"]]=table
   self.verified.append(dict(parent_manifest=r,**proof))
 def normalize(self,r,parent_context,trail):
  if Path(r.get("path","")).is_absolute():return r,None
  logical=parent_context.get("logical")if isinstance(parent_context,dict)else None
  pin=next((p for p in self.pins if p["parent_manifest"]==logical),None)
  if pin is None:return r,None
  physical=parent_context.get("physical");exact_readonly(physical)
  need((physical["bytes"],physical["sha256"])==(logical["bytes"],logical["sha256"]),"Historical parent logical/physical identity fork")
  need(json.loads(Path(physical["path"]).read_text())==self.parents[logical["path"]],"Historical verified parent changed")
  exact_readonly(physical);shape(r)
  need(isinstance(trail,(tuple,list))and len(trail)==2 and trail[0]=="members"and isinstance(trail[1],str)and trail[1].isdigit()and str(int(trail[1]))==trail[1],"Unknown historical archive member field")
  i=int(trail[1]);rows=self.parents[logical["path"]]["members"]
  need(i<len(rows)and r==rows[i],"Unknown or changed historical archive member identity")
  self.observed.add((logical["path"],i))
  return None,dict(source_parent=logical,source_field=list(trail),original_member_path=r["path"],expected_bytes=r["bytes"],expected_sha256=r["sha256"],archive_receipt=pin["archive_receipt"],canonical_receipt=None,current_execution_allowed=False,current_file_restored=False,raw_member_bytes_verified_in_archive=True,role=ROLE)
 def verification(self):
  for pin in self.pins:exact_readonly(pin["parent_manifest"]);exact_readonly(pin["archive_receipt"])
  return dict(schema="historical-archive-member-byte-verification.v1",status="EXACT_TWO_HISTORICAL_ARCHIVE_BYTES_AND588_MEMBER_BYTES_VERIFIED_NO_EXTRACTION_OR_NEW_SCIENCE",archives=copy.deepcopy(self.verified),historical_archive_context_parent_n=2,archive_member_n=EXPECTED_MEMBERS,allocation=self.allocation,all_regular_members_exactly_verified=True,original_index_JSON_bytes_unchanged=True,archive_extracted=False,archived_JSON_payload_parsed=False,current_file_restored=False,current_execution_authorized=False,new_scientific_inference=False)
 def mapping(self,verification_receipt,lineage):
  expected={(p["parent_manifest"]["path"],i)for p in self.pins for i in range(p["member_count"])}
  need(self.observed==expected,"All finite historical archive member edges must actually be observed")
  shape(verification_receipt);p=exact_readonly(verification_receipt)
  need(json.loads(p.read_text())==self.verification(),"Actual archive verification bytes/proof differ");exact_readonly(verification_receipt)
  rows=[]
  for pin in self.pins:
   parent=pin["parent_manifest"];entries=[]
   for i,r in enumerate(self.parents[parent["path"]]["members"]):
    entries.append(dict(source_parent=parent,source_field=["members",str(i)],original_member_path=r["path"],expected_bytes=r["bytes"],expected_sha256=r["sha256"],canonical_receipt=None,current_execution_allowed=False,current_file_restored=False,raw_member_bytes_verified_in_archive=True))
   rows.append(dict(parent_manifest=parent,archive_receipt=pin["archive_receipt"],member_count=pin["member_count"],entries=entries))
  for pin in self.pins:exact_readonly(pin["parent_manifest"]);exact_readonly(pin["archive_receipt"])
  return dict(schema=SCHEMA,status=STATUS,archives=rows,archive_member_verification=verification_receipt,historical_archive_context_parent_n=2,archive_member_n=EXPECTED_MEMBERS,all588_declared_member_edges_observed=True,all588_member_bytes_independently_verified_in_archives=True,original_index_JSON_bytes_unchanged=True,archive_extracted=False,archived_JSON_payload_parsed=False,current_file_restored=False,current_execution_authorized=False,new_scientific_inference=False,unknown_relative_edges_allowed=False,external_files_read=False,accepted_lineage_receipts=lineage,current_declared_graph_only=True)
