#!/usr/bin/env python3
"""Independently recompute common scores from restored raw PDB/JSON/NPZ.

Does not import screening_transfer, benchmark_common_review, ppiblocker or the
production budget orchestrator. Runs the pinned official ipSAE program anew.
"""
import collections,hashlib,json,math,os,subprocess,sys
from pathlib import Path
import numpy as np
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from scipy.spatial import cKDTree
from restore_resolver_v2 import path_factory

def summary(values,expected):
    valid=[float(v) for v in values if isinstance(v,(int,float,np.number)) and not isinstance(v,(bool,np.bool_)) and math.isfinite(float(v))]
    complete=len(values)==expected and len(valid)==expected
    return dict(n_expected=expected,n_observed=len(values),n_valid=len(valid),n_missing=max(expected-len(valid),0),
       median=float(np.median(valid)) if complete else None,observed_only_median=float(np.median(valid)) if valid else None,
       q25=float(np.quantile(valid,.25)) if complete else None,q75=float(np.quantile(valid,.75)) if complete else None,
       IQR=float(np.quantile(valid,.75)-np.quantile(valid,.25)) if complete else None,
       min=min(valid) if valid else None,max=max(valid) if valid else None)
def compare(actual,expected,where="value",tol=1e-6):
    if isinstance(expected,dict):
        if not isinstance(actual,dict):raise ValueError(where+": expected dict")
        for k,v in expected.items():
            if k not in actual:raise ValueError(where+": missing "+k)
            compare(actual[k],v,where+"."+k,tol)
    elif isinstance(expected,list):
        if not isinstance(actual,list) or len(actual)!=len(expected):raise ValueError(where+": list denominator")
        for i,(a,b) in enumerate(zip(actual,expected)):compare(a,b,where+"["+str(i)+"]",tol)
    elif expected is None or isinstance(expected,(str,bool)):
        if actual!=expected:raise ValueError(where+": exact value differs")
    elif isinstance(expected,(float,int,np.number)):
        if isinstance(actual,bool) or not isinstance(actual,(int,float,np.number)) or not math.isfinite(float(actual)) or not math.isclose(float(actual),float(expected),rel_tol=tol,abs_tol=tol):
            raise ValueError(where+": numeric value differs")
    elif actual!=expected:raise ValueError(where+": value differs")
def chain_data(path):
    model=next(PDBParser(QUIET=True).get_structure("raw",str(path)).get_models());result=[]
    for chain in model:
        residues=[r for r in chain if r.id[0]==" " and "CA" in r]
        if not residues:continue
        heavy=[]
        for r in residues:
            atoms=[np.asarray(a.coord,dtype=float) for a in r if a.element not in ("H","D")]
            if not atoms:raise ValueError("Empty residue heavy atoms")
            heavy.append(np.asarray(atoms))
        result.append(dict(id=chain.id,sequence="".join(seq1(r.resname) for r in residues),
            ca=np.asarray([r["CA"].coord for r in residues],float),
            plddt=np.asarray([r["CA"].bfactor for r in residues],float),heavy=heavy))
    return result
def contacts(a,b,cutoff):
    xa=np.concatenate(a["heavy"]);xb=np.concatenate(b["heavy"])
    ia=np.concatenate([np.full(len(v),i+1,int) for i,v in enumerate(a["heavy"])])
    ib=np.concatenate([np.full(len(v),i+1,int) for i,v in enumerate(b["heavy"])])
    neighborhoods=cKDTree(xa).query_ball_tree(cKDTree(xb),cutoff)
    pairs={(int(ia[i]),int(ib[j])) for i,js in enumerate(neighborhoods) for j in js}
    return sorted(pairs)
def mapping_check(query,reference,mapping):
    if len(set(mapping.values()))!=len(mapping):raise ValueError("Non-injective reference mapping")
    if any(i<1 or j<1 or i>len(query) or j>len(reference) or query[i-1]!=reference[j-1] for i,j in mapping.items()):
        raise ValueError("Reference mapping sequence identity differs")
