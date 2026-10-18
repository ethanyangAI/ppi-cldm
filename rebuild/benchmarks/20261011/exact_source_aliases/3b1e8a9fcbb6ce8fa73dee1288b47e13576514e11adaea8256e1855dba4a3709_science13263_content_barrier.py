#!/usr/bin/env python3
"""Distinct CPU-only full content repair; FAILED13263 preserved, explicit materialized RFD override only."""
import argparse, ast, hashlib, importlib.util, json, math, os, re, shutil, statistics, subprocess, sys, unittest
from pathlib import Path

R=Path("/lustre/users/u21111210118/projects/test9")
BASE="c3d528bb6801a7a571cdd20bfd90652e397a8540a136e1f0510ef0ccc5488dde"
ORIGINAL="13263"
STATUS="GENERIC_REPORT_CONTENT_AND_REVIEWED_MATERIALIZED_RUNTIME_CPU_REPAIR_ACCEPTED_ORIGINAL13263_FAILED_PRESERVED"
REPORT="reports/SCIENCE_AUDIT_AND_BENCHMARK_20261011_DRAFT.md"
SCORE="steps/24_benchmark_delivery/runs/native74_final_v2_13211/native74/scored/score.json"
PRED="steps/02_predict/runs/20261002T121305Z_be69fbefc530/manifest.json"
RECEIPTS={
"steps/20_screening_improvement/runs/20261011T041253Z_12951/manifest.json":"8e1889e98fe7d616597baee512768d9a0782c4e60dc45861dd9be4c6553ce141",
"steps/24_benchmark_delivery/runs/native74_final_v2_13211/native74/acceptance.json":"9effb60abceb03ca8c47b8e786f6613486bec96c90dec6aec517a1bd415fcff9",
SCORE:"cf5163b4e19adee5b0266ef3541e5b82f1e22be61f64d21fcd0bc7e763673d55",
"steps/23_common_review/bbf_diagnostics/scientific_review/runs/metric_verify_13232/acceptance.json":"c4443173e2482c394bdc9d156f055ddb7d913a388d7bcfe1aaa8dd8e5a88d2c2",
"steps/23_common_review/bbf_diagnostics/scientific_review/runs/partner_pose_13236/acceptance.json":"7ff1c4ae252e2c047a38d38aaa6c095f5dec4e8b02b9b73e1048ae24fcc730a1",
"steps/22_matched_benchmark/settings/pilot_v8/source/benchmark_runtime.py":"51b516a692d369f4d9a6ae9e3c39c0294da219c4d065420bbf9538a4af4b6562",
"steps/21_method_runtime/runs/native_runtime_handoff_13256/outputs/acceptance.json":"3726311ad3788645e2f60327c283b1b468b238a412cc9abef003b03c431394cd",
"steps/22_matched_benchmark/code/seeded_supplemental13246_audit_13254/acceptance.json":"c94d0d7f3cf05a83f1d6b6b621936296bdaeaccda00b852b314165e4bb35b04f",
"steps/22_matched_benchmark/formal_freeze_13257/plan/frozen_plan.json":"e913d1bbccd531bf88a73f6ba60e8a0de85bb03ad8bcd3455d8952ca4effe0b6",
"steps/22_matched_benchmark/formal_freeze_13257/plan/protocol.json":"26875ac0fa8382d812b89d9ed101428bd3cb2b79d661a987513a31ce309d2724",
"steps/22_matched_benchmark/formal_launchpolicy_13259/resource_policy.json":"a996cac084eb6630dc4c34a62b581f2bf298d5d720350f4f702476adb8df073e",
PRED:"a1096d4e0a31c174f67ca86fb403a44a71adc6e5d81678f1e612907b11d6fc40",
"steps/09_boltz_restore/outputs/native_predict_acceptance_11801.json":"c5d3e21b9e80ce3dcf8b167bd4cd32ae244ea1312060fadf40a3482707b3fd3b"}
HISTORICAL_LOCKS={
"core":{"path":str(R/"steps/02_predict/runs/20261002T121305Z_be69fbefc530/qc/runtime-lock-core.json"),"bytes":2823,"sha256":"cdc5a1e8814498c185315e4a4543f8f2c468f1615fe09925f915a6c79729a032"},
"boltz":{"path":str(R/"steps/02_predict/runs/20261002T121305Z_be69fbefc530/qc/runtime-lock-boltz.json"),"bytes":38197,"sha256":"5e0b40950d3746a0b345d6770a26df989c4491e7f302a1cdad313d20a979eb69"},
"rfd":{"path":str(R/"steps/03_design/runs/20261002T114616Z_cfa6d86555db/qc/runtime-lock-rfd.json"),"bytes":117798,"sha256":"77617214f2c978381ace222e41599a45de410b6bd1ad6fc1b6725994df47c03d"}}
RFD_PARENT="steps/03_design/runs/20261002T114616Z_cfa6d86555db/manifest.json"
LOCK_PARENTS={"core":PRED,"boltz":PRED,"rfd":RFD_PARENT}
LABELS=("PENDING","NOT_YET_ESTIMABLE","RETROSPECTIVE_CONTROL_GEOMETRY_DIAGNOSTIC","MPNN proposals","ENGINEERING_E2E_COMPLEMENT",BASE)
TARGETS={"MDM2_1YCR","KEAP1_2FLU","EGFR_DIII_1IVO","BCLXL_2M04","HRAS_4G0N","CRK_SH3_1CKA","BBF111_9HAG"}
PASS_TARGETS={"MDM2_1YCR","CRK_SH3_1CKA"}
TABLE_LABELS={"MDM2_1YCR":"MDM2–p53","KEAP1_2FLU":"KEAP1–NRF2","EGFR_DIII_1IVO":"EGFR DIII–EGF","BCLXL_2M04":"BCL-xL–PUMA","HRAS_4G0N":"H-Ras–Raf1","CRK_SH3_1CKA":"小鼠 Crk SH3–C3G","BBF111_9HAG":"BBF111–b4（诊断）"}

def need(ok,msg):
 if not ok: raise ValueError(msg)
def rec(p):
 p=Path(p).resolve();need(p.is_file(),"MISSING_REQUIRED_FILE: "+str(p));b=p.read_bytes()
 return {"path":str(p),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def dump(p,o):
 p=Path(p)
 with p.open("x")as handle:handle.write(json.dumps(o,indent=2,sort_keys=True)+"\n")
 p.chmod(0o444);return rec(p)
def read(p):return json.loads(Path(p).read_text())
def pin(p,sha,size=None):
 a=rec(p);need(a["sha256"]==sha and(size is None or a["bytes"]==size),"EXACT_BYTE_IDENTITY_CHANGED: "+str(p));return a
def freeze(src,dst,sha=None,size=None):
 src=Path(src);dst=Path(dst);need(not dst.exists(),"IMMUTABLE_DESTINATION_ALREADY_EXISTS: "+str(dst))
 before=rec(src);need(sha is None or before["sha256"]==sha,"ORIGINAL_BYTES_MISSING_OR_CHANGED: "+str(src))
 need(size is None or before["bytes"]==size,"ORIGINAL_BYTE_SIZE_CHANGED: "+str(src))
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);dst.chmod(0o444)
 after=rec(src);copy=rec(dst);need((before["bytes"],before["sha256"])==(after["bytes"],after["sha256"])==(copy["bytes"],copy["sha256"]),"SOURCE_CHANGED_DURING_FREEZE: "+str(src))
 return {"original":before,"frozen":copy}
def seal_tree(p):
 for q in sorted(Path(p).rglob("*"),reverse=True):
  if q.is_dir():q.chmod(0o555)
 Path(p).chmod(0o555)
def explicit_purge(text):
 text=text.lower()
 return ("invalid job id"in text)or("purged"in text and("job"in text or ORIGINAL in text))
