"""Separate, fixed confidence baseline scored for all technically valid models."""
import os,sys,json,math,hashlib
from pathlib import Path
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/17_control_calibration"
sys.path.insert(0,str(R/"source/rebuild"))
from control_review import rec,verify,dump
def baseline(iptm,binder,interface,pae):
 vals=(iptm,binder,interface,pae)
 if any(x is None or not math.isfinite(float(x)) for x in vals):return None
 if not(0<=iptm<=1 and 0<=binder<=1 and 0<=interface<=1 and pae>=0):return None
 ratios=[iptm/.75,binder/.8,interface/.8]
 if pae>0:ratios.append(8/pae)
 return min(ratios)
def summarize(values,expected=15):
 import numpy as np
 good=[float(x) for x in values if x is not None and math.isfinite(x)]
 full=len(good)==expected and len(values)==expected
 return {"n_expected":expected,"n_valid":len(good),"n_missing":expected-len(good),"median":float(np.median(good)) if full else None,"observed_only_median":float(np.median(good)) if good else None,"min":min(good) if good else None,"max":max(good) if good else None}
def contact_pairs(a_xyz,a_res,b_xyz,b_res,cutoff=5.0):
 from scipy.spatial import cKDTree
 tree=cKDTree(b_xyz);out=set()
 for i,hits in enumerate(tree.query_ball_point(a_xyz,r=cutoff)):
  for j in hits:out.add((int(a_res[i]),int(b_res[j])))
 return sorted(out)
def score_model(m):
 import numpy as np
 from Bio.PDB import PDBParser
 pp=verify(m["pdb"]);sp=verify(m["scores"]);sc=json.loads(sp.read_text())
 st=PDBParser(QUIET=True).get_structure("x",pp);chains=list(next(st.get_models()));assert len(chains)==2
 residues=[[r for r in c if r.id[0]==" "] for c in chains];nA=len(residues[0]);nB=len(residues[1]);arrays=[]
 for rs in residues:
  coords=[];indices=[]
  for i,r in enumerate(rs):
   for atom in r:
    if atom.element not in ("H","D"):
     coords.append(atom.coord);indices.append(i)
  arrays.append((np.asarray(coords),indices))
 pairs=contact_pairs(*arrays[0],*arrays[1])
 plddt=np.asarray(sc["plddt"],float)/100;pae=np.asarray(sc["pae"],float)
 binder=float(plddt[nA:].mean());target=float(plddt[:nA].mean());iptm=float(sc["iptm"]);ptm=float(sc["ptm"])
 if pairs:
  ia=np.array([a for a,b in pairs]);ib=np.array([b+nA for a,b in pairs]);a_to_b=float(pae[ia,ib].mean());b_to_a=float(pae[ib,ia].mean());both=(a_to_b+b_to_a)/2
  interface=float(plddt[np.unique(np.concatenate((ia,ib)))].mean())
 else:a_to_b=b_to_a=both=interface=None
 value=baseline(iptm,binder,interface,both)
 return {"model":m["model"],"seed":m["seed"],"global_iptm":iptm,"global_ptm":ptm,"target_plddt":target,"binder_plddt":binder,"interface_plddt":interface,"contact_PAE_A_to_B":a_to_b,"contact_PAE_B_to_A":b_to_a,"bidirectional_contact_PAE_A":both,"contact_residue_pair_count":len(pairs),"target_contact_residue_count":len({a for a,b in pairs}),"binder_contact_residue_count":len({b for a,b in pairs}),"confidence_baseline":value,"baseline_pass":value>=1 if value is not None else None,"missing_reason":None if value is not None else "No cross-chain heavy-atom contact residue pairs at 5 A","pdb":m["pdb"],"scores":m["scores"]}
