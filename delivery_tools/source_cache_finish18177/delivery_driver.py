#!/usr/bin/env python3
"""Root-owned CPU driver for the existing final delivery APIs. No automatic sbatch.
Modes resume-private/readback/finish. Requests/results are late archive controls.
"""
import argparse,importlib.util,json,os,subprocess,sys
from pathlib import Path
import request_assembler as a
R=Path('/lustre/users/u21111210118/projects/test9');S=R/'steps/24_benchmark_delivery'
CORE=R/'env/core/bin/python';D=Path(__file__).absolute().parent
SOFTWARE={'path':str(S/'runs/final_composer_operational_provenance_contracts_18110/acceptance.json'),'bytes':31799,'sha256':'bc6d2500d204a14e3815744a2073e2591862c64352cb025239ec091e60e5217c'}
MAIN=S/'frozen/final_delivery_composer_v7_operational_source_provenance_18110/code/final_delivery_composer.py'
BBF={'path':str(R/'steps/23_common_review/runs/downstream_frozen_13119/bbf110_review_13125/acceptance.json'),'bytes':828668,'sha256':'c19cc9c6cb15e32f8c7a660afc217ed856760bd6a3474ae7f40f66f0bc50f4db'}
META_SOFTWARE={'path':str(S/'runs/restored_common13460_metadata_software_13558/acceptance.json'),'bytes':19295,'sha256':'46961d96044333116e7dd829d364533be1d5815c147fa0df7819ffcd3baee5d7'}
COST_SOFTWARE={'path':str(S/'runs/restored_root298_cost_software_14692/acceptance.json'),'bytes':12577,'sha256':'2c73a47c7696fa78138a7d5fe810c13b5ac7b37e8ca74f9098958198c759f9dd'}
RESUME_PASS='ACTUAL_CURRENT_SOURCE_AND_REAL_STRICT_INDEX_COMPATIBLE_ARCHIVE_PUBLICATION_ISOLATED_RESTORE_PENDING'

def need(v,msg):
 if not v:raise ValueError(msg)
def load_main():
 need(os.environ.get('SLURM_JOB_ID','').isdigit() and os.environ.get('CUDA_VISIBLE_DEVICES')=='' and os.environ.get('JAX_PLATFORMS')=='cpu' and 'PYTHONPATH'not in os.environ,'Owned CPU isolation required')
 sys.path.insert(0,str(MAIN.parent));sys.path.insert(1,str(S/'frozen/history_policy_13223/code'))
 spec=importlib.util.spec_from_file_location('final_delivery_composer',MAIN);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 allocation=m.cpu();m.software(SOFTWARE,m.sources());return m,allocation
def output(m,p,raw):
 p=m.safe(p)
 with p.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
 return m.rec(p)
def run(m,out,name,argv,stdin=None):
 result=subprocess.run(argv,input=stdin,capture_output=True)
 stdout=output(m,out/(name+'.stdout'),result.stdout);stderr=output(m,out/(name+'.stderr'),result.stderr)
 record=m.dump(out/(name+'.command.json'),dict(argv=argv,returncode=result.returncode,stdout=stdout,stderr=stderr))
 need(result.returncode==0,name+' failed; full raw outputs retained')
 rows=[json.loads(line)for line in result.stdout.decode().splitlines()if line.strip().startswith('{')]
 need(rows,name+' printed no actual JSON descriptor');return rows[-1],record

