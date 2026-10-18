from pathlib import Path
import json,hashlib,os,subprocess,re
R=Path("/lustre/users/u21111210118/projects/test9")
J=os.environ['SLURM_JOB_ID']
assert J.isdigit() and not os.environ.get('CUDA_VISIBLE_DEVICES') and os.environ.get('JAX_PLATFORMS')=='cpu'
c=subprocess.run(['scontrol','show','job','-o',J],capture_output=True,text=True,check=True)
assert 'Partition=organ' in c.stdout and 'NumCPUs=1 ' in c.stdout and not re.search(r'(?:gres/gpu|gres:gpu|gpu)[:=][1-9]',c.stdout)
p=subprocess.run(['sacct','-j','13286','--format=JobIDRaw,State,ExitCode,AllocCPUS,AllocTRES','-n','-P'],capture_output=True,text=True,check=True)
rows=[x.split('|') for x in p.stdout.splitlines() if x.split('|')[0]=='13286']
assert len(rows)==1 and rows[0][1:4]==['COMPLETED','0:0','1'] and 'gpu' not in rows[0][4],p.stdout
out=R/'steps/24_benchmark_delivery/runs'/('root_receipt_capture_'+J)
out.mkdir(exist_ok=False)
items={}
for name in ['acceptance.json','runtime_override_acceptance.json']:
 f=R/'steps/24_benchmark_delivery/runs/generic_runtime_repair_13286'/name
 assert f.is_file() and not f.is_symlink() and not f.stat().st_mode&0o222
 b=f.read_bytes();value=json.loads(b)
 items[name]=dict(path=str(f),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),schema=value.get('schema'),status=value.get('status'))
expected={'acceptance.json':'GENERIC_REPORT_CONTENT_AND_REVIEWED_MATERIALIZED_RUNTIME_CPU_REPAIR_ACCEPTED_ORIGINAL13263_FAILED_PRESERVED','runtime_override_acceptance.json':'REVIEWED_FULL_MATERIALIZED_RFD_RUNTIME_OVERRIDE_CPU_ACCEPTED_DEFAULT_UNCHANGED'}
assert all(items[k]['status']==v for k,v in expected.items()),items
result=dict(schema='root-existing-receipt-descriptor-capture.v1',status='DESCRIPTOR_CAPTURE_ONLY_NOT_NEW_SCIENTIFIC_ACCEPTANCE',job_id=J,producer_job='13286',allocated_gpus=0,producer_terminal=p.stdout,allocation=c.stdout,receipts=items)
f=out/'descriptor_capture.json';f.write_text(json.dumps(result,indent=2)+'\n');f.chmod(0o444)
print(json.dumps(dict(job_id=J,receipts=items),indent=2))
