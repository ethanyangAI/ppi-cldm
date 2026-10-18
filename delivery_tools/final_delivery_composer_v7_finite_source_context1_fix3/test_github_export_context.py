"""32 real Git-object/export/closure/restore CPU contracts, all synthetic software evidence.
No remote requests, publication, production science, GPU, default writes or formal reads.
"""
import copy,hashlib,json,os,shutil,subprocess,tempfile,unittest
from pathlib import Path
from unittest import mock
import final_delivery_composer as m
g=m.export_api()
class ExportContracts(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=m.R/"steps/24_benchmark_delivery/tmp",prefix="github_export_fixture_");self.d=Path(self.tmp.name)
  self.repo=self.d/"repo";self.repo.mkdir()
  self.git("init","-q");self.git("config","user.name","SYNTHETIC CPU FIXTURE");self.git("config","user.email","fixture@example.invalid")
  (self.repo/"unchanged.txt").write_text("UNCHANGED SYNTHETIC\n");(self.repo/"deleted.txt").write_text("DELETED SYNTHETIC\n")
  self.git("add",".");self.git("commit","-qm","synthetic baseline");self.base=self.git("rev-parse","HEAD").strip()
  (self.repo/"deleted.txt").unlink();(self.repo/"nested").mkdir();(self.repo/"nested"/"data.json").write_text('{"path":"receipt-looking-relative","sha256":"'+"a"*64+'","bytes":3,"SYNTHETIC":true}\n')
  (self.repo/"script.sh").write_text("#!/bin/sh\nexit 0\n");(self.repo/"script.sh").chmod(0o755);os.symlink("unchanged.txt",self.repo/"link")
  self.git("add","-A");self.git("commit","-qm","synthetic final");self.head=self.git("rev-parse","HEAD").strip()
  producer=m.load("export_fixture_producer_"+self.d.name,Path(m.EXPORTER_RECEIPT["path"]))
  self.exportdir=self.d/"export";producer.export(self.repo,self.base,self.head,self.exportdir,g.REPOSITORY,allocation=dict(SYNTHETIC_SOFTWARE_ONLY=True))
  self.mr=m.rec(self.exportdir/"export_manifest.json");self.man=g.obj(self.mr,g.local_bytes);self.children=g.manifest_shape(self.man,str(self.exportdir),self.mr)
  self.ir=next(x["canonical"]for x in self.children if x["field"]==["source_inventory"]);self.entries=g.inventory_shape(g.obj(self.ir,g.local_bytes))
  self.plan=g.obj(next(x["canonical"]for x in self.children if x["field"]==["handoff_plan"]),g.local_bytes)
  self.source=m.sources();self.swlog=self.file("fixture_contracts.log",b"EXPLICIT SYNTHETIC SOFTWARE DATA; NO ACTUAL SOFTWARE ACCEPTANCE")
  self.contracts=self.dump("fixture_contracts.json",dict(status="PASS",tests_run=m.SOFTWARE_TESTS,errors=0,failures=0,tested_source=self.source,all_owned_and_context_python_compile_PASS=True,all_launchers_bash_syntax_PASS=True,log=self.swlog,SYNTHETIC_SOFTWARE_ONLY=True))
  self.software=self.dump("fixture_software.json",dict(schema="final-composer-software.v7",status=m.SOFTWARE_STATUS,source=self.source,contracts=self.contracts,original_owned_pre_and_post_byte_readback_PASS=True,original_executing_sources=self.source["composer"],original_source_entry=next(r for r in self.source["composer"]if Path(r["path"]).name=="composer_bootstrap.py"),SYNTHETIC_SOFTWARE_ONLY=True))
  self.branch="synthetic/qualified";self.fetched="refs/remotes/root-qualified/"+self.branch
  self.public=self.git("commit-tree",self.man["final_tree_sha"],"-p",self.base,input=b"SYNTHETIC public commit\n").strip()
  self.git("update-ref",self.fetched,self.public)
  self.captures=[]
  for call in self.plan["blob_calls"]+self.plan["tree_calls"]:
   e=next(x for x in self.children if x["relative_name"]==call["payload"]);operation="create_blob"if call in self.plan["blob_calls"]else"create_tree"
   self.capture(operation,g.obj(e["canonical"],g.local_bytes),dict(sha=call["expected_sha"]),export_payload_name=call["payload"],export_payload_receipt=e["canonical"])
  self.capture("create_commit",dict(repository_full_name=g.REPOSITORY,parent_sha=self.base,tree_sha=self.man["final_tree_sha"],message="SYNTHETIC public commit"),dict(sha=self.public,tree=dict(sha=self.man["final_tree_sha"]),parents=[dict(sha=self.base)]))
  self.capture("create_branch",dict(repository_full_name=g.REPOSITORY,branch_name=self.branch,sha=self.public),dict(ref="refs/heads/"+self.branch,object=dict(sha=self.public)))
  self.maps=g.response_maps(self.plan,self.captures,g.local_bytes,self.public,self.branch);self.maps_r=self.dump("maps.json",self.maps)
  verifier=m.load("export_fixture_verify_"+self.d.name,m.LIB/"github_export_verify.py")
  readback=verifier.verify(str(self.exportdir),str(self.repo),self.maps,self.fetched);self.check_r=self.dump("readback.json",readback)
  self.bundle=self.d/"source.bundle";self.git("bundle","create",str(self.bundle),"--all");self.bundle.chmod(0o444);self.bundle_r=m.rec(self.bundle)
  tree=dict(sha=self.man["final_tree_sha"],truncated=False,tree=g.leaf_rows(self.entries)+[dict(path=p,mode="040000",type="tree",sha=sha)for p,sha in g.tree_map(self.entries).items()if p])
  bodies=dict(ref=dict(ref="refs/heads/"+self.branch,object=dict(sha=self.public)),commit=dict(sha=self.public,tree=dict(sha=self.man["final_tree_sha"]),parents=[dict(sha=self.base)]),tree=tree)
  urls=dict(ref="git/ref/heads/"+self.branch,commit="git/commits/"+self.public,tree="git/trees/"+self.man["final_tree_sha"]+"?recursive=1")
  gets={k:dict(url="https://api.github.com/repos/"+g.REPOSITORY+"/"+urls[k],http_status=200,captured_utc="SYNTHETIC_ONLY",body=self.dump(k+".response.json",v),headers=self.file(k+".headers.txt",b"SYNTHETIC ONLY"))for k,v in bodies.items()}
  self.proof=dict(schema=g.REMOTE_SCHEMA,status=g.REMOTE_STATUS,root_owned=True,repository_full_name=g.REPOSITORY,actual_CPU_job_id="999999",source=self.source,software=self.software,manifest=self.mr,private_source_bundle=self.bundle_r,private_commit=self.head,public_commit=self.public,final_tree=self.man["final_tree_sha"],baseline_commit=self.base,branch=self.branch,remote_ref="refs/heads/"+self.branch,fetched_ref=self.fetched,public_GET=gets,write_response_captures=self.captures,normalized_API_responses=self.maps_r,unchanged_verifier_readback=self.check_r,fetch=dict(argv=["git","-C",str(self.repo),"fetch","--no-tags","https://github.com/"+g.REPOSITORY+".git","refs/heads/"+self.branch+":"+self.fetched],returncode=0,resolved_commit=self.public,resolved_tree=self.man["final_tree_sha"],parent_shas=[self.base],stdout=self.file("fetch.stdout",b"SYNTHETIC fixture only"),stderr=self.file("fetch.stderr",b"")),public_commit_object=self.file(self.public+".gitcommit",g.git(self.repo,"cat-file","commit",self.public)),baseline_commit_object=self.file(self.base+".gitcommit",g.git(self.repo,"cat-file","commit",self.base)),baseline_tree_entries=g.git_entries(self.repo,self.base),private_bundle_verification=dict(argv=["git","-C",str(self.repo),"bundle","verify",str(self.bundle)],returncode=0,stdout=self.file("bundle.stdout",b"SYNTHETIC fixture only"),stderr=self.file("bundle.stderr",b""),heads=self.file("bundle.heads",g.git(self.repo,"bundle","list-heads",str(self.bundle)))),SYNTHETIC_SOFTWARE_ONLY=True)
  self.proof["request"]=self.dump("readback_request.json",dict(schema="github-export-readback-request.v1",root_owned=True,repository_full_name=g.REPOSITORY,authorize_public_GET_and_exact_remote_fetch=True,branch=self.branch,source_bundle=self.bundle_r,write_response_captures=self.captures,export=dict(manifest=self.mr,export_dir=str(self.exportdir)),SYNTHETIC_SOFTWARE_ONLY=True))
  self.proof["allocation"]=dict(job_id="999999",allocated_gpus=0,scheduler_record="JobId=999999 JobState=RUNNING UserId=u21111210118(1) Account=u21111210118 Partition=organ NumCPUs=1 TRES=cpu=1,mem=16G")
  self.remote_r=self.dump("remote.json",self.proof);blobdir=self.d/"blobstore";blobdir.mkdir();rows=[];unique={}
  for i,e in enumerate(self.entries):
   if e["type"]=="blob":
    if e["sha"]not in unique:unique[e["sha"]]=self.file("blobstore/"+e["sha"]+".gitblob",g.git(self.repo,"cat-file","blob",e["sha"]))
    rows.append(dict(index=i,entry=dict({k:v for k,v in e.items()if k!="path"},repository_path=e["path"]),canonical=unique[e["sha"]]))
  blobdir.chmod(0o555);row=["999999","COMPLETED","0:0","1","cpu=1,mem=16G","u21111210118","u21111210118","organ","test9_final_composer_source_contexts_v7"]
  self.q=dict(schema=g.SCHEMA,status=g.STATUS,scope="PUBLIC_GIT_SOURCE_EVIDENCE_ONLY",source=self.source,software=self.software,private_source_bundle=self.bundle_r,manifest=self.mr,export_dir=str(self.exportdir),inventory=self.ir,children=self.children,blob_directory=str(blobdir),blob_observations=rows,remote_readback=self.remote_r,actual_remote_terminal=dict(row=row,raw_sacct="|".join(row)+"\n",allocated_GPUs=0,allocated_CPUs=1),parents_n=2,child_n=len(self.children),blob_path_n=len(rows),unique_blob_n=len(unique),raw_JSON_changed=False,live_restore_fallback_allowed=False,SYNTHETIC_SOFTWARE_ONLY=True)
  self.refresh()
 def tearDown(self):
  for p in self.d.rglob("*"):
   if p.is_dir()and not p.is_symlink():p.chmod(0o755)
  self.tmp.cleanup()
 def git(self,*args,input=None):
  return subprocess.check_output(["git","-C",str(self.repo),*args],input=input).decode()
 def file(self,name,data):
  p=self.d/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);p.chmod(0o444);return m.rec(p)
 def dump(self,name,data):return self.file(name,json.dumps(data,sort_keys=True).encode())
 def capture(self,operation,request,raw,**extra):
  raw_r=self.dump("tool_output_"+str(len(self.captures))+".json",dict(result=raw,SYNTHETIC_SOFTWARE_ONLY=True))
  names=dict(create_blob="mcp__codex_apps__github_create_blob",create_tree="mcp__codex_apps__github_create_tree",create_commit="mcp__codex_apps__github_create_commit",create_branch="mcp__codex_apps__github_create_branch")
  c=dict(schema="root-github-write-response-capture.v1",root_owned=True,repository_full_name=g.REPOSITORY,operation=operation,request=request,raw_response=raw,actual_tool_output=raw_r,response_json_pointer=["result"],response_value_encoding="JSON_OBJECT",actual_tool_name=names[operation],capture_id="SYNTHETIC_"+str(len(self.captures)),actual_tool_call_id=None,actual_response_id=None,opaque_connector_ids_status="UNAVAILABLE_FROM_CONNECTOR",captured_utc="SYNTHETIC_ONLY",response_success=True,SYNTHETIC_SOFTWARE_ONLY=True,**extra)
  self.captures.append(self.dump("capture_"+str(len(self.captures))+".json",c))
 def refresh(self):
  self.q.pop("required_receipts",None)
  rows=g.all_receipts(self.q)+g.evidence_inputs(self.proof,g.obj(self.software,g.local_bytes),g.obj(self.contracts,g.local_bytes),g.local_bytes)
  self.q["required_receipts"]=list({g.rid(r):r for r in rows}.values())
 def result(self):return g.qualification_core(self.q,g.local_bytes,self.source)
 def reader(self):
  return g.ExportContextReader(self.q,self.result(),g.local_bytes,lambda p:json.loads(Path(p).read_bytes()))
 def restored(self):
  root=self.d/"isolated";root.mkdir();entries={}
  qr=self.dump("qualification.json",self.q)
  for i,r in enumerate([qr]+self.q["required_receipts"]):
   target=root/str(i);target.write_bytes(g.local_bytes(r));target.chmod(0o444);entries[g.rid(r)]=target
  def read(r):
   g.receipt(r);p=entries[g.rid(r)];m.need(p.resolve()==p and p.is_relative_to(root)and not p.is_symlink()and not(p.stat().st_mode&0o222),"Indexed readonly restore file required");return p.read_bytes()
  return root,entries,qr,read
 def test_01_real_export_full_baseline_new_and_tree(self):
  self.result();self.assertIn("unchanged.txt",[e["path"]for e in self.entries]);self.assertNotIn("deleted.txt",[e["path"]for e in self.entries])
  self.assertEqual(g.tree_oid(self.entries),self.git("rev-parse",self.head+"^{tree}").strip())
 def test_02_both_namespace_read_views_and_raw_unchanged(self):
  before=g.local_bytes(self.mr),g.local_bytes(self.ir);r=self.reader();mv=r(self.mr["path"]);iv=r(self.ir["path"]);r.require_both_used()
  self.assertTrue(Path(mv["source_inventory"]["path"]).is_absolute());self.assertTrue(all(Path(e["path"]).suffix==".gitblob"for e in iv["entries"]if e["type"]=="blob"))
  self.assertEqual(before,(g.local_bytes(self.mr),g.local_bytes(self.ir)))
 def test_03_symlink_git_blob_text_is_not_target(self):
  row=next(x for x in self.q["blob_observations"]if x["entry"]["repository_path"]=="link")
  self.assertEqual(g.local_bytes(row["canonical"]),b"unchanged.txt");self.assertNotEqual(g.local_bytes(row["canonical"]),(self.repo/"unchanged.txt").read_bytes())
 def test_04_executable_and_json_modes_preserved(self):
  self.assertEqual(next(e["mode"]for e in self.entries if e["path"]=="script.sh"),"100755");self.assertEqual(next(e["mode"]for e in self.entries if e["path"].endswith(".json")),"100644");self.result()
 def test_05_wrong_manifest_schema_rejected(self):
  v=copy.deepcopy(self.man);v["schema"]="relative-anything"
  with self.assertRaises(ValueError):g.manifest_shape(v,str(self.exportdir),self.mr)
 def test_06_other_export_parent_rejected_before_dedup(self):
  r=self.reader();r(self.mr["path"])
  with self.assertRaises(ValueError):r.normalize_edge(self.children[0]["canonical"],dict(self.mr,sha256="0"*64),self.children[0]["field"])
 def test_07_wrong_field_and_index_rejected(self):
  r=self.reader();r(self.mr["path"])
  for field in(("unapproved",),("object_payloads","999")):
   with self.subTest(field=field),self.assertRaises(ValueError):r.normalize_edge(self.children[0]["canonical"],self.mr,field)
 def test_08_conflicting_child_identity_rejected(self):
  r=self.reader()
  with self.assertRaises(ValueError):r.normalize_edge(dict(self.children[0]["canonical"],sha256="0"*64),self.mr,self.children[0]["field"])
 def test_09_lexical_traversal_and_absolute_children_rejected(self):
  for p in("../source_inventory.json","./source_inventory.json","blobs//"+"a"*40+".json","/source_inventory.json"):
   with self.subTest(path=p),self.assertRaises(ValueError):g.relative_payload(p)
 def test_10_root_intermediate_leaf_symlinks_rejected(self):
  target=self.d/"target";target.mkdir();(target/"source_inventory.json").write_bytes(b"{}");sha="a"*40
  (target/(sha+".json")).write_bytes(b"{}")
  rootlink=self.d/"rootlink";rootlink.symlink_to(target)
  mid=self.d/"mid";mid.mkdir();(mid/"blobs").symlink_to(target)
  leaf=self.d/"leaf";leaf.mkdir();(leaf/"source_inventory.json").symlink_to(target/"source_inventory.json")
  for root,p in((rootlink,"source_inventory.json"),(mid,"blobs/"+sha+".json"),(leaf,"source_inventory.json")):
   with self.subTest(root=str(root)),self.assertRaises(ValueError):g.child_receipt(str(root),dict(path=p,bytes=2,sha256=hashlib.sha256(b"{}").hexdigest()))
 def test_11_duplicate_inventory_path_rejected(self):
  v=g.obj(self.ir,g.local_bytes);v["entries"].append(copy.deepcopy(v["entries"][0]))
  with self.assertRaises(ValueError):g.inventory_shape(v)
 def test_12_duplicate_payload_path_or_sha_rejected(self):
  v=copy.deepcopy(self.man);v["object_payloads"].append(copy.deepcopy(v["object_payloads"][0]))
  with self.assertRaises(ValueError):g.manifest_shape(v,str(self.exportdir),self.mr)
 def test_13_missing_full_baseline_blob_rejected(self):
  self.q["blob_observations"]=[x for x in self.q["blob_observations"]if x["entry"]["repository_path"]!="unchanged.txt"]
  with self.assertRaises(ValueError):self.result()
 def test_14_blob_bytes_or_git_header_identity_drift_rejected(self):
  row=self.q["blob_observations"][0];p=Path(row["canonical"]["path"]);p.chmod(0o644);p.write_bytes(b"CORRUPTED");p.chmod(0o444)
  with self.assertRaises(ValueError):self.result()
 def test_15_inventory_repository_namespace_not_export_dir(self):
  v=self.reader()(self.ir["path"]);row=next(e for e in v["entries"]if e["original_repository_path"]=="nested/data.json")
  self.assertEqual(Path(row["path"]).suffix,".gitblob");self.assertNotEqual(row["path"],str(self.exportdir/"nested/data.json"))
 def test_16_unknown_inventory_or_manifest_receipt_rejected(self):
  for kind in("manifest","inventory"):
   with self.subTest(kind=kind):
    v=copy.deepcopy(self.man)if kind=="manifest"else g.obj(self.ir,g.local_bytes);v["unapproved"]=dict(path="anything",bytes=1,sha256="a"*64)
    with self.assertRaises(ValueError):
     if kind=="manifest":g.manifest_shape(v,str(self.exportdir),self.mr)
     else:g.inventory_shape(v)
 def test_17_missing_or_false_actual_API_capture_rejected(self):
  with self.assertRaises(ValueError):g.response_maps(self.plan,self.captures[:-1],g.local_bytes,self.public,self.branch)
  c=g.obj(self.captures[0],g.local_bytes);c["response_success"]=False;bad=self.dump("capture_bad.json",c)
  with self.assertRaises(ValueError):g.response_maps(self.plan,[bad]+self.captures[1:],g.local_bytes,self.public,self.branch)
  for operation,field,value in(("create_commit","additional_parent_shas",[self.head]),("create_branch","base_ref","master")):
   capture=next(r for r in self.captures if g.obj(r,g.local_bytes)["operation"]==operation);c=g.obj(capture,g.local_bytes);c["request"][field]=value;bad=self.dump(operation+"_extra_parent.json",c);captures=[bad if r==capture else r for r in self.captures]
   with self.subTest(operation=operation),self.assertRaises(ValueError):g.response_maps(self.plan,captures,g.local_bytes,self.public,self.branch)
 def test_18_normalization_cannot_fork_actual_raw_tool_output(self):
  text_capture=g.obj(self.captures[0],g.local_bytes);text_capture["response_value_encoding"]="JSON_TEXT";text_capture["actual_tool_output"]=self.dump("actual_json_text.json",dict(result=json.dumps(text_capture["raw_response"])));text_r=self.dump("text_capture.json",text_capture)
  self.assertEqual(g.response_maps(self.plan,[text_r]+self.captures[1:],g.local_bytes,self.public,self.branch),self.maps)
  c=g.obj(self.captures[0],g.local_bytes);c["actual_tool_output"]=self.dump("fork_raw.json",dict(result=dict(sha="0"*40)));bad=self.dump("fork_capture.json",c)
  with self.assertRaises(ValueError):g.response_maps(self.plan,[bad]+self.captures[1:],g.local_bytes,self.public,self.branch)
 def test_19_commit_wrong_parent_or_tree_rejected(self):
  p=copy.deepcopy(self.proof);v=g.obj(p["public_GET"]["commit"]["body"],g.local_bytes);v["parents"]=[dict(sha=self.head)];p["public_GET"]["commit"]["body"]=self.dump("badcommit.json",v)
  with self.assertRaises(ValueError):g.remote_content(p,dict(data=self.man,receipt=self.mr),self.entries,self.plan,g.local_bytes)
 def test_20_remote_ref_alias_and_wrong_URL_rejected(self):
  root=g.obj(self.proof["request"],g.local_bytes);root["authorize_public_GET_and_exact_remote_fetch"]=False;p=copy.deepcopy(self.proof);p["request"]=self.dump("false_authority.json",root)
  with self.assertRaises(ValueError):g.remote_content(p,dict(data=self.man,receipt=self.mr),self.entries,self.plan,g.local_bytes)
  p=copy.deepcopy(self.proof);p["fetched_ref"]="HEAD"
  with self.assertRaises(ValueError):g.remote_content(p,dict(data=self.man,receipt=self.mr),self.entries,self.plan,g.local_bytes)
  p=copy.deepcopy(self.proof);p["public_GET"]["ref"]["url"]="https://example.invalid/ref"
  with self.assertRaises(ValueError):g.remote_content(p,dict(data=self.man,receipt=self.mr),self.entries,self.plan,g.local_bytes)
 def test_21_remote_tree_full_modes_and_nontruncation_required(self):
  for change in("truncated","mode","directory"):
   with self.subTest(change=change):
    p=copy.deepcopy(self.proof);v=g.obj(p["public_GET"]["tree"]["body"],g.local_bytes)
    if change=="truncated":v["truncated"]=True
    elif change=="mode":v["tree"][0]["mode"]="100755"if v["tree"][0]["mode"]!="100755"else"100644"
    else:next(e for e in v["tree"]if e["type"]=="tree")["sha"]="a"*40
    p["public_GET"]["tree"]["body"]=self.dump("tree_"+change+".json",v)
    with self.assertRaises(ValueError):g.remote_content(p,dict(data=self.man,receipt=self.mr),self.entries,self.plan,g.local_bytes)
 def test_22_raw_commit_object_and_baseline_graph_required(self):
  p=copy.deepcopy(self.proof);p["public_commit_object"]=self.file("invalid.gitcommit",b"tree "+self.man["final_tree_sha"].encode()+b"\n\ninvalid")
  with self.assertRaises(ValueError):g.remote_content(p,dict(data=self.man,receipt=self.mr),self.entries,self.plan,g.local_bytes)
 def test_23_whole_source_dependency_fork_rejected(self):
  source=copy.deepcopy(self.source);source["composer"][0]["sha256"]="0"*64
  with self.assertRaises(ValueError):g.qualification_core(self.q,g.local_bytes,source)
  altered=g.obj(self.software,g.local_bytes);altered["original_source_entry"]=self.source["composer"][0];qr=copy.deepcopy(self.q);qr["software"]=self.dump("wrong_bootstrap_software.json",altered)
  with self.assertRaises(ValueError):g.qualification_core(qr,g.local_bytes,self.source)
 def test_24_actual_helper_executes_sealed_path_and_module(self):
  self.assertEqual(Path(g.__file__).resolve(),m.D/"github_export_context.py");self.assertIs(g.m,m);self.assertEqual(len(m.FILES),15)
  original=[];sealed=[]
  for i,name in enumerate(m.FILES):
   original.append(self.file("original/"+name,("SYNTHETIC "+str(i)).encode()));sealed.append(self.file("sealed/"+name,("SYNTHETIC "+str(i)).encode()))
  m.original_source_readback(original,sealed);p=Path(original[0]["path"]);p.chmod(0o644);p.write_bytes(b"CHANGED");p.chmod(0o444)
  with self.assertRaises(ValueError):m.original_source_readback(original,sealed)
 def test_25_restored_only_no_live_default(self):
  qr=self.dump("qualification.json",self.q)
  with self.assertRaises(ValueError):g.verify_qualification(qr,restore=True,expected_source=self.source)
  with self.assertRaises(ValueError):g.verify_qualification(qr,g.local_bytes,restore=True,expected_source=self.source)
 def test_26_restored_full_blobs_and_tree_without_any_live_export(self):
  root,index,qr,read=self.restored()
  for p in self.exportdir.rglob("*"):
   if p.is_dir():p.chmod(0o755)
  self.exportdir.chmod(0o755);shutil.rmtree(self.exportdir);q,result=g.verify_qualification(qr,read,restore=True,expected_source=self.source);reader=g.ExportContextReader(q,result,read,lambda p:json.loads(read(next(r for r in q["required_receipts"]if r["path"]==p))))
  reader(q["manifest"]["path"]);reader(q["inventory"]["path"]);reader.require_both_used();self.assertEqual(g.tree_oid(result[1]),self.man["final_tree_sha"])
 def test_27_restored_missing_required_inputs_live_cannot_rescue(self):
  root,index,qr,read=self.restored()
  choices=[self.mr,self.ir,self.proof["public_GET"]["ref"]["body"],self.captures[0],self.q["blob_observations"][0]["canonical"],self.source["composer"][0],self.source["existing_API_dependencies"][0]]
  for r in choices:
   with self.subTest(path=r["path"]):
    p=index.pop(g.rid(r))
    with self.assertRaises(KeyError):g.verify_qualification(qr,read,restore=True,expected_source=self.source)
    index[g.rid(r)]=p
  p=index[g.rid(self.mr)];p.chmod(0o644)
  with self.assertRaises(ValueError):g.verify_qualification(qr,read,restore=True,expected_source=self.source)
  p.chmod(0o444)
 def test_28_saved_qualification_denominator_or_parent_fork_rejected(self):
  for k,v in(("parents_n",1),("child_n",0),("inventory",self.mr)):
   with self.subTest(key=k):
    q=copy.deepcopy(self.q);q[k]=v
    with self.assertRaises(ValueError):g.qualification_core(q,g.local_bytes,self.source)
 def test_29_terminal_numeric_GPU_duplicate_and_wrong_owner_rejected(self):
  row=self.q["actual_remote_terminal"]["row"];g.terminal_shape(row,"999999")
  for token in("cpu=0","cpu=1,cpu=1","cpu=1,gres/gpu=0,gres/gpu:a100=1"):
   a=copy.deepcopy(self.proof["allocation"]);a["scheduler_record"]=a["scheduler_record"].replace("cpu=1,mem=16G",token)
   with self.subTest(token=token),self.assertRaises(ValueError):m.allocation_shape(a,"999999")
  for idx,value in((4,"cpu=1,gres/gpu=1"),(4,"cpu=1,cpu=1"),(4,"cpu=x"),(5,"other"),(7,"cpu"),(8,"unrelated")):
   with self.subTest(idx=idx,value=value):
    wrong=list(row);wrong[idx]=value
    with self.assertRaises(ValueError):g.terminal_shape(wrong,"999999")
 def test_30_opaque_blob_JSON_and_unknown_payload_receipt_rejected(self):
  g.validate_payloads(self.man,self.entries,self.plan,self.children,g.local_bytes,self.proof["baseline_tree_entries"])
  blob=next(x for x in self.children if x["relative_name"].startswith("blobs/"));data=g.obj(blob["canonical"],g.local_bytes);self.assertNotIn("path",data)
  fake=dict(data,path="unapproved",sha256="a"*64,bytes=1);alter=self.dump("altered_payload.json",fake)
  children=copy.deepcopy(self.children);next(x for x in children if x["relative_name"]==blob["relative_name"])["canonical"]=alter
  with self.assertRaises(ValueError):g.validate_payloads(self.man,self.entries,self.plan,children,g.local_bytes,self.proof["baseline_tree_entries"])
 def test_31_actual_core_validate_package_extract_and_indexed_export_restore(self):
  old=m.load("export_existing_software_fixture",m.D/"test_final_delivery_composer.py");fixture=old.ExactContextContracts();fixture.setUp()
  try:
   ctx,mapping,parent,children=fixture.toy();config_r=fixture.config(parent,children,mapping);config=m.read(config_r["path"]);api=m.load("export_actual_core",m.LIB/"delivery_core_v2.py")
   gate_r=config["gates"]["source_release"]["receipt"];gate=m.read(gate_r["path"]);gate["commit"]=self.head;Path(gate_r["path"]).write_text(json.dumps(gate));config["gates"]["source_release"]["receipt"]=m.rec(gate_r["path"])
   files={item["receipt"]["path"]:item for item in config["files"]}
   files[gate_r["path"]]=dict(receipt=config["gates"]["source_release"]["receipt"],classification="EVIDENCE")
   for r in self.q["required_receipts"]:files[r["path"]]=dict(receipt=r,classification="EVIDENCE")
   qr=self.dump("qualification_for_archive.json",self.q);files[qr["path"]]=dict(receipt=qr,classification="EVIDENCE")
   config["files"]=list(files.values());config_r=fixture.file("export_config.json",json.dumps(config).encode())
   old_reader=ctx.VerifiedContextReader(mapping,api.read);reader=g.ExportContextReader(self.q,self.result(),g.local_bytes,old_reader);original=api.read
   check_output=api.subprocess.check_output
   def redirected(argv,*args,**kwargs):
    if len(argv)>2 and argv[:2]==["git","-C"]and argv[2]==str(m.R/"source"):argv=list(argv);argv[2]=str(self.repo)
    return check_output(argv,*args,**kwargs)
   with mock.patch.object(api.subprocess,"check_output",side_effect=redirected):
    m.validate_archive_context(api,config_r["path"],str(self.d/"validation.json"),reader,dict(SYNTHETIC_SOFTWARE_ONLY=True))
   self.assertIs(api.read,original);api.package(str(self.d/"validation.json"),str(self.d/"package"),1)
   package_r=m.rec(self.d/"package"/"packaging_receipt.json");api.extract(package_r["path"],str(self.d/"restored_package"));pkg=m.read(package_r["path"]);root=self.d/"restored_package"
   index={g.rid(e["receipt"]):root/e["relative"]for e in pkg["manifest"]}
   def read(r):return index[g.rid(r)].read_bytes()
   g.verify_qualification(qr,read,restore=True,expected_source=self.source);self.assertEqual(g.local_bytes(self.mr),index[g.rid(self.mr)].read_bytes())
  finally:fixture.tearDown()
 def test_32_real_core_failure_restores_reader_and_no_context_acceptance(self):
  old=m.load("export_existing_failure_fixture",m.D/"test_final_delivery_composer.py");fixture=old.ExactContextContracts();fixture.setUp()
  try:
   ctx,mapping,parent,children=fixture.toy(unknown=True);config=fixture.config(parent,children,mapping);api=m.load("export_actual_failure_core",m.LIB/"delivery_core_v2.py");original=api.read
   reader=g.ExportContextReader(self.q,self.result(),g.local_bytes,ctx.VerifiedContextReader(mapping,api.read))
   with fixture.git_fixture(api),self.assertRaises(ValueError):m.validate_archive_context(api,config["path"],str(self.d/"badvalidation.json"),reader,{})
   self.assertIs(api.read,original);self.assertFalse((self.d/"badvalidation_context.json").exists())
  finally:fixture.tearDown()