def command(argv,prefix,allow_explicit_purge=False):
 p=subprocess.run(argv,capture_output=True,text=True);prefix=Path(prefix)
 for suffix,content in ((".stdout",p.stdout),(".stderr",p.stderr)):
  path=Path(str(prefix)+suffix)
  with path.open("x")as handle:handle.write(content)
  path.chmod(0o444)
 d={"argv":list(argv),"returncode":p.returncode,"stdout":rec(str(prefix)+".stdout"),"stderr":rec(str(prefix)+".stderr")}
 purged=allow_explicit_purge and explicit_purge(p.stdout+"\n"+p.stderr)
 if p.returncode:d["source_status"]="SOURCE_FROM_REVIEWED_DIRECT_SCHEDULER_CAPTURE"if purged else"SCHEDULER_QUERY_FAILED_NO_SOURCE_FALLBACK"
 dump(str(prefix)+".command.json",d)
 need(p.returncode==0 or purged,"SCHEDULER_COMMAND_FAILED_NO_PURGE_AUTHORITY: "+repr(argv))
 return p.stdout,d
def parse_accounting(text,jid,terminal=True):
 lines=[s.split("|")for s in text.splitlines()if s.split("|",1)[0]==str(jid)]
 need(len(lines)==1,"UNIQUE_EXACT_ACCOUNTING_ROW_REQUIRED")
 cells=lines[0];need(len(cells)>=9,"ACCOUNTING_FIELDS_MISSING")
 job,state,exitcode,elapsed,tres,user,account,name,partition=cells[:9]
 vals={}
 for token in tres.split(","):
  if not token:continue
  need("="in token,"MALFORMED_ALLOC_TRES");k,v=token.split("=",1);need(k not in vals,"DUPLICATE_ALLOC_TRES");vals[k]=v
 def num(k):
  v=vals.get(k,"0");need(re.fullmatch(r"[0-9]+",v)is not None,"NONNUMERIC_ALLOC_TRES:"+k);return int(v)
 gpu=max(num("gres/gpu"),sum(num(k)for k in vals if k.startswith("gres/gpu:")))
 need(num("cpu")>=1 and gpu==0,"REAL_PURE_CPU_ALLOCATION_REQUIRED")
 need(re.fullmatch(r"[0-9]+",elapsed)is not None,"NONNUMERIC_ELAPSED")
 need(user=="u21111210118"and account=="u21111210118"and partition=="organ","ACCOUNT_OWNER_OR_PARTITION_CHANGED")
 if terminal:need(state=="COMPLETED"and exitcode=="0:0"and name=="test9_science_report_preflight","ORIGINAL_JOB_NOT_TERMINAL_COMPLETED_ZERO")
 else:need(state=="RUNNING","CURRENT_CPU_ALLOCATION_NOT_RUNNING")
 return {"job_id":job,"state":state,"exit_code":exitcode,"elapsed_seconds":int(elapsed),"allocated_TRES":tres,"allocated_CPUs":num("cpu"),"allocated_GPUs":gpu,"user":user,"account":account,"job_name":name,"partition":partition}
def embedded_receipts(batch):
 need(batch.startswith("#!/bin/sh\n# This script was created by sbatch --wrap.\n"),"ORIGINAL_WRAP_SOURCE_HEADER_CHANGED")
 marker="<<'SCIENCE_CPU_QA'\n";need(batch.count(marker)==1 and batch.endswith("\nSCIENCE_CPU_QA\n"),"ORIGINAL_HEREDOC_ENVELOPE_CHANGED")
 source=batch.split(marker,1)[1].rsplit("\nSCIENCE_CPU_QA\n",1)[0]
 tree=ast.parse(source);found=[]
 for x in tree.body:
  if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=="receipts"for t in x.targets):found.append(ast.literal_eval(x.value))
 need(found==[RECEIPTS],"EXACT_ORIGINAL_THIRTEEN_RECEIPTS_CHANGED")
 need(all(len(x)==64 and re.fullmatch(r"[0-9a-f]{64}",x)for x in RECEIPTS.values()),"PREDECLARED_SHA_MALFORMED")
 need('assert not os.environ.get("CUDA_VISIBLE_DEVICES")'in source and "SCIENCE_REPORT_QA_AND_ENGINEERING_E2E_INPUT_PREFLIGHT_PASS_NOT_GPU_EXECUTED"in source,"ORIGINAL_CPU_OR_FINAL_CONTRACT_CHANGED")
 return source
def finite(x):
 need(isinstance(x,(int,float))and not isinstance(x,bool)and math.isfinite(x),"NONFINITE_NATIVE_NUMBER");return float(x)
def report_target_cells(rows,report):
 slots={(x["target_id"],x["engine"]):x for x in rows};selected={}
 for line in report.splitlines():
  if not line.strip().startswith("|"):continue
  cells=[s.strip()for s in line.strip().strip("|").split("|")]
  if cells and cells[0]in TABLE_LABELS.values():
   need(cells[0]not in selected,"REPORT_DUPLICATE_TARGET_ROW")
   need(len(cells)==6,"REPORT_TARGET_CELL_COUNT_CHANGED")
   selected[cells[0]]=cells
 need(set(selected)==set(TABLE_LABELS.values()),"REPORT_EXACT_SEVEN_UNIQUE_TARGET_LABELS_REQUIRED")
 for target,label in TABLE_LABELS.items():
  boltz=slots[(target,"boltz")];af2=slots[(target,"af2")];cells=selected[label]
  expected=[f'{boltz["R1_median"]:.3f}',f'{af2["R1_median"]:.3f}',f'{boltz["partner_CA_RMSD_median_A"]:.3f}',f'{af2["partner_CA_RMSD_median_A"]:.3f}']
  need(cells[1:5]==expected,"REPORT_TARGET_OR_ENGINE_SPECIFIC_NUMERIC_CELLS_MISMATCH:"+target)
  counts=[s.strip()for s in re.split("[；;]",cells[5])]
  need(counts==[str(boltz["strict_count"])+"/"+str(boltz["model_count"]),str(af2["strict_count"])+"/"+str(af2["model_count"])],"REPORT_TARGET_SPECIFIC_STRICT_COUNT_MISMATCH:"+target)
 return selected
def native_rows(scores,report):
 for label in LABELS:need(label in report,"REPORT_REQUIRED_LABEL_MISSING:"+label)
 rows=[x for x in scores["results"]if x["variant"]=="primary"]
 need(len(rows)==14,"EXACT_NATIVE14_REQUIRED");seen=set();out=[]
 for row in rows:
  target,engine=row["target_id"],row["engine"];key=(target,engine)
  need(target in TARGETS and engine in {"boltz","af2"}and key not in seen,"NATIVE_TARGET_ENGINE_SLOT_CHANGED_OR_DUPLICATED");seen.add(key)
  n=3 if engine=="boltz"else 5;models=row["models"]
  need(len(models)==n and all(x["status"]=="VALID"for x in models),"NATIVE_MODEL_COUNT_OR_VALIDITY_CHANGED")
  vals=[(finite(x["R1"]),finite(x["geometry"]["known_partner_target_aligned_CA_RMSD_A"]),finite(x["geometry"]["contact_target_residue_F1"]))for x in models]
  need(all(rmsd>=0 and 0<=f1<=1 for _,rmsd,f1 in vals),"NATIVE_GEOMETRY_RANGE_INVALID")
  r1=statistics.median(x[0]for x in vals);rmsd=statistics.median(x[1]for x in vals);strict=sum(d<=2 and f>=.5 for _,d,f in vals)
  need(strict==(n if target in PASS_TARGETS else 0),"FIXED_STRICT_NATIVE_COUNT_CHANGED")
  need(f"{r1:.3f}"in report and f"{rmsd:.3f}"in report,"REPORT_NATIVE_NUMBER_MISSING")
  out.append({"target_id":target,"engine":engine,"R1_median":r1,"partner_CA_RMSD_median_A":rmsd,"strict_count":strict,"model_count":n,"all_models_VALID":True})
 need(seen=={(t,e)for t in TARGETS for e in ("boltz","af2")},"FULL_NATIVE14_SLOT_UNIVERSE_REQUIRED")
 report_target_cells(out,report)
 return out
