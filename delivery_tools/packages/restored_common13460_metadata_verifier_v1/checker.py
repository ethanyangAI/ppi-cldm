#!/usr/bin/env python3
"""Post-extraction exact-index-only13460/J6 metadata checker. No writer or scoring."""
import argparse,copy,datetime,hashlib,importlib.util,json,os,re,stat,subprocess,sys,unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/24_benchmark_delivery"
D=Path(__file__).absolute().parent;USER="u21111210118"
FILES=("checker.py","test_checker.py","checker_cpu.sbatch","HANDOFF.md")
TESTS=32
JOB_NAME="test9_restored_common13460_metadata"
SOFTWARE="RESTORED_COMMON13460_METADATA_VERIFIER_SOFTWARE_CPU_ACCEPTED_NOT_REAL_RESTORE"
CONTENT="RESTORED_COMMON13460_AND_J6_EXACT_INDEX_METADATA_CONTENT_ACCEPTED_NOT_SCIENCE"
SCOPE="RESTORED_METADATA_ONLY_NOT_SCIENCE_COST_PUBLICATION_OR_ACTIVE"
def pin(rel,n,h):return dict(path=str(R/rel),bytes=n,sha256=h)
COMPOSER_A=pin("steps/24_benchmark_delivery/runs/final_composer_contracts_13377/acceptance.json",19236,"51e1c79fa10accd8d86576ac217c0dc70d476dd9e6b16554dc978b06fc3557e5")
READER=pin("steps/24_benchmark_delivery/frozen/final_delivery_composer_v6_restoreindex1_fixturefix2_13377/code/restored_index_scope.py",34228,"9dec8043bcd8b44394869791f8046aff3f2787a491d8a285fcbc56a4c5e62fac")
CORE=pin("steps/24_benchmark_delivery/frozen/history_policy_13223/code/delivery_core_v2.py",21981,"eb46c9adf772433e06851f2328f47bd5b2b11a101288d97cce9424cea718eb06")
A13460=pin("steps/24_benchmark_delivery/runs/common_root_receipt_metadata_amendment_13460/acceptance.json",17771,"33631050f201ddae3870a52250bc84092c27fd71113394607c7e24c7a3a38146")
P=R/"steps/24_benchmark_delivery/submissions/formal_common_pending_from13422_primary_claim/root_submission.json"
TERMINAL_SEAL=R/"steps/24_benchmark_delivery/submissions/common13460_actual_metadata_amendment_terminal_seal/receipt.json"
J6=R/"steps/24_benchmark_delivery/submissions/root_gpu_journal/0006_common_controller_metadata_amendment_13460.json"
ADD=("raw_sbatch_stdout","raw_sbatch_stderr")
AMEND_NAMES=("amendment.py","test_amendment.py","amendment_cpu.sbatch","HANDOFF.md")
COST_NAMES={"root_gpu_cost_audit.py","test_root_gpu_cost_audit.py","root_gpu_cost_cpu.sbatch","HANDOFF.md"}
COMMON_NAMES={"common_review_successor.py","test_common_review_successor.py","successor_bootstrap.py","common_review_cpu.sbatch","common_review_gpu.sbatch","intrinsic_clearance.py","HANDOFF.md"}
def need(v,msg):
 if not v:raise ValueError(msg)
def lexical(p):
 raw=os.fspath(p);need(isinstance(raw,str)and raw.startswith("/")and all(x not in("","..",".")for x in raw.split("/")[1:]),"Absolute lexical path without traversal required");return Path(raw)
def local(p):
 p=lexical(p);need(p.is_relative_to(R)and p.resolve()==p,"Own CODE/control path outside authority or symlink");return p
def identity(r):return(r["path"],r["bytes"],r["sha256"])
def shape(r):
 need(isinstance(r,dict)and set(r)=={"path","bytes","sha256"}and type(r["bytes"])is int and r["bytes"]>=0 and re.fullmatch("[0-9a-f]{64}",r.get("sha256","")),"Exact three-field full identity required");lexical(r["path"]);return r
def rec(p):
 p=local(p);need(p.is_file()and not p.is_symlink()and not(p.stat().st_mode&0o222),"Readonly owned CODE/control required")
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def exact(r):
 shape(r);need(rec(r["path"])==r,"Qualified CODE/control bytes drift");return Path(r["path"]).read_bytes()
def parse_json(b):
 def pairs(items):
  result={}
  for k,v in items:need(k not in result,"Duplicate JSON key forbidden");result[k]=v
  return result
 def constant(v):raise ValueError("Nonfinite JSON constant forbidden: "+v)
 return json.loads(b,object_pairs_hook=pairs,parse_constant=constant)
