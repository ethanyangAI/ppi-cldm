#!/usr/bin/env python3
"""Owned pure CPU fixed-window query probes; no cost/science acceptance."""
import argparse, importlib.util, json, os, re, subprocess, sys
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
S=R/"steps/24_benchmark_delivery"
F=S/"frozen/root_gpu_cost_v2_13277/code"
OWN=("diagnostic.py","diagnostic_cpu.sbatch","HANDOFF.md")
SW={"path":str(S/"runs/root_gpu_cost_contracts_13277/acceptance.json"),"bytes":3766,"sha256":"c0a5d380dc18d12fdfa0ded176a5b89374211827a4f85a9d3f50b922374241e8"}
LR={"path":str(S/"runs/root_gpu_cost_seal-ledger_13782/root_gpu_submission_ledger.json"),"bytes":2782,"sha256":"b4601b7acabf198d22bc949985fcb2f707df9b82049f24886d01449944adf998"}
FAIL=S/"runs/root_gpu_cost_audit_14178"
SEAL=S/"submissions/root_gpu_cost_audit14178_actual_failed_typed_metadata_terminal_seal/receipt.json"
REASON="Bounded time-universe query did not independently cover every actual GPU allocation"

PRIOR={"path":str(S/"runs/root_cost_universe_diagnostic_14448/diagnostic.json"),"bytes":34633,"sha256":"0c4542e66f42e8399f43f13aac09920f27d14f3f41dca822177431db379997f4"}
PRIOR_SEAL=S/"submissions/root_cost_universe_diagnostic14448_actual_metadata_terminal_seal/receipt.json"
PRIOR_DIR=S/"runs/root_cost_universe_diagnostic_14448"
PROBE_NAME="test9_root_cost_time_probe"

