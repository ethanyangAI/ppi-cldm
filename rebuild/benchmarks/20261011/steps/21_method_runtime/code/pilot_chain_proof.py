#!/usr/bin/env python3
import hashlib,json,os,pickle
from pathlib import Path
import numpy as np
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/21_method_runtime";O=S/f"runs/pilot_chain_proof_{os.environ['SLURM_JOB_ID']}/outputs";O.mkdir(parents=True,exist_ok=True)
def rec(p):return {"path":str(p),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
target_path=R/"steps/22_matched_benchmark/input_preparation/prepared_7_13010/KEAP1_2FLU/input_manifest.json";target=json.loads(target_path.read_text())
base=R/"steps/22_matched_benchmark/engineering_pilot/runs/13069_0/attempts/000000/generated";pdb=base/"backbone_1436254356.pdb";trbpath=pdb.with_suffix(".trb")
trb=pickle.loads(trbpath.read_bytes());parser=PDBParser(QUIET=True);native=parser.get_structure("rfd",pdb)[0];reference=parser.get_structure("target",target["target_pdb"]["path"])[0]
def safe(v):
 if isinstance(v,dict):return {str(k):safe(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [safe(x) for x in v]
 if isinstance(v,np.ndarray):return safe(v.tolist())
 if isinstance(v,np.generic):return v.item()
 return v if isinstance(v,(str,int,float,bool)) or v is None else repr(v)
all_res=[r for c in native for r in c if r.id[0]==" "]
refs=trb["receptor_con_ref_pdb_idx"];hal=trb["receptor_con_hal_pdb_idx"];hal0=trb["complex_con_hal_idx0"];ref0=trb["receptor_con_ref_idx0"];local_hal0=trb["receptor_con_hal_idx0"]
mapped=[]
for ref,abstract,outidx,inidx in zip(refs,hal,hal0,ref0):
 source=reference[ref[0]][int(ref[1])];dest=all_res[int(outidx)]
 mapped.append({"input":safe(ref),"contigmap_abstract_hal":safe(abstract),"ref_idx0":int(inidx),"complex_hal_idx0":int(outidx),"actual_output":[dest.parent.id,dest.id[1]],"source_aa":seq1(source.resname),"output_aa":seq1(dest.resname)})
src=np.asarray([reference[ref[0]][int(ref[1])]["CA"].coord for ref in refs],dtype=np.float64);dst=np.asarray([all_res[int(i)]["CA"].coord for i in hal0],dtype=np.float64)
sc=src.mean(0);dc=dst.mean(0);u,s,vt=np.linalg.svd((src-sc).T@(dst-dc));rotation=u@np.diag([1.,1.,np.linalg.det(u@vt)])@vt
displacement={atom:[float(np.linalg.norm((reference[ref[0]][int(ref[1])][atom].coord-sc)@rotation+dc-all_res[int(i)][atom].coord)) for ref,i in zip(refs,hal0)] for atom in ["N","CA","C","O"]}
N=target["residue_count"];fixed_refs=[("A",i+1) for i in range(N)]
checks={"exact_full_target_query":''.join(seq1(r.resname) for r in native["A"])==target["target_sequence"],"target_length":len(native["A"])==N,"binder_polyG65":''.join(seq1(r.resname) for r in native["B"])=="G"*65,"exact_two_chains":set(c.id for c in native)=={"A","B"},"receptor_ref_mapping_exact":list(refs)==fixed_refs,"receptor_ref_idx0_exact":np.array_equal(ref0,np.arange(N)),"receptor_local_hal_idx0_exact":np.array_equal(local_hal0,np.arange(N)),"complex_hal_idx0_exact":np.array_equal(hal0,np.arange(65,65+N)),"complex_reference_equals_receptor_reference":list(trb["complex_con_ref_pdb_idx"])==list(refs),"actual_receptor_output_ids_exact":[x["actual_output"] for x in mapped]==[["A",i+1] for i in range(N)],"mapped_sequences_match":all(x["source_aa"]==x["output_aa"] for x in mapped),"fixed_backbone_preserved_after_rigid_alignment":max(x for values in displacement.values() for x in values)<=.02}
result={"schema":"rfd_actual_chain_proof.v1","status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"pdb":rec(pdb),"trb":rec(trbpath),"input_manifest":rec(target_path),"input_target_pdb":target["target_pdb"],"official_sampler_source":rec(R/"vendor/RFdiffusion/rfdiffusion/inference/model_runners.py"),"sampler_chain_source_lines":[363,404],"official_writer_source":rec(R/"vendor/RFdiffusion/scripts/run_inference.py"),"writer_source_lines":[126,143],"physical_target_chain":"A","physical_binder_chain":"B","contigmap_abstract_target_chain":"B","contigmap_abstract_binder_chain":"A","fixed_target_mapping":mapped,"rigid_fit_ca_rmsd_angstrom":float(np.sqrt(np.mean(np.sum(((src-sc)@rotation+dc-dst)**2,axis=-1)))),"rigid_fit_rotation":rotation.tolist(),"source_centroid":sc.tolist(),"output_centroid":dc.tolist(),"fixed_backbone_displacement_max_angstrom":{k:max(v) for k,v in displacement.items()},"fixed_backbone_atom_count":sum(len(v) for v in displacement.values()),"trb_index_semantics":"receptor_con_hal_idx0 is receptor-local; complex_con_hal_idx0 addresses full binder-first PDB order; receptor_con_hal_pdb_idx uses abstract ContigMap chains/offset numbering and does not represent Sampler physical PDB chain IDs","prior_diagnostic_interpretation_rejected":"pilot_chain_proof_13084 used receptor-local hal_idx0 as full-complex index; preserved as failed audit fixture","contig_mapping_source":rec(R/"vendor/RFdiffusion/rfdiffusion/contigs.py"),"contig_mapping_source_lines":[392,451],"slurm_job_id":os.environ["SLURM_JOB_ID"],"scontrol_record":os.popen("scontrol show job -o "+os.environ["SLURM_JOB_ID"]).read()}
out=O/"chain_proof.json";out.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps({"status":result["status"],"checks":checks,"maximums":result["fixed_backbone_displacement_max_angstrom"],"ca_rmsd":result["rigid_fit_ca_rmsd_angstrom"],"receipt":rec(out)},indent=2))
if result["status"]!="PASS":raise SystemExit(1)

