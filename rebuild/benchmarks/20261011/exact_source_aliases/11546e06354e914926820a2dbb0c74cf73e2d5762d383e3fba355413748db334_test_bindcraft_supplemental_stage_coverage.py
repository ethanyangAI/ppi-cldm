import copy,importlib.util,json,os,sys,unittest
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9")
P=Path(os.environ["SUPPLEMENTAL_SOURCE"])
spec=importlib.util.spec_from_file_location("supp",P);supp=importlib.util.module_from_spec(spec);spec.loader.exec_module(supp)
sys.path.insert(0,str(R/"vendor/BindCraft"));import functions
class TestContracts(unittest.TestCase):
 def args(self):
  return object(),"A"*65,"SUPPLEMENTAL_raw_index0",{"target_pdb":{"path":"/fixed_target"}},"/fixed_pose",
 def test_split_native_calls_do_not_bypass_filters(self):
  calls=[];seen=[];adv={"num_recycles_validation":3,"mpnn_fix_interface":True};fil={"1_pLDDT":{"threshold":.8,"higher":True}}
  old=copy.deepcopy((adv,fil))
  class Native:
   @staticmethod
   def predict_binder_complex(*a):
    calls.append(a);return ({a[7][0]+1:{"pLDDT":.1}},False)
  def observer(i,operation):seen.append(i);return operation()
  result=supp.cover_models(Native,*self.args(),adv,fil,{"MPNN":"/m"},"/fail",observer)
  self.assertEqual(seen,[0,1]);self.assertEqual([x[7] for x in calls],[[0],[1]])
  self.assertIs(result[1][1],False);self.assertIs(result[2][1],False)
  self.assertEqual((adv,fil),old);self.assertEqual(calls[0][1],"A"*65);self.assertEqual(calls[1][6],"/fixed_pose")
 def test_split_calls_pass_result_does_not_imply_acceptance(self):
  class Native:
   @staticmethod
   def predict_binder_complex(*a):return ({a[7][0]+1:{"i_pTM":.99}},True)
  result=supp.cover_models(Native,*self.args(),{}, {},{},"f",lambda i,operation:operation())
  self.assertEqual(list(result),[1,2]);self.assertIn("NOT_NATIVE_ACCEPTED",supp.SCOPE)
 def test_exception_is_typed_no_retry(self):
  calls=[]
  class Native:
   @staticmethod
   def predict_binder_complex(*a):calls.append(a[7]);raise ValueError("API broken")
  with self.assertRaises(ValueError):supp.cover_models(Native,*self.args(),{}, {},{},"f",lambda i,operation:operation())
  self.assertEqual(calls,[[0]])
 def test_official_thresholds_unchanged_low(self):
  filter={"Average_i_pTM":{"threshold":.5,"higher":True}}
  self.assertEqual(functions.check_filters([.49],["Average_i_pTM"],filter),["Average_i_pTM"])
  self.assertIs(functions.check_filters([.5],["Average_i_pTM"],filter),True)
 def test_official_thresholds_unchanged_high(self):
  filter={"Average_i_pAE":{"threshold":.35,"higher":False}}
  self.assertEqual(functions.check_filters([.36],["Average_i_pAE"],filter),["Average_i_pAE"])
  self.assertIs(functions.check_filters([.35],["Average_i_pAE"],filter),True)
 def test_official_averages_round_after_each_model(self):
  stats={1:{"i_pTM":.66},2:{"i_pTM":.67}}
  self.assertEqual(functions.calculate_averages(stats)["i_pTM"],round((.66+.67)/2,2))
 def test_config_native_exact_default(self):
  adv=json.loads((R/"vendor/BindCraft/settings_advanced/default_4stage_multimer.json").read_text())
  self.assertEqual((adv["num_seqs"],adv["sampling_temp"],adv["mpnn_fix_interface"],adv["mpnn_weights"],adv["omit_AAs"],adv["num_recycles_validation"]),(20,.1,True,"soluble","C",3))
 def test_source_no_formal_generation_ledger_writer(self):
  source=P.read_text()
  self.assertNotIn('append_stream(out/"sequences.jsonl"',source)
  self.assertNotIn('append_stream(out/"native_screening.jsonl"',source)
  self.assertIn('chosen=rows[0]',source)
  self.assertNotIn('sorted(pool',source)
  self.assertNotIn('binder_hallucination(',source)
 def test_physical_identity_both_chains(self):
  target=json.loads(supp.TARGET.read_text())
  actual=supp.identity(supp.POSE,target["target_sequence"],supp.SEQUENCE)
  self.assertEqual(actual["binder_count"],65);self.assertEqual(actual["full_target_count"],285)
 def test_wrong_binder_query_rejected(self):
  target=json.loads(supp.TARGET.read_text())
  with self.assertRaises(AssertionError):supp.identity(supp.POSE,target["target_sequence"],"G"*65)
 def test_wrong_target_rejected(self):
  with self.assertRaises(AssertionError):supp.identity(supp.POSE,"G"*285,supp.SEQUENCE)
 def test_numpy_seed_keyword_and_none_deterministic_contract(self):
  import numpy as np
  events=[];callback,original=supp.make_seed_controller(np,791205,lambda stage,**kw:events.append((stage,kw)))
  callback(seed=None);first=np.random.randint(0,2**31-1)
  callback(seed=123);self.assertEqual(np.random.randint(0,2**31-1),843828734)
  again,_=supp.make_seed_controller(np,791205,lambda stage,**kw:None);again(seed=None)
  self.assertEqual(first,np.random.randint(0,2**31-1))
  self.assertEqual(len(events),1);self.assertEqual(events[0][0],"deterministic_entropy_seed")
  self.assertGreaterEqual(events[0][1]["seed"],0);self.assertLess(events[0][1]["seed"],2**31-1)
 def test_official_soft_vs_hard_export_semantics(self):
  import numpy as np
  import jax.numpy as jnp
  from colabdesign.shared.model import soft_seq
  from colabdesign.af.alphafold.common import residue_constants as rc
  x=np.zeros((1,1,20));x[0,0,rc.restype_order["C"]]=100;x[0,0,rc.restype_order["M"]]=1
  bias=np.zeros(20);bias[rc.restype_order["C"]]=-1e6
  seq=soft_seq(jnp.asarray(x),jnp.asarray(bias),{"alpha":1,"temp":1,"soft":.792,"hard":0})
  self.assertEqual(rc.restypes[int(np.asarray(seq["hard"]).argmax(-1)[0,0])],"M")
  self.assertEqual(rc.restypes[int(np.asarray(seq["pseudo"]).argmax(-1)[0,0])],"C")
 def test_coverage_scope_rejects_formal_interpretation(self):
  self.assertEqual(supp.SCOPE,"ENGINEERING_STAGE_COVERAGE_ONLY_NOT_NATIVE_ACCEPTED_NOT_FORMAL")
if __name__=="__main__":unittest.main()
