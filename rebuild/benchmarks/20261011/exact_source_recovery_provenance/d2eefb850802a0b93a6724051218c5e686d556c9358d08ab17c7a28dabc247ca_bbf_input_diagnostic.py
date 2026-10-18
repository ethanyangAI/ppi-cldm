#!/usr/bin/env python3
"""BBF development input diagnosis. CPU planning/scoring, GPU only root submission.
Source labels never guide arm/candidate selection; all eleven controls are retained.
"""
import argparse,collections,json,math,os,subprocess,sys,time,unittest,tempfile
from pathlib import Path
import numpy as np
from screening_transfer import rec,verify,read,dump,summary,components,parse_ipsae,metrics,REVISION
from benchmark_common_review import allocation,cpu,seqcheck,seqhash,read_structure,interface,geometry
ROOT=Path("/lustre/users/u21111210118/projects/test9")
STEP=ROOT/"steps/23_common_review/bbf_diagnostics"
SETTINGS=dict(schema="BBF_input_diagnostic.v1",scope="DEVELOPMENT_ONLY",engine="ColabDesign_AF2_multimer_v3_inference_without_optimization",models=[1,2,3,4,5],seed=31031,recycles=3,target_MSA="single",binder_MSA="single",use_initial_guess=False,use_initial_atom_pos=False,arms=["single_no_template","single_target_only_9HAG_template"],binder_template_atom_mask_required=0,extra_target_terminal_residue_template_mask_required=0,template_target="EXPERIMENTAL_9HAG_A111",probability=None,operational_pass=None)
def prepare(prepared_path,out):
    cpu();obj=read(prepared_path)
    entry=next(v for v in obj["prepared"] if v["target_id"]=="BBF111_9HAG")
    manifest=read(verify(entry["input_manifest"]));ident=read(verify(manifest["identity_receipt"]));tp=verify(manifest["target_pdb"])
    from screening_transfer import chain_records
    target=chain_records(tp)
    if len(target)!=1 or len(target[0]["sequence"])!=111:raise ValueError("Complete experimental BBF A111 required")
    core=target[0]["sequence"]
    qualification=ROOT/"steps/14_control_qualification/bindcraft18/outputs/qualification_overlay.json"
    eligible=ROOT/"steps/18_qualified_calibration/frozen/eligibility78.json"
    q=read(qualification);entries=[v for v in q["entries"] if v["target"]=="BBF-14"]
    if len(entries)!=11 or len({v["id"] for v in entries})!=11:raise ValueError("All eleven controls required")
    models=ROOT/"steps/20_screening_improvement/runs/20261011T041253Z_12951/outputs/model_features1170.json"
    old=ROOT/"steps/20_screening_improvement/runs/20261011T041253Z_12951/outputs/screening_transfer.json"
    oldscore=read(old)
    if {v["id"] for v in oldscore["entries"] if v["target"]=="BBF-14"}!={v["id"] for v in entries}:raise ValueError("Old all11 identity set mismatch")
    registry_path=ROOT/"steps/23_common_review/inputs/registry7_bridge13010.json"
    registry=read(registry_path);native=next(v for v in registry["targets"] if v["target_id"]=="BBF111_9HAG")
    controls=[];jobs=[]
    for e in sorted(entries,key=lambda v:v["id"]):
        ts=seqcheck(e["target_sequence"]);bs=seqcheck(e["sequence"])
        if seqhash(ts)!=e["target_sequence_sha256"] or seqhash(bs)!=e["sequence_sha256"]:raise ValueError("Full author sequence receipt mismatch")
        if ts==core:mapping={str(i):i for i in range(1,112)}
        elif ts=="M"+core:mapping={str(i+1):i for i in range(1,112)}
        else:raise ValueError("Undeclared BBF query/terminal context")
        if int(e["primary_trace"]["all_primary_fields"]["Length"])!=len(bs):raise ValueError("Full binder length differs from author CSV")
        controls.append(dict(id=e["id"],source_id=e["source_id"],target_sequence=ts,binder_sequence=bs,target_sequence_sha256=seqhash(ts),binder_sequence_sha256=seqhash(bs),target_query_to_template_indices=mapping,positive=bool(e["binary_binding_label"]),source_csv_row=e["source_csv_row"],source_row_sha256=e["source_row_sha256"],conditioned_endpoint="published author SPR label; not intrinsic full assayed construct affinity",target_terminal_context="initial M present in query but absent from experimental coordinates" if len(ts)==112 else "111 experimental core"))
        for arm in SETTINGS["arms"]:
            jobs.append(dict(job_key=e["id"]+"_"+arm,control_id=e["id"],arm=arm,target_sequence=ts,binder_sequence=bs,target_query_to_template_indices=mapping,target_template_pdb=rec(tp),target_template_enabled=arm=="single_target_only_9HAG_template",binder_template_enabled=False,slots=[dict(seed=31031,model=i) for i in range(1,6)]))
    result=dict(status="ALL11_TWO_INPUT_ARMS_PREPARED_PENDING_ACTUAL_FEATURE_VALIDATION",settings=SETTINGS,source=rec(__file__),common_score_source=rec(Path(__file__).resolve().parent/"benchmark_common_review.py"),inputs=dict(prepared=rec(prepared_path),input_manifest=entry["input_manifest"],qualification=rec(qualification),eligibility=rec(eligible),old_model_features=rec(models),old_score_summary=rec(old),old_acceptance=rec(ROOT/"steps/20_screening_improvement/acceptance.json")),template_target=rec(tp),reference_complex=manifest["reference_complex"],native_partner_sequence=native["native_partner_sequence"],native_partner_query_to_reference_indices=native["native_partner_query_to_reference_indices"],native_partner_scope=native["native_partner_sequence_scope"],native_registry=rec(registry_path),controls=controls,jobs=jobs,n_controls=11,n_models_new=110,n_positive=sum(v["positive"] for v in controls),n_negative=sum(not v["positive"] for v in controls),old_15_model_protocol="Existing MSA/no-template reference only; different seed/model budget, not symmetric third arm")
    dump(out,result);print(json.dumps(dict(status=result["status"],n_models_new=110,plan=rec(out)),indent=2))
