"""Frozen all-78 target-MSA-only retrospective AF2 control refolding."""
import os,sys,json,hashlib,time,signal
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/17_control_calibration"
def rec(p):
 p=Path(p);return {"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}
def verify(row):
 got=rec(row["path"]);assert got["sha256"]==row["sha256"],row["path"]
 if "bytes" in row:assert got["bytes"]==row["bytes"]
 return Path(row["path"])
def write_new(p,obj):
 with Path(p).open("x") as f:json.dump(obj,f,indent=2,allow_nan=False);f.write("\n")
def init():
 cp=R/"steps/02_controls_recovery/runs/20261002T113406Z_11698/outputs/recovered_controls78.json"
 assert rec(cp)["sha256"]=="03c7f3aa14f7996393cd24d657f9a7e510c143893a95181a637ea786e7efe032"
 rows=json.loads(cp.read_text())["entries"];assert len(rows)==78 and len({x["id"] for x in rows})==78
 prevp=R/"steps/15_specificity_review/plan.json";prev=json.loads(prevp.read_text())
 verify(prev["runtime_acceptance"]);verify(prev["runtime_environment"])
 entries=[]
 for r in rows:
  for k in ("sequence","target_sequence"):
   assert hashlib.sha256(r[k].encode()).hexdigest()==r[k+"_sha256"]
   assert set(r[k])<=set("ACDEFGHIKLMNPQRSTVWY")
  entries.append({"condition_id":r["id"],"source_id":r["source_id"],"target":r["target"],"target_msa_key":r["target"]+"_"+r["target_sequence_sha256"][:12],"target_sequence":r["target_sequence"],"sequence":r["sequence"],"target_sequence_sha256":r["target_sequence_sha256"],"sequence_sha256":r["sequence_sha256"],"new_slot":len(entries),"historical_binding_label":r["binary_binding_label"],"qualification":"Use independent frozen step14/18 overlay. Every identity is modeled, no qualification-dependent inclusion."})
 assert len({r["target_msa_key"] for r in entries})==6
 plan={"status":"FROZEN_ALL_78_CONTROL_COMPOSITE_SEQUENCE_AF2_PLAN","created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"job":os.environ["SLURM_JOB_ID"],"control_identities":rec(cp),"inherited_runtime_plan":rec(prevp),"runtime_acceptance":prev["runtime_acceptance"],"runtime_environment":prev["runtime_environment"],"code":[rec(R/"source/rebuild"/x) for x in ("control_prepare.py","control_review.py","control_score.py","control_run.sh")],"conditions":entries,"protocol":prev["protocol"],"inference":{"model_type":"alphafold2_multimer_v3","models":[1,2,3,4,5],"seeds":[1042,1043,1044],"num_recycles":12,"recycle_early_stop_tolerance":0.5,"max_msa":[128,256],"target_msa":"MMseqs2 uniref+environment per exact target sequence, public service, frozen actual A3M hashes","binder_msa":"single sequence","pairing":"query-only, no homologous pairing","templates":False,"coordinates":False,"relax":False,"MSA_depth_policy":"True single-sequence return for synthetic or low-homology target is valid but reported explicitly. Network failure is never relabeled successful single-sequence retrieval."},"target_construct_note":"Six exact target sequences across five target names: BBF-14 has separate 111-aa and 112-aa author input constructs. Preserve exact per-ID sequences; never pool their MSA identities or interpret label-correlated construct length as biological evidence.","counts":{"conditions":78,"exact_target_sequences":6,"models_per_condition":15,"models":1170},"budget":{"estimated_GPU_hours":8.4,"maximum_concurrent_GPU_jobs":2,"GPUs_per_job":1,"array_task_walltime_hours":2,"notes":"Estimate extrapolated from restored matched inference; exact runtime recorded, no expansion to monomer/Rosetta/MD."},"scoring":{"unit":"unique binder-target identity","contact_cutoff_A":5.0,"score":"min(global_iptm/0.75,binder_plddt_fraction/0.8,interface_plddt_fraction/0.8,8/bidirectional_contact_PAE_A)","interface_plddt":"Mean per-residue pLDDT over unique residues participating in at least one cross-chain heavy-atom distance <=5 A contact, both chains.","contact_PAE":"Arithmetic mean of both directional PAE entries for each unique target-binder contact residue pair.","per_identity":"Median of all 15 valid models; incomplete model scores leave primary median null with missing count and observed-only summary separately.","missing":"Missing contact geometry or nonfinite quantity is null, never zero. Zero finite contact PAE makes PAE constraint nonlimiting.","calibration":"All labels are retrospective binding screen outcomes; qualification and family-held-out calibration frozen independently. No blockade or prospective superiority claim."},"coordinate_provenance":"NEW_PREDICTIONS_NOT_RESTORED_HISTORICAL_COORDINATES"}
 write_new(S/"plan.json",plan);print(json.dumps({"plan":rec(S/"plan.json"),"counts":plan["counts"],"budget":plan["budget"]},indent=2),flush=True)
def msa():
 from colabfold.colabfold import run_mmseqs2
 from colabfold.batch import msa_to_str,get_queries,unserialize_msa
 from alphafold.data import parsers
 plan=json.loads((S/"plan.json").read_text());msadir=S/"inputs/msas";qdir=S/"inputs/queries";targetrows={}
 for x in plan["code"]:verify(x)
 seqs={e["target_msa_key"]:e["target_sequence"] for e in plan["conditions"]}
 signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError("Bounded per-target MSA retrieval exceeded 40 minutes")))
 for key,seq in seqs.items():
  p=msadir/(key+".a3m")
  if p.exists():text=p.read_text();origin={"status":"RESUMED_FROZEN_LOCAL_A3M","url":"https://api.colabfold.com"}
  else:
   signal.alarm(2400)
   text=run_mmseqs2([seq],str(msadir/key),use_env=True,use_filter=True,use_templates=False,use_pairing=False,host_url="https://api.colabfold.com",user_agent="ppi-cldm-control-calibration/20261004")[0]
   signal.alarm(0)
   parsed=parsers.parse_a3m(text);assert parsed.sequences and parsed.sequences[0]==seq and all(len(x)==len(seq) for x in parsed.sequences)
   with p.open("x") as f:f.write(text)
   origin={"status":"PUBLIC_API_SUCCESS","url":"https://api.colabfold.com"}
  parsed=parsers.parse_a3m(text);assert parsed.sequences and parsed.sequences[0]==seq and all(len(x)==len(seq) for x in parsed.sequences)
  targetrows[key]={"input":rec(p),"raw_sequence_count":len(parsed.sequences),"raw_unique_sequence_count":len(set(parsed.sequences)),"single_sequence":len(set(parsed.sequences))==1,"origin":origin,"database_snapshot":"Public API does not expose database version. Actual A3M content/hash freezes input."}
  print("MSA_FROZEN",key,len(parsed.sequences),len(set(parsed.sequences)),flush=True)
 rows=[]
 for e in plan["conditions"]:
  text=Path(targetrows[e["target_msa_key"]]["input"]["path"]).read_text();target=e["target_sequence"];ligand=e["sequence"]
  a3m=msa_to_str([text,">binder\n"+ligand+"\n"],[">101\n"+target+"\n",">102\n"+ligand+"\n"],[target,ligand],[1,1]);p=qdir/(e["condition_id"]+".a3m")
  if p.exists():assert p.read_text()==a3m
  else:
   with p.open("x") as f:f.write(a3m)
  qs,complex_=get_queries(p);assert complex_ and len(qs)==1
  _,sequence,lines=qs[0];unpaired,paired,sequences,cardinality,_=unserialize_msa(lines,sequence);assert sequences==[target,ligand] and cardinality==[1,1]
  pm=parsers.parse_a3m(unpaired[0]);bm=parsers.parse_a3m(unpaired[1]);assert bm.sequences==[ligand]
  assert set(pm.sequences)==set(parsers.parse_a3m(text).sequences)
  rows.append({"condition_id":e["condition_id"],"input":rec(p),"effective_unpaired_target_sequence_count":len(pm.sequences),"effective_unpaired_ligand_sequence_count":len(bm.sequences),"chain_lengths":[len(target),len(ligand)]})
 result={"status":"ALL_78_CONTROL_INPUTS_READY","job":os.environ["SLURM_JOB_ID"],"plan":rec(S/"plan.json"),"targets":targetrows,"conditions":rows,"known_coordinates_in_inference_input":False}
 write_new(S/"inputs/msa_acceptance.json",result);print(json.dumps({"status":result["status"],"targets":targetrows,"acceptance":rec(S/"inputs/msa_acceptance.json")},indent=2),flush=True)
if __name__=="__main__":{"init":init,"msa":msa}[sys.argv[1]]()

