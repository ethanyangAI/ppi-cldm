import copy
import json
from pathlib import Path
import numpy as np
import pytest
import yaml
from ppiblocker import pipeline,backends,common
from ppiblocker.common import Run,record_file,read_json,atomic_json,EvidenceError
from ppiblocker.structure import competition,choose_pair,interface,write_pdb
from test_scientific_contracts import chain

BOOLEAN_FIELDS=[('structure','experimental'),('prediction','allow_external_msa'),('prediction','allow_single_sequence'),
 ('refold','allow_external_msa'),('refold','allow_single_sequence'),('context_review','native_interaction_supported'),
 ('context_review','soluble_construct'),('context_review','no_required_unmodelled_context')]
@pytest.mark.parametrize('section,key',BOOLEAN_FIELDS)
@pytest.mark.parametrize('value',['false',0,1,None,[]])
def test_config_rejects_nonboolean(section,key,value):
    config={'proteins':[{'sequence':'ACDEF'},{'sequence':'ACDEF'}],section:{key:value}}
    with pytest.raises(EvidenceError) as error:pipeline.validate_config(config)
    assert error.value.code=='INVALID_BOOLEAN'

@pytest.mark.parametrize('value',[True,False])
def test_valid_boolean_preserved(value):
    config={'proteins':[{},{}],'prediction':{'allow_external_msa':value}}
    assert pipeline.validate_config(config)['prediction']['allow_external_msa'] is value

def test_backend_rejects_quoted_false_without_network(tmp_path,monkeypatch):
    monkeypatch.setattr(backends,'require_gpu',lambda:None)
    monkeypatch.setattr(backends,'checked_command',lambda *a,**k:pytest.fail('No backend call allowed'))
    with pytest.raises(EvidenceError) as e:backends.boltz_predict(tmp_path,tmp_path/'job',[],{'allow_external_msa':'false'},tmp_path/'log')
    assert e.value.code=='INVALID_BOOLEAN'

def test_actual_and_projected_sidechain_clashes_are_distinct():
    predicted=chain('A');binder=chain('B',3);native=copy.deepcopy(predicted)
    # Native-only sidechain moved toward binder without changing any target CA.
    native['heavy'][0]=np.vstack([native['heavy'][0],np.array([0,2.9,0])])
    result=competition(native,chain('B',3),predicted,binder,predicted,binder)
    assert result['target_ca_rmsd']<1e-8
    assert result['predicted_complex_interface']['minimum_distance']==pytest.approx(3)
    assert result['reference_projection_interface']['minimum_distance']==pytest.approx(.1)

def test_entity_rejection_tries_remaining_pairs():
    proteins=[{'sequence':'ACDEF','canonical_start':1}]*2
    def validator(pair):
        if [pair['target_match']['chain'],pair['partner_match']['chain']]!=['A','C']:
            raise EvidenceError('STRUCTURE_ACCESSION_MISMATCH','wrong entity')
        return [{'entity':'accepted'}]
    a,b,pair=choose_pair([chain('A'),chain('B',2),chain('C',4)],proteins,{},validator=validator)
    assert [a['id'],b['id']]==['A','C'] and pair['rejected_entity_pairs']

def test_msa_snapshot_survives_original_change_and_detects_snapshot_tampering(tmp_path):
    original=tmp_path/'input.a3m';original.write_text('>query\nACDEF\n')
    config={'proteins':[{'msa':'input.a3m'},{}],'refold':{'target_msa':'input.a3m'}}
    run=Run(tmp_path,'test');common.pin_config_msas(run,config,tmp_path)
    manifest=run.finish('POSE_ACCEPTED','test')
    original.write_text('>replacement\nFFFFF\n')
    common.load_run(manifest,{'POSE_ACCEPTED'})
    snapshot=Path(config['proteins'][0]['msa'])
    assert snapshot.read_text()=='>query\nACDEF\n'
    snapshot.write_text('altered')
    with pytest.raises(EvidenceError) as e:common.load_run(manifest,{'POSE_ACCEPTED'})
    assert e.value.code=='INTEGRITY_FAILURE'