def geometry(a,b,ref,partner,mapping,control,partner_mapping):
    mapping_check(a["sequence"],ref["sequence"],mapping)
    x=np.asarray([a["ca"][i-1] for i,j in sorted(mapping.items())])
    y=np.asarray([ref["ca"][j-1] for i,j in sorted(mapping.items())])
    xc=x.mean(0);yc=y.mean(0);u,_,vt=np.linalg.svd((x-xc).T@(y-yc));rotation=u@vt
    if np.linalg.det(rotation)<0:u[:,-1]*=-1;rotation=u@vt
    translation=yc-xc@rotation
    rmsd=float(np.sqrt(np.mean(np.sum((x@rotation+translation-y)**2,axis=1))))
    truth=contacts(ref,partner,5);pred=contacts(a,b,5)
    native_interface={i for i,j in truth};covered={mapping[i] for i,j in pred if i in mapping}
    matched=len(covered&native_interface);coverage=matched/len(native_interface) if native_interface else None
    precision=matched/len(covered) if covered else 0.
    f1=2*precision*coverage/(precision+coverage) if coverage is not None and precision+coverage>0 else (0. if coverage is not None else None)
    xatoms=np.concatenate(b["heavy"])@rotation+translation;yatoms=np.concatenate(partner["heavy"])
    overlap=cKDTree(xatoms).query_ball_tree(cKDTree(yatoms),2.5);native_overlapped={j for js in overlap for j in js}
    partner_rmsd=pair_recall=None
    if control:
        mapping_check(b["sequence"],partner["sequence"],partner_mapping)
        indices=sorted(partner_mapping.items())
        if len(indices)<3:raise ValueError("Too few native partner anchors")
        predca=np.asarray([b["ca"][i-1] for i,j in indices])@rotation+translation
        truthca=np.asarray([partner["ca"][j-1] for i,j in indices])
        partner_rmsd=float(np.sqrt(np.mean(np.sum((predca-truthca)**2,axis=1))))
        mapped={(mapping[i],partner_mapping[j]) for i,j in pred if i in mapping and j in partner_mapping}
        pair_recall=len(set(truth)&mapped)/len(truth) if truth else None
    sensitivity={}
    for cutoff in (4,8):
        tr=contacts(ref,partner,cutoff);pr=contacts(a,b,cutoff)
        nt={i for i,j in tr};pc={mapping[i] for i,j in pr if i in mapping}
        sensitivity[str(cutoff)]={"native_interface_target_residue_n":len(nt),
            "predicted_mapped_target_contact_residue_n":len(pc),
            "native_interface_coverage":len(nt&pc)/len(nt) if nt else None}
    return dict(status="RIGID_OCCLUSION_PROXY_ONLY",target_observed_alignment_n=len(mapping),target_recovery_RMSD_A=rmsd,
       native_target_interface_residue_n=len(native_interface),native_interface_coverage=coverage,
       contact_target_residue_precision=precision,contact_target_residue_recall=coverage,contact_target_residue_F1=f1,
       partner_atom_overlap_pairs_lt_2p5A=sum(len(js) for js in overlap),
       binder_atoms_overlapping_native_partner=sum(bool(js) for js in overlap),native_partner_atoms_overlapped=len(native_overlapped),
       native_partner_heavy_atom_n=len(yatoms),native_partner_atom_overlap_fraction=len(native_overlapped)/len(yatoms),
       contact_sensitivity=sensitivity,known_partner_target_aligned_CA_RMSD_A=partner_rmsd,known_partner_native_contact_recall=pair_recall,
       known_partner_observed_CA_n=len(partner_mapping) if control else None,
       known_partner_full_query_length=len(b["sequence"]) if control else None,
       known_partner_structural_recovery=(rmsd<=2 and f1>=.5) if control and f1 is not None else None,
       experimental_blockade=False)
