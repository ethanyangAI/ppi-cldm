import sys,shutil,json,itertools
from pathlib import Path
import numpy as np
from Bio import SeqIO
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,checked_command,require,runtime_provenance
from ppiblocker.pipeline import validate_design_pose
from ppiblocker.backends import rfd_mpnn,backend_env,require_gpu
from ppiblocker.structure import read_structure,interface,write_pdb
from ppiblocker.benchmark_adapters import import_pool
root=Path("/lustre/users/u21111210118/projects/test9")
protocol=root/"source/benchmarks/development_20260922/protocol.json"
checks=root/"steps/09_benchmark_registry/runs/20260920T125042Z_c5523f54f659/outputs/preparation_checks.json"
spec=read_json(protocol)["generation"]["round_A"]
cells=list(itertools.product(spec["targets"],spec["conditions"],spec["seeds"]))
idx=int(sys.argv[1]);cid,condition,seed=cells[idx]
pose=verify_file(next(c for c in read_json(checks) if c["case_id"]==cid)["prepare_manifest"])
run=Run(root,"33_generation_development",[record_file(protocol),record_file(checks),record_file(pose)])
shutil.copy2(__file__,run.path/"qc/driver.py")
run.manifest.update(case=cid,condition=condition,seed=seed,cell_index=idx,analysis_role="development",old_gates_unchanged=True);run.save()
try:
 require_gpu();runtime_provenance(run,root,["rfd"])
 _,_,native=validate_design_pose(read_json(pose));target,partner=read_structure(native)[0]
 length=spec["binder_length"];number=spec["backbones_per_cell"];count=spec["sequences_per_backbone"]
 it=interface(target,partner);counts={}
 for a,b in it["residue_pairs"]:counts[a]=counts.get(a,0)+1
 ranked=sorted(counts,key=lambda a:(-counts[a],a));anchors=ranked[:3]
 if condition=="contact_diverse3":
  anchors=[ranked[0]]
  while len(anchors)<3:
   remaining=[a for a in ranked if a not in anchors]
   distances={a:min(np.linalg.norm(target["residues"][a-1]["ca"]-target["residues"][b-1]["ca"]) for b in anchors) for a in remaining}
   distant=[a for a in remaining if distances[a]>=8]
   anchors.append(distant[0] if distant else max(remaining,key=lambda a:(distances[a],counts[a],-a)))
 definition=dict(case=cid,condition=condition,seed=seed,target_anchors=anchors,
  anchor_semantics="geometric_contacts_not_experimentally_measured_energetic_hotspots",
  backbones=number,sequences_per_backbone=count,length=length,temperature=.1)
 if condition.startswith("contact_") and condition!="contact_core_motif":
  atomic_json(run.path/"outputs/arm_definition.json",definition);run.output("definition",run.path/"outputs/arm_definition.json")
  rows=rfd_mpnn(root,run.path/"work/design",native,dict(binder_length=length,backbones=number,sequences_per_backbone=count,seed=seed,temperature=.1,interface_anchors=anchors),run.path/"logs")
 else:
  plen=len(partner["sequence"])
  if condition=="full_native_motif":start,end=1,plen
  else:
   # Fixed eight-residue contiguous native window, maximizing observed contact pairs; earliest tie.
   width=min(8,plen);windows=range(1,plen-width+2)
   start=max(windows,key=lambda s:(sum(s<=b<s+width for a,b in it["residue_pairs"]),-s));end=start+width-1
  motif=end-start+1;left=(length-motif)//2;right=length-motif-left
  definition.update(motif_native_positions=[start,end],motif_binder_positions=[left+1,left+motif],
    motif_sequence=partner["sequence"][start-1:end],motif_rule="all16" if condition=="full_native_motif" else "maximum_contact_eight_residue_window_earliest_tie")
  atomic_json(run.path/"outputs/arm_definition.json",definition);run.output("definition",run.path/"outputs/arm_definition.json")
  prefix=run.path/"work/rfd/backbone";prefix.parent.mkdir()
  argv=[root/"env/rfd/bin/python",root/"vendor/RFdiffusion/scripts/run_inference.py",
   f"inference.input_pdb={native}",f"inference.output_prefix={prefix}",
   f"inference.ckpt_override_path={root}/assets/rfdiffusion/Complex_base_ckpt.pt",
   f"inference.num_designs={number}",f"inference.design_startnum={seed}","inference.deterministic=True","inference.write_trajectory=False",
   f"contigmap.contigs=[A1-{len(target['sequence'])}/0 {left}-{left}/B{start}-{end}/{right}-{right}]",
   "ppi.hotspot_res=["+",".join(f"A{x}" for x in anchors)+"]"]
  checked_command(argv,run.path/"work",run.path/"logs/rfd.log",backend_env(root,"rfd"),timeout=14400)
  rows=[]
  for k in range(seed,seed+number):
   raw=Path(str(prefix)+f"_{k}.pdb");cs,ctx=read_structure(raw)
   matches=[c for c in cs if c["sequence"]==target["sequence"]]
   require(len(matches)==1 and len(cs)==2 and not ctx,"CHAIN_MAPPING",str(raw))
   t=matches[0];b=next(c for c in cs if c is not t)
   require(len(b["sequence"])==length and b["sequence"][left:left+motif]==definition["motif_sequence"],"MOTIF_CHANGED",str(raw))
   normalized=run.path/"work"/f"backbone_{k}.pdb";write_pdb(normalized,[t,b])
   fixed=run.path/"work"/f"fixed_{k}.jsonl"
   fixed.write_text(json.dumps({normalized.stem:{"A":[],"B":list(range(left+1,left+motif+1))}})+"\n")
   out=run.path/"work"/f"mpnn_{k}"
   checked_command([root/"env/rfd/bin/python",root/"vendor/ProteinMPNN/protein_mpnn_run.py","--pdb_path",normalized,
    "--pdb_path_chains","B","--out_folder",out,"--num_seq_per_target",str(count),"--batch_size","1",
    "--sampling_temp","0.1","--seed",str(k),"--omit_AAs","CX","--fixed_positions_jsonl",fixed],
    run.path/"work",run.path/"logs"/f"mpnn_{k}.log",backend_env(root,"rfd"),timeout=1800)
   fasta=out/"seqs"/(normalized.stem+".fa");records=list(SeqIO.parse(str(fasta),"fasta"))
   require(len(records)==count+1,"MPNN_COUNT",str(fasta))
   for j,rec in enumerate(records[1:]):
    seq=str(rec.seq);require(len(seq)==length and seq[left:left+motif]==definition["motif_sequence"],"MPNN_MOTIF_CHANGED",str(fasta))
    rows.append(dict(id=f"bb{k}_seq{j}",sequence=seq,backbone=record_file(normalized),raw_backbone=record_file(raw),mpnn_fasta=record_file(fasta)))
 require(len(rows)==number*count,"POOL_COUNT",str(len(rows)))
 pool=dict(schema_version=1,pose_manifest=record_file(pose),method="RFdiffusion_ProteinMPNN_"+condition,
  code_revision=run.manifest["source"]["git_commit"],runtime_record=record_file(run.path/"qc/runtime-rfd.json"),
  candidate_budget=definition,candidates=rows)
 path=run.path/"outputs/pool_contract.json";atomic_json(path,pool);run.output("pool_contract",path)
 imported=import_pool(root,pose,path);run.manifest["design_manifest"]=record_file(imported)
 print(run.finish("DEVELOPMENT_POOL_GENERATED","unvalidated_sequences",dict(sequence_slots=len(rows))),flush=True)
except Exception as e:run.fail(e);raise

