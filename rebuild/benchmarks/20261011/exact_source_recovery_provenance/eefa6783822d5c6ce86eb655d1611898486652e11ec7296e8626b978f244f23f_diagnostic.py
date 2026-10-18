#!/usr/bin/env python3
"""DIAGNOSTIC_ONLY finite saved-source exact-byte search; no alias/acceptance."""
import ast,hashlib,json,os,subprocess,sys
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");STEP=R/"steps/24_benchmark_delivery"
BASE=STEP/"frozen/source_refresh_relative_v9_13307/code"
INPUT={"path":str(STEP/"runs/source_missing_operative_inventory_13308/diagnostic.json"),"bytes":207548,"sha256":"2a22a7f4aa4a787f934b72a1fe7ec4bf84c1891c08944120093519d4b469ba11"}
REGISTRY={"path":str(R/"steps/22_matched_benchmark/code/formal_contract_v2/manifest.json"),"bytes":11279,"sha256":"43cd4a6e3c0cc91890e06401bf65db1a6f5969ab1d6d8e3d10da4514d6714e47"}
ROOTS=tuple(R/x for x in (
 "steps/21_method_runtime/code","steps/21_method_runtime/frozen","steps/21_method_runtime/sources","steps/21_method_runtime/engineering_history","steps/21_method_runtime/source_snapshots",
 "steps/22_matched_benchmark/code","steps/22_matched_benchmark/settings","steps/22_matched_benchmark/source","steps/22_matched_benchmark/sources","steps/22_matched_benchmark/frozen",
 "steps/23_common_review/code","steps/23_common_review/frozen","steps/23_common_review/bbf_diagnostics/code","steps/23_common_review/bbf_diagnostics/frozen",
 "steps/23_common_review/bbf_diagnostics/scientific_review/code","steps/23_common_review/bbf_diagnostics/scientific_review/runs/review_sourcepack_13237/resources"))
METADATA=tuple(R/x for x in ("steps/23_common_review/frozen/native_common_13022/source_bundle.json","steps/23_common_review/frozen/native_common_13023/source_bundle.json"))
def need(v,message):
 if not v:raise ValueError(message)
def safe(p):
 p=Path(p)
 need(p.is_absolute()and p.is_relative_to(R)and p.resolve()==p and not p.is_symlink(),"Exact internal nonsymlink path required")
 need("/steps/22_matched_benchmark/formal_runs/"not in str(p)and "/steps/25_reference_free_e2e/runs/"not in str(p),"Current scientific output reads forbidden")
 return p
sys.path.insert(0,str(BASE))
from delivery_core import cpu,rec
need(os.environ.get("SLURM_CPUS_PER_TASK")=="1"and os.environ.get("CUDA_VISIBLE_DEVICES")=="","PureCPU1 invocation required")
allocation=cpu() # before hash, source/Git/archive/metadata content read
def exact(r,readonly=True):
 p=safe(r["path"]);need(p.is_file()and (not readonly or not(p.stat().st_mode&0o222)),"Required readonly source diagnostic input")
 need(rec(p)=={k:r[k]for k in ("path","bytes","sha256")},"Exact diagnostic input bytes differ")
 return p
def read_exact(r,readonly=True):
 p=exact(r,readonly);a=json.loads(p.read_text());exact(r,readonly);return a
executed_source_files=[]
for source_path in (Path(__file__).resolve(),Path(__file__).resolve().parent/"diagnostic.sbatch",BASE/"delivery_core.py"):
 safe(source_path);need(source_path.is_file()and not(source_path.stat().st_mode&0o222),"Executing diagnostic/dependency sources must be readonly")
 executed_source_files.append(rec(source_path))
