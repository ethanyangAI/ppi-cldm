"""Qualification-frozen, confidence-only held-family calibration.
All computation is a Slurm CPU task. No missing label or prediction becomes negative.
"""
from pathlib import Path
import argparse, collections, datetime, hashlib, importlib.util, json, math, os, sys
import numpy as np
from Bio import Align
R=Path("/lustre/users/u21111210118/projects/test9")
S=R/"steps/18_qualified_calibration"
RF=R/"steps/14_control_qualification/rfd60/runs/20261003T031835Z_11903_qualification_v1_1"
BC=R/"steps/14_control_qualification/bindcraft18"
BASE=R/"steps/02_controls_recovery/runs/20261002T113406Z_11698/outputs/recovered_controls78.json"
RFR=R/"steps/14_control_qualification/rfd60/runs/20261004T045558Z_11918_independent_validation/independent_validation.json"
BCR=BC/"validation/receipt.json"
MATH=R/"source/benchmarks/computational_strengthening_20260923/calibration_math.py"
spec=importlib.util.spec_from_file_location("historic_calibration_math",MATH)
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
def rec(p):
 p=Path(p); b=p.read_bytes()
 return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def verify(v):
 got=rec(v["path"]);assert got["sha256"]==v["sha256"],v["path"]
 if "bytes" in v:assert got["bytes"]==v["bytes"],v["path"]
 return Path(v["path"])
def read(p):return json.loads(Path(p).read_text())
def write(p,x,exclusive=False):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 text=json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+"\n"
 if exclusive:
  with p.open("x") as f:f.write(text)
 else:
  t=p.with_suffix(p.suffix+".partial");t.write_text(text);t.replace(p)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def counts(rows):
 return dict(n=len(rows),positive=sum(x["positive"] for x in rows),negative=sum(not x["positive"] for x in rows),by_family={f:dict(n=len(a:=[v for v in rows if v["family"]==f]),positive=sum(v["positive"] for v in a),negative=sum(not v["positive"] for v in a)) for f in sorted({v["family"] for v in rows})})
def sequence_identity(a,b):
 if min(len(a),len(b))/max(len(a),len(b))<.8:return 0.0
 al=Align.PairwiseAligner(mode="global",match_score=1,mismatch_score=0,open_gap_score=-2,extend_gap_score=-.1).align(a,b)[0]
 pairs=[(int(x),int(y)) for x,y in al.indices.T if x>=0 and y>=0]
 return sum(a[x]==b[y] for x,y in pairs)/max(len(a),len(b))
def threshold(y,s):
 if len(set(y))<2:
  return None,dict(status="not_estimable",reason="training_missing_class",n=len(y),n_positive=sum(y),n_negative=len(y)-sum(y))
 t,c=cm.choose_threshold(y,s,max_fpr=.2);return float(t),dict(status="estimable",**c)
def fold_fit(train,test):
 usable=[v for v in train if finite(v.get("confidence_score"))]
 t,tc=threshold([v["positive"] for v in usable],[v["confidence_score"] for v in usable])
 if t is None:return dict(threshold=None,training=tc),[dict(id=v["id"],family=v["family"],positive=v["positive"],raw_score=v.get("confidence_score"),score=None,predicted=None,reason="training_missing_class") for v in test]
 x=np.array([[v["confidence_score"]] for v in usable],float)
 ts=cm.transform(x,x)[:,0];t,tc=threshold([v["positive"] for v in usable],ts)
 rows=[]
 for v in test:
  raw=v.get("confidence_score")
  if finite(raw):
   s=float(cm.transform(x,np.array([[raw]],float))[0,0]);pred=bool(s>=t);reason=None
  else:s=None;pred=None;reason="missing_complete_confidence_score"
  rows.append(dict(id=v["id"],family=v["family"],positive=v["positive"],raw_score=raw,score=s,predicted=pred,reason=reason))
 return dict(threshold=t,training=tc),rows
