"""Prepared CPU metadata/source contracts. No real queue query or scientific finish."""
import contextlib, copy, hashlib, json, os, subprocess, sys, tempfile, types, unittest
from pathlib import Path
from unittest import mock
import common_v5_owner_queue_finish_driver as m

class FakeBackend:
 def __init__(self,stdout="",stderr="",rc=0,error=None):
  self.calls=[];self.value=subprocess.CompletedProcess(m.OWNER_ARGV,rc,stdout=stdout,stderr=stderr);self.error=error;self.marker=object()
 def run(self,*args,**kwargs):
  self.calls.append((args,kwargs))
  if self.error:raise self.error
  return self.value
 def check_output(self,*args,**kwargs):return "SYNTHETIC_DELEGATED_CHECK_OUTPUT"

def cpurow(cpu="1",tres=None,**fields):
 d=dict(JobId="14700",JobName=m.JOB_NAME,UserId=m.USER+"(123)",Account=m.USER,Partition="organ",JobState="RUNNING",NumCPUs=cpu,MinMemoryNode="8G",TimeLimit="00:10:00")
 d.update(fields)
 return " ".join(k+"="+v for k,v in d.items())+" "+(tres if tres is not None else"TRES=cpu="+cpu+",node=1,billing="+cpu)

@contextlib.contextmanager
def source_toy(d):
 original=d/"reviewed";frozen=d/"frozen"
 for p in (original,frozen):
  p.mkdir()
  for i,n in enumerate(m.FILES):
   q=p/n;q.write_text("SYNTHETIC SOFTWARE SOURCE "+str(i)+"\n");q.chmod(0o444)
  p.chmod(0o555)
 try:yield original,frozen
 finally:
  for p in (original,frozen):p.chmod(0o755)

def receipt(n):return dict(path=str(m.OLD_D/n),bytes=1,sha256="a"*64)
def control_toy():
 source=dict(successor=[receipt(n) for n in m.COMMON_FILES])
 entry=source["successor"][0];launcher=source["successor"][4]
 pre=dict(status="COMMON_SUCCESSOR_CPU_PREFLIGHT_ACCEPTED_ROOT_PENDING_ONLY_GPU_SUBMISSION_REQUIRED",source=source,software_acceptance=m.COMMON_SW,root_pending_job_indices=m.PENDING,expected_jobs=288,expected_models=1124)
 sub=dict(schema="formal_common_root_submission.v1",array_job_id=m.ARRAY,preflight=m.PREFLIGHT,indices=m.PENDING,concurrency_cap=2,entry=entry,launcher=launcher,raw_sbatch_stdout="13423\n",raw_stdout="13423\n",raw_sbatch_stderr="",raw_stderr="")
 sub["submit_argv"]=["sbatch","--parsable","--export=ALL,COMMON_SUCCESSOR_ENTRY="+entry["path"],"--array="+",".join(map(str,m.PENDING))+"%2",launcher["path"],m.PREFLIGHT["path"]]
 cost=dict(schema="root_current_gpu_cost_closure.v1",status="ROOT_CURRENT_GPU_SUBMISSION_UNIVERSE_AND_TERMINAL_COST_CPU_ACCEPTED",software_acceptance=m.COST_SW,ledger=m.LEDGER,scope_start_utc="2026-10-11T14:25:00Z",scope_end_utc="2026-10-12T16:39:19Z",complete_root_gpu_submission_universe=True,allocated_failure_before_manifest_cost_retained=True,actual_current_scope_maximum_concurrent_GPUs=2,root_gpu_submission_receipts=[m.CONTROLLER],allocation=dict(job_id="14576",allocated_CPUs=1,allocated_GPUs=0),dispatches=[dict(phase="common_review",job_id=m.ARRAY,indices=m.PENDING,preflight=m.PREFLIGHT,launcher=launcher)],scientific_output_acceptance=False,new_GPU_submission=False,ACTIVE_changed=False)
 return source,pre,sub,cost
