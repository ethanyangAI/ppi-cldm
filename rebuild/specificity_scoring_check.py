import os,json,importlib.util,hashlib
from pathlib import Path
import numpy as np
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/15_specificity_review"
spec=importlib.util.spec_from_file_location("review_analysis",S/"code/analyze.py");mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
plan=json.loads((S/"plan.json").read_text());t=next(t for t in plan["targets"] if t["target"]=="KEAP1");ann=mod.construct_annotation(t)
e=next(e for e in plan["conditions"] if e["target"]=="KEAP1" and e["analysis_track"]=="sensitivity_observed_construct")
n=len(e["target_sequence"]);b=len(e["sequence"]);pae=np.ones((n+b,n+b));pae[:n,n:]=3;pae[n:,:n]=7
work=S/"runs"/("scientific_unitchecks_"+os.environ["SLURM_JOB_ID"]);work.mkdir()
score=work/"synthetic_scores.json";score.write_text(json.dumps({"pae":pae.tolist(),"plddt":[90]*(n+b),"iptm":.9,"ptm":.9}))
m={"model":0,"seed":0,"pdb":t["native_pdb"],"scores":mod.rec(score)}
row=mod.score_model(e,m,t,ann)
assert row["geometry"]["ligand_CA_RMSD_after_target_alignment_A"]<1e-5
assert row["geometry"]["native_contact_recall"]==1
assert row["confidence"]["pae_target_rows_ligand_columns_at_contacts"]["mean"]==3
assert row["confidence"]["pae_ligand_rows_target_columns_at_contacts"]["mean"]==7
assert row["confidence"]["bidirectional_contact_pae"]["mean"]==5
assert row["native_control_recovery_pass"] and row["baseline_confidence_pass"]
assert row["coverage"]["query_target_length"]==285 and row["coverage"]["target_observed_fraction_of_query"]==1
# Explicit position mapping retains observed residues across internal gaps.
for target in plan["targets"]:
 ref,_=mod.read_structure(mod.verify(target["native_pdb"]))
 mapping=target["construct_mapping"][0];pos=mapping["observed_to_declared_positions"];by={p:i for i,p in enumerate(pos)}
 artificial={**ref[0],"sequence":mapping["declared_sequence"]}
 for field in ("residues","heavy","atoms"):artificial[field]=[ref[0][field][by[p]] if p in by else ref[0][field][0] for p in range(1,mapping["declared_length"]+1)]
 projected=mod.subset(artificial,pos);assert projected["sequence"]==ref[0]["sequence"];assert np.array_equal(mod.ca(projected),mod.ca(ref[0]))
 tag=mod.construct_annotation(target)
 print("CONSTRUCT",target["target"],json.dumps(tag),flush=True)
receipt={"status":"SPECIFICITY_SCORING_SCIENTIFIC_CHECKS_PASSED","job":os.environ["SLURM_JOB_ID"],"checks":["native self-pose near-zero RMSD and perfect contact recall","directional PAE 3A/7A retained separately with exact 5A pooled mean","native recovery gate and observed coverage denominator","all three declared-to-observed explicit mappings preserve coordinates including KLHL12 internal gap"],"synthetic_test_only":True,"model_inputs_modified":False,"analysis_code":mod.rec(S/"code/analyze.py")}
mod.dump(work/"receipt.json",receipt);print(json.dumps(receipt,indent=2))

