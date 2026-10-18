import copy,json,sys
import pytest,yaml
from ppiblocker import pipeline
from ppiblocker.benchmark import rank_pool,validate_registry
from ppiblocker.common import EvidenceError,checked_command,read_json

def candidate(cid="a",sequence="ACDEF",coverage=.9):
    metrics=dict(pair_iptm=.9,interface_pae_mean=3.,complex_plddt=.9,partner_plddt=.9,
                 interface_plddt=.9,interface_observed=True,interface_target_residues=8,interface_partner_residues=8)
    geometry=dict(binder_ca_rmsd_after_target_alignment=1.,target_ca_rmsd=.2,native_interface_coverage=coverage,
                  partner_overlap_atom_count_2A=8,predicted_complex_interface=dict(minimum_distance=2.))
    return dict(id=cid,sequence=sequence,status="REJECTED",requested_samples=3,
                models=[dict(metrics=copy.deepcopy(metrics),geometry=copy.deepcopy(geometry)) for _ in range(3)])

def test_shared_pool_competition_is_only_changed_gate():
    r=rank_pool([candidate(coverage=.1)],8)
    assert r["arms"]["s0"]["selected"]==["a"]
    assert r["arms"]["s1"]["selected"]==[]
    assert r["arms"]["s1"]["unfilled_slots"]==8
    assert r["experimental_results_available"] is False

def test_errors_never_reinterpreted_as_scientific_reject_or_pass():
    row=candidate();row["models"][0]={"status":"MODEL_EVALUATION_FAILED"}
    r=rank_pool([row])
    assert r["candidates"][0]["reason"]=="INVALID_MODEL"
    assert not r["arms"]["s0"]["selected"]

def test_exact_duplicate_sequences_not_extra_hits():
    r=rank_pool([candidate("b"),candidate("a")],8)
    assert r["arms"]["s0"]["selected"]==["a"]
    assert r["arms"]["s0"]["unfilled_slots"]==7

def test_no_truth_label_used_by_ranking():
    a=candidate("a");b=candidate("b","GGGGG")
    a["experimental_blockade"]=False;b["experimental_blockade"]=True
    assert rank_pool([b,a],1)["arms"]["s0"]["selected"]==["a"]

def test_nan_iptm_not_selectable():
    row=candidate();row["models"][0]["metrics"]["pair_iptm"]=float("nan")
    assert not rank_pool([row])["arms"]["s0"]["selected"]

@pytest.mark.parametrize("key,value",[("pdb","1YCR"),("path","reference.pdb"),("chains",["A","B"])])
def test_blind_mode_refuses_reference_inputs(key,value):
    with pytest.raises(EvidenceError,match="predict_only"):
        pipeline.validate_config(dict(proteins=[{},{}],structure=dict(mode="predict_only",**{key:value})))

def test_blind_prepare_never_calls_rcsb(tmp_path,monkeypatch):
    monkeypatch.setattr(pipeline,"runtime_provenance",lambda *args:None)
    monkeypatch.setattr(pipeline,"search_experimental_pair",lambda *args:pytest.fail("search leakage"))
    monkeypatch.setattr(pipeline.Repository,"get",lambda *args,**kw:pytest.fail("coordinate network"))
    config=tmp_path/"config.yaml"
    config.write_text(yaml.safe_dump(dict(proteins=[dict(sequence="ACDEFG"),dict(sequence="GGGAAA")],structure=dict(mode="predict_only"))))
    result=read_json(pipeline.prepare(tmp_path,config))
    assert result["status"]=="NEEDS_PREDICTION"
    assert read_json(result["outputs"]["retrieval"]["path"])["search_performed"] is False

def test_family_leakage_rejected():
    cases=[dict(case_id="a",split="DEVELOPMENT",family_group="x",qualification_status="PENDING_REVIEW"),
           dict(case_id="b",split="TEST",family_group="x",qualification_status="PENDING_REVIEW")]
    with pytest.raises(EvidenceError) as e:validate_registry(cases)
    assert e.value.code=="FAMILY_LEAKAGE"

def test_unknown_homology_blocks_test_freeze():
    with pytest.raises(EvidenceError) as e:
        validate_registry([dict(case_id="a",split="TEST",family_group="x",qualification_status="PENDING_REVIEW")])
    assert e.value.code=="HOMOLOGY_REVIEW_REQUIRED"

def test_failed_command_records_resources(tmp_path):
    log=tmp_path/"failed.log"
    with pytest.raises(EvidenceError):checked_command([sys.executable,"-c","raise SystemExit(3)"],tmp_path,log)
    receipt=read_json(log.with_suffix(".resources.json"))
    assert receipt["status"]=="FAILED" and receipt["returncode"]==3 and receipt["wall_seconds"]>0

def test_timeout_records_resources(tmp_path):
    log=tmp_path/"timeout.log"
    with pytest.raises(EvidenceError):checked_command([sys.executable,"-c","import time;time.sleep(1)"],tmp_path,log,timeout=.02)
    assert read_json(log.with_suffix(".resources.json"))["status"]=="TIMEOUT"


def test_nan_secondary_confidence_not_selectable():
    row=candidate();row["models"][0]["metrics"]["complex_plddt"]=float("nan")
    assert not rank_pool([row])["arms"]["s0"]["selected"]

def test_method_input_export_retains_shared_hotspots(tmp_path,monkeypatch):
    from ppiblocker import benchmark_adapters as adapters
    from ppiblocker.common import record_file,atomic_json
    from ppiblocker.structure import write_pdb
    from test_scientific_contracts import chain
    native=tmp_path/"native.pdb";write_pdb(native,[chain("A"),chain("B",3)])
    config=tmp_path/"config.json"
    atomic_json(config,dict(proteins=[{},{}],context_review=dict(native_interaction_supported=True,interaction_evidence="test fixture",soluble_construct=True,no_required_unmodelled_context=True)))
    pose=tmp_path/"pose.json";atomic_json(pose,dict(protein_chain_count=2,nonprotein_context=[]))
    proteins=tmp_path/"proteins.json";atomic_json(proteins,[dict(sequence="ACDEF"),dict(sequence="ACDEF")])
    manifest=tmp_path/"upstream.json";atomic_json(manifest,{})
    monkeypatch.setattr(adapters,"load_run",lambda *args:dict(outputs={k:record_file(v) for k,v in dict(native=native,config=config,pose=pose,proteins=proteins).items()}))
    m=read_json(adapters.export_inputs(tmp_path,manifest))
    assert m["status"]=="METHOD_INPUTS_EXPORTED"
    b=read_json(m["outputs"]["bindcraft"]["path"])
    g=yaml.safe_load(open(m["outputs"]["boltzgen"]["path"]))
    anchors=g["entities"][1]["file"]["binding_types"][0]["chain"]["binding"]
    assert b["target_hotspot_residues"]==",".join("A"+x for x in anchors.split(","))
    assert g["entities"][1]["file"]["include"]==[{"chain":{"id":"A"}}]