def metrics(rows):
 scored=[v for v in rows if finite(v.get("score"))]
 predicted=[v for v in rows if type(v.get("predicted")) is bool]
 c=cm.confusion([v["positive"] for v in predicted],[v["predicted"] for v in predicted]) if predicted else dict(TP=0,FP=0,TN=0,FN=0,TPR=None,FPR=None,precision=None)
 return dict(n_eligible=len(rows),n_positive=sum(v["positive"] for v in rows),n_negative=sum(not v["positive"] for v in rows),n_scored=len(scored),n_predicted=len(predicted),n_missing_score=len(rows)-len(scored),n_missing_prediction=len(rows)-len(predicted),score_coverage=len(scored)/len(rows) if rows else None,prediction_coverage=len(predicted)/len(rows) if rows else None,predicted_positive_denominator=sum(v["positive"] for v in predicted),predicted_negative_denominator=sum(not v["positive"] for v in predicted),AUROC=cm.auc([v["positive"] for v in scored],[v["score"] for v in scored]) if scored else None,AUROC_scope="available held-out scores only",**c)
def freeze():
 assert rec(BASE)["sha256"]=="03c7f3aa14f7996393cd24d657f9a7e510c143893a95181a637ea786e7efe032"
 assert rec(RF/"manifest.json")["sha256"]=="606d7c03c2dfcba52f55b43a6591c39b075adbb803fa499c3ca387d69162223b"
 assert rec(BC/"manifest.json")["sha256"]=="c87cecf1bafba480146e8aa1ca1d41813cc9e91b1ea1746cb4a4905f05433aa9"
 rr=read(RFR);br=read(BCR);assert rr["status"]=="INDEPENDENT_VALIDATION_PASS";verify(rr["qualification_manifest"])
 assert br["status"]=="INDEPENDENT_VALIDATION_PASSED" and br["manifest_sha256"]==rec(BC/"manifest.json")["sha256"]
 rfman=read(RF/"manifest.json");bcman=read(BC/"manifest.json")
 for v in rfman["outputs"]:verify(v)
 for v in bcman["outputs"].values():verify(v)
 rfs={v["id"]:v for v in read(RF/"outputs/qualification_overlay60.json")["entries"]}
 bcs={v["id"]:v for v in read(BC/"outputs/qualification_overlay.json")["entries"]}
 raw=read(BASE)["entries"];assert len(raw)==78 and len({v["id"] for v in raw})==78
 assert set(rfs).isdisjoint(bcs) and set(rfs)|set(bcs)=={v["id"] for v in raw}
 rows=[]
 for b in raw:
  ident=b["id"];pos=bool(b["binary_binding_label"])
  assert hashlib.sha256(b["sequence"].encode()).hexdigest()==b["sequence_sha256"]
  assert hashlib.sha256(b["target_sequence"].encode()).hexdigest()==b["target_sequence_sha256"]
  if ident in rfs:
   a=rfs[ident];qual=a["qualification"]
   assert a["author_binding_label"]["value"]==pos
   assert a["identity"]["binder_sequence_sha256"]==b["sequence_sha256"]
   assert a["identity"]["target_sequence_sha256"]==b["target_sequence_sha256"]
   main=qual["eligible_main_analysis"];screen=qual["eligible_source_matched_bli_screen"]
   assert not main or qual["main_analysis_label"]==pos
   reason=qual["main_analysis_exclusion_reason"];classification=qual["classification"]
   endpoint=qual["main_analysis_endpoint"];flags=qual["flags"];source="RFdiffusion2023"
  else:
   a=bcs[ident];qual=a["adjudication"];assert a["binary_binding_label"]==int(pos)
   assert a["sequence_sha256"]==b["sequence_sha256"] and a["target_sequence_sha256"]==b["target_sequence_sha256"]
   main=qual["main_analysis_eligible"];screen=qual["sensitivity_analysis_eligible"]
   reason=None if main else qual["exact_model_vs_assay_target_construct"]
   classification=qual["status"];endpoint=qual["main_analysis_endpoint"];flags=[qual["exact_model_vs_assay_target_construct"]];source="BindCraft2025"
  family={"Mdm2":"Mdm2","IL7Ra":"Ig_like","Pdl1":"Ig_like","BBF-14":"BBF-14","BetV1":"BetV1"}[b["target"]]
  rows.append(dict(id=ident,source_id=b["source_id"],target=b["target"],family=family,source=source,sequence=b["sequence"],sequence_sha256=b["sequence_sha256"],target_sequence_sha256=b["target_sequence_sha256"],positive=pos,main_eligible=bool(main),screen_sensitivity_eligible=bool(screen),qualification_class=classification,main_exclusion_reason=reason,conditioned_endpoint=endpoint,qualification_flags=flags,blockade_eligible=False))
 assert counts([v for v in rows if v["main_eligible"]])["n"]==32
 assert counts([v for v in rows if v["main_eligible"]])["positive"]==21
 assert counts([v for v in rows if v["screen_sensitivity_eligible"]])["n"]==67
 assert counts([v for v in rows if v["screen_sensitivity_eligible"]])["positive"]==38
 unresolved=[v for v in rows if not v["screen_sensitivity_eligible"]];assert len(unresolved)==11 and all(not v["positive"] and not v["main_eligible"] for v in unresolved)
 pairs=[]
 for i,a in enumerate(rows):
  for b in rows[:i]:
   if a["family"]==b["family"]:continue
   ident=sequence_identity(a["sequence"],b["sequence"])
   if ident>=.8:pairs.append(dict(id1=a["id"],id2=b["id"],full_length_identity=ident))
 protocol=dict(version="qualified-confidence-family-calibration-1.0",frozen_utc=now(),job_id=os.environ.get("SLURM_JOB_ID"),unit="unique binder sequence entry, not model seed",score="median of all 15 model confidence scores; missing/incomplete ensemble = missing",model_confidence="min(global AF2 ipTM / 0.75, binder pLDDT[0..1] / 0.8, interface pLDDT[0..1] / 0.8, 8 / max(contact PAE Angstrom,0.01)); no contacts or nonfinite => null",features=["confidence_score"],normalization="train-only midrank percentile using historical calibration_math.transform",threshold_rule="training FPR <= 0.20; maximize training TPR, then minimize FPR, then highest threshold",single_class_training="not_estimable; threshold, percentile, and prediction null",single_class_test="AUROC null; undefined class-specific rate null",missing_policy="retain full eligibility denominator, report score and prediction coverage; never impute rejection",family_leaveout={"Mdm2":"Mdm2","IL7Ra":"Ig_like","Pdl1":"Ig_like","BBF-14":"BBF-14","BetV1":"BetV1"},leakage_rule="remove train binder with >=0.8 identity to any held-out eligible binder; identity global exact matches/max full lengths; match=1 mismatch=0 gap_open=-2 gap_extend=-0.1",bootstrap=dict(unit="held-out target family",n=2000,seed=4142,quantiles=[.025,.975],limitation="Only three/four families; coarse intervals, no prospective or broad generalization claim"),fixed_confidence_reference="same raw confidence_score >= 1 with missing preserved; no historical model comparison",analysis_sets={"main":"32 source-conditioned, construct-supported screen entries, 21 positive/11 conditional negative; not standardized affinity","screen_sensitivity":"67 author screen entries, 38 positive/29 conditional negative; includes dose-uncertain RF nonhits, nonmonomeric positives, BetV1 F63/L63 uncertainty"},not_claimed=["binding affinity","native-partner blockade","prospective hit probability","pipeline superiority","training-set independence"],inputs=[rec(p) for p in [BASE,RF/"manifest.json",RF/"outputs/qualification_overlay60.json",RFR,BC/"manifest.json",BC/"outputs/qualification_overlay.json",BCR,MATH]])
 outputs=S/"frozen";write(outputs/"protocol.json",protocol,True)
 write(outputs/"eligibility78.json",dict(status="QUALIFICATIONS_FROZEN_BEFORE_STEP17_SCORES",created_utc=now(),entries=rows,denominators={k:counts([v for v in rows if v[f]]) for k,f in [("main","main_eligible"),("screen_sensitivity","screen_sensitivity_eligible")]},unresolved_ids=[v["id"] for v in unresolved]),True)
 write(outputs/"cross_family_sequence_leakage.json",dict(pairs=pairs,rule=protocol["leakage_rule"]),True)
 write(S/"freeze_receipt.json",dict(status="QUALIFICATION_AND_PROTOCOL_FROZEN",created_utc=now(),job_id=os.environ.get("SLURM_JOB_ID"),source=rec(__file__),outputs=[rec(outputs/p) for p in ["protocol.json","eligibility78.json","cross_family_sequence_leakage.json"]],score_inputs_read=False),True)
 print(json.dumps(dict(status="FROZEN",main=32,screen=67,unresolved=11,near_sequence_pairs=len(pairs)),indent=2))
