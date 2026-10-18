import json
from pathlib import Path
import numpy as np
import pytest
from ppiblocker.common import EvidenceError,Run,atomic_json,load_run,record_file
from ppiblocker.identity import clean_sequence,resolve_protein
from ppiblocker.structure import choose_pair,interface,superpose,write_pdb,read_structure,competition
from ppiblocker.backends import confidence_metrics,confidence_reasons

def chain(cid,offset=0,sequence="ACDEF"):
    letters={"A":"ALA","C":"CYS","D":"ASP","E":"GLU","F":"PHE"}
    xyz=[np.array([i*3.8,offset,0.]) for i in range(len(sequence))]
    return {"id":cid,"sequence":sequence,
            "residues":[{"name":letters[a],"letter":a,"number":i+1,"icode":"","ca":x} for i,(a,x) in enumerate(zip(sequence,xyz))],
            "heavy":[x[None,:] for x in xyz],"atoms":[[("CA","C",x)] for x in xyz]}

def test_identity_requires_species_for_gene():
    with pytest.raises(EvidenceError,match="Provide UniProt"):
        resolve_protein({"gene":"MDM2"},None)

@pytest.mark.parametrize("seq",["ACX","",">a\nACD\n>b\nEFG"])
def test_invalid_sequences(seq):
    with pytest.raises(EvidenceError):
        resolve_protein({"sequence":seq},None)

def test_construct_mapping():
    p=resolve_protein({"sequence":"MACDEFGHI","residues":[2,6]},None)
    assert p["sequence"]=="ACDEF" and p["canonical_start"]==2

def test_no_same_chain():
    a=chain("A")
    with pytest.raises(EvidenceError) as e:interface(a,a)
    assert e.value.code=="SAME_CHAIN"

def test_no_nearest_contact_fallback():
    p={"sequence":"ACDEF","canonical_start":1}
    with pytest.raises(EvidenceError) as e:choose_pair([chain("A"),chain("B",100)],[p,p],{})
    assert e.value.code=="NO_IDENTITY_VALID_CONTACTING_PAIR"

def test_wrong_identity_is_not_first_two_chains():
    p={"sequence":"ACDEF","canonical_start":1}
    wrong={"sequence":"YYYYY","canonical_start":1}
    with pytest.raises(EvidenceError):choose_pair([chain("A"),chain("B",3)],[p,wrong],{})

def test_roundtrip_pdb_and_interface(tmp_path):
    path=tmp_path/"p.pdb";write_pdb(path,[chain("X"),chain("Y",3)])
    chains,_=read_structure(path)
    assert [c["id"] for c in chains]==["A","B"]
    assert chains[0]["sequence"]=="ACDEF"
    assert len(interface(*chains)["target_residues"])==5

def test_rotation_translation():
    x=np.random.default_rng(3).normal(size=(20,3))
    r=np.array([[0,-1,0],[1,0,0],[0,0,1.]])
    y=x@r+[5,8,-3]
    rr,t,rmsd=superpose(x,y)
    assert rmsd<1e-10 and np.max(abs(x@rr+t-y))<1e-10

def test_competition_is_not_any_binding():
    a,b=chain("A"),chain("B",3)
    overlap=competition(a,b,a,b,a,b)
    assert overlap["native_interface_coverage"]==1 and overlap["partner_overlap_atom_count_2A"]==5
    opposite=chain("B",-3)
    other=competition(a,b,a,opposite,a,opposite)
    assert other["native_interface_coverage"]==1
    assert other["partner_overlap_atom_count_2A"]==0

def test_manifest_rejects_tampering(tmp_path):
    r=Run(tmp_path,"test")
    f=r.path/"outputs/x";f.write_text("accepted");r.output("x",f)
    m=r.finish("POSE_ACCEPTED","test")
    f.write_text("replaced")
    with pytest.raises(EvidenceError) as e:load_run(m,{"POSE_ACCEPTED"})
    assert e.value.code=="INTEGRITY_FAILURE"

def test_failed_upstream_rejected(tmp_path):
    r=Run(tmp_path,"test");m=r.finish("FAILED","not_accepted")
    with pytest.raises(EvidenceError):load_run(m,{"POSE_ACCEPTED"})

def test_metrics_use_pair_not_global_iptm(tmp_path):
    c=tmp_path/"confidence.json";p=tmp_path/"pae.npz"
    atomic_json(c,{"iptm":.99,"pair_chains_iptm":{"0":{"1":.3},"1":{"0":.2}},"complex_plddt":.9})
    np.savez(p,pae=np.ones((10,10))*5)
    metrics=confidence_metrics({"confidence":record_file(c),"pae":record_file(p)},5,5,interface(chain("A"),chain("B",3)))
    assert metrics["pair_iptm"]==.2 and "LOW_PAIR_IPTM" in confidence_reasons(metrics,{})

def test_nan_confidence_rejected(tmp_path):
    c=tmp_path/"confidence.json";p=tmp_path/"pae.npz"
    atomic_json(c,{"pair_chains_iptm":{"0":{"1":.9},"1":{"0":.9}},"complex_plddt":.9})
    np.savez(p,pae=np.full((10,10),np.nan))
    with pytest.raises(EvidenceError):confidence_metrics({"confidence":record_file(c),"pae":record_file(p)},5,5,interface(chain("A"),chain("B",3)))



def test_nan_gate_cannot_bypass_acceptance(tmp_path):
    from ppiblocker.pipeline import config_read
    p=tmp_path/"bad.yaml"
    p.write_text("proteins:\n - sequence: ACDEF\n - sequence: ACDEF\ngates:\n  min_pair_iptm: .nan\n")
    with pytest.raises(EvidenceError) as e:config_read(p)
    assert e.value.code=="INVALID_GATE"

def test_conflicting_accession_sequence_rejected():
    with pytest.raises(EvidenceError) as e:resolve_protein({"sequence":"ACDEF","uniprot":"P04637"},None)
    assert e.value.code=="CONFLICTING_IDENTITY_INPUT"


def test_short_motif_cannot_identify_entire_larger_chain():
    from ppiblocker.structure import match_chain
    p={"sequence":"ACDEF","canonical_start":1}
    result=match_chain(chain("A",sequence="ACDEFACDEF"),p)
    assert result["coverage"]==1 and not result["accepted"]

def test_local_confidence_not_hidden_by_global_plddt():
    reasons=confidence_reasons({"pair_iptm":.95,"complex_plddt":.95,"interface_pae_mean":2,
                                "partner_plddt":.3,"interface_plddt":.4},{})
    assert "LOW_PARTNER_PLDDT" in reasons and "LOW_INTERFACE_PLDDT" in reasons

