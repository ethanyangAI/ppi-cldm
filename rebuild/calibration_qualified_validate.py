"""Independent recalculation of frozen held-family classification and coverage.
Does not import calibration_qualified or run_calibration.
"""
from pathlib import Path
import json,hashlib,os,datetime,math
import numpy as np
S=Path("/lustre/users/u21111210118/projects/test9/steps/18_qualified_calibration")
def read(p):return json.loads(Path(p).read_text())
def rec(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def verify(v):
 r=rec(v["path"]);assert r["sha256"]==v["sha256"] and r["bytes"]==v.get("bytes",r["bytes"])
def eq(a,b):
 if a is None or b is None:assert a is None and b is None,(a,b)
 elif isinstance(a,bool) or isinstance(b,bool):assert a is b,(a,b)
 else:assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(a,b)
def finite(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def mcalc(rows):
 predicted=[v for v in rows if isinstance(v["predicted"],bool)]
 tp=sum(v["positive"] and v["predicted"] for v in predicted)
 fp=sum(not v["positive"] and v["predicted"] for v in predicted)
 tn=sum(not v["positive"] and not v["predicted"] for v in predicted)
 fn=sum(v["positive"] and not v["predicted"] for v in predicted)
 scored=[v for v in rows if finite(v["score"])]
 positives=[v["score"] for v in scored if v["positive"]];negatives=[v["score"] for v in scored if not v["positive"]]
 auc=sum((a>b)+.5*(a==b) for a in positives for b in negatives)/(len(positives)*len(negatives)) if positives and negatives else None
 return dict(TP=tp,FP=fp,TN=tn,FN=fn,TPR=tp/(tp+fn) if tp+fn else None,FPR=fp/(fp+tn) if fp+tn else None,precision=tp/(tp+fp) if tp+fp else None,AUROC=auc,n_eligible=len(rows),n_positive=sum(v["positive"] for v in rows),n_negative=sum(not v["positive"] for v in rows),n_scored=len(scored),n_predicted=len(predicted),n_missing_score=len(rows)-len(scored),n_missing_prediction=len(rows)-len(predicted),score_coverage=len(scored)/len(rows) if rows else None,prediction_coverage=len(predicted)/len(rows) if rows else None,predicted_positive_denominator=sum(v["positive"] for v in predicted),predicted_negative_denominator=sum(not v["positive"] for v in predicted))
def percentile(train,v):return (sum(s<v for s in train)+.5*sum(s==v for s in train))/len(train)
def train_fit(train):
 if len({v["positive"] for v in train})<2:return None
 raw=[v["confidence_score"] for v in train]
 ts=[percentile(raw,v) for v in raw]
 best=None
 for t in sorted(set(ts)|{max(ts)+1}):
  c=mcalc([dict(positive=v["positive"],score=s,predicted=s>=t) for v,s in zip(train,ts)])
  if c["FPR"]<=.2:
   key=(c["TPR"],-c["FPR"],t)
   if best is None or key>best[0]:best=(key,t)
 return best[1]
def check_metrics(actual,expected):
 for key,v in expected.items():eq(actual[key],v)
pointer=read(S/"calibration_pointer.json");verify(pointer["manifest"])
man=read(pointer["manifest"]["path"])
for v in man["inputs"]+man["source"]+man["outputs"]:verify(v)
result=read(next(v["path"] for v in man["outputs"] if v["path"].endswith("/calibration.json")))
rows=result["all78_rows"];frozen=read(S/"frozen/eligibility78.json")["entries"]
assert len(rows)==78 and len({v["sequence_sha256"] for v in rows})==78
byid={x["id"]:x for x in frozen}
for v in rows:
 for k,x in byid[v["id"]].items():assert v[k]==x,(v["id"],k)
 assert (v["confidence_score"] is None)==(v["n_confidence_models"]!=15)
near=read(S/"frozen/cross_family_sequence_leakage.json")["pairs"]
pairs={(v["id1"],v["id2"]) for v in near}|{(v["id2"],v["id1"]) for v in near}
counts={}
for name,key,expected_count in [("main","main_eligible",32),("screen_sensitivity","screen_sensitivity_eligible",67)]:
 resultset=result["analyses"][name];eligible=[v for v in rows if v[key]];assert len(eligible)==expected_count
 families=sorted({x["family"] for x in eligible});assert len(families)==(3 if name=="main" else 4)
 oof=[];foldmap={x["family"]:x for x in resultset["folds"]}
 for f in families:
  test=[v for v in eligible if v["family"]==f]
  train_pre=[v for v in eligible if v["family"]!=f]
  train=[v for v in train_pre if not any((v["id"],t["id"]) in pairs for t in test)]
  ft=foldmap[f];assert ft["train_after_leakage"]["n"]==len(train)
  assert set(ft["leakage_excluded_ids"])=={v["id"] for v in train_pre if v not in train}
  train=[v for v in train if finite(v["confidence_score"])];t=train_fit(train)
  eq(ft["fit"]["threshold"],t);test_results=[]
  for v in test:
   raw=v["confidence_score"]
   score=percentile([v["confidence_score"] for v in train],raw) if t is not None and finite(raw) else None
   pred=score>=t if score is not None else None
   test_results.append(dict(id=v["id"],family=f,positive=v["positive"],score=score,predicted=pred))
  check_metrics(ft["metrics"],mcalc(test_results));oof+=test_results
 outmap={v["id"]:v for v in resultset["oof"]};assert len(outmap)==len(eligible)
 for v in oof:
  eq(outmap[v["id"]]["score"],v["score"]);eq(outmap[v["id"]]["predicted"],v["predicted"])
 check_metrics(resultset["pooled"],mcalc(oof))
 baseline=[dict(positive=v["positive"],score=v["confidence_score"],predicted=v["confidence_score"]>=1 if finite(v["confidence_score"]) else None) for v in eligible]
 check_metrics(resultset["fixed_confidence_reference"],mcalc(baseline))
 rng=np.random.default_rng(4142);boot=[]
 for _ in range(2000):
  chosen=rng.choice(families,len(families),replace=True)
  boot.append(mcalc([v for f in chosen for v in oof if v["family"]==f]))
 for metric in ["TPR","FPR","precision","prediction_coverage","score_coverage"]:
  vals=[v[metric] for v in boot if v[metric] is not None]
  b=resultset["bootstrap"]["intervals"][metric]
  assert b["valid_replicates"]==len(vals) and b["undefined_replicates"]==2000-len(vals)
  eq(b["low"],float(np.quantile(vals,.025)) if vals else None);eq(b["high"],float(np.quantile(vals,.975)) if vals else None)
 def check_raw(actual,rr):
  expected=dict(n_eligible=len(rr),n_complete=sum(v["confidence_score"] is not None for v in rr),n_missing=sum(v["confidence_score"] is None for v in rr),n_complete_positive=sum(v["confidence_score"] is not None and v["positive"] for v in rr),n_complete_negative=sum(v["confidence_score"] is not None and not v["positive"] for v in rr))
  assert actual==expected
 check_raw(resultset["raw_confidence_coverage"],eligible)
 for f in families:check_raw(foldmap[f]["raw_confidence_coverage"],[v for v in eligible if v["family"]==f])
 counts[name]=mcalc(oof)
assert result["independent_experimental_validation"] is False
checks=["all_hash_receipts","frozen_all78_qualification_unchanged","78_unique_sequences","all_eligible_and_missing_denominators","independent_midrank_and_train_FPR_threshold_recalculation","all_fold_OOF_scores_and_nullable_predictions","single_class_rates_and_AUROC_null","fixed_baseline","family_bootstrap_2000_seed4142"]
out=dict(status="INDEPENDENT_QUALIFIED_CALIBRATION_VALIDATION_PASS",job_id=os.environ["SLURM_JOB_ID"],created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),calibration_manifest=pointer["manifest"],validator=rec(__file__),checks=checks,analyses=counts)
run=Path(pointer["manifest"]["path"]).parent
p=run/"independent_acceptance.json";p.write_text(json.dumps(out,indent=2)+"\n")
completion=dict(status="QUALIFIED_CONFIDENCE_CALIBRATION_ACCEPTED",calibration_manifest=pointer["manifest"],independent_acceptance=rec(p),scope="retrospective conditioned binding screens, not prospective affinity or blockade")
with (S/"completion.json").open("x") as f:json.dump(completion,f,indent=2);f.write("\n")
print(json.dumps(completion,indent=2),flush=True)

