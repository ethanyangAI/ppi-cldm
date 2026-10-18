#!/usr/bin/env python3
import json,hashlib,os,datetime
from pathlib import Path
R=Path('/lustre/users/u21111210118/projects/test9');S=R/'steps/20_screening_improvement'
def rec(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def load(p):return json.loads(Path(p).read_text())
def verify(v):assert rec(v['path'])==v or (rec(v['path'])['sha256']==v['sha256'] and rec(v['path'])['bytes']==v['bytes']);return Path(v['path'])
accp=R/'steps/17_control_calibration/outputs/acceptance_11941.json';sp=R/'steps/17_control_calibration/outputs/score_summary_11941.json'
ep=R/'steps/18_qualified_calibration/frozen/eligibility78.json';mp=R/'steps/17_control_calibration/inputs/msa_acceptance_v2.json'
ip=R/'steps/16_screening_evidence/runs/20261002T133856Z_11838/outputs/ipsae_source.json'
rf=R/'steps/14_control_qualification/rfd60/runs/20261003T031835Z_11903_qualification_v1_1/outputs/qualification_overlay60.json'
bc=R/'steps/14_control_qualification/bindcraft18/outputs/qualification_overlay.json'
ap=R/'steps/14_control_qualification/rfd60/raw/RFdiffusion_designs.zip'
lp=R/'steps/18_qualified_calibration/frozen/cross_family_sequence_leakage.json'
acc=load(accp);score=load(sp);elig=load(ep);msa=load(mp);ips=load(ip)
assert acc['status']=='ALL_1170_CONTROL_MODELS_VERIFIED' and acc['model_count']==1170
assert score['counts']=={'identities':78,'models':1170,'complete_confidence_identities':78,'missing_confidence_models':0}
for k in ['plan','acceptance','model_scores']:verify(score[k])
assert ips['revision']=='6174cf9e71cb1bd660cc805856a18c4871a6dec3'
for v in ips['files'].values():verify(v)
ids={e['id'] for e in elig['entries']};assert len(ids)==78 and ids=={a['condition']['condition_id'] for a in acc['accepted_conditions']}=={e['id'] for e in score['entries']}
files=[rec(p) for p in [accp,sp,ep,mp,ip,rf,bc,ap,lp,S/'PROTOCOL.md']]
files.append(rec(R/'source/rebuild/screening_transfer.py'))
for a in acc['accepted_conditions']:
 e=a['condition'];assert hashlib.sha256(e['target_sequence'].encode()).hexdigest()==e['target_sequence_sha256']
 assert len(a['models'])==15 and {(m['model'],m['seed']) for m in a['models']}=={(m,se) for m in range(1,6) for se in [1042,1043,1044]}
 for m in a['models']:
  verify(m['pdb']);verify(m['scores'])
for t in msa['targets'].values():verify(t['input'])
result=dict(status='ALL78_1170_INPUT_SCHEMA_VERIFIED_PROTOCOL_FROZEN',job_id=os.environ['SLURM_JOB_ID'],created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputs=files,source_inputs={'acceptance':rec(accp),'scores':rec(sp),'eligibility':rec(ep),'msa':rec(mp),'ipsae':rec(ip),'rf_overlay':rec(rf),'bc_overlay':rec(bc),'rf_archive':rec(ap),'leakage':rec(lp)},counts={'identities':78,'models':1170,'exact_target_constructs':len(msa['targets']),'main':sum(e['main_eligible'] for e in elig['entries']),'sensitivity':sum(e['screen_sensitivity_eligible'] for e in elig['entries'])},schema={'model_keys':list(acc['accepted_conditions'][0]['models'][0]),'score_model_keys':list(score['entries'][0]['models'][0]),'eligibility_keys':list(elig['entries'][0]),'targets':list(msa['targets'])},scientific_scope='DEVELOPMENT_ONLY_RETROSPECTIVE_CONDITIONED_BINDING_NOT_BLOCKADE')
out=S/'inputs'/'preparation_receipt.json'
out.parent.mkdir(parents=True,exist_ok=True)
with out.open('x') as f:json.dump(result,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
print(json.dumps({k:result[k] for k in ['status','job_id','counts','schema']},indent=2),flush=True)