def saved_probe_parent(m,qualified,seal):
 m.verify(PRIOR,True);a=m.read(PRIOR["path"])
 sr=m.rec(m.verify(m.rec(PRIOR_SEAL),True));s=m.read(PRIOR_SEAL)
 m.need(sr["bytes"]==11478 and s["schema"]=="root-cost-universe-diagnostic-actual-terminal-metadata-only.v1" and s["status"]=="ACTUAL_DIAGNOSTIC_TERMINAL_METADATA_READBACK_PASS_NOT_COST_ACCEPTANCE","Exact actual14448 diagnostic terminal seal")
 m.need(s["actual_job_id"]=="14448" and s["diagnostic"]==PRIOR and s["software_acceptance"]==SW and s["ledger"]==LR and s["failed_terminal_seal"]==seal and s["software_source4"]==qualified,"Actual14448 full input/source linkage")
 m.need(s["diagnostic_only"] is True and s["metadata_only"] is True and s["no_cost_or_scientific_acceptance"] is True,"Actual14448 is diagnostic only")
 m.need(a["schema"]=="root-cost-time-universe-failure-diagnostic.v1" and a["status"]=="DIAGNOSTIC_ONLY_STRICT_COVERAGE_FAILURE_REPRODUCED_NOT_COST_ACCEPTANCE" and a["failed_job_id"]=="14178","Actual14448 exact diagnostic status")
 m.need(a["software_acceptance"]==SW and a["ledger"]==LR and a["failed_terminal_seal"]==seal and a["qualified_cost_source"]==qualified and a["diagnostic_source"]==s["source3"],"Prior source/software/ledger identity")
 prior_names=("diagnostic.py","diagnostic_cpu.sbatch","HANDOFF.md")
 prior_source_root=S/"pending/root_cost_time_universe_diagnostic_v1_rev2_14178"
 m.need(len(s["source3"])==3 and [r["path"]for r in s["source3"]]==[str(prior_source_root/n)for n in prior_names],"Exact executed REV2 OWN3")
 for r in s["source3"]:m.verify(r,True)
 for key in ("all_failed_inputs_source_controls_prepost_pass","strict_coverage_equal_check_not_waived","saved_inventory_exact_reproduction","sealed_failed13_exact_metadata_before_end_pass","no_numeric_cost_totals_computed_or_accepted","no_scientific_acceptance"):
  m.need(a.get(key) is True,"Actual14448 missing strict diagnostic guard: "+key)
 m.need(a["expected_submitted_slots"]==298 and a["explicit_positive_allocation_rows"]==298 and a["independent_covered_positive_rows"]==297,"Actual14448 denominators")
 missing=a["missing_coverage_diagnostics"]
 m.need(len(missing)==1 and missing[0]["logical_id"]=="13260_3" and missing[0]["raw_id"]=="13296" and missing[0]["phase"]=="formal_generation" and missing[0]["classification"]=="LOGICAL_ID_ABSENT_FROM_INDEPENDENT_RAW" and missing[0]["independent_logical_candidates"]==[] and missing[0]["independent_raw_id_candidates"]==[],"Exact observed missing allocation, without cause attribution")
 m.need(s["actual_CPU_allocation_report"]==a["allocation"],"Recorded prior actual CPU proof same")
 old=m.select_cpu_record(a["allocation"]["selected_scheduler_record"],"14448")
 m.need(old==a["allocation"] and old["allocated_CPUs"]==1 and old["allocated_GPUs"]==0,"Recorded prior RUNNING CPU guard exact")
 t=s["actual_terminal_query"]
 tf="JobID,JobName%128,User%64,Account%64,Partition%64,State,ExitCode,ElapsedRaw,AllocTRES,Submit,Start,End,Timelimit,ReqCPUS,ReqMem"
 m.need(t["argv"]==["sacct","-X","-n","-P","-j","14448","--format="+tf] and t["returncode"]==0 and t["TZ"]=="UTC" and t["SLURM_TIME_FORMAT"]=="standard" and t["stderr"]=="","Actual14448 saved terminal query")
 m.need(t["stdout"]=="14448|test9_root_cost_universe_diagnostic|u21111210118|u21111210118|organ|COMPLETED|0:0|3|billing=1,cpu=1,node=1|2026-10-14T03:19:46|2026-10-14T03:19:46|2026-10-14T03:19:49|00:10:00|1|8G\n","Actual14448 COMPLETED3s/CPU1/8G10 terminal")
 names={"diagnostic.json","local_sacct_help.command.json","local_sacct_help.stderr","local_sacct_help.stdout","local_sacct_version.command.json","local_sacct_version.stderr","local_sacct_version.stdout"}
 paths={str(PRIOR_DIR/n)for n in names}|{str(S/"logs/root-cost-universe-diagnostic-14448.out"),str(S/"logs/root-cost-universe-diagnostic-14448.err")}
 before=s["files_before"];after=s["files_after"]
 m.need(len(before)==len(after)==9 and {r["path"]for r in before}=={r["path"]for r in after}==paths and {p.name for p in PRIOR_DIR.iterdir()}==names,"Exact prior nine sealed files/seven output universe")
 pb={r["path"]:r for r in before};metadata=[]
 for r in after:
  m.need(all(r[k]==pb[r["path"]][k]for k in ("path","bytes","inode","mtime_ns")) and r["mode"]=="0o444","Prior metadata-only seal unchanged bytes/inode/mtime")
  pp=m.path(r["path"]);st=pp.lstat()
  m.need(pp.is_file() and not pp.is_symlink() and (st.st_size,st.st_ino,st.st_mtime_ns,st.st_mode&0o777)==(r["bytes"],r["inode"],r["mtime_ns"],0o444),"Current prior exact metadata")
  rr=m.rec(pp);m.verify(rr,True);metadata.append({"receipt":rr,"metadata":r})
 ob=s["directories_before"];od=s["directories_after"]
 m.need(len(ob)==len(od)==1 and ob[0]["path"]==od[0]["path"]==str(PRIOR_DIR) and all(ob[0][k]==od[0][k]for k in ("inode","mtime_ns")) and od[0]["mode"]=="0o555","Prior exact directory seal")
 st=PRIOR_DIR.stat();m.need((st.st_ino,st.st_mtime_ns,st.st_mode&0o777)==(od[0]["inode"],od[0]["mtime_ns"],0o555),"Prior directory current metadata")
 for name,field,argv in (("version","local_sacct_version",["sacct","--version"]),("help","local_sacct_help",["sacct","--help"])):
  cr=a[field];j=m.read(m.verify(cr,True))
  m.need(j["argv"]==argv and j["returncode"]==0 and j["TZ"]=="UTC" and j["SLURM_TIME_FORMAT"]=="standard","Prior actual local capability query")
  m.verify(j["stdout"],True);m.verify(j["stderr"],True)
  if name=="version":m.need(Path(j["stdout"]["path"]).read_text()=="slurm 22.05.8\n","Actual observed local sacct version")
 return a,sr,metadata,od[0]