def original_stdout(text,rows):
 receipts={};numbers={};report=None;source=None;runtime=[];native=None;terminal=0
 for line in text.splitlines():
  if line.startswith("CURRENT_RECEIPT_SHA_PASS "):
   a=line.split();need(len(a)==4 and a[1]not in receipts and a[2].isdigit(),"ORIGINAL_RECEIPT_LOG_DUPLICATE_OR_MALFORMED")
   receipts[a[1]]={"bytes":int(a[2]),"sha256":a[3]}
  elif line.startswith("REPORT_NATIVE_NUMERIC_PASS "):
   a=line.split();need(len(a)==7 and tuple(a[1:3])not in numbers,"ORIGINAL_NATIVE_LOG_DUPLICATE_OR_MALFORMED")
   numbers[tuple(a[1:3])]=(finite(float(a[3])),finite(float(a[4])),int(a[5]),int(a[6]))
  elif line.startswith("REPORT_RECEIPT "):
   a=line.split();need(len(a)==4 and report is None and a[1]==str(R/REPORT)and a[2].isdigit()and re.fullmatch(r"[0-9a-f]{64}",a[3]),"ORIGINAL_REPORT_LOG_MISSING_IDENTITY")
   report={"path":a[1],"bytes":int(a[2]),"sha256":a[3]}
  elif line.startswith("CURRENT_GENERIC_SOURCE "):
   need(source is None,"DUPLICATE_ORIGINAL_SOURCE_LOG");source=json.loads(line.split(" ",1)[1])
  elif line.startswith("CURRENT_RUNTIME_LOCK_PASS "):runtime.append(line.split()[1])
  elif line.startswith("EXACT_OLD_PREDICTED_INPUT_AND_NATIVE_MODEL0_CHAIN_PASS "):
   need(native is None,"DUPLICATE_ORIGINAL_NATIVE_CHAIN_LOG");native=line.split(" ",1)[1]
  elif line=="SCIENCE_REPORT_QA_AND_ENGINEERING_E2E_INPUT_PREFLIGHT_PASS_NOT_GPU_EXECUTED":terminal+=1
 need(set(receipts)==set(RECEIPTS)and all(v["sha256"]==RECEIPTS[k]for k,v in receipts.items()),"ORIGINAL_THIRTEEN_RECEIPT_CONTENT_LOG_INCOMPLETE")
 expected={(x["target_id"],x["engine"]):(x["R1_median"],x["partner_CA_RMSD_median_A"],x["strict_count"],x["model_count"])for x in rows}
 need(numbers==expected,"ORIGINAL_NATIVE14_NUMERIC_LOG_DIFFERS_FROM_INDEPENDENT_REPEAT")
 need(report is not None and source is not None and source.get("python_source_sha256")==BASE and runtime==["core","rfd","boltz"]and native is not None and terminal==1,"ORIGINAL_FULL_CHECK_EVIDENCE_INCOMPLETE")
 return {"receipts":receipts,"report":report,"source":source,"native_chain_path":native,"runtime_components":runtime,"full_check_evidence":True}
def old_config(config,pose):
 need(pose.get("source")=={"kind":"boltz2_predicted","model":0},"ORIGINAL_MODEL0_SOURCE_CHANGED")
 need(config.get("structure")=={"mode":"predict_only"},"ORIGINAL_PREDICT_ONLY_CONFIG_CHANGED")
 need(config.get("design")=={"backbones":1,"sequences_per_backbone":1,"binder_length":65,"seed":42,"temperature":.1},"ORIGINAL_DESIGN_CONTRACT_CHANGED")
 need(config.get("refold",{}).get("seed")==1042 and config["refold"].get("samples")==3,"ORIGINAL_REFOLD_CONTRACT_CHANGED")
def source_tree(source):
 files=sorted((Path(source)/"src").rglob("*.py"));need(files,"EMPTY_GENERIC_SOURCE")
 return hashlib.sha256("".join(str(p.relative_to(source))+rec(p)["sha256"]for p in files).encode()).hexdigest(),[rec(p)for p in files]
def lock_parent_contract(component,parent):
 need(component in HISTORICAL_LOCKS,"UNKNOWN_RUNTIME_COMPONENT")
 need(parent.get("source",{}).get("python_source_sha256")==BASE,"HISTORICAL_LOCK_PARENT_SOURCE_NOT_C3")
 need(parent.get("runtime",{}).get(component,{}).get("lock")==HISTORICAL_LOCKS[component],"HISTORICAL_LOCK_PARENT_FIELD_CHANGED")
 if component=="rfd":
  need(parent.get("status")=="DESIGNS_GENERATED"and str(parent.get("execution",{}).get("slurm_job_id"))=="11728","RFD_HISTORICAL_ORIGIN_NOT_11728")
 else:
  need(parent.get("status")=="POSE_ACCEPTED"and str(parent.get("execution",{}).get("slurm_job_id"))=="11801","PREDICTION_HISTORICAL_ORIGIN_NOT_11801")
def exact_runtime(actual,expected,component):
 need(actual==expected,"CURRENT_RUNTIME_DRIFT_NO_REFRESH:"+component)
def cpu_accounting(out,jid,terminal):
 text,receipt=command(["sacct","-X","-j",str(jid),"--noheader","--parsable2","--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocTRES,User%64,Account%64,JobName%100,Partition%64"],out/("original_sacct"if terminal else"current_sacct"))
 return {"numeric":parse_accounting(text,jid,terminal),"capture":receipt}
def scheduler_metadata(text,terminal,prepared_state="PENDING"):
 fixed=("JobId=13263 ","JobName=test9_science_report_preflight ","UserId=u21111210118(","Account=u21111210118 ","Partition=organ ","WorkDir="+str(R),"StdOut="+str(R/"logs/science_report_preflight_13263.out"),"StdErr="+str(R/"logs/science_report_preflight_13263.err"),"NumCPUs=1 ","CPUs/Task=1 ")
 for value in fixed:need(value in text,"ORIGINAL_SCHEDULER_OWNER_PATH_RESOURCE_CHANGED:"+value)
 need(prepared_state in {"PENDING","RUNNING","COMPLETED","FAILED","CANCELLED"},"PREPARED_SCHEDULER_STATE_UNDECLARED")
 need(("JobState=COMPLETED "if terminal else"JobState="+prepared_state+" ")in text,"ORIGINAL_SCHEDULER_CAPTURE_STATE_CHANGED")
def original_scheduler(package,out):
 prepared=(package/"original13263.prepared.scontrol").read_text();metadata=read(package/"preparation_capture.json")
 scheduler_metadata(prepared,False,metadata.get("original_capture_state",""))
 need(metadata.get("original_job_id")==ORIGINAL and metadata.get("status")=="SOURCE_AND_SCHEDULER_METADATA_PREPARED_NOT_EXECUTED","DIRECT_REVIEWED_CAPTURE_RECEIPT_MISSING")
 expected=[("original13263.batch",["scontrol","write","batch_script",ORIGINAL,"-"]),("original13263.prepared.scontrol",["scontrol","show","job",ORIGINAL,"-o"])]
 need(metadata.get("captures")==[{"argv":argv,"returncode":0,"stdout_file":filename,"stderr_file":filename+".stderr","hash_computation":"NOT_EXECUTED","scientific_tests":"NOT_EXECUTED"}for filename,argv in expected],"DIRECT_REVIEWED_CAPTURE_COMMAND_AUTHORITY_CHANGED")
 batch=(package/"original13263.batch").read_text()
 live_batch,batch_capture=command(["scontrol","write","batch_script",ORIGINAL,"-"],out/"original_batch_readback",True)
 if batch_capture["returncode"]==0:need(live_batch==batch,"EXACT_ORIGINAL_SCHEDULER_BATCH_CHANGED")
 scheduler,scheduler_capture=command(["scontrol","show","job",ORIGINAL,"-o"],out/"original_scontrol_terminal",True)
 if scheduler_capture["returncode"]==0:scheduler_metadata(scheduler,True)
 return {"batch_actual_query":batch_capture,"terminal_metadata_actual_query":scheduler_capture,"prepared_batch":rec(package/"original13263.batch"),"prepared_metadata":rec(package/"original13263.prepared.scontrol"),"prepared_capture_receipt":rec(package/"preparation_capture.json"),"authority_status":"SOURCE_FROM_REVIEWED_DIRECT_SCHEDULER_CAPTURE"if batch_capture["returncode"]or scheduler_capture["returncode"]else"SOURCE_FROM_IDENTICAL_CURRENT_AND_REVIEWED_DIRECT_SCHEDULER_CAPTURE","only_explicit_scheduler_purge_fallback_allowed":True}

