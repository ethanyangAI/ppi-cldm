"""Independent CPU read-back of all specificity artifacts and key numerical estimands."""
import os,json,hashlib
from pathlib import Path
import numpy as np
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from scipy.spatial import cKDTree
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/15_specificity_review";D=S/"outputs/analysis_11863"
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(row):
 p=Path(row["path"]);assert p.is_file() and digest(p)==row["sha256"],str(p);return p
def chains(p):
 st=PDBParser(QUIET=True).get_structure("x",p);result=[]
 for c in next(st.get_models()):
  rs=[r for r in c if "CA" in r and r.id[0]==" "]
  result.append({"seq":"".join(seq1(r.resname) for r in rs),"ca":np.array([r["CA"].coord for r in rs],float),"heavy":[np.array([a.coord for a in r if a.element not in ("H","D")],float) for r in rs]})
 return result
def pairs(a,b):
 xa=np.concatenate(a["heavy"]);xb=np.concatenate(b["heavy"])
 ia=np.repeat(np.arange(len(a["heavy"])),[len(x) for x in a["heavy"]]);ib=np.repeat(np.arange(len(b["heavy"])),[len(x) for x in b["heavy"]])
 return {(int(ia[i])+1,int(ib[j])+1) for i,js in enumerate(cKDTree(xa).query_ball_tree(cKDTree(xb),5.0)) for j in js}
def projected(chain,positions):
 ix=[p-1 for p in positions]
 return {"seq":"".join(chain["seq"][i] for i in ix),"ca":chain["ca"][ix],"heavy":[chain["heavy"][i] for i in ix]}
def rmsd_aligned_target(a,b,ra,rb):
 x=a["ca"]-a["ca"].mean(0);y=ra["ca"]-ra["ca"].mean(0);u,_,vh=np.linalg.svd(x.T@y);rot=u@vh
 if np.linalg.det(rot)<0:u[:,-1]*=-1;rot=u@vh
 shifted=(b["ca"]-a["ca"].mean(0))@rot+ra["ca"].mean(0)
 return float(np.sqrt(np.mean(np.sum((shifted-rb["ca"])**2,axis=1))))
acc=json.loads((S/"outputs/acceptance_11863.json").read_text());assert acc["status"]=="ALL_225_SPECIFICITY_MODELS_VERIFIED"
plan=json.loads(verify(acc["plan"]).read_text());msa=json.loads(verify(acc["msa_acceptance"]).read_text())
for x in msa["conditions"]:verify(x["input"]);assert x["effective_unpaired_ligand_sequence_count"]==1 and x["effective_unpaired_target_sequence_count"]>1
for x in msa["targets"].values():verify(x["input"])
manifest=json.loads((D/"manifest.json").read_text())
for x in manifest["inputs"]+manifest["outputs"]:verify(x)
models=json.loads((D/"all_model_metrics.json").read_text())["models"];summary=json.loads((D/"summary.json").read_text());assert len(models)==270
targetinfo={t["target"]:t for t in plan["targets"]};refs={g:chains(verify(t["native_pdb"])) for g,t in targetinfo.items()}
ids=set();native_count=0
for row in models:
 key=(row["condition_id"],row["model"],row["seed"]);assert key not in ids;ids.add(key)
 cs=chains(verify(row["pdb"]));scores=json.loads(verify(row["scores"]).read_text());n=len(cs[0]["seq"]);b=len(cs[1]["seq"])
 assert [n,b]==[row["coverage"]["query_target_length"],row["coverage"]["query_ligand_length"]]
 cp=pairs(*cs);assert cp=={tuple(x) for x in row["interface_full_query"]["residue_pairs"]}
 matrix=np.array(scores["pae"]);v1=[matrix[i-1,n+j-1] for i,j in cp];v2=[matrix[n+j-1,i-1] for i,j in cp]
 for values,label in ((v1,"pae_target_rows_ligand_columns_at_contacts"),(v2,"pae_ligand_rows_target_columns_at_contacts"),(v1+v2,"bidirectional_contact_pae")):
  out=row["confidence"][label];assert out["n"]==len(values)
  assert (out["mean"] is None and not values) or (values and abs(out["mean"]-float(np.mean(values)))<1e-9)
 assert row["confidence"]["AF2_global_iptm"]==scores["iptm"]
 if row["role"]=="native":
  native_count+=1;ref=refs[row["target"]];a=projected(cs[0],row["coverage"]["target_mapped_positions"]);bchain=projected(cs[1],row["coverage"]["ligand_mapped_positions"])
  assert a["seq"]==ref[0]["seq"] and bchain["seq"]==ref[1]["seq"]
  npairs=pairs(*ref);predpairs=pairs(a,bchain);inter=len(npairs&predpairs)
  assert row["geometry"]["native_contact_recall_denominator"]==len(npairs) and row["geometry"]["native_contact_recall_numerator"]==inter
  assert abs(row["geometry"]["native_contact_recall"]-inter/len(npairs))<1e-12
  assert abs(row["geometry"]["ligand_CA_RMSD_after_target_alignment_A"]-rmsd_aligned_target(a,bchain,*ref))<1e-5
assert native_count==90
assert len({x[0] for x in ids})==18
for c in summary["conditions"]:
 xs=[r for r in models if r["condition_id"]==c["condition_id"]];assert len(xs)==15
 assert {(x["model"],x["seed"]) for x in xs}=={(m,s) for m in range(1,6) for s in (1042,1043,1044)}
 assert c["baseline_confidence_pass_count"]==sum(x["baseline_confidence_pass"] for x in xs)
 if c["role"]=="native":
  passed=[x for x in xs if x["native_control_recovery_pass"]];assert c["native_control_recovery_count"]==len(passed)
  assert c["native_positive_adequate"]==bool(len(passed)>=8 and len({x["seed"] for x in passed})>=2)
 else:
  control=next(d for d in summary["conditions"] if d["condition_id"]==c["matched_native_condition"]);assert c["matched_native_adequate"]==control["native_positive_adequate"]
report_receipt=json.loads((S/"outputs/report_receipt.json").read_text());verify(report_receipt["report"])
receipt={"status":"SPECIFICITY_REVIEW_INDEPENDENTLY_VERIFIED","job":os.environ["SLURM_JOB_ID"],"new_models_verified":225,"context_models_verified":45,"total_unique_scored_models":270,"condition_count":18,"native_predictions_with_independent_pose_and_contact_recalculation":90,"all_model_contact_pairs_and_bidirectional_PAE_independently_recomputed":270,"all_referenced_files_sha256_verified":True,"report":report_receipt["report"],"summary":{"path":str(D/"summary.json"),"sha256":digest(D/"summary.json")},"scientific_claims":"New computational diagnostic, not experimental specificity or blind generalization."}
p=S/"outputs/independent_acceptance.json"
with p.open("x") as f:json.dump(receipt,f,indent=2);f.write("\n")
print(json.dumps(receipt,indent=2),flush=True)

