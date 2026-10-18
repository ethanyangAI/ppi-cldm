import shutil
from collections import Counter
from Bio import Align
from util import *
from ppiblocker.af2_review import atom_overlap
run=Run(R,"86_strengthening_geometry",[record_file(SETUP),record_file(S/"protocol.json")]);shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 p,m=one("82_strengthening_extensions","EXTENSION_INPUTS_READY");plan=read_json(verify_file(m["outputs"]["plan"]));run.manifest["inputs"].append(record_file(p));run.save()
 refs={}
 for pdb in ("2FLU","1X2R","2DYH","3WN7"):
  refs[pdb]=chains(verify_file(plan["fetches"][pdb+".cif"]["file"]))
 if "KEAP1_AFDB.pdb" in plan["fetches"]:refs["AFDB_full"]=chains(verify_file(plan["fetches"]["KEAP1_AFDB.pdb"]["file"]))
 aligner=Align.PairwiseAligner(mode="local",match_score=2,mismatch_score=-4,open_gap_score=-6,extend_gap_score=-.5)
 rows=[]
 for e in baseplan()["candidates"]:
  native=chains(verify_file(e["native"]));it=interface(*native);weights=Counter(i for i,j in it["residue_pairs"]);motif=native[1]["sequence"].find("DEETGEFL")
  require(motif>=0,"NATIVE_MOTIF",native[1]["sequence"])
  etge={motif+3,motif+6};critical={i for i,j in it["residue_pairs"] if j in etge}
  found=[]
  for p in (R/"steps/75_af2_review_score/runs").glob("*/manifest.json"):
   mm=read_json(p)
   if mm["status"]=="AF2_REVIEW_SCORED" and mm.get("entry_id")==e["id"]:found.append((p,mm))
  require(len(found)==1,"CANDIDATE_REVIEW",e["id"]);p,mm=found[0];data=read_json(verify_file(mm["outputs"]["results"]))
  for z in data["models"]:
   if z["arm"]!="expanded":continue
   cs=chains(verify_file(z["raw_structure"]));actual=interface(*cs);covered=set(actual["target_residues"])
   metrics=dict(id=e["id"],weight=z["weight"],seed=z["seed"],native_contact_weighted_coverage=sum(v for k,v in weights.items() if k in covered)/sum(weights.values()),ETGE_glutamate_contact_residue_coverage=len(critical&covered)/max(1,len(critical)),native_contact_residues=len(weights),critical_contact_residues=sorted(critical),contexts=[])
   for refname,rc in refs.items():
    candidates=[]
    for c in rc:
     if len(c["sequence"])<200:continue
     al=aligner.align(cs[0]["sequence"],c["sequence"])[0];pairs=[(int(a),int(b)) for a,b in al.indices.T if a>=0 and b>=0];identity=sum(cs[0]["sequence"][a]==c["sequence"][b] for a,b in pairs)/max(1,len(pairs))
     if len(pairs)/len(cs[0]["sequence"])>=.9 and identity>=.95:candidates.append((c,pairs,identity))
    for c,pairs,identity in candidates:
     rr,tt,rms=superpose(ca(cs[0])[[a for a,b in pairs]],ca(c)[[b for a,b in pairs]]);binder=transform(cs[1],rr,tt);binder["id"]="projected_binder"
     mapped={b for a,b in pairs};extra=[i for i in range(len(c["sequence"])) if i not in mapped]
     extraclashes=None
     if extra:
      extra_c={**c,"atoms":[c["atoms"][i] for i in extra]}
      extraclashes=atom_overlap(extra_c,binder)
     partners=[]
     for other in rc:
      if other["id"]==c["id"]:continue
      other={**other,"id":"partner_"+other["id"]}
      ov=atom_overlap(other,binder)
      if len(other["sequence"])<100:
       refcontacts=interface(c,other);pro=interface(c,binder);a=set(refcontacts["target_residues"]);b=set(pro["target_residues"])
       partners.append(dict(chain=other["id"],sequence=other["sequence"],native_coverage=len(a&b)/max(1,len(a)),native_interface_residues=len(a),steric_overlap=ov))
      else:partners.append(dict(chain=other["id"],role="assembly_context",steric_overlap=ov))
     metrics["contexts"].append(dict(structure=refname,chain=c["id"],aligned_residues=len(pairs),identity=identity,target_ca_rmsd=rms,sequence_mismatches=[dict(target=a+1,reference=b+1) for a,b in pairs if cs[0]["sequence"][a]!=c["sequence"][b]],extra_domain_atoms_collision=extraclashes,extra_residue_mean_plddt=float(np.mean([c["residues"][i]["bfactor"] for i in extra])) if extra and refname=="AFDB_full" else None,partners=partners,interpretation="projection; not redocking; mismatches/nonhuman structures sensitivity only"))
   rows.append(metrics)
 atomic_json(run.path/"outputs/results.json",dict(models=rows,fetch_failures=plan["fetch_failures"],limitations=["Contact-derived hotspots are geometric proxies, not experimental energetic hotspots.","Projection into AFDB full-length does not validate interdomain orientation or biological dimer geometry.","2DYH/3WN7 species and mutations must be retained from entry records."]))
 run.output("results",run.path/"outputs/results.json");print(run.finish("COMPETITION_CONTEXT_COMPLETE","computational_only",dict(models=len(rows))),flush=True)
except Exception as x:run.fail(x);raise

