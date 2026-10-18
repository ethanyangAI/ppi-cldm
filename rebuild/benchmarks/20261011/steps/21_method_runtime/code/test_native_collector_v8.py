#!/usr/bin/env python3
import hashlib,importlib.util,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
import numpy as np
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";V=R/"steps/22_matched_benchmark/settings/pilot_v8"
D=S/f"runs/native_collector_contracts_{os.environ['SLURM_JOB_ID']}";O=D/"outputs";F=D/"source";O.mkdir(parents=True);F.mkdir()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
shutil.copyfile(S/"code/audit_native_confidence_v8.py",F/"audit_native_confidence_v8.py")
shutil.copyfile(Path(__file__),F/"test_native_collector.py")
for p in F.iterdir():p.chmod(0o444)
runtime=load("runtime",V/"source/benchmark_runtime.py");collector=load("collector",F/"audit_native_confidence_v8.py")
# Avoid test sys.modules mocks discarding imported C extensions.
sys.path.insert(0,str(R/"vendor/BindCraft"));import jax,colabdesign,functions
os.environ["RUNTIME_SOURCE"]=str(V/"source/benchmark_runtime.py")
fixtures=load("fixtures",V/"source/test_runtime_contracts.py")
class CollectorContracts(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(dir=S/"work");self.d=Path(self.temp.name);self.a=self.d/"000000";self.a.mkdir()
  self.target={"residue_count":3,"target_sequence":"ARD","rfd_output_target_chain":"A","rfd_binder_chain":"B"}
  self.raw={"sequence_record_id":"fixed_seq","sequence":"L"*65}
  runtime.append_stream(self.a/"sequences.jsonl",self.raw)
 def tearDown(self):self.temp.cleanup()
 def observe(self,index,method="rf_diffusion",iptm=.73456,reject=False):
  fixture=fixtures.ObservationContracts();model,query=fixture.native_fixture(index)
  # Make the three synthetic target CA atoms noncollinear so target alignment is identifiable.
  model.aux["all"]["atom_positions"][0,2,1]=[7.6,3.,2.]
  model.aux["all"]["atom_positions"][0,2,0]=[6.6,3.,2.]
  if method=="bindcraft":model.aux["pae"][:]=5.
  if reject:model.aux["plddt"][-65:]=.5
  pae=np.asarray(model.aux["pae"],dtype=float);T=3;cross=np.concatenate([pae[:T,T:].ravel(),pae[T:,:T].ravel()])
  model.aux["i_ptm"]=np.asarray(iptm,dtype=np.float32)
  model.aux["log"].update({"plddt":float(model.aux["plddt"][-65:].mean()),"i_ptm":float(model.aux["i_ptm"]),
   "ptm":float(model.aux["ptm"]),"pae":float(((pae+pae.T)/2)[-65:].mean()/31.),"i_pae":float(cross.mean()/31.)})
  context={"model_names":[model._model_names[index]],"sequence_record_id":"fixed_seq","native_design":"fixed_design",
   "sequence_record_ids":["fixed_seq"],"attempt_seed":20901,"num_recycles":3,"official_native_pdb_path":str(self.a/("official_"+str(index)+".pdb"))}
  item=runtime.save_native_confidence(model,self.a,"fixed_"+str(index),method,query[:3],query[3:],context)
  doc=json.loads(Path(item["path"]).read_text());shutil.copyfile(doc["raw_pdb"]["path"],context["official_native_pdb_path"])
  return model,item,doc
 def rf_complete(self):
  model,item,doc=self.observe(0)
  native=doc["context"]["official_native_pdb_path"];(self.a/"rf_native_inputs.json").write_text(json.dumps({"backbone_pdb":native}))
  pae=np.asarray(model.aux["pae"],dtype=float);cross=np.concatenate([pae[:3,3:].ravel(),pae[3:,:3].ravel()])
  metrics={"binder_plddt":float(model.aux["plddt"][-65:].mean()),"cross_pae_mean_angstrom":float(cross.mean()),
   "global_iptm":float(model.aux["i_ptm"]),"target_ca_rmsd":0.,"binder_backbone_rmsd":0.}
  cfg=json.loads((V/"rf_diffusion.json").read_text())
  update={"sequence_record_id":"fixed_seq","native_confidence":item,"native_metrics":metrics,"native_structure_path":native,
   "native_score_name":"native_single_AF2_PTM_pae_interaction","native_score":metrics["cross_pae_mean_angstrom"],
   "internal_acceptance":metrics["binder_plddt"]>=.8 and metrics["cross_pae_mean_angstrom"]<=10}
  runtime.append_stream(self.a/"native_screening.jsonl",update)
  return cfg,doc
 def test_rf_full_arrays_recompute_native_criterion_and_emitted_rank(self):
  cfg,doc=self.rf_complete();report=collector.audit_attempt(self.a,self.target,cfg,runtime)
  self.assertEqual(report["complete_observation_count"],1);self.assertEqual(len(report["ranking_value_and_criteria_checks"]),1)
  row=report["actual_native_predictions"][0];self.assertEqual(row["arrays"]["sha256"],rec(Path(doc["arrays"]["path"]))["sha256"])
  self.assertEqual(row["query_sha256"],hashlib.sha256(("ARD"+"L"*65).encode()).hexdigest())
 def test_changed_raw_pae_rejected_against_actual_native_scalar(self):
  cfg,doc=self.rf_complete();path=Path(doc["arrays"]["path"])
  with np.load(path) as f:arrays={k:f[k].copy() for k in f.files}
  arrays["pae"][:3,3:]+=1.;np.savez(path,**arrays)
  with self.assertRaisesRegex(RuntimeError,"confidence mismatch"):collector.audit_attempt(self.a,self.target,cfg,runtime)
 def test_changed_raw_aatype_rejected_against_full_query(self):
  cfg,doc=self.rf_complete();path=Path(doc["arrays"]["path"])
  with np.load(path) as f:arrays={k:f[k].copy() for k in f.files}
  arrays["aatype"][0]=19;np.savez(path,**arrays)
  with self.assertRaises(AssertionError):collector.audit_attempt(self.a,self.target,cfg,runtime)
 def bc_complete(self,reject=False):
  m1,item1,doc1=self.observe(0,"bindcraft",.73456,reject=reject);observations=[(m1,item1,doc1)]
  if not reject:observations.append(self.observe(1,"bindcraft",.84567))
  stats={}
  for model,item,doc in observations:
   number=doc["actual_model_indices"][0]+1;log=doc["native_aux_log"]
   stats[number]={label:round(log[key],2) for label,key in [("pLDDT","plddt"),("pTM","ptm"),("i_pTM","i_ptm"),("pAE","pae"),("i_pAE","i_pae")]}
  runtime.append_stream(self.a/"bindcraft_native_events.jsonl",{"event":"native_af2_filter_complete","design":"fixed_design","statistics":stats,"native_af2_pass":not reject})
  update={"sequence_record_id":"fixed_seq","native_confidence":[i for m,i,d in observations],"native_design":"fixed_design",
   "native_score_name":"native_BindCraft_average_AF2_iptm","native_score":None if reject else round(sum(stats[k]["i_pTM"] for k in stats)/len(stats),2),"internal_acceptance":not reject,"native_filter_result":True if not reject else None}
  if not reject:runtime.append_stream(self.a/"bindcraft_native_events.jsonl",{"event":"native_final_filter_complete","design":"fixed_design","result":True,
   "filter_values":{"Design":"fixed_design","Sequence":"L"*65,"Average_i_pTM":update["native_score"]}})
  runtime.append_stream(self.a/"native_screening.jsonl",update)
  return json.loads((V/"bindcraft.json").read_text()),observations
 def test_bc_two_raw_models_recompute_official_rounded_average_ranking(self):
  cfg,observations=self.bc_complete();report=collector.audit_attempt(self.a,self.target,cfg,runtime)
  self.assertEqual(report["complete_observation_count"],2)
  rank=report["ranking_value_and_criteria_checks"][0];self.assertEqual(rank["native_score_recomputed"],.79)
  self.assertAlmostEqual(rank["raw_mean_iptm"],(.73456+.84567)/2,places=6)
 def test_bc_reject_retains_one_actual_model_and_does_not_impute_score(self):
  cfg,observations=self.bc_complete(reject=True);Path(observations[0][2]["context"]["official_native_pdb_path"]).unlink()
  report=collector.audit_attempt(self.a,self.target,cfg,runtime)
  self.assertEqual(report["complete_observation_count"],1);rank=report["ranking_value_and_criteria_checks"][0]
  self.assertIsNone(rank["native_score_recomputed"]);self.assertEqual(rank["actual_models_completed"],1)
  self.assertFalse(report["actual_native_predictions"][0]["official_native_pdb_present"])
 def test_unpublished_partial_arrays_and_stream_tail_preserved_not_completed(self):
  cfg,doc=self.rf_complete();np.savez(self.a/"native_confidence/incomplete.npz",pae=np.eye(68))
  with open(self.a/"native_confidence.jsonl","ab") as f:f.write(b'{"unfinished":')
  report=collector.audit_attempt(self.a,self.target,cfg,runtime)
  self.assertEqual(report["complete_observation_count"],1);self.assertEqual(len(report["partial_unpublished_artifacts"]),1)
  self.assertGreater(report["streams"]["observations"]["partial_tail_bytes"],0)
 def test_bad_official_same_prediction_pdb_binding_rejected(self):
  cfg,doc=self.rf_complete();native=Path(doc["context"]["official_native_pdb_path"]);native.write_text(native.read_text()+"REMARK MUTATED\n")
  with self.assertRaisesRegex(AssertionError,"Archived PDB differs"):collector.audit_attempt(self.a,self.target,cfg,runtime)
 def test_bc_emitted_author_rank_corruption_rejected(self):
  cfg,observations=self.bc_complete();path=self.a/"native_screening.jsonl";update=json.loads(path.read_text());update["native_score"]=.90;path.write_text(json.dumps(update)+"\n")
  with self.assertRaisesRegex(RuntimeError,"ranking score"):collector.audit_attempt(self.a,self.target,cfg,runtime)
 def test_bc_native_final_filter_corruption_rejected(self):
  cfg,observations=self.bc_complete();path=self.a/"bindcraft_native_events.jsonl";events=[json.loads(line) for line in path.read_text().splitlines()]
  events[-1]["filter_values"]["Average_i_pTM"]=.10;path.write_text("".join(json.dumps(e)+"\n" for e in events))
  with self.assertRaises(AssertionError):collector.audit_attempt(self.a,self.target,cfg,runtime)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CollectorContracts))
report={"status":"NATIVE_RAW_CONFIDENCE_CPU_COLLECTOR_CONTRACTS_PASS" if result.wasSuccessful() else "COLLECTOR_CONTRACT_FAILURE",
 "collector_source":rec(F/"audit_native_confidence_v8.py"),"contracts_source":rec(F/"test_native_collector.py"),"runtime_source":rec(V/"source/benchmark_runtime.py"),
 "tests_run":result.testsRun,"errors":len(result.errors),"failures":len(result.failures),"cpu_job":os.environ["SLURM_JOB_ID"],
 "scope":"Synthetic collector contract fixtures only; no model prediction, native GPU acceptance or formal result",
 "scheduler_record":subprocess.check_output(["scontrol","show","job","-o",os.environ["SLURM_JOB_ID"]],text=True)}
assert "gres/gpu=" not in report["scheduler_record"]
(O/"acceptance.json").write_text(json.dumps(report,indent=2)+"\n")
for parent in [F,O]:
 for p in parent.iterdir():
  if p.is_file():p.chmod(0o444)
 parent.chmod(0o555)
print(json.dumps(report,indent=2));raise SystemExit(0 if result.wasSuccessful() else 1)