def jbytes(v):return(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode()
def dump(p,v):
 p=local(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("xb")as f:f.write(jbytes(v));f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 return rec(p)
def load(name,r):
 exact(r);p=Path(r["path"]);spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);need(Path(m.__file__).absolute()==p,"Executing module differs");return m
def tres(text):
 d={}
 for part in text.split(","):
  need("="in part,"Allocated TRES missing/malformed");k,v=part.split("=",1);need(k and v and k not in d,"Duplicate/empty TRES");d[k]=v
 need(d.get("cpu","").isdigit()and int(d["cpu"])>=1,"Positive numeric allocated CPU required")
 for k,v in d.items():
  if k.startswith("gres/gpu"):need(re.fullmatch(r"gres/gpu(?::[A-Za-z0-9_.-]+)?",k)and v.isdigit()and int(v)==0,"GPU allocation/malformed namespace forbidden")
 return d
def cpu():
 jid=os.environ.get("SLURM_JOB_ID","");need(jid.isdigit(),"Actual CPU before any hashes/content/imports")
 for k,v in {"CUDA_VISIBLE_DEVICES":"","JAX_PLATFORMS":"cpu","PYTHONNOUSERSITE":"1","PYTHONDONTWRITEBYTECODE":"1","OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1","MKL_NUM_THREADS":"1"}.items():need(os.environ.get(k)==v,"Pure CPU isolation differs")
 need("PYTHONPATH"not in os.environ,"PYTHONPATH injected")
 raw=subprocess.check_output(["scontrol","show","job",jid,"-o"],text=True)
 rows=[x for x in raw.splitlines()if re.search(r"\bJobId="+jid+r"(?:\s|$)",x)];need(len(rows)==1,"One actual CPU record")
 pairs=re.findall(r"(\w+)=(\S*)",rows[0]);keys={"JobId","JobName","JobState","UserId","Account","Partition","NumCPUs","TRES","AllocTRES"}
 need(all(sum(k==key for k,_ in pairs)<=1 for key in keys),"Duplicate live scheduler field");f=dict(pairs)
 need(f.get("JobName")==JOB_NAME and f.get("JobState")=="RUNNING"and f.get("UserId","").startswith(USER+"(")and f.get("Account")==USER and f.get("Partition")=="organ"and f.get("NumCPUs")=="1","Actual named CPU1 owner/account/organ required")
 ds=[tres(f[k])for k in("TRES","AllocTRES")if k in f];need(ds and all(x["cpu"]=="1"for x in ds)and(len(ds)==1 or ds[0]==ds[1]),"Actual CPU1/TRES agreement required")
 return dict(job_id=jid,allocated_CPUs=1,allocated_GPUs=0,selected_scheduler_record=rows[0])
def same_json(a,b):
 if type(a)is not type(b):return False
 if isinstance(a,dict):return set(a)==set(b)and all(same_json(a[k],b[k])for k in a)
 if isinstance(a,list):return len(a)==len(b)and all(same_json(x,y)for x,y in zip(a,b))
 return a==b
def pair_lists(original,frozen,names):
 need(len(original)==len(frozen)==len(names)and [Path(r["path"]).name for r in original]==list(names)and [Path(r["path"]).name for r in frozen]==list(names),"Whole source universe/order differs")
 need(all((a["bytes"],a["sha256"])==(b["bytes"],b["sha256"])for a,b in zip(original,frozen)),"Original/frozen source byte identities differ")
def code_qualification():
 a=parse_json(exact(COMPOSER_A));need(a.get("schema")=="final-composer-software.v6"and a.get("status")=="FINAL_DELIVERY_COMPOSER_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_ARCHIVE_ACCEPTANCE"and a.get("actual_CPU_job_id")=="13377"and a.get("original_owned_pre_and_post_byte_readback_PASS")is True,"Actual accepted Composer13377 software required")
 s=a["source"];need(set(s)=={"composer","existing_API_dependencies","context_API_dependencies"}and [len(s[k])for k in("composer","existing_API_dependencies","context_API_dependencies")]==[12,15,14],"Composer whole12+15+14 code universe required")
 rs=[r for rows in s.values()for r in rows];need(READER in s["composer"]and CORE in s["existing_API_dependencies"],"Pinned StrictIndex/core not in tested composer")
 for r in rs:exact(r)
 c=parse_json(exact(a["contracts"]));need(c.get("status")=="PASS"and c.get("tests_run")==130 and c.get("failures")==0 and c.get("errors")==0 and same_json(c.get("tested_source"),s)and c.get("all_owned_and_context_python_compile_PASS")is True and c.get("all_launchers_bash_syntax_PASS")is True,"Saved130/source qualification differs; no rerun")
 exact(c["log"])
 return dict(accepted_composer=COMPOSER_A,composer_contracts=a["contracts"],composer_contract_log=c["log"],qualified_code_sources=rs,reader=READER,core=CORE,original130_not_rerun=True)
def input_bytes(scope,r):shape(r);return scope.verify(r).read_bytes()
def input_json(scope,r):return parse_json(input_bytes(scope,r))
def source_set(scope,rows,n,names=None):
 need(isinstance(rows,list)and len(rows)==n and len({r["path"]for r in rows})==n,"Exact unique source count required")
 if names is not None:need({Path(r["path"]).name for r in rows}==set(names),"Source names differ")
 for r in rows:input_bytes(scope,r)
def select_index(scope,path):
 keys=scope.paths.get(str(path),[]);need(len(keys)==1,"Unknown ownSHA requires one unambiguous explicit full index identity")
 need(keys[0]in scope.rows,"Required journal must be an actual index row")
 return scope.rows[keys[0]][0]
def counts(scope,r,n,source=None):
 c=input_json(scope,r);need(c.get("status")=="PASS"and type(c.get("tests_run"))is int and c["tests_run"]==n and type(c.get("failures"))is int and c["failures"]==0 and type(c.get("errors"))is int and c["errors"]==0 and type(c.get("skipped",0))is int and c.get("skipped",0)==0,"Saved contracts counts differ")
 if source is not None:need(same_json(c.get("tested_source_files"),source),"Saved owned contracts source differs")
 input_bytes(scope,c["log"]);return c
def validate_metadata(scope,policy):
 """Only indexed original INPUTs. Fixture policy is available solely to the owned test module; CLI uses REAL."""
 need(str(scope.authority)==policy["authority"],"Metadata policy must equal package authority")
 a=input_json(scope,policy["acceptance"])
 need(a.get("schema")=="common13423-controller-metadata-amendment-acceptance.v1"and a.get("status")=="COMMON13423_ADDITION_ONLY_CONTROLLER_METADATA_CPU_ACCEPTED_NOT_SCIENCE_COST_OR_NEW_GPU"and a.get("scope")=="METADATA_ONLY_NOT_SCIENCE_COST_OR_NEW_GPU"and a.get("actual_CPU_job_id")=="13460","Exact amendment13460 metadata scope required")
 alloc=a["allocation"];need(alloc.get("job_id")=="13460"and type(alloc.get("allocated_CPUs"))is int and alloc["allocated_CPUs"]==1 and type(alloc.get("allocated_GPUs"))is int and alloc["allocated_GPUs"]==0,"Amendment owned CPU metadata differs")
 for k in("compiled_owned_Python","bash_syntax_passed","original_source_prepost_equal","original_and_frozen_sources_byte_identical","all_control_prepost_bytes_and_metadata_equal","original_all_fields_preserved","canonical_parent_mode_restored","no_journal_write"):need(a.get(k)is True,"Required amendment proof flag: "+k)
 for k in("new_GPU_submission","technical_GPU_rerun","science_accepted","cost_closure_accepted","source_or_settings_changed","default_changed","Git_changed","ACTIVE_changed"):need(a.get(k)is False,"Forbidden metadata scope flag: "+k)
 need(a.get("only_added_keys")==list(ADD)and a.get("whole_OWN_source_n")==4,"Exactly two aliases/whole4 required")
 oldr=a["old_identity"]["readonly_archive"];newr=a["new_canonical"];cr=a["candidate_archive"]
 need(newr["path"]==policy["canonical"]and a["old_identity"]["logical_original_path"]==policy["canonical"],"Canonical logical path differs")
 oldb=input_bytes(scope,oldr);newb=input_bytes(scope,newr);cb=input_bytes(scope,cr)
 need(len(oldb)==policy["old_bytes"]and len(newb)==policy["new_bytes"]and newb==cb and(newr["bytes"],newr["sha256"])==(cr["bytes"],cr["sha256"]),"Actual old/new/candidate byte identities differ")
 need(a["old_identity"]["observed_bytes"]==oldr["bytes"]and a["old_identity"]["observed_sha256"]==oldr["sha256"],"Scalar old identity must equal real readonly archive")
 old=parse_json(oldb);new=parse_json(newb)
 need(set(new)==set(old)|set(ADD)and not(set(old)&set(ADD))and all(same_json(old[k],new[k])for k in old),"Only two keys/type/list-order-preserving addition allowed")
 need(new["raw_sbatch_stdout"]==old["raw_stdout"]and new["raw_sbatch_stderr"]==old["raw_stderr"]and old["raw_stdout"]=="13423\n"and old["raw_stderr"]==""and type(old["array_job_id"])is str and old["array_job_id"]=="13423","Exact actual parsable raw aliases/13423 required")
 need(type(old["concurrency_cap"])is int and old["concurrency_cap"]==2 and len(old["indices"])==268 and all(type(x)is int and 0<=x<288 for x in old["indices"])and old["indices"]==sorted(set(old["indices"])),"Pending268/cap2 identity differs")
 fact=input_json(scope,a["factual_submit_receipt"]);need(type(fact.get("returncode"))is int and fact["returncode"]==0 and same_json(fact.get("argv"),old["submit_argv"])and fact.get("stdout")==old["raw_stdout"]and fact.get("stderr")==old["raw_stderr"],"Factual rc0/raw/fullargv differs")
 source_set(scope,a["source_files"],4,AMEND_NAMES);source_set(scope,a["original_executing_sources"],4,AMEND_NAMES);pair_lists(a["original_executing_sources"],a["source_files"],AMEND_NAMES)
 need(a["original_source_entry"]==a["original_executing_sources"][0]and a["executing_frozen_entry"]==a["source_files"][0],"Actual original/frozen entry differs")
 source_set(scope,a["external_contract_source_files"],11)
 syntax=input_json(scope,a["owned_source_syntax"]);snap=input_json(scope,a["source_snapshot"]);counts(scope,a["contracts"],20,a["source_files"])
 need(syntax.get("compile_owned_Python")is True and type(syntax.get("bash_returncode"))is int and syntax["bash_returncode"]==0 and same_json(syntax["source_files"],a["source_files"])and syntax["bash_argv"]==["bash","-n",str(Path(a["source_files"][0]["path"]).parent/"amendment_cpu.sbatch")],"Owned compile/bash/source evidence differs")
 need(snap["syntax"]==a["owned_source_syntax"]and same_json(snap["original_executing_sources"],a["original_executing_sources"])and same_json(snap["frozen_source_files"],a["source_files"])and same_json(snap["allocation"],a["allocation"]),"Bootstrap snapshot fork")
 cost=input_json(scope,a["accepted_COST_software"]);common=input_json(scope,a["accepted_Common_software"])
 need(cost.get("status")=="ROOT_GPU_COST_AUDITOR_SOFTWARE_CPU_ACCEPTED"and common.get("status")=="COMMON_SUCCESSOR_SOFTWARE_SOURCE_CPU_ACCEPTED_FUTURE_FORMAL_PREPARATION_PENDING","Saved Cost/Common software status differs")
 source_set(scope,cost["source"],4,COST_NAMES);source_set(scope,common["source"]["successor"],7,COMMON_NAMES)
 need(same_json(cost["source"]+common["source"]["successor"],a["external_contract_source_files"]),"External4+7 provenance differs");counts(scope,cost["contracts"],76);counts(scope,common["contracts"],58)
 pre=input_json(scope,a["preflight"]);need(old["preflight"]==a["preflight"]and pre.get("status")=="COMMON_SUCCESSOR_CPU_PREFLIGHT_ACCEPTED_ROOT_PENDING_ONLY_GPU_SUBMISSION_REQUIRED"and pre.get("no_inference")is True and pre.get("root_submission_performed")is False and pre["root_pending_job_indices"]==old["indices"]and same_json(pre["source"]["successor"],common["source"]["successor"]),"Actual metadata preflight/source/indices differs")
 entry=next(r for r in common["source"]["successor"]if Path(r["path"]).name=="common_review_successor.py");launcher=next(r for r in common["source"]["successor"]if Path(r["path"]).name=="common_review_gpu.sbatch")
 need(old["entry"]==entry and old["launcher"]==launcher and old["submit_argv"]==["sbatch","--parsable","--export=ALL,COMMON_SUCCESSOR_ENTRY="+entry["path"],"--array="+",".join(map(str,old["indices"]))+"%2",launcher["path"],a["preflight"]["path"]],"Original full source-bound rootargv differs")
 tx=input_json(scope,a["transaction_receipt"]);diff=input_json(scope,a["amendment"])
 need(tx.get("schema")=="common13423-addition-only-atomic-transaction.v1"and diff.get("schema")=="common13423-controller-metadata-addition-only.v1"and tx.get("scope")==a["scope"]==diff.get("scope"),"Transaction/diff scope differs")
 for v in(tx,diff):
  need(same_json(v["old_identity"],a["old_identity"])and v["candidate_archive"]==cr and same_json(v["transaction"],diff["transaction"]),"Transaction/archive fork")
 need(diff["new_canonical"]==newr and diff["transaction_receipt"]==a["transaction_receipt"]and diff["actual_factual_submit_receipt"]==a["factual_submit_receipt"]and diff["added_fields"]=={k:new[k]for k in ADD}and diff.get("all_original_fields_exactly_preserved")is True,"Diff/current/factual/only2 fork")
 t=tx["transaction"]
 for k in("committed","current_new_verified","parent_mode_restored"):need(t.get(k)is True,"Transaction not accepted: "+k)
 need(t.get("rollback_performed")is False and t.get("rollback_conflict")is False and t.get("cleanup_errors")==[]and t["logical_target_path"]==policy["canonical"],"Transaction rollback/cleanup/target differs")
 need(t["replacement_metadata"]["path"]==policy["canonical"]and t["replacement_metadata"]["size"]==len(newb)and t["replacement_metadata"]["mode"]==0o444 and type(t["replacement_inode"])is int and t["replacement_metadata"]["inode"]==t["replacement_inode"],"Known original replacement inode/readonly/size differs")
 need(t["parent_before"]["mode"]==t["parent_after"]["mode"]==0o555 and all(same_json(t["parent_before"][k],t["parent_after"][k])for k in("path","device","inode","uid","gid")),"Original parent restoration identity differs")
 need(diff["legacy_COST_expected_rejection"]==dict(type="ValueError",message="Actual raw parsable submission differs/missing",expected=True)and diff.get("legacy_Common_contract_PASS")is True and same_json(diff["proposed_contracts"],diff["current_contracts"]),"Legacy/proposed/current API observations differ")
 probes=diff["current_contracts"];need(probes.get("no_suites_rerun")is True and probes["cost"]["job_id"]=="13423"and probes["cost"]["indices"]==old["indices"]and probes["cost"]["expected_allocation_count"]==268 and probes["cost"]["preflight"]==a["preflight"]and probes["cost"]["launcher"]==launcher and probes["common"]==dict(job_id="13423",launcher=launcher),"Actual original contract returned different metadata identity")
 for key,jid,name,ncpu in(("cost","13277","ppi_root_gpu_cost_cpu",1),("common","13269","ppi_common_successor_cpu",2)):
  v=a["actual_producer_terminal"][key];capture=input_json(scope,v["actual_capture"]);record=v["record"];raw=capture["stdout"]
  need(type(capture.get("returncode"))is int and capture["returncode"]==0 and not capture["stderr"].strip()and record["raw_line"]in raw.splitlines(),"Saved producer raw capture differs")
  cols=record["raw_line"].split("|");need(len(cols)==9 and cols[:7]==[jid,name,USER,USER,"organ","COMPLETED","0:0"]and cols[7].isdigit()and int(cols[7])==record["elapsed_seconds"]and tres(cols[8])["cpu"]==str(ncpu)and record["allocated_CPUs"]==ncpu and record["allocated_GPUs"]==0,"Saved actual producer terminal metadata differs")
 j5r=a["journal_0005_unchanged"];j5=input_json(scope,j5r);j6r=select_index(scope,policy["journal6"]);j6=input_json(scope,j6r)
 need(j5.get("schema")==j6.get("schema")=="root-current-gpu-submission-journal.v1"and j5.get("authority_root")==j6.get("authority_root")==policy["authority"]and j5.get("scope_start_utc")==j6.get("scope_start_utc")=="2026-10-11T14:25:00Z","Exact journal authority/scope required")
 need(set(j6)==set(j5)|{"metadata_only_common_controller_amendment_CPU_qualifications"}and j6["previous_journal_path"]==j5r["path"]and all(same_json(j6[k],j5[k])for k in j5 if k!="previous_journal_path"),"J6 only new qualification/previous linkage; exact prefix required")
 need(j6["metadata_only_common_controller_amendment_CPU_qualifications"]==[policy["acceptance"]]and j5["metadata_only_controller_amendment_CPU_qualifications"]==[a["previous13315_amendment_preserved"]],"Separate13460 qualification or retained13315 list differs")
 need(j5["entries"]==a["declared_root_GPU_submission_journal_entries_before_and_after"]==diff["journal_entries_unchanged"]and len(j5["entries"])==4 and [x["submission_id"]for x in j5["entries"]]==["formal13260","e2e_design_13304","e2e_evaluate_13311","formal_common_13423"]and j5["entries"][-1]["receipt_path"]==policy["canonical"],"Four-entry order/identity/universe differs")
 previous=input_json(scope,a["previous13315_amendment_preserved"]);need(previous.get("schema")=="root-controller-metadata-amendment-CPU-qualification.v1"and previous.get("status")=="ROOT_ACTUAL_EVALUATE_CONTROLLER_SINGLE_DESCRIPTOR_ADDITION_CPU_ACCEPTED"and previous.get("actual_job_id")=="13311"and previous["allocation"].get("slurm_job_id")=="13315"and previous["allocation"].get("allocated_CPU_count")==1 and previous["allocation"].get("allocated_GPU_count")==0,"Previous13315 metadata qualification must remain distinct")
 for key,n in(("unchanged_three_claim_files",3),("unchanged_three_other_GPU_controllers",3)):
  need(len(a[key])==n and a[key]==diff[key],"Unchanged control receipt proof fork")
  for r in a[key]:input_bytes(scope,r)
 need(a["unchanged_three_claim_files"][0]==a["factual_submit_receipt"]and [r["path"]for r in a["unchanged_three_other_GPU_controllers"]]==[e["receipt_path"]for e in j5["entries"][:3]],"Claim or other GPU-controller identity differs")
 sealr=select_index(scope,policy["terminal_seal"]);seal=input_json(scope,sealr)
 need(seal.get("schema")=="common-metadata-amendment-terminal-metadata-only-seal.v1"and seal.get("status")=="ACTUAL_TERMINAL_METADATA_READBACK_PASS_NOT_NEW_COST_OR_SCIENCE_ACCEPTANCE"and seal.get("actual_acceptance_CPU_stdout_descriptor")==policy["acceptance"]and seal.get("current_canonical_descriptor_from_ownedCPU")==newr and seal.get("original_5096_archive_from_ownedCPU")==oldr,"Actual terminal13460/A/current/archive seal linkage differs")
 cap=seal["actual_terminal"];need(type(cap.get("returncode"))is int and cap["returncode"]==0 and cap["stderr"]=="","Actual terminal capture failure")
 rows=[x for x in cap["stdout"].splitlines()if x.strip()];need(len(rows)==1,"Unique actual terminal13460 row")
 v=rows[0].split("|");need(len(v)==10 and v[:7]==["13460","test9_common13423_metadata_amendment_v1",USER,USER,"organ","COMPLETED","0:0"]and v[7].isdigit()and v[8]=="1"and tres(v[9])["cpu"]=="1","Actual13460 terminal CPU1/GPU0 owner evidence differs")
 need(cap["argv"]==["sacct","-j","13460","--allocations","--noheader","--parsable2","--format=JobID,JobName%128,User,Account,Partition,State,ExitCode,ElapsedRaw,AllocCPUS,AllocTRES"],"Actual13460 terminal request differs")
 need(seal.get("file_count")==13 and len(seal["files_before"])==len(seal["files_after"])==13 and seal.get("bytes_inode_mtime_unchanged")is True and seal.get("only_two_added_fields")is True and seal.get("no_new_GPU_submission")is True and seal.get("full_cost_and_science_pending")is True,"Terminal metadata seal scope differs")
 for before,after in zip(seal["files_before"],seal["files_after"]):
  need(all(same_json(before[k],after[k])for k in("path","bytes","inode","mtime_ns"))and after["mode"]=="0o444","Original metadata-only terminal seal changed bytes/inode/mtime")
  r=select_index(scope,before["path"]);need(r["bytes"]==before["bytes"],"Terminal-sealed metadata denominator differs");input_bytes(scope,r)
 return dict(status=CONTENT,scope=SCOPE,accepted_amendment=policy["acceptance"],journal6=j6r,journal5=j5r,actual13460_terminal_seal=sealr,old_archive=oldr,new_canonical=newr,candidate_archive=cr,metadata_relationships_independently_checked=True,only_two_aliases=True,old_fields_types_and_list_order_preserved=True,separate13315_and13460_qualifications=True,scientific_recomputation_performed=False,cost_closed=False,new_GPU=False,ACTIVE_changed=False)
def extraction_marker_guard(pkg,root,package_receipt,m,expected_authority):
 need(m.get("status")=="RESTORED_HASHES_VERIFIED_CONTENT_RECOMPUTATION_PENDING"and m.get("package")==package_receipt and m.get("authority_root")==expected_authority and m.get("restore_root")==str(root)and type(m.get("files_verified"))is int and m["files_verified"]==len(pkg["manifest"]),"Exact unchanged-core extraction control required")
def restore_boundary(pkg,root,out,expected_authority):
 root=lexical(root);out=lexical(out);authority=lexical(expected_authority)
 need(pkg.get("authority_root")==str(authority)and root!=authority and root.resolve()==root and root.is_dir()and out.is_relative_to(root)and out!=root and out.resolve()==out and not out.exists(),"Real isolated restore/new absent out root required")
def restore_scope(reader,package_receipt,root,out,owned,software_control=None):
 pkg=parse_json(exact(package_receipt));root=local(root);out=local(out)
 restore_boundary(pkg,root,out,str(R))
 marker=rec(root/"RESTORE_HASH_ACCEPTANCE.json");m=parse_json(exact(marker))
 extraction_marker_guard(pkg,root,package_receipt,m,str(R))
 controls=[package_receipt,marker]+([software_control]if software_control is not None else[])
 base=reader.StrictIndex(pkg,root,out,controls=controls,owned=owned)
 config=input_json(base,pkg["config"]);aliases={}
 if config.get("resource_aliases")is not None:aliases=input_json(base,config["resource_aliases"])
 scope=reader.StrictIndex(pkg,root,out,aliases=aliases,controls=controls,owned=owned)
 input_bytes(scope,software_control)if software_control is not None else None
 input_bytes(scope,pkg["config"])
 if config.get("resource_aliases")is not None:input_bytes(scope,config["resource_aliases"])
 return scope,pkg,marker
def own(original,frozen):
 pair_lists(original,frozen,FILES)
 for r in original+frozen:exact(r)
 return True
def archived_composer(scope,code):
 a=input_json(scope,COMPOSER_A)
 need(a.get("schema")=="final-composer-software.v6"and a.get("status")=="FINAL_DELIVERY_COMPOSER_SOFTWARE_CPU_ACCEPTED_NO_SCIENCE_OR_ARCHIVE_ACCEPTANCE"and a.get("actual_CPU_job_id")=="13377"and a.get("original_owned_pre_and_post_byte_readback_PASS")is True,"Archived actual Composer130 qualification required")
 s=a["source"];rows=[r for values in s.values()for r in values]
 need([len(s[k])for k in("composer","existing_API_dependencies","context_API_dependencies")]==[12,15,14]and same_json(rows,code["qualified_code_sources"])and READER in s["composer"]and CORE in s["existing_API_dependencies"],"Archived Composer whole code identity differs")
 for r in rows:input_bytes(scope,r)
 ct=input_json(scope,a["contracts"]);need(ct.get("status")=="PASS"and ct.get("tests_run")==130 and ct.get("failures")==0 and ct.get("errors")==0 and same_json(ct.get("tested_source"),s)and ct.get("all_owned_and_context_python_compile_PASS")is True and ct.get("all_launchers_bash_syntax_PASS")is True,"Archived130/source contract evidence differs")
 input_bytes(scope,ct["log"])
def new_software_evidence(scope,sw,fs,sr):
 need(same_json(input_json(scope,sr),sw),"Execution control and archived software bytes must agree")
 for r in fs+sw["original_executing_sources"]:input_bytes(scope,r)
 pair_lists(sw["original_executing_sources"],fs,FILES)
 ct=counts(scope,sw["contracts"],TESTS)
 need(ct.get("source_files")==fs and ct.get("tested_source_files")==fs and ct.get("genuine_unchanged_core_package_extract")is True,"Actual new32 producer/source fields differ")
 snapshot=input_json(scope,sw["source_snapshot"])
 need(snapshot["frozen_source_files"]==fs and snapshot["original_executing_sources"]==sw["original_executing_sources"]and snapshot.get("compile_owned_Python")is True and type(snapshot.get("bash_returncode"))is int and snapshot["bash_returncode"]==0 and snapshot["allocation"]==sw["allocation"]and snapshot["bash_argv"]==["bash","-n",str(Path(fs[0]["path"]).parent/"checker_cpu.sbatch")],"Archived new software compile/snapshot proof")
 jid=sw["actual_CPU_job_id"];need(isinstance(jid,str)and jid.isdigit()and sw["allocation"].get("job_id")==jid and type(sw["allocation"].get("allocated_CPUs"))is int and sw["allocation"]["allocated_CPUs"]==1 and type(sw["allocation"].get("allocated_GPUs"))is int and sw["allocation"]["allocated_GPUs"]==0,"Exact software producer allocation link required")
 logical=Path(scope.authority)/"steps/24_benchmark_delivery/submissions"/("restored_common13460_metadata_software_"+jid+"_actual_terminal_seal")/"receipt.json"
 tr=select_index(scope,str(logical));terminal=input_json(scope,tr)
 need(terminal.get("schema")=="restored-common13460-metadata-software-terminal-seal.v1"and terminal.get("status")=="ACTUAL_TERMINAL_SOFTWARE_METADATA_READBACK_PASS_NOT_REAL_RESTORE"and terminal.get("software_acceptance_CPU_stdout_descriptor")==sr and terminal.get("source_files")==fs and terminal.get("metadata_only")is True,"Indexed software terminal/source/stdout binding differs")
 cap=terminal["actual_terminal"];argv=["sacct","-X","-n","-P","-j",jid,"--format=JobID,JobName%128,User%64,Account%64,Partition%64,State,ExitCode,ElapsedRaw,AllocTRES"]
 need(cap.get("argv")==argv and type(cap.get("returncode"))is int and cap["returncode"]==0 and cap.get("stderr")=="","Indexed software terminal request failed/differs")
 rows=[x for x in cap["stdout"].splitlines()if x.strip()];need(len(rows)==1,"Unique saved actual software terminal")
 v=rows[0].split("|");need(len(v)==9 and v[:7]==[jid,JOB_NAME,USER,USER,"organ","COMPLETED","0:0"]and v[7].isdigit()and tres(v[8])["cpu"]=="1","Indexed software terminal CPU1/GPU0/name/state differs")
 return tr
def write_scoped_output(scope,out,result):
 out=lexical(out);need(out==scope.out,"Only declared trusted new output root")
 scope.output(out).mkdir(exist_ok=False)
 target=scope.output(out/"acceptance.json")
 with target.open("xb")as f:
  #open registers its exact OUTPUT path before capturing the proof.
  result["strict_restored_index_proof"]=scope.proof()
  result["strict_restored_index_proof"]["verification_scope"]="REQUIRED_13460_METADATA_SOURCE_INPUTS_ONLY_FULL_RAW_IS_SEPARATE_PRIOR_GATE"
  f.write(jbytes(result));f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 need(not(scope.physical(target,"read").stat().st_mode&0o222),"Own new OUTPUT receipt must be readonly")
 return scope.rec(target)
def run_verify(args,allocation):
 # Only this accepted execution-control software JSON and current executing CODE
 # are external. All archived qualification/proof/source/log inputs are indexed.
 sr=rec(args.software);need(sr["sha256"]==args.software_sha,"Exact new checker software control required")
 sw=parse_json(exact(sr));need(sw.get("schema")=="restored-common13460-metadata-software.v1"and sw.get("status")==SOFTWARE and sw.get("production_restore_verified")is False and sw.get("compiled_owned_Python")is True and sw.get("bash_syntax_PASS")is True and sw.get("original_prepost_verified")is True and sw.get("no_GPU_submission")is True and sw.get("science_accepted")is False,"Actual new checker software execution qualification")
 fs=sw["source_files"];need(len(fs)==4 and [Path(r["path"]).name for r in fs]==list(FILES)and all(Path(r["path"]).parent==D for r in fs)and D==S/"frozen"/("restored_common13460_metadata_verifier_v1_"+sw["actual_CPU_job_id"])/"code"and fs[0]["path"]==str(Path(__file__).absolute()),"Production must execute actual software-qualified frozen OWN4")
 need(set(p.name for p in D.iterdir())==set(FILES)and not(D.stat().st_mode&0o222),"Exact readonly executing OWN4 directory universe")
 for r in fs:exact(r)
 code=sw["code_dependencies"];need(code["reader"]==READER and code["core"]==CORE and code["accepted_composer"]==COMPOSER_A,"Exact execution helper/compiler provenance")
 reader=load("metadata_checker_strictindex",READER)
 runtime=sw["conditional_core_runtime"];need(runtime["logical_executable"]==str(R/"env/core/bin/python")and runtime["logical_executable"]==sys.executable,"Exact software-qualified conditional core interpreter")
 reader.verify_runtime(runtime)
 pr=rec(args.package);need(pr["sha256"]==args.package_sha,"Exact packaging control SHA required")
 scope,pkg,marker=restore_scope(reader,pr,args.restore_root,args.out,fs+[READER],software_control=sr);scope.after(touched_only=True)
 terminal=new_software_evidence(scope,sw,fs,sr)
 archived_composer(scope,code)
 result=validate_metadata(scope,dict(acceptance=A13460,canonical=str(P),journal6=str(J6),terminal_seal=str(TERMINAL_SEAL),authority=str(R),old_bytes=5096,new_bytes=5157))
 scope.after(touched_only=True);reader.verify_runtime(runtime)
 for r in fs+[READER]:exact(r)
 out=Path(args.out)
 result.update(schema="restored-common13460-metadata-content.v1",actual_CPU_job_id=allocation["job_id"],allocation=allocation,checker_software_execution_control=sr,source_files=fs,code_dependencies=code,conditional_core_runtime=runtime,software_indexed_terminal_proof=terminal,package_control=pr,hash_extraction_control=marker,strict_restored_index_proof=scope.proof(),production_restore_verified=True,late_postarchive_receipt=True,archive_source_report_creation_prerequisite=False)
 ar=write_scoped_output(scope,out,result);print(json.dumps(dict(status=CONTENT,acceptance=ar),ensure_ascii=False))
def run_contracts(allocation,original,frozen,out,code):
 m=load("metadata_checker_tests",frozen[1]);m.CHECKER=sys.modules[__name__];m.READER=load("metadata_checker_fixture_reader",READER);m.CORE=load("metadata_checker_fixture_core",CORE)
 runtime=m.READER.runtime_descriptor(sys.executable);need(runtime["logical_executable"]==str(R/"env/core/bin/python"),"Exact conditional core interpreter");m.READER.verify_runtime(runtime)
 suite=unittest.defaultTestLoader.loadTestsFromModule(m);need(suite.countTestCases()==TESTS,"Actual new fixture definitions differ")
 with (out/"contracts.txt").open("x")as log:r=unittest.TextTestRunner(stream=log,verbosity=2).run(suite);log.flush();os.fsync(log.fileno());os.fchmod(log.fileno(),0o444)
 counts=dump(out/"contracts.json",dict(status="PASS"if r.wasSuccessful()else"FAIL",tests_run=r.testsRun,failures=len(r.failures),errors=len(r.errors),skipped=len(r.skipped),source_files=frozen,tested_source_files=frozen,log=rec(out/"contracts.txt"),genuine_unchanged_core_package_extract=True,scope="SYNTHETIC_METADATA_FIXTURES_ONLY_NOT_REAL_RESTORE"))
 need(r.wasSuccessful()and r.testsRun==TESTS and not r.skipped,"New software contracts failed")
 m.READER.verify_runtime(runtime)
 own(original,frozen)
 for r in code["qualified_code_sources"]+[COMPOSER_A,code["composer_contracts"],code["composer_contract_log"]]:exact(r)
 a=dump(out/"acceptance.json",dict(schema="restored-common13460-metadata-software.v1",status=SOFTWARE,actual_CPU_job_id=allocation["job_id"],allocation=allocation,source_files=frozen,original_executing_sources=original,original_and_frozen_sources_byte_identical=True,original_prepost_verified=True,contracts=counts,code_dependencies=code,source_snapshot=rec(out/"source_snapshot.json"),compiled_owned_Python=True,bash_syntax_PASS=True,conditional_core_runtime=runtime,production_restore_verified=False,science_accepted=False,no_GPU_submission=True,ACTIVE_changed=False))
 print(json.dumps(dict(status=SOFTWARE,acceptance=a),ensure_ascii=False))
def main():
 parser=argparse.ArgumentParser();sp=parser.add_subparsers(dest="mode",required=True);sp.add_parser("contracts");v=sp.add_parser("verify")
 for key in("software","software-sha","package","package-sha","restore-root","out"):v.add_argument("--"+key,required=True)
 args=parser.parse_args();allocation=cpu()
 if args.mode=="verify":run_verify(args,allocation);return
 need(D==S/"pending/restored_common13460_metadata_verifier_v1"and set(x.name for x in D.iterdir())==set(FILES)and not(D.stat().st_mode&0o222),"Exact readonly OWN4 original package required")
 original=[rec(D/n)for n in FILES];fd=S/"frozen"/("restored_common13460_metadata_verifier_v1_"+allocation["job_id"])/"code";fd.mkdir(parents=True,exist_ok=False)
 frozen=[]
 for r in original:
  p=fd/Path(r["path"]).name
  with p.open("xb")as f:f.write(exact(r));f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
  frozen.append(rec(p))
 fd.chmod(0o555);fd.parent.chmod(0o555);own(original,frozen)
 out=S/"runs"/("restored_common13460_metadata_software_"+allocation["job_id"]);out.mkdir(exist_ok=False)
 for r in frozen:
  if Path(r["path"]).suffix==".py":compile(exact(r),r["path"],"exec")
 b=subprocess.run(["bash","-n",str(fd/"checker_cpu.sbatch")],text=True,capture_output=True);need(b.returncode==0,"Owned launcher syntax")
 dump(out/"source_snapshot.json",dict(original_executing_sources=original,frozen_source_files=frozen,compile_owned_Python=True,bash_argv=b.args,bash_returncode=b.returncode,bash_stdout=b.stdout,bash_stderr=b.stderr,allocation=allocation))
 code=code_qualification();m=load("restored13460_metadata_sealed_checker",frozen[0])
 m.run_contracts(allocation,original,frozen,out,code)
if __name__=="__main__":main()
