#!/usr/bin/env python3
"""Read-only DIAGNOSTIC_ONLY attribution of the two frozen RF atom-coverage errors."""
import argparse, ast, datetime, hashlib, json, os, pathlib, re, subprocess, sys, traceback

R=pathlib.Path("/lustre/users/u21111210118/projects/test9")
S=R/"steps/24_benchmark_delivery"
F=R/"steps/22_matched_benchmark"
PLAN={"path":str(F/"formal_freeze_13257/plan/frozen_plan.json"),"bytes":20295,"sha256":"e913d1bbccd531bf88a73f6ba60e8a0de85bb03ad8bcd3455d8952ca4effe0b6"}
SOURCE={"path":str(F/"settings/pilot_v8/source/benchmark_runtime.py"),"bytes":51064,"sha256":"51b516a692d369f4d9a6ae9e3c39c0294da219c4d065420bbf9538a4af4b6562"}
TARGET={"path":str(F/"input_preparation/prepared_7_chainfix_13094/CRK_SH3_1CKA/input_manifest.json"),"bytes":4528,"sha256":"0f2022fd7dfd040044608b53cd57f98fccd2bf37b4e43cc54dda334ace2e793b"}
INNER={"path":str(S/"runs/formal_collection_13260/acceptance.json"),"bytes":8969,"sha256":"385da53a04dbf87e5d104c27804c2671e31496a0599977d7cef986323db309d1"}
ERROR="RuntimeError('RFD full backbone atom coverage rejected')"
UNITS={20:{"raw":"13349","replicate":21011,"attempt":2727024350,"task":"ea0acd5663671b3f6c16ad53","error_sha":"ce85305b5ea4eeb5cbd011aab434bf186958fdc7fa4b4dc5ad73440c9619c0e7"},22:{"raw":"13351","replicate":21012,"attempt":4026176678,"task":"25e73ebed9d3d055a9abe600","error_sha":"6cd13eb7429e899b4a8923e143d8c3ed6b47a07f01e84aee370a2883064573c5"}}
TERMINAL={"COMPLETED","FAILED","CANCELLED","TIMEOUT","OUT_OF_MEMORY","NODE_FAIL","PREEMPTED","BOOT_FAIL","DEADLINE","REVOKED"}
def need(condition,message):
 if not condition:raise ValueError(message)
def safe(p):
 p=pathlib.Path(p)
 need(p.is_absolute() and str(p)==os.path.normpath(str(p)) and R in p.parents,"Exact internal absolute path required")
 for x in [p]+list(p.parents):
  if x==R.parent:break
  need(not x.is_symlink(),"Symlink evidence path rejected: "+str(x))
 return p
def data(p,readonly=False):
 p=safe(p);need(p.is_file(),"Regular evidence file required: "+str(p))
 need(not readonly or p.stat().st_mode&0o222==0,"Readonly source/authority required: "+str(p))
 return p.read_bytes()
