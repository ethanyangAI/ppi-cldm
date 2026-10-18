import sys,shutil,re,itertools,subprocess
from pathlib import Path
from ppiblocker.common import Run,read_json,record_file,verify_file,atomic_json,require
from ppiblocker.structure import read_structure,write_pdb
root=Path(sys.argv[1])
jobs={"185845":("P06","RF_native"),"185846":("P09","RF_native"),"185861":("P06","RF_predicted_pose"),
"185876":("P09","RF_motif"),"185886":("P06","RF_motif"),"185872":("P06","BoltzGen"),"185873":("P09","BoltzGen"),"185879":("P32","RF_native_uncertain_reference")}
run=Run(root,"21_benchmark_analysis",[])
shutil.copy2(__file__,run.path/"qc/driver.py")
try:
 found={};entries=[];summary=[]
 for p in sorted((root/"steps/03_design/runs").glob("*/manifest.json")):
  m=read_json(p);j=m.get("execution",{}).get("slurm_job_id")
  if j not in jobs or m["status"]!="DESIGNS_GENERATED":continue
  require(j not in found,"DUPLICATE_DESIGN_JOB",j);found[j]=record_file(p)
  cid,method=jobs[j];native=verify_file(m["outputs"]["native"]);chains,_=read_structure(native);target=chains[0]["sequence"]
  candidates=read_json(verify_file(m["outputs"]["candidates"]))
  evaluators=[]
  for ep in (root/"steps/04_evaluate/runs").glob("*/manifest.json"):
   em=read_json(ep)
   if any(x["sha256"]==record_file(p)["sha256"] for x in em.get("inputs",[])) and em["status"]=="EVALUATION_COMPLETE":evaluators.append((ep,em))
  require(len(evaluators)<=1,"AMBIGUOUS_EVALUATION",str(p))
  ev=read_json(verify_file(evaluators[0][1]["outputs"]["evaluation"])) if evaluators else None
  row=dict(case=cid,method=method,job=j,design_manifest=record_file(p),count=len(candidates),
    evaluation_manifest=record_file(evaluators[0][0]) if evaluators else None,accepted=evaluators[0][1].get("accepted_count") if evaluators else None)
  if ev:
   row["candidate_metrics"]=[dict(id=c["id"],status=c["status"],models=[dict(metrics=x["metrics"],geometry={k:v for k,v in x["geometry"].items() if not isinstance(v,(dict,list))},reasons=x.get("reasons")) for x in c["models"]]) for c in ev["candidates"]]
  binderfiles=[]
  for i,c in enumerate(candidates):
   backbone=verify_file(c["backbone"]);cs,_=read_structure(backbone)
   binderfile=run.path/"work"/f"{cid}_{method}_{i}.pdb";write_pdb(binderfile,[cs[1]])
   binderfiles.append(binderfile)
   entries.append(dict(id=f"{cid}_{method}_{i}",group=cid,method=method,sequence=c["sequence"],target_sequence=target,
       native=record_file(native),backbone=record_file(backbone),source_candidate=c["id"],design_manifest=record_file(p)))
  scores=[]
  for a,b in itertools.combinations(range(len(binderfiles)),2):
   r=subprocess.run([root/"env/metrics/bin/TMalign",binderfiles[a],binderfiles[b]],capture_output=True,text=True,check=True)
   ts=[float(x) for x in re.findall(r"TM-score=\s*([0-9.]+)",r.stdout)]
   require(len(ts)>=2,"TMALIGN_PARSE",r.stdout)
   scores.append(dict(a=a,b=b,tm_min=min(ts[:2])))
  clusters={}
  for threshold in [.6,.8,.95]:
   parent=list(range(len(candidates)))
   def find(x):
    while parent[x]!=x:x=parent[x]
    return x
   for s in scores:
    if s["tm_min"]>=threshold:parent[find(s["a"])]=find(s["b"])
   clusters[str(threshold)]=len({find(i) for i in range(len(candidates))})
  row.update(tm_pairs=scores,structural_clusters_single_link=clusters,unique_sequences=len({c["sequence"] for c in candidates}))
  summary.append(row)
 controls=root/"steps/17_published_controls/runs/20260922T045641Z_92eb165c93ff/outputs/controls.json"
 p=root/"steps/01_pose/runs/20260920T125044Z_6e90b25258de/manifest.json";m=read_json(p);native=verify_file(m["outputs"]["native"]);target=read_structure(native)[0][0]["sequence"]
 for c in read_json(controls):entries.append(dict(id=c["id"].replace("-","_"),group="published_controls",target_sequence=target,
   sequence=c["sequence"],native=record_file(native),label=c["evidence_label"],source=record_file(controls)))
 plan=run.path/"outputs/af2_plan.json";atomic_json(plan,dict(entries=entries,expected_design_jobs=jobs,found_designs=found,missing_design_jobs=sorted(set(jobs)-set(found))))
 results=run.path/"outputs/summary.json";atomic_json(results,summary)
 run.output("af2_plan",plan);run.output("summary",results)
 print(run.finish("BENCHMARK_SNAPSHOT","computational_only",dict(complete_design_matrix=len(found)==len(jobs),found=len(found),expected=len(jobs))),flush=True)
except Exception as e:run.fail(e);raise