def official_table(text):
    header=None;directions={};maximum=None
    for line in text.splitlines():
        v=line.split()
        if not v:continue
        if v[0]=="Chn1":header=v;continue
        if header is None:continue
        if len(v)!=len(header):raise ValueError("Malformed official ipSAE")
        row=dict(zip(header,v));pair=(row["Chn1"],row["Chn2"])
        if pair not in (("A","B"),("B","A")):continue
        if row["Type"]=="asym":
            if pair in directions:raise ValueError("Duplicate direction")
            directions[pair]=(float(row["ipSAE"]),float(row["ipSAE_d0dom"]) if "ipSAE_d0dom" in row else None)
        elif row["Type"]=="max":
            if maximum is not None:raise ValueError("Duplicate max")
            maximum=float(row["ipSAE"])
    if set(directions)!={("A","B"),("B","A")} or maximum is None:raise ValueError("Incomplete official score")
    a,ad=directions[("A","B")];b,bd=directions[("B","A")]
    if not math.isclose(max(a,b),maximum,abs_tol=1.000001e-6):raise ValueError("Official max mismatch")
    if any(not math.isfinite(v) or not 0<=v<=1 for v in (a,b,maximum)):raise ValueError("Score range")
    return dict(target_to_binder=a,binder_to_target=b,minimum=min(a,b),maximum=maximum,
                target_to_binder_d0dom=ad,binder_to_target_d0dom=bd)
def verify_receipt(receipt,P):
    path=P(receipt["path"],expected_sha=receipt["sha256"]).physical();h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):h.update(block)
    if h.hexdigest()!=receipt["sha256"] or ("bytes" in receipt and path.stat().st_size!=receipt["bytes"]):
        raise ValueError("Restored receipt mismatch: "+receipt["path"])
    return path
def recompute_model(engine,row,entity,target,control,ipsae,P,out):
    files={Path(v["path"]).name:verify_receipt(v,P) for v in row["raw_files"]}
    ps=[v for n,v in files.items() if n.endswith(".pdb")]
    js=[v for n,v in files.items() if n.endswith(".json")]
    if len(ps)!=1 or len(js)!=1:raise ValueError("Raw model identity ambiguity")
    chains=chain_data(ps[0])
    if len(chains)!=2 or [x["id"] for x in chains]!=["A","B"] or chains[0]["sequence"]!=entity["target_sequence"] or chains[1]["sequence"]!=entity["binder_sequence"]:
        raise ValueError("Raw model exact chain/query mismatch")
    a,b=chains;nt=len(a["sequence"]);total=nt+len(b["sequence"]);raw=json.loads(js[0].read_text())
    if engine=="boltz":
        pae=np.load(next(v for n,v in files.items() if n.startswith("pae_")),allow_pickle=False)["pae"].astype(float)
        pp=np.load(next(v for n,v in files.items() if n.startswith("plddt_")),allow_pickle=False)["plddt"].astype(float);scale=1
    else:pae=np.asarray(raw["pae"],float);pp=np.asarray(raw["plddt"],float);scale=100
    if pae.shape!=(total,total) or pp.shape!=(total,) or not np.isfinite(pae).all() or not np.isfinite(pp).all() or pae.min()<0 or pp.min()<0 or pp.max()>scale:
        raise ValueError("Raw confidence shape/units/nonfinite mismatch")
    pp=pp/scale
    if np.max(np.abs(np.concatenate([a["plddt"],b["plddt"]])-pp*100))>.02:raise ValueError("CA confidence alignment differs")
    iptm=float(raw["iptm"])
    if not math.isfinite(iptm) or not 0<=iptm<=1:raise ValueError("Invalid global ipTM")
    pairs=contacts(a,b,5);binder=float(pp[nt:].mean());interface_plddt=contact_pae=None
    r0=None
    if pairs:
        ids=sorted({i-1 for i,j in pairs})+sorted({nt+j-1 for i,j in pairs})
        interface_plddt=float(pp[ids].mean())
        contact_pae=float(np.mean([pae[i-1,nt+j-1] for i,j in pairs]+[pae[nt+j-1,i-1] for i,j in pairs]))
        ratios=[iptm/.75,binder/.8,interface_plddt/.8]
        if contact_pae!=0:ratios.append(8/contact_pae)
        r0=min(ratios)
    out.mkdir(parents=True,exist_ok=False)
    (out/"model.pdb").write_bytes(ps[0].read_bytes())
    (out/"scores.json").write_text(json.dumps({"pae":pae.tolist(),"plddt":(pp*100).tolist(),"iptm":iptm})+"\n")
    official={}
    for cutoff in (10,15):
        cmd=[sys.executable,str(ipsae),str(out/"scores.json"),str(out/"model.pdb"),str(cutoff),"15"]
        pr=subprocess.run(cmd,capture_output=True,text=True)
        (out/("ipsae_"+str(cutoff)+".log")).write_text(pr.stdout+"\n"+pr.stderr)
        if pr.returncode:raise ValueError("Restored official ipSAE rerun failed")
        official[str(cutoff)]=official_table((out/("model_"+str(cutoff)+"_15.txt")).read_text())
    refs=chain_data(verify_receipt(target["reference_complex"],P))
    ref=next(v for v in refs if v["id"]=="A");partner=next(v for v in refs if v["id"]=="B")
    mapping={int(k):int(v) for k,v in target["query_to_reference_indices"].items()}
    pmapping={int(k):int(v) for k,v in target.get("native_partner_query_to_reference_indices",{}).items()}
    geo=geometry(a,b,ref,partner,mapping,control,pmapping)
    return dict(status="VALID" if pairs else "NO_INTERFACE",R0=r0,R1=official["10"]["maximum"] if pairs else None,
       global_iptm=iptm,target_plddt_fraction=float(pp[:nt].mean()),binder_plddt_fraction=binder,
       interface_plddt_fraction=interface_plddt,bidirectional_contact_PAE_A=contact_pae,
       contact_residue_pairs=[list(v) for v in pairs],ipsae=official,geometry=geo)