def diagnostic_query(m,argv,out,name):
 # Failed/unsupported variants retain their actual raw streams, without a PASS substitution.
 m.need(isinstance(argv,list) and argv and argv[0]=="sacct" and "-T"not in argv,"Finite sacct diagnostic query only; no truncated allocation time")
 env={**os.environ,"TZ":"UTC","SLURM_TIME_FORMAT":"standard"}
 p=subprocess.run(argv,capture_output=True,text=True,env=env,check=False)
 raw=[]
 for suffix,value in (("stdout",p.stdout),("stderr",p.stderr)):
  pp=out/(name+"."+suffix)
  with pp.open("x")as f:f.write(value)
  pp.chmod(0o444);raw.append(m.rec(pp))
 cr=m.dump(out/(name+".command.json"),{"argv":argv,"TZ":"UTC","SLURM_TIME_FORMAT":"standard","returncode":p.returncode,"stdout":raw[0],"stderr":raw[1],"diagnostic_only":True,"cost_acceptance":False})
 return p,cr

def variant_observations(m,dispatches,expected,allocated,text):
 # This independently checks correspondence and coverage, deliberately never sums GPU cost.
 rows,steps=m.parse_accounting(text);known={r["logical_id"]:r for r in allocated}
 m.need(len(known)==len(allocated),"Prior positive allocation identities unique")
 arrays={d["job_id"]for d in dispatches if d["indices"]is not None}
 names={d["job_name"]for d in dispatches};logical_seen=set();raw_seen=set();covered=set()
 issues=[];filtered={"owner_or_account":0,"name":0,"zero_parent":0,"non_gpu_or_unknown_other_name":0,"zero_unallocated":0}
 fields=("logical_id","raw_id","job_name","user","account","state","elapsed_seconds","AllocTRES","GPU_count","Submit","Start","End","node","partition","WorkDir")
 for original in rows:
  for row in m.expand_zero_row(original):
   if row["user"]!=m.USER or row["account"]!=m.USER:filtered["owner_or_account"]+=1;continue
   if not m.SCOPE_NAME.fullmatch(row["job_name"]):filtered["name"]+=1;continue
   if row["logical_id"]in arrays and row["GPU_count"]in {None,0} and not row["AllocTRES"] and row["elapsed_seconds"]==0:filtered["zero_parent"]+=1;continue
   if row["GPU_count"] is None:
    if row["logical_id"]in expected or row["job_name"]in names:issues.append({"kind":"MISSING_GPU_ALLOCATION_TRES_NOT_ZERO","row":row})
    else:filtered["non_gpu_or_unknown_other_name"]+=1
    continue
   if row["GPU_count"]==0:
    if row["state"]=="CANCELLED" and row["elapsed_seconds"]==0 and not row["AllocTRES"]:filtered["zero_unallocated"]+=1
    else:issues.append({"kind":"AMBIGUOUS_ZERO_ALLOCATION","row":row})
    continue
   if row["logical_id"]in logical_seen or row["raw_id"]in raw_seen:issues.append({"kind":"DUPLICATE_POSITIVE_LOGICAL_OR_PHYSICAL_ID","row":row})
   logical_seen.add(row["logical_id"]);raw_seen.add(row["raw_id"])
   if row["logical_id"]not in known:
    issues.append({"kind":"UNKNOWN_UNMAPPED_POSITIVE_ALLOCATION","row":row});continue
   different=[key for key in fields if row[key]!=known[row["logical_id"]][key]]
   if different:issues.append({"kind":"EXPLICIT_INDEPENDENT_IDENTITY_FIELD_MISMATCH","different_fields":different,"row":row,"explicit_row":known[row["logical_id"]]})
   else:covered.add(row["logical_id"])
 missing=[r for r in allocated if r["logical_id"]not in covered]
 return {"status":"DIAGNOSTIC_IDENTITY_COVERAGE_COMPLETE_NOT_COST_ACCEPTANCE"if not issues and not missing else"DIAGNOSTIC_IDENTITY_OR_COVERAGE_INCOMPLETE_NOT_COST_ACCEPTANCE","positive_explicit_denominator":len(allocated),"matched_positive_count":len(covered),"missing_positive_allocations":missing,"identity_or_representation_issues":issues,"excluded_step_count":len(steps),"filtered_row_counts":filtered,"no_explicit_rows_inserted_into_independent_query":True,"numeric_cost_totals_computed":False}

