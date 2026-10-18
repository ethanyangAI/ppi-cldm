#!/usr/bin/env python3
"""Request assembly for the existing CPU delivery APIs. No scheduler, Git,
network, filesystem write, science calculation, or Project import occurs here.
read_control is supplied by the owned CPU driver and reads only the receipts
selected below from already authenticated controls. Returned requests must be
materialized by that driver; their actual CPU receipts are subsequent inputs.
"""
import copy,json,re
from pathlib import PurePosixPath as P

R=P('/lustre/users/u21111210118/projects/test9')
S=R/'steps/24_benchmark_delivery'
FIRST4=('screening_content','bbf_input_sensitivity_content','target_identity','runtime_gpu_pilot')
SOURCE_ROLES=('formal13260_terminal_v3','native74_cache_catalog','native74_cache_binding',
 'reference_free_e2e','formal_common_review','independent_statistics','scientific_report',
 'final_delivery_tools','default_workflow_integration')
BINDING_KEYS={'schema','root_owned','producer','semantics_source','stage_acceptance',
 'late_source_publication','transport_aliases','additional_control_receipts','source_routes',
 'operational_source_provenance','partial_cache_software_authority'}
READBACK_STATUS='ACTUAL_PUBLIC_REF_COMMIT_FULL_TREE_AND_WRITE_RESPONSES_CPU_READ_BACK'
INVENTORY_STATUS='EXPLICIT_TERMINAL_FILE_UNIVERSE_CPU_SEALED_NOT_ARCHIVE_ACCEPTANCE'

def need(v,message):
 if not v:raise ValueError(message)
def clone(v):return copy.deepcopy(v)
def receipt(r):
 need(type(r)is dict and {'path','bytes','sha256'}<=set(r),'Actual CPU receipt required')
 p=r['path'];need(type(p)is str and p.startswith(str(R)+'/') and str(P(p))==p and '..'not in P(p).parts,'Exact authority path required')
 need(type(r['bytes'])is int and r['bytes']>=0 and type(r['sha256'])is str and re.fullmatch('[0-9a-f]{64}',r['sha256']),'Exact CPU byte identity required')
 return {k:r[k]for k in('path','bytes','sha256')}
def unique(rows):
 out=[];seen=set()
 for r in rows:
  r=receipt(r);k=(r['path'],r['bytes'],r['sha256'])
  if k not in seen:seen.add(k);out.append(r)
 return out
def read_json(read_control,r,limit=20*1024*1024):
 r=receipt(r);need(r['bytes']<=limit,'Bounded named control required')
 # The CPU driver verifies this exact receipt using the existing m.verify.
 raw=read_control(r);need(type(raw)is bytes and len(raw)==r['bytes'],'Whole exact control bytes required')
 def pairs(rows):
  o={}
  for k,v in rows:need(k not in o,'Duplicate JSON key');o[k]=v
  return o
 return json.loads(raw,object_pairs_hook=pairs)
def gate(read_control,r,status=None,extra=None):
 o=read_json(read_control,r);need(type(o)is dict and type(o.get('status'))is str,'Actual terminal control status required')
 if status is not None:need(o['status']==status,'Accepted terminal status changed')
 expect={'status':o['status']}
 if extra:
  for k,v in extra.items():need(o[k]==v,'Accepted gate content differs');expect[k]=clone(v)
 return {'receipt':receipt(r),'expect':expect},o

