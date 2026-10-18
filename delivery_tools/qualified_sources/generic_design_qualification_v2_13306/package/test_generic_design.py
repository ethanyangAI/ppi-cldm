"""CPU synthetic dispatch/validation contracts. Never call a real generator/refold."""
import copy,os
from pathlib import Path
import pytest
from ppiblocker import pipeline,common
from ppiblocker.common import EvidenceError,Run,atomic_json,record_file,read_json
from ppiblocker.structure import write_pdb
from test_audit_regressions import eval_case
from test_scientific_contracts import chain
from patch_generic_design import patch

@pytest.mark.parametrize("key",["backbones","sequences_per_backbone","binder_length"])
@pytest.mark.parametrize("value",[True,False,0,-1,1.5,"2",None])
def test_design_counts_reject_coercion(key,value):
    cfg={"proteins":[{},{}],"design":{key:value}}
    with pytest.raises(EvidenceError) as e:pipeline.validate_config(cfg)
    assert e.value.code=="INVALID_CONFIG"

@pytest.mark.parametrize("settings",[{},{"backbones":1,"sequences_per_backbone":1,"binder_length":30},
    {"backbones":1000,"sequences_per_backbone":2,"binder_length":200},
    {"backbones":4,"sequences_per_backbone":4,"binder_length":65,"temperature":.1}])
def test_existing_valid_design_counts_remain_accepted(settings):
    cfg={"proteins":[{},{}],"design":copy.deepcopy(settings)}
    before=copy.deepcopy(cfg);assert pipeline.validate_config(cfg)==before and cfg==before

@pytest.mark.parametrize("key,value,code",[("binder_length",29,"UNSUPPORTED_BINDER_LENGTH"),
    ("binder_length",201,"UNSUPPORTED_BINDER_LENGTH"),("backbones",1001,"INVALID_DESIGN_COUNT")])
def test_existing_backend_range_limits_rejected_before_generation(key,value,code):
    with pytest.raises(EvidenceError) as e:pipeline.validate_config({"proteins":[{},{}],"design":{key:value}})
    assert e.value.code==code

@pytest.mark.parametrize("value",[True,False,0,-1,float("nan"),float("inf"),10**400,"0.1 0.2"])
def test_nonfinite_zero_or_multiple_sampling_temperature_rejected(value):
    with pytest.raises(EvidenceError) as e:pipeline.validate_config({"proteins":[{},{}],"design":{"temperature":value}})
    assert e.value.code=="INVALID_DESIGN_TEMPERATURE"

@pytest.mark.parametrize("value",[1,.1,1e-8])
def test_single_finite_positive_temperature_preserved(value):
    cfg={"proteins":[{},{}],"design":{"temperature":value}}
    assert pipeline.validate_config(cfg)["design"]["temperature"]==value

def test_implicit_defaults_do_not_rewrite_configuration():
    cfg={"proteins":[{},{}]};before=copy.deepcopy(cfg)
    assert pipeline.validate_config(cfg)==before and "design"not in cfg

def design_case(tmp_path,monkeypatch,pool):
    upstream=tmp_path/"upstream.json";atomic_json(upstream,{"fixture":"SYNTHETIC_ONLY"})
    native=tmp_path/"native.pdb";write_pdb(native,[chain("A"),chain("B",3)])
    cfg={"proteins":[{},{}],"design":{"backbones":1,"sequences_per_backbone":1,"binder_length":65}}
    monkeypatch.setattr(pipeline,"load_run",lambda *a,**k:{"fixture":"SYNTHETIC_ONLY"})
    monkeypatch.setattr(pipeline,"validate_design_pose",lambda m:(pipeline.validate_config(cfg),{},native))
    monkeypatch.setattr(pipeline,"runtime_provenance",lambda *a,**k:None)
    calls=[]
    monkeypatch.setattr(pipeline,"rfd_mpnn",lambda *a,**k:(calls.append("mock_backend")or pool))
    return upstream,native,calls

def failed_manifests(tmp_path):
    paths=list((tmp_path/"steps").glob("03_design/runs/*/manifest.json"))
    return [read_json(p)for p in paths]

def test_empty_backend_pool_never_becomes_designs_generated(tmp_path,monkeypatch):
    upstream,native,calls=design_case(tmp_path,monkeypatch,[])
    with pytest.raises(EvidenceError) as e:pipeline.design(tmp_path,upstream)
    assert e.value.code=="EMPTY_DESIGN_POOL"and calls==["mock_backend"]
    rows=failed_manifests(tmp_path);assert len(rows)==1 and rows[0]["status"]=="FAILED"
    assert "candidates"not in rows[0]["outputs"]

