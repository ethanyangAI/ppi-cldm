#!/usr/bin/env python3
"""Synthetic software contracts: never biological results."""
import copy,datetime,hashlib,json,os,tempfile,unittest
from pathlib import Path
import independent_resource_policy as r
import audit_supplemental_engineering as s
class Contracts(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.D=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def write(self,name,value,readonly=False):
  p=self.D/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value)if not isinstance(value,str)else value)
  if readonly:p.chmod(0o444)
  return p
 def scheduler(self,jid="42",cpu=2,gpu=1,state="RUNNING",extras=""):
  return f"JobId={jid} JobState={state} StartTime=2026-10-11T12:00:00 NumCPUs={cpu} CPUs/Task={cpu} TRES=cpu={cpu},gres/gpu={gpu} NodeList=gpu1 Partition=organ MinMemoryNode=64G {extras}\n"
 def rows(self,seconds=500,cpu=2,gpu=1,state="COMPLETED",extra=""):
  return f"42|{seconds}|cpu={cpu},gres/gpu={gpu}|{state}|2026-10-11T12:00:00|2026-10-11T12:08:20|gpu1|organ\n43|0||CANCELLED by1|None|None||organ\n"+extra
 def pool(self):
  return {"rows":[{"raw_pool_index":i,"sequence_record_id":"id"+str(i),"sequence":"A"*65,"scientific_scope":s.SCOPE,"score":.4,"seqid":.2,"retained_fixed_cysteine_positions":[]}for i in range(20)]}
 def test_actual2gpu1_pass(self):self.assertEqual(s.allocation_contract(self.rows(),"42","43")["allocated_gpu_seconds"],500)
 def test_cancelled_zero_pass(self):self.assertEqual(s.allocation_contract(self.rows(),"42","43")["cancelled"]["allocated_gpu_seconds"],0)
 def test_resource_cpu2_not_cpu4(self):
  with self.assertRaises(ValueError):s.allocation_contract(self.rows(cpu=4),"42","43")
 def test_wrong_gpu(self):
  with self.assertRaises(ValueError):s.allocation_contract(self.rows(gpu=2),"42","43")
 def test_over_hardbudget(self):
  with self.assertRaises(ValueError):s.allocation_contract(self.rows(seconds=3603),"42","43")
 def test_upper_tolerance_pass(self):self.assertEqual(s.allocation_contract(self.rows(seconds=3602),"42","43")["allocated_gpu_seconds"],3602)
 def test_positive_duration_missing(self):
  with self.assertRaises(ValueError):s.allocation_contract(self.rows(seconds=0),"42","43")
 def test_pending_not_terminal(self):
  with self.assertRaises(ValueError):s.allocation_contract(self.rows(state="RUNNING"),"42","43")
 def test_step_no_doublecount(self):self.assertEqual(s.allocation_contract(self.rows(extra="42.batch|500|cpu=2,gres/gpu=1|COMPLETED|X|X|gpu1|organ\n"),"42","43")["allocated_gpu_seconds"],500)
 def test_duplicate_master_raw_reject(self):
  with self.assertRaises(ValueError):s.allocation_contract(self.rows(extra="42|42_0|500|cpu=2,gres/gpu=1|COMPLETED|X|X|gpu1|organ\n"),"42","43")
 def test_unrecorded_positive_reject(self):
  with self.assertRaises(ValueError):s.allocation_contract(self.rows(extra="44|500|cpu=2,gres/gpu=1|COMPLETED|X|X|gpu1|organ\n"),"42","43")
 def test_cancelled_gpu_requested_not_actual(self):
  text=self.rows().replace("43|0||","43|0|gres/gpu=1|")
  with self.assertRaises(ValueError):s.allocation_contract(text,"42","43")
 def test_cancelled_started_reject(self):
  text=self.rows().replace("by1|None|None","by1|2026-10-11T12:00:00|None")
  with self.assertRaises(ValueError):s.allocation_contract(text,"42","43")
 def test_cancelled_cpu_allocation_reject(self):
  with self.assertRaises(ValueError):s.allocation_contract(self.rows().replace("43|0||","43|0|cpu=2|"),"42","43")
 def test_typed_generic_mismatch(self):
  with self.assertRaises(ValueError):r.gpu_count("cpu=3,gres/gpu=1,gres/gpu:a100=2")
 def test_typed_generic_not_double(self):self.assertEqual(r.gpu_count("cpu=3,gres/gpu=1,gres/gpu:a100=1"),1)
 def test_requested_tres_is_not_allocation(self):
  with self.assertRaises(ValueError):r.running_allocation(self.scheduler().replace("TRES=","ReqTRES="),"42",2,1)
 def test_running_selected_not_sibling(self):
  text=self.scheduler("43")+self.scheduler(state="FAILED")
  with self.assertRaises(ValueError):r.running_allocation(text,"42",2,1)
 def test_ambiguous_selected(self):
  with self.assertRaises(ValueError):r.running_allocation(self.scheduler()+self.scheduler(),"42",2,1)
 def test_array_raw_vs_logical(self):
  a=r.running_allocation(self.scheduler(extras="ArrayJobId=41 ArrayTaskId=0"),"41_0",2,1)
  self.assertEqual(a["raw_allocation_id"],"42")
 def test_fullpool_all_lineages_retained(self):
  p=self.pool();c=s.raw_pool_contract(p,p["rows"]);self.assertEqual((c["raw_records"],c["unique_sequence_identities"]),(20,1))
 def test_missing_rejected_rawrow(self):
  p=self.pool();p["rows"].pop()
  with self.assertRaises(ValueError):s.raw_pool_contract(p,p["rows"])
 def test_wrong65_allraw_not_acceptedonly(self):
  p=self.pool();p["rows"][19]["sequence"]="A"*64
  with self.assertRaises(ValueError):s.raw_pool_contract(p,p["rows"])
 def test_reordered_pool(self):
  p=self.pool();p["rows"].reverse()
  with self.assertRaises(ValueError):s.raw_pool_contract(p,p["rows"])
 def test_duplicate_lineage(self):
  p=self.pool();p["rows"][19]["sequence_record_id"]="id0"
  with self.assertRaises(ValueError):s.raw_pool_contract(p,p["rows"])
 def test_stream_closure(self):
  p=self.pool();stream=copy.deepcopy(p["rows"]);stream[-1]["score"]=.5
  with self.assertRaises(ValueError):s.raw_pool_contract(p,stream)
 def test_fixed_c_is_not_omit_sampling_violation(self):
  p=self.pool();p["rows"][0]["sequence"]="C"+"A"*64;p["rows"][0]["retained_fixed_cysteine_positions"]=[1]
  self.assertEqual(s.raw_pool_contract(p,p["rows"])["raw_records"],20)
 def test_false_native_acceptance_reject(self):
  p=self.pool();p["rows"][0]["internal_acceptance"]=True
  with self.assertRaises(ValueError):s.raw_pool_contract(p,p["rows"])
 def test_native_score_leak_reject(self):
  p=self.pool();p["rows"][0]["native_score"]=.8
  with self.assertRaises(ValueError):s.raw_pool_contract(p,p["rows"])
 def test_partial_raw_stream(self):
  p=self.write("raw.jsonl",'{"a":1}')
  with self.assertRaises(ValueError):s.jsonl_complete(p)
 def test_scope_leak_reject(self):
  p=self.pool();p["rows"][0]["scientific_scope"]="FORMAL"
  with self.assertRaises(ValueError):s.raw_pool_contract(p,p["rows"])
 def test_memory_unavailable_notzero(self):
  m=r.memory_record({"MinMemoryNode":"64G","NumCPUs":"3"},"cpu=3,gres/gpu=1")
  self.assertIsNone(m["actual_allocated_memory_gib"]);self.assertEqual(m["actual_memory_status"],"UNAVAILABLE_NOT_ZERO")
 def test_memory_actual64(self):self.assertEqual(r.memory_record({"MinMemoryNode":"64G","NumCPUs":"3"},"cpu=3,mem=65536M")["actual_allocated_memory_gib"],64)
 def test_memory_smaller(self):
  with self.assertRaises(ValueError):r.memory_record({"MinMemoryNode":"64G","NumCPUs":"3"},"cpu=3,mem=32G")
 def test_requested_memory_changed(self):
  with self.assertRaises(ValueError):r.memory_record({"MinMemoryNode":"32G","NumCPUs":"3"},"cpu=3")
 def test_requested_cpu_fields_disagree(self):
  with self.assertRaises(ValueError):r.running_allocation(self.scheduler().replace("CPUs/Task=2","CPUs/Task=4"),"42",2,1)
 def fixture(self):
  protocol={"gpu_count":1,"budget_gpu_seconds":3600,"binder_length":65,"replicate_seeds":[21011,21012],"methods":[{"adapter_receipts":[r.RUNTIME_RECEIPT]},{"adapter_receipts":[r.RUNTIME_RECEIPT]}]}
  pp=self.write("protocol.json",protocol,True);plan={"protocol":protocol,"protocol_receipt":r.rec(pp),"tasks":[{"task_id":str(i),"array_index":i}for i in range(28)]}
  p=self.write("plan.json",plan,True)
  launch=self.write("original.sbatch",f"#SBATCH --cpus-per-task=4\n#SBATCH --mem=64G\n#SBATCH --gres=gpu:1\nexport OMP_NUM_THREADS=4\n{p} {r.rec(p)['sha256']}\n",True)
  from unittest.mock import patch
  with patch.object(r,"cpu_guard",return_value={"allocated_gpu_count":0}):result=r.freeze_resource_policy(p,launch,self.D/"frozen")
  policy_path=Path(result["policy"]["path"]);pol=r.read(policy_path);pol["created_at_epoch"]=0;policy_path.chmod(0o644);policy_path.write_text(json.dumps(pol));policy_path.chmod(0o444)
  submit=self.write("submit.json",{"launcher":pol["launcher"],"resource_policy":r.rec(policy_path),"plan":pol["plan"],"submit_argv":["sbatch","--parsable",pol["launcher"]["path"]],"job_id":"100"},True)
  receipts=[];lines=[]
  for i in range(28):
   raw=str(100+i);sched=self.write("sched"+str(i)+".txt",self.scheduler(raw,cpu=3,extras=f"ArrayJobId=100 ArrayTaskId={i} Command={pol['launcher']['path']}"))
   run={"task":plan["tasks"][i],"plan":pol["plan"],"allocation_key":"100_"+str(i),"scheduler_start":r.rec(sched),"hardware":{"gpus":[{"name":pol["gpu_name"],"memory_total_mib":40960}]}}
   receipts.append(r.rec(self.write("run"+str(i)+".json",run)))
   lines.append(f"{raw}|500|cpu=3,gres/gpu=1|COMPLETED|2026-10-11T12:00:00|2026-10-11T12:08:20|gpu1|organ")
  return policy_path,receipts,"\n".join(lines)+"\n",[r.rec(submit)]
 def test_formal_complete28_resources(self):
  self.assertEqual(r.formal_resources(*self.fixture())["task_count"],28)
 def test_formal_missing_empty_task(self):
  p,runs,text,sub=self.fixture()
  with self.assertRaises(ValueError):r.formal_resources(p,runs[:-1],text,sub)
 def test_formal_wrong_arm_cpu(self):
  p,runs,text,sub=self.fixture()
  with self.assertRaises(ValueError):r.formal_resources(p,runs,text.replace("cpu=3","cpu=4",1),sub)
 def test_formal_posthoc_cpu_override(self):
  p,runs,text,sub=self.fixture();doc=r.read(sub[0]["path"]);doc["submit_argv"].insert(2,"--cpus-per-task=4")
  path=Path(sub[0]["path"]);path.chmod(0o644);path.write_text(json.dumps(doc));path.chmod(0o444)
  with self.assertRaises(ValueError):r.formal_resources(p,runs,text,[r.rec(path)])
 def test_formal_missing_rerun_receipt(self):
  p,runs,text,sub=self.fixture();text+="199|500|cpu=3,gres/gpu=1|FAILED|2026-10-11T12:00:00|2026-10-11T12:08:20|gpu1|organ\n"
  with self.assertRaises(ValueError):r.formal_resources(p,runs,text,sub)
 def test_formal_repeated_physical_allocation(self):
  p,runs,text,sub=self.fixture()
  with self.assertRaises(ValueError):r.formal_resources(p,runs+[runs[0]],text,sub)
 def test_formal_generation_before_policy(self):
  p,runs,text,sub=self.fixture();doc=r.read(p);doc["created_at_epoch"]=9999999999;p.chmod(0o644);p.write_text(json.dumps(doc));p.chmod(0o444)
  submit=r.read(sub[0]["path"]);submit["resource_policy"]=r.rec(p);sp=Path(sub[0]["path"]);sp.chmod(0o644);sp.write_text(json.dumps(submit));sp.chmod(0o444)
  with self.assertRaises(ValueError):r.formal_resources(p,runs,text,[r.rec(sp)])
 def test_policy_armspecific_disallowed(self):
  p,runs,text,sub=self.fixture();pol=r.read(p);pol["arm_specific_resource_overrides_allowed"]=True
  with self.assertRaises(ValueError):r.formal_policy(pol)
 def test_policy_source_drift(self):
  p,runs,text,sub=self.fixture();pol=r.read(p);path=Path(pol["launcher"]["path"]);path.chmod(0o644);path.write_text(path.read_text()+"# drift\n");path.chmod(0o444)
  with self.assertRaises(ValueError):r.formal_resources(p,runs,text,sub)
 def test_frozen_source_pin_required(self):
  p,runs,text,sub=self.fixture();doc=r.read(p);doc["source"]["sha256"]="0"*64;p.chmod(0o644);p.write_text(json.dumps(doc));p.chmod(0o444)
  with self.assertRaises(ValueError):r.formal_resources(p,runs,text,sub)
 def test_array_index_task_mapping(self):
  p,runs,text,sub=self.fixture();run=r.read(runs[0]["path"]);sched=Path(run["scheduler_start"]["path"]);sched.write_text(sched.read_text().replace("ArrayTaskId=0","ArrayTaskId=27"));run["scheduler_start"]=r.rec(sched);path=Path(runs[0]["path"]);path.write_text(json.dumps(run));runs[0]=r.rec(path)
  with self.assertRaises(ValueError):r.formal_resources(p,runs,text,sub)
 def test_full_task_definition_not_only_id(self):
  p,runs,text,sub=self.fixture();run=r.read(runs[0]["path"]);run["task"]["array_index"]=17;path=Path(runs[0]["path"]);path.write_text(json.dumps(run));runs[0]=r.rec(path)
  with self.assertRaises(ValueError):r.formal_resources(p,runs,text,sub)
