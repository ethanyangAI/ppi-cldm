from __future__ import annotations
import os
import re
import shutil
from pathlib import Path
import numpy as np
import yaml
from Bio import SeqIO
from .common import require, read_json, record_file, checked_command, EvidenceError, strict_bool, verify_file, atomic_json
from .structure import read_structure, interface, write_pdb

def backend_env(root, component="boltz"):
    env=os.environ.copy()
    env.update(PYTHONNOUSERSITE="1", DGLBACKEND="pytorch", OMP_NUM_THREADS=str(min(int(env.get("SLURM_CPUS_PER_TASK","4")),8)),
               BOLTZ_CACHE=str(Path(root)/"assets/boltz"), MPLCONFIGDIR=str(Path(root)/"env/matplotlib"))
    if component=="rfd":
        base=Path(root)/"env/rfd"
        site=base/"lib/python3.10/site-packages"
        libs=[base/"lib",site/"torch/lib",site/"nvidia/cusparse/lib",site/"nvidia/cuda_runtime/lib"]
        env["LD_LIBRARY_PATH"]=":".join(map(str,libs))+":"+env.get("LD_LIBRARY_PATH","")
    env.pop("PYTHONPATH",None)
    return env

def require_gpu():
    require(bool(os.environ.get("SLURM_JOB_ID")), "SLURM_REQUIRED", "Run model stages in an allocated Slurm GPU job")
    require(bool(os.environ.get("CUDA_VISIBLE_DEVICES")), "GPU_REQUIRED", "A visible allocated GPU is required")

def boltz_predict(root, work, proteins, settings, log):
    require_gpu()
    work=Path(work);work.mkdir(parents=True,exist_ok=False)
    inputs=[]
    external=strict_bool(settings.get("allow_external_msa",False),"allow_external_msa")
    single=strict_bool(settings.get("allow_single_sequence",False),"allow_single_sequence")
    msa_records=[]
    for i,p in enumerate(proteins):
        spec={"id":chr(65+i),"sequence":p["sequence"]}
        if p.get("msa"):
            require(p.get("msa_record"),"MSA_UNPINNED","Re-prepare to snapshot the original MSA input")
            path=verify_file(p["msa_record"])
            require(path.resolve()==Path(p["msa"]).resolve(),"MSA_IDENTITY_MISMATCH","MSA path differs from pinned input")
            require(path.suffix in {".a3m",".csv"},"MSA_FORMAT_UNSUPPORTED",str(path))
            copy=work/f"input_{i}{path.suffix}";shutil.copy2(path,copy)
            receipt=record_file(copy)
            require(receipt["sha256"]==p["msa_record"]["sha256"],"INTEGRITY_FAILURE","MSA changed during copy")
            spec["msa"]=str(copy);msa_records.append({"chain":spec["id"],"source":p["msa_record"],"snapshot":receipt})
        elif p.get("de_novo"):
            spec["msa"]="empty"
        elif not external:
            require(single,"MSA_REQUIRED","Provide an MSA or explicitly permit public MSA server or single-sequence inference")
            spec["msa"]="empty"
        inputs.append({"protein":spec})
    atomic_json(work/"msa_inputs.json",msa_records)
    input_path=work/"complex.yaml"
    input_path.write_text(yaml.safe_dump({"version":1,"sequences":inputs},sort_keys=False))
    exe=Path(root)/"env/boltz/bin/boltz"
    argv=[exe,"predict",input_path,"--out_dir",work/"results","--cache",Path(root)/"assets/boltz",
          "--model","boltz2","--output_format","pdb","--write_full_pae","--no_kernels",
          "--seed",str(settings.get("seed",42)),"--diffusion_samples",str(settings.get("samples",3)),
          "--recycling_steps",str(settings.get("recycles",3)),"--sampling_steps",str(settings.get("sampling_steps",200)),
          "--devices","1","--num_workers","0","--max_parallel_samples","1"]
    if external: argv.append("--use_msa_server")
    checked_command(argv,work,log,backend_env(root))
    out=work/"results/boltz_results_complex/predictions/complex"
    # Only this new, isolated invocation; no broad latest-file search.
    models=[]
    for i in range(settings.get("samples",3)):
        pdb=out/f"complex_model_{i}.pdb"
        conf=out/f"confidence_complex_model_{i}.json"
        pae=out/f"pae_complex_model_{i}.npz"
        for path in (pdb,conf,pae):
            require(path.is_file(),"INCOMPLETE_PREDICTION",str(path))
        models.append({"structure":record_file(pdb),"confidence":record_file(conf),"pae":record_file(pae),"model_index":i})
    return models

