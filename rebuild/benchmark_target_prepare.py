#!/usr/bin/env python3
"""CPU-only target inventory and exact coordinate/sequence qualification."""
import argparse, copy, hashlib, json, time, urllib.request, traceback
from functools import lru_cache
from pathlib import Path
import numpy as np
from Bio.PDB import MMCIFParser, MMCIF2Dict, PDBIO, Structure, Model, Chain
from Bio.PDB.Polypeptide import protein_letters_3to1
from Bio.PDB.Atom import Atom as BioAtom
from Bio.PDB.Residue import Residue as BioResidue
from scipy.spatial.distance import cdist
FETCH_SOURCE_CACHE=[]
def receipt(p):
 p=Path(p); return {"path":str(p.resolve()),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,obj):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,allow_nan=False)+"\n")
def fetch(url,p):
 p=Path(p)
 if p.exists(): return receipt(p)
 for cache in FETCH_SOURCE_CACHE:
  if (cache/p.name).exists(): return receipt(cache/p.name)
 errors=[]
 for n in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"test9-reproducible-benchmark/1"}),timeout=90) as response:
    body=response.read()
   if not body: raise ValueError("empty download")
   p.parent.mkdir(parents=True,exist_ok=True); temp=p.with_suffix(p.suffix+".part"); temp.write_bytes(body); temp.replace(p)
   return receipt(p)
  except Exception as e:
   errors.append(repr(e)); time.sleep(min(2**n,8))
 raise RuntimeError({"url":url,"errors":errors})
def rows(d,key,n):
 x=d.get(key,[]); return x if isinstance(x,list) else [x]*n
@lru_cache(maxsize=32)
def atom_mapping(cif,chain):
 d=MMCIF2Dict.MMCIF2Dict(str(cif)); n=len(d["_atom_site.id"])
 labels=rows(d,"_atom_site.label_seq_id",n); authors=rows(d,"_atom_site.auth_seq_id",n)
 chains=rows(d,"_atom_site.auth_asym_id",n); codes=rows(d,"_atom_site.pdbx_PDB_ins_code",n)
 models=rows(d,"_atom_site.pdbx_PDB_model_num",n); entities=rows(d,"_atom_site.label_entity_id",n)
 mapping={}
 for ch,lab,auth,ins,model,ent in zip(chains,labels,authors,codes,models,entities):
  if ch==chain and model=="1" and lab not in (".","?"):
   mapping[(int(auth),"" if ins in (".","?") else ins)]=(int(lab),str(ent))
 entity_ids=d.get("_entity_poly.entity_id",[]); seqs=d.get("_entity_poly.pdbx_seq_one_letter_code_can",[])
 if isinstance(entity_ids,str): entity_ids=[entity_ids]; seqs=[seqs]
 seqs={str(i):"".join(s.split()) for i,s in zip(entity_ids,seqs)}
 return mapping,seqs,d
@lru_cache(maxsize=16)
def parsed_structure(cif):
 return MMCIFParser(QUIET=True).get_structure("reference",str(cif))
def extract(cif,chain,selection):
 st=parsed_structure(str(cif)); model=st[0]; mp,seqs,d=atom_mapping(cif,chain)
 found=[r for r in model[chain] if r.id[0]==" " and r.resname in protein_letters_3to1 and "CA" in r]
 allseq="".join(protein_letters_3to1[r.resname] for r in found)
 ents={mp[(r.id[1],r.id[2].strip())][1] for r in found if (r.id[1],r.id[2].strip()) in mp}
 if len(ents)!=1: raise ValueError("ambiguous entity "+str(ents))
 entity=next(iter(ents)); declared=seqs[entity]
 core=selection.get("core_sequence"); bounds=selection.get("target_range")
 if core:
  if declared.count(core)!=1: raise ValueError("exact core not uniquely found in declared sequence")
  start=declared.index(core)+1; end=start+len(core)-1
  found=[r for r in found if start<=mp[(r.id[1],r.id[2].strip())][0]<=end]
 elif bounds:
  found=[r for r in found if bounds[0]<=r.id[1]<=bounds[1]]
 if not found: raise ValueError("empty selected chain")
 sequence="".join(protein_letters_3to1[r.resname] for r in found)
 mapping=[{"normalized_index":i+1,"auth_seq_id":r.id[1],"insertion_code":r.id[2].strip(),"label_seq_id":mp[(r.id[1],r.id[2].strip())][0],"residue":protein_letters_3to1[r.resname]} for i,r in enumerate(found)]
 labels=[m["label_seq_id"] for m in mapping]; gaps=sorted(set(range(min(labels),max(labels)+1))-set(labels))
 coordinate_required_sequence=declared[min(labels)-1:max(labels)]
 if core: coordinate_required_sequence=core; gaps=sorted(set(range(start,end+1))-set(labels))
 context={"entity_id":entity,"declared_sequence":declared,"declared_length":len(declared),"observed_full_sequence":allseq,
  "selected_sequence":sequence,"selected_length":len(sequence),"mapping":mapping,"internal_missing_label_seq_ids":gaps,
  "coordinate_required_sequence":coordinate_required_sequence,
  "terminal_context_excluded":len(declared)-len(coordinate_required_sequence),
  "observed_sequence_is_coordinate_complete":sequence==coordinate_required_sequence,
  "source_chain":chain,"source_model_serial":int(getattr(model,"serial_num",1)),"source_model_count":len(list(st.get_models()))}
 return found,context,d