incoming=read_exact(INPUT)
need(incoming.get("status")=="FINITE_ACCESSIBLE_MISSING_OPERATIVE_TEXT_EDGES_DIAGNOSED_NO_SOURCE_ACCEPTANCE_NO_AUTHORIZATION"and incoming.get("failed_source_job")=="13307"and incoming.get("job_id")=="13308"and incoming.get("missing_identity_count")==8 and incoming.get("source_acceptance")is False and incoming.get("new_alias_or_history_permission_created")is False,"Actual eight-identity diagnostic required")
def historical_terminal(job_id,jobname):
 raw=subprocess.check_output(["sacct","-X","-j",job_id,"--noheader","--parsable2","--format=JobIDRaw,User%64,Account%64,Partition%64,JobName%100,State%40,ExitCode,AllocCPUS,AllocTRES%300"],text=True)
 rows=[x.split("|")for x in raw.splitlines()if x.strip()]
 rows=[x for x in rows if x[0]==job_id]
 need(len(rows)==1,"Exact historical CPU terminal row required")
 row=rows[0]
 need(row[1:7]==["u21111210118","u21111210118","organ",jobname,"COMPLETED","0:0"]and row[7]=="1","Historical diagnostic terminal owner/job/partition/state/CPU differs")
 parsed={}
 for token in row[8].split(","):
  if "="not in token:continue
  key,value=token.split("=",1);need(key not in parsed,"Duplicate historical TRES field");parsed[key]=value
 need(parsed.get("cpu")=="1"and all(int(v)==0 for k,v in parsed.items()if k.startswith("gres/gpu")),"Historical diagnostic must have CPU1/GPU0")
 return dict(job_id=job_id,job_name=jobname,raw_sacct=raw,actual_completed_exit_zero=True,allocated_cpus=1,allocated_gpus=0)
history=historical_terminal("13308","test9_missing_source_diagnostic_v1")
need(incoming.get("actual_allocation",{}).get("job_id")=="13308"and incoming.get("actual_allocation",{}).get("allocated_gpus")==0,"Historical input allocation differs")
targets={}
for e in incoming["edges"]:
 r=e["operative_receipt_after_declared_context_normalization"];need(Path(r["path"]).suffix==".py","This finite source recovery only searches declared Python source")
 targets[(r["path"],r["bytes"],r["sha256"])]=r
need(len(targets)==8,"Exact eight unique source targets required")
names={Path(r["path"]).name for r in targets.values()};sizes={r["bytes"]for r in targets.values()};prefixed={r["sha256"]+"_"+Path(r["path"]).name for r in targets.values()}
registry=read_exact(REGISTRY)
need(registry.get("status")=="INDEPENDENT_FORMAL_V2_ALL_NATIVE_OUTPUTS_AND112_FAIRNESS_READONLY_SOURCE_SNAPSHOT_PASS","Original accepted formal registry status differs")
alias_rows=registry.get("historical_exact_byte_aliases",[]);need(len(alias_rows)==5,"Literal five formal history rows required")
explicit=[];parents=[]
for i,row in enumerate(alias_rows):
 logical=row["logical_receipt"];physical=row["resolved_readonly_exact_byte_receipt"];report=row["historical_report"]
 need(row.get("original_mutable_path_hash_claimed_equal")is False and (logical["bytes"],logical["sha256"])==(physical["bytes"],physical["sha256"]),"Existing alias identity/history differs")
 exact(physical);exact(report)
 explicit.append(dict(registry=REGISTRY,field=["historical_exact_byte_aliases",str(i)],logical_receipt=logical,physical_receipt=physical,historical_report=report,original_mutable_path_hash_claimed_equal=False,actual_physical_bytes_verified=True,new_alias_accepted=False))
parents.append(REGISTRY)
candidates={Path(x["physical_receipt"]["path"])for x in explicit}
metadata_records=[]
def receipts(obj,trail=()):
 if isinstance(obj,dict):
  if {"path","bytes","sha256"}<=obj.keys()and isinstance(obj["path"],str):yield obj,trail
  for k,v in obj.items():yield from receipts(v,trail+(str(k),))
 elif isinstance(obj,list):
  for i,v in enumerate(obj):yield from receipts(v,trail+(str(i),))