def receipt(p,readonly=False):
 b=data(p,readonly);return {"path":str(p),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def verify(r,readonly=False):
 need(set(r)=={"path","bytes","sha256"} and type(r["bytes"]) is int and r["bytes"]>=0 and re.fullmatch("[0-9a-f]{64}",r["sha256"]),"Exact receipt shape required")
 actual=receipt(r["path"],readonly);need(actual==r,"Evidence byte identity changed: "+r["path"]);return data(r["path"],readonly)
def tres(s):
 pairs={}
 for item in s.split(","):
  need(item and "=" in item,"Explicit allocated TRES required")
  k,v=item.split("=",1);need(k and k not in pairs,"Duplicate/empty TRES key rejected");pairs[k]=v
 need("cpu" in pairs and re.fullmatch("[0-9]+",pairs["cpu"]),"Numeric allocated CPU missing")
 typed=[]
 for k,v in pairs.items():
  if k=="gres/gpu" or k.startswith("gres/gpu:"):
   need(re.fullmatch("[0-9]+",v),"Invalid allocated GPU count");typed.append((k,int(v)))
 aggregate=dict(typed).get("gres/gpu",0)
 return pairs,int(pairs["cpu"]),max(aggregate,sum(v for k,v in typed if k!="gres/gpu"))
def cpu():
 job=os.environ.get("SLURM_JOB_ID","");need(re.fullmatch("[0-9]+",job),"Actual Slurm CPU allocation mandatory")
 p=subprocess.run(["scontrol","show","job","-o",job],text=True,capture_output=True);need(p.returncode==0,"Current scheduler query failed")
 lines=[x for x in p.stdout.splitlines() if re.search(r"(?:^|\s)JobId="+re.escape(job)+r"(?:\s|$)",x)]
 need(len(lines)==1,"Current allocation absent/ambiguous")
 fields=dict(re.findall(r"(\S+?)=(\S+)",lines[0]))
 need(fields.get("JobState")=="RUNNING" and fields.get("UserId","").split("(")[0]=="u21111210118" and fields.get("Account")=="u21111210118" and fields.get("Partition")=="organ","Owned actual RUNNING organ CPU allocation required")
 records=[tres(fields[k]) for k in ("AllocTRES","TRES") if fields.get(k)]
 need(records and all(c==1 and g==0 for d,c,g in records) and fields.get("NumCPUs")=="1" and fields.get("NumTasks")=="1","Actual CPU1/GPU0 required")
 need(len(records)<2 or records[0][0]==records[1][0],"Contradictory current allocation fields")
 need(fields.get("JobName")=="test9_formal_failed_atom_coverage_v1","Exact diagnostic jobname required")
 return {"slurm_job_id":job,"actual_cpu_count":1,"actual_gpu_count":0,"scontrol_stdout":p.stdout,"scontrol_stderr":p.stderr,"returncode":p.returncode}
def dump(p,obj):
 p=safe(p);need(not p.exists(),"New diagnostic output already exists")
 with p.open("x",encoding="utf-8") as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write("\n")
 p.chmod(0o444);return receipt(p,True)
class Evidence:
 def __init__(self,out):self.out=out;self.records={};self.copies={};self.missing=[]
 def take(self,p,pinned=None,readonly=False,role="ORIGINAL_METADATA_DIAGNOSTIC_ONLY",missing=False):
  p=safe(p)
  if not p.exists():
   if missing:self.missing.append({"path":str(p),"role":role,"status":"MISSING_ORIGINAL_FILE_NOT_REPLACED"});return None
   raise FileNotFoundError(p)
  r=receipt(p,readonly)
  if pinned is not None:need(r==pinned,"Pinned original bytes differ: "+str(p))
  if str(p) in self.records:
   need(self.records[str(p)]["original"]==r,"Duplicate original identity conflict");return self.copies[str(p)]
  copy=self.out/"evidence"/("%04d_%s"%(len(self.records),p.name));copy.parent.mkdir(exist_ok=True)
  with copy.open("xb") as f:f.write(data(p,readonly))
  copy.chmod(0o444);cr=receipt(copy,True)
  need(cr["bytes"]==r["bytes"] and cr["sha256"]==r["sha256"],"Byte copy mismatch")
  self.records[str(p)]={"original":r,"immutable_copy":cr,"role":role,"original_mode":oct(p.stat().st_mode&0o777),"readonly_required":readonly}
  self.copies[str(p)]=copy;return copy
 def read(self,p,**kw):return json.loads(self.take(p,**kw).read_bytes())
 def post(self):
  for x in self.records.values():verify(x["original"],x["readonly_required"]);verify(x["immutable_copy"],True)
def scheduler(out,job,all28=False):
 argv=["sacct","-X","-j",job,"--noheader","--parsable2","--format=JobID%32,JobIDRaw,State,ExitCode,ElapsedRaw,AllocCPUS,AllocTRES%220,User%64,Account%64,Partition%64,JobName%128"]
 p=subprocess.run(argv,text=True,capture_output=True);need(p.returncode==0,"Actual terminal query failed")
 raw={"argv":argv,"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr};rows={}
 for line in p.stdout.splitlines():
  fields=line.strip().split("|")
  if fields and fields[-1]=="":fields.pop()
  need(len(fields)==11,"Unexpected terminal accounting fields")
  logical,physical,state_,exit_,elapsed,cpus,tr,owner,account,part,name=fields
  if all28 and logical=="13260":continue
  if all28:
   match=re.fullmatch("13260_([0-9]+)",logical);need(match is not None,"Unknown formal logical allocation")
   key=int(match.group(1));need(key in range(28),"Unknown fixed formal slot")
  else:need(logical==physical==job,"Exact collector terminal allocation required");key=job
  need(key not in rows and re.fullmatch("[0-9]+",physical),"Duplicate/unknown raw allocation")
  need(state_.split()[0].rstrip("+") in TERMINAL and owner==account=="u21111210118" and part=="organ","Actual owned terminal allocations required")
  _,c,g=tres(tr);need(re.fullmatch("[0-9]+",elapsed) and cpus==str(c),"Numeric allocated CPU/elapsed required")
  if all28:need(c==3 and g==1 and name=="test9_paired_formal_generation","Formal positive CPU3/GPU1 accounting required")
  else:need(c==2 and g==0 and state_=="COMPLETED" and exit_=="0:0","Actual accepted collector CPU2/GPU0 terminal required")
  rows[key]={"logical_job_id":logical,"raw_job_id":physical,"state":state_,"exit_code":exit_,"elapsed_seconds":int(elapsed),"allocated_cpu_count":c,"allocated_gpu_count":g,"AllocTRES":tr,"user":owner,"account":account,"partition":part,"job_name":name}
 if all28:need(set(rows)==set(range(28)) and len({x["raw_job_id"] for x in rows.values()})==28,"Exactly all28 unique raw terminal allocations required")
 else:need(set(rows)=={job},"Exact original collector terminal row absent")
 dump(out/("all28_actual_sacct.json" if all28 else "collector13264_actual_sacct.json"),raw);return rows
def verify_root_fence(fence,rows):
 expected=["sacct","-j","13260","-X","-n","-P","-o","JobIDRaw,JobID,State,ExitCode,ElapsedRaw,AllocCPUS,AllocTRES,Start,End,User%64,Account%64,JobName%64,Partition"]
 calls=[x for x in fence["raw_scheduler_calls"] if x.get("argv")==expected]
 need(len(calls)==1 and calls[0]["returncode"]==0,"Exact root ALL28 actual sacct capture required")
 observed=set()
 for line in calls[0]["stdout"].splitlines():
  values=line.strip().split("|");need(len(values)==13,"Exact root fence numeric fields required")
  raw,logical,state_,exit_,elapsed,cpus,tr,start,end,owner,account,name,part=values
  match=re.fullmatch("13260_([0-9]+)",logical);need(match is not None,"Unexpected root fence logical row");index=int(match.group(1))
  need(index in rows and index not in observed,"Duplicate/unknown root fence row");observed.add(index);row=rows[index]
  need(raw==row["raw_job_id"] and logical==row["logical_job_id"] and state_==row["state"] and exit_==row["exit_code"] and int(elapsed)==row["elapsed_seconds"] and cpus==str(row["allocated_cpu_count"]) and tres(tr)[0]==tres(row["AllocTRES"])[0] and owner==row["user"] and account==row["account"] and name==row["job_name"] and part==row["partition"],"Root fence differs from fresh actual accounting")
 need(observed==set(range(28)),"Root fence must bind all28 original allocations")
def extract_observer(text,out):
 tree=ast.parse(text);nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=="validate_rfd_output"]
 need(len(nodes)==1,"Frozen validation function absent")
 function=ast.get_source_segment(text,nodes[0])
 marker=' for rs in [source,mapped,binder]:\n  if any(atom not in r for r in rs for atom in ["N","CA","C","O"]):raise RuntimeError("RFD full backbone atom coverage rejected")'
 need(function.count(marker)==1,"Exact frozen N/CA/C/O gate changed")
 prefix=function.split(marker)[0]
 extension='''
 groups={"reference_target":source,"generated_target":mapped,"binder":binder}
 observations=[]
 for role,residues in groups.items():
  missing=[]
  for r in residues:
   atoms=[a for a in ["N","CA","C","O"] if a not in r]
   if atoms:missing.append({"chain":r.parent.id,"residue_id":[r.id[0],r.id[1],r.id[2]],"residue_name":r.resname,"missing_atoms":atoms})
  observations.append({"role":role,"residue_count":len(residues),"missing_residue_count":len(missing),"missing_atom_count":sum(len(x["missing_atoms"]) for x in missing),"missing":missing})
 return {"status":"FROZEN_ATOM_GATE_REJECTION_REPRODUCED" if any(x["missing_atom_count"] for x in observations) else "NO_MISSING_ATOMS_OBSERVED_CURRENT_ORIGINAL_BYTES","groups":observations,"mapping_checks":checks,"frozen_gate_selection_reached":True}
'''
 derived=out/"derived_frozen_gate_observer.py"
 with derived.open("x") as f:f.write(prefix+extension)
 derived.chmod(0o444);namespace={"inside_project":safe,"Path":pathlib.Path}
 exec(compile(derived.read_bytes(),str(derived),"exec"),namespace)
 return namespace["validate_rfd_output"],{"source_function":"validate_rfd_output","source_first_line":nodes[0].lineno,"source_last_line":nodes[0].end_lineno,"derived_executed_source":receipt(derived,True),"prefix_selection_unmodified":True,"stop_before_coordinate_comparison_or_scoring":True,"only_gate_error_replaced_with_typed_missing_atom_observation":True}
def unit(index,e,rows,plan,method,target,observer,accepted_receipts):
 expected=UNITS[index];d=F/"formal_runs"/("13260_"+str(index));a=d/"attempts/000000";rr=e.read(d/"run_receipt.json",pinned=accepted_receipts[index],readonly=False)
 need(rr["task"]==plan["tasks"][index] and rr["task"]["task_id"]==expected["task"] and rr["task"]["method_id"]=="rf_diffusion" and rr["task"]["target_id"]=="CRK_SH3_1CKA" and rr["task"]["seed"]==expected["replicate"],"Exact failed fixed task differs")
 need(rr["raw_allocation_id"]==rows[index]["raw_job_id"]==expected["raw"] and rr["logical_allocation_key"]=="13260_"+str(index),"Failed actual allocation binding differs")
 need(rows[index]["state"]=="FAILED" and rows[index]["exit_code"]=="2:0" and rr["status"]=="EARLY_ENGINEERING_FAILURE" and rr["attempt_count"]==1 and rr["comparable_full_budget"] is False and rr["technical_rerun_of"] is None and rr["source_amendment"] is None,"Exact original failure/non-full-budget policy required")
 initial=e.read(d/"initial.json",pinned=rr["initial_receipt"]);need(initial["task"]==rr["task"] and initial["allocation_identity"]==rr["allocation_identity"] and initial["plan"]==PLAN and rr["plan"]==PLAN,"Original initial allocation/plan binding differs")
 init=e.read(d/"session/initialization.json")
 need(init["status"]=="RESIDENT_IMPORTS_COMPLETE" and init["method"]=="rf_diffusion" and init["source_entry"]==SOURCE and init["target_manifest"]==TARGET and init["config"]==method["config_receipt"] and init["allocation"]["slurm_job_id"]==expected["raw"],"Actual resident source/input binding differs")
 ready=e.read(rr["session"]["ready"]["path"],pinned=rr["session"]["ready"])
 need(ready["schema"]=="paired-budget-session-v1" and ready["status"]=="READY" and ready["method"]=="rf_diffusion" and ready["slurm_job_id"]==expected["raw"] and ready["method_config_sha256"]==method["config_receipt"]["sha256"] and ready["target_manifest_sha256"]==TARGET["sha256"] and ready["plan_sha256"]==PLAN["sha256"],"Accepted session READY identity differs")
 ledger=e.take(d/"attempts.jsonl",pinned=rr["attempt_ledger"]);lines=ledger.read_text().splitlines();need(len(lines)==1,"Only original first failed attempt allowed");row=json.loads(lines[0])
 need(row["task_id"]==expected["task"] and row["attempt_index"]==0 and row["attempt_seed"]==expected["attempt"] and row["status"]=="ENGINEERING_FAILURE" and row["reason"]==ERROR,"Durable original failed attempt differs")
 error_receipt={"path":str(a/"attempt_result.json"),"bytes":204,"sha256":expected["error_sha"]}
 result=e.read(a/"attempt_result.json",pinned=error_receipt)
 need(result["status"]=="ENGINEERING_FAILURE" and result["reason"]==ERROR and result["method"]=="rf_diffusion" and result["seed"]==expected["attempt"],"Exact failed stage error differs")
 req=e.read(row["execution"]["request"]["path"],pinned=row["execution"]["request"]);response=e.read(row["execution"]["response"]["path"],pinned=row["execution"]["response"])
 need(req["action"]=="method-attempt" and req["attempt_dir"]==str(a) and req["seed"]==expected["attempt"] and req["attempt_index"]==0 and req["target_manifest"]==TARGET["path"] and req["target_manifest_sha256"]==TARGET["sha256"] and req["method_config_sha256"]==method["config_receipt"]["sha256"] and req["task_id"]==expected["task"] and req["plan_sha256"]==PLAN["sha256"],"Recorded request exact source/input/attempt binding differs")
 need(response["status"]=="COMPLETE" and response["reason"]==ERROR and response["attempt_result"]==error_receipt and response["request_id"]=="000000","Original completed RPC response/error differs; transport completion is not model success")
 pdb=a/"generated"/("backbone_"+str(expected["attempt"])+".pdb");trb=pdb.with_suffix(".trb")
 outp=e.take(pdb,missing=True,role="CURRENT_ORIGINAL_FAILED_ATTEMPT_GENERATED_PDB_NOT_INDEPENDENTLY_SCIENCE_ACCEPTED")
 outtrb=e.take(trb,missing=True,role="CURRENT_ORIGINAL_FAILED_ATTEMPT_OFFICIAL_TRB_DIAGNOSTIC_ONLY")
 meta={"unit":index,"raw_allocation":rows[index],"task_id":expected["task"],"replicate_seed":expected["replicate"],"attempt_seed":expected["attempt"],"original_error":ERROR,"early_engineering_failure":True,"comparable_full_budget":False,"session_returncode_is_not_causal_OOM_proof":rr["session"]["returncode"],"generated_path_basis":"Exact frozen method_attempt prefix+recorded attempt seed; no discovery or candidate selection"}
 if outp is None or outtrb is None or target is None:meta["observation"]={"status":"MISSING_ORIGINAL_INPUT_UNKNOWN_ATOM_ATTRIBUTION","frozen_gate_selection_reached":False};return meta
 try:meta["observation"]=observer(outp,outtrb,target)
 except Exception as exc:meta["observation"]={"status":"FROZEN_PRE_ATOM_GATE_ERROR_CURRENT_ORIGINAL_BYTES","frozen_gate_selection_reached":False,"error_type":type(exc).__name__,"error":str(exc),"traceback":traceback.format_exc()}
 return meta
def runtime_post(runtime):
 for x in runtime:
  b=data(x["installed_source_path"]);need(len(b)==x["installed_source_bytes"] and hashlib.sha256(b).hexdigest()==x["installed_source_sha256"],"Conditional parser runtime bytes drift")
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);args=ap.parse_args()
 allocation=cpu() # Mandatory before any content hash/copy or scientific input import/parser.
 need(pathlib.Path(sys.executable).absolute()==R/"env/rfd/bin/python" and pathlib.Path(sys.prefix)==R/"env/rfd","Same frozen RF parser interpreter environment required")
 out=safe(args.out);need(out==S/"runs"/("formal_failed_atom_coverage_"+allocation["slurm_job_id"]) and not out.exists(),"Exact new owned diagnostic directory required");out.mkdir(parents=True)
 e=Evidence(out)
 for name in ("diagnostic.py","diagnostic.sbatch"):e.take(pathlib.Path(__file__).parent/name,readonly=True,role="ACTUAL_DIAGNOSTIC_OWNED_SOURCE")
 collector_rows=scheduler(out,"13264");rows=scheduler(out,"13260",True)
 outer=e.read(F/"formal_terminal13260_cpu13264/acceptance.json",readonly=True)
 need(outer["schema"]=="formal13260_terminal_wrapper.v1" and outer["status"]=="FORMAL13260_TERMINAL_V2_COLLECTION_CPU_ACCEPTED_ROOT_COMMON_PREPARATION_PENDING" and outer["collection"]==INNER and outer["cpu_allocation"]["job_id"]=="13264" and outer["cpu_allocation"]["allocated_gpu_count"]==0,"Actual accepted outer collection authority differs")
 inner=e.read(INNER["path"],pinned=INNER,readonly=True)
 need(inner["schema"]=="formal_postprocess_collection.v2" and inner["status"]=="FORMAL_ALLOCATION_NATIVE_AND_COHORT_CLOSURE_ACCEPTED" and inner["array_job_id"]=="13260" and inner["allocation"]["job_id"]=="13264" and inner["plan"]==PLAN,"Exact original collection acceptance differs")
 fence=e.read(S/"submissions/formal13260_ALL28_terminal_metadata_20261012T0747Z/receipt.json",readonly=True)
 need(fence["schema"]=="root-ALL28-terminal-scheduler-metadata-fence.v1" and fence["all_original_slots_terminal"] is True and fence["logical_slots"]==28 and fence["completed_n"]==26 and fence["failed_n"]==2,"Root all28 metadata fence absent")
 verify_root_fence(fence,rows)
 e.take(S/"submissions/formal13264_actual_terminal_collection_metadata_seal/receipt.json",readonly=True)
 plan=e.read(PLAN["path"],pinned=PLAN,readonly=True);need(len(plan["tasks"])==28 and [x["array_index"] for x in plan["tasks"]]==list(range(28)),"Original fixed28 plan differs")
 protocol=e.read(plan["protocol_receipt"]["path"],pinned=plan["protocol_receipt"],readonly=True)
 methods=[m for m in protocol["methods"] if m["method_id"]=="rf_diffusion"];need(len(methods)==1,"Frozen RF method ambiguous");method=methods[0]
 need(SOURCE in method["adapter_receipts"],"Frozen method does not bind inspected source")
 source_copy=e.take(SOURCE["path"],pinned=SOURCE,readonly=True,role="UNCHANGED_FROZEN_GATE_SOURCE")
 for r in method["adapter_receipts"]:e.take(r["path"],pinned=r,readonly=True,role="FROZEN_METHOD_SOURCE")
 e.take(method["config_receipt"]["path"],pinned=method["config_receipt"],readonly=True,role="FROZEN_CONFIG_BYTES_NOT_EXECUTED")
 matches=[t for t in protocol["targets"] if t["target_id"]=="CRK_SH3_1CKA"];need(len(matches)==1 and matches[0]["input_manifest"]==TARGET,"Frozen target manifest differs")
 target=e.read(TARGET["path"],pinned=TARGET,readonly=True);need(target["status"]=="FROZEN_INPUT_READY" and target["target_id"]=="CRK_SH3_1CKA" and target["residue_count"]==57 and target["binder_length"]==65,"Exact frozen target identity differs")
 accepted_table=e.read(inner["files"]["run_receipts"]["path"],pinned=inner["files"]["run_receipts"],readonly=True)
 need(type(accepted_table) is list and len(accepted_table)==28 and len({x["path"] for x in accepted_table})==28,"Exact accepted all28 original receipt table required")
 accepted_by_path={x["path"]:x for x in accepted_table}
 need(set(accepted_by_path)=={str(F/"formal_runs"/("13260_"+str(i))/"run_receipt.json") for i in range(28)},"Accepted receipt table path universe differs")
 accepted_receipts={i:accepted_by_path[str(F/"formal_runs"/("13260_"+str(i))/"run_receipt.json")] for i in range(28)}
 for index in range(28):
  j=e.read(F/"formal_runs"/("13260_"+str(index))/"run_receipt.json",pinned=accepted_receipts[index],readonly=False)
  need(j["task"]==plan["tasks"][index] and j["raw_allocation_id"]==rows[index]["raw_job_id"] and j["logical_allocation_key"]=="13260_"+str(index) and j["plan"]==PLAN,"ALL28 durable original task/allocation metadata differs")
 target_pdb=e.take(target["target_pdb"]["path"],pinned=target["target_pdb"],missing=True,role="DECLARED_FROZEN_REFERENCE_TARGET_INPUT")
 e.take(target["reference_complex"]["path"],pinned=target["reference_complex"],missing=True,role="DECLARED_REFERENCE_COMPLEX_BYTES_NOT_PARSED_FOR_THIS_GATE")
 selected_target=None if target_pdb is None else dict(target)
 if selected_target is not None:selected_target["target_pdb"]=dict(target["target_pdb"],path=str(target_pdb))
 sys.path=[p for p in sys.path if p and (R/"env/rfd" in pathlib.Path(p).parents or pathlib.Path(p)==R/"env/rfd")]
 runtime=[]
 for name in ("Bio","Bio.PDB.PDBParser","numpy"):
  module=__import__(name,fromlist=["__file__"]);p=pathlib.Path(module.__file__)
  need(R/"env/rfd" in p.parents,"Exact installed frozen RF parser environment required")
  b=data(p);runtime.append({"module":name,"installed_source_path":str(p),"installed_source_bytes":len(b),"installed_source_sha256":hashlib.sha256(b).hexdigest(),"module_version":str(getattr(module,"__version__",None)),"role":"CONDITIONAL_INSTALLED_CPU_PARSER_RUNTIME_NOT_REDISTRIBUTED","archive_payload":False})
 observer,selection=extract_observer(source_copy.read_text(),out)
 observations=[unit(i,e,rows,plan,method,selected_target,observer,accepted_receipts) for i in (20,22)]
 e.post();verify(selection["derived_executed_source"],True);runtime_post(runtime)
 report={"schema":"formal-failed-rfd-atom-coverage-diagnostic.v1","status":"DIAGNOSTIC_ONLY_COMPLETE_NOT_SCIENCE_ACCEPTANCE","actual_CPU_allocation":allocation,"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scientific_scope":"COMPUTATIONAL_ONLY","experimental_binding_or_blockade":False,"new_scientific_acceptance":False,"primary_rerun":False,"rescoring":False,"atom_rebuild_or_fill":False,"source_protocol_threshold_or_budget_changes":False,"candidate_pool_or_ranking_read":False,"collector_actual_terminal":collector_rows["13264"],"all28_actual_terminal_allocation_bindings":[rows[i] for i in range(28)],"selected_failed_units":[20,22],"frozen_gate_selection":selection,"conditional_parser_runtime":{"python_executable":sys.executable,"prefix":sys.prefix,"python_version":sys.version,"modules":runtime,"excluded_from_redistribution":True,"parser_module_bytes_prepost_equal":True},"observations":observations,"original_inputs_and_owned_sources":list(e.records.values()),"missing_original_inputs":e.missing,"all_original_and_copy_bytes_prepost_equal":True,"original_files_unchanged":True,"cost_scope":"Positive failure allocations remain; diagnostic does not replace root cost auditor or create a primary rerun identity"}
 r=dump(out/"diagnostic.json",report);e.post();verify(selection["derived_executed_source"],True)
 runtime_post(runtime)
 print(json.dumps({"status":report["status"],"diagnostic":r,"unit_observation_statuses":[x["observation"]["status"] for x in observations]},ensure_ascii=False))
if __name__=="__main__":main()
