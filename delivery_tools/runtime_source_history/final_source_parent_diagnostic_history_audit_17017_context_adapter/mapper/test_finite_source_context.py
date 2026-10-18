"""Sixteen prepared software-only contracts. Run only after actual pureCPU Slurm guard."""
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
import finite_source_context as m
class FiniteAliasContracts(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.addCleanup(self.temp.cleanup)
  self.rows=[]
  for i in range(8):
   p=self.root/("saved_"+str(i)+".py");p.write_bytes(("VALUE="+str(i)+"\n").encode());p.chmod(0o444)
   r=self.receipt(p);original={**r,"path":str(self.root/("old_"+str(i)+".py"))}
   self.rows.append(dict(original=original,canonical=r,basis="EXISTING_READONLY_RUNTIME_SNAPSHOT"))
  parent=self.root/"parent.json";obj={("e"+str(i)):self.rows[i%8]["original"]for i in range(12)}
  parent.write_text(json.dumps(obj));parent.chmod(0o444);self.parent=self.receipt(parent)
  self.edges=[dict(source_parent=self.parent,parent_canonical_receipt=self.parent,source_field=["e"+str(i)],original=self.rows[i%8]["original"])for i in range(12)]
  self.declared=dict(aliases=copy.deepcopy(self.rows),edges=copy.deepcopy(self.edges))
 def receipt(self,p):
  data=p.read_bytes();return dict(path=str(p),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 def verify(self,path,r):
  p=Path(path)
  if p.is_symlink()or p.resolve()!=p or not p.is_file()or p.stat().st_mode&0o222 or self.receipt(p)!=r:raise ValueError("Readonly exact source drift")
  return p
 def proof(self,row):
  return dict(classification=row["basis"],canonical_receipt=row["canonical"],current_execution_authorized=False)
 def policy(self,rows=None,edges=None,provenance=None):
  return m.FiniteOperativeSourceAliases(rows or self.rows,edges or self.edges,self.verify,lambda p:json.loads(Path(p).read_text()),provenance or self.proof,self.declared)
 def context(self):return dict(logical=self.parent,physical=self.parent)
 def observe(self,p):
  for e in self.edges:p.authorize(e["original"],self.context(),e["source_field"])
 def test_real_exact_eight_twelve_closure(self):
  p=self.policy();self.observe(p);v=p.require_complete();self.assertEqual(v["source_identity_n"],8);self.assertEqual(v["original_edge_n"],12);self.assertFalse(v["current_execution_authorized"])
 def test_pending_bbf_blocks_before_partial_alias(self):
  rows=copy.deepcopy(self.rows);rows[1]["canonical"]=None
  with self.assertRaisesRegex(ValueError,"unresolved"):self.policy(rows)
 def test_unknown_ninth_source_rejected(self):
  rows=copy.deepcopy(self.rows);rows.append(copy.deepcopy(rows[0]))
  with self.assertRaisesRegex(ValueError,"eight"):self.policy(rows)
 def test_duplicate_source_identity_rejected(self):
  rows=copy.deepcopy(self.rows);rows[1]=copy.deepcopy(rows[0])
  with self.assertRaisesRegex(ValueError,"duplicate"):self.policy(rows)
 def test_unknown_source_not_given_alias(self):
  p=self.policy();r={**self.rows[0]["original"],"path":str(self.root/"unknown.py")}
  self.assertIsNone(p.authorize(r,self.context(),["e0"]))
 def test_wrong_parent_identity_denied_before_dedup(self):
  p=self.policy();p.authorize(self.rows[0]["original"],self.context(),["e0"])
  context=self.context();context["logical"]={**self.parent,"sha256":"f"*64}
  with self.assertRaisesRegex(ValueError,"Unknown parent"):p.authorize(self.rows[0]["original"],context,["e0"])
 def test_wrong_field_denied_after_seen_source(self):
  p=self.policy();p.authorize(self.rows[0]["original"],self.context(),["e0"])
  with self.assertRaisesRegex(ValueError,"Unknown parent"):p.authorize(self.rows[0]["original"],self.context(),["e1"])
 def test_changed_canonical_parent_denied(self):
  p=self.policy();context=self.context();context["physical"]={**self.parent,"path":str(self.root/"alias_parent.json")}
  with self.assertRaisesRegex(ValueError,"canonical identity"):p.authorize(self.rows[0]["original"],context,["e0"])
 def test_source_byte_drift_denied(self):
  p=Path(self.rows[0]["canonical"]["path"]);p.chmod(0o644);p.write_bytes(b"DIFFERENT");p.chmod(0o444)
  with self.assertRaisesRegex(ValueError,"drift"):self.policy()
 def test_writable_source_denied(self):
  Path(self.rows[0]["canonical"]["path"]).chmod(0o644)
  with self.assertRaisesRegex(ValueError,"drift"):self.policy()
 def test_selected_physical_path_fork_denied(self):
  rows=copy.deepcopy(self.rows);rows[0]["canonical"]["path"]=str(self.root/"another.py")
  with self.assertRaisesRegex(ValueError,"Selected literal"):self.policy(rows)
 def test_all_edges_observed_required(self):
  p=self.policy();p.authorize(self.rows[0]["original"],self.context(),["e0"])
  with self.assertRaisesRegex(ValueError,"All twelve"):p.require_complete()
  self.observe(p);parent=Path(self.parent["path"]);parent.chmod(0o644);parent.write_text("{}");parent.chmod(0o444)
  with self.assertRaisesRegex(ValueError,"drift"):p.require_complete()
 def test_permission_table_fork_denied(self):
  edges=copy.deepcopy(self.edges);edges[0]["source_field"]=["different"]
  with self.assertRaisesRegex(ValueError,"twelve"):self.policy(edges=edges)
 def test_source_provenance_false_or_execution_authority_denied(self):
  for value in ({},dict(classification=self.rows[0]["basis"],canonical_receipt=self.rows[0]["canonical"],current_execution_authorized=True)):
   with self.subTest(value=value):
    with self.assertRaisesRegex(ValueError,"provenance"):self.policy(provenance=lambda row:value)
 def test_recorded_chain_inverse_forward_and_no_execution(self):
  tuples=[["OLD%02d"%i,"NEW%02d"%i]for i in range(12)]
  script=("s=common.read_text()\n"+"".join("s=s.replace(%r,%r)\n"%(old,new)for old,new in tuples)+"common.write_text(s)\n").encode()
  proof=m.independent_recorded_replay("|".join(new for old,new in tuples).encode(),"|".join(old for old,new in tuples).encode(),script,tuples)
  self.assertTrue(proof["forward_equals_frozen_bytes"]);self.assertFalse(proof["freezer_executed"]);self.assertFalse(proof["reconstructed_source_executed"])
 def test_recorded_replay_wrong_anchors_nonliteral_duplicate_and_bytes_denied(self):
  cases=[(b"x=x.replace('A','B')\n",b"C",b"A",[["A","B"]]),(b"x=x.replace(a,b)\n",b"B",b"A",[["A","B"]]),(b"x=x.replace('A','B')\ny=y.replace('A','B')\n",b"B",b"A",[["A","B"]]),(b"x=x.replace('A','B')\n",b"B",b"AA",[["A","B"]])]
  for script,frozen,original,tuples in cases:
   with self.subTest(script=script):
    with self.assertRaises(ValueError):m.independent_recorded_replay(frozen,original,script,tuples)


class SourceRecoveryProofContracts(unittest.TestCase):
 """Independent software fixtures: source bytes, literal grammar, saved proof boundaries."""
 def common(self):
  pairs=[["OLD%02d"%i,"NEW%02d"%i]for i in range(12)]
  source="s=common.read_text()\n"+"".join("s=s.replace(%r,%r)\n"%tuple(p)for p in pairs)+"common.write_text(s)\n"
  return pairs,source
 def terminal(self,state="COMPLETED",exit_code="0:0",tres="cpu=1,node=1,billing=1"):
  return dict(job_id="13308",expected_job_name="test9_missing_source_diagnostic_v1",expected_state=state,expected_exit_code=exit_code,raw_sacct="13308|u21111210118|u21111210118|organ|test9_missing_source_diagnostic_v1|"+state+"|"+exit_code+"|1|"+tres+"\n")
 def test_common_only_authoritative_twelve_block(self):
  pairs,source=self.common()
  self.assertEqual(m.recorded_literal_replacements(("unused.replace('X','Y')\n"+source).encode(),pairs),pairs)
 def test_common_block_malformed_or_duplicate_read_rejected(self):
  pairs,source=self.common()
  cases=[source.replace("s=s.replace('OLD00','NEW00')","s=s.replace(old,new)"),source.replace("common.write_text(s)","other.write_text(s)"),"s=common.read_text()\n"+source,source.replace("s=s.replace('OLD11','NEW11')\n","")]
  for value in cases:
   with self.subTest(value=value):
    with self.assertRaises(ValueError):m.recorded_literal_replacements(value.encode(),pairs)
 def test_common_expected_pair_fork_rejected(self):
  pairs,source=self.common();pairs[7][1]="DIFFERENT"
  with self.assertRaises(ValueError):m.recorded_literal_replacements(source.encode(),pairs)
 def test_actual_two_JS_records_parse_twelve_literal_pairs(self):
  data=json.loads("{\"schema\":\"exact-two-historical-BBF-patch-records-data-only.v1\",\"original_session_id\":\"01a12917-8539-7e20-89ae-37dd9dcc35c1\",\"original_local_session_file\":\"/Users/yangzijian/.codex/sessions/2026/10/11/rollout-2026-10-11T11-52-49-01a12917-8539-7e20-89ae-37dd9dcc35c1.jsonl\",\"records\":[{\"record_line\":1381,\"raw_JSONL_record\":\"{\\\"timestamp\\\":\\\"2026-10-11T05:06:04.414Z\\\",\\\"ordinal\\\":1380,\\\"type\\\":\\\"response_item\\\",\\\"payload\\\":{\\\"type\\\":\\\"custom_tool_call\\\",\\\"id\\\":\\\"ctc_00918a3c2e5efc41016acb192eb7048191a4013912e378d57f\\\",\\\"status\\\":\\\"completed\\\",\\\"call_id\\\":\\\"call_1507b4e1755942269e8cf5d83799737f\\\",\\\"name\\\":\\\"exec\\\",\\\"input\\\":\\\"let c=load(\\\\\\\"bbf_diagnostic_code_v2\\\\\\\");\\\\nc=c.replace('msa=np.asarray(data[f[\\\\\\\"msa_feature_key\\\\\\\"]])','msa=np.asarray(data[f.get(\\\\\\\"msa_feature_key\\\\\\\",f.get(\\\\\\\"msa_feat_key\\\\\\\"))])');\\\\nc=c.replace('    mapping={int(k)-1:int(v)-1 for k,v in job[\\\\\\\"target_query_to_template_indices\\\\\\\"].items()}','    prev=np.asarray(data[f.get(\\\\\\\"initial_prev_pos_key\\\\\\\",\\\\\\\"prev_pos\\\\\\\")],float)\\\\\\\\n    if prev.shape!=(L,37,3) or not np.isfinite(prev).all() or prev.any():raise ValueError(\\\\\\\"Initial previous-position guess leaked\\\\\\\")\\\\\\\\n    cbmask=np.asarray(data[\\\\\\\"template_pseudo_beta_mask\\\\\\\"],float);cbpos=np.asarray(data[\\\\\\\"template_pseudo_beta\\\\\\\"],float)\\\\\\\\n    if cbmask.shape!=(1,L) or cbpos.shape!=(1,L,3) or not np.isfinite(cbmask).all() or not np.isfinite(cbpos).all():raise ValueError(\\\\\\\"Pseudo-beta template features malformed\\\\\\\")\\\\\\\\n    rawmask=np.asarray(data[\\\\\\\"batch_all_atom_mask\\\\\\\"],float);rawpos=np.asarray(data[\\\\\\\"batch_all_atom_positions\\\\\\\"],float)\\\\\\\\n    if rawmask.shape!=(L,37) or rawpos.shape!=(L,37,3):raise ValueError(\\\\\\\"Raw target-only source batch shape\\\\\\\")\\\\\\\\n    mapping={int(k)-1:int(v)-1 for k,v in job[\\\\\\\"target_query_to_template_indices\\\\\\\"].items()}');\\\\nc=c.replace('    if mask[:,T:].any() or pos[:,T:].any():','    if rawmask[T:].any() or rawpos[T:].any() or cbmask[:,T:].any() or cbpos[:,T:].any():raise ValueError(\\\\\\\"Binder raw/template pseudo-beta leakage\\\\\\\")\\\\\\\\n    if absent and (rawmask[absent].any() or rawpos[absent].any() or cbmask[:,absent].any() or cbpos[:,absent].any()):raise ValueError(\\\\\\\"Missing target raw/pseudo-beta leakage\\\\\\\")\\\\\\\\n    if mask[:,T:].any() or pos[:,T:].any():');\\\\nc=c.replace('    if not job[\\\\\\\"target_template_enabled\\\\\\\"] and n!=0:','    if not job[\\\\\\\"target_template_enabled\\\\\\\"] and (cbmask.any() or cbpos.any()):raise ValueError(\\\\\\\"No-template pseudo-beta channel leaked\\\\\\\")\\\\\\\\n    if not job[\\\\\\\"target_template_enabled\\\\\\\"] and n!=0:');\\\\nc=c.replace('actual_query_length=L)','actual_query_length=L,initial_prev_pos_nonzero=0,all_models_features_verified=f.get(\\\\\\\"all_models_feature_arrays_identical\\\\\\\"))');\\\\nc=c.replace('        if worker.get(\\\\\\\"allocation\\\\\\\",{}).get(\\\\\\\"allocated_gpu_count\\\\\\\")!=1:raise ValueError(\\\\\\\"GPU worker actual scheduler allocation missing/not1\\\\\\\")','        allocation_receipt=worker.get(\\\\\\\"allocation\\\\\\\",{})\\\\\\\\n        if allocation_receipt.get(\\\\\\\"allocated_gpu_count\\\\\\\")!=1:raise ValueError(\\\\\\\"GPU worker actual scheduler allocation missing/not1\\\\\\\")');\\\\nc=c.replace('components(conf[\\\\\\\"iptm\\\\\\\"],float(pp[na:].mean()),ip,cp)','components(conf.get(\\\\\\\"iptm\\\\\\\",conf.get(\\\\\\\"globaliptm\\\\\\\")),float(pp[na:].mean()),ip,cp)');\\\\nc=c.replace('global_iptm=float(conf[\\\\\\\"iptm\\\\\\\"])','global_iptm=float(conf.get(\\\\\\\"iptm\\\\\\\",conf.get(\\\\\\\"globaliptm\\\\\\\")))');\\\\nc=c.replace('        np.savez(path,mask=mask,pos=pos,aatype=query,msa=np.zeros((1,L,49)))','        cbmask=np.zeros((1,L));cbpos=np.zeros((1,L,3))\\\\\\\\n        np.savez(path,mask=mask,pos=pos,aatype=query,msa=np.zeros((1,L,49)),prev_pos=np.zeros((L,37,3)),template_pseudo_beta_mask=cbmask,template_pseudo_beta=cbpos,batch_all_atom_mask=np.zeros((L,37)),batch_all_atom_positions=np.zeros((L,37,3)))');\\\\nc=c.replace('actual_query_length=L,initial_prev_pos_nonzero=0,all_models_features_verified=f.get(\\\\\\\"all_models_feature_arrays_identical\\\\\\\"))','actual_query_length=L,initial_prev_pos_nonzero=0)');\\\\nstore(\\\\\\\"bbf_diagnostic_code_v3\\\\\\\",c);store(\\\\\\\"bbf_diagnostic_code_v2\\\\\\\",c);\\\\nconst q=s=>\\\\\\\"'\\\\\\\"+s.replace(/'/g,\\\\\\\"'\\\\\\\\\\\\\\\\''\\\\\\\")+\\\\\\\"'\\\\\\\";\\\\ntext(await tools.exec_command({cmd:load(\\\\\\\"screen_ssh\\\\\\\")+\\\\\\\" \\\\\\\"+q(\\\\\\\"cat > /lustre/users/u21111210118/projects/test9/source/rebuild/bbf_input_diagnostic.py <<'PY'\\\\\\\\n\\\\\\\"+c+\\\\\\\"\\\\\\\\nPY\\\\\\\\nsbatch /lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/code/cpu.sbatch test --out /lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/inputs/test_v3.json\\\\\\\\nsacct -j 13036 --format=JobID,State,ExitCode,Elapsed -n\\\\\\\\ntail -n 40 /lustre/users/u21111210118/projects/test9/steps/23_common_review/logs/hardware_13036.log\\\\\\\"),max_output_tokens:2000}));\\\\n\\\",\\\"internal_chat_message_metadata_passthrough\\\":{\\\"turn_id\\\":\\\"01a12928-f105-7cd3-bed9-6c73e91f0804\\\",\\\"create_time\\\":1791695150.7349188}}}\"},{\"record_line\":1408,\"raw_JSONL_record\":\"{\\\"timestamp\\\":\\\"2026-10-11T05:07:12.719Z\\\",\\\"ordinal\\\":1407,\\\"type\\\":\\\"response_item\\\",\\\"payload\\\":{\\\"type\\\":\\\"custom_tool_call\\\",\\\"id\\\":\\\"ctc_00918a3c2e5efc41016acb197e379c81918ceebce2e037ab7f\\\",\\\"status\\\":\\\"completed\\\",\\\"call_id\\\":\\\"call_695893637f52466ba2c6f5638ac69a8b\\\",\\\"name\\\":\\\"exec\\\",\\\"input\\\":\\\"let c=load(\\\\\\\"bbf_diagnostic_code_v3\\\\\\\");\\\\nc=c.replace('    checked=[]\\\\\\\\n    for key,job','    verify(features[\\\\\\\"source\\\\\\\"])\\\\\\\\n    checked=[]\\\\\\\\n    for key,job');\\\\nc=c.replace('        f=actual[key];actual_stats=feature_arrays(job,f)','        f=actual[key];actual_stats=feature_arrays(job,f)\\\\\\\\n        if f[\\\\\\\"actual_validated_model_slots\\\\\\\"]!=job[\\\\\\\"slots\\\\\\\"] or not f[\\\\\\\"all_models_feature_arrays_identical\\\\\\\"]:raise ValueError(\\\\\\\"Every fixed model actual forward feature proof required\\\\\\\")');\\\\nstore(\\\\\\\"bbf_diagnostic_code_v3\\\\\\\",c);store(\\\\\\\"bbf_diagnostic_code_v2\\\\\\\",c);\\\\nconst q=s=>\\\\\\\"'\\\\\\\"+s.replace(/'/g,\\\\\\\"'\\\\\\\\\\\\\\\\''\\\\\\\")+\\\\\\\"'\\\\\\\";\\\\ntext(await tools.exec_command({cmd:load(\\\\\\\"screen_ssh\\\\\\\")+\\\\\\\" \\\\\\\"+q(\\\\\\\"cat > /lustre/users/u21111210118/projects/test9/source/rebuild/bbf_input_diagnostic.py <<'PY'\\\\\\\\n\\\\\\\"+c+\\\\\\\"\\\\\\\\nPY\\\\\\\"),max_output_tokens:300}));\\\\n\\\",\\\"internal_chat_message_metadata_passthrough\\\":{\\\"turn_id\\\":\\\"01a12928-f105-7cd3-bed9-6c73e91f0804\\\",\\\"create_time\\\":1791695230.221601}}}\"}],\"recorded_tool_calls_executed\":false,\"scope\":\"Only exact two original JSONL records copied as data; AST literal replace statements only, no history execution.\"}")
  pairs,proof=m.recorded_js_patches(m.BBF_REPLAY_PINS["records"],lambda r:json.dumps(data).encode())
  self.assertEqual(len(pairs),12);self.assertEqual(proof,m.BBF_REPLAY_PINS["record_proofs"])
 def test_JS_record_metadata_or_nonliteral_fork_rejected(self):
  data=json.loads("{\"schema\":\"exact-two-historical-BBF-patch-records-data-only.v1\",\"original_session_id\":\"01a12917-8539-7e20-89ae-37dd9dcc35c1\",\"original_local_session_file\":\"/Users/yangzijian/.codex/sessions/2026/10/11/rollout-2026-10-11T11-52-49-01a12917-8539-7e20-89ae-37dd9dcc35c1.jsonl\",\"records\":[{\"record_line\":1381,\"raw_JSONL_record\":\"{\\\"timestamp\\\":\\\"2026-10-11T05:06:04.414Z\\\",\\\"ordinal\\\":1380,\\\"type\\\":\\\"response_item\\\",\\\"payload\\\":{\\\"type\\\":\\\"custom_tool_call\\\",\\\"id\\\":\\\"ctc_00918a3c2e5efc41016acb192eb7048191a4013912e378d57f\\\",\\\"status\\\":\\\"completed\\\",\\\"call_id\\\":\\\"call_1507b4e1755942269e8cf5d83799737f\\\",\\\"name\\\":\\\"exec\\\",\\\"input\\\":\\\"let c=load(\\\\\\\"bbf_diagnostic_code_v2\\\\\\\");\\\\nc=c.replace('msa=np.asarray(data[f[\\\\\\\"msa_feature_key\\\\\\\"]])','msa=np.asarray(data[f.get(\\\\\\\"msa_feature_key\\\\\\\",f.get(\\\\\\\"msa_feat_key\\\\\\\"))])');\\\\nc=c.replace('    mapping={int(k)-1:int(v)-1 for k,v in job[\\\\\\\"target_query_to_template_indices\\\\\\\"].items()}','    prev=np.asarray(data[f.get(\\\\\\\"initial_prev_pos_key\\\\\\\",\\\\\\\"prev_pos\\\\\\\")],float)\\\\\\\\n    if prev.shape!=(L,37,3) or not np.isfinite(prev).all() or prev.any():raise ValueError(\\\\\\\"Initial previous-position guess leaked\\\\\\\")\\\\\\\\n    cbmask=np.asarray(data[\\\\\\\"template_pseudo_beta_mask\\\\\\\"],float);cbpos=np.asarray(data[\\\\\\\"template_pseudo_beta\\\\\\\"],float)\\\\\\\\n    if cbmask.shape!=(1,L) or cbpos.shape!=(1,L,3) or not np.isfinite(cbmask).all() or not np.isfinite(cbpos).all():raise ValueError(\\\\\\\"Pseudo-beta template features malformed\\\\\\\")\\\\\\\\n    rawmask=np.asarray(data[\\\\\\\"batch_all_atom_mask\\\\\\\"],float);rawpos=np.asarray(data[\\\\\\\"batch_all_atom_positions\\\\\\\"],float)\\\\\\\\n    if rawmask.shape!=(L,37) or rawpos.shape!=(L,37,3):raise ValueError(\\\\\\\"Raw target-only source batch shape\\\\\\\")\\\\\\\\n    mapping={int(k)-1:int(v)-1 for k,v in job[\\\\\\\"target_query_to_template_indices\\\\\\\"].items()}');\\\\nc=c.replace('    if mask[:,T:].any() or pos[:,T:].any():','    if rawmask[T:].any() or rawpos[T:].any() or cbmask[:,T:].any() or cbpos[:,T:].any():raise ValueError(\\\\\\\"Binder raw/template pseudo-beta leakage\\\\\\\")\\\\\\\\n    if absent and (rawmask[absent].any() or rawpos[absent].any() or cbmask[:,absent].any() or cbpos[:,absent].any()):raise ValueError(\\\\\\\"Missing target raw/pseudo-beta leakage\\\\\\\")\\\\\\\\n    if mask[:,T:].any() or pos[:,T:].any():');\\\\nc=c.replace('    if not job[\\\\\\\"target_template_enabled\\\\\\\"] and n!=0:','    if not job[\\\\\\\"target_template_enabled\\\\\\\"] and (cbmask.any() or cbpos.any()):raise ValueError(\\\\\\\"No-template pseudo-beta channel leaked\\\\\\\")\\\\\\\\n    if not job[\\\\\\\"target_template_enabled\\\\\\\"] and n!=0:');\\\\nc=c.replace('actual_query_length=L)','actual_query_length=L,initial_prev_pos_nonzero=0,all_models_features_verified=f.get(\\\\\\\"all_models_feature_arrays_identical\\\\\\\"))');\\\\nc=c.replace('        if worker.get(\\\\\\\"allocation\\\\\\\",{}).get(\\\\\\\"allocated_gpu_count\\\\\\\")!=1:raise ValueError(\\\\\\\"GPU worker actual scheduler allocation missing/not1\\\\\\\")','        allocation_receipt=worker.get(\\\\\\\"allocation\\\\\\\",{})\\\\\\\\n        if allocation_receipt.get(\\\\\\\"allocated_gpu_count\\\\\\\")!=1:raise ValueError(\\\\\\\"GPU worker actual scheduler allocation missing/not1\\\\\\\")');\\\\nc=c.replace('components(conf[\\\\\\\"iptm\\\\\\\"],float(pp[na:].mean()),ip,cp)','components(conf.get(\\\\\\\"iptm\\\\\\\",conf.get(\\\\\\\"globaliptm\\\\\\\")),float(pp[na:].mean()),ip,cp)');\\\\nc=c.replace('global_iptm=float(conf[\\\\\\\"iptm\\\\\\\"])','global_iptm=float(conf.get(\\\\\\\"iptm\\\\\\\",conf.get(\\\\\\\"globaliptm\\\\\\\")))');\\\\nc=c.replace('        np.savez(path,mask=mask,pos=pos,aatype=query,msa=np.zeros((1,L,49)))','        cbmask=np.zeros((1,L));cbpos=np.zeros((1,L,3))\\\\\\\\n        np.savez(path,mask=mask,pos=pos,aatype=query,msa=np.zeros((1,L,49)),prev_pos=np.zeros((L,37,3)),template_pseudo_beta_mask=cbmask,template_pseudo_beta=cbpos,batch_all_atom_mask=np.zeros((L,37)),batch_all_atom_positions=np.zeros((L,37,3)))');\\\\nc=c.replace('actual_query_length=L,initial_prev_pos_nonzero=0,all_models_features_verified=f.get(\\\\\\\"all_models_feature_arrays_identical\\\\\\\"))','actual_query_length=L,initial_prev_pos_nonzero=0)');\\\\nstore(\\\\\\\"bbf_diagnostic_code_v3\\\\\\\",c);store(\\\\\\\"bbf_diagnostic_code_v2\\\\\\\",c);\\\\nconst q=s=>\\\\\\\"'\\\\\\\"+s.replace(/'/g,\\\\\\\"'\\\\\\\\\\\\\\\\''\\\\\\\")+\\\\\\\"'\\\\\\\";\\\\ntext(await tools.exec_command({cmd:load(\\\\\\\"screen_ssh\\\\\\\")+\\\\\\\" \\\\\\\"+q(\\\\\\\"cat > /lustre/users/u21111210118/projects/test9/source/rebuild/bbf_input_diagnostic.py <<'PY'\\\\\\\\n\\\\\\\"+c+\\\\\\\"\\\\\\\\nPY\\\\\\\\nsbatch /lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/code/cpu.sbatch test --out /lustre/users/u21111210118/projects/test9/steps/23_common_review/bbf_diagnostics/inputs/test_v3.json\\\\\\\\nsacct -j 13036 --format=JobID,State,ExitCode,Elapsed -n\\\\\\\\ntail -n 40 /lustre/users/u21111210118/projects/test9/steps/23_common_review/logs/hardware_13036.log\\\\\\\"),max_output_tokens:2000}));\\\\n\\\",\\\"internal_chat_message_metadata_passthrough\\\":{\\\"turn_id\\\":\\\"01a12928-f105-7cd3-bed9-6c73e91f0804\\\",\\\"create_time\\\":1791695150.7349188}}}\"},{\"record_line\":1408,\"raw_JSONL_record\":\"{\\\"timestamp\\\":\\\"2026-10-11T05:07:12.719Z\\\",\\\"ordinal\\\":1407,\\\"type\\\":\\\"response_item\\\",\\\"payload\\\":{\\\"type\\\":\\\"custom_tool_call\\\",\\\"id\\\":\\\"ctc_00918a3c2e5efc41016acb197e379c81918ceebce2e037ab7f\\\",\\\"status\\\":\\\"completed\\\",\\\"call_id\\\":\\\"call_695893637f52466ba2c6f5638ac69a8b\\\",\\\"name\\\":\\\"exec\\\",\\\"input\\\":\\\"let c=load(\\\\\\\"bbf_diagnostic_code_v3\\\\\\\");\\\\nc=c.replace('    checked=[]\\\\\\\\n    for key,job','    verify(features[\\\\\\\"source\\\\\\\"])\\\\\\\\n    checked=[]\\\\\\\\n    for key,job');\\\\nc=c.replace('        f=actual[key];actual_stats=feature_arrays(job,f)','        f=actual[key];actual_stats=feature_arrays(job,f)\\\\\\\\n        if f[\\\\\\\"actual_validated_model_slots\\\\\\\"]!=job[\\\\\\\"slots\\\\\\\"] or not f[\\\\\\\"all_models_feature_arrays_identical\\\\\\\"]:raise ValueError(\\\\\\\"Every fixed model actual forward feature proof required\\\\\\\")');\\\\nstore(\\\\\\\"bbf_diagnostic_code_v3\\\\\\\",c);store(\\\\\\\"bbf_diagnostic_code_v2\\\\\\\",c);\\\\nconst q=s=>\\\\\\\"'\\\\\\\"+s.replace(/'/g,\\\\\\\"'\\\\\\\\\\\\\\\\''\\\\\\\")+\\\\\\\"'\\\\\\\";\\\\ntext(await tools.exec_command({cmd:load(\\\\\\\"screen_ssh\\\\\\\")+\\\\\\\" \\\\\\\"+q(\\\\\\\"cat > /lustre/users/u21111210118/projects/test9/source/rebuild/bbf_input_diagnostic.py <<'PY'\\\\\\\\n\\\\\\\"+c+\\\\\\\"\\\\\\\\nPY\\\\\\\"),max_output_tokens:300}));\\\\n\\\",\\\"internal_chat_message_metadata_passthrough\\\":{\\\"turn_id\\\":\\\"01a12928-f105-7cd3-bed9-6c73e91f0804\\\",\\\"create_time\\\":1791695230.221601}}}\"}],\"recorded_tool_calls_executed\":false,\"scope\":\"Only exact two original JSONL records copied as data; AST literal replace statements only, no history execution.\"}")
  for token in ("timestamp","name","input"):
   altered=copy.deepcopy(data);item=json.loads(altered["records"][0]["raw_JSONL_record"])
   if token=="timestamp":item[token]="2020-01-01"
   elif token=="name":item["payload"][token]="different"
   else:item["payload"][token]=item["payload"][token].replace("c=c.replace(","c=other.replace(",1)
   altered["records"][0]["raw_JSONL_record"]=json.dumps(item)
   with self.subTest(token=token):
    with self.assertRaises(ValueError):m.recorded_js_patches(m.BBF_REPLAY_PINS["records"],lambda r:json.dumps(altered).encode())
 def test_JS_quoted_escape_positive_and_unknown_rejected(self):
  self.assertEqual(m.js_literal("'a\\nb'"),"a\nb")
  for token in ("'a\\q'","'''x'''","'line\nbreak'"):
   with self.subTest(token=token):
    with self.assertRaises(ValueError):m.js_literal(token)
 def test_numeric_terminal_complete_and_failed_predecessor(self):
  for state,code in (("COMPLETED","0:0"),("FAILED","1:0")):
   self.assertEqual(m.source_alias_terminal_record(self.terminal(state,code))["expected_state"],state)
 def test_numeric_terminal_GPU_duplicate_and_fraction_rejected(self):
  for tres in ("cpu=1,gres/gpu=0,gres/gpu:a100=1","cpu=1,cpu=1","cpu=1,gres/gpu=0.0","cpu=2"):
   with self.subTest(tres=tres):
    with self.assertRaises(ValueError):m.source_alias_terminal_record(self.terminal(tres=tres))
 def test_numeric_terminal_owner_or_state_fork_rejected(self):
  for bad in ("u21111210118|u21111210118","COMPLETED|0:0","organ|"):
   row=self.terminal();row["raw_sacct"]=row["raw_sacct"].replace(bad,"wrong|")
   with self.subTest(bad=bad):
    with self.assertRaises(ValueError):m.source_alias_terminal_record(row)
 def test_source_proof_view_scalarizes_only_called_exact_parent(self):
  r=dict(path="/synthetic/proof.json",bytes=4,sha256="a"*64);obj=dict(observed=dict(path="/old/file.py",bytes=8,sha256="b"*64),label="KEEP")
  saved=dict(proof_parent_views=[dict(parent_manifest=r,view=m.scalar_source_proof_view(obj))])
  view=m.source_alias_proof_parent_view(r,saved,lambda receipt:json.dumps(obj).encode())
  self.assertEqual(view["label"],"KEEP");self.assertEqual(list(m.receipt_edges(view)),[])
  self.assertIsNone(m.source_alias_proof_parent_view({**r,"sha256":"c"*64},saved,lambda receipt:json.dumps(obj).encode()))
 def test_source_proof_view_changed_parent_payload_rejected(self):
  r=dict(path="/synthetic/proof.json",bytes=4,sha256="a"*64);obj=dict(label="OLD")
  saved=dict(proof_parent_views=[dict(parent_manifest=r,view=m.scalar_source_proof_view(obj))])
  with self.assertRaises(ValueError):m.source_alias_proof_parent_view(r,saved,lambda receipt:b'{"label":"NEW"}')
 def test_exported_qualification_preserves_canonical_not_old_receipt_edge(self):
  original=dict(path="/old/source.py",bytes=8,sha256="b"*64);canonical={**original,"path":"/readonly/source.py"}
  qualified=dict(aliases=[dict(original=original,canonical=canonical,basis="EXISTING_READONLY_RUNTIME_SNAPSHOT")],reconstruction_proofs=dict(BBF=dict(original_byte_identity=original)))
  out=m.export_source_alias_qualification(qualified)
  self.assertEqual(out["aliases"][0]["canonical_receipt"],canonical);self.assertEqual(out["aliases"][0]["original_logical_path"],original["path"])
  self.assertEqual([r for r,trail in m.receipt_edges(out)],[canonical])

 def test_all_provenance_inputs_postwalk_drift_is_rejected(self):
  with tempfile.TemporaryDirectory()as directory:
   path=Path(directory)/"frozen_origin.py";path.write_bytes(b"VALUE=7\n");path.chmod(0o444)
   receipt=dict(path=str(path),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
   qualified=dict(canonical_source_and_provenance_inputs=[receipt])
   def reader(r):
    current=Path(r["path"]);data=current.read_bytes()
    if current.stat().st_mode&0o222 or len(data)!=r["bytes"]or hashlib.sha256(data).hexdigest()!=r["sha256"]:raise ValueError("Postwalk provenance input drift")
    return data
   self.assertEqual(m.source_alias_provenance_postreadback(qualified,reader)["verified_inputs"],[receipt])
   import context_mapper_audit_cpu as driver
   from unittest.mock import patch
   original_dir=Path(directory)/"original";frozen_dir=Path(directory)/"frozen";original_dir.mkdir();frozen_dir.mkdir();originals=[];frozen=[]
   for name in driver.NAMES:
    for base,table in ((original_dir,originals),(frozen_dir,frozen)):
     p=base/name;p.write_bytes(("EXACT_TOY_"+name).encode());p.chmod(0o444)
     table.append(dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
   def exact(r,readonly):
    current=Path(r["path"]);value=current.read_bytes()
    if current.stat().st_mode&0o222 or len(value)!=r["bytes"]or hashlib.sha256(value).hexdigest()!=r["sha256"]:raise ValueError("Executing original source drift")
    return current
   with patch.object(driver.bootstrap,"verify_bytes",side_effect=exact):
    self.assertTrue(driver.executing_source_readback(originals,frozen))
    changed=Path(originals[0]["path"]);changed.chmod(0o644);changed.write_bytes(b"DRIFT");changed.chmod(0o444)
    with self.assertRaisesRegex(ValueError,"Executing original source drift"):driver.executing_source_readback(originals,frozen)

   path.chmod(0o644);path.write_bytes(b"VALUE=8\n");path.chmod(0o444)
   with self.assertRaisesRegex(ValueError,"Postwalk"):m.source_alias_provenance_postreadback(qualified,reader)
 def test_restore_requires_explicit_reader_without_live_default(self):
  with self.assertRaisesRegex(ValueError,"explicit restored-index"):m.verify_exported_source_alias_qualification({},restore=True)
  from unittest.mock import patch
  qualified=dict(aliases=[],reconstruction_proofs=dict(BBF=dict(original_byte_identity=dict(path="/old.py",bytes=1,sha256="a"*64))),terminal_accounting=[])
  saved=m.export_source_alias_qualification(qualified);reader=lambda receipt:b"ONLY_RESTORED_TOY_BYTES"
  with patch.object(m,"qualify_source_alias_inputs",return_value=qualified)as call:
   self.assertEqual(m.verify_exported_source_alias_qualification(saved,reader,restore=True),qualified)
   call.assert_called_once_with(reader,[])


class ExactSourceManifestViewContracts(unittest.TestCase):
 def setUp(self):
  from unittest.mock import patch
  self.rows=[dict(original=dict(path="/old/source%d.py"%i,bytes=i+1,sha256=str(i)*64),canonical=dict(path="/readonly/source%d.py"%i,bytes=i+1,sha256=str(i)*64),basis="EXISTING_READONLY_RUNTIME_SNAPSHOT")for i in range(8)]
  self.parent=dict(path="/original/parent.json",bytes=5,sha256="a"*64)
  self.obj={"field%d"%i:self.rows[i%8]["original"]for i in range(12)}
  self.edges=[dict(source_parent=self.parent,parent_canonical_receipt=self.parent,source_field=["field%d"%i],original=self.rows[i%8]["original"])for i in range(12)]
  self.qualified=dict(aliases=self.rows,proof_parent_views=[])
  self.patch=patch.object(m,"PREPARED_PLAN",dict(aliases=self.rows,edges=self.edges));self.patch.start();self.addCleanup(self.patch.stop)
 def data(self,r):
  if r==self.parent:return json.dumps(self.obj).encode()
  return b"CANONICAL_TOY_BYTES"
 def test_original_twelve_fields_route_only_exact_byte_aliases(self):
  saved=copy.deepcopy(self.obj);view,proof=m.exact_source_manifest_view(self.parent,self.obj,self.qualified,self.data)
  self.assertEqual(self.obj,saved);self.assertEqual(len(proof["contexts"]),12)
  for i in range(12):self.assertEqual(view["field%d"%i],self.rows[i%8]["canonical"])
 def test_original_source_parent_field_fork_rejected(self):
  changed=copy.deepcopy(self.obj);changed["field3"]={**changed["field3"],"path":"/different.py"}
  with self.assertRaises(ValueError):m.exact_source_manifest_view(self.parent,changed,self.qualified,self.data)
 def test_unknown_parent_does_not_gain_source_alias_readview(self):
  self.assertEqual(m.exact_source_manifest_view({**self.parent,"path":"/unknown.json"},self.obj,self.qualified,self.data),(None,None))
  for base,closure in (({},{}),({"finite_source_recovery_inputs_qualification":self.parent},{"finite_source_recovery_inputs_qualification":{**self.parent,"sha256":"f"*64}})):
   with self.subTest(base=base):
    with self.assertRaisesRegex(ValueError,"artifact chain"):m.verify_source_alias_scope(base,closure,lambda r:Path("/never_read"))
 def test_proof_parent_inmemory_payload_fork_rejected(self):
  raw=dict(label="ORIGINAL",observed=self.rows[0]["original"]);qualified=dict(aliases=self.rows,proof_parent_views=[dict(parent_manifest=self.parent,view=m.scalar_source_proof_view(raw))])
  with self.assertRaises(ValueError):m.exact_source_manifest_view(self.parent,{**raw,"label":"FORK"},qualified,lambda r:json.dumps(raw).encode())
if __name__=="__main__":unittest.main()

class GeneratedSourceOutputContracts(unittest.TestCase):
 def setUp(self):
  from unittest.mock import patch
  self.rows=[dict(original=dict(path="/old/source%d.py"%i,bytes=i+1,sha256=str(i)*64),canonical=dict(path="/readonly/source%d.py"%i,bytes=i+1,sha256=str(i)*64),basis="EXISTING_READONLY_RUNTIME_SNAPSHOT")for i in range(8)]
  self.parent=dict(path="/original/source_parent.json",bytes=1,sha256="a"*64)
  self.edges=[dict(source_parent=self.parent,parent_canonical_receipt=self.parent,source_field=["r"+str(i)],original=r["original"])for i,r in enumerate(self.rows)]
  self.closure_receipt=dict(path="/accepted/source_closure.json",bytes=2,sha256="b"*64);self.inclusion_receipt=dict(path="/accepted/source_inclusion.json",bytes=3,sha256="c"*64)
  self.closure=dict(schema="benchmark-source-receipt-closure.v1",status="EXACT_CURRENT_TEXT_AND_SOURCE_DEPENDENCY_CLOSURE_WITH_TYPED_HISTORY",edges=[dict(receipt=r["original"],parent=self.parent["path"],field=e["source_field"],physical=r["canonical"],role="EXACT_TEXT_RECEIPT_READBACK",resolution_basis="EXACT_ACCEPTED_BYTECOPY_ALIAS",finite_exact_source_alias_context=dict(source_parent=self.parent,parent_canonical_receipt=self.parent,source_field=e["source_field"],**m.scalar_identity(r["original"]),canonical_receipt=r["canonical"],basis=r["basis"],current_execution_authorized=False))for r,e in zip(self.rows,self.edges)],source_receipts=[dict(logical=r["original"],physical=r["canonical"],basis="EXACT_ACCEPTED_BYTECOPY_ALIAS")for r in self.rows])
  self.inclusion=dict(status="SOURCE_INCLUSION_AUDIT_PASS",source_receipt_closure=self.closure_receipt,issues=[],applied=False)
  self.base=dict(source_closure=self.closure_receipt,source_inclusion=self.inclusion_receipt);self.qualified=dict(aliases=self.rows,proof_parent_views=[])
  self.patch=patch.object(m,"PREPARED_PLAN",dict(aliases=self.rows,edges=self.edges));self.patch.start();self.addCleanup(self.patch.stop)
 def data(self,r):return json.dumps(self.closure if r==self.closure_receipt else self.inclusion).encode()
 def test_sixteen_exact_generated_source_observations_readview(self):
  generated=m.qualify_generated_source_outputs(self.base,self.closure,self.qualified,self.data);self.assertEqual(len(generated["contexts"]),16)
  qualified={**self.qualified,"_generated_source_closure":generated};view,proof=m.exact_source_manifest_view(self.closure_receipt,self.closure,qualified,self.data)
  self.assertEqual(view["edges"][0]["receipt"],self.rows[0]["canonical"]);self.assertEqual(self.closure["edges"][0]["receipt"],self.rows[0]["original"]);self.assertEqual(len(proof["contexts"]),16)
 def test_generated_parent_field_canonical_or_unknown_observation_fork(self):
  for kind in ("parent","canonical","extra"):
   with self.subTest(kind=kind):
    saved=copy.deepcopy(self.closure)
    if kind=="parent":self.closure["edges"][0]["parent"]="/unknown.json"
    elif kind=="canonical":self.closure["source_receipts"][0]["physical"]=self.rows[1]["canonical"]
    else:self.closure["other_observation"]=self.rows[0]["original"]
    with self.assertRaises(ValueError):m.qualify_generated_source_outputs(self.base,self.closure,self.qualified,self.data)
    self.closure=saved
 def test_saved_full_readview_counters_and_authority_flags(self):
  value=dict(source_identity_n=8,original_source_parent_n=6,original_source_edge_n=12,source_proof_parent_n=5,generated_source_output_parent_n=1,generated_source_observation_n=16,restore_only=False,no_live_root_fallback=False);m.saved_readview_shape(value)
  for field in value:
   with self.subTest(field=field):
    with self.assertRaises(ValueError):m.saved_readview_shape({**value,field:None})
