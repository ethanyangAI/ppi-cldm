#!/usr/bin/env python3
"""CPU software fixtures, never scientific predictions."""
import copy,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import formal_postprocess_v2 as p
def plan28():
 return {"tasks":[dict(task_id="task%02d"%i,array_index=i,target_id="target"+str(i//4),method_id="rf_diffusion"if i%2==0 else"bindcraft",seed=21011+(i//2)%2)for i in range(28)]}
class Contracts(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=p.R/"steps/24_benchmark_delivery/tmp");self.root=Path(self.tmp.name);self.plan=plan28();self.pr=dict(path="/fixture/plan",sha256="a"*64,bytes=1)
 def tearDown(self):self.tmp.cleanup()
 def receipt(self,i,raw=None,plan=None,logical=None):
  path=self.root/("70000_"+str(i))/"run_receipt.json";path.parent.mkdir(parents=True,exist_ok=True)
  p.dump(path,dict(plan=plan or self.pr,task=self.plan["tasks"][i],logical_allocation_key=logical or "70000_"+str(i),raw_allocation_id=str(raw or 70001+i),status="EARLY_ENGINEERING_FAILURE"));return path
 def discover(self):return p.discover_receipts(self.plan,self.pr,"70000",self.root)
 def test_all28_missing_retained_not_empty_observations(self):
  slots,rs=self.discover();self.assertEqual((len(slots),rs),(28,[]));self.assertTrue(all(s["status"]=="RUN_RECEIPT_UNAVAILABLE"and "Unresolved"in s["meaning"]for s in slots))
 def test_present_slot_and_missing_denominators(self):
  self.receipt(11);slots,rs=self.discover();self.assertEqual((len(slots),len(rs),slots[11]["task"]["array_index"]),(28,1,11))
 def test_nonnumeric_array_rejected(self):
  for x in ["7_0","7; echo bad","a",""]:
   with self.assertRaises(ValueError):p.expected_slots(self.plan,x,self.root)
 def test_duplicate_tasks_rejected(self):
  self.plan["tasks"][1]["task_id"]=self.plan["tasks"][0]["task_id"]
  with self.assertRaises(ValueError):p.expected_slots(self.plan,"7",self.root)
 def test_shuffled_slots_rejected(self):
  self.plan["tasks"][0],self.plan["tasks"][1]=self.plan["tasks"][1],self.plan["tasks"][0]
  with self.assertRaises(ValueError):p.expected_slots(self.plan,"7",self.root)
 def test_wrong_plan_rejected(self):
  self.receipt(0,plan=dict(self.pr,sha256="b"*64))
  with self.assertRaisesRegex(ValueError,"plan/task"):self.discover()
 def test_wrong_alias_rejected(self):
  self.receipt(0,logical="70000_1")
  with self.assertRaisesRegex(ValueError,"logical"):self.discover()
 def test_duplicate_physical_id_rejected(self):
  self.receipt(0,raw=70100);self.receipt(1,raw=70100)
  with self.assertRaisesRegex(ValueError,"physical"):self.discover()
 def test_extra_slot_receipt_rejected(self):
  d=self.root/"70000_99";d.mkdir();p.dump(d/"run_receipt.json",{})
  with self.assertRaisesRegex(ValueError,"Unexpected"):self.discover()
 def test_positive_unjoined_cost_rejected(self):
  with self.assertRaisesRegex(ValueError,"Positive"):p.check_allocation_joins({"71":{"gpu_count":1,"elapsed_seconds":1}},[])
 def test_zero_cost_cancellation_not_sequence_pool(self):
  x=p.check_allocation_joins({"71":{"gpu_count":0,"elapsed_seconds":0}},[])
  self.assertEqual(x["zero_cost_unjoined_rows"],["71"]);self.assertTrue(x["missing_receipts_do_not_mean_zero_sequences"])
 def test_duplicate_receipts_not_doublecounted(self):
  r=p.rec(self.receipt(0,raw=71))
  with self.assertRaisesRegex(ValueError,"Duplicate"):p.check_allocation_joins({"71":{"gpu_count":1,"elapsed_seconds":1}},[r,r])
 def test_missing_scheduler_record_rejected(self):
  r=p.rec(self.receipt(0,raw=71))
  with self.assertRaisesRegex(ValueError,"absent"):p.check_allocation_joins({},[r])
 def test_frozen_parser_excludes_steps(self):
  b=p.module("budget");text="71|60|gres/gpu=1|COMPLETED|start|end|n|organ\n71.batch|60|gres/gpu=1|COMPLETED|start|end|n|organ\n"
  rows,excluded=b.parse_sacct(text);self.assertEqual(set(rows),{"71"});self.assertEqual(len(excluded),1)
 def test_native_partial_tail_retained(self):
  path=self.root/"stream.jsonl";path.write_bytes(b'{"x":1}\n{"unfinished":')
  rows,m=p.module("native").stream(path);self.assertEqual(rows,[{"x":1}]);self.assertEqual(m["complete_lines"],1);self.assertEqual(m["partial_tail_bytes"],14)
 def test_native_absent_stream_explicit(self):
  rows,m=p.module("native").stream(self.root/"missing");self.assertEqual(rows,[]);self.assertFalse(m["present"])
 def test_frozen_empty_cohorts_preserve28_and_fixedK(self):
  b=p.module("budget");pl=copy.deepcopy(self.plan);pl["protocol"]=dict(sampling=dict(salt="fixture",uniform_n_per_replicate=3,native_top_k_per_replicate=2),methods=[dict(method_id=m,native_score_name="fixture",native_score_direction="higher")for m in ["rf_diffusion","bindcraft"]]);pl["protocol_receipt"]=self.pr
  x=b.cohorts(pl,[],[]);self.assertEqual((len(x["coverage"]),x["selected"]),(28,[]))
  self.assertTrue(all(c["uniform_all_complete"]["requested"]==3 and c["native_fixed_top_k"]["requested"]==2 and c["comparison_status"]=="UNRESOLVED_NO_ACCEPTED_FULL_BUDGET"for c in x["coverage"]))
 def test_empty_membership_exact_coverage(self):
  c={"selected":[],"coverage":[dict(task_id=i)for i in range(28)]};m={"members":[],"coverage":copy.deepcopy(c["coverage"])}
  self.assertEqual(p.exact_membership(c,m)["fixed_task_coverage"],28)
 def test_nativeNA_and_rejection_unchanged(self):
  row=dict(cohort_record_id="one",native_score=None,internal_acceptance_values=["False","None"],sequence_sha256="x")
  c={"selected":[row],"coverage":[]};m={"members":[dict(row,blind_id="blind_fixture")],"coverage":[]}
  self.assertEqual(p.exact_membership(c,m)["selected_members"],1);m["members"][0]["native_score"]=0
  with self.assertRaisesRegex(ValueError,"altered"):p.exact_membership(c,m)
 def test_duplicate_membership_rejected(self):
  row=dict(cohort_record_id="x")
  with self.assertRaisesRegex(ValueError,"Duplicate"):p.exact_membership({"selected":[row],"coverage":[]},{"members":[row,row],"coverage":[]})
 def test_dropped_unresolved_coverage_rejected(self):
  with self.assertRaisesRegex(ValueError,"coverage"):p.exact_membership({"selected":[],"coverage":[{}]},{"members":[],"coverage":[]})
 def test_hash_change_rejected(self):
  f=self.root/"data";f.write_text("before");r=p.rec(f);f.write_text("after")
  with self.assertRaises(ValueError):p.verify(r)
 def test_no_output_overwrite(self):
  f=self.root/"out.json";p.dump(f,{"original":True})
  with self.assertRaises(FileExistsError):p.dump(f,{"original":False})
  self.assertEqual(p.read(f),{"original":True})
 def test_every_attempt_state_and_continue_after_one_failure(self):
  for fail_first in [False,True]:
   out=self.root/("audit_"+str(fail_first));out.mkdir();task=dict(task_id="task",method_id="rf_diffusion",target_id="target",seed=21011)
   rrpath=out/"run_receipt.json";p.dump(rrpath,dict(task=task));rr=p.rec(rrpath)
   pl={"protocol":{"methods":[dict(method_id="rf_diffusion",adapter_receipts=[{"path":"runtime"}],config_receipt={"path":"config","sha256":"x"})],"targets":[{"target_id":"target","input_manifest":{"path":"target"}}]}}
   attempts=[dict(attempt_index=i,status=s)for i,s in enumerate(["SCIENTIFIC_REJECT","TIMED_OUT_BOUNDARY","ENGINEERING_FAILURE"])];seen=[]
   class Formal:
    @staticmethod
    def raw_closure(*a):return {"n_attempts":3}
    @staticmethod
    def native_output_closure(*a):return {"n_attempts":3}
   def runner(argv,stem):
    i=int(Path(argv[argv.index("--attempt-dir")+1]).name);seen.append(i)
    if fail_first and i==0:raise RuntimeError("fixture interruption")
    dest=Path(argv[argv.index("--output-dir")+1]);dest.mkdir();p.dump(dest/"acceptance.json",{"no_new_predictions":True})
   with patch.object(p,"module",return_value=Formal),patch.object(p,"pin",return_value={"path":"collector"}),patch.object(p,"verify",side_effect=lambda r:Path(r["path"])),patch.object(p,"read_run_ledgers",return_value=(attempts,[],[])),patch.object(p,"run_cpu",side_effect=runner):
    if fail_first:
     with self.assertRaisesRegex(ValueError,"unresolved"):p.audit_attempts(pl,self.pr,[rr],out)
     self.assertFalse((out/"native_audits.json").exists())
    else:self.assertEqual(len(p.audit_attempts(pl,self.pr,[rr],out)["attempts"]),3)
   self.assertEqual(seen,[0,1,2])

 def phase_fixture(self,hard="M"*65,physical="M"*65,mpnn=False,tail=False):
  task=dict(task_id="fixturetask",method_id="bindcraft",target_id="target",seed=21011);attempt=dict(attempt_index=0,status="SCIENTIFIC_REJECT")
  run=dict(task=task);rr=dict(path=str(self.root/"slot"/"run_receipt.json"));folder=Path(rr["path"]).parent/"attempts"/"000000";folder.mkdir(parents=True)
  design="attempt_l65_s1";pdb=folder/"generated"/"Trajectory"/"Clashing"/(design+".pdb");pdb.parent.mkdir(parents=True)
  names={v:k for k,v in p.AA3.items()};lines=[]
  for chain,seq in [("A","AAAA"),("B",physical)]:
   for i,aa in enumerate(seq,1):lines.append("ATOM  %5d  CA  %3s %s%4d    %8.3f%8.3f%8.3f  1.00 50.00           C"%(len(lines)+1,names[aa],chain,i,float(i),0.,0.))
  pdb.write_text("\n".join(lines)+"\n")
  native=[dict(event="trajectory_started",design=design,length=65,seed=1),dict(event="trajectory_complete",design=design,sequence=hard,native_termination="Clashing")]
  proposals=[]
  if mpnn:
   native.append(dict(event="mpnn_raw_batch_complete",n=1,source_pdb=str(pdb)))
   proposals=[dict(attempt_index=0,lineage_id="fixturetask/attempt_0/trajectory",sequence_record_id="record1",sequence="A"*65,internal_acceptance=None,native_score=None,observed_before_generation_cutoff=True)]
   (folder/"sequences.jsonl").write_text("".join(json.dumps(x)+"\n"for x in proposals))
  (folder/"bindcraft_native_events.jsonl").write_text("".join(json.dumps(x)+"\n"for x in native)+('{"partial":'if tail else""))
  return rr,run,attempt,proposals,[],dict(target_sequence="AAAA"),folder
 def phase(self,f):return p.phase_attempt(*f[:6])
 def test_complete_optimized_rejection_is_not_zero_designs(self):
  f=self.phase_fixture();x=self.phase(f);self.assertEqual(x["phase_counts"]["trajectory_complete"],1);self.assertEqual(x["phase_counts"]["raw_complete_mpnn_proposals"],0)
  self.assertEqual(x["trajectories"][0]["native_termination"],"Clashing");self.assertEqual(x["trajectories"][0]["hard_sequence"]["sequence"],"M"*65);self.assertEqual(x["trajectories"][0]["physical_exports"][0]["hard_vs_physical"]["status"],"IDENTICAL")
  self.assertEqual(x["normalized_mpnn_proposals"],[]);self.assertTrue(x["primary_cohort_unchanged"])
 def test_hard_physical_difference_retained_not_rewritten(self):
  f=self.phase_fixture(hard="M"*65,physical="M"*11+"C"+"M"*53);raw=p.rec(next(f[-1].rglob("*.pdb")));x=self.phase(f)
  y=x["trajectories"][0]["physical_exports"][0];self.assertEqual(y["hard_vs_physical"]["differences"],[dict(position=12,hard="M",physical="C")]);self.assertEqual(p.rec(raw["path"]),raw)
 def test_partial_event_tail_retained_byte_exact(self):
  f=self.phase_fixture(tail=True);m=self.phase(f)["source_streams"]["bindcraft_native_events"]["metadata"]
  self.assertEqual(m["partial_tail_bytes"],11);self.assertEqual(bytes.fromhex(m["partial_tail_hex"]),b'{"partial":')
 def test_no_durable_complete_not_fabricated(self):
  f=self.phase_fixture();path=f[-1]/"bindcraft_native_events.jsonl";path.write_text(path.read_text().splitlines()[0]+"\n")
  x=self.phase(f);self.assertEqual(x["phase_counts"]["trajectory_complete"],0);self.assertEqual(x["trajectories"][0]["status"],"TRAJECTORY_STARTED_NO_DURABLE_COMPLETION");self.assertIsNone(x["trajectories"][0]["hard_sequence"])
 def test_mpnn_batch_lineage_source_and_na_retained(self):
  f=self.phase_fixture(mpnn=True);x=self.phase(f)
  self.assertEqual(x["phase_counts"]["raw_complete_mpnn_proposals"],1);self.assertIsNone(x["normalized_mpnn_proposals"][0]["native_score"]);self.assertEqual(x["mpnn_batches"][0]["source_pdb_identity"]["binder_sequence"],"M"*65)
 def test_wrong_proposal_lineage_rejected(self):
  f=self.phase_fixture(mpnn=True);f[3][0]["lineage_id"]="other/attempt_0/trajectory"
  with self.assertRaisesRegex(ValueError,"lineage"):self.phase(f)
 def test_completion_missing_start_rejected(self):
  f=self.phase_fixture();path=f[-1]/"bindcraft_native_events.jsonl";path.write_text(path.read_text().splitlines()[1]+"\n")
  with self.assertRaisesRegex(ValueError,"lineage start"):self.phase(f)
 def test_source_pdb_outside_attempt_rejected(self):
  f=self.phase_fixture(mpnn=True);path=f[-1]/"bindcraft_native_events.jsonl";rows=[json.loads(s)for s in path.read_text().splitlines()];rows[-1]["source_pdb"]=str(self.root/"external.pdb");path.write_text("".join(json.dumps(x)+"\n"for x in rows))
  with self.assertRaises(ValueError):self.phase(f)
 def test_batch_complete_count_cannot_hide_missing_raw_proposals(self):
  f=self.phase_fixture(mpnn=True);path=f[-1]/"bindcraft_native_events.jsonl";rows=[json.loads(s)for s in path.read_text().splitlines()];rows[-1]["n"]=2;path.write_text("".join(json.dumps(x)+"\n"for x in rows))
  with self.assertRaisesRegex(ValueError,"batch event count"):self.phase(f)
 def test_duplicate_raw_proposal_id_rejected(self):
  f=self.phase_fixture(mpnn=True);path=f[-1]/"sequences.jsonl";path.write_text(path.read_text()*2)
  with self.assertRaisesRegex(ValueError,"Duplicate raw"):self.phase(f)
 def test_partial_pdb_length_is_not_complete65(self):
  f=self.phase_fixture(physical="M"*20);x=self.phase(f);y=x["trajectories"][0]["physical_exports"][0]
  self.assertFalse(y["chains"]["B"]["complete65"]);self.assertEqual(y["hard_vs_physical"]["status"],"LENGTHS_DIFFER")
 def test_unknown_event_retained(self):
  f=self.phase_fixture();path=f[-1]/"bindcraft_native_events.jsonl"
  with path.open("a")as h:h.write('{"event":"future_observation","value":4}\n')
  self.assertEqual(self.phase(f)["source_streams"]["bindcraft_native_events"]["rows"][-1]["value"],4)
 def test_phase_inventory_continues_other_attempts_after_bad_lineage(self):
  f=self.phase_fixture();rrpath=Path(f[0]["path"]);p.dump(rrpath,f[1]);rr=p.rec(rrpath);targetpath=self.root/"target.json";p.dump(targetpath,f[5])
  pl=dict(protocol=dict(targets=[dict(target_id="target",input_manifest=p.rec(targetpath))]));attempts=[dict(attempt_index=i,status="TIMED_OUT_BOUNDARY")for i in range(3)];seen=[];out=self.root/"out";out.mkdir()
  def fake(rr,run,a,*rest):
   seen.append(a["attempt_index"])
   if a["attempt_index"]==0:raise ValueError("unresolved fixture")
   return dict(attempt_index=a["attempt_index"])
  with patch.object(p,"read_run_ledgers",return_value=(attempts,[],[])),patch.object(p,"phase_attempt",side_effect=fake):
   with self.assertRaisesRegex(ValueError,"unresolved"):p.phase_inventory(pl,self.pr,[rr],out,{})
  saved=p.read(out/"phase_lineage_inventory.json");self.assertEqual(seen,[0,1,2]);self.assertEqual(len(saved["attempts"]),2);self.assertEqual(len(saved["issues"]),1)


def engineering_readback(out):
 base=p.R/"steps/22_matched_benchmark/engineering_pilot/runs_v5"
 refs=[dict(path=str(base/"13175_0/run_receipt.json"),bytes=10093,sha256="d5687ce42c328743d13de12726cb20c0066be34610398d8d143d15b96f83cdf4"),
       dict(path=str(base/"13175_1/run_receipt.json"),bytes=10083,sha256="927d4c659b054d903a56693a0d571b3a5b9bd795d4554394df39a8c834b7fbbb")]
 observations=[]
 for rr in refs:
  run=p.read(p.verify(rr));plan=p.read(p.verify(run["plan"]));attempts,events,updates=p.read_run_ledgers(run)
  target=p.read(p.verify(next(x["input_manifest"]for x in plan["protocol"]["targets"]if x["target_id"]==run["task"]["target_id"])))
  for a in attempts:observations.append(p.phase_attempt(rr,run,a,events,updates,target))
 rf,bc=observations
 p.need(rf["phase_counts"]["physical_backbone_files"]==1 and rf["phase_counts"]["raw_complete_mpnn_proposals"]==8 and rf["phase_counts"]["normalized_native_screening_updates"]==8,"Actual RF engineering lineage changed")
 p.need(bc["phase_counts"]["trajectory_complete"]==1 and bc["phase_counts"]["raw_complete_mpnn_proposals"]==0,"Actual BC optimized completion must not be collapsed to zero designs")
 x=bc["trajectories"][0]
 p.need(x["native_termination"]=="Clashing"and x["hard_sequence"]["complete65"],"Actual BC termination/hard sequence changed")
 p.need(len(x["physical_exports"])==1 and x["physical_exports"][0]["target_identity_matches_input"],"Actual BC exported structure/target changed")
 p.need(x["physical_exports"][0]["hard_vs_physical"]["differences"]==[dict(position=12,hard="M",physical="C")],"Actual native hard/pseudo export distinction changed")
 return p.dump(out/"engineering_phase_readback.json",dict(status="ACTUAL_ENGINEERING_PHASE_LINEAGE_READBACK_PASS",source=p.rec(p.SELF),observations=observations,scope="Engineering source readback only; not formal candidates, not method improvement or new inference"))

def main():
 p.cpu();snapshot=p.immutable();suite=unittest.defaultTestLoader.loadTestsFromTestCase(Contracts);result=unittest.TextTestRunner(verbosity=2).run(suite)
 out=Path(os.environ["FORMAL_POSTPROCESS_TEST_OUTPUT"]);out.mkdir(parents=True,exist_ok=False)
 readback=engineering_readback(out)if result.wasSuccessful()else None
 p.dump(out/"acceptance.json",dict(engineering_phase_readback=readback,status="FORMAL_POSTPROCESS_CPU_CONTRACTS_PASS"if result.wasSuccessful()else"FAILED",tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),source_snapshot=snapshot,no_inference=True,software_fixtures_not_scientific_results=True,job_id=os.environ["SLURM_JOB_ID"]))
 if not result.wasSuccessful():raise SystemExit(1)
if __name__=="__main__":main()

