#!/usr/bin/env python3
"""Separated computational evidence axes, not validated binding or blockade."""
import json,os,shutil,subprocess,sys,unittest
from pathlib import Path
import numpy as np
from scipy.spatial.distance import cdist
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from pose_reassessment import receipt,verify,atomic_json,read_model,aligned,rmsd
ROOT=Path("/lustre/users/u21111210118/projects/test9")
def checked(rec):
    verify(rec);return json.loads(Path(rec["path"]).read_text())
def find_receipt(obj,suffix):
    found={}
    def walk(x):
        if isinstance(x,dict):
            if isinstance(x.get("path"),str) and x["path"].endswith(suffix) and "sha256" in x:found[x["path"]]=x
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(obj)
    if len(found)!=1:raise ValueError(f"Ambiguous/missing receipt {suffix}: {len(found)}")
    return next(iter(found.values()))
def stats(xs):
    v=[float(x) for x in xs if x is not None]
    if not all(np.isfinite(v)):raise ValueError("Nonfinite aggregation")
    return dict(n=len(v),missing=len(xs)-len(v),median=float(np.median(v)) if v else None,min=min(v) if v else None,max=max(v) if v else None)
def parse_ipsae(text,a="A",b="B"):
    header=None;rows={}
    for line in text.splitlines():
        p=line.split()
        if not p:continue
        if p[0]=="Chn1":header=p;continue
        if header is None:continue
        if len(p)!=len(header):raise ValueError("Malformed ipSAE")
        row=dict(zip(header,p));key=(row["Chn1"],row["Chn2"])
        if row["Type"]!="asym" or key not in ((a,b),(b,a)):continue
        if key in rows:raise ValueError("Duplicate direction")
        val=float(row["ipSAE"])
        if not np.isfinite(val) or not 0<=val<=1:raise ValueError("Invalid ipSAE")
        rows[key]=(val,row)
    if set(rows)!={(a,b),(b,a)}:raise ValueError("Missing direction")
    return dict(target_to_binder=rows[(a,b)][0],binder_to_target=rows[(b,a)][0],
        minimum=min(v[0] for v in rows.values()),directional_rows=[rows[(a,b)][1],rows[(b,a)][1]])
def heavy(chain):
    xyz=[];indices=[]
    for i,r in enumerate(chain.get_residues()):
        for a in r.get_atoms():
            if a.element not in ("H","D"):xyz.append(a.coord);indices.append(i)
    return np.asarray(xyz,float),np.asarray(indices,int)
def contacts(chains):
    a,ia=heavy(chains[0]);b,ib=heavy(chains[1]);d=cdist(a,b);x,y=np.nonzero(d<=5)
    pairs=np.unique(np.column_stack((ia[x],ib[y])),axis=0)
    return a,b,d,pairs
def axes(m,native):
    n=len(m["coords"][0]);a,b,d,pairs=contacts(m["chains"])
    f=dict(global_iptm=float(m["score"]["iptm"]),binder_plddt=float(m["plddt"][n:].mean()/100),
        target_plddt=float(m["plddt"][:n].mean()/100),heavy_atom_contacts_5A=int((d<=5).sum()),
        heavy_atom_pairs_lt2A=int((d<2).sum()),minimum_heavy_atom_distance_A=float(d.min()),
        residue_contacts_5A=len(pairs),original_design_backbone_rmsd_A=None,
        original_design_backbone_status="NOT_ESTIMABLE_LOST_ORIGINAL_BACKBONE")
    keys=("interface_plddt","contact_pae_target_to_binder_A","contact_pae_binder_to_target_A",
          "contact_pae_bidirectional_mean_A","confidence_baseline_margin","confidence_baseline_pass")
    f.update({k:None for k in keys})
    if len(pairs):
        ta,bi=pairs[:,0],pairs[:,1]+n
        f["interface_plddt"]=float(m["plddt"][np.unique(np.r_[ta,bi])].mean()/100)
        f["contact_pae_target_to_binder_A"]=float(m["pae"][ta,bi].mean())
        f["contact_pae_binder_to_target_A"]=float(m["pae"][bi,ta].mean())
        f["contact_pae_bidirectional_mean_A"]=float(np.r_[m["pae"][ta,bi],m["pae"][bi,ta]].mean())
        # PAE component capped at 4, above maximal ipTM/.75: no score rank change.
        f["confidence_baseline_margin"]=min(f["global_iptm"]/.75,f["binder_plddt"]/.8,
            f["interface_plddt"]/.8,8/max(2,f["contact_pae_bidirectional_mean_A"]))
        f["confidence_baseline_pass"]=f["confidence_baseline_margin"]>=1
    na,nb,nd,npairs=contacts(native)
    nca=np.asarray([r["CA"].coord for r in native[0].get_residues()])
    if len(nca)!=n:raise ValueError("Incomplete native target correspondence")
    mapped=aligned(b,m["coords"][0],nca);ov=cdist(mapped,nb)<2
    nat=set(map(int,npairs[:,0]));pred=set(map(int,pairs[:,0]));inter=nat&pred
    f["competition_geometry"]=dict(
        reference_target_ca_alignment_rmsd_A=rmsd(aligned(m["coords"][0],m["coords"][0],nca),nca),
        native_target_epitope_n=len(nat),candidate_target_epitope_n=len(pred),shared_target_epitope_n=len(inter),
        native_epitope_coverage=len(inter)/len(nat) if nat else None,
        candidate_epitope_overlap_fraction=len(inter)/len(pred) if pred else None,
        shared_target_sequence_positions=sorted(i+1 for i in inter),
        candidate_atoms_with_native_partner_overlap_lt2A=int(ov.any(axis=1).sum()),
        native_partner_atoms_with_candidate_overlap_lt2A=int(ov.any(axis=0).sum()),
        overlapping_atom_pairs_lt2A=int(ov.sum()),
        interpretation="Rigid static overlap, not experimental competition or blockade")
    return f
