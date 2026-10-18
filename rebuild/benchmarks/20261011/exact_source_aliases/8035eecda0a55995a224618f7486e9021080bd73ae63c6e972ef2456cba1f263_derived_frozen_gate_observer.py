def validate_rfd_output(output_pdb,trb_path,target):
 """Verify official Sampler PDB identity using TRB full-complex indices.

 receptor_con_hal_idx0 is receptor-local, while complex_con_hal_idx0 addresses
 the binder-first full output. ContigMap hal chain labels are abstract; the
 pinned Sampler preserves the source target chain and assigns new binder B.
 Final px0 is all-atom reconstructed, so target-coordinate differences are
 recorded, not silently overwritten or filtered by a posthoc tolerance.
 """
 import pickle
 import numpy as np
 from Bio.PDB import PDBParser
 from Bio.SeqUtils import seq1
 output_pdb=inside_project(output_pdb);trb_path=inside_project(trb_path)
 N=int(target["residue_count"]);length=65
 source_chain=target["input_target_chain"];target_chain=target["rfd_output_target_chain"];binder_chain=target["rfd_binder_chain"]
 if (source_chain,target_chain,binder_chain)!=("A","A","B"):
  raise RuntimeError("Prepared RFD physical mapping must match pinned Sampler: input target A, output target A, binder B")
 if target["rfd_contig"]!=f"A1-{N}/0 65-65":raise RuntimeError("Unexpected frozen target-plus-binder contig")
 parser=PDBParser(QUIET=True);native=parser.get_structure("rfd",output_pdb)[0]
 reference=parser.get_structure("target",target["target_pdb"]["path"])[0]
 chains={c.id:[r for r in c if r.id[0]==" "] for c in native}
 if set(chains)!={target_chain,binder_chain}:raise RuntimeError("RFD output chain set differs from prepared physical mapping")
 receptor=chains[target_chain];binder=chains[binder_chain]
 if len(receptor)!=N or "".join(seq1(r.resname) for r in receptor)!=target["target_sequence"]:
  raise RuntimeError("RFD output full target sequence/length rejected")
 if len(binder)!=length or "".join(seq1(r.resname) for r in binder)!="G"*length:
  raise RuntimeError("RFD output full de novo polyG binder rejected")
 if [r.id for r in receptor]!=[(" ",i+1," ") for i in range(N)] or [r.id for r in binder]!=[(" ",i+1," ") for i in range(length)]:
  raise RuntimeError("RFD output physical residue numbering rejected")
 # Only the current, project-owned official RFD attempt's TRB is unpickled.
 trb=pickle.loads(trb_path.read_bytes());refs=[tuple(x) for x in trb["receptor_con_ref_pdb_idx"]]
 expected=[("A",i+1) for i in range(N)]
 checks={"receptor_ref_pdb_exact":refs==expected,
  "complex_ref_pdb_equals_receptor":[tuple(x) for x in trb["complex_con_ref_pdb_idx"]]==expected,
  "receptor_local_hal_idx0_exact":np.array_equal(trb["receptor_con_hal_idx0"],np.arange(N)),
  "receptor_ref_idx0_exact":np.array_equal(trb["receptor_con_ref_idx0"],np.arange(N)),
  "complex_ref_idx0_exact":np.array_equal(trb["complex_con_ref_idx0"],np.arange(N)),
  "complex_full_hal_idx0_exact":np.array_equal(trb["complex_con_hal_idx0"],np.arange(length,length+N))}
 if not all(checks.values()):raise RuntimeError("RFD official TRB receptor/full-complex mapping rejected: "+repr(checks))
 all_res=[r for c in native for r in c if r.id[0]==" "];mapped=[all_res[int(i)] for i in trb["complex_con_hal_idx0"]]
 if [(r.parent.id,r.id[1]) for r in mapped]!=expected:
  raise RuntimeError("RFD TRB full indices do not map to physical output target A1-N")
 source=[reference[chain][int(index)] for chain,index in refs]
 if "".join(seq1(r.resname) for r in source)!=target["target_sequence"]:
  raise RuntimeError("RFD input target sequence differs from frozen query")

 groups={"reference_target":source,"generated_target":mapped,"binder":binder}
 observations=[]
 for role,residues in groups.items():
  missing=[]
  for r in residues:
   atoms=[a for a in ["N","CA","C","O"] if a not in r]
   if atoms:missing.append({"chain":r.parent.id,"residue_id":[r.id[0],r.id[1],r.id[2]],"residue_name":r.resname,"missing_atoms":atoms})
  observations.append({"role":role,"residue_count":len(residues),"missing_residue_count":len(missing),"missing_atom_count":sum(len(x["missing_atoms"]) for x in missing),"missing":missing})
 return {"status":"FROZEN_ATOM_GATE_REJECTION_REPRODUCED" if any(x["missing_atom_count"] for x in observations) else "NO_MISSING_ATOMS_OBSERVED_CURRENT_ORIGINAL_BYTES","groups":observations,"mapping_checks":checks,"frozen_gate_selection_reached":True}