def feature_arrays(job,f):
    data=np.load(verify(f["features"]),allow_pickle=False)
    mask=np.asarray(data[f["mask_key"]],float);pos=np.asarray(data[f["position_key"]],float)
    L=len(job["target_sequence"])+len(job["binder_sequence"]);T=len(job["target_sequence"])
    if mask.ndim==2:mask=mask[None]
    if pos.ndim==3:pos=pos[None]
    if mask.shape!=(1,L,37) or pos.shape!=(1,L,37,3):raise ValueError("Effective forward template array shape")
    if not np.isfinite(mask).all() or not np.isfinite(pos).all() or ((mask!=0)&(mask!=1)).any():raise ValueError("Invalid effective template atom mask/positions")
    query=np.asarray(data[f["query_aatype_key"]])
    order="ARNDCQEGHILKMFPSTWYV"
    if query.shape!=(L,) or not np.issubdtype(query.dtype,np.integer) or ((query<0)|(query>=20)).any():raise ValueError("Actual full query aatype shape/range")
    if "".join(order[int(v)] for v in query)!=job["target_sequence"]+job["binder_sequence"]:raise ValueError("Actual feature full query changed/deleted residues")
    msa=np.asarray(data[f.get("msa_feature_key",f.get("msa_feat_key"))])
    if msa.shape[:2]!=(1,L):raise ValueError("Actual forward single-sequence MSA shape")
    prev=np.asarray(data[f.get("initial_prev_pos_key","prev_pos")],float)
    if prev.shape!=(L,37,3) or not np.isfinite(prev).all() or prev.any():raise ValueError("Initial previous-position guess leaked")
    cbmask=np.asarray(data["template_pseudo_beta_mask"],float);cbpos=np.asarray(data["template_pseudo_beta"],float)
    if cbmask.shape!=(1,L) or cbpos.shape!=(1,L,3) or not np.isfinite(cbmask).all() or not np.isfinite(cbpos).all():raise ValueError("Pseudo-beta template features malformed")
    rawmask=np.asarray(data["batch_all_atom_mask"],float);rawpos=np.asarray(data["batch_all_atom_positions"],float)
    if rawmask.shape!=(L,37) or rawpos.shape!=(L,37,3):raise ValueError("Raw target-only source batch shape")
    mapping={int(k)-1:int(v)-1 for k,v in job["target_query_to_template_indices"].items()}
    absent=[i for i in range(T) if i not in mapping]
    if rawmask[T:].any() or rawpos[T:].any() or cbmask[:,T:].any() or cbpos[:,T:].any():raise ValueError("Binder raw/template pseudo-beta leakage")
    if absent and (rawmask[absent].any() or rawpos[absent].any() or cbmask[:,absent].any() or cbpos[:,absent].any()):raise ValueError("Missing target raw/pseudo-beta leakage")
    if mask[:,T:].any() or pos[:,T:].any():raise ValueError("Binder effective template coordinates/mask leakage")
    if absent and (mask[:,absent].any() or pos[:,absent].any()):raise ValueError("Unobserved target prefix effective template leakage")
    n=int(mask[:,:T].sum())
    if job["target_template_enabled"] and n<=0:raise ValueError("Target-only experimental template missing")
    if not job["target_template_enabled"] and (cbmask.any() or cbpos.any()):raise ValueError("No-template pseudo-beta channel leaked")
    if not job["target_template_enabled"] and n!=0:raise ValueError("No-template effective atom mask contains target")
    if job["target_template_enabled"] and any(not mask[:,i].any() for i in mapping):raise ValueError("Experimental observed target residue template removed")
    return dict(binder_template_atom_mask_count=int(mask[:,T:].sum()),binder_template_coordinate_nonzero_count=int(np.count_nonzero(pos[:,T:])),extra_target_terminal_template_atom_mask_count=int(mask[:,absent].sum()) if absent else 0,observed_target_template_atom_mask_count=n,target_msa_rows=1,binder_msa_rows=1,actual_template_shape=list(mask.shape),actual_query_length=L,initial_prev_pos_nonzero=0)
