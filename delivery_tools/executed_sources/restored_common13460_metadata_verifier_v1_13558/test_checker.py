#!/usr/bin/env python3
"""Thirty-two actual CPU synthetic-metadata fixtures; genuine unchanged core package/extract."""
import copy,hashlib,json,os,tempfile,unittest
from pathlib import Path
CHECKER=None;READER=None;CORE=None
class Ref:
 def __init__(self,name,field=None):self.name=name;self.field=field
class Fixture:
 def __init__(self,owner,mutate=None):
  self.m=CHECKER;self.temp=tempfile.TemporaryDirectory(prefix="restored_common13460_fixture_",dir=self.m.S/"tmp");owner.addCleanup(self.temp.cleanup)
  self.base=Path(self.temp.name);self.origin=self.base/"origin";self.origin.mkdir();self.root=self.base/"restored";self.out=self.root/"metadata_out";self.g={};self.memo={}
  self.canonical=str(self.origin/"controller/root_submission.json");self.j6path=str(self.origin/"journal/0006_common_controller_metadata_amendment_13460.json")
  def add(name,value):self.g[name]=value;return Ref(name)
  self.add=add
  own=[add("source/frozen/"+n,b"# SYNTHETIC_METADATA_FIXTURE_ONLY "+n.encode()+b"\n")for n in self.m.AMEND_NAMES]
  original=[add("source/original/"+n,b"# SYNTHETIC_METADATA_FIXTURE_ONLY "+n.encode()+b"\n")for n in self.m.AMEND_NAMES]
  cost=[add("source/cost/"+n,b"# SYNTHETIC_METADATA_FIXTURE_ONLY COST "+n.encode()+b"\n")for n in sorted(self.m.COST_NAMES)]
  common=[add("source/common/"+n,b"# SYNTHETIC_METADATA_FIXTURE_ONLY COMMON "+n.encode()+b"\n")for n in sorted(self.m.COMMON_NAMES)]
  entry=next(r for r in common if r.name.endswith("/common_review_successor.py"));launcher=next(r for r in common if r.name.endswith("/common_review_gpu.sbatch"))
  indices=list(range(268));pre=add("preflight.json",dict(status="COMMON_SUCCESSOR_CPU_PREFLIGHT_ACCEPTED_ROOT_PENDING_ONLY_GPU_SUBMISSION_REQUIRED",no_inference=True,root_submission_performed=False,root_pending_job_indices=indices,source=dict(successor=common),synthetic_fixture=True))
  paths=lambda ref:str(self.origin/ref.name)
  argv=["sbatch","--parsable","--export=ALL,COMMON_SUCCESSOR_ENTRY="+paths(entry),"--array="+",".join(map(str,indices))+"%2",paths(launcher),paths(pre)]
  old=dict(schema="formal_common_root_submission.v1",array_job_id="13423",concurrency_cap=2,indices=indices,raw_stdout="13423\n",raw_stderr="",entry=entry,launcher=launcher,preflight=pre,submit_argv=argv,scientific_settings_unchanged=True,synthetic_fixture="SYNTHETIC_METADATA_FIXTURE_ONLY")
  oldr=add("archive/original.json",old);new=copy.deepcopy(old);new.update(raw_sbatch_stdout="13423\n",raw_sbatch_stderr="")
  newr=add("controller/root_submission.json",new);candidate=add("archive/candidate.json",copy.deepcopy(new))
  fact=add("claim/submit_receipt.json",dict(returncode=0,stdout="13423\n",stderr="",argv=argv,synthetic_fixture=True))
  claims=[fact,add("claim/progress.json",dict(synthetic_fixture=True)),add("claim/request.json",dict(synthetic_fixture=True))]
  others=[add("other/formal.json",dict(synthetic_fixture=True)),add("other/design.json",dict(synthetic_fixture=True)),add("other/evaluate.json",dict(synthetic_fixture=True))]
  previous=add("previous13315.json",dict(schema="root-controller-metadata-amendment-CPU-qualification.v1",status="ROOT_ACTUAL_EVALUATE_CONTROLLER_SINGLE_DESCRIPTOR_ADDITION_CPU_ACCEPTED",actual_job_id="13311",allocation=dict(slurm_job_id="13315",allocated_CPU_count=1,allocated_GPU_count=0),synthetic_fixture="SYNTHETIC_METADATA_FIXTURE_ONLY"))
  entries=[dict(submission_id=i,phase=p,kind="primary",receipt_path=paths(r))for i,p,r in zip(["formal13260","e2e_design_13304","e2e_evaluate_13311","formal_common_13423"],["formal_generation","reference_free_e2e","reference_free_e2e","common_review"],others+[newr])]
  j5=add("journal/0005.json",dict(schema="root-current-gpu-submission-journal.v1",authority_root=str(self.origin),scope_start_utc="2026-10-11T14:25:00Z",previous_journal_path=str(self.origin/"journal/0004.json"),entries=entries,metadata_only_controller_amendment_CPU_qualifications=[previous]))
  log=add("contracts.log",b"SYNTHETIC_METADATA_FIXTURE_ONLY saved20\n")
  counts=add("contracts.json",dict(status="PASS",tests_run=20,failures=0,errors=0,skipped=0,log=log,tested_source_files=own))
  syntax=add("syntax.json",dict(compile_owned_Python=True,bash_returncode=0,bash_argv=["bash","-n",paths(own[0]).rsplit("/",1)[0]+"/amendment_cpu.sbatch"],source_files=own))
  allocation=dict(job_id="13460",allocated_CPUs=1,allocated_GPUs=0,synthetic_fixture=True)
  snapshot=add("snapshot.json",dict(original_executing_sources=original,frozen_source_files=own,allocation=allocation,syntax=syntax))
  ca_counts=add("cost_counts.json",dict(status="PASS",tests_run=76,failures=0,errors=0,log=log));co_counts=add("common_counts.json",dict(status="PASS",tests_run=58,failures=0,errors=0,log=log))
  cost_a=add("cost_a.json",dict(status="ROOT_GPU_COST_AUDITOR_SOFTWARE_CPU_ACCEPTED",source=cost,contracts=ca_counts))
  common_a=add("common_a.json",dict(status="COMMON_SUCCESSOR_SOFTWARE_SOURCE_CPU_ACCEPTED_FUTURE_FORMAL_PREPARATION_PENDING",source=dict(successor=common),contracts=co_counts))
  old_identity=dict(logical_original_path=self.canonical,observed_bytes=Ref(oldr.name,"bytes"),observed_sha256=Ref(oldr.name,"sha256"),readonly_archive=oldr)
  parent=dict(path=str(self.origin/"controller"),device=1,inode=22,uid=23,gid=23,mode=0o555)
  transaction=dict(logical_target_path=self.canonical,committed=True,current_new_verified=True,parent_mode_restored=True,rollback_performed=False,rollback_conflict=False,cleanup_errors=[],replacement_inode=42,replacement_metadata=dict(path=self.canonical,size=Ref(newr.name,"bytes"),mode=0o444,inode=42),parent_before=copy.deepcopy(parent),parent_after=copy.deepcopy(parent))
  txn=add("transaction.json",dict(schema="common13423-addition-only-atomic-transaction.v1",scope="METADATA_ONLY_NOT_SCIENCE_COST_OR_NEW_GPU",old_identity=old_identity,candidate_archive=candidate,transaction=transaction))
  probes=dict(cost=dict(job_id="13423",indices=indices,expected_allocation_count=268,preflight=pre,launcher=launcher),common=dict(job_id="13423",launcher=launcher),no_suites_rerun=True)
  diff=add("amendment.json",dict(schema="common13423-controller-metadata-addition-only.v1",scope="METADATA_ONLY_NOT_SCIENCE_COST_OR_NEW_GPU",old_identity=old_identity,new_canonical=newr,candidate_archive=candidate,transaction_receipt=txn,transaction=transaction,actual_factual_submit_receipt=fact,added_fields={k:new[k]for k in self.m.ADD},all_original_fields_exactly_preserved=True,legacy_COST_expected_rejection=dict(type="ValueError",message="Actual raw parsable submission differs/missing",expected=True),legacy_Common_contract_PASS=True,proposed_contracts=copy.deepcopy(probes),current_contracts=copy.deepcopy(probes),journal_entries_unchanged=entries,unchanged_three_claim_files=claims,unchanged_three_other_GPU_controllers=others))
  producer={}
  for key,jid,name,cpu in(("cost","13277","ppi_root_gpu_cost_cpu",1),("common","13269","ppi_common_successor_cpu",2)):
   raw="|".join([jid,name,self.m.USER,self.m.USER,"organ","COMPLETED","0:0","4","cpu="+str(cpu)+",node=1"])+"\n"
   capture=add("producer_"+jid+".json",dict(returncode=0,stdout=raw,stderr="",synthetic_fixture=True))
   producer[key]=dict(actual_capture=capture,record=dict(raw_line=raw.strip(),elapsed_seconds=4,allocated_CPUs=cpu,allocated_GPUs=0))
  a=dict(schema="common13423-controller-metadata-amendment-acceptance.v1",status="COMMON13423_ADDITION_ONLY_CONTROLLER_METADATA_CPU_ACCEPTED_NOT_SCIENCE_COST_OR_NEW_GPU",scope="METADATA_ONLY_NOT_SCIENCE_COST_OR_NEW_GPU",actual_CPU_job_id="13460",allocation=allocation,old_identity=old_identity,new_canonical=newr,candidate_archive=candidate,transaction_receipt=txn,amendment=diff,contracts=counts,source_snapshot=snapshot,owned_source_syntax=syntax,source_files=own,original_executing_sources=original,original_source_entry=original[0],executing_frozen_entry=own[0],whole_OWN_source_n=4,external_contract_source_files=cost+common,accepted_COST_software=cost_a,accepted_Common_software=common_a,actual_producer_terminal=producer,preflight=pre,factual_submit_receipt=fact,journal_0005_unchanged=j5,unchanged_three_claim_files=claims,unchanged_three_other_GPU_controllers=others,previous13315_amendment_preserved=previous,declared_root_GPU_submission_journal_entries_before_and_after=entries,only_added_keys=list(self.m.ADD),synthetic_fixture="SYNTHETIC_METADATA_FIXTURE_ONLY")
  for k in("compiled_owned_Python","bash_syntax_passed","original_source_prepost_equal","original_and_frozen_sources_byte_identical","all_control_prepost_bytes_and_metadata_equal","original_all_fields_preserved","canonical_parent_mode_restored","no_journal_write"):a[k]=True
  for k in("new_GPU_submission","technical_GPU_rerun","science_accepted","cost_closure_accepted","source_or_settings_changed","default_changed","Git_changed","ACTIVE_changed"):a[k]=False
  ar=add("acceptance13460.json",a)
  self.g["journal/0006_common_controller_metadata_amendment_13460.json"]=dict(schema="root-current-gpu-submission-journal.v1",authority_root=str(self.origin),scope_start_utc="2026-10-11T14:25:00Z",previous_journal_path=paths(j5),entries=entries,metadata_only_controller_amendment_CPU_qualifications=[previous],metadata_only_common_controller_amendment_CPU_qualifications=[ar])
  terminal=dict(argv=["sacct","-j","13460","--allocations","--noheader","--parsable2","--format=JobID,JobName%128,User,Account,Partition,State,ExitCode,ElapsedRaw,AllocCPUS,AllocTRES"],returncode=0,stdout="13460|test9_common13423_metadata_amendment_v1|"+self.m.USER+"|"+self.m.USER+"|organ|COMPLETED|0:0|3|1|cpu=1,node=1\n",stderr="")
  #13 synthetic copied metadata rows. These are DATA observations, not real jobs.
  seal_items=[add("seal_file_"+str(i)+".txt",b"SYNTHETIC_METADATA_FIXTURE_ONLY\n")for i in range(13)]
  seal_rows=[dict(path=paths(r),bytes=Ref(r.name,"bytes"),inode=100+i,mtime_ns=1,mode="0o444")for i,r in enumerate(seal_items)]
  seal=add("terminal_seal.json",dict(schema="common-metadata-amendment-terminal-metadata-only-seal.v1",status="ACTUAL_TERMINAL_METADATA_READBACK_PASS_NOT_NEW_COST_OR_SCIENCE_ACCEPTANCE",actual_acceptance_CPU_stdout_descriptor=ar,current_canonical_descriptor_from_ownedCPU=newr,original_5096_archive_from_ownedCPU=oldr,actual_terminal=terminal,file_count=13,files_before=copy.deepcopy(seal_rows),files_after=copy.deepcopy(seal_rows),bytes_inode_mtime_unchanged=True,only_two_added_fields=True,no_new_GPU_submission=True,full_cost_and_science_pending=True,synthetic_fixture=True))
  # Separate synthetic new32 proof uses the same production data consumer.
  # It never claims the current own test job has completed.
  checker_rows=[add("new_checker/frozen/"+n,b"# SYNTHETIC_METADATA_FIXTURE_ONLY NEWCHECKER "+n.encode()+b"\n")for n in self.m.FILES]
  checker_original=[add("new_checker/original/"+n,b"# SYNTHETIC_METADATA_FIXTURE_ONLY NEWCHECKER "+n.encode()+b"\n")for n in self.m.FILES]
  new_alloc=dict(job_id="12345",allocated_CPUs=1,allocated_GPUs=0,synthetic_fixture=True)
  new_counts=add("new_checker/contracts.json",dict(status="PASS",tests_run=32,failures=0,errors=0,skipped=0,source_files=checker_rows,tested_source_files=checker_rows,log=log,genuine_unchanged_core_package_extract=True))
  new_snap=add("new_checker/snapshot.json",dict(frozen_source_files=checker_rows,original_executing_sources=checker_original,compile_owned_Python=True,bash_returncode=0,allocation=new_alloc,bash_argv=["bash","-n",paths(checker_rows[0]).rsplit("/",1)[0]+"/checker_cpu.sbatch"]))
  new_sw=add("new_checker/software.json",dict(actual_CPU_job_id="12345",allocation=new_alloc,source_files=checker_rows,original_executing_sources=checker_original,contracts=new_counts,source_snapshot=new_snap,synthetic_fixture="SYNTHETIC_METADATA_FIXTURE_ONLY"))
  self.new_sw_ref=new_sw
  add("steps/24_benchmark_delivery/submissions/restored_common13460_metadata_software_12345_actual_terminal_seal/receipt.json",dict(schema="restored-common13460-metadata-software-terminal-seal.v1",status="ACTUAL_TERMINAL_SOFTWARE_METADATA_READBACK_PASS_NOT_REAL_RESTORE",software_acceptance_CPU_stdout_descriptor=new_sw,source_files=checker_rows,metadata_only=True,actual_terminal=dict(argv=["sacct","-X","-n","-P","-j","12345","--format=JobID,JobName%128,User%64,Account%64,Partition%64,State,ExitCode,ElapsedRaw,AllocTRES"],returncode=0,stdout="12345|"+self.m.JOB_NAME+"|"+self.m.USER+"|"+self.m.USER+"|organ|COMPLETED|0:0|1|cpu=1,node=1\n",stderr=""),synthetic_fixture=True))
  if mutate:mutate(self.g)
  for name in self.g:self.materialize(name)
  config=add("config.json",dict(resource_aliases=None,synthetic_fixture=True));self.materialize(config.name)
  validation=dict(status="FINAL_DELIVERY_CONFIG_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY",authority_root=str(self.origin),config=self.memo[config.name],phase_id="SYNTHETIC_METADATA_FIXTURE_ONLY",files={name:dict(receipt=r,classification="AUDIT")for name,r in self.memo.items()},conditional_inference_dependencies=[])
  vp=self.origin/"validation.json";vp.write_bytes(self.m.jbytes(validation));vp.chmod(0o444)
  CORE.package(str(vp),str(self.base/"package"),1)
  self.package_path=self.base/"package/packaging_receipt.json";self.package_path.chmod(0o444)
  CORE.extract(str(self.package_path),str(self.root))
  (self.root/"RESTORE_HASH_ACCEPTANCE.json").chmod(0o444)
  self.pkg=self.m.parse_json(self.package_path.read_bytes());self.package_receipt=READER.checksum(self.package_path);self.marker=READER.checksum(self.root/"RESTORE_HASH_ACCEPTANCE.json")
  self.policy=dict(acceptance=self.memo[ar.name],canonical=self.canonical,journal6=self.j6path,terminal_seal=str(self.origin/seal.name),authority=str(self.origin),old_bytes=self.memo[oldr.name]["bytes"],new_bytes=self.memo[newr.name]["bytes"])
  self.scope=self.new_scope()
 def resolve(self,x):
  if isinstance(x,Ref):
   r=self.materialize(x.name);return r[x.field]if x.field else r
  if isinstance(x,dict):return{k:self.resolve(v)for k,v in x.items()}
  if isinstance(x,list):return[self.resolve(v)for v in x]
  return x
 def materialize(self,name):
  if name in self.memo:return self.memo[name]
  v=self.g[name];b=v if isinstance(v,bytes)else self.m.jbytes(self.resolve(v));p=self.origin/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);p.chmod(0o444)
  r=dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest());self.memo[name]=r;return r
 def new_scope(self,pkg=None,aliases=None):
  return READER.StrictIndex(pkg or self.pkg,self.root,self.out,aliases=aliases,controls=[self.package_receipt,self.marker])
 def check(self):return self.m.validate_metadata(self.scope,self.policy)
 def omit(self,logical):
  p=copy.deepcopy(self.pkg);p["manifest"]=[x for x in p["manifest"]if x["receipt"]["path"]!=logical];self.scope=self.new_scope(p)
 def poison_live(self):
  for r in self.memo.values():
   p=Path(r["path"]);p.chmod(0o600);p.write_bytes(b"POISONED_LIVE_NOT_VALID_METADATA\n");p.chmod(0o444)