def evaluate(rows,near):
 families=sorted({v["family"] for v in rows});oof=[];folds=[]
 for family in families:
  test=[v for v in rows if v["family"]==family];testids={v["id"] for v in test}
  original_train=[v for v in rows if v["family"]!=family]
  train=[v for v in original_train if not any((v["id"],t) in near for t in testids)]
  fit,out=fold_fit(train,test);oof.extend(out)
  folds.append(dict(family=family,test=counts(test),train_before_leakage=counts(original_train),train_after_leakage=counts(train),train_complete_score_n=sum(finite(v.get("confidence_score")) for v in train),leakage_excluded_ids=[v["id"] for v in original_train if v not in train],fit=fit,metrics=metrics(out)))
 pooled=metrics(oof);rng=np.random.default_rng(4142);boot=[]
 for _ in range(2000):
  chosen=rng.choice(families,len(families),replace=True)
  boot.append(metrics([v for f in chosen for v in oof if v["family"]==f]))
 intervals={}
 for key in ["TPR","FPR","precision","prediction_coverage","score_coverage"]:
  vals=[v[key] for v in boot if v[key] is not None]
  intervals[key]=dict(low=float(np.quantile(vals,.025)) if vals else None,high=float(np.quantile(vals,.975)) if vals else None,valid_replicates=len(vals),undefined_replicates=2000-len(vals))
 baseline=[dict(id=v["id"],family=v["family"],positive=v["positive"],score=v.get("confidence_score"),predicted=bool(v["confidence_score"]>=1) if finite(v.get("confidence_score")) else None) for v in rows]
 return dict(denominator=counts(rows),folds=folds,oof=oof,pooled=pooled,bootstrap=dict(n=2000,seed=4142,families=len(families),intervals=intervals,warning="three/four target families only; coarse intervals"),fixed_confidence_reference=metrics(baseline),fixed_confidence_reference_by_family={f:metrics([v for v in baseline if v["family"]==f]) for f in families})