def physics_accept(manifest,out):
    old=checked(manifest["existing_physics"]);op=checked(old["plan"])
    new=checked(manifest["remaining_physics_plan"])
    expected={(e["identity"],e["seed"]):(e,old["plan"],op) for e in op["entries"]}
    for e in new["entries"]:
        key=(e["identity"],e["seed"])
        if key in expected:raise ValueError("Duplicate physics plan")
        expected[key]=(e,manifest["remaining_physics_plan"],new)
    recs=list(old["results"])+[receipt(Path(manifest["run"])/"outputs/minor_physics"/f"task_{i}"/"result.json") for i in range(len(new["entries"]))]
    seen=set();results=[];keys=("dG_separated","dSASA","shape_complementarity","packstat","hbond_count","buried_unsatisfied")
    for rec in recs:
        r=checked(rec);key=(r["identity"],r["seed"]);e,p,plan=expected[key]
        if key in seen:raise ValueError("Duplicate physics result")
        seen.add(key)
        if r["input"]!=e["input"] or r["plan"]!=p or r["sequences"]!=e["sequences"]:raise ValueError("Physics inputs mismatch")
        if r["environment_freeze"]!=plan["environment_freeze"]:raise ValueError("Physics environment drift")
        for rr in (r["input"],r["plan"],r["environment_freeze"],r["relaxed_pdb"]):verify(rr)
        if r["scorefunction"]!="ref2015" or r["fastrelax_repeats"]!=1 or r["max_iter"]!=200:raise ValueError("Physics parameters mismatch")
        if not all(np.isfinite(float(r[k])) for k in keys):raise ValueError("Nonfinite physics")
        model=next(PDBParser(QUIET=True).get_structure("r",r["relaxed_pdb"]["path"]).get_models())
        seqs=["".join(seq1(res.resname) for res in c.get_residues() if res.id[0]==" ") for c in model.get_chains()]
        if seqs!=e["sequences"]:raise ValueError("Relaxed sequence mismatch")
        r["dG_per_area_x100"]=100*r["dG_separated"]/r["dSASA"] if r["dSASA"]>0 else None
        r["area_ratio_status"]="ESTIMABLE" if r["dSASA"]>0 else "NOT_ESTIMABLE_ZERO_AREA"
        results.append(r)
    if seen!=set(expected) or len(seen)!=24:raise ValueError("Incomplete physics coverage")
    summaries=[]
    for ident in sorted(set(r["identity"] for r in results)):
        rs=[r for r in results if r["identity"]==ident]
        if sorted(r["seed"] for r in rs)!=[1042,1043,1044]:raise ValueError("Missing physics seed")
        summaries.append(dict(identity=ident,n_seeds=3,**{k:stats([r[k] for r in rs]) for k in keys+("dG_per_area_x100",)}))
    result=dict(status="ALL_24_PHYSICS_RESULTS_VERIFIED",candidate_representatives=5,native_controls=3,results=recs,summary=summaries,
        scope="Rosetta energy units and technical diagnostics; not affinity or validation")
    atomic_json(out/"physics_acceptance.json",result);return result
