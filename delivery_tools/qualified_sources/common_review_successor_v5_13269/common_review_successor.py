#!/usr/bin/env python3
"""Plan-bound common review successor. CPU orchestration; root submits GPU jobs."""
import argparse,datetime,hashlib,importlib.util,json,os,re,shutil,subprocess,sys
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
SELF=Path(__file__).resolve()
D=SELF.parent
LIB=R/"steps/24_benchmark_delivery/frozen/history_policy_13223/code"
CORE=R/"env/core/bin/python"
def pin(rel,n,h):return dict(path=str(R/rel),bytes=n,sha256=h)
PINS={
"common":pin("steps/23_common_review/frozen/common_core_v2_13130/code/benchmark_common_review_v2.py",62153,"7d72314e0409fa1fb2a6ed86f593b198cf3e5c99f747c58d8cfa7d1fd0404d17"),
"bundle":pin("steps/23_common_review/frozen/common_core_v2_13130/source_bundle.json",12276,"7743873fb5ec089c1edb14670823dc76c6f614dae9dec4baba19ca805cc7b804"),
"plan":pin("steps/22_matched_benchmark/formal_freeze_13257/plan/frozen_plan.json",20295,"e913d1bbccd531bf88a73f6ba60e8a0de85bb03ad8bcd3455d8952ca4effe0b6"),
"formal":pin("steps/22_matched_benchmark/code/formal_contract_v2/source/formal_benchmark_contract.py",46984,"768c0ca8fbdf942638688ed6a12ea1e88a42b50d7c219b902bbc3d945ddeb4bc"),
"guard":pin("steps/22_matched_benchmark/settings/pilot_budget_v4/source/paired_budget_benchmark.py",84446,"b37227bd862ee1425a59f5308be1ee3f4824042dea5d71c1269ad0f406b318f9"),
"independent":pin("steps/24_benchmark_delivery/frozen/history_policy_13223/code/common_review_independent_v2.py",18822,"e42fc17a996e0fddf5c9d9f0cda6fbee4487ae0577f69b4c1ed3c17ee1a96919"),
"statistics":pin("steps/24_benchmark_delivery/frozen/history_policy_13223/code/target_statistics_v2.py",8723,"cdad0d2dfb2005c2704178a641c48b40a5268b464cab9587d72ddcdc89f4bf73"),
"resolver":pin("steps/24_benchmark_delivery/frozen/history_policy_13223/code/restore_resolver_v2.py",4979,"1618974ee343570adf82ad70ac56a0fcfe0a1eac8274476e81ef05691190689c"),
"aliases":pin("steps/24_benchmark_delivery/frozen/history_policy_13223/code/provenance_aliases_v2.py",5048,"1de9f0ba13cf8774f6de0fbe4410fd41b8dacf5e9e6d5f1f969b9842f1d8bd01"),
"native":pin("steps/24_benchmark_delivery/runs/native74_final_v2_13211/native74/acceptance.json",9602,"9effb60abceb03ca8c47b8e786f6613486bec96c90dec6aec517a1bd415fcff9")}
ACTIVE_STATES={"PENDING","RUNNING","CONFIGURING","COMPLETING","SUSPENDED","RESIZING","REQUEUED","REQUEUE_FED"}
FILES=("common_review_successor.py","test_common_review_successor.py","successor_bootstrap.py","common_review_cpu.sbatch","common_review_gpu.sbatch","intrinsic_clearance.py","HANDOFF.md")
def need(v,msg):
 if not v:raise ValueError(msg)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text())
def project(p):
 p=Path(p);need(p.is_absolute() and p.resolve().is_relative_to(R) and not p.is_symlink(),"Path outside project or symbolic")
 return p
def rec(p):
 p=project(p);h=hashlib.sha256()
 with p.open("rb")as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return dict(path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest())
def verify(r,readonly=False):
 p=project(r["path"]);need(p.is_file()and rec(p)==r,"Exact receipt differs: "+str(p))
 need(not readonly or not(p.stat().st_mode&0o222),"Readonly source required: "+str(p));return p
def receipt_arg(path,sha):
 r=rec(path);need(r["sha256"]==sha,"Exact CLI receipt differs");return r
