#!/usr/bin/env python3
"""CPU-only native74 raw reuse gate. No model calls, source rewriting or score transfer.
First source hash/tests/catalog proof occur on an actual CPU Slurm allocation.
Future formal binding is a separate command; historical acceptance is not that binding.
"""
import argparse,ast,copy,hashlib,importlib.util,json,os,shutil,subprocess,sys,unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
D=R/"steps/24_benchmark_delivery/code/native74_cache_guard_v1"
SELF=D/"native74_cache_guard.py"
CORE=R/"env/core/bin/python"
def reference(rel,n,h):return dict(path=str(R/rel),bytes=n,sha256=h)
PINS={
"native":reference("steps/24_benchmark_delivery/runs/native74_final_v2_13211/native74/acceptance.json",9602,"9effb60abceb03ca8c47b8e786f6613486bec96c90dec6aec517a1bd415fcff9"),
"edge":reference("steps/24_benchmark_delivery/runs/native74_edge_seal_13214/acceptance.json",772271,"aa350763e14103e2cde432652b83fd6c5e95fd11569d663364e9c4ecb82bd45c"),
"old":reference("steps/23_common_review/frozen/native_common_13051/code/benchmark_common_review.py",59077,"876d29f9b8a20cf3f8bbf526262de96b1071a30b47590b632e5d31f97c362391"),
"new":reference("steps/23_common_review/frozen/common_core_v2_13130/code/benchmark_common_review_v2.py",62153,"7d72314e0409fa1fb2a6ed86f593b198cf3e5c99f747c58d8cfa7d1fd0404d17"),
"new_bundle":reference("steps/23_common_review/frozen/common_core_v2_13130/source_bundle.json",12276,"7743873fb5ec089c1edb14670823dc76c6f614dae9dec4baba19ca805cc7b804"),
"old_plan":reference("steps/23_common_review/runs/native_controls_frozen_13051/inference_plan.json",30895,"9c90d720d39f306e9c601a8281afaca0d29ac986872805dd6b913eb8f2e9373b"),
"pipeline":reference("steps/23_common_review/runs/downstream_frozen_13119/code/native_review_pipeline_v2.py",17474,"56648b7f905abfc393526fcba04dcd5e7ecc9cb4437db796b3b58047292b77fa"),
"resource":reference("steps/22_matched_benchmark/code/resource_contract_v3/source/independent_resource_policy.py",17811,"8449b40f4ffbe3d9e321335bccb9bfcc163291ac3f67497c66fe1555bcd2f6bc"),
"formal_plan":reference("steps/22_matched_benchmark/formal_freeze_13257/plan/frozen_plan.json",20295,"e913d1bbccd531bf88a73f6ba60e8a0de85bb03ad8bcd3455d8952ca4effe0b6")}
RAWROOTS=[
str(R/"steps/23_common_review/runs/native_controls_frozen_13051/raw"),
str(R/"steps/23_common_review/runs/allocation_v2_13106/native_index19/raw"),
str(R/"steps/23_common_review/engineering_history/native_index18_20261011/raw")]
SCIENCE_AST=["job_signature","units","geometry","one_score","blind_entities","a3m_rows","assert_mapping","seqcheck","transform_fit","find_raw"]
def need(v,msg):
 if not v:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text())
def rec(p):
 p=Path(p).resolve();h=hashlib.sha256()
 with p.open("rb")as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return dict(path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest())
def fp(r):return r["bytes"],r["sha256"]
def verify(r,readonly=False):
 p=Path(r["path"]);need(p.is_file()and not p.is_symlink(),"Missing or symbolic operative evidence: "+str(p))
 need(p.resolve().is_relative_to(R),"Evidence outside project")
 need(rec(p)==r,"Exact evidence bytes changed: "+str(p))
 need(not readonly or not(p.stat().st_mode&0o222),"Readonly source required: "+str(p));return p
