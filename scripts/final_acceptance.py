import json, hashlib, subprocess, os
from pathlib import Path
from ppiblocker.common import load_run, atomic_json, record_file
root=Path("/lustre/users/u21111210118/projects/test9")
paths={
"experimental":"01_pose/20260920T084801Z_5390ae1d0dd5",
"automatic_search":"01_pose/20260920T090928Z_c067f0942416",
"sequence_only":"02_predict/20260920T092528Z_14ed67149538",
"design":"03_design/20260920T085024Z_d05b2dfbd08f",
"evaluation":"04_evaluate/20260920T092746Z_7172d44080bd",
"accuracy":"05_validation/20260920T092747Z_4e269f61db54"}
records={}
for name,p in paths.items():
 step,run=p.split('/');path=root/'steps'/step/'runs'/run/'manifest.json'
 m=load_run(path,{'POSE_ACCEPTED','DESIGNS_GENERATED','EVALUATION_COMPLETE','VALIDATION_COMPLETE'})
 records[name]={**record_file(path),'status':m['status'],'checked_inventory_count':len(m.get('file_inventory',[]))}
 print(name,m['status'],flush=True)
eval_path=Path(records['evaluation']['path']).parent/'outputs/evaluation.json'
candidates=json.load(open(eval_path))['candidates']
assert len(candidates)==4 and all(len(c['models'])==3 for c in candidates)
assert all(c['status']=='REJECTED' for c in candidates)
result=subprocess.run([str(root/'env/core/bin/python'),'-m','pytest','-q'],cwd=root/'source',capture_output=True,text=True)
print(result.stdout);assert result.returncode==0,result.stderr
out=root/'steps/00_bootstrap/runs/rebuild_20260920/final_acceptance.json'
atomic_json(out,{'status':'ENGINEERING_ACCEPTED_NO_PASSING_DESIGNS','manifests':records,'design_count':4,'refold_model_count':12,'accepted_design_count':0,'tests':result.stdout.strip(),'scientific_validation':False,'generalization_validation':False})
print(out)