for p in METADATA:
 safe(p)
 if not p.is_file():metadata_records.append(dict(path=str(p),present=False));continue
 before=rec(p);need(not(p.stat().st_mode&0o222),"Named source metadata must remain readonly")
 obj=json.loads(p.read_text());need(rec(p)==before,"Named source bundle changed during read")
 metadata_records.append(dict(receipt=before,present=True,source_receipt_pointers=[dict(field=list(t),receipt=r)for r,t in receipts(obj)if Path(r["path"]).suffix==".py"]))
 for r,t in receipts(obj):
  if Path(r["path"]).suffix==".py"and any((r["bytes"],r["sha256"])==(x["bytes"],x["sha256"])for x in targets.values()):
   candidate=safe(r["path"])
   if candidate.is_file():candidates.add(candidate)
source_scope=[]
for root in ROOTS:
 safe(root);present=root.is_dir()
 source_scope.append(dict(root=str(root),present=present,selectors=["Exact missing basename","SHA256_missing-basename","Exact target byte count Python file within explicit source-only roots"],role="DIAGNOSTIC_CONTENT_SEARCH_NOT_RESOLVER_PERMISSION"))
 if not present:continue
 for current,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=[d for d in dirs if d not in (".git","__pycache__","env","models","outputs","site-packages")and not(Path(current)/d).is_symlink()]
  for name in files:
   p=Path(current)/name
   if p.suffix==".py"and not p.is_symlink()and (name in names or name in prefixed or p.stat().st_size in sizes):candidates.add(p)
results=[]
for p in sorted(candidates):
 p=safe(p);need(p.is_file(),"Explicit candidate missing")
 before=rec(p);after=rec(p);need(before==after,"Source candidate drift during actual CPU proof")
 matches=[r for r in targets.values()if (r["bytes"],r["sha256"])==(before["bytes"],before["sha256"])]
 results.append(dict(physical_content_receipt=before,matches_missing_receipts=matches,readonly=not bool(p.stat().st_mode&0o222),byte_identical_to_declared_missing=bool(matches),source_acceptance=False,new_alias_accepted=False,current_execution_authorized=False))
for r in parents:exact(r)
exact(INPUT)
for row in explicit:exact(row["physical_receipt"]);exact(row["historical_report"])
for row in metadata_records:
 if row.get("present"):exact(row["receipt"])