def confidence_metrics(model, target_length, partner_length, contacts):
    conf=read_json(model["confidence"]["path"])
    pair=conf.get("pair_chains_iptm",{})
    try: iptm=min(float(pair["0"]["1"]),float(pair["1"]["0"]))
    except (KeyError,TypeError,ValueError) as e: raise EvidenceError("PAIR_CONFIDENCE_MISSING","No A-B directional ipTM") from e
    with np.load(model["pae"]["path"],allow_pickle=False) as arr:
        require("pae" in arr,"PAE_MISSING","NPZ lacks pae")
        pae=np.asarray(arr["pae"])
    require(pae.shape==(target_length+partner_length,)*2,"TOKEN_MAPPING_MISMATCH","Only two canonical protein chains without extra tokens supported")
    pairs=contacts["residue_pairs"]
    require(np.isfinite(pae).all() and (pae>=0).all(),"INVALID_CONFIDENCE","PAE must be finite and nonnegative")
    values=[float(pae[i-1,target_length+j-1]) for i,j in pairs]+[float(pae[target_length+j-1,i-1]) for i,j in pairs]
    metrics={"pair_iptm":iptm,"interface_pae_mean":float(np.mean(values)) if values else None,
             "interface_observed":bool(values),
             "interface_pae_p90":float(np.quantile(values,.9)) if values else None,
             "complex_plddt":float(conf["complex_plddt"])}
    require(all(np.isfinite(x) for x in metrics.values() if x is not None),"INVALID_CONFIDENCE","Nonfinite confidence")
    require(0<=iptm<=1 and 0<=metrics["complex_plddt"]<=1,"INVALID_CONFIDENCE","Unexpected confidence scale")
    return metrics

def confidence_reasons(metrics,gates):
    reasons=[]
    if metrics["pair_iptm"]<gates.get("min_pair_iptm",.75): reasons.append("LOW_PAIR_IPTM")
    if metrics.get("interface_observed",True) is False:reasons.append("NO_INTERFACE")
    elif metrics["interface_pae_mean"]>gates.get("max_interface_pae",8): reasons.append("HIGH_INTERFACE_PAE")
    if metrics["complex_plddt"]<gates.get("min_plddt",.8): reasons.append("LOW_PLDDT")
    if metrics.get("partner_plddt",1)<gates.get("min_partner_plddt",.8): reasons.append("LOW_PARTNER_PLDDT")
    if metrics.get("interface_plddt",1) is not None and metrics.get("interface_plddt",1)<gates.get("min_interface_plddt",.8): reasons.append("LOW_INTERFACE_PLDDT")
    if metrics.get("interface_target_residues",3)<gates.get("min_interface_residues",3) or metrics.get("interface_partner_residues",3)<gates.get("min_partner_residues",3):reasons.append("INSUFFICIENT_INTERFACE_CONTACTS")
    return reasons