def resume_private(m,q,out,allocation):
 rr=m.rec(q['resume_request_path'])
 if q.get('resume_request_sha256')is not None:need(rr['sha256']==q['resume_request_sha256'],'Actual resume request SHA differs')
 request=json.loads(m.verify(rr,True).read_bytes())
 printed,resume_command=run(m,out,'resume',[str(CORE),'-B',str(D/'source_resume_control.py'),rr['path']])
 need(printed['status']==RESUME_PASS and printed['actual_job_id']==os.environ['SLURM_JOB_ID'] and printed['current_root_index_only']is True and printed['isolated_restore_accepted']is False,'Actual same-CPU resume acceptance required')
 accepted=json.loads(m.verify(printed['acceptance'],True).read_bytes());binding=json.loads(m.verify(printed['source_context_binding'],True).read_bytes())
 need(accepted['source_context']==binding and accepted['status']==RESUME_PASS,'Whole actual resume binding differs')
 rows=json.loads(m.verify(printed['source_rows'],True).read_bytes());need(type(rows)is list and rows,'Entire qualified Source rows required')
 compatibility=dict(acceptance=printed['acceptance'],current_index_manifest=accepted['current_index_manifest'],current_index_aliases=accepted['current_index_aliases'])
 read=lambda r:m.verify(r,True).read_bytes()
 common_r=next(x['gate']['receipt']for x in read_json(m,binding['producer']['acceptance'])['module_gates']if x['role']=='formal_common_review')
 cfg=q.get('common_config') or a.locate_common_config_on_CPU(read,common_r)
 controller={'qualification':dict(m.CONTROLLER_AMENDMENT_ACCEPTANCE),'journal4':m.rec(m.CONTROLLER_JOURNAL4_PATH)}
 anchors=a.existing_anchor_inputs(read,binding,q['phase_id'],m.rec(R/'00_admin/ACTIVE.json'),m.rec(S/'code/native_msa_history_policy.json'),m.rec(R/'steps/20_screening_improvement/acceptance.json'),BBF,cfg,controller)
 fixed=a.fixed_inputs(read,binding,anchors);fixed_r=m.dump(out/'fixed_delivery_inputs.json',fixed)
 alias_r=m.dump(out/'plan_alias_index.json',fixed['plan_alias_index'])
 private=dict(source_binding=binding,current_compatibility_inputs=compatibility,approved_source_rows=rows,bundle_path=q['bundle_path'],export_dir=q['export_dir'])
 code="import json,runpy,sys;runpy.run_path(sys.argv[1],init_globals={'ROOT_BIND_FINAL_PRIVATE_COMMIT_AND_EXPORT':json.load(sys.stdin)})"
 p,private_command=run(m,out,'private_git',[str(CORE),'-B','-c',code,str(D/'private_git_control.py')],json.dumps(private,allow_nan=False).encode())
 need(p['source_binding']==binding and p['current_compatibility_inputs']==compatibility and p['committed_required_source_rows']==len(rows),'Actual full-row private commit binding differs')
 return m.dump(out/'acceptance.json',dict(status='ACTUAL_PRIVATE_SOURCE_COMMIT_BUNDLE_AND_EXPORT_PUBLIC_READBACK_PENDING',allocation=allocation,software=SOFTWARE,resume=printed,resume_command=resume_command,private_command=private_command,private=p,source_context_binding=printed['source_context_binding'],fixed_inputs=fixed_r,plan_alias_index=alias_r,public_branch=q['public_branch'],ACTIVE_changed=False))
def read_json(m,r):return json.loads(m.verify(r,True).read_bytes())

def readback(m,q,out,allocation):
 private_r=q['private_acceptance'];prior=read_json(m,private_r);p=prior['private'];captures=[]
 helper=m.export_api()
 manifest=read_json(m,p['export_manifest'])
 for i,item in enumerate(q['write_captures']):
  spec=dict(item['capture_spec']);raw_path=item['raw_output_path']
  if 'actual_tool_output_path'in spec:need(spec.pop('actual_tool_output_path')==raw_path,'Actual raw tool path differs')
  spec['actual_tool_output']=m.rec(raw_path);m.verify(spec['actual_tool_output'],True)
  if spec['operation']in('create_blob','create_tree'):
   name=spec['export_payload_name'];row=next(x for x in manifest['object_payloads']if x['path']==name)
   expected={k:row[k]for k in('path','bytes','sha256')};expected['path']=str(Path(p['export_manifest']['path']).parent/name)
   need(m.rec(expected['path'])==expected,'Actual exported payload bytes differ before capture');spec['export_payload_receipt']=expected
  captures.append(m.dump(out/('write_capture_%05d.json'%i),spec))
 export={'export_dir':str(Path(p['export_manifest']['path']).parent),'manifest':p['export_manifest']}
 req=a.readback_request(export,p['private_commit'],p['source_bundle'],prior['public_branch'],captures);req_r=m.dump(out/'readback_request.json',req)
 runout=out/'public_readback';runout.mkdir(exist_ok=False)
 result=helper.readback(req,m.sources(),SOFTWARE,req_r,runout,allocation)
 actual=read_json(m,result);need(actual['private_commit']==p['private_commit'],'Public readback private commit mismatch')
 return m.dump(out/'acceptance.json',dict(status='ACTUAL_PUBLIC_READBACK_CAPTURED_TERMINAL_QUALIFICATION_NEXT',allocation=allocation,private_acceptance=private_r,request=req_r,remote_readback=result,ACTIVE_changed=False))