class MetadataIndexContracts(unittest.TestCase):
 def fx(self,mutation=None):return Fixture(self,mutation)
 def bad(self,mutation):
  f=self.fx(mutation)
  with self.assertRaises((ValueError,KeyError)):f.check()
 def test_01_genuine_core_package_extract_whole_positive(self):
  f=self.fx();sr=f.memo[f.new_sw_ref.name];sw=CHECKER.input_json(f.scope,sr);terminal=CHECKER.new_software_evidence(f.scope,sw,sw["source_files"],sr);self.assertIn("terminal_seal",terminal["path"])
  r=f.check();f.scope.after(touched_only=True);ar=CHECKER.write_scoped_output(f.scope,f.out,r);self.assertEqual(Path(ar["path"]).parent,f.out);self.assertEqual(set(x.name for x in f.out.iterdir()),{"acceptance.json"});saved=CHECKER.parse_json((f.out/"acceptance.json").read_bytes());self.assertIn(str(f.out/"acceptance.json"),saved["strict_restored_index_proof"]["fresh_output_paths"]);self.assertTrue(r["only_two_aliases"]);self.assertFalse(r["scientific_recomputation_performed"]);self.assertGreater(len(f.scope.reads),40)
 def test_02_live_poison_positive_no_live_fallback(self):
  f=self.fx();f.poison_live();self.assertEqual(f.check()["status"],CHECKER.CONTENT);f.scope.after(touched_only=True)
 def test_03_missing_indexed_old_with_live_file_present(self):
  f=self.fx();old=f.memo["archive/original.json"];self.assertTrue(Path(old["path"]).exists());f.omit(old["path"])
  with self.assertRaisesRegex(ValueError,"exact index/alias"):f.check()
 def test_04_missing_indexed_source_live_poison(self):
  f=self.fx();p=f.memo["source/frozen/amendment.py"]["path"];f.omit(p);f.poison_live()
  with self.assertRaisesRegex(ValueError,"exact index/alias"):f.check()
 def test_05_wrong_sha_full_identity(self):
  f=self.fx();f.policy["acceptance"]=dict(f.policy["acceptance"],sha256="0"*64)
  with self.assertRaisesRegex(ValueError,"exact index/alias"):f.check()
 def test_06_duplicate_index_path_rejected(self):
  f=self.fx();pkg=copy.deepcopy(f.pkg);pkg["manifest"].append(copy.deepcopy(pkg["manifest"][0]))
  with self.assertRaisesRegex(ValueError,"Duplicate"):f.new_scope(pkg)
 def test_07_conflicting_index_identity_rejected(self):
  f=self.fx();pkg=copy.deepcopy(f.pkg);row=copy.deepcopy(pkg["manifest"][0]);row["receipt"]["sha256"]="0"*64;pkg["manifest"].append(row)
  with self.assertRaisesRegex(ValueError,"Duplicate"):f.new_scope(pkg)
 def test_08_declared_byte_identical_alias_positive(self):
  f=self.fx();old=f.memo["archive/original.json"];archive=dict(old,path=str(f.origin/"alias/original.json"))
  aliases=dict(aliases=[dict(original=archive,archived=old,status="READONLY_BYTE_IDENTICAL_ALIAS")])
  scope=f.new_scope(aliases=aliases);self.assertEqual(scope.verify(archive).read_bytes(),scope.verify(old).read_bytes())
 def test_09_alias_changes_bytes_rejected(self):
  f=self.fx();old=f.memo["archive/original.json"];aliases=dict(aliases=[dict(original=dict(old,path=str(f.origin/"alias/bad.json"),bytes=old["bytes"]+1),archived=old,status="READONLY_BYTE_IDENTICAL_ALIAS")])
  with self.assertRaisesRegex(ValueError,"byte-identical"):f.new_scope(aliases=aliases)
 def test_10_lexical_traversal_absolute_and_empty_rejected(self):
  f=self.fx()
  for p in [str(f.origin)+"/../outside",str(f.origin)+"//a",str(f.origin)+"/./a"]:
   with self.subTest(p=p),self.assertRaises(ValueError):f.scope.verify(dict(path=p,bytes=0,sha256="0"*64))
 def test_11_restored_leaf_symlink_rejected(self):
  f=self.fx();r=f.memo["archive/original.json"];p=f.root/"archive/original.json";p.unlink();p.symlink_to(r["path"])
  with self.assertRaisesRegex(ValueError,"nonsymlink"):f.check()
  f2=self.fx();original=f2.root/"archive";real=f2.base/"real_archive";original.rename(real);original.symlink_to(real,target_is_directory=True)
  with self.assertRaisesRegex(ValueError,"nonsymlink"):f2.check()
  f3=self.fx();real3=f3.base/"real_restored";f3.root.rename(real3);f3.root.symlink_to(real3,target_is_directory=True)
  with self.assertRaises(ValueError):f3.new_scope()
 def test_12_writable_original_restored_input_rejected(self):
  f=self.fx();(f.root/"archive/original.json").chmod(0o644)
  with self.assertRaisesRegex(ValueError,"readonly"):f.check()
 def test_13_postread_bytes_drift_rejected(self):
  f=self.fx();f.check();p=f.root/"archive/original.json";p.chmod(0o600);p.write_bytes(b"CHANGED\n");p.chmod(0o444)
  with self.assertRaisesRegex(ValueError,"bytes differ"):f.scope.after(touched_only=True)
 def test_14_only_two_alias_keys_rejected(self):
  self.bad(lambda g:[g[n].update(extra_key=True)for n in("controller/root_submission.json","archive/candidate.json")])
 def test_15_original_field_type_fork_rejected(self):
  self.bad(lambda g:[g[n].update(concurrency_cap=2.0)for n in("controller/root_submission.json","archive/candidate.json")])
 def test_16_original_argv_list_order_fork_rejected(self):
  self.bad(lambda g:[g[n]["submit_argv"].reverse()for n in("controller/root_submission.json","archive/candidate.json")])
 def test_17_raw_alias_mismatch_rejected(self):
  self.bad(lambda g:[g[n].update(raw_sbatch_stdout="13423")for n in("controller/root_submission.json","archive/candidate.json")])
 def test_18_factual_rc_and_stdout_rejected(self):
  for key,value in [("returncode",False),("returncode",1),("stdout","other\n")]:
   with self.subTest(key=key,value=value):self.bad(lambda g:g["claim/submit_receipt.json"].update({key:value}))
 def test_19_A_scope_or_new_GPU_claim_rejected(self):
  self.bad(lambda g:g["acceptance13460.json"].update(science_accepted=True))
 def test_20_source_fork_and_whole_count_rejected(self):
  self.bad(lambda g:g["acceptance13460.json"]["source_files"].pop())
 def test_21_owned_counts_and_duplicate_JSON_nonfinite(self):
  self.bad(lambda g:g["contracts.json"].update(tests_run=21))
  for b in [b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}']:
   with self.subTest(raw=b),self.assertRaises(ValueError):CHECKER.parse_json(b)
 def test_22_compile_snapshot_source_fork_rejected(self):
  self.bad(lambda g:g["syntax.json"].update(compile_owned_Python=False))
 def test_23_transaction_rollback_and_inode_rejected(self):
  self.bad(lambda g:g["transaction.json"]["transaction"].update(rollback_performed=True))
 def test_24_proposed_vs_actual_protocol_fork_rejected(self):
  self.bad(lambda g:g["amendment.json"]["current_contracts"]["cost"].update(expected_allocation_count=267))
 def test_25_J6_previous_and_universe_order_rejected(self):
  self.bad(lambda g:g["journal/0006_common_controller_metadata_amendment_13460.json"].update(previous_journal_path="wrong"))
 def test_26_J6_separate13460_not13315_rejected(self):
  self.bad(lambda g:g["journal/0006_common_controller_metadata_amendment_13460.json"].update(metadata_only_common_controller_amendment_CPU_qualifications=[Ref("previous13315.json")]))
 def test_27_J6_ownSHA_ambiguity_rejected(self):
  f=self.fx();r=f.memo["journal/0006_common_controller_metadata_amendment_13460.json"];other=dict(r,path=str(f.origin/"alias/j6.json"))
  # Same logical path with a second hash cannot become a sha-less selection.
  f.scope.paths[r["path"]].append((r["path"],r["bytes"],"0"*64))
  with self.assertRaisesRegex(ValueError,"unambiguous"):f.check()
 def test_28_missing_terminal_seal_no_live_rescue(self):
  f=self.fx();f.omit(f.policy["terminal_seal"])
  with self.assertRaisesRegex(ValueError,"unambiguous"):f.check()
 def test_29_terminal_state_or_GPU_rejected(self):
  self.bad(lambda g:g["terminal_seal.json"]["actual_terminal"].update(stdout=g["terminal_seal.json"]["actual_terminal"]["stdout"].replace("|COMPLETED|","|FAILED|")))
 def test_30_package_marker_control_root_and_output_guards(self):
  f=self.fx()
  with self.assertRaises(ValueError):CHECKER.restore_boundary(f.pkg,f.origin,f.origin/"out",str(f.origin))
  with self.assertRaises(ValueError):f.scope.verify(dict(path=str(f.out/"unindexed.json"),bytes=0,sha256="0"*64))
  marker=CHECKER.parse_json((f.root/"RESTORE_HASH_ACCEPTANCE.json").read_bytes());CHECKER.extraction_marker_guard(f.pkg,f.root,f.package_receipt,marker,str(f.origin))
  for key,value in [("package",dict(f.package_receipt,sha256="0"*64)),("files_verified",0),("restore_root",str(f.origin))]:
   wrong=copy.deepcopy(marker);wrong[key]=value
   with self.subTest(marker_key=key),self.assertRaisesRegex(ValueError,"extraction control"):CHECKER.extraction_marker_guard(f.pkg,f.root,f.package_receipt,wrong,str(f.origin))
  f.out.mkdir()
  with self.assertRaisesRegex(ValueError,"absent"):f.new_scope()
 def test_31_missing_claim_proof_and_primary13315_list_rejected(self):
  f=self.fx();f.omit(f.memo["claim/progress.json"]["path"])
  with self.assertRaisesRegex(ValueError,"exact index/alias"):f.check()
  f2=self.fx();sr=f2.memo[f2.new_sw_ref.name];sw=CHECKER.input_json(f2.scope,sr)
  path=str(f2.origin/"steps/24_benchmark_delivery/submissions/restored_common13460_metadata_software_12345_actual_terminal_seal/receipt.json");f2.omit(path);f2.poison_live()
  with self.assertRaisesRegex(ValueError,"unambiguous"):CHECKER.new_software_evidence(f2.scope,sw,sw["source_files"],sr)
  for field in("source_files","tested_source_files"):
   f3=self.fx(lambda g:g["new_checker/contracts.json"].pop(field));sr3=f3.memo[f3.new_sw_ref.name];sw3=CHECKER.input_json(f3.scope,sr3)
   with self.subTest(missing=field),self.assertRaisesRegex(ValueError,"producer/source"):CHECKER.new_software_evidence(f3.scope,sw3,sw3["source_files"],sr3)
 def test_32_controls_are_readonly_no_scientific_acceptance(self):
  f=self.fx();f.marker["sha256"]="0"*64
  with self.assertRaisesRegex(ValueError,"bytes differ"):f.scope.after(touched_only=True)

  runtime=READER.runtime_descriptor(str(CHECKER.R/"env/core/bin/python"));READER.verify_runtime(runtime)
  drift=dict(runtime,resolved_sha256="0"*64)
  with self.assertRaisesRegex(ValueError,"drifted"):READER.verify_runtime(drift)