# Distinct root-reviewed repair identity. Original13263 remains FAILED history.
DIAG={"path":str(R/"steps/24_benchmark_delivery/runs/runtime_drift_diagnostic_13275/diagnostic.json"),"bytes":32980,"sha256":"fec7f6a05123d3702a9ad2f034bc25f33cab2810051a146ef7a997d507be2f88"}
CACHE_DIAG={"path":str(R/"steps/24_benchmark_delivery/runs/rfd_igso3_cache_diagnostic_13278/diagnostic.json"),"bytes":3250,"sha256":"934e984e3c44bcf734ab212207a24d5ef9c1301f5cb6efe7a4755de4b05450db"}
CACHE={"path":str(R/"vendor/RFdiffusion/schedules/T_50_omega_1000_min_sigma_0_02_min_b_1_5_max_b_2_5_schedule_linear.pkl"),"bytes":8016330,"sha256":"cfac2959f952bec968c5bb68b71e2caac37f106ddda0b3f370dd853211e1a7b5"}
MAT_STATUS="RFD_MATERIALIZED_IGSO3_RUNTIME_CPU_QUALIFIED_DEFAULT_LOCK_UNCHANGED"
OVERRIDE_STATUS="REVIEWED_FULL_MATERIALIZED_RFD_RUNTIME_OVERRIDE_CPU_ACCEPTED_DEFAULT_UNCHANGED"
def verify_receipt(r,readonly=True):
 need(isinstance(r,dict)and {"path","bytes","sha256"}<=r.keys()and type(r["bytes"])is int and re.fullmatch(r"[0-9a-f]{64}",r["sha256"]),"EXACT_RECEIPT_REQUIRED")
 p=Path(r["path"]);need(p.is_absolute()and p.is_relative_to(R)and p.resolve()==p and p.is_file()and not p.is_symlink(),"EXACT_AUTHORITY_FILE_REQUIRED")
 need(not readonly or not(p.stat().st_mode&0o222),"ACCEPTED_INPUT_MUST_BE_READONLY")
 pin(p,r["sha256"],r["bytes"]);return p
def repair_request(q):
 need(q.get("schema")=="generic-report-materialized-runtime-repair-request.v2"and q.get("root_owned")is True,"DISTINCT_ROOT_REVIEWED_REPAIR_REQUEST_REQUIRED")
 need(q.get("default_write_allowed")is False and q.get("original13263_failure_preserved")is True and q.get("original_job_id")==ORIGINAL,"NO_DEFAULT_WRITE_OR_ORIGINAL_FAILURE_UPGRADE")
 m=q.get("materialization_acceptance")
 need(isinstance(m,dict)and m.get("path")==str(R/"steps/24_benchmark_delivery/runs/rfd_cache_materialization_13281/acceptance.json"),"EXACT_REAL13281_ACCEPTANCE_REQUIRED")
 return m
def materialization_contract(m):
 need(m.get("schema")=="rfd-cache-materialization.v1"and m.get("status")==MAT_STATUS and m.get("job_id")=="13281","ACTUAL13281_CONTENT_ACCEPTANCE_REQUIRED")
 need(m.get("default_lock_updated")is False and m.get("application_to_default_runtime_performed")is False and m.get("model_inference_performed")is False and m.get("GPU_allocated")==0,"NO_DEFAULT_OR_MODEL_CHANGE_ALLOWED")
 need(m.get("cause_diagnostic")==DIAG and m.get("single_cache_diagnostic")==CACHE_DIAG and m.get("original_cache")==CACHE,"EXACT_DIAGNOSED_SINGLE_CACHE_IDENTITY_REQUIRED")
 need(m.get("fixed_numeric_equivalence")=={"rtol":1e-8,"atol":1e-8},"PREDECLARED_NUMERIC_TOLERANCE_CHANGED")
 spec=m.get("official_constructor_arguments",{})
 fixed={"T":50,"min_sigma":.02,"max_sigma":1.5,"min_b":1.5,"max_b":2.5,"num_omega":1000,"schedule":"linear","L":2000}
 need(all(spec.get(k)==v for k,v in fixed.items())and set(spec)==set(fixed)|{"cache_dir"},"EXACT_OFFICIAL_CACHE_CONSTRUCTOR_REQUIRED")
 need(spec["cache_dir"]==str(R/"steps/24_benchmark_delivery/runs/rfd_cache_materialization_13281/independent_regenerated_schedule"),"EXACT_ISOLATED_REGENERATION_ROOT_REQUIRED")
 rows=m.get("array_crosschecks",[])
 need(len(rows)==5 and {x.get("key")for x in rows}=={"cdf","score_norm","exp_score_norms","discrete_omega","discrete_sigma"},"COMPLETE_FIVE_CACHE_ARRAYS_REQUIRED")
 for x in rows:
  need(x.get("fixed_numeric_equivalent")is True and isinstance(x.get("shape"),list)and bool(x["shape"])and isinstance(x.get("dtype"),str)and finite(x.get("max_absolute_difference"))>=0,"CACHE_ARRAY_CONTENT_QUALIFICATION_INCOMPLETE")
 need(m.get("original_default_lock",{}).get("bytes")==HISTORICAL_LOCKS["rfd"]["bytes"]and m.get("original_default_lock",{}).get("sha256")==HISTORICAL_LOCKS["rfd"]["sha256"],"OLD_RFD_LOCK_IDENTITY_NOT_PRESERVED")
 need(m.get("old_pre_materialization_lock_preserved")is True and m.get("baseline_vendor225_bytes_unchanged")is True and m.get("all_other_RFD_runtime_fields_unchanged")is True and m.get("core_and_boltz_captured_match_historical")is True,"UNRELATED_RUNTIME_DRIFT_NOT_RESOLVED")
 need(m.get("scientific_generation_or_selection_settings_changed")is False,"SCIENTIFIC_SETTINGS_CHANGED")
 need(isinstance(m.get("source_records"),list)and len(m["source_records"])==5 and {Path(x["path"]).name for x in m["source_records"]}=={"materialization.py","diffusion.py","igso3.py","base.yaml","common.py"},"EXACT_FIVE_MATERIALIZATION_SOURCE_RECORDS_REQUIRED")
 need(m.get("materialized_runtime_lock",{}).get("path")==str(R/"steps/24_benchmark_delivery/runs/rfd_cache_materialization_13281/runtime-lock-rfd-materialized.json"),"FULL_NEW_RFD_LOCK_EXACT_PATH_REQUIRED")
 return m["materialized_runtime_lock"]
def rfd_full_delta_contract(old,new):
 left=__import__("copy").deepcopy(old);right=__import__("copy").deepcopy(new)
 a=left["vendor_files"].pop("RFdiffusion");b=right["vendor_files"].pop("RFdiffusion")
 need(left==right and a["path_root"]==b["path_root"],"ONLY_RF_FINGERPRINT_FIELDS_MAY_DIFFER")
 need(a["file_count"]==225 and b["file_count"]==226 and b["bytes"]-a["bytes"]==CACHE["bytes"],"FULL226_CACHE_INCLUDED_OLD225_BYTES_REQUIRED")
 need(a["tree_sha256"]!=b["tree_sha256"],"REAL_CACHE_MATERIALIZATION_FINGERPRINT_REQUIRED")
 return {"old_fingerprint":a,"full_new_fingerprint":b,"cache_included_not_excluded":True}

