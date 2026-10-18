import argparse,traceback,shutil
from pathlib import Path
from ppiblocker.common import Run,load_run,read_json,record_file,atomic_json
from ppiblocker.pipeline import predict,design,evaluate
from ppiblocker.benchmark import select
p=argparse.ArgumentParser();p.add_argument("root");p.add_argument("checks");p.add_argument("case");args=p.parse_args()
root=Path(args.root)
case=next(x for x in read_json(args.checks) if x["case_id"]==args.case)
run=Run(root,"10_benchmark_pilot",[record_file(args.checks)])
shutil.copy2(__file__,run.path/"qc/pilot_source.py")
results={}
for stage,fn,up in [("blind_pose",predict,case["blind_prepare_manifest"]["path"]),
                     ("experimental_pose_design",design,case["prepare_manifest"]["path"])]:
    try:
        result=fn(root,up);results[stage]=record_file(result)
        print(stage,result,read_json(result)["status"],flush=True)
    except Exception as e:
        results[stage]={"status":"FAILED","error":getattr(e,"code","ERROR"),"message":str(e)}
        traceback.print_exc()
    atomic_json(run.path/"outputs/progress.json",results)
if "path" in results.get("experimental_pose_design",{}):
    try:
        result=evaluate(root,results["experimental_pose_design"]["path"]);results["evaluation"]=record_file(result)
        result=select(root,result,8);results["selection"]=record_file(result)
    except Exception as e:
        results["evaluation_error"]={"status":"FAILED","error":getattr(e,"code","ERROR"),"message":str(e)}
        traceback.print_exc()
atomic_json(run.path/"outputs/progress.json",results);run.output("progress",run.path/"outputs/progress.json")
run.manifest["case_id"]=args.case
print(run.finish("PILOT_COMPUTE_COMPLETE" if "selection" in results else "PILOT_COMPUTE_INCOMPLETE",
                 "computational_only",{"experimental_blockade":False}),flush=True)

