#!/usr/bin/env python3
"""Two exact GitHub export namespaces; all bytes and Git objects are reverified.
No generic relative resolution, publication writes, live restore fallback or science.
"""
import argparse,base64,copy,hashlib,json,os,re,subprocess,urllib.request
from pathlib import Path
import final_delivery_composer as m

SCHEMA="exact-github-export-context-qualification.v1"
STATUS="EXACT_PUBLIC_EXPORT_MANIFEST_AND_FULL_COMMITTED_GIT_BLOB_CONTEXT_CPU_QUALIFIED"
REMOTE_SCHEMA="github-public-ref-commit-tree-readback.v1"
REMOTE_STATUS="ACTUAL_PUBLIC_REF_COMMIT_FULL_TREE_AND_WRITE_RESPONSES_CPU_READ_BACK"
REPOSITORY="ethanyangAI/ppi-cldm"
FIELDS={"source_inventory":"source_inventory.json","handoff_plan":"api_handoff_plan.json","delta_tree_payload":"delta_tree_payload.json"}
MODES={"100644":"blob","100755":"blob","120000":"blob","160000":"commit"}
HEX40=re.compile(r"[0-9a-f]{40}")
def need(v,msg):
 if not v:raise ValueError(msg)
def oid(kind,data):return hashlib.sha1(kind.encode()+b" "+str(len(data)).encode()+b"\0"+data).hexdigest()
def rid(r):return(r["path"],r["bytes"],r["sha256"])
def receipt(r):
 need(isinstance(r,dict)and isinstance(r.get("path"),str)and Path(r["path"]).is_absolute(),"Absolute qualified receipt required")
 need(isinstance(r.get("bytes"),int)and not isinstance(r["bytes"],bool)and r["bytes"]>=0 and isinstance(r.get("sha256"),str)and re.fullmatch("[0-9a-f]{64}",r["sha256"]),"Exact byte identity required")
 return r
def local_bytes(r):return m.verify(r,True).read_bytes()
def exact(r,read_bytes):
 receipt(r);data=read_bytes(r)
 need(isinstance(data,bytes)and len(data)==r["bytes"]and hashlib.sha256(data).hexdigest()==r["sha256"],"Qualified current/restored bytes differ: "+r["path"])
 return data
def obj(r,read_bytes):return json.loads(exact(r,read_bytes))
def repo_path(p):
 need(isinstance(p,str)and p and not p.startswith("/")and "\\"not in p and "\0"not in p,"Unsafe repository path")
 need(all(x not in("","..",".")for x in p.split("/"))and p.encode("utf-8").decode("utf-8")==p,"Unnormalized repository path")
 return p