def dump(p,o):
 p=Path(p)
 with p.open("x")as f:json.dump(o,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
 return rec(p)
def load_module(name,r):
 p=verify(r,True);spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def cpu():
 need(os.environ.get("CUDA_VISIBLE_DEVICES")=="","CPU requires exact empty CUDA mask")
 need(os.environ.get("PYTHONDONTWRITEBYTECODE")=="1"and os.environ.get("PYTHONNOUSERSITE")=="1","Source/import isolation required")
 need(os.environ.get("JAX_PLATFORMS")=="cpu"and os.environ.get("OPENBLAS_NUM_THREADS")=="1","CPU backend and thread bound required")
 need("PYTHONPATH"not in os.environ,"Injected Python path forbidden")
 need(Path.cwd()==R/"steps/24_benchmark_delivery","Wrong CPU working directory")
 return load_module("native_cache_resource",PINS["resource"]).cpu_guard()
def seal_source(out):
 need(Path(__file__).resolve()==SELF and not(D.stat().st_mode&0o222),"Readonly exact source context required")
 files=[]
 for name in ["native74_cache_guard.py","test_native74_cache_guard.py","native74_cache_cpu.sbatch","HANDOFF.md"]:
  p=D/name;need(not p.is_symlink()and not(p.stat().st_mode&0o222),"Readonly source regular files required")
  if p.suffix==".py":compile(p.read_bytes(),str(p),"exec",dont_inherit=True)
  files.append(rec(p))
 return dump(out/"source.json",dict(status="FIRST_ACTUAL_CPU_SOURCE_HASH_SEALED",files=files,pre_submission_CPU_tests="NOT_EXECUTED_RESOURCE_UNAVAILABLE",no_inference=True))
def contracts(out):
 sp=importlib.util.spec_from_file_location("native_cache_tests",D/"test_native74_cache_guard.py");m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 suite=unittest.defaultTestLoader.loadTestsFromModule(m)
 with(out/"contracts.txt").open("x")as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
 rr=dump(out/"contracts.json",dict(status="PASS"if result.wasSuccessful()else"FAIL",tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),log=rec(out/"contracts.txt")))
 need(result.wasSuccessful(),"Software cache guard contracts failed");return rr
def functions(text):
 return {n.name:n for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
def astval(v):return ast.dump(v,include_attributes=False)
def scientific_compatibility(old_text,new_text):
 old=functions(old_text);new=functions(new_text)
 for name in SCIENCE_AST:need(astval(old[name])==astval(new[name]),"Scientific function changed: "+name)
 def settings(text):
  return next(n for n in ast.parse(text).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=="SETTINGS"for t in n.targets))
 need(astval(settings(old_text))==astval(settings(new_text)),"SETTINGS AST changed")
 worker=copy.deepcopy(new["worker"])
 expected_call=ast.parse("require_immutable_source_context()").body[0]
 expected_check=ast.parse('if plan["source"]["path"]!=str(Path(__file__).resolve()) or plan["frozen_source_bundle"]["path"]!=str(FROZEN_DIR.parent/"source_bundle.json"):raise ValueError("GPU plan source does not bind this immutable corrected core")').body[0]
 need(astval(worker.body[0])==astval(expected_call),"Unexpected worker context change")
 need(astval(worker.body[4])==astval(expected_check),"Unexpected worker binding change")
 worker.body=[x for i,x in enumerate(worker.body)if i not in{0,4}]
 need(astval(worker)==astval(old["worker"]),"Model execution AST changed beyond exact source guard")
 return dict(scientific_functions_identical=SCIENCE_AST,settings_AST_identical=True,model_execution_AST_identical_after_exact_two_identity_guards=True)
class OldResolver:
 def __init__(self,index):
  self.aliases={};self.history=set()
  for x in index["aliases"]:
   key=(x["original"]["path"],x["original"]["sha256"])
   need(key not in self.aliases or self.aliases[key]["archived"]==x["archived"],"Conflicting historical alias")
   need(x["status"]=="READONLY_BYTE_IDENTICAL_ALIAS"and fp(x["original"])==fp(x["archived"]),"Alias changes actual content")
   self.aliases[key]=x
  for x in index["historical_unresolved"]:
   need(x["status"]=="HISTORICAL_UNRESOLVED_PROVENANCE","Untyped historical missing")
   self.history.add((x["original"]["path"],x["original"]["sha256"]))
  need(len(self.history)==2,"Only accepted two historical MSA derivation gaps expected")
 def verify(self,r):
  key=(r["path"],r["sha256"]);need(key not in self.history,"Historical missing cannot satisfy operative cache proof")
  if key in self.aliases:return verify(self.aliases[key]["archived"],True)
  return verify(r)