def selftest():
 def r(i,y,s,f="a"):return dict(id=i,positive=y,confidence_score=s,family=f,sequence="AAAAAAAAAA")
 checks={}
 fit,out=fold_fit([r("p",True,.5)],[r("test",False,.4)])
 assert fit["threshold"] is None and out[0]["predicted"] is None and out[0]["score"] is None;checks["single_class_training_abstains"]=True
 fit,out=fold_fit([r("p",True,.9),r("n",False,.1)],[r("t1",True,None),r("t2",True,.8)])
 met=metrics(out);assert met["n_eligible"]==2 and met["n_predicted"]==1 and met["FPR"] is None and met["AUROC"] is None;checks["missing_preserved_single_class_test_null"]=True
 t,_=threshold([True,False],[.5,.5]);assert t>.5;checks["ties_training_fpr_constraint"]=True
 assert np.allclose(cm.transform(np.array([[.1],[.1],[.9]]),np.array([[.1],[.5]])),[[1/3],[2/3]]);checks["train_only_midrank_ties"]=True
 fit,a=fold_fit([r("p",True,.9),r("n",False,.1)],[r("t",True,.5)])
 _,b=fold_fit([r("p",True,.9),r("n",False,.1)],[r("t",True,.5),r("extreme",False,1e6)])
 assert a[0]["score"]==b[0]["score"];checks["test_extreme_does_not_change_normalization"]=True
 assert sequence_identity("AAAAAAAAAA","AAAAAAAABB")==.8 and sequence_identity("AAAAAAAAAA","AAAAAAABBB")==.7;checks["full_length_identity_boundary"]=True
 rows=[r("a+",True,.9,"A"),r("a-",False,.1,"A"),r("b+",True,.8,"B"),r("b-",False,.2,"B")]
 ev=evaluate(rows,{("b-","a+"),("a+","b-")});fa=next(v for v in ev["folds"] if v["family"]=="A")
 assert fa["leakage_excluded_ids"]==["b-"] and fa["fit"]["threshold"] is None and all(v["predicted"] is None for v in ev["oof"] if v["family"]=="A");checks["cross_family_leakage_can_make_fold_unestimable"]=True
 assert metrics([])["TPR"] is None and metrics([])["FPR"] is None;checks["empty_metrics_null"]=True
 return dict(status="PASS",checks=checks)
def main():
 p=argparse.ArgumentParser();p.add_argument("command",choices=["freeze","selftest"]);a=p.parse_args()
 if a.command=="freeze":freeze()
 else:
  out=selftest();write(S/"tests"/("selftest_"+os.environ.get("SLURM_JOB_ID","manual")+".json"),out,True);print(json.dumps(out,indent=2))
if __name__=="__main__":main()