def write_pdb(path,chains):
 s=Structure.Structure("normalized"); m=Model.Model(0); s.add(m)
 atom_serial=0
 for name,residues in chains:
  ch=Chain.Chain(name); m.add(ch)
  for n,r in enumerate(residues,1):
   clone=BioResidue((" ",n," "),r.resname,r.segid)
   byname={}
   for atom in r.get_unpacked_list():
    if str(atom.element).upper() in ("H","D"): continue
    byname.setdefault(atom.name,[]).append(atom)
   for atomname,choices in byname.items():
    selected=sorted(choices,key=lambda a:(-(a.occupancy or 0),a.altloc!="A",a.altloc))[0]
    atom_serial+=1
    atom=BioAtom(selected.name,np.array(selected.coord,copy=True),selected.bfactor,selected.occupancy,
       " ",selected.fullname,atom_serial,element=selected.element)
    clone.add(atom)
   ch.add(clone)
 io=PDBIO(); io.set_structure(s); io.save(str(path))
 # Read-back validates atom/residue cardinality and exact observed sequence.
 from Bio.PDB import PDBParser
 recovered=PDBParser(QUIET=True).get_structure("normalized",str(path))[0]
 for name,residues in chains:
  expected="".join(protein_letters_3to1[r.resname] for r in residues)
  observed="".join(protein_letters_3to1[r.resname] for r in recovered[name])
  if expected!=observed or any("CA" not in r for r in recovered[name]): raise ValueError("normalized PDB read-back identity failure")
def contacts(target,partner):
 pairs=[]
 for i,r in enumerate(target,1):
  ta=np.array([a.coord for a in r.get_atoms() if str(a.element).upper() not in ("H","D")])
  for j,s in enumerate(partner,1):
   pa=np.array([a.coord for a in s.get_atoms() if str(a.element).upper() not in ("H","D")])
   if len(ta) and len(pa) and float(cdist(ta,pa).min())<5:
    pairs.append([i,j])
 return pairs