def validate_features(plan_path,feature_manifest,out):
    cpu();plan=read(plan_path);features=read(feature_manifest)
    if features["plan"]!=rec(plan_path):raise ValueError("Feature/plan mismatch")
    wanted={v["job_key"]:v for v in plan["jobs"]};actual={v["job_key"]:v for v in features["jobs"]}
    if set(wanted)!=set(actual) or len(actual)!=len(features["jobs"]):raise ValueError("Lost/duplicate BBF control/arm feature denominator")
    verify(features["source"])
    checked=[]
    for key,job in wanted.items():
        f=actual[key];actual_stats=feature_arrays(job,f)
        if f["actual_validated_model_slots"]!=job["slots"] or not f["all_models_feature_arrays_identical"]:raise ValueError("Every fixed model actual forward feature proof required")
        if f["initial_guess_enabled"] or f["initial_atom_position_enabled"]:raise ValueError("Initial coordinate leakage")
        if f["exact_target_query"]!=job["target_sequence"] or f["exact_binder_query"]!=job["binder_sequence"]:raise ValueError("Full query changed")
        for name,v in actual_stats.items():
            if name in f and f[name]!=v:raise ValueError("Actual array versus metadata mismatch: "+name)
        checked.append(dict(job_key=key,features=f["features"],actual_array_stats=actual_stats))
    tests=run_tests()
    acceptance=dict(status="BBF110_DEVELOPMENT_ACTUAL_FEATURES_CONTENT_ACCEPTED_READY_FOR_ROOT_GPU",plan=rec(plan_path),features=rec(feature_manifest),settings=SETTINGS,n_models=110,source=rec(__file__),checked_arrays=checked,tests=tests,experimental_validation=False)
    dump(out,acceptance);print(json.dumps(acceptance,indent=2))
