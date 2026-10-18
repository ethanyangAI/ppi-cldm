#!/usr/bin/env python3
"""DIAGNOSTIC_ONLY: recheck seven exact identities and recorded BBF freezer inverse."""
import ast,hashlib,io,json,os,subprocess,sys,tokenize
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");STEP=R/"steps/24_benchmark_delivery"
BASE=STEP/"frozen/source_refresh_relative_v9_13307/code"
INPUT={"path":str(STEP/"runs/source_saved_byte_recovery_diagnostic_13310/diagnostic.json"),"bytes":75704,"sha256":"48ce0453db4927cacea9804354fc9b0f598ca598922ff778f0f2024debc4b1ea"}
BBF_TARGET={"path":str(R/"source/rebuild/bbf_input_diagnostic.py"),"bytes":23056,"sha256":"a0adf54bfca538dafa17adde810455f8d883354a28038d9c0d241246c87277d3"}
BBF_FROZEN={"path":str(R/"steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061/code/bbf_input_diagnostic.py"),"bytes":24842,"sha256":"d2eefb850802a0b93a6724051218c5e686d556c9358d08ab17c7a28dabc247ca"}
BBF_BUNDLE=R/"steps/23_common_review/bbf_diagnostics/frozen/bbf_common_13061/source_bundle.json"
BBF_FREEZER=R/"steps/23_common_review/bbf_diagnostics/code/freeze_bbf.py"
BBF_LAUNCHER=R/"steps/23_common_review/bbf_diagnostics/code/freeze_launcher.py"
PATCH_RECORDS=Path(__file__).resolve().parent/"historical_patch_records.json"
EXPECTED=[
 ('ROOT/"source/rebuild/benchmark_common_review.py"','Path(__file__).resolve().parent/"benchmark_common_review.py"'),
 ('ROOT/"vendor"/("IPSAE_"+REVISION[:12])/"ipsae.py"','Path(__file__).resolve().parent/"vendor/ipsae.py"')]
def need(v,message):
 if not v:raise ValueError(message)
def safe(p):
 p=Path(p);need(p.is_absolute()and p.is_relative_to(R)and p.resolve()==p and not p.is_symlink(),"Exact internal nonsymlink path required")
 need("/steps/22_matched_benchmark/formal_runs/"not in str(p)and "/steps/25_reference_free_e2e/runs/"not in str(p),"Current formal/E2E scientific reads forbidden")
 return p
sys.path.insert(0,str(BASE))
from delivery_core import cpu,rec
need(os.environ.get("SLURM_CPUS_PER_TASK")=="1"and os.environ.get("CUDA_VISIBLE_DEVICES")=="","PureCPU1 required")
allocation=cpu() # before any content hash/read
def exact(r):
 p=safe(r["path"]);need(p.is_file()and not(p.stat().st_mode&0o222),"Readonly actual proof/source required")
 need(rec(p)=={k:r[k]for k in ("path","bytes","sha256")},"Exact bytes/SHA differ")
 return p
def read_exact(r):
 p=exact(r);o=json.loads(p.read_text());exact(r);return o
def terminal(job,jobname):
 raw=subprocess.check_output(["sacct","-X","-j",job,"--noheader","--parsable2","--format=JobIDRaw,User%64,Account%64,Partition%64,JobName%100,State%40,ExitCode,AllocCPUS,AllocTRES%300"],text=True)
 rows=[x.split("|")for x in raw.splitlines()if x.strip()and x.split("|")[0]==job];need(len(rows)==1,"One exact historical root job row required")
 row=rows[0];need(row[1:8]==["u21111210118","u21111210118","organ",jobname,"COMPLETED","0:0","1"],"Historical CPU terminal ownership/state differs")
 tres={}
 for part in row[8].split(","):
  need("="in part,"Malformed historical TRES");k,v=part.split("=",1);need(k not in tres,"Duplicate TRES");tres[k]=v
 need(tres.get("cpu")=="1"and all(int(v)==0 for k,v in tres.items()if k.startswith("gres/gpu")),"Historical CPU1/GPU0 required")
 return dict(job_id=job,raw_sacct=raw,allocated_cpus=1,allocated_gpus=0,COMPLETED_exit_zero=True)