@pytest.mark.parametrize("pool",[None,{}])
def test_nonlist_backend_pool_typed_failure(tmp_path,monkeypatch,pool):
    upstream,_,_=design_case(tmp_path,monkeypatch,pool)
    with pytest.raises(EvidenceError) as e:pipeline.design(tmp_path,upstream)
    assert e.value.code=="INVALID_DESIGN_POOL"

def imported_case(tmp_path,pool):
    r=Run(tmp_path,"03_design")
    for name,value in (("config",{"proteins":[{},{}]}),("candidates",pool)):
        p=r.path/"outputs"/(name+".json");atomic_json(p,value);r.output(name,p)
    # Empty pool must fail before native/runtime/refold reads.
    return r.finish("DESIGNS_GENERATED","synthetic_imported_pool_only")

@pytest.mark.parametrize("pool,code",[([],"EMPTY_DESIGN_POOL"),({},"INVALID_DESIGN_POOL")])
def test_imported_empty_or_nonlist_pool_cannot_complete_evaluation(tmp_path,monkeypatch,pool,code):
    upstream=imported_case(tmp_path,pool)
    monkeypatch.setattr(pipeline,"runtime_provenance",lambda *a,**k:pytest.fail("No runtime capture before rejecting empty pool"))
    monkeypatch.setattr(pipeline,"boltz_predict",lambda *a,**k:pytest.fail("No refold inference"))
    with pytest.raises(EvidenceError) as e:pipeline.evaluate(tmp_path,upstream)
    assert e.value.code==code
    rows=[read_json(p)for p in (tmp_path/"steps").glob("04_evaluate/runs/*/manifest.json")]
    assert len(rows)==1 and rows[0]["status"]=="FAILED"and "evaluation"not in rows[0]["outputs"]

def test_empty_replay_cannot_reuse_old_success(tmp_path,monkeypatch):
    upstream=imported_case(tmp_path,[])
    with pytest.raises(EvidenceError) as e:pipeline.evaluate(tmp_path,upstream,reuse=tmp_path/"nonexistent_success.json")
    assert e.value.code=="EMPTY_DESIGN_POOL"

def test_valid_nonempty_backend_pool_keeps_design_output(tmp_path,monkeypatch):
    upstream,native,calls=design_case(tmp_path,monkeypatch,[])
    fasta=tmp_path/"mpnn.fa";fasta.write_text(">synthetic\n"+"A"*65+"\n")
    row={"id":"synthetic","sequence":"A"*65,"backbone":record_file(native),"raw_backbone":record_file(native),"mpnn_fasta":record_file(fasta)}
    monkeypatch.setattr(pipeline,"rfd_mpnn",lambda *a,**k:[row])
    result=read_json(pipeline.design(tmp_path,upstream))
    assert result["status"]=="DESIGNS_GENERATED"and result["candidate_count"]==1
    assert read_json(result["outputs"]["candidates"]["path"])==[row]

def test_nonempty_all_rejected_pool_remains_honest_complete(eval_case):
    root,upstream,models=eval_case
    noncontact=root/"noncontact.pdb";write_pdb(noncontact,[chain("A"),chain("B",100)])
    for m in models:m["structure"]=record_file(noncontact)
    result=read_json(pipeline.evaluate(root,upstream))
    assert result["status"]=="EVALUATION_COMPLETE"and result["total_count"]==1 and result["accepted_count"]==0

def test_patch_cannot_reapply_to_derived_pipeline():
    parent=Path(os.environ["GENERIC_PATCH_PARENT_PIPELINE"]).read_text()
    with pytest.raises(ValueError):patch(patch(parent))

def test_patch_rejects_unrecognised_source_anchor():
    parent=Path(os.environ["GENERIC_PATCH_PARENT_PIPELINE"]).read_text()
    with pytest.raises(ValueError):patch(parent.replace('        reused=None','        reused = None'))



# V2 adds source-dependency fixtures in a distinct selected pytest suite.
# All original 50 design policy cases above are unchanged and remain separately counted.
import qualify_generic_design_cpu as qualification

def regression_dependency_case(tmp_path,monkeypatch):
    monkeypatch.setattr(qualification,"R",tmp_path)
    source=tmp_path/"source";(source/"scripts").mkdir(parents=True)
    original=source/"scripts/register_runtime_locks.py"
    original.write_text("def fixture():\n    return 1\n")
    out=tmp_path/"out";out.mkdir()
    return source,out,original

def test_regression_dependency_exact_sibling_copy_and_current_readback(tmp_path,monkeypatch):
    source,out,original=regression_dependency_case(tmp_path,monkeypatch)
    rows=qualification.freeze_source_dependencies(source,out)
    test_path=out/"generic_tests/test_runtime_registration.py"
    assert Path(rows[0]["frozen"]["path"])==test_path.resolve().parents[1]/"scripts/register_runtime_locks.py"
    assert original.read_bytes()==Path(rows[0]["frozen"]["path"]).read_bytes()
    assert qualification.verify_source_dependencies(rows,source,out) is True