def collect(plan_path,raw_root,out):
    cpu();plan=read(plan_path);jobs=[]
    for job in plan["jobs"]:
        wp=Path(raw_root)/job["job_key"]/"worker.json"
        if not wp.exists():jobs.append(dict(job_key=job["job_key"],status="WORKER_MISSING",models=[]));continue
        worker=read(wp)
        if worker["job_key"]!=job["job_key"] or worker["settings"]!=SETTINGS:raise ValueError("GPU worker protocol mismatch")
        allocation_receipt=worker.get("allocation",{})
        if allocation_receipt.get("allocated_gpu_count")!=1:raise ValueError("GPU worker actual scheduler allocation missing/not1")
        expected={tuple(sorted(s.items())) for s in job["slots"]};seen=set();models=[]
        for item in worker["models"]:
            sig=tuple(sorted(item["slot"].items()))
            if sig not in expected or sig in seen:raise ValueError("Unknown/duplicate BBF model slot")
            seen.add(sig)
            if item.get("returncode",0)!=0:models.append(dict(slot=item["slot"],status="PREDICTION_FAILED",reason=item.get("reason")));continue
            pp=Path(item["pdb_path"]);ss=Path(item["scores_path"])
            if not pp.exists() or not ss.exists():models.append(dict(slot=item["slot"],status="RAW_MODEL_FILES_MISSING"));continue
            models.append(dict(slot=item["slot"],status="RAW_MODEL_HASHED_PENDING_CONTENT_SCORE",pdb=rec(pp),scores=rec(ss)))
        jobs.append(dict(job_key=job["job_key"],status=worker.get("status"),worker=rec(wp),models=models))
    result=dict(status="BBF110_RAW_CONTENT_HASHED_PENDING_SCORE",plan=rec(plan_path),settings=SETTINGS,jobs=jobs,n_jobs_expected=22,n_models_expected=110,source=rec(__file__))
    dump(out,result);print(json.dumps(dict(status=result["status"],receipt=rec(out)),indent=2))