def fixed_inputs(read_control,source_context,anchors):
 """No synthetic old request. Derive named fields from A/CA and their controls.
 anchors contains six EXISTING authorities, never guessed paths or new tests:
 previous_active, historical_provenance_policy, first4_gates, common_config,
 controller_metadata_amendment, phase_id. The four expect objects are copied
 from their actual accepted control records, with status checked here.
 """
 need(type(source_context)is dict and set(source_context)==BINDING_KEYS and source_context['schema']=='finite-final-source-delivery-context.v4' and source_context['root_owned']is True,'Actual closed Fv4 binding required')
 need(set(anchors)=={'previous_active','historical_provenance_policy','first4_gates','common_config','controller_metadata_amendment','phase_id'},'Six existing Root anchors required')
 need(type(anchors['phase_id'])is str and re.fullmatch('[A-Za-z0-9_-]+',anchors['phase_id']),'Explicit final phase identity required')
 prod=source_context['producer'];need(set(prod)=={'acceptance','context_adapter_acceptance','source_inclusion','source_closure'},'Whole original producer binding required')
 a=read_json(read_control,prod['acceptance']);ca=read_json(read_control,prod['context_adapter_acceptance'])
 need(a['schema']=='final-source-closure-acceptance.v3' and a['status']=='FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED' and a['source_issues']==0,'Accepted original Source audit required')
 need(a['source_inclusion']==prod['source_inclusion'] and a['source_closure']==prod['source_closure'] and ca['actual_new_library_acceptance']==prod['acceptance'],'Original A/CA/I/C identities changed')
 plan=read_json(read_control,a['explicit_plan']);need(plan['schema']=='final-source-closure-plan.v3' and plan['root_owned']is True and plan['formal_array_job_id']=='13260','Actual accepted nine-role plan required')
 modules={m['role']:m for m in plan['modules']};need(len(modules)==9 and set(modules)==set(SOURCE_ROLES),'Original nine Source roles changed')
 need(a['module_gates']==[{'role':m['role'],'gate':m['gate']}for m in plan['modules']],'A/plan accepted role gates differ')
 def module(role):
  r=modules[role]['gate'];return gate(read_control,r['receipt'],r['expected_status'])
 _,formal_outer=module('formal13260_terminal_v3');collection_r=receipt(formal_outer['collection']);collection=read_json(read_control,collection_r)
 need(collection['schema']=='formal_postprocess_collection.v2' and collection['status']=='FORMAL_ALLOCATION_NATIVE_AND_COHORT_CLOSURE_ACCEPTED' and collection['array_job_id']=='13260','Accepted formal collection changed')
 common_gate,common=module('formal_common_review');report_gate,qa=module('scientific_report')
 need(qa['common_successor']==common_gate['receipt'] and qa['statistics']==common['statistics'] and qa['n_fixed_cohort_engine_rows']==112 and qa['n_primary_targets']==6 and qa['scientific_scope']=='COMPUTATIONAL_ONLY' and qa['experimental_binding_or_blockade']is False,'Report/common112 computational scope changed')
 cost_r=receipt(qa['root_gpu_cost']);cost_gate,cost=gate(read_control,cost_r,'ROOT_CURRENT_GPU_SUBMISSION_UNIVERSE_AND_TERMINAL_COST_CPU_ACCEPTED',{'complete_root_gpu_submission_universe':True,'allocated_failure_before_manifest_cost_retained':True})
 common_config=read_json(read_control,anchors['common_config']);need(common_config['producer_acceptance']==common['common_acceptance']['path'],'Existing Common configuration differs')
 gates={};first_controls={}
 need(type(anchors['first4_gates'])is dict and set(anchors['first4_gates'])==set(FIRST4),'Exactly four original scientific gate authorities required')
 for name in FIRST4:
  g=clone(anchors['first4_gates'][name]);o=read_json(read_control,g['receipt']);need(type(g['expect'])is dict and type(g['expect'].get('status'))is str,'Actual original expected status required')
  for dotted,wanted in g['expect'].items():
   value=o
   for part in dotted.split('.'):value=value[part]
   need(value==wanted,'Original scientific gate content changed: '+name)
  gates[name]=g;first_controls[name]=o
 gates['generation_accounting']=gate(read_control,collection['files']['accounting'])[0]
 gates['common_review_content']=gate(read_control,common['common_acceptance'],'COMMON_REVIEW_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY',{'independent_experimental_validation':False})[0]
 gates['independent_score_recomputation']=gate(read_control,common['independent_common'])[0]
 gates['scientific_report_content']=report_gate
 default_gate,default=module('default_workflow_integration')
 mapper_r=receipt(ca['mapper_software_acceptance']);mapper=read_json(read_control,mapper_r)
 need(mapper_r==default['accepted_prerequisites']['context_mapper']['receipt'],'Default/current mapper identity differs')
 relative={'mapper_acceptance':mapper_r,'base_acceptance':mapper['base_acceptance'],
  'mapping':mapper['relative_receipt_context_mapping'],'historical_mapping':mapper['external_historical_receipt_context_mapping'],
  'current_recovered_mapping':mapper['current_recovered_relative_receipt_context_mapping'],'archive_member_mapping':mapper['archive_member_receipt_context_mapping']}
 for k in('mapping','historical_mapping','current_recovered_mapping','archive_member_mapping'):
  pk={'mapping':'relative_receipt_context_mapping','historical_mapping':'external_historical_receipt_context_mapping','current_recovered_mapping':'current_recovered_relative_receipt_context_mapping','archive_member_mapping':'archive_member_receipt_context_mapping'}[k]
  need(relative[k]==plan[pk],'Original plan/mapper field differs: '+k)
 previous=read_json(read_control,anchors['previous_active']);need(all(k in previous for k in('current_phase','reconstruction','human_report')),'Whole prior ACTIVE authority required')
 read_json(read_control,anchors['historical_provenance_policy'])
 amendment=clone(anchors['controller_metadata_amendment'])
 need(amendment['qualification']['path']==str(R/'steps/25_reference_free_e2e/runs/controller_metadata_amendment_13315/acceptance.json') and amendment['journal4']['path']==str(S/'submissions/root_gpu_journal/0004_controller_metadata_amendment_13315.json'),'Existing controller13315/journal4 identities required')
 aliases=[]
 for row in plan['aliases']:
  original=receipt(row['logical']);archived=receipt(row['physical']);need((original['bytes'],original['sha256'])==(archived['bytes'],archived['sha256']),'Original plan alias changes bytes')
  aliases.append({'original':original,'archived':archived,'status':'READONLY_BYTE_IDENTICAL_ALIAS'})
 ref_gate,_=module('reference_free_e2e')
 evidence=unique([default_gate['receipt'],ref_gate['receipt'],cost_r,receipt(a['explicit_plan']),receipt(ca['request'])]+[m['gate']['receipt']for m in plan['modules']])
 return {'phase_id':anchors['phase_id'],'previous_active':receipt(anchors['previous_active']),
  'historical_provenance_policy':receipt(anchors['historical_provenance_policy']),'gates':gates,
  'common_successor':common_gate['receipt'],'common_config':receipt(anchors['common_config']),
  'formal_collection':collection_r,'root_gpu_cost':cost_r,'report_binding':{'report':receipt(qa['report'])},
  'relative_context':relative,'controller_metadata_amendment':amendment,'evidence_seeds':evidence,
  'source_release_fixed':{'final_source_acceptance':receipt(prod['acceptance']),'source_inclusion':receipt(prod['source_inclusion']),
   'derived_pipeline_qualification':receipt(a['mandatory_derived_pipeline_qualification']['acceptance'])},
  'plan_alias_index':{'aliases':aliases},'source_module_gates':clone(a['module_gates']),
  'scope_roots':{'formal_generation':str(P(collection['run_root'])),'common_raw':str(P(common['common_acceptance']['path']).parent),
   'native_raw':str(P(common['source']['operative']['native']['path']).parent),
   'bbf_raw':str(P(plan['context_parent_seeds'][0]['path']).parent),
   'screening':str(P(first_controls['screening_content']['manifest']['path']).parent),'reports':str(P(qa['report']['path']).parent)},
  'scope_gates':{'formal_generation':gate(read_control,collection_r)[0],'common_raw':common_gate,
   'native_raw':common_gate,'bbf_raw':gates['bbf_input_sensitivity_content'],
   'screening':gates['screening_content'],'reports':report_gate}}