def test_unpinned_msa_rejected(tmp_path,monkeypatch):
    monkeypatch.setattr(backends,'require_gpu',lambda:None)
    source=tmp_path/'x.a3m';source.write_text('>q\nACDEF\n')
    with pytest.raises(EvidenceError) as e:
        backends.boltz_predict(tmp_path,tmp_path/'work',[{'sequence':'ACDEF','msa':str(source)}],{},tmp_path/'log')
    assert e.value.code=='MSA_UNPINNED'

def test_input_and_runtime_receipt_tampering_rejected(tmp_path):
    source=tmp_path/'input';source.write_text('old')
    run=Run(tmp_path,'test',[record_file(source)]);manifest=run.finish('POSE_ACCEPTED','test')
    source.write_text('new')
    with pytest.raises(EvidenceError):common.load_run(manifest,{'POSE_ACCEPTED'})
    source.write_text('old')
    runtime=tmp_path/'runtime.json';atomic_json(runtime,{'version':'one'})
    run.manifest['runtime']={'core':{'snapshot':record_file(runtime)}};run.save()
    runtime.write_text('{}')
    with pytest.raises(EvidenceError):common.load_run(manifest,{'POSE_ACCEPTED'})

def test_live_runtime_drift_rejected(tmp_path,monkeypatch):
    lock=tmp_path/'source/environment/runtime-lock-core.json';atomic_json(lock,{'packages':['v1']})
    monkeypatch.setattr(common,'collect_runtime',lambda *a:{'packages':['v2']})
    run=Run(tmp_path,'test')
    with pytest.raises(EvidenceError) as e:common.runtime_provenance(run,tmp_path,['core'])
    assert e.value.code=='RUNTIME_DRIFT'

@pytest.fixture
def eval_case(tmp_path,monkeypatch):
    monkeypatch.setattr(pipeline,'runtime_provenance',lambda *a:None)
    design=Run(tmp_path,'03_design')
    config={'proteins':[{},{}],'refold':{'samples':3,'allow_single_sequence':True},'gates':{'contact_cutoff':7}}
    p=design.path/'outputs/config.json';atomic_json(p,config);design.output('config',p)
    native=design.path/'outputs/native.pdb';write_pdb(native,[chain('A'),chain('B',3)]);design.output('native',native)
    candidates=[{'id':'test','sequence':'ACDEF','backbone':record_file(native)}]
    p=design.path/'outputs/candidates.json';atomic_json(p,candidates);design.output('candidates',p)
    upstream=design.finish('DESIGNS_GENERATED','test')
    models=[]
    for i in range(3):
        conf=tmp_path/f'confidence{i}.json';atomic_json(conf,{'pair_chains_iptm':{'0':{'1':.9},'1':{'0':.9}},'complex_plddt':.9})
        pae=tmp_path/f'pae{i}.npz';np.savez(pae,pae=np.ones((10,10)))
        models.append({'model_index':i,'structure':record_file(native),'confidence':record_file(conf),'pae':record_file(pae)})
    monkeypatch.setattr(pipeline,'boltz_predict',lambda *a:models)
    return tmp_path,upstream,models

@pytest.mark.parametrize('bad',['confidence','pae','structure'])
def test_malformed_model_makes_whole_evaluation_incomplete(eval_case,bad):
    root,upstream,models=eval_case
    path=root/('broken_'+bad)
    if bad=='confidence':path.write_text('{broken json')
    elif bad=='pae':
        path=root/'broken_pae.npz';np.savez(path,pae=np.ones((2,2)))
    else:path.write_text('not a pdb')
    models[1][bad]=record_file(path)
    result=read_json(pipeline.evaluate(root,upstream))
    rows=read_json(result['outputs']['evaluation']['path'])['candidates']
    assert result['status']=='EVALUATION_INCOMPLETE' and result['failed_count']==1
    assert rows[0]['evaluation_failed_samples']==1 and rows[0]['models'][1]['status']=='MODEL_EVALUATION_FAILED'

