import numpy as np
import pytest
from ppiblocker.af2_review import atom_overlap,pose_distance
from ppiblocker.common import EvidenceError
def chain(atom,xyz):
 return {"atoms":[[(atom,"C",np.array(xyz))]]}
def test_sidechain_overlap_is_not_backbone_overlap():
 x=atom_overlap(chain("CB",[0,0,0]),chain("CB",[.5,0,0]))
 assert x["pairs_under_1_5A"]==1 and x["backbone_pairs_under_1_5A"]==0
def test_backbone_collision_and_distance():
 x=atom_overlap(chain("CA",[0,0,0]),chain("CA",[1,0,0]))
 assert x["backbone_pairs_under_1_5A"]==1 and x["minimum_heavy_distance"]==1
def test_unknown_element_cannot_silently_pass():
 a={"atoms":[[("XX","X",np.zeros(3))]]}
 with pytest.raises(EvidenceError):atom_overlap(a,chain("CA",[4,0,0]))
def c(coords):
 return {"sequence":"AAA","residues":[{"ca":np.array(x,dtype=float)} for x in coords]}
def test_pose_and_fold_are_separate():
 target=c([[0,0,0],[1,0,0],[0,1,0]]);binder=c([[0,0,3],[1,0,3],[0,1,3]])
 moved=c([[0,0,8],[1,0,8],[0,1,8]])
 result=pose_distance([target,binder],[target,moved])
 assert result["binder_ca_after_target_alignment"]==pytest.approx(5)
 assert result["binder_ca_after_self_alignment"]==pytest.approx(0,abs=1e-7)


def test_mpnn_sequence_changes_preserve_backbone_correspondence_only_when_explicit():
 target=c([[0,0,0],[1,0,0],[0,1,0]]);binder=c([[0,0,3],[1,0,3],[0,1,3]])
 mutated={**binder,"sequence":"VVV"}
 with pytest.raises(EvidenceError):pose_distance([target,binder],[target,mutated])
 assert pose_distance([target,binder],[target,mutated],allow_binder_sequence_change=True)["binder_ca_after_target_alignment"]==pytest.approx(0,abs=1e-7)
def test_mpnn_exception_does_not_allow_target_mutations():
 target=c([[0,0,0],[1,0,0],[0,1,0]]);binder=c([[0,0,3],[1,0,3],[0,1,3]])
 with pytest.raises(EvidenceError):pose_distance([target,binder],[{**target,"sequence":"VVV"},binder],allow_binder_sequence_change=True)