def cache_arrays_contract(historical,regenerated,materialization):
 import numpy as np
 keys={"cdf","score_norm","exp_score_norms","discrete_omega","discrete_sigma"}
 need(set(historical)==set(regenerated)==keys,"ALL_FIVE_ACTUAL_CACHE_ARRAYS_REQUIRED")
 rows=[]
 for key in sorted(keys):
  x=np.asarray(historical[key]);y=np.asarray(regenerated[key])
  need(x.shape==y.shape and x.dtype==y.dtype and np.isfinite(x).all()and np.isfinite(y).all(),"ACTUAL_CACHE_SHAPE_DTYPE_OR_FINITE_FAILURE")
  delta=np.abs(x-y);ok=bool(np.allclose(x,y,rtol=1e-8,atol=1e-8,equal_nan=False))
  row={"key":key,"shape":list(x.shape),"dtype":str(x.dtype),"exact_array_equal":bool(np.array_equal(x,y)),"max_absolute_difference":float(delta.max())if delta.size else 0.0,"fixed_numeric_equivalent":ok}
  need(ok,"ACTUAL_CACHE_NUMERIC_EQUIVALENCE_FAILED:"+key);rows.append(row)
 need(rows==materialization["array_crosschecks"],"ACTUAL_FIVE_ARRAY_CONTENT_DIFFERS_FROM_ORIGINAL13281_REPORT")
 return rows
def reverify_materialization_arrays(materialization):
 import pickle
 original=verify_receipt(materialization["original_cache"],False);regenerated=verify_receipt(materialization["regenerated_cache"],True)
 # Both trusted input pickle bytes are exact root-reviewed artifacts, never arbitrary user files.
 with original.open("rb")as h:historical=pickle.load(h)
 with regenerated.open("rb")as h:derived=pickle.load(h)
 rows=cache_arrays_contract(historical,derived,materialization)
 return {"status":"ACTUAL_ORIGINAL_AND_INDEPENDENT_REGENERATED_FIVE_ARRAYS_RECOMPARED_FIXED1E8","original_cache":materialization["original_cache"],"regenerated_cache":materialization["regenerated_cache"],"fixed_numeric_equivalence":{"rtol":1e-8,"atol":1e-8},"array_crosschecks":rows,"new_RFD_lock_still_includes_original_exact_cache":True}


def materialization_source_lineage(out,materialization):
 pending=R/"steps/24_benchmark_delivery/pending/rfd_cache_materialization_v2"
 executed=R/"steps/24_benchmark_delivery/frozen/rfd_cache_materialization_v2_13281/code"
 names={"materialization.py","materialization_cpu.sbatch"}
 need({p.name for p in executed.iterdir()}==names and {p.name for p in pending.iterdir()}==names,"EXACT_TWO_FILE_MATERIALIZATION_SOURCE_UNIVERSE_REQUIRED")
 source_rows=[]
 for name in sorted(names):
  a=rec(pending/name);b=rec(executed/name);verify_receipt(a,True);verify_receipt(b,True)
  need((a["bytes"],a["sha256"])==(b["bytes"],b["sha256"]),"EXECUTED_MATERIALIZATION_SOURCE_DIFFERS_FROM_REVIEWED_SUBMITTED_SOURCE")
  source_rows.append({"reviewed_source":a,"executed_source":b,"copy":freeze(executed/name,out/"frozen/materialization_source"/name,b["sha256"],b["bytes"])})
 actual_self=next(x["executed_source"]for x in source_rows if Path(x["executed_source"]["path"]).name=="materialization.py")
 need(materialization["source_records"][0]==actual_self,"MATERIALIZATION_SELF_SOURCE_RECORD_NOT_ACTUAL_EXECUTED_FROZEN_ENTRY")
 submission=R/"steps/24_benchmark_delivery/submissions/rfd_cache_materialization_v2_primary_claim/submission_receipt.json"
 sr=rec(submission);q=read(verify_receipt(sr,True))
 need(q.get("schema")=="root-pure-cpu-cache-requalification-submission.v1"and q.get("job_id")=="13281"and q.get("argv")==["sbatch","--parsable",str(pending/"materialization_cpu.sbatch")]and q.get("raw_stdout")=="13281\n"and q.get("raw_stderr")==""and q.get("returncode")==0,"ACTUAL_ROOT13281_SUBMISSION_IDENTITY_REQUIRED")
 need(q.get("requests_gpu")is False and q.get("defaultlock_changes")is False and q.get("fixed_comparison")=={"rtol":1e-8,"atol":1e-8},"SUBMITTED_MATERIALIZATION_POLICY_CHANGED")
 submitcopy=freeze(submission,out/"frozen/materialization_source/root_submission_receipt.json",sr["sha256"],sr["bytes"])
 return dump(out/"materialization_source_lineage.json",{"status":"EXACT_ACTUAL13281_ROOT_SUBMISSION_AND_TWO_EXECUTED_SOURCE_FILES_CPU_VERIFIED","actual_root_submission":submitcopy,"source_entries":source_rows,"actual_materialization_self_source":actual_self,"source_manifest_added_only_by_new_successor":True,"original13281_source_unmodified":True})

def terminal_repair_accounting(text,jid):
 rows=[x.split("|")for x in text.splitlines()if x.split("|",1)[0]==str(jid)]
 need(len(rows)==1 and len(rows[0])>=9,"UNIQUE_REAL_TERMINAL_ACCOUNTING_REQUIRED")
 job,state,exitcode,elapsed,tres,user,account,name,partition=rows[0][:9];vals={}
 for item in tres.split(","):
  need("="in item,"MISSING_NUMERIC_ALLOC_TRES");k,v=item.split("=",1);need(k not in vals,"DUPLICATE_ALLOC_TRES");vals[k]=v
 def n(k):
  value=vals.get(k,"0");need(re.fullmatch(r"[0-9]+",value),"NONNUMERIC_ALLOC_TRES");return int(value)
 need(user=="u21111210118"and account=="u21111210118"and partition=="organ"and elapsed.isdigit()and n("cpu")>=1 and max(n("gres/gpu"),sum(n(k)for k in vals if k.startswith("gres/gpu:")))==0,"EXACT_TERMINAL_PURECPU_OWNERSHIP_REQUIRED")
 if str(jid)==ORIGINAL:need(state=="FAILED"and exitcode=="1:0"and name=="test9_science_report_preflight","ORIGINAL13263_MUST_REMAIN_REAL_FAILED1")
 else:need(str(jid)in {"13275","13278","13281"}and state=="COMPLETED"and exitcode=="0:0","ACTUAL_REQUIRED_RUNTIME_JOB_COMPLETED0_REQUIRED")
 return {"job_id":job,"state":state,"exit_code":exitcode,"elapsed_seconds":int(elapsed),"allocated_CPUs":n("cpu"),"allocated_GPUs":0,"allocated_TRES":tres,"user":user,"account":account,"job_name":name,"partition":partition}
def terminal_repair(out,jid):
 text,capture=command(["sacct","-X","-j",str(jid),"--noheader","--parsable2","--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocTRES,User%64,Account%64,JobName%100,Partition%64"],out/("terminal_"+str(jid)))
 return {"numeric":terminal_repair_accounting(text,jid),"capture":capture}