# Separately authorized deterministic SOURCE transformation; never execute freezer.
def reconstruct_recorded_common(out):
 bundle_path=R/"steps/23_common_review/frozen/native_common_13022/source_bundle.json"
 bundle_record=next((x["receipt"]for x in metadata_records if x.get("present")and x["receipt"]["path"]==str(bundle_path)),None)
 need(bundle_record is not None,"Recorded native13022 bundle unavailable")
 bundle=read_exact(bundle_record)
 need(bundle.get("status")=="IMMUTABLE_COMMON_REVIEW_SOURCE_BUNDLE"and bundle.get("freeze_job")=="13022","Exact historical source-bundle scope differs")
 original={"path":str(R/"source/rebuild/benchmark_common_review.py"),"bytes":50747,"sha256":"3f0da7ebbaa0db916c9a39781e83c61ee7b0a136687b4242c5253649abd14740"}
 frozen={"path":str(R/"steps/23_common_review/frozen/native_common_13022/code/benchmark_common_review.py"),"bytes":50999,"sha256":"78fbf3a5dc7c2b7ca1729ad7d2a94fffd6ca0110c4ab203becddd2a737ceeae4"}
 need(bundle["files"][0]==dict(original=original,frozen=frozen)and bundle["source"]==frozen,"Full old/frozen historical tuple differs")
 need((original["path"],original["bytes"],original["sha256"])in targets,"Original common source must be a diagnosed exact missing identity")
 freezer=safe(R/"steps/23_common_review/code/freeze_native_review.py")
 need(freezer.is_file()and not(freezer.stat().st_mode&0o222)and freezer.stat().st_size==6790,"Exact named historical freezer readonly6790 bytes required")
 freezer_record=rec(freezer);freezer_text=freezer.read_text();need(rec(freezer)==freezer_record,"Recorded freezer source changed")
 expected=[
 ('STEP=ROOT/"steps/23_common_review"','STEP=ROOT/"steps/23_common_review"\nFROZEN_DIR=Path(__file__).resolve().parent'),
 ('sys.path.insert(0,str(ROOT/"source/src"))','sys.path.insert(0,str(FROZEN_DIR/"src"))'),
 ('ROOT/"source/rebuild/screening_transfer.py"','FROZEN_DIR/"screening_transfer.py"'),
 ('ROOT/"source/rebuild/control_msa_check.py"','FROZEN_DIR/"control_msa_check.py"'),
 ('ROOT/"source/src/ppiblocker/structure.py"','FROZEN_DIR/"src/ppiblocker/structure.py"'),
 ('ROOT/"steps/03_af2_restore/inference_env.sh"','FROZEN_DIR/"runtime_entries/af2_inference_env.sh"'),
 ('ROOT/"env/colabfold/bin/colabfold_batch"','FROZEN_DIR/"runtime_entries/colabfold_batch"'),
 ('ROOT/"env/boltz/bin/boltz"','FROZEN_DIR/"runtime_entries/boltz"'),
 ('ROOT/"vendor"/("IPSAE_"+REVISION[:12])/"ipsae.py"','FROZEN_DIR/"vendor/ipsae.py"'),
 ('str(ROOT/"source/rebuild"),job["input"]["path"]','str(FROZEN_DIR),job["input"]["path"]'),
 ('method_origin_present=False)','method_origin_present=False,frozen_source_bundle=rec(FROZEN_DIR.parent/"source_bundle.json"))'),
 ('allocation=allocated,runs=runs)','allocation=allocated,runs=runs,source=plan["source"],frozen_source_bundle=plan["frozen_source_bundle"],runtime_locks=plan["runtime_locks"],receipt_policy="CPU_PRECOMPUTED_SOURCE_AND_DEPENDENCY_HASH_REFERENCES_NO_GPU_HASH_TASK")')]
 module=ast.parse(freezer_text)
 assignments=[]
 for node in module.body:
  if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id=="s"and isinstance(node.value,ast.Call)and isinstance(node.value.func,ast.Attribute)and isinstance(node.value.func.value,ast.Name)and node.value.func.value.id=="s"and node.value.func.attr=="replace":
   need(len(node.value.args)==2 and not node.value.keywords,"Recorded replace shape differs")
   pair=tuple(ast.literal_eval(x)for x in node.value.args);need(all(type(x)is str for x in pair),"Only literal string transformation permitted")
   assignments.append((node.lineno,pair))
 need([x[1]for x in assignments]==expected and len(assignments)==12,"Exact twelve recorded replacement tuples differ")
 need(len({b for a,b in expected})==12 and all(a and b and a!=b for a,b in expected),"Ambiguous replacement policy")
 # No import or execution of the historical freezer or reconstructed source.
 frozen_path=exact(frozen);frozen_bytes=frozen_path.read_bytes();exact(frozen)
 value=frozen_bytes.decode("utf-8");reverse_log=[]
 for index in reversed(range(len(expected))):
  a,b=expected[index];n=value.count(b);need(n>0,"Missing recorded reverse anchor")
  reverse_log.append(dict(recorded_index=index,source_line=assignments[index][0],replacements=n))
  value=value.replace(b,a)
 raw=value.encode("utf-8");need(len(raw)==original["bytes"]and hashlib.sha256(raw).hexdigest()==original["sha256"],"Reconstructed historical source exact bytes/SHA differ")
 replay=value;forward_log=[]
 for index,(a,b)in enumerate(expected):
  n=replay.count(a);need(n>0,"Missing recorded forward anchor")
  forward_log.append(dict(recorded_index=index,source_line=assignments[index][0],replacements=n))
  replay=replay.replace(a,b)
 need(replay.encode("utf-8")==frozen_bytes,"Recorded transformation forward replay differs from frozen exact bytes")
 destination=out/"reconstructed_historical_source"/(original["sha256"]+"_benchmark_common_review.py")
 destination.parent.mkdir(exist_ok=False);destination.write_bytes(raw);destination.chmod(0o444)
 reconstructed=rec(destination);need((reconstructed["bytes"],reconstructed["sha256"])==(original["bytes"],original["sha256"]),"Saved reconstructed source readback differs")
 exact(bundle_record);exact(frozen);need(rec(freezer)==freezer_record,"Historical transformation source changed at end")
 return dict(status="RECONSTRUCTED_EXACT_HISTORICAL_SOURCE_FROM_RECORDED_FREEZER_REVERSE_AND_FORWARD_REPLAY_NOT_CURRENT_EXECUTION",classification="RECONSTRUCTED_HISTORICAL_SOURCE_NOT_FOUND_ORIGINAL",original_logical_receipt=original,historical_bundle=bundle_record,source_field=["files","0"],recorded_freezer=freezer_record,frozen_source=frozen,reconstructed_source=reconstructed,exact_twelve_replacements=expected,reverse_log=reverse_log,forward_log=forward_log,old_source_size_and_SHA_verified=True,forward_replay_byte_identical=True,historical_freezer_executed=False,reconstructed_source_executed=False,current_execution_authorized=False,new_alias_accepted=False,source_acceptance=False)