def execute():
    setup=json.loads((ROOT/"steps/16_screening_evidence/setup_receipt.json").read_text());manifest=checked(setup["manifest"])
    for v in manifest.values():
        if isinstance(v,dict) and "sha256" in v:verify(v)
    run=Path(manifest["run"])/f"axes_{os.environ.get('SLURM_JOB_ID','manual')}"
    out=run/"outputs";out.mkdir(parents=True,exist_ok=True)
    src=checked(manifest["ipsae_source"]);script=src["files"]["ipsae.py"];verify(script)
    acceptance=checked(manifest["af2_acceptance"]);pm=checked(manifest["pose_manifest"])
    pose_ref=find_receipt(pm,"/outputs/pose_reassessment.json");pose=checked(pose_ref)
    ph=checked(manifest["existing_physics"]);pp=checked(ph["plan"])
    ne=next(e for e in pp["entries"] if e["identity"]=="native_2FLU");verify(ne["input"])
    native=list(next(PDBParser(QUIET=True).get_structure("n",ne["input"]["path"]).get_models()).get_chains())
    if ["".join(seq1(r.resname) for r in c.get_residues()) for c in native]!=ne["sequences"]:raise ValueError("Native sequence mismatch")
    byid={c["candidate"]:c for c in pose["candidates"]};records=[];summary=[]
    for entry in acceptance["accepted_entries"]:
        if entry["mode"]!="complex":continue
        cand=entry["id"];c=byid[cand]
        if c["target_sequence"]!=ne["sequences"][0]:raise ValueError("Native target mapping mismatch")
        groups=c["clusters_by_cutoff_A"]["2"]
        for rec in sorted(entry["models"],key=lambda x:(x["model"],x["seed"])):
            m=read_model(rec,[c["target_sequence"],c["binder_sequence"]]);g=next(g for g in groups if m["id"] in g["members"])
            directory=run/"ipsae"/cand/m["id"];directory.mkdir(parents=True,exist_ok=True)
            pdb=directory/"model.pdb";score=directory/"scores.json"
            shutil.copyfile(m["pdb"]["path"],pdb);shutil.copyfile(m["scores"]["path"],score);iv={}
            for cut in (10,15):
                p=subprocess.run([sys.executable,script["path"],str(score),str(pdb),str(cut),"15"],capture_output=True,text=True)
                (directory/f"ipsae_{cut}.log").write_text(p.stdout+"\n"+p.stderr)
                if p.returncode:raise RuntimeError(p.stderr[-2000:])
                table=directory/f"model_{cut}_15.txt";iv[str(cut)]=parse_ipsae(table.read_text(),m["chains"][0].id,m["chains"][1].id)
                iv[str(cut)]["table"]=receipt(table)
            records.append(dict(candidate=cand,model_id=m["id"],model=m["model"],seed=m["seed"],pdb=m["pdb"],scores=m["scores"],
                cluster_id=g["cluster_id"],cluster_size=g["size"],is_co_major=g["is_co_major"],is_medoid=m["id"]==g["medoid"],
                ipsae=iv,**axes(m,native)))
        rows=[r for r in records if r["candidate"]==cand]
        if len(rows)!=15:raise ValueError("Not all15 models")
        medoids=[]
        for g in groups:
            r=next(r for r in rows if r["model_id"]==g["medoid"])
            medoids.append(dict(cluster_id=g["cluster_id"],size=g["size"],is_co_major=g["is_co_major"],model_id=g["medoid"],
                monomer_support_n=g["monomer_support_n"],monomer_support_denominator=15,
                ipsae10_minimum=r["ipsae"]["10"]["minimum"],confidence_baseline_pass=r["confidence_baseline_pass"],
                competition_geometry=r["competition_geometry"]))
        summary.append(dict(candidate=cand,models=15,metrics={k:stats([r[k] for r in rows]) for k in
            ("global_iptm","binder_plddt","interface_plddt","contact_pae_bidirectional_mean_A","confidence_baseline_margin")},
            ipsae={str(cut):{d:stats([r["ipsae"][str(cut)][d] for r in rows]) for d in ("target_to_binder","binder_to_target","minimum")} for cut in (10,15)},
            confidence_baseline_passing_models=sum(r["confidence_baseline_pass"] is True for r in rows),medoids=medoids))
        print("AXES_ACCEPTED",cand,len(rows),flush=True)
    phy=physics_accept(manifest,out)
    for c in summary:
        for g in c["medoids"]:g["physics"]=next(p for p in phy["summary"] if p["identity"]==c["candidate"]+"_"+g["cluster_id"])
    if len(records)!=45 or sum(len(c["medoids"]) for c in summary)!=5:raise ValueError("Coverage mismatch")
    obj=dict(id="PPI-EVIDENCE-REPAIR-20261002",version="2.0.1",status="SEPARATE_AXES_COMPUTED_NOT_VALIDATED_BLOCKADE",
        protocol=manifest["protocol"],metric_semantics_correction="Protocol2.0 pair_iptm means AF2 global ipTM. Threshold .75 unchanged; no directional AF2 ipTM claimed.",
        experimental_unit="3 sequences;45 models and relaxation seeds are technical replicates",records=records,summary=summary,
        physics=receipt(out/"physics_acceptance.json"),no_joint_fold_physics_rejection=True,blockade_evidence="NOT_MEASURED",
        original_design_backbone="NOT_RECOVERED",sources=[setup["manifest"],manifest["af2_acceptance"],pose_ref,manifest["primary_medoids"],script,ne["input"]])
    atomic_json(out/"evidence_axes.json",obj)
    report=["# 三候选分轴证据复核 v2.0.1\n",
      "统计单位为3条候选序列；45个复合物、45个单体模型及Rosetta种子均为技术重复。旧设计原始backbone丢失，无法计算设计保持RMSD。",
      "协议2.0的pair_iptm字段明确为AF2双链复合物global ipTM，阈值不变。ipSAE保留两方向及较小值；单体折叠与物理评分没有追加为淘汰门。没有实验结合/阻断/亲和力结论。",
      "\n|候选|global ipTM中位数|ipSAE10较小方向中位数|置信度通过模型|簇大小|各簇单体支持|\n|---|---:|---:|---:|---|---|"]
    for c in summary:
        report.append(f"|{c['candidate']}|{c['metrics']['global_iptm']['median']:.3f}|{c['ipsae']['10']['minimum']['median']:.3f}|{c['confidence_baseline_passing_models']}/15|"+"/".join(str(g["size"]) for g in c["medoids"])+"|"+", ".join(f"{g['cluster_id']}:{g['monomer_support_n']}/15" for g in c["medoids"])+"|")
    report+=["\n|候选/构象|占比|dG(REU)中位数|dSASA(Å²)中位数|SC中位数|埋藏未满足极性数中位数|天然靶位点覆盖|\n|---|---:|---:|---:|---:|---:|---:|"]
    for c in summary:
        for g in c["medoids"]:
            p=g["physics"];geo=g["competition_geometry"]
            report.append(f"|{c['candidate']}/{g['cluster_id']}|{g['size']}/15|{p['dG_separated']['median']:.2f}|{p['dSASA']['median']:.1f}|{p['shape_complementarity']['median']:.3f}|{p['buried_unsatisfied']['median']:.0f}|{geo['native_epitope_coverage']:.3f}|")
    report+=["\n全部5个候选构象与3个天然对照各3种子，共24个物理计算验收；零面积时归一能量为null。不同长度/面积/构建的REU不能直接比较亲和力。",
      "几何重叠分别记录候选原子与天然配体原子的覆盖数，避免旧字段计数方向混淆。刚性位点重叠不是实验竞争。",
      "ipSAE固定[作者实现](https://github.com/DunbrackLab/IPSAE) revision "+src["revision"]+"；PAE10主分析、PAE15敏感性、距离15Å。"]
    (out/"REPORT.md").write_text("\n".join(report)+"\n")
    final=dict(status=obj["status"],run=str(run),script=receipt(__file__),inputs=obj["sources"],summary=summary,
        outputs=[receipt(p) for p in sorted(run.rglob("*")) if p.is_file()])
    atomic_json(run/"manifest.json",final)
    atomic_json(ROOT/"steps/16_screening_evidence/acceptance.json",dict(status="ALL_45_MODELS_AND_24_PHYSICS_RESULTS_VERIFIED",
        manifest=receipt(run/"manifest.json"),axes=receipt(out/"evidence_axes.json"),report=receipt(out/"REPORT.md")))
    print("ACCEPTED",str(run),flush=True)
class Regression(unittest.TestCase):
    def test_directional_min_and_zero(self):
        self.assertEqual(parse_ipsae("Chn1 Chn2 Type ipSAE\nA B asym 0\nB A asym .9\nA B max .9\n")["minimum"],0)
    def test_missing_direction(self):
        with self.assertRaises(ValueError):parse_ipsae("Chn1 Chn2 Type ipSAE\nA B asym .9\nA B max .9\n")
    def test_nonfinite(self):
        with self.assertRaises(ValueError):parse_ipsae("Chn1 Chn2 Type ipSAE\nA B asym nan\nB A asym .9\n")
    def test_missing_not_negative(self):
        s=stats([None,.4]);self.assertEqual(s["median"],.4);self.assertEqual(s["missing"],1)
if __name__=="__main__":
    if "--test" in sys.argv:unittest.main(argv=[sys.argv[0]])
    else:execute()

