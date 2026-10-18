import math
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from ppiblocker.common import EvidenceError, atomic_json, record_file, read_json
from ppiblocker.pose_physical_gate import POLICY, physical_pose_reasons
from ppiblocker.structure import write_pdb, read_structure, interface
from ppiblocker import pipeline

def chain(cid, offset=3.0, hydrogens=False):
    xyz=[np.array([i*3.8,offset,0.]) for i in range(3)]
    atoms=[[("CA","C",x)] for x in xyz]
    if hydrogens:
        atoms[0].append(("H","H",np.array([0.,0.,0.])))
    return dict(id=cid,sequence="AAA",residues=[dict(name="ALA",letter="A",number=i+1,icode="",bfactor=95.,ca=x) for i,x in enumerate(xyz)],
                heavy=[x[None,:] for x in xyz],atoms=atoms)

class FixedDistanceContracts(unittest.TestCase):
    def test_just_below_is_rejected(self): self.assertEqual(physical_pose_reasons(dict(minimum_distance=1.499999)),["SEVERE_TARGET_PARTNER_CLASH"])
    def test_exact_boundary_passes(self): self.assertEqual(physical_pose_reasons(dict(minimum_distance=1.5)),[])
    def test_above_passes(self): self.assertEqual(physical_pose_reasons(dict(minimum_distance=1.500001)),[])
    def test_zero_rejects(self): self.assertTrue(physical_pose_reasons(dict(minimum_distance=0)))
    def test_nan_fails_closed(self): self.bad(float("nan"))
    def test_infinity_fails_closed(self): self.bad(float("inf"))
    def test_missing_fails_closed(self): self.bad(None)
    def test_negative_fails_closed(self): self.bad(-1)
    def test_boolean_fails_closed(self): self.bad(True)
    def test_string_fails_closed(self): self.bad("1.8")
    def bad(self,value):
        with self.assertRaises(EvidenceError) as c: physical_pose_reasons(dict(minimum_distance=value))
        self.assertEqual(c.exception.code,"INVALID_INTERFACE_DISTANCE")
    def test_policy_is_existing_threshold_not_ratio(self):
        self.assertEqual(POLICY["reject_if_minimum_distance_less_than_angstrom"],1.5)
        self.assertTrue(POLICY["not_a_clash_fraction_threshold"])
    def test_real_structure_excludes_hydrogen(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"pose.pdb";write_pdb(p,[chain("A",0),chain("B",3,True)])
            cs,ctx=read_structure(p)
            self.assertEqual(interface(*cs)["minimum_distance"],3.0)
            self.assertEqual(physical_pose_reasons(interface(*cs)),[])

class DesignEntryContracts(unittest.TestCase):
    def fixture(self,d,distance,claimed_distance=4,reviewed=True):
        d=Path(d);p=d/"native.pdb";write_pdb(p,[chain("A",0),chain("B",distance)])
        config=dict(proteins=[{},{}],context_review=dict(native_interaction_supported=reviewed,interaction_evidence="fixture",
            soluble_construct=True,no_required_unmodelled_context=True))
        paths=dict(native=p)
        for name,value in dict(config=config,pose=dict(nonprotein_context=[],protein_chain_count=2,pair=dict(interface=dict(minimum_distance=claimed_distance))),
                               proteins=[dict(sequence="AAA"),dict(sequence="AAA")]).items():
            paths[name]=d/(name+".json");atomic_json(paths[name],value)
        return dict(outputs={k:record_file(v) for k,v in paths.items()})
    def test_cached_claim_cannot_bypass_actual_coordinates(self):
        with tempfile.TemporaryDirectory() as d:
            m=self.fixture(d,1.44,99)
            with self.assertRaises(EvidenceError) as c: pipeline.validate_design_pose(m)
            self.assertEqual(c.exception.code,"SEVERE_NATIVE_POSE_CLASH")
    def test_valid_actual_coordinates_pass(self):
        with tempfile.TemporaryDirectory() as d:
            config,pose,p=pipeline.validate_design_pose(self.fixture(d,3))
            self.assertEqual(pose["design_entry_physical_gate"]["status"],"PHYSICAL_GATE_PASS")
    def test_interaction_context_contract_retained(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(EvidenceError) as c:pipeline.validate_design_pose(self.fixture(d,3,reviewed=False))
            self.assertEqual(c.exception.code,"INTERACTION_EVIDENCE_REQUIRED")

class EnsembleEligibilityContracts(unittest.TestCase):
    def run_case(self,distances,low_confidence=()):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        root=Path(temp.name);c=root/"config.json";p=root/"proteins.json"
        atomic_json(c,dict(proteins=[{},{}],prediction=dict(samples=3)))
        atomic_json(p,[dict(sequence="AAA"),dict(sequence="AAA")])
        models=[]
        for i in range(3):
            path=root/f"raw{i}.txt";path.write_text("raw retained")
            models.append(dict(model_index=i,**{k:record_file(path) for k in ("structure","confidence","pae")}))
        upstream=dict(outputs=dict(config=record_file(c),proteins=record_file(p)))
        def model_pair(model,*args):
            i=model["model_index"];a,b=chain("A",0),chain("B",3)
            contacts=interface(a,b);contacts["minimum_distance"]=distances[i]
            metrics=dict(pair_iptm=.2 if i in low_confidence else .95,interface_pae_mean=2,complex_plddt=.95,
                         partner_plddt=.95,interface_plddt=.95,interface_target_residues=3,interface_partner_residues=3)
            return a,b,dict(interface=contacts),metrics
        upstream_path=root/"upstream.json";atomic_json(upstream_path,dict(status="NEEDS_PREDICTION"))
        with patch.object(pipeline,"load_run",return_value=upstream),patch.object(pipeline,"runtime_provenance"),\
             patch.object(pipeline,"boltz_predict",return_value=models),patch.object(pipeline,"model_pair",side_effect=model_pair):
            manifest=read_json(pipeline.predict(root,upstream_path))
        ensemble=read_json(manifest["outputs"]["ensemble"]["path"])
        return manifest,ensemble
    def test_physically_bad_first_pose_not_chosen(self):
        m,e=self.run_case([1.44,3,3])
        self.assertEqual(m["status"],"POSE_ACCEPTED")
        self.assertEqual(read_json(m["outputs"]["pose"]["path"])["source"]["model"],1)
        self.assertEqual(e["eligible_model_indices"],[1,2])
        self.assertEqual(e["convergent_model_indices"],[1,2])
    def test_one_of_three_cannot_pass(self):
        m,e=self.run_case([1.44,1.44,3]);self.assertEqual(m["status"],"POSE_REJECTED")
        self.assertEqual(e["minimum_support"],2)
        self.assertEqual(e["eligible_model_indices"],[2])
    def test_all_bad_are_real_pose_reject(self):
        m,e=self.run_case([1.44,1.44,1.44]);self.assertEqual(m["status"],"POSE_REJECTED")
        self.assertEqual(e["eligible_model_indices"],[])
    def test_first_representative_rule_retained_for_all_valid(self):
        m,e=self.run_case([3,3,3]);self.assertEqual(read_json(m["outputs"]["pose"]["path"])["source"]["model"],0)
        self.assertEqual(e["convergent_model_indices"],[0,1,2])
    def test_all_three_raw_models_preserved_even_rejected(self):
        m,e=self.run_case([1.44,1.44,1.44])
        self.assertEqual(len([k for k in m["outputs"] if k.startswith("model_")]),9)
        self.assertEqual(len(e["models"]),3)
    def test_confidence_gate_still_applies(self):
        m,e=self.run_case([3,3,3],low_confidence=(1,2));self.assertEqual(m["status"],"POSE_REJECTED")
        self.assertEqual(e["eligible_model_indices"],[0])

class IndependentAtomContracts(unittest.TestCase):
    def fixture(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        path=Path(temp.name)/"p.pdb";write_pdb(path,[chain("A",0),chain("B",3,True)])
        return path
    def test_independent_hydrogen_exclusion_and_atom_identity(self):
        from physical_preflight_cpu import independent_atoms
        row=independent_atoms(self.fixture());self.assertEqual(row["minimum_distance_angstrom"],3)
        self.assertEqual([a["element"] for a in row["closest_atoms"]],["C","C"])
    def test_independent_altloc_fails_closed(self):
        from physical_preflight_cpu import independent_atoms
        path=self.fixture();lines=path.read_text().splitlines();lines[0]=lines[0][:16]+"A"+lines[0][17:];path.write_text("\n".join(lines)+"\n")
        with self.assertRaises(RuntimeError):independent_atoms(path)
    def test_independent_duplicate_heavy_atom_fails_closed(self):
        from physical_preflight_cpu import independent_atoms
        path=self.fixture();path.write_text(path.read_text()+path.read_text().splitlines()[0]+"\n")
        with self.assertRaises(RuntimeError):independent_atoms(path)
    def test_independent_multiple_models_fail_closed(self):
        from physical_preflight_cpu import independent_atoms
        path=self.fixture();text=path.read_text();path.write_text("MODEL        1\n"+text+"ENDMDL\nMODEL        2\n"+text+"ENDMDL\n")
        with self.assertRaises(RuntimeError):independent_atoms(path)

if __name__=="__main__":unittest.main()
