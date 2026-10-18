"""32 strict-index contracts; real immutable budget/common/statistics and parsers.
All synthetic fixtures are SOFTWARE_ONLY, never actual GPU/scientific results.
"""
import copy,datetime,hashlib,json,os,shutil,subprocess,sys,tempfile,types,unittest
from pathlib import Path
import final_delivery_composer as m
g=m.restore_index_api()
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
def ho(o):return hashlib.sha256(canon(o).encode()).hexdigest()
class IndexContracts(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(dir=m.R/"steps/24_benchmark_delivery/tmp",prefix="index_restore_fixture_");self.d=Path(self.t.name);self.authority=self.d/"original";self.authority.mkdir();self.root=self.d/"restored";self.root.mkdir();self.out=self.root/"recomputed"
  self.files=[];self.a=self.file("evidence/input.json",b'{"SYNTHETIC":true}');self.b=self.file("workers/worker.json",b'{"SYNTHETIC":true}');self.cfg=self.file("workers/af2/config.json",b'{"SYNTHETIC":true}');self.msa=self.file("workers/af2/complex.a3m",b"SYNTHETIC")
  self.pkg=self.package(self.a);self.pkgr=self.control("package.json",self.pkg);self.marker=self.control_at(self.root/"RESTORE_HASH_ACCEPTANCE.json",dict(status="RESTORED_HASHES_VERIFIED_CONTENT_RECOMPUTATION_PENDING",package=self.pkgr))
  self.owned=m.sources()["composer"]
 def tearDown(self):
  for p in self.d.rglob("*"):
   if p.is_dir()and not p.is_symlink():p.chmod(0o755)
  self.t.cleanup()
 def file(self,name,data):
  p=self.authority/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);p.chmod(0o444);r=m.rec(p)
  q=self.root/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data);q.chmod(0o444);self.files.append(r);return r
 def obj(self,name,value):return self.file(name,(json.dumps(value,sort_keys=True)+"\n").encode())
 def control_at(self,p,value):
  p=Path(p);self.assertTrue(p.is_relative_to(self.d)and p.resolve()==p and not p.is_symlink());p.parent.mkdir(parents=True,exist_ok=True)
  if p.exists():self.assertTrue(p.is_file());p.unlink() # Replace only this test's readonly synthetic control, never authority.
  with p.open("x")as f:f.write(json.dumps(value))
  p.chmod(0o444);return m.rec(p)
 def control(self,name,value):return self.control_at(self.d/name,value)
 def package(self,config):
  return dict(schema="benchmark-delivery-package.v1",status="PACKAGED_AWAITING_INDEPENDENT_RESTORE",authority_root=str(self.authority),manifest=[dict(relative=Path(r["path"]).relative_to(self.authority).as_posix(),receipt=r,classification="EVIDENCE")for r in self.files],config=config,phase_id="SYNTHETIC_SOFTWARE_ONLY",conditional_inference_dependencies=[])
 def scope(self,aliases=None):return g.StrictIndex(self.pkg,self.root,self.out,aliases,controls=[self.pkgr,self.marker],owned=self.owned)
 def test_01_exact_input_proxy_and_byte_read(self):
  s=self.scope();p=s.input(self.a["path"],expected_sha=self.a["sha256"]).physical();self.assertIsInstance(p,g.IndexedPath);self.assertEqual(p.read_bytes(),b'{"SYNTHETIC":true}')
 def test_02_derived_AF2_protocol_files_must_be_indexed(self):
  s=self.scope();directory=s.input(self.b["path"]).physical().parent
  self.assertEqual((directory/"af2/config.json").read_bytes(),b'{"SYNTHETIC":true}');self.assertEqual((directory/"af2/complex.a3m").read_bytes(),b"SYNTHETIC")
 def test_03_unindexed_present_file_is_rejected(self):
  s=self.scope();p=self.root/"workers/af2/unindexed.json";p.write_text("{}");p.chmod(0o444)
  with self.assertRaises(ValueError):(s.input(self.b["path"]).physical().parent/"af2/unindexed.json").read_bytes()
  for bad in("af2/./config.json","af2//config.json","af2/../config.json","/af2/config.json"):
   with self.subTest(raw_path=bad),self.assertRaises(ValueError):s.input(self.b["path"]).physical().parent/bad
  for bad in(str(self.root)+"/./workers/worker.json",str(self.root)+"//workers/worker.json",str(self.root)+"/workers/../workers/worker.json"):
   with self.subTest(raw_input=bad),self.assertRaises(ValueError):s.input(bad)
 def test_04_missing_index_cannot_read_poisoned_live(self):
  pkg=copy.deepcopy(self.pkg);pkg["manifest"]=[x for x in pkg["manifest"]if x["receipt"]!=self.cfg];s=g.StrictIndex(pkg,self.root,self.out)
  self.assertTrue(Path(self.cfg["path"]).is_file())
  with self.assertRaises(ValueError):s.input(self.cfg["path"]).read_bytes()
 def test_05_changed_bytes_or_writable_input_rejected(self):
  p=self.root/"evidence/input.json";p.chmod(0o644)
  with self.assertRaises(ValueError):self.scope().input(self.a["path"]).read_bytes()
  p.write_text("CHANGED");p.chmod(0o444)
  with self.assertRaises(ValueError):self.scope().input(self.a["path"]).read_bytes()
 def test_06_package_duplicate_and_conflicting_paths_rejected(self):
  for change in(False,True):
   pkg=copy.deepcopy(self.pkg);extra=copy.deepcopy(pkg["manifest"][0])
   if change:extra["receipt"]["sha256"]="0"*64
   pkg["manifest"].append(extra)
   with self.subTest(conflict=change),self.assertRaises(ValueError):g.StrictIndex(pkg,self.root,self.out)
 def test_07_symlink_leaf_intermediate_root_rejected(self):
  p=self.root/"evidence/input.json";p.unlink();p.symlink_to(Path(self.a["path"]))
  with self.assertRaises(ValueError):self.scope().input(self.a["path"]).read_bytes()
  p.unlink();p.write_bytes(Path(self.a["path"]).read_bytes());p.chmod(0o444)
  directory=self.root/"evidence";saved=self.d/"moved_evidence";directory.rename(saved);directory.symlink_to(saved,target_is_directory=True)
  with self.assertRaises(ValueError):self.scope().input(self.a["path"]).read_bytes()
  directory.unlink();saved.rename(directory)
  saved_root=self.d/"moved_restore";self.root.rename(saved_root);self.root.symlink_to(saved_root,target_is_directory=True)
  with self.assertRaises(ValueError):self.scope()
  self.root.unlink();saved_root.rename(self.root)
 def test_08_exact_byte_alias_to_indexed_source(self):
  original=dict(self.a,path=str(self.authority/"vanished/old.json"));aliases=dict(aliases=[dict(original=original,archived=self.a,status="READONLY_BYTE_IDENTICAL_ALIAS")]);s=self.scope(aliases)
  self.assertEqual(s.input(original["path"],expected_sha=original["sha256"]).read_bytes(),b'{"SYNTHETIC":true}')
 def test_09_alias_missing_unindexed_or_changed_identity_rejected(self):
  for key,value in(("bytes",self.a["bytes"]+1),("sha256","0"*64),("path",str(self.authority/"missing.json"))):
   b=dict(self.a);b[key]=value;aliases=dict(aliases=[dict(original=self.a,archived=b,status="READONLY_BYTE_IDENTICAL_ALIAS")])
   with self.subTest(key=key),self.assertRaises(ValueError):self.scope(aliases)
 def test_10_glob_cannot_silently_read_unindexed_file(self):
  s=self.scope();self.assertEqual(len(list(s.input(str(self.authority/"workers/af2")).glob("*.json"))),1)
  p=self.root/"workers/af2/extra.json";p.write_text("{}");p.chmod(0o444)
  with self.assertRaises(ValueError):list(s.input(str(self.authority/"workers/af2")).glob("*.json"))
 def test_11_fspath_physical_parent_keeps_guard(self):
  s=self.scope();p=s.input(self.b["path"]).physical();self.assertEqual(os.fspath(p),str(self.root/"workers/worker.json"));self.assertIsInstance(p.parent/"af2/config.json",g.IndexedPath)
  with self.assertRaises(ValueError):os.fspath(p.parent/"af2/missing.a3m")
 def test_12_only_tagged_new_outputs_can_write(self):
  s=self.scope();out=s.structural(self.out);out.mkdir();p=out/"answer.json";p.write_text("{}");self.assertEqual(p.read_text(),"{}")
  with self.assertRaises(ValueError):s.input(str(self.out/"answer.json")).read_text()
  with self.assertRaises(ValueError):s.input(self.a["path"]).write_text("REWRITE")
 def test_13_output_scope_cannot_become_original_receipt(self):
  s=self.scope();out=s.output(self.out);out.mkdir();p=out/"generated.pdb";p.write_text("GENERATED")
  with self.assertRaises(ValueError):s.input(p)
  with self.assertRaises(ValueError):s.verify(m.rec(self.out/"generated.pdb"))
 def test_14_original_index_must_not_overlap_output_root(self):
  pkg=copy.deepcopy(self.pkg);r=dict(self.a,path=str(self.authority/"recomputed/raw.json"));pkg["manifest"].append(dict(relative="recomputed/raw.json",receipt=r))
  with self.assertRaises(ValueError):g.StrictIndex(pkg,self.root,self.out)
 def test_15_ambiguous_alias_versions_require_exact_SHA(self):
  older=self.file("evidence/older.json",b"OLDER");self.pkg=self.package(self.a);original=dict(older,path=self.a["path"]);s=self.scope(dict(aliases=[dict(original=original,archived=older,status="READONLY_BYTE_IDENTICAL_ALIAS")]))
  with self.assertRaises(ValueError):s.input(self.a["path"]).read_bytes()
  self.assertEqual(s.input(self.a["path"],expected_sha=older["sha256"]).read_bytes(),b"OLDER")
 def test_16_existing_out_or_path_escape_rejected(self):
  self.out.mkdir()
  with self.assertRaises(ValueError):self.scope()
  with self.assertRaises(ValueError):g.StrictIndex(self.pkg,self.root,self.d/"outside")
 def test_17_patch_finally_restores_all_module_globals(self):
  import restore_resolver_v2 as r
  import common_review_independent_v2 as c
  api=m.load("fixture_index_patch_core",m.LIB/"restore_verify_v2.py");before=(api.Path,api.read,api.rec,api.path_factory,r.path_factory,r.load_budget_auditor,c.Path,c.subprocess,c.path_factory)
  config=dict(official_ipsae=self.a,msa_roundtrip_source=self.a);entry=next(x for x in self.owned if Path(x["path"]).name=="restored_index_scope.py")
  with g.patched_core(api,self.scope(),config,entry):self.assertIsNot(api.Path,before[0]);self.assertIsNot(c.subprocess,before[7])
  self.assertEqual(before,(api.Path,api.read,api.rec,api.path_factory,r.path_factory,r.load_budget_auditor,c.Path,c.subprocess,c.path_factory))
 def test_18_error_branch_restores_all_module_globals(self):
  import restore_resolver_v2 as r
  import common_review_independent_v2 as c
  api=m.load("fixture_index_error_core",m.LIB/"restore_verify_v2.py");before=(api.Path,api.read,r.path_factory,c.Path,c.subprocess)
  with self.assertRaisesRegex(RuntimeError,"SYNTHETIC_EXCEPTION"):
   with g.patched_core(api,self.scope(),dict(official_ipsae=self.a,msa_roundtrip_source=self.a),self.owned[0]):raise RuntimeError("SYNTHETIC_EXCEPTION")
  self.assertEqual(before,(api.Path,api.read,r.path_factory,c.Path,c.subprocess))
 def test_19_runtime_binary_is_scalar_conditional_not_archived_source(self):
  r=g.runtime_descriptor(sys.executable);self.assertIs(r["included_in_package"],False);self.assertNotIn("path",r);g.verify_runtime(r)
  bad=dict(r,resolved_sha256="0"*64)
  with self.assertRaises(ValueError):g.verify_runtime(bad)
  base=dict(JobId="1",JobState="RUNNING",NumCPUs="1",UserId="u21111210118(1)",Account="u21111210118",Partition="organ",TRES="cpu=1,mem=16G,gres/gpu=0")
  self.assertEqual(g.child_allocation_shape(base,"1")["cpu"],"1");self.assertEqual(g.child_allocation_shape(dict(base,AllocTRES="gres/gpu=0,mem=16G,cpu=1"),"1")["cpu"],"1")
  for fields in(dict(base,AllocTRES="cpu=1,mem=16G,gres/gpu=1"),dict(base,TRES="cpu=1,cpu=1"),dict(base,TRES="cpu=x"),dict(base,TRES=""),dict(base,Account="other")):
   with self.subTest(fields=fields),self.assertRaises(ValueError):g.child_allocation_shape(fields,"1")
 def test_20_exact_legacy_subprocess_no_arbitrary_c_or_exec(self):
  s=self.scope();s.runtime=dict(runtimes=dict(core=g.runtime_descriptor(sys.executable),msa=g.runtime_descriptor(sys.executable)));f=g.isolated_subprocess(s,dict(official_ipsae=self.a,msa_roundtrip_source=self.a),self.owned[0],subprocess.run)
  for argv in(([sys.executable,"-c","print(1)"],["/bin/sh","-c","true"])):
   with self.subTest(argv=argv),self.assertRaises(ValueError):f(argv,capture_output=True,text=True)
 def test_21_ipSAE_source_and_unregistered_output_input_rejected(self):
  s=self.scope();s.runtime=dict(runtimes=dict(core=g.runtime_descriptor(sys.executable),msa=g.runtime_descriptor(sys.executable)));self.out.mkdir();(self.out/"scores.json").write_text("{}");(self.out/"model.pdb").write_text("SYNTHETIC")
  f=g.isolated_subprocess(s,dict(official_ipsae=self.a,msa_roundtrip_source=self.a),self.owned[0],subprocess.run)
  with self.assertRaises(ValueError):f([sys.executable,str(self.root/"evidence/input.json"),str(self.out/"scores.json"),str(self.out/"model.pdb"),"10","15"],capture_output=True,text=True)
 def test_22_readonly_metadata_seal_preserves_original_bytes(self):
  p=self.root/"evidence/input.json";p.chmod(0o664);before=p.read_bytes();r=g.seal_restored_metadata(self.pkg,self.root);self.assertEqual(before,p.read_bytes());self.assertFalse(p.stat().st_mode&0o222);self.assertTrue(r["rows"])
 def test_23_alias_physical_parent_derivation_uses_indexed_copy(self):
  original=dict(self.b,path=str(self.authority/"old_worker/worker.json"));s=self.scope(dict(aliases=[dict(original=original,archived=self.b,status="READONLY_BYTE_IDENTICAL_ALIAS")]))
  self.assertEqual((s.input(original["path"],expected_sha=original["sha256"]).physical().parent/"af2/config.json").read_bytes(),b'{"SYNTHETIC":true}')
 def test_24_after_read_drift_is_rejected(self):
  s=self.scope();s.input(self.a["path"]).read_bytes();p=self.root/"evidence/input.json";p.chmod(0o644);p.write_text("DRIFT");p.chmod(0o444)
  with self.assertRaises(ValueError):s.after()
 def make_full(self,nonempty):
  # A genuine archived tiny fixture with synthetic 28 budget allocations, never GPU jobs.
  self.files=[];source={};binder="C"*65;total=3+len(binder)
  for name,r in zip(("budget.py","control_msa_check.py","ipsae.py"),m.RESTORE_FIXTURE_DEPENDENCIES):source[name]=self.file("source/"+name,Path(r["path"]).read_bytes())
  input_r=self.obj("target_manifest.json",dict(SYNTHETIC_SOFTWARE_ONLY=True,binder_length=65));adapter=self.obj("adapter.json",dict(SYNTHETIC_UNEXECUTED_ADAPTER=True))
  p=dict(protocol_id="SYNTHETIC_28_PAIRED",scientific_scope="COMPUTATIONAL_ONLY",execution_mode="persistent_session",targets=[dict(target_id="T"+str(i),analysis_role="primary"if i<6 else"diagnostic",input_manifest=input_r)for i in range(7)],replicate_seeds=[17,29],methods=[dict(method_id=k,native_score_name="native",native_score_direction="higher",config_receipt=adapter,adapter_receipts=[adapter],session_start=["SYNTHETIC_UNEXECUTED_ADAPTER"])for k in("rf_diffusion","bindcraft")],gpu_count=1,budget_gpu_seconds=60,shutdown_reserve_seconds=10,accounting_tolerance_seconds=0,hardware=dict(gpu_name="FAKE_GPU_CPU_UNIT_TEST"),sampling=dict(salt="SYNTHETIC_FIXED",uniform_n_per_replicate=1,native_top_k_per_replicate=1))
  protocol=self.obj("protocol.json",p)
  tasks=[]
  for target in p["targets"]:
   for seed in p["replicate_seeds"]:
    pair=dict(protocol_id=p["protocol_id"],target_id=target["target_id"],seed=seed)
    for method in p["methods"]:
     key=dict(pair,method_id=method["method_id"]);tasks.append(dict(key,task_id=ho(key)[:24],pair_id=ho(pair)[:24],budget_gpu_seconds=60,array_index=len(tasks)))
  plan=dict(status="FROZEN_BEFORE_GENERATION",protocol=p,protocol_receipt=protocol,orchestrator=adapter,tasks=tasks);plan_r=self.obj("frozen_plan.json",plan)
  hardware=dict(gpus=[dict(index=0,uuid="GPU-SYNTHETIC",name="FAKE_GPU_CPU_UNIT_TEST",memory_total_mib=1,device_minor=3)],nvml_inventory=[dict(index=0,uuid="GPU-SYNTHETIC",name="FAKE_GPU_CPU_UNIT_TEST",memory_total_mib=1)],physical_inventory=[dict(device_minor=3,uuid="GPU-SYNTHETIC",name="FAKE_GPU_CPU_UNIT_TEST",information="Model: FAKE_GPU_CPU_UNIT_TEST\nGPU UUID: GPU-SYNTHETIC\nDevice Minor: 3\n")],stdout="0, FAKE_GPU_CPU_UNIT_TEST, 1, GPU-SYNTHETIC\n",assignment_environment=dict(SLURM_JOB_GPUS="3",SLURM_STEP_GPUS=None,CUDA_VISIBLE_DEVICES="0"),selection_basis="SLURM_JOB_GPUS",owned_gpu_uuids=["GPU-SYNTHETIC"],child_cuda_visible_devices="GPU-SYNTHETIC",cuda_visibility_remapping=dict(original_cuda_visible_devices="0",interpretation="LOCAL_INDICES_REMAPPED_TO_OWNED_UUID",owned_gpu_uuids=["GPU-SYNTHETIC"],derived_child_cuda_visible_devices="GPU-SYNTHETIC"))
  runs=[];account=[];sacct=[];sequence_hash=hashlib.sha256(binder.encode()).hexdigest()
  for i,task in enumerate(tasks):
   prefix="run"+str(i);jid=str(700000+i);start=self.file(prefix+"/scheduler.txt",("JobId="+jid+" JobState=RUNNING StartTime=1970-01-01T00:16:40+00:00 TRES=cpu=1,gres/gpu=1\n").encode());events=[];attempts=[]
   initial={k:v for k,v in dict(hardware=hardware,child_cuda_visible_devices="GPU-SYNTHETIC",gpu_ownership_status="RUNNING_SLURM_GPU_OWNERSHIP_VERIFIED",scheduler_alloc_tres="cpu=1,gres/gpu=1",scheduler_start=start).items()}
   session=dict(pid=123,stdout=self.file(prefix+"/session/stdout.log",b""),stderr=self.file(prefix+"/session/stderr.log",b""),argv=["SYNTHETIC_UNEXECUTED_ADAPTER"],ended_at_epoch=1050)
   if nonempty and i==0:
    expected=dict(protocol_sha256=protocol["sha256"],plan_sha256=plan_r["sha256"],method_config_sha256=adapter["sha256"],method_definition_sha256=ho(p["methods"][0]),target_manifest_sha256=input_r["sha256"])
    session["ready"]=self.obj(prefix+"/session/READY.json",dict(expected,schema="paired-budget-session-v1",status="READY",pid=123))
    event=dict(task_id=task["task_id"],attempt_index=0,sequence_record_id="SYNTHETIC_SEQ",lineage_id="SYNTHETIC_LINEAGE",sequence=binder,sequence_sha256=sequence_hash,internal_acceptance=False,native_score=.8,native_score_name="native",completed_at_epoch=1001,observed_at_epoch=1001,observed_before_generation_cutoff=True,source_line_number=1)
    events=[event];raw=self.file(prefix+"/session/attempt000000/sequences.jsonl",(json.dumps(event)+"\n").encode());attemptdir=self.authority/prefix/"session/attempt000000"
    identity=dict(expected,task_id=task["task_id"],protocol_id=p["protocol_id"],request_id="000000",attempt_index=0,replicate_seed=task["seed"],seed=int(ho(dict(protocol_id=task["protocol_id"],target_id=task["target_id"],replicate_seed=task["seed"],attempt_index=0))[:8],16),schema="paired-budget-session-v1",action="method-attempt",attempt_dir=str(attemptdir),generation_deadline_epoch=1050,deadline_epoch=1050,allocation_deadline_epoch=1060)
    terminal=self.obj(prefix+"/session/attempt000000/attempt_result.json",dict(status="SCIENTIFIC_REJECT"))
    response=self.obj(prefix+"/session/attempt000000/response.json",dict(schema="paired-budget-session-v1",status="COMPLETE",request_id="000000",attempt_result=terminal))
    attempts=[dict(task_id=task["task_id"],attempt_index=0,status="SCIENTIFIC_REJECT",complete_sequence_records=1,precutoff_sequence_records=1,raw_sequence_stream=raw,raw_native_screening_stream=None,adapter_result=terminal,execution=dict(transport="persistent_session_rpc",session_pid=123,request=self.obj(prefix+"/session/attempt000000/request.json",identity),response=response,stdout=self.file(prefix+"/session/attempt000000/stdout.log",b""),stderr=self.file(prefix+"/session/attempt000000/stderr.log",b""),session_stdout_offsets=[0,0],session_stderr_offsets=[0,0]))]
   al=self.file(prefix+"/attempts.jsonl","".join(json.dumps(x)+"\n"for x in attempts).encode());sl=self.file(prefix+"/sequences.jsonl","".join(json.dumps(x)+"\n"for x in events).encode())
   run=dict(initial,task=task,allocation_key=jid,attempt_count=len(attempts),status="BUDGET_EXHAUSTED_WITH_EXPLICIT_BOUNDARY_CENSORING",attempt_ledger=al,sequence_ledger=sl,allocation_started_at_epoch=1000,generation_cutoff_epoch=1050,allocation_deadline_epoch=1060,plan=plan_r,execution_mode="persistent_session",session=session,session_initialization_boundary_censored=not attempts,initial_receipt=self.obj(prefix+"/initial.json",initial),SYNTHETIC_SOFTWARE_ONLY=True)
   rr=self.obj(prefix+"/receipt.json",run);runs.append(rr);sacct.append("|".join([jid,"60","gres/gpu=1","COMPLETED","1970-01-01T00:16:40+00:00","1970-01-01T00:17:40+00:00","SYNTHETIC_NODE","organ"]))
   identity=dict(raw_allocation_id=jid,logical_allocation_key=jid,array_job_id=None,array_task_id=None)
   account.append(dict(raw_allocation_id=jid,logical_allocation_key=jid,allocation_identity=identity,attempt_count=len(attempts),allocated_gpu_seconds=60,allocated_gpu_seconds_minus_budget=0,comparable_full_budget=True,sequence_record_count=len(events),precutoff_sequence_record_count=len(events),native_accepted_attempts=0,attempt_status_counts={s:(1 if attempts and s=="SCIENTIFIC_REJECT"else 0)for s in("COMPLETED","ENGINEERING_FAILURE","INTERRUPTED","SCIENTIFIC_REJECT","TIMED_OUT_BOUNDARY")}))
  ledger=self.obj("run_receipts.json",runs);scheduler=self.file("sacct.txt",("\n".join(sacct)+"\n").encode());account_r=self.obj("accounting.json",dict(all_attempt_count=int(nonempty),allocated_gpu_seconds_all_attempts=1680,tasks=account))
  selected=[]
  if nonempty:
   for cohort in("uniform_all_complete","native_fixed_top_k"):
    key=dict(task_id=tasks[0]["task_id"],cohort=cohort,sequence_sha256=sequence_hash,primary_run_receipt=runs[0]);selected.append(dict(key,cohort_record_id=ho(key),sequence=binder,sampling_key=hashlib.sha256(canon([p["sampling"]["salt"],"T0",17,sequence_hash]).encode()).hexdigest(),native_score=None if cohort=="uniform_all_complete"else .8))
  coverage=[]
  for i,task in enumerate(tasks):
   n=int(nonempty and i==0);coverage.append(dict(task=task,n_unique_complete=n,n_native_score_available=n,n_native_score_missing=0,uniform_all_complete=dict(requested=1,selected=n,underfilled=n<1),native_fixed_top_k=dict(requested=1,selected=n,underfilled=n<1)))
  cohorts=self.obj("cohorts.json",dict(selected=selected,coverage=coverage))
  pdb=[];serial=1
  for chain,res,y,nres in(("A","ALA",0.,3),("B","CYS",4.,len(binder))):
   for i in range(1,nres+1):
    x=3.8*(i-1);z=1. if i%3==0 else 0.
    pdb.append(f"ATOM  {serial:5d}  CA  {res:3s} {chain}{i:4d}    {x:8.3f}{y:8.3f}{z:8.3f}{1.:6.2f}{90.:6.2f}           C  ");serial+=1
    pdb.append(f"ATOM  {serial:5d}  CB  {res:3s} {chain}{i:4d}    {x:8.3f}{y:8.3f}{z+1.5:8.3f}{1.:6.2f}{90.:6.2f}           C  ");serial+=1
  rawpdb=self.file("raw_toy/model.pdb",("\n".join(pdb)+"\nEND\n").encode());rawjson=self.obj("raw_toy/scores.json",dict(pae=[[5.]*total for _ in range(total)],plddt=[90.]*total,iptm=.8));reference=self.file("raw_toy/reference.pdb",Path(rawpdb["path"]).read_bytes())
  self.target_toy=dict(target_id="T0",reference_complex=reference,query_to_reference_indices={str(i):i for i in range(1,4)})
  raw_rows=dict(af2=dict(raw_files=[rawpdb,rawjson]))
  # Actual CPU-only array serialization and unchanged official rescoring create the synthetic
  # producer records; the whole core below independently rereads/recomputes these same inputs.
  if nonempty:
   import io,numpy as np,common_review_independent_v2 as common_api
   def npz(name,key,value):
    stream=io.BytesIO();np.savez(stream,**{key:np.asarray(value)});return self.file(name,stream.getvalue())
   raw_rows["boltz"]=dict(raw_files=[rawpdb,self.obj("raw_toy/confidence.json",dict(iptm=.8)),npz("raw_toy/pae_model.npz","pae",[[5.]*total for _ in range(total)]),npz("raw_toy/plddt_model.npz","plddt",[.9]*total)])
   preparatory_pkg=self.package(self.a);preparatory_control=self.control("synthetic_raw_source_package.json",preparatory_pkg)
   preparatory_runtime=dict(runtimes=dict(core=g.runtime_descriptor(sys.executable),msa=g.runtime_descriptor(str(m.R/"env/colabfold/bin/python"))))
   preparatory_scope=g.StrictIndex(preparatory_pkg,self.root,self.root/"synthetic_producer_CPU_recomputation",dict(aliases=[]),controls=[preparatory_control],owned=self.owned,runtime=preparatory_runtime)
   preparatory_api=m.load("unchanged_core_for_synthetic_raw_producer",m.LIB/"restore_verify_v2.py");entry=next(r for r in self.owned if Path(r["path"]).name=="restored_index_scope.py")
   preparatory_cfg=dict(official_ipsae=source["ipsae.py"],msa_roundtrip_source=source["control_msa_check.py"])
   with g.patched_core(preparatory_api,preparatory_scope,preparatory_cfg,entry):
    saved_raw={engine:dict(raw,**common_api.recompute_model(engine,raw,dict(target_sequence="AAA",binder_sequence=binder),self.target_toy,False,preparatory_scope.verify(source["ipsae.py"]).physical(),preparatory_scope.input,preparatory_scope.output(preparatory_scope.out/engine)))for engine,raw in raw_rows.items()}
   preparatory_scope.after()
  slots=lambda n:[dict(model=i)for i in range(n)]
  jobs=[dict(job_key=k,blind_id="SYNTHETIC_B0",target_id="T0",engine=k,variant="primary",slots=slots(n),expected_models=n,input=None)for k,n in(("boltz",3),("af2",5))]if nonempty else[]
  input_msa=self.file("common/input.a3m",(f"#3,{len(binder)}\t1,1\n>101\t102\nAAA{binder}\n>101\nAAA{'-'*len(binder)}\n>102\n---{binder}\n").encode())
  if nonempty:jobs[1]["input"]=input_msa
  inference=self.obj("common/plan.json",dict(jobs=jobs,entities=[dict(blind_id="SYNTHETIC_B0",target_sequence="AAA",binder_sequence=binder)]if nonempty else[],settings=dict(SYNTHETIC_SOFTWARE_ONLY=True)))
  analysis=self.obj("common/analysis.json",dict(inference_plan=inference,targets=[self.target_toy]if nonempty else[],native_recovery_controls=[]))
  membership=self.obj("common/membership.json",dict(inference_plan=inference,members=[dict(blind_id="SYNTHETIC_B0",target_id="T0",method_id="rf_diffusion",seed=17,cohort=cohort)for cohort in("uniform_all_complete","native_fixed_top_k")]if nonempty else[]))
  def summary(n):return dict(n_expected=n,n_observed=n,n_valid=0,n_missing=n,median=None,observed_only_median=None,q25=None,q75=None,IQR=None,min=None,max=None)
  rows=[];summaries=[]
  for job in jobs:
   models=[dict(slot=s,status="MODEL_UNRESOLVED",reason="SYNTHETIC_UNRESOLVED_NO_MODEL_INFERENCE",R0=None,R1=None)for s in job["slots"]]
   models[0]=dict(saved_raw[job["engine"]],slot=job["slots"][0])
   row=dict(job_key=job["job_key"],blind_id=job["blind_id"],engine=job["engine"],variant="primary",models=models,R0=common_api.summary([x["R0"]for x in models],job["expected_models"]),R1=common_api.summary([x["R1"]for x in models],job["expected_models"]),operational_pass=None,experimental_probability=None,experimental_blockade=False)
   if job["engine"]=="af2":
    row["worker_record"]=self.obj("common/worker/worker.json",dict(settings=dict(SYNTHETIC_SOFTWARE_ONLY=True)));self.obj("common/worker/af2/config.json",dict(model_type="alphafold2_multimer_v3",num_models=5,num_seeds=1,random_seed=31021,num_recycles=3,num_relax=0,use_templates=False));self.file("common/worker/af2/complex.a3m",Path(input_msa["path"]).read_bytes())
   rows.append(row)
   for cohort in("uniform_all_complete","native_fixed_top_k"):summaries.append(dict(target_id="T0",method_id="rf_diffusion",seed=17,cohort=cohort,engine=job["engine"],n_selected=1,n_R1_complete=0,R1_candidates=summary(1),R0_candidates=summary(1),model_coverage=dict(expected=job["expected_models"],valid=1),operational_pass=None))
  summaries.sort(key=lambda r:(r["target_id"],r["method_id"],r["seed"],r["cohort"],r["engine"]))
  result=self.obj("common/result.json",dict(plan=inference,analysis_plan=analysis,results=rows));producer=self.obj("common/producer.json",dict(cohort_summaries=summaries,n_jobs=len(jobs),n_models_expected=sum(j["expected_models"]for j in jobs)))
  stats=self.obj("statistics.json",dict(status="FROZEN_COMPLETE_DENOMINATOR_DESCRIPTIVE_STATISTICS_RECOMPUTED",n_arms=28,n_cohort_engine_rows=112,n_primary_targets=6,n_diagnostic_targets=1,n_empty_cohort_engine_rows=108 if nonempty else 112,n_missing_selected_outcome_rows=4 if nonempty else 0,inference_mode="descriptive_only"))
  common=dict(result=result["path"],analysis_plan=analysis["path"],membership=membership["path"],producer_acceptance=producer["path"],official_ipsae=source["ipsae.py"],msa_roundtrip_source=source["control_msa_check.py"],colabfold_cpu_python=str(m.R/"env/colabfold/bin/python"))
  config=self.obj("config.json",dict(resource_aliases=self.obj("aliases.json",dict(aliases=[],historical_unresolved=[])),recomputation=dict(generation=dict(auditor_source=source["budget.py"],plan=plan_r["path"],run_receipts=ledger["path"],sacct=scheduler["path"],producer_accounting=account_r["path"],producer_cohort=cohorts["path"]),common=common,statistics=dict(aggregation_policy="complete_selected_candidate_median_then_both_replicate_mean",producer_summary=stats["path"],rf_method_id="rf_diffusion",bindcraft_method_id="bindcraft"))))
  self.pkg=self.package(config);self.pkgr=self.control("full_package.json",self.pkg);self.marker=self.control_at(self.root/"RESTORE_HASH_ACCEPTANCE.json",dict(status="RESTORED_HASHES_VERIFIED_CONTENT_RECOMPUTATION_PENDING",package=self.pkgr))
  runtime=dict(schema=g.RUNTIME_SCHEMA,actual_common_cpu_python=common["colabfold_cpu_python"],runtimes=dict(core=g.runtime_descriptor(sys.executable),msa=g.runtime_descriptor(common["colabfold_cpu_python"])))
  return common,runtime
 def test_25_actual_whole_core_budget28_common_and_statistics112_empty(self):
  common,runtime=self.make_full(False);api=m.load("actual_empty_full_core",m.LIB/"restore_verify_v2.py");result,proof=g.run_indexed_core(api,self.pkgr,self.pkg,self.root,self.out,dict(aliases=[]),self.owned,runtime,m)
  self.assertEqual(result["status"],"INDEPENDENT_RESTORE_RAW_CONTENT_RECOMPUTATION_ACCEPTED");self.assertEqual(m.read(self.out/"budget_acceptance.json")["full_budget_comparable_tasks"],28);self.assertEqual(m.read(self.out/"target_statistics.json")["n_empty_cohort_engine_rows"],112);self.assertTrue(Path(proof["path"]).is_file())
 def test_26_actual_whole_core_nonempty_AF2_derived_protocol_and_roundtrip(self):
  common,runtime=self.make_full(True);self.assertEqual(self.target_toy["query_to_reference_indices"],{"1":1,"2":2,"3":3});self.assertTrue(Path(self.authority/"common/input.a3m").read_text().startswith("#3,65\t1,1\n"));api=m.load("actual_nonempty_full_core",m.LIB/"restore_verify_v2.py");result,proof=g.run_indexed_core(api,self.pkgr,self.pkg,self.root,self.out,dict(aliases=[]),self.owned,runtime,m)
  self.assertEqual(result["status"],"INDEPENDENT_RESTORE_RAW_CONTENT_RECOMPUTATION_ACCEPTED");accepted=m.read(self.out/"common/acceptance.json");self.assertEqual(accepted["n_AF2_actual_MSA_feature_roundtrips"],1);self.assertEqual(accepted["n_models_typed_unresolved"],6);self.assertEqual(accepted["n_models_recomputed_from_raw"],2);self.assertEqual(m.read(self.out/"target_statistics.json")["n_missing_selected_outcome_rows"],4)
  p=m.read(proof["path"]);self.assertTrue(any(x["kind"]=="EXPLICIT_INDEXED_MSA_SOURCE_LOADER"for x in p["subprocesses"]));self.assertTrue(any(x["logical_path"].endswith("af2/complex.a3m")for x in p["indexed_original_identities_read"]))
  self.assertEqual(sum(x["kind"]=="EXPLICIT_INDEXED_OFFICIAL_IPSAE_SOURCE_LOADER"for x in p["subprocesses"]),4)
  for process in p["subprocesses"]:
   if process["kind"]=="EXPLICIT_INDEXED_OFFICIAL_IPSAE_SOURCE_LOADER":
    life=m.read(m.verify(process["official_output_lifecycle"],True));self.assertEqual(life["status"],"EXACT_THREE_OFFICIAL_OUTPUT_WRITERS_CLOSED");self.assertEqual(len(life["writers"]),3);self.assertTrue(all(w["status"]in("FLUSHED_AND_CLOSED","ALREADY_CLOSED")for w in life["writers"]))
  identities={x["logical_path"]for x in p["indexed_original_identities_read"]}
  for suffix in("raw_toy/model.pdb","raw_toy/scores.json","raw_toy/confidence.json","raw_toy/pae_model.npz","raw_toy/plddt_model.npz","raw_toy/reference.pdb","source/ipsae.py","source/control_msa_check.py"):
   self.assertTrue(any(x.endswith(suffix)for x in identities),suffix)

 def test_27_whole_core_missing_AF2_MSA_even_live_poisoned_rejects_and_restores(self):
  common,runtime=self.make_full(True);self.pkg["manifest"]=[r for r in self.pkg["manifest"]if not r["relative"].endswith("common/worker/af2/complex.a3m")];self.pkgr=self.control("missing_full_package.json",self.pkg);self.marker=self.control_at(self.root/"RESTORE_HASH_ACCEPTANCE.json",dict(status="RESTORED_HASHES_VERIFIED_CONTENT_RECOMPUTATION_PENDING",package=self.pkgr));api=m.load("actual_full_core_missing_AF2",m.LIB/"restore_verify_v2.py");before=(api.Path,api.path_factory,api.read)
  with self.assertRaises(ValueError):g.run_indexed_core(api,self.pkgr,self.pkg,self.root,self.out,dict(aliases=[]),self.owned,runtime,m)
  self.assertEqual(before,(api.Path,api.path_factory,api.read));self.assertFalse((self.out/"acceptance.json").exists())
 def test_28_whole_core_wrong_protocol_config_rejected_without_source_rewrite(self):
  common,runtime=self.make_full(True);r=next(x for x in self.files if x["path"].endswith("common/worker/af2/config.json"));path=self.root/Path(r["path"]).relative_to(self.authority);before=path.read_bytes();path.chmod(0o644);path.write_text('{"num_models":99}');path.chmod(0o444);api=m.load("actual_full_core_config_drift",m.LIB/"restore_verify_v2.py");old=api.Path
  with self.assertRaises(ValueError):g.run_indexed_core(api,self.pkgr,self.pkg,self.root,self.out,dict(aliases=[]),self.owned,runtime,m)
  self.assertIs(api.Path,old);self.assertNotEqual(before,path.read_bytes());self.assertFalse((self.out/"acceptance.json").exists())

 def lifecycle_source(self,code):
  source=self.file("lifecycle/synthetic_source.py",code.encode());pkg=self.package(self.a);control=self.control("lifecycle_package.json",pkg)
  scope=g.StrictIndex(pkg,self.root,self.out,dict(aliases=[]),controls=[control,self.marker],owned=self.owned);scope.output(self.out).mkdir()
  model=scope.output(self.out/"model.pdb");model.write_bytes(b"SYNTHETIC_IO_ONLY_NO_SCORING")
  return scope,scope.verify(source),model
 def lifecycle_code(self,ending=""):
  return '\n'.join(['OUT=open(output_dir+"/model_10_15.txt","w")','PML=open(output_dir+"/model_10_15.pml","w")','OUT2=open(output_dir+"/model_10_15_byres.txt","w")','OUT.write("SYNTHETIC_BUFFER_CONTENT")','PML.write("SYNTHETIC_PML_CONTENT")','OUT2.write("SYNTHETIC_BYRES_CONTENT")',ending])
 def test_29_real_buffered_three_output_writers_and_readonly_proof(self):
  scope,source,model=self.lifecycle_source(self.lifecycle_code());ns=dict(output_dir=str(self.out));trace={}
  result=g.execute_indexed_official_source(source,scope,str(model),"10",ns,trace)
  self.assertEqual(result["status"],"EXACT_THREE_OFFICIAL_OUTPUT_WRITERS_CLOSED");self.assertEqual(len(result["writers"]),3)
  for name in("OUT","PML","OUT2"):self.assertTrue(ns[name].closed)
  self.assertEqual(scope.output(self.out/"model_10_15.txt").read_bytes(),b"SYNTHETIC_BUFFER_CONTENT")
  r=g.write_official_output_lifecycle(scope,str(model),"10",trace);p=Path(r["path"]);self.assertFalse(p.stat().st_mode&0o222);self.assertEqual(m.rec(p),r);self.assertEqual(json.loads(p.read_text())["status"],"EXACT_THREE_OFFICIAL_OUTPUT_WRITERS_CLOSED")
  scope.after()
 def test_30_closed_missing_wrong_type_name_and_output_scope_are_typed(self):
  import io
  scope=self.scope();scope.output(self.out).mkdir();paths=g.declare_official_output_paths(scope,self.out/"model.pdb","10");ns={k:p.open("w")for k,p in paths.items()}
  for handle in ns.values():handle.write("SYNTHETIC");handle.close()
  trace={};g.finalize_official_output_streams(ns,scope,paths,True,trace);self.assertTrue(all(r["status"]=="ALREADY_CLOSED"for r in trace["writers"]))
  for replacement in(None,io.StringIO(),(self.d/"outside.txt").open("w")):
   altered=dict(ns);altered["OUT"]=replacement
   with self.subTest(replacement=type(replacement).__name__),self.assertRaises(ValueError):g.finalize_official_output_streams(altered,scope,paths,True,{})
   if replacement is not None:self.assertFalse(replacement.closed);replacement.close()
  conflict=dict(paths,OUT=self.d/"outside.txt")
  with self.assertRaises(ValueError):g.finalize_official_output_streams(ns,scope,conflict,True,{})
  with self.assertRaises(ValueError):g.declare_official_output_paths(scope,self.d/"model.pdb","10")
 def test_31_actual_indexed_source_exception_closes_partial_valid_streams(self):
  code='OUT=open(output_dir+"/model_10_15.txt","w")\nOUT.write("SYNTHETIC_PARTIAL")\nraise original_error\n';scope,source,model=self.lifecycle_source(code);primary=RuntimeError("SYNTHETIC_PRIMARY_EXECUTION_ERROR");ns=dict(output_dir=str(self.out),original_error=primary);trace={}
  with self.assertRaises(RuntimeError)as observed:g.execute_indexed_official_source(source,scope,str(model),"10",ns,trace)
  self.assertIs(observed.exception,primary);self.assertTrue(ns["OUT"].closed);self.assertEqual(scope.output(self.out/"model_10_15.txt").read_bytes(),b"SYNTHETIC_PARTIAL");self.assertEqual(trace["status"],"CLEANUP_AFTER_SOURCE_EXCEPTION");self.assertEqual(trace["cleanup_errors"],[])
  self.assertTrue(any(r["status"]=="MISSING_AFTER_SOURCE_EXCEPTION"for r in trace["writers"]));scope.after()
 def test_32_flush_close_and_proof_write_failures_preserve_original_exception(self):
  import io
  class FaultWriter(io.TextIOBase):
   def __init__(self,real):self.real=real;self.close_attempted=False;self.fail=True
   @property
   def name(self):return self.real.name
   @property
   def mode(self):return self.real.mode
   @property
   def closed(self):return self.real.closed
   def fileno(self):return self.real.fileno()
   def flush(self):
    if self.fail:raise OSError("SYNTHETIC_FLUSH_FAILURE")
    return self.real.flush()
   def close(self):
    self.close_attempted=True;self.real.close()
    if self.fail:raise OSError("SYNTHETIC_CLOSE_FAILURE")
  code=self.lifecycle_code('OUT=FaultWriter(OUT)\nraise original_error');scope,source,model=self.lifecycle_source(code);primary=RuntimeError("SYNTHETIC_ORIGINAL_ERROR");ns=dict(output_dir=str(self.out),original_error=primary,FaultWriter=FaultWriter);trace={}
  with self.assertRaises(RuntimeError)as observed:g.execute_indexed_official_source(source,scope,str(model),"10",ns,trace)
  self.assertIs(observed.exception,primary);self.assertTrue(ns["OUT"].close_attempted);self.assertTrue(all(ns[k].closed for k in("OUT","PML","OUT2")));self.assertEqual(trace["status"],"OFFICIAL_OUTPUT_LIFECYCLE_REJECTED");self.assertEqual(len(primary.strict_official_output_cleanup_errors),2);ns["OUT"].fail=False
  life=scope.output(self.out/"strict_ipsae_IO_10.json");life.write_text("SYNTHETIC_EXISTING_EXCLUSIVE_PROOF")
  result=g.write_official_output_lifecycle(scope,str(model),"10",trace,primary);self.assertIsNone(result);self.assertEqual(primary.strict_official_output_proof_write_error["type"],"FileExistsError")
  with self.assertRaises(FileExistsError):g.write_official_output_lifecycle(scope,str(model),"10",trace)
  scope.after()
