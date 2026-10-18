#!/usr/bin/env python3
"""Independent pureCPU exact BBF6 + recovered5 + historical9 mapper; no staging/raw rewriting."""
import argparse,importlib.util,json,shutil,subprocess,sys,unittest
from pathlib import Path
_s=importlib.util.spec_from_file_location("bootstrap_exact_context",Path(__file__).resolve().parent/"exact_relative_bbf_context.py")
bootstrap=importlib.util.module_from_spec(_s);_s.loader.exec_module(bootstrap)
NAMES=("finite_source_context.py","test_finite_source_context.py","exact_relative_bbf_context.py","test_exact_relative_bbf_context.py","context_mapper_audit_cpu.py","context_mapper_cpu.sbatch","context_consumer.py","HANDOFF.md","historical_annotation_context.py","test_historical_annotation_context.py","recovered_five_context.py","test_recovered_five_context.py","archive_member_context.py","test_archive_member_context.py")
CONTRACTS=201
def need(v,message):
 if not v:raise ValueError(message)
def rec(path):
 p=Path(path);data=p.read_bytes();return dict(path=str(p),bytes=len(data),sha256=__import__("hashlib").sha256(data).hexdigest())
def dump(path,obj):
 path=Path(path)
 with path.open("x")as f:f.write(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
 path.chmod(0o444);return rec(path)
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def run(request_path,out):
 allocation=bootstrap.cpu_guard();out=Path(out);request_path=Path(request_path)
 need(out.is_absolute()and out.is_relative_to(bootstrap.R/"steps/24_benchmark_delivery/runs")and out.resolve()==out and not out.exists(),"Fresh exact CPU authority output required")
 out.mkdir();phase="readonly_source_freeze"
 try:
  need(request_path.is_absolute()and request_path.is_relative_to(bootstrap.R)and request_path.resolve()==request_path and request_path.is_file()and not(request_path.stat().st_mode&0o222),"Readonly root-owned mapper request required")
  q=json.loads(request_path.read_text());need(q.get("schema")=="exact-current-context-mapper-request.v4"and q.get("root_owned")is True and q.get("raw_JSON_rewrite_allowed")is False and q.get("generic_relative_resolution_allowed")is False and q.get("generic_external_resolution_allowed")is False,"Distinct exact mapperV4 no-rewrite/no-generic request required")
  own=Path(__file__).resolve().parent;need(not(own.stat().st_mode&0o222),"Readonly whole reviewed source package required")
  frozen=out/"source";frozen.mkdir();sources=[];executed_original_sources=[]
  for name in NAMES:
   source=own/name;need(source.is_file()and not source.is_symlink()and not(source.stat().st_mode&0o222),"Whole fourteen readonly mapper source files required")
   executed_original_sources.append(rec(source))
   target=frozen/name;shutil.copyfile(source,target);target.chmod(0o444)
   need((rec(source)["bytes"],rec(source)["sha256"])==(rec(target)["bytes"],rec(target)["sha256"]),"Source copy byte mismatch")
   sources.append(rec(target))
  frozen.chmod(0o555);sys.path.insert(0,str(frozen))
  ctx=module("exact_relative_bbf_context",frozen/"exact_relative_bbf_context.py")
  hist=module("historical_annotation_context",frozen/"historical_annotation_context.py")
  five=module("recovered_five_context",frozen/"recovered_five_context.py")
  archives=module("archive_member_context",frozen/"archive_member_context.py")
  finite=module("finite_source_context",frozen/"finite_source_context.py")
  consumer=module("context_consumer",frozen/"context_consumer.py")
  phase="frozen_software_compile_bash_and_201_contracts"
  compiled=[]
  for p in sorted(frozen.glob("*.py")):compile(p.read_text(),str(p),"exec");compiled.append(rec(p))
  bash=subprocess.run(["bash","-n",str(frozen/"context_mapper_cpu.sbatch")],capture_output=True,text=True)
  for filename,value in (("bash_n.stdout",bash.stdout),("bash_n.stderr",bash.stderr)):
   with(out/filename).open("x")as f:f.write(value)
   (out/filename).chmod(0o444)
  need(bash.returncode==0,"Frozen mapperV4 launcher syntax failed")
  suite=unittest.TestSuite()
  for name in ("test_exact_relative_bbf_context","test_historical_annotation_context","test_recovered_five_context","test_archive_member_context","test_finite_source_context"):
   tests=module(name,frozen/(name+".py"));suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(tests))
  need(suite.countTestCases()==CONTRACTS,"Declared mapper software count differs")
  with(out/"contracts.log").open("x")as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
  (out/"contracts.log").chmod(0o444)
  contracts=dump(out/"contracts.json",dict(status="PASS"if result.wasSuccessful()else"FAIL",tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),tested_source_files=sources,log=rec(out/"contracts.log"),owned_python_compile_PASS=True,compiled_python_sources=compiled,bash_syntax_PASS=True,bash_syntax=dict(returncode=bash.returncode,stdout=rec(out/"bash_n.stdout"),stderr=rec(out/"bash_n.stderr")),fixture_hashes_are_only_toy_boundaries=True))
  need(result.wasSuccessful()and result.testsRun==CONTRACTS,"Actual mapper201 contracts failed")
  phase="actual_V10_base_closure_maps_and_parent_bytes"
  base_receipt=ctx.receipt(q["base_acceptance"]);relative=q["relative_receipt_context_mapping"];history=q["external_historical_receipt_context_mapping"];recovered=q["current_recovered_relative_receipt_context_mapping"];archived=q["archive_member_receipt_context_mapping"]
  base,closure=consumer.source_bundle(base_receipt,relative,history,lambda r:ctx.verify_bytes(r,True),recovered,archived)
  rm,relative_proof=ctx.verify_mapping_receipt(relative);hm,history_proof=hist.verify_mapping_receipt(history);fm,five_proof=five.verify_mapping_receipt(recovered);am,archive_proof=archives.verify_mapping_receipt(archived)
  # Both original JSON parents are actually read through bounded module-local views.
  reader=ctx.VerifiedContextReader(relative,lambda p:json.loads(Path(p).read_text()),q.get("bbf_parent_aliases",[]))
  rview=reader(ctx.PARENT["path"]);need(len(rview["outputs"])==6 and len(reader.used)==1,"Actual BBF6 parent view was not consumed")
  hreader=hist.VerifiedHistoricalAnnotationReader(history,lambda p:json.loads(Path(p).read_text()),q.get("historical_parent_aliases",[]))
  hview=hreader(hist.PARENT["path"]);need(len(hreader.used)==1 and len(hreader.used[0]["contexts"])==9,"Actual historical9 parent view was not consumed")
  freader=five.VerifiedRecoveredFiveReader(recovered,lambda p:json.loads(Path(p).read_text()),q.get("recovered_parent_aliases",[]))
  fview=freader(five.PARENT["path"]);need(len(freader.used)==1 and len(freader.used[0]["contexts"])==5,"Actual recovered5 parent view was not consumed")
  areader=archives.VerifiedArchiveMemberReader(archived,lambda p:json.loads(Path(p).read_text()),q.get("archive_parent_aliases",[]))
  for spec in archives.ARCHIVES:areader(spec["parent_manifest"]["path"])
  need({tuple(v["logical_parent"][k]for k in ("path","bytes","sha256"))for v in areader.used}=={tuple(s["parent_manifest"][k]for k in ("path","bytes","sha256"))for s in archives.ARCHIVES},"Actual two archive parent views were not consumed")
  archiveproof=dump(out/"archive_member_verification.json",archive_proof);archiveview=dump(out/"archive_member_read_view_proof.json",areader.proof())
  fiveproof=dump(out/"current_recovered_verification.json",five_proof);fiveview=dump(out/"current_recovered_read_view_proof.json",freader.proof())
  relproof=dump(out/"mapping_verification.json",relative_proof);histproof=dump(out/"historical_annotation_verification.json",history_proof)
  relview=dump(out/"read_view_proof.json",reader.proof());histview=dump(out/"historical_annotation_read_view_proof.json",hreader.proof())
  source_reader=finite.VerifiedFiniteSourceReader(base,closure,lambda p:json.loads(Path(p).read_text()),lambda r:ctx.verify_bytes(r,True),q.get("finite_source_parent_aliases",[]))
  for parent in finite.required_parent_receipts(source_reader.qualified):source_reader(parent["path"])
  source_reader.require_all_used()
  source_proof=dump(out/"finite_source_independent_verification.json",source_reader.verification)
  source_view=dump(out/"finite_source_read_view_proof.json",source_reader.proof())
  for r in sources:ctx.verify_bytes(r,True)
  executing_source_readback(executed_original_sources,sources)
  accepted=dict(schema="exact-current-context-mapper-acceptance.v4",status="EXACT_BBF6_RECOVERED5_NINE_ANNOTATIONS_ARCHIVE588_AND_EIGHT_SOURCE_ALIASES_MAPPER_CPU_ACCEPTED",request=rec(request_path),base_acceptance=base_receipt,source_closure=base["source_closure"],finite_source_independent_verification=source_proof,finite_source_read_view_proof=source_view,finite_source_recovery_inputs_qualification=base["finite_source_recovery_inputs_qualification"],finite_source_alias_verification=base["finite_source_alias_verification"],finite_exact_source_alias_index=base["finite_exact_source_alias_index"],exact_recovered_source_identity_n=8,exact_original_source_edge_n=12,relative_receipt_context_mapping=relative,external_historical_receipt_context_mapping=history,current_recovered_relative_receipt_context_mapping=recovered,archive_member_receipt_context_mapping=archived,archive_member_verification=archiveproof,archive_member_read_view_proof=archiveview,all_588_archive_member_bytes_independently_verified=True,archives_extracted=False,archive_current_files_restored=False,current_recovered_verification=fiveproof,current_recovered_read_view_proof=fiveview,all_five_current_recovered_outputs_actual_bytes_verified=True,contracts=contracts,mapping_verification=relproof,historical_annotation_verification=histproof,read_view_proof=relview,historical_annotation_read_view_proof=histview,source_files=sources,executed_original_sources=executed_original_sources,executing_source_prepost_byte_identity_verified=True,allocation=allocation,all_six_original_outputs_actual_bytes_verified=True,all_nine_original_annotations_actual_parent_bytes_verified=True,raw_historical_bytes_accepted=False,historical_files_restored=False,raw_JSON_changed=False,source_staged=False,published=False,ACTIVE_changed=False,GPU_submitted=False,scientific_scores_or_settings_changed=False)
  descriptor=dump(out/"acceptance.json",accepted);print(json.dumps(dict(status=accepted["status"],acceptance=descriptor),sort_keys=True),flush=True)
 except Exception as e:
  dump(out/"typed_incomplete.json",dict(status="EXACT_CURRENT_CONTEXT_MAPPER_TYPED_INCOMPLETE",failed_stage=phase,reason_type=type(e).__name__,reason=str(e),allocation=allocation,source_staged=False,raw_JSON_changed=False,ACTIVE_changed=False));raise
def executing_source_readback(originals,frozen):
 need(len(originals)==len(frozen)==len(NAMES),"Whole executing/frozen source universe required")
 by={Path(r["path"]).name:r for r in frozen}
 for r in originals:
  p=bootstrap.verify_bytes(r,True);f=by[Path(p).name];bootstrap.verify_bytes(f,True)
  need((r["bytes"],r["sha256"])==(f["bytes"],f["sha256"]),"Executing original source drift/frozen mismatch")
 return True
if __name__=="__main__":
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--request",required=True);ap.add_argument("--out",required=True);x=ap.parse_args();run(x.request,x.out)