def branch_name(p):
 repo_path(p);need(re.fullmatch(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*",p),"Explicit safe new branch name required");return p
def relative_payload(p):
 repo_path(p)
 need(p in FIELDS.values()or re.fullmatch(r"(?:blobs|trees)/[0-9a-f]{40}\.json",p),"Unrecognized exact export child name")
 return p
def child_receipt(root,r,check_filesystem=True):
 need(isinstance(r,dict)and {"path","bytes","sha256"}<=r.keys(),"Exact export child required")
 relative_payload(r["path"]);p=Path(root)/r["path"]
 # Check lexical spelling and every existing component before reading any child.
 need(Path(root).is_absolute()and Path(root).is_relative_to(m.R)and all(x not in('', '.', '..')for x in str(root).split('/')[1:]),'Exact authority export root required')
 if check_filesystem:m.safe(root);m.safe(p)
 return receipt(dict(r,path=str(p)))
def occurrences(value,trail=()):
 if isinstance(value,dict):
  if {"path","sha256"}<=value.keys():yield trail,value
  for k,v in value.items():yield from occurrences(v,trail+(str(k),))
 elif isinstance(value,list):
  for i,v in enumerate(value):yield from occurrences(v,trail+(str(i),))
def manifest_shape(manifest,root,manifest_r,check_filesystem=True):
 need(manifest.get("schema")=="github_exact_tree_export.v1"and manifest.get("status")=="READY_FOR_ROOT_REVIEW_NO_PUBLICATION_PERFORMED","Exact producer export schema/status required")
 need(manifest.get("repository_full_name")==REPOSITORY and manifest.get("source_clean_before_and_after")is True,"Approved public repository/clean export required")
 need(str(Path(root)/"export_manifest.json")==manifest_r["path"],"Manifest parent differs from explicit export root")
 for k in ("local_commit_sha","baseline_commit_sha","baseline_tree_sha","final_tree_sha"):need(HEX40.fullmatch(manifest.get(k,"")),"Exact Git identities required")
 children=[]
 for field,name in FIELDS.items():
  r=manifest[field];need(r["path"]==name,"Fixed export field/name differs");children.append(dict(field=[field],relative_name=name,canonical=child_receipt(root,r,check_filesystem)))
 paths=set(FIELDS.values());shas=set()
 for i,r in enumerate(manifest["object_payloads"]):
  sha=r.get("expected_git_sha");need(HEX40.fullmatch(sha or "")and r["path"]in("blobs/"+sha+".json","trees/"+sha+".json"),"Object payload/name/SHA mismatch")
  need(r["path"]not in paths and sha not in shas,"Duplicate export payload or object identity");paths.add(r["path"]);shas.add(sha)
  children.append(dict(field=["object_payloads",str(i)],relative_name=r["path"],canonical=child_receipt(root,r,check_filesystem)))
 allowed={tuple(x["field"])for x in children}|{("exporter",)}
 need({t for t,r in occurrences(manifest)}==allowed,"Unknown receipt field in exact export manifest")
 need(set(manifest["exporter"])=={"path","sha256"},"Producer source field changed")
 need(manifest["exporter"]=={k:m.EXPORTER_RECEIPT[k]for k in("path","sha256")},"Exact qualified immutable exporter source differs")
 return children
def inventory_shape(inventory):
 need(inventory.get("schema")=="github_source_inventory.v1"and set(inventory)=={"schema","entries"}and isinstance(inventory["entries"],list),"Exact source inventory schema required")
 entries=inventory["entries"];seen=set()
 for i,e in enumerate(entries):
  p=repo_path(e.get("path"));need(p not in seen,"Duplicate repository inventory path");seen.add(p)
  need(e.get("mode")in MODES and e.get("type")==MODES[e["mode"]]and HEX40.fullmatch(e.get("sha","")),"Unsupported inventory mode/type/Git identity")
  required={"path","mode","type","sha"}|({"bytes","sha256"}if e["type"]=="blob"else set())
  need(set(e)==required,"Unknown inventory metadata or receipt field")
  if e["type"]=="blob":receipt(dict(e,path="/qualified-placeholder"));need(e["bytes"]>=0,"Invalid inventory bytes")
 need({t for t,r in occurrences(inventory)}=={("entries",str(i))for i,e in enumerate(entries)if e["type"]=="blob"},"Unknown source inventory receipt")
 return entries
def tree_map(entries):
 root={};identities={}
 for e in entries:
  parts=repo_path(e["path"]).split("/");d=root
  for part in parts[:-1]:
   need(part not in d or isinstance(d[part],dict),"Git tree file/directory collision")
   d=d.setdefault(part,{})
  need(parts[-1]not in d,"Duplicate tree leaf or directory collision");d[parts[-1]]=(e["mode"],e["type"],e["sha"])
 def build(d,directory=''):
  rows=[]
  for n,v in d.items():
   if isinstance(v,dict):sha=build(v,(directory+"/"if directory else"")+n);mode="40000";sort=(n+"/").encode()
   else:mode,kind,sha=v;need(MODES.get(mode)==kind and HEX40.fullmatch(sha),"Invalid Git tree leaf");sort=n.encode()
   rows.append((sort,mode.encode()+b" "+n.encode()+b"\0"+bytes.fromhex(sha)))
  identities[directory]=oid("tree",b"".join(v for k,v in sorted(rows)));return identities[directory]
 build(root);return identities
def tree_oid(entries):return tree_map(entries)[""]
def git(repo,*argv):return subprocess.check_output(["git","-C",str(repo),*argv])
def git_entries(repo,commit):
 result=[]
 for raw in git(repo,"ls-tree","-r","-z",commit).split(b"\0"):
  if raw:
   head,path=raw.split(b"\t",1);mode,kind,sha=head.decode().split();result.append(dict(path=path.decode("utf-8"),mode=mode,type=kind,sha=sha))
 tree_oid(result);return result
def leaf_rows(rows):
 result=[]
 for r in rows:result.append({k:r[k]for k in("path","mode","type","sha")})
 return sorted(result,key=lambda x:x["path"])
def commit_shape(data,sha,tree,parents):
 need(oid("commit",data)==sha,"Raw public/baseline Git commit object SHA mismatch")
 header=data.split(b"\n\n",1)[0].splitlines()
 trees=[r[5:].decode()for r in header if r.startswith(b"tree ")]
 actual=[r[7:].decode()for r in header if r.startswith(b"parent ")]
 need(trees==[tree]and(actual==parents if parents is not None else True),"Raw commit tree or direct parent mismatch")
def response_maps(plan,captures,read_bytes,public_sha,branch):
 expected={c["payload"]:c for c in plan["blob_calls"]+plan["tree_calls"]};seen=set();capture_ids=set();maps=dict(blobs={},trees={});commit=None;ref=None
 need(isinstance(captures,list),"Actual write captures required")
 for cr in captures:
  c=obj(cr,read_bytes)
  need(c.get("schema")=="root-github-write-response-capture.v1"and c.get("root_owned")is True and c.get("repository_full_name")==REPOSITORY and c.get("capture_id")and c.get("captured_utc")and c.get("response_success")is True,"Actual root tool response provenance missing")
  need(c.get("opaque_connector_ids_status")=="UNAVAILABLE_FROM_CONNECTOR"and c.get("actual_tool_call_id")is None and c.get("actual_response_id")is None,"Opaque connector IDs must be honestly unavailable/null")
  need(c["capture_id"]not in capture_ids,"Duplicate root capture identity");capture_ids.add(c["capture_id"])
  raw=c["raw_response"];need(isinstance(raw,dict),"Unmodified actual response object required")
  original=obj(c["actual_tool_output"],read_bytes);need(not(isinstance(original,dict)and original.get("isError")is True),"Actual tool returned error")
  for part in c["response_json_pointer"]:original=original[int(part)]if isinstance(original,list)else original[part]
  encoding=c.get("response_value_encoding");need(encoding in("JSON_OBJECT","JSON_TEXT"),"Exact actual tool value encoding required")
  if encoding=="JSON_TEXT":need(isinstance(original,str),"Actual JSON text field required");original=json.loads(original)
  need(original==raw,"Normalized response differs from actual immutable tool output")
  operation=c["operation"];request=c["request"]
  need(c.get("actual_tool_name")=={"create_blob":"mcp__codex_apps__github_create_blob","create_tree":"mcp__codex_apps__github_create_tree","create_commit":"mcp__codex_apps__github_create_commit","create_branch":"mcp__codex_apps__github_create_branch"}.get(operation),"Actual writer tool name differs")
  if operation in("create_blob","create_tree"):
   name=c["export_payload_name"];need(name in expected and name not in seen,"Unexpected/duplicate actual API payload");seen.add(name);e=expected[name]
   need(operation==("create_blob"if name.startswith("blobs/")else"create_tree")and raw.get("sha")==e["expected_sha"],"Actual returned object SHA differs")
   need(request==obj(c["export_payload_receipt"],read_bytes),"Actual connector arguments differ from exact exported tool payload")
   maps["blobs"if operation=="create_blob"else"trees"][e["expected_sha"]]=raw["sha"]
  elif operation=="create_commit":
   need(commit is None and request.get("repository_full_name")==REPOSITORY and request.get("tree_sha")==plan["expected_final_tree_sha"]and request.get("parent_sha")==plan["public_parent_commit_sha"]and request.get("additional_parent_shas")in(None,[])and set(request)<=set(("repository_full_name","tree_sha","parent_sha","message","additional_parent_shas"))and isinstance(request.get("message"),str)and request["message"],"Actual public commit request differs")
   need(raw.get("sha")==public_sha and("tree"not in raw or raw["tree"].get("sha")==plan["expected_final_tree_sha"])and("parents"not in raw or[p["sha"]for p in raw["parents"]]==[plan["public_parent_commit_sha"]]),"Actual commit response identity/optional graph differs")
   commit=dict(sha=public_sha,tree_sha=request["tree_sha"],parent_shas=[request["parent_sha"]])
  elif operation=="create_branch":
   need(ref is None and set(request)<=set(("repository_full_name","branch_name","sha","base_ref"))and request.get("repository_full_name")==REPOSITORY and request.get("branch_name")==branch and request.get("sha")==public_sha and request.get("base_ref")is None,"Exact new branch tool arguments differ")
   need((raw.get("ref")=="refs/heads/"+branch and raw.get("object",{}).get("sha")==public_sha)or(raw.get("name")==branch and raw.get("commit",{}).get("sha")==public_sha),"Actual new branch response differs");ref=public_sha
  else:raise ValueError("Unrecognized actual write operation")
 need(seen==set(expected)and commit is not None and ref==public_sha,"Incomplete actual write-response universe")
 return dict(**maps,commit=commit)
def remote_content(proof,manifest,inventory,plan,read_bytes):
 need(proof.get("schema")==REMOTE_SCHEMA and proof.get("status")==REMOTE_STATUS and proof.get("root_owned")is True and proof.get("repository_full_name")==REPOSITORY,"Actual remote readback authority required")
 need(proof.get("manifest")==manifest["receipt"]and proof.get("private_commit")==manifest["data"]["local_commit_sha"]and proof.get("final_tree")==manifest["data"]["final_tree_sha"]and proof.get("baseline_commit")==manifest["data"]["baseline_commit_sha"],"Remote/export identity fork")
 root=obj(proof["request"],read_bytes);root_request(root,"readback")
 need(root.get("authorize_public_GET_and_exact_remote_fetch")is True and root.get("branch")==proof["branch"]and root.get("source_bundle")==proof["private_source_bundle"]and root.get("write_response_captures")==proof["write_response_captures"]and root.get("export",{}).get("manifest")==proof["manifest"]and root["export"].get("export_dir")==str(Path(proof["manifest"]["path"]).parent),"Actual readback root request/input fork")
 m.allocation_shape(proof["allocation"],proof["actual_CPU_job_id"])
 branch=branch_name(proof["branch"]);need("/"not in branch or all(branch.split("/")),"Invalid branch")
 need(proof["remote_ref"]=="refs/heads/"+branch and proof["fetched_ref"]=="refs/remotes/root-qualified/"+branch,"Exact fetched remote ref namespace required")
 urls={"ref":"/repos/"+REPOSITORY+"/git/ref/heads/"+branch,"commit":"/repos/"+REPOSITORY+"/git/commits/"+proof["public_commit"],"tree":"/repos/"+REPOSITORY+"/git/trees/"+proof["final_tree"]+"?recursive=1"}
 bodies={}
 for key,url in urls.items():
  r=proof["public_GET"][key];need(r["url"]=="https://api.github.com"+url and r["http_status"]==200 and r.get("captured_utc"),"Actual public GET URL/status/time mismatch")
  bodies[key]=obj(r["body"],read_bytes);exact(r["headers"],read_bytes)
 need(bodies["ref"].get("ref")==proof["remote_ref"]and bodies["ref"].get("object",{}).get("sha")==proof["public_commit"],"Actual remote ref differs")
 need(bodies["commit"].get("sha")==proof["public_commit"]and bodies["commit"].get("tree",{}).get("sha")==proof["final_tree"]and[p["sha"]for p in bodies["commit"].get("parents",[])]==[proof["baseline_commit"]],"Remote commit tree/parent differs")
 remote=bodies["tree"];need(remote.get("sha")==proof["final_tree"]and remote.get("truncated")is False,"Complete actual remote recursive tree required")
 leaves=[e for e in remote["tree"]if e["type"]!="tree"];need(leaf_rows(leaves)==leaf_rows(inventory),"Full remote tree/path/mode/type/blob parity failed")
 need(len({e["path"]for e in remote["tree"]})==len(remote["tree"]),"Duplicate remote tree row")
 need(tree_oid(leaves)==proof["final_tree"],"Remote root Git tree reconstruction differs")
 trees=tree_map(leaves);expected_dirs=[dict(path=p,mode="040000",type="tree",sha=sha)for p,sha in trees.items()if p]
 need(leaf_rows([e for e in remote["tree"]if e["type"]=="tree"])==leaf_rows(expected_dirs),"Remote complete directory tree rows differ")
 history=proof["private_bundle_verification"];need(history["argv"]==["git","-C",manifest["data"]["source_checkout"],"bundle","verify",proof["private_source_bundle"]["path"]]and history["returncode"]==0,"Actual private history bundle verification missing")
 for name in("stdout","stderr"):exact(history[name],read_bytes)
 need(proof["private_commit"]in {line.split()[0].decode()for line in exact(history["heads"],read_bytes).splitlines()},"Verified private history bundle lacks approved private HEAD")
 exact(proof["private_source_bundle"],read_bytes)
 maps=response_maps(plan,proof["write_response_captures"],read_bytes,proof["public_commit"],branch)
 need(obj(proof["normalized_API_responses"],read_bytes)==maps,"Normalized maps differ from actual raw responses")
 fetch=proof["fetch"];need(fetch["argv"]==["git","-C",manifest["data"]["source_checkout"],"fetch","--no-tags","https://github.com/"+REPOSITORY+".git",proof["remote_ref"]+":"+proof["fetched_ref"]]and fetch["returncode"]==0,"Actual authorized fetch argv/exit differs")
 for name in("stdout","stderr"):exact(fetch[name],read_bytes)
 need(fetch["resolved_commit"]==proof["public_commit"]and fetch["resolved_tree"]==proof["final_tree"]and fetch["parent_shas"]==[proof["baseline_commit"]],"Fetched object graph differs from actual public GET")
 commit_shape(exact(proof["public_commit_object"],read_bytes),proof["public_commit"],proof["final_tree"],[proof["baseline_commit"]])
 commit_shape(exact(proof["baseline_commit_object"],read_bytes),proof["baseline_commit"],manifest["data"]["baseline_tree_sha"],None)
 baseline=proof["baseline_tree_entries"];need(tree_oid(baseline)==manifest["data"]["baseline_tree_sha"],"Baseline tree metadata differs from raw baseline commit")
 readback=obj(proof["unchanged_verifier_readback"],read_bytes)
 need(readback.get("status")=="PASS"and readback.get("local_commit_sha")==proof["private_commit"]and readback.get("final_tree_sha")==proof["final_tree"]and readback.get("published_ref_verified")==proof["fetched_ref"]and readback.get("api_responses_verified")is True,"Actual unchanged verifier did not qualify publication")
 return maps,baseline
def validate_payloads(manifest,inventory,plan,children,read_bytes,baseline):
 need(plan.get("schema")=="github_exact_tree_handoff.v1"and plan.get("repository_full_name")==REPOSITORY and plan.get("expected_final_tree_sha")==manifest["final_tree_sha"]and plan.get("public_parent_commit_sha")==manifest["baseline_commit_sha"],"Handoff graph differs")
 lookup={r["relative_name"]:r["canonical"]for r in children}
 baseblobs={e["sha"]for e in baseline if e["type"]=="blob"};finalblobs={e["sha"]for e in inventory if e["type"]=="blob"}
 calls=plan["blob_calls"]+plan["tree_calls"];need(len({x["payload"]for x in calls})==len(calls),"Duplicate handoff payload")
 need({x["payload"]for x in calls}=={r["path"]for r in manifest["object_payloads"]},"Payload universe differs")
 need({c["expected_sha"]for c in plan["blob_calls"]}==finalblobs-baseblobs,"New versus baseline blob denominator differs")
 finaltrees=tree_map(inventory);basetrees=tree_map(baseline)
 need({c["expected_sha"]for c in plan["tree_calls"]}==set(finaltrees.values())-set(basetrees.values()),"Full dependency-ordered tree object denominator differs")
 for c in plan["tree_calls"]:need(c.get("directory")in finaltrees and finaltrees[c["directory"]]==c["expected_sha"]and c.get("tool")=="mcp__codex_apps__github_create_tree","Exact handoff tree directory/tool differs")
 for c in plan["blob_calls"]:need(c.get("tool")=="mcp__codex_apps__github_create_blob","Exact handoff blob tool differs")
 actualtrees={}
 for call in calls:
  p=obj(lookup[call["payload"]],read_bytes);sha=call["expected_sha"]
  need(p.get("repository_full_name")==REPOSITORY and sha==next(r["expected_git_sha"]for r in manifest["object_payloads"]if r["path"]==call["payload"]),"Actual payload identity differs")
  if call in plan["blob_calls"]:
   need(set(p)=={"repository_full_name","encoding","content"}and p["encoding"]=="base64","Exact opaque blob payload required")
   data=base64.b64decode(p["content"],validate=True);need(oid("blob",data)==sha,"API blob payload Git SHA differs")
  else:
   need(set(p)=={"repository_full_name","base_tree_sha","tree_elements"}and p["base_tree_sha"]is None,"Exact full tree payload required")
   entries=p["tree_elements"];need(len({e["path"]for e in entries})==len(entries),"Duplicate tree element")
   raw=[]
   for e in entries:
    need(set(e)=={"path","mode","type","sha"}and "/"not in repo_path(e["path"])and HEX40.fullmatch(e["sha"]),"Unsafe full tree payload entry")
    mode=e["mode"];kind=e["type"];need((mode=="040000"and kind=="tree")or MODES.get(mode)==kind,"Tree mode/type differs")
    raw.append(((e["path"]+("/"if kind=="tree"else"")).encode(),("40000"if kind=="tree"else mode).encode()+b" "+e["path"].encode()+b"\0"+bytes.fromhex(e["sha"])))
   need(oid("tree",b"".join(v for k,v in sorted(raw)))==sha,"API tree payload Git SHA differs");actualtrees[sha]=True
 for e in inventory:
  if e["type"]=="commit":need(next((b for b in baseline if b["path"]==e["path"]),None)=={k:e[k]for k in("path","mode","type","sha")},"New/modified gitlink lacks separate object qualification")
 expected_delta=[];base={e["path"]:e for e in baseline};final={e["path"]:{k:e[k]for k in("path","mode","type","sha")}for e in inventory}
 for path in sorted(set(base)|set(final)):
  if base.get(path)!=final.get(path):expected_delta.append(dict(base[path],sha=None)if path not in final else final[path])
 delta=obj(lookup["delta_tree_payload.json"],read_bytes)
 need(delta==dict(repository_full_name=REPOSITORY,base_tree_sha=manifest["baseline_tree_sha"],tree_elements=expected_delta),"Exact baseline delta differs")
 need(manifest["changed_path_count"]==len(expected_delta)and manifest["source_file_count"]==len(inventory)and manifest["new_blob_object_count"]==len(plan["blob_calls"])and manifest["new_tree_object_count"]==len(plan["tree_calls"])and manifest["total_blob_bytes"]==sum(e.get("bytes",0)for e in inventory),"Export denominators differ")
 # No receipt-like schema expansion for plan/delta/tree/blob payload metadata.
 for name,r in lookup.items():
  if name!="source_inventory.json":need(not list(occurrences(obj(r,read_bytes))),"Unexpected nested receipt in exported API payload/plan")
def all_receipts(value):
 result={}
 for trail,r in occurrences(value):
  receipt(r);old=result.get(r["path"]);need(old is None or rid(old)==rid(r),"Conflicting proof receipt identity");result[r["path"]]=r
 return list(result.values())
def evidence_inputs(remote,sw,contracts,read_bytes):
 rows=all_receipts(remote)+all_receipts(sw)+all_receipts(contracts)
 for cr in remote["write_response_captures"]:rows+=all_receipts(obj(cr,read_bytes))
 if "request"in remote:rows+=all_receipts(obj(remote["request"],read_bytes))
 return rows
def terminal_shape(r,job):
 need(len(r)==9 and r[0]==job,"Exact numeric terminal row required");tokens={}
 for t in r[4].split(","):
  if t:
   k,v=t.split("=",1);need(k not in tokens,"Duplicate allocation TRES");tokens[k]=v
 need(r[1]=="COMPLETED"and r[2]=="0:0"and r[3]=="1"and tokens.get("cpu")=="1"and r[5:8]==["u21111210118","u21111210118","organ"]and r[8]=="ppi_final_composer_v6_restoreindex1","Actual qualified terminal CPU1/GPU0 readback required")
 for k,v in tokens.items():
  if k.startswith("gres/gpu"):need(v.isdecimal()and int(v)==0,"Readback allocated GPU")
 return dict(row=r,allocated_GPUs=0,allocated_CPUs=1)
def terminal_cpu(job):
 need(isinstance(job,str)and job.isdecimal(),"Actual numeric readback CPU job required")
 fmt="JobIDRaw,State,ExitCode,AllocCPUS,AllocTRES,User%64,Account%64,Partition%64,JobName%100"
 raw=subprocess.check_output(["sacct","-n","-X","-P","-j",job,"--format="+fmt],text=True)
 rows=[x.split("|")for x in raw.splitlines()if x.strip()];rows=[r for r in rows if r[0]==job]
 need(len(rows)==1,"One actual terminal readback job required");r=rows[0];checked=terminal_shape(r,job)
 return dict(**checked,raw_sacct=raw)
def qualification_core(q,read_bytes,expected_source=None):
 need(q.get("schema")==SCHEMA and q.get("status")==STATUS and q.get("scope")=="PUBLIC_GIT_SOURCE_EVIDENCE_ONLY"and q.get("raw_JSON_changed")is False and q.get("live_restore_fallback_allowed")is False,"Exact export-context qualification required")
 if expected_source is not None:need(q["source"]==expected_source,"Whole executing producer/helper/library source fork")
 for r in q["source"]["composer"]+q["source"]["existing_API_dependencies"]+q["source"]["context_API_dependencies"]:exact(r,read_bytes)
 sw=obj(q["software"],read_bytes);contracts=obj(sw["contracts"],read_bytes)
 need(sw.get("schema")=="final-composer-software.v6"and sw.get("status")==m.SOFTWARE_STATUS and sw["source"]==q["source"]and contracts.get("tested_source")==q["source"]and contracts.get("tests_run")==126 and contracts.get("status")=="PASS"and contracts.get("errors")==0 and contracts.get("failures")==0 and contracts.get("all_owned_and_context_python_compile_PASS")is True and contracts.get("all_launchers_bash_syntax_PASS")is True,"Actual V6 software126/current source prerequisite failed")
 exact(contracts["log"],read_bytes)
 need(sw.get("original_owned_pre_and_post_byte_readback_PASS")is True and len(sw.get("original_executing_sources",[]))==len(m.FILES),"Actual original owned-source before/after qualification missing")
 sealed={Path(r["path"]).name:(r["bytes"],r["sha256"])for r in q["source"]["composer"]}
 need({Path(r["path"]).name for r in sw["original_executing_sources"]}==set(m.FILES),"Original software source universe differs")
 for r in sw["original_executing_sources"]:need((r["bytes"],r["sha256"])==sealed[Path(r["path"]).name],"Original vs frozen software bytes differ");exact(r,read_bytes)
 need(sw["original_source_entry"]==next(r for r in sw["original_executing_sources"]if Path(r["path"]).name=="composer_bootstrap.py"),"Original software entry must be its exact executing bootstrap")
 exact(sw["original_source_entry"],read_bytes)
 manifest=obj(q["manifest"],read_bytes);children=manifest_shape(manifest,q["export_dir"],q["manifest"],read_bytes is local_bytes)
 need(children==q["children"],"Qualified exact field/index child mapping fork")
 for e in children:exact(e["canonical"],read_bytes)
 inventory_r=next(e["canonical"]for e in children if e["field"]==["source_inventory"])
 need(q["inventory"]==inventory_r,"Exact qualified inventory parent differs")
 entries=inventory_shape(obj(inventory_r,read_bytes))
 need(len(q["blob_observations"])==sum(e["type"]=="blob"for e in entries),"Full final blob observation denominator differs")
 blobs={}
 for row in q["blob_observations"]:
  i=row["index"];need(isinstance(i,int)and not isinstance(i,bool)and 0<=i<len(entries)and row["entry"]==dict({k:v for k,v in entries[i].items()if k!="path"},repository_path=entries[i]["path"])and entries[i]["type"]=="blob","Exact inventory field/index fork")
  e=entries[i];data=exact(row["canonical"],read_bytes)
  need(len(data)==e["bytes"]and hashlib.sha256(data).hexdigest()==e["sha256"]and oid("blob",data)==e["sha"],"Raw committed Git blob content differs")
  need(row["canonical"]["path"]==str(Path(q["blob_directory"])/(e["sha"]+".gitblob")),"Canonical Git blob location differs")
  need(i not in blobs,"Duplicate inventory blob observation");blobs[i]=row
 need(set(blobs)=={i for i,e in enumerate(entries)if e["type"]=="blob"}and tree_oid(entries)==manifest["final_tree_sha"],"Entire committed source tree denominator/SHA differs")
 remote=obj(q["remote_readback"],read_bytes);need(remote["source"]==q["source"]and remote["software"]==q["software"]and remote["private_source_bundle"]==q["private_source_bundle"],"Remote executing source/software/private history bundle differs from qualification");plan=obj(next(e["canonical"]for e in children if e["field"]==["handoff_plan"]),read_bytes)
 maps,baseline=remote_content(remote,dict(data=manifest,receipt=q["manifest"]),entries,plan,read_bytes)
 validate_payloads(manifest,entries,plan,children,read_bytes,baseline)
 checked=terminal_shape(q["actual_remote_terminal"]["row"],remote["actual_CPU_job_id"]);need(all(q["actual_remote_terminal"].get(k)==v for k,v in checked.items()),"Saved terminal/readback allocation fork")
 need(q["actual_remote_terminal"]["raw_sacct"].strip().split("|")==q["actual_remote_terminal"]["row"],"Saved raw terminal accounting differs")
 need(q["parents_n"]==2 and q["child_n"]==len(children)and q["blob_path_n"]==len(blobs)and q["unique_blob_n"]==len({entries[i]["sha"]for i in blobs}),"Qualified count fork")
 for r in q["required_receipts"]:exact(r,read_bytes)
 needed=all_receipts({k:v for k,v in q.items()if k!="required_receipts"})+evidence_inputs(remote,sw,contracts,read_bytes)
 need(len({rid(r)for r in q["required_receipts"]})==len(q["required_receipts"])and {rid(r)for r in q["required_receipts"]}=={rid(r)for r in needed},"Qualified required-file universe incomplete")
 return manifest,entries,children,blobs
def verify_qualification(r,read_bytes=None,restore=False,expected_source=None):
 need(not restore or(read_bytes is not None and read_bytes is not local_bytes),"Restore requires explicit indexed-only reader; default/explicit live reader forbidden")
 reader=local_bytes if read_bytes is None else read_bytes;q=obj(r,reader)
 result=qualification_core(q,reader,expected_source)
 if not restore:need(q["actual_remote_terminal"]==terminal_cpu(obj(q["remote_readback"],reader)["actual_CPU_job_id"]),"Fresh remote-readback terminal differs")
 for x in q["required_receipts"]:exact(x,reader)
 return q,result
def qualify(export,expected_commit,source,software,out,readback_result,private_bundle):
 need(readback_result.get("status")=="PASS"and readback_result.get("local_commit_sha")==expected_commit and readback_result.get("api_responses_verified")is True and readback_result.get("published_ref_verified")==export["published_ref"],"Actual unchanged GitHub verifier PASS required before view")
 manifest=obj(export["manifest"],local_bytes);need(manifest["source_checkout"]==str(m.R/"source"),"Approved current source checkout required");children=manifest_shape(manifest,export["export_dir"],export["manifest"])
 entries=inventory_shape(obj(next(e["canonical"]for e in children if e["field"]==["source_inventory"]),local_bytes))
 remote=obj(export["remote_readback"],local_bytes)
 need(remote["private_source_bundle"]==private_bundle and remote["normalized_API_responses"]==export["api_responses"]and remote["fetched_ref"]==export["published_ref"]and remote["source"]==source and remote["software"]==software and remote["private_commit"]==expected_commit,"Root exact actual readback inputs/source differ")
 actual=terminal_cpu(remote["actual_CPU_job_id"])
 directory=m.safe(out/"committed_git_blobs");directory.mkdir(exist_ok=False);obs=[];created={}
 for i,e in enumerate(entries):
  if e["type"]!="blob":continue
  if e["sha"]not in created:
   data=git(manifest["source_checkout"],"cat-file","blob",e["sha"]);need(oid("blob",data)==e["sha"],"Committed raw blob Git identity differs")
   p=directory/(e["sha"]+".gitblob");p.write_bytes(data);p.chmod(0o444);created[e["sha"]]=m.rec(p)
  obs.append(dict(index=i,entry=dict({k:v for k,v in e.items()if k!="path"},repository_path=e["path"]),canonical=created[e["sha"]]))
 directory.chmod(0o555)
 q=dict(schema=SCHEMA,status=STATUS,scope="PUBLIC_GIT_SOURCE_EVIDENCE_ONLY",source=source,software=software,private_source_bundle=private_bundle,manifest=export["manifest"],export_dir=export["export_dir"],inventory=next(e["canonical"]for e in children if e["field"]==["source_inventory"]),children=children,blob_directory=str(directory),blob_observations=obs,remote_readback=export["remote_readback"],actual_remote_terminal=actual,parents_n=2,child_n=len(children),blob_path_n=len(obs),unique_blob_n=len(created),raw_JSON_changed=False,live_restore_fallback_allowed=False)
 sw=obj(software,local_bytes);contracts=obj(sw["contracts"],local_bytes)
 q["required_receipts"]=all_receipts(q)+evidence_inputs(remote,sw,contracts,local_bytes)
 unique={rid(r):r for r in q["required_receipts"]};q["required_receipts"]=list(unique.values())
 qualification_core(q,local_bytes,source);need(m.sources()==source,"Whole executing source changed during materialization")
 return m.dump(out/"github_export_context_qualification.json",q)
class ExportContextReader:
 def __init__(self,q,result,read_bytes,base):
  self.q=q;self.result=result;self.bytes=read_bytes;self.base=base;self.used=set();self.edges=set()
 def __call__(self,path):
  path=str(path);manifest,entries,children,blobs=self.result
  if path not in(self.q["manifest"]["path"],self.q["inventory"]["path"]):return self.base(path)
  r=self.q["manifest"]if path==self.q["manifest"]["path"]else self.q["inventory"];raw=obj(r,self.bytes);self.used.add(path);view=copy.deepcopy(raw)
  if path==self.q["manifest"]["path"]:
   need(manifest_shape(raw,self.q["export_dir"],r,self.bytes is local_bytes)==children,"Manifest changed after qualification")
   for row in children:
    target=view
    for part in row["field"][:-1]:target=target[int(part)]if isinstance(target,list)else target[part]
    last=row["field"][-1];target[int(last)if isinstance(target,list)else last]=copy.deepcopy(row["canonical"]);self.edges.add((path,tuple(row["field"])))
  else:
   need(inventory_shape(raw)==entries,"Inventory changed after qualification")
   for i,row in blobs.items():
    view["entries"][i]=dict(entries[i],path=row["canonical"]["path"],original_repository_path=entries[i]["path"])
    self.edges.add((path,("entries",str(i))))
  return view
 def normalize_edge(self,r,parent,trail):
  if parent is None or parent["path"]not in(self.q["manifest"]["path"],self.q["inventory"]["path"]):return False,r,None
  expected_parent=self.q["manifest"]if parent["path"]==self.q["manifest"]["path"]else self.q["inventory"]
  need(rid(parent)==rid(expected_parent),"Qualified parent byte identity differs before dedup")
  path=parent["path"];t=tuple(trail);rows=self.q["children"]if path==self.q["manifest"]["path"]else[dict(field=["entries",str(x["index"])],canonical=x["canonical"])for x in self.q["blob_observations"]]
  if path==self.q["manifest"]["path"]and t==("exporter",):return False,r,None
  match=[x for x in rows if tuple(x["field"])==t];need(len(match)==1 and rid(r)==rid(match[0]["canonical"]),"Unauthorized exact export parent/field/index or identity")
  self.edges.add((path,t));return True,r,dict(scope="EXACT_QUALIFIED_GITHUB_EXPORT_FIELD",parent_identity=rid(parent),field=list(t))
 def require_both_used(self):
  expected={(self.q["manifest"]["path"],tuple(e["field"]))for e in self.q["children"]}|{(self.q["inventory"]["path"],("entries",str(x["index"])))for x in self.q["blob_observations"]}
  need(self.used=={self.q["manifest"]["path"],self.q["inventory"]["path"]}and self.edges==expected,"All exact export parents/fields/blobs must be observed")
  if hasattr(self.base,"require_both_used"):self.base.require_both_used()
  for r in self.q["required_receipts"]:exact(r,self.bytes)
 def proof(self):return dict(status="TWO_EXACT_EXPORT_NAMESPACES_OBSERVED_NO_RAW_REWRITE",parent_n=len(self.used),field_n=len(self.edges),all_blob_paths_observed=True,underlying=self.base.proof()if hasattr(self.base,"proof")else None)
def required(binding,read_bytes=None,restore=False,source=None):
 r=binding["github_export_context_qualification"];q,result=verify_qualification(r,read_bytes,restore,source)
 return q,result,[r]+q["required_receipts"]
def root_request(q,kind):
 need(q.get("schema")=="github-export-"+kind+"-request.v1"and q.get("root_owned")is True and q.get("repository_full_name")==REPOSITORY,"Explicit root GitHub source request required")
def write_bytes(p,data):
 m.safe(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("xb")as f:f.write(data)
 p.chmod(0o444);return m.rec(p)
def readback(q,source,software,request_r,out,allocation):
 root_request(q,"readback");need(q.get("authorize_public_GET_and_exact_remote_fetch")is True,"Root exact remote fetch authorization missing")
 export=q["export"];manifest=obj(export["manifest"],local_bytes);children=manifest_shape(manifest,export["export_dir"],export["manifest"])
 entries=inventory_shape(obj(next(e["canonical"]for e in children if e["field"]==["source_inventory"]),local_bytes))
 need(manifest["source_checkout"]==str(m.R/"source"),"Approved current private source checkout required")
 branch=branch_name(q["branch"]);repo=m.safe(manifest["source_checkout"]);private=manifest["local_commit_sha"]
 need(git(repo,"rev-parse","HEAD").decode().strip()==private and not git(repo,"status","--porcelain","--untracked-files=all").strip(),"Approved private HEAD/clean source required before remote fetch")
 captures=q["write_response_captures"]
 # The public commit response comes from actual root captures; GET must agree independently.
 commits=[obj(r,local_bytes)for r in captures if obj(r,local_bytes).get("operation")=="create_commit"];need(len(commits)==1,"One actual public commit response required");public=commits[0]["raw_response"]["sha"];need(HEX40.fullmatch(public),"Actual public commit SHA required")
 plan=obj(next(e["canonical"]for e in children if e["field"]==["handoff_plan"]),local_bytes)
 maps=response_maps(plan,captures,local_bytes,public,branch)
 for cr in captures:
  c=obj(cr,local_bytes)
  if c["operation"]in("create_blob","create_tree"):
   e=next(x for x in children if x["relative_name"]==c["export_payload_name"]);need(c["export_payload_receipt"]==e["canonical"],"Actual capture payload receipt fork")
 responses=m.dump(out/"normalized_API_responses.json",maps);gets={}
 from datetime import datetime,timezone
 for key,suffix in(("ref","git/ref/heads/"+branch),("commit","git/commits/"+public),("tree","git/trees/"+manifest["final_tree_sha"]+"?recursive=1")):
  url="https://api.github.com/repos/"+REPOSITORY+"/"+suffix
  req=urllib.request.Request(url,headers={"Accept":"application/vnd.github+json","User-Agent":"ppi-cldm-root-cpu-qualified-readback","X-GitHub-Api-Version":"2022-11-28"})
  with urllib.request.urlopen(req,timeout=60)as response:
   data=response.read();need(response.status==200,"Actual public REST GET unsuccessful")
   body=write_bytes(out/(key+".response.json"),data);headers=write_bytes(out/(key+".headers.txt"),str(response.headers).encode())
   gets[key]=dict(url=url,http_status=response.status,captured_utc=datetime.now(timezone.utc).isoformat(),body=body,headers=headers)
 remote="refs/heads/"+branch;fetched="refs/remotes/root-qualified/"+branch
 argv=["git","-C",str(repo),"fetch","--no-tags","https://github.com/"+REPOSITORY+".git",remote+":"+fetched]
 run=subprocess.run(argv,capture_output=True);logs={name:write_bytes(out/("fetch."+name),getattr(run,name))for name in("stdout","stderr")};need(run.returncode==0,"Actual public ref fetch failed")
 resolved=git(repo,"rev-parse",fetched).decode().strip();tree=git(repo,"rev-parse",fetched+"^{tree}").decode().strip();parents=git(repo,"show","-s","--format=%P",fetched).decode().strip().split()
 need(resolved==public and tree==manifest["final_tree_sha"]and parents==[manifest["baseline_commit_sha"]],"Actually fetched public graph differs")
 verifier=m.load("v5_actual_unchanged_github",m.LIB/"github_export_verify.py")
 accepted=verifier.verify(export["export_dir"],str(repo),maps,fetched);readback_r=m.dump(out/"unchanged_verifier_readback.json",accepted)
 proof=dict(schema=REMOTE_SCHEMA,status=REMOTE_STATUS,root_owned=True,repository_full_name=REPOSITORY,actual_CPU_job_id=os.environ["SLURM_JOB_ID"],allocation=allocation,source=source,software=software,request=request_r,manifest=export["manifest"],private_source_bundle=q["source_bundle"],private_commit=private,public_commit=public,final_tree=tree,baseline_commit=manifest["baseline_commit_sha"],branch=branch,remote_ref=remote,fetched_ref=fetched,public_GET=gets,write_response_captures=captures,normalized_API_responses=responses,unchanged_verifier_readback=readback_r,fetch=dict(argv=argv,returncode=run.returncode,resolved_commit=resolved,resolved_tree=tree,parent_shas=parents,**logs),public_commit_object=write_bytes(out/(public+".gitcommit"),git(repo,"cat-file","commit",public)),baseline_commit_object=write_bytes(out/(manifest["baseline_commit_sha"]+".gitcommit"),git(repo,"cat-file","commit",manifest["baseline_commit_sha"])),baseline_tree_entries=git_entries(repo,manifest["baseline_commit_sha"]))
 checked=subprocess.run(["git","-C",str(repo),"bundle","verify",str(m.verify(q["source_bundle"],True))],capture_output=True)
 need(checked.returncode==0,"Actual private source bundle verification failed")
 heads=git(repo,"bundle","list-heads",q["source_bundle"]["path"]);need(private in {line.split()[0].decode()for line in heads.splitlines()},"Actual private bundle missing approved HEAD")
 proof["private_bundle_verification"]=dict(argv=["git","-C",str(repo),"bundle","verify",q["source_bundle"]["path"]],returncode=checked.returncode,stdout=write_bytes(out/"bundle.stdout",checked.stdout),stderr=write_bytes(out/"bundle.stderr",checked.stderr),heads=write_bytes(out/"bundle.heads",heads))

 remote_content(proof,dict(data=manifest,receipt=export["manifest"]),entries,plan,local_bytes);validate_payloads(manifest,entries,plan,children,local_bytes,proof["baseline_tree_entries"])
 need(git(repo,"rev-parse","HEAD").decode().strip()==private and not git(repo,"status","--porcelain","--untracked-files=all").strip(),"Private HEAD/worktree changed during fetch")
 sw=obj(software,local_bytes);contracts=obj(sw["contracts"],local_bytes)
 for r in evidence_inputs(proof,sw,contracts,local_bytes):exact(r,local_bytes)
 need(m.sources()==source,"Executing source changed during actual remote readback")
 return m.dump(out/"remote_readback.json",proof)
def main():
 p=argparse.ArgumentParser();p.add_argument("mode",choices=("readback","qualify"));p.add_argument("--request",required=True);p.add_argument("--request-sha256",required=True);p.add_argument("--software",required=True);p.add_argument("--software-sha256",required=True);p.add_argument("--out",required=True);a=p.parse_args()
 allocation=m.cpu();source=m.sources();rr=m.rec(a.request);sr=m.rec(a.software);need(rr["sha256"]==a.request_sha256 and sr["sha256"]==a.software_sha256,"Exact root CLI request/software binding differs")
 m.software(sr,source);q=obj(rr,local_bytes);out=m.safe(a.out);out.mkdir(parents=True,exist_ok=False)
 try:
  if a.mode=="readback":result=readback(q,source,sr,rr,out,allocation)
  else:
   root_request(q,"qualify");exp=q["export"];verifier=m.load("v5_qualify_unchanged_github",m.LIB/"github_export_verify.py");check=verifier.verify(exp["export_dir"],str(m.R/"source"),obj(exp["api_responses"],local_bytes),exp["published_ref"]);result=qualify(exp,q["expected_commit"],source,sr,out,check,q["source_bundle"])
  print(json.dumps(result))
 except Exception as e:m.dump(out/"typed_incomplete.json",dict(status="GITHUB_EXPORT_CONTEXT_TYPED_INCOMPLETE_NO_PUBLICATION_OR_SCIENCE_ACCEPTANCE",reason_type=type(e).__name__,reason=str(e)));raise
if __name__=="__main__":main()