own=[rec(safe(Path(__file__).resolve())),rec(safe(Path(__file__).resolve().parent/"diagnostic.sbatch")),rec(safe(BASE/"delivery_core.py")),rec(safe(PATCH_RECORDS))]
for r in own:exact(r)
previous=read_exact(INPUT)
need(previous.get("schema")=="saved-source-exact-byte-recovery-diagnostic-only.v1"and previous.get("status")=="FINITE_EIGHT_SOURCE_IDENTITIES_SEARCHED_NO_SOURCE_OR_ALIAS_ACCEPTANCE"and previous.get("job_id")=="13310"and previous.get("actual_allocation",{}).get("job_id")=="13310"and previous.get("actual_allocation",{}).get("allocated_gpus")==0,"Actual13310 pureCPU diagnostic required")
need(previous.get("source_acceptance")is False and previous.get("new_alias_accepted")is False and previous.get("current_execution_authorized")is False and previous.get("matched_identity_count")==6 and previous.get("reconstructed_historical_identity_count")==1 and previous.get("unmatched_targets_after_found_original_and_reconstructed")==[BBF_TARGET],"Only declared BBF identity may remain unresolved")
history=terminal("13310","test9_saved_source_diagnostic_v1")
for r in previous["executed_source_files"]:exact(r)
registry=previous["original_five_alias_registry"];registry_json=read_exact(registry)
rows=previous["existing_five_declared_aliases"]
need(len(rows)==5 and len(registry_json["historical_exact_byte_aliases"])==5,"Original five registered history source rows required")
seven=[];proof_inputs=[INPUT,registry,*previous["executed_source_files"]]
for i,row in enumerate(rows):
 raw=registry_json["historical_exact_byte_aliases"][i]
 need(raw["logical_receipt"]==row["logical_receipt"]and raw["resolved_readonly_exact_byte_receipt"]==row["physical_receipt"]and raw["historical_report"]==row["historical_report"]and raw["original_mutable_path_hash_claimed_equal"]is False,"Original exact registered source alias differs")
 physical=row["physical_receipt"];logical=row["logical_receipt"]
 need((physical["bytes"],physical["sha256"])==(logical["bytes"],logical["sha256"]),"Registered byte identity differs")
 exact(physical);exact(row["historical_report"]);proof_inputs += [physical,row["historical_report"]]
 if logical in previous["targets"]:seven.append(dict(logical_receipt=logical,physical_receipt=physical,classification="FOUND_EXISTING_REGISTERED_EXACT_HISTORICAL_SOURCE",registered_parent=registry,registered_field=["historical_exact_byte_aliases",str(i)],new_alias_accepted=False))
for relative,size,sha in (
 ("steps/22_matched_benchmark/settings/pilot_v3/source/benchmark_runtime.py",36014,"f3726e2fbbede3678c029ffe3e3f3cac5b52a9826325459d8d3e6756ded505e7"),
 ("steps/22_matched_benchmark/settings/pilot_v5/source/benchmark_runtime.py",37816,"773dc1b7d2e0cbbfdaca8c021e07f70323012a3f2c70bcbd6d744bb0ca50fc50")):
 physical=dict(path=str(R/relative),bytes=size,sha256=sha);logical=dict(physical,path=str(R/"source/rebuild/benchmark_runtime.py"))
 need(logical in previous["targets"]and any(x["physical_content_receipt"]==physical and logical in x["matches_missing_receipts"]and x["readonly"]is True for x in previous["source_candidates"]),"Exact runtime source must already be actual13310 match")
 exact(physical);proof_inputs.append(physical);seven.append(dict(logical_receipt=logical,physical_receipt=physical,classification="FOUND_EXISTING_READONLY_EXACT_HISTORICAL_SOURCE",previous_actual_proof=INPUT,new_alias_accepted=False))