def test_evaluation_uses_actual_interface_and_configured_cutoff(eval_case,monkeypatch):
    root,upstream,models=eval_case
    def pair(*args):
        a,b=chain('A'),chain('B',3)
        return a,b,{'interface':interface(a,b,7)},{'pair_iptm':.9,'interface_pae_mean':1,'complex_plddt':.9,'partner_plddt':.9,'interface_plddt':.9}
    monkeypatch.setattr(pipeline,'model_pair',pair)
    def geometry(*args,cutoff):
        assert cutoff==7
        return {'predicted_complex_interface':{'minimum_distance':2.5},'reference_projection_interface':{'minimum_distance':.1},
                'binder_ca_rmsd_after_target_alignment':1,'target_ca_rmsd':.2,'native_interface_coverage':1,'partner_overlap_atom_count_2A':20}
    monkeypatch.setattr(pipeline,'competition',geometry)
    result=read_json(pipeline.evaluate(root,upstream))
    assert result['status']=='EVALUATION_COMPLETE' and result['accepted_count']==1

def test_prediction_parse_failure_cannot_pass_ensemble(eval_case):
    root,_,models=eval_case
    run=Run(root,'01_pose')
    config={'proteins':[{},{}],'prediction':{'samples':3}}
    proteins=[{'sequence':'ACDEF','canonical_start':1}]*2
    for name,value in [('config',config),('proteins',proteins)]:
        path=run.path/'outputs'/f'{name}.json';atomic_json(path,value);run.output(name,path)
    upstream=run.finish('NEEDS_PREDICTION','test')
    malformed=root/'bad.json';malformed.write_text('{}');models[0]['confidence']=record_file(malformed)
    result=read_json(pipeline.predict(root,upstream))
    assert result['status']=='PREDICTION_INCOMPLETE'

def test_rfd_anchors_use_configured_cutoff(tmp_path,monkeypatch):
    monkeypatch.setattr(backends,'require_gpu',lambda:None)
    native=tmp_path/'native.pdb';write_pdb(native,[chain('A'),chain('B',6)])
    ckpt=tmp_path/'assets/rfdiffusion/Complex_base_ckpt.pt';ckpt.parent.mkdir(parents=True);ckpt.write_text('fixture')
    def stop(*args,**kwargs):raise EvidenceError('STOP_BEFORE_MODEL','anchor selection reached backend')
    monkeypatch.setattr(backends,'checked_command',stop)
    with pytest.raises(EvidenceError) as e:backends.rfd_mpnn(tmp_path,tmp_path/'work',native,{},tmp_path/'logs',contact_cutoff=7)
    assert e.value.code=='STOP_BEFORE_MODEL'

def test_competition_cutoff_changes_actual_contact_definition():
    a,b=chain('A'),chain('B',6)
    narrow=competition(a,b,a,b,a,b,cutoff=5)
    wide=competition(a,b,a,b,a,b,cutoff=7)
    assert narrow['predicted_complex_interface']['target_residues']==[]
    assert wide['native_interface_coverage']==1 and wide['contact_cutoff_angstrom']==7

def test_prediction_target_msa_is_not_silently_ignored():
    with pytest.raises(EvidenceError) as e:pipeline.validate_config({'proteins':[{},{}],'prediction':{'target_msa':'x.a3m'}})
    assert e.value.code=='INVALID_MSA_CONFIG'

def test_valid_noncontacting_models_are_rejected_not_failed(eval_case):
    root,upstream,models=eval_case
    separate=root/'separate.pdb';write_pdb(separate,[chain('A'),chain('B',100)])
    for m in models:m['structure']=record_file(separate)
    result=read_json(pipeline.evaluate(root,upstream))
    assert result['status']=='EVALUATION_COMPLETE' and result['failed_count']==0 and result['accepted_count']==0
    rows=read_json(result['outputs']['evaluation']['path'])['candidates']
    assert all('NO_INTERFACE' in m['reasons'] for m in rows[0]['models'])
    run=Run(root,'01_pose')
    for name,value in [('config',{'proteins':[{},{}],'prediction':{'samples':3}}),('proteins',[{'sequence':'ACDEF','canonical_start':1}]*2)]:
        path=run.path/'outputs'/f'{name}.json';atomic_json(path,value);run.output(name,path)
    result=read_json(pipeline.predict(root,run.finish('NEEDS_PREDICTION','test')))
    assert result['status']=='POSE_REJECTED'

