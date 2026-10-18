import pytest
from ppiblocker.common import EvidenceError,atomic_json,record_file
from ppiblocker.structure import choose_pair,write_pdb
from ppiblocker.pipeline import validate_design_pose
from test_scientific_contracts import chain

def test_near_identical_mutant_does_not_replace_requested_construct():
    wt="ACDEF"*10
    proteins=[dict(sequence=wt,canonical_start=1)]*2
    with pytest.raises(EvidenceError) as exc:
        choose_pair([chain("A",sequence="E"+wt[1:]),chain("B",3,wt)],proteins,{},exact_construct=True)
    assert exc.value.code=="CONSTRUCT_SEQUENCE_MISMATCH"

def test_exact_construct_selected_even_if_variant_has_contacts():
    wt="ACDEF"*10
    proteins=[dict(sequence=wt,canonical_start=1)]*2
    a,b,_=choose_pair([chain("A",sequence="E"+wt[1:]),chain("B",3,wt),chain("C",6,wt)],proteins,{},exact_construct=True)
    assert {a["id"],b["id"]}=={"B","C"}

def fixture_pose(tmp_path,mutant=False,context=False,reviewed=True):
    wt="ACDEF"*10
    native=tmp_path/"native.pdb"
    write_pdb(native,[chain("A",sequence=("E"+wt[1:]) if mutant else wt),chain("B",3,wt)])
    config=tmp_path/"config.json"
    atomic_json(config,dict(proteins=[{},{}],context_review=dict(native_interaction_supported=reviewed,
        interaction_evidence="explicit test interaction",soluble_construct=True,no_required_unmodelled_context=True)))
    pose=tmp_path/"pose.json";atomic_json(pose,dict(protein_chain_count=2,nonprotein_context=[{"resname":"ZN"}] if context else []))
    proteins=tmp_path/"proteins.json";atomic_json(proteins,[dict(sequence=wt),dict(sequence=wt)])
    return dict(outputs={k:record_file(v) for k,v in dict(native=native,config=config,pose=pose,proteins=proteins).items()})

def test_historical_accepted_mutant_pose_cannot_start_new_design(tmp_path):
    with pytest.raises(EvidenceError) as exc:validate_design_pose(fixture_pose(tmp_path,mutant=True))
    assert exc.value.code=="CONSTRUCT_SEQUENCE_MISMATCH"

@pytest.mark.parametrize("kwargs,code",[
    ({"mutant":True},"CONSTRUCT_SEQUENCE_MISMATCH"),
    ({"context":True},"UNSUPPORTED_ASSEMBLY_CONTEXT"),
    ({"reviewed":False},"INTERACTION_EVIDENCE_REQUIRED")])
def test_external_pool_cannot_bypass_native_design_contract(tmp_path,monkeypatch,kwargs,code):
    from ppiblocker import benchmark_adapters as adapters
    m=fixture_pose(tmp_path,**kwargs)
    monkeypatch.setattr(adapters,"load_run",lambda *a:m)
    with pytest.raises(EvidenceError) as exc:adapters.import_pool(tmp_path,"historical.json",tmp_path/"unused.json")
    assert exc.value.code==code

def test_exact_explicit_construct_remains_accepted(tmp_path):
    config,pose,native=validate_design_pose(fixture_pose(tmp_path))
    assert native.exists() and not pose["nonprotein_context"]

