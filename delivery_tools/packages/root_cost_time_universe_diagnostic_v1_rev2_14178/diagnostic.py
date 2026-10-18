#!/usr/bin/env python3
"""Owned pure CPU diagnosis of the immutable failed14178 time-universe coverage."""
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
def main():
 p=argparse.ArgumentParser();p.add_argument("--out",required=True);a=p.parse_args()
 # Import only previously CPU-qualified readonly source; no source/science fallback.
 spec=importlib.util.spec_from_file_location("qualified_cost",F/"root_gpu_cost_audit.py")
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 allocation=m.cpu() # Hashing, compile, parsing and comparisons begin only after owned CPU guard.
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
 version,vreceipt=m.query(["sacct","--version"],out,"local_sacct_version")
 helptext,hreceipt=m.query(["sacct","--help"],out,"local_sacct_help")
 # These are diagnostic differences, never accepted numeric cost or a replacement universe.
 result={"schema":"root-cost-time-universe-failure-diagnostic.v1","status":"DIAGNOSTIC_ONLY_STRICT_COVERAGE_FAILURE_REPRODUCED_NOT_COST_ACCEPTANCE","failed_job_id":"14178","allocation":allocation,"software_acceptance":SW,"qualified_cost_source":qualified,"diagnostic_source":own,"ledger":LR,"journal_closure":ledger["journal_closure"],"failed_terminal_seal":seal,"failed_inputs":inputs,"saved_explicit_query":expcmd,"saved_independent_query":ucmd,"expected_submitted_slots":len(expected),"explicit_positive_allocation_rows":len(allocated),"independent_covered_positive_rows":len(covered),"missing_coverage_diagnostics":classifications,"excluded_explicit_steps":len(esteps),"excluded_universe_steps":len(usteps),"saved_inventory_exact_reproduction":True,"strict_coverage_equal_check_not_waived":True,"no_numeric_cost_totals_computed_or_accepted":True,"no_scientific_acceptance":True,"no_neural_execution":True,"no_GPU_request":True,"no_new_accounting_query_for_cost":True,"local_sacct_version":vreceipt,"local_sacct_help":hreceipt,"own_compile_bash_syntax_pass":True}
 m.need(m.verify_journal_ledger(ledger)==journal,"Complete journal/closure/controller history unchanged at end")
 for r in inputs+[seal]:m.verify(r,True)
 for binding in list(consumed.values()):
  rr=binding["receipt"];pp=original_verify(rr,binding["readonly"]);st=pp.stat()
  m.need(binding["metadata"]=={"bytes":st.st_size,"inode":st.st_ino,"mtime_ns":st.st_mtime_ns,"mode":st.st_mode&0o777},"All actually consumed control/source input metadata unchanged")
 for pp,r in sealed_meta.items():
  st=Path(pp).lstat();m.need(st.st_size==r["bytes"] and st.st_ino==r["inode"] and st.st_mtime_ns==r["mtime_ns"] and st.st_mode&0o777==0o444,"All sealed13 metadata unchanged at end")
 m.need(FAIL.stat().st_ino==od["inode"] and FAIL.stat().st_mtime_ns==od["mtime_ns"] and FAIL.stat().st_mode&0o777==0o555,"Failed directory metadata unchanged at end")
 m.need(m.same(runtime_before,m.rec(resolved_runtime)),"Conditional actual core interpreter unchanged at end")
 result["runtime_scalar_only_no_binary_redistribution"]={"logical_interpreter":str(logical_runtime),"resolved_interpreter":str(resolved_runtime),"bytes_as_scalar":runtime_before["bytes"],"sha256_as_scalar":runtime_before["sha256"]}
 result["actually_consumed_receipts_and_metadata_before_end"]=list(consumed.values())
 result["sealed_failed13_exact_metadata_before_end_pass"]=True
 result["historical_failed_GPU_missing_key_not_zero_imputation"]=True
 m.need(own==[m.rec(ownroot/n)for n in OWN] and qualified==m.frozen_sources(),"Whole diagnostic/qualified source prepost identity")
 m.need(m.same(m.rec(LR["path"]),LR) and m.software_ready(SW)==qualified,"Control receipts/source unchanged")
 result["all_failed_inputs_source_controls_prepost_pass"]=True
 rr=m.dump(out/"diagnostic.json",result)
 print(json.dumps({"diagnostic":rr,"status":result["status"],"missing_coverage_rows":len(classifications),"no_cost_acceptance":True}))
if __name__=="__main__":main()
