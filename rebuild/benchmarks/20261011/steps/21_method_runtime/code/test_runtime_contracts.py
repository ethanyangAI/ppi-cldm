#!/usr/bin/env python3
"""CPU engineering contracts. Synthetic fixtures never enter scientific outputs."""
import hashlib,importlib.util,json,math,os,pickle,tempfile,time,types,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime"
spec=importlib.util.spec_from_file_location("benchmark_runtime",R/"source/rebuild/benchmark_runtime.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def receipt(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
class Contracts(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=S/"work");self.d=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def test_non_project_path_rejected(self):
  with self.assertRaises(RuntimeError):m.inside_project("/tmp/untrusted")
 def test_input_hash_mismatch_rejected(self):
  p=self.d/"input.txt";p.write_text("abc");v=receipt(p);p.write_text("xyz")
  with self.assertRaises(RuntimeError):m.checked_small_record(v)
 def test_repeated_attempt_rejects_changed_target_manifest(self):
  pdb=self.d/"target.pdb";pdb.write_text("CPU fixture only")
  target=self.d/"target.json";target.write_text(json.dumps({"schema":"prepared_benchmark_target.v1","target_pdb":receipt(pdb),"target_sequence":"AAA","residue_count":3}))
  config=self.d/"config.json";config.write_text(json.dumps({"schema":"matched_method_adapter.v1","method":"rf_diffusion","binder_length":65,"input_receipts":[]}))
  frozen=receipt(target)["sha256"];config_sha=receipt(config)["sha256"]
  with patch.dict(os.environ,{"BENCHMARK_TARGET_MANIFEST_SHA256":frozen}):
   for i in range(2):m.load_method_inputs(str(config),config_sha,str(target))
   changed=json.loads(target.read_text());changed["post_ready_mutation"]="must reject on each attempt";target.write_text(json.dumps(changed))
   with self.assertRaisesRegex(RuntimeError,"Prepared target manifest mismatch"):
    m.method_attempt("rf_diffusion",str(target),str(self.d/"must_not_start"),1042,str(config),config_sha)
  self.assertFalse((self.d/"must_not_start").exists())
 def test_incremental_native_mpnn_write_preserves_two_complete_before_partial_tail(self):
  import builtins
  fasta=self.d/"native.fa";ledger=self.d/"sequences.jsonl";observed=[];original_open=builtins.open
  chunks=[">native\n"+"G"*65+"\n",">T=0.0001, sample=1\n"+"A"*65+"\n",">T=0.0001, sample=2\n"+"L"*65+"\n",">T=0.0001, sample=3\nPARTIAL"]
  class Boundary(Exception):pass
  def official(*args,**kwargs):
   with builtins.open(fasta,"w") as f:
    for chunk in chunks:f.write(chunk)
   raise Boundary()
  def row(header,seq):
   observed.append((header,seq));m.append_stream(ledger,{"sequence":seq,"mpnn_header":header})
  old_args=list(m.sys.argv);old_cwd=os.getcwd()
  with patch("runpy.run_path",official):
   with self.assertRaises(Boundary):m.resident_mpnn(["python",str(R/"vendor/ProteinMPNN/protein_mpnn_run.py")],fasta,row)
  self.assertEqual(fasta.read_text(),"".join(chunks))
  self.assertEqual([seq for header,seq in observed],["A"*65,"L"*65])
  self.assertEqual(len(ledger.read_text().splitlines()),2)
  self.assertIs(builtins.open,original_open);self.assertEqual(m.sys.argv,old_args);self.assertEqual(os.getcwd(),old_cwd)
 def test_jsonable_preserves_missing_and_booleans(self):
  self.assertEqual(m.jsonable({"nan":float("nan"),"bool":True,"array":np.asarray([1,2])}),{"nan":None,"bool":True,"array":[1,2]})
 def test_atomic_does_not_overwrite(self):
  p=self.d/"one.json";m.atomic(p,{"n":1})
  with self.assertRaises(FileExistsError):m.atomic(p,{"n":2})
  self.assertEqual(json.loads(p.read_text()),{"n":1})
 def test_cpu_allocation_cannot_run_model(self):
  raw="JobId=1 JobState=RUNNING AllocTRES=cpu=4,mem=16G,node=1 ReqTRES=cpu=4,gres/gpu=1"
  with patch.dict(os.environ,{"SLURM_JOB_ID":"1"}),patch("subprocess.check_output",return_value=raw):
   with self.assertRaises(RuntimeError):m.allocated_gpu_guard()
 def test_one_actual_gpu_allocation_accepted(self):
  raw="JobId=1 JobState=RUNNING AllocTRES=cpu=4,mem=64G,node=1,gres/gpu=1,gres/gpu:v100=1"
  with patch.dict(os.environ,{"SLURM_JOB_ID":"1"}),patch("subprocess.check_output",return_value=raw):
   self.assertEqual(m.allocated_gpu_guard()["actually_allocated_gpu_count"],1)
 def test_nonrunning_or_multigpu_allocation_rejected(self):
  for raw in ["JobId=1 JobState=PENDING AllocTRES=gres/gpu=1","JobId=1 JobState=RUNNING AllocTRES=gres/gpu=2"]:
   with patch.dict(os.environ,{"SLURM_JOB_ID":"1"}),patch("subprocess.check_output",return_value=raw):
    with self.assertRaises(RuntimeError):m.allocated_gpu_guard()
 def test_session_frozen_hash_mismatch_rejected(self):
  frozen={k:"a"*64 for k in ["method_config_sha256","target_manifest_sha256","protocol_sha256","plan_sha256"]}
  request={**frozen,"attempt_dir":str(self.d/"attempt"),"method_config_sha256":"b"*64}
  with self.assertRaises(RuntimeError):m.validate_session_request(request,frozen)
 def test_file_rpc_keeps_one_resident_process_for_two_attempts(self):
  directory=self.d/"session";(directory/"requests").mkdir(parents=True)
  config=self.d/"method.json";config.write_text("{}");target=self.d/"target.json";target.write_text("{}")
  config_sha=receipt(config)["sha256"];target_sha=receipt(target)["sha256"]
  deadline=time.time()+30;frozen={"method_config_sha256":config_sha,"target_manifest_sha256":target_sha,"protocol_sha256":"a"*64,"plan_sha256":"b"*64}
  for i in range(2):
   ident=f"{i:06d}";request={**frozen,"request_id":ident,"action":"method-attempt","attempt_index":i,"attempt_dir":str(self.d/f"attempt{i}"),"seed":1042+i,"allocation_deadline_epoch":deadline}
   (directory/"requests"/(ident+".json")).write_text(json.dumps(request))
  calls=[]
  def attempt(method,tp,out,seed,cp,cs):
   calls.append((os.getpid(),seed));p=Path(out);p.mkdir();m.atomic(p/"attempt_result.json",{"status":"SCIENTIFIC_REJECT"})
   if len(calls)==2:os.environ["BENCHMARK_ALLOCATION_DEADLINE_EPOCH"]="0"
  torch=types.ModuleType("torch");torch.cuda=types.SimpleNamespace(is_available=lambda:True,device_count=lambda:1)
  modules={"torch":torch,"rfdiffusion":types.ModuleType("rfdiffusion"),"protein_mpnn_utils":types.ModuleType("protein_mpnn_utils")}
  old_session=m._SESSION
  try:
   with patch.dict(os.environ,{"BENCHMARK_ALLOCATION_DEADLINE_EPOCH":str(deadline),"BENCHMARK_PROTOCOL_SHA256":"a"*64,"BENCHMARK_PLAN_SHA256":"b"*64,"BENCHMARK_GENERATION_DEADLINE_EPOCH":str(deadline)}),patch.dict("sys.modules",modules),patch.object(m,"load_method_inputs",return_value=({"method":"rf_diffusion"},{},config,target)),patch.object(m,"allocated_gpu_guard",return_value={"actually_allocated_gpu_count":1}),patch.object(m,"method_attempt",attempt):
    m.method_session("rf_diffusion",str(target),str(directory),str(config),config_sha)
   ready=json.loads((directory/"READY.json").read_text());responses=[json.loads(p.read_text()) for p in sorted((directory/"responses").glob("*.json"))]
   self.assertEqual(len(calls),2);self.assertEqual({x[0] for x in calls},{ready["pid"]})
   self.assertTrue(all(x["schema"]=="paired-budget-session-v1" and x["status"]=="COMPLETE" and x["attempt_result"]["sha256"] for x in responses))
   self.assertEqual(ready["visible_gpu_count"],1);self.assertIn("cuda_visible_devices",ready)
  finally:m._SESSION=old_session
 def pdb(self,path,target,binder):
  lines=[];serial=1
  for chain,xyz in [("A",target),("B",binder)]:
   for i,pos in enumerate(xyz,1):
    x,y,z=pos;lines.append(f"ATOM  {serial:5d}  CA  ALA {chain}{i:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00 90.00           C  ");serial+=1
   lines.append("TER")
  lines.append("END");path.write_text("\n".join(lines)+"\n")
 def test_native_target_alignment_rotation_invariant(self):
  rng=np.random.default_rng(20);t=rng.normal(size=(10,3))*5;b=rng.normal(size=(65,3))*5
  r=self.d/"r.pdb";p=self.d/"p.pdb";self.pdb(r,t,b)
  rotation=np.asarray([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]]);delta=np.asarray([5.,10.,15.])
  self.pdb(p,t@rotation+delta,b@rotation+delta)
  v=m.method_native_metrics(str(r),str(p),"A","B")
  self.assertLess(v["target_ca_rmsd"],0.003);self.assertLess(v["binder_backbone_rmsd"],0.003)
 def test_native_rmsd_measures_binder_after_target_fit(self):
  rng=np.random.default_rng(21);t=rng.normal(size=(10,3))*5;b=rng.normal(size=(65,3))*5
  r=self.d/"r.pdb";p=self.d/"p.pdb";self.pdb(r,t,b);self.pdb(p,t,b+np.asarray([2.,0.,0.]))
  v=m.method_native_metrics(str(r),str(p),"A","B")
  self.assertLess(v["target_ca_rmsd"],1e-5);self.assertAlmostEqual(v["binder_backbone_rmsd"],2.,places=5)
 def test_native_chain_mismatch_rejected(self):
  t=np.arange(30).reshape(10,3);b=np.arange(195).reshape(65,3);r=self.d/"r.pdb";p=self.d/"p.pdb";self.pdb(r,t,b);self.pdb(p,t,b)
  with self.assertRaises(RuntimeError):m.method_native_metrics(str(r),str(p),"B","A")
 def fake_bindcraft(self,out,seed,actual_colabdesign=False):
  adv=self.d/"advanced.json";adv.write_text("{}");flt=self.d/"filters.json";flt.write_text("{}")
  cfg={"bindcraft":{"advanced":receipt(adv),"filters":receipt(flt)}}
  target={"target_pdb":{"path":str(self.d/"unused.pdb")},"input_target_chain":"A","hotspots":[3,4]}
  funcs=types.ModuleType("functions")
  funcs.check_n_trajectories=lambda *a:False
  pose=types.SimpleNamespace(get_seq=lambda **k:["A"*65],aux={"log":{"terminate":""}},_tmp={"best":{"aux":{"log":{"plddt":0.9}}}})
  funcs.binder_hallucination=lambda *a:pose
  seqs=["A"*64+x for x in "DEFHIKLM"]
  funcs.mpnn_gen_sequence=lambda *a:{"seq":np.asarray(seqs),"score":np.arange(8.)/10,"seqid":np.arange(8.)/20}
  funcs.predict_binder_complex=lambda *a:({0:{"i_ptm":0.7}},a[1]!=seqs[0])
  funcs.check_filters=lambda *a:True
  def runpath(*a,**kw):
   if actual_colabdesign:
    from colabdesign.shared.model import design_model
    holder=types.SimpleNamespace();design_model.set_seed(holder,seed=seed)
    self.assertEqual(np.asarray(holder.key()).shape,(2,))
   self.assertFalse(funcs.check_n_trajectories({},{}))
   funcs.binder_hallucination("name","unused.pdb","A",None,65,seed)
   self.assertTrue(funcs.check_n_trajectories({},{}))
   np.random.seed(seed=seed)
   np.random.seed(None);np.random.seed(seed=None)
   funcs.mpnn_gen_sequence("unused.pdb","B",{}, {})
   funcs.predict_binder_complex(None,seqs[0],"name_mpnn1")
   funcs.predict_binder_complex(None,seqs[1],"name_mpnn2")
   funcs.check_filters(["name_mpnn2",seqs[1],0.8],["Design","Sequence","Average_i_pTM"],{})
  out.mkdir()
  before_seed=np.random.seed;before_functions={k:getattr(funcs,k) for k in ['check_n_trajectories','binder_hallucination','mpnn_gen_sequence','predict_binder_complex','check_filters']}
  try:
   with patch.dict("sys.modules",{"functions":funcs}),patch("runpy.run_path",runpath):
    state=m.bindcraft_one_attempt(cfg,target,out,seed)
    self.assertIs(np.random.seed,before_seed)
    for key,value in before_functions.items():self.assertIs(getattr(funcs,key),value)
  finally:np.random.seed=before_seed
  return state
 def test_bindcraft_all_raw_sequences_and_native_updates(self):
  out=self.d/"attempt";state=self.fake_bindcraft(out,1042)
  rows=[json.loads(x) for x in (out/"sequences.jsonl").read_text().splitlines()]
  updates=[json.loads(x) for x in (out/"native_screening.jsonl").read_text().splitlines()]
  self.assertEqual(len(rows),8);self.assertEqual(len({x["sequence_record_id"] for x in rows}),8)
  self.assertTrue(all(x["internal_acceptance"] is None for x in rows))
  self.assertEqual([x["internal_acceptance"] for x in updates],[False,True])
  self.assertEqual(state["started"],1)
 def test_bindcraft_entropy_seed_stream_reproducible(self):
  a=self.d/"a";b=self.d/"b";self.fake_bindcraft(a,1042);self.fake_bindcraft(b,1042)
  def seeds(p):
   return [json.loads(x)["seed"] for x in (p/"bindcraft_native_events.jsonl").read_text().splitlines() if json.loads(x)["event"]=="deterministic_entropy_seed"]
  self.assertEqual(seeds(a),seeds(b));self.assertEqual(len(seeds(a)),2)
 def test_bindcraft_actual_colabdesign_keyword_seed_path(self):
  self.fake_bindcraft(self.d/"actual_keyword",1042,actual_colabdesign=True)
 def test_array_scheduler_exact_actual_job_selected(self):
  raw="JobId=2 JobState=RUNNING AllocTRES=cpu=4,gres/gpu=1\nJobId=1 JobState=FAILED AllocTRES=cpu=4,gres/gpu=1"
  with patch.dict(os.environ,{"SLURM_JOB_ID":"2"}),patch("subprocess.check_output",return_value=raw):
   proof=m.allocated_gpu_guard();self.assertTrue(proof["selected_scheduler_record"].startswith("JobId=2 "));self.assertEqual(proof["scontrol_job"],raw)
  with patch.dict(os.environ,{"SLURM_JOB_ID":"1"}),patch("subprocess.check_output",return_value=raw):
   with self.assertRaisesRegex(RuntimeError,"RUNNING"):m.allocated_gpu_guard()
 def test_array_scheduler_ambiguous_or_missing_actual_job_rejected(self):
  for raw in ["JobId=2 JobState=RUNNING AllocTRES=gres/gpu=1","JobId=1 JobState=RUNNING AllocTRES=gres/gpu=1\nJobId=1 JobState=RUNNING AllocTRES=gres/gpu=1"]:
   with patch.dict(os.environ,{"SLURM_JOB_ID":"1"}),patch("subprocess.check_output",return_value=raw):
    with self.assertRaisesRegex(RuntimeError,"absent or ambiguous"):m.allocated_gpu_guard()
 def actual_rfd_target(self):
  target=json.loads((R/"steps/22_matched_benchmark/input_preparation/prepared_7_13010/KEAP1_2FLU/input_manifest.json").read_text())
  target["rfd_output_target_chain"]="A";target["rfd_binder_chain"]="B"
  return target
 def actual_rfd_paths(self):
  base=R/"steps/22_matched_benchmark/engineering_pilot/runs/13069_0/attempts/000000/generated/backbone_1436254356"
  return base.with_suffix(".pdb"),base.with_suffix(".trb")
 def test_actual_official_rfd_output_complete_identity_and_coordinate_audit(self):
  pdb,trb=self.actual_rfd_paths();proof=m.validate_rfd_output(pdb,trb,self.actual_rfd_target())
  self.assertEqual(proof["status"],"PASS");self.assertEqual(proof["physical_target_chain"],"A");self.assertEqual(proof["physical_binder_chain"],"B")
  self.assertEqual(len(proof["actual_target_ids"]),285);self.assertEqual(len(proof["actual_binder_ids"]),65)
  self.assertLess(proof["target_rigid_aligned_ca_rmsd_angstrom"],.1)
  self.assertGreater(proof["target_rigid_aligned_backbone_max_displacement_angstrom"]["O"],1.)
 def test_actual_rfd_stale_abstract_chain_metadata_rejected(self):
  pdb,trb=self.actual_rfd_paths();target=self.actual_rfd_target();target["rfd_output_target_chain"]="B";target["rfd_binder_chain"]="A"
  with self.assertRaisesRegex(RuntimeError,"physical mapping"):m.validate_rfd_output(pdb,trb,target)
 def test_actual_rfd_wrong_full_query_and_truncated_chain_rejected(self):
  pdb,trb=self.actual_rfd_paths();target=self.actual_rfd_target();target["target_sequence"]="W"+target["target_sequence"][1:]
  with self.assertRaisesRegex(RuntimeError,"sequence/length"):m.validate_rfd_output(pdb,trb,target)
  target=self.actual_rfd_target();truncated=self.d/"truncated.pdb"
  truncated.write_text("".join(x for x in pdb.read_text().splitlines(keepends=True) if not (x.startswith("ATOM") and x[21]=="A" and int(x[22:26])==285)))
  with self.assertRaisesRegex(RuntimeError,"sequence/length"):m.validate_rfd_output(truncated,trb,target)
 def test_receptor_local_index_cannot_substitute_full_complex_index(self):
  pdb,trb=self.actual_rfd_paths();data=pickle.loads(trb.read_bytes());data["complex_con_hal_idx0"]=data["receptor_con_hal_idx0"].copy()
  wrong=self.d/"wrong_mapping.trb";wrong.write_bytes(pickle.dumps(data))
  with self.assertRaisesRegex(RuntimeError,"TRB receptor/full-complex"):m.validate_rfd_output(pdb,wrong,self.actual_rfd_target())
if __name__=="__main__":
 if not os.environ.get("SLURM_JOB_ID"):raise RuntimeError("CPU Slurm job required")
 unittest.main()