def test_regression_dependency_missing_named_source_rejected(tmp_path,monkeypatch):
    source,out,original=regression_dependency_case(tmp_path,monkeypatch);original.unlink()
    with pytest.raises(ValueError,match="Exact named regression dependency"):
        qualification.freeze_source_dependencies(source,out)
    assert not(out/"scripts").exists()

def test_regression_dependency_symlink_source_rejected(tmp_path,monkeypatch):
    source,out,original=regression_dependency_case(tmp_path,monkeypatch)
    other=tmp_path/"other.py";original.rename(other);original.symlink_to(other)
    with pytest.raises(ValueError,match="Exact named regression dependency"):
        qualification.freeze_source_dependencies(source,out)

def test_regression_dependency_wrong_original_root_rejected(tmp_path,monkeypatch):
    source,out,_=regression_dependency_case(tmp_path,monkeypatch)
    with pytest.raises(ValueError,match="Only exact current source"):
        qualification.freeze_source_dependencies(source/"scripts",out)

def test_regression_dependency_original_bytes_changed_after_freeze_rejected(tmp_path,monkeypatch):
    source,out,original=regression_dependency_case(tmp_path,monkeypatch)
    rows=qualification.freeze_source_dependencies(source,out);original.write_text("changed original")
    with pytest.raises(ValueError,match="Qualification input bytes changed"):
        qualification.verify_source_dependencies(rows,source,out)

def test_regression_dependency_frozen_bytes_changed_after_freeze_rejected(tmp_path,monkeypatch):
    source,out,_=regression_dependency_case(tmp_path,monkeypatch)
    rows=qualification.freeze_source_dependencies(source,out)
    frozen=Path(rows[0]["frozen"]["path"]);frozen.chmod(0o644);frozen.write_text("changed frozen");frozen.chmod(0o444)
    with pytest.raises(ValueError,match="Qualification input bytes changed"):
        qualification.verify_source_dependencies(rows,source,out)

def test_regression_dependency_original_receipt_path_fork_rejected(tmp_path,monkeypatch):
    source,out,original=regression_dependency_case(tmp_path,monkeypatch)
    rows=qualification.freeze_source_dependencies(source,out)
    other=source/"scripts/another.py";other.write_bytes(original.read_bytes())
    rows[0]["original"]=qualification.rec(other)
    with pytest.raises(ValueError,match="exact sibling path differs"):
        qualification.verify_source_dependencies(rows,source,out)

def test_regression_dependency_frozen_receipt_path_fork_rejected(tmp_path,monkeypatch):
    source,out,original=regression_dependency_case(tmp_path,monkeypatch)
    rows=qualification.freeze_source_dependencies(source,out)
    other=out/"another.py";other.write_bytes(original.read_bytes());other.chmod(0o444)
    rows[0]["frozen"]=qualification.rec(other)
    with pytest.raises(ValueError,match="exact sibling path differs"):
        qualification.verify_source_dependencies(rows,source,out)

def test_regression_dependency_wrong_role_rejected(tmp_path,monkeypatch):
    source,out,_=regression_dependency_case(tmp_path,monkeypatch)
    rows=qualification.freeze_source_dependencies(source,out);rows[0]["role"]="OTHER_UNREVIEWED_SOURCE"
    with pytest.raises(ValueError,match="Unknown regression source dependency"):
        qualification.verify_source_dependencies(rows,source,out)

def test_regression_dependency_extra_declared_source_rejected(tmp_path,monkeypatch):
    source,out,_=regression_dependency_case(tmp_path,monkeypatch)
    rows=qualification.freeze_source_dependencies(source,out)
    with pytest.raises(ValueError,match="Exactly one named"):
        qualification.verify_source_dependencies(rows+[copy.deepcopy(rows[0])],source,out)

def test_regression_dependency_missing_declared_source_rejected(tmp_path,monkeypatch):
    source,out,_=regression_dependency_case(tmp_path,monkeypatch)
    qualification.freeze_source_dependencies(source,out)
    with pytest.raises(ValueError,match="Exactly one named"):
        qualification.verify_source_dependencies([],source,out)

def test_regression_dependency_writable_frozen_source_rejected(tmp_path,monkeypatch):
    source,out,_=regression_dependency_case(tmp_path,monkeypatch)
    rows=qualification.freeze_source_dependencies(source,out);Path(rows[0]["frozen"]["path"]).chmod(0o644)
    with pytest.raises(ValueError,match="Readonly qualification input"):
        qualification.verify_source_dependencies(rows,source,out)
