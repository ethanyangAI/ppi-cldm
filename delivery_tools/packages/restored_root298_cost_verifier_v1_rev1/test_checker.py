#!/usr/bin/env python3
"""Twenty-four actual CPU contracts. All accounting rows are SYNTHETIC_SOFTWARE_FIXTURE_ONLY."""
import copy,datetime,hashlib,json,os,shutil,tempfile,unittest
from pathlib import Path
CHECKER=None;READER=None;CORE=None;COST=None
LABEL="SYNTHETIC_ACCOUNTING_METADATA_SOFTWARE_FIXTURE_ONLY_NO_ACTUAL_GPU"
class Ref:
 def __init__(self,name):self.name=name
class Fixture:
 def __init__(self,owner,mutate=None):
  self.temp=tempfile.TemporaryDirectory(prefix="root298_fixture_",dir=CHECKER.S/"tmp");owner.addCleanup(self.temp.cleanup)
  self.base=Path(self.temp.name);self.origin=self.base/"origin";self.origin.mkdir();self.root=self.base/"restored";self.out=self.root/"new_cost_output";self.graph={};self.memo={}
  self.dispatches=[
   dict(submission_id="formal13260",phase="formal_generation",kind="primary",job_id="13260",indices=list(range(28)),stage=None,preflight=None,launcher=None,job_name="test9_formal_synthetic",WorkDir=str(CHECKER.R),expected_allocation_count=28,rerun_of=None),
   dict(submission_id="common13423",phase="common_review",kind="primary",job_id="13423",indices=list(range(268)),stage=None,preflight=None,launcher=None,job_name="ppi_formal_common_synthetic",WorkDir=str(CHECKER.R),expected_allocation_count=268,rerun_of=None),
   dict(submission_id="design13304",phase="reference_free_e2e",kind="primary",job_id="13304",indices=None,stage="design",preflight=None,launcher=None,job_name="test9_e2e_synthetic",WorkDir=str(CHECKER.R),expected_allocation_count=1,rerun_of=None),
   dict(submission_id="evaluate13311",phase="reference_free_e2e",kind="primary",job_id="13311",indices=None,stage="evaluate",preflight=None,launcher=None,job_name="test9_e2e_synthetic",WorkDir=str(CHECKER.R),expected_allocation_count=1,rerun_of=None)]
  self.ledger=dict(schema="root-current-gpu-submission-universe.v1",authority_root=str(CHECKER.R),scope_start_utc=COST.PRIMARY_START,scope_end_utc="2026-10-12T16:39:19Z",formal_array_job_id="13260",global_current_scope_gpu_cap=2,synthetic_fixture=LABEL)
  expected,_=COST.expected_allocations(self.dispatches);self.lines=[]
  base=datetime.datetime.fromtimestamp(COST.utc(COST.PRIMARY_START),datetime.timezone.utc)
  stamp=lambda d:d.strftime("%Y-%m-%dT%H:%M:%S")
  for i,(logical,d)in enumerate(expected.items()):
   start=base+datetime.timedelta(seconds=60+10*i);end=start+datetime.timedelta(seconds=10)
   self.lines.append("|".join([logical,str(20000+i),d["job_name"],COST.USER,COST.USER,"FAILED"if i==0 else"COMPLETED","10","billing=1,cpu=3,gres/gpu=1,mem=64G",stamp(base),stamp(start),stamp(end),"SYNTHETIC_NODE","organ",str(CHECKER.R)]))
  self.step=self.lines[0].replace("13260_0|20000|","13260_0.batch|20000.batch|")
  self.explicit="\n".join(self.lines+[self.step])+"\n";self.universe="\n".join(list(reversed(self.lines))+[self.step])+"\n"
  self.closed=COST.close_rows(self.dispatches,self.explicit,self.universe,COST.utc(self.ledger["scope_end_utc"]))
  self.add("explicit.stdout",self.explicit.encode());self.add("universe.stdout",self.universe.encode());self.add("empty.stderr",b"")
  self.add("explicit.command.json",dict(argv=["sacct","-n","-P","-j","13260,13304,13311,13423","--format="+COST.FIELDS],returncode=0,TZ="UTC",SLURM_TIME_FORMAT="standard",stdout=Ref("explicit.stdout"),stderr=Ref("empty.stderr"),synthetic_fixture=LABEL))
  self.add("universe.command.json",dict(argv=COST.time_universe_argv(self.ledger),returncode=0,TZ="UTC",SLURM_TIME_FORMAT="standard",stdout=Ref("universe.stdout"),stderr=Ref("empty.stderr"),synthetic_fixture=LABEL))
  self.add("closure.json",self.closed)
  if mutate:mutate(self)
  self.package()
 def add(self,name,obj):self.graph[name]=obj;return Ref(name)
 def resolve(self,obj):
  if isinstance(obj,Ref):return self.materialize(obj.name)
  if isinstance(obj,dict):return {k:self.resolve(v)for k,v in obj.items()}
  if isinstance(obj,list):return [self.resolve(v)for v in obj]
  return obj
 def materialize(self,name):
  if name in self.memo:return self.memo[name]
  obj=self.graph[name];data=obj if isinstance(obj,bytes)else CHECKER.jbytes(self.resolve(obj));p=self.origin/name;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open("xb")as f:f.write(data)
  p.chmod(0o444);r=dict(path=str(p),bytes=len(data),sha256=hashlib.sha256(data).hexdigest());self.memo[name]=r;return r
 def package(self):
  for name in list(self.graph):self.materialize(name)
  config=self.materialize("config.json")if"config.json"in self.graph else self.add_config()
  validation=dict(status="FINAL_DELIVERY_CONFIG_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY",authority_root=str(self.origin),config=config,phase_id=LABEL,files={Path(r["path"]).relative_to(self.origin).as_posix():dict(receipt=r,classification="AUDIT")for r in self.memo.values()},conditional_inference_dependencies=[])
  vp=self.origin/"validation.json";vp.write_bytes(CHECKER.jbytes(validation));vp.chmod(0o444)
  CORE.package(vp,self.base/"package",1);pp=self.base/"package/packaging_receipt.json";pp.chmod(0o444);self.package_receipt=CORE.rec(pp);self.pkg=CHECKER.parse_json(pp.read_bytes())
  CORE.extract(pp,self.root);mp=self.root/"RESTORE_HASH_ACCEPTANCE.json";mp.chmod(0o444);self.marker=CORE.rec(mp);self.scope=self.new_scope()
 def add_config(self):
  self.add("config.json",dict(synthetic_fixture=LABEL,resource_aliases=None));return self.materialize("config.json")
 def new_scope(self,pkg=None,aliases=None):
  return READER.StrictIndex(pkg or self.pkg,self.root,self.out,aliases=aliases,controls=[self.package_receipt,self.marker])
 def replay(self):
  return CHECKER.replay_streams(self.scope,COST,self.dispatches,self.ledger,self.memo["explicit.command.json"],self.memo["universe.command.json"],self.memo["closure.json"])[0]
 def omit(self,name):
  pkg=copy.deepcopy(self.pkg);pkg["manifest"]=[row for row in pkg["manifest"]if row["receipt"]["path"]!=self.memo[name]["path"]];self.scope=self.new_scope(pkg)
 def poison_live(self):
  for r in self.memo.values():
   p=Path(r["path"]);p.chmod(0o600);p.write_bytes(b"POISONED_LIVE_SOFTWARE_INPUT\n");p.chmod(0o444)
 def row_change(self,idx,col,value,target="universe"):
  name=target+".stdout";lines=self.graph[name].decode().splitlines();row=lines[idx].split("|");row[col]=value;lines[idx]="|".join(row);self.graph[name]=("\n".join(lines)+"\n").encode()
