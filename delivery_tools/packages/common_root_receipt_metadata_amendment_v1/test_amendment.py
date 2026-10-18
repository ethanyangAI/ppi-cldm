#!/usr/bin/env python3
"""Twenty owned CPU metadata guards. Never invokes the76/58 suites or GPU APIs."""
import copy,json,os,tempfile,unittest
from pathlib import Path
AMEND=None
CONTEXT=None
class MetadataGuards(unittest.TestCase):
 def setUp(self):self.m=AMEND;self.c=CONTEXT;self.old=copy.deepcopy(self.c["old"]);self.new=copy.deepcopy(self.c["new"])
 def unchanged_guard(self,fn):
  with tempfile.TemporaryDirectory(prefix="common_amendment_fixture_",dir=self.m.S/"tmp")as d:
   p=Path(d)/"untouched.json";b=b'{"SYNTHETIC_METADATA_ONLY":true}\n';p.write_bytes(b);p.chmod(0o444)
   with self.assertRaises(ValueError):fn()
   self.assertEqual(p.read_bytes(),b);self.assertEqual(p.stat().st_mode&0o777,0o444)
 def toy(self):
  t=tempfile.TemporaryDirectory(prefix="common_amendment_fixture_",dir=self.m.S/"tmp");root=Path(t.name);claim=root/"claim";claim.mkdir()
  p=claim/"root_submission.json";p.write_bytes(self.m.encode(self.old));p.chmod(0o444)
  other=claim/"untouched.txt";other.write_bytes(b"SYNTHETIC_ONLY_UNCHANGED\n");other.chmod(0o444);claim.chmod(0o555)
  def clean():claim.chmod(0o700);t.cleanup()
  self.addCleanup(clean);return root,p,other
 def test_01_addition_only_positive(self):
  n=self.m.proposal(self.old);self.assertEqual(set(n)-set(self.old),set(self.m.EXTRA_KEYS));self.assertEqual({k:n[k]for k in self.old},self.old)
 def test_02_wrong_original_stdout_no_mutation(self):
  self.old["raw_stdout"]="99999\n";self.unchanged_guard(lambda:self.m.old_shape(self.old,self.c["fact"],self.c["ctx"]["pre"]))
 def test_03_nonempty_original_stderr_no_mutation(self):
  self.old["raw_stderr"]="submission error";self.unchanged_guard(lambda:self.m.old_shape(self.old,self.c["fact"],self.c["ctx"]["pre"]))
 def test_04_wrong_root_job_no_mutation(self):
  self.old["array_job_id"]="13424";self.unchanged_guard(lambda:self.m.old_shape(self.old,self.c["fact"],self.c["ctx"]["pre"]))
 def test_05_actual_argv_fork_no_mutation(self):
  fact=copy.deepcopy(self.c["fact"]);fact["argv"].append("--gres=gpu:2");self.unchanged_guard(lambda:self.m.old_shape(self.old,fact,self.c["ctx"]["pre"]))
 def test_06_existing_field_mutation_rejected(self):
  self.new["concurrency_cap"]=1;self.unchanged_guard(lambda:self.m.addition_only(self.old,self.new))
  self.new=copy.deepcopy(self.c["new"]);self.new["concurrency_cap"]=2.0;self.unchanged_guard(lambda:self.m.addition_only(self.old,self.new))
 def test_07_extra_field_rejected(self):
  self.new["technical_rerun"]=True;self.unchanged_guard(lambda:self.m.addition_only(self.old,self.new))
 def test_08_missing_alias_rejected(self):
  self.new.pop("raw_sbatch_stderr");self.unchanged_guard(lambda:self.m.addition_only(self.old,self.new))
 def test_09_alias_raw_fork_rejected(self):
  self.new["raw_sbatch_stdout"]="13423";self.unchanged_guard(lambda:self.m.addition_only(self.old,self.new))
 def test_10_stale_readonly_source_bytes_rejected(self):
  with tempfile.TemporaryDirectory(prefix="common_amendment_fixture_",dir=self.m.S/"tmp")as d:
   p=Path(d)/"source.py";p.write_bytes(b"# SYNTHETIC metadata guard\n");p.chmod(0o444);r=self.m.receipt(p);self.m.exact(r)
   p.chmod(0o600);p.write_bytes(b"# DIFFERENT readonly source\n");p.chmod(0o444)
   with self.assertRaisesRegex(ValueError,"byte drift"):self.m.exact(r)
 def test_11_actual_old_Common_PASS_COST_expected_rejection(self):
  c=self.c["ctx"];self.assertEqual(c["common"].submission_contract(self.old,self.m.PREFLIGHT,c["pre"])[0],"13423")
  with self.assertRaisesRegex(ValueError,"^Actual raw parsable submission differs/missing$"):self.m.contracts(c,self.old)
 def test_12_actual_proposal_both_frozen_APIs_PASS(self):
  p=self.m.contracts(self.c["ctx"],self.new);self.assertEqual(p["cost"]["job_id"],"13423");self.assertEqual(p["cost"]["expected_allocation_count"],268);self.assertEqual(p["common"]["job_id"],"13423")
 def test_13_exact_preflight_pointer_fork_rejected(self):
  self.new["preflight"]=dict(self.m.PREFLIGHT,path=str(self.m.S/"tmp/nonexistent_preflight.json"));self.unchanged_guard(lambda:self.m.contracts(self.c["ctx"],self.new))
 def test_14_pending_indices_fork_rejected(self):
  self.new["indices"]=self.new["indices"][:-1];self.unchanged_guard(lambda:self.m.contracts(self.c["ctx"],self.new))
 def test_15_source_entry_fork_rejected(self):
  self.new["entry"]=dict(self.new["entry"],sha256="0"*64);self.unchanged_guard(lambda:self.m.contracts(self.c["ctx"],self.new))
 def test_16_actual_CPU_TRES_boundaries(self):
  m=self.m
  text="JobId=999 JobState=RUNNING UserId="+m.USER+"(6263900) Account="+m.USER+" Partition=organ NumCPUs=1 TRES=cpu=1,node=1,billing=1"
  self.assertEqual(m.live_record(text,"999")["allocated_GPUs"],0);self.assertEqual(m.live_record(text+" AllocTRES=cpu=1,node=1,billing=1","999")["allocated_CPUs"],1)
  for tail in [" AllocTRES=cpu=1,node=1,billing=1,gres/gpu=1"," AllocTRES=cpu=2,node=1,billing=1"]:
   with self.subTest(tail=tail),self.assertRaises(ValueError):m.live_record(text+tail,"999")
  for t in ["cpu=1,cpu=1","cpu=1,gres/gpu=0,gres/gpu:a100=1","cpu=1,gres/gpu=0.0","cpu=1,gres/gpu_bad=0","cpu=1,gres/gpu:=0","node=1","cpu=0"]:
   with self.subTest(tres=t),self.assertRaises(ValueError):m.allocation_values(t)
  for field in ["JobId=999","NumCPUs=1","TRES=cpu=1,node=1,billing=1","Account="+m.USER]:
   with self.subTest(duplicate=field),self.assertRaisesRegex(ValueError,"Duplicate relevant"):m.live_record(text+" "+field,"999")
  named=text+" JobName="+m.OWN_JOB_NAME;self.assertEqual(m.live_record(named,"999",m.OWN_JOB_NAME)["job_id"],"999")
  with self.assertRaisesRegex(ValueError,"named CPU"):m.live_record(text+" JobName=wrong_name","999",m.OWN_JOB_NAME)
  with self.assertRaisesRegex(ValueError,"Duplicate relevant"):m.live_record(named+" JobName="+m.OWN_JOB_NAME,"999",m.OWN_JOB_NAME)
  for jid,name,cpus in [("13277","ppi_root_gpu_cost_cpu",1),("13269","ppi_common_successor_cpu",2)]:
   row="|".join([jid,name,m.USER,m.USER,"organ","COMPLETED","0:0","4","cpu="+str(cpus)+",node=1,billing="+str(cpus)])
   self.assertEqual(m.terminal_row(row,jid,cpus)["job_name"],name)
   with self.assertRaisesRegex(ValueError,"producer terminal"):m.terminal_row(row.replace("|"+name+"|","|wrong_job_name|"),jid,cpus)
 def test_17_atomic_positive_ONLY_add2_parent_restored(self):
  root,p,other=self.toy();before=other.read_bytes();old=p.read_bytes();new=self.m.encode(self.new)
  result=self.m.atomic_amend(p,old,new,lambda target:self.m.addition_only(self.old,json.loads(self.m.data(target))),"901",fixture_root=root)
  self.assertTrue(result["committed"]);self.assertTrue(result["parent_mode_restored"]);self.assertFalse(result["rollback_performed"]);self.assertEqual(p.read_bytes(),new);self.assertEqual(p.parent.stat().st_mode&0o777,0o555);self.assertEqual(other.read_bytes(),before)
  self.assertEqual(set(x.name for x in p.parent.iterdir()),{"root_submission.json","untouched.txt"})
 def test_18_precommit_failure_no_canonical_mutation(self):
  root,p,other=self.toy();old=p.read_bytes();flag=[];parent_before=self.m.metadata(p.parent)
  def before():raise ValueError("SYNTHETIC source precommit drift")
  with self.assertRaisesRegex(ValueError,"source precommit drift"):self.m.atomic_amend(p,old,self.m.encode(self.new),lambda p:flag.append(True),"902",fixture_root=root,precommit=before)
  self.assertEqual(p.read_bytes(),old);self.assertFalse(flag);self.assertEqual(self.m.metadata(p.parent),parent_before);self.assertEqual(p.parent.stat().st_mode&0o777,0o555);self.assertEqual(other.read_bytes(),b"SYNTHETIC_ONLY_UNCHANGED\n")
 def test_19_postcheck_failure_rollback_preserves_primary(self):
  root,p,other=self.toy();old=p.read_bytes();primary=ValueError("SYNTHETIC postcheck failure")
  def after(p):raise primary
  try:self.m.atomic_amend(p,old,self.m.encode(self.new),after,"903",fixture_root=root)
  except ValueError as exc:self.assertIs(exc,primary);self.assertTrue(exc.amendment_transaction["rollback_performed"]);self.assertFalse(exc.amendment_transaction["rollback_conflict"])
  else:self.fail("Postcheck failure must propagate")
  self.assertEqual(p.read_bytes(),old);self.assertEqual(p.parent.stat().st_mode&0o777,0o555);self.assertEqual(other.read_bytes(),b"SYNTHETIC_ONLY_UNCHANGED\n")
  root2,p2,other2=self.toy();old2=p2.read_bytes();original_metadata=self.m.metadata;parent_reads=[]
  def synthetic_cleanup_metadata_fault(path):
   result=original_metadata(path)
   if Path(path)==p2.parent:
    parent_reads.append(True)
    if len(parent_reads)==2:result=dict(result,mode=0o777)
   return result
  self.m.metadata=synthetic_cleanup_metadata_fault
  try:
   with self.assertRaisesRegex(RuntimeError,"Transaction cleanup failed")as failure:self.m.atomic_amend(p2,old2,self.m.encode(self.new),lambda p:None,"905",fixture_root=root2)
   self.assertTrue(failure.exception.amendment_transaction["committed"]);self.assertTrue(failure.exception.amendment_transaction["cleanup_errors"])
  finally:self.m.metadata=original_metadata
  self.assertEqual(p2.parent.stat().st_mode&0o777,0o555);self.assertEqual(other2.read_bytes(),b"SYNTHETIC_ONLY_UNCHANGED\n")
 def test_20_rollback_cannot_clobber_external_replacement(self):
  root,p,other=self.toy();old=p.read_bytes();new=self.m.encode(self.new);primary=ValueError("SYNTHETIC external concurrent replacement")
  def after(target):
   q=target.parent/"external_replacement.json";q.write_bytes(new);q.chmod(0o444);os.replace(q,target);raise primary
  try:self.m.atomic_amend(p,old,new,after,"904",fixture_root=root)
  except ValueError as exc:self.assertIs(exc,primary);self.assertFalse(exc.amendment_transaction["rollback_performed"]);self.assertTrue(exc.amendment_transaction["rollback_conflict"])
  else:self.fail("Unknown replacement cannot be silently rolled back")
  self.assertEqual(p.read_bytes(),new);self.assertEqual(p.parent.stat().st_mode&0o777,0o555);self.assertEqual(other.read_bytes(),b"SYNTHETIC_ONLY_UNCHANGED\n")

  root2,p2,other2=self.toy();old2=p2.read_bytes();new2=self.m.encode(self.new)
  result=self.m.atomic_amend(p2,old2,new2,lambda p:None,"906",fixture_root=root2);self.m.committed_guard(p2,new2,result)
  foreign=(json.dumps(self.new,separators=(",",":"))+"\n").encode();self.assertNotEqual(foreign,new2)
  p2.chmod(0o600);p2.write_bytes(foreign);p2.chmod(0o444)
  with self.assertRaisesRegex(ValueError,"Unknown current canonical"):self.m.committed_guard(p2,new2,result)
  self.assertEqual(p2.read_bytes(),foreign)
  p2.parent.chmod(0o755);replacement=p2.parent/"foreign_same_bytes.json";replacement.write_bytes(new2);replacement.chmod(0o444);os.replace(replacement,p2);p2.parent.chmod(0o555)
  with self.assertRaisesRegex(ValueError,"Unknown current canonical"):self.m.committed_guard(p2,new2,result)
  self.assertEqual(p2.read_bytes(),new2);self.assertEqual(other2.read_bytes(),b"SYNTHETIC_ONLY_UNCHANGED\n")
