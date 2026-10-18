#!/usr/bin/env python3
"""Fixed R0/R1 development scoring with honest transfer abstention. CPU only."""
import argparse,collections,datetime,hashlib,json,math,os,shutil,subprocess,sys,unittest,zipfile
from pathlib import Path
import numpy as np
from Bio.PDB import PDBParser,MMCIFParser
from Bio.SeqUtils import seq1
from Bio import Align
ROOT=Path("/lustre/users/u21111210118/projects/test9")
STEP=ROOT/"steps/20_screening_improvement"
REVISION="6174cf9e71cb1bd660cc805856a18c4871a6dec3"
EXPECTED={(m,s) for m in range(1,6) for s in (1042,1043,1044)}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def rec(path):
    path=Path(path);h=hashlib.sha256();n=0
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b);n+=len(b)
    return dict(path=str(path),sha256=h.hexdigest(),bytes=n)
def verify(record):
    actual=rec(record["path"])
    if actual["sha256"]!=record["sha256"] or ("bytes" in record and actual["bytes"]!=record["bytes"]):raise ValueError("Hash mismatch: "+record["path"])
    return Path(record["path"])
def read(path):return json.loads(Path(path).read_text())
def dump(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x") as f:json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False);f.write("\n")
def finite(x):return isinstance(x,(int,float,np.number)) and not isinstance(x,(bool,np.bool_)) and math.isfinite(float(x))
def summary(values,expected=15):
    valid=[float(v) for v in values if finite(v)]
    complete=len(values)==expected and len(valid)==expected
    return dict(n_expected=expected,n_observed=len(values),n_valid=len(valid),n_missing=max(expected-len(valid),0),median=float(np.median(valid)) if complete else None,observed_only_median=float(np.median(valid)) if valid else None,q25=float(np.quantile(valid,.25)) if complete else None,q75=float(np.quantile(valid,.75)) if complete else None,IQR=float(np.quantile(valid,.75)-np.quantile(valid,.25)) if complete else None,min=min(valid) if valid else None,max=max(valid) if valid else None)
def components(iptm,binder,interface,pae):
    vals=(iptm,binder,interface,pae)
    if any(not finite(v) for v in vals):return dict(status="MISSING_REQUIRED_FEATURE",ratios=None,limiting_components=[],score=None)
    if not all(0<=v<=1 for v in vals[:3]) or pae<0:raise ValueError("Units/range: ipTM and pLDDT must be fractions; PAE must be Angstrom")
    ratios=dict(global_iptm=iptm/.75,binder_plddt=binder/.80,interface_plddt=interface/.80,contact_PAE=None if pae==0 else 8/pae)
    active={k:v for k,v in ratios.items() if v is not None};score=min(active.values())
    return dict(status="VALID",ratios=ratios,limiting_components=[k for k,v in active.items() if math.isclose(v,score,rel_tol=0,abs_tol=1e-12)],score=score,zero_PAE_nonlimiting=pae==0)
def parse_ipsae(text,a="A",b="B"):
    header=None;rows={};official=None
    for line in text.splitlines():
        parts=line.split()
        if not parts:continue
        if parts[0]=="Chn1":header=parts;continue
        if header is None:continue
        if len(parts)!=len(header):raise ValueError("Malformed official ipSAE row")
        row=dict(zip(header,parts));pair=(row["Chn1"],row["Chn2"])
        if pair not in ((a,b),(b,a)):continue
        if row["Type"]=="asym":
            if pair in rows:raise ValueError("Duplicate ipSAE direction")
            vals={k:float(row[k]) for k in ("ipSAE","ipSAE_d0dom") if k in row}
            if any(not finite(v) or not 0<=v<=1 for v in vals.values()):raise ValueError("Invalid official ipSAE")
            rows[pair]=vals
        elif row["Type"]=="max":
            val=float(row["ipSAE"])
            if not finite(val) or not 0<=val<=1:raise ValueError("Invalid max")
            if official is not None:raise ValueError("Duplicate max")
            official=val
    if set(rows)!={(a,b),(b,a)} or official is None:raise ValueError("Missing official direction or max")
    av=rows[(a,b)]["ipSAE"];bv=rows[(b,a)]["ipSAE"]
    if not math.isclose(max(av,bv),official,abs_tol=1.000001e-6):raise ValueError("Official max mismatch")
    return dict(target_to_binder=av,binder_to_target=bv,minimum=min(av,bv),maximum=official,target_to_binder_d0dom=rows[(a,b)].get("ipSAE_d0dom"),binder_to_target_d0dom=rows[(b,a)].get("ipSAE_d0dom"))
def chain_records(path):
    parser=MMCIFParser(QUIET=True) if str(path).endswith(".cif") else PDBParser(QUIET=True)
    model=next(parser.get_structure("x",str(path)).get_models());out=[]
    for ch in model:
        rs=[r for r in ch if r.id[0]==" " and "CA" in r]
        if rs:out.append(dict(chain=ch.id,sequence="".join(seq1(r.resname) for r in rs),ca=np.asarray([r["CA"].coord for r in rs],dtype=float)))
    return out
def alignment_map(query,reference):
    # Semiglobal sequence correspondence; only exact amino-acid matches are used.
    al=Align.PairwiseAligner(mode="global",match_score=3,mismatch_score=-9,open_gap_score=-3,extend_gap_score=-.2).align(query,reference)[0]
    pairs=[(int(i),int(j)) for i,j in al.indices.T if i>=0 and j>=0]
    mismatch=sum(query[i]!=reference[j] for i,j in pairs)
    exact=[(i,j) for i,j in pairs if query[i]==reference[j]]
    return dict(pairs=exact,n_aligned=len(pairs),mismatches=mismatch,coverage=len(exact)/len(query) if query else None,identity=len(exact)/len(pairs) if pairs else None)
def reference_chain(query,records,min_coverage=.9):
    candidates=[]
    for r in records:
        mp=alignment_map(query,r["sequence"])
        if mp["mismatches"]==0 and mp["coverage"]>=min_coverage:
            candidates.append((mp["coverage"],-abs(len(r["sequence"])-len(query)),r["chain"],r,mp))
    if not candidates:return None,None
    best=sorted(candidates,key=lambda x:(-x[0],-x[1],x[2]))[0]
    return best[3],best[4]
def fit_rmsd(x,y):
    x=np.asarray(x,float);y=np.asarray(y,float)
    if x.shape!=y.shape or len(x)<3 or not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError("Invalid coordinate correspondence")
    xc=x-x.mean(0);yc=y-y.mean(0);u,_,vh=np.linalg.svd(xc.T@yc);rot=u@vh
    if np.linalg.det(rot)<0:u[:,-1]*=-1;rot=u@vh
    return float(np.sqrt(np.mean(np.sum((xc@rot-yc)**2,axis=1))))
def target_recovery(query,model,refs):
    target=reference_chain(query,model,1)[0]
    if target is None:raise ValueError("Submitted target is not exact in model")
    out={}
    for name,(records,record,kind) in refs.items():
        rr,mp=reference_chain(query,records,.9)
        if rr is None:out[name]=dict(status="NOT_ESTIMABLE_NO_EXACT_REFERENCE_CORE",rmsd_A=None,reference=record,reference_kind=kind);continue
        ii=np.array([i for i,j in mp["pairs"]],int);jj=np.array([j for i,j in mp["pairs"]],int)
        out[name]=dict(status="EXACT_CORE_MAPPING",rmsd_A=fit_rmsd(target["ca"][ii],rr["ca"][jj]),mapped_residues=len(ii),query_length=len(query),observed_coverage=mp["coverage"],reference_chain=rr["chain"],reference=record,reference_kind=kind)
    return out
def msa_diagnostic(path,query,calculate_neff=False):
    headers=[];sequences=[];current=[]
    for line in Path(path).read_text().splitlines():
        if not line or line.startswith("#"):continue
        if line.startswith(">"):
            if current:sequences.append("".join(current));current=[]
            headers.append(line[1:])
        else:current.append(line.strip())
    if current:sequences.append("".join(current))
    aligned=["".join(c for c in s if not c.islower() and c!=".") for s in sequences]
    if not aligned or aligned[0]!=query:raise ValueError("Target MSA exact query mismatch")
    if any(len(s)!=len(query) for s in aligned):raise ValueError("A3M aligned width mismatch")
    rows=[]
    for i,s in enumerate(aligned):
        observed=[p for p,c in enumerate(s) if c!="-"]
        matches=sum(s[p]==query[p] for p in observed)
        counts=collections.Counter(s[p] for p in observed);n=len(observed)
        ent=-sum((v/n)*math.log2(v/n) for v in counts.values()) if n else 0
        rows.append(dict(index=i,header=headers[i],sequence_sha256=hashlib.sha256(s.encode()).hexdigest(),coverage=n/len(query),identity_on_aligned_nongap=matches/n if n else None,shannon_entropy_bits=ent,low_complexity_entropy_lt2=ent<2))
    neff=None
    if calculate_neff:
        arr=np.array([list(s) for s in aligned]);weights=[]
        for i in range(len(arr)):
            # Full-query-width identity penalizes gap-heavy matches.
            nclose=int(((arr==arr[i])&(arr!="-")&(arr[i]!="-")).sum(1).__ge__(.8*len(query)).sum())
            weights.append(1/max(nclose,1))
        neff=float(sum(weights))
    nonquery=rows[1:];qcov=sum(v["coverage"]>=.7 for v in nonquery);qid=sum(v["coverage"]>=.7 and v["identity_on_aligned_nongap"] is not None and v["identity_on_aligned_nongap"]>=.3 for v in nonquery)
    return dict(status="MSA_QUERY_AND_ALIGNED_ROWS_DIAGNOSED",input=rec(path),query_length=len(query),raw_rows=len(rows),unique_aligned_sequences=len(set(aligned)),nonquery_rows=len(nonquery),nonquery_coverage_ge70_count=qcov,nonquery_coverage_ge70_identity_ge30_count=qid,nonquery_low_complexity_count=sum(v["low_complexity_entropy_lt2"] for v in nonquery),coverage_median=float(np.median([v["coverage"] for v in nonquery])) if nonquery else None,identity_median=float(np.median([v["identity_on_aligned_nongap"] for v in nonquery if v["identity_on_aligned_nongap"] is not None])) if qcov else None,neff80_full_query_width=neff,neff_scope="Only BBF target constructs; fixed full-width 80% identity redundancy weighting" if calculate_neff else "Not computed; raw/unique rows and identity/coverage diagnostics only",homology_status="DIAGNOSTIC_NOT_TAXONOMY_VERIFIED",rows=rows,limitations="Sequence identity/coverage do not establish evolutionary homology or exact per-recycle MSA sampling.")
def auc(rows,score_key):
    p=[r[score_key] for r in rows if r["positive"] and finite(r.get(score_key))]
    n=[r[score_key] for r in rows if not r["positive"] and finite(r.get(score_key))]
    if not p or not n:return None
    return float(sum(1 if a>b else .5 if a==b else 0 for a in p for b in n)/(len(p)*len(n)))
def metrics(rows,score_key,pred_key="development_prediction"):
    valid=[v for v in rows if finite(v.get(score_key))]
    pred=[v for v in rows if type(v.get(pred_key)) is bool]
    tp=sum(v["positive"] and v[pred_key] for v in pred);fp=sum(not v["positive"] and v[pred_key] for v in pred);tn=sum(not v["positive"] and not v[pred_key] for v in pred);fn=sum(v["positive"] and not v[pred_key] for v in pred)
    return dict(n_eligible=len(rows),n_positive=sum(v["positive"] for v in rows),n_negative=sum(not v["positive"] for v in rows),n_scored=len(valid),n_predicted=len(pred),score_coverage=len(valid)/len(rows) if rows else None,prediction_coverage=len(pred)/len(rows) if rows else None,TP=tp,FP=fp,TN=tn,FN=fn,TPR=tp/(tp+fn) if tp+fn else None,FPR=fp/(fp+tn) if fp+tn else None,AUROC=auc(rows,score_key))
def macro(metrics_by_family):
    return {k:dict(value=float(np.mean(vals)) if vals else None,defined_families=len(vals),families=len(metrics_by_family)) for k in ("TPR","FPR","AUROC") for vals in [[m[k] for m in metrics_by_family.values() if finite(m.get(k))]]}
def fit_threshold(train,score_key):
    usable=[dict(v) for v in train if finite(v.get(score_key))]
    positives=sum(v["positive"] for v in usable);negative=len(usable)-positives
    pf=sorted({v["family"] for v in usable if v["positive"]});nf=sorted({v["family"] for v in usable if not v["positive"]})
    support=dict(n_positive=positives,n_negative=negative,positive_families=pf,negative_families=nf,small_sample_reasons=[])
    if len(pf)<2:support["small_sample_reasons"].append("FEWER_THAN_TWO_POSITIVE_FAMILIES")
    if len(nf)<2:support["small_sample_reasons"].append("FEWER_THAN_TWO_NEGATIVE_FAMILIES")
    if negative<14:support["small_sample_reasons"].append("FEWER_THAN_14_NEGATIVES")
    if not positives or not negative:return dict(status="NOT_ESTIMABLE_TRAINING_MISSING_CLASS",threshold=None,support=support,training_ids=sorted(v["id"] for v in train))
    thresholds=sorted({v[score_key] for v in usable})+[float(np.nextafter(max(v[score_key] for v in usable),np.inf))]
    choices=[]
    for t in thresholds:
        rs=[dict(v,development_prediction=bool(v[score_key]>=t)) for v in usable]
        by={f:metrics([v for v in rs if v["family"]==f],score_key) for f in sorted({v["family"] for v in usable})}
        if any(by[f]["FPR"]>.20+1e-12 for f in nf):continue
        ma=macro(by);choices.append((ma["TPR"]["value"],-ma["FPR"]["value"],t,by,ma))
    if not choices:raise ValueError("Above-max threshold must be feasible")
    best=max(choices,key=lambda x:x[:3])
    return dict(status="DEVELOPMENT_HEURISTIC_NOT_TRANSFER_GUARANTEE",threshold=best[2],objective="max macro-family TPR; each negative training family FPR<=0.20; ties min macro FPR then higher threshold",training_by_family=best[3],training_macro=best[4],support=support,training_ids=sorted(v["id"] for v in train))
def deployment_decision(row,fit,known_families,score_key):
    reasons=[]
    if not finite(row.get(score_key)):reasons.append("MISSING_COMPLETE_SCORE")
    if fit["threshold"] is None:reasons.append("TRAINING_MISSING_CLASS")
    if fit["support"].get("small_sample_reasons"):reasons.append("SMALL_SAMPLE_UNSUPPORTED")
    if row["family"] not in known_families:reasons.append("NEW_FAMILY_UNVALIDATED")
    return dict(prediction=None if reasons else bool(row[score_key]>=fit["threshold"]),reasons=reasons,experimental_success_probability=None)
def evaluate(rows,score_key,near):
    folds=[];allout=[]
    for fam in sorted({v["family"] for v in rows}):
        test=[dict(v) for v in rows if v["family"]==fam];blocked={a for a,b in near if b in {v["id"] for v in test}}
        train=[dict(v) for v in rows if v["family"]!=fam and v["id"] not in blocked]
        fit=fit_threshold(train,score_key);inner=[]
        for inf in sorted({v["family"] for v in train}):
            itest=[dict(v) for v in train if v["family"]==inf];iblocked={a for a,b in near if b in {v["id"] for v in itest}}
            itr=[dict(v) for v in train if v["family"]!=inf and v["id"] not in iblocked]
            ifit=fit_threshold(itr,score_key)
            ir=[dict(v,development_prediction=None if ifit["threshold"] is None or not finite(v.get(score_key)) else bool(v[score_key]>=ifit["threshold"])) for v in itest]
            inner.append(dict(family=inf,fit=ifit,metrics=metrics(ir,score_key),used_for_score_selection=False))
        out=[]
        for v in test:
            dep=deployment_decision(v,fit,{x["family"] for x in train},score_key)
            v.update(development_prediction=None if fit["threshold"] is None or not finite(v.get(score_key)) else bool(v[score_key]>=fit["threshold"]),operational_prediction=dep["prediction"],abstention_reasons=dep["reasons"])
            out.append(v)
        allout.extend(out);folds.append(dict(family=fam,excluded_homologous_training_ids=sorted(blocked),fit=fit,inner_development_diagnostics=inner,metrics=metrics(out,score_key),operational_metrics=metrics(out,score_key,"operational_prediction"),rows=out))
    by={f["family"]:f["metrics"] for f in folds}
    return dict(score=score_key,folds=folds,macro=macro(by),pooled_raw_score_metrics=metrics(allout,score_key),operational_pooled_metrics=metrics(allout,score_key,"operational_prediction"),scope="All78 are development; outer/inner folds are diagnostics, not untouched validation; raw pooled AUC is family/assay-confounded",selection="Both pre-frozen R0 and R1 reported; no score/feature hyperparameter selection",rows=allout)
def prep_load(path):
    prep=read(path)
    if prep["status"]!="ALL78_1170_INPUT_SCHEMA_VERIFIED_PROTOCOL_FROZEN":raise ValueError("Preparation not accepted")
    for v in prep["inputs"]:verify(v)
    src=prep["source_inputs"]
    return prep,{k:read(verify(v)) for k,v in src.items() if k!="rf_archive"}
def run(preparation):
    prep,inputs=prep_load(preparation);job=os.environ["SLURM_JOB_ID"]
    run=STEP/"runs"/(datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"_"+job)
    run.mkdir(parents=True,exist_ok=False);out=run/"outputs";out.mkdir()
    acc=inputs["acceptance"];scores={v["id"]:v for v in inputs["scores"]["entries"]};elig={v["id"]:v for v in inputs["eligibility"]["entries"]}
    rf={v["id"]:v for v in inputs["rf_overlay"]["entries"]};bc={v["id"]:v for v in inputs["bc_overlay"]["entries"]}
    script=verify(inputs["ipsae"]["files"]["ipsae.py"])
    archive=zipfile.ZipFile(verify(prep["source_inputs"]["rf_archive"]))
    native_record=inputs["bc_overlay"]["sources"]["pdb9HAC"]["artifact"];native_chains=chain_records(verify(native_record))
    baserows=[];modelrows=[];msas=[];ref_records=[];table_records=[]
    target_conditions={}
    for a in acc["accepted_conditions"]:
        e=a["condition"];target_conditions[e["target_msa_key"]]=e
    for key,msa in inputs["msa"]["targets"].items():
        e=target_conditions[key];d=msa_diagnostic(verify(msa["input"]),e["target_sequence"],e["target"]=="BBF-14");d["target_msa_key"]=key;d["target"]=e["target"];msas.append(d)
    dump(out/"msa_diagnostics.json",dict(status="ALL_SIX_TARGET_MSAS_DIAGNOSED",targets=msas))
    for a in acc["accepted_conditions"]:
        e=a["condition"];ident=e["condition_id"];directory=run/"models"/ident;directory.mkdir(parents=True)
        if ident in rf:
            pr=next(p for p in rf[ident]["identity"]["provenance"] if p.get("member","").endswith(".pdb"))
            b=archive.read(pr["member"])
            if hashlib.sha256(b).hexdigest()!=pr["member_sha256"]:raise ValueError("RF author PDB member hash mismatch")
            refpath=directory/"author_reference.pdb";refpath.write_bytes(b);arec=rec(refpath);kind="AUTHOR_PREDICTED_COMPLEX_TARGET_NOT_EXPERIMENTAL"
        else:
            arec=bc[ident]["author_design_model"];verify(arec);kind="AUTHOR_PREDICTED_COMPLEX_TARGET_NOT_EXPERIMENTAL"
        author=chain_records(arec["path"]);refs={"author_predicted":(author,arec,kind)}
        ref_records.append(arec)
        if e["target"]=="BBF-14":refs["experimental_9HAC"]=(native_chains,native_record,"EXPERIMENTAL_BOUND_TARGET_CORE")
        original={(m["model"],m["seed"]):m for m in scores[ident]["models"]};rows=[]
        for m in sorted(a["models"],key=lambda x:(x["model"],x["seed"])):
            old=original[(m["model"],m["seed"])]
            assert m["pdb"]==old["pdb"] and m["scores"]==old["scores"]
            verify(m["pdb"]);verify(m["scores"])
            raw=read(m["scores"]["path"]);model=chain_records(m["pdb"]["path"])
            assert len(model)==2 and model[0]["sequence"]==e["target_sequence"] and model[1]["sequence"]==e["sequence"]
            pp=np.asarray(raw["plddt"],float);pae=np.asarray(raw["pae"],float)
            if pp.shape!=(len(e["target_sequence"])+len(e["sequence"]),) or not np.isfinite(pp).all() or pp.min()<0 or pp.max()>100:raise ValueError("Raw pLDDT units/range")
            if not np.isfinite(pae).all() or pae.min()<0:raise ValueError("Raw PAE units/range")
            cc=components(old["global_iptm"],old["binder_plddt"],old["interface_plddt"],old["bidirectional_contact_PAE_A"])
            if cc["score"] is None or not math.isclose(cc["score"],old["confidence_baseline"],abs_tol=1e-12):raise ValueError("R0 differs from accepted original")
            md=directory/(str(m["model"])+"_"+str(m["seed"]));md.mkdir()
            pdb=md/"model.pdb";sc=md/"scores.json"
            # Hard links avoid duplicating raw bytes and keep output writes in new step.
            os.link(m["pdb"]["path"],pdb);os.link(m["scores"]["path"],sc)
            ips={}
            for cut in (10,15):
                proc=subprocess.run([sys.executable,str(script),str(sc),str(pdb),str(cut),"15"],capture_output=True,text=True)
                log=md/("ipsae_"+str(cut)+".log");log.write_text(proc.stdout+"\n"+proc.stderr)
                if proc.returncode:raise RuntimeError("Official ipSAE failed: "+proc.stderr[-1000:])
                table=md/("model_"+str(cut)+"_15.txt");ips[str(cut)]=parse_ipsae(table.read_text(),model[0]["chain"],model[1]["chain"])
                for p in sorted(md.glob("model_"+str(cut)+"_15*")):table_records.append(rec(p))
                table_records.append(rec(log))
            rr=dict(id=ident,source_id=e["source_id"],target=e["target"],model=m["model"],seed=m["seed"],pdb=m["pdb"],scores=m["scores"],R0=cc["score"],components=cc,ipsae=ips,target_recovery=target_recovery(e["target_sequence"],model,refs),target_length=len(e["target_sequence"]),binder_length=len(e["sequence"]),target_plddt=old["target_plddt"],binder_plddt=old["binder_plddt"],interface_plddt=old["interface_plddt"],contact_residue_pair_count=old["contact_residue_pair_count"],target_contact_residue_count=old["target_contact_residue_count"],binder_contact_residue_count=old["binder_contact_residue_count"],binder_contact_fraction=old["binder_contact_residue_count"]/len(e["sequence"]),contact_pairs_per_binder_residue=old["contact_residue_pair_count"]/len(e["sequence"]))
            modelrows.append(rr);rows.append(rr)
        q=dict(elig[ident]);q.update(target_length=len(e["target_sequence"]),binder_length=len(e["sequence"]),model_count=len(rows),scores=dict(R0=summary([v["R0"] for v in rows]),R1=summary([v["ipsae"]["10"]["maximum"] for v in rows]),min10=summary([v["ipsae"]["10"]["minimum"] for v in rows]),max15=summary([v["ipsae"]["15"]["maximum"] for v in rows]),min15=summary([v["ipsae"]["15"]["minimum"] for v in rows])),R0=summary([v["R0"] for v in rows])["median"],R1=summary([v["ipsae"]["10"]["maximum"] for v in rows])["median"],limiting_component_counts=dict(collections.Counter(k for v in rows for k in v["components"]["limiting_components"])),target_plddt=summary([v["target_plddt"] for v in rows]),target_recovery={name:summary([v["target_recovery"][name]["rmsd_A"] for v in rows]) for name in refs})
        q["original_author_mean_global_iptm"]=float(bc[ident]["primary_trace"]["all_primary_fields"]["Average_i_pTM"]) if ident in bc else None
        q["monomer_feature_status"]="NOT_RECOMPUTED_IN_THIS_CPU_STEP; existing published monomer summaries are not common-protocol models"
        baserows.append(q);print("SCORED",ident,q["R0"],q["R1"],flush=True)
    archive.close()
    near={(v["id1"],v["id2"]) for v in inputs["leakage"]["pairs"]};near|={(b,a) for a,b in near}
    analyses={name:{key:evaluate([dict(v) for v in baserows if v[field]],key,near) for key in ("R0","R1")} for name,field in [("main","main_eligible"),("screen_sensitivity","screen_sensitivity_eligible")]}
    result=dict(status="ALL78_DEVELOPMENT_SCORES_AND_TRANSFER_DIAGNOSTICS_COMPLETE",job_id=job,created_utc=now(),scope="DEVELOPMENT_ONLY_NOT_BINDING_PROBABILITY_OR_BLOCKADE",counts=dict(identities=len(baserows),models=len(modelrows),complete_R0=sum(v["R0"] is not None for v in baserows),complete_R1=sum(v["R1"] is not None for v in baserows),main=sum(v["main_eligible"] for v in baserows),sensitivity=sum(v["screen_sensitivity_eligible"] for v in baserows)),entries=baserows,analyses=analyses,independent_experimental_validation=False)
    dump(out/"model_features1170.json",dict(status="ALL1170_RAW_MODELS_RETAINED_AND_OFFICIAL_IPSAE_SCORED",rows=modelrows))
    dump(out/"screening_transfer.json",result)
    tests=run_tests();dump(out/"tests.json",tests)
    report=build_report(result,msas,run);(out/"REPORT.md").write_text(report)
    manifest=dict(status="SCREENING_IMPROVEMENT_COMPLETE_PENDING_CONTENT_VALIDATION",created_utc=now(),job_id=job,preparation=rec(preparation),source=rec(__file__),protocol=rec(STEP/"PROTOCOL.md"),inputs=prep["inputs"]+list(inputs["ipsae"]["files"].values())+[native_record],author_reference_files=ref_records,official_output_files=table_records,outputs=[rec(out/p) for p in ["model_features1170.json","screening_transfer.json","msa_diagnostics.json","tests.json","REPORT.md"]],counts=result["counts"])
    dump(run/"manifest.json",manifest)
    dump(STEP/"run_pointer.json",dict(status=manifest["status"],manifest=rec(run/"manifest.json")))
    print(json.dumps(dict(status=result["status"],counts=result["counts"],manifest=rec(run/"manifest.json")),indent=2),flush=True)
def build_report(result,msas,run):
    def fmt(v):return "不可估计" if v is None else f"{v:.3f}"
    lines=["# 跨家族筛选改进：开发诊断与拒判报告","","状态：完成真实CPU重算；内容验收另见acceptance.json。","",
    "全部78条旧控制均为开发数据，1170个模型是技术重复。固定R0原confidence与R1官方ipSAE10-max，不选择表现较好者作为事后主评分。主资格32、宽条件敏感性67；剩余11条QC未解决身份全部保留。无实验概率、亲和力或阻断推断。","",
    "R0分数保留原定义；新阈值在原始单位以每个阴性训练family FPR≤0.20、最大宏TPR确定。外层留family，内层只做训练family诊断，无特征权重/超参数选择。低家族数、少阴性及新家族均显式拒判。","",
    "|集合|评分|留出family|n（阳/阴）|评分覆盖|开发预测覆盖|TPR|FPR|家族内AUROC|训练原始阈值|操作判定覆盖|",
    "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name,a in result["analyses"].items():
        for score,res in a.items():
            for fold in res["folds"]:
                m=fold["metrics"];o=fold["operational_metrics"]
                lines.append(f"|{name}|{score}|{fold['family']}|{m['n_eligible']}（{m['n_positive']}/{m['n_negative']}）|{m['n_scored']}/{m['n_eligible']}|{m['n_predicted']}/{m['n_eligible']}|{fmt(m['TPR'])}|{fmt(m['FPR'])}|{fmt(m['AUROC'])}|{fmt(fold['fit']['threshold'])}|{o['n_predicted']}/{o['n_eligible']}|")
    lines+=["","|集合|评分|宏TPR（有定义家族）|宏FPR（有定义家族）|宏AUROC（有定义家族）|pooled TP/FP/TN/FN|","|---|---|---|---|---|---|"]
    for name,a in result["analyses"].items():
        for score,res in a.items():
            ma=res["macro"];m=res["pooled_raw_score_metrics"]
            lines.append(f"|{name}|{score}|{fmt(ma['TPR']['value'])}（{ma['TPR']['defined_families']}）|{fmt(ma['FPR']['value'])}（{ma['FPR']['defined_families']}）|{fmt(ma['AUROC']['value'])}（{ma['AUROC']['defined_families']}）|{m['TP']}/{m['FP']}/{m['TN']}/{m['FN']}|")
    lines+=["","开发预测是诊断性阈值结果；操作判定覆盖为0的留出家族被标为NEW_FAMILY_UNVALIDATED，不自动记阴性。新family的实验真值尚未取得；减少误报的拒判机制与预测准确率改善是不同端点。","",
    "|target MSA|raw/unique行|非query覆盖≥70%且身份≥30%|非query身份中位数|低复杂度行|BBF Neff80|","|---|---:|---:|---:|---:|---:|"]
    for d in msas:lines.append(f"|{d['target_msa_key']}|{d['raw_rows']}/{d['unique_aligned_sequences']}|{d['nonquery_coverage_ge70_identity_ge30_count']}/{d['nonquery_rows']}|{fmt(d['identity_median'])}|{d['nonquery_low_complexity_count']}|{fmt(d['neff80_full_query_width'])}|")
    lines+=["","MSA身份/覆盖不证明进化同源；公开API未提供数据库快照，全部实际A3M已绑定哈希。BBF是人工靶点，检出MSA序列不应未经检查当作真实同源深度。","",
    "|target|身份n|target pLDDT中位数|对作者预测target RMSD Å|对9HAC实验target RMSD Å|","|---|---:|---:|---:|---:|"]
    for target in sorted({v["target"] for v in result["entries"]}):
        rs=[v for v in result["entries"] if v["target"]==target]
        med=lambda vals:float(np.median(vals)) if vals else None
        author=med([v["target_recovery"]["author_predicted"]["median"] for v in rs if v["target_recovery"]["author_predicted"]["median"] is not None])
        native=med([v["target_recovery"].get("experimental_9HAC",{}).get("median") for v in rs if v["target_recovery"].get("experimental_9HAC",{}).get("median") is not None])
        lines.append(f"|{target}|{len(rs)}|{fmt(med([v['target_plddt']['median'] for v in rs]))}|{fmt(author)}|{fmt(native)}|")
    lines+=["","作者预测target比对只能检验模型一致性；9HAC为BBF结合态实验核心，仍保留状态差异/残基观测覆盖。所有逐模型映射与reference身份在model_features1170.json。","",
    "|target|R0限制项（1170技术模型，不是实验n）|","|---|---|"]
    for target in sorted({v["target"] for v in result["entries"]}):
        c=collections.Counter()
        for v in result["entries"]:
            if v["target"]==target:c.update(v["limiting_component_counts"])
        lines.append(f"|{target}|"+", ".join(f"{k}:{v}" for k,v in sorted(c.items()))+"|")
    lines+=["","结论需以实际逐家族结果评估；提高或降低旧集合分数不构成新家族泛化证明。单体折叠与物理评分不追加硬淘汰门，本CPU步骤没有新增GPU模型。下一阶段冻结新家族、共同target/hotspot、相同实际GPU预算及共同外部评审，再运行RFdiffusion+ProteinMPNN与BindCraft。","",
    "[ipSAE官方实现](https://github.com/DunbrackLab/IPSAE)固定revision6174cf9e71cb1bd660cc805856a18c4871a6dec3；PAE10主、PAE15敏感性。输出distance15为官方距离诊断，主ipSAE不是5 Å接触掩码分数。[BindCraft论文](https://www.nature.com/articles/s41586-025-09429-6)的原生模板/monomer复核与共同no-template multimer复核存在协议差异。","",
    f"真实运行：{run}",f"协议：{STEP/'PROTOCOL.md'}",f"完整数据与manifest：{run/'outputs/screening_transfer.json'}；{run/'manifest.json'}",""]
    return "\n".join(lines)
class Tests(unittest.TestCase):
    def test_missing_ensemble(self):
        self.assertIsNone(summary([1]*14)["median"]);self.assertIsNone(summary([1]*14+[None])["median"]);self.assertEqual(summary([0]*15)["median"],0)
    def test_units_and_zero_pae(self):
        self.assertEqual(components(.9,.8,.8,0)["score"],1)
        with self.assertRaises(ValueError):components(.9,80,.8,8)
        with self.assertRaises(ValueError):components(.9,.8,.8,-1)
        self.assertIsNone(components(.9,.8,None,8)["score"])
    def test_ipsae_swap_and_nulls(self):
        t="Chn1 Chn2 Type ipSAE ipSAE_d0dom\nA B asym .3 .4\nB A asym .8 .9\nA B max .8 .9\n"
        a=parse_ipsae(t);b=parse_ipsae(t,"B","A");self.assertEqual(a["maximum"],b["maximum"]);self.assertEqual(a["minimum"],b["minimum"]);self.assertEqual(a["target_to_binder"],b["binder_to_target"])
        with self.assertRaises(ValueError):parse_ipsae(t.replace(".3 .4","nan .4"))
        with self.assertRaises(ValueError):parse_ipsae("Chn1 Chn2 Type ipSAE\nA B asym .3\nA B max .3\n")
    def test_rigid_rmsd(self):
        x=np.array([[0,0,0],[1,0,0],[0,2,0],[0,0,3]],float);rot=np.array([[0,-1,0],[1,0,0],[0,0,1]],float)
        self.assertLess(fit_rmsd(x,x@rot+2),1e-10)
    def test_alignment_terminal_tag(self):
        a=alignment_map("MABCDEFGH","ABCDEFGHGGHH")
        self.assertEqual(a["mismatches"],0);self.assertEqual(len(a["pairs"]),8)
    def test_training_missing_class_and_single_class_metrics(self):
        r=[dict(id="a",family="F",positive=True,R1=.8)]
        self.assertIsNone(fit_threshold(r,"R1")["threshold"]);self.assertIsNone(metrics(r,"R1")["AUROC"])
    def test_test_leakage_and_family_reweighting(self):
        tr=[dict(id=f"{f}{i}",family=f,positive=y,R1=s) for f in ["A","B"] for i,(y,s) in enumerate([(True,.9),(False,.1)])]
        before=fit_threshold(tr,"R1")
        te=dict(id="test",family="C",positive=True,R1=.2)
        deployment_decision(te,before,{"A","B"},"R1");te.update(positive=False,R1=.99)
        deployment_decision(te,before,{"A","B"},"R1");self.assertEqual(before,fit_threshold(tr,"R1"))
        dup=tr+[dict(v,id=v["id"]+"x") for v in tr if v["family"]=="A"]
        self.assertEqual(before["threshold"],fit_threshold(dup,"R1")["threshold"])
    def test_new_family_abstain(self):
        fit=dict(threshold=.5,support=dict(small_sample_reasons=[]))
        d=deployment_decision(dict(family="NEW",R1=.99),fit,{"OLD"},"R1");self.assertIsNone(d["prediction"]);self.assertIn("NEW_FAMILY_UNVALIDATED",d["reasons"])
    def test_technical_replicates_not_label_n(self):
        r=dict(id="only",family="A",positive=True,R1=summary([.9]*15)["median"])
        self.assertEqual(metrics([r],"R1")["n_eligible"],1)
    def test_threshold_constrains_each_negative_family(self):
        rs=[dict(id="a",family="A",positive=False,R1=.8),dict(id="b",family="B",positive=False,R1=.1),dict(id="c",family="A",positive=True,R1=.9),dict(id="d",family="B",positive=True,R1=.7)]
        f=fit_threshold(rs,"R1")
        self.assertTrue(all(v["FPR"] is None or v["FPR"]<=.2 for v in f["training_by_family"].values()))
def run_tests():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests);runner=unittest.TextTestRunner(verbosity=2);res=runner.run(suite)
    if not res.wasSuccessful():raise RuntimeError("Meaningful tests failed")
    return dict(status="MEANINGFUL_SCREENING_TESTS_PASSED",tests_run=res.testsRun,failures=len(res.failures),errors=len(res.errors),leakage_nulls_units_symmetry_and_training_only=True)
def validate(manifest_path):
    man=read(manifest_path)
    for v in [man["preparation"],man["source"],man["protocol"]]+man["inputs"]+man["author_reference_files"]+man["official_output_files"]+man["outputs"]:verify(v)
    outs={Path(v["path"]).name:read(v["path"]) for v in man["outputs"] if v["path"].endswith(".json")}
    data=outs["screening_transfer.json"];models=outs["model_features1170.json"]["rows"]
    assert len(data["entries"])==78 and len(models)==1170 and data["counts"]["complete_R0"]==data["counts"]["complete_R1"]==78
    assert len({(v["id"],v["model"],v["seed"]) for v in models})==1170
    for e in data["entries"]:
        rows=[v for v in models if v["id"]==e["id"]];assert {(v["model"],v["seed"]) for v in rows}==EXPECTED
        assert e["R0"]==float(np.median([v["R0"] for v in rows])) and e["R1"]==float(np.median([v["ipsae"]["10"]["maximum"] for v in rows]))
        assert e["blockade_eligible"] is False
    for name,analyses in data["analyses"].items():
        expected=32 if name=="main" else 67
        for score,res in analyses.items():
            assert res["pooled_raw_score_metrics"]["n_eligible"]==expected
            assert res["operational_pooled_metrics"]["n_predicted"]==0
            for fold in res["folds"]:
                assert not set(fold["fit"]["training_ids"])&{v["id"] for v in fold["rows"]}
                assert all("NEW_FAMILY_UNVALIDATED" in v["abstention_reasons"] and v["operational_prediction"] is None for v in fold["rows"])
                assert all(v["FPR"] is None or v["FPR"]<=.2+1e-12 for v in fold["fit"].get("training_by_family",{}).values())
    tests=run_tests()
    acceptance=dict(status="ALL78_1170_SCREENING_IMPROVEMENT_CONTENT_ACCEPTED_DEVELOPMENT_ONLY",job_id=os.environ["SLURM_JOB_ID"],created_utc=now(),manifest=rec(manifest_path),counts=data["counts"],tests=tests,verified_official_files=len(man["official_output_files"]),source=rec(__file__),report=next(v for v in man["outputs"] if v["path"].endswith("REPORT.md")),scientific_scope="DEVELOPMENT_DIAGNOSTICS_AND_EXPLICIT_NEW_FAMILY_ABSTENTION_NO_EXPERIMENTAL_SUCCESS_PROBABILITY",all_original_model_receipts_retained=True)
    dump(STEP/"acceptance.json",acceptance);print(json.dumps(acceptance,indent=2),flush=True)
def main():
    p=argparse.ArgumentParser();p.add_argument("command",choices=["test","run","validate"]);p.add_argument("input",nargs="?");a=p.parse_args()
    if a.command=="test":print(json.dumps(run_tests(),indent=2))
    elif a.command=="run":run(a.input)
    else:
        v=a.input or read(STEP/"run_pointer.json")["manifest"]["path"];validate(v)
if __name__=="__main__":main()

