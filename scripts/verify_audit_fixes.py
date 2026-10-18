"""CPU-only acceptance of the audited corrections; never invokes a model."""
import argparse
from pathlib import Path
from ppiblocker.common import Run,load_run,record_file,read_json,atomic_json,runtime_provenance,require
from ppiblocker.pipeline import prepare
parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--old',required=True);parser.add_argument('--new',required=True)
a=parser.parse_args();root=Path(a.root)
run=Run(root,'05_audit_validation',[record_file(a.old),record_file(a.new)])
try:
    old=load_run(a.old,{'EVALUATION_COMPLETE'});new=load_run(a.new,{'EVALUATION_COMPLETE'})
    require(new.get('evaluation_mode')=='existing_predictions_cpu_reanalysis','WRONG_VALIDATION_INPUT','Expected CPU reanalysis')
    rows_old=read_json(old['outputs']['evaluation']['path'])['candidates']
    rows_new=read_json(new['outputs']['evaluation']['path'])['candidates']
    require([(c['id'],c['sequence']) for c in rows_old]==[(c['id'],c['sequence']) for c in rows_new],'CANDIDATES_CHANGED','Candidate identity changed')
    summaries=[]
    for before,after in zip(rows_old,rows_new):
        require(len(before['models'])==len(after['models'])==3,'MODELS_MISSING',after['id'])
        for b,m in zip(before['models'],after['models']):
            geometry=m['geometry'];actual=geometry['predicted_complex_interface']['minimum_distance']
            require('LOW_PAIR_IPTM' in m['reasons'],'UNEXPECTED_GATE_RESULT',after['id'])
            require(actual>=1.5 and 'SEVERE_TARGET_BINDER_CLASH' not in m['reasons'],'COLLISION_REGRESSION',after['id'])
            summaries.append({'candidate':after['id'],'model':m['index'],'actual_minimum_distance_A':actual,
                'reference_projection_minimum_distance_A':geometry['reference_projection_interface']['minimum_distance'],
                'old_severe_clash':'SEVERE_TARGET_BINDER_CLASH' in b['reasons'],
                'new_severe_clash':'SEVERE_TARGET_BINDER_CLASH' in m['reasons'],
                'native_interface_coverage':geometry['native_interface_coverage'],'remaining_reasons':m['reasons']})
    require(len(summaries)==12 and new['total_count']==4 and new['accepted_count']==0 and new['failed_count']==0,'ACCEPTANCE_MISMATCH','Expected complete 4x3 negative result')
    print('Verified all 12 reanalysed models',flush=True)
    runtime_provenance(run,root,['core','rfd','boltz'])
    print('All three actual environments match reviewed runtime locks',flush=True)
    prepared=prepare(root,root/'source/configs/mdm2_tp53_benchmark.yaml')
    pose=load_run(prepared,{'POSE_ACCEPTED'})
    require(read_json(pose['outputs']['pose']['path'])['source']['pdb']=='1YCR','WRONG_EXPERIMENTAL_POSE','Expected 1YCR')
    run.manifest['inputs'].append(record_file(prepared))
    out=run.path/'outputs/audit_fix_validation.json'
    atomic_json(out,{'old_evaluation':record_file(a.old),'new_evaluation':record_file(a.new),
                    'prepare_manifest':record_file(prepared),'candidate_count':4,'model_count':12,'accepted_count':0,
                    'removed_false_clash_labels':sum(x['old_severe_clash'] for x in summaries),
                    'models':summaries,'runtime_verified':['core','rfd','boltz'],
                    'new_model_inference':False,'experimental_blockade':False})
    run.output('validation',out)
    print(run.finish('AUDIT_FIXES_VALIDATED','software_corrections_with_cpu_reanalysis'))
except Exception as error:run.fail(error);raise
