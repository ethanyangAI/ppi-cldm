import sys,shutil,json
from pathlib import Path
from Bio import SeqIO
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,checked_command,require,runtime_provenance
from ppiblocker.structure import read_structure,interface,write_pdb
from ppiblocker.backends import backend_env,require_gpu
from ppiblocker.benchmark_adapters import import_pool
from ppiblocker.pipeline import evaluate
from ppiblocker.benchmark import select
root=Path(sys.argv[1]);cid=sys.argv[2]
checks=root/"steps/09_benchmark_registry/runs/20260920T125042Z_c5523f54f659/outputs/preparation_checks.json"
case=next(c for c in read_json(checks) if c["case_id"]==cid)
pose=verify_file(case["prepare_manifest"]);up=read_json(pose)
run=Run(root,"15_motif_baseline",[record_file(pose),record_file(checks)])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 require_gpu();runtime_provenance(run,root,["rfd"])
 native=verify_file(up["outputs"]["native"])
 chains,context=read_structure(native);target,partner=chains
 require(not context and len(chains)==2,"INVALID_MOTIF_CONTEXT","Expected reviewed binary reference")
 length=65;motif=len(partner["sequence"]);left=(length-motif)//2;right=length-motif-left
 require(0<left and right>0,"MOTIF_TOO_LONG","Keep total length matched")
 n=len(target["sequence"]);counts={}
 for a,b in interface(target,partner)["residue_pairs"]:counts[a]=counts.get(a,0)+1
 anchors=sorted(counts,key=lambda a:(-counts[a],a))[:3]
 prefix=run.path/"work/rfd/backbone";prefix.parent.mkdir()
 settings=read_json(up["outputs"]["config"]["path"])["design"];seed=settings["seed"]
 argv=[root/"env/rfd/bin/python",root/"vendor/RFdiffusion/scripts/run_inference.py",
 f"inference.input_pdb={native}",f"inference.output_prefix={prefix}",
 f"inference.ckpt_override_path={root}/assets/rfdiffusion/Complex_base_ckpt.pt",
 "inference.num_designs=2",f"inference.design_startnum={seed}","inference.deterministic=True",
 "inference.write_trajectory=False",f"contigmap.contigs=[A1-{n}/0 {left}-{left}/B1-{motif}/{right}-{right}]",
 "ppi.hotspot_res=["+",".join(f"A{x}" for x in anchors)+"]"]
 if len(sys.argv)>3:
  previous=Path(sys.argv[3]);old=read_json(previous)
  require(old["inputs"][0]["sha256"]==record_file(pose)["sha256"],"REUSE_POSE_MISMATCH",str(previous))
  require(read_json(previous.parent/"logs/rfd.resources.json")["status"]=="COMPLETE","INCOMPLETE_RFD_REUSE",str(previous))
  for f in (previous.parent/"work/rfd").iterdir():
   if f.is_file():shutil.copy2(f,prefix.parent/f.name)
  run.manifest["inputs"].append(record_file(previous));run.save()
  atomic_json(run.path/"qc/reused_rfd.json",dict(source_manifest=record_file(previous),reason="Repair JSONL mask serialization after successful diffusion"))
 else:
  checked_command(argv,run.path/"work",run.path/"logs/rfd.log",backend_env(root,"rfd"),timeout=7200)
 rows=[]
 for k in range(seed,seed+2):
  raw=Path(str(prefix)+f"_{k}.pdb");generated,ctx=read_structure(raw)
  t=[c for c in generated if c["sequence"]==target["sequence"]]
  require(len(t)==1 and len(generated)==2,"MOTIF_CHAIN_MAPPING",str(raw))
  b=next(c for c in generated if c is not t[0])
  require(len(b["sequence"])==65 and b["sequence"][left:left+motif]==partner["sequence"],"MOTIF_IDENTITY",str(raw))
  normalized=run.path/"outputs"/f"motif_{k}.pdb";write_pdb(normalized,[t[0],b])
  fixed=run.path/"work"/f"fixed_{k}.jsonl";fixed.write_text(json.dumps({normalized.stem:{"A":[],"B":list(range(left+1,left+motif+1))}})+"\n")
  out=run.path/"work"/f"mpnn_{k}"
  checked_command([root/"env/rfd/bin/python",root/"vendor/ProteinMPNN/protein_mpnn_run.py",
   "--pdb_path",normalized,"--pdb_path_chains","B","--out_folder",out,"--num_seq_per_target","2",
   "--batch_size","1","--sampling_temp","0.1","--seed",str(k),"--omit_AAs","CX","--fixed_positions_jsonl",fixed],
   run.path/"work",run.path/"logs"/f"mpnn_{k}.log",backend_env(root,"rfd"),timeout=1800)
  fasta=out/"seqs"/(normalized.stem+".fa");records=list(SeqIO.parse(str(fasta),"fasta"))
  require(len(records)==3,"MPNN_COUNT","Expected two samples")
  for j,rec in enumerate(records[1:]):
   seq=str(rec.seq);require(len(seq)==65 and seq[left:left+motif]==partner["sequence"],"MPNN_MOTIF_CHANGED",str(fasta))
   rows.append(dict(id=f"motif{k}_seq{j}",sequence=seq,backbone=record_file(normalized),mpnn=record_file(fasta)))
 runtime=run.path/"qc/runtime-rfd.json"
 pool=dict(schema_version=1,pose_manifest=record_file(pose),method="RFdiffusion_native_motif_ProteinMPNN",
   code_revision=run.manifest["source"]["git_commit"],runtime_record=record_file(runtime),
   candidate_budget=dict(backbones=2,sequences_per_backbone=2,sequence_slots=4,seed=42),
   motif=dict(native_partner_sequence=partner["sequence"],binder_positions=[left+1,left+motif]),
   candidates=rows)
 path=run.path/"outputs/pool_contract.json";atomic_json(path,pool);run.output("pool_contract",path)
 design=import_pool(root,pose,path);run.manifest["design_manifest"]=record_file(design);run.save()
 ev=evaluate(root,design);run.manifest["evaluation_manifest"]=record_file(ev);run.save()
 sel=select(root,ev,8);run.manifest["selection_manifest"]=record_file(sel)
 print(run.finish("MOTIF_COMPARISON_COMPLETE","computational_only",dict(case_id=cid)))
except Exception as e:run.fail(e);raise