common=previous["recorded_common_reconstruction"]
need(common["classification"]=="RECONSTRUCTED_HISTORICAL_SOURCE_NOT_FOUND_ORIGINAL"and common["old_source_size_and_SHA_verified"]is True and common["forward_replay_byte_identical"]is True and common["historical_freezer_executed"]is False and common["reconstructed_source_executed"]is False and common["source_acceptance"]is False and common["current_execution_authorized"]is False,"Common reconstruction must preserve exact historical-only status")
original=common["original_logical_receipt"];physical=common["reconstructed_source"]
need(original in previous["targets"]and (original["bytes"],original["sha256"])==(physical["bytes"],physical["sha256"]),"Original exact common source identity differs")
for k in ("historical_bundle","recorded_freezer","frozen_source","reconstructed_source"):exact(common[k]);proof_inputs.append(common[k])
value=exact(physical).read_text();replay=value
need(len(common["exact_twelve_replacements"])==12,"Literal twelve common transforms required")
for a,b in common["exact_twelve_replacements"]:
 need(type(a)is str and type(b)is str and a and b and a!=b and replay.count(a)>0,"Recorded common transformation anchor differs")
 replay=replay.replace(a,b)
need(replay.encode()==exact(common["frozen_source"]).read_bytes(),"Repeated common forward replay differs")
seven.append(dict(logical_receipt=original,physical_receipt=physical,classification=common["classification"],previous_actual_reconstruction_proof=INPUT,recorded_freezer=common["recorded_freezer"],historical_bundle=common["historical_bundle"],frozen_source=common["frozen_source"],forward_replay_byte_identical=True,new_alias_accepted=False))
need(len(seven)==7 and len({(x["logical_receipt"]["path"],x["logical_receipt"]["bytes"],x["logical_receipt"]["sha256"])for x in seven})==7,"Exactly seven preceding byte identities required")
need(sorted([(r["path"],r["bytes"],r["sha256"])for r in previous["targets"]])==sorted([(x["logical_receipt"]["path"],x["logical_receipt"]["bytes"],x["logical_receipt"]["sha256"])for x in seven]+[(BBF_TARGET["path"],BBF_TARGET["bytes"],BBF_TARGET["sha256"])]),"Whole eight-identity denominator differs")
for p,size in ((BBF_FREEZER,3857),(BBF_LAUNCHER,4050),(BBF_BUNDLE,8124)):
 p=safe(p);need(p.is_file()and not(p.stat().st_mode&0o222)and p.stat().st_size==size,"Named recorded BBF source/metadata readonly size differs")
 proof_inputs.append(rec(p))
freezer_record=next(x for x in proof_inputs if x["path"]==str(BBF_FREEZER));launcher_record=next(x for x in proof_inputs if x["path"]==str(BBF_LAUNCHER));bundle_record=next(x for x in proof_inputs if x["path"]==str(BBF_BUNDLE))
bundle=read_exact(bundle_record)
need(bundle.get("status")=="BBF110_SCIENTIFIC_INPUTS_AND_SOURCE_CONTENT_ACCEPTED_AWAIT_NEW_BUDGET_GUARD_LAUNCHER"and bundle.get("cpu_job")=="13061"and bundle.get("scientific_jobs_exactly_unchanged")is True and bundle["source"]==BBF_FROZEN and bundle["source_files"][0]==BBF_FROZEN,"Exact BBF frozen-source metadata scope differs")
proof_inputs.append(BBF_FROZEN);frozen_bytes=exact(BBF_FROZEN).read_bytes()
# Shared literal statements are structurally parsed with AST, and decoded by
# the exact limited JavaScript quoted-string grammar present in these records.
# Nothing from the historical exec input is executed/evaluated.
def js_literal(token):
 need(len(token)>=2 and token[0]in ("'",'"')and token[-1]==token[0]and not token.startswith(token[0]*3),"Only simple JS quoted literal supported")
 result=[];i=1
 escapes={"n":"\n","r":"\r","t":"\t","b":"\b","f":"\f","v":"\v","\\":"\\","'":"'",'"':'"'}
 while i<len(token)-1:
  c=token[i]
  if c=="\\":
   i+=1;need(i<len(token)-1 and token[i]in escapes,"Unknown/nonshared JavaScript escape rejected");result.append(escapes[token[i]])
  else:
   need(c not in ("\n","\r",token[0]),"Unescaped JS quoted literal delimiter");result.append(c)
  i+=1
 return "".join(result)