def source_pairs(bundle):
 pairs={}
 for x in bundle["files"]:
  original=x["original"];frozen=x["frozen"];verify(frozen,True)
  need(fp(original)==fp(frozen),"New bundle copy differs from its declared original")
  pairs[(original["path"],frozen["path"])]=fp(original)
 return pairs
def runtime_compatibility(old,new,pairs,live=True):
 a=old["runtime_locks"];b=new["runtime_locks"]
 need(set(b)==set(a)|{"gpu_ownership_guard"},"Unexpected operative runtime key change")
 for k,r in a.items():
  s=b[k];need(fp(r)==fp(s),"Current model/runtime bytes differ: "+k)
  need(r["path"]==s["path"]or pairs.get((r["path"],s["path"]))==fp(r),"Unqualified runtime path rebind: "+k)
  if live:verify(s)
 if live:verify(b["gpu_ownership_guard"],True)
 need([fp(r)for r in old["af2_parameter_receipts"]]==[fp(r)for r in new["af2_parameter_receipts"]],"Model weights receipts differ")
 if live:
  for r in new["af2_parameter_receipts"]:verify(r)
 return dict(shared_runtime_keys=sorted(a),added_identity_guard_only=True,model_parameter_receipts_identical=True,current_operative_receipts_exact=True)
def planned_control_jobs(plan,controls):
 ids={x["blind_id"]for x in controls};need(len(ids)==7 and len(controls)==7,"Exact7 controls required")
 jobs=[x for x in plan["jobs"]if x["blind_id"]in ids]
 need(len(jobs)==20 and sum(j["expected_models"]for j in jobs)==74,"Full20 workers/74 control raw models required")
 keys=[(x["target_id"],x["engine"],x["variant"])for x in jobs];need(len(set(keys))==20,"Duplicate control job identity")
 return jobs
def binding(oldjob,newjob,oldentity,newentity,oldtarget,newtarget,signature):
 need(oldentity==newentity,"Full chain/query/entity identity differs")
 need(signature(oldjob)==signature(newjob),"Exact job input/MSA/model-seed/settings signature differs")
 a={k:v for k,v in oldtarget.items()if k!="input_manifest"};b={k:v for k,v in newtarget.items()if k!="input_manifest"}
 need(a==b,"Reference geometry or target identity changed beyond manifest pointer")
 return dict(job_signature=signature(newjob),input_bytes_identical=fp(oldjob["input"])==fp(newjob["input"]),query_entities_identical=True,reference_geometry_identical=True)