def new_sw_toy(source):
 flags=("all_owned_python_compile_PASS","all_launchers_bash_syntax_PASS","original_owned_pre_and_post_byte_readback_PASS","original_and_frozen_owned_byte_identities_equal","old_source_and_control_prepost_PASS","conditional_core_runtime_prepost_PASS")
 sw=dict(schema=m.SW_SCHEMA,status=m.SW_STATUS,source=source,entry=source[0],CPU_launcher=source[2],old_common_software=m.COMMON_SW,root_preflight=m.PREFLIGHT,current_controller=m.CONTROLLER,actual_full_cost=m.COST,**{k:True for k in flags})
 ct=dict(status="PASS",tests_run=32,failures=0,errors=0,skipped=0,tested_source=source)
 return sw,ct

class DriverContracts(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(dir=os.environ["TMPDIR"],prefix="common_queue_driver_SYNTHETIC_");self.d=Path(self.temp.name)
 def tearDown(self):self.temp.cleanup()
 def proof(self,stdout="200|RUNNING\n"):
  return m.observe_queue(self.d,FakeBackend(stdout))[0:2]
 def test01_empty_actual_owner_queue_derived_only(self):
  d=m.derive_queue("",0);self.assertEqual(d["target_rows"],[]);self.assertFalse(d["original_target_query_executed"]);self.assertEqual(d["original_request_role"],"INTERCEPTED_NOT_EXECUTED")
 def test02_other_and_nonprefix_ids_do_not_become_target(self):
  d=m.derive_queue("134230|RUNNING\n113423_2|PENDING\n13424_[0-9%2]|CONFIGURING\n",0)
  self.assertEqual(len(d["owner_rows"]),3);self.assertEqual(d["derived_stdout"],"")
 def test03_exact_parent_blocks_in_any_state(self):
  for state in ("PENDING","RUNNING","COMPLETING","CONFIGURING","SUSPENDED","COMPLETED","FAILED","CANCELLED"):
   with self.subTest(state=state),self.assertRaises(ValueError):m.derive_queue("13423|"+state+"\n",0)
 def test04_exact_task_blocks_in_any_state(self):
  for state in ("PENDING","RUNNING","COMPLETED","FAILED"):
   with self.subTest(state=state),self.assertRaises(ValueError):m.derive_queue("13423_0|"+state+"\n",0)
 def test05_compressed_range_and_throttle_block(self):
  for jid in ("13423_[0-267%2]","13423_[0,2-10,287%2]","13423_[287]"):
   with self.subTest(jid=jid),self.assertRaises(ValueError):m.derive_queue(jid+"|PENDING\n",0)
 def test06_duplicate_owner_logical_record_rejected(self):
  with self.assertRaisesRegex(ValueError,"Duplicate"):m.derive_queue("200_1|RUNNING\n200_1|RUNNING\n",0)
 def test07_malformed_scheduler_ids_rejected(self):
  for jid in ("0","00123","200.batch","200_-1","200_01","200_[4-1]","200_[1-4,3-5]","200_[1-4%0]","200_[x]","200_[]"):
   with self.subTest(jid=jid),self.assertRaises(ValueError):m.derive_queue(jid+"|RUNNING\n",0)
 def test08_malformed_blank_whitespace_or_extra_fields_rejected(self):
  for text in ("\n"," 200|RUNNING\n","200|RUNNING \n","200 RUNNING\n","200|RUNNING|x\n","200|running\n","200|\n"):
   with self.subTest(text=text),self.assertRaises(ValueError):m.derive_queue(text,0)
 def test09_actual_cpu_guard_dual_tres_and_production_envelope(self):
  self.assertEqual(m.select_cpu(cpurow(),"14700")["allocated_CPUs"],1)
  self.assertEqual(m.select_cpu(cpurow(tres="TRES=cpu=1,node=1 AllocTRES=node=1,cpu=1"),"14700")["allocated_TRES_fields"],["TRES","AllocTRES"])
  self.assertEqual(m.select_cpu(cpurow(cpu="2",MinMemoryNode="16G",TimeLimit="04:00:00"),"14700",True)["allocated_CPUs"],2)
  for row in (cpurow(tres=""),cpurow(tres="TRES=cpu=1,gres/gpu=1"),cpurow(tres="TRES=cpu=1,gres/gpu_bad=1"),cpurow(tres="TRES=cpu=1,gres/gpu:=0"),cpurow(tres="TRES=cpu=1,node=1 AllocTRES=cpu=1,node=2"),cpurow(JobName="other"),cpurow(JobState="PENDING"),cpurow(Account="other"),cpurow(tres="TRES=cpu=2"),cpurow()+" TRES=cpu=1"):
   with self.subTest(row=row),self.assertRaises(ValueError):m.select_cpu(row,"14700")
  with self.assertRaises(ValueError):m.select_cpu(cpurow(),"14700",True)
 def test10_nonzero_or_bool_rc_not_empty_queue_acceptance(self):
  for rc in (1,-1,None,True):
   with self.subTest(rc=rc),self.assertRaises(ValueError):m.derive_queue("",rc)
 def test11_real_readonly_query_and_derived_proof_saved_before_callback(self):
  backend=FakeBackend("200|RUNNING\n");r,d=m.observe_queue(self.d,backend)
  q=json.loads((self.d/"owner_queue.command.json").read_text());p=m.read(r)
  self.assertEqual(backend.calls[0][0],(m.OWNER_ARGV,));self.assertFalse(backend.calls[0][1]["check"]);self.assertEqual(q["returncode"],0)
  self.assertEqual(p["original_request"]["execution"],"INTERCEPTED_NOT_EXECUTED")
  self.assertEqual(p["old_finish_squeue_txt_role"],"DERIVED_TARGET_ONLY_NOT_ORIGINAL_SQUEUE_J_REPLY")
  self.assertTrue(all(not(x.stat().st_mode&0o222) for x in self.d.iterdir()))
 def test12_rc1_stdout_empty_stderr_preserved_not_accepted(self):
  with self.assertRaises(ValueError):m.observe_queue(self.d,FakeBackend("","literal query error",1))
  q=json.loads((self.d/"owner_queue.command.json").read_text())
  self.assertEqual(q["returncode"],1);self.assertEqual((self.d/"owner_queue.stderr").read_text(),"literal query error")
  self.assertFalse((self.d/"target_queue_proof.json").exists())
 def test13_timeout_partial_raw_and_exception_preserved(self):
  error=subprocess.TimeoutExpired(m.OWNER_ARGV,60,output=b"200|RUNNING\n",stderr=b"partial")
  with self.assertRaises(ValueError):m.observe_queue(self.d,FakeBackend(error=error))
  q=json.loads((self.d/"owner_queue.command.json").read_text())
  self.assertIsNone(q["returncode"]);self.assertEqual(q["exception"]["type"],"TimeoutExpired");self.assertEqual((self.d/"owner_queue.stdout").read_text(),"200|RUNNING\n")
  self.assertFalse((self.d/"target_queue_proof.json").exists())
 def test14_query_spawn_error_is_typed_no_derived_reply(self):
  with self.assertRaises(ValueError):m.observe_queue(self.d,FakeBackend(error=OSError("SYNTHETIC NO EXECUTABLE")))
  q=json.loads((self.d/"owner_queue.command.json").read_text());self.assertEqual(q["exception"]["type"],"OSError")
  self.assertFalse((self.d/"target_queue_proof.json").exists())
 def test15_proxy_exact_request_returns_labeled_empty_completedprocess(self):
  r,d=self.proof();backend=FakeBackend();p=m.QueueProxy(backend,r,d)
  result=p.run(list(m.TARGET_ARGV),**m.TARGET_KWARGS)
  self.assertIsInstance(result,subprocess.CompletedProcess);self.assertEqual(result.args,m.TARGET_ARGV);self.assertEqual((result.returncode,result.stdout,result.stderr),(0,"",""));self.assertEqual(backend.calls,[])
 def test16_proxy_wrong_exact_target_kwargs_rejected_without_delegate(self):
  r,d=self.proof();backend=FakeBackend();p=m.QueueProxy(backend,r,d)
  for kwargs in (dict(capture_output=True,text=True),dict(capture_output=1,text=True,check=True),dict(m.TARGET_KWARGS,timeout=60),dict(m.TARGET_KWARGS,shell=True)):
   with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):p.run(m.TARGET_ARGV,**kwargs)
  self.assertEqual(backend.calls,[])
 def test17_all_other_subprocess_calls_delegate_same_objects(self):
  r,d=self.proof();backend=FakeBackend();p=m.QueueProxy(backend,r,d)
  args=["sacct","-n","-P","-j","13423","--format=unchanged"];kwargs=dict(capture_output=True,text=True,check=True)
  value=p.run(args,**kwargs);self.assertIs(value,backend.value);self.assertIs(backend.calls[0][0][0],args);self.assertEqual(backend.calls[0][1],kwargs)
  self.assertEqual(p.check_output(["SYNTHETIC"]),backend.check_output(["SYNTHETIC"]));self.assertIs(p.marker,backend.marker)
 def test18_tuple_or_other_target_request_is_not_intercepted(self):
  r,d=self.proof();backend=FakeBackend();p=m.QueueProxy(backend,r,d)
  for args in (tuple(m.TARGET_ARGV),["squeue","-h","-j","134230"],["squeue","-h","-j","13423","-o","%i"]):
   self.assertIs(p.run(args,**m.TARGET_KWARGS),backend.value)
  self.assertEqual(p.calls,0);self.assertEqual(len(backend.calls),3)
 def test19_proof_content_byte_drift_rejected(self):
  for name in ("target_queue_proof.json","owner_queue.command.json","owner_queue.stdout"):
   directory=self.d/name.replace(".","_");directory.mkdir();r,d=m.observe_queue(directory,FakeBackend("200|RUNNING\n"))
   q=directory/name;q.chmod(0o664);q.write_text("{}\n");q.chmod(0o444)
   with self.subTest(file=name),self.assertRaises(ValueError):m.QueueProxy(FakeBackend(),r,d).run(m.TARGET_ARGV,**m.TARGET_KWARGS)
 def test20_second_target_interception_is_forbidden(self):
  r,d=self.proof();p=m.QueueProxy(FakeBackend(),r,d);p.run(m.TARGET_ARGV,**m.TARGET_KWARGS)
  with self.assertRaises(ValueError):p.run(m.TARGET_ARGV,**m.TARGET_KWARGS)
 def test21_module_local_proxy_restored_on_callback_failure(self):
  r,d=self.proof();backend=FakeBackend();p=m.QueueProxy(backend,r,d);events=[]
  def finish(args,out):
   module.subprocess.run(m.TARGET_ARGV,**m.TARGET_KWARGS);raise RuntimeError("SYNTHETIC NON SCIENTIFIC FAILURE")
  module=types.SimpleNamespace(subprocess=backend,finish=finish);original_global=m.subprocess
  with self.assertRaises(RuntimeError):m.with_old_finish(module,p,None,self.d,lambda e:events.append(type(e).__name__))
  self.assertIs(module.subprocess,backend);self.assertIs(m.subprocess,original_global);self.assertEqual(events,["RuntimeError"])
 def test22_module_local_success_keeps_stdlib_global_identity(self):
  r,d=self.proof();backend=FakeBackend();p=m.QueueProxy(backend,r,d)
  def finish(args,out):
   result=module.subprocess.run(m.TARGET_ARGV,**m.TARGET_KWARGS);(out/"synthetic_squeue.txt").write_text(result.stdout)
   return "SYNTHETIC NON SCIENTIFIC CALLBACK"
  module=types.SimpleNamespace(subprocess=backend,finish=finish);original_global=m.subprocess
  value=m.with_old_finish(module,p,None,self.d,lambda e:self.fail("unexpected"))
  self.assertEqual(value,"SYNTHETIC NON SCIENTIFIC CALLBACK");self.assertEqual((self.d/"synthetic_squeue.txt").read_text(),"")
  self.assertIs(module.subprocess,backend);self.assertIs(m.subprocess,original_global)
 def test23_old_module_identity_is_original_entry_not_copy(self):
  module=types.SimpleNamespace(__file__=str(m.OLD_ENTRY),SELF=m.OLD_ENTRY,D=m.OLD_D,FILES=m.COMMON_FILES,CORE=m.CORE)
  self.assertTrue(m.old_identity(module))
  for field,value in (("__file__",str(self.d/"common_review_successor.py")),("SELF",self.d/"common_review_successor.py"),("D",self.d),("FILES",m.COMMON_FILES[:-1]),("CORE",self.d/"python")):
   changed=copy.copy(module);setattr(changed,field,value)
   with self.subTest(field=field),self.assertRaises(ValueError):m.old_identity(changed)
 def test24_saved_old58_metadata_not_rerun_or_substituted(self):
  source=dict(successor=[receipt(n) for n in m.COMMON_FILES]);sw=dict(status="COMMON_SUCCESSOR_SOFTWARE_SOURCE_CPU_ACCEPTED_FUTURE_FORMAL_PREPARATION_PENDING",actual_CPU_job_id="13269",source=source,entry=source["successor"][0],CPU_launcher=source["successor"][3],GPU_launcher=source["successor"][4]);ct=dict(status="PASS",tests_run=58,failures=0,errors=0)
  m.old_contract(sw,ct,source)
  for key,value in (("tests_run",57),("tests_run",True),("failures",1),("errors",1)):
   changed=dict(ct);changed[key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):m.old_contract(sw,changed,source)
  changed=copy.deepcopy(sw);changed["source"]["successor"][0]["sha256"]="b"*64
  with self.assertRaises(ValueError):m.old_contract(changed,ct,source)
 def test25_root_metadata_controls_use_unchanged_old_submission_api(self):
  source,pre,sub,cost=control_toy();old=sys.modules["accepted_common_v5_ownerqueue"]
  self.assertEqual(m.control_semantics(old,source,pre,sub,cost),source["successor"][4])
 def test26_preflight_controller_and_fullcost_forks_rejected(self):
  source,pre,sub,cost=control_toy();old=sys.modules["accepted_common_v5_ownerqueue"]
  changes=(("pre","source",{}),("pre","expected_models",1123),("sub","array_job_id","13424"),("sub","indices",m.PENDING[:-1]),("sub","raw_sbatch_stdout","13424\n"),("cost","status","SOFTWARE ONLY"),("cost","complete_root_gpu_submission_universe",False),("cost","ledger",dict(m.LEDGER,sha256="b"*64)),("cost","scientific_output_acceptance",True))
  for obj,key,value in changes:
   a,b,c=copy.deepcopy(pre),copy.deepcopy(sub),copy.deepcopy(cost);{"pre":a,"sub":b,"cost":c}[obj][key]=value
   with self.subTest(obj=obj,key=key),self.assertRaises(ValueError):m.control_semantics(old,source,a,b,c)
 def test27_real_readonly_original_and_frozen_own4_bytes_match(self):
  with source_toy(self.d) as(a,b):
   x=m.reviewed(a);y=m.reviewed(b);self.assertTrue(m.source_binding(x,y,a,b));self.assertNotEqual(x[0]["path"],y[0]["path"])
 def test28_original_source_and_consumed_control_drift_rejected(self):
  with source_toy(self.d) as(a,b):
   x=m.reviewed(a);y=m.reviewed(b);q=a/m.FILES[0];q.chmod(0o664);q.write_text("SYNTHETIC ORIGINAL DRIFT\n");q.chmod(0o444)
   with self.assertRaises(ValueError):m.source_binding(x,y,a,b)
  q=self.d/"control.json";q.write_text("{}\n");q.chmod(0o444);r=m.record(q);table=[dict(receipt=r,metadata=m.metadata(q))]
  q.chmod(0o664);q.write_text('{"SYNTHETIC_CHANGED":true}\n');q.chmod(0o444)
  with self.assertRaises(ValueError):m.readback(table)
 def test29_frozen_source_byte_or_writable_source_rejected(self):
  with source_toy(self.d) as(a,b):
   x=m.reviewed(a);y=m.reviewed(b);q=b/m.FILES[1];q.chmod(0o664)
   with self.assertRaises(ValueError):m.source_binding(x,y,a,b)
   q.write_text("SYNTHETIC FROZEN DRIFT\n");q.chmod(0o444)
   with self.assertRaises(ValueError):m.source_binding(x,y,a,b)
 def test30_owned_universe_order_extra_and_symbolic_source_rejected(self):
  with source_toy(self.d) as(a,b):
   x=m.reviewed(a);y=m.reviewed(b)
   for changed in (x[:-1],list(reversed(x))):
    with self.assertRaises(ValueError):m.source_binding(changed,y,a,b)
   a.chmod(0o755);q=a/"UNDECLARED.py";q.write_text("SYNTHETIC\n");q.chmod(0o444);a.chmod(0o555)
   with self.assertRaises(ValueError):m.reviewed(a)
   a.chmod(0o755);q.unlink();leaf=a/m.FILES[0];leaf.unlink();leaf.symlink_to(b/m.FILES[0]);a.chmod(0o555)
   with self.assertRaises(ValueError):m.reviewed(a)
 def test31_new_driver32_software_count_flags_and_control_pins(self):
  source=[receipt(n) for n in m.FILES];sw,ct=new_sw_toy(source);self.assertTrue(m.driver_software_contract(sw,ct,source))
  for key,value in (("tests_run",58),("tests_run",True),("failures",1),("errors",1),("skipped",1),("errors",False)):
   changed=dict(ct);changed[key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):m.driver_software_contract(sw,changed,source)
  for key in ("all_owned_python_compile_PASS","original_owned_pre_and_post_byte_readback_PASS","old_source_and_control_prepost_PASS","conditional_core_runtime_prepost_PASS"):
   changed=dict(sw);changed[key]=False
   with self.subTest(flag=key),self.assertRaises(ValueError):m.driver_software_contract(changed,ct,source)
  for key,value in (("entry",source[1]),("CPU_launcher",source[3])):
   changed=dict(sw);changed[key]=value
   with self.subTest(binding=key),self.assertRaises(ValueError):m.driver_software_contract(changed,ct,source)
  changed=dict(sw);changed["actual_full_cost"]=dict(m.COST,sha256="b"*64)
  with self.assertRaises(ValueError):m.driver_software_contract(changed,ct,source)
 def test32_real_conditional_binary_bytes_and_link_prepost(self):
  binary=self.d/"python3.11";binary.write_bytes(b"SYNTHETIC CPU BINARY NOT EXECUTED");binary.chmod(0o755);logical=self.d/"python";logical.symlink_to("python3.11")
  expected=hashlib.sha256(binary.read_bytes()).hexdigest()
  with mock.patch.object(m,"CORE",logical),mock.patch.object(m,"CORE_REAL",binary),mock.patch.object(m,"CORE_BYTES",binary.stat().st_size),mock.patch.object(m,"CORE_SHA",expected):
   before=m.runtime_core(executable=logical);self.assertEqual(before,m.runtime_core(executable=logical))
   binary.write_bytes(b"SYNTHETIC CHANGED BINARY")
   with self.assertRaises(ValueError):m.runtime_core(executable=logical)
   binary.write_bytes(b"SYNTHETIC CPU BINARY NOT EXECUTED");logical.unlink();logical.symlink_to("wrong")
   with self.assertRaises(ValueError):m.runtime_core(executable=logical)