def metadata_command(package,restore_root,out):
 return [str(CORE),'-B',str(S/'frozen/restored_common13460_metadata_verifier_v1_13558/code/checker.py'),'verify','--software',META_SOFTWARE['path'],'--software-sha',META_SOFTWARE['sha256'],'--package',package['path'],'--package-sha',package['sha256'],'--restore-root',restore_root,'--out',out]
def cost_command(package,restore_root,raw,metadata,out):
 return [str(CORE),'-B',str(S/'frozen/restored_root298_cost_verifier_v1_rev1_14692/code/checker.py'),'verify','--software',COST_SOFTWARE['path'],'--software-sha',COST_SOFTWARE['sha256'],'--package',package['path'],'--package-sha',package['sha256'],'--restore-root',restore_root,'--out',out,'--raw-restore',raw['path'],'--raw-restore-sha',raw['sha256'],'--metadata-restore',metadata['path'],'--metadata-restore-sha',metadata['sha256']]

def finish(m,q,out,allocation):
 if 'completed_finish'in q:return finish_after_metadata(m,q,out,allocation)
 prior=read_json(m,q['private_acceptance']);p=prior['private'];fixed=read_json(m,prior['fixed_inputs']);binding=read_json(m,prior['source_context_binding'])
 rb=read_json(m,q['readback_acceptance']);need(rb['private_acceptance']==q['private_acceptance'],'Readback/private input fork')
 export=a.public_export(lambda r:m.verify(r,True).read_bytes(),rb['remote_readback'],p['private_commit'],p['source_bundle'])
 plan=a.scope_plan(fixed,export,rb['remote_readback']);plan_r=m.dump(out/'terminal_scope_plan.json',plan)
 req=a.inventory_request(plan,plan_r);req_r=m.dump(out/'inventory_request.json',req)
 invout=out/'inventory';invout.mkdir(exist_ok=False)
 class Args:pass
 args=Args();args.request=req_r;args.software=SOFTWARE
 inventory=m.inventory(args,invout)
 extra=list(q.get('evidence_seeds',[]))+[plan_r,META_SOFTWARE,COST_SOFTWARE]
 compose=a.compose_request(fixed,binding,export,p['private_commit'],p['source_bundle'],[inventory],[prior['plan_alias_index']]+q.get('alias_indices',[]),extra,q.get('native_resource_closures',[]))
 compose_r=m.dump(out/'compose_request.json',compose);args.request=compose_r
 cout=out/'compose';cout.mkdir(exist_ok=False);accepted_r=m.compose(args,cout);accepted=read_json(m,accepted_r)
 adapter=m.load('root_final_delivery_archive',MAIN.parent/'relative_archive_restore.py')
 pkgout=Path(q['package_out']);adapter.package(accepted['validation'],pkgout,q.get('part_mib',512));package=m.rec(pkgout/'packaging_receipt.json')
 core=m.load('root_final_delivery_core',m.LIB/'delivery_core_v2.py');root=str(m.safe(q['restore_root']));core.extract(package['path'],root)
 raw,raw_r=adapter.restore(package,root,str(Path(root)/'recomputed'))
 need(raw['status']=='INDEPENDENT_RESTORE_RAW_CONTENT_RECOMPUTATION_ACCEPTED','Actual indexed raw restore required')
 return m.dump(out/'acceptance.json',dict(status='ACTUAL_FINAL_PACKAGE_AND_ISOLATED_RAW_RESTORE_METADATA_COST_GATES_PENDING',allocation=allocation,private_acceptance=q['private_acceptance'],readback_acceptance=q['readback_acceptance'],fixed_inputs=prior['fixed_inputs'],inventory=inventory,compose=accepted_r,validation=accepted['validation'],source_release=accepted['source_release'],package=package,restore_root=root,raw_restore=raw_r,metadata_verify_argv=metadata_command(package,root,str(Path(root)/'metadata_common13460')),metadata_verify_job_name='test9_restored_common13460_metadata',cost_verify_job_name='test9_restored_root298_cost',ACTIVE_changed=False))

