from pathlib import Path
import json,hashlib,os,subprocess,re
R=Path("/lustre/users/u21111210118/projects/test9")
J=os.environ['SLURM_JOB_ID']
assert J.isdigit() and not os.environ.get('CUDA_VISIBLE_DEVICES') and os.environ.get('JAX_PLATFORMS')=='cpu'
c=subprocess.run(['scontrol','show','job','-o',J],capture_output=True,text=True,check=True)
assert 'Partition=organ' in c.stdout and 'NumCPUs=1 ' in c.stdout and not re.search(r'(?:gres/gpu|gres:gpu|gpu)[:=][1-9]',c.stdout)
p=subprocess.run(['sacct','-j','13265','--format=JobIDRaw,State,ExitCode,AllocCPUS,AllocTRES','-n','-P'],capture_output=True,text=True,check=True)
rows=[x.split('|') for x in p.stdout.splitlines() if x.split('|')[0]=='13265']
assert len(rows)==1 and rows[0][1:4]==['COMPLETED','0:0','1'] and 'gpu' not in rows[0][4],p.stdout
out=R/'steps/24_benchmark_delivery/runs'/('native_catalog_receipt_capture_'+J);out.mkdir(exist_ok=False)
def rec(f):
 f=Path(f);assert f.is_file() and not f.is_symlink() and f.resolve().is_relative_to(R) and not f.stat().st_mode&0o222
 b=f.read_bytes();return dict(path=str(f),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=R/'steps/24_benchmark_delivery/runs/native74_cache_catalog_13265/acceptance.json'
a=json.loads(f.read_text());assert a['status']=='CPU_CACHE_GUARD_CATALOG_COMPLETE' and a['formal_binding'] is False and a['no_inference'] is True
assert a['allocation']['allocated_gpu_count']==0
for key in ['source','contracts','result']:assert rec(a[key]['path'])==a[key]
contracts=json.loads(Path(a['contracts']['path']).read_text());assert contracts['status']=='PASS' and contracts['tests']==24 and contracts['failures']==contracts['errors']==0
catalog=json.loads(Path(a['result']['path']).read_text());assert catalog['workers']==20 and catalog['raw_models']==74 and catalog['no_scores_transferred'] is True and catalog['future_formal_binding'] is False
result=dict(schema='root-native-catalog-descriptor-capture.v1',status='DESCRIPTOR_CAPTURE_ONLY_NOT_NEW_SCIENTIFIC_ACCEPTANCE',job_id=J,producer_job='13265',allocated_gpus=0,producer_terminal=p.stdout,allocation=c.stdout,acceptance=rec(f),source=a['source'],contracts=a['contracts'],catalog=a['result'],scientific_recomputation_performed=False)
f=out/'descriptor_capture.json';f.write_text(json.dumps(result,indent=2)+'\n');f.chmod(0o444)
print(json.dumps(dict(job_id=J,acceptance=result['acceptance'],catalog=result['catalog']),indent=2))