def run_variants(m,dispatches,expected,allocated,ledger,expcmd,out):
 start=ledger["scope_start_utc"].replace("Z","");end=ledger["scope_end_utc"].replace("Z","")
 m.need(start=="2026-10-11T14:25:00" and end=="2026-10-12T16:39:19","Exact immutable UTC interval")
 modes=(("baseline_v",["-v"]),("array",["--array"]),("duplicates",["--duplicates"]),("array_duplicates",["--array","--duplicates"]),("array_allocations",["--array","-X"]),("state_running",["--state=RUNNING"]),("state_running_allocations",["--state=RUNNING","-X"]))
 variants=[]
 for name,flags in modes:
  argv=["sacct","-n","-P"]+flags+["-u",m.USER,"-S",start,"-E",end,"--format="+m.FIELDS]
  p,cr=diagnostic_query(m,argv,out,"bounded_"+name)
  observed={"mode":name,"query":cr,"returncode":p.returncode,"diagnostic_only":True,"capability_diagnostic_nonzero_allowed":"--array"in flags}
  if p.returncode!=0:observed["status"]="CAPABILITY_DIAGNOSTIC_NONZERO_ALLOWED_RAW_RETAINED_NOT_ACCEPTED"if "--array"in flags else"DIAGNOSTIC_QUERY_NONZERO_RAW_RETAINED_NOT_ACCEPTED"
  else:
   try:observed["observations"]=variant_observations(m,dispatches,expected,allocated,p.stdout)
   except Exception as e:observed.update(status="DIAGNOSTIC_QUERY_PARSE_OR_REPRESENTATION_ERROR_RAW_RETAINED",reason_type=type(e).__name__,reason=str(e))
  variants.append(observed)
 hf,hfr=diagnostic_query(m,["sacct","--helpformat"],out,"sacct_helpformat")
 eligible={"helpformat_query":hfr,"eligible_field_advertised":hf.returncode==0 and "Eligible"in re.findall(r"[A-Za-z][A-Za-z0-9]*",hf.stdout),"not_independent_universe":True,"never_used_to_fill_coverage":True}
 if eligible["eligible_field_advertised"]:
  p,cr=diagnostic_query(m,["sacct","-n","-P","-j","13296","--format="+m.FIELDS+",Eligible"],out,"explicit13296_eligible")
  eligible.update(query=cr,returncode=p.returncode,status="DIAGNOSTIC_EXPLICIT_CAUSE_METADATA_ONLY")
  if p.returncode==0:
   try:
    original=[];extra=[]
    for line in p.stdout.splitlines():
     if not line.strip():continue
     cells=line.split("|");m.need(len(cells)==15,"Exact fourteen fields plus Eligible")
     original.append("|".join(cells[:14]));extra.append({"logical_id":cells[0],"raw_id":cells[1],"Eligible":cells[14],"raw_line":line})
    rows,steps=m.parse_accounting("\n".join(original));target=[r for r in allocated if r["logical_id"]=="13260_3" and r["raw_id"]=="13296"]
    m.need(len(target)==1 and len(rows)==1 and all(rows[0][k]==target[0][k]for k in ("logical_id","raw_id","job_name","user","account","state","elapsed_seconds","AllocTRES","GPU_count","Submit","Start","End","node","partition","WorkDir")),"Exact13296 diagnostic query identity; no replacement")
    eligible.update(observations=extra,excluded_step_count=len(steps),exact_target_identity_match=True)
   except Exception as e:eligible.update(status="DIAGNOSTIC_EXPLICIT_METADATA_PARSE_OR_IDENTITY_ERROR",reason_type=type(e).__name__,reason=str(e))
  else:eligible["status"]="DIAGNOSTIC_EXPLICIT_METADATA_QUERY_NONZERO_RAW_RETAINED"
 else:eligible["status"]="ELIGIBLE_NOT_ADVERTISED_OR_HELPFORMAT_FAILED_NO_TARGET_QUERY"
 return variants,eligible

