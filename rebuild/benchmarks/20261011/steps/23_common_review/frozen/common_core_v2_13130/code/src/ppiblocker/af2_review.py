"""Separate confidence, fold, pose, sterics, and relaxation; never equate them to binding."""
import numpy as np
from scipy.spatial.distance import cdist
from .common import require,read_json,verify_file
from .structure import read_structure,interface,competition,superpose
RADII={"C":1.70,"N":1.55,"O":1.52,"S":1.80,"P":1.80}
BACKBONE={"N","CA","C","O"}
def atom_overlap(a,b):
 aa=[v for row in a["atoms"] for v in row];bb=[v for row in b["atoms"] for v in row]
 require(bool(aa) and bool(bb),"EMPTY_ATOMS","Cannot assess clashes")
 require(all(x[1] in RADII for x in aa+bb),"UNKNOWN_VDW_ELEMENT","No silent radius fallback")
 d=cdist([v[2] for v in aa],[v[2] for v in bb])
 radii=np.array([RADII[v[1]] for v in aa])[:,None]+np.array([RADII[v[1]] for v in bb])[None,:]
 mask=np.array([v[0] in BACKBONE for v in aa])[:,None]&np.array([v[0] in BACKBONE for v in bb])[None,:]
 overlaps=radii-d
 return dict(minimum_heavy_distance=float(d.min()),pairs_under_1_5A=int((d<1.5).sum()),backbone_pairs_under_1_5A=int(((d<1.5)&mask).sum()),vdw_overlap_pairs_over_0_4A=int((overlaps>.4).sum()),backbone_vdw_overlap_pairs_over_0_4A=int(((overlaps>.4)&mask).sum()),maximum_vdw_overlap=float(overlaps.max()),definition="interchain heavy-atom diagnostic, not MolProbity clashscore")
def ca(c):return np.array([r["ca"] for r in c["residues"]])
def pose_distance(reference,moving,allow_binder_sequence_change=False):
 require(reference[0]["sequence"]==moving[0]["sequence"] and len(reference[1]["sequence"])==len(moving[1]["sequence"]) and (allow_binder_sequence_change or reference[1]["sequence"]==moving[1]["sequence"]),"SEQUENCE_MISMATCH","Target identity and positional binder correspondence required")
 r,t,tr=superpose(ca(moving[0]),ca(reference[0]))
 return dict(target_ca_rmsd=tr,binder_ca_after_target_alignment=float(np.sqrt(np.mean(np.sum((ca(moving[1])@r+t-ca(reference[1]))**2,axis=1)))),binder_ca_after_self_alignment=superpose(ca(moving[1]),ca(reference[1]))[2])
def inspect(entry,pdb,scores):
 cs,ctx=read_structure(pdb);require(len(cs)==2 and not ctx,"INVALID_COMPLEX",str(pdb))
 require([c["sequence"] for c in cs]==[entry["target_sequence"],entry["sequence"]],"SEQUENCE_MISMATCH",str(pdb))
 n=len(entry["target_sequence"]);m=len(entry["sequence"]);s=read_json(scores);pae=np.array(s["pae"]);plddt=np.array(s["plddt"])/100
 require(pae.shape==(n+m,n+m) and plddt.shape==(n+m,),"SCORE_SHAPE",str(scores))
 require(np.isfinite(pae).all() and np.isfinite(plddt).all(),"NONFINITE_SCORES",str(scores))
 it=interface(*cs);pairs=it["residue_pairs"];pos=[i-1 for i in it["target_residues"]]+[n+j-1 for j in it["partner_residues"]]
 errors=[pae[i-1,n+j-1] for i,j in pairs]+[pae[n+j-1,i-1] for i,j in pairs]
 confidence=dict(global_iptm=float(s["iptm"]),ptm=float(s["ptm"]),binder_plddt=float(plddt[n:].mean()),interface_plddt=float(plddt[pos].mean()) if pos else None,contact_pae=float(np.mean(errors)) if errors else None,interface_target_residues=len(it["target_residues"]),interface_binder_residues=len(it["partner_residues"]))
 design=read_structure(verify_file(entry["backbone"]))[0]
 recovery=pose_distance(design,cs,allow_binder_sequence_change=entry['role']=='candidate')
 native=None
 if entry["role"]=="candidate":
  nt,np_=read_structure(verify_file(entry["native"]))[0]
  g=competition(nt,np_,*design,*cs)
  native={k:v for k,v in g.items() if not isinstance(v,dict)}
 threshold=bool(confidence["global_iptm"]>=.75 and confidence["binder_plddt"]>=.8 and confidence["interface_plddt"] is not None and confidence["interface_plddt"]>=.8 and confidence["contact_pae"]<=8)
 return dict(confidence=confidence,sterics=atom_overlap(*cs),design_recovery=recovery,native_competition_geometry=native,legacy_confidence_only=threshold,legacy_raw_binding_proxy=threshold and it["minimum_distance"]>=1.5),cs