def prepare(spec,base):
 print("PREPARE_TARGET",spec["target_id"],flush=True)
 out=base/"targets"/spec["target_id"]; out.mkdir(parents=True,exist_ok=True); ids=sorted({spec["pdb_id"],spec.get("design_pdb_id",spec["pdb_id"])})
 sources={}
 for id in ids:
  cif=base/"sources"/(id+".cif"); entry=base/"sources"/(id+".entry.json")
  sources[id]={"cif":fetch("https://files.rcsb.org/download/"+id+".cif",cif),
   "entry":fetch("https://data.rcsb.org/rest/v1/core/entry/"+id,entry)}
 rcif=Path(sources[spec["pdb_id"]]["cif"]["path"])
 ref_target,tc,td=extract(rcif,spec["target_chain"],spec); ref_partner,pc,pd=extract(rcif,spec["partner_chain"],{})
 dcif=Path(sources[spec.get("design_pdb_id",spec["pdb_id"])]["cif"]["path"])
 target,design_tc,dd=extract(dcif,spec.get("design_target_chain",spec["target_chain"]),spec)
 entities={}
 for id,ch,context in [(spec["pdb_id"],spec["target_chain"],tc),(spec["pdb_id"],spec["partner_chain"],pc),(spec.get("design_pdb_id",spec["pdb_id"]),spec.get("design_target_chain",spec["target_chain"]),design_tc)]:
  key=id+"_"+context["entity_id"]
  if key not in entities:
   path=base/"sources"/(key+".entity.json"); rec=fetch("https://data.rcsb.org/rest/v1/core/polymer_entity/"+id+"/"+context["entity_id"],path)
   entities[key]={"receipt":rec,"metadata":json.loads(Path(rec["path"]).read_text())}
 if spec.get("target_uniprot"):
  md=entities[spec.get("design_pdb_id",spec["pdb_id"])+"_"+design_tc["entity_id"]]["metadata"]
  ids=md.get("rcsb_polymer_entity_container_identifiers",{}).get("uniprot_ids",[])
  if spec["target_uniprot"] not in ids: raise ValueError("target UniProt mismatch: "+str(ids))
 target_path=out/"target_observed.pdb"; reference_path=out/"reference_complex.pdb"
 write_pdb(target_path,[("A",target)]); write_pdb(reference_path,[("A",ref_target),("B",ref_partner)])
 (out/"target_observed.fasta").write_text(">"+spec["target_id"]+"\n"+design_tc["selected_sequence"]+"\n")
 (out/"target_coordinate_required.fasta").write_text(">"+spec["target_id"]+"\n"+design_tc["coordinate_required_sequence"]+"\n")
 interface_pairs=contacts(ref_target,ref_partner)
 byres={}
 for i,j in interface_pairs: byres[i]=byres.get(i,0)+1
 if not byres: raise ValueError("selected target and specified partner have no 5A contacts")
 # Target IDs are common even when the design coordinates are unbound.
 shared={}
 reference_labels={x["label_seq_id"]:x["normalized_index"] for x in tc["mapping"]}
 for x in design_tc["mapping"]:
  if x["label_seq_id"] in reference_labels: shared[x["normalized_index"]]=reference_labels[x["label_seq_id"]]
 ranked=sorted(byres,key=lambda k:(-byres[k],k))
 hotspots=[]
 for refi in ranked:
  available=[di for di,ri in shared.items() if ri==refi]
  if available: hotspots.append(available[0])
  if len(hotspots)==3: break
 if len(hotspots)!=3: raise ValueError("fewer than three mapped common hotspots")
 excluded_nonproteins={}
 for dictionary in (td,dd):
  components=dictionary.get("_pdbx_entity_nonpoly.comp_id",[])
  if isinstance(components,str): components=[components]
  for v in components:
   if v!="HOH": excluded_nonproteins[v]=True
 status="INPUT_QUALIFIED" if design_tc["observed_sequence_is_coordinate_complete"] else "TARGET_ONLY_COORDINATE_REPAIR_REQUIRED"
 result={"schema_version":"target_identity.v1","status":status,"spec":spec,"sources":sources,"entity_receipts":{k:v["receipt"] for k,v in entities.items()},
  "target_context":design_tc,"reference_target_context":tc,"reference_partner_context":pc,
  "design_structure":receipt(target_path),"reference_complex":receipt(reference_path),
  "reference_5A_residue_pairs":interface_pairs,"reference_interface_target_residues":sorted(byres),
  "hotspots":hotspots,"hotspots_format":"A"+",A".join(map(str,hotspots)),
  "design_to_reference_indices":shared,"excluded_nonprotein_components":sorted(excluded_nonproteins),
  "binder_length":65,"source_model_policy":"deposited_model_1_fixed_before_design","atom_altloc_policy":"maximum_occupancy_A_wins_ties_rebuild_atoms_without_parent_graph",
  "evidence_boundaries":["coordinate-conditioned computational design","not experimental binding or blockade","protein-only omitted-context limitations retained","no generation yet"]}
 save(out/"identity.json",result); result["identity_receipt"]=receipt(out/"identity.json"); return result
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--matrix",required=True); ap.add_argument("--out",required=True); ap.add_argument("--source-cache",action="append",default=[]); a=ap.parse_args()
 global FETCH_SOURCE_CACHE
 FETCH_SOURCE_CACHE=[Path(x) for x in a.source_cache]
 base=Path(a.out); base.mkdir(parents=True,exist_ok=True); specs=json.loads(Path(a.matrix).read_text())["targets"]; results=[]; failures=[]
 for spec in specs:
  try: results.append(prepare(spec,base))
  except Exception as exc:
   print("TARGET_FAILURE",spec["target_id"],repr(exc),flush=True)
   failures.append({"target_id":spec["target_id"],"error":repr(exc),"traceback":traceback.format_exc()})
 report={"schema_version":"target_matrix_preparation.v1","preparation_source":receipt(__file__),"matrix_receipt":receipt(a.matrix),"slurm_job_id":__import__("os").environ.get("SLURM_JOB_ID"),"target_count":len(specs),
  "qualified_target_count":sum(r["status"]=="INPUT_QUALIFIED" for r in results),"coordinate_repair_target_count":sum(r["status"]=="TARGET_ONLY_COORDINATE_REPAIR_REQUIRED" for r in results),"failures":failures,"targets":results,
  "status":"COMPLETE_INPUT_INVENTORY" if len(results)==len(specs) else "INPUT_INVENTORY_HAS_TYPED_FAILURES"}
 save(base/"inventory.json",report); print(json.dumps({k:report[k] for k in ("status","target_count","qualified_target_count","coordinate_repair_target_count","failures")}))
 if failures: raise SystemExit(2)
if __name__=="__main__": main()