def main():
 p=argparse.ArgumentParser();p.add_argument("--out",required=True);a=p.parse_args()
 # Import only previously CPU-qualified readonly source; no source/science fallback.
 spec=importlib.util.spec_from_file_location("qualified_cost",F/"root_gpu_cost_audit.py")
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 allocation=m.cpu() # Hashing, compile, parsing and comparisons begin only after owned CPU guard.
 m.need(allocation["allocated_CPUs"]==1 and allocation["allocated_GPUs"]==0 and re.search(r"\bJobName="+PROBE_NAME+r"(?:\s|$)",allocation["selected_scheduler_record"]),"Exact named owned pure CPU1 probe allocation")
 out=m.path(a.out);m.need(not out.exists(),"New absent diagnostic output required");out.mkdir()
 ownroot=Path(__file__).resolve().parent
 original_verify=m.verify;consumed={}
 def tracked_verify(r,readonly=False):
  pp=original_verify(r,readonly)
  rr={k:r[k]for k in ("path","bytes","sha256")}
  st=pp.stat();meta={"bytes":st.st_size,"inode":st.st_ino,"mtime_ns":st.st_mtime_ns,"mode":st.st_mode&0o777}
  if rr["path"] in consumed:
   m.need(m.same(consumed[rr["path"]]["receipt"],rr) and consumed[rr["path"]]["metadata"]==meta,"Consumed control identity/metadata drift")
  else:consumed[rr["path"]]={"receipt":rr,"metadata":meta,"readonly":readonly}
  return pp
 m.verify=tracked_verify
 logical_runtime=Path(sys.executable);resolved_runtime=logical_runtime.resolve()
 runtime_before=m.rec(resolved_runtime)
 m.need(runtime_before["bytes"]==25916456 and runtime_before["sha256"]=="76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a","Accepted core interpreter actual scalar pin")
 m.need(not(ownroot.stat().st_mode&0o222),"Readonly diagnostic source directory required")
 own=[m.rec(m.verify(m.rec(ownroot/n),True))for n in OWN]
 qualified=m.software_ready(SW)
 for n in OWN:
  if n.endswith(".py"):compile((ownroot/n).read_bytes(),str(ownroot/n),"exec")
  if n.endswith(".sbatch"):m.need(subprocess.run(["bash","-n",str(ownroot/n)],capture_output=True).returncode==0,"Diagnostic launcher syntax")
 m.verify(LR,True);ledger=m.read(LR["path"]);entries,end=m.ledger_contract(ledger)
 journal=m.verify_journal_ledger(ledger)
 inputs=[m.rec(m.verify(m.rec(x),True))for x in sorted(FAIL.iterdir())]
 seal=m.rec(m.verify(m.rec(SEAL),True));savedseal=m.read(SEAL)
 m.need(seal["bytes"]==9834 and savedseal["schema"]=="root-cost-audit-failed-actual-terminal-metadata-only.v1" and savedseal["status"]=="ACTUAL_FAILED_TYPED_COST_TERMINAL_METADATA_READBACK_PASS_NOT_COST_ACCEPTANCE","Exact9834 failed terminal seal schema/status")
 m.need(savedseal["actual_job_id"]=="14178" and savedseal["acceptance_absent"] is True,"Exact failed14178 identity")
 terminal=savedseal["actual_terminal_query"]
 m.need(terminal["returncode"]==0 and terminal["TZ"]=="UTC" and terminal["SLURM_TIME_FORMAT"]=="standard" and terminal["stderr"]=="","Actual qualified UTC terminal query")
 exact_terminal="14178|ppi_root_gpu_cost_cpu|u21111210118|u21111210118|organ|FAILED|1:0|38|billing=1,cpu=1,node=1|2026-10-14T02:08:10|2026-10-14T02:57:27|2026-10-14T02:58:05|00:30:00|1|8G\n"
 m.need(terminal["stdout"]==exact_terminal,"Actual failedCPU1/38s/owner/account/organ/8G30min terminal tuple")
 # Historical absence of a GPU key is not used as zero-GPU scientific allocation evidence.
 expected_fail_names={"bounded_current_name_universe.command.json","bounded_current_name_universe.stderr","explicit_root_submissions.stderr","bounded_current_name_universe.stdout","current_scope_squeue.stderr","typed_incomplete.json","current_scope_squeue.stdout","explicit_root_submissions.stdout","explicit_root_submissions.command.json","current_scope_squeue.command.json","preclosure_numeric_inventory.json"}
 expected_paths={str(FAIL/n)for n in expected_fail_names}|{str(S/"logs/root-gpu-cost-14178.out"),str(S/"logs/root-gpu-cost-14178.err")}
 post=savedseal["files_after"];prior=savedseal["files_before"]
 m.need(len(post)==len(prior)==13 and {r["path"]for r in post}=={r["path"]for r in prior}==expected_paths,"Exact13 sealed file universe")
 m.need({x.name for x in FAIL.iterdir()}==expected_fail_names and len(inputs)==11,"Exact11 failed output directory inputs")
 prior_by={r["path"]:r for r in prior};sealed_meta={}
 for r in post:
  before_meta=prior_by[r["path"]]
  m.need(all(r[k]==before_meta[k]for k in ("path","bytes","inode","mtime_ns")) and r["mode"]=="0o444","Metadata-only seal preserved original bytes/inode/mtime")
  pp=m.path(r["path"]);st=pp.lstat()
  m.need(pp.is_file() and not pp.is_symlink() and st.st_size==r["bytes"] and st.st_ino==r["inode"] and st.st_mtime_ns==r["mtime_ns"] and st.st_mode&0o777==0o444,"Exact sealed file current metadata")
  sealed_meta[r["path"]]=r
  m.verify(m.rec(pp),True)
 m.need(len(savedseal["directories_before"])==len(savedseal["directories_after"])==1,"Exact failed output directory seal")
 od=savedseal["directories_after"][0];ob=savedseal["directories_before"][0]
 m.need(od["path"]==ob["path"]==str(FAIL) and od["inode"]==ob["inode"]==FAIL.stat().st_ino and od["mtime_ns"]==ob["mtime_ns"]==FAIL.stat().st_mtime_ns and od["mode"]=="0o555" and FAIL.stat().st_mode&0o777==0o555,"Directory exact inode/mtime/readonly")
 m.need(not(FAIL/"acceptance.json").exists() and not(FAIL.stat().st_mode&0o222),"Readonly failed output; no cost acceptance")
 typed=m.read(FAIL/"typed_incomplete.json")
 m.need(typed["status"]=="ROOT_GPU_COST_UNIVERSE_TYPED_INCOMPLETE" and typed["mode"]=="audit" and typed["reason_type"]=="ValueError" and typed["reason"]==REASON,"Replay exact recorded failed gate only")
 expcmd=m.read(FAIL/"explicit_root_submissions.command.json")
 ucmd=m.read(FAIL/"bounded_current_name_universe.command.json")
 for command in (expcmd,ucmd):
  m.need(command["returncode"]==0 and command["TZ"]=="UTC" and command["SLURM_TIME_FORMAT"]=="standard","Saved successful exact UTC query control")
  m.verify(command["stdout"],True);m.verify(command["stderr"],True)
 explicit=Path(expcmd["stdout"]["path"]).read_text()
 universe=Path(ucmd["stdout"]["path"]).read_text()
 before=m.preliminary_inventory(explicit,universe)
 m.need(before==m.read(FAIL/"preclosure_numeric_inventory.json"),"Saved CPU inventory independently reproduced exactly")
 dispatches=[]
 for e in entries:
  controller=m.read(m.verify(e["receipt"],True))
  m.verify(controller["launcher"],True)
  if controller.get("entry") is not None:m.verify(controller["entry"],True)
  dispatches.append(m.submission_contract(e,controller,lambda r:m.read(m.verify(r,True)),Path(controller["launcher"]["path"]).read_text()))
 expected,arrays=m.expected_allocations(dispatches)
 jobs=sorted({d["job_id"]for d in dispatches},key=int)
 m.need(expcmd["argv"]==["sacct","-n","-P","-j",",".join(jobs),"--format="+m.FIELDS],"Exact explicit query argv")
 m.need(ucmd["argv"]==["sacct","-n","-P","-u",m.USER,"-S",ledger["scope_start_utc"].replace("Z",""),"-E",ledger["scope_end_utc"].replace("Z",""),"--format="+m.FIELDS],"Exact independent bounded query argv")
 try:
  m.close_rows(dispatches,explicit,universe,end)
 except ValueError as e:
  m.need(str(e)==REASON,"Replay failed at a different gate")
 else:raise ValueError("Expected strict coverage failure was not reproduced")
 erows,esteps=m.parse_accounting(explicit);urows,usteps=m.parse_accounting(universe)
 allocated=[]
 for raw in erows:
  for row in m.expand_zero_row(raw):
   if row["logical_id"] in expected and row["GPU_count"] is not None and row["GPU_count"]>0:allocated.append(row)
 classifications=[];covered=[]
 for row in allocated:
  candidates=[u for u in urows if u["logical_id"]==row["logical_id"]]
  eligible=[u for u in candidates if u["user"]==m.USER and u["account"]==m.USER and m.SCOPE_NAME.fullmatch(u["job_name"]) and u["GPU_count"] is not None and u["GPU_count"]>0]
  if eligible:covered.append(row["logical_id"]);continue
  rawmatches=[u for u in urows if u["raw_id"]==row["raw_id"]]
  if not candidates:reason="LOGICAL_ID_ABSENT_FROM_INDEPENDENT_RAW"
  elif any(u["user"]!=m.USER or u["account"]!=m.USER for u in candidates):reason="OWNER_OR_ACCOUNT_FILTER"
  elif all(not m.SCOPE_NAME.fullmatch(u["job_name"])for u in candidates):reason="JOB_NAME_SCOPE_FILTER"
  else:reason="ALLOCATION_REPRESENTATION_REQUIRES_DIAGNOSIS"
  classifications.append({"logical_id":row["logical_id"],"raw_id":row["raw_id"],"phase":expected[row["logical_id"]]["phase"],"classification":reason,"explicit_row":row,"independent_logical_candidates":candidates,"independent_raw_id_candidates":rawmatches})
 m.need(classifications,"No saved coverage difference found")
 prior,prior_seal,prior_metadata,prior_directory=saved_probe_parent(m,qualified,seal)
 m.need(len(expected)==prior["expected_submitted_slots"] and len(allocated)==prior["explicit_positive_allocation_rows"] and len(covered)==prior["independent_covered_positive_rows"] and classifications==prior["missing_coverage_diagnostics"],"Original CPU diagnosis independently reproduced exactly")
 variants,eligible=run_variants(m,dispatches,expected,allocated,ledger,expcmd,out)
 # These are diagnostic differences, never accepted numeric cost or a replacement universe.
 result={"schema":"root-cost-time-query-probe.v1","status":"DIAGNOSTIC_ONLY_FIXED_TIME_QUERY_VARIANTS_OBSERVED_NOT_COST_OR_SCIENCE_ACCEPTANCE","failed_job_id":"14178","allocation":allocation,"software_acceptance":SW,"qualified_cost_source":qualified,"diagnostic_source":own,"ledger":LR,"journal_closure":ledger["journal_closure"],"failed_terminal_seal":seal,"failed_inputs":inputs,"saved_explicit_query":expcmd,"saved_independent_query":ucmd,"expected_submitted_slots":len(expected),"explicit_positive_allocation_rows":len(allocated),"independent_covered_positive_rows":len(covered),"missing_coverage_diagnostics":classifications,"excluded_explicit_steps":len(esteps),"excluded_universe_steps":len(usteps),"saved_inventory_exact_reproduction":True,"strict_coverage_equal_check_not_waived":True,"no_numeric_cost_totals_computed_or_accepted":True,"no_scientific_acceptance":True,"no_neural_execution":True,"no_GPU_request":True,"no_new_accounting_query_for_cost":True,"actual14448_diagnostic":PRIOR,"actual14448_terminal_seal":prior_seal,"independent_fixed_time_query_variants":variants,"explicit13296_eligible_metadata_not_universe":eligible,"own_compile_bash_syntax_pass":True}
 new_query_controls=[v["query"]for v in variants]+[eligible["helpformat_query"]]
 if "query"in eligible:new_query_controls.append(eligible["query"])
 for cr in new_query_controls:
  cj=m.read(m.verify(cr,True));m.verify(cj["stdout"],True);m.verify(cj["stderr"],True)
 m.need(m.verify_journal_ledger(ledger)==journal,"Complete journal/closure/controller history unchanged at end")
 for r in inputs+[seal]:m.verify(r,True)
 for binding in list(consumed.values()):
  rr=binding["receipt"];pp=original_verify(rr,binding["readonly"]);st=pp.stat()
  m.need(binding["metadata"]=={"bytes":st.st_size,"inode":st.st_ino,"mtime_ns":st.st_mtime_ns,"mode":st.st_mode&0o777},"All actually consumed control/source input metadata unchanged")
 for pp,r in sealed_meta.items():
  st=Path(pp).lstat();m.need(st.st_size==r["bytes"] and st.st_ino==r["inode"] and st.st_mtime_ns==r["mtime_ns"] and st.st_mode&0o777==0o444,"All sealed13 metadata unchanged at end")
 m.need(FAIL.stat().st_ino==od["inode"] and FAIL.stat().st_mtime_ns==od["mtime_ns"] and FAIL.stat().st_mode&0o777==0o555,"Failed directory metadata unchanged at end")
 for binding in prior_metadata:
  rr=binding["receipt"];r=binding["metadata"];pp=m.verify(rr,True);st=pp.lstat()
  m.need((st.st_size,st.st_ino,st.st_mtime_ns,st.st_mode&0o777)==(r["bytes"],r["inode"],r["mtime_ns"],0o444),"Prior nine sealed files unchanged at end")
 st=PRIOR_DIR.stat();m.need((st.st_ino,st.st_mtime_ns,st.st_mode&0o777)==(prior_directory["inode"],prior_directory["mtime_ns"],0o555),"Prior directory unchanged at end")
 m.need(m.same(runtime_before,m.rec(resolved_runtime)),"Conditional actual core interpreter unchanged at end")
 result["runtime_scalar_only_no_binary_redistribution"]={"logical_interpreter":str(logical_runtime),"resolved_interpreter":str(resolved_runtime),"bytes_as_scalar":runtime_before["bytes"],"sha256_as_scalar":runtime_before["sha256"]}
 result["actually_consumed_receipts_and_metadata_before_end"]=list(consumed.values())
 result["sealed_failed13_exact_metadata_before_end_pass"]=True
 result["historical_failed_GPU_missing_key_not_zero_imputation"]=True
 m.need(own==[m.rec(ownroot/n)for n in OWN] and qualified==m.frozen_sources(),"Whole diagnostic/qualified source prepost identity")
 m.need(m.same(m.rec(LR["path"]),LR) and m.software_ready(SW)==qualified,"Control receipts/source unchanged")
 result["all_failed_inputs_source_controls_prepost_pass"]=True
 rr=m.dump(out/"diagnostic.json",result)
 print(json.dumps({"diagnostic":rr,"status":result["status"],"probe_modes":len(variants),"no_cost_acceptance":True}))
if __name__=="__main__":main()