def test_reevaluate_never_invokes_models(eval_case,monkeypatch):
    root,upstream,_=eval_case
    old=pipeline.evaluate(root,upstream)
    original=record_file(old)
    monkeypatch.setattr(pipeline,'boltz_predict',lambda *a:pytest.fail('No model invocation during CPU reanalysis'))
    new=read_json(pipeline.reevaluate(root,old))
    assert new['evaluation_mode']=='existing_predictions_cpu_reanalysis' and new['status']=='EVALUATION_COMPLETE'
    assert record_file(old)==original

def test_replay_wrong_design_rejected(eval_case):
    root,upstream,_=eval_case
    old=pipeline.evaluate(root,upstream)
    alternate=root/'alternate.json';obj=read_json(upstream);obj['run_id']='another';atomic_json(alternate,obj)
    with pytest.raises(EvidenceError) as e:pipeline.evaluate(root,alternate,reuse=old)
    assert e.value.code=='REPLAY_INPUT_MISMATCH'

def test_runtime_tree_detects_added_config(tmp_path):
    directory=tmp_path/'model';directory.mkdir();(directory/'settings.yaml').write_text('a: 1')
    before=common.tree_fingerprint(directory)
    (directory/'settings.yaml').write_text('a: 2')
    assert common.tree_fingerprint(directory)['tree_sha256']!=before['tree_sha256']
    (directory/'settings.yaml').write_text('a: 1');(directory/'extra.json').write_text('{}')
    assert common.tree_fingerprint(directory)['file_count']==2

def test_backend_runtime_always_checks_core(tmp_path,monkeypatch):
    calls=[]
    def collect(root,component):calls.append(component);return {'component':component}
    for component in ('core','boltz'):
        atomic_json(tmp_path/'source/environment'/f'runtime-lock-{component}.json',{'component':component})
    monkeypatch.setattr(common,'collect_runtime',collect)
    run=Run(tmp_path,'test');common.runtime_provenance(run,tmp_path,['boltz'])
    assert calls==['core','boltz'] and set(run.manifest['runtime'])=={'core','boltz'}

def test_core_drift_blocks_backend_before_backend_capture(tmp_path,monkeypatch):
    atomic_json(tmp_path/'source/environment/runtime-lock-core.json',{'version':'reviewed'})
    calls=[]
    def collect(root,component):calls.append(component);return {'version':'changed'}
    monkeypatch.setattr(common,'collect_runtime',collect)
    with pytest.raises(EvidenceError) as e:common.runtime_provenance(Run(tmp_path,'test'),tmp_path,['boltz'])
    assert e.value.code=='RUNTIME_DRIFT' and calls==['core']

@pytest.mark.parametrize('suffix,text',[('.a3m','>query\nACDEF\n'),('.csv','key,sequence\n-1,ACDEF\n')])
def test_msa_format_and_bytes_preserved_to_backend(tmp_path,monkeypatch,suffix,text):
    original=tmp_path/('original'+suffix);original.write_text(text)
    run=Run(tmp_path,'test');config={'proteins':[{'sequence':'ACDEF','msa':str(original)},{}]}
    common.pin_config_msas(run,config,tmp_path)
    monkeypatch.setattr(backends,'require_gpu',lambda:None)
    def inspect(argv,work,*args):
        inp=yaml.safe_load((work/'complex.yaml').read_text())
        msa=Path(inp['sequences'][0]['protein']['msa'])
        assert msa.suffix==suffix and msa.read_text()==text
        assert '--use_msa_server' not in argv
        raise EvidenceError('STOP_BEFORE_MODEL','verified immutable input')
    monkeypatch.setattr(backends,'checked_command',inspect)
    with pytest.raises(EvidenceError) as e:backends.boltz_predict(tmp_path,tmp_path/'work',[config['proteins'][0]],{},tmp_path/'log')
    assert e.value.code=='STOP_BEFORE_MODEL'

def test_core_probe_rejects_wrong_calling_interpreter(tmp_path):
    with pytest.raises(EvidenceError) as error:common.collect_runtime(tmp_path,'core')
    assert error.value.code=='ENVIRONMENT_INTERPRETER_MISMATCH'