class Root298IndexContracts(unittest.TestCase):
 def fx(self,mutate=None):return Fixture(self,mutate)
 def bad(self,mutate):
  f=self.fx(mutate)
  with self.assertRaises((ValueError,KeyError)):f.replay()
 def test_01_genuine_core_package_extract_full298_replay(self):
  f=self.fx();actual=f.replay();self.assertEqual(actual["expected_submitted_allocation_slots"],298);self.assertEqual(actual["allocated_GPU_jobs"],298);self.assertEqual(actual["actual_GPU_seconds"],2980);self.assertEqual(actual["allocated_failure_GPU_seconds"],10)
  self.assertTrue(actual["complete_root_gpu_submission_universe"]);self.assertEqual(len(actual["excluded_job_steps"]),1);self.assertEqual(len(actual["excluded_universe_steps"]),1)
  f.scope.after(touched_only=True);r=CHECKER.write_scoped(f.scope,f.out,"replayed.json",actual);self.assertEqual(Path(r["path"]).parent,f.out);self.assertIn(r["path"],f.scope.proof()["fresh_output_paths"]);self.assertFalse(f.scope.proof()["live_scientific_fallback"])
 def test_02_restored_positive_with_poisoned_live_inputs(self):
  f=self.fx();f.poison_live();self.assertEqual(f.replay()["allocated_GPU_jobs"],298);f.scope.after(touched_only=True)
 def test_03_missing_indexed_streams_and_saved_object_no_live_rescue(self):
  for name in("explicit.stdout","universe.stdout","closure.json"):
   with self.subTest(name=name):
    f=self.fx();self.assertTrue(Path(f.memo[name]["path"]).exists());f.omit(name);f.poison_live()
    with self.assertRaises(ValueError):f.replay()
 def test_04_wrong_sha_and_ambiguous_index_selection(self):
  f=self.fx();bad=dict(f.memo["closure.json"],sha256="0"*64)
  with self.assertRaises(ValueError):CHECKER.input_json(f.scope,bad)
  logical=f.memo["closure.json"]["path"];f.scope.paths[logical].append((logical,0,"1"*64))
  with self.assertRaisesRegex(ValueError,"unambiguous"):CHECKER.select_index(f.scope,logical)
 def test_05_duplicate_and_conflicting_index_paths(self):
  f=self.fx()
  for change in(False,True):
   pkg=copy.deepcopy(f.pkg);row=copy.deepcopy(pkg["manifest"][0])
   if change:row["receipt"]["sha256"]="0"*64
   pkg["manifest"].append(row)
   with self.subTest(conflict=change),self.assertRaises(ValueError):f.new_scope(pkg)
 def test_06_byte_identical_alias_and_alias_conflict(self):
  f=self.fx();r=f.memo["closure.json"];a=dict(r,path=str(f.origin/"declared/old.json"));aliases=dict(aliases=[dict(original=a,archived=r,status="READONLY_BYTE_IDENTICAL_ALIAS")])
  scope=f.new_scope(aliases=aliases);self.assertEqual(CHECKER.input_bytes(scope,a),CHECKER.input_bytes(scope,r));scope.after(touched_only=True)
  for entry in [dict(original=dict(a,bytes=a["bytes"]+1),archived=r,status="READONLY_BYTE_IDENTICAL_ALIAS"),dict(original=a,archived=r,status="UNVERIFIED")]:
   with self.subTest(alias=entry),self.assertRaises(ValueError):f.new_scope(aliases=dict(aliases=[entry]))
 def test_07_lexical_and_leaf_ancestor_root_symlink_inputs(self):
  f=self.fx()
  for p in(str(f.origin)+"/../closure.json",str(f.origin)+"//closure.json",str(f.origin)+"/./closure.json"):
   with self.subTest(path=p),self.assertRaises(ValueError):f.scope.verify(dict(path=p,bytes=0,sha256="0"*64))
  leaf=f.root/"closure.json";leaf.unlink();leaf.symlink_to(f.memo["closure.json"]["path"])
  with self.assertRaises(ValueError):f.replay()
  f2=self.fx();real=f2.base/"realroot";f2.root.rename(real);f2.root.symlink_to(real,target_is_directory=True)
  with self.assertRaises(ValueError):f2.new_scope()
  f3=self.fx(lambda f:f.add("nested/evidence/checked.json",dict(synthetic_fixture=LABEL)));folder=f3.root/"nested/evidence";real3=f3.base/"real_evidence";folder.rename(real3);folder.symlink_to(real3,target_is_directory=True)
  with self.assertRaises(ValueError):CHECKER.input_json(f3.scope,f3.memo["nested/evidence/checked.json"])
 def test_08_readonly_and_postread_byte_drift(self):
  f=self.fx();(f.root/"closure.json").chmod(0o644)
  with self.assertRaises(ValueError):f.replay()
  f2=self.fx();f2.replay();p=f2.root/"universe.stdout";p.chmod(0o600);p.write_bytes(b"DRIFT\n");p.chmod(0o444)
  with self.assertRaises(ValueError):f2.scope.after(touched_only=True)
 def test_09_independent_omitted_allocation_no_explicit_fill(self):
  self.bad(lambda f:f.graph.update({"universe.stdout":"\n".join(f.universe.splitlines()[1:]).encode()+b"\n"}))
 def test_10_unknown_current_allocated_gpu_job_rejected(self):
  def change(f):
   row=f.lines[0].split("|");row[0]="999999";row[1]="999999";f.graph["universe.stdout"]+=("|".join(row)+"\n").encode()
  self.bad(change)
 def test_11_duplicate_logical_and_actual_numeric_allocations(self):
  self.bad(lambda f:f.graph.update({"universe.stdout":f.universe.encode()+(f.lines[0]+"\n").encode()}))
  self.bad(lambda f:f.row_change(1,1,"20000",target="explicit"))
 def test_12_explicit_and_independent_tuple_drift(self):
  values={1:"999999",5:"FAILED",6:"9",7:"cpu=3,gres/gpu=1,mem=64G",8:"2026-10-11T14:25:01",9:"2026-10-11T14:25:02",10:"2026-10-11T14:25:03",13:str(CHECKER.R/"different_workdir")}
  for col,value in values.items():
   with self.subTest(field=col):self.bad(lambda f:f.row_change(0,col,value))
 def test_13_missing_gpu_tres_and_malformed_width_rejected(self):
  self.bad(lambda f:f.row_change(0,7,"cpu=3"))
  self.bad(lambda f:f.graph.update({"universe.stdout":f.universe.encode()+b"not|fourteen|fields\n"}))
 def test_14_explicit_missing_slot_or_nonterminal_rejected(self):
  self.bad(lambda f:f.graph.update({"explicit.stdout":"\n".join(f.explicit.splitlines()[1:]).encode()+b"\n"}))
  self.bad(lambda f:f.row_change(0,5,"RUNNING",target="explicit"))
 def test_15_positive_failure_memory_unknown_and_zero_history(self):
  f=self.fx();self.assertGreater(f.replay()["allocated_failure_GPU_seconds"],0)
  exp=f.explicit.replace(",mem=64G","");uni=f.universe.replace(",mem=64G","");r=COST.close_rows(f.dispatches,exp,uni,COST.utc(f.ledger["scope_end_utc"]));self.assertTrue(all(x["actual_memory_AllocTRES"]=="UNAVAILABLE_NOT_ZERO"for x in r["rows"]))
  zero="13266|13266|test9_unallocated_cpu|"+COST.USER+"|"+COST.USER+"|CANCELLED|0||2026-10-11T14:25:00|Unknown|Unknown|None|organ|"+str(CHECKER.R)+"\n"
  z=COST.close_rows(f.dispatches,f.explicit,f.universe+zero,COST.utc(f.ledger["scope_end_utc"]));self.assertEqual(z["actual_GPU_seconds"],r["actual_GPU_seconds"]);self.assertEqual(len(z["universe_observed_zero_unallocated_cancels"]),1)
 def test_16_strict_global_gpu_cap_two(self):
  f=self.fx();rows=f.lines[:]
  for i in range(3):
   row=rows[i].split("|");row[9]="2026-10-11T14:26:00";row[10]="2026-10-11T14:26:10";rows[i]="|".join(row)
  raw="\n".join(rows)+"\n"
  with self.assertRaisesRegex(ValueError,"cap2"):COST.close_rows(f.dispatches,raw,raw,COST.utc(f.ledger["scope_end_utc"]))
 def test_17_complete_object_types_order_and_flags_equality(self):
  for change in [lambda o:o.update(actual_GPU_seconds=2980.0),lambda o:o["rows"].reverse(),lambda o:o.update(result_manifests_read_for_cost=True),lambda o:o["rows"][0].update(raw_id="other")]:
   with self.subTest(change=change):self.bad(lambda f:change(f.graph["closure.json"]))
 def test_18_exact_saved_query_window_protocol_and_no_job_fill(self):
  f=self.fx();argv=COST.time_universe_argv(f.ledger);self.assertIn("--state=RUNNING",argv);self.assertNotIn("-j",argv);self.assertNotIn("-X",argv);self.assertNotIn("-T",argv);self.assertIn("--format="+COST.FIELDS,argv)
  for key,value in [("returncode",False),("returncode",1),("TZ","LOCAL"),("SLURM_TIME_FORMAT","relative"),("argv",argv+["-j","13260"])]:
   with self.subTest(key=key):self.bad(lambda f:f.graph["universe.command.json"].update({key:value}))
  self.bad(lambda f:f.graph.update({"empty.stderr":b"unexpected error\n"}))
 def test_19_two_scalar_result_directories_no_live_io_finally(self):
  allowed=[str(CHECKER.R/"software_fixture/e2e/design"),str(CHECKER.R/"software_fixture/e2e/evaluate")];names=("path","read","query","cpu","audit","dump");before={n:getattr(COST,n)for n in names}
  with self.assertRaisesRegex(RuntimeError,"sentinel"):
   with CHECKER.pure_cost_context(COST,allowed):
    self.assertEqual(str(COST.path(allowed[0])),allowed[0])
    for p in [str(CHECKER.R/"not_declared"),allowed[0]+"/../other",allowed[0]+"/leaf"]:
     with self.subTest(path=p),self.assertRaises(ValueError):COST.path(p)
    with self.assertRaises(ValueError):COST.read(allowed[0])
    with self.assertRaises(ValueError):COST.query("anything")
    raise RuntimeError("sentinel")
  for n in names:self.assertIs(getattr(COST,n),before[n])
 def test_20_indexed_journal_prefix_and_current_controller_binding(self):
  f=self.fx();journal_cases(f,self)
 def test_21_source_universe_pair_byte_identity_and_counts(self):
  def add_sources(x):
   rows=[x.add("source/"+n,("# "+LABEL+" "+n+"\n").encode())for n in CHECKER.FILES];x.add("own_contracts.log",b"SYNTHETIC_NEW_SOFTWARE_LOG_ONLY\\n");x.add("own_contracts.json",dict(status="PASS",tests_run=24,failures=0,errors=0,skipped=0,tested_source_files=rows,source_files=rows,log=Ref("own_contracts.log"),synthetic_fixture=LABEL))
  f=self.fx(add_sources);rows=[f.memo["source/"+n]for n in CHECKER.FILES];CHECKER.counts(f.scope,f.memo["own_contracts.json"],24,rows);CHECKER.source_set(f.scope,rows,4,CHECKER.FILES);CHECKER.pair_lists(rows,[dict(r,path=str(f.origin/"other"/Path(r["path"]).name))for r in rows],CHECKER.FILES)
  with self.assertRaises(ValueError):CHECKER.source_set(f.scope,rows[:-1],4,CHECKER.FILES)
  changed=copy.deepcopy(rows);changed[0]["sha256"]="0"*64
  with self.assertRaises(ValueError):CHECKER.pair_lists(rows,changed,CHECKER.FILES)
  with self.assertRaises(ValueError):CHECKER.input_bytes(f.scope,changed[0])
  def bad_count(x):
   add_sources(x);x.graph["own_contracts.json"]["tests_run"]=True
  bad=self.fx(bad_count)
  with self.assertRaises(ValueError):CHECKER.counts(bad.scope,bad.memo["own_contracts.json"],24)
 def test_22_json_duplicate_nonfinite_and_semantic_type(self):
  for b in [b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}',b'{"x":-Infinity}']:
   with self.subTest(raw=b),self.assertRaises(ValueError):CHECKER.parse_json(b)
  self.assertFalse(CHECKER.same_json(dict(x=1),dict(x=True)));self.assertFalse(CHECKER.same_json([1,2],[2,1]));self.assertTrue(CHECKER.same_json(dict(x=[1,None]),dict(x=[1,None])))
 def test_23_conditional_runtime_and_owned_source_before_end(self):
  runtime=READER.runtime_descriptor(str(CHECKER.R/"env/core/bin/python"));READER.verify_runtime(runtime)
  with self.assertRaises(ValueError):READER.verify_runtime(dict(runtime,resolved_sha256="0"*64))
  f=self.fx(lambda x:[x.add("original/"+n,("# "+LABEL+" "+n+"\n").encode())or None for n in CHECKER.FILES])
  original=[f.memo["original/"+n]for n in CHECKER.FILES];frozen=[]
  for r in original:
   p=f.origin/"frozen"/Path(r["path"]).name;p.parent.mkdir(exist_ok=True);p.write_bytes(Path(r["path"]).read_bytes());p.chmod(0o444);frozen.append(CHECKER.rec(p))
  CHECKER.own(original,frozen);p=Path(original[0]["path"]);p.chmod(0o600);p.write_bytes(b"source fork\n");p.chmod(0o444)
  with self.assertRaises(ValueError):CHECKER.own(original,frozen)
 def test_24_typed_output_and_controls_no_unindexed_permission(self):
  f=self.fx()
  with self.assertRaises(ValueError):f.scope.verify(dict(path=str(f.out/"unindexed_input.json"),bytes=0,sha256="0"*64))
  r=CHECKER.write_scoped(f.scope,f.out,"acceptance.json",dict(scope=LABEL,not_real_cost=True));self.assertEqual(set(p.name for p in f.out.iterdir()),{"acceptance.json"});self.assertEqual(Path(r["path"]).stat().st_mode&0o777,0o444);self.assertIn(r["path"],f.scope.proof()["fresh_output_paths"])
  with self.assertRaises(ValueError):f.new_scope()
  with self.assertRaises(ValueError):CHECKER.write_scoped(f.scope,f.root,"outside.json",{})
  f.marker["sha256"]="0"*64
  with self.assertRaises(ValueError):f.scope.after(touched_only=True)
