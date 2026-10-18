#!/usr/bin/env python3
"""Root-submitted CPU DIAGNOSTIC_ONLY: immutable13368 toy65/official scorer IO.
No acceptance, no repaired SOURCE, no formal/common payload or GPU use.
"""
import contextlib,hashlib,importlib.util,io,json,os,pathlib,shutil,subprocess,sys,traceback
R=pathlib.Path("/lustre/users/u21111210118/projects/test9")
F=R/"steps/24_benchmark_delivery/frozen/final_delivery_composer_v6_restoreindex1_13368/code"
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
 m=load("exact_failed_composer_for_IO_diagnostic",F/"final_delivery_composer.py")
 allocation=m.cpu() # Actual owner/CPU1/GPU0/organ before hashing/content/scorer imports.
 source=m.sources();g=m.restore_index_api()
 owned=[m.rec(m.verify(m.rec(pathlib.Path(__file__).resolve()),True)),m.rec(m.verify(m.rec(pathlib.Path(__file__).with_name("diagnostic.sbatch")),True))]
 failed=m.load("diagnostic_pinned_common_parser",m.LIB/"common_review_independent_v2.py")
 actual=subprocess.check_output(["sacct","-X","-j","13368","--noheader","--parsable2","--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocCPUS,AllocTRES%300,User%64,Account%64,Partition%64"],text=True)
 fields=[v.split("|")for v in actual.splitlines()if v.split("|")[0]=="13368"];m.need(len(fields)==1,"Exact failed13368 terminal required")
 row=fields[0];values={}
 for token in row[5].split(","):
  m.need("="in token,"Terminal failed predecessor TRES missing");key,value=token.split("=",1);m.need(key not in values and key and value,"Duplicate failed predecessor TRES");values[key]=value
 m.need(row[1:3]==["FAILED","1:0"]and row[4]=="1"and values.get("cpu")=="1"and all(v.isdecimal()and int(v)==0 for k,v in values.items()if k.startswith("gres/gpu"))and row[6:9]==["u21111210118","u21111210118","organ"],"Actual failed CPU predecessor required")
 out=R/"steps/24_benchmark_delivery/runs"/("ipsae_synthetic_loader_diagnostic_"+os.environ["SLURM_JOB_ID"]);out.mkdir()
 m.dump(out/"predecessor.json",dict(status="FAILED_PREDECESSOR_PRESERVED_NO_ACCEPTANCE",sacct=actual,allocation=row))
 originals={}
 for name in("contracts.json","contracts.txt"):
  r=m.rec(R/"steps/24_benchmark_delivery/runs/final_composer_contracts_13368"/name);m.verify(r,True);originals[name]=r
 contracts=m.read(originals["contracts.json"]["path"]);m.need(contracts.get("tests_run")==126 and contracts.get("errors")==3 and contracts.get("failures")==0 and contracts.get("status")=="FAIL"and contracts.get("tested_source")==source and contracts.get("log")==originals["contracts.txt"],"Exact126/3ERROR failed software/source/log evidence")
 fixture=m.verify(next(r for r in source["composer"]if pathlib.Path(r["path"]).name=="test_restored_index_scope.py"),True).read_text()
 m.need('binder="C"*65;total=3+len(binder)'in fixture and '("A","ALA",0.,3),("B","CYS",4.,len(binder))'in fixture,"Exact reviewed failed toy65 fixture")
 source_r=m.RESTORE_FIXTURE_DEPENDENCIES[2];original_source=m.verify(source_r,True);source_data=original_source.read_bytes()
 authority=out/"original";authority.mkdir();root=out/"restored";root.mkdir()
 src=authority/"source/ipsae.py";src.parent.mkdir();src.write_bytes(source_data);src.chmod(0o444);src_r=m.rec(src);copy=root/"source/ipsae.py";copy.parent.mkdir();copy.write_bytes(source_data);copy.chmod(0o444)
 pkg=dict(schema="benchmark-delivery-package.v1",status="PACKAGED_AWAITING_INDEPENDENT_RESTORE",authority_root=str(authority),manifest=[dict(relative="source/ipsae.py",receipt=src_r,classification="SYNTHETIC_SOURCE")],config=src_r,phase_id="SYNTHETIC_IO_DIAGNOSTIC_ONLY",conditional_inference_dependencies=[])
 package_r=m.dump(out/"synthetic_source_package.json",pkg);owned_entry=next(r for r in source["composer"]if pathlib.Path(r["path"]).name=="restored_index_scope.py")
 runtime=dict(runtimes=dict(core=g.runtime_descriptor(sys.executable)))
 # Reproduce the exact FAILED13368 fixture producer route first. Its tested source
 # and helper are executed from immutable F; no method/parser/result replacement.
 sys.modules["final_delivery_composer"]=m
 fixture_module=m.load("exact_failed_fixture_producer",F/"test_restored_index_scope.py")
 instance=fixture_module.IndexContracts("test_26_actual_whole_core_nonempty_AF2_derived_protocol_and_roundtrip")
 reproduction=dict(kind="EXACT_FROZEN13368_SETUP_AND_MAKE_FULL_TRUE",fixture_source=next(r for r in source["composer"]if pathlib.Path(r["path"]).name=="test_restored_index_scope.py"),helper_source=owned_entry,method_result_mocked=False,source_or_parser_changed=False)
 import common_review_independent_v2 as exact_common
 original_subprocess=exact_common.subprocess;observed_processes=[]
 class ObservationOnlyProxy:
  def __getattr__(self,name):return getattr(original_subprocess,name)
  @staticmethod
  def run(argv,*args,**kwargs):
   result=original_subprocess.run(argv,*args,**kwargs) # Unchanged argv/kwargs and actual returned object.
   n=len(observed_processes);stdout=out/("exact_fixture_child_"+str(n)+".stdout");stderr=out/("exact_fixture_child_"+str(n)+".stderr")
   for p,value in((stdout,result.stdout),(stderr,result.stderr)):
    p.write_bytes(value if isinstance(value,bytes)else(value or"").encode());p.chmod(0o444)
   observed_processes.append(dict(argv=list(argv),returncode=result.returncode,stdout=m.rec(stdout),stderr=m.rec(stderr),actual_result_object_returned_without_modification=True));return result
 try:
  instance.setUp();instance.t._finalizer.detach() # Own diagnostic temp only, retain real evidence.
  exact_common.subprocess=ObservationOnlyProxy()
  instance.make_full(True);reproduction["observed_status"]="PREPARATION_COMPLETED_WITHOUT_EXPECTED_ERROR"
 except BaseException as e:reproduction.update(observed_status="ACTUAL_TYPED_PREPARATION_EXCEPTION",error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc())
 finally:exact_common.subprocess=original_subprocess
 reproduction["actual_unmodified_child_processes"]=observed_processes
 retained_fixture=out/"retained_exact_failed_fixture";copied=[]
 if hasattr(instance,"d")and instance.d.is_dir():
  reproduction["original_diagnostic_temp_path"]=str(instance.d)
  shutil.copytree(instance.d,retained_fixture,symlinks=True)
  for file in sorted(retained_fixture.rglob("*")):
   m.need(not file.is_symlink(),"Unexpected synthetic fixture symlink: copying never follows it")
   if file.is_file():file.chmod(0o444);copied.append(dict(relative=file.relative_to(retained_fixture).as_posix(),receipt=m.rec(file),role="SYNTHETIC_SOFTWARE_DIAGNOSTIC_ONLY"))
 reproduction["retained_copy_files"]=copied;reproduction["temporary_evidence_deleted"]=False
 normalized=retained_fixture/"restored/synthetic_producer_CPU_recomputation/af2"
 pdbfile=normalized/"model.pdb";scorefile=normalized/"scores.json"
 m.dump(out/"exact_fixture_reproduction.json",reproduction)
 if not(pdbfile.is_file()and scorefile.is_file()):
  m.need(m.sources()==source,"Exact failed source changed during partial reproduction")
  for r in owned+list(originals.values()):m.verify(r,True)
  record=m.dump(out/"diagnostic.json",dict(status="DIAGNOSTIC_ONLY_PARTIAL_EXACT_FIXTURE_NO_NORMALIZED_MODEL_INPUTS",allocation=allocation,source=source,executed_diagnostic_sources=owned,failed_originals=originals,reproduction=reproduction,source_acceptance=False,software_acceptance=False,scientific_result=False,formal_payload_read=False,GPU_used=False));print(json.dumps(record));return
 pdb_bytes=pdbfile.read_bytes();score_bytes=scorefile.read_bytes()
 normalized_inputs=[m.rec(pdbfile),m.rec(scorefile)];reproduction["normalized_input_receipts"]=normalized_inputs
 # Both exact failed normalized files, not independently hand-built approximations,
 # supply all six direct/loader/namespace comparisons below.
 input_receipts=[]
 def files(folder):
  folder.mkdir(parents=True);p=folder/"model.pdb";j=folder/"scores.json";p.write_bytes(pdb_bytes);j.write_bytes(score_bytes);p.chmod(0o444);j.chmod(0o444);input_receipts.extend([m.rec(p),m.rec(j)]);return p,j
 def inspect(table,snapshot=None):
  data=table.read_bytes()if table.is_file()else b""
  if snapshot is not None:snapshot.write_bytes(data);snapshot.chmod(0o444)
  observed=snapshot if snapshot is not None else table
  outcome=dict(original_table_path=str(table),table=m.rec(observed)if observed.is_file()else None,observed_byte_n=len(data),raw_text=data.decode(),header_lines=[x for x in data.decode().splitlines()if x.startswith("Chn1")])
  try:outcome["actual_unchanged_parser_result"]=failed.official_table(data.decode());outcome["parser_status"]="COMPLETE"
  except Exception as e:outcome.update(parser_status="TYPED_PARSER_REJECTION",error_type=type(e).__name__,error=str(e))
  return outcome
 reports=[]
 for cutoff in("10","15"):
  # Exact unchanged script under normal CLI.
  direct=out/("direct_"+cutoff);p,j=files(direct);pr=subprocess.run([sys.executable,str(copy),str(j),str(p),cutoff,"15"],capture_output=True,text=True)
  (direct/"stdout.txt").write_text(pr.stdout);(direct/"stderr.txt").write_text(pr.stderr)
  direct_report=dict(kind="DIRECT_UNCHANGED_OFFICIAL_CLI",inputs=[m.rec(p),m.rec(j)],cutoff=cutoff,returncode=pr.returncode,stdout=m.rec(direct/"stdout.txt"),stderr=m.rec(direct/"stderr.txt"),observed=inspect(direct/("model_"+cutoff+"_15.txt")))
  # Exact failed frozen helper's explicit source loader; no instrumentation of its bytes.
  child=root/("child_"+cutoff);p,j=files(child)
  c=dict(schema="indexed-IPSAE-subprocess-contract.v1",package=pkg,package_control=package_r,restore_root=str(root),new_output_root=str(child),aliases=dict(aliases=[]),owned_entry=owned_entry,runtime=runtime,source=src_r,generated_inputs=[m.rec(j),m.rec(p)],cutoff=cutoff)
  cr=m.dump(out/("child_contract_"+cutoff+".json"),c)
  pr=subprocess.run([sys.executable,owned_entry["path"],"child-ipsae","--contract",cr["path"],"--contract-sha256",cr["sha256"]],capture_output=True,text=True)
  (child/"stdout.txt").write_text(pr.stdout);(child/"stderr.txt").write_text(pr.stderr)
  child_report=dict(kind="EXACT_FROZEN13368_EXPLICIT_SOURCE_LOADER",cutoff=cutoff,contract=cr,returncode=pr.returncode,stdout=m.rec(child/"stdout.txt"),stderr=m.rec(child/"stderr.txt"),observed=inspect(child/("model_"+cutoff+"_15.txt")))
  # Diagnostic namespace retains the actual writer handles; sample before and after
  # their explicit flush/close to observe buffering, without changing script/scorer bytes.
  retained=out/("retained_namespace_"+cutoff);p,j=files(retained);old=sys.argv;sys.argv=[str(copy),str(j),str(p),cutoff,"15"];ns=dict(__name__="__main__",__file__=str(copy));stdout=io.StringIO();stderr=io.StringIO();exception=None
  try:
   with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):exec(compile(source_data,str(copy),"exec",dont_inherit=True),ns)
  except BaseException as e:exception=dict(type=type(e).__name__,message=str(e))
  finally:sys.argv=old
  (retained/"stdout.txt").write_text(stdout.getvalue());(retained/"stderr.txt").write_text(stderr.getvalue())
  before=inspect(retained/("model_"+cutoff+"_15.txt"),retained/("model_"+cutoff+"_15.beforeflush.txt"));streams=[]
  for name in("OUT","PML","OUT2"):
   handle=ns.get(name)
   if handle is None:streams.append(dict(name=name,status="WRITER_NOT_CREATED",exec_exception=exception));continue
   item=dict(name=name,file=getattr(handle,"name",None),closed_before=getattr(handle,"closed",None));streams.append(item)
   if not isinstance(item["file"],str)or not pathlib.Path(item["file"]).is_relative_to(retained):item["status"]="UNEXPECTED_OUTPUT_WRITER_PATH_NOT_TOUCHED";continue
   if item["closed_before"]is True:item["status"]="ALREADY_CLOSED_OBSERVED";continue
   try:handle.flush();handle.close();item["status"]="OPEN_WRITER_FLUSHED_AND_CLOSED_FOR_DIAGNOSTIC"
   except Exception as e:item.update(status="TYPED_DIAGNOSTIC_WRITER_OPERATION_EXCEPTION",error_type=type(e).__name__,error=str(e))
  after=inspect(retained/("model_"+cutoff+"_15.txt"))
  reports.extend([direct_report,child_report,dict(kind="RETAINED_ACTUAL_SCRIPT_NAMESPACE_BUFFER_OBSERVATION",inputs=[m.rec(p),m.rec(j)],cutoff=cutoff,exception=exception,stdout=m.rec(retained/"stdout.txt"),stderr=m.rec(retained/"stderr.txt"),writers=streams,before_flush=before,after_flush=after)])
 for folder in(out/"direct_10",out/"direct_15",root/"child_10",root/"child_15",out/"retained_namespace_10",out/"retained_namespace_15"):
  for file in folder.iterdir():
   if file.is_file()and not file.is_symlink():file.chmod(0o444)
 for r in input_receipts:
  path=m.verify(r,True);m.need(path.read_bytes()==(pdb_bytes if path.name=="model.pdb"else score_bytes),"Exact six-mode synthetic input changed")
 m.need(m.sources()==source,"Frozen failed sources/dependencies changed during diagnostic")
 for r in owned+list(originals.values()):m.verify(r,True)
 for item in copied:m.verify(item["receipt"],True)
 for r in normalized_inputs:m.verify(r,True)
 m.need(original_source.read_bytes()==source_data,"Pinned official source drifted")
 record=m.dump(out/"diagnostic.json",dict(schema="synthetic-official-IPSAE-source-loader-IO-diagnostic.v1",status="DIAGNOSTIC_ONLY_ACTUAL_BUFFERING_AND_PARSER_OBSERVATIONS_SAVED",allocation=allocation,source=source,executed_diagnostic_sources=owned,failed_predecessor="13368",failed_originals=originals,official_source=source_r,synthetic_source=src_r,synthetic_binder_length=65,synthetic_total_residues=68,exact_frozen_fixture_reproduction=reproduction,exact_normalized_input_receipts=normalized_inputs,all_mode_inputs=input_receipts,all_same_toy_input_bytes_before_and_after=True,reports=reports,source_acceptance=False,software_acceptance=False,scientific_result=False,formal_payload_read=False,GPU_used=False,original_SOURCE_or_scorer_changed=False))
 print(json.dumps(record))
if __name__=="__main__":main()
