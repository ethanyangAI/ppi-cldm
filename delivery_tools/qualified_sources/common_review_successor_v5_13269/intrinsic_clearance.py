#!/usr/bin/env python3
"""Predeclared CPU diagnostic only. Never selects candidates or changes locked scores."""
import json,math,re
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
POLICY=dict(schema="common_intrinsic_clearance_policy.v1",scope="ALL_FIXED_COMMON_RAW_MODEL_SLOTS_NATIVE_CANDIDATE_BOTH_ENGINES_ALL_VARIANTS",atoms="ATOM standard protein residues, non-hydrogen/non-deuterium heavy atoms; HETATM excluded",distance_units="angstrom",continuous_endpoint="minimum interchain protein-heavy atom distance",severe_flag_operator="<",severe_flag_cutoff_A=1.5,reader="single model, chains A/B, canonical full queries, no nonempty heavy atom altloc or duplicate heavy atoms",missing="typed unresolved with null distance/flag; retain denominator",ranking_or_filter_changes=False,formal_primary_R1_changes=False,experimental_negative=False,policy_declared_before_production=True)
AA3={"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}
def need(v,msg):
 if not v:raise ValueError(msg)
def parse(text):
 model_count=sum(line.startswith("MODEL ")for line in text.splitlines())
 need(model_count<=1,"Multiple MODEL blocks are ambiguous")
 atoms={"A":[],"B":[]};residues={"A":{},"B":{}};seen=set();excluded=0;ended=False;started=model_count==0
 for number,line in enumerate(text.splitlines(),1):
  if line.startswith("MODEL "):started=True;continue
  if line.startswith("ENDMDL"):ended=True;continue
  if not line.startswith("ATOM  "):continue
  need(started and not ended,"ATOM outside the single model")
  need(len(line)>=54,"Truncated ATOM record")
  chain=line[21];need(chain in atoms,"Unexpected protein chain")
  residue=line[17:20].strip();need(residue in AA3,"Noncanonical protein residue")
  name=line[12:16].strip();element=line[76:78].strip().upper()if len(line)>=78 else ""
  if not element:element=name.lstrip("0123456789")[:1].upper()
  need(bool(element)and bool(name),"Atom element/name unavailable")
  if element in{"H","D"}:excluded+=1;continue
  need(not line[16].strip(),"Nonempty heavy atom altloc is ambiguous")
  rid=line[22:26].strip();need(re.fullmatch(r"-?\d+",rid)is not None,"Invalid residue number")
  ins=line[26];key=(chain,rid,ins,residue,name)
  need(key not in seen,"Duplicate protein heavy atom");seen.add(key)
  xyz=[float(line[i:i+8])for i in(30,38,46)];need(all(math.isfinite(x)for x in xyz),"Nonfinite heavy atom coordinate")
  rkey=(rid,ins);row=residues[chain].setdefault(rkey,dict(residue_name=residue,has_CA=False))
  need(row["residue_name"]==residue,"Conflicting residue identities");row["has_CA"]|=name=="CA"
  atoms[chain].append(dict(chain=chain,residue_number=int(rid),insertion_code=ins.strip(),residue_name=residue,atom_name=name,element=element,xyz_A=xyz,pdb_line=number))
 need(all(atoms.values()),"One protein chain has no heavy atoms")
 for values in residues.values():need(all(r["has_CA"]for r in values.values()),"Protein residue lacks CA")
 queries={ch:"".join(AA3[r["residue_name"]]for r in values.values())for ch,values in residues.items()}
 return atoms,queries,excluded
def observe(text,target,binder):
 atoms,queries,excluded=parse(text);need(queries=={"A":target,"B":binder},"Full protein chain/query identity differs")
 xa=np.asarray([a["xyz_A"]for a in atoms["A"]],float);xb=np.asarray([a["xyz_A"]for a in atoms["B"]],float)
 distances,indices=cKDTree(xb).query(xa,k=1);i=int(np.argmin(distances));j=int(indices[i]);distance=float(distances[i])
 need(math.isfinite(distance)and distance>=0,"Intrinsic minimum distance not finite")
 return dict(status="INTRINSIC_HEAVY_ATOM_COORDINATE_DIAGNOSTIC_OBSERVED",minimum_distance_A=distance,severe_lt_1p5_A=distance<1.5,closest_target_atom=atoms["A"][i],closest_binder_atom=atoms["B"][j],target_heavy_atom_count=len(xa),binder_heavy_atom_count=len(xb),excluded_H_D_atoms=excluded,experimental_negative=False,filter_or_ranking_applied=False)
def diagnose(plan,scored,rawroot,locate,record,verify,out,source_receipt,source_qualification=None):
 expected=sum(j["expected_models"]for j in plan["jobs"]);scored_by={r["job_key"]:r for r in scored["results"]}if scored else {}
 entities={r["blind_id"]:r for r in plan["entities"]};rows=[]
 for index,job in enumerate(plan["jobs"]):
  byslot={json.dumps(m["slot"],sort_keys=True):m for m in scored_by.get(job["job_key"],{}).get("models",[])}
  for slot in job["slots"]:
   confidence=byslot.get(json.dumps(slot,sort_keys=True));base=dict(job_key=job["job_key"],index=index,blind_id=job["blind_id"],engine=job["engine"],variant=job["variant"],slot=slot,confidence_content_status=confidence["status"]if confidence else"NOT_SCORED_SOURCE_GATE_UNRESOLVED",source_qualification=(source_qualification or{}).get(job["job_key"],"UNRESOLVED_WORKER_LINEAGE_COORDINATES_ONLY"),minimum_distance_A=None,severe_lt_1p5_A=None,closest_target_atom=None,closest_binder_atom=None,raw_PDB=None,experimental_negative=False,filter_or_ranking_applied=False)
   try:
    p=locate(job,rawroot,slot)[0];rr=record(p);verify(rr);base["raw_PDB"]=rr
    if confidence and confidence["status"]in{"VALID","NO_INTERFACE"}:
     known=[r for r in confidence["raw_files"]if Path(r["path"]).suffix.lower()==".pdb"]
     need(len(known)==1 and known[0]==rr,"Coordinate diagnostic differs from scored raw PDB")
    e=entities[job["blind_id"]];row=observe(Path(p).read_text(),e["target_sequence"],e["binder_sequence"]);base.update(row)
   except (OSError,ValueError,KeyError,IndexError)as error:
    base.update(status="INTRINSIC_COORDINATE_DIAGNOSTIC_TYPED_UNRESOLVED",reason_type=type(error).__name__,reason=str(error))
   rows.append(base)
 need(len(rows)==expected and len({(r["job_key"],json.dumps(r["slot"],sort_keys=True))for r in rows})==expected,"Full fixed physical model denominator lost")
 result=dict(schema="common_intrinsic_clearance_diagnostic.v1",status="ALL_FIXED_COMMON_MODEL_INTRINSIC_DIAGNOSTICS_RECORDED",policy=POLICY,source=source_receipt,expected_models=expected,n_coordinate_observed=sum(r["minimum_distance_A"]is not None for r in rows),n_typed_unresolved=sum(r["minimum_distance_A"]is None for r in rows),n_severe_flag_observed=sum(r["severe_lt_1p5_A"]is True for r in rows),rows=rows,formal_112_or_scores_changed=False,experimental_binding_or_blockade=False)
 with Path(out).open("x")as f:json.dump(result,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
 return result
