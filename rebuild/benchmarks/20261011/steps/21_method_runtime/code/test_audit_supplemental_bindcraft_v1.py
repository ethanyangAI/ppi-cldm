import importlib.util,os,unittest
from pathlib import Path
P=Path(os.environ["COLLECTOR_SOURCE"]);spec=importlib.util.spec_from_file_location("collector",P);c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class Contracts(unittest.TestCase):
 def test_basic_raw_vs_rounded_lower(self):
  self.assertEqual(c.basic_decision({"plddt":.795},1,{"1_pLDDT":{"threshold":.8}}),(False,["1_pLDDT"]))
 def test_basic_exact_boundary_pass(self):
  self.assertEqual(c.basic_decision({"plddt":.8},1,{"1_pLDDT":{"threshold":.8}}),(True,[]))
 def test_basic_upper_raw_fail(self):
  self.assertEqual(c.basic_decision({"i_pae":.35001},2,{"2_i_pAE":{"threshold":.35}}),(False,["2_i_pAE"]))
 def test_none_threshold_skipped(self):
  self.assertEqual(c.basic_decision({},2,{"2_i_pAE":{"threshold":None}}),(True,[]))
 def rows(self,sequence):return [{"raw_pool_index":i,"sequence":sequence} for i in range(20)]
 def test_fixed_C_is_native_allowed(self):
  sequence="A"*11+"C"+"A"*53;c.check_pool(self.rows(sequence),{12},sequence)
 def test_new_sampled_C_rejected(self):
  with self.assertRaises(AssertionError):c.check_pool(self.rows("C"+"A"*64),{12},"A"*11+"C"+"A"*53)
 def test_wrong_pool_index_order_rejected(self):
  rows=self.rows("A"*65);rows[1]["raw_pool_index"]=0
  with self.assertRaises(AssertionError):c.check_pool(rows,set(),"A"*65)
 def test_no_complete_pool_fake(self):
  with self.assertRaises(AssertionError):c.check_pool(self.rows("A"*65)[:19],set(),"A"*65)
 def test_duplicates_remain_complete_generation(self):
  c.check_pool(self.rows("A"*65),set(),"A"*65)
if __name__=="__main__":unittest.main()