def test():
 import numpy as np
 assert baseline(.9,.8,.8,8)==1
 assert baseline(.9,.8,.8,0)==1
 assert abs(baseline(.3,.8,.8,8)-.4)<1e-12
 assert baseline(.9,.8,None,8) is None and baseline(.9,.8,.8,float("nan")) is None
 assert baseline(.9,.8,.8,-1) is None
 assert summarize([1]*14)["median"] is None
 assert summarize([1]*14+[None])["n_missing"]==1
 assert summarize([0]*15)["median"]==0
 # Duplicate atom contacts must not multiply the residue-pair PAE denominator.
 assert contact_pairs(np.array([[0.,0,0],[0.1,0,0],[20,0,0]]),[0,0,1],np.array([[1.,0,0],[2,0,0]]),[0,0])==[(0,0)]
 assert contact_pairs(np.array([[0.,0,0]]),[0],np.array([[20.,0,0]]),[0])==[]
 print("CONTROL_SCORING_TESTS_PASSED",flush=True)
def score(array):
 ap=S/"outputs"/("acceptance_"+array+".json");acc=json.loads(ap.read_text());assert acc["status"]=="ALL_1170_CONTROL_MODELS_VERIFIED" and acc["model_count"]==1170
 verify(acc["plan"]);verify(acc["msa_acceptance"]);plan=json.loads(verify(acc["plan"]).read_text());test();results=[];allrows=[]
 keys=("global_iptm","global_ptm","target_plddt","binder_plddt","interface_plddt","bidirectional_contact_PAE_A","confidence_baseline")
 for row in acc["accepted_conditions"]:
  e=row["condition"];models=[score_model(m) for m in row["models"]]
  summaries={k:summarize([m[k] for m in models]) for k in keys}
  item={"id":e["condition_id"],"source_id":e["source_id"],"target":e["target"],"historical_binding_label":e["historical_binding_label"],"target_sequence_sha256":e["target_sequence_sha256"],"sequence_sha256":e["sequence_sha256"],"model_count":len(models),"confidence_baseline_median":summaries["confidence_baseline"]["median"],"confidence_baseline_n_valid":summaries["confidence_baseline"]["n_valid"],"confidence_baseline_n_missing":summaries["confidence_baseline"]["n_missing"],"baseline_pass_count":sum(m["baseline_pass"] is True for m in models),"baseline_missing_count":sum(m["baseline_pass"] is None for m in models),"metrics":summaries,"models":models}
  results.append(item);allrows.extend([{"id":item["id"],"target":item["target"],**m} for m in models])
  print("SCORED",item["id"],item["confidence_baseline_median"],flush=True)
 modelp=S/"outputs"/("model_scores_"+array+".json");dump(modelp,{"status":"ALL_1170_TECHNICALLY_ACCEPTED_MODELS_SCORED","acceptance":rec(ap),"rows":allrows},True)
 out={"status":"ALL_78_CONTROLS_SCORED_WITH_EXPLICIT_MISSINGNESS","job_id":os.environ.get("SLURM_JOB_ID"),"array_job_id":array,"plan":rec(S/"plan.json"),"acceptance":rec(ap),"model_scores":rec(modelp),"counts":{"identities":len(results),"models":len(allrows),"complete_confidence_identities":sum(r["confidence_baseline_n_valid"]==15 for r in results),"missing_confidence_models":sum(r["confidence_baseline_n_missing"] for r in results)},"scoring":plan["scoring"],"entries":results,"qualification":"This output models every frozen control. Eligibility determined solely by independently frozen step18 manifest. Scores are not binding/blockade truth."}
 p=S/"outputs"/("score_summary_"+array+".json");dump(p,out,True);dump(S/"outputs/score_summary.json",{"status":out["status"],"receipt":rec(p)},True)
 print(json.dumps({"status":out["status"],"counts":out["counts"],"summary":rec(p)},indent=2),flush=True)
if __name__=="__main__":
 if sys.argv[1]=="test":test()
 elif sys.argv[1]=="score":score(sys.argv[2])
 else:raise ValueError(sys.argv[1])