def score(plan_path,raw_manifest,out):
    cpu();plan=read(plan_path);raw=read(raw_manifest)
    if raw["plan"]!=rec(plan_path) or raw["settings"]!=SETTINGS:raise ValueError("Raw BBF protocol mismatch")
    wanted={v["job_key"]:v for v in plan["jobs"]};actual={v["job_key"]:v for v in raw["jobs"]}
    if set(actual)-set(wanted):raise ValueError("Unknown BBF raw job")
    directory=Path(out).parent/"ipsae";directory.mkdir(exist_ok=False)
    controls={v["id"]:v for v in plan["controls"]};ref,_=read_structure(verify(plan["reference_complex"]));refa=next(v for v in ref if v["id"]=="A");refb=next(v for v in ref if v["id"]=="B")
    results=[]
    for key,job in wanted.items():
        ctl=controls[job["control_id"]];models=[];r=actual.get(key,{})
        records={tuple(sorted(v["slot"].items())):v for v in r.get("models",[])}
        for slot in job["slots"]:
            try:
                model=records[tuple(sorted(slot.items()))];p=verify(model["pdb"]);s=verify(model["scores"]);conf=read(s);ch,_=read_structure(p)
                a,b=ch
                if len(ch)!=2 or a["id"]!="A" or b["id"]!="B" or a["sequence"]!=ctl["target_sequence"] or b["sequence"]!=ctl["binder_sequence"]:raise ValueError("BBF model chain/full-query mismatch")
                from benchmark_common_review import units
                na=len(a["sequence"]);pp,pae=units(conf["plddt"],conf["pae"],na+len(b["sequence"]),100)
                contacts=interface(a,b,5);pairs=contacts["residue_pairs"]
                ai=sorted({i-1 for i,j in pairs});bi=sorted({na+j-1 for i,j in pairs})
                ip=float(pp[ai+bi].mean()) if pairs else None
                cp=float(np.mean([pae[i-1,na+j-1] for i,j in pairs]+[pae[na+j-1,i-1] for i,j in pairs])) if pairs else None
                cc=components(conf.get("iptm",conf.get("globaliptm")),float(pp[na:].mean()),ip,cp)
                wd=directory/key/(str(slot["seed"])+"_"+str(slot["model"]));wd.mkdir(parents=True)
                os.link(p,wd/"model.pdb");os.link(s,wd/"scores.json");ips={}
                for cut in (10,15):
                    pr=subprocess.run([str(ROOT/"env/core/bin/python"),str(Path(__file__).resolve().parent/"vendor/ipsae.py"),str(wd/"scores.json"),str(wd/"model.pdb"),str(cut),"15"],capture_output=True,text=True)
                    (wd/("ipsae_"+str(cut)+".log")).write_text(pr.stdout+"\n"+pr.stderr)
                    if pr.returncode:raise ValueError("Official ipSAE failed")
                    ips[str(cut)]=parse_ipsae((wd/("model_"+str(cut)+"_15.txt")).read_text(),"A","B")
                mapping={int(k):int(v) for k,v in ctl["target_query_to_template_indices"].items()}
                # Same core sequence in experimental 9HAC bound reference, target mapping validated.
                known=ctl["binder_sequence"]==plan["native_partner_sequence"]
                bindermap={int(k):int(v) for k,v in plan["native_partner_query_to_reference_indices"].items()} if known else None
                geo=geometry(a,b,refa,refb,mapping,known,bindermap)
                models.append(dict(status="VALID" if pairs else "NO_INTERFACE",slot=slot,pdb=model["pdb"],scores=model["scores"],R0=cc["score"],R1=ips["10"]["maximum"] if pairs else None,components=cc,ipsae=ips,global_iptm=float(conf.get("iptm",conf.get("globaliptm"))),binder_plddt_fraction=float(pp[na:].mean()),interface_plddt_fraction=ip,bidirectional_contact_PAE_A=cp,target_plddt_fraction=float(pp[:na].mean()),geometry=geo,official_files=[rec(v) for v in sorted(wd.iterdir())]))
            except (KeyError,FileNotFoundError,ValueError) as error:models.append(dict(status="MODEL_UNRESOLVED",slot=slot,R0=None,R1=None,reason=str(error)))
        results.append(dict(id=ctl["id"],arm=job["arm"],models=models,R0=summary([v["R0"] for v in models],5),R1=summary([v["R1"] for v in models],5),positive=ctl["positive"],operational_pass=None,probability=None))
    oldscore=read(verify(plan["inputs"]["old_score_summary"]))
    oldref=[dict(id=v["id"],positive=v["positive"],scores=v["scores"],protocol="EXISTING15_MSA_NO_TEMPLATE_UNMATCHED_REFERENCE") for v in oldscore["entries"] if v["target"]=="BBF-14"]
    if len(oldref)!=11:raise ValueError("All eleven old reference controls required")
    comparisons={}
    for arm in SETTINGS["arms"]:
        rows=[dict(id=v["id"],family="BBF-development",positive=v["positive"],R0=v["R0"]["median"],R1=v["R1"]["median"]) for v in results if v["arm"]==arm]
        comparisons[arm]={axis:metrics(rows,axis) for axis in ["R0","R1"]}
    result=dict(status="BBF_INPUT_DIAGNOSTIC_SCORED_DEVELOPMENT_ONLY",plan=rec(plan_path),raw=rec(raw_manifest),settings=SETTINGS,results=results,old_reference=oldref,comparisons=comparisons,n_control_arm=22,n_models_expected=110,n_models_valid=sum(m["status"]=="VALID" for v in results for m in v["models"]),old_reference_protocol="15 existing MSA/no-template models, not matched third arm",experimental_success_probability=None)
    dump(out,result)
    lines=["# BBF 输入诊断（开发数据）","","全部11个既有控制，固定2输入臂×5模型×seed31031×3recycles，未重新筛选阳性。target全query保留初始M，实验9HAG111仅用其观测原子作为target模板；binder模板/initial guess为零。已有15模型MSA臂是不同预算参考。","","|control|输入臂|R0 median|R1 median|有效R1/5|","|---|---|---:|---:|---:|"]
    fmt=lambda x:"不可估计" if x is None else f"{x:.3f}"
    for v in results:lines.append(f"|{v['id']}|{v['arm']}|{fmt(v['R0']['median'])}|{fmt(v['R1']['median'])}|{v['R1']['n_valid']}/5|")
    lines += ["","已有15模型参考（未对称匹配seed/模型数，不作为第三输入臂）：","","|control|R0 median|R1 median|有效R1/15|","|---|---:|---:|---:|"]
    for v in oldref:lines.append(f"|{v['id']}|{fmt(v['scores']['R0']['median'])}|{fmt(v['scores']['R1']['median'])}|{v['scores']['R1']['n_valid']}/15|")
    lines += ["","R1为连续分数，不设新家族通用二元门；结构一致性可能受已输入target模板影响。所有11数据为development，既有SPR是作者条件化端点，不能称新验证或workflow优越证明。",""]
    report=Path(out).parent/"REPORT.md";report.write_text("\n".join(lines))
    dump(Path(out).parent/"manifest.json",dict(status=result["status"],source=rec(__file__),inputs=[rec(plan_path),rec(raw_manifest)],outputs=[rec(out),rec(report)]))
