#!/usr/bin/env python3
import os,sys,json,hashlib,subprocess,stat,datetime,io,contextlib,runpy,re,time
from pathlib import Path
R=Path('/lustre/users/u21111210118/projects/test9');S=R/'steps/24_benchmark_delivery';J=os.environ['SLURM_JOB_ID']
def md(p):
 p=str(p);s=os.lstat(p);return dict(path=p,bytes=s.st_size,inode=s.st_ino,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns,mode=s.st_mode,dev=s.st_dev,nlink=s.st_nlink,uid=s.st_uid,gid=s.st_gid)
def raw(p):
 p=Path(p);a=md(p);assert stat.S_ISREG(a['mode']) and a['nlink']==1 and a['bytes']<128*1024*1024
 for q in p.parents:
  if q==R.parent:break
  assert stat.S_ISDIR(os.lstat(q).st_mode)
 b=p.read_bytes();assert md(p)==a;return b
def rec(p):
 b=raw(p);return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def dump(p,v):
 b=(json.dumps(v,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode();fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb')as f:f.write(b);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444);os.fsync(f.fileno())
 assert raw(p)==b;return rec(p)
assert all(os.environ.get(k)==v for k,v in {'CUDA_VISIBLE_DEVICES':'','JAX_PLATFORMS':'cpu','PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}.items()) and 'PYTHONPATH' not in os.environ
sc=subprocess.run(['scontrol','show','job','-o',J],capture_output=True,text=True,timeout=15);assert sc.returncode==0
fields=dict(re.findall(r'(\w+)=(\S+)',sc.stdout));assert fields['JobId']==J and fields['JobState']=='RUNNING' and fields['NumCPUs']=='1' and fields['NumNodes']=='1' and fields['NumTasks']=='1' and fields['Partition']=='organ' and fields['Account']=='u21111210118' and fields['UserId'].split('(')[0]=='u21111210118'
for k in ('AllocTRES','TRES','ReqTRES'):
 if k in fields:
  for t in fields[k].split(','):
   name,value=t.split('=',1)
   if 'gpu' in name.lower():assert value.isdecimal() and int(value)==0
assert 'AllocTRES' in fields or 'TRES' in fields
assert fields['JobName']=='test9_final_composer_partial_cache_names_contracts_v7'
for key,value in fields.items():
 if 'gpu' in key.lower():assert value in ('0','N/A','(null)') or all(x.rsplit(':',1)[-1]=='0' for x in value.split(','))
for attempt in range(20):
 ac=subprocess.run(['sacct','-X','-j',J,'-n','-P','--format=JobIDRaw,State,AllocCPUS,AllocTRES'],capture_output=True,text=True,timeout=10)
 rows=[x.split('|')for x in ac.stdout.splitlines()if x.split('|')[0]==J]
 if ac.returncode==0 and len(rows)==1 and rows[0][1:3]==['RUNNING','1']:break
 time.sleep(1)
else:raise RuntimeError('Current CPU accounting readiness not observed')
cfg=json.loads(raw(sys.argv[1]));P=Path(cfg['proposal']);old=Path(cfg['original_code']);core=R/'env/core/bin/python3.11'
core_before=md(core);assert rec(core)==dict(path=str(core),bytes=25916456,sha256='76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a')
assert (R/'env/core/bin/python').resolve()==core
prior=cfg['prior_TRO_metadata'];assert md(prior['path'])==prior
Aold=json.loads(raw(cfg['software']['path']));assert rec(cfg['software']['path'])==cfg['software']
original_before={};proposed_before={}
for r in Aold['source']['composer']:
 n=Path(r['path']).name;assert Path(r['path']).parent==old;original_before[r['path']]=md(r['path']);b=raw(r['path']);assert rec(r['path'])==r
 text=b.decode()
 for change in cfg['replacements'].get(n,[]):
  assert text.count(change['old'])==change['count'];text=text.replace(change['old'],change['new'])
 p=P/n;assert raw(p)==text.encode();proposed_before[str(p)]=md(p)
assert sorted(os.listdir(P))==sorted(Path(r['path']).name for r in Aold['source']['composer'])
control_source=rec(__file__);request_r=rec(sys.argv[1]);launcher_r=rec(cfg['launcher_path']);controller_before=md(__file__)
print(json.dumps(dict(status='ACTUAL_CPU1_GPU0_EXACT_PATCH_AND_SOURCE_INPUTS_VERIFIED_SOFTWARE_RUNNING',actual_job_id=J)),flush=True)
log=io.StringIO()
with contextlib.redirect_stdout(log):runpy.run_path(str(P/'composer_bootstrap.py'),run_name='__main__')
producer_stdout=log.getvalue();ar=json.loads(producer_stdout.strip().splitlines()[-1]);assert rec(ar['path'])==ar
A=json.loads(raw(ar['path']));ct=json.loads(raw(A['contracts']['path']));assert rec(A['contracts']['path'])==A['contracts'];txt=raw(ct['log']['path']).decode();assert rec(ct['log']['path'])==ct['log']
named=[]
for line in txt.splitlines():
 if line.startswith('test_'):
  assert line.endswith(' ... ok');named.append(line[:-7])
assert len(named)==len(set(named))==ct['tests_run']==237 and ct['status']=='PASS' and ct['failures']==ct['errors']==0
assert A['actual_CPU_job_id']==J and A['original_owned_pre_and_post_byte_readback_PASS'] is True
for p,v in original_before.items():assert md(p)==v
for p,v in proposed_before.items():assert md(p)==v
for r in A['source']['composer']+A['source']['existing_API_dependencies']+A['source']['context_API_dependencies']:assert rec(r['path'])==r
for r in A['original_executing_sources']:assert rec(r['path'])==r
assert md(core)==core_before and rec(core)['sha256']=='76bfffa0a59589ff6ed13dafd3267a8dff5b73551b6b4d710b96710148d3b33a'
assert md(prior['path'])==prior and md(__file__)==controller_before and rec(__file__)==control_source and rec(sys.argv[1])==request_r
D=S/'submissions'/('root_final_composer_v7_fix10_software_execution_control_'+J);D.mkdir(mode=0o775)
original_groups=dict(composer=A['original_executing_sources'],existing_API_dependencies=A['source']['existing_API_dependencies'],context_API_dependencies=cfg['mapper_original_receipts'])
co=dict(schema='root-final-composer-v7-software-execution-control.v1',status='ACTUAL_SOFTWARE_CONTRACTS_FULL_READBACK_NOT_SCIENCE_SOURCE_OR_INDEX_COMPATIBILITY',actual_job_id=J,actual_producer_acceptance=ar,actual_contracts=A['contracts'],actual_contract_log=ct['log'],actual_frozen_source_groups=A['source'],actual_source_groups_original=original_groups,actual_fresh_allocation=A['allocation'],actual_test_count=ct['tests_run'],zero_failure_error_skip=True,actual_named_loader_ids=named,actual_fixture_SOURCE_PROVENANCE_control_inputs=A['software_operational_control_fixture_receipts'],original_metadata_before_all_Root_IO=[prior]+list(original_before.values())+list(proposed_before.values()),Source_or_INDEX_compatibility_accepted=False,package_restore_accepted=False,production_science_accepted=False,Git_changed=False,published=False,ACTIVE_changed=False,source_repair='EXACT_BASE_I_LOGICAL_CACHE_IDENTITY_WITH_FIXED_NAMES_ONLY_AUTHORITY',controller_source=control_source,controller_request=request_r,controller_launcher=launcher_r,actual_scontrol_stdout=sc.stdout,producer_stdout=producer_stdout,whole_Source_prepost_PASS=True,conditional_Core_prepost_PASS=True)
cr=dump(D/'execution_control.json',co);D.chmod(0o555)
print(producer_stdout,end='',flush=True)
print(json.dumps(dict(status='ACTUAL_CHANGED_SOFTWARE237_AND_ROOT_CONTROL_CPU_ACCEPTED_PENDING_TERMINAL',actual_job_id=J,software=ar,execution_control=cr,software_source=A['source'],controller_source=control_source,controller_request=request_r,controller_launcher=launcher_r)),flush=True)