def historical225_recompute(common,old_fingerprint):
 vendor=R/"vendor/RFdiffusion";all_rows=common.tree_records(vendor)
 expected_cache=next((x for x in all_rows if x["path"]==CACHE["path"]),None)
 need(expected_cache==CACHE and len(all_rows)==226,"EXACT_ONE_CACHE_IN_REAL226_INVENTORY_REQUIRED")
 retained=[x for x in all_rows if x["path"]!=CACHE["path"]]
 payload=[{"relative_path":str(Path(x["path"]).relative_to(vendor)),"sha256":x["sha256"],"bytes":x["bytes"]}for x in retained]
 fingerprint={"path_root":str(vendor),"file_count":len(payload),"bytes":sum(x["bytes"]for x in payload),"tree_sha256":hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()}
 need(fingerprint==old_fingerprint,"ALL_PREEXISTING225_REAL_VENDOR_BYTES_CHANGED")
 return {"status":"EXACT_HISTORICAL225_FINGERPRINT_RECONSTRUCTED_FORENSIC_ONLY_NEWLOCK_STILL_INCLUDES226","actual_full_inventory":all_rows,"historical225_fingerprint":fingerprint,"only_removed_for_historical_comparison":CACHE,"live_vendor_files_deleted":False,"new_runtime_cache_excluded":False}
def failed_original_stdout(text,rows):
 receipts={};numbers={};report=None;source=None;runtime=[];native=None;terminal=0
 for line in text.splitlines():
  if line.startswith("CURRENT_RECEIPT_SHA_PASS "):
   a=line.split();need(len(a)==4 and a[1]not in receipts and a[2].isdigit(),"ORIGINAL_RECEIPT_LOG_DUPLICATE_OR_MALFORMED")
   receipts[a[1]]={"bytes":int(a[2]),"sha256":a[3]}
  elif line.startswith("REPORT_NATIVE_NUMERIC_PASS "):
   a=line.split();need(len(a)==7 and tuple(a[1:3])not in numbers,"ORIGINAL_NATIVE_LOG_DUPLICATE_OR_MALFORMED")
   numbers[tuple(a[1:3])]=(finite(float(a[3])),finite(float(a[4])),int(a[5]),int(a[6]))
  elif line.startswith("REPORT_RECEIPT "):
   a=line.split();need(len(a)==4 and report is None and a[1]==str(R/REPORT)and a[2].isdigit()and re.fullmatch(r"[0-9a-f]{64}",a[3]),"ORIGINAL_REPORT_LOG_MISSING_IDENTITY")
   report={"path":a[1],"bytes":int(a[2]),"sha256":a[3]}
  elif line.startswith("CURRENT_GENERIC_SOURCE "):
   need(source is None,"DUPLICATE_ORIGINAL_SOURCE_LOG");source=json.loads(line.split(" ",1)[1])
  elif line.startswith("CURRENT_RUNTIME_LOCK_PASS "):runtime.append(line.split()[1])
  elif line.startswith("EXACT_OLD_PREDICTED_INPUT_AND_NATIVE_MODEL0_CHAIN_PASS "):
   need(native is None,"DUPLICATE_ORIGINAL_NATIVE_CHAIN_LOG");native=line.split(" ",1)[1]
  elif line=="SCIENCE_REPORT_QA_AND_ENGINEERING_E2E_INPUT_PREFLIGHT_PASS_NOT_GPU_EXECUTED":terminal+=1
 need(set(receipts)==set(RECEIPTS)and all(v["sha256"]==RECEIPTS[k]for k,v in receipts.items()),"ORIGINAL_THIRTEEN_RECEIPT_CONTENT_LOG_INCOMPLETE")
 expected={(x["target_id"],x["engine"]):(x["R1_median"],x["partner_CA_RMSD_median_A"],x["strict_count"],x["model_count"])for x in rows}
 need(numbers==expected,"ORIGINAL_NATIVE14_NUMERIC_LOG_DIFFERS_FROM_INDEPENDENT_REPEAT")
 need(report is not None and source is not None and source.get("python_source_sha256")==BASE and runtime==["core"]and native is not None and terminal==0,"ORIGINAL_REAL_FAILED_PARTIAL_HISTORY_CHANGED")
 return {"receipts":receipts,"report":report,"source":source,"native_chain_path":native,"runtime_components":runtime,"full_check_evidence":False,"original_failure_preserved":True}
def failed_original_scheduler(package,out):
 prepared=(package/"original13263.prepared.scontrol").read_text();metadata=read(package/"preparation_capture.json")
 scheduler_metadata(prepared,False,metadata.get("original_capture_state",""))
 need(metadata.get("original_job_id")==ORIGINAL and metadata.get("status")=="SOURCE_AND_SCHEDULER_METADATA_PREPARED_NOT_EXECUTED","DIRECT_REVIEWED_CAPTURE_RECEIPT_MISSING")
 expected=[("original13263.batch",["scontrol","write","batch_script",ORIGINAL,"-"]),("original13263.prepared.scontrol",["scontrol","show","job",ORIGINAL,"-o"])]
 need(metadata.get("captures")==[{"argv":argv,"returncode":0,"stdout_file":filename,"stderr_file":filename+".stderr","hash_computation":"NOT_EXECUTED","scientific_tests":"NOT_EXECUTED"}for filename,argv in expected],"DIRECT_REVIEWED_CAPTURE_COMMAND_AUTHORITY_CHANGED")
 batch=(package/"original13263.batch").read_text()
 live_batch,batch_capture=command(["scontrol","write","batch_script",ORIGINAL,"-"],out/"original_batch_readback",True)
 if batch_capture["returncode"]==0:need(live_batch==batch,"EXACT_ORIGINAL_SCHEDULER_BATCH_CHANGED")
 scheduler,scheduler_capture=command(["scontrol","show","job",ORIGINAL,"-o"],out/"original_scontrol_terminal",True)
 if scheduler_capture["returncode"]==0:scheduler_metadata(scheduler,False,"FAILED")
 return {"batch_actual_query":batch_capture,"terminal_metadata_actual_query":scheduler_capture,"prepared_batch":rec(package/"original13263.batch"),"prepared_metadata":rec(package/"original13263.prepared.scontrol"),"prepared_capture_receipt":rec(package/"preparation_capture.json"),"authority_status":"SOURCE_FROM_REVIEWED_DIRECT_SCHEDULER_CAPTURE"if batch_capture["returncode"]or scheduler_capture["returncode"]else"SOURCE_FROM_IDENTICAL_CURRENT_AND_REVIEWED_DIRECT_SCHEDULER_CAPTURE","only_explicit_scheduler_purge_fallback_allowed":True}

