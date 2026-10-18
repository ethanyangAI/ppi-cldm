import numpy as np
import pytest
from ppiblocker.identity import resolve_protein
from ppiblocker.common import EvidenceError
from ppiblocker.structure import competition,transform
from test_scientific_contracts import chain

class Repo:
 def __init__(self,matches):self.matches=matches
 def get(self,url):
  if "/search?" in url:return {"results":self.matches}
  return {"organism":{"taxonId":9606},"sequence":{"value":"ACDEFGHIKL"}}
def hit(acc,gene,syn=None):
 return {"primaryAccession":acc,"genes":[{"geneName":{"value":gene},"synonyms":[{"value":syn or gene}]}]}
def test_primary_gene_disambiguates_synonym_without_hit_order():
 r=resolve_protein({"gene":"RNH1","taxon":9606},Repo([hit("OTHER","RNASEH1","RNH1"),hit("RIGHT","RNH1")]))
 assert r["uniprot"]=="RIGHT"
 assert r["gene_resolution"]["matched_accessions"]==["OTHER","RIGHT"]
def test_multiple_primary_genes_still_rejected():
 with pytest.raises(EvidenceError):
  resolve_protein({"gene":"X","taxon":9606},Repo([hit("ONE","X"),hit("TWO","X")]))
def test_ambiguous_synonyms_still_rejected():
 with pytest.raises(EvidenceError):
  resolve_protein({"gene":"X","taxon":9606},Repo([hit("ONE","A","X"),hit("TWO","B","X")]))
def test_unique_synonym_retains_legacy_resolution():
 r=resolve_protein({"gene":"X","taxon":9606},Repo([hit("ONE","A","X")]))
 assert r["uniprot"]=="ONE"
def test_rigid_binder_displacement_is_pose_failure_not_fold_failure():
 a,b=chain("A"),chain("B",3)
 moved=transform(b,np.eye(3),np.array([0.,20.,0.]))
 g=competition(a,b,a,b,a,moved)
 assert g["binder_ca_rmsd_after_self_alignment"]<1e-8
 assert g["binder_ca_rmsd_after_target_alignment"]==pytest.approx(20)
def test_fold_and_pose_metrics_invariant_to_global_frame():
 a,b=chain("A"),chain("B",3)
 r=np.array([[0,-1,0],[1,0,0],[0,0,1.]])
 g=competition(a,b,a,b,transform(a,r,np.array([3.,5.,8.])),transform(b,r,np.array([3.,5.,8.])))
 assert g["binder_ca_rmsd_after_self_alignment"]<1e-8
 assert g["binder_ca_rmsd_after_target_alignment"]<1e-8


def test_projection_is_invariant_to_author_chain_labels_across_structures():
 a,b=chain("A"),chain("B",3)
 expected=competition(a,b,a,b,a,b)
 # Reference target B and independently predicted binder B are different molecules.
 x,y={**a,"id":"B"},{**b,"id":"A"}
 actual=competition(x,y,x,y,a,b)
 for key in ["binder_ca_rmsd_after_target_alignment","binder_ca_rmsd_after_self_alignment","native_interface_coverage","reference_projection_native_interface_coverage"]:
  assert actual[key]==pytest.approx(expected[key])
def test_native_same_chain_is_still_rejected():
 a,b=chain("A"),chain("A",3)
 with pytest.raises(EvidenceError,match="distinct physical chains"):
  competition(a,b,a,b,a,b)