def readback_request(export,private_commit,private_bundle,branch,write_response_captures):
 need(type(export)is dict and set(export)=={'export_dir','manifest'},'Actual export directory/manifest required')
 need(receipt(export['manifest'])['path']==str(P(export['export_dir'])/'export_manifest.json'),'Actual export manifest path differs')
 need(re.fullmatch('[0-9a-f]{40}',private_commit) and re.fullmatch('[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*',branch),'Actual private commit and explicit public branch required')
 need(type(write_response_captures)is list and write_response_captures,'Actual GitHub write response captures required')
 return {'schema':'github-export-readback-request.v1','root_owned':True,'repository_full_name':'ethanyangAI/ppi-cldm',
  'authorize_public_GET_and_exact_remote_fetch':True,'branch':branch,'source_bundle':receipt(private_bundle),
  'export':clone(export),'write_response_captures':unique(write_response_captures)}

def public_export(read_control,readback_receipt,private_commit,private_bundle):
 q=read_json(read_control,readback_receipt)
 need(q['schema']=='github-public-ref-commit-tree-readback.v1' and q['status']==READBACK_STATUS and q['root_owned']is True and q['repository_full_name']=='ethanyangAI/ppi-cldm','Actual public readback required')
 need(q['private_commit']==private_commit and q['private_source_bundle']==private_bundle and q['fetched_ref']=='refs/remotes/root-qualified/'+q['branch'],'Private bundle/public readback linkage differs')
 return {'export_dir':str(P(q['manifest']['path']).parent),'manifest':receipt(q['manifest']),
  'api_responses':receipt(q['normalized_API_responses']),'published_ref':q['fetched_ref'],'remote_readback':receipt(readback_receipt)}