def journal_cases(f,test):
 # Independent metadata case uses genuine restored index and declared byte-identical aliases.
 entries=[dict(submission_id="formal13260",phase="formal_generation",kind="primary",receipt_path=str(COST.FORMAL_SUB)),dict(submission_id="common13423",phase="common_review",kind="primary",receipt_path=str(f.origin/"journal_controllers/common.json"))]
 docs=[dict(schema="root-current-gpu-submission-journal.v1",authority_root=str(CHECKER.R),scope_start_utc=COST.PRIMARY_START,entries=entries[:1],previous_journal_path=None,synthetic_fixture=LABEL),dict(schema="root-current-gpu-submission-journal.v1",authority_root=str(CHECKER.R),scope_start_utc=COST.PRIMARY_START,entries=entries,previous_journal_path=str(f.origin/"journals/1.json"),synthetic_fixture=LABEL)]
 # A second tiny real package isolates journal graph; it is not an actual root ledger.
 temp=tempfile.TemporaryDirectory(prefix="root298_journal_",dir=CHECKER.S/"tmp");test.addCleanup(temp.cleanup);base=Path(temp.name);origin=base/"origin";origin.mkdir();root=base/"restore";out=root/"new"
 def put(name,obj):
  p=origin/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(CHECKER.jbytes(obj));p.chmod(0o444);return CORE.rec(p)
 formal=put("controllers/formal.json",dict(synthetic_fixture=LABEL));common=put("controllers/common.json",dict(synthetic_fixture=LABEL))
 formal_alias=dict(formal,path=str(COST.FORMAL_SUB));entries[1]["receipt_path"]=common["path"]
 docs[0]["entries"]=copy.deepcopy(entries[:1]);j1=put("journals/1.json",docs[0]);docs[1]["entries"]=copy.deepcopy(entries);docs[1]["previous_journal_path"]=j1["path"];j2=put("journals/2.json",docs[1])
 le=[{**{k:v for k,v in e.items()if k!="receipt_path"},"receipt":r}for e,r in zip(entries,[formal_alias,common])]
 closure=put("closure.json",dict(status="ROOT_SUBMISSION_JOURNAL_CHAIN_CPU_SEALED",journal_receipts=[j1,j2],final_journal=j2,controller_receipts=[formal_alias,common],entries=le,synthetic_fixture=LABEL))
 config=put("config.json",dict(synthetic_fixture=LABEL));rows=[formal,common,j1,j2,closure,config]
 validation=put("validation.json",dict(status="FINAL_DELIVERY_CONFIG_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY",authority_root=str(origin),config=config,phase_id=LABEL,files={Path(r["path"]).relative_to(origin).as_posix():dict(receipt=r,classification="AUDIT")for r in rows},conditional_inference_dependencies=[]))
 CORE.package(validation["path"],base/"pkg",1);pp=base/"pkg/packaging_receipt.json";pp.chmod(0o444);CORE.extract(pp,root);(root/"RESTORE_HASH_ACCEPTANCE.json").chmod(0o444);pkg=CHECKER.parse_json(pp.read_bytes())
 aliases=dict(aliases=[dict(original=formal_alias,archived=formal,status="READONLY_BYTE_IDENTICAL_ALIAS")]);scope=READER.StrictIndex(pkg,root,out,aliases=aliases,controls=[CORE.rec(pp),CORE.rec(root/"RESTORE_HASH_ACCEPTANCE.json")])
 ledger=dict(journal_closure=closure,entries=le);CHECKER.indexed_journal(scope,COST,ledger);scope.after(touched_only=True)
 # Exact saved prefix/current identity may never be replaced by a same-size live file.
 for changed in [dict(ledger,entries=list(reversed(le))),dict(ledger,entries=[dict(le[0],receipt=common),le[1]])]:
  with test.assertRaises(ValueError):CHECKER.indexed_journal(scope,COST,changed)
 subset=copy.deepcopy(pkg);subset["manifest"]=[r for r in subset["manifest"]if r["receipt"]["path"]!=j1["path"]]
 missing=READER.StrictIndex(subset,root,out,aliases=aliases,controls=[CORE.rec(pp),CORE.rec(root/"RESTORE_HASH_ACCEPTANCE.json")])
 with test.assertRaises(ValueError):CHECKER.indexed_journal(missing,COST,ledger)
