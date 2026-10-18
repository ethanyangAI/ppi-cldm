import shutil,statistics,collections
from pathlib import Path
import numpy as np
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,require
from ppiblocker.structure import read_structure,superpose,interface
root=Path("/lustre/users/u21111210118/projects/test9")
protocol=root/"source/benchmarks/development_20260922/protocol.json"
plan=root/"steps/21_benchmark_analysis/runs/20260922T051817Z_f84fa156702c/outputs/af2_plan.json"
summary=root/"steps/23_benchmark_report/runs/20260922T052344Z_6cb1d7733a0a/outputs/summary.json"
run=Run(root,"30_development_diagnostics",[record_file(p) for p in [protocol,plan,summary]])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 entries=[e for e in read_json(plan)["entries"] if e.get("backbone")]
 require(len(entries)==32,"COUNT","Expected all 32 historical candidates")
 pools={(p["case"],p["method"]):p for p in read_json(summary)["pools"]}
 rows=[]
 ca=lambda c:np.array([r["ca"] for r in c["residues"]])
 for e in entries:
  p=pools[e["group"],e["method"]]; em=read_json(verify_file(p["evaluation_manifest"]))
  ev=read_json(verify_file(em["outputs"]["evaluation"]))
  row=next(c for c in ev["candidates"] if c["id"]==e["source_candidate"])
  dt,db=read_structure(verify_file(e["backbone"]))[0]
  d=ca(db); n=len(d)
  distances=np.linalg.norm(d[:,None,:]-d[None,:,:],axis=-1)
  neighbors=((distances<10)&(distances>0)).sum(1)
  core=np.where(neighbors>=8)[0]
  if len(core)<3:core=np.arange(5,n-5)
  for model in row["models"]:
   require("geometry" in model,"MODEL_FAILED",e["id"])
   rec=em["outputs"][f"{e['source_candidate']}_{model['index']}_structure"]
   pt,pb=read_structure(verify_file(rec))[0];a=ca(pb)
   require(pb["sequence"]==e["sequence"],"IDENTITY",e["id"])
   r,t,sr=superpose(a,d);rt,tt,tr=superpose(ca(pt),ca(dt))
   dr=float(np.sqrt(np.mean(np.sum((a@rt+tt-d)**2,axis=1))))
   cr,ct,core_rmsd=superpose(a[core],d[core])
   terminal=np.r_[0:5,n-5:n]
   trm=float(np.sqrt(np.mean(np.sum((a[terminal]@r+t-d[terminal])**2,axis=1))))
   pd=np.linalg.norm(a[:,None,:]-a[None,:,:],axis=-1)
   pairrms=float(np.sqrt(np.mean((pd-distances)**2)))
   gaps=np.linalg.norm(np.diff(d,axis=0),axis=1)
   diagnosis="FOLD_AND_POSE_RECOVERED" if sr<=2 and dr<=2 else "FOLD_RECOVERED_POSE_CHANGED" if sr<=2 else "CORE_RECOVERED_PERIPHERY_CHANGED" if core_rmsd<=2 else "FOLD_NOT_RECOVERED"
   rows.append(dict(id=e["id"],case=e["group"],method=e["method"],index=model["index"],
     model=rec,backbone=e["backbone"],self_rmsd=sr,target_aligned_rmsd=dr,target_rmsd=tr,
     core_rmsd=core_rmsd,core_positions=(core+1).tolist(),terminal_rmsd_after_self_alignment=trm,
     pair_distance_rmsd=pairrms,design_ca_gap_count=int(((gaps<2.5)|(gaps>4.5)).sum()),diagnosis=diagnosis,
     original_reasons=model["reasons"],historical_gate_unchanged=True))
 groups=[]
 for key in sorted(pools):
  rr=[r for r in rows if (r["case"],r["method"])==key]
  groups.append(dict(case=key[0],method=key[1],n_models=len(rr),median_self=statistics.median(r["self_rmsd"] for r in rr),
   median_target_aligned=statistics.median(r["target_aligned_rmsd"] for r in rr),
   median_core=statistics.median(r["core_rmsd"] for r in rr),diagnoses=dict(collections.Counter(r["diagnosis"] for r in rr)),
   design_gap_models=sum(r["design_ca_gap_count"]>0 for r in rr)))
 atomic_json(run.path/"outputs/diagnostics.json",dict(rows=rows,groups=groups,not_calibrated=True,threshold_2A_descriptive_only=True))
 run.output("diagnostics",run.path/"outputs/diagnostics.json")
 lines=["# 生成失败分解：折叠与对接位置","",
 "全部32条历史候选、96个Boltz模型的CPU诊断。2 Å仅为沿用的描述性分界，不是新校准阈值；未修改旧S0/S1。",
 "核心由设计骨架中10 Å内至少8个其他CA邻居定义；不足3个时使用去除两端各5残基的区域。核心单独对齐，不等于整体设计pose恢复。",
 "","|体系|方法|模型数|自身对齐RMSD|靶标对齐RMSD|核心RMSD|诊断计数|","|---|---|---:|---:|---:|---:|---|"]
 for g in groups:lines.append(f"|{g['case']}|{g['method']}|{g['n_models']}|{g['median_self']:.2f}|{g['median_target_aligned']:.2f}|{g['median_core']:.2f}|{g['diagnoses']}|")
 (run.path/"outputs/生成失败分解.md").write_text("\n".join(lines)+"\n");run.output("report",run.path/"outputs/生成失败分解.md")
 print(run.finish("DEVELOPMENT_DIAGNOSTICS_COMPLETE","posthoc_development_diagnostic",dict(models=len(rows))),flush=True)
except Exception as e:run.fail(e);raise