def run(out,request_path):
 out=Path(out).resolve();need(out.is_relative_to(R/"steps/24_benchmark_delivery/runs"),"OUTPUT_MUST_BE_ISOLATED_AUTHORITY_RUN");out.mkdir(parents=True,exist_ok=False)
 phase="pure_CPU_guard";allocation=None;package=Path(__file__).resolve().parent
 try:
  jid=os.environ.get("SLURM_JOB_ID","");need(jid.isdigit()and jid!=ORIGINAL,"ACTUAL_NEW_CPU_JOB_REQUIRED")
  need(not os.environ.get("CUDA_VISIBLE_DEVICES")and not os.environ.get("PYTHONPATH")and os.environ.get("PYTHONNOUSERSITE")=="1","NO_GPU_OR_INJECTED_PYTHON_ENV_ALLOWED")
  need(os.environ.get("JAX_PLATFORMS")=="cpu"and sys.dont_write_bytecode,"CPU_ONLY_NO_BYTECODE_REQUIRED")
  allocation=cpu_accounting(out,jid,False);need(not(package.stat().st_mode&0o222),"REVIEWED_PACKAGE_MUST_BE_READONLY")
  phase="freeze_original_scheduler_and_all_scoped_bytes";frozen=out/"frozen";frozen.mkdir();runner=[]
  for p in sorted(package.iterdir()):
   if p.is_file():
    need(not p.is_symlink()and not(p.stat().st_mode&0o222),"EVERY_REVIEWED_PACKAGE_FILE_MUST_BE_READONLY_REGULAR")
    runner.append(freeze(p,frozen/"barrier_source"/p.name))
  batch=(package/"original13263.batch").read_text();embedded=embedded_receipts(batch)
  scheduler_authority=failed_original_scheduler(package,out)
  original_allocation=terminal_repair(out,ORIGINAL)
  request_path=verify_receipt(rec(request_path),True);q=read(request_path);mat_receipt=repair_request(q)
  materialization=read(verify_receipt(mat_receipt,True));new_rfd_receipt=materialization_contract(materialization)
  materialization_source=materialization_source_lineage(out,materialization)
  actual_arrays=reverify_materialization_arrays(materialization)
  arrayproof=dump(out/"materialization_five_arrays_independent_repeat.json",actual_arrays)
  runtime_prerequisites={j:terminal_repair(out,j)for j in ("13275","13278","13281")}
  diagnosed=read(verify_receipt(DIAG,True));cache_diagnosed=read(verify_receipt(CACHE_DIAG,True))
  need(diagnosed.get("status")=="DIAGNOSTIC_CAPTURE_COMPLETE_RUNTIME_NOT_ACCEPTED"and diagnosed.get("runtime_mismatch_components")==["rfd"],"EXACT_ORIGINAL_RUNTIME_DIAGNOSIS_REQUIRED")
  need(cache_diagnosed.get("status")=="RFD_RUNTIME_DRIFT_SINGLE_DERIVED_IGSO3_CACHE_IDENTIFIED_NOT_LOCK_ACCEPTANCE"and cache_diagnosed.get("source_provenance",{}).get("python_source_sha256")==BASE,"EXACT_CACHE_DIAGNOSIS_SOURCE_REQUIRED")
  for obj in (diagnosed,cache_diagnosed,materialization):
   def refs(v):
    if isinstance(v,dict):
     if {"path","bytes","sha256"}<=v.keys():yield v
     else:
      for value in v.values():yield from refs(value)
    elif isinstance(v,list):
     for value in v:yield from refs(value)
   for rr in refs(obj):verify_receipt(rr,False)
  matf=freeze(mat_receipt["path"],frozen/"materialization/acceptance.json",mat_receipt["sha256"],mat_receipt["bytes"])
  diagf=freeze(DIAG["path"],frozen/"materialization/diagnostic13275.json",DIAG["sha256"],DIAG["bytes"])
  cachef=freeze(CACHE_DIAG["path"],frozen/"materialization/diagnostic13278.json",CACHE_DIAG["sha256"],CACHE_DIAG["bytes"])
  logf=freeze(R/"logs/science_report_preflight_13263.out",frozen/"original13263.stdout")
  errf=freeze(R/"logs/science_report_preflight_13263.err",frozen/"original13263.stderr")
  frozen_inputs={}
  for rel,sha in RECEIPTS.items():frozen_inputs[rel]=freeze(R/rel,frozen/"exact_inputs"/rel,sha)
  reportf=freeze(R/REPORT,frozen/"exact_inputs"/REPORT,"ddf52048693a87778adabc7dbbc6d90ead40ddfe7d7741449f506a44bd6ea40d",47237)
  lock_parents={PRED:frozen_inputs[PRED],RFD_PARENT:freeze(R/RFD_PARENT,frozen/"exact_inputs"/RFD_PARENT)}
  historical_locks={};locks={}
  for component in ("core","rfd","boltz"):
   declared=HISTORICAL_LOCKS[component];parent=lock_parents[LOCK_PARENTS[component]]
   lock_parent_contract(component,read(parent["frozen"]["path"]))
   historical_locks[component]={"origin_manifest":parent,"origin_field":["runtime",component,"lock"],"declared":declared,"copy":freeze(declared["path"],frozen/"historical_runtime_locks"/("runtime-lock-"+component+".json"),declared["sha256"],declared["bytes"])}
   locks[component]=freeze(R/"source/environment"/("runtime-lock-"+component+".json"),frozen/"generic_source/environment"/("runtime-lock-"+component+".json"),declared["sha256"],declared["bytes"])
  overrides={}
  for component in ("core","rfd","boltz"):
   source=new_rfd_receipt if component=="rfd"else HISTORICAL_LOCKS[component]
   verify_receipt(source,False)
   overrides[component]=freeze(source["path"],frozen/"runtime_override"/("runtime-lock-"+component+".json"),source["sha256"],source["bytes"])
  delta=rfd_full_delta_contract(read(historical_locks["rfd"]["copy"]["frozen"]["path"]),read(overrides["rfd"]["frozen"]["path"]))
  live_sha,live_files=source_tree(R/"source");need(live_sha==BASE,"CURRENT_GENERIC_SOURCE_NOT_EXACT_C3")
  sourcefiles=[]
  for rr in live_files:sourcefiles.append(freeze(rr["path"],frozen/"generic_source"/Path(rr["path"]).relative_to(R/"source"),rr["sha256"],rr["bytes"]))
  frozen_sha,_=source_tree(frozen/"generic_source");need(frozen_sha==BASE and source_tree(R/"source")[0]==BASE,"FULL_FROZEN_AND_LIVE_GENERIC_C3_CLOSURE_REQUIRED")
  seal_tree(frozen);dump(out/"frozen_input_manifest.json",{"schema":"science13263-frozen-inputs.v1","runner":runner,"original_logs":[logf,errf],"required_thirteen_inputs":frozen_inputs,"report":reportf,"generic_source":sourcefiles,"runtime_locks":locks,"historical_runtime_lock_anchors":historical_locks,"python_source_sha256":frozen_sha,"runtime_override":overrides,"materialization":matf,"diagnostics":[diagf,cachef],"original_failure_preserved":True})
  phase="CPU_contracts"
  for path in sorted((frozen/"barrier_source").glob("*.py")):compile(path.read_text(),str(path),"exec")
  _,bash_contract=command(["bash","-n",str(frozen/"barrier_source/science13263_content_barrier_cpu.sbatch")],out/"launcher_bash_n")
  source_spec=importlib.util.spec_from_file_location("science13263_content_barrier",frozen/"barrier_source/science13263_content_barrier.py")
  source_module=importlib.util.module_from_spec(source_spec);sys.modules["science13263_content_barrier"]=source_module;source_spec.loader.exec_module(source_module)
  spec=importlib.util.spec_from_file_location("science13263_contracts",frozen/"barrier_source/test_science13263_content_barrier.py");module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  suite=unittest.defaultTestLoader.loadTestsFromModule(module)
  need(suite.countTestCases()==CONTRACT_COUNT,"DECLARED_CONTRACT_COUNT_CHANGED")
  with(out/"contracts.log").open("x")as log:tested=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
  (out/"contracts.log").chmod(0o444)
  need(tested.wasSuccessful(),"CPU_SOURCE_CONTRACTS_FAILED")
  contracts=dump(out/"contracts.json",{"status":"PASS","tests":tested.testsRun,"failures":len(tested.failures),"errors":len(tested.errors),"log":rec(out/"contracts.log"),"source_files":[x["frozen"]for x in runner],"owned_python_compile_PASS":True,"bash_syntax_PASS":True,"bash_syntax":bash_contract})
  phase="independent_native14_report_and_original_log_repeat"
  report=Path(reportf["frozen"]["path"]).read_text()
  rows=native_rows(read(frozen_inputs[SCORE]["frozen"]["path"]),report)
  original=failed_original_stdout(Path(logf["frozen"]["path"]).read_text(),rows)
  need("AssertionError: ('CURRENT_RUNTIME_DRIFT', 'rfd')"in Path(errf["frozen"]["path"]).read_text(),"ORIGINAL_RFD_FAILURE_STDERR_IDENTITY_CHANGED")
  need(original["report"]["sha256"]==reportf["original"]["sha256"]and original["report"]["bytes"]==reportf["original"]["bytes"],"ORIGINAL_DRAFT_REPORT_BYTES_CHANGED_NO_REPORT_IDENTITY_WAIVER")
  for rel,x in frozen_inputs.items():need(x["original"]["sha256"]==original["receipts"][rel]["sha256"]and x["original"]["bytes"]==original["receipts"][rel]["bytes"],"ORIGINAL_INPUT_LOG_IDENTITY_DIFFERS:"+rel)
  native_receipt=dump(out/"native14_independent_repeat.json",{"status":"ALL14_PRIMARY_NATIVE_ROWS_RECOMPUTED_REPORT_AND_ORIGINAL_LOG_MATCH","rows":rows,"score":frozen_inputs[SCORE],"report":reportf,"required_labels":list(LABELS)})
  phase="old11801_load_run_and_design_pose_content_repeat"
  sys.path.insert(0,str(frozen/"generic_source/src"))
  need(not any(k=="ppiblocker"or k.startswith("ppiblocker.")for k in sys.modules),"STALE_GENERIC_IMPORT_FORBIDDEN")
  from ppiblocker import common,pipeline
  need(Path(common.__file__).resolve().is_relative_to(frozen/"generic_source/src")and Path(pipeline.__file__).resolve().is_relative_to(frozen/"generic_source/src"),"EXACT_FROZEN_OLD_SOURCE_IMPORT_REQUIRED")
  m=common.load_run(Path(frozen_inputs[PRED]["frozen"]["path"]),{"POSE_ACCEPTED"})
  config,pose,native= pipeline.validate_design_pose(m);old_config(config,pose)
  need(m["source"]["python_source_sha256"]==BASE and common.source_provenance()["python_source_sha256"]==BASE,"OLD_MANIFEST_AND_ACTUAL_SOURCE_NOT_C3")
  need(str(native)==original["native_chain_path"],"ORIGINAL_NATIVE_MODEL0_CHAIN_PATH_CHANGED")
  # load_run verifies all manifest references; retain exact numeric receipts for independent closure.
  refs=list(common.file_references({"inputs":m.get("inputs"),"outputs":m.get("outputs"),"file_inventory":m.get("file_inventory"),"runtime":m.get("runtime")}))
  closure=[]
  for rr in refs:
   actual=pin(rr["path"],rr["sha256"],rr.get("bytes"));closure.append({"declared":rr,"actual":actual})
  old_receipt=dump(out/"old11801_load_run_design_pose_repeat.json",{"status":"EXACT_OLD_PREDICTED_INPUT_AND_NATIVE_MODEL0_CHAIN_CONTENT_REPEATED","prediction_manifest":frozen_inputs[PRED],"config":config,"pose":pose,"native_chain":rec(native),"load_run_reference_closure":closure,"source_tree_sha256":BASE,"generic_source":sourcefiles,"source_import_paths":{"common":str(Path(common.__file__).resolve()),"pipeline":str(Path(pipeline.__file__).resolve())},"not_new_physical_qualification":True})
  phase="all_three_actual_runtime_matches_reviewed_override_old_default_locks_preserved";runtime=[]
  for c in ("core","rfd","boltz"):
   expected=read(overrides[c]["frozen"]["path"]);actual=common.collect_runtime(R,c);exact_runtime(actual,expected,c)
   current=pin(locks[c]["original"]["path"],locks[c]["original"]["sha256"],locks[c]["original"]["bytes"])
   ap=dump(out/("runtime_actual_"+c+".json"),actual)
   runtime.append({"component":c,"historical_lock_anchor":historical_locks[c],"original_lock":current,"historical_frozen_lock":locks[c]["frozen"],"reviewed_override":overrides[c]["frozen"],"actual":ap,"full_JSON_equal":True})
  need(source_tree(R/"source")[0]==BASE,"DEFAULT_SOURCE_CHANGED_DURING_BARRIER")
  final_runtime=dump(out/"runtime3_independent_repeat.json",{"status":"ALL3_ACTUAL_RUNTIME_JSON_EQUAL_EXPLICIT_REVIEWED_OVERRIDES_DEFAULT_LOCKS_UNCHANGED","components":runtime,"no_runtime_lock_refresh":True})
  historical_vendor=historical225_recompute(common,delta["old_fingerprint"])
  vendorproof=dump(out/"historical225_vendor_content_repeat.json",historical_vendor)
  override_acceptance=dump(out/"runtime_override_acceptance.json",{"schema":"reviewed-runtime-override-acceptance.v1","status":OVERRIDE_STATUS,"slurm_job_id":jid,"allocation":allocation,"runtime_override_directory":str(frozen/"runtime_override"),"runtime_locks":{c:overrides[c]["frozen"]for c in overrides},"original_default_locks":{c:locks[c]["original"]for c in locks},"historical_runtime_lock_anchors":historical_locks,"materialization_acceptance":mat_receipt,"materialization_copy":matf,"diagnostics":[diagf,cachef],"runtime_prerequisites":runtime_prerequisites,"actual_runtime3":final_runtime,"historical225_vendor_content_repeat":vendorproof,"materialization_five_arrays_independent_repeat":arrayproof,"materialization_source_lineage":materialization_source,"full_cache_delta":delta,"new_RFD_lock_includes_exact_cache":CACHE,"default_source_C3_unchanged":True,"default_runtime_locks_unchanged":True,"cache_excluded_from_new_lock":False,"no_auto_refresh":True,"source_files":[x["frozen"]for x in runner],"contracts":contracts})
  phase="terminal_content_acceptance"
  acceptance={"schema":"generic-report-materialized-runtime-repair-acceptance.v2","status":STATUS,"slurm_job_id":jid,"original_job_id":ORIGINAL,"allocation":allocation,"original_terminal_CPU_accounting":original_allocation,"original_scheduler_batch":rec(frozen/"barrier_source/original13263.batch"),"original_scheduler_source_authority":scheduler_authority,"original_embedded_python":dump(out/"original_embedded_python_identity.json",{"source":embedded}),"original_stdout":logf,"original_stderr":errf,"contracts":contracts,"source_files":[x["frozen"]for x in runner],"frozen_input_manifest":rec(out/"frozen_input_manifest.json"),"all13_exact_receipts_repeated":True,"required_report_content_repeated":True,"strict_original_report_identity_required":True,"native14_numeric_content_repeated":True,"old11801_load_run_design_pose_content_repeated":True,"original_generic_python_source_sha256":BASE,"full_generic_source_C3_repeated":True,"all3_original_default_lock_bytes_repeated":True,"all3_actual_runtimes_equal_reviewed_overrides":True,"reviewed_runtime_override_acceptance":override_acceptance,"materialization_acceptance":mat_receipt,"runtime_prerequisites":runtime_prerequisites,"original13263_failure_preserved":True,"all3_historical_lock_anchors_matched":True,"historical_runtime_lock_anchors":historical_locks,"native14_repeat":native_receipt,"old11801_repeat":old_receipt,"runtime3_repeat":final_runtime,"report":reportf,"original_failed_partial_stdout_history":original,"repair_request":rec(request_path),"no_GPU_calls":True,"default_source_changed":False,"formal13260_changed":False,"no_runtime_lock_refresh":True,"source_staged":False,"published":False,"ACTIVE_changed":False}
  dump(out/"acceptance.json",acceptance);print(STATUS,flush=True)
 except Exception as e:
  dump(out/"typed_incomplete.json",{"status":"GENERIC_REPORT_MATERIALIZED_RUNTIME_REPAIR_TYPED_INCOMPLETE_ORIGINAL_FAILURE_PRESERVED","slurm_job_id":os.environ.get("SLURM_JOB_ID"),"failed_stage":phase,"reason_type":type(e).__name__,"reason":str(e),"allocation":allocation,"default_source_changed":False,"published":False,"ACTIVE_changed":False,"requires_root_review":True});raise
CONTRACT_COUNT=94
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--out",required=True);ap.add_argument("--request",required=True);a=ap.parse_args();run(a.out,a.request)
if __name__=="__main__":main()
