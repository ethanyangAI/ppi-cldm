#!/usr/bin/env python3
"""Software-only cache contracts. Real old74 readback is a separate CPU catalog gate."""
import ast,copy,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location("cache_guard_under_test",Path(__file__).with_name("native74_cache_guard.py"));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def receipt(path="old"):
 return dict(path=path,sha256="a"*64,bytes=10)
def signature(j):
 v=copy.deepcopy(j)
 for key in ["input","target_msa"]:
  if v.get(key):v[key]={k:v[key][k]for k in ["bytes","sha256"]}
 return hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()
class Contracts(unittest.TestCase):
 def job(self):return dict(job_key="j",blind_id="b",target_id="t",engine="af2",variant="primary",slots=[dict(seed=31021,model=1)],expected_models=1,input=receipt(),target_msa=receipt("msa"),max_msa="128:256")
 def bind(self,a=None,b=None,e=None,f=None,t=None,u=None):
  j=self.job();return m.binding(a or j,b or copy.deepcopy(j),e or dict(target_sequence="AAA",binder_sequence="CCC"),f or dict(target_sequence="AAA",binder_sequence="CCC"),t or dict(reference_complex=receipt("ref"),input_manifest=receipt("old")),u or dict(reference_complex=receipt("ref"),input_manifest=receipt("new")),signature)
 def test_exact_query_and_metadata_only_paths_reuse(self):
  j=self.job();k=copy.deepcopy(j);k["input"]["path"]="newpath";self.assertTrue(self.bind(j,k)["query_entities_identical"])
 def test_query_change_rejected(self):
  with self.assertRaisesRegex(ValueError,"query"):self.bind(f=dict(target_sequence="AAA",binder_sequence="CCM"))
 def test_model_seed_change_rejected(self):
  j=self.job();j["slots"][0]["seed"]=31022
  with self.assertRaisesRegex(ValueError,"signature"):self.bind(b=j)
 def test_model_slot_change_rejected(self):
  j=self.job();j["slots"][0]["model"]=2
  with self.assertRaises(ValueError):self.bind(b=j)
 def test_input_bytes_change_rejected(self):
  j=self.job();j["input"]["sha256"]="b"*64
  with self.assertRaises(ValueError):self.bind(b=j)
 def test_msa_bytes_change_rejected(self):
  j=self.job();j["target_msa"]["bytes"]=11
  with self.assertRaises(ValueError):self.bind(b=j)
 def test_msa_depth_change_rejected(self):
  j=self.job();j["max_msa"]="1:1"
  with self.assertRaises(ValueError):self.bind(b=j)
 def test_variant_change_rejected(self):
  j=self.job();j["variant"]="single_sensitivity"
  with self.assertRaises(ValueError):self.bind(b=j)
 def test_reference_geometry_change_rejected(self):
  with self.assertRaisesRegex(ValueError,"geometry"):self.bind(u=dict(reference_complex=dict(receipt("ref"),sha256="b"*64)))
 def test_extra_entity_field_not_silently_dropped(self):
  with self.assertRaises(ValueError):self.bind(f=dict(target_sequence="AAA",binder_sequence="CCC",extra=1))
 def runtime(self):
  old=dict(runtime_locks=dict(model=receipt("old")),af2_parameter_receipts=[receipt("weight")]);new=copy.deepcopy(old);new["runtime_locks"]["gpu_ownership_guard"]=receipt("guard");return old,new
 def test_runtime_exact_extra_guard_only(self):
  a,b=self.runtime();self.assertTrue(m.runtime_compatibility(a,b,{},False)["added_identity_guard_only"])
 def test_runtime_samehash_newpath_requires_qualified_copy(self):
  a,b=self.runtime();b["runtime_locks"]["model"]["path"]="new"
  with self.assertRaisesRegex(ValueError,"Unqualified"):m.runtime_compatibility(a,b,{},False)
  m.runtime_compatibility(a,b,{("old","new"):(10,"a"*64)},False)
 def test_runtime_changed_source_rejected(self):
  a,b=self.runtime();b["runtime_locks"]["model"]["sha256"]="b"*64
  with self.assertRaisesRegex(ValueError,"bytes"):m.runtime_compatibility(a,b,{},False)
 def test_weights_changed_rejected(self):
  a,b=self.runtime();b["af2_parameter_receipts"][0]["sha256"]="b"*64
  with self.assertRaisesRegex(ValueError,"weights"):m.runtime_compatibility(a,b,{},False)
 def test_new_unknown_runtime_source_rejected(self):
  a,b=self.runtime();b["runtime_locks"]["new_source"]=receipt("new")
  with self.assertRaises(ValueError):m.runtime_compatibility(a,b,{},False)
 def history(self):
  return dict(aliases=[],historical_unresolved=[dict(status="HISTORICAL_UNRESOLVED_PROVENANCE",original=receipt(x))for x in["history1","history2"]])
 def test_historical_missing_never_satisfies_current_cache(self):
  r=m.OldResolver(self.history())
  with self.assertRaisesRegex(ValueError,"Historical missing"):r.verify(receipt("history1"))
 def test_no_third_history_exemption(self):
  x=self.history();x["historical_unresolved"].append(dict(status="HISTORICAL_UNRESOLVED_PROVENANCE",original=receipt("currentmissing")))
  with self.assertRaisesRegex(ValueError,"two"):m.OldResolver(x)
 def test_alias_changed_bytes_rejected(self):
  x=self.history();x["aliases"]=[dict(status="READONLY_BYTE_IDENTICAL_ALIAS",original=receipt("o"),archived=dict(receipt("a"),sha256="b"*64))]
  with self.assertRaisesRegex(ValueError,"Alias changes"):m.OldResolver(x)
 def controlplan(self):
  controls=[dict(blind_id=str(i))for i in range(7)];jobs=[]
  for i in range(7):
   for engine,variant,n in [("boltz","primary",3),("af2","primary",5)]+([("boltz","single_sensitivity",3)]if i<6 else[]):
    jobs.append(dict(job_key=str(i)+engine+variant,blind_id=str(i),target_id=str(i),engine=engine,variant=variant,expected_models=n))
  return dict(jobs=jobs),controls
 def test_exact20_74_controls(self):
  p,c=self.controlplan();self.assertEqual(len(m.planned_control_jobs(p,c)),20)
 def test_one_missing_control_worker_not_accepted(self):
  p,c=self.controlplan();p["jobs"].pop()
  with self.assertRaisesRegex(ValueError,"20"):m.planned_control_jobs(p,c)
 def test_candidate_not_counted_as_cache_control(self):
  p,c=self.controlplan();p["jobs"].append(dict(job_key="design",blind_id="design",expected_models=5));self.assertEqual(len(m.planned_control_jobs(p,c)),20)
 def test_duplicate_control_identity_rejected(self):
  p,c=self.controlplan();p["jobs"][1]=dict(p["jobs"][0],expected_models=5)
  with self.assertRaisesRegex(ValueError,"Duplicate"):m.planned_control_jobs(p,c)
 def test_source_scientific_ast_changes_rejected(self):
  funcs="\n".join("def "+n+"(x):\n return x\n"for n in m.SCIENCE_AST);old="SETTINGS=dict(a=1)\n"+funcs+"\ndef worker(plan_path,index,out):\n allocated=allocation(1)\n plan=read(plan_path);job=plan['jobs'][index]\n return job\n"
  new=old.replace(" allocated=allocation(1)"," require_immutable_source_context()\n allocated=allocation(1)").replace(" return job",' if plan["source"]["path"]!=str(Path(__file__).resolve()) or plan["frozen_source_bundle"]["path"]!=str(FROZEN_DIR.parent/"source_bundle.json"):raise ValueError("GPU plan source does not bind this immutable corrected core")\n return job')
  self.assertTrue(m.scientific_compatibility(old,new)["settings_AST_identical"])
  with self.assertRaisesRegex(ValueError,"Scientific"):m.scientific_compatibility(old,new.replace("def geometry(x):\n return x","def geometry(x):\n return x+1"))
 def test_source_model_call_extra_rejected(self):
  funcs="\n".join("def "+n+"(x):\n return x\n"for n in m.SCIENCE_AST);old="SETTINGS=dict(a=1)\n"+funcs+"\ndef worker(plan_path,index,out):\n allocated=allocation(1)\n plan=read(plan_path);job=plan['jobs'][index]\n return job\n"
  new=old.replace(" allocated=allocation(1)"," require_immutable_source_context()\n allocated=allocation(1)").replace(" return job",' if plan["source"]["path"]!=str(Path(__file__).resolve()) or plan["frozen_source_bundle"]["path"]!=str(FROZEN_DIR.parent/"source_bundle.json"):raise ValueError("GPU plan source does not bind this immutable corrected core")\n extra_model_call()\n return job')
  with self.assertRaisesRegex(ValueError,"Model execution"):m.scientific_compatibility(old,new)
if __name__=="__main__":unittest.main()

