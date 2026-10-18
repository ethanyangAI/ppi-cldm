#!/usr/bin/env python3
import hashlib,json,os,pickle
from pathlib import Path
import numpy as np
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";O=S/f"runs/pilot_failure_diag_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
manifest_path=R/"steps/22_matched_benchmark/input_preparation/prepared_7_13010/KEAP1_2FLU/input_manifest.json";target=json.loads(manifest_path.read_text());expected=target["target_sequence"]
base=R/"steps/22_matched_benchmark/engineering_pilot/runs/13069_0/attempts/000000/generated";pdb=base/"backbone_1436254356.pdb";trbpath=base/"backbone_1436254356.trb"
parser=PDBParser(QUIET=True);native=parser.get_structure("rfd",pdb)[0];reference=parser.get_structure("target",target["target_pdb"]["path"])[0]
trb=pickle.loads(trbpath.read_bytes())
def safe(v):
 if isinstance(v,dict):return {str(k):safe(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [safe(x) for x in v]
 if isinstance(v,np.ndarray):return safe(v.tolist())
 if isinstance(v,np.generic):return v.item()
 return v if isinstance(v,(str,int,float,bool)) or v is None else repr(v)
chains={}
for chain in native:
 rs=[r for r in chain if r.id[0]==" "];seq="".join(seq1(r.resname) for r in rs)
 chains[chain.id]={"count":len(rs),"sequence":seq,"residue_ids":[r.id[1] for r in rs],"atoms_per_residue":[[a.name for a in r] for r in rs],"matches_expected_target":seq==expected,"mismatches_vs_expected_target":[{"index":i+1,"got":aa,"expected":bb} for i,(aa,bb) in enumerate(zip(seq,expected)) if aa!=bb] if len(seq)==len(expected) else None}
mapped=[]
for ref,hal in zip(trb.get("con_ref_pdb_idx",[]),trb.get("con_hal_pdb_idx",[])):
 r=reference[ref[0]][ref[1]];n=native[hal[0]][hal[1]]
 mapped.append({"input":safe(ref),"output":safe(hal),"input_residue":r.resname,"output_residue":n.resname,"atom_displacements_angstrom":{a:float(np.linalg.norm(r[a].coord-n[a].coord)) for a in ["N","CA","C","O"] if a in r and a in n}})
result={"status":"ACTUAL_RF_GENERATED_COMPLEX_IDENTITY_DIAGNOSED_CPU","pdb":rec(pdb),"trb":rec(trbpath),"target_manifest":rec(manifest_path),"chains":chains,"trb_keys":list(trb),"trb_mapping":{k:safe(v) for k,v in trb.items() if k not in ["plddt","config"]},"trb_config":safe(trb["config"]),"mapped_target_residues":mapped,"mapped_target_count":len(mapped),"mapped_backbone_displacement_max_angstrom":max(v for row in mapped for v in row["atom_displacements_angstrom"].values()) if mapped else None,"cpu_only":True}
(O/"diagnosis.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({"chains":{k:{"count":v["count"],"sequence":v["sequence"],"matches_expected_target":v["matches_expected_target"],"mismatches":v["mismatches_vs_expected_target"]} for k,v in chains.items()},"mapped_target_count":len(mapped),"mapped_backbone_displacement_max_angstrom":result["mapped_backbone_displacement_max_angstrom"],"trb_keys":list(trb)},indent=2))