def finish_after_metadata(m,q,out,allocation):
 f=read_json(m,q['completed_finish']);package=f['package'];root=f['restore_root'];meta=read_json(m,q['metadata_restore'])
 need(meta['status']=='RESTORED_COMMON13460_AND_J6_EXACT_INDEX_METADATA_CONTENT_ACCEPTED_NOT_SCIENCE' and meta['production_restore_verified']is True and meta['package_control']==package,'Actual same-package metadata verification required')
 marker=read_json(m,meta['hash_extraction_control']);need(marker['restore_root']==root and marker['package']==package,'Metadata proof belongs to another restore root')
 if 'cost_restore'not in q:
  return m.dump(out/'acceptance.json',dict(status='ACTUAL_METADATA_GATE_ACCEPTED_ROOT298_COST_NEXT',completed_finish=q['completed_finish'],metadata_restore=q['metadata_restore'],cost_verify_job_name='test9_restored_root298_cost',cost_verify_argv=cost_command(package,root,f['raw_restore'],q['metadata_restore'],str(Path(root)/'root298_cost')),ACTIVE_changed=False))
 cost=read_json(m,q['cost_restore'])
 need(cost['status']=='RESTORED_ROOT298_GPU_COST_INDEPENDENT_RECOMPUTATION_ACCEPTED_NOT_SCIENCE' and cost['production_restore_verified']is True and cost['package_control']==package and cost['restore_root']==root and cost['previous_full_RAW_restore']==f['raw_restore'] and cost['previous_13460_metadata_restore']==q['metadata_restore'],'Actual same-package/root full RAW/metadata/Root298 chain required')
 fixed=read_json(m,f['fixed_inputs']);phase=dict(phase_id=fixed['phase_id'],status='MATCHED_BENCHMARK_ACCEPTED_COMPUTATIONAL_ONLY',scientific_scope='COMPUTATIONAL_ONLY',delivery_validation=f['validation'],independent_restore=f['raw_restore'],human_report=fixed['report_binding']['report'],source_release=f['source_release'],package=package,restored_common_metadata=q['metadata_restore'],restored_Root298_cost=q['cost_restore'],experimental_binding_or_blockade=False,clinical_efficacy=False)
 phase_r=m.dump(out/'phase.json',phase)
 result=dict(status='ACTUAL_ARCHIVE_ISOLATED_RESTORE_ALL_EXISTING_GATES_READY_FOR_ROOT_ACTIVE_PUBLICATION',phase=phase_r,package=package,restore_root=root,validation=f['validation'],raw_restore=f['raw_restore'],metadata_restore=q['metadata_restore'],cost_restore=q['cost_restore'],ACTIVE_changed=False)
 if q.get('publish_ACTIVE')is True:
  core=m.load('root_final_active_publish',m.LIB/'delivery_core_v2.py');publication=core.publish(f['validation']['path'],f['raw_restore']['path'],phase_r['path'],str(R/'00_admin/ACTIVE.json'));result.update(status='ACTUAL_COMPLETE_DELIVERY_AND_SINGLE_ACTIVE_PUBLISHED',publication=publication,ACTIVE_changed=True)
 return m.dump(out/'acceptance.json',result)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('resume-private','readback','finish'));parser.add_argument('--request',required=True);parser.add_argument('--request-sha256');parser.add_argument('--out',required=True);args=parser.parse_args()
 m,allocation=load_main();rr=m.rec(args.request)
 if args.request_sha256 is not None:need(rr['sha256']==args.request_sha256,'Root actual request SHA differs')
 q=read_json(m,rr);need(q.get('root_owned')is True and q.get('schema')=='root-final-delivery-driver-request.v1','Explicit Root driver request required')
 out=m.safe(args.out);out.mkdir(parents=True,exist_ok=False)
 m.dump(out/'actual_driver_input.json',dict(request=rr,mode=args.mode,allocation=allocation,executing_driver=m.rec(__file__),assembler=m.rec(D/'request_assembler.py')))
 try:
  r={'resume-private':resume_private,'readback':readback,'finish':finish}[args.mode](m,q,out,allocation);print(json.dumps(r,allow_nan=False))
 except BaseException as e:
  m.dump(out/'typed_incomplete.json',dict(status='FINAL_DELIVERY_INCOMPLETE_ACTUAL_OUTPUTS_PRESERVED_NO_RETRY',mode=args.mode,error_type=type(e).__name__,error=str(e),request=rr));raise
if __name__=='__main__':main()
