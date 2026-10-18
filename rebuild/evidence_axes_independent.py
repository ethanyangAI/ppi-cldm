import os,sys,json,hashlib,copy,importlib.util,datetime
from pathlib import Path
import numpy as np
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from scipy.spatial import cKDTree
R=Path("/lustre/users/u21111210118/projects/test9");S=R/"steps/16_screening_evidence/independent_review";run=S/("run_"+os.environ["SLURM_JOB_ID"]);run.mkdir(parents=True)
verified={}
def rec(p):
 p=Path(p);return {"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size}
def verify(r):
 p=Path(r["path"]);got=rec(p);assert got["sha256"]==r["sha256"],str(p)
 if "bytes" in r:assert got["bytes"]==r["bytes"]
 verified[str(p)]=got;return p
def read(r):return json.loads(verify(r).read_text())
def write(p,x):
 with Path(p).open("x") as f:json.dump(x,f,indent=2,allow_nan=False);f.write("\n")
def structure(p):
 m=list(PDBParser(QUIET=True).get_structure("x",p).get_models());assert len(m)==1
 out=[]
 for c in m[0]:
  rs=list(c);assert all(r.id[0]==" " and "CA" in r for r in rs)
  xyz=[];owners=[]
  for i,r in enumerate(rs):
   for a in r:
    if a.element not in ("H","D"):xyz.append(a.coord);owners.append(i)
  out.append({"id":c.id,"seq":"".join(seq1(r.resname) for r in rs),"ca":np.asarray([r["CA"].coord for r in rs],float),"atoms":np.asarray(xyz,float),"owners":np.asarray(owners)})
 return out
def contacts(a,b):
 neighbors=cKDTree(a["atoms"]).query_ball_tree(cKDTree(b["atoms"]),5.0)
 pairs={(int(a["owners"][i]),int(b["owners"][j])) for i,js in enumerate(neighbors) for j in js}
 return pairs,sum(map(len,neighbors))
def aligned(points,moving,fixed):
 cm=moving.mean(0);cf=fixed.mean(0);u,_,vt=np.linalg.svd((moving-cm).T@(fixed-cf))
 if np.linalg.det(u@vt)<0:u[:,-1]*=-1
 return (points-cm)@(u@vt)+cf
def ip(block,cut):
 result=[]
 for row in block:
  good=row[row<cut];L=max(26,len(good));d=max(1.,1.24*(L-15)**(1/3)-1.8)
  result.append(float(np.mean(1/(1+(good/d)**2))) if len(good) else 0.)
 return max(result)
def near(a,b,tol=1e-8):
 assert abs(float(a)-float(b))<=tol,(a,b)
accp=R/"steps/16_screening_evidence/acceptance.json";acc=json.loads(accp.read_text())
assert acc["status"]=="ALL_45_MODELS_AND_24_PHYSICS_RESULTS_VERIFIED"
manifest=read(acc["manifest"]);axes=read(acc["axes"]);verify(acc["report"]);verify(manifest["script"])
for r in manifest["outputs"]:verify(r)
setup=read(json.loads((R/"steps/16_screening_evidence/setup_receipt.json").read_text())["manifest"])
source=read(setup["ipsae_source"])
for r in source["files"].values():verify(r)
physics=read(axes["physics"]);old=read(setup["existing_physics"]);oldplan=read(old["plan"]);newplan=read(setup["remaining_physics_plan"]);medoids=read(setup["primary_medoids"])
nentry=next(e for e in oldplan["entries"] if e["identity"]=="native_2FLU");native=structure(verify(nentry["input"]));npairs,_=contacts(*native);native_res={i for i,j in npairs}
assert len(axes["records"])==45;identities=set();ips=[];geos=[]
for row in axes["records"]:
 key=(row["candidate"],row["model"],row["seed"]);assert key not in identities;identities.add(key)
 cs=structure(verify(row["pdb"]));score=read(row["scores"]);n=len(cs[0]["seq"]);pae=np.asarray(score["pae"]);plddt=np.asarray(score["plddt"])/100
 assert cs[0]["seq"]==native[0]["seq"] and pae.shape==(len(plddt),len(plddt))
 for cut in (10,15):
  record=row["ipsae"][str(cut)];table=verify(record["table"]);lines=table.read_text().splitlines();header=None;directions={}
  for line in lines:
   p=line.split()
   if not p:continue
   if p[0]=="Chn1":header=p;continue
   if header is None:continue
   d=dict(zip(header,p));assert len(d)==len(header)
   if d["Type"]=="asym":
    assert float(d["PAE"])==cut and float(d["Dist"])==15
    directions[(d["Chn1"],d["Chn2"])]=float(d["ipSAE"])
  assert set(directions)=={("A","B"),("B","A")}
  a=ip(pae[:n,n:],cut);b=ip(pae[n:,:n],cut)
  near(a,directions[("A","B")],5.01e-7);near(b,directions[("B","A")],5.01e-7)
  near(record["target_to_binder"],directions[("A","B")]);near(record["binder_to_target"],directions[("B","A")])
  near(record["minimum"],min(directions.values()))
  ips.append({"candidate":row["candidate"],"model_id":row["model_id"],"pae_cutoff":cut,"independent_AB":a,"independent_BA":b,"reported_min":record["minimum"],"differs_from_max":min(directions.values())!=max(directions.values())})
 pairs,natom=contacts(*cs);assert natom==row["heavy_atom_contacts_5A"] and len(pairs)==row["residue_contacts_5A"]
 plddtpos=sorted({i for i,j in pairs}|{n+j for i,j in pairs})
 if pairs:
  ev=[pae[i,n+j] for i,j in pairs];rev=[pae[n+j,i] for i,j in pairs]
  near(row["interface_plddt"],float(plddt[plddtpos].mean()));near(row["contact_pae_target_to_binder_A"],np.mean(ev));near(row["contact_pae_binder_to_target_A"],np.mean(rev));near(row["contact_pae_bidirectional_mean_A"],np.mean(ev+rev))
  margin=min(score["iptm"]/.75,float(plddt[n:].mean())/.8,float(plddt[plddtpos].mean())/.8,8/max(2,float(np.mean(ev+rev))))
  near(row["confidence_baseline_margin"],margin);assert row["confidence_baseline_pass"]==(margin>=1)
 else:assert row["interface_plddt"] is None and row["confidence_baseline_pass"] is None
 moved=aligned(cs[1]["atoms"],cs[0]["ca"],native[0]["ca"]);neighbors=cKDTree(moved).query_ball_tree(cKDTree(native[1]["atoms"]),2.0)
 # strict <2, not <=2 boundary
 pairs2=[(i,j) for i,js in enumerate(neighbors) for j in js if np.linalg.norm(moved[i]-native[1]["atoms"][j])<2]
 candn=len({i for i,j in pairs2});natn=len({j for i,j in pairs2});g=row["competition_geometry"]
 assert g["candidate_atoms_with_native_partner_overlap_lt2A"]==candn
 assert g["native_partner_atoms_with_candidate_overlap_lt2A"]==natn
 assert g["overlapping_atom_pairs_lt2A"]==len(pairs2)
 pred_res={i for i,j in pairs};shared=native_res&pred_res
 assert g["native_target_epitope_n"]==len(native_res) and g["candidate_target_epitope_n"]==len(pred_res) and g["shared_target_epitope_n"]==len(shared)
 near(g["native_epitope_coverage"],len(shared)/len(native_res))
 if pred_res:near(g["candidate_epitope_overlap_fraction"],len(shared)/len(pred_res))
 else:assert g["candidate_epitope_overlap_fraction"] is None
 geos.append({"candidate":row["candidate"],"model_id":row["model_id"],"candidate_atoms":candn,"native_atoms":natn,"pairs":len(pairs2)})
assert len({x[0] for x in identities})==3
for cand in {x[0] for x in identities}:assert {(m,s) for c,m,s in identities if c==cand}=={(m,s) for m in range(1,6) for s in (1042,1043,1044)}
expected={}
for p,r in ((oldplan,old["plan"]),(newplan,setup["remaining_physics_plan"])):
 for e in p["entries"]:
  key=(e["identity"],e["seed"]);assert key not in expected;expected[key]=(e,r,p)
assert len(expected)==24 and len(physics["results"])==24
presults={};zero=[];negative=[]
for receipt in physics["results"]:
 result=read(receipt);key=(result["identity"],result["seed"]);assert key not in presults
 e,planrec,planobj=expected[key]
 assert result["input"]==e["input"] and result["plan"]==planrec and result["sequences"]==e["sequences"]
 assert result["environment_freeze"]==planobj["environment_freeze"]
 for r in (result["input"],result["plan"],result["environment_freeze"],result["relaxed_pdb"]):verify(r)
 assert [c["seq"] for c in structure(Path(result["input"]["path"]))]==e["sequences"]
 assert [c["seq"] for c in structure(Path(result["relaxed_pdb"]["path"]))]==e["sequences"]
 assert result["scorefunction"]=="ref2015" and result["fastrelax_repeats"]==1 and result["max_iter"]==200
 assert result["rigid_body_jumps_fixed"] and result["coordinate_constraints_to_input"]
 area=float(result["dSASA"]);ratio=100*result["dG_separated"]/area if area>0 else None
 if area==0:zero.append(key)
 if area<0:negative.append(key)
 if ratio is None:assert result["dG_per_area_x100"] is None
 else:near(result["dG_per_area_x100"],ratio,1e-8)
 presults[key]=result
assert set(presults)==set(expected)
candidate_ids={e["candidate"]+"_"+e["cluster_id"] for e in medoids["entries"]};assert len(candidate_ids)==5
assert {k[0] for k in presults if not k[0].startswith("native_")}==candidate_ids
assert {k[0] for k in presults if k[0].startswith("native_")}=={"native_2FLU","native_4CH9","native_6TTK"}
for e in medoids["entries"]:
 ident=e["candidate"]+"_"+e["cluster_id"]
 for seed in (1042,1043,1044):assert expected[(ident,seed)][0]["input"]==e["normalized_pdb"]
 axis_medoid=next(x for x in axes["records"] if x["candidate"]==e["candidate"] and x["model_id"]==e["medoid_id"])
 assert axis_medoid["is_medoid"] and axis_medoid["cluster_id"]==e["cluster_id"]
for summary in physics["summary"]:
 ident=summary["identity"];rs=[v for k,v in presults.items() if k[0]==ident];assert len(rs)==3
 vals=[100*r["dG_separated"]/r["dSASA"] if r["dSASA"]>0 else None for r in rs];valid=[x for x in vals if x is not None]
 stat=summary["dG_per_area_x100"];assert stat["n"]==len(valid) and stat["missing"]==3-len(valid)
 if valid:near(stat["median"],np.median(valid))
 else:assert stat["median"] is None and stat["min"] is None and stat["max"] is None
# Test the audited root zero-area branch without modifying any original data.
sys.path.insert(0,str(R/"source/rebuild"));spec=importlib.util.spec_from_file_location("root_axes_audit",R/"source/rebuild/evidence_axes.py");module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
orig_checked=module.checked;native_zero_paths={r["path"] for r in physics["results"] if json.loads(Path(r["path"]).read_text())["identity"]=="native_2FLU"}
def injected_zero(record):
 x=orig_checked(record)
 if record["path"] in native_zero_paths:x=copy.deepcopy(x);x["dSASA"]=0.;x["dG_per_area_x100"]=999.
 return x
module.checked=injected_zero
testout=run/"zero_area_fixture";testout.mkdir()
fixture=module.physics_accept(setup,testout);z=next(x for x in fixture["summary"] if x["identity"]=="native_2FLU")["dG_per_area_x100"]
assert z=={"n":0,"missing":3,"median":None,"min":None,"max":None}
write(run/"recalculated_ipsae.json",{"rows":ips})
write(run/"recalculated_competition_counts.json",{"rows":geos})
observations=[{"severity":"information","issue":"Author ipSAE rescaled score uses PAE-filtered interchain pairs and residue-specific d0; distance15 is recorded by the author implementation for distance diagnostics, not an extra mask on reported ipSAE.","impact":"No numerical defect found; avoid describing ipSAE as a heavy-atom distance-filtered score."},{"severity":"information","issue":"No actual nonpositive interface area occurred in these24 results; root zero-area handling was verified with an isolated in-memory fixture.","impact":"Zero-area null behaviour checked without inventing a real zero-area result."}]
if negative:observations.append({"severity":"warning","issue":"Negative dSASA values encountered","values":negative})
report={"status":"EVIDENCE_AXES_INDEPENDENT_REVIEW_PASSED","job":os.environ["SLURM_JOB_ID"],"root_acceptance":rec(accp),"root_script":rec(R/"source/rebuild/evidence_axes.py"),"counts":{"AF2_models":45,"pae_cutoffs":2,"ipsae_direction_values_recomputed":180,"ipsae_minimum_values_verified":90,"physics_results":24,"candidate_medoids":5,"native_controls":3,"contact_confidence_models":45,"competition_count_models":45,"verified_files":len(verified),"actual_zero_area_results":len(zero),"actual_negative_area_results":len(negative)},"all_90_minima_not_maxima":True,"max_not_equal_min_cases":sum(x["differs_from_max"] for x in ips),"zero_area_null_fixture_passed":True,"original_outputs_modified":False,"GPU_used":False,"blocking_findings":[],"observations":observations}
write(run/"report.json",report)
text=["# 分轴证据独立审阅","","结论：45个AF2复合物与24次物理复核均通过本轮独立验收；没有发现阻断性数值或覆盖错误。","",
"- 从原始PAE独立重算PAE10/15共180个方向ipSAE，与作者固定实现输出在6位小数舍入范围内一致；90个汇总值均取两个方向较小值。",
"- 全部24次物理复核的原始input、plan、environment freeze、relaxed PDB及结果SHA均一致；5个候选medoid和3个原生参照各3个种子，覆盖完整。",
"- 全45模型的接触集合、双向接触PAE、界面pLDDT、置信度门及刚体竞争几何独立复算一致。候选原子计数、原生配体原子计数和原子对数量方向未混淆。",
"- 实际24个结果未出现零或负界面面积。隔离的零面积fixture验证root分支会输出null，中位数与n/missing分母正确；没有改原始文件。",
"- ipSAE作者实现的报告值由PAE过滤及逐残基d0计算；distance15参数同时生成距离诊断，不应误称ipSAE本身施加了重原子距离15Å掩码。","",
"计算模型和种子是技术重复；本验收不证明亲和力、实验结合、竞争阻断或工作流优越性。",""]
(run/"REPORT.md").write_text("\n".join(text))
manifest={"status":report["status"],"job":os.environ["SLURM_JOB_ID"],"inputs":[rec(accp),rec(R/"source/rebuild/evidence_axes.py")],"outputs":[rec(p) for p in sorted(run.rglob("*")) if p.is_file()],"counts":report["counts"],"blocking_findings":[],"script":rec(__file__)}
write(S/"manifest.json",manifest);print(json.dumps(report,indent=2),flush=True)