def recorded_js_patches(receipt):
 data=read_exact(receipt)
 need(data.get("schema")=="exact-two-historical-BBF-patch-records-data-only.v1"and data.get("original_session_id")=="01a12917-8539-7e20-89ae-37dd9dcc35c1"and data.get("original_local_session_file")=="/Users/yangzijian/.codex/sessions/2026/10/11/rollout-2026-10-11T11-52-49-01a12917-8539-7e20-89ae-37dd9dcc35c1.jsonl"and data.get("recorded_tool_calls_executed")is False,"Only exact authorized two historical input records permitted")
 declarations=[
  (1381,"2026-10-11T05:06:04.414Z","ctc_00918a3c2e5efc41016acb192eb7048191a4013912e378d57f","call_1507b4e1755942269e8cf5d83799737f",'let c=load("bbf_diagnostic_code_v2");',10),
  (1408,"2026-10-11T05:07:12.719Z","ctc_00918a3c2e5efc41016acb197e379c81918ceebce2e037ab7f","call_695893637f52466ba2c6f5638ac69a8b",'let c=load("bbf_diagnostic_code_v3");',2)]
 need(len(data["records"])==2,"Exactly two historical input records required")
 patches=[];proofs=[]
 for row,decl in zip(data["records"],declarations):
  line,timestamp,item_id,call_id,start,wanted=decl
  need(row["record_line"]==line and type(row["raw_JSONL_record"])is str,"Authorized historical record identity differs")
  item=json.loads(row["raw_JSONL_record"]);payload=item["payload"];code=payload["input"];lines=code.splitlines()
  need(item["type"]=="response_item"and item["timestamp"]==timestamp and payload["type"]=="custom_tool_call"and payload["id"]==item_id and payload["call_id"]==call_id and payload["name"]=="exec"and type(code)is str and lines[0]==start,"Exact historical tool input metadata differs")
  statements=[(i+1,text)for i,text in enumerate(lines)if text.lstrip().startswith("c=")]
  need(len(statements)==wanted and all(text.startswith("c=c.replace(")for _,text in statements),"Only exact literal c.replace chain permitted")
  extracted=[]
  for innerline,text in statements:
   parsed=ast.parse(text);need(len(parsed.body)==1 and isinstance(parsed.body[0],ast.Assign),"One literal assignment statement required")
   node=parsed.body[0];value=node.value
   need(len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id=="c"and isinstance(value,ast.Call)and isinstance(value.func,ast.Attribute)and isinstance(value.func.value,ast.Name)and value.func.value.id=="c"and value.func.attr=="replace"and len(value.args)==2 and not value.keywords and all(isinstance(x,ast.Constant)and type(x.value)is str for x in value.args),"Only c.replace(two literal strings) AST permitted")
   tokens=[t.string for t in tokenize.generate_tokens(io.StringIO(text).readline)if t.type==tokenize.STRING]
   need(len(tokens)==2,"Implicit concatenation/multiple literals forbidden")
   pair=tuple(js_literal(t)for t in tokens);need(pair==tuple(x.value for x in value.args)and pair[0]and pair[1]and pair[0]!=pair[1]and "$"not in pair[1],"Shared JS/AST literal decoding or replacement expansion differs")
   extracted.append(dict(record_line=line,input_line=innerline,old=pair[0],new=pair[1],replace_semantics="JAVASCRIPT_LITERAL_FIRST_OCCURRENCE"));patches.append(pair)
  proofs.append(dict(record_line=line,timestamp=timestamp,tool_item_id=item_id,call_id=call_id,raw_record_sha256=hashlib.sha256(row["raw_JSONL_record"].encode()).hexdigest(),input_sha256=hashlib.sha256(code.encode()).hexdigest(),literal_patch_count=wanted,extracted_patches=extracted,historical_exec_input_executed=False))
 need(len(patches)==12,"Exact total10+2 historical transformations required")
 return patches,proofs