def verify_result(path,out):
    cpu();result=read(path);plan=read(verify(result["plan"]));verify(result["raw"])
    expected={(j["control_id"],j["arm"]):j for j in plan["jobs"]}
    actual={(j["id"],j["arm"]):j for j in result["results"]}
    if set(expected)!=set(actual) or len(actual)!=len(result["results"]):raise ValueError("Control/arm denominator mismatch")
    for key,j in expected.items():
        row=actual[key]
        if len(row["models"])!=5 or {tuple(sorted(m["slot"].items())) for m in row["models"]}!={tuple(sorted(s.items())) for s in j["slots"]}:raise ValueError("Fixed five model slots lost")
        if row["operational_pass"] is not None or row["probability"] is not None:raise ValueError("Unsupported transfer/experiment claim")
        for axis in ("R0","R1"):
            if row[axis]!=summary([m[axis] for m in row["models"]],5):raise ValueError("Ensemble denominator/median mismatch")
        for m in row["models"]:
            if m["status"] not in {"VALID","NO_INTERFACE"}:continue
            verify(m["pdb"]);verify(m["scores"])
            for f in m["official_files"]:verify(f)
            cc=m["components"]
            if components(m["global_iptm"],m["binder_plddt_fraction"],m["interface_plddt_fraction"],m["bidirectional_contact_PAE_A"])!=cc:raise ValueError("Raw R0 recomputation mismatch")
            tables={Path(f["path"]).name:f for f in m["official_files"]}
            for cutoff in ("10","15"):
                if parse_ipsae(Path(tables["model_"+cutoff+"_15.txt"]["path"]).read_text(),"A","B")!=m["ipsae"][cutoff]:raise ValueError("Official ipSAE result mismatch")
            if m["R1"]!=(m["ipsae"]["10"]["maximum"] if m["status"]=="VALID" else None):raise ValueError("Wrong no-interface R1")
    acceptance=dict(status="BBF110_DIAGNOSTIC_CONTENT_ACCEPTED_DEVELOPMENT_ONLY",score=rec(path),plan=result["plan"],settings=SETTINGS,n_control_arm=22,n_models_expected=110,n_models_valid=result["n_models_valid"],tests=run_tests(),independent_experimental_validation=False)
    dump(out,acceptance);print(json.dumps(acceptance,indent=2))
def run_tests():
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    if not r.wasSuccessful():raise RuntimeError("BBF meaning tests failed")
    return dict(status="PASSED",n_tests=r.testsRun)