def rfd_mpnn(root, work, native, settings, logdir, contact_cutoff=5):
    require_gpu()
    root,work,logdir=Path(root),Path(work),Path(logdir)
    work.mkdir(parents=True,exist_ok=False)
    chains,_=read_structure(native)
    require([c["id"] for c in chains]==["A","B"],"NORMALIZED_CHAINS_REQUIRED","Expected native A target, B partner")
    target,partner=chains
    n=len(target["residues"])
    # RFdiffusion contigs require an unbroken observed target backbone.
    distances=np.linalg.norm(np.diff(np.array([r["ca"] for r in target["residues"]]),axis=0),axis=1)
    require(np.all((distances>2.5)&(distances<4.5)),"TARGET_BACKBONE_GAPS",
            "Observed target contains gaps or a chain break; supply a reviewed complete construct")
    anchors=settings.get("interface_anchors")
    contacts=interface(target,partner,contact_cutoff)
    if anchors is None:
        counts={}
        for a,b in contacts["residue_pairs"]: counts[a]=counts.get(a,0)+1
        anchors=sorted(counts,key=lambda a:(-counts[a],a))[:3]
    require(anchors and all(isinstance(a,int) and a in contacts["target_residues"] for a in anchors),
            "INVALID_ANCHORS","Anchors must be observed native-interface residue indices")
    length=int(settings.get("binder_length",65))
    require(30<=length<=200,"UNSUPPORTED_BINDER_LENGTH","Supported miniprotein length 30-200")
    number=int(settings.get("backbones",4))
    require(1<=number<=1000,"INVALID_DESIGN_COUNT","Backbones must be 1-1000")
    seed=int(settings.get("seed",42))
    prefix=work/"rfd/backbone"; prefix.parent.mkdir()
    ckpt=root/"assets/rfdiffusion/Complex_base_ckpt.pt"
    require(ckpt.is_file(),"WEIGHTS_MISSING",str(ckpt))
    argv=[root/"env/rfd/bin/python",root/"vendor/RFdiffusion/scripts/run_inference.py",
          f"inference.input_pdb={native}",f"inference.output_prefix={prefix}",
          f"inference.ckpt_override_path={ckpt}",f"inference.num_designs={number}",
          f"inference.design_startnum={seed}","inference.deterministic=True",
          "inference.write_trajectory=False",f"contigmap.contigs=[A1-{n}/0 {length}-{length}]",
          "ppi.hotspot_res=["+",".join(f"A{x}" for x in anchors)+"]"]
    checked_command(argv,work,logdir/"rfd.log",backend_env(root,"rfd"))
    candidates=[]
    for k in range(seed,seed+number):
        raw=Path(str(prefix)+f"_{k}.pdb"); require(raw.exists(),"RFD_OUTPUT_MISSING",str(raw))
        gen,_=read_structure(raw)
        matches=[c for c in gen if c["sequence"]==target["sequence"]]
        require(len(matches)==1 and len(gen)==2,"RFD_TARGET_IDENTITY_FAILED","Cannot uniquely recover fixed target chain")
        fixed=matches[0]; binder=next(c for c in gen if c["id"]!=fixed["id"])
        require(len(binder["sequence"])==length,"RFD_LENGTH_MISMATCH",str(raw))
        normalized=work/f"backbone_{k}.pdb";write_pdb(normalized,[fixed,binder])
        out=work/f"mpnn_{k}"
        count=int(settings.get("sequences_per_backbone",4))
        checked_command([root/"env/rfd/bin/python",root/"vendor/ProteinMPNN/protein_mpnn_run.py",
                         "--pdb_path",normalized,"--pdb_path_chains","B","--out_folder",out,
                         "--num_seq_per_target",str(count),"--batch_size","1","--sampling_temp",str(settings.get("temperature",.1)),
                         "--seed",str(k),"--omit_AAs","CX"],work,logdir/f"mpnn_{k}.log",backend_env(root,"rfd"))
        fasta=out/"seqs"/(normalized.stem+".fa")
        records=list(SeqIO.parse(str(fasta),"fasta"))
        require(len(records)==count+1 and "designed_chains=['B']" in records[0].description,
                "MPNN_OUTPUT_INVALID","Expected native plus designed B-only records")
        for j,rec in enumerate(records[1:]):
            seq=str(rec.seq)
            require(len(seq)==length and set(seq)<=set("ACDEFGHIKLMNPQRSTVWY"),"INVALID_DESIGN_SEQUENCE",rec.id)
            candidates.append({"id":f"bb{k}_seq{j}","sequence":seq,"backbone":record_file(normalized),
                               "raw_backbone":record_file(raw),"mpnn_fasta":record_file(fasta),
                               "mpnn_header":rec.description,"target_sequence":target["sequence"],
                               "interface_anchors":anchors,"contact_cutoff_angstrom":contact_cutoff,"anchor_semantics":"geometric contact anchors; not measured energetic hotspots"})
    return candidates

