import copy,unittest
from e2e_design_audit_cpu import validate_design_chain,validate_fasta_candidate,validate_design_cpu_gate,ACCEPTED
class Gate(unittest.TestCase):
    def fixture(self):
        P=dict(path="/exact/new/pose",sha256="p",bytes=1);S=dict(path="/exact/source",sha256="s",bytes=2);A=dict(path="/cpu/pre",sha256="a",bytes=3)
        pre=dict(status="CPU_PHYSICAL_GATE_SOURCE_CONTRACTS_AND_REQUALIFICATION_ACCEPTED",qualified_prediction=dict(status="POSE_ACCEPTED",manifest=P),source_manifest=S)
        result=dict(status="ACTUAL_MODEL_STAGE_COMPLETE",stage="design",CPU_preflight=A,source_manifest=S,upstream=P)
        design=dict(inputs=[P],status="DESIGNS_GENERATED",candidate_count=1)
        return pre,A,result,design
    def test_exact_new_pose_chain_passes(self):validate_design_chain(*self.fixture())
    def test_old_model0_edge_rejected(self):
        pre,A,result,design=self.fixture();result["upstream"]=dict(path="/old/model0",sha256="x")
        with self.assertRaises(ValueError):validate_design_chain(pre,A,result,design)
    def test_pose_rejection_not_rescued(self):
        pre,A,result,design=self.fixture();pre["qualified_prediction"]["status"]="POSE_REJECTED"
        with self.assertRaises(ValueError):validate_design_chain(pre,A,result,design)
    def test_exact_canonical65_single_MPNN_passes(self):
        seq="A"*65;self.assertEqual(validate_fasta_candidate([dict(sequence=seq)],[("designed_chains=['B']","G"*65),("sample",seq)]),seq)
    def test_wrong_MPNN_chain_rejected(self):
        with self.assertRaises(ValueError):validate_fasta_candidate([dict(sequence="A"*65)],[("designed_chains=['A']","G"*65),("sample","A"*65)])
    def test_C_or_X_cannot_enter_actual_proposal(self):
        with self.assertRaises(ValueError):validate_fasta_candidate([dict(sequence="C"+"A"*64)],[("designed_chains=['B']","G"*65),("sample","C"+"A"*64)])
    def test_evaluation_requires_actual_CPU_design_gate(self):
        with self.assertRaises(ValueError):validate_design_cpu_gate(dict(status="PENDING",GPU_allocated=0),{}, {}, {}, {})
    def test_evaluation_gate_pins_exact_design(self):
        audit=dict(status=ACCEPTED,GPU_allocated=0,preflight_acceptance={"a":1},source_manifest={"s":1},actual_design_manifest={"d":1},actual_design_stage_result={"r":1})
        validate_design_cpu_gate(audit,{"a":1},{"s":1},{"d":1},{"r":1})
        with self.assertRaises(ValueError):validate_design_cpu_gate(audit,{"a":1},{"s":1},{"d":2},{"r":1})
if __name__=="__main__":unittest.main()