def prove_catalog(out):
 native=read(verify(PINS["native"]));edge=read(verify(PINS["edge"]))
 need(native["status"]=="NATIVE74_FULL_RAW_AND_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY","Native74 not accepted")
 need(edge["prior_final_native_acceptance"]==PINS["native"]and edge["raw_model_outcomes"]=={"VALID":74},"Independent edge seal does not bind all74")
 need(edge["n_typed_historical_unresolved"]==2 and edge["original_resource_fallback_used"]is False,"Historical qualification differs")
 need(native["raw_source_roots"]==RAWROOTS,"Original three-source raw recovery differs")
 index=read(verify(native["resource_aliases"]));resolver=OldResolver(index)
 old=read(resolver.verify(PINS["old_plan"]));oldanalysis=read(resolver.verify(native["analysis"]));oldmembership=read(resolver.verify(native["membership"]))
 need(old["source"]==PINS["old"] and native["original_scientific_pipeline"]==PINS["pipeline"],"Original scientific source differs")
 compatibility=scientific_compatibility(verify(PINS["old"],True).read_text(),verify(PINS["new"],True).read_text())
 pairs=source_pairs(read(verify(PINS["new_bundle"])))
 pipeline=load_module("native_cache_original_pipeline",PINS["pipeline"]);newmodule=load_module("native_cache_common",PINS["new"])
 need(old["settings"]==newmodule.SETTINGS,"Original/future settings differ")
 jobs=planned_control_jobs(old,oldmembership["controls"]);need(jobs==old["jobs"],"Original native plan contains noncontrol jobs")
 assembly=read(resolver.verify(native["assembly"]));rawaudit=read(resolver.verify(native["independent_raw_audit"]))
 score=read(resolver.verify(native["canonical_score"]));msa=read(resolver.verify(native["independent_current_MSA_audit"]))
 need(assembly["n_jobs_copied"]==20 and rawaudit["n_raw_confidence_accepted"]==74 and rawaudit["n_raw_unresolved"]==0,"Full source assembly/raw74 closure lost")
 need(msa["n_jobs_expected"]==msa["n_jobs_accepted"]==7 and not msa["old_MSA_derivation_sources_executed"],"Current actual MSA features unqualified")
 entities={x["blind_id"]:x for x in old["entities"]};targets={x["target_id"]:x for x in oldanalysis["targets"]}
 sourceby={x["job_key"]:x for x in assembly["rows"]};scoreby={x["job_key"]:x for x in score["results"]};rows=[]
 need(len(sourceby)==20 and len(scoreby)==20,"Native exact workers lost or duplicated")
 for i,job in enumerate(jobs):
  a=sourceby[job["job_key"]];expectedroot=RAWROOTS[2 if i==18 else 1 if i==19 else 0]
  need(a["index"]==i and a["source_directory"]==expectedroot+"/"+job["job_key"],"Original worker source/recovery18 mapping differs")
  workerpath=resolver.verify(a["copied_worker"]);worker=read(workerpath)
  need(fp(a["original_worker"])==fp(a["copied_worker"]),"Worker JSON was rewritten")
  need(worker["source"]==old["source"]and worker["frozen_source_bundle"]==old["frozen_source_bundle"]and worker["runtime_locks"]==old["runtime_locks"],"Original worker operative provenance differs")
  need(worker["settings"]==old["settings"]and newmodule.job_signature(worker["job"])==newmodule.job_signature(job),"Original job settings/signature differs")
  allocation=pipeline.selected_allocation(worker,i)
  records=[];relseen=set()
  for pair in a["files"]:
   need(fp(pair["original"])==fp(pair["copy"]),"Original/copy content differs")
   rel=str(Path(pair["original"]["path"]).relative_to(a["source_directory"]));need(rel not in relseen,"Repeated cache file path");relseen.add(rel)
   physical=resolver.verify(pair["copy"]);records.append(dict(relative_path=rel,original=pair["original"],assembled=pair["copy"],verified_physical=rec(physical)))
  models=[]
  for slot in job["slots"]:
   model=pipeline.raw_model(job,entities[job["blind_id"]],slot,Path(a["copy_directory"]).parent)
   accepted=next(x for x in scoreby[job["job_key"]]["models"]if x["slot"]==slot)
   need(model["status"]=="RAW_EXACT_QUERY_CONFIDENCE_UNITS_ACCEPTED"and model["files"]==accepted["raw_files"]and model["global_iptm"]==accepted["global_iptm"],"Raw74 independent content readback changed")
   models.append(model)
  rows.append(dict(old_index=i,old_job=job,old_entity=entities[job["blind_id"]],old_target=targets[job["target_id"]],
    old_worker=a["copied_worker"],original_worker=a["original_worker"],original_source_root=expectedroot,
    allocation_identity=allocation["raw_allocation_identity"],signature=newmodule.job_signature(job),models=models,copy_files=records))
 need(sum(len(r["models"])for r in rows)==74,"Full74 readback denominator lost")
 result=dict(schema="native74_cache_catalog.v1",status="NATIVE74_RAW_CACHE_CATALOG_VERIFIED_FUTURE_FORMAL_BINDING_PENDING",
  native_acceptance=PINS["native"],independent_edge_seal=PINS["edge"],old_plan=PINS["old_plan"],old_source=PINS["old"],
  new_source=PINS["new"],new_source_bundle=PINS["new_bundle"],source_compatibility=compatibility,
  rows=rows,workers=20,raw_models=74,source_roots=RAWROOTS,split_recovery_index18_retained=True,
  historical_MSA_derivation_gaps_preserved=edge["historical_MSA_gaps"],historical_missing_exemption_for_current_inputs=False,
  old_runtime_locks=old["runtime_locks"],old_af2_parameter_receipts=old["af2_parameter_receipts"],
  no_new_predictions=True,no_scores_transferred=True,new_inference_GPU_seconds=0,old_GPU_cost_not_recharged=True,
  future_formal_binding=False)
 return dump(out/"catalog.json",result)