out=STEP/"runs"/("source_saved_byte_recovery_diagnostic_"+os.environ["SLURM_JOB_ID"]);out.mkdir(parents=True,exist_ok=False)
resolved={k for k,r in targets.items()if any(r in x["matches_missing_receipts"]for x in results)}
reconstruction=reconstruct_recorded_common(out)
reconstruction_identity=tuple(reconstruction["original_logical_receipt"][k]for k in ("path","bytes","sha256"))
exact(INPUT);exact(REGISTRY)
for row in explicit:exact(row["physical_receipt"]);exact(row["historical_report"])
for row in metadata_records:
 if row.get("present"):exact(row["receipt"])
for row in executed_source_files:exact(row)
report=dict(schema="saved-source-exact-byte-recovery-diagnostic-only.v1",status="FINITE_EIGHT_SOURCE_IDENTITIES_SEARCHED_NO_SOURCE_OR_ALIAS_ACCEPTANCE",job_id=os.environ["SLURM_JOB_ID"],actual_allocation=allocation,executed_source_files=executed_source_files,input_missing_inventory=INPUT,historical_diagnostic_terminal=history,original_five_alias_registry=REGISTRY,existing_five_declared_aliases=explicit,source_bundle_metadata=metadata_records,finite_source_roots=source_scope,source_candidates=results,targets=list(targets.values()),matched_identity_count=len(resolved),reconstructed_historical_identity_count=1,recorded_common_reconstruction=reconstruction,unmatched_targets_after_found_original_and_reconstructed=[r for k,r in targets.items()if k not in resolved and k!=reconstruction_identity],unmatched_targets=[r for k,r in targets.items()if k not in resolved],source_acceptance=False,new_alias_accepted=False,source_staged=False,default_changed=False,current_execution_authorized=False,model_inference=False,formal_outputs_read=False,E2E_outputs_read=False,scientific_payload_read=False,upstream_vendor_tar_payloads_read=False,source_reconstruction_performed=True,deterministic_recorded_patch_reconstruction_separate_proof=True,scope="Exact content matches only under pureCPU. Existing literal alias registry and byte-preserving candidate lineage remain distinct; any operative alias needs a separately reviewed exact parent/field/provenance source successor.")
dest=out/"diagnostic.json";dest.write_text(json.dumps(report,indent=2)+"\n");dest.chmod(0o444)
print(json.dumps(dict(status=report["status"],diagnostic=rec(dest),matched_identities=len(resolved),unmatched_targets=report["unmatched_targets"],source_acceptance=False)))