class Tests(unittest.TestCase):
    def fixture(self,mask=None,pos=None,query=None):
        job=dict(target_sequence="MAC",binder_sequence="DEF",target_query_to_template_indices={"2":1,"3":2},target_template_enabled=True)
        order="ARNDCQEGHILKMFPSTWYV";L=6
        if mask is None:mask=np.zeros((1,L,37));mask[:,1:3,:5]=1
        if pos is None:pos=np.zeros((1,L,37,3));pos[:,1:3,:5]=2.
        if query is None:query=np.array([order.index(a) for a in "MACDEF"])
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);path=Path(temp.name)/"features.npz"
        cbmask=np.zeros((1,L));cbpos=np.zeros((1,L,3))
        np.savez(path,mask=mask,pos=pos,aatype=query,msa=np.zeros((1,L,49)),prev_pos=np.zeros((L,37,3)),template_pseudo_beta_mask=cbmask,template_pseudo_beta=cbpos,batch_all_atom_mask=np.zeros((L,37)),batch_all_atom_positions=np.zeros((L,37,3)))
        f=dict(features=rec(path),mask_key="mask",position_key="pos",query_aatype_key="aatype",msa_feature_key="msa")
        return job,f
    def test_actual_arrays_full_query_and_missing_prefix(self):
        j,f=self.fixture();a=feature_arrays(j,f);self.assertEqual(a["observed_target_template_atom_mask_count"],10);self.assertEqual(a["actual_query_length"],6)
        j["target_sequence"]="AC"
        with self.assertRaises(ValueError):feature_arrays(j,f)
    def test_binder_or_missing_prefix_coordinates_rejected(self):
        p=np.zeros((1,6,37,3));p[:,3,0]=3
        j,f=self.fixture(pos=p)
        with self.assertRaises(ValueError):feature_arrays(j,f)
        p=np.zeros((1,6,37,3));p[:,0,0]=3
        j,f=self.fixture(pos=p)
        with self.assertRaises(ValueError):feature_arrays(j,f)
    def test_actual_template_arm_ablation(self):
        j,f=self.fixture();j["target_template_enabled"]=False
        with self.assertRaises(ValueError):feature_arrays(j,f)
        j,f=self.fixture(mask=np.zeros((1,6,37)))
        with self.assertRaises(ValueError):feature_arrays(j,f)
        j["target_template_enabled"]=False;self.assertEqual(feature_arrays(j,f)["observed_target_template_atom_mask_count"],0)
    def test_actual_query_aatype_identity_not_observed_concatenation(self):
        order="ARNDCQEGHILKMFPSTWYV";q=np.array([order.index(a) for a in "MACDFE"])
        j,f=self.fixture(query=q)
        with self.assertRaises(ValueError):feature_arrays(j,f)
    def test_missing_units_and_technical_denominator(self):
        from benchmark_common_review import units
        with self.assertRaises(ValueError):units([.8,90],[[0,2],[1,0]],2,1)
        self.assertIsNone(summary([1,None,1,1,1],5)["median"])
        self.assertIsNone(components(.9,.9,None,None)["score"])
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="command",required=True)
    s=sub.add_parser("prepare");s.add_argument("--prepared",required=True);s.add_argument("--out",required=True)
    s=sub.add_parser("features")
    for name in ["plan","features","out"]:s.add_argument("--"+name,required=True)
    s=sub.add_parser("score")
    for name in ["plan","raw","out"]:s.add_argument("--"+name,required=True)
    s=sub.add_parser("collect")
    for name in ["plan","raw-root","out"]:s.add_argument("--"+name,required=True)
    s=sub.add_parser("verify")
    for name in ["input","out"]:s.add_argument("--"+name,required=True)
    s=sub.add_parser("test");s.add_argument("--out",required=True)
    a=p.parse_args()
    if a.command=="prepare":prepare(a.prepared,a.out)
    elif a.command=="features":validate_features(a.plan,a.features,a.out)
    elif a.command=="score":score(a.plan,a.raw,a.out)
    elif a.command=="collect":collect(a.plan,a.raw_root,a.out)
    elif a.command=="verify":verify_result(a.input,a.out)
    else:cpu();dump(a.out,dict(run_tests(),source=rec(__file__)))
if __name__=="__main__":main()

