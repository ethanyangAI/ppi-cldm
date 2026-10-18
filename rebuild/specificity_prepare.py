import os,sys,json,hashlib,time,signal
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/15_specificity_review"
def rec(p):
 p=Path(p);return {"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}
def verify(row):
 got=rec(row["path"]);assert got["sha256"]==row["sha256"],row["path"]
 if "bytes" in row:assert got["bytes"]==row["bytes"]
 return Path(row["path"])
def write_new(p,obj):
 with Path(p).open("x") as f:json.dump(obj,f,indent=2);f.write("\n")
def init():
 sys.path.insert(0,str(R/"source/src"))
 from ppiblocker.structure import read_structure
 regp=R/"00_admin/reconstruction_20261002.json";reg=json.loads(regp.read_text())
 candp=verify(reg["recovered_three_candidates.json"]);cs=json.loads(candp.read_text())["entries"];verify(reg["candidate_recovery_receipt.json"])
 oldaccp=verify(reg["evidence"]["AF2_acceptance"]);oldacc=json.loads(oldaccp.read_text());oldplanp=verify(oldacc["plan"]);oldplan=json.loads(oldplanp.read_text())
 targets=[];entries=[];refman=[]
 for gene,pdb,suffix,fn in (("KEAP1","2FLU","20261002T114903Z_11737","2FLU_A_B_normalized.pdb"),("KLHL3","4CH9","20261002T114000Z_11716","4CH9_B_D_normalized.pdb"),("KLHL12","6TTK","20261002T114000Z_11716","6TTK_A_H_normalized.pdb")):
  mp=R/"steps/06_native_diagnostics/runs"/suffix/"manifest.json";m=json.loads(mp.read_text())
  assert m["status"]=="EXPERIMENTAL_NATIVE_REFERENCES_PREPARED_NOT_PREDICTIVE_VALIDATION"
  for row in m["inputs"]+list(m["outputs"].values()):verify(row)
  ref=m["outputs"][fn];chains,ctx=read_structure(verify(ref));assert len(chains)==2 and not ctx
  metarec=m["outputs"][pdb+"_native_identity_and_geometry.json"];meta=json.loads(verify(metarec).read_text());mapping=[]
  for c in chains:
   hit=[a for a in meta["chains"] if a["observed_sequence"]==c["sequence"]];assert hit
   ch=hit[0];entity=meta["entities"][ch["entity_id"]];pos=[r["entity_sequence_position"] for r in ch["residue_mapping"]];missing=ch["missing_entity_positions"]
   decl=entity["declared_construct_sequence"];assert "".join(decl[i-1] for i in pos)==c["sequence"]
   mapping.append({"observed_sequence":c["sequence"],"observed_length":len(c["sequence"]),"declared_sequence":decl,"declared_length":entity["declared_construct_length"],"missing_entity_positions":missing,"internal_missing_positions":[i for i in missing if min(pos)<i<max(pos)],"observed_to_declared_positions":pos,"entity":ch["entity_id"],"reference_chain":c["id"]})
  t={"target":gene,"pdb":pdb,"native_pdb":ref,"identity_metadata":metarec,"construct_mapping":mapping};targets.append(t);refman.append(rec(mp))
  ligands=[("native_"+pdb,"native",mapping[1]["declared_sequence"])]+[(c["id"],"candidate",c["sequence"]) for c in cs]
  for lid,role,seq in ligands:
   entries.append({"condition_id":gene+"__"+lid+"__declared","target":gene,"target_msa_key":gene+"_declared","ligand_id":lid,"role":role,"analysis_track":"primary_declared_entity","target_sequence":mapping[0]["declared_sequence"],"sequence":seq,"native_reference":ref,"new_slot":len(entries)})
  assert any(a["observed_sequence"]!=a["declared_sequence"] for a in mapping)
  entries.append({"condition_id":gene+"__native_"+pdb+"__observed_sensitivity","target":gene,"target_msa_key":gene+"_observed","ligand_id":"native_"+pdb,"role":"native","analysis_track":"sensitivity_observed_construct","target_sequence":mapping[0]["observed_sequence"],"sequence":mapping[1]["observed_sequence"],"native_reference":ref,"new_slot":len(entries)})
 assert len(entries)==15
 plan={"status":"FROZEN_MATCHED_SPECIFICITY_DECLARED_ENTITY_PRIMARY_PLAN","created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"job":os.environ["SLURM_JOB_ID"],"registry_snapshot":rec(regp),"candidate_sequences":rec(candp),"native_manifests":refman,"context_only_AF2_acceptance":rec(oldaccp),"runtime_acceptance":oldplan["runtime_acceptance"],"runtime_environment":oldplan["runtime_environment"],"targets":targets,"conditions":entries,"protocol":oldplan["protocol"],"inference":{"model_type":"alphafold2_multimer_v3","msa_mode":"mmseqs2_uniref_env","target_msa":"frozen per exact target construct; 128:256 caps","ligand_msa":"single sequence","pairing":"query-only, no homologous pairing","templates":False,"raw_unrelaxed":True,"known_coordinates_used_as_input":False},"counts":{"primary_conditions":12,"sensitivity_conditions":3,"models_per_condition":15,"primary_models":180,"sensitivity_models":45,"new_models":225,"reused_primary_models":0},"analysis":{"confidence_baseline":{"AF2_global_iptm_min":0.75,"binder_plddt_min":0.8,"interface_plddt_min":0.8,"bidirectional_contact_pae_max_A":8.0},"contact_cutoff_A":5.0,"native_recovery_operational_rule":{"ligand_CA_RMSD_after_target_alignment_max_A":5.0,"native_contact_recall_min":0.5,"confidence_baseline_required":True},"positive_control_denominator":15,"positive_adequacy":"At least 8/15 native models with confidence baseline AND native pose recovery, with >=2/3 seeds represented. Raw fractions are primary quantities; operational diagnostic, not calibrated biological cutoff.","specificity_interpretation":"If primary native recovery inadequate, candidate low confidence is NOT_ESTIMABLE_FOR_SPECIFICITY, never evidence of no off-target binding.","pair_iptm_note":"AF2 score JSON global ipTM cannot be relabeled directional pair ipTM. Bidirectional interface PAE retained independently.","reference_mapping":"Predictions retain complete declared sequence; comparison uses explicit entity positions of experimentally observed residues, with full-length and mapped denominators.","sensitivity":"All three observed native conditions predeclared; never choose better construct, never pool tracks. Different exact target constructs may yield different public MSA retrievals, recorded as an additional sensitivity limitation.","training_overlap":"Known PDB references may overlap AF2 training; diagnostic, not blind generalization benchmark."},"old_reused_conditions_status":"285aa KEAP1 candidate models are context only, not part of declared308aa primary analysis.","coordinate_provenance":"NEW_DIAGNOSTIC_PREDICTIONS_NOT_OLD_COORDINATES","references":["https://www.nature.com/articles/s41592-022-01488-1","https://www.biorxiv.org/content/10.1101/2021.10.04.463034","https://www.rcsb.org/structure/4CH9","https://www.rcsb.org/structure/6TTK","https://www.rcsb.org/structure/2FLU"]}
 write_new(S/"plan.json",plan)
 print(json.dumps({"plan":rec(S/"plan.json"),"counts":plan["counts"]},indent=2),flush=True)
def msa():
 from colabfold.colabfold import run_mmseqs2
 from colabfold.batch import msa_to_str,get_queries,unserialize_msa
 from alphafold.data import parsers
 signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError("Bounded MSA retrieval exceeded 40 minutes")));signal.alarm(2400)
 plan=json.loads((S/"plan.json").read_text());msadir=S/"inputs/msas";qdir=S/"inputs/queries";msadir.mkdir(exist_ok=True);qdir.mkdir(exist_ok=True);targetrows={}
 seqs={e["target_msa_key"]:e["target_sequence"] for e in plan["conditions"]}
 for key,seq in seqs.items():
  p=msadir/(key+".a3m")
  if key=="KEAP1_observed":
   original=R/"steps/03_af2_restore/target_msa/KEAP1_285aa.a3m";assert rec(original)["sha256"]=="c32ee0fa09f354469a2c94c76881c96b9b379faa8ef82663fb12d54a1cc0c6c8"
   text=original.read_text();origin=rec(original)
  else:
   text=run_mmseqs2([seq],str(msadir/key),use_env=True,use_filter=True,use_templates=False,use_pairing=False,host_url="https://api.colabfold.com",user_agent="ppi-cldm-specificity-review/20261002")[0]
   origin={"url":"https://api.colabfold.com","database_snapshot":"Current public API; version not exposed; exact A3M hash freezes actual input"}
  parsed=parsers.parse_a3m(text);assert parsed.sequences[0]==seq and len(parsed.sequences)>1 and all(len(x)==len(seq) for x in parsed.sequences)
  with p.open("x") as f:f.write(text)
  targetrows[key]={"input":rec(p),"raw_sequence_count":len(parsed.sequences),"origin":origin}
  print("MSA_FROZEN",key,len(parsed.sequences),flush=True)
 rows=[]
 for e in plan["conditions"]:
  text=Path(targetrows[e["target_msa_key"]]["input"]["path"]).read_text();target=e["target_sequence"];ligand=e["sequence"]
  a3m=msa_to_str([text,">binder\n"+ligand+"\n"],[">101\n"+target+"\n",">102\n"+ligand+"\n"],[target,ligand],[1,1]);p=qdir/(e["condition_id"]+".a3m")
  with p.open("x") as f:f.write(a3m)
  qs,complex_=get_queries(p);assert complex_ and len(qs)==1
  _,sequence,lines=qs[0];unpaired,paired,sequences,cardinality,_=unserialize_msa(lines,sequence);assert sequences==[target,ligand] and cardinality==[1,1]
  pm=parsers.parse_a3m(unpaired[0]);bm=parsers.parse_a3m(unpaired[1]);assert bm.sequences==[ligand]
  assert set(pm.sequences)==set(parsers.parse_a3m(text).sequences)
  rows.append({"condition_id":e["condition_id"],"input":rec(p),"effective_unpaired_target_sequence_count":len(pm.sequences),"effective_unpaired_ligand_sequence_count":len(bm.sequences),"chain_lengths":[len(target),len(ligand)]})
 result={"status":"ALL_15_MATCHED_CONDITION_INPUTS_READY","job":os.environ["SLURM_JOB_ID"],"plan":rec(S/"plan.json"),"targets":targetrows,"conditions":rows,"known_coordinates_in_inference_input":False}
 write_new(S/"inputs/msa_acceptance.json",result);signal.alarm(0);print(json.dumps(result,indent=2),flush=True)
if __name__=="__main__":{"init":init,"msa":msa}[sys.argv[1]]()

