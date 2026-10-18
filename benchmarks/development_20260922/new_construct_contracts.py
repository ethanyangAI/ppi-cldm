import json,shutil,copy
from pathlib import Path
import numpy as np
from Bio.PDB import MMCIFParser,PDBIO
from ppiblocker.common import Run,read_json,verify_file,record_file,atomic_json,require
from ppiblocker.structure import read_structure,interface,superpose
from ppiblocker.pipeline import prepare,validate_design_pose
root=Path("/lustre/users/u21111210118/projects/test9")
review=root/"steps/37_construct_review/runs/20260922T100601Z_2b659c0c0597/outputs/constructs.json"
run=Run(root,"56_new_construct_contracts",[record_file(review)])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 cases={r["id"]:r for r in read_json(review)};base=read_json(root/"steps/01_pose/runs/20260920T125042Z_8e4ecd8ead82/outputs/config.json")
 r=cases["N02"]["candidates"][0];cfg=copy.deepcopy(base)
 require(r["pdb"]=="2PE6","REFERENCE_CHANGED","N02")
 cfg["proteins"]=[dict(id="UBE2I_GSH_tagged_1_158",sequence=r["identities"][0]["observed_sequence"],taxon=9606,
  construct_provenance=dict(reference_uniprot="P63279",canonical_residues=[1,158],n_terminal_tag="GSH",source=r["source"])),
  dict(uniprot="P63165",taxon=9606,residues=[21,94])]
 require(cfg["proteins"][0]["sequence"]=="GSH"+r["identities"][0]["canonical_sequence"],"TAG_IDENTITY","Unexpected variant")
 cfg["structure"]=dict(pdb="2PE6",assembly=r["assembly"],chains=r["chains"])
 cfg["context_review"]=dict(native_interaction_supported=True,interaction_evidence="https://doi.org/10.1016/j.jmb.2007.04.006; RCSB author-assigned noncovalent human Ubc9-SUMO1 binary assembly",
  soluble_construct=True,no_required_unmodelled_context=True,
  restricted_scope="Explicit GSH-tagged UBE2I with observed SUMO1 21-94 core; not full-length SUMO conjugation, not catalytic-state or full assay replication",
  context_exclusions="No E1/E3, covalent SUMO thioester, poly-SUMO chain, or cellular function claims")
 p=run.path/"outputs/N02_tagged_core.json";atomic_json(p,cfg);run.output("N02_config",p)
 mp=prepare(root,p);m=read_json(mp);validate_design_pose(m);run.output("N02_pose",mp)
 n=cases["N10"]["candidates"][0]
 from ppiblocker.identity import Repository
 repo=Repository(root/"cache/nmr_ensemble")
 raw=repo.get("https://files.rcsb.org/download/2ASQ.cif",binary=True)
 atomic_json(run.path/"outputs/ensemble_retrieval.json",repo.receipts);run.output("ensemble_retrieval",run.path/"outputs/ensemble_retrieval.json")
 structure=MMCIFParser(QUIET=True,auth_chains=False).get_structure("nmr",raw)
 models=[];references=[]
 for k,model in enumerate(structure):
  p=run.path/"work"/f"N10_model_{k:02d}.pdb";io=PDBIO();io.set_structure(model);io.save(str(p))
  cs,context=read_structure(p);require(len(cs)==2 and not context,"NMR_CONTEXT",str(k))
  require([c["sequence"] for c in cs]==[x["observed_sequence"] for x in n["identities"]],"NMR_SEQUENCE",str(k))
  models.append(cs);references.append(record_file(p))
 require(len(models)==10,"NMR_ENSEMBLE_COUNT",str(len(models)))
 ca=lambda c:np.array([r["ca"] for r in c["residues"]])
 rmsd=np.zeros((len(models),len(models)));jaccard=np.ones_like(rmsd)
 contacts=[set(map(tuple,interface(*cs)["residue_pairs"])) for cs in models]
 for i,(t,b) in enumerate(models):
  for j,(tt,bb) in enumerate(models):
   R,T,_=superpose(ca(tt),ca(t));rmsd[i,j]=np.sqrt(np.mean(np.sum((ca(bb)@R+T-ca(b))**2,axis=1)))
   jaccard[i,j]=len(contacts[i]&contacts[j])/len(contacts[i]|contacts[j])
 medoid=int(np.argmin(rmsd.mean(axis=1)))
 result=dict(N02=dict(status="EXPLICIT_TAGGED_CORE_DESIGN_INPUT_ACCEPTED",pose=record_file(mp),not_canonical_untagged=True,assay_construct_replication=False),
  N10=dict(status="NMR_ENSEMBLE_CHALLENGE_RETAINED",references=references,source=record_file(raw),models=10,
   target="SUMO1_21_97",partner="PIAS2_466_479",target_aligned_partner_RMSD=rmsd.tolist(),contact_jaccard=jaccard.tolist(),medoid_zero_index=medoid,
   medoid_selection="minimum_mean_pairwise_partner_CA_RMSD_after_target_alignment_before_design",requirement="Future design validation must report all ten references; single-model score is insufficient",assay_construct_replication=False),
  main_six_target_gate="NO_GO_NOT_SIX_INDEPENDENT_QUALIFIED_TARGETS",family_dependency="N02 and N10 share SUMO1 and must not be assigned to independent train/test groups")
 atomic_json(run.path/"outputs/contracts.json",result);run.output("contracts",run.path/"outputs/contracts.json")
 print(run.finish("ADDITIONAL_CONSTRUCT_CONTRACTS_REVIEWED","design_inputs_not_benchmark_results"),flush=True)
 print("N02",m["status"],"N10_models",len(models),"RMSD_range",float(rmsd.max()),"Jaccard_min",float(jaccard.min()),flush=True)
except Exception as e:run.fail(e);raise