class RNGContracts(unittest.TestCase):
 def events(self,entropy=True):
  import random,numpy as np
  seed=791205;value=random.Random(seed).randint(0,2147483647)
  rows=[{"stage":"python_rng_seeded_before_official_constructors","root_seed":seed,"additional_draws":0},
   {"stage":"python_random_randint_observed","lower":0,"upper":2147483647,"value":value},
   {"stage":"actual_mpnn_constructor_key_seed_observed","seed":value,"constructor_kwargs":{},"additional_draws":0}]
  if entropy:rows.append({"stage":"deterministic_entropy_seed","seed":int(np.random.default_rng(seed).integers(0,2**31-1))})
  return[dict(x,scientific_scope=s.SCOPE,completed_at_epoch=100+i)for i,x in enumerate(rows)]
 def test_distinct_python_numpy_streams(self):
  import audit_seeded_supplemental as c
  rows=self.events();self.assertNotEqual(rows[2]["seed"],rows[3]["seed"]);self.assertEqual(c.rng_events(rows,791205)["actual_mpnn_key_seed"],1781849165)
 def test_actual_python_return_changed(self):
  import audit_seeded_supplemental as c
  rows=self.events();rows[1]["value"]+=1
  with self.assertRaises(ValueError):c.rng_events(rows,791205)
 def test_mpnn_seed_is_not_numpy_fallback(self):
  import audit_seeded_supplemental as c
  rows=self.events();rows[2]["seed"]=rows[3]["seed"]
  with self.assertRaises(ValueError):c.rng_events(rows,791205)
 def test_numpy_fallback_changed(self):
  import audit_seeded_supplemental as c
  rows=self.events();rows[-1]["seed"]+=1
  with self.assertRaises(ValueError):c.rng_events(rows,791205)
 def test_missing_preconstructor_seed(self):
  import audit_seeded_supplemental as c
  with self.assertRaises(ValueError):c.rng_events(self.events()[1:],791205)
 def test_seed_observer_extra_draw(self):
  import audit_seeded_supplemental as c
  rows=self.events();rows[2]["additional_draws"]=1
  with self.assertRaises(ValueError):c.rng_events(rows,791205)
if __name__=="__main__":unittest.main(verbosity=2)

