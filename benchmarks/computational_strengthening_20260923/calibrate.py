import shutil
from collections import Counter
from Bio import Align
from util import *
from calibration_math import *
run=Run(R,"88_strengthening_calibration",[record_file(SETUP),record_file(S/"protocol.json")]);shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 def collect(stages,status,key):
  out={}
  for stage in stages:
   for p in (R/"steps"/stage/"runs").glob("*/manifest.json"):
    m=read_json(p)
    if m["status"]==status:
     d=read_json(verify_file(m["outputs"]["results"]));k=d["entry"][key];require(k not in out,"DUPLICATE_RESULTS",k);out[k]=(d,record_file(p))
  return out
 scored=collect(("75_af2_review_score","81_strengthening_score"),"AF2_REVIEW_SCORED","id")
 mono=collect(("87_strengthening_extension_score",),"EXTENSION_SCORED","id")
 phys=collect(("84_strengthening_physics",),"PHYSICS_COMPLETE","id")
 entries=baseplan()["all_controls"]+baseplan()["candidates"];rows=[]
 for e in entries:
  require(e["id"] in scored and e["id"]+"_mono" in mono and e["id"] in phys,"MISSING_MODULE",e["id"])
  data,source=scored[e["id"]];md,ms=mono[e["id"]+"_mono"];pd,ps=phys[e["id"]];expanded=[v for v in data["models"] if v["arm"]=="expanded"];old=[v for v in data["models"] if v["arm"]=="baseline"];require(len(expanded)==15 and len(md["models"])==15 and len(pd["models"])==3,"ENSEMBLE_COUNT",e["id"])
  ips=[]
  for v in expanded:
   directions=[s["ipSAE"] for x in v["ipsae"] if x["pae_cutoff"]==10 for s in x["scores"] if s["type"]=="asym"]
   require(len(directions)==2,"IPSAE",e["id"]);ips.append(min(directions))
  def confidence(v):
   c=v["raw"]["confidence"];return min(c["global_iptm"]/.75,c["binder_plddt"]/.8,(c["interface_plddt"] or 0)/.8,8/max(c["contact_pae"] or 1e6,.01))
  med=lambda xs:float(np.median(xs))
  physics=pd["models"];dg=med([v["dG_per_area_x100"] for v in physics]);sc=med([v["shape_complementarity"] for v in physics]);unsat=med([v["buried_unsatisfied"]/max(v["dSASA"],1)*1000 for v in physics])
  monofrac=sum(v["plddt"]>=80 and v["bound_fold_rmsd"]<=2 for v in md["models"])/15
  row=dict(id=e["id"],role=e["role"],target=e["target"],family=e.get("family","KEAP1"),sequence=e["sequence"],positive=e.get("positive"),confidence_score=med([confidence(v) for v in expanded]),ipsae_min=med(ips),monomer_support=monofrac,monomer_plddt=med([v["plddt"] for v in md["models"]]),monomer_bound_rmsd=med([v["bound_fold_rmsd"] for v in md["models"]]),hydrophobic_sasa_fraction=med([v["hydrophobic_sasa_fraction"] for v in md["models"]]),interface_dG_per_area=dg,shape_complementarity=sc,unsat_per_1000A2=unsat,old_raw=sum(v["raw"]["legacy_raw_binding_proxy"] for v in old)>=2,new_raw=sum(v["raw"]["legacy_raw_binding_proxy"] for v in expanded)>=10,new_post_relax_diagnostic=sum(v["raw"]["legacy_confidence_only"] and v["relaxed"]["sterics"]["minimum_heavy_distance"]>=1.5 for v in expanded)>=10,sources=[source,ms,ps])
  paired=[v for v in expanded if v["weight"]==1]
  require(len(paired)==3,"PAIRED_MODEL1_COUNT",e["id"])
  row.update(old_post_relax_diagnostic=sum(v["raw"]["legacy_confidence_only"] and v["relaxed"]["sterics"]["minimum_heavy_distance"]>=1.5 for v in old)>=2,new_model1_raw=sum(v["raw"]["legacy_raw_binding_proxy"] for v in paired)>=2,new_model1_post_relax_diagnostic=sum(v["raw"]["legacy_confidence_only"] and v["relaxed"]["sterics"]["minimum_heavy_distance"]>=1.5 for v in paired)>=2)
  rows.append(row)
 controls=[v for v in rows if v["role"]=="control"];require(len(controls)==78,"CONTROL_COUNT",str(len(controls)))
 # Exact labels remain retrospective. Homologous binder sequences crossing outer folds are removed from training.
 aligner=Align.PairwiseAligner(mode="global",match_score=1,mismatch_score=0,open_gap_score=-2,extend_gap_score=-.1)
 near=set()
 for i,a in enumerate(controls):
  for j,b in enumerate(controls[:i]):
   if min(len(a["sequence"]),len(b["sequence"]))/max(len(a["sequence"]),len(b["sequence"]))<.8:continue
   al=aligner.align(a["sequence"],b["sequence"])[0];pairs=[(int(x),int(y)) for x,y in al.indices.T if x>=0 and y>=0]
   ident=sum(a["sequence"][x]==b["sequence"][y] for x,y in pairs)/max(len(a["sequence"]),len(b["sequence"]))
   if ident>=.8:near.add((a["id"],b["id"]));near.add((b["id"],a["id"]))
 feature_sets={"confidence":["confidence_score"],"plus_ipSAE":["confidence_score","ipsae_min"],"plus_fold_physics":["confidence_score","ipsae_min","monomer_support","negative_energy","shape_complementarity","negative_unsat"]}
 for v in rows:v["negative_energy"]=-v["interface_dG_per_area"];v["negative_unsat"]=-v["unsat_per_1000A2"]
 folds=[];oof={k:[] for k in feature_sets}
 for family in sorted({v["family"] for v in controls}):
  test=[v for v in controls if v["family"]==family];testids={v["id"] for v in test}
  train=[v for v in controls if v["family"]!=family and not any((v["id"],t) in near for t in testids)]
  require(len(train)>0,"NO_TRAINING",family);yy=[v["positive"] for v in test];record=dict(family=family,n_test=len(test),n_train=len(train),variants={})
  for name,features in feature_sets.items():
   X=np.array([[v[k] for k in features] for v in train]);xt=np.array([[v[k] for k in features] for v in test])
   ts=transform(X,X).min(1);vs=transform(X,xt).min(1);threshold,tc=choose_threshold([v["positive"] for v in train],ts)
   pred=vs>=threshold;met=confusion(yy,pred);met.update(AUROC=auc(yy,vs),threshold=threshold,training=tc,topK={})
   order=sorted(range(len(test)),key=lambda i:(-vs[i],test[i]["id"]))
   for K in (1,3,5):met["topK"][str(K)]=dict(n=min(K,len(test)),positive=sum(yy[i] for i in order[:K]),precision=sum(yy[i] for i in order[:K])/min(K,len(test)))
   record["variants"][name]=met
   for v,s,prediction in zip(test,vs,pred):oof[name].append(dict(id=v["id"],family=family,positive=v["positive"],score=float(s),predicted=bool(prediction),threshold=threshold))
  folds.append(record)
 pooled={k:confusion([v["positive"] for v in vv],[v["predicted"] for v in vv]) for k,vv in oof.items()}
 # Resample held-out families, not individual model seeds. Four clusters imply coarse intervals.
 rng=np.random.default_rng(4142);bootstrap={}
 families=sorted({v["family"] for v in controls})
 for name,records in oof.items():
  samples=[]
  for _ in range(2000):
   chosen=rng.choice(families,len(families),replace=True)
   rr=[v for f in chosen for v in records if v["family"]==f]
   samples.append(confusion([v["positive"] for v in rr],[v["predicted"] for v in rr]))
  bootstrap[name]={k:dict(low=float(np.quantile([v[k] for v in samples if v[k] is not None],.025)),high=float(np.quantile([v[k] for v in samples if v[k] is not None],.975))) for k in ("TPR","FPR") if any(v[k] is not None for v in samples)}
 legacy={k:confusion([v["positive"] for v in controls],[v[k] for v in controls]) for k in ("old_raw","old_post_relax_diagnostic","new_model1_raw","new_model1_post_relax_diagnostic","new_raw","new_post_relax_diagnostic")}
 result=dict(family_bootstrap=bootstrap,rows=rows,folds=folds,oof=oof,pooled=pooled,legacy=legacy,near_sequence_pairs=sorted(near),limitations=["78 retrospective controls, only4 conservative families, not prospective success probability.","Original AF2-guided selection and incomplete assay constructs prevent independent biological validation claims.","Competition is evaluated only for candidate/native structures; control binding labels do not supply blockade labels.","Feature sets fixed before new scores; min training-percentile and training FPR<=0.20 threshold, no candidate-driven tuning."])
 atomic_json(run.path/"outputs/results.json",result);run.output("results",run.path/"outputs/results.json")
 print(run.finish("HELD_FAMILY_CALIBRATION_COMPLETE","retrospective_computational",dict(controls=78,candidates=3,families=4)),flush=True)
except Exception as x:run.fail(x);raise