def dump(p,obj):
 p=project(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("x")as f:json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
 p.chmod(0o444);return rec(p)
def load(name,r):
 p=verify(r,True);sys.path.insert(0,str(p.parent));spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def frozen():
 need(D.is_relative_to(R/"steps/24_benchmark_delivery/frozen"),"Execute actual sealed successor snapshot only")
 need(not(D.stat().st_mode&0o222),"Readonly source directory required")
 return [rec(verify(rec(D/n),True))for n in FILES]
def sources():
 own=frozen()
 for r in PINS.values():verify(r, r is not PINS["native"] and r is not PINS["plan"])
 bundle=read(PINS["bundle"]["path"]);need(bundle["source"]==PINS["common"],"Core bundle source differs")
 for pair in bundle["files"]:verify(pair["frozen"],True)
 return dict(successor=own,operative=PINS,common_bundle=PINS["bundle"])
def cpu():
 need(os.environ.get("CUDA_VISIBLE_DEVICES")==""and os.environ.get("JAX_PLATFORMS")=="cpu","Pure CPU CUDA/JAX mask required")
 need(os.environ.get("PYTHONNOUSERSITE")=="1"and os.environ.get("PYTHONDONTWRITEBYTECODE")=="1","CPU import isolation required")
 need("PYTHONPATH"not in os.environ and os.environ.get("OPENBLAS_NUM_THREADS")=="1","Injected path/CPU thread mismatch")
 common=load("successor_cpu_common",PINS["common"]);return common.allocation(0)
def by(rows,key):
 result={}
 for row in rows:
  k=key(row);need(k not in result,"Duplicate fixed key");result[k]=row
 return result
def expected_sensitivity(plan,analysis,membership):
 entities=by(plan["entities"],lambda x:x["blind_id"]);targets=by(analysis["targets"],lambda x:x["target_id"])
 controls=membership["controls"];need(len(controls)==7 and len({c["target_id"]for c in controls})==7,"Exact seven native controls required")
 sensitive={x["blind_id"]for x in controls};groups={}
 for m in membership["members"]:
  need(m["blind_id"]in entities,"Membership blind entity absent")
  if m["cohort"]=="uniform_all_complete":groups.setdefault(m["task_id"],[]).append(m)
 for rows in groups.values():sensitive.add(min(rows,key=lambda v:(v["sampling_key"],v["sequence_sha256"]))["blind_id"])
 expected={}
 for bid,e in entities.items():
  for engine in ("boltz","af2"):expected[(bid,engine,"primary")]=3 if engine=="boltz"else 5
  if bid in sensitive and not targets[e["target_id"]]["synthetic"]:expected[(bid,"boltz","single_sensitivity")]=3
 jobs=by(plan["jobs"],lambda x:(x["blind_id"],x["engine"],x["variant"]))
 need(set(jobs)==set(expected),"Complete primary plus prescribed single-MSA sensitivity set differs")
 for key,n in expected.items():
  j=jobs[key];slots=[dict(seed=s,model=0)for s in(31011,31012,31013)]if j["engine"]=="boltz"else[dict(seed=31021,model=i)for i in(1,2,3,4,5)]
  need(j["expected_models"]==n and j["slots"]==slots,"Fixed common model/seed slots differ")
 nativejobs=[j for j in plan["jobs"]if j["blind_id"]in {c["blind_id"]for c in controls}]
 need(len(nativejobs)==20 and sum(j["expected_models"]for j in nativejobs)==74,"Native20/74 fixed denominator differs")
 return dict(n_jobs=len(jobs),n_models=sum(expected.values()),n_sensitivity_jobs=sum(k[2]=="single_sensitivity"for k in expected),sensitive_blind_ids=sorted(sensitive),coverage="all native controls plus minimum uniform hash per nonempty arm; synthetic single primary")
def validate_inputs(preparation):
 prepared=read(verify(preparation));need(prepared["status"]=="FORMAL_BLIND_COMMON_REVIEW_PREPARED_NOT_INFERRED"and prepared["plan"]==PINS["plan"]and prepared["source"]==PINS["common"],"Future preparation/source/formal-plan not accepted")
 for rr in prepared["outputs"].values():verify(rr)
 collection=read(verify(prepared["collection"]));need(collection["schema"]=="formal_postprocess_collection.v2"and collection["status"]=="FORMAL_ALLOCATION_NATIVE_AND_COHORT_CLOSURE_ACCEPTED"and collection["plan"]==PINS["plan"],"Formal collection unqualified")
 for rr in collection["files"].values():verify(rr)
 plan=read(verify(prepared["outputs"]["inference_plan"]));analysis=read(verify(prepared["outputs"]["analysis_plan"]));membership=read(verify(prepared["outputs"]["membership"]))
 need(plan["source"]==PINS["common"]and plan["frozen_source_bundle"]==PINS["bundle"]and plan["method_origin_present"]is False,"Common source/blinding differs")
 common=load("successor_preflight_common",PINS["common"]);need(plan["settings"]==common.SETTINGS,"Frozen science settings differ")
 for key in("registry","msa","generation_gate_protocol"):verify(plan[key])
 for rr in plan["runtime_locks"].values():verify(rr)
 for rr in plan["af2_parameter_receipts"]:verify(rr)
 for j in plan["jobs"]:
  verify(j["input"])
  if j.get("target_msa"):verify(j["target_msa"])
 need(analysis["inference_plan"]==membership["inference_plan"]==prepared["outputs"]["inference_plan"],"Analysis/membership source differs")
 need(membership["coverage"]==read(verify(collection["files"]["cohorts"]))["coverage"],"Generation fixed coverage lost")
 scope=expected_sensitivity(plan,analysis,membership)
 dispatch=read(verify(prepared["outputs"]["root_dispatch"]));need(dispatch["global_project_gpu_concurrency_cap"]==2 and dispatch["job_count"]==len(plan["jobs"]),"Root dispatch/cap differs")
 for i,j in enumerate(plan["jobs"]):
  r=dispatch["jobs"][i];need(r["index"]==i and r["job_key"]==j["job_key"]and r["signature"]==common.job_signature(j),"Dispatch fixed identity differs")
 return prepared,collection,plan,analysis,membership,scope
def safe_relative(name):
 p=Path(name);need(not p.is_absolute()and ".."not in p.parts and name and name!=".","Unsafe cache relative file");return p
def copy_worker(source,dest):
 source=project(source);dest=project(dest);need(source.is_dir()and not dest.exists(),"Cache source missing or destination collision")
 dest.mkdir(parents=True);mapping=[]
 for p in sorted(source.rglob("*")):
  need(not p.is_symlink(),"Symbolic cache contents forbidden")
  if not p.is_file():continue
  rel=safe_relative(str(p.relative_to(source)));rr=rec(p);target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(verify(rr),target)
  need(rec(target)["sha256"]==rr["sha256"]and rec(target)["bytes"]==rr["bytes"],"Cache bytecopy mismatch");target.chmod(0o444)
  mapping.append(dict(original=rr,copy=rec(target)))
 need((dest/"worker.json").is_file(),"Copied cache worker absent")
 return mapping
def binding_rows(binding,plan):
 rows=binding["rows"];control={r["job_key"]:r for r in rows}
 need(len(control)==len(rows)==20,"Cache controls lost/duplicated")
 reusable={k for k,r in control.items()if r["status"]=="CACHE_RAW_BOUND_TO_CURRENT_FORMAL_JOB"}
 indexed={i:j for i,j in enumerate(plan["jobs"])}
 expected=[i for i,j in indexed.items()if j["job_key"]not in reusable]
 need(binding["root_pending_job_indices"]==expected,"Pending-only index list differs")
 for key in reusable:
  row=control[key];j=indexed[row["new_index"]];need(j==row["new_job"]and key==j["job_key"],"Cache bound job/index differs")
 need(binding["reusable_workers"]==len(reusable),"Reusable worker count differs")
 return control,reusable,expected
def preflight(args,out):
 guard=cpu();source=sources();software=receipt_arg(args.software_acceptance,args.software_acceptance_sha256);software_doc=read(verify(software))
 need(software_doc["status"]=="COMMON_SUCCESSOR_SOFTWARE_SOURCE_CPU_ACCEPTED_FUTURE_FORMAL_PREPARATION_PENDING"and software_doc["source"]==source,"Actual tested successor source acceptance required")
 test_doc=read(verify(software_doc["contracts"]));need(test_doc["status"]=="PASS"and test_doc["tests_run"]==58,"Software boundary contracts unaccepted")
 pr=receipt_arg(args.preparation,args.preparation_sha256);prepared,collection,plan,analysis,membership,scope=validate_inputs(pr)
 br=receipt_arg(args.binding,args.binding_sha256);accepted=read(verify(br));need(accepted["status"]=="CPU_CACHE_GUARD_BIND_COMPLETE"and accepted["formal_binding"]is True and accepted["no_inference"]is True,"Actual CPU cache-binding acceptance required")
 need(read(verify(accepted["contracts"]))["status"]=="PASS","Cache software contracts not accepted")
 cache_source=read(verify(accepted["source"]))
 for rr in cache_source["files"]:verify(rr,True)
 binding=read(verify(accepted["result"]));need(binding["status"]in{"CACHE_BINDING_CPU_COMPLETE_ALL20_REUSABLE","CACHE_BINDING_CPU_COMPLETE_WITH_TYPED_NONREUSABLE_JOBS"}and binding["preparation"]==pr and binding["inference_plan"]==prepared["outputs"]["inference_plan"],"Cache binding/preparation differs")
 need(binding["original_worker_bytes_unchanged"]and binding["current_scorer_must_rescore_raw"]and binding["no_scores_transferred"]and binding["new_inference_GPU_seconds"]==0,"Cache provenance/score/cost rule differs")
 control,reusable,pending=binding_rows(binding,plan)
 native_ids={r["blind_id"]for r in membership["controls"]};need(set(control)=={j["job_key"]for j in plan["jobs"]if j["blind_id"]in native_ids},"Cache20 must be exact native controls")
 # Newly prepared review plans and query inputs are sealed without changing bytes; prior formal/source/input artifacts are unchanged.
 for rr in prepared["outputs"].values():verify(rr).chmod(0o444)
 for j in plan["jobs"]:verify(j["input"]).chmod(0o444)
 raw=out/"raw";raw.mkdir();maps=[]
 for key in sorted(reusable):
  row=control[key];cache_worker=verify(row["copy"]["worker"])
  for rr in row["copy"]["files"]:verify(rr["copy"])
  expected={str(Path(rr["copy"]["path"]).relative_to(cache_worker.parent))for rr in row["copy"]["files"]}
  observed={str(p.relative_to(cache_worker.parent))for p in cache_worker.parent.rglob("*")if p.is_file()}
  need(observed==expected,"Cache directory has unbound or missing bytes")
  files=copy_worker(cache_worker.parent,raw/key)
  need(rec(raw/key/"worker.json")["sha256"]==row["old_worker"]["sha256"],"Old worker JSON provenance rewritten")
  maps.append(dict(job_key=key,new_index=row["new_index"],original_worker=row["original_worker"],old_worker=row["old_worker"],bound_cache_worker=row["copy"]["worker"],approved_worker=rec(raw/key/"worker.json"),files=files,original_GPU_allocation=row["original_GPU_allocation"],old_cost_recharged=False,source_identity_rewritten=False))
 (out/"dispatch_claims").mkdir()
 result=dict(schema="formal_common_successor_preflight.v1",status="COMMON_SUCCESSOR_CPU_PREFLIGHT_ACCEPTED_ROOT_PENDING_ONLY_GPU_SUBMISSION_REQUIRED",source=source,software_acceptance=software,allocation=guard,preparation=pr,binding_acceptance=br,binding=accepted["result"],collection=prepared["collection"],outputs=prepared["outputs"],scope=scope,approved_raw_root=str(raw),dispatch_claim_root=str(out/"dispatch_claims"),cached_workers=maps,root_pending_job_indices=pending,pending_jobs=[dict(index=i,job=plan["jobs"][i])for i in pending],expected_jobs=len(plan["jobs"]),expected_models=scope["n_models"],intrinsic_clearance_policy=dict(source=rec(D/"intrinsic_clearance.py"),policy=load("successor_intrinsic_preflight",rec(D/"intrinsic_clearance.py")).POLICY,policy_scope_frozen_before_production=True),GPU_resource_policy=dict(cpu=3,gpu=1,memory_MiB=65536,OMP_NUM_THREADS="4",hardware="NVIDIA A100-PCIE-40GB",global_project_gpu_concurrency_cap=2),root_submission_performed=False,no_inference=True,old_GPU_cost_not_recharged=True,created_utc=now())
 return dump(out/"preflight.json",result)
def gpu_resources(allocation):
 row=allocation["selected_scheduler_record"];fields=dict(re.findall(r"(\w+)=(\S+)",row))
 need(fields.get("JobState")=="RUNNING"and fields.get("NumCPUs")=="3","Unique actual RUNNING CPU3 allocation required")
 memory=fields.get("MinMemoryNode");need(memory in{"64G","65536M"},"Actual memory64G node policy required")
 need(os.environ.get("OMP_NUM_THREADS")=="4","Literal OMP4 shared policy required")
 owned=allocation["owned_gpu_guard"];need(owned["status"]=="RUNNING_SLURM_GPU_OWNERSHIP_VERIFIED"and len(owned["owned_gpu_uuids"])==1 and owned["child_cuda_visible_devices"]==os.environ.get("CUDA_VISIBLE_DEVICES"),"Owned physical UUID propagation differs")
 need(all(v["name"]=="NVIDIA A100-PCIE-40GB"and v["memory_total_mib"]==40960 for v in owned["hardware"]["gpus"]),"Exact A10040GB hardware required")
 return allocation
def gpu_plan(preflight,index):
 need(preflight["status"]=="COMMON_SUCCESSOR_CPU_PREFLIGHT_ACCEPTED_ROOT_PENDING_ONLY_GPU_SUBMISSION_REQUIRED","CPU preflight absent")
 need(index in preflight["root_pending_job_indices"],"Index already cache-bound or not frozen pending")
 need(str(SELF)==next(x["path"]for x in preflight["source"]["successor"]if Path(x["path"]).name==SELF.name),"GPU entry must be exact CPU-tested immutable source")
 plan=read(preflight["outputs"]["inference_plan"]["path"]);job=plan["jobs"][index]
 need(plan["source"]==PINS["common"]and plan["frozen_source_bundle"]==PINS["bundle"]and plan["method_origin_present"]is False,"GPU immutable plan source differs")
 expected=next(x["job"]for x in preflight["pending_jobs"]if x["index"]==index);need(job==expected,"GPU job differs from CPU-bound slot")
 return plan,job
def worker(args):
 # Source/content hashes are precomputed by pureCPU; GPU performs indispensable identity/ownership metadata only.
 pre=read(args.preflight);index=args.index;plan,job=gpu_plan(pre,index)
 claim=project(pre["dispatch_claim_root"])/str(index);claim.mkdir(exist_ok=False)
 need(os.environ.get("SLURM_ARRAY_TASK_ID")==str(index)and os.environ.get("SLURM_ARRAY_JOB_ID"),"Invoking array identity required")
 need(not(project(pre["approved_raw_root"])/job["job_key"]).exists(),"Existing raw slot cannot be overwritten")
 spec=importlib.util.spec_from_file_location("successor_gpu_core",PINS["common"]["path"]);m=importlib.util.module_from_spec(spec);sys.path.insert(0,str(Path(PINS["common"]["path"]).parent));spec.loader.exec_module(m)
 allocated=gpu_resources(m.allocation(1))
 start=dict(status="COMMON_REVIEW_GPU_SLOT_STARTED_AFTER_CPU_PREFLIGHT",job=job,index=index,preflight_path=args.preflight,successor_entry_path=str(SELF),source_receipts=pre["source"],actual_allocation=allocated,neural_worker_source=PINS["common"],created_utc=now())
 with(claim/"start.json").open("x")as f:json.dump(start,f,indent=2);f.write("\n")
 m.worker(pre["outputs"]["inference_plan"]["path"],index,pre["approved_raw_root"])
 with(claim/"complete.json").open("x")as f:json.dump(dict(status="COMMON_REVIEW_GPU_WORKER_RETURNED_PENDING_CPU_RAW_VALIDATION",job_key=job["job_key"]),f);f.write("\n")
def scheduler_rows(text,array_id,indices,resource_strict=True):
 rows=[]
 for line in text.splitlines():
  if not line.strip():continue
  cells=line.split("|");need(len(cells)==8,"Malformed actual review sacct row")
  jid,raw,state,elapsed,tres,start,end,node=cells
  if "."in jid or jid==array_id:continue
  match=re.fullmatch(re.escape(array_id)+r"_(\d+)",jid)
  if not match:continue
  idx=int(match[1]);need(idx in indices and re.fullmatch(r"\d+",raw),"Unknown actual common array slot")
  state=state.split()[0].rstrip("+");need(state not in ACTIVE_STATES,"Review allocation remains nonterminal")
  n=int(elapsed);need(n>=0,"Invalid GPU elapsed cost")
  entries=dict(x.split("=",1)for x in tres.split(",")if "="in x)
  gpu=int(entries["gres/gpu"])if"gres/gpu"in entries else sum(int(v)for k,v in entries.items()if k.startswith("gres/gpu:"))
  need(gpu>=0,"Negative actual GPU count")
  if resource_strict:
   need(gpu==1 or(n==0 and gpu==0),"Review actual GPU resource differs")
   if n>0:need(entries.get("cpu")=="3","Review actual CPU3 differs")
  rows.append(dict(index=idx,logical_id=jid,raw_allocation_id=raw,state=state,elapsed_seconds=n,actual_gpu_count=gpu,actual_GPU_seconds=n*gpu,actual_AllocTRES=tres,Start=start,End=end,NodeList=node))
 need({r["index"]for r in rows}==set(indices)and len(rows)==len(indices),"Actual review terminal allocations lost/duplicated")
 need(len({r["raw_allocation_id"]for r in rows})==len(rows),"Actual GPU cost raw allocation ID duplicated")
 return rows
def submission_contract(sub,pr,pre):
 need(sub["schema"]=="formal_common_root_submission.v1"and sub["preflight"]==pr,"Root submission receipt must bind exact CPU preflight")
 need(sub["indices"]==pre["root_pending_job_indices"]and sub["concurrency_cap"]==2,"Root array pending-only indices/cap differ")
 need(re.fullmatch(r"\d+",str(sub["array_job_id"]))is not None,"Root array numeric identity required")
 launcher=next(x for x in pre["source"]["successor"]if Path(x["path"]).name=="common_review_gpu.sbatch")
 need(sub["launcher"]==launcher and sub["entry"]==next(x for x in pre["source"]["successor"]if Path(x["path"]).name=="common_review_successor.py"),"Root source/launcher differs")
 required="--array="+",".join(str(i)for i in sub["indices"])+"%2"
 expected=["sbatch","--parsable","--export=ALL,COMMON_SUCCESSOR_ENTRY="+sub["entry"]["path"]]
 if sub.get("dependency")is not None:
  need(re.fullmatch(r"afterany:\d+(?:_\d+)?(?::\d+(?:_\d+)?)*",sub["dependency"])is not None,"Unsupported root dependency")
  expected.append("--dependency="+sub["dependency"])
 expected.extend([required,launcher["path"],pr["path"]])
 need(sub["submit_argv"]==expected,"Exact full root argv/entry/preflight/resources differs")
 return str(sub["array_job_id"]),launcher
def start_contract(start,index,preflight_receipt,preflight,job):
 need(start["index"]==index and start["job"]==job and start["preflight_path"]==preflight_receipt["path"],"External start index/job/preflight differs")
 need(start["successor_entry_path"]==str(SELF)and start["source_receipts"]==preflight["source"],"External start source/preflight provenance differs")
 need(start["neural_worker_source"]==PINS["common"],"External neural source differs")
def new_worker_check(w,job,plan,allocationrow,launcher,start,index,preflight_receipt,preflight):
 start_contract(start,index,preflight_receipt,preflight,job)
 need(w["source"]==PINS["common"]and w["frozen_source_bundle"]==PINS["bundle"]and w["runtime_locks"]==plan["runtime_locks"]and w["settings"]==plan["settings"],"New worker source/settings/runtime provenance differs")
 common=load("successor_finish_worker_common",PINS["common"]);need(common.job_signature(w["job"])==common.job_signature(job),"New worker exact job differs")
 allocated=w["allocation"];need(allocated["raw_allocation_identity"]["raw_allocation_id"]==allocationrow["raw_allocation_id"]and allocated["raw_allocation_identity"]["logical_allocation_key"]==allocationrow["logical_id"],"Worker actual terminal allocation join differs")
 owned=allocated["owned_gpu_guard"];need(len(owned["owned_gpu_uuids"])==1 and owned["child_cuda_visible_devices"]==owned["owned_gpu_uuids"][0],"Worker owned UUID guard lost")
 row=allocated["selected_scheduler_record"];fields=dict(re.findall(r"(\w+)=(\S+)",row))
 need(fields.get("JobState")=="RUNNING"and fields.get("NumCPUs")=="3"and fields.get("MinMemoryNode")in{"64G","65536M"}and fields.get("Command")==launcher["path"],"Worker actual RUNNING resource/Command differs")
 common.gpu_guard_module().validate_scheduler_gpu_allocation(row,1)
 need(start["job"]==job and start["neural_worker_source"]==PINS["common"]and start["actual_allocation"]["raw_allocation_identity"]==allocated["raw_allocation_identity"],"External successor start lineage differs")
def independent_copy_tree(config,plan,analysis,scored,tree):
 tree=project(tree);tree.mkdir(exist_ok=False);items={}
 def add(rr):
  p=verify(rr);key=str(p.relative_to(R))
  if key in items:need(items[key]==rr,"Independent logical byte receipt conflict")
  else:items[key]=rr
 for name in("result","analysis_plan","membership","producer_acceptance"):add(rec(config[name]))
 add(scored["plan"]);add(config["official_ipsae"]);add(config["msa_roundtrip_source"])
 for job in plan["jobs"]:add(job["input"])
 for target in analysis["targets"]:add(target["reference_complex"])
 for result in scored["results"]:
  if result["worker_record"]:add(result["worker_record"])
  for rr in result.get("protocol_files",[]):add(rr)
  for model in result["models"]:
   for rr in model.get("raw_files",[]):add(rr)
 mappings=[]
 for relative,rr in sorted(items.items()):
  dest=tree/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(verify(rr),dest);copied=rec(dest)
  need(copied["sha256"]==rr["sha256"]and copied["bytes"]==rr["bytes"],"Independent evidence copy differs");dest.chmod(0o444)
  mappings.append(dict(original=rr,restored=copied))
 return dict(status="CURRENT_COMMON_INDEPENDENT_INPUT_SUBSET_BYTECOPIED",authority_root=str(R),restore_root=str(tree),files=mappings,complete_final_project_restore=False,no_original_evidence_reads_in_next_audit=True,conditional_CPU_software=str(R/"env/colabfold/bin/python"))
def finish(args,out):
 guard=cpu();source=sources();pr=receipt_arg(args.preflight,args.preflight_sha256);pre=read(verify(pr))
 need(pre["source"]==source,"Finish exact CPU-tested source set differs")
 prepared,collection,plan,analysis,membership,scope=validate_inputs(pre["preparation"]);need(scope==pre["scope"],"Sensitivity denominator changed")
 for rr in pre["source"]["successor"]:verify(rr,True)
 for rr in pre["source"]["operative"].values():verify(rr)
 raw=project(pre["approved_raw_root"]);union=[];lineage_issues=[];source_qualification={}
 common=load("successor_terminal_common",PINS["common"])
 cached_rows=pre["cached_workers"]
 pending=pre["root_pending_job_indices"];allocationrows=[];subreceipt=None
 if pending:
  subreceipt=receipt_arg(args.submission,args.submission_sha256);sub=read(verify(subreceipt));array,launcher=submission_contract(sub,pr,pre)
  queued=subprocess.run(["squeue","-h","-j",array],capture_output=True,text=True,check=True);need(not queued.stdout.strip(),"Review GPU array still active")
  (out/"squeue.txt").write_text(queued.stdout)
  sacct=subprocess.run(["sacct","-n","-P","-j",array,"--format=JobID,JobIDRaw,State,ElapsedRaw,AllocTRES,Start,End,NodeList"],capture_output=True,text=True,check=True)
  (out/"sacct.txt").write_text(sacct.stdout);allocationrows=scheduler_rows(sacct.stdout,array,pending,resource_strict=False);indexed={r["index"]:r for r in allocationrows}
  # Durable numeric cost first, independent of absent/malformed worker metadata.
  dump(out/"review_allocations.json",dict(status="ALL_PENDING_COMMON_NUMERIC_COSTS_READ_BACK_RESOURCE_CLOSURE_PENDING",root_submission=subreceipt,rows=allocationrows,actual_new_review_GPU_seconds=sum(r["actual_GPU_seconds"]for r in allocationrows),old_native_GPU_cost_not_recharged=True))
  try:scheduler_rows(sacct.stdout,array,pending,resource_strict=True)
  except Exception as e:lineage_issues.append(dict(scope="all_current_review_allocations",reason_type=type(e).__name__,reason=str(e)))
  for i in pending:
   j=plan["jobs"][i];path=raw/j["job_key"]/"worker.json"
   source_qualification[j["job_key"]]="UNRESOLVED_WORKER_LINEAGE_COORDINATES_ONLY"
   if path.exists():
    try:
     start_path=project(pre["dispatch_claim_root"])/str(i)/"start.json";start=read(start_path)
     new_worker_check(read(path),j,plan,indexed[i],launcher,start,i,pr,pre)
     need(not any(q.get("scope")=="all_current_review_allocations"for q in lineage_issues),"Current allocation shared resource closure unresolved")
     source_qualification[j["job_key"]]="PASSED_CURRENT_WORKER_SOURCE_OWNERSHIP_AND_SLOT_LINEAGE"
     union.append(dict(job_key=j["job_key"],role="NEW_CURRENT_COMMON_MODEL_INFERENCE",worker=rec(path),allocation=indexed[i],start=rec(start_path)))
    except Exception as e:
     lineage_issues.append(dict(job_key=j["job_key"],index=i,reason_type=type(e).__name__,reason=str(e)))
     union.append(dict(job_key=j["job_key"],role="WRITTEN_WORKER_LINEAGE_TYPED_UNRESOLVED",worker=rec(path),allocation=indexed[i],reason=str(e)))
   else:union.append(dict(job_key=j["job_key"],role="MODEL_WORKER_UNRESOLVED_NO_IMPUTATION",reason="Worker not written by terminal allocated slot",allocation=indexed[i]))
  dump(out/"review_resource_closure.json",dict(status="ALL_PRESENT_COMMON_WORKER_OWNERSHIP_AND_SOURCE_CHECKS_PASSED"if not lineage_issues else"COMMON_REVIEW_LINEAGE_TYPED_UNRESOLVED",root_submission=subreceipt,review_allocations=rec(out/"review_allocations.json"),missing_worker_costs_retained=True,issues=lineage_issues))
 else:
  need(not args.submission and not args.submission_sha256,"No pending jobs means no new GPU submission")
  dump(out/"review_allocations.json",dict(status="ZERO_PENDING_GPU_SLOTS",rows=[],actual_new_review_GPU_seconds=0,old_native_GPU_cost_not_recharged=True))
 for cache in cached_rows:
  key=cache["job_key"];source_qualification[key]="UNRESOLVED_WORKER_LINEAGE_COORDINATES_ONLY"
  try:
   for pair in cache["files"]:verify(pair["copy"])
   verify(cache["approved_worker"]);source_qualification[key]="PASSED_EXACT_CPU_NATIVE_CACHE_SOURCE_AND_SLOT_BINDING"
   union.append(dict(job_key=key,role="HISTORICAL_NATIVE_RAW_BOUND_BY_CPU_CACHE_PROOF",worker=cache["approved_worker"],original_GPU_allocation=cache["original_GPU_allocation"],old_cost_recharged=False))
  except Exception as e:
   lineage_issues.append(dict(job_key=key,scope="cache_lineage",reason_type=type(e).__name__,reason=str(e)))
   union.append(dict(job_key=key,role="CACHE_WORKER_LINEAGE_TYPED_UNRESOLVED",reason=str(e),original_GPU_allocation=cache["original_GPU_allocation"],old_cost_recharged=False))
 if not {p.name for p in raw.iterdir()if p.is_dir()}<={j["job_key"]for j in plan["jobs"]}:lineage_issues.append(dict(scope="raw_union",reason="Unjoined raw worker directory"))
 dump(out/"raw_union.json",dict(schema="formal_common_raw_union.v1",preflight=pr,rows=union,expected_jobs=scope["n_jobs"],expected_models=scope["n_models"],old_worker_JSON_bytes_preserved=not any(q.get("scope")=="cache_lineage"for q in lineage_issues),no_scores_transferred=True,source_qualification=source_qualification,lineage_issues=lineage_issues))
 intrinsic=load("successor_intrinsic_finish",pre["intrinsic_clearance_policy"]["source"]);need(intrinsic.POLICY==pre["intrinsic_clearance_policy"]["policy"],"Predeclared physical diagnostic policy differs")
 if lineage_issues:
  intrinsic.diagnose(plan,None,str(raw),common.find_raw,rec,verify,out/"intrinsic_clearance_unqualified_coordinates.json",pre["intrinsic_clearance_policy"]["source"],source_qualification)
  dump(out/"worker_lineage_incomplete.json",dict(status="WORKER_LINEAGE_UNRESOLVED_NO_SCORE_OR_PROMOTION",issues=lineage_issues,review_allocations=rec(out/"review_allocations.json"),physical_coordinates=rec(out/"intrinsic_clearance_unqualified_coordinates.json")))
  need(False,"Worker/source/allocation lineage unresolved; unqualified coordinate diagnostics retained")
 common=load("successor_final_common",PINS["common"]);scorepath=out/"score.json";common.score(prepared["outputs"]["inference_plan"]["path"],prepared["outputs"]["analysis_plan"]["path"],str(raw),str(scorepath))
 acceptancepath=out/"common_acceptance.json";common.verify_result(str(scorepath),prepared["outputs"]["membership"]["path"],str(acceptancepath))
 accepted=read(acceptancepath);scored=read(scorepath);need(accepted["n_jobs"]==scope["n_jobs"]and accepted["n_models_expected"]==scope["n_models"],"All primary/sensitivity models lost")
 intrinsic=load("successor_intrinsic_finish",pre["intrinsic_clearance_policy"]["source"]);need(intrinsic.POLICY==pre["intrinsic_clearance_policy"]["policy"],"Predeclared physical diagnostic policy differs")
 physical=intrinsic.diagnose(plan,scored,str(raw),common.find_raw,rec,verify,out/"intrinsic_clearance.json",pre["intrinsic_clearance_policy"]["source"],source_qualification)
 need(physical["expected_models"]==scope["n_models"],"Full physical fixed model denominator differs")
 # Preserve all112 null/empty/partial producer rows before the independent gate can reject partial AF2 protocols.
 statlib=load("successor_target_statistics",PINS["statistics"]);cohorts=read(verify(collection["files"]["cohorts"]));formalplan=read(PINS["plan"]["path"])
 stats=statlib.statistics(accepted,formalplan,cohorts,"rf_diffusion","bindcraft");need(stats["n_cohort_engine_rows"]==112,"Fixed112 rows lost")
 statpath=out/"target_statistics.json";dump(statpath,stats)
 config=dict(result=str(scorepath),analysis_plan=prepared["outputs"]["analysis_plan"]["path"],membership=prepared["outputs"]["membership"]["path"],producer_acceptance=str(acceptancepath),official_ipsae=plan["runtime_locks"]["ipsae"],msa_roundtrip_source=plan["runtime_locks"]["msa_roundtrip_module"],colabfold_cpu_python=str(R/"env/colabfold/bin/python"))
 dump(out/"independent_common_config.json",config)
 independent_tree=out/"independent_input_tree";copied=independent_copy_tree(config,plan,analysis,scored,independent_tree);dump(out/"independent_input_copy_manifest.json",copied)
 independent=load("successor_independent_common",PINS["independent"]);independent_result=independent.audit_common(config,str(R),str(independent_tree),independent_tree/"recomputed",None)
 need(independent_result["status"]=="RESTORED_RAW_COMMON_SCORES_AND_COHORT_STATISTICS_RECOMPUTED","Independent current raw recomputation failed")
 formalargv=[str(CORE),PINS["formal"]["path"],"--plan",PINS["plan"]["path"],"--accounting",collection["files"]["accounting"]["path"],"--cohorts",collection["files"]["cohorts"]["path"],"--independent-budget",collection["files"]["independent_budget"]["path"],"--run-receipts",collection["files"]["run_receipts"]["path"],"--common",str(acceptancepath),"--membership",prepared["outputs"]["membership"]["path"],"--inference",prepared["outputs"]["inference_plan"]["path"],"--scored",str(scorepath),"--target-statistics",str(statpath),"--native-audits",collection["files"]["native_audits"]["path"],"--output",str(out/"formal112_acceptance.json")]
 dump(out/"formal112_command.json",dict(argv=formalargv));proc=subprocess.run(formalargv,capture_output=True,text=True)
 (out/"formal112.stdout").write_text(proc.stdout);(out/"formal112.stderr").write_text(proc.stderr);need(proc.returncode==0,"Independent formal112 fairness/raw closure failed")
 final=read(out/"formal112_acceptance.json");need(final["status"]=="INDEPENDENT_FORMAL112_FAIRNESS_AND_STATISTICS_AUDIT_PASS","Formal112 status differs")
 unresolved=[i for i,j in enumerate(plan["jobs"])if any(m["status"]=="MODEL_UNRESOLVED"for m in next(x for x in scored["results"]if x["job_key"]==j["job_key"])["models"])]
 return dump(out/"acceptance.json",dict(schema="formal_common_successor_acceptance.v1",status="FORMAL_COMMON_RAW_CONTENT_INDEPENDENT_AND112_ACCEPTED_COMPUTATIONAL_ONLY",source=source,allocation=guard,preflight=pr,root_submission=subreceipt,common_acceptance=rec(acceptancepath),independent_common=rec(independent_tree/"recomputed/acceptance.json"),independent_input_tree=rec(out/"independent_input_copy_manifest.json"),complete_final_project_restore=False,formal112=rec(out/"formal112_acceptance.json"),statistics=rec(statpath),raw_union=rec(out/"raw_union.json"),review_allocations=rec(out/"review_allocations.json"),scope=scope,n_fixed_cohort_engine_rows=112,n_primary_targets=6,n_diagnostic_targets=1,typed_unresolved_job_indices=unresolved,all_required_raw_model_exports_available=not unresolved,complete_macro_requires_all_six_pairs=True,intrinsic_target_binder_physical_clearance=rec(out/"intrinsic_clearance.json"),intrinsic_clearance_policy=pre["intrinsic_clearance_policy"],physical_flags_are_separate_diagnostics=True,workflow_superiority=False,experimental_binding_or_blockade=False,ACTIVE_changed=False,publication_pending=True))
def main():
 p=argparse.ArgumentParser();sp=p.add_subparsers(dest="mode",required=True)
 a=sp.add_parser("preflight")
 for k in("software-acceptance","software-acceptance-sha256","preparation","preparation-sha256","binding","binding-sha256","out"):a.add_argument("--"+k,required=True)
 a=sp.add_parser("finish")
 for k in("preflight","preflight-sha256","out"):a.add_argument("--"+k,required=True)
 a.add_argument("--submission");a.add_argument("--submission-sha256")
 a=sp.add_parser("worker");a.add_argument("--preflight",required=True);a.add_argument("--index",type=int,required=True)
 a=sp.add_parser("engine");a.add_argument("--preflight",required=True);a.add_argument("--index",type=int,required=True)
 args=p.parse_args()
 if args.mode=="engine":
  _,job=gpu_plan(read(args.preflight),args.index);print(job["engine"]);return
 if args.mode=="worker":worker(args);return
 out=project(args.out);out.mkdir(parents=True,exist_ok=False)
 try:
  rr=preflight(args,out)if args.mode=="preflight"else finish(args,out);print(json.dumps(rr))
 except Exception as e:
  dump(out/"typed_incomplete.json",dict(status="COMMON_SUCCESSOR_TYPED_INCOMPLETE",stage=args.mode,reason_type=type(e).__name__,reason=str(e),no_automatic_retry=True,no_promotion=True,existing_files=[str(p)for p in out.rglob("*")if p.is_file()]));raise
if __name__=="__main__":main()
