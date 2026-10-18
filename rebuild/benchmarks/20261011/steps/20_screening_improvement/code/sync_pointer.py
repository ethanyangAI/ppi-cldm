import os,sys,json
from pathlib import Path
R=Path('/lustre/users/u21111210118/projects/test9')
sys.path.insert(0,str(R/'source/rebuild'))
from screening_transfer import rec,read,verify
p=R/'steps/20_screening_improvement/run_pointer.json'
a=R/'steps/20_screening_improvement/acceptance.json'
accepted=read(a);old=read(p)
assert accepted['status']=='ALL78_1170_SCREENING_IMPROVEMENT_CONTENT_ACCEPTED_DEVELOPMENT_ONLY'
assert old['manifest']==accepted['manifest']
assert accepted['manifest']['sha256']=='8e1889e98fe7d616597baee512768d9a0782c4e60dc45861dd9be4c6553ce141'
verify(accepted['manifest'])
new=dict(status=accepted['status'],manifest=accepted['manifest'],acceptance=rec(a),pointer_sync_job=os.environ['SLURM_JOB_ID'],scientific_scope=accepted['scientific_scope'])
tmp=p.with_suffix('.json.accepted.partial')
with tmp.open('x') as f:json.dump(new,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
tmp.replace(p)
print(json.dumps(dict(status=new['status'],pointer=rec(p)),indent=2))
