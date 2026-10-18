import os,json,shutil
from pathlib import Path
from ppiblocker.common import *
R=Path("/lustre/users/u21111210118/projects/test9")
src=R/"source/benchmarks/computational_strengthening_20260923";src.mkdir(exist_ok=True)
run=Run(R,"79_strengthening_setup",[])
old=R/"steps/73_af2_review_setup/runs/20260923T092849Z_a3695ac8dc12/manifest.json"
om=read_json(old);op=read_json(verify_file(om["outputs"]["plan"]))
cm=R/"steps/60_af2_control_inputs/runs/20260922T111813Z_0f6bf85d0301/manifest.json"
c=read_json(cm);cs=read_json(verify_file(c["outputs"]["plan"]))["entries"];ms=read_json(verify_file(c["outputs"]["inputs"]))
baseline={}
for p in (R/"steps/61_af2_calibration/runs").glob("*/manifest.json"):
 m=read_json(p)
 if m["status"]=="AF2_VERIFICATION_COMPLETE":
  for x in read_json(verify_file(m["outputs"]["results"])):baseline[x["id"]]=x["models"]
prior={e["id"]:e for e in op["entries"] if e["role"]=="control"}
allentries=[];pending=[]
for e in cs:
 e.update(role="control",positive=str(e["label"]).lower() in ("true","1"),msa=ms[e["id"]],baseline_models=baseline[e["id"]],family="Ig_like" if e["target"] in ("IL7Ra","Pdl1") else e["target"],construct_caveat="author core sequence; assay tags/context incompletely resolved")
 allentries.append(e)
 if e["id"] not in prior:e["slot"]=len(pending);pending.append(e)
require(len(pending)==68,"MISSING_COUNT",str(len(pending)))
protocol=read_json(verify_file(op["protocol"]))
protocol.update(id="COMPUTATIONAL-STRENGTHENING-20260923",scope="All six computational workstreams plus bounded replicated MD; no experimental claims",selection="All78 public controls plus all3 KEAP1 candidates; reuse exact matched prior runs",
calibration=dict(groups="4 conservative target families; IL7Ra and Pdl1 together",outer="leave-one-family-out",metrics=["FPR","TPR","balanced_accuracy","AUROC","topK_precision"],threshold="training-only choose max sensitivity subject to empirical FPR<=0.20; missing stays failure; no prospective PPV",models="15 predictions aggregate per sequence, not independent samples"),
extensions=dict(monomer="all78 controls plus3 candidates; 5weights 3seeds single sequence 12recycles",physics="3 fixed seeds, model1 seed1042 start; constrained FastRelax max_iter200; ref2015; separated repacking; all81",ablation="native peptide + motif alanine, nonmotif contact alanine, two motif-preserving flank shuffles and one full shuffle per candidate; fiveweights threeseeds; synthetic controls unlabeled",specificity="KLHL3 and KLHL12 Kelch constructs, on-target matched single-sequence arm, full-length KEAP1, binder homodimers",context="fetch2FLU,1X2R,2DYH,3WN7 assemblies; sequence-mapped projection and uncertainty; full-length AF model context diagnostic",MD="bb145 and bb1144 and native complex; three fixed replicas each; CPU implicit solvent Amber14/GBn2,300K,2fs,100ps equilibration+1ns production; diagnostic not affinity/convergence evidence"),
promotion="No automatic experimental or superiority claims. Gates diagnostic until held-out qualified evaluation.")
pp=src/"protocol.json";atomic_json(pp,protocol)
p=run.path/"outputs/plan.json";atomic_json(p,dict(entries=pending,all_controls=allentries,candidates=[e for e in op["entries"] if e["role"]=="candidate"],protocol=record_file(pp),prior_setup=record_file(old)))
run.output("plan",p);run.output("ipsae_source",verify_file(om["outputs"]["ipsae_source"]))
for name in ("predict.py","score.py"):
 s=(R/"source/benchmarks/af2_review_20260923"/name).read_text()
 s=s.replace('73_af2_review_setup','79_strengthening_setup').replace('74_af2_review_predict','80_strengthening_predict').replace('75_af2_review_score','81_strengthening_score').replace('"AF2_REVIEW_INPUTS_READY"','"STRENGTHENING_INPUTS_READY"')
 (src/name).write_text(s)
for name in ("predict.sbatch","score.sbatch"):
 s=(R/"source/benchmarks/af2_review_20260923"/name).read_text().replace("benchmarks/af2_review_20260923/","benchmarks/computational_strengthening_20260923/")
 (src/name).write_text(s)
run.manifest["inputs"]=[record_file(old),record_file(cm),record_file(pp)];run.save()
print(run.finish("STRENGTHENING_INPUTS_READY","protocol_frozen",dict(controls=78,new_controls=68,candidates=3)),flush=True)