def copy_cache_row(row,destination):
 destination=Path(destination);destination.mkdir(parents=True,exist_ok=False);copied=[]
 for item in row["copy_files"]:
  rel=Path(item["relative_path"]);need(not rel.is_absolute()and ".."not in rel.parts,"Unsafe copied file relative path")
  source=verify(item["verified_physical"]);dest=destination/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  need(not dest.exists(),"Never overwrite cache evidence");shutil.copyfile(source,dest);need(fp(rec(dest))==fp(item["assembled"]),"Cache bytecopy differs");dest.chmod(0o444)
  copied.append(dict(original=item["original"],source=item["verified_physical"],copy=rec(dest)))
 worker=rec(destination/"worker.json");need(fp(worker)==fp(row["old_worker"]),"Original worker bytes rewritten")
 return dict(worker=worker,files=copied,source_identity_rewritten=False,scores_transferred=False)
def bind_future(args,out):
 cr=rec(Path(args.catalog));need(cr["sha256"]==args.catalog_sha256,"Exact accepted catalog receipt required")
 accepted=read(verify(cr));need(accepted["status"]=="CPU_CACHE_GUARD_CATALOG_COMPLETE" and accepted["no_inference"]is True,"Catalog CPU acceptance absent")
 need(read(verify(accepted["contracts"]))["status"]=="PASS","Catalog software contracts unaccepted")
 source=read(verify(accepted["source"]))
 need(rec(SELF)in source["files"],"Catalog source differs from binding source")
 for rr in source["files"]:verify(rr,True)
 catalog=read(verify(accepted["result"]));need(catalog["status"]=="NATIVE74_RAW_CACHE_CATALOG_VERIFIED_FUTURE_FORMAL_BINDING_PENDING"and catalog["workers"]==20 and catalog["raw_models"]==74,"Catalog not fully accepted")
 need(catalog["native_acceptance"]==PINS["native"]and catalog["independent_edge_seal"]==PINS["edge"],"Catalog historical acceptance differs")
 ar=rec(Path(args.preparation));need(ar["sha256"]==args.preparation_sha256,"Exact new common preparation receipt required")
 prepared=read(verify(ar));need(prepared["status"]=="FORMAL_BLIND_COMMON_REVIEW_PREPARED_NOT_INFERRED"and prepared["plan"]==PINS["formal_plan"]and prepared["source"]==PINS["new"],"Current formal common preparation unqualified")
 for rr in prepared["outputs"].values():verify(rr)
 collection=read(verify(prepared["collection"]));need(collection["status"]=="FORMAL_ALLOCATION_NATIVE_AND_COHORT_CLOSURE_ACCEPTED"and collection["plan"]==PINS["formal_plan"],"Formal generation acceptance absent")
 plan=read(verify(prepared["outputs"]["inference_plan"]));analysis=read(verify(prepared["outputs"]["analysis_plan"]));membership=read(verify(prepared["outputs"]["membership"]))
 need(plan["source"]==PINS["new"]and plan["frozen_source_bundle"]==PINS["new_bundle"]and plan["method_origin_present"]is False,"Future exact immutable common source/blinding differs")
 common=load_module("native_cache_bound_common",PINS["new"]);need(plan["settings"]==common.SETTINGS,"Future model settings changed")
 compatibility=scientific_compatibility(verify(PINS["old"],True).read_text(),verify(PINS["new"],True).read_text())
 runtime=runtime_compatibility(dict(runtime_locks=catalog["old_runtime_locks"],af2_parameter_receipts=catalog["old_af2_parameter_receipts"]),plan,source_pairs(read(verify(PINS["new_bundle"]))))
 for key in ["registry","msa","generation_gate_protocol"]:verify(plan[key])
 need(analysis["inference_plan"]==prepared["outputs"]["inference_plan"]and membership["inference_plan"]==analysis["inference_plan"],"Formal common membership/analysis plan identity differs")
 jobs=planned_control_jobs(plan,membership["controls"]);entities={x["blind_id"]:x for x in plan["entities"]};targets={x["target_id"]:x for x in analysis["targets"]}
 oldrows={(x["old_job"]["target_id"],x["old_job"]["engine"],x["old_job"]["variant"]):x for x in catalog["rows"]}
 need(len(oldrows)==20,"Duplicate catalog logical workers")
 rows=[];raw=out/"raw";raw.mkdir()
 for job in jobs:
  key=(job["target_id"],job["engine"],job["variant"]);oldrow=oldrows.get(key)
  try:
   need(oldrow is not None,"No original fixed native worker")
   verify(job["input"])
   if job.get("target_msa"):verify(job["target_msa"])
   proof=binding(oldrow["old_job"],job,oldrow["old_entity"],entities[job["blind_id"]],oldrow["old_target"],targets[job["target_id"]],common.job_signature)
   for m in oldrow["models"]:
    for rr in m["files"]:verify(rr)
   copied=copy_cache_row(oldrow,raw/job["job_key"])
   rows.append(dict(job_key=job["job_key"],status="CACHE_RAW_BOUND_TO_CURRENT_FORMAL_JOB",new_index=plan["jobs"].index(job),new_job=job,
    old_index=oldrow["old_index"],old_job=oldrow["old_job"],old_worker=oldrow["old_worker"],original_worker=oldrow["original_worker"],
    source_compatibility=proof,original_GPU_allocation=oldrow["allocation_identity"],copy=copied,no_new_inference=True))
  except Exception as e:
   rejected=None
   if(raw/job["job_key"]).exists():
    quarantine=out/"rejected_partial_cache";quarantine.mkdir(exist_ok=True);dest=quarantine/job["job_key"]
    need(not dest.exists(),"Rejected cache evidence collision");(raw/job["job_key"]).rename(dest);rejected=str(dest)
   rows.append(dict(rejected_partial_directory=rejected,job_key=job["job_key"],status="CACHE_NOT_REUSABLE_TYPED_REVIEW_REQUIRED",new_index=plan["jobs"].index(job),
    expected_models=job["expected_models"],reason_type=type(e).__name__,reason=str(e),no_invented_results=True))
 reusable={x["job_key"]for x in rows if x["status"]=="CACHE_RAW_BOUND_TO_CURRENT_FORMAL_JOB"}
 manifest=dict(schema="native74_current_formal_cache_binding.v1",
  status="CACHE_BINDING_CPU_COMPLETE_ALL20_REUSABLE"if len(reusable)==20 else"CACHE_BINDING_CPU_COMPLETE_WITH_TYPED_NONREUSABLE_JOBS",
  catalog=cr,preparation=ar,inference_plan=prepared["outputs"]["inference_plan"],source=rec(SELF),old_source=PINS["old"],current_source=PINS["new"],
  source_compatibility=compatibility,runtime_compatibility=runtime,rows=rows,reusable_workers=len(reusable),
  reusable_models=sum(x["new_job"]["expected_models"]for x in rows if x["job_key"]in reusable),
  root_pending_job_indices=[i for i,j in enumerate(plan["jobs"])if j["job_key"]not in reusable],
  cache_raw_root=str(raw),original_worker_bytes_unchanged=True,old_worker_source_claims_preserved=True,
  current_scorer_must_rescore_raw=True,no_scores_transferred=True,new_inference_GPU_seconds=0,old_GPU_cost_not_recharged=True,
  historical_MSA_gaps_cannot_satisfy_current_proof=True,no_GPU_submission=True)
 return dump(out/"binding.json",manifest)