def audit_common(config,authority_root,restore_root,out,aliases=None):
    P=path_factory(authority_root,restore_root,aliases);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    result=json.loads(P(config["result"]).read_text());analysis=json.loads(P(config["analysis_plan"]).read_text())
    membership=json.loads(P(config["membership"]).read_text());producer=json.loads(P(config["producer_acceptance"]).read_text())
    plan=json.loads(verify_receipt(result["plan"],P).read_text())
    verify_receipt(result["analysis_plan"],P)
    if result["analysis_plan"]["path"]!=config["analysis_plan"]:raise ValueError("Analysis source path differs")
    if membership["inference_plan"]!=result["plan"] or analysis["inference_plan"]!=result["plan"]:
        raise ValueError("Frozen common plan pointers disagree")
    ipsae=verify_receipt(config["official_ipsae"],P)
    expected={x["job_key"]:x for x in plan["jobs"]}
    rows={x["job_key"]:x for x in result["results"]}
    if set(rows)!=set(expected) or len(rows)!=len(result["results"]):raise ValueError("Lost/duplicate fixed common job")
    entities={x["blind_id"]:x for x in plan["entities"]};targets={x["target_id"]:x for x in analysis["targets"]}
    controls={x["blind_id"] for x in analysis["native_recovery_controls"]}
    completed=unresolved=0;msa_roundtrips=0
    for key,row in rows.items():
        job=expected[key]
        if job["engine"]=="af2" and row.get("worker_record"):
            worker=json.loads(verify_receipt(row["worker_record"],P).read_text())
            if worker["settings"]!=plan["settings"]:raise ValueError("Worker/settings mismatch")
            worker_directory=P(row["worker_record"]["path"]).physical().parent
            saved=json.loads((worker_directory/"af2/config.json").read_text())
            wanted={"model_type":"alphafold2_multimer_v3","num_models":5,"num_seeds":1,"random_seed":31021,"num_recycles":3,"num_relax":0,"use_templates":False}
            for name,value in wanted.items():
                actual=next((saved[n] for n in ([name,"num_recycle"] if name=="num_recycles" else [name]) if n in saved),None)
                if actual!=value:raise ValueError("Restored AF2 actual config mismatch: "+name)
            helper=verify_receipt(config["msa_roundtrip_source"],P)
            envpython=config["colabfold_cpu_python"]
            rebuild=str(helper.parent)
            code="import json,sys; sys.path.insert(0,sys.argv[1]); from control_msa_check import verify_roundtrip; print(json.dumps(verify_roundtrip(*sys.argv[2:]),sort_keys=True))"
            entity=entities[job["blind_id"]]
            pr=subprocess.run([envpython,"-c",code,rebuild,str(verify_receipt(job["input"],P)),str(worker_directory/"af2/complex.a3m"),entity["target_sequence"],entity["binder_sequence"]],
                 env=dict(os.environ,CUDA_VISIBLE_DEVICES="",JAX_PLATFORMS="cpu",PYTHONNOUSERSITE="1"),capture_output=True,text=True)
            if pr.returncode:raise ValueError("Restored exact AF2 MSA/deletion feature semantics failed:"+pr.stderr[-1000:])
            (out/(key+"_MSA_ROUNDTRIP.json")).write_text(pr.stdout)
            msa_roundtrips+=1
        slots={json.dumps(s,sort_keys=True) for s in job["slots"]}
        if {json.dumps(v["slot"],sort_keys=True) for v in row["models"]}!=slots or len(row["models"])!=len(slots):
            raise ValueError("Fixed model denominator differs")
        for i,model in enumerate(row["models"]):
            if model["status"] in ("VALID","NO_INTERFACE"):
                actual=recompute_model(job["engine"],model,entities[job["blind_id"]],targets[job["target_id"]],
                           job["blind_id"] in controls,ipsae,P,out/"models"/key/str(i))
                for name,value in actual.items():compare(value,model[name],key+"."+name)
                completed+=1
            elif model["status"]=="MODEL_UNRESOLVED":
                if model["R0"] is not None or model["R1"] is not None or not model.get("reason"):
                    raise ValueError("Unresolved model lacks typed null")
                unresolved+=1
            else:raise ValueError("Unknown model status")
        for axis in ("R0","R1"):compare(summary([v[axis] for v in row["models"]],job["expected_models"]),row[axis],key+"."+axis)
        if row["operational_pass"] is not None or row.get("experimental_probability") is not None or row.get("experimental_blockade"):
            raise ValueError("Unsupported operational/experimental claim")
    if completed+unresolved!=sum(x["expected_models"] for x in plan["jobs"]):
        raise ValueError("Full model denominator lost")
    by={(v["blind_id"],v["engine"],v["variant"]):v for v in rows.values()};groups=collections.defaultdict(list)
    for m in membership["members"]:
        for engine in ("boltz","af2"):
            v=by[(m["blind_id"],engine,"primary")]
            groups[(m["target_id"],m["method_id"],m["seed"],m["cohort"],engine)].append(v)
    summaries=[]
    for (target,method,seed,cohort,engine),group in sorted(groups.items()):
        values=[v["R1"]["median"] for v in group]
        summaries.append(dict(target_id=target,method_id=method,seed=seed,cohort=cohort,engine=engine,n_selected=len(group),
           n_R1_complete=sum(v is not None for v in values),R1_candidates=summary(values,len(group)),
           R0_candidates=summary([v["R0"]["median"] for v in group],len(group)),
           model_coverage=dict(expected=sum(v["R1"]["n_expected"] for v in group),valid=sum(v["R1"]["n_valid"] for v in group)),
           operational_pass=None))
    compare(summaries,producer["cohort_summaries"],"cohort_summaries")
    if producer["n_jobs"]!=len(rows) or producer["n_models_expected"]!=completed+unresolved:
        raise ValueError("Producer acceptance denominator differs")
    acceptance=dict(status="RESTORED_RAW_COMMON_SCORES_AND_COHORT_STATISTICS_RECOMPUTED",
       evidence_reads="RESTORED_TREE_ONLY",production_scoring_imports=False,official_ipSAE_rerun=True,
       n_jobs=len(rows),n_AF2_actual_MSA_feature_roundtrips=msa_roundtrips,n_models_recomputed_from_raw=completed,n_models_typed_unresolved=unresolved,
       cohort_summaries=summaries,native_control_blind_ids=sorted(controls),
       scientific_scope="COMPUTATIONAL_ONLY",frozen_bytes_changed=False)
    (out/"acceptance.json").write_text(json.dumps(acceptance,indent=2,allow_nan=False)+"\n")
    return acceptance