patch_receipt=next(x for x in own if x["path"]==str(PATCH_RECORDS));patches,patch_proofs=recorded_js_patches(patch_receipt)
# Parse the literal recorded copy/freeze transformation without executing any freezer.
tree=ast.parse(exact(freezer_record).read_text());nodes=[n for n in tree.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id=="source"]
need(len(nodes)==1,"One literal recorded BBF source transformation required")
def literal_chain(node):
 if isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and node.func.attr=="replace":
  need(len(node.args)==2 and not node.keywords,"Recorded BBF replace shape differs")
  base=literal_chain(node.func.value);pair=tuple(ast.literal_eval(a)for a in node.args);need(all(type(x)is str for x in pair),"Only literal recorded strings permitted");return base+[pair]
 need(isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and node.func.attr=="read_text"and isinstance(node.func.value,ast.Name)and node.func.value.id=="own"and not node.args and not node.keywords,"Recorded BBF source must originate in own.read_text")
 return []
transforms=literal_chain(nodes[0].value);need(transforms==EXPECTED,"Only exact two recorded BBF freezer transformations allowed")
candidate=frozen_bytes.decode("utf-8");reverse=[]
for index in reversed(range(len(EXPECTED))):
 a,b=EXPECTED[index];count=candidate.count(b);need(count>0,"Recorded BBF inverse anchor unavailable");reverse.append(dict(index=index,replacements=count));candidate=candidate.replace(b,a)
post_patch_source=candidate;post_patch_bytes=post_patch_source.encode("utf-8")
patch_reverse=[]
for index in reversed(range(len(patches))):
 a,b=patches[index];count=candidate.count(b);need(count>0,"Recorded historical JS inverse anchor unavailable")
 patch_reverse.append(dict(index=index,available_occurrences=count,replacements=1,replace_semantics="JAVASCRIPT_LITERAL_FIRST_OCCURRENCE"))
 candidate=candidate.replace(b,a,1)
raw=candidate.encode("utf-8");candidate_sha=hashlib.sha256(raw).hexdigest()
historical_forward=candidate;patch_forward=[]
for index,(a,b)in enumerate(patches):
 count=historical_forward.count(a);need(count>0,"Recorded historical JS forward anchor unavailable")
 patch_forward.append(dict(index=index,available_occurrences=count,replacements=1,replace_semantics="JAVASCRIPT_LITERAL_FIRST_OCCURRENCE"))
 historical_forward=historical_forward.replace(a,b,1)
need(historical_forward.encode("utf-8")==post_patch_bytes,"Historical first-occurrence forward replay differs from recorded freeze input")
forward=historical_forward;forward_log=[]
for index,(a,b)in enumerate(EXPECTED):
 count=forward.count(a);need(count>0,"Recorded BBF Python forward anchor unavailable");forward_log.append(dict(index=index,replacements=count,replace_semantics="PYTHON_LITERAL_ALL_OCCURRENCES"));forward=forward.replace(a,b)
