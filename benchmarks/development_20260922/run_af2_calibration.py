import sys,os,re,shutil,subprocess
from pathlib import Path
import numpy as np
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,checked_command,require,tree_fingerprint
from ppiblocker.structure import read_structure,interface,competition,superpose
from ppiblocker.backends import require_gpu
root=Path(sys.argv[1]);plan=Path(sys.argv[2]);group=sys.argv[3]
entries=[x for x in read_json(plan)["entries"] if x["group"]==group]
msa_manifest=Path(sys.argv[4])
run=Run(root,"61_af2_calibration",[record_file(plan),record_file(msa_manifest)])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 require_gpu();require(entries,"EMPTY_AF2_BATCH",group)
 receipt=read_json(root/"env/colabfold-assets.json")
 for f in receipt["weights"]:verify_file(f)
 atomic_json(run.path/"qc/runtime.json",dict(assets=record_file(root/"env/colabfold-assets.json"),
  packages=record_file(root/"env/colabfold-freeze.txt"),
  colabfold=tree_fingerprint(root/"env/colabfold/lib/python3.10/site-packages/colabfold"),
  alphafold=tree_fingerprint(root/"env/colabfold/lib/python3.10/site-packages/alphafold"),
  protocol="AF2 multimer v3 model 1, seeds 1042-1044, 3 recycles, public-target MSA max_seq 128 max_extra_seq 256 plus single binder sequence, no template, no relaxation",
  global_iptm_not_directional_pair_iptm=True))
 fasta=run.path/"outputs/queries.fasta"
 fasta.write_text("".join(f">{x['id']}\n{x['target_sequence']}:{x['sequence']}\n" for x in entries))
 msa_up=read_json(msa_manifest);require(msa_up["status"]=="MSA_INPUTS_VALIDATED","INVALID_MSA_INPUTS",str(msa_manifest))
 msa_inputs=read_json(verify_file(msa_up["outputs"]["inputs"]))
 directory=run.path/"outputs/msa_queries";directory.mkdir()
 for entry in entries:shutil.copy2(verify_file(msa_inputs[entry["id"]]),directory/(entry["id"]+".a3m"))
 fasta=directory
 out=run.path/"work/af2"
 env=os.environ.copy();env.update(PYTHONNOUSERSITE="1",XLA_PYTHON_CLIENT_PREALLOCATE="false",TF_FORCE_UNIFIED_MEMORY="0",OMP_NUM_THREADS=os.environ.get("SLURM_CPUS_PER_TASK","4"))
 site=root/"env/colabfold/lib/python3.10/site-packages"
 env["LD_LIBRARY_PATH"]=":".join(str(x) for x in sorted((site/"nvidia").glob("*/lib")))+":"+str(root/"env/colabfold/lib")+":"+env.get("LD_LIBRARY_PATH","")
 env["PATH"]=str(root/"env/colabfold/bin")+":"+str(site/"nvidia/cuda_nvcc/bin")+":"+env.get("PATH","")
 env["XLA_FLAGS"]="--xla_gpu_cuda_data_dir="+str(site/"nvidia/cuda_nvcc")
 env.update(OPENBLAS_NUM_THREADS="1",MKL_NUM_THREADS="1",NUMEXPR_NUM_THREADS="1",TF_NUM_INTRAOP_THREADS="4",TF_NUM_INTEROP_THREADS="1")
 env.pop("PYTHONPATH",None)
 argv=[root/"env/colabfold/bin/colabfold_batch",fasta,out,"--model-type","alphafold2_multimer_v3",
 "--num-models","1","--model-order","1","--num-seeds","3","--random-seed","1042","--num-recycle","3",
 "--msa-mode","mmseqs2_uniref_env","--max-msa","128:256","--num-relax","0","--data",root/"assets/colabfold"]
 checked_command(argv,run.path/"work",run.path/"logs/af2.log",env,timeout=21600)
 results=[]
 for entry in entries:
  models=[]
  files=sorted(out.glob(entry["id"]+"_unrelaxed_rank_*.pdb"))
  require(len(files)==3,"AF2_SAMPLE_COUNT",f"{entry['id']}: {len(files)}")
  native,_=read_structure(verify_file(entry["native"]))
  nt,np_=native
  design=None
  if entry.get("backbone"):design=read_structure(verify_file(entry["backbone"]))[0]
  for f in files:
   cs,ctx=read_structure(f);require(len(cs)==2 and not ctx,"AF2_CHAIN_COUNT",str(f))
   a,b=cs;require(a["sequence"]==entry["target_sequence"] and b["sequence"]==entry["sequence"],"AF2_CHAIN_IDENTITY",str(f))
   score=f.with_name(f.name.replace("_unrelaxed_","_scores_").replace(".pdb",".json"))
   scores=read_json(score);pae=np.array(scores["pae"]);plddt=np.array(scores["plddt"])/100
   n=len(a["sequence"]);m=len(b["sequence"]);require(pae.shape==(n+m,n+m),"AF2_PAE_SHAPE",str(f))
   it=interface(a,b);pairs=it["residue_pairs"]
   directional=[pae[i-1,n+j-1] for i,j in pairs]+[pae[n+j-1,i-1] for i,j in pairs]
   positions=[i-1 for i in it["target_residues"]]+[n+j-1 for j in it["partner_residues"]]
   geom=competition(nt,np_,*(design if design else [a,b]),a,b)
   if not design:geom.pop("binder_ca_rmsd_after_target_alignment",None)
   metrics=dict(global_iptm=float(scores["iptm"]),ptm=float(scores["ptm"]),
     partner_plddt=float(plddt[n:].mean()),
     interface_plddt=float(plddt[positions].mean()) if positions else None,
     contact_pae_mean=float(np.mean(directional)) if directional else None)
   binding=bool(metrics["global_iptm"]>=.75 and metrics["partner_plddt"]>=.8 and
     metrics["interface_plddt"] is not None and metrics["interface_plddt"]>=.8 and
     metrics["contact_pae_mean"]<=8 and it["minimum_distance"]>=1.5)
   geometry=bool(geom["native_interface_coverage"]>=.5 and geom["partner_overlap_atom_count_2A"]>=5 and geom["target_ca_rmsd"]<=2)
   reproducible=bool(geom.get("binder_ca_rmsd_after_target_alignment",0)<=2) if design else None
   models.append(dict(pdb=record_file(f),scores=record_file(score),metrics=metrics,geometry=geom,
       exploratory_binding_proxy_pass=binding,competition_geometry_pass=geometry,design_recovery_pass=reproducible))
  results.append(dict(id=entry["id"],group=group,label=entry.get("label"),models=models,
    binding_proxy_pass_count=sum(x["exploratory_binding_proxy_pass"] for x in models),
    joint_proxy_pass_count=sum(x["exploratory_binding_proxy_pass"] and x["competition_geometry_pass"] and x["design_recovery_pass"] is not False for x in models),
    interpretation="AF2 calibration input. Reference is author design, not native partner; geometric overlap is design recovery only and does not establish competition. Global ipTM differs from directional Boltz ipTM."))
 output=run.path/"outputs/results.json";atomic_json(output,results);run.output("results",output)
 print(run.finish("AF2_VERIFICATION_COMPLETE","computational_only",dict(group=group,candidate_count=len(entries))),flush=True)
except Exception as e:run.fail(e);raise