def scope_plan(fixed,export,readback_receipt):
 roots=dict(fixed['scope_roots'],source_export=export['export_dir'])
 ordered=('formal_generation','common_raw','native_raw','bbf_raw','screening','reports','source_export')
 need(set(roots)==set(ordered),'Exactly seven mandatory terminal evidence roles required')
 rows=[]
 for role in ordered:
  root=roots[role];need(type(root)is str and root.startswith(str(R)+'/') and str(P(root))==root and '..'not in P(root).parts,'Exact terminal scope path required')
  need(root!=str(R) and not P(root).is_relative_to(R/'source') and not P(root).is_relative_to(R/'env'),'Whole project/source/runtime inventory forbidden')
  g=fixed['scope_gates'][role]if role!='source_export'else {'receipt':receipt(readback_receipt),'expect':{'status':READBACK_STATUS}}
  rows.append({'root':root,'role':role,'terminal_gate':clone(g)})
 for i,left in enumerate(rows):
  for right in rows[i+1:]:need(not(P(left['root']).is_relative_to(P(right['root']))or P(right['root']).is_relative_to(P(left['root']))),'Overlapping terminal inventory roots')
 return {'schema':'root-final-delivery-terminal-scope-plan.v1','root_owned':True,'formal_array_job_id':'13260',
  'scientific_scope':'COMPUTATIONAL_ONLY','directories':rows,'accepted_source_nine_role_gates':clone(fixed['source_module_gates'])}

def inventory_request(plan,actual_scope_plan_receipt):
 r=receipt(actual_scope_plan_receipt)
 return {'schema':'final-delivery-inventory-request.v1','root_owned':True,'formal_array_job_id':'13260','scientific_scope':'COMPUTATIONAL_ONLY',
  'directories':[dict(clone(row),root_binding={'receipt':r,'field':'directories.'+str(i)+'.root'})for i,row in enumerate(plan['directories'])]}

def compose_request(fixed,source_context,export,private_commit,private_bundle,terminal_inventories,alias_indices,evidence_seeds=(),native_resource_closures=()):
 need(terminal_inventories,'Actual completed inventory receipt required')
 need(type(source_context)is dict and set(source_context)==BINDING_KEYS,'Whole actual finite binding required')
 src=dict(clone(fixed['source_release_fixed']),expected_commit=private_commit,source_bundle=receipt(private_bundle),github=clone(export))
 need(source_context['producer']['acceptance']==src['final_source_acceptance'] and source_context['producer']['source_inclusion']==src['source_inclusion'],'Final finite binding/original release graph fork')
 return {'schema':'final-delivery-compose-request.v1','root_owned':True,'formal_array_job_id':'13260','scientific_scope':'COMPUTATIONAL_ONLY',
  'phase_id':fixed['phase_id'],'previous_active':clone(fixed['previous_active']),'gates':clone(fixed['gates']),
  'common_successor':clone(fixed['common_successor']),'common_config':clone(fixed['common_config']),
  'formal_collection':clone(fixed['formal_collection']),'root_gpu_cost':clone(fixed['root_gpu_cost']),
  'report_binding':clone(fixed['report_binding']),'relative_context':clone(fixed['relative_context']),
  'controller_metadata_amendment':clone(fixed['controller_metadata_amendment']),
  'historical_provenance_policy':clone(fixed['historical_provenance_policy']),
  'source_context':clone(source_context),'source_release':src,'terminal_inventories':unique(terminal_inventories),
  'alias_indices':unique(alias_indices),'evidence_seeds':unique(fixed['evidence_seeds']+list(evidence_seeds)),
  'native_resource_closures':unique(native_resource_closures)}