need(forward.encode("utf-8")==frozen_bytes,"Whole historical12 plus Pythonfreeze2 forward replay differs from exact frozen source")
matched=len(raw)==BBF_TARGET["bytes"]and candidate_sha==BBF_TARGET["sha256"]
out=STEP/"runs"/("source_bbf_recorded_recovery_diagnostic_"+os.environ["SLURM_JOB_ID"]);out.mkdir(parents=True,exist_ok=False)
bbf=dict(status="RECONSTRUCTED_EXACT_HISTORICAL_BBF_SOURCE_NOT_CURRENT_EXECUTION"if matched else"RECORDED_HISTORICAL12_AND_FREEZER2_CHAIN_DOES_NOT_MATCH_TARGET23056",requested_logical_receipt=BBF_TARGET,historical_source_bundle=bundle_record,recorded_freezer=freezer_record,recorded_launcher_source=launcher_record,frozen_source=BBF_FROZEN,transforms=transforms,source_line=nodes[0].lineno,python_freeze_semantics="ALL_OCCURRENCES",reverse_log=reverse,forward_log=forward_log,historical_patch_records=patch_receipt,historical_patch_record_proofs=patch_proofs,historical_js_patch_semantics="FIRST_OCCURRENCE",historical_patch_reverse_log=patch_reverse,historical_patch_forward_log=patch_forward,post_historical_patch_source_bytes=len(post_patch_bytes),post_historical_patch_source_sha256=hashlib.sha256(post_patch_bytes).hexdigest(),historical_forward_replay_byte_identical=True,inverse_candidate_bytes=len(raw),inverse_candidate_sha256=candidate_sha,target_exact_bytes_and_SHA_matched=matched,forward_replay_byte_identical=True,reconstructed_source=None,candidate_current_execution_allowed=False,historical_freezers_executed=False,scientific_payload_read=False,new_alias_accepted=False,source_acceptance=False)
if matched:
 p=out/"reconstructed_historical_source"/(BBF_TARGET["sha256"]+"_bbf_input_diagnostic.py");p.parent.mkdir();p.write_bytes(raw);p.chmod(0o444);bbf["reconstructed_source"]=rec(p);exact(bbf["reconstructed_source"])
# Mismatched inverse is scalar metadata only, never saved as an authorized source.
for r in proof_inputs+own:exact(r)
result=dict(schema="bbf-recorded-source-recovery-diagnostic-only.v1",status="EXACT_PRECEDING_SEVEN_IDENTITIES_AND_ONLY_RECORDED_BBF_TRANSFORM_CPU_DIAGNOSED_NO_SOURCE_ACCEPTANCE",job_id=os.environ["SLURM_JOB_ID"],actual_allocation=allocation,executed_source_files=own,previous_actual_diagnostic=INPUT,previous_actual_terminal=history,whole_missing_identity_count=8,preceding_seven_byte_identities=seven,existing_all_five_formal_history_rows=rows,bbf_recorded_transform=bbf,all_eight_byte_identities_closed=matched,unresolved_source_identities=[]if matched else[BBF_TARGET],source_acceptance=False,new_alias_accepted=False,current_execution_authorized=False,default_changed=False,model_inference=False,formal_outputs_read=False,E2E_outputs_read=False,scientific_payload_read=False,historical_freezers_executed=False,scope="Source metadata and exact source bytes only. Two exact recorded JavaScript10+2 first-occurrence patch chains, then recorded Python freezer2 all-occurrence transforms; no extra source editing, guessed transformation or SHA search. Mismatch is unresolved, never waived.")
dest=out/"diagnostic.json";dest.write_text(json.dumps(result,indent=2)+"\n");dest.chmod(0o444)
print(json.dumps(dict(status=result["status"],diagnostic=rec(dest),all_eight_byte_identities_closed=matched,unresolved_source_identities=result["unresolved_source_identities"],source_acceptance=False)))
