"""Twenty bounded synthetic contracts; run only in the root CPU qualifier."""
import copy,json,os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
m=None
JID="90001"
def ctrl(**changes):
 fields=dict(JobId=JID,JobName="test9_default_scheduler_readiness_v1",JobState="RUNNING",UserId="u21111210118(6263900)",Account="u21111210118",Partition="organ",NumCPUs="1",TRES="cpu=1,mem=16G,node=1,billing=1")
 fields.update(changes);return" ".join(k+"="+v for k,v in fields.items())+"\n"
def acct(state="RUNNING",value="billing=1,cpu=1,node=1",user="u21111210118",account="u21111210118",partition="organ"):
 return"|".join([JID,state,value,user,account,partition])+"\n"
def query_record(**changes):
 result=dict(returncode=0,timed_out=False);result.update(changes);return result
def toy_sources(root):
 original=[];frozen=[];a=root/"original";b=root/"frozen";a.mkdir();b.mkdir()
 for name in m.OWN:
  for base,rows in((a,original),(b,frozen)):
   p=base/name;p.write_text("SYNTHETIC_WRAPPER_SOURCE_"+name+"\n");p.chmod(0o444);rows.append(m.rec(p))
 return original,frozen
class SchedulerContracts(unittest.TestCase):
 def test01_actual_controller_owner_cpu1_gpu0(self):
  row=m.scontrol_view(ctrl(),JID,m.SOFTWARE_JOB);self.assertEqual((row["state"],row["allocated_CPUs"],row["allocated_GPUs"]),("RUNNING",1,0))
 def test02_controller_identity_state_and_cpu_boundaries(self):
  for fields in(dict(JobId="999"),dict(JobName="wrong"),dict(JobState="PENDING"),dict(UserId="other(1)"),dict(Account="other"),dict(Partition="cell"),dict(NumCPUs="2")):
   with self.subTest(fields=fields),self.assertRaises(m.ReadinessError):m.scontrol_view(ctrl(**fields),JID,m.SOFTWARE_JOB)
 def test03_controller_gpu_and_duplicate_tokens_rejected(self):
  for raw in(ctrl(TRES="cpu=1,gres/gpu=0,gres/gpu:a100=1"),ctrl(TRES="cpu=1,cpu=1"),ctrl()+"JobId="+JID,ctrl().rstrip("\n")+" TRES=cpu=1\n",ctrl()+"\n"+ctrl()):
   with self.subTest(raw=raw),self.assertRaises(m.ReadinessError):m.scontrol_view(raw,JID,m.SOFTWARE_JOB)
 def test04_strict_numeric_and_unique_tres(self):
  self.assertEqual(m.tres("cpu=1,mem=16G,gres/gpu=0,gres/gpu:a100=0")[1:],(1,0))
  for value in("cpu=1,cpu=0","cpu=1.0","cpu=-1","cpu=true","cpu=1,gres/gpu:a100=x","cpu=1,gres/gpu_bad=0","cpu=1,gres/gpu:=0","cpu=1,broken","cpu=1,,node=1"):
   with self.subTest(value=value),self.assertRaises(m.ReadinessError):m.tres(value)
 def test05_original_six_columns_running_and_samejob_steps(self):
  raw=acct()+JID+".batch|RUNNING|cpu=1|u|a|p\n";row=m.accounting_view(raw,JID)
  self.assertTrue(row["ready"]);self.assertEqual(len(row["row"]),6);self.assertEqual(len(row["excluded"]),1)
 def test06_missing_partial_pending_only_wait_never_accept(self):
  for raw in("",acct("PENDING","",user="",account="",partition=""),acct(value="cpu=0"),acct(user=""),acct("CONFIGURING")):
   with self.subTest(raw=raw):self.assertFalse(m.accounting_view(raw,JID)["ready"])
 def test07_wrong_owner_and_column_truncation_refused(self):
  for raw in(acct(user="other"),acct(account="other"),acct(partition="cell"),JID+"|RUNNING|cpu=1\n"):
   with self.subTest(raw=raw),self.assertRaises(m.ReadinessError):m.accounting_view(raw,JID)
 def test08_duplicate_current_and_other_job_refused(self):
  for raw in(acct()+acct(),acct().replace(JID,"90002",1)):
   with self.subTest(raw=raw),self.assertRaises(m.ReadinessError):m.accounting_view(raw,JID)
 def test09_terminal_current_state_not_ready(self):
  for state in("COMPLETED","FAILED","CANCELLED","SUSPENDED","UNKNOWN"):
   with self.subTest(state=state),self.assertRaises(m.ReadinessError):m.accounting_view(acct(state),JID)
 def test10_gpu_duplicate_and_cpu_conflict_accounting_refused(self):
  for value in("cpu=1,gres/gpu=1","cpu=1,gres/gpu=0,gres/gpu:a100=1","cpu=1,gres/gpu=1,gres/gpu=0","cpu=2","cpu=abc"):
   with self.subTest(value=value),self.assertRaises(m.ReadinessError):m.accounting_view(acct(value=value),JID)
 def test11_bounded_empty_then_actual_ready_uses_original_argv(self):
  seen=[]
  def query(argv,label,attempt,timeout):
   seen.append((argv,label,attempt,timeout));return(ctrl()if label=="controller"else(""if attempt==0 else acct())),query_record()
  result=m.wait_ready(JID,m.SOFTWARE_JOB,query,clock=lambda:0,pause=lambda _:None)
  self.assertEqual(len(result["attempts"]),2);self.assertFalse(result["PENDING_accepted"]);self.assertEqual(seen[-1][0],m.sacct_argv(JID));self.assertEqual(m.FORMAT,"JobIDRaw,State,AllocTRES,User%64,Account%64,Partition%64")
 def test12_absolute_deadline_after_controller_not_accepted(self):
  now=[0]
  def query(argv,label,attempt,timeout):now[0]=2;return ctrl(),query_record()
  with self.assertRaisesRegex(m.ReadinessError,"timeout"):m.wait_ready(JID,m.SOFTWARE_JOB,query,clock=lambda:now[0],pause=lambda _:None,max_wait=1)
 def test13_attempt_limit_has_no_positive_status(self):
  calls=[]
  def query(argv,label,attempt,timeout):calls.append(label);return(ctrl()if label=="controller"else""),query_record()
  with self.assertRaisesRegex(m.ReadinessError,"attempt limit"):m.wait_ready(JID,m.SOFTWARE_JOB,query,clock=lambda:0,pause=lambda _:None,max_attempts=2)
  self.assertEqual(calls,["controller","accounting","controller","accounting"])
 def test14_wrong_accounting_owner_is_not_retried(self):
  calls=[]
  def query(argv,label,attempt,timeout):calls.append(label);return(ctrl()if label=="controller"else acct(user="other")),query_record()
  with self.assertRaises(m.ReadinessError):m.wait_ready(JID,m.SOFTWARE_JOB,query,clock=lambda:0,pause=lambda _:None)
  self.assertEqual(calls,["controller","accounting"])
 def test15_controller_pending_cannot_be_rescued_by_accounting(self):
  calls=[]
  def query(argv,label,attempt,timeout):calls.append(label);return ctrl(JobState="PENDING"),query_record()
  with self.assertRaises(m.ReadinessError):m.wait_ready(JID,m.SOFTWARE_JOB,query,clock=lambda:0,pause=lambda _:None)
  self.assertEqual(calls,["controller"])
 def test16_query_failure_and_timeout_capture_raw_readonly(self):
  with tempfile.TemporaryDirectory()as temp:
   base=Path(temp)
   with patch.object(m.subprocess,"run",return_value=subprocess.CompletedProcess(["sacct"],2,"RAW_FAILED_STDOUT","PERMISSION_ERROR")):
    _,record=m.run_query(["sacct"],base/"error")
   with self.assertRaises(m.ReadinessError):m.query_success(record)
   self.assertEqual(Path(record["stderr"]["path"]).read_text(),"PERMISSION_ERROR");self.assertEqual(Path(record["stdout"]["path"]).stat().st_mode&0o222,0)
   with patch.object(m.subprocess,"run",side_effect=subprocess.TimeoutExpired(["sacct"],1,output=b"PARTIAL",stderr=b"TIMEOUT")):
    _,record=m.run_query(["sacct"],base/"timeout",timeout=1)
   with self.assertRaises(m.ReadinessError):m.query_success(record)
   self.assertTrue(record["timed_out"]);self.assertEqual(Path(record["stdout"]["path"]).read_text(),"PARTIAL")
 def test17_executing_original_frozen_whole5_exact_then_drift(self):
  with tempfile.TemporaryDirectory()as temp:
   original,frozen=toy_sources(Path(temp));m.original_readback(original,frozen)
   p=Path(original[0]["path"]);p.chmod(0o644);p.write_text("ORIGINAL_DRIFT");p.chmod(0o444)
   with self.assertRaises(m.ReadinessError):m.original_readback(original,frozen)
 def test18_readonly_symlink_and_missing_input_authority(self):
  with tempfile.TemporaryDirectory()as temp:
   root=Path(temp);p=root/"a";p.write_text("EXACT");p.chmod(0o444);m.verify(m.rec(p))
   p.chmod(0o644)
   with self.assertRaises(m.ReadinessError):m.readonly(p)
   p.chmod(0o444);link=root/"link";link.symlink_to(p)
   with self.assertRaises(m.ReadinessError):m.readonly(link)
   with self.assertRaises(m.ReadinessError):m.readonly(root/"absent")
 def test19_qualified20_source_counts_compile_and_flags(self):
  with tempfile.TemporaryDirectory()as temp:
   originals,rows=toy_sources(Path(temp));a=dict(schema=m.SCHEMA,status=m.STATUS,source_files=rows,original_executing_sources=originals,original_and_frozen_pre_post_readback_PASS=True,software53_and84_retested=False,default_written=False,science_accepted=False,GPU_requested=False,ACTIVE_changed=False)
   c=dict(tested_source=rows,tests=20,status="PASS",errors=0,failures=0,skipped=0,compiled_all_owned_python=True,bash_syntax_PASS=True);m.software_contract(a,c,rows)
   for key,value in(("tests",19),("compiled_all_owned_python",False),("bash_syntax_PASS",False),("skipped",1),("tested_source",rows[:-1])):
    bad=copy.deepcopy(c);bad[key]=value
    with self.subTest(key=key),self.assertRaises(m.ReadinessError):m.software_contract(a,bad,rows)
   for key in("software53_and84_retested","default_written","science_accepted","GPU_requested","ACTIVE_changed"):
    bad=copy.deepcopy(a);bad[key]=True
    with self.subTest(key=key),self.assertRaises(m.ReadinessError):m.software_contract(bad,c,rows)
 def test20_original_cpu_probe_and_terminal_numeric_binding(self):
  row=dict(job_id=JID,scheduler_record=acct(),numeric_sacct_row=acct().rstrip("\n").split("|"),allocated_CPUs=1,allocated_gpus=0);m.probe_contract(row,JID)
  for key,value in(("job_id","90002"),("allocated_gpus",1),("scheduler_record",acct(user="other")),("numeric_sacct_row",[])):
   bad=copy.deepcopy(row);bad[key]=value
   with self.subTest(key=key),self.assertRaises(m.ReadinessError):m.probe_contract(bad,JID)
  raw=JID+"|COMPLETED|0:0|1|cpu=1,node=1|u21111210118|u21111210118|"+m.SOFTWARE_JOB+"|organ\n";m.terminal_view(raw,JID,m.SOFTWARE_JOB)
  for bad in(raw.replace("COMPLETED","RUNNING"),raw.replace("cpu=1","cpu=1,gres/gpu=0,gres/gpu:a100=1"),raw+raw,raw.replace("0:0","1:0")):
   with self.subTest(raw=bad),self.assertRaises(m.ReadinessError):m.terminal_view(bad,JID,m.SOFTWARE_JOB)
