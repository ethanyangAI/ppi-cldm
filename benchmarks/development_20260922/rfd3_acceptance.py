import os,sys,gzip,shutil,collections
from pathlib import Path
from Bio import SeqIO
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,checked_command,require,tree_fingerprint
from ppiblocker.pipeline import validate_design_pose
from ppiblocker.structure import read_structure,write_pdb,interface
from ppiblocker.backends import require_gpu,backend_env
from ppiblocker.benchmark_adapters import import_pool
root=Path("/lustre/users/u21111210118/projects/test9");pose=root/"steps/01_pose/runs/20260920T125042Z_8e4ecd8ead82/manifest.json"
run=Run(root,"59_rfd3_acceptance",[record_file(pose)])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 require_gpu();_,_,native=validate_design_pose(read_json(pose));target,partner=read_structure(native)[0]
 path=run.path/"outputs/target_only.pdb";write_pdb(path,[target]);run.output("target",path)
 counts=collections.Counter(a for a,b in interface(target,partner)["residue_pairs"]);anchors=sorted(counts,key=lambda a:(-counts[a],a))[:3]
 spec={"P06_runtime":{"dialect":2,"input":str(path),"contig":f"65,/0,A1-{len(target['sequence'])}","infer_ori_strategy":"hotspots","select_hotspots":{f"A{x}":"CA" for x in anchors},"is_non_loopy":True}}
 inputs=run.path/"outputs/input.json";atomic_json(inputs,spec);run.output("specification",inputs)
 checkpoint=root/"assets/rfd3/rfd3_latest.ckpt";require(checkpoint.is_file(),"CHECKPOINT_MISSING",str(checkpoint))
 verified=[(p,read_json(p)) for step in ("67_rfd3_weights_repair","70_rfd3_segmented_repair") for p in (root/"steps"/step/"runs").glob("*/manifest.json") if read_json(p)["status"]=="CHECKPOINT_TRANSPORT_VERIFIED"]
 require(len(verified)==1,"CHECKPOINT_RECEIPT_NOT_UNIQUE",str(len(verified)))
 receipt=read_json(verify_file(verified[0][1]["outputs"]["receipt"]))
 require(verify_file(receipt["checkpoint"])==checkpoint,"CHECKPOINT_PATH_MISMATCH",str(checkpoint))
 run.manifest["inputs"].append(record_file(verified[0][0]));run.save()
 wrapper=root/"source/benchmarks/development_20260922/rfd3_compat.py";runtime=run.path/"qc/runtime.json"
 atomic_json(runtime,dict(source=record_file(root/"vendor/foundry/.source_receipt.json"),checkpoint=record_file(checkpoint),wrapper=record_file(wrapper),rfd3=tree_fingerprint(root/"env/rfd3/lib/python3.12/site-packages/rfd3"),budget=dict(backbones=1,mpnn_sequences=2,seed=2142),purpose="runtime_acceptance_not_head_to_head_comparison"))
 env=os.environ.copy();env.update(PYTHONNOUSERSITE="1",FOUNDRY_CHECKPOINT_DIRS=str(root/"assets/rfd3"),OMP_NUM_THREADS=str(os.environ.get("SLURM_CPUS_PER_TASK","4")))
 env.pop("PYTHONPATH",None);env["PATH"]=str(root/"env/rfd3/bin")+":"+env.get("PATH","")
 env["LD_LIBRARY_PATH"]=str(root/"env/rfd3/lib")+":"+env.get("LD_LIBRARY_PATH","")
 out=run.path/"work/rfd3"
 checked_command([root/"env/rfd3/bin/python",wrapper,run.path/"qc/gpu_profile.json","design",f"out_dir={out}",f"inputs={inputs}","diffusion_batch_size=1","n_batches=1","seed=2142","low_memory_mode=True","compile_model=False"],run.path/"work",run.path/"logs/rfd3.log",env,timeout=7200)
 files=list(out.rglob("*.cif.gz"));require(len(files)==1,"RFD3_BACKBONE_COUNT",str(files))
 raw=run.path/"work/rfd3_model.cif"
 with gzip.open(files[0],"rb") as f:raw.write_bytes(f.read())
 cs,ctx=read_structure(raw);matches=[c for c in cs if c["sequence"]==target["sequence"]]
 require(len(cs)==2 and len(matches)==1 and not ctx,"RFD3_CHAIN_MAPPING",str(raw));t=matches[0];b=next(c for c in cs if c is not t)
 require(len(b["sequence"])==65,"RFD3_LENGTH",str(len(b["sequence"])))
 norm=run.path/"outputs/backbone.pdb";write_pdb(norm,[t,b]);run.output("backbone",norm)
 mpnn=run.path/"work/mpnn"
 checked_command([root/"env/rfd/bin/python",root/"vendor/ProteinMPNN/protein_mpnn_run.py","--pdb_path",norm,"--pdb_path_chains","B","--out_folder",mpnn,"--num_seq_per_target","2","--batch_size","1","--sampling_temp","0.1","--seed","2142","--omit_AAs","CX"],run.path/"work",run.path/"logs/mpnn.log",backend_env(root,"rfd"),timeout=1200)
 fa=mpnn/"seqs/backbone.fa";seqs=list(SeqIO.parse(str(fa),"fasta"))[1:];require(len(seqs)==2,"MPNN_COUNT",str(len(seqs)))
 rows=[dict(id=f"rfd3_{i}",sequence=str(s.seq),backbone=record_file(norm),mpnn_fasta=record_file(fa)) for i,s in enumerate(seqs)]
 profile=read_json(run.path/"qc/gpu_profile.json");pool=dict(schema_version=1,pose_manifest=record_file(pose),method="RFdiffusion3_ProteinMPNN_"+profile["profile"],code_revision=read_json(root/"vendor/foundry/.source_receipt.json")["revision"],runtime_record=record_file(runtime),candidate_budget=dict(backbones=1,sequences_per_backbone=2,profile="runtime_acceptance"),candidates=rows)
 cp=run.path/"outputs/pool_contract.json";atomic_json(cp,pool);run.output("pool",cp);run.output("runtime",runtime);run.output("gpu_profile",run.path/"qc/gpu_profile.json")
 imported=import_pool(root,pose,cp);run.output("design_manifest",imported)
 print(run.finish("RFD3_COMPATIBILITY_RUNTIME_ACCEPTED" if profile["profile"].startswith("FP32") else "RFD3_RUNTIME_ACCEPTED","unvalidated_sequences",dict(profile=profile["profile"],candidate_count=2,official_precision_equivalence_established=False)),flush=True)
except Exception as e:run.fail(e);raise