def cpu_argv(entry,mode,request_receipt,software_receipt,out):
 rr=receipt(request_receipt);sw=receipt(software_receipt)
 need(mode in('inventory','compose','readback'),'Existing CPU mode required')
 return [str(R/'env/core/bin/python'),'-B',entry,mode,'--request',rr['path'],'--request-sha256',rr['sha256'],
  '--software',sw['path'],'--software-sha256',sw['sha256'],'--out',out]

def archive_restore_argv(source_directory,validation,package,package_out,restore_root,restore_out):
 validation=receipt(validation);package=receipt(package);d=P(source_directory);python=str(R/'env/core/bin/python')
 return {'package':[python,'-B',str(d/'relative_archive_restore.py'),'package','--validation',validation['path'],'--validation-sha256',validation['sha256'],'--out',package_out],
  'extract':[python,'-B',str(S/'frozen/history_policy_13223/code/delivery_core_v2.py'),'extract','--package',package['path'],'--restore-root',restore_root],
  'isolated_restore':[python,'-B',str(d/'relative_archive_restore.py'),'restore','--package',package['path'],'--package-sha256',package['sha256'],'--restore-root',restore_root,'--out',restore_out]}


def existing_anchor_inputs(read_control,source_context,phase_id,previous_active,historical_policy,screening_receipt,bbf_sensitivity_receipt,common_config,controller_binding):
 """Complete the six anchors from actual existing controls; no date/job inference.
 Root supplies the existing ACTIVE/policy/control tuples. Frozen plan authority
 determines the input-identity and real-GPU pilot gates, never a CPU-only handoff.
 """
 a=read_json(read_control,source_context['producer']['acceptance'])
 mods={m['role']:m for m in a['module_gates']}
 formal=read_json(read_control,mods['formal13260_terminal_v3']['gate']['receipt'])
 collection=read_json(read_control,formal['collection'])
 frozen_plan=read_json(read_control,collection['plan']);protocol=frozen_plan['protocol']
 first={
  'screening_content':gate(read_control,screening_receipt,'ALL78_1170_SCREENING_IMPROVEMENT_CONTENT_ACCEPTED_DEVELOPMENT_ONLY')[0],
  'bbf_input_sensitivity_content':gate(read_control,bbf_sensitivity_receipt)[0],
  'target_identity':gate(read_control,protocol['input_bridge'])[0],
  'runtime_gpu_pilot':gate(read_control,protocol['engineering_acceptance'])[0]}
 return {'phase_id':phase_id,'previous_active':receipt(previous_active),
  'historical_provenance_policy':receipt(historical_policy),'first4_gates':first,
  'common_config':receipt(common_config),'controller_metadata_amendment':clone(controller_binding)}

def locate_common_config_on_CPU(read_control,common_successor_receipt):
 """Follow only pinned JSON config descriptors in the accepted inner Common
 control; no directory walk or scientific payload is performed. Return exactly
 one actual config whose producer_acceptance names the accepted inner control.
 """
 common=read_json(read_control,common_successor_receipt)
 inner=read_json(read_control,common['common_acceptance'])
 rows=[]
 def collect(value,trail=()):
  if type(value)is dict:
   if {'path','bytes','sha256'}<=set(value) and P(value['path']).suffix=='.json' and 'config' in P(value['path']).name.lower():rows.append((trail,receipt(value)))
   for k,v in value.items():collect(v,trail+(str(k),))
  elif type(value)is list:
   for i,v in enumerate(value):collect(v,trail+(str(i),))
 collect(inner);pins=unique([r for trail,r in rows]);need(0<len(pins)<=16,'A bounded explicit Common config descriptor is required')
 matches=[]
 for r in pins:
  obj=read_json(read_control,r)
  if type(obj)is dict and obj.get('producer_acceptance')==common['common_acceptance']['path']:
   need(all(k in obj for k in('result','analysis_plan','membership','official_ipsae','msa_roundtrip_source','colabfold_cpu_python')),'Complete accepted Common restore configuration required')
   matches.append(r)
 need(len(matches)==1,'Exactly one accepted Common recomputation config required')
 return matches[0]
