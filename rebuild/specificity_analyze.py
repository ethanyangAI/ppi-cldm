"""CPU-only frozen specificity scoring, explicit native-coordinate mapping and denominators."""
import os,sys,json,hashlib,datetime,csv
from pathlib import Path
import numpy as np
from scipy.spatial.distance import cdist
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/15_specificity_review"
sys.path.insert(0,str(R/"source/src"))
from ppiblocker.structure import read_structure,interface,superpose
from ppiblocker.af2_review import atom_overlap
def rec(p):
 p=Path(p);return {"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}
def verify(row):
 p=Path(row["path"]);assert rec(p)["sha256"]==row["sha256"],str(p);return p
def dump(p,obj):
 with Path(p).open("x") as f:json.dump(obj,f,indent=2,allow_nan=False);f.write("\n")
def subset(c,positions):
 ii=[x-1 for x in positions];assert len(set(ii))==len(ii) and min(ii)>=0 and max(ii)<len(c["sequence"])
 return {**c,"sequence":"".join(c["sequence"][i] for i in ii),"residues":[c["residues"][i] for i in ii],"atoms":[c["atoms"][i] for i in ii],"heavy":[c["heavy"][i] for i in ii]}
def ca(c):return np.asarray([r["ca"] for r in c["residues"]])
def finite_summary(values):
 a=np.asarray(values,dtype=float);return {"mean":float(a.mean()),"median":float(np.median(a)),"p90":float(np.percentile(a,90)),"n":int(a.size)} if a.size else {"mean":None,"median":None,"p90":None,"n":0}
def construct_annotation(t):
 meta=json.loads(verify(t["identity_metadata"]).read_text());rows=[]
 for mapping in t["construct_mapping"]:
  entity=meta["entities"][mapping["entity"]];native=set()
  for aln in entity["reference_alignments"]:
   if aln["reference_database_name"]=="UniProt":
    for reg in aln["aligned_regions"]:native.update(range(reg["entity_beg_seq_id"],reg["entity_beg_seq_id"]+reg["length"]))
  length=mapping["declared_length"];native={x for x in native if 1<=x<=length};unmapped=sorted(set(range(1,length+1))-native)
  rows.append({"entity":mapping["entity"],"declared_length":length,"observed_length":mapping["observed_length"],"uniprot_mapped_positions":sorted(native),"non_uniprot_mapped_positions":unmapped,"non_uniprot_mapped_sequence":"".join(mapping["declared_sequence"][i-1] for i in unmapped),"non_uniprot_annotation":"Sequence outside RCSB UniProt alignment: engineered tag/linker or construct extension; not assumed native missing core.","missing_observed_positions":mapping["missing_entity_positions"],"internal_missing_positions":mapping["internal_missing_positions"]})
 return rows
def score_model(e,model,t,annotations):
 chains,ctx=read_structure(verify(model["pdb"]));assert len(chains)==2 and not ctx
 assert [x["sequence"] for x in chains]==[e["target_sequence"],e["sequence"]]
 sc=json.loads(verify(model["scores"]).read_text());n=len(e["target_sequence"]);b=len(e["sequence"]);pl=np.asarray(sc["plddt"],float)/100;pae=np.asarray(sc["pae"],float)
 assert pl.shape==(n+b,) and pae.shape==(n+b,n+b)
 declared=e["analysis_track"]=="primary_declared_entity"
 tp=t["construct_mapping"][0]["observed_to_declared_positions"] if declared else list(range(1,n+1))
 mapped_target=subset(chains[0],tp)
 ref,_=read_structure(verify(t["native_pdb"]));assert mapped_target["sequence"]==ref[0]["sequence"]
 it=interface(*chains,cutoff=5.0);pairs=it["residue_pairs"];pij=[(i-1,n+j-1) for i,j in pairs]
 d1=[pae[i,j] for i,j in pij];d2=[pae[j,i] for i,j in pij]
 ipos=[i-1 for i in it["target_residues"]]+[n+j-1 for j in it["partner_residues"]]
 conf={"AF2_global_iptm":float(sc["iptm"]),"ptm":float(sc["ptm"]),"binder_plddt":float(pl[n:].mean()),"target_plddt":float(pl[:n].mean()),"interface_plddt":float(pl[ipos].mean()) if ipos else None,"bidirectional_contact_pae":finite_summary(d1+d2),"pae_target_rows_ligand_columns_at_contacts":finite_summary(d1),"pae_ligand_rows_target_columns_at_contacts":finite_summary(d2),"pae_all_target_rows_ligand_columns":finite_summary(pae[:n,n:].ravel()),"pae_all_ligand_rows_target_columns":finite_summary(pae[n:,:n].ravel()),"interface_target_residue_denominator":len(it["target_residues"]),"interface_ligand_residue_denominator":len(it["partner_residues"]),"contact_residue_pair_denominator":len(pairs),"plddt_scale":"0..1","directional_pair_iptm":None,"directional_pair_iptm_status":"NOT_AVAILABLE_IN_AF2_SCORE_JSON_NOT_SUBSTITUTED"}
 baseline=bool(conf["AF2_global_iptm"]>=.75 and conf["binder_plddt"]>=.8 and conf["interface_plddt"] is not None and conf["interface_plddt"]>=.8 and conf["bidirectional_contact_pae"]["mean"] is not None and conf["bidirectional_contact_pae"]["mean"]<=8.)
 coreit=interface(mapped_target,chains[1],cutoff=5.0)
 target_ann=annotations[0]
 if declared:
  tag_positions=target_ann["non_uniprot_mapped_positions"];natural_positions=target_ann["uniprot_mapped_positions"]
 else:
  original=t["construct_mapping"][0]["observed_to_declared_positions"]
  tag_positions=[i+1 for i,p in enumerate(original) if p in target_ann["non_uniprot_mapped_positions"]]
  natural_positions=[i+1 for i,p in enumerate(original) if p in target_ann["uniprot_mapped_positions"]]
 plddt_regions={"full_query_target":finite_summary(pl[:n]),"experimental_observed_target_core":finite_summary([pl[i-1] for i in tp]),"uniprot_mapped_target_sequence":finite_summary([pl[i-1] for i in natural_positions]),"tag_linker_or_unmapped_target_extension":finite_summary([pl[i-1] for i in tag_positions]),"full_query_ligand":finite_summary(pl[n:])}
 coverage={"query_target_length":n,"query_ligand_length":b,"experimentally_observed_target_length":len(tp),"target_observed_fraction_of_query":len(tp)/n,"target_mapped_positions":tp,"full_predicted_sequences_verified":True,"target_tag_or_extension_positions":tag_positions,"uniprot_mapped_target_positions":natural_positions}
 nativeit=interface(*ref,cutoff=5.0);nativepairs={tuple(x) for x in nativeit["residue_pairs"]}
 r,translation,trmsd=superpose(ca(mapped_target),ca(ref[0]))
 geom={"target_CA_RMSD_on_observed_core_A":float(trmsd),"experimental_reference_contact_pairs":len(nativepairs),"reference_target_interface_residues":len(nativeit["target_residues"])}
 recovered=None
 if e["role"]=="native":
  lp=t["construct_mapping"][1]["observed_to_declared_positions"] if declared else list(range(1,b+1));ml=subset(chains[1],lp);assert ml["sequence"]==ref[1]["sequence"]
  mpairs={tuple(x) for x in interface(mapped_target,ml,cutoff=5.0)["residue_pairs"]};intersection=len(mpairs&nativepairs)
  lrmsd=float(np.sqrt(np.mean(np.sum((ca(ml)@r+translation-ca(ref[1]))**2,axis=1))))
  geom.update(ligand_CA_RMSD_after_target_alignment_A=lrmsd,ligand_CA_RMSD_after_self_alignment_A=float(superpose(ca(ml),ca(ref[1]))[2]),native_contact_recall=intersection/len(nativepairs) if nativepairs else None,native_contact_recall_numerator=intersection,native_contact_recall_denominator=len(nativepairs),predicted_observed_contact_pairs=len(mpairs),native_contact_precision=intersection/len(mpairs) if mpairs else None,predicted_observed_residue_contact_pairs=sorted(mpairs))
  coverage.update(experimentally_observed_ligand_length=len(lp),ligand_observed_fraction_of_query=len(lp)/b,ligand_mapped_positions=lp)
  plddt_regions["experimental_observed_ligand"]=finite_summary([pl[n+i-1] for i in lp])
  ligandann=annotations[1]
  ltag=ligandann["non_uniprot_mapped_positions"] if declared else [i+1 for i,p in enumerate(t["construct_mapping"][1]["observed_to_declared_positions"]) if p in ligandann["non_uniprot_mapped_positions"]]
  plddt_regions["tag_linker_or_unmapped_ligand_extension"]=finite_summary([pl[n+i-1] for i in ltag])
  recovered=bool(baseline and lrmsd<=5.0 and geom["native_contact_recall"] is not None and geom["native_contact_recall"]>=.5)
 else:
  covered=len(set(coreit["target_residues"])&set(nativeit["target_residues"]))
  moved_ligand=np.concatenate(chains[1]["heavy"])@r+translation;native_ligand=np.concatenate(ref[1]["heavy"]);dist=cdist(moved_ligand,native_ligand)
  geom.update(native_target_interface_coverage=covered/len(nativeit["target_residues"]),native_target_interface_coverage_numerator=covered,native_target_interface_coverage_denominator=len(nativeit["target_residues"]),candidate_fraction_at_native_target_interface=covered/len(coreit["target_residues"]) if coreit["target_residues"] else None,aligned_candidate_native_ligand_atom_pairs_under_2A=int((dist<2).sum()),competition_geometry_note="Spatial occupancy diagnostic only; not experimental blockade",design_pose_RMSD_status="NOT_ESTIMABLE_ORIGINAL_BACKBONE_UNAVAILABLE")
 return {"condition_id":e["condition_id"],"target":e["target"],"ligand_id":e["ligand_id"],"role":e["role"],"analysis_track":e["analysis_track"],"model":model["model"],"seed":model["seed"],"pdb":model["pdb"],"scores":model["scores"],"confidence":conf,"baseline_confidence_pass":baseline,"native_control_recovery_pass":recovered,"coverage":coverage,"plddt_regions":plddt_regions,"interface_full_query":it,"interface_observed_target_core":coreit,"geometry":geom,"sterics":atom_overlap(*chains)}
def main(array):
 acceptpath=S/"outputs"/("acceptance_"+array+".json");acc=json.loads(acceptpath.read_text());assert acc["status"]=="ALL_225_SPECIFICITY_MODELS_VERIFIED"
 plan=json.loads(verify(acc["plan"]).read_text());targets={t["target"]:t for t in plan["targets"]};annotations={g:construct_annotation(t) for g,t in targets.items()}
 out=S/"outputs"/("analysis_"+array);out.mkdir(exist_ok=False)
 rows=[];conditions={}
 for condition in acc["accepted_conditions"]:
  e=condition["condition"];models=[]
  for model in condition["models"]:models.append(score_model(e,model,targets[e["target"]],annotations[e["target"]]))
  assert len(models)==15;conditions[e["condition_id"]]=e;rows.extend(models)
  print("SCORED",e["condition_id"],flush=True)
 # Explicit additional complete KEAP1 core arm: 45 accepted candidates plus this run's 15 observed native predictions.
 old=json.loads(verify(plan["context_only_AF2_acceptance"]).read_text());oldplan=json.loads(verify(old["plan"]).read_text())
 for condition in old["accepted_entries"]:
  if condition["mode"]!="complex":continue
  olde=next(e for e in oldplan["entries"] if e["id"]==condition["id"] and e["mode"]=="complex")
  e={"condition_id":"KEAP1__"+condition["id"]+"__observed_core_arm","target":"KEAP1","ligand_id":condition["id"],"role":"candidate","analysis_track":"additional_KEAP1_observed_core_arm","target_sequence":olde["target_sequence"],"sequence":olde["sequence"]}
  assert e["target_sequence"]==targets["KEAP1"]["construct_mapping"][0]["observed_sequence"]
  conditions[e["condition_id"]]=e
  for model in condition["models"]:rows.append(score_model(e,model,targets["KEAP1"],annotations["KEAP1"]))
 summary=[]
 for cid,e in conditions.items():
  xs=[r for r in rows if r["condition_id"]==cid];passes=[x for x in xs if x["native_control_recovery_pass"]]
  d={"condition_id":cid,"target":e["target"],"ligand_id":e["ligand_id"],"role":e["role"],"analysis_track":e["analysis_track"],"model_denominator":len(xs),"baseline_confidence_pass_count":sum(x["baseline_confidence_pass"] for x in xs),"native_control_recovery_count":len(passes) if e["role"]=="native" else None,"native_positive_adequate":bool(len(passes)>=8 and len({x["seed"] for x in passes})>=2) if e["role"]=="native" else None,"AF2_global_iptm":finite_summary([x["confidence"]["AF2_global_iptm"] for x in xs]),"contact_pae":finite_summary([x["confidence"]["bidirectional_contact_pae"]["mean"] for x in xs if x["confidence"]["bidirectional_contact_pae"]["mean"] is not None]),"native_ligand_pose_RMSD_A":finite_summary([x["geometry"]["ligand_CA_RMSD_after_target_alignment_A"] for x in xs if "ligand_CA_RMSD_after_target_alignment_A" in x["geometry"]]),"native_contact_recall":finite_summary([x["geometry"]["native_contact_recall"] for x in xs if x["geometry"].get("native_contact_recall") is not None])}
  summary.append(d)
 for d in summary:
  if d["role"]=="candidate":
   track="primary_declared_entity" if d["analysis_track"]=="primary_declared_entity" else "sensitivity_observed_construct"
   control=next(x for x in summary if x["target"]==d["target"] and x["role"]=="native" and x["analysis_track"]==track)
   d["matched_native_condition"]=control["condition_id"];d["matched_native_adequate"]=control["native_positive_adequate"]
   d["specificity_status"]="NATIVE_CONTROL_INADEQUATE_LOW_SCORES_NOT_INTERPRETABLE" if not control["native_positive_adequate"] else "COMPUTATIONAL_COUNTERSCREEN_ONLY_NOT_PROOF_OF_ABSENT_BINDING"
 report={"status":"MATCHED_SPECIFICITY_REVIEW_COMPLETE","job":os.environ.get("SLURM_JOB_ID"),"plan":rec(S/"plan.json"),"technical_acceptance":rec(acceptpath),"new_models":225,"reused_context_models":45,"scored_models_total":len(rows),"primary_model_denominator":180,"observed_native_sensitivity_denominator":45,"additional_KEAP1_core_arm":{"models":60,"native_new_observed_models":15,"candidate_reused_models":45,"overlap_warning":"15 native models are also in sensitivity; not added again to total unique models."},"construct_annotations":annotations,"conditions":summary,"confidence_baseline_definition":plan["analysis"]["confidence_baseline"],"native_positive_definition":plan["analysis"]["positive_adequacy"],"claims":{"experimental_specificity":False,"experimental_binding":False,"experimental_blockade":False,"workflow_superiority":False,"old_predictions_restored":False},"limitations":["Known PDB structures can overlap model training; these are diagnostics, not blind generalization results.","Seeds/models are technical perturbations, not independent experiments.","Declared and observed target constructs have separately retrieved, frozen target MSAs; construct sensitivity includes potential MSA changes.","Global AF2 ipTM is not Boltz minimum directional pair ipTM.","Missing experimental residues are not included in RMSD/contact reference comparisons; full query coverage and core/tag confidence are explicitly retained.","Low candidate confidence cannot establish absence of binding even where positive controls recover."]}
 assert len(rows)==270
 dump(out/"all_model_metrics.json",{"models":rows});dump(out/"summary.json",report)
 with (out/"condition_summary.tsv").open("x") as f:
  fields=["condition_id","target","ligand_id","role","analysis_track","model_denominator","baseline_confidence_pass_count","native_control_recovery_count","native_positive_adequate","matched_native_adequate","specificity_status"]
  writer=csv.DictWriter(f,fieldnames=fields,delimiter="\t",extrasaction="ignore");writer.writeheader();writer.writerows(summary)
 manifest={"status":"SPECIFICITY_ALL_NEW_AND_CONTEXT_MODELS_SCORED","inputs":[rec(acceptpath),rec(S/"plan.json")],"outputs":[rec(out/"all_model_metrics.json"),rec(out/"summary.json"),rec(out/"condition_summary.tsv")],"counts":{"new_models":225,"context_models":45,"unique_scored_models":270},"job":os.environ.get("SLURM_JOB_ID")}
 dump(out/"manifest.json",manifest);print(json.dumps(manifest,indent=2),flush=True)
if __name__=="__main__":main(sys.argv[1])