def main():
 ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest="mode",required=True)
 a=sub.add_parser("catalog");a.add_argument("--out",required=True)
 a=sub.add_parser("contracts");a.add_argument("--out",required=True)
 a=sub.add_parser("bind")
 for k in ["catalog","catalog-sha256","preparation","preparation-sha256","out"]:a.add_argument("--"+k,required=True)
 args=ap.parse_args();guard=cpu();out=Path(args.out).resolve();out.relative_to(R/"steps/24_benchmark_delivery");out.mkdir(parents=True,exist_ok=False)
 try:
  source=seal_source(out);ct=contracts(out)
  result=prove_catalog(out)if args.mode=="catalog"else bind_future(args,out)if args.mode=="bind"else None
  dump(out/"acceptance.json",dict(status="CPU_CACHE_GUARD_"+args.mode.upper()+"_COMPLETE",source=source,contracts=ct,result=result,allocation=guard,no_inference=True,no_GPU_submission=True,formal_binding=args.mode=="bind"))
 except Exception as e:
  dump(out/"typed_incomplete.json",dict(status="CACHE_GUARD_TYPED_INCOMPLETE_NO_REUSE_AUTHORIZED",reason_type=type(e).__name__,reason=str(e),allocation=guard,no_inference=True));raise
if __name__=="__main__":main()

